# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
ISSUE-136: the note reads defaulted their type filter to "Action". Note is a
subtype of Notification, which is a subtype of Action, so Notes still came
back -- but so did every other Action subtype (a note log can hold
Notifications that are not Notes, and find_notes searches all assets). The
defaults are now "Note"; a caller can still pass another type.
"""
import json

import pytest

from pyegeria.core._server_client import ServerClient


class _Response:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def _client(calls: list, payload: dict, monkeypatch) -> ServerClient:
    monkeypatch.setattr(ServerClient, "check_connection", lambda self: "test")
    client = ServerClient("view-server", "https://localhost:1", "user", "pwd")

    async def fake_make_request(method, url, body=None, *args, **kwargs):
        calls.append((url, json.loads(body) if isinstance(body, str) else body))
        return _Response(payload)

    client._async_make_request = fake_make_request
    return client


@pytest.mark.asyncio
async def test_get_notes_for_note_log_defaults_to_note(monkeypatch):
    calls: list = []
    client = _client(calls, {"elements": []}, monkeypatch)

    await client._async_get_notes_for_note_log("log-guid")

    url, body = calls[0]
    assert url.endswith("feedback-manager/note-logs/log-guid/notes/retrieve")
    assert body["metadataElementTypeName"] == "Note"


@pytest.mark.asyncio
async def test_get_notes_for_note_log_type_can_be_widened(monkeypatch):
    calls: list = []
    client = _client(calls, {"elements": []}, monkeypatch)

    await client._async_get_notes_for_note_log("log-guid", metadata_element_type_name="Notification")

    assert calls[0][1]["metadataElementTypeName"] == "Notification"


@pytest.mark.asyncio
async def test_get_note_by_guid_defaults_to_note(monkeypatch):
    calls: list = []
    client = _client(calls, {"element": {}}, monkeypatch)

    await client._async_get_note_by_guid("note-guid")

    url, body = calls[0]
    # Served by Asset Maker's /assets/{assetGUID}/retrieve under the feedback-manager url marker.
    assert url.endswith("feedback-manager/assets/note-guid/retrieve")
    assert body["metadataElementTypeName"] == "Note"


@pytest.mark.asyncio
async def test_find_notes_defaults_to_note(monkeypatch):
    calls: list = []
    client = _client(calls, {"elements": []}, monkeypatch)

    await client._async_find_notes("*")

    url, body = calls[0]
    assert url.endswith("feedback-manager/assets/by-search-string")
    assert body["metadataElementTypeName"] == "Note"
