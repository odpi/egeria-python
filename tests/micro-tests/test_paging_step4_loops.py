"""Pager step 4 (ruling (A), 2026-11-13): the loops on page_all. Per loop: a null-then-empty-probes end is
acted on as the end (with the trace for the write paths); the empty-run cap is incomplete; display loops say
"at least", never a total or "none", unless the end is confirmed."""
import asyncio

import pytest

from pyegeria.core.paging import END_REASONS, page_all

pytestmark = pytest.mark.unit

NULL = "No elements found"


# ── PageResult.end_reason ──

@pytest.mark.parametrize("pages,policy,reason,reached", [
    ({0: [{"guid": "a"}]}, "trusted", "trusted_null", True),
    ({0: [{"guid": "a"}]}, "suspect", "null_then_empty_probes", True),
    ({n: [] for n in range(0, 5000, 100)}, "suspect", "empty_run_cap", False),
    ({n: [{"guid": "a"}] for n in range(0, 500, 100)}, "suspect", "stalled", False),
])
def test_end_reason_and_reached_end(pages, policy, reason, reached):
    r = page_all(lambda s, n: pages.get(s, NULL), end_policy=policy)
    assert r.end_reason == reason and r.end_reason in END_REASONS and r.reached_end is reached
    assert r.trace() == {"positions_read": r.positions_read, "end": r.end, "end_reason": reason}


def test_max_pages_and_want_are_their_own_reasons():
    rows = lambda s, n: [{"guid": f"g{s + i}"} for i in range(n)]   # noqa: E731
    assert page_all(rows, max_pages=2).end_reason == "max_pages"
    assert page_all(rows, want=5).end_reason == "want"


def test_stall_pages_tolerates_one_overlapping_page_but_not_the_same_page_twice():
    overlap = {0: [{"guid": "a"}, {"guid": "b"}], 100: [{"guid": "b"}], 200: [{"guid": "c"}]}
    r = page_all(lambda s, n: overlap.get(s, NULL), stall_pages=2)
    assert [x["guid"] for x in r.items] == ["a", "b", "c"] and r.end_reason == "null_then_empty_probes"
    same = lambda s, n: [{"guid": "a"}]   # noqa: E731
    assert page_all(same, stall_pages=2).end_reason == "stalled"


# ── a write path: publication history ──

class _History:
    def __init__(self, entries, tail=NULL):
        self.entries, self.tail, self.calls = entries, tail, []

    async def _async_get_element_history(self, guid, oldest_first=False, start_from=0, page_size=0, **kw):
        self.calls.append((start_from, page_size))
        page = self.entries[start_from:start_from + page_size]
        return page or self.tail


def _entry(v):
    return {"elementGUID": "g1", "versions": {"version": v, "updateTime": f"t{v}"},
            "elementProperties": {"propertyValueMap": {}}}


def test_history_acts_on_null_then_empty_probes_and_carries_the_trace():
    from types import SimpleNamespace

    from pyegeria.authoring.publication import HISTORY_PAGE, async_read_history
    me = _History([_entry(v) for v in (3, 2, 1)])
    trace = {}
    entries, why = asyncio.run(async_read_history(SimpleNamespace(metadata_expert=me), "g1", trace=trace))
    assert len(entries) == 3 and why is None              # every version of one GUID kept (its own key)
    assert HISTORY_PAGE >= 100 and {size for _, size in me.calls} == {HISTORY_PAGE}
    assert trace == {"method": "publication.async_read_history", "positions_read": 5 * HISTORY_PAGE,   # rows, the null, 3 probes
                     "end": "not_confirmed", "end_reason": "null_then_empty_probes"}


def test_history_empty_run_cap_is_incomplete():
    from types import SimpleNamespace

    from pyegeria.authoring.publication import async_read_history
    me = _History([], tail=[])   # every page filtered
    entries, why = asyncio.run(async_read_history(SimpleNamespace(metadata_expert=me), "g1"))
    assert entries == [] and "wasn't read whole" in why and "consecutive positions" in why


# ── a write path: Dr.Egeria parent links ──

def _parent_sync(element_list_at):
    from md_processing.v2.processors import AsyncBaseCommandProcessor

    class Expert:
        reads, created = [], []

        async def _async_get_all_related_elements(self, guid, starting_at_end=0, start_from=0, page_size=0, **kw):
            Expert.reads.append(start_from)
            got = element_list_at(start_from)
            return {"startingElement": {"guid": guid}, **({} if got is None else {"elementList": got})}

        async def _async_create_related_elements(self, body):
            Expert.created.append(body["type_name"])

    class P(AsyncBaseCommandProcessor):
        async def apply_changes(self):  # pragma: no cover
            raise NotImplementedError

    proc = object.__new__(P)
    proc.client = type("C", (), {"metadata_expert": Expert()})()
    proc.related_results, proc.warnings = [], []
    proc._add_warning = lambda w: None
    attrs = {"Parent ID": {"guid": "root"}, "Parent Relationship Type Name": {"value": "CollectionMembership"},
             "Parent at End1": {"value": True}}
    asyncio.run(proc._sync_parent_relationship("folder", attrs))
    return proc, Expert


def test_parent_links_act_on_null_then_empty_probes_with_the_trace():
    proc, expert = _parent_sync(lambda start: [] if start == 0 else None)
    assert expert.created == ["CollectionMembership"]
    assert proc._parent_link_read["end_reason"] == "null_then_empty_probes"
    assert "Egeria didn't confirm there were no more" in proc.related_results[-1]["message"]


def test_parent_links_empty_run_cap_refuses():
    proc, expert = _parent_sync(lambda start: [])   # every page filtered
    assert expert.created == []
    assert proc.related_results[-1]["status"] == "failure"
    assert "empty_run_cap" in proc.related_results[-1]["message"]


# ── display loops: "at least" ──

def test_drafts_list_says_at_least_unless_confirmed():
    from pyegeria.authoring.drafts import EgeriaDraftStore as DraftStore
    zone = "private-erin"

    class CM:
        async def _async_get_elements(self, *a, start_from=0, **kw):
            return [{"elementHeader": {"guid": "d1", "versions": {}}, "properties": {"qualifiedName": "Q",
                     "displayName": "D"}}] if start_from == 0 else NULL

    store = object.__new__(DraftStore)
    store.client = type("C", (), {"classification_manager": CM()})()
    store._author = lambda user: zone
    store._zones = lambda el: [zone]
    notes = []
    out = asyncio.run(store.async_list("erin", "spec", notes=notes))
    assert [d["name"] for d in out] == ["D"]
    assert notes and notes[0].startswith("Showing at least 1 spec drafts")


def test_folder_members_unconfirmed_is_recorded_and_a_cap_raises():
    from pyegeria.view import egeria_folders as ef

    class C:
        def __init__(self, at):
            self.at = at

        def get_collection_members(self, collection_guid=None, start_from=0, page_size=0, **kw):
            return self.at(start_from)

    unconfirmed = []
    got = ef._members(C(lambda s: [{"elementHeader": {"guid": "m1"}}] if s == 0 else NULL), "f1", unconfirmed)
    assert [m["elementHeader"]["guid"] for m in got] == ["m1"] and unconfirmed == ["f1"]
    rows = lambda s: [{"elementHeader": {"guid": f"m{s + i}"}} for i in range(ef.MEMBERS_PAGE)]   # noqa: E731
    with pytest.raises(ef.FolderTooLarge):
        ef._members(C(rows), "f2")
