from __future__ import annotations

import json
import os
from typing import Dict, Any, Iterable

from .parse_compact_export import load_compact_json, expand_command


def _to_semicolon_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple, set)):
        return "; ".join([str(v) for v in value if str(v).strip()])
    return str(value)


def _attr_to_legacy_entry(attr: Dict[str, Any]) -> Dict[str, Any]:
    # The legacy schema expects a one-item dict: { "Label": { ...metadata... } }
    label = attr.get("name") or attr.get("variable_name") or "Unknown"
    meta: Dict[str, Any] = dict(attr)
    # Remove wrapper key 'name' used only as the label
    meta.pop("name", None)
    return {label: meta}


def _command_to_legacy_spec(name: str, cdef: Dict[str, Any], expanded: Dict[str, Any]) -> Dict[str, Any]:
    # Copy known top-level fields if present in the compact command
    legacy: Dict[str, Any] = {}
    for key in (
        "display_name",
        "qn_prefix",
        "family",
        "description",
        "verb",
        "upsert",
        "attach",
        "ReferenceURL",
        "level",
        "find_method",
        "find_constraints",
        "extra_find",
        "extra_constraints",
        "Journal Entry",
    ):
        if key in cdef:
            legacy[key] = cdef[key]

    # Normalize alternate_names to the legacy semicolon string
    alt = cdef.get("alternate_names", "")
    legacy["alternate_names"] = _to_semicolon_str(alt)

    # Build legacy Attributes from expanded attribute definitions
    attrs_legacy = []
    for attr in expanded.get("all_attributes", []):
        attrs_legacy.append(_attr_to_legacy_entry(attr))
    legacy["Attributes"] = attrs_legacy

    return legacy




def load_compact_specs_from_dir(dir_path: str, families_allowlist: Iterable[str] | None = None) -> Dict[str, Dict[str, Any]]:
    """
    Load all compact command files from a directory and return a mapping suitable
    for merging into the legacy COMMAND_DEFINITIONS["Command Specifications"].

    Args:
        dir_path: Path to directory with compact JSON files.
        families_allowlist: If provided, include only commands whose 'family' is in this set.

    Returns:
        Dict[str, Dict]: { command_name: legacy_style_spec }
    """
    if families_allowlist:
        families = {f.strip() for f in families_allowlist if f and f.strip()}
    else:
        families = set()

    specs: Dict[str, Dict[str, Any]] = {}

    if not os.path.isdir(dir_path):
        return specs

    all_attr_defs = {}
    all_bundles = {}
    all_commands = {}

    for fname in os.listdir(dir_path):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(dir_path, fname)
        try:
            data = load_compact_json(fpath)
        except Exception as e:
            from loguru import logger
            logger.warning(f"Failed to load compact JSON {fname}: {e}")
            continue

        all_attr_defs.update(data.get("attribute_definitions", {}))
        all_bundles.update(data.get("bundles", {}))
        all_commands.update(data.get("commands", {}))

    for cname, cdef in all_commands.items():
        # Family gating
        fam = cdef.get("family")
        if families and fam not in families:
            continue
        
        try:
            expanded = expand_command(cdef, all_bundles, all_attr_defs)
            specs[cname] = _command_to_legacy_spec(cname, cdef, expanded)
        except (KeyError, ValueError) as e:
            from loguru import logger
            logger.warning(f"Skipping command '{cname}': {e}")
            continue

    return specs
