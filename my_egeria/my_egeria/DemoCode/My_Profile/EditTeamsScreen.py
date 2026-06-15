"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.css.query import NoMatches
from textual.screen import ModalScreen
from textual.widgets import Header, Footer, DataTable, Static, Placeholder
from textual.widgets._data_table import RowKey

class EditTeamsScreen(ModalScreen):
    """ Screen called during editing of a users profile to allow editing of the teams
        they belong too."""

    BINDINGS = [
        ("escape", "app.pop_screen", "Exit"),
        ("d", "delete_row", "Delete Row")
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_teams_table: DataTable
        self.row_key = None
        self.teams_container: ScrollableContainer

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Edit Teams", classes="span-3", id="edit_teams_title")
        yield Static(" Please note you may only delete one row at a time!", classes="span-3")
        yield ScrollableContainer(id="edit_teams_container")
        yield Footer()

    def on_mount(self):
        self.log("Edit teams screen mounted")
        self.title = "Egeria - my_profile"
        self.sub_title = "Edit Teams"
        try:
            # Establish awareness of the MainScreen where the teams table exists
            main_screen = self.app.get_screen("main")
            self.log(f"Main screen found: {main_screen}")
            # Access the teams table in the main screen class
            self.my_teams_table = main_screen.query_one("#teams_table", DataTable)
            self.log(f"Teams table found: {self.my_teams_table}")
            self.my_teams_table.cursor_type = "row"
            self.my_teams_table.zebra = True
            self.my_teams_table.display = True
            self.my_teams_table.visible = True
            try:
                # Access the edit teams container in the screen composition objects
                self.teams_container = self.query_one("#edit_teams_container", ScrollableContainer)
                self.log(f"Teams container found: {self.teams_container}")
                # Mount the table into the container
                self.teams_container.mount(self.my_teams_table)
                self.log("Table mounted into container")
                # To make sure, refresh the container object on the display
                self.teams_container.refresh(layout=True)
                self.my_teams_table.refresh(layout=True)
                self.focus()
                self.call_after_refresh(self.my_teams_table.focus)
            except NoMatches as e:
                # If there is an error finding the container
                self.log(f"Edit teams container not found - Error: {e}")
                self.dismiss(400)
        except NoMatches as e:
            # If there is an error finding the teams table
            self.log(f"Teams table not found, possible timing error: {e}")
            self.dismiss(401)

    def on_unmount(self):
        """ When the screen is unmounted move the table back to the main screen"""
        try:
            main_screen = self.app.get_screen("main")
            main_container = main_screen.query_one("#main_teams_container", ScrollableContainer)
            main_container.mount(self.my_teams_table)
        except NoMatches:
            self.log("Error moving teams table back to main screen")

    @on(DataTable.RowSelected, "#teams_table")
    def row_selected(self, event: DataTable.RowSelected):
        """ When the user selects a row in the data table store the row key"""
        self.row_key = event.row_key

    def action_delete_row(self):
        """ The user has selected the delete row option """
        # If there is a row selected, delete it and clear the row key variable
        if self.row_key:
            self.my_teams_table.remove_row(self.row_key)
            self.my_teams_table.refresh()
            self.row_key = None
        # If there is no row key in the variable, inform the user by mounting a message into the container
        # and wait for any further actions.
        else:
            self.teams_container.mount(Static("Please select a row to delete prior to using the hot key!"))
            self.teams_container.refresh()
