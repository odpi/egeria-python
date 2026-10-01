"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides the screens for the app-wide feedback mechanism in my_egeria:
   a form to leave feedback from any screen, and a viewer for the private feedback
   note log (see feedback_handler.py for the Egeria side).

"""
from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Header, Static, Footer, Button, DataTable, Select, TextArea

FEEDBACK_CATEGORIES = ["Bug", "Suggestion", "Question", "Praise", "Other"]


class FeedbackScreen(ModalScreen):
    """ Collect feedback about the screen the user was on when they pressed the feedback key """

    BINDINGS = [
        ("ctrl+s", "submit", "Submit Feedback"),
        ("escape", "cancel", "Cancel"),
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, screen_name: str, screen_title: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.screen_name = screen_name
        self.screen_title = screen_title
        self.category = FEEDBACK_CATEGORIES[1]

    def on_mount(self):
        self.title = "Egeria - My Profile"
        self.sub_title = "Leave Feedback"
        self.query_one("#feedback_text", TextArea).focus()

    def compose(self) -> ComposeResult:
        """This method composes the UI for the FeedbackScreen."""
        context = self.screen_name if not self.screen_title else f"{self.screen_name} ({self.screen_title})"
        yield Header(show_clock=True)
        yield Static("Leave Feedback", classes="span-3", id="feedback_title")
        yield ScrollableContainer(
            Static(f"[b]Feedback on:[/b] {context}"),
            Static("Category"),
            Select(
                [(category, category) for category in FEEDBACK_CATEGORIES],
                value=self.category,
                allow_blank=False,
                id="feedback_category",
            ),
            Static("Feedback"),
            TextArea(id="feedback_text"),
            Static("Your feedback is recorded in a private feedback log. Use Cancel to return to the previous screen"),
            Horizontal(
                Button("Submit", id="submit_feedback_button", variant="primary"),
                Button("Cancel", id="cancel_feedback_button", variant="warning"),
            ),
            id="feedback_container",
        )
        yield Footer()

    @on(Select.Changed, "#feedback_category")
    def handle_category_changed(self, event: Select.Changed):
        self.category = str(event.value)

    def action_submit(self):
        feedback_text = self.query_one("#feedback_text", TextArea).text.strip()
        if not feedback_text:
            self.notify("Please enter some feedback before submitting", timeout=5, severity="warning")
            return
        feedback_data = {
            "screen": self.screen_name,
            "screen_title": self.screen_title,
            "category": self.category,
            "text": feedback_text,
        }
        self.log(f"Feedback data: {feedback_data} being returned from screen")
        self.dismiss(feedback_data)

    def action_cancel(self):
        self.dismiss(None)

    @on(Button.Pressed, "#submit_feedback_button")
    def handle_submit_button(self):
        self.action_submit()

    @on(Button.Pressed, "#cancel_feedback_button")
    def handle_cancel_button(self):
        self.action_cancel()


class FeedbackLogScreen(ModalScreen):
    """ Show the accumulated entries in the private feedback note log """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "quit", "Back"),
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, feedback_entries: list[dict[str, Any]], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.feedback_entries = feedback_entries or []

    def on_mount(self):
        self.title = "Egeria - My Profile"
        self.sub_title = f"Feedback Log ({len(self.feedback_entries)} entries)"
        table = self.query_one("#feedback_log_table", DataTable)
        table.add_columns("Date", "Submitted By", "Category", "Screen", "Feedback")
        table.zebra_stripes = True
        table.cursor_type = "row"
        if not self.feedback_entries:
            table.add_row("", "", "", "", "No feedback has been recorded yet")
        for entry in self.feedback_entries:
            table.add_row(
                str(entry.get("date", "")),
                str(entry.get("submitted_by", "")),
                str(entry.get("category", "")),
                str(entry.get("screen", "")),
                str(entry.get("text", "")),
            )
        table.focus()

    def compose(self) -> ComposeResult:
        """This method composes the UI for the FeedbackLogScreen."""
        yield Header(show_clock=True)
        yield Static("Feedback Log", classes="span-3", id="feedback_log_title")
        yield ScrollableContainer(
            DataTable(id="feedback_log_table"),
            id="feedback_log_container",
        )
        yield Footer()

    def action_quit(self):
        self.dismiss(200)
