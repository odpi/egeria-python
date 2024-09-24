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
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
)
from pyegeria.glossary_browser_omvs import GlossaryBrowser

disable_ssl_warnings = True

EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("VIEW_SERVER", "view-server")
EGERIA_VIEW_SERVER_URL = os.environ.get(
    "EGERIA_VIEW_SERVER_URL", "https://localhost:9443"
)
EGERIA_INTEGRATION_DAEMON = os.environ.get("INTEGRATION_DAEMON", "integration-daemon")
EGERIA_ADMIN_USER = os.environ.get("ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_JUPYTER = bool(os.environ.get("EGERIA_JUPYTER", "False"))
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "200"))


def display_glossary_terms(
    search_string: str,
    guid: str,
    server: str,
    url: str,
    username: str,
    user_password: str,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
):
    g_client = GlossaryBrowser(server, url, username, user_password)
    token = g_client.create_egeria_bearer_token()

    def generate_table(search_string: str = "*") -> Table:
        """Make a new table."""
        table = Table(
            title=f"Glossary Definitions for Terms like  {search_string} @ {time.asctime()}",
            style="bright_white on black",
            # row_styles="bright_white on black",
            header_style="bright_white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Glossary View Server '{server}' @ Platform - {url}",
            expand=True,
        )
        table.add_column("Display Name")
        table.add_column("Qualified Name")

        table.add_column("Abbreviation")
        table.add_column("Summary")
        table.add_column("Description")

        terms = g_client.find_glossary_terms(
            search_string,
            guid,
            starts_with=False,
            ends_with=False,
            status_filter=[],
            page_size=500,
        )

        if type(terms) is str:
            print(f"No terms found!")
            sys.exit(0)
        sorted_terms = sorted(
            terms, key=lambda k: k["glossaryTermProperties"]["displayName"]
        )
        style = "bright_white on black"
        if type(terms) is str:
            return table

        for term in sorted_terms:
            props = term.get("glossaryTermProperties", "None")
            if props == "None":
                return table

            display_name = Text(props["displayName"], style=style)
            qualified_name = Text(props["qualifiedName"], style=style)
            abbrev = Text(props.get("abbreviation", " "), style=style)
            summary = Text(props.get("summary", " "), style=style)
            description = Text(props.get("description", " "), style=style)

            table.add_row(
                display_name,
                qualified_name,
                abbrev,
                summary,
                description,
                style="bold white on black",
            )

        g_client.close_session()
        return table

    try:
        # with Live(generate_table(), refresh_per_second=4, screen=True) as live:
        #     while True:
        #         time.sleep(2)
        #         live.update(generate_table(search_string))
        console = Console(
            style="bold bright_white on black", width=width, force_terminal=not jupyter
        )
        with console.pager(styles=True):
            console.print(generate_table(search_string))

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
    ) as e:
        console.print_exception()


def main():
    sus_guid = "f9b78b26-6025-43fa-9299-a905cc6d1575"
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    parser.add_argument("--guid", help="GUID of glossary to search")
    parser.add_argument("--sustainability", help="Set True for Sustainability Glossary")
    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    guid = args.guid if args.guid is not None else None
    guid = sus_guid if args.sustainability else None

    try:
        search_string = Prompt.ask("Enter the term you are searching for:", default="*")
        display_glossary_terms(search_string, guid, server, url, userid, user_pass)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
