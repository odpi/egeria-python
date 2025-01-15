#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Display the status of cataloged platforms and servers.
"""
import argparse
import os
import sys
import time

import rich.box as box
from rich import print
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
    AutomatedCuration,
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


disable_ssl_warnings = True
console = Console(width=200)

guid_list = []


def list_tech_elements(
    tech_name: str,
    server_name: str,
    platform_url: str,
    user: str,
    user_pass: str,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
):
    console = Console(width=width, force_terminal=not jupyter)

    a_client = AutomatedCuration(server_name, platform_url, user_id=user)
    token = a_client.create_egeria_bearer_token(user, user_pass)

    def build_classifications(classification: dict) -> Markdown:
        class_md = "\n"
        for c in classification:
            c_type = c["classificationName"]
            if c_type == "Anchors":
                continue
            class_md += f"* Classification: {c_type}\n"
            class_props = c.get("classificationProperties", None)
            if class_props is None:
                continue
            for prop in class_props.keys():
                class_md += f"\t* {prop}: {class_props[prop]}\n"
        if class_md == "-":
            output = None
        else:
            output = class_md
        return output

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Tech Type Elements for {tech_name} @ {time.asctime()}",
            caption=f"{platform_url} - {server_name} @ {time.asctime()}",
            style="bold bright_white on black",
            row_styles=["bold bright_white on black"],
            header_style="white on dark_blue",
            title_style="bold bright_white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            expand=True,
        )

        table.add_column("Qualified Name/GUID", width=38, no_wrap=True)
        table.add_column("Properties", width=40)
        table.add_column("Classifications", width=50)

        tech_elements = a_client.get_technology_type_elements(
            tech_name, get_templates=False
        )
        if type(tech_elements) is str:
            console.print(f"No elements found for {tech_name}")
            sys.exit(1)

        note: str = " "
        for element in tech_elements:
            header = element["elementHeader"]
            tech_type = header["type"]["typeName"]
            tech_collection = header["origin"]["homeMetadataCollectionName"]
            tech_created_by = header["versions"]["createdBy"]
            tech_created_at = header["versions"]["createTime"]
            tech_guid = header["guid"]
            tech_classifications = header["classifications"]
            class_md = build_classifications(tech_classifications)

            referenceables = element["referenceableProperties"]
            tech_qualified_name = referenceables["qualifiedName"]
            extended = referenceables["extendedProperties"]
            ex_md: str = ""
            for key, value in extended.items():
                ex_md += f"* {key}: {value}\n"

            note = (
                f"{ex_md}\n"
                f"* Created by: {tech_created_by}\n"
                f"* Created at: {tech_created_at}\n"
                f"* Home Collection: {tech_collection}\n"
            )

            interfaces = extended.get("connectorInterfaces", None)
            if interfaces is not None:
                interface_type_name = interfaces["typeName"]
                interface_array_cnt = interfaces["arrayCount"]
                note += f"* Interface Type: {interface_type_name}\n"
                for i in range(0, int(interface_array_cnt)):
                    note += (
                        f"\t* Type: {interfaces['arrayValues']['propertyValueMap'][str(i)]['typeName']}"
                        f"\tName: {interfaces['arrayValues']['propertiesAsStrings'][str(i)]}\n"
                    )
            note_md = Markdown(note)
            qn = Markdown(f"\n{tech_qualified_name}\n \n--- \n\n\n{tech_guid}")
            cm = Markdown(class_md)
            table.add_row(qn, note_md, cm)
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
        print("\n\nPerhaps the type name isn't known")
    finally:
        a_client.close_session()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    try:
        tech_name = Prompt.ask(
            "Enter the tech type to view:", default="PostgreSQL Server"
        )
        list_tech_elements(tech_name, server, url, userid, user_pass)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
