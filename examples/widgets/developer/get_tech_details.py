#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

A simple viewer for collections - provide the root and we display the hierarchy

"""
import os
import argparse
import asyncio
import nest_asyncio

from rich import print
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.tree import Tree
from rich.console import Console
from pyegeria import (UserNotAuthorizedException, PropertyServerException,
                      InvalidParameterException, AutomatedCuration)
from pyegeria._exceptions import (
    print_exception_response,
)
EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get('KAFKA_ENDPOINT', 'localhost:9092')
EGERIA_PLATFORM_URL = os.environ.get('EGERIA_PLATFORM_URL', 'https://localhost:9443')
EGERIA_VIEW_SERVER = os.environ.get('VIEW_SERVER', 'view-server')
EGERIA_VIEW_SERVER_URL = os.environ.get('EGERIA_VIEW_SERVER_URL', 'https://localhost:9443')
EGERIA_INTEGRATION_DAEMON = os.environ.get('INTEGRATION_DAEMON', 'integration-daemon')
EGERIA_ADMIN_USER = os.environ.get('ADMIN_USER', 'garygeeke')
EGERIA_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'secret')
EGERIA_USER = os.environ.get('EGERIA_USER', 'erinoverview')
EGERIA_USER_PASSWORD = os.environ.get('EGERIA_USER_PASSWORD', 'secret')

nest_asyncio.apply()
console = Console()
disable_ssl_warnings = True

def tech_viewer(tech: str, server_name:str, platform_url:str, user:str, user_password:str):

    def view_tech_details(a_client: AutomatedCuration, root_collection_name: str, tree: Tree) -> Tree:
        l2: Tree = None
        tech_details = a_client.get_technology_type_detail(tech)
        if (type(tech_details) is dict) and (len(tech_details)>0):
            name = tech_details.get('name','---')
            qualified_name = tech_details.get('qualifiedName',"---")
            category = tech_details.get('category','---')
            description = tech_details.get('description','---')

            style = ""
            l2 = tree.add(Text(f"Name: {name}", "bold red"))
            l2 = tree.add(Text(f"* QualifiedName: {qualified_name}","bold white"))
            l2 = tree.add(Text(f"* Category: {category}", "bold white"))
            l2 = tree.add(Text(f"* Technology Description: {description}", "bold white"))
            ext_ref = tech_details.get('externalReferences', None)

            if ext_ref is not None:
                uri = ext_ref[0]["properties"].get("uri", "---")
                # console.print(f" {type(ext_ref)}, {len(ext_ref)}")
                l2 = tree.add(Text(f'* URI: {uri}', "bold white"))

            resource_list = tech_details.get('resourceList',None)
            if resource_list:
                t_r = tree.add("Resource List[bold red]")
                for resource in resource_list:
                    resource_use = Text(f"[bold white]{resource.get('resourceUse','---')}", "")
                    resource_use_description = Text(f"[bold white]{resource.get('resourceUseDescription','---')}", "")
                    type_name = Text(f"[bold white]{resource['relatedElement']['type'].get('typeName','---')}", "")
                    unique_name = Text(f"[bold white]{resource['relatedElement'].get('uniqueName','---')}", "")
                    related_guid = Text(f"[bold white]{resource['relatedElement'].get('guid','---')}", "")
                    resource_text = (f"[bold red]Resource\n"
                                     f"[white]Resource use: {resource_use}[white]\nDescription: "
                                     f"{resource_use_description}\nType Name: {type_name}\n"
                                     f"[white]Unique Name: {unique_name}\n[white]Related GUID: {related_guid}\n")
                    p = Panel.fit(resource_text)
                    tt = t_r.add(p, style=style)

        else:
            tt = tree.add(f"Tech type {tech} was not found - please check the tech type name")

        return tt

    try:
        tree = Tree(f"{tech}", style = "bold bright_white on black", guide_style="bold bright_blue")
        a_client = AutomatedCuration(server_name, platform_url,
                                     user_id=user)

        token = a_client.create_egeria_bearer_token(user, user_password)
        view_tech_details(a_client,tech,tree)
        print(tree)

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException
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
        tech = Prompt.ask("Enter the Technology to start from:", default="PostgreSQL Server")
        tech_viewer(tech,server, url, userid, user_pass)
    except(KeyboardInterrupt):
        pass


if __name__ == "__main__":
    main()