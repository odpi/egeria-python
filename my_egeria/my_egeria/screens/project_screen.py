# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Screen related functions of my_egeria module.


"""

from textual.widgets import DataTable
from textual.containers import Container
from my_egeria.services.project_manager_service import ProjectManagerService
from .base_screen import BaseScreen
from my_egeria.widgets.back_button import BackButton

class ProjectScreen(BaseScreen):
    CSS_PATH = ["/styles/common.css", "/styles/project_screen.css"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = ProjectManagerService()

    def compose(self):
        yield from super().compose()
        yield Container(BackButton(), DataTable(id="project_table"))

    async def on_mount(self):
        await super().on_mount()
        table = self.query_one("#project_table", DataTable)
        table.clear()
        table.add_columns("ID", "Name", "Description", "Owner")
        for p in self.service.list_projects():
            table.add_row(
                p.get("id"), p.get("name"), p.get("description"), p.get("owner")
            )
