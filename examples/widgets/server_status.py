#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple server status display
"""

import time
import argparse

from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from rich.table import Table
from rich.live import Live

from pyegeria.server_operations import ServerOps


def test_display_status(server: str, url: str , username: str ):
    p_client = ServerOps(server, url, username)

    def generate_table() -> Table:
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
        with Live(generate_table(), refresh_per_second=4, screen=True) as live:
            while True:
                time.sleep(2)
                live.update(generate_table())
                # services = p_client.get_server_status(server)['serverStatus']['services']
                # for service in services:
                #     service_name = service['serviceName']
                #     service_status = service['serviceStatus']

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
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'garygeeke'

    test_display_status(server, url, userid)
