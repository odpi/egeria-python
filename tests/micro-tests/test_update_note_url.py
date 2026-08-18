# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Regression test for ISSUE-30 (PYEGERIA_ISSUES.md): `_async_update_note`'s
URL pointed at `feedback-manager/notes/{noteGUID}`, which 404s on a live
server despite matching what an earlier, stale copy of
`Egeria-api-feedback-manager.http` documented. The real, working endpoint
(confirmed against the refreshed `.http` ground truth and live against
qs-view-server) is `feedback-manager/assets/{noteGUID}/update` -- same
`assets/{guid}/update` shape used elsewhere in the feedback-manager service.

No live server needed: a mocked `_async_make_request` confirms the actual
outgoing URL.
"""
from unittest.mock import MagicMock, patch

from pyegeria.omvs.automated_curation import AutomatedCuration


def _client():
    with patch("pyegeria.core._base_server_client.BaseServerClient.check_connection", return_value=""):
        return AutomatedCuration(view_server="vs", platform_url="https://localhost:9443",
                                  user_id="u", user_pwd="p")


def _mock_request(capture):
    async def fake(method, url, body=None, **kwargs):
        capture["method"] = method
        capture["url"] = url
        capture["body"] = body
        resp = MagicMock()
        resp.json = MagicMock(return_value={})
        return resp
    return fake


def test_update_note_url_targets_assets_update_not_notes():
    client = _client()
    cap = {}
    client._async_make_request = _mock_request(cap)

    client.update_note("note-guid", display_name="new title")

    assert cap["url"].endswith("/feedback-manager/assets/note-guid/update")
    assert "/feedback-manager/notes/" not in cap["url"]


def test_update_note_body_shape_uses_note_properties():
    client = _client()
    cap = {}
    client._async_make_request = _mock_request(cap)

    client.update_note("note-guid", display_name="new title", description="new text")

    props = cap["body"]["properties"]
    assert props["class"] == "NoteProperties"
    assert props["typeName"] == "Note"
    assert props["displayName"] == "new title"
    assert props["description"] == "new text"
