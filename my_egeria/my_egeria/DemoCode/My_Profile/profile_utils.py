"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Utility and data transformation functions for My Profile Textual App.
"""

import re
from typing import Any


def truncate_at_sequence(data: Any, target: str = "specificationMermaidGraph") -> tuple[Any, bool]:
    """
    Recursively traverses data. Truncates strings containing the target
    and drops all following sibling items within lists or dictionaries.
    Returns (truncated_data, should_terminate_parent_container)
    """
    # Handle Strings
    if isinstance(data, str):
        if target in data:
            # Drop the sequence and everything after it
            truncated_str = data.split(target)[0]
            return truncated_str, True
        return data, False

    # Handle Dictionaries
    elif isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            # First, check if the key itself contains the target
            if isinstance(key, str) and target in key:
                truncated_key = key.split(target)[0]
                if truncated_key:  # Keep key fragment if not empty
                    new_dict[truncated_key] = value
                return new_dict, True

            # Recursively check the value
            updated_value, terminate = truncate_at_sequence(value, target)
            new_dict[key] = updated_value
            if terminate:
                return new_dict, True
        return new_dict, False

    # Handle Lists and Tuples
    elif isinstance(data, (list, tuple)):
        new_list = []
        for item in data:
            updated_item, terminate = truncate_at_sequence(item, target)
            new_list.append(updated_item)
            if terminate:
                break
        # Maintain original type integrity
        return (tuple(new_list) if isinstance(data, tuple) else new_list), terminate

    # Handle Booleans, Numbers, None
    return data, False


def clean_structure(data: Any, target: str = "specificationMermaidGraph") -> Any:
    """Helper wrapper for clean execution of truncate_at_sequence."""
    result, _ = truncate_at_sequence(data, target)
    return result


def bools_to_strings(data: Any) -> Any:
    """
    Recursively traverses data structures and converts
    all Boolean values into their corresponding string format.
    """
    # Check explicitly for bool first (since bool is a subclass of int in Python)
    if isinstance(data, bool):
        return str(data)

    # Handle Dictionaries
    elif isinstance(data, dict):
        return {key: bools_to_strings(value) for key, value in data.items()}

    # Handle Lists and Tuples
    elif isinstance(data, (list, tuple)):
        converted = [bools_to_strings(item) for item in data]
        return tuple(converted) if isinstance(data, tuple) else converted

    # Return all other types unchanged (ints, floats, strings, None)
    return data


def extract_glossary_terms(text: str) -> list[str]:
    """
    Extracts GlossaryTerm items from a string structure.
    Pattern: Starts with 'GlossaryTerm::', ends at the next ','.
    """
    pattern = r"GlossaryTerm::([^,\']+)"
    matches = re.findall(pattern, text)
    return [match.strip() for match in matches]
