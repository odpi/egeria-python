"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

General utility functions in support of the Egeria Python Client package.

"""

import json
from datetime import datetime
from loguru import logger
from rich import print, print_json
from rich.console import Console
from pyegeria.config import settings as app_settings
from typing import Callable, TypeVar

T = TypeVar('T', bound=Callable)

console = Console(width=200)

def init_log():
    pass

def print_rest_request_body(body):
    """

    Args:
        body:
    """
    pretty_body = json.dumps(body, indent=4)
    print_json(pretty_body, indent=4, sort_keys=True)


def print_rest_response(response):
    """

    Args:
        response:
    """
    print("Returns:")
    pretty_body = json.dumps(response, indent=4)
    print_json(pretty_body, indent=4, sort_keys=True)


def print_guid_list(guids):
    """Print a list of guids"""
    if guids is None:
        print("No assets created")
    else:
        pretty_guids = json.dumps(guids, indent=4)
        print_json(pretty_guids, indent=4, sort_keys=True)


#
# OCF Common services
# Working with assets - this set of functions displays assets returned from the open metadata repositories.
#




def body_slimmer(body: dict) -> dict:
    """body_slimmer is a little function to remove unused keys from a dict
    and recursively slim embedded dicts

    Parameters
    ----------
    body : the dictionary that you want to slim

    Returns
    -------
    dict:
        a slimmed body with all embedded dictionaries also slimmed
    """
    if body is None:
        return {}

    slimmed = {}
    for key, value in body.items():
        if value and not isinstance(value, tuple):
            if isinstance(value, dict):
                # Recursively slim embedded dictionaries
                slimmed_value = body_slimmer(value)
                if slimmed_value:  # Only include non-empty dictionaries
                    slimmed[key] = slimmed_value
            else:
                slimmed[key] = value
    return slimmed

import re

def camel_to_title_case(input_string):
    # Add a space before uppercase letters and capitalize each word
    result = re.sub(r'([a-z])([A-Z])', r'\1 \2', input_string).title()
    return result


def to_camel_case(input_string):
    """Convert an input string to camelCase, singularizing if plural.
    
    This function takes an input string, converts it to singular form if it's plural,
    and then transforms it to camelCase format (first word lowercase, subsequent words
    capitalized with no spaces).
    
    Parameters
    ----------
    input_string : str
        The string to convert to camelCase
        
    Returns
    -------
    str:
        The input string converted to camelCase, after singularization if needed
        
    Examples
    --------
    >>> to_camel_case("data categories")
    'dataCategory'
    >>> to_camel_case("business terms")
    'businessTerm'
    >>> to_camel_case("glossary categories")
    'glossaryCategory'
    """
    if not input_string:
        return ""
    
    # Convert to lowercase for consistent processing
    lowercase_input = input_string.lower()
    
    # First, convert to singular if plural
    singular = lowercase_input
    
    # Handle common plural endings
    if singular.endswith('ies'):
        singular = singular[:-3] + 'y'
    elif singular.endswith('es'):
        # Special cases like 'classes' -> 'class'
        if singular.endswith('sses') or singular.endswith('ches') or singular.endswith('shes') or singular.endswith('xes'):
            singular = singular[:-2]
        else:
            singular = singular[:-1]
    elif singular.endswith('s') and not singular.endswith('ss'):
        singular = singular[:-1]
    
    # Split the string into words and convert to camelCase
    words = singular.split()
    if not words:
        return ""
    
    # First word is lowercase, rest are capitalized
    result = words[0]
    for word in words[1:]:
        result += word.capitalize()
    
    return result

def to_pascal_case(input_string)->str:
    """
        Convert input string to PascalCase, singularizing if plural.
    Args:
        input_string ():

    Returns:
        transformed string
    """
    result = to_camel_case(input_string)
    output_string = result[0].upper() + result[1:]
    return output_string

def flatten_dict_to_string(d: dict) -> str:
    """Flatten a dictionary into a string and replace quotes with backticks."""
    try:
        flat_string = ", ".join(
            # Change replace(\"'\", '`') to replace("'", '`')
            f"{key}=`{str(value).replace('\"', '`').replace("'", '`')}`"
            for key, value in d.items()
        )
        return flat_string
    except Exception as e:
        # Corrected syntax for exception chaining
        raise Exception("Error flattening dictionary") from e
# The decorator logic, which applies @logger.catch dynamically


import json
import re


# def parse_to_dict(input_str: str):
#     """
#     Check if a string is valid JSON or a name:value list without braces and convert to a dictionary.
#
#     Args:
#         input_str: The input string to parse.
#
#     Returns:
#         dict: A dictionary converted from the input string.
#         None: If the input is neither valid JSON nor a valid name:value list.
#     """
#
#     if input_str is None:
#         return None
#
#     # Check if the input string is valid JSON
#     try:
#         result = json.loads(input_str)
#         if isinstance(result, dict):  # Ensure it's a dictionary
#             return result
#     except json.JSONDecodeError:
#         pass
#
#     # Check if input string looks like a name:value list
#     # Supports both comma and newline as separators
#     pattern = r'^(\s*("[^"]+"|\'[^\']+\'|[a-zA-Z0-9_-]+)\s*:\s*("[^"]+"|\'[^\']+\'|[a-zA-Z0-9 _-]*)\s*)' \
#               r'(\s*[,|\n]\s*("[^"]+"|\'[^\']+\'|[a-zA-Z0-9_-]+)\s*:\s*("[^"]+"|\'[^\']+\'|[a-zA-Z0-9 _-]*)\s*)*$'
#     if re.match(pattern, input_str.strip()):
#         try:
#             # Split by ',' or '\n' and process key-value pairs
#             pairs = [pair.split(":", 1) for pair in re.split(r'[,|\n]+', input_str.strip())]
#             return {key.strip().strip('\'"'): value.strip().strip('\'"') for key, value in pairs}
#         except Exception:
#             return None
#
#     # If neither pattern matches, return None
#     return None


