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
        """This method composes the UI for the AddAssociationScreen."""
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

class AddAssociationScreen(ModalScreen):
    """ Add an association as an element the user is connected to """

    BINDINGS = [
        ("s", "save_association", "Save Association"),
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

            id="association_input_container"
            )
        yield Footer()

    def action_save_association(self):
        # comment = self.query_one("#community_comment-textarea", TextArea)
        # if comment:
        #     user_comment = comment.text
        #     self.log(f"User comment: {user_comment}")
        #     self.dismiss([self.community_GUID, user_comment])
        # else:
        #     container =self.query_one("#comment_textarea_container", ScrollableContainer)
        #     container.mount(Static(f"[@b aquamarine]Please enter a comment prior to selecting Save Comment[/]"))
        #     container.refresh()
        pass

    def action_cancel(self):
        self.dismiss(200)


class AddProjectScreen(ModalScreen):
    """ Add a project as an element the user is connected to """

    BINDINGS = [
        ("s", "save_project", "Save Project"),
        ("c", "cancel", "Cancel")
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, project_GUID):
        super().__init__()
        self.project_GUID = project_GUID

    def on_mount(self):
        self.title = "Egeria - My Profile"
        self.subtitle = "Add Comment to a Community"

    def compose(self) -> ComposeResult:
        """This method composes the UI for the AddProjectScreen."""
        yield Header(show_clock=True)
        yield ScrollableContainer(

            id="association_input_container"
        )
        yield Footer()

    def action_save_project(self):

        # comment = self.query_one("#community_comment-textarea", TextArea)
        # if comment:
        #     user_comment = comment.text
        #     self.log(f"User comment: {user_comment}")
        #     self.dismiss([self.community_GUID, user_comment])
        # else:
        #     container =self.query_one("#comment_textarea_container", ScrollableContainer)
        #     container.mount(Static(f"[@b aquamarine]Please enter a comment prior to selecting Save Comment[/]"))
        #     container.refresh()
        pass

    def action_cancel(self):
        self.dismiss(200)


class AddCommunityScreen(ModalScreen):
    """ Add a community as an element the user is connected to """

    BINDINGS = [
        ("s", "save_community", "Save Community"),
        ("c", "cancel", "Cancel")
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, community_GUID):
        super().__init__()
        self.community_GUID = community_GUID

    def on_mount(self):
        self.title = "Egeria - My Profile"
        self.subtitle = "Add a Community"

    def compose(self) -> ComposeResult:
        """This method composes the UI for the AddCommunityScreen."""
        yield Header(show_clock=True)
        yield ScrollableContainer(

            id="association_input_container"
        )
        yield Footer()

    def action_save_community(self):

        # comment = self.query_one("#community_comment-textarea", TextArea)
        # if comment:
        #     user_comment = comment.text
        #     self.log(f"User comment: {user_comment}")
        #     self.dismiss([self.community_GUID, user_comment])
        # else:
        #     container =self.query_one("#comment_textarea_container", ScrollableContainer)
        #     container.mount(Static(f"[@b aquamarine]Please enter a comment prior to selecting Save Comment[/]"))
        #     container.refresh()
        pass

    def action_cancel(self):
        self.dismiss(200)


class AddRoleScreen(ModalScreen):
    """ Add a role as an element the user is connected to """

    BINDINGS = [
        ("s", "save_role", "Save Role"),
        ("c", "cancel", "Cancel")
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, role_GUID):
        super().__init__()
        self.role_GUID = role_GUID

    def on_mount(self):
        self.title = "Egeria - My Profile"
        self.subtitle = "Add Comment to a Community"

    def compose(self) -> ComposeResult:
        """This method composes the UI for the AddRoleScreen."""
        yield Header(show_clock=True)
        yield ScrollableContainer(

            id="role_input_container"
        )
        yield Footer()

    def action_save_role(self):

        # comment = self.query_one("#community_comment-textarea", TextArea)
        # if comment:
        #     user_comment = comment.text
        #     self.log(f"User comment: {user_comment}")
        #     self.dismiss([self.community_GUID, user_comment])
        # else:
        #     container =self.query_one("#comment_textarea_container", ScrollableContainer)
        #     container.mount(Static(f"[@b aquamarine]Please enter a comment prior to selecting Save Comment[/]"))
        #     container.refresh()
        pass

    def action_cancel(self):
        self.dismiss(200)


class AddTeamScreen(ModalScreen):
    """ Add an association to an element the user is connected to """

    BINDINGS = [
        ("s", "save_team", "Save Team"),
        ("c", "cancel", "Cancel")
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, team_GUID):
        super().__init__()
        self.team_GUID = team_GUID

    def on_mount(self):
        self.title = "Egeria - My Profile"
        self.subtitle = "Add Team"

    def compose(self) -> ComposeResult:
        """This method composes the UI for the AddTeamScreen."""
        yield Header(show_clock=True)
        yield ScrollableContainer(

            id="association_input_container"
        )
        yield Footer()

    def action_save_team(self):

        # comment = self.query_one("#community_comment-textarea", TextArea)
        # if comment:
        #     user_comment = comment.text
        #     self.log(f"User comment: {user_comment}")
        #     self.dismiss([self.community_GUID, user_comment])
        # else:
        #     container =self.query_one("#comment_textarea_container", ScrollableContainer)
        #     container.mount(Static(f"[@b aquamarine]Please enter a comment prior to selecting Save Comment[/]"))
        #     container.refresh()
        pass

    def action_cancel(self):
        self.dismiss(200)


