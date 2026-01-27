#!/usr/bin/env python3
"""
SPDX-Lic
ense-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


Display user actions
"""
import argparse
import os
import time

from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table

from pyegeria import (
    PyegeriaAPIException, PyegeriaClientException, print_basic_exception, ACTIVITY_STATUS, EgeriaTech,
)
from pyegeria.core.utils import list_actors
from pyegeria.omvs.my_profile import MyProfile

EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("EGERIA_VIEW_SERVER", "view-server")
EGERIA_VIEW_SERVER_URL = os.environ.get(
    "EGERIA_VIEW_SERVER_URL", "https://localhost:9443"
)
EGERIA_INTEGRATION_DAEMON = os.environ.get("EGERIA_INTEGRATION_DAEMON", "integration-daemon")
EGERIA_INTEGRATION_DAEMON_URL = os.environ.get(
    "EGERIA_INTEGRATION_DAEMON_URL", "https://localhost:9443"
)
EGERIA_ADMIN_USER = os.environ.get("ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_JUPYTER = bool(os.environ.get("EGERIA_JUPYTER", "False"))
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "200"))


def display_user_actions(
    search_string: str,
    server: str,
    url: str,
    username: str,
    user_pass: str,
    status_filter: list,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
):
    m_client = EgeriaTech(server, url, user_id=username)
    token = m_client.create_egeria_bearer_token(username, user_pass)

    def generate_table(search_string: str = "*") -> Table:
        """Make a new table."""
        table = Table(
            title=f"User Actions for Platform {url} @ {time.asctime()}",
            # style = "black on grey66",
            header_style="white on dark_blue",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"ToDos for Server '{server}' @ Platform - {url}",
            expand=True,
            width=width,
        )


        table.add_column("Action Name")
        table.add_column("Action Type")
        table.add_column("GUID", no_wrap=True)
        table.add_column("Requested Time", no_wrap=True)
        table.add_column("Priority")
        table.add_column("Due")
        table.add_column("Completion")
        table.add_column("Status")
        table.add_column("Sponsor")
        table.add_column("Assigned")

        action_items = m_client.find_processes(search_string, activity_status_list=status_filter, metadata_element_type="Action",
                                               metadata_element_subtypes=["ToDo","Meeting","Notification","Review"],
                                               graph_query_depth=5, relationship_page_size=10)

        if type(action_items) is str:
            name = " "
            type_name = " "
            created = " "
            priority = " "
            due = " "
            completed = " "

            status = " "
            sponsor = " "
            assigned_out = ""
        else:
            for item in action_items:
                guid = item["elementHeader"]["guid"]
                props = item["properties"]
                name = props.get("displayName",'---')
                type_name = props.get("typeName", "---")
                requested = props.get("requestedTime", "---")[:-16]
                priority = str(props.get("priority", "---"))
                due = props.get("dueTime", "---")[:-16]
                completed = props.get("completionTime", "---")[:-16]
                status = props.get("activityStatus", "---")

                assigned_out = ""
                assigned_actors = item.get("assignedActors", None)
                assigned_out = list_actors(assigned_actors)
                sponsor_out = ""
                sponsors = item.get('actionCause', None)
                sponsor_out = list_actors(sponsors)

                if status in ("WAITING", "REQUESTED"):
                    status = f"[yellow]{status}"
                elif status in ("IN_PROGRESS", "COMPLETE"):
                    status = f"[green]{status}"
                else:
                    status = f"[red]{status}"

                table.add_row(
                    name,
                    type_name,
                    guid,
                    requested,
                    priority,
                    due,
                    completed,
                    status,
                    sponsor_out,
                    assigned_out,
                )

        m_client.close_session()
        return table

    try:
        # with Live(generate_table(), refresh_per_second=4, screen=True) as live:
        #     while True:
        #         time.sleep(2)
        #         live.update(generate_table())
        console = Console(width=width, force_terminal=not jupyter)
        with console.pager():
            console.print(generate_table(search_string))

    except (PyegeriaAPIException, PyegeriaClientException) as e:
        print_basic_exception(e)
    except KeyboardInterrupt:
        pass
    finally:
        m_client.close_session()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    # parser.add_argument("--sponsor", help="Name of sponsor to search")
    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    try:
        search_string = Prompt.ask("Enter the Action you are searching for", default="*")
        status_filter = Prompt.ask("Enter the activity statuses to filter on:",
                                   choices=ACTIVITY_STATUS,default="REQUESTED")
        status_filter_list = status_filter.split(",")
        display_user_actions(search_string, server, url, userid, user_pass, status_filter_list)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
