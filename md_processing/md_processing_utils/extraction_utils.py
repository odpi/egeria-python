"""
This file contains functions for extracting data from text for Egeria Markdown processing
"""
import re
from typing import Any

from md_processing.md_processing_utils.common_md_utils import (print_msg, find_key_with_value, get_element_dictionary,
                                                               update_element_dictionary)
from md_processing.md_processing_utils.message_constants import INFO, EXISTS_REQUIRED
from md_processing.md_processing_utils.md_processing_constants import debug_level
from pyegeria._globals import NO_ELEMENTS_FOUND
from pyegeria.egeria_tech_client import EgeriaTech


def extract_command_plus(block: str) -> tuple[str, str, str] | None:
    """
    Extracts a multi-word object and its associated action from the given block of text.

    This function searches for a pattern in the format of `#...##` or `#...\n`
    inside the provided string `block`. The matched pattern is split into
    two parts: the action and the object type. The action is expected to
    be the first part, while the rest is treated as the object type. If
    no match is found, the function returns None.

    Lines beginning with '>' are ignored.

    Args:
        block: A string containing the block of text to search for the
            object_action and action.

    Returns:
        A tuple containing the object_action, the object type, and the object action if a
        match is found. Otherwise, returns None.
    """
    # Filter out lines beginning with '>'
    filtered_lines = [line for line in block.split('\n') if not line.strip().startswith('>')]
    filtered_block = '\n'.join(filtered_lines)

    match = re.search(r"#(.*?)(?:##|\n|$)", filtered_block)  # Using a non capturing group
    if match:
        clean_match = match.group(1).strip()
        if ' ' in clean_match:
            parts = clean_match.split(' ')
            object_action = parts[0].strip()
            # Join the rest of the parts to allow object_type to be one or two words
            object_type = ' '.join(parts[1:]).strip()
        else:
            object_type = clean_match.split(' ')[1].strip()
            object_action = clean_match.split(' ')[0].strip()

        return clean_match, object_type, object_action
    return None


def extract_command(block: str) -> str | None:
    """
    Extracts a object_action from a block of text that is contained between a single hash ('#') and
    either a double hash ('##'), a newline character, or the end of the string.

    The function searches for a specific pattern within the block of text and extracts the
    content that appears immediately after a single hash ('#'). Ensures that the extracted
    content is appropriately trimmed of leading or trailing whitespace, if present.

    Args:
        block: A string representing the block of text to process. Contains the content
            in which the object_action and delimiters are expected to be present.

    Returns:
        The extracted object_action as a string if a match is found, otherwise None.
    """
    match = re.search(r"#(.*?)(?:##|\n|$)", block)  # Using a non-capturing group
    if match:
        return match.group(1).strip()
    return None


def extract_attribute(text: str, labels: set) -> str | None:
    """
        Extracts the attribute value from a string.

        Args:
            text: The input string.
            labels: List of equivalent labels to search for

        Returns:
            The value of the attribute, or None if not found.

        Note:
            Lines beginning with '>' are ignored.
        """
    # Iterate over the list of labels
    for label in labels:
        # Construct pattern for the current label
        # text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'\n\n+', '\n\n', text).strip()

        label = label.strip()
        pattern = rf"##\s*{re.escape(label)}\s*\n(?:\s*\n)*?(.*?)(?:#|___|$)"

        # pattern = rf"##\s+{re.escape(label)}\n(.*?)(?:#|___|$)"  # modified from --- to enable embedded tables
        match = re.search(pattern, text, re.DOTALL)
        if match:
            # Extract matched text
            matched_text = match.group(1)

            # Filter out lines beginning with '>'
            filtered_lines = [line for line in matched_text.split('\n') if not line.strip().startswith('>')]
            filtered_text = '\n'.join(filtered_lines)

            # Replace consecutive \n with a single \n
            extracted_text = re.sub(r'\n+', '\n', filtered_text)
            if not extracted_text.isspace() and extracted_text:
                return extracted_text.strip()  # Return the cleaned text - I removed the title casing

    return None


