""" python

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a utility function for my_egeria.

    This file is being used to test some display layout options
    This is a test file to explore different ways to display Egeria data
    Author: Peter Coldicott, November 2025

    This version is to test having the user input required parameters to run
    customized reports

"""

import os
import sys

# Ensure we're using the local pyegeria, not an installed version
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from pydantic import ValidationError
from textual import on
from textual.app import App
from textual.containers import Container, Horizontal
from textual.widgets import Static, Button, DataTable, Header, Footer, Placeholder, Input, Tree


class MyApp(App):
    CSS_PATH = "./my_reports.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "show report", "Show"), ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.Egeria_config = ["https://127.0.0.1:9443", "qs-view-server", "erinoverview", "secret"]
        self.platform_url = self.Egeria_config[0]
        self.view_server = self.Egeria_config[1]
        self.user = self.Egeria_config[2]
        self.password = self.Egeria_config[3]
        self.selected_report_spec: str = ""
        self.items: list = []

    def compose(self):
        yield Header()
        yield Container(
            Static("Start of report specification list:", id="one_start"),
            Tree(label="Report Specs", id="spec_tree", classes="trees"),
            Static("End of report specification list:", id="one_end"),
            id="container1", classes="box")
        yield Container(
            Static("Report Specification Details", classes="box", id="two_start"),
            DataTable(id="spec_extracted_datatable"),
            Static("End of Report Specification Details", classes="box", id="two_end"),
            id="container2", classes="box")
        yield Container(
            Static("Report Specification Output)", classes="box", id="three_start"),
            DataTable(id="spec_output_datatable"),
            Static("End of Report Specification Output)", classes="box", id="three_end"),
            id="container3", classes="box")
        yield Container(
            Static("Report Specs Input Fields", classes="box", id="four_start"),
            Placeholder(id="input_fields"),
            Static("End of Report Specs Input Fields", classes="box", id="four_end"),
            id="container4", classes="box"
        )
        yield Container(
            Button("Quit", variant="primary", id="quit"),
            id="action_row"
        )
        yield Footer()

    def on_mount(self):
        # Import here after path is set
        from pyegeria.base_report_formats import report_spec_list

        self.spec_tree = self.query_one("#spec_tree", Tree)
        self.spec_tree.clear()
        root_data = "A categorized list of PyEgeria report specifications"
        self.spec_tree.root.expand()
        self.spec_tree.root.label = "Report Specs"
        self.spec_tree.root.data = root_data
        tree_root = self.spec_tree.root
        self.family: str = ""
        self.heading = "Report Specs"
        self.subheading = "Select a report spec to execute:"
        self.description = "A list of report specifications, click on one to see its attributes\ns key to run"

        try:
            self.report_spec_list: list = report_spec_list(show_family=True, sort_by_family=True, return_kind="dicts")
            self.log(f"report_spec_list: {self.report_spec_list}, type: {type(self.report_spec_list)}")
        except Exception as e:
            self.log(f"Error getting report_spec_list: {e}")
            import traceback
            self.log(traceback.format_exc())
            self.report_spec_list = []

        for spec in self.report_spec_list:
            if spec.get("family") != self.family:
                self.family = spec.get("family")
                family_node = tree_root.add(self.family, data="family_name")
                family_node.expand()
                family_node.add(spec.get("name"), data=spec.get("description"))
                continue
            else:
                family_node.add(spec.get("name"), spec.get("description"))
                continue
        self.spec_tree.refresh()

    @on(Tree.NodeSelected, "#spec_tree")
    async def handle_spec_tree_node_selected(self, message: Tree.NodeSelected):
        self.log(f"Node Selected, Processing selection")
        self.selected_report_spec = message.node
        self.log(f"selected_report_spec: {self.selected_report_spec}")
        snode = message.node
        self.log(f"snode: {snode}", type(snode))
        if snode.data:
            snode_label = str(snode.label)
            self.log(f"snode_label: {snode_label}", type(snode_label))
        else:
            snode_label = str(snode.label)
            self.log(f"snode_label: {snode_label}", type(snode_label))
        await self.get_named_report_spec_details(snode_label)
        await self.execute_selected_report_spec(snode_label)

    async def get_named_report_spec_details(self, name):
        """Get the details of a named report spec and render as a flat table."""
        from pyegeria.base_report_formats import select_report_spec

        self.spec_name = name
        self.log(f"get_named_report_spec_details: {self.spec_name}")
        selected_report_spec = select_report_spec(self.spec_name, output_type="DICT")
        self.log(f"selected_report_spec: {selected_report_spec}, type: {type(selected_report_spec)}")
        if selected_report_spec == None:
            selected_report_spec = {"NoDetails": "No details found for selected report spec"}
        # Normalize the shape of the returned spec → always a dict
        if isinstance(selected_report_spec, dict) and "data" in selected_report_spec:
            self.extracted_report_spec: dict = selected_report_spec.get("data") or {}
        elif isinstance(selected_report_spec, dict):
            self.extracted_report_spec: dict = selected_report_spec or {}
        else:
            error_text = f"Unknown shape: {selected_report_spec}"
            self.extracted_report_spec = {"Error": error_text}

        self.log(f"extracted_report_spec: {self.extracted_report_spec}, type: {type(self.extracted_report_spec)}")
        response_data = self.extracted_report_spec
        # Access the datatable used to display report specification attributes
        self.spec_attribute_datatable = self.query_one("#spec_extracted_datatable", DataTable)
        # Ensure columns exist only once
        self.spec_attribute_datatable.clear(columns=True)
        self.spec_attribute_datatable.add_columns("Attribute", "Value", "Extended Values")
        self.spec_attribute_datatable.border = True
        self.spec_attribute_datatable.zebra_stripes = True
        self.spec_attribute_datatable.cursor_type = "row"
        self.spec_attribute_datatable.refresh()

        if not response_data or response_data == None or response_data == "":
            response_data = {"NoData": "No data found for selected item"}
        if isinstance(response_data, list):
            for list_item in response_data:
                response_data: dict = list_item
                self.log(f"list_item: {list_item}")
                if isinstance(response_data, dict):
                    for key, value in response_data.items():
                        self.log(f"key: {key}, value: {value}")
                        # check for input capable report spec parms
                        if key == "required_params" or key == "optional_params" or key == "spec_params" or key == "types":
                            self.log(f"Executing populate_input_fields for key: {key}")
                            self.populate_input_fields(key, value)
                            self.log(f"populate_input_fields completed for key: {key}")
                        self.log(f"key: {key}, value: {value}")
                        if isinstance(value, dict):
                            for vkey, vvalue in value.items():
                                if vkey == "required_params" or vkey == "optional_params" or vkey == "spec_params" or vkey == "types":
                                    self.log(f"Executing populate_input_fields for key: {vkey}")
                                    self.populate_input_fields(vkey, vvalue)
                                    self.log(f"populate_input_fields completed for key: {vkey}")
                                self.log(f"vkey: {vkey}, vvalue: {vvalue}")
                                self.spec_attribute_datatable.add_row(vkey, vvalue)
                                continue
                        elif isinstance(value, list):
                            for v in value:
                                self.log(f"v: {v}")
                                self.spec_attribute_datatable.add_row(key, v)
                                continue
                        elif key == "kind" and value == "empty":
                            key_str = "No Data"
                            value_str = "For That Asset Type in this repository"
                            self.log(f"key_str: {key_str}, value_str: {value_str}")
                            self.spec_attribute_datatable.add_row(key_str, value_str)
                            continue
                        else:
                            self.log(f"else: key {key} value: {value}")
                            self.spec_attribute_datatable.add_row(key, value)
                            continue
        elif isinstance(response_data, dict):
            for key, value in response_data.items():
                self.log(f"key: {key}, value: {value}")
                if key == "required_params" or key == "optional_params" or key == "spec_params" or key == "types":
                    self.log(f"Executing populate_input_fields for key: {key}")
                    self.populate_input_fields(key, value)
                    self.log(f"populate_input_fields completed for key: {key}")
                if isinstance(value, dict):
                    for vkey, vvalue in value.items():
                        if vkey == "required_params" or vkey == "optional_params" or vkey == "spec_params" or vkey == "types":
                            self.log(f"Executing populate_input_fields for key: {vkey}")
                            self.populate_input_fields(vkey, vvalue)
                            self.log(f"populate_input_fields completed for key: {vkey}")
                        self.spec_attribute_datatable.add_row(vkey, vvalue)
                        continue
                elif isinstance(value, list):
                    for v in value:
                        self.spec_attribute_datatable.add_row(key, v)
                        continue
                elif key == "kind" and value == "empty":
                    key_str = "No Data"
                    value_str = "For That Asset Type in this repository"
                    self.spec_attribute_datatable.add_row(key_str, value_str)
                    continue
                else:
                    self.spec_attribute_datatable.add_row(key, value)
                    continue

        self.spec_attribute_datatable.refresh()
        mount_point = self.query_one("#container2", Container)
        await mount_point.mount(self.spec_attribute_datatable, before="#two_end")
        return

    async def execute_selected_report_spec(self, selected_name: str = ""):
        """ execute the selected report spec """
        from pyegeria.format_set_executor import exec_report_spec

        self.selected_name = selected_name
        self.log(f"Executing report spec: {self.selected_name}")
        try:
            reponse = exec_report_spec(format_set_name=selected_name,
                                       output_format="DICT",
                                       view_server=self.view_server,
                                       view_url=self.platform_url,
                                       user=self.user,
                                       user_pass=self.password)
            self.log(f"Return from exec_report_spec:")
            self.log(f"reponse: {reponse}")
        except (ValidationError) as e:
            self.log(f"ValidationError: {e}")
            reponse = {"error": f"ValidationError: {e}"}
        except Exception as e:
            self.log(f"Exception: {e}")
            import traceback
            self.log(traceback.format_exc())
            reponse = {"error": f"Exception: {e}"}
        await self.display_response(reponse)

    async def display_response(self, response):
        """ Display the response from executing the selected report spec"""
        self.response = response
        # create and/or clear datatable for displaying data
        self.spec_output_datatable = self.query_one("#spec_output_datatable", DataTable)
        self.spec_output_datatable.clear(columns=True)
        self.log(f"self.spec_output_datatable : {self.spec_output_datatable} has been created")
        # self.spec_output_datatable.id = "spec_output_datatable"
        self.log(f"self.spec_output_datatable has been assigned an id : {self.spec_output_datatable.id} ")
        self.spec_output_datatable.add_columns("Key", "Value", "Description")
        self.log(f"self.spec_output_datatable has been assigned columns {self.spec_output_datatable.columns}")
        # extract data payload from response["data"]. Then populate variables for display
        if isinstance(self.response, dict) and "data" in self.response:
            self.response_data = self.response.get("data")
        elif isinstance(self.response, dict):
            self.response_data = self.response
        elif isinstance(self.response, list):
            self.response_data = self.response
        else:
            response_data = [{"NoData": "No data found for selected item", "Data Content": self.response}]

        if isinstance(self.response_data, list):
            for list_item in self.response_data:
                response_dict = list_item if isinstance(list_item, dict) else {"Value": list_item}
                self.log(f"list_item: {list_item}")
                for key, value in response_dict.items():
                    self.log(f"key: {key}, value: {value}")
                    if isinstance(value, dict):
                        for vkey, vvalue in value.items():
                            self.log(f"vkey: {vkey}, vvalue: {vvalue}")
                            self.spec_output_datatable.add_row(str(vkey), str(vvalue), "")
                    elif isinstance(value, list):
                        for v in value:
                            self.log(f"v: {v}")
                            self.spec_output_datatable.add_row(str(key), str(v), "")
                    elif key == "kind" and value == "empty":
                        key_str = "No Data"
                        value_str = "For That Asset Type in this repository"
                        self.log(f"key_str: {key_str}, value_str: {value_str}")
                        self.spec_output_datatable.add_row(key_str, value_str, "")
                    else:
                        self.log(f"else: key {key} value: {value}")
                        self.spec_output_datatable.add_row(str(key), str(value), "")

        elif isinstance(self.response_data, dict):
            for key, value in self.response_data.items():
                self.log(f"key: {key}, value: {value}")
                if key == "kind":
                    continue
                elif isinstance(value, dict):
                    for vkey, vvalue in value.items():
                        self.spec_output_datatable.add_row(str(vkey), str(vvalue), "")
                elif isinstance(value, list):
                    for v in value:
                        self.spec_output_datatable.add_row(str(key), str(v), "")
                elif key == "kind" and value == "empty":
                    key_str = "No Data"
                    value_str = "For That Asset Type in this repository"
                    self.spec_output_datatable.add_row(key_str, value_str, "")
                else:
                    self.spec_output_datatable.add_row(str(key), str(value), "")

        # Always refresh after populating
        self.spec_output_datatable.refresh()
        mount_point = self.query_one("#container3", Container)
        await mount_point.mount(self.spec_output_datatable, before="#three_end")
        return

    def populate_input_fields(self, key, value):
        """ Take input (optional or required) parameters and populate the input fields table"""
        self.key = key
        self.input = value
        new_input = Horizontal()
        self.log(f"populate_input_fields: {self.key}, type: {type(self.key)}, {self.input}, type: {type(self.input)}")
        if isinstance(self.input, dict):
            for ikey, ivalue in self.input.items():
                self.log(f"key: {key}, value: {value}")
                new_input = Horizontal(id="input_field" + str(ikey))
                try:
                    self.query_one("#input_fields").remove()
                    self.query_one("#container4").mount(new_input, before="#four_end")
                    new_input.mount(Static(f"{ikey}+{str(ivalue)}:"))
                    new_input.mount(Input(" ", classes="input_fields"))
                except Exception as e:
                    self.log(f"Exception replacing placeholder: {e}")
                self.query_one("#container4").refresh()
        elif isinstance(self.input, list):
            for list_item in self.input:
                # check for type field, if so, handle specifically
                if key == "types":
                    new_input = Horizontal(id="input_field" + str(key))
                    try:
                        self.query_one("#input_fields").remove()
                        self.query_one("#container4").mount(new_input, before="#four_end")
                        new_input.mount(Static(f"DICT:"))
                        new_input.mount(Static(" DICT is required to run the report in this program"))
                    except Exception as e:
                        self.log(f"Exception replacing placeholder: {e}")
                    self.query_one("#container4").refresh()
                else:
                    new_input = Horizontal(id="input_field" + str(list_item))
                    try:
                        self.query_one("#input_fields").remove()
                        self.query_one("#container4").mount(new_input, before="#four_end")
                        new_input.mount(Static(f"{list_item}:"))
                        new_input.mount(Input("", classes="input_fields"))
                    except Exception as e:
                        self.log(f"Exception replacing placeholder: {e}")
                    self.query_one("#container4").refresh()
        else:
            new_input = Horizontal(id="input_field" + str(key))
            try:
                self.query_one("#input_fields").remove()
                self.query_one("#container4").mount(new_input, before="#four_end")
                new_input.mount(Static(f"Error, Unknown Shape for {key}: {value}"))
            except Exception as e:
                self.log(f"Exception replacing placeholder: {e}")
            self.query_one("#container4").refresh()
        return

    @on(Button.Pressed, "#quit")
    def handle_quit(self, event: Button.Pressed) -> None:
        self.action_quit()

    def action_quit(self):
        self.exit()

def start_exp2():
    app = MyApp()
    app.run()



if __name__ == "__main__":
    start_exp2()