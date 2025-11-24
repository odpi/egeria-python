#!/usr/bin/env python3
"""
SPDX-Lic
ense-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


Get valid relationship types.
"""
import argparse
import os
import time

from rich import box, print
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table

from pyegeria import (
    PyegeriaException,
    ValidMetadataManager,
    print_basic_exception,
    settings,
    config_logging
)

EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")

app_config = settings.Environment
config_logging()
console = Console(width=app_config.console_width)


def display_relationship_types(
    type_name: str,
    server: str,
    url: str,
    username: str,
    user_pass: str,
    save_output: bool = False,
    jupyter: bool = app_config.egeria_jupyter,
    width: int = app_config.console_width,
):
    p_client = ValidMetadataManager(server, url, user_id=username, user_pwd=user_pass)
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
            expand=True,
        )

        table.add_column("Name")
        table.add_column("Status")
        table.add_column("Description")
        table.add_column("Description Wiki", no_wrap=True)
        table.add_column("Attributes", min_width=50)

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
                name = types["name"]
                # guid = types['guid']
                status = types["initialStatus"]
                description = types["description"]
                description_wiki = types.get("descriptionWiki", " ")
                attribute_defs = types.get("attributeDefinitions")

                att_table = Table(show_lines=True)
                att_table.add_column("Name")
                att_table.add_column("Description")
                att_table.add_column("Status")
                att_table.add_column("Type")

                if attribute_defs:
                    att_md = True
                    for attr in attribute_defs:
                        attr_name = attr["attributeName"]
                        attr_desc = attr["attributeDescription"]
                        attr_status = attr["attributeStatus"]
                        attr_type = attr["attributeType"]["name"]
                        att_table.add_row(attr_name, attr_desc, attr_status, attr_type)

                else:
                    att_md = False
            att_out = att_table if att_md else " "

            table.add_row(name, status, description, description_wiki, att_out)
        p_client.close_session()
        return table

    try:
        console = Console(width=width, force_terminal=not jupyter, record=True)
        with console.pager(styles=True):
            console.print(generate_table(type_name))
        if save_output:
            console.save_html("projects.html")

    except (
        PyegeriaException,
        ValueError,
    ) as e:
        if type(e) is str:
            print(e)
        else:
            print_basic_exception(e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    parser.add_argument("--save-output", help="Save output to file?")

    args = parser.parse_args()

    server = args.server if args.server is not None else app_config.egeria_view_server
    url = args.url if args.url is not None else app_config.egeria_platform_url
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    save_output = args.save_output if args.save_output is not None else False
    type_name = Prompt.ask(
        "Enter the OM Type Name to retrieve relationships for:", default="AssetOwner"
    )

    display_relationship_types(type_name, server, url, userid, user_pass, save_output)


if __name__ == "__main__":
    main()
