#!/usr/bin/env python3
"""
SPDX-Lic
ense-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


List the currently loaded Governance Action Processes.
"""
import argparse
import os
import sys
import time

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
    EgeriaTech,
)
from pyegeria import ValidMetadataManager

EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("VIEW_SERVER", "view-server")
EGERIA_VIEW_SERVER_URL = os.environ.get(
    "EGERIA_VIEW_SERVER_URL", "https://localhost:9443"
)
EGERIA_INTEGRATION_DAEMON = os.environ.get("INTEGRATION_DAEMON", "integration-daemon")
EGERIA_ADMIN_USER = os.environ.get("ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_JUPYTER = bool(os.environ.get("EGERIA_JUPYTER", "False"))
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "200"))


def display_gov_processes(
    type_name: str,
    server: str,
    url: str,
    username: str,
    user_pass: str,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
) -> Table:
    p_client = EgeriaTech(server, url, user_id=username, user_pwd=user_pass)
    token = p_client.create_egeria_bearer_token(username, user_pass)

    def generate_table(type_name: str) -> Table:
        """Make a new table."""
        table = Table(
            title=f"Available Governance Action Processes  @ {time.asctime()}",
            style="bold white on black",
            row_styles=["bold white on black"],
            header_style="white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"list for Server '{server}' @ Platform - {url}",
            expand=True,
        )

        table.add_column(
            "Name",
            no_wrap=True,
        )
        table.add_column("Qualified Name")
        table.add_column(
            "GUID",
            no_wrap=True,
        )
        table.add_column("Description")

        process_list = p_client.find_gov_action_processes(type_name)

        if type(process_list) is str:
            print("No Governance Processes found matching the type name\n")
            sys.exit(1)

        for proc in process_list:
            guid = proc["elementHeader"]["guid"]
            props = proc["processProperties"]
            name = props[("displayName" "")]
            qualified_name = props["qualifiedName"]
            description = props.get("description", "---")

            table.add_row(name, qualified_name, guid, description)

        p_client.close_session()
        return table

    try:
        console = Console(width=width, force_terminal=not jupyter, record=True)
        with console.pager(styles=True):
            console.print(generate_table(type_name))

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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    parser.add_argument("--save-output", help="Save output to file?")

    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    type_name = Prompt.ask("Enter the Type Name to retrieve:", default="*")

    display_gov_processes(type_name, server, url, userid, user_pass)


if __name__ == "__main__":
    main()
