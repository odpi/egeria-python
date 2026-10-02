"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""
from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.css.query import NoMatches
from textual.screen import ModalScreen
from textual.widgets import DataTable, Header, Static, Footer, Input, Button

from pyegeria import PyegeriaException, EgeriaTech, exec_report_spec, load_app_config, settings


class ShowCommentsScreen(ModalScreen):
    """Show any comments for an element Screen for My Profile App."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+a", "add_comment", "Add Comment"),
        ("ctrl+r", "add_response", "Add Response"),
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(
        self,
        table_name: str | None = None,
        table_row: Any = None,
        *args,
        selected_comment_guid: str | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        load_app_config()
        # The comment whose responses this screen shows (None = show an element's comments)
        self.selected_comment_guid = selected_comment_guid or None
        # The comment currently highlighted in the DataTable (target for Ctrl+R)
        self.highlighted_comment_guid: str | None = None
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.table = table_name
        self.row = table_row
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.selected_row = ""
        self.comment_text = ""
        self.comment_type = ""
        self.backend_id = ""
        # Columns are added in on_mount: DataTable.add_columns needs an active app
        self.show_comments_datatable: DataTable = DataTable(id="show_comments_dt", cursor_type="row", zebra_stripes=True)
        self.dt_row_selected = None
        self.comment_guid = ""

    def on_mount(self):
        """On mount, find the GUID for the Row """
        self.title = "Egeria - My Profile"
        self.sub_title = "Show Comments"
        self.dt_row_selected = None
        self.show_comments_datatable.add_columns("Comment", "GUID", "Qualified Name", "Name")
        if self.selected_comment_guid:
            # Responding to a comment: a response is just a comment attached to the comment element
            backend_id = self.selected_comment_guid
        else:
            # Extract the correct string identifier
            backend_id = self.extract_backend_identifier(self.table, self.row)
            self.log(f"Backend identifier: {backend_id} extracted")
        if not backend_id:
            self.notify("Selected table does not contain valid GUID or Qualified Name columns.", severity="error")
            return

        self.notify(f"Accessing backend system with identifier: {backend_id}")
        self.backend_id = backend_id
        self.load_comments(backend_id)

    def load_comments(self, element_guid: str) -> None:
        """Fetch the comments attached to element_guid and show them in the DataTable."""
        try:
            comments_list = exec_report_spec(
                format_set_name="Comment-by-Element",
                output_format="DICT",
                params={"element_guid": element_guid, "graph_query_depth": 0},  # comment properties only
                view_server=self.view_server,
                view_url=self.platform_url,
                user=self.user_name,
                user_pass=self.user_password,
            )
        except PyegeriaException as e:
            self.notify(f"No comments found: {str(e)}", severity="warning")
            return

        self.log(f"comments_list: {comments_list}")
        comment_table = self.show_comments_datatable
        if isinstance(comments_list, dict):
            if comments_list.get("kind") == "json":
                comments_list_ext = comments_list.get("data") or []
                self.log(f"comments_list_ext: {comments_list_ext}, len: {len(comments_list_ext)}")
                for comment in comments_list_ext:
                    self.log(f"processing value: {comment}")
                    comment_table.add_row(comment.get('Description'), comment.get('Comment Guid'),
                                          comment.get('Qualified Name'), comment.get('Display Name'))
        elif isinstance(comments_list, str):
            self.log(f"processing str comment: {comments_list}")
            comment_table.add_row(comments_list, "", "", "")
        elif comments_list:
            self.log(f"processing list of: {len(comments_list)} comments")
            for comment in comments_list:
                comment_table.add_row(str(comment), "", "", "")

        if comment_table.row_count == 0:
            if self.selected_comment_guid:
                self.notify("This comment has no responses yet - use Ctrl+A to add one", timeout=10)
            else:
                self.notify("Selected element does not have any comments - use Ctrl+A to add one", timeout=10)
            return

        # Mount the table once, after all rows have been added
        container = self.query_one("#show_comments_container", ScrollableContainer)
        container.mount(comment_table)
        container.mount(Static("Ctrl+R on a highlighted comment to view and add responses to it"))

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
            # use pyegeria to get a GUID for that Qualified Name entity and use it as the index (upper)
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
        if self.selected_comment_guid:
            heading = f"Responses to comment: {self.selected_comment_guid}"
        else:
            heading = f"Show Comments for: {self.table}"
        yield Header(show_clock=True)
        yield Static(classes="empty")
        yield ScrollableContainer(
            Static(heading, id="show_comments_static"),
            id="show_comments_container"
        )
        yield Footer()

    def action_add_comment(self):
        """ Add an attached Comment to the selected row """
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

    def action_add_response(self):
        """ Reopen this screen focused on the highlighted comment, to view/add responses to it """
        if self.highlighted_comment_guid:
            self.log(f"Add response to comment: Selected row: {self.highlighted_comment_guid}")
            self.dismiss([250, self.highlighted_comment_guid])
        else:
            self.notify("Highlight a comment in the table first, to respond to it", severity="warning")

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

    @on(Button.Pressed, "#add_comment_button")
    def handle_button_pressed(self, event: Button.Pressed):
        """ Handle user request to add a comment to the selected element """
        self.log(f"Button pressed: {event.button.id}")
        self.log(f"Comment text: {self.comment_text}, Comment type: {self.comment_type}")
        if self.comment_text and self.comment_type:
            # add_comment dismisses the screen itself on success, and stays open on failure
            self.add_comment()
        else:
            self.notify("Both comment text and comment type are required!")
            return

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
            self.comment_type = self.comment_type.strip().upper().replace(" ", "_")
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
        except Exception as e:
            self.log(f"Failed to add comment: {e}")
            self.notify(f"Failed to add comment: {e} \n Please try again.")
            return
        self.dismiss(200)

    @on(DataTable.RowHighlighted, "#show_comments_dt")
    def on_row_highlighted(self, event: DataTable.RowHighlighted):
        self.log(f"Row highlighted: {event.row_key}")
        self._track_comment_row(event.row_key)

    @on(DataTable.RowSelected, "#show_comments_dt")
    def on_row_selected(self, event: DataTable.RowSelected):
        self.log(f"Row selected: {event.row_key}")
        self._track_comment_row(event.row_key)

    def _track_comment_row(self, row_key) -> None:
        """Remember the GUID (column 1) of the comment under the cursor."""
        self.dt_row_selected = row_key
        try:
            row_data = self.show_comments_datatable.get_row(row_key)
        except Exception as e:
            self.log(f"Unable to read comment row {row_key}: {e}")
            self.highlighted_comment_guid = None
            return
        self.highlighted_comment_guid = row_data[1] or None
        self.comment_guid = self.highlighted_comment_guid or ""
        
    def action_quit(self):
        self.app.pop_screen()