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


class ConfirmDeleteScreen(ModalScreen[bool]):
    """Confirmation prompt shown before an element is deleted from Egeria.

    Dismisses with True to proceed with the delete, False to cancel.
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, label: str, guid: str, context: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs, id="confirm_delete_screen")
        self.label = label
        self.guid = guid
        self.context = context

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Confirm Deletion", classes="span-3", id="confirm_delete_title")
        yield ScrollableContainer(
            Static("This will permanently delete the following element from Egeria:"),
            Static(f"  {self.label}"),
            Static(f"  GUID: {self.guid}"),
            Static(""),
            Static("This cannot be undone from this screen."),
            Horizontal(
                Button("Delete", id="confirm_delete_btn", variant="error"),
                Button("Cancel", id="cancel_delete_btn", variant="primary"),
            ),
            id="confirm_delete_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Egeria - my_profile"
        self.sub_title = f"Confirm Deletion{f' - {self.context}' if self.context else ''}"

    @on(Button.Pressed, "#confirm_delete_btn")
    def handle_confirm_button(self, event: Button.Pressed) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#cancel_delete_btn")
    def handle_cancel_button(self, event: Button.Pressed) -> None:
        self.dismiss(False)

    def action_cancel(self) -> None:
        self.dismiss(False)


class BaseEditScreen(ModalScreen):
    """Shared behaviour for every per-table edit screen.

    Subclasses declare only their identifiers; the parse/mount/add/delete logic
    lives here once. Each subclass keeps its historical attribute names
    (``my_roles_table``, ``roles_container``, ...) because the stylesheet and the
    rest of the app refer to them.

    Dismisses with the screen's rows as ``[(row_key, row_values), ...]`` so the
    caller can write them back to the corresponding table on the main screen.
    """

    #: id given to the screen itself
    SCREEN_ID: str = ""
    #: id of the DataTable this screen owns
    TABLE_ID: str = ""
    #: id of the ScrollableContainer the table is mounted into
    CONTAINER_ID: str = ""
    #: id of the title Static
    TITLE_ID: str = ""
    #: historical attribute name for the table, e.g. "my_roles_table"
    TABLE_ATTR: str = ""
    #: historical attribute name for the container, e.g. "roles_container"
    CONTAINER_ATTR: str = ""
    #: heading text, also used as the sub-title
    TITLE_TEXT: str = ""
    #: id of the originating table on the main screen, used for add/delete routing
    SOURCE_TABLE: str = ""

    BINDINGS = [
        ("escape", "exit_screen", "Exit"),
        ("a", "add_row", "Add Row"),
        ("d", "delete_row", "Delete Row"),
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, columns=None, rows_with_keys=None, *args, **kwargs):
        super().__init__(*args, **kwargs, id=self.SCREEN_ID)
        self.columns = columns or []
        self.rows_with_keys = rows_with_keys or []
        self.row_key = None
        self.table: DataTable = DataTable(id=self.TABLE_ID)
        self.table.zebra_stripes = True
        self.table.cursor_type = "row"
        self.container: ScrollableContainer | None = None
        # Keep the per-screen attribute names the stylesheet and app expect.
        if self.TABLE_ATTR:
            setattr(self, self.TABLE_ATTR, self.table)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(self.TITLE_TEXT, classes="span-3", id=self.TITLE_ID)
        yield Static(
            " Press 'a' to add a row, 'd' to delete the selected row, Esc to exit."
            " Please note you may only delete one row at a time!",
            classes="span-3",
        )
        yield ScrollableContainer(id=self.CONTAINER_ID)
        yield Footer()

    async def on_mount(self) -> None:
        self.title = "Egeria - my_profile"
        self.sub_title = self.TITLE_TEXT

        self.table.clear(columns=True)
        if self.columns:
            self.table.add_columns(*self.columns)
        for key_str, cell_values in self.rows_with_keys:
            self.table.add_row(*cell_values, key=key_str)

        try:
            self.container = self.query_one(f"#{self.CONTAINER_ID}", ScrollableContainer)
            if self.CONTAINER_ATTR:
                setattr(self, self.CONTAINER_ATTR, self.container)
            await self.container.mount(self.table)
            self.container.refresh(layout=True)
            self.table.refresh(layout=True)
            self.focus()
            self.call_after_refresh(self.table.focus)
        except NoMatches as e:
            self.log(f"Container #{self.CONTAINER_ID} not found: {e}")
            self.dismiss(400)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Remember which row the user picked."""
        self.row_key = event.row_key

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Track the cursor too, so 'd' acts on the highlighted row."""
        self.row_key = event.row_key

    def action_exit_screen(self) -> None:
        """Hand the current rows back to the caller."""
        rows_with_keys = []
        for row_key in self.table.rows:
            rows_with_keys.append((row_key.value, self.table.get_row(row_key)))
        self.dismiss(rows_with_keys)

    async def action_add_row(self) -> None:
        """Open this table's Add screen."""
        if not self.SOURCE_TABLE:
            self.notify("Adding rows is not supported for this table.", timeout=5, severity="warning")
            return
        await self.app.add_to_tables(self.SOURCE_TABLE, self.row_key)

    def _selected_guid(self) -> str | None:
        """GUID of the selected row, or None (having notified) if unusable.

        The GUID is always the last column: most tables carry four columns, but
        my_collections_table has only three.
        """
        if self.row_key is None:
            self.notify("Please select a row to delete prior to using the hot key!",
                        timeout=5, severity="warning")
            return None
        try:
            row = self.table.get_row(self.row_key)
        except Exception as e:  # row removed, or key no longer valid
            self.log(f"Could not read row {self.row_key}: {e}")
            self.notify("Could not read the selected row.", timeout=5, severity="error")
            return None

        guid = str(row[-1]).strip() if row else ""
        if not guid or guid.lower() in ("none", "null"):
            self.notify("This row has no GUID, so it cannot be deleted from Egeria.",
                        timeout=8, severity="warning")
            return None
        return guid

    def _row_label(self) -> str:
        """A human-readable name for the selected row, for the confirm prompt."""
        try:
            row = self.table.get_row(self.row_key)
        except Exception:
            return "the selected row"
        for cell in row:
            text = str(cell).strip()
            if text:
                return text
        return "the selected row"

    async def action_delete_row(self) -> None:
        """Delete the selected row's element from Egeria, after confirmation."""
        guid = self._selected_guid()
        if guid is None:
            return

        row_key = self.row_key
        label = self._row_label()

        async def on_confirm(confirmed: bool | None) -> None:
            if not confirmed:
                self.notify("Delete cancelled.", timeout=4)
                return
            deleted = await self.app.delete_element(self.SOURCE_TABLE, guid)
            if not deleted:
                # delete_element has already reported why; leave the row in place
                # so the display keeps matching Egeria.
                return
            try:
                self.table.remove_row(row_key)
            except Exception as e:
                self.log(f"Row {row_key} already gone from the display: {e}")
            self.table.refresh()
            if self.container is not None:
                self.container.refresh(layout=True)
            if self.row_key == row_key:
                self.row_key = None
            self.notify(f"Deleted {label} from Egeria.", timeout=6)

        self.push_screen(ConfirmDeleteScreen(label, guid, self.TITLE_TEXT), callback=on_confirm)


