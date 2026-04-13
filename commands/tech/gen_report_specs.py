"""
Generate report FormatSet specifications for pyegeria from command specifications (compact commands).

Overview
- This utility reads Dr. Egeria style command specifications (JSON files)
  and converts relevant entries (by default, only those with a display name
  beginning with "Create") into pyegeria FormatSet definitions. These can be:
  - returned in-memory as a FormatSetDict
  - saved to a JSON file that can be loaded by pyegeria.view.base_report_formats.load_report_specs
  - saved as a Python module that defines a dictionary of FormatSet objects
  - merged directly into the built-in report_specs registry at runtime
  - persisted into the base_report_formats.py source file (using --merge)

Typical uses
- Quickly scaffold report formats for new content types defined in your command
  specifications, without hand-writing every Column/Format block.
- Keep generated formats in sync with your Dr. Egeria command definitions.

What this tool extracts
- Target type: from each command's display_name (e.g., "Create Asset" -> "Asset")
- Columns: attributes are resolved from inherited bundles and attribute_definitions.
- Action parameter: if a find_method is present on the command, an ActionParameter
  is created to allow running reports directly from the spec.

CLI usage examples
- Run as part of the main CLI:
    hey_egeria tech gen-report-specs md_processing/data/compact_commands --emit dict --list

- Persistently update base_report_formats.py with generated specs:
    hey_egeria tech gen-report-specs md_processing/data/compact_commands --merge

- Save to JSON:
    hey_egeria tech gen-report-specs md_processing/data/compact_commands --emit json --output-file my_specs.json

- Emit Python code:
    hey_egeria tech gen-report-specs md_processing/data/compact_commands --emit code --output-file my_specs.py

Notes
- Only commands whose key or display_name begins with "Create" are included by
  default.
- When pointing to a directory, all JSON files are merged to resolve bundles and
  attribute definitions before generating specs.
"""
import json
import re
import argparse
import os
import click
from pathlib import Path
from typing import Iterable, List, Optional

from loguru import logger
from rich.prompt import Prompt

from pyegeria.core.config import get_app_config
from pyegeria.view._output_format_models import Column, Format, ActionParameter, FormatSet, FormatSetDict
from pyegeria.view.base_report_formats import OPTIONAL_SEARCH_PARAMS  # ["page_size","start_from","starts_with","ends_with","ignore_case"]


GENERATED_REPORT_EXCLUDED_KEYS = {
    "anchor_id",
    "anchor_scope_id",
    "anchor_scope_ids",
    "external_source_guid",
    "external_source_name",
    "for_duplicate_processing",
    "for_lineage",
    "journal_entry",
    "merge_update",
    "parent_at_end1",
    "parent_id",
    "parent_relationship_attributes",
    "parent_relationship_type_name",
    "request_id",
    "search_keywords",
}

LIST_PRIORITY_KEYS = ["display_name", "qualified_name", "guid"]
LIST_DEMOTED_KEYS = {"version_identifier"}
LIST_LAST_KEY = "category"

# Keys excluded from LIST output only (still present in ALL/FORM/REPORT).
LIST_EXCLUDED_KEYS = {
    "url",
}


def _clone_column(col: Column) -> Column:
    if hasattr(col, "model_dump"):
        return Column(**col.model_dump())
    return Column(**col.dict())


def _filter_generated_columns(columns: List[Column]) -> List[Column]:
    """Remove keys excluded from ALL generated formats (LIST and ALL)."""
    return [
        _clone_column(col)
        for col in columns
        if getattr(col, "key", None) not in GENERATED_REPORT_EXCLUDED_KEYS
    ]


def _filter_list_columns(columns: List[Column]) -> List[Column]:
    """Remove keys excluded specifically from LIST output (superset of _filter_generated_columns)."""
    return [
        col
        for col in columns
        if getattr(col, "key", None) not in LIST_EXCLUDED_KEYS
    ]


