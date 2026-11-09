# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Dashboard analytics that count inside Egeria instead of paging results (6.2.29).

`stale_assets`: Egeria cannot count by an update-time condition (a search condition reaches only an
element's own properties; `updateTime LT <cutoff>` counts 0, checked live 2026-11-09). It does sort by
update time, and `startFrom` is an offset into the repository's sorted rows -- a row the viewer cannot
see keeps its offset and reads as an empty one-row page. So the stale count is the offset of the first
row updated at or after the cutoff, found by bisection: about log2(total / 25) one-row reads, then one
read of the last 25-row window. Live, as erinoverview: 287 of 37,431 Assets, where 6.2.28 read a
500-Asset page and reported "not measured".

`orphan_glossary_terms`: distinct relationship ends cannot be counted natively, so the
SemanticAssignment scan stays; its slow viewer term count now runs while the scan pages.

The fake below is a sorted repository: a list of update times (None = a row the viewer cannot see).
"""
import random
import threading
from datetime import datetime, timedelta, timezone

import pytest
from unittest.mock import MagicMock

from pyegeria.view import overview_metrics as om

AS_OF = "2026-11-09T00:00:00Z"
NOW = datetime(2026, 11, 9, tzinfo=timezone.utc)
CUTOFF = NOW - timedelta(days=180)
OLD, NEW = "2026-04-01T06:45:49.989+00:00", "2026-11-07T15:09:37.189+00:00"
WHAT = "Assets not updated within 180 days"


@pytest.fixture(autouse=True)
def _clean():
    om._count_caps.clear()
    om._native_server_ok.clear()
    yield
    om._count_caps.clear()
    om._native_server_ok.clear()


class _SortedRepo:
    """count_metadata_elements answers len(rows); find_metadata_elements serves rows[startFrom:+pageSize]
    in LAST_UPDATE_OLDEST order, leaving out hidden rows (None), as Egeria does."""

    def __init__(self, rows, count=None, fail_find_at=None):
        self.rows, self.count, self.fail_find_at = rows, count, fail_find_at
        self.finds, self.counts = [], []
        self.platform_url, self.view_server = "https://localhost:9443", "test-server"

    def count_metadata_elements(self, body, **kw):
        self.counts.append((body, kw))
        if isinstance(self.count, BaseException):
            raise self.count
        return {"count": len(self.rows) if self.count is None else self.count}

    def find_metadata_elements(self, body, *a, **kw):
        self.finds.append(body)
        if self.fail_find_at is not None and len(self.finds) > self.fail_find_at:
            raise RuntimeError("read failed")
        assert body["sequencingOrder"] == "LAST_UPDATE_OLDEST"
        s, n = body["startFrom"], body["pageSize"]
        return [{"elementGUID": f"a{i}", "versions": {"createTime": t, "updateTime": t}}
                for i, t in enumerate(self.rows[s:s + n], start=s) if t is not None]


def _rows(n_stale, n_recent, hidden=()):
    rows = [OLD] * n_stale + [NEW] * n_recent
    for i in hidden:
        rows[i] = None
    return rows


def test_stale_count_is_the_offset_of_the_first_recent_row_found_by_bisection():
    repo = _SortedRepo(_rows(287, 37431 - 287))
    with om.recording_unmeasured() as notes:
        r = om.stale_assets(repo, as_of=AS_OF)
    assert r == {"staleCount": 287, "assetTotal": 37431}
    assert notes == []
    # log2(37,431 / 25) one-row reads, then one read of the last window: never a page of Assets
    assert len(repo.finds) <= 13
    assert [b["pageSize"] for b in repo.finds][:-1] == [1] * (len(repo.finds) - 1)
    assert repo.finds[-1]["pageSize"] <= om.BISECT_WINDOW
    assert all(b["asOfTime"] == AS_OF and b["metadataElementTypeName"] == "Asset" for b in repo.finds)
    assert repo.counts[0][1] == {"push_down": True}           # the repository population


def test_hidden_rows_among_stale_rows_are_stale_too():
    # Rows the viewer cannot see between two stale rows were updated before the cutoff (the order is by
    # update time), so they count: the figure is in the repository population, like assetTotal.
    repo = _SortedRepo(_rows(300, 700, hidden=range(100, 150)))
    assert om.stale_assets(repo, as_of=AS_OF) == {"staleCount": 300, "assetTotal": 1000}


@pytest.mark.parametrize("hidden", [[290], [299], [300], [296, 297, 303]])
def test_a_hidden_row_near_the_cutoff_still_gives_the_exact_count(hidden):
    # Hidden rows strictly inside the stale run or the recent run are placed by the order; the last window
    # is read once, and if it holds a hidden row the bisection carries on one row at a time.
    repo = _SortedRepo(_rows(300, 700, hidden=hidden))
    with om.recording_unmeasured() as notes:
        r = om.stale_assets(repo, as_of=AS_OF)
    if r["staleCount"] is None:   # a hidden row sat exactly at the cutoff: the range must hold 300
        assert notes[0]["at_least"] <= 300 and "between" in notes[0]["reason"]
    else:
        assert r == {"staleCount": 300, "assetTotal": 1000}
    assert sum(1 for b in repo.finds if b["pageSize"] > 1) <= 1


def test_hidden_rows_at_the_cutoff_give_a_range_not_a_count():
    repo = _SortedRepo(_rows(300, 700, hidden=range(295, 305)))
    with om.recording_unmeasured() as notes:
        r = om.stale_assets(repo, as_of=AS_OF)
    assert r == {"staleCount": None, "assetTotal": 1000}
    assert notes == [{"count": WHAT, "at_least": 295,
                      "reason": "the 10 rows between the last one updated before the cutoff and the first one "
                                "updated after it are not visible to you, so there are between 295 and 305"}]


def test_a_failed_asset_count_measures_neither_and_reads_nothing():
    repo = _SortedRepo(_rows(10, 10), count=RuntimeError("timed out"))
    with om.recording_unmeasured() as notes:
        r = om.stale_assets(repo, as_of=AS_OF)
    assert r == {"staleCount": None, "assetTotal": None}       # never 0
    assert repo.finds == []
    assert [n["count"] for n in notes] == ["Asset", WHAT]
    assert notes[1]["reason"] == "the Asset count it bisects over was not measured"


def test_a_failed_read_is_not_measured():
    repo = _SortedRepo(_rows(300, 700), fail_find_at=3)
    with om.recording_unmeasured() as notes:
        r = om.stale_assets(repo, as_of=AS_OF)
    assert r == {"staleCount": None, "assetTotal": 1000}
    assert notes == [{"count": WHAT, "at_least": None,
                      "reason": "a read of the rows in update-time order failed"}]


def test_the_bisection_has_a_read_budget(monkeypatch):
    monkeypatch.setattr(om, "MAX_BISECT_READS", 4)
    repo = _SortedRepo(_rows(300, 700))
    with om.recording_unmeasured() as notes:
        assert om.stale_assets(repo, as_of=AS_OF)["staleCount"] is None
    assert len(repo.finds) == 4
    assert notes[0]["count"] == WHAT and "used all 4 of its one-row reads" in notes[0]["reason"]


@pytest.mark.parametrize("n_stale, n_recent, want", [(0, 50, 0), (50, 0, 50), (0, 0, 0), (1, 0, 1), (0, 1, 0)])
def test_the_edges(n_stale, n_recent, want):
    repo = _SortedRepo(_rows(n_stale, n_recent))
    assert om.stale_assets(repo, as_of=AS_OF) == {"staleCount": want, "assetTotal": n_stale + n_recent}


def test_as_of_anchors_the_cutoff():
    # 2026-04-01 is stale on 2026-11-09 but not on 2026-05-01.
    repo = _SortedRepo(_rows(5, 5))
    assert om.stale_assets(repo, as_of="2026-05-01T00:00:00Z")["staleCount"] == 0
    assert om.stale_assets(repo, as_of=AS_OF, days=1)["staleCount"] == 10


@pytest.mark.parametrize("seed", range(40))
def test_bisection_agrees_with_counting_every_row(seed):
    rng = random.Random(seed)
    n = rng.randint(1, 3000)
    start = CUTOFF - timedelta(days=400)
    times = sorted(start + timedelta(minutes=rng.randint(0, 800 * 24 * 60)) for _ in range(n))
    rows = [t.isoformat() if rng.random() > 0.2 else None for t in times]   # a fifth hidden
    truth = sum(1 for t in times if t < CUTOFF)
    repo = _SortedRepo(rows)
    with om.recording_unmeasured() as notes:
        r = om.stale_assets(repo, as_of=AS_OF)
    if r["staleCount"] is None:   # hidden rows at the cutoff: the note's range holds the truth
        lo = notes[0]["at_least"]
        hi = int(notes[0]["reason"].rsplit(" and ", 1)[1])
        assert lo <= truth <= hi
        assert all(rows[i] is None for i in range(lo, hi))
    else:
        assert r["staleCount"] == truth
    assert len(repo.finds) <= om.MAX_BISECT_READS


def test_stale_assets_is_declared_in_the_repository_population():
    from pyegeria.view.analytic_registry import get_analytic_registry
    measures = {m.name: m for m in get_analytic_registry()["stale_assets"].declaration.measures}
    assert measures["stale_assets"].population == "repository"
    assert measures["assets"].population == "repository"


# ── orphan_glossary_terms ──────────────────────────────────────────────────

def _assignments(n_rels, n_terms):
    return [{"relationshipHeader": {"guid": f"r{i}"},
             "end1": {"guid": f"a{i}", "type": {"typeName": "CSVFile"}},
             "end2": {"guid": f"t{i % n_terms}", "type": {"typeName": "GlossaryTerm"}}} for i in range(n_rels)]


def _ce(rels, on_read=None):
    ce = MagicMock()

    def fake(*a, relationship_type=None, body=None, **kw):
        if on_read:
            on_read()
        return rels[body["startFrom"]:body["startFrom"] + body["pageSize"]]
    ce.get_relationships.side_effect = fake
    return ce


def test_orphan_term_count_runs_while_the_scan_pages():
    scan_started = threading.Event()
    seen = {}
    mgr = MagicMock(spec=["platform_url", "view_server", "count_metadata_elements", "find_metadata_elements"])

    def count(body, **kw):
        # Sequential code would count first and wait here for a scan that has not started.
        seen["concurrent"] = scan_started.wait(timeout=5)
        seen["push_down"] = kw.get("push_down")
        return {"count": 1061}
    mgr.count_metadata_elements.side_effect = count
    r = om.orphan_glossary_terms(mgr, _ce(_assignments(747, 77), on_read=scan_started.set))
    assert r == {"termTotal": 1061, "referencedCount": 77, "orphanCount": 984}
    assert seen == {"concurrent": True, "push_down": False}   # the viewer population, as the scan


def test_the_term_count_note_from_its_thread_reaches_the_caller():
    mgr = MagicMock(spec=["platform_url", "view_server", "count_metadata_elements", "find_metadata_elements"])
    mgr.count_metadata_elements.side_effect = RuntimeError("timed out")
    mgr.find_metadata_elements.side_effect = RuntimeError("down")
    with om.recording_unmeasured() as notes:
        r = om.orphan_glossary_terms(mgr, _ce(_assignments(10, 3)))
    assert r == {"termTotal": None, "referencedCount": 3, "orphanCount": None}
    assert [n["count"] for n in notes] == ["GlossaryTerm"]
    assert notes[0]["reason"] == "the native count timed out, and the find fallback failed"
