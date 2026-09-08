"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""
from typing import Any
from textual import events, on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import DataTable, OptionList, Header, Static, Footer
from textual.widgets._option_list import Option


class MainScreen(Screen):
    """Main Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+b", "bookmarks", "Manage Bookmarks"),
        ("ctrl+s", "show_comments", "Show Comments for Selected Row"),
        ("ctrl+t", "edit_table", "Edit Selected Table"),
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
                Option("Subscriptions"),
                Option("Technology Types"),
                Option("User Bookmarks"),
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

    def on_descendant_focus(self, event: events.DescendantFocus) -> None:
        """Track which DataTable is currently focused when clicking or navigating into it."""
        if isinstance(event.widget, DataTable):
            self.selected_table = event.widget.id
            if event.widget.row_count > 0 and 0 <= event.widget.cursor_row < event.widget.row_count:
                try:
                    self.selected_row = event.widget.coordinate_to_cell_key(event.widget.cursor_coordinate).row_key
                except Exception:
                    self.selected_row = None
            else:
                self.selected_row = None
            self.log(f"Focused Table: {self.selected_table}, Row: {self.selected_row}")

    @on(DataTable.RowHighlighted)
    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted):
        """ Collect row and table when the user highlights a row in a table """
        self.selected_row = event.row_key
        self.selected_table = event.data_table.id
        self.log(f"Highlighted Table: {self.selected_table}, Row: {self.selected_row}")

    @on(DataTable.RowSelected)
    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        """ Collect row and table when the user selects a row in a table """
        self.selected_row = event.row_key
        self.selected_table = event.data_table.id
        self.log(f"Selected Table: {self.selected_table}, Row: {self.selected_row}")

    @on(DataTable.CellHighlighted)
    def on_data_table_cell_highlighted(self, event: DataTable.CellHighlighted):
        """ Collect row and table when a cell is highlighted in a table """
        self.selected_row = event.cell_key.row_key
        self.selected_table = event.data_table.id
        self.log(f"Cell Highlighted Table: {self.selected_table}, Row: {self.selected_row}")

    @on(DataTable.CellSelected)
    def on_data_table_cell_selected(self, event: DataTable.CellSelected):
        """ Collect row and table when a cell is selected in a table """
        self.selected_row = event.cell_key.row_key
        self.selected_table = event.data_table.id
        self.log(f"Cell Selected Table: {self.selected_table}, Row: {self.selected_row}")

    @on(DataTable.HeaderSelected)
    def on_data_table_header_selected(self, event: DataTable.HeaderSelected):
        """ Collect table when header is selected in a table """
        self.selected_table = event.data_table.id
        self.log(f"Header Selected Table: {self.selected_table}")

    def get_focused_table(self) -> DataTable | None:
        focused_widget = self.screen.focused

        # Check if the focused widget is a DataTable
        if isinstance(focused_widget, DataTable):
            return focused_widget

        return None

    def get_current_table_and_row(self) -> tuple[str | None, Any]:
        """Return the currently focused or selected table id and row key."""
        focused_table = self.get_focused_table()
        if focused_table is not None:
            table_id = focused_table.id
            row_key = None
            if focused_table.row_count > 0 and 0 <= focused_table.cursor_row < focused_table.row_count:
                try:
                    row_key = focused_table.coordinate_to_cell_key(focused_table.cursor_coordinate).row_key
                except Exception:
                    row_key = None
            return table_id, row_key
        return self.selected_table, self.selected_row

    def action_edit_table(self):
        """ Edit the selected table """
        table_name, row_k = self.get_current_table_and_row()
        if table_name:
            self.selected_table = table_name
            self.selected_row = row_k
            self.log(f"Editing Table: {table_name}, Row: {row_k}")
            self.app.edit_tables(table_name, row_k)
        else:
            self.notify("Please select at least a table, or a table and row to edit.", timeout=5, severity="warning")

    async def action_show_comments(self):
        """ Show comments for the selected table """
        table_name, row_k = self.get_current_table_and_row()
        if table_name and row_k:
            self.selected_table = table_name
            self.selected_row = row_k
            self.app.show_comments(table_name, row_k)
        else:
            self.notify("Please select a row and table to show comments.", timeout=5, severity="warning")

    async def action_add_to_table(self):
        """ Add to the selected table.

        Kept as a generic entry point; adding a row is normally reached from
        within the per-table edit screen (Edit Selected Table -> Add Row).
        """
        table_name, row_k = self.get_current_table_and_row()
        if table_name:
            self.selected_table = table_name
            self.selected_row = row_k
            await self.app.add_to_tables(table_name, row_k)
        else:
            self.notify("Please select a table to add to.", timeout=5, severity="warning")

    def action_bookmarks(self):
        """ Manages BookMarks for the currently logged in user
            Note - to add a new bookmark you must first have found and copied
            the GUID of the item you want to bookmark to the clipboard
            as you will need to know it during the add processing"""
        self.app.show_my_bookmarks()

