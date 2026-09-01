"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""
from typing import Any

from textual.widgets._tree import TreeNode

from pyegeria import load_app_config, settings
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Container
from textual.css.query import NoMatches
from textual.screen import ModalScreen
from textual.widgets import Header, Static, OptionList, Button, Footer, Input, Tree, TextArea
from textual.widgets._option_list import Option


class TechnologyTypeOptionsScreen(ModalScreen):
    """ Modal screen to display a technology type's templates and processes."""
    BINDINGS = [("q", "dismiss", "Quit"),
                ("b", "back", "Go_Back"),
                # ("ctl+s", "Select", "tech_type_option_select")
                ]

    CSS_PATH = "my_profile.tcss"

    def __init__(
        self,
        tech_type_guid: str | None = None,
        tech_type_name: str | None = None,
        tech_type_description: str | None = None,
        user_name: str | None = None,
        user_pwd: str | None = None,
        user_kpts: int | None = None,
        tech_type_templates: list[dict] | None = None,
        tech_type_processes: list[dict] | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Initialize the TechnologyTypeOptions screen with a technology type's templates and processes."""
        super().__init__(*args, **kwargs)
        load_app_config()
        app_user = settings.User_Profile
        self.selected_process_index = None
        self.tech_type_guid = tech_type_guid
        self.tech_type_name = tech_type_name or ""
        self.tech_type_description = tech_type_description or ""
        self.user_name = user_name or app_user.user_name or "garygeeke"
        self.user_password = user_pwd or app_user.user_pwd or "secret"
        self.karma_points = user_kpts if user_kpts is not None else 0
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

class TechnologyTypeProcessesScreen(ModalScreen[Any]):
    """Modal screen to display technology type processes in Egeria."""
    BINDINGS = [("q", "quit", "Quit"),
                ("b", "back", "Go back"),
                ("ctl+e", "expand", "Toggle Twisties")]

    CSS_PATH = "my_profile.tcss"

    def __init__(
        self,
        user_name: str | None = None,
        user_kpts: int | None = None,
        tech_type_name: str = "",
        tech_type_description: str = "",
        selected_t_option: str = "",
        tech_type_option_selected: str = "",
        tech_type_processes: list[dict] | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Initialize the TechnologyTypeProcesses screen."""
        super().__init__(*args, **kwargs)
        load_app_config()
        app_user = settings.User_Profile
        self.user_name = user_name or app_user.user_name or "garygeeke"
        self.karma_points = user_kpts if user_kpts is not None else 0
        self.tech_type_name = tech_type_name
        self.tech_type_description = tech_type_description
        self.selected_t_option = selected_t_option
        self.selected_t_option_selected = tech_type_option_selected
        self.tech_type_processes = tech_type_processes
        self.full_process = None
        self.selected_process = None

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


class TechnologyTypesScreen(ModalScreen):
    """Modal screen to display technology types in Egeria."""
    BINDINGS = [("q", "dismiss(200)", "Quit"),
                ("g", "go_back", "Back"),
                ("ctl+e", "expand", "Toggle Twisties")]

    CSS_PATH = "my_profile.tcss"

    def __init__(
        self,
        ttlist: list | None = None,
        user_name: str | None = None,
        user_pwd: str | None = None,
        user_kpts: int | None = None,
        *args,
        **kwargs,
    ):
        """Initialize the TechnologyTypes screen with a list of technology types."""
        super().__init__(*args, **kwargs)
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.tech_type_list = ttlist
        self.user_name = user_name or app_user.user_name or "garygeeke"
        self.user_password = user_pwd or app_user.user_pwd or "secret"
        self.karma_points = user_kpts if user_kpts is not None else 0
        self.tech_type_tree: Tree[str] = Tree(label="Technology Types", id="technology_types_tree")
        self.tech_type_tree.root.expand()
        self.tech_type_tree.auto_expand = True
        self.selected_t_node = None
        self.selected_t_node_label = None
        self.node_id = None
        self.node_status = "expanded"

    def on_mount(self) -> None:
        self.title = f"User: {self.user_name}"
        self.sub_title = "Select a technology type"

    def compose(self) -> ComposeResult:
        """ Compose and display the technology type screen"""
        self.tech_type_tree.refresh()
        if self.tech_type_list:
            self.log(f"Technology types: {self.tech_type_list}, type: {type(self.tech_type_list)}")
            self.render_tech_type_hierarchy_to_tree(self.tech_type_list, self.tech_type_tree)
        else:
            self.tech_type_tree.root.add("No technology types found", expand=True)
        self.tech_type_tree.refresh()
        self.log(f"Technology types tree: {self.tech_type_tree}")

        yield Header(show_clock=True)
        yield ScrollableContainer(
            Static("Display technology types in Egeria"),
            self.tech_type_tree,
            # Button("Select", id="select_tech_type_btn"),
            id="technology_types_table"
        )
        yield Footer()

    def action_quit(self) -> None:
        """ The quit option in the footer has been selected. Dismiss the screen."""
        self.dismiss("200")

    def action_go_back(self) -> None:
        """ The back option in the footer has been selected. Dismiss the screen."""
        self.dismiss("201")

    @on(Tree.NodeSelected)
    def handle_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """ The user has selected a node in the tree. """
        self.log(f"Tree node selected, node: {event.node}")
        self.selected_t_node = event.node
        self.selected_t_node_label = event.node.label
        self.log(f"Selected node: {self.selected_t_node}, label: {self.selected_t_node.label}")
        self.dismiss(str(self.selected_t_node.label))

    @on(Tree.NodeCollapsed)
    def handle_tree_node_collapsed(self, event: Tree.NodeCollapsed) -> None:
        # handle the twisty to close a node in the tree
        # logger.debug(f"TreeNodeCollapsed: {event.node.id}")
        self.node_id = str(event.node.id)
        self.node_status = "collapsed"

    @on(Tree.NodeExpanded)
    def handle_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        # handle the twisty to open a node in the tree
        # logger.debug(f"TreeNodeExpanded: {event.node.id}")
        self.node_id = str(event.node.id)
        self.node_status = "expanded"

    def action_expand(self):
        # handle the hot key to expand/collapse all nodes in the tree (see bindings)
        self.tech_type_tree = self.query_one("#technology_types_tree", Tree)
        if self.node_status == "collapsed":
            self.tech_type_tree.root.expand_all()
        else:
            self.tech_type_tree.root.collapse_all()
        return

    def render_tech_type_hierarchy_to_tree(self,
            data: dict | list[dict],
            tree_or_node: Tree[str] | TreeNode[str],
            label_attr: str = "displayName",
            guid_attr: str = "guid",
            children_attr: str = "subTypes"
    ) -> None:
        """Recursively render a DICT) hierarchy into a Textual Tree.

        Args:
            data: The data structure from pyegeria.get_tech_type_hierarchy.
            tree_or_node: The Tree object or a TreeNode to add children to.
            label_attr: The attribute in the data for the node label.
            guid_attr: The attribute in the data for the node data (GUID).
            children_attr: The attribute in the data containing the list of children.
        """
        if isinstance(data, list):
            for item in data:
                self.render_tech_type_hierarchy_to_tree(item, tree_or_node, label_attr, guid_attr, children_attr)
            return

        if not isinstance(data, dict):
            return

        label = str(data.get(label_attr) or data.get("Display Name") or "Unknown")
        guid = str(data.get(guid_attr) or data.get("GUID") or "")

        # If it's a Tree, we add to root. If it's a TreeNode, we add to it.
        if isinstance(tree_or_node, Tree):
            node = tree_or_node.root.add(label, data=guid, expand=True)
        else:
            node = tree_or_node.add(label, data=guid, expand=True)

        children = data.get(children_attr)
        if children and isinstance(children, list):
            for child in children:
                self.render_tech_type_hierarchy_to_tree(child, node, label_attr, guid_attr, children_attr)


class TechnologyTypeTemplatesScreen(ModalScreen[Any]):
    """Modal screen to display technology type templates in Egeria."""
    BINDINGS = [("q", "dismiss(200)", "Quit"),
                ("b", "back", "Go back"),
                ("ctl+e", "expand", "Toggle Twisties")]

    CSS_PATH = "my_profile.tcss"

    def __init__(
        self,
        user_name: str | None = None,
        user_kpts: int | None = None,
        tech_type_name: str = "",
        tech_type_description: str = "",
        selected_t_option: str = "",
        tech_type_option_selected: str = "",
        tech_type_templates: list[dict] | None = None,
        *args,
        **kwargs,
    ) -> None:
        """Initialize the Technology_Type_Templates screen."""
        super().__init__(*args, **kwargs)
        load_app_config()
        app_user = settings.User_Profile
        self.user_name = user_name or app_user.user_name or "garygeeke"
        self.karma_points = user_kpts if user_kpts is not None else 0
        self.tech_type_name = tech_type_name
        self.tech_type_description = tech_type_description
        self.selected_t_option = selected_t_option
        self.selected_t_option_selected = tech_type_option_selected
        self.tech_type_templates = tech_type_templates
        self.full_template = None
        self.selected_t_template = None

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
