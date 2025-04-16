"""

This file contains functions to parse and process Egeria Markdown (Freddie)


"""

import os
import re
import sys
from datetime import datetime
from typing import List, Optional

from rich import print
from rich.console import Console
from rich.markdown import Markdown

from pyegeria import body_slimmer
from pyegeria._globals import (NO_GLOSSARIES_FOUND, NO_ELEMENTS_FOUND, NO_PROJECTS_FOUND, \
                               NO_CATEGORIES_FOUND)
from pyegeria.dr_egeria_state import get_element_dictionary, update_element_dictionary, find_key_with_value
from pyegeria.egeria_tech_client import EgeriaTech
# from pyegeria.md_processing_helpers import process_q_name_list
from pyegeria.project_manager_omvs import ProjectManager

EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "170"))
console = Console(width=EGERIA_WIDTH)

command_list = ["Provenance", "Create Glossary", "Update Glossary", "Create Term", "Update Term", "List Terms",
                "List Glossary Terms", "List Term History", "Term Journal Report", "List Glossary Structure",
                "List Glossaries", "List Categories", "List Glossary Categories",
                "Create Personal Project", "Update Personal Project", "Create Category",
                "Update Category", "Create Solution Blueprint", "Update Solution Blueprint",
                "Create Solution Component", "Update Solution Component", "Set Parent Category",
                "UnSet Parent Category", "Unset Parent Category"]
# verbosity - verbose, quiet, debug
debug_level = "debug"
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

GLOSSARY_NAME_LABELS = ["Glossary Name", "Glossary", "Glossaries", "Owning Glossary", "In Glossary"]
CATEGORY_NAME_LABELS = ["Glossary Category Name", "Glossary Category", "Glossary Categories", "Category Name",
                        "Category", "Categories"]
PARENT_CATEGORY_LABELS = ["Parent Category Name", "Parent Category", "parent category name", "parent category"]
CHILD_CATEGORY_LABELS = ["Child Category Name", "Child Category", "child category name", "child category"]
TERM_NAME_LABELS = ["Glossary Term Name", "Glossary Term", "Glossary Terms", "Term Name", "Term", "Terms", "Term Names"]
PROJECT_NAME_LABELS = ["Project Name", "Project", "Project Names", "Projects"]
BLUEPRINT_NAME_LABELS = ["Solution Blueprint Name", "Solution Blueprint", "Solution Blueprints", "Blueprint Name",
                         "Blueprint", "Blueprints"]
COMPONENT_NAME_LABELS = ["Solution Component Name", "Solution Component", "Solution Components", "Component Name",
                         "Component", "Components", "Parent Components", "Parent Component"]
SOLUTION_ROLE_LABELS = ["Solution Role Name", "Solution Role", "Solution Roles", "Role Name", "Role", "Roles"]
SOLUTION_ACTOR_ROLE_LABELS = ["Solution Actor Role Name", "Solution Actor Role Names", "Solution Actor Role",
                              "Solution Actor Roles", "Actor Role Name", "Actor Role", "Actor Roles",
                              "Actor Role Names"]
SOLUTION_LINKING_ROLE_LABELS = ["Solution Linking Role Name", "Solution Linking Role Names", "Solution Linking Role",
                                "Solution Linking Roles", "Linking Role Name", "Linking Role", "Linking Roles",
                                "Linking Role Names"]
GUID_LABELS = ['GUID', 'guid']


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


