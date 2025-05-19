"""
This file contains term-related object_action functions for processing Egeria Markdown
"""
import json
import os
from typing import Optional

from rich import print
from rich.console import Console
from rich.markdown import Markdown

from md_processing.md_processing_utils.common_md_proc_utils import (parse_user_command, sync_data_dict_membership,
        sync_data_spec_membership, sync_data_structure_membership, sync_term_links, sync_parent_data_field)

from md_processing.md_processing_utils.common_md_utils import print_msg, update_element_dictionary
from md_processing.md_processing_utils.extraction_utils import (extract_command, extract_command_plus, update_a_command)
from md_processing.md_processing_utils.md_processing_constants import (load_commands, ERROR)
from pyegeria import DEBUG_LEVEL, body_slimmer
from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.md_processing_utils import ALWAYS, INFO


load_commands('commands.json')
debug_level = DEBUG_LEVEL

console = Console(width=int(200))

def  add_member_to_data_collections(egeria_client: EgeriaTech, in_data_collection:dict, display_name: str, guid:str )-> bool:
    """
    Add member to data dictionaries and data specifications.
    """
    try:
        for collection in in_data_collection.keys():
            collection_name = collection
            collection_valid = in_data_collection[collection].get('el_valid', False)
            collection_guid = in_data_collection[collection].get('guid', None)
            if collection_guid and collection_valid:
                egeria_client.add_to_collection(collection_guid, guid)
                msg = f"Added `{display_name}` member to `{collection_name}`"
                print_msg(INFO, msg, debug_level)
        return True

    except Exception as e:
        console.print_exception()


def find_memberships_in_collection_type(egeria_client: EgeriaTech, collection_type: str, guid: str) -> list:
    """ Find the collections of a particular type that the element is a member of"""
    collection_guid_list = []
    collections = egeria_client.get_related_elements(guid, "CollectionMembership", "Collection")
    for collection in collections:
        print(collection["relationshipHeader"]['guid'])
        related_el_guid = collection["relatedElement"]['elementHeader']["guid"]
        coll_type = collection["relatedElement"]['properties'].get('collectionType', None)
        print(coll_type)
        if coll_type:
            if coll_type == collection_type:
                collection_guid_list.append(related_el_guid)
                print(collection_guid_list)
    return collection_guid_list




def update_data_collection_memberships(egeria_client: EgeriaTech, in_data_collection:dict, guid: str, replace_all_props:bool = False) -> bool:
    """ update the collection membership of the element """
    pass


