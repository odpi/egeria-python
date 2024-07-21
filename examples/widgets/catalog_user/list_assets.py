#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple display for glossary terms
"""
import argparse
import os
import time

from rich import box
from rich.console import Console
from rich.prompt import Prompt
# import pyegeria.X_asset_catalog_omvs
from rich.table import Table

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
    AssetCatalog
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

disable_ssl_warnings = True

def display_assets(search_string: str, guid: str, server: str, url: str, username: str, user_password: str):

    g_client = AssetCatalog(server, url, username)
    token = g_client.create_egeria_bearer_token(username, user_password)


    def generate_table(search_string:str = 'Enter Your Tech Type') -> Table:
        """Make a new table."""
        table = Table(
            title=f"Asset Definitions contining the string  {search_string} @ {time.asctime()}",
            # style = "black on grey66",
            header_style="white on dark_blue",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"View Server '{server}' @ Platform - {url}",
            expand=True
        )
        table.add_column("Display Name")
        table.add_column("Type Name")
        table.add_column("GUID", no_wrap=True)
        table.add_column("Technology Type")
        table.add_column("Path")
        table.add_column("Qualified Name")


        assets = g_client.find_assets_in_domain(search_string, starts_with=True,
                                             ends_with=False, ignore_case=True, page_size=10)
        if type(assets) is str:
            return table

        for element in assets:
            display_name = element.get("resourceName",'---')
            qualified_name = element["qualifiedName"]
            type_name = element["type"]["typeName"]
            tech_type = element.get("deployedImplementationType",'---')
            guid = element["guid"]
            path_name = element.get("extendedProperties", None)
            if path_name:
                path = path_name.get("pathName"," ")
            else:
                path = " "



            table.add_row(
                display_name, type_name,guid, tech_type, path, qualified_name
            )

        g_client.close_session()
        return table

    try:
        # with Live(generate_table(), refresh_per_second=4, screen=True) as live:
        #     while True:
        #         time.sleep(2)
        #         live.update(generate_table())
        console = Console()
        with console.pager():
            console.print(generate_table(search_string))


    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
        console.print_exception()



def main():
    sus_guid = "f9b78b26-6025-43fa-9299-a905cc6d1575"
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")

    parser.add_argument("--guid", help="GUID of glossary to search")
    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    guid = args.guid if args.guid is not None else None

    search_string = Prompt.ask("Enter a search string:", default="")
    display_assets(search_string, guid,server, url, userid, user_pass)

if __name__ == "__main__":
    main()