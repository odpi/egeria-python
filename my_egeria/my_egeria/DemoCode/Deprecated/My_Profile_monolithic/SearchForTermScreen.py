"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""
import os

from textual import on
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Header, Footer, Static, Input, Placeholder, Button, Markdown
from pyegeria import load_app_config, settings, PyegeriaException, exec_report_spec


class SearchForTermScreen(ModalScreen):

    BINDINGS = [("q", "quit", "Quit"),
                ("g", "go back", "Go back"),
                ]

    CSS_PATH = "my_profile.tcss"

    def __init__(self, user, password, view_server, platform_url):
        super().__init__()
        self.search_term = ""
        self.view_server = view_server
        self.platform_url = platform_url
        self.user = user
        self.password = password

    def on_mount(self):
        self.title = "Egeria"
        self.sub_title = "Search for Term"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield (Horizontal
            (
            ScrollableContainer
                (
            Static("Search for term, please key in term to search for:"),
            Input(id="search_term_input"),
            Button("Search", id="search_term_btn"),
            id="search_term_input_container"
                ),
            ScrollableContainer
                (
            Static("Result:", id="search_for_term_result_header"),
            Placeholder(id="search_term_result"),
            id="search_term_result_container"
                )))
        yield Footer()

    def action_quit(self) -> None:
        self.log("User requested quit")
        self.dismiss(200)

    def action_go_back(self) -> None:
        self.log("User requested go back")
        self.dismiss(201)

    @on(Input.Changed, "#search_term_input")
    def handle_search_term_input_changed(self, event: Input.Changed) -> None:
        self.search_term = event.value
        self.log(f"Search term input changed: {self.search_term}")

    @on(Button.Pressed, "#search_term_btn")
    async def handle_search_term(self) -> None:
        self.log("User requested search term")
        if self.search_term:
            # search for the term
            search_result = self.search_for_the_term(self.search_term)
            self.log(f"Search result: {search_result}")
            my_placeholder = self.query_one("#search_term_result")
            await my_placeholder.remove()
            markdown = Markdown(search_result, id="search_term_result")
            markdown.code_indent_guides = False
            await self.query_one("#search_term_result_container", ScrollableContainer).mount(markdown)
        else:
            self.log("No search term provided")
            my_placeholder = self.query_one("#search_term_result")
            await my_placeholder.remove()
            markdown = Markdown(f"# No Content Found for: {self.search_term}", id="search_term_result")
            markdown.code_indent_guides = False
            await self.query_one("#search_term_result_container", ScrollableContainer).mount(markdown)

    def search_for_the_term(self, search_term):
        """ Invoke egeria function to search Egeria for the term """
        try:
            self.search_result = exec_report_spec(format_set_name="Glossary-Terms",
                                             output_format="MD",
                                              params={"search_string": search_term, "filter_string": search_term},
                                              view_server=self.view_server,
                                              view_url=self.platform_url,
                                              user=self.user,
                                              user_pass=self.password, )
            if isinstance(self.search_result, dict):
                if self.search_result.get("kind") == "text":
                    if self.search_result.get("mimeType") == "text/markdown":
                        self.search_result = self.search_result.get("content")
                    else:
                        self.search_result = "# No Markdown content found for this glossary term"
                else:
                    self.search_result = "# No Markdown content found for this glossary term"
            else:
                self.search_result = "# No Markdown content found for this glossary term"

            return self.search_result
        except PyegeriaException as e:
            self.log(f"Error searching for term: {e}")
            self.search_result = f"# Error searching for term: {e}"
            return self.search_result
