# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Unit tests for pyegeria.core.relationship_multiplicity -- the relationshipCategory-
based multi-link detection utility (ISSUE-68 follow-up).

No live server needed: a fake client stands in for ValidMetadataManager's
_async_get_all_relationship_defs.
"""
import pytest

from pyegeria.core import relationship_multiplicity as rm


class _FakeClient:
    def __init__(self, platform_url="https://fake:9443", view_server="fake-view", defs=None):
        self.platform_url = platform_url
        self.view_server = view_server
        self.calls = 0
        self._defs = defs if defs is not None else [
            {"name": "DataFlow", "relationshipCategory": "MULTI_LINK"},
            {"name": "SolutionLinkingWire", "relationshipCategory": "UNI_LINK"},
            {"name": "Synonym", "relationshipCategory": "REVERSIBLE"},
        ]

    async def _async_get_all_relationship_defs(self):
        self.calls += 1
        return self._defs


@pytest.fixture(autouse=True)
def _clear_cache():
    rm.clear_relationship_category_cache()
    yield
    rm.clear_relationship_category_cache()


@pytest.mark.asyncio
async def test_multi_link_type_detected():
    client = _FakeClient()
    assert await rm.async_is_multi_link(client, "DataFlow") is True


@pytest.mark.asyncio
async def test_uni_link_type_not_multi_link():
    client = _FakeClient()
    # SolutionLinkingWire is UNI_LINK in the live type registry -- trust
    # relationshipCategory as the source of truth, per user direction,
    # even though existing Dr.Egeria code treats it as multi-link.
    assert await rm.async_is_multi_link(client, "SolutionLinkingWire") is False


@pytest.mark.asyncio
async def test_reversible_type_not_multi_link():
    client = _FakeClient()
    assert await rm.async_is_multi_link(client, "Synonym") is False
    assert await rm.async_get_relationship_category(client, "Synonym") == "REVERSIBLE"


@pytest.mark.asyncio
async def test_unknown_type_defaults_to_not_multi_link():
    client = _FakeClient()
    assert await rm.async_is_multi_link(client, "SomeTypeNotInRegistry") is False
    assert await rm.async_get_relationship_category(client, "SomeTypeNotInRegistry") is None


@pytest.mark.asyncio
async def test_result_is_cached_per_server():
    client = _FakeClient()
    await rm.async_is_multi_link(client, "DataFlow")
    await rm.async_is_multi_link(client, "DataFlow")
    await rm.async_get_relationship_category(client, "Synonym")
    assert client.calls == 1


@pytest.mark.asyncio
async def test_refresh_bypasses_cache():
    client = _FakeClient()
    await rm.async_is_multi_link(client, "DataFlow")
    await rm.async_is_multi_link(client, "DataFlow", refresh=True)
    assert client.calls == 2


@pytest.mark.asyncio
async def test_different_servers_cached_independently():
    client_a = _FakeClient(view_server="server-a")
    client_b = _FakeClient(view_server="server-b", defs=[
        {"name": "DataFlow", "relationshipCategory": "UNI_LINK"},
    ])
    assert await rm.async_is_multi_link(client_a, "DataFlow") is True
    assert await rm.async_is_multi_link(client_b, "DataFlow") is False
