"""
This file contains category-related command functions for processing Egeria Markdown
"""
from typing import Optional

from rich.markdown import Markdown

from pyegeria.egeria_tech_client import EgeriaTech
from md_processing.utils.common_utils import (
    debug_level, print_msg, ALWAYS, ERROR, INFO, WARNING, pre_command, EXISTS_REQUIRED
)
from md_processing.utils.extraction_utils import (
    extract_command_plus, extract_command, process_simple_attribute
    )
from md_processing.utils.validation_utils import (
    process_element_identifiers, update_a_command
)
from md_processing.utils.display_utils import (
    GLOSSARY_NAME_LABELS, CATEGORY_NAME_LABELS, PARENT_CATEGORY_LABELS, OUTPUT_LABELS, ELEMENT_OUTPUT_FORMATS, SEARCH_LABELS
)
from pyegeria.dr_egeria_state import update_element_dictionary

def process_category_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a category create or update command by extracting key attributes such as
    category name, glossary name, description, and parent category from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting category-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    from md_processing.utils.common_utils import set_debug_level
    
    command, object_type, object_action = extract_command_plus(txt)
    set_debug_level(directive)

    category_name = process_simple_attribute(txt, CATEGORY_NAME_LABELS, ERROR)
    print(Markdown(f"{pre_command} `{object_action}` `{object_type}` for category: `\'{category_name}\'` with directive: `{directive}` "))
    description = process_simple_attribute(txt, ['Description'], INFO)
    q_name = process_simple_attribute(txt, ['Qualified Name'], INFO)
    valid = True

    if category_name is None:
        valid = False
        known_q_name = None
        known_guid = None
        category_exists = False
    else:
        element_labels = CATEGORY_NAME_LABELS
        element_labels.append('Display Name')
        known_q_name, known_guid, valid, category_exists = process_element_identifiers(egeria_client, object_type,
                                                                                      element_labels, txt,
                                                                                      object_action, None)

    # Get the glossary this category is in
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

    # Get the parent category if specified
    parent_category_name = process_simple_attribute(txt, PARENT_CATEGORY_LABELS)
    if parent_category_name:
        known_parent_q_name, known_parent_guid, parent_valid, parent_exists = process_element_identifiers(
            egeria_client, "Category", PARENT_CATEGORY_LABELS, txt, EXISTS_REQUIRED, None)
        if not parent_exists:
            valid = False
    else:
        known_parent_q_name = None
        known_parent_guid = None
        parent_valid = True
        parent_exists = False

    category_display = (f"\n* Command: `{command}`\n\t* Glossary: {glossary_name}\n\t"
                        f"* Category Name: {category_name}\n\t* Parent Category: {parent_category_name}\n\t"
                        f"* Description: {description}\n")

    if object_action == 'Update':
        guid = process_simple_attribute(txt, ['GUID', 'guid', 'Guid'])
        category_display += f"* Qualified Name: `{q_name}`\n\t* GUID: {guid}\n\n"
        if not category_exists:
            msg = f"Category can't be updated; `{category_name}` not found"
            print_msg("ERROR", msg, debug_level)
            valid = False
        else:
            msg = f"Category can be updated; `{category_name}` found"
            print_msg(ALWAYS, msg, debug_level)

    elif object_action == "Create":
        if category_exists:
            msg = f"Category `{category_name}` can't be created because it already exists.\n"
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
            msg = f"Validation failed for Category `{category_name}`\n"
            print_msg(ERROR, msg, debug_level)
            print(Markdown(category_display))

        return valid

    elif directive == "process":
        if valid:
            print(Markdown(category_display))
        else:
            if category_exists and object_action == "Create":
                msg = f"Create failed because category `{category_name}` exists - changing `Create` to `Update` in processed output \n"
                print_msg(ERROR, msg, debug_level)
                print(Markdown(category_display))
                return update_a_command(txt, command, object_type, known_q_name, known_guid)
            else:
                return None

        if object_action == "Update":
            if not category_exists:
                print(f"\n{ERROR}Category `{category_name}` does not exist! Updating result document with Create "
                      f"command\n")
                return update_a_command(txt, command, object_type, known_q_name, known_guid)

            body = {
                "class": "ReferenceableRequestBody", "elementProperties": {
                    "class": "GlossaryCategoryProperties", "qualifiedName": known_q_name, "description": description
                    }
                }
            egeria_client.update_category(known_guid, body)
            print_msg(ALWAYS, f"Updated Category `{category_name}` with GUID {known_guid}", debug_level)
            update_element_dictionary(known_q_name, {
                'guid': known_guid, 'display_name': category_name
                })

            # Update parent category if specified
            if parent_category_name and parent_exists:
                update_category_parent(egeria_client, known_guid, known_parent_guid, category_name, parent_category_name)

            return egeria_client.get_category_by_guid(known_guid, output_format='MD')

        elif object_action == "Create":
            if category_exists:
                print(f"\nCategory `{category_name}` already exists and result document updated\n")
                return update_a_command(txt, command, object_type, known_q_name, known_guid)
            else:
                category_guid = egeria_client.create_category(category_name, description, known_glossary_guid, known_parent_guid)
                if category_guid:
                    print_msg(ALWAYS, f"Created Category `{category_name}` with GUID {category_guid}", debug_level)
                    return egeria_client.get_category_by_guid(category_guid, output_format='MD')
                else:
                    print_msg(ERROR, f"Failed to create Category `{category_name}`", debug_level)
                    return None


