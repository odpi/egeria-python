"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a screen listing the current user's digital subscriptions.

"""

from textual.app import ComposeResult
from textual.containers import ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import DataTable, Header, Static, Footer

from pyegeria import Egeria, PyegeriaException, load_app_config, settings, print_basic_exception
from profile_utils import element_summary


class ViewSubscriptionsScreen(ModalScreen):
    """View the digital subscriptions created by the current user."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, *args, **kwargs):
        super().__init__(id="view_subscriptions_screen", *args, **kwargs)
        load_app_config()
        app_config = settings.Environment
        app_user = settings.User_Profile
        self.user_name = app_user.user_name or "garygeeke"
        self.user_password = app_user.user_pwd or "secret"
        self.view_server = app_config.egeria_view_server or "qs-view-server"
        self.platform_url = app_config.egeria_platform_url or "https://127.0.0.1:9443"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield ScrollableContainer(
            Static("Your digital subscriptions. Press q to return.", id="view_subsciptions_static"),
            DataTable(id="subscriptions_table", zebra_stripes=True, cursor_type="row"),
            id="view-subscriptions_container",
        )
        yield Footer()

    def on_mount(self):
        table = self.query_one("#subscriptions_table", DataTable)
        table.add_columns("Name", "Status", "Description", "GUID")
        for row in self.get_my_subscriptions():
            table.add_row(*row)
        if table.row_count == 0:
            self.notify("You have no digital subscriptions", timeout=5)

    def get_my_subscriptions(self) -> list[tuple[str, str, str, str]]:
        """(name, status, description, GUID) for each DigitalSubscription the user created."""
        eclient = None
        try:
            eclient = Egeria(self.view_server, self.platform_url, self.user_name, self.user_password)
            eclient.create_egeria_bearer_token(self.user_name, self.user_password)
            subscriptions = eclient.find_collections(
                search_string="*",
                metadata_element_type_name="DigitalSubscription",
                output_format="JSON",
                graph_query_depth=0,  # only header/properties are used
            )
        except PyegeriaException as e:
            print_basic_exception(e)
            self.notify(f"Could not retrieve your subscriptions: {e}", timeout=10, severity="error")
            return []
        finally:
            if eclient:
                eclient.close_session()

        rows = []
        for element in subscriptions if isinstance(subscriptions, list) else []:
            summary = element_summary(element)
            if summary.get("created_by") != self.user_name or not summary.get("guid"):
                continue
            status = str((element.get("properties") or {}).get("contentStatus") or "")
            rows.append((summary["name"], status, summary["description"], summary["guid"]))
        return rows

    def action_quit(self):
        self.dismiss(200)
