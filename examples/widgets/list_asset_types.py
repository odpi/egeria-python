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


def display_asset_types(server: str, url: str, username: str):
    r_client = RegisteredInfo(server, url, username)
    token = r_client.create_egeria_bearer_token(username, "secret")
    asset_types = r_client.list_asset_types()

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Asset Types for: {url} @ {time.asctime()}",
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
                    name, description, super_type, str(version)
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
