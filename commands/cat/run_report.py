#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Generic list command that wraps exec_report_spec and adds TABLE output.

- TABLE: renders results as a paged Rich table; table title comes from get_report_spec_heading().
- MD, REPORT, FORM, HTML, MERMAID, LIST: writes the output to a timestamped file in the outbox.

Environment variables used (with defaults aligned to other commands):
- EGERIA_VIEW_SERVER, EGERIA_VIEW_SERVER_URL
- EGERIA_USER, EGERIA_USER_PASSWORD
- EGERIA_WIDTH, EGERIA_JUPYTER
- EGERIA_ROOT_PATH, EGERIA_OUTBOX_PATH
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from rich import box
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

from pyegeria import config_logging
from pyegeria.config import settings
from pyegeria._exceptions import PyegeriaException, print_exception_response
from pyegeria.base_report_formats import get_report_spec_heading, select_report_spec
from pyegeria.format_set_executor import exec_report_spec
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")


app_config = settings.Environment
# config_logging()

TEXT_FILE_FORMATS = {"MD", "REPORT", "FORM", "HTML", "MERMAID", "LIST", "DICT", "JSON"}


def list_generic(
    report_spec: str,
    *,
    output_format: str = "TABLE",
    params: Dict[str, Any] | None = None,
    view_server: str = app_config.egeria_view_server,
    view_url: str = app_config.egeria_view_server_url,
    user: str = EGERIA_USER,
    user_pass: str = EGERIA_USER_PASSWORD,
    jupyter: bool = app_config.egeria_jupyter,
    width: int = app_config.console_width,
    prompt_missing: bool = False,
    write_file: bool = False,
    render_table: bool = False,
    table_caption: str | None = None,
    use_pager: bool = True,
) -> Dict[str, Any]:
    """
    Execute a report spec and return results, usable both as a library function and CLI.

    Required vs Optional parameters are derived from the report spec's action:
    - Required: fmt.action.required_params (or action.user_params) not supplied by spec_params.
    - Optional: fmt.action.optional_params.

    Behavior:
    - If prompt_missing is True, will interactively Prompt.ask for any missing required params.
    - If prompt_missing is False and required params are missing, raises ValueError.
    - For output_format == "TABLE": returns a JSON payload for table rendering; no file I/O by default.
      - If render_table=True, this function will also render a Rich table immediately (useful for remote/programmatic calls).
        You can customize rendering via table_caption and use_pager.
    - For narrative formats (MD, REPORT, FORM, MERMAID, LIST, HTML):
      - If write_file=True, writes to outbox and returns the file path in the result.
      - Otherwise returns the text content in the result.

    Parameters (additional rendering options)
    - render_table: bool (default False) — when True and output_format==TABLE, render the Rich table directly.
    - table_caption: Optional[str] — custom caption; defaults to "View Server '{view_server}' @ Platform - {view_url}".
    - use_pager: bool (default True) — wrap the table output in console.pager().

    Returns a dict with keys like:
      {"kind": "table"|"text"|"json"|"empty", "data"|"content", "file_path"?, "heading", "required", "optional", "rendered"?}
    """
    params = dict(params or {})
    ofmt = (output_format or "TABLE").upper()

    # Load format spec to introspect required/optional params
    fmt = select_report_spec(report_spec, ofmt if ofmt not in {"TABLE", "MD", "FORM", "LIST"} else "DICT")
    if not fmt:
        raise ValueError(f"Report spec '{report_spec}' not found for format '{ofmt}'.")
    action = fmt.get("action", {}) or {}
    required_params = action.get("required_params", action.get("user_params", [])) or []
    optional_params = action.get("optional_params", []) or []
    spec_params = action.get("spec_params", {}) or {}

    # Identify missing required params (not provided by caller and not satisfied by spec_params)
    missing = [p for p in required_params if params.get(p) in (None, "") and p not in spec_params]

    if missing:
        if prompt_missing:
            # Prompt user for each missing required param
            for p in missing:
                val = Prompt.ask(f"Enter value for required parameter '{p}'")
                params[p] = val
        else:
            raise ValueError(f"Missing required parameter(s): {', '.join(missing)}")

    # Map only TABLE to DICT for data retrieval; pass through other formats
    # mapped_format = "DICT" if ofmt == "TABLE" else ofmt
    mapped_format = ofmt
    try:
    # Execute
        result = exec_report_spec(
            report_spec,
            output_format=mapped_format,
            params=params,
            view_server=view_server,
            view_url=view_url,
            user=user,
            user_pass=user_pass,
        )
    except ValueError as e:
        console = Console(
            style="bold bright_white on black",
        )
        console.print(f"Error executing report: {e}")
        sys.exit(1)

    # Normalize/augment response
    if result.get("kind") == "empty":
        return {
            "kind": "empty",
            "heading": get_report_spec_heading(report_spec) or f"Report: {report_spec}",
            "required": required_params,
            "optional": optional_params,
        }

    # For TABLE, optionally render Rich table and return json data for caller
    if ofmt == "TABLE":
        if result.get("kind") == "json":
            heading = get_report_spec_heading(report_spec) or f"Report: {report_spec}"
            data = result.get("data")
            rendered = False
            if render_table:
                console = Console(
                    style="bold bright_white on black",
                    width=width,
                    force_terminal=not jupyter,
                )
                caption = table_caption or f"View Server '{view_server}' @ Platform - {view_url}"
                _render_table(console, heading, caption, data, use_pager=use_pager)
                rendered = True
            return {
                "kind": "table",
                "heading": heading,
                "data": data,
                "required": required_params,
                "optional": optional_params,
                "rendered": rendered,
            }
        # Fallback: unexpected shape
        return {
            "kind": "unknown",
            "raw": result,
            "required": required_params,
            "optional": optional_params,
        }

    # Narrative formats (all non-TABLE should generate files)
    content: str = ""
    if result.get("kind") == "text":
        # Already-rendered text like Markdown or HTML
        content = str(result.get("content", ""))
    elif result.get("kind") == "json":
        data = result.get("data")
        # For DICT/JSON explicitly produce raw JSON text; otherwise fallback to fenced JSON
        if ofmt in {"DICT", "JSON"}:
            content = json.dumps(data, indent=2)
        else:
            content = "```json\n" + json.dumps(data, indent=2) + "\n```"
    else:
        content = json.dumps(result, indent=2, default=str)

    if write_file or ofmt in TEXT_FILE_FORMATS:
        # Determine suffix for file naming
        suffix = ofmt
        path = write_output_file(content, report_spec, suffix)
        return {
            "kind": "text" if ofmt not in {"DICT", "JSON"} else "json",
            "content": content,
            "file_path": path,
            "heading": get_report_spec_heading(report_spec) or f"Report: {report_spec}",
            "required": required_params,
            "optional": optional_params,
        }

    return {
        "kind": "text",
        "content": content,
        "heading": get_report_spec_heading(report_spec) or f"Report: {report_spec}",
        "required": required_params,
        "optional": optional_params,
    }


