# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Collections related functions of my_egeria module.


"""


# screens/collection_members_screen.py
from textual.widgets import Static, DataTable, Button
from textual.app import ComposeResult
from textual import on

from my_egeria.services.collection_service import CollectionService
# from utils.egeria_client import EgeriaTechClientManager
# import os
from ..base_screen import BaseScreen


class CollectionMemberScreen(BaseScreen):
    """Screen to display glossary terms from Egeria."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.table = DataTable()

    def compose(self) -> ComposeResult:
        yield from super().compose()
        yield Static("[b]Egeria Collection Member[/b]", id="glossary_title")
        self.table.add_columns("Member Name", "Description")
        yield self.table
        yield Button("Refresh", id="refresh_btn")

    def on_mount(self) -> None:
        self.load_members()

    def load_members(self) -> None:
        """Fetch and display collection members."""
        self.table.clear()
        try:
            self.asset_mgr = CollectionService(
                # view_server=os.getenv("EGERIA_SERVER", "myserver"),
                # platform_url=os.getenv("EGERIA_PLATFORM_URL", "http://localhost:8080"),
                # user_id=os.getenv("EGERIA_USER", "admin"),
                # user_pwd=os.getenv("EGERIA_USER_PASSWORD", ""),
            )
            # token = self.asset_mgr.get_token()
            collection_members = self.asset_mgr.get_collection_members() or []
            # self.asset_mgr.close_session()

            if not collection_members:
                self.table.add_row("No glossary terms found", "")
                return

            for member in collection_members:
                name = member.get("displayName", "Unknown")
                description = member.get("description", "")
                guid = member.get("guid", "?")
                self.table.add_row(name, description, guid)
        except Exception as e:
            self.table.add_row("Error", str(e))

    @on(Button.Pressed, "#refresh_btn")
    def on_refresh(self, event: Button.Pressed) -> None:
        self.load_members()
