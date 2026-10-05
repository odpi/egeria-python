"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""
import pwd
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import DataTable, OptionList, Header, Static, Footer
from textual.widgets._option_list import Option


class MainScreen(Screen):
    """Main Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+s", "show_comments", "Show Comments for Selected Row"),
        ("ctrl+t", "add_todos", "Add Todos"),
        ("ctrl+j", "add_journals", "Add Journals"),
        ("ctrl+b", "add_blogs", "Add Blogs"),
        ("ctrl+c", "add_association", "Add Association"),
        ("ctrl+r", "add_role", "Add Role"),
        ("ctrl+g", "add_team", "Add Team"),
        ("ctrl+m", "add_my_collections", "Add My Collections"),
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, *args, **kwargs):
        super().__init__(id="main_screen", *args, **kwargs)
        self.title = "Egeria"
        self.sub_title = "My Profile"
        self.other_function_list: OptionList = OptionList(id="other_function_list")
        self.selected_table = None
        self.selected_row = None

    def compose(self) -> ComposeResult:
        # place widgets into grid on screen, note sequence determines position!
        yield Header(show_clock=True, id="main_header")

        yield ScrollableContainer(
            Static("User Associations"),
            DataTable(id="associations_table"),
            id="main_associations_container"
        )
        yield ScrollableContainer(
            Static(f"My Collections"),
            DataTable(id=("my_collections_table")),
            id="my_collections_container"
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

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted):
        """ Collect row and table when the user highlights a row in a table """
        self.selected_row = event.row_key
        self.selected_table = event.data_table.id

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        """ Collect row and table when the user selects a row in a table """
        self.selected_row = event.row_key
        self.selected_table = event.data_table.id

    async def action_edit_table(self):
        """ Edit the selected table """
        if self.selected_table and self.selected_row:
            await self.app.edit_tables(self.selected_table, self.selected_row)
        else:
            self.notify("Please select a row and table to edit.", timeout=5, severity="warning")

    async def action_show_comments(self):
        """ Show comments for the selected table """
        if self.selected_table and self.selected_row:
            self.app.show_comments(self.selected_table, self.selected_row)
        else:
            self.notify("Please select a row and table to show comments.", timeout=5, severity="warning")

    async def action_add_to_table(self):
        """ Add to the selected table """
        if self.selected_table and self.selected_row:
            await self.app.add_to_tables(self.selected_table, self.selected_row)
        else:
            self.notify("Please select a row and table to add to.", timeout=5, severity="warning")

    async def action_add_todos(self):
        """ Add to the selected table """
        self.selected_table = "todos_table"
        self.selected_row = 0
        await self.app.add_to_tables(self.selected_table, self.selected_row)

    async def action_add_journals(self):
        """ Add to the selected table """
        self.selected_table = "journal_table"
        self.selected_row = 0
        await self.app.add_to_tables(self.selected_table, self.selected_row)

    async def action_add_blogs(self):
        """ Add to the selected table """
        self.selected_table = "blogs_table"
        self.selected_row = 0
        await self.app.add_to_tables(self.selected_table, self.selected_row)

    async def action_add_my_collections(self):
        """ Add to the selected table """
        self.selected_table = "my_collections_table"
        self.selected_row = 0
        await self.app.add_to_tables(self.selected_table, self.selected_row)

    async def action_add_association(self):
        """ Add to the selected table """
        self.selected_table = "associations_table"
        self.selected_row = 0
        await self.app.add_to_tables(self.selected_table, self.selected_row)

    async def action_add_role(self):
        """ Add to the selected table """
        self.selected_table = "roles_table"
        self.selected_row = 0
        await self.app.add_to_tables(self.selected_table, self.selected_row)

    async def action_add_team(self):
        """ Add to the selected table """
        self.selected_table = "my_team_table"
        self.selected_row = 0
        await self.app.add_to_tables(self.selected_table, self.selected_row)
