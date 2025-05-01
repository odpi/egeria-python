"""
This file contains term-related command functions for processing Egeria Markdown
"""
import json
from typing import Optional
from rich.console import Console
from rich import print
from rich.markdown import Markdown

from md_processing import ERROR
from md_processing.md_processing_utils.common_md_proc_utils import parse_user_command
from md_processing.md_processing_utils.extraction_utils import (
    extract_command, extract_command_plus, update_a_command
    )
from md_processing.md_processing_utils.md_processing_constants import (
    load_commands, )
from pyegeria import DEBUG_LEVEL

from pyegeria.egeria_tech_client import EgeriaTech
import os

from md_processing.md_processing_utils.common_md_utils import print_msg, update_element_dictionary
from pyegeria.md_processing_utils import ALWAYS

print("Current working directory: ", os.getcwd())
load_commands('../../md_processing/commands.json')
debug_level = DEBUG_LEVEL

console = Console(width=int(200))

# def update_term_categories(egeria_client: EgeriaTech, term_guid: str, current_categories: List[str], new_categories: List[str]) -> None:
#     """
#     Updates the categories of a term.
#
#     Args:
#         egeria_client: The Egeria client to use for the update.
#         term_guid: The GUID of the term to update.
#         current_categories: The current categories of the term.
#         new_categories: The new categories of the term.
#     """
#     if new_categories:  # If categories are specified, add them
#         for cat in new_categories:
#             if cat not in current_categories:
#                 egeria_client.add_term_to_category(term_guid, cat)
#                 msg = f"Added term {term_guid} to category {cat}"
#                 print_msg("DEBUG-INFO", msg, debug_level)
#         # Remove any categories that are not in the new list
#         for cat in current_categories:
#             if cat not in new_categories:
#                 egeria_client.remove_term_from_category(term_guid, cat)
#                 msg = f"Removed term {term_guid} from category {cat}"
#                 print_msg("DEBUG-INFO", msg, debug_level)
#     else:  # No categories specified - so remove any categories a term is in
#         for cat in current_categories:
#             egeria_client.remove_term_from_category(term_guid, cat)
#             msg = f"Removed term {term_guid} from category {cat}"
#             print_msg("DEBUG-INFO", msg, debug_level)


def process_data_spec_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a data specification create or update command by extracting key attributes such as
    spec name, parent_guid, parent_relationship_type, parent_at_end_1, collection_type

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    from md_processing.md_processing_utils.common_md_utils import set_debug_level

    set_debug_level(directive)

    command, object_type, object_action = extract_command_plus(txt)


    parsed_output = parse_user_command(egeria_client, object_type, object_action, txt, directive)

    valid = parsed_output['valid']
    exists = parsed_output['exists']

    qualified_name = parsed_output.get('qualified_name', None)
    guid = parsed_output.get('guid', None)

    print(Markdown(parsed_output['display']))

    if directive == "display":

        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for command `{command}`\n"
        return valid

    elif directive == "process":
        print(json.dumps(parsed_output, indent=4))


        attributes = parsed_output['attributes']
        description = attributes['Description'].get('value', None)
        display_name = attributes['Display Name'].get('value', None)
        anchor_guid = attributes.get('Anchor ID', {}).get('guid', None)
        parent_guid = attributes.get('Parent ID', {}).get('guid', None)
        parent_relationship_type_name = attributes.get('Parent Relationship Type Name', {}).get('value', None)
        parent_at_end1 = attributes.get('Parent at End1', {}).get('value', None)

        anchor_scope_guid = attributes.get('Anchor Scope GUID', {}).get('value', None)
        is_own_anchor = attributes.get('Is Own Anchor', {}).get('value', None)
        collection_ordering = "NAME"
        order_property_name = "Something"
        collection_type = object_type
        replace_all_props = True

        if not valid:
            return None

        try:
            if object_action == "Update":
                if not exists:
                    print(f"\n{ERROR}Element `{display_name}` does not exist! Updating result document with Create "
                          f"command\n")
                    return update_a_command(txt, command, object_type, qualified_name, guid)


                egeria_client.update_collection(guid, qualified_name, display_name,
                                                description, collection_type,
                                                collection_ordering, order_property_name,
                                                replace_all_props)
                print_msg(ALWAYS, f"Updated  {object_type} `{display_name}` with GUID {guid}", debug_level)
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                return egeria_client.get_collection_by_guid(guid, )

            elif object_action == "Create":
                if exists:
                    print(f"\nData Specication `{display_name}` already exists and result document updated changing `Create` to `Update` in processed output\n")
                    return update_a_command(txt, command, object_type, qualified_name, guid)
                else:
                    guid = egeria_client.create_data_spec_collection(anchor_guid, parent_guid, parent_relationship_type_name,
                                                                     parent_at_end1, display_name, description,
                                                                     collection_type, anchor_scope_guid, is_own_anchor,
                                                                     collection_ordering, order_property_name, qualified_name)
                    if guid:
                        print_msg(ALWAYS, f"Created Element `{display_name}` with GUID {guid}", debug_level)


                        return egeria_client.get_collection_by_guid(guid)
                    else:
                        print_msg(ERROR, f"Failed to create Term `{display_name}`", debug_level)
                        return None

        except Exception as e:
            print(f"{ERROR}Error performing {command}: {e}")
            Console().print_exception(show_locals=True)
            return None
    else:
        return None