def update_term_categories(egeria_client: EgeriaTech, term_guid: str, categories_exist: bool,
                           categories_list: List[str]) -> None:
    """

    Adds or removes a term to/from specified categories in a glossary.

    This function associates a term, identified by its GUID, with one or more
    categories. It uses the provided EgeriaTech client to assign the term
    to the categories. If the GUID of a category is not readily available, it
    is retrieved either from a pre-loaded dictionary or through a client lookup.

    Args:
        egeria_client (EgeriaTech): The client to interact with the glossary.
        term_guid (str): The GUID of the term to be associated with categories.
        categories_exist (bool): Flag indicating whether the categories already
                                 exist.
        categories_list (List[str]): A list of category names to associate with
                                     the term.

    Returns:
        None
    """
    to_be_cat_guids: list[str] = []
    # find the categories a term is currently in.
    existing_categories = egeria_client.get_categories_for_term(term_guid)
    if type(existing_categories) is str:
        current_categories = []
    else:
        current_categories = [cat['elementHeader']['guid'] for cat in existing_categories]

    if categories_exist is True and categories_list is not None:
        if type(categories_list) is str:
            categories_list = categories_list.split(",").trim()
        for category in categories_list:
            cat_guid = None
            cat_el = category.strip()
            element_dict = get_element_dictionary()
            if cat_el in element_dict:
                cat = element_dict.get(cat_el, None)
                cat_guid = cat.get('guid', None) if cat else None
            if cat_guid is None:
                cat_guid = egeria_client.__get_guid__(qualified_name=cat_el)
                update_element_dictionary(cat_el, {'guid': cat_guid})
            to_be_cat_guids.append(cat_guid)

        for cat in to_be_cat_guids:
            if cat not in current_categories:
                egeria_client.add_term_to_category(term_guid, cat)
                current_categories.append(cat)
                msg = f"Added term {term_guid} to category {cat}"
                print_msg("DEBUG-INFO", msg, debug_level)

        for cat in current_categories:
            if cat not in to_be_cat_guids:
                egeria_client.remove_term_from_category(term_guid, cat)
                msg = f"Removed term {term_guid} from category {cat}"
                print_msg("DEBUG-INFO", msg, debug_level)
    else: # No categories specified - so remove any categories a term is in
        for cat in current_categories:
            egeria_client.remove_term_from_category(term_guid, cat)
            msg = f"Removed term {term_guid} from category {cat}"
            print_msg("DEBUG-INFO", msg, debug_level)

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
            command and action.

    Returns:
        A tuple containing the command, the object type and the object action if a
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
    Extracts a command from a block of text that is contained between a single hash ('#') and
    either a double hash ('##'), a newline character, or the end of the string.

    The function searches for a specific pattern within the block of text and extracts the
    content that appears immediately after a single hash ('#'). Ensures that the extracted
    content is appropriately trimmed of leading or trailing whitespace, if present.

    Args:
        block: A string representing the block of text to process. Contains the content
            in which the command and delimiters are expected to be present.

    Returns:
        The extracted command as a string if a match is found, otherwise None.
    """
    match = re.search(r"#(.*?)(?:##|\n|$)", block)  # Using a non capturing group
    if match:
        return match.group(1).strip()
    return None


def extract_attribute(text: str, labels: [str]) -> str | None:
    """
        Extracts the attribute value from a string.

        Args:
            text: The input string.
            labels: List of equivalent labels to search for

        Returns:
            The glossary name, or None if not found.

        Note:
            Lines beginning with '>' are ignored.
        """
    # Iterate over the list of labels
    for label in labels:
        # Construct pattern for the current label
        pattern = rf"## {re.escape(label)}\n(.*?)(?:#|___|>|$)"  # modified from --- to enable embedded tables
        match = re.search(pattern, text, re.DOTALL)
        if match:
            # Extract matched text
            matched_text = match.group(1).strip()

            # Filter out lines beginning with '>'
            filtered_lines = [line for line in matched_text.split('\n') if not line.strip().startswith('>')]
            filtered_text = '\n'.join(filtered_lines)

            # Replace consecutive \n with a single \n
            extracted_text = re.sub(r'\n+', '\n', filtered_text)
            if not extracted_text.isspace() and extracted_text:
                return extracted_text  # Return the cleaned text - I removed the title casing


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
    msg_level = msg_level.upper()
    record = f"{message_types[msg_level]} {msg}"
    if msg_level in ("WARNING", "ERROR", "INFO"):
        record = f"* {record}"

    match verbosity.lower():
        case "verbose":
            if msg_level in ("WARNING", "ERROR", "INFO", "ALWAYS"):
                print(record)
        case "quiet":
            if msg_level in ("WARNING", "ERROR", "ALWAYS"):
                print(record)
        case "debug":
            print(record)
        case "display-only":
            pass
        case _:
            print("Invalid verbosity level - exiting\n")
            sys.exit(1)


def process_simple_attribute(txt: str, labels: [str], if_missing: str = INFO) -> str | None:
    """Process a simple attribute based on the provided labels and if_missing value.
       Extract the attribute value from the text and return it if it exists.
       If it doesn`t exist, return None and print an error message with severity of if_missing.

       Parameters:
       ----------
       txt: str
         The block of command text to extract attributes from.
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
            msg = f"Optional attribute {labels[0]} missing"
        else:
            msg = f"Missing {labels[0]} attribute"
        print_msg(if_missing, msg, debug_level)
        return None
    return attribute


def update_a_command(txt: str, command: str, obj_type: str, q_name: str, u_guid: str) -> str:
    """
    Updates a command by modifying the input text with corresponding actions, GUID, and qualified name.
    The function processes the provided command based on the given parameters, updating the relevant
    sections in the text, including command actions, GUID, qualified name, and optionally the status
    of the attributes. It ensures that proper formatting and necessary fields are present in the text.

    Args:
        txt (str): The input text containing the content to be updated.
        command (str): The command to be processed (e.g., "Create Term", "Update Term").
        obj_type (str): The object type related to the command (e.g., "Term", "Category").
        q_name (str): The qualified name to be added or updated in the text.
        u_guid (str): The unique identifier (GUID) to be added or updated in the text. If not provided,
            it defaults to an empty string.

    Returns:
        str: The updated text containing the modifications based on the provided command.

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

    status = extract_attribute(txt, ["Status"])
    if command in ["Create Term", "Update Term"] and status is None:
        pattern = r"(## Status\s*\n)(.*?)(#)"
        replacement = r"\1\n DRAFT\n\n\3"
        txt = re.sub(pattern, replacement, txt)
    return txt


def process_provenance_command(file_path: str, txt: [str]) -> str:
    """This commands processes a provenence command by pre-pending the current file name and time to the provenance
    output"""
    output = (f"* Derived from processing file {file_path} on "
              f"{get_current_datetime_string()}\n")
    pattern = rf"# {re.escape('Provenance')}\n(.*?)(?:#|---|$)"
    match = re.search(pattern, txt, re.DOTALL)
    if match:
        # Extract matched text and replace consecutive \n with a single \n
        extracted_text = re.sub(r'\n+', '\n', match.group(1).strip())
        if not extracted_text.isspace() and extracted_text:
            existing_prov = extracted_text  # Return the cleaned text
        else:
            existing_prov = None
    # print(f"txt is: {txt}, existing_prov: {existing_prov}")
    existing_prov = existing_prov if existing_prov else " "
    return f"\n# Provenance:\n{existing_prov}\n{output}\n"


def process_element_identifiers(egeria_client: EgeriaTech, element_type: str, element_labels: [str], txt: str,
                                action: str, version: str = None) -> tuple[str, str, bool, bool]:
    """
    Processes element identifiers by extracting display name and qualified name from the input text,
    checking if the element exists in Egeria, and validating the information.

    Parameters:
        element_labels:
    egeria_client: EgeriaTech
        Client object for interacting with Egeria.
    element_type: str
        type of element to process (e.g., 'blueprint', 'category', 'term')
    element_labels: a list of equivalent label names to use in processing the element.
    txt: str
        A string representing the input text to be processed for extracting element identifiers.
    action: str
        The action command to be executed (e.g., 'Create', 'Update', 'Display', ...)
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
    elif action == "Exists Required":
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
        exists = True
        if guid is not None:  # Found complete entry in element_dictionary
            msg = f'Found {element_type} qualified name and guid in element_dictionary for `{element_name}`'
            print_msg("DEBUG-INFO", msg, debug_level)
            return q_name, guid, unique, exists

        else:  # Missing guid from element_dictionary
            guid = egeria_client.get_element_guid_by_unique_name(element_name)
            if guid == NO_ELEMENTS_FOUND:
                guid = None
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
    property_names = ['qualifiedName', 'name', 'displayName']
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
    update_element_dictionary(el_qname, {
        'guid': el_guid, 'displayName': el_display_name
        })
    msg = f"Found {element_type} `{el_display_name}` with qualified name `{el_qname}`"
    print_msg("DEBUG-INFO", msg, debug_level)
    exists = True
    unique = True
    return el_qname, el_guid, unique, exists

    # Convert element_type to plural form for method name construction  # if element_type.endswith('y'):  #  #
    # plural_type = f"{element_type[:-1]}ies"  # elif element_type.endswith('s'):  #     plural_type = f"{  #
    # element_type}es"  # else:  #     plural_type = f"{element_type}s"  #  # # Construct method name  # method_name
    # = f"get_{plural_type}_by_name"  #  # # Check if the method exists on the client  # if hasattr(egeria_client,
    # method_name):  #     # Call the method  #     method = getattr(egeria_client, method_name)  #     result =  #
    # method(element_name)  #     return result  # else:  #     # Method doesn't exist  #     return f"Method {  #
    # method_name} not found on client"


def process_q_name_list(egeria_client: EgeriaTech, element_type: str, txt: str, element_labels: [str]) -> tuple[
    str | None, list | None, bool, bool]:
    """
    Processes a list of qualified names specified in the given text, retrieves details for each
    element based on the provided type, and generates a list of valid qualified names.

    The function reads a text block, extracts a list of element names according to the specified
    element type, looks them up using the provided Egeria client, and classifies them as valid or
    invalid. It returns the processed names, a list of qualified names, and validity and existence
    flags.

    Args:

        egeria_client (EgeriaTech): The client instance to connect and query elements from an
            external system.
        element_type (str): The type of element, such as schema or attribute, to process.
        txt (str): The raw input text containing element names to be processed.
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
            msg = f" Name list contains one or more invalid qualified names."
            print_msg("DEBUG-INFO", msg, debug_level)
        return elements, new_element_list, valid, exists


def process_blueprint_upsert_command(egeria_client: EgeriaTech, element_dictionary: dict, txt: str,
                                     directive: str = "display") -> Optional[str]:
    """
    Processes a blueprint create or update command by extracting key attributes such as
    blueprint name, description, and version from the given cell.

    Parameters:
    egeria_client: SolutionArchitect
        Client object for interacting with Egeria.
    txt: str
        A string representing the input cell to be processed for
        extracting element attributes.
    directive: str, optional, default "display"
        An optional string indicating the directive to be used - display, validate or execute

    Returns: str
        A string summarizing the outcome of the processing.
    """
    command, object_type, object_action = extract_command_plus(txt)
    set_debug_level(directive)
    display_name = process_simple_attribute(txt, ['Display Name', 'Blueprint Name'], ERROR)
    description = process_simple_attribute(txt, ['Description'])
    version = process_simple_attribute(txt, ['Version', "Version Identifier", "Published Version"])

    print(
        Markdown(f"{pre_command} {object_action} `{object_type}` for Blueprint: `\'{display_name}\'` with directive: `"
                 f"{directive}`\n"))
    if display_name is None:
        valid = False
        q_name, known_guid, exists = None
    else:
        element_labels = BLUEPRINT_NAME_LABELS
        element_labels.append('Display Name')
        q_name, known_guid, valid, exists = process_element_identifiers(egeria_client, object_type, element_labels, txt,
                                                                        object_action, version)

    element_display = (f"\n* Command: {object_action} {object_type}\n\t* Blueprint: {display_name}\n\t"
                       f"* Description: {description}\n\t"
                       f"* Version: {version}\n\t* Qualified Name:{q_name}\n\t* GUID: {known_guid} "
                       # f"\n\t* Update Description: {update_description}\n"
                       )

    if valid:
        msg = f"\n-->It is valid to **{object_action}** element \'{display_name}\'\n"
        print_msg("ALWAYS", msg, debug_level)
    if directive == "display":
        print(Markdown(element_display))
        return None
    elif directive == "validate":
        print(Markdown(element_display))
        return valid

    elif directive == "process":
        print(Markdown(element_display))
        try:
            if not valid:  # First validate the element before we process it
                msg = "\nInvalid input found - please review the errors and warnings above\n"
                print_msg("ERROR", msg, debug_level)
                return None

            if object_action == "Update" and directive == "process":
                if not exists:
                    msg = f"\n-->Update failed - Blueprint {display_name} does not exist"
                    print_msg("ERROR", msg, debug_level)
                    return None

                # call update blueprint here

                msg = f"\nUpdated Blueprint `{display_name}` with GUID {known_guid}"
                print_msg("ALWAYS", msg, debug_level)

                # update with get blueprint by guid
                return 'Would return get blueprint by guid and return md'  # egeria_client.get_terms_by_guid(  #
                # known_guid, 'md')

            elif object_action == "Update" and directive == "validate":
                return 'Would call get_blueprint_by_guid and return md'  # egeria_client.get_terms_by_guid(  #
                # known_guid, 'md')

            elif object_action == "Create":
                if exists:
                    msg = f"\n{WARNING}Blueprint {display_name} exists and result document updated"
                    print_msg("WARNING", msg, debug_level)
                    return update_a_command(txt, f"{object_type}{object_action}", object_type, q_name, known_guid)
                else:
                    # create the blueprint
                    # term_guid = egeria_client.create_controlled_glossary_term(glossary_guid, term_body)
                    # if term_guid == NO_ELEMENTS_FOUND:
                    #     print(f"{ERROR}Term {term_name} not created")
                    #     return None
                    new_guid = f"guid:{get_current_datetime_string()}"
                    msg = f"\nCreated Blueprint `{display_name}`with GUID {new_guid}"
                    print_msg("ALWAYS", msg, debug_level)

                    update_element_dictionary(q_name, {'guid': new_guid, 'display_name': display_name})
                    return 'Would return get blueprint by guid results as md'  # egeria_client.get_terms_by_guid(  #
                    # term_guid, 'MD')

        except Exception as e:
            msg = f"{ERROR}Error creating term {display_name}: {e}"
            print_msg("ERROR", msg, debug_level)
            console.print_exception(show_locals=True)
            return None


