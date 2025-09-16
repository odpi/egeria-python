"""
This file contains glossary-related object_action functions for processing Egeria Markdown
"""

import json
import os
import re
from typing import List, Optional
from loguru import logger
from rich import print
from rich.console import Console
from rich.markdown import Markdown

from md_processing.md_processing_utils.common_md_proc_utils import (parse_upsert_command, parse_view_command,
                                                                    sync_collection_memberships)
from md_processing.md_processing_utils.common_md_utils import update_element_dictionary, set_update_body, \
    set_element_status_request_body, set_element_prop_body, set_delete_request_body, set_rel_request_body, set_peer_gov_def_request_body, \
    set_rel_request_body, set_create_body, set_object_classifications, set_product_body, set_rel_prop_body

from md_processing.md_processing_utils.extraction_utils import (extract_command_plus, update_a_command)
from md_processing.md_processing_utils.md_processing_constants import (load_commands, ERROR)
from pyegeria import DEBUG_LEVEL, body_slimmer, to_pascal_case, PyegeriaException, print_basic_exception, print_exception_table
from pyegeria.egeria_tech_client import EgeriaTech



from md_processing.md_processing_utils.common_md_utils import (debug_level, print_msg, set_debug_level,
                                                               get_element_dictionary, update_element_dictionary,
                                                               )
from md_processing.md_processing_utils.extraction_utils import (extract_command_plus, extract_command,
                                                                process_simple_attribute, process_element_identifiers,
                                                                update_a_command, extract_attribute,
                                                                get_element_by_name, process_name_list)

from pyegeria import body_slimmer
from pyegeria._globals import (NO_GLOSSARIES_FOUND, NO_ELEMENTS_FOUND, NO_CATEGORIES_FOUND)
from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.utils import make_format_set_name_from_type


# EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "170"))
# console = Console(width=EGERIA_WIDTH)

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

    parsed_output = parse_upsert_command(egeria_client, object_type, object_action, txt, directive)
    if not parsed_output:
        logger.error(f"No output for `{object_action}`")
        return None

    valid = parsed_output['valid']
    exists = parsed_output['exists']

    qualified_name = parsed_output.get('qualified_name', None)
    guid = parsed_output.get('guid', None)

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']

    display_name = attributes['Display Name'].get('value', None)
    status = attributes.get('Status', {}).get('value', None)
    #

    if directive == "display":
        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
        return valid

    elif directive == "process":
        try:
            obj = "Glossary"
            #   Set the property body for a glossary collection
            #
            prop_body = set_element_prop_body(obj, qualified_name, attributes)
            prop_body["languager"] = attributes.get('Language', {}).get('value', None)
            prop_body["usage"] = attributes.get('Usage', {}).get('value', None)

            if object_action == "Update":
                if not exists:
                    msg = (f" Element `{display_name}` does not exist! Updating result document with Create "
                           f"{object_action}\n")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif not valid:
                    return None
                else:
                    print(Markdown(
                        f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))


                body = set_update_body(obj, attributes)
                body['properties'] = prop_body

                egeria_client.update_collection(guid, body)
                if status:
                    egeria_client.update_collection_status(guid, status)

                logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}\n\n___")
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                return egeria_client.get_collection_by_guid(guid, element_type='Glossary',
                                                            output_format='MD', output_format_set = "DrE-Glossary")


            elif object_action == "Create":
                if valid is False and exists:
                    msg = (f"  Digital Product `{display_name}` already exists and result document updated changing "
                           f"`Create` to `Update` in processed output\n\n___")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)

                else:
                    body = set_create_body(object_type,attributes)

                    # if this is a root or folder (maybe more in the future), then make sure that the classification is set.
                    body["initialClassifications"] = set_object_classifications(object_type, attributes, ["Taxonomy", "CanonicalVocabulary"])
                    if object_type == "Taxonomy":
                        body["initialClassifications"]['Taxonomy']['organizingPrinciple'] = attributes.get('Organizing Principle', {}).get('value', None)
                    elif object_type == "CanonicalVocabulary":
                        body["initialClassifications"]['CanonicalVocabulary']['usage'] = attributes.get('Usage', {}).get('value', None)

                    body["properties"] = prop_body

                    guid = egeria_client.create_collection(body = body)
                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        msg = f"Created Element `{display_name}` with GUID {guid}\n\n___"
                        logger.success(msg)
                        return egeria_client.get_collection_by_guid(guid, obj, output_format='MD')
                    else:
                        msg = f"Failed to create element `{display_name}` with GUID {guid}\n\n___"
                        logger.error(msg)
                        return None

        except PyegeriaException as e:
            logger.error(f"Pyegeria error performing {command}: {e}")
            print_basic_exception(e)
            return None
        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
    else:
        return None


