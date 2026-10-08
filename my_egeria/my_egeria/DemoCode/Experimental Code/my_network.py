"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides the main entry point and core lifecycle for the My Profile Textual App.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import asyncio

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.widgets import Header, Footer, Static, Placeholder, Input, DataTable, Button

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
        self.user_name = app_user.user_name or "tessatube"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"
        self.log(f"Platform URL: {self.platform_url}")
        self.log(f"View Server: {self.view_server}")
        self.log(f"User: {self.user_name}")
        self.log(f"User PWD: {self.user_password}")
        self.users_found: DataTable = DataTable(id="users_found")
        self.my_network: DataTable = DataTable(id="my_network")
        self.my_user_contact_details: DataTable = DataTable(id="my_user_contact_details")
        self.my_user_communities: DataTable = DataTable(id="my_user_communities")
        self.nickname = ""
        self.description = ""
        self.selected_network_member = None

    def on_mount(self) -> None:
        """Perform actions when the application is mounted."""
        self.my_network.add_column("Nickname", key="nickname")
        self.my_network.add_column("User ID", key="user_id")
        self.my_network.add_column("GUID", key="guid")
        self.my_network.add_column("Qualified Name", key="qualified_name")
        self.my_network.add_column("Notes", key="notes")
        self.my_network.cursor_type="row"
        self.my_network.zebra_stripes=True
        try:
            eclient = Egeria(self.view_server, self.platform_url, self.user_name, self.user_password)
            token=eclient.create_egeria_bearer_token(self.user_name, self.user_password)
            self.my_profile=eclient.get_my_profile(output_format="DICT")
            self.log(f"User profile retrieved successfully, {self.my_profile}")
        except PyegeriaException as e:
            self.log(f"Error: {e}")
            self.notify(f"Error, unable to retrieve user profile: {e}", severity="error", timeout=20)
            self.exit(400)
        finally:
            if eclient:
                eclient.close_session()
        if self.my_profile:
            if isinstance(self.my_profile, list):
                self.user_GUID = self.my_profile[0].get("GUID") or None
            else:
                self.notify(f"User profile is not a list: {self.my_profile}", severity="error", timeout=20)
                self.exit(400)
        else:
            self.notify(f"User profile not found: {self.user_name}", severity="error", timeout=20)
            self.exit(400)

        # Get existing peer relationship list

        try:
            eclient = Egeria(self.view_server, self.platform_url, self.user_name, self.user_password)
            token = eclient.create_egeria_bearer_token(self.user_name, self.user_password)
            peers = eclient.exec_report_spec(
                format_set_name="My-User-Peers",
                output_format="DICT",
                )
            self.log(f"Peers: {peers}")
        except PyegeriaException as e:
            self.log(f"Error creating peer relationship: {e}")
            self.notify(f"Error creating peer relationship: {e}", timeout=15, severity="error")
            self.exit(400)
        finally:
            if eclient:
                eclient.close_session()
        for peer in peers:
            self.log(f"Peer: {peer}")
            self.my_network.add_row(peer.get("Label"),
                                    peer.get("uniqueName"),
                                    peer.get("guid"),
                                    peer.get("Qualified Name"),
                                    peer.get("relationshipProperties", "description"))
            continue
        self.my_network.refresh()
        container=self.query_one("#users_network_container", ScrollableContainer)
        container.remove_children("#users_network_placeholder")
        container.mount(self.my_network)
        container.mount(Button(label="User Details", id="user_details1", variant="primary"))
        container.refresh()
        self.my_network.refresh()
        return

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(self.description)
        yield ScrollableContainer(
            Placeholder(label="Placeholder for contacts list", id="users_network_placeholder"),
            id="users_network_container")
        yield ScrollableContainer(
            Static("Search for user, enter the (partial) name to search for and press return:"),
            Input(placeholder="Name", id="user_search_input"),
            id="users_input_container")
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
        if len(user_found) == 0:
            self.notify(f"No users found with name: {event.value}", severity="warning", timeout=20)
            return
        if isinstance(user_found, str):
            self.notify(f"Error searching for users: {user_found}", severity="error", timeout=20)
            return
        if isinstance(user_found, list):
            for user in user_found:
                self.users_found.add_row(user["Display Name"], user["GUID"], user["Qualified Name"])
            self.query_one("#users_network_container", ScrollableContainer).remove_children()
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
        self.query_one("#users_input_container", ScrollableContainer).remove_children()

    def search_users(self, user_name: str) -> Any:
        self.log(f"Searching for users with name: {user_name}")
        try:
            eclient=Egeria(self.view_server, self.platform_url, self.user_name, self.user_password)
            token=eclient.create_egeria_bearer_token(self.user_name, self.user_password)
            user_found=eclient.find_actor_profiles(
                search_string=user_name,
                ignore_case=True,
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
        self.query_one("#users_input_container", ScrollableContainer).remove_children()
        self.selected_user_id = row_data[0]
        self.selected_GUID = row_data[1]
        self.selected_qualified_name = row_data[2]
        self.log(f"Selected user ID: {self.selected_user_id}")
        self.log(f"Selected GUID: {self.selected_GUID}")
        self.log(f"Selected qualified name: {self.selected_qualified_name}")
        self.query_one("#users_input_container", ScrollableContainer).mount(
            Static("Selected ID for new network contact is:"),
            Static(f"{self.selected_user_id, " ", self.selected_qualified_name}"),
            Static("Please provide a NickName to Store this contact under:"),
            Input(placeholder="Nickname", id="nickname_input"),
            Static("Optionally provide a description/comment about this relationship"),
            Input(placeholder="Description", id="description_input"),
            Button("Link Peer", id="link_peer_button", variant="primary")
            )

    @on(Input.Changed, "#nickname_input")
    def handle_nickname_input(self, event: Input.Changed):
        """Handle the submission of the user nickname input."""
        self.log(f"User nickname input submitted: {event.value}")
        self.nickname = event.value

    @on(Input.Changed, "#description_input")
    def handle_description_input(self, event: Input.Changed):
        """Handle the submission of the user description input."""
        self.log(f"User description input submitted: {event.value}")
        self.description = event.value

    @on(Button.Pressed, "#link_peer_button")
    def handle_link_peer_button(self, event: Button.Pressed):
        """Handle the submission of the link peer button.
           Since there is no validity check and both NickName and Description are optional
           we link the peer person without further upfront validation """
        self.my_network.add_row(self.nickname, self.selected_user_id, self.selected_GUID, self.selected_qualified_name)
        #add link to peer
        self.log(f"Owner GUID: {self.user_GUID} Peer selected GUID: {self.selected_GUID}")
        now = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        body = {
            "class": "NewRelationshipRequestBody",
            "properties": {
                "class": "PeerProperties",
                "peer_relationship_name": self.nickname,
                "description": self.description,
                "effective_from" : None,
                "effective_to": None
            }
        }
        self.log(f"Linking peer person: body {body} Owner GUID: {self.user_GUID} and Peer selected GUID: {self.selected_GUID}")
        try:
            eclient = Egeria(self.view_server,
                             self.platform_url,
                             self.user_name,
                             self.user_password)
            token = eclient.create_egeria_bearer_token(self.user_name, self.user_password)
            eclient.link_peer_person(self.user_GUID,
                                     self.selected_GUID,
                                     body
                                     )
            self.notify(f"Peer person linked successfully")
        except PyegeriaException as e:
            self.log(f"Error linking peer person: {e}")
            self.notify(f"Error linking peer person: {e}")
        finally:
            # clear input fields
            self.query_one("#nickname_input", Input).clear()
            self.query_one("#description_input", Input).clear()
            # reset display to allow another search
            self.query_one("#users_input_container", ScrollableContainer).remove_children()
            self.query_one("#users_network_container", ScrollableContainer).remove_children()
            self.query_one("#users_input_container").mount(
                Static("Search for user, enter the (partial) name to search for and press return:"),
                Input(placeholder="Name", id="user_search_input")
            )
            self.query_one("#users_network_container").mount(
                Static("Peer person network"),
                self.my_network,
                Button(label="User Details", id="user_details2", variant="primary")
            )
            return

    @on(DataTable.RowHighlighted, "#user_network_table")
    def handle_network_member_selected(self,event: DataTable.RowHighlighted):
        self.log(f"Row highlighted: {event.row_key}")
        self.selected_network_member = event.row_key

    @on(DataTable.RowSelected, "#user_network_table")
    def handle_network_member_selected(self, event: DataTable.RowSelected):
        self.log(f"Row selected: {event.row_key}")
        self.selected_network_member = event.row_key

    @on(Button.Pressed, "#user_details1")
    def handle_user_details_1_button(self, event: Button.Pressed):
        if self.selected_network_member:
            selected_row_data = self.my_network.get_row(self.selected_network_member)
            self.show_user_details(selected_row_data)
            return
        else:
            self.notify(f"Please select a network member to view details before using the Button.", severity="warning", timeout=10)
            return

    @on(Button.Pressed, "#user_details2")
    def handle_user_details_2_button(self, event: Button.Pressed):
        if self.selected_network_member:
            selected_row_data = self.my_network.get_row(self.selected_network_member)
            self.show_user_details(selected_row_data)
            return
        else:
            self.notify(f"Please select a network member to view details before using the Button.", severity="warning",
                        timeout=10)
            return

    def show_user_details(self, selected_row_data):
        """ Show both contact details and community membership details for the selected network member."""
        self.selected_network_member = selected_row_data
        self.user_GUID = selected_row_data[2]
        self.user_qname = selected_row_data[3]
        self.user_nickname = selected_row_data[0]
        #clear and set up the datatables
        self.my_user_contact_details.clear(columns=True)
        self.my_user_contact_details.add_columns("Name", "Method Type", "Contact Type", "Service", "Value", "GUID")
        self.my_user_contact_details.cursor_type = "row"
        self.my_user_contact_details.zebra_stripes=True
        self.my_user_communities.clear(columns=True)
        self.my_user_communities.add_columns("Name", "Assignment Type", "Description", "GUID")
        self.my_user_communities.cursor_type = "row"
        self.my_user_communities.zebra_stripes=True
        # retrieve the users contact information
        try:
            eclient=Egeria(
                self.view_server,
                self.platform_url,
                self.user_name,
                self.user_password)
            token=eclient.create_egeria_bearer_token(self.user_name, self.user_password)
            self.user_contact_details = exec_report_spec(
                                        format_set_name="My-User-Contact-Detail")
            self.log(f"Retrieved user contact details: {self.user_contact_details}")
        except Exception as e:
            self.notify(f"Error retrieving user contact details: {str(e)}", severity="error", timeout=10)
            return
        try:
            self.user_communities = exec_report_spec(
                                        format_set_name="My-User-Communities-Detail")
            self.log(f"Retrieved user community memberships: {self.user_communities}")
        except Exception as e:
            self.notify(f"Error retrieving user community memberships: {str(e)}", severity="error", timeout=10)
            return
        finally:
            if eclient:
                eclient.close_session()
        if isinstance(self.user_contact_details, list):
            for contact in self.user_contact_details:
                self.my_user_contact_details.add_row(contact.get("Name"),
                                                     contact.get("Method Type"),
                                                     contact.get("Contact Type"),
                                                     contact.get("Service"),
                                                     contact.get("Value"),
                                                     contact.get("GUID"))
        if isinstance(self.user_communities, list):
            for community in self.user_communities:
                self.my_user_communities.add_row(community.get("Name"),
                                                 community.get("Assignment Type"),
                                                 community.get("Desacription"),
                                                 community.get("GUID"))
        return

def main() -> None:
    """Entry point for the my_profile console script."""
    MyNetworkApp().run()


if __name__ == "__main__":
    main()