def _is_status_like_key(key: str) -> bool:
    if not isinstance(key, str):
        return False
    return key == "status" or key.endswith("_status") or key == "status_identifier"


def _order_list_columns(columns: List[Column]) -> List[Column]:
    keyed_columns = [col for col in columns if getattr(col, "key", None)]
    original_positions = {col.key: idx for idx, col in enumerate(keyed_columns)}
    priority_rank = {key: idx for idx, key in enumerate(LIST_PRIORITY_KEYS)}

    def sort_key(col: Column):
        key = col.key
        if key in priority_rank:
            return (0, priority_rank[key], original_positions.get(key, 10_000))
        if key == LIST_LAST_KEY:
            return (4, 0, original_positions.get(key, 10_000))
        if key in LIST_DEMOTED_KEYS:
            return (2, 0, original_positions.get(key, 10_000))
        if _is_status_like_key(key):
            return (3, 0, original_positions.get(key, 10_000))
        return (1, 0, original_positions.get(key, 10_000))

    return [_clone_column(col) for col in sorted(keyed_columns, key=sort_key)]

def _is_create_command(cmd_key: str, cmd_obj: dict) -> bool:
    """Return True if a command should be treated as a "Create" command.

    A command qualifies if either its dictionary key or its "display_name"
    begins with the word "Create" (case-insensitive). This mirrors how the
    CLI specs tend to name creation operations and is used to filter which
    commands are transformed into report FormatSets by default.
    """
    name = str(cmd_obj.get("display_name", "")).strip()
    return (isinstance(cmd_key, str) and cmd_key.strip().lower().startswith("create")) or \
           (name.lower().startswith("create"))

def _derive_set_name_from_display_name(display_name: str) -> str:
    """Derive a compact set name from a command display name.

    Example: 'Create Governance Strategy Definition' -> 'GovernanceStrategyDefinition-DrE'
    Currently not used in favor of a dash-separated variant, but kept for
    reference and potential future toggles.
    """
    if not display_name:
        return ""
    parts = display_name.strip().split()
    if len(parts) <= 1:
        return re.sub(r"\s+", "", display_name.strip())+"-DrE"
    rest = " ".join(parts[1:]).strip()
    rest = rest+"-DrE"
    return re.sub(r"\s+", "", rest)

def _safe_parse_constraints(s) -> dict:
    """Parse a command's `find_constraints` field into a Python dict.

    Accepts:
    - A dict (returned as-is)
    - A JSON string (possibly surrounded by quotes or single-quoted)
    - A loosely dict-like string using single quotes

    Returns an empty dict on failure and logs at debug level.
    """
    if not s:
        return {}
    if isinstance(s, dict):
        return s
    txt = str(s).strip()
    # Attempt 1: direct JSON
    try:
        return json.loads(txt)
    except Exception:
        logger.error(f"Error parsing constraints: {s!r}")
        pass
    # Attempt 2: unwrap quotes
    try:
        txt2 = txt.strip('"').strip("'")
        return json.loads(txt2)
    except Exception:
        pass
    # Attempt 3: heuristic single->double quotes for dict-like strings
    if ("{" in txt and "}" in txt) and ("'" in txt and '"' not in txt):
        try:
            return json.loads(txt.replace("'", '"'))
        except Exception:
            pass
    logger.debug(f"Could not parse find_constraints: {s!r} -> {{}}")
    return {}

