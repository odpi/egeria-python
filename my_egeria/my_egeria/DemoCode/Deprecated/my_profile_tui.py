"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""
from __future__ import annotations

import datetime
import re
from typing import Any

from prompt_toolkit import PromptSession
from prompt_toolkit.clipboard import ClipboardData
from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard

from pyegeria.view.format_set_executor import exec_report_spec
from pyegeria import MyProfile, PyegeriaException, print_basic_exception, AutomatedCuration
from pyegeria import load_app_config, settings
from pyegeria import MetadataExpert

from textual.css.query import NoMatches

from textual.widgets._tree import TreeNode
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Container
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Static, Tree, OptionList, TextArea, Placeholder,
)
from textual.widgets._option_list import Option

class SelectionOverviewScreen(Screen):
    """Screen to display the selection of the user's data sources."""
    BINDINGS = [("q", "quit", "Quit"),
                ("b", "back", "Go back")]

    CSS_PATH = "../My_Profile/my_profile.tcss"

    def __init__(self, category, view_server, url, user, pwd):
        self.category = category
        self.view_server = view_server
        self.platform_url = url
        self.user_name = user
        self.user_password = pwd
        if self.category == "glossary":
            self.data_tree: Tree = app.query_one("#glossary_details_tree", Tree)
        elif self.category == "catalog":
            self.data_tree: Tree = app.query_one("#digital_product_catalog_tree", Tree)
        elif self.category == "dictionary":
            self.data_tree: Tree = app.query_one("#data_dictionary_tree", Tree)
        elif self.category == "domain":
            self.data_tree: Tree = app.query_one("#business_domain_tree", Tree)
        elif self.category == "specification":
            self.data_tree: Tree = app.query_one("#data_specification_tree", Tree)
        else:
            # unknown category
            # push status screen, logic error in code.
            error_category = "Collection Category"
            error_message = "Unknown collection category returned"
            self.log(f"Error in selection overview processing: {error_category}, {error_message}")
            app.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=app.status_callback)
        super().__init__()

    def compose(self) -> ComposeResult:
        """ Compose the UI components for the SelectionOverviewScreen screen."""
        self.title = f"Shopping for Data, Data Selection:"
        self.sub_title = f"Category: {self.category}"
        yield Header(show_clock=True)
        yield Static("Please select an item from the tree [blink]:[/]")
        yield ScrollableContainer(
                                    self.data_tree,
                                    id="data_tree_container"
                                    )
        yield ScrollableContainer(
                                Placeholder(id="data_details_placeholder"),
                                id="data_details_placeholder_container"
                                    )
        yield Footer()

    def action_quit(self) -> None:
        """ The quit option in the footer has been selected. Dismiss the screen."""
        self.dismiss(210)

    def action_back(self) -> None:
        """ The back option in the footer has been selected. Dismiss the screen."""
        self.dismiss(200)

    @on(Tree.NodeSelected, "#data_tree")
    def handle_tree_node_selected(self, event: Tree.NodeSelected):
        # Modify to handle for each tree?
        self.node_selected = event.node
        self.log(f"Node selected: {self.node_selected}")
        self.node_label = self.node_selected.label
        # the provided id can be either a GUID or a qualified name!
        # the variable is labeled guid but it could contain a qualified name, both guid and qualified name are strings.
        self.node_GUID = self.node_selected.data
        self.log(f"Node label: {self.node_label}, GUID: {self.node_GUID}")
        if self.node_label == "glossary":
            self.display_selected_term_details(self.node_GUID)
        elif self.node_label == "digital_product_catalog":
            self.display_selected_digital_product(self.node_GUID)
        elif self.node_label == "data_dictionary":
            self.display_selected_data_dictionary(self.node_GUID)
        elif self.node_label == "business_domain":
            self.display_selected_business_domain(self.node_GUID)
        elif self.node_label == "data_specification":
            self.display_selected_data_specification(self.node_GUID)

    def display_selected_term_details(self, term_GUID) -> Any:
        """ The user has selected a glossary term, build a display of the term details,
             and show along side the glossary tree """
        self.term_GUID = term_GUID
        self.log(f"Selected glossary term GUID: {self.term_GUID}")
        try:
            self.glossary_term_data = exec_report_spec(format_set_name="Glossary-Terms",
                                                  output_format="DICT",
                                                  params={"search_string": self.term_GUID, "filter_string": self.term_GUID},
                                                  view_server=self.view_server,
                                                  view_url=self.platform_url,
                                                  user=self.user_name,
                                                  user_pass=self.user_password)
        except PyegeriaException as e:
            print_basic_exception(e)
            self.log(f"Error retrieving glossary details: {e!s}")
            self.dismiss(421)
            return (421)
        if not self.glossary_term_data or self.glossary_term_data == []:
            self.log(f"No glossary term data returned for GUID: {self.term_GUID}")
            Static(f"No glossary term data returned for GUID: {self.term_GUID}").mount(self.query_one("#glossary_term_details_container"))
        else:
            self.log(f"Glossary term data returned for GUID: {self.term_GUID}")
            TextArea(f"Glossary term data returned for GUID: {self.term_GUID}", id="glossary_term_details_text_area", read_only=True).mount(self.query_one("#glossary_term_details_container"))
            TextArea.data = self.glossary_term_data

    def display_selected_digital_product(self, digital_product_GUID) -> Any:
        """ The user has selected a glossary term, build a display of the term details,
                    and show along side the glossary tree """
        self.digital_product_GUID = digital_product_GUID
        self.log(f"Selected digital product GUID: {self.digital_product_GUID}")
        try:
            self.digital_product_data = exec_report_spec(format_set_name="Digital-Products",
                                                       output_format="DICT",
                                                       params={"search_string": self.digital_product_GUID,
                                                               "filter_string": self.digital_product_GUID},
                                                       view_server=self.view_server,
                                                       view_url=self.platform_url,
                                                       user=self.user_name,
                                                       user_pass=self.user_password)
        except PyegeriaException as e:
            print_basic_exception(e)
            self.log(f"Error retrieving digital product details: {e!s}")
            self.dismiss(421)
            return (421)
        if not self.digital_product_data or self.digital_product_data == []:
            self.log(f"No digital product data returned for GUID: {self.digital_product_GUID}")
            Static(f"No digital product data returned for GUID: {self.digital_product_GUID}").mount(
                self.query_one("#digital_product_details_container"))
        else:
            self.log(f"Digital product data returned for GUID: {self.digital_product_GUID}")
            TextArea(f"Digital product data returned for GUID: {self.digital_product_GUID}", id="digital_product_details_text_area",
                     read_only=True).mount(self.query_one("#digital_product_details_container"))
            TextArea.data = self.digital_product_data

    def display_selected_data_dictionary(self, data_dictionary_GUID) -> Any:
        """ The user has selected a data dictionary, build a display of the dictionary details,
                            and show along side the dictionary tree """
        self.data_dictionary_GUID = data_dictionary_GUID
        self.log(f"Selected data dictionary GUID: {self.data_dictionary_GUID}")
        try:
            self.data_dictionary_data = exec_report_spec(format_set_name="Data-Dictionaries",
                                                         output_format="DICT",
                                                         params={"search_string": self.data_dictionary_GUID,
                                                                 "filter_string": self.data_dictionary_GUID},
                                                         view_server=self.view_server,
                                                         view_url=self.platform_url,
                                                         user=self.user_name,
                                                         user_pass=self.user_password)
        except PyegeriaException as e:
            print_basic_exception(e)
            self.log(f"Error retrieving data dictionary details: {e!s}")
            self.dismiss(421)
            return (421)
        if not self.data_dictionary_data or self.data_dictionary_data == []:
            self.log(f"No data dictionary data returned for GUID: {self.data_dictionary_GUID}")
            Static(f"No data dictionary data returned for GUID: {self.data_dictionary_GUID}").mount(
                self.query_one("#data_dictionary_details_container"))
        else:
            self.log(f"Data dictionary data returned for GUID: {self.data_dictionary_GUID}")
            TextArea(f"Data dictionary data returned for GUID: {self.data_dictionary_GUID}",
                     id="data_dictionary_details_text_area",
                     read_only=True).mount(self.query_one("#data_dictionary_details_container"))
            TextArea.data = self.data_dictionary_data

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
            print_basic_exception(e)
            self.log(f"Error retrieving business domain details: {e!s}")
            self.dismiss(421)
            return (421)
        if not self.business_domain_data or self.business_domain_data == []:
            self.log(f"No business domain data returned for GUID: {self.business_domain_GUID}")
            Static(f"No business domain data returned for GUID: {self.business_domain_GUID}").mount(
                self.query_one("#business_domain_details_container"))
        else:
            self.log(f"Business domain data returned for GUID: {self.business_domain_GUID}")
            TextArea(f"Business domain data returned for GUID: {self.business_domain_GUID}",
                     id="business_domain_details_text_area",
                     read_only=True).mount(self.query_one("#business_domain_details_container"))
            TextArea.data = self.business_domain_data

    def display_selected_data_specification(self, data_specification_GUID) -> int:
        """ The user has selected a data specification, build a display of the specification details
            and show alongside data specifications tree """

        self.data_specification_qualified_name = data_specification_GUID
        self.log(f"Data specification selected: {self.data_specification_qualified_name}")
        try:
            self_data_specification_data = exec_report_spec(format_set_name="Data-Specification",
                                                            output_format="DICT",
                                                            params={"search_string": self.data_specification_qualified_name,
                                                                    "filter_string": self.data_specification_qualified_name},
                                                            view_server=self.view_server,
                                                            view_url=self.platform_url,
                                                            user=self.user_name,
                                                            user_pass=self.user_password)
        except PyegeriaException as e:
            print_basic_exception(e)
            self.log(f"Error retrieving data specification details: {e!s}")
            self.dismiss(431)
            return (431)
        if not self_data_specification_data or self_data_specification_data == []:
            self.log(f"No data specification data returned for qualified name: {self.data_specification_qualified_name}")
            Static(f"No data specification data returned for qualified name: {self.data_specification_qualified_name}").mount(
                self.query_one("#data_specification_details_container"))
        else:
            self.log(f"Data specification data returned for qualified name: {self.data_specification_qualified_name}")
            TextArea(f"Data specification data returned for qualified name: {self.data_specification_qualified_name}",
                     id="data_specification_details_text_area",
                     read_only=True).mount(self.query_one("#data_specification_details_container"))
            TextArea.data = self_data_specification_data


