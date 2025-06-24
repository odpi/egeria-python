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

from rich import box, print
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich.console import Console
from rich.markdown import Markdown


from pyegeria import (
    EgeriaTech,
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
    NO_ELEMENTS_FOUND
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

console = Console(width=EGERIA_WIDTH)


def display_data_obj(
    object_type: str,
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
    object_type: str
        The type of object to display,
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

    match object_type:
        case "Data Structures":
            find_proc = m_client.find_data_structures
        case "Data Fields":
            find_proc = m_client.find_data_fields
        case "Data Classes":
            find_proc = m_client.find_data_classes
        case _: #catch invalid patterns
            print(f"Invalid object type: {object_type}")
            return

    try:
        if not callable(find_proc):
            raise TypeError(f"find_proc is not callable for object type '{object_type}'")

        if output_format == "FORM":
            action = "Update-Form"
        elif output_format == "REPORT":
            action = "Report"
        if output_format != "TABLE":
            file_path = os.path.join(EGERIA_ROOT_PATH, EGERIA_OUTBOX_PATH)
            file_name = f"{object_type}-{time.strftime('%Y-%m-%d-%H-%M-%S')}-{action}.md"
            full_file_path = os.path.join(file_path, file_name)
            os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
            output = find_proc(search_string, output_format=output_format)
            if output == NO_ELEMENTS_FOUND:
                print(f"\n==> No elements found for search string '{search_string}'")
                return
            with open(full_file_path, 'w') as f:
                f.write(output)
            print(f"\n==> Elements output written to {full_file_path}")
            return
        else:
            output =find_proc(search_string, output_format="LIST")
            if output == NO_ELEMENTS_FOUND:
                print(f"\n==> No elements found for search string '{search_string}'")
                return
            console.print(Markdown(output))
            return




    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        m_client.close_session()


def main_structs():
    main(object_type = "Data Structures")

def main_fields():
    main(object_type = "Data Fields")

def main_classes():
    main(object_type = "Data Classes")

def main(object_type: str="Data Fields"):
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=["Data Structures", "Data Fields", "Data Classes"])
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")

    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    kind = args.kind if args.kind is not None else object_type

    try:
        search_string = Prompt.ask(
            "Enter the element you are searching for or '*' for all:", default="*"
        )
        output_format = Prompt.ask("What output format do you want?", choices=["TABLE", "FORM", "REPORT"],
                                   default="TABLE")

        display_data_obj(kind, search_string, server, url, userid,
                           user_pass, output_format = output_format)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
