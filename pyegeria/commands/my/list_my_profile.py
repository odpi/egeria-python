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

from rich import box, print
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.markdown import Markdown

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria.my_profile_omvs import MyProfile

disable_ssl_warnings = True
EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("EGERIA_VIEW_SERVER", "view-server")
EGERIA_VIEW_SERVER_URL = os.environ.get(
    "EGERIA_VIEW_SERVER_URL", "https://localhost:9443"
)
EGERIA_INTEGRATION_DAEMON = os.environ.get("INTEGRATION_DAEMON", "integration-daemon")
EGERIA_INTEGRATION_DAEMON_URL = os.environ.get(
    "EGERIA_INTEGRATION_DAEMON_URL", "https://localhost:9443"
)
EGERIA_ADMIN_USER = os.environ.get("ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_JUPYTER = bool(os.environ.get("EGERIA_JUPYTER", "False"))
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "150"))


def display_my_profile(
    server: str,
    url: str,
    username: str,
    user_pass: str,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
):
    try:
        m_client = MyProfile(server, url, user_id=username, user_pwd=user_pass)
        token = m_client.create_egeria_bearer_token(username, user_pass)
        my_profiles = m_client.get_my_profile()
        if type(my_profiles) is str:
            print(f"No profiles found for {username}")
            sys.exit(1)

        console = Console(width=width, force_terminal=not jupyter, soft_wrap=True)

        profile_props = my_profiles.get("profileProperties", "---")
        name = profile_props["fullName"]

        tree = Tree(
            Panel(f"Profile of {name}", title="Personal Profile"),
            expanded=True,
            style="bright_white on black",
            guide_style="bold bright_blue",
        )

        profile_props_md = f"\n* GUID: {my_profiles['elementHeader']['guid']}\n"
        if type(profile_props) is dict:
            for key in profile_props.keys():
                if type(profile_props[key]) is str:
                    profile_props_md += f"* {key}: {profile_props[key]}\n"
                elif type(profile_props[key]) is dict:
                    p_md = "\n* Additional Details:\n"
                    for k in profile_props[key].keys():
                        p_md += f"\t* {k}: {profile_props[key][k]}\n"
                    profile_props_md += p_md
            t1 = tree.add(
                Panel(
                    Markdown(profile_props_md), title="Profile Properties", expand=False
                )
            )

        id_list_md = ""
        for identities in my_profiles["userIdentities"]:
            id_list_md += (
                f"* {identities['userIdentity']['properties']['userId']}\n"
                f"* {identities['userIdentity']['elementHeader']['guid']}\n"
            )
        t2 = tree.add(Panel(Markdown(id_list_md), title="Identities", expand=False))

        contact_methods = my_profiles["contactMethods"]
        for method in contact_methods:
            contact = method["properties"]
            contact_methods_md = ""
            for key in contact.keys():
                contact_methods_md += f"* {key}: {contact[key]}\n"
            t3 = tree.add(
                Panel(
                    Markdown(contact_methods_md), title="Contact Methods", expand=False
                )
            )

        my_roles = my_profiles["roles"]
        table = Table(
            title=f" Roles of {name}",
            show_lines=True,
            box=box.ROUNDED,
            expand=True,
        )
        table.add_column("Role Type")
        table.add_column("Role")
        table.add_column("Role GUID")
        for a_role in my_roles:
            my_role_props = a_role["properties"]
            role_type = my_role_props["typeName"]
            role = my_role_props.get("title", " ")
            role_guid = a_role["elementHeader"]["guid"]
            table.add_row(role_type, role, role_guid)
        t4 = tree.add(Panel(table, title="Roles", expand=False), expanded=True)

        print(tree)

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
    ) as e:
        print_exception_response(e)
    finally:
        m_client.close_session()


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

    display_my_profile(server, url, userid, user_pass)


if __name__ == "__main__":
    main()
