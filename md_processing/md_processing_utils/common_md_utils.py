"""
This file contains general utility functions for processing Egeria Markdown
"""
import os
import re
from datetime import datetime
from typing import Any
from loguru import logger
from rich import print
from rich.console import Console
from rich.markdown import Markdown

from pyegeria._globals import DEBUG_LEVEL
from md_processing.md_processing_utils.message_constants import message_types

# Constants
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "170"))
console = Console(width=EGERIA_WIDTH)

debug_level = DEBUG_LEVEL
global COMMAND_DEFINITIONS

def split_tb_string(input: str)-> [Any]:
    """Split the string and trim the items"""
    l = [item.strip() for item in re.split(r'[;,\n]+',input)] if input is not None else None
    return l

def str_to_bool(value: str) -> bool:
    """Converts a string to a boolean value."""
    return value.lower() in ("yes", "true", "t", "1")

def render_markdown(markdown_text: str) -> None:
    """Renders the given markdown text in the console."""
    console.print(Markdown(markdown_text))


def is_valid_iso_date(date_text) -> bool:
    """Checks if the given string is a valid ISO date."""
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def set_debug_level(directive: str) -> None:
    """Sets the debug level for the script."""
    global debug_level
    if directive == "display":
        debug_level = "display-only"


def get_current_datetime_string():
    """Returns the current date and time as a human-readable string."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    return now


def print_msg(msg_level: str, msg: str, verbosity: str):
    """
    Prints a message based on its type and verbosity level.

    This function handles the output of messages depending on the specified
    verbosity level and message type. It uses predefined message types and
    formats the output accordingly.

    Args:
        msg_level: The type of the message, such as 'WARNING', 'ERROR', 'INFO', or
            'ALWAYS'.
        msg: The content of the message to display.
        verbosity: The verbosity level, which determines how the message is
            displayed ('verbose', 'quiet', or 'debug').
    """
    if msg_level == "ALWAYS":
        print(f"{message_types.get(msg_level, '')}{msg}")
    # else:
    #     logger.info(f"{message_types.get(msg_level, '')}{msg}")
    # elif verbosity == "verbose" and msg_level in ["INFO", "WARNING", "ERROR"]:
    #     print(f"{message_types.get(msg_level, '')}{msg}")
    # elif verbosity == "quiet" and msg_level in ["WARNING", "ERROR"]:
    #     print(f"{message_types.get(msg_level, '')}{msg}")
    # elif verbosity == "debug" and msg_level in ["INFO", "WARNING", "ERROR", "DEBUG-INFO", "DEBUG-WARNING",
    #                                             "DEBUG-ERROR"]:
    #     print(f"{message_types.get(msg_level, '')}{msg}")
    # elif verbosity == "display-only" and msg_level in ["ALWAYS", "ERROR"]:
    #     print(f"{message_types.get(msg_level, '')}{msg}")
    elif msg_level == "ERROR":
        logger.error(f"{message_types.get(msg_level, '')}{msg}")
    elif msg_level == "WARNING":
        logger.warning(f"{message_types.get(msg_level, '')}{msg}")
    elif msg_level == "DEBUG":
        logger.debug(f"{message_types.get(msg_level, '')}{msg}")
    else:
        logger.info(f"{message_types.get(msg_level, '')}{msg}")

def process_provenance_command(file_path: str, txt: [str]) -> str:
    """
    Processes a provenance object_action by extracting the file path and current datetime.

    Args:
        file_path: The path to the file being processed.
        txt: The text containing the provenance object_action.

    Returns:
        A string containing the provenance information.
    """
    now = get_current_datetime_string()
    file_name = os.path.basename(file_path)
    provenance = f"\n\n\n# Provenance:\n \n* Derived from processing file {file_name} on {now}\n"
    return provenance


# Dictionary to store element information to avoid redundant API calls
element_dictionary = {}


def get_element_dictionary():
    """
    Get the shared element dictionary.

    Returns:
        dict: The shared element dictionary
    """
    global element_dictionary
    return element_dictionary


def update_element_dictionary(key, value):
    """
    Update the shared element dictionary with a new key-value pair.

    Args:
        key (str): The key to update
        value (dict): The value to associate with the key
    """
    global element_dictionary
    if (key is None or value is None):
        print(f"===>ERROR Key is {key} and value is {value}")
        return
    element_dictionary[key] = value


def clear_element_dictionary():
    """
    Clear the shared element dictionary.
    """
    global element_dictionary
    element_dictionary.clear()


def is_present(value: str) -> bool:
    global element_dictionary
    present = value in element_dictionary.keys() or any(
        value in inner_dict.values() for inner_dict in element_dictionary.values())
    return present


def find_key_with_value(value: str) -> str | None:
    """
    Finds the top-level key whose nested dictionary contains the given value.

    Args:
        data (dict): A dictionary where keys map to nested dictionaries.
        value (str): The value to search for.

    Returns:
        str | None: The top-level key that contains the value, or None if not found.
    """
    global element_dictionary
    # Check if the value matches a top-level key
    if value in element_dictionary.keys():
        return value

    # Check if the value exists in any of the nested dictionaries
    for key, inner_dict in element_dictionary.items():
        if value in inner_dict.values():
            return key

    return None  # If value not found
