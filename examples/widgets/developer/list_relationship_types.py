#!/usr/bin/env python3
"""
SPDX-Lic
ense-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


Get valid relationship types.
"""
import os
import argparse
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


def display_list(type_name:str, server: str, url: str ,
                   username: str, user_pass:str, save_output: bool = False):

    p_client = ValidMetadataManager(server, url, user_id=username)
    token = p_client.create_egeria_bearer_token(username, user_pass)

    def generate_table(type_name: str) -> Table:
        """Make a new table."""
        table = Table(
            title=f"Relationship types for: {type_name}  @ {time.asctime()}",
            style="bold white on black",
            row_styles=["bold white on black"],
            header_style="white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"list for Server '{server}' @ Platform - {url}",
            expand=True
        )

        table.add_column("Status")
        table.add_column("Name")
        # table.add_column("GUID", no_wrap=True,)

        table.add_column("Description")
        table.add_column("Attrib Name")
        table.add_column("Attrib Status")
        table.add_column("Attrib Type")
        table.add_column("Attrib Description")
        table.add_column("Description Wiki", no_wrap=True)

        types_list = p_client.get_valid_relationship_types(type_name)

        print(type(types_list))
        if types_list is None:
            name = " "
            guid = " "
            status = " "

        elif type(types_list) == str:
            print(types_list)
            raise ValueError("-->This is not a known Type")
        else:
            for types in types_list:

                name = types['name']
                # guid = types['guid']
                status = types['initialStatus']
                description = types['description']
                description_wiki = types.get("descriptionWiki"," ")
                attribute_defs = types.get("attributeDefinitions")
                if attribute_defs:
                    for attr in attribute_defs:
                        attr_name = attr['attributeName']
                        attr_desc = attr['attributeDescription']
                        attr_status = attr['attributeStatus']
                        attr_type = attr['attributeType']["name"]
                        table.add_row(
                             status, name, description, attr_name, attr_status, attr_type, attr_desc,
                            description_wiki
                        )
                else:
                    table.add_row(status,name,description,description_wiki," ", " ", " "," " )

        p_client.close_session()
        return table

    try:

        console = Console(record=True)
        with console.pager(styles=True):
            console.print(generate_table(type_name))
        if save_output:
            console.save_html("projects.html")

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
    parser.add_argument("--password", help="User Password")
    parser.add_argument("--save-output", help="Save output to file?")

    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    save_output = args.save_output if args.save_output is not None else False
    type_name = Prompt.ask("Enter the Type Name to retrieve:", default="AssetOwner")

    display_list(type_name, server, url, userid, user_pass,save_output)

if __name__ == "__main__":
    main()