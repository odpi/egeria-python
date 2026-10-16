"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides the main entry point and core lifecycle for the My Profile Textual App.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer, Grid
from textual.css.query import NoMatches
from textual.screen import ModalScreen
from textual.widgets import Header, Footer, Static, Placeholder, Input, DataTable, Button, Label

# Add the project root to sys.path to allow running this script from any directory
root_path = Path(__file__).resolve().parents[4]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

import os
os.environ.setdefault("PYEGERIA_CONFIG_DIRECTORY", str(root_path / "config"))

from pyegeria import (
    load_app_config,
    settings,
    MyProfile,
    PyegeriaException,
    print_basic_exception,
    exec_report_spec, Egeria,
)

class ConfirmRemoveScreen(ModalScreen[bool]):
    """Modal dialog asking the user to confirm removing a peer from their network.
       Dismisses with True if the user confirms, False otherwise."""

    DEFAULT_CSS = """
    ConfirmRemoveScreen {
        align: center middle;
    }
    #confirm_dialog {
        grid-size: 2;
        grid-gutter: 1 2;
        grid-rows: 1fr 3;
        padding: 0 1;
        width: 60;
        height: 11;
        border: thick $background 80%;
        background: $surface;
    }
    #confirm_question {
        column-span: 2;
        height: 1fr;
        width: 1fr;
        content-align: center middle;
    }
    #confirm_dialog Button {
        width: 100%;
    }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, question: str) -> None:
        super().__init__()
        self.question = question

    def compose(self) -> ComposeResult:
        yield Grid(
            Label(self.question, id="confirm_question"),
            Button("Remove", variant="error", id="confirm_remove"),
            Button("Cancel", variant="primary", id="confirm_cancel"),
            id="confirm_dialog",
        )

    @on(Button.Pressed, "#confirm_remove")
    def handle_confirm(self, event: Button.Pressed) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#confirm_cancel")
    def handle_cancel(self, event: Button.Pressed) -> None:
        self.dismiss(False)

    def action_cancel(self) -> None:
        self.dismiss(False)


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
        self.peer_qname = None,
        self.peer_dname = None,
        self.peer_fname = None,
        self.peer_pronouns = None,
        self.peer_guid = None,
        self.peer_description = None
        # GUID of the peer whose details are currently displayed (get_peer_data resets self.peer_guid)
        self.details_peer_guid = None

    def on_mount(self) -> None:
        """Perform actions when the application is mounted."""
        self.my_network.add_columns("Qualified Name", "Display Name", "Full Name", "Pronouns", "GUID", "Description")
        self.my_network.cursor_type="row"
        self.my_network.zebra_stripes=True
        error_flag = 0
        try:
            eclient = Egeria(self.view_server, self.platform_url, self.user_name, self.user_password)
            token=eclient.create_egeria_bearer_token(self.user_name, self.user_password)
            self.my_profile=eclient.get_my_profile(output_format="DICT")
            self.log(f"User profile retrieved successfully, {self.my_profile}")
        except PyegeriaException as e:
            self.log(f"Error: {e}")
            self.notify(f"Error, unable to retrieve user profile: {e}", severity="error", timeout=20)
            error_flag = 1
        finally:
            if eclient:
                eclient.close_session()
            if error_flag == 1:
            # Use the error_flag to see if there was an error and if so exit
                self.exit(400)
        if isinstance(self.my_profile, list):
            self.user_GUID = self.my_profile[0].get("GUID") or None
        else:
            self.notify(f"User profile is not a list: {self.my_profile}", severity="error", timeout=20)
            self.exit(400)
        self.get_peer_data()
        return


    def get_peer_data(self):
        # clear out DataTable
        self.my_network.clear()
        # Get existing peer relationship list
        try:
            eclient = Egeria(self.view_server, self.platform_url, self.user_name, self.user_password)
            token = eclient.create_egeria_bearer_token(self.user_name, self.user_password)
            open_metadata_type_name = "Referenceable"
            relationship_type = "Peer"
            body = {
                "class": "ResultsRequestBody",
                "metadataElementTypeName": open_metadata_type_name,
                "includeOnlyRelationships": ["ContactThrough"]
            }
            peers = eclient.get_related_elements(element_guid=self.user_GUID,
                                                 relationship_type=relationship_type,
                                                 body=body)
            self.log(f"Peers: {peers}")
        except PyegeriaException as e:
            self.log(f"Error creating peer relationship: {e}")
            self.notify(f"Error creating peer relationship: {e}", timeout=15, severity="error")
            self.exit(400)
        finally:
            if eclient:
                eclient.close_session()
        if peers != "No elements found":
            for peer in peers:
                self.log(f"Peer: {peer}")
                peer_properties = peer.get("properties", None)
                self.log(f"Peer Properties: {peer_properties}")
                peer_related_by = peer.get("relatedBy", None)
                self.log(f"Peer Related By: {peer_related_by}")
                peer_relationship_properties = peer.get("relationshipProperties", None)
                self.log(f"Peer Relationship Properties: {peer_relationship_properties}")
                if peer_properties is not None:
                    if peer_properties.get("class") == "PersonProperties" and peer_properties.get("typeName") == "Person":
                        self.peer_qname = peer_properties.get("qualifiedName")
                        self.peer_dname = peer_properties.get("displayName")
                        self.peer_fname = peer_properties.get("fullName")
                        self.peer_pronouns = peer_properties.get("pronouns")
                    # the peer's own GUID is in its elementHeader - relatedBy describes the Peer relationship
                    self.peer_guid = (peer.get("elementHeader") or {}).get("guid")
                    if peer_relationship_properties is not None:
                        self.peer_description = peer_relationship_properties.get("description")
                    self.my_network.add_row(self.peer_qname,
                                            self.peer_dname,
                                            self.peer_fname,
                                            self.peer_pronouns,
                                            self.peer_guid,
                                            self.peer_description)
                    self.my_network.cursor_type = "row"
                    # reset variables
                    self.peer_qname = None
                    self.peer_dname = None
                    self.peer_fname = None
                    self.peer_pronouns = None
                    self.peer_guid = None
                    self.peer_description = None
                    continue
                continue
        else:
            self.notify(f"No peers found for user: {self.user_name}", timeout=15, severity="error")
        self.my_network.refresh()
        container=self.query_one("#users_network_container", ScrollableContainer)
        container.remove_children("#users_network_placeholder")
        container.mount(self.my_network)
        try:
            self.query_one("#user_details1", Button)
        except NoMatches:
            self.log("Button 1 not found")
            try: self.query_one("#user_details2", Button)
            except NoMatches:
                self.log("Button 2 not found")
                container.mount(Button(label="User Details", id="user_details1", variant="primary"))
        try:
            self.query_one("#remove_peer_button", Button)
        except NoMatches:
            container.mount(Button(label="Remove from Network", id="remove_peer_button", variant="error"))
        # container.refresh()
        # self.my_network.refresh()

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
        yield ScrollableContainer(id="user_details_container")
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
    def handle_users_found_row_selected(self, event: DataTable.RowSelected) -> None:
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
                self.my_network
                )
            # update the data table to display the updated list of peers
            # (get_peer_data also mounts the User Details button if it isn't already present)
            self.get_peer_data()
            return

    @on(DataTable.RowHighlighted, "#my_network")
    def handle_network_member_highlighted(self,event: DataTable.RowHighlighted):
        self.log(f"Row highlighted: {event.row_key}")
        self.selected_network_member = event.row_key
        return

    @on(DataTable.RowSelected, "#my_network")
    def handle_network_member_selected(self, event: DataTable.RowSelected):
        self.log(f"Row selected: {event.row_key}")
        self.selected_network_member = event.row_key
        return

    @on(Button.Pressed, "#user_details1")
    def handle_user_details_1_button(self, event: Button.Pressed):
        if self.selected_network_member:
            selected_row_data = self.my_network.get_row(self.selected_network_member)
            self.log(f"Selected row data: {selected_row_data}")
            self.show_user_details(selected_row_data)
            return
        else:
            self.notify(f"Please select a network member to view details before using the Button.", severity="warning", timeout=10)
            return

    @on(Button.Pressed, "#remove_peer_button")
    def handle_remove_peer_button(self, event: Button.Pressed):
        """Remove the Peer relationship between the current user and the highlighted network member."""
        if not self.selected_network_member:
            self.notify(f"Please select a network member to remove before using the Button.", severity="warning", timeout=10)
            return
        selected_row_data = self.my_network.get_row(self.selected_network_member)
        self.log(f"Selected row data for removal: {selected_row_data}")
        peer_dname = selected_row_data[1]
        peer_guid = selected_row_data[4]
        if not peer_guid:
            self.notify(f"No GUID found for network member {peer_dname}", severity="error", timeout=10)
            return

        def confirm_removal(confirmed: bool | None) -> None:
            if confirmed:
                self.remove_peer(peer_guid, peer_dname)
            else:
                self.notify(f"{peer_dname} was not removed from your network", severity="information", timeout=5)

        self.push_screen(ConfirmRemoveScreen(f"Remove {peer_dname} from your network?"), confirm_removal)
        return

    def remove_peer(self, peer_guid: str, peer_dname: str) -> None:
        """Unlink the peer from the current user's profile and refresh the network display."""
        body = {
            "class": "DeleteRelationshipRequestBody"
        }
        self.log(f"Unlinking peer person: body {body} Owner GUID: {self.user_GUID} and Peer GUID: {peer_guid}")
        eclient = None
        try:
            eclient = Egeria(self.view_server,
                             self.platform_url,
                             self.user_name,
                             self.user_password)
            token = eclient.create_egeria_bearer_token(self.user_name, self.user_password)
            # same GUID order as link_peer_person: owner first, peer second
            eclient.unlink_peer_person(self.user_GUID,
                                       peer_guid,
                                       body
                                       )
            self.notify(f"{peer_dname} removed from your network")
        except PyegeriaException as e:
            self.log(f"Error unlinking peer person: {e}")
            self.notify(f"Error removing {peer_dname} from your network: {e}", severity="error", timeout=15)
            return
        finally:
            if eclient:
                eclient.close_session()
        # the removed row's key is no longer valid, so clear the selection before reloading the peers
        self.selected_network_member = None
        # hide the details panel if it is showing the peer that was just removed
        if self.details_peer_guid == peer_guid:
            self.query_one("#user_details_container", ScrollableContainer).display = False
            self.details_peer_guid = None
        self.get_peer_data()
        return

    def show_user_details(self, selected_row_data):
        """ Show both contact details and community membership details for the selected network member."""
        # keep the peer's details separate from self.user_GUID, which is the logged-in user's own profile GUID
        self.log(f"Selected row data: {selected_row_data}")
        self.peer_qname = selected_row_data[0]
        self.peer_dname = selected_row_data[1]
        self.peer_fname = selected_row_data[2]
        self.peer_pronouns = selected_row_data[3]
        self.peer_guid = selected_row_data[4]
        self.peer_description = selected_row_data[5]
        self.log(f"Peer details: GUID={self.peer_guid}, qname={self.peer_qname}, full_name={self.peer_fname}, display_name={self.peer_dname}, pronouns={self.peer_pronouns}, description={self.peer_description}")
        if not self.peer_guid:
            self.notify(f"No GUID found for network member {self.peer_dname}", severity="error", timeout=10)
            return
        #clear and set up the datatables
        self.my_user_contact_details.clear(columns=True)
        self.my_user_contact_details.add_columns("Name", "Method Type", "Contact Type", "Service", "Value", "GUID")
        self.my_user_contact_details.cursor_type = "row"
        self.my_user_contact_details.zebra_stripes=True
        self.my_user_communities.clear(columns=True)
        self.my_user_communities.add_columns("Name", "Assignment Type", "Description", "GUID")
        self.my_user_communities.cursor_type = "row"
        self.my_user_communities.zebra_stripes=True
        # retrieve the peer's profile and extract contact methods and communities using the
        # My-User report spec (whose detail specs are My-User-Contact-Detail / My-User-Communities-Detail)
        eclient = None
        try:
            eclient=Egeria(
                self.view_server,
                self.platform_url,
                self.user_name,
                self.user_password)
            token=eclient.create_egeria_bearer_token(self.user_name, self.user_password)
            peer_profile = eclient.get_actor_profile_by_guid(self.peer_guid, output_format="JSON")
            peer_details = eclient._generate_my_profile_output(peer_profile, output_format="DICT",
                                                               report_spec="My-User")
            self.log(f"Retrieved peer profile details: {peer_details}")
        except Exception as e:
            self.notify(f"Error retrieving details for {self.peer_dname}: {str(e)}", severity="error", timeout=10)
            return
        finally:
            if eclient:
                eclient.close_session()
        if isinstance(peer_details, list) and peer_details:
            peer_details = peer_details[0]
        if not isinstance(peer_details, dict):
            self.notify(f"No profile details found for {self.peer_dname}", severity="warning", timeout=10)
            return
        self.user_contact_details = peer_details.get("Contact Methods") or []
        self.user_communities = peer_details.get("Communities") or []
        self.log(f"User details: {self.user_contact_details}")
        self.log(f"User communities: {self.user_communities}")
        for contact in self.user_contact_details:
            self.my_user_contact_details.add_row(contact.get("name"),
                                                 contact.get("contactMethodType"),
                                                 contact.get("contactType"),
                                                 contact.get("contactMethodService"),
                                                 contact.get("contactMethodValue"),
                                                 contact.get("guid"))
        for community in self.user_communities:
            self.my_user_communities.add_row(community.get("name"),
                                             community.get("assignmentType"),
                                             community.get("description"),
                                             community.get("guid"))
        # display the tables, mounting them the first time through
        container = self.query_one("#user_details_container", ScrollableContainer)
        container.display = True
        self.details_peer_guid = self.peer_guid
        try:
            container.query_one("#user_details_heading", Static).update(f"Details for {self.peer_dname}")
        except NoMatches:
            container.mount(Static(f"Details for {self.peer_dname}", id="user_details_heading"),
                            Static("Contact Methods:"),
                            self.my_user_contact_details,
                            Static("Communities:"),
                            self.my_user_communities)
        if not self.user_contact_details:
            self.notify(f"No contact methods found for {self.peer_dname}", severity="information", timeout=10)
        if not self.user_communities:
            self.notify(f"No community memberships found for {self.peer_dname}", severity="information", timeout=10)
        return

def main() -> None:
    """Entry point for the my_profile console script."""
    MyNetworkApp().run()


if __name__ == "__main__":
    main()