class EditAssociationsScreen(BaseEditScreen):
    """Screen called during editing of a user's profile to allow editing of the
    associations (communities and projects) the user belongs to."""

    SCREEN_ID = "edit_associations_screen"
    TABLE_ID = "associations_destination"
    CONTAINER_ID = "edit_associations_container"
    TITLE_ID = "edit_associations_title"
    TABLE_ATTR = "my_associations_table"
    CONTAINER_ATTR = "associations_container"
    TITLE_TEXT = "Edit Associations"
    SOURCE_TABLE = "associations_table"


class EditBlogsScreen(BaseEditScreen):
    """Screen called during editing of a user's profile to allow editing of the
    blog entries the user has written."""

    SCREEN_ID = "edit_blogs_screen"
    TABLE_ID = "blogs_destination"
    CONTAINER_ID = "edit_blogs_container"
    TITLE_ID = "edit_blogs_title"
    TABLE_ATTR = "my_blogs_table"
    CONTAINER_ATTR = "blogs_container"
    TITLE_TEXT = "Edit Blogs"
    SOURCE_TABLE = "blogs_table"


class EditCollectionsScreen(BaseEditScreen):
    """Screen called during editing of a user's profile to allow editing of the
    collections the user owns."""

    SCREEN_ID = "edit_collections_screen"
    TABLE_ID = "collections_destination"
    CONTAINER_ID = "edit_collections_container"
    TITLE_ID = "edit_collections_title"
    TABLE_ATTR = "my_collections_table"
    CONTAINER_ATTR = "collections_container"
    TITLE_TEXT = "Edit Collections"
    SOURCE_TABLE = "my_collections_table"


