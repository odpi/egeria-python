"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Unit tests for the bookmarks mixin and screen (bookmarks are members of a
   personal collection).
"""

from unittest.mock import MagicMock, patch

import pytest
from textual.app import App
from textual.widgets import DataTable, Input, Button

from bookmarks_handler import BookmarksMixin, bookmarks_qualified_name, BOOKMARKS_DISPLAY_NAME
from MyBookMarksScreen import MyBookMarksScreen
from pyegeria import PyegeriaException

BOOKMARKS_QN = bookmarks_qualified_name("garygeeke")


def _element(guid, name, type_name="Asset", qualified_name=None):
    return {"elementHeader": {"guid": guid, "type": {"typeName": type_name}},
            "properties": {"displayName": name, "qualifiedName": qualified_name or f"{type_name}::{name}"}}


BOOKMARKS_COLLECTION = _element("bm-coll-guid", BOOKMARKS_DISPLAY_NAME, "Collection", BOOKMARKS_QN)


class DummyApp(BookmarksMixin):
    def __init__(self):
        self.view_server = "qs-view-server"
        self.platform_url = "https://127.0.0.1:9443"
        self.user_name = "garygeeke"
        self.user_password = "secret"
        self.user_GUID = "profile-guid"
        self.notices = []
        self.pushed = []

    def log(self, *args, **kwargs):
        pass

    def notify(self, message, **kwargs):
        self.notices.append((message, kwargs.get("severity")))

    def push_screen(self, screen, callback=None):
        self.pushed.append((screen, callback))


@pytest.fixture
def client():
    with patch("bookmarks_handler.Egeria") as mock_egeria:
        yield mock_egeria.return_value


class TestBookmarksMixin:
    def test_list_without_collection_is_empty(self, client):
        client.get_collections_by_name.return_value = "No elements found"
        assert DummyApp().list_my_bookmarks() == []
        client.get_collection_members.assert_not_called()
        client.close_session.assert_called_once()

    def test_list_returns_member_rows(self, client):
        client.get_collections_by_name.return_value = [BOOKMARKS_COLLECTION]
        # Members may come back wrapped in relatedElement
        client.get_collection_members.return_value = [
            _element("asset-1", "Sales Data", "DataSet"),
            {"relatedElement": _element("asset-2", "Churn Model", "Asset")},
        ]
        rows = DummyApp().list_my_bookmarks()
        client.get_collection_members.assert_called_once_with(collection_guid="bm-coll-guid", output_format="JSON",
                                                               graph_query_depth=0)
        assert rows == [("Sales Data", "DataSet", "asset-1"), ("Churn Model", "Asset", "asset-2")]

    def test_list_ignores_same_name_collection_with_other_qualified_name(self, client):
        client.get_collections_by_name.return_value = [
            _element("other-guid", BOOKMARKS_DISPLAY_NAME, "Collection", "Bookmarks::erinoverview")]
        assert DummyApp().list_my_bookmarks() == []

    def test_list_error_returns_none(self, client):
        client.get_collections_by_name.side_effect = PyegeriaException("boom")
        app = DummyApp()
        assert app.list_my_bookmarks() is None
        assert app.notices[-1][1] == "error"

    def test_add_creates_collection_first_time(self, client):
        client.get_collections_by_name.return_value = []
        client.create_collection.return_value = "new-coll-guid"
        assert DummyApp().add_my_bookmark("asset-1") is True
        body = client.create_collection.call_args.kwargs["body"]
        assert body["properties"]["qualifiedName"] == BOOKMARKS_QN == "Bookmarks::garygeeke"
        # Anchored to, and linked from, the user's profile so get_my_resources() finds it
        assert body["anchorGUID"] == body["parentGUID"] == "profile-guid"
        assert body["isOwnAnchor"] is False
        assert body["parentRelationshipTypeName"] == "ResourceList"
        assert body["parentRelationshipProperties"]["resourceUse"] == "Bookmarks"
        client.add_to_collection.assert_called_once_with(collection_guid="new-coll-guid", element_guid="asset-1")

    def test_add_looks_up_profile_guid_when_not_known(self, client):
        client.get_collections_by_name.return_value = []
        client.get_my_profile.return_value = [{"elementHeader": {"guid": "looked-up-profile"}, "properties": {}}]
        app = DummyApp()
        app.user_GUID = ""
        assert app.add_my_bookmark("asset-1") is True
        assert client.create_collection.call_args.kwargs["body"]["parentGUID"] == "looked-up-profile"

    def test_add_already_bookmarked_is_refused(self, client):
        client.get_collections_by_name.return_value = [BOOKMARKS_COLLECTION]
        client.get_collection_members.return_value = [_element("asset-1", "Sales Data", "DataSet")]
        app = DummyApp()
        assert app.add_my_bookmark("asset-1") is False
        client.add_to_collection.assert_not_called()
        assert app.notices[-1][1] == "warning"

    def test_add_reuses_existing_collection(self, client):
        client.get_collections_by_name.return_value = [BOOKMARKS_COLLECTION]
        assert DummyApp().add_my_bookmark("asset-1") is True
        client.create_collection.assert_not_called()
        client.add_to_collection.assert_called_once_with(collection_guid="bm-coll-guid", element_guid="asset-1")

    def test_add_failure_returns_false(self, client):
        client.get_collections_by_name.return_value = [BOOKMARKS_COLLECTION]
        client.add_to_collection.side_effect = PyegeriaException("bad guid")
        assert DummyApp().add_my_bookmark("nope") is False
        client.close_session.assert_called_once()

    def test_delete_removes_member(self, client):
        client.get_collections_by_name.return_value = [BOOKMARKS_COLLECTION]
        assert DummyApp().delete_my_bookmark("asset-1") is True
        client.remove_from_collection.assert_called_once_with(collection_guid="bm-coll-guid", element_guid="asset-1")

    def test_delete_without_collection(self, client):
        client.get_collections_by_name.return_value = []
        assert DummyApp().delete_my_bookmark("asset-1") is False
        client.remove_from_collection.assert_not_called()

    def test_show_pushes_screen(self, client):
        client.get_collections_by_name.return_value = []
        app = DummyApp()
        app.show_my_bookmarks()
        screen, callback = app.pushed[0]
        assert isinstance(screen, MyBookMarksScreen)
        assert callback == app.my_bookmarks_callback

    def test_show_passes_target_guid_to_screen(self, client):
        client.get_collections_by_name.return_value = []
        app = DummyApp()
        app.show_my_bookmarks(target_guid="asset-7")
        assert app.pushed[0][0].target_guid == "asset-7"


class BookmarksHostApp(App):
    """Host app standing in for MyProfileApp's bookmark methods."""

    def __init__(self, rows):
        super().__init__()
        self.rows = list(rows)
        self.target_guid = None
        self.add_my_bookmark = MagicMock(side_effect=self._add)
        self.delete_my_bookmark = MagicMock(side_effect=self._delete)
        self.dismissed = None

    def _add(self, guid):
        self.rows.append(("New", "Asset", guid))
        return True

    def _delete(self, guid):
        self.rows = [r for r in self.rows if r[2] != guid]
        return True

    def list_my_bookmarks(self):
        return list(self.rows)

    async def on_mount(self):
        self.screen_under_test = MyBookMarksScreen(list(self.rows), target_guid=self.target_guid)
        await self.push_screen(self.screen_under_test, callback=lambda r: setattr(self, "dismissed", r))


