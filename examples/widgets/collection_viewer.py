#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

A simple viewer for collections - provide the root and we display the hierarchy

"""

import argparse

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


def collection_viewer(root: str, server_name: str, platform_url: str, user: str):
    """ A simple collection viewer"""
    def walk_collection_hierarchy(collection_client: CollectionManager, root_collection_name: str, tree: Tree) -> None:
        """Recursively build a Tree with collection contents."""
        members = collection_client.get_member_list(root_collection_name)
        if members:
            for member in members:

                style = ""
                text_collection_name = Text(f"[bold white] Name: {member['name']}", "")
                text_qualified_name = Text(f"* QualifiedName: {member['qualifiedName']}""yellow")
                text_guid = Text(f"* GUID: {member['guid']}", "green")
                text_collection_type = Text(f"* Collection Type: {member['collectionType']}", "cyan")
                text_description = Text(f"* Description: {member['description']}", "cyan")
                p = Panel.fit(f"[white]{text_collection_name}[green]\n{text_qualified_name}\n{text_guid}\n"
                              f"{text_collection_type}\n{text_description}")
                tt = tree.add(p, style=style)

                children = collection_client.get_collection_members(member['guid'])
                if type(children) is list:
                    branch = tt.add(f"[bold magenta]Members", style=style, guide_style=style)
                    walk_collection_hierarchy(collection_client, member['qualifiedName'], branch),

    try:
        tree = Tree(f"[bold bright green]{root}", guide_style="bold bright_blue")
        c_client = CollectionManager(server_name, platform_url,
                                     user_id=user)

        token = c_client.create_egeria_bearer_token(user, "secret")
        walk_collection_hierarchy(c_client, root, tree)
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

    root_collection = Prompt.ask("Enter the Root Collection to start from:", default="Digital Products Root")
    collection_viewer(root_collection, server, url, userid)
