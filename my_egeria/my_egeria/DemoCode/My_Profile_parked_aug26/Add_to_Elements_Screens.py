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
        main_screen = self.app.get_screen("main")
        self.community_table = main_screen.query_one("#community_table", DataTable())
        self.community_table.cursor_type = "row"
        self.community_table.zebra_stripes = True
        self.community_row_selected = ""

    def on_mount(self):
        self.title = "Egeria - My Profile"
        self.subtitle = "Add a Community"

    def compose(self) -> ComposeResult:
        """This method composes the UI for the AddCommunityScreen."""
        yield Header(show_clock=True)
        yield ScrollableContainer (
            DataTable(id="community_table")
            )
        yield ScrollableContainer(
            Static(f"Please complete all input fields before selecting the Add Community button"),
            Static("Community Name"),
            Input(id="community_name-input"),
            Static("Community Description"),
            Input(id="community_description-input"),
            Horizontal (
                Button("Add Community", id="add_community_button", variant="primary")
                ),
            id="association_input_container"
            )
        yield Static(f"Please select a community before you select one of the action buttons")
        Horizontal (
            Button("Remove from my Profile", id="remove_community_link_button", variant="warning"),
            Button("Delete Community", id="delete_community_button", variant="error")
            )
        yield Footer()

    @on(DataTable.RowSelected, "#community_table")
    def action_select_community(self, event: DataTable.RowSelected):
        """ Once thew user has selected a community in the table,
        this routine retrieves the community identity from the table row
        and then call a delete community routine in  the app to delete it from egeria """
        self.log(f"Row: {event} selected by user")
        self.community_row_selected = event.row_key

    @on(DataTable.RowHighlighted)
    def action_highlight_community(self, event: DataTable.RowHighlighted):
        """ Once thew user has selected a community in the table,
        this routine retrieves the community identity from the table row
        and then call a delete community routine in  the app to delete it from egeria """
        self.log(f"Row: {event} highlighted by user")
        self.community_row_selected = event.row_key

    @on(Button.Pressed, "#add_community_button")
    def action_add_community(self, event: Button.Pressed):
        """ Once user input is complete, use that to create a new community in Egeria
        This function calls back to an add community function in the app """
        self.log(f"Button: {event} selected by user")
        self.community_name = self.query_one("#community_name_input", Input)
        self.community_description = self.query_one("#community_description_input", Input)
        if self.community_name and self.community_description:
            return_code = self.app.add_community(self.community_name.value, self.community_description.value)
            if return_code == 200:
                self.notify(f"Community {self.community_name.value} created in Egeria", timeout=15, severity="information")
            else:
                self.notify(f"Failed to create community in Egeria, error in log")
                self.dismiss(return_code)
        else:
            self.notify(f"please complete input before selecting Add Community", timeout=12, severity="warning")


