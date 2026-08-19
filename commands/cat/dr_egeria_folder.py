"""
Run every Dr.Egeria markdown command file in a folder, in one CLI call.

Semantics agreed with the equivalent folder-batch runner in egeria-workspaces-fs
(compose-configs/egeria-quickstart/PyegeriaWebHandler/bootstrap_batches.py,
documented there in PORTAL_STARTUP.md) so "run all commands in a folder" means
the same thing across both repos:

- Ordering: an optional `_batch.json` manifest at the folder root, shaped
  {"files": ["a.md", "b.md", ...]}, gives the explicit order for those files.
  Any other *.md file in the folder not mentioned there is appended after,
  alphabetically. No manifest at all -> pure alphabetical. A manifest entry
  naming a file that no longer exists on disk is silently dropped (stale
  reference, not an error) -- this mirrors bootstrap_batches.py exactly.
- Only *.md files are processed; `_batch.json` itself is always excluded.
- Every file is expected to be upsert-safe (Create -> Update transitions are
  handled by the processors themselves), so this command is safe to re-run
  against the same folder repeatedly -- there is no staleness tracking here,
  only presence/absence, matching the peer implementation's own assumption.

One deliberate difference from the peer implementation, which always goes
straight to process: this command defaults to --validate (matching this
repo's single-file `dr_egeria` CLI's own default), so a first run against an
unfamiliar folder is safe by default. Pass --process for real writes.

Also deliberately different: files are processed in-process via one shared
EgeriaTech client (one bearer token for the whole run), not one subprocess
per file -- this matches tests/dr-egeria-command-tests/run_dr_tests.py's
existing pattern rather than the peer's asyncio.create_subprocess_exec
approach, since egeria-python's CLI already has direct access to
process_md_file_v2 without needing a subprocess boundary.

Error handling: continues through every file regardless of earlier failures
and reports full per-file results at the end -- the peer implementation
offers this same choice ("stop at first failure" vs. "keep going and report
everything") depending on caller; an interactive CLI invocation is the
"someone explicitly triggered this and wants full visibility" case, so that
is the only mode this command implements. (The peer's own auto-heal path
uses the opposite, stop-on-first-failure, choice for its own unattended
use case -- not applicable here.)
"""
import asyncio
import io
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import click
from loguru import logger
from rich.console import Console
from rich.table import Table

from pyegeria.core.config import settings

# Configure logging (matches commands/cat/dr_egeria.py)
log_format = "{time} | {level} | {function} | {line} | {message} | {extra}"
logger.remove()
logger.add(sys.stderr, level="WARNING", format=log_format, colorize=True)
logger.add("debug_log.log", rotation="1 day", retention="1 week", compression="zip", level="WARNING", format=log_format,
           colorize=True)

app_config = settings.Environment
EGERIA_VIEW_SERVER = os.environ.get("EGERIA_VIEW_SERVER", app_config.egeria_view_server)
EGERIA_VIEW_SERVER_URL = os.environ.get("EGERIA_VIEW_SERVER_URL", app_config.egeria_view_server_url)
EGERIA_USER = settings.User_Profile.user_name or "erinoverview"
EGERIA_USER_PASSWORD = settings.User_Profile.user_pwd or "secret"
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", settings.Environment.egeria_width or 190))

console = Console(width=EGERIA_WIDTH)

MANIFEST_NAME = "_batch.json"


def resolve_batch_order(folder: Path) -> list[str]:
    """
    Resolve the ordered list of *.md filenames to process in `folder`,
    following the same manifest semantics as egeria-workspaces-fs's
    bootstrap_batches.py: explicit order from _batch.json's "files" list
    (dropping any entry that no longer exists on disk), then every other
    *.md file in the folder appended alphabetically.
    """
    all_md = sorted(p.name for p in folder.glob("*.md"))

    manifest_path = folder / MANIFEST_NAME
    ordered: list[str] = []
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text())
        except (json.JSONDecodeError, OSError) as e:
            console.print(f"[yellow]Warning:[/yellow] could not read {MANIFEST_NAME}: {e} -- falling back to alphabetical order")
            manifest = {}
        for name in manifest.get("files", []):
            if name in all_md:
                ordered.append(name)
            # else: stale manifest entry, silently dropped (matches peer semantics)

    remainder = sorted(name for name in all_md if name not in ordered)
    return ordered + remainder


async def run_one_file(input_file: Path, directive: str, client, parse_summary: str,
                        attribute_logs: str, usage_level: str, debug: bool) -> tuple[str, int, int, int, str]:
    """
    Run a single file through process_md_file_v2, capturing its console
    output the same way tests/dr-egeria-command-tests/run_dr_tests.py does,
    and return (filename, success_count, failure_count, warning_count, tail_of_output).
    """
    from md_processing.dr_egeria import process_md_file_v2
    import md_processing.dr_egeria as dre_module

    buf = io.StringIO()
    old_console = dre_module.console
    dre_module.console = Console(file=buf, width=EGERIA_WIDTH, highlight=False, markup=True)

    try:
        await process_md_file_v2(
            input_file=str(input_file),
            output_folder="",
            directive=directive,
            client=client,
            parse_summary=parse_summary,
            attribute_logs=attribute_logs,
            usage_level=usage_level,
            summary_only=True,
            debug=debug,
        )
        output = buf.getvalue()
    except Exception as e:
        output = buf.getvalue() + f"\nEXCEPTION: {e}\n"
    finally:
        dre_module.console = old_console

    successes = output.count("SUCCESS")
    failures = output.count("FAILURE")
    warnings = output.count("WARNING")
    tail = output[-800:] if failures else ""
    return input_file.name, successes, failures, warnings, tail


