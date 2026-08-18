"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a user screen to allow the user to add todos to my_egeria.

"""

import pwd
from datetime import datetime

import optional
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Horizontal
from textual.screen import ModalScreen
from textual.widgets import DataTable, OptionList, Header, Static, Footer, Input, Button, Switch
from textual.widgets._option_list import Option

from pyegeria import Egeria, PyegeriaException, load_app_config, settings, print_basic_exception


class AddTodoScreen(ModalScreen):
    """Add Todo Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+a", "add_new_todo", "Add New Todo")
        ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, selected_table, user_GUID, *args, **kwargs):
        super().__init__(id="add_todo_screen", *args, **kwargs)
        self.selected_table = selected_table
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"
        self.todo_name = ""
        self.todo_description = ""
        self.todo_priority = ""
        self.todo_guid = ""
        self.user_guid = user_GUID
        self.link_todo_to_profile = True

    def on_mount(self):
        main_screen = self.app.get_screen("main")

        self.todos_table = main_screen.query_one("#todos_table", DataTable)
        assert self.todos_table is not None

        self.todos_table.zebra_stripes = True
        self.todos_table.cursor_type = "row"
        self.todos_table.focus()

    def compose(self) -> ComposeResult:
        yield Static("Add Todo Screen")
        yield ScrollableContainer(
            Static("This screen is intended for the user who wants to add a small number of Todos\n"
                     "Please ensure that you have filled in all fields before clicking 'Add Todo'\n"
                     "For bulk additions please use Dr_Egeria instead."),
            Input("Name of Todo", id="todo_name"),
            Input("Description of Todo", id="todo_description"),
            Input("Priority of Todo", id="todo_priority"),
            Static("Status will be automatically set to 'REQUESTED'"),
            Horizontal(
                Static("Link Todo to your profile? True or False, Default = True"),
                Switch(value=True, id="link_todo_to_profile")
            ),
            Horizontal(
                Button("Add Todo", id="add_todo_button", variant="primary"),
                Button("Quit", id="quit_button", variant="warning")
            ))
        yield Footer()

    def action_add_new_todo(self):
        """ Call Egeria to add the new todo """
        tclient = Egeria(
            view_server=self.view_server,
            platform_url=self.platform_url,
            user_id=self.user_name,
            user_pwd=self.user_password
            )

        try:
            token = tclient.create_egeria_bearer_token(self.user_name, self.user_password)
            todo_guid = tclient.create_my_todo(
                        todo_name=self.todo_name,
                        description=self.todo_description,
                        priority=self.todo_priority,
                        activity_status="REQUESTED"
                        )
            self.log(f"Created ToDo assigned to the current user: {todo_guid}")
            if self.link_todo_to_profile is True:
                try:
                    self.todo_link_guid = tclient.link_todo_to_profile(
                        todo_guid=todo_guid,
                        profile_guid=self.user_guid
                    )
                    self.notify(f"Linked ToDo to profile: {self.todo_link_guid}", timeout=10, severity="information")
                except PyegeriaException as e:
                    self.log(f"Link todo to profile failed with return: {e}")
                    self.notify(f"Link todo to profile failed with return: {e}", timeout=10, severity="error")
        except PyegeriaException as e:
            self.notify(f"Add todo failed with return: {e}", timeout=10, severity="error")
        finally:
            tclient.close_session()
            self.todo_name = ""
            self.todo_description = ""
            self.todo_priority = ""
            self.todo_guid = ""
            self.todo_link_guid = ""
            self.query_one("#todo_name", Input).clear()
            self.query_one("#todo_description", Input).clear()
            self.query_one("#todo_priority", Input).clear()
        return

    @on(Switch.Changed, "#link_todo_to_profile")
    def handle_link_todo_to_profile_changed(self, event: Switch.Changed):
        self.link_todo_to_profile = event.switch.value

    @on(Input.Changed)
    def handle_input_changed(self, event: Input.Changed):
        if event.input.id == "todo_name":
            self.todo_name = event.input.value
        if event.input.id == "todo_description":
            self.todo_description = event.input.value
        if event.input.id == "todo_priority":
            self.todo_priority = event.input.value

    def action_quit(self):
        self.dismiss(200)

    @on(Button.Pressed, "#add_todo_button")
    def handle_add_todo_button(self, event: Button.Pressed):
        """ Handle the add button press """
        if self.todo_name and self.todo_description:
            self.action_add_new_todo()
        else:
            self.notify("Please enter at least anew todo name and description", timeout=10, severity="error")

    @on(Button.Pressed, "#quit_button")
    def handle_quit_button(self, event: Button.Pressed):
        """ Handle the quit button press """
        self.action_quit()


