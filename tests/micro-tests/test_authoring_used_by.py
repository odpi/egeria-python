"""P3 used_by (DESIGN-P3-AUTHORING-USED-BY-2026-11-14, APPROVED by the Architect's ruling (c)): live reads as the
user, never the shared consumer index; complete only when every read is confirmed; never "used by none" on an
unconfirmed read; a failed read is in the notes; nothing cached across users."""
import asyncio
import json

import pytest

from pyegeria.authoring import AuthoringRefused, async_used_by, used_by
from pyegeria.authoring.models import ANSWER_ABSENT, ANSWER_UNKNOWN
from pyegeria.core import paging

pytestmark = pytest.mark.unit

NULL = "No elements found"
GATED = json.dumps({"version": "6.3-SNAPSHOT", "time": "2026-11-14T19:55:39.317Z"})
OLD = json.dumps({"version": "6.3-SNAPSHOT", "time": "2026-11-10T08:00:00Z"})


@pytest.fixture(autouse=True)
def _fresh_gate():
    paging._GATE_CACHE.clear()
    yield
    paging._GATE_CACHE.clear()


def _el(qn, type_name, guid=None, **extra):
    props = {"qualifiedName": qn, "displayName": qn.split("::")[-1], **extra}
    return {"elementHeader": {"guid": guid or f"g-{qn}", "type": {"typeName": type_name}}, "properties": props}


def _report(name, spec):
    return _el(f"Report::{name}", "Report", additionalProperties={"reportSpec": spec})


def _rel(el):
    return {"relationshipHeader": {"type": {"typeName": "x"}}, "relatedElement": el}


class _Egeria:
    """Pages like Egeria: a short page then null. related[(guid, rel, end)] -> elements at the other end."""

    def __init__(self, user="peterprofile", about=GATED, elements=(), reports=(), related=None, fail=()):
        self.user_id, self.about, self.platform_url = user, about, f"https://{user}:9443"
        self.elements = {e["properties"]["qualifiedName"]: e for e in elements}
        self.reports, self.related, self.fail = list(reports), related or {}, set(fail)
        self.reads = []
        outer = self

        class CM:
            async def _async_get_element_by_unique_name(self, qn):
                return outer.elements.get(qn) or NULL

            async def _async_get_elements_by_property_value(self, value, names, **kw):
                hits = [r for r in outer.reports if r["properties"]["displayName"] == value]
                return hits[kw.get("start_from", 0):kw.get("start_from", 0) + kw.get("page_size", 25)] or NULL

            async def _async_get_elements(self, type_name, start_from=0, page_size=0, **kw):
                outer.reads.append(("elements", type_name, start_from))
                if "reports" in outer.fail:
                    raise TimeoutError("slow")
                return outer.reports[start_from:start_from + page_size] or NULL

            async def _async_get_related_elements(self, guid, rel, start_at_end=1, start_from=0, page_size=0, **kw):
                outer.reads.append(("related", guid, rel, start_at_end, start_from))
                if rel in outer.fail:
                    raise TimeoutError("slow")
                items = [_rel(e) for e in outer.related.get((guid, rel, start_at_end), [])]
                return items[start_from:start_from + page_size] or NULL

        self.classification_manager = CM()

    def get_platform_origin(self):
        return self.about

    async def async_get_platform_origin(self):
        return self.about


def _ask(kind, label, eg):
    return asyncio.run(async_used_by(kind, label, eg))


SPEC = _el("ReportSpec::Stale Assets", "ReportSpec", guid="spec1")
FOLDER = _el("ReportSpecFolder::Consumer::Portal", "Collection")
OTHER_COLLECTION = _el("SomeCollection::x", "Collection")


def test_a_spec_is_used_by_its_reports_and_consumer_folders_complete_on_a_gated_platform():
    eg = _Egeria(elements=[SPEC],
                 reports=[_report("Weekly", "Stale Assets"), _report("Pinned", "ReportSpec::Stale Assets"),
                          _report("Other", "Something Else")],
                 related={("spec1", "CollectionMembership", 2): [FOLDER, OTHER_COLLECTION]})
    out = _ask("spec", "Stale Assets", eg)
    assert {(i["kind"], i["name"], i["via"]) for i in out["items"]} == {
        ("report", "Weekly", "reportSpec"), ("report", "Pinned", "reportSpec"),
        ("folder", "Portal", "CollectionMembership")}
    # the Report scan is confirmed (gated), but get_related_elements isn't trusted yet: "at least" for folders
    assert out["complete"] is False
    assert any("consumer folders" in n and "at least" in n for n in out["notes"])
    assert not any("Reports that run this spec" in n for n in out["notes"])