def update_category_parent(egeria_client: EgeriaTech, category_guid: str, parent_guid: str, category_name: str, parent_name: str) -> Optional[str]:
    """
    Updates the parent category of a category.

    :param egeria_client: The Egeria client to use for the update.
    :param category_guid: The GUID of the category to update.
    :param parent_guid: The GUID of the parent category.
    :param category_name: The name of the category to update.
    :param parent_name: The name of the parent category.
    :return: A string summarizing the outcome of the processing.
    """
    try:
        # Get the current parent category
        category = egeria_client.get_category_by_guid(category_guid)
        if 'parentCategory' in category:
            current_parent_guid = category['parentCategory'].get('guid', None)
            if current_parent_guid and current_parent_guid != parent_guid:
                # Remove the current parent
                egeria_client.remove_parent_category(current_parent_guid, category_guid)
                print_msg(INFO, f"Removed current parent category from {category_name}", debug_level)

        # Add the new parent
        egeria_client.add_parent_category(parent_guid, category_guid)
        print_msg(ALWAYS, f"Added parent category {parent_name} to {category_name}", debug_level)
        return f"Updated parent category of {category_name} to {parent_name}"
    except Exception as e:
        print_msg(ERROR, f"Error updating parent category: {e}", debug_level)
        return None


def process_category_list_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a category list command by extracting key attributes such as
    glossary name, output format, and search string from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting category-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    from md_processing.utils.common_utils import set_debug_level
    
    command = extract_command(txt)
    set_debug_level(directive)
    print(Markdown(f"{pre_command} `{command}` with directive: `{directive}`"))

    glossary_name = process_simple_attribute(txt, GLOSSARY_NAME_LABELS)
    output_format = process_simple_attribute(txt, OUTPUT_LABELS)
    output_format = output_format.upper() if output_format else "MD"
    if output_format not in ELEMENT_OUTPUT_FORMATS:
        print_msg(WARNING, f"Output format {output_format} not recognized, using MD", debug_level)
        output_format = "MD"

    search_string = process_simple_attribute(txt, SEARCH_LABELS)

    if glossary_name:
        known_q_name, known_guid, valid, glossary_exists = process_element_identifiers(egeria_client, "Glossary",
                                                                                      GLOSSARY_NAME_LABELS, txt,
                                                                                      EXISTS_REQUIRED, None)
        if not glossary_exists:
            print_msg(ERROR, f"Glossary {glossary_name} not found", debug_level)
            return None

    if directive == "display":
        print(Markdown(f"\n* Command: {command}\n\t* Glossary Name: {glossary_name}\n\t* Output Format: {output_format}\n\t* Search String: {search_string}"))
        return None
    elif directive == "validate":
        print(Markdown(f"\n* Command: {command}\n\t* Glossary Name: {glossary_name}\n\t* Output Format: {output_format}\n\t* Search String: {search_string}"))
        return True
    elif directive == "process":
        print(Markdown(f"\n* Command: {command}\n\t* Glossary Name: {glossary_name}\n\t* Output Format: {output_format}\n\t* Search String: {search_string}"))
        if glossary_name and glossary_exists:
            return egeria_client.list_categories_for_glossary(known_guid, output_format=output_format, search_string=search_string)
        else:
            return egeria_client.list_categories(output_format=output_format, search_string=search_string)