# def update_term_categories(egeria_client: EgeriaTech, term_guid: str, current_categories: List[str],
# new_categories: List[str]) -> None:
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
    Processes a data specification create or update object_action by extracting key attributes such as
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

    print(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']
    description = attributes['Description'].get('value', None)
    display_name = attributes['Display Name'].get('value', None)
    anchor_guid = attributes.get('Anchor ID', {}).get('guid', None)
    parent_guid = attributes.get('Parent ID', {}).get('guid', None)
    parent_relationship_type_name = attributes.get('Parent Relationship Type Name', {}).get('value', "CollectionMembership")
    parent_at_end1 = attributes.get('Parent at End1', {}).get('value', True)

    anchor_scope_guid = attributes.get('Anchor Scope GUID', {}).get('value', None)
    is_own_anchor = attributes.get('Is Own Anchor', {}).get('value', True)
    collection_ordering = "NAME"
    order_property_name = "Something"
    collection_type = object_type
    replace_all_props = not attributes.get('Merge Update', {}).get('value', True)
    in_data_spec_list = attributes.get('In Data Specification', {}).get('value', None)
    in_data_spec_valid = attributes.get('In Data Specification', {}).get('valid', None)
    in_data_spec_exists = attributes.get('In Data Specification', {}).get('exists', None)

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
            if object_action == "Update":
                if not exists:
                    msg = (f" Element `{display_name}` does not exist! Updating result document with Create "
                          f"object_action\n")
                    print_msg(ERROR, msg, debug_level)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif not valid:
                    return None
                else:
                    print(Markdown(
                        f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))

                egeria_client.update_collection(guid, qualified_name, display_name, description, collection_type,
                                                collection_ordering, order_property_name, replace_all_props)
                print_msg(ALWAYS, f"Updated  {object_type} `{display_name}` with GUID {guid}", debug_level)
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                return egeria_client.get_collection_by_guid(guid, output_format='FORM')


            elif object_action == "Create":
                if valid is False and exists:
                    msg = (f"  Data Specification `{display_name}` already exists and result document updated changing "
                          f"`Create` to `Update` in processed output\n")
                    print_msg(ERROR, msg, debug_level)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif valid is False and in_data_spec_valid is False:
                    msg = (f" Invalid data specification(s) `{in_data_spec_list}` "
                           f" perhaps they don't yet exist? - Correct and try again")
                    print_msg(ERROR, msg, debug_level)
                else:
                    guid = egeria_client.create_data_spec_collection(anchor_guid, parent_guid,
                                                                     parent_relationship_type_name, parent_at_end1,
                                                                     display_name, description, collection_type,
                                                                     anchor_scope_guid, is_own_anchor,
                                                                     collection_ordering, order_property_name,
                                                                     qualified_name)
                    if guid:

                        print_msg(ALWAYS, f"Created Element `{display_name}` with GUID {guid}", debug_level)

                        return egeria_client.get_collection_by_guid(guid, output_format='FORM')
                    else:
                        print_msg(ERROR, f"Failed to create Term `{display_name}`", debug_level)
                        return None

        except Exception as e:
            print(f"{ERROR}Error performing {command}: {e}")
            Console().print_exception(show_locals=True)
            return None
    else:
        return None


def process_data_dict_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a data dictionary create or update object_action by extracting key attributes such as
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
            msg = f"Validation failed for object_action `{command}`\n"
        return valid

    elif directive == "process":
        print(json.dumps(parsed_output, indent=4))

        attributes = parsed_output['attributes']
        description = attributes['Description'].get('value', None)
        display_name = attributes['Display Name'].get('value', None)
        anchor_guid = attributes.get('Anchor ID', {}).get('guid', None)
        parent_guid = attributes.get('Parent ID', {}).get('guid', None)
        parent_relationship_type_name = attributes.get('Parent Relationship Type Name', {}).get('value',
                                                                                                "CollectionMembership")
        parent_at_end1 = attributes.get('Parent at End1', {}).get('value', True)

        anchor_scope_guid = attributes.get('Anchor Scope GUID', {}).get('value', None)
        is_own_anchor = attributes.get('Is Own Anchor', {}).get('value', True)
        if parent_guid is None:
            is_own_anchor = True
        collection_ordering = "NAME"
        order_property_name = "Something"
        collection_type = object_type
        replace_all_props = not attributes.get('Merge Update', {}).get('value', True)


        try:
            if object_action == "Update":

                if not exists:
                    print(f"\n{ERROR}Element `{display_name}` does not exist! Updating result document with Create "
                          f"object_action\n")
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif not valid:
                    return None
                else:
                    print(Markdown(
                        f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))

                egeria_client.update_collection(guid, qualified_name, display_name, description, collection_type,
                                                collection_ordering, order_property_name, replace_all_props)
                print_msg(ALWAYS, f"Updated  {object_type} `{display_name}` with GUID {guid}", debug_level)
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                return egeria_client.get_collection_by_guid(guid, output_format='FORM')

            elif object_action == "Create":
                if valid is False and exists:
                    print(f"\nElement `{display_name}` already exists and result document updated changing "
                          f"`Create` to `Update` in processed output\n")
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                else:
                    guid = egeria_client.create_data_dictionary_collection(anchor_guid, parent_guid,
                                                                           parent_relationship_type_name,
                                                                           parent_at_end1, display_name, description,
                                                                           collection_type, anchor_scope_guid,
                                                                           is_own_anchor, collection_ordering,
                                                                           order_property_name, qualified_name)
                    if guid:
                        print_msg(ALWAYS, f"Created Element `{display_name}` with GUID {guid}", debug_level)

                        return egeria_client.get_collection_by_guid(guid, output_format='FORM')
                    else:
                        print_msg(ERROR, f"Failed to create Term `{display_name}`", debug_level)
                        return None

        except Exception as e:
            print(f"{ERROR}Error performing {command}: {e}")
            Console().print_exception(show_locals=True)
            return None
    else:
        return None


def process_data_field_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a data dictionary create or update object_action by extracting key attributes such as
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
            msg = f"Validation failed for object_action `{command}`\n"
        return valid

    elif directive == "process":
        print(json.dumps(parsed_output, indent=4))
        attributes = parsed_output['attributes']

        external_source_guid = attributes.get('External Source Name', {}).get('guid', None)
        external_source_name = attributes.get('External Source Name', {}).get('value', None)
        effective_time = attributes.get('Effective Time', {}).get('value', None)
        for_lineage = attributes.get('For Lineage', {}).get('value', None)
        for_duplicate_processing = attributes.get('For Duplicate Processing', {}).get('value', None)
        anchor_guid = attributes.get('Anchor ID', {}).get('guid', None)
        is_own_anchor = attributes.get('Is Own Anchor', {}).get('value', None)
        # parent_id = attributes.get('Parent ID', {}).get('value', None)
        # parent_guid = attributes['Parent ID'].get('guid', None)
        # parent_relationship_type_name = attributes.get('Parent Relationship Type Name', {}).get('value', None)
        # parent_relationship_properties = attributes.get('Parent Relationship Properties',{}).get('value', None)
        # parent_at_end1 = attributes.get('Parent at End1', {}).get('value', None)

        display_name = attributes['Display Name'].get('value', None)

        namespace = attributes.get('Namespace',{}).get('value', None)
        description = attributes.get('Description',{}).get('value', None)
        version_id = attributes.get('Version Identifier', {}).get('value', None)
        aliases = attributes.get('Aliases', {}).get('value', None)
        name_patterns = attributes.get('Name Patterns', {}).get('value', None)
        is_nullable = attributes.get('Is Nullable', {}).get('value', None)
        default_value = attributes.get('Default Value', {}).get('value', None)
        data_type = attributes.get('Data Type', {}).get('value', None)
        min_length = attributes.get('Minimum Length', {}).get('value', None)
        length = attributes.get('Length', {}).get('value', None)
        precision = attributes.get('Precision', {}).get('value', None)
        ordered_values = attributes.get('Ordered Values', {}).get('value', None)
        sort_order = attributes.get('Sort Order', {}).get('value', None)
        additional_properties = attributes.get('Additional Properties', {}).get('value', None)
        effective_from = attributes.get('Effective From', {}).get('value', None)
        effective_to = attributes.get('Effective To', {}).get('value', None)

        position = attributes.get('Position', {}).get('value', None)
        min_cardinality = attributes.get('Minimum Cardinality', {}).get('value', None)
        max_cardinality = attributes.get('Maximum Cardinality', {}).get('value', None)

        in_data_structure = attributes.get('In Data Structure', {}).get('value', None)
        in_data_structure_names = attributes.get('In Data Structure Names', {}).get('name_list', None)

        data_class = attributes['Data Class'].get('value', None)

        glossary_term = attributes['Glossary Term'].get('value', None)
        glossary_term_guid = attributes['Glossary Term'].get('guid', None)

        in_data_dictionary = attributes.get('In Data Dictionary', {}).get('value', None)
        in_data_dictionary_names = attributes.get('In Data Dictionary Names', {}).get('name_list', None)

        parent_data_field = attributes.get('Parent Data Field', {}).get('value', None)
        parent_data_field_guid = attributes.get('Parent Data Field', {}).get('guid', None)

        anchor_scope_guid = attributes.get('Anchor Scope GUID', {}).get('value', None)

        merge_update = attributes.get('Merge Update', {}).get('value', None)


        collection_ordering = "NAME"
        order_property_name = "Something"
        collection_type = object_type
        replace_all_props = True

        if not valid:
            if exists and object_action == "Create":
                msg = (f"Create failed because Element `{display_name}` exists - changing `Create` to `Update` in "
                       f"processed output \n")
                print_msg(ERROR, msg, debug_level)
                return update_a_command(txt, object_action, object_type, qualified_name, guid)
            else:
                return None
        else:
            print(Markdown(f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))

        try:
            if object_action == "Update":
                if not exists:
                    print(f"\n{ERROR}Element `{display_name}` does not exist! Updating result document with Create "
                          f"object_action\n")
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)

                body = {
                    "class": "UpdateDataFieldRequestBody",
                    "externalSourceGUID": external_source_guid,
                    "externalSourceName": external_source_name,
                    "effectiveTime": None,
                    "forLineage": False,
                    "forDuplicateProcessing": False,
                    "properties": {
                        "class": "DataFieldProperties",
                        "qualifiedName": qualified_name,
                        "displayName": display_name,
                        "namespace": namespace,
                        "description": description,
                        "versionIdentifier": version_id,
                        "aliases": aliases,
                        "namePatterns": name_patterns,
                        "isDeprecated": False,
                        "isNullable": is_nullable,
                        "defaultValue": default_value,
                        "dataType": data_type,
                        "minimumLength": min_length,
                        "length": length,
                        "precision": precision,
                        "orderedValues": ordered_values,
                        "sortOrder": sort_order,
                        "additionalProperties": additional_properties,
                        "effectiveFrom": effective_from,
                        "effectiveTo": effective_to
                        }
                    }

                egeria_client.update_data_field(guid, body, not merge_update)
                print_msg(ALWAYS, f"Updated  {object_type} `{display_name}` with GUID {guid}", debug_level)
                # Update data dictionary membership
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                core_props = egeria_client.get_data_field_by_guid(guid, output_format='MD')

                existing_data_field = egeria_client.get_data_field_by_guid(guid, output_format='JSON')
                existing_data_field_dicts = 3

                # Sync membership in data dictionaries
                result = sync_data_dict_membership(egeria_client, in_data_dictionary_names, in_data_dictionary, guid, object_type)
                print_msg(ALWAYS, f"Will update data dictionary `{in_data_dictionary}`", debug_level)
                core_props += f"\n\n## In Data Dictionary\n\n{in_data_dictionary}\n\n"

                # Update data spec membership
                result = sync_data_spec_membership(egeria_client, in_data_dictionary_names, in_data_dictionary, guid,
                                                   object_type)
                print_msg(ALWAYS, f"Will update data dictionary `{in_data_dictionary}`", debug_level)
                core_props += f"\n\n## In Data Dictionary\n\n{in_data_dictionary}\n\n"

                # Sync membership in data structuress
                result = sync_data_structure_membership(egeria_client, in_data_dictionary_names, in_data_dictionary, guid,
                                                   object_type)
                core_props += f"\n\n## In Data Structure {in_data_structure}\n\n"

                # Update glossary links
                result = sync_term_links(egeria_client, glossary_term, glossary_term_guid, guid, object_type)
                print_msg(ALWAYS, f"Updating glossary term to `{glossary_term}`", debug_level)

                core_props += f"\n\n## Glossary Term \n\n{glossary_term}\n\n"
                # Update parent field
                result = sync_parent_data_field(egeria_client, parent_data_field, parent_data_field_guid, guid, object_type)

                core_props += f"\n\n## Parent Data Field\n\n{parent_data_field}\n\n"

                # Update data classes
                print_msg(ALWAYS, f"Created Element `{display_name}` ", debug_level)


                return core_props


            elif object_action == "Create":
                if valid is False and exists:
                    print(f"\nData Field `{display_name}` already exists and result document updated changing `Create` "
                          f"to `Update` in processed output\n")
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                else:
                    # First lets create the data field
                    body = {
                        "properties": {
                            "class": "DataFieldProperties", "qualifiedName": qualified_name,
                            "displayName": display_name, "namespace": namespace, "description": description,
                            "versionIdentifier": version_id, "aliases": aliases, "namePatterns": name_patterns,
                            "isDeprecated": False, "isNullable": is_nullable, "defaultValue": default_value,
                            "dataType": data_type, "minimumLength": min_length, "length": length,
                            "precision": precision, "orderedValues": ordered_values, "sortOrder": sort_order,
                            "additionalProperties": additional_properties
                            }
                        }
                    guid = egeria_client.create_data_field(body)
                    if guid:
                        # Now update our element dictionary with the new information
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        # Start assembling the information we will present back out
                        core_props = egeria_client.get_data_field_by_guid(guid, output_format='MD')

                        # Add the field to any data dictionaries
                        if in_data_dictionary:
                            print_msg(ALWAYS, f"Will add to data dictionary `{in_data_dictionary}`", debug_level)
                            core_props += f"\n\n## In Data Dictionary\n\n{in_data_dictionary_names}\n\n"
                        # Add the field to any data structures
                        if in_data_structure:
                            core_props += f"\n\n## In Data Structure\n\n{in_data_structure_names}\n\n"
                            for key in in_data_structure.keys():
                                ds_qname = in_data_structure[key].get('known_q_name', None)
                                ds_guid = in_data_structure[key].get('known_guid', None)
                                if ds_guid is not None:
                                    df_body = {
                                        "class": "MemberDataFieldRequestBody", "properties": {
                                            "class": "MemberDataFieldProperties", "dataFieldPosition": 0,
                                            "minCardinality": 0, "maxCardinality": -1,
                                            }
                                        }

                                    msg = f"Adding field to structure {ds_qname}"
                                    print_msg(INFO, msg, debug_level)
                                    egeria_client.link_member_data_field(ds_guid, guid, df_body)
                            core_props += f"\n\n## In Data Structure {in_data_structure}\n\n"

                        if glossary_term:
                            if glossary_term_guid:
                                glossary_body = {
                                    "class": "MetadataSourceRequestBody", "externalSourceGUID": None,
                                    "externalSourceName": None, "effectiveTime": None, "forLineage": False,
                                    "forDuplicateProcessing": False
                                    }

                                core_props += f"\n\n## Glossary Term \n\n{glossary_term}\n\n"
                                egeria_client.link_semantic_definition(guid, glossary_term_guid, glossary_body)

                        if parent_data_field_guid:
                            parent_df_body = {
                                "class": "MetadataSourceRequestBody", "externalSourceGUID": None,
                                "externalSourceName": None, "effectiveTime": None, "forLineage": False,
                                "forDuplicateProcessing": False
                                }

                            egeria_client.link_nested_data_field(parent_data_field_guid, guid, parent_df_body)
                            core_props += f"\n\n## Parent Data Field\n\n{parent_data_field}\n\n"

                        # Link data class
                        print_msg(ALWAYS, f"Created Element `{display_name}` ", debug_level)
                        return core_props

                    else:
                        print_msg(ERROR, f"Failed to create Term `{display_name}`", debug_level)
                        return None

        except Exception as e:
            print(f"{ERROR}Error performing {command}: {e}")
            Console().print_exception(show_locals=True)
            return None
    else:
        return None