class ShopForDataScreen(Screen):
    """ Screen to Present a choice of different data sources to the user."""
    BINDINGS = [("q", "dismiss(200)", "Quit"),
                ("b", "back", "Go back")]

    CSS_PATH = "../My_Profile/my_profile.tcss"

    def __init__ (self, glossary_table, digital_product_catalog_table, data_dictionary_table, business_domain_table, data_specification_table ):
        """Initialize the ShopForDataScreen screen."""
        self.glossary_table: DataTable = glossary_table
        self.digital_product_catalog_table: DataTable = digital_product_catalog_table
        self.data_dictionary_table: DataTable = data_dictionary_table
        self.business_domain_table: DataTable = business_domain_table
        self.data_specification_table: DataTable = data_specification_table
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
            Static("Data Specification"),
            self.data_specification_table)
        yield Footer()

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
        # row_values = self.glossary_table.get_row(event.row_key)
        row_values = self.query_one("#digital_product_catalog_table", DataTable).get_row(event.row_key)
        self.log(f"Digital product row values: {row_values}")
        row_display_name = row_values[0]
        row_description = row_values[1]
        row_qualified_name = row_values[2]
        self.log(f"Row selected: {row_selected}, values: {row_values}, display name: {row_display_name}, description: {row_description}, qualified name: {row_qualified_name}")
        self.dismiss (["product", row_qualified_name, row_display_name])

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

    def action_back(self) -> None:
        """ The back option in the footer has been selected. Dismiss the screen."""
        self.dismiss(200)

    def action_quit(self) -> None:
        """ The quit option in the footer has been selected. Dismiss the screen."""
        self.dismiss(210)


class StatusScreen(ModalScreen[Any]):
    """Modal screen to display the status of the application."""
    BINDINGS = [("q", "quit", "Quit"),
                ("return", "successful", "Continue"),
                ("b", "unsuccessful", "Bad result"),
                ("c", "copy GUID to clipboard", "Copy GUID to clipboard"),
                ]

    CSS_PATH = "../My_Profile/my_profile.tcss"

    def __init__(self, status_message: str) -> None:
        """Initialize the StatusScreen screen."""
        super().__init__()
        self.status_message = status_message
        self.clipboard = PyperclipClipboard()

    def compose(self) -> ComposeResult:
        """ Compose the UI components for the StatusScreen screen."""
        yield Header(show_clock=True)
        yield TextArea(self.status_message, id="status_message_text_area", read_only=True)
        yield Footer()
        
    def action_quit(self) -> None:
        """ The quit option in the footer has been selected. Dismiss the screen."""
        self.dismiss(200)
        
    def action_unsuccessful(self) -> None:
        """ The bad result option in the footer has been selected. Dismiss the screen."""
        self.dismiss(400)
        
    def action_copy_guid_to_clipboard(self) -> None:
        """ The copy GUID to clipboard option in the footer has been selected. Copy the GUID to the clipboard."""
        # The GUID is between single ' marks in the status_message when a good result is recorded.
        match = re.search(r"'(.*?)'", self.status_message)
        self.log(f"Match: {match}")
        if match:
            guid = match.group(1)
            self.clipboard.set_data(ClipboardData(text = guid))
            self.log(f"Copied GUID to clipboard: {guid}")
        else:
            self.dismiss(400)
        self.dismiss(200)

    def action_successful(self):
        """ The successful option in the footer has been selected. Dismiss the screen."""
        self.dismiss(200)

class TechnologyTypeProcessesScreen(ModalScreen[Any]):
    """Modal screen to display technology type templates in Egeria."""
    BINDINGS = [("q", "quit", "Quit"),
                ("b", "back", "Go back"),
                ("ctl+e", "expand", "Toggle Twisties")]

    CSS_PATH = "../My_Profile/my_profile.tcss"

    def __init__ (self,
                  user_name: str,
                  user_kpts: int,
                  tech_type_name: str,
                  tech_type_description: str,
                  selected_t_option,
                  tech_type_option_selected,
                  tech_type_processes
                  ) -> None:
        """Initialize the Technology_Type_Templatess screen."""
        super().__init__()
        self.user_name = user_name
        self.karma_points = user_kpts
        self.tech_type_name = tech_type_name
        self.tech_type_description = tech_type_description
        self.selected_t_option = selected_t_option
        self.selected_t_option_selected = tech_type_option_selected
        self.tech_type_processes = tech_type_processes
        self.full_process = None
        load_app_config()

    async def on_mount(self) -> None:
        """ On Mount function of the Technology_Type_Templatess screen."""
        self.title = f"User: {self.user_name}, Karma Points: {self.karma_points}"
        self.sub_title = f"Technology Type: {self.tech_type_name}, Description: {self.tech_type_description}"

        if self.selected_t_option == "process":
            self.log(f"Processing processes, with data: {self.selected_t_option_selected}")
            # get selected process from the tech_type data
            self.log(f"Technology Type Process: {self.tech_type_processes}")
            if isinstance(self.tech_type_processes, list):
                for process in self.tech_type_processes:
                    if process.get("Governance Process Name") == self.selected_t_option_selected:
                        self.full_process = process
                        self.selected_t_process = process.get("Qualified Name")
                        self.log(f"Selected Process: {self.selected_t_process}")
                        break
                    else:
                        continue
            self.log(f"Selected Process: {self.selected_t_process}")

            for placeholder in self.selected_t_process:
                name = placeholder.get("Property Name") or None
                Description = placeholder.get("Description") or None
                Type = placeholder.get("Data Type") or None
                Example = placeholder.get("Example") or None
                Required = placeholder.get("Required") or False

                # Sanitize the name for use as a CSS ID
                safe_name = name.replace(" ", "_") if name else f"placeholder_{id(placeholder)}"
                placeholder_text: TextArea = TextArea(
                    f"{name}\n\nDescription: {Description}\nType: {Type}\nExample: {Example}\nRequired: {Required}",
                    id=f"{safe_name}_placeholder_text_area",
                    read_only=True
                )
                # Ensure TextArea is visible
                placeholder_text.styles.height = 8

                placeholder_input = Input(id=f"{safe_name}_placeholder_input", placeholder="Enter value here")
                self.log(f"Placeholder: {placeholder_text.text}\n {placeholder_input}")

                # Mount the TextArea and the associated Input field into the ScrollableContainer
                try:
                    load_point = self.query_one("#technology_type_templates_input")
                    await load_point.mount(placeholder_text, before="#submit_button")
                    await load_point.mount(placeholder_input, before="#submit_button")
                    self.log(f"Placeholder text area loaded: {placeholder_text.text}")
                    self.log(f"Placeholder input loaded: {placeholder_input}")
                    continue
                except Exception as e:
                    self.log(f"Error loading placeholder container: {e!s}")
                    self.app.dismiss(416)

    def compose(self) -> ComposeResult:
        """ Compose the UI components for the Technology_Type_Templatess screen."""
        yield Header(show_clock=True)
        yield Static("Please complete the required fields and any optional fields you prefer:")
        yield ScrollableContainer(
            Static("Technology Type Template Input"),
            Button("Submit", id="submit_button"),
            id="technology_type_templates_input"
        )
        yield Footer()

    def action_quit(self) -> None:
        """ The quit option in the footer has been selected. Dismiss the screen."""
        self.dismiss("200", )

    @on(Button.Pressed, "#submit_button")
    def handle_submit_button_pressed(self, event: Button.Pressed) -> None:
        """ The submit button has been pressed."""
        self.log(f"Submit button pressed, button: {event.button}")
        save_input_data: dict = {}
        for input_widget in self.query("Input"):
            self.log(f"Input widget: {input_widget.id}, value: {input_widget}")
            save_input_data.update({input_widget.id: input_widget})
        self.log(f"Save input data: {save_input_data}")
        self.dismiss(["input", save_input_data, self.full_process])

    @on(Input.Changed, "#technology_type_templates_input")
    def handle_input_changed(self, event: Input.Changed) -> None:
        """ The user has changed the input on the screen."""
        self.log(f"Input changed, input: {event.input}")


class TechnologyTypeTemplatesScreen(ModalScreen[Any]):
    """Modal screen to display technology type templates in Egeria."""
    BINDINGS = [("q", "dismiss(200)", "Quit"),
                ("b", "back", "Go back"),
                ("ctl+e", "expand", "Toggle Twisties")]

    CSS_PATH = "../My_Profile/my_profile.tcss"

    def __init__ (self,
                  user_name: str,
                  user_kpts: int,
                  tech_type_name: str,
                  tech_type_description: str,
                  selected_t_option,
                  tech_type_option_selected,
                  tech_type_templates
                  ) -> None:
        """Initialize the Technology_Type_Templatess screen."""
        super().__init__()
        self.user_name = user_name
        self.karma_points = user_kpts
        self.tech_type_name = tech_type_name
        self.tech_type_description = tech_type_description
        self.selected_t_option = selected_t_option
        self.selected_t_option_selected = tech_type_option_selected
        self.tech_type_templates = tech_type_templates
        self.full_template = None
        load_app_config()

    async def on_mount(self) -> None:
        """ On Mount function of the Technology_Type_Templatess screen."""
        self.title = f"User: {self.user_name}, Karma Points: {self.karma_points}"
        self.sub_title = f"Technology Type: {self.tech_type_name}, Description: {self.tech_type_description}"

        if self.selected_t_option == "template":
            self.log(f"Processing templates, with data: {self.selected_t_option_selected}")
            # get selected template from the tech_type data
            self.log(f"Technology Type Templates: {self.tech_type_templates}")
            if isinstance(self.tech_type_templates, list):
                for template in self.tech_type_templates:
                    if template.get("Catalog Template Name") == self.selected_t_option_selected:
                        self.full_template = template
                        self.selected_t_template = template.get("Placeholder Properties")
                        self.log(f"Selected Template: {self.selected_t_template}")
                        break
                    else:
                        continue
            self.log(f"Selected Template: {self.selected_t_template}")

            for placeholder in self.selected_t_template:
                name = placeholder.get("Property Name") or None
                Description = placeholder.get("Description") or None
                Type = placeholder.get("Data Type") or None
                Example = placeholder.get("Example") or None
                Required = placeholder.get("Required") or False

                # Sanitize the name for use as a CSS ID
                safe_name = name.replace(" ", "_") if name else f"placeholder_{id(placeholder)}"
                placeholder_text: TextArea = TextArea(
                    f"{name}\n\nDescription: {Description}\nType: {Type}\nExample: {Example}\nRequired: {Required}",
                    id=f"{safe_name}_placeholder_text_area",
                    read_only=True
                )
                # Ensure TextArea is visible
                placeholder_text.styles.height = 8

                placeholder_input = Input(id=f"{safe_name}_placeholder_input", placeholder="Enter value here")
                self.log(f"Placeholder: {placeholder_text.text}\n {placeholder_input}")

                # Mount the TextArea and the associateds Input field into the ScrollableContainer
                try:
                    load_point = self.query_one("#technology_type_templates_input")
                    await load_point.mount(placeholder_text, before="#submit_button")
                    await load_point.mount(placeholder_input, before="#submit_button")
                    self.log(f"Placeholder text area loaded: {placeholder_text.text}")
                    self.log(f"Placeholder input loaded: {placeholder_input}")
                    continue
                except Exception as e:
                    self.log(f"Error loading placeholder container: {e!s}")
                    self.app.dismiss(416)

    def compose(self) -> ComposeResult:
        """ Compose the UI components for the Technology_Type_Templatess screen."""
        yield Header(show_clock=True)
        yield Static("Please complete the required fields and any optional fields you prefer:")
        yield ScrollableContainer(
            Static("Technology Type Template Input"),
            Button("Submit", id="submit_button"),
            id="technology_type_templates_input"
        )
        yield Footer()

    def action_quit(self) -> None:
        """ The quit option in the footer has been selected. Dismiss the screen."""
        self.dismiss("200", )

    @on(Button.Pressed, "#submit_button")
    def handle_submit_button_pressed(self, event: Button.Pressed) -> None:
        """ The submit button has been pressed."""
        self.log(f"Submit button pressed, button: {event.button}")
        save_input_data: dict = {}
        for input_widget in self.query("Input"):
            self.log(f"Input widget: {input_widget.id}, value: {input_widget}")
            save_input_data.update({input_widget.id: input_widget})
        self.log(f"Save input data: {save_input_data}")
        self.dismiss(["input", save_input_data, self.full_template])

    @on(Input.Changed, "#technology_type_templates_input")
    def handle_input_changed(self, event: Input.Changed) -> None:
        """ The user has changed the input on the screen."""
        self.log(f"Input changed, input: {event.input}")


