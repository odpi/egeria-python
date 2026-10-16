# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Regression test for ISSUE-146 (PYEGERIA_ISSUES.md): Egeria 6.2 has no note
delete endpoint (notes are Actions), so `remove_note` uses the generic
Metadata Expert element delete. The URL is built from the platform root, so
it is the same on a MetadataExpert client, which overrides command_root.

No live server needed: a mocked `_async_make_request` captures the URL.
"""
from unittest.mock import MagicMock, patch

import pytest

from pyegeria.omvs.my_profile import MyProfile
from pyegeria.omvs.metadata_expert import MetadataExpert

EXPECTED = ("https://localhost:9443/servers/vs/api/open-metadata/"
            "metadata-expert/metadata-elements/note-guid/delete")


def _client(cls):
    with patch("pyegeria.core._base_server_client.BaseServerClient.check_connection", return_value=""):
        return cls(view_server="vs", platform_url="https://localhost:9443", user_id="u", user_pwd="p")


@pytest.mark.parametrize("cls", [MyProfile, MetadataExpert])
def test_remove_note_uses_metadata_expert_delete(cls):
    client = _client(cls)
    cap = {}

    async def fake(method, url, body=None, **kwargs):
        cap["method"], cap["url"], cap["body"] = method, url, body
        resp = MagicMock()
        resp.json = MagicMock(return_value={})
        return resp

    client._async_make_request = fake
    client.remove_note("note-guid")

    assert cap["method"] == "POST"
    assert cap["url"] == EXPECTED