class AddBlogEntryScreen(ModalScreen):
    """ Add a Blog Entry as  an element for the user """

    BINDINGS = [
        ("s", "save_blog_entry", "Save Blog Entry"),
        ("c", "cancel", "Cancel")
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, actor_profile_GUID):
        super().__init__()
        self.actor_profile_GUID = actor_profile_GUID

    def on_mount(self):
        self.title = "Egeria - My Profile"
        self.subtitle = "Add Blog Entry to an actor profile"

    def compose(self) -> ComposeResult:
        """This method composes the UI for the AddBlogEntryScreen."""
        yield Header(show_clock=True)
        yield ScrollableContainer(

            id="blog_entry_input_container"
        )
        yield Footer()

    def action_save_blog_entry(self):

        # comment = self.query_one("#community_comment-textarea", TextArea)
        # if comment:
        #     user_comment = comment.text
        #     self.log(f"User comment: {user_comment}")
        #     self.dismiss([self.community_GUID, user_comment])
        # else:
        #     container =self.query_one("#comment_textarea_container", ScrollableContainer)
        #     container.mount(Static(f"[@b aquamarine]Please enter a comment prior to selecting Save Comment[/]"))
        #     container.refresh()
        pass

    def action_cancel(self):
        self.dismiss(200)


class AddJournalEntryScreen(ModalScreen):
    """ Add a Journal Entry to the actor profile """

    BINDINGS = [
        ("s", "save_journal_entry", "Save Journal Entry"),
        ("c", "cancel", "Cancel")
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, user_GUID):
        super().__init__()
        self.user_GUID = user_GUID

    def on_mount(self):
        self.title = "Egeria - My Profile"
        self.subtitle = "Add Journal Entry"

    def compose(self) -> ComposeResult:
        """This method composes the UI for the AddJournalEntryScreen."""
        yield Header(show_clock=True)
        yield ScrollableContainer(

            id="journal_entry_input_container"
        )
        yield Footer()

    def action_save_journal_entry(self):

        # comment = self.query_one("#community_comment-textarea", TextArea)
        # if comment:
        #     user_comment = comment.text
        #     self.log(f"User comment: {user_comment}")
        #     self.dismiss([self.community_GUID, user_comment])
        # else:
        #     container =self.query_one("#comment_textarea_container", ScrollableContainer)
        #     container.mount(Static(f"[@b aquamarine]Please enter a comment prior to selecting Save Comment[/]"))
        #     container.refresh()
        pass

    def action_cancel(self):
        self.dismiss(200)


class AddTodosScreen(ModalScreen):
    """ Add an association to an element the user is connected to """

    BINDINGS = [
        ("s", "save_todo", "Save Todo"),
        ("c", "cancel", "Cancel")
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, user_GUID):
        super().__init__()
        self.user_GUID = user_GUID

    def on_mount(self):
        self.title = "Egeria - My Profile"
        self.subtitle = "Add Todos for an Actor"

    def compose(self) -> ComposeResult:
        """This method composes the UI for the AddTodosScreen."""
        yield Header(show_clock=True)
        yield ScrollableContainer(

            id="todo_input_container"
        )
        yield Footer()

    def action_save_todo(self):

        # comment = self.query_one("#community_comment-textarea", TextArea)
        # if comment:
        #     user_comment = comment.text
        #     self.log(f"User comment: {user_comment}")
        #     self.dismiss([self.community_GUID, user_comment])
        # else:
        #     container =self.query_one("#comment_textarea_container", ScrollableContainer)
        #     container.mount(Static(f"[@b aquamarine]Please enter a comment prior to selecting Save Comment[/]"))
        #     container.refresh()
        pass

    def action_cancel(self):
        self.dismiss(200)


class AddUserIdentityScreen(ModalScreen):
    """ Add a user identity to the actor profile """

    BINDINGS = [
        ("s", "save_user_identity", "Save User_Identity"),
        ("c", "cancel", "Cancel")
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, user_GUID):
        super().__init__()
        self.user_GUID = user_GUID

    def on_mount(self):
        self.title = "Egeria - My Profile"
        self.subtitle = "Add user identity to the actor profile"

    def compose(self) -> ComposeResult:
        """This method composes the UI for the AddUserIdentityScreen."""
        yield Header(show_clock=True)
        yield ScrollableContainer(

            id="user_identity_input_container"
        )
        yield Footer()

    def action_save_user_identity(self):

        # comment = self.query_one("#community_comment-textarea", TextArea)
        # if comment:
        #     user_comment = comment.text
        #     self.log(f"User comment: {user_comment}")
        #     self.dismiss([self.community_GUID, user_comment])
        # else:
        #     container =self.query_one("#comment_textarea_container", ScrollableContainer)
        #     container.mount(Static(f"[@b aquamarine]Please enter a comment prior to selecting Save Comment[/]"))
        #     container.refresh()
        pass

    def action_cancel(self):
        self.dismiss(200)