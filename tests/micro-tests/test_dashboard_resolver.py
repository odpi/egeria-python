# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
The shared dashboard data step, resolve_dashboard_sheet (BRIEF EA-CATCHUP-AND-DASHBOARDS B4 / D4, §4.7).

On fakes: a viewer-aware Egeria that behaves as Egeria's access security connector does (checked in its
Java): an element in a zone the viewer cannot see is DROPPED from relationship reads, searches and type
listings, while an explicit read by GUID is refused with OPEN-METADATA-SECURITY-403-020. Cases: visible,
restricted Report, restricted ReportSpec, missing (gone, and link-gone with no recorded GUID), text,
order and perspective, a refused token, per-viewer listing, run=True, and the five live sheets.
"""
import importlib.util
import json
import pathlib

import httpx
import pytest

from md_processing.v2.dashboard_sheet import DashboardSheetEgeriaWriter
from pyegeria.core._exceptions import PyegeriaUnauthorizedException
from pyegeria.view import dashboard_resolver as dr
from pyegeria.view._output_dashboard_sheet_models import DashboardSheet, Placement
from pyegeria.view.dashboards import REPORT_LINK_MISSING, async_load_dashboard_sheet

_HERE = pathlib.Path(__file__).parent
_spec = importlib.util.spec_from_file_location("dashboard_fake_egeria", _HERE / "dashboard_fake_egeria.py")
fake_egeria = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fake_egeria)

LIVE = json.loads((_HERE / "data" / "dashboard_sheets_live_2026_11_09.json").read_text())


class NotVisible(Exception):
    """What pyegeria raises for Egeria's explicit-read refusal (the message id is what matters)."""


class ViewerEgeria(fake_egeria.FakeEgeria):
    """FakeEgeria as seen by one viewer: GUIDs in `hidden` are in a zone they cannot see."""

    def __init__(self):
        super().__init__()
        self.hidden = set()
        self.token_refused = False
        self.user_id = "viewer"

    def _visible(self, items):
        if not isinstance(items, list):
            return items
        kept = [e for e in items if (e.get("elementHeader") or {}).get("guid") not in self.hidden]
        return kept or "No elements found"

    async def _async_get_element_by_guid_(self, guid, **kwargs):
        if self.token_refused:
            raise PyegeriaUnauthorizedException(httpx.Response(401, request=httpx.Request("POST", "http://x")),
                                                {"caller method": "test"}, {"userid": "viewer"})
        if guid in self.hidden:
            raise NotVisible(f"OPEN-METADATA-SECURITY-403-020 User viewer is not authorized to issue an operation "
                             f"read on Report element {guid}")
        return await super()._async_get_element_by_guid_(guid)

    async def _async_get_related_elements(self, *a, **k):
        return self._visible(await super()._async_get_related_elements(*a, **k))

    async def _async_get_elements_by_property_value(self, *a, **k):
        return self._visible(await super()._async_get_elements_by_property_value(*a, **k))

    async def _async_get_elements(self, *a, **k):
        return self._visible(await super()._async_get_elements(*a, **k))

    async def _async_get_placement_reports(self, dashboard_guid, placement_qualified_names, **kwargs):
        saved = self.relationships
        self.relationships = [r for r in saved
                              if not (r["type"] == "DataSetContent" and r["end2"] in self.hidden)]
        try:
            return await super()._async_get_placement_reports(dashboard_guid, placement_qualified_names)
        finally:
            self.relationships = saved


class FakeFormatSet:
    def __init__(self, analytic=None):
        self.action = type("A", (), {"analytic_function": analytic, "required_params": []})()


SPECS = {
    "Spec-Local": (FakeFormatSet(), {"tier": "local", "label": "Spec-Local", "version": None}),
    "Spec-Egeria": (FakeFormatSet(), {"tier": "egeria", "label": "Spec-Egeria", "version": 3}),
}


def spec_lookup(label):
    return SPECS.get(label, (None, None))


def _report(fake, name, spec="Spec-Local", **extra):
    return fake.add_entity("Report", f"DeployedReport::{name}", name, description=f"{name} description",
                           additionalProperties={"reportSpec": spec, "outputFormat": "DICT", **extra})


SHEET = DashboardSheet(name="mixed", heading="Mixed visibility", placements=[
    Placement(ref="Intro", content="**hello**", span="full", emphasis="panel"),
    Placement(ref="Public Count", span="1", emphasis="kpi", perspectives=["Steward"]),
    Placement(ref="Secret Count", span="2", emphasis="kpi"),
    Placement(ref="Panel", span="full", emphasis="panel", perspectives=["Owner"]),
])