class TechnologyTypeOptionsScreen(ModalScreen):
    """ Modal screen to display a technology type's templates and processes."""
    BINDINGS = [("q", "dismiss", "Quit"),
                ("b", "back", "Go back"),
                ("ctl+s", "Select", "tech_type_option_select")]

    CSS_PATH = "../My_Profile/my_profile.tcss"

    def __init__(self, tech_type_guid: str,
                       tech_type_name: str,
                       tech_type_description: str,
                       user_name: str,
                       user_pwd:str,
                       user_kpts: int,
                       tech_type_templates: list[dict],
                       tech_type_processes: list[dict]) -> None:
        """Initialize the TechnologyTypeOptions screen with a technology type's templates and processes."""
        super().__init__()
        self.selected_process_index = None
        self.tech_type_guid = tech_type_guid
        self.tech_type_name = tech_type_name
        self.tech_type_description = tech_type_description
        self.user_name = user_name
        self.user_password = user_pwd
        self.karma_points = user_kpts
        self.tech_type_templates = tech_type_templates
        self.tech_type_processes = tech_type_processes
        self.selected_template_guid = None
        self.selected_process_guid = None
        self.option_type_selected = None
        self.selected_template = None
        self.selected_template_index = None
        self.selected_template_data = None
        self.selected_process = None
        self.selected_process_data = None

        load_app_config("config/config.json")
        app_config = settings.Environment
        app_user = settings.User_Profile

        if not self.user_name:
            self.user_name = app_user.user_name or "garygeeke"
            self.user_password = app_user.user_pwd or "secret"

    def compose(self) -> ComposeResult:

        """ Compose the UI components for the TechnologyTypeOptions screen."""
        yield Header(show_clock=True)
        yield Static(f"Description: {self.tech_type_description}")
        yield ScrollableContainer(
            Static(f"Technology Type: {self.tech_type_name}"),
            Container(
                Static("Select a template or process to continue."),
                Static(f"Templates", id="number_of_templates_label"),
                ScrollableContainer(
                    Static("Available Templates", id="template_options_label"),
                    OptionList(id="template_options"),
                    Button("Select Template", id="select_template_btn"),
                    id="template_options_container"),
                Static(f"Processes:", id="number_of_processes_label"),
                ScrollableContainer(
                    Static("Available Processes",id="process_options_label"),
                    OptionList(id="process_options"),
                    id="process_options_container"),
                Button(
                    "Select Process",
                    id="select_process_btn")))
        yield Footer()

    async def on_mount(self) -> int:
        """Mount the TechnologyTypeOptions screen."""
        self.title =  f"User: {self.user_name}, Karma Points: {self.karma_points}"
        self.sub_title = f"Technology Type: {self.tech_type_name}, Description: {self.tech_type_description}"
        self.log(f"Technology Type: {self.tech_type_name}, Description: {self.tech_type_description}")

        for widget in self.query():
            self.log(f"Widgets: {widget}")

        self.log(f"Templates: {self.tech_type_templates}, Processes: {self.tech_type_processes}")
        self.log(f"Templates Type: {type(self.tech_type_templates)}, Processes Type: {type(self.tech_type_processes)}")

        if self.tech_type_templates and self.tech_type_templates != "None":
            for t in self.tech_type_templates:
                try:
                    self.log(f"Template: {t}")
                    templates = self.query_one("#template_options", OptionList).add_option(
                        Option(t.get("Catalog Template Name")))
                    self.log(f"Added option: {t.get('Catalog Template Name')}")
                    await templates.mount(after=self.query_one("#template_options_label"))
                    self.log(f"Mounted option")
                    self.query_one("#select_template_btn", Button).disabled = False
                    self.log(f"Enabled the template button")
                except NoMatches as e:
                    try:
                        templates: OptionList = OptionList(id="template_options")
                        await templates.mount(after=self.query_one("#template_options_label"))
                        templates.add_option(Option(t.get("Catalog Template Name")))
                        templates.refresh()
                        self.query_one("#select_template_btn", Button).disabled = False
                        continue
                    except Exception as e:
                        self.log(f"Error creating template option list: {e}, (410")
                        return (410)
                except Exception as e:
                    self.log(f"Error creating template option list: {e} (411)")
                    return (411)
        else:
            try:
                self.log(f" No Templates")
                templates = self.query_one("#template_options", OptionList).add_option(
                    Option("No Templates Found for this Tech Type"))
                await templates.mount(after=self.query_one("#template_options_label"))
                self.query_one("#select_template_btn", Button).disabled = True
            except NoMatches as e:
                try:
                    templates: OptionList = OptionList(id="template_options")
                    await templates.mount(after=self.query_one("#template_options_label"))
                    templates.add_option(Option("No Templates found for this Tech Type"))
                    self.query_one("#select_template_btn", Button).disabled = True
                except Exception as e:
                    self.log(f"Error creating template option list: {e}")
                    return (409)
            except Exception as e:
                self.log(f"Error creating template option list: {e}")
                return (408)

        if self.tech_type_processes and self.tech_type_processes != "None":
            for p in self.tech_type_processes:
                try:
                    self.log(f"Process: {p}")
                    processes = self.query_one("#process_options", OptionList).add_option(
                        Option(p.get("Governance Process Name")))
                    await processes.mount(after=self.query_one("#process_options_label"))
                    self.query_one("#select_process_btn", Button).disabled = False
                except NoMatches as e:
                    try:
                        processes: OptionList = OptionList(id="process_options")
                        await processes.mount(after=self.query_one("#process_options_label"))
                        processes.add_option(Option(p.get("Governance Process Name")))
                        processes.refresh()
                        self.query_one("#select_process_btn", Button).disabled = False
                    except Exception as e:
                        self.log(f"Error creating process option list: {e}")
                        return (407)
                except Exception as e:
                    self.log(f"Error creating process option list: {e}")
                    return (406)
        else:
            try:
                self.log(f" No Processes")
                processes = self.query_one("#process_options", OptionList).add_option(
                    Option("No processes found for this Tech Type"))
                await processes.mount(after=self.query_one("#process_options_label"))
                self.query_one("#select_process_btn", Button).disabled = True
            except NoMatches as e:
                try:
                    processes: OptionList = OptionList(id="process_options")
                    await processes.mount(after=self.query_one("#process_options_label"))
                    processes.add_option(Option(" No Processes found for this Tech Type"))
                    processes.refresh()
                    self.query_one("#select_process_btn", Button).disabled = True
                except Exception as e:
                    self.log(f"Error creating process option list: {e}")
                    return (405)
            except Exception as e:
                self.log(f"Error creating process option list: {e}")
                return (404)

        return(200)

    @on(OptionList.OptionHighlighted, "#template_options")
    def handle_template_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        """Handle the highlighting of an option in the template option list."""
        self.log(f"Template option highlighted: {event.option}")
        self.log(f"Option index: {event.option_index}, Option list: {event.option_list.name}")
        self.selected_template_index = event.option_index
        selected_option = event.option
        self.selected_template = selected_option.prompt
        self.log(f"Highlighted Template: {self.selected_template}, index: {self.selected_template_index}")

    @on(OptionList.OptionSelected, "#template_options")
    def handle_template_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle the selection of an option from the template or process option lists."""
        self.log(f"Template selected: {event.option}")
        self.log(f"Option index: {event.option_index}, Option list: {event.option_list.name}")
        self.option_type_selected = event.option_list.name
        self.selected_template_index = event.option_index
        selected_option = event.option
        self.selected_template = selected_option.prompt
        self.log(f"Selected Option List: {self.option_type_selected}, template: {self.selected_template}, index: {self.selected_template_index}")

    @on(OptionList.OptionHighlighted, "#process_options")
    def handle_process_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        """Handle the highlighting of an option in the process option list."""
        self.log(f"Process option highlighted: {event.option}")
        self.log(f"Option index: {event.option_index}, Option list: {event.option_list.name}")
        self.selected_process_index = event.option_index
        selected_option = event.option
        self.selected_process = selected_option.prompt
        self.log(f"Highlighted Process: {self.selected_process}, index: {self.selected_process_index}")

    @on(OptionList.OptionSelected, "#process_options")
    def handle_process_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle the selection of an option from the template or process option lists."""
        self.log(f"Process selected: {event.option}")
        self.log(f"Option index: {event.option_index}, Option list: {event.option_list.name}")
        self.option_type_selected = event.option_list.name
        self.selected_process_index = event.option_index
        selected_option = event.option
        self.selected_process = selected_option.prompt
        self.log(f"Selected Option List: {self.option_type_selected}, template: {self.selected_process}, index: {self.selected_process_index}")

    def action_back(self) -> None:
        """Handle the back button press."""
        self.dismiss("back")

    @on(Button.Pressed, "#select_template_btn")
    def handle_template_selected(self, event: Button.Pressed) -> None:
        """Handle the selection of a template option."""
        if self.selected_template is None:
            return
        self.log(f"Template option selected: {self.selected_template}")
        self.dismiss(["template", self.selected_template])

    @on(Button.Pressed, "#select_process_btn")
    def handle_process_selected(self, event: Button.Pressed) -> None:
        """Handle the selection of a process option."""
        if self.selected_process is None:
            return
        self.log(f"Process option selected: {self.selected_process}")
        self.dismiss(["process", self.selected_process])


