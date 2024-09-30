#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple status display for Governance Actions
"""
import argparse
import os
import time

from rich import box
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.table import Table

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    EgeriaTech,
)

EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("VIEW_SERVER", "view-server")
EGERIA_VIEW_SERVER_URL = os.environ.get(
    "EGERIA_VIEW_SERVER_URL", "https://localhost:9443"
)
EGERIA_INTEGRATION_DAEMON = os.environ.get(
    "EGERIA_INTEGRATION_DAEMON", "integration-daemon"
)
EGERIA_ENGINE_HOST = os.environ.get("EGERIA_ENGINE_HOST", "engine-host")
EGERIA_ENGINE_HOST_URL = os.environ.get(
    "EGERIA_ENGINE_HOST_URL", "https://localhost:9443"
)
EGERIA_ADMIN_USER = os.environ.get("EGERIA_ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("EGERIA_ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_JUPYTER = bool(os.environ.get("EGERIA_JUPYTER", "False"))
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "200"))


disable_ssl_warnings = True


def display_gov_eng_status(
    engine_host: str,
    view_server: str,
    url: str,
    username: str,
    user_pass: str,
    paging: bool,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
):
    console = Console(width=EGERIA_WIDTH)

    s_client = EgeriaTech(view_server, url, username, user_pass)
    token = s_client.create_egeria_bearer_token()

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
            caption=f"Server: '{engine_host}' running on {url}",
            expand=True,
        )
        # table.footer: f"Server {view_server} on Platform {good_platform1_url}"
        table.add_column("Gov Engine")
        table.add_column("Gov Engine Type")
        table.add_column("Gov Engine Desc")
        table.add_column("Engine Status")
        table.add_column("Request Types")

        eng_host_guid = s_client.get_guid_for_name(engine_host)
        gov_eng_status = s_client.get_server_report(eng_host_guid)
        eng_summaries = gov_eng_status["governanceEngineSummaries"]
        sorted_gov_eng_status = sorted(
            eng_summaries, key=lambda k: k.get("governanceEngineName", " ")
        )
        for engine in sorted_gov_eng_status:
            gov_eng = engine["governanceEngineName"]
            eng_type = engine.get("governanceEngineTypeName", " ")

            eng_desc = engine.get("governanceEngineDescription", " ")
            eng_req_types = engine.get("governanceRequestTypes", " ")
            eng_req_type_md = " "
            if type(eng_req_types) is list:
                for i in eng_req_types:
                    eng_req_type_md += f"* {i}\n"
                eng_req_type_out = Markdown(eng_req_type_md)
            else:
                eng_req_type_out = " "
            status = engine["governanceEngineStatus"]
            if status in ("RUNNING"):
                eng_status = f"[green]{status}"
            elif status in ("FAILED"):
                eng_status = f"[red]{status}"
            else:
                eng_status = f"[yellow]{status}"

            table.add_row(gov_eng, eng_type, eng_desc, eng_status, eng_req_type_out)

        table.caption = f"Server {engine_host} running on {url}"
        return table

    try:
        if paging is True:
            console = Console(width=width, force_terminal=not jupyter)
            with console.pager():
                console.print(generate_table())
        else:
            with Live(
                generate_table(),
                refresh_per_second=1,
                screen=True,
                vertical_overflow="visible",
            ) as live:
                while True:
                    time.sleep(2)
                    live.update(generate_table())

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
    ) as e:
        console.print_exception(show_locals=True)

    except KeyboardInterrupt:
        pass

    finally:
        s_client.close_session()


def main_live():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--engine_host", help="Name of the server to display status for"
    )
    parser.add_argument("--view_server", help="Name of the view server to use")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    parser.add_argument("--paging", help="Paging")
    args = parser.parse_args()

    engine_host = (
        args.engine_host if args.engine_host is not None else EGERIA_ENGINE_HOST
    )
    view_server = (
        args.view_server if args.view_server is not None else EGERIA_VIEW_SERVER
    )
    url = args.url if args.url is not None else EGERIA_ENGINE_HOST_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    paging = args.paging if args.paging is not None else False
    display_gov_eng_status(engine_host, view_server, url, userid, user_pass, paging)


def main_paging():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--engine_host", help="Name of the engine host to display status for"
    )
    parser.add_argument("--view_server", help="Name of the view server to use")
    parser.add_argument("--url", help="URL of Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    args = parser.parse_args()

    engine_host = (
        args.engine_host if args.engine_host is not None else EGERIA_ENGINE_HOST
    )
    view_server = (
        args.view_server if args.view_server is not None else EGERIA_VIEW_SERVER
    )
    url = args.url if args.url is not None else EGERIA_VIEW_SERVER_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD

    display_gov_eng_status(
        engine_host, view_server, url, userid, user_pass, paging=True
    )


if __name__ == "__main__":
    main_live()

if __name__ == "__main_paging__":
    main_paging()