@click.command("dr_egeria_folder", help="Run every Dr.Egeria markdown command file in a folder.")
@click.argument("folder", type=click.Path(exists=True, file_okay=False, dir_okay=True), required=True)
@click.option("--directive", default="validate", help="How to process each file (display/validate/process). "
              "Overridden by --validate or --process flags.",
              type=click.Choice(["display", "validate", "process"], case_sensitive=False), prompt=False)
@click.option("--validate", "do_validate", is_flag=True, default=False,
              help="Shortcut: validate every file without making changes (overrides --directive; default behavior)")
@click.option("--process", "do_process", is_flag=True, default=False,
              help="Shortcut: execute all commands in every file and make permanent changes in Egeria")
@click.option("--server", default=EGERIA_VIEW_SERVER, help="Egeria view server to use.")
@click.option("--url", default=EGERIA_VIEW_SERVER_URL, help="URL of Egeria platform to connect to")
@click.option("--userid", default=EGERIA_USER, help="Egeria user. Overrides EGERIA_USER (env var or .env file).")
@click.option("--user_pass", default=EGERIA_USER_PASSWORD,
              help="Egeria user password. Overrides EGERIA_USER_PASSWORD (env var or .env file).")
@click.option("--parse-summary", default="none", help="When to show parse summaries",
              type=click.Choice(["all", "errors", "none"], case_sensitive=False))
@click.option("--attribute-logs", default="info", help="Per-attribute log verbosity",
              type=click.Choice(["debug", "info", "none"], case_sensitive=False))
@click.option("--advanced", is_flag=True, default=False,
              help="Use Advanced usage level -- shows additional attributes (default: Basic)")
@click.option("--debug", is_flag=True, default=False, help="Print each Egeria API request URL and body to the console")
@click.option("--results-file", default="", help="Optional path to also write the full per-file report to.")
@logger.catch
def dr_egeria_folder(folder: str, directive: str, do_validate: bool, do_process: bool,
                      server: str, url: str, userid: str, user_pass: str,
                      parse_summary: str, attribute_logs: str, advanced: bool,
                      debug: bool, results_file: str) -> None:
    """
    Discover and run every *.md file in FOLDER through Dr.Egeria, in order
    (see module docstring for the _batch.json manifest / ordering rules).
    Every file is processed regardless of earlier failures; a full per-file
    summary is printed (and optionally written to --results-file) at the end.
    """
    if do_process:
        directive = "process"
    elif do_validate:
        directive = "validate"

    usage_level = "Advanced" if advanced else "Basic"
    folder_path = Path(folder)

    md_files = resolve_batch_order(folder_path)
    if not md_files:
        console.print(f"[yellow]No *.md files found in {folder_path}[/yellow]")
        return

    console.print(f"[bold]Dr.Egeria folder batch[/bold]: {folder_path}  |  directive={directive}  |  {len(md_files)} file(s)")
    for name in md_files:
        console.print(f"  - {name}")

    from pyegeria import EgeriaTech
    client = EgeriaTech(server, url, userid, user_pass)
    client.create_egeria_bearer_token()

    results = []
    for name in md_files:
        input_path = folder_path / name
        result = asyncio.run(run_one_file(
            input_path, directive, client, parse_summary, attribute_logs, usage_level, debug
        ))
        results.append(result)
        fname, s, f, w, _tail = result
        status = "[red]FAILED[/red]" if f else "[green]ok[/green]"
        console.print(f"  {status}  {fname}  ({s} success, {f} failure, {w} warning)")

    table = Table(title="Dr.Egeria Folder Batch Summary")
    table.add_column("File")
    table.add_column("Success", justify="right")
    table.add_column("Failure", justify="right")
    table.add_column("Warning", justify="right")

    total_s = total_f = total_w = 0
    lines = [f"Dr.Egeria Folder Batch Run -- {datetime.now()}", f"Folder: {folder_path}  Directive: {directive}", ""]
    for fname, s, f, w, tail in results:
        table.add_row(fname, str(s), str(f), str(w))
        total_s += s
        total_f += f
        total_w += w
        lines.append(f"{fname}: {s} success, {f} failure, {w} warning")
        if tail:
            lines.append(f"  last output:\n{tail}\n")

    console.print(table)
    console.print(f"\n[bold]TOTALS[/bold]: {total_s} success, {total_f} failure, {total_w} warning")
    lines.append(f"\nTOTALS: {total_s} success, {total_f} failure, {total_w} warning")

    if results_file:
        Path(results_file).write_text("\n".join(lines))
        console.print(f"Full report written to: {results_file}")

    if total_f:
        sys.exit(1)


if __name__ == "__main__":
    dr_egeria_folder()
