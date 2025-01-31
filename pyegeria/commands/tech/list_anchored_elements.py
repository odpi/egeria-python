#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


Retrieve anchored elements based on a search of a specified properties.
"""
import argparse
import os
import sys
import time

from rich import box
from rich.console import Console
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.table import Table

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
    EgeriaTech,
)

EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("EGERIA_VIEW_SERVER", "view-server")
EGERIA_VIEW_SERVER_URL = os.environ.get(
    "EGERIA_VIEW_SERVER_URL", "https://localhost:9443"
)
EGERIA_INTEGRATION_DAEMON = os.environ.get("INTEGRATION_DAEMON", "integration-daemon")
EGERIA_ADMIN_USER = os.environ.get("ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_JUPYTER = bool(os.environ.get("EGERIA_JUPYTER", "False"))
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "260"))


disable_ssl_warnings = True


def display_anchored_elements(
    property_value: str,
    prop_list: list[str],
    server: str,
    url: str,
    username: str,
    user_password: str,
    time_out: int = 60,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
):
    console = Console(width=width, force_terminal=not jupyter, soft_wrap=True)
    if (property_value is None) or (len(property_value) < 3):
        print(
            "\nError --> Invalid Search String - must be greater than four characters long"
        )
        sys.exit(3)
    g_client = EgeriaTech(server, url, username, user_password)
    token = g_client.create_egeria_bearer_token()
    print(f"search value is {property_value} and prop_list is {prop_list}\n")

    def generate_table(property_value: str, prop_list: [str]) -> Table:
        """Make a new table."""
        table = Table(
            title=f"Elements containing the string  {property_value} @ {time.asctime()}",
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
        # table.add_column("Qualified Name")
        table.add_column("GUID", no_wrap=True)
        table.add_column("Properties")

        table.add_column("Classification Props", width=30)
        table.add_column("Matching Elements")

        classification = "Anchors"
        open_type_name = None
        property_value = property_value

        property_names = prop_list

        elements = g_client.find_elements_by_classification_with_property_value(
            classification, property_value, property_names, open_type_name
        )
        if type(elements) is str:
            return table

        for element in elements:
            template = False
            guid = element["elementHeader"].get("guid", "---")
            classifications = element["elementHeader"]["classifications"]

            class_prop_md = ""
            for classific in classifications:
                class_prop = classific.get("classificationProperties", "---")
                if type(class_prop) is dict:
                    for key in class_prop.keys():
                        class_prop_md += f"* {key}: {class_prop[key]}\n"

            class_prop_out = Markdown(class_prop_md)

            properties = element["properties"]
            props_md = ""
            if type(properties) is dict:
                for key in properties.keys():
                    props_md += f"* {key}: {properties[key]}\n"
                    if key == "category" and properties[key] == "placeholderProperty":
                        template = True
            props_out = Markdown(props_md)

            if template:  # Not interested in template elements in this method
                continue

            relationship = g_client.get_related_elements(guid, None, None)

            if type(relationship) is list:
                rel_md = ""
                for rel in relationship:
                    match_tab = Table(expand=True)
                    match_tab.add_column("Type Name")
                    match_tab.add_column("GUID", no_wrap=True, width=36)
                    match_tab.add_column("Properties")
                    match = rel["relationshipHeader"]
                    match_type_name = match["type"]["typeName"]
                    matching_guid = match["guid"]
                    match_props = rel["relatedElement"]["properties"]
                    match_details_md = ""
                    for key in match_props.keys():
                        match_details_md += f"* {key}: {match_props[key]}\n"
                    match_details_out = Markdown(match_details_md)
                    match_tab.add_row(match_type_name, matching_guid, match_details_out)

            table.add_row(guid, props_out, class_prop_out, match_tab)

        g_client.close_session()
        return table

    try:
        with console.pager(styles=True):
            console.print(generate_table(property_value, prop_list), soft_wrap=True)

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
    ) as e:
        console.print_exception()
        sys.exit(1)

    except Exception as e:
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

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    time_out = args.time_out if args.time_out is not None else 60
    try:
        property_value = Prompt.ask("Enter an property search string:", default="")
        prop_list = Prompt.ask(
            "Enter the list of properties to search", default="anchorTypeName"
        )
        if property_value == "":
            print("\nError --> Search string can't be empty")
            sys.exit(1)
        elif len(property_value) <= 4:
            print("\nError --> Search string must be greater than four characters long")
            sys.exit(2)
        else:
            display_anchored_elements(
                property_value, [prop_list], server, url, userid, user_pass, time_out
            )
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
