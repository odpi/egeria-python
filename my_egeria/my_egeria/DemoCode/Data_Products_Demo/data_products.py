"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of Data Product functions for my_egeria.

"""
import ast
import os

from textual.css.query import NoMatches
from textual.screen import ModalScreen
from textual import on
from textual.app import App, ComposeResult
from textual.message import Message
from textual.containers import Container, ScrollableContainer, Vertical
from textual.widgets import Label, Button, TextArea, Header, Static, Footer, DataTable
from demo_service import get_config
from pyegeria.format_set_executor import exec_report_spec as exec_format_set
from pyegeria._output_format_models import (
    Column,
    Format,
    ActionParameter,
    FormatSet)
from member_details_screen import MemberDetailsScreen
from pyegeria.base_report_formats import select_report_spec, report_specs

CSS_PATH = ["data_products.tcss"]

class SplashScreen(ModalScreen):
    """Splash screen with inline styles (no TCSS)."""

    class SplashContinue(Message):
        """Message to continue to the login screen."""
        pass

    def __init__(self) -> None:
        super().__init__()
        self.app_title = "My Egeria"
        self.subtitle = "Data Products"
        self.app_version = "6.0.0"
        self.app_build_date = "2025-09-08"
        self.app_build_time = "00:00"
        self.app_build_author = "Peter Coldicott"
        self.app_build_commit = "00000000000000000"
        self.app_build_branch = "main"
        self.app_build_platform = "MacOS"
        self.welcome_text = (
            "\n\n"
            "This is example UI code package that leverages the Textual/Rich open source UI Frameworks,\n"
            "and the pyegeria package which is part of the Egeria Project.\n\n"
            "The UI is written in Python and is certainly not meant to demonstrate best coding practices!\n\n"
            "Textual/Rich frameworks originally authored by Will McGugan (Textualize).\n\n"
            "My_Egeria SPDX-License-Identifier: Apache-2.0, "
            "Copyright Contributors to the ODPi Egeria project.\n"
        )

    def compose(self):
        cfg = get_config()
        self.view_server = cfg[1]
        self.platform_url = cfg[0]
        self.user = cfg[2]
        self.password = cfg[3]

        top = Container(
            Label(
                f"Welcome to {self.app_title} v{self.app_version} "
                f"({self.app_build_date} {self.app_build_time})",
                id="splash_title",
            ),
            TextArea(self.welcome_text, id="splash_text"),
            Label(
                f"Build Author: {self.app_build_author} | "
                f"Commit: {self.app_build_commit} | "
                f"Branch: {self.app_build_branch} | "
                f"Platform: {self.app_build_platform}",
                id="splash_meta",
            ),
            id="splash_top"
        )
        yield Header(show_clock=True)
        yield Container(
            Static(
                f"Server: {self.view_server} | Platform: {self.platform_url} | User: {self.user}",
                id="connection_info",
            )
        )
        yield Container(
            Static("MyEgeria", id="title"),
            Static("Data Products", id="main_menu"),
            id="title_row",
        )
        yield top
        yield Button("Continue", variant="primary", id="continue")
        yield Footer()

    async def on_mount(self):
        # Place content in top half, center horizontally
        top = self.query_one("#splash_top", Container)

        top.styles.dock = "top"
        top.styles.height = "25%"
        top.styles.width = "100%"
        top.styles.padding = (1, 2)
        top.styles.align_horizontal = "center"
        top.styles.align_vertical = "top"
        top.styles.gap = 1

        title = self.query_one("#splash_title", Label)
        title.styles.text_align = "center"
        title.styles.text_style = "bold"

        # Fixed visible rows for vertical centering math
        VISIBLE_ROWS = 15

        ta = self.query_one("#splash_text", TextArea)
        ta.styles.width = "90%"
        ta.styles.height = VISIBLE_ROWS  # fixed rows to make vertical centering predictable
        ta.styles.border = ("solid", "white")  # solid white border
        ta.styles.text_style = "bold"
        ta.styles.padding = 1
        ta.styles.text_align = "center"  # horizontal centering of text

        # Vertically center the content by adding top padding lines
        raw_text = self.welcome_text.strip("\n")
        content_lines = raw_text.splitlines() or [raw_text]
        content_rows = len(content_lines)

        # Compute usable rows considering numeric padding
        pad_top = int(getattr(ta.styles.padding, "top", 0) or 0)
        pad_bottom = int(getattr(ta.styles.padding, "bottom", 0) or 0)
        usable_rows = max(VISIBLE_ROWS - (pad_top + pad_bottom), 1)
        top_pad = max((usable_rows - content_rows) // 2, 0)

        ta.value = ("\n" * top_pad) + raw_text

        meta = self.query_one("#splash_meta", Label)
        meta.styles.text_align = "center"

        btn = self.query_one("#continue", Button)
        btn.styles.margin = (1, 0, 0, 0)

    @on(Button.Pressed, "#continue")
    async def continue_to_app(self) -> None:
        """ Continue button pressed, issue continue message to app """
        self.log(f"Continue button pressed, app is: {self.app}")
        self.post_message(SplashScreen.SplashContinue())


class DataProducts(App):

    SCREENS = {
        "splash": SplashScreen,
        "member": MemberDetailsScreen,
    }

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "back", "Back"),
    ]

    CSS_PATH = ["data_products.tcss"]

    def __init__(self):
        super().__init__()
        self.Egeria_config = ["https://127.0.0.1:9443", "qs-view-server", "erinoverview", "secret"]
        self.platform_url = self.Egeria_config[0]
        self.view_server = self.Egeria_config[1]
        self.user = self.Egeria_config[2]
        self.password = self.Egeria_config[3]
        self.token: str

        """ Access Egeria report specifications """
        self.log(f"Accessing Egeria report specs")
        try:

            # Retrieve needed format sets from Egeria
            catalog_set = select_report_spec("Digital-Product-Catalog-MyE", "DICT")
            if catalog_set:
                self.log("Successfully retrieved format set by name!")
                self.log(f"Heading: {catalog_set['heading']}")
                self.log(f"Description: {catalog_set['description']}")
            else:
                self.log("Failed to retrieve DataProductsCatalogMyE format set by name.")
                self.log("Program Error, please report issue to maintainer.")
                self.exit(400)
            product_set = select_report_spec("Digital-Products-MyE", "DICT")
            if product_set:
                self.log("Successfully retrieved format set by name!")
                self.log(f"Heading: {product_set['heading']}")
                self.log(f"Description: {product_set['description']}")
            else:
                self.log("Failed to retrieve DataProductsMyE format set by name.")
                self.log("Program Error, please report issue to maintainer.")
                self.exit(400)
        except Exception as e:
            self.log(f"Error connecting to PyEgeria: {str(e)}")
            self.exit(400)

            # Create a custom output-format-set for browsing the Catalog structures
            # without regard to the specific type of an entry
        columns = [
            Column(name="Display Name", key="display_name"),
            Column(name="Qualified Name", key="qualified_name"),
            Column(name="Description", key="description", format=True),
            Column(name="Type Name", key="type_name"),
            Column(name="Status", key="status"),
            Column(name="Containing Members", key="Containing Members", format=True),
            ]
        MyE_format = Format(
            types=["DICT"],
            attributes=columns
            )
        explorer_format_set = FormatSet(
            heading="Explore-Structure-Format-Set",
            description="A custom format set for exploring Catalog Structures",
            aliases=["Catalog Explorer"],
            formats=[MyE_format],
            action=ActionParameter(
                function="CollectionManager.find_collections",
                required_params=["search_string"],
                spec_params={},
            ),
            get_additional_props=ActionParameter(
                function="CollectionManager._find_collection",
                required_params=[],
                spec_params={},
            )
            )

        # report_specs["ExploreStructure"] = explorer_format_set

        # explorer_set = select_report_spec("ExploreStructure", "DICT")

    def on_mount(self):
        self.log(f"on_mount event triggered")
        self.log(f"Getting default screen: SplashScreen")
        self.push_screen("splash")

    def compose(self) -> ComposeResult:
        """Create the layout of the screen."""
        yield Header(show_clock=True)
        yield Container(
            Static(
                f"Server: {self.view_server} | Platform: {self.platform_url} | User: {self.user}",
                id="connection_info",
            )
        )
        yield Container(
            Static("MyEgeria", id="title"),
            Static("Data Products", id="main_menu"),
            id = "title_row",
        )
        yield ScrollableContainer(
            Vertical(
                Static(f"Available Data Product Marketplaces:\n\n", id="before_static", expand=True, shrink=True),
                Static("\n\nEnd of DataTable", id="after_static"),
            ),
            id="main_content")
        yield Container(
            Button("Quit", id="quit"),
            id="action_row",
        )
        yield Footer()
        self.log("done yielding, now waiting for user input")

    def on_splash_screen_splash_continue(self):
        """ Continue received from the Splash Screen"""
        self.log(f"Continue received from Splash Screen, so remove splash screen")
        self.pop_screen()
        # run the function to retrieve collections data from Egeria
        self.log(f"Retrieving Data Products from Egeria - get_collections_from_egeria")
        # self.get_collections_from_egeria(Egeria_config=self.Egeria_config, Search_str = "*")
        self.refresh_main_screen()

    def refresh_main_screen(self):
        try:
            self.collections = [{}]
            response = exec_format_set(
                format_set_name="Digital-Product-Catalog-MyE",
                output_format="DICT",
                view_server=self.view_server,
                view_url=self.platform_url,
                user=self.user,
                user_pass=self.password,
            )
            self.log(f"response: {response}")

            # Robustly extract data payload from response["data"]. Then populate self.collections.
            payload = None
            if isinstance(response, dict) or isinstance(response, list):
                payload = self.unpack_egeria_data(response)

            if not payload:
                self.log("No parsable data found in response['data']")
                payload = [{"NoData": "No parsable data found in response"}]

            self.collections = payload
            self.log(f"collections after extraction: {type(self.collections)} len={len(self.collections)}")

        except Exception as e:
            self.log(f"Error connecting to Egeria: {str(e)}")
            self.collections = [{"Egeria Error": str(e)}]

        self.collection_datatable: DataTable = DataTable()
        # configure the DataTable - collection_datatable
        self.collection_datatable.id = "collection_datatable"
        # Add columns with keys to the DataTable
        # self.collection_datatable.add_columns(*DataProductScreen.ROWS[0])
        self.collection_datatable.add_columns(
            ("Display Name", "dn_key"),
            ("Qualified Name", "qn_key"),
            ("Type Name", "tn_key"),
            ("Description", "desc_key")
            )

        # set the cursor to row instead of cell
        self.collection_datatable.cursor_type = "row"
        # give the DataTable zebra stripes so it is easier to follow across rows on the screen
        self.collection_datatable.zebra_stripes = True
        # Check that we have at least one Data Product Catalogue
        if self.collections is None:
            # No Data Product Catalogues found
            # self.log("No Data Product Catalogues found")
            self.collection_datatable.add_row("Error", "No Data Product Catalogues found")
        else:
            # Load data into the DataTable
            try:
                for entry in self.collections:
                    if "unknown" in entry:
                        self.collection_datatable.add_row(
                            # entry.get("error"),
                            # entry.get("unknown")
                            entry
                            )
                        continue
                    elif "shape" in entry:
                        self.collection_datatable.add_row(
                            # entry.get("error"),
                            # entry.get("shape")
                            entry
                        )
                        continue
                    elif "Egeria Error" in entry:
                        self.collection_datatable.add_row(
                            # entry.get("Egeria Error")
                            entry
                        )
                        continue
                    elif "error" in entry:
                        self.collection_datatable.add_row(
                            # entry.get("error")
                            entry
                        )
                        continue
                    else:
                        if isinstance(entry, dict):
                            self.collection_datatable.add_row(
                                entry.get("Display Name", "None"),
                                entry.get("Qualified Name", "None"),
                                entry.get("Type Name", "None"),
                                entry.get("Description", "None")
                            )
                        elif isinstance(entry, list):
                            for item in entry:
                                self.collection_datatable.add_row(
                                    item.get("Display Name", "None"),
                                    item.get("Qualified Name", "None"),
                                    item.get("Type Name", "None"),
                                    item.get("Description", "None")
                                    )
                        else:
                            self.collection_datatable.add_row(
                                entry
                            )
            except Exception as e:
                self.collection_datatable.add_row("Error", "Error unpacking collection dict", str(e))
        try:
            catalog_mounted =self.query_one("#collection_datatable")
            if not catalog_mounted:
                self.mount(self.collection_datatable, after="#before_static")
            else:
                self.collection_datatable.refresh(layout=True, recompose=True)
        except (NoMatches):
            self.mount(self.collection_datatable, after="#before_static")

    def handle_splash_screen_splash_continue(self):
        """Allow direct calls from SplashScreen to continue the app flow."""
        # Delegate to the standard event handler so logic stays in one place
        self.on_splash_screen_splash_continue()

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "quit":
            """ Quit the application gracefully with a "good" return code (200) """
            self.log(f"Quit button clicked")
            self.exit(200)
            return
        else:
            self.log(f"Button pressed: {event.button.id}")
            self.log(f"Unknown button id: {event.button.id}")
            return

    @on(DataTable.RowSelected, "#collection_datatable")
    def handle_catalog_table_row_selected(self, message: DataTable.RowSelected):
        self.log(f"Row Selected, Processing selection")
        self.row_selected = message.row_key
        self.row_selected_data = self.collection_datatable.get_row(message.row_key)
        self.selected_name = str(self.row_selected_data[0] or "")
        self.selected_qname = str(self.row_selected_data[1] or "")
        self.selected_type = str(self.row_selected_data[2] or "")
        self.selected_desc = str(self.row_selected_data[3] or "")
        self.member_list: list = []
        self.log(f"qname: {self.selected_qname}<====")

        payload: list = []
        payload.clear()

        try:
            self.log(f"selected qualified name = {self.selected_qname}<====, type: {type(self.selected_qname)}")
            response = exec_format_set(
                format_set_name="Digital-Product-Catalog-MyE",
                params = {"search_string" : self.selected_qname},
                output_format="DICT",
                view_server=self.view_server,
                view_url=self.platform_url,
                user=self.user,
                user_pass=self.password,
            )
            self.log(f"response: {response}")
            if isinstance(response, dict) or isinstance(response, list):
                oneinstance = self.unpack_egeria_data(response)
                payload = oneinstance
                self.log(f"payload: {payload}")

            if not payload:
                self.log("No parsable data found in response from Egeria")
                payload = [{"error": "No parsable data found in response from Egeria"}]

            for entry in payload:
                if isinstance(entry, dict) and len(entry) > 0:
                    if  entry.get("Containing Members") is not None:
                        member = entry.get("Containing Members")
                        self.log(f"member variable: {member}, type: {type(member)}")
                        split_members = member.split(",")
                        self.log(f"split_members: {split_members}, type: {type(split_members)}")
                        self.member_list.extend(split_members)
                        self.log(f"member_list: {self.member_list}, type: {type(self.member_list)}")
                        continue
                    else:
                        self.member_list.append({"error": "no Containing Members"})
                        continue
                else:
                    if isinstance(entry, list):
                        for member in entry:
                            if isinstance(member, dict) and member.get("Containing Members") is not None:
                                self.log(f"member is a dict and has containing members")
                                if isinstance(member.get("Containing Members"), list):
                                    member_ext = member.get("Containing Members")
                                    self.log(f"member variable: {member_ext}, type: {type(member_ext)}")
                                    split_members = member_ext.split(",")
                                    self.log(f"split_members: {split_members}, type: {type(split_members)}")
                                    self.member_list.extend(split_members)
                                    self.log(f"member_list: {self.member_list}, type: {type(self.member_list)}")
                                    continue
                                else:
                                    if isinstance(member.get("Containing Members"), str):
                                        item_string = member.get("Containing Members")
                                        self.log(f"member variable: {item_string}, type: {type(item_string)}")
                                        split_members = item_string.split(",")
                                        self.log(f"split_members: {split_members}, type: {type(split_members)}")
                                        self.member_list.extend(split_members)
                                        self.log(f"member_list: {self.member_list}, type: {type(self.member_list)}")
                                        continue
                            elif isinstance(member, dict) and member.get("Containing Members") is None:
                                self.member_list.append({"error": "no Containing Members"})
                                self.log(f"member is a dict and has no containing members")
                                continue
                            else:
                                if isinstance(member, list):
                                    self.log(f"member is a list")
                                    for item in member:
                                        if isinstance(item, dict) and item.get("Containing Members") is not None:
                                            self.log(f"item inside a list is a dict and has containing members")
                                            if isinstance(item.get("Containing Members"), list):
                                                for items in item.get("Containing Members"):
                                                    self.log(f"containing members contains a list")
                                                    self.member_list.append(items)
                                            else:
                                                if isinstance(item.get("Containing Members"), str):
                                                    item_string = item.get("Containing Members")
                                                    self.log(f"containing members contains a string")
                                                    split_list = ast.literal_eval(item_string)
                                                    self.log(f"literal_eval of member_list: {split_list}")
                                                    if isinstance(split_list, list):
                                                        self.member_list.extend(split_list)
                                                    else:
                                                        self.member_list.append(split_list)
                                                    self.log(f" Members after split: {type(self.member_list)}, {self.member_list}")
                                                else:
                                                    self.member_list.append({"error": "unknown inner data structure"})
                                            continue
                                        else:
                                            self.member_list.append({"error": "unknown inner data structure"})
                                else:
                                    self.member_list.append({"error": "unknown inner data structure"})
                                    continue
                    else:
                        self.member_list.append({"error": "unknown outer data structure"})
                        continue
        except Exception as e:
            self.log(f"Error connecting to Egeria: {str(e)}")
            self.member_list = [{"Egeria Error": str(e)}]

        # set up the data table

        self.member_datatable: DataTable = DataTable()
        # Configure the DataTable - member_datatable
        self.member_datatable.id = "member_datatable"
        # Add columns to the DataTable
        # self.member_datatable.add_columns(*MembersScreen.ROWS[0])
        self.member_datatable.add_columns( "Display Name","Qualified Name", "Type Name", "Status", "Description")
        # set the cursor to row instead of cell
        self.member_datatable.cursor_type = "row"
        # give the DataTable zebra stripes so it is easier to follow across rows on the screen
        self.member_datatable.zebra_stripes = True
        # Check that we have at least one Data Product Catalogue
        if self.member_list is None or "There are no members for this collection" in self.member_list:
            # No Data Product Catalogues found
            # self.log("No Data Product Catalogues found")
            self.member_datatable.add_row("Error", "No Data Product Catalogues found")
        elif type(self.member_list) is list and "There are no members for this collection" in self.member_list:
            # No members found for the collection
            self.member_datatable.add_row("Error", "No members found for this collection")
        else:
            # Load data into the DataTable
            try:
                self.log(f"payload: {self.member_list}")
                if isinstance(self.member_list, str):
                    self.member_list: list = ast.literal_eval(self.member_list)
                for entry in self.member_list:
                    self.log(f" from member_list - entry: {entry}")
                    self.member_instance = entry
                    qualified_name = self.member_instance
                    try:
                        member_data: dict = exec_format_set(
                            format_set_name="ExploreStructure",
                            params={"search_string": str(qualified_name)},
                            output_format="DICT",
                            view_server=self.view_server,
                            view_url=self.platform_url,
                            user=self.user,
                            user_pass=self.password,
                            )
                        self.log(f"from explorer set member_data: {member_data}")
                    except Exception as e:
                        self.log(f"Exception in Egeria response processing: {str(e)}")
                        member_data = {}
                    if member_data:
                        self.log(f" found member_data: {member_data}")
                        twoinstance = self.unpack_egeria_data(member_data)
                        member_attributes = twoinstance
                        self.log(f"member_attributes: {member_attributes}, type: {type(member_attributes)}")
                        for entry in member_attributes:
                            # extract the data area from the response
                            if "unknown" in entry:
                                self.member_datatable.add_row(
                                    entry.get("error"),
                                    entry.get("unknown")
                                )
                                continue
                            elif "shape" in entry:
                                self.member_datatable.add_row(
                                    entry.get("error"),
                                    entry.get("shape")
                                )
                                continue
                            elif "Egeria Error" in entry:
                                self.member_datatable.add_row(
                                    entry.get("Egeria Error")
                                )
                                continue
                            elif "error" in entry:
                                self.member_datatable.add_row(
                                    entry.get("error")
                                )
                                continue
                            else:
                                self.member_datatable.add_row(
                                    entry["Display Name"],
                                    qualified_name,
                                    entry["Type Name"],
                                    entry["Description"]
                                )
                            continue
                    else:
                        self.log(f"no member data found: {member_data}")
                        self.member_datatable.add_row(
                            qualified_name,
                            {"Data": "No member data found"}
                        )
                        self.log(f" No member_data empty (None) row added")
                        continue
            except Exception as e:
                self.member_datatable.add_row("Error", "Error updating member list", str(e))
                self.log(f"Error updating member list: {str(e)}")
        try:
            collection_mounted = self.query_one("#collection_datatable")
            if collection_mounted:
                self.collection_datatable.remove()
            widget_to_mount = self.query_one("#member_datatable")
            if not widget_to_mount:
                self.mount(self.member_datatable, before="after_static")
            self.member_datatable.refresh(layout=True, recompose=True)
            update_label_description = self.query_one("#before_static", Static)
            update_label_description.update(content = "Available Contained Members List:\n\n", layout = True)
        except (NoMatches):
            self.mount(self.member_datatable, after="#after_static")
        # self.log(f"DataTable Refreshed")

    @on(DataTable.RowSelected, "#member_datatable")
    def handle_member_table_row_selected(self, message: DataTable.RowSelected):
        """ Retrieve members of a collection """
        self.selected_row = message.row_key
        self.log(f"Row Selected, Processing selection, {self.selected_row}")
        self.selected_member_data = self.member_datatable.get_row(message.row_key)
        self.log(f"Member DataTable, row selected: {self.selected_member_data}")
        self.selected_name = str(self.selected_member_data[0] or "")
        self.selected_qname = str(self.selected_member_data[1] or "")
        self.selected_type = str(self.selected_member_data[2] or "")
        self.selected_desc = str(self.selected_member_data[3] or "")
        self.log(f"selected_qname: {self.selected_qname}")
        # Retrieve selected Member
        response = exec_format_set(
            format_set_name="ExploreStructure",
            params={"search_string": self.selected_qname},
            output_format="DICT",
            view_server=self.view_server,
            view_url=self.platform_url,
            user=self.user,
            user_pass=self.password,
        )
        # Robustly extract data payload from response["data"]. Then populate self.members.
        self.log(f"from egeria response: {response}")
        self.members = []
        self.members.clear()
        payload: list = []
        payload.clear()
        oneinstance = self.unpack_egeria_data(response)
        payload = oneinstance
        self.log(f"member selected payload: {payload}")
        for entry in payload:
            self.log(f"entry in payload: {entry}")
            if isinstance(entry, dict) and "data" not in list(entry.keys()):
                self.members = entry.get("Containing Members")
                self.log(f"Containing members: {self.members}")
                if not isinstance(self.members, str) or self.members is None or self.members == '':
                    self.log(f"No member data found")
                    self.members = None
                else:
                    split_list = ast.literal_eval(self.members)
                    self.log(f"literal_eval of member_list: {split_list}")
                    self.members = split_list
            else:
                self.member_data = entry.get("data")
                self.log(f"member data: {self.member_data}")
                self.members = self.member_data.get("Containing Members")
                self.log(f"Containing members: {self.members}")
                if not self.members or self.members is None:
                    self.members = None
                else:
                    split_list = ast.literal_eval(self.members)
                    self.log(f"literal_eval of member_list: {split_list}")
                    self.members = split_list
        # If the member has members carry on drilling down to leaf level -
        # Create an instance of the Members Screen and pass it the data retrieved from Egeria
        # and push it to the top of screen stack to display
        self.log(f"members: {self.members}")
        if isinstance(self.members, list) and self.members != None :
            self.process_members()
        else:
            self.log(f"No members, display data for selected member: {self.selected_qname}")
            self.display_member_details(self.selected_qname)

    def display_member_details(self, selected_qname):
        """ Request to display the details for a selected record """
            # gather details returned from egeria
        self.selected_qname = selected_qname
        self.log(f"Selected qname to get member details: {self.selected_qname}")
        member_details = self.get_member_details(self.selected_qname)
        self.log(f"member_details: {member_details}, type: {type(member_details)}")
        inner_dn = inner_qn = inner_c = inner_d = inner_s = inner_tn = ""
        inner_cm = []

        if member_details:
            if isinstance(member_details, list):
                self.log(f"Member Details input is a list: {member_details}")
                if "error" in list(member_details[0].keys()):
                    self.log(f"member_details contain error message: {member_details}")
                elif member_details is None:
                    self.log(f"No member data found {member_details}")
                    # no input provided, set to empty list
                    member_details: list = [{"error": "No data returned from Egeria"}]
                    self.log(f"no member_details from Egeria: {member_details}")
                else:
                    # input is list, not empty and not an error message
                    if isinstance(member_details[0], dict):
                        self.log(f"member_details[0] contains a dict: {member_details}")
                        members_ext = member_details[0]
                        self.log (f"members_ext: {members_ext}")
                        if members_ext is not None:
                            inner_dn= members_ext.get("Display Name") if "Display Name" in members_ext else None
                            inner_qn= members_ext.get("Qualified Name") if "Qualified Name" in members_ext else None
                            inner_c= members_ext.get("Categories") if "Categories" in members_ext else None
                            inner_d= members_ext.get("Description") if "Description" in members_ext else None
                            inner_s= members_ext.get("Status") if "Status" in members_ext else None
                            inner_tn= members_ext.get("Type Name") if "Type Name" in members_ext else None
                            inner_cm= members_ext.get("Contains Members") if "Contains Members" in members_ext else None
                        if inner_cm != None and inner_cm != "":
                            if isinstance(inner_cm, str):
                                split_list = ast.literal_eval(inner_cm)
                                self.log(f"split of inner_cm: {split_list}")
                                inner_cm: list = split_list
                            else:
                                # input is not a string, no Contains Members
                                self.log(f"Contains Members is not a string: {inner_cm}, clearing")
                                inner_cm.clear()
                                pass
                        else:
                            # input is none, empty
                            self.log(f"Contains Members is: {inner_cm}, empty")
                            inner_cm = []
                    else:
                        # the first entry in the list is not a dict, unknown shape
                        self.log(f"First entry in member_details is not a dict: {member_details}")
                        self.inner_cm = None
                        pass
            elif isinstance(member_details, dict):
                # input is dict
                self.log(f"Member Details input is a dict: {member_details}")
                inner_dn = member_details.get("Display Name") if "Display Name" in member_details else None
                inner_qn = member_details.get("Qualified Name") if "Qualified Name" in member_details else None
                inner_c = member_details.get("Categories") if "Categories" in member_details else None
                inner_d = member_details.get("Description") if "Description" in member_details else None
                inner_s = member_details.get("Status") if "Status" in member_details else None
                inner_tn = member_details.get("Type Name") if "Type Name" in member_details else None
                inner_cm = member_details.get("Containing Members") if "Containing Members" in member_details else None
                if isinstance(inner_cm, list):
                    self.containing_members = inner_cm
                    self.log(
                        f"members after extraction: {type(self.containing_members)} len={len(self.containing_members)}")
                else:
                    self.containing_members = None
            else:
                # Unknown shape of input to member details screen, setting to emply list
                self.log(f"Member Details input is not a list or dict: {member_details}")
                member_details = []
        else:
            #member_details does not exist
            self.log(f"member_details does not exist: {member_details}")
            member_details = [{"error": "No member_details found"}]
        try:
            inner_dn = inner_dn.strip()
            inner_qn = inner_qn.strip()
            inner_tn = inner_tn.strip()
        except IndexError:
            pass

        table_data: list = [inner_dn, inner_qn, inner_c, inner_d, inner_s, inner_tn, inner_cm, inner_cm, member_details]
        self.log(f"table_data: {table_data}")
        self.push_screen(MemberDetailsScreen(table_data))


    def process_members(self):
        """ Process the members of a collection """
        self.log(f"Processing members of collection: {self.selected_name}")
        self.log(f"Selected qualified name: {self.selected_qualified_name}")
        try:
            self.member_datatable = self.query_one("#member_datatable").remove()
            self.member_datatable: DataTable = DataTable()
        except(NoMatches):
            self.log(f"No DataTable found")
            self.member_datatable: DataTable = DataTable()
        # Configure the DataTable - member_datatable
        self.member_datatable.id = "member_datatable"
        # Add columns to the DataTable
        self.member_datatable.add_columns(
            ("Qualified Name"),
            ("Display Name"),
            ("Type Name"),
        )
        # set the cursor to row instead of cell
        self.member_datatable.cursor_type = "row"
        # give the DataTable zebra stripes so it is easier to follow across rows on the screen
        self.member_datatable.zebra_stripes = True
        # Check that we have at least one Data Product Catalogue
        if self.members is None or "There are no members for this collection" in self.members:
            # No Data Product Catalogues found
            # self.log("No Data Product Catalogues found")
            self.member_datatable.add_row("Error, No Data Product Catalogues found")
        elif type(self.members) is list and "There are no members for this collection" in self.members:
            # No members found for the collection
            self.member_datatable.add_row("Error, No members found for this collection")
        else:
            # Load data into the DataTable
            try:
                for entry in self.members:
                    self.member_datatable.add_row(
                        # entry.get("Qualified Name", "None"),
                        entry["Qualified Name"],
                        entry["Display Name"],
                        entry["Type Name"],
                    )
                    # self.log(f"DataTable row added with: {entry['Qualified Name']}")
            except Exception as e:
                self.member_datatable.add_row("Error", "Error updating member list", str(e))
                # self.log(f"Error updating member list: {str(e)}")
        try:
            collection_mounted = self.query_one("#collection_datatable")
            if collection_mounted:
                self.collection_datatable.remove()
            widget_to_mount = self.query_one("#member_datatable")
            if not widget_to_mount:
                self.mount(self.member_datatable, after="#after_static")
            self.member_datatable.refresh(layout=True, recompose=True)
        except (NoMatches):
            self.mount(self.member_datatable, after="#after_static")

    def get_member_details(self, selected_qname) -> list:
        """ Retrieve members of a collection """
        self.selected_qualified_name = str(selected_qname)
        self.log(f"Selected qualified name for exec_format_set: {self.selected_qualified_name}")
        # Retrieve selected Member
        response = exec_format_set(
            # format_set_name="BasicCollections",
            format_set_name=self.explorer_format_set,
            params={"search_string": self.selected_qualified_name},
            output_format="DICT",
            view_server=self.view_server,
            view_url=self.platform_url,
            user=self.user,
            user_pass=self.password,
        )
        self.log(f"response: {response}")

        # Robustly extract data payload from response["data"]. Then populate self.members.
        payload = [{}]
        if isinstance(response, dict) or isinstance(response, list):
            payload = self.unpack_egeria_data(response)
            self.log(f"payload: {payload}")

        if not isinstance(payload, list) or len(payload) == 0:
            self.log("No parsable data found in response from Egeria")
            payload = [{"error": "No parsable data found in response from Egeria"}]

        return payload

    async def action_back(self) -> None:
    #     """ Return to the Display Available Catalogs display """
        self.log(f"Back requested")
        self.refresh_main_screen()

    def unpack_egeria_data(self, data) -> list[dict]:
        """ Unpack the data returned from Egeria """
        output_data: list[dict] = []
        output_data.clear()
        if isinstance(data, dict):
            if "data" in data:
                output_data = data.get("data")
        elif isinstance(data, list):
            for entry in data:
                if isinstance(entry, dict):
                    output_data = entry.get("data")
                elif isinstance(entry, list):
                    for subentry in entry:
                        if isinstance(subentry, dict):
                            output_data = subentry.get("data")
                        else:
                            output_data = [{"error": "unknown data structure"}]
                else:
                    output_data = [{"error": "unknown outer data structure"}]
        else:
            output_data = [{"error": "not dict or list", "shape": "data to unpack is not a recognized shape"}]
        return(output_data)

if __name__ == "__main__":
    try:
        import pydevd_pycharm
        pydevd_pycharm.settrace(
            "127.0.0.1",  # Ensure it's localhost since your app runs on the same machine as PyCharm
            port=5679,  # Choose an available port
            stdout_to_server=True,
            stderr_to_server=True,
            suspend=False  # Set to False to let the application continue running after starting
            )
    except ImportError:
        print("pydevd-pycharm not installed or setup failed. Debugger won't be active.")
    except Exception as e:
        pass

    app = DataProducts()
    os.environ.setdefault("EGERIA_PLATFORM_URL", "https://127.0.0.1:9443")
    os.environ.setdefault("EGERIA_VIEW_SERVER", "qs-view-server")
    os.environ.setdefault("EGERIA_USER", "erinoverview")
    os.environ.setdefault("EGERIA_USER_PASSWORD", "secret")
    app.run()