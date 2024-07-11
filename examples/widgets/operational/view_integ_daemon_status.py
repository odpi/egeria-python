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
from rich.table import Table

from pyegeria import ServerOps, AutomatedCuration
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)

disable_ssl_warnings = True


def display_integration_daemon_status(integ_server: str, integ_url: str,
                                      view_server:str, view_url: str, user: str):
    s_client = ServerOps(integ_server, integ_url, user)
    a_client = AutomatedCuration(view_server, view_url, user, "secret")
    token = a_client.create_egeria_bearer_token()

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Integration Daemon Status @ {time.asctime()}",
            # style = "black on grey66",
            header_style="white on dark_blue",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Integration Daemon Status for Server '{integ_server}' @ Platform - {integ_url}",
            expand=True
        )
        table.add_column("Connector Name")
        table.add_column("Connector Status")

        table.add_column("Last Refresh Time")
        table.add_column("Min Refresh (min)")
        table.add_column("Target Element")
        table.add_column("Exception Message")

        daemon_status = s_client.get_integration_daemon_status()
        connector_reports = daemon_status["integrationConnectorReports"]
        for connector in connector_reports:
            connector_name = connector.get("connectorName", "---")
            connector_status = connector.get("connectorStatus", "---")
            connector_guid = connector.get("connectorGUID","---")
            last_refresh_time = connector.get("lastRefreshTime", "---")
            refresh_interval = str(connector.get("minMinutesBetweenRefresh", "---"))
            exception_msg = " "
            if connector_guid != '---':
                targets = a_client.get_catalog_targets(connector_guid)
                tgt_tab = Table()
                tgt_tab.add_column("Target")
                tgt_tab.add_column("UniqueName")
                tgt_tab.add_column("Relationship GUID", no_wrap=True)

                if type(targets) == list:
                    targets_md = True
                    for target in targets:
                        t_name = target["catalogTargetName"]
                        # t_sync = target["permittedSynchronization"]
                        t_unique_name = target["catalogTargetElement"]["uniqueName"]
                        t_rel_guid = target["relationshipGUID"]
                        # targets_m += f"* Target Name: __{t_name}__\n* Sync: {t_sync}\n* Unique Name: {t_unique_name}\n\n"
                        tgt_tab.add_row(t_name,t_unique_name, t_rel_guid)
                    # targets_md = Markdown(targets_m)
                else:
                    targets_md = False
            else:
                targets_md = False
            if targets_md is False:
                targets_out = ""
            else:
                targets_out = tgt_tab

            if connector_status in ("RUNNING", "REFRESHING", "WAITING"):
                connector_status = f"[green]{connector_status}"
            elif connector_status in ("INITIALIZE FAILED", "CONFIG_FAILED", "FAILED"):
                connector_status = f"[red]{connector_status}"
            else:
                connector_status = f"[yellow]{connector_status}"

            table.add_row(
                connector_name, connector_status, last_refresh_time, refresh_interval,
                targets_out, exception_msg
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
        a_client.close_session()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--integ_server", help="Name of the integration server to display status for")
    parser.add_argument("--integ_url", help="URL Platform to connect to")
    parser.add_argument("--view_server", help="Name of the integration server to display status for")
    parser.add_argument("--view_url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    args = parser.parse_args()

    integ_server = args.integ_server if args.integ_server is not None else "integration-daemon"
    integ_url = args.integ_url if args.integ_url is not None else "https://localhost:9443"
    view_server = args.view_server if args.view_server is not None else "view-server"
    view_url = args.view_url if args.view_url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'garygeeke'
    display_integration_daemon_status(integ_server=integ_server, integ_url=integ_url,
                                      view_server = view_server, view_url = view_url,
                                      user=userid)

if __name__ == "__main__":
    main()