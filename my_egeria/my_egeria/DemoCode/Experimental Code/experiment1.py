""" python

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a utility function for my_egeria.

    This file is being used to test some display layout options
    This is a test file to explore different ways to display Egeria data
    Author: Peter Coldicott, November 2025

"""

import os

from pydantic import ValidationError
from pyegeria.base_report_formats import report_spec_list, get_report_format_description, select_report_spec
from pyegeria.format_set_executor import exec_report_spec
from textual import on
from textual.app import App
from textual.containers import Container
from textual.widgets import Static, Button, DataTable, Header, Footer

class MyApp(App):
    CSS_PATH = "experiment1.tcss"

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
            DataTable(id="spec_datatable"),
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
            Button("Quit", id="quit"),
            id = "action_row"
        )
        yield Footer()

    def on_mount(self):
        self.spec_datatable = self.query_one("#spec_datatable", DataTable)
        self.spec_datatable.clear(columns=True)
        self.spec_datatable.add_columns("Name", "Description", "")
        self.spec_datatable.zebra_stripes = True
        self.spec_datatable.cursor_type = "row"
        num_columns = len(self.spec_datatable.columns)
        self.log(f"Number of columns: {num_columns}")
        self.heading = "Report Specs"
        self.subheading = "Select a report spec to execute:"
        self.description = "A list of report specifications, click on one to see its attributes\ns key to run"
        self.report_spec_list: list = report_spec_list()
        self.log(f"report_spec_list: {self.report_spec_list}, type: {type(self.report_spec_list)}")
        for spec in self.report_spec_list:
            if not isinstance(spec, str):
                spec = str(spec)
            self.log(f"spec: {spec}")
            desc = get_report_format_description(spec)
            if not isinstance(desc, str):
                desc = str(desc)
            self.log(f"desc: {desc}")
            self.spec_datatable.add_row(spec, desc)
        self.spec_datatable.refresh()

    @on(DataTable.RowSelected, "#spec_datatable")
    async def handle_spec_table_row_selected(self, message: DataTable.RowSelected):
        self.log(f"Row Selected, Processing selection")
        self.selected_report_spec = message.row_key
        self.log(f"selected_report_spec: {self.selected_report_spec}")
        self.selected_row_data = self.spec_datatable.get_row(message.row_key)
        self.log(f"selected_row: {self.selected_row_data}")
        self.selected_name = str(self.selected_row_data[0] or "")
        self.log(f"selected_name: {self.selected_name}")
        await self.get_named_report_spec_details(self.selected_name)
        await self.execute_selected_report_spec(self.selected_name)

    async def get_named_report_spec_details(self, name):
        """Get the details of a named report spec and render as a flat table.

        Simplified approach:
        - Normalize the incoming spec to a dict.
        - Recursively walk dicts/lists with a small helper that yields rows.
        - Use a path convention where the first segment is shown in "Attribute",
          the remaining path (if any) is shown in "Value", and the leaf value in
          "Extended Values". This keeps the UI compact while preserving structure.

        """

        self.spec_name = name
        self.log(f"get_named_report_spec_details: {self.spec_name}")
        selected_report_spec = select_report_spec(self.spec_name, output_type="DICT")
        self.log(f"selected_report_spec: {selected_report_spec}, type: {type(selected_report_spec)}")

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
                        if isinstance(value, dict):
                            for vkey, vvalue in value.items():
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
        if isinstance(response_data, dict):
            for key, value in response_data.items():
                self.log(f"key: {key}, value: {value}")
                if isinstance(value, dict):
                    for vkey, vvalue in value.items():
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

    @on(Button.Pressed, "#quit")
    def handle_quit(self, event: Button.Pressed) -> None:
        self.action_quit()

    def action_quit(self):
        self.exit()

if __name__ == "__main__":
    app = MyApp()
    app.run()