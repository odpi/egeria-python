"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""

from typing import Any

from pyegeria import exec_report_spec, PyegeriaException, print_basic_exception
from textual import app, on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Container
from textual.css.query import NoMatches
from textual.screen import Screen, ModalScreen
from textual.widgets import Tree, Header, Static, Placeholder, Footer, TextArea, Markdown

from StatusScreen import StatusScreen


class SelectionOverviewScreen(ModalScreen):
    """Screen to display the selection of the user's data sources."""
    BINDINGS = [("q", "quit", "Quit"),
                ("s", "subscribe", "Subscribe to Data Source"),
                ("b", "back", "Go back")]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, category, view_server, url, user, pwd, data_tree=None, data_samples=None):
        self.category = category
        self.view_server = view_server
        self.platform_url = url
        self.user_name = user
        self.user_password = pwd
        self.data_tree = data_tree
        self.sample_data = data_samples
        self.glossary_term_var_list: list = []

        if self.data_tree is None:
            if self.category == "glossary":
                try:
                    self.data_tree: Tree = self.app.query_one("#glossary_details_tree", Tree)
                except NoMatches:
                    self.dismiss(411)
                    return
            elif self.category == "catalog":
                try:
                    self.data_tree: Tree = self.app.query_one("#digital_product_catalog_tree", Tree)
                except NoMatches:
                    self.dismiss(412)
                    return
            elif self.category == "dictionary":
                try:
                    self.data_tree: Tree = self.app.query_one("#data_dictionary_tree", Tree)
                except NoMatches:
                    self.dismiss(413)
                    return
            elif self.category == "domain":
                try:
                    self.data_tree: Tree = self.app.query_one("#business_domain_tree", Tree)
                except NoMatches:
                    self.dismiss(414)
                    return
            elif self.category == "collection":
                try:
                    self.data_tree: Tree = self.app.query_one("#root_collection_tree", Tree)
                except NoMatches:
                    self.dismiss(415)
                    return
            else:
                # unknown category
                self.dismiss(410)
        super().__init__()

    def compose(self) -> ComposeResult:
        """ Compose the UI components for the SelectionOverviewScreen screen."""
        self.title = f"Shopping for Data, Data Selection:"
        self.sub_title = f"Category: {self.category}"
        yield Header(show_clock=True)
        yield Static("Please select an item from the tree [blink]:[/]", id="instruction_static")
        yield ScrollableContainer(
                                    self.data_tree,
                                    id="data_tree_container"
                                    )
        yield Container(
            ScrollableContainer(
                                Placeholder(id="data_details_placeholder"),
                                id="data_details_placeholder_container"
                                    ),
            ScrollableContainer(
                                Placeholder(id="data_sample_placeholder"),
                                id="data_sample_placeholder_container"
                                    )
                        )
        yield Footer()

    def action_quit(self) -> None:
        """ The quit option in the footer has been selected. Dismiss the screen."""
        self.dismiss(210)

    def action_back(self) -> None:
        """ The back option in the footer has been selected. Dismiss the screen."""
        self.dismiss(200)

    @on(Tree.NodeSelected)
    def handle_tree_node_selected(self, event: Tree.NodeSelected):
        # Modify to handle for each tree?
        self.node_selected = event.node
        self.tree_selected = event.node.parent
        self.log(f"Tree selected: {self.tree_selected}")
        self.log(f"Node selected: {self.node_selected}")
        self.node_label = self.node_selected.label
        self.node_data = self.node_selected.data
        # the provided id can be either a GUID or a qualified name!
        # the variable is labeled guid but it could contain a qualified name, both guid and qualified name are strings.
        self.node_GUID = self.node_selected.data
        self.log(f"Node label: {self.node_label}, GUID: {self.node_GUID}")
        if self.category == "glossary":
            self.display_selected_term_details(self.node_GUID)
        elif self.category == "catalog":
            self.display_selected_digital_product(self.node_GUID)
        elif self.category == "dictionary":
            self.display_selected_data_dictionary(self.node_GUID)
        elif self.category == "domain":
            self.display_selected_business_domain(self.node_GUID)
        elif self.category == "collection":
            self.display_selected_root_collection(self.node_GUID)
        # elif self.category == "specification":
        #     self.display_selected_data_specification(self.node_GUID)

    def display_selected_term_details(self, term_GUID) -> Any:
        """ The user has selected a glossary term, build a display of the term details,
             and show along side the glossary tree """
        self.term_GUID = term_GUID
        self.log(f"Selected glossary term GUID: {self.term_GUID}")
        try:
            self.glossary_term_data = exec_report_spec(format_set_name="Glossary-Terms",
                                                  output_format="MD",
                                                  params={"search_string": self.term_GUID, "filter_string": self.term_GUID},
                                                  view_server=self.view_server,
                                                  view_url=self.platform_url,
                                                  user=self.user_name,
                                                  user_pass=self.user_password)
        except PyegeriaException as e:
            self.log(f"Error retrieving glossary details: {e!s}")
            self.glossary_term_data = []
        if isinstance(self.glossary_term_data, dict):
            if self.glossary_term_data.get("kind") == "text":
                if self.glossary_term_data.get("mime") == "text/markdown":
                    self.glossary_term_data = self.glossary_term_data.get("content")
                else:
                    self.glossary_term_data = "No Markdown content found for this glossary term"
            else:
                self.glossary_term_data = "No Markdown content found for this glossary term"
        else:
            self.glossary_term_data = "No Markdown content found for this glossary term"
        container = self.query_one("#data_details_placeholder_container")
        container.remove_children()

        # if not self.glossary_term_data or self.glossary_term_data == [] or self.glossary_term_data == None or self.glossary_term_data.get("kind") == "empty":
        if not self.glossary_term_data or self.glossary_term_data == [] or self.glossary_term_data == None:
            self.log(f"No glossary term data returned for GUID: {self.term_GUID}")
            container.mount(Static(f"No glossary term data returned for GUID: {self.term_GUID}"))
        else:
            self.log(f"Glossary term data returned for term: {self.term_GUID}, content: {self.glossary_term_data} \n")
            markdown = Markdown(self.glossary_term_data)
            markdown.code_indent_guides = False
            self.query_one("#data_details_placeholder_container").mount(markdown)

    def display_selected_digital_product(self, digital_product_GUID) -> Any:
        """ The user has selected a glossary term, build a display of the term details,
                    and show along side the glossary tree """
        self.digital_product_GUID = digital_product_GUID
        self.log(f"Selected digital product: {self.digital_product_GUID}")
        try:
            self.digital_product_data = exec_report_spec(format_set_name="Digital-Products-MyE",
                                                        output_format="MD",
                                                        params={"search_string": self.digital_product_GUID,
                                                               "filter_string": self.digital_product_GUID},
                                                        view_server=self.view_server,
                                                        view_url=self.platform_url,
                                                        user=self.user_name,
                                                        user_pass=self.user_password)
        except PyegeriaException as e:
            print_basic_exception(e)
            self.log(f"Error retrieving digital product details: {e!s}")
            self.digital_product_data = []

        container = self.query_one("#data_details_placeholder_container")
        container.remove_children()

        if not self.digital_product_data or self.digital_product_data == [] or self.digital_product_data == None:
            self.log(f"No digital product data returned for: {self.digital_product_GUID}")
            container.mount(Static(f"No digital product data returned for: {self.digital_product_GUID}"))
        else:
            self.log(f"Digital product data returned for: {self.digital_product_GUID}")
            if isinstance(self.digital_product_data, dict) and self.digital_product_data.get("kind") == "empty":
                self.digital_product_data = "# No content found for this digital product"
            elif isinstance(self.digital_product_data, dict) and self.digital_product_data.get("kind") == "text":
                if self.digital_product_data.get("mime") == "text/markdown":
                    self.digital_product_data = self.digital_product_data.get("content")
                else:
                    self.digital_product_data = "# No Markdown content found for this digital product"
            else:
                self.digital_product_data = "# No dict content found for this digital product"

            markdown = Markdown(str(self.digital_product_data))
            container.mount(markdown)
            sample_container = self.query_one("#data_sample_placeholder_container")
            sample_container.remove_children()
            sample_markdown= Markdown(str(self.sample_data))
            sample_container.mount(sample_markdown)

    def display_selected_data_dictionary(self, data_dictionary_GUID) -> Any:
        """ The user has selected a data dictionary, build a display of the dictionary details,
                            and show along side the dictionary tree """
        self.data_dictionary_GUID = data_dictionary_GUID
        self.log(f"Selected data dictionary GUID: {self.data_dictionary_GUID}")
        try:
            self.data_dictionary_data = exec_report_spec(format_set_name="Data-Dictionaries",
                                                         output_format="MD",
                                                         params={"search_string": self.data_dictionary_GUID,
                                                                 "filter_string": self.data_dictionary_GUID},
                                                         view_server=self.view_server,
                                                         view_url=self.platform_url,
                                                         user=self.user_name,
                                                         user_pass=self.user_password)
        except PyegeriaException as e:
            self.log(f"Error retrieving data dictionary details: {e!s}")
            self.data_dictionary_data = []

        container = self.query_one("#data_details_placeholder_container")
        container.remove_children()

        if not self.data_dictionary_data or self.data_dictionary_data == []:
            self.log(f"No data dictionary data returned for GUID: {self.data_dictionary_GUID}")
            container.mount(Static(f"No data dictionary data returned for GUID: {self.data_dictionary_GUID}"))
        else:
            self.log(f"Data dictionary data returned for GUID: {self.data_dictionary_GUID}")
            if isinstance(self.data_dictionary_data, dict) and self.data_dictionary_data.get("kind") == "text":
                if self.data_dictionary_data.get("mime") == "text/markdown":
                    self.data_dictionary_data = self.data_dictionary_data.get("content")
                else:
                    self.data_dictionary_data = "No Markdown content found for this data dictionary"
            markdown = Markdown(str(self.data_dictionary_data))
            markdown.code_indent_guides = False
            container.mount(markdown)
            container.refresh()

    def display_selected_business_domain(self, business_domain_GUID) -> int:
        """ The user has selected a business domain, build a display of the domain details,
                            and show along side the glossary tree """
        self.business_domain_GUID = business_domain_GUID
        self.log(f"Selected business domain GUID: {self.business_domain_GUID}")
        try:
            self.business_domain_data = exec_report_spec(format_set_name="BusinessCapabilities",
                                                         output_format="DICT",
                                                         params={"search_string": self.business_domain_GUID,
                                                                 "filter_string": self.business_domain_GUID},
                                                         view_server=self.view_server,
                                                         view_url=self.platform_url,
                                                         user=self.user_name,
                                                         user_pass=self.user_password)
        except PyegeriaException as e:
            self.log(f"Error retrieving business domain details: {e!s}")
            self.business_domain_data = []

        container = self.query_one("#data_details_placeholder_container")
        container.remove_children()

        if not self.business_domain_data or self.business_domain_data == []:
            self.log(f"No business domain data returned for GUID: {self.business_domain_GUID}")
            container.mount(Static(f"No business domain data returned for GUID: {self.business_domain_GUID}"))
        else:
            self.log(f"Business domain data returned for GUID: {self.business_domain_GUID}")
            text_area = TextArea(f"Business domain data returned for GUID: {self.business_domain_GUID}",
                     id="business_domain_details_text_area",
                     read_only=True)
            container.mount(text_area)
            text_area.text = str(self.business_domain_data)

    def display_selected_data_specification(self, data_specification_GUID) -> int:
        """ The user has selected a data specification, build a display of the specification details
            and show alongside data specifications tree """

        self.data_specification_qualified_name = data_specification_GUID
        self.log(f"Data specification selected: {self.data_specification_qualified_name}")
        try:
            self.data_specification_data = exec_report_spec(format_set_name="Data-Specification",
                                                            output_format="DICT",
                                                            params={"search_string": self.data_specification_qualified_name,
                                                                    "filter_string": self.data_specification_qualified_name},
                                                            view_server=self.view_server,
                                                            view_url=self.platform_url,
                                                            user=self.user_name,
                                                            user_pass=self.user_password)
        except PyegeriaException as e:
            self.log(f"Error retrieving data specification details: {e!s}")
            self.data_specification_data = []

        container = self.query_one("#data_details_placeholder_container")
        container.remove_children()

        if not self.data_specification_data or self.data_specification_data == []:
            self.log(f"No data specification data returned for qualified name: {self.data_specification_qualified_name}")
            container.mount(Static(f"No data specification data returned for qualified name: {self.data_specification_qualified_name}"))
        else:
            self.log(f"Data specification data returned for qualified name: {self.data_specification_qualified_name}")
            text_area = TextArea(f"Data specification data returned for qualified name: {self.data_specification_qualified_name}",
                     id="data_specification_details_text_area",
                     read_only=True)
            container.mount(text_area)
            text_area.text = str(self.data_specification_data)

    def display_selected_root_collection(self, root_collection_GUID) -> int:
        """ The user has selected a root collection, build a display of the collection details,
            and show alongside the collection tree """
        self.root_collection_GUID = root_collection_GUID
        self.log(f"Selected root collection GUID: {self.root_collection_GUID}")
        try:
            self.root_collection_data = exec_report_spec(format_set_name="Collections",
                                                         output_format="MD",
                                                         params={"search_string": self.root_collection_GUID,
                                                                 "filter_string": self.root_collection_GUID},
                                                         view_server=self.view_server,
                                                         view_url=self.platform_url,
                                                         user=self.user_name,
                                                         user_pass=self.user_password)

        except PyegeriaException as e:
            self.log(f"Error retrieving root collection data: {e}")
            self.collection_data = []

        container = self.query_one("#data_details_placeholder_container")
        container.remove_children()

        if not self.root_collection_data or self.root_collection_data == [] or self.root_collection_data == None:
            self.log(f"No Root collection data returned for GUID: {self.root_collection_GUID}")
            container.mount(Static(f"No Root collection data returned for GUID: {self.root_collection_GUID}"))
        else:
            self.log(f"Root collection data returned for GUID: {self.root_collection_GUID}")
            if isinstance(self.root_collection_data, dict) and self.root_collection_data.get("kind") == "text":
                if self.root_collection_data.get("mime") == "text/markdown":
                    self.root_collection_data = self.root_collection_data.get("content")
                else:
                    self.root_collection_data = "No Markdown content found for this root collection"
            markdown = Markdown(str(self.root_collection_data))
            markdown.code_indent_guides = False
            container.mount(markdown)
            container.refresh()

    def action_subscribe(self):
        """ The subscribe option in the footer has been selected. """
        self.log(f"Subscribe to data selected: {self.node_GUID}")
        # return a completion code, the guid/qualified name of the selected item and the id of the tree it was selected from
        self.dismiss([211, self.node_GUID, self.tree_selected])