class AddAssociationScreen(ModalScreen):
    """Add Association (Projects or Communities) Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+a", "add_new_association", "Add New Association")
        ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, selected_table, user_GUID, *args, **kwargs):
        super().__init__(id="add_association_screen", *args, **kwargs)
        self.selected_table = selected_table
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.user_guid = user_GUID
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"
        self.project_name = ""
        self.project_description = ""
        self.project_classification = ""
        self.project_identifier = ""
        self.project_start_date = ""
        self.project_end_date = ""
        self.community_name = ""
        self.community_description = ""
        self.community_guid = ""
        self.community_link_guid = ""
        self.project_link_guid = ""
        self.link_community_to_profile = True
        self.link_project_to_profile = True

    def on_mount(self):
        main_screen = self.app.get_screen("main")

    def compose(self) -> ComposeResult:
        yield Static("Add Association Screen")
        yield ScrollableContainer(
            Static("This screen is intended for the user who wants to add a small number of new Projects or Communities to Egeria\n"
                   "First please select which element type you want to add, Project or Community, and the screen will change accordingly.\n"
                   "Please ensure that you have filled in all fields before clicking 'Add Association'\n"
                   "For bulk additions please use Dr_Egeria instead."),
            Input("Element type to be added:", id="element_type"),
            Horizontal(
                Button("Select Element Type", id="select_element_type_button", variant="primary"),
                Button("Quit", id="quit_button", variant="warning"),
                id="add_association_button_container"
                ),
            id="element_type_input",
            )
        yield Footer()

    def display_add_new_project_screen(self):
        input_container = self.query_one("#element_type_input", ScrollableContainer)
        input_container.remove_children()
        input_container.border_title = "Add New Project"
        input_container.mount(Static("Please fill in all input fields before clicking 'Add Project'"),
                              Input("Name of the project:", id="project_name"),
                              Input("Description of the project:", id="project_description"),
                              Static("Classification: Campaign, StudyProject, Task, PersonalProject or Project"),
                              Input("Project Classification:", id="project_classification"),
                              Input("Project Identifier:", id="project_identifier"),
                              Input("Start Date (mm/dd/yyyy):", id="project_start_date"),
                              Input("Planned End Date (mm/dd/yyyy):", id="project_end_date"),
                              Horizontal(
                                  Static("Link Project to your profile? True or False, Default = True"),
                                  Switch(value=True, id="link_project_to_profile")
                              ),
                              Horizontal(
                                  Button("Add Project", id="add_project_button"),
                                  Button("Quit", id="quit_button")
                                  )
                              )

    def display_add_new_community_screen(self):
        input_container = self.query_one("#element_type_input", ScrollableContainer)
        input_container.remove_children()
        input_container.border_title = "Add New Community"
        input_container.mount(Static("Please fill in all input fields before clicking 'Add Project'"),
                              Input("Name of the community:", id="community_name"),
                              Input("Description of the community:", id="community_description"),
                              Horizontal(
                                  Static("Link Community to your profile? True or False, Default = True"),
                                  Switch(value=True, id="link_community_to_profile")
                              ),
                              Horizontal(
                                  Button("Add Community", id="add_community_button"),
                                  Button("Quit", id="quit_button")
                                  )
                              )

    def action_add_new_community(self):
        """ Call Egeria to add the new community """

        tclient = Egeria(
            view_server=self.view_server,
            platform_url=self.platform_url,
            user_id=self.user_name,
            user_pwd=self.user_password
        )

        try:
            token = tclient.create_egeria_bearer_token(self.user_name, self.user_password)

            community_body = {
                "class": "NewElementRequestBody",
                "typeName": "Community",  # community type
                "initialStatus": "ACTIVE",  # initial status of the new element
                "properties": {  # properties for a Community instance
                    "class": "CommunityProperties",
                    "qualifiedName": tclient.__create_qualified_name__("Community", self.community_name),
                    "displayName": self.community_name,  # community name to be displayed in UI
                    "description": self.community_description,  # description of the new element (optional)
                }
            }
            community_guid = tclient.create_community(
                body=community_body
            )
            self.log(f"Created Community: {community_guid}")
            if self.link_community_to_profile is True:
                try:
                    self.community_link_guid = tclient.link_community_to_profile(
                        community_guid=community_guid,
                        profile_guid=self.user_guid
                    )
                    self.notify(f"Linked Community to profile: {self.community_link_guid}", timeout=10, severity="information")
                except PyegeriaException as e:
                    self.log(f"Link community to profile failed with return: {e}")
        except PyegeriaException as e:
            self.notify(f"Add todo failed with return: {e}", timeout=10, severity="error")
        finally:
            tclient.close_session()
            self.community_name = ""
            self.community_description = ""
            self.community_guid = ""
            self.query_one("#community_name", Input).clear()
            self.query_one("#community_description", Input).clear()
        return

    def action_add_new_project(self):
        """ Call Egeria to add the new project """
        tclient = Egeria(
            view_server=self.view_server,
            platform_url=self.platform_url,
            user_id=self.user_name,
            user_pwd=self.user_password
        )
        try:
            token = tclient.create_egeria_bearer_token(self.user_name, self.user_password)
            project_body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "classificationName": "Campaign",  # type of project
                    "displayName": self.project_name,  # display name
                    "description": self.project_description,  # description
                    "identifier": self.project_identifier  # business identifier for the project
                }
            }
            project_guid = tclient.create_project(
                anchor_guid=None,               # The identity of the anchor element for the project.
                parent_guid=None,                # The identity of the parent element for the project.
                parent_relationship_type_name=None,# The type of relationship to the parent element.
                parent_at_end1=False,            # True if the parent is at end 1 of the relationship.
                display_name=self.project_name,   # The display name of the project.
                description=self.project_description,# A description of the project.
                classification_name=self.project_classification,    # The type of project - Campaign, StudyProject, Task, PersonalProject or Project.
                identifier=self.project_identifier,           # A business identifier for the project.
                is_own_anchor=False,            # True if the project is its own anchor.
                status=None,                     # The project status.
                phase=None,                      # The project phase.
                health=None,                     # The project health.
                start_date=self.project_start_date,                 # The start date of the project.
                planned_end_date=self.project_end_date,           # The planned completion date of the project.
                body=project_body                        # A dict representing the details of the project to create.
            )
            self.log(f"Created project: {project_guid}")
            if self.link_project_to_profile is True:
                try:
                    self.project_link_guid = tclient.link_project_to_profile(
                        profile_guid=self.user_guid,
                        project_guid=project_guid
                    )
                    self.log(f"Linked project: {self.project_link_guid}")
                    self.notify(f"Linked project: {self.project_link_guid}", timeout=10, severity="information")
                except PyegeriaException as e:
                    self.notify(f"Link project to profile failed with return: {e}", timeout=10, severity="error")
        except PyegeriaException as e:
            self.notify(f"Add project failed with return: {e}", timeout=10, severity="error")
        finally:
            tclient.close_session()
            self.project_name = ""
            self.project_description = ""
            self.project_classification = ""
            self.project_identifier = ""
            self.project_start_date = ""
            self.project_end_date = ""
            self.query_one("#project_name", Input).clear()
            self.query_one("#project_description", Input).clear()
            self.query_one("#project_classification", Input).clear()
            self.query_one("#project_identifier", Input).clear()
            self.query_one("#project_start_date", Input).clear()
            self.query_one("#project_end_date", Input).clear()
        return

    @on(Switch.Changed, "#link_project_to_profile")
    def handle_link_project_to_profile_changed(self, event: Switch.Changed):
        self.link_project_to_profile = event.switch.value

    @on(Switch.Changed, "#link_community_to_profile")
    def handle_link_community_to_profile_changed(self, event: Switch.Changed):
        self.link_community_to_profile = event.switch.value

    @on(Input.Changed)
    def handle_input_changed(self, event: Input.Changed):
        if event.input.id == "select_element_type":
            self.selected_element_type = event.input.value
            if self.selected_element_type == "Project":
                self.log.info("Selected element type is Project")
            elif self.selected_element_type == "Community":
                self.log.info("Selected element type is Community")
            else:
                self.notify("Invalid element type selected, Only 'Project' or 'Community' are allowed.", severity="error", timeout=15)
        elif event.input.id == "project_name":
            self.project_name = event.input.value
        elif event.input.id == "project_description":
            self.project_description = event.input.value
        elif event.input.id == "project classification":
            self.project_classification = event.input.value
        elif event.input.id == "project_identifier":
            self.project_identifier = event.input.value
        elif event.input.id == "project_start_date":
            self.project_start_date = event.input.value
        elif event.input.id == "project_end_date":
            self.project_end_date = event.input.value
        elif event.input.id == "community_name":
            self.community_name = event.input.value
        elif event.input.id == "community_description":
            self.community_description = event.input.value
        else:
            self.notify("Invalid input field selected.", severity="error", timeout=10)

    def action_quit(self):
        self.dismiss(200)

    @on(Button.Pressed, "#select_element_type_button")
    def handle_select_element_type_button(self, event: Button.Pressed):
        self.selected_element_type = event.button.id
        if self.selected_element_type == "Project":
            self.display_add_new_project_screen()
        elif self.selected_element_type == "Community":
            self.display_add_new_community_screen()
        else:
            self.notify("Invalid element type selected, Only 'Project' or 'Community' are allowed.", severity="error", timeout=15)

    @on(Button.Pressed, "#add_community_button")
    def handle_add_community_button(self, event: Button.Pressed):
        """ Handle the add button press """
        if self.community_name and self.community_description:
            self.action_add_new_community()
        else:
            self.notify("Please enter new community name and description before selecting Add Community button", timeout=10, severity="error")

    @on(Button.Pressed, "#add_project_button")
    def handle_add_project_button(self, event: Button.Pressed):
        """ Handle the add button press """
        if self.project_name and self.project_description:
            self.action_add_new_project()
        else:
            self.notify("Please enter new community name and description before selecting Add Community button",
                        timeout=10, severity="error")

    @on(Button.Pressed, "#quit_button")
    def handle_quit_button(self, event: Button.Pressed):
        """ Handle the quit button press """
        self.action_quit()

class AddBlogEntryScreen(ModalScreen):
    """Add Blog Entry Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+a", "add_new_blog", "Add New Blog Entry")
        ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, selected_table, user_GUID, *args, **kwargs):
        super().__init__(id="add_blog_screen", *args, **kwargs)
        self.selected_table = selected_table
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.user_guid = user_GUID
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"
        self.blog_entry_name = ""
        self.blog_entry_description = ""
        self.blog_entry_priority = ""
        self.blog_entry_guid = ""
        self.link_blog_entry_to_profile = True

    def on_mount(self):
        main_screen = self.app.get_screen("main")

        self.blogs_table = main_screen.query_one("#blogs_table", DataTable)
        assert self.blogs_table is not None

        self.blogs_table.zebra_stripes = True
        self.blogs_table.cursor_type = "row"
        self.blogs_table.focus()

    def compose(self) -> ComposeResult:
        yield Static("Add Blog Entry Screen")
        yield ScrollableContainer(
            Static("This screen is intended for the user who wants to add a small number of blog entries\n"
                   "Please ensure that you have filled in all fields before clicking 'Add Blog Entry'\n"
                   "For bulk additions please use Dr_Egeria instead."),
            Static("Name"),
            Input("Name of Blog Entry", id="blog_entry_name"),
            Static("Text"),
            Input("Text of Entry", id="blog_entry_text"),
            Static("Situation"),
            Input("Situation", id="blog_entry_situation"),
            Horizontal(
                Static("Link Blog Entry to your profile? True or False, Default = True"),
                Switch(value=True, id="link_blog_entry_to_profile")
            ),
            Horizontal(
                Button("Add Blog Entry", id="add_entry_button", variant="primary"),
                Button("Quit", id="quit_button", variant="warning")
            ))
        yield Footer()

    def action_add_new_blog(self):
        """ Call Egeria to add the new blog entry """
        tclient = Egeria(
            view_server=self.view_server,
            platform_url=self.platform_url,
            user_id=self.user_name,
            user_pwd=self.user_password
        )
        try:
            token = tclient.create_egeria_bearer_token(self.user_name, self.user_password)
            body = {
                "class": "NewAttachmentRequestBody",
                "properties": {
                    "class": "BlogEntryProperties",
                    "qualifiedName": f"Blog::Blog-{datetime.now().isoformat()}",
                    "displayName": self.blog_entry_name,
                    "situation": self.blog_entry_situation,
                    "description": self.blog_entry_text,
                }
            }
            blog_entry_response = tclient.blog_my_activity(body=body)
            assert isinstance(blog_entry_response, str)
            blog_entry_guid = blog_entry_response
            self.log(f"Created Blog Entry assigned to the current user: {blog_entry_guid}")
            if self.link_blog_entry_to_profile is True:
                try:
                    tclient.link_element_to_profile(
                        element_guid=self.user_guid,
                        linked_element_guid=blog_entry_guid,
                        relationship_type="BlogEntryToUser",
                        relationship_properties={"class": "BlogEntryToUserProperties"},
                    )
                    self.notify(f"Linked Blog Entry to Profile: {blog_entry_guid}", timeout=10, severity="information")
                except PyegeriaException as e:
                    self.notify(f"Link Blog Entry to Profile failed with return: {e}", timeout=10, severity="error")
        except PyegeriaException as e:
            self.notify(f"Add blog entry failed with return: {e}", timeout=10, severity="error")
        finally:
            tclient.close_session()
            self.blog_entry_name = ""
            self.blog_entry_description = ""
            self.blog_entry_situation = ""
            self.blog_entry_guid = ""
            self.query_one("#blog_entry_name", Input).clear()
            self.query_one("#blog_entry_text", Input).clear()
            self.query_one("#blog_entry_situation", Input).clear()
        return

    @on(Input.Changed)
    def handle_input_changed(self, event: Input.Changed):
        if event.input.id == "blog_entry_name":
            self.blog_entry_name = event.input.value
        if event.input.id == "blog_entry_text":
            self.blog_entry_text = event.input.value
        if event.input.id == "blog_entry_situation":
            self.blog_entry_situation = event.input.value

    @on(Switch.Changed, "#link_blog_entry_to_profile")
    def handle_link_blog_entry_to_profile_changed(self, event: Switch.Changed):
        self.link_blog_entry_to_profile = event.switch.value

    def action_quit(self):
        self.dismiss(200)

    @on(Button.Pressed, "#add_entry_button")
    def handle_add_entry_button(self, event: Button.Pressed):
        """ Handle the add button press """
        self.log(f"Blog entry name: {self.blog_entry_name}, blog entry text: {self.blog_entry_text}, blog entry situation: {self.blog_entry_situation}")
        if self.blog_entry_name:
            self.action_add_new_blog()
        else:
            self.notify("Please enter at least a new blog name and text", timeout=10, severity="error")

    @on(Button.Pressed, "#quit_button")
    def handle_quit_button(self, event: Button.Pressed):
        """ Handle the quit button press """
        self.action_quit()