class TechnologyTypesScreen(ModalScreen):
    """Modal screen to display technology types in Egeria."""
    BINDINGS = [("q", "dismiss(200)", "Quit"),
                ("ctl+e", "expand", "Toggle Twisties")]

    CSS_PATH = "../My_Profile/my_profile.tcss"

    def __init__(self, ttlist, user_name, user_pwd, user_kpts):
        """Initialize the TechnologyTypes screen with a list of technology types."""
        super().__init__()
        self.tech_type_list = ttlist
        self.user_name = user_name
        self.user_password = user_pwd
        self.karma_points = user_kpts
        self.tech_type_tree: Tree[str] = Tree(label="Technology Types", id="technology_types_tree")
        self.tech_type_tree.root.expand()
        self.tech_type_tree.auto_expand = True
        self.selected_t_node = None
        self.selected_t_node_label = None
        self.node_id = None
        self.node_status = "expanded"
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        # config_logging()
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"

    def on_mount(self) -> None:
        self.title = f"User: {self.user_name}"
        self.sub_title = "Select a technology type"

    def compose(self) -> ComposeResult:
        """ Compose and display the technology type screen"""
        self.tech_type_tree.refresh()
        if self.tech_type_list:
            self.log(f"Technology types: {self.tech_type_list}, type: {type(self.tech_type_list)}")
            self.render_tech_type_hierarchy_to_tree(self.tech_type_list, self.tech_type_tree)
        else:
            self.tech_type_tree.root.add("No technology types found", expand=True)
        self.tech_type_tree.refresh()
        self.log(f"Technology types tree: {self.tech_type_tree}")

        yield Header(show_clock=True)
        yield ScrollableContainer(
            Static("Display technology types in Egeria"),
            self.tech_type_tree,
            Button("Select", id="select_tech_type_btn"),
            id="technology_types_table"
        )
        yield Footer()

    def action_quit(self) -> None:
        """ The quit option in the footer has been selected. Dismiss the screen."""
        self.dismiss("200")

    @on(Button.Pressed, "#select_tech_type_btn")
    def handle_select_tech_type(self, event: Button.Pressed) -> str|None:
        """ The select button on the screen has been pressed."""
        self.log(f"Select button pressed, button: {event.button}")
        if self.selected_t_node:
            self.log(f"Selected node: {self.selected_t_node}, label: {self.selected_t_node.label}")
            self.dismiss(str(self.selected_t_node.label))
        else:
            return "No technology type selected"

    @on(Tree.NodeSelected)
    def handle_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """ The user has selected a node in the tree. """
        self.log(f"Tree node selected, node: {event.node}")
        self.selected_t_node = event.node
        self.selected_t_node_label = event.node.label
        return

    @on(Tree.NodeCollapsed)
    def handle_tree_node_collapsed(self, event: Tree.NodeCollapsed) -> None:
        # handle the twisty to close a node in the tree
        # logger.debug(f"TreeNodeCollapsed: {event.node.id}")
        self.node_id = str(event.node.id)
        self.node_status = "collapsed"

    @on(Tree.NodeExpanded)
    def handle_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        # handle the twisty to open a node in the tree
        # logger.debug(f"TreeNodeExpanded: {event.node.id}")
        self.node_id = str(event.node.id)
        self.node_status = "expanded"

    def action_expand(self):
        # handle the hot key to expand/collapse all nodes in the tree (see bindings)
        self.tech_type_tree = self.query_one("#technology_types_tree", Tree)
        if self.node_status == "collapsed":
            self.tech_type_tree.root.expand_all()
        else:
            self.tech_type_tree.root.collapse_all()
        return

    def render_tech_type_hierarchy_to_tree(self,
            data: dict | list[dict],
            tree_or_node: Tree[str] | TreeNode[str],
            label_attr: str = "displayName",
            guid_attr: str = "guid",
            children_attr: str = "subTypes"
    ) -> None:
        """Recursively render a DICT) hierarchy into a Textual Tree.

        Args:
            data: The data structure from pyegeria.get_tech_type_hierarchy.
            tree_or_node: The Tree object or a TreeNode to add children to.
            label_attr: The attribute in the data for the node label.
            guid_attr: The attribute in the data for the node data (GUID).
            children_attr: The attribute in the data containing the list of children.
        """
        if isinstance(data, list):
            for item in data:
                self.render_tech_type_hierarchy_to_tree(item, tree_or_node, label_attr, guid_attr, children_attr)
            return

        if not isinstance(data, dict):
            return

        label = str(data.get(label_attr) or data.get("Display Name") or "Unknown")
        guid = str(data.get(guid_attr) or data.get("GUID") or "")

        # If it's a Tree, we add to root. If it's a TreeNode, we add to it.
        if isinstance(tree_or_node, Tree):
            node = tree_or_node.root.add(label, data=guid, expand=True)
        else:
            node = tree_or_node.add(label, data=guid, expand=True)

        children = data.get(children_attr)
        if children and isinstance(children, list):
            for child in children:
                self.render_tech_type_hierarchy_to_tree(child, node, label_attr, guid_attr, children_attr)


class CreateProfileScreen(ModalScreen[int]):
    """Modal screen to create a new user profile in Egeria.

    Dismisses with:
      200 on success
      4xx on failure
    """

    BINDINGS = [("q", "dismiss(200)", "Quit")]
    CSS_PATH = "../My_Profile/my_profile.tcss"

    def __init__(self):
        super().__init__()
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        # config_logging()
        self.karma_points = 0

        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server
        self.platform_url = app_config.egeria_platform_url
        print("Platform:", app_config.egeria_platform_url)
        print("View Server:", app_config.egeria_view_server)

    def on_mount(self) -> None:
        self.title = f"User: {self.user_name}, Karma Points: {self.karma_points}"
        self.sub_title = f"Create Egeria Profile for user: {self.user_name}"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Create a new profile in Egeria")
        yield ScrollableContainer(
            Static("Fill in your information below:"),
            Input(placeholder="Courtesy Title", id="user_title"),
            Input(placeholder="Given Names", id="user_given_names"),
            Input(placeholder="Family Name", id="user_family_name"),
            Input(placeholder="Preferred Name", id="user_preferred_name"),
            Input(placeholder="Pronouns", id="user_pronouns"),
            Input(placeholder="Job Title", id="user_job_title"),
            Input(placeholder="Description", id="user_description"),
            Input(placeholder="Employee ID", id="user_employee_id"),
            Input(placeholder="Preferred Language", id="user_preferred_language"),
            Input(placeholder="Resident Country", id="user_resident_country"),
            Input(placeholder="Time Zone", id="user_time_zone"),
            Button("Create Profile", id="create_profile_btn"),
            id="create_profile_form",
        )

        yield Footer()

    @on(Button.Pressed, "#create_profile_btn")
    def create_profile(self) -> int:
        """Create a new profile in Egeria from data provided in Input fields."""

        self.new_element_request_body:dict = {"class": "NewElementRequestBody",
                                              "isOwnAnchor": True,
                                              "properties": {
                                                  "class": "PersonProperties",
                                                  "qualifiedName": "Person" + self.query_one("#user_employee_id",
                                                                                             Input).value +
                                                                   self.query_one("#user_resident_country",
                                                                                  Input).value +
                                                                   self.query_one("#user_given_names", Input).value +
                                                                   self.query_one("#user_family_name", Input).value,
                                                  "displayName": self.query_one("#user_preferred_name", Input).value,
                                                  "courtesyTitle": self.query_one("#user_title", Input).value,
                                                  "initials": "PAT",
                                                  "givenNames": self.query_one("#user_given_names", Input).value,
                                                  "surname": self.query_one("#user_family_name", Input).value,
                                                  "fullName": self.query_one("#user_preferred_name", Input).value,
                                                  "pronouns": self.query_one("#user_pronouns", Input).value,
                                                  "jobTitle": self.query_one("#user_job_title", Input).value,
                                                  "employeeNumber": self.query_one("#user_employee_id", Input).value,
                                                  "employeeType": "Full-Time",
                                                  "preferredLanguage": self.query_one("#user_preferred_language",
                                                                                      Input).value,
                                                  "residentCountry": self.query_one("#user_resident_country",
                                                                                    Input).value,
                                                  "timeZone": self.query_one("#user_time_zone", Input).value,
                                                  "description": self.query_one("#user_description", Input).value,
                                              }
                                            }
        try:
            new_profile_inst = MyProfile(self.app.view_server, self.app.platform_url, self.app.user, self.app.password)
            new_profile_guid = new_profile_inst.add_my_profile(self.new_element_request_body)
            self.log(f"Profile created with GUID: {new_profile_guid}")
            self.dismiss(200)
            return(200)
        except PyegeriaException as e:
            self.log(f"Error creating profile: {e!s} | request={self.new_element_request_body}")
            self.dismiss(401)
            return(401)

    def action_quit(self) -> int:
        self.dismiss(200)
        return(200)


