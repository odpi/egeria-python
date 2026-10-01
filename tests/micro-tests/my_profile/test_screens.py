"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Unit tests for My Profile UI modal screens.
"""

import uuid
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
    AddCollectionScreen,
    AddUserIdentityScreen,
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
from ViewSubscriptionsScreen import ViewSubscriptionsScreen


class ScreenTestHostApp(App):
    """Host Textual App with main screen mounted."""

    def __init__(self, screen_factory, backend=None):
        super().__init__()
        self.screen_factory = screen_factory
        self.target_screen = None
        self.dismissed_result = None
        self.view_server = "qs-view-server"
        self.platform_url = "https://127.0.0.1:9443"
        self.user_name = "garygeeke"
        self.user_password = "secret"
        if backend is not None:
            backend.apply_connection(self)
        self.user = self.user_name
        self.password = self.user_password
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

    @pytest.mark.live_capable
    @pytest.mark.asyncio
    async def test_search_for_term_screen_search(self, backend):
        backend.patch(
            "SearchForTermScreen.exec_report_spec",
            returns={
                "kind": "text",
                "mimeType": "text/markdown",
                "content": "## Term Details\nDescription of clinical trial",
            },
        )
        app = ScreenTestHostApp(
            lambda: SearchForTermScreen(
                backend.user_id, backend.user_pwd, backend.view_server, backend.platform_url
            ),
            backend,
        )
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

    @pytest.mark.live_capable
    @pytest.mark.asyncio
    async def test_create_profile_screen_create_profile(self, backend):
        """Calls add_my_profile — a real write when running live."""
        if backend.live:
            # add_my_profile creates the profile for the *calling* user, and the
            # server rejects a second one (OMVS-MY-PROFILE-400-001). This path
            # is only reachable live for a user who has no profile yet.
            from pyegeria import MyProfile

            probe = MyProfile(
                backend.view_server, backend.platform_url, backend.user_id, backend.user_pwd
            )
            probe.create_egeria_bearer_token(backend.user_id, backend.user_pwd)
            if probe.get_my_profile(output_format="DICT", report_spec="My-User-MD"):
                pytest.skip(
                    f"user {backend.user_id} already has a profile; "
                    "add_my_profile cannot be exercised live"
                )
            backend.patch("CreateProfileScreen.MyProfile")
        else:
            mock_mp = MagicMock()
            mock_mp.create_egeria_bearer_token.return_value = "token"
            mock_mp.add_my_profile.return_value = "profile-guid-999"
            backend.always_fake("CreateProfileScreen.MyProfile", returns=mock_mp)

        app = ScreenTestHostApp(
            lambda: CreateProfileScreen(
                backend.user_id, backend.user_pwd, backend.view_server, backend.platform_url
            ),
            backend,
        )
        async with app.run_test() as pilot:
            if backend.live:
                # An empty form yields qualifiedName "Person", which the server
                # rejects. Fill it with values unique to this run.
                suffix = uuid.uuid4().hex[:8]
                for field_id, value in {
                    "#user_employee_id": f"TEST-{suffix}",
                    "#user_resident_country": "United Kingdom",
                    "#user_given_names": "Pytest",
                    "#user_family_name": f"Fixture{suffix}",
                    "#user_preferred_name": f"Pytest Fixture {suffix}",
                    "#user_title": "Dr",
                    "#user_pronouns": "they/them",
                    "#user_job_title": "Automated test profile",
                    "#user_description": "Created by the My Profile live test suite",
                    "#user_preferred_language": "English",
                    "#user_time_zone": "Europe/London",
                }.items():
                    app.target_screen.query_one(field_id, Input).value = value
                await pilot.pause()

            app.target_screen.create_profile()
            await pilot.pause()
            assert app.dismissed_result == 200


class TestCreateSubscriptionRequestScreen:
    """Tests for CreateSubscriptionRequestScreen."""

    @pytest.mark.asyncio
    async def test_create_subscription_request_screen(self):
        app = ScreenTestHostApp(lambda: CreateSubscriptionRequestScreen(selected_item="guid-item-123"))
        async with app.run_test() as pilot:
            inp = app.target_screen.query_one("#sub_display_name", Input)
            inp.value = "My Sub"
            status_inp = app.target_screen.query_one("#sub_status", Input)
            status_inp.value = "ACTIVE"
            await pilot.pause()
            app.target_screen.action_create_subscription()
            await pilot.pause()
            assert app.dismissed_result == {
                "externalSourceGUID": "guid-item-123",
                "guid": "guid-item-123",
                "GUID": "guid-item-123",
                "displayName": "My Sub",
                "Status": "ACTIVE",
            }


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
            (AddCollectionScreen, "my_collections_table"),
            (AddUserIdentityScreen, "user_identity_table"),
        ],
    )
    async def test_add_screens_mount_and_cancel(self, screen_cls, table_id):
        app = ScreenTestHostApp(lambda: screen_cls(table_id, "user-guid-123"))
        async with app.run_test() as pilot:
            app.target_screen.dismiss(200)
            await pilot.pause()
            assert app.dismissed_result == 200


class TestBaseAddScreen:
    """Tests for the BaseAddScreen-driven add screens (Collection, User Identity)."""

    @pytest.fixture
    def mock_egeria(self):
        with patch("AddToElementsScreens.Egeria") as mock_egeria:
            # MagicMock doesn't auto-create dunder-style attributes, so supply this one
            mock_egeria.return_value.__create_qualified_name__ = MagicMock(
                side_effect=lambda type_name, name: f"{type_name}::{name}")
            yield mock_egeria

    @staticmethod
    def _fill(screen, values):
        for field_id, value in values.items():
            screen.query_one(f"#{field_id}", Input).value = value

    @pytest.mark.asyncio
    async def test_missing_required_field_does_not_call_egeria(self, mock_egeria):
        app = ScreenTestHostApp(lambda: AddCollectionScreen("my_collections_table", "user-guid-123"))
        async with app.run_test() as pilot:
            self._fill(app.target_screen, {"collection_name": "My Collection"})
            app.target_screen.action_add_element()
            await pilot.pause()
            mock_egeria.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_collection(self, mock_egeria):
        client = mock_egeria.return_value
        client.create_collection.return_value = "coll-guid-1"
        app = ScreenTestHostApp(lambda: AddCollectionScreen("my_collections_table", "user-guid-123"))
        async with app.run_test() as pilot:
            screen = app.target_screen
            self._fill(screen, {"collection_name": "My Collection",
                                "collection_description": "Things I use"})
            # press() rather than pilot.click(): the button sits below the test terminal's visible area
            screen.query_one("#add_button", Button).press()
            await pilot.pause()
            client.create_collection.assert_called_once_with(
                display_name="My Collection", description="Things I use", category=None)
            client.close_session.assert_called_once()
            assert screen.created_guids == ["coll-guid-1"]
            # The form is cleared after a successful add
            assert screen.query_one("#collection_name", Input).value == ""

    @pytest.mark.asyncio
    async def test_add_user_identity_and_link(self, mock_egeria):
        client = mock_egeria.return_value
        client.create_user_identity.return_value = "uid-guid-1"
        app = ScreenTestHostApp(lambda: AddUserIdentityScreen("user_identity_table", "user-guid-123"))
        async with app.run_test() as pilot:
            self._fill(app.target_screen, {"user_identity_user_id": "erinoverview"})
            app.target_screen.action_add_element()
            await pilot.pause()
            props = client.create_user_identity.call_args.kwargs["body"]["properties"]
            assert props["class"] == "UserIdentityProperties"
            assert props["userId"] == "erinoverview"
            assert props["displayName"] == "erinoverview"
            client.link_identity_to_profile.assert_called_once_with(
                user_identity_guid="uid-guid-1", actor_profile_guid="user-guid-123")

    @pytest.mark.asyncio
    async def test_add_user_identity_without_link(self, mock_egeria):
        client = mock_egeria.return_value
        client.create_user_identity.return_value = "uid-guid-1"
        app = ScreenTestHostApp(lambda: AddUserIdentityScreen("user_identity_table", "user-guid-123"))
        async with app.run_test() as pilot:
            self._fill(app.target_screen, {"user_identity_user_id": "erinoverview"})
            app.target_screen.query_one("#link_to_profile").value = False
            await pilot.pause()
            app.target_screen.action_add_element()
            await pilot.pause()
            client.create_user_identity.assert_called_once()
            client.link_identity_to_profile.assert_not_called()

    @pytest.mark.asyncio
    async def test_failed_create_keeps_form(self, mock_egeria):
        from pyegeria import PyegeriaException
        client = mock_egeria.return_value
        client.create_collection.side_effect = PyegeriaException("Create failed")
        app = ScreenTestHostApp(lambda: AddCollectionScreen("my_collections_table", "user-guid-123"))
        async with app.run_test() as pilot:
            screen = app.target_screen
            self._fill(screen, {"collection_name": "My Collection",
                                "collection_description": "Things I use"})
            screen.action_add_element()
            await pilot.pause()
            assert screen.created_guids == []
            assert screen.query_one("#collection_name", Input).value == "My Collection"
            client.close_session.assert_called_once()


class TestMigratedAddScreens:
    """The Add screens built on BaseAddScreen call the right Egeria methods."""

    @pytest.fixture
    def mock_egeria(self):
        with patch("AddToElementsScreens.Egeria") as mock_egeria:
            client = mock_egeria.return_value
            client.__create_qualified_name__ = MagicMock(
                side_effect=lambda type_name, name: f"{type_name}::{name}")
            client.make_feedback_qn = MagicMock(
                side_effect=lambda kind, src, name: f"{kind}::{src}::{name}")
            yield mock_egeria

    async def _add(self, screen_cls, table_id, values, link=None):
        app = ScreenTestHostApp(lambda: screen_cls(table_id, "user-guid-123"))
        async with app.run_test() as pilot:
            screen = app.target_screen
            for field_id, value in values.items():
                screen.query_one(f"#{field_id}", Input).value = value
            if link is not None:
                screen.query_one("#link_to_profile").value = link
                await pilot.pause()
            screen.action_add_element()
            await pilot.pause()
            return screen

    @pytest.mark.asyncio
    async def test_add_todo(self, mock_egeria):
        await self._add(AddTodoScreen, "todos_table",
                        {"todo_name": "Review", "todo_description": "Review specs", "todo_priority": "2"})
        mock_egeria.return_value.create_my_todo.assert_called_once_with(
            todo_name="Review", description="Review specs", priority=2, activity_status="REQUESTED")

    @pytest.mark.asyncio
    async def test_add_todo_rejects_bad_priority(self, mock_egeria):
        await self._add(AddTodoScreen, "todos_table",
                        {"todo_name": "Review", "todo_description": "Review specs", "todo_priority": "High"})
        mock_egeria.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_blog_entry(self, mock_egeria):
        await self._add(AddBlogEntryScreen, "blogs_table",
                        {"blog_entry_name": "Day 1", "blog_entry_text": "Started"})
        body = mock_egeria.return_value.blog_my_activity.call_args.kwargs["body"]
        assert body["properties"]["class"] == "BlogEntryProperties"
        assert body["properties"]["displayName"] == "Day 1"
        assert body["properties"]["description"] == "Started"

    @pytest.mark.asyncio
    async def test_add_journal_entry(self, mock_egeria):
        await self._add(AddJournalEntryScreen, "journal_table",
                        {"journal_entry_title": "Notes", "journal_entry_text": "Text"})
        body = mock_egeria.return_value.journal_my_activity.call_args.kwargs["body"]
        assert body["properties"]["class"] == "JournalEntryProperties"

    @pytest.mark.asyncio
    async def test_add_community(self, mock_egeria):
        await self._add(AddCommunityScreen, "communities_table",
                        {"community_display_name": "Data Club", "community_description": "Chat"})
        body = mock_egeria.return_value.create_community.call_args.kwargs["body"]
        assert body["properties"]["class"] == "CommunityProperties"
        assert body["properties"]["qualifiedName"] == "Community::Data Club"

    @pytest.mark.asyncio
    async def test_add_project_and_join_team(self, mock_egeria):
        client = mock_egeria.return_value
        client.create_project.return_value = "proj-guid-1"
        await self._add(AddProjectScreen, "projects_table",
                        {"project_name": "Clinical", "project_description": "Trial data",
                         "project_classification": "Campaign", "project_start_date": "2026-10-01"})
        kwargs = client.create_project.call_args.kwargs
        assert kwargs["classification_name"] == "Campaign"
        assert kwargs["start_date"] == "2026-10-01"
        client.add_to_project_team.assert_called_once_with(project_guid="proj-guid-1", actor_guid="user-guid-123")

    @pytest.mark.asyncio
    async def test_add_project_rejects_bad_date(self, mock_egeria):
        await self._add(AddProjectScreen, "projects_table",
                        {"project_name": "Clinical", "project_description": "Trial data",
                         "project_start_date": "01/10/2026"})
        mock_egeria.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_role_and_appoint(self, mock_egeria):
        client = mock_egeria.return_value
        client.create_actor_role.return_value = "role-guid-1"
        await self._add(AddRoleScreen, "roles_table",
                        {"role_name": "Steward", "role_description": "Looks after data"})
        body = client.create_actor_role.call_args.kwargs["body"]
        assert body["properties"]["typeName"] == "PersonRole"
        client.link_person_role_to_profile.assert_called_once_with(
            person_role_guid="role-guid-1", person_profile_guid="user-guid-123")

    @pytest.mark.asyncio
    async def test_add_role_without_appointment(self, mock_egeria):
        client = mock_egeria.return_value
        await self._add(AddRoleScreen, "roles_table",
                        {"role_name": "Steward", "role_description": "Looks after data"}, link=False)
        client.create_actor_role.assert_called_once()
        client.link_person_role_to_profile.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_team_and_join(self, mock_egeria):
        client = mock_egeria.return_value
        client.create_actor_profile.return_value = "team-guid-1"
        client.create_actor_role.return_value = "member-role-guid-1"
        await self._add(AddTeamScreen, "teams_table",
                        {"team_name": "Platform", "team_description": "Runs Egeria"})
        body = client.create_actor_profile.call_args.kwargs["body"]
        assert body["properties"]["class"] == "TeamProperties"
        assert body["properties"]["typeName"] == "Team"
        role_body = client.create_actor_role.call_args.kwargs["body"]
        assert role_body["properties"]["typeName"] == "TeamMember"
        client.link_person_role_to_profile.assert_called_once_with(
            person_role_guid="member-role-guid-1", person_profile_guid="user-guid-123")
        client.link_assignment_scope.assert_called_once_with(
            scope_element_guid="team-guid-1", actor_guid="member-role-guid-1")

    @pytest.mark.asyncio
    async def test_add_team_without_joining(self, mock_egeria):
        client = mock_egeria.return_value
        await self._add(AddTeamScreen, "teams_table",
                        {"team_name": "Platform", "team_description": "Runs Egeria"}, link=False)
        client.create_actor_profile.assert_called_once()
        client.create_actor_role.assert_not_called()
        client.link_assignment_scope.assert_not_called()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("button_id,expected", [
        ("#choose_project_button", "project"),
        ("#choose_community_button", "community"),
    ])
    async def test_association_chooser(self, button_id, expected):
        app = ScreenTestHostApp(lambda: AddAssociationScreen("associations_table", "user-guid-123"))
        async with app.run_test() as pilot:
            app.target_screen.query_one(button_id, Button).press()
            await pilot.pause()
            assert app.dismissed_result == expected


class TestViewSubscriptionsScreen:
    """The Subscriptions screen lists the current user's own digital subscriptions."""

    @staticmethod
    def _subscription(guid, name, created_by, status="ACTIVE"):
        return {"elementHeader": {"guid": guid, "type": {"typeName": "DigitalSubscription"},
                                  "versions": {"createdBy": created_by}},
                "properties": {"displayName": name, "description": f"{name} desc", "contentStatus": status}}

    @pytest.mark.asyncio
    @patch("ViewSubscriptionsScreen.Egeria")
    async def test_lists_own_subscriptions(self, mock_egeria):
        client = mock_egeria.return_value
        client.find_collections.return_value = [
            self._subscription("sub-1", "Sales Feed", "garygeeke", "PROPOSED"),
            self._subscription("sub-2", "Not Mine", "erinoverview"),
        ]
        app = ScreenTestHostApp(ViewSubscriptionsScreen)
        async with app.run_test() as pilot:
            await pilot.pause()
            assert client.find_collections.call_args.kwargs["metadata_element_type_name"] == "DigitalSubscription"
            table = app.target_screen.query_one("#subscriptions_table", DataTable)
            assert table.row_count == 1
            assert table.get_row_at(0) == ["Sales Feed", "PROPOSED", "Sales Feed desc", "sub-1"]
            client.close_session.assert_called_once()

    @pytest.mark.asyncio
    @patch("ViewSubscriptionsScreen.Egeria")
    async def test_quit_closes_screen_not_app(self, mock_egeria):
        mock_egeria.return_value.find_collections.return_value = "No elements found"
        app = ScreenTestHostApp(ViewSubscriptionsScreen)
        async with app.run_test() as pilot:
            await pilot.press("q")
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
    async def test_edit_screens_query_one_source_table(self, screen_cls):
        """Verify edit screens query the source table from main screen when instantiated without args."""
        app = ScreenTestHostApp(lambda: screen_cls())
        async with app.run_test() as pilot:
            assert app.target_screen is not None
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
    async def test_tech_types_screen_default_config(self):
        app = ScreenTestHostApp(lambda: TechnologyTypesScreen())
        async with app.run_test() as pilot:
            assert app.target_screen is not None
            assert app.target_screen.user_name is not None

    @pytest.mark.asyncio
    async def test_tech_type_options_screen(self):
        templates = [{"displayName": "Tmpl1", "Catalog Template Name": "Tmpl1"}]
        processes = [{"displayName": "Proc1"}]
        app = ScreenTestHostApp(lambda: TechnologyTypeOptionsScreen("guid-1", "PostgreSQL", "DB", "user", "pwd", 100, templates, processes))
        async with app.run_test() as pilot:
            assert app.target_screen is not None

    @pytest.mark.asyncio
    async def test_tech_type_options_screen_default_config(self):
        app = ScreenTestHostApp(lambda: TechnologyTypeOptionsScreen())
        async with app.run_test() as pilot:
            assert app.target_screen is not None
            assert app.target_screen.user_name is not None

    @pytest.mark.asyncio
    async def test_tech_type_templates_screen(self):
        templates = [{"displayName": "Tmpl1", "Catalog Template Name": "Tmpl1", "placeholderPropertyValues": {"db_name": "mydb"}}]
        app = ScreenTestHostApp(lambda: TechnologyTypeTemplatesScreen("user", 100, "PostgreSQL", "DB", "template", "Tmpl1", templates))
        async with app.run_test() as pilot:
            assert app.target_screen is not None

    @pytest.mark.asyncio
    async def test_tech_type_templates_screen_default_config(self):
        app = ScreenTestHostApp(lambda: TechnologyTypeTemplatesScreen())
        async with app.run_test() as pilot:
            assert app.target_screen is not None

    @pytest.mark.asyncio
    async def test_tech_type_processes_screen(self):
        processes = [{"displayName": "Proc1", "additionalProperties": {"templateGUID": "tmpl-1"}}]
        app = ScreenTestHostApp(lambda: TechnologyTypeProcessesScreen("user", 100, "PostgreSQL", "DB", "process", "Proc1", processes))
        async with app.run_test() as pilot:
            assert app.target_screen is not None

    @pytest.mark.asyncio
    async def test_tech_type_processes_screen_default_config(self):
        app = ScreenTestHostApp(lambda: TechnologyTypeProcessesScreen())
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
    async def test_selection_overview_screen_default_config(self):
        app = ScreenTestHostApp(lambda: SelectionOverviewScreen())
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

    @pytest.mark.asyncio
    async def test_shop_for_data_screen_catalog_selection(self):
        t2 = DataTable(id="digital_product_catalog_table")
        app = ScreenTestHostApp(lambda: ShopForDataScreen(digital_product_catalog_table=t2))
        async with app.run_test() as pilot:
            target = app.target_screen.query_one("#digital_product_catalog_table", DataTable)
            target.add_columns("Name", "Desc", "QN", "GUID")
            row_key = target.add_row("Prod1", "Desc1", "Cat::Prod1", "guid-prod-999")
            target.move_cursor(row=0)
            await pilot.pause()
            app.target_screen.handle_digital_product_catalog_table_selection(
                DataTable.RowSelected(target, row_key=row_key, cursor_row=0)
            )
            await pilot.pause()
            assert app.dismissed_result == ["catalog", "Cat::Prod1", "Prod1", "guid-prod-999"]

    @pytest.mark.asyncio
    async def test_shop_for_data_screen_bookmark_highlighted_row(self):
        t2 = DataTable(id="digital_product_catalog_table")
        app = ScreenTestHostApp(lambda: ShopForDataScreen(digital_product_catalog_table=t2))
        app.bookmark_table_row = MagicMock(return_value=True)
        async with app.run_test() as pilot:
            target = app.target_screen.query_one("#digital_product_catalog_table", DataTable)
            target.add_columns("Name", "Desc", "QN", "GUID")
            row_key = target.add_row("Prod1", "Desc1", "Cat::Prod1", "guid-prod-999")
            target.focus()
            target.move_cursor(row=0)
            await pilot.pause()
            await pilot.press("k")
            await pilot.pause()
            app.bookmark_table_row.assert_called_once_with(target, row_key)

    @pytest.mark.asyncio
    async def test_shop_for_data_screen_default_config(self):
        app = ScreenTestHostApp(lambda: ShopForDataScreen())
        async with app.run_test() as pilot:
            app.target_screen.action_quit()
            await pilot.pause()
            assert app.dismissed_result == [210]

    @pytest.mark.asyncio
    async def test_shop_for_data_screen_subscribe_action(self):
        t2 = DataTable(id="digital_product_catalog_table")
        app = ScreenTestHostApp(lambda: ShopForDataScreen(digital_product_catalog_table=t2))
        async with app.run_test() as pilot:
            target = app.target_screen.query_one("#digital_product_catalog_table", DataTable)
            target.add_columns("Name", "Desc", "QN", "GUID")
            row_key = target.add_row("Prod1", "Desc1", "Cat::Prod1", "guid-prod-999")
            target.move_cursor(row=0)
            app.target_screen.data_table_highlighted = "digital_product_catalog_table"
            app.target_screen.row_highlighted = row_key
            app.target_screen.cursor_row_highlighted = 0
            await pilot.pause()

            app.target_screen.action_subscribe_to_data_source()
            await pilot.pause()
            assert app.dismissed_result is not None
            assert app.dismissed_result[0] == 211
            assert app.dismissed_result[4] == ["Prod1", "Desc1", "Cat::Prod1", "guid-prod-999"]


