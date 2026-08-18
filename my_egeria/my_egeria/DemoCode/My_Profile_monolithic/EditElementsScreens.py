"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""
from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Horizontal
from textual.css.query import NoMatches
from textual.screen import ModalScreen
from textual.widgets import Header, Footer, DataTable, Static, Placeholder, Input, Button

from pyegeria import PyegeriaException, Egeria, load_app_config


class EditAssociationsScreen(ModalScreen):
    """ Screen called during editing of a users profile to allow editing of the communities and projects
        they belong too."""

    BINDINGS = [
        ("e", "exit_screen", "Exit"),
    ]

    def __init__(self, columns, rows_with_keys, *args, **kwargs):
        super().__init__(*args, **kwargs, id="edit_associations_screen")
        self.main_screen = self.query_screen("main_screen")
        self.my_communities_table = self.main_screen.query_one("#communities_table", DataTable)
        self.my_projects_table = self.main_screen.query_one("#projects_table", DataTable)
        self.my_communities_table.id="my_communities_table"
        self.my_projects_table.id="my_projects_table"
        self.my_communities_table.cursor_type = "row"
        self.my_projects_table.cursor_type = "row"
        self.my_communities_table.zebra_stripes = True
        self.my_projects_table.zebra_stripes = True

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Edit Communities", classes="span-3", id="edit_communities_title")
        yield Static(" Please note you may only delete one row at a time!", classes="span-3")
        yield ScrollableContainer(
            DataTable(id="my_communities_table"),
            Horizontal(
                Button("Remove", id="remove_community", variant="error"),
                Button("Edit Values for selected row", id="edit_community", variant="warning"),
                ),
            id="edit_communities_container")
        yield ScrollableContainer(
            DataTable(id="my_projects_table"),
            Horizontal(
                Button("Remove", id="remove_project",variant="error"),
                Button("Edit Values for selected row", id="edit_project", variant="warning"),
                ),
            id="edit_projects_container")
        yield Horizontal(
            Button("Exit", id="exit_screen", variant="primary"),
            id="bottom_buttons_container")
        yield Footer()

    async def on_mount(self):
        self.log("Edit communities screen mounted")
        self.title = "Egeria - my_profile"
        self.sub_title = "Edit Communities"

    @on(DataTable.RowSelected, "#communities_table")
    def row_selected(self, event: DataTable.RowSelected):
        """ When the user selects a row in the data table store the row key"""
        self.row_key = event.row_key

    @on(DataTable.RowSelected, "#projects_table")
    def row_selected(self, event: DataTable.RowSelected):
        """ When the user selects a row in the data table store the row key"""
        self.row_key = event.row_key

    def action_exit_screen(self):
        """ The user has requested to exit the screen, return the current table data """
        self.dismiss(200)

    def action_remove_community(self):
        """ The user has selected the delete row option """
        self.log(f"Delete row selected, row key: {self.row_key}")
        # If there is a row selected, delete it and clear the row key variable
        if self.row_key:
            self.my_communities_table.remove_row(self.row_key)
            self.my_communities_table.refresh()
            # self.communities_container.refresh(layout=True)
            self.row_key = None
        # If there is no row key in the variable, inform the user by mounting a message into the container
        # and wait for any further actions.
        else:
            self.communities_container.mount(Static("Please select a row to delete prior to using the hot key!"))
            self.communities_container.refresh(layout=True)

