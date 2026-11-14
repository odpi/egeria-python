"""Pager step 4, the Architect's overview_metrics ruling (ii), 2026-11-14: a scan-based figure, by kind
(count, percentage, distinct count) x how its scan ended (confirmed, null_then_empty_probes, capped)."""
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
    monkeypatch.setattr(paging, "TRUSTED_END_METHODS", paging.TRUSTED_END_METHODS | {"get_relationships"})
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
    assert r["unconfirmed"][key] == {"unconfirmed": True, "positions_read": 2500, "reason": REASON,
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
