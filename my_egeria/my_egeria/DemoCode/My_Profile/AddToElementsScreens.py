"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides the screens that add elements (todos, blog and journal entries, projects,
   communities, roles, teams, collections and user identities) to Egeria for My Profile.

"""

from datetime import datetime

from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Static, Footer, Input, Button, Switch

from pyegeria import Egeria, PyegeriaException, load_app_config, settings, print_basic_exception


class BaseAddScreen(ModalScreen):
    """Shared plumbing for the screens that add one element at a time to Egeria.

    A subclass describes its form with the class attributes below and implements
    create_element(). If LINK_LABEL is set the form shows a "link to my profile"
    switch, and link_element() is called after a successful create.

    The screen stays open after an add so the user can add several elements in
    a row; Quit dismisses it with 200.
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+a", "add_element", "Add"),
        ]

    CSS_PATH = "my_profile.tcss"

    SCREEN_ID = ""
    ELEMENT_NAME = ""  # e.g. "Collection" - used for the title, button and messages
    INTRO_TEXT = ""
    # (input id, label, required)
    FIELDS: list[tuple[str, str, bool]] = []
    # Label for the "link to my profile" switch; None means the form has no switch
    LINK_LABEL: str | None = None

    def __init__(self, selected_table, user_GUID, *args, **kwargs):
        super().__init__(id=self.SCREEN_ID, *args, **kwargs)
        self.selected_table = selected_table
        self.user_guid = user_GUID
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"
        self.link_to_profile = self.LINK_LABEL is not None
        self.created_guids: list[str] = []

    def compose(self) -> ComposeResult:
        yield Static(f"Add {self.ELEMENT_NAME} Screen")
        widgets = [Static(
            f"{self.INTRO_TEXT}"
            f"Please fill in all required (*) fields before clicking 'Add {self.ELEMENT_NAME}'\n"
            "For bulk additions please use Dr_Egeria instead.\n"
            "Once additions are complete Quit and use the Refresh hot key on the main screen to update the display.")]
        for field_id, label, required in self.FIELDS:
            widgets.append(Static(f"{label}{' *' if required else ''}"))
            widgets.append(Input(placeholder=label, id=field_id))
        if self.LINK_LABEL is not None:
            widgets.append(Horizontal(
                Static(self.LINK_LABEL),
                Switch(value=True, id="link_to_profile"),
                ))
        widgets.append(Horizontal(
            Button(f"Add {self.ELEMENT_NAME}", id="add_button", variant="primary"),
            Button("Quit", id="quit_button", variant="warning"),
            ))
        yield ScrollableContainer(*widgets, id="add_input_container")
        yield Footer()

    def validate(self, values: dict[str, str]) -> str | None:
        """Return an error message if the (non-empty) form values are unacceptable."""
        return None

    def create_element(self, client: Egeria, values: dict[str, str]) -> str:
        """Create the element in Egeria from the form values and return its GUID."""
        raise NotImplementedError

    def link_element(self, client: Egeria, guid: str) -> None:
        """Link the newly created element to the user's profile.

        The form values used for the create are available as self.last_values.
        """
        raise NotImplementedError

    def _read_values(self) -> dict[str, str]:
        return {field_id: self.query_one(f"#{field_id}", Input).value.strip()
                for field_id, _, _ in self.FIELDS}

    def _clear_inputs(self) -> None:
        for field_id, _, _ in self.FIELDS:
            self.query_one(f"#{field_id}", Input).clear()

    def action_add_element(self) -> None:
        """Validate the form, then create (and optionally link) the element in Egeria."""
        values = self._read_values()
        missing = [label for field_id, label, required in self.FIELDS if required and not values[field_id]]
        if missing:
            self.notify(f"Please enter: {', '.join(missing)}", timeout=10, severity="error")
            return
        problem = self.validate(values)
        if problem:
            self.notify(problem, timeout=10, severity="error")
            return
        self.last_values = values

        client = Egeria(
            view_server=self.view_server,
            platform_url=self.platform_url,
            user_id=self.user_name,
            user_pwd=self.user_password
            )
        try:
            client.create_egeria_bearer_token(self.user_name, self.user_password)
            guid = self.create_element(client, values)
            self.created_guids.append(guid)
            self.log(f"Created {self.ELEMENT_NAME}: {guid}")
            self.notify(f"Created {self.ELEMENT_NAME}: {guid}", timeout=10, severity="information")
            if self.link_to_profile:
                if not self.user_guid:
                    self.notify(f"{self.ELEMENT_NAME} not linked: your profile GUID is unknown",
                                timeout=10, severity="warning")
                else:
                    try:
                        self.link_element(client, guid)
                        self.notify(f"Linked {self.ELEMENT_NAME} to your profile", timeout=10,
                                    severity="information")
                    except PyegeriaException as e:
                        print_basic_exception(e)
                        self.notify(f"Link {self.ELEMENT_NAME} to profile failed with return: {e}",
                                    timeout=10, severity="error")
            # Only clear the form on success, so a failed add can be corrected and retried
            self._clear_inputs()
        except PyegeriaException as e:
            print_basic_exception(e)
            self.notify(f"Add {self.ELEMENT_NAME} failed with return: {e}", timeout=10, severity="error")
        finally:
            client.close_session()

    @on(Switch.Changed, "#link_to_profile")
    def handle_link_to_profile_changed(self, event: Switch.Changed):
        self.link_to_profile = event.switch.value

    def action_quit(self):
        self.dismiss(200)

    @on(Button.Pressed, "#add_button")
    def handle_add_button(self, event: Button.Pressed):
        """ Handle the add button press """
        self.action_add_element()

    @on(Button.Pressed, "#quit_button")
    def handle_quit_button(self, event: Button.Pressed):
        """ Handle the quit button press """
        self.action_quit()


