#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

A simple viewer for Information Solution Roles

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
    ProjectManager,
    PropertyServerException,
    UserNotAuthorizedException,
    save_mermaid_html,
)
from pyegeria._exceptions import print_exception_response
from pyegeria.mermaid_utilities import EGERIA_MERMAID_FOLDER
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


def solution_role_list(
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
            title=f"Solution Roles matching  {search_string} @ {time.asctime()}",
            style="bright_white on black",
            header_style="bright_white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"View Server '{server_name}' @ Platform - {platform_url}",
            expand=True,
        )
        table.add_column("Role Id  /  Diagram Link", justify="center", no_wrap=False)
        table.add_column("Title / Type / Scope / HeadCount", justify="center")
        table.add_column(
            "Qualified Name   /  GUID", justify="center", width=38, no_wrap=False
        )
        table.add_column("Description / HeadCount", justify="center")
        table.add_column("Solution Components", justify="center")

        roles = client.find_solution_roles(search_string)
        if isinstance(roles, list) is False:
            return "No Roles found"

        for role in roles:
            role_name = role["properties"].get("roleId", "---")

            role_title = role["properties"].get("title", "---")
            role_scope = role["properties"].get("scope", "---")
            role_type = role["properties"].get("typeName", "---")
            role_headcount = (
                role["properties"].get("extendedProperties", {}).get("headCount", "---")
            )
            role_info = (
                f"Title: {role_title}\n\n--\n\nType: {role_type}\n\n--\n\n"
                f"Scope: {role_scope}\n\n--\n\nHeadCount: {role_headcount}"
            )

            role_qname = role["properties"].get("qualifiedName", "---")
            role_guid = role["elementHeader"]["guid"]
            role_unique_name = f"{role_qname}\n\n--\n\n{role_guid}"

            role_desc = role["properties"].get("description", "---")

            role_mermaid = role.get("mermaidGraph", "---")
            if role_mermaid != "---":
                link = save_mermaid_html(
                    role_name, role_mermaid, f"{EGERIA_MERMAID_FOLDER}/roles"
                )
                link = f"file://:{link}"
                role_mermaid = Text(link, style="blue link " + link)

            role_mermaid_label = Text(f"{role_name}\n\n--\n\n{role_mermaid}")

            role_components = role.get("solutionComponents", [])
            comp_props_md = ""
            first_comp = True
            for component in role_components:
                if first_comp:
                    first_comp = False
                else:
                    comp_props_md += "\n\n---\n\n"
                comp = component.get("relatedElement", "")
                if isinstance(comp, dict) is False:
                    continue
                comp_props = comp.get("properties", {})

                for prop in comp_props.keys():
                    comp_props_md += f"* **{prop}**: {comp_props[prop]}\n"



            comp_props_out = Markdown(comp_props_md)
            table.add_row(
                role_mermaid_label,
                role_info,
                role_unique_name,
                role_desc,
                comp_props_out,
            )

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
        solution_role_list(search_string, server, url, userid, user_pass)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
