# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Regression test for ISSUE-74 (PYEGERIA_ISSUES.md): ProjectManager's
_async_create_project / _async_update_project / _async_create_project_task
all built their default ProjectProperties body with a "name" key instead
of "displayName" -- the real Egeria property name (confirmed against
Egeria-api-project-manager.http, the ground truth). The wrong key is
silently ignored server-side: the call reports success, but the display
name is never actually set/changed.

No live server needed: patches _async_make_request to capture the JSON
body that would have been sent, instead of making a real HTTP call.
"""
import json
from unittest.mock import patch

import pytest

from pyegeria.omvs.project_manager import ProjectManager


class _FakeResponse:
    def json(self):
        return {"guid": "fake-guid"}


def _make_client() -> ProjectManager:
    # BaseServerClient.__init__ does its own live connectivity probe
    # (check_connection()) before any mock can be installed, so
    # check_connection is patched out for the duration of client
    # construction -- otherwise this file would silently depend on a
    # reachable Egeria platform despite living in tests/micro-tests/.
    with patch("pyegeria.core._base_server_client.BaseServerClient.check_connection", return_value=""):
        return ProjectManager(view_server="fake-view", platform_url="https://fake:9443",
                               user_id="fake-user", user_pwd="fake-pwd")


def _capture_body(client, monkeypatch):
    captured = {}

    async def _fake_make_request(method, url, json_body=None, is_json=True, **kwargs):
        captured["body"] = json.loads(json_body) if isinstance(json_body, str) else json_body
        return _FakeResponse()

    monkeypatch.setattr(client, "_async_make_request", _fake_make_request)
    return captured


@pytest.mark.asyncio
async def test_create_project_sends_display_name_not_name(monkeypatch):
    client = _make_client()
    captured = _capture_body(client, monkeypatch)

    await client._async_create_project(display_name="My Project", identifier="proj-1")

    props = captured["body"]["properties"]
    assert props.get("displayName") == "My Project"
    assert "name" not in props


@pytest.mark.asyncio
async def test_update_project_sends_display_name_not_name(monkeypatch):
    client = _make_client()
    captured = _capture_body(client, monkeypatch)

    await client._async_update_project("proj-guid-1", display_name="Renamed Project")

    props = captured["body"]["properties"]
    assert props.get("displayName") == "Renamed Project"
    assert "name" not in props


@pytest.mark.asyncio
async def test_create_project_task_sends_display_name_not_name(monkeypatch):
    client = _make_client()
    captured = _capture_body(client, monkeypatch)

    await client._async_create_project_task("proj-guid-1", display_name="My Task")

    props = captured["body"]["properties"]
    assert props.get("displayName") == "My Task"
    assert "name" not in props
