#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple display for my profile
"""

import argparse
import time

from rich import box
from rich.console import Console
from rich.table import Table

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
    RegisteredInfo
)

disable_ssl_warnings = True

good_platform1_url = "https://127.0.0.1:9443"
good_platform2_url = "https://egeria.pdr-associates.com:7443"
bad_platform1_url = "https://localhost:9443"

# good_platform1_url = "https://127.0.0.1:30080"
# good_platform2_url = "https://127.0.0.1:30081"
# bad_platform1_url = "https://localhost:9443"

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


def display_asset_types(server: str = good_server_3, url: str = good_platform1_url, username: str = good_user_2):
    r_client = RegisteredInfo(good_platform1_url, good_user_2, "secret",
                              server_name=good_server_3, )
    token = r_client.create_egeria_bearer_token(good_user_2, "secret")
    asset_types = r_client.list_asset_types()

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Asset Types for: {good_platform1_url} @ {time.asctime()}",
            # style = "black on grey66",
            header_style="white on dark_blue",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Asset Types from Server '{server}' @ Platform - {url}",
            expand=True
        )

        table.add_column("Name")
        table.add_column("Description")
        table.add_column("SuperType")
        table.add_column("Version")

        name = " "
        description = " "
        version = " "
        super_type = " "
        if len(asset_types) > 0:
            for a_type in asset_types:
                name = a_type.get("name", "none")
                description = a_type.get("description", "none")
                version = a_type.get("version", " ")
                super_type = a_type.get("superType", "none")
                table.add_row(
                    name, description, str(version), super_type
                )
        return table

    try:
        console = Console()
        with console.pager():
            console.print(generate_table())

    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
        print_exception_response(e)
        assert e.related_http_code != "200", "Invalid parameters"
    finally:
        r_client.close_session()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")

    args = parser.parse_args()

    server = args.server if args.server is not None else "view-server"
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'erinoverview'
    # guid = args.guid if args.guid is not None else None
    guid = None

    display_asset_types(server, url, userid)
