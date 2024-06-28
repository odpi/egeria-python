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
from pyegeria.core_omag_server_config import CoreServerConfig

disable_ssl_warnings = True

def display_status(server: str, url: str, username: str):
    p_client = ServerOps(server, url, username)
    c_client = CoreServerConfig(server, url, username)

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Server Status for Platform - {time.asctime()}",
            # style = "black on grey66",
            header_style="white on dark_blue",
            caption=f"Server Status for Platform - '{url}'",
            show_lines=True,
            # expand=True
        )

        table.add_column("Known Server")
        table.add_column("Status")
        table.add_column("Server Type")
        table.add_column("Server Description")
        known_server_list = p_client.get_known_servers()
        active_server_list = p_client.get_active_server_list()
        if len(known_server_list) == 0:
            return table

        for server in known_server_list:
            if server in active_server_list:
                status = "Active"
            else:
                status = "Inactive"
            server_type = c_client.get_server_type_classification(server)["serverTypeName"]
            description = c_client.get_basic_server_properties(server).get("localServerDescription", " ")

            table.add_row(server,
                          "[red]Inactive" if status == "Inactive" else "[green]Active",
                          server_type, description)

        return table

    try:
        with Live(generate_table(), refresh_per_second=4, screen=True) as live:
            while True:
                time.sleep(2)
                live.update(generate_table())

    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
        print_exception_response(e)
        assert e.related_http_code != "200", "Invalid parameters"

    finally:
        p_client.close_session()
        c_client.close_session()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    args = parser.parse_args()

    server = args.server if args.server is not None else "active-metadata-store"
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'garygeeke'

    display_status(server, url, userid)
