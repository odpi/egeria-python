#!/usr/bin/env python3
"""
SPDX-Lic
ense-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple display for glossary terms
"""
import os
import argparse
import json

from rich import print
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
from rich.tree import Tree
from rich.panel import Panel

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
    Client
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


def display_guid(guid: str, server: str, url: str, username: str, user_password: str):

    c = Client(server, url, user_id=username)
    url = (f"{url}/servers/{server}/open-metadata/repository-services/users/{username}/"
           f"instances/entity/{guid}")


    try:
        console = Console(width = 160, style="bold white on black")
        r = c.make_request("GET", url)
        if r.status_code == 200:
            pass
        e = r.json()['entity']
        p = e['properties']['instanceProperties']

        type_name = Text(f"Type is: {e['type']['typeDefName']}")
        metadataCollection = Text(f"Metadadata Collection: {e['metadataCollectionName']}")
        created = Text(f"Created at: {e['createTime']}")
        details = Text(f"Details: {json.dumps(p, indent=2)}")

        tree = Tree(f"{guid}", style = "bold bright_white on black", guide_style="bold bright_blue")

        tree = tree.add(type_name)
        tree.add(metadataCollection)
        tree.add(created)
        tree.add(Panel(details,title="Element Details", expand=False))
        print(tree)

        c.close_session()

    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException, ValueError) as e:
        if type(e) is str:
           console.print_exception()
        else:
            console.print(f"\n Looks like the GUID isn't known...\n")

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")

    # parser.add_argument("--sponsor", help="Name of sponsor to search")
    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_METADATA_STORE
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD

    try:
        guid = Prompt.ask("Enter the GUID to retrieve", default=None)
        display_guid(guid, server, url, userid, user_pass)
    except (KeyboardInterrupt):
        pass
if __name__ == "__main__":
    main()