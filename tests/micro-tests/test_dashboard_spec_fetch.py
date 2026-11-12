# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Consumer folders govern what a tool LISTS, not whether a spec a sheet already references can RUN
(Architect, B7a read-back). "Analytic - Generic Metric Trend" sits only in
ReportSpecFolder::Consumer::Portal; EA syncs only Consumer::EgeriaAdvisor, so a sheet both apps show
failed in EA. When no tier holds a placement's spec, the resolver fetches it as the viewer, and the
placement says so; a spec the viewer cannot read stays absent, with the reason.
"""
import pytest

# micro-tests is on sys.path under pytest.
from test_dashboard_resolver import NotVisible, ViewerEgeria, _report
from test_rs_egeria_tier import spec_element, tier  # noqa: F401 -- `tier` is a fixture

from md_processing.v2.dashboard_sheet import DashboardSheetEgeriaWriter
from pyegeria.view import dashboard_resolver as dr
from pyegeria.view._output_dashboard_sheet_models import DashboardSheet, Placement

pytestmark = pytest.mark.unit

LABEL = "Generic-Metric-Trend"
SPEC_GUID = "5bec0000-0000-0000-0000-000000000001"


class SpecEgeria(ViewerEgeria):
    """The viewer's Egeria also holds ReportSpec elements, read the way fetch-on-call reads them. A hidden
    spec is filtered out of a search (as Egeria does) and refused on a read by GUID."""

    def __init__(self):
        super().__init__()
        self.specs = {}

    async def _async_get_collections_by_name(self, name, metadata_element_type=None, output_format="JSON", **_):
        hits = [e for g, e in self.specs.items() if g not in self.hidden
                and e["properties"]["qualifiedName"] in (name, f"ReportSpec::{name}")]
        return hits or "No elements found"

    async def _async_get_collection_by_guid(self, guid, output_format="JSON", **_):
        if guid in self.hidden:
            raise NotVisible(f"OPEN-METADATA-SECURITY-403-020 User viewer is not authorized to issue an operation "
                             f"read on ReportSpec element {guid}")
        return self.specs.get(guid) or "No elements found"


def _no_tier_holds_it(label):
    return None, None


async def _sheet_naming_the_spec():
    fake = SpecEgeria()
    fake.specs[SPEC_GUID] = spec_element(label=LABEL, guid=SPEC_GUID, aliases=[])
    _report(fake, "Trend", spec=LABEL)
    await DashboardSheetEgeriaWriter(fake).write_sheet(
        DashboardSheet(name="shared", heading="Shown by the Portal and EA",
                       placements=[Placement(ref="Trend", span="full", emphasis="panel")]))
    return fake


async def test_a_spec_not_in_this_tools_folder_but_readable_runs_with_the_note(tier):
    fake = await _sheet_naming_the_spec()
    sheet = await dr.async_resolve_dashboard_sheet(fake, "shared", spec_lookup=_no_tier_holds_it)
    trend = sheet.placements[0]
    assert trend.kind == "report" and trend.error is None
    assert trend.note == dr.SPEC_NOT_IN_FOLDER
    assert trend.fetched_as == f"egeria:{LABEL}@v1"
    assert trend.format_set is not None
    assert (trend.spec, trend.spec_source["tier"], trend.spec_source["guid"]) == (LABEL, "egeria", SPEC_GUID)


async def test_a_fetched_spec_runs_under_its_fetched_name(tier, monkeypatch):
    fake = await _sheet_naming_the_spec()
    ran = []
    import pyegeria.view.format_set_executor as fse
    monkeypatch.setattr(fse, "exec_report_spec", lambda name, **kw: ran.append(name) or {"kind": "empty"})
    sheet = await dr.async_resolve_dashboard_sheet(fake, "shared", spec_lookup=_no_tier_holds_it, run=True)
    assert ran == [f"egeria:{LABEL}@v1"]
    assert sheet.placements[0].result == {"kind": "empty"}


async def test_a_spec_the_viewer_cannot_see_stays_absent_with_its_reason(tier):
    fake = await _sheet_naming_the_spec()
    fake.hidden.add(SPEC_GUID)
    sheet = await dr.async_resolve_dashboard_sheet(fake, "shared", spec_lookup=_no_tier_holds_it)
    trend = sheet.placements[0]
    assert trend.format_set is None and trend.fetched_as is None and trend.note is None
    assert trend.error.startswith(f"report spec '{LABEL}' was not found in any tier, and fetching it from Egeria "
                                  f"as viewer failed: ")
    assert "was not found in Egeria" in trend.error


async def test_a_spec_refused_by_guid_says_not_visible(tier):
    fake = await _sheet_naming_the_spec()
    # The viewer's cache already knows the GUID (an earlier fetch), and the spec has since been zoned away.
    assert (await dr.async_resolve_dashboard_sheet(fake, "shared", spec_lookup=_no_tier_holds_it)
            ).placements[0].fetched_as
    fake.hidden.add(SPEC_GUID)
    trend = (await dr.async_resolve_dashboard_sheet(fake, "shared", spec_lookup=_no_tier_holds_it)).placements[0]
    assert trend.format_set is None
    assert trend.error.endswith(f"as viewer failed: {dr.NOT_VISIBLE}")


async def test_fetching_can_be_turned_off(tier):
    fake = await _sheet_naming_the_spec()
    sheet = await dr.async_resolve_dashboard_sheet(fake, "shared", spec_lookup=_no_tier_holds_it,
                                                   fetch_missing=False)
    assert sheet.placements[0].error == f"report spec '{LABEL}' was not found in any tier"


async def test_the_note_stays_once_the_fetched_spec_is_in_the_viewers_cache(tier):
    """A per-user cache keeps the fetched copy, so the next view finds it in the EGERIA tier; it is still in
    none of this tool's folders, so the note stays (the Architect's LD-1 read-back)."""
    from pyegeria.view.dashboard_resolver import _default_spec_lookup

    fake = await _sheet_naming_the_spec()
    first = (await dr.async_resolve_dashboard_sheet(fake, "shared")).placements[0]
    assert first.fetched_as and first.note == dr.SPEC_NOT_IN_FOLDER
    second = (await dr.async_resolve_dashboard_sheet(fake, "shared")).placements[0]
    assert second.fetched_as is None and second.spec_source["tier"] == "egeria"   # from the cache this time
    assert second.note == dr.SPEC_NOT_IN_FOLDER
    assert _default_spec_lookup(LABEL)[0] is not None
