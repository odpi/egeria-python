# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Glossary related functions of my_egeria module.


"""

from textual.widgets import Static
from textual.containers import Vertical
from my_egeria.widgets.editable_table import EditableDataTable
from my_egeria.services.term_service import get_terms_for_glossary
from ..base_screen import BaseScreen


class TermListScreen(BaseScreen):
    CSS_PATH = ["../styles/common.css", "/styles/term_list_screen.css"]
    """Screen showing list of terms for a given glossary."""

    def __init__(self, glossary_name: str) -> None:
        super().__init__()
        self.term_service = get_terms_for_glossary
        self.glossary_name = glossary_name
        self.query_one()

    def compose(self):
        yield from super().compose()
        yield Vertical(
            Static(f"Terms in Glossary: {self.glossary_name}", classes="header"),
            self.table,
        )

    async def on_mount(self):
        await super().on_mount()
        self.table.add_columns("Term Name", "Description")
        terms = self.term_service(self, glossary_name=self.glossary_name) or []
        for t in terms:
            self.table.add_row(getattr(t, "name", ""), getattr(t, "description", "") or "")
        self.table.focus()
