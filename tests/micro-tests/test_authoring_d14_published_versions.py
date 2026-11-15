# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""D14: published versions are immutable; a change is a new published version under the same element.

The fake Egeria answers in the shapes the real one does:
- element history: OpenMetadataElements (`elementGUID`, `versions`, `elementProperties.propertyValueMap`,
  additionalProperties as a `MapTypePropertyValue`), newest first;
- classification-explorer lookups: view beans (`elementHeader` + flat `properties`).
Provenance: no laz spec with publication stamps exists yet (nothing has published through the authoring API),
so the entries are built, not captured. Their header (headerVersion, status, origin, versions keys) and the
property-value classes are copied from real laz OpenMetadataElements read on 2026-11-13
(tests/micro-tests/data/raw_elements/laz_topic_live_2026_11_13.json; its DataScope classification carries the
`map<string,string>` additionalProperties shape used here).
"""
import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

from pyegeria.authoring import AuthoringRefused, ReportDraft, SheetDraft, SheetPlacement, SpecDraft, validate
from pyegeria.authoring.lifecycle import async_apply, async_publish_plan, publish_plan, report_draft_from_element
from pyegeria.authoring.preview import async_preview
from pyegeria.authoring.publication import (
    AT_PLACEHOLDER, LOOKUP_PAGE, async_resolve_target, digest_text, ordered_entries, publication_entry,
)
from pyegeria.authoring.versions import async_spec_at_version
from pyegeria.core.element_shape import as_view_element
from pyegeria.view._output_format_models import FormatSet

pytestmark = pytest.mark.unit

RAW = Path(__file__).parent / "data" / "raw_elements" / "laz_topic_live_2026_11_13.json"
LAZ_HEADER = {k: v for k, v in json.loads(RAW.read_text()).items() if k in ("headerVersion", "status", "origin")}
ERIN = "erinoverview"
SPEC_QN = "ReportSpec::Team Projects"


def _string(value: str) -> Dict[str, Any]:
    return {"class": "PrimitiveTypePropertyValue", "typeName": "string",
            "primitiveTypeCategory": "OM_PRIMITIVE_TYPE_STRING", "primitiveValue": value}


def ome(guid: str, type_name: str, supers: List[str], version: int, props: Dict[str, str],
        additional: Optional[Dict[str, str]] = None, zones: Optional[List[str]] = None) -> Dict[str, Any]:
    """An OpenMetadataElement as Egeria's history endpoint returns it (laz header shape)."""
    pvm = {k: _string(v) for k, v in props.items()}
    if additional:
        pvm["additionalProperties"] = {"class": "MapTypePropertyValue", "typeName": "map<string,string>",
                                       "mapValues": {"propertyValueMap": {k: _string(v) for k, v in additional.items()}}}
    classifications = []
    if zones:
        classifications.append({"type": {"typeName": "ZoneMembership"}, "classificationName": "ZoneMembership",
                                "classificationProperties": {"propertyValueMap": {"zoneMembership": {
                                    "class": "ArrayTypePropertyValue", "arrayValues": {"propertyValueMap": {
                                        str(i): _string(z) for i, z in enumerate(zones)}}}}}})
    t = f"2026-11-{10 + version:02d}T09:00:00.000+00:00"
    return {**json.loads(json.dumps(LAZ_HEADER)),
            "type": {"typeName": type_name, "superTypeNames": supers, "typeCategory": "ENTITY_DEF"},
            "versions": {"createdBy": ERIN, "updatedBy": ERIN, "createTime": "2026-11-11T09:00:00.000+00:00",
                         "updateTime": t, "version": version},
            "elementGUID": guid, "classifications": classifications,
            "elementProperties": {"propertyValueMap": pvm, "propertyCount": len(pvm), "propertyNames": list(pvm)}}


def _spec_props(description: str) -> Dict[str, str]:
    from pyegeria.view.microflow import format_set_to_microflow
    fs = FormatSet.model_validate({"heading": "Team Projects", "description": description, "target_type": "Project",
                                   "formats": [{"types": ["TABLE"], "attributes": [
                                       {"name": "Name", "key": "display_name"}]}],
                                   "action": {"function": "ProjectManager.find_projects",
                                              "required_params": ["search_string"]}})
    return {"qualifiedName": SPEC_QN, "displayName": "Team Projects", "description": description,
            "targetTypeName": "Project", "microflow": format_set_to_microflow(fs).to_json()}


