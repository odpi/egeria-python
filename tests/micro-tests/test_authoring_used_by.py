"""P3 used_by (DESIGN-P3-AUTHORING-USED-BY-2026-11-14, APPROVED by the Architect's ruling (c)): live reads as the
user, never the shared consumer index; complete only when every read is confirmed; never "used by none" on an
unconfirmed read; a failed read is in the notes; nothing cached across users."""
import asyncio
import json

import pytest

from pyegeria.authoring import VIA_KEYS, AuthoringRefused, async_used_by, spec_label_of, used_by
from pyegeria.authoring.models import ANSWER_ABSENT, ANSWER_UNKNOWN
from pyegeria.core import paging

pytestmark = pytest.mark.unit

NULL = "No elements found"
GATED = json.dumps({"version": "6.3-SNAPSHOT", "time": "2026-11-14T19:55:39.317Z"})
OLD = json.dumps({"version": "6.3-SNAPSHOT", "time": "2026-11-10T08:00:00Z"})
WITH_9454 = json.dumps({"version": "6.3-SNAPSHOT", "time": "2026-11-15T08:29:25.754Z"})   # laz a5c3a195


@pytest.fixture(autouse=True)
def _fresh_gate(monkeypatch):
    """Hermetic (P3-4): no EGERIA_* identity from the developer's shell; a fresh #9453 gate cache."""
    for var in ("EGERIA_USER", "EGERIA_USER_PASSWORD", "EGERIA_PASSWORD"):
        monkeypatch.delenv(var, raising=False)
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
                outer.reads.append(("unique", qn))
                if "unique" in outer.fail:
                    raise TimeoutError("slow")
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


def test_complete_only_when_every_read_is_confirmed():
    # G2 (#9454): get_related_elements is trusted on a platform carrying #9454, with no change to used_by (P3-3)
    eg = _Egeria(about=WITH_9454, elements=[SPEC], reports=[_report("Weekly", "Stale Assets")],
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


# ── P3-1..P3-4 (the Architect's approval, 2026-11-15) ──

def test_p3_1_a_spec_egeria_doesnt_hold_and_isnt_built_in_raises_absent_and_scans_nothing():
    eg = _Egeria(reports=[_report("Weekly", "Nowhere Spec")])
    with pytest.raises(AuthoringRefused) as ei:
        _ask("spec", "Nowhere Spec", eg)
    assert ei.value.answer == ANSWER_ABSENT and "holds no report spec named 'Nowhere Spec'" in str(ei.value)
    assert not any(r[0] == "elements" for r in eg.reads)   # resolved first: no Report scan


@pytest.mark.parametrize("kind, label", [("spec", "Stale Assets"), ("report", "Report::Weekly"), ("sheet", "ops")])
def test_p3_1_a_unique_name_read_that_fails_raises_unknown_never_absent(kind, label):
    eg = _Egeria(elements=[SPEC], fail={"unique"})
    with pytest.raises(AuthoringRefused) as ei:
        _ask(kind, label, eg)
    assert ei.value.answer == ANSWER_UNKNOWN and "Couldn't confirm" in str(ei.value)


def test_p3_1_a_report_lookup_that_errors_is_unknown(monkeypatch):
    import pyegeria.authoring.lifecycle as lc

    async def _boom(client, label):
        raise ConnectionError("down")

    monkeypatch.setattr(lc, "_report_element", _boom)
    with pytest.raises(AuthoringRefused) as ei:
        _ask("report", "Weekly", _Egeria())
    assert ei.value.answer == ANSWER_UNKNOWN


def test_p3_2_exact_case_sensitive_match_after_one_prefix():
    assert spec_label_of("ReportSpec::X") == "X" and spec_label_of("ReportType::X") == "X"
    assert spec_label_of("ReportSpec::ReportSpec::X") == "ReportSpec::X" and spec_label_of(None) == ""
    eg = _Egeria(elements=[SPEC], reports=[
        _report("Plain", "Stale Assets"), _report("Spec", "ReportSpec::Stale Assets"),
        _report("Legacy", "ReportType::Stale Assets"),
        _report("Case", "stale assets"), _report("CasePrefix", "reportspec::Stale Assets"),
        _report("Twice", "ReportSpec::ReportSpec::Stale Assets"), _report("Space", "Stale Assets ")])
    out = _ask("spec", "ReportSpec::Stale Assets", eg)
    assert {i["name"] for i in out["items"] if i["kind"] == "report"} == {"Plain", "Spec", "Legacy"}


def test_p3_3_a_forbidden_read_is_a_failed_read_never_not_used():
    from pyegeria.core._exceptions import PyegeriaUnauthorizedException
    eg = _Egeria(elements=[SPEC])

    async def _forbidden(*a, **kw):
        raise PyegeriaUnauthorizedException.__new__(PyegeriaUnauthorizedException)

    eg.classification_manager._async_get_related_elements = _forbidden
    out = _ask("spec", "Stale Assets", eg)
    assert out["complete"] is False and any("couldn't be read" in n for n in out["notes"])
    assert any("isn't \"used by none\"" in n for n in out["notes"])


def test_via_is_a_closed_set_of_machine_keys():
    assert VIA_KEYS == ("reportSpec", "CollectionMembership", "DataSetContent")
    eg = _Egeria(elements=[SPEC], reports=[_report("Weekly", "Stale Assets")],
                 related={("spec1", "CollectionMembership", 2): [FOLDER]})
    assert {i["via"] for i in _ask("spec", "Stale Assets", eg)["items"]} <= set(VIA_KEYS)


@pytest.mark.parametrize("shell_user", [None, "peterprofile", "someoneelse"])
def test_p3_4_the_shells_user_changes_nothing(monkeypatch, shell_user):
    if shell_user:
        monkeypatch.setenv("EGERIA_USER", shell_user)
    eg = _Egeria(user="erinoverview", elements=[SPEC], reports=[_report("Weekly", "Stale Assets")])
    assert [i["name"] for i in _ask("spec", "Stale Assets", eg)["items"]] == ["Weekly"]