def parse_to_dict(input_str: str) -> dict | None:
    """
    Parse input strings into a dictionary, handling both JSON and key-value pairs.
    Recovers from malformed JSON (e.g., where commas are missing between key-value pairs)
    and supports multiline values.

    Args:
        input_str (str): The input string to parse.

    Returns:
        dict: A parsed dictionary if validation is successful, or None if the string cannot be parsed.
    """
    if not input_str:
        return None

    # Attempt to parse valid JSON
    try:
        result = json.loads(input_str)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    # Fix malformed JSON or attempt alternate parsing for "key: value" patterns
    try:
        # Step 1: Inject missing commas where they are omitted between key-value pairs
        fixed_input = re.sub(
            r'("\s*:[^,}\n]+)\s*("(?![:,}\n]))',  # Find missing commas (key-value-value sequences)
            r'\1,\2',  # Add a comma between the values
            input_str
        )

        # Attempt to parse the fixed string as JSON
        try:
            result = json.loads(fixed_input)
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

        # Step 2: Handle key-value format fallback (supports multiline strings)
        # Matches `key: value` pairs, including multiline quoted values
        key_value_pattern = re.compile(r'''
            (?:"([^"]+)"|'([^']+)'|([a-zA-Z0-9_-]+))  # Key: quoted "key", 'key', or unquoted key
            \s*:\s*                                   # Key-value separator
            (?:"((?:\\.|[^"\\])*?)"|'((?:\\.|[^'\\])*?)'|([^\n,]+))  # Value: quoted or unquoted
        ''', re.VERBOSE | re.DOTALL)

        matches = key_value_pattern.findall(input_str)

        # Build dictionary from matches
        result_dict = {}
        for match in matches:
            key = next((group for group in match[:3] if group), "").strip()
            value = next((group for group in match[3:] if group), "").strip()
            result_dict[key] = value

        if result_dict:
            return result_dict
    except Exception as e:
        # Log or handle parsing exception if needed
        pass

    # If all parsing attempts fail, return None
    return None


def dynamic_catch(func: T) -> T:
    if app_settings.get("enable_logger_catchh", False):
        return logger.catch(func)  # Apply the logger.catch decorator
    else:
        return func  # Return the function unwrapped

def make_format_set_name_from_type(obj_type: str)-> str:
    formatted_name = obj_type.replace(" ", "-")
    return f"{formatted_name}-DrE"


if __name__ == "__main__":
    print("Main-Utils")
