#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


A simple display for glossary terms
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
from rich.text import Text

from pyegeria import (
    EgeriaTech, settings,
    PyegeriaException, print_basic_exception, NO_CATEGORIES_FOUND,
    )
from pyegeria._globals import NO_GLOSSARIES_FOUND
app_config = settings.Environment
# config_logging()
disable_ssl_warnings = True


EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")


def display_glossary_terms(
    search_string: str = "*",
    glossary_guid: str = settings.User_Profile.egeria_home_glossary_name,
    glossary_name: str = None,
    view_server: str = app_config.egeria_view_server,
    view_url: str = app_config.egeria_view_server_url,
    user_id: str = EGERIA_USER,
    user_pass: str = EGERIA_USER_PASSWORD,
    jupyter: bool = app_config.egeria_jupyter,
    width: int = app_config.console_width,
    output_format: str = "TABLE",
):
    """Display a table of glossary terms filtered by search_string and glossary, if specified. If no
        filters then all terms are displayed. If glossary_guid or name is specified, then only terms from that
        glossary are displayed.
    Parameters
    ----------
    search_string : str, optional
        The string to search for terms. Defaults to "*".
    glossary_guid : str, optional
        The unique identifier of the glossary. Defaults to None. If specified, then only terms from that glossary
        are displayed. If both glossary_guid and glossary_name are provided then glossary_guid will take precedence.
    glossary_name : str, optional
        The display name of the glossary. Defaults to None. If specified, then only terms from that glossary
        are displayed. If both glossary_guid and glossary_name are provided then glossary_guid will take precedence.
        Note that the use of glossary display name relies on the qualified name conforming to convention. GUID is more
        reliable.
    view_server : str
        The server where the glossary is hosted. Defaults to EGERIA_VIEW_SERVER.
    view_url : str
        The URL of the server where the glossary is hosted. Defaults to EGERIA_VIEW_SERVER_URL.
    user_id : str
        The user ID for authentication. Defaults to EGERIA_USER.
    user_pass : str
        The user password for authentication. Defaults to EGERIA_USER_PASSWORD.
    jupyter : bool
        Flag to indicate if the output should be formatted for Jupyter notebook. Defaults to EGERIA_JUPYTER.
    width : int
        The width of the console output. Defaults to EGERIA_WIDTH.
        output_format: str, optional, default is 'JSON'
        One of TABLE, FORM, REPORT
    """

    console = Console(
        style="bold bright_white on black", width=width, force_terminal=not jupyter
    )
    try:
        g_client = EgeriaTech(view_server, view_url, user_id, user_pass)
        token = g_client.create_egeria_bearer_token(user_id, user_pass)
        if (glossary_name is not None) and (glossary_name != "*"):
            glossary_guid = g_client.get_guid_for_name(glossary_name)
            if glossary_guid == NO_GLOSSARIES_FOUND:
                console.print(
                    f"\nThe glossary name {glossary_name} was not found. Please try using the glossary guid"
                )
                sys.exit(1)
        elif (glossary_guid is not None) and (len(glossary_guid) < 10):
                glossary_guid = None

        if output_format == "FORM":
            action = "Update-Form"
        elif output_format == "REPORT":
            action = "Report"
        if output_format != "TABLE":
            file_path = os.path.join(app_config.pyegeria_root, app_config.egeria_outbox)
            file_name = f"Terms-{time.strftime('%Y-%m-%d-%H-%M-%S')}-{action}.md"
            full_file_path = os.path.join(file_path, file_name)
            os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
            output = g_client.find_glossary_terms(search_string, glossary_guid, output_format=output_format)
            if output == "NO_TERMS_FOUND":
                print(f"\n==> No terms found for search string '{search_string}'")
                return
            with open(full_file_path, 'w') as f:
                f.write(output)
            print(f"\n==> Terms output written to {full_file_path}")
            return

    except (
        PyegeriaException
        ) as e:
        print_basic_exception(e)



    def generate_table(search_string: str, glossary_guid: str) -> Table:
        """Make a new table."""
        table = Table(
            title=f"Glossary Definitions for Terms like  {search_string} @ {time.asctime()}",
            style="bright_white on black",
            # row_styles="bright_white on black",
            header_style="bright_white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption=f"View Server '{view_server}' @ Platform - {view_url}",
            expand=True,
        )
        table.add_column("Term Name / Abbreviation / Version")
        table.add_column("Qualified Name / GUID / Aliases", width=38, no_wrap=True)
        table.add_column("Summary")
        table.add_column("Description")
        table.add_column("Glossary")
        table.add_column("Collection Folder")
        table.add_column("Status")
        table.add_column("Example/Usage", min_width=50)

        terms = g_client.find_glossary_terms(
            search_string,
            page_size=500,
        )

        if type(terms) is str:
            print(f"No terms found! - {search_string} : {glossary_guid} ")
            sys.exit(0)
        sorted_terms = sorted(
            terms, key=lambda k: k["properties"].get("displayName","---")
        )
        style = "bright_white on black"
        if type(terms) is str:
            return table
        glossary_info = {}
        for term in sorted_terms:
            props = term.get("properties", "None")
            if props == "None":
                return table

            display_name = props.get("displayName","---")
            qualified_name = props["qualifiedName"]
            term_guid = term["elementHeader"]["guid"]
            aliases = props.get("aliases", "---")
            q_name = Text(
                f"{qualified_name}\n&\n{term_guid}\n&\n{aliases}", style=style, justify="center"
            )
            abbrev = props.get("abbreviation", "---")
            summary = props.get("summary", "---")
            description = Markdown(props.get("description",'---'))
            version = props.get("publishVersionIdentifier", "---")
            example = props.get("example", "---")
            usage = props.get("usage", "---")
            ex_us_out = Markdown(f"Example:\n{example}\n---\nUsage: \n{usage}")

            parents = term.get('memberOfCollections',[])
            glossary_list_md = ""
            category_list_md = ""
            for parent in parents:
                parent_q_name = parent.get('relatedElement',{}).get('properties',{}).get('qualifiedName','---')
                parent_type = parent.get('relatedElement',{}).get('elementHeader',{}).get('type',{}).get('typeName','---')
                if parent_type == 'Glossary':
                    glossary_list_md += f"{parent_q_name}\n"
                elif parent_type == 'CollectionFolder':
                    category_list_md += f"{parent_q_name}\n"


            term_abb_ver_out = Markdown(f"{display_name}\n---\n{abbrev}\n---\n{version}")
            category_list_out = Markdown(category_list_md)

            term_status = term["elementHeader"].get("status","---")
            table.add_row(
                term_abb_ver_out,
                q_name,
                summary,
                description,
                glossary_list_md,
                category_list_out,
                term_status,
                ex_us_out,
                style="bold white on black",
            )

        g_client.close_session()
        return table

    try:
        with console.pager(styles=True):
            console.print(generate_table(search_string, glossary_guid))

    except (
        PyegeriaException
    ) as e:
        print_basic_exception(e)


def main():
    sus_guid = "f9b78b26-6025-43fa-9299-a905cc6d1575"
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    parser.add_argument("--guid", help="GUID of glossary to search")

    args = parser.parse_args()

    # server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    server = args.server if args.server is not None else app_config.egeria_view_server

    url = args.url if args.url is not None else app_config.egeria_view_server_url
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    guid = args.guid if args.guid is not None else settings.User_Profile.egeria_home_glossary_name

    try:
        search_string = Prompt.ask("Enter the term you are searching for:", default="*")
        glossary_name = Prompt.ask(
            "Enter the name of the glossary to search or '*' for all glossaries:",
            default="*",
        )
        output_format = Prompt.ask("What output format do you want?", choices=["TABLE", "FORM", "REPORT"], default="TABLE")

        display_glossary_terms(search_string, guid, glossary_name, server, url, userid, user_pass,
                               output_format=output_format)

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
