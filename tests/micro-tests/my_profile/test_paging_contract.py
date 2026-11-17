"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   My Profile follows Egeria's paging contract (fix/myegeria-paging-exists).

   A list from Egeria is one page of matches; [] is a page filtered empty (keep paging); only null means no
   more. So:
   - a write guard keyed on a qualified name asks Egeria's exact unique-name read: found -> reuse; Egeria's
     specific not-found -> create; anything else -> refuse, nothing written (read-back R2);
   - a write guard keyed on a GUID (membership, a Peer link) pages with exists: create only on absent,
     refuse on unknown;
   - a display reads every page, and shows a plain list, a plain count or "none" only after a CONFIRMED end;
     any other end, null_then_empty_probes included, says "at least" (read-back R1).

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
    assert paging_support.paged_rows([1], confirmed, "x").note is None
    for read in (reached, capped, null_not_end):   # R1: only a confirmed end drops "at least"
        r = paging_support.paged_rows([1], read, "things")
        assert not r.complete and r.note.startswith("Showing at least 1 things")
        assert r.reached_end is (read is reached)   # kept for the trace; write paths only


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


def _unique(element=None, error=None):
    """A fake get_element_by_unique_name: the element, Egeria's NO_ELEMENTS_FOUND, or an exception."""
    if error is not None:
        return MagicMock(side_effect=error)
    return MagicMock(return_value=element if element is not None else NULL)


def _not_found():
    return PyegeriaNotFoundException.__new__(PyegeriaNotFoundException)


def _failed():
    return PyegeriaException.__new__(PyegeriaException)


class TestUniqueNameRead:
    def test_answers(self):
        coll = _el("c", "Q", type_name="Collection")
        assert paging_support.by_unique_name(MagicMock(get_element_by_unique_name=_unique(coll)), "Q",
                                             "Collection").guid == "c"
        for unique, answer in ((_unique(), "absent"), (_unique(error=_not_found()), "absent"),
                               (_unique(error=_failed()), "unknown"), (_unique(error=TimeoutError()), "unknown"),
                               (_unique("garbage"), "unknown"),
                               (_unique(_el("x", "Q", type_name="Asset")), "unknown")):   # the wrong type
            assert paging_support.by_unique_name(MagicMock(get_element_by_unique_name=unique), "Q",
                                                 "Collection").answer == answer

    def test_never_pages(self):
        client = MagicMock(get_element_by_unique_name=_unique())
        paging_support.by_unique_name(client, "Q")
        client.get_element_by_unique_name.assert_called_once_with("Q")
        client.get_collections_by_name.assert_not_called()


class TestBookmarksGuards:
    def test_found_collection_is_reused(self, bm_client):
        bm_client.get_element_by_unique_name = _unique(BM_COLL)
        bm_client.get_collection_members = paged([])
        assert BookmarksApp().add_my_bookmark("asset-1") is True
        bm_client.get_element_by_unique_name.assert_called_once_with(BM_QN)
        bm_client.create_collection.assert_not_called()
        bm_client.add_to_collection.assert_called_once_with(collection_guid="bm-guid", element_guid="asset-1")

    @pytest.mark.parametrize("unique", [_unique(), _unique(error=_not_found())], ids=["no-elements", "not-found"])
    def test_not_found_collection_is_created_once(self, bm_client, unique):
        bm_client.get_element_by_unique_name = unique
        bm_client.create_collection.return_value = "new-bm-guid"
        bm_client.get_collection_members = paged()
        assert BookmarksApp().add_my_bookmark("asset-1") is True
        bm_client.create_collection.assert_called_once()
        bm_client.add_to_collection.assert_called_once_with(collection_guid="new-bm-guid", element_guid="asset-1")

    @pytest.mark.parametrize("unique", [_unique(error=_failed()), _unique("garbage"),
                                        _unique(_el("x", BM_QN, type_name="Asset"))],
                             ids=["error", "not-an-element", "wrong-type"])
    def test_any_other_answer_refuses_and_writes_nothing(self, bm_client, unique):
        bm_client.get_element_by_unique_name = unique
        app = BookmarksApp()
        assert app.add_my_bookmark("asset-1") is False
        bm_client.create_collection.assert_not_called()
        bm_client.add_to_collection.assert_not_called()
        assert app.said("Couldn't confirm whether Egeria already holds your bookmarks collection")
        assert app.said("Nothing was created")

    def test_member_on_a_later_page_is_already_bookmarked(self, bm_client):
        bm_client.get_element_by_unique_name = _unique(BM_COLL)
        bm_client.get_collection_members = paged([_el("other")], [], [_el("asset-1")])
        app = BookmarksApp()
        assert app.add_my_bookmark("asset-1") is False
        bm_client.add_to_collection.assert_not_called()
        assert app.said("already bookmarked")

    def test_unknown_membership_refuses_and_adds_nothing(self, bm_client):
        bm_client.get_element_by_unique_name = _unique(BM_COLL)
        bm_client.get_collection_members = MagicMock(side_effect=FILTERED)
        app = BookmarksApp()
        assert app.add_my_bookmark("asset-1") is False
        bm_client.add_to_collection.assert_not_called()
        assert app.said("Couldn't confirm whether Egeria already holds a bookmark for asset-1")

    def test_delete_on_unknown_collection_removes_nothing(self, bm_client):
        bm_client.get_element_by_unique_name = _unique(error=_failed())
        app = BookmarksApp()
        assert app.delete_my_bookmark("asset-1") is False
        bm_client.remove_from_collection.assert_not_called()
        assert not app.said("You have no bookmarks")