def _extract_columns_from_attributes(attributes: Iterable[dict], usage_level: str = None) -> List[Column]:
    """Extract Columns from a command's Attributes list.

    Parameters
    - attributes: iterable of dict entries. Support both old single-key
      mapping (Label -> metadata) and new flat mapping (name, variable_name, level, etc.).
    - usage_level: Egeria usage level (Basic or Advanced). If None, uses EGERIA_USAGE_LEVEL.

    Behavior
    - Visibility is determined by common_md_proc_utils._level_visible
    - Duplicate variable_name values are de-duplicated
    - Column.name is the label; Column.key is the variable_name

    Returns
    - List[Column]
    """
    from md_processing.md_processing_utils.common_md_proc_utils import _level_visible, EGERIA_USAGE_LEVEL
    target_usage = usage_level or EGERIA_USAGE_LEVEL

    cols: List[Column] = []
    seen: set[str] = set()

    def process_attr(label, details):
        if not isinstance(details, dict):
            return
        if not _level_visible(details.get("level"), target_usage):
            return
        key = details.get("variable_name")
        if not key or key in seen:
            return
        seen.add(key)
        cols.append(Column(name=str(label), key=str(key)))

    for entry in attributes or []:
        if not isinstance(entry, dict) or not entry:
            continue
        
        if "name" in entry and "variable_name" in entry:
            # New flat structure
            process_attr(entry["name"], entry)
        else:
            # Old nested structure
            for label, details in entry.items():
                process_attr(label, details)

    return cols


def _build_generated_formats(columns: List[Column], default_types: Optional[List[str]] = None) -> List[Format]:
    filtered_columns = _filter_generated_columns(columns)
    if not filtered_columns:
        return []

    if default_types is not None:
        return [Format(types=default_types, attributes=filtered_columns)]

    list_columns = _order_list_columns(_filter_list_columns(filtered_columns))
    return [
        Format(types=["LIST"], attributes=list_columns),
        Format(types=["ALL"], attributes=filtered_columns),
    ]


def _derive_target_type(cmd_key: str, cmd_obj: dict) -> str:
    display_name = str(cmd_obj.get("display_name", "")).strip()
    if isinstance(cmd_key, str):
        key_parts = cmd_key.strip().split(maxsplit=1)
        if len(key_parts) == 2:
            return key_parts[1]
    return display_name


def _load_command_specs(path: Path | str) -> dict:
    """Load compact command specifications from a directory using the internal compact loader."""
    path_str = str(path)
    try:
        from md_processing.md_processing_utils.compact_loader import load_compact_specs_from_dir
        specs = load_compact_specs_from_dir(path_str)
        if specs:
            logger.info(f"Loaded compact specs from {path_str} with {len(specs)} commands")
            return specs
    except Exception as e:
        logger.error(f"Failed to use compact_loader on dir {path_str}: {e}")
    return {}

def build_format_sets_from_commands(
    commands_json_path: str | Path,
    *,
    include_only_create: bool = True,
    default_types: Optional[List[str]] = None,
    usage_level: str = None
) -> FormatSetDict:
    """Build a FormatSetDict from a commands.json file.

    Parameters
    - commands_json_path: path to the Dr Egeria style commands.json file. The
      file may be an object with a "Command Specifications" map, or a list of
      command objects.
    - include_only_create: when True (default), include only commands whose key
      or display_name starts with "Create".
    - default_types: the list used for Format.types for each produced Format
      (defaults to ["ALL"]).
    - usage_level: Egeria usage level override (Basic or Advanced).

    Returns
    - FormatSetDict keyed by set names derived from display_name + "-DrE".

    Notes
    - Columns are derived from Attributes entries based on usage_level.
    - If find_method is present, an ActionParameter is created.
    """
    path = Path(commands_json_path)
    data = _load_command_specs(path)


    results = FormatSetDict()
    types = default_types or ["ALL"]

    for cmd_key, cmd_obj in data.items():
        if not isinstance(cmd_obj, dict):
            continue
        if include_only_create and not _is_create_command(cmd_key, cmd_obj):
            continue

        target_type = _derive_target_type(cmd_key, cmd_obj)
        display_name = target_type.strip()
        if not display_name:
            logger.debug(f"Skip {cmd_key!r}: missing display_name")
            continue
        set_name = re.sub(r"\s+", "-", display_name)
        set_name = set_name.strip() + "-DrE"
        # set_name = _derive_set_name_from_display_name(display_name)
        if not set_name:
            logger.debug(f"Skip {cmd_key!r}: could not derive set name from display_name={display_name!r}")
            continue

        levels_to_generate = [usage_level.capitalize()] if usage_level else ["Basic", "Advanced"]
        
        for lvl in levels_to_generate:
            columns = _extract_columns_from_attributes(cmd_obj.get("Attributes", []), usage_level=lvl)
            if not columns:
                if lvl == "Basic":
                    columns = _extract_columns_from_attributes(cmd_obj.get("Attributes", []), usage_level="Advanced")
                if not columns:
                    logger.debug(f"Skip {set_name}-{lvl}: no attributes")
                    continue

            find_method = cmd_obj.get("find_method") or ""
            constraints = _safe_parse_constraints(cmd_obj.get("find_constraints"))
            action = None
            if find_method:
                action = ActionParameter(
                    function=find_method,
                    required_params=["search_string"],
                    optional_params=OPTIONAL_SEARCH_PARAMS,
                    spec_params=constraints or {},
                )

            formats = _build_generated_formats(columns, default_types=default_types)
            if not formats:
                logger.debug(f"Skip {set_name}-{lvl}: no remaining attributes after generated filtering")
                continue

            fs = FormatSet(
                target_type=display_name,
                heading=f"{set_name}-{lvl} Attributes",
                description=f"Auto-generated format for {display_name} (Create, {lvl}).",
                family=cmd_obj.get("family"),
                formats=formats,
                action=action
            )
            results[f"{set_name}-{lvl}"] = fs

    return results