def process_category_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    pass
#     """
#     Processes a glossary category create or update object_action by extracting key attributes such as
#     category name, qualified, description, and anchor glossary from the given txt..
#
#     :param txt: A string representing the input cell to be processed for
#         extracting category-related attributes.
#     :param directive: an optional string indicating the directive to be used - display, validate or execute
#     :return: A string summarizing the outcome of the processing.
#     """
#     valid = True
#     set_debug_level(directive)
#
#     command, object_type, object_action = extract_command_plus(txt)
#     print(Markdown(f"# {command}\n"))
#
#     category_name = process_simple_attribute(txt, ['Category Name', 'category_name', 'Cat'])
#     print(Markdown(f"{pre_command} `{command}` for category: `\'{category_name}\'` with directive: `{directive}` "))
#
#     owning_glossary_name = extract_attribute(txt, ['Owning Glossary', 'In Glossary'])
#     description = process_simple_attribute(txt, ['Description'])
#     q_name = process_simple_attribute(txt, ['Qualified Name'])
#
#     parent_category_name = process_simple_attribute(txt, PARENT_CATEGORY_LABELS, "INFO")
#
#     element_labels = CATEGORY_NAME_LABELS
#     element_labels.append('Display Name')
#     # Check if category exists (and get qname and guid)
#     if category_name is None:
#         valid = False
#         known_q_name, known_guid, category_exists = None
#     else:
#         element_labels = CATEGORY_NAME_LABELS
#         element_labels.append('Display Name')
#         known_q_name, known_guid, valid, category_exists = process_element_identifiers(egeria_client, object_type,
#                                                                                        element_labels, txt,
#                                                                                        object_action, None)
#
#     # Check if owning glossary exists (and get qname)
#     if owning_glossary_name is None:
#         valid = False
#         known_glossary_q_name, known_glossary__guid, glossary_exists = None
#
#     else:
#         known_glossary_q_name, known_glossary_guid, valid, owning_glossary_exists = process_element_identifiers(
#             egeria_client, "Glossary", GLOSSARY_NAME_LABELS, txt, EXISTS_REQUIRED, None)
#
#     if parent_category_name:
#         _, parent_guid, parent_valid, parent_exists = get_element_by_name(egeria_client, 'Glossary Categories',
#                                                                           parent_category_name)
#     else:
#         parent_guid = None
#         parent_exists = False
#         parent_valid = False
#
#     category_display = (
#         f"\n* Command: {command}\n\t* Category: {category_name}\n\t* In Glossary: {owning_glossary_name}\n\t"
#         f"* Description:\n{description}\n\t* Parent Category: {parent_category_name}\n\t"
#         f"* Qualified Name: {q_name}\n\t")
#
#     if object_action == 'Update':
#         guid = process_simple_attribute(txt, ['GUID', 'guid', 'Guid'])
#
#         category_display += (f"* GUID: {guid}\n\n")
#         if not category_exists:
#             msg = f"Category {category_name} can't be updated; {category_name} not found."
#             print_msg(ERROR, msg, debug_level)
#             valid = False
#         else:
#             msg = f"Glossary can be updated; {category_name} found"
#             print_msg(ALWAYS, msg, debug_level)
#
#     elif object_action == "Create":
#         if category_exists:
#             msg = f"Category {category_name} can't be created because it already exists.\n"
#             print_msg("ERROR", msg, debug_level)
#             valid = False
#         elif valid:
#             msg = f"It is valid to create Category `{category_name}` with:\n"
#             print_msg("ALWAYS", msg, debug_level)
#
#     if directive == "display":
#         print(Markdown(category_display))
#         return None
#
#     elif directive == "validate":
#         if valid:
#             print(Markdown(category_display))
#         else:
#             msg = f"Validation failed for {object_type} `{category_name}`\n"
#             print_msg(ERROR, msg, debug_level)
#             print(Markdown(category_display))
#         return valid
#
#     elif directive == "process":
#         if valid:
#             print(Markdown(category_display))
#         else:
#             if category_exists and object_action == "Create":
#                 msg = (f"Create failed because category `{category_name}` exists - changing `Create` to `Update` in "
#                        f"processed output \n")
#                 print_msg(ERROR, msg, debug_level)
#                 print(Markdown(category_display))
#                 return update_a_command(txt, object_action, object_type, known_q_name, known_guid)
#             else:
#                 return None
#
#         if object_action == "Update":
#             if not category_exists:
#                 print(f"\n{ERROR}category `{category_name}` does not exist! Updating result document with Create "
#                       f"object_action\n")
#                 return update_a_command(txt, object_action, object_type, known_q_name, known_guid)
#
#             # Update the basic category properties
#             egeria_client.update_category(known_guid, category_name, description, known_q_name, None)
#             msg = f"->Updated category `{category_name}`with GUID {known_guid}"
#             print_msg(ALWAYS, msg, debug_level)
#
#             # Update parent-child relationships
#
#             update_element_dictionary(known_q_name, {
#                 'guid': known_guid, 'display_name': category_name
#                 })
#
#             category_sync = update_category_parent(egeria_client, known_guid, parent_category_name)
#             print_msg(ALWAYS, f"Updated Category hierarchy for  `{category_name}` with outcome {category_sync}",
#                       debug_level)
#             return egeria_client.get_category_by_guid(known_guid, output_format='FORM')
#
#         elif object_action == "Create":
#             is_root = True
#
#             if category_exists:
#                 msg = (f"Cannot create`{category_name}` because it already exists; result document written for "
#                        f"category update\n")
#                 print_msg(WARNING, msg, debug_level)
#                 return update_a_command(txt, object_action, object_type, known_q_name, known_guid)
#             else:
#                 category_guid = egeria_client.create_category(known_glossary_guid, category_name, description, is_root)
#                 category_details = egeria_client.get_category_by_guid(category_guid)
#
#                 if category_details == NO_CATEGORIES_FOUND:
#                     msg = f"Just created category with GUID {category_guid} but category not found"
#                     print_msg(ERROR, msg, debug_level)
#                     return None
#
#                 qualified_name = category_details['glossaryCategoryProperties']["qualifiedName"]
#                 update_element_dictionary(qualified_name, {
#                     'guid': category_guid, 'display_name': category_name
#                     })
#                 print_msg(ALWAYS, f"Created Category `{category_name}` with GUID {category_guid}", debug_level)
#                 if parent_valid and parent_guid:
#                     egeria_client.set_parent_category(parent_guid, category_guid)
#                     print_msg(ALWAYS, f"Set parent category for `{category_name}` to `{parent_category_name}`",
#                               debug_level)
#                 else:
#                     print_msg(ERROR,
#                               f"Parent category `{parent_category_name}` not found or invalid for `{category_name}`",
#                               debug_level)
#                 return egeria_client.get_category_by_guid(category_guid, output_format='FORM')
#         return None
#     return None
#
#
def update_category_parent(egeria_client, category_guid: str, parent_category_name: str = None) -> bool:
    pass
