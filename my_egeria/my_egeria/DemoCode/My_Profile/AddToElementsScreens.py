"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a user screen to allow the user to add todos to my_egeria.

"""

import pwd
from datetime import datetime

from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Horizontal
from textual.screen import ModalScreen
from textual.widgets import DataTable, OptionList, Header, Static, Footer, Input, Button
from textual.widgets._option_list import Option

from pyegeria import Egeria, PyegeriaException, load_app_config, settings


class AddTodoScreen(ModalScreen):
    """Add Todo Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+a", "add_new_todo", "Add New Todo")
        ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, selected_table, *args, **kwargs):
        super().__init__(id="add_todo_screen", *args, **kwargs)
        self.selected_table = selected_table
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"
        self.todo_name = ""
        self.todo_description = ""
        self.todo_priority = ""
        self.todo_guid = ""

    def on_mount(self):
        main_screen = self.app.get_screen("main")

        self.todos_table = main_screen.query_one("#todos_table", DataTable)
        assert self.todos_table is not None

        self.todos_table.zebra_stripes = True
        self.todos_table.cursor_type = "row"
        self.todos_table.focus()

    def compose(self) -> ComposeResult:
        yield Static("Add Todo Screen")
        yield ScrollableContainer(
            Static("This screen is intended for the user who wants to add a small number of Todos\n"
                     "Please ensure that you have filled in all fields before clicking 'Add Todo'\n"
                     "For bulk additions please use Dr_Egeria instead."),
            Input("Name of Todo", id="todo_name"),
            Input("Description of Todo", id="todo_description"),
            Input("Priority of Todo", id="todo_priority"),
            Static("Status will be automatically set to 'REQUESTED'"),
            Horizontal(
                Button("Add Todo", id="add_todo_button", variant="primary"),
                Button("Quit", id="quit_button", variant="warning")
            ))

    def action_add_new_todo(self):
        """ Call Egeria to add the new todo """
        tclient = Egeria(
            view_server=self.view_server,
            platform_url=self.platform_url,
            user_id=self.user_name,
            user_pwd=self.user_password
            )

        try:
            tclient.create_egeria_bearer_token()
            todo_guid = tclient.create_my_todo(
                        todo_name=self.todo_name,
                        description=self.todo_description,
                        priority=self.todo_priority,
                        activity_status="REQUESTED"
                        )
            self.log(f"Created ToDo assigned to the current user: {todo_guid}")
        except PyegeriaException as e:
            self.notify(f"Add todo failed with return: {e}", timeout=10, severity="error")
        finally:
            tclient.close_session()
            self.todo_name = ""
            self.todo_description = ""
            self.todo_priority = ""
            self.todo_guid = ""
            self.query_one("#todo_name", Input).clear()
            self.query_one("#todo_description", Input).clear()
            self.query_one("#todo_priority", Input).clear()
        return

    @on(Input.Changed)
    def handle_input_changed(self, event: Input.Changed):
        if event.input.id == "todo_name":
            self.todo_name = event.input.value
        if event.input.id == "todo_description":
            self.todo_description = event.input.value
        if event.input.id == "todo_priority":
            self.todo_priority = event.input.value

    def action_quit(self):
        self.dismiss(200)

    @on(Button.Pressed, "#add_todo_button")
    def handle_add_todo_button(self, event: Button.Pressed):
        """ Handle the add button press """
        if self.todo_name and self.todo_description:
            self.action_add_new_todo()
        else:
            self.notify("Please enter at least anew todo name and description", timeout=10, severity="error")

    @on(Button.Pressed, "#quit_button")
    def handle_quit_button(self, event: Button.Pressed):
        """ Handle the quit button press """
        self.action_quit()


