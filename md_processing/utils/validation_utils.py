"""
This file contains functions for validating data for Egeria Markdown processing
"""
import re

from pyegeria._globals import NO_ELEMENTS_FOUND
from pyegeria.dr_egeria_state import get_element_dictionary, update_element_dictionary


def process_element_identifiers(egeria_client, element_type: str, element_labels: list[str], txt: str, action: str, version: str = None) -> tuple[str, str, bool, bool]:
    """
    Processes element identifiers from a string.

    Args:
        egeria_client: The Egeria client to use for validation.
        element_type: The type of element to process.
        element_labels: List of equivalent labels to search for
        txt: The input string.
        action: The action to perform (Create, Update, or Exists Required).
        version: The version of the element.

    Returns:
        A tuple containing:
        - The qualified name of the element
        - The GUID of the element
        - A boolean indicating if the element is valid
        - A boolean indicating if the element exists
    """
    from md_processing.utils.common_utils import debug_level, print_msg, EXISTS_REQUIRED
    from md_processing.utils.extraction_utils import process_simple_attribute

    element_name = process_simple_attribute(txt, element_labels)
    if element_name is None:
        return None, None, False, False

    element = get_element_by_name(egeria_client, element_type, element_name)
    if element is None:
        if action == EXISTS_REQUIRED or action == "Update":
            msg = f"{element_type} {element_name} not found"
            print_msg("ERROR", msg, debug_level)
            return None, None, False, False
        else:
            return None, None, True, False
    else:
        element_guid = element.get('guid', None)
        element_q_name = element.get('qualifiedName', None)
        if element_guid and element_q_name:
            if action == "Create":
                msg = f"{element_type} {element_name} already exists with GUID {element_guid}"
                print_msg("WARNING", msg, debug_level)
            else:
                msg = f"{element_type} {element_name} exists with GUID {element_guid}"
                print_msg("INFO", msg, debug_level)
            return element_q_name, element_guid, True, True
        else:
            msg = f"{element_type} {element_name} exists but has no GUID or qualified name"
            print_msg("ERROR", msg, debug_level)
            return None, None, False, True


