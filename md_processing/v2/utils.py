"""
General utility functions for Dr.Egeria v2 processing.
"""
import json
import re
from typing import Any, Optional, Type
from enum import Enum

_TABLE_SEPARATOR = re.compile(r'^:?-{3,}:?$')


def parse_table(text: str) -> list[dict[str, Optional[str]]]:
    """
    Parse a markdown table into one dict per row, keyed by the header row's
    column names (the "Table" attribute style).

        | Value   | Display Name | Default |
        |---------|--------------|---------|
        | PENDING | Pending      | true    |

    gives [{"Value": "PENDING", "Display Name": "Pending", "Default": "true"}].
    Empty cells are None. A literal pipe inside a cell is written as \\|.
    Commas are ordinary text. Rows with no non-empty cell are skipped; a row
    with more cells than the header keeps only the first len(header) cells.
    Text that is not a table gives [].
    """
    if not text:
        return []

    def cells(line: str) -> list[str]:
        line = line.strip()
        if line.startswith('|'):
            line = line[1:]
        if line.endswith('|') and not line.endswith('\\|'):
            line = line[:-1]
        parts = re.split(r'(?<!\\)\|', line)
        return [p.strip().replace('\\|', '|') for p in parts]

    lines = [l for l in text.splitlines() if l.strip().startswith('|')]
    if len(lines) < 2:
        return []
    header = cells(lines[0])
    rows = []
    for line in lines[1:]:
        values = cells(line)
        if all(_TABLE_SEPARATOR.match(v) for v in values if v) and any(values):
            continue
        row = {col: (values[i] if i < len(values) and values[i] != "" else None)
               for i, col in enumerate(header) if col}
        if any(v is not None for v in row.values()):
            rows.append(row)
    return rows


def parse_line_list(text: str) -> list[str]:
    """
    Split on new lines only (the "Line List" attribute style), stripping a
    leading markdown bullet. Unlike "Simple List", commas and semicolons are
    part of the value, so "Washington, D.C." stays one item.
    """
    if not text:
        return []
    items = []
    for line in text.splitlines():
        item = re.sub(r'^\s*[\-\*\+]\s+', '', line).strip()
        if item:
            items.append(item)
    return items


def parse_key_value(text: str) -> dict[str, Any]:
    """
    Parses key-value pairs from various markdown formats:
    - Markdown tables: | Key | Value |
    - Lists: * Key: Value or - Key = Value
    - Simple blocks: Key: Value (one per line)
    - A JSON object: {"Key": "Value", ...}

    Values are always returned as strings (callers treat the result as a
    Map<String,String>). A non-string JSON value is JSON-encoded, so a caller
    that needs its real type back (report.py's _coerce_analytic_value) can
    json.loads it.
    """
    if not text:
        return {}

    # JSON object -- previously split on its first ':' like a "Key: Value" line,
    # silently producing keys like '{"owner"'.
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        try:
            parsed = json.loads(stripped)
        except ValueError:
            parsed = None
        if isinstance(parsed, dict):
            return {str(k): v if isinstance(v, str) else json.dumps(v) for k, v in parsed.items()}

    results = {}
    
    # Check for Markdown Table (| Key | Value |)
    if '|' in text:
        lines = [l.strip() for l in text.splitlines() if '|' in l and '---' not in l]
        if len(lines) > 1: # Header + at least one row
            # Attempt to Parse table
            for line in lines[1:]: # Skip potential header
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 2:
                    results[parts[0]] = parts[1]
            if results: return results

    # Check for List/Simple structures
    for line in text.splitlines():
        line = line.strip()
        if not line: continue
        
        # Remove list markers
        line = re.sub(r'^[*+-]\s*', '', line)
        
        # Split by : or =
        if ':' in line:
            k, v = line.split(':', 1)
            results[k.strip()] = v.strip()
        elif '=' in line:
            k, v = line.split('=', 1)
            results[k.strip()] = v.strip()
            
    return results