def process_simple_attribute(txt: str, labels: set, if_missing: str = INFO) -> str | None:
    """Process a simple attribute based on the provided labels and if_missing value.
       Extract the attribute value from the text and return it if it exists.
       If it doesn`t exist, return None and print an error message with severity of if_missing.

       Parameters:
       ----------
       txt: str
         The block of object_action text to extract attributes from.
       labels: list
         The possible attribute labels to search for. The first label will be used in messages.
       if_missing: str, default is INFO
         Can be one of "WARNING", "ERROR", "INFO". The severity of the missing attribute.
    """
    if if_missing not in ["WARNING", "ERROR", "INFO"]:
        print_msg("ERROR", "Invalid severity for missing attribute", debug_level)
        return None

    attribute = extract_attribute(txt, labels)

    if attribute is None:
        if if_missing == INFO:
            msg = f"Optional attribute with labels `{labels}` missing"
        else:
            msg = f"Missing attribute with labels `{labels}` "
        print_msg(if_missing, msg, debug_level)
        return None
    return attribute


# def process_simple_attribute(txt: str, labels: list[str], if_missing: str = INFO) -> str | None:
#     """
#     Processes a simple attribute from a string.
#
#     Args:
#         txt: The input string.
#         labels: List of equivalent labels to search for
#         if_missing: The message level to use if the attribute is missing.
#
#     Returns:
#         The value of the attribute, or None if not found.
#     """
#     from md_processing.md_processing_utils.common_utils import debug_level, print_msg
#
#     attribute = extract_attribute(txt, labels)
#     if attribute is None and if_missing:
#         msg = f"No {labels[0]} found"
#         print_msg(if_missing, msg, debug_level)
#     return attribute


def process_name_list(egeria_client: EgeriaTech, element_type: str, txt: str, element_labels: set) -> tuple[str,
list[Any], bool | Any, bool | None | Any] | None:
    """
    Processes a list of names specified in the given text, retrieves details for each
    element based on the provided type, and generates a list of valid qualified names.

    The function reads a text block, extracts a list of element names according to the specified
    element type, looks them up using the provided Egeria client, and classifies them as valid or
    invalid. It returns the processed names, a list of qualified names, and validity and existence
    flags.

    Args:

        egeria_client (EgeriaTech): The client instance to connect and query elements from an
            external system.
        Element_type (str): The type of element, such as schema or attribute, to process.
        Txt (str): The raw input text containing element names to be processed.
        element_labels: a list of equivalent label names to use in processing the element.

    Returns:
        tuple[str | None, list | None, bool, bool]: A tuple containing:
            - Concatenated valid input names as a single string (or None if empty).
            - A list of known qualified names extracted from the processed elements.
            - A boolean indicating whether all elements are valid.
            - A boolean indicating whether all elements exist.
    """
    valid = True
    exists = True
    elements = ""
    new_element_list = []

    elements_txt = extract_attribute(txt, element_labels)

    if elements_txt is None:
        msg = f"No {element_type} found"
        print_msg("DEBUG-INFO", msg, debug_level)

    else:
        element_list = re.split(r'[,\n]+', elements_txt)

        for element in element_list:
            element_el = element.strip()

            # Get the element using the generalized function
            known_q_name, known_guid, el_valid, el_exists = get_element_by_name(egeria_client, element_type, element_el)
            # print_msg("DEBUG-INFO", status_msg, debug_level)

            if el_exists and el_valid:
                elements = f"{element_el} {elements}"  # list of the input names
                new_element_list.append(known_q_name)  # list of qualified names
            elif not el_exists:
                msg = f"No {element_type} `{element_el}` found"
                print_msg("DEBUG-INFO", msg, debug_level)
                valid = False
            valid = valid if el_valid is None else (valid and el_valid)
            exists = exists and el_exists

        if elements:
            # elements += "\n"
            msg = f"Found {element_type}: {elements}"
            print_msg("DEBUG-INFO", msg, debug_level)
        else:
            msg = " Name list contains one or more invalid qualified names."
            print_msg("DEBUG-INFO", msg, debug_level)
        return elements, new_element_list, valid, exists


