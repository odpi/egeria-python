# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Platform related functions of my_egeria module.


"""

from textual.widgets import Static, DataTable
from textual.app import ComposeResult
from textual.containers import Container
from my_egeria.utils.config import get_global_config
from my_egeria.utils.egeria_client import EgeriaTechClientManager
from ..base_screen import BaseScreen


class PlatformsScreen(BaseScreen):
    """Screen to list platforms and their active servers using EgeriaTech."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.table = DataTable()
        self.cfg = get_global_config()
        self.manager = EgeriaTechClientManager(self.cfg)

    def compose(self) -> ComposeResult:
        yield from super().compose()
        yield Static(
            "[b]Egeria Platforms[/b] (Press R to refresh)", id="platforms_title"
        )
        self.table.add_columns(
            "Platform URL",
            "Platform Status",
            "Active Servers",
        )
        yield Container(self.table)

    async def on_mount(self) -> None:
        await super().on_mount()
        await self.load_platforms()

    # rest of file unchanged
