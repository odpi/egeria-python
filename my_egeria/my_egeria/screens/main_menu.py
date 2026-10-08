# Python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides the main menu for the my_egeria module.


"""

from textual.widgets import Static, Button
from textual.containers import Container, Vertical
from textual import events
from my_egeria.con_services.egeria_connection import EgeriaConnectionService
from my_egeria.widgets.popup import show_popup_and_exit
from my_egeria.screens.base_screen import BaseScreen


class MainMenuScreen(BaseScreen):
    CSS_PATH = ["../styles/common.css", "../styles/main_menu.css"]

    def __init__(self):
        super().__init__()
        self.connection_service = EgeriaConnectionService()

    def compose(self):
        yield from super().compose()
        # Top-half container -> bordered box -> centered vertical menu
        yield Container(
            Container(
                Vertical(
                    Static("Egeria Management Console", id="menu_title"),
                    Vertical(
                        Button("Glossaries", id="glossaries"),
                        Button("Collections", id="collections"),
                        Button("GovernanceOfficer", id="gov_officers"),
                        Button("Product Managers", id="product_managers", disabled=True),
                        Button("Project Managers", id="projects", disabled=True),
                        Button("Subject Areas", id="subject_areas", disabled=True),
                        Button("Quit", id="quit"),
                        id="menu_buttons",
                    ),
                    id="menu_form",
                ),
                id="menu_box",
            ),
            id="menu_top",
        )

    async def on_mount(self):
        await super().on_mount()
        try:
            self.connection_service.verify_connection()
        except ConnectionError as e:
            show_popup_and_exit(str(e))
            return

        # Place the content in the top half, centered horizontally
        top = self.query_one("#menu_top", Container)
        top.styles.dock = "top"
        top.styles.height = "60%"               # a bit more than half for breathing room
        top.styles.width = "100%"
        top.styles.padding = (1, 2)
        top.styles.align_horizontal = "center"
        top.styles.align_vertical = "top"
        top.styles.gap = 1

        # Bordered box around the menu
        box = self.query_one("#menu_box", Container)
        box.styles.width = "50%"
        box.styles.border = ("solid", "white")
        box.styles.padding = (1, 2)
        box.styles.align_horizontal = "center"
        box.styles.align_vertical = "top"
        box.styles.min_height = 12

        # Inner vertical container
        form = self.query_one("#menu_form", Vertical)
        form.styles.gap = 1
        form.styles.width = "100%"
        form.styles.align_horizontal = "center"

        # Title styling
        title = self.query_one("#menu_title", Static)
        title.styles.text_align = "center"
        title.styles.text_style = "bold"
        title.styles.margin = (0, 0, 1, 0)

        # Buttons container: center children
        buttons = self.query_one("#menu_buttons", Vertical)
        buttons.styles.align_horizontal = "center"
        buttons.styles.gap = 1
        buttons.styles.width = "100%"

        # Make buttons a consistent width for aesthetics
        for bid in ("#glossaries", "#collections", "#projects", "#subject_areas", "#quit"):
            btn = self.query_one(bid, Button)
            btn.styles.width = 24  # fixed character width

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "glossaries":
            await self.app.push_screen("glossary_browser")
        elif event.button.id == "collections":
            await self.app.push_screen("collection_browser")
        elif event.button.id == "gov_officers":
            await self.app.push_screen("governance_officer_browser")
        elif event.button.id == "product_managers":
            pass
        elif event.button.id == "projects":
            pass
        elif event.button.id == "subject_areas":
            pass
        elif event.button.id == "quit":
            self.app.exit()

    async def on_key(self, event: events.Key):
        if event.key == "q":
            self.app.exit()
