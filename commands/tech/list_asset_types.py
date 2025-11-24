#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple display for my profile
"""
import argparse
import os
import time

from rich import box
from rich.console import Console
from rich.table import Table

from pyegeria import (
    RegisteredInfo,
    print_basic_exception,
    PyegeriaException,
    settings, load_app_config, pretty_print_config,
    config_logging,
    save_mermaid_html,
)

app_config = settings.Environment
config_path = os.path.join(app_config.pyegeria_config_directory, app_config.pyegeria_config_file)

EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_MERMAID_FOLDER = os.path.join(app_config.pyegeria_root, app_config.egeria_mermaid_folder)
conf = load_app_config(config_path)
# print(f"Loading config from {config_path} and mermaid folder is {EGERIA_MERMAID_FOLDER}")
console = Console(width=app_config.console_width)
config_logging()


def display_asset_types(
    server: str,
    url: str,
    username: str,
    user_password: str,
    jupyter: bool = app_config.egeria_jupyter,
    width: int = app_config.console_width,
):
    r_client = RegisteredInfo(server, url, username)
    token = r_client.create_egeria_bearer_token(username, user_password)
    asset_types = r_client.list_asset_types()

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Asset Types for: {url} @ {time.asctime()}",
            style="bold bright_white on black",
            row_styles=["bold bright_white on black"],
            header_style="white on dark_blue",
            title_style="bold white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Asset Types from Server '{server}' @ Platform - {url}",
            expand=True,
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
                table.add_row(name, description, super_type, str(version))
        return table

    try:
        console = Console(width=width, force_terminal=not jupyter)
        with console.pager(styles=True):
            console.print(generate_table())

    except (
        PyegeriaException
    ) as e:
        print_basic_exception(e)
        assert e.related_http_code != "200", "Invalid parameters"
    finally:
        r_client.close_session()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")

    args = parser.parse_args()

    server = args.server if args.server is not None else app_config.egeria_view_server
    url = args.url if args.url is not None else app_config.egeria_platform_url
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    # guid = args.guid if args.guid is not None else None
    guid = None

    display_asset_types(server, url, userid, user_pass)


if __name__ == "__main__":
    main()
