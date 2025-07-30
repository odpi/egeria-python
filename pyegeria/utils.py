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
from pyegeria.load_config import get_app_config

app_settings = get_app_config()

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


def print_response(response):
    """

    Args:
        response:

    Returns:
        : str
    """
    pretty_response = json.dumps(response.json(), indent=4)
    print(" ")
    print("Response: ")
    print(pretty_response)
    print(" ")


def print_unexpected_response(server_name, platform_name, platform_url, response):
    """

    Args:
        server_name:
        platform_name:
        platform_url:
        response:
    """
    if response.status_code == 200:
        related_http_code = response.json().get("related_http_code")
        if related_http_code == 200:
            print("Unexpected response from server " + server_name)
            print_response(response)
        else:
            exceptionErrorMessage = response.json().get("exceptionErrorMessage")
            exceptionSystemAction = response.json().get("exceptionSystemAction")
            exceptionUserAction = response.json().get("exceptionUserAction")
            if exceptionErrorMessage is not None:
                print(exceptionErrorMessage)
                print(" * " + exceptionSystemAction)
                print(" * " + exceptionUserAction)
            else:
                print("Unexpected response from server " + server_name)
                print_response(response)
    else:
        print(
            "Unexpected response from server platform "
            + platform_name
            + " at "
            + platform_url
        )
        print_response(response)


def get_last_guid(guids):
    """

    Args:
        guids:

    Returns:

    """
    if guids is None:
        return None
    else:
        return guids[-1]


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
        if value:
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


def dynamic_catch(func):
    if app_settings.get("enable_logger_catchh", False):
        return logger.catch(func)  # Apply the logger.catch decorator
    else:
        return func  # Return the function unwrapped

if __name__ == "__main__":
    print("Main-Utils")
