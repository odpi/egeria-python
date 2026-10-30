"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides the screen my_egeria shows while it cannot reach Egeria.

"""

from typing import Any
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Header, Footer, Button, Label, Static

from pyegeria import load_app_config, settings
from profile_utils import check_egeria_access

# Seconds between automatic reconnection attempts
RETRY_INTERVAL = 10


class ConnectionErrorScreen(ModalScreen):
    """Explain that Egeria could not be reached, and wait for it to come up.

    The screen retries every RETRY_INTERVAL seconds (or when Retry Now is pressed),
    and dismisses with 200 as soon as Egeria accepts the current user's credentials.
    It dismisses with 201 if the user wants to change user, or 402 if they quit.
    """

    BINDINGS = [
        ("r", "retry_now", "Retry Now"),
        ("u", "change_user", "Change User"),
        ("q", "quit_app", "Quit"),
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, error_message: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.title = "Egeria"
        self.sub_title = "Unable to connect to Egeria"
        self.error_message = error_message
        self.attempts = 0
        self.countdown = RETRY_INTERVAL
        load_app_config()
        self.user_name = settings.User_Profile.user_name
        self.user_password = settings.User_Profile.user_pwd
        self.view_server = settings.Environment.egeria_view_server
        self.platform_url = settings.Environment.egeria_platform_url

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="connection_error_card"):
            yield Label(
                "my_egeria could not connect to Egeria.\n\n"
                f"Platform URL: {self.platform_url}\n"
                f"View Server:  {self.view_server}\n"
                f"User:         {self.user_name}\n\n"
                "Please start your Egeria instance; my_egeria will keep retrying "
                "and carry on as soon as it is available.",
                id="connection_error_text",
            )
            yield Static(self.error_message, id="connection_error_reason")
            yield Static(self._status_text(), id="connection_retry_status")
            yield Horizontal(
                Button("Retry Now", id="retry_now", variant="success"),
                Button("Change User", id="change_user", variant="warning"),
                Button("Quit", id="quit_app", variant="error"),
                id="connection_error_buttons",
            )
        yield Footer()

    def on_mount(self) -> None:
        self.retry_timer = self.set_interval(1, self._tick)

    def _status_text(self) -> str:
        attempts = f"Attempts so far: {self.attempts}.  " if self.attempts else ""
        return f"{attempts}Retrying in {self.countdown} seconds..."

    def _tick(self) -> None:
        self.countdown -= 1
        if self.countdown <= 0:
            self.retry_connection()
        else:
            self.query_one("#connection_retry_status", Static).update(self._status_text())

    def retry_connection(self) -> None:
        """Try Egeria again; leave this screen if it now accepts the credentials."""
        self.attempts += 1
        self.query_one("#connection_retry_status", Static).update("Trying to connect to Egeria...")
        error = check_egeria_access(self.view_server, self.platform_url, self.user_name, self.user_password)
        # self.log(f"Connection attempt {self.attempts}: {error or 'connected'}")
        if error is None:
            self.retry_timer.stop()
            self.dismiss(200)
            return
        self.error_message = error
        self.query_one("#connection_error_reason", Static).update(error)
        self.countdown = RETRY_INTERVAL
        self.query_one("#connection_retry_status", Static).update(self._status_text())

    def action_retry_now(self) -> None:
        self.retry_connection()

    def action_change_user(self) -> None:
        self.retry_timer.stop()
        self.dismiss(201)

    def action_quit_app(self) -> None:
        self.retry_timer.stop()
        self.dismiss(402)

    @on(Button.Pressed, "#retry_now")
    def handle_retry_now(self) -> None:
        self.action_retry_now()

    @on(Button.Pressed, "#change_user")
    def handle_change_user(self) -> None:
        self.action_change_user()

    @on(Button.Pressed, "#quit_app")
    def handle_quit(self) -> None:
        self.action_quit_app()
