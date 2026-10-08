# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Glossary related functions of my_egeria module.


"""

from textual.widgets import Static
from textual.containers import Vertical
from my_egeria.widgets.editable_table import EditableDataTable
from my_egeria.services.glossary_service import GlossaryService
from my_egeria.screens.base_screen import BaseScreen

class GlossaryListScreen(BaseScreen):
    CSS_PATH = ["../styles/common.css", "/styles/glossary_list_screen.css"]
    """Screen showing list of glossaries in a table."""

    def __init__(self, glossary_service: GlossaryService) -> None:
        super().__init__()
        self.glossary_service = glossary_service
        self.table = EditableDataTable(id="glossary-table")

    def compose(self):
        yield from super().compose()
        yield Vertical(
            Static("Glossaries", classes="header"),
            self.table,
        )

    async def on_mount(self):
        await super().on_mount()
        self.table.add_columns("Glossary Name", "Description")
        glossaries = await self.glossary_service.list_glossaries_async()
        for g in glossaries or []:
            name = g.get("display_name") or g.get("displayName") or g.get("qualified_name") or g.get("qualifiedName") or ""
            desc = g.get("description") or g.get("summary") or ""
            self.table.add_row(name, desc)
        self.table.focus()

    async def on_editable_data_table_row_selected(self, event):
        selected_row = self.table.get_row_at(event.cursor_row)
        glossary_name = selected_row[0]
        self.app.show_term_list(glossary_name)