class EditBlogsScreen(ModalScreen):
    """ Screen called during editing of a users profile to allow editing of the blogs
        they belong too."""

    BINDINGS = [
        ("escape", "exit_screen", "Exit"),
        ("d", "delete_row", "Delete Row")
    ]

    def __init__(self, columns, rows_with_keys, *args, **kwargs):
        super().__init__(*args, **kwargs, id="edit_blogs_screen")
        self.my_blogs_table: DataTable = DataTable(id="blogs_destination")
        self.row_key = None
        self.columns = columns
        self.rows_with_keys = rows_with_keys
        self.blogs_container: ScrollableContainer

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Edit Blogs", classes="span-3", id="edit_blogs_title")
        yield Static(" Please note you may only delete one row at a time!", classes="span-3")
        yield ScrollableContainer(id="edit_blogs_container")
        yield Footer()

    async def on_mount(self):
        self.log("Edit blogs screen mounted")
        self.title = "Egeria - my_profile"
        self.sub_title = "Edit Blogs"
        # Populate DataTable
        self.my_blogs_table.clear(columns=True)
        self.my_blogs_table.add_columns(*self.columns)
        for key_str, cell_values in self.rows_with_keys:
            self.my_blogs_table.add_row(*cell_values, key=key_str)

        try:
            # Access the edit blogs container in the screen composition objects
            self.blogs_container = self.query_one("#edit_blogs_container", ScrollableContainer)
            self.log(f"Blogs container found: {self.blogs_container}")
            # Mount the table into the container
            await self.blogs_container.mount(self.my_blogs_table)
            self.log("Table mounted into container")
            # To make sure, refresh the container object on the display
            self.blogs_container.refresh(layout=True)
            self.my_blogs_table.refresh(layout=True)
            self.focus()
            self.call_after_refresh(self.my_blogs_table.focus)
        except NoMatches as e:
            # If there is an error finding the container
            self.log(f"Edit blogs container not found - Error: {e}")
            await self.dismiss(400)

    @on(DataTable.RowSelected, "#blogs_destination")
    def row_selected(self, event: DataTable.RowSelected):
        """ When the user selects a row in the data table store the row key"""
        self.row_key = event.row_key

    def action_exit_screen(self):
        """ The user has requested to exit the screen, return the current table data """
        rows_with_keys = []
        for row_key in self.my_blogs_table.rows:
            rows_with_keys.append((row_key.value, self.my_blogs_table.get_row(row_key)))
        self.dismiss(rows_with_keys)

    def action_delete_row(self):
        """ The user has selected the delete row option """
        self.log(f"Delete row selected, row key: {self.row_key}")
        # If there is a row selected, delete it and clear the row key variable
        if self.row_key:
            self.my_blogs_table.remove_row(self.row_key)
            self.my_blogs_table.refresh()
            self.blogs_container.refresh(layout=True)
            self.row_key = None
        # If there is no row key in the variable, inform the user by mounting a message into the container
        # and wait for any further actions.
        else:
            self.blogs_container.mount(Static("Please select a row to delete prior to using the hot key!"))
            self.blogs_container.refresh(layout=True)

class EditCommunitiesScreen(ModalScreen):
    """ Screen called during editing of a users profile to allow editing of the communities
        they belong too."""

    BINDINGS = [
        ("escape", "exit_screen", "Exit"),
        ("d", "delete_row", "Delete Row")
    ]

    def __init__(self, columns, rows_with_keys, *args, **kwargs):
        super().__init__(*args, **kwargs, id="edit_communities_screen")
        self.my_communities_table: DataTable = DataTable(id="communities_destination")
        self.row_key = None
        self.columns = columns
        self.rows_with_keys = rows_with_keys
        self.communities_container: ScrollableContainer

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Edit Communities", classes="span-3", id="edit_communities_title")
        yield Static(" Please note you may only delete one row at a time!", classes="span-3")
        yield ScrollableContainer(id="edit_communities_container")
        yield Footer()

    async def on_mount(self):
        self.log("Edit communities screen mounted")
        self.title = "Egeria - my_profile"
        self.sub_title = "Edit Communities"
        # Populate DataTable
        self.my_communities_table.clear(columns=True)
        self.my_communities_table.add_columns(*self.columns)
        for key_str, cell_values in self.rows_with_keys:
            self.my_communities_table.add_row(*cell_values, key=key_str)

        try:
            # Access the edit communities container in the screen composition objects
            self.communities_container = self.query_one("#edit_communities_container", ScrollableContainer)
            self.log(f"Communities container found: {self.communities_container}")
            # Mount the table into the container
            await self.communities_container.mount(self.my_communities_table)
            self.log("Table mounted into container")
            # To make sure, refresh the container object on the display
            self.communities_container.refresh(layout=True)
            self.my_communities_table.refresh(layout=True)
            self.focus()
            self.call_after_refresh(self.my_communities_table.focus)
        except NoMatches as e:
            # If there is an error finding the container
            self.log(f"Edit communities container not found - Error: {e}")
            await self.dismiss(400)

    @on(DataTable.RowSelected, "#communities_destination")
    def row_selected(self, event: DataTable.RowSelected):
        """ When the user selects a row in the data table store the row key"""
        self.row_key = event.row_key

    def action_exit_screen(self):
        """ The user has requested to exit the screen, return the current table data """
        rows_with_keys = []
        for row_key in self.my_communities_table.rows:
            rows_with_keys.append((row_key.value, self.my_communities_table.get_row(row_key)))
        self.dismiss(rows_with_keys)

    def action_delete_row(self):
        """ The user has selected the delete row option """
        self.log(f"Delete row selected, row key: {self.row_key}")
        # If there is a row selected, delete it and clear the row key variable
        if self.row_key:
            self.my_communities_table.remove_row(self.row_key)
            self.my_communities_table.refresh()
            self.communities_container.refresh(layout=True)
            self.row_key = None
        # If there is no row key in the variable, inform the user by mounting a message into the container
        # and wait for any further actions.
        else:
            self.communities_container.mount(Static("Please select a row to delete prior to using the hot key!"))
            self.communities_container.refresh(layout=True)

