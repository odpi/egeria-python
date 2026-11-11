# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""R1: native extraction, the structured TABLE (`table_shape="structured"`) and native DICT
(`dict_shape="native"`), BRIEFS-R1-R2-R3-PYEGERIA-STRUCTURED-TABLE-2026-11-11.

The key gate is the golden comparison: every default output (TABLE, DICT, LIST, REPORT, MD, FORM, and
MERMAID for the ISC register) on the five CDO-sheet fixtures is byte-identical to the fix-now head
(rs-fix-now 289f9e6b), with only the "created at <minute>" stamp normalised. Fixtures are raw Egeria
JSON captured read-only on laz and replayed through the whole stack (report_fixture_replay.py).
"""
import asyncio
import copy
import hashlib
import importlib.util
import json
import re
from pathlib import Path

import pytest

import pyegeria.view.base_report_formats as brf
import pyegeria.view.overview_metrics as om
from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.view import format_set_executor as fse
from pyegeria.view._output_format_models import ActionParameter, Format, FormatSet
from pyegeria.view.analytic_registry import (AnalyticFunctionSpec, clear_runtime_analytic_functions,
                                             register_analytic_functions)
from pyegeria.view.output_formatter import _legacy_text, related_ref
from pyegeria.view.structured_table import build_structured_table, reduce_third_level, value_type

_spec = importlib.util.spec_from_file_location("report_fixture_replay",
                                               Path(__file__).parent / "report_fixture_replay.py")
replay_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(replay_mod)
ReportReplay, TILES = replay_mod.ReportReplay, replay_mod.TILES

GOLDEN = json.loads((Path(__file__).parent / "data" / "report_specs" / "golden_default_outputs.json").read_text())
FORMATS = ["TABLE", "DICT", "LIST", "REPORT", "MD", "FORM"]


def _run(replay, output_format, **kw):
    fx = replay.fixture
    return fse.exec_report_spec(fx["spec"], output_format=output_format, params=dict(fx["params"]),
                                view_server="qs-view-server", view_url="https://localhost:9443",
                                user=fx["user"], user_pass="", token="replay-token", **kw)


def _golden_text(result):
    text = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, default=str)
    return re.sub(r"created at \d{4}-\d{2}-\d{2} \d{2}:\d{2}", "created at <time>", text)


# ── The gate: default outputs are byte-identical to the fix-now head ──

@pytest.mark.parametrize("case", sorted(GOLDEN))
def test_default_outputs_are_byte_identical(monkeypatch, case):
    name, fmt = case.split("/")
    replay = ReportReplay(monkeypatch, name)
    try:
        text = _golden_text(_run(replay, fmt))
    except Exception as e:  # noqa: BLE001 -- an error is part of the default output too
        text = f"ERROR {type(e).__name__}: {e}"
    assert {"sha256": hashlib.sha256(text.encode()).hexdigest(), "bytes": len(text.encode())} == GOLDEN[case]


def test_the_golden_covers_every_tile_and_format():
    assert set(GOLDEN) == {f"{t}/{f}" for t in TILES for f in FORMATS} | {"isc_register/MERMAID"}


# ── Legacy text comes from the native layer ──

def test_legacy_text_is_derived_from_native_values():
    refs = [{"guid": "g1", "qualifiedName": "QN::a", "displayName": "A"}, {"guid": "g2", "displayName": "B"},
            {"guid": "g3"}]
    assert _legacy_text(refs) == "QN::a, B"                         # QN first; an unnamed one is left out
    assert _legacy_text([{"name": "Task"}, {"name": "Campaign"}]) == "Task, Campaign"
    assert _legacy_text(["quarantine", "PROJ-CT-TBDF"]) == "quarantine, PROJ-CT-TBDF"
    assert _legacy_text(None) == ""


def test_related_ref_keeps_both_names(monkeypatch):
    item = replay_mod.load_fixture("digital_products")["calls"][1]["answer"]["elements"][0]["collectionMembers"][0]
    ref = related_ref(item)
    assert set(ref) == {"guid", "qualifiedName", "displayName", "type"}
    assert ref["type"] == "SolutionComponent"


# ── The structured TABLE ──

EXPECTED_TYPES = {
    "risk_register": {"Implications": "list", "Authors": "list", "Description": "text", "Display Name": "scalar"},
    "governance_metrics": {"Implications": "list", "Outcomes": "list", "Authors": "list"},
    "ninety_day_plan": {"Success Criteria": "list", "Mission": "text"},
    "digital_products": {"License": "elements", "Members": "elements", "Product Manager": "elements"},
    "isc_register": {"Containing Members": "elements"},
}


@pytest.mark.parametrize("name", TILES)
def test_structured_shape_on_each_fixture(monkeypatch, name):
    out = _run(ReportReplay(monkeypatch, name), "TABLE", table_shape="structured")
    assert out["kind"] == "table"
    assert set(out) >= {"kind", "columns", "rows", "total", "shown", "notes"}
    by_name = {c["name"]: c for c in out["columns"]}
    for col, t in EXPECTED_TYPES[name].items():
        assert by_name[col]["type"] == t, (col, by_name[col])
    for c in out["columns"]:
        assert set(c) == {"key", "name", "type", "render", "detail_spec", "valid_values", "max_items", "max_lines"}
        assert c["render"]
    keys = {c["key"] for c in out["columns"]}
    assert all(set(r) <= keys for r in out["rows"])               # rows are keyed by column key
    assert out["shown"] == len(out["rows"])


def test_structured_renders_default_by_type(monkeypatch):
    cols = {c["name"]: c for c in _run(ReportReplay(monkeypatch, "risk_register"), "TABLE",
                                       table_shape="structured")["columns"]}
    assert cols["Implications"]["render"] == "bullets" and cols["Description"]["render"] == "text"


def test_structured_native_values(monkeypatch):
    out = _run(ReportReplay(monkeypatch, "digital_products"), "TABLE", table_shape="structured")
    row = out["rows"][0]
    assert isinstance(row["members"], list) and {"guid", "qualifiedName", "displayName"} <= set(row["members"][0])
    assert isinstance(row["assigned_actors"][0]["displayName"], str)


def test_total_shown_and_notes_when_capped(monkeypatch):
    out = _run(ReportReplay(monkeypatch, "digital_products"), "TABLE", table_shape="structured")
    assert out["shown"] == 100 and out["total"] is None
    assert out["notes"][0] == "Showing the first 100: the query stopped at its page size of 100; more may exist."


def test_total_is_the_row_count_when_not_capped(monkeypatch):
    out = _run(ReportReplay(monkeypatch, "risk_register"), "TABLE", table_shape="structured")
    assert out["total"] == out["shown"] == 12


def test_a_third_level_is_reduced_with_a_note(monkeypatch):
    rows = _run(ReportReplay(monkeypatch, "digital_products"), "DICT", dict_shape="native")["data"][:2]
    sub_rows = [{"Display Name": r["Display Name"], "Members": r["Members"]} for r in rows]  # real refs, nested
    out = build_structured_table([{"Products": sub_rows}], [{"name": "Products", "key": "products"}])
    cell = out["rows"][0]["products"]
    assert out["columns"][0]["type"] == "table"
    assert cell[0]["Members"]["count"] == len(rows[0]["Members"]) and cell[0]["Members"]["names"]
    assert any("third level" in n for n in out["notes"])
    assert reduce_third_level({"guid": "g", "displayName": "X"}) == {"count": 1, "names": ["X"], "guid": "g"}


def test_value_types():
    assert value_type("short") == "scalar" and value_type("x" * 200) == "text" and value_type("a\nb") == "text"
    assert value_type(["a"]) == "list" and value_type({"k": 1}) == "map"
    assert value_type([{"guid": "g"}]) == "elements" and value_type([{"Name": "a"}]) == "table"
    assert value_type([]) is None


# ── Native DICT ──

def test_native_dict_has_lists_and_objects_where_flat_has_strings(monkeypatch):
    replay = ReportReplay(monkeypatch, "digital_products")
    flat = _run(replay, "DICT")["data"][0]
    native = _run(replay, "DICT", dict_shape="native")["data"][0]
    assert isinstance(flat["Members"], str) and isinstance(native["Members"], list)
    assert native["Members"][0]["qualifiedName"] in flat["Members"]
    assert list(flat) == list(native)                               # same columns, same order


def test_native_dict_zones_and_classifications_are_lists(monkeypatch):
    rows = _run(ReportReplay(monkeypatch, "ninety_day_plan"), "DICT", dict_shape="native")["data"]
    assert all(isinstance(r.get("Zone Membership"), list) for r in rows)


def test_dict_shape_native_leaves_table_flat(monkeypatch):
    replay = ReportReplay(monkeypatch, "risk_register")
    assert _run(replay, "TABLE", dict_shape="native") == _run(replay, "TABLE")


@pytest.mark.parametrize("kw, words", [({"table_shape": "fancy"}, "table_shape must be one of rows, structured"),
                                      ({"dict_shape": "deep"}, "dict_shape must be one of flat, native")])
def test_unknown_shapes_are_refused(monkeypatch, kw, words):
    with pytest.raises(ValueError, match=words):
        _run(ReportReplay(monkeypatch, "risk_register"), "TABLE", **kw)


def test_rows_shape_is_the_default(monkeypatch):
    replay = ReportReplay(monkeypatch, "risk_register")
    assert _run(replay, "TABLE", table_shape="rows") == _run(replay, "TABLE")


# ── table_shape is ignored for DOCUMENT, charts and KPIs ──

@pytest.fixture
def toy_routines(monkeypatch):
    monkeypatch.setattr(om, "_r1_kpi", lambda **k: 7, raising=False)
    monkeypatch.setattr(om, "_r1_series", lambda **k: [{"label": "a", "value": 1}, {"label": "b", "value": 2}],
                        raising=False)
    monkeypatch.setattr(om, "_r1_doc", lambda **k: {"text": "{}"}, raising=False)
    register_analytic_functions({n: AnalyticFunctionSpec(name=n, function=f"pyegeria.view.overview_metrics._{n}")
                                 for n in ("r1_kpi", "r1_series", "r1_doc")})
    brf.register_report_specs({
        "R1-KPI": FormatSet(heading="K", description="k", action=ActionParameter(analytic_function="r1_kpi"),
                            formats=[Format(types=["DICT", "TABLE"], attributes=[])]),
        "R1-Series": FormatSet(heading="S", description="s", action=ActionParameter(analytic_function="r1_series"),
                               formats=[Format(types=["DICT"], attributes=[])]),
        "R1-Doc": FormatSet(heading="D", description="d", action=ActionParameter(analytic_function="r1_doc"),
                            formats=[Format(types=["DOCUMENT"], document={"standard": "s", "media_type":
                                                                          "application/json", "file_name": "d.json"})]),
    }, source="test")
    yield
    clear_runtime_analytic_functions()
    brf.clear_runtime_report_specs()


def _plain(name, fmt, **kw):
    return fse.exec_report_spec(name, output_format=fmt, params={}, view_server="vs", view_url="https://x",
                                user="u", user_pass="p", **kw)


def test_table_shape_is_ignored_for_kpis_charts_and_documents(toy_routines):
    assert _plain("R1-KPI", "TABLE", table_shape="structured") == _plain("R1-KPI", "TABLE")
    assert _plain("R1-Series", "SERIES", table_shape="structured")["kind"] == "json"
    assert _plain("R1-Doc", "DOCUMENT", table_shape="structured")["kind"] == "document"


# ── The async twin matches ──

def _async_run(name, fmt, **kw):
    replay_fx = replay_mod.load_fixture(name)
    client = EgeriaTech("qs-view-server", "https://localhost:9443", user_id="erinoverview", user_pwd="")
    client.set_bearer_token("replay-token")
    return asyncio.run(fse._async_run_report(replay_fx["spec"], client, output_format=fmt,
                                             params=dict(replay_fx["params"]), **kw))


@pytest.mark.parametrize("fmt, kw", [("TABLE", {"table_shape": "structured"}), ("DICT", {"dict_shape": "native"})])
def test_the_async_twin_matches(monkeypatch, fmt, kw):
    replay = ReportReplay(monkeypatch, "risk_register")
    sync = _run(replay, fmt, **kw)
    a = _async_run("risk_register", fmt, **kw)
    sync.pop("spec_source", None), a.pop("spec_source", None)
    assert a == sync
