#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple status display for Governance Actions
"""

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
from rich import console

from pyegeria.server_operations import ServerOps

disable_ssl_warnings = True

good_platform1_url = "https://127.0.0.1:9443"
good_platform2_url = "https://egeria.pdr-associates.com:7443"
bad_platform1_url = "https://localhost:9443"

# good_platform1_url = "https://127.0.0.1:30080"
# good_platform2_url = "https://127.0.0.1:30081"
# bad_platform1_url = "https://localhost:9443"

good_user_1 = "garygeeke"
good_user_2 = "erinoverview"
bad_user_1 = "eviledna"
bad_user_2 = ""

good_server_1 = "active-metadata-store"
good_server_2 = "simple-metadata-store"
good_server_3 = "engine-host"
good_server_4 = "engine-host"
bad_server_1 = "coco"
bad_server_2 = ""


def display_gov_actions_status(server: str = good_server_3, url: str = good_platform1_url, username: str = good_user_1):
    server_name = server
    s_client = ServerOps(server_name, url, username)

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"Governance Engine Status @ {time.asctime()}",
            # style = "black on grey66",
            header_style="white on dark_blue",
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
        with Live(generate_table(), refresh_per_second=1, screen=True, vertical_overflow="visible") as live:
            while True:
                time.sleep(2)
                live.update(generate_table())

    except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
        print_exception_response(e)
        assert e.related_http_code != "200", "Invalid parameters"

    finally:
        s_client.close_session()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    args = parser.parse_args()

    server = args.server if args.server is not None else "engine-host"
    url = args.url if args.url is not None else "https://localhost:9443"
    userid = args.userid if args.userid is not None else 'garygeeke'
    display_gov_actions_status(server=server, url=url, username=userid)
