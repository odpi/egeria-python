#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
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


from pyegeria.server_operations import ServerOps
from pyegeria._deprecated_gov_engine import GovEng
from pyegeria.glossary_browser_omvs import GlossaryBrowser
disable_ssl_warnings = True

good_platform1_url = "https://127.0.0.1:9443"
good_platform2_url = "https://egeria.pdr-associates.com:7443"
bad_platform1_url = "https://localhost:9443"

# good_platform1_url = "https://127.0.0.1:30080"
# good_platform2_url = "https://127.0.0.1:30081"
# bad_platform1_url = "https://localhost:9443"

good_user_1 = "garygeeke"
good_user_2 = "erinoverview"
bad_user_1 = "eviledna"
bad_user_2 = ""

good_server_1 = "active-metadata-store"
good_server_2 = "simple-metadata-store"
good_server_3 = "view-server"
good_server_4 = "engine-host"
bad_server_1 = "coco"
bad_server_2 = ""


def display_glossary_terms(search_string: str, guid: str=None, server: str = good_server_3, url: str = good_platform1_url, username: str = good_user_2):

    g_client = GlossaryBrowser(server, url)
    token = g_client.create_egeria_bearer_token(username, "secret")


    def generate_table(search_string:str = '*') -> Table:
        """Make a new table."""
        table = Table(
            title=f"Glossary Definitions for Terms like  {search_string} @ {time.asctime()}",
            # style = "black on grey66",
            header_style="white on dark_blue",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Glossary View Server '{server}' @ Platform - {url}",
            expand=True
        )
        table.add_column("Display Name")
        table.add_column("Qualified Name")

        table.add_column("Abbreviation")
        table.add_column("Summary")
        table.add_column("Description")

        terms = g_client.find_glossary_terms(search_string, guid, starts_with=True,
                                             ends_with=False, status_filter=[], page_size=500)
        if type(terms) is str:
            return table

        for term in terms:
            props = term.get("glossaryTermProperties","None")
            if props == "None":
                return table

            display_name = props["displayName"]
            qualified_name = props["qualifiedName"]
            abbrev = props.get("abbreviation"," ")
            summary = props.get("summary", " ")
            description = props.get("description", " ")


            table.add_row(
                display_name,qualified_name, abbrev, summary, description
            )

        g_client.close_session()
        return table

    try:
        # with Live(generate_table(), refresh_per_second=4, screen=True) as live:
        #     while True:
        #         time.sleep(2)
        #         live.update(generate_table())
        console = Console()
        with console.pager():
            console.print(generate_table(search_string))


    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
        print_exception_response(e)
        assert e.related_http_code != "200", "Invalid parameters"

if __name__ == "__main__":
    sus_guid = "f9b78b26-6025-43fa-9299-a905cc6d1575"
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--guid", help="GUID of glossary to search")
    parser.add_argument("--sustainability", help="Set True for Sustainability Glossary")
    args = parser.parse_args()

    server = args.server if args.server is not None else "view-server"
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'garygeeke'
    guid = args.guid if args.guid is not None else None
    guid = sus_guid  if args.sustainability else None

    search_string = Prompt.ask("Enter the term you are searching for:", default="*")
    display_glossary_terms(search_string, guid,server, url, userid)