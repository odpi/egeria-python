"""
Run every Dr.Egeria markdown command file in a folder, in one CLI call.

Semantics agreed with the equivalent folder-batch runner in egeria-workspaces-fs
(compose-configs/egeria-quickstart/PyegeriaWebHandler/bootstrap_batches.py,
documented there in PORTAL_STARTUP.md) so "run all commands in a folder" means
the same thing across both repos:

- Ordering: an optional `_batch.json` manifest in a folder gives the explicit
  order in its "files" list. An entry is a file ("a.md"), a file in a
  subfolder ("sub/x.md"), or a whole subfolder ("sub/"), which runs in place
  in its own order (its own `_batch.json`, recursively). Anything not listed
  is appended after: *.md files alphabetically, then subfolders
  alphabetically, each flagged with a warning when the folder has a "files"
  list. A stale entry is skipped with a warning. No manifest -> alphabetical
  files, then alphabetical subfolders.
- Skipped: README.md, and the subfolders dr-egeria-outbox, egeria-outbox,
  logs, data, templates, __pycache__, .ipynb_checkpoints and any dot-folder
  (the outbox folders hold processed copies with live commands), unless named
  explicitly in "files". "exclude" in `_batch.json` skips more.
- Run-as user: a "userid" in `_batch.json` (folder default, inherited by
  subfolders) or per entry as {"file": "a.md", "userid": "juleskeeper"}; the
  nearest declaration wins. Passwords never come from the manifest:
  EGERIA_BOOTSTRAP_PASSWORD_<USERID> (upper-cased), else --user_pass. Files
  with no declared userid run as --userid. --no-manifest-userids runs
  everything as --userid.
- A file reachable twice (listed directly and via its folder, or through a
  symlink) runs once.
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


_SKIP_SUBDIRS = {"logs", ".ipynb_checkpoints", "__pycache__", "dr-egeria-outbox",
                 "egeria-outbox", "data", "templates"}
_SKIP_FILES = {"readme.md"}


def _read_manifest(folder: Path, warnings: list[str]) -> dict:
    manifest_path = folder / MANIFEST_NAME
    if not manifest_path.is_file():
        return {}
    try:
        data = json.loads(manifest_path.read_text())
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError) as e:
        warnings.append(f"could not read {manifest_path}: {e} -- that folder falls back to alphabetical order")
        return {}


def _entry_parts(entry) -> tuple:
    """A "files" entry is a plain string, or {"file": ..., "userid": ...}."""
    if isinstance(entry, str):
        return entry, None
    if isinstance(entry, dict) and isinstance(entry.get("file"), str):
        return entry["file"], (str(entry["userid"]) if entry.get("userid") else None)
    return None, None


def _is_md(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() == ".md"


def resolve_batch(folder: Path) -> tuple[list[tuple[str, str | None]], list[str]]:
    """
    Resolve the ordered (relative path, userid) pairs to process under
    `folder`, plus any warnings about the ordering, following the same
    manifest semantics as egeria-workspaces-fs's bootstrap_batches.py (see the
    module docstring). userid is None where no manifest declares one.
    """
    out: list[tuple[str, str | None]] = []
    warnings: list[str] = []
    seen_files: set[Path] = set()
    visited_dirs: set[Path] = set()

    def expand(d: Path, prefix: str, inherited_user: str | None) -> None:
        real = d.resolve()
        if real in visited_dirs:
            warnings.append(f"{prefix or './'} is reachable twice (symlink loop?) -- expanded once")
            return
        visited_dirs.add(real)

        manifest = _read_manifest(d, warnings)
        folder_user = str(manifest["userid"]) if manifest.get("userid") else inherited_user
        listed = manifest.get("files") or []
        excluded = {str(x).rstrip("/") for x in (manifest.get("exclude") or [])}
        placed: set[str] = set()

        def add_file(p: Path, rel: str, user: str | None) -> None:
            rp = p.resolve()
            if rp in seen_files:
                return
            seen_files.add(rp)
            out.append((rel, user))

        for entry in listed:
            raw, entry_user = _entry_parts(entry)
            if raw is None:
                warnings.append(f"{MANIFEST_NAME} in {prefix or './'} has an unreadable files entry {entry!r} -- skipped")
                continue
            name = raw.rstrip("/")
            if name in excluded:
                continue
            p = d / name
            user = entry_user or folder_user
            if "/" not in name:
                placed.add(name)  # a nested entry ("sub/x.md") leaves the rest of sub/ to the remainder pass
            if p.is_dir():
                expand(p, f"{prefix}{name}/", user)
            elif _is_md(p):
                add_file(p, prefix + name, user)
            else:
                warnings.append(f"{MANIFEST_NAME} in {prefix or './'} lists {raw!r}, which isn't there -- skipped")

        has_order = bool(listed)
        children = sorted(d.iterdir(), key=lambda c: c.name)
        for c in children:
            if (_is_md(c) and c.name not in placed and c.name not in excluded
                    and c.name.lower() not in _SKIP_FILES):
                if has_order:
                    warnings.append(f"{prefix}{c.name} isn't in {MANIFEST_NAME}'s files list -- "
                                    "runs after the listed files, alphabetically")
                add_file(c, prefix + c.name, folder_user)
        for c in children:
            if (c.is_dir() and c.name not in placed and c.name not in excluded
                    and c.name not in _SKIP_SUBDIRS and not c.name.startswith(".")):
                before = len(out)
                expand(c, f"{prefix}{c.name}/", folder_user)
                if has_order and len(out) > before:
                    warnings.append(f"{prefix}{c.name}/ isn't in {MANIFEST_NAME}'s files list -- "
                                    "runs after the listed files, alphabetically")

    expand(folder, "", None)
    return out, warnings


def resolve_batch_order(folder: Path) -> list[str]:
    """Ordered relative paths only -- see resolve_batch."""
    return [rel for rel, _user in resolve_batch(folder)[0]]


def password_for(userid: str, default: str) -> str:
    """A manifest names a user, never a password: EGERIA_BOOTSTRAP_PASSWORD_<USERID>
    (the same variable the Portal reads), else the CLI's --user_pass."""
    return os.environ.get(f"EGERIA_BOOTSTRAP_PASSWORD_{userid.upper()}") or default


