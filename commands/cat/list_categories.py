#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

List categories for a category.


A simple display for category terms
"""
import argparse
import os
import sys
import time

from rich import box
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from pyegeria import (
    EgeriaTech,
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)

disable_ssl_warnings = True

EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("EGERIA_VIEW_SERVER", "view-server")
EGERIA_VIEW_SERVER_URL = os.environ.get(
    "EGERIA_VIEW_SERVER_URL", "https://localhost:9443"
)
EGERIA_INTEGRATION_DAEMON = os.environ.get("EGERIA_INTEGRATION_DAEMON", "integration-daemon")
EGERIA_ADMIN_USER = os.environ.get("ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_JUPYTER = bool(os.environ.get("EGERIA_JUPYTER", "False"))
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "150"))
EGERIA_category_PATH = os.environ.get("EGERIA_category_PATH", None)
EGERIA_ROOT_PATH = os.environ.get("EGERIA_ROOT_PATH", "../../")
EGERIA_INBOX_PATH = os.environ.get("EGERIA_INBOX_PATH", "md_processing/dr_egeria_inbox")
EGERIA_OUTBOX_PATH = os.environ.get("EGERIA_OUTBOX_PATH", "md_processing/dr_egeria_outbox")



def display_categories(
    search_string: str = "*",
    view_server: str = EGERIA_VIEW_SERVER,
    view_url: str = EGERIA_VIEW_SERVER_URL,
    user: str = EGERIA_USER,
    user_pass: str = EGERIA_USER_PASSWORD,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
    output_format: str = "TABLE",
):
    """Display either a specified category or all categories if the search_string is '*'.
    Parameters
    ----------
    search_string : str, default is '*'
        The string used to search for categories.
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
    output_format: str, optional, default is 'JSON'
        One of  FORM, REPORT, TABLE
    """
    m_client = EgeriaTech(view_server, view_url, user_id=user, user_pwd=user_pass)
    token = m_client.create_egeria_bearer_token()


    try:
        if output_format == "FORM":
            action = "Update-Form"
        elif output_format == "REPORT":
            action = "Report"
        if output_format != "TABLE":
            file_path = os.path.join(EGERIA_ROOT_PATH, EGERIA_OUTBOX_PATH)
            file_name = f"Categories-{time.strftime('%Y-%m-%d-%H-%M-%S')}-{action}.md"
            full_file_path = os.path.join(file_path, file_name)
            os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
            output = m_client.find_glossary_categories(search_string, output_format=output_format)
            if output == "NO_CATEGORIES_FOUND":
                print(f"\n==> No categories found for search string '{search_string}'")
                return
            with open(full_file_path, 'w') as f:
                f.write(output)
            print(f"\n==> Categories output written to {full_file_path}")
            return

        table = Table(
            title=f"Category List @ {time.asctime()}",
            style="bright_white on black",
            header_style="bright_white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"View Server '{view_server}' @ Platform - {view_url}",
            expand=True,
        )
        table.add_column("Category Name")
        table.add_column(
            "Qualified Name & GUID", width=38, no_wrap=True, justify="center"
        )
        table.add_column("Description")
        table.add_column("In Glossary")
        table.add_column("Parent Category")

        categories = m_client.find_glossary_categories(search_string)
        if type(categories) is list:
            sorted_category_list = sorted(
                categories, key=lambda k: k["glossaryCategoryProperties"]["displayName"]
            )
            for category in sorted_category_list:
                display_name = category["glossaryCategoryProperties"].get("displayName",'---')
                qualified_name = category["glossaryCategoryProperties"]["qualifiedName"]
                category_guid = category["elementHeader"]["guid"]
                q_name = Text(f"{qualified_name}\n&\n{category_guid}", justify="center")
                description = category["glossaryCategoryProperties"].get("description",'---')
                classification_props = category["elementHeader"]['classifications'][0].get('classificationProperties',None)
                glossary_qualified_name = '---'
                if classification_props is not None:
                    glossary_guid = classification_props.get('anchorScopeGUID','---')
                    glossary_qualified_name = (
                        m_client.get_glossary_by_guid(glossary_guid))['glossaryProperties']['qualifiedName']
                cat_info = m_client.get_category_parent(category_guid)
                if type(cat_info) is dict:
                    parent_qn = cat_info['glossaryCategoryProperties']['qualifiedName']
                else:
                    parent_qn = '---'


                table.add_row(display_name, q_name, description, glossary_qualified_name, parent_qn)
            console = Console(
                style="bold bright_white on black",
                width=width,
                force_terminal=not jupyter,
            )
            console.print(table)

    except (InvalidParameterException, PropertyServerException) as e:
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

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD

    try:
        search_string = Prompt.ask(
            "Enter the category you are searching for or '*' for all:", default="*"
        )
        output_format = Prompt.ask("What output format do you want?", choices=["TABLE", "FORM", "REPORT"],
                                   default="TABLE")

        display_categories(search_string, server, url, userid,
                           user_pass, output_format = output_format)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
