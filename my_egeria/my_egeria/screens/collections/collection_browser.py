# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Collections related functions of my_egeria module.


"""

from textual.widgets import DataTable
from textual.widgets import Button, Input, Static
from textual.containers import Container, Vertical, Horizontal
# from textual.geometry import Coordinate  # remove unused/unsupported import
from ..base_screen import BaseScreen
from my_egeria.services.collection_service import CollectionService
from .add_collection import AddCollectionScreen
from .delete_collection import DeleteCollectionScreen
import asyncio
from textual import on
# ... existing imports ...

class CollectionBrowserScreen(BaseScreen):
    CSS_PATH = ["../../styles/common.css", "../../styles/collection_browser.css"]
    BINDINGS = [
        ("r", "refresh", "Refresh"),
        ("n", "new", "New Collection"),
        ("q", "back", "Back"),
        ("escape", "back", "Back"),
    ]


    def compose(self):
        yield from super().compose()
        # Simple vertical layout: top (list), search (fixed 5 rows), spacer, bottom (buttons)
        yield Vertical(
            # Top: Title + Table
            Container(
                Vertical(
                    Static("Collections", id="c_title"),
                    DataTable(id="collection-table"),
                    id="c_top_content",
                ),
                id="c_top_row",
            ),
            # Search (fixed 5 rows)
            Container(
                Horizontal(
                    Input(placeholder="Search collections...", id="search-input"),
                    Button("Search", id="search-button"),
                    id="c_search_row",
                ),
                id="c_search_row_container",
            ),
            # Flexible spacer to push buttons to bottom
            Container(id="c_spacer"),
            # Bottom: action buttons
            Container(
                Horizontal(
                    Button("Add New Collection", id="new-button"),
                    Button("Delete Selected Collection", id="delete-button"),
                    Button("Back", id="back-button"),
                    id="c_action_row",
                ),
                id="c_action_row_container",
            ),
            id="c_v_root",
        )

    async def on_mount(self):
        await super().on_mount()
        # Root fills available space
        vroot = self.query_one("#c_v_root", Vertical)
        vroot.styles.width = "100%"
        vroot.styles.height = "100%"
        vroot.styles.gap = 0

        # Top row: fixed percentage so the table is always visible
        top_row = self.query_one("#c_top_row", Container)
        top_row.styles.width = "100%"
        top_row.styles.height = "60%"  # take the top ~60% of the screen
        top_row.styles.padding = (1, 2)

        top_content = self.query_one("#c_top_content", Vertical)
        top_content.styles.width = "100%"
        top_content.styles.height = "100%"
        top_content.styles.gap = 1

        title = self.query_one("#c_title", Static)
        title.styles.text_align = "center"
        title.styles.text_style = "bold"
        title.styles.margin = (0, 0, 1, 0)

        # Table fills remaining space within top_row
        self.table = self.query_one("#collection-table", DataTable)
        self.table.styles.height = "100%"
        self.table.styles.min_height = 8
        self.table.cursor_type = "row"

        # Search row: fixed ~5 lines height
        sbox = self.query_one("#c_search_row_container", Container)
        sbox.styles.width = "100%"
        sbox.styles.height = 5
        sbox.styles.padding = (0, 1)
        sbox.styles.border = ("solid", "blue")

        srow = self.query_one("#c_search_row", Horizontal)
        srow.styles.align_horizontal = "center"
        srow.styles.gap = 1

        sinput = self.query_one("#search-input", Input)
        sinput.styles.width = "40%"
        sinput.styles.margin = (1, 0, 1, 0)

        sbtn = self.query_one("#search-button", Button)
        sbtn.styles.margin = (1, 0, 1, 0)

        # Spacer flexes to keep buttons at bottom
        spacer = self.query_one("#c_spacer", Container)
        spacer.styles.height = "1fr"

        # Bottom action bar
        abox = self.query_one("#c_action_row_container", Container)
        abox.styles.width = "100%"
        abox.styles.height = "auto"
        abox.styles.padding = (1, 2)

        arow = self.query_one("#c_action_row", Horizontal)
        arow.styles.align_horizontal = "center"
        arow.styles.gap = 1

        # Service and initial load
        self.service = CollectionService()
        self.table.clear()
        self.table.add_columns("GUID", "Display Name", "Qualified Name", "Description")
        self.last_selected_guid = ""  # track selection defensively
        await self.load_collections()
        # Ensure the table has focus for key handling (use Screen API)
        try:
            self.set_focus(self.table)
        except Exception:
            pass

    # Defensive row highlight/selection handlers
    async def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted):
        """
        Textual may emit RowHighlighted with a None/invalid row_key during updates.
        Guard get_row with a try/except to avoid crashes.
        """
        try:
            row_data = self.table.get_row(event.row_key)
        except Exception:
            return
        if row_data:
            self.last_selected_guid = row_data[0] or ""

    async def on_data_table_row_selected(self, event: DataTable.RowSelected):
        try:
            row_data = self.table.get_row(event.row_key)
        except Exception:
            return
        if row_data:
            self.last_selected_guid = row_data[0] or ""

    @on(Button.Pressed, "#new-button")
    async def handle_new_button(self, event: Button.Pressed) -> None:
        """Open the Create New Collection screen (non-blocking)."""
        if self._add_open:
            return
        self._add_open = True
        await self.app.push_screen(AddCollectionScreen())

    @on(Button.Pressed, "#delete-button")
    async def handle_delete_button(self, event: Button.Pressed) -> None:
        """Open the Create New Collection screen (non-blocking)."""
        if self._del_open:
            return
        self._del_open = True
        await self.app.push_screen(DeleteCollectionScreen(self.last_selected_guid))

    @on(Button.Pressed, "#back-button")
    async def handle_back_button(self, event: Button.Pressed) -> None:
        """Go back to the previous screen."""
        await self.app.pop_screen()

    async def action_back(self) -> None:
        """Hotkeys q / Esc to go back."""
        await self.app.pop_screen()

    async def on_screen_resume(self):
        """
        When returning from the Add or Delete Collection screen, refresh the list and restore focus.
        """
        await asyncio.sleep(0)  # let the screen stack settle
        self._add_open = False  # reset guard on return
        self._del_open = False # reset guard on return

        # Refresh immediately (don't wait for any message)
        try:
            await self._refresh_and_focus()
        except Exception:
            # If anything goes wrong, still try to restore focus so hotkeys and input work
            try:
                self.set_focus(self.table)
            except Exception:
                pass

    # Helper defined BEFORE handlers that call it to avoid "unresolved reference" warnings
    async def _refresh_and_focus(self):
        await self.load_collections()
        try:
            if self.table.row_count > 0:
                try:
                    self.table.move_cursor(row=0, column=0)
                except Exception:
                    # Fallback removed to avoid Coordinate dependency
                    pass
            self.set_focus(self.table)
        except Exception:
            pass

    @on(AddCollectionScreen.CollectionCreated)
    async def on_collection_created(self, msg: AddCollectionScreen.CollectionCreated):
        """
        Refresh after a collection is created and restore a working input context.
        """
        await self._refresh_and_focus()

    @on(DeleteCollectionScreen.CollectionDeleted)
    async def on_collection_deleted(self, msg: DeleteCollectionScreen.CollectionDeleted):
        """
        Refresh after a collection is created and restore a working input context.
        """
        await self._refresh_and_focus()

    async def action_refresh(self):
        """
        Hotkey handler for 'r' to reload collections.
        """
        await self._refresh_and_focus()

    async def load_collections(self, search: str = ""):
        self.table.clear()
        try:
            collections = await asyncio.to_thread(self.service.list_collections, search or "*")
            if collections:
                for c in collections:
                    guid = (
                        c.get("GUID", "")
                        or c.get("guid", "")
                        or c.get("Id", "")
                        or c.get("ID", "")
                    )
                    display = (
                        c.get("display_name", "")
                        or c.get("displayName", "")
                        or c.get("Display Name", "")
                        or c.get("name", "")
                        or c.get("Name", "")
                    )
                    qname = (
                        c.get("qualified_name", "")
                        or c.get("qualifiedName", "")
                        or c.get("Qualified Name", "")
                    )
                    desc = (
                        c.get("description", "")
                        or c.get("summary", "")
                        or c.get("Description", "")
                    )
                    self.table.add_row(guid, display, qname, desc)
            else:
                self.table.add_row("", "No results found", "", "")
        except Exception as e:
            self.table.add_row("", f"Error: {e}", "", "")
        self.last_selected_guid = ""
        try:
            if self.table.row_count > 0:
                try:
                    self.table.move_cursor(row=0, column=0)
                except Exception:
                    pass
            self.set_focus(self.table)
        except Exception:
            pass
