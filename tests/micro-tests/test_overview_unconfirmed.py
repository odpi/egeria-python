"""Pager step 4, the Architect's overview_metrics ruling (ii), 2026-11-14: a scan-based figure, by kind
(count, percentage, distinct count) x how its scan ended (confirmed, null_then_empty_probes, capped)."""
import asyncio
from unittest.mock import MagicMock

import pytest

from pyegeria.core import paging
from pyegeria.view import overview_metrics as om

pytestmark = pytest.mark.unit

REASON = "Egeria didn't confirm there are no more"
NULL = "No elements found"


def _ce(rows, full_pages=False):
    """get_relationships paging like Egeria: rows from startFrom, then null; full_pages: every page full."""
    def fake(*a, relationship_type=None, body=None, **kw):
        start, size = body["startFrom"], body["pageSize"]
        if full_pages:
            return [{"relationshipHeader": {"guid": f"r{start + i}"},
                     "end1": {"guid": f"a{(start + i) % 3}"}} for i in range(size)]
        return rows[start:start + size] or NULL
    ce = MagicMock()
    ce.get_relationships.side_effect = fake
    return ce


ROWS = [{"relationshipHeader": {"guid": f"r{i}"}, "end1": {"guid": f"a{i % 3}"}} for i in range(6)]


# One figure function per kind, built on the real scan helper and the real marking.

@om._marks_unconfirmed({"links": "count"})
def _count_figure(ce):
    rels = om._all_relationships(ce, "SemanticAssignment")
    return {"links": None if rels is None else len(rels)}


@om._marks_unconfirmed({"pct": ("percent", "read")})
def _percent_figure(ce):
    rels = om._all_relationships(ce, "SemanticAssignment")   # numerator and denominator: the same read
    if rels is None:
        return {"pct": None, "read": None}
    on_a0 = sum(1 for r in rels if r["end1"]["guid"] == "a0")
    return {"pct": round(100 * on_a0 / len(rels)), "read": len(rels)}


@om._marks_unconfirmed({"assets": "distinct"})
def _distinct_figure(ce):
    rels = om._all_relationships(ce, "SemanticAssignment")
    return {"assets": None if rels is None else len({r["end1"]["guid"] for r in rels})}


FIGURES = {"count": (_count_figure, "links", 6, "at least 6"),
           "percent": (_percent_figure, "pct", 33, f"33% of the 6 read; {REASON}"),
           "distinct": (_distinct_figure, "assets", 3, f"3 found; {REASON}")}


@pytest.mark.parametrize("kind", FIGURES)
def test_confirmed_figures_are_unchanged(monkeypatch, kind):
    # A confirmed end is simulated at the seam (a #9454 platform gives one for real: the G2 R1 tests below).
    monkeypatch.setattr(paging, "paging_for", lambda method, client=None: {"end_policy": "trusted"})
    fn, key, value, _words = FIGURES[kind]
    with om.recording_unmeasured() as notes, om.recording_unconfirmed() as scans:
        r = fn(_ce(ROWS))
    assert r[key] == value and "unconfirmed" not in r and notes == [] and scans == []


@pytest.mark.parametrize("kind", FIGURES)
def test_null_then_empty_probes_computes_over_what_was_read_and_marks_it(kind):
    fn, key, value, words = FIGURES[kind]
    with om.recording_unmeasured() as notes, om.recording_unconfirmed() as scans:
        r = fn(_ce(ROWS))
    assert r[key] == value
    assert r["unconfirmed"][key] == {"unconfirmed": True, "positions_read": 4000, "reason": REASON,
                                     "words": words}
    assert notes == []   # not "not measured": the executor would withhold the figure
    assert scans and scans[0]["unconfirmed"] is True


@pytest.mark.parametrize("kind", FIGURES)
def test_capped_counts_say_at_least_and_shares_are_not_measured(monkeypatch, kind):
    monkeypatch.setattr(om, "MAX_SCAN_PAGES", 2)
    fn, key, _value, _words = FIGURES[kind]
    with om.recording_unmeasured() as notes:
        r = fn(_ce([], full_pages=True))
    assert r[key] is None and "unconfirmed" not in r          # never 0, never a bare number
    assert notes[0]["at_least"] == 2 * om.DEFAULT_CAP           # the lower bound rides on the note
    assert "stopped after 2 pages" in notes[0]["reason"]


