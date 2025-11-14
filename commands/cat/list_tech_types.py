#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple display for my profile
"""
import argparse
import os
import sys
import time

from rich import box
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from pyegeria import (
    AutomatedCuration,
    settings,
    PyegeriaException,
    print_basic_exception
)


EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
app_config = settings.Environment
# config_logging()


disable_ssl_warnings = True


def display_tech_types(
    search_string: str,
    server: str,
    url: str,
    username: str,
    user_pass: str,
    jupyter: bool = app_config.egeria_jupyter,
        width: int = app_config.console_width,
):
    a_client = AutomatedCuration(server, url, username)
    token = a_client.create_egeria_bearer_token(username, user_pass)
    tech_list = a_client.find_technology_types(search_string, page_size=0)

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Technology Types for: {url} @ {time.asctime()}",
            style="bold white on black",
            row_styles=["bold white on black"],
            header_style="white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Technology Types from Server '{server}' @ Platform - {url}",
            expand=True,
        )

        table.add_column("Name")
        table.add_column("Qualified Name")
        table.add_column("Category")
        table.add_column("Description")

        name = " "
        description = " "
        version = " "
        super_type = " "
        if type(tech_list) is list:
            for item in tech_list:
                if "deployedImplementationType" not in item["qualifiedName"]:
                    continue
                qualified_name = item.get("qualifiedName", " ")
                name = item.get("displayName", "none")
                category = item.get("category", "none")
                description = item.get("description", "none")

                table.add_row(name, qualified_name, category, description)
            return table
        else:
            print("Unknown technology type")
            sys.exit(1)

    try:
        console = Console(width=width, force_terminal=not jupyter)
        with console.pager(styles=True):
            console.print(generate_table())

    except (
        PyegeriaException,
    ) as e:
        print_basic_exception(e)
        assert e.related_http_code != "200", "Invalid parameters"
    finally:
        a_client.close_session()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")

    args = parser.parse_args()

    server = args.server if args.server is not None else app_config.egeria_view_server
    url = args.url if args.url is not None else app_config.egeria_view_server_url
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD

    try:
        search_string = Prompt.ask(
            "Enter the technology you are searching for:", default="*"
        )
        display_tech_types(search_string, server, url, userid, user_pass)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
