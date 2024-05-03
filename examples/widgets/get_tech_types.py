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
    RegisteredInfo,
    AutomatedCuration
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


def display_tech_details(search_string:str = "*", server: str = good_server_3, url: str = good_platform1_url, username: str = good_user_2):
    a_client = AutomatedCuration(server, url, username)
    token = a_client.create_egeria_bearer_token(good_user_2, "secret")
    tech_list = a_client.get_all_technology_types(search_string)

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Technology Types for: {good_platform1_url} @ {time.asctime()}",
            # style = "black on grey66",
            header_style="white on dark_blue",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Technology Types from Server '{server}' @ Platform - {url}",
            expand=True
        )

        table.add_column("Name")
        table.add_column("Qualified Name")
        table.add_column("Category")
        table.add_column("Description")
        table.add_column("Templates")
        table.add_column("Placeholders")
        table.add_column("Connector GUID")
        table.add_column("Config Properties")

        name = " "
        description = " "
        version = " "
        super_type = " "
        if len(tech_list) > 0:
            for item in tech_list:
                qualified_name = item.get("qualifiedName", " ")
                name = item.get("name", "none")
                category = item.get("category", "none")
                description = item.get("description", "none")
                details = a_client.get_technology_type_detail(name)


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
        a_client.close_session()


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
