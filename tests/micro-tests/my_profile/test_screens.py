"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Unit tests for My Profile UI modal screens.
"""

from unittest.mock import MagicMock, AsyncMock, patch
import pytest
from textual.app import App, ComposeResult
from textual.widgets import Input, Button, Markdown, DataTable, Static, Tree

from StatusScreen import StatusScreen
from UserIdentitiesScreen import UserIdentitiesScreen
from MyTeamScreen import MyTeam
from SearchForTermScreen import SearchForTermScreen
from ShowCommentsScreen import ShowCommentsScreen
from MainScreen import MainScreen
from CreateProfileScreen import CreateProfileScreen
from CreateSubscriptionRequestScreen import CreateSubscriptionRequestScreen
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
from EditElementsScreens import (
    EditProfileScreen,
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
from TechnologyTypeScreens import (
    TechnologyTypesScreen,
    TechnologyTypeOptionsScreen,
    TechnologyTypeTemplatesScreen,
    TechnologyTypeProcessesScreen,
)
from SelectionOverviewScreen import SelectionOverviewScreen
from ShopForDataScreen import ShopForDataScreen


class ScreenTestHostApp(App):
    """Host Textual App with main screen mounted."""

    def __init__(self, screen_factory):
        super().__init__()
        self.screen_factory = screen_factory
        self.target_screen = None
        self.dismissed_result = None
        self.view_server = "qs-view-server"
        self.platform_url = "https://127.0.0.1:9443"
        self.user_name = "garygeeke"
        self.user_password = "secret"
        self.user = "garygeeke"
        self.password = "secret"
        self.karma_points = 150

    async def on_mount(self):
        main1 = MainScreen()
        main2 = MainScreen()
        self.install_screen(main1, name="main")
        self.install_screen(main2, name="main_screen")
        await self.push_screen("main")
        self.target_screen = self.screen_factory()

        def _cb(result):
            self.dismissed_result = result

        await self.push_screen(self.target_screen, callback=_cb)


class TestStatusScreen:
    """Tests for StatusScreen."""

    @pytest.mark.asyncio
    async def test_status_screen_actions(self):
        app = ScreenTestHostApp(lambda: StatusScreen("Operation completed with GUID: 'test-guid-123'"))
        async with app.run_test() as pilot:
            app.target_screen.action_quit()
            await pilot.pause()
            assert app.dismissed_result == 200

    @pytest.mark.asyncio
    async def test_status_screen_unsuccessful(self):
        app = ScreenTestHostApp(lambda: StatusScreen("Error occurred"))
        async with app.run_test() as pilot:
            app.target_screen.action_unsuccessful()
            await pilot.pause()
            assert app.dismissed_result == 400

    @pytest.mark.asyncio
    @patch("StatusScreen.copy_to_clipboard")
    async def test_status_screen_copy_guid(self, mock_copy):
        app = ScreenTestHostApp(lambda: StatusScreen("Created element with GUID: 'guid-abc-123'"))
        async with app.run_test() as pilot:
            app.target_screen.action_copy_guid_to_clipboard()
            await pilot.pause()
            mock_copy.assert_called_once_with("guid-abc-123")
            assert app.dismissed_result == 200


class TestUserIdentitiesScreen:
    """Tests for UserIdentitiesScreen."""

    @pytest.mark.asyncio
    async def test_user_identities_screen_with_data(self, sample_user_identities):
        app = ScreenTestHostApp(lambda: UserIdentitiesScreen("garygeeke", "secret", 150, sample_user_identities))
        async with app.run_test() as pilot:
            table = app.target_screen.query_one("#user_identity_datatable", DataTable)
            assert table is not None
            assert table.row_count == 1

    @pytest.mark.asyncio
    async def test_user_identities_screen_empty(self):
        app = ScreenTestHostApp(lambda: UserIdentitiesScreen("garygeeke", "secret", 150, []))
        async with app.run_test() as pilot:
            assert app.target_screen is not None


class TestMyTeamScreen:
    """Tests for MyTeamScreen."""

    @pytest.mark.asyncio
    async def test_my_team_screen_with_members(self):
        members = [["Gary Geeke", "TeamLeader", "guid-1"], ["Erin Overview", "TeamMember", "guid-2"]]
        properties = ["IT Team", "Team::IT", "Ops", "Infrastructure team"]
        app = ScreenTestHostApp(lambda: MyTeam(members, properties, "Gary Geeke"))
        async with app.run_test() as pilot:
            table = app.target_screen.query_one("#team_table", DataTable)
            assert table.row_count == 2
            app.target_screen.action_quit()
            await pilot.pause()
            assert app.dismissed_result == "200"

    @pytest.mark.asyncio
    async def test_my_team_screen_error_member(self):
        members = [["Selection Error", "No members found", ""]]
        properties = ["IT Team", "Team::IT", "Ops", "Infrastructure team"]
        app = ScreenTestHostApp(lambda: MyTeam(members, properties, "Gary Geeke"))
        async with app.run_test() as pilot:
            table = app.target_screen.query_one("#team_table", DataTable)
            assert table.row_count == 1
            app.target_screen.action_back()
            await pilot.pause()
            assert app.dismissed_result == "201"


class TestSearchForTermScreen:
    """Tests for SearchForTermScreen."""

    @pytest.mark.asyncio
    async def test_search_for_term_screen_actions(self):
        app = ScreenTestHostApp(lambda: SearchForTermScreen("garygeeke", "secret", "qs-view-server", "https://127.0.0.1:9443"))
        async with app.run_test() as pilot:
            app.target_screen.action_quit()
            await pilot.pause()
            assert app.dismissed_result == 200

    @pytest.mark.asyncio
    @patch("SearchForTermScreen.exec_report_spec")
    async def test_search_for_term_screen_search(self, mock_exec):
        mock_exec.return_value = {
            "kind": "text",
            "mimeType": "text/markdown",
            "content": "## Term Details\nDescription of clinical trial",
        }
        app = ScreenTestHostApp(lambda: SearchForTermScreen("garygeeke", "secret", "qs-view-server", "https://127.0.0.1:9443"))
        async with app.run_test() as pilot:
            inp = app.target_screen.query_one("#search_term_input", Input)
            inp.value = "Clinical"
            await pilot.click("#search_term_btn")
            await pilot.pause()
            md = app.target_screen.query_one("#search_term_result", Markdown)
            assert md is not None


class TestCreateProfileScreen:
    """Tests for CreateProfileScreen."""

    @pytest.mark.asyncio
    async def test_create_profile_screen_actions(self):
        app = ScreenTestHostApp(lambda: CreateProfileScreen("garygeeke", "secret", "qs-view-server", "https://127.0.0.1:9443"))
        async with app.run_test() as pilot:
            app.target_screen.action_quit()
            await pilot.pause()
            assert app.dismissed_result == 200

    @pytest.mark.asyncio
    @patch("CreateProfileScreen.MyProfile")
    async def test_create_profile_screen_create_profile(self, mock_mp_cls):
        mock_mp = MagicMock()
        mock_mp.create_egeria_bearer_token.return_value = "token"
        mock_mp.add_my_profile.return_value = "profile-guid-999"
        mock_mp_cls.return_value = mock_mp

        app = ScreenTestHostApp(lambda: CreateProfileScreen("garygeeke", "secret", "qs-view-server", "https://127.0.0.1:9443"))
        async with app.run_test() as pilot:
            app.target_screen.create_profile()
            await pilot.pause()
            assert app.dismissed_result == 200


class TestCreateSubscriptionRequestScreen:
    """Tests for CreateSubscriptionRequestScreen."""

    @pytest.mark.asyncio
    async def test_create_subscription_request_screen(self):
        app = ScreenTestHostApp(lambda: CreateSubscriptionRequestScreen())
        async with app.run_test() as pilot:
            inp = app.target_screen.query_one("#sub_display_name", Input)
            inp.value = "My Sub"
            status_inp = app.target_screen.query_one("#sub_status", Input)
            status_inp.value = "ACTIVE"
            await pilot.pause()
            app.target_screen.action_create_subscription()
            await pilot.pause()
            assert app.dismissed_result == ["My Sub", "Status: ACTIVE"]


class TestAddToElementsScreens:
    """Tests for AddToElements screens."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "screen_cls,table_id",
        [
            (AddRoleScreen, "roles_table"),
            (AddProjectScreen, "projects_table"),
            (AddCommunityScreen, "communities_table"),
            (AddTeamScreen, "my_team_table"),
            (AddBlogEntryScreen, "blogs_table"),
            (AddJournalEntryScreen, "journal_table"),
            (AddTodoScreen, "todos_table"),
            (AddAssociationScreen, "associations_table"),
        ],
    )
    async def test_add_screens_mount_and_cancel(self, screen_cls, table_id):
        app = ScreenTestHostApp(lambda: screen_cls(table_id, "user-guid-123"))
        async with app.run_test() as pilot:
            app.target_screen.dismiss(200)
            await pilot.pause()
            assert app.dismissed_result == 200