class AddCommunityScreen(ModalScreen):
    """ Add Community Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+a", "add_new_community", "Add New Community")
        ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, selected_table, user_GUID, *args, **kwargs):
        super().__init__(id="add_community_screen", *args, **kwargs)
        self.selected_table = selected_table
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.user_guid = user_GUID
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"
        self.community_description = ""
        self.community_name = ""
        self.link_community_to_profile = True
    #
    def on_mount(self):
        main_screen = self.app.get_screen("main")

    def compose(self) -> ComposeResult:
        yield Static("Add Community Screen")
        yield ScrollableContainer(
            Static("This screen is intended for the user who wants to add a small number of Communities\n"
                   "Please ensure that you have filled in all fields before clicking 'Add Community'\n"
                   "For bulk additions please use Dr_Egeria instead.\n"
                   "Following the add, please use the Refresh hot key on the main screen to display the updated data"
                    ),
            Input("Name of Community", id="community_display_name"),
            Input("Description of Community", id="community_description"),
            Static("Domain Identifier will be automatically set to '0 - All Domains'"),

            Horizontal(
                Static("Link Community to your profile? True or False, Default = True"),
                Switch(value=True, id="link_community_to_profile")
            ),
            Horizontal(
                Button("Add Community", id="add_community_button", variant="primary"),
                Button("Quit", id="quit_button", variant="warning")
                )
            )
        yield Footer()

    def action_add_new_community(self):
        """ Call Egeria to add the new todo """
        tclient = Egeria(
            view_server=self.view_server,
            platform_url=self.platform_url,
            user_id=self.user_name,
            user_pwd=self.user_password
        )

        try:
            token = tclient.create_egeria_bearer_token(self.user_name, self.user_password)
            body = {
                "class": "Community",
                "properties": {
                    "typeName": "Community",  # the actual Egeria type
                    "qualifiedName": tclient.__create_qualified_name__("Community", self.community_name),
                    "displayName": self.community_name,
                    "description": self.community_description,
                    "domainIdentifier": 0,  # 0 = all domains
                }
            }
            response = tclient.create_governance_definition(body)
            if isinstance(response, dict):
                self.log(f"Created community with ID {response['guid']}")
                if self.link_community_to_profile is True:
                    try:
                        tclient.link_element_to_profile(
                            element_guid=self.user_guid,
                            linked_element_guid=response["guid"],
                            relationship_type="CommunityToUser",
                            relationship_properties={"class": "CommunityToUserProperties"},
                        )
                        self.notify(f"Linked Community to Profile: {response['guid']}", timeout=10, severity="information")
                    except PyegeriaException as e:
                        self.notify(f"Link Community to Profile failed with return: {e}", timeout=10, severity="error")
            else:
                self.log(f"Error creating community: {response}")
        except PyegeriaException as e:
            print_basic_exception(e)
        finally:
            tclient.close_session()

    @on(Input.Changed)
    def handle_input_changed(self, event: Input.Changed):
        if event.input.id == "community_display_name":
            self.community_name = event.input.value
        if event.input.id == "community_description":
            self.community_description = event.input.value

    @on(Switch.Changed, "#link_community_to_profile")
    def handle_link_community_to_profile_changed(self, event: Switch.Changed):
        self.link_community_to_profile = event.switch.value

    def action_quit(self):
        self.dismiss(200)

    @on(Button.Pressed, "#add_community_button")
    def handle_add_todo_button(self, event: Button.Pressed):
        """ Handle the add button press """
        if self.community_name and self.community_description:
            self.action_add_new_community()
        else:
            self.notify("Please enter a community name and description", timeout=10, severity="error")

    @on(Button.Pressed, "#quit_button")
    def handle_quit_button(self, event: Button.Pressed):
        """ Handle the quit button press """
        self.dismiss(200)

class AddJournalEntryScreen(ModalScreen):
    """ Add Journal Entry Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+a", "add_new_journal_entry", "Add New Journal Entry")
        ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, selected_table, user_GUID, *args, **kwargs):
        super().__init__(id="add_journal_entry_screen", *args, **kwargs)
        self.selected_table = selected_table
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.user_guid = user_GUID
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"
        self.journal_entry_title = ""
        self.journal_entry_text = ""
        self.journal_entry_qualified_name = ""
        self.journal_entry_situation = ""
        self.link_journal_entry_to_profile = True

    def on_mount(self):
        main_screen = self.app.get_screen("main")

        self.journal_table = main_screen.query_one("#journal_table", DataTable)
        self.journal_table.zebra_stripes = True
        self.journal_table.cursor_type = "row"
        self.journal_table.focus()

    def compose(self) -> ComposeResult:
        yield Static("Add Todo Screen")
        yield ScrollableContainer(
            Static("Please ensure that you have filled in all fields before clicking 'Add Journal Entry' Button\n"
                   "For bulk additions please use Dr_Egeria instead."),
            Static("Title"),
            Input("Title of Entry", id="journal_entry_title"),
            Static("Text"),
            Input("Text of Entry", id="journal_entry_text"),
            Static("Situation"),
            Input("Situation of Entry", id="journal_entry_situation"),
            Horizontal(
                Button("Add Journal Entry", id="add_journal_entry_button", variant="primary"),
                Button("Quit", id="quit_button", variant="warning")
            ))
        yield Footer()

    def action_add_new_journal_entry(self):
        """ Call Egeria to add the new entry """

        self.qualified_name = f"{self.user_name}:{self.journal_entry_title}:JournalEntry:{datetime.now().isoformat()}"
        body = {
            "class": "NewAttachmentRequestBody",
            "properties": {
                "class": "JournalEntryProperties",
                "qualifiedName": self.qualified_name,
                "displayName": self.journal_entry_title,
                "situation": self.journal_entry_situation,
                "description": self.journal_entry_text
                }
            }
        tclient = Egeria(
            view_server=self.view_server,
            platform_url=self.platform_url,
            user_id=self.user_name,
            user_pwd=self.user_password
        )
        try:
            token = tclient.create_egeria_bearer_token(self.user_name, self.user_password)
            journal_entry_response = tclient.journal_my_activity(body=body)
            assert isinstance(journal_entry_response, str)
            self.log(f"Created Journal Entry for the current user: {journal_entry_response}")
        except PyegeriaException as e:
            self.notify(f"Add journal entry failed with return: {e}", timeout=10, severity="error")
        finally:
            tclient.close_session()
            self.journal_entry_title = ""
            self.journal_entry_text = ""
            self.journal_entry_situation = ""
            self.qualified_name = ""
            self.query_one("#journal_entry_title", Input).clear()
            self.query_one("#journal_entry_text", Input).clear()
            self.query_one("#journal_entry_situation", Input).clear()
        return

    @on(Input.Changed)
    def handle_input_changed(self, event: Input.Changed):
        if event.input.id == "journal_entry_title":
            self.journal_entry_title = event.input.value
        if event.input.id == "journal_entry_text":
            self.journal_entry_text = event.input.value
        if event.input.id == "journal_entry_situation":
            self.journal_entry_situation = event.input.value

    @on(Switch.Changed, "#link_journal_entry_to_profile")
    def handle_link_journal_entry_to_profile_changed(self, event: Switch.Changed):
        self.link_journal_entry_to_profile = event.switch.value

    def action_quit(self):
        self.dismiss(200)

    @on(Button.Pressed, "#add_journal_entry_button")
    def handle_add_journal_entry_button(self, event: Button.Pressed):
        """ Handle the add button press """
        if self.journal_entry_title and self.journal_entry_text:
            self.action_add_new_journal_entry()
        else:
            self.notify("Please enter at least a new title and text for the entry", timeout=10, severity="error")

    @on(Button.Pressed, "#quit_button")
    def handle_quit_button(self, event: Button.Pressed):
        """ Handle the quit button press """
        self.action_quit()


