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

from pydantic import ValidationError
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from typing import List, Dict, Any
from html import escape
try:
    from markdown_it import MarkdownIt
except Exception:
    MarkdownIt = None

from pyegeria import (
    EgeriaTech,
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException, NO_CATEGORIES_FOUND, PyegeriaException, print_basic_exception, print_validation_error,
)
from commands.cat.glossary_actions import EGERIA_HOME_GLOSSARY_GUID
from pyegeria._globals import NO_GLOSSARIES_FOUND

disable_ssl_warnings = True

EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("EGERIA_VIEW_SERVER", "view-server")
EGERIA_VIEW_SERVER_URL = os.environ.get(
    "EGERIA_VIEW_SERVER_URL", "https://localhost:9443"
)
EGERIA_INTEGRATION_DAEMON = os.environ.get("EGERIA_INTEGRATION_DAEMON", "integration-daemon")
EGERIA_ADMIN_USER = os.environ.get("ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_JUPYTER = bool(os.environ.get("EGERIA_JUPYTER", "False"))
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "250"))
EGERIA_GLOSSARY_PATH = os.environ.get("EGERIA_GLOSSARY_PATH", None)
EGERIA_ROOT_PATH = os.environ.get("EGERIA_ROOT_PATH", "../../")
EGERIA_INBOX_PATH = os.environ.get("EGERIA_INBOX_PATH", "md_processing/dr_egeria_inbox")
EGERIA_OUTBOX_PATH = os.environ.get("EGERIA_OUTBOX_PATH", "md_processing/dr_egeria_outbox")

def _get_console_width_from_config(default_width: int = EGERIA_WIDTH) -> int:
    try:
        from pyegeria.config import settings
        return int(getattr(settings.Environment, "console_width", default_width) or default_width)
    except Exception:
        return default_width

def _get_outbox_dir() -> str:
    root = os.environ.get("EGERIA_ROOT_PATH", EGERIA_ROOT_PATH)
    out = os.environ.get("EGERIA_OUTBOX_PATH", EGERIA_OUTBOX_PATH)
    return os.path.join(root, out)

def _md_to_html(md_text: str) -> str:
    if not md_text:
        return ""
    if MarkdownIt is None:
        return f"<pre>{escape(md_text)}</pre>"
    try:
        return MarkdownIt().render(md_text)
    except Exception:
        return f"<pre>{escape(md_text)}</pre>"

def _build_html_table(columns: List[str], rows: List[List[str]]) -> str:
    ths = ''.join(f'<th>{escape(c)}</th>' for c in columns)
    body_rows = []
    for r in rows:
        tds = []
        for cell in r:
            if isinstance(cell, str) and cell.lstrip().startswith('<table'):
                tds.append(f"<td>{cell}</td>")
            else:
                tds.append(f"<td>{escape(cell or '')}</td>")
        body_rows.append('<tr>' + ''.join(tds) + '</tr>')
    return '<table>\n<thead><tr>' + ths + '</tr></thead>\n<tbody>\n' + "\n".join(body_rows) + '\n</tbody>\n</table>'

