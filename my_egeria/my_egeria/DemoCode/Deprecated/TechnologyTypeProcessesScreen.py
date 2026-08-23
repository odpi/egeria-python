"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""

from typing import Any

from pyegeria import load_app_config
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Container
from textual.screen import ModalScreen
from textual.widgets import TextArea, Input, Header, Static, Button, Footer


class TechnologyTypeProcessesScreen(ModalScreen[Any]):
    """Modal screen to display technology type processes in Egeria."""
    BINDINGS = [("q", "quit", "Quit"),
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
                  tech_type_processes
                  ) -> None:
        """Initialize the TechnologyTypeProcesses screen."""
        super().__init__()
        self.user_name = user_name
        self.karma_points = user_kpts
        self.tech_type_name = tech_type_name
        self.tech_type_description = tech_type_description
        self.selected_t_option = selected_t_option
        self.selected_t_option_selected = tech_type_option_selected
        self.tech_type_processes = tech_type_processes
        self.full_process = None
        self.selected_process = None
        load_app_config()

    async def on_mount(self) -> None:
        """ On Mount function of the Technology_Type_Templatess screen."""
        self.title = f"User: {self.user_name}, Karma Points: {self.karma_points}"
        self.sub_title = f"Technology Type: {self.tech_type_name}, Description: {self.tech_type_description}"

        if self.selected_t_option == "process":
            self.log(f"Processing processes, with data: {self.selected_t_option_selected}")
            # get selected process from the tech_type data
            self.log(f"Technology Type Process: {self.tech_type_processes}")
            if isinstance(self.tech_type_processes, list):
                for process in self.tech_type_processes:
                    self.log(f"Process: {process.get("displayName")}, Selected: {self.selected_t_option_selected}")
                    if self.selected_t_option_selected  == process.get("displayName"):
                        self.full_process = process
                        self.selected_t_process = process
                        self.log(f"Selected Process: {self.selected_t_process}")
                        break
                    else:
                        continue
            self.log(f"Selected Process: {self.selected_t_process}, type: {type(self.selected_t_process)}")

            if self.selected_t_process is None:
                self.log("No process selected, skipping placeholder display")
                return
            else:
                specification = self.selected_t_process.get("specification")
                if specification is None:
                    self.log("Selected process has no specification, skipping placeholder display")
                    return
                else:
                    placeholderProperties = specification.get("supportedRequestParameter")
                    if placeholderProperties is None:
                        self.log("Selected process has no req   uest parameters, skipping display")
                        return
                    else:
                        for parameter in placeholderProperties:
                            if parameter.get("class") != "SupportedRequestParameter":
                                continue
                            else:
                                name = parameter.get("name") or None
                                Description = parameter.get("description") or None
                                Type = parameter.get("dataType")
                                Example = parameter.get("example")
                                Required = parameter.get("required")
                                # governance_action_steps = self.full_process.get("Governance Action Steps") or None

                                # Sanitize the name for use as a CSS ID
                                safe_name = name.replace(" ", "_") if name else f"placeholder_{id(self.selected_t_process)}"
                                safe_name = safe_name.replace("::", "_")
                                safe_name = safe_name.replace(":", "_")
                                self.log(f"Safe name = {safe_name}")
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
                                    load_point = self.query_one("#technology_type_processes_input")
                                    await load_point.mount(placeholder_text, before="#process_submit_button")
                                    await load_point.mount(placeholder_input, before="#process_submit_button")
                                    self.log(f"Placeholder text area loaded: {placeholder_text.text}")
                                    self.log(f"Placeholder input loaded: {placeholder_input}")
                                    continue
                                except Exception as e:
                                    self.log(f"Error loading placeholder container: {e!s}")
                                    self.app.dismiss(416)


    def compose(self) -> ComposeResult:
        """ Compose the UI components for the Technology_Type_Processes screen."""
        yield Header(show_clock=True)
        yield Static("Please complete the required fields and any optional fields you prefer:")
        yield ScrollableContainer(
            Static("Technology Type Process Input"),
            Button("Submit", variant="primary", id="process_submit_button"),
            id="technology_type_processes_input"
            )
        yield Footer()

    def action_quit(self) -> None:
        """ The quit option in the footer has been selected. Dismiss the screen."""
        self.dismiss("200", )

    @on(Button.Pressed, "#process_submit_button")
    def handle_submit_button_pressed(self, event: Button.Pressed) -> None:
        """ The submit button has been pressed."""
        self.log(f"Submit button pressed, button: {event.button}")
        save_input_data:dict = {}
        for input_widget in self.query("Input"):
            self.log(f"Input widget: {input_widget.id}, value: {input_widget.value}")
            save_input_data.update({input_widget.id: input_widget.value})
        self.log(f"Save input data: {save_input_data}")
        self.dismiss(["input", save_input_data, self.full_process])

    @on(Input.Changed, "#technology_type_processes_input")
    def handle_input_changed(self, event: Input.Changed) -> None:
        """The user has changed the input on the screen."""
        self.log(f"Input changed, input: {event.input}")