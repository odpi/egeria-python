# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Screen related functions of my_egeria module.


"""

from textual.widgets import Static, DataTable
from textual.app import ComposeResult
from textual import on
# from pyegeria.admin_services import AdminServices
import os
from .base_screen import BaseScreen


class CohortsScreen(BaseScreen):
    """Screen to list cohort registrations and statuses."""

    BINDINGS = [("r", "refresh_data", "Refresh")]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.table = DataTable()
        # self.admin = AdminServices(
        server_name=os.getenv("EGERIA_SERVER", "myserver"),
        platform_url=os.getenv("EGERIA_PLATFORM_URL", "http://localhost:8080"),
        # )

    def compose(self) -> ComposeResult:
        yield from super().compose()
        yield Static(
            "[b]Cohort Memberships[/b] (Press R to refresh)", id="cohorts_title"
        )
        self.table.add_columns(
            "Cohort Name",
            "Status",
            "Registration ID",
            "Last Connected",
        )
        yield self.table

    def on_mount(self) -> None:
        self.load_cohorts()

    def load_cohorts(self) -> None:
        """Fetch and display cohort information from pyegeria."""
        self.table.clear()
        try:
            cohorts = self.admin.get_cohort_list()
            if cohorts:
                for cohort in cohorts:
                    details = self.admin.get_cohort_registration(cohort) or {}
                    status = details.get("status", "Unknown")
                    reg_id = details.get("registrationId", "")
                    last_conn = details.get("lastConnectedTime", "")
                    self.table.add_row(cohort, status, reg_id, last_conn)
            else:
                self.table.add_row("No cohorts registered", "", "", "")
        except Exception as e:
            self.table.add_row("Error", str(e), "", "")

    @on("r")
    def on_refresh(self) -> None:
        self.load_cohorts()