class AddTodoScreen(BaseAddScreen):
    """Add a To-Do for the current user."""

    SCREEN_ID = "add_todo_screen"
    ELEMENT_NAME = "Todo"
    INTRO_TEXT = ("This screen is intended for the user who wants to add a small number of Todos\n"
                  "Status will be automatically set to 'REQUESTED'\n")
    FIELDS = [
        ("todo_name", "Name of Todo", True),
        ("todo_description", "Description of Todo", True),
        ("todo_priority", "Priority of Todo (a whole number, default 0)", False),
        ]

    def validate(self, values: dict[str, str]) -> str | None:
        if values["todo_priority"] and not values["todo_priority"].isdigit():
            return "Priority must be a whole number"
        return None

    def create_element(self, client: Egeria, values: dict[str, str]) -> str:
        return client.create_my_todo(
            todo_name=values["todo_name"],
            description=values["todo_description"],
            priority=int(values["todo_priority"] or 0),
            activity_status="REQUESTED",
            )


class AddAssociationScreen(ModalScreen):
    """Ask whether the new association is a Project or a Community.

    Dismisses with "project" or "community"; the app's add_association_callback then
    opens AddProjectScreen or AddCommunityScreen. Quit dismisses with 200.
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, selected_table, user_GUID, *args, **kwargs):
        super().__init__(id="add_association_screen", *args, **kwargs)
        self.selected_table = selected_table
        self.user_guid = user_GUID

    def compose(self) -> ComposeResult:
        yield Static("Add Association Screen")
        yield ScrollableContainer(
            Static("Which kind of association do you want to add?"),
            Horizontal(
                Button("Project", id="choose_project_button", variant="primary"),
                Button("Community", id="choose_community_button", variant="primary"),
                Button("Quit", id="quit_button", variant="warning"),
                ),
            id="element_type_input",
            )
        yield Footer()

    def action_quit(self):
        self.dismiss(200)

    @on(Button.Pressed, "#choose_project_button")
    def handle_choose_project(self, event: Button.Pressed):
        self.dismiss("project")

    @on(Button.Pressed, "#choose_community_button")
    def handle_choose_community(self, event: Button.Pressed):
        self.dismiss("community")

    @on(Button.Pressed, "#quit_button")
    def handle_quit_button(self, event: Button.Pressed):
        """ Handle the quit button press """
        self.action_quit()


class AddBlogEntryScreen(BaseAddScreen):
    """Add an entry to the current user's blog."""

    SCREEN_ID = "add_blog_screen"
    ELEMENT_NAME = "Blog Entry"
    INTRO_TEXT = "This screen is intended for the user who wants to add a small number of blog entries\n"
    FIELDS = [
        ("blog_entry_name", "Name of Blog Entry", True),
        ("blog_entry_text", "Text of Entry", True),
        ("blog_entry_situation", "Situation", False),
        ]

    def create_element(self, client: Egeria, values: dict[str, str]) -> str:
        name = values["blog_entry_name"]
        body = {
            "class": "NewAttachmentRequestBody",
            "properties": {
                "class": "BlogEntryProperties",
                "typeName": "BlogEntry",
                "qualifiedName": client.make_feedback_qn("Blog", self.user_name, name),
                "displayName": name,
                "situation": values["blog_entry_situation"] or None,
                "description": values["blog_entry_text"],
                }
            }
        # blog_my_activity attaches the entry to the user's own blog
        return client.blog_my_activity(body=body)


