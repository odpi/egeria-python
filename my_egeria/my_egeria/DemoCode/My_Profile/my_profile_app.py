"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides the main entry point and core lifecycle for the My Profile Textual App.
"""

import sys
from pathlib import Path
from typing import Any
import asyncio

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
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable, OptionList, Header, Footer
from SplashScreen import SplashScreen
from CreateProfileScreen import CreateProfileScreen
from EditElementsScreens import (
    EditProfileScreen,
    EditCommunitiesScreen,
    EditIdentitiesScreen,
    EditProjectsScreen,
    EditTodosScreen,
    EditRolesScreen,
    EditTeamsScreen,
    EditBlogsScreen,
    EditJournalScreen,
    EditAssociationsScreen,
)
from TechnologyTypeScreens import (
    TechnologyTypesScreen,
    TechnologyTypeOptionsScreen,
    TechnologyTypeTemplatesScreen,
    TechnologyTypeProcessesScreen,
)
from StatusScreen import StatusScreen
from ShopForDataScreen import ShopForDataScreen
from SelectionOverviewScreen import SelectionOverviewScreen
from MyTeamScreen import MyTeam
from MainScreen import MainScreen
from SearchForTermScreen import SearchForTermScreen
from CreateSubscriptionRequestScreen import CreateSubscriptionRequestScreen
from UserIdentitiesScreen import UserIdentitiesScreen
from ShowCommentsScreen import ShowCommentsScreen
from AddToElementsScreens import (
    AddRoleScreen,
    AddProjectScreen,
    AddCommunityScreen,
    AddTeamScreen,
    AddBlogEntryScreen,
    AddJournalEntryScreen,
    AddTodoScreen,
    AddAssociationScreen,
)
from ViewSubscriptionsScreen import ViewSubscriptionsScreen
from GenericDataViewScreen import GenericDataViewScreen, DataViewScreen
from AddCommentScreen import AddCommentScreen
from profile_utils import (
    truncate_at_sequence,
    clean_structure,
    bools_to_strings,
    extract_glossary_terms,
    check_request_serialization,
    element_summary,
)
from tech_types_handler import TechTypesMixin
from shop_for_data_handler import ShopForDataMixin
from team_roles_handler import TeamRolesMixin
from elements_crud_handler import ElementsCrudMixin
from feedback_handler import FeedbackMixin, FEEDBACK_LOG_OWNER
from bookmarks_handler import BookmarksMixin, bookmarks_qualified_name
from MyBookMarksScreen import MyBookMarksScreen


class MyProfileApp(App, TechTypesMixin, ShopForDataMixin, TeamRolesMixin, ElementsCrudMixin, FeedbackMixin,
                   BookmarksMixin):
    """My Profile App.

    Retrieves a user's profile from Egeria and displays current work items.
    If no profile is found, offers a UI to create one.
    """

    # The feedback bindings are priority bindings: Textual ignores ordinary App bindings
    # while a ModalScreen is active, and most screens in this app are modal. Priority also
    # means ctrl+f wins over the Input/TextArea "delete word right" binding on the same key.
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh Data"),
        Binding("ctrl+f", "feedback", "Feedback", priority=True),
        Binding("f3", "view_feedback_log", "Feedback Log", priority=True),
    ]

    CSS_PATH = "my_profile.tcss"

    SCREENS = {
        "splash": SplashScreen,
        "main": MainScreen,
        "create_profile": CreateProfileScreen,
        "edit_profile": EditProfileScreen,
        "edit_communities": EditCommunitiesScreen,
        "edit_identities": EditIdentitiesScreen,
        "edit_roles": EditRolesScreen,
        "edit_teams": EditTeamsScreen,
        "edit_todos": EditTodosScreen,
        "edit_projects": EditProjectsScreen,
        "edit_blogs": EditBlogsScreen,
        "edit_journal": EditJournalScreen,
        "edit_associations": EditAssociationsScreen,
        "tech_types": TechnologyTypesScreen,
        "tech_type_options": TechnologyTypeOptionsScreen,
        "tech_type_templates": TechnologyTypeTemplatesScreen,
        "tech_type_processes": TechnologyTypeProcessesScreen,
        "status": StatusScreen,
        "shop_4_data": ShopForDataScreen,
        "search_for_term": SearchForTermScreen,
        "overview": SelectionOverviewScreen,
        "create_subscription": CreateSubscriptionRequestScreen,
        "my_team": MyTeam,
        "show_comments": ShowCommentsScreen,
        "add_comment": AddCommentScreen,
        "add_role": AddRoleScreen,
        "add_project": AddProjectScreen,
        "add_community": AddCommunityScreen,
        "add_team": AddTeamScreen,
        "add_blog_entry": AddBlogEntryScreen,
        "add_journal_entry": AddJournalEntryScreen,
        "add_todo": AddTodoScreen,
        "add_association": AddAssociationScreen,
        "view_subscriptions": ViewSubscriptionsScreen,
        "generic_data_view": GenericDataViewScreen,
        "data_view": DataViewScreen,
        "my_bookmarks": MyBookMarksScreen,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.contribution_record = None
        self.heading = "My_Profile"
        self.subheading = "Egeria Profile for current user"
        self.description = "Display the user related items for the current user."
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

        # Ensure compose() is safe before data loads
        self.actor_profile: dict = {}
        self.projects = []
        self.communities = []
        self.roles = []
        self.blogs = []
        self.journal = []
        self.todos = []
        self.teams = []
        self.other_function_list = []
        self.tech_type_json: str = ""
        self.tech_type_response = None
        self.tech_type_list = []
        self.tech_type_guid = ""
        self.tech_type_name = ""
        self.tech_type_description = ""
        self.selected_t_node = None
        self.selected_t_node_label = None
        self.karma_points = 0
        self.tech_type_templates = [{}]
        self.tech_type_processes = [{}]
        self.full_template = None
        self.glossary_data_extract = None
        self.business_glossary_data_extract = None
        self.display_glossary_data_extract = None
        self.digital_glossary_data_extract = None
        self.team_members: list[list] = []
        self.max_mermaid_node_count = 0  # This is to tell egeria we dont want mermaid graphs in the response packet.
        self.graph_query_depth = 0  # This tells egeria not to include relationships in the response packet
        self.user_GUID = ""
        self.user_data = {}
        self.user_identities = []
        self.user_identity = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Only show the feedback log binding to the log's owner."""
        if action == "view_feedback_log":
            return self.user_name == FEEDBACK_LOG_OWNER
        return True

    async def on_mount(self) -> None:
        """Mount the main screen, start loading profile data in parallel, and display the splash screen."""
        environment_error = check_request_serialization()
        if environment_error:
            self.exit(430, return_code=1, message=environment_error)
            return
        await self.push_screen("main")
        self._load_task = asyncio.create_task(self._load_profile_and_populate())
        await self.push_screen("splash", callback=self.mainline)

    async def mainline(self, splash_return: Any = None) -> None:
        """Process any return values from the splash screen, then
        ensure user profile is loaded and tables are populated."""
        if isinstance(splash_return, list):
            if hasattr(self, "_load_task") and not self._load_task.done():
                self._load_task.cancel()
            self.user_name = splash_return[0]
            self.user_password = splash_return[1]
            # Screens read the user from pyegeria's (cached) settings, so record the
            # switch there too, or their Egeria calls would still run as the old user
            settings.User_Profile.user_name = self.user_name
            settings.User_Profile.user_pwd = self.user_password
            self.refresh_bindings()
            await self._load_or_create_profile()
        else:
            # Splash screen finished (timeout or dismissed)
            if hasattr(self, "_load_task"):
                try:
                    profile_found = await self._load_task
                except asyncio.CancelledError:
                    return
                except Exception as e:
                    self.log(f"Error in parallel initial load: {e}")
                    profile_found = False

                if not profile_found and (not hasattr(self, "my_profile_data") or not self.my_profile_data):
                    self.log("No profile found. Prompting to create one...")
                    await self.push_screen(
                        CreateProfileScreen(
                            user=self.user_name,
                            password=self.user_password,
                            view_server=self.view_server,
                            platform_url=self.platform_url,
                        ),
                        callback=self.new_profile_return,
                    )

    async def _load_profile_and_populate(self) -> bool:
        """Retrieve the user's profile and populate UI tables in parallel.
        Returns True if profile exists and tables were populated, False if profile is missing."""
        try:
            self.my_profile_inst = MyProfile(self.view_server, self.platform_url, self.user_name, self.user_password)
            self.my_profile_inst.create_egeria_bearer_token(self.user_name, self.user_password)
            # Fetch the profile once and format it locally for each view (My-User-MD here,
            # User-Identities in _process_profile_data) instead of fetching it per view.
            self.my_profile_raw = await self.my_profile_inst._async_get_my_profile(output_format="JSON")
            self.my_profile_data = (
                self.my_profile_inst._generate_my_profile_output(
                    self.my_profile_raw, "My", "MyProfile", "DICT", "My-User-MD")
                if isinstance(self.my_profile_raw, dict) else self.my_profile_raw
            )
            self.log(f"retrieve profile result: {self.my_profile_data}")
        except PyegeriaException as e:
            self.log(f"Error retrieving profile: {e!s}")
            print_basic_exception(e)
            self.exit(402)
            return False

        if not self.my_profile_data:
            self.log("No profile found for user.")
            return False

        self._process_profile_data(self.my_profile_data)
        await self._populate_tables()
        return True

    async def _load_or_create_profile(self) -> None:
        """Load user profile; if missing, prompt to create it."""
        profile_found = await self._load_profile_and_populate()
        if not profile_found and (not hasattr(self, "my_profile_data") or not self.my_profile_data):
            self.log("No profile found. Prompting to create one...")
            await self.push_screen(
                CreateProfileScreen(
                    user=self.user_name,
                    password=self.user_password,
                    view_server=self.view_server,
                    platform_url=self.platform_url,
                ),
                callback=self.new_profile_return,
            )

    def _process_profile_data(self, profile_struct: list[dict]) -> None:
        """Parse raw profile structure and extract individual elements."""
        self.user_profile_struct = profile_struct
        # clear the target data structures.
        self.my_blogs_data = [{}]
        self.my_journal_data = [{}]

        # strip out the individual profile elements
        self.user_profile = self.user_profile_struct[0]
        self.contribution_record = self.user_profile.get("Contribution Record") or {}
        if isinstance(self.contribution_record, list) and len(self.contribution_record) > 0:
            self.karma_points = self.contribution_record[0].get("Karma Points") or 0
        elif isinstance(self.contribution_record, dict):
            self.karma_points = self.contribution_record.get("Karma Points") or 0
        else:
            self.karma_points = 0
        self.my_projects_data = self.user_profile.get("Projects") or []
        self.my_teams_data = self.user_profile.get("Teams") or []
        self.my_communities_data = self.user_profile.get("Communities") or []
        self.my_roles_data = self.user_profile.get("Roles") or []
        self.my_note_logs = self.user_profile.get("Note Logs") or []
        self.log(f"my_note_logs: {self.my_note_logs}, type: {type(self.my_note_logs)}")
        for entry in self.my_note_logs:
            if entry.get("class") == "BlogEntryProperties":
                self.my_blogs_data.append(entry)
            elif entry.get("class") == "JournalEntryProperties":
                self.my_journal_data.append(entry)
                # are todos part of note logs?

        self.log(f"Contribution Record: {self.contribution_record}")
        self.log(f"Karma Points: {self.karma_points}")
        self.log(f"my_projects_data: {self.my_projects_data}")
        self.log(f"my_teams_data: {self.my_teams_data}")
        self.log(f"my_communities_data: {self.my_communities_data}")
        self.log(f"my_roles_data: {self.my_roles_data}")
        self.log(f"my_blogs_data: {self.my_blogs_data}")
        self.log(f"my_journal_data: {self.my_journal_data}")

        # User Identities
        try:
            raw = getattr(self, "my_profile_raw", None)
            self.user_identities = (
                self.my_profile_inst._generate_my_profile_output(raw, "My", "MyProfile", "DICT", "User-Identities")
                if isinstance(raw, dict)
                else self.my_profile_inst.get_my_profile(report_spec="User-Identities", output_format="DICT")
            )
            self.log(f"User-Identities: {self.user_identities}, type: {type(self.user_identities)}")
        except PyegeriaException as e:
            self.log(f"Error retrieving User-Identities: {e!s}")
            self.user_identities = {}

        # User To-Dos
        try:
            self.my_todos_data = self.my_profile_inst.get_my_to_dos(
                report_spec="My-User-ToDos",
                graph_query_depth=0,  # the to-do table shows properties only
                output_format="DICT",
            )
            self.log(f"My To-Dos: {self.my_todos_data}, type: {type(self.my_todos_data)}")
        except PyegeriaException as e:
            self.log(f"Error retrieving My To-Dos: {e!s}")
            self.my_todos_data = {}

        self.log(f"my_todos_data: {self.my_todos_data}")

        self.my_collections = self._load_my_collections()

        # User GUID — resolve self-scoped
        self.user_GUID = ""
        if isinstance(self.user_profile, dict) and self.user_profile.get("GUID"):
            self.user_GUID = self.user_profile.get("GUID")
        else:
            try:
                actor = exec_report_spec(
                    format_set_name="Actor-Profiles",
                    output_format="DICT",
                    params={"search_string": self.user_name, "graph_query_depth": 2},
                    view_server=self.view_server,
                    view_url=self.platform_url,
                    user=self.user_name,
                    user_pass=self.user_password,
                )
            except PyegeriaException as e:
                print_basic_exception(e)
                self.log(f"Error retrieving actor profile: {e!s}")
                actor = None
            data = actor.get("data") if isinstance(actor, dict) else None
            if data:
                self.user_GUID = data[0].get("GUID") or ""
            else:
                self.log("Actor-Profiles lookup returned no data; user_GUID left unset.")
        self.log(f"User GUID retrieved: {self.user_GUID!r}")

        # Normalize expected keys
        self.full_name = self.user_profile.get("Full Name") or ""
        self.sub_title = f"{self.full_name} ({self.user_profile.get('User ID')}, Karma Points: {self.karma_points})"
        self.projects = self.my_projects_data or []
        self.communities = self.my_communities_data or []
        self.roles = self.my_roles_data or []
        self.blogs = self.my_blogs_data or []
        self.journal = self.my_journal_data or []
        self.todos = self.my_todos_data or []
        self.teams = self.my_teams_data or []
        self.log(f"Blogs data: {self.blogs}")
        self.log(f"Journal data: {self.journal}")
        self.log(f"Todos data: {self.todos}")
        if isinstance(self.user_identities, list):
            self.user_identity = self.user_identities
        else:
            self.user_identity = self.user_identities.get("User-Identities") or []

    def _load_my_collections(self) -> list[dict[str, str]]:
        """Collections created by the current user, other than their bookmarks collection."""
        eclient = None
        try:
            eclient = Egeria(view_server=self.view_server, platform_url=self.platform_url,
                             user_id=self.user_name, user_pwd=self.user_password)
            eclient.create_egeria_bearer_token(self.user_name, self.user_password)
            # Depth 0: only header/properties are summarised (~70s at the default depth 3 vs <1s).
            response = eclient.find_collections(search_string="*", output_format="JSON", graph_query_depth=0)
        except PyegeriaException as e:
            self.log(f"Error retrieving My Collections: {e!s}")
            return []
        finally:
            if eclient:
                eclient.close_session()
        bookmarks_qn = bookmarks_qualified_name(self.user_name)
        return [summary for summary in (element_summary(e) for e in (response if isinstance(response, list) else []))
                if summary.get("created_by") == self.user_name and summary.get("guid")
                and summary.get("qualified_name") != bookmarks_qn]

    def new_profile_return(self, result: int) -> None:
        """This function handles either the return from the create new profile screen or
        when the user already has a profile continue processing."""
        self.log(f"Profile creation result: {result}")
        if not result or result != 200:
            self.log(f"Profile creation cancelled/failed; return: {result}, exiting.")
            self.exit(403)
            return

        self.result = result

        # Retry after creation if necessary
        try:
            self.user_profile_struct = self.my_profile_inst.get_my_profile(
                output_format="DICT",
                report_spec="My-User-MD",
            )
            self.log(f"Profile retrieved successfully: {self.user_profile_struct}")
            self.show_main_screen()
        except PyegeriaException as e2:
            self.log(f"Error retrieving user profile: {e2!s}")
            self.exit(412)
            return

        if not self.user_profile_struct or self.user_profile_struct == []:
            self.log("Error retrieving user profile. Exiting.")
            self.exit(413)
            return

        self._process_profile_data(self.user_profile_struct)
        self._populate_tables_sync()

    def _populate_tables_sync(self) -> Any:
        """Populates tables from normalized profile data."""
        main_screen = self.get_screen("main")

        try:
            self.projects_table = main_screen.query_one("#projects_table", DataTable)
        except Exception:
            self.projects_table = None

        try:
            self.communities_table = main_screen.query_one("#communities_table", DataTable)
        except Exception:
            self.communities_table = None

        self.roles_table = main_screen.query_one("#roles_table", DataTable)
        self.blogs_table = main_screen.query_one("#blogs_table", DataTable)
        self.journal_table = main_screen.query_one("#journal_table", DataTable)
        self.todos_table = main_screen.query_one("#todos_table", DataTable)
        self.user_identity_table = main_screen.query_one("#user_identity_table", DataTable)
        self.teams_table = main_screen.query_one("#teams_table", DataTable)
        self.associations_table = main_screen.query_one("#associations_table", DataTable)
        self.my_collections_table = main_screen.query_one("#my_collections_table", DataTable)

        if self.projects_table:
            self.projects_table.clear(columns=True)
            self.projects_table.add_columns("Status or Type", "Name", "Description", "GUID")
            self.projects_table.zebra_stripes = True
            self.projects_table.cursor_type = "row"
            self.projects_table.loading = True

        if self.communities_table:
            self.communities_table.clear(columns=True)
            self.communities_table.add_columns("Assignment Type", "Community Name", "Description", "GUID")
            self.communities_table.zebra_stripes = True
            self.communities_table.cursor_type = "row"
            self.communities_table.loading = True

        self.digital_product_catalog_table: DataTable = DataTable(id="digital_product_catalog_table")
        self.digital_product_catalog_table.add_columns("Digital Product Catalog Name", "Description", "Qualified Name", "GUID")
        self.digital_product_catalog_table.cursor_type = "row"
        self.digital_product_catalog_table.zebra_stripes = True
        self.digital_product_catalog_table.loading = True

        self.roles_table.clear(columns=True)
        self.roles_table.add_columns("Role Name", "Role Type", "Description", "GUID")
        self.roles_table.zebra_stripes = True
        self.roles_table.cursor_type = "row"
        self.roles_table.loading = True

        self.teams_table.clear(columns=True)
        self.teams_table.add_columns("Assignment Type", "Team Name", "Description", "GUID")
        self.teams_table.zebra_stripes = True
        self.teams_table.cursor_type = "row"
        self.teams_table.loading = True

        self.blogs_table.clear(columns=True)
        self.blogs_table.add_columns("Blog Title", "Date", "Text", "GUID")
        self.blogs_table.zebra_stripes = True
        self.blogs_table.cursor_type = "row"
        self.blogs_table.loading = True

        self.journal_table.clear(columns=True)
        self.journal_table.add_columns("Journal Entry", "Date", "Text", "GUID")
        self.journal_table.zebra_stripes = True
        self.journal_table.cursor_type = "row"
        self.journal_table.loading = True

        self.todos_table.clear(columns=True)
        self.todos_table.add_columns("To-Do Name", "Activity Status", "Description", "GUID")
        self.todos_table.zebra_stripes = True
        self.todos_table.cursor_type = "row"
        self.todos_table.loading = True

        self.user_identity_table.clear(columns=True)
        self.user_identity_table.add_columns("Display Name", "User ID", "Distinguished Name", "GUID")
        self.user_identity_table.zebra_stripes = True
        self.user_identity_table.cursor_type = "row"
        self.user_identity_table.loading = True

        self.associations_table.clear(columns=True)
        self.associations_table.add_columns("Status or Type", "Name", "Description", "GUID")
        self.associations_table.zebra_stripes = True
        self.associations_table.cursor_type = "row"
        self.associations_table.loading = True

        self.my_collections_table.clear(columns=True)
        self.my_collections_table.add_columns("Collection Name", "Collection Description", "Collection GUID")
        self.my_collections_table.zebra_stripes = True
        self.my_collections_table.cursor_type = "row"
        for collection in getattr(self, "my_collections", []):
            self.my_collections_table.add_row(
                collection["name"], collection["description"], collection["guid"])

        # Populate rows
        if self.projects_table:
            for p in self.projects if isinstance(self.projects, list) else []:
                self.projects_table.add_row(
                    str(p.get("Project Status", "")),
                    str(p.get("Name", "")),
                    str(p.get("Description", "")),
                    str(p.get("GUID", p.get("guid", ""))),
                )
            self.projects_table.loading = False
        if self.communities_table:
            for c in self.communities if isinstance(self.communities, list) else []:
                self.communities_table.add_row(
                    str(c.get("Assignment Type", "")),
                    str(c.get("Name", "")),
                    str(c.get("Description", "")),
                    str(c.get("GUID", c.get("guid", ""))),
                )
            self.communities_table.loading = False
        for r in self.roles if isinstance(self.roles, list) else []:
            self.roles_table.add_row(
                str(r.get("Name", "")),
                str(r.get("Type", "")),
                str(r.get("Description", "")),
                str(r.get("GUID", r.get("guid", ""))),
            )
        self.roles_table.loading = False
        for t in self.teams if isinstance(self.teams, list) else []:
            self.teams_table.add_row(
                str(t.get("Assignment Type", "")),
                str(t.get("Team Name", "")),
                str(t.get("Description", "")),
                str(t.get("GUID", t.get("guid", ""))),
            )
        self.teams_table.loading = False
        for b in self.blogs if isinstance(self.blogs, list) else []:
            self.blogs_table.add_row(
                str(b.get("qualifiedName", "")),
                str(b.get("time", "")),
                str(b.get("text", "")),
                str(b.get("GUID", "")),
            )
        self.blogs_table.loading = False
        for j in self.journal if isinstance(self.journal, list) else []:
            self.journal_table.add_row(
                str(j.get("qualifiedName", "")),
                str(j.get("time", "")),
                str(j.get("text", "")),
                str(j.get("GUID", j.get("guid", ""))),
            )
        self.journal_table.loading = False
        for td in self.todos if isinstance(self.todos, list) else []:
            self.todos_table.add_row(
                str(td.get("Name", "")),
                str(td.get("Activity Status", "")),
                str(td.get("Description", "")),
                str(td.get("GUID", td.get("guid", ""))),
            )
        self.todos_table.loading = False
        for ui in self.user_identity if isinstance(self.user_identity, list) else []:
            self.user_identity_table.add_row(
                str(ui.get("Display Name", "")),
                str(ui.get("User ID", "")),
                str(ui.get("Distinguished Name", "")),
                str(ui.get("GUID", ui.get("guid", ""))),
            )
        self.user_identity_table.loading = False
        for c in self.communities if isinstance(self.communities, list) else []:
            self.associations_table.add_row(
                str(c.get("Assignment Type", "")),
                str(c.get("Name", "")),
                str(c.get("Description", "")),
                str(c.get("GUID", c.get("guid", ""))),
            )
        self.associations_table.loading = False

    async def _populate_tables(self) -> Any:
        return self._populate_tables_sync()

    def action_quit(self) -> Any:
        self.exit(200)

    async def action_refresh(self) -> None:
        self.log("Refreshing data...")
        await self._load_or_create_profile()
        await self._populate_tables()
        self.log("Data refresh completed.")

    @on(OptionList.OptionSelected, "#other_function_list")
    async def handle_option_selected(self, event: OptionList.OptionSelected) -> None:
        selected_option = event.option.prompt.strip("[] ")
        selected_option_id = event.option.id
        self.log(f"Selected option: {selected_option} ({selected_option_id})")
        if selected_option == "Technology Types":
            await self.handle_technology_types_option()
        elif selected_option == "User Identities":
            await self.push_screen(
                UserIdentitiesScreen(
                    karma_points=self.karma_points,
                    user_identities=self.user_identities,
                ),
                callback=self.user_identities_callback,
            )
        elif selected_option == "Catalogs/Shop for Data":
            await self.handle_shop_for_data_option()
        elif selected_option == "Edit Profile":
            await self.push_screen(
                EditProfileScreen(
                    karma_points=self.karma_points,
                    user_profile=self.user_profile,
                    user_GUID=self.user_GUID,
                ),
                callback=self.edit_profile_callback,
            )
        elif selected_option == "User Bookmarks":
            self.show_my_bookmarks()
        elif selected_option == "Subscriptions":
            await self.push_screen(ViewSubscriptionsScreen(), callback=self.view_subscriptions_callback)
        elif selected_option == "Leave Feedback":
            await self.action_feedback()
        elif selected_option == "Feedback Log":
            await self.action_view_feedback_log()

    def status_callback(self, status_callback_rc: Any) -> None:
        """Callback routine from the status screen: the user has read the message, so carry on."""
        self.log(f"Status screen returned: {status_callback_rc}")
        self.show_main_screen()

    @on(DataTable.RowSelected, "#roles_table")
    def _on_roles_row_selected(self, event: DataTable.RowSelected) -> None:
        """Open the team roster for a TeamLeader/TeamMember role.

        Registered here rather than on TeamRolesMixin: Textual only collects @on
        handlers from its own classes, so a decorator on the plain mixin never fires.
        """
        self.handle_roles_table_row_selection(event)

    def show_main_screen(self) -> None:
        """Show or switch back to the main screen by unwinding the screen stack."""
        self.log("Returning to main screen")
        try:
            while len(getattr(self, "screen_stack", [])) > 1 and not isinstance(getattr(self, "screen", None), MainScreen):
                self.pop_screen()
        except Exception as e:
            self.log(f"Error popping screens to return to main screen: {e}")

        try:
            if getattr(self, "is_mounted", False) and not isinstance(getattr(self, "screen", None), MainScreen):
                self.push_screen("main")
        except Exception as e:
            self.log(f"Error ensuring main screen: {e}")

    # Alias for handlers calling _show_main_screen
    _show_main_screen = show_main_screen

    def view_subscriptions_callback(self, subscriptions_callback_rc: Any) -> None:
        """Callback routine from the view subscriptions screen."""
        self.log(f"View subscriptions screen returned: {subscriptions_callback_rc}")
        self.show_main_screen()

    def get_data_product_catalog_table(self) -> int:
        """Fetch and populate digital product catalog table."""
        if not hasattr(self, "digital_product_catalog_table") or self.digital_product_catalog_table is None:
            self.digital_product_catalog_table = DataTable(id="digital_product_catalog_table")
            self.digital_product_catalog_table.add_columns("Digital Product Catalog Name", "Description", "Qualified Name", "GUID")
            self.digital_product_catalog_table.cursor_type = "row"
            self.digital_product_catalog_table.zebra_stripes = True
        else:
            self.digital_product_catalog_table.clear(columns=True)
            self.digital_product_catalog_table.add_columns("Digital Product Catalog Name", "Description", "Qualified Name", "GUID")
            self.digital_product_catalog_table.cursor_type = "row"
            self.digital_product_catalog_table.zebra_stripes = True

        try:
            self.digital_product_catalog_data = exec_report_spec(
                format_set_name="Digital-Product-Catalog",
                output_format="DICT",
                params={
                    "search_string": "*",
                    "metadata_element_subtypes": ["DigitalProduct", "DigitalProductFamily"],
                    "graph_query_depth": 0,
                },
                view_server=self.view_server,
                view_url=self.platform_url,
                user=self.user_name,
                user_pass=self.user_password,
            )
        except PyegeriaException as e:
            self.log(f"Error retrieving digital product catalog details: {e!s}")
            return 421
        self.log(f"Digital Product Catalog data returned: {self.digital_product_catalog_data}")
        self.digital_product_catalog_data_extract = self.digital_product_catalog_data.get("data") or []
        self.log(f"Digital Product Catalog data extracted: {self.digital_product_catalog_data_extract}")
        if not self.digital_product_catalog_data_extract:
            self.log(f"No digital product catalog data found for user: {self.user_name}")
            self.digital_product_catalog_table.add_row("No digital product catalogs found",
                                                       "No data returned from Egeria", "")
            if hasattr(self, "notify"):
                self.notify(f"No digital product catalogs found for user: {self.user_name}")
        else:
            for catalog_item in self.digital_product_catalog_data_extract:
                self.digital_product_catalog_table.add_row(
                    catalog_item.get("Display Name", ""),
                    catalog_item.get("Description", ""),
                    catalog_item.get("Qualified Name", ""),
                    catalog_item.get("GUID", ""),
                )
                self.digital_product_catalog_table.loading=False
        return 200

    def add_comment(self, table_name, table_row):
        self.table_name = table_name
        self.table_row = table_row
        main_screen = self.get_screen("main")
        try:
            table = main_screen.query_one("#"+self.table_name, DataTable)
            table_row = table.get_row(self.table_row)
            target_heading = "GUID"
            column_key = None
            # find the column containing the GUID
            for key, column in table.columns.items():
                if column.label.plain == target_heading:
                    self.log(f"GUID column found: {column.label.plain}")
                    column_key = key
                    break

            if column_key:
                # If GUID is found, use the row and column to get the selected row's GUID
                self.log(f"GUID found in table: row: {table_row}, column: {column_key}")
            else:
                # No GUID in table so look for Qualified Name to use instead
                target_heading = "Qualified Name"
                column_key = None
                for key, column in table.columns.items():
                    if column.label.plain == target_heading:
                        self.log(f"Qualified Name column found: {column.label.plain}")
                        column_key = key
                        break

            if column_key:
                self.log (f"Row_key is : {self.table_row}")
                self.log(f"Column key is: {column_key}")
                row_id = table.get_cell(self.table_row, column_key)
                self.log(f"Row ID is: {row_id}")
            else:
                self.notify(f"Error retrieving row from table to add comment, no GUID or Qualified Name column found", severity="error", timeout=30)
                self.log(f"Column_key is: {column_key} not valid to access Egeria")
                return (400)

            if row_id == "":
                self.log(f"Row ID is: {row_id}, not valid to access Egeria")
                return (400)

        except PyegeriaException as e:
            self.notify(f"Error retrieving row from table to add comment: {e}", severity="error", timeout=30)
            return(400)

        self.push_screen(AddCommentScreen(table_name = self.table_name,
                                            element_guid = row_id),
                                            callback = self.add_comment_callback)

    def add_comment_callback(self, comment_content):
        """ Process feedback from thew add comment functions and then return to main screen"""
        # If the return is an integer, then either success or failure, return to main screen
        self.log(f"Return from Add Comment Screen: {comment_content}")
        # An integer return is cancel/quit (200) or no element selected (400); the
        # main screen is already showing once AddCommentScreen has dismissed
        if not isinstance(comment_content, (list, tuple)):
            return
        # Check that all required data has been returned (Comment, Type, and the GUID of the element the comment applies to)
        if len(comment_content) != 3:
            self.notify("Return from Add Comment Screen incomplete, please retry", severity="error", timeout=30)
            self.log(f"Return from Add Comment Screen: {comment_content}, length: {len(comment_content)}")
            return
        # We have 3 return data items so extract them to individual variables
        self.comment = comment_content[0]
        self.type = comment_content[1]
        self.element_guid = comment_content[2]
        # Make sure we really have all the required data
        if not self.comment or not self.type or not self.element_guid:
            self.notify("A row must be selected and Both comment text and comment type are required!")
            self.log(f"One or more element missing: {comment_content}, length: {len(comment_content)}")
            return
        # We have all the required data, then try to create the Egeria client
        eclient = None
        try:
            eclient = Egeria(self.view_server,
                            self.platform_url,
                            self.user_name,
                            self.user_password)
            eclient.create_egeria_bearer_token(self.user_name, self.user_password)
        except PyegeriaException as e:
            self.log(f"Error creating Egeria client: {e}")
            self.notify(
                "Unable to connect to the Egeria Server, please check the server is running and your credentials and try again",
                timeout=10,
                severity="error")
            return
        # If we get here, we have a valid Egeria client, so try to add the comment
        try:
            # Add comment to selected element
            self.comment_type = self.type.upper()
            self.log(f"Adding comment to element: {self.element_guid}, values: {self.comment}, {self.comment_type}")
            response = eclient.add_comment_to_element(
                element_guid=self.element_guid,
                comment=self.comment,
                comment_type=self.comment_type
            )
            self.log(f"Comment successfully added! New Comment GUID: {response}")
            self.notify(f"Comment successfully added! New Comment GUID: {response}")
        except Exception as e:
            self.log(f"Failed to add comment: {e}")
            self.notify(f"Failed to add comment: {e} \n Please try again.", severity="error")
            return
        finally:
            if eclient:
                eclient.close_session()
        return(200)

    # Compatibility wrappers delegating to profile_utils
    def clean_structure(self, data: Any, target: str = "specificationMermaidGraph") -> Any:
        return clean_structure(data, target)

    def bools_to_strings(self, data: Any) -> Any:
        return bools_to_strings(data)

    def truncate_at_sequence(self, data: Any, target: str = "specificationMermaidGraph") -> tuple[Any, bool]:
        return truncate_at_sequence(data, target)

    def extract_glossary_terms(self, text: str) -> list[str]:
        return extract_glossary_terms(text)

    async def get_guid_for_qualified_name(self, qname: str) -> str:
        eclient=Egeria(
                        self.view_server,
                        self.platform_url,
                        self.user_name,
                        self.user_password,
                        )
        token = eclient.create_egeria_bearer_token(self.user_name, self.user_password)
        guid = eclient.get_guid_for_name(name=qname)
        self.log(f"GUID: {guid} returned for qualified name: {qname}")
        eclient.close_session()
        return guid

def main() -> None:
    """Entry point for the my_profile console script."""
    MyProfileApp().run()


if __name__ == "__main__":
    main()
