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

from rich import box, print
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from pyegeria import (
    EgeriaTech,
    PyegeriaException,
    ValidMetadataManager,
    print_basic_exception,
    settings,
    config_logging
)
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")

app_config = settings.Environment
config_logging()
console = Console(width = app_config.console_width)


def display_gov_processes(
    type_name: str,
    server: str,
    url: str,
    username: str,
    user_pass: str,
    jupyter: bool = app_config.egeria_jupyter,
    width: int = app_config.console_width,
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

        process_list = p_client.find_governance_definitions(search_string = type_name, metadata_element_subtypes=["GovernanceActionProcess"])

        if type(process_list) is str:
            print("No Governance Processes found matching the type name\n")
            sys.exit(1)

        for proc in process_list:
            guid = proc["elementHeader"]["guid"]
            props = proc["properties"]
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
        PyegeriaException,
        ValueError,
    ) as e:
        if type(e) is str:
            print(e)
        else:
            print_basic_exception(e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    parser.add_argument("--save-output", help="Save output to file?")

    args = parser.parse_args()

    server = args.server if args.server is not None else app_config.egeria_view_server
    url = args.url if args.url is not None else app_config.egeria_view_server_url
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    type_name = Prompt.ask("Enter the Type Name to retrieve:", default="*")

    display_gov_processes(type_name, server, url, userid, user_pass)


if __name__ == "__main__":
    main()
