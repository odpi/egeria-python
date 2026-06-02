"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""
import asyncio
import os

from pydantic import ValidationError
from textual import on
from textual.app import ComposeResult, App
from textual.containers import Container, Horizontal, Grid, Vertical
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widgets import Static, Button, Footer, Header, DataTable, Tree

from pyegeria.view.base_report_formats import *
from pyegeria.view.format_set_executor import exec_report_spec

# from my_connectors_splash_screen import SplashScreen

CSS_PATH = ["my_connectors.tcss"]

class ReportSpec(App):

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "back", "Back"),
    ]

    class MainScreen(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def compose(self) -> ComposeResult:
                self.heading = "Report Specs"
                self.subheading = "Select a report spec to execute:"
                self.description = "Select a report spec to execute."
                # self.tech_type_list = "Tech-Type-Details"
                # self.log(f"tech_type_datatable: {self.tech_type_datatable}, id: {self.tech_type_datatable.id}")
                
                self.tech_type_list = self.get_tech_type_list()
                self.log(f"tech_type_list: {self.tech_type_list}, type: {type(self.tech_type_list)}")
                try:
                    self.tech_type_datatable = self.query_one("#tech_type_datatable", DataTable)
                    self.tech_type_datatable.clear()

                except NoMatches:
                    self.tech_type_datatable: DataTable = DataTable(id="tech_type_datatable")

                for entry in self.tech_type_list:
                        dname = entry.get("Display Name", "No Display Name")
                        qname = entry.get("Qualified Name", "No Qualified Name")
                        desc = entry.get("Description", "No Description")
                        self.tech_type_datatable.add_row(dname, desc, qname)
                        continue

                self.tech_type_datatable.refresh()

                yield Header(show_clock=True)
                yield Vertical(
                    Static(f"{self.subheading},   {self.description}", id="tech_type_list_header"),
                    Static(f"Server: {self.view_server} | Platform: {self.platform_url} | User: {self.user}"),
                    id="connection_info")
                yield Container(
                    Static(f"Start of Technology Type List:", id="report_start"),
                    self.tech_type_datatable,
                    Static(f"End of Technology Type List:", id = "report_end"),
                    id = "tech_type_data_container",
                    )
                yield Horizontal(
                    Button("Quit", id="quit"),
                    Button("Back", id="back"),
                    id="action_row"
                    )
                yield Footer()

        def get_tech_type_list(self):
            """ Get the list of tech types """
            self.tech_type_list: list = [{}]
            self.list_unpack: dict = {}
            self.tech_type_dict: dict = {}
            try:
                self.tech_type_response = exec_report_spec(format_set_name="Tech-Types",
                                                           output_format="DICT",
                                                           params={"search_string": "*"},
                                                           view_server=self.view_server,
                                                           view_url=self.platform_url,
                                                           user=self.user,
                                                           user_pass=self.password)
                self.tech_type_list = self.tech_type_response.get("data")
                self.tech_type_separated = ReportSpec.unpack_egeria_data(self.tech_type_response)
                self.log(f"tech_type_separated: {self.tech_type_separated}")
            except Exception as e:
                self.log(f"Exception in get_tech_type_list: {e}")
                self.tech_type_separated = {"Error": f"get_tech_type_list - {e}"}
            except ValidationError as e:
                self.log(f"ValidationError in get_tech_type_list: {e}")
                self.tech_type_separated = {"ValidationError": f"get_tech_type_list - {e}"}
            return self.tech_type_separated


    class GridChildrenApp(App):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def compose(self):
            self.query_one("#spec_grid", Grid).mount()
            return

    SCREENS = {
        "tech_type_details": "tech_type_details",
        "_default": MainScreen
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tech_type_datatable: DataTable = DataTable()
        self.tech_type_datatable.id="tech_type_datatable"
        self.Egeria_config = ["https://127.0.0.1:9443", "qs-view-server", "erinoverview", "secret"]
        self.platform_url = self.Egeria_config[0]
        self.view_server = self.Egeria_config[1]
        self.user = self.Egeria_config[2]
        self.password = self.Egeria_config[3]
        self.selected_tech_type: str = ""
        self.items: list = []
        self.processes: str = ""

    async def on_mount(self) -> None:
        # push the main screen onto the stack so the queries will work correctly
        await self.push_screen("_default")

    @on(DataTable.RowSelected, "#tech_type_datatable")
    def on_datatable_row_selected(self, event: DataTable.RowSelected) -> None:
        # def handle_datatable_row_selected(self, message: DataTable.RowSelected) -> None:
        """ Handle ListView selection event """
        selected_row = event.row_key
        selected_item = self.tech_type_datatable.get_row(selected_row)
        self.log(f"Selected item: {selected_item} type: {type(selected_item)}")
        selected_item_name = str(selected_item[0] or None)
        selected_item_desc = str(selected_item[1] or None)
        selected_item_qname = str(selected_item[2] or None)
        if selected_item_qname:
            self.selected_tech_type = selected_item_qname
        else:
            self.selected_tech_type = selected_item_name

        self.log(f"Selected tech type: {self.selected_tech_type}")
        self.query_selected_tech_type(self.selected_tech_type)

    @on(Button.Pressed, "#quit")
    def handle_button_pressed(self, event: Button.Pressed) -> None:
        """ Quit the application gracefully with a "good" return code (200) """
        self.log(f"Quit button clicked")
        self.exit(200)
        return

    @on(Button.Pressed, "#back")
    def handle_back_button_pressed(self, event: Button.Pressed) -> None:
        """ Return to the main menu screen """
        self.log(f"Back button clicked")
        self.tech_type_list = ""
        self.selected_tech_type = ""
        self.items.clear()
    
    def get_tech_type_list(self):
        """ Get the list of tech types """
        self.tech_type_list: list = [{}]
        self.list_unpack: dict = {}
        self.tech_type_dict: dict = {}
        try:
            self.tech_type_response = exec_report_spec(format_set_name="Tech-Types",
                                                    output_format="DICT",
                                                    params = {"search_string": "*"},
                                                    view_server=self.view_server,
                                                    view_url=self.platform_url,
                                                    user=self.user,
                                                    user_pass=self.password)
            self.tech_type_list = self.tech_type_response.get("data")
            self.tech_type_separated = self.unpack_egeria_data(self.tech_type_response)
            self.log(f"tech_type_separated: {self.tech_type_separated}")

        except Exception as e:
            self.log(f"Exception in get_tech_type_list: {e}")
            self.tech_type_dict = {"Error": f"get_tech_type_list - {e}"}
        except ValidationError as e:
            self.log(f"ValidationError in get_tech_type_list: {e}")
            self.tech_type_dict = {"ValidationError": f"get_tech_type_list - {e}"}
        return self.tech_type_separated

    def query_selected_tech_type(self, tech_type: str):
        self.selected_tech_type = tech_type
        # query the selected tech type
        self.log(f"Executing tech type query: {self.selected_tech_type}")
        self.parms = {"filter": self.selected_tech_type}
        try:
            response = exec_report_spec(format_set_name="Tech-Type-Processes",
                                        params=self.parms,
                                        output_format="DICT",
                                        view_server=self.view_server,
                                        view_url=self.platform_url,
                                        user=self.user,
                                        user_pass=self.password)
            self.log(f"Return from tech type query:")
            self.log(f"reponse: {response}")
        except (ValidationError) as e:
            self.log(f"ValidationError: {e}")
            response = {"error": f"ValidationError: {e}"}
        except Exception as e:
            self.log(f"Exception: {e}")
            response = {"error": f"Exception: {e}"}
        if response is None:
            response:dict = {"NoData": "No data returned from Egeria for tech type processes for {self.selected_tech_type}"}
        if isinstance(response, dict) and "kind" in response:
            if response.get("kind") == "Empty":
                response:dict = {"NoData": "No data returned from Egeria for tech type processes for {self.selected_tech_type}"}
        # remove superfluous data from response
        response = self.unpack_egeria_data(response)
        new_response: list[dict] = [{}]
        counter = 0
        for item in response:
            for key, value in item.items():
                if key != "Mermaid" or "Mermaid Specification":
                    new_response[counter].update({key: value})
                    continue
                else:
                    # omit the Mermaid fields from the response
                    continue
            counter += 1
            continue

        # build and display tree of processes for selected tech type
        self.build_tech_processes_tree(new_response)

    def unpack_egeria_data(self, data) -> dict:
        """ Unpack the data returned from Egeria """
        output_data: list[dict] = [{}]
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
                            output_data = {"error": "unknown data structure"}
                else:
                    output_data = {"error": "unknown outer data structure"}
        else:
            output_data = {"error": "not dict or list", "shape": "data to unpack is not a recognized shape"}
        self.log(f"output_data: {output_data}, {type(output_data)}")
        # return the extracted data (dict)
        return(output_data)

    def build_tech_processes_tree(self, response_data):
       """ Create tree of processes for the selected tech_type"""
       self.response = response_data
       self.items.clear()
       try:
           self.proc_tree = self.query_one("#proc_tree", Tree)
           self.proc_tree.clear()
       except NoMatches:
           self.proc_tree: Tree = Tree("Processes", id = "proc_tree")
       except Exception as e:
           self.log(f"Exception building tree: {e}")
           self.exit(400)
       root_data = "A list of Processes associated with the selected technology type"
       self.proc_tree.auto_expand=True
       # self.proc_tree.root.expand()
       self.proc_tree.root.label = "Associated Processes"
       self.proc_tree.root.data = root_data
       tree_root = self.proc_tree.root
       self.processes = ""

       if not self.response:
           response_message = f"No data returned from Egeria for tech type processes for {self.selected_tech_type}"
           self.response = [{"Display Name": response_message}]
       if type(self.response) is dict:
           self.response = [self.response]
       if not isinstance(self.response, list):
           self.response = [self.response]
       self.log(f"response: {self.response}", type(self.response), len(self.response))
       for item in self.response:
           process_node = tree_root.add(str(item.get("Display Name")), expand=True)
           if len(self.response) > 0 and len(self.response[0]) >= 2:
                for key, value in self.response:
                   if isinstance(value, dict):
                        self.log(f"key: {key}, {type(key)}, {value}")
                        sub_node = process_node.add(label=(str(key)), expand=True)
                        for subkey, subvalue in value.items():
                            if isinstance(subvalue, dict):
                                self.log(f"subkey: {subkey}, {type(subkey)}, {subvalue}")
                                subprocess_node = sub_node.add(label=(str(subkey)), expand=True)
                                for subsubkey, subsubvalue in subvalue.items():
                                    self.log(f"subsubkey: {subsubkey}, {type(subsubkey)}, {subsubvalue}")
                                    subprocess_node.add_leaf(label=(str(subsubkey)), expand=True)
                                    continue
                            else:
                                self.log(f"subkey: {subkey}, {type(subkey)}, {subvalue}")
                                subprocess_node = sub_node.add_leaf(label=(str(subkey)), expand=True)
                                continue
                        else:
                            self.log(f"key: {key}, {type(key)}, {value}")
                            sub_node = tree_root.add_leaf(label=(str(key)), expand=True)
                            continue
                   else:
                       process_node.add_leaf(label=(str(key)), expand=True)
                       continue
           else:
                #if there is no input, skip
                continue

       # remove the technology type list and mount the processes tree
       self.query_one("#tech_type_data_container", Container).remove()
       self.query_one("#tech_type_data_container", Container).mount(self.proc_tree, before="#report_end")
       self.query_one("#tech_type_data_container", Container).refresh()

       self.heading = "Available Processes"
       self.subheading = "Select a Process to fill in required variables:"
       self.description = "A list of available processes, click on one"
       # self.tech_processes_tree = TechTypeDetails(self.selected_tech_type, self.response_data)


def start_myc():
    try:
        import pydevd_pycharm
        pydevd_pycharm.settrace(
            "127.0.0.1",
            port=5679,
            stdout_to_server=True,
            stderr_to_server=True,
            suspend=False  # Set to False to let the application continue running after starting
            )
    except ImportError:
        print("pydevd-pycharm not installed or setup failed. Debugger won't be active.")
        pass
    except Exception as e:
        print(f"Exception setting up debugger: {e}, execution will attempt to continue.")
        pass

    app = ReportSpec()
    os.environ.setdefault("EGERIA_PLATFORM_URL", "https://127.0.0.1:9443")
    os.environ.setdefault("EGERIA_VIEW_SERVER", "qs-view-server")
    os.environ.setdefault("EGERIA_USER", "erinoverview")
    os.environ.setdefault("EGERIA_USER_PASSWORD", "secret")
    app.run()

if __name__ == "__main__":
    app = ReportSpec()
    os.environ.setdefault("EGERIA_PLATFORM_URL", "https://127.0.0.1:9443")
    os.environ.setdefault("EGERIA_VIEW_SERVER", "qs-view-server")
    os.environ.setdefault("EGERIA_USER", "erinoverview")
    os.environ.setdefault("EGERIA_USER_PASSWORD", "secret")
    app.run()
