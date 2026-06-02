# Python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides the main Screen for the Governance Officer related functions of my_egeria module.


"""

from textual.widgets import DataTable
from textual.widgets import Button, Input, Static, Tree
from textual.containers import Container, Vertical, Horizontal
from ..base_screen import BaseScreen
from .marketplace_tree import MarketPlaceTree
from my_egeria.services.governance_officer_service import GovernanceOfficerService
from .add_governance_definition import AddGovernanceDefinitionScreen
from .delete_governance_definition import DeleteGovernanceDefinitionScreen
import asyncio
from textual import on
from my_egeria.utils.config import EgeriaConfig, get_global_config


# ... existing imports ...

class GovernanceOfficerBrowserScreen(BaseScreen):
    CSS_PATH = ["../../styles/common.css", "../../styles/governance_officer_browser.css"]

    BINDINGS = [
        ("r", "refresh", "Refresh"),
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
                    Static("Governance Officer", id="go_title"),
                    DataTable(id="governance-officer-table"),
                    id="go_top_content",
                ),
                id="go_top_row",
            ),
            # Search (fixed 5 rows)
            Container(
                Horizontal(
                    Input(placeholder="Search Governance Definitions...", id="gd-search-input"),
                    Button("Search", id="gd-search-button"),
                    id="go_search_row",
                ),
                id="go_search_row_container",
            ),
            # Flexible spacer to push buttons to bottom
            Container(id="go_spacer"),
            # Bottom: action buttons
            Container(
                Horizontal(
                    Button("Select Definition", id="gd-select-button", disabled = True),
                    Button("Add Governance Definition", id="gd-new-button"),
                    Button("Delete Selected Definition", id="gd-delete-button"),
                    Button("Back", id="back-button"),
                    id="go_action_row",
                ),
                id="go_action_row_container",
            ),
            id="go_v_root",
        )

    async def on_mount(self):
        await super().on_mount()
        # Root fills available space
        vroot = self.query_one("#go_v_root", Vertical)
        vroot.styles.width = "100%"
        vroot.styles.height = "100%"
        vroot.styles.gap = 0

        # Top row: fixed percentage so the table is always visible
        top_row = self.query_one("#go_top_row", Container)
        top_row.styles.width = "100%"
        top_row.styles.height = "60%"  # take the top ~60% of the screen
        top_row.styles.padding = (1, 2)

        top_content = self.query_one("#go_top_content", Vertical)
        top_content.styles.width = "100%"
        top_content.styles.height = "100%"
        top_content.styles.gap = 1

        title = self.query_one("#go_title", Static)
        title.styles.text_align = "center"
        title.styles.text_style = "bold"
        title.styles.margin = (0, 0, 1, 0)

        # Table fills remaining space within top_row
        self.table = self.query_one("#governance-officer-table", DataTable)
        self.table.styles.height = "100%"
        self.table.styles.min_height = 8
        self.table.cursor_type = "row"

        # Search row: fixed ~5 lines height
        sbox = self.query_one("#go_search_row_container", Container)
        sbox.styles.width = "100%"
        sbox.styles.height = 5
        sbox.styles.padding = (0, 1)
        sbox.styles.border = ("solid", "blue")

        srow = self.query_one("#go_search_row", Horizontal)
        srow.styles.align_horizontal = "center"
        srow.styles.gap = 1

        sinput = self.query_one("#gd-search-input", Input)
        sinput.styles.width = "40%"
        sinput.styles.margin = (1, 0, 1, 0)

        sbtn = self.query_one("#gd-search-button", Button)
        sbtn.styles.margin = (1, 0, 1, 0)

        # Spacer flexes to keep buttons at bottom
        spacer = self.query_one("#go_spacer", Container)
        spacer.styles.height = "1fr"

        # Bottom action bar
        abox = self.query_one("#go_action_row_container", Container)
        abox.styles.width = "100%"
        abox.styles.height = "auto"
        abox.styles.padding = (1, 2)

        arow = self.query_one("#go_action_row", Horizontal)
        arow.styles.align_horizontal = "center"
        arow.styles.gap = 1

        # Service and initial load
        self.service = GovernanceOfficerService(config=get_global_config())
        self.table.clear()
        self.table.add_columns("GUID", "Type Name", "Document ID", "Unique Name", "Short Name", "Description")
        self.last_selected_guid = ""  # track selection defensively
        await self.load_governance_officer_definitions()
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

    @on(Button.Pressed, "#gd-select-button")
    async def handle_select_button(self, event: Button.Pressed) -> None:
        """Open the Create New Collection screen (non-blocking)."""
        if self.last_selected_guid:
            # Find the Root(s) for that selected type and display a table of them to select from,
            # could be a tree maybe betterand display 2 or 3 levels deep by default
                root = await self.service.get_collections_by_name(self.last_selected_guid)
                root_guid = root.get("GUID", None)
                root_name = root.get("title", None)
                root_qname = root.get("qualifiedName", None)
                root_desc = root.get("description", None)
                root_members = root.get("members", None)
                if ("marketplace" in root_name.lower()) or ("marketplace" in root_qname.lower()):
                    marketplace_guid = root_guid
                    self.log(f"Found marketplace guid of {marketplace_guid}, {root_name}")
                    #set up Textual Tree structure for display
                    market_tree: Tree =Tree(root_name, data=root_guid, id="marketplace_tree")
                    # now query for all the collection members, probably 2 levels for initial display
                    marketplace_folders = await self.service.get_collections_by_name(marketplace_guid)
                    if marketplace_folders:
                        for folder in marketplace_folders:
                            folder_guid = folder.get("GUID", None)
                            folder_name = folder.get("title", None)
                            folder_qname = folder.get("qualifiedName", None)
                            folder_desc = folder.get("description", None)
                            folder_members = folder.get("members", None)
                            market_tree.root.expand()
                            if "Folder" in folder_qname:
                                self.log(f"Found folder guid of {folder_guid}, {folder_name}")
                                entries = market_tree.root.add(folder_name, data= folder_guid, expasnd = True)
                                if folder_members:
                                    for member in folder_members:
                                        member_guid = member.get("GUID", None)
                                        member_name = member.get("title", None)
                                        #process level 3
                                        entries.add(member_name, member_guid, expand = True)
                                        continue
                                else:
                                    entries.add(f"No members found for {folder_name}")
                                    continue
                            else:
                                market_tree.root.add_leaf(folder_name, data = folder_guid, expand = True)
                    else:
                        # marketplace is empty
                        self.log(f"Marketplace guid {marketplace_guid} is empty")
                        self.spacer_container = self.query_one("#go_spacer", Container)
                        market_tree.root.add(f"Marketplace {marketplace_guid} is empty")
                else:
                    self.not_marketplace_guid(root_guid)
        else:
            # display error and stay on base screen until a different action is selected
            # or a selection is made
            self.log("No definition selected")
            await self._refresh_and_focus()
            return
        #
        await self.app.push_screen(MarketPlaceTree(market_tree))

    def not_marketplace_guid(self, root_guid: str):
        self.log(f"Found non-marketplace guid of {root_guid}")
        pass


    @on(Button.Pressed, "#gd-new-button")
    async def handle_new_button(self, event: Button.Pressed) -> None:
        """Open the Create New Collection screen (non-blocking)."""
        self.log(f"Add definition button pressed, add_open: {self._add_open}")
        if self._add_open:
            return
        self._add_open = True
        await self.app.push_screen(AddGovernanceDefinitionScreen())

    @on(Button.Pressed, "#gd-delete-button")
    async def handle_delete_button(self, event: Button.Pressed) -> None:
        """Open the Create New Collection screen (non-blocking)."""
        self.log(f"Delete definition button pressed, del_open: {self._del_open}")
        if self._del_open:
            return
        self._del_open = True
        await self.app.push_screen(DeleteGovernanceDefinitionScreen(self.last_selected_guid))

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
        await self.load_governance_officer_definitions()
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

    @on(AddGovernanceDefinitionScreen.GovernanceDefinitionCreated)
    async def process_definition_created(self, msg: AddGovernanceDefinitionScreen.GovernanceDefinitionCreated):
        """
        Refresh after a collection is created and restore a working input context.
        """
        await self._refresh_and_focus()

    @on(DeleteGovernanceDefinitionScreen.GovernanceDefinitionDeleted)
    async def process_definition_deleted(self, msg: DeleteGovernanceDefinitionScreen.GovernanceDefinitionDeleted):
        """
        Refresh after a collection is created and restore a working input context.
        """
        await self._refresh_and_focus()

    async def action_refresh(self):
        """
        Hotkey handler for 'r' to reload collections.
        """
        await self._refresh_and_focus()

    async def load_governance_officer_definitions(self, search: str = ""):
        self.table.clear()
        try:
            collections = await asyncio.to_thread(self.service.find_governance_definitions, search or "*")
            if collections:
                for c in collections:
                    guid = (c.get("GUID", ""))
                    type_name = (c.get("typeName", ""))
                    doc_id = (c.get("documentIdentifier", ""))
                    unique_name = (c.get("title", ""))
                    summary = (c.get("summary", ""))
                    description = (c.get("description", ""))

                    self.table.add_row(guid, type_name, doc_id, unique_name, summary, description)
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