def process_data_structure_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[
    str]:
    """
    Processes a data structure create or update object_action by extracting key attributes such as
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
            msg = f"Validation failed for object_action `{command}`\n"
        return valid

    elif directive == "process":
        print(json.dumps(parsed_output, indent=4))
        attributes = parsed_output['attributes']

        external_source_guid = attributes.get('External Source Name', {}).get('guid', None)
        external_source_name = attributes.get('External Source Name', {}).get('value', None)
        effective_time = attributes.get('Effective Time', {}).get('value', None)
        for_lineage = attributes.get('For Lineage', {}).get('value', None)
        for_duplicate_processing = attributes.get('For Duplicate Processing', {}).get('value', None)
        anchor_guid = attributes.get('Anchor ID', {}).get('guid', None)
        is_own_anchor = attributes.get('Is Own Anchor', {}).get('value', None)
        parent_id = attributes.get('Parent ID', {}).get('value', None)
        parent_guid = attributes.get('Parent ID', {}).get('guid', None)
        parent_relationship_type_name = attributes.get('Parent Relationship Type Name', {}).get('value', None)
        parent_relationship_properties = attributes.get('Parent Relationship Properties', {}).get('value', None)
        parent_at_end1 = attributes.get('Parent at End1', {}).get('value', None)

        display_name = attributes['Display Name'].get('value', None)

        namespace = attributes.get('Namespace', {}).get('value', None)
        description = attributes.get('Description', {}).get('value', None)
        version_id = attributes.get('Version Identifier', {}).get('value', None)
        aliases = attributes.get('Aliases', {}).get('value', None)
        name_patterns = attributes.get('Name Patterns', {}).get('value', None)
        is_nullable = attributes.get('Is Nullable', {}).get('value', None)
        default_value = attributes.get('Default Value', {}).get('value', None)
        data_type = attributes.get('Data Type', {}).get('value', None)
        min_length = attributes.get('Minimum Length', {}).get('value', None)
        length = attributes.get('Length', {}).get('value', None)
        precision = attributes.get('Precision', {}).get('value', None)
        ordered_values = attributes.get('Ordered Values', {}).get('value', None)
        sort_order = attributes.get('Sort Order', {}).get('value', None)
        additional_properties = attributes.get('Additional Properties', {}).get('value', None)
        effective_from = attributes.get('Effective From', {}).get('value', None)
        effective_to = attributes.get('Effective To', {}).get('value', None)

        position = attributes.get('Position', {}).get('value', None)
        min_cardinality = attributes.get('Minimum Cardinality', {}).get('value', None)
        max_cardinality = attributes.get('Maximum Cardinality', {}).get('value', None)
        in_data_structure = attributes.get('In Data Structure', {}).get('value', None)
        data_class = attributes.get('Data Class', {}).get('value', None)
        glossary_term = attributes.get('Glossary Term', {}).get('value', None)
        glossary_term_guid = attributes.get('Glossary Term', {}).get('guid', None)

        # name_details_list = attributes.get("dict_list", None)

        in_data_spec = attributes.get("In Data Specification", {}).get("dict_list")  # this is a [dict]
        data_spec_name_list = attributes.get("In Data Specification", {}).get("name_list", None)
        data_spec_value_list = attributes.get("In Data Specification", {}).get("value", None)

        in_data_dictionary = attributes.get('In Data Dictionary', {}).get('dict_list', None)
        data_dict_name_list = attributes.get('In Data Dictionary', {}).get('name_list', None)
        data_dict_value_list = attributes.get('In Data Dictionary', {}).get('value', None)

        parent_data_field = attributes.get('Parent Data Field', {}).get('value', None)
        parent_data_field_guid = attributes.get('Parent Data Field', {}).get('guid', None)

        anchor_scope_guid = attributes.get('Anchor Scope GUID', {}).get('value', None)

        collection_ordering = "NAME"
        order_property_name = "Something"
        collection_type = object_type
        replace_all_props = True
        if not valid:
            if exists and object_action == "Create":
                msg = (f"Create failed because Element `{display_name}` exists - changing `Create` to `Update` in "
                       f"processed output \n")
                print_msg(ERROR, msg, debug_level)
                return update_a_command(txt, object_action, object_type, qualified_name, guid)
            else:
                return None
        elif object_action == "Update" and not exists:
            print(f"\n{ERROR}Element `{display_name}` does not exist! Updating result document with Create "
                  f"object_action\n")
            return update_a_command(txt, object_action, object_type, qualified_name, guid)

        else:
            print(Markdown(f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))

        try:
            if object_action == "Update":
                body = {
                    "class": "UpdateDataStructureRequestBody",
                    "externalSourceGUID": external_source_guid,
                    "externalSourceName": external_source_name,
                    "effectiveTime": effective_time,
                    "forLineage": for_lineage,
                    "forDuplicateProcessing": for_duplicate_processing,
                    "properties": {
                        "class": "DataStructureProperties",
                        "qualifiedName": qualified_name,
                        "displayName": display_name,
                        "description": description,
                        "namespace": namespace,
                        "versionIdentifier": version_id,
                        "additionalProperties": additional_properties,
                        "effectiveFrom": effective_from,
                        "effectiveTo": effective_to
                        }
                    }
                egeria_client.update_data_structure_w_body(guid, body, replace_all_props)
                print_msg(ALWAYS, f"Updated element `{display_name}` with GUID {guid}", debug_level)
                core_props = egeria_client.get_data_structure_by_guid(guid, output_format='FORM')

                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                update_data_collection_memberships(egeria_client, in_data_spec, guid, replace_all_props)

                return egeria_client.get_data_structure_by_guid(guid, output_format='MD')

            elif object_action == "Create":
                if exists:
                    print(f"\nTerm `{display_name}` already exists and result document updated\n")
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                else:

                    body = {
                        "class": "NewDataStructureRequestBody", "externalSourceGUID": external_source_guid,
                        "externalSourceName": external_source_name, "effectiveTime": effective_time,
                        "forLineage": False, "forDuplicateProcessing": False, "anchorGUID": anchor_guid,
                        "isOwnAnchor": is_own_anchor, "parentGUID": parent_guid,
                        "parentRelationshipTypeName": parent_relationship_type_name,
                        "parentRelationshipProperties": parent_relationship_properties, "parentAtEnd1": parent_at_end1,
                        "properties": {
                            "class": "DataStructureProperties", "qualifiedName": qualified_name,
                            "displayName": display_name, "description": description, "namespace": namespace,
                            "versionIdentifier": version_id, "additionalProperties": additional_properties,
                            "effectiveFrom": effective_from, "effectiveTo": effective_to
                            }
                        }

                    guid = egeria_client.create_data_structure_w_body(body_slimmer(body))
                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })

                        core_props = egeria_client.get_data_structure_by_guid(guid, output_format='FORM')

                        if in_data_dictionary:
                            print_msg(ALWAYS, f"Will add to data dictionary(s) `{in_data_dictionary}`", debug_level)
                            result = add_member_to_data_collections(egeria_client, in_data_dictionary, display_name,guid )
                            core_props += f"\n\n## In Data Dictionary\n\n{in_data_dictionary}\n\n"
                        # ==>> update to use new function.
                        if in_data_spec:
                            # member_body = {
                            #     "class": "CollectionMembershipProperties",
                            #     "membershipRationale": "Adding data structure to data specification",
                            #     "expression": None, "confidence": 100, "status": None, "userDefinedStatus": None,
                            #     "steward": None, "stewardTypeName": None, "stewardPropertyName": None, "source": None,
                            #     "notes": None,
                            #     }
                            #
                            # if data_spec_name_list is not None:
                            #     for el in data_spec_value_list:
                            #         for key in el:
                            #             ds = el[key]
                            #             ds_qname = ds.get('known_q_name', None)
                            #             ds_guid = ds.get('known_guid', None)
                            #             if ds_guid is not None:
                            #                 msg = f"Adding field to Data Specification `{ds_qname}`"
                            #                 egeria_client.add_to_collection(ds_guid, guid, member_body)
                            #                 print_msg(INFO, msg, debug_level)
                            result = add_member_to_data_collections(egeria_client, in_data_spec, display_name,guid )

                            core_props += f"\n\n## In Data Specifications\n\n`{data_spec_name_list}`\n\n"

                        print_msg(ALWAYS, f"Created Element `{display_name}` with GUID {guid}", debug_level)

                        return core_props
                    else:
                        print_msg(ERROR, f"Failed to create Data Structure `{display_name}`", debug_level)
                        return None


        except Exception as e:
            print(f"{ERROR}Error performing {object_action}: {e}")
            Console().print_exception(show_locals=True)
            return None
    else:
        return None


# def process_data_field_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[
# str]:
#     """
#     Processes a data structure create or update object_action by extracting key attributes such as
#     spec name, parent_guid, parent_relationship_type, parent_at_end_1, collection_type
#
#     :param txt: A string representing the input cell to be processed for
#         extracting glossary-related attributes.
#     :param directive: an optional string indicating the directive to be used - display, validate or execute
#     :return: A string summarizing the outcome of the processing.
#     """
#
#     from md_processing.md_processing_utils.common_md_utils import set_debug_level
#
#     valid = True
#
#     set_debug_level(directive)
#     known_q_name = None
#     command, object_type, object_action = extract_command_plus(txt)

