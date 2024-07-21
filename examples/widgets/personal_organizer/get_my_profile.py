#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple display for my profile
"""
import os
import argparse
import time
import sys

from rich import box
from rich.console import Console
from rich.table import Table

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria.my_profile_omvs import MyProfile

disable_ssl_warnings = True
EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get('KAFKA_ENDPOINT', 'localhost:9092')
EGERIA_PLATFORM_URL = os.environ.get('EGERIA_PLATFORM_URL', 'https://localhost:9443')
EGERIA_VIEW_SERVER = os.environ.get('VIEW_SERVER', 'view-server')
EGERIA_VIEW_SERVER_URL = os.environ.get('EGERIA_VIEW_SERVER_URL', 'https://localhost:9443')
EGERIA_INTEGRATION_DAEMON = os.environ.get('INTEGRATION_DAEMON', 'integration-daemon')
EGERIA_INTEGRATION_DAEMON_URL = os.environ.get('EGERIA_INTEGRATION_DAEMON_URL', 'https://localhost:9443')
EGERIA_ADMIN_USER = os.environ.get('ADMIN_USER', 'garygeeke')
EGERIA_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'secret')
EGERIA_USER = os.environ.get('EGERIA_USER', 'erinoverview')
EGERIA_USER_PASSWORD = os.environ.get('EGERIA_USER_PASSWORD', 'secret')

def display_my_profiles(server: str, url: str, username: str, user_pass:str):

    m_client = MyProfile(server, url, user_id=username, user_pwd=user_pass)
    token = m_client.create_egeria_bearer_token(username, user_pass)
    my_profiles = m_client.get_my_profile()
    if type(my_profiles) is str:
        print(f"No profiles found for {username}")
        sys.exit(1)

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"My Profile Information {url} @ {time.asctime()}",
            # style = "black on grey66",
            header_style="white on dark_blue",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"My Profile from Server '{server}' @ Platform - {url}\n Press 'q' to Quit",
            expand=True
        )

        table.add_column("Name")
        table.add_column("Job Title")
        table.add_column("userId")
        table.add_column("myGUID")
        table.add_column("Role Type")
        table.add_column("Role")
        table.add_column("Role GUID")

        if len(my_profiles) == 0:
            name = " "
            job_title = " "
            user_id = " "
            my_guid = " "
            role_type = " "
            role = " "
            role_guid = " "
        else:
            name = my_profiles["profileProperties"]["fullName"]
            job_title = my_profiles["profileProperties"]["jobTitle"]
            id_list=" "
            for identities in my_profiles["userIdentities"]:
                id_list = f"{identities['userIdentity']['properties']['userId']} {id_list}"

            my_guid = my_profiles["elementHeader"]["guid"]

            my_roles = my_profiles["roles"]
            for a_role in my_roles:
                my_role_props = a_role["properties"]
                role_type = my_role_props["typeName"]
                role = my_role_props.get("title"," ")
                role_guid = a_role["elementHeader"]["guid"]
                table.add_row(
                    name, job_title, str(id_list), my_guid, role_type, role, role_guid
                )

        m_client.close_session()
        return table

    try:
        # with Live(generate_table(), refresh_per_second=4, screen=True) as live:
        #     while True:
        #         time.sleep(2)
        #         live.update(generate_table())
        console = Console()
        with console.pager():
            console.print(generate_table())


    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
        print_exception_response(e)
        assert e.related_http_code != "200", "Invalid parameters"

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

    display_my_profiles(server, url, userid, user_pass)

if __name__ == "__main__":
    main()