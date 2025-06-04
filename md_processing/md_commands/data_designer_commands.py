"""
This file contains term-related object_action functions for processing Egeria Markdown
"""
import json
import sys
from typing import Optional

from loguru import logger
from rich import print
from rich.console import Console
from rich.markdown import Markdown

from md_processing.md_processing_utils.common_md_proc_utils import (parse_upsert_command, add_member_to_data_collections,
                                                                    update_data_collection_memberships,
                                                                    sync_data_field_rel_elements,
                                                                    sync_data_class_rel_elements, parse_view_command)
from md_processing.md_processing_utils.common_md_utils import update_element_dictionary
from md_processing.md_processing_utils.extraction_utils import (extract_command, extract_command_plus, update_a_command)
from md_processing.md_processing_utils.md_processing_constants import (load_commands, ERROR)
from pyegeria import DEBUG_LEVEL, body_slimmer
from pyegeria.egeria_tech_client import EgeriaTech

load_commands('commands.json')
debug_level = DEBUG_LEVEL

console = Console(width=int(200))

log_format = "D {time} | {level} | {function} | {line} | {message} | {extra}"
logger.remove()
logger.add(sys.stderr, level="SUCCESS", format=log_format, colorize=True)
logger.add("debug_log.log", rotation="1 day", retention="1 week", compression="zip", level="TRACE", format=log_format,
           colorize=True)


@logger.catch
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

    parsed_output = parse_upsert_command(egeria_client, object_type, object_action, txt, directive)

    valid = parsed_output['valid']
    exists = parsed_output['exists']

    qualified_name = parsed_output.get('qualified_name', None)
    guid = parsed_output.get('guid', None)

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

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
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif not valid:
                    return None
                else:
                    print(Markdown(
                        f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))

                egeria_client.update_collection(guid, qualified_name, display_name, description, collection_type,
                                                replace_all_props)
                logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}")
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                return egeria_client.get_collection_by_guid(guid, collection_type='Data Specification',
                                                            output_format='MD')


            elif object_action == "Create":
                if valid is False and exists:
                    msg = (f"  Data Specification `{display_name}` already exists and result document updated changing "
                           f"`Create` to `Update` in processed output\n")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif valid is False and in_data_spec_valid is False:
                    msg = (f" Invalid data specification(s) `{in_data_spec_list}` "
                           f" perhaps they don't yet exist? - Correct and try again")
                    logger.error(msg)
                else:
                    guid = egeria_client.create_data_spec_collection(anchor_guid, parent_guid,
                                                                     parent_relationship_type_name, parent_at_end1,
                                                                     display_name, description, collection_type,
                                                                     anchor_scope_guid, is_own_anchor, qualified_name)
                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        msg = f"Created Element `{display_name}` with GUID {guid}"
                        logger.success(msg)
                        return egeria_client.get_collection_by_guid(guid, collection_type='Data Specification',
                                                                    output_format='MD')
                    else:
                        msg = f"Failed to create element `{display_name}` with GUID {guid}"
                        logger.error(msg)
                        return None

        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            return None
    else:
        return None


@logger.catch
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

    parsed_output = parse_upsert_command(egeria_client, object_type, object_action, txt, directive)

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
        logger.debug(json.dumps(parsed_output, indent=4))

        attributes = parsed_output['attributes']
        description = attributes['Description'].get('value', None)
        display_name = attributes.get('Display Name',{}).get('value', "None Found")
        display_name = display_name if display_name is not None else "None Found"
        anchor_guid = attributes.get('Anchor ID', {}).get('guid', None)
        parent_guid = attributes.get('Parent ID', {}).get('guid', None)
        parent_relationship_type_name = attributes.get('Parent Relationship Type Name', {}).get('value',
                                                                                                "CollectionMembership")
        parent_at_end1 = attributes.get('Parent at End1', {}).get('value', True)

        anchor_scope_guid = attributes.get('Anchor Scope GUID', {}).get('value', None)
        is_own_anchor = attributes.get('Is Own Anchor', {}).get('value', True)
        if parent_guid is None:
            is_own_anchor = True
        collection_type = object_type
        replace_all_props = not attributes.get('Merge Update', {}).get('value', True)

        try:
            if object_action == "Update":

                if not exists:
                    logger.error(f"Element `{display_name}` does not exist! Updating result document with Create "
                                 f"object_action\n")
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif not valid:
                    return None
                else:
                    print(Markdown(
                        f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))

                egeria_client.update_collection(guid, qualified_name, display_name, description, collection_type,
                                                replace_all_props)
                logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}")
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                return egeria_client.get_collection_by_guid(guid, collection_type='Data Dictionary', output_format='MD')

            elif object_action == "Create":
                if valid is False and exists:
                    logger.error(f"\nElement `{display_name}` already exists and result document updated changing "
                                 f"`Create` to `Update` in processed output\n")
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                else:
                    guid = egeria_client.create_data_dictionary_collection(anchor_guid, parent_guid,
                                                                           parent_relationship_type_name,
                                                                           parent_at_end1, display_name, description,
                                                                           collection_type, anchor_scope_guid,
                                                                           is_own_anchor, qualified_name)
                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        logger.success(f"Created Element `{display_name}` with GUID {guid}")

                        return egeria_client.get_collection_by_guid(guid, collection_type='Data Dictionary',
                                                                    output_format='MD')
                    else:
                        logger.error(f"Failed to create Term `{display_name}`")
                        return None

        except Exception as e:
            logger.error(f"{ERROR}Error performing {command}: {e}")
            Console().print_exception(show_locals=True)
            return None
    else:
        return None



