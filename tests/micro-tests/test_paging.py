"""pyegeria.core.paging.page_all: an empty page is not the end; on a suspect path neither is null."""
import asyncio

import pytest

from pyegeria.core._globals import NO_ELEMENTS_FOUND
from pyegeria.core.paging import PageResult, async_page_all, page_all

pytestmark = pytest.mark.unit


def el(n):
    return {"elementHeader": {"guid": f"g{n}"}, "properties": {"displayName": f"E{n}"}}


class Server:
    """A fake Egeria: `pages` maps a start position to what that request returns. Anything not listed is
    null (pyegeria's "No elements found"). Records every (start, size) it was asked for."""

    def __init__(self, pages, null=NO_ELEMENTS_FOUND):
        self.pages, self.null, self.calls = pages, null, []

    def __call__(self, start, size):
        self.calls.append((start, size))
        return self.pages.get(start, self.null)


def guids(result):
    return [e["elementHeader"]["guid"] for e in result.items]


# ── the Revision 3 cases ──

def test_empty_pages_then_rows_then_null_on_a_trusted_path():
    # find_authored_elements DRAFT + GlossaryTerm: [] for the first pages, then the matches, then null.
    srv = Server({0: [], 100: [], 200: [el(1), el(2)], 300: [el(3)]})
    r = page_all(srv, end_policy="trusted")
    assert guids(r) == ["g1", "g2", "g3"]
    assert r.end == "confirmed" and r.complete and r.note is None
    assert r.count_text() == "3"


def test_advance_is_the_page_size_never_the_rows_returned():
    srv = Server({0: [el(1)], 100: [el(2)]})
    page_all(srv, end_policy="trusted")
    assert [s for s, _ in srv.calls] == [0, 100, 200]
    assert {size for _, size in srv.calls} == {100}


def test_suspect_null_then_rows_found_by_a_probe():
    # B5: metadata-expert answers null for a filtered page at 0; the live Topic sits at the next position.
    srv = Server({1: [el(7)]})
    r = page_all(srv, fetch_page_size=1, end_policy="suspect")
    assert guids(r) == ["g7"]
    assert r.end == "not_confirmed"   # after g7, three more nulls: still not proof of the end
    assert r.count_text() == "at least 1"
    assert [s for s, _ in srv.calls] == [0, 1, 2, 3, 4, 5]


def test_suspect_null_with_empty_probes_is_not_confirmed_and_says_why():
    srv = Server({})
    r = page_all(srv, fetch_page_size=25, end_policy="suspect")
    assert r.items == [] and r.end == "not_confirmed" and not r.complete
    assert "position 0" in r.note and "can't be ruled out" in r.note
    assert [s for s, _ in srv.calls] == [0, 25, 50, 75]   # the null, then 3 probes
    assert r.count_text() == "at least 0"


def test_trusted_null_on_the_first_page_is_a_confirmed_nothing():
    srv = Server({})
    r = page_all(srv, end_policy="trusted")
    assert r.items == [] and r.end == "confirmed" and srv.calls == [(0, 100)]


def test_suspect_is_the_default():
    srv = Server({})
    assert page_all(srv).end == "not_confirmed"


def test_none_is_null_too():
    srv = Server({0: [el(1)]}, null=None)
    assert page_all(srv, end_policy="trusted").end == "confirmed"


def test_an_empty_page_during_probing_resumes_normal_paging():
    # null at 0, then [] at 100: the server has rows there, so the probe count resets.
    srv = Server({100: [], 500: [el(9)]})
    r = page_all(srv, end_policy="suspect")
    assert guids(r) == ["g9"]


def test_repeated_rows_stop_as_stalled():
    srv = Server({0: [el(1), el(2)], 100: [el(1), el(2)]})
    r = page_all(srv, end_policy="trusted")
    assert guids(r) == ["g1", "g2"] and r.end == "stalled" and "position 100" in r.note


