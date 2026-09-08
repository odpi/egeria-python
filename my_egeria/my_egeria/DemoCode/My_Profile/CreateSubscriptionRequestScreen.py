"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a Screen Layout and support functions for supporting a user
   creating a subscription to a digital data asset.

"""
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Header, Static, Input, Footer


class CreateSubscriptionRequestScreen(ModalScreen):

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "create_subscription", "Create Subscription")
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, selected_item: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_item = selected_item
        self.display_name = ""
        self.description = ""
        self.status = "DRAFT"
        self.identifier = ""
        self.response = {}
        self.valid_status = ["DRAFT",
                             "PROPOSED",
                             "ACTIVE",
                             "SUSPENDED",
                             "CANCELLED",
                             "EXPIRED",
                             "PREPARED",
                             "APPROVED",
                             "DISABLED",
                             "DEPRECATED",
                             "OTHER"]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield ScrollableContainer(
            Static(f"Please provide the following input as appropriate:"),
            Static("Display Name should be short but descriptive, it will also be used to create the Qualified Name as well"),
            Input("Display Name for the subscription", id = "sub_display_name"),
            Static(f"Description of this Subscription"),
            Input(placeholder="Please enter a description", id="sub_description"),
            Static(f"A short identifier for the subscription, e..g. MySub1"),
            Input(placeholder="Please enter an identifier", id="sub_ID"),
            Static("By default the user defined status for this subscription will be set to DRAFT, you can override"),
            Input("User defined Status - optional", id = "sub_status"),
            Static("When all input is completed please click the 'Create Subscription' (c) key"),
            id = "subscription_input_container")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Create Subscription Request"
        self.subtitle = "Enter details for the subscription request"

    def action_quit(self):
        self.log("Quitting Create Subscription Request screen")
        self.dismiss(200)

    @on(Input.Changed, "#sub_display_name")
    def handle_subscription_name_change(self, event):
        self.display_name = event.value

    @on(Input.Changed, "#sub_status")
    def handle_subscription_status_change(self, event):
        self.status = event.value
        if self.status not in self.valid_status:
            self.status = "DRAFT"

    @on(Input.Changed, "#sub_description")
    def handle_description_change(self, event):
        self.description = event.value or ""

    @on(Input.Changed, "#sub_ID")
    def handle_subscription_id_change(self, event):
        self.identifier = event.value

    def action_create_subscription(self):
        self.log("Creating subscription request")
        self.response: dict = {}
        if self.selected_item:
            self.response["externalSourceGUID"] = self.selected_item
            self.response["guid"] = self.selected_item
        if self.display_name:
            self.response["displayName"] = self.display_name
        if self.status:
            self.response["Status"] = self.status
        if self.description:
            self.response["description"] = self.description
        if self.identifier:
            self.response["identifier"] = self.identifier
        self.dismiss(self.response)
        return self.response