class MyProfileTui(App):
    """My Profile App.

    Retrieves a user's profile from Egeria and displays current work items.
    If no profile is found, offers a UI to create one.
    """

    BINDINGS = [("q", "quit", "Quit")]
    CSS_PATH = "../My_Profile/my_profile.tcss"

    SCREENS = {
        "create_profile": CreateProfileScreen,
        "tech_types": TechnologyTypesScreen,
        "tech_type_options": TechnologyTypeOptionsScreen,
        "tech_type_templates": TechnologyTypeTemplatesScreen,
        "tech_type_processes": TechnologyTypeProcessesScreen,
        "status": StatusScreen,
        "shop_4_data": ShopForDataScreen,
        "overview": SelectionOverviewScreen
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.contribution_record = None
        self.heading = "My_Profile"
        self.subheading = "Egeria Profile for current user"
        self.description = "Display the user related items for the current user."
        load_app_config("config/config.json")
        app_config = settings.Environment
        app_user = settings.User_Profile
        # config_logging()
        print("Platform:", app_config.egeria_platform_url)
        print("View Server:", app_config.egeria_view_server)
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"

        # Ensure compose() is safe before data loads
        self.actor_profile: dict = {}
        self.projects = []
        self.communities = []
        self.roles = []
        self.actions = []
        self.teams = []
        self.other_function_list = []
        self.tech_type_json: str
        self.tech_type_response = None
        self.tech_type_list = []
        self.tech_type_guid = ""
        self.tech_type_name = ""
        self.tech_type_description = ""
        self.selected_t_node = None
        self.selected_t_node_label = None
        self.karma_points = 0
        self.tech_type_templates = [{}]
        self.tech_type_processes = [{}]
        self.full_template = None
        self.glossary_data_extract = None
        self.business_glossary_data_extract = None
        self.display_glossary_data_extract = None
        self.digital_glossary_data_extract = None

    def compose(self) -> ComposeResult:

        # Create tables up-front; populate them in on_mount()
        self.projects_table = DataTable(id="projects_table")
        self.communities_table = DataTable(id="communities_table")
        self.roles_table = DataTable(id="roles_table")
        self.actions_table = DataTable(id="actions_table")
        self.teams_table = DataTable(id="teams_table")
        self.user_identity_table = DataTable(id="user_identity_table")
        self.other_function_list = OptionList(id="other_function_list")

        # place widgets into grid on screen, note sequence determines position!
        yield Header(show_clock=True)

        yield ScrollableContainer(
            Static("Projects"),
            self.projects_table
        )

        yield ScrollableContainer(
            Static("Communities"),
            self.communities_table
        )

        yield ScrollableContainer(
            Static(f"Other Functions"),
            Static(f"[b]Select a function[/b]"),
            OptionList(
                Option("User Identities", disabled=True),
                Option("Catalogs/Shop for Data"),
                Option("Edit Profile", disabled=True),
                Option("Subscriptions", disabled=True),
                Option("Technology Types"),
                Option("Update Profile", disabled=True),
                Option("User Bookmarks", disabled=True),
                id="other_function_list"
            ),
            id="other_function_container"
        )

        yield ScrollableContainer(
            Static("Roles"),
            self.roles_table
        )

        yield ScrollableContainer(
            Static("Teams"),
            self.teams_table
        )

        yield ScrollableContainer(
            Static("Actions"),
            self.actions_table
        )
        yield Footer()

    async def on_mount(self) -> None:
        """Load profile; if missing, prompt to create it; then populate tables."""
        # DOMInfo.attach_to(self)
        # Initiate clipboard session
        clipboard = PyperclipClipboard()

        await self._load_or_create_profile()
        await self._populate_tables()


    async def _load_or_create_profile(self) -> None:
        try:
            #instantiate the class
            self.my_profile_inst = MyProfile(self.view_server, self.platform_url, self.user_name, self.user_password)
            self.my_profile_inst.create_egeria_bearer_token(self.user_name, self.user_password)
            #retrieve the profile
            self.my_profile_data = await self.my_profile_inst._async_get_my_profile(
                report_spec="My-User-MD",
                output_format="DICT",
                )
            self.log(f"retrieve profile result: {self.my_profile_data}")
        except (PyegeriaException) as e:
            self.log(f"Error retrieving profile: {e!s}")
            print_basic_exception(e)
            self.exit(402)
            return

        if self.my_profile_data == []:
            self.log(f"Error retrieving profile. Prompting to create one...")
            self.log(f"To create a profile you must have a valid userid in the system, please contact your system administrator to create one if needed")
            await self.push_screen(CreateProfileScreen(), callback = self.new_profile_return)
        else:
            self.new_profile_return(200)

    def new_profile_return(self, result: int) -> None:
        """ This function handles either the return from the create new profile screen or
            when the user already has a profile continue processing """
        self.log(f"Profile creation result: {result}")
        if not result or result != 200:
            self.log(f"Profile creation cancelled/failed; return: {result}, exiting.")
            self.exit(403)
            return

        self.result = result

        # Retry after creation if necessary
        try:
            self.user_profile_struct = self.my_profile_inst.get_my_profile(
                output_format="DICT",
                report_spec="My-User-MD",
            )
            self.log(f"Profile retrieved successfully: {self.user_profile_struct}")
        except PyegeriaException as e2:
            self.log(f"Error retrieving user profile: {e2!s}")
            self.exit(412)
            return
        if self.user_profile_struct is []:
            self.log(f"Error retrieving user profile. Exiting.")
            self.exit(413)
            return

        # strip out the individual profile elements
        self.user_profile = self.user_profile_struct[0]
        self.contribution_record = self.user_profile.get("Contribution Record") or {}
        for c in self.contribution_record:
            self.karma_points = c.get("Karma Points") or 0
            break
        self.my_projects_data = self.user_profile.get("Projects") or []
        self.my_teams_data = self.user_profile.get("Teams") or []
        self.my_communities_data = self.user_profile.get("Communities") or []
        self.my_roles_data = self.user_profile.get("Roles") or []
        self.my_actions_data = self.user_profile.get("Actions") or []
        self.log(f"Contribution Record: {self.contribution_record}")
        self.log(f"Karma Points: {self.karma_points}")
        self.log(f"my_projects_data: {self.my_projects_data}")
        self.log(f"my_teams_data: {self.my_teams_data}")
        self.log(f"my_communities_data: {self.my_communities_data}")
        self.log(f"my_roles_data: {self.my_roles_data}")
        self.log(f"my_actions_data: {self.my_actions_data}")
        # User Identities
        try:
            self.user_identities = self.my_profile_inst.get_my_profile(
                report_spec="User-Identities",
                output_format="DICT",
            )
            self.log(f"User-Identities: {self.user_identities}, type: {type(self.user_identities)}")
        except PyegeriaException as e:
            self.log(f"Error retrieving User-Identities: {e!s}")
            self.user_identities = {}

        # Normalize expected keys
        self.full_name = self.user_profile.get("Full Name") or ""
        self.sub_title = f"{self.full_name} ({self.user_profile.get('User ID')}, Karma Points: {self.karma_points})"
        self.projects = self.my_projects_data or []
        self.communities = self.my_communities_data or []
        self.roles = self.my_roles_data or []
        self.actions = self.user_profile.get("actions") or []
        self.teams = self.my_teams_data or []
        if isinstance(self.user_identities, list):
            self.user_identity = self.user_identities
        else:
            self.user_identity = self.user_identities.get("User-Identities") or []

    async def _populate_tables(self) -> None:
        """Populates tables from normalized profile data"""
        assert self.projects_table is not None
        assert self.communities_table is not None
        assert self.roles_table is not None
        assert self.actions_table is not None
        assert self.user_identity_table is not None
        assert self.teams_table is not None

        self.projects_table.clear(columns=True)
        self.projects_table.add_columns("Project Name", "Description", "Qualified Name")

        self.communities_table.clear(columns=True)
        self.communities_table.add_columns("Assignment Type", "Community Name", "Description", "Qualified Name")

        self.roles_table.clear(columns=True)
        self.roles_table.add_columns("Role Name", "Description","GUID")

        self.teams_table.clear(columns=True)
        self.teams_table.add_columns("Assignment Type", "Team Name", "Description","GUID")

        self.actions_table.clear(columns=True)
        self.actions_table.add_columns("Action Name", "Status", "Description")

        self.user_identity_table.clear(columns=True)
        self.user_identity_table.add_columns("Display Name", "User ID", "Distinguished Name")

        # Populate rows
        for p in self.projects if isinstance(self.projects, list) else []:
            self.projects_table.add_row(
                str(p.get("Name", "")),
                str(p.get("Description", "")),
                str(p.get("Qualified Name", "")),
            )

        for c in self.communities if isinstance(self.communities, list) else []:
            self.communities_table.add_row(
                str(c.get("Assignment Type", "")),
                str(c.get("Display Name", "")),
                str(c.get("Description", "")),
                str(c.get("Qualified Name", ""))
            )

        for r in self.roles if isinstance(self.roles, list) else []:
            self.roles_table.add_row(
                str(r.get("Name", "")),
                str(r.get("Type", "")),
                str(r.get("GUID", "")),
            )

        for a in self.actions if isinstance(self.actions, list) else []:
            self.actions_table.add_row(
                str(a.get("Display Name", "")),
                str(a.get("Description", "")),
            )

        for t in self.teams if isinstance(self.teams, list) else []:
            self.teams_table.add_row(
                str(t.get("Assignment Type", "")),
                str(t.get("Name", "")),
                str(t.get("Description", "")),
                str(t.get("GUID", "")),
            )

    def action_quit(self) -> None:
        # quit selected by user, so exit app
        self.exit(200)

    @on(OptionList.OptionSelected, "#other_function_list")
    async def handle_option_selected(self, event: OptionList.OptionSelected):
        # option selected by user
        selected_option = event.option.prompt
        selected_option_id = event.option.id
        self.log(f"Selected option: {selected_option} ({selected_option_id})")
        if selected_option == "Technology Types":
            self.log("Fetching technology types...")
            await self.fetch_technology_types()
            self.log(f"Tech Type Response: {self.tech_type_response} | {self.tech_type_list}")
            if self.tech_type_response == []:
                self.log("No technology types found.")
                self.exit(200)
            elif len(self.tech_type_response) == 3 and int(self.tech_type_response) >= 400:
                self.log("Error fetching technology types.")
                self.exit(int(self.tech_type_response))
            self.log("Technology types fetched successfully.")
            self.log("Displaying technology types...")
            await self.push_screen(TechnologyTypesScreen(self.tech_type_list, self.user_name, self.user_password, self.karma_points), callback=self.tech_type_callback)
            self.log("Technology types displayed successfully.")
        elif selected_option == "User Identities":
            pass
        elif selected_option == "Catalogs/Shop for Data":
            """ Push new Screen, Show Glossaries, Digital Product Catalogs, Data Dictionaries and
                Business Domains, allow the user to select from one of the 4 categories and use that selection to
                display a list of available collections of the chosen type and allow the user to subscribe to them
                """

            # start by gathering the data using Pyegeria to access the Egeria backend servers

            # Glossaries
            glossary_table: DataTable = DataTable(id="glossary_table")
            glossary_table.add_columns("Glossary Name", "Description", "Qualified Name")
            glossary_table.cursor_type = "row"
            glossary_table.zebra_stripes = True
            try:
                self.glossary_data = exec_report_spec(format_set_name="Glossaries",
                                                       output_format="DICT",
                                                       params = {"search_string" : "*"},
                                                       view_server=self.view_server,
                                                       view_url=self.platform_url,
                                                       user=self.user_name,
                                                       user_pass=self.user_password)
            except PyegeriaException as e:
                print_basic_exception(e)
                self.log(f"Error retrieving glossary details: {e!s}")
                self.exit(420)
                return(420)
            self.log(f"Glossary data returned: {self.glossary_data}")
            self.glossary_data_extract = self.glossary_data.get("data") or []
            self.log(f"Glossary data extracted: {self.glossary_data_extract}")
            if self.glossary_data_extract == []:
                self.log(f"No glossary data found for search string: {self.selected_t_node}")
                glossary_table.add_row("No glossaries found", "No data returned from Egeria", "")
            else:
                for g in self.glossary_data_extract:
                    glossary_table.add_row(g.get("Display Name"), g.get("Description"), g.get("Qualified Name"))
                    continue

            # Digital Product Catalogs
            digital_product_catalog_table: DataTable = DataTable(id="digital_product_catalog_table")
            digital_product_catalog_table.add_columns("Digital Product Catalog Name", "Description", "Qualified Name")
            digital_product_catalog_table.cursor_type = "row"
            digital_product_catalog_table.zebra_stripes = True
            try:
                self.digital_product_catalog_data = exec_report_spec(format_set_name="Digital-Product-Catalog",
                                                                     output_format="DICT",
                                                                     params = {"search_string" : "*"},
                                                                     view_server=self.view_server,
                                                                     view_url=self.platform_url,
                                                                     user=self.user_name,
                                                                     user_pass=self.user_password)
            except PyegeriaException as e:
                self.log(f"Error retrieving digital product catalog details: {e!s}")
                self.exit(421)
                return(421)
            self.log(f"Digital Product Catalog data returned: {self.digital_product_catalog_data}")
            self.digital_product_catalog_data_extract = self.digital_product_catalog_data.get("data") or []
            self.log(f"Digital Product Catalog data extracted: {self.digital_product_catalog_data_extract}")
            if self.digital_product_catalog_data_extract == []:
                self.log(f"No digital product catalog data found for user: {self.user_name}")
                digital_product_catalog_table.add_row("No digital product catalogs found", "No data returned from Egeria", "")
            else:
                for catalog_item in self.digital_product_catalog_data_extract:
                    digital_product_catalog_table.add_row(catalog_item["Display Name"],
                                                          catalog_item["Description"],
                                                          catalog_item["Qualified Name"])
                    continue

            # Data Dictionaries
            data_dictionary_table: DataTable = DataTable(id="data_dictionary_table")
            data_dictionary_table.add_columns("Data Dictionary Name", "Description", "Qualified Name")
            data_dictionary_table.cursor_type = "row"
            data_dictionary_table.zebra_stripes = True
            try:
                self.data_dictionary_data = exec_report_spec(format_set_name="Data-Dictionaries",
                                                           output_format="DICT",
                                                           params = {"search_string" : "*"},
                                                           view_server=self.view_server,
                                                           view_url=self.platform_url,
                                                           user=self.user_name,
                                                           user_pass=self.user_password)
            except PyegeriaException as e:
                self.log(f"Error retrieving data dictionary details: {e!s}")
                self.exit(422)
                return(422)
            self.data_dictionary_data_extract = self.data_dictionary_data.get("data") or []
            if self.data_dictionary_data_extract == []:
                self.log(f"No data dictionary details found for user: {self.user_name}")
                data_dictionary_table.add_row("No data dictionaries found", "No data returned from Egeria", "")
            else:
                self.log(f"Found {self.data_dictionary_data_extract} data dictionaries for user {self.user_name}")
                data_dictionary_table.add_row("Display Name", "Description", "Qualified Name")
                for dictionary in self.data_dictionary_data_extract:
                    data_dictionary_table.add_row(dictionary.get("Display Name", ""),
                                                       dictionary.get("Description", ""),
                                                       dictionary.get("Qualified Name", ""))
                    continue

            # Business Domains
            business_domain_table: DataTable = DataTable(id="business_domain_table")
            business_domain_table.add_columns("Business Area Name", "Type Name", "GUID")
            business_domain_table.cursor_type = "row"
            business_domain_table.zebra_stripes = True
            try:
                self.business_domain_data = exec_report_spec(format_set_name="BusinessCapabilities",
                                                           output_format="DICT",
                                                           params = {"search_string" : "*"},
                                                           view_server=self.view_server,
                                                           view_url=self.platform_url,
                                                           user=self.user_name,
                                                           user_pass=self.user_password)
            except PyegeriaException as e:
                self.log(f"Error retrieving business domain details: {e!s}")
                self.exit(423)
                return(423)
            self.business_domain_data_extract = self.business_domain_data.get("data") or []
            if self.business_domain_data_extract == []:
                self.log(f"No business domains found for user {self.user_name}")
                business_domain_table.add_row("No business domains found", "No data returned from Egeria", "")
            else:
                self.log(f"Found {self.business_domain_data_extract} business domains for user {self.user_name}")
                # business_domain_table.add_row("Business Domain Name", "Description", "GUID")
                for domain in self.business_domain_data_extract:
                    business_domain_table.add_row(domain.get("Qualified Name", ""),
                                                       domain.get("Type Name", ""),
                                                       domain.get("GUID", ""))
                    continue

            # Data Specifications
            data_specification_table: DataTable = DataTable(id="data_specification_table")
            data_specification_table.add_columns("Display Name", "Description", "Qualified Name")
            data_specification_table.cursor_type = "row"
            data_specification_table.zebra_stripes = True
            try:
                self.data_specification_data = exec_report_spec(format_set_name="Data-Specifications",
                                                                 output_format="DICT",
                                                                 params = {"search_string": "*"},
                                                                 view_server=self.view_server,
                                                                 view_url=self.platform_url,
                                                                 user=self.user_name,
                                                                 user_pass=self.user_password)
            except PyegeriaException as e:
                self.log(f"Error retrieving data specification details: {e!s}")
                self.exit(423)
                return (423)

            if isinstance(self.data_specification_data, dict):
                self.data_specification_data_extract = self.data_specification_data.get("data")
            elif isinstance(self.data_specification_data, list):
                self.data_specification_data_extract = self.data_specification_data
            else:
                self.data_specification_data_extract = self.data_specification_data.get("Data-Specifications") or []

            if self.data_specification_data_extract == [] or self.data_specification_data_extract == {} or self.data_specification_data_extract == None:
                self.log(f"No data specifications found for user {self.user_name}")
                data_specification_table.add_row("No data specifications found", "No data returned from Egeria", "")
            else:
                self.log(f"Found {self.data_specification_data_extract} data specifications for user {self.user_name}")

                for spec in self.data_specification_data_extract:
                    data_specification_table.add_row(spec.get("Display Name", ""),
                                                  spec.get("Description", ""),
                                                  spec.get("Qualified Name", ""))
                    continue

            # hand the data to the Screen for displaying
            await self.push_screen(ShopForDataScreen(glossary_table, digital_product_catalog_table, data_dictionary_table, business_domain_table, data_specification_table ), callback = self.shop_for_data_callback)

        elif selected_option == "User Bookmarks":
            pass
        elif selected_option == "Subscriptions":
            pass
        else:
            pass

    async def tech_type_callback(self, result) -> int:
        """ Callback for Technology Types screen
             If the result is int (4xx) it indicates an error in the screen
             if the result is str it contains the GUID of the selected technology type
        """
        #clear local data fields
        tech_type_description = ""
        self.tech_type_data = {}
        self.tech_type_data_extracted = {}
        self.tech_type_templates = []
        self.tech_type_processes = []
        # check that we got a valid result from the screen
        if not result or isinstance(result, int) :
            self.log(f"Technology Types screen cancelled/failed; return: {result}, exiting.")
            self.exit(result)
            return (result)
        self.selected_t_node = str(result)
        self.log(f"Technology Types screen returned: {self.selected_t_node}")
        # Request details for selected tech type
        try:
            self.tech_type_data = exec_report_spec(format_set_name="Tech-Type-Details-MD",
                                                   output_format="DICT",
                                                   params={"search_string": self.selected_t_node, "filter_string": self.selected_t_node},
                                                   view_server=self.view_server,
                                                   view_url=self.platform_url,
                                                   user=self.user_name,
                                                   user_pass=self.user_password)
        except PyegeriaException as e:
            print_basic_exception(e)
            self.log(f"Error retrieving technology type details: {e!s}")
            self.exit(414)
            return (414)

        self.log(f"Technology Type Data: {self.tech_type_data}, type: {type(self.tech_type_data)}")

        if self.tech_type_data.get("kind") is not None:
            self.tech_type_data_extracted = self.tech_type_data.get("data")
        else:
            self.tech_type_data_extracted = {"Error": "No data found for this technology type."}

        self.log (f"Technology Type Data Extracted: {self.tech_type_data_extracted}")

        for dataset in self.tech_type_data_extracted:
            self.tech_type_guid = dataset.get("GUID")
            self.tech_type_name = dataset.get("Display Name")
            self.tech_type_templates = dataset.get("Catalog Templates")
            self.tech_type_processes = dataset.get("Governance Processes")
            self.tech_type_description = tech_type_description
            self.log(f"Technology Type GUID: {self.tech_type_guid}")
            self.log(f"Technology Type Name: {self.tech_type_name}")
            self.log(f"Technology Type Description: {self.tech_type_description}")
            self.log(f"Technology Type Templates: {self.tech_type_templates}" or [{"templates": "None"}])
            self.log(f"Technology Type Processes: {self.tech_type_processes}" or [{"processes": "None"}])

        await self.push_screen(TechnologyTypeOptionsScreen(self.tech_type_guid,
                                               self.tech_type_name,
                                               self.tech_type_description,
                                               self.user_name,
                                               self.user_password,
                                               self.karma_points,
                                               self.tech_type_templates,
                                               self.tech_type_processes), callback = self.tech_type_options_callback)
        return(200)

    async def tech_type_options_callback(self, result: list):
        self.log(f"Technology Type Options screen returned: {result}")
        if not result[0] or isinstance(result[0], int):
            if isinstance(result[0], int) and result[0] == 200:
                self.log("Technology Type Options screen returned successfully.")
                return(200)
            else:
                self.log(f"Technology Type Options screen cancelled/failed; return: {result}, exiting.")
                self.exit(415)
            self.log(f"Technology Type Options screen cancelled/failed; return: {result}, exiting.")
            self.exit(415)
            return

        self.selected_t_option = str(result[0])
        self.selected_t_option_selected = result[1]
        self.log(f"Technology Type Options screen returned: {self.selected_t_option} | {self.selected_t_option_selected}")

        # display the screen so the objects we need to mount to are created in the DOM
        # then we can build the display elements for the placeholder properties
        # and mount them in the appropriatwe containers on the screen
        if self.selected_t_option == "template":
            await self.push_screen(TechnologyTypeTemplatesScreen(self.user_name,
                                                             self.karma_points,
                                                             self.tech_type_name,
                                                             self.tech_type_description,
                                                             self.selected_t_option,
                                                             self.selected_t_option_selected,
                                                             self.tech_type_templates),
                                   callback=self.tech_type_templates_callback)
        elif self.selected_t_option == "process":
            await self.push_screen(TechnologyTypeProcessesScreen(self.user_name,
                                                             self.karma_points,
                                                             self.tech_type_name,
                                                             self.tech_type_description,
                                                             self.selected_t_option,
                                                             self.selected_t_option_selected,
                                                             self.tech_type_processes),
                                   callback=self.tech_type_processes_callback)
        else:
            self.log(f"Technology Type Options screen returned invalid option: {self.selected_t_option_selected}")
            self.exit(416)
        return(200)

    async def fetch_technology_types(self) -> int:
        self.tech_type_list: list = [{}]
        try:
            self.autoc = AutomatedCuration(self.view_server, self.platform_url, self.user_name, self.user_password)
            self.autoc.create_egeria_bearer_token(self.user_name, self.user_password)
            # retrieve the tech type data
            self.log(f"Fetching technology type hierarchy for tech_type='*'")
            self.tech_type_response = await self.autoc._async_get_tech_type_hierarchy(filter_string = "*" )
        except Exception as e:
            self.log(f"Exception in get_tech_type_hierarchy: {e}")
            self.log(print_basic_exception(e))
            self.tech_type_list = [{}]
            self.exit(416)
            return(416)

        self.log (f"tech_type_response: {self.tech_type_response}")
        # Copy the data into a working variable for the extraction routine
        self.tech_type_list = self.tech_type_response
        return(200)

    def unpack_egeria_data(self) -> int:
        """ Unpack the data returned from Egeria """
        output_data: list[dict] = [{}]
        output_data.clear()
        if isinstance(self.tech_type_data, dict):
            if "data" in self.tech_type_data:
                output_data = self.tech_type_data.get("data")
            else:
                output_data = [self.tech_type_data]
        elif isinstance(self.tech_type_data, list):
            for entry in self.tech_type_data:
                if isinstance(entry, dict):
                    output_data = entry.get("data")
                elif isinstance(entry, list):
                    for subentry in entry:
                        if isinstance(subentry, dict):
                            output_data = [subentry]
                        else:
                            self.log(f"error unknown data structure for Tech Type data")
                            return(417)
                else:
                    self.log(f"error unknown outer data structure for Tech Type data")
                    return (417)
        else:
            self.log(f"Tech Type data not dict or list")
            return(417)

        self.log(f"output_data: {output_data}, {type(output_data)}")
        # return the extracted data (dict)
        self.tech_type_list = output_data
        return (200)

    def tech_type_templates_callback(self, result):
        """ Callback for Technology Type Templates screen
            result contains up to 3 elements:
            [0] = return code or 'input', [1] input data, [2] full template"""
        # take the input data and use it in the form and
        # create from template
        self.log(f"Technology Type Templates screen returned: {result}")
        # Check for return code
        if isinstance(result, int):
            self.log(f"Technology Type Templates screen returned: {result}, exiting.")
            self.exit(result)
        # Check for unexpected return
        if not result or result[0] != "input":
            self.log(f"Technology Type Templates screen cancelled/failed; return: {result}, exiting.")
            self.exit(418)
            return

            # make the keys to the input data match the keys in the template structure
            # take each key and use the data value to replace the placeholder value in the template
            # then use the pyegeria create_metadata_element_from template to create the metadata element
            # finally display a status screen to confirm the creation of the metadata element

        # make a working version of the full template if it is returned 
        if isinstance(result[2], dict):
            self.full_template = result[2]
        # create an empty dict for the returned data
        my_placeholderPropertyValues: dict = {}
        # load in the returned placeholder user data
        if isinstance(result[1], dict):
            self.placeholder_input = result[1]
        # clean up the keys of the user data to match the template keys
        if isinstance(self.placeholder_input, dict):
            # for each data input item in the dict
            for input_item, input_value in self.placeholder_input.items():
                self.log(f"input_item: {input_item}, input_value: {input_value}")
                input_fix1 = input_item.replace("_", " ")
                self.log(f"input_item after underscore removal: {input_fix1}")
                input_fix2 = input_fix1.replace(" placeholder input", "")
                self.log(f"input_item after placeholder removal: {input_fix2}")

                self.log(f"fixed input_item: {input_fix2}, {input_value}")
                # build the placeholderPropertyValues dict
                my_placeholderPropertyValues.update({input_fix2: input_value})
                continue
        else:
            self.log(f"placeholder_input is not a dict: {self.placeholder_input}")
            return(419)

        # create a dict structure that matches the template structure
        # we have the input data in my_placeholderPropertyValues and
        # the selected template in self.full_template
        # so we can use the pyegeria create_metadata_element_from template to create the metadata element
        # finally display a status screen to confirm the creation of the metadata element

        self.log(f"my_placeholderPropertyValues: {my_placeholderPropertyValues}")
        self.log(f"self.placeholder_input: {self.placeholder_input}")
        self.log(f"self.full_template: {self.full_template}")

        # copy the retrieved template into the request body
        request_body:dict = {
          "class" : "TemplateRequestBody",
          "externalSourceGUID" : self.full_template.get("externalSourceGUID") or "",
          "externalSourceName" : self.full_template.get("externalSourceName") or "",
          "typeName" : self.full_template.get("typeName") or "",
          "templateGUID" : self.full_template.get("Catalog Template GUID"),
          "anchorGUID" : self.full_template.get("anchorGUID"),
          "isOwnAnchor" : "false",
          "effectiveFrom" : "2026-01-01",
          "effectiveTo": "2030-12-31",
          "replacementProperties" : self.full_template.get("replacementProperties") or {},
          "placeholderPropertyValues" : {},
          "parentGUID" : None,
          "parentRelationshipTypeName" : None,
          "parentRelationshipProperties" : None,
          "parentAtEnd1" : self.full_template.get("parentAtEnd1") or True,
          "effectiveTime" : self.full_template.get("effectiveTime") or datetime.datetime.now().isoformat(),
        }
        self.log(f"request_body: {request_body}")
        # update the request body with the user provided input
        for key, value in my_placeholderPropertyValues.items():
            request_body["placeholderPropertyValues"].update({key: value})
            continue
        self.log(f"request_body after update: {request_body}")
        # now instantiate and call the function to create the element from the template
        try:
            tokendata = self.autoc.create_egeria_bearer_token(self.user_name, self.user_password)
            my_md_instance = MetadataExpert(self.view_server, self.platform_url, self.user_name, self.user_password, tokendata)
            # new_guid = my_md_instance.create_metadata_element_from_template(self.template_guid, body = request_body)
            new_guid = my_md_instance.create_metadata_element_from_template(body=request_body)
        except Exception as e:
            self.log(f"Exception in create_element_from_template: {e}")
            if isinstance(e, PyegeriaException):
                self.log(print_basic_exception(e))
            else:
                self.log(f"Exception in create_element_from_template: {e}")
            self.push_screen(StatusScreen(f"Error creating element from Template/n{print_basic_exception(e)}"), callback=self.status_callback)
            return(420)

        self.log(f"new_guid: {new_guid}")
        self.push_screen(StatusScreen(f"Element created from Template/Metadata element created with GUID: '{new_guid}'"), callback=self.status_callback)

    def status_callback(self, status_callback_rc) -> None:
        """ Callback routine from the status screen,
            this screen is typically displayed at the end of a process
            to indicate success or failure of the process."""

        self.log(f"Status screen returned: {status_callback_rc}")
        self.exit(status_callback_rc)

    def tech_type_processes_callback(self, result):
        """ Callback for Technology Type Processes screen"""
        # take the input data and use it to run the command/process
        pass

    def shop_for_data_callback(self, result):
        """ Callback for Shop For Data screen"""
        selection_type = result[0]
        selection_parm_1 = result[1]
        selection_parm_2 = result[2]

        if isinstance(selection_type, int):
            if selection_type == 200:
                return(200)
            else:
                self.log(f"Shop For Data screen returned: {selection_type}, exiting.")
                self.exit(selection_type)

        if selection_type == "dictionary":
            self.log(f"Selected dictionary with qualified name: {selection_parm_1}")
            self.build_dictionary_details(selection_parm_1, selection_parm_2)
        elif selection_type == "domain":
            self.log(f"Selected business domain with qualified name: {selection_parm_1}")
            self.build_domain_details(selection_parm_1, selection_parm_2)
        elif selection_type == "catalog":
            self.log(f"Selected catalog with qualified name: {selection_parm_1}")
            self.build_catalog_details(selection_parm_1, selection_parm_2)
        elif selection_type == "glossary":
            self.log(f"Selected glossary with qualified name: {selection_parm_2}")
            self.build_glossary_details(selection_parm_1, selection_parm_2)
        elif selection_type == "specification":
            self.log(f"Selected data specification with qualified name: {selection_parm_2}")
            self.build_data_specification_details(selection_parm_1, selection_parm_2)
        else:
            self.log(f"Unknown selection type: {selection_type}")
            self.exit(429)

    @work(thread=True, exclusive=True)
    def build_dictionary_details(self, target_qualified_name, target_display_name):
        """ Build the details object for a dictionary details screen"""
        self.log(f"Building dictionary details for qualified name: {target_qualified_name}")
        self.dictionary_qualified_name = target_qualified_name
        self.dictionary_display_name = target_display_name
        build_structure = {}

        try:
            self.dictionary_details = exec_report_spec(format_set_name="Data-Dictionaries",
                                                  output_format="DICT",
                                                  params={"search_string": self.dictionary_qualified_name, "filter_string": self.dictionary_qualified_name},
                                                  view_server=self.view_server,
                                                  view_url=self.platform_url,
                                                  user=self.user_name,
                                                  user_pass=self.user_password)
        except PyegeriaException as e:
            print_basic_exception(e)
            self.log(f"Error retrieving dictionary details: {e!s}")
            self.exit(420)
            return (420)

        if not self.dictionary_details or self.dictionary_details == None:
            error_category = "Dictionary Details"
            error_message = "No dictionary details found"
            self.log(f"Error retrieving dictionary details: {error_category}, {error_message}")
            self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
        elif self.dictionary_details.get("kind") == "empty":
            dictionary_tree: Tree = Tree(label="Empty Dictionary", id="dictionary_details")
            dictionary_tree.root.expand()
            dictionary_tree.root.content = "No dictionary terms found for this dictionary"
        else:
            dictionary_tree: Tree = Tree(label=self.dictionary_display_name, id="dictionary_details")
            dictionary_tree.root.expand()
            dictionary_tree.auto_expand = True
            self.dictionary_details_data = self.dictionary_details.get("data")
            for term in self.dictionary_details_data:
                term_qualified_name = term.get("Qualified Name") or ""
                term_subject = term.get("Subject Area") or ""
                term_summary = term.get("Summary") or ""
                # create dict structure for loading the tree
                build_structure.update({term_subject: [{term_qualified_name: term_summary}]})
                continue
            # Once the structure is complete we can build the tree from it
            for term_subject in build_structure:
                dictionary_branch = dictionary_tree.add(Tree(label=term_subject, id=term_subject))
                for term_qualified_name, term_summary in build_structure[term_subject]:
                    dictionary_branch.add_leaf(Tree(label=term_summary, id=term_summary, data=term_qualified_name))
                dictionary_tree.root.expand()
        self.push_screen(SelectionOverviewScreen("dictionary",
                                                 self.view_server,
                                                 self.platform_url,
                                                 self.user_name,
                                                 self.user_password), callback=self.overview_callback)

    @work(thread=True, exclusive=True)
    def build_domain_details(self, target_qualified_name, target_type__name):
        """ Build the details object for a business domain details screen"""
        self.log(f"Building domain details for qualified name: {target_qualified_name}")
        self.domain_qualified_name = target_qualified_name
        self.domain_type__name = target_type__name
        build_structure = {}

        try:
            self.domain_details = exec_report_spec(format_set_name="BusinessCapabilities",
                                                  output_format="DICT",
                                                  params={"search_string": self.domain_qualified_name, "filter_string": self.domain_qualified_name},
                                                  view_server=self.view_server,
                                                  view_url=self.platform_url,
                                                  user=self.user_name,
                                                  user_pass=self.user_password)
        except PyegeriaException as e:
            print_basic_exception(e)
            self.log(f"Error retrieving business domain details: {e!s}")
            self.exit(420)
            return (420)

        if not self.domain_details or self.domain_details == None:
            error_category = "Business Domain Details"
            error_message = "No domain details found"
            self.log(f"Error retrieving business domain details: {error_category}, {error_message}")
            self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
        elif self.domain_details.get("kind") == "empty":
            domain_tree: Tree = Tree(label="Empty Business Domain", id="domain_details")
            domain_tree.root.expand()
            domain_tree.root.content = "No domain details found for this business domain"
        else:
            self.domain_details_data = self.domain_details.get("data")
            self.domain_display_name = self.domain_details_data.get("displayName")
            domain_tree: Tree = Tree(label=self.domain_display_name, id="domain_details")
            domain_tree.root.expand()
            domain_tree.auto_expand = True
            self.domain_details_data = self.domain_details.get("data")
            for term in self.domain_details_data:
                if term == None:
                    continue
                term_qualified_name = term.get("Qualified Name") or ""
                term_subject = term.get("Subject Area") or ""
                term_summary = term.get("Summary") or ""
                # create dict structure for loading the tree
                build_structure.update({term_subject: [{term_qualified_name: term_summary}]})
                continue
            # Once the structure is complete we can build the tree from it
            for term_subject in build_structure:
                domain_branch = domain_tree.root.add(Tree(label=term_subject, id=term_subject))
                for term_qualified_name, term_summary in build_structure[term_subject]:
                    domain_branch.add_leaf(Tree(label=term_summary, id=term_summary, data=term_qualified_name))
                domain_tree.root.expand()
        self.push_screen(SelectionOverviewScreen("domain",
                                                 self.view_server,
                                                 self.platform_url,
                                                 self.user_name,
                                                 self.user_password), callback=self.overview_callback)

    @work(thread=True, exclusive=True)
    def build_catalog_details(self, target_qualified_name, target_display_name):
        """ Build the details object for a catalog details screen"""
        self.log(f"Building catalog details for qualified name: {target_qualified_name}")
        self.catalog_qualified_name = target_qualified_name
        self.catalog_display_name = target_display_name
        build_structure = {}

        try:
            self.catalog_details = exec_report_spec(format_set_name="Digital-Product-Catalog",
                                                  output_format="DICT",
                                                  params={"search_string": self.catalog_qualified_name, "filter_string": self.catalog_qualified_name},
                                                  view_server=self.view_server,
                                                  view_url=self.platform_url,
                                                  user=self.user_name,
                                                  user_pass=self.user_password)
        except PyegeriaException as e:
            print_basic_exception(e)
            self.log(f"Error retrieving catalog details: {e!s}")
            self.exit(420)
            return (420)

        if not self.catalog_details or self.catalog_details == None:
            error_category = "Catalog Details"
            error_message = "No catalog details found"
            self.log(f"Error retrieving catalog details: {error_category}, {error_message}")
            self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
        elif self.catalog_details.get("kind") == "empty":
            catalog_tree: Tree = Tree(label="Empty Catalog", id="catalog_details")
            catalog_tree.root.expand()
            catalog_tree.root.content = "No catalog terms found for this catalog"
        else:
            catalog_tree: Tree = Tree(label=self.catalog_display_name, id="catalog_details")
            catalog_tree.root.expand()
            catalog_tree.auto_expand = True
            self.catalog_details_data = self.catalog_details.get("data")

            if not self.catalog_details_data or self.catalog_details_data == None:
                error_category = "Catalog Details"
                error_message = "No catalog details found or the data dict entry is missing"
                self.log(f"Error retrieving catalog details: {error_category}, {error_message}")
                self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
                return

            for term in self.catalog_details_data:
                term_qualified_name = term.get("Qualified Name") or ""
                term_subject = term.get("Subject Area") or ""
                term_summary = term.get("Summary") or ""
                # create dict structure for loading the tree
                build_structure.update({term_subject: [{term_qualified_name: term_summary}]})
                continue
            # Once the structure is complete we can build the tree from it
            for term_subject in build_structure:
                catalog_branch = catalog_tree.root.add(Tree(label=term_subject, id=term_subject))
                for term_qualified_name, term_summary in build_structure[term_subject]:
                    catalog_branch.add_leaf(Tree(label=term_summary, id=term_summary, data=term_qualified_name))
                catalog_tree.root.expand()
        self.push_screen(SelectionOverviewScreen("catalog",
                                                 self.view_server,
                                                 self.platform_url,
                                                 self.user_name,
                                                 self.user_password), callback=self.overview_callback)

    @work(thread=True, exclusive=True)
    def build_glossary_details(self, target_qualified_name, target_display_name):
        """ Build the details object for a glossary details screen"""
        self.log(f"Building glossary details for qualified name: {target_qualified_name}")
        self.glossary_qualified_name = target_qualified_name
        self.glossary_display_name = target_display_name
        build_structure: dict = {}
        try:
            self.glossary_details = exec_report_spec(format_set_name="Glossary-Terms",
                                                  output_format="JSON",
                                                  params={"search_string": self.glossary_qualified_name, "filter_string": self.glossary_qualified_name},
                                                  view_server=self.view_server,
                                                  view_url=self.platform_url,
                                                  user=self.user_name,
                                                  user_pass=self.user_password)
        except PyegeriaException as e:
            print_basic_exception(e)
            self.log(f"Error retrieving glossary details: {e!s}")
            self.exit(420)
            return (420)

        self.log(f"glossary_details: {self.glossary_details}")

        if not self.glossary_details or self.glossary_details == None:
            error_category = "Glossary Details"
            error_message = "No glossary details found"
            self.log(f"Error retrieving glossary details: {error_category}, {error_message}")
            self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
        elif self.glossary_details.get("kind") == "empty":
            glossary_tree: Tree = Tree(label="Empty Glossary", id="glossary_details_tree")
            glossary_tree.root.expand()
            glossary_tree.root.content = "No glossary terms found for this glossary"
        else:
            glossary_tree: Tree = Tree(label=self.glossary_display_name, id="glossary_details_tree")
            glossary_tree.root.expand()
            glossary_tree.auto_expand = True

            self.glossary_details_data = self.glossary_details.get("data")

            if not self.glossary_details_data or self.glossary_details_data == None:
                error_category = "Glossary Details"
                error_message = "No glossary details found or the data dict entry is missing"
                self.log(f"Error retrieving glossary details: {error_category}, {error_message}")
                self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
                return
            else:
                for term in self.glossary_details_data:
                    if term == None:
                        continue
                    term_qualified_name = term.get("Qualified Name") or ""
                    term_subject = term.get("Subject Area") or ""
                    term_summary = term.get("Summary") or ""
                    # create dict structure for loading the tree
                    build_structure.update({term_subject: [{term_qualified_name: term_summary}]})
                    continue

            # Once the structure is complete we can build the tree from it
            for term_subject in build_structure:
                glossary_branch = glossary_tree.root.add(Tree(label=term_subject, id=term_subject))
                for term_qualified_name, term_summary in build_structure[term_subject]:
                    glossary_branch.add_leaf(Tree(label=term_summary, id=term_summary, data=term_qualified_name))
                glossary_tree.root.expand()

        self.push_screen(SelectionOverviewScreen("glossary", self.view_server, self.platform_url, self.user_name, self.user_password), callback=self.overview_callback)

    def build_data_specification_details(self, target_qualified_name, target_display_name):
        """ Build the details object for a data specification details screen"""
        self.log(f"Building data specification details for qualified name: {target_qualified_name}")
        self.data_specification_qualified_name = target_qualified_name
        self.data_specification_display_name = target_display_name

        try:
            self.data_specification_details = exec_report_spec(format_set_name="Data-Specifications",
                                                  output_format="JSON",
                                                  params={"search_string": self.data_specification_qualified_name, "filter_string": self.data_specification_qualified_name},
                                                  view_server=self.view_server,
                                                               view_url=self.platform_url,
                                                               user=self.user_name,
                                                               user_pass=self.user_password)
        except Exception as e:
            self.log(f"Error retrieving data specification details: {e}")
            return

        if not self.data_specification_details or self.data_specification_details == None or self.data_specification_details.get("kind") == "empty":
            self.log(f"No data specification details found for qualified name: {self.data_specification_qualified_name}")
            error_category = "Data Specification Details"
            error_message = "No data specification details found"
            self.log(f"Error retrieving data specification details: {error_category}, {error_message}")
            self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
            return

        self.log(f"Data specification details retrieved successfully for qualified name: {self.data_specification_qualified_name}")
        self.log(f"Data specification details: {self.data_specification_details}")

        data_spec_tree: Tree = Tree(label=self.data_specification_display_name, id="data_specification_details")
        data_spec_tree.root.expand()
        data_spec_tree.auto_expand = True
        self.data_specification_details_data = self.data_specification_details.get("data")
        self.log(f"Data specification details data: {self.data_specification_details_data}")

        if not self.data_specification_details_data or self.data_specification_details_data == None:
            error_category = "Data Specification Details"
            error_message = "No data specification details found or the data dict entry is missing"
            self.log(f"Error retrieving data specification details: {error_category}, {error_message}")
            self.push_screen(StatusScreen(f"{error_category}: {error_message}"), callback=self.status_callback)
            return

        specified_id = 0
        for spec in self.data_specification_details_data:
            spec_qualified_name = spec.get("properties", {}).get("qualifiedName") or ""
            spec_type = spec.get("properties", {}).get("typeName") or ""
            spec_description = spec.get("properties", {}).get("description") or ""
            spec_url = spec.get("properties", {}).get("URL") or ""
            spec_display_name = spec.get("properties", {}).get("displayName") or ""
            spec_fixed_label = spec_display_name.replace(" ", "")
            spec_fixed_label = spec_fixed_label.replace(":", "")
            self.log(f"Creating tree node for spec: {spec_fixed_label}, with id: {"id"+str(specified_id)}")
            spec_branch = data_spec_tree.root.add(Tree(label=spec_fixed_label, id="id"+str(specified_id), data=[(spec_display_name, spec_qualified_name, spec_type, spec_description, spec_url)]))
            spec_branch.expand()
            data_spec_tree.root.expand()
            specified_id +=1
        self.push_screen(SelectionOverviewScreen("specification", self.view_server, self.platform_url, self.user_name, self.user_password), callback=self.overview_callback)

    def overview_callback(self):
        """Callback function for handling overview screen actions."""
        pass

if __name__ == "__main__":
    app = MyProfileTui()
    app.run()