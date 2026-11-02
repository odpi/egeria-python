# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""find_note_logs takes graph_query_depth as a named parameter.

At the default depth each log's noteLogEntries are inlined, and page_size bounds
logs, not entries, so listing logs on a server with two large system logs took
about 30 s (Trellis Coordinator, 2026-10-31). graph_query_depth=0 lists logs
only; it used to reach the request only through **kwargs. The default (3) is
unchanged.
"""
import json

import pytest

from pyegeria.omvs.asset_maker import AssetMaker

pytestmark = pytest.mark.unit


class _Response:
    def json(self):
        return {"elements": []}


def _client(monkeypatch, bodies):
    monkeypatch.setattr(AssetMaker, "check_connection", lambda self: "test")
    client = AssetMaker("view-server", "https://localhost:1", "user", "pwd")

    async def fake_make_request(method, url, body=None, *args, **kwargs):
        bodies.append(json.loads(body) if isinstance(body, str) else body)
        return _Response()

    client._async_make_request = fake_make_request
    return client


@pytest.mark.parametrize("kwargs,expected", [({}, 3), ({"graph_query_depth": 0}, 0)])
def test_graph_query_depth_reaches_the_request(monkeypatch, kwargs, expected):
    bodies = []
    _client(monkeypatch, bodies).find_note_logs("*", **kwargs)
    assert bodies[0]["graphQueryDepth"] == expected


async def test_async_graph_query_depth_reaches_the_request(monkeypatch):
    bodies = []
    await _client(monkeypatch, bodies)._async_find_note_logs("*", graph_query_depth=0)
    assert bodies[0]["graphQueryDepth"] == 0