@logger.catch
def process_data_structure_upsert_command(egeria_client: EgeriaTech, txt: str,
                                          directive: str = "display") -> Optional[str]:
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

    parsed_output = parse_upsert_command(egeria_client, object_type, object_action, txt, directive)

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
        logger.debug(json.dumps(parsed_output, indent=4))
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

        in_data_spec = attributes.get("In Data Specification", {}).get("dict_list", None)  # this is a [dict]
        data_spec_name_list = attributes.get("In Data Specification", {}).get("name_list", "")
        data_spec_value_list = attributes.get("In Data Specification", {}).get("value", None)
        data_spec_guid_list = attributes.get("In Data Specification", {}).get("guid_list", None)

        in_data_dictionary = attributes.get('In Data Dictionary', {}).get('dict_list', None)
        data_dict_name_list = attributes.get('In Data Dictionary', {}).get('name_list', "")
        data_dict_value_list = attributes.get('In Data Dictionary', {}).get('value', None)
        data_dict_guid_list = attributes.get("In Data Dictionary", {}).get("guid_list", None)

        parent_data_field = attributes.get('Parent Data Field', {}).get('value', None)
        parent_data_field_guid = attributes.get('Parent Data Field', {}).get('guid', None)

        anchor_scope_guid = attributes.get('Anchor Scope GUID', {}).get('value', None)

        collection_type = object_type
        replace_all_props = True
        if not valid:
            if exists and object_action == "Create":
                msg = (f"Create failed because Element `{display_name}` exists - changing `Create` to `Update` in "
                       f"processed output \n")
                logger.error(msg)
                return update_a_command(txt, object_action, object_type, qualified_name, guid)
            else:
                return None
        elif object_action == "Update" and not exists:
            logger.error(f"Element `{display_name}` does not exist! Updating result document with Create "
                         f"object_action\n")
            return update_a_command(txt, object_action, object_type, qualified_name, guid)

        else:
            print(Markdown(f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))

        try:
            if object_action == "Update":
                body = {
                    "class": "UpdateDataStructureRequestBody", "externalSourceGUID": external_source_guid,
                    "externalSourceName": external_source_name, "effectiveTime": effective_time,
                    "forLineage": for_lineage, "forDuplicateProcessing": for_duplicate_processing, "properties": {
                        "class": "DataStructureProperties", "qualifiedName": qualified_name,
                        "displayName": display_name, "description": description, "namespace": namespace,
                        "versionIdentifier": version_id, "additionalProperties": additional_properties,
                        "effectiveFrom": effective_from, "effectiveTo": effective_to
                        }
                    }
                egeria_client.update_data_structure_w_body(guid, body, replace_all_props)
                logger.info(f"Updated element `{display_name}` with GUID {guid}")
                core_props = egeria_client.get_data_structure_by_guid(guid, output_format='MD')

                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })

                update_data_collection_memberships(egeria_client, object_type, data_spec_guid_list,
                                                   "Data Specification", guid, display_name, replace_all_props)
                core_props += f"## In Data Dictionary\n\n{data_dict_name_list}\n\n"
                core_props += f"## In Data Specification\n\n{data_spec_name_list}\n\n"
                return core_props

            elif object_action == "Create":
                if exists:
                    logger.warning(f"\nTerm `{display_name}` already exists and result document updated\n")
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

                        core_props = egeria_client.get_data_structure_by_guid(guid, output_format='MD')

                        if in_data_dictionary:
                            logger.info(f"Will add to data dictionary(s) `{in_data_dictionary}`")
                            result = add_member_to_data_collections(egeria_client, in_data_dictionary, display_name,
                                                                    guid)
                            core_props += f"## In Data Dictionary\n\n{data_dict_name_list}\n\n"

                        if in_data_spec:
                            result = add_member_to_data_collections(egeria_client, data_spec_guid_list, display_name,
                                                                    guid)
                            core_props += f"## In Data Specifications\n\n`{data_spec_name_list}`\n\n"

                        logger.info(f"Created Element `{display_name}` with GUID {guid}")

                        return core_props
                    else:
                        logger.error(f"Failed to create Data Structure `{display_name}`")
                        return None


        except Exception as e:
            logger.error(f"Error performing {object_action}: {e}")
            Console().print_exception(show_locals=True)
            return None
    else:
        return None

