"""
This file contains general utility functions for processing Egeria Markdown
"""
import os
import re
import sys
from typing import List

from rich.console import Console

from md_processing.md_processing_utils.common_md_utils import (get_current_datetime_string, print_msg,
                                                               get_element_dictionary,
                                                               update_element_dictionary, )
from md_processing.md_processing_utils.extraction_utils import (process_simple_attribute,
                                                                extract_attribute,
                                                                get_element_by_name)
from md_processing.md_processing_utils.message_constants import (ERROR, INFO, WARNING, ALWAYS, EXISTS_REQUIRED)
from md_processing.md_processing_utils.md_processing_constants import (get_command_spec)
from pyegeria import EgeriaTech
from pyegeria._globals import DEBUG_LEVEL

# Constants
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "170"))
console = Console(width=EGERIA_WIDTH)

debug_level = DEBUG_LEVEL
global COMMAND_DEFINITIONS


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


def parse_user_command(egeria_client: EgeriaTech, object_type: str, object_action: str, txt: str,
                       directive: str = "display") -> dict:
    parsed_attributes, parsed_output = {}, {}

    parsed_output['valid'] = True
    parsed_output['exists'] = False
    parsed_output['display'] = ""
    display_name = ""
    labels = {}

    command_spec = get_command_spec(object_type)
    attributes = command_spec.get('Attributes', [])
    command_display_name = command_spec.get('display_name', None)
    command_qn_prefix = command_spec.get('qn_prefix', None)


    # get the version early because we may need it to construct qualified names.
    version = process_simple_attribute(txt, {'Version', "Version Identifier", "Published Version"}, INFO)
    parsed_output['display_name'] = command_display_name
    parsed_output['qn_prefix'] = command_qn_prefix
    parsed_output['version'] = version
    parsed_output['is_own_anchor'] = command_spec.get('isOwnAnchor', True)
    parsed_output['parent_guid'] = command_spec.get('isOwnAnchor', True)

    msg = f"\tProcessing {object_action} on a {object_type} named `{command_display_name}` \n"
    print_msg(ALWAYS, msg, debug_level)

    for attr in attributes:
        for key in attr:
            if attr[key]['input_required'] is True:
                if_missing = ERROR
            else:
                if_missing = INFO
            lab= attr[key]['attr_labels'].split(';')
            labels:set = set()
            labels.add(key.strip())
            if lab is not None and lab != [""]:
                labels.update(lab)

            # if labels == "" or labels is None:
            #     msg = f"Missing attribute labels for {key}"
            #     print_msg(ERROR, msg, debug_level)
            #     parsed_output['valid'] = False
            #     continue
            style = attr[key]['style']
            if style == 'Simple':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing)
            elif style == 'Valid Value':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing)
            elif style == 'QN':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing)
            elif style == 'ID':
                parsed_attributes[key] = proc_el_id(egeria_client, command_display_name, command_qn_prefix,labels, txt,
                                                                  object_action, version, if_missing)
                parsed_output['guid'] = parsed_attributes[key].get('guid', None)
                parsed_output['qualified_name'] = parsed_attributes[key]['qualified_name']
                parsed_output['exists'] = parsed_attributes[key]['exists']

            elif style == 'Reference Name':
                parsed_attributes[key] = proc_ids(egeria_client, key,  labels,
                                                 txt, object_action, if_missing)
            elif style == 'GUID':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing)
            elif style == 'Ordered Int':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing)
            elif style == 'Simple Int':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing)
            elif style == 'Simple List':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing)
            elif style == 'Parent':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing)
            elif style == 'Bool':
                parsed_attributes[key] = proc_bool_attribute(txt, object_action, labels, if_missing)

            elif style == 'Reference Name List':
                parsed_attributes[key] = proc_name_list(egeria_client, key, txt, labels, if_missing)
            else:
                msg = f"Unknown attribute style: {style}"
                print_msg(ERROR, msg, debug_level)
                sys.exit(1)
                parsed_attributes[key]['valid'] = False
                parsed_attributes[key]['value'] = None
            if key == "Display Name":
                display_name = parsed_attributes[key]['value']

            if key == 'Qualified Name' and parsed_attributes[key]['exists'] is False:
                parsed_output['exists'] = False
            if parsed_attributes[key].get('value', None) is not None:
                parsed_output['display'] += (f"\n\t* {key}: `{parsed_attributes[key]['value']}`\n\t")

    if parsed_attributes['Parent ID']['value'] is not None:
        if (parsed_attributes['Parent Relationship Type Name']['value'] is None) or (parsed_attributes['Parent at End1']['value'] is  None):
            msg = "Parend ID was found but either Parent `Relationship Type Name` or `Parent at End1` are missing"
            print_msg(ERROR, msg, debug_level)
            parsed_output['valid'] = False
            parsed_output['reason'] = msg

    if directive in ["validate", "process"] and object_action == "Update" and not parsed_output['exists']:  # check to see if provided information exists and is consistent with existing info
        msg = f"Update request invalid, Term {display_name} does not exist\n"
        print_msg(ERROR, msg, debug_level)
        parsed_output['valid'] = False
    if directive in ["validate", "process"] and not parsed_output['valid']:
        msg = f"Request is invalid, `{object_action} {object_type}` is not valid - see previous messages\n"
        print_msg(ERROR, msg, debug_level)

    elif directive in ["validate", "process"] and object_action == 'Create':  # if the command is create, check that it doesn't already exist
        if parsed_output['exists']:
            msg = f"Element `{display_name}` cannot be created since it already exists\n"
            print_msg(ERROR, msg, debug_level)
            parsed_output['valid'] = False
        else:
            msg = f"It is valid to create Element `{display_name}`"
            print_msg(ALWAYS, msg, debug_level)

    parsed_output['attributes'] = parsed_attributes
    return parsed_output


