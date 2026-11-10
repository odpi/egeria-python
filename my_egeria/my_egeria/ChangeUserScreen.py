"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a screen to change the Egeria user that my_egeria is logged in as.

"""

from typing import Any
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Header, Footer, Button, Label, Input

from pyegeria import load_app_config, settings
from profile_utils import check_egeria_access, set_screen_heading


class ChangeUserScreen(ModalScreen):
    """Collect a new user id and password, and check Egeria accepts them.

    Dismisses with [user_name, password] once Egeria has accepted the credentials,
    or 200 if the user cancels.
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        load_app_config()
        self.user_name = settings.User_Profile.user_name
        self.view_server = settings.Environment.egeria_view_server
        self.platform_url = settings.Environment.egeria_platform_url

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="change_user_card"):
            yield Label(f"Currently logged in as: {self.user_name}\n"
                        f"Enter the user id and password to switch to.", id="change_user_text")
            yield Input(placeholder="Enter new user name", id="new_user_name")
            yield Input(placeholder="Enter password for new user", id="new_user_password", password=True)
            yield Horizontal(
                Button("Submit", id="submit_new_user", variant="success"),
                Button("Cancel", id="cancel_change_user", variant="warning"),
                id="change_user_buttons",
            )
        yield Footer()

    def on_mount(self) -> None:
        set_screen_heading(self, "Change User")
        self.query_one("#new_user_name", Input).focus()

    def action_cancel(self) -> None:
        self.dismiss(200)

    @on(Button.Pressed, "#cancel_change_user")
    def handle_cancel(self) -> None:
        self.dismiss(200)

    @on(Input.Submitted, "#new_user_name")
    def handle_user_name_submitted(self) -> None:
        self.query_one("#new_user_password", Input).focus()

    @on(Input.Submitted, "#new_user_password")
    @on(Button.Pressed, "#submit_new_user")
    def handle_submit_new_user(self) -> None:
        new_user = self.query_one("#new_user_name", Input).value.strip()
        new_password = self.query_one("#new_user_password", Input).value
        if not new_user or not new_password:
            self.notify("Please enter both user name and password", severity="error", timeout=20)
            return
        error = check_egeria_access(self.view_server, self.platform_url, new_user, new_password)
        if error:
            self.notify(f"User credential validation failed: {error}", severity="error", timeout=30)
            return
        self.dismiss([new_user, new_password])