def process_solution_component_upsert_command(egeria_client: EgeriaTech, element_dictionary: dict, txt: str,
                                              directive: str = "display") -> Optional[str]:
    """
    Processes a solution componentt create or update command by extracting key attributes such as
    solution component name, description, version, solution component type etc from the given cell.

    Parameters:
    egeria_client: SolutionArchitect
        Client object for interacting with Egeria.
    txt: str
        A string representing the input cell to be processed for
        extracting element attributes.
    directive: str, optional, default "display"
        An optional string indicating the directive to be used - display, validate or execute

    Returns: str
        A string summarizing the outcome of the processing.
    """
    set_debug_level(directive)
    bp_qname_list = []
    command, object_type, object_action = extract_command_plus(txt)

    display_name = process_simple_attribute(txt, ['Display Name', 'Solution Component Name'], ERROR)
    description = process_simple_attribute(txt, ['Description'])
    version = process_simple_attribute(txt, ['Version', "Version Identifier", "Published Version"])
    solution_component_type = process_simple_attribute(txt, ['Solution Component Type'])
    planned_deployed_implementation_type = process_simple_attribute(txt, ['Planned Deployment Implementation Type'])
    solution_blueprints = process_simple_attribute(txt, ['Solution Blueprints'])
    parent_components = process_simple_attribute(txt, ['Parent Components'])

    print(Markdown(
        f"{pre_command}  {object_action} `{object_type}` for Solution Component: `\'{display_name}\'` with directive: "
        f"`{directive}`\n"))

    if display_name is None:
        valid = False
        q_name, known_guid, exists = None
    else:
        element_labels = COMPONENT_NAME_LABELS
        element_labels.append('Display Name')
        known_q_name, known_guid, valid, exists = process_element_identifiers(egeria_client, object_type,
                                                                              element_labels, txt, object_action,
                                                                              version)

    if solution_blueprints:  # Find information about blueprints that include this component
        msg = "Checking for blueprints that include this solution component"
        print_msg("DEBUG-INFO", msg, debug_level)
        solution_blueprints, bp_qname_list, bp_valid, bp_exist = process_q_name_list(egeria_client,
                                                                                     'Solution Blueprints', txt,
                                                                                     BLUEPRINT_NAME_LABELS)
        if bp_exist and bp_valid:
            msg = f"Found valid blueprints that include this solution component:\n\t{solution_blueprints}"
            print_msg("INFO", msg, debug_level)
        else:
            msg = f"No valid blueprints that include this solution component found."
            print_msg("INFO", msg, debug_level)
    if parent_components is None:
        msg = f"Parent Components are missing"
        print_msg("INFO", msg, debug_level)
    else:
        parent_components, parent_qname_list, parents_valid, parent_components_exist = process_q_name_list(
            egeria_client, 'Parent Components', txt, COMPONENT_NAME_LABELS)
        if parent_components_exist and parents_valid:
            msg = f"Found valid parent components that include this solution component:\n\t{parent_qname_list}"
            print_msg("INFO", msg, debug_level)
        else:
            msg = f"No valid parent components that include this solution component found."
            print_msg("INFO", msg, debug_level)

    element_display = (f"* Command: {object_action} {object_type}\n\t* Display Name: {display_name}\n\t"
                       f"* Description: {description}\n\t"
                       f"* Version Identifier: {version}\n\t"
                       f"* Solution Component Type {solution_component_type}\n\t"
                       f"* Planned Deployment Implementation Type {planned_deployed_implementation_type}\n\t"
                       f"* Solution_Blueprints: {solution_blueprints}\n\t"
                       f"* Parent Components: {parent_components}\n\t"
                       f"* Qualified Name:{known_q_name}\n\t* GUID: {known_guid} "
                       # f"\n\t* Update Description: {update_description}"
                       )

    if object_action == "Update":  # check to see if provided information exists and is consistent with existing info
        if not exists:
            msg = f"Element {display_name} does not exist with input:\n"
            print_msg("ERROR", msg, debug_level)
            valid = False
        elif not valid:
            msg = (f"\n-->Validation checks failed in updating {object_type} \'{display_name}\' with: \n"
                   f"{element_display}")
            print_msg("ERROR", msg, debug_level)
        else:  # it exists and is valid
            msg = f"\n-->It is valid to update {object_type} \'{display_name}\' with: \n"
            print_msg("ALWAYS", msg, debug_level)
            if known_q_name is None:
                known_q_name = egeria_client.__create_qualified_name__(object_type, display_name,
                                                                       version_identifier=version)
            update_element_dictionary(known_q_name, {'display_name': display_name, 'guid': known_guid})

    elif object_action == 'Create':  # if the command is create, check that it doesn't already exist
        if exists:
            msg = f"{object_type} `{display_name}` already exists."
            print_msg("ERROR", msg, debug_level)
            valid = False
        elif not valid:
            msg = f"\n-->Validation checks failed in creating element \'{display_name}\' with: \n"
            print_msg("ERROR", msg, debug_level)
        else:  # valid to create - update element_dictionary
            msg = f"\n-->It is valid to create element \'{display_name}\' with: \n"
            print_msg("ALWAYS", msg, debug_level)
            if known_q_name is None:
                known_q_name = egeria_client.__create_qualified_name__(object_type, display_name,
                                                                       version_identifier=version)
            update_element_dictionary(known_q_name, {'display_name': display_name})
    print(Markdown(element_display))
    if directive == "display":
        return None
    elif directive == "validate":
        return valid

    elif directive == "process":
        try:
            if not valid:  # First validate the term before we process it
                return None

            if object_action == "Update" and directive == "process":
                if not exists:
                    msg = (f"\n-->Solution Component {display_name} does not exist")
                    print_msg("ERROR", msg, debug_level)
                    return None

                # call update solution component here

                msg = f"\nUpdated Solution Component `{display_name}` with GUID {known_guid}"
                print_msg("ALWAYS", msg, debug_level)
                # update with get solution component by guid
                return 'Would return get Solution Component by guid and return md'  #  #
                # egeria_client.get_terms_by_guid(known_guid, 'md')

            elif object_action == "Update" and directive == "validate":
                return 'Would call get_blueprint_by_guid and return md'  # egeria_client.get_terms_by_guid(  #
                # known_guid, 'md')

            elif object_action == "Create":
                if exists:
                    f"\n{WARNING}Component {display_name} exists and result document updated"
                    print_msg("WARNING", msg, debug_level)
                    return update_a_command(txt, f"{object_type}{object_action}", object_type, known_q_name, known_guid)
                else:
                    # create the solution component
                    # term_guid = egeria_client.create_controlled_glossary_term(glossary_guid, term_body)
                    # if term_guid == NO_ELEMENTS_FOUND:
                    #     print(f"{ERROR}Term {term_name} not created")
                    #     return None

                    msg = f"\nCreated Solution Component `{display_name}` with GUID {known_guid}"
                    print_msg("ALWAYS", msg, debug_level)
                    update_element_dictionary(known_q_name, {'guid': known_guid, 'display_name': display_name})
                    return 'Would return get solution component by guid results as md'  #  #
                    # egeria_client.get_terms_by_guid(term_guid, 'MD')

        except Exception as e:
            msg = f"Error creating term {display_name}: {e}"
            print_msg("ERROR", msg, debug_level)
            console.print_exception(show_locals=True)
            return None


