"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a user screen to allow the user to add todos to my_egeria.

"""
import pwd

from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Horizontal
from textual.screen import ModalScreen
from textual.widgets import DataTable, OptionList, Header, Static, Footer, Input, Button
from textual.widgets._option_list import Option

from pyegeria import Egeria, PyegeriaException, load_app_config, settings


class AddTodoScreen(ModalScreen):
    """Main Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+a", "add_new_todo", "Add New Todo")
        ]

    CSS_PATH = "../My_Profile/my_profile.tcss"

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