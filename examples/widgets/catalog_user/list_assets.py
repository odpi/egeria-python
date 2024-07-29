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

def display_assets(search_string: str, server: str, url: str, username: str, user_password: str, time_out: int = 60):

    g_client = AssetCatalog(server, url, username)
    token = g_client.create_egeria_bearer_token(username, user_password)


    def generate_table(search_string:str = 'Enter Your Tech Type') -> Table:
        """Make a new table."""
        table = Table(
            title=f"Assets containing the string  {search_string} @ {time.asctime()}",
            header_style="white on dark_blue",
            style="bold white on black",
            row_styles=["bold white on black"],
            title_style="bold white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"View Server '{server}' @ Platform - {url}",
            expand=True
        )
        table.add_column("Display Name")
        table.add_column("Type Name")
        table.add_column("GUID", no_wrap=True)
        table.add_column("Technology Type")
        # table.add_column("Qualified Name",max_width=15)
        table.add_column("Matching Elements")


        assets = g_client.find_assets_in_domain(search_string, starts_with=True,
                                             ends_with=False, ignore_case=True, page_size=100, time_out=time_out)
        if type(assets) is str:
            return table

        for element in assets:
            display_name = element.get("resourceName",'---')
            # qualified_name = element["qualifiedName"] # we decided that qualified name wasn't useful
            type_name = element["type"]["typeName"]
            tech_type = element.get("deployedImplementationType",'---')
            guid = element["guid"]
            #### We decided that path wasn't useful
            # path_name = element.get("extendedProperties", None)
            # if path_name:
            #     path = path_name.get("pathName"," ")
            # else:
            #     path = " "
            matches = element['matchingElements']
            match_md = ""

            match_tab = Table(expand=True)
            match_tab.add_column("Type Name")
            match_tab.add_column("GUID", no_wrap=True, width=36)
            match_tab.add_column("Properties")

            for match in matches:
                match_type_name = match['type']['typeName']
                matching_guid = match['guid']
                match_props = match['properties']
                match_details_md = ""
                for key in match_props.keys():
                    match_details_md += f"{key}: {match_props[key]}\n"

                match_tab.add_row(match_type_name, matching_guid, match_details_md)


            table.add_row(
                display_name, type_name,guid, tech_type, match_tab
            )

        g_client.close_session()
        return table

    try:
        # with Live(generate_table(), refresh_per_second=4, screen=True) as live:
        #     while True:
        #         time.sleep(2)
        #         live.update(generate_table())
        console = Console()
        with console.pager(styles=True):
            console.print(generate_table(search_string))


    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
        console.print_exception()



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    parser.add_argument("--time_out", help="Time Out")

    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    time_out = args.time_out if args.time_out is not None else 60
    try:
        search_string = Prompt.ask("Enter an asset search string:", default="")
        display_assets(search_string, server, url, userid, user_pass, time_out)
    except(KeyboardInterrupt):
        pass
if __name__ == "__main__":
    main()