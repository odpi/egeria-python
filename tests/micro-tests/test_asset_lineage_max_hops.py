"""
AssetCatalog lineage-graph parameters added for Egeria 6.3 (odpi/egeria#9420):
max_hops -> "maxHops" and skip_relationships -> "skipRelationships" are sent
only when set, so a call to a 6.2 platform is byte-identical to before; a
per-call timeout reaches _async_make_request; and the Asset-Lineage-Hops
output says when the graph was cut instead of presenting it as complete.
"""
import json

import pytest

from pyegeria.omvs.asset_catalog import (
    AssetCatalog,
    LINEAGE_HOPS_REPORT_SPEC,
    lineage_hop_summary,
)


def _node(guid, name, hops=None, cut=None):
    node = {
        "elementHeader": {
            "guid": guid,
            "type": {"typeName": "DataSet"},
            "origin": {"homeMetadataCollectionId": "mc-1"},
            "versions": {"createdBy": "user", "version": 1},
        },
        "properties": {"displayName": name, "qualifiedName": f"DataSet::{name}"},
    }
    if hops is not None:
        node["hopsFromStart"] = hops
    if cut is not None:
        node["hopLimitReached"] = cut
    return node


def _graph_63(cut: bool):
    graph = _node("g0", "start", 0, False)
    graph["mermaidGraph"] = "graph TD"
    graph["linkedAssets"] = [_node("g1", "one", 1, False), _node("g2", "two", 2, cut)]
    return graph


def _graph_62():
    graph = _node("g0", "start")
    graph["mermaidGraph"] = "graph TD"
    graph["linkedAssets"] = [_node("g1", "one"), _node("g2", "two")]
    return graph


class _Response:
    def __init__(self, element):
        self._element = element

    def json(self):
        return {"element": self._element}


def _client_capturing(calls: list, monkeypatch, element=None) -> AssetCatalog:
    # No live server: skip the constructor's connection check, and use a port
    # nothing listens on so any real network call would fail loudly.
    monkeypatch.setattr(AssetCatalog, "check_connection", lambda self: "test")
    client = AssetCatalog("view-server", "https://localhost:1", "user", "pwd")

    async def fake_make_request(method, url, body=None, *args, **kwargs):
        calls.append({"body": json.loads(body) if isinstance(body, str) else body, "kwargs": kwargs})
        return _Response(element if element is not None else {"mermaidGraph": "graph TD"})

    client._async_make_request = fake_make_request
    return client


@pytest.mark.asyncio
async def test_unset_fields_are_omitted(monkeypatch):
    calls: list = []
    client = _client_capturing(calls, monkeypatch)

    await client._async_get_asset_lineage_graph_by_guid("guid-1", output_format="JSON")

    body = calls[0]["body"]
    assert "maxHops" not in body
    assert "skipRelationships" not in body
    assert "timeout" not in calls[0]["kwargs"]


@pytest.mark.asyncio
@pytest.mark.parametrize("max_hops", [0, 3])
async def test_max_hops_sent_including_zero(max_hops, monkeypatch):
    calls: list = []
    client = _client_capturing(calls, monkeypatch)

    await client._async_get_asset_lineage_graph_by_guid("guid-1", max_hops=max_hops, output_format="JSON")

    assert calls[0]["body"]["maxHops"] == max_hops


@pytest.mark.asyncio
async def test_skip_relationships_and_timeout_passed(monkeypatch):
    calls: list = []
    client = _client_capturing(calls, monkeypatch)

    await client._async_get_asset_lineage_graph_by_guid(
        "guid-1",
        relationship_types=["LineageRelationship"],
        skip_relationships=["DataSetContent"],
        timeout=300,
        output_format="JSON",
    )

    assert calls[0]["body"]["includeOnlyRelationships"] == ["LineageRelationship"]
    assert calls[0]["body"]["skipRelationships"] == ["DataSetContent"]
    assert calls[0]["kwargs"]["timeout"] == 300


def test_sync_and_mermaid_wrappers_pass_through(monkeypatch):
    calls: list = []
    client = _client_capturing(calls, monkeypatch)

    client.get_asset_lineage_graph_by_guid("guid-1", max_hops=2, timeout=90, output_format="JSON")
    client.get_asset_lineage_mermaid_graph("guid-1", max_hops=0, skip_relationships=["DataMapping"])

    assert calls[0]["body"]["maxHops"] == 2
    assert calls[0]["kwargs"]["timeout"] == 90
    assert calls[1]["body"]["maxHops"] == 0
    assert calls[1]["body"]["skipRelationships"] == ["DataMapping"]


def test_summary_reports_cut():
    summary = lineage_hop_summary(_graph_63(cut=True), max_hops=2)

    assert summary["complete"] is False
    assert summary["hopLimitReachedCount"] == 1
    assert summary["cutAtHops"] == 2
    assert summary["summary"].startswith("Graph cut at 2 hops · 1 element continues past the limit")


def test_summary_reports_complete():
    summary = lineage_hop_summary(_graph_63(cut=False))

    assert summary["complete"] is True
    assert summary["maxHopsFromStart"] == 2
    assert summary["summary"].startswith("Complete graph")


def test_summary_on_pre_63_platform_is_unknown_not_complete():
    summary = lineage_hop_summary(_graph_62())

    assert summary["complete"] is None
    assert summary["hopLimitReachedCount"] is None
    assert "unknown" in summary["summary"]


@pytest.mark.asyncio
async def test_hops_report_spec_lists_nodes_with_summary(monkeypatch):
    calls: list = []
    client = _client_capturing(calls, monkeypatch, element=_graph_63(cut=True))

    result = await client._async_get_asset_lineage_graph_by_guid(
        "guid-1", max_hops=2, output_format="DICT", report_spec=LINEAGE_HOPS_REPORT_SPEC
    )

    assert result["lineageSummary"]["complete"] is False
    nodes = result["nodes"]
    assert [n["GUID"] for n in nodes] == ["g0", "g1", "g2"]
    assert [n["Hops From Start"] for n in nodes] == [0, 1, 2]
    assert nodes[2]["Hop Limit Reached"] is True


@pytest.mark.asyncio
async def test_hops_report_spec_markdown_starts_with_summary(monkeypatch):
    calls: list = []
    client = _client_capturing(calls, monkeypatch, element=_graph_63(cut=True))

    result = await client._async_get_asset_lineage_graph_by_guid(
        "guid-1", max_hops=2, output_format="MD", report_spec=LINEAGE_HOPS_REPORT_SPEC
    )

    assert isinstance(result, str)
    assert result.startswith("Graph cut at 2 hops")
