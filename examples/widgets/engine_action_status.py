#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple status display for Engine Actions
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
from pyegeria import GovEng, AutomatedCuration

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


def display_status_engine_actions(server: str = good_server_3, url: str = good_platform1_url, user: str = good_user_1):
    g_client = AutomatedCuration(server, url, user, user_pwd="secret")

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Engine Action Status for Platform {good_platform1_url} @ {time.asctime()}",
            # style = "black on grey66",
            header_style="white on dark_blue",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Engine Status for Server '{server}' @ Platform - {url}",
            expand=True
        )
        table.add_column("Requested Time")
        table.add_column("Start Time")

        table.add_column("Engine Name")
        table.add_column("Request Type")
        table.add_column("Action Status")
        table.add_column("Target Element")
        table.add_column("Completion Time")
        table.add_column("Process Name")
        table.add_column("Completion Message")

        token = g_client.create_egeria_bearer_token()
        action_status = g_client.get_engine_actions()
        if action_status is None:
            requested_time = " "
            start_time = " "
            completion_time = " "
            engine_name = " "
            request_type = " "
            action_status = " "
            target_element = " "
            process_name = " "
            completion_message = " "
        else:
            for action in action_status:
                requested_time = action["requestedTime"]
                start_time = action.get("startTime", " ")
                completion_time = action.get("completionTime", " ")

                engine_name = action["governanceEngineName"]
                request_type = action["requestType"]

                if action["actionStatus"] in ("REQUESTED", "APPROVED", "WAITING", "ACTIVATING"):
                    action_status = f"[yellow]{action['actionStatus']}"
                elif action["actionStatus"] in ("IN_PROGRESS", "ACTIONED"):
                    action_status = f"[green]{action['actionStatus']}"
                else:
                    action_status = f"[red]{action['actionStatus']}"

                target= action.get("actionTargetElements","Empty")
                if type(target) is list:
                    target_element = json.dumps(target[0]["targetElement"]["elementProperties"]["propertiesAsStrings"])
                else:
                    target_element = " "

                process_name = action.get("processName", " ")
                completion_message = action.get("completionMessage", " ")

                table.add_row(
                    requested_time, start_time, engine_name, request_type,
                    action_status, target_element, completion_time, process_name, completion_message
                )

        # g_client.close_session()
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
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    args = parser.parse_args()

    server = args.server if args.server is not None else "view-server"
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'garygeeke'
    print(f"Starting display_status_engine_actions with {server}, {url}, {userid}")
    display_status_engine_actions(server=server, url=url, user=userid)
