"""G2-G4, the per-fix paging gate (#9453 and #9454; the Architect's G2 brief and ruling, 2026-11-15).

#9454 (970092b9) fixed get_relationships and get_related_elements: on a platform that carries it they send [] for
a filtered page and null only at the end (G1 capture, laz a5c3a195). Without it:
- get_relationships (and _async_get_relationships, the same server call) stays NULL_NOT_END;
- get_related_elements stays plain suspect, as before (ruling 1: never shown sending a mid-set null).
The find / by-name / by-type reads keep needing #9453 only."""
import asyncio
import json

import pytest

from pyegeria.core import paging

pytestmark = pytest.mark.unit

NULL = "No elements found"
LAZ_A5C3A195 = {"version": "6.3-SNAPSHOT", "time": "2026-11-15T08:29:25.754Z"}   # main c61bad65: #9453 + #9454
LAZ_5DEDA38D = {"version": "6.3-SNAPSHOT", "time": "2026-11-14T19:55:39.317Z"}   # #9453 only (between the cutoffs)
LAZ_002A3EF1 = {"version": "6.3-SNAPSHOT", "time": "2026-11-10T08:00:00.000Z"}   # neither
BOTH = {paging.FIX_9453, paging.FIX_9454}
FIND_METHODS = sorted(m for m, needs in paging.METHOD_NEEDS.items() if needs == {paging.FIX_9453})


@pytest.fixture(autouse=True)
def _fresh_gate(monkeypatch):
    paging._GATE_CACHE.clear()
    monkeypatch.delenv(paging.GATE_OVERRIDE_ENV, raising=False)
    yield
    paging._GATE_CACHE.clear()


class _Platform:
    def __init__(self, about, url="https://laz:9443"):
        self.about, self.platform_url, self.about_reads = about, url, 0

    def _answer(self):
        self.about_reads += 1
        if isinstance(self.about, BaseException):
            raise self.about
        return self.about if isinstance(self.about, str) else json.dumps(self.about)

    def get_platform_origin(self):
        return self._answer()

    async def async_get_platform_origin(self):
        return self._answer()


# ── the table ──

def test_each_fix_has_a_cutoff_a_floor_and_a_later_line_rule():
    assert set(paging.FIXES) == BOTH
    assert paging.FIXES["9453"]["snapshot_cutoff"] == paging.GATE_SNAPSHOT_TIME == "2026-11-14T19:52:00Z"
    assert paging.FIXES["9453"]["release_floor"] == (6, 3, 0)
    assert paging.FIXES["9454"]["snapshot_cutoff"] == "2026-11-15T07:26:00Z"
    assert paging.FIXES["9454"]["release_floor"] is None          # G3: set only from the 6.3.0 tag check
    assert paging.FIXES["9454"]["later_snapshots"] is True        # ruling 4


def test_each_method_needs_its_own_fix():
    for m in ("find_metadata_elements", "get_elements_by_property_value", "get_collections_by_name", "get_elements"):
        assert paging.METHOD_NEEDS[m] == {"9453"}, m
    for m in ("get_relationships", "_async_get_relationships", "get_related_elements", "_async_get_related_elements"):
        assert paging.METHOD_NEEDS[m] == {"9454"}, m


# ── each fix, each side of its snapshot cutoff ──

@pytest.mark.parametrize("about, fixes", [
    ({"version": "6.3-SNAPSHOT", "time": "2026-11-14T19:51:59Z"}, set()),            # just before 9453
    ({"version": "6.3-SNAPSHOT", "time": "2026-11-14T19:52:00Z"}, {"9453"}),         # at 9453
    ({"version": "6.3-SNAPSHOT", "time": "2026-11-15T07:25:59Z"}, {"9453"}),         # just before 9454
    ({"version": "6.3-SNAPSHOT", "time": "2026-11-15T07:26:00Z"}, BOTH),             # at 9454
    (LAZ_A5C3A195, BOTH), (LAZ_5DEDA38D, {"9453"}), (LAZ_002A3EF1, set()),
])
def test_each_fix_on_each_side_of_its_snapshot_cutoff(about, fixes):
    assert paging.fixes_from_about(about) == fixes
    assert paging.gate_from_about(about) is ("9453" in fixes)   # the back-compatible 9453 alias


# ── the release floor ──

