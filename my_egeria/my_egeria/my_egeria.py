# Python

"""

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

"""

import os
from typing import Any

from textual import on

from . import utils

# Set safe defaults BEFORE importing anything that might import pyegeria
os.environ.setdefault("EGERIA_USER", "erinoverview")
os.environ.setdefault("EGERIA_USER_PASSWORD", "secret")
os.environ.setdefault("EGERIA_VIEW_SERVER", "qs-view-server")
os.environ.setdefault("EGERIA_PLATFORM_URL", "https://localhost:9443")

from textual.app import App, ComposeResult
from textual.widgets import Footer
from my_egeria.screens.login_screen import LoginScreen
from my_egeria.screens.main_menu import MainMenuScreen
from my_egeria.screens.glossary.glossary_browser import GlossaryBrowserScreen
from my_egeria.screens.collections.collection_browser import CollectionBrowserScreen
from my_egeria.screens.collections.collection_members_screen import CollectionMemberScreen
from my_egeria.screens.collections.collection_details import CollectionDetailsScreen
from my_egeria.screens.collections.add_collection import AddCollectionScreen
from my_egeria.screens.collections.delete_collection import DeleteCollectionScreen
from my_egeria.screens.glossary.glossary_list_screen import GlossaryListScreen
from my_egeria.screens.glossary.term_details import TermDetailsScreen
from my_egeria.screens.glossary.term_list_screen import TermListScreen
from my_egeria.screens.GovernanceOfficer.governance_officer_browser import GovernanceOfficerBrowserScreen
from my_egeria.screens.GovernanceOfficer.add_governance_definition import AddGovernanceDefinitionScreen
from my_egeria.screens.GovernanceOfficer.delete_governance_definition import DeleteGovernanceDefinitionScreen
from my_egeria.screens.GovernanceOfficer.marketplace_tree import MarketPlaceTree
from my_egeria.screens.ProductManager.product_manager_browser import ProductManagerBrowser
from my_egeria.utils.egeria_client import close_all_managers
from my_egeria.utils.config import EgeriaConfig
from my_egeria.screens.splash_screen import SplashScreen  # your existing splash screen
from my_egeria.services.term_service import get_terms_for_glossary

class MyEgeria(App):
    """Main app class of my_egeria."""
    CSS_PATH = ["./styles/common.css"]

    # Only register screens that do NOT need constructor arguments here
    SCREENS = {
        "splash": SplashScreen,
        "login": LoginScreen,
        "main_menu": MainMenuScreen,
        "glossary_browser": GlossaryBrowserScreen,
        "glossary_list_screen": GlossaryListScreen,
        "term_details": TermDetailsScreen,
        "term_list_screen": TermListScreen,
        "collection_details": CollectionDetailsScreen,
        "add_collection": AddCollectionScreen,
        "collection_members": CollectionMemberScreen,
        "collection_browser": CollectionBrowserScreen,
        "delete_collection": DeleteCollectionScreen,
        "governance_officer_browser": GovernanceOfficerBrowserScreen,
        "add_governance_definition": AddGovernanceDefinitionScreen,
        "delete_governance_definition": DeleteGovernanceDefinitionScreen,
        "marketplace_tree": MarketPlaceTree,
        "product_manager_browser": ProductManagerBrowser,
        # Details screens require arguments; push them with instances at runtime
        # "term_details": lambda: TermDetailsScreen("<guid>"),
        # "collection_details": lambda: CollectionDetailsScreen("<guid>"),
        # "add_collection": AddCollectionScreen,   # can be registered or pushed directly
    }

    def compose(self) -> ComposeResult:
        yield Footer()

    async def on_mount(self) -> None:
        # Start at splash
        await self.push_screen("splash")

    # Optional: handle a "login successful" message from LoginScreen if you use one
    # Provide a generic hook to go to main menu after login
    @on(LoginScreen.LoginSuccess)
    async def handle_login_screen_login_success(self, message: LoginScreen.LoginSuccess) -> None:
        # self.login_payload = message.login_payload
        # self.log(f"Login successful, going to main menu")
        # self.log(f"login_payload: {self.login_payload}, type: {type(self.login_payload)}")
        # self.user = self.login_payload[0]
        # self.password = self.login_payload[1]
        # self.platform_url = self.login_payload[2]
        # self.view_server = self.login_payload[3]
        await self.switch_screen("main_menu")

    # Convenience helpers for pushing details screens (that need args)
    async def on_show_term_details(self, term_guid: str):
        await self.switch_screen(TermDetailsScreen(term_guid))

    async def on_show_term_list(self, glossary_name: str):
        await self.switch_screen(TermListScreen(glossary_name = glossary_name))

    async def on_show_collection_details(self, collection_guid: str):
        await self.switch_screen(CollectionDetailsScreen(collection_guid))

    async def on_show_add_collection(self):
        await self.switch_screen(AddCollectionScreen())

    async def on_show_governance_officer_browser(self):
        await self.switch_screen(GovernanceOfficerBrowserScreen())

    async def on_splash_screen_splash_continue(self):
        await self.switch_screen("login")

    async def on_shutdown(self) -> None:
        try:
            close_all_managers()
        except Exception:
            pass


if __name__ == "__main__":
    # Optionally preload env defaults for demo
    os.environ.setdefault("EGERIA_PLATFORM_URL", "https://localhost:9443")
    os.environ.setdefault("EGERIA_VIEW_SERVER", "qs-view-server")
    MyEgeria().run()
