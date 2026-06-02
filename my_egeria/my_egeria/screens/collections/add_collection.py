# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Collections related functions of my_egeria module.


"""

import asyncio
from textual.message import Message
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Input, Button

# from .collection_browser import CollectionBrowserScreen
from my_egeria.screens.base_screen import BaseScreen
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



class AddCollectionScreen(BaseScreen):
    CSS_PATH = ["../../styles/common.css", "../../styles/add_collection.css"]

    class CollectionCreated(Message):
        def __init__(self, created: dict):
            super().__init__()
            self.created = created

    class CollectionCreateRequested(Message):
        def __init__(self, payload: Dict[str, Any]):
            super().__init__()
            self.payload = payload

    def __init__(self):
        super().__init__()
        self.service = CollectionService()

    def compose(self):
        yield from super().compose()

        # Top-half container -> bordered box -> centered vertical form
        yield Container(
            Container(
                Vertical(
                    Static("Create New Collection", id="ac_title"),
                    # Inputs
                    Static("Display Name (required)"),
                    Input(placeholder="e.g. Data Products", id="display-name"),
                    Static("Description (required)"),
                    Input(placeholder="Describe the collection purpose...", id="description"),
                    Static("Collection Type (required)"),
                    Input(placeholder="e.g. Folder, Group, Set...", id="collection-type"),
                    Static("Additional Properties (optional: key=value; key2=value2)"),
                    Input(placeholder="key=value; foo=bar", id="additional-props"),
                    # Buttons + Status
                    Horizontal(
                        Button("Create", id="create-btn"),
                        Button("Cancel", id="cancel-btn"),
                        id="ac_buttons",
                    ),
                    Static("", id="status"),
                    id="ac_form",
                ),
                id="ac_box",
            ),
            id="ac_top",
        )

    async def on_mount(self):
        await super().on_mount()

        # Position the top-level container in the upper portion; give vertical room
        top = self.query_one("#ac_top", Container)
        top.styles.dock = "top"
        top.styles.height = "60%"               # top ~60% of the screen
        top.styles.width = "100%"
        top.styles.padding = (1, 2)
        top.styles.align_horizontal = "center"  # center child (ac_box) horizontally
        top.styles.align_vertical = "top"       # keep at top within the section

        # Bordered box that contains the vertical form
        box = self.query_one("#ac_box", Container)
        box.styles.width = "70%"
        box.styles.border = ("solid", "white")
        box.styles.padding = (1, 2)
        box.styles.align_horizontal = "center"
        box.styles.align_vertical = "top"
        box.styles.min_height = 18

        form = self.query_one("#ac_form", Vertical)
        form.styles.gap = 1
        form.styles.width = "100%"

        # Title styling
        title = self.query_one("#ac_title", Static)
        title.styles.text_align = "center"
        title.styles.text_style = "bold"
        title.styles.margin = (0, 0, 1, 0)

        # Inputs: make them a reasonable width
        for iid in ("#display-name", "#description", "#collection-type", "#additional-props"):
            inp = self.query_one(iid, Input)
            inp.styles.width = "80%"

        # Buttons row: center and add a little spacing
        btn_row = self.query_one("#ac_buttons", Horizontal)
        btn_row.styles.align_horizontal = "center"
        btn_row.styles.gap = 2

        # Button margins
        self.query_one("#create-btn", Button).styles.margin = (1, 0, 0, 0)
        self.query_one("#cancel-btn", Button).styles.margin = (1, 0, 0, 0)

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "cancel-btn":
            await self.app.push_screen(CollectionBrowserScreen())
            return

        if event.button.id == "create-btn":
            display_name = (self.query_one("#display-name", Input).value or "").strip()
            description = (self.query_one("#description", Input).value or "").strip()
            collection_type = (self.query_one("#collection-type", Input).value or "").strip()
            add_props_raw = (self.query_one("#additional-props", Input).value or "").strip()

            status = self.query_one("#status", Static)

            # Required fields: name, description, type
            missing = []
            if not display_name:
                missing.append("Display Name")
            if not description:
                missing.append("Description")
            if not collection_type:
                missing.append("Collection Type")
            if missing:
                status.update(f"Required: {', '.join(missing)}.")
                return

            payload: Dict[str, Any] = {
                "display_name": display_name,
                "description": description,
                "collection_type": collection_type,
            }
            add_props: Dict[str, Any] = parse_kv_pairs(add_props_raw)
            if add_props:
                payload["additional_properties"] = add_props

            # Fire-and-forget background create; do NOT block this screen.
            async def _create_and_notify():
                try:
                    created = await asyncio.to_thread(self.service.add_collection, payload)
                except Exception:
                    created = None
                # Notify the parent screen (even on failure; parent may decide how to react)
                self.app.post_message(self.CollectionCreated(created or {}))

            asyncio.create_task(_create_and_notify())

            # Close immediately; CollectionBrowser will refresh when it receives CollectionCreated
            await asyncio.sleep(0)  # yield one tick
            await self.app.push_screen(CollectionBrowserScreen())
