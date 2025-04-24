"""
This file contains term-related command functions for processing Egeria Markdown
"""
import re
from typing import Optional, List

from rich.markdown import Markdown
from rich.console import Console

from pyegeria.egeria_tech_client import EgeriaTech
from md_processing.utils.common_utils import (
    debug_level, print_msg, ALWAYS, ERROR, INFO, WARNING, pre_command, EXISTS_REQUIRED
)
from md_processing.utils.extraction_utils import (
    extract_command, process_simple_attribute, process_name_list
)
from md_processing.utils.validation_utils import (
    process_element_identifiers, update_a_command
)
from md_processing.utils.display_utils import (
    GLOSSARY_NAME_LABELS, CATEGORY_NAME_LABELS, TERM_NAME_LABELS, OUTPUT_LABELS, ELEMENT_OUTPUT_FORMATS, 
    SEARCH_LABELS, GUID_LABELS, TERM_RELATIONSHPS
)
from pyegeria.dr_egeria_state import update_element_dictionary

def update_term_categories(egeria_client: EgeriaTech, term_guid: str, current_categories: List[str], new_categories: List[str]) -> None:
    """
    Updates the categories of a term.

    Args:
        egeria_client: The Egeria client to use for the update.
        term_guid: The GUID of the term to update.
        current_categories: The current categories of the term.
        new_categories: The new categories of the term.
    """
    if new_categories:  # If categories are specified, add them
        for cat in new_categories:
            if cat not in current_categories:
                egeria_client.add_term_to_category(term_guid, cat)
                msg = f"Added term {term_guid} to category {cat}"
                print_msg("DEBUG-INFO", msg, debug_level)
        # Remove any categories that are not in the new list
        for cat in current_categories:
            if cat not in new_categories:
                egeria_client.remove_term_from_category(term_guid, cat)
                msg = f"Removed term {term_guid} from category {cat}"
                print_msg("DEBUG-INFO", msg, debug_level)
    else:  # No categories specified - so remove any categories a term is in
        for cat in current_categories:
            egeria_client.remove_term_from_category(term_guid, cat)
            msg = f"Removed term {term_guid} from category {cat}"
            print_msg("DEBUG-INFO", msg, debug_level)