class EditIdentitiesScreen(ModalScreen):
    """ Screen called during editing of a users profile to allow editing of the identities
        they have in Egeria."""

    BINDINGS = [
        ("escape", "exit_screen", "Exit"),
        ("d", "delete_row", "Delete Row")
    ]

    def __init__(self, columns, rows_with_keys, *args, **kwargs):
        super().__init__(*args, **kwargs, id="edit_identities_screen")
        self.my_identities_table: DataTable = DataTable(id="identities_destination")
        self.row_key = None
        self.columns = columns
        self.rows_with_keys = rows_with_keys
        self.identities_container: ScrollableContainer

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Edit Identities", classes="span-3", id="edit_identities_title")
        yield Static(" Please note you may only delete one row at a time!", classes="span-3")
        yield ScrollableContainer(id="edit_identities_container")
        yield Footer()

    async def on_mount(self):
        self.log("Edit identities screen mounted")
        self.title = "Egeria - my_profile"
        self.sub_title = "Edit Identities"
        # Populate DataTable
        self.my_identities_table.clear(columns=True)
        self.my_identities_table.add_columns(*self.columns)
        for key_str, cell_values in self.rows_with_keys:
            self.my_identities_table.add_row(*cell_values, key=key_str)

        try:
            # Access the edit identities container in the screen composition objects
            self.identities_container = self.query_one("#edit_identities_container", ScrollableContainer)
            self.log(f"Identities container found: {self.identities_container}")
            # Mount the table into the container
            await self.identities_container.mount(self.my_identities_table)
            self.log("Table mounted into container")
            # To make sure, refresh the container object on the display
            self.identities_container.refresh(layout=True)
            self.my_identities_table.refresh(layout=True)
            self.focus()
            self.call_after_refresh(self.my_identities_table.focus)
        except NoMatches as e:
            # If there is an error finding the container
            self.log(f"Edit identities container not found - Error: {e}")
            await self.dismiss(400)

    @on(DataTable.RowSelected, "#identities_destination")
    def row_selected(self, event: DataTable.RowSelected):
        """ When the user selects a row in the data table store the row key"""
        self.row_key = event.row_key

    def action_exit_screen(self):
        """ The user has requested to exit the screen, return the current table data """
        rows_with_keys = []
        for row_key in self.my_identities_table.rows:
            rows_with_keys.append((row_key.value, self.my_identities_table.get_row(row_key)))
        self.dismiss(rows_with_keys)

    def action_delete_row(self):
        """ The user has selected the delete row option """
        self.log(f"Delete row selected, row key: {self.row_key}")
        # If there is a row selected, delete it and clear the row key variable
        if self.row_key:
            self.my_identities_table.remove_row(self.row_key)
            self.my_identities_table.refresh()
            self.identities_container.refresh(layout=True)
            self.row_key = None
        # If there is no row key in the variable, inform the user by mounting a message into the container
        # and wait for any further actions.
        else:
            self.identities_container.mount(Static("Please select a row to delete prior to using the hot key!"))
            self.identities_container.refresh(layout=True)

