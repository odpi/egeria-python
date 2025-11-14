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
from rich.table import Table

from pyegeria import (
    ClassificationManager,
    PyegeriaException, settings
)
app_config = settings.Environment

EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")

disable_ssl_warnings = True


def display_certifications(
    server: str,
    url: str,
    username: str,
    user_password: str,
    time_out: int = 60,
    jupyter: bool = app_config.egeria_jupyter,
    width: int = app_config.console_width,
):
    console = Console(width=width, force_terminal=not jupyter, soft_wrap=True)

    g_client = ClassificationManager(
        server, url, user_id=username, user_pwd=user_password
    )
    token = g_client.create_egeria_bearer_token(username, user_password)

    def generate_table(search_string: str = "CertificationType") -> Table:
        """Make a new table."""
        table = Table(
            title=f"Certifications Types  @ {time.asctime()}",
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
        table.add_column("Name", max_width=15)
        table.add_column("summary")
        table.add_column("domainID")
        table.add_column("Unique Name")
        table.add_column("Scope")
        # table.add_column("Qualified Name",max_width=15)
        table.add_column("Description")
        table.add_column("Details")
        table.add_column("Related Elements")

        certs = g_client.get_elements(search_string, page_size=100, time_out=time_out)
        if type(certs) is str:
            return table

        for element in certs:
            properties = element["properties"]
            summary = properties.get("summary", "---")
            domain = str(properties.get("domainIdentifier", "---"))
            unique_name = properties.get("qualifiedName", "---")
            scope = properties.get("scope", "---")
            description = properties.get("description", "---")
            details = properties.get("details", "---")
            name = properties.get("displayName", "---")
            cert_guid = element["elementHeader"]["guid"]

            related = g_client.get_related_elements(cert_guid)
            if (len(related) > 0) and (type(related) is list):
                rel_md = ""
                for rel in related:
                    rel_type = rel["relationshipHeader"]["type"]["typeName"]
                    rel_element_props = rel["relatedElement"]["properties"]
                    rel_el_md = f"* Rel Type: {rel_type}\n"
                    for key in rel_element_props.keys():
                        rel_el_md += f"* {key}: {rel_element_props[key]}\n"
                    rel_md += f"----\n{rel_el_md}\n"
            else:
                rel_md = "---"

            table.add_row(
                name, summary, domain, unique_name, scope, description, details, rel_md
            )

        g_client.close_session()

        return table

    try:

        with console.pager(styles=True):
            console.print(generate_table("CertificationType"), soft_wrap=True)

    except (
        PyegeriaException
    ) as e:
        console.print_exception()
        sys.exit(1)

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
    url = args.url if args.url is not None else app_config.egeria_view_server_url
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    time_out = args.time_out if args.time_out is not None else 60
    try:
        display_certifications(server, url, userid, user_pass, time_out)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