# def process_data_structure_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
#     """
#     Processes a data structure create or update command by extracting key attributes such as
#     spec name, parent_guid, parent_relationship_type, parent_at_end_1, collection_type
#
#     :param txt: A string representing the input cell to be processed for
#         extracting glossary-related attributes.
#     :param directive: an optional string indicating the directive to be used - display, validate or execute
#     :return: A string summarizing the outcome of the processing.
#     """
#     from md_processing.md_processing_utils.common_md_utils import set_debug_level
#
#     valid = True
#
#     set_debug_level(directive)
#     known_q_name = None
#     command = extract_command(txt)
#     object_type = command.split(' ')[1].strip()
#     object_action = command.split(' ')[0].strip()
#
#     display_name_label = ['Data Structure Name', 'Display Name', 'Name']
#
#     display_name = process_simple_attribute(txt, display_name_label, ERROR)
#     print(Markdown(f"{pre_command} `{command}` for term:`{display_name}` with directive: `{directive}`"))
#
#     description = process_simple_attribute(txt, ['Description'], INFO)
#     namespace = process_simple_attribute(txt, ['Namespace'], INFO)
#     version_id = process_simple_attribute(txt, ['Namespace'], INFO)
#     in_data_spec = process_simple_attribute(txt, ['In Data Spec'], INFO)
#
#     q_name = process_simple_attribute(txt, ['Qualified Name'], INFO)
#
#     # validate display name and get existing qualified_name and guid if they exist
#     if display_name is None:
#         valid = False
#         known_q_name, known_guid, exists = None, None, False
#     else:
#         known_q_name, known_guid, valid, exists = process_element_identifiers(egeria_client, object_type,
#                                                                               display_name_label, txt, object_action,
#                                                                               None)
#
#     if object_action == "Update":  # check to see if provided information exists and is consistent with existing info
#         guid = process_simple_attribute(txt, GUID_LABELS)
#
#         display = (f"\n* Command: {command}\n\t"
#                    f"* Name: {display_name}\n\t* Description: {description}\n\t"
#                    f"* Qualified Name: {q_name}\n\t* GUID: {guid}"
#                    )
#
#         if not exists:
#             msg = f"Update request invalid, Term {display_name} does not exist\n"
#             print_msg(ERROR, msg, debug_level)
#             valid = False
#
#     elif object_action == 'Create':  # if the command is create, check that it doesn't already exist
#         display = (f"\n* Command: {command}\n\t* Glossary: {known_q_name}\n\t"
#                    f"* Name: {display_name}\n\t* Description: {description}\n\t"
#                    f"* Qualified Name: {q_name}\n\t"
#                    )
#         if exists:
#             msg = f"Element `{display_name}` cannot be created since it already exists\n"
#             print_msg(ERROR, msg, debug_level)
#         else:
#             msg = f"It is valid to create Element `{display_name}`"
#             print_msg(ALWAYS, msg, debug_level)
#
#     if directive == "display":
#         print(Markdown(display))
#         return None
#     elif directive == "validate":
#         if valid:
#             print(Markdown(display))
#         else:
#             msg = f"Validation failed for Term `{display_name}`\n"
#             print_msg(ERROR, msg, debug_level)
#             print(Markdown(display))
#         return valid
#
#     elif directive == "process":
#         if valid:
#             print(Markdown(display))
#         else:
#             if exists and object_action == "Create":
#                 msg = f"Create failed because Element `{display_name}` exists - changing `Create` to `Update` in processed output \n"
#                 print_msg(ERROR, msg, debug_level)
#                 print(Markdown(display))
#                 return update_a_command(txt, command, object_type, known_q_name, known_guid)
#             else:
#                 return None
#
#         try:
#             if object_action == "Update":
#                 if not exists:
#                     print(f"\n{ERROR}Element `{display_name}` does not exist! Updating result document with Create "
#                           f"command\n")
#                     return update_a_command(txt, command, object_type, known_q_name, known_guid)
#
#                 egeria_client.update_term(known_guid, body)
#                 print_msg(ALWAYS, f"Updated Term `{term_name}` with GUID {known_guid}", debug_level)
#                 update_element_dictionary(known_q_name, {
#                     'guid': known_guid, 'display_name': term_name
#                     })
#
#                 return egeria_client.get_term_by_guid(known_guid, output_format='MD')
#
#             elif object_action == "Create":
#                 if exists:
#                     print(f"\nTerm `{display_name}` already exists and result document updated\n")
#                     return update_a_command(txt, command, object_type, known_q_name, known_guid)
#                 else:
#                     guid = egeria_client.create_data_spec_collection(None, None, None,
#                                                                      True, display_name, description,
#                                                                      collection_type, None,
#                                                                      True, None)
#                     if guid:
#                         print_msg(ALWAYS, f"Created Element `{display_name}` with GUID {guid}", debug_level)
#                         # Add categories if specified
#
#                         return egeria_client.get_collection_by_guid(guid, output_format='FORM')
#                     else:
#                         print_msg(ERROR, f"Failed to create Term `{display_name}`", debug_level)
#                         return None
#
#         except Exception as e:
#             print(f"{ERROR}Error performing {command}: {e}")
#             Console().print_exception(show_locals=True)
#             return None
#     else:
#         return None
#
#
def process_data_field_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[
    str]:
    """
    Processes a data structure create or update command by extracting key attributes such as
    spec name, parent_guid, parent_relationship_type, parent_at_end_1, collection_type

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """

    from md_processing.md_processing_utils.common_md_utils import set_debug_level

    valid = True

    set_debug_level(directive)
    known_q_name = None
    command, object_type, object_action = extract_command_plus(txt)

    # command = extract_command(txt)
    # object_type = command.split(' ')[1].strip()
    # object_action = command.split(' ')[0].strip()

    parsed_output = parse_user_command(egeria_client, object_type, object_action, txt)


