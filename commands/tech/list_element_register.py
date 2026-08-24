"""
Element Register — a hey_egeria/Rich take on browsing any family of Egeria
elements grouped by their real (sub)type, with badges for classifications
and a simple search/filter.

Deliberately general: takes any Open Metadata Type name (e.g.
"GovernanceDefinition", "Referenceable", "Project", "SolutionComponent")
and groups whatever comes back by `elementHeader.type.typeName` -- so one
command works for every element family, not just governance definitions.
"""

import argparse
import os
import sys
import time

from rich import box
from rich.console import Console, Group
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pyegeria import (
    EgeriaTech,
    PyegeriaException,
    config_logging,
    load_app_config,
    print_basic_exception,
    settings,
)

app_config = settings.Environment
config_path = os.path.join(app_config.pyegeria_config_directory, app_config.pyegeria_config_file)

EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
conf = load_app_config(config_path)

config_logging()

# A small, fixed palette so classification badges are stable across runs --
# the same classification name always lands on the same color, cycling
# deterministically by a hash of the name rather than insertion order.
_BADGE_PALETTE = [
    "black on #c9a227",  # gold
    "black on #4fa5a0",  # teal
    "black on #7a9b4e",  # olive
    "black on #4d7ea8",  # steel blue
    "black on #a8544d",  # rust
    "black on #8b6bb1",  # violet
    "black on #b1866b",  # tan
    "black on #6b8fb1",  # blue-grey
]


def _badge_style(label: str) -> str:
    return _BADGE_PALETTE[sum(ord(c) for c in label) % len(_BADGE_PALETTE)]


def _badges(labels: list[str]) -> Text:
    out = Text()
    for i, label in enumerate(labels):
        if i:
            out.append(" ")
        out.append(f" {label} ", style=_badge_style(label))
    return out


def _display_name(properties: dict, qualified_name: str) -> str:
    for key in ("displayName", "name", "title"):
        val = properties.get(key)
        if val:
            return val
    return qualified_name or "---"


def _fetch_all_elements(c_client: EgeriaTech, om_type: str, page_size: int) -> list[dict]:
    """Page through get_elements until an empty page comes back.

    Per Egeria's own paging contract, a short page does not mean the last
    page -- only an empty result does -- so this keeps asking until that
    happens rather than stopping the moment a page comes back under
    page_size.
    """
    all_elements: list[dict] = []
    start_from = 0
    while True:
        page = c_client.get_elements(om_type, start_from=start_from, page_size=page_size, output_format="JSON")
        if not isinstance(page, list) or len(page) == 0:
            break
        all_elements.extend(page)
        start_from += page_size
    return all_elements


def element_register(
    om_type: str,
    server: str,
    url: str,
    username: str,
    password: str,
    search: str | None = None,
    classification: str | None = None,
    page_size: int = 100,
    jupyter: bool = settings.Environment.egeria_jupyter,
    width: int = settings.Environment.egeria_width,
):
    c_client = EgeriaTech(server, url, user_id=username, user_pwd=password)
    c_client.create_egeria_bearer_token()

    om_typedef = c_client.get_typedef_by_name(om_type)
    if isinstance(om_typedef, str):
        print(f"The type name '{om_type}' is not known to the Egeria platform at {url} - {server}")
        sys.exit(1)

    try:
        raw_elements = _fetch_all_elements(c_client, om_type, page_size)

        rows = []
        for element in raw_elements:
            header = element.get("elementHeader", {})
            properties = element.get("properties", {})
            qualified_name = properties.get("qualifiedName", "---")
            type_name = header.get("type", {}).get("typeName", om_type)
            guid = header.get("guid", "---")
            classifications = [
                c.get("classificationName", "---")
                for c in header.get("otherClassifications", []) or []
                if isinstance(c, dict)
            ]
            rows.append({
                "display_name": _display_name(properties, qualified_name),
                "qualified_name": qualified_name,
                "type_name": type_name,
                "guid": guid,
                "classifications": classifications,
            })

        search_lower = search.lower() if search else None
        if search_lower:
            rows = [
                r for r in rows
                if search_lower in r["display_name"].lower() or search_lower in r["qualified_name"].lower()
            ]
        if classification:
            rows = [r for r in rows if classification in r["classifications"]]

        groups: dict[str, list[dict]] = {}
        for r in rows:
            groups.setdefault(r["type_name"], []).append(r)

        distinct_classifications = {c for r in rows for c in r["classifications"]}

        stats = Table.grid(padding=(0, 3))
        stats.add_row(
            Text(str(len(rows)), style="bold white"),
            Text(str(len(groups)), style="bold white"),
            Text(str(len(distinct_classifications)), style="bold white"),
        )
        stats.add_row(
            Text("ELEMENTS", style="dim"),
            Text("SUBTYPES", style="dim"),
            Text("CLASSIFICATIONS", style="dim"),
        )

        header_lines = [f"Open Metadata Type: [bold]{om_type}[/bold]  ·  {server} @ {url}"]
        if search:
            header_lines.append(f"Search: '{search}'")
        if classification:
            header_lines.append(f"Classification filter: '{classification}'")
        header_lines.append(f"{len(rows)} of {len(raw_elements)} shown  ·  {time.asctime()}")

        panel = Panel(
            Group(stats, Padding(Text("\n".join(header_lines), style="dim"), (1, 0, 0, 0))),
            title=f"Element Register",
            border_style="bright_blue",
            box=box.ROUNDED,
        )

        renderables = [panel]
        for type_name in sorted(groups.keys()):
            group_rows = groups[type_name]
            table = Table(
                title=f"{type_name}  [dim]({len(group_rows)})[/dim]",
                title_justify="left",
                box=box.SIMPLE_HEAVY,
                header_style="bold white",
                show_lines=False,
                expand=True,
            )
            table.add_column("Display Name", style="bold")
            table.add_column("Classifications")
            table.add_column("Qualified Name", style="dim", overflow="fold")

            for r in sorted(group_rows, key=lambda r: r["display_name"].lower()):
                table.add_row(
                    r["display_name"],
                    _badges(r["classifications"]) if r["classifications"] else Text("—", style="dim"),
                    r["qualified_name"],
                )
            renderables.append(table)

        if not rows:
            renderables.append(Text("No elements matched.", style="italic dim"))

        console = Console(width=width)
        with console.pager(styles=True):
            for renderable in renderables:
                console.print(renderable)
                console.print()

    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the server to display status for")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="Password")
    parser.add_argument("--om-type", default="Referenceable", help="Open Metadata Type to browse")
    parser.add_argument("--search", default=None, help="Filter by display name or qualified name substring")
    parser.add_argument("--classification", default=None, help="Filter to elements carrying this classification")
    parser.add_argument("--page-size", type=int, default=100, help="Page size used when paging through results")

    args = parser.parse_args()

    server = args.server if args.server is not None else app_config.egeria_view_server
    url = args.url if args.url is not None else app_config.egeria_platform_url
    userid = args.userid if args.userid is not None else EGERIA_USER
    password = args.password if args.password is not None else EGERIA_USER_PASSWORD

    try:
        element_register(
            args.om_type,
            server,
            url,
            userid,
            password,
            search=args.search,
            classification=args.classification,
            page_size=args.page_size,
        )
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