def process_term_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a term create or update command by extracting key attributes such as
    term name, summary, description, abbreviation, examples, usage, version, and status from the given cell.

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    from md_processing.utils.common_utils import set_debug_level

    valid = True
    categories_list = None
    cats_exist = False
    set_debug_level(directive)
    known_q_name = None
    command = extract_command(txt)
    object_type = command.split(' ')[1].strip()
    object_action = command.split(' ')[0].strip()

    term_name = process_simple_attribute(txt, ['Term Name', 'Display Name'], ERROR)
    print(Markdown(f"{pre_command} `{command}` for term:`{term_name}` with directive: `{directive}`"))
    summary = process_simple_attribute(txt, ['Summary'],INFO)
    description = process_simple_attribute(txt, ['Description'], INFO)
    abbreviation = process_simple_attribute(txt, ['Abbreviation'], INFO)
    examples = process_simple_attribute(txt, ['Examples'], INFO)
    usage = process_simple_attribute(txt, ['Usage'], INFO)
    status = process_simple_attribute(txt, ['Status'])
    status = status.upper() if status else 'DRAFT'
    version = process_simple_attribute(txt, ['Version', "Version Identifier", "Published Version"], INFO)
    q_name = process_simple_attribute(txt, ['Qualified Name'], INFO)

    aliases = process_simple_attribute(txt, ['Aliases','Alias'], INFO)
    if aliases:
        alias_list = list(filter(None, re.split(r'[,\n]+', aliases.strip())))
    else:
        alias_list = None


    # validate term name and get existing qualified_name and guid if they exist
    if term_name is None:
        valid = False
        known_q_name, known_guid, term_exists = None, None, False
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

    # process categories, if present
    categories = process_simple_attribute(txt, ['Glossary Categories', 'Glossary Category', 'Category', 'Categories'])
    if categories:  # Find information about categoriess that classify this term
        msg = "Checking for categories that classify this term"
        print_msg("DEBUG-INFO", msg, debug_level)
        categories_list, cat_q_name_list, cats_valid, cats_exist = process_name_list(egeria_client, 'Glossary Categories',
                                                                                   txt, CATEGORY_NAME_LABELS)
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

    elif object_action == 'Create':  # if the command is create, check that it doesn't already exist
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
        if valid:
            print(Markdown(term_display))
        else:
            msg = f"Validation failed for Term `{term_name}`\n"
            print_msg(ERROR, msg, debug_level)
            print(Markdown(term_display))
        return valid
    elif directive == "process":
        if valid:
            print(Markdown(term_display))
        else:
            if term_exists and object_action == "Create":
                msg = f"Create failed because term `{term_name}` exists - changing `Create` to `Update` in processed output \n"
                print_msg(ERROR, msg, debug_level)
                print(Markdown(term_display))
                return update_a_command(txt, command, object_type, known_q_name, known_guid)
            else:
                return None

        try:
            if object_action == "Update":
                if not term_exists:
                    print(f"\n{ERROR}Term `{term_name}` does not exist! Updating result document with Create "
                          f"command\n")
                    return update_a_command(txt, command, object_type, known_q_name, known_guid)

                body = {
                    "class": "ReferenceableRequestBody", "elementProperties": {
                        "class": "GlossaryTermProperties", "qualifiedName": known_q_name, "summary": summary,
                        "description": description, "abbreviation": abbreviation, "examples": examples,
                        "usage": usage, "status": status
                        }
                    }
                egeria_client.update_term(known_guid, body)
                print_msg(ALWAYS, f"Updated Term `{term_name}` with GUID {known_guid}", debug_level)
                update_element_dictionary(known_q_name, {
                    'guid': known_guid, 'display_name': term_name
                    })

                # Update categories if specified
                if categories:
                    # Get the current categories
                    term_details = egeria_client.get_term_by_guid(known_guid)
                    current_categories = []
                    if 'categories' in term_details:
                        for cat in term_details['categories']:
                            current_categories.append(cat.get('guid', None))
                    # Update the categories
                    update_term_categories(egeria_client, known_guid, current_categories, cat_q_name_list)

                # Update aliases if specified
                if alias_list:
                    # Get the current aliases
                    term_details = egeria_client.get_term_by_guid(known_guid)
                    current_aliases = term_details.get('aliases', [])
                    # Add new aliases
                    for alias in alias_list:
                        if alias not in current_aliases:
                            egeria_client.add_term_alias(known_guid, alias)
                    # Remove aliases that are not in the new list
                    for alias in current_aliases:
                        if alias not in alias_list:
                            egeria_client.remove_term_alias(known_guid, alias)

                return egeria_client.get_term_by_guid(known_guid, output_format='MD')

            elif object_action == "Create":
                if term_exists:
                    print(f"\nTerm `{term_name}` already exists and result document updated\n")
                    return update_a_command(txt, command, object_type, known_q_name, known_guid)
                else:
                    term_guid = egeria_client.create_term(term_name, summary, description, glossary_name=glossary_name,
                                                         status=status, abbreviation=abbreviation, examples=examples,
                                                         usage=usage, aliases=alias_list)
                    if term_guid:
                        print_msg(ALWAYS, f"Created Term `{term_name}` with GUID {term_guid}", debug_level)
                        # Add categories if specified
                        if categories and cats_exist and cats_valid:
                            update_term_categories(egeria_client, term_guid, [], cat_q_name_list)
                        return egeria_client.get_term_by_guid(term_guid, output_format='MD')
                    else:
                        print_msg(ERROR, f"Failed to create Term `{term_name}`", debug_level)
                        return None

        except Exception as e:
            print(f"{ERROR}Error performing {command}: {e}")
            Console().print_exception(show_locals=True)
            return None
    else:
        return None


