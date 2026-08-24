""""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a screen for a user to add a comment to a community for my_egeria.

"""

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import Header, Static, TextArea, Footer
from pyegeria import Egeria

class AddCommentScreen(ModalScreen):
    """ Add a comment to a community the user belongs to """

    BINDINGS = [
        ("s", "save_comment", "Save Comment"),
        ("c", "cancel", "Cancel")
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, community_GUID):
        super().__init__()
        self.community_GUID = community_GUID

    def on_mount(self):
        self.title = "Egeria - My Profile"
        self.subtitle = "Add Comment to a Community"


    def compose(self) -> ComposeResult:
        """This method composes the UI for the AddCommentScreen."""
        yield Header(show_clock=True)
        yield ScrollableContainer(
            Static("Enter your comment in the text area."),
            Static("When complete use Save Comment to save current commment and add another"),
            Static("Use Cancel to return to the previous screen"),
            TextArea(id="community_comment-textarea"),
            id="comment_textarea_container"
            )
        yield Footer()

    def action_save_comment(self):
        comment = self.query_one("#community_comment-textarea", TextArea)
        if comment:
            user_comment = comment.text
            self.log(f"User comment: {user_comment}")
            self.dismiss([self.community_GUID, user_comment])
        else:
            container =self.query_one("#comment_textarea_container", ScrollableContainer)
            container.mount(Static(f"[@b aquamarine]Please enter a comment prior to selecting Save Comment[/]"))
            container.refresh()

    def action_cancel(self):
        self.dismiss(200)