def _flatten(item: Any, parent_key: str = "", sep: str = ".") -> Dict[str, Any]: 
    """Flatten nested dict-like objects into a single level using dot-notation keys."""
    flat: Dict[str, Any] = {}
    if isinstance(item, Mapping):
        for k, v in item.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else str(k)
            flat.update(_flatten(v, new_key, sep))
    elif isinstance(item, (list, tuple)):
        # Represent short sequences inline; longer ones as counts
        if len(item) <= 3:
            flat[parent_key or "list"] = ", ".join([str(x) for x in item])
        else:
            flat[parent_key or "list"] = f"{len(item)} items"
    else:
        flat[parent_key or "value"] = item
    return flat


def _collect_columns(rows: Sequence[Mapping[str, Any]], max_cols: int = 12) -> List[str]:
    """Collect a union of keys across rows, up to max_cols, keeping a stable ordering."""
    seen: List[str] = []
    for row in rows:
        for k in row.keys():
            if k not in seen:
                seen.append(k)
            if len(seen) >= max_cols:
                return seen
    return seen


def _ensure_rows(data: Any) -> List[Mapping[str, Any]]:
    """Convert result data into a list of row mappings suitable for table rendering."""
    if data is None:
        return []
    if isinstance(data, list):
        rows: List[Mapping[str, Any]] = []
        for item in data:
            if isinstance(item, Mapping):
                rows.append(_flatten(item))
            else:
                rows.append({"value": item})
        return rows
    if isinstance(data, Mapping):
        # If a single object contains a list-like 'elements' or similar, prefer that
        for key in ("elements", "items", "results"):
            if isinstance(data.get(key), list):
                return _ensure_rows(data[key])
        return [_flatten(data)]
    # Fallback: scalar
    return [{"value": data}]


