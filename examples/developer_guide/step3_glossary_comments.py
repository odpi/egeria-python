"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Developer Guide step 3: act on the selected DataTable row. Ctrl+A opens a modal screen,
   pre-filled with the selected glossary's GUID, that adds a comment to it in Egeria.
   This is the same pattern My Profile uses for comments and bookmarks.

   Run:  python examples/developer_guide/step3_glossary_comments.py
"""

from pyegeria import EgeriaTech, PyegeriaException
from textual import on, work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Input, Label, Select

from step2_glossary_browser import GlossaryBrowserApp

COMMENT_TYPES = ["STANDARD_COMMENT", "QUESTION", "SUGGESTION", "USAGE_EXPERIENCE", "REQUIREMENT"]


class AddCommentScreen(ModalScreen[tuple[str, str, str] | None]):
    """Collect a comment for an element. Dismisses with (guid, comment, comment_type), or None if cancelled."""

    CSS = """
    AddCommentScreen { align: center middle; }
    #dialog { width: 90; height: auto; padding: 1 2; border: thick $primary; background: $surface; }
    #dialog Input, #dialog Select { margin-bottom: 1; }
    #buttons { height: auto; align-horizontal: right; }
    #buttons Button { margin-left: 2; }
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    def __init__(self, element_name: str, element_guid: str) -> None:
        super().__init__()
        self.element_name = element_name
        self.element_guid = element_guid

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label(f"Add a comment to [b]{self.element_name}[/b]")
            # value= pre-fills the GUID from the selected row; the user can still change it
            yield Input(value=self.element_guid, placeholder="GUID of the element", id="guid")
            yield Input(placeholder="Comment text", id="comment")
            yield Select([(t.replace("_", " ").title(), t) for t in COMMENT_TYPES],
                         value="STANDARD_COMMENT", allow_blank=False, id="comment_type")
            with Horizontal(id="buttons"):
                yield Button("Add Comment", variant="primary", id="add")
                yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        self.query_one("#comment", Input).focus()

    @on(Button.Pressed, "#add")
    def handle_add(self) -> None:
        guid = self.query_one("#guid", Input).value.strip()
        comment = self.query_one("#comment", Input).value.strip()
        if not guid or not comment:
            self.notify("Both a GUID and comment text are required", severity="warning")
            return
        self.dismiss((guid, comment, self.query_one("#comment_type", Select).value))

    @on(Button.Pressed, "#cancel")
    def action_cancel(self) -> None:
        self.dismiss(None)


class GlossaryCommentsApp(GlossaryBrowserApp):
    """The step 2 browser, plus a Ctrl+A action that comments on the selected glossary."""

    SUB_TITLE = "Glossary Comments"

    BINDINGS = [("ctrl+a", "add_comment", "Comment on Selected Row")]

    def action_add_comment(self) -> None:
        table = self.query_one("#glossary_table", DataTable)
        if table.row_count == 0:
            self.notify("There are no rows to comment on", severity="warning")
            return
        # The cursor position identifies the selected row; step 2 used the GUID as the row key
        row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
        name = table.get_row(row_key)[0]
        self.push_screen(AddCommentScreen(name, row_key.value), callback=self.comment_entered)

    def comment_entered(self, result: tuple[str, str, str] | None) -> None:
        """Called with the value the AddCommentScreen was dismissed with."""
        if result:
            self.add_comment(*result)

    @work(thread=True)
    def add_comment(self, guid: str, comment: str, comment_type: str) -> None:
        conn = self.conn
        client = EgeriaTech(conn.view_server, conn.platform_url, conn.user_name, conn.user_password)
        try:
            client.create_egeria_bearer_token(conn.user_name, conn.user_password)
            response = client.add_comment_to_element(guid, comment=comment, comment_type=comment_type)
            # A GUIDResponse dict: {"class": "GUIDResponse", "relatedHTTPCode": 200, "guid": "..."}
            comment_guid = response.get("guid") if isinstance(response, dict) else response
            self.call_from_thread(self.notify, f"Comment added, GUID: {comment_guid}")
        except PyegeriaException as e:
            self.call_from_thread(self.notify, f"Unable to add comment: {e}", severity="error")
        finally:
            client.close_session()


if __name__ == "__main__":
    GlossaryCommentsApp().run()
