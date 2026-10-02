"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Developer Guide step 2: a Textual app that shows Egeria glossaries in a DataTable.
   The Egeria call runs in a thread worker so the UI stays responsive while it loads.

   Run:  python examples/developer_guide/step2_glossary_browser.py
"""

from pyegeria import PyegeriaException
from textual import work
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer, Header, Static

from common import connection_settings, fetch_glossaries


class GlossaryBrowserApp(App):
    """List the glossaries known to Egeria."""

    TITLE = "Egeria"
    SUB_TITLE = "Glossary Browser"

    CSS = """
    #heading { padding: 1 2; text-style: bold; }
    DataTable { height: 1fr; }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.conn = connection_settings()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(f"Glossaries visible to {self.conn.user_name}", id="heading")
        yield DataTable(id="glossary_table", cursor_type="row", zebra_stripes=True)
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#glossary_table", DataTable)
        table.add_columns("Display Name", "Qualified Name", "GUID")
        self.action_refresh()

    def action_refresh(self) -> None:
        """Bound to "r": clear the table and reload it from Egeria."""
        table = self.query_one("#glossary_table", DataTable)
        table.clear()
        table.loading = True
        self.load_glossaries()

    @work(thread=True, exclusive=True)
    def load_glossaries(self) -> None:
        """Runs in a background thread. Widgets must only be updated on the UI thread,
        so the results are handed back with call_from_thread."""
        try:
            glossaries = fetch_glossaries(self.conn)
        except PyegeriaException as e:
            self.call_from_thread(self.notify, f"Egeria request failed: {e}", severity="error")
            glossaries = []
        self.call_from_thread(self.show_glossaries, glossaries)

    def show_glossaries(self, glossaries: list[dict]) -> None:
        table = self.query_one("#glossary_table", DataTable)
        for glossary in glossaries:
            # The GUID doubles as the row key, so it can be looked up directly later
            table.add_row(glossary["Display Name"], glossary["Qualified Name"], glossary["GUID"],
                          key=glossary["GUID"])
        table.loading = False
        self.notify(f"Loaded {len(glossaries)} glossaries")


if __name__ == "__main__":
    GlossaryBrowserApp().run()
