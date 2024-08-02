#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


A simple status display for the Integration Daemon.


"""
import argparse
import os
import time

from rich import box
from rich.console import Console
from rich.live import Live
from rich.table import Table

from pyegeria import ServerOps, AutomatedCuration
from pyegeria._exceptions import (
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
EGERIA_INTEGRATION_DAEMON = os.environ.get('INTEGRATION_DAEMON', 'integration-daemon')
EGERIA_INTEGRATION_DAEMON_URL = os.environ.get('EGERIA_INTEGRATION_DAEMON_URL', 'https://localhost:9443')
EGERIA_ADMIN_USER = os.environ.get('ADMIN_USER', 'garygeeke')
EGERIA_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'secret')
EGERIA_USER = os.environ.get('EGERIA_USER', 'erinoverview')
EGERIA_USER_PASSWORD = os.environ.get('EGERIA_USER_PASSWORD', 'secret')
EGERIA_JUPYTER = bool(os.environ.get('EGERIA_JUPYTER', 'False'))
EGERIA_WIDTH = int(os.environ.get('EGERIA_WIDTH', '200'))

disable_ssl_warnings = True


def display_integration_daemon_status(integ_server: str, integ_url: str,
                                      view_server: str, view_url: str, user: str, user_pass: str, paging: bool,
                                      jupyter: bool = EGERIA_JUPYTER, width: int = EGERIA_WIDTH
                                      ):
    s_client = ServerOps(integ_server, integ_url, user)
    a_client = AutomatedCuration(view_server, view_url, user, user_pass)
    token = a_client.create_egeria_bearer_token()

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Integration Daemon Status @ {time.asctime()}",
            style="bold white on black",
            row_styles=["bold white on black"],
            header_style="white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Integration Daemon Status for Server '{integ_server}' @ Platform - {integ_url}",
            expand=True
        )
        table.add_column("Connector Name", min_width=15)
        table.add_column("Status", max_width=6)

        table.add_column("Last Refresh Time", min_width=12)
        table.add_column("Min Refresh (mins)", max_width=6)
        table.add_column("Target Element", min_width=20)
        table.add_column("Exception Message", min_width=10)

        daemon_status = s_client.get_integration_daemon_status()
        connector_reports = daemon_status["integrationConnectorReports"]
        for connector in connector_reports:
            connector_name = connector.get("connectorName", "---")
            connector_status = connector.get("connectorStatus", "---")
            connector_guid = connector.get("connectorGUID", "---")
            last_refresh_time = connector.get("lastRefreshTime", "---")[:-10]
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
                        tgt_tab.add_row(t_name, t_unique_name, t_rel_guid)
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
        if paging is True:
            console = Console(width=width, force_terminal=not jupyter)
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
        s_client.close_session()
        a_client.close_session()


def main_live():
    parser = argparse.ArgumentParser()
    parser.add_argument("--integ_server", help="Name of the integration server to display status for")
    parser.add_argument("--integ_url", help="URL Platform to connect to")
    parser.add_argument("--view_server", help="Name of the view server to use")
    parser.add_argument("--view_url", help="view server URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    args = parser.parse_args()

    integ_server = args.integ_server if args.integ_server is not None else EGERIA_INTEGRATION_DAEMON
    integ_url = args.integ_url if args.integ_url is not None else EGERIA_INTEGRATION_DAEMON_URL
    view_server = args.view_server if args.view_server is not None else EGERIA_VIEW_SERVER
    view_url = args.view_url if args.view_url is not None else EGERIA_VIEW_SERVER_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    display_integration_daemon_status(integ_server=integ_server, integ_url=integ_url,
                                      view_server=view_server, view_url=view_url,
                                      user=userid, user_pass=user_pass, paging=False)


def main_paging():
    parser = argparse.ArgumentParser()
    parser.add_argument("--integ_server", help="Name of the integration server to display status for")
    parser.add_argument("--integ_url", help="URL Platform to connect to")
    parser.add_argument("--view_server", help="Name of the view server to use")
    parser.add_argument("--view_url", help="view server URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    args = parser.parse_args()

    integ_server = args.integ_server if args.integ_server is not None else EGERIA_INTEGRATION_DAEMON
    integ_url = args.integ_url if args.integ_url is not None else EGERIA_INTEGRATION_DAEMON_URL
    view_server = args.view_server if args.view_server is not None else EGERIA_VIEW_SERVER
    view_url = args.view_url if args.view_url is not None else EGERIA_VIEW_SERVER_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    display_integration_daemon_status(integ_server=integ_server, integ_url=integ_url,
                                      view_server=view_server, view_url=view_url,
                                      user=userid, user_pass=user_pass, paging=True)


if __name__ == "__main__":
    main_live()

if __name__ == "__main_paging__":
    main_paging()
