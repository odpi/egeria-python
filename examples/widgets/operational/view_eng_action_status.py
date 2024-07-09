#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple status display for Engine Actions
"""

import argparse
import json
import sys
import time

from rich import box
from rich.console import Console
from rich.table import Table
from rich.live import Live

from pyegeria import AutomatedCuration
from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)

disable_ssl_warnings = True


def display_status_engine_actions(server: str, url: str, user: str):
    g_client = AutomatedCuration(server, url, user, user_pwd="secret")

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Engine Action Status for Platform {url} @ {time.asctime()}",
            # style = "black on grey66",
            header_style="white on dark_blue",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Engine Status for Server '{server}' @ Platform - {url}",
            expand=True
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
            for action in action_status:
                requested_time = action.get("requestedTime", " ")
                start_time = action.get("startTime", " ")
                completion_time = action.get("completionTime", " ")

                engine_name = action["governanceEngineName"]
                request_type = action["requestType"]
                action_guid = action["elementHeader"]["guid"]
                if action["actionStatus"] in ("REQUESTED", "APPROVED", "WAITING", "ACTIVATING"):
                    action_status = f"[yellow]{action['actionStatus']}"
                elif action["actionStatus"] in ("IN_PROGRESS", "ACTIONED"):
                    action_status = f"[green]{action['actionStatus']}"
                else:
                    action_status = f"[red]{action['actionStatus']}"

                target= action.get("actionTargetElements", "Empty")
                if type(target) is list:
                    target_element = json.dumps(target[0]["targetElement"]["elementProperties"]["propertiesAsStrings"])
                else:
                    target_element = " "

                process_name = action.get("processName", " ")
                completion_message = action.get("completionMessage", " ")

                table.add_row(
                    requested_time, start_time, action_guid,engine_name, request_type,
                    action_status, target_element, completion_time, process_name, completion_message
                )
        else:
            print("Egeria integration daemon not running")
            sys.exit()

        return table

    try:
        # console = Console()
        # with console.pager():
        #     console.print(generate_table())
        with Live(generate_table(), refresh_per_second=1, screen=True, vertical_overflow="visible") as live:
            while True:
                time.sleep(2)
                live.update(generate_table())

    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
        print_exception_response(e)
        assert e.related_http_code != "200", "Invalid parameters"
    finally:
        g_client.close_session()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    args = parser.parse_args()

    server = args.server if args.server is not None else "view-server"
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'garygeeke'
    print(f"Starting display_status_engine_actions with {server}, {url}, {userid}")
    display_status_engine_actions(server=server, url=url, user=userid)