def process_glossary_upsert_command(egeria_client: EgeriaTech, element_dictionary: dict, txt: str,
                                    directive: str = "display") -> Optional[str]:
    """
    Processes a glossary create or update command by extracting key attributes such as
    glossary name, language, description, and usage from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    # command = extract_command(txt)
    # object_type = command.split(' ')[1].strip()
    # object_action = command.split(' ')[0].strip()
    command, object_type, object_action = extract_command_plus(txt)
    set_debug_level(directive)

    glossary_name = process_simple_attribute(txt, ['Glossary Name', 'Display Name'])
    print(Markdown(
        f"{pre_command} `{object_action}` `{object_type}`  for glossary: `\'{glossary_name}\'` with directive: `"
        f"{directive}` "))
    language = process_simple_attribute(txt, ['Language'])
    description = process_simple_attribute(txt, ['Description'])
    usage = process_simple_attribute(txt, ['Usage'])
    q_name = process_simple_attribute(txt, ['Qualified Name'])

    if glossary_name is None:
        valid = False
        known_q_name, known_guid, glossary_exists = None
    else:
        element_labels = GLOSSARY_NAME_LABELS
        element_labels.append('Display Name')
        known_q_name, known_guid, valid, glossary_exists = process_element_identifiers(egeria_client, object_type,
                                                                                       element_labels, txt,
                                                                                       object_action, None)
    glossary_display = (f"\n* Command: `{command}`\n\t* Glossary Name: {glossary_name}\n\t"
                        f"* Language: {language}\n\t* Description:\n{description}\n"
                        f"* Usage: {usage}\n")

    if object_action == 'Update':
        guid = process_simple_attribute(txt, ['GUID', 'guid', 'Guid'])
        glossary_display += f"* Qualified Name: `{q_name}`\n\t* GUID: {guid}\n\n"
        if not glossary_exists:
            msg = f"Glossary can't be updated; `{glossary_name}` not found"
            print_msg("ERROR", msg, debug_level)
            valid = False
        else:
            msg = f"Glossary can be updated; `{glossary_name}` found"
            print_msg(ALWAYS, msg, debug_level)


    elif object_action == "Create":
        if glossary_exists:
            msg = f"Glossary `{glossary_name}` can't be created because it already exists.\n"
            print_msg("ERROR", msg, debug_level)
            valid = False
        elif valid:
            msg = f"It is valid to create Glossary `{glossary_name}` with:\n"
            print_msg("ALWAYS", msg, debug_level)

    if directive == "display":
        print(Markdown(glossary_display))
        return None

    elif directive == "validate":
        if valid:
            print(Markdown(glossary_display))
        else:
            msg = f"Validation failed for Glossary `{glossary_name}`\n"
            print_msg(ERROR, msg, debug_level)
            print(Markdown(glossary_display))

        return valid

    elif directive == "process":
        if valid:
            print(Markdown(glossary_display))
        else:
            msg = f"Validation failed for Glossary `{glossary_name}`\n"
            print_msg(ERROR, msg, debug_level)
            print(Markdown(glossary_display))
            return None

        if object_action == "Update":
            if not glossary_exists:
                print(
                    f"\n{ERROR}Glossary `{glossary_name}` does not exist! Updating result document with Create "
                    f"command\n")
                return update_a_command(txt, command, object_type, known_q_name, known_guid)

            body = {
                "class": "ReferenceableRequestBody", "elementProperties": {
                    "class": "GlossaryProperties", "qualifiedName": known_q_name, "description": description,
                    "language": language, "usage": usage
                    }
                }
            egeria_client.update_glossary(known_guid, body)
            print_msg(ALWAYS, f"Updated Glossary `{glossary_name}` with GUID {known_guid}", debug_level)
            update_element_dictionary(known_q_name, {
                'guid': known_guid, 'display_name': glossary_name
                })
            return egeria_client.get_glossary_by_guid(known_guid, output_format='MD')
        elif object_action == "Create":
            glossary_guid = None

            if glossary_exists:
                print(f"\nGlossary `{glossary_name}` already exists and result document updated\n")
                return update_a_command(txt, command, object_type, known_q_name, known_guid)
            else:
                glossary_guid = egeria_client.create_glossary(glossary_name, description, language, usage)
                glossary = egeria_client.get_glossary_by_guid(glossary_guid)
                if glossary == NO_GLOSSARIES_FOUND:
                    print(f"{ERROR}Just created with GUID {glossary_guid} but Glossary not found\n")
                    return None
                qualified_name = glossary['glossaryProperties']["qualifiedName"]
                update_element_dictionary(qualified_name, {
                    'guid': glossary_guid, 'display_name': glossary_name
                    })
                # return update_a_command(txt, command, object_type, qualified_name, glossary_guid)
                print_msg(ALWAYS, f"Created Glossary `{glossary_name}` with GUID {glossary_guid}", debug_level)
                return egeria_client.get_glossary_by_guid(glossary_guid, output_format='MD')


def process_categories_upsert_command(egeria_client: EgeriaTech, element_dictionary: dict, txt: str,
                                      directive: str = "display") -> Optional[str]:
    """
    Processes a glossary category create or update command by extracting key attributes such as
    category name, qualified, description, and anchor glossary from the given txt..

    :param txt: A string representing the input cell to be processed for
        extracting category-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    valid = True
    set_debug_level(directive)
    # command = extract_command(txt)
    # object_type = command.split(' ')[1].strip()
    # object_action = command.split(' ')[0].strip()
    command, object_type, object_action = extract_command_plus(txt)

    category_name = process_simple_attribute(txt, ['Category Name', 'category_name', 'Cat'])
    print(Markdown(f"{pre_command} `{command}` for category: `\'{category_name}\'` with directive: `{directive}` "))

    owning_glossary_name = extract_attribute(txt, ['Owning Glossary', 'In Glossary'])
    description = process_simple_attribute(txt, ['Description'])
    q_name = process_simple_attribute(txt, ['Qualified Name'])

    element_labels = CATEGORY_NAME_LABELS
    element_labels.append('Display Name')
    # Check if category exists (and get qname and guid)
    if category_name is None:
        valid = False
        known_q_name, known_guid, category_exists = None
    else:
        element_labels = CATEGORY_NAME_LABELS
        element_labels.append('Display Name')
        known_q_name, known_guid, valid, category_exists = process_element_identifiers(egeria_client, object_type,
                                                                                       element_labels, txt,
                                                                                       object_action, None)

    # Check if owning glossary exists (and get qname)
    if owning_glossary_name is None:
        valid = False
        known_glossary_q_name, known_glossary__guid, glossary_exists = None
    else:
        known_glossary_q_name, known_glossary_guid, valid, owning_glossary_exists = process_element_identifiers(
            egeria_client, "Glossary", GLOSSARY_NAME_LABELS, txt, "Exists Required", None)

    category_display = (
        f"\n* Command: {command}\n\t* Category: {category_name}\n\t* In Glossary: {owning_glossary_name}\n\t"
        f"* Description:\n{description}\n\t* Qualified Name: {q_name}\n\t")

    if object_action == 'Update':
        guid = process_simple_attribute(txt, ['GUID', 'guid', 'Guid'])
        # update_description = process_simple_attribute(txt, 'Update Description')
        category_display += (f"* GUID: {guid}\n\n")
        if not category_exists:
            msg = f"Category {category_name} can't be updated; {category_name} not found."
            print_msg(ERROR, msg, debug_level)
            valid = False
        else:
            msg = f"Glossary can be updated; {category_name} found"
            print_msg(ALWAYS, msg, debug_level)

    elif object_action == "Create":
        if category_exists:
            msg = f"Category {category_name} can't be created because it already exists.\n"
            print_msg("ERROR", msg, debug_level)
            valid = False
        elif valid:
            msg = f"It is valid to create Category `{category_name}` with:\n"
            print_msg("ALWAYS", msg, debug_level)

    if directive == "display":
        print(Markdown(category_display))
        return None

    elif directive == "validate":
        if valid:
            print(Markdown(category_display))
        else:
            msg = f"Validation failed for {object_type} `{category_name}`\n"
            print_msg(ERROR, msg, debug_level)
            print(Markdown(category_display))
        return valid

    elif directive == "process":
        if valid:
            print(Markdown(category_display))
        else:
            msg = f"* --> Validation failed for {object_type} `{category_name}`\n"
            print_msg(ERROR, msg, debug_level)
            print(Markdown(category_display))
            return None

        if object_action == "Update":
            if not category_exists:
                print(f"\n{ERROR}category `{category_name}` does not exist! Updating result document with Create "
                      f"command\n")
                return update_a_command(txt, command, object_type, known_q_name, known_guid)

            egeria_client.update_category(known_guid, category_name, description, known_q_name, None)
            msg = f"->Updated category `{category_name}`with GUID {known_guid}"
            print_msg(ALWAYS, msg, debug_level)
            update_element_dictionary(known_q_name, {
                'guid': known_guid, 'display_name': category_name
                })
            print_msg(ALWAYS, f"Updated Category `{category_name}` with GUID {known_guid}", debug_level)
            return egeria_client.get_categories_by_guid(known_guid, output_format='FORM')

        elif object_action == "Create":
            is_root = True

            if category_exists:
                msg = (f"Cannot create`{category_name}` because it already exists; result document written for "
                       f"category update\n")
                print_msg(WARNING, msg, debug_level)
                return update_a_command(txt, command, object_type, known_q_name, known_guid)
            else:
                category_guid = egeria_client.create_category(known_glossary_guid, category_name, description, is_root)
                category_details = egeria_client.get_categories_by_guid(category_guid)

                if category_details == NO_CATEGORIES_FOUND:
                    msg = f"Just created category with GUID {category_guid} but category not found"
                    print_msg(ERROR, msg, debug_level)
                    return None

                qualified_name = category_details['glossaryCategoryProperties']["qualifiedName"]
                update_element_dictionary(qualified_name, {
                    'guid': category_guid, 'display_name': category_name
                    })
                print_msg(ALWAYS, f"Created Category `{category_name}` with GUID {category_guid}", debug_level)
                return egeria_client.get_categories_by_guid(category_guid, output_format='DR')


