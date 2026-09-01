"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a user screen to allow the user to add todos to my_egeria.

"""

import pwd
from datetime import datetime
from typing import Any

import optional
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Horizontal
from textual.screen import ModalScreen
from textual.widgets import DataTable, OptionList, Header, Static, Footer, Input, Button, Switch
from textual.widgets._option_list import Option

from pyegeria import Egeria, PyegeriaException, load_app_config, settings, print_basic_exception


class ViewSubscriptionsScreen(ModalScreen):
    """View Subscription Screen for the current user in My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+a", "add_new_todo", "Add New Todo")
        ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, *args, **kwargs):
        super().__init__(id="view_subscriptions_screen", *args, **kwargs)
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield ScrollableContainer(
            Static("View Subscriptions for logged in User", id="view_subsciptions_static"),
            id="view-subscriptions_container",
        )
        yield Footer()

    def on_mount(self):

        eclient=Egeria(self.view_server,
                       self.platform_url,
                       self.user_name,
                       self.user_password
                       )
        token = eclient.create_egeria_bearer_token(self.user_name, self.user_password)  # uses env vars; or pass (user, password) explicitly

        try:
            # --- API call (show at minimum the required params; document optional ones) ---
            subscriptions = eclient.find_collections(
                search_string="*",
                metadata_element_type="DigitalSubscription"
            )

            # --- Output rendering ---
            if isinstance(subscriptions, list):
                self.log(f"Found {len(subscriptions)} subscription items")
                self.log(f"Subscriptions: {subscriptions}")
            elif isinstance(subscriptions, str):
                self.log(f"Response from get subscriptions: {subscriptions}")
                self.notify(f"Response from get subscriptions: {subscriptions}")
            else:
                self.log(f"Unrecognized Response from get subscriptions: {subscriptions}")
                self.notify("Unrecognized Response from get subscriptions: {subscriptions}")

        except PyegeriaException as e:
            print_basic_exception(e)
            self.notify(f"Pyegeria error response from get subscriptions: {e}")
        finally:
            eclient.close_session()