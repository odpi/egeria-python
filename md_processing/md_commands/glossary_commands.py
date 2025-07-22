"""
This file contains glossary-related object_action functions for processing Egeria Markdown
"""

import json
import os
import re
from typing import List, Optional

from rich import print
from rich.console import Console
from rich.markdown import Markdown

from md_processing.md_processing_utils.common_md_utils import (debug_level, print_msg, set_debug_level,
                                                               get_element_dictionary, update_element_dictionary,
                                                               setup_log)
from md_processing.md_processing_utils.extraction_utils import (extract_command_plus, extract_command,
                                                                process_simple_attribute, process_element_identifiers,
                                                                update_a_command, extract_attribute,
                                                                get_element_by_name, process_name_list)
from md_processing.md_processing_utils.md_processing_constants import (GLOSSARY_NAME_LABELS, TERM_NAME_LABELS,
                                                                       TERM_RELATIONSHPS, PARENT_CATEGORY_LABELS,
                                                                       CATEGORY_NAME_LABELS, ALWAYS, ERROR, INFO,
                                                                       WARNING, pre_command, EXISTS_REQUIRED,
                                                                       OUTPUT_LABELS, SEARCH_LABELS, GUID_LABELS,
                                                                       ELEMENT_OUTPUT_FORMATS, command_seperator)
from pyegeria import body_slimmer
from pyegeria._globals import (NO_GLOSSARIES_FOUND, NO_ELEMENTS_FOUND, NO_CATEGORIES_FOUND)
from pyegeria.egeria_tech_client import EgeriaTech

EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "170"))
console = Console(width=EGERIA_WIDTH)
setup_log()

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