class EditJournalScreen(ModalScreen):
    """ Screen called during editing of a users profile to allow editing of the journal
        they belong too."""

    BINDINGS = [
        ("escape", "exit_screen", "Exit"),
        ("d", "delete_row", "Delete Row")
    ]

    def __init__(self, columns, rows_with_keys, *args, **kwargs):
        super().__init__(*args, **kwargs, id="edit_journal_screen")
        self.my_journal_table: DataTable = DataTable(id="journal_destination")
        self.row_key = None
        self.columns = columns
        self.rows_with_keys = rows_with_keys
        self.journal_container: ScrollableContainer

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Edit Journal", classes="span-3", id="edit_journal_title")
        yield Static(" Please note you may only delete one row at a time!", classes="span-3")
        yield ScrollableContainer(id="edit_journal_container")
        yield Footer()

    async def on_mount(self):
        self.log("Edit journal screen mounted")
        self.title = "Egeria - my_profile"
        self.sub_title = "Edit Journal"
        # Populate DataTable
        self.my_journal_table.clear(columns=True)
        self.my_journal_table.add_columns(*self.columns)
        for key_str, cell_values in self.rows_with_keys:
            self.my_journal_table.add_row(*cell_values, key=key_str)

        try:
            # Access the edit journal container in the screen composition objects
            self.journal_container = self.query_one("#edit_journal_container", ScrollableContainer)
            self.log(f"Journal container found: {self.journal_container}")
            # Mount the table into the container
            await self.journal_container.mount(self.my_journal_table)
            self.log("Table mounted into container")
            # To make sure, refresh the container object on the display
            self.journal_container.refresh(layout=True)
            self.my_journal_table.refresh(layout=True)
            self.focus()
            self.call_after_refresh(self.my_journal_table.focus)
        except NoMatches as e:
            # If there is an error finding the container
            self.log(f"Edit journal container not found - Error: {e}")
            await self.dismiss(400)

    @on(DataTable.RowSelected, "#journal_destination")
    def row_selected(self, event: DataTable.RowSelected):
        """ When the user selects a row in the data table store the row key"""
        self.row_key = event.row_key

    def action_exit_screen(self):
        """ The user has requested to exit the screen, return the current table data """
        rows_with_keys = []
        for row_key in self.my_journal_table.rows:
            rows_with_keys.append((row_key.value, self.my_journal_table.get_row(row_key)))
        self.dismiss(rows_with_keys)

    def action_delete_row(self):
        """ The user has selected the delete row option """
        self.log(f"Delete row selected, row key: {self.row_key}")
        # If there is a row selected, delete it and clear the row key variable
        if self.row_key:
            self.my_journal_table.remove_row(self.row_key)
            self.my_journal_table.refresh()
            self.journal_container.refresh(layout=True)
            self.row_key = None
        # If there is no row key in the variable, inform the user by mounting a message into the container
        # and wait for any further actions.
        else:
            self.journal_container.mount(Static("Please select a row to delete prior to using the hot key!"))
            self.journal_container.refresh(layout=True)

class EditProfileScreen(ModalScreen[Any]):
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
                        user_profile,
                        user_GUID
                 ):
        super().__init__(id="edit_profile_screen")
        load_app_config()
        self.user_name = user
        self.user_password = password
        self.view_server = view_server
        self.platform_url = platform_url
        self.karma_points = karma_points
        self.user_profile = user_profile
        self.user_GUID = user_GUID
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
            new_profile_inst.update_actor_profile(self.user_GUID, self.update_element_request_body)
            self.log(f"Profile updated for GUID: {self.user_GUID}")
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


