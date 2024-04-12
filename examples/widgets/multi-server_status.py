#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple server status display
"""

import time
import argparse

from rich.box import Box

from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from rich.table import Table
from rich.live import Live
from rich import print
from rich.console import Group
from rich.panel import Panel
from rich import box, align
from rich.layout import Layout
import rich
from pyegeria.server_operations import ServerOps

disable_ssl_warnings = True

good_platform1_url = "https://127.0.0.1:9443"
good_platform2_url = "https://egeria.pdr-associates.com:9443"
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


def test_display_status(server: str = good_server_1, url: str = good_platform2_url, username: str = good_user_1):
    layout = Layout()
    print(layout)

    print(layout)
    p_client1 = ServerOps(server, "https://cray.local:9443", username)
    p_client2 = ServerOps('ecosystem-monitor', "https://cray.local:9446", username)


    def generate_table(p_client) -> Table:
        """Make a new table."""
        table = Table(
            title=f"Server Status for Platform - {time.asctime()}",
            # style = "black on grey66",
            header_style="white on dark_blue",
            caption=f"Server Status for Platform - '{url}'",
            # show_lines=True,
        )

        table.add_column("Known Server")
        table.add_column("Status")

        known_server_list = p_client.get_known_servers()
        active_server_list = p_client.get_active_server_list()
        if len(known_server_list) == 0:
            return table

        for server in known_server_list:
            if server in active_server_list:
                status = "Active"
            else:
                status = "Inactive"

            table.add_row(server,
                          "[red]Inactive" if status == "Inactive" else "[green]Active",
                          )
        # p_client.close_session()
        return table

    try:
        # panel_group = Group(
        #     rich.align.Align(Panel(, generate_table(p_client2)), box.ROUNDED))
        #
        # )
        layout.split_row(
            Layout(Panel(generate_table(p_client1), box.ROUNDED)),
            Layout(Panel(generate_table(p_client2), box.ROUNDED))
        )
        with Live(layout, refresh_per_second=4, screen=True) as live:
            while True:
                time.sleep(2)
                live.update(layout)


    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
        print_exception_response(e)
        assert e.related_http_code != "200", "Invalid parameters"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    args = parser.parse_args()

    server = args.server if args.server is not None else "active-metadata-store"
    url = args.url if args.url is not None else "https://cray.local:9443"
    userid = args.userid if args.userid is not None else 'garygeeke'

    test_display_status(server, url, userid)
