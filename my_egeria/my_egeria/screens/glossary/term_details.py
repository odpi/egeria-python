# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Glossary related functions of my_egeria module.


"""

from ..base_screen import BaseScreen
from my_egeria.widgets.editable_table import EditableDataTable, CellEdited
from my_egeria.widgets.ok_popup import OkPopup

class TermDetailsScreen(BaseScreen):

    def __init__(self, termguid, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.termguid = termguid

    def on_mount(self):
        pass
    # needs to be rewritten using updated architecture


    # CSS_PATH = ["../styles/common.css", "/styles/term_details.css"]
    #
    # def __init__(self, glossary_guid: str, term_guid: str, **kwargs):
    #     super().__init__(**kwargs)
    #     self.glossary_guid = glossary_guid
    #     self.term_guid = term_guid
    #     self.table = EditableDataTable()
    #
    # def compose(self):
    #     yield Static(f"Term Details: {self.term_guid}", classes="header")
    #     yield Container(self.table)
    #
    # async def on_mount(self):
    #     """Load term details into table."""
    #     details = EgeriaTech.get_term_details(self.term_name, self.term_guid)
    #     for key, value in details.items():
    #         self.table.add_row(key, value)
    #
    # async def on_cell_edited(self, event: CellEdited):
    #     """Handle cell edits and persist changes via pyegeria."""
    #     key = self.table.get_cell_at(event.row, 0)
    #     new_value = event.value
    #
    #     try:
    #         await pyegeria.update_term_property(
    #             self.glossary_guid, self.term_guid, key, new_value
    #         )
    #         await self.mount_popup(OkPopup(f"{key} updated successfully"))
    #     except Exception as e:
    #         # Restore original value
    #         self.table.set_cell_at(event.row, event.column, event.table._original_value)
    #         await self.mount_popup(OkPopup(f"Error updating {key}: {e}"))
    #
    # async def mount_popup(self, popup: OkPopup):
    #     """Show a popup modal."""
    #     await self.mount(popup)
    #     popup.focus()
    #
    # async def on_button_pressed(self, event: Button.Pressed):
    #     if event.button.id == "cancel-btn":
    #         await self.app.pop_screen()
    #         return
