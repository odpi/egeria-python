""""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a screen for a user to show cooments attached to a community for my_egeria.

"""
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Header, Static, Footer, Input, Button, DataTable

from pyegeria import load_app_config, settings


class AddCommentScreen(ModalScreen):
    """ Add a comment to an Egeria Element the user has access to """

    BINDINGS = [
        ("a", "add_comment", "Add Comment"),
        ("c", "cancel", "Cancel"),
        ("q", "quit", "Quit")
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, table_name, element_guid, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table_name = table_name
        self.element_guid = element_guid or None
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = (app_config.egeria_platform_url or "https://127.0.0.1:9443")
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.comment = ""
        self.comment_type = ""

    def on_mount(self):
        self.title = "Egeria - My Profile"
        self.subtitle = "Add a comment to an element in Egeria"
        if self.element_guid == None:
            self.notify(f"A row must be selected from a table on the main screen before adding a comment")
            self.dismiss(400)

    def compose(self) -> ComposeResult:
        """This method composes the UI for the AddCommentScreen."""
        yield Header(show_clock=True)
        yield Static(classes="empty")
        yield ScrollableContainer(
            Static(f"[b]Add Comment[/b] to {self.element_guid}"),
            Input(placeholder="Enter comment", id="add_comment_input"),
            Static(f"Valid comment types are: Question, Answer, Suggestion and Requirement"),
            Input(placeholder="Comment Type: Question, Suggestion, etc.", id="add_comment_type_input"),
            Static("Use Cancel to return to the previous screen"),
            Button("Submit", id="add_comment_button", variant="primary"),
            id="add_comment_container"
            )
        yield Footer()

    def action_quit(self):
        self.dismiss(200)

    def action_cancel(self):
        self.dismiss(200)

    @on(Button.Pressed, "#add_comment_button")
    def handle_button_pressed(self):
        self.action_add_comment()

    def action_add_comment(self):
        if self.comment and self.comment_type:
            self.comment_data = [self.comment, self.comment_type, self.element_guid]
            self.log(f"Comment data: {self.comment_data} being returned from screen")
            self.dismiss(self.comment_data)
        else:
            self.notify("Please enter both a comment and comment type, before submitting")

    def on_input_changed(self, event: Input.Changed):
        self.log(f"Input detected: {event.input.id}, {event.input.value}")
        if  event.input.id == "add_comment_input":
                self.comment = event.value
        elif event.input.id == "add_comment_type_input":
                self.comment_type = event.value

