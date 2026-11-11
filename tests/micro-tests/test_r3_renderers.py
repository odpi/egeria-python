# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""R3: renderers from native values: markdown table cells (LIST), REPORT, and the CLI's Rich table.

Fixtures are raw Egeria JSON captured read-only on laz (report_fixture_replay.py). Where a test needs a
value the data does not hold (a `|`, a newline, a sub-row column), it changes or nests real values and
says so."""
import copy
import importlib.util
import re
from pathlib import Path

import pytest
from rich.console import Console

from commands.cat import run_report
from pyegeria.view import format_set_executor as fse
from pyegeria.view._output_format_models import Column
from pyegeria.view.output_formatter import generate_output, markdown_cell_from_native, populate_common_columns
from pyegeria.view.structured_table import build_structured_table

_spec = importlib.util.spec_from_file_location("report_fixture_replay",
                                               Path(__file__).parent / "report_fixture_replay.py")
replay_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(replay_mod)
ReportReplay, TILES, load_fixture = replay_mod.ReportReplay, replay_mod.TILES, replay_mod.load_fixture


def _run(monkeypatch, name, fmt, **kw):
    fx = ReportReplay(monkeypatch, name).fixture
    return fse.exec_report_spec(fx["spec"], output_format=fmt, params=dict(fx["params"]),
                                view_server="qs-view-server", view_url="https://localhost:9443",
                                user=fx["user"], user_pass="", token="replay-token", **kw)


def _table_rows(markdown):
    lines = [line for line in markdown.splitlines() if line.startswith("| ")]
    header = [h.strip() for h in lines[0].strip().strip("|").split(" | ")]
    return header, [[c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))] for line in lines[1:]]


def _rich(result, width=200):
    console = Console(record=True, width=width)
    run_report.render_structured_table(console, result, "T")
    return console.export_text()


# ── Every surface renders on every fixture ──

@pytest.mark.parametrize("name", TILES)
def test_every_surface_renders_each_fixture(monkeypatch, name):
    listing = _run(monkeypatch, name, "LIST")
    assert listing["kind"] == "text" and "| " in listing["content"]
    report = _run(monkeypatch, name, "REPORT")
    assert report["kind"] == "text" and "## " in report["content"]
    structured = _run(monkeypatch, name, "TABLE", table_shape="structured")
    text = _rich(structured, width=400)
    assert structured["rows"] and str(structured["rows"][0].get("display_name") or "")[:10] in text


# ── Lists are bullets, not commas ──

def test_risk_implications_are_bullets_in_list(monkeypatch):
    header, rows = _table_rows(_run(monkeypatch, "risk_register", "LIST")["content"])
    raw = load_fixture("risk_register")["calls"][-1]["answer"]["elements"]
    first = next(e for e in raw if e["properties"]["displayName"] in rows[0][0])
    items = first["properties"]["implications"]
    assert rows[0][header.index("Implications")] == "<br>".join(items)


def test_risk_implications_are_bullets_in_rich(monkeypatch):
    text = _rich(_run(monkeypatch, "risk_register", "TABLE", table_shape="structured"), width=420)
    assert "• A Responsible Person must be formally" in text


def test_report_shows_lists_as_a_list(monkeypatch):
    content = _run(monkeypatch, "risk_register", "REPORT")["content"]
    assert re.search(r"### Implications\n- \S", content)


def test_join_caps_with_more_names():
    refs = [{"guid": f"g{i}", "qualifiedName": f"QN::{i}", "displayName": f"N{i}"} for i in range(4)]
    assert markdown_cell_from_native(refs, "join", max_items=2) == "QN::0, QN::1 (+2 more: QN::2, QN::3)"
    assert markdown_cell_from_native(refs, "join", max_items=2, label="display_name").startswith("N0, N1")
    assert markdown_cell_from_native(["a", "b", "c"], "bullets", max_items=2) == "a<br>b<br>+1 more"
    assert markdown_cell_from_native({"k": "v", "n": 2}, "kv") == "k: v<br>n: 2"
    assert markdown_cell_from_native(refs, "count") == "4"


def test_a_pipe_and_a_newline_keep_one_row():
    element = copy.deepcopy(load_fixture("risk_register")["calls"][-1]["answer"]["elements"][0])
    element["properties"]["implications"] = ["first | with a pipe", "second\nwith a newline"]
    struct = {"heading": "T", "description": "t", "annotations": {},
              "formats": {"types": ["LIST"], "attributes": [Column(name="Display Name", key="display_name").model_dump(),
                                                           Column(name="Implications", key="implications").model_dump()]}}
    out = generate_output(elements=[element], search_string="x", entity_type="Risk", output_format="LIST",
                          extract_properties_func=populate_common_columns, columns_struct=struct)
    header, rows = _table_rows(out)
    assert len(rows) == 1                                           # one data row (the separator is not "| ")
    assert rows[0][1] == "first \\| with a pipe<br>second<br>with a newline"


# ── The CLI's Rich table ──

def test_a_subtable_prints_as_a_second_rich_table(monkeypatch):
    rows = _run(monkeypatch, "digital_products", "DICT", dict_shape="native")["data"][:2]
    nested = [{"Display Name": "Portfolio", "Products": [{"Display Name": r["Display Name"],
                                                         "Members": r["Members"]} for r in rows]}]
    result = build_structured_table(nested, [{"name": "Display Name", "key": "display_name"},
                                             {"name": "Products", "key": "products"}])
    text = _rich(result)
    assert "2 items · see below" in text
    assert "Portfolio · Products" in text                         # titled "<row name> · <column>"
    assert rows[0]["Display Name"][:20] in text.split("Portfolio · Products")[1]
    assert "third level" in " ".join(result["notes"])


def test_a_narrow_terminal_names_its_dropped_columns(monkeypatch):
    result = _run(monkeypatch, "risk_register", "TABLE", table_shape="structured")
    text = _rich(result, width=60)
    names = [c["name"] for c in result["columns"]]
    fit = 60 // run_report.MIN_COLUMN_WIDTH
    assert f"+{len(names) - fit} more columns: {', '.join(names[fit:])}" in " ".join(text.split())


def test_capped_results_say_so_in_rich(monkeypatch):
    text = _rich(_run(monkeypatch, "digital_products", "TABLE", table_shape="structured"), width=300)
    assert "100 rows shown; the total was not counted." in text
    assert "more may exist" in text


def test_long_text_is_cut_at_max_lines():
    long = "word " * 200
    out = build_structured_table([{"Description": long}], [{"name": "Description", "key": "description",
                                                            "max_lines": 2}])
    cell = run_report._rich_cell(long, out["columns"][0], 30)
    assert cell.endswith("…") and len(cell.splitlines()) == 2


def test_list_generic_asks_for_structured_only_when_told(monkeypatch):
    fx = ReportReplay(monkeypatch, "risk_register").fixture
    kw = dict(params=dict(fx["params"]), view_server="qs-view-server", view_url="https://localhost:9443",
              user=fx["user"], user_pass="")
    monkeypatch.setattr(run_report, "exec_report_spec",
                        lambda *a, **k: fse.exec_report_spec(*a, **{**k, "token": "replay-token"}))
    structured = run_report.list_generic(fx["spec"], output_format="TABLE", table_shape="structured", **kw)
    assert structured["structured"]["kind"] == "table"
    rows = run_report.list_generic(fx["spec"], output_format="TABLE", **kw)   # the default: flat rows (the TUI's)
    assert rows["kind"] == "table" and isinstance(rows["data"], list) and "structured" not in rows
