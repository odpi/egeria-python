#!/usr/bin/env python3
"""
SPDX-Lic
ense-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple display for glossary terms
"""
import argparse
import json
import os

from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.tree import Tree

from pyegeria import (
    ServerClient,
    PyegeriaException,
    print_basic_exception,
    settings,
    config_logging
)

EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")

app_config = settings.Environment
config_logging()
console = Console(width=app_config.console_width)


def display_guid(
    guid: str,
    server: str,
    url: str,
    username: str,
    user_password: str,
    jupyter: bool = app_config.egeria_jupyter,
    width: int = app_config.console_width,
):
    c = ServerClient(server, url, user_id=username)
    bearer_token = c.create_egeria_bearer_token(username, user_password)

    try:
        console = Console(
            width=width, force_terminal=not jupyter, style="bold white on black"
        )
        r = c._get_element_by_guid_(guid)
        el = r["elementHeader"]
        p = r["properties"]

        type_name = Text(f"Type is: {el['type']['typeName']}")
        metadataCollection = Text(
            f"Metadadata Collection: {el['origin']['homeMetadataCollectionName']}"
        )
        created = Text(f"Created at: {el['versions']['createTime']}")
        details = Text(f"Details: {json.dumps(p, indent=2)}")

        tree = Tree(
            f"{guid}",
            style="bold bright_white on black",
            guide_style="bold bright_blue",
        )

        tree = tree.add(type_name)
        tree.add(metadataCollection)
        tree.add(created)
        tree.add(Panel(details, title="Element Details", expand=False))
        print(tree)

        c.close_session()

    except (
        PyegeriaException,
        ValueError,
    ) as e:
        if type(e) is str:
            console.print_exception()
        else:
            # console.print_exception(show_locals=True)
            console.print(f"\n ===> Looks like the GUID isn't known...\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")

    # parser.add_argument("--sponsor", help="Name of sponsor to search")
    args = parser.parse_args()

    server = args.server if args.server is not None else app_config.egeria_view_server
    url = args.url if args.url is not None else app_config.egeria_view_server_url
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD

    try:
        guid = Prompt.ask("Enter the GUID to retrieve", default=None)
        display_guid(guid.strip(), server, url, userid, user_pass)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
