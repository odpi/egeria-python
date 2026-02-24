#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

List registered report specs with optional filtering and show available formats.

Columns:
- Report Name
- Description
- Available Formats

Usage examples:
- poetry run list_reports
- poetry run list_reports --search user
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Iterable

from rich import box
from rich.console import Console
from rich.table import Table

from pyegeria.core.config import settings
from pyegeria.view.base_report_formats import get_report_registry

EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")

app_config = settings.Environment


def _matches(needle: str, haystack: Iterable[str]) -> bool:
    if not needle:
        return True
    n = needle.strip().lower()
    if not n:
        return True
    for s in haystack:
        if n in (s or "").strip().lower():
            return True
    return False


def display_reports(*, search: str | None = None, width: int = app_config.console_width,
                    jupyter: bool = app_config.egeria_jupyter) -> None:
    registry = get_report_registry()

    def generate_table() -> Table:
        table = Table(
            title=f"Report Specs @ {time.asctime()}",
            style="bold white on black",
            row_styles=["bold white on black"],
            header_style="white on dark_blue",
            title_style="bold white on black",
            caption_style="white on black",
            show_lines=True,
            box=box.ROUNDED,
            caption="Use 'run_report' to execute a report; use '--search' to filter.",
            expand=True,
        )
        table.add_column("Report Name")
        table.add_column("Family")
        table.add_column("Description")
        table.add_column("Available Formats")

        rows = []
        for name, fs in registry.items():
            fam = (getattr(fs, "family", "") or "").strip()
            desc = getattr(fs, "description", "") or ""
            aliases = getattr(fs, "aliases", []) or []
            formats = sorted({str(t).upper() for f in getattr(fs, "formats", []) or [] for t in getattr(f, "types", []) or []})
            if not _matches(search or "", [name, fam, desc, " ".join(aliases)]):
                continue
            rows.append((name, fam, desc, ", ".join(formats)))

        for name, fam, desc, fmts in sorted(rows, key=lambda r: (r[1].lower(), r[0].lower())):
            table.add_row(name, fam, desc, fmts)
        return table

    console = Console(width=width, force_terminal=not jupyter)
    with console.pager(styles=True):
        console.print(generate_table())


def main():
    parser = argparse.ArgumentParser(description="List available report specs")
    parser.add_argument("--search", "-s", dest="search", help="Optional substring to filter by name/description/aliases")
    args = parser.parse_args()

    try:
        display_reports(search=args.search)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