@pytest.mark.parametrize("version", ["6.3", "6.3.0", "6.3.2", "6.4.1", "7.0"])
def test_a_release_carries_9453_but_not_9454_while_its_floor_is_none(version):
    assert paging.fixes_from_about({"version": version}) == {"9453"}


def test_a_release_floor_present_promotes_releases_from_it_on(monkeypatch):
    monkeypatch.setitem(paging.FIXES, "9454", {**paging.FIXES["9454"], "release_floor": (6, 3, 0)})
    assert paging.fixes_from_about({"version": "6.3.0"}) == BOTH
    assert paging.fixes_from_about({"version": "6.4"}) == BOTH
    assert paging.fixes_from_about({"version": "6.2.9"}) == set()


@pytest.mark.parametrize("about, fixes", [
    ({"version": "6.4-SNAPSHOT"}, BOTH), ({"version": "7.0.1-SNAPSHOT"}, BOTH),       # later lines: both (ruling 4)
    ({"version": "6.2-SNAPSHOT", "time": "2027-01-01T00:00:00Z"}, set()),             # earlier lines: none
    ({"version": "6.3.1-SNAPSHOT", "time": "2027-01-01T00:00:00Z"}, set()),           # not the main-line SNAPSHOT
])
def test_snapshots_of_other_lines(about, fixes):
    assert paging.fixes_from_about(about) == fixes


# ── fail-safe ──

@pytest.mark.parametrize("about", [None, "not json", [], {"name": "x"}, {"version": "6.3-SNAPSHOT"},
                                   {"version": "6.3-SNAPSHOT", "time": "yesterday"},
                                   {"version": "6.3-SNAPSHOT", "time": "2026-11-15T08:29:25"}])   # no timezone
def test_an_unreadable_about_is_no_fixes(about):
    assert paging.fixes_from_about(about) == set()


def test_an_about_read_that_fails_is_no_fixes_and_every_read_is_untrusted():
    client = _Platform(ConnectionError("down"))
    assert paging.platform_fixes(client) == set()
    assert asyncio.run(paging.async_platform_fixes(_Platform(TimeoutError("x"), url="https://b"))) == set()
    assert paging.paging_for("get_relationships", client)["null_not_end"] is True
    assert paging.paging_for("get_related_elements", client) == {"end_policy": "suspect"}
    assert paging.paging_for("find_metadata_elements", client)["null_not_end"] is True


def test_override_off_turns_every_fix_off(monkeypatch):
    monkeypatch.setenv(paging.GATE_OVERRIDE_ENV, "off")
    client = _Platform(LAZ_A5C3A195)
    assert paging.platform_fixes(client) == set() and client.about_reads == 0
    assert paging.platform_promoted(client) is False
    assert paging.paging_for("get_relationships", client)["null_not_end"] is True
    assert paging.paging_for("get_related_elements", client) == {"end_policy": "suspect"}
    assert paging.paging_for("find_metadata_elements", client)["null_not_end"] is True


def test_there_is_no_force_on(monkeypatch):
    monkeypatch.setenv(paging.GATE_OVERRIDE_ENV, "on")
    assert paging.platform_fixes(_Platform(LAZ_002A3EF1)) == set()


def test_one_about_read_per_platform_serves_every_fix():
    client = _Platform(LAZ_A5C3A195)
    for method in ("find_metadata_elements", "get_relationships", "get_related_elements", "get_elements"):
        paging.paging_for(method, client)
        asyncio.run(paging.async_paging_for(method, client))
    assert client.about_reads == 1


def test_platform_promoted_is_the_9453_alias():
    assert paging.platform_promoted(_Platform(LAZ_5DEDA38D)) is True
    assert paging.platform_promoted(_Platform(LAZ_A5C3A195, url="https://new")) is True
    assert paging.platform_promoted(_Platform(LAZ_002A3EF1, url="https://old")) is False
    assert asyncio.run(paging.async_platform_promoted(_Platform(LAZ_5DEDA38D, url="https://a"))) is True


# ── a 9453-only platform (a SNAPSHOT between the two cutoffs) ──

@pytest.mark.parametrize("method", ["get_relationships", "_async_get_relationships"])
def test_a_9453_only_platform_keeps_get_relationships_null_not_end(method):
    p = paging.paging_for(method, _Platform(LAZ_5DEDA38D))
    assert p == {"end_policy": "suspect", "probe_pages": paging.NULL_NOT_END_PROBE_PAGES, "null_not_end": True}