def save_generated_format_sets(
    commands_json_path: str | Path,
    out_file: str | Path,
    *,
    include_only_create: bool = True,
    default_types: Optional[List[str]] = None
) -> Path:
    """Build FormatSets from commands.json and save them as JSON.

    The resulting JSON can be loaded via `pyegeria.base_report_formats.load_report_specs`.

    Parameters
    - commands_json_path: input commands.json path
    - out_file: where to write the generated JSON
    - include_only_create: filter to only "Create" commands (default True)
    - default_types: list for Format.types (default ["ALL"]).

    Returns
    - Path to the written JSON file
    """
    sets = build_format_sets_from_commands(
        commands_json_path,
        include_only_create=include_only_create,
        default_types=default_types,
    )
    out = Path(out_file)
    out.parent.mkdir(parents=True, exist_ok=True)
    sets.save_to_json(str(out))
    logger.info(f"Saved {len(sets)} generated format sets to {out}")
    return out

# New: expose a simple alias that returns a FormatSetDict directly
# for callers that want the in-memory object rather than JSON.
def generate_format_sets(
    commands_json_path: str | Path,
    *,
    include_only_create: bool = True,
    default_types: Optional[List[str]] = None,
):
    """Return a FormatSetDict built from commands.json (no file I/O).

    This is a convenience wrapper around `build_format_sets_from_commands` for
    programmatic use when you don't want to touch the filesystem.
    """
    return build_format_sets_from_commands(
        commands_json_path,
        include_only_create=include_only_create,
        default_types=default_types,
    )

# New: merge generated sets into the builtin registry

def merge_generated_format_sets(
    commands_json_path: str | Path,
    *,
    include_only_create: bool = True,
    default_types: Optional[List[str]] = None,
) -> int:
    """Build and merge generated FormatSets into the built-in registry.

    Parameters
    - commands_json_path: input commands.json path
    - include_only_create: filter to only "Create" commands (default True)
    - default_types: list for Format.types (default ["ALL"]).

    Returns
    - int: number of sets merged/added into `pyegeria.base_report_formats.report_specs`.
    """
    from pyegeria.view.base_report_formats import report_specs  # local import to avoid cycles on tooling

    gen = build_format_sets_from_commands(
        commands_json_path,
        include_only_create=include_only_create,
        default_types=default_types,
    )
    count = 0
    for name, fs in gen.items():
        report_specs.upsert(name, fs)
        count += 1
    logger.info(f"Merged {count} generated format sets into built-ins (upsert)")
    return count


