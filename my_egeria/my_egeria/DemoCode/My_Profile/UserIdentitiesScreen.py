"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.css.query import NoMatches
from textual.screen import ModalScreen
from textual.widgets import Header, Footer, Placeholder, DataTable, Static
from typing import Any

from pyegeria import load_app_config, settings


class UserIdentitiesScreen(ModalScreen):
    """ Modal Screen to display the user identities as stored in Egeria """

    BINDINGS = [
        ("escape", "app.pop_screen", "Exit Screen"),
        ("q", "app.pop_screen", "Exit Screen"),
        ]

    CSS_PATH = "my_profile.tcss"

    def __init__(
        self,
        user_name: str | None = None,
        user_password: str | None = None,
        karma_points: int | None = None,
        user_identities: Any = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        load_app_config()
        app_user = settings.User_Profile
        self.user_name = user_name or app_user.user_name or "garygeeke"
        self.user_password = user_password or app_user.user_pwd or "secret"
        self.karma_points = karma_points if karma_points is not None else 0
        self.user_identities = user_identities

    def on_mount(self) -> None:
        if self.user_identities is None and hasattr(self, "app"):
            self.user_identities = getattr(self.app, "user_identities", None)
        if self.karma_points == 0 and hasattr(self, "app"):
            self.karma_points = getattr(self.app, "karma_points", 0)
        self.title = "My_Egeria User Identities Screen"
        self.sub_title = f"User Identities for {self.user_name}, Karma Points: {self.karma_points}"
        self.log(f"UserIdentitiesScreen mounted for user: {self.user_name}, Karma Points: {self.karma_points}")
        self.log(f"User identity input: {self.user_identities}")
        try:
            self.user_identity_datatable = self.query_one("#user_identity_datatable", DataTable)
            self.user_identity_datatable.clear(columns=False)
        except NoMatches:
            self.user_identity_datatable : DataTable = DataTable(id="user_identity_datatable")
            self.user_identity_datatable.cursor_type="row"
            self.user_identity_datatable.zebra_stripes=True
            self.user_identity_datatable.show_header=True
            self.user_identity_datatable.add_columns("Display Name",
                                                     "Category",
                                                     "Description",
                                                     "Type Name",
                                                     "URL",
                                                     "GUID",
                                                     "Qualified Name",
                                                     "Metadata Collection ID",
                                                     "Metadata Collection Name",
                                                     "User ID",
                                                     "Distinguished Name"
                                                     )
        if self.user_identities:
            for identity in self.user_identities:
                self.log(f"User identity: {identity}")
                display_name = identity.get('Display Name', 'Unknown')
                qualified_name = identity.get('Qualified Name', 'Unknown')
                category = identity.get('Category', 'Unknown')
                description = identity.get('Description', 'No description available')
                type_name = identity.get('Type Name', 'Unknown')
                URL = identity.get('URL', 'Unknown')
                GUID = identity.get('GUID', 'Unknown')
                metadata_collection_id = identity.get('Metadata Collection ID', 'Unknown')
                metadata_collection_name = identity.get('Metadata Collection Name', 'Unknown')
                useridentity_user_id = identity.get('User ID', 'Unknown')
                distinguished_name = identity.get('Distinguished Name', 'Unknown')
                self.user_identity_datatable.add_row(
                                                    display_name,
                                                            category,
                                                            description,
                                                            type_name,
                                                            URL,
                                                            GUID,
                                                            qualified_name,
                                                            metadata_collection_id,
                                                            metadata_collection_name,
                                                            useridentity_user_id,
                                                            distinguished_name
                )
                continue
            self.query_one("#user_identities_placeholder", Placeholder).remove()
            container = self.query_one("#user_identities_container", ScrollableContainer)
            container.mount(self.user_identity_datatable)
        else:
            self.query_one("#user_identities_placeholder", Placeholder).remove()
            container = self.query_one("#user_identities_container", ScrollableContainer)
            container.mount(Static("No User Identities Data found for this user"))

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(
            Placeholder("Placeholder", id="user_identities_placeholder"),
            id = "user_identities_container"
            )
        yield Footer()

    def action_exit_screen(self) -> None:
        self.app.pop_screen()