def _render_table(console: Console, title: str, caption: str, data: Any, use_pager: bool = True) -> None:
    rows = _ensure_rows(data)
    if not rows:
        console.print("No results found.")
        return

    columns = _collect_columns(rows)

    table = Table(
        title=title,
        style="bright_white on black",
        header_style="bright_white on dark_blue",
        title_style="bold white on black",
        caption_style="white on black",
        show_lines=True,
        box=box.ROUNDED,
        caption=caption,
        expand=True,
    )
    for col in columns:
        table.add_column(str(col))

    for row in rows:
        table.add_row(*[str(row.get(col, "")) for col in columns])

    # Page the table if it's large
    if use_pager:
        with console.pager():
            console.print(table)
    else:
        console.print(table)


def write_output_file(content: str, report_spec: str, suffix: str) -> str:
    # Base directory is outbox/report_spec specific folder
    file_path = os.path.join(app_config.pyegeria_root, app_config.dr_egeria_outbox, f"{report_spec}")
    ts = time.strftime("%Y-%m-%d-%H-%M-%S")
    safe_spec = "".join(c for c in report_spec if c.isalnum() or c in ("-", "_", "+", ".", " ")).strip().replace(" ", "_")
    # Determine extension by content type rules
    if suffix in {"MD", "REPORT", "FORM", "MERMAID", "LIST"}:
        ext = ".md"
    elif suffix in {"HTML"}:
        ext = ".html"
    elif suffix in {"DICT", "JSON"}:
        ext = ".json"
    else:
        ext = ".txt"
    file_name = f"{safe_spec}-{ts}-{suffix}{ext}"
    full_file_path = os.path.join(file_path, file_name)
    os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
    with open(full_file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return full_file_path


def main():
    parser = argparse.ArgumentParser(description="Generic list command using exec_report_spec")
    parser.add_argument("--report", dest="report_spec", help="Report spec name to execute (see report specs)")
    parser.add_argument("--output-format", dest="output_format", default="TABLE",
                        choices=["TABLE", "MD", "REPORT", "FORM", "HTML", "MERMAID", "LIST", "JSON", "DICT"],
                        help="Output rendering format")
    parser.add_argument("--server", dest="server", help="Egeria view server name", default=app_config.egeria_view_server)
    parser.add_argument("--url", dest="url", help="Egeria platform URL", default=app_config.egeria_view_server_url)
    parser.add_argument("--userid", dest="user", help="User Id", default=EGERIA_USER)
    parser.add_argument("--password", dest="password", help="User Password", default=EGERIA_USER_PASSWORD)
    # Allow arbitrary parameters as JSON or repeated key=value
    parser.add_argument("--params-json", dest="params_json", help="JSON string of parameters for the report spec")
    parser.add_argument("--param", dest="params_kv", action="append", default=[], help="Repeated key=value parameters")

    args = parser.parse_args()

    # Prompt for report spec if not provided
    report_spec = args.report_spec or Prompt.ask("Enter the report spec to execute").strip()
    output_format = (args.output_format or "TABLE").upper()

    # Build params dict
    params: Dict[str, Any] = {}
    if args.params_json:
        try:
            parsed = json.loads(args.params_json)
            if isinstance(parsed, dict):
                params.update(parsed)
        except Exception:
            pass
    for kv in (args.params_kv or []):
        if "=" in kv:
            k, v = kv.split("=", 1)
            params[k.strip()] = v.strip()

    console = Console(
        style="bold bright_white on black",
        width=app_config.console_width,
        force_terminal=not app_config.egeria_jupyter,
    )

    try:
        # Use shared function with prompting enabled for missing required params
        write_file = output_format in TEXT_FILE_FORMATS
        result = list_generic(report_spec, output_format=output_format, params=params, view_server=args.server,
                              view_url=args.url, user=args.user, user_pass=args.password, jupyter=app_config.egeria_jupyter,
                              width=app_config.console_width, prompt_missing=True, write_file=write_file)

        if result.get("kind") == "empty":
            console.print("No results found.")
            return

        if output_format == "TABLE":
            heading = result.get("heading") or (get_report_spec_heading(report_spec) or f"Report: {report_spec}")
            caption = f"View Server '{args.server}' @ Platform - {args.url}"
            _render_table(console, heading, caption, result.get("data"))
            return

        # For narrative formats, either a file was written or content is returned
        fpath = result.get("file_path")
        if fpath:
            print(f"\n==> Output written to {fpath}")
        else:
            print(result.get("content", ""))

    except PyegeriaException as e:
        print_exception_response(e)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
