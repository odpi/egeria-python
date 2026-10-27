"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Tests for waiting on an unreachable Egeria at startup, and for changing the logged in user.
"""

from unittest.mock import MagicMock, AsyncMock, patch
import pytest
from textual.app import App
from textual.widgets import Button, Input, Static

from my_egeria.DemoCode.My_Profile.my_egeria import MyProfileApp
from ChangeUserScreen import ChangeUserScreen
from ConnectionErrorScreen import ConnectionErrorScreen, RETRY_INTERVAL
from SplashScreen import SplashScreen
from profile_utils import check_egeria_access
from pyegeria import PyegeriaConnectionException

BAD_CREDENTIALS_BODY = (
    '{"class":"FFDCResponseBase","relatedHTTPCode":401,'
    '"exceptionErrorMessage":"User authentication failed for user: garygeeke - Bad credentials"}'
)


class HostApp(App):
    """Pushes one screen and records what it dismisses with."""

    def __init__(self, screen_factory):
        super().__init__()
        self.screen_factory = screen_factory
        self.target_screen = None
        self.dismissed_result = "not dismissed"

    async def on_mount(self):
        self.target_screen = self.screen_factory()

        def _cb(result):
            self.dismissed_result = result

        await self.push_screen(self.target_screen, callback=_cb)


class TestCheckEgeriaAccess:
    """check_egeria_access must tell 'unreachable' and 'bad credentials' apart from success."""

    @patch("pyegeria.Egeria")
    def test_good_credentials(self, mock_egeria):
        mock_egeria.return_value.create_egeria_bearer_token.return_value = "eyJhbGciOi.jwt.token"
        assert check_egeria_access("qs-view-server", "https://localhost:9443", "garygeeke", "secret") is None
        mock_egeria.return_value.close_session.assert_called_once()

    @patch("pyegeria.Egeria")
    def test_unreachable_platform(self, mock_egeria):
        mock_egeria.side_effect = PyegeriaConnectionException(None, None, ConnectionError("refused"))
        error = check_egeria_access("qs-view-server", "https://localhost:9443", "garygeeke", "secret")
        assert error == "Unable to connect to the Egeria platform at https://localhost:9443."

    @patch("pyegeria.Egeria")
    def test_bad_credentials_body_is_not_a_token(self, mock_egeria):
        mock_egeria.return_value.create_egeria_bearer_token.return_value = BAD_CREDENTIALS_BODY
        error = check_egeria_access("qs-view-server", "https://localhost:9443", "garygeeke", "wrong")
        assert "Bad credentials" in error


class TestConnectionErrorScreen:

    @pytest.mark.asyncio
    @patch("ConnectionErrorScreen.check_egeria_access", return_value=None)
    async def test_retry_succeeds_dismisses_200(self, mock_check):
        app = HostApp(lambda: ConnectionErrorScreen("Unable to connect"))
        async with app.run_test() as pilot:
            app.target_screen.action_retry_now()
            await pilot.pause()
            assert app.dismissed_result == 200

    @pytest.mark.asyncio
    @patch("ConnectionErrorScreen.check_egeria_access", return_value="Still down")
    async def test_retry_fails_stays_and_shows_reason(self, mock_check):
        app = HostApp(lambda: ConnectionErrorScreen("Unable to connect"))
        async with app.run_test() as pilot:
            screen = app.target_screen
            screen.action_retry_now()
            await pilot.pause()
            assert app.dismissed_result == "not dismissed"
            assert screen.attempts == 1
            assert screen.countdown == RETRY_INTERVAL
            assert "Still down" in str(screen.query_one("#connection_error_reason", Static).render())

    @pytest.mark.asyncio
    @patch("ConnectionErrorScreen.check_egeria_access", return_value=None)
    async def test_countdown_triggers_retry(self, mock_check):
        app = HostApp(lambda: ConnectionErrorScreen("Unable to connect"))
        async with app.run_test() as pilot:
            app.target_screen.countdown = 1
            app.target_screen._tick()
            await pilot.pause()
            mock_check.assert_called_once()
            assert app.dismissed_result == 200

    @pytest.mark.asyncio
    @pytest.mark.parametrize("button_id,expected", [("change_user", 201), ("quit_app", 402)])
    @patch("ConnectionErrorScreen.check_egeria_access", return_value="down")
    async def test_buttons(self, mock_check, button_id, expected):
        app = HostApp(lambda: ConnectionErrorScreen("Unable to connect"))
        async with app.run_test(size=(120, 40)) as pilot:
            app.target_screen.query_one(f"#{button_id}", Button).press()
            await pilot.pause()
            assert app.dismissed_result == expected


class TestChangeUserScreen:

    async def _submit(self, pilot, app, user, password):
        app.target_screen.query_one("#new_user_name", Input).value = user
        app.target_screen.query_one("#new_user_password", Input).value = password
        app.target_screen.handle_submit_new_user()
        await pilot.pause()

    @pytest.mark.asyncio
    @patch("ChangeUserScreen.check_egeria_access", return_value=None)
    async def test_valid_credentials_dismiss_with_user_and_password(self, mock_check):
        app = HostApp(ChangeUserScreen)
        async with app.run_test() as pilot:
            await self._submit(pilot, app, " erinoverview ", "secret")
            assert app.dismissed_result == ["erinoverview", "secret"]
            assert mock_check.call_args[0][2:] == ("erinoverview", "secret")

    @pytest.mark.asyncio
    @patch("ChangeUserScreen.check_egeria_access", return_value="Bad credentials")
    async def test_rejected_credentials_stay_on_screen(self, mock_check):
        app = HostApp(ChangeUserScreen)
        async with app.run_test() as pilot:
            await self._submit(pilot, app, "erinoverview", "wrong")
            assert app.dismissed_result == "not dismissed"

    @pytest.mark.asyncio
    @patch("ChangeUserScreen.check_egeria_access")
    async def test_missing_fields_not_checked(self, mock_check):
        app = HostApp(ChangeUserScreen)
        async with app.run_test() as pilot:
            await self._submit(pilot, app, "erinoverview", "")
            mock_check.assert_not_called()
            assert app.dismissed_result == "not dismissed"

    @pytest.mark.asyncio
    async def test_cancel_dismisses_200(self):
        app = HostApp(ChangeUserScreen)
        async with app.run_test() as pilot:
            await pilot.press("escape")
            assert app.dismissed_result == 200


class TestSplashChangeUser:

    @pytest.mark.asyncio
    async def test_change_user_button_opens_change_user_screen(self):
        app = HostApp(SplashScreen)
        async with app.run_test(size=(120, 40)) as pilot:
            app.target_screen.query_one("#change_user", Button).press()
            await pilot.pause()
            assert isinstance(app.screen, ChangeUserScreen)

    @pytest.mark.asyncio
    async def test_new_credentials_passed_on_cancel_stays(self):
        app = HostApp(SplashScreen)
        async with app.run_test() as pilot:
            app.target_screen.change_user_callback(200)
            await pilot.pause()
            assert app.dismissed_result == "not dismissed"
            app.target_screen.change_user_callback(["erinoverview", "secret"])
            await pilot.pause()
            assert app.dismissed_result == ["erinoverview", "secret"]


class TestAppConnectionAndUserChange:

    @pytest.mark.asyncio
    async def test_connection_failure_message_names_platform(self):
        app = MyProfileApp()
        with patch("my_egeria.DemoCode.My_Profile.my_egeria.MyProfile",
                   side_effect=PyegeriaConnectionException(None, None, ConnectionError("refused"))):
            assert await app._load_profile_and_populate() is False
        assert app.load_error == f"Unable to connect to the Egeria platform at {app.platform_url}."

    @pytest.mark.asyncio
    async def test_egeria_back_reloads_profile(self):
        app = MyProfileApp()
        app._load_or_create_profile = AsyncMock()
        await app.connection_error_callback(200)
        app._load_or_create_profile.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_change_user_from_error_screen(self):
        app = MyProfileApp()
        app.push_screen = AsyncMock()
        await app.connection_error_callback(201)
        assert isinstance(app.push_screen.call_args[0][0], ChangeUserScreen)
        assert app.push_screen.call_args.kwargs["callback"] == app.change_user_callback

    @pytest.mark.asyncio
    async def test_quit_from_error_screen_exits_402(self):
        app = MyProfileApp()
        app.exit = MagicMock()
        await app.connection_error_callback(402)
        app.exit.assert_called_once_with(402)

    @pytest.mark.asyncio
    async def test_cancel_change_user_while_disconnected_returns_to_error_screen(self):
        app = MyProfileApp()
        app.load_error = "Unable to connect"
        app.push_screen = AsyncMock()
        await app.change_user_callback(200)
        assert isinstance(app.push_screen.call_args[0][0], ConnectionErrorScreen)

    @pytest.mark.asyncio
    async def test_cancel_change_user_while_connected_does_nothing(self):
        app = MyProfileApp()
        app.push_screen = AsyncMock()
        app.change_user = AsyncMock()
        await app.change_user_callback(200)
        app.push_screen.assert_not_called()
        app.change_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_change_user_callback_switches_user(self):
        app = MyProfileApp()
        app.change_user = AsyncMock()
        await app.change_user_callback(["erinoverview", "secret"])
        app.change_user.assert_awaited_once_with("erinoverview", "secret")

    @pytest.mark.asyncio
    async def test_change_user_menu_option(self):
        app = MyProfileApp()
        app.push_screen = AsyncMock()
        event = MagicMock()
        event.option.prompt = "[] Change User"
        await app.handle_option_selected(event)
        assert isinstance(app.push_screen.call_args[0][0], ChangeUserScreen)
        assert app.push_screen.call_args.kwargs["callback"] == app.change_user_callback
