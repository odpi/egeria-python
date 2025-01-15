#!/usr/bin/env python3
"""
SPDX-Lic
ense-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple display for archives
"""
import argparse
import json
import os
import time, datetime

from rich import box
from rich import print
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria import ProjectManager, ClassificationManager

EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("EGERIA_VIEW_SERVER", "view-server")
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


def display_archive_list(
    server: str,
    url: str,
    username: str,
    user_pass: str,
    save_output: bool,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
) -> object:
    c_client = ClassificationManager(server, url, user_id=username)
    token = c_client.create_egeria_bearer_token(username, user_pass)

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Archive List  @ {time.asctime()}",
            header_style="white on dark_blue",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Archive list for Server '{server}' @ Platform - {url}",
            expand=True,
        )

        table.add_column("Name")
        table.add_column("Description")
        table.add_column("Path Name")

        # table.add_column("Creator")
        # table.add_column("Description")

        open_metadata_type_name = None
        property_value = "omarchive"
        property_names = ["fileExtension"]
        archives = c_client.get_elements_by_property_value(
            property_value, property_names, open_metadata_type_name
        )

        if type(archives) != list:
            raise ValueError("--> No archives found")
        else:
            sorted_archives = sorted(
                archives, key=lambda k: k["properties"].get("name", "---")
            )

            for archive in sorted_archives:
                name = archive["properties"].get("name", "---")
                path_name = archive["properties"].get("pathName", "---")
                description = archive["properties"].get("description", "---")
                creation_date_epoch = (
                    int(archive["properties"].get("storeCreateTime", 0)) / 1000
                )
                create_date = datetime.datetime.fromtimestamp(creation_date_epoch)
                creator = "---"

                table.add_row(name, description, path_name)

        return table

    try:
        # with Live(generate_table(), refresh_per_second=4, screen=True) as live:
        #     while True:
        #         time.sleep(2)
        #         live.update(generate_table())
        console = Console(
            record=True, width=width, force_terminal=not jupyter, soft_wrap=True
        )
        with console.pager():
            console.print(generate_table(), soft_wrap=True)
        if save_output:
            console.save_html("archives.html")

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
        ValueError,
    ) as e:
        if type(e) is str:
            print(e)
        else:
            print_exception_response(e)
    except KeyboardInterrupt:
        pass
    finally:
        c_client.close_session()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--save-output", help="Save output to file?")
    parser.add_argument("--password", help="User Password")
    # parser.add_argument("--sponsor", help="Name of sponsor to search")
    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD

    try:
        save_output = args.save_output if args.save_output is not None else False
        display_archive_list(server, url, userid, user_pass, save_output)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