# def process_name_list(egeria_client, element_type: str, txt: str, element_labels: list[str]) -> tuple[list, list,
# bool, bool]:
#     """
#     Processes a list of names from a string.
#
#     Args:
#         egeria_client: The Egeria client to use for validation.
#         element_type: The type of element to process.
#         txt: The input string.
#         element_labels: List of equivalent labels to search for
#
#     Returns:
#         A tuple containing:
#         - A list of element names
#         - A list of element qualified names
#         - A boolean indicating if all elements are valid
#         - A boolean indicating if any elements exist
#     """
#     from md_processing.md_processing_utils.common_utils import debug_level, print_msg
#
#     element_names = []
#     element_q_names = []
#     all_valid = True
#     any_exist = False
#
#     # Get the list of element names
#     element_list = process_simple_attribute(txt, element_labels)
#     if element_list:
#         # Split the list by commas or newlines
#         element_names = list(filter(None, re.split(r'[,\n]+', element_list.strip())))
#
#         # Validate each element
#         for element_name in element_names:
#             element_name = element_name.strip()
#             if element_name:
#                 element = get_element_by_name(egeria_client, element_type, element_name)
#                 if element:
#                     any_exist = True
#                     element_q_name = element.get('qualifiedName', None)
#                     if element_q_name:
#                         element_q_names.append(element_q_name)
#                     else:
#                         all_valid = False
#                         msg = f"Element {element_name} has no qualified name"
#                         print_msg("ERROR", msg, debug_level)
#                 else:
#                     all_valid = False
#                     msg = f"Element {element_name} not found"
#                     print_msg("ERROR", msg, debug_level)
#
#     return element_names, element_q_names, all_valid, any_exist

def process_element_identifiers(egeria_client: EgeriaTech, element_type: str, element_labels: set, txt: str,
                                action: str, version: str = None) -> tuple[str, str, bool, bool]:
    """
    Processes element identifiers by extracting display name and qualified name from the input text,
    checking if the element exists in Egeria and validating the information.

    Parameters
    ----------
    egeria_client: EgeriaTech
        Client object for interacting with Egeria.
    element_type: str
        type of element to process (e.g., 'blueprint', 'category', 'term')
    element_labels: a list of equivalent label names to use in processing the element.
    txt: str
        A string representing the input text to be processed for extracting element identifiers.
    action: str
        The action object_action to be executed (e.g., 'Create', 'Update', 'Display', ...)
    version: str, optional = None
        An optional version identifier used if we need to construct the qualified name

    Returns: tuple[str, str, str, bool, bool]
        A tuple containing:
        - qualified_name: Empty string or element identifier
        - guid: Empty string or additional element information
        - Valid: Boolean indicating if the element information is valid
        - Exists: Boolean indicating if the element exists in Egeria
    """
    valid = True

    element_name = extract_attribute(txt, element_labels)
    qualified_name = extract_attribute(txt, ["Qualified Name"])

    if qualified_name:
        q_name, guid, unique, exists = get_element_by_name(egeria_client, element_type,
                                                           qualified_name)  # Qualified name could be different if it
        # is being updated
    else:
        q_name, guid, unique, exists = get_element_by_name(egeria_client, element_type, element_name)
    if unique is False:
        msg = f"Multiple elements named  {element_name} found"
        print_msg("DEBUG-ERROR", msg, debug_level)
        valid = False

    if action == "Update" and not exists:
        msg = f"Element {element_name} does not exist"
        print_msg("DEBUG-ERROR", msg, debug_level)
        valid = False

    elif action == "Update" and exists:
        msg = f"Element {element_name} exists"
        print_msg("DEBUG-INFO", msg, debug_level)

    elif action == "Create" and exists:
        msg = f"Element {element_name} already exists"
        print_msg("DEBUG-ERROR", msg, debug_level)
        valid = False

    elif action == "Create" and not exists:
        msg = f"{element_type} `{element_name}` does not exist"
        print_msg("DEBUG-INFO", msg, debug_level)

        if q_name is None and qualified_name is None:
            q_name = egeria_client.__create_qualified_name__(element_type, element_name, version_identifier=version)
            update_element_dictionary(q_name, {'display_name': element_name})
        elif qualified_name:
            update_element_dictionary(qualified_name, {'display_name': element_name})
    elif action == EXISTS_REQUIRED:
        if not exists:
            msg = f"Required {element_type} `{element_name}` does not exist"
            print_msg("DEBUG-ERROR", msg, debug_level)
            valid = False
        else:
            msg = f"Required {element_type} `{element_name}` exists"
            print_msg("DEBUG-INFO", msg, debug_level)
            valid = True

    return q_name, guid, valid, exists


