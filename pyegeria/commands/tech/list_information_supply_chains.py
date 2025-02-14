#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

A simple viewer for Information Supply Chains

"""

import argparse
import os
import time

from rich import box, print
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    save_mermaid_graph,
    save_mermaid_html,
)
from pyegeria._exceptions import print_exception_response
from pyegeria.solution_architect_omvs import SolutionArchitect

disable_ssl_warnings = True
EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("EGERIA_VIEW_SERVER", "qs-view-server")
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
EGERIA_MERMAID_FOLDER = os.environ.get("EGERIA_MERMAID_FOLDER", "work/mermaid_graphs")


def supply_chain_viewer(
    search_string: str,
    server_name: str,
    platform_url: str,
    user: str,
    user_password: str,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
    timeout: int = 30,
):
    """A Supply Chain viewer"""
    client = SolutionArchitect(server_name, platform_url, user, user_password)
    token = client.create_egeria_bearer_token()

    def generate_table() -> Table | str:
        table = Table(
            title=f"Supply Chains matching  {search_string} @ {time.asctime()}",
            style="bright_white on black",
            header_style="bright_white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"View Server '{server_name}' @ Platform - {platform_url}",
            expand=True,
        )
        table.add_column("Supply Chain Name")
        table.add_column("Qualified Name \n/\n GUID", justify = 'center', width=38, no_wrap=False)
        table.add_column("Purposes")
        table.add_column("Scope\n/\n Mermaid Link", justify = 'center')
        table.add_column("Description", justify = 'center')
        table.add_column("Segments", justify = 'center')

        supply_chains = client.find_information_supply_chains(search_string)
        if isinstance(supply_chains, list) is False:
            return "No Supply Chains found"

        for sc in supply_chains:
            sc_name = sc["properties"].get("displayName", "---")
            sc_qname = sc["properties"].get("qualifiedName", "---")
            sc_guid = sc["elementHeader"]["guid"]
            sc_purpose = sc["properties"].get("purposes", "---")
            if isinstance(sc_purpose, list):
                sc_purpose_str = "\n* ".join(sc_purpose)
            else:
                sc_purpose_str = sc_purpose
            sc_scope = sc["properties"].get("scope", "---")
            sc_desc = sc["properties"].get("description", "---")
            sc_unique_name = f"{sc_qname}\n\n\t\t/\n\n{sc_guid}"
            sc_mermaid = sc.get("mermaidGraph", "---")
            if sc_mermaid != "---":
                link = save_mermaid_html(
                    sc_name, sc_mermaid, f"{EGERIA_MERMAID_FOLDER}/supply-chains"
                )
                sc_mermaid_link = Text(f"file://:{link}", style="blue link " + link)
                sc_scope = Text(f"{sc_scope}\n\n/\n\n{sc_mermaid_link}",  justify = "center")


            sc_segments = sc.get("segments", "---")
            if sc_segments != "---":
                first_segment = True
                sc_segments_md = ""
                for segment in sc_segments:
                    seg_prop = segment['properties']
                    if first_segment:
                        first_segment = False
                    else:
                        sc_segments_md += "----\n\n"  # add a seperator from previous segment

                    for key in seg_prop.keys():
                        sc_segments_md += f"* **{key}**: {seg_prop[key]}\n"
                sc_segments_md = Markdown(sc_segments_md)
            else:
                sc_segments_md = "---"

            table.add_row(sc_name, sc_unique_name, sc_purpose_str, sc_scope, sc_desc, sc_segments_md)

        return table

    try:
        console = Console(width=width, force_terminal=not jupyter)
        with console.pager():
            console.print(generate_table())

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
    ) as e:
        print_exception_response(e)


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
        search_string = Prompt.ask("Enter a search string:", default="*")
        supply_chain_viewer(search_string, server, url, userid, user_pass)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
