#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

A simple viewer for Information Solution Blueprints

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


def blueprint_list(
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
            title=f"Blueprints matching  {search_string} @ {time.asctime()}",
            style="bright_white on black",
            header_style="bright_white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"View Server '{server_name}' @ Platform - {platform_url}",
            expand=True,
        )
        table.add_column("Blueprint Name  /  Diagram Link", justify="center")
        table.add_column(
            "Qualified Name   /  GUID  /  Version",
            justify="center",
            width=38,
            no_wrap=False,
        )
        table.add_column("Description", justify="center")
        table.add_column("Solution Components", justify="center")

        blueprints = client.find_solution_blueprints(search_string)
        if isinstance(blueprints, list) is False:
            return "No Blueprints found"

        for bp in blueprints:
            bp_name = bp["properties"].get("displayName", "---")
            bp_qname = bp["properties"].get("qualifiedName", "---")
            bp_guid = bp["elementHeader"]["guid"]
            bp_desc = bp["properties"].get("description", "---")
            bp_unique_name = f"{bp_qname}\n\n--\n\n{bp_guid}"
            bp_mermaid = bp.get("mermaidGraph", "---")
            if bp_mermaid != "---":
                link = save_mermaid_html(
                    bp_name, bp_mermaid, f"{EGERIA_MERMAID_FOLDER}/blueprints"
                )
                link = f"file://:{link}"
                bp_mermaid = Text(link, style="blue link " + link)

            bp_mermaid_label = Text(f"{bp_name}\n\n--\n\n{bp_mermaid}")

            bp_components = bp.get("solutionComponents", [])
            comp_md = ""
            first_comp = True
            for component in bp_components:
                comp = component.get("solutionComponent", "")
                if isinstance(comp, dict) is False:
                    continue
                comp_props = comp.get("properties", {})
                comp_name = comp_props.get("displayName", "---")
                comp_description = comp_props.get("description", "---")
                comp_planned = comp_props["extendedProperties"].get(
                    "plannedDeployedImplementationType", "---"
                )
                comp_type = comp_props.get("solutionComponentType", "---")

                comp_actors = comp.get("actors", [])
                comp_actors_list = f"{len(comp_actors)}\n"
                for actor in comp_actors:
                    comp_actor_role = actor["relationshipProperties"].get("role", "---")
                    comp_actor_props = actor["relatedElement"].get("properties", {})
                    comp_actor_props_md = f"\n\t* Role: {comp_actor_role}\n"
                    for prop in comp_actor_props.keys():
                        comp_actor_props_md += f"\n\t\t* {prop}: {comp_actor_props[prop]}"
                    comp_actors_list += comp_actor_props_md
                if first_comp:
                    first_comp = False
                else:
                    comp_md += "\n\n---\n\n"
                comp_md += f"Solution Component {comp_name}\n\n"
                comp_md += f"* Type: {comp_type}\n"
                comp_md += f"* Description: {comp_description}\n"
                comp_md += f"* Planned Deployment: {comp_planned}\n"
                comp_md += f"* Actors: {comp_actors_list}\n"
            comp_out = Markdown(comp_md)
            table.add_row(bp_mermaid_label, bp_unique_name, bp_desc, comp_out)

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
        blueprint_list(search_string, server, url, userid, user_pass)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