@logger.catch
def process_data_field_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a data field create or update object_action by extracting key attributes such as
    spec name, parent_guid, parent_relationship_type, parent_at_end_1, collection_type

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    from md_processing.md_processing_utils.common_md_utils import set_debug_level

    set_debug_level(directive)

    command, object_type, object_action = extract_command_plus(txt)

    parsed_output = parse_upsert_command(egeria_client, object_type, object_action, txt, directive)
    attributes = parsed_output['attributes']
    display_name = attributes['Display Name'].get('value', None)
    qualified_name = parsed_output.get('qualified_name', None)
    guid = parsed_output.get('guid', None)
    valid = parsed_output['valid']
    exists = parsed_output['exists']

    print(Markdown(parsed_output['display']))

    if directive == "display":

        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
            logger.error(msg)
        return valid

    elif directive == "process":
        logger.debug(json.dumps(parsed_output, indent=4))

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

        glossary_term = attributes['Glossary Term'].get('value', None)
        glossary_term_guid = attributes['Glossary Term'].get('guid', None)

        merge_update = attributes.get('Merge Update', {}).get('value', None)

        position = attributes.get('Position', {}).get('value', None)
        min_cardinality = attributes.get('Minimum Cardinality', {}).get('value', None)
        max_cardinality = attributes.get('Maximum Cardinality', {}).get('value', None)

        in_data_structure = attributes.get('In Data Structure', {}).get('value', None)
        data_structure_guid_list = attributes.get('In Data Structure', {}).get('guid_list', None)
        in_data_structure_names = attributes.get('In Data Structure Names', {}).get('name_list', None)

        data_class = attributes.get('Data Class', {}).get('value', None)
        glossary_term = attributes.get('Glossary Term', {}).get('value', None)

        glossary_term_guid = attributes.get('Glossary Term', {}).get('guid', None)

        # name_details_list = attributes.get("dict_list", None)

        in_data_spec = attributes.get("In Data Specification", {}).get("value", None)  # this is a [dict]
        data_spec_name_list = attributes.get("In Data Specification", {}).get("name_list", None)
        data_spec_guid_list = attributes.get("In Data Specification", {}).get("guid_list", None)

        in_data_dictionary = attributes.get('In Data Dictionary', {}).get('value', None)
        in_data_dictionary_names = attributes.get('In Data Dictionary', {}).get('name_list', None)
        data_dict_guid_list = attributes.get("In Data Dictionary", {}).get("guid_list", None)

        parent_data_field = attributes.get('Parent Data Field', {}).get('value', None)
        parent_data_field_guids = attributes.get('Parent Data Field', {}).get('guid_list', None)
        parent_data_field_names = attributes.get('Parent Data Field', {}).get('name_list', None)


        anchor_scope_guid = attributes.get('Anchor Scope GUID', {}).get('value', None)

        replace_all_props = not merge_update

        if not valid:
            if exists and object_action == "Create":
                msg = (f"Create failed because Element `{display_name}` exists - changing `Create` to `Update` in "
                       f"processed output \n")
                logger.error(msg)
                return update_a_command(txt, object_action, object_type, qualified_name, guid)
            else:
                return None
        else:
            print(Markdown(f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))

        try:
            if object_action == "Update":
                if not exists:
                    logger.error(f"Element `{display_name}` does not exist! Updating result document with Create "
                                 f"object_action\n")
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)

                # first update the base data field
                body = {
                    "class": "UpdateDataFieldRequestBody", "externalSourceGUID": external_source_guid,
                    "externalSourceName": external_source_name, "effectiveTime": effective_time,
                    "forLineage": for_lineage, "forDuplicateProcessing": for_duplicate_processing, "properties": {
                        "class": "DataFieldProperties", "qualifiedName": qualified_name, "displayName": display_name,
                        "namespace": namespace, "description": description, "versionIdentifier": version_id,
                        "aliases": aliases, "namePatterns": name_patterns, "isDeprecated": False,
                        "isNullable": is_nullable, "defaultValue": default_value, "dataType": data_type,
                        "minimumLength": min_length, "length": length, "precision": precision,
                        "orderedValues": ordered_values, "sortOrder": sort_order,
                        "additionalProperties": additional_properties, "effectiveFrom": effective_from,
                        "effectiveTo": effective_to
                        }
                    }

                egeria_client.update_data_field(guid, body, not merge_update)
                logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}")
                # Update data dictionary membership
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                core_props = egeria_client.get_data_field_by_guid(guid, None,'MD')

                # existing_data_field = egeria_client.get_data_field_by_guid(guid, output_format='JSON')

                # Sync membership in data dictionaries
                update_data_collection_memberships(egeria_client, object_type, data_dict_guid_list, "Data Dictionary",
                                                   guid, display_name, replace_all_props)
                logger.success(f"Updating data dictionaries `{in_data_dictionary_names}`")
                core_props += f"\n\n## In Data Dictionary\n\n{in_data_dictionary_names}\n\n"

                # Sync data field related elements (data structure, parent data fields, terms, data classes
                sync_data_field_rel_elements(egeria_client, data_structure_guid_list, parent_data_field_guids,
                                             [glossary_term_guid], data_class, guid, display_name, replace_all_props)
                core_props += f"\n\n## In Data Structure {in_data_structure_names}\n\n"
                core_props += f"\n\n## Glossary Term \n\n{glossary_term}\n\n"
                core_props += f"\n\n## Parent Data Field\n\n{parent_data_field_names}\n\n"
                core_props += "\n___\n\n"

                # Update data classes
                logger.success(f"Updated Element `{display_name}`")
                return core_props

            elif object_action == "Create":
                if valid is False and exists:
                    logger.error(
                        f"\nData Field `{display_name}` already exists and result document updated changing `Create` "
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
                        core_props = egeria_client.get_data_field_by_guid(guid, None,'MD')

                        # Add the field to any data dictionaries
                        if in_data_dictionary:
                            logger.info(f"Will add to data dictionary `{in_data_dictionary}`")
                            add_member_to_data_collections(egeria_client, data_dict_guid_list, display_name, guid)
                            core_props += f"\n\n## In Data Dictionary\n\n{in_data_dictionary_names}\n\n"

                        # Add the field to any data structures
                        if in_data_structure:
                            core_props += f"\n\n## In Data Structure\n\n{in_data_structure_names}\n\n"
                            for ds_guid in data_structure_guid_list:
                                # todo This is too naive? - need to better accommodate the relationship
                                df_body = {
                                    "class": "MemberDataFieldRequestBody", "properties": {
                                        "class": "MemberDataFieldProperties", "dataFieldPosition": position,
                                        "minCardinality": min_cardinality, "maxCardinality": max_cardinality,
                                        }
                                    }

                                msg = f"Adding field to structure {ds_guid}"
                                logger.info(msg)
                                egeria_client.link_member_data_field(ds_guid, guid, df_body)
                            core_props += f"\n\n## In Data Structure {in_data_structure_names}\n\n"

                        if glossary_term:
                            if glossary_term_guid:
                                glossary_body = {
                                    "class": "MetadataSourceRequestBody", "externalSourceGUID": external_source_guid,
                                    "externalSourceName": external_source_name, "effectiveTime": effective_time,
                                    "forLineage": for_lineage, "forDuplicateProcessing": for_duplicate_processing
                                    }

                                core_props += f"\n\n## Glossary Term \n\n{glossary_term}\n\n"
                                egeria_client.link_semantic_definition(guid, glossary_term_guid, glossary_body)

                        if parent_data_field_guids:
                            # parent_df_body = {
                            #     "class": "MetadataSourceRequestBody", "externalSourceGUID": external_source_guid,
                            #     "externalSourceName": external_source_name, "effectiveTime": effective_time,
                            #     "forLineage": for_lineage, "forDuplicateProcessing": for_duplicate_processing
                            #     }

                            # egeria_client.link_nested_data_field(parent_data_field_guid, guid, parent_df_body)
                            for parent_guid in parent_data_field_guids:
                                egeria_client.link_nested_data_field(parent_guid, guid)
                            core_props += f"\n\n## Parent Data Field\n\n{parent_data_field_names}\n\n"

                        # Link data class
                        # if data_class:
                        #     egeria_client.link_data_class_definition(guid, data_class)
                        #     msg = f"Adding data class `{data_class}` to data field {display_name}"
                        #     logger.info(msg)

                        logger.success(f"Created Element `{display_name}`")
                        core_props += "\n___\n\n"
                        return core_props

                    else:
                        logger.error(f"Failed to create Term `{display_name}`")
                        return None

        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            Console().print_exception(show_locals=True)
            return None
    else:
        return None


@logger.catch
def process_data_class_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a data class create or update object_action by extracting key attributes such as
    spec name, parent_guid, parent_relationship_type, parent_at_end_1, collection_type

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """

    command, object_type, object_action = extract_command_plus(txt)

    parsed_output = parse_upsert_command(egeria_client, object_type, object_action, txt, directive)

    attributes = parsed_output['attributes']
    display_name = attributes['Display Name'].get('value', None)
    qualified_name = parsed_output.get('qualified_name', None)
    guid = parsed_output.get('guid', None)
    valid = parsed_output['valid']
    exists = parsed_output['exists']

    print(Markdown(parsed_output['display']))

    if directive == "display":

        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
            logger.error(msg)
        return valid

    elif directive == "process":
        logger.debug(json.dumps(parsed_output, indent=4))

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

        namespace = attributes.get('Namespace', {}).get('value', None)
        description = attributes.get('Description', {}).get('value', None)
        version_id = attributes.get('Version Identifier', {}).get('value', None)

        ###############
        match_property_names = attributes.get('Match Property Names', {}).get('value', [])
        specification_details = attributes.get('Specification Details', {}).get('value', {})
        match_threshold = attributes.get('Match Threshold', {}).get('value', 0)
        specification = attributes.get('Specification', {}).get('value', None)
        data_type = attributes.get('Data Type', {}).get('value', None)
        is_nullable = attributes.get('Is Nullable', {}).get('value', True)
        allow_duplicates = attributes.get('Allow Duplicates', {}).get('value', True)
        default_value = attributes.get('Default Value', {}).get('value', None)
        average_value = attributes.get('Average Value', {}).get('value', None)
        value_list = attributes.get('Value List', {}).get('value', None)
        value_range_from = attributes.get('Value Range From', {}).get('value', None)
        value_range_to = attributes.get('Value Range To', {}).get('value', None)
        sample_values = attributes.get('Sample Values', {}).get('value', [])
        data_patterns = attributes.get('Data Patterns', {}).get('value', [])
        additional_properties = attributes.get('Additional Properties', {}).get('value', {})


        ###############
        aliases = attributes.get('Aliases', {}).get('value', None)
        name_patterns = attributes.get('Name Patterns', {}).get('value', None)



        min_length = attributes.get('Minimum Length', {}).get('value', None)
        length = attributes.get('Length', {}).get('value', None)
        precision = attributes.get('Precision', {}).get('value', None)
        ordered_values = attributes.get('Ordered Values', {}).get('value', None)
        sort_order = attributes.get('Sort Order', {}).get('value', None)
        effective_from = attributes.get('Effective From', {}).get('value', None)
        effective_to = attributes.get('Effective To', {}).get('value', None)

        glossary_term = attributes.get('Glossary Term',{}).get('value', None)
        glossary_term_guid = attributes.get('Glossary Term',{}).get('guid', None)

        merge_update = attributes.get('Merge Update', {}).get('value', None)

        position = attributes.get('Position', {}).get('value', None)
        min_cardinality = attributes.get('Minimum Cardinality', {}).get('value', None)
        max_cardinality = attributes.get('Maximum Cardinality', {}).get('value', None)

        in_data_structure = attributes.get('In Data Structure', {}).get('value', None)
        data_structure_guid_list = attributes.get('In Data Structure', {}).get('guid_list', None)
        in_data_structure_names = attributes.get('In Data Structure Names', {}).get('name_list', None)

        data_class = attributes.get('Data Class', {}).get('value', None)
        glossary_term = attributes.get('Glossary Term', {}).get('value', None)

        glossary_term_guid = attributes.get('Glossary Term', {}).get('guid', None)

        in_data_dictionary = attributes.get('In Data Dictionary', {}).get('value', None)
        in_data_dictionary_names = attributes.get('In Data Dictionary', {}).get('name_list', None)
        data_dict_guid_list = attributes.get("In Data Dictionary", {}).get("guid_list", None)

        containing_data_class = attributes.get('Containing Data Class', {}).get('value', None)
        containing_data_class_guids = attributes.get('Containing Data Class', {}).get('guid_list', None)
        containing_data_class_names = attributes.get('Containing Data Class', {}).get('name_list', None)

        specializes_data_class = attributes.get('Specializes Data Class', {}).get('value', None)
        specializes_data_class_guid = attributes.get('Specializes Data Class', {}).get('guid', None)
        specializes_data_class_name = attributes.get('Specializes Data Class', {}).get('name', None)


        anchor_scope_guid = attributes.get('Anchor Scope GUID', {}).get('value', None)


        replace_all_props = not merge_update

        if not valid:
            if exists and object_action == "Create":
                msg = (f"Create failed because Element `{display_name}` exists - changing `Create` to `Update` in "
                       f"processed output \n")
                logger.error(msg)
                return update_a_command(txt, object_action, object_type, qualified_name, guid)
            else:
                return None
        else:
            print(Markdown(f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))

        try:
            if object_action == "Update":
                if not exists:
                    logger.error(f"Element `{display_name}` does not exist! Updating result document with Create "
                                 f"object_action\n")
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)

                # first update the base data class
                body = {
                  "class" : "UpdateDataClassRequestBody",
                  "externalSourceGUID": external_source_guid,
                  "externalSourceName": external_source_name,
                  "effectiveTime" : effective_time,
                  "forLineage" : for_lineage,
                  "forDuplicateProcessing" : for_duplicate_processing,
                  "properties": {
                    "class" : "DataClassProperties",
                    "qualifiedName": qualified_name,
                    "displayName": display_name,
                    "description": description,
                    "namespace": namespace,
                    "matchPropertyNames": match_property_names,
                    "matchThreshold": match_threshold,
                    "specification": specification,
                    "specificationDetails": specification_details,
                    "dataType": data_type,
                    "allowsDuplicateValues": allow_duplicates,
                    "isNullable": is_nullable,
                    "defaultValue": default_value,
                    "averageValue": average_value,
                    "valueList": value_list,
                    "valueRangeFrom": value_range_from,
                    "valueRangeTo": value_range_to,
                    "sampleValues": sample_values,
                    "dataPatterns" : data_patterns,
                    "additionalProperties": additional_properties
                  }
                }

                egeria_client.update_data_class(guid, body, not merge_update)
                logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}")
                # Update data dictionary membership
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                core_props = egeria_client.get_data_class_by_guid(guid, None,'MD')

                # Sync membership in data dictionaries
                update_data_collection_memberships(egeria_client, object_type, data_dict_guid_list, "Data Dictionary",
                                                   guid, display_name, replace_all_props)
                logger.success(f"Updating data dictionaries `{in_data_dictionary_names}`")
                core_props += f"\n\n## In Data Dictionary\n\n{in_data_dictionary_names}\n\n"

                # Sync data field related elements (data structure, parent data fields, terms, data classes
                sync_data_class_rel_elements(egeria_client, containing_data_class_guids,
                                             [glossary_term_guid],specializes_data_class_guid,
                                             [glossary_term_guid], guid, display_name, replace_all_props)

                core_props += f"\n\n## Glossary Term \n\n{glossary_term}\n\n"
                core_props += f"\n\n## Containing Data Class\n\n{containing_data_class_names}\n\n"
                core_props += "\n___\n\n"

                # Update data classes
                logger.success(f"Updated Element `{display_name}`")
                return core_props

            elif object_action == "Create":
                if valid is False and exists:
                    logger.error(
                        f"\nData Class `{display_name}` already exists and result document updated changing `Create` "
                        f"to `Update` in processed output\n")
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                else:
                    # First lets create the data class
                    body = {
                        "properties": {
                            "class": "DataClassProperties",
                            "qualifiedName": qualified_name,
                            "displayName": display_name,
                            "description": description,
                            "namespace": namespace,
                            "matchPropertyNames": match_property_names,
                            "matchThreshold": match_threshold,
                            "specification": specification,
                            "specificationDetails": specification_details,
                            "dataType": data_type,
                            "allowsDuplicateValues": allow_duplicates,
                            "isNullable": is_nullable,
                            "defaultValue": default_value,
                            "averageValue": average_value,
                            "valueList": value_list,
                            "valueRangeFrom": value_range_from,
                            "valueRangeTo": value_range_to,
                            "sampleValues": sample_values,
                            "dataPatterns": data_patterns,
                            "additionalProperties": additional_properties
                            }
                        }
                    guid = egeria_client.create_data_class(body)
                    if guid:
                        # Now update our element dictionary with the new information
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        # Start assembling the information we will present back out
                        core_props = egeria_client.get_data_class_by_guid(guid, None,'MD')

                        # Add the field to any data dictionaries
                        if in_data_dictionary:
                            logger.info(f"Will add to data dictionary `{in_data_dictionary}`")
                            add_member_to_data_collections(egeria_client, data_dict_guid_list, display_name, guid)
                            core_props += f"\n\n## In Data Dictionary\n\n{in_data_dictionary_names}\n\n"

                        if glossary_term:
                            if glossary_term_guid:
                                glossary_body = {
                                    "class": "MetadataSourceRequestBody", "externalSourceGUID": external_source_guid,
                                    "externalSourceName": external_source_name, "effectiveTime": effective_time,
                                    "forLineage": for_lineage, "forDuplicateProcessing": for_duplicate_processing
                                    }

                                core_props += f"\n\n## Glossary Term \n\n{glossary_term}\n\n"
                                egeria_client.link_semantic_definition(guid, glossary_term_guid, glossary_body)

                        if containing_data_class_guids:
                            for dc_guid in containing_data_class_guids:
                                egeria_client.link_nested_data_class(dc_guid, guid)
                            core_props += f"\n\n## Parent Data Field\n\n{containing_data_class_names}\n\n"


                        if specializes_data_class_guid:
                            egeria_client.link_specialist_data_class(specializes_data_class_guid, guid)
                            core_props += f"\n\n## Specialized Data Field\n\n{specializes_data_class_name}\n\n"


                        logger.success(f"Created Element `{display_name}`")
                        core_props += "\n___\n\n"
                        return core_props

                    else:
                        logger.error(f"Failed to create Term `{display_name}`")
                        return None

        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            Console().print_exception(show_locals=True)
            return None
    else:
        return None





@logger.catch
def process_data_dict_list_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a Data Dictionary list object_action by extracting key attributes such as
     search string from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting term-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    command, object_type, object_action = extract_command_plus(txt)

    parsed_output = parse_view_command(egeria_client, object_type, object_action, txt, directive)

    attributes = parsed_output['attributes']

    valid = parsed_output['valid']

    print(Markdown(parsed_output['display']))

    if directive == "display":
        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
            logger.error(msg)
        return valid

    elif directive == "process":
        attributes = parsed_output['attributes']
        search_string = attributes.get('Search String', {}).get('value', '*')
        output_format = attributes.get('Output Format', {}).get('value', 'LIST')
        detailed = attributes.get('Detailed', {}).get('value', False)

        try:
            if not valid:  # First validate the command before we process it
                msg = f"Validation failed for {object_action} `{object_type}`\n"
                logger.error(msg)
                return None

            list_md = f"\n# Data Dictionaries with filter: `{search_string}`\n\n"
            if output_format == "DICT":
                struct = egeria_client.get_classified_collections('DataDictionary', output_format=output_format)
                list_md += f"```{json.dumps(struct, indent=4)}```\n"
            else:
                list_md += egeria_client.find_collections(search_string, output_format=output_format)
            logger.info(f"Wrote Dictionaries for search string: `{search_string}`")

            return list_md

        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            console.print_exception(show_locals=True)
            return None
    else:
        return None


# @logger.catch
# def process_list_data_dictionary_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
#     """
#     Processes a list data dictionary.
#
#     :param txt: A string representing the input cell to be processed for
#         extracting term-related attributes.
#     :param directive: an optional string indicating the directive to be used - display, validate or execute
#     :return: A string summarizing the outcome of the processing.
#     """
#
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
