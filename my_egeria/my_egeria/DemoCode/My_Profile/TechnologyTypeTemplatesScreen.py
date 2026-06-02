"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""

from typing import Any

from pyegeria import load_app_config
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import TextArea, Input, Header, Static, Button, Footer


class TechnologyTypeTemplatesScreen(ModalScreen[Any]):
    """Modal screen to display technology type templates in Egeria."""
    BINDINGS = [("q", "dismiss(200)", "Quit"),
                ("b", "back", "Go back"),
                ("ctl+e", "expand", "Toggle Twisties")]

    CSS_PATH = "my_profile.tcss"

    def __init__ (self,
                  user_name: str,
                  user_kpts: int,
                  tech_type_name: str,
                  tech_type_description: str,
                  selected_t_option,
                  tech_type_option_selected,
                  tech_type_templates
                  ) -> None:
        """Initialize the Technology_Type_Templatess screen."""
        super().__init__()
        self.user_name = user_name
        self.karma_points = user_kpts
        self.tech_type_name = tech_type_name
        self.tech_type_description = tech_type_description
        self.selected_t_option = selected_t_option
        self.selected_t_option_selected = tech_type_option_selected
        self.tech_type_templates = tech_type_templates
        self.full_template = None
        self.selected_t_template = None
        load_app_config()

    async def on_mount(self) -> None:
        """ On Mount function of the Technology_Type_Templatess screen."""
        self.title = f"User: {self.user_name}, Karma Points: {self.karma_points}"
        self.sub_title = f"Technology Type: {self.tech_type_name}, Description: {self.tech_type_description}"

        if self.selected_t_option == "template":
            self.log(f"Processing templates, with data: {self.selected_t_option_selected}")
            # get selected template from the tech_type data
            self.log(f"Technology Type Templates: {self.tech_type_templates}")
            if isinstance(self.tech_type_templates, list):
                for template in self.tech_type_templates:
                    self.log(f"Template: {template.get('displayName')}, Selected: {self.selected_t_option_selected}")
                    if self.selected_t_option_selected == template.get("displayName"):
                        self.full_template = template
                        self.selected_t_template = template
                        self.log(f"Selected Template: {self.selected_t_template}")
                        break
                    else:
                        continue
            self.log(f"Selected Template: {self.selected_t_template}")

            if self.selected_t_template is None:
                self.log("No template selected, skipping placeholder display")
                return
            else:
                specification = self.selected_t_template.get("specification")
                if specification is None:
                    self.log("Selected template has no specification, skipping placeholder display")
                    return
                else:
                    placeholderProperties = specification.get("placeholderProperty")
                    if placeholderProperties is None:
                        self.log("Selected template has no placeholder properties, skipping display")
                        return
                    else:
                        for placeholder in placeholderProperties:
                            if placeholder.get("class") != "PlaceholderProperty":
                                continue
                            else:
                                name = placeholder.get("name") or None
                                Description = placeholder.get("description") or None
                                Type = placeholder.get("dataType") or None
                                Example = placeholder.get("example") or None
                                Required = placeholder.get("required") or False

                                # Sanitize the name for use as a CSS ID
                                safe_name = name.replace(" ", "_") if name else f"placeholder_{id(placeholder)}"
                                placeholder_text: TextArea = TextArea(
                                    f"{name}\n\nDescription: {Description}\nType: {Type}\nExample: {Example}\nRequired: {Required}",
                                    id=f"{safe_name}_placeholder_text_area",
                                    read_only=True
                                )
                                # Ensure TextArea is visible
                                placeholder_text.styles.height = 8

                                placeholder_input = Input(id=f"{safe_name}_placeholder_input", placeholder="Enter value here")
                                self.log(f"Placeholder: {placeholder_text.text}\n {placeholder_input}")

                                # Mount the TextArea and the associated Input field into the ScrollableContainer
                                try:
                                    load_point = self.query_one("#technology_type_templates_input")
                                    await load_point.mount(placeholder_text, before="#template_submit_button")
                                    await load_point.mount(placeholder_input, before="#template_submit_button")
                                    self.log(f"Placeholder text area loaded: {placeholder_text.text}")
                                    self.log(f"Placeholder input loaded: {placeholder_input}")
                                    continue
                                except Exception as e:
                                    self.log(f"Error loading placeholder container: {e!s}")
                                    self.app.dismiss(416)

    def compose(self) -> ComposeResult:
        """ Compose the UI components for the Technology_Type_Templatess screen."""
        yield Header(show_clock=True)
        yield Static("Please complete the required fields and any optional fields you prefer:")
        yield ScrollableContainer(
            Static("Technology Type Template Input"),
            Button("Submit", id="template_submit_button"),
            id="technology_type_templates_input"
        )
        yield Footer()

    def action_quit(self) -> None:
        """ The quit option in the footer has been selected. Dismiss the screen."""
        self.dismiss("200", )

    @on(Button.Pressed, "#template_submit_button")
    def handle_submit_button_pressed(self, event: Button.Pressed) -> None:
        """ The submit button has been pressed."""
        self.log(f"Submit button pressed, button: {event.button}")
        save_input_data: dict = {}
        for input_widget in self.query("Input"):
            self.log(f"Input widget: {input_widget.id}, value: {input_widget.value}")
            save_input_data.update({input_widget.id: input_widget.value})
        self.log(f"Save input data: {save_input_data}")
        self.dismiss(["input", save_input_data, self.full_template])

    @on(Input.Changed, "#technology_type_templates_input")
    def handle_input_changed(self, event: Input.Changed) -> None:
        """ The user has changed the input on the screen."""
        self.log(f"Input changed, input: {event.input}")
