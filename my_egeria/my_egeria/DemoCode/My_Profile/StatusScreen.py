"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""

import re
from typing import Any

from prompt_toolkit.clipboard import ClipboardData
from prompt_toolkit.clipboard.pyperclip import PyperclipClipboard
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Header, TextArea, Footer, Static


class StatusScreen(ModalScreen):
    """Modal screen to display the status of the application."""
    BINDINGS = [("q", "quit", "Quit"),
                ("return", "successful", "Continue"),
                ("b", "unsuccessful", "Bad result"),
                ("c", "copy GUID to clipboard", "Copy GUID to clipboard", )
                ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, status_message: str) -> None:
        """Initialize the StatusScreen screen."""
        super().__init__()
        self.status_message = status_message
        self.clipboard = PyperclipClipboard()

    def compose(self) -> ComposeResult:
        """ Compose the UI components for the StatusScreen screen."""
        yield Header(show_clock=True)
        yield ScrollableContainer(
            Static("Status"),
            TextArea(self.status_message, id="status_message_text_area", read_only=True),
            Static("End of Status"))
        yield Footer()

    def action_quit(self) -> None:
        """ The quit option in the footer has been selected. Dismiss the screen."""
        self.dismiss(200)

    def action_unsuccessful(self) -> None:
        """ The bad result option in the footer has been selected. Dismiss the screen."""
        self.dismiss(400)

    def action_copy_guid_to_clipboard(self) -> None:
        """ The copy GUID to clipboard option in the footer has been selected. Copy the GUID to the clipboard."""
        # The GUID is between single ' marks in the status_message when a good result is recorded.
        match = re.search(r"'(.*?)'", self.status_message)
        self.log(f"Match: {match}")
        if match:
            guid = match.group(1)
            self.clipboard.set_data(ClipboardData(text=guid))
            self.log(f"Copied GUID to clipboard: {guid}")
        else:
            self.dismiss(400)
        self.dismiss(200)

    def action_successful(self):
        """ The successful option in the footer has been selected. Dismiss the screen."""
        self.dismiss(200)