class AddAssociationScreen(ModalScreen):
    """Add Association (Projects or Communities Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+a", "add_new_association", "Add New Association")
        ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, selected_table, *args, **kwargs):
        super().__init__(id="add_association_screen", *args, **kwargs)
        self.selected_table = selected_table
    #     load_app_config()
    #     app_config = settings.Environment
    #     app_user = settings.User_Profile
    #     self.user_name = app_user.user_name or "garygeeke"
    #     self.user_password = app_user.user_pwd or "secret"
    #     self.view_server = app_config.egeria_view_server or "qs-view-server"
    #     self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"
    #     self.todo_name = ""
    #     self.todo_description = ""
    #     self.todo_priority = ""
    #     self.todo_guid = ""
    #
    # def on_mount(self):
    #     main_screen = self.app.get_screen("main")
    #
    #     self.todos_table = main_screen.query_one("#todos_table", DataTable)
    #     assert self.todos_table is not None
    #
    #     self.todos_table.zebra_stripes = True
    #     self.todos_table.cursor_type = "row"
    #     self.todos_table.focus()
    #
    # def compose(self) -> ComposeResult:
    #     yield Static("Add Todo Screen")
    #     yield ScrollableContainer(
    #         Static("This screen is intended for the user who wants to add a small number of Todos\n"
    #                "Please ensure that you have filled in all fields before clicking 'Add Todo'\n"
    #                "For bulk additions please use Dr_Egeria instead."),
    #         Input("Name of Todo", id="todo_name"),
    #         Input("Description of Todo", id="todo_description"),
    #         Input("Priority of Todo", id="todo_priority"),
    #         Static("Status will be automatically set to 'REQUESTED'"),
    #         Horizontal(
    #             Button("Add Todo", id="add_todo_button", variant="primary"),
    #             Button("Quit", id="quit_button", variant="warning")
    #         ))
    #
    # def action_add_new_todo(self):
    #     """ Call Egeria to add the new todo """
    #     tclient = Egeria(
    #         view_server=self.view_server,
    #         platform_url=self.platform_url,
    #         user_id=self.user_name,
    #         user_pwd=self.user_password
    #     )
    #
    #     try:
    #         tclient.create_egeria_bearer_token()
    #         todo_guid = tclient.create_my_todo(
    #             todo_name=self.todo_name,
    #             description=self.todo_description,
    #             priority=self.todo_priority,
    #             activity_status="REQUESTED"
    #         )
    #         self.log(f"Created ToDo assigned to the current user: {todo_guid}")
    #     except PyegeriaException as e:
    #         self.notify(f"Add todo failed with return: {e}", timeout=10, severity="error")
    #     finally:
    #         tclient.close_session()
    #         self.todo_name = ""
    #         self.todo_description = ""
    #         self.todo_priority = ""
    #         self.todo_guid = ""
    #         self.query_one("#todo_name", Input).clear()
    #         self.query_one("#todo_description", Input).clear()
    #         self.query_one("#todo_priority", Input).clear()
    #     return
    #
    # @on(Input.Changed)
    # def handle_input_changed(self, event: Input.Changed):
    #     if event.input.id == "todo_name":
    #         self.todo_name = event.input.value
    #     if event.input.id == "todo_description":
    #         self.todo_description = event.input.value
    #     if event.input.id == "todo_priority":
    #         self.todo_priority = event.input.value
    #
    # def action_quit(self):
    #     self.dismiss(200)
    #
    # @on(Button.Pressed, "#add_todo_button")
    # def handle_add_todo_button(self, event: Button.Pressed):
    #     """ Handle the add button press """
    #     if self.todo_name and self.todo_description:
    #         self.action_add_new_todo()
    #     else:
    #         self.notify("Please enter at least anew todo name and description", timeout=10, severity="error")
    #
    # @on(Button.Pressed, "#quit_button")
    # def handle_quit_button(self, event: Button.Pressed):
    #     """ Handle the quit button press """
    #     self.action_quit()

class AddBlogEntryScreen(ModalScreen):
    """Add Blog Entry Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+a", "add_new_blog", "Add New Blog Entry")
        ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, selected_table, *args, **kwargs):
        super().__init__(id="add_blog_screen", *args, **kwargs)
        self.selected_table = selected_table
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"
        self.blog_entry_name = ""
        self.blog_entry_description = ""
        self.blog_entry_priority = ""
        self.blog_entry_guid = ""

    def on_mount(self):
        main_screen = self.app.get_screen("main")

        self.blogs_table = main_screen.query_one("#blogs_table", DataTable)
        assert self.blogs_table is not None

        self.blogs_table.zebra_stripes = True
        self.blogs_table.cursor_type = "row"
        self.blogs_table.focus()

    def compose(self) -> ComposeResult:
        yield Static("Add Blog Entry Screen")
        yield ScrollableContainer(
            Static("This screen is intended for the user who wants to add a small number of blog entries\n"
                   "Please ensure that you have filled in all fields before clicking 'Add Blog Entry'\n"
                   "For bulk additions please use Dr_Egeria instead."),
            Static("Name"),
            Input("Name of Blog Entry", id="blog_entry_name"),
            Static("Text"),
            Input("Text of Entry", id="blog_entry_text"),
            Static("Situation"),
            Input("Situation", id="blog_entry_situation"),
            Horizontal(
                Button("Add Blog Entry", id="add_entry_button", variant="primary"),
                Button("Quit", id="quit_button", variant="warning")
            ))

    def action_add_new_blog(self):
        """ Call Egeria to add the new blog entry """
        tclient = Egeria(
            view_server=self.view_server,
            platform_url=self.platform_url,
            user_id=self.user_name,
            user_pwd=self.user_password
        )

        try:
            token = tclient.create_egeria_bearer_token(self.user_name, self.user_password)

            body = {
                "class": "NewAttachmentRequestBody",
                "properties": {
                    "class": "BlogEntryProperties",
                    "qualifiedName": f"Blog::Blog-{datetime.now().isoformat()}",
                    "displayName": self.blog_entry_name,
                    "situation": self.blog_entry_situation,
                    "description": self.blog_entry_text,
                }
            }
            blog_entry_response = tclient.blog_my_activity(body=body)

            assert isinstance(blog_entry_response, str)
            blog_entry_guid = blog_entry_response
            self.log(f"Created Blog Entry assigned to the current user: {blog_entry_guid}")
        except PyegeriaException as e:
            self.notify(f"Add blog entry failed with return: {e}", timeout=10, severity="error")
        finally:
            tclient.close_session()
            self.blog_entry_name = ""
            self.blog_entry_description = ""
            self.blog_entry_situation = ""
            self.blog_entry_guid = ""
            self.query_one("#blog_entry_name", Input).clear()
            self.query_one("#blog_entry_text", Input).clear()
            self.query_one("#blog_entry_situation", Input).clear()
        return

    @on(Input.Changed)
    def handle_input_changed(self, event: Input.Changed):
        if event.input.id == "blog_entry_name":
            self.blog_entry_name = event.input.value
        if event.input.id == "blog_entry_text":
            self.blog_entry_text = event.input.value
        if event.input.id == "blog_entry_situation":
            self.blog_entry_situation = event.input.value

    def action_quit(self):
        self.dismiss(200)

    @on(Button.Pressed, "#add_entry_button")
    def handle_add_entry_button(self, event: Button.Pressed):
        """ Handle the add button press """
        self.log(f"Blog entry name: {self.blog_entry_name}, blog entry text: {self.blog_entry_text}, blog entry situation: {self.blog_entry_situation}")
        if self.blog_entry_name:
            self.action_add_new_blog()
        else:
            self.notify("Please enter at least a new blog name and text", timeout=10, severity="error")

    @on(Button.Pressed, "#quit_button")
    def handle_quit_button(self, event: Button.Pressed):
        """ Handle the quit button press """
        self.action_quit()


