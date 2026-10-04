"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides the main entry point and core lifecycle for the My Profile Textual App.
"""

import sys
from pathlib import Path
from typing import Any
import asyncio

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.widgets import Header, Footer, Static, Placeholder, Input, DataTable

# Add the project root to sys.path to allow running this script from any directory
root_path = Path(__file__).resolve().parents[4]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from pyegeria import (
    load_app_config,
    settings,
    MyProfile,
    PyegeriaException,
    print_basic_exception,
    exec_report_spec, Egeria,
)

class MyNetworkApp(App):
    """My Network App.

    Finds user ids based on a search parameter to allow the current user to add the user(s)
    found to their private "peer network" in their profile in Egeria.
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh Data"),
        Binding("ctrl+f", "feedback", "Feedback", priority=True),
        Binding("f3", "view_feedback_log", "Feedback Log", priority=True),
    ]

    # CSS_PATH = "my_profile.tcss"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.title = "My_Network"
        self.sub_title = "Egeria network of contacts for the current user"
        self.description = "Display the user's network of (Egeria) contacts."
        load_app_config()
        app_config = settings.Environment
        self.log(f"Application Config: {app_config}")
        app_user = settings.User_Profile
        self.log(f"User Profile: {app_user}")
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"
        self.log(f"Platform URL: {self.platform_url}")
        self.log(f"View Server: {self.view_server}")
        self.log(f"User: {self.user_name}")
        self.log(f"User PWD: {self.user_password}")
        self.users_found: DataTable = DataTable(id="users_found")
        self.my_network: DataTable = DataTable(id="my_network")

    def on_mount(self) -> None:
        """Perform actions when the application is mounted."""
        self.my_network.add_column("Nickname", key="nickname")
        self.my_network.add_column("User ID", key="user_id")
        self.my_network.add_column("GUID", key="guid")
        self.my_network.add_column("Qualified Name", key="qualified_name")
        self.my_network.add_column("Notes", key="notes")
        self.my_network.cursor_type="row"
        self.my_network.zebra_stripes=True

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(self.description)
        yield ScrollableContainer(
            Placeholder(label="Placeholder for contacts list", id="users_network_placeholder"),
            id="users_network_container")
        yield ScrollableContainer(
            Static("Search for user, enter the (partial) name to search for and press return:"),
            Input(placeholder="Name", id="user_search_input"),
            id="user_input_container")
        yield Footer()

    @on(Input.Submitted, "#user_search_input")
    def handle_input_submitted(self, event: Input.Submitted) -> None:
        """Handle the submission of the user search input."""
        self.log(f"User search input submitted: {event.value}")
        user_found = self.search_users(str(event.value))
        self.users_found.clear(columns=True)
        self.users_found.add_columns("Id", "GUID", "Qualified Name")
        self.users_found.cursor_type = "row"
        self.users_found.zebra_stripes=True
        self.notify(f"Found {len(user_found)} users with name: {event.value}", severity="information", timeout=20)
        if isinstance(user_found, list):
            for user in user_found:
                self.users_found.add_row(user["User ID"], user["GUID"], user["Qualified Name"])
            self.query_one("#users_network_container", ScrollableContainer).mount(self.users_found,
                                                                                  Static("Please select a row to add to your network"))
        elif isinstance(user_found, dict):
            self.users_found.add_row(user_found["User ID"], user_found["GUID"], user_found["Qualified Name"])
            self.query_one("#users_network_container", ScrollableContainer).mount(self.users_found,
                                                                                  Static(
                                                                                      "Please select a row to add to your network"))
        else:
            self.log(f"Unexpected response type: {type(user_found)}")
            self.notify(f"Unexpected response type: {type(user_found)}")
        self.users_found.refresh()
        self.query_one("#user_input_container", ScrollableContainer).remove_children()

    def search_users(self, user_name: str) -> Any:
        self.log(f"Searching for users with name: {user_name}")
        try:
            eclient=Egeria(self.view_server, self.platform_url, self.user_name, self.user_password)
            token=eclient.create_egeria_bearer_token(self.user_name, self.user_password)
            user_found=eclient.find_user_identities(
                search_string=user_name,
                output_format="DICT",
                report_spec="User-Identities",
                query_depth=0,
                page_size=10,
            )
            self.log(f"Found {user_found} users with name: {user_name}")
        except PyegeriaException as e:
            self.log(f"Error searching for users: {e}")
            user_found="Error"
            self.notify(f"Error searching for users: {e}", severity="error", timeout=20)
        finally:
            if eclient:
                eclient.close_session()
        return user_found

    @on(DataTable.RowSelected, "#users_found")
    def on_users_found_row_selected(self, event: DataTable.RowSelected) -> None:
        self.log(f"User selected: {event.row_key}")
        self.row_selected = event.row_key
        row_data = self.users_found.get_row(self.row_selected)
        self.log(f"Selected row data: {row_data}")
        self.selected_user_id = row_data[0]
        self.selected_GUID = row_data[1]
        self.selected_qualified_name = row_data[2]
        self.log(f"Selected user ID: {self.selected_user_id}")
        self.log(f"Selected GUID: {self.selected_GUID}")
        self.log(f"Selected qualified name: {self.selected_qualified_name}")
        self.query_one("#user_input_container", ScrollableContainer).remove_children()
        self.query_one("#users_input_container", ScrollableContainer).mount(
            Static("Selected ID for new network contact is:"),
            Static(f"{self.selected_user_id, " ", self.selected_qualified_name}"),
            Static("Please provide a NickName to Store this contact under:"),
            Input(placeholder="Nickname", id="nickname_input"),
            )

    @on(Input.Submitted, "#nickname_input")
    def handle_nickname_input(self, event: Input.Submitted):
        """Handle the submission of the user nickname input."""
        self.log(f"User nickname input submitted: {event.value}")
        self.nickname = event.value
        self.my_network.add_row(self.nickname, self.selected_user_id, self.selected_GUID, self.selected_qualified_name)

def main() -> None:
    """Entry point for the my_profile console script."""
    MyNetworkApp().run()


if __name__ == "__main__":
    main()