def proc_simple_attribute(txt: str, action: str, labels: set, if_missing: str = INFO) -> dict:
    """Process a simple attribute based on the provided labels and if_missing value.
       Extract the attribute value from the text and store it in a dictionary along with valid.
       If it doesn`t exist, mark the dictionary entry as invalid and print an error message with severity of if_missing.

       Parameters:
       ----------
       txt: str
         The block of command text to extract attributes from.
       labels: list
         The possible attribute labels to search for. The first label will be used in messages.
       if_missing: str, default is INFO
         Can be one of "WARNING", "ERROR", "INFO". The severity of the missing attribute.
    """
    valid = True

    if if_missing not in ["WARNING", "ERROR", "INFO"]:
        msg = "Invalid severity for missing attribute"
        print_msg("ERROR", msg, debug_level)
        return {"status": ERROR, "reason": msg, "value": None, "valid": False}

    attribute = extract_attribute(txt, labels)

    if attribute is None:
        if if_missing == INFO or if_missing == WARNING:
            msg = f"Optional attribute with labels: `{labels}` missing"
            valid = True
        else:
            msg = f"Missing attribute with labels `{labels}` "
            valid = False
        print_msg(if_missing, msg, debug_level)
        return {"status": if_missing, "reason": msg, "value": None, "valid": valid, "exists": False}
    return {"status": INFO, "OK": None, "value": attribute, "valid": valid, "exists": True}