#     """
#     Updates the parent relationship for a category.
#
#     If a parent category is specified, it will check if a parent is currently set.
#     If a parent category was set and is the same as the parent category specified, no change is needed.
#     If a parent category was set and is different from the parent_category_name, the parent category is updated.
#     If parent_category_name is None or empty and an existing parent category was set, the parent category is removed.
#
#     Parameters
#     ----------
#     egeria_client: EgeriaTech
#         The Egeria client to use for API calls
#     category_guid: str
#         The GUID of the category to update
#     parent_category_name: str, optional
#         The name of the parent category to set, or None to remove the parent
#
#     Returns
#     -------
#
#     True if successful, False otherwise.
#
#     """
#     outcome = True
#     # Handle parent category updates
#     if parent_category_name:
#         # Check if a parent is currently set
#         current_parent = egeria_client.get_category_parent(category_guid)
#
#         if isinstance(current_parent, str) and "No Parent Category found" in current_parent:
#             # No parent currently set, need to set it
#             _, parent_guid, _, parent_exists = get_element_by_name(egeria_client, 'Glossary Categories',
#                                                                    parent_category_name)
#
#             if parent_exists and parent_guid:
#                 egeria_client.set_parent_category(parent_guid, category_guid)
#                 print_msg(ALWAYS, f"Set parent category of category to `{parent_category_name}`", debug_level)
#             else:
#                 print_msg(ERROR, f"Parent category `{parent_category_name}` not found", debug_level)
#                 outcome = False
#         else:
#             # Parent is set, check if it's the same
#             current_parent_name = current_parent.get('glossaryCategoryProperties', {}).get('qualifiedName', '')
#
#             if current_parent_name != parent_category_name:
#                 # Different parent, need to update
#                 # First remove the current parent
#                 current_parent_guid = current_parent.get('elementHeader', {}).get('guid', '')
#                 if current_parent_guid:
#                     egeria_client.remove_parent_category(current_parent_guid, category_guid)
#
#                 # Then set the new parent
#                 _, parent_guid, _, parent_exists = get_element_by_name(egeria_client, 'Glossary Categories',
#                                                                        parent_category_name)
#
#                 if parent_exists and parent_guid:
#                     egeria_client.set_parent_category(parent_guid, category_guid)
#                     print_msg(ALWAYS,
#                               f"Updated parent category from `{current_parent_name}` to `{parent_category_name}`",
#                               debug_level)
#                 else:
#                     print_msg(ERROR, f"Parent category `{parent_category_name}` not found", debug_level)
#                     outcome = False
#     elif parent_category_name is None or parent_category_name == '':
#         # Check if a parent is currently set and remove it if needed
#         current_parent = egeria_client.get_category_parent(category_guid)
#
#         if not isinstance(current_parent, str) or "No Parent Category found" not in current_parent:
#             # Parent is set, need to remove it
#             current_parent_guid = current_parent.get('elementHeader', {}).get('guid', '')
#             current_parent_name = current_parent.get('glossaryCategoryProperties', {}).get('qualifiedName', '')
#
#             if current_parent_guid:
#                 egeria_client.remove_parent_category(current_parent_guid, category_guid)
#                 print_msg(ALWAYS, f"Removed parent category `{current_parent_name}`", debug_level)
#
#     return outcome


