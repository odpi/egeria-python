#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

A simple display for Data Structures
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

from pyegeria import (
    EgeriaTech,
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response, NO_ELEMENTS_FOUND,
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
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "200"))
EGERIA_GLOSSARY_PATH = os.environ.get("EGERIA_GLOSSARY_PATH", None)
EGERIA_ROOT_PATH = os.environ.get("EGERIA_ROOT_PATH", "../../")
EGERIA_INBOX_PATH = os.environ.get("EGERIA_INBOX_PATH", "md_processing/dr_egeria_inbox")
EGERIA_OUTBOX_PATH = os.environ.get("EGERIA_OUTBOX_PATH", "md_processing/dr_egeria_outbox")


def display_data_struct(
    search_string: str = "*",
    view_server: str = EGERIA_VIEW_SERVER,
    view_url: str = EGERIA_VIEW_SERVER_URL,
    user: str = EGERIA_USER,
    user_pass: str = EGERIA_USER_PASSWORD,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
    output_format: str = "TABLE"
):
    """Display data structures filtered by search_string. If search_string is not specified, all data structures are displayed.
    Parameters
    ----------
    search_string : str, default is '*'
        The string used to search for structures.
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
    m_client = EgeriaTech(view_server, view_url, user_id=user, user_pwd=user_pass)
    m_client.create_egeria_bearer_token()
    try:

        if output_format == "FORM":
            action = "Update-Form"
        elif output_format == "REPORT":
            action = "Report"
        elif output_format == "DICT":
            action = "Dict"
        elif output_format == "MERMAID":
            action = "Mermaid"
        filter = search_string.strip() if search_string != "*" else None

        body = {
            "class": "FilterRequestBody",
            "asOfTime": None,
            "effectiveTime": None,
            "forLineage": False,
            "forDuplicateProcessing" : False,
            "limitResultsByStatus": ["ACTIVE"],
            "sequencingOrder": "PROPERTY_ASCENDING",
            "sequencingProperty": "qualifiedName",
            "filter": filter
            }

        if output_format != "TABLE":
            file_path = os.path.join(EGERIA_ROOT_PATH, EGERIA_OUTBOX_PATH)
            file_name = f"Terms-{time.strftime('%Y-%m-%d-%H-%M-%S')}-{action}.md"
            full_file_path = os.path.join(file_path, file_name)
            os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
            output = m_client.find_data_structures_w_body(
                body, 0, None, starts_with= True, ends_with=False, ignore_case=False,
                output_format=output_format
                )
            if output == NO_ELEMENTS_FOUND:
                print(f"\n==> No structures found for search string '{search_string}'")
                return
            elif isinstance(output, str | list) and output_format == "DICT":
                output = json.dumps(output, indent=4)
            elif isinstance(output, list) and output_format == "MERMAID":
                output = "\n\n".join(output)

            with open(full_file_path, 'w') as f:
                f.write(output)
            print(f"\n==> structures output written to {full_file_path}")
            return

        table = Table(
            title=f"Data Structure List @ {time.asctime()}",
            style="bright_white on black",
            header_style="bright_white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"View Server '{view_server}' @ Platform - {view_url}",
            expand=True,
        )
        table.add_column("Data Structure Name")
        table.add_column("Namespace")
        table.add_column(
            "Qualified Name & GUID", width=38, no_wrap=True, justify="center"
        )
        table.add_column("Description")
        table.add_column("Classifications")
        table.add_column("Version Id")


        structures = m_client.find_data_structures_w_body(
            body, 0, None, starts_with = True, ends_with=False, ignore_case=False,
            output_format = "DICT"
        )
        if type(structures) is list:
            sorted_structures_list = sorted(
                structures, key=lambda k: k["displayName"]
            )
            for structure in sorted_structures_list:
                display_name = structure["displayName"]
                qualified_name = structure["qualifiedName"]
                namespace = structure.get("namespace",'---')
                version_id = structure.get("versionId",'---')

                guid = structure["guid"]
                q_name = Text(f"{qualified_name}\n&\n{guid}", justify="center")
                description = structure.get("description",'---')
                classifications = structure.get("classifications", "---")
                classifications_md = Markdown(classifications)

                table.add_row(
                    display_name,
                    namespace,
                    q_name,
                    description,
                    classifications_md,
                    version_id
                )
            console = Console(
                style="bold bright_white on black",
                width=width,
                force_terminal=not jupyter,
            )
            console.print(table)
        else:
            print("==> No structures with that name found")

    except (
        InvalidParameterException,
        UserNotAuthorizedException,
        PropertyServerException,
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

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD

    try:
        search_string = Prompt.ask(
            "Enter the data structures you are searching for or '*' for all:", default="*"
        ).strip()
        output_format = Prompt.ask("What output format do you want?", choices=["DICT", "TABLE", "FORM", "REPORT", "MERMAID"], default="TABLE")

        display_data_struct(search_string, server, url, userid, user_pass, output_format = output_format)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