async def _mixed():
    fake = ViewerEgeria()
    fake_egeria.seed_perspectives(fake)
    guids = {"Public Count": _report(fake, "Public Count", searchString="Coco", analyticParams='{"top": 5}'),
             "Secret Count": _report(fake, "Secret Count"),
             "Panel": _report(fake, "Panel", spec="Spec-Egeria")}
    await DashboardSheetEgeriaWriter(fake).write_sheet(SHEET)
    return fake, guids


@pytest.mark.asyncio
async def test_visible_text_and_order():
    fake, guids = await _mixed()
    sheet = await dr.async_resolve_dashboard_sheet(fake, "mixed", spec_lookup=spec_lookup,
                                                   check_spec_visibility=False)
    assert [(p.position, p.ref, p.kind) for p in sheet.placements] == [
        (1, "Intro", "text"), (2, "Public Count", "report"), (3, "Secret Count", "report"), (4, "Panel", "report")]
    intro, pub = sheet.placements[0], sheet.placements[1]
    assert (intro.content, intro.span, intro.emphasis) == ("**hello**", "full", "panel")
    assert pub.report_guid == guids["Public Count"] and pub.title == "Public Count"
    assert pub.report.params == {"searchString": "Coco"} and pub.report.analytic_params == {"top": 5}
    assert (pub.spec, pub.spec_source["tier"], pub.restricted, pub.reason) == ("Spec-Local", "local", False, None)
    assert pub.perspectives == ["Steward"] and pub.span == "1" and pub.emphasis == "kpi"
    assert sheet.placements[3].spec_source["tier"] == "egeria"
    assert "format_set" not in pub.model_dump()


@pytest.mark.asyncio
async def test_restricted_report_on_a_public_sheet():
    fake, guids = await _mixed()
    fake.hidden.add(guids["Secret Count"])
    sheet = await dr.async_resolve_dashboard_sheet(fake, "mixed", spec_lookup=spec_lookup)
    secret = sheet.placements[2]
    assert (secret.kind, secret.restricted, secret.restricted_element, secret.reason) == (
        "restricted", True, "Report", "not visible to you")
    assert secret.report is None and secret.position == 3 and secret.span == "2"
    # the sheet's other placements still resolve
    assert [p.kind for p in sheet.placements] == ["text", "report", "restricted", "report"]


@pytest.mark.asyncio
async def test_restricted_report_spec_held_in_egeria():
    fake, guids = await _mixed()
    spec_guid = fake.add_entity("ReportSpec", "ReportSpec::Spec-Egeria", "Spec-Egeria")
    fake.hidden.add(spec_guid)
    lookup = lambda label: (SPECS[label][0], {**SPECS[label][1], "guid": spec_guid}) if label == "Spec-Egeria" \
        else spec_lookup(label)
    sheet = await dr.async_resolve_dashboard_sheet(fake, "mixed", spec_lookup=lookup)
    panel = sheet.placements[3]
    assert (panel.kind, panel.restricted, panel.restricted_element, panel.reason) == (
        "restricted", True, "ReportSpec", "not visible to you")
    assert panel.report.name == "Panel"            # the Report itself is visible: say so
    assert sheet.placements[1].kind == "report"


@pytest.mark.asyncio
async def test_missing_report_is_its_own_kind():
    fake, guids = await _mixed()
    fake._delete(guids["Secret Count"])            # gone, not hidden
    sheet = await dr.async_resolve_dashboard_sheet(fake, "mixed", spec_lookup=spec_lookup)
    secret = sheet.placements[2]
    assert (secret.kind, secret.restricted) == ("missing", False)
    assert secret.reason == REPORT_LINK_MISSING and secret.report_guid == guids["Secret Count"]


@pytest.mark.asyncio
async def test_link_gone_without_recorded_guid_says_missing():
    """A placement written before the writer recorded reportGUID: only "missing" can be said."""
    fake, guids = await _mixed()
    field = next(g for g in fake.of_type("DisplayDataField")
                 if fake.entities[g]["props"]["qualifiedName"].endswith("::Secret Count"))
    fake.entities[field]["props"]["additionalProperties"].pop("reportGUID")
    fake.hidden.add(guids["Secret Count"])
    sheet = await dr.async_resolve_dashboard_sheet(fake, "mixed", spec_lookup=spec_lookup)
    assert (sheet.placements[2].kind, sheet.placements[2].reason) == ("missing", REPORT_LINK_MISSING)


