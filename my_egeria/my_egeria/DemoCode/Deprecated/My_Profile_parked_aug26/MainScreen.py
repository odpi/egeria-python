"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import DataTable, OptionList, Header, Static, Footer
from textual.widgets._option_list import Option


class MainScreen(Screen):
    """Main Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+e", "edit_selected_table", "Edit Selected Table"),
        ("ctrl+a", "add_note", "Add Note to Selected Item"),
        ("ctrl+s", "show_notes", "Show Notes for Selected Item"),
        ("ctrl+t", "show_team", "Show Team Members for Selected Role"),
        ("r", "app.refresh", "Refresh")
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, *args, **kwargs):
        super().__init__(id="main_screen", *args, **kwargs)
        self.title = "Egeria"
        self.sub_title = "My Profile"
        self.other_function_list: OptionList = OptionList(id="other_function_list")
        self.selected_table = None
        self.selected_row = None

        self.associatioons_table: DataTable = DataTable(id="associations_table")
        self.associatioons_table.zebra_stripes = True
        self.associatioons_table.cursor_type = "row"

        self.projects_table: DataTable = DataTable(id="projects_table")
        self.projects_table.zebra_stripes = True
        self.projects_table.cursor_type = "row"

        self.communities_table: DataTable = DataTable(id="communities_table")
        self.communities_table.zebra_stripes = True
        self.communities_table.cursor_type = "row"

        self.roles_table: DataTable = DataTable(id="roles_table")
        self.roles_table.zebra_stripes = True
        self.roles_table.cursor_type = "row"

        self.teams_table: DataTable = DataTable(id="teams_table")
        self.teams_table.zebra_stripes = True
        self.teams_table.cursor_type = "row"

        self.blogs_table: DataTable = DataTable(id="blogs_table")
        self.blogs_table.zebra_stripes = True
        self.blogs_table.cursor_type = "row"

        self.journal_table: DataTable = DataTable(id="journal_table")
        self.journal_table.zebra_stripes = True
        self.journal_table.cursor_type = "row"

        self.todos_table: DataTable = DataTable(id="todos_table")
        self.todos_table.zebra_stripes = True
        self.todos_table.cursor_type = "row"

    def compose(self) -> ComposeResult:
        # place widgets into grid on screen, note sequence determines position!
        yield Header(show_clock=True, id="main_header")

        yield ScrollableContainer(
            Static("My Associations"),
            DataTable(id="associations_table"),
            id="main_associations_container"
        )

        yield ScrollableContainer(
            Static("My Collections"),
            DataTable(id="my_collections_table"),
            id="main_my_collections_container"
        )

        yield ScrollableContainer(
            Static(f"Other Functions"),
            Static(f"[b]Select a function[/b]"),
            OptionList(
                Option("User Identities"),
                Option("Catalogs/Shop for Data"),
                Option("Edit Profile"),
                Option("Subscriptions", disabled=True),
                Option("Technology Types"),
                Option("User Bookmarks", disabled=True),
                id="other_function_list"
            ),
            id="other_function_container"
        )

        yield ScrollableContainer(
            Static("Roles"),
            DataTable(id="roles_table"),
            id="main_roles_container"
        )

        yield ScrollableContainer(
            Static("Teams"),
            DataTable(id="teams_table"),
            id="main_teams_container"
        )

        yield ScrollableContainer(
            Static("Blogs"),
            DataTable(id="blogs_table"),
            Static("Journal"),
            DataTable(id="journal_table"),
            Static("To-Dos"),
            DataTable(id="todos_table"),
            id="main_activities_container"
        )

        yield ScrollableContainer(
            Static("User Identity"),
            DataTable(id="user_identity_table"),
            id="main_identities_container"
        )

        yield Footer(id="main_footer")

    def action_show_team(self):
        self.log(f"action_show_team, row_key: {self.row_key}, table: {self.table}")
        if self.row_key and self.table == "roles_table":
            self.app.show_team(self.row_key)
        else:
            self.notify(f"Team Members can only be displayed by selecting a role in the Roles table first")

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        self.log(f"{event}, event.row_key: {event.row_key}, table: {event.data_table}")
        self.row_key = event.row_key
        self.table = event.data_table

    def action_edit_selected_table(self):
        self.log(f"action_edit_selected_table, row_key: {self.row_key}, table: {self.table}")
        if self.table:
            self.app.action_edit_selected_table(self.table)
        else:
            self.notify(f"Please select a table first")

    def action_add_note(self):
        self.log(f"action_add_note, row_key: {self.row_key}, table: {self.table}")
        if self.row_key and self.table:
            self.app.action_add_note(self.row_key, self.table)
        else:
            self.notify(f"Please select a table and row first")

    def action_show_notes(self):
        self.log(f"action_show_notes, row_key: {self.row_key}, table: {self.table}")
        if self.row_key and self.table:
            self.app.action_show_notes(self.row_key, self.table)
        else:
            self.notify(f"Please select a table and row first")

