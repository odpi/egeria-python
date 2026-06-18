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

class EditRolesScreen(ModalScreen):
    """ Screen called during editing of a users profile to allow editing of the roles
        they belong too."""

    BINDINGS = [
        ("escape", "exit_screen", "Exit"),
        ("d", "delete_row", "Delete Row")
    ]

    def __init__(self, columns, rows_with_keys, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_roles_table: DataTable = DataTable(id="roles_destination")
        self.row_key = None
        self.columns = columns
        self.rows_with_keys = rows_with_keys
        self.roles_container: ScrollableContainer

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Edit Roles", classes="span-3", id="edit_roles_title")
        yield Static(" Please note you may only delete one row at a time!", classes="span-3")
        yield ScrollableContainer(id="edit_roles_container")
        yield Footer()

    async def on_mount(self):
        self.log("Edit roles screen mounted")
        self.title = "Egeria - my_profile"
        self.sub_title = "Edit Roles"
        # Populate DataTable
        self.my_roles_table.clear(columns=True)
        self.my_roles_table.add_columns(*self.columns)
        for key_str, cell_values in self.rows_with_keys:
            self.my_roles_table.add_row(*cell_values, key=key_str)

        try:
            # Access the edit roles container in the screen composition objects
            self.roles_container = self.query_one("#edit_roles_container", ScrollableContainer)
            self.log(f"Roles container found: {self.roles_container}")
            # Mount the table into the container
            await self.roles_container.mount(self.my_roles_table)
            self.log("Table mounted into container")
            # To make sure, refresh the container object on the display
            self.roles_container.refresh(layout=True)
            self.my_roles_table.refresh(layout=True)
            self.focus()
            self.call_after_refresh(self.my_roles_table.focus)
        except NoMatches as e:
            # If there is an error finding the container
            self.log(f"Edit roles container not found - Error: {e}")
            await self.dismiss(400)

    @on(DataTable.RowSelected, "#roles_destination")
    def row_selected(self, event: DataTable.RowSelected):
        """ When the user selects a row in the data table store the row key"""
        self.row_key = event.row_key

    def action_exit_screen(self):
        """ The user has requested to exit the screen, return the current table data """
        rows_with_keys = []
        for row_key in self.my_roles_table.rows:
            rows_with_keys.append((row_key.value, self.my_roles_table.get_row(row_key)))
        self.dismiss(rows_with_keys)

    def action_delete_row(self):
        """ The user has selected the delete row option """
        self.log(f"Delete row selected, row key: {self.row_key}")
        # If there is a row selected, delete it and clear the row key variable
        if self.row_key:
            self.my_roles_table.remove_row(self.row_key)
            self.my_roles_table.refresh()
            self.roles_container.refresh(layout=True)
            self.row_key = None
        # If there is no row key in the variable, inform the user by mounting a message into the container
        # and wait for any further actions.
        else:
            self.roles_container.mount(Static("Please select a row to delete prior to using the hot key!"))
            self.roles_container.refresh(layout=True)
