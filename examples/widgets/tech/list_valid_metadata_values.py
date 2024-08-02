#!/usr/bin/env python3
"""
SPDX-Lic
ense-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple display for glossary terms
"""
import os
import argparse
import json
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
)
from pyegeria import ValidMetadataManager
EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get('KAFKA_ENDPOINT', 'localhost:9092')
EGERIA_PLATFORM_URL = os.environ.get('EGERIA_PLATFORM_URL', 'https://localhost:9443')
EGERIA_VIEW_SERVER = os.environ.get('VIEW_SERVER', 'view-server')
EGERIA_VIEW_SERVER_URL = os.environ.get('EGERIA_VIEW_SERVER_URL', 'https://localhost:9443')
EGERIA_INTEGRATION_DAEMON = os.environ.get('INTEGRATION_DAEMON', 'integration-daemon')
EGERIA_ADMIN_USER = os.environ.get('ADMIN_USER', 'garygeeke')
EGERIA_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'secret')
EGERIA_USER = os.environ.get('EGERIA_USER', 'erinoverview')
EGERIA_USER_PASSWORD = os.environ.get('EGERIA_USER_PASSWORD', 'secret')

def display_values(property_name: str, type_name: str, server: str, url: str,
                   username: str,  user_pass:str, save_output: bool):

    m_client = ValidMetadataManager(server, url, user_id=username)
    token = m_client.create_egeria_bearer_token(username, user_pass)

    def generate_table(property_name: str, type_name: str) -> Table:
        """Make a new table."""
        table = Table(
            title=f"Valid Metadata Values for Property: {property_name} of type {type_name} @ {time.asctime()}",
            style="bold white on black",
            row_styles=["bold white on black"],
            header_style="white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
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
        with console.pager(styles=True):
            console.print(generate_table(property_name, type_name))
        if save_output:
            console.save_html("valid-metadata-values.html")

    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException, ValueError) as e:
        if type(e) is str:
            print(e)
        else:
            print_exception_response(e)

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
    save_output = args.save_output if args.save_output is not None else False
    property_name = Prompt.ask("Enter the Property to retrieve:", default="projectHealth")

    try:
        type_name = Prompt.ask("Enter the Metadata Type to filter on:", default="Project")
        display_values(property_name, type_name,server, url, userid, user_pass, save_output)
    except(KeyboardInterrupt):
        pass


if __name__ == "__main__":
    main()