def _py_literal(value):
    """Render a value as a valid Python literal string.

    Supports strings, numbers, bools, None, lists, tuples, dicts. Used when
    emitting Python code for generated FormatSets.
    """
    if isinstance(value, str):
        return repr(value)
    if isinstance(value, (int, float)):
        return str(value)
    if value is True:
        return "True"
    if value is False:
        return "False"
    if value is None:
        return "None"
    if isinstance(value, list):
        return "[" + ", ".join(_py_literal(v) for v in value) + "]"
    if isinstance(value, dict):
        # Render dict with stable key ordering
        items = ", ".join(f"{_py_literal(k)}: {_py_literal(v)}" for k, v in sorted(value.items(), key=lambda kv: str(kv[0]).lower()))
        return "{" + items + "}"
    # Fallback
    return repr(value)


def _format_column(col: Column) -> str:
    """Render a Column instance as Python code.

    Returns a string like: Column(name='Display Name', key='display_name', ...)
    Only includes optional attributes when present.
    """
    parts = [f"name={_py_literal(getattr(col, 'name', ''))}", f"key={_py_literal(getattr(col, 'key', ''))}"]
    fmt = getattr(col, 'format', None)
    if fmt not in (None, False):
        parts.append(f"format={_py_literal(bool(fmt))}")
    return "Column(" + ", ".join(parts) + ")"


def _format_action(ap: ActionParameter | None) -> str:
    """Render an ActionParameter as Python code for emission.

    Includes function, required_params, optional_params, and spec_params when present.
    """
    if not ap:
        return "None"
    parts = [
        f"function={_py_literal(getattr(ap, 'function', ''))}",
    ]
    req = getattr(ap, 'required_params', None)
    if req:
        parts.append(f"required_params={_py_literal(list(req))}")
    opt = getattr(ap, 'optional_params', None)
    if opt:
        parts.append(f"optional_params={_py_literal(list(opt))}")
    spec = getattr(ap, 'spec_params', None)
    if spec:
        parts.append(f"spec_params={_py_literal(dict(spec))}")
    return "ActionParameter(" + ", ".join(parts) + ")"


def _format_format(fmt: Format) -> str:
    """Render a Format instance as Python code, including types and attributes."""
    cols = getattr(fmt, 'attributes', []) or []
    types = getattr(fmt, 'types', []) or []
    col_code = ", ".join(_format_column(c) for c in cols)
    parts = [f"types={_py_literal(list(types))}", f"attributes=[{col_code}]"]
    return "Format(" + ", ".join(parts) + ")"


def _format_formatset(fs: FormatSet) -> str:
    """Render a FormatSet as Python code including nested formats and actions."""
    parts = []
    if getattr(fs, 'target_type', None):
        parts.append(f"target_type={_py_literal(fs.target_type)}")
    if getattr(fs, 'heading', None):
        parts.append(f"heading={_py_literal(fs.heading)}")
    if getattr(fs, 'description', None):
        parts.append(f"description={_py_literal(fs.description)}")
    if getattr(fs, 'family', None):
        parts.append(f"family={_py_literal(fs.family)}")
    aliases = getattr(fs, 'aliases', None)
    if aliases:
        parts.append(f"aliases={_py_literal(list(aliases))}")
    ann = getattr(fs, 'annotations', None)
    if ann:
        parts.append(f"annotations={_py_literal(dict(ann))}")
    # formats
    fmts = getattr(fs, 'formats', []) or []
    fmt_code = ", ".join(_format_format(f) for f in fmts)
    parts.append(f"formats=[{fmt_code}]")
    # actions
    action = getattr(fs, 'action', None)
    if action:
        parts.append(f"action={_format_action(action)}")
    get_add = getattr(fs, 'get_additional_props', None)
    if get_add:
        parts.append(f"get_additional_props={_format_action(get_add)}")
    return "FormatSet(" + ", ".join(parts) + ")"