class AddCommunityScreen(ModalScreen):
    """Main Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+a", "add_new_community", "Add New Community")
        ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, selected_table, *args, **kwargs):
        super().__init__(id="add_community_screen", *args, **kwargs)
        self.selected_table = selected_table
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
    #     self.user_name = app_user.user_name or "garygeeke"
    #     self.user_password = app_user.user_pwd or "secret"
    #     self.view_server = app_config.egeria_view_server or "qs-view-server"
    #     self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"
    #     self.todo_name = ""
    #     self.todo_description = ""
    #     self.todo_priority = ""
    #     self.todo_guid = ""
    #
    # def on_mount(self):
    #     main_screen = self.app.get_screen("main")
    #
    #     self.todos_table = main_screen.query_one("#todos_table", DataTable)
    #     assert self.todos_table is not None
    #
    #     self.todos_table.zebra_stripes = True
    #     self.todos_table.cursor_type = "row"
    #     self.todos_table.focus()
    #
    # def compose(self) -> ComposeResult:
    #     yield Static("Add Todo Screen")
    #     yield ScrollableContainer(
    #         Static("This screen is intended for the user who wants to add a small number of Todos\n"
    #                "Please ensure that you have filled in all fields before clicking 'Add Todo'\n"
    #                "For bulk additions please use Dr_Egeria instead."),
    #         Input("Name of Todo", id="todo_name"),
    #         Input("Description of Todo", id="todo_description"),
    #         Input("Priority of Todo", id="todo_priority"),
    #         Static("Status will be automatically set to 'REQUESTED'"),
    #         Horizontal(
    #             Button("Add Todo", id="add_todo_button", variant="primary"),
    #             Button("Quit", id="quit_button", variant="warning")
    #         ))
    #
    # def action_add_new_todo(self):
    #     """ Call Egeria to add the new todo """
    #     tclient = Egeria(
    #         view_server=self.view_server,
    #         platform_url=self.platform_url,
    #         user_id=self.user_name,
    #         user_pwd=self.user_password
    #     )
    #
    #     try:
    #         tclient.create_egeria_bearer_token()
    #         todo_guid = tclient.create_my_todo(
    #             todo_name=self.todo_name,
    #             description=self.todo_description,
    #             priority=self.todo_priority,
    #             activity_status="REQUESTED"
    #         )
    #         self.log(f"Created ToDo assigned to the current user: {todo_guid}")
    #     except PyegeriaException as e:
    #         self.notify(f"Add todo failed with return: {e}", timeout=10, severity="error")
    #     finally:
    #         tclient.close_session()
    #         self.todo_name = ""
    #         self.todo_description = ""
    #         self.todo_priority = ""
    #         self.todo_guid = ""
    #         self.query_one("#todo_name", Input).clear()
    #         self.query_one("#todo_description", Input).clear()
    #         self.query_one("#todo_priority", Input).clear()
    #     return
    #
    # @on(Input.Changed)
    # def handle_input_changed(self, event: Input.Changed):
    #     if event.input.id == "todo_name":
    #         self.todo_name = event.input.value
    #     if event.input.id == "todo_description":
    #         self.todo_description = event.input.value
    #     if event.input.id == "todo_priority":
    #         self.todo_priority = event.input.value
    #
    # def action_quit(self):
    #     self.dismiss(200)
    #
    # @on(Button.Pressed, "#add_todo_button")
    # def handle_add_todo_button(self, event: Button.Pressed):
    #     """ Handle the add button press """
    #     if self.todo_name and self.todo_description:
    #         self.action_add_new_todo()
    #     else:
    #         self.notify("Please enter at least anew todo name and description", timeout=10, severity="error")
    #
    # @on(Button.Pressed, "#quit_button")
    # def handle_quit_button(self, event: Button.Pressed):
    #     """ Handle the quit button press """
    #     self.action_quit()


class AddJournalEntryScreen(ModalScreen):
    """Main Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+a", "add_new_journal_entry", "Add New Journal Entry")
        ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, selected_table, *args, **kwargs):
        super().__init__(id="add_journal_entry_screen", *args, **kwargs)
        self.selected_table = selected_table
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"
        self.journal_entry_title = ""
        self.journal_entry_text = ""
        self.journal_entry_qualified_name = ""
        self.journal_entry_situation = ""

    def on_mount(self):
        main_screen = self.app.get_screen("main")

        self.journal_table = main_screen.query_one("#journal_table", DataTable)
        assert self.journal_table is not None

        self.journal_table.zebra_stripes = True
        self.journal_table.cursor_type = "row"
        self.journal_table.focus()

    def compose(self) -> ComposeResult:
        yield Static("Add Todo Screen")
        yield ScrollableContainer(
            Static("Please ensure that you have filled in all fields before clicking 'Add Journal Entry' Button\n"
                   "For bulk additions please use Dr_Egeria instead."),
            Static("Title"),
            Input("Title of Entry", id="journal_entry_title"),
            Static("Text"),
            Input("Text of Entry", id="journal_entry_text"),
            Static("Situation"),
            Input("Situation of Entry", id="journal_entry_situation"),
            Horizontal(
                Button("Add Journal Entry", id="add_journal_entry_button", variant="primary"),
                Button("Quit", id="quit_button", variant="warning")
            ))

    def action_add_new_journal_entry(self):
        """ Call Egeria to add the new entry """

        self.qualified_name = f"{self.user_name}:{self.journal_entry_title}:JournalEntry:{datetime.now().isoformat()}"
        body = {
            "class": "NewAttachmentRequestBody",
            "properties": {
                "class": "JournalEntryProperties",
                "qualifiedName": self.qualified_name,
                "displayName": self.journal_entry_title,
                "situation": self.journal_entry_situation,
                "description": self.journal_entry_text
                }
            }

        tclient = Egeria(
            view_server=self.view_server,
            platform_url=self.platform_url,
            user_id=self.user_name,
            user_pwd=self.user_password
        )

        try:
            token = tclient.create_egeria_bearer_token(self.user_name, self.user_password)
            journal_entry_response = tclient.journal_my_activity(body=body)
            assert isinstance(journal_entry_response, str)
            self.log(f"Created ToDo assigned to the current user: {journal_entry_response}")
        except PyegeriaException as e:
            self.notify(f"Add journal entry failed with return: {e}", timeout=10, severity="error")
        finally:
            tclient.close_session()
            self.journal_entry_title = ""
            self.journal_entry_text = ""
            self.journal_entry_situation = ""
            self.qualified_name = ""
            self.query_one("#journal_entry_title", Input).clear()
            self.query_one("#journal_entry_text", Input).clear()
            self.query_one("#journal_entry_situation", Input).clear()
        return

    @on(Input.Changed)
    def handle_input_changed(self, event: Input.Changed):
        if event.input.id == "journal_entry_title":
            self.journal_entry_title = event.input.value
        if event.input.id == "journal_entry_text":
            self.journal_entry_text = event.input.value
        if event.input.id == "journal_entry_situation":
            self.journal_entry_situation = event.input.value

    def action_quit(self):
        self.dismiss(200)

    @on(Button.Pressed, "#add_journal_entry_button")
    def handle_add_journal_entry_button(self, event: Button.Pressed):
        """ Handle the add button press """
        if self.journal_entry_title and self.journal_entry_text:
            self.action_add_new_journal_entry()
        else:
            self.notify("Please enter at least a new title and text for the entry", timeout=10, severity="error")

    @on(Button.Pressed, "#quit_button")
    def handle_quit_button(self, event: Button.Pressed):
        """ Handle the quit button press """
        self.action_quit()