def process_glossary_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a glossary create or update object_action by extracting key attributes such as
    glossary name, language, description, and usage from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """

    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))
    set_debug_level(directive)

    glossary_name = process_simple_attribute(txt, GLOSSARY_NAME_LABELS, ERROR)
    print(Markdown(
        f"{pre_command} `{object_action}` `{object_type}`  for glossary: `\'{glossary_name}\'` with directive: `"
        f"{directive}` "))
    language = process_simple_attribute(txt, ['Language'], INFO)
    description = process_simple_attribute(txt, ['Description'], INFO)
    usage = process_simple_attribute(txt, ['Usage'], INFO)
    q_name = process_simple_attribute(txt, ['Qualified Name'], INFO)
    valid = True

    if glossary_name is None:
        valid = False
        known_q_name = None
        known_guid = None
        glossary_exists = False
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
            if glossary_exists and object_action == "Create":
                msg = (f"Create failed because glossary `{glossary_name}` exists - changing `Create` to `Update` in "
                       f"processed output \n")
                print_msg(ERROR, msg, debug_level)
                print(Markdown(glossary_display))
                print(command_seperator)
                return update_a_command(txt, object_action, object_type, known_q_name, known_guid)
            else:
                return None
        if object_action == "Update":
            if not glossary_exists:
                print(f"\n{ERROR}Glossary `{glossary_name}` does not exist! Updating result document with Create "
                      f"object_action\n")
                return update_a_command(txt, object_action, object_type, known_q_name, known_guid)

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
                return update_a_command(txt, object_action, object_type, known_q_name, known_guid)
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
                # return update_a_command(txt, object_action, object_type, qualified_name, glossary_guid)
                print_msg(ALWAYS, f"Created Glossary `{glossary_name}` with GUID {glossary_guid}", debug_level)
                return egeria_client.get_glossary_by_guid(glossary_guid, output_format='FORM')
        else:
            return None
    else:
        return None


def process_category_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a glossary category create or update object_action by extracting key attributes such as
    category name, qualified, description, and anchor glossary from the given txt..

    :param txt: A string representing the input cell to be processed for
        extracting category-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    valid = True
    set_debug_level(directive)

    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))

    category_name = process_simple_attribute(txt, ['Category Name', 'category_name', 'Cat'])
    print(Markdown(f"{pre_command} `{command}` for category: `\'{category_name}\'` with directive: `{directive}` "))

    owning_glossary_name = extract_attribute(txt, ['Owning Glossary', 'In Glossary'])
    description = process_simple_attribute(txt, ['Description'])
    q_name = process_simple_attribute(txt, ['Qualified Name'])

    parent_category_name = process_simple_attribute(txt, PARENT_CATEGORY_LABELS, "INFO")

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
            egeria_client, "Glossary", GLOSSARY_NAME_LABELS, txt, EXISTS_REQUIRED, None)

    if parent_category_name:
        _, parent_guid, parent_valid, parent_exists = get_element_by_name(egeria_client, 'Glossary Categories',
                                                                          parent_category_name)
    else:
        parent_guid = None
        parent_exists = False
        parent_valid = False

    category_display = (
        f"\n* Command: {command}\n\t* Category: {category_name}\n\t* In Glossary: {owning_glossary_name}\n\t"
        f"* Description:\n{description}\n\t* Parent Category: {parent_category_name}\n\t"
        f"* Qualified Name: {q_name}\n\t")

    if object_action == 'Update':
        guid = process_simple_attribute(txt, ['GUID', 'guid', 'Guid'])

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
            if category_exists and object_action == "Create":
                msg = (f"Create failed because category `{category_name}` exists - changing `Create` to `Update` in "
                       f"processed output \n")
                print_msg(ERROR, msg, debug_level)
                print(Markdown(category_display))
                return update_a_command(txt, object_action, object_type, known_q_name, known_guid)
            else:
                return None

        if object_action == "Update":
            if not category_exists:
                print(f"\n{ERROR}category `{category_name}` does not exist! Updating result document with Create "
                      f"object_action\n")
                return update_a_command(txt, object_action, object_type, known_q_name, known_guid)

            # Update the basic category properties
            egeria_client.update_category(known_guid, category_name, description, known_q_name, None)
            msg = f"->Updated category `{category_name}`with GUID {known_guid}"
            print_msg(ALWAYS, msg, debug_level)

            # Update parent-child relationships

            update_element_dictionary(known_q_name, {
                'guid': known_guid, 'display_name': category_name
                })

            category_sync = update_category_parent(egeria_client, known_guid, parent_category_name)
            print_msg(ALWAYS, f"Updated Category hierarchy for  `{category_name}` with outcome {category_sync}",
                      debug_level)
            return egeria_client.get_category_by_guid(known_guid, output_format='FORM')

        elif object_action == "Create":
            is_root = True

            if category_exists:
                msg = (f"Cannot create`{category_name}` because it already exists; result document written for "
                       f"category update\n")
                print_msg(WARNING, msg, debug_level)
                return update_a_command(txt, object_action, object_type, known_q_name, known_guid)
            else:
                category_guid = egeria_client.create_category(known_glossary_guid, category_name, description, is_root)
                category_details = egeria_client.get_category_by_guid(category_guid)

                if category_details == NO_CATEGORIES_FOUND:
                    msg = f"Just created category with GUID {category_guid} but category not found"
                    print_msg(ERROR, msg, debug_level)
                    return None

                qualified_name = category_details['glossaryCategoryProperties']["qualifiedName"]
                update_element_dictionary(qualified_name, {
                    'guid': category_guid, 'display_name': category_name
                    })
                print_msg(ALWAYS, f"Created Category `{category_name}` with GUID {category_guid}", debug_level)
                if parent_valid and parent_guid:
                    egeria_client.set_parent_category(parent_guid, category_guid)
                    print_msg(ALWAYS, f"Set parent category for `{category_name}` to `{parent_category_name}`",
                              debug_level)
                else:
                    print_msg(ERROR,
                              f"Parent category `{parent_category_name}` not found or invalid for `{category_name}`",
                              debug_level)
                return egeria_client.get_category_by_guid(category_guid, output_format='FORM')
        return None
    return None


def update_category_parent(egeria_client, category_guid: str, parent_category_name: str = None) -> bool:
    """
    Updates the parent relationship for a category.

    If a parent category is specified, it will check if a parent is currently set.
    If a parent category was set and is the same as the parent category specified, no change is needed.
    If a parent category was set and is different from the parent_category_name, the parent category is updated.
    If parent_category_name is None or empty and an existing parent category was set, the parent category is removed.

    Parameters
    ----------
    egeria_client: EgeriaTech
        The Egeria client to use for API calls
    category_guid: str
        The GUID of the category to update
    parent_category_name: str, optional
        The name of the parent category to set, or None to remove the parent

    Returns
    -------

    True if successful, False otherwise.

    """
    outcome = True
    # Handle parent category updates
    if parent_category_name:
        # Check if a parent is currently set
        current_parent = egeria_client.get_category_parent(category_guid)

        if isinstance(current_parent, str) and "No Parent Category found" in current_parent:
            # No parent currently set, need to set it
            _, parent_guid, _, parent_exists = get_element_by_name(egeria_client, 'Glossary Categories',
                                                                   parent_category_name)

            if parent_exists and parent_guid:
                egeria_client.set_parent_category(parent_guid, category_guid)
                print_msg(ALWAYS, f"Set parent category of category to `{parent_category_name}`", debug_level)
            else:
                print_msg(ERROR, f"Parent category `{parent_category_name}` not found", debug_level)
                outcome = False
        else:
            # Parent is set, check if it's the same
            current_parent_name = current_parent.get('glossaryCategoryProperties', {}).get('qualifiedName', '')

            if current_parent_name != parent_category_name:
                # Different parent, need to update
                # First remove the current parent
                current_parent_guid = current_parent.get('elementHeader', {}).get('guid', '')
                if current_parent_guid:
                    egeria_client.remove_parent_category(current_parent_guid, category_guid)

                # Then set the new parent
                _, parent_guid, _, parent_exists = get_element_by_name(egeria_client, 'Glossary Categories',
                                                                       parent_category_name)

                if parent_exists and parent_guid:
                    egeria_client.set_parent_category(parent_guid, category_guid)
                    print_msg(ALWAYS,
                              f"Updated parent category from `{current_parent_name}` to `{parent_category_name}`",
                              debug_level)
                else:
                    print_msg(ERROR, f"Parent category `{parent_category_name}` not found", debug_level)
                    outcome = False
    elif parent_category_name is None or parent_category_name == '':
        # Check if a parent is currently set and remove it if needed
        current_parent = egeria_client.get_category_parent(category_guid)

        if not isinstance(current_parent, str) or "No Parent Category found" not in current_parent:
            # Parent is set, need to remove it
            current_parent_guid = current_parent.get('elementHeader', {}).get('guid', '')
            current_parent_name = current_parent.get('glossaryCategoryProperties', {}).get('qualifiedName', '')

            if current_parent_guid:
                egeria_client.remove_parent_category(current_parent_guid, category_guid)
                print_msg(ALWAYS, f"Removed parent category `{current_parent_name}`", debug_level)

    return outcome


def process_term_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a term create or update object_action by extracting key attributes such as
    term name, summary, description, abbreviation, examples, usage, version, and status from the given cell.

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    valid = True
    categories_list = None
    cats_exist = False
    set_debug_level(directive)
    known_q_name = None
    command = extract_command(txt)
    print(Markdown(f"# {command}\n"))

    object_type = command.split(' ')[1].strip()
    object_action = command.split(' ')[0].strip()

    term_name = process_simple_attribute(txt, ['Term Name', 'Display Name'], ERROR)
    print(Markdown(f"{pre_command} `{command}` for term:`{term_name}` with directive: `{directive}`"))
    summary = process_simple_attribute(txt, ['Summary'], INFO)
    description = process_simple_attribute(txt, ['Description'], INFO)
    abbreviation = process_simple_attribute(txt, ['Abbreviation'], INFO)
    examples = process_simple_attribute(txt, ['Examples'], INFO)
    usage = process_simple_attribute(txt, ['Usage'], INFO)
    status = process_simple_attribute(txt, ['Status'])
    status = status.upper() if status else 'DRAFT'
    version = process_simple_attribute(txt, ['Version', "Version Identifier", "Published Version"], INFO)
    q_name = process_simple_attribute(txt, ['Qualified Name'], INFO)

    aliases = process_simple_attribute(txt, ['Aliases', 'Alias'], INFO)
    if aliases:
        alias_list = list(filter(None, re.split(r'[,\n]+', aliases.strip())))
    else:
        alias_list = None

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
            egeria_client, "Glossary", GLOSSARY_NAME_LABELS, txt, EXISTS_REQUIRED, None)
        if not glossary_exists or known_glossary_guid is None:
            glossary_valid = False
            valid = False

    # process categories, if present
    categories = process_simple_attribute(txt, ['Glossary Categories', 'Glossary Category', 'Category', 'Categories'])
    if categories:  # Find information about categoriess that classify this term
        msg = "Checking for categories that classify this term"
        print_msg("DEBUG-INFO", msg, debug_level)
        categories_list, cat_q_name_list, cats_valid, cats_exist = process_name_list(egeria_client,
                                                                                     'Glossary Categories', txt,
                                                                                     CATEGORY_NAME_LABELS)
        if cats_exist and cats_valid:
            msg = f"Found valid glossary categories to classify the term:\n\t{term_name}"
            print_msg("INFO", msg, debug_level)
        else:
            msg = "No valid glossary categories found."
            print_msg("INFO", msg, debug_level)
    else:
        cats_exist = cats_valid = False
        cat_q_name_list = None

    if object_action == "Update":  # check to see if provided information exists and is consistent with existing info
        term_guid = process_simple_attribute(txt, GUID_LABELS)
        update_description = process_simple_attribute(txt, ['Update Description'])
        term_display = (f"\n* Command: {command}\n\t* Glossary: {known_glossary_q_name}\n\t"
                        f"* Term Name: {term_name}\n\t* Qualified Name: {q_name}\n\t* Aliases: {aliases}\n\t"
                        f"* Categories: {categories}\n\t"
                        f"* Summary: {summary}\n\t* Description: {description}\n\t"
                        f"* Abbreviation: {abbreviation}\n\t* Examples: {examples}\n\t* Usage: {usage}\n\t"
                        f"* Version: {version}\n\t* Status: {status}\n\t* GUID: {term_guid}"
                        f"\n\t* Update Description: {update_description}\n")
        if not term_exists:
            msg = f"Update request invalid, Term {term_name} does not exist\n"
            print_msg(ERROR, msg, debug_level)
            valid = False

    elif object_action == 'Create':  # if the object_action is create, check that it doesn't already exist
        term_display = (f"\n* Command: {command}\n\t* Glossary: {known_glossary_q_name}\n\t"
                        f"* Term Name: {term_name}\n\t* Categories: {categories}\n\t* Summary: {summary}\n\t"
                        f"* Qualified Name: {q_name}\n\t* Aliases: {aliases}\n\t* Description: {description}\n\t"
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
                if term_exists and object_action == "Create":
                    msg = (f"Create failed because term `{term_name}` exists - changing `Create` to `Update` in "
                           f"processed output \n")
                    print_msg(ERROR, msg, debug_level)
                    print(Markdown(term_display))
                    return update_a_command(txt, object_action, object_type, known_q_name, known_guid)
                else:
                    return None

            print(Markdown(term_display))
            if object_action == "Update" and directive == "process":
                if not term_exists:
                    return None
                body = {
                    "class": "ReferenceableRequestBody", "elementProperties": {
                        "displayName": term_name, "class": "GlossaryTermProperties", "qualifiedName": known_q_name,
                        "aliases": alias_list, "summary": summary, "description": description,
                        "abbreviation": abbreviation, "examples": examples, "usage": usage,
                        "publishVersionIdentifier": version, "status": status
                        }, "updateDescription": update_description
                    }
                egeria_client.update_term(known_guid, body_slimmer(body), is_merge_update=False)
                # if cat_exist and cat_valid:
                update_term_categories(egeria_client, known_guid, cats_exist, cat_q_name_list)
                print_msg(ALWAYS,
                          f"\tUpdated Term `{term_name}` with GUID {known_guid}\n\tand categories `{categories}`",
                          debug_level)
                return egeria_client.get_term_by_guid(known_guid,
                                                      'md')  # return update_a_command(txt, object_action, object_type,
                # known_q_name, known_guid)
            elif object_action == "Update" and directive == "validate":  # is sthis reachable?
                return egeria_client.get_term_by_guid(known_guid, 'md')

            elif object_action == "Create":
                if term_exists:
                    msg = f"Term {term_name} exists so result document modifies term create to term update"
                    print_msg(INFO, msg, debug_level)
                    return update_a_command(txt, object_action, object_type, q_name, known_guid)
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
                            "aliases": alias_list, "summary": summary, "description": description,
                            "abbreviation": abbreviation, "examples": examples, "usage": usage,
                            "publishVersionIdentifier": version
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
                    return egeria_client.get_term_by_guid(term_guid,
                                                          'MD')  # return update_a_command(txt, object_action,
                    # object_type, q_name, term_guid)
        except Exception as e:
            print(f"{ERROR}Error creating term {term_name}: {e}")
            console.print_exception(show_locals=True)
            return None
    else:
        return None


def process_create_term_term_relationship_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> \
Optional[str]:
    """ Relate two terms through the specified relationship. ."""
    set_debug_level(directive)
    valid = True
    command = extract_command(txt)
    print(Markdown(f"# {command}\n"))

    object_type = command.split(' ')[1].strip()
    object_action = command.split(' ')[0].strip()
    term1_guid = None
    term2_guid = None

    term_relationship = process_simple_attribute(txt, ["Term Relationship", "Relationship Type"], "ERROR")
    if term_relationship not in TERM_RELATIONSHPS:
        valid = False

    print(Markdown(
        f"{pre_command} `{command}` for term relationship: `{term_relationship}` with directive: `{directive}` "))

    term1_q_name, term1_guid, term1_valid, term1_exists = process_element_identifiers(egeria_client, object_type,
                                                                                      ["Term 1 Name", "Term 1"], txt,
                                                                                      "Exists Required", None)

    term2_q_name, term2_guid, term2_valid, term2_exists = process_element_identifiers(egeria_client, object_type,
                                                                                      ["Term 2 Name", "Term 2"], txt,
                                                                                      "Exists Required", None)

    request_display = (f"\n\t* Term 1 Qualified Name: {term1_q_name}\n\t* Term 2 Qualified Name {term2_q_name}\n\t"
                       f"* Term Relationship: {term_relationship}")

    if not (term1_valid and term2_valid and term1_exists and term2_exists):
        valid = False

    if directive == "display":
        print(request_display)
        return None
    elif directive == "validate":
        print(request_display)
        return str(valid)
    elif directive == "process":
        try:
            print(request_display)
            if not valid:  # First validate the term before we process it
                return None
            egeria_client.add_relationship_between_terms(term1_guid, term2_guid, term_relationship)
            print_msg(ALWAYS, f"Relationship `{term_relationship}` created", debug_level)
            update_md = (f"\n\n# Update Term-Term Relationship\n\n## Term 1 Name:\n\n{term1_q_name}"
                         f"\n\n## Term 2 Name\n\n{term2_q_name}\n\n## Term Relationship:\n\n{term_relationship}")
            return update_md


        except Exception as e:
            print(f"{ERROR}Error performing {command}: {e}")
            console.print_exception(show_locals=True)
            return None
    else:
        return None


def process_term_list_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """ List terms as a markdown table. Filter based on optional search string. """
    set_debug_level(directive)
    valid = True
    command = extract_command(txt)
    print(Markdown(f"# {command}\n"))

    search_string = process_simple_attribute(txt, SEARCH_LABELS)
    if search_string is None:
        search_string = '*'
    print(Markdown(f"{pre_command} `{command}` with search string:`{search_string}` with directive: `{directive}`"))

    glossary = process_simple_attribute(txt, ['Glossary', 'In Glossary', "Glossary Name"])
    if glossary is not None:
        _, glossary_guid, _, glossary_exists = get_element_by_name(egeria_client, "Glossary", glossary)
        msg = f"Found glossary `{glossary}` with GUID {glossary_guid}"
        print_msg(INFO, msg, debug_level)
    else:
        glossary_guid = None
        msg = f"No glossary found"
        print_msg(INFO, msg, debug_level)

    output_format = process_simple_attribute(txt, OUTPUT_LABELS)
    if output_format is None:
        output_format = "LIST"
    elif output_format not in ELEMENT_OUTPUT_FORMATS:
        valid = False
        print_msg(ERROR, f"Invalid output format: `{output_format}`", debug_level)

    request_display = (f"\n\t* Search String: {search_string}\n\t* Glossary: {glossary}\n\t* Output Format: "
                       f"{output_format}\n")

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

            term_list_md = f"\n# Term List for search string: `{search_string}`\n\n"
            if output_format == "DICT":
                struct = egeria_client.find_glossary_terms(search_string, glossary_guid, output_format=output_format)
                term_list_md += f"```{json.dumps(struct, indent=4)}```\n"
            else:
                term_list_md += egeria_client.find_glossary_terms(search_string, glossary_guid,
                                                                  output_format=output_format)
            print_msg("ALWAYS", f"Wrote Term List for search string: `{search_string}`", debug_level)

            return term_list_md

            md_table = egeria_client.find_glossary_terms(search_string, glossary_guid, output_format=output_format)

            print_msg("ALWAYS", f"Wrote Term list for search string `{search_string}`", debug_level)
            return md_table

        except Exception as e:
            print(f"{ERROR}Error performing {command}: {e}")
            console.print_exception(show_locals=True)
            return None
    else:
        return None


def process_category_list_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """ List terms as a markdown table. Filter based on optional search string. """
    set_debug_level(directive)
    valid = True
    command = extract_command(txt)
    print(Markdown(f"# {command}\n"))

    search_string = process_simple_attribute(txt, SEARCH_LABELS, "INFO")
    if search_string is None:
        search_string = '*'
    print(Markdown(f"{pre_command} `{command}` with search string:`{search_string}` with directive: `{directive}`"))

    output_format = process_simple_attribute(txt, OUTPUT_LABELS, "INFO")
    if output_format is None:
        output_format = "LIST"
    elif output_format not in ELEMENT_OUTPUT_FORMATS:
        valid = False
        print_msg(ERROR, f"Invalid output format: `{output_format}`", debug_level)

    request_display = f"\n\t* Search String: {search_string}\n\t* Output Format: {output_format}\n"

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

            cat_list_md = f"\n# Category List for search string: `{search_string}`\n\n"
            if output_format == "DICT":
                struct = egeria_client.find_glossary_categories(search_string, output_format=output_format)
                cat_list_md += f"```{json.dumps(struct, indent=4)}```\n"
            else:
                cat_list_md += egeria_client.find_glossary_categories(search_string, output_format=output_format)
            print_msg("ALWAYS", f"Wrote Category List for search string: `{search_string}`", debug_level)

            return cat_list_md

        except Exception as e:
            print(f"{ERROR}Error performing {command}: {e}")
            console.print_exception(show_locals=True)
            return None
    else:

        return None


def process_glossary_structure_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[
    str]:
    """ List terms as a markdown table. Filter based on optional search string. """
    set_debug_level(directive)
    valid = True
    command = extract_command(txt)
    print(Markdown(f"# {command}\n"))

    known_glossary_guid = ""

    glossary_name = process_simple_attribute(txt, GLOSSARY_NAME_LABELS, "ERROR")

    _, known_glossary_guid, valid, _ = process_element_identifiers(egeria_client, "Glossary", GLOSSARY_NAME_LABELS, txt,
                                                                   EXISTS_REQUIRED, None)

    print(Markdown(f"{pre_command} `{command}` for glossary:`{glossary_name}` with directive: `{directive}`"))

    output_format = process_simple_attribute(txt, OUTPUT_LABELS, "INFO")
    if output_format is None:
        output_format = "MD"
    elif output_format not in ["DICT", "LIST", "MD"]:
        valid = False
        print_msg(ERROR, f"Invalid output format: `{output_format}`", debug_level)

    request_display = f"\n\t* Glossary name: {glossary_name}\n\t* Output Format: {output_format}\n"

    if directive == "display":
        print(Markdown(request_display))
        return None
    elif directive == "validate":
        print(Markdown(request_display))
        return str(valid)
    elif directive == "process":
        try:
            print(Markdown(request_display))
            if not valid:  # First validate the term before we process it
                return None

            glossary_structure_md = f"\n# Glossary Structure for `{glossary_name}`\n\n"
            if output_format == "DICT":
                struct = egeria_client.get_glossary_category_structure(known_glossary_guid, output_format=output_format)
                glossary_structure_md += f"```{json.dumps(struct, indent=4)}```\n"
            else:
                glossary_structure_md += egeria_client.get_glossary_category_structure(known_glossary_guid,
                                                                                       output_format=output_format)
            print_msg("ALWAYS", f"Wrote Glossary Structure for glossary: `{glossary_name}`", debug_level)

            return glossary_structure_md

        except Exception as e:
            print(f"{ERROR}Error performing {command}: {e}")
            console.print_exception(show_locals=True)
            return None
    else:
        return None


def process_glossary_list_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """ List terms as a markdown table. Filter based on optional search string. """
    set_debug_level(directive)
    valid = True
    command = extract_command(txt)
    print(Markdown(f"# {command}\n"))

    search_string = process_simple_attribute(txt, SEARCH_LABELS, "INFO")
    if search_string is None:
        search_string = '*'
    print(Markdown(f"{pre_command} `{command}` with search string:`{search_string}` with directive: `{directive}`"))
    if search_string is None:
        search_string = '*'

    output_format = process_simple_attribute(txt, OUTPUT_LABELS, "INFO")
    if output_format is None:
        output_format = "LIST"
    elif output_format not in ELEMENT_OUTPUT_FORMATS:
        valid = False
        print_msg(ERROR, f"Invalid output format: `{output_format}`", debug_level)

    request_display = f"\n\t* Search String: {search_string}\n\t* Output Format: {output_format}\n"

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

            glossary_list_md = f"\n# Glossary List for `{search_string}`\n\n"
            if output_format == "DICT":
                struct = egeria_client.find_glossaries(search_string, output_format=output_format)
                glossary_list_md += f"```{json.dumps(struct, indent=4)}```\n"
            else:
                glossary_list_md += egeria_client.find_glossaries(search_string, output_format=output_format)
            print_msg("ALWAYS", f"Wrote Glossary List for search string: `{search_string}`", debug_level)

            return glossary_list_md

        except Exception as e:
            print(f"{ERROR}Error performing {command}: {e}")
            console.print_exception(show_locals=True)
            return None
    else:
        return None


def process_term_details_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """ List terms as a markdown table. Filter based on optional search string. """
    set_debug_level(directive)
    valid = True
    command = extract_command(txt)
    print(Markdown(f"# {command}\n"))
    object_type = command.split(' ')[1].strip()
    object_action = command.split(' ')[0].strip()

    term_identifier = process_simple_attribute(txt, TERM_NAME_LABELS, "ERROR")

    print(Markdown(f"{pre_command} `{command}` for term:`{term_identifier}` with directive: `{directive}`"))

    output_format = process_simple_attribute(txt, OUTPUT_LABELS, "INFO")
    if output_format is None:
        output_format = "REPORT"
    else:
        output_format = output_format.upper()

    if output_format not in ["DICT", "REPORT"]:
        valid = False
        print_msg(ERROR, f"Invalid output format: `{output_format}`", debug_level)

    request_display = f"\n\t* Term Identifier: {term_identifier}\n\t* Output Format {output_format}"

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
            output = egeria_client.get_term_details(term_identifier, output_format=output_format)
            if output_format == "DICT":
                output = f"```{json.dumps(output, indent=4)}```"
            print_msg("ALWAYS", f"Wrote Term Details for term: `{term_identifier}`", debug_level)

            return output

        except Exception as e:
            print(f"{ERROR}Error performing {command}: {e}")
            console.print_exception(show_locals=True)
            return None
    else:
        return None


def process_term_history_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """ List terms as a markdown table. Filter based on optional search string. """
    set_debug_level(directive)
    valid = True
    command = extract_command(txt)
    print(Markdown(f"# {command}\n"))
    object_type = command.split(' ')[1].strip()
    object_action = command.split(' ')[0].strip()

    element_labels = TERM_NAME_LABELS
    element_labels.append('Display Name')

    term_name = process_simple_attribute(txt, element_labels, "ERROR")

    known_q_name, known_guid, valid, term_exists = process_element_identifiers(egeria_client, object_type,
                                                                               element_labels, txt, object_action, )

    print(Markdown(f"{pre_command} `{command}` for term:`{term_name}` with directive: `{directive}`"))

    output_format = process_simple_attribute(txt, OUTPUT_LABELS, "INFO")
    if output_format is None:
        output_format = "LIST"
    elif output_format not in ["DICT", "LIST"]:
        valid = False
        print_msg(ERROR, f"Invalid output format: `{output_format}`", debug_level)

    request_display = f"\n\t* Term Name: {term_name}\n\t* Output Format {output_format}\n\t* GUID: {known_guid}\n"

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
            if output_format == "DICT":
                struct = egeria_client.list_term_revision_history(known_guid, output_format=output_format)
                term_history_md += f"```{json.dumps(struct, indent=4)}```\n"
            else:
                term_history_md += egeria_client.list_full_term_history(known_guid, output_format)
            print_msg("ALWAYS", f"Wrote Term History for term `{term_name}`", debug_level)

            return term_history_md

        except Exception as e:
            print(f"{ERROR}Error performing {command}: {e}")
            console.print_exception(show_locals=True)
            return None
    else:
        return None


def process_term_revision_history_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[
    str]:
    """ List term revision history as a markdown table or list."""
    set_debug_level(directive)
    valid = True
    command = extract_command(txt)
    print(Markdown(f"# {command}\n"))
    object_type = command.split(' ')[1].strip()
    object_action = command.split(' ')[0].strip()
    known_q_name = None
    known_guid = None

    element_labels = TERM_NAME_LABELS

    term_name = process_simple_attribute(txt, element_labels, "ERROR")
    print(Markdown(f"{pre_command} `{command}` for term: `{term_name}` with directive: `{directive}` "))

    known_q_name, known_guid, valid, _ = process_element_identifiers(egeria_client, object_type, element_labels, txt,
                                                                     object_action, )
    output_format = process_simple_attribute(txt, ['Output Format', 'Format'], 'INFO')
    if output_format is None:
        output_format = "LIST"
    elif output_format not in ["DICT", "LIST", "MD"]:
        valid = False
        print_msg(ERROR, f"Invalid output format: `{output_format}`", debug_level)

    request_display = f"\n\t* Term Name: {term_name}\n\t* Output Format: {output_format}\n"

    if directive == "display":
        print(request_display)
        return None
    elif directive == "validate":
        print(request_display)
        return str(valid)
    elif directive == "process":
        try:
            print(request_display)
            if not valid:  # First validate the term before we process it
                return None
            term_history_md = f"\n# Term Revision History for `{term_name}`\n\n"
            if output_format == "DICT":
                struct = egeria_client.list_term_revision_history(known_guid, output_format)
                term_history_md += f"```{json.dumps(struct, indent=4)}```\n"
            else:
                term_history_md += egeria_client.list_term_revision_history(known_guid, output_format)
            print_msg("ALWAYS", f"Wrote Term Revision History for term `{term_name}`", debug_level)
            return term_history_md

        except Exception as e:
            print(f"{ERROR}Error performing {command}: {e}")
            console.print_exception(show_locals=True)
            return None
    else:
        return None
