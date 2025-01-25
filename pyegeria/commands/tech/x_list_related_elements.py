#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

List elements related to given element guid by the specified relationship type. Optionally filter by a specified
open metadata type.

"""
import argparse
import os
import sys
import time

from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
    ClassificationManager,
)

console = Console()
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


def display_related_elements(
    element_guid: str,
    relationship: str,
    om_type: str,
    server: str,
    url: str,
    username: str,
    password: str,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
):
    c_client = ClassificationManager(server, url, user_id=username, user_pwd=password)
    token = c_client.create_egeria_bearer_token()
    rel_el = c_client.get_related_elements(element_guid, relationship, om_type)

    if type(rel_el) is str:
        print(
            f"\n\nWas not able find related elements for {element_guid} with relationship {relationship}\n\n"
        )
        sys.exit(0)

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Elements Related to guid: {element_guid} by relationship: {relationship}  @ {time.asctime()}",
            style="bold bright_white on black",
            row_styles=["bold bright_white on black"],
            header_style="white on dark_blue",
            title_style="bold bright_white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Elements from Server '{server}' @ Platform - {url}",
            expand=True,
            # width=500
        )

        table.add_column("Relationship Properties")
        table.add_column("Preferred Value")
        table.add_column("Case Sensitive")
        table.add_column("Description")
        table.add_column("Additional Properties")

        for related_element in rel_el:
            relationship_props = related_element["relationshipProperties"]

            rel_prop_md = ""
            for key in relationship_props.keys():
                rel_prop_md += f"{key}: {relationship_props[key]}\n"
            # rel_prop_out = Markdown(rel_prop_md)

            rel_element = related_element["relatedElement"]
            el = rel_element["properties"]
            for prop in el:
                el_case = el.get("isCaseSensitive", "---")
                el_pref = el.get("preferredValue", "---")
                el_desc = el.get("description", "---")
                el_add = el.get("additionalProperties", "---")

                el_add_md = ""
                el_add_f = el_add.replace("\u003d", ":")
                s = el_add.strip("{}").strip()
                pairs = [i.split("=") for i in s.split(", ")]
                # d_add_prop = dict(pairs)
                # for key in d_add_prop.keys():
                #     el_add_md += f"{key}: {d_add_prop[key]}\n"
                # el_add_out = Markdown(el_add_md)

            table.add_row(rel_prop_md, el_pref, el_case, el_desc, s)

        return table

    try:
        console = Console(width=width, force_terminal=not jupyter)

        with console.pager(styles=True):
            console.print(generate_table())

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
    ) as e:
        print_exception_response(e)
        assert e.related_http_code != "200", "Invalid parameters"
    finally:
        c_client.close_session()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="Password")

    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    password = args.password if args.password is not None else EGERIA_USER_PASSWORD
    guid = None

    try:
        element_guid = Prompt.ask("Enter an Element GUID find relationships for")
        relationship = Prompt.ask(
            "Enter the relationship to search",
            default="SpecificationPropertyAssignment",
        )
        om_type = Prompt.ask("Enter an optional Open Metadata Type", default="Referenceable")
        display_related_elements(
            element_guid, relationship, om_type, server, url, userid, password
        )
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