class _Egeria:
    """Egeria holding elements by qualified name, each with its history (raw, newest first)."""
    def __init__(self, user: str = ERIN):
        self.user_id = user
        self.histories: Dict[str, List[Dict[str, Any]]] = {}   # qn -> raw entries, newest first
        self.lookup_error: Optional[Exception] = None
        self.duplicates: int = 1
        self.full_page = False
        self.history_calls: List[tuple] = []
        self.unique_reads: List[str] = []
        self.not_found_error = False
        outer = self

        def current(qn):
            h = outer.histories.get(qn)
            return as_view_element(h[0]) if h else None

        class CM:
            async def _async_get_elements_by_property_value(self, value, names, metadata_element_type=None,
                                                            page_size=None, **kw):
                assert page_size and page_size >= 25, "B5: never a one-element page"
                if outer.lookup_error:
                    raise outer.lookup_error
                if outer.full_page:
                    return [as_view_element(ome(f"g{i}", metadata_element_type, [], 1, {"qualifiedName": f"x{i}"}))
                            for i in range(LOOKUP_PAGE)]
                out = []
                for qn in outer.histories:
                    el = current(qn)
                    if (el["elementHeader"]["type"]["typeName"] == metadata_element_type
                            and el["properties"].get(names[0]) == value):
                        out += [el] * outer.duplicates
                return out or "No elements found"

            async def _async_get_element_by_unique_name(self, qn):
                outer.unique_reads.append(qn)
                if outer.lookup_error:
                    raise outer.lookup_error
                if outer.not_found_error:
                    from pyegeria.core._exceptions import PyegeriaNotFoundException
                    raise PyegeriaNotFoundException.__new__(PyegeriaNotFoundException)
                return current(qn) or "No elements found"

        class ME:
            async def _async_get_element_history(self, guid, oldest_first=False, start_from=0, page_size=0, **kw):
                """Egeria's paging: a page from start_from; past the end, "No elements found"."""
                outer.history_calls.append((start_from, page_size))
                for h in outer.histories.values():
                    if h[0]["elementGUID"] == guid:
                        page = list(h)[start_from:start_from + page_size] if page_size else list(h)
                        return page or "No elements found"
                return "No elements found"
        self.classification_manager, self.metadata_expert = CM(), ME()

    def hold(self, qn: str, *entries: Dict[str, Any]) -> None:
        self.histories[qn] = sorted(entries, key=lambda e: -e["versions"]["version"])


def _spec_history(eg: _Egeria, *, edited_after: bool = False, unversioned: bool = False) -> None:
    """Team Projects: Egeria versions 1..5. Published 2 at v2, 3 at v4; a hand edit at v3 (keeps stamp 2), and
    with edited_after an edit at v5 (keeps stamp 3)."""
    S = ["Collection", "Referenceable", "OpenMetadataRoot"]
    st = (lambda n: None) if unversioned else (lambda n: {"publishedVersion": str(n), "publishedBy": ERIN,
                                                         "publishedAt": f"2026-11-1{n}T08:00:00Z"})
    entries = [ome("spec-guid", "ReportSpec", S, 1, _spec_props("first, never published")),
               ome("spec-guid", "ReportSpec", S, 2, _spec_props("published two"), st(2)),
               ome("spec-guid", "ReportSpec", S, 3, _spec_props("edited by hand after two"), st(2)),
               ome("spec-guid", "ReportSpec", S, 4, _spec_props("published three"), st(3))]
    if edited_after:
        entries.append(ome("spec-guid", "ReportSpec", S, 5, _spec_props("edited by hand after three"), st(3)))
    eg.hold(SPEC_QN, *entries)


def _spec_draft() -> SpecDraft:
    return SpecDraft(label="Team Projects", format_set=FormatSet.model_validate({
        "heading": "Team Projects", "description": "published four", "target_type": "Project",
        "formats": [{"types": ["TABLE"], "attributes": [{"name": "Name", "key": "display_name"}]}],
        "action": {"function": "ProjectManager.find_projects", "required_params": ["search_string"]}}))


@pytest.fixture(autouse=True)
def _not_builtin(monkeypatch):
    monkeypatch.setattr("pyegeria.authoring.lifecycle._is_builtin", lambda label: False)


def _report(**kw) -> ReportDraft:
    return ReportDraft(**{"display_name": "Team Projects Report", "qualified_name": "Report::Team Projects",
                          "spec": "Team Projects", "output_format": "TABLE",
                          "parameters": {"search_string": "*"}, **kw})


