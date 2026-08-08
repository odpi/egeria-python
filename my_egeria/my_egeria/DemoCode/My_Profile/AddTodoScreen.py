"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a user screen to allow the user to add todos to my_egeria.

"""
import pwd

from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import DataTable, OptionList, Header, Static, Footer, Input, Button
from textual.widgets._option_list import Option

from pyegeria import Egeria, PyegeriaException


class AddTodoScreen(ModalScreen):
    """Main Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+a", "add_new_role", "Add New Role")
        ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, selected_table, *args, **kwargs):
        super().__init__(id="main_screen", *args, **kwargs)
        self.selected_table = selected_table

    def on_mount(self):
        main_screen = self.app.get_screen("main")

        self.todos_table = main_screen.query_one("#todos_table", DataTable)
        assert self.todos_table is not None

        self.todos_table.zebra_stripes = True
        self.todos_table.cursor_type = "row"

    def compose(self) -> ComposeResult:
        yield Static("Add Todo Screen")
        yield Static("This screen is intended for the user who wants to add a small number of Todos\n"
                     "Please ensure that you have filled in all fields before clicking 'Add Todo'\n"
                     "For bulk additions please use Dr_Egeria instead.")
        yield Input("Name of Todo", id="todo_name")
        yield Input("Description of Todo", id="todo_description")
        yield Input("Priority of Todo", id="todo_priority")
        yield Static("Status will be automatically set to 'REQUESTED'")
        yield Button("Add Todo", id="add_todo_button", variant="primary")

    def action_add_new_role(self):
        client = Egeria(
            view_server=self.view_server,
            platform_url=self.platform_url,
            user_id=self.user_name,
            user_pwd=self.user_password,
        )

        try:
            client.create_egeria_bearer_token()

            todo_guid = client.create_my_todo(
                todo_name=self.todo_name,
                description=self.todo_description,
                priority=self.todo_priority,
                activity_status="REQUESTED"
                )
           self.log(f"Created ToDo assigned to the current user: {todo_guid}")
        except PyegeriaException as e:
            self.notify(f"Add todo failed with return: {e}", timeout=10, severity="error")
        finally:
            client.close_session()
        pass

    @on(Input.Changed)
    def handle_input_changed(self, event: Input.Changed):
        if event.input.id == "todo_name":
            self.todo_name = event.input.value
        if event.input.id == "todo_description":
            self.todo_description = event.input.value
        if event.input.id == "todo_priority":
            self.todo_priority = event.input.value