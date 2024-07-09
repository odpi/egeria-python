#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

A simple viewer for collections - provide the root and we display the hierarchy

"""

import time
import argparse

from rich.box import Box
from rich.markdown import Markdown
from rich.prompt import Prompt

from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.tree import Tree
from rich.markdown import Markdown

from rich import print
from rich.console import Group
from rich.panel import Panel
from rich import box, align
from rich.layout import Layout
import rich
from pyegeria import (CollectionManager, UserNotAuthorizedException, PropertyServerException,
                      InvalidParameterException, AutomatedCuration)

disable_ssl_warnings = True

platform = "https://127.0.0.1:9443"
user = "erinoverview"
view_server = "view-server"


def tech_viewer(tech: str, server_name:str, platform_url:str, user:str):

    def view_tech_details(a_client: AutomatedCuration, root_collection_name: str, tree: Tree) -> Tree:
        l2: Tree = None
        tech_details = a_client.get_technology_type_detail(tech)
        if type(tech_details) is dict:
            style = ""
            l2 = tree.add(Text(f"Name: {tech_details.get('name',' ')}", "bold red"))
            l2 = tree.add(Text(f"* QualifiedName: {tech_details['qualifiedName']}","bold white"))
            l2 = tree.add(Text(f"* Category: {tech_details['category']}", "bold white"))
            l2 = tree.add(Text(f"* Technology Description: {tech_details['description']}", "bold white"))
            ext_ref = tech_details.get('externalReferences', None)
            if ext_ref is not None:
                l2 = tree.add(Text(f'* URI: {ext_ref[0]["properties"]["uri"]}', "bold white"))


            resource_list = tech_details.get('resourceList',None)
            if resource_list:
                t_r = tree.add("Resource List[bold red]")
                for resource in resource_list:
                    resource_use = Text(f"[bold white]{resource['resourceUse']}", "")
                    resource_use_description = Text(f"[bold white]{resource['resourceUseDescription']}", "")
                    type_name = Text(f"[bold white]{resource['relatedElement']['type']['typeName']}", "")
                    unique_name = Text(f"[bold white]{resource['relatedElement']['uniqueName']}", "")
                    related_guid = Text(f"[bold white]{resource['relatedElement']['guid']}", "")
                    resource_text = (f"[bold red]Resource\n"
                                     f"[white]Resource use: {resource_use}[white]\nDescription: "
                                     f"{resource_use_description}\nType Name: {type_name}\n"
                                     f"[white]Unique Name: {unique_name}\n[white]Related GUID: {related_guid}\n")
                    p = Panel.fit(resource_text)
                    tt = t_r.add(p, style=style)


            return tt


    try:
        tree = Tree(f"[bold bright green]{tech}", guide_style="bold bright_blue")
        a_client = AutomatedCuration(view_server, platform,
                                     user_id=user)

        token = a_client.create_egeria_bearer_token(user, "secret")
        view_tech_details(a_client,tech,tree)
        print(tree)

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException
    ) as e:
        print_exception_response(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    args = parser.parse_args()

    server = args.server if args.server is not None else "view-server"
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'erinoverview'

    tech = Prompt.ask("Enter the Technology to start from:", default="PostgreSQL Server")
    tech_viewer(tech,server, url, userid)
