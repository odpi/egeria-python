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
from textual.widgets import Header, Footer, Button, Label, Static

from pyegeria import load_app_config, settings
from ChangeUserScreen import ChangeUserScreen
from profile_utils import set_screen_heading


class SplashScreen(ModalScreen):
    """ SplashScreen for my_egeria """

    # Escape must dismiss (not pop) the screen, so that MyProfileApp.mainline still runs
    BINDINGS = [("escape", "continue_to_app", "Continue")]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.user_name = app_user.user_name
        self.user_password = app_user.user_pwd
        self.view_server = app_config.egeria_view_server
        self.platform_url = app_config.egeria_platform_url

    def on_mount(self) -> None:
        set_screen_heading(self, "Welcome to my_egeria")

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
        self.app.push_screen(ChangeUserScreen(), callback=self.change_user_callback)

    def change_user_callback(self, result: Any) -> None:
        """Pass validated [user, password] on to MyProfileApp.mainline; on cancel stay on the splash."""
        if isinstance(result, list):
            self.dismiss(result)