# ── The stamp ─────────────────────────────────────────────────────────────────

def test_a_first_publish_is_version_1_stamped_in_the_elements_own_block():
    plan = asyncio.run(async_publish_plan(_report(), _Egeria()))
    create = plan["markdown"].split("## Create Report", 1)[1].split("___", 1)[0]
    assert ("### Additional Properties\npublishedAt: (set when published)\npublishedBy: erinoverview\n"
            "publishedVersion: 1") in create
    assert plan["steps"][0] == "publish Report 'Team Projects Report' as version 1"
    assert plan["published_version"] == 1 and plan["publication"]["held"] is False


def test_publishing_over_stamped_3_is_version_4_and_says_3_stays_readable():
    eg = _Egeria()
    _spec_history(eg)
    plan = asyncio.run(async_publish_plan(_spec_draft(), eg, folders=["ReportSpecFolder::Consumer::Portal"]))
    assert "## Update Report Spec" in plan["markdown"] and "publishedVersion: 4" in plan["markdown"]
    assert plan["steps"][0] == ("publish version 4 of spec 'Team Projects'; version 3 stays readable for "
                                "Reports pinned to it")
    assert plan["publication"] == {"resolved": True, "held": True, "guid": "spec-guid", "qualified_name": SPEC_QN,
                                   "published_version": 3}


def test_a_held_unversioned_element_is_stamped_1_and_said_so():
    eg = _Egeria()
    _spec_history(eg, unversioned=True)
    plan = asyncio.run(async_publish_plan(_spec_draft(), eg, folders=["ReportSpecFolder::Consumer::Portal"]))
    assert "publishedVersion: 1" in plan["markdown"]
    assert "never published through the authoring API" in plan["steps"][0]


def test_the_digest_leaves_out_the_publish_time_and_apply_sets_it():
    eg = _Egeria()
    a = publish_plan(_report(), held=asyncio.run(async_resolve_target(eg, _report())), published_by=ERIN)
    b = publish_plan(_report(), held=asyncio.run(async_resolve_target(eg, _report())), published_by=ERIN,
                     published_at="2026-11-13T12:00:00Z")
    assert a["digest"] == b["digest"] and digest_text(b["markdown"]) == a["markdown"]
    ran = []
    asyncio.run(async_apply(a, step="process", run=lambda md, d: ran.append(md) or {"success": True}, client=eg,
                            confirmed=True, digest=a["digest"]))
    assert AT_PLACEHOLDER not in ran[0] and "publishedAt: 20" in ran[0]


# ── Pins name publications ───────────────────────────────────────────────────

def test_a_pin_resolves_the_publication_itself_not_a_later_edit():
    eg = _Egeria()
    _spec_history(eg, edited_after=True)
    assert asyncio.run(async_spec_at_version(eg, "Team Projects", 2)).description == "published two"
    assert asyncio.run(async_spec_at_version(eg, "Team Projects", 3)).description == "published three"
    entries = ordered_entries(None, [as_view_element(e) for e in eg.histories[SPEC_QN]])
    assert publication_entry(entries, 2)["elementHeader"]["versions"]["version"] == 2


def test_a_pin_to_a_missing_version_names_the_published_ones():
    eg = _Egeria()
    _spec_history(eg)
    with pytest.raises(AuthoringRefused, match="has no published version 7; its published versions are 2, 3"):
        asyncio.run(async_spec_at_version(eg, "Team Projects", 7))


def test_a_pin_to_an_unversioned_spec_is_refused():
    eg = _Egeria()
    _spec_history(eg, unversioned=True)
    with pytest.raises(AuthoringRefused, match="has no published versions yet"):
        asyncio.run(async_spec_at_version(eg, "Team Projects", 1))


# ── Exact target or refuse ───────────────────────────────────────────────────

# The exists-lookups ruling (2026-11-14): publishing reads its target by Egeria's unique-name read, never by
# paging a property search (a NULL_NOT_END path, where a filtered page reads as "none").

def test_the_target_is_found_by_the_unique_name_read():
    eg = _Egeria()
    _spec_history(eg)
    plan = asyncio.run(async_publish_plan(_spec_draft(), eg, folders=["ReportSpecFolder::Consumer::Portal"]))
    assert plan["publication"]["held"] is True and eg.unique_reads   # found -> update


