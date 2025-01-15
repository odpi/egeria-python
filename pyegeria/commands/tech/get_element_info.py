#!/usr/bin/env python3
"""
SPDX-Lic
ense-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


A simple display of elements for an Open Metadata Type in tree form.
"""
import argparse
import json
import os
import sys

from rich import print, box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from rich.prompt import Prompt
from rich.text import Text
from rich.tree import Tree

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    Client,
    ClassificationManager,
)


EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("EGERIA_VIEW_SERVER", "view-server")
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


def display_elements(
    om_type: str,
    server: str,
    url: str,
    username: str,
    user_password: str,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
):
    c = ClassificationManager(server, url, user_id=username, user_pwd=user_password)

    bearer_token = c.create_egeria_bearer_token(username, user_password)

    try:
        console = Console(
            width=width, force_terminal=not jupyter, style="bold white on black"
        )
        r = c.get_elements(om_type)
        if type(r) is not list:
            print(f"\n\n\tno elements found: {r}")
            sys.exit(1)

        tree = Tree(
            f"Elements for Open Metadata Type:{om_type}\n* There are {len(r)} elements",
            style="bold bright_white on black",
            guide_style="bold bright_blue",
        )
        t = tree.add(f"Elements for {om_type}", style="bold bright_white on black")
        for element in r:
            header = element["elementHeader"]
            el_type = header["type"]["typeName"]
            el_home = header["origin"]["homeMetadataCollectionName"]
            el_create_time = header["versions"]["createTime"]
            el_guid = header["guid"]

            el_md = (
                f"#### Element Basics\n"
                f"* **Type**: {el_type}\n"
                f"* **Home**: {el_home}\n"
                f"* **Created**: {el_create_time}\n"
                f"* **GUID**: {el_guid}\n ---\n"
            )
            for prop in element["properties"].keys():
                el_md += f"* **{prop}**: {element['properties'][prop]}\n"

            el_out = Markdown(el_md)
            p = Panel.fit(
                el_out,
                title=element["properties"]["qualifiedName"],
                style="bold white on black",
            )
            t = tree.add(p)

        print(tree)

        c.close_session()

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
        ValueError,
    ) as e:
        if type(e) is str:
            console.print_exception()
        else:
            # console.print_exception(show_locals=True)
            console.print(f"\n ===> Looks like the type {om_type} isn't known...\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")

    # parser.add_argument("--sponsor", help="Name of sponsor to search")
    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_VIEW_SERVER_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD

    try:
        om_type = Prompt.ask(
            "Enter the Open Metadata Type to find Elements for", default=None
        )
        display_elements(om_type, server, url, userid, user_pass)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
