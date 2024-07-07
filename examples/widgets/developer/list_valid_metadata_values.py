#!/usr/bin/env python3
"""
SPDX-Lic
ense-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple display for glossary terms
"""

import time
import json
import argparse
from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from rich.table import Table
from rich.live import Live
from rich import box
from rich.prompt import Prompt
from rich.tree import Tree
from rich import print
from rich.console import Console
from pyegeria import ValidMetadataManager

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


def display_values(property_name: str, type_name: str=None, server: str = good_server_3, url: str = good_platform1_url,
                   username: str = good_user_2,  save_output: bool = False):

    m_client = ValidMetadataManager(server, url, user_id=username)
    token = m_client.create_egeria_bearer_token(username, "secret")

    def generate_table(property_name: str, type_name: str) -> Table:
        """Make a new table."""
        table = Table(
            title=f"Valid Metadata Values for Property: {property_name} of type {type_name} @ {time.asctime()}",
            header_style="white on dark_blue",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Valid Metadata Values for Server '{server}' @ Platform - {url}",
            expand=True
        )

        table.add_column("Category")
        table.add_column("Display Name")

        table.add_column("Preferred Value")
        table.add_column("Deprecated")
        table.add_column("Case Sensitive")
        table.add_column("Additional Properties")
        table.add_column("Description")

        valid_values = m_client.get_valid_metadata_values(property_name, type_name)

        if valid_values is None:
            name = " "
            type_name = " "
            created = " "
            priority = " "
            due = " "
            completed = " "
            status = " "
            sponsor = " "
        elif type(valid_values[0]) == str:
            raise ValueError("-->This is not a known metadata property with a valid value")
        else:
            for value in valid_values:
                category = value.get("category","None")
                display_name = value.get("displayName","None")
                preferred_value = value.get("preferredValue", "None ")
                deprecated = str(value.get("isDeprecated", "None "))
                case_sensitive = str(value.get("isCaseSensitive", "None"))
                description = value.get("description", "None")
                additional_properties = value.get('additionalProperties',"None")
                if additional_properties is not None:
                    props = json.dumps(additional_properties)
                table.add_row(
                    category, display_name, preferred_value, deprecated, case_sensitive, props,description
                )

        m_client.close_session()
        return table

    try:
        # with Live(generate_table(), refresh_per_second=4, screen=True) as live:
        #     while True:
        #         time.sleep(2)
        #         live.update(generate_table())
        console = Console(record=True)
        with console.pager():
            console.print(generate_table(property_name, type_name))
        if save_output:
            console.save_html("valid-metadata-values.html")

    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException, ValueError) as e:
        if type(e) is str:
            print(e)
        else:
            print_exception_response(e)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--save-output", help="Save output to file?")
    # parser.add_argument("--sponsor", help="Name of sponsor to search")
    args = parser.parse_args()

    server = args.server if args.server is not None else "view-server"
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'erinoverview'
    save_output = args.save_output if args.save_output is not None else False
    property_name = Prompt.ask("Enter the Property to retrieve:", default="projectHealth")
    type_name = Prompt.ask("Enter the Metadata Type to filter on:", default="Project")
    display_values(property_name, type_name,server, url, userid, save_output)