# object_action = extract_command(txt)
# object_type = object_action.split(' ')[1].strip()
# object_action = object_action.split(' ')[0].strip()

# parsed_output = parse_user_command(egeria_client, object_type, object_action, txt)


# valid = True
#
#     set_debug_level(directive)
#     known_q_name = None
#     object_action = extract_command(txt)
#     object_type = object_action.split(' ')[1].strip()
#     object_action = object_action.split(' ')[0].strip()
#
#     display_name_label = ['Data Structure Name', 'Display Name', 'Name']
#
#     display_name = process_simple_attribute(txt, display_name_label, ERROR)
#     print(Markdown(f"{pre_command} `{object_action}` for term:`{display_name}` with directive: `{directive}`"))
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
#         display = (f"\n* Command: {object_action}\n\t"
#                    f"* Name: {display_name}\n\t* Description: {description}\n\t"
#                    f"* Qualified Name: {q_name}\n\t* GUID: {guid}"
#                    )
#
#         if not exists:
#             msg = f"Update request invalid, Term {display_name} does not exist\n"
#             print_msg(ERROR, msg, debug_level)
#             valid = False
#
#     elif object_action == 'Create':  # if the object_action is create, check that it doesn't already exist
#         display = (f"\n* Command: {object_action}\n\t* Glossary: {known_q_name}\n\t"
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
#                 msg = f"Create failed because Element `{display_name}` exists - changing `Create` to `Update` in
#                 processed output \n"
#                 print_msg(ERROR, msg, debug_level)
#                 print(Markdown(display))
#                 return update_a_command(txt, object_action, object_type, known_q_name, known_guid)
#             else:
#                 return None
#
#         try:
#             if object_action == "Update":
#                 if not exists:
#                     print(f"\n{ERROR}Element `{display_name}` does not exist! Updating result document with Create "
#                           f"object_action\n")
#                     return update_a_command(txt, object_action, object_type, known_q_name, known_guid)
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
#                     return update_a_command(txt, object_action, object_type, known_q_name, known_guid)
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
#             print(f"{ERROR}Error performing {object_action}: {e}")
#             Console().print_exception(show_locals=True)
#             return None
#     else:
#         return None
#
#
def process_data_dict_list_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a Data Dictionary list object_action by extracting key attributes such as
     search string from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting term-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    from md_processing.md_processing_utils.common_md_utils import set_debug_level

    set_debug_level(directive)
    known_q_name = None
    command, object_type, object_action = extract_command_plus(txt)

    object_action = extract_command(txt)
    set_debug_level(directive)

    parsed_output = parse_user_command(egeria_client, object_action, 'View', txt)
    print(Markdown(parsed_output['display']))
    valid = parsed_output['valid']

    if directive == "display":
        return None
    elif directive == "validate":
        if valid:
            msg = f"Validation passed for {object_action} `{object_type}`\n"
        else:
            msg = f"Validation failed for {object_action} `{object_type}`\n"
        print_msg(ERROR, msg, debug_level)
        return valid
    elif directive == "process":
        attributes = parsed_output['attributes']
        search_string = attributes.get('Search String', {}).get('value', '*')
        output_format = attributes.get('Output Format', {}).get('value', 'LIST')
        detailed = attributes.get('Detailed', {}).get('value', False)

        try:
            if not valid:  # First validate the command before we process it
                msg = f"Validation failed for {object_action} `{object_type}`\n"
                print_msg(ERROR, msg, debug_level)
                return None

            list_md = f"\n# Data Dictionaries with filter: `{search_string}`\n\n"
            if output_format == "DICT":
                struct = egeria_client.get_classified_collections('DataDictionary', output_format=output_format)
                list_md += f"```{json.dumps(struct, indent=4)}```\n"
            else:
                list_md += egeria_client.find_collections(search_string, output_format=output_format)
            print_msg("ALWAYS", f"Wrote Dictionaries for search string: `{search_string}`", debug_level)

            return list_md

        except Exception as e:
            print(f"{ERROR}Error performing {command}: {e}")
            console.print_exception(show_locals=True)
            return None
    else:
        return None

