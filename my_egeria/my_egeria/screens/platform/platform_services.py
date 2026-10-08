# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Platform related functions of my_egeria module.


"""

from textual.screen import Screen
from textual.widgets import DataTable
from textual.containers import Container
from textual import events

from my_egeria.services.platform_service import PlatformServices
from my_egeria.widgets.popup import show_popup_and_exit


class PlatformServicesScreen(Screen):
    """Screen to view and manage Egeria platform services."""

    def __init__(self):
        super().__init__()
        self.table = DataTable()
        self.platform_service = PlatformServices()

    async def on_mount(self):
        self.table.add_columns("Platform Name", "URL", "Status")

        try:
            platforms = self.platform_service.list_platforms()
        except ConnectionError as e:
            show_popup_and_exit(str(e))
            return

        for platform in platforms:
            self.table.add_row(
                platform.get("platformName", "Unknown"),
                platform.get("platformURL", "Unknown"),
                platform.get("status", "Unknown"),
            )

        await self.mount(Container(self.table))

    async def on_key(self, event: events.Key):
        if event.key == "q":
            await self.app.pop_screen()
