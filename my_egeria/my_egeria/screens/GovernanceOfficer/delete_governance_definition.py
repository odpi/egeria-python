# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module implements the Delete Governance Definition functions of my_egeria module.


"""
from textual.messages import Message
from typing import Dict, Any
from my_egeria.screens.base_screen import BaseScreen
from my_egeria.services.governance_officer_service import GovernanceOfficerService
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Button
import asyncio


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

class DeleteGovernanceDefinitionScreen(BaseScreen,):

    class GovernanceDefinitionDeleted(Message):
        def __init__(self, definition_guid:str,*args, **kwargs):
            super().__init__()
            self.definition_guid = definition_guid

    def __init__(self, gdGUID):
        super().__init__()
        self.gdGUID = gdGUID
        self.service = GovernanceOfficerService()

    def compose(self):
        yield from super().compose()
        # Top-half container -> bordered box -> centered vertical form
        yield Container(
            Container(
                Vertical(
                    Static("Delete a Governance Definition", id="dgd_title"),
                    Horizontal(
                    Static(f"Governance Definition GUID, {self.gdGUID}", id="delgdguid"),
                    ),
                    Horizontal(
                        Button("Delete Definition", id="gd-delete-btn"),
                        Button("Cancel", id="gd-cancel-btn"),
                        id="dgd_buttons",
                    ),
                    Static("", id="dgd-delstatus"),
                    id="dgd_form",
                ),
                id="gdg_box",
            ),
            id="gdg_top",
        )

    async def on_mount(self):
        await super().on_mount()

        # Position the top-level container in the upper portion; give vertical room
        top = self.query_one("#gdg_top", Container)
        top.styles.dock = "top"
        top.styles.height = "60%"               # top ~60% of the screen
        top.styles.width = "100%"
        top.styles.padding = (1, 2)
        top.styles.align_horizontal = "center"  # center child (ac_box) horizontally
        top.styles.align_vertical = "top"       # keep at top within the section

        # Bordered box that contains the vertical form
        box = self.query_one("#gdg_box", Container)
        box.styles.width = "70%"
        box.styles.border = ("solid", "white")
        box.styles.padding = (1, 2)
        box.styles.align_horizontal = "center"
        box.styles.align_vertical = "top"
        box.styles.min_height = 18

        form = self.query_one("#gdg-form", Vertical)
        form.styles.gap = 1
        form.styles.width = "100%"

        # Title styling
        title = self.query_one("#dgd_title", Static)
        title.styles.text_align = "center"
        title.styles.text_style = "bold"
        title.styles.margin = (0, 0, 1, 0)

        # Buttons row: center and add a little spacing
        btn_row = self.query_one("#dgd_buttons", Horizontal)
        btn_row.styles.align_horizontal = "center"
        btn_row.styles.gap = 2

        # Button margins
        self.query_one("#gd-delete-btn", Button).styles.margin = (1, 0, 0, 0)
        self.query_one("#gd-cancel-btn", Button).styles.margin = (1, 0, 0, 0)

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "gd-cancel-btn":
            await self.app.pop_screen()
            return
        elif event.button.id == "gd-delete-btn":

            payload: str = self.gdGUID

            # Fire-and-forget background create; do NOT block this screen.
            # @work
            async def _create_and_notify():
                # try:
                #     deleted = self.service.delete_governance_definition, payload
                try:
                    deleted = await asyncio.to_thread(self.service.delete_governance_definition(payload), self.gdGUID)
                except Exception:
                    deleted = None
                # Notify the parent screen (even on failure; parent may decide how to react)
                self.app.post_message(self.GovernanceDefinitionDeleted(deleted or {}))

            asyncio.create_task(_create_and_notify())

            # Close immediately; Governance Officer Browser will refresh when it receives GovernanceDefinitionCreated
            await asyncio.sleep(0)  # yield one tick
            await self.app.pop_screen()
