"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""

from pyegeria import load_app_config, settings
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Container
from textual.css.query import NoMatches
from textual.screen import ModalScreen
from textual.widgets import Header, Static, OptionList, Button, Footer
from textual.widgets._option_list import Option


class TechnologyTypeOptionsScreen(ModalScreen):
    """ Modal screen to display a technology type's templates and processes."""
    BINDINGS = [("q", "dismiss", "Quit"),
                ("b", "back", "Go_Back"),
                # ("ctl+s", "Select", "tech_type_option_select")
                ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, tech_type_guid: str,
                       tech_type_name: str,
                       tech_type_description: str,
                       user_name: str,
                       user_pwd:str,
                       user_kpts: int,
                       tech_type_templates: list[dict],
                       tech_type_processes: list[dict]) -> None:
        """Initialize the TechnologyTypeOptions screen with a technology type's templates and processes."""
        super().__init__()
        self.selected_process_index = None
        self.tech_type_guid = tech_type_guid
        self.tech_type_name = tech_type_name
        self.tech_type_description = tech_type_description
        self.user_name = user_name
        self.user_password = user_pwd
        self.karma_points = user_kpts
        self.tech_type_templates = tech_type_templates
        self.tech_type_processes = tech_type_processes
        self.selected_template_guid = None
        self.selected_process_guid = None
        self.option_type_selected = None
        self.selected_template = None
        self.selected_template_index = None
        self.selected_template_data = None
        self.selected_process = None
        self.selected_process_data = None

        load_app_config("config/config.json")
        app_config = settings.Environment
        app_user = settings.User_Profile

        if not self.user_name:
            self.user_name = app_user.user_name or "garygeeke"
            self.user_password = app_user.user_pwd or "secret"

    def compose(self) -> ComposeResult:

        """ Compose the UI components for the TechnologyTypeOptions screen."""
        yield Header(show_clock=True)
        yield Static(f"Description: {self.tech_type_description}")
        yield ScrollableContainer(
            Static(f"Technology Type: {self.tech_type_name}"),
            Container(
                Static("Select a template or process to continue."),
                Static(f"Templates", id="number_of_templates_label"),
                ScrollableContainer(
                    Static("Available Templates", id="template_options_label"),
                    OptionList(id="template_options"),
                    Button("Select Template", id="select_template_btn"),
                    id="template_options_container"),
                Static(f"Processes:", id="number_of_processes_label"),
                ScrollableContainer(
                    Static("Available Processes",id="process_options_label"),
                    OptionList(id="process_options"),
                    id="process_options_container"),
                    Button("Select Process",
                    id="select_process_btn")))
        yield Footer()

    async def on_mount(self) -> int:
        """Mount the TechnologyTypeOptions screen."""
        self.title =  f"User: {self.user_name}, Karma Points: {self.karma_points}"
        self.sub_title = f"Technology Type: {self.tech_type_name}, Description: {self.tech_type_description}"
        self.log(f"Technology Type: {self.tech_type_name}, Description: {self.tech_type_description}")

        for widget in self.query():
            self.log(f"Widgets: {widget}")

        self.log(f"Templates: {self.tech_type_templates}, Processes: {self.tech_type_processes}")
        self.log(f"Templates Type: {type(self.tech_type_templates)}, Processes Type: {type(self.tech_type_processes)}")

        if self.tech_type_templates and self.tech_type_templates != "None":
            for t in self.tech_type_templates:
                try:
                    self.log(f"Template: {t}")
                    templates = self.query_one("#template_options", OptionList).add_option(
                        Option(t.get("displayName")))
                    self.log(f"Added option: {t.get('Catalog Template Name')}")
                    await templates.mount(after=self.query_one("#template_options_label"))
                    self.log(f"Mounted option")
                    self.query_one("#select_template_btn", Button).disabled = False
                    self.log(f"Enabled the template button")
                except NoMatches as e:
                    try:
                        templates: OptionList = OptionList(id="template_options")
                        await templates.mount(after=self.query_one("#template_options_label"))
                        templates.add_option(Option(t.get("displayName")))
                        templates.refresh()
                        self.query_one("#select_template_btn", Button).disabled = False
                        continue
                    except Exception as e:
                        self.log(f"Error creating template option list: {e}, (410")
                        return (410)
                except Exception as e:
                    self.log(f"Error creating template option list: {e} (411)")
                    return (411)
                else:
                    continue
        else:
            try:
                self.log(f" No Templates")
                templates = self.query_one("#template_options", OptionList).add_option(
                    Option("No Templates Found for this Tech Type"))
                await templates.mount(after=self.query_one("#template_options_label"))
                self.query_one("#select_template_btn", Button).disabled = True
            except NoMatches as e:
                try:
                    templates: OptionList = OptionList(id="template_options")
                    await templates.mount(after=self.query_one("#template_options_label"))
                    templates.add_option(Option("No Templates found for this Tech Type"))
                    self.query_one("#select_template_btn", Button).disabled = True
                except Exception as e:
                    self.log(f"Error creating template option list: {e}")
                    return (409)
            except Exception as e:
                self.log(f"Error creating template option list: {e}")
                return (408)

        if self.tech_type_processes and self.tech_type_processes != "None":
            for p in self.tech_type_processes:
                try:
                    self.log(f"Process: {p}")
                    processes = self.query_one("#process_options", OptionList).add_option(
                        Option(p.get("displayName")))
                    self.log(f"Process option added: {p.get('displayName')}")
                    await processes.mount(after=self.query_one("#process_options_label"))
                    self.query_one("#select_process_btn", Button).disabled = False
                    self.log(f"Enabled the process button")
                except NoMatches as e:
                    try:
                        processes: OptionList = OptionList(id="process_options")
                        await processes.mount(after=self.query_one("#process_options_label"))
                        processes.add_option(Option(p.get("displayName")))
                        processes.refresh()
                        self.query_one("#select_process_btn", Button).disabled = False
                    except Exception as e:
                        self.log(f"Error creating process option list: {e}")
                        return (407)
                except Exception as e:
                    self.log(f"Error creating process option list: {e}")
                    return (406)
                else:
                    continue
        else:
            try:
                self.log(f" No Processes")
                processes = self.query_one("#process_options", OptionList).add_option(
                    Option("No processes found for this Tech Type"))
                await processes.mount(after=self.query_one("#process_options_label"))
                self.query_one("#select_process_btn", Button).disabled = True
            except NoMatches as e:
                try:
                    processes: OptionList = OptionList(id="process_options")
                    await processes.mount(after=self.query_one("#process_options_label"))
                    processes.add_option(Option(" No Processes found for this Tech Type"))
                    self.query_one("#select_process_btn", Button).disabled = True
                except Exception as e:
                    self.log(f"Error creating process option list: {e}")
                    return (405)
            except Exception as e:
                self.log(f"Error creating process option list: {e}")
                return (404)

        return(200)

    @on(OptionList.OptionHighlighted, "#template_options")
    def handle_template_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        """Handle the highlighting of an option in the template option list."""
        self.log(f"Template option highlighted: {event.option}")
        self.log(f"Option index: {event.option_index}, Option list: {event.option_list.name}")
        self.selected_template_index = event.option_index
        selected_option = event.option
        self.selected_template = selected_option.prompt
        self.log(f"Highlighted Template: {self.selected_template}, index: {self.selected_template_index}")

    @on(OptionList.OptionSelected, "#template_options")
    def handle_template_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle the selection of an option from the template or process option lists."""
        self.log(f"Template selected: {event.option}")
        self.log(f"Option index: {event.option_index}, Option list: {event.option_list.name}")
        self.option_type_selected = event.option_list.name
        self.selected_template_index = event.option_index
        selected_option = event.option
        self.selected_template = selected_option.prompt
        self.log(f"Selected Option List: {self.option_type_selected}, template: {self.selected_template}, index: {self.selected_template_index}")

    @on(OptionList.OptionHighlighted, "#process_options")
    def handle_process_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        """Handle the highlighting of an option in the process option list."""
        self.log(f"Process option highlighted: {event.option}")
        self.log(f"Option index: {event.option_index}, Option list: {event.option_list.name}")
        self.selected_process_index = event.option_index
        selected_option = event.option
        self.selected_process = selected_option.prompt
        self.log(f"Highlighted Process: {self.selected_process}, index: {self.selected_process_index}")

    @on(OptionList.OptionSelected, "#process_options")
    def handle_process_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle the selection of an option from the template or process option lists."""
        self.log(f"Process selected: {event.option}")
        self.log(f"Option index: {event.option_index}, Option list: {event.option_list.name}")
        self.option_type_selected = event.option_list.name
        self.selected_process_index = event.option_index
        selected_option = event.option
        self.selected_process = selected_option.prompt
        self.log(f"Selected Option List: {self.option_type_selected}, template: {self.selected_process}, index: {self.selected_process_index}")

    def action_go_back(self) -> None:
        """ Handle the back key press."""
        self.dismiss("back")

    def action_Quit(self) -> None:
        """ Handle the quit key press"""
        self.dismiss(200)

    @on(Button.Pressed, "#select_template_btn")
    def handle_template_selected(self, event: Button.Pressed) -> None:
        """Handle the selection of a template option."""
        if self.selected_template is None:
            return
        self.log(f"Template option selected: {self.selected_template}")
        self.dismiss(["template", self.selected_template])

    @on(Button.Pressed, "#select_process_btn")
    def handle_process_selected(self, event: Button.Pressed) -> None:
        """Handle the selection of a process option."""
        if self.selected_process is None:
            return
        self.log(f"Process option selected: {self.selected_process}")
        self.dismiss(["process", self.selected_process])
