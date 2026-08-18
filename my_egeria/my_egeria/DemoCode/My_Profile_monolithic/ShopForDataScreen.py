"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""

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

    def __init__ (self, glossary_table, digital_product_catalog_table, data_dictionary_table, business_domain_table, root_collection_table,
                  user_name, user_password, view_server, platform_url):
        """Initialize the ShopForDataScreen screen."""
        self.glossary_table: DataTable = glossary_table
        self.digital_product_catalog_table: DataTable = digital_product_catalog_table
        self.data_dictionary_table: DataTable = data_dictionary_table
        self.business_domain_table: DataTable = business_domain_table
        self.root_collection_table: DataTable = root_collection_table
        self.user_name = user_name
        self.user_password = user_password
        self.view_server = view_server
        self.platform_url = platform_url
        super().__init__()

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

    # @on(DataTable.RowHighlighted)
    # def handle_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
    #     """ Handle the highlighting of a row in the DataTable."""
    #     table = event.data_table
    #     row_key = event.row_key
    #     row_values = self.query_one("#"+str(table), DataTable).get_row(row_key)
    #     row_qualified_name = row_values[0]
    #     row_description = row_values[1]
    #     row_GUID = row_values[2]
    #     self.log(f"Table {table} Row highlighted: {row_key}, values: {row_values}, qualified name: {row_qualified_name}, description: {row_description}, GUID: {row_GUID}")

    def action_back(self) -> None:
        """ The back option in the footer has been selected. Dismiss the screen."""
        self.dismiss([200])

    def action_search_for_term(self) -> None:
        """ The search for term option in the footer has been selected. Dismiss the screen."""
        self.dismiss([201])

    def action_quit(self) -> None:
        """ The quit option in the footer has been selected. Dismiss the screen."""
        self.dismiss([210])

    # def action_subscribe_to_data(self) -> None:
    #     """ The subscribe to data option in the footer has been selected."""
    #     self.dismiss([211])

    def action_sample_data_source(self):
        """ The sample data source option in the footer has been selected."""
        self.dismiss([212, self.row_highlighted, self.cursor_row_highlighted, self.data_table_highlighted])