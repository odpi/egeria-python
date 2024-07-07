#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


A simple status display for the Integration Daemon.

Note that there are a couple of assumptions currently being made that need to get resolved in future
versions. First, we assume that the view-server used by AutomatedCuration is called "view-server". Second, we
assume that the user password is always "secret".

"""

import argparse
import time

from rich import box
from rich.live import Live
from rich.markdown import Markdown
from rich.table import Table

from pyegeria import ServerOps, AutomatedCuration
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)

disable_ssl_warnings = True


def display_integration_daemon_status(server: str, url: str, user: str):
    s_client = ServerOps(server, url, user)
    a_client = AutomatedCuration("view-server", url, user, "secret")
    token = a_client.create_egeria_bearer_token()

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
            connector_name = connector.get("connectorName", "---")
            connector_status = connector.get("connectorStatus", "---")
            connector_guid = connector["connectorGUID"]
            last_refresh_time = connector.get("lastRefreshTime", "---")
            refresh_interval = str(connector.get("minMinutesBetweenRefresh", "---"))
            exception_msg = " "

            targets = a_client.get_catalog_targets(connector_guid)
            if type(targets) == list:
                targets_m = "\n"
                for target in targets:
                    t_name = target["catalogTargetName"]
                    t_sync = target["permittedSynchronization"]
                    t_unique_name = target["catalogTargetElement"]["uniqueName"]
                    targets_m += f"* Target Name: __{t_name}__\n* Sync: {t_sync}\n* Unique Name: {t_unique_name}\n\n"
                targets_md = Markdown(targets_m)
            else:
                targets_md = " "

            if connector_status in ("RUNNING", "REFRESHING", "WAITING"):
                connector_status = f"[green]{connector_status}"
            elif connector_status in ("INITIALIZE FAILED", "CONFIG_FAILED", "FAILED"):
                connector_status = f"[red]{connector_status}"
            else:
                connector_status = f"[yellow]{connector_status}"

            table.add_row(
                connector_name, connector_status, last_refresh_time, refresh_interval,
                targets_md, exception_msg
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
    parser.add_argument("--server", help="Name of the integration server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    args = parser.parse_args()

    server = args.server if args.server is not None else "integration-daemon"
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'garygeeke'
    display_integration_daemon_status(server=server, url=url, user=userid)
