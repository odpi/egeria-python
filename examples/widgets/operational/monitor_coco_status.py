#!/usr/bin/python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple server status display for the Coco Pharmaceuticals Configuration
"""

import argparse
import time

from rich import box
from rich import print
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria.server_operations import ServerOps

disable_ssl_warnings = True


def display_status(server: str, url: str, username: str):
    layout = Layout()

    p_client1 = ServerOps("Core Catalog", "https://localhost:9443", username)
    p_client2 = ServerOps('Datalake Catalog', "https://localhost:9444", username)
    p_client3 = ServerOps('DevCatalog', "https://localhost:9445", username)

    def generate_table(p_client) -> Table:
        """Make a new table."""
        table = Table(
            title=f"Server Status for {p_client.server_name}- {time.asctime()}",
            # style = "black on grey66",
            header_style="white on dark_blue",
            caption=f"Server Status for Platform - '{p_client.platform_url}'",
            # show_lines=True,
        )

        table.add_column("Known Server")
        table.add_column("Status")
        known_server_list = p_client.get_known_servers()
        active_server_list = p_client.get_active_server_list()
        if type(known_server_list) is str:
            return table

        for server in known_server_list:
            if server in active_server_list:
                status = "Active"
            else:
                status = "Inactive"

            table.add_row(server,
                          "[red]Inactive" if status == "Inactive" else "[green]Active",
                          )
        return table

    try:
        layout.split_row(
            Layout(Panel(generate_table(p_client1), box.ROUNDED)),
            Layout(Panel(generate_table(p_client2), box.ROUNDED)),
            Layout(Panel(generate_table(p_client3), box.ROUNDED))
        )
        with Live(layout, refresh_per_second=4, screen=True) as live:
            while True:
                time.sleep(2)
                live.update(layout)

    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
        print_exception_response(e)
    except KeyboardInterrupt:
        pass

    finally:
        p_client1.close_session()
        p_client2.close_session()
        p_client3.close_session()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    args = parser.parse_args()

    server = args.server if args.server is not None else "active-metadata-store"
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'garygeeke'

    display_status(server, url, userid)

if __name__ == "__main__":
    main()