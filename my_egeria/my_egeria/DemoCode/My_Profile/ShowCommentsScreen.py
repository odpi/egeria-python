"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""
from typing import Any

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.css.query import NoMatches
from textual.screen import ModalScreen
from textual.widgets import DataTable, Header, Static, Footer, Input, Button

from pyegeria import PyegeriaException, EgeriaTech, exec_report_spec


class ShowCommentsScreen(ModalScreen):
    """Main Screen for My Profile App."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+a", "add_comment", "Add Comment")
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, table_name, table_row, view_server, platfgorm_url, user_name, user_password, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = table_name
        self.row = table_row
        self.view_server = view_server
        self.platform_url = platfgorm_url
        self.user_name = user_name
        self.user_password = user_password
        self.selected_row = ""
        self.comment_text = ""
        self.comment_type = ""
        self.backend_id = ""
        self.show_comments_datratable: DataTable = DataTable(id="show_comments_dt")

    def on_mount(self):
        """On mount, find the GUID for the Row """
        self.title = "Egeria - My Profile"
        self.sub_title = "Show Comments"
        # Extract the correct string identifier
        backend_id = self.extract_backend_identifier(self.table, self.row)
        self.log(f"Backend identifier: {backend_id} extracted")
        if backend_id:
            self.notify(f"Accessing backend system with identifier: {backend_id}")
            self.backend_id = backend_id
            try:
                comments_list: dict = exec_report_spec(format_set_name="Comment-by-Element",
                                                       output_format="DICT",
                                                       params={"element_guid" : backend_id,})
                if isinstance(comments_list, str) or comments_list == "No elements found":
                    self.log(f"processing str comment: {comments_list}")
                    comment_text = str(comments_list)
                    self.query_one("#show_comments_container", ScrollableContainer).mount(Static(comment_text))
                elif isinstance(comments_list, dict):
                    comment_count = 0
                    structured_comments: list[list] = []
                    comment_text: list[Any] = []
                    for key, value in comments_list:
                        structured_comments[comment_count] = (key,
                                                              value["Display Name"],
                                                              value["Qualified Name"],
                                                              value["Comment Guid"],
                                                              value["Description"])
                        comment_count += 1
                    for row in structured_comments:
                        comment_text.append[row]
                        self.query_one("#show_comments_container", ScrollableContainer).mount(Static(row))
                else:
                    self.log(f"processing list of: {len(comments_list)} comments")
                    for comment in comments_list:
                        comment_text = str(comment)
                        self.query_one("#show_comments_container", ScrollableContainer).mount(Static(comment_text))
            except PyegeriaException as e:
                self.notify(f"No comments found: {str(e)}", severity="warning")
        else:
            self.notify("Selected table does not contain valid GUID or Qualified Name columns.", severity="error")

    def extract_backend_identifier(self, table_name, row_key):
        try:
            # Query the table from the current active screen (MainScreen)
            # We look for the screen with id 'main_screen' if it's not the current one
            try:
                target_screen = self.app.get_screen("main_screen")
            except KeyError:
                target_screen = self.app.get_screen("main")
            
            table_addr = target_screen.query_one(f"#{table_name}", DataTable)
        except (NoMatches, KeyError):
            try:
                # Fallback to current screen
                table_addr = self.app.screen.query_one(f"#{table_name}", DataTable)
            except NoMatches:
                self.log(f"Table {table_name} not found on any relevant screen")
                return None

        # Map the clean string representation of column labels to their index positions
        column_mapping = {col.label.plain.strip(): idx for idx, col in enumerate(table_addr.columns.values())}
        self.log(f"Column mapping for table {table_name}: {column_mapping}")

        # Case-insensitive check for target columns
        upper_mapping = {k.upper(): v for k, v in column_mapping.items()}
        idx = None
        if "GUID" in upper_mapping:
            idx = upper_mapping["GUID"]
        elif "QUALIFIED NAME" in upper_mapping:
            # use pyegeria to obtain a GUID for that Qualified Name entity and use it as the index (upper)
            comment_attributes = exec_report_spec(format_set_name="Search-Keywords",
                                                   output_format="DICT",
                                                   params=({"search_string":upper_mapping["QUALIFIED NAME"]}))
            backend_id = comment_attributes["GUID"]
            idx = backend_id
        self.log(f"Target column idx value: {idx}")
        if idx is None:
            self.log(f"Target columns GUID or Qualified Name not found in {list(column_mapping.keys())}")
            return None

        self.selected_row = idx
        self.log(f"Selected row index: {self.selected_row}")

        try:
            # handle if row_key is RowKey object or string
            actual_row_key = row_key
            row_data = table_addr.get_row(actual_row_key)
            self.log(f"Row data: {row_data}")
            return str(row_data[idx])
        except Exception as e:
            self.log(f"Error retrieving row {row_key} from table {table_name}: {e}")
            return None


    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield ScrollableContainer(
            Static(f"Show Comments for: {self.table}", id="show_comments_static"),
            id="show_comments_container"
        )
        yield Footer()

    def action_add_comment(self):
        """ Add an attached Comment to thew selected row """
        if self.backend_id:
            self.log(f"Selected row: {self.backend_id}")
            container = (self.query_one("#show_comments_container", ScrollableContainer))
            container.remove_children()
            container.mount(Static(f"[b]Add Comment[/b]"))
            container.mount(Input(placeholder="Enter comment", id="add_comment_input"))
            container.mount(Static(f"Valid comment types are: Question, Answer, Suggestion and Requirement"))
            container.mount(Input(placeholder="Comment Type: Question, Suggestion, etc.", id="add_comment_type_input"))
            container.mount(Button("Add", id="add_comment_button"))
        else:
            self.notify("No row selected, a selected row is required to add a comment!")

    def on_input_changed(self, event: Input.Changed):
        self.log(f"Input detected: {event.input.id}, {event.input.value}")
        if event.input.id == "add_comment_input":
            self.log(f"Input changed: {event.input.value}")
            self.comment_text = str(event.input.value)
        elif event.input.id == "add_comment_type_input":
            self.log(f"Input changed: {event.input.value}")
            self.comment_type = str(event.input.value)
        else:
            self.notify("Input not recognized! Please try again")
            return
        self.log(f"Comment text: {self.comment_text}, Comment type: {self.comment_type}")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "add_comment_button":
            self.log(f"Button pressed: {event.button.id}")
            self.log(f"Comment text: {self.comment_text}, Comment type: {self.comment_type}")
            if self.comment_text and self.comment_type:
                self.add_comment()
            else:
                self.notify("Both comment text and comment type are required!")
                return
        else:
            self.notify("Button not recognized! Please try again")

    def add_comment(self):
        if not self.comment_text or not self.comment_type or not self.backend_id:
            self.notify("A row must be selected and Both comment text and comment type are required!")
            return

        try:
            egeria_tech = EgeriaTech(self.view_server,
                                     self.platform_url,
                                     self.user_name,
                                     self.user_password)
            egeria_tech.create_egeria_bearer_token(self.user_name, self.user_password)
        except PyegeriaException as e:
            self.notify(f"Error creating Egeria Tech object: {e}", timeout=5, severity="error")
            self.notify("Unable to connect to the Egeria Server, please check the server is running and your credentials and try again",
                        timeout=10,
                        severity="error")
            return

        try:
            # Add comment to selected element
            self.comment_type = self.comment_type.upper()
            self.log(f"Adding comment to element: {self.backend_id}, values: {self.comment_text}, {self.comment_type}")
            response = egeria_tech.add_comment_to_element(
                element_guid=self.backend_id,
                comment=self.comment_text,
                comment_type=self.comment_type
            )
            self.log(f"Comment successfully added! New Comment GUID: {response}")
            self.notify(f"Comment successfully added! New Comment GUID: {response}")
            container = (self.query_one("#show_comments_container", ScrollableContainer))
            container.remove_children()
            rc = 200
        except Exception as e:
            self.log(f"Failed to add comment: {e}")
            self.notify(f"Failed to add comment: {e} \n Please try again.")
            rc = 400
        self.dismiss()

    def action_quit(self):
        self.app.pop_screen()