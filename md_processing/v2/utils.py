"""
General utility functions for Dr.Egeria v2 processing.
"""
import re
from typing import Any, Optional, Type
from enum import Enum

def parse_key_value(text: str) -> dict[str, Any]:
    """
    Parses key-value pairs from various markdown formats:
    - Markdown tables: | Key | Value |
    - Lists: * Key: Value or - Key = Value
    - Simple blocks: Key: Value (one per line)
    """
    if not text:
        return {}
        
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
