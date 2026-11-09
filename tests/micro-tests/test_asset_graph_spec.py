"""The Asset-Graph report spec (6.2.28): DICT and JSON for code, REPORT, HTML and MERMAID for people.
DICT is the asset itself with its graph fields, JSON the full graph response, REPORT/HTML the
asset's fields with its graphs rendered, MERMAID the graph (and, from 6.2.29, the action and
activity graphs the element carries). Any other format is refused with words.
The edge helper (pyegeria/view/asset_graph.py), kept for the Wave 3 edge-table spec, is tested
directly at the end, not through the spec.

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
DECLARED = ["DICT", "JSON", "REPORT", "HTML", "MERMAID"]
GRAPH_COLUMNS = {"Mermaid Graph": "mermaidGraph", "Anchor Graph": "anchorMermaidGraph",
                 "Action Graph": "actionMermaidGraph"}
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


def test_the_spec_declares_dict_json_report_html_mermaid_and_the_corrected_key():
    spec = brf.base_report_specs["Asset-Graph"]
    assert sorted(t for f in spec.formats for t in f.types) == sorted(DECLARED)
    keys = {c.key for f in spec.formats for c in f.attributes}
    assert "anchorMermaidGRaph" not in keys
    assert {"mermaidGraph", "anchorMermaidGraph", "actionMermaidGraph"} <= keys
    assert spec.action.function == "AssetCatalog.get_asset_graph_by_guid"
    assert spec.action.required_params == ["guid"]


def test_dict_is_one_row_the_asset_itself_with_its_graph_fields(offline_asset_catalog):
    result = _run("DICT")
    assert result["kind"] == "json"
    rows = result["data"]
    assert isinstance(rows, list) and len(rows) == 1  # the asset, not its related elements
    row = rows[0]
    assert row["GUID"] == GUID and row["Display Name"] == NAME
    for column, key in GRAPH_COLUMNS.items():
        assert row[column] == RECORDED[key], column
    assert offline_asset_catalog and offline_asset_catalog[0][1].endswith(f"/assets/{GUID}/as-graph")


def test_json_is_the_full_graph(offline_asset_catalog):
    result = _run("JSON")
    assert result["kind"] == "json" and result["data"] == RECORDED


def test_report_carries_the_asset_fields_and_every_graph(offline_asset_catalog):
    result = _run("REPORT")
    assert result["kind"] == "text" and result["content"]
    content = result["content"]
    assert NAME in content and GUID in content
    assert content.count("```mermaid") == len(GRAPH_COLUMNS)
    for column in GRAPH_COLUMNS:
        assert f"### {column}" in content, column
    # Architect P3: a fetch by GUID is not a search.
    assert "search string" not in content and "Members" not in content


def test_html_carries_the_graphs(offline_asset_catalog):
    result = _run("HTML")
    assert result["kind"] == "text" and result["mime"] == "text/html"
    content = result["content"]
    assert "mermaid" in content and NAME in content
    assert "search string" not in content


def test_mermaid_is_the_asset_graph_then_its_action_graph(offline_asset_catalog):
    # 6.2.29: the action (and activity) graph follows the context graph when the element carries
    # it, because Egeria's mermaidGraph leaves out Action and Activity relationships.
    result = _run("MERMAID")
    assert result["kind"] == "text"
    content = result["content"]
    assert "activityMermaidGraph" not in RECORDED  # recorded before Egeria shipped it
    assert content.count("```mermaid") == 2
    from pyegeria.view.output_formatter import _format_mermaid_value
    context = _format_mermaid_value(RECORDED["mermaidGraph"])
    action = _format_mermaid_value(RECORDED["actionMermaidGraph"])
    assert context in content and action in content
    assert content.index(context) < content.index(action)
    assert _format_mermaid_value(RECORDED["anchorMermaidGraph"]) not in content


@pytest.mark.parametrize("fmt", ["TABLE", "LIST", "MD", "FORM", "ALL"])
def test_a_format_the_spec_does_not_declare_is_an_error_with_words(offline_asset_catalog, fmt):
    with pytest.raises(ValueError) as exc:
        _run(fmt)
    words = str(exc.value)
    assert f"does not support requested output_format '{fmt}'" in words
    assert "Available formats: DICT, HTML, JSON, MERMAID, REPORT." in words
    assert not offline_asset_catalog  # refused before any request


@pytest.mark.parametrize("fmt", DECLARED)
def test_no_declared_format_returns_none(offline_asset_catalog, fmt):
    result = _run(fmt)
    assert result is not None and result.get("kind") in {"json", "text"}
    assert result.get("data") is not None or result.get("content")


def test_a_search_report_still_names_its_search_string():
    catalog = object.__new__(AssetCatalog)
    out = catalog._generate_asset_output(elements=copy.deepcopy(RECORDED), filter_string="orders",
                                         element_type_name="Asset", output_format="REPORT",
                                         report_spec="Asset-Graph")
    assert "found from the search string:  `orders`" in out


def test_other_specs_keep_the_table_to_dict_fallback():
    # Data-Structures declares DICT and neither TABLE nor ALL: TABLE still gets its DICT format.
    table = brf.select_report_spec("Data-Structures", "TABLE")
    assert table is not None and "DICT" in table["formats"]["types"]
    assert brf.select_report_spec("Asset-Graph", "TABLE") is None
    assert brf.select_report_spec("builtin:Asset-Graph", "TABLE") is None


# ── The edge helper kept for the Wave 3 edge-table spec (not used by Asset-Graph) ──

def test_edge_helper_lists_each_relationship_once_with_its_direction():
    from pyegeria.view import asset_graph
    rows = asset_graph.graph_edges(RECORDED)
    assert all(list(r.keys()) == EDGE_KEYS for r in rows)
    assert {(r["From GUID"], r["Relationship"], r["To GUID"]) for r in rows} == EXPECTED_EDGES
    assert len(rows) == len(EXPECTED_EDGES)


def test_edge_helper_order_is_deterministic_whatever_order_egeria_returns():
    from pyegeria.view import asset_graph
    shuffled = copy.deepcopy(RECORDED)
    shuffled["relationships"].reverse()
    shuffled = dict(reversed(list(shuffled.items())))
    assert asset_graph.graph_edges(shuffled) == asset_graph.graph_edges(RECORDED)


def test_node_helper_lists_the_asset_first_then_anchored_then_related():
    from pyegeria.view import asset_graph
    nodes = asset_graph.graph_nodes(RECORDED)
    assert nodes[0]["guid"] == GAPI and nodes[0]["role"] == "asset"
    assert {n["guid"] for n in nodes} == {GAPI, ENGINE, CONNECTOR, PROCESS, STOCK, STAGING}
    assert [n["role"] for n in nodes] == ["asset", "anchored"] + ["related"] * 4