class AddProjectScreen(ModalScreen):
    """Main Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+a", "add_new_project", "Add New Project")
        ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, selected_table, *args, **kwargs):
        super().__init__(id="add_project_screen", *args, **kwargs)
        self.selected_table = selected_table
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"
        self.todo_name = ""
        self.todo_description = ""
        self.todo_priority = ""
        self.todo_guid = ""

    def on_mount(self):
        main_screen = self.app.get_screen("main")

        self.todos_table = main_screen.query_one("#todos_table", DataTable)
        assert self.todos_table is not None

        self.todos_table.zebra_stripes = True
        self.todos_table.cursor_type = "row"
        self.todos_table.focus()

    def compose(self) -> ComposeResult:
        yield Static("Add Todo Screen")
        yield ScrollableContainer(
            Static("This screen is intended for the user who wants to add a small number of Todos\n"
                   "Please ensure that you have filled in all fields before clicking 'Add Todo'\n"
                   "For bulk additions please use Dr_Egeria instead."),
            Input("Name of Todo", id="todo_name"),
            Input("Description of Todo", id="todo_description"),
            Input("Priority of Todo", id="todo_priority"),
            Static("Status will be automatically set to 'REQUESTED'"),
            Horizontal(
                Button("Add Todo", id="add_todo_button", variant="primary"),
                Button("Quit", id="quit_button", variant="warning")
            ))

    def action_add_new_todo(self):
        """ Call Egeria to add the new todo """
        tclient = Egeria(
            view_server=self.view_server,
            platform_url=self.platform_url,
            user_id=self.user_name,
            user_pwd=self.user_password
        )

        try:
            tclient.create_egeria_bearer_token()
            todo_guid = tclient.create_my_todo(
                todo_name=self.todo_name,
                description=self.todo_description,
                priority=self.todo_priority,
                activity_status="REQUESTED"
            )
            self.log(f"Created ToDo assigned to the current user: {todo_guid}")
        except PyegeriaException as e:
            self.notify(f"Add todo failed with return: {e}", timeout=10, severity="error")
        finally:
            tclient.close_session()
            self.todo_name = ""
            self.todo_description = ""
            self.todo_priority = ""
            self.todo_guid = ""
            self.query_one("#todo_name", Input).clear()
            self.query_one("#todo_description", Input).clear()
            self.query_one("#todo_priority", Input).clear()
        return

    @on(Input.Changed)
    def handle_input_changed(self, event: Input.Changed):
        if event.input.id == "todo_name":
            self.todo_name = event.input.value
        if event.input.id == "todo_description":
            self.todo_description = event.input.value
        if event.input.id == "todo_priority":
            self.todo_priority = event.input.value

    def action_quit(self):
        self.dismiss(200)

    @on(Button.Pressed, "#add_todo_button")
    def handle_add_todo_button(self, event: Button.Pressed):
        """ Handle the add button press """
        if self.todo_name and self.todo_description:
            self.action_add_new_todo()
        else:
            self.notify("Please enter at least anew todo name and description", timeout=10, severity="error")

    @on(Button.Pressed, "#quit_button")
    def handle_quit_button(self, event: Button.Pressed):
        """ Handle the quit button press """
        self.action_quit()


class AddRoleScreen(ModalScreen):
    """Main Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+a", "add_new_role", "Add New Role")
        ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, selected_table, *args, **kwargs):
        super().__init__(id="add_role_screen", *args, **kwargs)
        self.selected_table = selected_table
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"
        self.todo_name = ""
        self.todo_description = ""
        self.todo_priority = ""
        self.todo_guid = ""

    def on_mount(self):
        main_screen = self.app.get_screen("main")

        self.todos_table = main_screen.query_one("#todos_table", DataTable)
        assert self.todos_table is not None

        self.todos_table.zebra_stripes = True
        self.todos_table.cursor_type = "row"
        self.todos_table.focus()

    def compose(self) -> ComposeResult:
        yield Static("Add Todo Screen")
        yield ScrollableContainer(
            Static("This screen is intended for the user who wants to add a small number of Todos\n"
                   "Please ensure that you have filled in all fields before clicking 'Add Todo'\n"
                   "For bulk additions please use Dr_Egeria instead."),
            Input("Name of Todo", id="todo_name"),
            Input("Description of Todo", id="todo_description"),
            Input("Priority of Todo", id="todo_priority"),
            Static("Status will be automatically set to 'REQUESTED'"),
            Horizontal(
                Button("Add Todo", id="add_todo_button", variant="primary"),
                Button("Quit", id="quit_button", variant="warning")
            ))

    def action_add_new_todo(self):
        """ Call Egeria to add the new todo """
        tclient = Egeria(
            view_server=self.view_server,
            platform_url=self.platform_url,
            user_id=self.user_name,
            user_pwd=self.user_password
        )

        try:
            tclient.create_egeria_bearer_token()
            todo_guid = tclient.create_my_todo(
                todo_name=self.todo_name,
                description=self.todo_description,
                priority=self.todo_priority,
                activity_status="REQUESTED"
            )
            self.log(f"Created ToDo assigned to the current user: {todo_guid}")
        except PyegeriaException as e:
            self.notify(f"Add todo failed with return: {e}", timeout=10, severity="error")
        finally:
            tclient.close_session()
            self.todo_name = ""
            self.todo_description = ""
            self.todo_priority = ""
            self.todo_guid = ""
            self.query_one("#todo_name", Input).clear()
            self.query_one("#todo_description", Input).clear()
            self.query_one("#todo_priority", Input).clear()
        return

    @on(Input.Changed)
    def handle_input_changed(self, event: Input.Changed):
        if event.input.id == "todo_name":
            self.todo_name = event.input.value
        if event.input.id == "todo_description":
            self.todo_description = event.input.value
        if event.input.id == "todo_priority":
            self.todo_priority = event.input.value

    def action_quit(self):
        self.dismiss(200)

    @on(Button.Pressed, "#add_todo_button")
    def handle_add_todo_button(self, event: Button.Pressed):
        """ Handle the add button press """
        if self.todo_name and self.todo_description:
            self.action_add_new_todo()
        else:
            self.notify("Please enter at least anew todo name and description", timeout=10, severity="error")

    @on(Button.Pressed, "#quit_button")
    def handle_quit_button(self, event: Button.Pressed):
        """ Handle the quit button press """
        self.action_quit()

