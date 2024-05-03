#!/usr/bin/env python3
"""
SPDX-Lic
ense-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


Get valid relationship types.
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



def display_list(type_name:str, server: str = good_server_3, url: str = good_platform1_url,
                   username: str = good_user_2,  save_output: bool = False):

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


        table.add_column("Name")
        # table.add_column("GUID", no_wrap=True,)
        table.add_column("Status")
        table.add_column("Description")
        table.add_column("Description Wiki")
        table.add_column("Attribute Name")
        table.add_column("Attribute Status")
        table.add_column("Attribute Type")
        # table.add_column("Attribute Type")
        table.add_column("Attribute Description")

        types_list = p_client.get_valid_relationship_types(type_name)
        # print(json.dumps(types_list, indent=4))
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
                            name, status, description, description_wiki, attr_name, attr_status, attr_type, attr_desc
                        )
                else:
                    table.add_row(name,status,description,description_wiki," ", " ", " "," " )

        p_client.close_session()
        return table

    try:
        # with Live(generate_table(), refresh_per_second=4, screen=True) as live:
        #     while True:
        #         time.sleep(2)
        #         live.update(generate_table())
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
    # parser.add_argument("--sponsor", help="Name of sponsor to search")
    args = parser.parse_args()

    server = args.server if args.server is not None else "view-server"
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'erinoverview'
    save_output = args.save_output if args.save_output is not None else False
    type_name = Prompt.ask("Enter the Type Name to retrieve:", default="*")

    display_list(type_name, server, url, userid, save_output)