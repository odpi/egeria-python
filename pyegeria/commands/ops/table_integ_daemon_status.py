#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


A simple status display for the Integration Daemon.


"""
import os
import time
from typing import Union

import nest_asyncio
from rich import box
from rich.table import Table
from textual.widgets import DataTable

from pyegeria import EgeriaTech
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
EGERIA_INTEGRATION_DAEMON = os.environ.get("INTEGRATION_DAEMON", "integration-daemon")
EGERIA_INTEGRATION_DAEMON_URL = os.environ.get(
    "EGERIA_INTEGRATION_DAEMON_URL", "https://localhost:9443"
)
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_JUPYTER = bool(os.environ.get("EGERIA_JUPYTER", "False"))
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "200"))

disable_ssl_warnings = True


def add_row(
    table: Union[Table, DataTable],
    connector_name: str,
    connector_status: str,
    last_refresh_time: str,
    refresh_interval: str,
    targets_out,
    exception_msg,
) -> Table | DataTable:
    table.add_row(
        connector_name,
        connector_status,
        last_refresh_time,
        refresh_interval,
        targets_out,
        exception_msg,
    )
    return table


def display_integration_daemon_status(
    integ_server: str = EGERIA_INTEGRATION_DAEMON,
    integ_url: str = EGERIA_INTEGRATION_DAEMON_URL,
    view_server: str = EGERIA_VIEW_SERVER,
    view_url: str = EGERIA_VIEW_SERVER_URL,
    user: str = EGERIA_USER,
    user_pass: str = EGERIA_USER_PASSWORD,
    paging: bool = True,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
    sort: bool = True,
    data_table: bool = False,
) -> Table | DataTable:
    """Returns a table representing the status of connectors running on the specified Integration Daemon OMAG Server.
    This routine is meant to be used in a python script or Jupyter Notebook where the resulting table is rendered
    in either a Rich Console or a Textual Application.

    Parameters
    ----------
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
    data_table: bool, optional, default is False.
        If True, a Textual DataTable widget is returned. If false, a Rich table is returned..

    Returns
    -------

    Either a Rich Table or a Textual DataTable depending on the status of data_table
    """

    s_client = EgeriaTech(view_server, view_url, user, user_pass)
    nest_asyncio.apply()

    def generate_table() -> Table:
        """Make a new table."""

        if data_table:
            table = DataTable()
            table.add_columns(
                "Connector Name",
                "Status",
                "Last Refresh Time",
                "Min Refresh (Mins)",
                "Target Element",
                "Exception Message",
            )
        else:
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

        # Now get the integration connector report
        token = s_client.create_egeria_bearer_token()
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
            connector_status = connector.get("connectorStatus", "---")
            connector_guid = connector.get("connectorGUID", "---")
            last_refresh_time = connector.get("lastRefreshTime", "---")[:-10]
            refresh_interval = str(connector.get("minMinutesBetweenRefresh", "---"))
            exception_msg = " "
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

            add_row(
                table,
                connector_name,
                connector_status,
                last_refresh_time,
                refresh_interval,
                targets_out,
                exception_msg,
            )
        return table

    try:
        return generate_table()

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
