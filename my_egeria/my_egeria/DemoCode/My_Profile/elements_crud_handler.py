"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Profile elements CRUD and comments handler mixin for My Profile Textual App.
"""

import sys
from pathlib import Path
from typing import Any

# Ensure project root is on sys.path
root_path = Path(__file__).resolve().parents[4]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from textual.widgets import DataTable

from pyegeria import Egeria, PyegeriaException

from EditElementsScreens import (
    EditProfileScreen,
    EditCollectionsScreen,
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
from AddToElementsScreens import (
    AddRoleScreen,
    AddProjectScreen,
    AddCollectionScreen,
    AddCommunityScreen,
    AddTeamScreen,
    AddBlogEntryScreen,
    AddJournalEntryScreen,
    AddTodoScreen,
    AddAssociationScreen,
    AddUserIdentityScreen,
)
from ShowCommentsScreen import ShowCommentsScreen

# Main-screen table id -> (edit screen, name of the callback that writes rows back).
EDIT_TABLE_ROUTES: dict[str, tuple[type, str]] = {
    "associations_table": (EditAssociationsScreen, "edit_assaociations_callback"),
    "blogs_table": (EditBlogsScreen, "edit_blogs_callback"),
    "communities_table": (EditCommunitiesScreen, "edit_communities_callback"),
    "journal_table": (EditJournalScreen, "edit_journal_callback"),
    "my_collections_table": (EditCollectionsScreen, "edit_collections_callback"),
    "projects_table": (EditProjectsScreen, "edit_projects_callback"),
    "roles_table": (EditRolesScreen, "edit_roles_callback"),
    "teams_table": (EditTeamsScreen, "edit_teams_callback"),
    "todos_table": (EditTodosScreen, "edit_todos_callback"),
    "user_identity_table": (EditIdentitiesScreen, "edit_identities_callback"),
}

# Main-screen table id -> (add screen, name of the callback run after the add).
ADD_TABLE_ROUTES: dict[str, tuple[type, str]] = {
    "associations_table": (AddAssociationScreen, "add_association_callback"),
    "blogs_table": (AddBlogEntryScreen, "add_blog_entry_callback"),
    "communities_table": (AddCommunityScreen, "add_community_callback"),
    "journal_table": (AddJournalEntryScreen, "add_journal_entry_callback"),
    "my_collections_table": (AddCollectionScreen, "add_collection_callback"),
    "projects_table": (AddProjectScreen, "add_project_callback"),
    "roles_table": (AddRoleScreen, "add_role_callback"),
    "teams_table": (AddTeamScreen, "add_team_callback"),
    "todos_table": (AddTodoScreen, "add_todo_callback"),
    "user_identity_table": (AddUserIdentityScreen, "add_user_identity_callback"),
    # Historical alias: earlier code routed teams through this id
    "my_team_table": (AddTeamScreen, "add_team_callback"),
}

# Main-screen table id -> (Egeria delete method, keyword arguments).
# Blogs, journal entries and to-dos have no bespoke SDK delete, so they use the
# generic metadata-element delete: it takes only a GUID, so it cannot be wrong
# about the element's type.
DELETE_METHODS: dict[str, tuple[str, dict[str, Any]]] = {
    "associations_table": ("delete_community", {"cascade": False}),
    "blogs_table": ("delete_metadata_element", {"cascade_delete": False}),
    "communities_table": ("delete_community", {"cascade": False}),
    "journal_table": ("delete_metadata_element", {"cascade_delete": False}),
    "my_collections_table": ("delete_collection", {"cascade": False}),
    "projects_table": ("delete_project", {"cascade": False}),
    "roles_table": ("delete_actor_role", {"cascade": False}),
    "teams_table": ("delete_actor_profile", {"cascade": False}),
    "todos_table": ("delete_metadata_element", {"cascade_delete": False}),
    "user_identity_table": ("delete_user_identity", {"cascade": False}),
}


class ElementsCrudMixin:
    """Mixin class providing profile element addition, editing, and comment handling for MyProfileApp."""

    def user_identities_callback(self) -> None:
        """Callback routine for the user identities screen.
        The user has requested to exit the screen, so push the main screen again.
        """
        self._show_main_screen()

    def _get_main_table(self, table_id: str) -> DataTable | None:
        """The named DataTable on the main screen, or None if it isn't composed."""
        try:
            main_screen = self.get_screen("main")
            return main_screen.query_one(f"#{table_id}", DataTable)
        except Exception as e:
            self.log(f"Table #{table_id} not available on the main screen: {e}")
            return None

    def _write_back_rows(self, table_id: str, rows_with_keys: Any) -> None:
        """Write an edit screen's rows back onto its main-screen table."""
        if isinstance(rows_with_keys, list):
            table = self._get_main_table(table_id)
            if table is not None:
                table.clear()
                for key_str, cell_values in rows_with_keys:
                    table.add_row(*cell_values, key=key_str)
        self._show_main_screen()

    def edit_identities_callback(self, rows_with_keys: Any) -> None:
        """Callback for EditIdentitiesScreen."""
        self._write_back_rows("user_identity_table", rows_with_keys)

    def edit_communities_callback(self, rows_with_keys: Any) -> None:
        """Callback for EditCommunitiesScreen."""
        self._write_back_rows("communities_table", rows_with_keys)

    def edit_roles_callback(self, rows_with_keys: Any) -> None:
        """Callback for EditRolesScreen."""
        self._write_back_rows("roles_table", rows_with_keys)

    def edit_teams_callback(self, rows_with_keys: Any) -> None:
        """Callback for EditTeamsScreen."""
        self._write_back_rows("teams_table", rows_with_keys)

    def edit_profile_callback(self, return_c: Any) -> None:
        """Callback routine for the edit profile screen."""
        if isinstance(return_c, int):
            if return_c == 200:
                self._show_main_screen()
            else:
                self.log(f"Error returned from EditProfileScreen: {return_c}")
                self.log("Returning to main screen")
                self._show_main_screen()
        elif isinstance(return_c, str):
            if return_c == "identity":
                main_screen = self.get_screen("main")
                self.identities_table = main_screen.query_one("#user_identity_table", DataTable)
                columns = [col.label.plain for col in self.identities_table.columns.values()]
                rows_with_keys = []
                for row_key in self.identities_table.rows:
                    rows_with_keys.append((row_key.value, self.identities_table.get_row(row_key)))
                self.push_screen(EditIdentitiesScreen(columns, rows_with_keys), callback=self.edit_identities_callback)
            elif return_c == "community":
                main_screen = self.get_screen("main")
                self.communities_table = main_screen.query_one("#communities_table", DataTable)
                columns = [col.label.plain for col in self.communities_table.columns.values()]
                rows_with_keys = []
                for row_key in self.communities_table.rows:
                    rows_with_keys.append((row_key.value, self.communities_table.get_row(row_key)))
                self.push_screen(EditCommunitiesScreen(columns, rows_with_keys), callback=self.edit_communities_callback)
            elif return_c == "role":
                main_screen = self.get_screen("main")
                self.roles_table = main_screen.query_one("#roles_table", DataTable)
                columns = [col.label.plain for col in self.roles_table.columns.values()]
                rows_with_keys = []
                for row_key in self.roles_table.rows:
                    rows_with_keys.append((row_key.value, self.roles_table.get_row(row_key)))
                self.push_screen(EditRolesScreen(columns, rows_with_keys), callback=self.edit_roles_callback)
            elif return_c == "team":
                main_screen = self.get_screen("main")
                self.teams_table = main_screen.query_one("#teams_table", DataTable)
                columns = [col.label.plain for col in self.teams_table.columns.values()]
                rows_with_keys = []
                for row_key in self.teams_table.rows:
                    rows_with_keys.append((row_key.value, self.teams_table.get_row(row_key)))
                self.push_screen(EditTeamsScreen(columns, rows_with_keys), callback=self.edit_teams_callback)
        else:
            self.log(f"Unexpected return type from EditProfileScreen: {type(return_c)}")
            self._show_main_screen()

    async def edit_tables(self, table_name: str, row_k: Any) -> None:
        """Push the edit screen for the selected table, populated with its live rows."""
        self.log(f"Editing table: {table_name}, row: {row_k}")
        route = EDIT_TABLE_ROUTES.get(table_name)
        if route is None:
            self.log(f"Unexpected table name: {table_name}")
            return

        screen_cls, callback_name = route
        table = self._get_main_table(table_name)
        if table is None:
            self.notify(f"The {table_name} table isn't available to edit.",
                        timeout=5, severity="warning")
            return

        columns = [col.label.plain for col in table.columns.values()]
        rows_with_keys = [(row_key.value, table.get_row(row_key)) for row_key in table.rows]
        self.push_screen(screen_cls(columns, rows_with_keys), callback=getattr(self, callback_name))

    def edit_projects_callback(self, rows_with_keys: Any) -> None:
        """Callback for EditProjectsScreen."""
        self._write_back_rows("projects_table", rows_with_keys)

    def edit_blogs_callback(self, rows_with_keys: Any) -> None:
        """Callback for EditBlogsScreen."""
        self._write_back_rows("blogs_table", rows_with_keys)

    def edit_journal_callback(self, rows_with_keys: Any) -> None:
        """Callback for EditJournalScreen."""
        self._write_back_rows("journal_table", rows_with_keys)

    def edit_todos_callback(self, rows_with_keys: Any) -> None:
        """Callback for EditTodosScreen."""
        self._write_back_rows("todos_table", rows_with_keys)

    def edit_collections_callback(self, rows_with_keys: Any) -> None:
        """Callback for EditCollectionsScreen."""
        self._write_back_rows("my_collections_table", rows_with_keys)

    def edit_assaociations_callback(self, rows_with_keys: Any) -> None:
        """Callback for EditAssociationsScreen.

        The misspelling is kept because existing callers and tests refer to it;
        edit_associations_callback is the alias to prefer in new code.
        """
        self._write_back_rows("associations_table", rows_with_keys)

    def edit_associations_callback(self, rows_with_keys: Any) -> None:
        """Correctly-spelled alias for edit_assaociations_callback."""
        self.edit_assaociations_callback(rows_with_keys)

    async def delete_element(self, source_table: str, guid: str) -> bool:
        """Delete the Egeria element behind a table row.

        Returns True only if Egeria accepted the delete, so the caller can leave
        the row on display when it didn't.
        """
        self.log(f"Deleting element {guid} on behalf of table {source_table}")
        if not guid:
            return False

        route = DELETE_METHODS.get(source_table)
        if route is None:
            self.log(f"No delete is defined for table: {source_table}")
            self.notify(f"Deleting rows from {source_table} isn't supported.",
                        timeout=6, severity="warning")
            return False
        method_name, kwargs = route

        client = Egeria(view_server=self.view_server, platform_url=self.platform_url,
                        user_id=self.user_name, user_pwd=self.user_password)
        try:
            client.create_egeria_bearer_token(self.user_name, self.user_password)
            getattr(client, method_name)(guid, **kwargs)
            self.log(f"{method_name}({guid}) succeeded")
            return True
        except PyegeriaException as e:
            self.log(f"{method_name}({guid}) failed: {e}")
            self.notify(f"Delete failed: {e}", timeout=10, severity="error")
            return False
        finally:
            client.close_session()

    def show_comments(self, table_name: str, row_k: Any) -> None:
        """Show comments for the selected table."""
        self.log(f"Showing comments for table: {table_name}, row: {row_k}")
        self.push_screen(
            ShowCommentsScreen(
                table_name,
                row_k,
                self.view_server,
                self.platform_url,
                self.user_name,
                self.user_password,
            ),
            callback=self.show_comments_callback,
        )

    def show_comments_callback(self, return_c: Any) -> None:
        """Callback for ShowCommentsScreen."""
        self.log(f"Return from ShowCommentsScreen: {return_c}")
        if return_c is None:
            self.log("No return from ShowCommentsScreen")
            self._show_main_screen()
        else:
            self.log(f"Unexpected return type from ShowCommentsScreen: {type(return_c)}")
            self._show_main_screen()

    async def add_to_tables(self, selected_table: str, selected_row: Any) -> None:
        """Called from main screen when user selects to add a row to a table."""
        self.log(f"Adding row {selected_row} to table {selected_table}")
        self.selected_table = selected_table
        self.selected_row = selected_row

        route = ADD_TABLE_ROUTES.get(self.selected_table)
        if route is None:
            self.log(f"Unexpected table name: {self.selected_table}")
            return

        screen_cls, callback_name = route
        await self.push_screen(screen_cls(self.selected_table, self.user_GUID),
                               callback=getattr(self, callback_name))

    def add_role_callback(self, result: Any) -> None:
        """Called from AddRoleScreen when user adds a role."""
        if result:
            self.log(f"Added role {result}")
            self.switch_screen("main")

    def add_association_callback(self, result: Any) -> None:
        """Called from AddAssociationScreen when user adds an association."""
        if result:
            self.log(f"Added association {result}")
            self.switch_screen("main")

    def add_project_callback(self, result: Any) -> None:
        """Called from AddProjectScreen when user adds a project."""
        if result:
            self.log(f"Added project {result}")
            self.switch_screen("main")

    def add_community_callback(self, result: Any) -> None:
        """Called from AddCommunityScreen when user adds a community."""
        if result:
            self.log(f"Added community {result}")
            self.switch_screen("main")

    def add_team_callback(self, result: Any) -> None:
        """Called from AddTeamScreen when user adds a team."""
        if result:
            self.log(f"Added team {result}")
            self.switch_screen("main")

    def add_blog_entry_callback(self, result: Any) -> None:
        """Called from AddBlogEntryScreen when user adds a blog entry."""
        if result:
            self.log(f"Added blog entry {result}")
            self.switch_screen("main")

    def add_journal_entry_callback(self, result: Any) -> None:
        """Called from AddJournalEntryScreen when user adds a journal entry."""
        if result:
            self.log(f"Added journal entry {result}")
            self.switch_screen("main")

    def add_todo_callback(self, result: Any) -> None:
        """Called from AddTodoScreen when user adds a todo."""
        if result:
            self.log(f"Added todo {result}")
            self.switch_screen("main")

    def add_collection_callback(self, result: Any) -> None:
        """Called from AddCollectionScreen when user adds a collection."""
        if result:
            self.log(f"Added collection {result}")
            self.switch_screen("main")

    def add_user_identity_callback(self, result: Any) -> None:
        """Called from AddUserIdentityScreen when user adds a user identity."""
        if result:
            self.log(f"Added user identity {result}")
            self.switch_screen("main")
