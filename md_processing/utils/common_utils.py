"""
This file contains general utility functions for processing Egeria Markdown
"""
import os
import re
from datetime import datetime
from typing import List, Optional, Any

from rich import print
from rich.console import Console
from rich.markdown import Markdown

from pyegeria._globals import DEBUG_LEVEL

# Constants
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "170"))
console = Console(width=EGERIA_WIDTH)

message_types = {
    "INFO": "INFO-", "WARNING": "WARNING->", "ERROR": "ERROR->", "DEBUG-INFO": "DEBUG-INFO->",
    "DEBUG-WARNING": "DEBUG-WARNING->", "DEBUG-ERROR": "DEBUG-ERROR->", "ALWAYS": "\n\n==> "
}
ALWAYS = "ALWAYS"
ERROR = "ERROR"
INFO = "INFO"
WARNING = "WARNING"
pre_command = "\n---\n==> Processing command:"
command_seperator = Markdown("\n---\n")
EXISTS_REQUIRED = "Exists Required"

debug_level = DEBUG_LEVEL

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
        msg_type: The type of the message, such as 'WARNING', 'ERROR', 'INFO', or
            'ALWAYS'.
        msg: The content of the message to display.
        verbosity: The verbosity level, which determines how the message is
            displayed ('verbose', 'quiet', or 'debug').
    """
    if msg_level == "ALWAYS":
        print(f"{message_types.get(msg_level, '')}{msg}")
    elif verbosity == "verbose" and msg_level in ["INFO", "WARNING", "ERROR"]:
        print(f"{message_types.get(msg_level, '')}{msg}")
    elif verbosity == "quiet" and msg_level in ["WARNING", "ERROR"]:
        print(f"{message_types.get(msg_level, '')}{msg}")
    elif verbosity == "debug" and msg_level in ["INFO", "WARNING", "ERROR", "DEBUG-INFO", "DEBUG-WARNING", "DEBUG-ERROR"]:
        print(f"{message_types.get(msg_level, '')}{msg}")
    elif verbosity == "display-only" and msg_level in ["ALWAYS", "ERROR"]:
        print(f"{message_types.get(msg_level, '')}{msg}")


def process_provenance_command(file_path: str, txt: [str]) -> str:
    """
    Processes a provenance command by extracting the file path and current datetime.

    Args:
        file_path: The path to the file being processed.
        txt: The text containing the provenance command.

    Returns:
        A string containing the provenance information.
    """
    now = get_current_datetime_string()
    file_name = os.path.basename(file_path)
    provenance = f"\n\n\n# Provenance:\n \n* Derived from processing file {file_name} on {now}\n"
    return provenance