def get_element_by_name(egeria_client, element_type: str, element_name: str) -> tuple[
    str | None, str | None, bool | None, bool | None]:
    """
    Generalized function to retrieve an element by name based on its type.

    Parameters:
    egeria_client: Client
        Client object for interacting with Egeria.
    element_type: str
        The type of element to retrieve (e.g., 'blueprint', 'category', 'term').
    element_name: str
        The name of the element to retrieve.

    Returns:
        tuple of qualified_name, guid, uniqye, exists
    """
    unique = None

    element_dict = get_element_dictionary()
    q_name = find_key_with_value(element_name)
    if q_name:  # use information from element_dictionary
        guid = element_dict[q_name].get('guid', None)
        unique = True

        if guid is not None:  # Found complete entry in element_dictionary
            msg = f'Found {element_type} qualified name and guid in element_dictionary for `{element_name}`'
            print_msg("DEBUG-INFO", msg, debug_level)
            exists = True
            return q_name, guid, unique, exists

        else:  # Missing guid from element_dictionary
            guid = egeria_client.get_element_guid_by_unique_name(element_name)
            if guid == NO_ELEMENTS_FOUND:
                guid = None
                exists = False
                msg = f"No {element_type} guid found with name {element_name} in Egeria"
                print_msg("DEBUG-INFO", msg, debug_level)

                return q_name, guid, unique, exists
            else:
                exists = True
                update_element_dictionary(q_name, {'guid': guid})
                msg = f"Found guid value of {guid} for  {element_name} in Egeria"
                print_msg("DEBUG-INFO", msg, debug_level)

                return q_name, guid, unique, exists

    # Haven't seen this element before
    property_names = ['qualifiedName', 'name', 'displayName', 'title']
    open_metadata_type_name = None
    details = egeria_client.get_elements_by_property_value(element_name, property_names, open_metadata_type_name)
    if isinstance(details, str):
        msg = f"{element_type} `{element_name}` not found in Egeria"
        print_msg("DEBUG-INFO", msg, debug_level)
        exists = False
        return None, None, unique, exists
    if len(details) > 1:
        msg = (f"More than one element with name {element_name} found, please specify a "
               f"**Qualified Name**")
        print_msg("DEBUG-ERROR", msg, debug_level)
        unique = False
        exists = None
        return element_name, None, unique, exists

    el_qname = details[0]["properties"].get('qualifiedName', None)
    el_guid = details[0]['elementHeader']['guid']
    el_display_name = details[0]["properties"].get('displayName', None)
    if el_display_name is None:
        el_display_name = details[0]["properties"].get('name', None)
    update_element_dictionary(el_qname, {
        'guid': el_guid, 'displayName': el_display_name
        })
    msg = f"Found {element_type} `{el_display_name}` with qualified name `{el_qname}`"
    print_msg("DEBUG-INFO", msg, debug_level)
    exists = True
    unique = True
    return el_qname, el_guid, unique, exists


def update_a_command(txt: str, object_action: str, obj_type: str, q_name: str, u_guid: str) -> str:
    """
    Updates a command in a string.

    Args:
        txt: The input string.
        object_action: The command to update.
        obj_type: The type of object to update.
        q_name: The qualified name of the object.
        u_guid: The GUID of the object.

    Returns:
        The updated string.
    """

    # Determine the new action
    new_action = "Update" if object_action == "Create" else "Create"

    # Replace the object_action
    new_command = f"{new_action} {obj_type}"
    pattern = rf"#\s*{object_action}\s+{obj_type}"
    replacement = f"# {new_command}"
    updated_txt = re.sub(pattern, replacement, txt)

    # Add qualified name and GUID if updating
    if new_action == "Update" and q_name and u_guid:
        # Check if Qualified Name section exists
        if "## Qualified Name" not in updated_txt:
            # Add Qualified Name section before the first ## that's not part of the object_action
            pattern = r"(##\s+[^#\n]+)"
            replacement = f"## Qualified Name\n{q_name}\n\n\\1"
            updated_txt = re.sub(pattern, replacement, updated_txt, count=1)

        # Check if GUID section exists
        if "## GUID" not in updated_txt and "## guid" not in updated_txt:
            # Add GUID section before the first ## that's not part of the object_action or Qualified Name
            pattern = r"(##\s+(?!Qualified Name)[^#\n]+)"
            replacement = f"## GUID\n{u_guid}\n\n\\1"
            updated_txt = re.sub(pattern, replacement, updated_txt, count=1)

    return updated_txt
