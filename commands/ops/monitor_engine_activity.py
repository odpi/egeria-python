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
from datetime import datetime
from rich import box
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.table import Table

from pyegeria import (
    EgeriaTech,
    PyegeriaException,
    print_basic_exception,
    settings,
    config_logging
)


EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")

app_config = settings.Environment
config_logging()
console = Console(width = app_config.console_width)


def display_engine_activity_c(
    row_limit: int = 0,
    view_server: str = app_config.egeria_view_server,
    view_url: str = app_config.egeria_view_server_url,
    user: str = EGERIA_USER,
    user_pass: str = EGERIA_USER_PASSWORD,
    paging: bool = True,
    jupyter: bool = app_config.egeria_jupyter,
    width: int = app_config.console_width,
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
    g_client = EgeriaTech(view_server, view_url, user, user_pwd=user_pass)
    token = g_client.create_egeria_bearer_token()

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
        table.add_column("Core Info")
        table.add_column("Target Elements")

        table.add_column("Action Status")
        table.add_column("Completion Time")
        table.add_column("Core Results")
        # table.add_column("Completion Message")

        action_status = g_client.find_engine_actions()

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
                key=lambda i: i.get("requestedTime", datetime.now().isoformat()),
                reverse=True,
            )
            row_count = 0
            for action in sorted_action_status:
                if row_limit > 0 and row_count >= row_limit:
                    break
                row_count += 1
                requested_time = action['properties'].get("requestedStartTime", " ")[:-10]
                start_time = action['properties'].get("startTime", " ")[:-10]
                completion_time = action['properties'].get("completionTime", " ")[:-10]
                completion_guards = action['properties'].get("completionGuards", " ")

                engine_name = action['properties'].get("executorEngineName",'---')
                request_type = action['properties'].get("requestType",'---')
                action_guid = action["elementHeader"]["guid"]
                activity_status = action['properties'].get("activityStatus",'---')
                if activity_status in (
                    "REQUESTED",
                    "APPROVED",
                    "WAITING",
                    "ACTIVATING",
                ):
                    action_status = f"[yellow]{activity_status}"
                elif activity_status in ("IN_PROGRESS", "COMPLETED"):
                    action_status = f"[green]{activity_status}"
                else:
                    action_status = f"[red]{activity_status}"

                request_parameters_md = " "
                request_parameters = action['properties'].get("requestParameters", "Empty")
                if type(request_parameters) is dict:
                    for key, value in request_parameters.items():
                        request_parameters_md += f"\t* {key}: {value}\n"
                #
                # Discuss
                #
                targets = action['properties'].get("actionTargetElements", "Empty")
                if type(targets) is list:
                    targets_md = ""
                    for target in targets:
                        t_name = target["actionTargetName"]
                        t_guid = target["actionTargetGUID"]
                        t_type = target["targetElement"]["type"]["typeName"]
                        targets_md += (
                            f"* Target Name: {t_name}\n"
                            f"   * Target GUID: {t_guid}\n"
                            f"   * Target Type: {t_type}\n"
                        )

                    # target_element = json.dumps(target[0]["targetElement"]["elementProperties"]["propertiesAsStrings"])
                    target_element = Markdown(f"{targets_md} ---\n")
                else:
                    target_element = " "

                process_name = action['properties'].get("processName", "Null")
                completion_message = action['properties'].get("completionMessage", " ")
                core_results_md = (
                    f"* Completion Guards: {completion_guards}\n"
                    f"* Completion Message: {completion_message}"
                )
                core_results_out = Markdown(core_results_md)
                core_info_md = (
                    f"* Start Time: {start_time}\n* Engine Name: {engine_name}\n* GUID: {action_guid}\n"
                    f"* Request Type: {request_type}\n"
                    f"* Process Name: {process_name}\n"
                    f"---\n"
                    f"* Request Parameters: \n{request_parameters_md}\n"
                )
                core_info_out = Markdown(core_info_md)
                table.add_row(
                    requested_time,
                    core_info_out,
                    target_element,
                    action_status,
                    completion_time,
                    core_results_out,
                )
        else:
            print("Egeria integration daemon not running")
            sys.exit()
        g_client.refresh_egeria_bearer_token()
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
        PyegeriaException
    ) as e:
        print_basic_exception(e)
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

    server = args.server if args.server is not None else app_config.egeria_view_server
    url = args.url if args.url is not None else app_config.egeria_view_server_url
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    rowlimit = int(args.rowlimit) if args.rowlimit is not None else 0
    display_engine_activity_c(
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

    server = args.server if args.server is not None else app_config.egeria_view_server
    url = args.url if args.url is not None else app_config.egeria_view_server_url
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    rowlimit = int(args.rowlimit) if args.rowlimit is not None else 0

    display_engine_activity_c(
        rowlimit, server, url, user=userid, user_pass=user_pass, paging=True
    )


if __name__ == "__main__":
    main_live()

if __name__ == "__main_paging__":
    main_paging()