class AddTeamScreen(ModalScreen):
    """Main Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+a", "add_new_team", "Add New Team")
        ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, selected_table, *args, **kwargs):
        super().__init__(id="add_team_screen", *args, **kwargs)
        self.selected_table = selected_table
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"
        self.todo_name = ""
        self.todo_description = ""
        self.todo_priority = ""
        self.todo_guid = ""

    def on_mount(self):
        main_screen = self.app.get_screen("main")

        self.todos_table = main_screen.query_one("#todos_table", DataTable)
        assert self.todos_table is not None

        self.todos_table.zebra_stripes = True
        self.todos_table.cursor_type = "row"
        self.todos_table.focus()

    def compose(self) -> ComposeResult:
        yield Static("Add Todo Screen")
        yield ScrollableContainer(
            Static("This screen is intended for the user who wants to add a small number of Todos\n"
                   "Please ensure that you have filled in all fields before clicking 'Add Todo'\n"
                   "For bulk additions please use Dr_Egeria instead."),
            Input("Name of Todo", id="todo_name"),
            Input("Description of Todo", id="todo_description"),
            Input("Priority of Todo", id="todo_priority"),
            Static("Status will be automatically set to 'REQUESTED'"),
            Horizontal(
                Button("Add Todo", id="add_todo_button", variant="primary"),
                Button("Quit", id="quit_button", variant="warning")
            ))

    def action_add_new_todo(self):
        """ Call Egeria to add the new todo """
        tclient = Egeria(
            view_server=self.view_server,
            platform_url=self.platform_url,
            user_id=self.user_name,
            user_pwd=self.user_password
        )

        try:
            tclient.create_egeria_bearer_token()
            todo_guid = tclient.create_my_todo(
                todo_name=self.todo_name,
                description=self.todo_description,
                priority=self.todo_priority,
                activity_status="REQUESTED"
            )
            self.log(f"Created ToDo assigned to the current user: {todo_guid}")
        except PyegeriaException as e:
            self.notify(f"Add todo failed with return: {e}", timeout=10, severity="error")
        finally:
            tclient.close_session()
            self.todo_name = ""
            self.todo_description = ""
            self.todo_priority = ""
            self.todo_guid = ""
            self.query_one("#todo_name", Input).clear()
            self.query_one("#todo_description", Input).clear()
            self.query_one("#todo_priority", Input).clear()
        return

    @on(Input.Changed)
    def handle_input_changed(self, event: Input.Changed):
        if event.input.id == "todo_name":
            self.todo_name = event.input.value
        if event.input.id == "todo_description":
            self.todo_description = event.input.value
        if event.input.id == "todo_priority":
            self.todo_priority = event.input.value

    def action_quit(self):
        self.dismiss(200)

    @on(Button.Pressed, "#add_todo_button")
    def handle_add_todo_button(self, event: Button.Pressed):
        """ Handle the add button press """
        if self.todo_name and self.todo_description:
            self.action_add_new_todo()
        else:
            self.notify("Please enter at least anew todo name and description", timeout=10, severity="error")

    @on(Button.Pressed, "#quit_button")
    def handle_quit_button(self, event: Button.Pressed):
        """ Handle the quit button press """
        self.action_quit()