class AddProjectScreen(ModalScreen):
    """Add project Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+a", "add_new_project", "Add New Project")
        ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, selected_table, user_GUID, *args, **kwargs):
        super().__init__(id="add_project_screen", *args, **kwargs)
        self.selected_table = selected_table
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"
        self.project_name = ""
        self.project_description = ""
        self.project_identifier = ""

    def on_mount(self):
        main_screen = self.app.get_screen("main")

    def compose(self) -> ComposeResult:
        yield Static("Add Project Screen")
        yield ScrollableContainer(
            Static("This screen is intended for the user who wants to add a small number of Projects\n"
                   "Please ensure that you have filled in all fields before clicking 'Add Project'\n"
                   "For bulk additions please use Dr_Egeria instead."),
            Input("Name of Project", id="project_name"),
            Input("Description of project", id="project_description"),
            Input("Poject Identifier", id="project_identifier"),
            Horizontal(
                Static("Link Project to your profile? True or False, Default = True"),
                Switch(value=True, id="link_project_to_profile")
            ),
            Horizontal(
                Button("Add Project", id="add_project_button", variant="primary"),
                Button("Quit", id="quit_button", variant="warning")
            ))
        yield Footer()

    def action_add_new_project(self):
        """ Call Egeria to add the new project """
        tclient = Egeria(
            view_server=self.view_server,
            platform_url=self.platform_url,
            user_id=self.user_name,
            user_pwd=self.user_password
        )
        body = {
            "class": "NewElementRequestBody",
            "properties": {
                "classificationName": "Project",  # The type of project
                "displayName": self.project_name,  # Display name for the new element.
                "description": self.project_description,  # Description for the new element.
                "identifier": self.project_identifier,  # A business identifier for the element (e.g., a unique code).
            }
        }

        try:
            token = tclient.create_egeria_bearer_token(self.user_name, self.user_password)
            project_guid = tclient.create_project(
                anchor_guid=None,  # The identity of the anchor element for the project
                parent_guid=None,  # The identity of the parent element for the project
                parent_relationship_type_name="Project",  # The type of relationship to the parent element.
                parent_at_end1=False,
                display_name=body["properties"]["displayName"],  # Display name of the new element.
                description=body["properties"]["description"],  # Description of the new element (optional).
                classification_name=body["properties"]["classificationName"],
                identifier=body["properties"]["identifier"],
                is_own_anchor=True,  # True if this project is its own anchor.
                status=None,
                phase=None,
                health=None,
                start_date=None,
                planned_end_date=None,
                body=body
            )
            self.log(f"Created Project assigned to the current user: {project_guid}")
            if self.link_project_to_profile is True:
                try:
                    link_project_body = {
                        "class": "NewRelationshipRequestBody",
                        "properties": {
                            "relationshipType": "ProjectLinkedToUser"
                        }
                    }

                    project_link_guid = tclient.add_to_project_team(
                        project_guid="PROJECT_GUID",  # identity of the project to update
                        actor_guid=tclient.__create_egeria_user_id__(),
                        # identity of the actor to add (current logged in user)
                        assignment_type=None,  # Name of the role the actor plays in the project.
                        description="",  # Date at which the actor becomes active in the project.
                        body=body
                    )
                    self.notify(f"Project linked to current user, response {project_link_guid}")
                except PyegeriaException as e:
                    print_basic_exception(e)
                    self.notify(f"Link project to user failed with return: {e}", timeout=10, severity="error")
        except PyegeriaException as e:
            self.notify(f"Add project failed with return: {e}", timeout=10, severity="error")
        finally:
            tclient.close_session()
            self.project_name = ""
            self.project_description = ""
            self.project_identifier = ""
            self.project_guid = ""
            self.query_one("#project_name", Input).clear()
            self.query_one("#project_description", Input).clear()
            self.query_one("#project_identifier", Input).clear()
        return

    @on(Input.Changed)
    def handle_input_changed(self, event: Input.Changed):
        if event.input.id == "project_name":
            self.project_name = event.input.value
        if event.input.id == "project_description":
            self.project_description = event.input.value
        if event.input.id == "project_identifier":
            self.project_identifier = event.input.value

    @on(Switch.Changed, "#link_project_to_profile")
    def handle_link_project_to_profile_changed(self, event: Switch.Changed):
        self.link_project_to_profile = event.switch.value

    def action_quit(self):
        self.dismiss(200)

    @on(Button.Pressed, "#add_todo_button")
    def handle_add_project_button(self, event: Button.Pressed):
        """ Handle the add button press """
        if self.project_name and self.project_description and self.project_identifier:
            self.action_add_new_project()
        else:
            self.notify("Please enter a project name, description and identifier", timeout=10, severity="error")

    @on(Button.Pressed, "#quit_button")
    def handle_quit_button(self, event: Button.Pressed):
        """ Handle the quit button press """
        self.action_quit()


class AddRoleScreen(ModalScreen):
    """ Add Role Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+a", "add_new_role", "Add New Role")
        ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, selected_table, user_GUID, *args, **kwargs):
        super().__init__(id="add_role_screen", *args, **kwargs)
        self.user_GUID = user_GUID
        self.selected_table = selected_table
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"
        self.role_name = ""
        self.role_description = ""
        self.link_self_to_role = True

    def on_mount(self):
        main_screen = self.app.get_screen("main")

    def compose(self) -> ComposeResult:
        yield Static("Add Role Screen")
        yield ScrollableContainer(
            Static("This screen is intended for the user who wants to add a small number of Roles\n"
                   "Please ensure that you have filled in all fields before clicking 'Add Role'\n"
                   "For bulk additions please use Dr_Egeria instead."
                   "Once additions are complete Quit and use the Refresh hot key on the main screen to update the display."),
            Input("Name of role", id="role_name"),
            Input("Description of role", id="role_description"),
            Horizontal(
                Static("Link to this role in your profile? (True or False, default is True)"),
                Switch(value=True, id="link_self_to_role"),
            ),
            Horizontal(
                Button("Add Role", id="add_role_button", variant="primary"),
                Button("Quit", id="quit_button", variant="warning")
            ))
        yield Footer()

    def action_add_new_role(self):
        """ Call Egeria to add the new role """

        tclient = Egeria(
            view_server=self.view_server,
            platform_url=self.platform_url,
            user_id=self.user_name,
            user_pwd=self.user_password
        )

        token = tclient.create_egeria_bearer_token(self.user_name, self.user_password)

        role_body = {
            "class": "NewElementRequestBody",
            "isOwnAnchor": True,
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}",
            "properties": {
                "class": "ActorRoleProperties",
                "typeName": "Role",
                "actorProfileGroups": [],
                "qualifiedName": tclient.__create_qualified_name__("Role:", self.role_name),
                "displayName": self.role_name,
                "description": self.role_description,
                "scope": "0",
                "additionalProperties": {
                },
                "extendedProperties": {
                    }
                }
            }

        try:
            self.role_guid = tclient.create_actor_role(body=role_body)
            self.log(f"Created Role by the current user: {self.role_guid}")
            if self.link_self_to_role is True:
                link_body = {
                    "class": "NewRelationshipRequestBody",
                    "externalSourceGUID": "add guid here",
                    "externalSourceName": "add qualified name here",
                    "effectiveTime": "{{$isoTimestamp}}",
                    "forLineage": False,
                    "forDuplicateProcessing": False,
                    "properties": {
                        "class": "PersonRoleAppointmentProperties",
                        "effectiveFrom": "{{$isoTimestamp}}",
                        "effectiveTo": ""
                        }
                    }
                try:
                    self.link_guid = tclient.link_person_role_to_profile({
                        self.role_guid: str,
                        self.user_GUID: str,
                        "body": link_body,
                        })
                except(PyegeriaException) as e:
                    self.notify(f"Linking role failed with return: {e}", timeout=10, severity="error")
                    print_basic_exception(e)
            else:
                self.link_guid = ""
                self.log(f"Link to profile not requested: {self.link_self_to_role}")
        except PyegeriaException as e:
            self.notify(f"Add role failed with return: {e}", timeout=10, severity="error")
        finally:
            tclient.close_session()
            self.role_name = ""
            self.role_description = ""
            self.role_guid = ""
            self.query_one("#role_name", Input).clear()
            self.query_one("#role_description", Input).clear()
        return

    @on(Switch.Changed, "#link_self_to_role")
    def handle_link_self_to_role_changed(self, event: Switch.Changed):
        self.link_self_to_role = event.switch.value

    @on(Input.Changed)
    def handle_input_changed(self, event: Input.Changed):
        if event.input.id == "role_name":
            self.role_name = event.input.value
        if event.input.id == "role_description":
            self.role_description = event.input.value

    def action_quit(self):
        self.dismiss(200)

    @on(Button.Pressed, "#add_role_button")
    def handle_add_role_button(self, event: Button.Pressed):
        """ Handle the add button press """
        if self.role_name and self.role_description:
            self.action_add_new_role()
        else:
            self.notify("Please enter at least anew todo name and description", timeout=10, severity="error")

    @on(Button.Pressed, "#quit_button")
    def handle_quit_button(self, event: Button.Pressed):
        """ Handle the quit button press """
        self.action_quit()