# valid = True
#
#     set_debug_level(directive)
#     known_q_name = None
#     command = extract_command(txt)
#     object_type = command.split(' ')[1].strip()
#     object_action = command.split(' ')[0].strip()
#
#     display_name_label = ['Data Structure Name', 'Display Name', 'Name']
#
#     display_name = process_simple_attribute(txt, display_name_label, ERROR)
#     print(Markdown(f"{pre_command} `{command}` for term:`{display_name}` with directive: `{directive}`"))
#
#     description = process_simple_attribute(txt, ['Description'], INFO)
#     data_type = process_simple_attribute(txt, ['Data Type', "Type"], WARNING)
#     positoion = process_simple_attribute(txt, ['Position'], INFO)
#     min_cardinalityc = process_simple_attribute(txt, ['Minimum Cardinality', 'Min Cardinality'], WARNING)
#     max_cardinality= process_simple_attribute(txt, ['Maximum Cardinality', 'Max Cardinality'], INFO)
#     in_data_structure = process_simple_attribute(txt, ['In Data Structure', 'In Data Struct'], INFO)
#     data_class = process_simple_attribute(txt, ['Data Class','DataClass'], INFO)
#     glossary_term = process_simple_attribute(txt, GLOSSARY_NAME_LABELS, INFO)
#     namesspace= process_simple_attribute(txt, ['Namespace'], INFO)
#     version_id = process_simple_attribute(txt, ['Version','Version Id', 'Version Identifier'], INFO)
#     in_data_dict = process_simple_attribute(txt, ['In Data Dict', 'Data Dictionary', 'In Data Dictionary'], INFO)
#
#     q_name = process_simple_attribute(txt, ['Qualified Name'], INFO)
#
#     # validate display name and get existing qualified_name and guid if they exist
#     if display_name is None:
#         valid = False
#         known_q_name, known_guid, exists = None, None, False
#     else:
#         known_q_name, known_guid, valid, exists = process_element_identifiers(egeria_client, object_type,
#                                                                               display_name_label, txt, object_action,
#                                                                               None)
#
#     if object_action == "Update":  # check to see if provided information exists and is consistent with existing info
#         guid = process_simple_attribute(txt, GUID_LABELS)
#
#         display = (f"\n* Command: {command}\n\t"
#                    f"* Name: {display_name}\n\t* Description: {description}\n\t"
#                    f"* Qualified Name: {q_name}\n\t* GUID: {guid}"
#                    )
#
#         if not exists:
#             msg = f"Update request invalid, Term {display_name} does not exist\n"
#             print_msg(ERROR, msg, debug_level)
#             valid = False
#
#     elif object_action == 'Create':  # if the command is create, check that it doesn't already exist
#         display = (f"\n* Command: {command}\n\t* Glossary: {known_q_name}\n\t"
#                    f"* Name: {display_name}\n\t* Description: {description}\n\t"
#                    f"* Qualified Name: {q_name}\n\t"
#                    )
#         if exists:
#             msg = f"Element `{display_name}` cannot be created since it already exists\n"
#             print_msg(ERROR, msg, debug_level)
#         else:
#             msg = f"It is valid to create Element `{display_name}`"
#             print_msg(ALWAYS, msg, debug_level)

