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

from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria.server_operations import ServerOps

disable_ssl_warnings = True

good_platform1_url = "https://127.0.0.1:9443"
good_platform2_url = "https://egeria.pdr-associates.com:7443"
bad_platform1_url = "https://localhost:9443"

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


def display_integration_daemon_status(server: str = good_server_4, url: str = good_platform1_url,
                                      user: str = good_user_1):
    s_client = ServerOps(server, url, user)

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Integration Daemon Status @ {time.asctime()}",
            # style = "black on grey66",
            header_style="white on dark_blue",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Integration Daemon Status for Server '{server}' @ Platform - {url}",
            expand=True
        )
        table.add_column("Connector Name")
        table.add_column("Connector Status")

        table.add_column("Last Refresh Time")
        table.add_column("Minimum Refresh Interval (min)")
        table.add_column("Target Element")
        table.add_column("Exception Message")

        daemon_status = s_client.get_integration_daemon_status()
        connector_reports = daemon_status["integrationConnectorReports"]
        for connector in connector_reports:
            connector_name = connector["connectorName"]
            connector_status = connector["connectorStatus"]
            last_refresh_time = connector.get("lastRefreshTime","---")
            refresh_interval = str(connector.get("minMinutesBetweenRefresh","---"))
            target_element = " "
            exception_msg = " "

            if connector_name is None:
                connector_name = "connector name"
            if connector_status is None:
                connector_status = "connector status"

            if connector_status in ("RUNNING", "REFRESHING", "WAITING"):
                connector_status = f"[green]{connector_status}"
            elif connector_status in ("INITIALIZE FAILED","CONFIG_FAILED","FAILED"):
                connector_status = f"[red]{connector_status}"
            else:
                connector_status = f"[yellow]{connector_status}"

            # target= action.get("actionTargetElements","Empty")
            # if type(target) is list:
            #     target_element = json.dumps(target[0]["targetElement"]["elementProperties"]["propertiesAsStrings"])
            # else:
            #     target_element = " "

            table.add_row(
                connector_name,connector_status,last_refresh_time,refresh_interval,
                target_element, exception_msg
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
        assert e.related_http_code != "200", "Invalid parameters"

    finally:
        s_client.close_session()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    args = parser.parse_args()

    server = args.server if args.server is not None else "integration-daemon"
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'garygeeke'
    display_integration_daemon_status(server=server, url=url, user=userid)
