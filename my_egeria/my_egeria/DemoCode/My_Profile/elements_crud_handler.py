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
from ShowCommentsScreen import ShowCommentsScreen


class ElementsCrudMixin:
    """Mixin class providing profile element addition, editing, and comment handling for MyProfileApp."""

    def user_identities_callback(self) -> None:
        """Callback routine for the user identities screen.
        The user has requested to exit the screen, so push the main screen again.
        """
        self._show_main_screen()

    def edit_identities_callback(self, rows_with_keys: Any) -> None:
        """Callback for EditIdentitiesScreen."""
        if isinstance(rows_with_keys, list):
            main_screen = self.get_screen("main")
            table = main_screen.query_one("#user_identity_table", DataTable)
            table.clear()
            for key_str, cell_values in rows_with_keys:
                table.add_row(*cell_values, key=key_str)
        self._show_main_screen()

    def edit_communities_callback(self, rows_with_keys: Any) -> None:
        """Callback for EditCommunitiesScreen."""
        if isinstance(rows_with_keys, list):
            main_screen = self.get_screen("main")
            table = main_screen.query_one("#communities_table", DataTable)
            table.clear()
            for key_str, cell_values in rows_with_keys:
                table.add_row(*cell_values, key=key_str)
        self._show_main_screen()

    def edit_roles_callback(self, rows_with_keys: Any) -> None:
        """Callback for EditRolesScreen."""
        if isinstance(rows_with_keys, list):
            main_screen = self.get_screen("main")
            table = main_screen.query_one("#roles_table", DataTable)
            table.clear()
            for key_str, cell_values in rows_with_keys:
                table.add_row(*cell_values, key=key_str)
        self._show_main_screen()

    def edit_teams_callback(self, rows_with_keys: Any) -> None:
        """Callback for EditTeamsScreen."""
        if isinstance(rows_with_keys, list):
            main_screen = self.get_screen("main")
            table = main_screen.query_one("#teams_table", DataTable)
            table.clear()
            for key_str, cell_values in rows_with_keys:
                table.add_row(*cell_values, key=key_str)
        self._show_main_screen()

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

    def edit_tables(self, table_name: str, row_k: Any) -> None:
        """Edit the selected table."""
        self.log(f"Editing table: {table_name}, row: {row_k}")
        if table_name == "roles_table":
            self.push_screen(EditRolesScreen(), callback=self.edit_roles_callback)
        elif table_name == "projects_table":
            self.push_screen(EditProjectsScreen(), callback=self.edit_projects_callback)
        elif table_name == "communities_table":
            self.push_screen(EditCommunitiesScreen(), callback=self.edit_communities_callback)
        elif table_name == "teams_table":
            self.push_screen(EditTeamsScreen(), callback=self.edit_teams_callback)
        elif table_name == "blogs_table":
            self.push_screen(EditBlogsScreen(), callback=self.edit_blogs_callback)
        elif table_name == "journal_table":
            self.push_screen(EditJournalScreen(), callback=self.edit_journal_callback)
        elif table_name == "todos_table":
            self.push_screen(EditTodosScreen(), callback=self.edit_todos_callback)
        elif table_name == "associations_table":
            self.push_screen(EditAssociationsScreen(), callback=self.edit_assaociations_callback)
        else:
            self.log(f"Unexpected table name: {table_name}")

    def edit_projects_callback(self, return_c: Any) -> None:
        pass

    def edit_blogs_callback(self, return_c: Any) -> None:
        pass

    def edit_journal_callback(self, return_c: Any) -> None:
        pass

    def edit_todos_callback(self, return_c: Any) -> None:
        pass

    def edit_assaociations_callback(self, return_c: Any) -> None:
        pass

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
        if self.selected_table == "roles_table":
            await self.push_screen(AddRoleScreen(self.selected_table, self.user_GUID), callback=self.add_role_callback)
        elif self.selected_table == "projects_table":
            await self.push_screen(AddProjectScreen(self.selected_table, self.user_GUID), callback=self.add_project_callback)
        elif self.selected_table == "communities_table":
            await self.push_screen(AddCommunityScreen(self.selected_table, self.user_GUID), callback=self.add_community_callback)
        elif self.selected_table == "my_team_table":
            await self.push_screen(AddTeamScreen(self.selected_table, self.user_GUID), callback=self.add_team_callback)
        elif self.selected_table == "blogs_table":
            await self.push_screen(AddBlogEntryScreen(self.selected_table, self.user_GUID), callback=self.add_blog_entry_callback)
        elif self.selected_table == "journal_table":
            await self.push_screen(AddJournalEntryScreen(self.selected_table, self.user_GUID), callback=self.add_journal_entry_callback)
        elif self.selected_table == "todos_table":
            await self.push_screen(AddTodoScreen(self.selected_table, self.user_GUID), callback=self.add_todo_callback)
        elif self.selected_table == "associations_table":
            await self.push_screen(AddAssociationScreen(self.selected_table, self.user_GUID), callback=self.add_association_callback)
        else:
            self.log(f"Unexpected table name: {self.selected_table}")

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
