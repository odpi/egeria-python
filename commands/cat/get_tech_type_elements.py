#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Display the status of cataloged platforms and servers.
"""
import argparse
import os

from rich.console import Console
from rich.prompt import Prompt

from commands.cat.run_report import list_generic
from pyegeria import (
    settings,
    config_logging, print_basic_exception, PyegeriaException
)

EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")

app_config = settings.Environment
config_logging()
console = Console(width=app_config.console_width)

guid_list = []


def tech_viewer(
    tech_name: str,
    server_name: str,
    platform_url: str,
    user: str,
    user_pass: str,
    jupyter: bool = app_config.egeria_jupyter,
    width: int = app_config.console_width,
):
    try:
        list_generic(report_spec = "Tech-Type-Elements", output_format = "TABLE", view_server = server_name,
                 view_url= platform_url, user = user, user_pass = user_pass, prompt_missing = True,
                     params = {"filter": tech_name},
                 render_table=True, table_caption="Tech Type Elements", use_pager=True, width=width, jupyter=jupyter)

    except PyegeriaException as e:
        console.print_exception(show_locals=True)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    args = parser.parse_args()

    server = args.server if args.server is not None else app_config.egeria_view_server
    url = args.url if args.url is not None else app_config.egeria_view_server_url
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    try:
        tech_name = Prompt.ask(
            "Enter the Asset Name to view:", default="PostgreSQL Server"
        )
        tech_viewer(tech_name, server, url, userid, user_pass)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
