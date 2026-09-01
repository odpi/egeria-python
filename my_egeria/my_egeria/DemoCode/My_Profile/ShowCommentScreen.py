""""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a screen for a user to show cooments attached to a community for my_egeria.

"""

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Header, Static, TextArea, Footer
from pyegeria import Egeria

class ShowCommentScreen(ModalScreen):
    """ Add a comment to a community the user belongs to """

    BINDINGS = [
        ("a", "add_comment", "Add Comment"),
        ("c", "cancel", "Cancel"),
        ("q", "quit", "Quit")
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, community_GUID, attached_messages):
        super().__init__()
        self.community_GUID = community_GUID
        self.attached_messages = attached_messages
        self.log(f"Attached Messages: {self.attached_messages}")
        self.log(f"Community GUID: {self.community_GUID}")

    def on_mount(self):
        self.title = "Egeria - My Profile"
        self.subtitle = "Show Comments attached to a Community"
        all_comments = self.extract_comments(self.attached_messages)
        for comment in all_comments:
            self.query_one("#show_comment_textarea_container", ScrollableContainer).mount(Static(comment))



    def compose(self) -> ComposeResult:
        """This method composes the UI for the AddCommentScreen."""
        yield Header(show_clock=True)
        yield ScrollableContainer(
            Static("Use Cancel to return to the previous screen"),
            Static("Comments:\n"),
            id="show_comment_textarea_container"
            )
        yield Footer()

    def action_quit(self):
        self.dismiss([200, ""])

    def action_cancel(self):
        self.dismiss([200, ""])

    def action_add_comment(self):
        self.dismiss([200, self.community_GUID])

    def extract_comments(self, data):
        """
        Recursively searches through a data structure (dict or list) to find
        all comments identified by 'class': 'CommentProperties' and returns
        their 'description' values.

        Parameters:
        data (dict|list): The data structure received from the external system.

        Returns:
        list: A list of comment strings found in the structure.
        """
        comments = []

        if isinstance(data, dict):
            # Check if this dictionary is a CommentProperties object
            if data.get('class') == 'CommentProperties' and 'description' in data:
                comments.append(data['description'])

            # Recursively search all values in the dictionary
            for value in data.values():
                comments.extend(self.extract_comments(value))

        elif isinstance(data, list):
            # Recursively search all items in the list
            for item in data:
                comments.extend(self.extract_comments(item))

        return comments