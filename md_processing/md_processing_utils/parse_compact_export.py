#!/usr/bin/env python3
"""
Parser for compact hierarchical Tinderbox command specification export.

Reads the compact JSON format with three sections:
1. attribute_definitions - full metadata for each attribute
2. bundles - hierarchy with inherits + own_attributes
3. commands - references bundle + custom_attributes

Expands bundle inheritance chains to produce full attribute lists per command.
"""

import json
import re
import sys
from pathlib import Path


def load_compact_json(path: str) -> dict:
    """
    Load and clean compact JSON.

    Strategy:
    1) Try strict JSON first.
    2) If it fails, remove trailing commas and attempt again.
    3) As a last resort, try json5 (if available) to tolerate minor issues like
       unescaped quotes. If json5 is not installed, raise a clear error with guidance.
    """
    text = Path(path).read_text()

    # Fast path: strict JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Remove trailing commas before } or ]
    cleaned = re.sub(r',\s*([}\]])', r'\1', text)

    # Heuristic: escape inner JSON blocks that are intended to be strings
    # e.g., find_constraints: "{\"metadata_element_types\": [\"X\"]}"
    def _escape_inner_json_strings(s: str) -> str:
        for key in ("find_constraints", "extra_find", "extra_constraints"):
            # Replace occurrences of: "key": "{ ... }" by escaping inner quotes
            pattern = r'(\"' + key + r'\"\s*:\s*)"(\{.*?\})"'
            try:
                s = re.sub(
                    pattern,
                    lambda m: m.group(1) + "\"" + m.group(2).replace("\\", "\\\\").replace("\"", r"\\\"") + "\"",
                    s,
                    flags=re.DOTALL,
                )
            except re.error:
                continue
        return s

    cleaned = _escape_inner_json_strings(cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e1:
        # Try json5 if available for more permissive parsing
        try:
            import json5  # type: ignore
            return json5.loads(text)
        except Exception as e2:  # noqa: F841
            raise json.JSONDecodeError(
                "Failed to parse compact JSON. Consider fixing quoting/commas in the file or install 'json5' (optional).",
                cleaned,
                e1.pos,
            ) from e1


def resolve_bundle_chain(bundle_name: str, bundles: dict, _seen: set = None) -> list[str]:
    """
    Walk the inheritance chain for a bundle, returning ordered list of
    attribute names from root to leaf (most general first).

    Detects cycles.
    """
    if _seen is None:
        _seen = set()

    if bundle_name in _seen:
        raise ValueError(f"Circular inheritance detected: {bundle_name}")
    _seen.add(bundle_name)

    if bundle_name not in bundles:
        raise KeyError(f"Bundle '{bundle_name}' not found in bundle definitions")

    bundle = bundles[bundle_name]
    parent = bundle.get("inherits")

    # Recursively resolve parent first
    if parent:
        parent_attrs = resolve_bundle_chain(parent, bundles, _seen)
    else:
        parent_attrs = []

    # Append this bundle's own attributes
    return parent_attrs + bundle.get("own_attributes", [])


def expand_command(command: dict, bundles: dict, attr_defs: dict) -> dict:
    """
    Expand a command's bundle reference into a full attribute list.

    Returns dict with:
    - all command metadata
    - 'all_attributes': ordered list of {name, variable_name, data_type, ...}
    - 'bundle_chain': list of bundle names from root to leaf
    """
    bundle_name = command.get("bundle", "")

    # Resolve bundle chain
    if bundle_name and bundle_name in bundles:
        bundle_attr_names = resolve_bundle_chain(bundle_name, bundles)

        # Build chain for reference
        chain = []
        current = bundle_name
        while current:
            chain.insert(0, current)
            current = bundles[current].get("inherits")
    else:
        bundle_attr_names = []
        chain = []

    # Add custom attributes
    custom_attr_names = command.get("custom_attributes", [])
    all_attr_names = bundle_attr_names + custom_attr_names

    # Resolve each attribute name to its full definition
    all_attributes = []
    missing = []
    for attr_name in all_attr_names:
        if attr_name in attr_defs:
            attr = {"name": attr_name, **attr_defs[attr_name]}
            all_attributes.append(attr)
        else:
            missing.append(attr_name)

    result = {
        "verb": command.get("verb"),
        "display_name": command.get("display_name"),
        "family": command.get("family"),
        "description": command.get("description"),
        "bundle": bundle_name,
        "bundle_chain": chain,
        "all_attributes": all_attributes,
        "total_attribute_count": len(all_attributes),
        "bundle_attribute_count": len(bundle_attr_names),
        "custom_attribute_count": len(custom_attr_names),
    }

    if missing:
        result["missing_attribute_defs"] = missing

    return result


def validate_export(data: dict) -> list[str]:
    """Run validation checks on the export data, return list of issues."""
    issues = []
    attr_defs = data["attribute_definitions"]
    bundles = data["bundles"]
    commands = data["commands"]

    # Check all bundle attribute references resolve
    for bname, bdef in bundles.items():
        for attr_name in bdef.get("own_attributes", []):
            if attr_name not in attr_defs:
                issues.append(f"Bundle '{bname}' references undefined attribute '{attr_name}'")
        parent = bdef.get("inherits")
        if parent and parent not in bundles:
            issues.append(f"Bundle '{bname}' inherits from undefined bundle '{parent}'")

    # Check all command bundle references resolve
    for cname, cdef in commands.items():
        bundle = cdef.get("bundle", "")
        if bundle and bundle not in bundles:
            issues.append(f"Command '{cname}' references undefined bundle '{bundle}'")
        for attr_name in cdef.get("custom_attributes", []):
            if attr_name not in attr_defs:
                issues.append(f"Command '{cname}' references undefined custom attribute '{attr_name}'")

    # Check for circular inheritance
    for bname in bundles:
        try:
            resolve_bundle_chain(bname, bundles)
        except ValueError as e:
            issues.append(str(e))

    # Check all attr_defs have variable_name
    for aname, adef in attr_defs.items():
        if not adef.get("variable_name"):
            issues.append(f"Attribute '{aname}' is missing variable_name")

    return issues


def print_command_summary(expanded: dict, indent: int = 2):
    """Pretty print an expanded command."""
    pad = " " * indent
    print(f"{pad}Verb: {expanded['verb']}")
    print(f"{pad}Bundle chain: {' → '.join(expanded['bundle_chain'])}")
    print(f"{pad}Total attributes: {expanded['total_attribute_count']} "
          f"({expanded['bundle_attribute_count']} from bundle + "
          f"{expanded['custom_attribute_count']} custom)")

    if expanded.get("missing_attribute_defs"):
        print(f"{pad}⚠ Missing defs: {expanded['missing_attribute_defs']}")

    # Group by level
    standard = [a for a in expanded["all_attributes"] if a.get("level", "") != "Advanced"]
    advanced = [a for a in expanded["all_attributes"] if a.get("level", "") == "Advanced"]

    print(f"{pad}Standard attributes ({len(standard)}):")
    for a in standard:
        print(f"{pad}  - {a.get('variable_name','?')}: {a.get('style','')}")

    if advanced:
        print(f"{pad}Advanced attributes ({len(advanced)}):")
        for a in advanced:
            print(f"{pad}  - {a.get('variable_name','?')}: {a.get('style','')}")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "test_compact_export.json"

    print(f"Loading: {path}")
    data = load_compact_json(path)

    print(f"\nExport date: {data['exported']}")
    print(f"Attribute definitions: {len(data['attribute_definitions'])}")
    print(f"Bundles: {len(data['bundles'])}")
    print(f"Commands: {len(data['commands'])}")

    # Validate
    print("\n=== Validation ===")
    issues = validate_export(data)
    if issues:
        print(f"Found {len(issues)} issues:")
        for issue in issues:
            print(f"  ⚠ {issue}")
    else:
        print("✅ All references valid, no issues found.")

    # Show bundle inheritance chains
    print("\n=== Bundle Hierarchy ===")
    for bname in data["bundles"]:
        chain = []
        current = bname
        while current:
            chain.insert(0, current)
            current = data["bundles"][current].get("inherits")
        attrs = resolve_bundle_chain(bname, data["bundles"])
        print(f"  {' → '.join(chain)}: {len(attrs)} total attributes")

    # Expand and show each command
    print("\n=== Expanded Commands ===")
    for cname, cdef in data["commands"].items():
        print(f"\n{cname}:")
        expanded = expand_command(cdef, data["bundles"], data["attribute_definitions"])
        print_command_summary(expanded)


if __name__ == "__main__":
    main()