def test_a_share_of_a_separate_count_is_not_stated_when_its_numerator_is_unconfirmed():
    mgr = MagicMock(spec=["platform_url", "view_server", "count_metadata_elements"])
    mgr.count_metadata_elements.return_value = {"count": 384}
    with om.recording_unmeasured() as notes:
        r = om.contextualised_coverage(mgr, _ce([{"relationshipHeader": {"guid": "r1"},
                                                  "end1": {"guid": "c1", "type": {"typeName": "SolutionComponent"}},
                                                  "end2": {"guid": "a1", "type": {"typeName": "Asset"}}}]))
    assert r["contextualisedCount"] == 1 and r["contextualisedPct"] is None
    assert any(n["count"] == "contextualisedPct" and "isn't from one read" in n["reason"] for n in notes)


def test_the_executor_carries_unconfirmed_scans_on_an_analytic_output(monkeypatch):
    from pyegeria.view import format_set_executor as fse
    ce = _ce(ROWS)
    monkeypatch.setattr(fse, "_run_analytic_function", lambda action, **kw: om.count_relationships(
        ce, "SemanticAssignment", population="viewer"))
    result, notes = fse._run_recording_unmeasured({"analytic_function": "x"}, params={})
    assert result == 6 and notes == []
    extra = fse._unconfirmed_extra()
    assert extra["unconfirmed"][0]["count"] == "SemanticAssignment relationships"
    assert extra["unconfirmed"][0]["reason"] == REASON


# ── the Architect's ruling after the step 4 capture ──

def test_orphan_count_is_not_measured_unless_the_scan_is_confirmed():
    mgr = MagicMock(spec=["platform_url", "view_server", "count_metadata_elements"])
    mgr.count_metadata_elements.return_value = {"count": 10}
    rels = [{"relationshipHeader": {"guid": "r1"}, "end1": {"guid": "a1", "type": {"typeName": "CSVFile"}},
             "end2": {"guid": "t1", "type": {"typeName": "GlossaryTerm"}}}]
    with om.recording_unmeasured() as notes:
        r = om.orphan_glossary_terms(mgr, _ce(rels))
    assert r["referencedCount"] == 1 and r["orphanCount"] is None            # never "at most 9"
    assert "orphanCount" not in r["unconfirmed"]
    assert any(n["count"] == "orphanCount" and "needs the whole set" in n["reason"] for n in notes)


def test_a_null_not_end_method_never_reaches_the_end_and_probes_six_pages():
    assert paging.NULL_NOT_END_METHODS - paging.BY_TYPE_METHODS == {"find_metadata_elements", "get_relationships",
                                           "_async_get_relationships",   # + G2: the same server call
                                           "get_elements_by_property_value", "find_elements_by_property_value",
                                           "_async_get_elements_by_property_value"   # + the exists-lookups ruling
                                           } | paging.BY_NAME_METHODS   # + the MyEgeria read-back R3 (findMetadataElements)
    assert paging.BY_TYPE_METHODS < paging.NULL_NOT_END_METHODS   # + P3 ruling (c): elements/by-type, the same
    calls = []

    def fetch(start, size):
        calls.append(start)
        return [{"guid": "a"}] if start == 0 else NULL

    r = paging.page_all(fetch, fetch_page_size=25, **paging.paging_for("get_relationships"))
    assert r.end_reason == "null_then_empty_probes" and r.reached_end is False and r.null_not_end is True
    assert calls == [0, 25] + [25 * k for k in range(2, 8)]   # the null at 25, then 6 probes
    plain = paging.page_all(fetch, fetch_page_size=25)          # another suspect method: 3 probes, an end
    assert plain.reached_end is True and plain.positions_read == 25 * 5


def test_a_run_of_three_mid_set_nulls_is_read_through():
    # the capture's governed_coverage @25: nulls at 25, 50, 75, then rows at 100
    pages = {0: [{"guid": "a"}], 100: [{"guid": "b"}]}
    r = paging.page_all(lambda s, n: pages.get(s, NULL), fetch_page_size=25,
                        **paging.paging_for("find_metadata_elements"))
    assert [x["guid"] for x in r.items] == ["a", "b"]


def test_null_not_end_methods_can_never_be_trusted():
    assert not (paging.TRUSTED_END_METHODS & paging.NULL_NOT_END_METHODS)
    assert all(paging.end_policy_for(m) == "suspect" for m in paging.NULL_NOT_END_METHODS)


