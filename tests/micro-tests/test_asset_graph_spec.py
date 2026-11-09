"""The Asset-Graph report spec renders Egeria's asset graph in every format it declares (6.2.28).

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
DECLARED = ["DICT", "TABLE", "JSON", "REPORT", "HTML", "MERMAID"]
GRAPH_COLUMNS = {"Mermaid Graph": "mermaidGraph", "Anchor Graph": "anchorMermaidGraph",
                 "Action Graph": "actionMermaidGraph"}


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


def test_the_spec_declares_exactly_the_graph_formats_and_the_corrected_key():
    spec = brf.base_report_specs["Asset-Graph"]
    types = sorted(t for f in spec.formats for t in f.types)
    assert types == sorted(DECLARED)
    keys = {c.key for f in spec.formats for c in f.attributes}
    assert "anchorMermaidGRaph" not in keys
    assert {"mermaidGraph", "anchorMermaidGraph", "actionMermaidGraph"} <= keys
    assert spec.action.function == "AssetCatalog.get_asset_graph_by_guid"
    assert spec.action.required_params == ["guid"]


@pytest.mark.parametrize("fmt", ["DICT", "TABLE"])
def test_dict_and_table_are_one_row_the_asset_itself_with_its_graphs(offline_asset_catalog, fmt):
    result = _run(fmt)
    assert result["kind"] == "json"
    rows = result["data"]
    assert isinstance(rows, list) and len(rows) == 1  # the asset, not its related elements
    row = rows[0]
    assert row["GUID"] == GUID and row["Display Name"] == NAME
    for column, key in GRAPH_COLUMNS.items():
        assert row[column] == RECORDED[key], column
    assert offline_asset_catalog and offline_asset_catalog[0][1].endswith(f"/assets/{GUID}/as-graph")


def test_json_is_the_raw_graph(offline_asset_catalog):
    result = _run("JSON")
    assert result["kind"] == "json" and result["data"]["mermaidGraph"] == RECORDED["mermaidGraph"]


def test_report_carries_the_asset_fields_and_every_graph(offline_asset_catalog):
    result = _run("REPORT")
    assert result["kind"] == "text" and result["content"]
    content = result["content"]
    assert NAME in content and GUID in content
    assert content.count("```mermaid") == len(GRAPH_COLUMNS)
    for column in GRAPH_COLUMNS:
        assert f"### {column}" in content, column


def test_html_carries_the_graphs(offline_asset_catalog):
    result = _run("HTML")
    assert result["kind"] == "text" and result["mime"] == "text/html"
    assert "mermaid" in result["content"] and NAME in result["content"]


def test_mermaid_is_the_asset_graph(offline_asset_catalog):
    result = _run("MERMAID")
    assert result["kind"] == "text"
    content = result["content"]
    assert content.count("```mermaid") == 1
    # Exactly the recorded asset graph (mermaidGraph) as the formatter renders it, not the anchor
    # or action graph.
    from pyegeria.view.output_formatter import _format_mermaid_value
    assert _format_mermaid_value(RECORDED["mermaidGraph"]) in content
    for other in ("anchorMermaidGraph", "actionMermaidGraph"):
        assert _format_mermaid_value(RECORDED[other]) not in content


@pytest.mark.parametrize("fmt", ["ALL", "MD", "FORM", "LIST"])
def test_a_format_the_spec_does_not_declare_is_an_error_with_words(offline_asset_catalog, fmt):
    with pytest.raises(ValueError) as exc:
        _run(fmt)
    words = str(exc.value)
    assert f"does not support requested output_format '{fmt}'" in words
    assert "Available formats: DICT, HTML, JSON, MERMAID, REPORT, TABLE." in words
    assert not offline_asset_catalog  # refused before any request


@pytest.mark.parametrize("fmt", DECLARED)
def test_no_declared_format_returns_none_or_empty(offline_asset_catalog, fmt):
    result = _run(fmt)
    assert result is not None and result.get("kind") in {"json", "text"}
    assert result.get("data") is not None or result.get("content")
