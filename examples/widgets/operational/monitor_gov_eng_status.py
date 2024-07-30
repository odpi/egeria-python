#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple status display for Governance Actions
"""
import os
import time
import json
import argparse


from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from rich.table import Table
from rich.live import Live
from rich import box
from rich.console import Console


from pyegeria.server_operations import ServerOps
EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get('KAFKA_ENDPOINT', 'localhost:9092')
EGERIA_PLATFORM_URL = os.environ.get('EGERIA_PLATFORM_URL', 'https://localhost:9443')
EGERIA_VIEW_SERVER = os.environ.get('VIEW_SERVER', 'view-server')
EGERIA_VIEW_SERVER_URL = os.environ.get('EGERIA_VIEW_SERVER_URL', 'https://localhost:9443')
EGERIA_INTEGRATION_DAEMON = os.environ.get('INTEGRATION_DAEMON', 'integration-daemon')
EGERIA_ENGINE_HOST = os.environ.get('INTEGRATION_ENGINE_HOST', 'engine-host')
EGERIA_ADMIN_USER = os.environ.get('ADMIN_USER', 'garygeeke')
EGERIA_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'secret')
EGERIA_USER = os.environ.get('EGERIA_USER', 'erinoverview')
EGERIA_USER_PASSWORD = os.environ.get('EGERIA_USER_PASSWORD', 'secret')

disable_ssl_warnings = True



def display_gov_eng_status(server: str , url: str, username: str, user_pass:str, paging:bool):
    server_name = server
    s_client = ServerOps(server_name, url, username, user_pass)

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Governance Engine Status @ {time.asctime()}",
            style="bold white on black",
            row_styles=["bold white on black"],
            header_style="white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Server: '{server_name}' running on {url}",
            expand=True
        )
        # table.footer: f"Server {server_name} on Platform {good_platform1_url}"
        table.add_column("Gov Engine")
        table.add_column("Gov Engine Type")
        table.add_column("Gov Engine Desc")
        table.add_column("Engine Status")
        table.add_column("Request Types")

        gov_eng_status = s_client.get_governance_engine_summaries()
        for engine in gov_eng_status:
            gov_eng = engine["governanceEngineName"]
            eng_type = engine["governanceEngineTypeName"]

            eng_desc = engine["governanceEngineDescription"]
            eng_req_type = json.dumps(engine["governanceRequestTypes"], indent = 2)
            status = engine["governanceEngineStatus"]
            if status in ("RUNNING"):
                eng_status = f"[green]{status}"
            elif status in ("FAILED"):
                eng_status = f"[red]{status}"
            else: eng_status = f"[yellow]{status}"

            table.add_row(
                gov_eng, eng_type, eng_desc, eng_status,eng_req_type
            )

        table.caption = f"Server {server_name} running on {url}"
        return table

    try:
        if paging is True:
            console = Console()
            with console.pager():
                console.print(generate_table())
        else:
            with Live(generate_table(), refresh_per_second=1, screen=True, vertical_overflow="visible") as live:
                while True:
                    time.sleep(2)
                    live.update(generate_table())

    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
        print_exception_response(e)

    except KeyboardInterrupt:
        pass

    finally:
        s_client.close_session()


def main_live():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_ENGINE_HOST
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    display_gov_eng_status(server=server, url=url, username=userid, user_pass=user_pass, paging=False)

def main_paging():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_ENGINE_HOST
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    display_gov_eng_status(server=server, url=url, username=userid, user_pass=user_pass, paging=True)



if __name__ == "__main__":
    main_live()


if __name__ == "__main_paging__":
    main_paging()