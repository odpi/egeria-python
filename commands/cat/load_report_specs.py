#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Refresh the in-process report-spec registry from Egeria.

Reads ReportType collections and their QuestionSpec folders from Egeria and
merges question_specs into the runtime registry so that find_report_specs_by_*
and the MCP find_report_specs tool return Egeria-aware results.

Usage (standalone):
    load_report_specs [--force] [--ttl <seconds>]
    load_report_specs --server qs-view-server --url https://localhost:9443

Usage (hey_egeria):
    hey_egeria cat show info load-report-specs [--force] [--ttl <seconds>]
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import click
from rich.console import Console

from pyegeria.core.config import settings
from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.view.base_report_formats import (
    load_egeria_report_specs,
    report_spec_list,
    _EGERIA_SPECS_LOADED_AT,
    _EGERIA_SPECS_CACHE_TTL,
)

EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
app_config = settings.Environment


def _run(
    *,
    view_server: str = app_config.egeria_view_server,
    view_url: str = app_config.egeria_view_server_url,
    user: str = EGERIA_USER,
    user_pass: str = EGERIA_USER_PASSWORD,
    force: bool = False,
    ttl_seconds: int | None = None,
    width: int = settings.Environment.egeria_width,
    jupyter: bool = settings.Environment.egeria_jupyter,
) -> None:
    console = Console(width=width, force_terminal=not jupyter)

    from pyegeria.view import base_report_formats as _brf
    last = getattr(_brf, "_EGERIA_SPECS_LOADED_AT", None)
    effective_ttl = ttl_seconds if ttl_seconds is not None else _EGERIA_SPECS_CACHE_TTL

    if not force and last is not None:
        from datetime import datetime, timezone
        age = (datetime.now(timezone.utc) - last).total_seconds()
        if age < effective_ttl:
            console.print(
                f"[green]Registry is fresh[/green] (loaded {age:.0f}s ago, TTL={effective_ttl}s). "
                f"Use --force to reload anyway."
            )
            return

    client = EgeriaTech(view_server, view_url, user_id=user, user_pwd=user_pass)
    client.create_egeria_bearer_token(user, user_pass)

    before = set(report_spec_list())
    start = time.perf_counter()
    updated = load_egeria_report_specs(client, force=force, ttl_seconds=ttl_seconds)
    elapsed = time.perf_counter() - start

    client.close_session()

    after = set(report_spec_list())
    new_specs = sorted(after - before)

    if updated:
        console.print(
            f"[green]Registry updated[/green] from Egeria in {elapsed:.2f}s. "
            f"{len(new_specs)} new spec(s) added."
        )
        if new_specs:
            for s in new_specs:
                console.print(f"  + {s}")
    else:
        console.print(
            f"[yellow]No update performed[/yellow] — Egeria returned no ReportType collections "
            f"(or registry was already fresh)."
        )


# ── Click command (for hey_egeria) ────────────────────────────────────────────

@click.command("load-report-specs")
@click.option("--force", is_flag=True, default=False,
              help="Bypass the TTL cache and reload from Egeria unconditionally.")
@click.option("--ttl", "ttl_seconds", default=None, type=int,
              help="Override cache TTL for this call only (seconds). "
                   f"Default: PYEGERIA_REPORT_SPECS_CACHE_TTL env var or {_EGERIA_SPECS_CACHE_TTL}s.")
@click.pass_context
def load_report_specs_cmd(ctx, force: bool, ttl_seconds: int | None) -> None:
    """Refresh the report-spec registry from Egeria (ReportTypes and QuestionSpecs)."""
    c = ctx.obj
    _run(
        view_server=c.view_server,
        view_url=c.view_server_url,
        user=c.userid,
        user_pass=c.password,
        force=force,
        ttl_seconds=ttl_seconds,
    )


# ── Standalone CLI entry point ─────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Refresh the report-spec registry from Egeria."
    )
    parser.add_argument("--force", action="store_true",
                        help="Bypass the TTL cache and reload unconditionally.")
    parser.add_argument("--ttl", dest="ttl_seconds", type=int, default=None,
                        help=f"Override cache TTL (seconds). "
                             f"Default: PYEGERIA_REPORT_SPECS_CACHE_TTL env var or {_EGERIA_SPECS_CACHE_TTL}s.")
    parser.add_argument("--server", dest="server",
                        default=app_config.egeria_view_server,
                        help="Egeria view server name")
    parser.add_argument("--url", dest="url",
                        default=app_config.egeria_view_server_url,
                        help="Egeria platform URL")
    parser.add_argument("--userid", dest="user",
                        default=EGERIA_USER, help="User ID")
    parser.add_argument("--password", dest="password",
                        default=EGERIA_USER_PASSWORD, help="User password")
    args = parser.parse_args()

    try:
        _run(
            view_server=args.server,
            view_url=args.url,
            user=args.user,
            user_pass=args.password,
            force=args.force,
            ttl_seconds=args.ttl_seconds,
        )
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
