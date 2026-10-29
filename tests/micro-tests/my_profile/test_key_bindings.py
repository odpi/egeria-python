"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Guards the app-wide key binding convention so every My Profile screen behaves the same:
     escape  back one level (every screen except Main)
     q       the only plain-letter key: Main Menu on sub-screens, Quit on Main.
             Left off text-entry forms, where it would be typed into the Input instead.
     ctrl+*  every other action, one meaning per key (see docs/my_egeria_manual.md)
"""

import inspect

import pytest
from textual.app import App
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Input

import AddCommentScreen
import AddToElementsScreens
import CommunitiesScreen
import CommunityScreen
import CreateProfileScreen
import CreateSubscriptionRequestScreen
import EditElementsScreens
import FeedbackScreens
import GenericDataViewScreen
import MainScreen
import MyBookMarksScreen
import MyNetworkScreen
import MyTeamScreen
import SearchForTermScreen
import SelectionOverviewScreen
import ShopForDataScreen
import ShowCommentsScreen
import SplashScreen
import StatusScreen
import TechnologyTypeScreens
import UserIdentitiesScreen
import ViewSubscriptionsScreen
from my_egeria.DemoCode.My_Profile.my_egeria import MyProfileApp

MODULES = [
    AddCommentScreen, AddToElementsScreens, CommunitiesScreen, CommunityScreen, CreateProfileScreen, CreateSubscriptionRequestScreen,
    EditElementsScreens, FeedbackScreens, GenericDataViewScreen, MainScreen, MyBookMarksScreen,
    MyNetworkScreen, MyTeamScreen, SearchForTermScreen, SelectionOverviewScreen, ShopForDataScreen,
    ShowCommentsScreen, SplashScreen, StatusScreen, TechnologyTypeScreens, UserIdentitiesScreen,
    ViewSubscriptionsScreen,
]

SCREENS = sorted(
    {
        cls
        for module in MODULES
        for _, cls in inspect.getmembers(module, inspect.isclass)
        if issubclass(cls, Screen) and cls.__module__ == module.__name__
    },
    key=lambda c: c.__name__,
)

# ctrl+c is Textual's copy/quit, a terminal sends ctrl+i as Tab, ctrl+m/ctrl+j as Enter and
# ctrl+h as Backspace, and ctrl+p opens the command palette. "return" is not a Textual key name.
UNUSABLE_KEYS = {"ctrl+c", "ctrl+i", "ctrl+m", "ctrl+j", "ctrl+h", "ctrl+p", "return"}


def _bindings(cls):
    for b in cls.BINDINGS:
        key, action = (b.key, b.action) if isinstance(b, Binding) else (b[0], b[1])
        for k in key.split(","):
            yield k.strip(), action


@pytest.mark.parametrize("screen_cls", SCREENS, ids=lambda c: c.__name__)
def test_only_q_is_a_plain_letter(screen_cls):
    letters = [k for k, _ in _bindings(screen_cls) if len(k) == 1 and k != "q"]
    assert not letters, f"{screen_cls.__name__} binds plain letter(s) {letters}; use a ctrl key"


@pytest.mark.parametrize("screen_cls", [s for s in SCREENS if s is not MainScreen.MainScreen],
                         ids=lambda c: c.__name__)
def test_escape_goes_back(screen_cls):
    assert "escape" in dict(_bindings(screen_cls)), f"{screen_cls.__name__} has no escape binding"


@pytest.mark.parametrize("screen_cls", SCREENS + [MyProfileApp], ids=lambda c: c.__name__)
def test_no_unusable_keys(screen_cls):
    bad = [k for k, _ in _bindings(screen_cls) if k in UNUSABLE_KEYS]
    assert not bad, f"{screen_cls.__name__} binds {bad}, which never reach the app"


@pytest.mark.parametrize("screen_cls", SCREENS, ids=lambda c: c.__name__)
def test_every_binding_has_an_action(screen_cls):
    for key, action in _bindings(screen_cls):
        if action.startswith("app."):
            continue
        name = action.split("(")[0]
        assert hasattr(screen_cls, f"action_{name}"), f"{screen_cls.__name__}: {key} -> missing action_{name}"


class _Host(App):
    """Pushes one screen and records what it dismisses with."""

    def __init__(self, screen):
        super().__init__()
        self._screen = screen
        self.dismissed = "not dismissed"

    def on_mount(self):
        self.push_screen(self._screen, callback=lambda r: setattr(self, "dismissed", r))


@pytest.mark.parametrize("key, expected", [("ctrl+g", "community"), ("ctrl+l", "identity"),
                                           ("ctrl+r", "role"), ("ctrl+t", "team"), ("escape", 200)])
async def test_edit_profile_keys_work_while_typing(key, expected):
    app = _Host(EditElementsScreens.EditProfileScreen(user_profile={"displayName": "Gary"}, user_GUID="g-1"))
    async with app.run_test() as pilot:
        await pilot.pause()
        app.screen.query_one("#user_job_title", Input).focus()
        await pilot.press(key)
        await pilot.pause()
        assert app.dismissed == expected


@pytest.mark.parametrize("key", ["enter", "escape", "q"])
async def test_status_screen_close_keys(key):
    app = _Host(StatusScreen.StatusScreen("Created element 'guid-1'"))
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press(key)
        await pilot.pause()
        assert app.dismissed == 200