class EditCommunitiesScreen(BaseEditScreen):
    """Screen called during editing of a user's profile to allow editing of the
    communities the user belongs to."""

    SCREEN_ID = "edit_communities_screen"
    TABLE_ID = "communities_destination"
    CONTAINER_ID = "edit_communities_container"
    TITLE_ID = "edit_communities_title"
    TABLE_ATTR = "my_communities_table"
    CONTAINER_ATTR = "communities_container"
    TITLE_TEXT = "Edit Communities"
    SOURCE_TABLE = "communities_table"


class EditIdentitiesScreen(BaseEditScreen):
    """Screen called during editing of a user's profile to allow editing of the
    user identities associated with the profile."""

    SCREEN_ID = "edit_identities_screen"
    TABLE_ID = "identities_destination"
    CONTAINER_ID = "edit_identities_container"
    TITLE_ID = "edit_identities_title"
    TABLE_ATTR = "my_identities_table"
    CONTAINER_ATTR = "identities_container"
    TITLE_TEXT = "Edit Identities"
    SOURCE_TABLE = "user_identity_table"


class EditJournalScreen(BaseEditScreen):
    """Screen called during editing of a user's profile to allow editing of the
    journal entries the user has written."""

    SCREEN_ID = "edit_journal_screen"
    TABLE_ID = "journal_destination"
    CONTAINER_ID = "edit_journal_container"
    TITLE_ID = "edit_journal_title"
    TABLE_ATTR = "my_journal_table"
    CONTAINER_ATTR = "journal_container"
    TITLE_TEXT = "Edit Journal"
    SOURCE_TABLE = "journal_table"


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
        #base code from which tyo build
        # ========================================================
        # token = client.create_egeria_bearer_token()  # uses env vars; or pass (user, password) explicitly
        #
        # try:
        #     # --- API call ---
        #
        #     community_guid_to_update = "YOUR_COMMUNITY_GUID_TO_UPDATE"
        #
        #     body_for_community_update = {
        #         'class': 'UpdateElementRequestBody',
        #         'properties': {
        #             'displayName': 'New display name for the updated community',  # Update this
        #             'description': 'Updated description of the community'  # Update this
        #         }
        #     }
        #
        #     client.update_community(community_guid_to_update, body_for_community_update)
        #
        # except PyegeriaException as e:
        #     print_basic_exception(e)
        # finally:
        #     client.close_session()
        # ========================================================
        self.dismiss("community")

    def action_Edit_identities(self) -> str:
        self.dismiss("identity")

    def action_Edit_roles(self) -> str:
        self.dismiss("role")

    def action_Edit_teams(self) -> str:
        self.dismiss("team")


class EditProjectsScreen(BaseEditScreen):
    """Screen called during editing of a user's profile to allow editing of the
    projects the user belongs to."""

    SCREEN_ID = "edit_projects_screen"
    TABLE_ID = "projects_destination"
    CONTAINER_ID = "edit_projects_container"
    TITLE_ID = "edit_projects_title"
    TABLE_ATTR = "my_projects_table"
    CONTAINER_ATTR = "projects_container"
    TITLE_TEXT = "Edit Projects"
    SOURCE_TABLE = "projects_table"


class EditRolesScreen(BaseEditScreen):
    """Screen called during editing of a user's profile to allow editing of the
    roles the user holds."""

    SCREEN_ID = "edit_roles_screen"
    TABLE_ID = "roles_destination"
    CONTAINER_ID = "edit_roles_container"
    TITLE_ID = "edit_roles_title"
    TABLE_ATTR = "my_roles_table"
    CONTAINER_ATTR = "roles_container"
    TITLE_TEXT = "Edit Roles"
    SOURCE_TABLE = "roles_table"


class EditTeamsScreen(BaseEditScreen):
    """Screen called during editing of a user's profile to allow editing of the
    teams the user belongs to."""

    SCREEN_ID = "edit_teams_screen"
    TABLE_ID = "teams_destination"
    CONTAINER_ID = "edit_teams_container"
    TITLE_ID = "edit_teams_title"
    TABLE_ATTR = "my_teams_table"
    CONTAINER_ATTR = "teams_container"
    TITLE_TEXT = "Edit Teams"
    SOURCE_TABLE = "teams_table"


class EditTodosScreen(BaseEditScreen):
    """Screen called during editing of a user's profile to allow editing of the
    to-dos assigned to the user."""

    SCREEN_ID = "edit_todos_screen"
    TABLE_ID = "todos_destination"
    CONTAINER_ID = "edit_todos_container"
    TITLE_ID = "edit_todos_title"
    TABLE_ATTR = "my_todos_table"
    CONTAINER_ATTR = "todos_container"
    TITLE_TEXT = "Edit Todos"
    SOURCE_TABLE = "todos_table"
