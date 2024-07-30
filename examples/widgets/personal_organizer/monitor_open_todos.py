#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple status display for Open To Dos
"""
import os
import argparse
import time
import sys
from rich import box
from rich.live import Live
from rich.table import Table
from rich import console

from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)

from pyegeria.my_profile_omvs import MyProfile
disable_ssl_warnings = True

EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get('KAFKA_ENDPOINT', 'localhost:9092')
EGERIA_PLATFORM_URL = os.environ.get('EGERIA_PLATFORM_URL', 'https://localhost:9443')
EGERIA_VIEW_SERVER = os.environ.get('VIEW_SERVER', 'view-server')
EGERIA_VIEW_SERVER_URL = os.environ.get('EGERIA_VIEW_SERVER_URL', 'https://localhost:9443')
EGERIA_INTEGRATION_DAEMON = os.environ.get('INTEGRATION_DAEMON', 'integration-daemon')
EGERIA_INTEGRATION_DAEMON_URL = os.environ.get('EGERIA_INTEGRATION_DAEMON_URL', 'https://localhost:9443')
EGERIA_ADMIN_USER = os.environ.get('ADMIN_USER', 'garygeeke')
EGERIA_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'secret')
EGERIA_USER = os.environ.get('EGERIA_USER', 'erinoverview')
EGERIA_USER_PASSWORD = os.environ.get('EGERIA_USER_PASSWORD', 'secret')


def display_todos(server: str , url: str, user: str, user_pass:str):
    m_client = MyProfile(server, url, user_id=user)
    token = m_client.create_egeria_bearer_token(user, user_pass)

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

        todo_items = m_client.find_to_do("*", starts_with=True)
        if type(todo_items) is str:
            print("===> No To Do items found")
            sys.exit()
        if todo_items is None:
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
                elif status in ("INPROGRESS", "COMPLETE"):
                    status = f"[green]{status}"
                else:
                    status = f"[red]{status}"

                table.add_row(
                    name, type_name, created, priority, due, completed, status, sponsor
                )

        return table

    try:
        with Live(generate_table(), refresh_per_second=4, screen=True) as live:
            while True:
                time.sleep(2)
                live.update(generate_table())
                live.console.pager()

    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
        print_exception_response(e)
    except KeyboardInterrupt:
        pass
    finally:
        m_client.close_session()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the view server to connect to")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    display_todos(server=server, url=url, user=userid, user_pass=user_pass)


if __name__ == "__main__":
    main()