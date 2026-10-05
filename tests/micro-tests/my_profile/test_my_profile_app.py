"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Full lifecycle, user functionality, and regression tests for MyProfileApp.

   Tests marked `live_capable` run against fakes by default and against a real
   Egeria view server when PYEG_LIVE_EGERIA=1 is set.
"""

from unittest.mock import MagicMock, AsyncMock, patch, PropertyMock
import pytest
from textual.widgets import Button, OptionList, DataTable
from textual.widgets._option_list import Option

from my_profile_app import MyProfileApp
from MainScreen import MainScreen
from CreateProfileScreen import CreateProfileScreen
from SplashScreen import SplashScreen
from UserIdentitiesScreen import UserIdentitiesScreen
from EditElementsScreens import EditProfileScreen
from egeria_backend import at_least, is_int, nonempty_str
from pyegeria import PyegeriaException


def stub_profile_client(backend, profile_data, identities, todos):
    """Keep MyProfileApp's on_mount off the network in fake mode.

    Any test that enters `app.run_test()` triggers on_mount ->
    _load_or_create_profile, which builds a real MyProfile client. Without this
    the test silently depends on a reachable server even when the behaviour
    under test is mocked. Live mode leaves the real client in place.
    """
    if backend.live:
        return backend.patch("my_profile_app.MyProfile")

    mock_mp = MagicMock()
    mock_mp.create_egeria_bearer_token.return_value = "token"
    mock_mp._async_get_my_profile = AsyncMock(return_value=profile_data)
    mock_mp.get_my_profile.side_effect = [
        profile_data,  # for get_my_profile in new_profile_return
        identities,  # for User-Identities lookup
    ]
    mock_mp.get_my_to_dos.return_value = todos
    # The My Collections lookup goes through the Egeria facade, not MyProfile
    mock_egeria = MagicMock()
    mock_egeria.find_collections.return_value = SAMPLE_COLLECTIONS
    backend.always_fake("my_profile_app.Egeria", returns=mock_egeria)
    return backend.always_fake("my_profile_app.MyProfile", returns=mock_mp)


def _collection(guid, name, created_by, qualified_name=None):
    return {
        "elementHeader": {"guid": guid, "type": {"typeName": "Collection"},
                          "versions": {"createdBy": created_by}},
        "properties": {"displayName": name, "description": f"{name} description",
                       "qualifiedName": qualified_name or f"Collection::{name}"},
    }


# Raw (JSON-format) find_collections results: only the first is the user's own,
# non-bookmarks collection, so My Collections should show exactly one row.
SAMPLE_COLLECTIONS = [
    _collection("coll-guid-mine", "Clinical Trials", "garygeeke"),
    _collection("coll-guid-other", "Someone Else's", "erinoverview"),
    _collection("coll-guid-bookmarks", "My Bookmarks", "garygeeke", "Bookmarks::garygeeke"),
]


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

    @pytest.mark.live_capable
    @pytest.mark.asyncio
    async def test_app_on_mount_success(
        self, backend, sample_profile_data, sample_user_identities, sample_todos_data
    ):
        # Live mode uses the real MyProfile against the configured view server.
        stub_profile_client(
            backend, sample_profile_data, sample_user_identities, sample_todos_data
        )

        app = MyProfileApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            backend.expect(app.karma_points, fake=150, live=is_int, label="karma_points")
            backend.expect(len(app.projects), fake=1, live=at_least(0), label="projects")
            backend.expect(len(app.teams), fake=1, live=at_least(0), label="teams")
            backend.expect(len(app.roles), fake=1, live=at_least(1), label="roles")
            backend.expect(len(app.todos), fake=1, live=at_least(0), label="todos")
            backend.expect(
                app.user_GUID, fake="profile-guid-12345", live=nonempty_str, label="user_GUID"
            )

            main_screen = app.get_screen("main")
            for table_id, fake_rows in (
                ("#projects_table", 1),
                ("#my_collections_table", 1),
                ("#roles_table", 1),
                ("#teams_table", 1),
                ("#todos_table", 1),
            ):
                table = main_screen.query_one(table_id, DataTable)
                backend.expect(
                    table.row_count, fake=fake_rows, live=at_least(0), label=table_id
                )
            blogs_table = main_screen.query_one("#blogs_table", DataTable)
            assert blogs_table.row_count >= 1

    @pytest.mark.asyncio
    async def test_app_on_mount_prompt_create_profile(self, backend):
        # Always faked: a live server cannot be asked for a user with no profile.
        mock_mp = MagicMock()
        mock_mp.create_egeria_bearer_token.return_value = "token"
        mock_mp._async_get_my_profile = AsyncMock(return_value=[])
        backend.always_fake("my_profile_app.MyProfile", returns=mock_mp)

        app = MyProfileApp()
        async with app.run_test() as pilot:
            # Wait for the splash screen to be pushed. Match on type: the screen
            # itself has no id (id="splash" is on its Header widget).
            for _ in range(10):
                if isinstance(app.screen, SplashScreen):
                    break
                await pilot.pause(0.1)
            assert isinstance(app.screen, SplashScreen)

            # "Continue to App" dismisses with None -> mainline's no-new-user branch
            # (pressed directly: at the default 80x24 test size the button is off-screen)
            app.screen.query_one("#continue", Button).press()
            await pilot.pause()

            # Wait for the async task to finish and the callback to be processed
            # and the new screen to be pushed.
            for _ in range(50):
                if isinstance(app.screen, CreateProfileScreen):
                    break
                await pilot.pause(0.1)

            assert isinstance(app.screen, CreateProfileScreen)

    @pytest.mark.asyncio
    async def test_splash_escape_still_prompts_create_profile(self, backend):
        """Escape on the splash screen must dismiss it (running mainline), not pop it."""
        mock_mp = MagicMock()
        mock_mp.create_egeria_bearer_token.return_value = "token"
        mock_mp._async_get_my_profile = AsyncMock(return_value=[])
        backend.always_fake("my_profile_app.MyProfile", returns=mock_mp)

        app = MyProfileApp()
        async with app.run_test() as pilot:
            for _ in range(10):
                if isinstance(app.screen, SplashScreen):
                    break
                await pilot.pause(0.1)
            assert isinstance(app.screen, SplashScreen)
            await pilot.press("escape")
            for _ in range(50):
                if isinstance(app.screen, CreateProfileScreen):
                    break
                await pilot.pause(0.1)
            assert isinstance(app.screen, CreateProfileScreen)

    @pytest.mark.asyncio
    async def test_app_load_profile_exception_exits_402(self, backend):
        # Always faked: exercises the app's error handling, not the server's.
        mock_mp = MagicMock()
        mock_mp.create_egeria_bearer_token.return_value = "token"
        mock_mp._async_get_my_profile = AsyncMock(side_effect=PyegeriaException("Server error"))
        backend.always_fake("my_profile_app.MyProfile", returns=mock_mp)

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
        """Closing a status screen returns to the main screen; it must not end the app."""
        app = MyProfileApp()
        app.exit = MagicMock()
        app.show_main_screen = MagicMock()
        app.status_callback(200)
        app.exit.assert_not_called()
        app.show_main_screen.assert_called_once()

    @pytest.mark.asyncio
    async def test_change_user_updates_settings_for_screens(self):
        """After Change User, screens that read pyegeria settings must see the new user."""
        from pyegeria import settings
        from AddToElementsScreens import AddTodoScreen
        saved = (settings.User_Profile.user_name, settings.User_Profile.user_pwd)
        app = MyProfileApp()
        app._load_or_create_profile = AsyncMock()
        app.refresh_bindings = MagicMock()
        try:
            await app.mainline(["erinoverview", "erin-pwd"])
            assert (app.user_name, app.user_password) == ("erinoverview", "erin-pwd")
            screen = AddTodoScreen("todos_table", "user-guid-123")
            assert (screen.user_name, screen.user_password) == ("erinoverview", "erin-pwd")
            app._load_or_create_profile.assert_awaited_once()
        finally:
            settings.User_Profile.user_name, settings.User_Profile.user_pwd = saved

    @pytest.mark.asyncio
    async def test_ctrl_k_bookmarks_selected_row(
        self, backend, sample_profile_data, sample_user_identities, sample_todos_data
    ):
        stub_profile_client(backend, sample_profile_data, sample_user_identities, sample_todos_data)
        app = MyProfileApp()
        app.bookmark_table_row = MagicMock(return_value=True)
        async with app.run_test(size=(180, 50)) as pilot:
            for _ in range(20):
                if isinstance(app.screen, SplashScreen):
                    break
                await pilot.pause(0.1)
            app.screen.query_one("#continue", Button).press()
            await pilot.pause(0.3)
            main = app.get_screen("main")
            table = main.query_one("#roles_table", DataTable)
            table.focus()
            await pilot.pause()
            await pilot.press("ctrl+k")
            await pilot.pause()
            app.bookmark_table_row.assert_called_once()
            called_table, row_key = app.bookmark_table_row.call_args.args
            assert called_table is table and row_key is not None

    def test_roles_row_selection_is_registered(self):
        """The roles_table RowSelected handler must be one Textual actually dispatches."""
        handlers = MyProfileApp._decorated_handlers.get(DataTable.RowSelected, [])
        assert any(method.__name__ == "_on_roles_row_selected" for method, _ in handlers)

    def test_roles_row_selected_delegates_to_mixin(self):
        app = MyProfileApp()
        app.handle_roles_table_row_selection = MagicMock()
        event = MagicMock()
        app._on_roles_row_selected(event)
        app.handle_roles_table_row_selection.assert_called_once_with(event)

    @pytest.mark.parametrize("returned", [200, 400, None])
    def test_add_comment_callback_ignores_cancel(self, returned):
        """Cancel/quit/no-selection returns are not errors and make no Egeria call."""
        app = MyProfileApp()
        with patch("my_profile_app.Egeria") as mock_egeria:
            assert app.add_comment_callback(returned) is None
            mock_egeria.assert_not_called()

    def test_add_comment_callback_success(self):
        app = MyProfileApp()
        app.notify = MagicMock()
        with patch("my_profile_app.Egeria") as mock_egeria:
            client = mock_egeria.return_value
            client.add_comment_to_element.return_value = "comment-guid-1"
            assert app.add_comment_callback(["Nice", "question", "elem-guid-1"]) == 200
            client.add_comment_to_element.assert_called_once_with(
                element_guid="elem-guid-1", comment="Nice", comment_type="QUESTION")
            client.close_session.assert_called_once()
            # No "Failed to add comment" notice after a successful add
            assert all("Failed" not in str(c) for c in app.notify.call_args_list)

    def test_show_main_screen(self):
        app = MyProfileApp()
        app.pop_screen = MagicMock()
        app.push_screen = MagicMock()
        app.is_mounted = True

        main_screen_obj = MainScreen()
        modal1 = MagicMock()
        modal2 = MagicMock()
        default_screen = MagicMock()

        # Case 1: Multiple screens above MainScreen - pop until MainScreen is active
        stack_list = [default_screen, main_screen_obj, modal1, modal2]
        with patch.object(MyProfileApp, "screen_stack", new_callable=PropertyMock) as mock_stack, \
             patch.object(MyProfileApp, "screen", new_callable=PropertyMock) as mock_screen:
            mock_stack.side_effect = lambda: stack_list
            mock_screen.side_effect = lambda: stack_list[-1] if stack_list else None

            def mock_pop():
                if len(stack_list) > 1:
                    stack_list.pop()
            app.pop_screen.side_effect = mock_pop

            app.show_main_screen()
            assert stack_list[-1] is main_screen_obj
            assert app.pop_screen.call_count == 2
            app.push_screen.assert_not_called()

        # Case 2: MainScreen is already active - do not pop MainScreen
        app.pop_screen.reset_mock()
        app.push_screen.reset_mock()
        stack_list_2 = [default_screen, main_screen_obj]
        with patch.object(MyProfileApp, "screen_stack", new_callable=PropertyMock) as mock_stack, \
             patch.object(MyProfileApp, "screen", new_callable=PropertyMock) as mock_screen:
            mock_stack.side_effect = lambda: stack_list_2
            mock_screen.side_effect = lambda: stack_list_2[-1] if stack_list_2 else None

            app.show_main_screen()
            assert app.pop_screen.call_count == 0
            assert len(stack_list_2) == 2
            app.push_screen.assert_not_called()

        # Case 3: Only default screen on stack - push 'main'
        app.pop_screen.reset_mock()
        app.push_screen.reset_mock()
        stack_list_3 = [default_screen]
        with patch.object(MyProfileApp, "screen_stack", new_callable=PropertyMock) as mock_stack, \
             patch.object(MyProfileApp, "screen", new_callable=PropertyMock) as mock_screen:
            mock_stack.side_effect = lambda: stack_list_3
            mock_screen.side_effect = lambda: stack_list_3[-1] if stack_list_3 else None

            app.show_main_screen()
            assert app.pop_screen.call_count == 0
            app.push_screen.assert_called_once_with("main")

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

    @pytest.mark.live_capable
    @pytest.mark.asyncio
    async def test_get_data_product_catalog_table_success(
        self, backend, sample_profile_data, sample_user_identities, sample_todos_data
    ):
        stub_profile_client(
            backend, sample_profile_data, sample_user_identities, sample_todos_data
        )
        mock_exec = backend.patch(
            "my_profile_app.exec_report_spec",
            returns={
                "kind": "data",
                "data": [
                    {
                        "Display Name": "Catalog 1",
                        "Description": "Desc 1",
                        "Qualified Name": "Cat::1",
                    }
                ],
            },
        )
        app = MyProfileApp()
        async with app.run_test():
            rc = app.get_data_product_catalog_table()
            assert rc == 200
            assert mock_exec.called
            assert app.digital_product_catalog_table is not None
            backend.expect(
                app.digital_product_catalog_table.row_count,
                fake=1,
                live=at_least(1),
                label="catalog rows",
            )

    @pytest.mark.asyncio
    async def test_get_data_product_catalog_table_empty(
        self, backend, sample_profile_data, sample_user_identities, sample_todos_data
    ):
        # Always faked: an empty catalog is a server-state the live instance
        # cannot be asked to produce.
        stub_profile_client(
            backend, sample_profile_data, sample_user_identities, sample_todos_data
        )
        backend.always_fake("my_profile_app.exec_report_spec", returns={"kind": "empty", "data": []})
        app = MyProfileApp()
        async with app.run_test():
            rc = app.get_data_product_catalog_table()
            assert rc == 200
            assert app.digital_product_catalog_table is not None
            assert app.digital_product_catalog_table.row_count == 1