def display_command_terms(
    search_string: str = "*",
    glossary_guid: str = EGERIA_HOME_GLOSSARY_GUID,
    glossary_name: str = None,
    view_server: str = EGERIA_VIEW_SERVER,
    view_url: str = EGERIA_VIEW_SERVER_URL,
    user_id: str = EGERIA_USER,
    user_pass: str = EGERIA_USER_PASSWORD,
    jupyter: bool = EGERIA_JUPYTER,
    width: int = EGERIA_WIDTH,
    output_format: str = "TABLE",
    mode: str = "terminal",
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


        if output_format == "LIST":
            action = "LIST"
        elif output_format == "REPORT":
            action = "Report"
        if output_format != "TABLE":
            file_path = _get_outbox_dir()
            file_name = f"Command-Help-{time.strftime('%Y-%m-%d-%H-%M-%S')}-{action}.md"
            full_file_path = os.path.join(file_path, file_name)
            os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
            output = g_client.find_glossary_terms(search_string,  output_format=output_format, output_format_set="Help-Terms")
            if output == "NO_TERMS_FOUND":
                print(f"\n==> No commands found for search string '{search_string}'")
                return
            with open(full_file_path, 'w') as f:
                f.write(output)
            print(f"\n==> Terms output written to {full_file_path}")
            return

    except (
        PyegeriaException
        ) as e:
        print_basic_exception(e)
    except ValidationError as e:
        print_validation_error(e)
    except Exception as e:
        console.print_exception(e)


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
        table.add_column("Term Name", width=20)
        # table.add_column("Summary")
        table.add_column("Description", width=40)
        table.add_column("Usage", min_width=100)

        terms = g_client.find_glossary_terms(
            search_string,
            page_size=500,
        )

        if isinstance(terms, str):
            print(f"No commands found - this was not the command you were looking for?! - {search_string} : {glossary_guid} ")
            sys.exit(0)
        sorted_terms = sorted(
            terms, key=lambda k: (k.get("properties") or {}).get("displayName","---")
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
            description = props.get("description",'---')
            version = props.get("publishVersionIdentifier", "---")
            example = props.get("example", "---")
            usage = props.get("usage", "---")
            # ex_us_out = Markdown(f"Example:\n{example}\n---\nUsage: \n{usage}")

            classifications = term["elementHeader"].get("classifications",None)
            glossary_guid = None


            if glossary_guid and glossary_guid in glossary_info:
                glossary_name = glossary_info[glossary_guid]
            elif glossary_guid:
                g = g_client.get_glossary_for_term(term_guid)
                glossary_name = g["glossaryProperties"].get("displayName", "---")
                glossary_info[glossary_guid] = glossary_name
            else:
                glossary_name = "---"

            term_abb_ver_out = Markdown(f"{display_name}\n---\n{abbrev}\n---\n{version}")

            term_status = term["elementHeader"].get("status","---")
            table.add_row(
                Markdown(display_name),
                # summary,
                Markdown(description),
                Markdown(usage),
                style="bold white on black",
            )
            if not classifications:
                continue
            for c in classifications:
                if c["classificationName"] == "Anchors":
                    glossary_guid = c["classificationProperties"]["anchorScopeGUID"]

        g_client.close_session()
        return table

    # Shared fetch for md modes
    if mode in ("md", "md-html"):
        try:
            terms = g_client.find_glossary_terms(search_string, page_size=500)
        except Exception:
            terms = []
        if isinstance(terms, str) and terms == "NO_TERMS_FOUND":
            print(f"\n==> No commands found for search string '{search_string}'")
            return
        # Build outputs
        out_dir = _get_outbox_dir()
        os.makedirs(out_dir, exist_ok=True)
        stamp = time.strftime('%Y-%m-%d-%H-%M-%S')
        if mode == "md":
            # Simple sections per term
            lines: List[str] = []
            lines.append(f"# Dr.Egeria Commands (search: `{search_string}`)")
            lines.append("")
            sorted_terms = sorted(terms, key=lambda t: (t.get("properties") or {}).get("displayName", "---"))
            for term in sorted_terms:
                props = term.get("properties") or {}
                name = props.get("displayName", "---") or "---"
                desc = props.get("description", "") or ""
                usage = props.get("usage", "") or ""
                lines.append(f"## {name}")
                lines.append("")
                lines.append("### Description\n")
                lines.append(desc if desc.strip() else "_No description_")
                lines.append("")
                if usage.strip():
                    lines.append("### Usage\n")
                    lines.append(usage)
                    lines.append("")
                lines.append("---\n")
            content = "\n".join(lines)
            file_name = f"Command-Help-{stamp}-md.md"
        else:
            # md-html nested tables
            columns = ["Command", "Description", "Usage"]
            rows: List[List[str]] = []
            sorted_terms = sorted(terms, key=lambda t: (t.get("properties") or {}).get("displayName", "---"))
            for term in sorted_terms:
                props = term.get("properties") or {}
                name = props.get("displayName", "---") or "---"
                desc = props.get("description", "") or ""
                usage_md = props.get("usage", "") or ""
                usage_html = _md_to_html(usage_md).strip()
                rows.append([name, desc, usage_html])
            content = f"# Dr.Egeria Commands (search: `{search_string}`)\n\n" + _build_html_table(columns, rows) + "\n"
            file_name = f"Command-Help-{stamp}-md-html.md"
        full_file_path = os.path.join(out_dir, file_name)
        with open(full_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n==> Help written to {full_file_path}")
        return

    try:
        with console.pager(styles=True):
            console.print(generate_table(search_string, glossary_guid))

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
    ) as e:
        console.print_exception()


def main():
    sus_guid = "f9b78b26-6025-43fa-9299-a905cc6d1575"
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    parser.add_argument("--guid", help="GUID of glossary to search")
    parser.add_argument("--mode", choices=["terminal","md","md-html"], default="terminal", help="Output mode: terminal (default) prints Rich table; md writes Markdown; md-html writes Markdown with HTML tables.")
    parser.add_argument("--search", help="Search string for commands", default=None)

    args = parser.parse_args()

    # server = args.server if args.server is not None else EGERIA_VIEW_SERVER
    server = args.server if args.server is not None else EGERIA_VIEW_SERVER

    url = args.url if args.url is not None else EGERIA_PLATFORM_URL
    userid = args.userid if args.userid is not None else EGERIA_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    guid = args.guid if args.guid is not None else EGERIA_HOME_GLOSSARY_GUID

    try:
        search_default = args.search or "*"
        search_string = args.search or Prompt.ask("Enter the command you are searching for:", default=search_default)

        if args.mode == "terminal":
            output_format = Prompt.ask("What output format do you want?", choices=["TABLE", "LIST", "REPORT"], default="TABLE")
        else:
            output_format = "TABLE"

        display_command_terms(
            search_string, guid, 'Egeria-Markdown', server, url,
            userid, user_pass, output_format=output_format, mode=args.mode
        )

    except KeyboardInterrupt:
        pass




if __name__ == "__main__":
    main()
