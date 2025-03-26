"""
Improved version of md_processing_utils.py with better modularity.
This module provides the same API as the original md_processing_utils.py
but uses the new modular entity_processors package internally.
"""

import re
from datetime import datetime
from typing import List, Optional, Dict, Any

from rich import print
from rich.console import Console
from rich.markdown import Markdown

from pyegeria._globals import (
    NO_TERMS_FOUND, NO_GLOSSARIES_FOUND, NO_PROJECTS_FOUND, NO_CATEGORIES_FOUND, 
    NO_ELEMENTS_FOUND
)
from pyegeria.project_manager_omvs import ProjectManager
from pyegeria.glossary_manager_omvs import GlossaryManager
from pyegeria.entity_processors import (
    EntityProcessor, GlossaryProcessor, ERROR, INFO, WARNING, pre_command
)

import os
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "200"))
console = Console(width=EGERIA_WIDTH)

# List of supported commands
command_list = ["Provenance", "Create Glossary", "Update Glossary", "Create Term", "Update Term", 
                "Create Personal Project", "Update Personal Project", "Create Category", "Update Category"]

# Global dictionary to store entity information
element_dictionary = {}


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


def get_current_datetime_string():
    """Returns the current date and time as a human-readable string."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    return now


def add_term_to_categories(egeria_client: GlossaryManager, term_guid: str, categories_exist: bool,
                           categories_list: List[str], element_dictionary: dict) -> None:
    """Add a term to categories."""
    if categories_exist is True and categories_list is not None:
        for category in categories_list:
            cat_guid = None
            cat_el = category.strip()
            if cat_el in element_dictionary:
                cat= element_dictionary.get(cat_el, None)
                cat_guid = cat.get('guid', None) if cat else None
            if cat_guid is None:
                cat_guid = egeria_client.__get_guid__(qualified_name=cat_el)
            egeria_client.add_term_to_category(term_guid, cat_guid)


def extract_command(block: str) -> Optional[str]:
    """Extract the command from a markdown block."""
    match = re.search(r"#(.*?)(?:##|\n|$)", block)  # Using a non capturing group
    if match:
        return match.group(1).strip()
    return None


def extract_attribute(text: str, labels: List[str]) -> Optional[str]:
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


def update_a_command(txt: str, command: str, obj_type: str, q_name: str, u_guid: str) -> str:
    """Update a command in markdown text."""
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


def process_provenance_command(file_path: str, txt: [str]) -> str:
    """Process a provenance command."""
    output = (f"* Derived from processing file {file_path} on "
              f"{get_current_datetime_string()}\n")
    pattern = rf"# {re.escape('Provenance')}\n(.*?)(?:#|---|$)"
    match = re.search(pattern, txt, re.DOTALL)
    if match:
        # Extract matched text and replace consecutive \n with a single \n
        extracted_text = re.sub(r'\n+', '\n', match.group(1).strip())
        if not extracted_text.isspace() and extracted_text:
            existing_prov =  extracted_text  # Return the cleaned text
        else:
            existing_prov = None
    print(f"txt is: {txt}, existing_prov: {existing_prov}")
    existing_prov = existing_prov if existing_prov else " "
    return f"\n# Provenance:\n{existing_prov}\n{output}\n"


def process_glossary_upsert_command(egeria_client: GlossaryManager, element_dictionary: dict, txt: str,
                                    directive: str = "display") -> Optional[str]:
    """
    Processes a glossary create or update command.
    
    Args:
        egeria_client: The GlossaryManager client
        element_dictionary: Dictionary to store entity information
        txt: The markdown text containing the command
        directive: The processing directive (display, validate, or process)
        
    Returns:
        Updated markdown text or None
    """
    processor = GlossaryProcessor(egeria_client, element_dictionary)
    return processor.process(txt, directive)


# The rest of the functions would be implemented similarly, delegating to the appropriate processor classes