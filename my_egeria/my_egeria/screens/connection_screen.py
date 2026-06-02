# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Screen related functions of my_egeria module.


"""

from textual.widgets import Static, DataTable, Button
from textual.app import ComposeResult
from textual import on
# from pyegeria.repository_services import RepositoryServices
import os
from .base_screen import BaseScreen


class ConnectionScreen(BaseScreen):
    """Screen to display connection details from Egeria."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.table = DataTable()
        # self.repo_svc = RepositoryServices(
        server_name=os.getenv("EGERIA_SERVER", "myserver"),
        platform_url=os.getenv("EGERIA_PLATFORM_URL", "http://localhost:8080"),
        # )

    def compose(self) -> ComposeResult:
        yield from super().compose()
        yield Static("[b]Egeria Connections[/b]", id="connection_title")
        self.table.add_columns("Connection Name", "GUID")
        yield self.table
        yield Button("Refresh", id="refresh_btn")

    def on_mount(self) -> None:
        self.load_connections()

    def load_connections(self) -> None:
        """Fetch and display active connections."""
        self.table.clear()
        try:
            results = self.repo_svc.find_connections() or []
            if not results:
                self.table.add_row("No connections found", "")
                return

            for conn in results:
                name = conn.get("displayName", "Unknown")
                guid = conn.get("guid", "?")
                self.table.add_row(name, guid)
        except Exception as e:
            self.table.add_row("Error", str(e))

    @on(Button.Pressed, "#refresh_btn")
    def on_refresh(self, event: Button.Pressed) -> None:
        self.load_connections()