def format_sets_to_python_code(sets: FormatSetDict, var_name: str = "generated_format_sets") -> str:
    """Render a FormatSetDict into the text of a small Python module.

    Parameters
    - sets: the FormatSetDict to render
    - var_name: the variable name to assign the dict to (default 'generated_format_sets')

    Returns
    - str: Python source code that, when imported, defines `var_name` as a FormatSetDict
    """
    header = (
        "# Auto-generated by gen_report_specs.py\n"
        "from pyegeria.view._output_format_models import Column, Format, ActionParameter, FormatSet, FormatSetDict\n\n"
    )
    # Stable ordering by key
    entries = []
    for name in sorted(sets.keys(), key=lambda s: s.lower()):
        fs = sets[name]
        entries.append(f"    {_py_literal(name)}: {_format_formatset(fs)}")
    body = f"{var_name} = FormatSetDict({{\n" + ",\n".join(entries) + "\n})\n"
    return header + body


def save_generated_format_sets_code(
    commands_json_path: str | Path,
    out_file: str | Path,
    *,
    include_only_create: bool = True,
    default_types: Optional[List[str]] = None,
    var_name: str = "generated_format_sets",
) -> Path:
    """Build FormatSets and save them as an importable Python module.

    Parameters
    - commands_json_path: input commands.json path
    - out_file: path to write the .py file (module will define `var_name`)
    - include_only_create: filter to only "Create" commands (default True)
    - default_types: list for Format.types (default ["ALL"]).
    - var_name: variable name to bind the resulting FormatSetDict to

    Returns
    - Path to the written Python file

    Notes
    - You can import the resulting file dynamically and access the variable
      to merge into `pyegeria.base_report_formats.report_specs`.
    """
    sets = build_format_sets_from_commands(
        commands_json_path,
        include_only_create=include_only_create,
        default_types=default_types,
    )
    code = format_sets_to_python_code(sets, var_name=var_name)
    out = Path(out_file)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(code, encoding="utf-8")
    logger.info(f"Saved Python code for {len(sets)} generated format sets to {out}")
    return out


def _update_base_report_formats_file(sets: FormatSetDict):
    try:
        import pyegeria.view.base_report_formats as brf
        target_path = Path(brf.__file__)
    except ImportError:
        target_path = Path("pyegeria/view/base_report_formats.py")

    if not target_path.exists():
        return "file_missing", target_path

    content = target_path.read_text(encoding="utf-8")
    start_marker = "# --- GENERATED FORMAT SETS ---"
    end_marker = "# --- END GENERATED FORMAT SETS ---"

    if start_marker not in content or end_marker not in content:
        return "markers_missing", target_path

    entries = []
    for name in sorted(sets.keys(), key=lambda s: s.lower()):
        fs = sets[name]
        entries.append(f"    {_py_literal(name)}: {_format_formatset(fs)}")

    new_section = (
        f"{start_marker}\n"
        f"# This section is updated by gen-report-specs.\n"
        f"generated_format_sets = FormatSetDict({{\n"
        + ",\n".join(entries) +
        "\n})\n"
        f"{end_marker}"
    )

    import re
    pattern = re.escape(start_marker) + r".*?" + re.escape(end_marker)
    new_content = re.sub(pattern, new_section, content, flags=re.DOTALL)

    if new_content != content:
        target_path.write_text(new_content, encoding="utf-8")
        return "updated", target_path
    else:
        return "no_change", target_path


def _merge_generated_sets_and_report_status(sets: FormatSetDict) -> None:
    from pyegeria.view.base_report_formats import report_specs

    merged_count = 0
    for name, fs in sets.items():
        report_specs.upsert(name, fs)
        merged_count += 1

    file_status, target_path = _update_base_report_formats_file(sets)
    base_msg = f"Merged {merged_count} generated format sets into runtime registry."
    target_msg = f"Generated section target: {target_path}"

    if file_status == "updated":
        status_msg = f"{base_msg} Updated generated section in {target_path}."
        logger.info(status_msg)
        click.echo(status_msg)
    elif file_status == "no_change":
        status_msg = f"{base_msg} Generated section in {target_path} already up to date."
        logger.info(status_msg)
        click.echo(status_msg)
    elif file_status == "markers_missing":
        status_msg = f"{base_msg} WARNING: generated-section markers not found in {target_path}; skipped file update."
        logger.warning(status_msg)
        click.secho(status_msg, fg="yellow")
    elif file_status == "file_missing":
        status_msg = f"{base_msg} WARNING: target file {target_path} was not found; skipped file update."
        logger.warning(status_msg)
        click.secho(status_msg, fg="yellow")
    else:
        status_msg = f"{base_msg} WARNING: merge status unknown for {target_path}; skipped file update."
        logger.warning(status_msg)
        click.secho(status_msg, fg="yellow")

    logger.info(target_msg)
    click.echo(target_msg)