async def run_one_file(input_file: Path, display_name: str, directive: str, client, parse_summary: str,
                        attribute_logs: str, usage_level: str, debug: bool) -> tuple[str, int, int, int, str]:
    """
    Run a single file through process_md_file_v2, capturing its console
    output the same way tests/dr-egeria-command-tests/run_dr_tests.py does,
    and return (relative name, success_count, failure_count, warning_count, tail_of_output).
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
    return display_name, successes, failures, warnings, tail


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
@click.option("--no-manifest-userids", is_flag=True, default=False,
              help="Ignore userid settings in _batch.json and run every file as --userid.")
@logger.catch
def dr_egeria_folder(folder: str, directive: str, do_validate: bool, do_process: bool,
                      server: str, url: str, userid: str, user_pass: str,
                      parse_summary: str, attribute_logs: str, advanced: bool,
                      debug: bool, results_file: str, no_manifest_userids: bool) -> None:
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

    plan, order_warnings = resolve_batch(folder_path)
    if no_manifest_userids:
        plan = [(rel, None) for rel, _user in plan]
    if not plan:
        console.print(f"[yellow]No *.md files found in {folder_path}[/yellow]")
        return

    console.print(f"[bold]Dr.Egeria folder batch[/bold]: {folder_path}  |  directive={directive}  |  {len(plan)} file(s)")
    for rel, file_user in plan:
        console.print(f"  - {rel}  [dim](as {file_user or userid})[/dim]")
    for w in order_warnings:
        console.print(f"  [yellow]![/yellow] {w}")

    from pyegeria import EgeriaTech
    clients: dict[str, EgeriaTech] = {}

    def client_for(user: str) -> EgeriaTech:
        """One client (one bearer token) per user for the whole run."""
        if user not in clients:
            pwd = user_pass if user == userid else password_for(user, user_pass)
            c = EgeriaTech(server, url, user, pwd)
            c.create_egeria_bearer_token()
            clients[user] = c
        return clients[user]

    results = []
    for rel, file_user in plan:
        input_path = folder_path / rel
        run_as = file_user or userid
        try:
            client = client_for(run_as)
        except Exception as e:  # noqa: BLE001 -- report per file, keep going
            result = (rel, 0, 1, 0, f"could not sign in as {run_as}: {e}")
        else:
            result = asyncio.run(run_one_file(
                input_path, rel, directive, client, parse_summary, attribute_logs, usage_level, debug
            ))
        results.append(result)
        fname, s, f, w, _tail = result
        status = "[red]FAILED[/red]" if f else "[green]ok[/green]"
        console.print(f"  {status}  {fname}  as {run_as}  ({s} success, {f} failure, {w} warning)")

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
