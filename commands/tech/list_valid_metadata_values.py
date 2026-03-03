#!/usr/bin/env python3
"""
SPDX-Lic
ense-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Unit tests for the Utils helper functions using the Pytest framework.


A simple display for glossary terms
"""
import argparse
import json
import os
import sys
import time
from typing import Optional

# Add the repository root to sys.path to ensure local pyegeria is used
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from rich import box, print
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from pyegeria import (
    PyegeriaException,
    ValidMetadataManager, print_basic_exception,

)
from pyegeria.core.config import load_app_config, get_app_config

# Legacy environment variables - now handled via pyegeria.core.config
# EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
# ... (others removed to use unified config)


def display_metadata_values(
    property_name: str,
    type_name: str,
    server: str,
    url: str,
    username: str,
    user_pass: str,
    save_output: bool,
    jupyter: bool = False,
    width: int = 200,
):
    try:
        m_client = ValidMetadataManager(server, url, user_id=username)
        token = m_client.create_egeria_bearer_token(username, user_pass)
    except PyegeriaException as e:
        print_basic_exception(e)
        return
    except ValueError as ve:
        print(f"[red]Input error: {ve}[/red]")
        return

    def generate_table(property_name: str, type_name: Optional[str]) -> Table:
        """Make a new table."""
        table = Table(
            title=f"Valid Metadata Values for Property: {property_name} of type {type_name} @ {time.asctime()}",
            style="bold bright_white on black",
            row_styles=["bold bright_white on black"],
            header_style="white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Valid Metadata Values for Server '{server}' @ Platform - {url}",
            expand=True,
        )

        table.add_column("Category")
        table.add_column("Display Name")

        table.add_column("Preferred Value")
        table.add_column("Deprecated")
        table.add_column("Case Sensitive")
        table.add_column("Additional Properties")
        table.add_column("Description")

        valid_values = m_client.get_valid_metadata_values(property_name, type_name)

        if valid_values is None:
            name = " "
            type_name = " "
            created = " "
            priority = " "
            due = " "
            completed = " "
            status = " "
            sponsor = " "
        elif type(valid_values[0]) == str:
            raise ValueError(
                "-->This is not a known metadata property with a valid value"
            )
        else:
            for value in valid_values:
                category = value.get("category", "None")
                display_name = value.get("displayName", "None")
                preferred_value = value.get("preferredValue", "None ")
                deprecated = str(value.get("isDeprecated", "None "))
                case_sensitive = str(value.get("isCaseSensitive", "None"))
                description = value.get("description", "None")
                additional_properties = value.get("additionalProperties", "None")
                if additional_properties is not None:
                    props = json.dumps(additional_properties)
                table.add_row(
                    category,
                    display_name,
                    preferred_value,
                    deprecated,
                    case_sensitive,
                    props,
                    description,
                )

        m_client.close_session()
        return table

    try:
        # with Live(generate_table(), refresh_per_second=4, screen=True) as live:
        #     while True:
        #         time.sleep(2)
        #         live.update(generate_table())
        console = Console(width=width, force_terminal=not jupyter, record=True)
        with console.pager(styles=True):
            console.print(generate_table(property_name, type_name))
        if save_output:
            console.save_html("valid-metadata-values.html")

    except (
        PyegeriaException,
        ValueError,
    ) as e:
        if type(e) is str:
            print(e)
        else:
            print_basic_exception(e)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--save-output", help="Save output to file?")
    parser.add_argument("--password", help="User Password")
    # parser.add_argument("--sponsor", help="Name of sponsor to search")
    args = parser.parse_args()

    config = load_app_config()
    user_profile = config.User_Profile
    env = config.Environment

    server = args.server if args.server is not None else env.egeria_view_server
    url = args.url if args.url is not None else env.egeria_platform_url
    userid = args.userid if args.userid is not None else user_profile.user_name
    user_pass = args.password if args.password is not None else user_profile.user_pwd
    save_output = args.save_output if args.save_output is not None else False

    try:
        property_name = Prompt.ask(
            "Enter the Property to retrieve:", default="projectHealth"
        )
        type_name = Prompt.ask(
            "Enter the Metadata Type to filter on (Optional, use :: or leave blank for None):", default="::"
        )
        if type_name == "":
            type_name = None

        display_metadata_values(
            property_name, type_name, server, url, userid, user_pass, save_output, 
            jupyter=env.egeria_jupyter, width=env.console_width
        )
    except PyegeriaException as e:
        print_basic_exception(e)
    except ValueError as ve:
        print(f"[red]Value Error: {ve}[/red]")
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"[red]An unexpected error occurred: {e}[/red]")


if __name__ == "__main__":
    main()
