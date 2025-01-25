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
from rich.prompt import Prompt
from rich.table import Table
import nest_asyncio
from typing import Union
from textual.widgets import DataTable

from pyegeria import EgeriaTech, AutomatedCuration
from pyegeria._exceptions import (
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
EGERIA_INTEGRATION_DAEMON = os.environ.get("EGERIA_INTEGRATION_DAEMON", "integration-daemon")
EGERIA_INTEGRATION_DAEMON_URL = os.environ.get(
    "EGERIA_INTEGRATION_DAEMON_URL", "https://localhost:9443"
)
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_JUPYTER = bool(os.environ.get("EGERIA_JUPYTER", "False"))
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "200"))

disable_ssl_warnings = True


def display_integration_daemon_status(
    search_list: list[str] = ["*"],
    integ_server: str = os.environ.get("EGERIA_INTEGRATION_DAEMON", "integration-daemon"),
    integ_url: str = os.environ.get("EGERIA_INTEGRATION_DAEMON_URL", "https://localhost:9443"),
    view_server: str = os.environ.get("EGERIA_VIEW_SERVER", "view-server"),
    view_url: str = os.environ.get('EGERIA_VIEW_SERVER_URL', "https://localhost:9443"),
    user: str = os.environ.get("EGERIA_USER"),
    user_pass: str = os.environ.get("EGERIA_USER_PASSWORD"),
    paging: bool = False,
    jupyter: bool = os.environ.get("EGERIA_JUPYTER", "False"),
    width: int = os.environ.get("EGERIA_WIDTH","150"),
    sort: bool = True,
) -> None:
    """Display the status of connectors running on the specified Integration Daemon OMAG Server.

    Parameters
    ----------
    search_list : list[str], optional
        A list of connector names to search for. Default is ["*"], which returns all connectors.

    integ_server : str, optional
        The name of the integration daemon server. Default is EGERIA_INTEGRATION_DAEMON.

    integ_url : str, optional
        The URL of the integration daemon server. Default is EGERIA_INTEGRATION_DAEMON_URL.

    view_server : str, optional
        The name of the view server. Default is EGERIA_VIEW_SERVER.

    view_url : str, optional
        The URL of the view server. Default is EGERIA_VIEW_SERVER_URL.

    user : str, optional
        The username for authentication. Default is EGERIA_USER.

    user_pass : str, optional
        The password for authenticated access. Default is EGERIA_USER_PASSWORD.

    paging : bool, optional
        Determines whether to use paging or a live monitor for console output. Default is True.

    jupyter : bool, optional
        Determines whether running in a Jupyter environment. Default is EGERIA_JUPYTER.

    width : int, optional
        The width of the console display. Default is EGERIA_WIDTH.

    sort : bool, optional
        Determines whether to sort the connector reports. Default is True.

    Returns
    -------

    Nothing
    """
    s_client = EgeriaTech(view_server, view_url, user, user_pass)
    token = s_client.create_egeria_bearer_token()

    def generate_table(search_list: list[str]) -> Table:
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
            expand=True,
        )
        table.add_column("Connector Name", min_width=15)
        table.add_column("Status", max_width=6)

        table.add_column("Last Refresh Time", min_width=12)
        table.add_column("Min Refresh (mins)", max_width=6)
        table.add_column("Target Element", min_width=20)
        table.add_column("Exception Message", min_width=10)

        # server_guid = s_client.get_guid_for_name(integ_server)
        daemon_status = s_client.get_server_report(None, integ_server)

        reports = daemon_status["integrationConnectorReports"]
        if sort is True:
            connector_reports = sorted(
                reports, key=lambda x: x.get("connectorName", "---")
            )
        else:
            connector_reports = reports

        for connector in connector_reports:
            connector_name = connector.get("connectorName", "---")

            if (connector_name not in search_list) and (search_list != ["*"]):
                # if specific connectors are requested and it doesn't match, then skip
                continue

            connector_status = connector.get("connectorStatus", "---")
            connector_guid = connector.get("connectorGUID", "---")
            last_refresh_time = connector.get("lastRefreshTime", "---")[:-10]
            refresh_interval = str(connector.get("minMinutesBetweenRefresh", "---"))
            exception_msg = connector.get("failingExceptionMessage", " ")
            if connector_guid != "---":
                targets = s_client.get_catalog_targets(connector_guid)
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
                connector_name,
                connector_status,
                last_refresh_time,
                refresh_interval,
                targets_out,
                exception_msg,
            )

        return table

    try:
        if paging is True:
            console = Console(width=width)  # main_pagig, force_terminal=not jupyter)
            with console.pager():
                console.print(generate_table(search_list))
        else:
            with Live(
                generate_table(search_list),
                refresh_per_second=1,
                screen=True,
                vertical_overflow="visible",
            ) as live:
                while True:
                    time.sleep(2)
                    live.update(generate_table(search_list))

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
    ) as e:
        print_exception_response(e)

    except KeyboardInterrupt:
        pass

    finally:
        s_client.close_session()


def main_live(paging: bool = False) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--integ_server", help="Name of the integration server to display status for"
    )
    parser.add_argument("--integ_url", help="URL Platform to connect to")
    parser.add_argument("--view_server", help="Name of the view server to use")
    parser.add_argument("--view_url", help="view server URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")

    args = parser.parse_args()

    integ_server = (
        args.integ_server
        if args.integ_server is not None
        else EGERIA_INTEGRATION_DAEMON
    )
    integ_url = (
        args.integ_url if args.integ_url is not None else EGERIA_INTEGRATION_DAEMON_URL
    )
    view_server = (
        args.view_server if args.view_server is not None else EGERIA_VIEW_SERVER
    )
    view_url = args.view_url if args.view_url is not None else EGERIA_VIEW_SERVER_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD

    search_list = Prompt.ask(
        "Enter the list of connectors you are interested in or '*' for all",
        default="*",
    )
    display_integration_daemon_status(
        search_list=[search_list],
        integ_server=integ_server,
        integ_url=integ_url,
        view_server=view_server,
        view_url=view_url,
        user=userid,
        user_pass=user_pass,
        paging=paging,
    )


def main_paging(paging: bool = True) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--integ_server", help="Name of the integration server to display status for"
    )
    parser.add_argument("--integ_url", help="URL Platform to connect to")
    parser.add_argument("--view_server", help="Name of the view server to use")
    parser.add_argument("--view_url", help="view server URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")

    args = parser.parse_args()

    integ_server = (
        args.integ_server
        if args.integ_server is not None
        else EGERIA_INTEGRATION_DAEMON
    )
    integ_url = (
        args.integ_url if args.integ_url is not None else EGERIA_INTEGRATION_DAEMON_URL
    )
    view_server = (
        args.view_server if args.view_server is not None else EGERIA_VIEW_SERVER
    )
    view_url = args.view_url if args.view_url is not None else EGERIA_VIEW_SERVER_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    search_list = Prompt.ask(
        "Enter the list of connectors you are interested in or '*' for all",
        default="*",
    )
    display_integration_daemon_status(
        search_list=[search_list],
        integ_server=integ_server,
        integ_url=integ_url,
        view_server=view_server,
        view_url=view_url,
        user=userid,
        user_pass=user_pass,
        paging=paging,
    )


if __name__ == "__main__":
    main_live(paging=False)

if __name__ == "__main_paging__":
    main_paging(paging=True)
