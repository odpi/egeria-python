"""The Asset-Graph report spec gives each output format a shape that fits a graph (6.2.28):
DICT/TABLE an edge table, LIST the nodes, REPORT/MD/HTML the asset summary with its graph and
edge table, MERMAID the graph, JSON the full response.

Recorded input: `data/asset_graph_by_guid_response.json`, one AssetCatalog.get_asset_graph_by_guid
response from qs-view-server (read only). The executor tests run the real path,
exec_report_spec -> AssetCatalog.get_asset_graph_by_guid -> _async_get_results_body_request ->
_generate_asset_output; only the HTTP request is replaced by the recording.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

import pyegeria.view.base_report_formats as brf
from pyegeria.omvs.asset_catalog import AssetCatalog
from pyegeria.view.format_set_executor import exec_report_spec

pytestmark = pytest.mark.unit

RECORDED = json.loads((Path(__file__).parent / "data" / "asset_graph_by_guid_response.json").read_text())["response"]
GUID = RECORDED["elementHeader"]["guid"]
NAME = RECORDED["properties"]["displayName"]
DECLARED = ["DICT", "TABLE", "LIST", "REPORT", "MD", "HTML", "JSON", "MERMAID"]
EDGE_KEYS = ["From Display Name", "From Type", "From GUID", "Relationship", "To Display Name", "To Type",
             "To GUID"]

# The recorded graph's edges, read off the response by hand (end1 -> end2). The asset's own
# ActionRequester appears both in `relationships` and in `requestedActions`: one edge.
GAPI, ENGINE, CONNECTOR = "bf1d5f61-9d79-41bc-a89a-d863222585ff", "1de658d3-6af5-4c32-b915-5fb6bd5bb524", \
    "fed3e17d-6aa0-4959-8af4-a2cbfde1717b"
PROCESS, STOCK, STAGING = "33884dcc-c0b8-455e-8991-52c704a84d46", "1c365ba1-9f05-4e4c-accc-98fe576ad098", \
    "408e542a-272d-4773-ba9b-4cea3d539f01"
EXPECTED_EDGES = {
    (GAPI, "GovernedBy", PROCESS),        # the asset's own relationship (governedBy)
    (GAPI, "ActionRequester", ENGINE),    # in requestedActions and in relationships
    (CONNECTOR, "ActionRequester", ENGINE),
    (ENGINE, "ActionTarget", STOCK),
    (ENGINE, "ActionTarget", STAGING),
}


class _Response:
    status_code = 200

    def __init__(self, body):
        self._body = body

    def json(self):
        return copy.deepcopy(self._body)


@pytest.fixture
def offline_asset_catalog(monkeypatch):
    """AssetCatalog with no platform: the request returns the recorded graph."""
    calls = []

    def _init(self, view_server, platform_url, user_id=None, user_pwd=None, **_):
        self.view_server, self.platform_url, self.user_id = view_server, platform_url, user_id

    async def _request(self, method, url, payload=None, *a, **k):
        calls.append((method, url))
        return _Response({"class": "AssetGraphResponse", "element": RECORDED})

    # The executor maps every class name to EgeriaTech, which proxies to AssetCatalog; build the
    # AssetCatalog directly so nothing can reach a platform, and fail loudly if EgeriaTech is built.
    import pyegeria.view.format_set_executor as fse
    from pyegeria.egeria_tech_client import EgeriaTech
    real_resolve = fse._resolve_client_and_method

    def _resolve(decl):
        cls, method = real_resolve(decl)
        return (AssetCatalog, method) if decl == "AssetCatalog.get_asset_graph_by_guid" else (cls, method)

    def _no_egeria_tech(self, *a, **k):
        raise AssertionError("the test would have built a real EgeriaTech client")

    monkeypatch.setattr(fse, "_resolve_client_and_method", _resolve)
    monkeypatch.setattr(EgeriaTech, "__init__", _no_egeria_tech)
    monkeypatch.setattr(AssetCatalog, "__init__", _init)
    monkeypatch.setattr(AssetCatalog, "_async_make_request", _request)
    monkeypatch.setattr(AssetCatalog, "create_egeria_bearer_token", lambda self, *a, **k: "token")
    monkeypatch.setattr(AssetCatalog, "close_session", lambda self: None)
    return calls


def _run(fmt):
    return exec_report_spec("Asset-Graph", output_format=fmt, params={"guid": GUID},
                            view_server="qs-view-server", view_url="https://localhost:9443",
                            user="tester", user_pass="unused")


def test_the_spec_declares_a_shape_per_format_and_no_form_or_all():
    spec = brf.base_report_specs["Asset-Graph"]
    assert sorted(t for f in spec.formats for t in f.types) == sorted(DECLARED)
    by_type = {t: f for f in spec.formats for t in f.types}
    assert [c.name for c in by_type["DICT"].attributes] == EDGE_KEYS
    assert [c.name for c in by_type["LIST"].attributes] == ["Display Name", "Type", "GUID", "Role"]
    keys = {c.key for f in spec.formats for c in f.attributes}
    assert "anchorMermaidGRaph" not in keys and "anchorMermaidGraph" in keys
    assert spec.action.function == "AssetCatalog.get_asset_graph_by_guid"
    assert spec.action.required_params == ["guid"]


@pytest.mark.parametrize("fmt", ["DICT", "TABLE"])
def test_dict_and_table_are_one_row_per_edge(offline_asset_catalog, fmt):
    result = _run(fmt)
    assert result["kind"] == "json"
    rows = result["data"]
    assert all(list(r.keys()) == EDGE_KEYS for r in rows)
    assert {(r["From GUID"], r["Relationship"], r["To GUID"]) for r in rows} == EXPECTED_EDGES
    assert len(rows) == len(EXPECTED_EDGES)  # each relationship once
    names = {r["From GUID"]: (r["From Display Name"], r["From Type"]) for r in rows}
    assert names[GAPI] == (NAME, "GovernanceActionProcessInstance")
    assert not any("mermaid" in str(v) or "flowchart" in str(v) for r in rows for v in r.values())
    assert offline_asset_catalog and offline_asset_catalog[0][1].endswith(f"/assets/{GUID}/as-graph")


def test_edge_order_is_deterministic_whatever_order_egeria_returns():
    from pyegeria.view import asset_graph
    shuffled = copy.deepcopy(RECORDED)
    shuffled["relationships"].reverse()
    shuffled = dict(reversed(list(shuffled.items())))
    assert asset_graph.graph_edges(shuffled) == asset_graph.graph_edges(RECORDED)


def test_list_is_the_nodes(offline_asset_catalog):
    result = _run("LIST")
    assert result["kind"] == "text"
    content = result["content"]
    assert "| Display Name | Type | GUID | Role |" in content
    for guid in (GAPI, ENGINE, CONNECTOR, PROCESS, STOCK, STAGING):
        assert content.count(guid) == 1, guid
    assert f"| {NAME} | GovernanceActionProcessInstance | {GAPI} | asset |" in content
    assert "| anchored |" in content and "```mermaid" not in content


@pytest.mark.parametrize("fmt", ["REPORT", "MD"])
def test_report_and_md_are_the_summary_the_graph_and_the_edge_table(offline_asset_catalog, fmt):
    result = _run(fmt)
    assert result["kind"] == "text"
    content = result["content"]
    assert content.startswith(f"# Asset Graph: {NAME}")
    assert "## Asset" in content and f"| GUID | {GUID} |" in content
    assert "## Graph" in content and content.count("```mermaid") == 3  # graph, anchor graph, action graph
    assert f"## Relationships ({len(EXPECTED_EDGES)})" in content
    assert "| " + " | ".join(EDGE_KEYS) + " |" in content
    # Architect P3: a by-GUID fetch is not a search.
    assert "search string" not in content and "Members" not in content


def test_html_is_the_report_rendered(offline_asset_catalog):
    result = _run("HTML")
    assert result["kind"] == "text" and result["mime"] == "text/html"
    content = result["content"]
    assert "<table" in content and "mermaid" in content and NAME in content
    assert "search string" not in content


def test_json_is_the_full_graph(offline_asset_catalog):
    result = _run("JSON")
    assert result["kind"] == "json" and result["data"] == RECORDED


def test_mermaid_is_the_graph(offline_asset_catalog):
    result = _run("MERMAID")
    assert result["kind"] == "text"
    content = result["content"]
    assert content.count("```mermaid") == 1
    from pyegeria.view.output_formatter import _format_mermaid_value
    assert _format_mermaid_value(RECORDED["mermaidGraph"]) in content


@pytest.mark.parametrize("fmt", ["ALL", "FORM"])
def test_a_format_the_spec_does_not_declare_is_an_error_with_words(offline_asset_catalog, fmt):
    with pytest.raises(ValueError) as exc:
        _run(fmt)
    words = str(exc.value)
    assert f"does not support requested output_format '{fmt}'" in words
    assert "Available formats: DICT, HTML, JSON, LIST, MD, MERMAID, REPORT, TABLE." in words
    assert not offline_asset_catalog  # refused before any request


@pytest.mark.parametrize("fmt", DECLARED)
def test_no_declared_format_returns_none_or_one_row_of_mermaid(offline_asset_catalog, fmt):
    result = _run(fmt)
    assert result is not None and result.get("kind") in {"json", "text"}
    assert result.get("data") is not None or result.get("content")
    if isinstance(result.get("data"), list):
        assert len(result["data"]) > 1 or not any("```mermaid" in str(v) for v in result["data"][0].values())


def test_a_graph_with_no_edges_has_an_empty_edge_table_and_says_so():
    from pyegeria.view import asset_graph
    lone = {k: v for k, v in RECORDED.items() if k not in ("relationships", "governedBy", "requestedActions")}
    assert asset_graph.graph_edges(lone) == []
    assert "## Relationships (0)" in asset_graph.render(lone, "REPORT")
    assert "No relationships." in asset_graph.render(lone, "REPORT")
