# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Dashboard sheets held in Egeria (BRIEF RS-DASH PR-1, pipeline note v5.5 §8d / §10.6(c)).

The three sheet commands keep their names and syntax and now write the Egeria 6.3 chain:
Dashboard -Schema-> DisplayDataSchemaType -AttributeForSchema-> DisplayDataContainer
-NestedSchemaAttribute(position)-> DisplayDataField per placement, plus DataSetContent (Dashboard -> Report,
queryId = the placement's qualifiedName), ScopedBy (Perspective -> placement) and DataDescription
(placement -> ReportSpec). DB-1: the local JSON store is written too.

Every command goes through the real setup_dispatcher() / V2Dispatcher.dispatch() with an in-memory fake
Egeria (dashboard_fake_egeria.py), so command resolution, parsing and processor routing are the
production ones. No live server.
"""
import json
from typing import Any, Dict

import pytest

from md_processing.dr_egeria import setup_dispatcher
from md_processing.md_processing_utils.common_md_utils import clear_element_dictionary
from md_processing.v2.dashboard_sheet import (
    DashboardSheetEgeriaWriter, LOCAL_ONLY_ENV, perspective_qualified_name,
)
from md_processing.v2.extraction import DrECommand
from pyegeria.view._output_dashboard_sheet_models import DashboardSheetDict

import importlib.util as _ilu
import pathlib as _pl

_spec = _ilu.spec_from_file_location("dashboard_fake_egeria", _pl.Path(__file__).with_name("dashboard_fake_egeria.py"))
fake_egeria = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(fake_egeria)

SHEET = "glossary-health"


@pytest.fixture(autouse=True)
def _store(tmp_path, monkeypatch):
    path = tmp_path / "dashboard_sheets.json"
    monkeypatch.setenv("PYEGERIA_DASHBOARD_SHEETS_STORE", str(path))
    monkeypatch.delenv(LOCAL_ONLY_ENV, raising=False)
    clear_element_dictionary()
    yield path
    clear_element_dictionary()


@pytest.fixture
def egeria():
    fake = fake_egeria.FakeEgeria()
    fake_egeria.seed_perspectives(fake)
    fake.add_entity("Report", "DeployedReport::Coco Terms Total", "Coco Terms Total")
    fake.add_entity("Report", "DeployedReport::Coco Term Counts", "Coco Term Counts")
    fake.add_entity("ReportSpec", "ReportSpec::Glossary-Term-Counts", "Glossary-Term-Counts")
    return fake


def _command(verb: str, object_type: str, attributes: Dict[str, str]) -> DrECommand:
    raw = f"## {verb} {object_type}\n" + "".join(f"### {k}\n{v}\n\n" for k, v in attributes.items())
    return DrECommand(verb=verb, object_type=object_type, attributes=attributes, raw_block=raw)


async def _run(client, verb, object_type, attributes):
    dispatcher = setup_dispatcher(client)
    context: Dict[str, Any] = {"directive": "process"}
    result = await dispatcher.dispatch(_command(verb, object_type, attributes), context)
    assert result["status"] == "success", result
    return result


CREATE = {"Display Name": SHEET, "Dashboard Sheet Heading": "Glossary Health",
          "Dashboard Sheet Description": "How complete and how used the glossaries are.",
          "Dashboard Sheet Family": "Glossary Manager"}
TEXT = {"Dashboard Sheet Name": SHEET, "Placement Name": "Coverage header",
        "MD Content": "**Coverage** - counts and definition completeness per glossary.",
        "Placement Span": "full", "Placement Emphasis": "panel"}
LINK_1 = {"Dashboard Sheet Name": SHEET, "Report Name": "Coco Terms Total", "Placement Span": "1",
          "Placement Emphasis": "kpi", "Placement Perspectives": "Steward, owner",
          "Placement Detail Spec": "Glossary-Term-Counts"}
LINK_2 = {"Dashboard Sheet Name": SHEET, "Report Name": "Coco Term Counts", "Placement Span": "2",
          "Placement Emphasis": "panel", "Placement Perspectives": "steward",
          "Placement Detail Spec": "Glossary-With-Terms"}


async def _document(client):
    await _run(client, "Create", "Dashboard Sheet", CREATE)
    await _run(client, "Add", "Text on Dashboard Sheet", TEXT)
    await _run(client, "Link", "Report to Dashboard Sheet", LINK_1)
    return await _run(client, "Link", "Report to Dashboard Sheet", LINK_2)


def _fields(fake):
    """(position, qualifiedName, props) for each placement, in position order."""
    out = []
    for rel in fake.rels("NestedSchemaAttribute"):
        out.append((rel["props"]["position"], fake.entities[rel["end2"]]["props"]))
    return sorted(out, key=lambda x: x[0])


# ---------------------------------------------------------------------------- create

@pytest.mark.asyncio
async def test_create_sheet_writes_dashboard_schema_and_container(egeria, _store):
    result = await _run(egeria, "Create", "Dashboard Sheet", CREATE)

    dash = egeria.by_qn("Dashboard::glossary-health")
    st = egeria.by_qn("DashboardSchema::glossary-health")
    container = egeria.by_qn("DashboardSheet::glossary-health")
    assert egeria.entities[dash]["type"] == "Dashboard"
    assert egeria.entities[dash]["props"]["displayName"] == "Glossary Health"
    assert egeria.entities[dash]["props"]["description"] == "How complete and how used the glossaries are."
    assert egeria.entities[dash]["props"]["additionalProperties"] == {"family": "Glossary Manager"}
    assert egeria.entities[st]["type"] == "DisplayDataSchemaType"
    assert egeria.entities[container]["type"] == "DisplayDataContainer"
    assert [(r["end1"], r["end2"]) for r in egeria.rels("Schema")] == [(dash, st)]
    afs, = egeria.rels("AttributeForSchema")
    assert (afs["end1"], afs["end2"], afs["props"]["position"]) == (st, container, 1)
    # schema elements are anchored to the Dashboard
    assert egeria.entities[st]["anchor"] == dash and egeria.entities[container]["anchor"] == dash
    # DB-1: the local store is written too
    sheets = DashboardSheetDict.load_from_json(str(_store))
    assert sheets[SHEET].heading == "Glossary Health"
    assert "Egeria**: written" in result["output"]


@pytest.mark.asyncio
async def test_full_document_writes_the_10_6_chain(egeria):
    result = await _document(egeria)

    fields = _fields(egeria)
    assert [(pos, p["qualifiedName"]) for pos, p in fields] == [
        (1, "DashboardPlacement::glossary-health::1::Coverage header"),
        (2, "DashboardPlacement::glossary-health::2::Coco Terms Total"),
        (3, "DashboardPlacement::glossary-health::3::Coco Term Counts"),
    ]
    text, kpi, panel = (p for _, p in fields)
    assert (text["placementKind"], text["span"], text["presentationStyle"]) == ("text", "full", "panel")
    assert text["markdownContent"].startswith("**Coverage**")
    assert (kpi["placementKind"], kpi["span"], kpi["presentationStyle"]) == ("report", "1", "kpi")
    assert kpi.get("markdownContent") is None
    assert kpi["additionalProperties"] == {"placementName": "Coco Terms Total", "perspectives": "Steward,owner",
                                           "detailSpec": "Glossary-Term-Counts"}
    # not the Report's own displayName: Dr.Egeria's untyped `Report Name` lookup must stay unambiguous
    assert kpi["displayName"] == "glossary-health / Coco Terms Total"

    # DataSetContent: Dashboard -> Report, queryId = the placement's qualifiedName, for REPORT placements only
    dash = egeria.by_qn("Dashboard::glossary-health")
    dsc = {(r["end1"], egeria.entities[r["end2"]]["props"]["displayName"], r["props"]["queryId"], r["props"]["queryType"])
           for r in egeria.rels("DataSetContent")}
    assert dsc == {(dash, "Coco Terms Total", kpi["qualifiedName"], "placement"),
                   (dash, "Coco Term Counts", panel["qualifiedName"], "placement")}

    # ScopedBy: Perspective -> placement; "owner" maps to the Trellis element Perspective::Owner (DB-2)
    kpi_guid = egeria.by_qn(kpi["qualifiedName"])
    scopes = sorted(egeria.entities[r["end1"]]["props"]["qualifiedName"]
                    for r in egeria.rels("ScopedBy") if r["end2"] == kpi_guid)
    assert scopes == ["Perspective::Owner", "Perspective::Steward"]

    # DataDescription: placement -> the ReportSpec element; a spec with no element is a note, not silence
    dd = [(r["end1"], egeria.entities[r["end2"]]["props"]["qualifiedName"]) for r in egeria.rels("DataDescription")]
    assert dd == [(kpi_guid, "ReportSpec::Glossary-Term-Counts")]
    assert "Glossary-With-Terms" in result["output"] and "no DataDescription link" in result["output"]

    # membership is not anchoring: nothing created a Report or a Perspective
    assert len(egeria.of_type("Report")) == 2 and len(egeria.of_type("Perspective")) == 12


@pytest.mark.asyncio
async def test_rerunning_the_document_changes_nothing(egeria, _store):
    await _document(egeria)
    writes_after_first = list(egeria.writes)
    store_after_first = _store.read_text()

    result = await _document(egeria)

    assert egeria.writes == writes_after_first, egeria.writes[len(writes_after_first):]
    assert _store.read_text() == store_after_first
    assert "no change" in result["output"]


@pytest.mark.asyncio
async def test_update_changes_only_what_changed(egeria):
    await _document(egeria)
    before = len(egeria.writes)

    await _run(egeria, "Link", "Report to Dashboard Sheet", {**LINK_2, "Placement Span": "full"})
    await _run(egeria, "Create", "Dashboard Sheet", {**CREATE, "Dashboard Sheet Heading": "Glossary Health v2"})

    new = egeria.writes[before:]
    assert [w[0] for w in new] == ["update_schema_attribute", "update_asset"]
    panel = egeria.entities[egeria.by_qn("DashboardPlacement::glossary-health::3::Coco Term Counts")]["props"]
    assert panel["span"] == "full"
    assert egeria.entities[egeria.by_qn("Dashboard::glossary-health")]["props"]["displayName"] == "Glossary Health v2"


@pytest.mark.asyncio
async def test_update_clears_removed_perspectives(egeria):
    await _document(egeria)
    await _run(egeria, "Link", "Report to Dashboard Sheet", {**LINK_1, "Placement Perspectives": "Steward"})
    kpi_qn = "DashboardPlacement::glossary-health::2::Coco Terms Total"
    kpi_guid = egeria.by_qn(kpi_qn)
    scopes = [egeria.entities[r["end1"]]["props"]["qualifiedName"] for r in egeria.rels("ScopedBy") if r["end2"] == kpi_guid]
    assert scopes == ["Perspective::Steward"]
    assert egeria.entities[kpi_guid]["props"]["additionalProperties"]["perspectives"] == "Steward"


# ---------------------------------------------------------------------------- remove / delete

@pytest.mark.asyncio
async def test_remove_placement_deletes_field_and_link_not_report(egeria):
    await _document(egeria)
    reports_before = set(egeria.of_type("Report"))

    writer = DashboardSheetEgeriaWriter(egeria)
    assert await writer.remove_placement(SHEET, "Coco Terms Total") is True

    assert egeria.by_qn("DashboardPlacement::glossary-health::2::Coco Terms Total") is None
    assert [r["props"]["queryId"] for r in egeria.rels("DataSetContent")] == [
        "DashboardPlacement::glossary-health::3::Coco Term Counts"]
    assert set(egeria.of_type("Report")) == reports_before
    assert not [w for w in egeria.writes if w[0] == "delete_asset"]

    # a placement added afterwards takes the next free position, never a taken one
    await _run(egeria, "Link", "Report to Dashboard Sheet", LINK_1)
    assert [pos for pos, _ in _fields(egeria)] == [1, 3, 4]


@pytest.mark.asyncio
async def test_delete_sheet_deletes_chain_only(egeria):
    await _document(egeria)
    keep = set(egeria.of_type("Report")) | set(egeria.of_type("ReportSpec")) | set(egeria.of_type("Perspective"))

    writer = DashboardSheetEgeriaWriter(egeria)
    assert await writer.delete_sheet(SHEET) is True

    assert set(egeria.entities) == keep
    assert not egeria.rels("DataSetContent") and not egeria.rels("ScopedBy")
    deleted_types = sorted(w[1] for w in egeria.writes if w[0].startswith("delete"))
    assert deleted_types == ["Dashboard", "DisplayDataContainer", "DisplayDataField", "DisplayDataField",
                             "DisplayDataField", "DisplayDataSchemaType"]
    assert await DashboardSheetEgeriaWriter(egeria).delete_sheet(SHEET) is False


@pytest.mark.asyncio
async def test_dry_run_writes_nothing_and_lists_every_element(egeria):
    from pyegeria.view._output_dashboard_sheet_models import DashboardSheet, Placement
    sheet = DashboardSheet(name="dry", heading="Dry", placements=[
        Placement(ref="Coco Terms Total", perspectives=["governance"]),
        Placement(ref="Intro", content="hello", span="full", emphasis="panel")])
    writer = DashboardSheetEgeriaWriter(egeria, dry_run=True)
    await writer.write_sheet(sheet)

    assert egeria.writes == []
    creates = [a for a in writer.actions if a.startswith("create")]
    assert creates == ["create Dashboard Dashboard::dry", "create DisplayDataSchemaType DashboardSchema::dry",
                       "create DisplayDataContainer DashboardSheet::dry",
                       "create DisplayDataField DashboardPlacement::dry::1::Coco Terms Total",
                       "create DisplayDataField DashboardPlacement::dry::2::Intro"]
    assert any(a.startswith("link DataSetContent") for a in writer.actions)
    assert any(a.startswith("link ScopedBy Perspective::Governance") for a in writer.actions)


# ---------------------------------------------------------------------------- absences and local-only

@pytest.mark.asyncio
async def test_missing_report_command_is_refused_as_today(egeria, _store):
    """Dr.Egeria refuses `Link Report to Dashboard Sheet` for a Report it cannot find (unchanged): nothing is
    written to Egeria or to the store."""
    await _run(egeria, "Create", "Dashboard Sheet", CREATE)
    writes, store = list(egeria.writes), _store.read_text()
    result = await setup_dispatcher(egeria).dispatch(
        _command("Link", "Report to Dashboard Sheet", {**LINK_2, "Report Name": "No Such Report"}),
        {"directive": "process"})
    assert result["status"] == "failure"
    assert egeria.writes == writes and _store.read_text() == store


@pytest.mark.asyncio
async def test_missing_report_in_migration_is_written_without_link_and_said(egeria):
    from pyegeria.view._output_dashboard_sheet_models import DashboardSheet, Placement
    writer = DashboardSheetEgeriaWriter(egeria)
    await writer.write_sheet(DashboardSheet(name="m", heading="M", placements=[Placement(ref="No Such Report")]))
    assert egeria.by_qn("DashboardPlacement::m::1::No Such Report")
    assert not egeria.rels("DataSetContent")
    assert any("reads as missing" in n for n in writer.notes)


@pytest.mark.asyncio
async def test_missing_perspective_is_written_without_link_and_said(egeria):
    await _run(egeria, "Create", "Dashboard Sheet", CREATE)
    result = await _run(egeria, "Link", "Report to Dashboard Sheet",
                        {**LINK_2, "Placement Perspectives": "Astrologer", "Placement Detail Spec": ""})
    assert not egeria.rels("ScopedBy")
    assert "Perspective 'Astrologer'" in result["output"] and "not created here" in result["output"]
    assert len(egeria.of_type("Perspective")) == 12


@pytest.mark.asyncio
async def test_local_only_writes_store_alone_and_says_so(egeria, _store, monkeypatch):
    monkeypatch.setenv(LOCAL_ONLY_ENV, "1")
    result = await _document(egeria)

    assert egeria.writes == []
    assert "not written" in result["output"] and LOCAL_ONLY_ENV in result["output"]
    sheets = DashboardSheetDict.load_from_json(str(_store))
    assert [p.ref for p in sheets[SHEET].placements] == ["Coverage header", "Coco Terms Total", "Coco Term Counts"]


@pytest.mark.asyncio
async def test_local_only_sheet_is_written_whole_on_next_egeria_command(egeria, monkeypatch):
    monkeypatch.setenv(LOCAL_ONLY_ENV, "1")
    await _run(egeria, "Create", "Dashboard Sheet", CREATE)
    await _run(egeria, "Add", "Text on Dashboard Sheet", TEXT)
    monkeypatch.delenv(LOCAL_ONLY_ENV)

    result = await _run(egeria, "Link", "Report to Dashboard Sheet", LINK_1)

    assert [p["additionalProperties"]["placementName"] for _, p in _fields(egeria)] == [
        "Coverage header", "Coco Terms Total"]
    assert "only in the local store" in result["output"]


def test_perspective_mapping_db2():
    assert perspective_qualified_name("governance") == "Perspective::Governance"
    assert perspective_qualified_name("owner") == "Perspective::Owner"          # Trellis "Data Owner"
    assert perspective_qualified_name("Data Owner") == "Perspective::Owner"
    assert perspective_qualified_name("engineer") == "Perspective::Data Expert"
    assert perspective_qualified_name("builder") == "Perspective::App/AI Builder"
    assert perspective_qualified_name("data expert") == "Perspective::Data Expert"
    assert perspective_qualified_name("Perspective::Steward") == "Perspective::Steward"


# ---------------------------------------------------------------------------- Create Report

REPORT = {"Display Name": "Coco Glossaries", "Report Spec": "Glossary-With-Terms", "Output Format": "MD",
          "Page Size": "25", "Search String": "Coco"}


def _report_props(fake):
    guid = fake.by_qn(next(e["props"]["qualifiedName"] for e in fake.entities.values()
                           if e["props"].get("displayName") == "Coco Glossaries"))
    return guid, fake.entities[guid]["props"]


@pytest.mark.asyncio
@pytest.mark.parametrize("prefix", ["ReportSpec::", "ReportType::"])
async def test_create_report_writes_parameters_and_report_type_instance(prefix):
    fake = fake_egeria.FakeEgeria()
    spec_type = "ReportSpec" if prefix == "ReportSpec::" else "ReportType"
    spec_guid = fake.add_entity(spec_type, f"{prefix}Glossary-With-Terms", "Glossary-With-Terms")

    result = await _run(fake, "Create", "Report", REPORT)

    report_guid, props = _report_props(fake)
    assert props["outputFormat"] == "MD"
    assert json.loads(props["reportParameters"]) == {"page_size": 25, "search_string": "Coco"}
    assert props["additionalProperties"]["reportSpec"] == "Glossary-With-Terms"  # kept one release
    assert [(r["end1"], r["end2"]) for r in fake.rels("ReportTypeInstance")] == [(spec_guid, report_guid)]
    assert "no ReportTypeInstance" not in result["output"]

    # re-run: the link is not duplicated
    await _run(fake, "Create", "Report", REPORT)
    assert len(fake.rels("ReportTypeInstance")) == 1


@pytest.mark.asyncio
async def test_create_report_spec_without_element_says_so():
    fake = fake_egeria.FakeEgeria()
    result = await _run(fake, "Create", "Report", REPORT)
    assert not fake.rels("ReportTypeInstance")
    assert "has no Egeria element" in result["output"]
    assert "ReportSpec::Glossary-With-Terms and ReportType::Glossary-With-Terms" in result["output"]


@pytest.mark.asyncio
async def test_create_report_relinks_when_spec_changes():
    fake = fake_egeria.FakeEgeria()
    old = fake.add_entity("ReportSpec", "ReportSpec::Glossary-With-Terms", "Glossary-With-Terms")
    new = fake.add_entity("ReportSpec", "ReportSpec::Glossary-Term-Counts", "Glossary-Term-Counts")
    await _run(fake, "Create", "Report", REPORT)
    await _run(fake, "Create", "Report", {**REPORT, "Report Spec": "Glossary-Term-Counts"})
    report_guid, _ = _report_props(fake)
    assert [(r["end1"], r["end2"]) for r in fake.rels("ReportTypeInstance")] == [(new, report_guid)]
    assert old in fake.entities  # a spec is never deleted


@pytest.mark.asyncio
async def test_report_found_when_its_name_is_shared_with_another_type(egeria):
    """Live 2026-11-09: a Report whose displayName another element also has (and a longer Report name that
    contains it) is still found -- exact displayName among Reports only."""
    from pyegeria.view._output_dashboard_sheet_models import DashboardSheet, Placement
    report = egeria.add_entity("Report", "X::Report::TDC", "Term Definition Completeness")
    egeria.add_entity("Report", "X::Report::TDC-metric", "Term Definition Completeness Metric Report")
    egeria.add_entity("GovernanceMetric", "X::Metric::TDC", "Term Definition Completeness")
    writer = DashboardSheetEgeriaWriter(egeria)
    await writer.write_sheet(DashboardSheet(name="s", heading="S",
                                            placements=[Placement(ref="Term Definition Completeness")]))
    assert [r["end2"] for r in egeria.rels("DataSetContent")] == [report]
    assert writer.notes == []


@pytest.mark.asyncio
async def test_two_reports_with_one_name_is_a_note_not_a_guess(egeria):
    from pyegeria.view._output_dashboard_sheet_models import DashboardSheet, Placement
    egeria.add_entity("Report", "X::Report::1", "Twin")
    egeria.add_entity("Report", "X::Report::2", "Twin")
    writer = DashboardSheetEgeriaWriter(egeria)
    await writer.write_sheet(DashboardSheet(name="s", heading="S", placements=[Placement(ref="Twin")]))
    assert not egeria.rels("DataSetContent")
    assert any("2 Reports are named 'Twin'" in n for n in writer.notes)


# ---------------------------------------------------------------------------- read-back P3s (2026-11-09)

@pytest.mark.asyncio
async def test_migrate_after_removal_never_reuses_a_position(egeria):
    from pyegeria.view._output_dashboard_sheet_models import DashboardSheet, Placement
    for name in ("A", "B", "C", "D"):
        egeria.add_entity("Report", f"R::{name}", name)
    writer = DashboardSheetEgeriaWriter(egeria)
    await writer.write_sheet(DashboardSheet(name="p", heading="P", placements=[Placement(ref=n) for n in "ABC"]))
    await writer.remove_placement("p", "B")
    await writer.write_sheet(DashboardSheet(name="p", heading="P", placements=[Placement(ref=n) for n in "ACD"]))
    positions = sorted((rel["props"]["position"], egeria.entities[rel["end2"]]["props"]["additionalProperties"]["placementName"])
                       for rel in egeria.rels("NestedSchemaAttribute"))
    assert positions == [(1, "A"), (3, "C"), (4, "D")]


@pytest.mark.asyncio
async def test_sheet_with_duplicate_placement_names_is_refused_before_any_write(egeria):
    from pyegeria.view._output_dashboard_sheet_models import DashboardSheet, Placement
    sheet = DashboardSheet(name="dup", heading="Dup", placements=[
        Placement(ref="Coco Terms Total", emphasis="kpi"), Placement(ref="Coco Terms Total", emphasis="panel")])
    with pytest.raises(ValueError, match="more than one placement named 'Coco Terms Total'"):
        await DashboardSheetEgeriaWriter(egeria).write_sheet(sheet)
    assert egeria.writes == []


@pytest.mark.asyncio
async def test_text_placement_cannot_take_a_report_placements_name(egeria, _store):
    await _document(egeria)
    writes, store = list(egeria.writes), _store.read_text()
    result = await setup_dispatcher(egeria).dispatch(
        _command("Add", "Text on Dashboard Sheet", {**TEXT, "Placement Name": "Coco Terms Total"}),
        {"directive": "process"})
    assert result["status"] == "failure"
    assert "already has a report placement named 'Coco Terms Total'" in json.dumps(result)
    assert egeria.writes == writes and _store.read_text() == store


@pytest.mark.asyncio
async def test_link_command_finds_a_report_whose_name_another_type_shares(egeria):
    """Dr.Egeria's untyped lookup is ambiguous here (and refused live); the command's typed lookup is not."""
    report = egeria.add_entity("Report", "X::Report::TDC", "Term Definition Completeness")
    egeria.add_entity("GovernanceMetric", "X::Metric::TDC", "Term Definition Completeness")
    await _run(egeria, "Create", "Dashboard Sheet", CREATE)
    await _run(egeria, "Link", "Report to Dashboard Sheet",
               {**LINK_2, "Report Name": "Term Definition Completeness", "Placement Detail Spec": ""})
    assert [r["end2"] for r in egeria.rels("DataSetContent")] == [report]
