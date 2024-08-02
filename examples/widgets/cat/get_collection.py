#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

A simple viewer for collections - provide the root and we display the hierarchy

"""

import argparse
import os
from rich import print
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.tree import Tree

from pyegeria import CollectionManager, UserNotAuthorizedException, PropertyServerException, InvalidParameterException
from pyegeria._exceptions import (
    print_exception_response,
)

disable_ssl_warnings = True
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
EGERIA_JUPYTER = bool(os.environ.get('EGERIA_JUPYTER', 'False'))
EGERIA_WIDTH = int(os.environ.get('EGERIA_WIDTH', '200'))

def collection_viewer(root: str, server_name: str, platform_url: str, user: str, user_password: str,
                      jupyter:bool=EGERIA_JUPYTER, width:int = EGERIA_WIDTH):
    """ A simple collection viewer"""
    def walk_collection_hierarchy(collection_client: CollectionManager, root_collection_name: str, tree: Tree) -> None:
        """Recursively build a Tree with collection contents."""
        members = collection_client.get_member_list(root_collection_name)
        if members:
            for member in members:
                style = "bold white on black"
                text_collection_name = Text(f"[bold white on black]Name: {member['name']}", style=style)
                text_qualified_name = Text(f"* QualifiedName: {member['qualifiedName']}")
                text_guid = Text(f"* GUID: {member['guid']}", "green")
                text_collection_type = Text(f"* Collection Type: {member['collectionType']}")
                text_description = Text(f"* Description: {member['description']}")
                p = Panel.fit(f"{text_collection_name}[green]\n{text_qualified_name}\n{text_guid}\n"
                              f"{text_collection_type}\n{text_description}")
                tt = tree.add(p, style=style)

                children = collection_client.get_collection_members(member['guid'])
                if type(children) is list:
                    branch = tt.add(f"[bold magenta on black]Members", style=style, guide_style=style)
                    walk_collection_hierarchy(collection_client, member['qualifiedName'], branch),
        else:
            tt = tree.add(f"[bold magenta on black]No collections match {root_collection_name}")
    try:
        tree = Tree(f"[bold bright green on black]{root}",guide_style="bold bright_blue")
        c_client = CollectionManager(server_name, platform_url,
                                     user_id=user)

        token = c_client.create_egeria_bearer_token(user, user_password)
        walk_collection_hierarchy(c_client, root, tree)
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
        root_collection = Prompt.ask("Enter the Root Collection to start from:", default="Root Sustainability Collection")
        collection_viewer(root_collection, server, url, userid, user_pass)
    except (KeyboardInterrupt):
        pass
if __name__ == "__main__":
    main()