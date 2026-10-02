"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a splash scrren and optional change of logged in user for my_egeria.

"""

from typing import Any
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Header, Footer, Button, Label, Input, Static

from pyegeria import Egeria, load_app_config, settings, PyegeriaException


class SplashScreen(ModalScreen):
    """ SplashScreen for my_profile_app """

    # Escape must dismiss (not pop) the screen, so that MyProfileApp.mainline still runs
    BINDINGS = [("escape", "continue_to_app", "Continue")]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.title = "Egeria"
        self.subtitle = "Welcome to my_profile_app"
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.user_name = app_user.user_name
        self.user_password = app_user.user_pwd
        self.view_server = app_config.egeria_view_server
        self.platform_url = app_config.egeria_platform_url

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True,id="splash")
        # 1. Define multi-line layout with line breaks
        splash_content = (
            f"Welcome to My_Profile for Egeria Users, {self.user_name}!\n"
            "----------------------------------------\n"
            "Initializing secure packages...\n\n"
            "© PDX-License-Identifier: Apache-2.0\n"    
            "Copyright Contributors to the ODPi Egeria project.\n\n"
            "This file provides a set of profile related functions for my_egeria."
            )

        # 2. Build the UI components
        yield Static(classes="empty")
        with Vertical(id="splash-card"):
            yield Label(splash_content, id="splash-text")
        # yield Static(classes="empty")
        # yield Static(classes="empty")
            yield Horizontal(
                Button("Continue to App", id="continue", variant="success", classes="splash_buttons"),
                Button("Change User", variant="warning", id="change_user", classes="splash_buttons"),
                id="SplashButtons"
            )
        # yield Static(classes="empty")
        yield Footer()

    def action_continue_to_app(self):
        self.dismiss()

    @on(Button.Pressed, "#continue")
    def handle_continue(self):
        self.dismiss()

    @on(Button.Pressed, "#change_user")
    def handle_change_user(self):
        self.query_one("#splash-card").remove_children()
        self.query_one("#change_user").remove()
        self.query_one("#splash-card").mount(
            Input(placeholder="Enter new user name", id="new_user_name"),
            Input(placeholder="Enter password for new user", id="new_user_password", password=True),
            Button("Submit", id="submit_new_user", variant="success")
        )

    @on(Button.Pressed, "#submit_new_user")
    def handle_submit_new_user(self):
        self.new_user = self.query_one("#new_user_name", Input).value
        self.new_password = self.query_one("#new_user_password", Input).value
        if not self.new_user or not self.new_password:
            self.notify("Please enter both user name and password", severity="error", timeout=20)
            return
        # Validate new user credentials
        eclient = None
        try:
            eclient = Egeria(
                self.view_server,
                self.platform_url,
                self.new_user,
                self.new_password,
            )
        except PyegeriaException as e:
            self.notify(f"User credential validation failed: {e}", timeout=30, severity="error")
            return
        finally:
            if eclient:
                eclient.close_session()
        self.dismiss([self.new_user, self.new_password])