def process_set_categories_parent_command(egeria_client: EgeriaTech, element_dictionary: dict, txt: str,
                                          directive: str = "display") -> Optional[str]:
    """
    Processes a set_parent_category command by extracting key attributes such as
    parent and child category names from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting category-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    valid = True
    set_debug_level(directive)

    command, object_type, object_action = extract_command_plus(txt)

    parent_category_name = process_simple_attribute(txt, PARENT_CATEGORY_LABELS, "ERROR")
    child_category_name = process_simple_attribute(txt, CHILD_CATEGORY_LABELS, "ERROR")
    print(Markdown(f"{pre_command} `{command}` for parent category: `\'{parent_category_name}\'` \n\t"
                   f"and child category: `\'{child_category_name}\'` \nwith directive: `{directive}` "))

    if parent_category_name is None or child_category_name is None:
        valid = False
    else:
        parent_cat_q_name, parent_cat_guid, parent_cat_valid, parent_cat_exists = (
            get_element_by_name(egeria_client, 'Glossary Categories', parent_category_name))
        child_cat_q_name, child_cat_guid, child_cat_valid, child_cat_exists = (
            get_element_by_name(egeria_client, 'Glossary Categories', child_category_name))

    # Check if category exists (and get qname and guid)

    if parent_cat_exists and child_cat_exists:
        valid = True
        msg = f" Both categories {parent_category_name} and {child_category_name} exist\n"
        print_msg(INFO, msg, debug_level)
        if parent_cat_guid and child_cat_guid:
            msg = f" Both categories {parent_category_name} and {child_category_name} have GUIDs\n"
            print_msg(INFO, msg, debug_level)
        else:
            msg = f" Both categories {parent_category_name} and {child_category_name} do not have GUIDs\n"
            print_msg(ERROR, msg, debug_level)
            valid = False


    else:
        valid = False
        msg = f"Both categories {parent_category_name} and {child_category_name} do NOT exist\n"
        print_msg(ERROR, msg, debug_level)

    category_display = (f"\n* Command: {command}\n\t* Parent Category: {parent_category_name}\n\t\t"
                        f"* Qualified Name: {parent_cat_q_name}\n\t\t* GUID: {parent_cat_guid}\n\t"
                        f"* Child Category:\n{child_category_name}\n\t\t* Qualified Name: {child_cat_q_name}\n\t\t"
                        f"* GUID: {child_cat_guid}\n")

    # if object_action == 'Remove Parent Category':
    #     parent_guid = process_simple_attribute(txt, ['GUID', 'guid', 'Guid'])
    #
    #     category_display += (f"* GUID: {guid}\n\n")
    #     if not category_exists:
    #         msg = f"Category {category_name} can't be updated; {category_name} not found."
    #         print_msg(ERROR, msg, debug_level)
    #         valid = False
    #     else:
    #         msg = f"Glossary can be updated; {category_name} found"
    #         print_msg(ALWAYS, msg, debug_level)
    #
    # elif object_action == "Create":
    #     if category_exists:
    #         msg = f"Category {category_name} can't be created because it already exists.\n"
    #         print_msg("ERROR", msg, debug_level)
    #         valid = False
    #     elif valid:
    #         msg = f"It is valid to create Category `{category_name}` with:\n"
    #         print_msg("ALWAYS", msg, debug_level)

    if directive == "display":
        print(Markdown(category_display))
        return None

    elif directive == "validate":
        if valid:
            print(Markdown(category_display))
        else:
            msg = f"Validation failed for {object_type} `{parent_category_name}`\n"
            print_msg(ERROR, msg, debug_level)
            print(Markdown(category_display))
        return valid

    elif directive == "process":
        if valid:
            print(Markdown(category_display))
        else:
            msg = f"* --> Validation failed for {object_type} `{parent_category_name}`\n"
            print_msg(ERROR, msg, debug_level)
            print(Markdown(category_display))
            return None

        if object_action in ["Set", "Set Parent"]:
            egeria_client.set_parent_category(parent_cat_guid, child_cat_guid)
            print_msg(ALWAYS, f"Set parent category of `{child_category_name}` to `{parent_category_name}`",
                      debug_level)
            output_txt = txt.replace("Set Parent", "UnSet Parent")
            return output_txt

        elif object_action in ["UnSet", "UnSet Parent", "Unset Parent", "Unset", "Remove Parent"]:
            egeria_client.remove_parent_category(parent_cat_guid, child_cat_guid)
            print_msg(ALWAYS, f"UnSet parent category `{child_category_name}` from {parent_category_name}", debug_level)
            output_txt = txt.replace("UnSet Parent", "Set Parent")
            return output_txt

def process_term_list_command(egeria_client: EgeriaTech, element_dictionary: dict, txt: str,
                                directive: str = "display") -> Optional[str]:
    """ List terms as a markdown table. Filter based on optional search string. """
    set_debug_level(directive)
    valid = True
    command = extract_command(txt)
    object_type = command.split(' ')[1].strip()
    object_action = command.split(' ')[0].strip()
    known_glossary_q = ""
    known_glossary_guid = ""
    glossary_exists = False
    glossary_valid = False


    search_string = process_simple_attribute(txt, ['Search String', 'Filter'])
    if search_string is None:
        search_string = '*'
    print(Markdown(f"{pre_command} `{command}` with search string:`{search_string}` with directive: `{directive}`"))

    glossary = process_simple_attribute(txt, ['Glossary', 'In Glossary'])
    if glossary is not None:
        _, glossary_guid, _, glossary_exists = get_element_by_name(
        egeria_client, "Glossary", glossary)
        msg = f"Found glossary `{glossary}` with GUID {glossary_guid}"
        print_msg(INFO, msg, debug_level)
    else:
        glossary_guid= None
        msg = f"No glossary found"
        print_msg(INFO, msg, debug_level)


    request_display = f"\n* Search String: {search_string}\n* Glossary: {glossary}\n"

    if directive == "display":
        print(Markdown(request_display))
        return None
    elif directive == "validate":
        print(Markdown(request_display))
        return valid
    elif directive == "process":
        try:
            print(Markdown(request_display))
            if not valid:  # First validate the term before we process it
                return None

            md_table = egeria_client.find_glossary_terms(search_string,glossary_guid, output_format = "LIST")

            return md_table

        except Exception as e:
            print(f"{ERROR}Error creating Glossary Term list: {e}")
            console.print_exception(show_locals=True)
            return None

def process_category_list_command(egeria_client: EgeriaTech, element_dictionary: dict, txt: str,
                                directive: str = "display") -> Optional[str]:
    """ List terms as a markdown table. Filter based on optional search string. """
    set_debug_level(directive)
    valid = True
    command = extract_command(txt)
    object_type = command.split(' ')[1].strip()
    object_action = command.split(' ')[0].strip()
    known_glossary_q = ""
    known_glossary_guid = ""
    glossary_exists = False
    glossary_valid = False


    search_string = process_simple_attribute(txt, ['Search String', 'Filter'])
    if search_string is None:
        search_string = '*'
    print(Markdown(f"{pre_command} `{command}` with search string:`{search_string}` with directive: `{directive}`"))

    # glossary = process_simple_attribute(txt, ['Glossary', 'In Glossary'])
    # if glossary is not None:
    #     _, glossary_guid, _, glossary_exists = get_element_by_name(
    #     egeria_client, "Glossary", glossary)
    #     msg = f"Found glossary `{glossary}` with GUID {glossary_guid}"
    #     print_msg(INFO, msg, debug_level)
    # else:
    #     glossary_guid= None
    #     msg = f"No glossary found"
    #     print_msg(INFO, msg, debug_level)


    request_display = f"\n* Search String: {search_string}\n"

    if directive == "display":
        print(Markdown(request_display))
        return None
    elif directive == "validate":
        print(Markdown(request_display))
        return valid
    elif directive == "process":
        try:
            print(Markdown(request_display))
            if not valid:  # First validate the term before we process it
                return None
            md_table = egeria_client.find_glossary_categories(search_string, output_format = "LIST")

            return md_table

        except Exception as e:
            print(f"{ERROR}Error creating Glossary Category list: {e}")
            console.print_exception(show_locals=True)
            return None

def process_glossary_list_command(egeria_client: EgeriaTech, element_dictionary: dict, txt: str,
                                directive: str = "display") -> Optional[str]:
    """ List terms as a markdown table. Filter based on optional search string. """
    set_debug_level(directive)
    valid = True
    command = extract_command(txt)
    object_type = command.split(' ')[1].strip()
    object_action = command.split(' ')[0].strip()
    known_glossary_q = ""
    known_glossary_guid = ""
    glossary_exists = False
    glossary_valid = False


    search_string = process_simple_attribute(txt, ['Search String', 'Filter'])
    if search_string is None:
        search_string = '*'
    print(Markdown(f"{pre_command} `{command}` with search string:`{search_string}` with directive: `{directive}`"))


    request_display = f"\n* Search String: {search_string}\n"

    if directive == "display":
        print(request_display)
        return None
    elif directive == "validate":
        print(request_display)
        return valid
    elif directive == "process":
        try:
            print(request_display)
            if not valid:  # First validate the term before we process it
                return None

            md_table = egeria_client.find_glossaries(search_string, output_format = "LIST")

            return md_table

        except Exception as e:
            print(f"{ERROR}Error creating Glossary list: {e}")
            console.print_exception(show_locals=True)
            return None

def process_term_history_command(egeria_client: EgeriaTech, element_dictionary: dict, txt: str,
                                directive: str = "display") -> Optional[str]:
    """ List terms as a markdown table. Filter based on optional search string. """
    set_debug_level(directive)
    valid = True
    command = extract_command(txt)
    object_type = command.split(' ')[1].strip()
    object_action = command.split(' ')[0].strip()

    element_labels = TERM_NAME_LABELS
    element_labels.append('Display Name')

    term_name = process_simple_attribute(txt, element_labels, "ERROR")
    print(Markdown(f"{pre_command} `{command}` for term: `\'{term_name}\'` with directive: `{directive}` "))

    known_q_name, known_guid, valid, term_exists = process_element_identifiers(egeria_client, object_type,
                                                                               element_labels, txt, object_action,
                                                                            )

    print(Markdown(f"{pre_command} `{command}` for term:`{term_name}` with directive: `{directive}`"))


    request_display = f"\n\t* Term Name: {term_name}\n\t* Qualified Name: {known_q_name}\n\t* GUID: {known_guid}\n"

    if directive == "display":
        print(request_display)
        return None
    elif directive == "validate":
        print(request_display)
        return valid
    elif directive == "process":
        try:
            print(request_display)
            if not valid:  # First validate the term before we process it
                return None
            term_history_md = f"\n# Term History for `{term_name}`\n\n"
            term_history_md += egeria_client.list_full_term_history(known_guid, 'LIST')

            return term_history_md

        except Exception as e:
            print(f"{ERROR}Error creating Glossary list: {e}")
            console.print_exception(show_locals=True)
            return None




def process_term_upsert_command(egeria_client: EgeriaTech, element_dictionary: dict, txt: str,
                                directive: str = "display") -> Optional[str]:
    """
    Processes a term create or update command by extracting key attributes such as
    term name, summary, description, abbreviation, examples, usage, version, and status from the given cell.

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    valid = True
    categories_list = None
    cats_exist = True
    set_debug_level(directive)
    known_q_name = None
    command = extract_command(txt)
    object_type = command.split(' ')[1].strip()
    object_action = command.split(' ')[0].strip()

    term_name = process_simple_attribute(txt, ['Term Name', 'Display Name'], ERROR)
    print(Markdown(f"{pre_command} `{command}` for term:`{term_name}` with directive: `{directive}`"))
    summary = process_simple_attribute(txt, ['Summary'])
    description = process_simple_attribute(txt, ['Description'])
    abbreviation = process_simple_attribute(txt, ['Abbreviation'])
    examples = process_simple_attribute(txt, ['Examples'])
    usage = process_simple_attribute(txt, ['Usage'])
    status = process_simple_attribute(txt, ['Status'])
    status = status.upper() if status else 'DRAFT'
    version = process_simple_attribute(txt, ['Version', "Version Identifier", "Published Version"])
    q_name = process_simple_attribute(txt, ['Qualified Name'])

    # validate term name and get existing qualified_name and guid if they exist
    if term_name is None:
        valid = False
        known_q_name, known_guid, term_exists = None
    else:
        element_labels = TERM_NAME_LABELS
        element_labels.append('Display Name')
        known_q_name, known_guid, valid, term_exists = process_element_identifiers(egeria_client, object_type,
                                                                                   element_labels, txt, object_action,
                                                                                   version)

    # get the glossary qualified name this term is in
    glossary_name = process_simple_attribute(txt, GLOSSARY_NAME_LABELS, ERROR)
    if glossary_name is None:
        valid = False
        known_glossary_guid = None
        known_glossary_q_name = None
        glossary_valid = False
        glossary_exists = False
    else:
        known_glossary_q_name, known_glossary_guid, glossary_valid, glossary_exists = process_element_identifiers(
            egeria_client, "Glossary", GLOSSARY_NAME_LABELS, txt, "Exists Required", None)

    # process categories, if present
    categories = process_simple_attribute(txt, ['Glossary Categories', 'Glossary Category', 'Category', 'Categories'])
    if categories:  # Find information about categoriess that classify this term
        msg = "Checking for categories that classify this term"
        print_msg("DEBUG-INFO", msg, debug_level)
        categories_list, cat_q_name_list, cat_valid, cat_exist = process_q_name_list(egeria_client,
                                                                                     'Glossary Categories', txt,
                                                                                     CATEGORY_NAME_LABELS)
        if cat_exist and cat_valid:
            msg = f"Found valid glossary categories to classify the term:\n\t{term_name}"
            print_msg("INFO", msg, debug_level)
        else:
            msg = "No valid glossary categories found."
            print_msg("INFO", msg, debug_level)
    else:
        cat_exist = cat_valid = False
        cat_q_name_list = None

    if object_action == "Update":  # check to see if provided information exists and is consistent with existing info
        term_guid = process_simple_attribute(txt, GUID_LABELS)
        update_description = process_simple_attribute(txt, ['Update Description'])
        term_display = (f"\n* Command: {command}\n\t* Glossary: {known_glossary_q_name}\n\t"
                        f"* Term Name: {term_name}\n\t* Qualified Name: {q_name}\n\t* Categories: {categories}\n\t"
                        f"* Summary: {summary}\n\t* Description: {description}\n\t"
                        f"* Abbreviation: {abbreviation}\n\t* Examples: {examples}\n\t* Usage: {usage}\n\t"
                        f"* Version: {version}\n\t* Status: {status}\n\t* GUID: {term_guid}"
                        f"\n\t* Update Description: {update_description}\n")
        if not term_exists:
            msg = f"Update request invalid, Term {term_name} does not exist\n"
            print_msg(ERROR, msg, debug_level)
            valid = False

    elif object_action == 'Create':  # if the command is create, check that it doesn't already exist
        term_display = (f"\n* Command: {command}\n\t* Glossary: {known_glossary_q_name}\n\t"
                        f"* Term Name: {term_name}\n\t* Categories: {categories}\n\t* Summary: {summary}\n\t"
                        f"* Qualified Name: {q_name}\n\t* Description: {description}\n\t"
                        f"* Abbreviation: {abbreviation}\n\t* Examples: {examples}\n\t* Usage: {usage}\n\t"
                        f"* Version: {version}\n\t* Status: {status}\n")
        if term_exists:
            msg = f"Term `{term_name}` cannot be created since it already exists\n"
            print_msg(ERROR, msg, debug_level)
        else:
            msg = f"It is valid to create Term `{term_name}`"
            print_msg(ALWAYS, msg, debug_level)

    if directive == "display":
        print(Markdown(term_display))
        return None
    elif directive == "validate":
        print(Markdown(term_display))
        return valid
    elif directive == "process":
        try:
            if not valid:  # First validate the term before we process it
                return None
            print(Markdown(term_display))
            if object_action == "Update" and directive == "process":
                if not term_exists:
                    return None
                body = {
                    "class": "ReferenceableRequestBody", "elementProperties": {
                        "class": "GlossaryTermProperties", "qualifiedName": known_q_name, "summary": summary,
                        "description": description, "abbreviation": abbreviation, "examples": examples, "usage": usage,
                        "publishVersionIdentifier": version, "status": status
                        }, "updateDescription": update_description
                    }
                egeria_client.update_term(known_guid, body_slimmer(body))
                # if cat_exist and cat_valid:
                update_term_categories(egeria_client, known_guid, cats_exist, cat_q_name_list)
                print_msg(ALWAYS,
                          f"\tUpdated Term `{term_name}` with GUID {known_guid}\n\tand categories `{categories}`",
                          debug_level)
                return egeria_client.get_terms_by_guid(known_guid,
                                                       'md')  # return update_a_command(txt, command, object_type,
                # known_q_name, known_guid)
            elif object_action == "Update" and directive == "validate":  # is sthis reachable?
                return egeria_client.get_terms_by_guid(known_guid, 'md')

            elif object_action == "Create":
                if term_exists:
                    msg = f"Term {term_name} exists so result document modifies term create to term update"
                    print_msg(INFO, msg, debug_level)
                    return update_a_command(txt, command, object_type, q_name, known_guid)
                else:
                    ## get the guid for the glossary from the name - first look in cache
                    cached = get_element_dictionary().get(known_glossary_q_name, None)

                    if cached is not None:
                        glossary_guid = cached.get('guid', None)
                        if glossary_guid is None:
                            msg = f"Glossary GUID for {known_glossary_q_name} not found in cache"
                            print_msg(WARNING, msg, debug_level)  # should this ever occur?
                            return None
                    else:
                        glossary_guid = egeria_client.__get_guid__(qualified_name=known_glossary_q_name)
                        if glossary_guid == NO_ELEMENTS_FOUND:
                            msg = f"Glossary {known_glossary_q_name} not found"
                            print_msg(WARNING, msg, debug_level)
                            return None
                    term_body = {
                        "class": "ReferenceableRequestBody", "elementProperties": {
                            "class": "GlossaryTermProperties", "qualifiedName": known_q_name, "displayName": term_name,
                            "summary": summary, "description": description, "abbreviation": abbreviation,
                            "examples": examples, "usage": usage, "publishVersionIdentifier": version
                            # "additionalProperties":
                            #     {
                            #         "propertyName1": "xxxx",
                            #         "propertyName2": "xxxx"
                            #         }
                            }, "initialStatus": status
                        }
                    term_guid = egeria_client.create_controlled_glossary_term(glossary_guid, body_slimmer(term_body))
                    if term_guid == NO_ELEMENTS_FOUND:
                        print(f"{ERROR}Term {term_name} not created")
                        return None
                    if cats_exist and categories is not None:
                        update_term_categories(egeria_client, term_guid, cats_exist, cat_q_name_list)
                    update_element_dictionary(known_q_name, {'guid': term_guid, 'display_name': term_name})
                    print_msg(ALWAYS, f"Created term `{term_name}` with GUID {term_guid}", debug_level)
                    return egeria_client.get_terms_by_guid(term_guid,
                                                           'MD')  # return update_a_command(txt, command,
                    # object_type, q_name, term_guid)
        except Exception as e:
            print(f"{ERROR}Error creating term {term_name}: {e}")
            console.print_exception(show_locals=True)
            return None


