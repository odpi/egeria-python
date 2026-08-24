""""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a screen for a user to add a comment to a community for my_egeria.

"""
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Header, Static, TextArea, Footer, Input, DataTable, Switch, Button
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
        ("q", "quit", "Quit Edit Project"),
        ("c", "cancel", "Cancel")
        ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, project_GUID):
        super().__init__()
        self.project_GUID = project_GUID
        main_screen = self.app.get_screen("main")
        self.project_table = main_screen.query_one("#project_table", DataTable())
        self.project_table.cursor_type = "row"
        self.project_table.zebra_stripes = True
        self.project_type = ""
        self.project_name = ""
        self.project_description = ""
        self.project_id = ""
        self.result = 0

    def on_mount(self):
        self.title = "Egeria - My Profile"
        self.subtitle = "Add Project to Egeria"

    def compose(self) -> ComposeResult:
        """This method composes the UI for the AddProjectScreen."""
        yield Header(show_clock=True)
        yield DataTable(id="self.project_table")
        yield ScrollableContainer(
            Static(f"[b]Please complete input fields before selecting Add Project[/b]"),
            Static(f"Project Type - Campaign, StudyProject, Task, PersonalProject or Project."),
            Input(placeholder="Enter Project Type", id="project_type_input"),
            Input(placeholder="Enter Project Name (Display Name)", id="project_name_input"),
            Input(placeholder="Enter Project Description", id="project_description_input"),
            Input(placeholder="Enter a short business id for project", id="project_id_input"),
            Static(f"Do you wish to link this project to your profile? [b]Default is True (link the project)[/b]"),
            Switch(value=True, id="link_project_switch"),
            id="association_input_container"
            )
        yield Horizontal(
            Button(label="Add Project", id="add_project_button", variant="primary"),
            Button(label="Delete Project", id="delete_project_button", variant="error"),
            id="project_buttons_container"
            )
        yield Footer()

    @on(Input.Changed)
    def handle_input_change(self, event: Input.Changed):
        if event.control.id == "project_type_input":
            self.project_type = event.value
        elif event.control.id == "project_name_input":
            self.project_name = event.value
        elif event.control.id == "project_description_input":
            self.project_description = event.value
        elif event.control.id == "project_id_input":
            self.project_id = event.value

    @on(DataTable.RowHighlighted)
    def handle_row_hovered(self, event: DataTable.RowHighlighted):
        self.table_row = event.row_key

    @on(DataTable.RowSelected)
    def handle_row_selected(self, event: DataTable.RowSelected):
        self.table_row = event.row_key

    @on(Button.Pressed, id="add_project_button")
    def handle_add_project(self):
        if not self.project_type or not self.project_name:
            self.notify("At least Project Type and Project Name are required", timeout=12, severity="error")
        else:
            self.result =self.app.add_project(self.project_type, self.project_name, self.project_description, self.project_id)
        if self.result == 200:
            self.notify("Project added successfully", timeout=15, severity="information")

        else:
            self.notify("Project addition to Egeria failed", timeout=20, severity="error")

        self.query_one("project_type_input", Input).clear()
        self.query_one("project_name_input", Input).clear()
        self.query_one("project_description_input", Input).clear()
        self.query_one("project_id_input", Input).clear()
        self.project_table.refresh()

    @on(Button.Pressed, id="delete_project_button")
    def handle_delete_project(self):
        if not self.table_row:
            self.notify("Please select a project to delete before you press the delete button", timeout=12, severity="error")
        else:
            self.app.delete_project(self.table_row)

    def action_quit(self):
        self.dismiss(200)

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