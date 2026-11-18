"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides the Work with Projects screen for My Profile.

"""
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Horizontal
from textual.screen import ModalScreen
from textual.widgets import DataTable, Header, Static, Footer, Input, Button, Select, TextArea

from ProjectScreen import ProjectScreen, JOIN_ASSIGNMENT_TYPES
from paging_support import is_complete, none_words
from profile_utils import set_screen_heading

# The "Linked Through" value of a membership held by the user's own profile, which they can leave
DIRECT_LINK = "Your profile"
# Whoever creates a project manages it, so they may also lead it
CREATOR_ASSIGNMENT_TYPES = ["Leader", "ProjectManager"] + JOIN_ASSIGNMENT_TYPES
PROJECT_TYPES = ["Project", "Campaign", "Task", "PersonalProject", "StudyProject", "Experiment", "Investigation"]
# The "Your part in it" choice for a creator who doesn't join their new project
NOT_JOINING = ""


def is_direct_membership(row) -> bool:
    """True if a my-projects row includes a link from the user's own profile."""
    return DIRECT_LINK in row[2].split("; ")


class CreateProjectScreen(ModalScreen):
    """Collect the details of a new project, and the part the user will take in it.

    Dismisses with {"name", "description", "mission", "assignment_type", "project_type"}, where an empty
    assignment_type means the user doesn't join, or None if cancelled.
    """

    BINDINGS = [
        ("escape", "cancel", "Back"),
        ("ctrl+s", "submit", "Create"),
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, id="create_project_screen")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Create Project", classes="span-3", id="create_project_title")
        yield ScrollableContainer(
            Static("Name *"),
            Input(placeholder="Name of the project", id="project_name_input"),
            Static("Description *"),
            Input(placeholder="What the project is about", id="project_description_input"),
            Static("Project Type"),
            Select([(t, t) for t in PROJECT_TYPES], value=PROJECT_TYPES[0], allow_blank=False,
                   id="project_type_select"),
            Static("Mission / Planned Results"),
            TextArea(id="project_mission_text"),
            Static("Your part in it"),
            Select([(t, t) for t in CREATOR_ASSIGNMENT_TYPES] + [("Don't join", NOT_JOINING)],
                   value=CREATOR_ASSIGNMENT_TYPES[0], allow_blank=False, id="project_creator_assignment_type"),
            Horizontal(
                Button("Create", id="submit_create_project_btn", variant="primary"),
                Button("Cancel", id="cancel_create_project_btn", variant="warning"),
            ),
            id="create_project_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        set_screen_heading(self, "Projects - Create Project")
        self.query_one("#project_name_input", Input).focus()

    def action_submit(self) -> None:
        name = self.query_one("#project_name_input", Input).value.strip()
        description = self.query_one("#project_description_input", Input).value.strip()
        if not name or not description:
            self.notify("Please enter both a name and a description for the project", timeout=5,
                        severity="warning")
            return
        self.dismiss({"name": name, "description": description,
                      "mission": self.query_one("#project_mission_text", TextArea).text.strip(),
                      "project_type": self.query_one("#project_type_select", Select).value,
                      "assignment_type": self.query_one("#project_creator_assignment_type", Select).value})

    def action_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#submit_create_project_btn")
    def handle_submit_button(self, event: Button.Pressed) -> None:
        self.action_submit()

    @on(Button.Pressed, "#cancel_create_project_btn")
    def handle_cancel_button(self, event: Button.Pressed) -> None:
        self.action_cancel()


class ConfirmLeaveProjectScreen(ModalScreen[bool]):
    """Confirmation prompt shown before the user leaves a project.

    Dismisses with True to proceed with leaving, False to cancel.
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, project_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs, id="confirm_leave_project_screen")
        self.project_name = project_name

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Leave Project", classes="span-3", id="confirm_leave_project_title")
        yield ScrollableContainer(
            Static(f"[b]Leave {self.project_name}?[/b]"),
            Static("The project is not changed, only the link between you and it."),
            Horizontal(
                Button("Leave", id="submit_leave_project_btn", variant="error"),
                Button("Cancel", id="cancel_leave_project_btn", variant="primary"),
            ),
            id="confirm_leave_project_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        set_screen_heading(self, f"Projects - Leave {self.project_name}")
        self.query_one("#cancel_leave_project_btn", Button).focus()

    def action_cancel(self) -> None:
        self.dismiss(False)

    @on(Button.Pressed, "#submit_leave_project_btn")
    def handle_submit_button(self, event: Button.Pressed) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#cancel_leave_project_btn")
    def handle_cancel_button(self, event: Button.Pressed) -> None:
        self.dismiss(False)


class ProjectsScreen(ModalScreen):
    """The user's projects and the means to find, join, create and leave projects.

    The Egeria work is done by the app's ProjectsMixin (list_my_projects, search_projects,
    create_project, join_project, leave_project); this screen only drives it. Open Project
    opens a ProjectScreen for the highlighted row.
    """

    BINDINGS = [
        ("escape", "quit", "Back"),
        ("q", "quit", "Main Menu"),
        ("ctrl+o", "open_project", "Open Project"),
        ("ctrl+n", "join_project", "Join Project"),
        ("ctrl+t", "create_project", "Create Project"),
        ("ctrl+d", "leave_project", "Leave Project"),
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, my_projects: list[tuple[str, str, str, str, str]], focus_search: bool = False,
                 *args, **kwargs):
        super().__init__(id="projects_screen", *args, **kwargs)
        self.my_projects_data = my_projects or []
        self.focus_search = focus_search
        self.search_string = "*"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Projects", classes="span-3", id="projects_title")
        yield ScrollableContainer(
            Static("[b]The projects you belong to[/b]  [dim]Enter or ctrl+o opens one "
                   "(team, blog/notes, resources and comments); ctrl+d leaves; ctrl+t creates a new project[/dim]"),
            DataTable(id="my_projects_table", zebra_stripes=True, cursor_type="row"),
            Horizontal(
                Button("Open Project", id="open_my_project_btn", variant="primary"),
                Button("Create Project", id="create_project_btn", variant="primary"),
                Button("Leave Project", id="leave_project_btn", variant="error"),
                id="my_projects_buttons",
            ),
            id="my_projects_container",
        )
        yield ScrollableContainer(
            Static("[b]Find other projects[/b]  [dim]enter a search term ('*' for all) and press return; "
                   "ctrl+n joins the highlighted project; Enter or ctrl+o opens it[/dim]"),
            Input(placeholder="Search term or *", id="project_search_input"),
            DataTable(id="projects_found_table", zebra_stripes=True, cursor_type="row"),
            Horizontal(
                Select([(t, t) for t in JOIN_ASSIGNMENT_TYPES], value=JOIN_ASSIGNMENT_TYPES[0],
                       allow_blank=False, id="project_join_assignment_type"),
                Button("Join Project", id="join_project_btn", variant="primary"),
                Button("Open Project", id="open_found_project_btn", variant="primary"),
                id="found_projects_buttons",
            ),
            id="find_projects_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        set_screen_heading(self, "Projects")
        self.query_one("#my_projects_table", DataTable).add_columns(
            "Name", "Assignment Type", "Linked Through", "Description", "GUID")
        self.query_one("#projects_found_table", DataTable).add_columns(
            "Name", "Description", "Qualified Name", "GUID")
        self._fill_my_table()
        self._search()
        if self.focus_search:
            self.query_one("#project_search_input", Input).focus()

    def _fill_my_table(self) -> None:
        table = self.query_one("#my_projects_table", DataTable)
        table.clear()
        for row in self.my_projects_data:
            table.add_row(*row, key=row[4])
        if not self.my_projects_data:
            self.notify("You don't belong to any projects yet - find one to join", timeout=5)

    def _search(self) -> None:
        """Run the current search, listing only projects the user doesn't already belong to."""
        found = self.app.search_projects(self.search_string)
        if found is None:
            return
        table = self.query_one("#projects_found_table", DataTable)
        table.clear()
        mine = {row[4] for row in self.my_projects_data}
        for row in found:
            if row[3] not in mine:
                table.add_row(*row, key=row[3])
        if table.row_count == 0:
            if is_complete(found):
                self.notify(f"No other projects found matching {self.search_string}", timeout=5,
                            severity="warning")
            else:
                self.notify(none_words("other projects", complete=False, matching=self.search_string),
                            timeout=10, severity="warning")
        elif getattr(found, "note", None):
            self.notify(found.note, timeout=10, severity="warning")

    def _reload(self) -> None:
        rows = self.app.list_my_projects()
        if rows is not None:
            self.my_projects_data = rows
            self._fill_my_table()
        self._search()

    @staticmethod
    def _highlighted(table: DataTable) -> list | None:
        if table.row_count == 0:
            return None
        return table.get_row_at(table.cursor_row)

    def action_quit(self) -> None:
        """The user elects to quit the projects function."""
        self.dismiss(200)

    # --- opening a project ------------------------------------------------

    def _open(self, project_guid: str, project_name: str) -> None:
        project_screen = ProjectScreen(project_guid, project_name)

        def on_close(result) -> None:
            # q on the project screen goes on to the main screen
            if result == 210:
                self.dismiss(200)
            elif project_screen.joined:
                # Joined from inside the project: it moves from the found list to the user's own
                self._reload()

        self.app.push_screen(project_screen, callback=on_close)

    def action_open_project(self) -> None:
        """Open the highlighted project in whichever list has focus."""
        found_table = self.query_one("#projects_found_table", DataTable)
        if self.focused is found_table:
            self._open_found()
        else:
            self._open_mine()

    def _open_mine(self) -> None:
        row = self._highlighted(self.query_one("#my_projects_table", DataTable))
        if row is None:
            self.notify("You don't belong to any projects to select", timeout=5, severity="warning")
            return
        self._open(row[4], row[0])

    def _open_found(self) -> None:
        row = self._highlighted(self.query_one("#projects_found_table", DataTable))
        if row is None:
            self.notify("There are no projects found to select", timeout=5, severity="warning")
            return
        self._open(row[3], row[0])

    @on(Button.Pressed, "#open_my_project_btn")
    def handle_open_mine_button(self, event: Button.Pressed) -> None:
        self._open_mine()

    @on(Button.Pressed, "#open_found_project_btn")
    def handle_open_found_button(self, event: Button.Pressed) -> None:
        self._open_found()

    @on(DataTable.RowSelected, "#my_projects_table")
    def handle_my_project_selected(self, event: DataTable.RowSelected) -> None:
        self._open_mine()

    @on(DataTable.RowSelected, "#projects_found_table")
    def handle_found_project_selected(self, event: DataTable.RowSelected) -> None:
        self._open_found()

    # --- finding and joining -------------------------------------------------

    @on(Input.Changed, "#project_search_input")
    def handle_search_changed(self, event: Input.Changed) -> None:
        self.search_string = event.value.strip() or "*"

    @on(Input.Submitted, "#project_search_input")
    def handle_search_submitted(self, event: Input.Submitted) -> None:
        self.search_string = event.value.strip() or "*"
        self._search()

    def action_join_project(self) -> None:
        """Join the project highlighted in the found list."""
        self._join_found()

    def _join_found(self) -> None:
        row = self._highlighted(self.query_one("#projects_found_table", DataTable))
        if row is None:
            self.notify("Please select a project to join from the list below", timeout=5, severity="warning")
            return
        assignment_type = self.query_one("#project_join_assignment_type", Select).value
        if self.app.join_project(row[3], assignment_type):
            self._reload()

    @on(Button.Pressed, "#join_project_btn")
    def handle_join_button(self, event: Button.Pressed) -> None:
        self._join_found()

    # --- creating ------------------------------------------------------------

    def action_create_project(self) -> None:
        def on_create(project_data: dict | None) -> None:
            if not project_data:
                return
            if self.app.create_project(project_data["name"], project_data["description"],
                                       project_data["mission"], project_data["assignment_type"],
                                       project_data.get("project_type", PROJECT_TYPES[0])):
                self._reload()

        self.app.push_screen(CreateProjectScreen(), callback=on_create)

    @on(Button.Pressed, "#create_project_btn")
    def handle_create_button(self, event: Button.Pressed) -> None:
        self.action_create_project()

    # --- leaving -------------------------------------------------------------

    def action_leave_project(self) -> None:
        row = self._highlighted(self.query_one("#my_projects_table", DataTable))
        if row is None:
            self.notify("Please select a project to leave", timeout=5, severity="warning")
            return
        if not is_direct_membership(row):
            self.notify(f"You belong to {row[0]} through a role ({row[2]}), not directly: "
                        f"leaving is not possible from here", timeout=10, severity="warning")
            return

        def on_confirm(proceed: bool) -> None:
            if proceed and self.app.leave_project(row[4]):
                self._reload()

        self.app.push_screen(ConfirmLeaveProjectScreen(row[0]), callback=on_confirm)

    @on(Button.Pressed, "#leave_project_btn")
    def handle_leave_button(self, event: Button.Pressed) -> None:
        self.action_leave_project()
