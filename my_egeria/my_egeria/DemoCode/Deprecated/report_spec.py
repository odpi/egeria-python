"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a set of report specification related functions for my_egeria.

"""
import os

from pydantic import ValidationError
from textual import on
from textual.app import ComposeResult, App
from textual.containers import Container, Horizontal, Grid, Vertical
from textual.widgets import Static, ListView, ListItem, Button, Footer, Header

from pyegeria.base_report_formats import report_spec_list
from pyegeria.format_set_executor import exec_report_spec

from report_spec_splash_screen import SplashScreen
from report_spec_details import ReportSpecDetails

CSS_PATH = ["report_specs.tcss"]

class ReportSpec(App):

    SCREENS = {
        "splash": SplashScreen,
        "spec_details": ReportSpecDetails,
    }

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "back", "Back"),
    ]

    # CSS_PATH = ["report_specs.tcss"]

    class GridChildrenApp(App):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

        def compose(self):
            self.query_one("#spec_grid", Grid).mount()
            return

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.Egeria_config = ["https://127.0.0.1:9443", "qs-view-server", "erinoverview", "secret"]
        self.platform_url = self.Egeria_config[0]
        self.view_server = self.Egeria_config[1]
        self.user = self.Egeria_config[2]
        self.password = self.Egeria_config[3]
        self.selected_report_spec: str = ""
        self.items: list = []

    def compose(self) -> ComposeResult:
        self.heading = "Report Specs"
        self.subheading = "Select a report spec to execute:"
        self.description = "Select a report spec to execute."
        self.report_spec_list = report_spec_list()
        self.log(f"report_spec_list: {self.report_spec_list}, type: {type(self.report_spec_list)}")
        # Split the report spec string into individual report spec names and insert into ListView
        self.report_specs_listview: ListView = ListView()
        self.report_specs_listview.id = "report_specs_listview"
        for item in self.report_spec_list:
            self.items.append(ListItem(Static(f"{item}")))

        yield Header(show_clock=True)
        yield Vertical(
            Static(f"{self.subheading},   {self.description}"),
            Static(f"Server: {self.view_server} | Platform: {self.platform_url} | User: {self.user}"),
            id="connection_info")
        yield Container(
            Static(f"Start of Report Specification List:", id="report_start"),
            ListView(*self.items, id="report_specs_listview"),
            Static(f"End of Report Specification List:", id = "report_end"),
            id = "report_specs_listview_container",
            )
        yield Horizontal(
            Button("Quit", id="quit"),
            Button("Back", id="back"),
            id="action_row"
            )
        yield Footer()
    def on_mount(self) -> None:
        # Apply heights after DOM is built
        self.query_one("#connection_info", Vertical).styles.height = "10%"
        self.query_one("#report_specs_listview_container", Container).styles.height = "80%"
        self.query_one("#action_row", Horizontal).styles.height = "10%"
        self.push_screen("splash")


    def on_splash_screen_splash_continue(self, Message) -> None:
        # continue button pressed on the splash screen, pop the splash screen
        self.pop_screen()

    def on_list_view_selected(self, event: ListView.Selected):
        """ Handle ListView selection event """
        selected_item = event.item.query_one(Static).content
        self.log(f"Selected item: {selected_item} type: {type(selected_item)}")
        selected_item_text = selected_item
        self.log(f"Selected item text: {selected_item_text}, type: {type(selected_item_text)}")
        self.selected_report_spec = selected_item_text
        self.log(f"Selected report spec: {self.selected_report_spec}")
        self.execute_selected_report_spec()

    @on(Button.Pressed, "#quit")
    def handle_button_pressed(self, event: Button.Pressed) -> None:
        """ Quit the application gracefully with a "good" return code (200) """
        self.log(f"Quit button clicked")
        self.exit(200)
        return

    @on(Button.Pressed, "#back")
    def handle_back_button_pressed(self, event: Button.Pressed) -> None:
        """ Return to the main menu screen """
        self.log(f"Back button clicked")
        self.report_spec_list = ""
        self.selected_report_spec = ""
        self.items.clear()
        self.switch_screen("splash")

    def execute_selected_report_spec(self):
        # execute the selected report spec
        self.log(f"Executing report spec: {self.selected_report_spec}")
        try:
            reponse = exec_report_spec(format_set_name=self.selected_report_spec,
                                       output_format="DICT",
                                       view_server=self.view_server,
                                       view_url=self.platform_url,
                                       user=self.user,
                                       user_pass=self.password)
            self.log(f"Return from exec_report_spec:")
            self.log(f"reponse: {reponse}")
        except (ValidationError) as e:
            self.log(f"ValidationError: {e}")
            reponse = {"error": f"ValidationError: {e}"}
        except Exception as e:
            self.log(f"Exception: {e}")
            reponse = {"error": f"Exception: {e}"}
            # self.display_response(reponse)
        spec_details = ReportSpecDetails(reponse)
        self.push_screen(spec_details)

    def on_report_spec_report_details_back(self, Message) -> None:
        """ Return to the main menu screen """
        self.pop_screen()

    def on_report_spec_report_details_quit(self, Message) -> None:
        """ Quit the application gracefully with a "good" return code (200) """
        self.exit(200)

    def on_report_spec_report_details_continue(self, Message) -> None:
        """ Return to the main menu screen """
        self.pop_screen()

if __name__ == "__main__":
    try:
        import pydevd_pycharm
        pydevd_pycharm.settrace(
            "127.0.0.1",  # Ensure it's localhost since your app runs on the same machine as PyCharm
            port=5679,  # Choose an available port
            stdout_to_server=True,
            stderr_to_server=True,
            suspend=False  # Set to False to let the application continue running after starting
        )
    except ImportError:
        print("pydevd-pycharm not installed or setup failed. Debugger won't be active.")
    except Exception as e:
        pass

    app = ReportSpec()
    os.environ.setdefault("EGERIA_PLATFORM_URL", "https://127.0.0.1:9443")
    os.environ.setdefault("EGERIA_VIEW_SERVER", "qs-view-server")
    os.environ.setdefault("EGERIA_USER", "erinoverview")
    os.environ.setdefault("EGERIA_USER_PASSWORD", "secret")
    app.run()
