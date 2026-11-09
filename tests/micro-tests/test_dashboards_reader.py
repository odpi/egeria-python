# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Dashboard sheets held in Egeria: the reader (BRIEF RS-DASH PR-2).

Gate: a round trip on fakes. Every live sheet's JSON (the five sheets in the Portal's store, copied read
only on 2026-11-09 to data/dashboard_sheets_live_2026_11_09.json) -> Egeria elements (through the PR-1
writer, as `migrate` does) -> DashboardSheet gives an EQUAL model: order, span, style, perspectives, text
and refs. Plus the two absence cases, worded; the registry's EGERIA tier; migrate's idempotence.
"""
import importlib.util
import json
import pathlib

import pytest

from md_processing.v2.dashboard_sheet import DashboardSheetEgeriaWriter
from pyegeria.view import dashboard_sheet_registry as registry
from pyegeria.view._output_dashboard_sheet_models import DashboardSheet, DashboardSheetDict
from pyegeria.view.dashboards import (
    REPORT_LINK_MISSING, EgeriaDashboardSheet, as_local_model, async_list_dashboard_sheets,
    async_load_dashboard_sheet, async_migrate_dashboard_sheets,
)

_HERE = pathlib.Path(__file__).parent
_spec = importlib.util.spec_from_file_location("dashboard_fake_egeria", _HERE / "dashboard_fake_egeria.py")
fake_egeria = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fake_egeria)

LIVE = json.loads((_HERE / "data" / "dashboard_sheets_live_2026_11_09.json").read_text())


def _egeria_with_reports(sheets: dict):
    fake = fake_egeria.FakeEgeria()
    fake_egeria.seed_perspectives(fake)
    for sheet in sheets.values():
        for p in sheet["placements"]:
            if p.get("content") is None and not fake.by_qn(f"DeployedReport::{p['ref']}"):
                fake.add_entity("Report", f"DeployedReport::{p['ref']}", p["ref"])
    return fake


def test_fixture_is_the_five_live_sheets():
    assert sorted(LIVE) == sorted(["Chief Data Officer Dashboard", "local-dashboards-next-steps",
                                   "Assets by Type and Location Demo", "digital-product-portfolio",
                                   "my-team-dashboard"])
    placements = [p for s in LIVE.values() for p in s["placements"]]
    assert len(placements) == 40
    assert sum(1 for p in placements if p.get("content") is not None) == 10


@pytest.mark.asyncio
@pytest.mark.parametrize("name", sorted(LIVE))
async def test_round_trip_every_live_sheet(name):
    fake = _egeria_with_reports(LIVE)
    original = DashboardSheet(**LIVE[name])

    await DashboardSheetEgeriaWriter(fake).write_sheet(original)
    loaded = await async_load_dashboard_sheet(fake, name)

    assert isinstance(loaded, EgeriaDashboardSheet) and loaded.breaks == []
    assert as_local_model(loaded) == original
    assert all(p.kind in ("report", "text") and p.note is None for p in loaded.placements)
    # still the base model, so consumers keep their code
    assert isinstance(loaded, DashboardSheet)


@pytest.mark.asyncio
async def test_list_returns_all_live_sheets_and_migrate_is_idempotent():
    fake = _egeria_with_reports(LIVE)
    store = DashboardSheetDict({k: DashboardSheet(**v) for k, v in LIVE.items()})

    first = await async_migrate_dashboard_sheets(fake, store)
    writes = list(fake.writes)
    second = await async_migrate_dashboard_sheets(fake, store)

    assert fake.writes == writes
    assert all(not [a for a in w.actions if not a.startswith("unchanged")] for w in second.values())
    sheets = await async_list_dashboard_sheets(fake)
    assert [s.name for s in sheets] == sorted(LIVE, key=str.lower)
    assert {s.name: as_local_model(s) for s in sheets} == {k: DashboardSheet(**v) for k, v in LIVE.items()}
    # element counts: per sheet Dashboard + schema type + container, one field per placement
    assert len(fake.of_type("Dashboard")) == 5 and len(fake.of_type("DisplayDataField")) == 40
    assert len(fake.rels("DataSetContent")) == 30
    assert sum(len(w.actions) for w in first.values()) > 0
    # DB-3: owned by the migrating user (the fake has none, so owner is given), set once
    assert [w for w in writes if w[0] == "add_ownership"] == []  # no owner known -> not classified


@pytest.mark.asyncio
async def test_migrate_sets_ownership_once_db3():
    fake = _egeria_with_reports(LIVE)
    store = DashboardSheetDict({k: DashboardSheet(**v) for k, v in LIVE.items()})
    await async_migrate_dashboard_sheets(fake, store, only="my-team-dashboard", owner="garygeeke")
    await async_migrate_dashboard_sheets(fake, store, only="my-team-dashboard", owner="garygeeke")
    owned = [w for w in fake.writes if w[0] == "add_ownership"]
    assert owned == [("add_ownership", fake.by_qn("Dashboard::my-team-dashboard"), "garygeeke")]


@pytest.mark.asyncio
async def test_dry_run_migrate_writes_nothing():
    fake = _egeria_with_reports(LIVE)
    store = DashboardSheetDict({k: DashboardSheet(**v) for k, v in LIVE.items()})
    results = await async_migrate_dashboard_sheets(fake, store, dry_run=True)
    assert fake.writes == []
    creates = [a for w in results.values() for a in w.actions if a.startswith("create")]
    assert len(creates) == 5 * 3 + 40
    assert not [a for w in results.values() for a in w.actions if a.startswith("classify")]  # no owner known


@pytest.mark.asyncio
async def test_dry_run_lists_ownership():
    fake = _egeria_with_reports(LIVE)
    store = DashboardSheetDict({k: DashboardSheet(**v) for k, v in LIVE.items()})
    results = await async_migrate_dashboard_sheets(fake, store, only="my-team-dashboard", dry_run=True,
                                                   owner="erinoverview")
    assert "classify Ownership Dashboard::my-team-dashboard (owner erinoverview)" in results["my-team-dashboard"].actions
    assert fake.writes == []


@pytest.mark.asyncio
async def test_rename_writes_a_scratch_copy():
    fake = _egeria_with_reports(LIVE)
    store = DashboardSheetDict({k: DashboardSheet(**v) for k, v in LIVE.items()})
    await async_migrate_dashboard_sheets(fake, store, only="my-team-dashboard",
                                         rename="scratch-my-team-dashboard")
    loaded = await async_load_dashboard_sheet(fake, "scratch-my-team-dashboard")
    expected = DashboardSheet(**{**LIVE["my-team-dashboard"], "name": "scratch-my-team-dashboard"})
    assert as_local_model(loaded) == expected
    assert await async_load_dashboard_sheet(fake, "my-team-dashboard") is None


# ---------------------------------------------------------------------------- absences, in words

@pytest.mark.asyncio
async def test_report_link_gone_reads_missing():
    fake = _egeria_with_reports(LIVE)
    name = "digital-product-portfolio"
    await DashboardSheetEgeriaWriter(fake).write_sheet(DashboardSheet(**LIVE[name]))
    gone = next(r for r in fake.rels("DataSetContent") if r["props"]["queryId"].endswith("::Total Products Count"))
    fake.relationships.remove(gone)

    loaded = await async_load_dashboard_sheet(fake, name)

    first = loaded.placements[0]
    assert (first.kind, first.ref, first.note) == ("missing", "Total Products Count", REPORT_LINK_MISSING)
    assert [p.kind for p in loaded.placements[1:]] == ["report"] * 3


@pytest.mark.asyncio
async def test_broken_chain_is_listed_with_the_break_named():
    fake = _egeria_with_reports(LIVE)
    await DashboardSheetEgeriaWriter(fake).write_sheet(DashboardSheet(**LIVE["my-team-dashboard"]))
    fake.relationships = [r for r in fake.relationships if r["type"] != "AttributeForSchema"]
    fake.add_entity("Dashboard", "Dashboard::plain", "A plain Create Dashboard")  # no chain at all

    sheets = {s.name: s for s in await async_list_dashboard_sheets(fake)}

    assert sheets["my-team-dashboard"].breaks == [
        "no sheet container: the DisplayDataSchemaType has no AttributeForSchema link to a DisplayDataContainer"]
    assert sheets["plain"].breaks == [
        "no layout schema: the Dashboard has no Schema link to a DisplayDataSchemaType"]
    assert sheets["plain"].heading == "A plain Create Dashboard" and sheets["plain"].placements == []


@pytest.mark.asyncio
async def test_unknown_sheet_is_none():
    assert await async_load_dashboard_sheet(fake_egeria.FakeEgeria(), "nope") is None


# ---------------------------------------------------------------------------- registry tier

@pytest.fixture
def clean_registry(monkeypatch):
    monkeypatch.delenv("PYEGERIA_DASHBOARD_SHEETS_JSON", raising=False)
    monkeypatch.delenv("PYEGERIA_DASHBOARD_SHEETS_MODULES", raising=False)
    registry.refresh_dashboard_sheets()
    registry.clear_runtime_dashboard_sheets()
    registry.clear_egeria_dashboard_sheets()
    yield
    registry.clear_runtime_dashboard_sheets()
    registry.clear_egeria_dashboard_sheets()
    registry.refresh_dashboard_sheets()


def test_local_overrides_egeria_with_one_warning(clean_registry, tmp_path, monkeypatch):
    egeria_a = EgeriaDashboardSheet(name="a", heading="A from Egeria")
    egeria_b = EgeriaDashboardSheet(name="b", heading="B from Egeria")
    registry.set_egeria_dashboard_sheets([egeria_a, egeria_b])
    path = tmp_path / "local.json"
    path.write_text(json.dumps({"a": {"name": "a", "heading": "A local"}}))
    monkeypatch.setenv("PYEGERIA_DASHBOARD_SHEETS_JSON", str(path))
    registry.refresh_dashboard_sheets()

    warnings = []
    handler = registry.logger.add(lambda m: warnings.append(m), level="WARNING")
    try:
        combined = registry.get_dashboard_sheet_registry()
        registry.get_dashboard_sheet_registry()
    finally:
        registry.logger.remove(handler)

    assert combined["a"].heading == "A local" and combined["b"].heading == "B from Egeria"
    assert registry.get_dashboard_sheet_tier("a") == "local"
    assert registry.get_dashboard_sheet_tier("b") == "egeria"
    assert len([w for w in warnings if "'a'" in w]) == 1


def test_runtime_registration_may_shadow_egeria(clean_registry):
    registry.set_egeria_dashboard_sheets([EgeriaDashboardSheet(name="x", heading="X from Egeria")])
    registry.register_dashboard_sheets({"x": DashboardSheet(name="x", heading="X runtime")})
    assert registry.get_dashboard_sheet_registry()["x"].heading == "X runtime"


# ---------------------------------------------------------------------------- drift (read-back P3, 2026-11-09)

async def _cdo_with_link_edits(edit):
    fake = _egeria_with_reports(LIVE)
    name = "Chief Data Officer Dashboard"
    await DashboardSheetEgeriaWriter(fake).write_sheet(DashboardSheet(**LIVE[name]))
    edit(fake)
    loaded = await async_load_dashboard_sheet(fake, name)
    return fake, {p.ref: p for p in loaded.placements}


@pytest.mark.asyncio
async def test_extra_scopedby_link_is_a_note():
    def edit(fake):
        field = fake.by_qn("DashboardPlacement::Chief Data Officer Dashboard::4::Governance Metrics Defined")
        fake.relationships.append({"guid": "x1", "type": "ScopedBy", "end1": fake.by_qn("Perspective::Privacy"),
                                   "end2": field, "props": {}})
    _, placements = await _cdo_with_link_edits(edit)
    p = placements["Governance Metrics Defined"]
    assert p.perspectives == ["governance"]  # the stored labels stay the value
    assert p.note == "ScopedBy link(s) to Perspective::Privacy are not in the stored perspectives"


@pytest.mark.asyncio
async def test_removed_scopedby_link_is_a_note():
    def edit(fake):
        field = fake.by_qn("DashboardPlacement::Chief Data Officer Dashboard::7::Data Asset Ownership")
        owner = fake.by_qn("Perspective::Owner")
        fake.relationships = [r for r in fake.relationships
                              if not (r["type"] == "ScopedBy" and r["end1"] == owner and r["end2"] == field)]
    _, placements = await _cdo_with_link_edits(edit)
    assert placements["Data Asset Ownership"].note == "stored perspective(s) owner have no ScopedBy link in Egeria"


@pytest.mark.asyncio
async def test_unexplained_datadescription_link_is_a_note():
    def edit(fake):
        spec = fake.add_entity("ReportSpec", "ReportSpec::Something-Else", "Something-Else")
        field = fake.by_qn("DashboardPlacement::Chief Data Officer Dashboard::4::Governance Metrics Defined")
        fake.relationships.append({"guid": "x2", "type": "DataDescription", "end1": field, "end2": spec, "props": {}})
    _, placements = await _cdo_with_link_edits(edit)
    assert placements["Governance Metrics Defined"].note == (
        "DataDescription links to ReportSpec::Something-Else, but the stored drill-down is Governance-Metric-DrE-Basic")
