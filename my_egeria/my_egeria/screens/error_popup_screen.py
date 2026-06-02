# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Screen related functions of my_egeria module.


"""

from textual.app import App, ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Static
from textual.containers import Center


class ErrorPopup(ModalScreen):
    CSS = """    Screen > Center {
        align: center middle;
    }
    .popup {
        border: heavy red;
        padding: 1 2;
        width: 60%;
    }
    .msg {
        height: auto;
        padding: 1 0;
    }
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(**kwargs)
        self.message = message

    def compose(self) -> ComposeResult:
        yield Center(Static(self.message, classes="popup msg"))
        yield Center(Button("OK", id="ok_button", classes="popup"))

    def on_button_pressed(self, event):
        if event.button.id == "ok_button":
            self.dismiss(self.message)
