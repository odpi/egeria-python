"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides the main entry point and core lifecycle for the My Profile Textual App.
"""

import sys
from pathlib import Path
from typing import Any

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
from textual.widgets import DataTable, OptionList, Header, Footer

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

from profile_utils import (
    truncate_at_sequence,
    clean_structure,
    bools_to_strings,
    extract_glossary_terms,
)
from tech_types_handler import TechTypesMixin
from shop_for_data_handler import ShopForDataMixin
from team_roles_handler import TeamRolesMixin
from elements_crud_handler import ElementsCrudMixin


class MyProfileApp(App, TechTypesMixin, ShopForDataMixin, TeamRolesMixin, ElementsCrudMixin):
    """My Profile App.

    Retrieves a user's profile from Egeria and displays current work items.
    If no profile is found, offers a UI to create one.
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh Data"),
    ]

    CSS_PATH = "my_profile.tcss"

    SCREENS = {
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
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.contribution_record = None
        self.heading = "My_Profile"
        self.subheading = "Egeria Profile for current user"
        self.description = "Display the user related items for the current user."
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        print("Platform:", app_config.egeria_platform_url)
        print("View Server:", app_config.egeria_view_server)
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"

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
        self.graph_query_depth = 0  # This tell egeria not to include relationships in the response packet
        self.user_GUID = ""
        self.user_data = {}
        self.user_identities = []
        self.user_identity = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    async def on_mount(self) -> None:
        """Load profile; if missing, prompt to create it; then populate tables."""
        await self.push_screen("main")
        await self._load_or_create_profile()
        await self._populate_tables()

    async def _load_or_create_profile(self) -> None:
        try:
            self.my_profile_inst = MyProfile(self.view_server, self.platform_url, self.user_name, self.user_password)
            self.my_profile_inst.create_egeria_bearer_token(self.user_name, self.user_password)
            self.my_profile_data = await self.my_profile_inst._async_get_my_profile(
                report_spec="My-User-MD",
                output_format="DICT",
            )
            self.log(f"retrieve profile result: {self.my_profile_data}")
        except PyegeriaException as e:
            self.log(f"Error retrieving profile: {e!s}")
            print_basic_exception(e)
            self.exit(402)
            return

        if self.my_profile_data == []:
            self.log("Error retrieving profile. Prompting to create one...")
            self.log("To create a profile you must have a valid userid in the system, please contact your system administrator to create one if needed")
            await self.push_screen(
                CreateProfileScreen(),
                callback=self.new_profile_return,
            )
        else:
            self.new_profile_return(200)

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
            self.user_identities = self.my_profile_inst.get_my_profile(
                report_spec="User-Identities",
                output_format="DICT",
            )
            self.log(f"User-Identities: {self.user_identities}, type: {type(self.user_identities)}")
        except PyegeriaException as e:
            self.log(f"Error retrieving User-Identities: {e!s}")
            self.user_identities = {}

        # User To-Dos
        try:
            self.my_todos_data = self.my_profile_inst.get_my_to_dos(
                report_spec="My-User-ToDos",
                output_format="DICT",
            )
            self.log(f"My To-Dos: {self.my_todos_data}, type: {type(self.my_todos_data)}")
        except PyegeriaException as e:
            self.log(f"Error retrieving My To-Dos: {e!s}")
            self.my_todos_data = {}

        self.log(f"my_todos_data: {self.my_todos_data}")

        # User GUID — resolve self-scoped
        self.user_GUID = ""
        if isinstance(self.user_profile, dict) and self.user_profile.get("GUID"):
            self.user_GUID = self.user_profile.get("GUID")
        else:
            try:
                actor = exec_report_spec(
                    format_set_name="Actor-Profiles",
                    output_format="DICT",
                    params={"search_string": self.user_name},
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

    async def _populate_tables(self) -> Any:
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

        if self.communities_table:
            self.communities_table.clear(columns=True)
            self.communities_table.add_columns("Assignment Type", "Community Name", "Description", "GUID")
            self.communities_table.zebra_stripes = True
            self.communities_table.cursor_type = "row"

        self.digital_product_catalog_table: DataTable = DataTable(id="digital_product_catalog_table")
        self.digital_product_catalog_table.add_columns("Digital Product Catalog Name", "Description", "Qualified Name")
        self.digital_product_catalog_table.cursor_type = "row"
        self.digital_product_catalog_table.zebra_stripes = True

        self.roles_table.clear(columns=True)
        self.roles_table.add_columns("Role Name", "Role Type", "Description", "GUID")
        self.roles_table.zebra_stripes = True
        self.roles_table.cursor_type = "row"

        self.teams_table.clear(columns=True)
        self.teams_table.add_columns("Assignment Type", "Team Name", "Description", "GUID")
        self.teams_table.zebra_stripes = True
        self.teams_table.cursor_type = "row"

        self.blogs_table.clear(columns=True)
        self.blogs_table.add_columns("Blog Title", "Date", "Text", "GUID")
        self.blogs_table.zebra_stripes = True
        self.blogs_table.cursor_type = "row"
        # for b in self.blogs if isinstance(self.blogs, list) else []:
        #     if b != "":
        #         temp_qname = b.get("qualifiedName", "")
        #         temp_guid = await self.get_guid_for_qualified_name(temp_qname), ""
        #         b.update("GUID", temp_guid)
        #         self.log(f"GUID: {temp_guid}, retrieved for {temp_qname}")

        self.journal_table.clear(columns=True)
        self.journal_table.add_columns("Journal Entry", "Date", "Text", "GUID")
        self.journal_table.zebra_stripes = True
        self.journal_table.cursor_type = "row"

        self.todos_table.clear(columns=True)
        self.todos_table.add_columns("To-Do Name", "Activity Status", "Description", "GUID")
        self.todos_table.zebra_stripes = True
        self.todos_table.cursor_type = "row"

        self.user_identity_table.clear(columns=True)
        self.user_identity_table.add_columns("Display Name", "User ID", "Distinguished Name", "GUID")
        self.user_identity_table.zebra_stripes = True
        self.user_identity_table.cursor_type = "row"

        self.associations_table.clear(columns=True)
        self.associations_table.add_columns("Status or Type", "Name", "Description", "GUID")
        self.associations_table.zebra_stripes = True
        self.associations_table.cursor_type = "row"

        self.my_collections_table.clear(columns=True)
        self.my_collections_table.add_columns("Collection Name", "Collection Description", "Collection GUID")
        self.my_collections_table.zebra_stripes = True
        self.my_collections_table.cursor_type = "row"

        # Populate rows
        if self.projects_table:
            for p in self.projects if isinstance(self.projects, list) else []:
                self.projects_table.add_row(
                    str(p.get("Project Status", "")),
                    str(p.get("Name", "")),
                    str(p.get("Description", "")),
                    str(p.get("GUID", p.get("guid", ""))),
                )
        if self.communities_table:
            for c in self.communities if isinstance(self.communities, list) else []:
                self.communities_table.add_row(
                    str(c.get("Assignment Type", "")),
                    str(c.get("Name", "")),
                    str(c.get("Description", "")),
                    str(c.get("GUID", c.get("guid", ""))),
                )
        for r in self.roles if isinstance(self.roles, list) else []:
            self.roles_table.add_row(
                str(r.get("Name", "")),
                str(r.get("Type", "")),
                str(r.get("Description", "")),
                str(r.get("GUID", r.get("guid", ""))),
            )
        for t in self.teams if isinstance(self.teams, list) else []:
            self.teams_table.add_row(
                str(t.get("Assignment Type", "")),
                str(t.get("Team Name", "")),
                str(t.get("Description", "")),
                str(t.get("GUID", t.get("guid", ""))),
            )
        for b in self.blogs if isinstance(self.blogs, list) else []:
                self.blogs_table.add_row(
                    str(b.get("qualifiedName", "")),
                    str(b.get("time", "")),
                    str(b.get("text", "")),
                    str(b.get("GUID", "")),
                    )
        for j in self.journal if isinstance(self.journal, list) else []:
            self.journal_table.add_row(
                str(j.get("qualifiedName", "")),
                str(j.get("time", "")),
                str(j.get("text", "")),
                str(j.get("GUID", j.get("guid", ""))),
            )
        for td in self.todos if isinstance(self.todos, list) else []:
            self.todos_table.add_row(
                str(td.get("Name", "")),
                str(td.get("Activity Status", "")),
                str(td.get("Description", "")),
                str(td.get("GUID", td.get("guid", ""))),
            )
        for ui in self.user_identity if isinstance(self.user_identity, list) else []:
            self.user_identity_table.add_row(
                str(ui.get("Display Name", "")),
                str(ui.get("User ID", "")),
                str(ui.get("Distinguished Name", "")),
                str(ui.get("GUID", ui.get("guid", ""))),
            )
        for c in self.communities if isinstance(self.communities, list) else []:
            self.associations_table.add_row(
                str(c.get("Assignment Type", "")),
                str(c.get("Name", "")),
                str(c.get("Description", "")),
                str(c.get("GUID", c.get("guid", ""))),
            )

    def action_quit(self) -> Any:
        self.exit(200)

    async def action_refresh(self) -> None:
        self.log("Refreshing data...")
        await self._load_or_create_profile()
        await self._populate_tables()
        self.log("Data refresh completed.")

    @on(OptionList.OptionSelected, "#other_function_list")
    async def handle_option_selected(self, event: OptionList.OptionSelected) -> None:
        selected_option = event.option.prompt
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
            pass
        elif selected_option == "Subscriptions":
            await self.push_screen(ViewSubscriptionsScreen(), callback=self.view_subscriptions_callback)

    def status_callback(self, status_callback_rc: Any) -> None:
        """Callback routine from the status screen."""
        self.log(f"Status screen returned: {status_callback_rc}")
        self.exit(status_callback_rc)

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
            self.digital_product_catalog_table.add_columns("Digital Product Catalog Name", "Description", "Qualified Name")
            self.digital_product_catalog_table.cursor_type = "row"
            self.digital_product_catalog_table.zebra_stripes = True
        else:
            self.digital_product_catalog_table.clear(columns=True)
            self.digital_product_catalog_table.add_columns("Digital Product Catalog Name", "Description", "Qualified Name")
            self.digital_product_catalog_table.cursor_type = "row"
            self.digital_product_catalog_table.zebra_stripes = True

        try:
            self.digital_product_catalog_data = exec_report_spec(
                format_set_name="Digital-Product-Catalog",
                output_format="DICT",
                params={
                    "search_string": "*",
                    "metadata_element_subtypes": ["DigitalProduct", "DigitalProductFamily"],
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
                )
        return 200

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

if __name__ == "__main__":
    app = MyProfileApp()
    app.run()
