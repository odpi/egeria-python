"""
Generate report FormatSet specifications for pyegeria from a commands.json file.

Overview
- This utility reads a Dr Egeria style commands.json (aka Command Specifications)
  and converts relevant entries (by default, only those with a display name
  beginning with "Create") into pyegeria FormatSet definitions. These can be:
  - returned in-memory as a FormatSetDict
  - saved to a JSON file that can be loaded by pyegeria.base_report_formats.load_report_specs
  - saved as a Python module that defines a dictionary of FormatSet objects
  - merged directly into the built-in report_specs registry at runtime

Typical uses
- Quickly scaffold report formats for new content types defined in your command
  specifications, without hand-writing every Column/Format block.
- Keep generated formats alongside your hand-curated ones and iterate as the
  command specifications evolve.

What this script extracts
- Target type: from each command's display_name
- Columns: only attributes marked with level == "Basic" are included. The
  column name comes from the attribute label; the column key from the
  attribute's variable_name.
- Action parameter: if a find_method is present on the command, an ActionParameter
  is created with:
  - function = find_method
  - required_params = ["search_string"]
  - optional_params = pyegeria.base_report_formats.OPTIONAL_PARAMS
  - spec_params = parsed find_constraints (see parsing notes below)

Constraints parsing
- find_constraints may be a dict or a JSON string (sometimes double-escaped).
  We try, in order: direct JSON, unquoted JSON, and a simple single-to-double
  quote substitution for dict-like strings. Failures yield an empty dict, and
  a debug message is logged.

Naming
- Each FormatSet key and heading are derived from the command's display_name.
  The key is display_name with spaces replaced by '-' and suffixed with '-DrE'.
  Example: "Create Governance Strategy Definition" -> "Create-Governance-Strategy-Definition-DrE".

CLI usage examples
- Save to JSON (default mode):
    poetry run python -m md_processing.md_processing_utils.gen_report_specs \
        md_processing/data/commands.json md_processing/data/generated_format_sets.json --emit json

- Emit Python code to a .py file:
    poetry run python -m md_processing.md_processing_utils.gen_report_specs \
        md_processing/data/commands.json md_processing/data/generated_report_specs.py --emit code

- Build in-memory only and list set names:
    poetry run python -m md_processing.md_processing_utils.gen_report_specs \
        md_processing/data/commands.json --emit dict --list

- Merge generated sets into the built-in registry (report_specs):
    poetry run python -m md_processing.md_processing_utils.gen_report_specs \
        md_processing/data/commands.json --emit dict --merge --list

Programmatic usage
- Build in memory:
    from md_processing.md_processing_utils.gen_report_specs import generate_format_sets
    sets = generate_format_sets("md_processing/data/commands.json")

- Save JSON that can be loaded by pyegeria:
    from md_processing.md_processing_utils.gen_report_specs import save_generated_format_sets
    save_generated_format_sets("md_processing/data/commands.json", "md_processing/data/generated_format_sets.json")

- Save as importable Python module:
    from md_processing.md_processing_utils.gen_report_specs import save_generated_format_sets_code
    save_generated_format_sets_code("md_processing/data/commands.json", "md_processing/data/generated_report_specs.py")

- Merge directly into built-ins at runtime:
    from md_processing.md_processing_utils.gen_report_specs import merge_generated_report_specs
    merge_generated_format_sets("md_processing/data/commands.json")

Notes
- Only commands whose key or display_name begins with "Create" are included by
  default. Pass include_only_create=False to include all commands.
- default_types controls the Format.types field, and defaults to ["ALL"].
- This script logs progress with loguru.
"""
import argparse
import json
import re
import argparse
from pathlib import Path
from typing import Iterable, List, Optional

from loguru import logger
from rich.prompt import Prompt

from pyegeria._output_format_models import Column, Format, ActionParameter, FormatSet, FormatSetDict
from pyegeria.base_report_formats import OPTIONAL_PARAMS  # ["page_size","start_from","starts_with","ends_with","ignore_case"]

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

