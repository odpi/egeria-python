# python

"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides services for the Screen related functions of my_egeria module.


"""

from textual.screen import Screen
from textual.widgets import DataTable, Header, Footer
from textual.containers import Container
from my_egeria.widgets.back_button import BackButton
from my_egeria.services.subject_area_service import SubjectAreaService


class SubjectAreaScreen(Screen):
    CSS_PATH = ["/styles/common.css", "/styles/subject_area_screen.css"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = SubjectAreaService()

    def compose(self):
        yield Header()
        yield Container(BackButton(), DataTable(id="subject_area_table"))
        yield Footer()

    def on_mount(self):
        table = self.query_one("#subject_area_table", DataTable)
        table.clear()
        table.add_columns("ID", "Name", "Description")
        for sa in self.service.list_subject_areas():
            table.add_row(sa.get("id"), sa.get("name"), sa.get("description"))

    def on_back_button_back_pressed(self, message):
        self.app.pop_screen()
