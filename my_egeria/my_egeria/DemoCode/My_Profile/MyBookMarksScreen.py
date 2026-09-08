"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import DataTable, Header, Static, Footer, Placeholder, Input, Button
from pyegeria import (load_app_config,
                      settings,
                      print_basic_exception,
                      Egeria)


class MyBookMarksScreen(ModalScreen):
    """Main Screen for My Profile App."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+n", "new_bookmark", "Add New Bookmark"),
        ("ctrl+r", "remove_bookmark", "Delete Selected Bookmark"),
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, my_bookmarks, *args, **kwargs):
        super().__init__(id="bookmark_screen", *args, **kwargs)
        self.title = "Egeria"
        self.sub_title = "My Bookmarks"
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"
        self.my_bookmarks_data = my_bookmarks

    def on_mount(self) -> None:
        self.my_bookmark_table: DataTable = DataTable(id="my_bookmark_table")
        self.my_bookmark_table.zebra_stripes=True
        self.my_bookmark_table.cursor_type="row"
        self.my_bookmark_table.add_columns("", "", "")
        self.log(f"Bookmark Data:{self.my_bookmarks_data}")
        if self.my_bookmarks_data == None:
            self.my_bookmark_table.add_row("No Bookmarks found for", self.user_name, "")
        else:
            for entry in self.my_bookmarks_data:
                self.my_bookmark_table.add_row(entry[0], entry[1], entry[2])

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield ScrollableContainer(
            Static(f"Existing  Bookmarks, (if any)"),
            DataTable(id="my_bookmark_table"),
            id="bookmarks_table_container",
        )
        yield Container(
            Placeholder(id="bookmark_guid"),
            id="action_bookmark_container"
        )
        yield Footer()

    @on(DataTable.RowHighlighted, "#my_bookmarks_table")
    def handle_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """ Handle the case where the user just highlights the row """
        self.row_key = event.row_key

    @on(DataTable.RowSelected, "#my_bookmarks_table")
    def handle_row_selected(self, event: DataTable.RowSelected) -> None:
        """ Handle the case where the user selects the row """
        self.row_key = event.row_key

    def action_quit(self) -> None:
        """ The user elects to quit the bookmarks function """
        self.dismiss(200)

    def action_new_bookmark(self) -> None:
        """ The user wants to add a bookmark"""
        input_container = self.query_one("#action_bookmark_container", Container)
        input_container.remove_children()
        input_container.mount(Input(placeholder="GUID of the target of the bookmark", id="add_bookmark_guid"))
        input_container.mount(Horizontal(
                Button("Add New Bookmark", id="add_new_bookmark", variant="primary"),
                Button("Quit", id="quit_add_bookmark", variant="warning")))

    @on(Button.Pressed, "#add_new_bookmark")
    def handle_add_new_bookmark(self, event: Button.Pressed) -> None:
        input_guid = self.query_one("#add_bookmark_guid", Input).value
        if input_guid:
            self.app.add_my_bookmark(input_guid)
        else:
            self.notify("You must provide the GUID of the item you want to bookmark before you press the button!",
                        timeout=10,
                        severity="warning")
        self.dismiss(200)

    def action_remove_bookmark(self) -> None:
        """ The user wants to delete a bookmark"""
        input_container = self.query_one("#action_bookmark_container", Container)
        input_container.remove_children()
        input_container.mount(Input(placeholder="GUID of the bookmark to delete", id="del_bookmark_guid"))
        input_container.mount(Button("Delete Bookmark", id="delete_bookmark", variant="primary"))

    @on(Button.Pressed, "#delete_bookmark")
    def handle_add_new_bookmark(self, event: Button.Pressed) -> None:
        input_guid = self.query_one("#del_bookmark_guid", Input).value
        if input_guid:
            self.app.add_my_bookmark(input_guid)
        else:
            self.notify("You must provide the GUID of the bookmark you want to delete before you press the button!",
                        timeout=10,
                        severity="warning")
        self.dismiss(200)