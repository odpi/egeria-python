# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Unit tests for AssetMaker's new SupportedGovernanceService relationship wrapper
(ISSUE-68 follow-up). SupportedGovernanceService is MULTI_LINK -- Egeria's own
Egeria-api-asset-maker.http documents it as such ("the same governance engine
may call the same governance service many times, each with a different
request type... The unique identifier of the new relationship is returned so
it can be updated or removed later"), and it previously had no OMVS wrapper
at all despite dedicated attach/update/detach REST endpoints existing
(confirmed against a live server's OpenAPI spec and the .http ground truth).

These tests confirm the URL construction and that the create path returns
the GUID; they don't hit a live server (see PYEGERIA_ISSUES.md ISSUE-68 for
the separate live routing check performed against a running server, which
confirmed correct request routing via expected 404s on fake GUIDs).
"""
from typing import Any, cast

import pytest

from pyegeria.omvs.asset_maker import AssetMaker


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class _CapturingClient(AssetMaker):
    """Subclass that intercepts the outgoing HTTP call instead of a real client."""

    def __init__(self):
        super().__init__(view_server="fake-view", platform_url="https://fake:9443", user_id="fake-user")
        self.calls = []

    async def _async_make_request(self, method, url, payload=None):
        self.calls.append((method, url, payload))
        return _FakeResponse({"class": "GUIDResponse", "guid": "sgs-rel-guid-0001"})


@pytest.mark.asyncio
async def test_link_supported_governance_service_url_and_guid():
    client = _CapturingClient()
    body = {
        "class": "NewRelationshipRequestBody",
        "properties": {"class": "SupportedGovernanceServiceProperties", "requestType": "survey-folder"},
    }

    guid = await client._async_link_supported_governance_service("engine-guid", "service-guid", body)

    assert guid == "sgs-rel-guid-0001"
    assert len(client.calls) == 1
    method, url, _ = client.calls[0]
    assert method == "POST"
    assert url == (
        "https://fake:9443/servers/fake-view/api/open-metadata/asset-maker/"
        "governance-engines/engine-guid/supported-governance-services/service-guid/attach"
    )


@pytest.mark.asyncio
async def test_update_supported_governance_service_url():
    client = _CapturingClient()
    body = {
        "class": "UpdateRelationshipRequestBody",
        "properties": {"class": "SupportedGovernanceServiceProperties", "requestType": "survey-folder-v2"},
        "mergeUpdate": True,
    }

    await client._async_update_supported_governance_service("sgs-rel-guid-0001", body)

    method, url, _ = client.calls[0]
    assert method == "POST"
    assert url == (
        "https://fake:9443/servers/fake-view/api/open-metadata/asset-maker/"
        "supported-governance-services/sgs-rel-guid-0001/update"
    )


@pytest.mark.asyncio
async def test_detach_supported_governance_service_url():
    client = _CapturingClient()

    await client._async_detach_supported_governance_service("sgs-rel-guid-0001")

    method, url, _ = client.calls[0]
    assert method == "POST"
    assert url == (
        "https://fake:9443/servers/fake-view/api/open-metadata/asset-maker/"
        "supported-governance-services/sgs-rel-guid-0001/detach"
    )