def process_term_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    pass
    """
    Processes a term create or update object_action by extracting key attributes such as
    term name, summary, description, abbreviation, examples, usage, version, and status from the given cell.

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """

    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))

    parsed_output = parse_upsert_command(egeria_client, object_type, object_action, txt, directive)
    if not parsed_output:
        logger.error(f"No output for `{object_action}`")
        return None

    valid = parsed_output['valid']
    exists = parsed_output['exists']

    qualified_name = parsed_output.get('qualified_name', None)
    guid = parsed_output.get('guid', None)

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']

    display_name = attributes['Display Name'].get('value', None)
    status = attributes.get('Status', {}).get('value', None)
    merge_update = attributes.get('Merge Update', {}).get('value', True)
    #

    if directive == "display":
        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
        return valid

    elif directive == "process":
        try:
            obj = "GlossaryTerm"
            #   Set the property body for a glossary collection
            #
            prop_body = set_element_prop_body(obj, qualified_name, attributes)
            prop_body["aliases"] = attributes.get('Aliases', {}).get('value', None)
            prop_body["summary"] = attributes.get('Summary', {}).get('value', None)
            prop_body["examples"] = attributes.get('Examples', {}).get('value', None)
            prop_body["abbreviation"] = attributes.get('Abbreviation', {}).get('value', None)
            prop_body["usage"] = attributes.get('Usage', {}).get('value', None)
            prop_body["user_defined_status"] = attributes.get('UserDefinedStatus', {}).get('value', None)
            to_be_collection_guids = [attributes.get("Glossary", {}).get("guid", {}),
                                      attributes.get("Folder", {}).get("guid_list", {})]
            glossary_guid = attributes.get("Glossary", {}).get('guid', None)
            anchor_scope_guid = attributes.get("Anchor Scope", {}).get('guid', None)


            get_method = egeria_client.get_term_by_guid
            collection_types = ["Glossary", "Folder"]

            output_set = make_format_set_name_from_type(object_type)

            if object_action == "Update":
                if not exists:
                    msg = (f" Element `{display_name}` does not exist! Updating result document with Create "
                           f"{object_action}\n")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif not valid:
                    return None
                else:
                    print(Markdown(
                        f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))

                body = set_update_body(obj, attributes)
                body['properties'] = prop_body

                egeria_client.update_glossary_term(guid, body)
                if status:
                    egeria_client.update_term_status(guid, status)
                get_method = egeria_client.get_term_by_guid
                collection_types = ["Glossary", "Folder"]

                sync_collection_memberships(egeria_client, guid, get_method,  collection_types,
                                            to_be_collection_guids, merge_update)
                logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}\n\n___")
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                return egeria_client.get_term_by_guid(guid, element_type='GlossaryTerm',
                                                            output_format='MD', output_format_set=output_set)


            elif object_action == "Create":
                if valid is False and exists:
                    msg = (f"  Digital Product `{display_name}` already exists and result document updated changing "
                           f"`Create` to `Update` in processed output\n\n___")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)

                else:
                    body = set_create_body(obj,attributes)

                    # if this is a root or folder (maybe more in the future), then make sure that the classification is set.

                    body["properties"] = prop_body
                    # If the anchor scope is not already set and a glossary is specified
                    if anchor_scope_guid is None and glossary_guid:
                        body["anchorScopeGUID"] = glossary_guid

                    guid = egeria_client.create_glossary_term(body = body)
                    if guid:
                        sync_collection_memberships(egeria_client, guid, get_method,
                                                    collection_types, to_be_collection_guids, True)
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        msg = f"Created Element `{display_name}` with GUID {guid}\n\n___"
                        logger.success(msg)
                        return egeria_client.get_term_by_guid(guid, obj, output_format='MD', output_format_set=output_set)
                    else:
                        msg = f"Failed to create element `{display_name}` with GUID {guid}\n\n___"
                        logger.error(msg)
                        return None

        except PyegeriaException as e:
            logger.error(f"Pyegeria error performing {command}: {e}")
            print_basic_exception(e)
            return None
        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
    else:
        return None