class AddCommunityScreen(BaseAddScreen):
    """Add a new Community to Egeria."""

    SCREEN_ID = "add_community_screen"
    ELEMENT_NAME = "Community"
    INTRO_TEXT = "This screen is intended for the user who wants to add a small number of Communities\n"
    FIELDS = [
        ("community_display_name", "Name of Community", True),
        ("community_description", "Description of Community", True),
        ]

    def create_element(self, client: Egeria, values: dict[str, str]) -> str:
        name = values["community_display_name"]
        body = {
            "class": "NewElementRequestBody",
            "isOwnAnchor": True,
            "properties": {
                "class": "CommunityProperties",
                "typeName": "Community",
                "qualifiedName": client.__create_qualified_name__("Community", name),
                "displayName": name,
                "description": values["community_description"],
                }
            }
        return client.create_community(body=body)


class AddJournalEntryScreen(BaseAddScreen):
    """Add an entry to the current user's journal."""

    SCREEN_ID = "add_journal_entry_screen"
    ELEMENT_NAME = "Journal Entry"
    INTRO_TEXT = ""
    FIELDS = [
        ("journal_entry_title", "Title of Entry", True),
        ("journal_entry_text", "Text of Entry", True),
        ("journal_entry_situation", "Situation of Entry", False),
        ]

    def create_element(self, client: Egeria, values: dict[str, str]) -> str:
        title = values["journal_entry_title"]
        body = {
            "class": "NewAttachmentRequestBody",
            "properties": {
                "class": "JournalEntryProperties",
                "qualifiedName": client.make_feedback_qn("Journal", self.user_name, title),
                "displayName": title,
                "situation": values["journal_entry_situation"] or None,
                "description": values["journal_entry_text"],
                }
            }
        # journal_my_activity attaches the entry to the user's own journal
        return client.journal_my_activity(body=body)


PROJECT_CLASSIFICATIONS = ["Project", "Campaign", "StudyProject", "Task", "PersonalProject"]


class AddProjectScreen(BaseAddScreen):
    """Add a new Project to Egeria, optionally adding the user to its team."""

    SCREEN_ID = "add_project_screen"
    ELEMENT_NAME = "Project"
    INTRO_TEXT = "This screen is intended for the user who wants to add a small number of Projects\n"
    FIELDS = [
        ("project_name", "Name of Project", True),
        ("project_description", "Description of Project", True),
        ("project_classification", f"Kind of project: {', '.join(PROJECT_CLASSIFICATIONS)} (default Project)", False),
        ("project_identifier", "Project Identifier", False),
        ("project_start_date", "Start Date (YYYY-MM-DD)", False),
        ("project_end_date", "Planned End Date (YYYY-MM-DD)", False),
        ]
    LINK_LABEL = "Add yourself to the project team? Default = True"

    def validate(self, values: dict[str, str]) -> str | None:
        kind = values["project_classification"]
        if kind and kind not in PROJECT_CLASSIFICATIONS:
            return f"Kind of project must be one of: {', '.join(PROJECT_CLASSIFICATIONS)}"
        for field_id in ("project_start_date", "project_end_date"):
            if values[field_id]:
                try:
                    datetime.strptime(values[field_id], "%Y-%m-%d")
                except ValueError:
                    return "Dates must be in the form YYYY-MM-DD"
        return None

    def create_element(self, client: Egeria, values: dict[str, str]) -> str:
        return client.create_project(
            display_name=values["project_name"],
            description=values["project_description"],
            classification_name=values["project_classification"] or "Project",
            identifier=values["project_identifier"] or None,
            is_own_anchor=True,
            start_date=values["project_start_date"] or None,
            planned_end_date=values["project_end_date"] or None,
            )

    def link_element(self, client: Egeria, guid: str) -> None:
        client.add_to_project_team(project_guid=guid, actor_guid=self.user_guid)


class AddRoleScreen(BaseAddScreen):
    """Add a new Person Role to Egeria, optionally appointing the user to it."""

    SCREEN_ID = "add_role_screen"
    ELEMENT_NAME = "Role"
    INTRO_TEXT = "This screen is intended for the user who wants to add a small number of Roles\n"
    FIELDS = [
        ("role_name", "Name of Role", True),
        ("role_description", "Description of Role", True),
        ]
    LINK_LABEL = "Appoint yourself to this role? Default = True"

    def create_element(self, client: Egeria, values: dict[str, str]) -> str:
        name = values["role_name"]
        body = {
            "class": "NewElementRequestBody",
            "isOwnAnchor": True,
            "properties": {
                "class": "PersonRoleProperties",
                "typeName": "PersonRole",
                "qualifiedName": client.__create_qualified_name__("PersonRole", name),
                "displayName": name,
                "description": values["role_description"],
                }
            }
        return client.create_actor_role(body=body)

    def link_element(self, client: Egeria, guid: str) -> None:
        client.link_person_role_to_profile(person_role_guid=guid, person_profile_guid=self.user_guid)


