#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple server status display
"""
import argparse
import os
import time

from rich.live import Live
from rich.table import Table

from pyegeria._exceptions import (InvalidParameterException, PropertyServerException, UserNotAuthorizedException,
                                  print_exception_response, )
from pyegeria.core_omag_server_config import CoreServerConfig
from pyegeria.server_operations import ServerOps

disable_ssl_warnings = True

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


def display_status(server: str, url: str, username: str, user_pass: str, jupyter: bool = EGERIA_JUPYTER,
                   width: int = EGERIA_WIDTH):
    p_client = ServerOps(server, url, username)
    c_client = CoreServerConfig(server, url, username, user_pass)

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(title=f"Server Status for Platform - {time.asctime()}", style="bold white on black",
                      row_styles=["bold white on black"], header_style="white on dark_blue",
                      title_style="bold white on black",
                      caption_style="white on black", caption=f"Server Status for Platform - '{url}'", show_lines=True,
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

            table.add_row(server, "[red]Inactive" if status == "Inactive" else "[green]Active", server_type,
                          description)

        return table

    try:
        with Live(generate_table(), refresh_per_second=4, screen=True) as live:
            while True:
                time.sleep(2)
                live.update(generate_table())

    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
        print_exception_response(e)
    except KeyboardInterrupt:
        pass

    finally:
        p_client.close_session()
        c_client.close_session()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_METADATA_STORE
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_ADMIN_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD

    display_status(server, url, userid, user_pass)


if __name__ == "__main__":
    main()
