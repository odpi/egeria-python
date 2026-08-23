# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Regression test for ISSUE-70 (PYEGERIA_ISSUES.md):
`_async_update_next_action_process_step` called a method that does not exist
on the shared base -- `_async_update_relationship_body_request` -- so
`update_next_action_process_step()` could never succeed; it raised
`AttributeError` before issuing any request. The fix routes through the real
shared helper, `_async_update_relationship_request`, matching every other
relationship-update call site in the package (see e.g.
`asset_maker.py`'s `_async_update_catalog_target`).

No live server needed: a mocked `_async_make_request` confirms the call
completes and reaches the real outgoing URL/body.
"""
import json
from unittest.mock import MagicMock, patch

from pyegeria.omvs.action_author import ActionAuthor


def _client():
    with patch("pyegeria.core._base_server_client.BaseServerClient.check_connection", return_value=""):
        return ActionAuthor(view_server="vs", platform_url="https://localhost:9443",
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


def test_update_next_action_process_step_does_not_raise_attribute_error():
    client = _client()
    cap = {}
    client._async_make_request = _mock_request(cap)

    body = {
        "class": "UpdateRelationshipRequestBody",
        "properties": {
            "class": "NextGovernanceActionProcessStepProperties",
            "guard": "some-guard",
            "mandatoryGuard": False,
        },
    }

    # Previously raised AttributeError before any request was ever issued.
    client.update_next_action_process_step("relationship-guid", body)

    assert cap["method"] == "POST"
    assert cap["url"].endswith(
        "/action-author/governance-action-process-steps/next-process-steps/relationship-guid/update"
    )
    sent_body = json.loads(cap["body"]) if isinstance(cap["body"], str) else cap["body"]
    assert sent_body["properties"]["guard"] == "some-guard"
