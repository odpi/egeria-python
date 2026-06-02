# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Collections related functions of my_egeria module.


"""

from textual.widgets import Static, DataTable, Button, Input
from textual.containers import Vertical, Horizontal
from my_egeria.services.collection_service import CollectionService
from ..base_screen import BaseScreen


class CollectionDetailsScreen(BaseScreen):
    CSS_PATH = ["../styles/common.css", "/styles/collection_details.css"]

    def __init__(self, collection_guid: str):
        super().__init__()
        self.collection_guid = collection_guid
        self.service = CollectionService()
        self.details_table = DataTable()
        self.members_table = DataTable()

    def compose(self):
        yield from super().compose()
        self.details_table.add_columns("Field", "Value")
        self.members_table.add_columns(
            "Member GUID", "Display Name", "Qualified Name", "Type"
        )
        yield Vertical(
            Static(f"Collection Details: {self.collection_guid}", classes="header"),
            self.details_table,
            Static("Members", classes="subheader"),
            self.members_table,
            Horizontal(
                Button("Back", id="back-btn"),
                Button("Delete", id="delete-btn", classes="danger"),
                Input(placeholder='Type "DELETE" to confirm', id="confirm-input"),
            ),
            Static("", id="status"),
        )

    async def on_mount(self):
        await super().on_mount()
        await self.load_details()
        await self.load_members()

    async def load_details(self):
        self.details_table.clear()
        try:
            col = await self.service.get_collection_details_async(self.collection_guid)
            rows = [
                ("GUID", col.get("GUID") or col.get("guid") or ""),
                (
                    "Display Name",
                    col.get("display_name") or col.get("displayName") or "",
                ),
                (
                    "Qualified Name",
                    col.get("qualified_name") or col.get("qualifiedName") or "",
                ),
                ("Description", col.get("description") or col.get("summary") or ""),
                ("Type", col.get("type_name") or col.get("typeName") or ""),
            ]
            for k, v in rows:
                if v not in (None, "", []):
                    self.details_table.add_row(k, str(v))

            known = {k for k, _ in rows}
            for key, value in sorted(col.items()):
                if key in {
                    "GUID",
                    "guid",
                    "display_name",
                    "displayName",
                    "qualified_name",
                    "qualifiedName",
                    "description",
                    "summary",
                    "type_name",
                    "typeName",
                }:
                    continue
                self.details_table.add_row(key, str(value))
        except Exception as e:
            self.details_table.add_row("Error", str(e))

    async def load_members(self):
        self.members_table.clear()
        try:
            members = await self.service.get_collection_members_async(self.collection_guid)
            if not members:
                self.members_table.add_row("", "No members", "", "")
                return
            for m in members:
                self.members_table.add_row(
                    m.get("GUID", "") or m.get("guid", ""),
                    m.get("display_name", "") or m.get("displayName", ""),
                    m.get("qualified_name", "") or m.get("qualifiedName", ""),
                    m.get("type_name", "") or m.get("typeName", ""),
                )
        except Exception as e:
            self.members_table.add_row("", f"Error: {e}", "", "")

    async def on_button_pressed(self, event: Button.Pressed):
        status = self.query_one("#status", Static)
        if event.button.id == "back-btn":
            await self.app.pop_screen()
            return

        if event.button.id == "delete-btn":
            confirm = self.query_one("#confirm-input", Input).value.strip()
            if confirm != "DELETE":
                status.update('Type "DELETE" in the confirm box to proceed.')
                return
            try:
                await self.service.delete_collection_async(self.collection_guid)
                status.update("Deleted successfully.")
                await self.app.pop_screen()
            except Exception as e:
                status.update(f"Error: {e}")