#     if directive == "display":
#         print(Markdown(display))
#         return None
#     elif directive == "validate":
#         if valid:
#             print(Markdown(display))
#         else:
#             msg = f"Validation failed for Term `{display_name}`\n"
#             print_msg(ERROR, msg, debug_level)
#             print(Markdown(display))
#         return valid
#
#     elif directive == "process":
#         if valid:
#             print(Markdown(display))
#         else:
#             if exists and object_action == "Create":
#                 msg = f"Create failed because Element `{display_name}` exists - changing `Create` to `Update` in processed output \n"
#                 print_msg(ERROR, msg, debug_level)
#                 print(Markdown(display))
#                 return update_a_command(txt, command, object_type, known_q_name, known_guid)
#             else:
#                 return None
#
#         try:
#             if object_action == "Update":
#                 if not exists:
#                     print(f"\n{ERROR}Element `{display_name}` does not exist! Updating result document with Create "
#                           f"command\n")
#                     return update_a_command(txt, command, object_type, known_q_name, known_guid)
#
#                 egeria_client.update_term(known_guid, body)
#                 print_msg(ALWAYS, f"Updated Term `{term_name}` with GUID {known_guid}", debug_level)
#                 update_element_dictionary(known_q_name, {
#                     'guid': known_guid, 'display_name': term_name
#                     })
#
#                 return egeria_client.get_term_by_guid(known_guid, output_format='MD')
#
#             elif object_action == "Create":
#                 if exists:
#                     print(f"\nTerm `{display_name}` already exists and result document updated\n")
#                     return update_a_command(txt, command, object_type, known_q_name, known_guid)
#                 else:
#                     guid = egeria_client.create_data_spec_collection(None, None, None,
#                                                                      True, display_name, description,
#                                                                      collection_type, None,
#                                                                      True, None)
#                     if guid:
#                         print_msg(ALWAYS, f"Created Element `{display_name}` with GUID {guid}", debug_level)
#                         # Add categories if specified
#
#                         return egeria_client.get_collection_by_guid(guid, output_format='FORM')
#                     else:
#                         print_msg(ERROR, f"Failed to create Term `{display_name}`", debug_level)
#                         return None
#
#         except Exception as e:
#             print(f"{ERROR}Error performing {command}: {e}")
#             Console().print_exception(show_locals=True)
#             return None
#     else:
#         return None
#
#
# def process_term_list_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
#     """
#     Processes a term list command by extracting key attributes such as
#     glossary name, output format, and search string from the given text.
#
#     :param txt: A string representing the input cell to be processed for
#         extracting term-related attributes.
#     :param directive: an optional string indicating the directive to be used - display, validate or execute
#     :return: A string summarizing the outcome of the processing.
#     """
#     from md_processing.md_processing_utils.common_md_utils import set_debug_level
#
#     command = extract_command(txt)
#     set_debug_level(directive)
#     print(Markdown(f"{pre_command} `{command}` with directive: `{directive}`"))
#
#     glossary_name = process_simple_attribute(txt, GLOSSARY_NAME_LABELS)
#     category_name = process_simple_attribute(txt, CATEGORY_NAME_LABELS)
#     output_format = process_simple_attribute(txt, OUTPUT_LABELS)
#     output_format = output_format.upper() if output_format else "MD"
#     if output_format not in ELEMENT_OUTPUT_FORMATS:
#         print_msg(WARNING, f"Output format {output_format} not recognized, using MD", debug_level)
#         output_format = "MD"
#
#     search_string = process_simple_attribute(txt, SEARCH_LABELS)
#
#     known_glossary_guid = None
#     known_category_guid = None
#
#     if glossary_name:
#         known_glossary_q_name, known_glossary_guid, glossary_valid, glossary_exists = process_element_identifiers(
#             egeria_client, "Glossary", GLOSSARY_NAME_LABELS, txt, EXISTS_REQUIRED, None)
#         if not glossary_exists:
#             print_msg(ERROR, f"Glossary {glossary_name} not found", debug_level)
#             return None
#
#     if category_name:
#         known_category_q_name, known_category_guid, category_valid, category_exists = process_element_identifiers(
#             egeria_client, "Category", CATEGORY_NAME_LABELS, txt, EXISTS_REQUIRED, None)
#         if not category_exists:
#             print_msg(ERROR, f"Category {category_name} not found", debug_level)
#             return None
#
#     if directive == "display":
#         print(Markdown(f"\n* Command: {command}\n\t* Glossary Name: {glossary_name}\n\t* Category Name: {category_name}\n\t* Output Format: {output_format}\n\t* Search String: {search_string}"))
#         return None
#     elif directive == "validate":
#         print(Markdown(f"\n* Command: {command}\n\t* Glossary Name: {glossary_name}\n\t* Category Name: {category_name}\n\t* Output Format: {output_format}\n\t* Search String: {search_string}"))
#         return True
#     elif directive == "process":
#         print(Markdown(f"\n* Command: {command}\n\t* Glossary Name: {glossary_name}\n\t* Category Name: {category_name}\n\t* Output Format: {output_format}\n\t* Search String: {search_string}"))
#         if category_name and category_exists:
#             return egeria_client.list_terms_for_category(known_category_guid, output_format=output_format, search_string=search_string)
#         elif glossary_name and glossary_exists:
#             return egeria_client.list_terms_for_glossary(known_glossary_guid, output_format=output_format, search_string=search_string)
#         else:
#             return egeria_client.list_terms(output_format=output_format, search_string=search_string)
#
#
# def process_term_details_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
#     """
#     Processes a term details command by extracting key attributes such as
#     term name and output format from the given text.
#
#     :param txt: A string representing the input cell to be processed for
#         extracting term-related attributes.
#     :param directive: an optional string indicating the directive to be used - display, validate or execute
#     :return: A string summarizing the outcome of the processing.
#     """
#     from md_processing.md_processing_utils.common_md_utils import set_debug_level
#
#     command = extract_command(txt)
#     set_debug_level(directive)
#     print(Markdown(f"{pre_command} `{command}` with directive: `{directive}`"))
#
#     term_name = process_simple_attribute(txt, TERM_NAME_LABELS, ERROR)
#     output_format = process_simple_attribute(txt, OUTPUT_LABELS)
#     output_format = output_format.upper() if output_format else "MD"
#     if output_format not in ELEMENT_OUTPUT_FORMATS:
#         print_msg(WARNING, f"Output format {output_format} not recognized, using MD", debug_level)
#         output_format = "MD"
#
#     if term_name is None:
#         print_msg(ERROR, "No term name found", debug_level)
#         return None
#
#     known_q_name, known_guid, valid, term_exists = process_element_identifiers(egeria_client, "Term",
#                                                                               TERM_NAME_LABELS, txt,
#                                                                               EXISTS_REQUIRED, None)
#     if not term_exists:
#         print_msg(ERROR, f"Term {term_name} not found", debug_level)
#         return None
#
#     if directive == "display":
#         print(Markdown(f"\n* Command: {command}\n\t* Term Name: {term_name}\n\t* Output Format: {output_format}"))
#         return None
#     elif directive == "validate":
#         print(Markdown(f"\n* Command: {command}\n\t* Term Name: {term_name}\n\t* Output Format: {output_format}"))
#         return True
#     elif directive == "process":
#         print(Markdown(f"\n* Command: {command}\n\t* Term Name: {term_name}\n\t* Output Format: {output_format}"))
#         return egeria_client.get_term_by_guid(known_guid, output_format=output_format)
#
#
# def process_term_history_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
#     """
#     Processes a term history command by extracting key attributes such as
#     term name and output format from the given text.
#
#     :param txt: A string representing the input cell to be processed for
#         extracting term-related attributes.
#     :param directive: an optional string indicating the directive to be used - display, validate or execute
#     :return: A string summarizing the outcome of the processing.
#     """
#     from md_processing.md_processing_utils.common_md_utils import set_debug_level
#
#     command = extract_command(txt)
#     set_debug_level(directive)
#     print(Markdown(f"{pre_command} `{command}` with directive: `{directive}`"))
#
#     term_name = process_simple_attribute(txt, TERM_NAME_LABELS, ERROR)
#     output_format = process_simple_attribute(txt, OUTPUT_LABELS)
#     output_format = output_format.upper() if output_format else "MD"
#     if output_format not in ELEMENT_OUTPUT_FORMATS:
#         print_msg(WARNING, f"Output format {output_format} not recognized, using MD", debug_level)
#         output_format = "MD"
#
#     if term_name is None:
#         print_msg(ERROR, "No term name found", debug_level)
#         return None
#
#     known_q_name, known_guid, valid, term_exists = process_element_identifiers(egeria_client, "Term",
#                                                                               TERM_NAME_LABELS, txt,
#                                                                               EXISTS_REQUIRED, None)
#     if not term_exists:
#         print_msg(ERROR, f"Term {term_name} not found", debug_level)
#         return None
#
#     if directive == "display":
#         print(Markdown(f"\n* Command: {command}\n\t* Term Name: {term_name}\n\t* Output Format: {output_format}"))
#         return None
#     elif directive == "validate":
#         print(Markdown(f"\n* Command: {command}\n\t* Term Name: {term_name}\n\t* Output Format: {output_format}"))
#         return True
#     elif directive == "process":
#         print(Markdown(f"\n* Command: {command}\n\t* Term Name: {term_name}\n\t* Output Format: {output_format}"))
#         return egeria_client.get_term_history(known_guid, output_format=output_format)
#
#
# def process_term_revision_history_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
#     """
#     Processes a term revision history command by extracting key attributes such as
#     term name and output format from the given text.
#
#     :param txt: A string representing the input cell to be processed for
#         extracting term-related attributes.
#     :param directive: an optional string indicating the directive to be used - display, validate or execute
#     :return: A string summarizing the outcome of the processing.
#     """
#     from md_processing.md_processing_utils.common_md_utils import set_debug_level
#
#     command = extract_command(txt)
#     set_debug_level(directive)
#     print(Markdown(f"{pre_command} `{command}` with directive: `{directive}`"))
#
#     term_name = process_simple_attribute(txt, TERM_NAME_LABELS, ERROR)
#     output_format = process_simple_attribute(txt, OUTPUT_LABELS)
#     output_format = output_format.upper() if output_format else "MD"
#     if output_format not in ELEMENT_OUTPUT_FORMATS:
#         print_msg(WARNING, f"Output format {output_format} not recognized, using MD", debug_level)
#         output_format = "MD"
#
#     if term_name is None:
#         print_msg(ERROR, "No term name found", debug_level)
#         return None
#
#     known_q_name, known_guid, valid, term_exists = process_element_identifiers(egeria_client, "Term",
#                                                                               TERM_NAME_LABELS, txt,
#                                                                               EXISTS_REQUIRED, None)
#     if not term_exists:
#         print_msg(ERROR, f"Term {term_name} not found", debug_level)
#         return None
#
#     if directive == "display":
#         print(Markdown(f"\n* Command: {command}\n\t* Term Name: {term_name}\n\t* Output Format: {output_format}"))
#         return None
#     elif directive == "validate":
#         print(Markdown(f"\n* Command: {command}\n\t* Term Name: {term_name}\n\t* Output Format: {output_format}"))
#         return True
#     elif directive == "process":
#         print(Markdown(f"\n* Command: {command}\n\t* Term Name: {term_name}\n\t* Output Format: {output_format}"))
#         return egeria_client.get_term_revision_history(known_guid, output_format=output_format)