# def process_term_details_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
#     """
#     Processes a term details object_action by extracting key attributes such as
#     term name and output format from the given text.
#
#     :param txt: A string representing the input cell to be processed for
#         extracting term-related attributes.
#     :param directive: an optional string indicating the directive to be used - display, validate or execute
#     :return: A string summarizing the outcome of the processing.
#     """
#     from md_processing.md_processing_utils.common_md_utils import set_debug_level
#
#     object_action = extract_command(txt)
#     set_debug_level(directive)
#     print(Markdown(f"{pre_command} `{object_action}` with directive: `{directive}`"))
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
#         print(Markdown(f"\n* Command: {object_action}\n\t* Term Name: {term_name}\n\t* Output Format: {
#         output_format}"))
#         return None
#     elif directive == "validate":
#         print(Markdown(f"\n* Command: {object_action}\n\t* Term Name: {term_name}\n\t* Output Format: {
#         output_format}"))
#         return True
#     elif directive == "process":
#         print(Markdown(f"\n* Command: {object_action}\n\t* Term Name: {term_name}\n\t* Output Format: {
#         output_format}"))
#         return egeria_client.get_term_by_guid(known_guid, output_format=output_format)
#
#
# def process_term_history_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
#     """
#     Processes a term history object_action by extracting key attributes such as
#     term name and output format from the given text.
#
#     :param txt: A string representing the input cell to be processed for
#         extracting term-related attributes.
#     :param directive: an optional string indicating the directive to be used - display, validate or execute
#     :return: A string summarizing the outcome of the processing.
#     """
#     from md_processing.md_processing_utils.common_md_utils import set_debug_level
#
#     object_action = extract_command(txt)
#     set_debug_level(directive)
#     print(Markdown(f"{pre_command} `{object_action}` with directive: `{directive}`"))
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
#         print(Markdown(f"\n* Command: {object_action}\n\t* Term Name: {term_name}\n\t* Output Format: {
#         output_format}"))
#         return None
#     elif directive == "validate":
#         print(Markdown(f"\n* Command: {object_action}\n\t* Term Name: {term_name}\n\t* Output Format: {
#         output_format}"))
#         return True
#     elif directive == "process":
#         print(Markdown(f"\n* Command: {object_action}\n\t* Term Name: {term_name}\n\t* Output Format: {
#         output_format}"))
#         return egeria_client.get_term_history(known_guid, output_format=output_format)
#
#
# def process_term_revision_history_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") ->
# Optional[str]:
#     """
#     Processes a term revision history object_action by extracting key attributes such as
#     term name and output format from the given text.
#
#     :param txt: A string representing the input cell to be processed for
#         extracting term-related attributes.
#     :param directive: an optional string indicating the directive to be used - display, validate or execute
#     :return: A string summarizing the outcome of the processing.
#     """
#     from md_processing.md_processing_utils.common_md_utils import set_debug_level
#
#     object_action = extract_command(txt)
#     set_debug_level(directive)
#     print(Markdown(f"{pre_command} `{object_action}` with directive: `{directive}`"))
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
#         print(Markdown(f"\n* Command: {object_action}\n\t* Term Name: {term_name}\n\t* Output Format: {
#         output_format}"))
#         return None
#     elif directive == "validate":
#         print(Markdown(f"\n* Command: {object_action}\n\t* Term Name: {term_name}\n\t* Output Format: {
#         output_format}"))
#         return True
#     elif directive == "process":
#         print(Markdown(f"\n* Command: {object_action}\n\t* Term Name: {term_name}\n\t* Output Format: {
#         output_format}"))
#         return egeria_client.get_term_revision_history(known_guid, output_format=output_format)
