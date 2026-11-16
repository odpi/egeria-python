#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

DEPRECATED command name, kept until the next release: it now runs the spec cache's sync
(pyegeria.view.egeria_spec_cache.sync_report_specs, the same as `pyegeria report-specs sync`), which
loads the report specs held in Egeria into the cache the registry's EGERIA tier reads. It used to run
the legacy ReportType:: loader (load_egeria_report_specs), deprecated and removed in the next release.

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
    # The owner's direction (2026-11-14): our own callers move off the deprecated legacy ReportType:: loader
    # (load_egeria_report_specs, removed in the next release). This command now runs the spec cache's sync, the
    # system of record for Egeria-held report specs, exactly as `pyegeria report-specs sync` does.
    console.print(DEPRECATION_WORDS)
    if force or ttl_seconds is not None:
        console.print("[dim]--force and --ttl applied to the legacy loader's cache and are ignored now: a sync "
                      "reads Egeria each time.[/dim]")
    from pyegeria.view.egeria_spec_cache import SyncAlreadyRunning, sync_report_specs
    client = EgeriaTech(view_server, view_url, user_id=user, user_pwd=user_pass)
    start = time.perf_counter()
    try:
        client.create_egeria_bearer_token(user, user_pass)
        report = sync_report_specs(client)
    except SyncAlreadyRunning as exc:
        console.print(f"[yellow]{exc}[/yellow]")
        return
    finally:
        try:
            client.close_session()
        except Exception:  # noqa: BLE001
            pass
    console.print(report.render())
    console.print(f"[dim]({time.perf_counter() - start:.2f}s)[/dim]")


#: Printed by load-report-specs / load_report_specs since it moved to the spec cache.
DEPRECATION_WORDS = ("[yellow]load-report-specs is deprecated[/yellow]: it ran the legacy ReportType:: loader, "
                     "which will be removed in the next release. It now runs the spec "
                     "cache's sync (`pyegeria report-specs sync`), which loads Egeria-held report specs.")


#: An empty result from the legacy ReportType:: loader, confirmed or not (the legacy-loader ruling, 2026-11-14).
NO_LEGACY_WORDS = "No legacy ReportType collections found (Egeria-held specs load through the spec cache)."


def load_status_words(status: dict, elapsed: float, new_specs: list) -> str:
    """Words for how the deprecated load_egeria_report_specs ended (85f5bc15 read-back R1): one sentence per
    status, never "no ReportType collections" unless Egeria confirmed the end. Kept for anyone still calling the
    legacy loader until the next release; this command itself now runs the spec cache's sync."""
    kind, count = status.get("status"), status.get("count") or 0
    retry_at, error = status.get("retry_at"), status.get("error")
    if kind in ("loaded", "registered_unconfirmed") and not count:
        # the legacy-loader ruling: never imply specs are missing (they load through the spec cache)
        return NO_LEGACY_WORDS
    if kind == "loaded":
        return (f"[green]Registry updated[/green] from Egeria in {elapsed:.2f}s: {count} ReportType(s) read, "
                f"{len(new_specs)} new spec(s) added.")
    if kind == "registered_unconfirmed":
        return (f"[yellow]Registered {count} spec(s)[/yellow] in {elapsed:.2f}s; Egeria didn't confirm there "
                f"are no more; will re-read after {retry_at}.")
    if kind == "retry_window":
        return (f"[yellow]Not re-read[/yellow]: the last read wasn't confirmed complete; next read after {retry_at} "
                f"(use --force).")
    if kind == "fresh":
        return "[green]Registry is fresh[/green]: the last confirmed load is within its TTL (use --force)."
    if kind == "failed":
        return f"[red]Not loaded[/red]: Egeria couldn't be queried ({error}); nothing was marked loaded."
    return f"[yellow]Load ended without a status[/yellow] ({elapsed:.2f}s)."


# ── Click command (for hey_egeria) ────────────────────────────────────────────

@click.command("load-report-specs")
@click.option("--force", is_flag=True, default=False,
              help="Ignored (it applied to the legacy loader's cache); a sync reads Egeria each time.")
@click.option("--ttl", "ttl_seconds", default=None, type=int,
              help="Ignored (it applied to the legacy loader's cache).")
@click.pass_context
def load_report_specs_cmd(ctx, force: bool, ttl_seconds: int | None) -> None:
    """DEPRECATED: syncs the report specs held in Egeria into the spec cache (use `pyegeria report-specs sync`)."""
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
        description="DEPRECATED: sync the report specs held in Egeria into the spec cache "
                    "(use `pyegeria report-specs sync`)."
    )
    parser.add_argument("--force", action="store_true",
                        help="Ignored (it applied to the legacy loader's cache).")
    parser.add_argument("--ttl", dest="ttl_seconds", type=int, default=None,
                        help="Ignored (it applied to the legacy loader's cache).")
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
