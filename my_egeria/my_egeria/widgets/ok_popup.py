""" python

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a common widget for my_egeria.


"""

from textual.widget import Widget
from textual.widgets import Button, Static
from textual.containers import Vertical
from textual.app import ComposeResult


class OkPopup(Widget):
    """A simple modal popup with an OK button."""

    DEFAULT_CSS = """
    OkPopup {
        align: center middle;
        background: $surface;
        border: round $accent;
        padding: 2;
        width: 60%;
        height: auto;
    }
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(**kwargs)
        self.message = message

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(self.message, classes="popup-message"), Button("OK", id="ok-btn")
        )

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "ok-btn":
            await self.remove()