@pytest.mark.parametrize("not_found", ["string", "exception"])
def test_egerias_not_found_is_absent_and_plans_a_create(not_found):
    eg = _Egeria()   # holds nothing
    eg.not_found_error = not_found == "exception"
    plan = asyncio.run(async_publish_plan(_spec_draft(), eg, folders=["ReportSpecFolder::Consumer::Portal"]))
    assert plan["publication"]["held"] is False and plan["publication"]["guid"] is None   # absent -> create


def test_any_other_error_is_unknown_refuses_and_plans_nothing():
    eg = _Egeria()
    _spec_history(eg)
    eg.lookup_error = TimeoutError("slow")
    with pytest.raises(AuthoringRefused, match="Couldn't find out whether Egeria already holds .*unique-name "
                                               "read of qualifiedName failed: TimeoutError"):
        asyncio.run(async_publish_plan(_spec_draft(), eg, folders=["ReportSpecFolder::Consumer::Portal"]))


def test_unknown_creates_nothing(monkeypatch):
    from pyegeria.authoring import publication
    eg = _Egeria()
    eg.lookup_error = ConnectionError("down")
    with pytest.raises(AuthoringRefused):
        asyncio.run(publication.async_resolve_target(eg, _spec_draft()))
    assert eg.history_calls == []   # nothing planned, nothing read past the refusal


def test_a_target_of_another_type_under_that_qualified_name_is_refused():
    eg = _Egeria()
    _spec_history(eg)
    qn = next(iter(eg.histories))
    eg.histories[qn][0]["type"]["typeName"] = "Glossary"
    eg.histories[qn][0]["type"]["superTypeNames"] = ["Referenceable"]
    with pytest.raises(AuthoringRefused, match="not a ReportSpec"):
        asyncio.run(async_publish_plan(_spec_draft(), eg, folders=["ReportSpecFolder::Consumer::Portal"]))


def test_publish_plan_without_a_resolved_target_is_refused():
    with pytest.raises(AuthoringRefused, match="finds the exact element it will write first"):
        publish_plan(_report(), published_by=ERIN)


def test_a_report_named_only_by_display_name_is_refused_for_its_qualified_name():
    # The exists-lookups ruling: one displayName match can't be proven the only one on a NULL_NOT_END path.
    eg = _Egeria()
    eg.hold("Coco::DeployedReport::Team-Projects::1.0",
            ome("r-guid", "Report", ["DataSet"], 1, {"qualifiedName": "Coco::DeployedReport::Team-Projects::1.0",
                                                    "displayName": "Team Projects Report"}))
    with pytest.raises(AuthoringRefused, match="Give the qualified name: Egeria can't confirm there's only one "
                                               "Report with displayName 'Team Projects Report'"):
        asyncio.run(async_publish_plan(_report(qualified_name=None), eg))
    assert eg.unique_reads == []   # nothing was looked up by a property search either


# ── No silent overwrite ──────────────────────────────────────────────────────

def test_apply_refuses_when_the_target_was_published_since_the_plan():
    eg = _Egeria()
    _spec_history(eg)
    plan = asyncio.run(async_publish_plan(_spec_draft(), eg, folders=["ReportSpecFolder::Consumer::Portal"]))
    S = ["Collection", "Referenceable", "OpenMetadataRoot"]
    eg.histories[SPEC_QN].insert(0, ome("spec-guid", "ReportSpec", S, 6, _spec_props("someone else's four"),
                                        {"publishedVersion": "4", "publishedBy": "garygeeke"}))
    ran = []
    with pytest.raises(AuthoringRefused, match="was published as version 4 since this plan was made"):
        asyncio.run(async_apply(plan, step="process", run=lambda md, d: ran.append(d) or {"success": True},
                                client=eg, confirmed=True, digest=plan["digest"]))
    assert ran == []


def test_apply_refuses_when_a_new_element_appeared_since_the_plan():
    eg = _Egeria()
    plan = asyncio.run(async_publish_plan(_spec_draft(), eg, folders=["ReportSpecFolder::Consumer::Portal"]))
    _spec_history(eg)
    with pytest.raises(AuthoringRefused, match="no longer the element this plan was made for"):
        asyncio.run(async_apply(plan, step="process", run=lambda md, d: {"success": True}, client=eg,
                                confirmed=True, digest=plan["digest"]))


def test_apply_of_a_publish_plan_needs_the_users_client():
    plan = asyncio.run(async_publish_plan(_report(), _Egeria()))
    with pytest.raises(AuthoringRefused, match="re-checks the element it writes as you"):
        asyncio.run(async_apply(plan, step="process", run=lambda md, d: {"success": True}, confirmed=True,
                                digest=plan["digest"]))


