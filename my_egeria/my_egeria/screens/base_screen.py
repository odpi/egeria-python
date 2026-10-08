# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Screen related functions of my_egeria module.


"""

from textual.screen import Screen
from textual.widgets import Header, Footer, Static
from textual.app import ComposeResult
from textual import on
from textual.containers import Container
from my_egeria.utils.config import get_global_config
from my_egeria.utils.egeria_client import EgeriaTechClientManager
from my_egeria.con_services.egeria_connection import EgeriaConnectionService

class BaseScreen(Screen):
    CSS_PATH = ["../styles/common.css", "../styles/base_screen.css"]
    """Base class for all screens with consistent header, footer, and keybindings."""

    BINDINGS = [
        ("r", "refresh_data", "Refresh"),
        ("escape", "pop_screen", "Back"),
        ("q", "quit_app", "Quit"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use centralized config (set at login)
        self.cfg = get_global_config()
        self.manager = EgeriaTechClientManager(self.cfg)
        self._is_connected = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static(
                f"Server: {self.cfg.view_server} | Platform: {self.cfg.platform_url} | User: {self.cfg.user}",
                id="connection_info",
            )
        )
        yield Footer()

    async def on_mount(self) -> None:
        # Use a fast connectivity check; don't build the heavy client on mount
        try:
            ecs = EgeriaConnectionService()
            if not ecs.is_connected():
                # Optionally: display a non-blocking warning or status
                pass
        except Exception:
            # Optionally: display a non-blocking warning or status
            pass

    def check_connection(self) -> None:
        # If you still need this elsewhere, prefer the service verify instead of building a client
        ecs = EgeriaConnectionService()
        ecs.verify_connection()

    def show_error_and_exit(self, error_message: str) -> None:
        """Show popup with error and quit app."""
        from textual.widgets import Button
        from textual.containers import Vertical

        popup = Vertical(
            Static(f"[b]Egeria Connection Error[/b]\n\n{error_message}"),
            Button("OK", id="ok_button"),
        )
        self.mount(popup)
        self.set_focus(popup.query_one(Button))

        @on(Button.Pressed, "#ok_button")
        def _exit_app(_):
            self.app.exit()

    def action_refresh_data(self) -> None:
        """Refresh data for the screen."""
        self.refresh()

    def action_quit_app(self) -> None:
        """Quit the application."""
        self.app.exit()

    def action_pop_screen(self) -> None:
        """Pop this screen (Back)."""
        self.app.pop_screen()

