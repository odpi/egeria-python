"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Unit tests for elements_crud_handler module.
"""

from unittest.mock import MagicMock, AsyncMock, patch
import pytest
from textual.widgets import DataTable

from elements_crud_handler import ElementsCrudMixin
from EditElementsScreens import (
    EditIdentitiesScreen,
    EditCommunitiesScreen,
    EditRolesScreen,
    EditTeamsScreen,
    EditProjectsScreen,
    EditTodosScreen,
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


class DummyApp(ElementsCrudMixin):
    """Test harness implementing ElementsCrudMixin with mocked host methods."""

    def __init__(self):
        self.pushed_screens = []
        self.switched_screens = []
        self.shown_main_screen = False
        self.log_messages = []
        self.user_GUID = "test-user-guid"
        self.view_server = "qs-view-server"
        self.platform_url = "https://127.0.0.1:9443"
        self.user_name = "garygeeke"
        self.user_password = "secret"
        self._screens = {}

    def log(self, msg, *args, **kwargs):
        self.log_messages.append(str(msg))

    def _show_main_screen(self):
        self.shown_main_screen = True

    def get_screen(self, screen_id):
        return self._screens.get(screen_id, MagicMock())

    def push_screen(self, screen, callback=None):
        self.pushed_screens.append((screen, callback))

    def switch_screen(self, screen_id):
        self.switched_screens.append(screen_id)


class TestElementsCrudMixinCallbacks:
    """Tests for ElementsCrudMixin callbacks and screen transitions."""

    def test_user_identities_callback(self):
        app = DummyApp()
        app.user_identities_callback()
        assert app.shown_main_screen is True

    def test_edit_identities_callback(self):
        app = DummyApp()
        mock_main = MagicMock()
        mock_table = MagicMock()
        mock_main.query_one.return_value = mock_table
        app._screens["main"] = mock_main

        rows = [("k1", ["Gary", "garygeeke", "dn1", "g1"])]
        app.edit_identities_callback(rows)

        mock_table.clear.assert_called_once()
        mock_table.add_row.assert_called_once_with("Gary", "garygeeke", "dn1", "g1", key="k1")
        assert app.shown_main_screen is True

    def test_edit_communities_callback(self):
        app = DummyApp()
        mock_main = MagicMock()
        mock_table = MagicMock()
        mock_main.query_one.return_value = mock_table
        app._screens["main"] = mock_main

        rows = [("k2", ["LEADER", "Cloud Arch", "Desc", "g2"])]
        app.edit_communities_callback(rows)

        mock_table.clear.assert_called_once()
        mock_table.add_row.assert_called_once_with("LEADER", "Cloud Arch", "Desc", "g2", key="k2")
        assert app.shown_main_screen is True

    def test_edit_roles_callback(self):
        app = DummyApp()
        mock_main = MagicMock()
        mock_table = MagicMock()
        mock_main.query_one.return_value = mock_table
        app._screens["main"] = mock_main

        rows = [("k3", ["Lead", "TeamLeader", "Desc", "g3"])]
        app.edit_roles_callback(rows)

        mock_table.clear.assert_called_once()
        mock_table.add_row.assert_called_once_with("Lead", "TeamLeader", "Desc", "g3", key="k3")
        assert app.shown_main_screen is True

    def test_edit_teams_callback(self):
        app = DummyApp()
        mock_main = MagicMock()
        mock_table = MagicMock()
        mock_main.query_one.return_value = mock_table
        app._screens["main"] = mock_main

        rows = [("k4", ["MEMBER", "DevOps", "Desc", "g4"])]
        app.edit_teams_callback(rows)

        mock_table.clear.assert_called_once()
        mock_table.add_row.assert_called_once_with("MEMBER", "DevOps", "Desc", "g4", key="k4")
        assert app.shown_main_screen is True

    def test_edit_profile_callback_int(self):
        app = DummyApp()
        app.edit_profile_callback(200)
        assert app.shown_main_screen is True

        app.shown_main_screen = False
        app.edit_profile_callback(400)
        assert app.shown_main_screen is True

    def test_edit_profile_callback_string_subscreens(self):
        for route_str, screen_cls in [
            ("identity", EditIdentitiesScreen),
            ("community", EditCommunitiesScreen),
            ("role", EditRolesScreen),
            ("team", EditTeamsScreen),
        ]:
            app = DummyApp()
            mock_main = MagicMock()
            mock_table = MagicMock()
            mock_col = MagicMock()
            mock_col.label.plain = "Col1"
            mock_table.columns = {"c1": mock_col}
            mock_row_key = MagicMock()
            mock_row_key.value = "r1"
            mock_table.rows = [mock_row_key]
            mock_table.get_row.return_value = ["Val1"]
            mock_main.query_one.return_value = mock_table
            app._screens["main"] = mock_main

            app.edit_profile_callback(route_str)
            assert len(app.pushed_screens) == 1
            screen_instance, callback = app.pushed_screens[0]
            assert isinstance(screen_instance, screen_cls)

    def test_edit_profile_callback_unexpected(self):
        app = DummyApp()
        app.edit_profile_callback([1, 2, 3])
        assert app.shown_main_screen is True


class TestElementsCrudMixinEditTables:
    """Tests for edit_tables routing."""

    @pytest.mark.parametrize(
        "table_name,expected_screen_cls",
        [
            ("roles_table", EditRolesScreen),
            ("projects_table", EditProjectsScreen),
            ("communities_table", EditCommunitiesScreen),
            ("teams_table", EditTeamsScreen),
            ("blogs_table", EditBlogsScreen),
            ("journal_table", EditJournalScreen),
            ("todos_table", EditTodosScreen),
            ("associations_table", EditAssociationsScreen),
        ],
    )
    def test_edit_tables_routing(self, table_name, expected_screen_cls):
        app = DummyApp()
        app.edit_tables(table_name, 0)
        assert len(app.pushed_screens) == 1
        screen_instance, callback = app.pushed_screens[0]
        assert isinstance(screen_instance, expected_screen_cls)

    def test_edit_tables_unexpected(self):
        app = DummyApp()
        app.edit_tables("unknown_table", 0)
        assert len(app.pushed_screens) == 0
        assert any("Unexpected table name" in msg for msg in app.log_messages)

    def test_empty_edit_callbacks(self):
        app = DummyApp()
        # These are currently no-op pass methods, verify they run without exception
        app.edit_projects_callback(None)
        app.edit_blogs_callback(None)
        app.edit_journal_callback(None)
        app.edit_todos_callback(None)
        app.edit_assaociations_callback(None)


class TestElementsCrudMixinAddAndComments:
    """Tests for add_to_tables and show_comments."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "table_name,expected_screen_cls",
        [
            ("roles_table", AddRoleScreen),
            ("projects_table", AddProjectScreen),
            ("communities_table", AddCommunityScreen),
            ("my_team_table", AddTeamScreen),
            ("blogs_table", AddBlogEntryScreen),
            ("journal_table", AddJournalEntryScreen),
            ("todos_table", AddTodoScreen),
            ("associations_table", AddAssociationScreen),
        ],
    )
    async def test_add_to_tables_routing(self, table_name, expected_screen_cls):
        app = DummyApp()
        app.push_screen = AsyncMock()
        await app.add_to_tables(table_name, 0)
        assert app.push_screen.call_count == 1
        call_args = app.push_screen.call_args[0]
        assert isinstance(call_args[0], expected_screen_cls)

    @pytest.mark.asyncio
    async def test_add_to_tables_unexpected(self):
        app = DummyApp()
        app.push_screen = AsyncMock()
        await app.add_to_tables("unknown_table", 0)
        assert app.push_screen.call_count == 0
        assert any("Unexpected table name" in msg for msg in app.log_messages)

    @pytest.mark.parametrize(
        "callback_name",
        [
            "add_role_callback",
            "add_association_callback",
            "add_project_callback",
            "add_community_callback",
            "add_team_callback",
            "add_blog_entry_callback",
            "add_journal_entry_callback",
            "add_todo_callback",
        ],
    )
    def test_add_callbacks_switch_main(self, callback_name):
        app = DummyApp()
        cb = getattr(app, callback_name)
        cb("new-guid-123")
        assert "main" in app.switched_screens

    def test_show_comments_and_callback(self):
        app = DummyApp()
        app.show_comments("roles_table", "role-guid-1")
        assert len(app.pushed_screens) == 1
        screen_instance, callback = app.pushed_screens[0]
        assert isinstance(screen_instance, ShowCommentsScreen)

        app.shown_main_screen = False
        app.show_comments_callback(None)
        assert app.shown_main_screen is True

        app.shown_main_screen = False
        app.show_comments_callback("custom_return")
        assert app.shown_main_screen is True
