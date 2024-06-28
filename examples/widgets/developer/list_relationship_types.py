#!/usr/bin/env python3
"""
SPDX-Lic
ense-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


Get valid relationship types.
"""

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


def display_list(type_name:str, server: str, url: str ,
                   username: str, save_output: bool = False):

    p_client = ValidMetadataManager(server, url, user_id=username)
    token = p_client.create_egeria_bearer_token(username, "secret")

    def generate_table(type_name: str) -> Table:
        """Make a new table."""
        table = Table(
            title=f"Relationship types for: {type_name}  @ {time.asctime()}",
            header_style="white on dark_blue",
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
        with console.pager():
            console.print(generate_table(type_name))
        if save_output:
            console.save_html("projects.html")

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

    args = parser.parse_args()

    server = args.server if args.server is not None else "view-server"
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'erinoverview'
    save_output = args.save_output if args.save_output is not None else False
    type_name = Prompt.ask("Enter the Type Name to retrieve:", default="AssetOwner")

    display_list(type_name, server, url, userid, save_output)