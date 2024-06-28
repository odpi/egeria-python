#!/usr/bin/env python3
"""
SPDX-Lic
ense-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple display for glossary terms
"""

import argparse
import httpx
import json
import time

from rich import box
from rich import print
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
from rich.tree import Tree
from rich.json import JSON

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
    Client
)
from pyegeria import ProjectManager


def display_guid(guid: str, server: str, url: str, username: str):

    c = Client(server, url, user_id=username)
    url = (f"{url}/servers/{server}/open-metadata/repository-services/users/{username}/"
           f"instances/entity/{guid}")


    try:
        console = Console(width = 180)
        r = c.make_request("GET", url)
        e = r.json()['entity']
        p = e['properties']['instanceProperties']

        type_name = Text(f"Type is: {e['type']['typeDefName']}")
        metadataCollection = Text(f"Metadadata Collection: {e['metadataCollectionName']}")
        created = Text(f"Created at: {e['createTime']}")
        details = Text(f"Details: {json.dumps(p, indent=2)}")

        tree = Tree(f"[bold bright green]{guid}", guide_style="bold bright_blue")

        tree = tree.add(type_name)
        tree.add(metadataCollection)
        tree.add(created)
        tree.add(details)
        print(tree)

        c.close_session()

    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException, ValueError) as e:
        if type(e) is str:
            print(e)
        else:
            print_exception_response(e)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")

    # parser.add_argument("--sponsor", help="Name of sponsor to search")
    args = parser.parse_args()

    server = args.server if args.server is not None else "active-metadata-store"
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'erinoverview'

    guid = Prompt.ask("Enter the GUID to retrieve:", default=None)

    display_guid(guid, server, url, userid)