class TestBookmarksDisplay:
    def test_members_after_a_filtered_page_are_all_listed_but_at_least(self, bm_client):
        # R1: the read reached the end (null, then empty probes) on a suspect path: every row is listed, and
        # the words still say "at least" because Egeria didn't confirm the end
        bm_client.get_element_by_unique_name = _unique(BM_COLL)
        bm_client.get_collection_members = paged([_el("a1", name="One")], [], [_el("a2", name="Two")])
        app = BookmarksApp()
        rows = app.list_my_bookmarks()
        assert [r[2] for r in rows] == ["a1", "a2"] and rows.reached_end and not rows.complete
        assert rows.note.startswith("Showing at least 2 bookmarks") and app.said("Showing at least 2 bookmarks")

    def test_unconfirmed_members_say_at_least(self, bm_client):
        bm_client.get_element_by_unique_name = _unique(BM_COLL)
        bm_client.get_collection_members = paged([_el("a1")], *([[]] * 30))   # one row, then the run cap
        app = BookmarksApp()
        rows = app.list_my_bookmarks()
        assert rows == [("a1", "Asset", "a1")] and not rows.complete and not rows.reached_end
        assert app.said("Showing at least 1 bookmarks")

    def test_unknown_collection_is_not_shown_as_no_bookmarks(self, bm_client):
        bm_client.get_element_by_unique_name = _unique(error=_failed())
        app = BookmarksApp()
        assert app.list_my_bookmarks() is None   # the screen isn't shown with an empty list
        assert app.said("Couldn't confirm whether Egeria already holds your bookmarks collection")

    def test_not_found_collection_is_a_plain_none(self, bm_client):
        # Egeria's exact not-found is an answer, not a paged end: "You have no bookmarks yet" may be said
        bm_client.get_element_by_unique_name = _unique()
        rows = BookmarksApp().list_my_bookmarks()
        assert rows == [] and is_complete(rows)
        bm_client.get_collection_members.assert_not_called()


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
    def test_found_blog_log_is_used(self, cm_client):
        cm_client.get_element_by_unique_name = _unique(_el("log-guid", BLOG_QN, type_name="NoteLog"))
        assert CommunityApp().add_community_blog_post("comm-guid", "Data", "Hi", "text") is True
        cm_client.get_element_by_unique_name.assert_called_once_with(BLOG_QN)
        cm_client.create_note_log.assert_not_called()
        assert cm_client.create_note.call_args.args[0] == "log-guid"

    def test_not_found_blog_log_is_created(self, cm_client):
        cm_client.get_element_by_unique_name = _unique(error=_not_found())
        cm_client.create_note_log.return_value = "new-log"
        assert CommunityApp().add_community_blog_post("comm-guid", "Data", "Hi", "text") is True
        cm_client.create_note_log.assert_called_once()
        assert cm_client.create_note.call_args.args[0] == "new-log"

    def test_unknown_blog_log_refuses_and_posts_nothing(self, cm_client):
        cm_client.get_element_by_unique_name = _unique(error=_failed())
        app = CommunityApp()
        assert app.add_community_blog_post("comm-guid", "Data", "Hi", "text") is False
        cm_client.create_note_log.assert_not_called()
        cm_client.create_note.assert_not_called()
        assert app.said("Couldn't confirm whether Egeria already holds a blog for Data")

    @pytest.mark.parametrize("unique, created", [(_unique(), True), (_unique(error=_not_found()), True),
                                                 (_unique(_el("c", "Community::Data", type_name="Community")), False)],
                             ids=["no-elements", "not-found", "found"])
    def test_create_community_found_or_absent(self, cm_client, unique, created):
        cm_client.__create_qualified_name__ = MagicMock(return_value="Community::Data")
        cm_client.get_element_by_unique_name = unique
        cm_client.create_community.return_value = "new-comm"
        app = CommunityApp()
        result = app.create_community("Data", "about data", assignment_type="")
        assert (result == "new-comm") is created
        assert cm_client.create_community.called is created
        cm_client.get_communities_by_name.assert_not_called()   # no paged by-name search decides a create
        if not created:
            assert app.said("already exists")

    def test_create_community_unknown_refuses(self, cm_client):
        cm_client.__create_qualified_name__ = MagicMock(return_value="Community::Data")
        cm_client.get_element_by_unique_name = _unique(error=_failed())
        app = CommunityApp()
        assert app.create_community("Data", "about data") is None
        cm_client.create_community.assert_not_called()
        cm_client.link_assignment_scope.assert_not_called()
        assert app.said("Couldn't confirm whether Egeria already holds a community called Data")


