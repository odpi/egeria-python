# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Report-spec rendering fix-now (BRIEF-REPORT-SPEC-FIX-NOW-2026-11-11, F1-F10), pyegeria 6.2.37.

Every element here is real: captured read-only on laz (erinoverview) from the tiles of the CDO sheet
"How the Data Governance Program is Going" by scripts/capture_report_fixtures.py and replayed through
the whole pyegeria stack (report_fixture_replay.py). Where a test needs a value the real data does
not hold (a second classification, a `|`, a False), it changes one field of a real element and
says so.
"""
import copy
import importlib.util
import json
import re
from pathlib import Path

import pytest
from rich.console import Console

from commands.cat import run_report
from pyegeria.view import format_set_executor as fse
from pyegeria.view._output_format_models import Column, Format, FormatSet
from pyegeria.view.base_report_formats import select_report_spec
from pyegeria.view.output_formatter import (DIAGRAM_OMITTED, generate_output, list_item_name, make_md_attribute,
                                            markdown_cell, populate_common_columns)

_spec = importlib.util.spec_from_file_location("report_fixture_replay",
                                               Path(__file__).parent / "report_fixture_replay.py")
replay_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(replay_mod)
ReportReplay, load_fixture = replay_mod.ReportReplay, replay_mod.load_fixture


def _elements(name):
    fx = load_fixture(name)
    return next(c["answer"]["elements"] for c in fx["calls"] if isinstance(c["answer"].get("elements"), list))


def _struct(columns, types=("ALL",)):
    fs = FormatSet(heading="T", description="t", formats=[Format(types=list(types), attributes=columns)])
    return {"heading": "T", "description": "t", "formats": fs.formats[0].dict(), "annotations": {}}


def _render(elements, columns, fmt):
    return generate_output(elements=elements, search_string="x", entity_type="Thing", output_format=fmt,
                           extract_properties_func=populate_common_columns, columns_struct=_struct(columns))


# ── F1: header classifications are joined with ", " (no stray newline) ──

@pytest.mark.parametrize("fmt", ["REPORT", "LIST", "MD"])
def test_f1_two_classifications_join_with_a_comma(fmt):
    element = copy.deepcopy(next(e for e in _elements("ninety_day_plan") if e["elementHeader"].get("projectKinds")))
    second = copy.deepcopy(element["elementHeader"]["projectKinds"][0])
    second["classificationName"] = "Campaign"                     # a second real-shape classification
    element["elementHeader"]["projectKinds"].append(second)
    out = _render([element], [Column(name="Kinds", key="project_kinds")], fmt)
    assert "Task, Campaign" in out
    assert "\n, " not in out


# ── F2: REPORT/MD/FORM show False and 0 ──

@pytest.mark.parametrize("fmt", ["REPORT", "MD", "FORM"])
def test_f2_false_and_zero_render(fmt):
    element = copy.deepcopy(_elements("risk_register")[0])
    element["properties"]["domainIdentifier"] = 0                  # a real int property, set to 0
    element["properties"]["isOwnAnchor"] = False
    out = _render([element], [Column(name="Domain Identifier", key="domain_identifier"),
                              Column(name="Is Own Anchor", key="is_own_anchor")], fmt)
    assert re.search(r"### Domain Identifier\n0\n", out), out[:600]
    assert re.search(r"### Is Own Anchor\nFalse\n", out)


# ── F3: FORM/MD say a diagram is omitted (camelCase key matches too); links render ──

@pytest.mark.parametrize("fmt", ["FORM", "MD"])
def test_f3_diagram_omission_is_said(fmt):
    element = _elements("isc_register")[0]
    out = _render([element], [Column(name="Display Name", key="display_name"),
                              Column(name="Mermaid", key="mermaid")], fmt)
    assert f"### Mermaid\n{DIAGRAM_OMITTED}" in out
    assert "flowchart" not in out and "mindmap" not in out


def test_f3_camel_case_blueprint_graph_and_links():
    assert make_md_attribute("solutionBlueprintMermaidGraph", "flowchart TD\nA-->B", "MD") == \
        f"### Solution Blueprint Mermaid Graph\n{DIAGRAM_OMITTED}\n\n"
    assert make_md_attribute("links", "a, b", "FORM") == "### Links\na, b\n\n"
    assert make_md_attribute("implemented by", "Comp X", "MD") == "### Implemented By\nComp X\n\n"
    assert make_md_attribute("sub_components", "c1, c2", "MD") == "### Sub Components\nc1, c2\n\n"
    assert make_md_attribute("Mermaid", "", "MD") == "\n"           # nothing to omit


# ── F4: CLI cells never reduce a list to a bare count; maps are one cell ──

def test_f4_list_of_scalars_shows_items_and_more():
    long = [f"Implication number {i} about the programme" for i in range(6)]
    cell = run_report._flatten({"Implications": long})["Implications"]
    shown = cell.split(" (+")[0].split(", ")
    assert cell.startswith("Implication number 0") and cell.endswith(f"(+{6 - len(shown)} more)")
    assert 1 <= len(shown) <= 3 and "6 items" not in cell
    assert run_report._flatten({"Authors": ["a", "b", "c", "d", "e"]})["Authors"] == "a, b, c, d, e"  # fits


def test_f4_objects_cut_at_120_say_more_and_maps_stay_one_cell():
    rows = [{"name": f"Member element with a fairly long display name {i}"} for i in range(8)]
    cell = run_report._flatten({"Members": rows})["Members"]
    assert len(cell) < 160 and re.search(r"\(\+\d+ more\)$", cell)
    flat = run_report._flatten({"Display Name": "x", "Additional Properties": {"contactName": "Robbie", "n": 2}})
    assert list(flat) == ["Display Name", "Additional Properties"]
    assert flat["Additional Properties"] == "contactName: Robbie; n: 2"


# ── F5: the CLI drops columns from the end of the author's order and names them ──

def test_f5_hidden_columns_are_named(monkeypatch):
    replay = ReportReplay(monkeypatch, "risk_register")
    rows = replay.run("DICT")["data"]
    console = Console(record=True, width=400)
    run_report._render_table(console, "Risk", "cap", rows, use_pager=False)
    text = console.export_text()
    names = list(rows[0].keys())
    assert len(names) > 12
    assert f"+{len(names) - 12} more columns: {', '.join(names[12:])}" in text
    shown, dropped = run_report._collect_columns(run_report._ensure_rows(rows))
    assert shown == names[:12] and dropped == names[12:]


# ── F6: LIST never drops a nameless object ──

def test_f6_nameless_items_fall_back():
    assert list_item_name({"description": "only a description"}) == "only a description"
    assert list_item_name({"count": 3, "type": {"typeName": "Annotation"}}) == "(unnamed Annotation)"
    assert list_item_name({"count": 3}) == "(unnamed item)"


def test_f6_list_cell_keeps_every_item():
    element = copy.deepcopy(_elements("risk_register")[0])
    element["properties"]["implications"] = [{"description": "first, unnamed"}, {"count": 2}]
    out = _render([element], [Column(name="Implications", key="implications")], "LIST")
    assert "first, unnamed, (unnamed item)" in out


# ── F7: relationship columns read Egeria's field names and show display names ──

def test_f7_members_and_product_manager(monkeypatch):
    rows = ReportReplay(monkeypatch, "digital_products").run("DICT")["data"]
    assert all(r["Members"] for r in rows)                          # collectionMembers, on all 100
    pm = [r["Product Manager"] for r in rows if r["Product Manager"]]
    assert pm and all("_productManager" not in v and v.startswith("Product Manager for") for v in pm)
    assert not any("LicenseType::" in (r["License"] or "") for r in rows)


def test_f7_absent_relationships_are_genuinely_none(monkeypatch):
    """Uses/Used by/Solution Blueprint: Egeria omits an empty list, and none of the 100 carries one."""
    replay = ReportReplay(monkeypatch, "digital_products")
    raw = _elements("digital_products")
    for field in ("usesDigitalProducts", "usedByDigitalProducts", "solutionDesigns"):
        assert not any(field in e for e in raw)
    rows = replay.run("DICT")["data"]
    assert all(r["Uses Products"] in (None, "") and r["Solution Blueprint"] in (None, "") for r in rows)


# ── F8: a result that filled its page says so; page_size is a whole number or refused ──

def test_f8_capped_dict_and_text_say_so(monkeypatch):
    replay = ReportReplay(monkeypatch, "digital_products")
    words = "Showing the first 100: the query stopped at its page size of 100; more may exist."
    assert replay.run("DICT")["notes"] == [words]
    report = replay.run("REPORT")
    assert report["notes"] == [words] and f"_{words}_" in report["content"]


def test_f8_uncapped_results_carry_no_note(monkeypatch):
    out = ReportReplay(monkeypatch, "risk_register").run("DICT")
    assert "notes" not in out and len(out["data"]) == 12


def test_f8_cli_prints_the_note(monkeypatch):
    out = ReportReplay(monkeypatch, "digital_products").run("DICT")
    console = Console(record=True, width=300)
    run_report._render_table(console, "DP", "cap", out["data"], use_pager=False, notes=out["notes"])
    assert "more may exist" in console.export_text()


@pytest.mark.parametrize("value, expected", [("5", 5), (5, 5), (" 20 ", 20), ("", None)])
def test_f8_page_size_numbers_are_accepted(value, expected):
    assert fse.coerce_paging_params({"page_size": value}).get("page_size") == (expected if value != "" else "")


@pytest.mark.parametrize("value", ["abc", "-1", True, "1.5"])
def test_f8_page_size_otherwise_is_refused_in_words(value):
    with pytest.raises(ValueError, match="page_size must be a whole number of 0 or more"):
        fse.coerce_paging_params({"page_size": value})


# ── F9: markdown cells escape | and turn newlines into <br>, keeping emphasis ──

def test_f9_markdown_cell():
    assert markdown_cell("a | b\nc") == "a \\| b<br>c"
    assert markdown_cell("**Likelihood:** Low — x") == "**Likelihood:** Low — x"


def test_f9_risk_description_in_a_list_keeps_one_row():
    element = copy.deepcopy(_elements("risk_register")[0])
    element["properties"]["description"] += "\nSecond line | with a pipe"
    out = _render([element], [Column(name="Display Name", key="display_name"),
                              Column(name="Description", key="description")], "LIST")
    rows = [line for line in out.splitlines() if line.startswith("| ") and "---" not in line][1:]
    assert len(rows) == 1
    assert "**Likelihood:**" in rows[0] and "—" in rows[0]
    assert "<br>Second line \\| with a pipe" in rows[0]


def test_f9_flat_dict_table_is_escaped():
    out = make_md_attribute("Additional Properties", {"contact": "a|b", "note": "x\ny"}, "REPORT")
    assert "| Contact | a\\|b |" in out and "| Note | x<br>y |" in out


# ── F10: format='bulleted-list' works outside LIST ──

@pytest.mark.parametrize("fmt", ["REPORT", "MD"])
def test_f10_bulleted_list_in_report_and_md(fmt):
    element = copy.deepcopy(_elements("risk_register")[0])
    items = element["properties"]["implications"]
    assert isinstance(items, list) and len(items) >= 2
    out = _render([element], [Column(name="Implications", key="implications", format="bulleted-list")], fmt)
    assert f"### Implications\n- {items[0]}\n- {items[1]}" in out


def test_f10_bulleted_list_in_a_table_cell():
    element = copy.deepcopy(_elements("risk_register")[0])
    out = _render([element], [Column(name="Implications", key="implications", format="bulleted-list")], "LIST")
    assert "<br> - " in out