class EditProjectsScreen(ModalScreen):
    """ Screen called during editing of a users profile to allow editing of the projects
        they belong too."""

    BINDINGS = [
        ("escape", "exit_screen", "Exit"),
        ("d", "delete_row", "Delete Row")
    ]

    def __init__(self, columns, rows_with_keys, *args, **kwargs):
        super().__init__(*args, **kwargs, id="edit_projects_screen")
        self.my_projects_table: DataTable = DataTable(id="projects_destination")
        self.row_key = None
        self.columns = columns
        self.rows_with_keys = rows_with_keys
        self.projects_container: ScrollableContainer

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Edit Projects", classes="span-3", id="edit_projects_title")
        yield Static(" Please note you may only delete one row at a time!", classes="span-3")
        yield ScrollableContainer(id="edit_projects_container")
        yield Footer()

    async def on_mount(self):
        self.log("Edit projects screen mounted")
        self.title = "Egeria - my_profile"
        self.sub_title = "Edit Projects"
        # Populate DataTable
        self.my_projects_table.clear(columns=True)
        self.my_projects_table.add_columns(*self.columns)
        for key_str, cell_values in self.rows_with_keys:
            self.my_projects_table.add_row(*cell_values, key=key_str)

        try:
            # Access the edit projects container in the screen composition objects
            self.projects_container = self.query_one("#edit_projects_container", ScrollableContainer)
            self.log(f"Projects container found: {self.projects_container}")
            # Mount the table into the container
            await self.projects_container.mount(self.my_projects_table)
            self.log("Table mounted into container")
            # To make sure, refresh the container object on the display
            self.projects_container.refresh(layout=True)
            self.my_projects_table.refresh(layout=True)
            self.focus()
            self.call_after_refresh(self.my_projects_table.focus)
        except NoMatches as e:
            # If there is an error finding the container
            self.log(f"Edit projects container not found - Error: {e}")
            await self.dismiss(400)

    @on(DataTable.RowSelected, "#projects_destination")
    def row_selected(self, event: DataTable.RowSelected):
        """ When the user selects a row in the data table store the row key"""
        self.row_key = event.row_key

    def action_exit_screen(self):
        """ The user has requested to exit the screen, return the current table data """
        rows_with_keys = []
        for row_key in self.my_projects_table.rows:
            rows_with_keys.append((row_key.value, self.my_projects_table.get_row(row_key)))
        self.dismiss(rows_with_keys)

    def action_delete_row(self):
        """ The user has selected the delete row option """
        self.log(f"Delete row selected, row key: {self.row_key}")
        # If there is a row selected, delete it and clear the row key variable
        if self.row_key:
            self.my_projects_table.remove_row(self.row_key)
            self.my_projects_table.refresh()
            self.projects_container.refresh(layout=True)
            self.row_key = None
        # If there is no row key in the variable, inform the user by mounting a message into the container
        # and wait for any further actions.
        else:
            self.projects_container.mount(Static("Please select a row to delete prior to using the hot key!"))
            self.projects_container.refresh(layout=True)

