"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.css.query import NoMatches
from textual.screen import ModalScreen
from textual.widgets import Header, Footer, DataTable, Static, Placeholder


class EditIdentitiesScreen(ModalScreen):
    """ Screen called during editing of a users profile to allow editing of the identities
        they have in Egeria."""

    BINDINGS = [
        ("escape", "app.pop_screen", "Exit"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_identities_table: DataTable
        self.identities_container: ScrollableContainer

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Edit Identities", classes="span-3", id="edit_identities_title")
        yield ScrollableContainer(id="edit_identities_container")
        yield Footer()

    def on_mount(self):
        self.title = "Egeria - my_profile"
        self.sub_title = "Edit Identities"
        try:
            main_screen = self.app.get_screen("main")
            self.my_identities_table = main_screen.query_one("#user_identity_table", DataTable)
            self.my_identities_table.cursor_type = "row"
            self.my_identities_table.zebra = True
            self.my_identities_table.display = True
            self.my_identities_table.visible = True
            try:
                self.identities_container = self.query_one("#edit_identities_container", ScrollableContainer)
                self.identities_container.mount(self.my_identities_table)
                self.identities_container.refresh(layout=True)
                self.my_identities_table.refresh(layout=True)
                self.focus()
                self.call_after_refresh(self.my_identities_table.focus)
            except NoMatches:
                self.dismiss(400)
        except NoMatches:
            self.dismiss(401)
    def on_unmount(self):
        """ When the screen is unmounted move the table back to the main screen"""
        try:
            main_screen = self.app.get_screen("main")
            main_container = main_screen.query_one("#main_identities_container", ScrollableContainer)
            main_container.mount(self.my_identities_table)
        except NoMatches:
            self.log("Error moving identities table back to main screen")
