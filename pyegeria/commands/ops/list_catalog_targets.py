#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



List catalog targets

"""
import argparse
import os
import time

from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table

from pyegeria import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
    AutomatedCuration,
    INTEGRATION_GUIDS,
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
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "200"))


def display_catalog_targets(
    connector: str,
    view_server: str = EGERIA_VIEW_SERVER,
    view_url: str = EGERIA_VIEW_SERVER_URL,
    user: str = EGERIA_USER,
    user_pass: str = EGERIA_USER_PASSWORD,
    paging: bool = True,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
):
    """Display catalog targets for the specified connector as a table.

    Parameters
    ----------
    connector : str
        The connector to retrieve catalog targets for.
    view_server : str
        The Egeria view server name.
    view_url : str
        The URL for the Egeria view server.
    user : str
        The user name for authenticating with the Egeria server.
    user_pass : str
        The user password for authenticating with the Egeria server.
    paging : bool, default is True
        Whether to enable paging mode when displaying the table.
    jupyter : bool
        Indicates if the environment is a Jupyter notebook.
    width : int
        The width of the console for table printing.
    """
    console = Console(force_terminal=not jupyter, width=width, soft_wrap=True)

    def generate_table() -> Table:
        """Make a new table."""
        table = Table(
            title=f"All Catalog Targets for Integration Connector {connector} @ {time.asctime()}",
            style="bold white on black",
            row_styles=["bold white on black"],
            header_style="white on dark_blue",
            title_style="bold white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"Catalog Targets for '{view_server}' @ Platform - {view_url}",
            expand=True,
        )
        table.add_column("Name of Target")
        table.add_column("Catalog Target")

        # table.add_column("Relationship GUID", no_wrap=True)
        table.add_column("Configuration Properties")
        table.add_column("Template Properties")
        table.add_column("Operational Instructions", max_width=20)
        # table.add_column("Delete Method")

        if type(cat_targets) is list:
            for target in cat_targets:
                target_name = target.get("catalogTargetName", "---")
                target_source = target.get("metadataSourceQualifiedName", "---")
                target_rel = target.get("relationshipGUID", "---")
                target_sync = target.get("permittedSynchronization")
                target_delete = target.get("deleteMethod", "---")
                op_instruct = f"* {target_sync}\n* {target_delete}"
                op_instruct_out = Markdown(op_instruct)
                # target_guid = target['catalogTargetElement']['guid']
                connector_unique = target["catalogTargetElement"]["uniqueName"]

                cat_target_out = Markdown(
                    f"* Target Name: {target_name}\n* Target Source: {target_source}\n"
                    f"* Relationship Guid: {target_rel}"
                )

                config_props = target.get("configurationProperties", "---")
                if type(config_props) is dict:
                    config_props_md = ""
                    for prop in config_props:
                        config_props_md += f"* {prop}: {config_props[prop]}\n"
                    config_props_out = Markdown(config_props_md)
                else:
                    config_props_out = "---"

                template_props = target.get("templateProperties", "---")
                if type(template_props) is dict:
                    template_props_md = ""
                    for prop in template_props:
                        template_props_md += f"* {prop}: {template_props[prop]}\n"
                    template_props_out = Markdown(template_props_md)
                else:
                    template_props_out = "---"

                table.add_row(
                    connector_unique,
                    cat_target_out,
                    config_props_out,
                    template_props_out,
                    op_instruct_out,
                )

        return table

    try:
        a_client = AutomatedCuration(view_server, view_url, user)
        token = a_client.create_egeria_bearer_token(user, user_pass)
        connector = connector.strip()
        if connector not in INTEGRATION_GUIDS.keys():
            raise Exception

        connector_guid = INTEGRATION_GUIDS[connector]
        cat_targets = a_client.get_catalog_targets(connector_guid)
        console = Console(force_terminal=not jupyter, width=width, soft_wrap=True)
        with console.pager(styles=True):
            console.print(generate_table(), soft_wrap=True)

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
    ) as e:
        print_exception_response(e)
    except Exception as e:
        print(f"\n\n===> Perhaps integration connector {connector} is not known?\n\n")
        console.print_exception()
    finally:
        a_client.close_session()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    parser.add_argument("--jupyter", help="Enable for Jupyter terminal compatibility")
    parser.add_argument("--width", help="Screen width, in characters, to use")

    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    url = args.url if args.url is not None else EGERIA_VIEW_SERVER_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    jupyter = args.jupyter if args.jupyter is not None else EGERIA_JUPYTER
    width = args.width if args.width is not None else EGERIA_WIDTH

    try:
        connector = Prompt.ask(
            "Enter the Integration Connector to list catalog targets for"
        ).strip()
        display_catalog_targets(
            connector, server, url, userid, user_pass, jupyter, width=width
        )

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