class TestMyBookMarksScreen:
    @pytest.mark.asyncio
    async def test_lists_bookmarks(self):
        app = BookmarksHostApp([("Sales Data", "DataSet", "asset-1")])
        async with app.run_test() as pilot:
            table = app.screen_under_test.query_one("#my_bookmark_table", DataTable)
            assert table.row_count == 1
            assert table.get_row_at(0) == ["Sales Data", "DataSet", "asset-1"]

    @pytest.mark.asyncio
    async def test_add_bookmark(self):
        app = BookmarksHostApp([])
        async with app.run_test() as pilot:
            screen = app.screen_under_test
            screen.action_new_bookmark()
            await pilot.pause()
            screen.query_one("#add_bookmark_guid", Input).value = "asset-9"
            screen.query_one("#add_new_bookmark", Button).press()
            await pilot.pause()
            app.add_my_bookmark.assert_called_once_with("asset-9")
            assert screen.query_one("#my_bookmark_table", DataTable).row_count == 1

    @pytest.mark.asyncio
    async def test_add_bookmark_is_prefilled_with_target_guid(self):
        app = BookmarksHostApp([])
        app.target_guid = "asset-5"
        async with app.run_test() as pilot:
            screen = app.screen_under_test
            screen.action_new_bookmark()
            await pilot.pause()
            assert screen.query_one("#add_bookmark_guid", Input).value == "asset-5"

    @pytest.mark.asyncio
    async def test_remove_highlighted_bookmark(self):
        app = BookmarksHostApp([("A", "Asset", "asset-1"), ("B", "Asset", "asset-2")])
        async with app.run_test() as pilot:
            screen = app.screen_under_test
            table = screen.query_one("#my_bookmark_table", DataTable)
            table.move_cursor(row=1)
            screen.action_remove_bookmark()
            await pilot.pause()
            app.delete_my_bookmark.assert_called_once_with("asset-2")
            assert table.row_count == 1

    @pytest.mark.asyncio
    async def test_quit(self):
        app = BookmarksHostApp([])
        async with app.run_test() as pilot:
            app.screen_under_test.action_quit()
            await pilot.pause()
            assert app.dismissed == 200


