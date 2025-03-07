#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple display for glossary terms
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
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "200"))
EGERIA_GLOSSARY_PATH = os.environ.get("EGERIA_GLOSSARY_PATH", None)
EGERIA_ROOT_PATH = os.environ.get("EGERIA_ROOT_PATH", "/Users/dwolfson/localGit/egeria-v5-3/egeria-python")
EGERIA_INBOX_PATH = os.environ.get("EGERIA_INBOX_PATH", "pyegeria/commands/cat/freddies-inbox")
EGERIA_OUTBOX_PATH = os.environ.get("EGERIA_OUTBOX_PATH", "pyegeria/commands/cat/freddies-outbox")



def display_glossaries(
    search_string: str = "*",
    view_server: str = EGERIA_VIEW_SERVER,
    view_url: str = EGERIA_VIEW_SERVER_URL,
    user: str = EGERIA_USER,
    user_pass: str = EGERIA_USER_PASSWORD,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
    md: bool = False,
    form: bool = False,
):
    """Display either a specified glossary or all glossaries if the search_string is '*'.
    Parameters
    ----------
    search_string : str, default is '*'
        The string used to search for glossaries.
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
    md: bool, [default=False]
        If true, a simplified markdown report of the glossaries will be created. Filename is Glossaries-<DATE>-<ACTION>
        The filepath is derived from the environment variables EGERIA_ROOT_PATH and EGERIA_OUTPUT_PATH, respectively.
    form: bool, [default=False]
        If true and md is true, a form for the glossaries will be created as a markdown file.
        If false and md is true, a markdown report for the glossaries will be created.
    """
    m_client = EgeriaTech(view_server, view_url, user_id=user, user_pwd=user_pass)
    token = m_client.create_egeria_bearer_token()


    try:
        if md:
            if form:
                action = "Update-Form"
            else:
                action = "Report"
            file_path = os.path.join(EGERIA_ROOT_PATH, EGERIA_OUTBOX_PATH)
            file_name = f"Glossaries-{time.strftime('%Y-%m-%d-%H-%M-%S')}-{action}.md"
            full_file_path = os.path.join(file_path, file_name)
            os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
            output = m_client.find_glossaries(search_string, md=md, form=form)
            if output == "NO_GLOSSARIES_FOUND":
                print(f"\n==> No glossaries found for search string '{search_string}'")
                return
            with open(full_file_path, 'w') as f:
                f.write(output)
            print(f"\n==> Glossaries output written to {full_file_path}")
            return

        table = Table(
            title=f"Glossary List @ {time.asctime()}",
            style="bright_white on black",
            header_style="bright_white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"View Server '{view_server}' @ Platform - {view_url}",
            expand=True,
        )
        table.add_column("Glossary Name")
        table.add_column(
            "Qualified Name & GUID", width=38, no_wrap=True, justify="center"
        )
        table.add_column("Language")
        table.add_column("Description")
        table.add_column("Usage")

        glossaries = m_client.find_glossaries(search_string)
        if type(glossaries) is list:
            sorted_glossary_list = sorted(
                glossaries, key=lambda k: k["glossaryProperties"]["displayName"]
            )
            for glossary in sorted_glossary_list:
                display_name = glossary["glossaryProperties"].get("displayName",'---')
                qualified_name = glossary["glossaryProperties"]["qualifiedName"]
                guid = glossary["elementHeader"]["guid"]
                q_name = Text(f"{qualified_name}\n&\n{guid}", justify="center")
                language = glossary["glossaryProperties"].get("language",'---')
                description = glossary["glossaryProperties"].get("description",'---')
                usage = glossary["glossaryProperties"].get("usage",'---')
                table.add_row(display_name, q_name, language, description, usage)
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
            "Enter the glossary you are searching for or '*' for all:", default="*"
        )
        mdq = Prompt.ask("Do you want to create a markdown report?", choices=["y", "n"], default="n")
        md = True if mdq.lower() == "y" else False

        formq = Prompt.ask("Do you want to create a form?", choices=["y", "n"], default="n")
        form = True if formq.lower() == "y" else False

        display_glossaries(search_string, server, url, userid,
                           user_pass, md = md, form = form)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