def get_element_by_name(egeria_client, element_type: str, element_name: str) -> dict | None:
    """
    Gets an element by name.

    Args:
        egeria_client: The Egeria client to use for validation.
        element_type: The type of element to get.
        element_name: The name of the element to get.

    Returns:
        The element if found, otherwise None.
    """
    from md_processing.utils.common_utils import debug_level, print_msg
    from md_processing.utils.display_utils import (
        GLOSSARY_NAME_LABELS, CATEGORY_NAME_LABELS, TERM_NAME_LABELS, PROJECT_NAME_LABELS,
        BLUEPRINT_NAME_LABELS, COMPONENT_NAME_LABELS
    )

    # Check if we already have this element in our dictionary
    element_dict = get_element_dictionary()
    if element_dict:
        for q_name, details in element_dict.items():
            if details.get('display_name', '').lower() == element_name.lower():
                if element_type.lower() in q_name.lower():
                    msg = f"Found {element_type} {element_name} in dictionary with qualified name {q_name}"
                    print_msg("DEBUG-INFO", msg, debug_level)
                    return {'qualifiedName': q_name, 'guid': details.get('guid', None)}

    # If not in dictionary, query Egeria
    try:
        if element_type in GLOSSARY_NAME_LABELS:
            glossaries = egeria_client.list_glossaries()
            if glossaries == NO_ELEMENTS_FOUND:
                return None
            for glossary in glossaries:
                if glossary.get('displayName', '').lower() == element_name.lower():
                    q_name = glossary.get('qualifiedName', None)
                    guid = glossary.get('guid', None)
                    if q_name and guid:
                        update_element_dictionary(q_name, {'guid': guid, 'display_name': element_name})
                        return {'qualifiedName': q_name, 'guid': guid}
        elif element_type in CATEGORY_NAME_LABELS:
            categories = egeria_client.list_categories()
            if categories == NO_ELEMENTS_FOUND:
                return None
            for category in categories:
                if category.get('displayName', '').lower() == element_name.lower():
                    q_name = category.get('qualifiedName', None)
                    guid = category.get('guid', None)
                    if q_name and guid:
                        update_element_dictionary(q_name, {'guid': guid, 'display_name': element_name})
                        return {'qualifiedName': q_name, 'guid': guid}
        elif element_type in TERM_NAME_LABELS:
            terms = egeria_client.list_terms()
            if terms == NO_ELEMENTS_FOUND:
                return None
            for term in terms:
                if term.get('displayName', '').lower() == element_name.lower():
                    q_name = term.get('qualifiedName', None)
                    guid = term.get('guid', None)
                    if q_name and guid:
                        update_element_dictionary(q_name, {'guid': guid, 'display_name': element_name})
                        return {'qualifiedName': q_name, 'guid': guid}
        elif element_type in PROJECT_NAME_LABELS:
            projects = egeria_client.list_projects()
            if projects == NO_ELEMENTS_FOUND:
                return None
            for project in projects:
                if project.get('displayName', '').lower() == element_name.lower():
                    q_name = project.get('qualifiedName', None)
                    guid = project.get('guid', None)
                    if q_name and guid:
                        update_element_dictionary(q_name, {'guid': guid, 'display_name': element_name})
                        return {'qualifiedName': q_name, 'guid': guid}
        elif element_type in BLUEPRINT_NAME_LABELS:
            blueprints = egeria_client.list_solution_blueprints()
            if blueprints == NO_ELEMENTS_FOUND:
                return None
            for blueprint in blueprints:
                if blueprint.get('displayName', '').lower() == element_name.lower():
                    q_name = blueprint.get('qualifiedName', None)
                    guid = blueprint.get('guid', None)
                    if q_name and guid:
                        update_element_dictionary(q_name, {'guid': guid, 'display_name': element_name})
                        return {'qualifiedName': q_name, 'guid': guid}
        elif element_type in COMPONENT_NAME_LABELS:
            components = egeria_client.list_solution_components()
            if components == NO_ELEMENTS_FOUND:
                return None
            for component in components:
                if component.get('displayName', '').lower() == element_name.lower():
                    q_name = component.get('qualifiedName', None)
                    guid = component.get('guid', None)
                    if q_name and guid:
                        update_element_dictionary(q_name, {'guid': guid, 'display_name': element_name})
                        return {'qualifiedName': q_name, 'guid': guid}
    except Exception as e:
        msg = f"Error getting {element_type} {element_name}: {e}"
        print_msg("ERROR", msg, debug_level)
        return None

    return None


def update_a_command(txt: str, command: str, obj_type: str, q_name: str, u_guid: str) -> str:
    """
    Updates a command in a string.

    Args:
        txt: The input string.
        command: The command to update.
        obj_type: The type of object to update.
        q_name: The qualified name of the object.
        u_guid: The GUID of the object.

    Returns:
        The updated string.
    """
    # Split the command into action and object
    parts = command.split()
    action = parts[0]
    
    # Determine the new action
    new_action = "Update" if action == "Create" else "Create"
    
    # Replace the command
    new_command = f"{new_action} {obj_type}"
    pattern = rf"#{command}(?:##|\n|$)"
    replacement = f"#{new_command}\n"
    updated_txt = re.sub(pattern, replacement, txt)
    
    # Add qualified name and GUID if updating
    if new_action == "Update" and q_name and u_guid:
        # Check if Qualified Name section exists
        if "## Qualified Name" not in updated_txt:
            # Add Qualified Name section before the first ## that's not part of the command
            pattern = r"(##\s+[^#\n]+)"
            replacement = f"## Qualified Name\n{q_name}\n\n\\1"
            updated_txt = re.sub(pattern, replacement, updated_txt, count=1)
        
        # Check if GUID section exists
        if "## GUID" not in updated_txt and "## guid" not in updated_txt:
            # Add GUID section before the first ## that's not part of the command or Qualified Name
            pattern = r"(##\s+(?!Qualified Name)[^#\n]+)"
            replacement = f"## GUID\n{u_guid}\n\n\\1"
            updated_txt = re.sub(pattern, replacement, updated_txt, count=1)
    
    return updated_txt