def test_no_write_path_reads_from_a_null_not_end_method():
    """The ruling: no write path may act on a read from find_metadata_elements / get_relationships (a null is
    never the end there). The write paths that page today, by source."""
    import inspect

    from md_processing.v2 import dashboard_sheet, processors
    from pyegeria.authoring import drafts, publication
    from pyegeria.view import saved_query
    # Not listed, by ruling:
    # - drafts.async_prune_drafts / async_list: prune reads drafts through find_elements_by_property_value
    #   (NULL_NOT_END), but deletes only drafts it actually read, never on absence or a count (asserted in
    #   test_prune_decides_only_from_rows_read below);
    # - dashboard_sheet._resolve_report: a placement link is a reversible relationship; the ruling (a)+(b) lets a
    #   single display-name match be linked with a note, never a link on a limit, 2+ or 0 (its own tests).
    write_paths = [publication.async_read_history, publication._find_exact,
                   processors.AsyncBaseCommandProcessor._parent_links_of_type,
                   saved_query._all_related, saved_query.delete_saved_query,
                   dashboard_sheet.DashboardSheetEgeriaWriter._related]
    for fn in write_paths:
        source = inspect.getsource(fn)
        for method in paging.NULL_NOT_END_METHODS:
            assert method not in source, f"{fn.__qualname__} reads {method}: a null is never the end there"



def test_prune_decides_only_from_rows_read():
    """drafts.async_prune_drafts acts only on drafts it read: a draft not in the read is never deleted, an
    empty (unconfirmed) read deletes nothing, and no decision uses a count or an "absent" answer."""
    from datetime import datetime, timedelta, timezone

    from pyegeria.authoring.drafts import EgeriaDraftStore
    zone = "private-erin"
    old = (datetime.now(timezone.utc) - timedelta(days=400)).isoformat()
    store = object.__new__(EgeriaDraftStore)
    store._author = lambda user: zone
    deleted = []

    async def delete(user, kind, name):
        deleted.append(name)
        return True
    store.async_delete = delete

    def listing(rows):
        async def async_list(user, kind=None, notes=None):
            if notes is not None:
                notes.append("Showing at least ...")
            return rows
        return async_list

    row = {"kind": "spec", "name": "Old", "updated": old, "zones": [zone], "marked": True, "published_version": None}
    store.async_list = listing([row])
    out = asyncio.run(store.async_prune_drafts("erin"))
    assert deleted == ["Old"] and out["removed"] == ["spec:Old"] and out["read_notes"]
    deleted.clear()
    store.async_list = listing([])   # nothing read (an unconfirmed, empty read): nothing is deleted
    out = asyncio.run(store.async_prune_drafts("erin"))
    assert deleted == [] and out["removed"] == []


# ── G2 R1: the Overview's relationship scans pass their client, so the #9454 gate can promote them ──

class _CeOn:
    """_ce(ROWS) on a platform whose /api/about is a 6.3-SNAPSHOT built at `about_time`."""

    def __init__(self, about_time, url):
        self.platform_url, self._time, self._ce = url, about_time, _ce(ROWS)

    def get_relationships(self, *a, **kw):
        return self._ce.get_relationships(*a, **kw)

    def get_platform_origin(self):
        import json
        return json.dumps({"version": "6.3-SNAPSHOT", "time": self._time})


def _ce_on(about_time, url):
    return _CeOn(about_time, url)


@pytest.fixture
def _fresh_gate(monkeypatch):
    paging._GATE_CACHE.clear()
    monkeypatch.delenv(paging.GATE_OVERRIDE_ENV, raising=False)
    yield
    paging._GATE_CACHE.clear()


def test_a_9454_client_makes_the_relationship_scan_trusted_and_complete(_fresh_gate, monkeypatch):
    seen = []
    real = paging.page_all
    monkeypatch.setattr(paging, "page_all", lambda fetch, **kw: seen.append(kw) or real(fetch, **kw))
    with om.recording_unconfirmed() as scans:
        rels = om._all_relationships(_ce_on("2026-11-15T08:29:25.754Z", "https://a5c3a195"), "SemanticAssignment")
    assert seen[-1]["end_policy"] == "trusted" and "null_not_end" not in seen[-1]
    assert len(rels) == 6 and scans == []   # a confirmed end: the figure is a total, no unconfirmed marker


def test_a_9453_only_client_keeps_the_relationship_scan_null_not_end(_fresh_gate, monkeypatch):
    seen = []
    real = paging.page_all
    monkeypatch.setattr(paging, "page_all", lambda fetch, **kw: seen.append(kw) or real(fetch, **kw))
    with om.recording_unconfirmed() as scans:
        rels = om._all_relationships(_ce_on("2026-11-14T19:55:39.317Z", "https://5deda38d"), "SemanticAssignment")
    assert seen[-1]["null_not_end"] is True and seen[-1]["probe_pages"] == paging.NULL_NOT_END_PROBE_PAGES
    assert len(rels) == 6 and scans and scans[0]["unconfirmed"] is True   # what was read, marked: never a total
