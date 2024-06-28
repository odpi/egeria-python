#!/usr/bin/env python3
"""
SPDX-Lic
ense-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple display for glossary terms
"""

import argparse
import time

from rich import box
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria.my_profile_omvs import MyProfile


def display_to_dos(search_string: str, guid:str, server: str, url: str, username: str):

    m_client = MyProfile(server, url, user_id=username)
    token = m_client.create_egeria_bearer_token(username, "secret")

    def generate_table(search_string:str = '*') -> Table:
        """Make a new table."""
        table = Table(
            title=f"Open ToDos for Platform {url} @ {time.asctime()}",
            # style = "black on grey66",
            header_style="white on dark_blue",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"ToDos for Server '{server}' @ Platform - {url}",
            expand=True
        )

        table.add_column("Name")
        table.add_column("Type Name")

        table.add_column("Created")
        table.add_column("Priority")
        table.add_column("Due")
        table.add_column("Completion")
        table.add_column("Status")
        table.add_column("Sponsor")

        todo_items = m_client.find_to_do(search_string)

        if type(todo_items) is str:
            name = " "
            type_name = " "
            created = " "
            priority = " "
            due = " "
            completed = " "
            status = " "
            sponsor = " "
        else:
            for item in todo_items:
                props = item["properties"]
                name = props["name"]
                type_name = props.get("toDoType", " ")
                created = props.get("creationTime", " ")
                priority = str(props.get("priority", " "))
                due = props.get("dueTime", " ")
                completed = props.get("completionTime", " ")
                status = props.get("status")
                # assigned_actors = item["assignedActors"]
                # sponsor = assigned_actors[0].get("uniqueName", " ")
                sponsor = "erinoverview"
                if status in ("WAITING", "OPEN"):
                    status = f"[yellow]{status}"
                elif status in ("IN_PROGRESS", "COMPLETE"):
                    status = f"[green]{status}"
                else:
                    status = f"[red]{status}"

                table.add_row(
                    name, type_name, created, priority, due, completed, status, sponsor
                )

        m_client.close_session()
        return table

    try:
        # with Live(generate_table(), refresh_per_second=4, screen=True) as live:
        #     while True:
        #         time.sleep(2)
        #         live.update(generate_table())
        console = Console(width = 200)
        with console.pager():

            console.print(generate_table(search_string))


    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
        print_exception_response(e)
        assert e.related_http_code != "200", "Invalid parameters"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    # parser.add_argument("--sponsor", help="Name of sponsor to search")
    args = parser.parse_args()

    server = args.server if args.server is not None else "view-server"
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'erinoverview'
    guid = None

    search_string = Prompt.ask("Enter the ToDo you are searching for:", default="*")
    display_to_dos(search_string, guid,server, url, userid)