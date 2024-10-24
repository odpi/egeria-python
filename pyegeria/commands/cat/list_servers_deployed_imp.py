#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Display by deployed implementation type.

Note: This implementation is using the runtime manager.



A simple server status display
"""
import argparse
import os
import sys
import time

from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

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


def display_servers_by_dep_imp(
    filter: str = "*",
    view_server: str = EGERIA_VIEW_SERVER,
    view_url: str = EGERIA_VIEW_SERVER_URL,
    user: str = EGERIA_USER,
    user_pass: str = EGERIA_USER_PASSWORD,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
):
    p_client = RuntimeManager(view_server, view_url, user, user_pass)
    token = p_client.create_egeria_bearer_token()

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Servers by Deployed Implementation Type - {time.asctime()}",
            style="bold white on black",
            row_styles=["bold white on black"],
            header_style="white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
            caption=f"Platform - '{view_url}'",
            show_lines=True,
        )

        table.add_column("Server")
        table.add_column("Deployed Impl Type")
        table.add_column("Zones")

        table.add_column("Description")
        table.add_column("Qualified Name & GUID", no_wrap=True)

        unsorted_server_list = p_client.get_servers_by_dep_impl_type(filter)
        if type(unsorted_server_list) is str:
            print("No matching Software Servers found?")
            sys.exit(1)
        server_list = sorted(
            unsorted_server_list,
            key=lambda x: x["properties"].get("displayName", "---").lower(),
        )

        for server in server_list:
            display_name = server["properties"].get("displayName", "---")
            qualified_name = server["properties"].get("qualifiedName", "---")
            classifications = server["elementHeader"].get("classifications", None)
            zones = ""
            if classifications:
                for clas in classifications:
                    if clas["classificationName"] == "AssetZoneMembership":
                        classification_props = clas["classificationProperties"]
                        zone_membership = classification_props.get(
                            "zoneMembership", None
                        )
                        if zone_membership:
                            for z in zone_membership.keys():
                                zones += f"{zone_membership[z]}, "
                            zones = zones[:-2]

            impl_type = server["properties"].get("deployedImplementationType", "---")
            server_guid = server["elementHeader"]["guid"]
            server_desc = server["properties"].get("resourceDescription", "---")

            server_id = Text(f"{qualified_name}\n&\n{server_guid}", justify="center")

            table.add_row(display_name, impl_type, zones, server_desc, server_id)

        return table

    try:
        console = Console(width=width, force_terminal=not jupyter)

        with console.pager(styles=True):
            console.print(generate_table())

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

    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_ADMIN_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    filter = Prompt.ask(
        "Filter deployed for deployed implementation type by search string", default="*"
    )
    display_servers_by_dep_imp(filter, server, url, userid, user_pass)


if __name__ == "__main__":
    main()
