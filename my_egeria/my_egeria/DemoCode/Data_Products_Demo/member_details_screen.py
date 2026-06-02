""" python

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a utility function for my_egeria.

    My_Egeria demos are hard wirewd to work with the Egeria QuickStart configuration
    running in docker containers, but can be easily modified to work with any other
    Egeria configuration.
"""

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Static, Button, DataTable, Header, Footer, ListView, ListItem, Label


class MemberDetailsScreen(ModalScreen):
    """Main menu for the Data Product functions of my_egeria"""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "back", "Back"),
        ]

    CSS_PATH = ["data_products.tcss"]

    class QuitRequested(Message):
        """ Message to terminate application gracefully """
        def __init__(self):
            super().__init__()

    class BackRequested(Message):
        """ Message to terminate application gracefully """
        def __init__(self):
            super().__init__()

    def __init__(self, table_data: list = None):
        super().__init__()
        self.Egeria_config = ["https://127.0.0.1:9443", "qs-view-server", "erinoverview", "secret"]
        self.platform_url = self.Egeria_config[0]
        self.view_server = self.Egeria_config[1]
        self.user = self.Egeria_config[2]
        self.password = self.Egeria_config[3]
        self.token: str
        self.inner_dn: str = table_data[0]
        self.inner_qn: str = table_data[1]
        self.inner_c: str = table_data[2]
        self.inner_d: str = table_data[3]
        self.inner_s: str = table_data[4]
        self.inner_tn: str = table_data[5]
        self.inner_cm = table_data[6]
        self.member_details = table_data[7]
        self.items:list = []

    # def on_mount(self) -> None:
    #     """Create the layout of the screen."""
    #
        # Check that we have at least one Data Product Component

        # self.mount(ListView(*self.items, id="member_listview"), before="#member_after_static")
        # self.member_details_listview.refresh(layout=True, recompose=True)

    def compose(self) -> ComposeResult:
        """Create the layout of the screen."""
        #create the ListView
        self.member_details_listview: ListView = ListView()
        # configure the ListView - member_listview
        self.member_details_listview.id = "member_listview"
        self.log(f"self.inner_gn: {self.inner_qn} ")
        # create the ListView content
        if isinstance(self.inner_qn, str) and self.inner_qn is not None:
            try:
                self.items.append(ListItem(Label(f"Display Name: {self.inner_dn}")))
                self.items.append(ListItem(Label(f"Qualified Name: {self.inner_qn}")))
                self.items.append(ListItem(Label(f"Categories: {self.inner_c})")))
                self.items.append(ListItem(Label(f"Description: {self.inner_d}")))
                self.items.append(ListItem(Label(f"Status: {self.inner_s}")))
                self.items.append(ListItem(Label(f"Type Name: {self.inner_tn}")))
                if isinstance(self.inner_cm, list) and len(self.inner_cm) > 0:
                    self.items.append(ListItem(Label(f"Contains Members:")))
                    for component in self.inner_cm:
                        self.items.append(ListItem(Label(f"Member: {self.inner_cm}")))
            except Exception as e:
                self.items.append(Label(f"Error, Error updating member list, {str(e)}"))
        else:
            self.items.append(Label(f"Error, No Data Product Component Data found"))

        # Place widgets on screen
        yield Header(show_clock=True)
        yield Container(
            Static(
                f"Server: {self.view_server} | Platform: {self.platform_url} | User: {self.user}",
                id="member_connection_info",
            )
        )
        yield Container(
            Static("MyEgeria", id="member_title"),
            Static("Member Details", id="member_details_menu"),
            id = "member_title_row",
        )
        yield ScrollableContainer(
            Vertical(
                Static(f"Member Details:\n\n", id="member_before_static"),
                ListView(*self.items, id="member_listview"),
                Static("\n\nEnd of Data", id="member_after_static"),
            ),
            id="member_content")
        yield Container(
            Button("Quit", id="quit"),
            Button("Back", id="back"),
            id="member_action_row",
        )
        yield Footer()

    @on(Button.Pressed, "#quit")
    async def quit(self) -> None:
        """ Pop this screen and return to previous screen """
        self.post_message(self.QuitRequested())

    def action_quit(self):
        """ Pop this screen and return to previous screen """
        self.post_message(self.QuitRequested())

    def action_back(self):
        """ Pop this screen and return to the previous screen"""
        self.post_message(self.BackRequested())


