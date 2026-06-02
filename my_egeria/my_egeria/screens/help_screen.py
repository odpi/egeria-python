# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Screen related functions of my_egeria module.


"""

from textual.screen import Screen


class HelpScreen(Screen):
    CSS_PATH = ["styles/common.css", "styles/help_screen.css"]

    def compose(self):
        yield from []