class AddTeamScreen(BaseAddScreen):
    """Add a new Team to Egeria, optionally making the user a member of it."""

    SCREEN_ID = "add_team_screen"
    ELEMENT_NAME = "Team"
    INTRO_TEXT = "This screen is intended for the user who wants to add a small number of new Teams\n"
    FIELDS = [
        ("team_name", "Name of Team", True),
        ("team_description", "Description of Team", True),
        ]
    LINK_LABEL = "Join this team as a member? Default = True"

    def create_element(self, client: Egeria, values: dict[str, str]) -> str:
        name = values["team_name"]
        # A Team is an actor profile in Egeria
        body = {
            "class": "NewElementRequestBody",
            "isOwnAnchor": True,
            "properties": {
                "class": "TeamProperties",
                "typeName": "Team",
                "qualifiedName": client.__create_qualified_name__("Team", name),
                "displayName": name,
                "description": values["team_description"],
                }
            }
        return client.create_actor_profile(body=body)

    def link_element(self, client: Egeria, guid: str) -> None:
        # Team membership in Egeria: a TeamMember role (a PersonRole subtype), appointed
        # to the person and scoped to the team by an AssignmentScope relationship
        team_name = self.last_values["team_name"]
        role_body = {
            "class": "NewElementRequestBody",
            "isOwnAnchor": True,
            "properties": {
                "class": "PersonRoleProperties",
                "typeName": "TeamMember",
                "qualifiedName": client.__create_qualified_name__("TeamMember", f"{team_name}-{self.user_name}"),
                "displayName": f"Member of {team_name}",
                "description": f"{self.user_name}'s membership of team {team_name}",
                }
            }
        role_guid = client.create_actor_role(body=role_body)
        client.link_person_role_to_profile(person_role_guid=role_guid, person_profile_guid=self.user_guid)
        client.link_assignment_scope(scope_element_guid=guid, actor_guid=role_guid)

class AddCollectionScreen(BaseAddScreen):
    """ Add a new Collection to Egeria"""

    SCREEN_ID = "add_collection_screen"
    ELEMENT_NAME = "Collection"
    INTRO_TEXT = "This screen is intended for the user who wants to add a small number of Collections\n"
    FIELDS = [
        ("collection_name", "Name of Collection", True),
        ("collection_description", "Description of Collection", True),
        ("collection_category", "Category of Collection", False),
        ]

    def create_element(self, client: Egeria, values: dict[str, str]) -> str:
        # With no body, create_collection builds a self-anchored collection and its qualified name
        return client.create_collection(
            display_name=values["collection_name"],
            description=values["collection_description"],
            category=values["collection_category"] or None,
            )


class AddUserIdentityScreen(BaseAddScreen):
    """ Add a new User Identity to Egeria"""

    SCREEN_ID = "add_user_identity_screen"
    ELEMENT_NAME = "User Identity"
    INTRO_TEXT = "This screen is intended for the user who wants to add a small number of User Identities\n"
    FIELDS = [
        ("user_identity_user_id", "User ID", True),
        ("user_identity_display_name", "Display Name", False),
        ("user_identity_distinguished_name", "Distinguished Name", False),
        ]
    LINK_LABEL = "Link User Identity to your profile? True or False, Default = True"

    def create_element(self, client: Egeria, values: dict[str, str]) -> str:
        user_id = values["user_identity_user_id"]
        body = {
            "class": "NewElementRequestBody",
            "isOwnAnchor": True,
            "properties": {
                "class": "UserIdentityProperties",
                "typeName": "UserIdentity",
                "qualifiedName": client.__create_qualified_name__("UserIdentity", user_id),
                "displayName": values["user_identity_display_name"] or user_id,
                "userId": user_id,
                "distinguishedName": values["user_identity_distinguished_name"] or None,
                }
            }
        return client.create_user_identity(body=body)

    def link_element(self, client: Egeria, guid: str) -> None:
        client.link_identity_to_profile(user_identity_guid=guid, actor_profile_guid=self.user_guid)