def process_create_term_term_relationship_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a term-term relationship create command by extracting key attributes such as
    term names and relationship type from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting term relationship attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    from md_processing.utils.common_utils import set_debug_level

    command = extract_command(txt)
    set_debug_level(directive)
    print(Markdown(f"{pre_command} `{command}` with directive: `{directive}`"))

    # Get the terms involved in the relationship
    from_term_name = process_simple_attribute(txt, ['From Term', 'From Term Name'], ERROR)
    to_term_name = process_simple_attribute(txt, ['To Term', 'To Term Name'], ERROR)
    relationship_type = process_simple_attribute(txt, ['Relationship Type'], ERROR)

    if from_term_name is None or to_term_name is None or relationship_type is None:
        print_msg(ERROR, "Missing required attributes for term-term relationship", debug_level)
        return None

    # Validate the relationship type
    if relationship_type not in TERM_RELATIONSHPS:
        print_msg(ERROR, f"Invalid relationship type: {relationship_type}", debug_level)
        print_msg(INFO, f"Valid relationship types: {', '.join(TERM_RELATIONSHPS)}", debug_level)
        return None

    # Get the term GUIDs
    from_term_q_name, from_term_guid, from_term_valid, from_term_exists = process_element_identifiers(
        egeria_client, "Term", TERM_NAME_LABELS, txt, EXISTS_REQUIRED, None)
    to_term_q_name, to_term_guid, to_term_valid, to_term_exists = process_element_identifiers(
        egeria_client, "Term", TERM_NAME_LABELS, txt, EXISTS_REQUIRED, None)

    if not from_term_exists or not to_term_exists:
        print_msg(ERROR, "One or both terms do not exist", debug_level)
        return None

    relationship_display = (f"\n* Command: {command}\n\t* From Term: {from_term_name}\n\t"
                           f"* To Term: {to_term_name}\n\t* Relationship Type: {relationship_type}\n")

    if directive == "display":
        print(Markdown(relationship_display))
        return None
    elif directive == "validate":
        print(Markdown(relationship_display))
        return True
    elif directive == "process":
        print(Markdown(relationship_display))
        try:
            # Check if the relationship already exists
            term_relationships = egeria_client.get_term_relationships(from_term_guid)
            for rel in term_relationships:
                if rel.get('end2', {}).get('guid', '') == to_term_guid and rel.get('type', {}).get('name', '') == relationship_type:
                    print_msg(WARNING, f"Relationship already exists between {from_term_name} and {to_term_name}", debug_level)
                    return None

            # Create the relationship
            result = egeria_client.create_term_relationship(from_term_guid, to_term_guid, relationship_type)
            if result:
                print_msg(ALWAYS, f"Created relationship between {from_term_name} and {to_term_name}", debug_level)
                return egeria_client.get_term_by_guid(from_term_guid, output_format='MD')
            else:
                print_msg(ERROR, f"Failed to create relationship between {from_term_name} and {to_term_name}", debug_level)
                return None
        except Exception as e:
            print_msg(ERROR, f"Error creating term relationship: {e}", debug_level)
            Console().print_exception(show_locals=True)
            return None


def process_term_list_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a term list command by extracting key attributes such as
    glossary name, output format, and search string from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting term-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    from md_processing.utils.common_utils import set_debug_level

    command = extract_command(txt)
    set_debug_level(directive)
    print(Markdown(f"{pre_command} `{command}` with directive: `{directive}`"))

    glossary_name = process_simple_attribute(txt, GLOSSARY_NAME_LABELS)
    category_name = process_simple_attribute(txt, CATEGORY_NAME_LABELS)
    output_format = process_simple_attribute(txt, OUTPUT_LABELS)
    output_format = output_format.upper() if output_format else "MD"
    if output_format not in ELEMENT_OUTPUT_FORMATS:
        print_msg(WARNING, f"Output format {output_format} not recognized, using MD", debug_level)
        output_format = "MD"

    search_string = process_simple_attribute(txt, SEARCH_LABELS)

    known_glossary_guid = None
    known_category_guid = None

    if glossary_name:
        known_glossary_q_name, known_glossary_guid, glossary_valid, glossary_exists = process_element_identifiers(
            egeria_client, "Glossary", GLOSSARY_NAME_LABELS, txt, EXISTS_REQUIRED, None)
        if not glossary_exists:
            print_msg(ERROR, f"Glossary {glossary_name} not found", debug_level)
            return None

    if category_name:
        known_category_q_name, known_category_guid, category_valid, category_exists = process_element_identifiers(
            egeria_client, "Category", CATEGORY_NAME_LABELS, txt, EXISTS_REQUIRED, None)
        if not category_exists:
            print_msg(ERROR, f"Category {category_name} not found", debug_level)
            return None

    if directive == "display":
        print(Markdown(f"\n* Command: {command}\n\t* Glossary Name: {glossary_name}\n\t* Category Name: {category_name}\n\t* Output Format: {output_format}\n\t* Search String: {search_string}"))
        return None
    elif directive == "validate":
        print(Markdown(f"\n* Command: {command}\n\t* Glossary Name: {glossary_name}\n\t* Category Name: {category_name}\n\t* Output Format: {output_format}\n\t* Search String: {search_string}"))
        return True
    elif directive == "process":
        print(Markdown(f"\n* Command: {command}\n\t* Glossary Name: {glossary_name}\n\t* Category Name: {category_name}\n\t* Output Format: {output_format}\n\t* Search String: {search_string}"))
        if category_name and category_exists:
            return egeria_client.list_terms_for_category(known_category_guid, output_format=output_format, search_string=search_string)
        elif glossary_name and glossary_exists:
            return egeria_client.list_terms_for_glossary(known_glossary_guid, output_format=output_format, search_string=search_string)
        else:
            return egeria_client.list_terms(output_format=output_format, search_string=search_string)