# ── Edited since publication: said, not refused ──────────────────────────────

def test_an_edit_since_publication_is_a_note_not_an_error(monkeypatch):
    eg = _Egeria()
    _spec_history(eg, edited_after=True)
    plan = asyncio.run(async_publish_plan(_spec_draft(), eg, folders=["ReportSpecFolder::Consumer::Portal"]))
    assert any("changed since published version 3 (outside publishing)" in s for s in plan["steps"])
    result = validate(_spec_draft(), eg)
    assert any("changed since published version 3" in n for n in result.not_applied)
    assert not any("changed since" in e for e in result.errors)
    monkeypatch.setattr("pyegeria.view.format_set_executor.exec_report_spec", lambda spec, **kw: {"kind": "empty"})
    eg.token, eg.user_pwd = "t", None
    out = asyncio.run(async_preview(_spec_draft(), client=eg))
    assert any("changed since published version 3" in n for n in out["notes"])


def test_no_edit_since_publication_says_nothing():
    eg = _Egeria()
    _spec_history(eg)
    plan = asyncio.run(async_publish_plan(_spec_draft(), eg, folders=["ReportSpecFolder::Consumer::Portal"]))
    assert not any("changed since" in s for s in plan["steps"])


def test_a_zone_only_change_is_not_an_edit():
    eg = _Egeria()
    S = ["DataSet"]
    props = {"qualifiedName": "Report::Team Projects", "displayName": "Team Projects Report"}
    stamp = {"publishedVersion": "1", "publishedBy": ERIN, "publishedAt": "2026-11-12T08:00:00Z"}
    eg.hold("Report::Team Projects", ome("r", "Report", S, 1, props, stamp, zones=[ERIN]),
            ome("r", "Report", S, 2, props, stamp))   # declassified: same properties, new instance version
    held = asyncio.run(async_resolve_target(eg, _report()))
    assert held["published_version"] == 1 and held["edited_since"] is False


# ── Promotion: the stamp lands before the Declassify ─────────────────────────

def test_promotion_stamps_the_element_before_it_declassifies():
    eg = _Egeria()
    eg.hold("Dashboard::team", ome("d", "Dashboard", ["Asset"], 1, {"qualifiedName": "Dashboard::team",
                                                                   "displayName": "Team"}, zones=[ERIN]))
    sheet = SheetDraft(name="team", heading="Team", placements=[SheetPlacement(report="Team Projects Report")])
    md = asyncio.run(async_publish_plan(sheet, eg, folders=["DashboardFolder::Consumer::Portal"]))["markdown"]
    assert md.index("publishedVersion: 1") < md.index("## Declassify Zone Membership")
    report_md = asyncio.run(async_publish_plan(_report(), _Egeria()))["markdown"]
    eg.hold("Report::Team Projects", ome("r", "Report", ["DataSet"], 1, {
        "qualifiedName": "Report::Team Projects", "displayName": "Team Projects Report"}, zones=[ERIN]))
    report_md = asyncio.run(async_publish_plan(_report(), eg))["markdown"]
    assert report_md.index("publishedVersion: 1") < report_md.index("## Declassify Zone Membership")


# ── The stamp is bookkeeping, never a parameter; a published element is never deleted ──

def test_stamp_keys_are_not_report_parameters():
    from pyegeria.view.dashboard_resolver import report_from_element
    el = {"elementHeader": {"guid": "r"}, "properties": {"displayName": "R", "additionalProperties": {
        "reportSpec": "Team Projects", "outputFormat": "TABLE", "searchString": "*", "publishedVersion": "2",
        "publishedAt": "2026-11-13T08:00:00Z", "publishedBy": ERIN, "authoringState": "published"}}}
    assert report_from_element(el).params == {"searchString": "*"}
    assert report_draft_from_element(el).parameters == {"search_string": "*"}


