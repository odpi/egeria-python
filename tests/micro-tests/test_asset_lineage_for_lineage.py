"""
AssetCatalog.get_asset_lineage_graph_by_guid's for_lineage parameter: omitted
from the request body by default (leaving Egeria's own default in force), sent
as "forLineage": true when set -- so callers no longer need to inject it.
"""
import json

import pytest

from pyegeria.omvs.asset_catalog import AssetCatalog


class _Response:
    def json(self):
        return {"element": {"mermaidGraph": "graph TD"}}


def _client_capturing(bodies: list, monkeypatch) -> AssetCatalog:
    # No live server: skip the constructor's connection check, and use a port
    # nothing listens on so any real network call would fail loudly.
    monkeypatch.setattr(AssetCatalog, "check_connection", lambda self: "test")
    client = AssetCatalog("view-server", "https://localhost:1", "user", "pwd")

    async def fake_make_request(method, url, body=None, *args, **kwargs):
        bodies.append(json.loads(body) if isinstance(body, str) else body)
        return _Response()

    client._async_make_request = fake_make_request
    return client


@pytest.mark.asyncio
@pytest.mark.parametrize("kwargs, expected", [({}, None), ({"for_lineage": True}, True)])
async def test_for_lineage_in_lineage_graph_body(kwargs, expected, monkeypatch):
    bodies: list = []
    client = _client_capturing(bodies, monkeypatch)

    await client._async_get_asset_lineage_graph_by_guid("guid-1", output_format="JSON", **kwargs)

    assert bodies[0].get("forLineage") == expected
    if expected is None:
        assert "forLineage" not in bodies[0]