@click.command(name="gen-report-specs")
@click.argument("commands_json", required=False)
@click.argument("output_path", required=False)
@click.option(
    "--emit",
    type=click.Choice(["json", "dict", "code"]),
    default="json",
    help="Output mode",
)
@click.option(
    "--merge",
    is_flag=True,
    help="Merge into runtime report registry and sync generated section in pyegeria/view/base_report_formats.py.",
)
@click.option("--list", "list_names", is_flag=True, help="List set names")
@click.option("--usage-level", default=None, help="Egeria usage level (Basic or Advanced)",
              type=click.Choice(["Basic", "Advanced"], case_sensitive=False))
def main(commands_json, output_path, emit, merge, list_names, usage_level):
    """CLI entry point for generating report FormatSets from commands.json.

    Notes
    - If a command object includes a string field `family`, it will be propagated into the generated
      `FormatSet.family`. This applies to both JSON emission and generated Python code.

    Synopsis
    - Default (emit JSON):
        python -m md_processing.md_processing_utils.gen_report_specs \
            md_processing/data/commands.json md_processing/data/generated_format_sets.json --emit json
    - Emit Python code:
        python -m md_processing.md_processing_utils.gen_report_specs \
            md_processing/data/commands.json md_processing/data/generated_format_sets.py --emit code
    - In-memory only and list:
        python -m md_processing.md_processing_utils.gen_report_specs \
            md_processing/data/commands.json --emit dict --list

    Flags
    - --emit json|dict|code: controls output mode (default json)
    - --merge: also merge generated sets into built-in report_specs at runtime
    - --list: when emitting dict (or after merge), list set names to stdout
    """
    config = get_app_config()
    env = config.Environment

    try:
        input_file = commands_json or Prompt.ask(
            "Enter commands.json or directory:",
            default=os.path.join(env.pyegeria_root, "md_processing/data/compact_commands"),
        )

        sets = build_format_sets_from_commands(input_file, usage_level=usage_level)

        if emit == "json":
            output_file = output_path or Prompt.ask(
                "Output File:", default="md_processing/data/generated_format_sets.json"
            )
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            sets.save_to_json(output_file)
            logger.info(f"Saved JSON for {len(sets)} generated format sets to {output_file}")
            if merge:
                _merge_generated_sets_and_report_status(sets)
        elif emit == "code":
            output_file = output_path or Prompt.ask(
                "Output Python File:", default="pyegeria/dr_egeria_reports.py"
            )
            code = format_sets_to_python_code(sets)
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            Path(output_file).write_text(code, encoding="utf-8")
            logger.info(f"Saved Python code for {len(sets)} generated format sets to {output_file}")
            if merge:
                _merge_generated_sets_and_report_status(sets)
        else:
            # emit == "dict"
            logger.info(f"Generated {len(sets)} format sets (in-memory FormatSetDict)")
            if merge:
                _merge_generated_sets_and_report_status(sets)

        if list_names and sets is not None:
            names = sorted(list(sets.keys()))
            print(f"Generated set names ({len(names)}):")
            for n in names:
                print(f"- {n}")
    except (KeyboardInterrupt, EOFError):
        # Graceful exit when user cancels or stdin is not interactive
        pass

if __name__ == "__main__":
    main()
