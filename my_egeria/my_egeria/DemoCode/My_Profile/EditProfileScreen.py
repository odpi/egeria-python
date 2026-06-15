"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""
from typing import Any

from md_processing.v2 import actor_manager

from pyegeria import Egeria
from pyegeria import load_app_config, settings, MyProfile, PyegeriaException
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Header, Static, Input, Button, Footer


class EditProfileScreen(ModalScreen[int]):
    """Modal screen to create a new user profile in Egeria.

    Dismisses with:
      200 on success or a code for further editing of related collections
      4xx on failure
    """

    BINDINGS = [("q", "dismiss(200)", "Quit"),
                ("ctrl+c", "Edit_communities", "Edit communities"),
                ("ctrl+i", "Edit_identities", "Edit identities"),
                ("ctrl+r", "Edit_roles", "Edit roles"),
                ("ctrl+t", "Edit_teams", "Edit teams"),
                ]

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
        self.user_name = user
        self.user_password = password
        self.view_server = view_server
        self.platform_url = platform_url
        self.karma_points = karma_points
        self.user_profile = user_profile
        print("Platform:", self.platform_url)
        print("View Server:", self.view_server)

    def on_mount(self) -> None:
        self.title = f"User: {self.user_name}, Karma Points: {self.karma_points}"
        self.sub_title = f"Edit Egeria Profile for user: {self.user_name}"
        # retrieve person profile details


    def compose(self) -> ComposeResult:
        self.job_title = str(self.user_profile.get("jobTitle", self.user_profile.get("Job Title", "")))
        self.log(f"Job Title: {self.job_title}")
        self.given_names = str(self.user_profile.get("givenNames", ""))
        self.log(f"Given Names: {self.given_names}")
        self.surname = str(self.user_profile.get("surname", ""))
        self.log(f"Surname: {self.surname}")
        self.display_name = str(self.user_profile.get("displayName", ""))
        self.log(f"Display Name: {self.display_name}")
        self.pronouns = str(self.user_profile.get("pronouns", ""))
        self.log(f"Pronouns: {self.pronouns}")
        self.description = str(self.user_profile.get("description", ""))
        self.log(f"Description: {self.description}")
        self.employee_id = str(self.user_profile.get("employeeNumber", self.user_profile.get("employeeId", self.user_profile.get("Employee Number", ""))))
        self.log(f"Employee ID: {self.employee_id}")
        self.preferred_language = str(self.user_profile.get("preferredLanguage", ""))
        self.log(f"Preferred Language: {self.preferred_language}")
        self.resident_country = str(self.user_profile.get("residentCountry", ""))
        self.log(f"Resident Country: {self.resident_country}")
        self.time_zone = str(self.user_profile.get("timeZone", ""))
        self.log(f"Time Zone: {self.time_zone}")
        self.courtesy_title = str(self.user_profile.get("courtesyTitle", ""))

        yield Header(show_clock=True)
        yield Static("Update your profile in Egeria", classes="span-3", id="edit_profile_title")
        yield Static()
        yield ScrollableContainer(
            Static("Edit your information as needed:"),
            Horizontal(
                Static("Courtesy Title:"),
                Input(value=self.courtesy_title, placeholder="Courtesy Title", id="user_title")),
            Horizontal(
                Static("Job Title:"),
                Input(value=self.job_title, placeholder="Job Title", id="user_job_title")),
            Horizontal(
                Static("Given Names:"),
                Input(value=self.given_names, placeholder="Given Names", id="user_given_names")),
            Horizontal(
                Static("Family/Surname:"),
                Input(value=self.surname, placeholder="Surname", id="user_family_name")),
            Horizontal(
                Static("Preferred Name:"),
                Input(value=self.display_name, placeholder="Preferred Name", id="user_preferred_name")),
            Horizontal(
                Static("Pronouns:"),
                Input(value=self.pronouns, placeholder="Pronouns", id="user_pronouns")),
            Horizontal(
                Static("Description:"),
                Input(value=self.description, placeholder="Description", id="user_description")),
            Horizontal(
                Static("Time Zone:"),
                Input(value=self.time_zone, placeholder="Time Zone", id="user_time_zone")),
            Horizontal(
                Static("Employee ID:"),
                Input(value=self.employee_id, placeholder="Employee ID", id="user_employee_id")),
            Horizontal(
                Static("Preferred Language:"),
                Input(value=self.preferred_language, placeholder="Preferred Language", id="user_preferred_language")),
            Horizontal(
                Static("Resident Country:"),
                Input(value=self.resident_country, placeholder="Resident Country", id="user_resident_country")),
            Button("Edit Profile", id="edit_profile_btn"),
            id="edit_profile_form",
            )
        yield Static()
        yield Footer()

    @on(Button.Pressed, "#edit_profile_btn")
    def create_profile(self) -> Any:
        """Update profile in Egeria from data provided in Input fields."""
        profile_guid = self.user_profile.get("guid") or self.user_profile.get("GUID")
        if not profile_guid:
            self.log("Error: Profile GUID not found, cannot update.")
            self.dismiss(401)
            return (401)

        input_q_name = "Person" + self.query_one("#user_employee_id", Input).value + \
                        self.query_one("#user_resident_country", Input).value + \
                        self.query_one("#user_given_names", Input).value + \
                        self.query_one("#user_family_name", Input).value

        input_d_name = self.query_one("#user_preferred_name", Input).value

        input_c_title = self.query_one("#user_title", Input).value

        input_g_name = self.query_one("#user_given_names", Input).value

        input_s_name = self.query_one("#user_family_name", Input).value

        input_f_name = self.query_one("#user_preferred_name", Input).value

        input_pronouns = self.query_one("#user_pronouns", Input).value

        input_j_title = self.query_one("#user_job_title", Input).value

        input_e_num = self.query_one("#user_employee_id", Input).value

        input_p_lang = self.query_one("#user_preferred_language", Input).value

        input_r_country = self.query_one("#user_resident_country", Input).value

        input_t_z = self.query_one("#user_time_zone", Input).value

        input_desc = self.query_one("#user_description", Input).value

        self.log(f"Input q_name:{input_q_name}")
        self.log(f"Input d_name:{input_d_name}")
        self.log(f"Input j_title:{input_j_title}")
        self.log(f"Input e_num:{input_e_num}")
        self.log(f"Input p_lang:{input_p_lang}")
        self.log(f"Input r_country:{input_r_country}")
        self.log(f"Input t_z:{input_t_z}")
        self.log(f"Input desc:{input_desc}")

        props: dict = {}
        props.update({"class": "PersonProperties"})
        if input_q_name:
            props.update({"qualifiedName": input_q_name})
        if input_d_name:
            props.update({"displayName": input_d_name})
        if input_c_title:
            props.update({"courtesyTitle": input_c_title})
        if input_g_name:
            props.update({"givenNames": input_g_name})
        if input_s_name:
            props.update({"surname": input_s_name})
        if input_f_name:
            props.update({"fullName": input_f_name})
        if input_pronouns:
            props.update({"pronouns": input_pronouns})
        if input_j_title:
            props.update({"jobTitle": input_j_title})
        if input_e_num:
            props.update({"employeeNumber": input_e_num})
        if input_p_lang:
            props.update({"preferredLanguage": input_p_lang})
        if input_r_country:
            props.update({"residentCountry": input_r_country})
        if input_t_z:
            props.update({"timeZone": input_t_z})
        if input_desc:
            props.update({"description": input_desc})

        self.log(f"Props: {props}")

        self.update_element_request_body: dict = {"class": "UpdateElementRequestBody",
                                                 "isOwnAnchor": True,
                                                 "properties": props
                                                 }
        try:
            new_profile_inst = Egeria(self.view_server, self.platform_url, self.user_name, self.user_password)
            new_profile_inst.create_egeria_bearer_token(self.user_name, self.user_password)
            new_profile_inst.update_actor_profile(profile_guid, self.update_element_request_body)
            self.log(f"Profile updated for GUID: {profile_guid}")
            self.dismiss(200)
            return (200)
        except PyegeriaException as e:
            self.log(f"Error creating profile: {e!s} | request={self.update_element_request_body}")
            self.dismiss(401)
            return (401)

    def action_quit(self) -> int:
        self.dismiss(200)
        return(200)

    def action_Edit_communities(self) -> str:
        self.dismiss("community")

    def action_Edit_identities(self) -> str:
        self.dismiss("identity")

    def action_Edit_roles(self) -> str:
        self.dismiss("role")

    def action_Edit_teams(self) -> str:
        self.dismiss("team")