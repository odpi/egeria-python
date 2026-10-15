"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides the My Network screen for My Profile.

"""
from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import DataTable, Header, Static, Footer, Input, Button


class ConfirmRemovePeerScreen(ModalScreen[bool]):
    """Confirmation prompt shown before a person is removed from the user's network.

    Dismisses with True to proceed with the removal, False to cancel.
    """

    BINDINGS = [("escape", "cancel", "Cancel")]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, peer_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs, id="confirm_remove_peer_screen")
        self.peer_name = peer_name

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Confirm Removal", classes="span-3", id="confirm_remove_peer_title")
        yield ScrollableContainer(
            Static(f"Remove {self.peer_name} from your network?"),
            Static("Their profile is not changed, only the link between you."),
            Horizontal(
                Button("Remove", id="confirm_remove_peer_btn", variant="error"),
                Button("Cancel", id="cancel_remove_peer_btn", variant="primary"),
            ),
            id="confirm_remove_peer_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Egeria - my_profile"
        self.sub_title = "Confirm Removal - My Network"

    @on(Button.Pressed, "#confirm_remove_peer_btn")
    def handle_confirm_button(self, event: Button.Pressed) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#cancel_remove_peer_btn")
    def handle_cancel_button(self, event: Button.Pressed) -> None:
        self.dismiss(False)

    def action_cancel(self) -> None:
        self.dismiss(False)


class MyNetworkScreen(ModalScreen):
    """List the current user's network of peers, add people to it and remove them.

    The Egeria work is done by the app's NetworkMixin (list_my_peers, search_people,
    link_peer, unlink_peer, get_peer_details); this screen only drives it.
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("v", "view_details", "View Highlighted Person"),
        ("d", "remove_peer", "Remove Highlighted Person"),
    ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, my_peers, *args, **kwargs):
        super().__init__(id="my_network_screen", *args, **kwargs)
        self.title = "Egeria"
        self.sub_title = "My Network"
        # Rows of (qualified name, display name, full name, pronouns, GUID, description)
        self.my_peers_data = list(my_peers or [])
        # (display name, GUID) of the person picked from the search results to add
        self.selected_person = None
        # GUID of the peer whose details are currently displayed
        self.details_peer_guid = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("My Network", classes="span-3", id="my_network_title")
        yield ScrollableContainer(
            Static("The people in your network. 'v' shows the highlighted person's details; 'd' removes them."),
            DataTable(id="my_network_table", zebra_stripes=True, cursor_type="row"),
            Horizontal(
                Button("Person Details", id="peer_details_btn", variant="primary"),
                Button("Remove from Network", id="remove_peer_btn", variant="error"),
                id="my_network_buttons",
            ),
            id="my_network_container",
        )
        yield ScrollableContainer(
            Static("Add to your network: enter a (partial) name and press return"),
            Input(placeholder="Name", id="people_search_input"),
            DataTable(id="people_found_table", zebra_stripes=True, cursor_type="row"),
            Container(id="add_peer_container"),
            id="people_search_container",
        )
        yield ScrollableContainer(
            Static("", id="peer_details_heading"),
            Static("Contact Methods:"),
            DataTable(id="peer_contacts_table", zebra_stripes=True, cursor_type="row"),
            Static("Communities:"),
            DataTable(id="peer_communities_table", zebra_stripes=True, cursor_type="row"),
            id="peer_details_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#my_network_table", DataTable).add_columns(
            "Qualified Name", "Display Name", "Full Name", "Pronouns", "GUID", "Description")
        self.query_one("#people_found_table", DataTable).add_columns("Name", "GUID", "Qualified Name")
        self.query_one("#peer_contacts_table", DataTable).add_columns(
            "Name", "Method Type", "Contact Type", "Service", "Value", "GUID")
        self.query_one("#peer_communities_table", DataTable).add_columns(
            "Name", "Assignment Type", "Description", "GUID")
        self.query_one("#peer_details_container").display = False
        self._fill_table()

    def _fill_table(self) -> None:
        table = self.query_one("#my_network_table", DataTable)
        table.clear()
        for row in self.my_peers_data:
            table.add_row(*row, key=row[4])
        if not self.my_peers_data:
            self.notify("There is no-one in your network yet - search for someone to add them", timeout=5)

    def _reload(self) -> None:
        rows = self.app.list_my_peers()
        if rows is not None:
            self.my_peers_data = rows
            self._fill_table()

    def _highlighted_peer(self) -> tuple[str, str] | None:
        """(display name, GUID) of the highlighted network row, or None if the network is empty."""
        table = self.query_one("#my_network_table", DataTable)
        if table.row_count == 0:
            self.notify("There is no-one in your network to select", timeout=5, severity="warning")
            return None
        row = table.get_row_at(table.cursor_row)
        return row[1] or row[0], row[4]

    def action_quit(self) -> None:
        """ The user elects to quit the network function """
        self.dismiss(200)

    @on(Button.Pressed, "#peer_details_btn")
    def handle_peer_details_button(self, event: Button.Pressed) -> None:
        self.action_view_details()

    def action_view_details(self) -> None:
        """ Show the contact methods and communities of the highlighted peer """
        peer = self._highlighted_peer()
        if not peer:
            return
        peer_name, peer_guid = peer
        details = self.app.get_peer_details(peer_guid)
        if details is None:
            return
        contacts, communities = details
        contacts_table = self.query_one("#peer_contacts_table", DataTable)
        contacts_table.clear()
        for contact in contacts:
            contacts_table.add_row(contact.get("name"),
                                   contact.get("contactMethodType"),
                                   contact.get("contactType"),
                                   contact.get("contactMethodService"),
                                   contact.get("contactMethodValue"),
                                   contact.get("guid"))
        communities_table = self.query_one("#peer_communities_table", DataTable)
        communities_table.clear()
        for community in communities:
            communities_table.add_row(community.get("name"),
                                      community.get("assignmentType"),
                                      community.get("description"),
                                      community.get("guid"))
        self.query_one("#peer_details_heading", Static).update(f"[b]Details for {peer_name}[/b]")
        self.query_one("#peer_details_container").display = True
        self.details_peer_guid = peer_guid
        if not contacts:
            self.notify(f"No contact methods found for {peer_name}", timeout=10)
        if not communities:
            self.notify(f"No community memberships found for {peer_name}", timeout=10)

    @on(Button.Pressed, "#remove_peer_btn")
    def handle_remove_peer_button(self, event: Button.Pressed) -> None:
        self.action_remove_peer()

    def action_remove_peer(self) -> None:
        """ The user wants to remove the highlighted peer, after confirmation """
        peer = self._highlighted_peer()
        if not peer:
            return
        peer_name, peer_guid = peer

        def on_confirm(confirmed: bool | None) -> None:
            if not confirmed:
                self.notify(f"{peer_name} was not removed from your network", timeout=5)
                return
            if self.app.unlink_peer(peer_guid):
                # hide the details panel if it is showing the person just removed
                if self.details_peer_guid == peer_guid:
                    self.query_one("#peer_details_container").display = False
                    self.details_peer_guid = None
                self._reload()

        self.app.push_screen(ConfirmRemovePeerScreen(peer_name), callback=on_confirm)

    @on(Input.Submitted, "#people_search_input")
    def handle_people_search(self, event: Input.Submitted) -> None:
        search_string = event.value.strip()
        if not search_string:
            self.notify("Enter a (partial) name to search for", timeout=5, severity="warning")
            return
        found = self.app.search_people(search_string)
        if found is None:
            return
        table = self.query_one("#people_found_table", DataTable)
        table.clear()
        in_network = {row[4] for row in self.my_peers_data}
        for name, guid, qualified_name in found:
            if guid not in in_network:
                table.add_row(name, guid, qualified_name, key=guid)
        if table.row_count == 0:
            self.notify(f"No-one new found matching {search_string}", timeout=5, severity="warning")
        else:
            self.notify("Select a person to add them to your network", timeout=5)
            table.focus()

    @on(DataTable.RowSelected, "#people_found_table")
    def handle_person_selected(self, event: DataTable.RowSelected) -> None:
        name, guid, qualified_name = event.data_table.get_row(event.row_key)
        self.selected_person = (name, guid)
        container = self.query_one("#add_peer_container", Container)
        container.remove_children()
        container.mount(
            Static(f"Add [b]{name}[/b] ({qualified_name}) to your network"),
            Input(placeholder="Nickname (optional)", id="peer_nickname_input"),
            Input(placeholder="Description/comment about this relationship (optional)", id="peer_description_input"),
            Horizontal(
                Button("Add to Network", id="add_peer_btn", variant="primary"),
                Button("Cancel", id="cancel_add_peer_btn", variant="warning"),
            ),
        )
        self.query_one("#peer_nickname_input", Input).focus()

    @on(Button.Pressed, "#add_peer_btn")
    def handle_add_peer_button(self, event: Button.Pressed) -> None:
        if not self.selected_person:
            return
        nickname = self.query_one("#peer_nickname_input", Input).value.strip()
        description = self.query_one("#peer_description_input", Input).value.strip()
        if self.app.link_peer(self.selected_person[1], nickname, description):
            self._clear_search()
            self._reload()

    @on(Button.Pressed, "#cancel_add_peer_btn")
    def handle_cancel_add_peer_button(self, event: Button.Pressed) -> None:
        self.query_one("#add_peer_container", Container).remove_children()
        self.selected_person = None

    def _clear_search(self) -> None:
        self.query_one("#add_peer_container", Container).remove_children()
        self.query_one("#people_found_table", DataTable).clear()
        self.query_one("#people_search_input", Input).clear()
        self.selected_person = None
