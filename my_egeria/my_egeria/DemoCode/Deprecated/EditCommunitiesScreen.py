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
from textual.widgets import Header, Footer, DataTable, Static, Placeholder, Input, Button


class EditCommunitiesScreen(ModalScreen):
    """ Screen called during editing of a users profile to allow editing of the communities
        they belong too."""

    BINDINGS = [
        ("escape", "exit_screen", "Exit"),
        ("ctrl+c", "add_community", "Add Community"),
        ("ctrl+r", "remove_link_to_community", "Remove Link to Community"),
        ("ctrl+e", "delete_community", "Delete Community"),
        ("ctrl+m", "add_comment", "Add Comment"),
        ("ctrl+o", "show_comments", "Show Comments"),
        ("ctrl+s", "show_team_members", "Show Team")
    ]

    def __init__(self, columns, rows_with_keys, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.my_communities_table: DataTable = DataTable(id="communities_destination")
        self.row_key = None
        self.columns = columns
        self.rows_with_keys = rows_with_keys
        self.communities_container: ScrollableContainer
        self.new_name = ""
        self.new_description = ""
        self.new_mission = ""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Edit Communities", classes="span-3", id="edit_communities_title")
        yield Static(" Please note you may only add or delete one row at a time!", classes="span-3")
        yield ScrollableContainer(id="edit_communities_container")
        yield Footer()

    async def on_mount(self):
        self.log("Edit communities screen mounted")
        self.title = "Egeria - my_profile"
        self.sub_title = "Edit Communities"
        # Populate DataTable
        self.my_communities_table.clear(columns=True)
        self.my_communities_table.add_columns(*self.columns)
        self.my_communities_table.cursor_type="row"
        for key_str, cell_values in self.rows_with_keys:
            self.my_communities_table.add_row(*cell_values, key=key_str)

        try:
            # Access the edit communities container in the screen composition objects
            self.communities_container = self.query_one("#edit_communities_container", ScrollableContainer)
            self.log(f"Communities container found: {self.communities_container}")
            # Mount the table into the container
            await self.communities_container.mount(self.my_communities_table)
            self.log("Table mounted into container")
            # To make sure, refresh the container object on the display
            self.communities_container.refresh(layout=True)
            self.my_communities_table.refresh(layout=True)
            self.focus()
            self.call_after_refresh(self.my_communities_table.focus)
        except NoMatches as e:
            # If there is an error finding the container
            self.log(f"Edit communities container not found - Error: {e}")
            await self.dismiss(400)

    @on(DataTable.RowSelected, "#communities_destination")
    def row_selected(self, event: DataTable.RowSelected):
        """ When the user selects a row in the data table store the row key"""
        self.row_key = event.row_key

    def action_exit_screen(self):
        """ The user has requested to exit the screen, return the current table data """
        rows_with_keys = []
        for row_key in self.my_communities_table.rows:
            rows_with_keys.append((row_key.value, self.my_communities_table.get_row(row_key)))
        self.dismiss(rows_with_keys)

    def action_delete_community(self):
        """ The user has selected the delete row option """
        self.log(f"Delete community selected, row key: {self.row_key}")
        # If there is a row selected, delete it and clear the row key variable
        if self.row_key:
            self.row_content = self.my_communities_table.get_row(self.row_key)
            # Delete the Community from Egeria, change this to call a function in the app.
            self.log(f"Deleting community with content: {self.row_content}")
            del_comm_rc = self.app.delete_community(self.row_content)
            if del_comm_rc == 200:
                self.my_communities_table.remove_row(self.row_key)
                self.my_communities_table.refresh()
                self.communities_container.refresh(layout=True)
            else:
                self.communities_container.mount(Static("Failed to delete community, please try again!"))
                self.communities_container.refresh(layout=True)
            self.row_key = None
        # If there is no row key in the variable, inform the user by notifying the user
        # and waiting for any further actions.
        else:
            self.notify("Please select a row to delete prior to using the hot key!")
            self.communities_container.refresh(layout=True)
        return

    def action_add_community(self):
        """ The user has selected the add community option """
        self.log("Add community selected")
        container = self.query_one("#edit_communities_container", ScrollableContainer)
        container.mount(
            Input("Name", id="new_community_name"),
            Input("Description", id="new_community_description"),
            Input("Mission", id="new_community_mission"),
            Button("Add community", id="add_community_button")
        )
        container.refresh()
        new_name = self.query_one("#new_community_name", Input).focus=True
       # self.communities_container.mount(Static("Add community functionality not yet implemented!"))
        # self.communities_container.refresh(layout=True)

    def action_remove_link_to_community(self):
        """ The user has selected the remove link to community option """
        self.log(f"Remove link to community selected: {self.row_key}")

        # If there is a row selected, remove the link to the actor profile and
        # delete it from the DataTable and clear the row key variable
        if self.row_key:
            self.row_content = self.my_communities_table.get_row(self.row_key)
            # Remove the link to the Community from the actor profile,
            # to do this call a function in the app.
            self.log(f"Deleting link to community with content: {self.row_content}")
            rem_comm_rc = self.app.remove_link_to_community(self.row_content)
            if rem_comm_rc == 200:
                self.my_communities_table.remove_row(self.row_key)
                self.my_communities_table.refresh()
                self.communities_container.refresh(layout=True)
            else:
                self.communities_container.mount(Static("Failed to delete link to community, please try again!"))
                self.communities_container.refresh(layout=True)
            self.row_key = None
        # If there is no row key in the variable, inform the user by notifying the user
        # and waiting for any further actions.
        else:
            self.notify("Please select a row to remove the link to prior to using the hot key!")
            self.communities_container.refresh(layout=True)
        return

    def action_show_team_members(self):
        """ The user has selected the show team members option """
        self.log("Show team members selected")
        self.app.show_team(self.row_key)

    @on(Input.Changed, "#new_community_name")
    def on_input_changed(self, event: Input.Changed):
        self.log("Input changed")
        self.new_name = event.value

    @on(Input.Changed, "#new_community_description")
    def on_input_changed(self, event: Input.Changed):
        self.log("Input changed")
        self.new_description = event.value

    @on(Input.Changed, "#new_community_mission")
    def on_input_changed(self, event: Input.Changed):
        self.log("Input changed")
        if event.control.id == "new_community_mission":
            self.new_mission = event.value
        elif event.control.id == "new_community_description":
            self.new_description = event.value
        elif event.control.id == "new_community_name":
            self.new_name = event.value

    @on(Button.Pressed, "#add_community_button")
    def on_button_pressed(self, event: Button.Pressed):
        self.log("Button pressed")
        self.add_community()

    def add_community(self):
        if self.new_name and self.new_description and self.new_mission:
            self.dismiss(["add", self.new_name, self.new_description, self.new_mission])
        else:
            self.log("Missing required fields")
            self.notify("Missing required fields, please complete all input before adding", timeout=5, severity="warning")