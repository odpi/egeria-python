#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Display the server status of all registered servers across all platforms.

Note: This implementation is using the platform-report. A more complex platform environment may require
reimplementing from a server only perspective using get_servers_by_dep_impl_type() to find the guids and
then get_server_by_guid() to get the status. Less efficient but may be more robust for some environments.



A simple server status display
"""
import argparse
import os
import sys
import time

from rich.live import Live
from rich.table import Table

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
    RuntimeManager,
)

EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("VIEW_SERVER", "view-server")
EGERIA_VIEW_SERVER_URL = os.environ.get(
    "EGERIA_VIEW_SERVER_URL", "https://localhost:9443"
)
EGERIA_INTEGRATION_DAEMON = os.environ.get("INTEGRATION_DAEMON", "integration-daemon")
EGERIA_INTEGRATION_DAEMON_URL = os.environ.get(
    "EGERIA_INTEGRATION_DAEMON_URL", "https://localhost:9443"
)
EGERIA_ADMIN_USER = os.environ.get("ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_JUPYTER = bool(os.environ.get("EGERIA_JUPYTER", "False"))
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "200"))


def display_status(
    extended: bool,
    view_server: str,
    url: str,
    username: str,
    user_pass: str,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
):
    p_client = RuntimeManager(view_server, url, username, user_pass)
    token = p_client.create_egeria_bearer_token()

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Server Status for Platform - {time.asctime()}",
            style="bold white on black",
            row_styles=["bold white on black"],
            header_style="white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
            caption=f"Server Status from Platform - '{url}'",
            show_lines=True,
        )

        table.add_column("Known Server")
        table.add_column("Status")
        if extended:
            table.add_column("GUID", no_wrap=True)
            table.add_column("Qualified Name")
            table.add_column("Description")
            table.add_column("Server Type")
            table.add_column("Last Started")

        platform_list = p_client.get_platforms_by_type()
        if type(platform_list) is str:
            print("No OMAG Server Platforms found?")
            sys.exit(1)

        for platform in platform_list:
            platform_name = platform["properties"].get("displayName", "---")
            platform_guid = platform["elementHeader"]["guid"]
            platform_desc = platform["properties"].get("resourceDescription", "---")
            p_server_list = ""

            platform_report = p_client.get_platform_report(platform_guid)
            servers = platform_report.get("omagservers", None)
            for p_server in servers:
                server_name = p_server.get("serverName", "--- ")
                server_type = p_server.get("serverType", "--- ")
                server_desc = p_server.get("description", "--- ")
                last_start_time = p_server.get("lastStartTime", "--- ")

                server_status = p_server.get("serverActiveStatus", "UNKNOWN")
                if server_status in ("RUNNING", "STARTING"):
                    status = "Active"
                elif server_status in ("INACTIVE", "STOPPING", "UNKNOWN"):
                    status = "Inactive"
                else:
                    status = "UNKNOWN"

                if extended:
                    #
                    #  get the qualified name and guid from get_server_by_name?
                    #
                    server_info = p_client.get_servers_by_name(server_name)
                    if type(server_info) is str:
                        guid = "---"
                        qualified_name = "---"
                    else:
                        guid = ""
                        qualified_name = ""
                        for i in server_info:
                            guid += f"{i['elementHeader']['guid']} "
                            qualified_name += f"{i['properties']['qualifiedName']} "

                    table.add_row(
                        server_name,
                        "[red]Inactive" if status == "Inactive" else "[green]Active",
                        guid,
                        qualified_name,
                        server_desc,
                        server_type,
                        last_start_time,
                    )
                else:
                    table.add_row(
                        server_name,
                        "[red]Inactive" "" if status == "Inactive" else "[green]Active",
                        # server_status,
                    )
        # p_client.close_session()
        return table

    try:
        with Live(generate_table(), refresh_per_second=4, screen=True) as live:
            while True:
                time.sleep(2)
                live.update(generate_table())

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
    ) as e:
        print_exception_response(e)
    except KeyboardInterrupt:
        pass
    finally:
        p_client.close_session()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", default=True, help="Extended Information?")
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    args = parser.parse_args()

    full = args.full if args.full is not None else False
    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_ADMIN_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD

    display_status(full, server, url, userid, user_pass)


if __name__ == "__main__":
    main()
