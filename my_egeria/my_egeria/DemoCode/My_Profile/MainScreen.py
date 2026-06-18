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
        super().__init__(id="main_screen")
        self.title = "Egeria"
        self.sub_title = "My Profile"

    def compose(self) -> ComposeResult:
        # place widgets into grid on screen, note sequence determines position!
        yield Header(show_clock=True, id="main_header")

        yield ScrollableContainer(
            Static("Projects"),
            DataTable(id="projects_table"),
            id="main_projects_container"
        )

        yield ScrollableContainer(
            Static("Communities"),
            DataTable(id="communities_table"),
            id="main_communities_container"
        )

        yield ScrollableContainer(
            Static(f"Other Functions"),
            Static(f"[b]Select a function[/b]"),
            OptionList(
                Option("User Identities"),
                Option("Catalogs/Shop for Data"),
                Option("Edit Profile"),
                Option("Subscriptions", disabled=True),
                Option("Technology Types"),
                Option("User Bookmarks", disabled=True),
                id="other_function_list"
            ),
            id="other_function_container"
        )

        yield ScrollableContainer(
            Static("Roles"),
            DataTable(id="roles_table"),
            id="main_roles_container"
        )

        yield ScrollableContainer(
            Static("Teams"),
            DataTable(id="teams_table"),
            id="main_teams_container"
        )

        yield ScrollableContainer(
            Static("Actions"),
            DataTable(id="actions_table"),
            id="main_actions_container"
        )

        yield ScrollableContainer(
            Static("User Identity"),
            DataTable(id="user_identity_table"),
            id="main_identities_container"
        )

        yield Footer(id="main_footer")