def _extract_basic_columns_from_attributes(attributes: Iterable[dict]) -> List[Column]:
    """Extract Basic-level Columns from a command's Attributes list.

    Parameters
    - attributes: iterable of dict entries. Each entry is typically a single-key
      mapping of attribute label -> metadata dict with fields like
      {"variable_name": ..., "level": "Basic"|"Advanced"|...}.

    Behavior
    - Only items with level == "Basic" are included
    - Duplicate variable_name values are de-duplicated
    - Column.name is the label; Column.key is the variable_name

    Returns
    - List[Column]
    """

    cols: List[Column] = []
    seen: set[str] = set()
    for entry in attributes or []:
        if not isinstance(entry, dict) or not entry:
            continue
        # Some entries may contain more than one key; scan all items
        for label, details in entry.items():
            if not isinstance(details, dict):
                continue
            if details.get("level") != "Basic":
                continue
            key = details.get("variable_name")
            if not key or key in seen:
                continue
            seen.add(key)
            cols.append(Column(name=str(label), key=str(key)))
    return cols

def build_format_sets_from_commands(
    commands_json_path: str | Path,
    *,
    include_only_create: bool = True,
    default_types: Optional[List[str]] = None
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

    Returns
    - FormatSetDict keyed by set names derived from display_name + "-DrE".

    Notes
    - Columns are derived from Attributes entries whose level == "Basic".
    - If find_method is present, an ActionParameter is created.
    """
    path = Path(commands_json_path)
    data = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(data, dict):
        items_iter = data.items()
    elif isinstance(data, list):
        # If it’s a list of command objects, synthesize keys from display_name or index
        def _key_for(idx, obj):
            dn = str(obj.get("display_name", "")).strip()
            return dn or f"cmd_{idx}"

        items_iter = ((_key_for(i, obj), obj) for i, obj in enumerate(data))
    else:
        raise ValueError("commands.json root must be an object/dict or an array of command objects")
    data = dict(items_iter).get("Command Specifications", {})
    logger.info(
        f"Loaded commands.json from {path} with {len(data)} commands"
    )


    results = FormatSetDict()
    types = default_types or ["ALL"]

    for cmd_key, cmd_obj in data.items():
        if not isinstance(cmd_obj, dict):
            continue
        if include_only_create and not _is_create_command(cmd_key, cmd_obj):
            continue

        display_name = str(cmd_obj.get("display_name", "")).strip()
        if not display_name:
            logger.debug(f"Skip {cmd_key!r}: missing display_name")
            continue
        set_name = re.sub(r"\s+", "-", display_name)
        set_name = set_name.strip() + "-DrE"
        # set_name = _derive_set_name_from_display_name(display_name)
        if not set_name:
            logger.debug(f"Skip {cmd_key!r}: could not derive set name from display_name={display_name!r}")
            continue

        columns = _extract_basic_columns_from_attributes(cmd_obj.get("Attributes", []))
        if not columns:
            logger.debug(f"Skip {set_name}: no Basic attributes")
            continue

        find_method = cmd_obj.get("find_method") or ""
        constraints = _safe_parse_constraints(cmd_obj.get("find_constraints"))
        action = None
        if find_method:
            action = ActionParameter(
                function=find_method,
                required_params=["search_string"],
                optional_params=OPTIONAL_PARAMS,
                spec_params=constraints or {},
            )

        fs = FormatSet(
            target_type=display_name,
            heading=f"{set_name} Attributes",
            description=f"Auto-generated format for {display_name} (Create).",
            family=cmd_obj.get("family"),
            formats=[Format(types=types, columns=columns)],
            action=action
        )
        results[set_name] = fs

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
    from pyegeria.base_report_formats import report_specs  # local import to avoid cycles on tooling

    gen = build_format_sets_from_commands(
        commands_json_path,
        include_only_create=include_only_create,
        default_types=default_types,
    )
    count = 0
    for name, fs in gen.items():
        report_specs[name] = fs
        count += 1
    logger.info(f"Merged {count} generated format sets into built-ins")
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
    """Render a Format instance as Python code, including types and columns."""
    cols = getattr(fmt, 'columns', []) or []
    types = getattr(fmt, 'types', []) or []
    col_code = ", ".join(_format_column(c) for c in cols)
    parts = [f"types={_py_literal(list(types))}", f"columns=[{col_code}]"]
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
        "from pyegeria._output_format_models import Column, Format, ActionParameter, FormatSet, FormatSetDict\n\n"
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


def main():
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
    parser = argparse.ArgumentParser(description="Generate FormatSets from commands.json")
    parser.add_argument("commands_json", nargs="?", help="Path to commands.json")
    parser.add_argument("output_json", nargs="?", help="Path to output JSON file (when --emit json)")
    parser.add_argument("--emit", choices=["json", "dict", "code"], default="json",
                        help="Choose output mode: save JSON file, write Python code, or work with in-memory FormatSetDict")
    parser.add_argument("--merge", action="store_true",
                        help="Merge generated sets into built-in registry (report_specs)")
    parser.add_argument("--list", action="store_true",
                        help="When emitting dict (and/or after merge), list set names to stdout")
    args = parser.parse_args()

    try:
        input_file = args.commands_json or Prompt.ask(
            "Enter commands.json:", default="md_processing/data/commands.json"
        )

        if args.emit == "json":
            # JSON output path
            output_file = args.output_json or Prompt.ask(
                "Output File:", default="md_processing/data/generated_format_sets.json"
            )
            save_generated_format_sets(input_file, output_file)
            if args.merge:
                # Also load and merge saved JSON into registry for convenience
                from pyegeria.base_report_formats import load_report_specs
                load_report_specs(output_file, merge=True)
                logger.info("Merged saved JSON into built-in registry")
            elif args.emit == "code":
                # Python code output path
                output_file = args.output_json or Prompt.ask(
                    "Output Python File:", default="pyegeria/dr_egeria_reports.py"  # Changed from config/
                )
                saved_path = save_generated_format_sets_code(input_file, output_file)
                logger.info(f"Generated Python code written to {saved_path}")

        if args.merge:
            # Dynamically import and merge the generated variable
            try:
                import importlib.util
                import sys as _sys

                # Convert to absolute path to ensure spec_from_file_location can find it
                abs_output_file = saved_path.resolve()

                spec = importlib.util.spec_from_file_location("_gen_fs_module", abs_output_file)
                if spec is None or spec.loader is None:
                    raise ImportError(f"Could not create module spec from {abs_output_file}")

                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)  # type: ignore

                generated = getattr(mod, "generated_format_sets", None)
                if generated:
                    from pyegeria.base_report_formats import report_specs
                    merged = 0
                    for name, fs in generated.items():
                        report_specs[name] = fs
                        merged += 1
                    logger.info(f"Merged {merged} generated format sets from code into built-ins")
                else:
                    logger.warning("No 'generated_format_sets' found in generated code module")
            except Exception as e:
                logger.error(f"Failed to import and merge generated code: {e}")
        else:
            # Emit dict path: build in memory
            sets = generate_format_sets(input_file)
            logger.info(f"Generated {len(sets)} format sets (in-memory FormatSetDict)")
            if args.merge:
                from pyegeria.base_report_formats import report_specs
                merged = 0
                for name, fs in sets.items():
                    report_specs[name] = fs
                    merged += 1
                logger.info(f"Merged {merged} generated format sets into built-ins")
                if args.list:
                    # If merged, show names from the global registry that match the generated ones
                    names = sorted(list(sets.keys()))
                    print("Merged set names:")
                    for n in names:
                        print(f"- {n}")
            else:
                if args.list:
                    names = sorted(list(sets.keys()))
                    print(f"Generated set names ({len(names)}):")
                    for n in names:
                        print(f"- {n}")
    except (KeyboardInterrupt, EOFError):
        # Graceful exit when user cancels or stdin is not interactive
        pass

if __name__ == "__main__":
    main()
