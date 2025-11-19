#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



List catalog targets

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
    EgeriaTech,
    PyegeriaException,
    print_basic_exception,
    settings,
    config_logging
)

EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")

app_config = settings.Environment
config_logging()
console = Console(width = app_config.console_width)


def display_catalog_targets(
    connector: str,
    view_server: str = app_config.egeria_view_server,
    view_url: str = app_config.egeria_view_server_url,
    user: str = EGERIA_USER,
    user_pass: str = EGERIA_USER_PASSWORD,
    paging: bool = True,
    jupyter: bool = app_config.egeria_jupyter,
    width: int = app_config.console_width,
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
                target_name = target['properties'].get("catalogTargetName", "---")
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
        a_client = EgeriaTech(view_server, view_url, user)
        token = a_client.create_egeria_bearer_token(user, user_pass)
        connector = connector.strip()


        connector_guid = a_client.get_connector_guid(connector)
        if connector_guid is None or connector_guid == "No connector found":
            console.print(f"\n\n===> No connector found with name '{connector}'\n\n")
            sys.exit(1)

        cat_targets = a_client.get_catalog_targets(connector_guid)
        console = Console(force_terminal=not jupyter, width=width, soft_wrap=True)
        with console.pager(styles=True):
            console.print(generate_table(), soft_wrap=True)


    except PyegeriaException as e:
        print(f"\n\n===> Perhaps integration connector {connector} is not known?\n\n")
        print_basic_exception(e)
    except (
        Exception
    ) as e:
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

    server = args.server if args.server is not None else app_config.egeria_view_server
    url = args.url if args.url is not None else app_config.egeria_view_server_url
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    jupyter = args.jupyter if args.jupyter is not None else app_config.egeria_jupyter
    width = args.width if args.width is not None else app_config.console_width

    try:
        connector = Prompt.ask(
            "Enter the Integration Connector to list catalog targets for"
        ).strip()
        display_catalog_targets(connector, server, url, userid, user_pass, jupyter, width=width)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