class TestCommunityDisplay:
    def test_search_reads_past_a_filtered_page(self, cm_client):
        cm_client.find_communities = paged([], [_el("c1", "Community::A", "A")])
        rows = CommunityApp().search_communities("*")
        assert [r[3] for r in rows] == ["c1"] and rows.reached_end and rows.note.startswith("Showing at least 1")

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


def _fb_client(unique):
    client = MagicMock()
    client._async_get_element_by_unique_name = unique
    client._async_create_note_log = AsyncMock(return_value="new-log")
    client._async_create_note = AsyncMock(return_value="note-guid")
    return client


def _aunique(element=None, error=None):
    if error is not None:
        return AsyncMock(side_effect=error)
    return AsyncMock(return_value=element if element is not None else NULL)


class TestFeedbackLog:
    def test_found_is_reused(self):
        client = _fb_client(_aunique(LOG))
        assert asyncio.run(FeedbackApp()._get_or_create_feedback_log(client)) == "fb-log"
        client._async_get_element_by_unique_name.assert_awaited_once_with(FEEDBACK_LOG_QN)
        client._async_create_note_log.assert_not_called()

    @pytest.mark.parametrize("unique", [_aunique(), _aunique(error=_not_found())], ids=["no-elements", "not-found"])
    def test_not_found_is_created(self, unique):
        client = _fb_client(unique)
        assert asyncio.run(FeedbackApp()._get_or_create_feedback_log(client)) == "new-log"
        client._async_create_note_log.assert_called_once()

    def test_unknown_refuses_and_saves_nothing(self):
        client = _fb_client(_aunique(error=_failed()))
        app = FeedbackApp()
        with patch.object(FeedbackApp, "_feedback_client", return_value=client):
            asyncio.run(app.feedback_callback({"category": "Bug", "screen": "S", "text": "t"}))
        client._async_create_note_log.assert_not_called()
        client._async_create_note.assert_not_called()
        assert app.said("Couldn't confirm whether Egeria already holds the feedback log")
        assert app.said("not saved")

    def test_entries_unconfirmed(self):
        client = _fb_client(_aunique(LOG))
        client._async_get_notes_for_note_log = AsyncMock(side_effect=FILTERED)
        entries = asyncio.run(FeedbackApp().get_feedback_entries(client))
        assert entries == [] and not entries.complete

    def test_entries_across_pages_say_at_least(self):
        client = _fb_client(_aunique(LOG))
        client._async_get_notes_for_note_log = apaged([_el("n1")], [], [_el("n2")])
        entries = asyncio.run(FeedbackApp().get_feedback_entries(client))
        assert len(entries) == 2 and entries.reached_end and not entries.complete
        assert paging_support.count_text(entries) == "at least 2"


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


# ── R1: a confirmed end shows a plain list; R3: the by-name methods are classified centrally ─────────────────

def test_a_confirmed_read_shows_plain_n():
    trusted = paged([_el("a")], [_el("b")])   # find_authored_elements is a trusted path: its null is the end
    read = paging_support.read_all(lambda s, z: trusted(start_from=s, page_size=z), method="find_authored_elements")
    rows = paging_support.paged_rows(read.items, read, "things")
    assert rows.complete and rows.note is None and paging_support.count_text(rows) == "2"
    assert trusted.call_count == 3   # two pages, then the trusted null: no probes


def test_a_suspect_null_then_empty_probes_shows_at_least_n():
    fake = paged([_el("a")], [_el("b")])
    read = paging_support.read_all(lambda s, z: fake(start_from=s, page_size=z), method="get_collection_members")
    assert read.end_reason == "null_then_empty_probes" and read.reached_end
    rows = paging_support.paged_rows(read.items, read, "things")
    assert not rows.complete and paging_support.count_text(rows) == "at least 2"
    assert rows.note.startswith("Showing at least 2 things")


def test_by_name_methods_are_null_not_end_and_gated():
    from pyegeria.core import paging
    for name in ("get_collections_by_name", "_async_get_collections_by_name", "get_communities_by_name",
                 "_async_get_communities_by_name", "get_note_logs_by_name", "_async_get_note_logs_by_name"):
        assert name in paging.NULL_NOT_END_METHODS and name in paging.GATED_TRUSTED_METHODS, name
        assert paging._paging(name, promoted=False)["null_not_end"] is True
        assert paging._paging(name, promoted=True) == {"end_policy": "trusted"}
    # search-string (findEntities) and attached/related (getRelatedMetadataElements) reads stay plain suspect
    for name in ("find_communities", "find_actor_profiles", "find_tabular_data_sets", "get_notes_for_note_log",
                 "_async_get_notes_for_note_log", "get_attached_note_logs", "get_attached_comments",
                 "get_collection_members", "get_related_elements"):
        assert paging.paging_for(name) == {"end_policy": "suspect"}, name