def process_term_details_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a term details command by extracting key attributes such as
    term name and output format from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting term-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    from md_processing.utils.common_utils import set_debug_level

    command = extract_command(txt)
    set_debug_level(directive)
    print(Markdown(f"{pre_command} `{command}` with directive: `{directive}`"))

    term_name = process_simple_attribute(txt, TERM_NAME_LABELS, ERROR)
    output_format = process_simple_attribute(txt, OUTPUT_LABELS)
    output_format = output_format.upper() if output_format else "MD"
    if output_format not in ELEMENT_OUTPUT_FORMATS:
        print_msg(WARNING, f"Output format {output_format} not recognized, using MD", debug_level)
        output_format = "MD"

    if term_name is None:
        print_msg(ERROR, "No term name found", debug_level)
        return None

    known_q_name, known_guid, valid, term_exists = process_element_identifiers(egeria_client, "Term",
                                                                              TERM_NAME_LABELS, txt,
                                                                              EXISTS_REQUIRED, None)
    if not term_exists:
        print_msg(ERROR, f"Term {term_name} not found", debug_level)
        return None

    if directive == "display":
        print(Markdown(f"\n* Command: {command}\n\t* Term Name: {term_name}\n\t* Output Format: {output_format}"))
        return None
    elif directive == "validate":
        print(Markdown(f"\n* Command: {command}\n\t* Term Name: {term_name}\n\t* Output Format: {output_format}"))
        return True
    elif directive == "process":
        print(Markdown(f"\n* Command: {command}\n\t* Term Name: {term_name}\n\t* Output Format: {output_format}"))
        return egeria_client.get_term_by_guid(known_guid, output_format=output_format)


def process_term_history_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a term history command by extracting key attributes such as
    term name and output format from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting term-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    from md_processing.utils.common_utils import set_debug_level

    command = extract_command(txt)
    set_debug_level(directive)
    print(Markdown(f"{pre_command} `{command}` with directive: `{directive}`"))

    term_name = process_simple_attribute(txt, TERM_NAME_LABELS, ERROR)
    output_format = process_simple_attribute(txt, OUTPUT_LABELS)
    output_format = output_format.upper() if output_format else "MD"
    if output_format not in ELEMENT_OUTPUT_FORMATS:
        print_msg(WARNING, f"Output format {output_format} not recognized, using MD", debug_level)
        output_format = "MD"

    if term_name is None:
        print_msg(ERROR, "No term name found", debug_level)
        return None

    known_q_name, known_guid, valid, term_exists = process_element_identifiers(egeria_client, "Term",
                                                                              TERM_NAME_LABELS, txt,
                                                                              EXISTS_REQUIRED, None)
    if not term_exists:
        print_msg(ERROR, f"Term {term_name} not found", debug_level)
        return None

    if directive == "display":
        print(Markdown(f"\n* Command: {command}\n\t* Term Name: {term_name}\n\t* Output Format: {output_format}"))
        return None
    elif directive == "validate":
        print(Markdown(f"\n* Command: {command}\n\t* Term Name: {term_name}\n\t* Output Format: {output_format}"))
        return True
    elif directive == "process":
        print(Markdown(f"\n* Command: {command}\n\t* Term Name: {term_name}\n\t* Output Format: {output_format}"))
        return egeria_client.get_term_history(known_guid, output_format=output_format)


def process_term_revision_history_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a term revision history command by extracting key attributes such as
    term name and output format from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting term-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    from md_processing.utils.common_utils import set_debug_level

    command = extract_command(txt)
    set_debug_level(directive)
    print(Markdown(f"{pre_command} `{command}` with directive: `{directive}`"))

    term_name = process_simple_attribute(txt, TERM_NAME_LABELS, ERROR)
    output_format = process_simple_attribute(txt, OUTPUT_LABELS)
    output_format = output_format.upper() if output_format else "MD"
    if output_format not in ELEMENT_OUTPUT_FORMATS:
        print_msg(WARNING, f"Output format {output_format} not recognized, using MD", debug_level)
        output_format = "MD"

    if term_name is None:
        print_msg(ERROR, "No term name found", debug_level)
        return None

    known_q_name, known_guid, valid, term_exists = process_element_identifiers(egeria_client, "Term",
                                                                              TERM_NAME_LABELS, txt,
                                                                              EXISTS_REQUIRED, None)
    if not term_exists:
        print_msg(ERROR, f"Term {term_name} not found", debug_level)
        return None

    if directive == "display":
        print(Markdown(f"\n* Command: {command}\n\t* Term Name: {term_name}\n\t* Output Format: {output_format}"))
        return None
    elif directive == "validate":
        print(Markdown(f"\n* Command: {command}\n\t* Term Name: {term_name}\n\t* Output Format: {output_format}"))
        return True
    elif directive == "process":
        print(Markdown(f"\n* Command: {command}\n\t* Term Name: {term_name}\n\t* Output Format: {output_format}"))
        return egeria_client.get_term_revision_history(known_guid, output_format=output_format)
