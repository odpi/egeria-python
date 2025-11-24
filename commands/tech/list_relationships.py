#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

List certification types


A simple display for certification types
"""
import argparse
import os
import sys
import time

from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table

from pyegeria import (
    ClassificationManager,
    PyegeriaException,
    print_basic_exception,
    settings,
    config_logging
)

EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")

app_config = settings.Environment
config_logging()
console = Console(width=app_config.console_width)


def list_relationships(
    search_string: str,
    server: str,
    url: str,
    username: str,
    user_password: str,
    time_out: int = 60,
    jupyter: bool = app_config.egeria_jupyter,
    width: int = app_config.console_width,
):
    console = Console(width=width, force_terminal=not jupyter, soft_wrap=True)
    if (search_string is None) or (len(search_string) < 3) and (search_string != "*"):
        raise ValueError(
            "Invalid Search String - must be greater than four characters long"
        )
    g_client = ClassificationManager(
        server, url, user_id=username, user_pwd=user_password
    )
    token = g_client.create_egeria_bearer_token(username, user_password)

    def generate_table(search_string: str = None) -> Table:
        """Make a new table."""
        table = Table(
            title=f"Relationship List for {search_string}  @ {time.asctime()}",
            header_style="white on dark_blue",
            style="bold white on black",
            row_styles=["bold white on black"],
            title_style="bold white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"View Server '{server}' @ Platform - {url}",
            expand=True,
        )
        table.add_column("End 1 Name")
        table.add_column("End 1 GUID", no_wrap=True)
        table.add_column("End 1 Type")
        table.add_column("End 2 Name")
        table.add_column("End 2 GUID", no_wrap=True)
        table.add_column("End 2 Type")
        table.add_column("Properties", min_width=40)

        rel_list = g_client.get_relationships(search_string, page_size=0, time_out=time_out,
                                              output_format="JSON")
        if type(rel_list) is str:
            return table

        for rel in rel_list:
            end1_name = rel["end1"].get("uniqueName", "---")
            end1_guid = rel["end1"]["guid"]
            end1_type = rel["end1"]["type"]["typeName"]
            end2_name = rel["end2"].get("uniqueName", "---")
            end2_guid = rel["end2"]["guid"]
            end2_type = rel["end2"]["type"]["typeName"]

            rel_md = ""
            p_test = rel.get("properties", "---")
            if type(p_test) is str:
                rel_md = "---"
            else:
                for key in rel["properties"].keys():
                    rel_md += f"* {key}: {rel['properties'][key]}\n"

            rel_out = Markdown(rel_md)

            table.add_row(
                end1_name,
                end1_guid,
                end1_type,
                end2_name,
                end2_guid,
                end2_type,
                rel_out,
            )

        g_client.close_session()

        return table

    try:
        with console.pager(styles=True):
            console.print(generate_table(search_string), soft_wrap=True)

    except (
        PyegeriaException
    ) as e:
        if e.response_egeria_msg_id == "OMAG-COMMON-400-018":
            print("\n\n==>Invalid Relationship Type\n\n")
        else:
            print_basic_exception(e)
            assert False, "Invalid request"

    except ValueError as e:
        console.print(
            f"\n\n====> Invalid Search String - must be greater than four characters long"
        )
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    parser.add_argument("--time_out", help="Time Out")

    args = parser.parse_args()

    server = args.server if args.server is not None else app_config.egeria_view_server
    url = args.url if args.url is not None else app_config.egeria_platform_url
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    time_out = args.time_out if args.time_out is not None else 60
    try:
        search_string = Prompt.ask(
            "Enter an asset search string:", default="Certification"
        )

        list_relationships(search_string, server, url, userid, user_pass, time_out)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
