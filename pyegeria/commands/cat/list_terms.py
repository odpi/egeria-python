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
    EgeriaTech,
)

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
    search_string: str = "*",
    glossary_guid: str = None,
    glossary_name: str = None,
    view_server: str = EGERIA_VIEW_SERVER,
    view_url: str = EGERIA_VIEW_SERVER_URL,
    user_id: str = EGERIA_USER,
    user_pass: str = EGERIA_USER_PASSWORD,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
):
    """Display a table of glossary terms filtered by search_string and glossary, if specified. If no
        filters then all terms are displayed. If glossary_guid or name is specified, then only terms from that
        glossary are displayed.
    Parameters
    ----------
    search_string : str, optional
        The string to search for terms. Defaults to "*".
    glossary_guid : str, optional
        The unique identifier of the glossary. Defaults to None. If specified, then only terms from that glossary
        are displayed. If both glossary_guid and glossary_name are provided then glossary_guid will take precedence.
    glossary_name : str, optional
        The display name of the glossary. Defaults to None. If specified, then only terms from that glossary
        are displayed. If both glossary_guid and glossary_name are provided then glossary_guid will take precedence.
        Note that the use of glossary display name relies on the qualified name conforming to convention. GUID is more
        reliable.
    view_server : str
        The server where the glossary is hosted. Defaults to EGERIA_VIEW_SERVER.
    view_url : str
        The URL of the server where the glossary is hosted. Defaults to EGERIA_VIEW_SERVER_URL.
    user_id : str
        The user ID for authentication. Defaults to EGERIA_USER.
    user_pass : str
        The user password for authentication. Defaults to EGERIA_USER_PASSWORD.
    jupyter : bool
        Flag to indicate if the output should be formatted for Jupyter notebook. Defaults to EGERIA_JUPYTER.
    width : int
        The width of the console output. Defaults to EGERIA_WIDTH.
    """

    console = Console(
        style="bold bright_white on black", width=width, force_terminal=not jupyter
    )
    g_client = EgeriaTech(view_server, view_url, user_id, user_pass)
    token = g_client.create_egeria_bearer_token()
    if (glossary_name is not None) and (glossary_name != "*"):
        glossary_guid = g_client.get_guid_for_name(glossary_name)
        if glossary_guid == "No elements found":
            console.print(
                f"\nThe glossary name {glossary_name} was not found. Please try using the glossary guid"
            )
            sys.exit(0)

    def generate_table(search_string: str, glossary_guid: str = None) -> Table:
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
            caption=f"View Server '{view_server}' @ Platform - {view_url}",
            expand=True,
        )
        table.add_column("Term Name")
        table.add_column("Qualified Name / GUID", width=38, no_wrap=True)
        table.add_column("Abbreviation")
        table.add_column("Summary")
        table.add_column("Description")
        table.add_column("Version Id")
        table.add_column("Glossary")
        table.add_column("Status")
        table.add_column("Example")

        terms = g_client.find_glossary_terms(
            search_string,
            glossary_guid,
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
        glossary_info = {}
        for term in sorted_terms:
            props = term.get("glossaryTermProperties", "None")
            if props == "None":
                return table

            display_name = Text(props["displayName"], style=style, justify="center")
            qualified_name = props["qualifiedName"]
            term_guid = term["elementHeader"]["guid"]
            q_name = Text(
                f"{qualified_name}\n&\n{term_guid}", style=style, justify="center"
            )
            abbrev = Text(props.get("abbreviation", " "), style=style, justify="center")
            summary = Text(props.get("summary", " "), style=style)
            description = Text(props.get("description", " "), style=style)
            version = Text(
                props.get("publishVersionIdentifier", " "),
                style=style,
                justify="center",
            )
            example = Text(props.get("example", " "), style=style)

            classifications = term["elementHeader"]["classifications"]
            glossary_guid = None
            for c in classifications:
                if c["classificationName"] == "Anchors":
                    glossary_guid = c["classificationProperties"]["anchorGUID"]

            if glossary_guid and glossary_guid in glossary_info:
                glossary_name = glossary_info[glossary_guid]
            elif glossary_guid:
                g = g_client.get_glossary_for_term(term_guid)
                glossary_name = g["glossaryProperties"].get("displayName", "---")
                glossary_info[glossary_guid] = glossary_name
            else:
                glossary_name = "---"

            term_status = term["elementHeader"]["status"]
            table.add_row(
                display_name,
                q_name,
                abbrev,
                summary,
                description,
                version,
                glossary_name,
                term_status,
                example,
                style="bold white on black",
            )

        g_client.close_session()
        return table

    try:
        with console.pager(styles=True):
            console.print(generate_table(search_string, glossary_guid))

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

    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    guid = args.guid if args.guid is not None else None

    try:
        search_string = Prompt.ask("Enter the term you are searching for:", default="*")
        glossary_name = Prompt.ask(
            "Enter the name of the glossary to search or '*' for all glossaries:",
            default="*",
        )
        display_glossary_terms(
            search_string, guid, glossary_name, server, url, userid, user_pass
        )

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