@on(Button.Pressed, "#remove_community_link_button")
def remove_community(self, event: Button.Pressed):
    """ Once thew user has selected a community in the table,
    this routine retrieves the community identity from the table row
    and then call a remove link to the user_profile routine in  the app to delete it from egeria """
    self.log(f"Button: {event} selected by user")
    if self.community_row_selected:
        return_code = self.app.remove_link_to_community(self.community_row_selected)
        if return_code == 200:
            self.notify(f"Community {self.community_name.value} Link removed from Profile", timeout=15, severity="information")
        else:
            self.notify(f"Failed to remove community link from profile, error in log")
        self.dismiss(return_code)
    else:
        self.notify(f"please select a community (table row) before selecting Remove Community", timeout=12,
                    severity="warning")

    @on(Button.Pressed, "#delete_community_button")
    def delete_community(self, event: Button.Pressed):
        """ Once thew user has selected a community in the table,
        this routine retrieves the community identity from the table row
        and then call a delete community routine in  the app to delete it from egeria """
        self.log(f"Button: {event} selected by user")
        if self.community_row_selected:
            return_code = self.app.delete_community(self.community_row_selected)
            if return_code == 200:
                self.notify(f"Community {self.community_name.value} deleted in Egeria", timeout=15, severity="information")
            else:
                self.notify(f"Failed to delete community in Egeria, error in log")
            self.dismiss(return_code)
        else:
            self.notify(f"please select a community (table row) before selecting Delete Community", timeout=12, severity="warning")

    def action_cancel(self):
        self.log(f"Cancel hot key selected by user")
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
        self.blog_selected = None
        self.blog_entry_selected = None
        self.blog_table = self.app.query_one("#blog_table")
        self.blog_table.id="blog_table"
        self.blog_table.cursor_type="row"
        self.blog_table.zebra_stripes=True

    def on_mount(self):
        self.title = "Egeria - My Profile"
        self.subtitle = "Blog and Blog Entry Processing"

    def compose(self) -> ComposeResult:
        """This method composes the UI for the AddBlogEntryScreen."""
        yield Header(show_clock=True)
        yield DataTable(id="blog_table")
        yield DataTable(id="blog_entry_table")
        yield ScrollableContainer(
            Static(f"Please complete input fields before selecting the Add Blog button", id="blog_static_1"),
            Static("Please select a blog before selecting display blog entries", id="blog_static_2"),
            Static("Please select a blog before selecting delete blog", id="blog_static_3"),
            Static("Please select a blog entry before selecting delete blog entry", id="blog_static_4"),
            Input(placeholder="Enter blog entry title", id="blog_entry_title"),
            TextArea(id="blog_entry_text"),
            Horizontal(
                Button("Add Blog", variant="primary", id="add_blog_button"),
                Button("Add Blog Entry", variant="primary", id="add_blog_entry_button"),
                Button("Display Blog Entries", variant="primary", id="display_blog_entries_button"),
                id="blog_button_container"
            ),
            id="blog_entry_input_container"
        )
        yield Button("Delete Blog", variant="error", id="delete_blog_button")
        yield Footer()

    @on(DataTable.RowHighlighted, "#blog_table")
    def action_highlighted_blog(self, event: DataTable.RowHighlighted):
        """ Highlight a blog"""
        self.blog_selected = event.row_key
        self.log(f"Blog Row Highlighted: {self.blog_selected}")

    @on(DataTable.RowSelected, "#blog_table")
    def action_selected_blog(self, event: DataTable.RowSelected):
        """Select a blog to delete"""
        self.blog_selected = event.row_key
        self.log(f"Blog Row Selected: {self.blog_selected}")

    @on(DataTable.RowHighlighted, "#blog_entry_table")
    def action_highlighted_blog_entry(self, event: DataTable.RowHighlighted):
        """ Highlight a blog entry to delete"""
        self.blog_entry_selected = event.row_key
        self.log(f"Blog Entry Row Highlighted: {self.blog_entry_selected}")

    @on(DataTable.RowSelected, "#blog_entry_table")
    def action_selected_blog_entry(self, event: DataTable.RowSelected):
        """Select a blog entry to delete"""
        self.blog_selected = event.row_key
        self.log(f"Blog Entry Row Selected: {self.blog_selected}")

    @on(Button.Pressed, "#add_blog_entry_button")
    def action_add_blog_entry(self):
        """ Verify that the input is complete and then call the
        add blog function in the app """
        self.blog_entry_title = self.query_one("#blog_entry_title")
        self.blog_entry_text = self.query_one("#blog_entry_text")
        if self.blog_entry_title and self.blog_entry_text:
            return_code = self.app.add_blog_entry(self.blog_entry_title, self.blog_entry_text)
            if return_code == 200:
                self.log(f"Blog entry added {self.blog_entry_title}")
                self.notify(f"Blog entry added {self.blog_entry_title}")
            else:
                self.log(f"Blog entry not added {self.blog_entry_title}, return code {return_code}")
                self.notify(f"Blog entry not added {self.blog_entry_title}, return code {return_code}")

    @on(Button.Pressed, "#delete_blog_button")
    def action_delete_blog(self):
        """Delete a blog, user must select the entry to delete"""
        if self.blog_selected:
            return_code = self.app.delete_blog(self.blog_selected)
            if return_code == 200:
                self.log(f"Blog entry deleted {self.blog_selected}")
                self.notify(f"Blog entry deleted {self.blog_selected}")
            else:
                self.log(f"Blog entry not deleted {self.blog_selected}, return code {return_code}")
                self.notify(f"Blog entry not deleted {self.blog_selected}, return code {return_code}")

    @on()

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