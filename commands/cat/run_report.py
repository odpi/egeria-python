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
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import click
from rich import box
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

from pyegeria.core.config import settings
from pyegeria.core._exceptions import PyegeriaException, print_exception_response
from pyegeria.view.base_report_formats import get_report_spec_heading, select_report_spec, get_report_registry
from pyegeria.view.format_set_executor import exec_report_spec
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")


app_config = settings.Environment
# config_logging()

# Note: CLI --param/--params-json must use snake_case names (e.g., metadata_element_subtypes). The
# underlying clients serialize to camelCase for on-wire Egeria JSON automatically.
TEXT_FILE_FORMATS = {"MD", "REPORT", "REPORT-GRAPH", "FORM", "HTML", "MERMAID", "LIST", "DICT", "JSON"}


def list_generic(
    report_spec: str,
    *,
    output_format: str = "TABLE",
    params: Dict[str, Any] | None = None,
    view_server: str = app_config.egeria_view_server,
    view_url: str = app_config.egeria_view_server_url,
    user: str = EGERIA_USER,
    user_pass: str = EGERIA_USER_PASSWORD,
    jupyter: bool = settings.Environment.egeria_jupyter,
    width: int = settings.Environment.egeria_width,
    prompt_missing: bool = False,
    write_file: bool = False,
    render_table: bool = False,
    table_caption: str | None = None,
    use_pager: bool = True,
    table_shape: str = "rows",
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

    if ofmt == "DOCUMENT":
        # SD-1: a document spec's exporter takes its own parameters; exec_report_spec refuses a
        # spec that is not a document spec, and the caller writes the file (write_document).
        return exec_report_spec(report_spec, output_format="DOCUMENT", params=params, view_server=view_server,
                                view_url=view_url, user=user, user_pass=user_pass)

    # Load format spec to introspect required/optional params
    # First, validate existence of the report regardless of type
    fmt_any = select_report_spec(report_spec, "ANY")
    if not fmt_any:
        raise ValueError(
            f"Unknown report spec '{report_spec}'. Run 'list_reports' to see available reports."
        )

    # Then resolve the specific output format (TABLE maps to DICT rendering under the hood)
    requested_type = ofmt
    lookup_type = ofmt if ofmt not in {"TABLE", "MD", "FORM", "LIST"} else "DICT"
    fmt = select_report_spec(report_spec, lookup_type)
    if not fmt:
        # Provide actionable message with available types
        available: list[str] = []
        try:
            registry = get_report_registry()
            fs = registry.get(report_spec)
            if fs is None:
                for key, v in registry.items():
                    aliases = getattr(v, "aliases", []) or []
                    if report_spec in aliases:
                        fs = v
                        break
            if fs is not None:
                seen = set()
                for f in getattr(fs, "formats", []) or []:
                    for t in getattr(f, "types", []) or []:
                        seen.add(str(t).upper())
                available = sorted(seen)
        except Exception:
            pass
        hint = f" Available formats: {', '.join(available)}." if available else ""
        raise ValueError(
            f"Report spec '{report_spec}' does not support requested output_format '{requested_type}'.{hint} "
            f"Run 'list_reports' to see available reports."
        )
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

    if ofmt == "TABLE" and table_shape == "structured":
        # R3: the structured table, drawn natively (run_report's own CLI asks for it; the library default
        # stays "rows", which the Textual TUI and hey_egeria commands read).
        result = exec_report_spec(report_spec, output_format="TABLE", table_shape="structured", params=params,
                                  view_server=view_server, view_url=view_url, user=user, user_pass=user_pass)
        heading = get_report_spec_heading(report_spec) or f"Report: {report_spec}"
        rendered = False
        if render_table and result.get("kind") == "table":
            console = Console(width=width, force_terminal=not jupyter)
            render_structured_table(console, result, heading,
                                    table_caption or f"View Server '{view_server}' @ Platform - {view_url}",
                                    use_pager=use_pager)
            rendered = True
        return {"kind": result.get("kind"), "heading": heading, "structured": result,
                "notes": list(result.get("notes") or []), "rendered": rendered}

    # Map only TABLE to DICT for data retrieval; pass through other formats
    mapped_format = "DICT" if ofmt == "TABLE" else ofmt
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
    if result is None:
        click.echo(f"\nNo data returned for report: {report_spec}\n")
        return {
            "kind": "empty",
            "heading": get_report_spec_heading(report_spec) or f"Report: {report_spec}",
            "required": required_params,
            "optional": optional_params,
        }

    if result.get("kind") == "empty":
        click.echo(f"No data returned for report: {report_spec}")
        return {
            "kind": "empty",
            "heading": get_report_spec_heading(report_spec) or f"Report: {report_spec}",
            "required": required_params,
            "optional": optional_params,
        }

    # For TABLE, optionally render Rich table and return json data for caller
    if ofmt in {"TABLE", "DICT"}:
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
                _render_table(console, heading, caption, data, use_pager=use_pager, notes=result.get("notes"))
                rendered = True
            return {
                "kind": "table",
                "heading": heading,
                "data": data,
                "notes": list(result.get("notes") or []),
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


#: How many scalar list items a CLI cell shows before "+N more" (fix-now F4), and the width a joined
#: cell may reach before items are cut at an item boundary.
CELL_ITEMS = 3
CELL_CHARS = 120


def _object_name(x: Mapping[str, Any]) -> str:
    name = x.get("name") or x.get("displayName") or x.get("qualifiedName") or x.get("guid")
    if name:
        return str(name)
    str_vals = [v for v in x.values() if isinstance(v, str) and v.strip()]
    return str_vals[0] if str_vals else f"(unnamed {x.get('type') or 'item'})"


def _join_capped(items: List[str], *, max_items: Optional[int] = None, max_chars: int = CELL_CHARS) -> str:
    """Items joined with ", ", cut at an item boundary when there are more than `max_items` or the
    cell would pass `max_chars`, always with "+N more" (fix-now F4: never only a count)."""
    shown: List[str] = []
    for item in items:
        if max_items is not None and len(shown) >= max_items:
            break
        if shown and len(", ".join(shown + [item])) > max_chars:
            break
        shown.append(item)
    if not shown and items:
        shown = [items[0]]
    rest = len(items) - len(shown)
    return ", ".join(shown) + (f" (+{rest} more)" if rest else "")


def _cell(value: Any) -> str:
    """One CLI table cell for a nested value (fix-now F4)."""
    if isinstance(value, Mapping):  # a map is one "k: v; ..." cell, never exploded into columns
        return "; ".join(f"{k}: {_cell(v)}" for k, v in value.items())
    if isinstance(value, (list, tuple)):
        if not value:
            return ""
        if all(isinstance(x, Mapping) for x in value):
            return _join_capped([_object_name(x) for x in value])
        items = [str(x) for x in value]
        if len(", ".join(items)) <= CELL_CHARS // 2:  # the whole list fits: show all of it
            return ", ".join(items)
        return _join_capped(items, max_items=CELL_ITEMS)
    return "" if value is None else str(value)


def _flatten(item: Any, parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    """One table row from a result row: each top-level key is a column; a nested map is one
    "k: v; ..." cell and a list is a joined cell with "+N more" (fix-now F4), so nested values never
    explode into dotted columns that push the author's columns out."""
    if isinstance(item, Mapping):
        return {(f"{parent_key}{sep}{k}" if parent_key else str(k)): _cell(v) for k, v in item.items()}
    return {parent_key or "value": _cell(item)}


def _collect_columns(rows: Sequence[Mapping[str, Any]], max_cols: int = 12) -> Tuple[List[str], List[str]]:
    """The columns to show, in the author's order (first appearance across rows), and the ones dropped
    from the end past `max_cols` (fix-now F5: the caller names them in a footer, never a silent cut)."""
    seen: List[str] = []
    for row in rows:
        for k in row.keys():
            if k not in seen:
                seen.append(k)
    return seen[:max_cols], seen[max_cols:]


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
                rows.append({"value": _cell(item)})
        return rows
    if isinstance(data, Mapping):
        # If a single object contains a list-like 'elements' or similar, prefer that
        for key in ("elements", "items", "results"):
            if isinstance(data.get(key), list):
                return _ensure_rows(data[key])
        return [_flatten(data)]
    # Fallback: scalar
    return [{"value": data}]


def hidden_columns_footer(dropped: Sequence[str]) -> str:
    """The footer naming columns the table could not show (fix-now F5, the Portal #832 pattern)."""
    return f"+{len(dropped)} more column{'s' if len(dropped) != 1 else ''}: {', '.join(dropped)}" if dropped else ""


def _render_table(console: Console, title: str, caption: str, data: Any, use_pager: bool = True,
                  notes: Optional[Sequence[str]] = None, max_cols: int = 12) -> None:
    rows = _ensure_rows(data)
    if not rows:
        console.print("No results found.")
        return

    columns, dropped = _collect_columns(rows, max_cols=max_cols)

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

    footer = [hidden_columns_footer(dropped)] if dropped else []
    footer += list(notes or [])  # fix-now F8: e.g. "the first 100 ...; more may exist"

    def _print():
        console.print(table)
        for line in footer:
            console.print(line)

    # Page the table if it's large
    if use_pager:
        with console.pager():
            _print()
    else:
        _print()


# ── R3: the structured TABLE (kind "table") drawn natively with Rich ──

#: Narrowest a main-table column may get before columns are dropped from the end (author's order).
MIN_COLUMN_WIDTH = 14


def _row_name(row: Mapping[str, Any], columns: Sequence[Mapping[str, Any]]) -> str:
    for key in ("display_name", "displayName", "title", "qualified_name", "name"):
        if row.get(key):
            return str(row[key])
    first = next((row.get(c["key"]) for c in columns if isinstance(row.get(c["key"]), (str, int, float))), None)
    return str(first) if first not in (None, "") else "row"


def _names(value: Any, label: Optional[str]) -> List[str]:
    from pyegeria.view.output_formatter import _legacy_name
    items = value if isinstance(value, list) else [value]
    out = []
    for item in items:
        if isinstance(item, Mapping):
            out.append(_legacy_name(dict(item), label) or _object_name(item))
        elif item not in (None, ""):
            out.append(str(item))
    return out


def _clamp(text: str, max_lines: int, width: int) -> str:
    """Long text cut at max_lines lines of the column's width, with "…" (R3)."""
    lines: List[str] = []
    for para in str(text).splitlines() or [""]:
        while len(para) > width and len(lines) < max_lines:
            lines.append(para[:width])
            para = para[width:]
        if len(lines) >= max_lines:
            break
        lines.append(para)
    cut = "\n".join(lines[:max_lines])
    return cut + "…" if len(cut.replace("\n", "")) < len(str(text).replace("\n", "")) else cut


def _rich_cell(value: Any, column: Mapping[str, Any], width: int) -> Any:
    from rich.table import Table as _Table
    from pyegeria.view.structured_table import DEFAULT_MAX_ITEMS, DEFAULT_MAX_LINES
    if value in (None, "", [], {}):
        return ""
    render = column.get("render") or "text"
    limit = column.get("max_items") or DEFAULT_MAX_ITEMS
    if render == "subtable":
        n = len(value) if isinstance(value, list) else 1
        return f"{n} item{'s' if n != 1 else ''} · see below"
    if render == "count":
        return str(len(value)) if isinstance(value, (list, dict)) else str(value)
    if render == "kv" and isinstance(value, Mapping):
        grid = _Table.grid(padding=(0, 1))
        grid.add_column(style="bold")
        grid.add_column()
        for k, v in value.items():
            grid.add_row(str(k), _cell(v))
        return grid
    if isinstance(value, (list, Mapping)):
        names = _names(value, column.get("label"))
        shown, rest = names[:limit], len(names) - min(len(names), limit)
        if render == "bullets":
            return "\n".join(f"• {n}" for n in shown) + (f"\n+{rest} more" if rest else "")
        return ", ".join(shown) + (f" (+{rest} more)" if rest else "")
    if column.get("type") == "text":  # long text only: a short value is never cut
        return _clamp(str(value), column.get("max_lines") or DEFAULT_MAX_LINES, max(width, 8))
    return str(value)


def render_structured_table(console: Console, result: Mapping[str, Any], title: str, caption: str = "",
                            use_pager: bool = False) -> None:
    """Draw a structured TABLE (kind "table", R1) with Rich (R3): bullets one per line, kv as a nested
    table, long text cut at max_lines with "…", each subtable as a separate table after the main one
    titled "<row name> · <column>" (owner §7.3), and columns that do not fit the terminal dropped from
    the end of the author's order with a footer naming them. Notes (caps, reductions) follow."""
    columns = list(result.get("columns") or [])
    rows = list(result.get("rows") or [])
    if not rows:
        console.print("No results found.")
        for note in result.get("notes") or []:
            console.print(note)
        return
    fit = max(1, (console.width or 80) // MIN_COLUMN_WIDTH)
    shown_cols, dropped = columns[:fit], columns[fit:]
    width = max(MIN_COLUMN_WIDTH, (console.width or 80) // max(1, len(shown_cols)) - 3)

    table = Table(title=title, caption=caption or None, show_lines=True, box=box.ROUNDED, expand=True)
    for col in shown_cols:
        table.add_column(str(col.get("name") or col.get("key")), overflow="fold")
    subtables = []
    for row in rows:
        table.add_row(*[_rich_cell(row.get(c["key"]), c, width) for c in shown_cols])
        for c in shown_cols:
            if c.get("render") == "subtable" and isinstance(row.get(c["key"]), list) and row.get(c["key"]):
                subtables.append((f"{_row_name(row, columns)} · {c.get('name')}", row[c["key"]]))

    footer = []
    if dropped:
        footer.append(hidden_columns_footer([str(c.get("name") or c.get("key")) for c in dropped]))
    if result.get("total") is None and result.get("shown"):
        footer.append(f"{result['shown']} rows shown; the total was not counted.")
    footer += list(result.get("notes") or [])

    def _print():
        console.print(table)
        for sub_title, sub_rows in subtables:
            sub = Table(title=sub_title, show_lines=True, box=box.SIMPLE_HEAD, expand=True)
            keys: List[str] = []
            for r in sub_rows:
                for k in (r.keys() if isinstance(r, Mapping) else ["value"]):
                    if k not in keys:
                        keys.append(k)
            for k in keys:
                sub.add_column(str(k), overflow="fold")
            for r in sub_rows:
                r = r if isinstance(r, Mapping) else {"value": r}
                sub.add_row(*[_sub_cell(r.get(k)) for k in keys])
            console.print(sub)
        for line in footer:
            console.print(line)

    if use_pager:
        with console.pager():
            _print()
    else:
        _print()


def _sub_cell(value: Any) -> str:
    """A subtable cell: two levels only, so a reduced third level shows as "N: names"."""
    if isinstance(value, Mapping) and "count" in value and "names" in value:
        return f"{value['count']}: {', '.join(value['names'])}"
    return _cell(value)


def write_output_file(content: str, report_spec: str, suffix: str) -> str:
    # Base directory is outbox/report_spec specific folder
    file_path = os.path.join(app_config.pyegeria_root, app_config.dr_egeria_outbox, f"{report_spec}")
    ts = time.strftime("%Y-%m-%d-%H-%M-%S")
    safe_spec = "".join(c for c in report_spec if c.isalnum() or c in ("-", "_", "+", ".", " ")).strip().replace(" ", "_")
    # Determine extension by content type rules
    if suffix in {"MD", "REPORT", "REPORT-GRAPH", "FORM", "MERMAID", "LIST"}:
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


def validation_line(result: Mapping[str, Any]) -> str:
    """One line saying whether a DOCUMENT result was validated, by what, and what was found."""
    v = result.get("validation") or {}
    state = v.get("state", "not_validated")
    if state == "not_validated":
        return f"Validation: not validated ({v.get('reason') or 'no reason given'})"
    findings = v.get("findings") or []
    tail = f", {len(findings)} finding{'s' if len(findings) != 1 else ''}" if findings else ""
    return f"Validation: {state} ({v.get('validator')}{tail})"


def write_document(result: Mapping[str, Any], output_dir: str, *, force: bool = False) -> str:
    """Write a DOCUMENT result's text to `output_dir/<file_name>` and return the path.

    The file name is the result's own (already checked by the executor) and is checked again
    here: it must name a file directly inside `output_dir`. An existing file is not overwritten
    unless `force` is set (FileExistsError, with the path)."""
    from pyegeria.view._output_format_models import check_document_file_name

    if result.get("kind") != "document":
        raise ValueError(f"not a DOCUMENT result (kind {result.get('kind')!r})")
    file_name = str(result.get("file_name") or "")
    reason = check_document_file_name(file_name)
    if reason:
        raise ValueError(f"DOCUMENT file_name refused: {reason}")
    out_dir = os.path.abspath(os.path.expanduser(output_dir))
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, file_name)
    if os.path.dirname(os.path.abspath(path)) != out_dir:
        raise ValueError(f"DOCUMENT file_name refused: '{file_name}' does not name a file in {out_dir}")
    if os.path.exists(path) and not force:
        raise FileExistsError(f"{path} already exists; pass --force to overwrite it")
    with open(path, "w", encoding="utf-8") as f:
        f.write(str(result.get("text", "")))
    return path


def main(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser(description="Generic list command using exec_report_spec")
    parser.add_argument("--report", dest="report_spec", help="Report spec name to execute (see report specs)")
    parser.add_argument("--output-format", dest="output_format", default="TABLE",
                        choices=["TABLE", "MD", "REPORT", "REPORT-GRAPH", "FORM", "HTML", "MERMAID", "LIST", "JSON", "DICT",
                                 "DOCUMENT"],
                        help="Output rendering format (DOCUMENT: a standard document from a document spec)")
    parser.add_argument("--output", dest="output_dir",
                        help="DOCUMENT only: directory to write the document to, as its file name")
    parser.add_argument("--force", action="store_true",
                        help="DOCUMENT only: overwrite the file if it already exists")
    parser.add_argument("--server", dest="server", help="Egeria view server name", default=app_config.egeria_view_server)
    parser.add_argument("--url", dest="url", help="Egeria platform URL", default=app_config.egeria_view_server_url)
    parser.add_argument("--userid", dest="user", help="User Id", default=EGERIA_USER)
    parser.add_argument("--password", dest="password", help="User Password", default=EGERIA_USER_PASSWORD)
    # Allow arbitrary parameters as JSON or repeated key=value
    parser.add_argument("--params-json", dest="params_json", help="JSON string of parameters for the report spec")
    parser.add_argument("--param", dest="params_kv", action="append", default=[], help="Repeated key=value parameters")

    args = parser.parse_args(argv)

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
        width=settings.Environment.egeria_width,
        force_terminal=not app_config.egeria_jupyter,
    )

    if output_format == "DOCUMENT":
        if not args.output_dir:
            console.print("[bold red]DOCUMENT output needs --output <dir> to write the document to[/]")
            return 2
        try:
            result = list_generic(report_spec, output_format="DOCUMENT", params=params, view_server=args.server,
                                  view_url=args.url, user=args.user, user_pass=args.password)
            path = write_document(result, args.output_dir, force=args.force)
        except FileExistsError as e:
            console.print(f"[bold red]{e}[/]")
            return 1
        except ValueError as e:
            console.print(f"[bold red]{e}[/]")
            return 1
        except PyegeriaException as e:
            print_exception_response(e)
            return 1
        print(f"==> {result.get('standard')} document written to {path}")
        print(validation_line(result))
        for note in result.get("notes") or []:
            print(f"  note: {note}")
        return 0

    try:
        # Use shared function with prompting enabled for missing required params
        write_file = output_format in TEXT_FILE_FORMATS
        result = list_generic(report_spec, output_format=output_format, params=params, view_server=args.server,
                              view_url=args.url, user=args.user, user_pass=args.password, jupyter=app_config.egeria_jupyter,
                              width=settings.Environment.egeria_width, prompt_missing=True, write_file=write_file,
                              table_shape="structured" if output_format == "TABLE" else "rows")  # R3

        if result.get("kind") == "empty":
            console.print("No results found.")
            return

        if output_format in {"TABLE", "DICT"}:
            heading = result.get("heading") or (get_report_spec_heading(report_spec) or f"Report: {report_spec}")
            caption = f"View Server '{args.server}' @ Platform - {args.url}"
            if result.get("structured") is not None:
                render_structured_table(console, result["structured"], heading, caption)
            else:
                _render_table(console, heading, caption, result.get("data"), notes=result.get("notes"))
            return

        # For narrative formats, either a file was written or content is returned
        fpath = result.get("file_path")
        if fpath:
            print(f"\n==> Output written to {fpath}")
        else:
            print(result.get("content", ""))

    except ValueError as e:
        console.print(f"[bold red]{e}[/]")
        console.print("Tip: Run 'list_reports' to see available reports.")
    except PyegeriaException as e:
        print_exception_response(e)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
