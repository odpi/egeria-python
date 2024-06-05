#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple status display of a user's todos
"""

import argparse
import json
import time

from rich import box
from rich.live import Live
from rich.table import Table
from rich import console

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria._deprecated_gov_engine import GovEng
from pyegeria.my_profile_omvs import MyProfile
disable_ssl_warnings = True

good_platform1_url = "https://127.0.0.1:9443"
good_platform2_url = "https://egeria.pdr-associates.com:7443"
bad_platform1_url = "https://localhost:9443"

# good_platform1_url = "https://127.0.0.1:30080"
# good_platform2_url = "https://127.0.0.1:30081"
# bad_platform1_url = "https://localhost:9443"

good_user_1 = "garygeeke"
good_user_2 = "erinoverview"
bad_user_1 = "eviledna"
bad_user_2 = ""

good_server_1 = "active-metadata-store"
good_server_2 = "simple-metadata-store"
good_server_3 = "view-server"
good_server_4 = "engine-host"
bad_server_1 = "coco"
bad_server_2 = ""


def display_todos(server: str = good_server_4, url: str = good_platform1_url, user: str = good_user_1):
    m_client = MyProfile(server, url, user_id=user)
    token = m_client.create_egeria_bearer_token(user, "secret")

    def add_rows(table: Table, guid: str, identity: str) -> None:
        todo_items = m_client.get_assigned_actions(guid)
        if type(todo_items) is str:
            return

        for item in todo_items:
            assigned_actors = [" "]
            if todo_items is None:
                name = " "
                type_name = " "
                todo_guid = " "
                created = " "
                priority = " "
                due = " "
                completed = " "
                status = " "
                sponsor = " "
            else:
                props = item["properties"]
                name = props["name"]
                todo_type_name = props.get("toDoType", " ")
                todo_guid = item["elementHeader"]["guid"]
                created = props.get("creationTime", " ")
                priority = str(props.get("priority", " "))
                due = props.get("dueTime", " ")
                completed = props.get("completionTime", " ")
                status = props.get("status")

                for actor in item["assignedActors"]:
                    assigned_actors.append(actor.get("uniqueName", "NoOne"))
                if status in ("WAITING", "OPEN"):
                    status = f"[yellow]{status}"
                elif status in ("INPROGRESS", "COMPLETE"):
                    status = f"[green]{status}"
                else:
                    status = f"[red]{status}"

            table.add_row(
                str(identity), name, todo_type_name, todo_guid, created, priority, due,
                completed, status, str(assigned_actors)
            )

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Open ToDos for Platform {good_platform1_url} @ {time.asctime()}",
            # style = "black on grey66",
            header_style="white on dark_blue",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"ToDos for Server '{server}' @ Platform - {url}",
            expand=True
        )
        table.add_column("Actor")
        table.add_column("ToDo Name")
        table.add_column("Type Name")
        table.add_column("GUID")
        table.add_column("Created")
        table.add_column("Priority")
        table.add_column("Due")
        table.add_column("Completion")
        table.add_column("Status")
        table.add_column("Sponsor")

        my_profile = m_client.get_my_profile()
        my_guid = my_profile["elementHeader"]["guid"]
        my_ids = my_profile["userIdentities"]
        my_title = my_profile["profileProperties"].get("jobTitle", "No Title")
        user_ids = []
        for id in my_ids:
            user_ids.append(id["userIdentity"]["properties"].get("userId", "NoOne"))
        add_rows(table, my_guid, user_ids)

        my_roles = my_profile["roles"]
        if type(my_roles) is list:
            for role in my_roles:
                role_guid = role["elementHeader"]["guid"]
                role_title = role["properties"].get("title","No Title")
                add_rows(table,role_guid,role_title)

        # m_client.close_session()
        return table

    try:
        with Live(generate_table(), refresh_per_second=4, screen=True) as live:
            while True:
                time.sleep(2)
                live.update(generate_table())
                live.console.pager()

    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
        print_exception_response(e)
        assert e.related_http_code != "200", "Invalid parameters"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the view server to connect to")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    args = parser.parse_args()

    server = args.server if args.server is not None else "view-server"
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'erinoverview'
    print(f"Starting display_todos with {server}, {url}, {userid}")
    display_todos(server=server, url=url, user=userid)