class EditRolesScreen(ModalScreen):
    """ Screen called during editing of a users profile to allow editing of the roles
        they belong too."""

    BINDINGS = [
        ("escape", "exit_screen", "Exit"),
        ("d", "delete_row", "Delete Row")
    ]

    def __init__(self, columns, rows_with_keys, *args, **kwargs):
        super().__init__(*args, **kwargs, id="edit_roles_screen")
        self.my_roles_table: DataTable = DataTable(id="roles_destination")
        self.row_key = None
        self.columns = columns
        self.rows_with_keys = rows_with_keys
        self.roles_container: ScrollableContainer

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Edit Roles", classes="span-3", id="edit_roles_title")
        yield Static(" Please note you may only delete one row at a time!", classes="span-3")
        yield ScrollableContainer(id="edit_roles_container")
        yield Footer()

    async def on_mount(self):
        self.log("Edit roles screen mounted")
        self.title = "Egeria - my_profile"
        self.sub_title = "Edit Roles"
        # Populate DataTable
        self.my_roles_table.clear(columns=True)
        self.my_roles_table.add_columns(*self.columns)
        for key_str, cell_values in self.rows_with_keys:
            self.my_roles_table.add_row(*cell_values, key=key_str)

        try:
            # Access the edit roles container in the screen composition objects
            self.roles_container = self.query_one("#edit_roles_container", ScrollableContainer)
            self.log(f"Roles container found: {self.roles_container}")
            # Mount the table into the container
            await self.roles_container.mount(self.my_roles_table)
            self.log("Table mounted into container")
            # To make sure, refresh the container object on the display
            self.roles_container.refresh(layout=True)
            self.my_roles_table.refresh(layout=True)
            self.focus()
            self.call_after_refresh(self.my_roles_table.focus)
        except NoMatches as e:
            # If there is an error finding the container
            self.log(f"Edit roles container not found - Error: {e}")
            await self.dismiss(400)

    @on(DataTable.RowSelected, "#roles_destination")
    def row_selected(self, event: DataTable.RowSelected):
        """ When the user selects a row in the data table store the row key"""
        self.row_key = event.row_key

    def action_exit_screen(self):
        """ The user has requested to exit the screen, return the current table data """
        rows_with_keys = []
        for row_key in self.my_roles_table.rows:
            rows_with_keys.append((row_key.value, self.my_roles_table.get_row(row_key)))
        self.dismiss(rows_with_keys)

    def action_delete_row(self):
        """ The user has selected the delete row option """
        self.log(f"Delete row selected, row key: {self.row_key}")
        # If there is a row selected, delete it and clear the row key variable
        if self.row_key:
            self.my_roles_table.remove_row(self.row_key)
            self.my_roles_table.refresh()
            self.roles_container.refresh(layout=True)
            self.row_key = None
        # If there is no row key in the variable, inform the user by mounting a message into the container
        # and wait for any further actions.
        else:
            self.roles_container.mount(Static("Please select a row to delete prior to using the hot key!"))
            self.roles_container.refresh(layout=True)

class EditTeamsScreen(ModalScreen):
    """ Screen called during editing of a users profile to allow editing of the teams
        they belong too."""

    BINDINGS = [
        ("escape", "exit_screen", "Exit"),
        ("d", "delete_row", "Delete Row")
    ]

    def __init__(self, columns, rows_with_keys, *args, **kwargs):
        super().__init__(*args, **kwargs, id="edit_teams_screen")
        self.my_teams_table: DataTable = DataTable(id="teams_destination")
        self.row_key = None
        self.columns = columns
        self.rows_with_keys = rows_with_keys
        self.teams_container: ScrollableContainer

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Edit Teams", classes="span-3", id="edit_teams_title")
        yield Static(" Please note you may only delete one row at a time!", classes="span-3")
        yield ScrollableContainer(id="edit_teams_container")
        yield Footer()

    async def on_mount(self):
        self.log("Edit teams screen mounted")
        self.title = "Egeria - my_profile"
        self.sub_title = "Edit Teams"
        # Polulate DataTable
        self.my_teams_table.clear(columns=True)
        self.my_teams_table.add_columns(*self.columns)
        for key_str, cell_values in self.rows_with_keys:
            self.my_teams_table.add_row(*cell_values, key=key_str)
        try:
            # Access the edit teams container in the screen composition objects
            self.teams_container = self.query_one("#edit_teams_container", ScrollableContainer)
            self.log(f"Teams container found: {self.teams_container}")
            # Mount the table into the container
            await self.teams_container.mount(self.my_teams_table)
            self.log("Table mounted into container")
            # To make sure, refresh the container object on the display
            self.teams_container.refresh(layout=True)
            self.my_teams_table.refresh(layout=True)
            self.focus()
            self.call_after_refresh(self.my_teams_table.focus)
        except NoMatches as e:
            # If there is an error finding the container
            self.log(f"Edit teams container not found - Error: {e}")
            await self.dismiss(400)

    @on(DataTable.RowSelected, "#teams_destination")
    def row_selected(self, event: DataTable.RowSelected):
        """ When the user selects a row in the data table store the row key"""
        self.row_key = event.row_key

    def action_exit_screen(self):
        """ The user has requested to exit the screen, return the current table data """
        rows_with_keys = []
        for row_key in self.my_teams_table.rows:
            rows_with_keys.append((row_key.value, self.my_teams_table.get_row(row_key)))
        self.dismiss(rows_with_keys)

    def action_delete_row(self):
        """ The user has selected the delete row option """
        self.log(f"Delete row selected, row key: {self.row_key}")
        # If there is a row selected, delete it and clear the row key variable
        if self.row_key:
            self.my_teams_table.remove_row(self.row_key)
            self.my_teams_table.refresh()
            self.teams_container.refresh(layout=True)
            self.row_key = None
        # If there is no row key in the variable, inform the user by mounting a message into the container
        # and wait for any further actions.
        else:
            self.teams_container.mount(Static("Please select a row to delete prior to using the hot key!"))
            self.teams_container.refresh(layout=True)