def test_duplicates_across_pages_are_dropped_but_not_a_stall():
    srv = Server({0: [el(1), el(2)], 100: [el(2), el(3)]})
    r = page_all(srv, end_policy="trusted")
    assert guids(r) == ["g1", "g2", "g3"] and r.end == "confirmed"


def test_max_pages_caps_the_read():
    srv = Server({i * 10: [el(i)] for i in range(50)})
    r = page_all(srv, fetch_page_size=10, max_pages=5, end_policy="trusted")
    assert len(r.items) == 5 and r.end == "capped" and "may be more" in r.note
    assert len(srv.calls) == 5


# ── the Architect's changes ──

def test_want_is_separate_from_the_fetch_page_size():
    # ▲1: ask for 3 rows, fetch 100 at a time; the result is cut to 3 and says there may be more.
    srv = Server({0: [el(i) for i in range(100)]})
    r = page_all(srv, want=3, end_policy="trusted")
    assert guids(r) == ["g0", "g1", "g2"]
    assert r.end == "capped" and srv.calls == [(0, 100)]
    assert r.count_text() == "at least 3"


def test_want_collected_across_filtered_pages():
    srv = Server({0: [], 100: [el(1)], 200: [], 300: [el(2), el(3)]})
    r = page_all(srv, want=2, end_policy="trusted")
    assert guids(r) == ["g1", "g2"] and r.end == "capped"


def test_fewer_than_want_then_null_is_confirmed():
    srv = Server({0: [el(1)]})
    r = page_all(srv, want=25, end_policy="trusted")
    assert guids(r) == ["g1"] and r.end == "confirmed"


def test_the_draft_terms_case_fits_at_fetch_size_100():
    # 1,100 filtered positions before the matches: 11 empty pages at 100 is under the 2,000-row cap.
    pages = {s: [] for s in range(0, 1100, 100)}
    pages[1100] = [el(i) for i in range(79)]
    pages[1200] = [el(i) for i in range(79, 86)]
    r = page_all(Server(pages), end_policy="trusted")
    assert len(r.items) == 86 and r.end == "confirmed"


def test_the_empty_run_cap_is_in_rows_not_pages():
    # ▲2: the same 2,000 filtered positions stop the read whether fetched 100 or 25 at a time.
    for size in (100, 25):
        pages = {s: [] for s in range(0, 5000, size)}
        srv = Server(pages)
        r = page_all(srv, fetch_page_size=size, max_empty_rows=2000, end_policy="trusted")
        assert r.end == "not_confirmed" and r.positions_read == 2000, size
        assert "2000 consecutive positions" in r.note


def test_rows_reset_the_empty_run():
    pages = {s: [] for s in range(0, 5000, 100)}
    pages[1500] = [el(1)]
    r = page_all(Server(pages), max_empty_rows=2000, end_policy="trusted")
    assert guids(r) == ["g1"] and r.end == "not_confirmed" and r.positions_read == 3600


def test_fetch_errors_propagate():
    def boom(start, size):
        raise RuntimeError("read failed")

    with pytest.raises(RuntimeError):
        page_all(boom)


@pytest.mark.parametrize("kwargs", [dict(end_policy="maybe"), dict(fetch_page_size=0), dict(want=0),
                                    dict(probe_pages=0), dict(max_empty_rows=0), dict(max_pages=True)])
def test_bad_arguments_are_refused(kwargs):
    with pytest.raises(ValueError):
        page_all(Server({}), **kwargs)


def test_async_driver_matches_the_sync_one():
    pages = {0: [], 100: [el(1)], 300: [el(2)]}
    srv = Server(pages)

    async def fetch(start, size):
        return srv(start, size)

    r = asyncio.run(async_page_all(fetch, end_policy="suspect"))
    assert isinstance(r, PageResult)
    assert guids(r) == ["g1", "g2"] and r.end == "not_confirmed"
    sync = page_all(Server(pages), end_policy="suspect")
    assert (guids(sync), sync.end, sync.pages_read) == (guids(r), r.end, r.pages_read)


