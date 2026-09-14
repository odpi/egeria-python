"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Unit tests for team_roles_handler module.

   Tests marked `live_capable` run against fakes by default and against a real
   Egeria view server when PYEG_LIVE_EGERIA=1 is set.
"""

from unittest.mock import MagicMock
import pytest

from team_roles_handler import TeamRolesMixin
from MyTeamScreen import MyTeam
from ShopForDataScreen import ShopForDataScreen
from StatusScreen import StatusScreen
from egeria_backend import at_least, nonempty_str
from pyegeria import PyegeriaException


class DummyTeamRolesApp(TeamRolesMixin):
    """Test harness implementing TeamRolesMixin."""

    def __init__(self, backend=None):
        self.pushed_screens = []
        self.exit_code = None
        self.shown_main_screen = False
        self.log_messages = []
        self.user_name = "garygeeke"
        self.user_password = "secret"
        self.view_server = "qs-view-server"
        self.platform_url = "https://127.0.0.1:9443"
        if backend is not None:
            backend.apply_connection(self)
        self.team_members = []
        self.widgets = {}
        self.screen = MagicMock()

    def log(self, msg, *args, **kwargs):
        self.log_messages.append(str(msg))

    def _show_main_screen(self):
        self.shown_main_screen = True

    def push_screen(self, screen, callback=None):
        self.pushed_screens.append((screen, callback))

    def exit(self, code):
        self.exit_code = code

    def status_callback(self, *args, **kwargs):
        pass

    def shop_for_data_callback(self, *args, **kwargs):
        pass

    def query_one(self, selector, *args, **kwargs):
        if selector in self.widgets:
            return self.widgets[selector]
        mock_widget = MagicMock()
        return mock_widget


class TestTeamRolesMixin:
    """Tests for TeamRolesMixin methods."""

    def test_handle_roles_table_row_selection_non_team(self):
        app = DummyTeamRolesApp()
        mock_event = MagicMock()
        mock_table = MagicMock()
        mock_table.get_row.return_value = ["DataSteward", "DataSteward", "Desc", "guid1"]
        mock_event.data_table = mock_table
        mock_event.row_key = "k1"

        res = app.handle_roles_table_row_selection(mock_event)
        assert res == 201
        assert len(app.pushed_screens) == 0

    @pytest.mark.live_capable
    def test_handle_roles_table_row_selection_team_leader(
        self, backend, sample_team_members_response, request
    ):
        app = DummyTeamRolesApp(backend)
        backend.patch("team_roles_handler.exec_report_spec", returns=sample_team_members_response)

        # Live mode needs a role name the server actually knows: find_team_members
        # searches on everything after the first '::' segment.
        role_name = (
            request.getfixturevalue("live_team_role_name")
            if backend.live
            else "Department::101::TeamLeader"
        )

        mock_event = MagicMock()
        mock_table = MagicMock()
        mock_table.get_row.return_value = [role_name, "TeamLeader", "Desc", "guid1"]
        mock_event.data_table = mock_table
        mock_event.row_key = "k1"

        app.handle_roles_table_row_selection(mock_event)

        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, MyTeam)
        assert cb == app.my_team_callback
        backend.expect(len(app.team_members), fake=2, live=at_least(1), label="team_members")
        backend.expect(
            app.team_members[0],
            fake=["Gary Geeke", "TeamLeader", "profile-guid-12345"],
            live=lambda row: isinstance(row, list) and len(row) == 3,
            label="first team member",
        )

    @pytest.mark.live_capable
    def test_find_team_members_success(self, backend, sample_team_members_response, request):
        app = DummyTeamRolesApp(backend)
        backend.patch("team_roles_handler.exec_report_spec", returns=sample_team_members_response)

        role_name = (
            request.getfixturevalue("live_team_role_name")
            if backend.live
            else "Department::101::TeamLeader"
        )

        members, dname, qname, cat, desc = app.find_team_members(role_name)
        backend.expect(len(members), fake=2, live=at_least(1), label="members")
        backend.expect(dname, fake="IT Infrastructure Team", live=nonempty_str, label="display name")
        backend.expect(qname, fake="Team::IT_Infra", live=nonempty_str, label="qualified name")
        backend.expect(cat, fake="Operations", label="category")
        backend.expect(
            desc, fake="Team responsible for core infrastructure", label="description"
        )

    def test_find_team_members_pyegeria_exception(self, backend):
        # Always faked: injected failure, exercising the handler's error path.
        app = DummyTeamRolesApp(backend)
        backend.always_fake("team_roles_handler.exec_report_spec", side_effect=PyegeriaException("API Error"))

        members, dname, qname, cat, desc = app.find_team_members("Department::101::TeamLeader")
        assert members == []
        assert app.exit_code == 440

    def test_find_team_members_empty_kind(self, backend):
        # Always faked: an 'empty' result is not something a live server can be asked for.
        app = DummyTeamRolesApp(backend)
        backend.always_fake("team_roles_handler.exec_report_spec", returns={"kind": "empty"})

        members, dname, qname, cat, desc = app.find_team_members("Department::101::TeamLeader")
        assert members == []
        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, StatusScreen)

    def test_find_team_members_no_members_found(self, backend):
        # Always faked: as above, a team with no members is a fixed fake state.
        app = DummyTeamRolesApp(backend)
        backend.always_fake("team_roles_handler.exec_report_spec", returns={"kind": "data", "data": []})

        members, dname, qname, cat, desc = app.find_team_members("Department::101::TeamLeader")
        assert members == []
        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, StatusScreen)

    def test_my_team_callback(self):
        app = DummyTeamRolesApp()
        app.my_team_callback(200)
        assert app.shown_main_screen is True

        app.shown_main_screen = False
        app.my_team_callback(400)
        assert app.shown_main_screen is True

    def test_search_for_term_callback_200(self):
        app = DummyTeamRolesApp()
        app.search_for_term_callback(200)
        assert app.shown_main_screen is True

    def test_search_for_term_callback_201_shop_for_data(self):
        app = DummyTeamRolesApp()
        app.search_for_term_callback(201)
        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, ShopForDataScreen)

    def test_search_for_term_callback_error(self):
        app = DummyTeamRolesApp()
        app.search_for_term_callback(500)
        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, StatusScreen)

    @pytest.mark.live_capable
    def test_display_glossary_term_details_success(self, backend):
        app = DummyTeamRolesApp(backend)
        backend.patch(
            "team_roles_handler.exec_report_spec",
            returns={"kind": "data", "data": {"displayName": "Test Term"}},
        )
        mock_container = MagicMock()
        app.screen.query_one.return_value = mock_container

        # '*' matches whatever terms the live glossary holds; the fake ignores it.
        ret = app.display_glossary_term_details("*" if backend.live else "Test Term")
        assert ret == 200
        # The handler mounts one Static per field of a dict payload; a live JSON
        # payload is a list, which mounts nothing, so only assert on the fake.
        if not backend.live:
            mock_container.mount.assert_called_once()

    def test_display_glossary_term_details_pyegeria_exception(self, backend):
        # Always faked: injected failure, exercising the handler's error path.
        app = DummyTeamRolesApp(backend)
        backend.always_fake("team_roles_handler.exec_report_spec", side_effect=PyegeriaException("API Error"))

        ret = app.display_glossary_term_details("Test Term")
        assert ret == 440
        assert app.exit_code == 440

    def test_display_glossary_term_details_empty(self, backend):
        # Always faked: a null response is not a live-server state.
        app = DummyTeamRolesApp(backend)
        backend.always_fake("team_roles_handler.exec_report_spec", returns=None)

        ret = app.display_glossary_term_details("Test Term")
        assert ret == 440
        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, StatusScreen)
