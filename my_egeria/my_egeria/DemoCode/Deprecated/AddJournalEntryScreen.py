"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""
import pwd
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import DataTable, OptionList, Header, Static, Footer
from textual.widgets._option_list import Option


class AddJournalEntryScreen(ModalScreen):
    """Main Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+a", "add_new_role", "Add New Role")
        ]

    CSS_PATH = "../My_Profile/my_profile.tcss"

    def __init__(self, selected_table, *args, **kwargs):
        super().__init__(id="main_screen", *args, **kwargs)
        self.selected_table = selected_table