def test_the_report_scan_on_an_older_platform_is_never_complete():
    eg = _Egeria(about=OLD, elements=[SPEC], reports=[_report("Weekly", "Stale Assets")])
    out = _ask("spec", "Stale Assets", eg)
    assert out["complete"] is False and any("Reports that run this spec" in n for n in out["notes"])


def test_complete_only_when_every_read_is_confirmed(monkeypatch):
    monkeypatch.setattr(paging, "GATED_TRUSTED_METHODS", paging.GATED_TRUSTED_METHODS | {"get_related_elements"})
    eg = _Egeria(elements=[SPEC], reports=[_report("Weekly", "Stale Assets")],
                 related={("spec1", "CollectionMembership", 2): [FOLDER]})
    out = _ask("spec", "Stale Assets", eg)
    assert out["complete"] is True and len(out["items"]) == 2


def test_nothing_found_unconfirmed_is_never_used_by_none():
    eg = _Egeria(about=OLD, elements=[SPEC])
    out = _ask("spec", "Stale Assets", eg)
    assert out["items"] == [] and out["complete"] is False
    assert any("isn't \"used by none\"" in n for n in out["notes"])


def test_a_failed_read_is_in_the_notes_and_never_none():
    eg = _Egeria(elements=[SPEC], reports=[_report("Weekly", "Stale Assets")], fail={"CollectionMembership"})
    out = _ask("spec", "Stale Assets", eg)
    assert [i["name"] for i in out["items"]] == ["Weekly"] and out["complete"] is False
    assert any("couldn't be read (TimeoutError)" in n for n in out["notes"])
    eg = _Egeria(elements=[SPEC], fail={"reports"})
    out = _ask("spec", "Stale Assets", eg)
    assert out["complete"] is False and any("The Reports couldn't be read" in n for n in out["notes"])


def test_a_report_is_used_by_the_sheets_placing_it():
    rep = _report("Weekly", "Stale Assets")
    dash = _el("Dashboard::ops", "Dashboard")
    eg = _Egeria(elements=[rep], related={(rep["elementHeader"]["guid"], "DataSetContent", 2): [dash, dash]})
    out = _ask("report", "Report::Weekly", eg)
    assert out["items"] == [{"kind": "sheet", "name": "ops", "qualified_name": "Dashboard::ops",
                             "via": "DataSetContent"}]   # two placements on one sheet: one item


def test_a_sheet_is_used_by_its_consumer_folders():
    dash = _el("Dashboard::ops", "Dashboard", guid="d1")
    eg = _Egeria(elements=[dash], related={("d1", "CollectionMembership", 2): [
        _el("DashboardFolder::Consumer::MyEgeria", "Collection"), FOLDER]})
    out = _ask("sheet", "ops", eg)
    assert [(i["kind"], i["name"]) for i in out["items"]] == [("folder", "MyEgeria")]


def test_an_unresolvable_report_or_sheet_refuses_with_the_answer():
    with pytest.raises(AuthoringRefused) as ei:
        _ask("sheet", "nowhere", _Egeria())
    assert ei.value.answer == ANSWER_ABSENT
    with pytest.raises(AuthoringRefused) as ei:
        _ask("report", "Nope", _Egeria(about=OLD))
    assert ei.value.answer == ANSWER_UNKNOWN


def test_a_spec_not_held_still_lists_reports_and_says_why_no_folders():
    eg = _Egeria(reports=[_report("Weekly", "Referenceable")])
    out = _ask("spec", "Referenceable", eg)
    assert [i["name"] for i in out["items"]] == ["Weekly"]
    assert any("holds no report spec 'Referenceable'" in n for n in out["notes"])


def test_two_users_get_their_own_answers_nothing_cached():
    a = _Egeria(user="peterprofile", elements=[SPEC], reports=[_report("Mine", "Stale Assets")])
    b = _Egeria(user="erinoverview", elements=[SPEC], reports=[])
    assert [i["name"] for i in _ask("spec", "Stale Assets", a)["items"]] == ["Mine"]
    assert _ask("spec", "Stale Assets", b)["items"] == []
    assert a.reads and b.reads   # each answer came from its own reads


def test_bad_arguments_refuse_and_the_sync_form_works():
    with pytest.raises(AuthoringRefused):
        _ask("table", "x", _Egeria())
    with pytest.raises(AuthoringRefused):
        _ask("spec", "x", None)
    assert used_by("spec", "Stale Assets", _Egeria(elements=[SPEC]))["items"] == []
