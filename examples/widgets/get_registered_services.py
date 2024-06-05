#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

A simple widget to retrieve the registered services.

"""

import argparse
import sys
import time

from rich import box
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    RegisteredInfo,
)


def display_registered_svcs(service: str, server: str , url: str,
                            username: str, password: str ):
    """ Display the registered services list
    Parameters
    ----------
    service : str, optional
        The type of service to display information for. Default is "help".

    server : str, optional
        The server to connect to. Default is `default_server`.

    url : str, optional
        The platform URL. Default is `default_platform`.

    username : str, optional
        The username for authentication. Default is `default_user`.

    password : str, optional
        The password for authentication. Default is `default_password`.
    """
    def generate_table(svc_list) -> Table:
        """Make a new table."""
        table = Table(
            title=f"Technology Types for: {url} @ {time.asctime()}",
            # style = "black on grey66",
            header_style="white on dark_blue",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Registered Services from Server '{server}' @ Platform - {url}",
            expand=True
        )
        table.add_column("Service Id")
        table.add_column("Service Name")
        table.add_column("Service  Development Status")
        table.add_column("URL Marker")
        table.add_column("Description")
        table.add_column("Wiki")
        table.add_column("Server Type")
        table.add_column("Partner Service Name")
        table.add_column("Partner Service Type")

        if type(svc_list) is list:
            for svc in svc_list:
                svc_id = str(svc.get("serviceId", " "))
                svc_name = svc.get("serviceName", "b")
                svc_dev_status = svc.get("serviceDevelopmentStatus", " ")
                svc_url_marker = svc.get("serviceUrlMarker", " ")
                svc_description = svc.get("serviceDescription", " ")
                svc_wiki = svc.get("serviceWiki", " ")
                svc_partner_svc_name = svc.get("partnerServiceName", " ")
                svc_partner_svc_type = svc.get("partnerServiceType", " ")

                table.add_row(
                    svc_id, svc_name, svc_dev_status, svc_url_marker, svc_description, svc_wiki,
                    svc_partner_svc_name, svc_partner_svc_type
                )
            return table
        elif type(svc_list) is str:
            help = """
            The kinds of services that you can get more information include:
                all.....................lists all registered services
                access-services.........lists all registered access services
                common-services.........lists all registered common services
                engine-services.........lists all registered engine services
                governance-services.....lists all registered governance services
                integration-services....lists all registered integration services
                view-services...........lists all registered view services
                
                Pass in a parameter from the left-hand column into the function to 
                get more details on the specified service category.
            """
            console.print(help)

        else:
            print("Unknown service type")
            sys.exit(1)

    console = Console()
    try:
        a_client = RegisteredInfo(server, url, username)
        # token = a_client.create_egeria_bearer_token(username, password)
        svc_list = a_client.list_registered_svcs(service)

        with console.pager():
            console.print(generate_table(svc_list))

    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
        console.print_exception(show_locals=True)
    finally:
        a_client.close_session()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="Password")

    args = parser.parse_args()

    server = args.server if args.server is not None else "active-metadata-store"
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'garygeeke'
    password = args.password if args.password is not None else 'secret'

    svc_kind = Prompt.ask("Enter the service type you are searching for:", default="all")

    display_registered_svcs(svc_kind, server, url, userid, password=password)