class EditTodosScreen(ModalScreen):
    """ Screen called during editing of a users profile to allow editing of the todos
        they belong too."""

    BINDINGS = [
        ("escape", "exit_screen", "Exit"),
        ("d", "delete_row", "Delete Row")
    ]

    def __init__(self, columns, rows_with_keys, *args, **kwargs):
        super().__init__(*args, **kwargs, id="edit_todos_screen")
        self.my_todos_table: DataTable = DataTable(id="todos_destination")
        self.row_key = None
        self.columns = columns
        self.rows_with_keys = rows_with_keys
        self.todos_container: ScrollableContainer

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Edit Todos", classes="span-3", id="edit_todos_title")
        yield Static(" Please note you may only delete one row at a time!", classes="span-3")
        yield ScrollableContainer(id="edit_todos_container")
        yield Footer()

    async def on_mount(self):
        self.log("Edit todos screen mounted")
        self.title = "Egeria - my_profile"
        self.sub_title = "Edit Todos"
        # Populate DataTable
        self.my_todos_table.clear(columns=True)
        self.my_todos_table.add_columns(*self.columns)
        for key_str, cell_values in self.rows_with_keys:
            self.my_todos_table.add_row(*cell_values, key=key_str)

        try:
            # Access the edit todos container in the screen composition objects
            self.todos_container = self.query_one("#edit_todos_container", ScrollableContainer)
            self.log(f"Todos container found: {self.todos_container}")
            # Mount the table into the container
            await self.todos_container.mount(self.my_todos_table)
            self.log("Table mounted into container")
            # To make sure, refresh the container object on the display
            self.todos_container.refresh(layout=True)
            self.my_todos_table.refresh(layout=True)
            self.focus()
            self.call_after_refresh(self.my_todos_table.focus)
        except NoMatches as e:
            # If there is an error finding the container
            self.log(f"Edit todos container not found - Error: {e}")
            await self.dismiss(400)

    @on(DataTable.RowSelected, "#todos_destination")
    def row_selected(self, event: DataTable.RowSelected):
        """ When the user selects a row in the data table store the row key"""
        self.row_key = event.row_key

    def action_exit_screen(self):
        """ The user has requested to exit the screen, return the current table data """
        rows_with_keys = []
        for row_key in self.my_todos_table.rows:
            rows_with_keys.append((row_key.value, self.my_todos_table.get_row(row_key)))
        self.dismiss(rows_with_keys)

    def action_delete_row(self):
        """ The user has selected the delete row option """
        self.log(f"Delete row selected, row key: {self.row_key}")
        # If there is a row selected, delete it and clear the row key variable
        if self.row_key:
            self.my_todos_table.remove_row(self.row_key)
            self.my_todos_table.refresh()
            self.todos_container.refresh(layout=True)
            self.row_key = None
        # If there is no row key in the variable, inform the user by mounting a message into the container
        # and wait for any further actions.
        else:
            self.todos_container.mount(Static("Please select a row to delete prior to using the hot key!"))
            self.todos_container.refresh(layout=True)