def process_per_proj_upsert_command(egeria_client: ProjectManager, element_dictionary: dict, txt: str,
                                    directive: str = "display") -> str | None:
    """
    Processes a personal project create or update command by extracting key attributes such as
    glossary name, language, description, and usage from the given cell.

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    command = extract_command(txt)
    object = command.split()
    object_type = f"{object[1]} {object[2]}"
    object_action = object[0]
    set_debug_level(directive)

    project_name = process_simple_attribute(txt, ['Project Name'])
    description = process_simple_attribute(txt, ['Description'])
    project_identifier = process_simple_attribute(txt, ['Project Identifier'])
    project_status = process_simple_attribute(txt, ['Project Status'])
    project_phase = process_simple_attribute(txt, ['Project Phase'])
    project_health = process_simple_attribute(txt, ['Project Health'])
    start_date = process_simple_attribute(txt, ['Start Date'])
    planned_end_date = process_simple_attribute(txt, ['Planned End Date'])
    print(Markdown(f"{pre_command} `\'{command}\'` for project: `{project_name}` with directive: `{directive}` "))

    project_display = (f"\n* Command: {command}\n\t* Project: {project_name}\n\t"
                       f"* Status: {project_status}\n\t* Description: {description}\n\t"
                       f"* Phase: {project_phase}\n\t* Health: {project_health}\n\t"
                       f"* Start Date: {start_date}\n\t* Planned End Date: {planned_end_date}\n")

    def validate_project(obj_action: str) -> tuple[bool, bool, str, str]:
        valid = True
        msg = ""
        known_guid = None
        known_q_name = None

        project_details = egeria_client.get_projects_by_name(project_name)
        if project_details == NO_PROJECTS_FOUND:
            project_exists = False
        else:
            project_exists = True

        if project_name is None:
            msg = f"* {ERROR}Project name is missing\n"
            valid = False
        if project_status is None:
            msg += f"* {INFO}No Project status found\n"

        if description is None:
            msg += f"* {INFO}No Description found\n"

        if project_identifier is None:
            msg += f"* {INFO}No Project Identifier found\n"

        if project_phase is None:
            msg += f"* {INFO}No Project Phase found\n"

        if project_health is None:
            msg += f"* {INFO}No Project Health found\n"

        if start_date is None:
            msg += f"* {INFO}No Start Date found\n"
        elif not is_valid_iso_date(start_date):
            msg += f"* {ERROR}Start Date is not a valid ISO date of form  YYYY-MM-DD\n"
            valid = False

        if planned_end_date is None:
            msg += f"* {INFO} No Planned End Date found\n"
        elif not is_valid_iso_date(planned_end_date):
            msg += f"* {ERROR}Planned End Date is not a valid ISO date of form  YYYY-MM-DD\n"
            valid = False

        if obj_action == "Update":
            q_name = process_simple_attribute(txt, 'Qualified Name')

            if not project_exists:
                msg += f"* {ERROR}Project {project_name} does not exist\n"
                valid = False
            if len(project_details) > 1 and project_exists:
                msg += f"* {ERROR}More than one project with name {project_name} found\n"
                valid = False
            if len(project_details) == 1:
                known_guid = project_details[0]['elementHeader'].get('guid', None)
                known_q_name = project_details[0]['glossaryProperties'].get('qualifiedName', None)
            if q_name is None:
                msg += f"* {INFO}Qualified Name is missing => can use known qualified name of {known_q_name}\n"
                valid = True
            elif q_name != known_q_name:
                msg += (f"* {ERROR}Project {project_name} qualifiedName mismatch between {q_name} and {known_q_name}\n")
                valid = False
            if valid:
                msg += project_display
                msg += f"* -->Project {project_name} exists and can be updated\n"
            else:
                msg += f"* --> validation failed\n"
            msg += '---'
            print(Markdown(msg))
            return valid, project_exists, known_guid, known_q_name

        elif obj_action == "Create":
            if project_exists:
                msg += f"\n{ERROR}Project {project_name} already exists"
            else:
                msg += f"\n-->It is valid to create Project \'{project_name}\' with:\n"
            print(Markdown(msg))
            return valid, project_exists, known_guid, known_q_name

    if directive == "display":
        print(Markdown(project_display))
        return None

    elif directive == "validate":
        is_valid, exists, known_guid, known_q_name = validate_project(object_action)
        valid = is_valid if is_valid else None
        return valid

    elif directive == "process":
        is_valid, exists, known_guid, known_q_name = validate_project(object_action)
        if not is_valid:
            return None
        if object_action == "Update":
            if not exists:
                print(f"\n\n-->Project {project_name} does not exist")
                return None

            egeria_client.update_project(known_guid, known_q_name, project_identifier, project_name, description,
                                         project_status, project_phase, project_health, start_date, planned_end_date,
                                         False)
            print_msg(ALWAYS, f"Updated Project `{project_name}` with GUID {known_guid}", debug_level)
            return update_a_command(txt, command, object_type, known_q_name, known_guid)
        elif object_action == "Create":
            guid = None
            if exists:
                print(f"Project `{project_name}` already exists and update document created")
                return update_a_command(txt, command, object_type, known_q_name, known_guid)
            else:
                guid = egeria_client.create_project(None, None, None, False, project_name, description,
                                                    "PersonalProject", project_identifier, True, project_status,
                                                    project_phase, project_health, start_date, planned_end_date)
                project_g = egeria_client.get_project_by_guid(guid)
                if project_g == NO_GLOSSARIES_FOUND:
                    print(f"Just created with GUID {guid} but Project not found")
                    return None

                q_name = project_g['projectProperties']["qualifiedName"]
                update_element_dictionary(q_name, {'guid': guid, 'display_name': project_name})
                print_msg(ALWAYS, f"Created project `{project_name}` with GUID {guid}", debug_level)
                return update_a_command(txt, command, object_type, q_name, guid)
