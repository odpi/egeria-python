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

from rich.live import Live
from rich.table import Table
from rich.console import Console

from pyegeria import AutomatedCuration
from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)

EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get('KAFKA_ENDPOINT', 'localhost:9092')
EGERIA_PLATFORM_URL = os.environ.get('EGERIA_PLATFORM_URL', 'https://localhost:9443')
EGERIA_VIEW_SERVER = os.environ.get('VIEW_SERVER', 'view-server')
EGERIA_VIEW_SERVER_URL = os.environ.get('EGERIA_VIEW_SERVER_URL', 'https://localhost:9443')
EGERIA_ENGINE_HOST = os.environ.get('INTEGRATION_ENGINE_HOST', 'engine-host')
EGERIA_INTEGRATION_DAEMON = os.environ.get('INTEGRATION_DAEMON', 'integration-daemon')
EGERIA_ADMIN_USER = os.environ.get('ADMIN_USER', 'garygeeke')
EGERIA_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'secret')
EGERIA_USER = os.environ.get('EGERIA_USER', 'erinoverview')
EGERIA_USER_PASSWORD = os.environ.get('EGERIA_USER_PASSWORD', 'secret')

disable_ssl_warnings = True


def display_engine_activity(server: str, url: str, user: str, user_pass:str, paging: bool):
    g_client = AutomatedCuration(server, url, user, user_pwd=user_pass)

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Engine Action Status for Platform {url} @ {time.asctime()}",
            style="bold white on black",
            row_styles=["bold white on black"],
            header_style="white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
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
        if paging is True:
            console = Console()
            with console.pager():
                console.print(generate_table())
        else:
            with Live(generate_table(), refresh_per_second=1, screen=True, vertical_overflow="visible") as live:
                while True:
                    time.sleep(2)
                    live.update(generate_table())

    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
        print_exception_response(e)
    except KeyboardInterrupt:
        pass
    finally:
        g_client.close_session()


def main_live():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")

    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD

    display_engine_activity(server=server, url=url, user=userid, user_pass=user_pass, paging=False)

def main_paging():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")

    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD

    display_engine_activity(server=server, url=url, user=userid, user_pass=user_pass, paging=True)

if __name__ == "__main__":
    main_live()

if __name__ == "__main_paging__":
    main_paging()