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
from pyegeria import ValidMetadataManager, ProjectManager

disable_ssl_warnings = True

good_platform1_url = "https://127.0.0.1:9443"


# good_platform1_url = "https://127.0.0.1:30080"
# good_platform2_url = "https://127.0.0.1:30081"
# bad_platform1_url = "https://localhost:9443"

good_user_1 = "garygeeke"
good_user_2 = "erinoverview"
good_server_3 = "view-server"



def display_list(standard: str, org:str, identifier:str, server: str = good_server_3, url: str = good_platform1_url,
                   username: str = good_user_2,  save_output: bool = False):

    p_client = ValidMetadataManager(server, url, user_id=username)
    token = p_client.create_egeria_bearer_token(username, "secret")

    def generate_table(standard:str, org: str, identifier: str) -> Table:
        """Make a new table."""
        table = Table(
            title=f"Metadata Types: {identifier}  @ {time.asctime()}",
            header_style="white on dark_blue",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Type list for Server '{server}' @ Platform - {url}",
            expand=True
        )


        table.add_column("Name")
        table.add_column("GUID", no_wrap=True,)
        table.add_column("Status")
        table.add_column("Description")
        table.add_column("Description Wiki")
        table.add_column("Attribute Name")
        table.add_column("Attribute Status")
        table.add_column("Attribute GUID")
        table.add_column("Attribute Type")
        table.add_column("Attribute Description")


        types_list = p_client.find_types_by_external_id(standard, org, identifier)

        if types_list is None:
            name = " "
            guid = " "
            status = " "

        elif type(types_list) == str:
            raise ValueError("-->This is not a known Type")
        else:
            for types in types_list:

                name = types['name']
                guid = types['guid']
                status = types['initialStatus']
                description = types['description']
                description_wiki = types['descriptionWiki']
                attribute_defs = types['attributeDefinitions']


                table.add_row(
                    name, guid, classification, qualified_name, identifier, phase, health, status, start,
                    end,description)

        p_client.close_session()
        return table

    try:
        # with Live(generate_table(), refresh_per_second=4, screen=True) as live:
        #     while True:
        #         time.sleep(2)
        #         live.update(generate_table())
        console = Console(record=True)
        with console.pager():
            console.print(generate_table(project_name))
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
    # parser.add_argument("--sponsor", help="Name of sponsor to search")
    args = parser.parse_args()

    server = args.server if args.server is not None else "view-server"
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'erinoverview'
    save_output = args.save_output if args.save_output is not None else False
    project_name = Prompt.ask("Enter the Property to retrieve:", default="*")

    display_list(project_name, server, url, userid, save_output)