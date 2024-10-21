#!/usr/bin/env python3
"""
SPDX-Lic
ense-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple display for glossary terms
"""
import os
import argparse
import time

from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria.my_profile_omvs import MyProfile

EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("VIEW_SERVER", "view-server")
EGERIA_VIEW_SERVER_URL = os.environ.get(
    "EGERIA_VIEW_SERVER_URL", "https://localhost:9443"
)
EGERIA_INTEGRATION_DAEMON = os.environ.get("INTEGRATION_DAEMON", "integration-daemon")
EGERIA_INTEGRATION_DAEMON_URL = os.environ.get(
    "EGERIA_INTEGRATION_DAEMON_URL", "https://localhost:9443"
)
EGERIA_ADMIN_USER = os.environ.get("ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_JUPYTER = bool(os.environ.get("EGERIA_JUPYTER", "False"))
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "200"))


def display_to_dos(
    search_string: str,
    status_filter: str,
    server: str,
    url: str,
    username: str,
    user_pass: str,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
):
    m_client = MyProfile(server, url, user_id=username)
    token = m_client.create_egeria_bearer_token(username, user_pass)

    def generate_table(search_string: str = "*") -> Table:
        """Make a new table."""
        table = Table(
            title=f"Open ToDos for Platform {url} @ {time.asctime()}",
            # style = "black on grey66",
            header_style="white on dark_blue",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"ToDos for Server '{server}' @ Platform - {url}",
            expand=True,
        )

        table.add_column("Name")
        table.add_column("Type Name")
        table.add_column("GUID", no_wrap=True)
        table.add_column("Created")
        table.add_column("Priority")
        table.add_column("Due")
        table.add_column("Completion")
        table.add_column("Status")
        table.add_column("Sponsor")
        table.add_column("Assigned")

        todo_items = m_client.find_to_do(search_string, status=status_filter)

        if type(todo_items) is str:
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
            for item in todo_items:
                guid = item["elementHeader"]["guid"]
                props = item["properties"]
                name = props["name"]
                type_name = props.get("toDoType", " ")
                created = props.get("creationTime", " ")[:-19]
                priority = str(props.get("priority", " "))
                due = props.get("dueTime", "          ")[:-19]
                completed = props.get("completionTime", "           ")[:-10]
                status = props.get("toDoStatus", "---")

                assigned_out = ""
                assigned_actors = item.get("assignedActors", "---")
                if type(assigned_actors) is list:
                    assigned_md = ""
                    for actor in assigned_actors:
                        assigned_md += f"* {actor['uniqueName'].split(',')[0]}\n"
                    assigned_out = Markdown(assigned_md)

                sponsor = "erinoverview"
                if status in ("WAITING", "OPEN"):
                    status = f"[yellow]{status}"
                elif status in ("IN_PROGRESS", "COMPLETE"):
                    status = f"[green]{status}"
                else:
                    status = f"[red]{status}"

                table.add_row(
                    name,
                    type_name,
                    guid,
                    created,
                    priority,
                    due,
                    completed,
                    status,
                    sponsor,
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

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
    ) as e:
        print_exception_response(e)
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
        search_string = Prompt.ask("Enter the ToDo you are searching for", default="*")
        status_filter = Prompt.ask(
            "Enter an optional status filter ['OPEN','IN_PROGRESS','WAITING','COMPLETE',"
            "'ABANDONED', 'None']",
            default=None,
        )
        display_to_dos(search_string, status_filter, server, url, userid, user_pass)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