def process_link_term_term_relationship_command(egeria_client: EgeriaTech, txt: str,
                                                  directive: str = "display") -> Optional[str]:
    """ Relate two terms through the specified relationship. ."""
    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))

    parsed_output = parse_view_command(egeria_client, object_type, object_action, txt, directive)

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']
    term1_guid = attributes.get('Term 1', {}).get('guid', None)
    term1_qname = attributes.get('Term 1', {}).get('qualified_name', None)
    term2_guid = attributes.get('Term 2', {}).get('guid', None)
    term2_qname = attributes.get('Term 2', {}).get('qualified_name', None)
    relationship = attributes.get('Relationship', {}).get('value', None)
    expression = attributes.get('Expression', {}).get('value', None)
    confidence = attributes.get('Confidence', {}).get('value', None)
    status = attributes.get('Status', {}).get('value', None)
    steward = attributes.get('Steward', {}).get('value', None)
    source = attributes.get('Source', {}).get('value', None)



    valid = parsed_output['valid']
    exists = term1_guid is not None and term2_guid is not None

    if not (valid and exists):
        valid = False

    if directive == "display":
        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
        return valid

    elif directive == "process":
        prop_body = set_rel_prop_body("GlossaryTerm", attributes)
        prop_body['expression'] = expression
        prop_body['confidence'] = confidence
        prop_body['status'] = status
        prop_body['steward'] = steward
        prop_body['source'] = source

        try:

            if not valid:  # First validate the term before we process it
                return None

            if object_action == "Link":
                if not exists:
                    msg = f"  Term `{term1_guid}` or {term2_guid} does not exist! "
                    logger.error(msg)
                    return None
                else:
                    print(Markdown(
                        f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))
            body = set_rel_request_body(relationship, prop_body)
            body['properties'] = prop_body
            body = body_slimmer(body)
            # todo removing body for now since don't know relationship properties class
            egeria_client.add_relationship_between_terms(term1_guid, term2_guid, relationship)
            logger.success(f"Created  `{relationship}` relationship between `{term1_qname}` and `{term2_qname}`\n\n___")
            update_md = (f"\n\n# Update Term-Term Relationship\n\n## Term 1 Name:\n\n{term1_qname}"
                         f"\n\n## Term 2 Name\n\n{term2_qname}\n\n## Term Relationship:\n\n{relationship}")
            return update_md


        except Exception as e:
            print(f"{ERROR}Error performing {command}: {e}")
            print_basic_exception(e)
            return None
            return None
    else:
        return None


