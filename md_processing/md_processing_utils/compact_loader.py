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


def _command_to_spec(name: str, cdef: Dict[str, Any], expanded: Dict[str, Any]) -> Dict[str, Any]:
    # Copy known top-level fields if present in the compact command
    spec: Dict[str, Any] = {}
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
        "OM_TYPE",
    ):
        if key in cdef:
            spec[key] = cdef[key]

    # Normalize alternate_names to the legacy semicolon string
    alt = cdef.get("alternate_names", "")
    spec["alternate_names"] = _to_semicolon_str(alt)

    # Use expanded attributes directly (already resolved and expanded)
    # We ensure each attribute has a 'style' for processor compatibility
    attrs = expanded.get("all_attributes", [])
    for attr in attrs:
        if not attr.get("style"):
            attr["style"] = "Simple"
            
    # Apply defaults from md_processing_constants to fill in missing labels/etc.
    from .md_processing_constants import add_default_upsert_attributes, add_default_link_attributes
    if spec.get("upsert"):
        spec["Attributes"] = add_default_upsert_attributes(attrs)
    elif spec.get("attach"):
        spec["Attributes"] = add_default_link_attributes(attrs)
    else:
        spec["Attributes"] = attrs

    return spec


def load_compact_specs_from_dir(dir_path: str, families_allowlist: Iterable[str] | None = None) -> Dict[str, Dict[str, Any]]:
    """
    Load all compact command files from a directory and return a mapping 
    for COMMAND_DEFINITIONS["Command Specifications"].

    Args:
        dir_path: Path to directory with compact JSON files.
        families_allowlist: If provided, include only commands whose 'family' is in this set.

    Returns:
        Dict[str, Dict]: { command_name: command_spec }
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
    loaded_files = []

    from loguru import logger

    for fname in sorted(os.listdir(dir_path)):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(dir_path, fname)
        try:
            data = load_compact_json(fpath)

            # Merge attribute definitions with conflict detection
            for aname, adef in data.get("attribute_definitions", {}).items():
                if aname in all_attr_defs:
                    # If the existing definition has valid_values and the new one doesn't, keep the old one
                    # This prevents files with empty valid_values from overwriting complete ones.
                    if all_attr_defs[aname].get("valid_values") and not adef.get("valid_values"):
                        continue
                    
                    if all_attr_defs[aname] != adef:
                        logger.debug(f"Attribute '{aname}' in {fname} differs from previous definition.")
                all_attr_defs[aname] = adef

            # Merge bundle definitions with conflict detection
            for bname, bdef in data.get("bundles", {}).items():
                if bname in all_bundles and all_bundles[bname] != bdef:
                    logger.debug(f"Bundle '{bname}' in {fname} differs from previous definition.")
                all_bundles[bname] = bdef

            loaded_files.append((fname, data))
        except Exception as e:
            logger.warning(f"Failed to load compact JSON {fname}: {e}")
            continue

    for fname, data in loaded_files:
        file_commands = data.get("commands", {})

        for cname, cdef in file_commands.items():
            fam = cdef.get("family")
            if families and fam not in families:
                continue

            if cname in specs:
                logger.warning(f"Command '{cname}' in {fname} overwrites a definition from a previous file.")

            try:
                expanded = expand_command(cdef, all_bundles, all_attr_defs)
                specs[cname] = _command_to_spec(cname, cdef, expanded)
            except (KeyError, ValueError) as e:
                logger.warning(f"Skipping command '{cname}' from {fname}: {e}")
                continue

    return specs
