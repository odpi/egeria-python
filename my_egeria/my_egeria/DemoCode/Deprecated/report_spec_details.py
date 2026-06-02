"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""
import time
from datetime import datetime
from typing import Optional
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Container
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Static, ListView, Button, Footer, Header
from textual.reactive import reactive
from textual.widgets._data_table import DataTable

CSS_PATH = ["report_specs.tcss"]

class ReportSpecDetails(ModalScreen):
    """Screen to display report specification details."""

    message = reactive("Loop is stopped")
    _interval_task = None  # To store the interval task handle

    class ReportDetailsContinue(Message):
        """Message to reeturn to the previous screen."""
        pass

    class ReportDetailsQuit(Message):
        """Message to terminate application gracefully."""
        def __init__(self, return_code:Optional[int]=200):
            super().__init__()
            self.return_code = return_code

    class ReportDetailsBack(Message):
        """Message to return to the previous screen."""
        pass

    def __init__(self, response,**kwargs):
        super().__init__(**kwargs)
        # response = details from pyegeria call
        self.response = response
        """create  a DataTable of key/value pairs"""
        self.spec_datatable: DataTable = DataTable()
        self.log(f"self.spec_datatable : {self.spec_datatable} has been created")
        self.spec_datatable.id = "spec_data_table"
        self.log(f"self.spec_datatable has been assigned an id : {self.spec_datatable.id} ")
        self.spec_datatable.add_columns("Key", "Value", "Description")
        self.log(f"self.spec_datatable has been assigned columns {self.spec_datatable.columns}")
        self.spec_datatable.border = True
        self.spec_datatable.zebra_stripes = True
        self.log(f"DataTable created and configured {self.spec_datatable}, id: {self.spec_datatable.id}")
        # instantiate connection data for screen
        self.Egeria_config = ["https://127.0.0.1:9443", "qs-view-server", "erinoverview", "secret"]
        self.platform_url = self.Egeria_config[0]
        self.view_server = self.Egeria_config[1]
        self.user = self.Egeria_config[2]
        self.password = self.Egeria_config[3]

    def compose(self) -> ComposeResult:
        # Process response data into the DataTable and mount it on the screen
        # self.display_response( self.response)
        # Now build the screen content
        self.heading = "Report Spec Details"
        self.subheading = "Details from executing selected report spec."
        yield Header(show_clock=True)
        yield Static(f"{self.subheading}")
        yield Static(
            f"Server: {self.view_server} | Platform: {self.platform_url} | User: {self.user}",
            id="detail_connection_info",
        )
        yield Container(
            Static(f"Start of Report Specification List:", id="report_start"),
            self.spec_datatable,
            Static(f"End of Report Specification List:", id="report_end"),
            id="report_details")
        yield Horizontal(
            Button("Quit", id="quit"),
            Button("Back", id="back"),
            Button("continue", id="continue"),
            id="action_row"
        )
        yield Footer()

    def on_mount(self) -> None:
        """ On mount process the data and load the datatable"""
        # populate table data
        self.display_response()

    def display_response(self):
        """process reesponse data into a DataTable for display"""
        response_data: list[dict] = self.response.get("data")
        self.log(f"response_data: {response_data}")
        self.log(f"Find address of DataTable")
        # self.spec_datatable = self.query_one("#spec_data_table", DataTable)

        if not response_data or response_data == None or response_data == "":
            response_data = [{"NoData": "No data found for selected item"}]
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
                                self.spec_datatable.add_row(vkey, vvalue)
                                continue
                        elif isinstance(value, list):
                            for v in value:
                                self.log(f"v: {v}")
                                self.spec_datatable.add_row(key, v)
                                continue
                        elif key == "kind" and value == "empty":
                            key_str = "No Data"
                            value_str = "For That Asset Type in this repository"
                            self.log(f"key_str: {key_str}, value_str: {value_str}")
                            self.spec_datatable.add_row(key_str, value_str)
                            continue
                        else:
                            self.log(f"else: key {key} value: {value}")
                            self.spec_datatable.add_row(key, value)
                            continue
        if isinstance(response_data, dict):
            for key, value in response_data.items():
                self.log(f"key: {key}, value: {value}")
                if isinstance(value, dict):
                    for vkey, vvalue in value.items():
                        self.spec_datatable.add_row(vkey, vvalue)
                        continue
                elif isinstance(value, list):
                    for v in value:
                        self.spec_datatable.add_row(key, v)
                        continue
                elif key == "kind" and value == "empty":
                    key_str = "No Data"
                    value_str = "For That Asset Type in this repository"
                    self.spec_datatable.add_row(key_str, value_str)
                    continue
                else:
                    self.spec_datatable.add_row(key, value)
                    continue
        self.log(f"Start Refresh DataTable task")
        if self._interval_task is None:
            # Set an interval to call update_message every 1 second
            self._interval_task = self.set_interval(5, self.update_message)
            self.notify("Loop started!")
        else:
            self.notify("Loop is already running.")

        # self.spec_datatable.refresh()
        return

    def update_message(self) -> None:
        """A function to be called repeatedly by the interval."""
        now = datetime.now()
        current_time_str = now.strftime("%H:%M:%S")
        self.message = f"Loop is running! Current time: {current_time_str}"
        self.spec_datatable.refresh()

    def action_stop_loop(self) -> None:
        if self._interval_task is not None:
            # Cancel the interval task
            self._interval_task.stop()
            self._interval_task = None
            self.message = "Loop is stopped."
            self.notify("Loop stopped!")
        else:
            self.notify("Loop is already stopped.")

    @on(Button.Pressed, "#continue")
    def handle_continue(self, event: Button.Pressed) -> None:
        """ handler for continue button"""
        self.action_stop_loop()
        self.post_message(self.ReportDetailsContinue())

    @on(Button.Pressed, "#quit")
    def handle_quit(self, event: Button.Pressed) -> None:
        """ handler for quit button"""
        self.action_stop_loop()
        self.post_message(self.ReportDetailsQuit())

    @on(Button.Pressed, "#back")
    def handle_back(self, event: Button.Pressed) -> None:
        """ handler for back button"""
        self.action_stop_loop()
        self.post_message(self.ReportDetailsBack())