def test_draft_prune_and_delete_never_take_a_published_element():
    from pyegeria.authoring.drafts import EgeriaDraftStore
    eg = _Egeria()
    stamp = {"publishedVersion": "1", "publishedBy": ERIN, "publishedAt": "2026-09-01T08:00:00Z"}
    eg.hold("Report::Old", ome("r-old", "Report", ["DataSet"], 1, {"qualifiedName": "Report::Old",
                                                                   "displayName": "Old", }, {**stamp, "authoringState": "draft"},
                               zones=[ERIN]))

    class AM:
        async def _async_delete_asset(self, guid):
            raise AssertionError("a published element was deleted")
    eg.asset_maker = AM()

    async def by_type(metadata_element_type=None, **kw):
        return [as_view_element(h[0]) for h in eg.histories.values()
                if h[0]["type"]["typeName"] == metadata_element_type] if not kw.get("start_from") else []
    eg.classification_manager._async_get_elements = by_type
    store = EgeriaDraftStore(eg)
    out = store.prune_drafts(ERIN, older_than_days=1)
    assert out["removed"] == [] and "published (version 1)" in out["kept_reasons"]["report:Old"]
    with pytest.raises(AuthoringRefused, match="a published element is never deleted"):
        store.delete(ERIN, "report", "Report::Old")


# ── The sheet's Dashboard carries the stamp ──────────────────────────────────

def test_create_dashboard_sheet_writes_the_documents_additional_properties(monkeypatch):
    from md_processing.v2 import dashboard_sheet as ds
    sent: Dict[str, Any] = {}

    async def fake_upsert(client, qn, props, existing, **kw):
        sent.update(props)
        return "d-guid", "Created", {}
    monkeypatch.setattr(ds, "upsert_dashboard_asset", fake_upsert)

    async def chain(self, name):
        return ds.SheetChain(sheet_name=name, schema_type_guid="st", container_guid="c")
    monkeypatch.setattr(ds.DashboardSheetEgeriaWriter, "find_chain", chain)
    writer = ds.DashboardSheetEgeriaWriter(object())
    asyncio.run(writer.ensure_sheet("team", "Team", family="Overview",
                                    additional={"publishedVersion": "2", "publishedBy": ERIN}))
    assert sent["additionalProperties"] == {"publishedVersion": "2", "publishedBy": ERIN, "family": "Overview"}


# ── A history too long to read whole: never resolve a pin on part of it ──────

def test_history_is_read_in_pages_until_an_empty_one(monkeypatch):
    monkeypatch.setattr("pyegeria.authoring.publication.HISTORY_PAGE", 2)
    eg = _Egeria()
    _spec_history(eg, edited_after=True)   # 5 entries
    assert asyncio.run(async_spec_at_version(eg, "Team Projects", 2)).description == "published two"
    # a short page (1) isn't the last page; the read advances by the page size (pager step 4), and on this
    # suspect path the null at 6 is probed 3 pages ahead before it's acted on as the end
    assert eg.history_calls == [(0, 2), (2, 2), (4, 2), (6, 2), (8, 2), (10, 2), (12, 2)]


def test_a_capped_history_refuses_the_pin_and_skips_the_edit_check(monkeypatch):
    """The publication of 2 (Egeria v2) lies past the pages read; v3, an edit still stamped 2, would be the
    oldest stamped-2 entry returned. Refused, not resolved to the edit (read-back follow-up 1)."""
    monkeypatch.setattr("pyegeria.authoring.publication.HISTORY_PAGE", 1)
    monkeypatch.setattr("pyegeria.authoring.publication.HISTORY_MAX_PAGES", 3)
    eg = _Egeria()
    _spec_history(eg, edited_after=True)
    with pytest.raises(AuthoringRefused, match="history is too long to read whole"):
        asyncio.run(async_spec_at_version(eg, "Team Projects", 2))
    held = asyncio.run(async_resolve_target(eg, _spec_draft()))
    assert held["published_version"] == 3 and held["edited_since"] is None
    assert any("history is too long to read whole" in n for n in held["notes"])


def test_authoring_keys_have_a_stable_public_path():
    from pyegeria.authoring import AUTHORING_KEYS
    assert AUTHORING_KEYS == {"authoringState", "reportSpecVersion", "publishedVersion", "publishedAt",
                              "publishedBy"}


@pytest.mark.parametrize("answer", [[], ["x"], "Something else", {"neither": "elementHeader nor element"}, None])
def test_an_unexpected_unique_name_answer_is_refused_and_plans_nothing(monkeypatch, answer):
    # step 5 read-back R1: only Egeria's "not found" (the string, or PyegeriaNotFoundException) is absent
    eg = _Egeria()

    async def odd(qn):
        return answer
    monkeypatch.setattr(eg.classification_manager, "_async_get_element_by_unique_name", odd)
    with pytest.raises(AuthoringRefused, match="wasn't an element or 'not found'"):
        asyncio.run(async_publish_plan(_spec_draft(), eg, folders=["ReportSpecFolder::Consumer::Portal"]))
    assert eg.history_calls == []
