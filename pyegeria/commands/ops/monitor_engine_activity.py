#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple status display for Engine Actions
"""

import argparse
import json
import os
import sys
import time

from rich import box
from rich.console import Console
from rich.live import Live
from rich.table import Table

from pyegeria import AutomatedCuration
from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)

EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("EGERIA_VIEW_SERVER", "view-server")
EGERIA_VIEW_SERVER_URL = os.environ.get(
    "EGERIA_VIEW_SERVER_URL", "https://localhost:9443"
)
EGERIA_ENGINE_HOST = os.environ.get("INTEGRATION_ENGINE_HOST", "engine-host")
EGERIA_ENGINE_HOST_URL = os.environ.get(
    "INTEGRATION_ENGINE_HOST_URL", "https://localhost:9443"
)
EGERIA_INTEGRATION_DAEMON = os.environ.get("INTEGRATION_DAEMON", "integration-daemon")
EGERIA_ADMIN_USER = os.environ.get("ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_JUPYTER = bool(os.environ.get("EGERIA_JUPYTER", "False"))
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "200"))

disable_ssl_warnings = True


def display_engine_activity(
    row_limit: int = 0,
    view_server: str = EGERIA_VIEW_SERVER,
    view_url: str = EGERIA_VIEW_SERVER_URL,
    user: str = EGERIA_USER,
    user_pass: str = EGERIA_USER_PASSWORD,
    paging: bool = True,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
):
    """Display governance engine activity as a table.

    Parameters
    ----------
    row_limit : int, opt, default = 0
        If non-zero, limit the number of rows returned
    view_server : str
        The Egeria view server name.
    view_url : str
        The URL for the Egeria view server.
    user : str
        The user name for authenticating with the Egeria server.
    user_pass : str
        The user password for authenticating with the Egeria server.
    paging : bool, default is True
        Whether to enable paging mode when displaying the table.
    jupyter : bool
        Indicates if the environment is a Jupyter notebook.
    width : int
        The width of the console for table printing.
    """
    g_client = AutomatedCuration(view_server, view_url, user, user_pwd=user_pass)

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Engine Action Status for Platform {view_url} @ {time.asctime()}",
            style="bold white on black",
            row_styles=["bold white on black"],
            header_style="white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Engine Status for Server '{view_server}' @ Platform - {view_url}",
            expand=True,
        )
        table.add_column("Requested Time")
        table.add_column("Start Time")
        table.add_column("Action GUID", no_wrap=True)
        table.add_column("Engine Name")
        table.add_column("Request Type")
        table.add_column("Action Status")
        table.add_column("Target Element")
        table.add_column("Completion Time")
        table.add_column("Process Name")
        table.add_column("Completion Message")

        token = g_client.create_egeria_bearer_token()
        action_status = g_client.get_engine_actions()

        if type(action_status) is str:
            requested_time = " "
            start_time = " "
            completion_time = " "
            engine_name = " "
            request_type = " "
            action_status = " "
            target_element = " "
            process_name = " "
            completion_message = " "
        elif type(action_status) is list:
            sorted_action_status = sorted(
                action_status,
                key=lambda i: i.get("requestedTime", time.asctime()),
                reverse=True,
            )
            row_count = 0
            for action in sorted_action_status:
                if row_limit > 0 and row_count >= row_limit:
                    break
                row_count += 1
                requested_time = action.get("requestedTime", " ")
                start_time = action.get("startTime", " ")
                completion_time = action.get("completionTime", " ")

                engine_name = action["governanceEngineName"]
                request_type = action["requestType"]
                action_guid = action["elementHeader"]["guid"]
                if action["actionStatus"] in (
                    "REQUESTED",
                    "APPROVED",
                    "WAITING",
                    "ACTIVATING",
                ):
                    action_status = f"[yellow]{action['actionStatus']}"
                elif action["actionStatus"] in ("IN_PROGRESS", "ACTIONED"):
                    action_status = f"[green]{action['actionStatus']}"
                else:
                    action_status = f"[red]{action['actionStatus']}"

                targets = action.get("actionTargetElements", "Empty")
                if type(targets) is list:
                    tgt_tab = Table()
                    tgt_tab.add_column("name")
                    tgt_tab.add_column("guid", no_wrap=True)
                    tgt_tab.add_column("type_name")
                    targets_md = ""
                    for target in targets:
                        t_name = target["actionTargetName"]
                        t_guid = target["actionTargetGUID"]
                        t_type = target["targetElement"]["type"]["typeName"]
                        tgt_tab.add_row(t_name, t_guid, t_type)
                    # target_element = json.dumps(target[0]["targetElement"]["elementProperties"]["propertiesAsStrings"])
                    target_element = tgt_tab
                else:
                    target_element = " "

                process_name = action.get("processName", " ")
                completion_message = action.get("completionMessage", " ")

                table.add_row(
                    requested_time,
                    start_time,
                    action_guid,
                    engine_name,
                    request_type,
                    action_status,
                    target_element,
                    completion_time,
                    process_name,
                    completion_message,
                )
        else:
            print("Egeria integration daemon not running")
            sys.exit()

        return table

    try:
        if paging is True:
            console = Console(width=width, force_terminal=not jupyter)
            with console.pager():
                console.print(generate_table())
        else:
            with Live(
                generate_table(),
                refresh_per_second=1,
                screen=True,
                vertical_overflow="visible",
            ) as live:
                while True:
                    time.sleep(2)
                    live.update(generate_table())

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
    ) as e:
        print_exception_response(e)
    except KeyboardInterrupt:
        pass
    finally:
        g_client.close_session()


def main_live():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rowlimit", default=0, help="Number of rows to return; 0 for all"
    )
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")

    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_VIEW_SERVER_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    rowlimit = int(args.rowlimit) if args.rowlimit is not None else 0

    display_engine_activity(
        rowlimit, server, url, user=userid, user_pass=user_pass, paging=False
    )


def main_paging():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rowlimit", default=0, help="Number of rows to return; 0 for all"
    )
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")

    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_VIEW_SERVER_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    rowlimit = int(args.rowlimit) if args.rowlimit is not None else 0

    display_engine_activity(
        rowlimit, server, url, user=userid, user_pass=user_pass, paging=True
    )


if __name__ == "__main__":
    main_live()

if __name__ == "__main_paging__":
    main_paging()
