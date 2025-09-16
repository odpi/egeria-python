import argparse
import json
import re
import argparse
from pathlib import Path
from typing import Iterable, List, Optional

from loguru import logger
from rich.prompt import Prompt

from pyegeria._output_format_models import Column, Format, ActionParameter, FormatSet, FormatSetDict
from pyegeria._output_formats import OPTIONAL_PARAMS  # ["page_size","start_from","starts_with","ends_with","ignore_case"]

def _is_create_command(cmd_key: str, cmd_obj: dict) -> bool:
    name = str(cmd_obj.get("display_name", "")).strip()
    return (isinstance(cmd_key, str) and cmd_key.strip().lower().startswith("create")) or \
           (name.lower().startswith("create"))

def _derive_set_name_from_display_name(display_name: str) -> str:
    """From 'Create Governance Strategy Definition' -> 'GovernanceStrategyDefinition'."""
    if not display_name:
        return ""
    parts = display_name.strip().split()
    if len(parts) <= 1:
        return re.sub(r"\s+", "", display_name.strip())+"-DrE"
    rest = " ".join(parts[1:]).strip()
    rest = rest+"-DrE"
    return re.sub(r"\s+", "", rest)

def _safe_parse_constraints(s) -> dict:
    """Parse find_constraints (often an escaped JSON string) into a dict."""
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
    """
    attributes: list of single-key dicts, e.g.
      {"Display Name": {"variable_name": "display_name", "level": "Basic", ...}}
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
    """
    Convert commands.json into a FormatSetDict following your mappings.
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
    """Build and save to a JSON file loadable by _output_formats.load_output_format_sets."""
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
    """Return a FormatSetDict built from commands.json (no file I/O)."""
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
    """Build a FormatSetDict and merge into pyegeria._output_formats.output_format_sets.
    Returns the number of sets merged/added.
    """
    from pyegeria._output_formats import output_format_sets  # local import to avoid cycles on tooling

    gen = build_format_sets_from_commands(
        commands_json_path,
        include_only_create=include_only_create,
        default_types=default_types,
    )
    count = 0
    for name, fs in gen.items():
        output_format_sets[name] = fs
        count += 1
    logger.info(f"Merged {count} generated format sets into built-ins")
    return count


def _py_literal(value):
    """Render a Python literal safely for strings, lists, dicts, bools, None, numbers."""
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
    parts = [f"name={_py_literal(getattr(col, 'name', ''))}", f"key={_py_literal(getattr(col, 'key', ''))}"]
    fmt = getattr(col, 'format', None)
    if fmt not in (None, False):
        parts.append(f"format={_py_literal(bool(fmt))}")
    return "Column(" + ", ".join(parts) + ")"


def _format_action(ap: ActionParameter | None) -> str:
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
    cols = getattr(fmt, 'columns', []) or []
    types = getattr(fmt, 'types', []) or []
    col_code = ", ".join(_format_column(c) for c in cols)
    parts = [f"types={_py_literal(list(types))}", f"columns=[{col_code}]"]
    return "Format(" + ", ".join(parts) + ")"


def _format_formatset(fs: FormatSet) -> str:
    parts = []
    if getattr(fs, 'target_type', None):
        parts.append(f"target_type={_py_literal(fs.target_type)}")
    if getattr(fs, 'heading', None):
        parts.append(f"heading={_py_literal(fs.heading)}")
    if getattr(fs, 'description', None):
        parts.append(f"description={_py_literal(fs.description)}")
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
    """Render a FormatSetDict into a Python module string defining `var_name`."""
    header = (
        "# Auto-generated by gen_format_sets.py\n"
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
    """Build FormatSetDict and save as Python code to out_file."""
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
    parser = argparse.ArgumentParser(description="Generate FormatSets from commands.json")
    parser.add_argument("commands_json", nargs="?", help="Path to commands.json")
    parser.add_argument("output_json", nargs="?", help="Path to output JSON file (when --emit json)")
    parser.add_argument("--emit", choices=["json", "dict", "code"], default="json",
                        help="Choose output mode: save JSON file, write Python code, or work with in-memory FormatSetDict")
    parser.add_argument("--merge", action="store_true",
                        help="Merge generated sets into built-in registry (output_format_sets)")
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
                from pyegeria._output_formats import load_output_format_sets
                load_output_format_sets(output_file, merge=True)
                logger.info("Merged saved JSON into built-in registry")
        elif args.emit == "code":
            # Python code output path
            output_file = args.output_json or Prompt.ask(
                "Output Python File:", default="md_processing/data/generated_format_sets.py"
            )
            save_generated_format_sets_code(input_file, output_file)
            if args.merge:
                # Dynamically import and merge the generated variable
                try:
                    import importlib.util
                    import sys as _sys
                    spec = importlib.util.spec_from_file_location("_gen_fs_module", output_file)
                    mod = importlib.util.module_from_spec(spec)
                    assert spec and spec.loader
                    spec.loader.exec_module(mod)  # type: ignore
                    generated = getattr(mod, "generated_format_sets", None)
                    if generated:
                        from pyegeria._output_formats import output_format_sets
                        merged = 0
                        for name, fs in generated.items():
                            output_format_sets[name] = fs
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
                from pyegeria._output_formats import output_format_sets
                merged = 0
                for name, fs in sets.items():
                    output_format_sets[name] = fs
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
