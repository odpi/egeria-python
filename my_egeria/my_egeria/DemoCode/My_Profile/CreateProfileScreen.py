"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""

from pyegeria import load_app_config, settings, MyProfile, PyegeriaException
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Header, Static, Input, Button, Footer


class CreateProfileScreen(ModalScreen[int]):
    """Modal screen to create a new user profile in Egeria.

    Dismisses with:
      200 on success
      4xx on failure
    """

    BINDINGS = [("q", "dismiss(200)", "Quit")]
    CSS_PATH = "my_profile.tcss"

    def __init__(self, user, password, view_server, platform_url):
        super().__init__()
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        # config_logging()
        self.karma_points = 0

        self.user_name = user
        self.user_password = password
        self.view_server = view_server
        self.platform_url = platform_url
        print("Platform:", self.platform_url)
        print("View Server:", self.view_server)

    def on_mount(self) -> None:
        self.title = f"User: {self.user_name}, Karma Points: {self.karma_points}"
        self.sub_title = f"Create Egeria Profile for user: {self.user_name}"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Create a new profile in Egeria")
        yield ScrollableContainer(
            Static("Fill in your information below:"),
            Input(placeholder="Courtesy Title", id="user_title"),
            Input(placeholder="Given Names", id="user_given_names"),
            Input(placeholder="Family Name", id="user_family_name"),
            Input(placeholder="Preferred Name", id="user_preferred_name"),
            Input(placeholder="Pronouns", id="user_pronouns"),
            Input(placeholder="Job Title", id="user_job_title"),
            Input(placeholder="Description", id="user_description"),
            Input(placeholder="Employee ID", id="user_employee_id"),
            Input(placeholder="Preferred Language", id="user_preferred_language"),
            Input(placeholder="Resident Country", id="user_resident_country"),
            Input(placeholder="Time Zone", id="user_time_zone"),
            Button("Create Profile", id="create_profile_btn"),
            id="create_profile_form",
        )

        yield Footer()

    @on(Button.Pressed, "#create_profile_btn")
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
