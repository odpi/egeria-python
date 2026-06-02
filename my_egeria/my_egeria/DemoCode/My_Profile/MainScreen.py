"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import Screen
from textual.widgets import DataTable, OptionList, Header, Static, Footer
from textual.widgets._option_list import Option


class MainScreen(Screen):
    """Main Screen for My Profile App."""

    CSS_PATH = "my_profile.tcss"

    def __init__(self):
        super().__init__()
        self.title = "Egeria"
        self.sub_title = "My Profile"

    def compose(self) -> ComposeResult:
        # place widgets into grid on screen, note sequence determines position!
        yield Header(show_clock=True)

        yield ScrollableContainer(
            Static("Projects"),
            DataTable(id="projects_table")
        )

        yield ScrollableContainer(
            Static("Communities"),
            DataTable(id="communities_table")
        )

        yield ScrollableContainer(
            Static(f"Other Functions"),
            Static(f"[b]Select a function[/b]"),
            OptionList(
                Option("User Identities", disabled=True),
                Option("Catalogs/Shop for Data"),
                Option("Edit Profile", disabled=True),
                Option("Subscriptions", disabled=True),
                Option("Technology Types"),
                Option("User Bookmarks", disabled=True),
                id="other_function_list"
            ),
            id="other_function_container"
        )

        yield ScrollableContainer(
            Static("Roles"),
            DataTable(id="roles_table")
        )

        yield ScrollableContainer(
            Static("Teams"),
            DataTable(id="teams_table")
        )

        yield ScrollableContainer(
            Static("Actions"),
            DataTable(id="actions_table")
        )

        yield ScrollableContainer(
            Static("User Identity"),
            DataTable(id="user_identity_table")
        )

        yield Footer()
