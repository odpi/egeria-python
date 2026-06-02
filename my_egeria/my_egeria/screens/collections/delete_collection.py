# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides a delete collection function for my_egeria.


"""

import asyncio
# refactor from asyncio to textual @work feature
from textual.message import Message
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Button
from ..base_screen import BaseScreen
from my_egeria.services.collection_service import CollectionService
from typing import Dict, Any

def parse_kv_pairs(text: str) -> Dict[str, Any]:
    """
    Parse a simple 'key=value;key2=value2' string into a dict.
    Ignores empty segments; trims whitespace. No escaping supported.
    """
    result: Dict[str, Any] = {}
    if not text:
        return result
    for part in text.split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            k, v = part.split("=", 1)
            result[k.strip()] = v.strip()
        else:
            # Bare key → True
            result[part] = True
    return result



class DeleteCollectionScreen(BaseScreen):
    CSS_PATH = ["../../styles/common.css", "../../styles/delete_collection.css"]

    class CollectionDeleted(Message):
        def __init__(self, deleted: dict):
            super().__init__()
            self.deleted = deleted

    class CollectionDeleteRequested(Message):
        def __init__(self, payload: Dict[str, Any]):
            super().__init__()
            self.payload = payload

    def __init__(self, guid2delete):
        super().__init__()
        self.service = CollectionService()
        self.guid2delete = guid2delete

    def compose(self):
        yield from super().compose()

        # Top-half container -> bordered box -> centered vertical form
        yield Container(
            Container(
                Vertical(
                    Static("Delete a Collection", id="dc_title"),
                    # Inputs
                    Static(f"Collection GUID, {self.guid2delete}", id="delcolguid"),
                    Static(f"Display Name", id="delcolname"),
                    Static(f"Description", id="delcoldesc"),
                    Horizontal(
                        Button("Delete", id="delete-btn"),
                        Button("Cancel", id="dcancel-btn"),
                        id="dc_buttons",
                    ),
                    Static("", id="delstatus"),
                    id="dc_form",
                ),
                id="dc_box",
            ),
            id="dc_top",
        )

    async def on_mount(self):
        await super().on_mount()

        # Position the top-level container in the upper portion; give vertical room
        top = self.query_one("#dc_top", Container)
        top.styles.dock = "top"
        top.styles.height = "60%"               # top ~60% of the screen
        top.styles.width = "100%"
        top.styles.padding = (1, 2)
        top.styles.align_horizontal = "center"  # center child (ac_box) horizontally
        top.styles.align_vertical = "top"       # keep at top within the section

        # Bordered box that contains the vertical form
        box = self.query_one("#dc_box", Container)
        box.styles.width = "70%"
        box.styles.border = ("solid", "white")
        box.styles.padding = (1, 2)
        box.styles.align_horizontal = "center"
        box.styles.align_vertical = "top"
        box.styles.min_height = 18

        form = self.query_one("#dc_form", Vertical)
        form.styles.gap = 1
        form.styles.width = "100%"

        # Title styling
        title = self.query_one("#dc_title", Static)
        title.styles.text_align = "center"
        title.styles.text_style = "bold"
        title.styles.margin = (0, 0, 1, 0)

        # Buttons row: center and add a little spacing
        btn_row = self.query_one("#dc_buttons", Horizontal)
        btn_row.styles.align_horizontal = "center"
        btn_row.styles.gap = 2

        # Button margins
        self.query_one("#delete-btn", Button).styles.margin = (1, 0, 0, 0)
        self.query_one("#dcancel-btn", Button).styles.margin = (1, 0, 0, 0)

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "dcancel-btn":
            await self.app.pop_screen()
            return
        elif event.button.id == "delete-btn":

            payload: str = self.guid2delete

            # Fire-and-forget background create; do NOT block this screen.
            # @work
            async def _create_and_notify():
                # try:
                #     deleted = self.service.delete_collection, payload
                try:
                    deleted = await asyncio.to_thread(self.service.delete_collection, self.guid2delete)
                except Exception:
                    deleted = None
                # Notify the parent screen (even on failure; parent may decide how to react)
                self.app.post_message(self.CollectionDeleted(deleted or {}))

            asyncio.create_task(_create_and_notify())

            # Close immediately; CollectionBrowser will refresh when it receives CollectionCreated
            await asyncio.sleep(0)  # yield one tick
            await self.app.pop_screen()
