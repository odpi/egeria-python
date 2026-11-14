"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   My Profile follows Egeria's paging contract (fix/myegeria-paging-exists).

   A list from Egeria is one page of matches; [] is a page filtered empty (keep paging); only null means no
   more. So:
   - a write guard (get-or-create, add-if-missing) creates only when Egeria confirmed the item is absent,
     and on "can't tell" refuses with words and writes nothing;
   - a display reads every page, and says "none" or a plain count only after a confirmed end.

   The fakes below page like Egeria: ``paged(p0, p1, ...)`` returns page i for start_from = i * page_size and
   null ("No elements found") past the last; ``FILTERED`` returns [] forever (every page filtered empty, so the
   end is never reached).
"""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pyegeria import PyegeriaException
from pyegeria.core._exceptions import PyegeriaNotFoundException

import paging_support
from paging_support import (PagedRows, is_complete, none_words, report_empty_cells, report_empty_words)

NULL = "No elements found"


def paged(*pages):
    """A fake pyegeria list method: page i at start_from = i * page_size, null after the last."""
    def fetch(*args, start_from=0, page_size=100, **kwargs):
        index = start_from // page_size
        return pages[index] if index < len(pages) else NULL
    return MagicMock(side_effect=fetch)


def apaged(*pages):
    """``paged`` as an AsyncMock."""
    sync = paged(*pages)
    return AsyncMock(side_effect=lambda *a, **k: sync(*a, **k))


FILTERED = lambda *args, **kwargs: []   # noqa: E731 -- every page filtered empty: the end is never confirmed


def _el(guid, qualified_name="", name="", type_name="Asset", **props):
    return {"elementHeader": {"guid": guid, "type": {"typeName": type_name}},
            "properties": {"qualifiedName": qualified_name or f"{type_name}::{guid}",
                           "displayName": name or guid, **props}}


class _App:
    """The parts of the Textual app the mixins use."""
    view_server = "qs-view-server"
    platform_url = "https://127.0.0.1:9443"
    user_name = "garygeeke"
    user_password = "secret"
    user_GUID = "profile-guid"

    def __init__(self):
        self.notices = []
        self.pushed = []

    def log(self, *args, **kwargs):
        pass

    def notify(self, message, **kwargs):
        self.notices.append((str(message), kwargs.get("severity")))

    def push_screen(self, screen, callback=None):
        self.pushed.append(screen)

    def said(self, text):
        return any(text in message for message, _ in self.notices)


# ── paging_support words ────────────────────────────────────────────────────────────────────────────────────

def test_none_words_only_say_none_on_a_confirmed_end():
    assert none_words("bookmarks", True) == "No bookmarks found"
    unconfirmed = none_words("bookmarks", False, matching="sales")
    assert unconfirmed.startswith("No bookmarks found matching sales in what Egeria returned")
    assert "didn't confirm there are no more" in unconfirmed


def test_report_empty_cells_tells_failure_none_and_unconfirmed_apart():
    failed = report_empty_cells("glossaries", ["No Data", "Returned by Egeria"])   # the handlers' error sentinel
    confirmed = report_empty_cells("glossaries", {"kind": "empty", "end": "confirmed"})
    unconfirmed = report_empty_cells("glossaries", {"kind": "empty", "end": "not_confirmed",
                                                    "notes": ["nothing in the first 500 positions"]})
    assert failed[0] == "Couldn't retrieve glossaries from Egeria"
    assert confirmed == ("No glossaries found", "Egeria confirmed there are none")
    assert unconfirmed == ("No glossaries found in what Egeria returned", "nothing in the first 500 positions")
    assert report_empty_words("terms", {"kind": "empty"}).endswith("didn't confirm there are no more")  # no end


def test_paged_rows_is_a_plain_list_with_an_end():
    rows = PagedRows([1, 2], complete=False, note="Showing at least 2")
    assert rows == [1, 2] and not is_complete(rows) and not rows.reached_end and is_complete([])
    assert paging_support.count_text(rows) == "at least 2" and paging_support.count_text([1]) == "1"


def test_paged_rows_levels_from_a_read():
    from pyegeria.core.paging import PageResult
    confirmed = PageResult(items=[1], end="confirmed", end_reason="trusted_null")
    reached = PageResult(items=[1], end="not_confirmed", end_reason="null_then_empty_probes")
    capped = PageResult(items=[1], end="capped", note="there may be more", end_reason="max_pages")
    null_not_end = PageResult(items=[1], end="not_confirmed", end_reason="null_then_empty_probes", null_not_end=True)
    assert paging_support.paged_rows([1], confirmed, "x").complete
    r = paging_support.paged_rows([1], reached, "x")
    assert r.reached_end and not r.complete and r.note is None
    for read in (capped, null_not_end):
        r = paging_support.paged_rows([1], read, "things")
        assert not r.reached_end and r.note.startswith("Showing at least 1 things")


# ── bookmarks: get-or-create the collection, add-if-missing the member ─────────────────────────────────────

from bookmarks_handler import BookmarksMixin, bookmarks_qualified_name  # noqa: E402

BM_QN = bookmarks_qualified_name("garygeeke")
BM_COLL = _el("bm-guid", BM_QN, type_name="Collection")


class BookmarksApp(_App, BookmarksMixin):
    pass


@pytest.fixture
def bm_client():
    with patch("bookmarks_handler.Egeria") as egeria:
        yield egeria.return_value


class TestBookmarksGuards:
    def test_collection_on_a_later_page_is_found_not_recreated(self, bm_client):
        # page 0 filtered empty: the old code read it as "no collection" and created a second one
        bm_client.get_collections_by_name = paged([], [BM_COLL])
        bm_client.get_collection_members = paged([])
        assert BookmarksApp().add_my_bookmark("asset-1") is True
        bm_client.create_collection.assert_not_called()
        bm_client.add_to_collection.assert_called_once_with(collection_guid="bm-guid", element_guid="asset-1")

    def test_absent_collection_is_created_once(self, bm_client):
        bm_client.get_collections_by_name = paged()            # null, then empty probes: confirmed absent
        bm_client.create_collection.return_value = "new-bm-guid"
        bm_client.get_collection_members = paged()
        assert BookmarksApp().add_my_bookmark("asset-1") is True
        bm_client.create_collection.assert_called_once()
        bm_client.add_to_collection.assert_called_once_with(collection_guid="new-bm-guid", element_guid="asset-1")

    def test_unknown_collection_refuses_and_writes_nothing(self, bm_client):
        bm_client.get_collections_by_name = MagicMock(side_effect=FILTERED)
        app = BookmarksApp()
        assert app.add_my_bookmark("asset-1") is False
        bm_client.create_collection.assert_not_called()
        bm_client.add_to_collection.assert_not_called()
        assert app.said("Couldn't confirm whether Egeria already holds your bookmarks collection")
        assert app.said("Nothing was created")

    def test_member_on_a_later_page_is_already_bookmarked(self, bm_client):
        bm_client.get_collections_by_name = paged([BM_COLL])
        bm_client.get_collection_members = paged([_el("other")], [], [_el("asset-1")])
        app = BookmarksApp()
        assert app.add_my_bookmark("asset-1") is False
        bm_client.add_to_collection.assert_not_called()
        assert app.said("already bookmarked")

    def test_unknown_membership_refuses_and_adds_nothing(self, bm_client):
        bm_client.get_collections_by_name = paged([BM_COLL])
        bm_client.get_collection_members = MagicMock(side_effect=FILTERED)
        app = BookmarksApp()
        assert app.add_my_bookmark("asset-1") is False
        bm_client.add_to_collection.assert_not_called()
        assert app.said("Couldn't confirm whether Egeria already holds a bookmark for asset-1")

    def test_delete_on_unknown_collection_removes_nothing(self, bm_client):
        bm_client.get_collections_by_name = MagicMock(side_effect=FILTERED)
        app = BookmarksApp()
        assert app.delete_my_bookmark("asset-1") is False
        bm_client.remove_from_collection.assert_not_called()
        assert not app.said("You have no bookmarks")


class TestBookmarksDisplay:
    def test_members_after_a_filtered_page_are_all_listed(self, bm_client):
        bm_client.get_collections_by_name = paged([BM_COLL])
        bm_client.get_collection_members = paged([_el("a1", name="One")], [], [_el("a2", name="Two")])
        rows = BookmarksApp().list_my_bookmarks()
        # reached the end (null, then empty probes): shown as the list; not "confirmed" on this suspect path
        assert [r[2] for r in rows] == ["a1", "a2"] and rows.reached_end and rows.note is None
        assert not rows.complete

    def test_unconfirmed_members_say_at_least(self, bm_client):
        rows_then_filtered = paged([_el("a1")], *([[]] * 30))   # one row, then filtered pages to the run cap
        bm_client.get_collections_by_name = paged([BM_COLL])
        bm_client.get_collection_members = rows_then_filtered
        app = BookmarksApp()
        rows = app.list_my_bookmarks()
        assert rows == [("a1", "Asset", "a1")] and not rows.complete
        assert app.said("Showing at least 1 bookmarks")

    def test_unknown_collection_is_not_shown_as_no_bookmarks(self, bm_client):
        bm_client.get_collections_by_name = MagicMock(side_effect=FILTERED)
        rows = BookmarksApp().list_my_bookmarks()
        assert rows == [] and not is_complete(rows)

    def test_absent_collection_is_none_in_what_egeria_returned(self, bm_client):
        # absent (the read reached the end) is enough to create, but "none" as words needs a confirmed end,
        # which get_collections_by_name (a suspect path) never gives
        bm_client.get_collections_by_name = paged()
        rows = BookmarksApp().list_my_bookmarks()
        assert rows == [] and rows.reached_end and not is_complete(rows)


class TestRowGuid:
    """bookmarks_handler.get_row_guid: a qualified name resolves through the exact unique-name read, and a
    failed lookup is said as such, never as "the row doesn't identify an element"."""

    @pytest.fixture
    def qn_row(self):
        with patch("bookmarks_handler.row_identity", return_value=("", "Glossary::Sales")):
            yield

    def test_found(self, bm_client, qn_row):
        bm_client.get_element_guid_by_unique_name.return_value = "glossary-guid"
        assert BookmarksApp().get_row_guid(object(), "row") == "glossary-guid"

    def test_not_found_is_said(self, bm_client, qn_row):
        bm_client.get_element_guid_by_unique_name.side_effect = PyegeriaNotFoundException.__new__(
            PyegeriaNotFoundException)
        app = BookmarksApp()
        assert app.bookmark_table_row(object(), "row") is False
        assert app.said("Egeria holds no element with the qualified name Glossary::Sales")
        assert not app.said("doesn't identify")

    def test_error_is_not_not_found(self, bm_client, qn_row):
        bm_client.get_element_guid_by_unique_name.side_effect = PyegeriaException.__new__(PyegeriaException)
        app = BookmarksApp()
        assert app.bookmark_table_row(object(), "row") is False
        assert app.said("Couldn't look up the element Glossary::Sales")
        bm_client.add_to_collection.assert_not_called()


# ── communities: the blog log, a new community, the search ─────────────────────────────────────────────────

from community_handler import BLOG_LOG_QN, CommunitiesMixin  # noqa: E402

BLOG_QN = BLOG_LOG_QN.format(community_guid="comm-guid")


class CommunityApp(_App, CommunitiesMixin):
    pass


@pytest.fixture
def cm_client():
    with patch("community_handler.Egeria") as egeria:
        client = egeria.return_value
        client.make_feedback_qn.return_value = "BlogEntry::qn"
        yield client


class TestCommunityGuards:
    def test_blog_log_on_a_later_page_is_used(self, cm_client):
        cm_client.get_attached_note_logs = paged([], [_el("log-guid", BLOG_QN, type_name="NoteLog")])
        assert CommunityApp().add_community_blog_post("comm-guid", "Data", "Hi", "text") is True
        cm_client.create_note_log.assert_not_called()
        cm_client.create_note.assert_called_once()
        assert cm_client.create_note.call_args.args[0] == "log-guid"

    def test_absent_blog_log_is_created(self, cm_client):
        cm_client.get_attached_note_logs = paged([_el("other-log", "NoteLog::other", type_name="NoteLog")])
        cm_client.create_note_log.return_value = "new-log"
        assert CommunityApp().add_community_blog_post("comm-guid", "Data", "Hi", "text") is True
        cm_client.create_note_log.assert_called_once()
        assert cm_client.create_note.call_args.args[0] == "new-log"

    def test_unknown_blog_log_refuses_and_posts_nothing(self, cm_client):
        cm_client.get_attached_note_logs = MagicMock(side_effect=FILTERED)
        app = CommunityApp()
        assert app.add_community_blog_post("comm-guid", "Data", "Hi", "text") is False
        cm_client.create_note_log.assert_not_called()
        cm_client.create_note.assert_not_called()
        assert app.said("Couldn't confirm whether Egeria already holds a blog for Data")

    @pytest.mark.parametrize("pages, created", [((), True), (([], [_el("c", "Community::Data")]), False)])
    def test_create_community_found_or_absent(self, cm_client, pages, created):
        cm_client.__create_qualified_name__ = MagicMock(return_value="Community::Data")
        cm_client.get_communities_by_name = paged(*pages)
        cm_client.create_community.return_value = "new-comm"
        app = CommunityApp()
        result = app.create_community("Data", "about data", assignment_type="")
        assert (result == "new-comm") is created
        assert cm_client.create_community.called is created
        if not created:
            assert app.said("already exists")

    def test_create_community_unknown_refuses(self, cm_client):
        cm_client.__create_qualified_name__ = MagicMock(return_value="Community::Data")
        cm_client.get_communities_by_name = MagicMock(side_effect=FILTERED)
        app = CommunityApp()
        assert app.create_community("Data", "about data") is None
        cm_client.create_community.assert_not_called()
        cm_client.link_assignment_scope.assert_not_called()
        assert app.said("Couldn't confirm whether Egeria already holds a community called Data")


class TestCommunityDisplay:
    def test_search_reads_past_a_filtered_page(self, cm_client):
        cm_client.find_communities = paged([], [_el("c1", "Community::A", "A")])
        rows = CommunityApp().search_communities("*")
        assert [r[3] for r in rows] == ["c1"] and rows.reached_end and rows.note is None

    def test_unconfirmed_search_is_not_none(self, cm_client):
        cm_client.find_communities = MagicMock(side_effect=FILTERED)
        rows = CommunityApp().search_communities("x")
        assert rows == [] and not rows.complete
        assert none_words("other communities", rows.complete, "x").endswith("didn't confirm there are no more")

    def test_blog_posts_unconfirmed_say_so(self, cm_client):
        cm_client.get_attached_note_logs = paged([_el("log", BLOG_QN, type_name="NoteLog")])
        cm_client.get_notes_for_note_log = MagicMock(side_effect=FILTERED)
        app = CommunityApp()
        posts = app.get_community_blog_posts("comm-guid")
        assert posts == [] and not posts.complete
        assert app.said("newer posts may be missing")

    def test_comments_across_pages(self, cm_client):
        cm_client.get_attached_comments = paged([_el("k1")], [], [_el("k2")])
        rows = CommunityApp().get_community_comments("comm-guid")
        assert sorted(r[4] for r in rows) == ["k1", "k2"] and rows.reached_end


# ── feedback log (async) ───────────────────────────────────────────────────────────────────────────────────

from feedback_handler import FEEDBACK_LOG_OWNER, FEEDBACK_LOG_QN, FeedbackMixin  # noqa: E402

LOG = _el("fb-log", FEEDBACK_LOG_QN, type_name="NoteLog")


class FeedbackApp(_App, FeedbackMixin):
    user_name = FEEDBACK_LOG_OWNER


def _fb_client(note_logs):
    client = MagicMock()
    client._async_get_note_logs_by_name = note_logs
    client._async_create_note_log = AsyncMock(return_value="new-log")
    client._async_create_note = AsyncMock(return_value="note-guid")
    return client


class TestFeedbackLog:
    def test_found_on_a_later_page(self):
        client = _fb_client(apaged([], [LOG]))
        assert asyncio.run(FeedbackApp()._get_or_create_feedback_log(client)) == "fb-log"
        client._async_create_note_log.assert_not_called()

    def test_absent_is_created(self):
        client = _fb_client(apaged())
        assert asyncio.run(FeedbackApp()._get_or_create_feedback_log(client)) == "new-log"
        client._async_create_note_log.assert_called_once()

    def test_unknown_refuses_and_saves_nothing(self):
        client = _fb_client(AsyncMock(side_effect=FILTERED))
        app = FeedbackApp()
        with patch.object(FeedbackApp, "_feedback_client", return_value=client):
            asyncio.run(app.feedback_callback({"category": "Bug", "screen": "S", "text": "t"}))
        client._async_create_note_log.assert_not_called()
        client._async_create_note.assert_not_called()
        assert app.said("Couldn't confirm whether Egeria already holds the feedback log")
        assert app.said("not saved")

    def test_entries_unconfirmed(self):
        client = _fb_client(apaged([LOG]))
        client._async_get_notes_for_note_log = AsyncMock(side_effect=FILTERED)
        entries = asyncio.run(FeedbackApp().get_feedback_entries(client))
        assert entries == [] and not entries.complete

    def test_entries_across_pages(self):
        client = _fb_client(apaged([LOG]))
        client._async_get_notes_for_note_log = apaged([_el("n1")], [], [_el("n2")])
        entries = asyncio.run(FeedbackApp().get_feedback_entries(client))
        assert len(entries) == 2 and entries.reached_end


# ── network: add a peer, search people ─────────────────────────────────────────────────────────────────────

from network_handler import NetworkMixin  # noqa: E402


class NetworkApp(_App, NetworkMixin):
    pass


@pytest.fixture
def nw_client():
    with patch("network_handler.Egeria") as egeria:
        yield egeria.return_value


def _person(guid):
    return {"elementHeader": {"guid": guid}, "properties": {"class": "PersonProperties", "qualifiedName": guid}}


class TestNetwork:
    def test_already_a_peer_on_a_later_page_is_not_linked_again(self, nw_client):
        nw_client.get_related_elements = paged([_person("p1")], [], [_person("p2")])
        app = NetworkApp()
        assert app.link_peer("p2") is False
        nw_client.link_peer_person.assert_not_called()
        assert app.said("already in your network")

    def test_absent_peer_is_linked(self, nw_client):
        nw_client.get_related_elements = paged([_person("p1")])
        assert NetworkApp().link_peer("p2") is True
        nw_client.link_peer_person.assert_called_once()

    def test_unknown_refuses(self, nw_client):
        nw_client.get_related_elements = MagicMock(side_effect=FILTERED)
        app = NetworkApp()
        assert app.link_peer("p2") is False
        nw_client.link_peer_person.assert_not_called()
        assert app.said("Couldn't confirm whether Egeria already holds a link to that person")

    def test_peers_body_paged_in_the_call(self, nw_client):
        nw_client.get_related_elements = paged([_person("p1")], [], [_person("p2")])
        rows = NetworkApp().list_my_peers()
        assert [r[4] for r in rows] == ["p1", "p2"] and rows.reached_end
        first = nw_client.get_related_elements.call_args_list[0].kwargs
        assert first["body"]["includeOnlyRelationships"] == ["ContactThrough"] and first["page_size"] == 100

    def test_search_people_reads_past_ten(self, nw_client):
        page0 = [{"GUID": f"g{i}", "Display Name": f"P{i}", "Qualified Name": f"q{i}"} for i in range(25)]
        nw_client.find_actor_profiles = paged(page0, [], [{"GUID": "late", "Display Name": "Late"}])
        rows = NetworkApp().search_people("P")
        assert len(rows) == 26 and rows.reached_end   # the old read stopped at page_size=10
        assert all(c.kwargs["page_size"] == 25 for c in nw_client.find_actor_profiles.call_args_list)

    def test_search_people_single_dict(self, nw_client):
        nw_client.find_actor_profiles = paged({"GUID": "solo", "Display Name": "Solo"})
        assert [r[1] for r in NetworkApp().search_people("Solo")] == ["solo"]


# ── Shop for Data: the data-set lookup that used page_size=1 ──────────────────────────────────────────────

from shop_for_data_handler import DATA_SET_PAGE, data_set_absence_words, find_data_set  # noqa: E402


class TestDataSetLookup:
    def test_found_after_a_filtered_page_and_never_page_size_1(self):
        client = MagicMock()
        client.find_tabular_data_sets = paged([], [{"GUID": "ds-1", "Qualified Name": "DS"}])
        found = find_data_set(client, "DigitalProduct::X")
        assert found.found and found.matches[0]["GUID"] == "ds-1"
        assert {c.kwargs["page_size"] for c in client.find_tabular_data_sets.call_args_list} == {DATA_SET_PAGE}

    def test_absent_and_unknown_words(self):
        absent = find_data_set(MagicMock(find_tabular_data_sets=paged()), "X")
        unknown = find_data_set(MagicMock(find_tabular_data_sets=MagicMock(side_effect=FILTERED)), "X")
        assert absent.answer == "absent" and unknown.answer == "unknown"
        assert data_set_absence_words(absent, "X") == "No metadata found for dataset X"
        assert "in what Egeria returned" in data_set_absence_words(unknown, "X")


# ── Search for a term: the executor's "mime" key ──────────────────────────────────────────────────────────

def test_search_for_term_reads_the_executors_mime_key():
    import SearchForTermScreen as screen_module
    fake = SimpleNamespace(view_server="v", platform_url="u", user="x", password="y")
    with patch.object(screen_module, "exec_report_spec",
                      return_value={"kind": "text", "mime": "text/markdown", "content": "# Sales"}):
        assert screen_module.SearchForTermScreen.search_for_the_term(fake, "Sales") == "# Sales"
    with patch.object(screen_module, "exec_report_spec", return_value={"kind": "empty", "end": "not_confirmed"}):
        words = screen_module.SearchForTermScreen.search_for_the_term(fake, "Sales")
        assert "in what Egeria returned" in words
    with patch.object(screen_module, "exec_report_spec", return_value={"kind": "empty", "end": "confirmed"}):
        assert screen_module.SearchForTermScreen.search_for_the_term(fake, "Sales") == \
            "# No glossary terms found matching Sales"


def test_display_max_pages_bounds_a_read():
    calls = MagicMock(side_effect=FILTERED)
    read = paging_support.read_all(calls, method="find_collections", max_pages=3)
    assert calls.call_count == 3 and not read.complete