@pytest.mark.asyncio
async def test_spec_not_found_is_an_error_not_a_blank():
    fake, guids = await _mixed()
    fake.entities[guids["Public Count"]]["props"]["additionalProperties"]["reportSpec"] = "No-Such-Spec"
    sheet = await dr.async_resolve_dashboard_sheet(fake, "mixed", spec_lookup=spec_lookup)
    pub = sheet.placements[1]
    assert pub.kind == "report" and pub.spec_source is None
    assert pub.error == "report spec 'No-Such-Spec' was not found in any tier"


@pytest.mark.asyncio
async def test_perspective_keeps_order_and_unscoped_placements():
    fake, _ = await _mixed()
    sheet = await dr.async_resolve_dashboard_sheet(fake, "mixed", perspective="Owner", spec_lookup=spec_lookup)
    assert [(p.position, p.ref) for p in sheet.placements] == [(1, "Intro"), (3, "Secret Count"), (4, "Panel")]
    assert sheet.perspective == "Owner"


@pytest.mark.asyncio
async def test_refused_token_raises_not_restricted():
    fake, _ = await _mixed()
    fake.token_refused = True
    with pytest.raises(PyegeriaUnauthorizedException):
        await dr.async_resolve_dashboard_sheet(fake, "mixed", spec_lookup=spec_lookup)


@pytest.mark.asyncio
async def test_unknown_or_hidden_sheet_is_none_and_listing_is_per_viewer():
    fake, _ = await _mixed()
    assert await dr.async_resolve_dashboard_sheet(fake, "no-such-sheet") is None
    assert [s.name for s in await dr.async_list_dashboard_sheets_for_viewer(fake)] == ["mixed"]
    fake.hidden.add(fake.by_qn("Dashboard::mixed"))
    assert await dr.async_list_dashboard_sheets_for_viewer(fake) == []


@pytest.mark.asyncio
async def test_run_runs_only_resolved_report_placements(monkeypatch):
    fake, guids = await _mixed()
    fake.hidden.add(guids["Secret Count"])
    ran = []

    def fake_run(client, placement):
        ran.append(placement.ref)
        if placement.ref == "Panel":
            raise RuntimeError("boom")
        return {"kind": "json", "data": [1]}
    monkeypatch.setattr(dr, "_run_report", fake_run)
    sheet = await dr.async_resolve_dashboard_sheet(fake, "mixed", spec_lookup=spec_lookup, run=True)
    assert sorted(ran) == ["Panel", "Public Count"]
    assert sheet.placements[1].result == {"kind": "json", "data": [1]}
    assert sheet.placements[3].error == "RuntimeError: boom" and sheet.placements[3].result is None
    assert sheet.placements[2].result is None and sheet.placements[2].kind == "restricted"


def test_not_visible_classifier():
    assert dr.is_not_visible_error(Exception("OPEN-METADATA-SECURITY-403-020 User x is not authorized"))
    assert dr.is_not_visible_error(Exception("Element g is not visible to user x; it has been filtered"))
    assert not dr.is_not_visible_error(Exception("OMAG-REPOSITORY-HANDLER-404-001 not found"))


@pytest.mark.asyncio
@pytest.mark.parametrize("name", sorted(LIVE))
async def test_live_sheets_resolve_to_the_readers_placements(name):
    """The five live sheets: same placements, kinds and order as the reader gives, every report resolved."""
    fake = ViewerEgeria()
    fake_egeria.seed_perspectives(fake)
    for p in LIVE[name]["placements"]:
        if p.get("content") is None and not fake.by_qn(f"DeployedReport::{p['ref']}"):
            _report(fake, p["ref"])
    await DashboardSheetEgeriaWriter(fake).write_sheet(DashboardSheet(**LIVE[name]))
    read = await async_load_dashboard_sheet(fake, name)
    sheet = await dr.async_resolve_dashboard_sheet(fake, name, spec_lookup=spec_lookup)
    assert [(p.ref, p.kind, p.span, p.emphasis, p.perspectives, p.detail_spec) for p in sheet.placements] == \
        [(p.ref, p.kind, p.span, p.emphasis, p.perspectives, p.detail_spec) for p in read.placements]
    assert all(p.kind in ("report", "text") and not p.restricted for p in sheet.placements)
