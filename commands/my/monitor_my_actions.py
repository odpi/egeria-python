#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple status display of a user's todos
"""
import argparse
import os
import time

from rich import box
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table

from pyegeria import print_basic_exception, PyegeriaException, EgeriaTech, ACTIVITY_STATUS
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

disable_ssl_warnings = True


def display_my_todos(

    server: str,
    url: str,
    user: str,
    user_pass: str,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
    status_filter: list = []
):

    m_client = EgeriaTech(server, url, user_id=user, user_pwd=user_pass)
    token = m_client.create_egeria_bearer_token(user, user_pass)

    def add_rows(table: Table, guid: str, identity: str) -> None:
        todo_items = m_client.get_assigned_actions(actor_guid = guid, activity_status_list=status_filter)
        if type(todo_items) is str:
            return

        for item in todo_items:
            assigned_actors = ""
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
                name = props["displayName"]
                todo_type_name = item["elementHeader"]["type"].get("typeName", "---")
                todo_guid = item["elementHeader"].get("guid", "---")
                created = props.get("requestedTime", "---")
                requested_start_time = props.get("requestedStartTime", "---")
                priority = str(props.get("priority", "---"))
                due = props.get("dueTime", "---")
                completed = props.get("completionTime", "---")
                status = props.get("activityStatus")

                for actor in item["assignedActors"]:
                    assigned_actors += f"{actor.get("uniqueName", "---")}\n"
                assigned_actors_out = Markdown(assigned_actors)
                if status in ("WAITING", "OPEN"):
                    status = f"[yellow]{status}"
                elif status in ("IN_PROGRESS", "COMPLETE"):
                    status = f"[green]{status}"
                else:
                    status = f"[red]{status}"

            table.add_row(
                str(identity),
                name,
                todo_type_name,
                todo_guid,
                created[:16],
                requested_start_time[:16],
                priority,
                due,
                completed,
                status,
                assigned_actors_out,
            )

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"My Open Personal Actions for Platform {url} @ {time.asctime()}",
            # style = "black on grey66",
            header_style="white on dark_blue",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"ToDos for Server '{server}' @ Platform - {url}",
            expand=True,
            width=EGERIA_WIDTH,
        )
        table.add_column("Actor")
        table.add_column("Action")
        table.add_column("Action Type")
        table.add_column("GUID", no_wrap=True)
        table.add_column("Created")
        table.add_column("RequestedTime", no_wrap=True)
        table.add_column("Priority")
        table.add_column("Due")
        table.add_column("Completion")
        table.add_column("Status")
        table.add_column("Sponsor")

        my_profile = m_client.get_my_profile()
        my_guid = my_profile["elementHeader"].get("guid", "---")
        my_ids = my_profile["userIdentities"]
        my_title = my_profile["properties"].get("jobTitle", "No Title")
        user_ids = []
        for id in my_ids:
            user_ids.append(id["relatedElement"]["properties"].get("userid", "NoOne"))
            add_rows(
                table,
                id["relatedElement"]["elementHeader"]["guid"],
                id["relatedElement"]["properties"]["userId"],
            )

        add_rows(table, my_guid, user_ids)

        # user_id_guid = my_profile["userIdentity"]["guid"]
        # user_id_name = my_profile["userIdentity"]["properties"]["userid"]
        # add_rows(table, user_id_guid, user_id_name)

        my_roles = my_profile["performsRoles"]
        if type(my_roles) is list:
            for role in my_roles:
                role_guid = role['relatedElement']["elementHeader"]["guid"]
                role_id = role['relatedElement']["properties"].get("roleId", "No Role Id")
                add_rows(table, role_guid, role_id)

        token = m_client.refresh_egeria_bearer_token()
        return table

    try:
        with Live(generate_table(), refresh_per_second=4, screen=True) as live:
            while True:
                time.sleep(2)
                live.update(generate_table())

    except (
        PyegeriaException
    ) as e:
        print_basic_exception(e)

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
    userid = args.userid if args.userid is not None else "erinoverview"
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD

    try:
        status_filter = Prompt.ask("Enter the activity statuses to filter on:",
                                   choices=ACTIVITY_STATUS,default="REQUESTED")
        status_filter_list = status_filter.split(",")

        print(f"Starting display_todos with {server}, {url}, {userid}")
        display_my_todos(server=server, url=url, user=userid, user_pass=user_pass, status_filter=status_filter_list)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
