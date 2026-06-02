""" python

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a common widget for my_egeria.


"""

from textual.widgets import Button, Static
from textual.screen import Screen
from textual.containers import Container


class PopupScreen(Screen):
    """Simple popup with OK button that exits the app."""

    def __init__(self, message: str):
        super().__init__()
        self.message = message

    async def on_mount(self):
        await self.mount(
            Container(
                Static(self.message, id="popup-message"),
                Button("OK", id="popup-ok", variant="primary"),
            )
        )

    async def on_button_pressed(self, event):
        if event.button.id == "popup-ok":
            await self.app.shutdown()


def show_popup_and_exit(message: str):
    """Convenience function to show popup and exit."""
    from app import MyApp  # Ensure correct app import path

    app = MyApp()
    app.push_screen(PopupScreen(message))