def test_relationship_headers_and_unkeyed_items_dedupe():
    rel = {"relationshipHeader": {"guid": "r1"}}
    srv = Server({0: [rel, "loose"], 100: [dict(rel)]})
    r = page_all(srv, end_policy="trusted")
    assert r.items == [rel, "loose"] and r.end == "stalled"


# ── rows decoded afresh from JSON on every page (read-back of 82ca106a) ──

import json  # noqa: E402

from pyegeria.core.paging import default_key  # noqa: E402

EGERIA6_ELEMENTS = [{"elementHeader": {"guid": "g1", "type": {"typeName": "Topic"}},
                     "properties": {"displayName": "openlineage.events"}},
                    {"elementHeader": {"guid": "g2", "type": {"typeName": "Topic"}},
                     "properties": {"displayName": "openlineage.events"}}]
METADATA_EXPERT_ELEMENTS = [{"class": "OpenMetadataElement", "elementGUID": "g1",
                             "elementProperties": {"displayName": "openlineage.events"}},
                            {"class": "OpenMetadataElement", "elementGUID": "g2",
                             "elementProperties": {"displayName": "openlineage.events"}}]
METADATA_EXPERT_RELATIONSHIPS = [{"class": "OpenMetadataRelationship", "relationshipGUID": "r1"},
                                 {"class": "OpenMetadataRelationship", "relationshipGUID": "r2"}]


class JsonServer(Server):
    """Like Server, but every page is a fresh json.loads of its text, as from the wire."""

    def __call__(self, start, size):
        page = super().__call__(start, size)
        return json.loads(json.dumps(page)) if isinstance(page, list) else page


@pytest.mark.parametrize("rows", [EGERIA6_ELEMENTS, METADATA_EXPERT_ELEMENTS, METADATA_EXPERT_RELATIONSHIPS],
                         ids=["egeria6", "metadata-expert-elements", "metadata-expert-relationships"])
def test_the_same_rows_decoded_twice_stall(rows):
    # The Architect's repro: the same 2 rows at startFrom 0 and 2, then null (trusted).
    r = page_all(JsonServer({0: rows, 2: rows}), fetch_page_size=2, end_policy="trusted")
    assert len(r.items) == 2 and r.end == "stalled"


@pytest.mark.parametrize("rows", [EGERIA6_ELEMENTS, METADATA_EXPERT_ELEMENTS, METADATA_EXPERT_RELATIONSHIPS],
                         ids=["egeria6", "metadata-expert-elements", "metadata-expert-relationships"])
def test_overlapping_decoded_pages_dedupe(rows):
    r = page_all(JsonServer({0: rows, 2: rows[1:]}), fetch_page_size=2, end_policy="trusted")
    assert len(r.items) == 2 and r.end == "stalled"
    r = page_all(JsonServer({0: rows[:1], 2: rows}), fetch_page_size=2, end_policy="trusted")
    assert len(r.items) == 2 and r.end == "confirmed"


def test_default_key_reads_every_guid_shape():
    assert default_key(EGERIA6_ELEMENTS[0]) == "g1"
    assert default_key(METADATA_EXPERT_ELEMENTS[1]) == "g2"
    assert default_key(METADATA_EXPERT_RELATIONSHIPS[0]) == "r1"
    assert default_key({"relationshipHeader": {"guid": "r9"}}) == "r9"
    assert default_key({"guid": "g9"}) == "g9"


def test_rows_without_a_guid_are_keyed_by_content_not_identity():
    a, b = {"displayName": "x"}, {"displayName": "x"}
    assert a is not b and default_key(a) == default_key(b)
    assert default_key({"displayName": "y"}) != default_key(a)
    assert default_key({"elementGUID": ""}) != default_key({"elementGUID": "", "n": 1})   # empty guid: content
