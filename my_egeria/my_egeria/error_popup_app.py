"""

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

"""

from textual.app import App
from my_egeria.screens.error_popup_screen import ErrorPopup


class ErrorPopupApp (App):

    SCREENS = {
        "error": ErrorPopup,
        }

    def __init__(self, msg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.msg = msg

    def on_mount(self):
        self.push_screen(ErrorPopup(self.msg))
        self.exit()