class TableHostApp(App):
    """Host app with a single DataTable, for row-identity and bookmark-row tests."""

    def __init__(self, columns, rows):
        super().__init__()
        self.columns, self.rows = columns, rows

    def compose(self):
        yield DataTable(id="t")

    def on_mount(self):
        table = self.query_one("#t", DataTable)
        table.add_columns(*self.columns)
        for i, row in enumerate(self.rows):
            table.add_row(*row, key=f"r{i}")


class TestBookmarkTableRow:
    @pytest.mark.asyncio
    async def test_row_identity_reads_guid_and_qualified_name_columns(self):
        from profile_utils import row_identity
        app = TableHostApp(["Collection Name", "Qualified Name", "Collection GUID"],
                           [("Clinical", "Collection::Clinical", "coll-1")])
        async with app.run_test():
            assert row_identity(app.query_one("#t", DataTable), "r0") == ("coll-1", "Collection::Clinical")

    @pytest.mark.asyncio
    async def test_bookmarks_row_by_guid(self, client):
        client.get_collections_by_name.return_value = [BOOKMARKS_COLLECTION]
        app = TableHostApp(["Role Name", "Description", "GUID"], [("Steward", "Looks after data", "role-1")])
        async with app.run_test():
            assert DummyApp().bookmark_table_row(app.query_one("#t", DataTable), "r0") is True
            client.get_guid_for_name.assert_not_called()
            client.add_to_collection.assert_called_once_with(collection_guid="bm-coll-guid", element_guid="role-1")

    @pytest.mark.asyncio
    async def test_bookmarks_row_by_qualified_name(self, client):
        client.get_collections_by_name.return_value = [BOOKMARKS_COLLECTION]
        client.get_guid_for_name.return_value = "gloss-1"
        app = TableHostApp(["Glossary Name", "Description", "Qualified Name"],
                           [("Clinical Terms", "Terms", "Glossary::Clinical-Terms")])
        async with app.run_test():
            assert DummyApp().bookmark_table_row(app.query_one("#t", DataTable), "r0") is True
            client.get_guid_for_name.assert_called_once_with("Glossary::Clinical-Terms")
            client.add_to_collection.assert_called_once_with(collection_guid="bm-coll-guid", element_guid="gloss-1")

    @pytest.mark.asyncio
    async def test_row_without_identity_is_refused(self, client):
        app = TableHostApp(["Name", "Description"], [("Something", "No id here")])
        async with app.run_test():
            dummy = DummyApp()
            assert dummy.bookmark_table_row(app.query_one("#t", DataTable), "r0") is False
            client.add_to_collection.assert_not_called()
            assert dummy.notices[-1][1] == "warning"

    @pytest.mark.asyncio
    async def test_unresolvable_qualified_name_is_refused(self, client):
        client.get_guid_for_name.return_value = "No elements found"
        app = TableHostApp(["Glossary Name", "Qualified Name"], [("Gone", "Glossary::Gone")])
        async with app.run_test():
            assert DummyApp().bookmark_table_row(app.query_one("#t", DataTable), "r0") is False
            client.add_to_collection.assert_not_called()
