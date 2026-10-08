""" python

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file is a unit test for my_egeria.


"""

import pytest
from unittest.mock import patch
from textual.app import App
from textual.widgets import Input, Button
from my_egeria.screens.login_screen import LoginScreen


class LoginApp(App):
    """Minimal harness to run LoginScreen in isolation."""
    pass


# @pytest.mark.asyncio
# async def test_successful_login():
#     """A valid connection should move past the login screen."""
#     with patch(
#         "my_egeria.services.egeria_connection.connect_to_egeria", return_value=True
#     ):
#         app = LoginApp()
#         async with app.run_test() as pilot:
#             await pilot.app.push_screen(LoginScreen())
#             # Wait for the screen to be pushed and settled
#             while not pilot.app.query("#username"):
#                 await pilot.pause()
#             
#             # Fill in username and password
#             pilot.app.query_one("#username", Input).value = "demo_user"
#             pilot.app.query_one("#password", Input).value = "demo_pass"
# 
#             # Click the login button
#             await pilot.click(pilot.app.query_one("#login_button", Button))
# 
#             # After successful login, we shouldn't still be on LoginScreen
#             assert not isinstance(pilot.app.screen, LoginScreen)
# 
# 
# @pytest.mark.asyncio
# async def test_failed_login():
#     """An invalid connection should keep us on the login screen."""
#     with patch(
#         "my_egeria.services.egeria_connection.connect_to_egeria", return_value=False
#     ):
#         app = LoginApp()
#         async with app.run_test() as pilot:
#             await pilot.app.push_screen(LoginScreen())
#             while not pilot.app.query("#username"):
#                 await pilot.pause()
#             pilot.app.query_one("#username", Input).value = "bad_user"
#             pilot.app.query_one("#password", Input).value = "bad_pass"
# 
#             await pilot.click(pilot.app.query_one("#login_button", Button))
# 
#             # Auth failed → still on LoginScreen
#             assert isinstance(pilot.app.screen, LoginScreen)