def proc_bool_attribute(txt: str, action: str, labels: set, if_missing: str = INFO) -> dict:
    """Process a boolean attribute based on the provided labels and if_missing value.
       Extract the attribute value from the text and store it in a dictionary along with valid.
       If it doesn`t exist, mark the dictionary entry as invalid and print an error message with severity of if_missing.

       Parameters:
       ----------
       txt: str
         The block of command text to extract attributes from.
       labels: list
         The possible attribute labels to search for. The first label will be used in messages.
       if_missing: str, default is INFO
         Can be one of "WARNING", "ERROR", "INFO". The severity of the missing attribute.
    """
    valid = True

    if if_missing not in ["WARNING", "ERROR", "INFO"]:
        msg = "Invalid severity for missing attribute"
        print_msg("ERROR", msg, debug_level)
        return {"status": ERROR, "reason": msg, "value": None, "valid": False}

    attribute = extract_attribute(txt, labels)

    if attribute is None:
        if if_missing == INFO or if_missing == WARNING:
            msg = f"Optional attribute with labels: `{labels}` missing"
            valid = True
        else:
            msg = f"Missing attribute with labels `{labels}` "
            valid = False
        print_msg(if_missing, msg, debug_level)
        return {"status": if_missing, "reason": msg, "value": None, "valid": valid, "exists": False}

    if isinstance(attribute, str):
        attribute = attribute.strip().lower()
        if attribute in ["true", "yes", "1"]:
            attribute = True
        elif attribute in ["false", "no", "0"]:
            attribute = False
        else:
            msg = f"Invalid value for boolean attribute `{labels}`"
            print_msg("ERROR", msg, debug_level)
            return {"status": ERROR, "reason": msg, "value": attribute, "valid": False, "exists": True}

    return {"status": INFO, "OK": None, "value": attribute, "valid": valid, "exists": True}



def proc_el_id(egeria_client: EgeriaTech, element_type: str, qn_prefix: str, element_labels: list[str], txt: str,
                             action: str, version: str = None, if_missing: str = INFO) -> dict:
    """
    Processes display_name and qualified_name by extracting them from the input text,
    checking if the element exists in Egeria, and validating the information. If a qualified
    name isn't found, one will be created.

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
        The action command to be executed (e.g., 'Create', 'Update', 'Display', ...)
    version: str, optional = None
        An optional version identifier used if we need to construct the qualified name

    Returns: dict with keys:
        status
        reason
        value   - value of display name
        valid   - name we parse out
        exists
        qualified_name - qualified name - either that we find or the one we construct
        guid - guid of the element if it already exists
    """
    valid = True
    exists = False
    identifier_output = {}

    element_name = extract_attribute(txt, element_labels)
    qualified_name = extract_attribute(txt, ["Qualified Name"])

    if qualified_name:
        q_name, guid, unique, exists = get_element_by_name(egeria_client, element_type,
                                                           qualified_name)  # Qualified name could be different if it
        # is being updated
    else:
        q_name, guid, unique, exists = get_element_by_name(egeria_client, element_type, element_name)
        qualified_name = q_name

    if unique is False:
        msg = f"Multiple elements named  {element_name} found"
        print_msg("DEBUG-ERROR", msg, debug_level)
        identifier_output = {"status": ERROR, "reason": msg, "value": element_name, "valid": False, "exists": True, }

    if action == "Update" and not exists:
        msg = f"Element {element_name} does not exist"
        print_msg("DEBUG-ERROR", msg, debug_level)
        identifier_output = {"status": ERROR, "reason": msg, "value": element_name, "valid": False, "exists": False, }

    elif action == "Update" and exists:
        msg = f"Element {element_name} exists"
        print_msg("DEBUG-INFO", msg, debug_level)
        identifier_output = {
            "status": INFO, "reason": msg, "value": element_name, "valid": True, "exists": True, 'qualified_name': q_name,
            'guid': guid
            }

    elif action == "Create" and exists:
        msg = f"Element {element_name} already exists"
        print_msg("DEBUG-ERROR", msg, debug_level)
        identifier_output = {"status": ERROR, "reason": msg, "value": element_name, "valid": False, "exists": True,
                             'qualified_name': qualified_name, 'guid': guid,}

    elif action == "Create" and not exists:
        msg = f"{element_type} `{element_name}` does not exist"
        print_msg("DEBUG-INFO", msg, debug_level)
        identifier_output = {"status": INFO, "reason": msg, "value": element_name, "valid": True, "exists": False,
                             'qualified_name': q_name}

        if q_name is None and qualified_name is None:
            q_name = egeria_client.__create_qualified_name__(qn_prefix, element_name, version_identifier=version)
            update_element_dictionary(q_name, {'display_name': element_name})
            identifier_output['qualified_name'] = q_name
        elif qualified_name:
            update_element_dictionary(qualified_name, {'display_name': element_name})
            identifier_output['qualified_name'] = qualified_name


    return identifier_output

