# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Screen related functions of my_egeria module.


"""

import os
from textual.containers import Container, Vertical
from textual.message import Message
from textual.widgets import Static, Input, Button
from .base_screen import BaseScreen
from ..con_services.egeria_connection import connect_to_egeria


class LoginScreen(BaseScreen):
    """User log in screen, automatically displayed following the package splash screen."""

    CSS_PATH = ["../styles/common.css", "../styles/login_screen.css"]

    class LoginSuccess(Message):
        def __init__(self, login_payload: list):
            self.payload = login_payload
            super().__init__()

    def __init__(self):
        super().__init__()
        self.login_payload: list = []

    def compose(self):
        yield from super().compose()
        # Top-half container holds a bordered box with the form, centered horizontally
        yield Container(
            Container(
                Vertical(
                    Static("Login to Egeria", id="login_title"),
                    Static("Username"),
                    Input(placeholder="erinoverview", id="username"),
                    Static("Password"),
                    Input(placeholder="secret", password=True, id="password"),
                    Static("Platform URL (optional)"),
                    Input(placeholder="https://localhost:9443", id="platform-url"),
                    Static("View Server (optional)"),
                    Input(placeholder="qs-view-server", id="view-server"),
                    Button(label="Login", id="login_button"),
                    Static("", id="login_status"),
                    id="login_form",
                ),
                id="login_box",
            ),
            id="login_top",
        )

    async def on_mount(self):
        # await super().on_mount()

        # Position the top-level container in the upper portion; give a bit more vertical room
        top = self.query_one("#login_top", Container)
        top.styles.dock = "top"
        top.styles.height = "60%"               # was 50%; increase so the button doesn't get clipped
        top.styles.width = "100%"
        top.styles.padding = (1, 2)
        top.styles.align_horizontal = "center"  # center child (login_box) horizontally
        top.styles.align_vertical = "top"       # keep at top within the section

        # Bordered box that contains the vertical form
        box = self.query_one("#login_box", Container)
        box.styles.width = "60%"
        box.styles.border = ("solid", "white")
        box.styles.padding = (1, 2)
        box.styles.align_horizontal = "center"
        box.styles.align_vertical = "top"
        # Ensure the box is tall enough to show the button
        box.styles.min_height = 14              # numeric rows to guarantee interior content fits

        form = self.query_one("#login_form", Vertical)
        form.styles.gap = 1
        form.styles.width = "100%"

        # Title styling
        title = self.query_one("#login_title", Static)
        title.styles.text_align = "center"
        title.styles.text_style = "bold"
        title.styles.margin = (0, 0, 1, 0)

        # Inputs: make them a reasonable width and centered by the parent
        for iid in ("#username", "#password", "#platform-url", "#view-server"):
            inp = self.query_one(iid, Input)
            inp.styles.width = "80%"

        # Login button: small top margin (numeric)
        btn = self.query_one("#login_button", Button)
        btn.styles.margin = (1, 0, 0, 0)

        # Defaults into the inputs
        self.query_one("#username", Input).value = os.getenv("EGERIA_USER", "erinoverview")
        self.query_one("#password", Input).value = os.getenv("EGERIA_USER_PASSWORD", "secret")
        self.query_one("#platform-url", Input).value = os.getenv("EGERIA_PLATFORM_URL", "https://localhost:9443")
        self.query_one("#view-server", Input).value = os.getenv("EGERIA_VIEW_SERVER", "qs-view-server")

        # Focus username for convenience
        self.query_one("#username", Input).focus()

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id != "login_button":
            return

        username = self.query_one("#username", Input).value.strip()
        password = self.query_one("#password", Input).value.strip()
        platform_url = self.query_one("#platform-url", Input).value.strip()
        view_server = self.query_one("#view-server", Input).value.strip()

        # Fill defaults correctly
        if not username:
            username = "erinoverview"
        if not password:
            password = "secret"
        if not platform_url:
            platform_url = "https://localhost:9443"
        if not view_server:
            view_server = "qs-view-server"

        status = self.query_one("#login_status", Static)
        btn = self.query_one("#login_button", Button)

        self.login_payload: list = [username,
                               password,
                               platform_url,
                               view_server
                               ]
        self.log(f"Payload created: {self.login_payload}")
        # Disable button and show status while working
        btn.disabled = True
        # status.update("Connecting...")
        ok = False
        try:
            # Run blocking work off the UI thread, with a timeout for safety
            ok = connect_to_egeria(username, password, platform_url, view_server)
        except Exception as e:
            ok = False
            status.update(f"Error: {e}")
        finally:
            btn.disabled = False

        if ok:
            status.update("Connected.")
            self.post_message(LoginScreen.LoginSuccess(self.login_payload))
        else:
            if not status.render:
                status.update("Login failed.")
