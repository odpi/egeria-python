#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Display Asset Graph Information using generic functions.
"""
from __future__ import annotations
import argparse
import json
import os
import time
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from rich import box
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

from commands.cat.run_report import list_generic
from pyegeria import config_logging
from pyegeria.config import settings
from pyegeria._exceptions import PyegeriaException, print_exception_response, print_basic_exception
from pyegeria.base_report_formats import get_report_spec_heading, select_report_spec
from pyegeria.format_set_executor import exec_report_spec
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")


app_config = settings.Environment

guid_list = []

console = Console(width=app_config.console_width, force_terminal=(not app_config.egeria_jupyter))


def asset_viewer(
    output_format: str = "TABLE",
    asset_guid: str = None,
    view_server: str = app_config.egeria_view_server,
    view_url: str = app_config.egeria_view_server_url,
    user: str = EGERIA_USER,
    user_pass: str = EGERIA_USER_PASSWORD,
    jupyter: bool = app_config.egeria_jupyter,
    width: int = app_config.console_width,
    prompt_missing: bool = False,
    write_file: bool = False,
    render_table: bool = False,
    table_caption: str | None = None,
    use_pager: bool = True,
):
    try:
        list_generic(report_spec="Asset-Graph", output_format=output_format, view_server=view_server,
                 view_url=view_url, user=user, user_pass=user_pass, params={"asset_guid": asset_guid},
                 render_table=render_table, write_file = write_file, table_caption=table_caption, use_pager=use_pager,
                     width=width, jupyter=jupyter, prompt_missing=prompt_missing)

    except PyegeriaException as e:
        print_basic_exception(e)


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
        asset_guid = Prompt.ask("Enter the Asset GUID to view:", default="")
        output_format = Prompt.ask("Enter the output format:", default="TABLE")
        asset_viewer(output_format, asset_guid, server, url, userid,
                     user_pass, prompt_missing=True, write_file=True, render_table=True,
                     table_caption="Asset Graph")
    except KeyboardInterrupt as e:
        # console.print_exception()
        pass
    except Exception as e:
        console.print_exception()


if __name__ == "__main__":
    main()
