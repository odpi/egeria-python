"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""

from pyegeria import load_app_config, settings
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.events import Action
from textual.screen import Screen
from textual.widgets import DataTable, Header, TextArea, Static, Footer


class ShopForDataScreen(Screen):
    """ Screen to Present a choice of different data sources to the user."""
    BINDINGS = [("q", "dismiss(200)", "Quit"),
                ("s", "sample_data_source", "Sample data source"),
                ("b", "back", "Go back")]

    CSS_PATH = "my_profile.tcss"

    def __init__(
        self,
        glossary_table: DataTable | None = None,
        digital_product_catalog_table: DataTable | None = None,
        data_dictionary_table: DataTable | None = None,
        business_domain_table: DataTable | None = None,
        root_collection_table: DataTable | None = None,
        user_name: str | None = None,
        user_password: str | None = None,
        view_server: str | None = None,
        platform_url: str | None = None,
        data_specification_table: DataTable | None = None,
        *args,
        **kwargs,
    ):
        """Initialize the ShopForDataScreen screen."""
        super().__init__(*args, **kwargs)
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.user_name = user_name or app_user.user_name or "garygeeke"
        self.user_password = user_password or app_user.user_pwd or "secret"
        self.view_server = view_server or app_config.egeria_view_server or "qs-view-server"
        self.platform_url = platform_url or app_config.egeria_platform_url or "https://127.0.0.1:9443"

        self.glossary_table: DataTable = glossary_table if glossary_table is not None else DataTable(id="glossary_table")
        self.digital_product_catalog_table: DataTable = (
            digital_product_catalog_table if digital_product_catalog_table is not None else DataTable(id="digital_product_catalog_table")
        )
        self.data_dictionary_table: DataTable = (
            data_dictionary_table if data_dictionary_table is not None else DataTable(id="data_dictionary_table")
        )
        self.business_domain_table: DataTable = (
            business_domain_table if business_domain_table is not None else DataTable(id="business_domain_table")
        )
        self.root_collection_table: DataTable = (
            root_collection_table if root_collection_table is not None else DataTable(id="root_collection_table")
        )
        self.data_specification_table: DataTable = (
            data_specification_table if data_specification_table is not None else DataTable(id="data_specification_table")
        )
        self.row_highlighted = None
        self.cursor_row_highlighted = None
        self.data_table_highlighted = None

    def compose(self) -> ComposeResult:
        """ Compose the UI components for the ShopForDataScreen screen."""
        yield Header(show_clock=True)
        yield TextArea(f"\n\n\nPlease click on a line to select a data source:")
        yield ScrollableContainer(
            Static("Glossary"),
            self.glossary_table)
        yield ScrollableContainer(
            Static("Digital Product Catalog"),
            self.digital_product_catalog_table)
        yield ScrollableContainer(
            Static("Data Dictionary"),
            self.data_dictionary_table)
        yield ScrollableContainer(
            Static("Business Domain"),
            self.business_domain_table)
        yield ScrollableContainer(
            Static("Root Collection"),
            self.root_collection_table)
        yield Footer()


    def on_mount(self) -> None:
        self.header = f"Egeria Data Sources for user {self.user_name}"
        self.sub_header = "Shop for Data"

    # @on(DataTable.RowSelected)
    # def handle_data_table_highlight(self, event: DataTable.RowHighlighted):
    #     self.row_highlighted = event.row_key
    #     self.cursor_row_highlighted = event.cursor_row
    #     self.data_table_highlighted = event.data_table
    #     self.log(f"Row highlighted: {self.row_highlighted}")


    @on(DataTable.RowSelected, "#glossary_table")
    def handle_glossary_table_selection(self, event: DataTable.RowSelected):
        row_selected = event.row_key
        row_values = self.glossary_table.get_row(row_selected)
        row_display_name = row_values[0]
        row_description = row_values[1]
        row_qualified_name = row_values[2]
        self.log(f"Row selected: {row_selected}, values: {row_values}, display name: {row_display_name}, description: {row_description}, qualified name: {row_qualified_name}")
        self.dismiss (["glossary", row_qualified_name, row_display_name])

    @on(DataTable.RowSelected, "#digital_product_catalog_table")
    def handle_digital_product_catalog_table_selection(self, event: DataTable.RowSelected):
        row_selected = event.row_key
        self.log(f"Digital product row selected: {row_selected}, event: {event}")
        row_values = self.query_one("#digital_product_catalog_table", DataTable).get_row(event.row_key)
        self.log(f"Digital product row values: {row_values}")
        row_display_name = row_values[0]
        row_description = row_values[1]
        row_qualified_name = row_values[2]
        self.log(f"Row selected: {row_selected}, values: {row_values}, display name: {row_display_name}, description: {row_description}, qualified name: {row_qualified_name}")
        self.dismiss (["catalog", row_qualified_name, row_display_name])

    @on(DataTable.RowSelected, "#data_dictionary_table")
    def handle_data_dictionary_table_selection(self, event: DataTable.RowSelected):
        row_selected = event.row_key
        row_values = self.query_one("#data_dictionary_table", DataTable).get_row(event.row_key)
        row_display_name = row_values[0]
        row_description = row_values[1]
        row_qualified_name = row_values[2]
        self.log(f"Row selected: {row_selected}, values: {row_values}, display name: {row_display_name}, description: {row_description}, qualified name: {row_qualified_name}")
        self.dismiss (["dictionary", row_qualified_name, row_display_name])

    @on(DataTable.RowSelected, "#business_domain_table")
    def handle_business_domain_table_selection(self, event: DataTable.RowSelected):
        row_selected = event.row_key
        row_values = self.query_one("#business_domain_table", DataTable).get_row(event.row_key)
        row_qualified_name = row_values[0]
        row_type_name = row_values[1]
        row_guid = row_values[2]
        self.log(f"Row selected: {row_selected}, values: {row_values}, qualified name: {row_qualified_name}, type name: {row_type_name}, guid: {row_guid}")
        self.dismiss (["domain", row_qualified_name, row_type_name])

    @on(DataTable.RowSelected, "#data_specification_table")
    def handle_data_specification_table_selection(self, event: DataTable.RowSelected):
        row_selected = event.row_key
        row_values = self.query_one("#data_specification_table", DataTable).get_row(event.row_key)
        row_display_name = row_values[0]
        row_description = row_values[1]
        row_qualified_name = row_values[2]
        self.log(f"Row selected: {row_selected}, values: {row_values}, display name: {row_display_name}, description: {row_description}, qualified name: {row_qualified_name}")
        self.dismiss (["specification", row_qualified_name, row_display_name])

    @on (DataTable.RowSelected, "#root_collection_table")
    def handle_root_collection_table_selection(self, event: DataTable.RowSelected):
        row_selected = event.row_key
        row_values = self.query_one("#root_collection_table", DataTable).get_row(event.row_key)
        row_qualified_name = row_values[0]
        row_description = row_values[1]
        row_GUID = row_values[2]
        self.log(f"Row selected: {row_selected}, values: {row_values}, qualified name: {row_qualified_name}, description: {row_description}, GUID: {row_GUID}")
        self.dismiss (["collection", row_qualified_name, row_description])

    @on(DataTable.RowHighlighted)
    def handle_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Handle the highlighting of a row in any DataTable."""
        self.row_highlighted = event.row_key
        self.cursor_row_highlighted = event.cursor_row
        self.data_table_highlighted = event.data_table.id
        self.log(f"Table {self.data_table_highlighted} Row highlighted: {self.row_highlighted}, cursor: {self.cursor_row_highlighted}")

    def action_back(self) -> None:
        """ The back option in the footer has been selected. Dismiss the screen."""
        self.dismiss([200])

    def action_search_for_term(self) -> None:
        """ The search for term option in the footer has been selected. Dismiss the screen."""
        self.dismiss([201])

    def action_quit(self) -> None:
        """ The quit option in the footer has been selected. Dismiss the screen."""
        self.dismiss([210])

    def action_sample_data_source(self):
        """ The sample data source option in the footer has been selected."""
        tables = [
            self.digital_product_catalog_table,
            self.glossary_table,
            self.data_dictionary_table,
            self.business_domain_table,
            self.root_collection_table,
            self.data_specification_table,
        ]
        target_table = None
        if getattr(self, "data_table_highlighted", None):
            for t in tables:
                if t is not None and getattr(t, "id", None) == self.data_table_highlighted:
                    target_table = t
                    break

        if target_table is None:
            focused = getattr(self, "focused", None)
            if isinstance(focused, DataTable):
                target_table = focused
                self.data_table_highlighted = getattr(focused, "id", None)
                self.cursor_row_highlighted = focused.cursor_row
                try:
                    self.row_highlighted = list(focused.rows.keys())[focused.cursor_row] if focused.cursor_row is not None and focused.cursor_row < len(focused.rows) else None
                except Exception:
                    self.row_highlighted = None

        if target_table is None:
            for t in tables:
                if t is not None and getattr(t, "row_count", 0) > 0:
                    target_table = t
                    self.data_table_highlighted = getattr(t, "id", None)
                    self.cursor_row_highlighted = t.cursor_row
                    try:
                        self.row_highlighted = list(t.rows.keys())[t.cursor_row] if t.cursor_row is not None and t.cursor_row < len(t.rows) else None
                    except Exception:
                        self.row_highlighted = None
                    break

        row_data = []
        if target_table is not None and getattr(target_table, "row_count", 0) > 0:
            try:
                if getattr(self, "row_highlighted", None) is not None and hasattr(target_table, "rows") and self.row_highlighted in target_table.rows:
                    row_data = list(target_table.get_row(self.row_highlighted))
                elif getattr(self, "cursor_row_highlighted", None) is not None and target_table.row_count > self.cursor_row_highlighted:
                    row_data = list(target_table.get_row_at(self.cursor_row_highlighted))
                elif target_table.cursor_row is not None and target_table.row_count > target_table.cursor_row:
                    row_data = list(target_table.get_row_at(target_table.cursor_row))
                else:
                    row_data = list(target_table.get_row_at(0))
            except Exception as e:
                self.log(f"Error getting row data from table: {e}")

        self.dismiss([
            212,
            getattr(self, "row_highlighted", None),
            getattr(self, "cursor_row_highlighted", None),
            getattr(self, "data_table_highlighted", None),
            row_data,
        ])