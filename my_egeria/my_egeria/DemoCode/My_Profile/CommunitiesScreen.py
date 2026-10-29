"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides the Work with Communities screen for My Profile.

"""
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Horizontal
from textual.screen import ModalScreen
from textual.widgets import DataTable, Header, Static, Footer, Input, Button, Select

from CommunityScreen import CommunityScreen

# The "Linked Through" value of a membership held by the user's own profile, which they can leave
DIRECT_LINK = "Your profile"
# Assignment types a user can give themselves when joining. Leaders and administrators are
# assigned by the people who manage the community (https://egeria-project.org/concepts/community/)
JOIN_ASSIGNMENT_TYPES = ["Contributor", "Observer"]


def is_direct_membership(row) -> bool:
    """True if a my-communities row includes a link from the user's own profile."""
    return DIRECT_LINK in row[2].split("; ")


class ConfirmLeaveCommunityScreen(ModalScreen[bool]):
    """Confirmation prompt shown before the user leaves a community.

    Dismisses with True to proceed with leaving, False to cancel.
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, community_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs, id="confirm_leave_community_screen")
        self.community_name = community_name

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Confirm Leaving", classes="span-3", id="confirm_leave_community_title")
        yield ScrollableContainer(
            Static(f"Leave {self.community_name}?"),
            Static("The community is not changed, only the link between you and it."),
            Horizontal(
                Button("Leave", id="confirm_leave_community_btn", variant="error"),
                Button("Cancel", id="cancel_leave_community_btn", variant="primary"),
            ),
            id="confirm_leave_community_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Egeria - my_profile"
        self.sub_title = "Confirm Leaving - Communities"

    @on(Button.Pressed, "#confirm_leave_community_btn")
    def handle_confirm_button(self, event: Button.Pressed) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#cancel_leave_community_btn")
    def handle_cancel_button(self, event: Button.Pressed) -> None:
        self.dismiss(False)

    def action_cancel(self) -> None:
        self.dismiss(False)


class CommunitiesScreen(ModalScreen):
    """List the communities the current user belongs to, find others to join, open a
    community (members, blog and comments) and leave a community.

    The Egeria work is done by the app's CommunitiesMixin (list_my_communities,
    search_communities, join_community, leave_community); this screen only drives it.
    """

    BINDINGS = [
        ("escape", "quit", "Back"),
        ("q", "quit", "Main Menu"),
        ("ctrl+o", "open_community", "Open Community"),
        ("ctrl+n", "join_community", "Join Community"),
        ("ctrl+d", "leave_community", "Leave Community"),
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, my_communities, *args, **kwargs):
        super().__init__(id="communities_screen", *args, **kwargs)
        self.title = "Egeria"
        self.sub_title = "Communities"
        # Rows of (name, assignment type, linked through, description, GUID)
        self.my_communities_data = list(my_communities or [])
        # The last search, repeated after joining or leaving so the found list stays current
        self.search_string = "*"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Communities", classes="span-3", id="communities_title")
        yield ScrollableContainer(
            Static("The communities you belong to. Enter or ctrl+o opens one (members, blog and comments); "
                   "ctrl+d leaves."),
            DataTable(id="my_communities_table", zebra_stripes=True, cursor_type="row"),
            Horizontal(
                Button("Open Community", id="open_my_community_btn", variant="primary"),
                Button("Leave Community", id="leave_community_btn", variant="error"),
                id="my_communities_buttons",
            ),
            id="my_communities_container",
        )
        yield ScrollableContainer(
            Static("Find other communities: enter a search term ('*' for all) and press return"),
            Input(value=self.search_string, placeholder="Search term, or * for all", id="community_search_input"),
            DataTable(id="communities_found_table", zebra_stripes=True, cursor_type="row"),
            Horizontal(
                Select([(t, t) for t in JOIN_ASSIGNMENT_TYPES], value=JOIN_ASSIGNMENT_TYPES[0],
                       allow_blank=False, id="join_assignment_type"),
                Button("Join Community", id="join_community_btn", variant="primary"),
                Button("Open Community", id="open_found_community_btn", variant="default"),
                id="found_communities_buttons",
            ),
            id="find_communities_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#my_communities_table", DataTable).add_columns(
            "Name", "Assignment Type", "Linked Through", "Description", "GUID")
        self.query_one("#communities_found_table", DataTable).add_columns(
            "Name", "Description", "Qualified Name", "GUID")
        self._fill_my_table()
        self._search()

    def _fill_my_table(self) -> None:
        table = self.query_one("#my_communities_table", DataTable)
        table.clear()
        for row in self.my_communities_data:
            table.add_row(*row, key=row[4])
        if not self.my_communities_data:
            self.notify("You don't belong to any communities yet - find one to join", timeout=5)

    def _search(self) -> None:
        """Run the current search, listing only communities the user doesn't already belong to."""
        found = self.app.search_communities(self.search_string)
        if found is None:
            return
        table = self.query_one("#communities_found_table", DataTable)
        table.clear()
        mine = {row[4] for row in self.my_communities_data}
        for row in found:
            if row[3] not in mine:
                table.add_row(*row, key=row[3])
        if table.row_count == 0:
            self.notify(f"No other communities found matching {self.search_string}", timeout=5,
                        severity="warning")

    def _reload(self) -> None:
        rows = self.app.list_my_communities()
        if rows is not None:
            self.my_communities_data = rows
            self._fill_my_table()
        self._search()

    @staticmethod
    def _highlighted(table: DataTable) -> list | None:
        if table.row_count == 0:
            return None
        return table.get_row_at(table.cursor_row)

    def action_quit(self) -> None:
        """ The user elects to quit the communities function """
        self.dismiss(200)

    # --- opening a community ----------------------------------------------

    def _open(self, community_guid: str, community_name: str) -> None:
        def on_close(result) -> None:
            # q on the community screen goes on to the main screen
            if result == 210:
                self.dismiss(200)

        self.app.push_screen(CommunityScreen(community_guid, community_name), callback=on_close)

    def action_open_community(self) -> None:
        """ Open the highlighted community in whichever list has focus """
        found_table = self.query_one("#communities_found_table", DataTable)
        if self.focused is found_table:
            self._open_found()
        else:
            self._open_mine()

    def _open_mine(self) -> None:
        row = self._highlighted(self.query_one("#my_communities_table", DataTable))
        if row is None:
            self.notify("You don't belong to any communities to select", timeout=5, severity="warning")
            return
        self._open(row[4], row[0])

    def _open_found(self) -> None:
        row = self._highlighted(self.query_one("#communities_found_table", DataTable))
        if row is None:
            self.notify("There are no communities found to select", timeout=5, severity="warning")
            return
        self._open(row[3], row[0])

    @on(Button.Pressed, "#open_my_community_btn")
    def handle_open_mine_button(self, event: Button.Pressed) -> None:
        self._open_mine()

    @on(Button.Pressed, "#open_found_community_btn")
    def handle_open_found_button(self, event: Button.Pressed) -> None:
        self._open_found()

    @on(DataTable.RowSelected, "#my_communities_table")
    def handle_my_community_selected(self, event: DataTable.RowSelected) -> None:
        self._open_mine()

    @on(DataTable.RowSelected, "#communities_found_table")
    def handle_found_community_selected(self, event: DataTable.RowSelected) -> None:
        self._open_found()

    # --- finding and joining -------------------------------------------------

    @on(Input.Submitted, "#community_search_input")
    def handle_community_search(self, event: Input.Submitted) -> None:
        self.search_string = event.value.strip() or "*"
        self._search()
        found_table = self.query_one("#communities_found_table", DataTable)
        if found_table.row_count:
            found_table.focus()

    @on(Button.Pressed, "#join_community_btn")
    def handle_join_button(self, event: Button.Pressed) -> None:
        self.action_join_community()

    def action_join_community(self) -> None:
        """ The user joins the highlighted found community, with the chosen assignment type """
        row = self._highlighted(self.query_one("#communities_found_table", DataTable))
        if row is None:
            self.notify("Find a community to join first", timeout=5, severity="warning")
            return
        assignment_type = self.query_one("#join_assignment_type", Select).value
        if self.app.join_community(row[3], assignment_type):
            self._reload()

    # --- leaving -------------------------------------------------------------

    @on(Button.Pressed, "#leave_community_btn")
    def handle_leave_button(self, event: Button.Pressed) -> None:
        self.action_leave_community()

    def action_leave_community(self) -> None:
        """ The user wants to leave the highlighted community, after confirmation """
        row = self._highlighted(self.query_one("#my_communities_table", DataTable))
        if row is None:
            self.notify("You don't belong to any communities to leave", timeout=5, severity="warning")
            return
        community_name, community_guid = row[0], row[4]
        if not is_direct_membership(row):
            self.notify(f"You belong to {community_name} through a role ({row[2]}), so you can't leave it "
                        f"here; ask whoever manages that role", timeout=10, severity="warning")
            return

        def on_confirm(confirmed: bool | None) -> None:
            if not confirmed:
                self.notify(f"You are still a member of {community_name}", timeout=5)
                return
            if self.app.leave_community(community_guid):
                self._reload()

        self.app.push_screen(ConfirmLeaveCommunityScreen(community_name), callback=on_confirm)
