"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

A form exemplar for Egeria users to enter data into templates using Textual open source framework

Peter Coldicott
"""

import os
from os import system
import click
from textual.reactive import Reactive

from textual.app import App, ComposeResult
from textual.containers import (
    Container,
    Vertical,
    HorizontalScroll,
    VerticalScroll,
    ScrollableContainer,
)
from textual import on, work
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Input,
    Static,
    Button,
    RichLog,
    Label,
    Tree,
    Footer,
    DataTable,
    Header,
)

from typing import Any


EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("EGERIA_VIEW_SERVER", "view-server")
EGERIA_VIEW_SERVER_URL = os.environ.get(
    "EGERIA_VIEW_SERVER_URL", "https://localhost:9443"
)
EGERIA_INTEGRATION_DAEMON = os.environ.get("INTEGRATION_DAEMON", "integration-daemon")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_JUPYTER = bool(os.environ.get("EGERIA_JUPYTER", "False"))

disable_ssl_warnings = True

TITLE = "User Access"


class UserInfo(Screen):
    """A screen to request user access info - required
    If no information is supplied the access defaults to a set of
    demo/test values:
    User: erinoverview
    Password: Secret
    Platform URL: https://localhost:9443
    View Server Name: view-server"""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def __init__(self) -> None:
        """Initialize the UserInfo Screen variables"""
        self.app.dark = True
        self.user = ""
        self.password = ""
        self.platformu = ""
        self.view_server = ""
        self.tech_type = ""
        super().__init__()

    def compose(self) -> ComposeResult:
        self.log("In UserInfo - Compose ")
        with VerticalScroll(id="user-container"):
            yield Label("Username: ", classes="uprompt")
            yield Input("", id="username", classes="uinput")
        with VerticalScroll(id="pwd-container"):
            yield Label("Password: ", classes="uprompt")
            yield Input("", id="password", classes="uinput")
        with VerticalScroll(id="platform-container"):
            yield Label("Platform URL: ", classes="uprompt")
            yield Input("", id="platform_url", classes="uinput")
        with VerticalScroll(id="view-server-container"):
            yield Label("View Server Name: ", classes="uprompt")
            yield Input("", id="view_server", classes="uinput")
        with HorizontalScroll(id="button-container"):
            yield Button("Cancel", "warning", id="cancel")
            yield Button("Submit", "primary", id="submit")
        yield RichLog()
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""

        self.app.dark = not self.app.dark

    def on_input_changed(self, event: Input.Changed) -> None:
        """Detect input changed events and capture input value"""

        try:
            ivalue = str(event.value)
        except ValueError:
            return
        else:
            if event.input.id == "username":
                self.user = ivalue
            elif event.input.id == "password":
                self.password = ivalue
            elif event.input.id == "platform_url":
                self.platformu = ivalue
            elif event.input.id == "view_server":
                self.view_server = ivalue
        return

    @on(Button.Pressed, "#submit")
    async def on_submit(self) -> []:
        """This processes the user input."""

        global EGERIA_USER
        global EGERIA_USER_PASSWORD
        global EGERIA_PLATFORM_URL
        global EGERIA_VIEW_SERVER

        result = [" meow", "woof", "neigh", "hoot"]

        if self.user:
            result[0] = self.user
        else:
            result[0] = "erinoverview"
        if self.password:
            result[1] = self.password
        else:
            result[1] = "secret"
        if self.platformu:
            result[2] = self.platformu
        else:
            result[2] = "https://localhost:9443"
        if self.view_server:
            result[3] = self.view_server
        else:
            result[3] = "view-server"

        # Also store the input in global variables

        EGERIA_USER = result[0]
        EGERIA_USER_PASSWORD = result[1]
        EGERIA_PLATFORM_URL = result[2]
        EGERIA_VIEW_SERVER = result[3]

        await self.action_dismiss(result)

    @on(Button.Pressed, "#cancel")
    def on_cancel(self) -> None:
        self.action_dismiss()


class ExitScreen(ModalScreen):
    """App exit screen."""

    DEFAULT_CSS = """
    ExitScreen {
        align: center middle;
    }

    ExitScreen > Container {
        width: auto;
        height: auto;
    }
    """

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def __init__(self) -> None:
        """Initialize the UserInfo Screen variables"""
        super().__init__()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.app.dark = not self.app.dark

    def compose(self) -> ComposeResult:
        with Container():
            yield Label("Are you sure you want to quit?")
            yield Button("No", id="no", variant="error")
            yield Button("Yes", id="yes", variant="success")
            yield Footer()
            yield RichLog()

    @on(Button.Pressed, "#no")
    def on_no(self) -> None:
        """No the user pressed the exit button in error"""
        self.action_dismiss()

    @on(Button.Pressed, "#yes")
    def on_yes(self) -> None:
        """Yes the user wants to quit the app"""
        self.app.exit()


class Egeria_login(App):
    """main app class"""

    CSS_PATH = "txt_custom_v2.tcss"

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        dark = Reactive(True, compute=False)
        self.app.dark = False
        self.template: Any = None

    def compose(self) -> ComposeResult:
        """Compose the main display"""

        yield Label(f"User: {EGERIA_USER}, password: {EGERIA_USER_PASSWORD}")
        yield Label(
            f"Platform: {EGERIA_PLATFORM_URL}, View Server: {EGERIA_VIEW_SERVER}"
        )
        yield Button("Finish", "success", id="finish")
        yield RichLog()
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> (str, str, str, str):
        """Yes the user wants to quit the app"""

        self.exit(
            (
                EGERIA_USER,
                EGERIA_USER_PASSWORD,
                EGERIA_PLATFORM_URL,
                EGERIA_VIEW_SERVER,
            ),
            200,
            "Finished",
        )

    def action_toggle_dark(self) -> None:
        """An action to toggle dark and light mode."""
        self.app.dark = not self.app.dark

    async def on_mount(self) -> None:
        """Main Program flow control start routine
        Pushes the user info popup with an associated call back routine"""

        global EGERIA_USER
        global EGERIA_USER_PASSWORD
        global EGERIA_PLATFORM_URL
        global EGERIA_VIEW_SERVER

        system("clear")
        # Display User Info Screen
        self.install_screen(UserInfo(), name="userinfo")
        await self.push_screen(UserInfo(), self.input_userinfo_callback)

    async def input_userinfo_callback(self, user_input) -> (str, str, str, str):
        """Prompt for user id and password, callback routine
        This routine is invoked when user input is completed
        """

        global EGERIA_USER
        global EGERIA_USER_PASSWORD
        global EGERIA_PLATFORM_URL
        global EGERIA_VIEW_SERVER
        global TECH_NAME

        if user_input[0] != None:
            EGERIA_USER = user_input[0]
        else:
            EGERIA_USER = "erinoverview"
        if user_input[1] != None:
            EGERIA_USER_PASSWORD = user_input[1]
        else:
            EGERIA_USER_PASSWORD = "secret"
        if user_input[2] != None:
            EGERIA_PLATFORM_URL = user_input[2]
        else:
            EGERIA_PLATFORM_URL = "https://localhost:9443"
        if user_input[3] != None:
            EGERIA_VIEW_SERVER = user_input[3]
        else:
            EGERIA_VIEW_SERVER = "view-server"

        return (
            EGERIA_USER,
            EGERIA_USER_PASSWORD,
            EGERIA_PLATFORM_URL,
            EGERIA_VIEW_SERVER,
        )


# @click.command("egeria-login")
# @click.option("--server", default=EGERIA_VIEW_SERVER, help="Egeria view server to use.")
# @click.option(
#     "--url", default=EGERIA_VIEW_SERVER_URL, help="URL of Egeria platform to connect to"
# )
# @click.option("--userid", default=EGERIA_USER, help="Egeria user")
# @click.option("--password", default=EGERIA_USER_PASSWORD, help="Egeria user password")
def login(userid: str, password: str, server: str, url: str) -> None:
    app = Egeria_login()
    app.run()
    return "peterprofile"


if __name__ == "__main__":
    app = Egeria_login()
    app.run()
