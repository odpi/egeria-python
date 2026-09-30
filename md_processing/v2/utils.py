"""
General utility functions for Dr.Egeria v2 processing.
"""
import json
import re
from typing import Any, Optional, Type
from enum import Enum

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
