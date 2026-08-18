"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Unit tests for team_roles_handler module.
"""

from unittest.mock import MagicMock, patch
import pytest
from textual.widgets import DataTable

from team_roles_handler import TeamRolesMixin
from MyTeamScreen import MyTeam
from ShopForDataScreen import ShopForDataScreen
from StatusScreen import StatusScreen
from pyegeria import PyegeriaException


class DummyTeamRolesApp(TeamRolesMixin):
    """Test harness implementing TeamRolesMixin."""

    def __init__(self):
        self.pushed_screens = []
        self.exit_code = None
        self.shown_main_screen = False
        self.log_messages = []
        self.user_name = "garygeeke"
        self.user_password = "secret"
        self.view_server = "qs-view-server"
        self.platform_url = "https://127.0.0.1:9443"
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

    @patch("team_roles_handler.exec_report_spec")
    def test_handle_roles_table_row_selection_team_leader(self, mock_exec, sample_team_members_response):
        app = DummyTeamRolesApp()
        mock_exec.return_value = sample_team_members_response

        mock_event = MagicMock()
        mock_table = MagicMock()
        mock_table.get_row.return_value = ["Department::101::TeamLeader", "TeamLeader", "Desc", "guid1"]
        mock_event.data_table = mock_table
        mock_event.row_key = "k1"

        app.handle_roles_table_row_selection(mock_event)

        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, MyTeam)
        assert cb == app.my_team_callback
        assert len(app.team_members) == 2
        assert app.team_members[0] == ["Gary Geeke", "TeamLeader", "profile-guid-12345"]

    @patch("team_roles_handler.exec_report_spec")
    def test_find_team_members_success(self, mock_exec, sample_team_members_response):
        app = DummyTeamRolesApp()
        mock_exec.return_value = sample_team_members_response

        members, dname, qname, cat, desc = app.find_team_members("Department::101::TeamLeader")
        assert len(members) == 2
        assert dname == "IT Infrastructure Team"
        assert qname == "Team::IT_Infra"
        assert cat == "Operations"
        assert desc == "Team responsible for core infrastructure"

    @patch("team_roles_handler.exec_report_spec")
    def test_find_team_members_pyegeria_exception(self, mock_exec):
        app = DummyTeamRolesApp()
        mock_exec.side_effect = PyegeriaException("API Error")

        members, dname, qname, cat, desc = app.find_team_members("Department::101::TeamLeader")
        assert members == []
        assert app.exit_code == 440

    @patch("team_roles_handler.exec_report_spec")
    def test_find_team_members_empty_kind(self, mock_exec):
        app = DummyTeamRolesApp()
        mock_exec.return_value = {"kind": "empty"}

        members, dname, qname, cat, desc = app.find_team_members("Department::101::TeamLeader")
        assert members == []
        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, StatusScreen)

    @patch("team_roles_handler.exec_report_spec")
    def test_find_team_members_no_members_found(self, mock_exec):
        app = DummyTeamRolesApp()
        mock_exec.return_value = {"kind": "data", "data": []}

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

    @patch("team_roles_handler.exec_report_spec")
    def test_display_glossary_term_details_success(self, mock_exec):
        app = DummyTeamRolesApp()
        mock_exec.return_value = {"kind": "data", "data": {"displayName": "Test Term"}}
        mock_container = MagicMock()
        app.screen.query_one.return_value = mock_container

        ret = app.display_glossary_term_details("Test Term")
        assert ret == 200
        mock_container.mount.assert_called_once()

    @patch("team_roles_handler.exec_report_spec")
    def test_display_glossary_term_details_pyegeria_exception(self, mock_exec):
        app = DummyTeamRolesApp()
        mock_exec.side_effect = PyegeriaException("API Error")

        ret = app.display_glossary_term_details("Test Term")
        assert ret == 440
        assert app.exit_code == 440

    @patch("team_roles_handler.exec_report_spec")
    def test_display_glossary_term_details_empty(self, mock_exec):
        app = DummyTeamRolesApp()
        mock_exec.return_value = None

        ret = app.display_glossary_term_details("Test Term")
        assert ret == 440
        assert len(app.pushed_screens) == 1
        screen, cb = app.pushed_screens[0]
        assert isinstance(screen, StatusScreen)
