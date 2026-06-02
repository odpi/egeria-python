# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Screen related functions of my_egeria module.


"""

from textual.containers import Container
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Label, Button, TextArea, Header, Static, Footer
from textual import on
from demo_service import get_config

class SplashScreen(Screen):
    """Splash screen with inline styles (no TCSS)."""
    app: "DataProducts"

    class SplashContinue(Message):
        """Message to continue to the login screen."""
        pass

    def __init__(self) -> None:
        super().__init__()
        self.app_title = "My Egeria"
        self.app_version = "6.0.0"
        self.app_build_date = "2025-09-08"
        self.app_build_time = "00:00"
        self.app_build_author = "Peter Coldicott"
        self.app_build_commit = "00000000000000000"
        self.app_build_branch = "main"
        self.app_build_platform = "MacOS"
        self.welcome_text = (
            "\n\n"
            "This is example UI code package that leverages the Textual/Rich open source UI Frameworks,\n"
            "and the pyegeria package which is part of the Egeria Project.\n\n"
            "The UI is written in Python and is certainly not meant to demonstrate best coding practices!\n\n"
            "Textual/Rich frameworks originally authored by Will McGugan (Textualize).\n\n"
            "My_Egeria SPDX-License-Identifier: Apache-2.0, "
            "Copyright Contributors to the ODPi Egeria project.\n"
        )

    def compose(self):
        cfg = get_config()
        self.view_server=cfg[1]
        self.platform_url=cfg[0]
        self.user = cfg[2]
        self.password = cfg[3]

        top = Container(
            Label(
                f"Welcome to {self.app_title} v{self.app_version} "
                f"({self.app_build_date} {self.app_build_time})",
                id="splash_title",
            ),
            TextArea(self.welcome_text, id="splash_text"),
            Label(
                f"Build Author: {self.app_build_author} | "
                f"Commit: {self.app_build_commit} | "
                f"Branch: {self.app_build_branch} | "
                f"Platform: {self.app_build_platform}",
                id="splash_meta",
            ),
            id="splash_top"
        )
        yield Header(show_clock=True)
        yield Container(
            Static(
                f"Server: {self.view_server} | Platform: {self.platform_url} | User: {self.user}",
                id="connection_info",
            )
        )
        yield Container(
            Static("MyEgeria", id="title"),
            Static("Data Products", id="main_menu"),
            id="title_row",
        )
        yield top
        yield Button("Continue", variant="primary", id="continue")
        yield Footer()

    async def on_mount(self):

        # Place content in top half, center horizontally
        top = self.query_one("#splash_top", Container)
        
        top.styles.dock = "top"
        top.styles.height = "50%"
        top.styles.width = "100%"
        top.styles.padding = (1, 2)
        top.styles.align_horizontal = "center"
        top.styles.align_vertical = "top"
        top.styles.gap = 1

        title = self.query_one("#splash_title", Label)
        title.styles.text_align = "center"
        title.styles.text_style = "bold"

        # Fixed visible rows for vertical centering math
        VISIBLE_ROWS = 12

        ta = self.query_one("#splash_text", TextArea)
        ta.styles.width = "90%"
        ta.styles.height = VISIBLE_ROWS          # fixed rows to make vertical centering predictable
        ta.styles.border = ("solid", "white")    # solid white border
        ta.styles.text_style = "bold"
        ta.styles.padding = 1
        ta.styles.text_align = "center"          # horizontal centering of text

        # Vertically center the content by adding top padding lines
        raw_text = self.welcome_text.strip("\n")
        content_lines = raw_text.splitlines() or [raw_text]
        content_rows = len(content_lines)

        # Compute usable rows considering numeric padding
        pad_top = int(getattr(ta.styles.padding, "top", 0) or 0)
        pad_bottom = int(getattr(ta.styles.padding, "bottom", 0) or 0)
        usable_rows = max(VISIBLE_ROWS - (pad_top + pad_bottom), 1)
        top_pad = max((usable_rows - content_rows) // 2, 0)

        ta.value = ("\n" * top_pad) + raw_text

        meta = self.query_one("#splash_meta", Label)
        meta.styles.text_align = "center"

        btn = self.query_one("#continue", Button)
        btn.styles.margin = (1, 0, 0, 0)

    @on(Button.Pressed, "#continue")
    async def continue_to_app(self) -> None:
        """ Quit button pressed, isssue continue message to app """
        self.log(f"Continue button pressed, app is: {self.app}")
        # self.post_message(SplashScreen.SplashContinue())
        self.app.handle_splash_screen_splash_continue()