class TestMainScreen:
    """Tests for MainScreen table selection and edit actions."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "table_id",
        [
            "roles_table",
            "teams_table",
            "blogs_table",
            "journal_table",
            "todos_table",
            "user_identity_table",
            "associations_table",
            "my_collections_table",
        ],
    )
    async def test_main_screen_edit_selected_table(self, table_id):
        """Verify clicking any DataTable selects it and edit action targets that table."""
        class MockMainHostApp(App):
            def __init__(self):
                super().__init__()
                self.edited_calls = []

            async def on_mount(self):
                self.main_screen = MainScreen()
                self.install_screen(self.main_screen, name="main")
                await self.push_screen("main")

            def edit_tables(self, table_name, row_k):
                self.edited_calls.append((table_name, row_k))

        app = MockMainHostApp()
        async with app.run_test() as pilot:
            main_screen = app.main_screen

            # Populate tables with sample data
            for t_name in [
                "roles_table",
                "teams_table",
                "blogs_table",
                "journal_table",
                "todos_table",
                "user_identity_table",
                "associations_table",
                "my_collections_table",
            ]:
                t = main_screen.query_one(f"#{t_name}", DataTable)
                t.cursor_type = "row"
                t.add_columns("Col1", "Col2")
                t.add_row("val1", "val2", key=f"{t_name}_row_1")

            await pilot.pause()

            # Click on target table
            await pilot.click(f"#{table_id}")
            await pilot.pause()

            # Trigger edit table hotkey
            await pilot.press("ctrl+t")
            await pilot.pause()

            assert len(app.edited_calls) == 1
            assert app.edited_calls[0][0] == table_id
