
"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module implements the Add Governance Definition functions of my_egeria module.


"""

import asyncio

from textual.reactive import reactive
from textual.screen import ModalScreen
# need to refactor from asyncio workers to built in textual @worker features
from textual.message import Message
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Input, Button, Pretty, OptionList, Footer, Header
# from .governance_officer_browser import GovernanceOfficerBrowserScreen
from ..base_screen import BaseScreen
from my_egeria.services.governance_officer_service import GovernanceOfficerService
from typing import Dict, Any
from my_egeria.utils.config import EgeriaConfig

def parse_kv_pairs(text: str) -> Dict[str, Any]:
    """
    Parse a simple 'key=value;key2=value2' string into a dict.
    Ignores empty segments; trims whitespace. No escaping supported.
    """
    result: Dict[str, Any] = {}
    if not text:
        return result
    for part in text.split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            k, v = part.split("=", 1)
            result[k.strip()] = v.strip()
        else:
            # Bare key → True
            result[part] = True
    return result



class AddGovernanceDefinitionScreen(BaseScreen):
    """ Create a governance definition. It may be of type:
            * BusinessImperative
            * RegulationArticle
            * Threat
            * GovernancePrinciple
            * GovernanceObligation
            * GovernanceApproach
            * GovernanceProcessingPurpose
            The type is added to the "typeName" property.

           Simple body structure:
        {
          "class": "NewElementRequestBody",
          "properties": {
            "class" : "GovernanceDefinitionProperties",
            "typeName" : "enter the type of the governance definition",
            "domainIdentifier": 0,
            "documentIdentifier": "add unique name here",
            "title": "add short name here",
            "summary": "add summary here",
            "description": "add description here",
            "scope": "add scope of effect for this definition",
            "importance": "add importance for this definition",
            "implications": [],
            "outcomes": [],
            "results": [],
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            }
          },
          "initialStatus": "DRAFT"
        }

        """

    CSS_PATH = ["../../styles/common.css", "../../styles/add_governance_definition.css"]


    class GovernanceDefinitionCreated(Message):
        def __init__(self, created: dict):
            super().__init__()
            self.created = created

    class GovernanceDefinitionCreateRequested(Message):
        def __init__(self, payload: Dict[str, Any]):
            super().__init__()
            self.payload = payload

    def __init__(self):
        super().__init__()
        self.valid_types = [("A", "BusinessImperative"),
                            ("B", "RegulationArticle"),
                            ("C", "Threat"),
                            ("D", "GovernancePrinciple"),
                            ("E", "GovernanceObligation"),
                            ("F", "GovernanceApproach"),
                            ("G", "GovernanceProcessingPurpose")]

        self.selected_type: reactive[str] = ""

    def compose(self):
        yield from super().compose()

        # Top-half container -> bordered box -> centered vertical form
        yield Container(
            Container(
                Vertical(
                    Static("Create New Governance Definition", id="agd_title"),
                    # Inputs
                    Horizontal(
                        Static("Type Name (required)", classes="agd_input_label"),
                        Static(f"Type Selected: {self.selected_type} ", id="agd_type_name", classes = "agd_input_field")
                            ),
                    Horizontal(
                        Static("Document ID (required)", classes="agd_input_label"),
                        Input(placeholder="add unique name here", id="agd_doc_id", classes = "agd_input_field")
                            ),
                    Horizontal(
                        Static("Title (required)", classes="agd_input_label"),
                        Input(placeholder="short name", id="agd_short_name", classes = "agd_input_field")
                            ),
                    Horizontal(
                        Static("Summary of usage, (required)", classes="agd_input_label"),
                        Input(placeholder="Summary of definition", id="agd_summary", classes = "agd_input_field")
                            ),
                    Horizontal(
                        Static("Description (required)", classes="agd_input_label"),
                        Input(placeholder="add description here", id="agd_description", classes = "agd_input_field")
                            ),
                    Horizontal(
                        Static("Scope of effect (required)", classes="agd_input_label"),
                        Input(placeholder="add scope of effect for this definition", id="agd_scope", classes = "agd_input_field")
                            ),
                    Horizontal(
                        Static("Importance (required)", classes="agd_input_label"),
                        Input(placeholder="add importance for this definition", id="agd_importance", classes = "agd_input_field")
                            ),
                    Horizontal(
                        Static("Implications", classes="agd_input_label"),
                        Input(placeholder="add implications", id="agd_implications", classes = "agd_input_field")
                            ),
                    Horizontal(
                        Static("Outcomes", classes="agd_input_label"),
                        Input(placeholder="add outcomes", id="agd_outcomes", classes = "agd_input_field")
                            ),
                    Horizontal(
                        Static("Results", classes="agd_input_label"),
                        Input(placeholder="add results", id="agd_results", classes = "agd_input_field")
                            ),
                    Horizontal(
                        Static("Additional Properties (optional: key=value; key2=value2)", classes="agd_input_label"),
                        Input(placeholder="key=value; foo=bar", id="agd-additional-props", classes = "agd_input_field")
                            ),
                    # Buttons + Status
                    Horizontal(
                        Button("Create", id="agd_create-btn"),
                        Button("Cancel", id="agd_cancel-btn"),
                        id="agd_buttons",
                            ),
                    Static("", id="status"),
                    id="agd_form"),
                id="agd_box"),
            id="agd_top")

    async def on_mount(self):
        await super().on_mount()

        # Position the top-level container in the upper portion; give vertical room

        top = self.query_one("#agd_top", Container)
        top.styles.dock = "top"
        top.styles.height = "60%"               # top ~60% of the screen
        top.styles.width = "100%"
        top.styles.padding = (1, 2)
        top.styles.align_horizontal = "center"  # center child (ac_box) horizontally
        top.styles.align_vertical = "top"       # keep at top within the section

        # Bordered box that contains the vertical form
        box = self.query_one("#agd_box", Container)
        box.styles.width = "70%"
        box.styles.border = ("solid", "white")
        box.styles.padding = (1, 2)
        box.styles.align_horizontal = "center"
        box.styles.align_vertical = "top"
        box.styles.min_height = 18

        form = self.query_one("#agd_form", Vertical)
        form.styles.gap = 1
        form.styles.width = "100%"

        # Title styling
        title = self.query_one("#agd_title", Static)
        title.styles.text_align = "center"
        title.styles.text_style = "bold"
        title.styles.margin = (0, 0, 1, 0)

        # Inputs: make them a reasonable width
        for iid in ("#agd_doc_id", "#agd_short_name", "#agd_summary", "#agd_description", "#agd_scope", "#agd_importance", "#agd_implications", "#agd_outcomes", "#agd_results", "#agd-additional-props"):
            inp = self.query_one(iid, Input)
            inp.styles.width = "80%"

        # Allow selection of Type Name from a list

        await self.display_valid_type_popup(self.valid_types)
        self.query_one("#agd_type_name", Static).update()

        # Buttons row: center and add a little spacing
        btn_row = self.query_one("#agd_buttons", Horizontal)
        btn_row.styles.align_horizontal = "center"
        btn_row.styles.gap = 2

        # Button margins
        self.query_one("#agd_create-btn", Button).styles.margin = (1, 0, 0, 0)
        self.query_one("#agd_cancel-btn", Button).styles.margin = (1, 0, 0, 0)

    async def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "agd_cancel-btn":
            self.query_one("#status", Static).update("Cancelled", )
            await self.app.show_governance_officer_browser()
            return

        if event.button.id == "agd-create-btn":
            type_name = (self.query_one("#agd_title", Input).value or "").strip()
            document_id = (self.query_one("#agd_doc_id", Input).value or "").strip()
            title = (self.query_one("#agd_short_name", Input).value or "").strip()
            summary = (self.query_one("#agd_summary", Input).value or "").strip()
            description = (self.query_one("#agd_description", Input).value or "").strip()
            scope = (self.query_one("#agd_scope", Input).value or "").strip()
            importance = (self.query_one("#agd_importance", Input).value or "").strip()
            implications = (self.query_one("#agd_implications", Input).value or "").strip()
            outcomes = (self.query_one("#agd_outcomes", Input).value or "").strip()
            results = (self.query_one("#agd_results", Input).value or "").strip()
            add_props_raw = (self.query_one("#agd_additional_props", Input).value or "").strip()

            status = self.query_one("#status", Static)

            # Required fields:
            missing = []
            if not type_name:
                missing.append("Type Name")
            if not document_id:
                missing.append("Unique Name")
            if not title:
                missing.append("Short Name")
            if not description:
                missing.append("Description")
            if not scope:
                missing.append("Scope of Effect")
            if not importance:
                missing.append("Importance")
            if not implications:
                missing.append("Implications")
            if not outcomes:
                missing.append("Outcomes")
            if not results:
                missing.append("Results")
            if missing:
                status.update(f"Required: {', '.join(missing)}.")
                return

            payload: Dict[str, Any] = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class" : "GovernanceDefinitionProperties",
                    "typeName" : type_name,
                    "domainIdentifier": 0,
                    "documentIdentifier": document_id,
                    "title": title,
                    "summary": summary,
                    "description": description,
                    "scope": scope,
                    "importance": importance,
                    "implications": implications,
                    "outcomes": outcomes,
                    "results": results,
                }
            }
            add_props: Dict[str, Any] = parse_kv_pairs(add_props_raw)
            if add_props:
                payload["additionalProperties"] = add_props

            # Fire-and-forget background create; do NOT block this screen.
            async def _create_and_notify():
                try:
                    created = await asyncio.to_thread(GovernanceOfficerService.create_governance_definition, payload)
                except Exception:
                    created = None
                # Notify the parent screen (even on failure; parent may decide how to react)
                self.app.post_message(self.GovernanceDefinitionCreated(created or {}))

            asyncio.create_task(_create_and_notify())

            # Close immediately; GovernanceOfficerBrowser will refresh when it receives GovernanceDefinitionCreated
            await asyncio.sleep(0)  # yield one tick
            await self.app.pop_screen()

    async def on_definition_type_popup_definition_type_popup_message(self, selected_type):
        self.selected_type = selected_type
        self.query_one("#agd_type_name", Static).update(f"Type Selected: {selected_type}")
        self.query_one("#agd_type_name", Static).update(selected_type)

    async def display_valid_type_popup(self, valid_types):
        self.valid_types = valid_types
        types_selection_list = OptionList(*self.valid_types, id = "validtypes")
        await self.app.push_screen(self.DefinitionTypePopup())
        return self.selected_type

    class DefinitionTypePopup(BaseScreen, ModalScreen):

        CSS_PATH  = ["../../styles/common.css", "../../styles/add_governance_definition.css"]

        BINDINGS = [("q", "quit_app", "Quit"),
                    ("escape", "back", "Back"),
                    ("b", "back", "Back")]

        class DefinitionTypePopupMessage(Message):
            def __init__(self, selected_type: str):
                super().__init__()
                self.selected_type = selected_type

        def __init__(self):
            super().__init__()
            self.prompt = None
            self.selected_type = None

        def compose(self):

            self.valid_types = ("BusinessImperative",
                                "RegulationArticle",
                                "Threat",
                                "GovernancePrinciple",
                                "GovernanceObligation",
                                "GovernanceApproach",
                                "GovernanceProcessingPurpose")
            yield Header()
            with Container():
                yield Static("Select a valid definition type by double clicking on an option:")
                yield OptionList(*self.valid_types, id="validtypeslist")
                yield Button("Select", id="popup-ok")
                yield Pretty("")
            yield Footer()

        def on_option_list_highlighted(self, event:OptionList.OptionHighlighted):
            self.selected_type = event.option.value
            self.query_one(Pretty).update(f"You selected: {self.prompt}")
            self.log(f"Pretty updated user highlighted: {self.prompt}")
            self.query_one("#agd_type_name", Static).update(self.prompt)

        def on_option_list_selected(self, event:OptionList.OptionSelected):
                self.prompt = event.option.value
                if self.prompt not in self.valid_types:
                    self.prompt = None
                    self.query_one(Pretty).update(f"You selected: {self.prompt} which is not valid, please select one of the valid types")
                elif self.prompt is not None:
                    self.selected_type = event.option.value
                    self.query_one(Pretty).update(f"You selected: {self.prompt}")
                    self.log(f"Pretty updated user selected: {self.prompt}")
                    self.query_one("#agd_type_name", Static).update(self.prompt)
                    self.dismiss(self.prompt)
                else:
                    self.selected_type = event.option.label
                    self.query_one(Pretty).update(f"You selected: {self.selected_type}")
                    self.query_one("#agd_type_name", Static).update(self.selected_type)
                    self.dismiss(self.selected_type)

        def action_back(self) -> None:
            """Hotkeys q / Esc to go back."""
            self.app.pop_screen()

        def action_quit_app(self) -> None:
            """Quit the application."""
            self.app.exit()

        def on_button_pressed(self, event: Button.Pressed):
            if event.button.id == "popup-ok":
                self.post_message(self.DefinitionTypePopupMessage(self.selected_type))

        def action_refresh(self):
            self.query_one(Pretty).refresh("")
            self.query_one("#gd_type_name").refresh()
