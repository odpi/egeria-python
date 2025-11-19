#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

A simple viewer for collections - provide the root and we display the hierarchy

"""
import argparse
import os
import sys

from rich import print
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.tree import Tree

from pyegeria import (
    AutomatedCuration,
    PyegeriaException,
    print_basic_exception,
    settings,
    config_logging
)

EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")

app_config = settings.Environment
config_logging()
console = Console(width = app_config.console_width)



def tech_details_viewer(
    tech: str,
    server_name: str,
    platform_url: str,
    user: str,
    user_password: str,
    jupyter: bool = app_config.egeria_jupyter,
    width: int = app_config.console_width,
):
    console = Console(width=width, force_terminal=not jupyter)

    def view_tech_details(
        a_client: AutomatedCuration, root_collection_name: str, tree: Tree
    ) -> Tree:
        l2: Tree = None
        tech_details = a_client.get_tech_type_detail(tech)
        if (type(tech_details) is dict) and (len(tech_details) > 0):
            name = tech_details.get("displayName", "---")
            qualified_name = tech_details.get("qualifiedName", "---")
            category = tech_details.get("category", "---")
            description = tech_details.get("description", "---")

            style = "bold bright_white on black"

            bas_md = f"* **Name**: {name}\n"
            bas_md += f"* **QualifiedName**: {qualified_name}\n"
            bas_md += f"* **Category**: {category}\n"
            bas_md += f"* **Technology Description**: {description}\n"

            bas_out = Markdown(bas_md)

            l2 = tree.add(Panel(bas_out))
            ext_ref = tech_details.get("externalReferences", None)

            if ext_ref is not None:
                uri = ext_ref[0]["properties"].get("uri", "---")
                # console.print(f" {type(ext_ref)}, {len(ext_ref)}")
                l2 = tree.add(Panel(Markdown(f"* URI: {uri}", style)))

            resource_list = tech_details.get("resourceList", None)
            if resource_list:
                t_r = tree.add(Panel("Resource List[bold red]"))
                for resource in resource_list:
                    resource_use = Text(
                        f"[bold bright_white]{resource.get('resourceUse', '---')}"
                    )
                    resource_use_description = Text(
                        f"[bold bright_white]{resource.get('description', '---')}"
                    )
                    type_name = Text(
                        f"[bold bright_white]{resource['relatedElement']['elementHeader']['type'].get('typeName', '---')}"
                    )
                    unique_name = Text(
                        f"[bold bright_white]{resource['relatedElement']['properties'].get('qualifiedName', '---')}"
                    )
                    related_guid = Text(
                        f"[bold bright_white]{resource['relatedElement']['elementHeader'].get('guid', '---')}"
                    )
                    resource_text = (
                        f"[bold red]Resource\n"
                        f"[white]Resource use: {resource_use}[white]\nDescription: "
                        f"{resource_use_description}\n[white]Type Name: {type_name}\n"
                        f"[white]Unique Name: {unique_name}\n[white]Related GUID: {related_guid}\n"
                    )
                    p = Panel.fit(resource_text)
                    tt = t_r.add(p, style=style)
            else:
                tt = tree.add(Panel(f"Resource details for {tech} where not found"))

        else:
            tt = tree.add(
                Panel(
                    f"Tech type {tech} was not found - please check the tech type name"
                )
            )

        return tt

    try:
        tree = Tree(
            f"{tech}",
            style="bold bright_white on black",
            guide_style="bold bright_blue",
        )
        a_client = AutomatedCuration(server_name, platform_url, user_id=user)

        token = a_client.create_egeria_bearer_token(user, user_password)
        view_tech_details(a_client, tech, tree)
        print(tree)

    except (
        PyegeriaException,
    ) as e:
        print_basic_exception(e)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    args = parser.parse_args()

    server = args.server if args.server is not None else app_config.egeria_view_server
    url = args.url if args.url is not None else app_config.egeria_view_server_url
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    try:
        tech = Prompt.ask(
            "Enter the Technology to start from:", default="PostgreSQL Server"
        )
        tech_details_viewer(tech, server, url, userid, user_pass)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
