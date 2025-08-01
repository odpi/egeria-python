#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

A simple display for collections
"""
import argparse
import json
import os
import time

from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from loguru import logger
from pyegeria import (
    CollectionManager,
     NO_ELEMENTS_FOUND,config_logging, get_app_config, init_logging
    )
from pyegeria._exceptions_new import PyegeriaException, print_exception_response

EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
PYEGERIA_ROOT_PATH= os.environ.get("PYEGERIA_ROOT_PATH", "/Users/dwolfson/localGit/egeria-v5-3/egeria-python")
app_settings = get_app_config(PYEGERIA_ROOT_PATH+"/.env")
app_config = app_settings.Environment
config_logging()

out_struct = {
            "formats": {
                "types": ["ALL"],
                "columns": [
                    {'name': 'display_name', 'key': 'display_name'},
                    {'name': 'qualified_name', 'key': 'qualified_name', 'format': True},
                    {'name': 'description', 'key': 'description', 'format': True},
                    {'name': "classifications", 'key': 'classifications'},
                    {'name': 'members', 'key': 'members', 'format': True},
                    {'name': 'collection_type', 'key': 'collection_type', 'format': True},
                    {'name': 'GUID', 'key': 'GUID'},
                ],
            },

        }

def display_collections(
    search_string: str = "*",
    view_server: str = app_config.egeria_view_server,
    view_url: str = app_config.egeria_view_server_url,
    user: str = app_settings.User_Profile.user_name,
    user_pass: str = app_settings.User_Profile.user_pwd,
    jupyter: bool = app_config.egeria_jupyter,
    width: int = app_config.console_width,
    output_format: str = "TABLE"
):
    """Display either a specified glossary or all collections if the search_string is '*'.
    Parameters
    ----------
    search_string : str, default is '*'
        The string used to search for collections.
    view_server : str
        The view server name or address where the Egeria services are hosted.
    view_url : str
        The URL of the platform the view server is on.
    user : str
        The user ID for authentication with the Egeria server.
    user_pass : str
        The password for authentication with the Egeria server.
    jupyter : bool, optional
        A boolean indicating whether the output is intended for a Jupyter notebook (default is EGERIA_JUPYTER).
    width : int, optional
        The width of the console output (default is EGERIA_WIDTH).
    output_format : str, optional
        Format of the output. Default is TABLE.
    """
    m_client = CollectionManager(view_server, view_url, user_id=user, user_pwd=user_pass)
    m_client.create_egeria_bearer_token()
    try:

        if output_format == "FORM":
            action = "Update-Form"
        elif output_format == "REPORT":
            action = "Report"
        elif output_format == "DICT":
            action = "Dict"
        elif output_format == "HTML":
            action = "html"
        elif output_format == "LIST":
            action = "List"

        if output_format != "TABLE":
            file_path = os.path.join(app_config['Pyegeria Root'], app_config['Dr.Egeria Outbox'])
            if output_format == "HTML":
                file_name = f"Collections-{time.strftime('%Y-%m-%d-%H-%M-%S')}-{action}.html"
            else:
                file_name = f"Collections-{time.strftime('%Y-%m-%d-%H-%M-%S')}-{action}.md"
            full_file_path = os.path.join(file_path, file_name)
            os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
            output = m_client.find_collections(
                search_string.strip(), None, True, False, ignore_case=True,
                output_format=output_format
                )
            if output == NO_ELEMENTS_FOUND:
                print(f"\n==> No collections found for search string '{search_string}'")
                return
            elif isinstance(output, str | list) and output_format == "DICT":
                output = json.dumps(output, indent=4)

            with open(full_file_path, 'w') as f:
                f.write(output)
            print(f"\n==> Collections output written to {full_file_path}")
            return

        table = Table(
            title=f"Collection List @ {time.asctime()}",
            style="bright_white on black",
            header_style="bright_white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"View Server '{view_server}' @ Platform - {view_url}",
            expand=True,
        )
        table.add_column("Collection Name")
        table.add_column(
            "Qualified Name & GUID", width=38, no_wrap=True, justify="center"
        )
        table.add_column("Description")
        table.add_column("Collection Type")
        table.add_column("Classifications")
        table.add_column("Members")

        collections = m_client.find_collections(
            search_string.strip(), None, True, False, ignore_case=True,
            output_format = "DICT", output_format_set=out_struct
        )
        if type(collections) is list:

            sorted_collection_list = sorted(
                collections, key=lambda k: k["display_name"]
            )
            for collection in sorted_collection_list:

                display_name = collection["display_name"]
                qualified_name = collection["qualified_name"]
                guid = collection["GUID"]
                q_name = Text(f"{qualified_name}\n&\n{guid}", justify="center")
                description = collection.get("description",'---')
                collection_type = collection.get("collectionType", "---")
                classifications = collection.get("classifications", "---")

                classifications_md = Markdown(classifications)
                members_struct = m_client.get_member_list(collection_guid=guid)
                member_list = ""
                if isinstance(members_struct, list):
                    for member in members_struct:
                        member_list = member_list + f"- {member.get('qualifiedName','---')}\n"

                # members = "\n* ".join(collection.get("members", []))
                members_md = Markdown(member_list)

                table.add_row(
                    display_name,
                    q_name,
                    description,
                    collection_type,
                    classifications_md,
                    members_md,
                )
            console = Console(
                style="bold bright_white on black",
                width=width,
                force_terminal=not jupyter,
            )
            console.print(table)
        else:
            print("==> No collections with that name found")

    except (
        PyegeriaException
    ) as e:
        print_exception_response(e)
    finally:
        m_client.close_session()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")

    args = parser.parse_args()
    # app_settings = get_app_config(PYEGERIA_ROOT_PATH + "/.env")
    # app_config = app_settings.Environment

    server = args.server if args.server is not None else app_config.egeria_view_server
    url = args.url if args.url is not None else app_config.egeria_view_server_url
    userid = args.userid if args.userid is not None else app_settings.User_Profile.user_name
    user_pass = args.password if args.password is not None else app_settings.User_Profile.user_pwd

    try:
        search_string = Prompt.ask(
            "Enter the collection you are looking for or '*' for all:", default="*"
        ).strip()
        output_format = Prompt.ask("Which output format do you want?", choices=["DICT", "TABLE", "FORM", "REPORT", "HTML", "LIST"], default="TABLE")

        display_collections(search_string, server, url, userid, user_pass, output_format = output_format)

    except KeyboardInterrupt:
        pass

    except PyegeriaException as e:
        print_exception_response(e)


if __name__ == "__main__":
    # EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
    # EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
    # PYEGERIA_ROOT_PATH = os.environ.get("PYEGERIA_ROOT_PATH", "/Users/dwolfson/localGit/egeria-v5-3/egeria-python")
    main()