def proc_ids(egeria_client: EgeriaTech, element_type: str, element_labels: set, txt: str,
                             action: str, if_missing: str = INFO) -> dict:
    """
    Processes element identifiers from the input text using the labels supplied,
    checking if the element exists in Egeria, and validating the information.

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
        The action command to be executed (e.g., 'Create', 'Update', 'Display', ...)
    version: str, optional = None
        An optional version identifier used if we need to construct the qualified name

    Returns: dict with keys:
        status
        reason
        value
        valid   - name we parse out
        exists
        qualified_name - what we find exists
        guid
    """
    valid = True
    exists = False
    identifier_output = {}
    unique = True
    value = None

    element_name = extract_attribute(txt, element_labels)
    if element_name:
        q_name, guid, unique, exists = get_element_by_name(egeria_client, element_type, element_name)
        value = element_name
    else:
        exists = False


    if exists is True and unique is False:
        msg = f"Multiple elements named  {element_name} found"
        print_msg("DEBUG-ERROR", msg, debug_level)
        identifier_output = {"status": ERROR, "reason": msg, "value": element_name, "valid": False, "exists": True, }


    elif action == EXISTS_REQUIRED or if_missing == ERROR and not exists:
        msg = f"Required {element_type} `{element_name}` does not exist"
        print_msg("DEBUG-ERROR", msg, debug_level)
        identifier_output = {"status": ERROR, "reason": msg, "value": element_name, "valid": False, "exists": False, }
    elif value is None:
        msg = f"Optional attribute with label`{element_type}` missing"
        print_msg("INFO", msg, debug_level)
        identifier_output = {"status": INFO, "reason": msg, "value": None, "valid": False, "exists": False, }
    else:
        msg = f"Element {element_type} `{element_name}` exists"
        print_msg("DEBUG-INFO", msg, debug_level)
        identifier_output = {
            "status": INFO, "reason": msg, "value": element_name, "valid": True, "exists": True,
            "qualified_name": q_name, 'guid': guid
            }

    return identifier_output




def proc_name_list(egeria_client: EgeriaTech, element_type: str, txt: str, element_labels: set,
                   if_missing: str = INFO) -> dict:
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
        required: bool, default is False
            - indicates whether the list of names is required to be present in the input text.

    Returns:
        Dict containing:
        'names'    - Concatenated valid input names as a single string (or None if empty).
        'name_list'    - A list of known qualified names extracted from the processed elements.
        'valid'    - A boolean indicating whether all elements are valid.
        'exists'    - A boolean indicating whether all elements exist.
    """
    valid = True
    exists = True
    id_list_output = {}
    elements = ""
    new_element_list = []

    elements_txt = extract_attribute(txt, element_labels)

    if elements_txt is None:
        msg = f"Attribute with labels `{{element_type}}` missing"
        print_msg("DEBUG-INFO", msg, debug_level)
        return {"status": if_missing, "reason": msg, "value": None, "valid": False, "exists": False, }
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
            id_list_output = {
                "status": INFO, "reason": msg, "value": elements, "valid": valid, "exists": exists,
                "name_list": new_element_list,
                }
        else:
            msg = f" Name list contains one or more invalid qualified names."
            print_msg("DEBUG-INFO", msg, debug_level)
            id_list_output = {"status": if_missing, "reason": msg, "value": None, "valid": valid, "exists": exists, }
        return id_list_output


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
    else:  # No categories specified - so remove any categories a term is in
        for cat in current_categories:
            egeria_client.remove_term_from_category(term_guid, cat)
            msg = f"Removed term {term_guid} from category {cat}"
            print_msg("DEBUG-INFO", msg, debug_level)