@pytest.mark.parametrize("method", ["get_related_elements", "_async_get_related_elements"])
def test_a_9453_only_platform_keeps_get_related_elements_plain_suspect(method):
    # ruling 1: today's behaviour, so delete_saved_query, sheet link reads and link_peer don't regress on releases
    assert paging.paging_for(method, _Platform(LAZ_5DEDA38D)) == {"end_policy": "suspect"}
    assert paging.paging_for(method) == {"end_policy": "suspect"}


@pytest.mark.parametrize("method", FIND_METHODS)
def test_a_9453_only_platform_still_trusts_find(method):
    assert paging.paging_for(method, _Platform(LAZ_5DEDA38D)) == {"end_policy": "trusted"}


# ── a 9454 platform ──

@pytest.mark.parametrize("method", sorted(paging.RELATIONSHIP_METHODS) + FIND_METHODS)
def test_a_9454_platform_trusts_both(method):
    assert paging.paging_for(method, _Platform(LAZ_A5C3A195)) == {"end_policy": "trusted"}
    assert asyncio.run(paging.async_paging_for(method, _Platform(LAZ_A5C3A195, url="https://a"))) == \
        {"end_policy": "trusted"}


def test_a_9454_platform_reads_get_relationships_to_a_confirmed_end():
    rows = {0: [{"guid": "a"}], 25: [], 50: [{"guid": "b"}]}   # [] for a filtered page; null at 75 is the end
    r = paging.page_all(lambda s, z: rows.get(s, NULL), fetch_page_size=25,
                        **paging.paging_for("get_relationships", _Platform(LAZ_A5C3A195)))
    assert [e["guid"] for e in r.items] == ["a", "b"] and r.end == "confirmed" and r.reached_end


def test_the_same_read_on_a_9453_only_platform_is_never_the_end():
    rows = {0: [{"guid": "a"}]}
    r = paging.page_all(lambda s, z: rows.get(s, NULL), fetch_page_size=25,
                        **paging.paging_for("get_relationships", _Platform(LAZ_5DEDA38D)))
    assert r.end == "not_confirmed" and not r.reached_end and r.count_text() == "at least 1"


# ── the client fix at the two call sites (ruling 2) ──

class _Related(_Platform):
    """A client whose get_related_elements answers one short page, then null."""

    def __init__(self, about, url="https://laz:9443"):
        super().__init__(about, url)
        self.classification_manager = self

    def get_related_elements(self, guid, rel, start_at_end=1, start_from=0, page_size=0, output_format="JSON"):
        return [{"elementHeader": {"guid": "q1"}}] if start_from == 0 else NULL

    async def _async_get_related_elements(self, guid, rel, start_at_end=1, start_from=0, page_size=0, **kw):
        return self.get_related_elements(guid, rel, start_at_end, start_from, page_size)


def test_saved_query_links_are_trusted_with_a_9454_client(monkeypatch):
    from pyegeria.view import saved_query
    seen = []
    real = paging.page_all

    def spy(fetch, **kw):
        seen.append(kw.get("end_policy"))
        return real(fetch, **kw)
    monkeypatch.setattr(paging, "page_all", spy)
    items, paged = saved_query._all_related(_Related(LAZ_A5C3A195), "g", "SmartQuery", 1)
    assert seen == ["trusted"] and paged.end == "confirmed"
    paging._GATE_CACHE.clear()
    items, paged = saved_query._all_related(_Related(LAZ_5DEDA38D, url="https://older"), "g", "SmartQuery", 1)
    assert seen[-1] == "suspect" and paged.reached_end   # today's behaviour on a platform without #9454


def test_a_client_less_call_stays_suspect_and_a_9454_client_is_trusted():
    assert paging.paging_for("get_related_elements") == {"end_policy": "suspect"}
    assert asyncio.run(paging.async_paging_for("get_related_elements")) == {"end_policy": "suspect"}
    assert paging.paging_for("get_related_elements", _Platform(LAZ_A5C3A195)) == {"end_policy": "trusted"}


def test_the_dashboard_sheet_related_read_passes_its_client():
    import inspect
    from md_processing.v2 import dashboard_sheet
    src = inspect.getsource(dashboard_sheet)
    assert 'paging_for("get_related_elements")' not in src
    assert 'async_paging_for("get_related_elements", self.client)' in src
