# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Glossary related functions of my_egeria module.


"""

from textual.widgets import Static, DataTable, Input, Button
from textual.containers import Horizontal, Vertical, Container
from my_egeria.screens.base_screen import BaseScreen
from my_egeria.services.glossary_service import GlossaryService
from .term_details import TermDetailsScreen
import asyncio


class GlossaryBrowserScreen(BaseScreen):
    CSS_PATH = ["../../styles/common.css", "../../styles/glossary_browser.css"]

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.service = None
        self.mode = None
        self.selected_glossary_guid = None
        self.selected_glossary_name = None
        self.selected_term_guid = None
        self.selected_term_name = None
        self.title_widget = None
        self.table = None

    def compose(self):
        # yield from super().compose()

        # Simple vertical layout: top (list), search (fixed 5 rows), spacer, bottom (buttons)
        yield Vertical(
            # Top: Title + Table
            Container(
                Vertical(
                    Static("Glossaries", id="title"),
                    DataTable(id="main-table"),
                    id="top_content",
                ),
                id="top_row",
            ),
            # Search (fixed 5 rows)
            Container(
                Horizontal(
                    Input(placeholder="Search...", id="search-input"),
                    Button("Search", id="search-button"),
                    id="search_row",
                ),
                id="search_row_container",
            ),
            # Flexible spacer to push buttons to bottom
            Container(id="spacer"),
            # Bottom: action buttons
            Container(
                Horizontal(
                    Button("List Terms", id="list-terms-button", disabled = True),
                    Button("Back to Glossaries", id="back-button"),
                    # Glossary actions (enabled in glossary mode)
                    # Button("Add Glossary", id="add-glossary-button", disabled = True),
                    # Button("Delete Glossary", id="delete-glossary-button"),
                    # Button("Update Glossary", id="update-glossary-button", disabled = True),
                    # Term actions (enabled in terms mode)
                    # Button("Add Term", id="add-term-button", disabled = True),
                    # Button("Delete Term", id="delete-term-button"),
                    # Button("Term Details", id="term-details-button", disabled = True),
                    id="action_row",
                ),
                id="action_row_container",
            ),
            id="v_root",
        )

    async def on_mount(self):
        await super().on_mount()
        # Root fills available space
        vroot = self.query_one("#v_root", Vertical)
        vroot.styles.width = "100%"
        vroot.styles.height = "100%"
        vroot.styles.gap = 0

        # Top row: fixed percentage so the table is always visible
        top_row = self.query_one("#top_row", Container)
        top_row.styles.width = "100%"
        top_row.styles.height = "60%"  # take the top ~60% of the screen
        top_row.styles.padding = (1, 2)

        top_content = self.query_one("#top_content", Vertical)
        top_content.styles.width = "100%"
        top_content.styles.height = "100%"
        top_content.styles.gap = 1

        title = self.query_one("#title", Static)
        title.styles.text_align = "center"
        title.styles.text_style = "bold"
        title.styles.margin = (0, 0, 1, 0)

        # Table fills remaining space within top_row
        self.table = self.query_one("#main-table", DataTable)
        self.table.styles.height = "100%"
        self.table.styles.min_height = 8
        self.table.cursor_type = "row"

        # Search row: fixed ~5 lines height
        sbox = self.query_one("#search_row_container", Container)
        sbox.styles.width = "100%"
        sbox.styles.height = 5
        sbox.styles.padding = (0, 1)
        sbox.styles.border = ("solid", "blue")

        srow = self.query_one("#search_row", Horizontal)
        srow.styles.align_horizontal = "center"
        srow.styles.gap = 1

        sinput = self.query_one("#search-input", Input)
        sinput.styles.width = "40%"
        sinput.styles.margin = (1, 0, 1, 0)

        sbtn = self.query_one("#search-button", Button)
        sbtn.styles.margin = (1, 0, 1, 0)

        # Spacer flexes to keep buttons at bottom
        spacer = self.query_one("#spacer", Container)
        spacer.styles.height = "1fr"

        # Bottom action bar
        abox = self.query_one("#action_row_container", Container)
        abox.styles.width = "100%"
        abox.styles.height = "auto"
        abox.styles.padding = (1, 2)

        arow = self.query_one("#action_row", Horizontal)
        arow.styles.align_horizontal = "center"
        arow.styles.gap = 1

        # Service + mode setup
        self.service = GlossaryService()
        self.mode = "glossaries"
        self.selected_glossary_guid = ""
        self.selected_glossary_name = ""
        self.selected_term_guid = ""
        self.selected_term_name = ""
        self.title_widget = title

        # Configure and load initial glossaries
        self._configure_for_glossaries()
        await self._load_glossaries()

    # ------------- UI mode configuration -------------

    def _configure_for_glossaries(self):
        self.mode = "glossaries"
        self.title_widget.update("Glossaries")
        self.table.clear(columns=True)
        self.table.add_columns("GUID", "Display Name", "Qualified Name", "Description")
        self.selected_glossary_guid = ""
        self.selected_glossary_name = ""
        self._set_buttons_state(
            list_terms=True,
            back=False,
            add_glossary=True,
            delete_glossary=False,
            update_glossary=False,
            add_term=False,
            delete_term=False,
            term_details=False,
        )

    def _configure_for_terms(self):
        self.mode = "terms"
        self.title_widget.update(
            f"Terms in: {self.selected_glossary_name or self.selected_glossary_guid}"
        )
        self.table.clear(columns=True)
        self.table.add_columns("GUID", "Term Name", "Summary/Description", "Status")
        self.selected_term_guid = ""
        self.selected_term_name = ""
        self._set_buttons_state(
            list_terms=False,
            back=True,
            add_glossary=False,
            delete_glossary=False,
            update_glossary=False,
            add_term=True,
            delete_term=True,
            term_details=True,
        )

    def _set_buttons_state(
        self,
        *,
        list_terms: bool,
        back: bool,
        add_glossary: bool,
        delete_glossary: bool,
        update_glossary: bool,
        add_term: bool,
        delete_term: bool,
        term_details: bool,
    ):
        self.query_one("#list-terms-button", Button).disabled = not list_terms
        self.query_one("#back-button", Button).disabled = not back
        # self.query_one("#add-glossary-button", Button).disabled = not add_glossary
        self.query_one("#add-glossary-button", Button).disabled = True
        self.query_one("#delete-glossary-button", Button).disabled = not delete_glossary
        # self.query_one("#update-glossary-button", Button).disabled = not update_glossary
        self.query_one("#update-glossary-button", Button).disabled = True
        # self.query_one("#add-term-button", Button).disabled = not add_term
        # self.query_one("#delete-term-button", Button).disabled = not delete_term
        # self.query_one("#term-details-button", Button).disabled = not term_details
        self.query_one("#add-term-button", Button).disabled = True
        self.query_one("#delete-term-button", Button).disabled = True
        self.query_one("#term-details-button", Button).disabled = True

    # ------------- Selection wiring -------------

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        # Capture selection for both modes
        if self.mode == "glossaries":
            try:
                guid, name, *_ = self.table.get_row(event.row_key)
            except Exception:
                guid, name = "", ""
            self.selected_glossary_guid = guid or ""
            self.selected_glossary_name = name or ""
            # Enable delete/update only when a glossary is selected
            self.query_one("#delete-glossary-button", Button).disabled = not bool(guid)
            # Keep update disabled for now as requested
            self.query_one("#update-glossary-button", Button).disabled = True
        else:
            try:
                guid, name, *_ = self.table.get_row(event.row_key)
            except Exception:
                guid, name = "", ""
            self.selected_term_guid = guid or ""
            self.selected_term_name = name or ""
        if self.selected_glossary_guid:
            self.query_one("#delete-term-button", Button).disabled = False
        else:
            self.query_one("#delete-term-button", Button).disabled = True

    # ------------- Loaders -------------

    async def _load_glossaries(self, search: str = ""):
        self.table.clear()
        try:
            # Run the sync call in a worker thread to avoid blocking the UI loop
            glossaries = await asyncio.to_thread(self.service.list_glossaries, search or "*")
            self.log(f"Loaded {len(glossaries)} glossaries")
            self.log(f"Glossaries: {glossaries}")
            if glossaries:
                for g in glossaries:
                    self.table.add_row(
                        g.get("GUID", "") or g.get("guid", ""),
                        g.get("display_name", "") or g.get("displayName", ""),
                        g.get("qualified_name", "") or g.get("qualifiedName", ""),
                        g.get("description", "") or g.get("summary", ""),
                    )
            else:
                self.table.add_row("", "No glossaries found", "", "")
        except Exception as e:
            self.table.add_row("", f"Error: {e}", "", "")

    async def _load_terms_for_glossary(self, glossary_guid: str, search: str = ""):
        self.table.clear()

        try:
            terms = await self.service.get_glossary_terms_async(glossary_guid, search=search)
            if terms:
                for t in terms:
                    pass
                    # load tree with results

                    # self.table.add_row(
                    #     t.get("guid", "") or t.get("GUID", ""),
                    #     t.get("displayName", "") or t.get("display_name", ""),
                    #     t.get("summary", "") or t.get("description", ""),
                    #     t.get("status", "") or "",
                    # )
            else:
                self.table.add_row("", "No terms found", "", "")
        except Exception as e:
            self.table.add_row("", f"Error: {e}", "", "")

    async def _load_all_terms(self, search: str = ""):
        """Aggregate and list terms from all glossaries."""
        self.table.clear()
        try:
            # Fetch glossaries in a worker thread
            glossaries = await asyncio.to_thread(self.service.list_glossaries, "*")
            aggregate = []
            for g in (glossaries or []):
                g_guid = g.get("GUID", "") or g.get("guid", "")
                if not g_guid:
                    continue
                search_string = "*"
                try:
                    # Fetch terms for each glossary in a worker thread
                    terms = await asyncio.to_thread(self.service.get_terms,  search_string, glossary_guid=g_guid )
                    # Tag term with source glossary display name for context (optional)
                    g_name = g.get("display_name", "") or g.get("displayName", "") or ""
                    for t in (terms or []):
                        t = dict(t)  # shallow copy
                        if "glossary" not in t:
                            t["glossary"] = g_name
                        aggregate.append(t)
                except Exception:
                    # Skip problematic glossary and continue
                    continue

            if aggregate:
                # Switch to terms table layout
                self.mode = "terms"
                self.title_widget.update("Terms in: All Glossaries")
                self.table.clear(columns=True)
                self.table.add_columns("GUID", "Term Name", "Summary/Description", "Status")
                # Populate
                for t in aggregate:
                    self.table.add_row(
                        t.get("guid", "") or t.get("GUID", ""),
                        t.get("displayName", "") or t.get("display_name", ""),
                        t.get("summary", "") or t.get("description", ""),
                        t.get("status", "") or "",
                    )
                # Enable term actions
                self._set_buttons_state(
                    list_terms=False, back=True,
                    add_glossary=False, delete_glossary=False, update_glossary=False,
                    add_term=True, delete_term=True, term_details=True
                )
            else:
                self.table.add_row("", "No terms found", "", "")
        except Exception as e:
            self.table.add_row("", f"Error: {e}", "", "")

        # ------------- Button handlers -------------

    async def on_button_pressed(self, event: Button.Pressed):
        btn_id = event.button.id
        if btn_id == "search-button":
            query = self.query_one("#search-input", Input).value.strip()
            if self.mode == "glossaries":
                await self._load_glossaries(search=query)
            else:
                await self._load_terms_for_glossary(self.selected_glossary_guid, search=query)

        elif btn_id == "list-terms-button":
            # If a glossary is selected, show its terms; otherwise show all terms
            if self.selected_glossary_guid:
                self._configure_for_terms()
                await self._load_terms_for_glossary(self.selected_glossary_guid)
            else:
                await self._load_all_terms()

        elif btn_id == "back-button":
            self._configure_for_glossaries()
            await self._load_glossaries()

        elif btn_id == "add-glossary-button":
            # Minimal add flow: create a new glossary with placeholder values, then refresh.
            # Replace with a dedicated screen later.
            payload = {
                "display_name": "New Glossary",
                "description": "Created from TUI",
                "language": "English",
                "usage": "General",
            }
            try:
                await self.service.add_glossary_async(payload)
                await self._load_glossaries()
            except Exception:
                pass

        elif btn_id == "delete-glossary-button":
            if not self.selected_glossary_guid:
                return
            try:
                await self.service.delete_glossary_async(self.selected_glossary_guid)
                self.selected_glossary_guid = ""
                self.selected_glossary_name = ""
                await self._load_glossaries()
                # After reload, disable delete until new selection
                self.query_one("#delete-glossary-button", Button).disabled = True
            except Exception:
                pass

        elif btn_id == "add-term-button":
            if not self.selected_glossary_guid:
                return
            payload = {"display_name": "New Term", "summary": "Created from TUI"}
            try:
                await self.service.add_term_async(self.selected_glossary_guid, payload)
                await self._load_terms_for_glossary(self.selected_glossary_guid)
            except Exception:
                pass

        elif btn_id == "delete-term-button":
            if not self.selected_term_guid:
                return
            try:
                await self.service.delete_term_async(self.selected_term_guid)
                await self._load_terms_for_glossary(self.selected_glossary_guid)
                self.selected_term_guid = None
            except Exception:
                pass

        elif btn_id == "term-details-button":
            if self.selected_term_guid:
                await self.app.push_screen(TermDetailsScreen())
