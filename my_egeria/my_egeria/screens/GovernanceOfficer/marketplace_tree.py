# Python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides the main Screen for the Governance Officer related functions of my_egeria module.


"""
from ..base_screen import BaseScreen
from textual.widgets import Button, Tree, Static, Input
from my_egeria.utils.config import EgeriaConfig, get_global_config
from textual import on
from textual.containers import Container, Horizontal

class MarketPlaceTree(BaseScreen):
    """Screen showing a Data Product MarketPlace in a Tree structure"""

    CSS_PATH = ["../../styles/common.css", "../../styles/governance_officer_browser.css"]

    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("q", "back", "Back"),
        ("escape", "back", "Back"),
    ]

    def __init__(self, market_tree: Tree, *args, **kwargs):
        super().__init__(**kwargs)
        self.market_tree = market_tree

    def compose(self):
        yield from super().compose()
        # Simple vertical layout: top (list), search (fixed 5 rows), spacer, bottom (buttons)
        Static("Governance Officer - Data Product MarketPlace", id="go_title"),
        yield Container(self.market_tree, id="marketplace_tree")
        # Search (fixed 5 rows)
        Container(
            Horizontal(
                Input(placeholder="Search Governance Definitions...", id="pt-search-input", disabled=True),
                Button("Search", id="pt-search-button", disabled=True),
                id="pt_search_row",
            ),
            id="pt_search_row_container",
        ),
        # Flexible spacer to push buttons to bottom
        Container(id="pt_spacer"),
        # Bottom: action buttons
        Container(
            Horizontal(
                Button("Select Definition", id="pt-select-button"),
                Button("Back", id="back-button"),
                id="pt_action_row",
            ),
            id="pt_action_row_container",
        ),
        id = "pt_root",

    def action_refresh(self, event):
        self.market_tree.refresh()

    def action_back(self) -> None:
        self.app.pop_screen()

    @on (Button.Pressed, "#pt-select-button")
    def process_select_button(self, event: Button.Pressed) -> None:
        # check which tree element selected and then take that element and expand ina new tree
        self.log(f"Processing Selection: {self.market_tree_node_selected} of {self.market_tree}")
        self.market_tree.expand(self.market_tree_node_selected)

    def on_tree_node_selected(self, market_tree, market_tree_node_selected):
        self.market_tree = market_tree
        self.market_tree_node_selected = market_tree_node_selected
        self.log(f"Selected node: {market_tree_node_selected} of {market_tree}")
        self.market_tree.expand(market_tree_node_selected)

