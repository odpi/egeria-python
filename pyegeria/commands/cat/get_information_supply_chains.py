#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

A simple viewer for Information Supply Chains

"""

import argparse
import os
from datetime import time

from rich import print, box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.tree import Tree
from pyegeria.solution_architect_omvs import SolutionArchitect
from pyegeria import (
    ProjectManager,
    UserNotAuthorizedException,
    PropertyServerException,
    InvalidParameterException,
    )

from pyegeria._exceptions import (
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
EGERIA_INTEGRATION_DAEMON = os.environ.get("INTEGRATION_DAEMON", "integration-daemon")
EGERIA_ADMIN_USER = os.environ.get("ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_JUPYTER = bool(os.environ.get("EGERIA_JUPYTER", "False"))
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "200"))


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

    def display_supply_chains(supply_chains: list[dict] ) -> Table:
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
        table.add_column("Qualified Name / GUID", width=38, no_wrap=True)
        table.add_column("Purpose")
        table.add_column("Scope")
        table.add_column("Description")

        for sc in supply_chains:
            sc_name = sc["properties"].get("displayName", '---')
            sc_qname = sc["elementHeader"]["qualifiedName"]
            sc_guid = sc["elementHeader"]["guid"]
            sc_purpose = sc["properties"].get("purposes",'---')
            sc_scope = sc["properties"].get("scope",'---')
            sc_desc = sc["properties"].get("description",'---')
            sc_unique_name = f"\t{sc_qname}\n\t/\n\t{sc_guid}"
            table.add_row(sc_name, sc_unique_name, sc_purpose, sc_scope, sc_desc)

        return table


    def walk_project_hierarchy(
        project_client: ProjectManager,
        project_name: str,
        tree: Tree,
        root: bool = False,
    ) -> None:
        """Recursively build a Tree with collection contents."""
        t = None
        style = "bright_white on black"

        project = project_client.get_projects_by_name(project_name)
        if type(project) is list:
            proj_guid = project[0]["elementHeader"]["guid"]
            proj_props = project[0]["properties"]

            proj_type = proj_props.get("typeName", "---")
            proj_unique = proj_props.get("qualifiedName", "---")
            proj_identifier = proj_props.get("identifier", "---")
            proj_name = proj_props.get("name", "---")
            proj_desc = proj_props.get("description", "---")
            proj_status = proj_props.get("projectStatus", "---")
            proj_priority = proj_props.get("priority", "---")
            proj_start = proj_props.get("startDate", "---")[:-10]
            proj_props_md = (
                f"* Name: {proj_name}\n"
                f"* Identifier: {proj_identifier}\n"
                f"* Type: {proj_type}\n"
                f"* Status: {proj_status}\n"
                f"* priority: {proj_priority}\n"
                f"* Start:    {proj_start}\n"
                f"* Description: {proj_desc}\n"
                f"* GUID: {proj_guid}"
            )
        else:
            return

        team = project_client.get_project_team(proj_guid)
        member_md = ""
        if type(team) is list:
            for member in team:
                member_guid = member["member"]["guid"]
                member_unique = member["member"]["uniqueName"]
                member_md += f"* Member Unique Name: {member_unique}\n* Member GUID: {member_guid}"
            proj_props_md += f"\n### Team Members\n {member_md}"

        proj_props_out = Markdown(proj_props_md)
        p = Panel.fit(proj_props_out, style=style, title=project_name)
        t = tree.add(p)

        linked_projects = project_client.get_linked_projects(proj_guid)
        if type(linked_projects) is list:
            for proj in linked_projects:
                child_md = ""
                child_guid = proj["elementHeader"]["guid"]
                child_name = proj["properties"]["name"]
                relationship = proj["relatedElement"]["relationshipHeader"]["type"][
                    "typeName"
                ]
                if relationship != "ProjectDependency":
                    continue
                walk_project_hierarchy(project_client, child_name, t)

        else:
            return t

    try:
        console = Console(width=width, force_terminal=not jupyter)
        tree = Tree(
            f"[bold bright green on black]Supply Chains containing: {search_string}", guide_style="bold bright_blue"
        )
        client = SolutionArchitect(server_name, platform_url, user, user_password)

        token = client.create_egeria_bearer_token()

        sc = client.find_all_information_supply_chains(search_string, start_from=0)

        if (isinstance(sc, list)):
            t = tree.add(display_supply_chains(sc))
        else:
            t = tree.add(type(sc))
        # walk_project_hierarchy(p_client, root, tree, root=True)
        print(tree)

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
        search_string = Prompt.ask(
            "Enter a search string:", default="*"
        )
        supply_chain_viewer(search_string, server, url, userid, user_pass)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
