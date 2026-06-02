"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""
import os

from pydantic import ValidationError
from textual import on
from textual.app import ComposeResult, App
from textual.containers import Container, Horizontal
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Header, Static, Button, Footer

CSS_PATH = ["tech_type.tcss"]

class TechTypeDetails(ModalScreen):

    def __init__(self, response, **kwargs):
        super().__init__()
        # response = details from calls to pyegeria
        self.response = response
        # instantiate connection data for screen
        self.Egeria_config = ["https://127.0.0.1:9443", "qs-view-server", "erinoverview", "secret"]
        self.platform_url = self.Egeria_config[0]
        self.view_server = self.Egeria_config[1]
        self.user = self.Egeria_config[2]
        self.password = self.Egeria_config[3]

    class TechTypeContinue(Message):
        """ Message to indicate user is ready to continue to application"""
        def __init__(self):
            super().__init__()
            pass

    class TechTypeBack(Message):
        """ Message to terminate application gracefully """
        def __init__(self):
            super().__init__()


    class TechTypeQuit(Message):
        """ Message to terminate application gracefully """
        def __init__(self):
            super().__init__()
            pass

def comnpose(self) -> ComposeResult:
    """ Compose the screen """
    self.heading = "Technology Type Details"
    self.subheading = "Details from querying selected technology type."
    yield Header(show_clock=True)
    yield Static(f"{self.subheading}")
    yield Static(
        f"Server: {self.view_server} | Platform: {self.platform_url} | User: {self.user}",
        id="detail_connection_info",
    )
    yield Container(
        Static(f"Start of Technology Type Details:", id="report_start"),
        # self.tech_type_datatable,
        Static(f"End of Technology Type Details:", id="report_end"),
        id="report_details")
    yield Horizontal(
        Button("Quit", id="quit"),
        Button("Back", id="back"),
        Button("continue", id="continue"),
        id="action_row"
    )
    yield Footer()