"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Full lifecycle, user functionality, and regression tests for MyProfileApp.
"""

from unittest.mock import MagicMock, AsyncMock, patch, PropertyMock
import pytest
from textual.widgets import OptionList, DataTable
from textual.widgets._option_list import Option

from my_profile_app import MyProfileApp
from CreateProfileScreen import CreateProfileScreen
from UserIdentitiesScreen import UserIdentitiesScreen
from EditElementsScreens import EditProfileScreen
from pyegeria import PyegeriaException


class TestMyProfileAppLifecycle:
    """Tests for MyProfileApp lifecycle, initialization, and data loading."""

    def test_app_initialization(self):
        app = MyProfileApp()
        assert app.user_name is not None
        assert app.user_password is not None
        assert app.view_server is not None
        assert app.platform_url is not None
        assert app.projects == []
        assert app.teams == []
        assert app.roles == []
        assert app.todos == []
        assert app.karma_points == 0

    @pytest.mark.asyncio
    @patch("my_profile_app.MyProfile")
    async def test_app_on_mount_success(self, mock_mp_cls, sample_profile_data, sample_user_identities, sample_todos_data):
        mock_mp = MagicMock()
        mock_mp.create_egeria_bearer_token.return_value = "token"
        mock_mp._async_get_my_profile = AsyncMock(return_value=sample_profile_data)
        mock_mp.get_my_profile.side_effect = [
            sample_profile_data,  # for get_my_profile in new_profile_return
            sample_user_identities,  # for User-Identities lookup
        ]
        mock_mp.get_my_to_dos.return_value = sample_todos_data
        mock_mp_cls.return_value = mock_mp

        app = MyProfileApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            assert app.karma_points == 150
            assert len(app.projects) == 1
            assert len(app.teams) == 1
            assert len(app.roles) == 1
            assert len(app.todos) == 1
            assert app.user_GUID == "profile-guid-12345"

            main_screen = app.get_screen("main")
            roles_table = main_screen.query_one("#roles_table", DataTable)
            assert roles_table.row_count == 1
            teams_table = main_screen.query_one("#teams_table", DataTable)
            assert teams_table.row_count == 1
            todos_table = main_screen.query_one("#todos_table", DataTable)
            assert todos_table.row_count == 1
            blogs_table = main_screen.query_one("#blogs_table", DataTable)
            assert blogs_table.row_count >= 1

    @pytest.mark.asyncio
    @patch("my_profile_app.MyProfile")
    async def test_app_on_mount_prompt_create_profile(self, mock_mp_cls):
        mock_mp = MagicMock()
        mock_mp.create_egeria_bearer_token.return_value = "token"
        mock_mp._async_get_my_profile = AsyncMock(return_value=[])
        mock_mp_cls.return_value = mock_mp

        app = MyProfileApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            assert isinstance(app.screen, CreateProfileScreen)

    @pytest.mark.asyncio
    @patch("my_profile_app.MyProfile")
    async def test_app_load_profile_exception_exits_402(self, mock_mp_cls):
        mock_mp = MagicMock()
        mock_mp.create_egeria_bearer_token.return_value = "token"
        mock_mp._async_get_my_profile = AsyncMock(side_effect=PyegeriaException("Server error"))
        mock_mp_cls.return_value = mock_mp

        app = MyProfileApp()
        app.exit = MagicMock()
        await app._load_or_create_profile()
        app.exit.assert_called_once_with(402)

    def test_new_profile_return_error_code(self):
        app = MyProfileApp()
        app.exit = MagicMock()
        app.new_profile_return(401)
        app.exit.assert_called_once_with(403)

    def test_new_profile_return_empty_profile_exits_413(self):
        app = MyProfileApp()
        app.my_profile_inst = MagicMock()
        app.my_profile_inst.get_my_profile.return_value = []
        app.exit = MagicMock()
        app.new_profile_return(200)
        app.exit.assert_called_once_with(413)

    def test_new_profile_return_exception_exits_412(self):
        app = MyProfileApp()
        app.my_profile_inst = MagicMock()
        app.my_profile_inst.get_my_profile.side_effect = PyegeriaException("Retrieve failed")
        app.exit = MagicMock()
        app.new_profile_return(200)
        app.exit.assert_called_once_with(412)


class TestMyProfileAppActionsAndOptions:
    """Tests for actions, menu selections, and UI options in MyProfileApp."""

    def test_action_quit(self):
        app = MyProfileApp()
        app.exit = MagicMock()
        app.action_quit()
        app.exit.assert_called_once_with(200)

    @pytest.mark.asyncio
    async def test_action_refresh(self):
        app = MyProfileApp()
        app._load_or_create_profile = AsyncMock()
        app._populate_tables = AsyncMock()
        await app.action_refresh()
        app._load_or_create_profile.assert_called_once()
        app._populate_tables.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "option_name,handler_attr,screen_cls",
        [
            ("Technology Types", "handle_technology_types_option", None),
            ("User Identities", None, UserIdentitiesScreen),
            ("Catalogs/Shop for Data", "handle_shop_for_data_option", None),
            ("Edit Profile", None, EditProfileScreen),
        ],
    )
    async def test_handle_option_selected(self, option_name, handler_attr, screen_cls):
        app = MyProfileApp()
        app.user_profile = {"Full Name": "Gary Geeke"}
        app.push_screen = AsyncMock()

        event = MagicMock()
        event.option.prompt = option_name
        event.option.id = option_name.lower().replace(" ", "_")

        if handler_attr:
            setattr(app, handler_attr, AsyncMock())
            await app.handle_option_selected(event)
            getattr(app, handler_attr).assert_called_once()
        else:
            await app.handle_option_selected(event)
            assert app.push_screen.call_count == 1
            call_args = app.push_screen.call_args[0]
            assert isinstance(call_args[0], screen_cls)

    def test_status_callback(self):
        app = MyProfileApp()
        app.exit = MagicMock()
        app.status_callback(200)
        app.exit.assert_called_once_with(200)

    def test_show_main_screen(self):
        app = MyProfileApp()
        app.pop_screen = MagicMock()
        app.push_screen = MagicMock()
        app.is_mounted = True

        # When screen stack has multiple screens, pop until only 1 remains
        stack_list = [MagicMock(), MagicMock(), MagicMock()]
        with patch.object(MyProfileApp, "screen_stack", new_callable=PropertyMock) as mock_stack:
            def side_effect():
                if stack_list:
                    return stack_list
                return []
            mock_stack.side_effect = lambda: stack_list

            def mock_pop():
                if len(stack_list) > 1:
                    stack_list.pop()
            app.pop_screen.side_effect = mock_pop

            app.show_main_screen()
            assert len(stack_list) == 1
            assert app.pop_screen.call_count == 2

        # Alias _show_main_screen test
        stack_list_2 = [MagicMock(), MagicMock()]
        with patch.object(MyProfileApp, "screen_stack", new_callable=PropertyMock) as mock_stack:
            mock_stack.side_effect = lambda: stack_list_2
            def mock_pop_2():
                if len(stack_list_2) > 1:
                    stack_list_2.pop()
            app.pop_screen.side_effect = mock_pop_2
            app._show_main_screen()
            assert len(stack_list_2) == 1

    def test_utility_delegation_wrappers(self):
        app = MyProfileApp()
        # Clean structure
        res = app.clean_structure({"k": "v specificationMermaidGraph extra"})
        assert res == {"k": "v "}

        # Bools to strings
        res = app.bools_to_strings({"active": True, "count": 5})
        assert res == {"active": "True", "count": 5}

        # Truncate at sequence
        res, term = app.truncate_at_sequence("hello specificationMermaidGraph world")
        assert res == "hello "
        assert term is True

        # Extract glossary terms
        res = app.extract_glossary_terms("GlossaryTerm::TermA, other")
        assert res == ["TermA"]
