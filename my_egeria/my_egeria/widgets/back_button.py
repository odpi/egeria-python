""" python

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a common widget for my_egeria.


"""


from textual.widgets import Button
from textual.message import Message


class BackButton(Button):
    class BackPressed(Message):
        pass

    def __init__(self):
        super().__init__("← Back", id="back")

    def on_button_pressed(self, event):
        self.post_message(self.BackPressed())
