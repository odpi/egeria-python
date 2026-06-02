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
import re
import sys

from inflect import pl_sb_U_louse_lice_list
from textual.widget import WidgetError

# Ensure we're using the local pyegeria, not an installed version
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from typing import Any
from loguru import logger

from commands.cat.run_report import list_generic
from pyegeria import Run_Report
from pydantic import ValidationError
from textual import on
from textual.app import App
from textual.containers import Container, Horizontal, ScrollableContainer, HorizontalScroll
from textual.widgets import Static, Button, DataTable, Header, Footer, Placeholder, Input, Tree, Label


class MyApp(App):
    CSS_PATH = "./my_reports.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctl+e", "expand", "Expand Twisties"),
        ("r", "prepare_report", "Run"),
        ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.Egeria_config = ["https://127.0.0.1:9443", "qs-view-server", "erinoverview", "secret"]
        self.platform_url = self.Egeria_config[0]
        self.view_server = self.Egeria_config[1]
        self.user = self.Egeria_config[2]
        self.password = self.Egeria_config[3]
        self.selected_tech_type: str = ""
        self.items: list = []
        self.created_inputs: list[Input] = []
        self.inputs_tracker: dict[str, list] = {}
        self.snode_label: str = ""
        # Holds rotated data as column -> list of row values
        self.rotated_table: dict[str, list[str]] = {}

    def compose(self):
        self.title = "My_Egeria"
        self.sub_title = "Report Specification Details"
        yield Header()
        yield Container(
            Static("Start of Technology Type list:", id="one_start"),
            Tree(label="Tech Types", id="tech_table", classes="tables"),
            Static("End of report specification list:", id="one_end"),
            id="container1", classes="box")
        yield Container(
            Static("Report Specification Details", classes="box", id="two_start"),
            DataTable(id="spec_extracted_datatable"),
            Static("End of Report Specification Details", classes="box", id="two_end"),
            id="container2", classes="box")
        yield ScrollableContainer(
            Static("Report Specs Input Fields", classes="box", id="four_start"),
            Container(id="input_fields"),
            Static("End of Report Specs Input Fields", classes="box", id="four_end"),
            id="container4", classes="box")
        yield Container(
            Static("Report Specification Output)", classes="box", id="three_start"),
            DataTable(id="spec_output_datatable"),
            Static("End of Report Specification Output)", classes="box", id="three_end"),
            id="container3", classes="box")
        yield Footer()

    def on_mount(self):
        # Import here after path is set
        from pyegeria.format_set_executor import exec_report_spec
        from pyegeria.base_report_formats import Tech-Type-Processes
        from pyegeria import list_tech_types

        self.tech_tree = self.query_one("#tech_tree", Tree)
        self.tech_tree.clear()
        root_data = "A categorized list of Egeria supported Technology Types"
        self.tech_tree.root.expand()
        self.tech_tree.root.label = "Technology Types"
        self.tech_tree.root.data = root_data
        tree_root = self.tech_tree.root
        self.family: str = ""
        self.heading = "Report Specs"
        self.subheading = "Select a report spec to execute:"
        self.description = "A list of report specifications, click on one to see its attributes\ns key to run"

        try:
            self.tech_type_list: dict = list_tech_types(
                # format_set_name="Tech-Type-Processes",
                output_format="DICT",
            )
            logger.debug(f"tech_type_list: {self.tech_type_list}, type: {type(self.tech_type_list)}")
        except Exception as e:
            logger.debug(f"Error getting tech_type_list: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            self.tech_type_list = {}

        for type in self.tech_type_list:
            # if ttype.get("family") != self.family:
            #     self.family = spec.get("family")
            #     family_node = tree_root.add(self.family, data="family_name")
            #     family_node.expand()
            #     family_node.add(spec.get("name"), data=spec.get("description"))
            #     continue
            # else:
            #     family_node.add(spec.get("name"), spec.get("description"))
            #     continue
        tree_root.collapse_all()
        self.tech_tree.refresh()

    @on(Tree.NodeSelected, "#tech_tree")
    async def handle_tech_tree_node_selected(self, message: Tree.NodeSelected):
        logger.debug(f"Node Selected, Processing selection")
        self.selected_tech_type = message.node
        logger.debug(f"selected_tech_type: {self.selected_tech_type}")
        snode = message.node
        logger.debug(f"snode: {snode}", type(snode))
        if snode.data:
            snode_label = str(snode.label)
            logger.debug(f"snode_label: {snode_label}", type(snode_label))
        else:
            snode_label = str(snode.label)
            logger.debug(f"snode_label: {snode_label}", type(snode_label))
            # address input fields container so we can clear it from prior selections
            inputs_container = self.query_one("#input_fields", Container)
            # Clear previous rows
            try:
                self.created_inputs: list[Input] = []
                # Remove all existing children synchronously
                for child in list(inputs_container.children):
                    await child.remove()
            except Exception as e:
                # if this is first time through there is validly no container to clear
                logger.debug(f"Exception clearing inputs container: {e} possibly first time through")
            except WidgetError:
                # assume this is forst time through and container is not yet created
                pass
            self.snode_label = snode_label
            await self.get_named_tech_type_details(snode_label)

        if "DICT" or "FORM" in self.inputs_tracker:
            outlabel = Label("Output Format: DICT to display report on screen, FORM to write to file", id="comment1")
            await inputs_container.mount(outlabel)

    async def get_named_tech_type_details(self, name):
        """Get the details of a named report spec and render as a flat table."""
        from pyegeria.base_report_formats import

        self.spec_name = name
        logger.debug(f"get_named_tech_type_details: {self.spec_name}")
        selected_tech_type = select_tech_type(self.spec_name, output_type="DICT")
        logger.debug(f"selected_tech_type: {selected_tech_type}, type: {type(selected_tech_type)}")
        if selected_tech_type == None:
            selected_tech_type = {"NoDetails": "No details found for selected report spec"}
        # Normalize the shape of the returned spec → always a dict
        if isinstance(selected_tech_type, dict) and "data" in selected_tech_type:
            self.extracted_tech_type: dict = selected_tech_type.get("data") or {}
        elif isinstance(selected_tech_type, dict):
            self.extracted_tech_type: dict = selected_tech_type or {}
        else:
            error_text = f"Unknown shape: {selected_tech_type}"
            self.extracted_tech_type = {"Error": error_text}

        logger.debug(f"extracted_tech_type: {self.extracted_tech_type}, type: {type(self.extracted_tech_type)}")
        response_data = self.extracted_tech_type
        # Access the datatable used to display report specification attributes
        self.spec_attribute_datatable = self.query_one("#spec_extracted_datatable", DataTable)
        # Ensure columns exist only once
        self.spec_attribute_datatable.clear(columns=True)
        self.spec_attribute_datatable.add_columns("Attribute", "Value", "Extended Values")
        self.spec_attribute_datatable.border = True
        self.spec_attribute_datatable.zebra_stripes = True
        self.spec_attribute_datatable.cursor_type = "row"
        self.spec_attribute_datatable.refresh()

        if not response_data:
            response_data = {"NoData": "No data found for selected item"}
        if isinstance(response_data, list):
            for list_item in response_data:
                response_data: dict = list_item
                logger.debug(f"list_item: {list_item}")
                if isinstance(response_data, dict):
                    for key, value in response_data.items():
                        logger.debug(f"key: {key}, value: {value}")
                        # check for input capable report spec parms
                        if key == "required_params" or key == "optional_params" or key == "spec_params" or key == "types":
                            logger.debug(f"Executing populate_input_fields for key: {key}")
                            await self.populate_input_fields(key, value)
                            logger.debug(f"populate_input_fields completed for key: {key}")
                        logger.debug(f"key: {key}, value: {value}")
                        if isinstance(value, dict):
                            for vkey, vvalue in value.items():
                                if vkey == "required_params" or vkey == "optional_params" or vkey == "spec_params" or vkey == "types":
                                    logger.debug(f"Executing populate_input_fields for key: {vkey}")
                                    await self.populate_input_fields(vkey, vvalue)
                                    logger.debug(f"populate_input_fields completed for key: {vkey}")
                                logger.debug(f"vkey: {vkey}, vvalue: {vvalue}")
                                self.spec_attribute_datatable.add_row(vkey, vvalue)
                                continue
                        elif isinstance(value, list):
                            for v in value:
                                logger.debug(f"v: {v}")
                                self.spec_attribute_datatable.add_row(key, v)
                                continue
                        elif key == "kind" and value == "empty":
                            key_str = "No Data"
                            value_str = "For That Asset Type in this repository"
                            logger.debug(f"key_str: {key_str}, value_str: {value_str}")
                            self.spec_attribute_datatable.add_row(key_str, value_str)
                            continue
                        elif isinstance(value, dict):
                            for vkey, vvalue in value.items():
                                logger.debug(f"vkey: {vkey}, vvalue: {vvalue}")
                                self.spec_attribute_datatable.add_row(vkey, vvalue)
                                continue
                        else:
                            logger.debug(f"else: key {key} value: {value}")
                            self.spec_attribute_datatable.add_row(key, value)
                            continue
        elif isinstance(response_data, dict):
            for key, value in response_data.items():
                logger.debug(f"key: {key}, value: {value}")
                if key == "required_params" or key == "optional_params" or key == "spec_params" or key == "types":
                    logger.debug(f"Executing populate_input_fields for key: {key}")
                    await self.populate_input_fields(key, value)
                    logger.debug(f"populate_input_fields completed for key: {key}")
                if isinstance(value, dict):
                    for vkey, vvalue in value.items():
                        if vkey == "required_params" or vkey == "optional_params" or vkey == "spec_params" or vkey == "types":
                            logger.debug(f"Executing populate_input_fields for key: {vkey}")
                            await self.populate_input_fields(vkey, vvalue)
                            logger.debug(f"populate_input_fields completed for key: {vkey}")
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

    async def execute_selected_tech_type(self, selected_name: str = "", additional_parameters: dict = None):
        """ execute the selected report spec """
        from pyegeria.format_set_executor import Run_Report

        self.selected_name = selected_name
        self.additional_parameters = additional_parameters
        output_form = "DICT"
        if len(self.additional_parameters) > 0:
            logger.debug(f"additional_parameters: {self.additional_parameters}")
            for key, value in self.additional_parameters.items():
                if value == "True" or value == "False":
                    self.additional_parameters[key] = bool(value)
        else:
            logger.debug(f"No additional parameters provided")
            self.additional_parameters = {}
        if self.additional_parameters != None:
            if "inp_types" in self.additional_parameters:
                output_form = self.additional_parameters["inp_types"]

        logger.debug(f"Executing report spec: {self.selected_name}")
        try:
            reponse = exec_tech_type(format_set_name=selected_name,
                                       output_format=output_form,
                                       view_server=self.view_server,
                                       view_url=self.platform_url,
                                       user=self.user,
                                       user_pass=self.password,
                                       params=self.additional_parameters
                                       )
            logger.debug(f"Return from exec_tech_type:")
            logger.debug(f"reponse: {reponse}")
        except (ValidationError) as e:
            logger.debug(f"ValidationError: {e}")
            reponse = {"error": f"ValidationError: {e}"}
        except Exception as e:
            logger.debug(f"Exception: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            reponse = {"error": f"Exception: {e}"}
        await self.display_response(reponse)

    async def display_response(self, response):
        """ Display the response from executing the selected report spec"""
        self.response = response
        # create and/or clear datatable for displaying data
        self.spec_output_datatable = self.query_one("#spec_output_datatable", DataTable)
        self.spec_output_datatable.clear(columns=True)
        logger.debug(f"self.spec_output_datatable : {self.spec_output_datatable} has been created")
        logger.debug(f"self.spec_output_datatable has been assigned an id : {self.spec_output_datatable.id} ")
        # extract data payload from response["data"]. Then populate variables for display
        if isinstance(self.response, dict) and "data" in self.response:
            self.response_data = self.response.get("data")
        elif isinstance(self.response, dict):
            self.response_data = self.response
        elif isinstance(self.response, list):
            self.response_data = self.response
        else:
            self.response_data = [{"NoData": "No data found for selected item", "Data Content": self.response}]

        self.rotated_table.clear()
        if isinstance(self.response_data, list):
            for list_item in self.response_data:
                response_dict = list_item if isinstance(list_item, dict) else {"Value": list_item}
                logger.debug(f"list_item: {list_item}")
                for key, value in response_dict.items():
                    logger.debug(f"key: {key}, value: {value}")
                    if isinstance(value, dict):
                        for vkey, vvalue in value.items():
                            logger.debug(f"vkey: {vkey}, vvalue: {vvalue}")
                            self.rotated_table.setdefault(str(vkey), []).append(vvalue)
                    elif isinstance(value, list):
                        for v in value:
                            logger.debug(f"v: {v}")
                            self.rotated_table.setdefault(str(v), []).append(" ")
                    elif key == "kind" and value == "empty":
                        key_str: str = "NoData"
                        message: str = "For That Asset Type in this repository"
                        logger.debug(f"key_str: {key_str}, value_str: {message}")
                        # Present a single consolidated message row under NoData
                        self.rotated_table[key_str] = [message]
                    else:
                        logger.debug(f"else: key {key} value: {value}")
                        self.rotated_table.setdefault(str(key), []).append(value)
        elif isinstance(self.response_data, dict):
            for key, value in self.response_data.items():
                logger.debug(f"key: {key}, value: {value}")
                if key == "kind":
                    continue
                elif isinstance(value, dict):
                    for vkey, vvalue in value.items():
                        self.rotated_table.setdefault(str(vkey), []).append(vvalue)
                elif isinstance(value, list):
                    for v in value:
                        self.rotated_table.setdefault(str(v), []).append(" ")
                elif key == "kind" and value == "empty":
                    key_str = "NoData"
                    message = "For That Asset Type in this repository"
                    logger.debug(f"key_str: {key_str}, value_str: {message}")
                    # Present a single consolidated message row under NoData
                    self.rotated_table[key_str] = [message]
                else:
                    self.rotated_table.setdefault(str(key), []).append(value)
        # now the rotated table is loaded with data, create the datatable
        keys = list(self.rotated_table.keys())
        for col_key in keys:
            self.spec_output_datatable.add_column(str(col_key))
        max_rows = max((len(self.rotated_table[k]) for k in keys), default=0)
        for row_idx in range(max_rows):
            row = [str(self.rotated_table[k][row_idx]) if row_idx < len(self.rotated_table[k]) else "" for k in keys]
            self.spec_output_datatable.add_row(*row)

        # Always refresh after populating
        self.spec_output_datatable.refresh()
        mount_point = self.query_one("#container3", Container)
        await mount_point.mount(self.spec_output_datatable, before="#three_end")
        return

    async def populate_input_fields(self, key, value):
        """Create interactive input rows for required/optional params."""
        self.key = key
        self.input = value
        inp_value: Any = None
        inputs_container = self.query_one("#input_fields", Container)

        def safe_id(s: str) -> str:
            return re.sub(r"[^0-9a-zA-Z_-]", "_", s)

        self.created_inputs: list[Input] = []
        # reset tracker for this render; we'll repopulate with the current inputs
        self.inputs_tracker.clear()

        # Build rows according to incoming shape
        if isinstance(self.input, dict):
            items = list(self.input.items())
            for ikey, ivalue in items:
                row = HorizontalScroll(id=f"input_row_{safe_id(str(ikey))}")
                await inputs_container.mount(row)
                await row.mount(Label(f"{ikey}:"))
                logger.debug(f"Processing input field: {ikey}")
                if ikey == "search_string":
                    inp_value = "*"
                elif ikey == "page_size":
                    inp_value = '0'
                elif ikey == "start_from":
                    inp_value = '0'
                elif ikey == "starts_with":
                    inp_value = "True"
                elif ikey == "ends_with":
                    inp_value = "False"
                elif ikey == "ignore_case":
                    inp_value = "False"
                elif ikey == "output_format":
                    inp_value = "DICT"
                else:
                    inp_value = ""
                inp = Input(value=inp_value, placeholder=str(ivalue), id=f"inp_{safe_id(str(ikey))}", classes="spaced")
                await row.mount(inp)
                self.created_inputs.append(inp)
                # Track by input id so events can update values reliably
                self.inputs_tracker[inp.id] = [str(ikey), ""]
        elif isinstance(self.input, list):
            # Special-case for types: just display info text
            if key == "types":
                row = Horizontal(id=f"input_row_{safe_id(str(key))}")
                await inputs_container.mount(row)
                await row.mount(Label("Output Format:"))
                await row.mount(Input(value="DICT", placeholder="DICT", id=f"inp_{safe_id(str(key))}", classes="spaced"))
                # informational only; no input to track
            else:
                for list_item in self.input:
                    label = str(list_item)
                    row = Horizontal(id=f"input_row_{safe_id(label)}")
                    await inputs_container.mount(row)
                    await row.mount(Label(f"{label}:"))
                    logger.debug(f"Processing input field: {label}")
                    if label == "search_string":
                        inp_value = "*"
                    elif label == "page_size":
                        inp_value = '0'
                    elif label == "start_from":
                        inp_value = '0'
                    elif label == "starts_with":
                        inp_value = "True"
                    elif label == "ends_with":
                        inp_value = "False"
                    elif label == "ignore_case":
                        inp_value = "False"
                    elif label == "output_format":
                        inp_value = "DICT"
                    else:
                        inp_value = ""
                    if isinstance(inp_value, list):
                        inp_value = ", ".join(inp_value)
                        logger.debug(f"inp_value: {inp_value}")
                    inp = Input(value=inp_value, placeholder="", id=f"inp_{safe_id(label)}")
                    await row.mount(inp)
                    self.created_inputs.append(inp)
                    # Track with a reasonable parameter name for list entries
                    self.inputs_tracker[inp.id] = [label, ""]
        else:
            # Unknown shape: show a message
            row = Horizontal(id=f"input_row_{safe_id(str(key))}")
            await inputs_container.mount(row)
            await row.mount(Label(f"Error, Unknown Shape for {key}: {value}"))

        # Give focus to the first input if any
        if self.created_inputs:
            self.created_inputs[0].focus()
        logger.debug(f"inputs_tracker: {self.inputs_tracker}")

        # Refresh the container
        inputs_container.refresh()
        return

    @on(Input.Changed, "#input_fields Input")
    async def handle_input_changed(self, event: Input.Changed) -> None:
        """Update the tracker whenever an input changes.

        We key the tracker by the actual Input id and store [param_name, value].
        """
        input_id = event.input.id
        value = event.value or ""
        # Initialize if missing (defensive)
        if input_id not in self.inputs_tracker:
            # Default param name falls back to the visible label-less id
            self.inputs_tracker[input_id] = [input_id, value]
        else:
            self.inputs_tracker[input_id][1] = value
        logger.debug(f"Changed: {input_id} -> {value}")
        return

    @on(Button.Pressed, "#quit")
    def handle_quit(self, event: Button.Pressed) -> None:
        self.exit(200)

    def action_quit(self):
        self.exit(200)

    def action_expand_spec_attribute_table(self):
        self.tech_tree.root.expand_all()
        return

    async def action_prepare_report(self):
        # Build additional parameters from current inputs
        self.new_additional_parameters = {}
        self.additional_parameters = {}
        if self.inputs_tracker:
            logger.debug(f"self.inputs_tracker: {self.inputs_tracker}")
            for _, (parm_name, parm_value) in self.inputs_tracker.items():
                self.additional_parameters[parm_name] = parm_value
        logger.debug(f"additional_parameters: {self.additional_parameters}")
        # run report when input fields completed
        # iterate and strip the inp_ from the front of the key values if present
        for key, value in self.additional_parameters.items():
            new_key:str = key.removeprefix("inp_")
            self.new_additional_parameters.update({new_key: value})
        self.additional_parameters.clear()
        # change the types key to output_format if present fior inclusion in parameters dict
        value = self.new_additional_parameters.get("types")
        if value:
            self.new_additional_parameters.update({"output_format": value})
        else:
            self.new_additional_parameters.update({"output_format": "DICT"})
        self.log (f"new_additional_parameters: {self.new_additional_parameters}")
        self.additional_parameters = self.new_additional_parameters
        logger.debug(f"additional_parameters trimmed: {self.additional_parameters}")
        # Retrieve the output_format value
        output_form = self.additional_parameters.get("output_format", "FORM")
        logger.debug(f"output_format: {output_form}")
        # if output_format is FORM, we write the report output to a file
        # if not then we execute the report spec and display the output on the screen
        if output_form == "FORM":
            await self.report_to_file(self.snode_label, self.additional_parameters)
        else:
            await self.execute_selected_tech_type(self.snode_label, self.additional_parameters)
        return

    async def report_to_file(self, selected_name: str = "", additional_parameters: dict = None):
        """ execute the selected report spec """
        # self.selected_name = selected_name
        # self.additional_parameters = additional_parameters
        my_additional_parameters: dict = additional_parameters
        output_form = "FORM"
        if len(my_additional_parameters) > 0:
            logger.debug(f"additional_parameters: {my_additional_parameters}")
            if "output_format" in my_additional_parameters:
                output_form = my_additional_parameters.get("output_format")
                del my_additional_parameters["output_format"]
            else:
                output_form = "FORM"
        else:
            logger.debug(f"No additional parameters provided")
            my_additional_parameters = {}

        logger.debug(f"Executing report spec: {selected_name}")
        try:
            reponse = list_generic(tech_type=selected_name,
                                   output_format=output_form,
                                   view_server=self.view_server,
                                   view_url=self.platform_url,
                                   user=self.user,
                                   user_pass=self.password,
                                   params=my_additional_parameters,
                                   write_file=True
                                )
            logger.debug(f"Return from exec_tech_type:")
            logger.debug(f"reponse: {reponse}")
        except (ValidationError) as e:
            logger.debug(f"ValidationError: {e}")
            reponse = {"error": f"ValidationError: {e}"}
        except Exception as e:
            logger.debug(f"Exception: {e}")
            reponse = {"error": f"Exception: {e}"}
        await self.display_response(reponse)

def start_exp2():
    app = MyApp()
    app.run()

if __name__ == "__main__":
    start_exp2()