class AddTeamScreen(ModalScreen):
    """Main Screen for My Profile App."""

    BINDINGS = [
        ("q", "app.quit", "Quit"),
        ("ctrl+a", "add_new_team", "Add New Team")
        ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, selected_table, user_GUID, *args, **kwargs):
        super().__init__(id="add_team_screen", *args, **kwargs)
        self.selected_table = selected_table
        self.user_guid = user_GUID
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"
        self.team_name = ""
        self.team_description = ""
        self.team_identifier = ""
        self.team_status = ""
        self.team_phase = ""
        self.team_health = ""

    def on_mount(self):
        main_screen = self.app.get_screen("main")

    def compose(self) -> ComposeResult:
        yield Static("Add Team Screen")
        yield ScrollableContainer(
            Static("This screen is intended for the user who wants to add a small number of new Teams\n"
                   "Please ensure that you have filled in all fields before clicking 'Add Team'\n"
                   "For bulk additions please use Dr_Egeria instead.\n"
                   "Once new teams have been added use the Refresh hot key on the main screen to update the list of teams"),
            Input("Name of Team", id="team_name"),
            Input("Description of Team", id="team_description"),
            Input("Identifier of Team", id="team_identifier"),
            Input("Status of Team, 'Active' or 'Deleted'", id="team_status"),
            Input("Phase of Team, 'planning', 'in_progress', 'completed'", id="team_phase"),
            Input("Health of Team, 'green', 'yellow', 'red'", id="team_health"),
            Static("Domain will be automatically set to '0' - all domains"),
            Horizontal(
                Static("Link Team to your profile? True or False, Default = True"),
                Switch(value=True, id="link_team_to_profile")
            ),
            Horizontal(
                Button("Add Team", id="add_team_button", variant="primary"),
                Button("Quit", id="quit_button", variant="warning")
            ))

    def action_add_new_team(self):
        """ Call Egeria to add the new team """
        tclient = Egeria(
            view_server=self.view_server,
            platform_url=self.platform_url,
            user_id=self.user_name,
            user_pwd=self.user_password
        )

        team_body = {
            "class": "NewElementRequestBody",
            "properties": {
                "classificationName": "Team",  # classification type
                "displayName": self.team_name,
                "description": self.team_description,
                "identifier": self.team_identifier,
                "isOwnAnchor": False,
                "status": self.team_status,  # project status (e.g. 'active')
                "phase": self.team_phase,  # project phase (e.g. 'planning', 'in_progress')
                "health": self.team_health  # project health (e.g. 'green', 'yellow', 'red')
            }
        }
        tclient.create_egeria_bearer_token(self.user_name, self.user_password)
        self.link_team_to_user = self.query_one("#link_team_to_profile")
        try:
            team_guid = tclient.create_team(
                anchor_guid=None,
                parent_guid=None,
                parent_relationship_type_name=None,  # optional
                parent_at_end1=False,  # False by default; indicates the relationship is at end-2 (project)
                display_name=self.team_name,  # project name
                description=self.team_description,  # project description
                classification_name="Team",  # team type
                identifier=None,
                is_own_anchor=True,  # True if this team is its own anchor element
                status="Active",  # team status (e.g. 'Active' or 'Deleted')
                phase=self.team_phase,  # team phase (e.g. 'planning', 'in_progress')
                health=self.team_health,  # team health (e.g. 'green', 'yellow', 'red')
                start_date=None,
                planned_end_date=None,
                body=team_body
            )
            self.log(f"Created Team: {team_guid}")
            self.notify(f"Team created, guid {team_guid}")
            if self.link_team_to_user == True:
                try:
                    # Add the new team GUID to the actor's profile
                    team_link_body = {
                        "class": "NewClassificationRequestBody",
                        "properties": {
                            "class": "SecurityGroupMembershipProperties",
                            "groups": [team_guid],
                            "effectiveFrom": "{{$isoTimestamp}}",
                            "effectiveTo": "{{$isoTimestamp}}"
                        },
                        "externalSourceGUID": self.user_guid,
                        "externalSourceName": "",  # e.g. 'My Actor Profile'
                    }
                    tclient.add_security_group_membershipdef(
                        user_identity_guid="current_user_GUID",  # Replace with actual GUID
                        security_groups=["new_team_GUID"],
                        body=team_link_body,  # Add the new team to the actor's profile
                    )
                except PyegeriaException as e:
                    print_basic_exception(e)
                    self.notify(f"Add team link to profile failed with return: {e}", timeout=10, severity="error")
        except PyegeriaException as e:
            self.notify(f"Add team failed with return: {e}", timeout=10, severity="error")
        finally:
            tclient.close_session()
            self.team_name = ""
            self.team_description = ""
            self.team_identifier = ""
            self.team_status = ""
            self.team_phase = ""
            self.team_health = ""
            self.team_guid = ""
            self.query_one("#team_name", Input).clear()
            self.query_one("#team_description", Input).clear()
            self.query_one("#team_identifier", Input).clear()
            self.query_one("#team_status", Input).clear()
            self.query_one("#team_phase", Input).clear()
            self.query_one("#team_health", Input).clear()
        return

    @on(Input.Changed)
    def handle_input_changed(self, event: Input.Changed):
        if event.input.id == "team_name":
            self.team_name = event.input.value
        if event.input.id == "team_description":
            self.team_description = event.input.value
        if event.input.id == "team_identifier":
            self.team_identifier = event.input.value
        if event.input.id == "team_status":
            self.team_status = event.input.value
        if event.input.id == "team_phase":
            self.team_phase = event.input.value
        if event.input.id == "team_health":
            self.team_health = event.input.value

    @on(Switch.Changed, "#link_team_to_profile")
    def handle_link_team_to_profile_changed(self, event: Switch.Changed):
        self.link_team_to_profile = event.switch.value

    def action_quit(self):
        self.dismiss(200)

    @on(Button.Pressed, "#add_team_button")
    def handle_add_team_button(self, event: Button.Pressed):
        """ Handle the add button press """
        if self.team_name and self.team_description:
            self.action_add_new_team()
        else:
            self.notify("Please enter all the required fields before pressing the 'Add Team' button", timeout=10, severity="error")

    @on(Button.Pressed, "#quit_button")
    def handle_quit_button(self, event: Button.Pressed):
        """ Handle the quit button press """
        self.action_quit()
