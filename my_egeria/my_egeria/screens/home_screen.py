# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Screen related functions of my_egeria module.


"""

from .base_screen import BaseScreen

class HomeScreen(BaseScreen):
    CSS_PATH = ["styles/common.css", "styles/home_screen.css"]

    def compose(self):
        yield from super().compose()
        yield from []
