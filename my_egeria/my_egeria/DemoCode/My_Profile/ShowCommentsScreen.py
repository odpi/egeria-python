"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import Screen, ModalScreen
from textual.widgets import DataTable, OptionList, Header, Static, Footer
from textual.widgets._option_list import Option

from pyegeria import Egeria, PyegeriaException


class ShowCommentsScreen(ModalScreen):
    """Main Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+a", "add_comment", "Add Comment")
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, table_name, table_row, view_server, platfgorm_url, user_name, user_password):
        super().__init__(id="main_screen")
        self.title = "Egeria - My Profile"
        self.sub_title = "Show Comments"
        self.table = table_name
        self.row = table_row
        self.view_server = view_server
        self.platform_url = platfgorm_url
        self.user_name = user_name
        self.user_password = user_password

    def on_mount(self):
        """On mount, access the DataTable, and find the GUID for the Row """
        table_addr = self.query_one(f"#{self.table}", DataTable)
        table_row_data = table_addr.get_row(self.row)
        column_names = [column.label for column in table_addr.columns.values()]

        # Extract the correct string identifier
        backend_id = self.extract_backend_identifier(self.table, self.row)

        if backend_id:
            self.notify(f"Accessing backend system with identifier: {backend_id}")
            try:
                cclient = Egeria.Client(self.view_server,
                                        self.platform_url,
                                        self.user_name,
                                        self.user_password)
                token = cclient.create_egeria_user_token(self.user_name, self.user_password)
                comments_list = cclient.get_element_comments(backend_id)
                self.log(f"Retrieved {comments_list} comments for element {backend_id}")
                for comment in comments_list:
                    self.query_one("#show_comments_static", Static).mount(Static(text=comment))
            except PyegeriaException as e:
                self.notify(f"No messages found: {str(e)}", severity="warning")
        else:
            self.notify("Selected table does not contain valid GUID or Qualified Name columns.", severity="error")

    def extract_backend_identifier(self, table_addr, row_key):

        # Map the clean string representation of column labels to their index positions
        column_mapping = {str(col.label): idx for idx, col in enumerate(table_addr.columns.values())}

        # Check for target columns
        if "GUID" in column_mapping:
            idx = column_mapping["GUID"]
        elif "Qualified Name" in column_mapping:
            idx = column_mapping["Qualified Name"]
        else:
            return None
        try:
            row_data = table_addr.get_row(row_key)
            return str(row_data[idx])
        except KeyError:
            return None


    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, id="show_comments_header")
        yield ScrollableContainer(
            Static(f"Show Comments for: {self.table}", id="show_comments_static"),
            id="show_comments_container"
        )
        yield Footer()

    def action_add_comment(self):
        pass