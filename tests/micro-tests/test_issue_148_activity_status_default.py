# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Regression test for ISSUE-148 (PYEGERIA_ISSUES.md): seven AssetMaker
action/process queries defaulted `activity_status_list` to ["IN_PROGRESS"],
which silently dropped JournalEntries (no activity status) and every
finished action. The default is now None: no status filter is sent.

No live server needed: a mocked `_async_make_request` captures the body.
"""
import json
from unittest.mock import MagicMock, patch

import pytest

from pyegeria.omvs.asset_maker import AssetMaker

CALLS = [
    ("find_processes", ("*",)),
    ("get_processes_by_category", ("cat",)),
    ("get_action_targets", ("g",)),
    ("get_actions_for_action_target", ("g",)),
    ("get_assigned_actions", ("g",)),
    ("get_actions_for_sponsor", ("g",)),
    ("get_actions_for_requester", ("g",)),
]


def _client():
    with patch("pyegeria.core._base_server_client.BaseServerClient.check_connection", return_value=""):
        return AssetMaker(view_server="vs", platform_url="https://localhost:9443", user_id="u", user_pwd="p")


def _capture(client):
    cap = {}

    async def fake(method, url, body=None, **kwargs):
        cap["url"] = url
        cap["body"] = json.loads(body) if isinstance(body, str) else (body or {})
        resp = MagicMock()
        resp.json = MagicMock(return_value={"elements": []})
        return resp

    client._async_make_request = fake
    return cap


@pytest.mark.parametrize("name,args", CALLS)
def test_default_sends_no_activity_status_filter(name, args):
    client = _client()
    cap = _capture(client)
    getattr(client, name)(*args)
    assert not cap["body"].get("activityStatusList")


@pytest.mark.parametrize("name,args", CALLS)
def test_explicit_filter_is_still_sent(name, args):
    client = _client()
    cap = _capture(client)
    getattr(client, name)(*args, activity_status_list=["IN_PROGRESS"])
    assert cap["body"]["activityStatusList"] == ["IN_PROGRESS"]
