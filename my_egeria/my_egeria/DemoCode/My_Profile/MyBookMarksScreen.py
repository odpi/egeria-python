"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides the bookmarks screen for My Profile.

"""
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import DataTable, Header, Static, Footer, Input, Button


class MyBookMarksScreen(ModalScreen):
    """List, add and remove the current user's bookmarks.

    The Egeria work is done by the app's BookmarksMixin (add_my_bookmark,
    delete_my_bookmark, list_my_bookmarks); this screen only drives it.
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+n", "new_bookmark", "Add New Bookmark"),
        ("d", "remove_bookmark", "Remove Highlighted Bookmark"),
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, my_bookmarks, *args, target_guid: str | None = None, **kwargs):
        super().__init__(id="bookmark_screen", *args, **kwargs)
        self.title = "Egeria"
        self.sub_title = "My Bookmarks"
        # Rows of (name, type, GUID)
        self.my_bookmarks_data = list(my_bookmarks or [])
        # GUID of the row highlighted when the screen was opened, if any, used to pre-fill a new bookmark
        self.target_guid = target_guid or ""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield ScrollableContainer(
            Static("Your bookmarks. Ctrl+N adds one by GUID; 'd' removes the highlighted one."),
            DataTable(id="my_bookmark_table", zebra_stripes=True, cursor_type="row"),
            id="bookmarks_table_container",
        )
        yield Container(id="action_bookmark_container")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#my_bookmark_table", DataTable)
        table.add_columns("Name", "Type", "GUID")
        self._fill_table()

    def _fill_table(self) -> None:
        table = self.query_one("#my_bookmark_table", DataTable)
        table.clear()
        for name, element_type, guid in self.my_bookmarks_data:
            table.add_row(name, element_type, guid, key=guid)
        if not self.my_bookmarks_data:
            self.notify("You have no bookmarks yet - press Ctrl+N to add one", timeout=5)

    def _reload(self) -> None:
        rows = self.app.list_my_bookmarks()
        if rows is not None:
            self.my_bookmarks_data = rows
            self._fill_table()

    def action_quit(self) -> None:
        """ The user elects to quit the bookmarks function """
        self.dismiss(200)

    def action_new_bookmark(self) -> None:
        """ The user wants to add a bookmark"""
        input_container = self.query_one("#action_bookmark_container", Container)
        input_container.remove_children()
        input_container.mount(
            Input(value=self.target_guid, placeholder="GUID of the element to bookmark", id="add_bookmark_guid"),
            Horizontal(
                Button("Add New Bookmark", id="add_new_bookmark", variant="primary"),
                Button("Cancel", id="cancel_add_bookmark", variant="warning"),
                ),
            )
        self.query_one("#add_bookmark_guid", Input).focus()

    @on(Button.Pressed, "#add_new_bookmark")
    def handle_add_new_bookmark(self, event: Button.Pressed) -> None:
        input_guid = self.query_one("#add_bookmark_guid", Input).value.strip()
        if not input_guid:
            self.notify("You must provide the GUID of the item you want to bookmark before you press the button!",
                        timeout=10, severity="warning")
            return
        if self.app.add_my_bookmark(input_guid):
            self.query_one("#action_bookmark_container", Container).remove_children()
            self._reload()

    @on(Button.Pressed, "#cancel_add_bookmark")
    def handle_cancel_add_bookmark(self, event: Button.Pressed) -> None:
        self.query_one("#action_bookmark_container", Container).remove_children()

    def action_remove_bookmark(self) -> None:
        """ The user wants to remove the highlighted bookmark"""
        table = self.query_one("#my_bookmark_table", DataTable)
        if table.row_count == 0:
            self.notify("There is no bookmark to remove", timeout=5, severity="warning")
            return
        guid = table.get_row_at(table.cursor_row)[2]
        if self.app.delete_my_bookmark(guid):
            self._reload()
