"""
Base class for processing Egeria entities from markdown.
"""

import re
from datetime import datetime
from typing import List, Optional, Dict, Any

from rich import print
from rich.console import Console
from rich.markdown import Markdown

import os
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "200"))
console = Console(width=EGERIA_WIDTH)

from .constants import ERROR, INFO, WARNING, pre_command


class EntityProcessor:
    """Base class for processing Egeria entities from markdown."""

    def __init__(self, client: Any, element_dictionary: Dict[str, Dict[str, str]]):
        """
        Initialize the processor.

        Args:
            client: The Egeria client to use for API calls
            element_dictionary: Dictionary to store entity information
        """
        self.client = client
        self.element_dictionary = element_dictionary

    def extract_command(self, block: str) -> Optional[str]:
        """
        Extracts the command from a markdown block.

        Args:
            block: The markdown block to extract from

        Returns:
            The extracted command or None if not found
        """
        match = re.search(r"#(.*?)(?:##|\n|$)", block)
        if match:
            return match.group(1).strip()
        return None

    def extract_attribute(self, text: str, labels: List[str]) -> Optional[str]:
        """
        Extracts an attribute from markdown text.

        Args:
            text: The markdown text
            labels: List of possible labels for the attribute

        Returns:
            The extracted attribute value or None if not found
        """
        for label in labels:
            pattern = rf"## {re.escape(label)}\n(.*?)(?:#|---|$)"
            match = re.search(pattern, text, re.DOTALL)
            if match:
                extracted_text = re.sub(r'\n+', '\n', match.group(1).strip())
                if not extracted_text.isspace() and extracted_text:
                    return extracted_text
        return None

    def is_valid_iso_date(self, date_text: str) -> bool:
        """
        Checks if a string is a valid ISO date.

        Args:
            date_text: The date string to check

        Returns:
            True if valid, False otherwise
        """
        try:
            datetime.strptime(date_text, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def get_current_datetime_string(self) -> str:
        """
        Returns the current date and time as a formatted string.

        Returns:
            Formatted date and time string
        """
        return datetime.now().strftime('%Y-%m-%d %H:%M')

    def update_a_command(self, txt: str, command: str, obj_type: str, q_name: str, u_guid: str) -> str:
        """
        Updates a command in markdown text.

        Args:
            txt: The original markdown text
            command: The command to update
            obj_type: The object type
            q_name: The qualified name
            u_guid: The GUID

        Returns:
            Updated markdown text
        """
        u_guid = u_guid if u_guid else " "
        verb = command.split(' ')[0].strip()
        action = "Update" if (verb == "Create" and u_guid is not None) else "Create"
        txt = txt.replace(f"{command}", f'{action} {obj_type}\n')  # update the command
        txt = txt.replace('<GUID>', f'GUID\n{u_guid}')  # update with GUID
        txt = txt.replace('<Qualified Name>', f"Qualified Name\n{q_name}")
        if "Qualified Name" not in txt:
            txt += f"\n## Qualified Name\n{q_name}\n"
        if "GUID" not in txt:
            txt += f"\n## GUID\n{u_guid}\n"
        return txt

    def render_markdown(self, markdown_text: str) -> None:
        """
        Renders markdown text in the console.

        Args:
            markdown_text: The markdown text to render
        """
        console.print(Markdown(markdown_text))

    def process(self, txt: str, directive: str = "display") -> Optional[str]:
        """
        Process an entity command.

        Args:
            txt: The markdown text containing the command
            directive: The processing directive (display, validate, or process)

        Returns:
            Updated markdown text or None
        """
        raise NotImplementedError("Subclasses must implement this method")