class TestEditElementsScreens:
    """Tests for EditElements screens."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "screen_cls",
        [
            EditIdentitiesScreen,
            EditCommunitiesScreen,
            EditRolesScreen,
            EditTeamsScreen,
            EditProjectsScreen,
            EditTodosScreen,
            EditBlogsScreen,
            EditJournalScreen,
            EditAssociationsScreen,
        ],
    )
    async def test_edit_screens_mount_and_exit(self, screen_cls):
        cols = ["Col1", "Col2"]
        rows = [("k1", ["Val1", "Val2"])]
        app = ScreenTestHostApp(lambda: screen_cls(cols, rows))
        async with app.run_test() as pilot:
            app.target_screen.action_exit_screen()
            await pilot.pause()
            assert app.dismissed_result is not None


class TestTechnologyTypeScreens:
    """Tests for TechnologyTypeScreens."""

    @pytest.mark.asyncio
    async def test_tech_types_screen(self, sample_tech_types_list):
        app = ScreenTestHostApp(lambda: TechnologyTypesScreen(sample_tech_types_list, "garygeeke", "secret", 150))
        async with app.run_test() as pilot:
            assert app.target_screen is not None

    @pytest.mark.asyncio
    async def test_tech_type_options_screen(self):
        templates = [{"displayName": "Tmpl1", "Catalog Template Name": "Tmpl1"}]
        processes = [{"displayName": "Proc1"}]
        app = ScreenTestHostApp(lambda: TechnologyTypeOptionsScreen("guid-1", "PostgreSQL", "DB", "user", "pwd", 100, templates, processes))
        async with app.run_test() as pilot:
            assert app.target_screen is not None

    @pytest.mark.asyncio
    async def test_tech_type_templates_screen(self):
        templates = [{"displayName": "Tmpl1", "Catalog Template Name": "Tmpl1", "placeholderPropertyValues": {"db_name": "mydb"}}]
        app = ScreenTestHostApp(lambda: TechnologyTypeTemplatesScreen("user", 100, "PostgreSQL", "DB", "template", "Tmpl1", templates))
        async with app.run_test() as pilot:
            assert app.target_screen is not None

    @pytest.mark.asyncio
    async def test_tech_type_processes_screen(self):
        processes = [{"displayName": "Proc1", "additionalProperties": {"templateGUID": "tmpl-1"}}]
        app = ScreenTestHostApp(lambda: TechnologyTypeProcessesScreen("user", 100, "PostgreSQL", "DB", "process", "Proc1", processes))
        async with app.run_test() as pilot:
            assert app.target_screen is not None


class TestShopForDataAndOverviewScreens:
    """Tests for ShopForDataScreen and SelectionOverviewScreen."""

    @pytest.mark.asyncio
    async def test_selection_overview_screen(self):
        tree = Tree("Glossary Tree")
        app = ScreenTestHostApp(lambda: SelectionOverviewScreen("glossary", "view-server", "https://url", "user", "pwd", data_tree=tree))
        async with app.run_test() as pilot:
            app.target_screen.action_quit()
            await pilot.pause()
            assert app.dismissed_result == 210

    @pytest.mark.asyncio
    async def test_shop_for_data_screen(self):
        t1 = DataTable(id="glossary_table")
        t2 = DataTable(id="digital_product_catalog_table")
        t3 = DataTable(id="data_dictionary_table")
        t4 = DataTable(id="business_domain_table")
        t5 = DataTable(id="data_specification_table")
        app = ScreenTestHostApp(lambda: ShopForDataScreen(t1, t2, t3, t4, t5, "user", "pwd", "view-server", "https://url"))
        async with app.run_test() as pilot:
            app.target_screen.action_quit()
            await pilot.pause()
            assert app.dismissed_result == [210]
