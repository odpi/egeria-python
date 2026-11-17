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
from paging_support import is_complete, none_words, paged_rows, read_all
from profile_utils import element_summary, set_screen_heading


class ViewSubscriptionsScreen(ModalScreen):
    """View the digital subscriptions created by the current user."""

    BINDINGS = [
        ("escape", "quit", "Back"),
        ("q", "quit", "Main Menu"),
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
            Static("Your digital subscriptions. Press Escape to go back.", id="view_subsciptions_static"),
            DataTable(id="subscriptions_table", zebra_stripes=True, cursor_type="row"),
            id="view-subscriptions_container",
        )
        yield Footer()

    def on_mount(self):
        set_screen_heading(self, "My Subscriptions")
        table = self.query_one("#subscriptions_table", DataTable)
        table.add_columns("Name", "Status", "Description", "GUID")
        rows = self.get_my_subscriptions()
        if rows is None:   # the read failed (already said): never "you have none"
            return
        for row in rows:
            table.add_row(*row)
        if table.row_count == 0:
            if is_complete(rows):
                self.notify("You have no digital subscriptions", timeout=5)
            else:
                self.notify(none_words("digital subscriptions of yours", complete=False), timeout=10,
                            severity="warning")
        elif getattr(rows, "note", None):
            self.notify(rows.note, timeout=10, severity="warning")

    def get_my_subscriptions(self) -> list[tuple[str, str, str, str]] | None:
        """(name, status, description, GUID) for each DigitalSubscription the user created (PagedRows), or None
        if they could not be read."""
        eclient = None
        try:
            eclient = Egeria(self.view_server, self.platform_url, self.user_name, self.user_password)
            eclient.create_egeria_bearer_token(self.user_name, self.user_password)
            # Every subscription is read (paged to Egeria's end), then filtered here by creator
            def fetch(start: int, size: int):
                return eclient.find_collections(
                    search_string="*",
                    metadata_element_type_name="DigitalSubscription",
                    output_format="JSON",
                    graph_query_depth=0,  # only header/properties are used
                    start_from=start,
                    page_size=size,
                )

            read = read_all(fetch, method="find_collections", client=eclient)
        except PyegeriaException as e:
            print_basic_exception(e)
            self.notify(f"Could not retrieve your subscriptions: {e}", timeout=10, severity="error")
            return None
        finally:
            if eclient:
                eclient.close_session()

        rows = []
        for element in read.items:
            if not isinstance(element, dict):
                continue
            summary = element_summary(element)
            if summary.get("created_by") != self.user_name or not summary.get("guid"):
                continue
            status = str((element.get("properties") or {}).get("contentStatus") or "")
            rows.append((summary["name"], status, summary["description"], summary["guid"]))
        return paged_rows(rows, read, "of your digital subscriptions")

    def action_quit(self):
        self.dismiss(200)
