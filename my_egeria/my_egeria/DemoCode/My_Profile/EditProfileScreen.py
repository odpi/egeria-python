"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""

from pyegeria import Egeria
from pyegeria import load_app_config, settings, MyProfile, PyegeriaException
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Header, Static, Input, Button, Footer


class EditProfileScreen(ModalScreen[int]):
    """Modal screen to create a new user profile in Egeria.

    Dismisses with:
      200 on success
      4xx on failure
    """

    BINDINGS = [("q", "dismiss(200)", "Quit")]
    CSS_PATH = "my_profile.tcss"

    def __init__(self, user,
                        password,
                        view_server,
                        platform_url,
                        karma_points,
                        user_profile
                 ):
        super().__init__()
        load_app_config()
        # config_logging()
        self.karma_points = 0

        self.user_name = user
        self.user_password = password
        self.view_server = view_server
        self.platform_url = platform_url
        self.karma_points = karma_points
        self.user_profile = user_profile
        self.user_identities = self.user_identities
        self.projects = self.user_profile.get("Projects") or []
        self.communities = self.user_profile.get("Communities") or []
        self.roles = self.user_profile.get("Roles") or []
        self.teams = self.user_profile.get("Teams") or []
        print("Platform:", self.platform_url)
        print("View Server:", self.view_server)

    def on_mount(self) -> None:
        self.title = f"User: {self.user_name}, Karma Points: {self.karma_points}"
        self.sub_title = f"Edit Egeria Profile for user: {self.user_name}"
        # retrieve person profile details


    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Create a new profile in Egeria")
        yield ScrollableContainer(
            Static("Edit your information below:"),
            Input(placeholder=self.user_profile.get("courtesyTitle"), id="user_title"),
            Input(placeholder=self.user_profile.get("givenNames"), id="user_given_names"),
            Input(placeholder=self.user_profile.get("surname"), id="user_family_name"),
            Input(placeholder=self.user_profile.get("displayName"), id="user_preferred_name"),
            Input(placeholder=self.user_profile.get("pronouns"), id="user_pronouns"),
            Input(placeholder=self.user_profile.get("jobTitle"), id="user_job_title"),
            Input(placeholder=self.user_profile.get("description"), id="user_description"),
            Input(placeholder=self.user_profile.get("employeeNumber"), id="user_employee_id"),
            Input(placeholder=self.user_profile.get("preferredLanguage"), id="user_preferred_language"),
            Input(placeholder=self.user_profile.get("residentCountry"), id="user_resident_country"),
            Input(placeholder=self.user_profile.get("timeZone"), id="user_time_zone"),
            Button("Edit Profile", id="edit_profile_btn"),
            id="edit_profile_form",
        )

        yield Footer()

    @on(Button.Pressed, "#edit_profile_btn")
    def create_profile(self) -> int:
        """Create a new profile in Egeria from data provided in Input fields."""

        self.new_element_request_body:dict = {"class": "NewElementRequestBody",
                                              "isOwnAnchor": True,
                                              "properties": {
                                                  "class": "PersonProperties",
                                                  "qualifiedName": "Person" + self.query_one("#user_employee_id",
                                                                                             Input).value +
                                                                   self.query_one("#user_resident_country",
                                                                                  Input).value +
                                                                   self.query_one("#user_given_names", Input).value +
                                                                   self.query_one("#user_family_name", Input).value,
                                                  "displayName": self.query_one("#user_preferred_name", Input).value,
                                                  "courtesyTitle": self.query_one("#user_title", Input).value,
                                                  "initials": "PAT",
                                                  "givenNames": self.query_one("#user_given_names", Input).value,
                                                  "surname": self.query_one("#user_family_name", Input).value,
                                                  "fullName": self.query_one("#user_preferred_name", Input).value,
                                                  "pronouns": self.query_one("#user_pronouns", Input).value,
                                                  "jobTitle": self.query_one("#user_job_title", Input).value,
                                                  "employeeNumber": self.query_one("#user_employee_id", Input).value,
                                                  "employeeType": "Full-Time",
                                                  "preferredLanguage": self.query_one("#user_preferred_language",
                                                                                      Input).value,
                                                  "residentCountry": self.query_one("#user_resident_country",
                                                                                    Input).value,
                                                  "timeZone": self.query_one("#user_time_zone", Input).value,
                                                  "description": self.query_one("#user_description", Input).value,
                                              }
                                            }
        try:
            new_profile_inst = MyProfile(self.app.view_server, self.app.platform_url, self.app.user, self.app.password)
            new_profile_guid = new_profile_inst.add_my_profile(self.new_element_request_body)
            self.log(f"Profile created with GUID: {new_profile_guid}")
            self.dismiss(200)
            return(200)
        except PyegeriaException as e:
            self.log(f"Error creating profile: {e!s} | request={self.new_element_request_body}")
            self.dismiss(401)
            return(401)

    def action_quit(self) -> int:
        self.dismiss(200)
        return(200)


    def sample_get_and_update_profile(self):
        """
        Demonstrates fetching and updating a user profile using the Egeria client.
        """
        # Initialize the Egeria client
        # (Credential defaults are typically loaded from your .env file)
        client = Egeria()
        client.create_egeria_bearer_token()

        try:
            # 1. Fetch current profile to ensure the GUID is retrieved and cached
            client.my_profile.get_my_profile()
            my_guid = client.my_profile.my_profile_guid

            if my_guid:
                # 2. Define the update properties
                # For a user profile, use 'PersonProperties' as the properties class
                update_body = {
                    "class": "UpdateElementRequestBody",
                    "properties": {
                        "class": "PersonProperties",
                        "displayName": "Jane Doe",
                        "jobTitle": "Lead Metadata Scientist",
                        "description": "Updated profile via pyegeria API"
                    }
                }

                # 3. Execute the update via ActorManager
                client.actor_manager.update_actor_profile(my_guid, update_body)
                print("Profile updated successfully!")
            else:
                print("Could not retrieve profile GUID. Ensure you have a profile created.")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            client.close_session()