"""
This file contains product manager commands for processing Egeria Markdown
"""
import json
import os
import sys
from typing import Optional

from loguru import logger
from rich import print
from rich.console import Console
from rich.markdown import Markdown

from md_processing.md_processing_utils.common_md_proc_utils import (parse_upsert_command, parse_view_command)
from md_processing.md_processing_utils.common_md_utils import update_element_dictionary, setup_log, set_update_body, \
    set_element_status_request_body, set_prop_body, set_metadata_source_request_body, set_peer_gov_def_request_body, \
    set_rel_request_body, set_create_body, set_collection_classifications, set_collection_property_body
from md_processing.md_processing_utils.extraction_utils import (extract_command_plus, update_a_command)
from md_processing.md_processing_utils.md_processing_constants import (load_commands, ERROR)
from pyegeria import DEBUG_LEVEL, body_slimmer, to_pascal_case
from pyegeria.egeria_tech_client import EgeriaTech

GERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("EGERIA_VIEW_SERVER", "view-server")
EGERIA_VIEW_SERVER_URL = os.environ.get("EGERIA_VIEW_SERVER_URL", "https://localhost:9443")
EGERIA_INTEGRATION_DAEMON = os.environ.get("EGERIA_INTEGRATION_DAEMON", "integration-daemon")
EGERIA_INTEGRATION_DAEMON_URL = os.environ.get("EGERIA_INTEGRATION_DAEMON_URL", "https://localhost:9443")
EGERIA_ADMIN_USER = os.environ.get("ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_WIDTH = os.environ.get("EGERIA_WIDTH", 220)
EGERIA_JUPYTER = os.environ.get("EGERIA_JUPYTER", False)
EGERIA_HOME_GLOSSARY_GUID = os.environ.get("EGERIA_HOME_GLOSSARY_GUID", None)
EGERIA_GLOSSARY_PATH = os.environ.get("EGERIA_GLOSSARY_PATH", None)
EGERIA_ROOT_PATH = os.environ.get("EGERIA_ROOT_PATH", "../../")
EGERIA_INBOX_PATH = os.environ.get("EGERIA_INBOX_PATH", "md_processing/dr_egeria_inbox")
EGERIA_OUTBOX_PATH = os.environ.get("EGERIA_OUTBOX_PATH", "md_processing/dr_egeria_outbox")

load_commands('commands.json')
debug_level = DEBUG_LEVEL

console = Console(width=int(200))
setup_log()


#
# Helper functions for the data designer commands
#
@logger.catch
def add_member_to_collections(egeria_client: EgeriaTech, collection_list: list, display_name: str,
                                   guid: str) -> None:
    """
    Add member to data dictionaries and data specifications.
    """
    body = {
        "class": "RelationshipRequestBody", "properties": {
            "class": "CollectionMembershipProperties", "membershipRationale": "User Specified",
            "notes": "Added by Dr.Egeria"
            }
        }
    try:
        if collection_list is not None:
            for collection in collection_list:
                egeria_client.add_to_collection(collection, guid, body)
                msg = f"Added `{display_name}` member to `{collection}`"
                logger.info(msg)
        else:
            logger.info("There were no data collections to add.")
        return

    except Exception as e:
        console.print_exception()


@logger.catch
def remove_member_from_collections(egeria_client: EgeriaTech, collection_list: list, display_name: str,
                                        guid: str) -> None:
    try:
        for collection in collection_list:
            egeria_client.remove_from_collection(collection, guid)
            msg = f"Removed `{display_name}` member from `{collection}`"
            logger.info(msg)
        return

    except Exception as e:
        console.print_exception()


@logger.catch
def update_data_collection_memberships(egeria_client: EgeriaTech, entity_type: str, guid_list: list,
                                       collection_class: str, guid: str, display_name: str,
                                       replace_all_props: bool = True) -> None:
    """ update the collection membership of the element

        If replace_all_props is set to True, all existing memberships are removed and new memberships are added.
        If replace_all_props is set to False, only the new memberships are added.
    """

    if replace_all_props:
        match entity_type:
            case "Data Specification":
                get_command = egeria_client.get_collection_by_guid
            case "Data Structure":
                get_command = egeria_client.get_data_structure_by_guid
            case "Data Field":
                get_command = egeria_client.get_data_field_by_guid
            case "Data Class":
                get_command = egeria_client.get_data_class_by_guid

        coll_list = egeria_client.get_data_memberships(get_command, guid)
        if coll_list is None:
            logger.warning("Unexpected -> the collection list was None - assigning empty dict")
            coll_list = {}
        # compare the existing collections to desired collections
        if collection_class == "DataDictionary":
            as_is = set(coll_list.get("DictList", {}))
        elif collection_class == "DataSpec":
            as_is = set(coll_list.get("SpecList", {}))

        dict_set = set(coll_list.get("DictList", {}))
        spec_set = set(coll_list.get("SpecList", {}))
        to_be_set = set(guid_list) if guid_list is not None else set()
        logger.debug(f"as_is: {as_is}")
        logger.debug(f"to_be_set: {to_be_set}")

        # Remove membership for collections that are in the as-is but not in the to-be
        to_remove = as_is - to_be_set
        logger.debug(f"to_remove: {to_remove}")
        if len(to_remove) > 0:
            remove_member_from_collections(egeria_client, to_remove, display_name, guid)

        # add membership for collections that are in the to-be but are not in the as-is
        to_add = to_be_set - as_is
        logger.debug(f"to_add: {to_add}")
        if len(to_add) > 0:
            add_member_to_collections(egeria_client, to_add, display_name, guid)
    else:
        add_member_to_collections(egeria_client, guid_list, display_name, guid)


# @logger.catch


@logger.catch
def add_field_to_data_structures(egeria_client: EgeriaTech, display_name: str, struct_list: list, guid) -> None:
    """
        Add data field to data structures.
        """

    try:
        for structure_guid in struct_list:
            egeria_client.link_member_data_field(structure_guid, guid, None)
            msg = f"Added `{display_name}` to structure `{structure_guid}`"
            logger.info(msg)
        return

    except Exception as e:
        console.print_exception()


@logger.catch
def remove_field_from_data_structures(egeria_client: EgeriaTech, display_name: str, struct_list: list,
                                      guid: str) -> None:
    """Remove a data field from a list of data structures."""
    try:
        for structure_guid in struct_list:
            egeria_client.detach_member_data_field(structure_guid, guid, None)
            msg = f"Removed `{display_name}` from structure `{structure_guid}`"
            logger.info(msg)
        return

    except Exception as e:
        console.print_exception()


@logger.catch
def sync_data_field_rel_elements(egeria_client: EgeriaTech, structure_list: list, parent_field_list: list, terms: list,
                                 data_class_guid: str, guid: str, display_name: str,
                                 replace_all_props: bool = True) -> None:
    """Sync a field's related elements.

    TODO: Need to add data class support when ready and may need to revisit bodies.

    """
    if terms:
        terms = [terms]

    if replace_all_props:
        rel_el_list = egeria_client.get_data_field_rel_elements(guid)
        # should I throw an exception if empty?
        if rel_el_list is None:
            logger.warning("Unexpected -> the list was None - assigning empty list")
            rel_el_list = {}

        as_is_data_structs = set(rel_el_list.get("data_structure_guids", []))
        as_is_parent_fields = set(rel_el_list.get("parent_guids", []))
        as_is_assigned_meanings = set(rel_el_list.get("assigned_meanings_guids", []))
        as_is_data_classes = set(rel_el_list.get("data_class_guids", []))

        to_be_data_structs = set(structure_list) if structure_list is not None else set()
        to_be_parent_fields = set(parent_field_list) if parent_field_list is not None else set()
        to_be_assigned_meanings = set(terms) if terms is not None else set()
        to_be_data_classes = set([data_class_guid]) if data_class_guid is not None else set()

        logger.trace(f"as_is_data_structs: {list(as_is_data_structs)} to_be_data_struct: {list(to_be_data_structs)}")
        logger.trace(
            f"as_is_parent_fields: {list(as_is_parent_fields)} to_be_parent_fields: {list(to_be_parent_fields)}")
        logger.trace(f"as_is_assigned_meanings: {list(as_is_assigned_meanings)} to_be_assigned_meanings: "
                     f"{list(to_be_assigned_meanings)}")
        logger.trace(f"as_is_data_classes: {list(as_is_data_classes)} to_be_assigned_data_classes: "
                     f"{list(to_be_data_classes)}")

        data_struct_to_remove = as_is_data_structs - to_be_data_structs
        logger.trace(f"data_struct_to_remove: {list(data_struct_to_remove)}")
        if len(data_struct_to_remove) > 0:
            for ds in data_struct_to_remove:
                egeria_client.detach_member_data_field(ds, guid, None)
                msg = f"Removed `{display_name}` from structure `{ds}`"
                logger.trace(msg)
        data_struct_to_add = to_be_data_structs - as_is_data_structs
        logger.trace(f"data_struct_to_add: {list(data_struct_to_add)}")
        if len(data_struct_to_add) > 0:
            for ds in data_struct_to_add:
                egeria_client.link_member_data_field(ds, guid, None)
                msg = f"Added `{display_name}` to structure `{ds}`"
                logger.trace(msg)

        parent_field_to_remove = to_be_parent_fields - as_is_parent_fields
        logger.trace(f"parent_field_to_remove: {list(parent_field_to_remove)}")
        if len(parent_field_to_remove) > 0:
            for field in parent_field_to_remove:
                egeria_client.detach_nested_data_field(field, guid, None)
                msg = f"Removed `{display_name}` from field `{field}`"
                logger.trace(msg)
        parent_field_to_add = to_be_parent_fields - as_is_parent_fields
        logger.trace(f"parent_field_to_add: {list(parent_field_to_add)}")
        if len(parent_field_to_add) > 0:
            for field in parent_field_to_add:
                egeria_client.link_nested_data_field(field, guid, None)
                msg = f"Added `{display_name}` to field `{field}`"
                logger.trace(msg)

        terms_to_remove = as_is_assigned_meanings - to_be_assigned_meanings
        logger.trace(f"terms_to_remove: {list(terms_to_remove)}")
        if terms:
            for term in terms_to_remove:
                egeria_client.detach_semantic_definition(guid, term, None)
                msg = f"Removed `{term}` from `{display_name}`"
                logger.trace(msg)
        terms_to_add = to_be_assigned_meanings - as_is_assigned_meanings
        logger.trace(f"terms_to_add: {list(terms_to_add)}")
        if len(terms_to_add) > 0:
            for term in terms_to_add:
                egeria_client.link_semantic_definition(guid, term, None)
                msg = f"Added `{term}` to`{display_name}`"
                logger.trace(msg)

        classes_to_remove = as_is_data_classes - to_be_data_classes
        logger.trace(f"classes_to_remove: {list(classes_to_remove)}")
        if len(terms_to_remove) > 0:
            for dc in classes_to_remove:
                body = {
                    "class": "MetadataSourceRequestBody", "forLineage": False, "forDuplicateProcessing": False
                    }
                egeria_client.detach_data_class_definition(guid, dc, body)
                msg = f"Removed `{dc}` from `{display_name}`"
                logger.trace(msg)
        classes_to_add = to_be_data_classes - as_is_data_classes
        logger.trace(f"classes_to_add: {list(classes_to_add)}")
        if len(terms_to_add) > 0:
            for dc in classes_to_add:
                body = {
                    "class": "RelationshipRequestBody", "forLineage": False, "forDuplicateProcessing": False
                    }
                egeria_client.link_data_class_definition(guid, dc, body)
                msg = f"Added `{dc}` to`{display_name}`"
                logger.trace(msg)


    else:  # merge - add field to related elements
        if structure_list:
            add_field_to_data_structures(egeria_client, display_name, structure_list, guid)
            msg = f"Added `{display_name}` to `{structure_list}`"
            logger.trace(msg)

        if parent_field_list:
            for field in parent_field_list:
                egeria_client.link_nested_data_field(field, guid, None)
                msg = f"Added `{display_name}` to `{field}`"
                logger.trace(msg)
        if terms:
            for term in terms:
                egeria_client.link_semantic_definition(guid, term, None)
                msg = f"Added `{term}` to `{display_name}`"
                logger.trace(msg)

        if data_class_guid:
            egeria_client.link_data_class_definition(guid, data_class_guid)
            msg = f"Added `{data_class_guid}` to `{display_name}`"
            logger.trace(msg)


@logger.catch
def sync_data_class_rel_elements(egeria_client: EgeriaTech, containing_data_class_guids: list, terms: list,
                                 specializes_data_classes: list, guid: str, display_name: str,
                                 replace_all_props: bool = True) -> None:
    """Sync a data class' related elements.

    """
    if terms:
        terms = [terms]

    if replace_all_props:
        rel_el_list = egeria_client.get_data_class_rel_elements(guid)
        if rel_el_list is None:
            logger.warning("Unexpected -> the list was None - assigning empty list")
            rel_el_list = {}
        if terms:
            terms = [terms]

        as_is_nested_classes = set(rel_el_list.get("nested_data_class_guids", []))
        as_is_assigned_meanings = set(rel_el_list.get("assigned_meanings_guids", []))
        as_is_specialized_classes = set(rel_el_list.get("specialized_data_class_guids", []))

        to_be_nested_classes = set(containing_data_class_guids) if containing_data_class_guids is not None else set()
        to_be_assigned_meanings = set(terms) if terms is not None else set()
        to_be_specialized_classes = set([specializes_data_classes]) if specializes_data_classes is not None else set()

        logger.trace(
            f"as_is_nested_classes: {list(as_is_nested_classes)} to_be_nested_classes: {list(to_be_nested_classes)}")
        logger.trace(f"as_is_assigned_meanings: {list(as_is_assigned_meanings)} to_be_assigned_meanings: "
                     f"{list(to_be_assigned_meanings)}")
        logger.trace(f"as_is_specialized_classes: {list(as_is_specialized_classes)} to_be_specizialized_data_classes: "
                     f"{list(to_be_specialized_classes)}")

        nested_classes_to_remove = to_be_nested_classes - as_is_nested_classes
        logger.trace(f"nested_classes_to_remove: {list(nested_classes_to_remove)}")
        if len(nested_classes_to_remove) > 0:
            for field in nested_classes_to_remove:
                egeria_client.detach_nested_data_class(field, guid, None)
                msg = f"Removed `{display_name}` from field `{field}`"
                logger.trace(msg)
        nested_classes_to_add = to_be_nested_classes - as_is_nested_classes
        logger.trace(f"nested_classes_to_add: {list(nested_classes_to_add)}")
        if len(nested_classes_to_add) > 0:
            for field in nested_classes_to_add:
                egeria_client.link_nested_data_class(field, guid, None)
                msg = f"Added `{display_name}` to field `{field}`"
                logger.trace(msg)

        terms_to_remove = as_is_assigned_meanings - to_be_assigned_meanings
        logger.trace(f"terms_to_remove: {list(terms_to_remove)}")
        if len(terms_to_remove) > 0:
            for term in terms_to_remove:
                egeria_client.detach_semantic_definition(guid, term, None)
                msg = f"Removed `{term}` from `{display_name}`"
                logger.trace(msg)
        terms_to_add = to_be_assigned_meanings - as_is_assigned_meanings
        logger.trace(f"terms_to_add: {list(terms_to_add)}")
        if len(terms_to_add) > 0:
            for term in terms_to_add:
                egeria_client.link_semantic_definition(guid, term, None)
                msg = f"Added `{term}` to`{display_name}`"
                logger.trace(msg)

        specialized_classes_to_remove = as_is_specialized_classes - to_be_specialized_classes
        logger.trace(f"classes_to_remove: {list(specialized_classes_to_remove)}")
        if len(terms_to_remove) > 0:
            for dc in specialized_classes_to_remove:
                body = {
                    "class": "MetadataSourceRequestBody", "forLineage": False, "forDuplicateProcessing": False
                    }
                egeria_client.detach_specialist_data_class(guid, dc, body)
                msg = f"Removed `{dc}` from `{display_name}`"
                logger.trace(msg)
        specialized_classes_to_add = to_be_specialized_classes - as_is_specialized_classes
        logger.trace(f"classes_to_add: {list(specialized_classes_to_add)}")
        if len(specialized_classes_to_add) > 0:
            for dc in specialized_classes_to_add:
                body = {
                    "class": "RelationshipRequestBody", "forLineage": False, "forDuplicateProcessing": False
                    }
                egeria_client.link_specialist_data_class(guid, dc, body)
                msg = f"Added `{dc}` to`{display_name}`"
                logger.trace(msg)


    else:  # merge - add field to related elements
        if containing_data_class_guids:
            for field in containing_data_class_guids:
                egeria_client.link_nested_data_class(field, guid, None)
                msg = f"Added `{display_name}` to `{field}`"
                logger.trace(msg)

        if terms:
            for term in terms:
                egeria_client.link_semantic_definition(guid, term, None)
                msg = f"Added `{term}` to `{display_name}`"
                logger.trace(msg)
        if specializes_data_classes:
            for el in specializes_data_classes:
                egeria_client.link_specialist_data_class(guid, el)
            msg = f"Linked `{el}` to `{display_name}`"
            logger.trace(msg)
#
# Product Manager Commands
#

@logger.catch
def process_collection_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a digital product create or update object_action by extracting key attributes such as
    spec name, parent_guid, parent_relationship_type, parent_at_end_1, collection_type

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
    description = attributes.get('Description',{}).get('value', None)
    user_defined_status = attributes.get('User Defined Status',{}).get('value', None)

    collection_classification = attributes.get('Collection Classification', {}).get('value', None)

    current_version = attributes.get('Version Identifier',{}).get('value', None)

    # status = attributes.get('Status',{}).get('value', "ACTIVE")

    anchor_guid = attributes.get('Anchor ID', {}).get('guid', None)
    parent_guid = attributes.get('Parent ID', {}).get('guid', None)
    parent_relationship_type_name = attributes.get('Parent Relationship Type Name', {}).get('value', None)
    parent_relationship_type_name = attributes.get('Parent Relationship Type Name', {}).get('value',"CollectionMembership")
    parent_at_end1 = attributes.get('Parent at End1', {}).get('value', True)
    anchor_scope_guid = attributes.get('Anchor Scope GUID', {}).get('value', None)
    is_own_anchor = attributes.get('Is Own Anchor', {}).get('value', True)
    if parent_guid is None:
        is_own_anchor = True


    additional_prop = attributes.get('Additional Properties', {}).get('value', None)
    additional_properties = json.loads(additional_prop) if additional_prop is not None else None
    extended_prop = attributes.get('Extended Properties', {}).get('value', None)
    extended_properties = json.loads(extended_prop) if extended_prop is not None else None
    external_source_guid = attributes.get('External Source Name', {}).get('guid', None)
    external_source_name = attributes.get('External Source Name', {}).get('value', None)
    effective_time = attributes.get('Effective Time', {}).get('value', None)
    for_lineage = attributes.get('For Lineage', {}).get('value', None)
    for_duplicate_processing = attributes.get('For Duplicate Processing', {}).get('value', None)

    replace_all_props = not attributes.get('Merge Update', {}).get('value', True)

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
                prop_body = set_collection_property_body(object_type,qualified_name,attributes)

                body = set_update_body(object_type, attributes)
                body['properties'] = set_collection_property_body(object_type,qualified_name,attributes)

                egeria_client.update_collection_w_body(guid, body)
                # egeria_client.update_collection_status(guid, status)

                logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}\n\n___")
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                return egeria_client.get_collection_by_guid(guid, collection_type='Data Specification',
                                                            output_format='MD')


            elif object_action == "Create":
                if valid is False and exists:
                    msg = (f"  Digital Product `{display_name}` already exists and result document updated changing "
                           f"`Create` to `Update` in processed output\n\n___")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)

                else:
                    body = set_create_body(object_type,attributes)
                    body["initialClassifications"] = set_collection_classifications(object_type, attributes)
                    body["properties"] = set_collection_property_body(object_type, qualified_name,attributes)


                    guid = egeria_client.create_collection_w_body(body)
                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        msg = f"Created Element `{display_name}` with GUID {guid}\n\n___"
                        logger.success(msg)
                        return egeria_client.get_collection_by_guid(guid, collection_type='Digital Product',
                                                                    output_format='MD')
                    else:
                        msg = f"Failed to create element `{display_name}` with GUID {guid}\n\n___"
                        logger.error(msg)
                        return None

        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            return None
    else:
        return None

@logger.catch
def process_digital_product_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a digital product create or update object_action by extracting key attributes such as
    spec name, parent_guid, parent_relationship_type, parent_at_end_1, collection_type

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """

    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))

    parsed_output = parse_upsert_command(egeria_client, object_type, object_action, txt, directive)

    valid = parsed_output['valid']
    exists = parsed_output['exists']

    qualified_name = parsed_output.get('qualified_name', None)
    guid = parsed_output.get('guid', None)

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']

    display_name = attributes['Display Name'].get('value', None)
    description = attributes.get('Description',{}).get('value', None)
    user_defined_status = attributes.get('User Defined Status',{}).get('value', None)
    product_identifier = attributes.get('Product Identifier',{}).get('value', None)
    product_name = attributes.get('Product Name',{}).get('value', None)
    product_type = attributes.get('Product Type',{}).get('value', None)



    product_description = attributes.get('Product Description',{}).get('value', None)
    maturity = attributes.get('Maturity',{}).get('value', None)
    service_life = attributes.get('Service Life',{}).get('value', None)
    introduction_date = attributes.get('Introduction Date',{}).get('value', None)
    next_version_date = attributes.get('Next Version Date',{}).get('value', None)
    withdrawal_date = attributes.get('Withdrawal Date',{}).get('value', None)

    collection_type = attributes.get('Collection Type', {}).get('value', None)
    current_version = attributes.get('Version Identifier',{}).get('value', None)
    product_manager = attributes.get('Product Manager',{}).get('value', None)


    product_status = attributes.get('Status',{}).get('value', "ACTIVE")

    anchor_guid = attributes.get('Anchor ID', {}).get('guid', None)
    parent_guid = attributes.get('Parent ID', {}).get('guid', None)
    parent_relationship_type_name = attributes.get('Parent Relationship Type Name', {}).get('value', None)
    parent_relationship_type_name = attributes.get('Parent Relationship Type Name', {}).get('value',"CollectionMembership")
    parent_at_end1 = attributes.get('Parent at End1', {}).get('value', True)
    anchor_scope_guid = attributes.get('Anchor Scope GUID', {}).get('value', None)
    is_own_anchor = attributes.get('Is Own Anchor', {}).get('value', True)
    if parent_guid is None:
        is_own_anchor = True


    additional_prop = attributes.get('Additional Properties', {}).get('value', None)
    additional_properties = json.loads(additional_prop) if additional_prop is not None else None
    extended_prop = attributes.get('Extended Properties', {}).get('value', None)
    extended_properties = json.loads(extended_prop) if extended_prop is not None else None
    external_source_guid = attributes.get('External Source Name', {}).get('guid', None)
    external_source_name = attributes.get('External Source Name', {}).get('value', None)
    effective_time = attributes.get('Effective Time', {}).get('value', None)
    for_lineage = attributes.get('For Lineage', {}).get('value', None)
    for_duplicate_processing = attributes.get('For Duplicate Processing', {}).get('value', None)

    replace_all_props = not attributes.get('Merge Update', {}).get('value', True)

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
                prop_body = set_prop_body(object_type,qualified_name,attributes)

                body ={
                    "class": "UpdateElementRequestBody",
                    "properties": {
                        "class": "DigitalProductProperties",
                        "qualifiedName": qualified_name,
                        "userDefinedStatus": user_defined_status,
                        "name": display_name,
                        "description": description,
                        "identifier": product_identifier,
                        "productName": product_name,
                        "productType": product_type,
                        "maturity": maturity,
                        "serviceLife": service_life,
                        "introductionDate": introduction_date,
                        "nextVersionDate": next_version_date,
                        "withdrawDate": withdrawal_date,
                        "currentVersion": current_version,
                        "additionalProperties": additional_properties,
                        "extendedProperties": extended_properties,
                        },
                    "externalSourceGUID": external_source_guid,
                    "externalSourceName": external_source_name,
                    "effectiveTime": effective_time,
                    "forLineage": for_lineage,
                    "forDuplicateProcessing": for_duplicate_processing
                    }

                egeria_client.update_digital_product(guid, body)
                egeria_client.update_digital_product_status(guid, product_status)

                logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}\n\n___")
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                return egeria_client.get_collection_by_guid(guid, collection_type='Data Specification',
                                                            output_format='MD')


            elif object_action == "Create":
                if valid is False and exists:
                    msg = (f"  Digital Product `{display_name}` already exists and result document updated changing "
                           f"`Create` to `Update` in processed output\n\n___")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)

                else:
                    body = {
                        "class": "NewDigitalProductRequestBody",
                        "isOwnAnchor": is_own_anchor,
                        "parentGUID": parent_guid,
                        "parentRelationshipTypeName": parent_relationship_type_name,
                        "parentAtEnd1": parent_at_end1,
                        "properties": {
                            "class": "DigitalProductProperties",
                            "qualifiedName": qualified_name,
                            "userDefinedStatus": user_defined_status,
                            "name": display_name,
                            "description" : description,
                            "identifier": product_identifier,
                            "productName": product_name,
                            "productType": product_type,
                            "maturity": maturity,
                            "serviceLife": service_life,
                            "introductionDate": introduction_date,
                            "nextVersionDate": next_version_date,
                            "withdrawDate": withdrawal_date,
                            "currentVersion": current_version,

                            "additionalProperties": additional_properties,
                            "extendedProperties": extended_properties,
                            },
                        "initialStatus": product_status,
                        "externalSourceGUID": external_source_guid,
                        "externalSourceName": external_source_name,
                        "effectiveTime" : effective_time,
                        "forLineage": for_lineage,
                        "forDuplicateProcessing": for_duplicate_processing
                        }



                    guid = egeria_client.create_digital_product(body)
                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        msg = f"Created Element `{display_name}` with GUID {guid}\n\n___"
                        logger.success(msg)
                        return egeria_client.get_collection_by_guid(guid, collection_type='Digital Product',
                                                                    output_format='MD')
                    else:
                        msg = f"Failed to create element `{display_name}` with GUID {guid}\n\n___"
                        logger.error(msg)
                        return None

        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            return None
    else:
        return None

@logger.catch
def process_agreement_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes an agreement create or update object_action by extracting key attributes such as
    spec name, parent_guid, parent_relationship_type, parent_at_end_1, collection_type

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """

    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))

    parsed_output = parse_upsert_command(egeria_client, object_type, object_action, txt, directive)

    valid = parsed_output['valid']
    exists = parsed_output['exists']

    qualified_name = parsed_output.get('qualified_name', None)
    guid = parsed_output.get('guid', None)

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']

    display_name = attributes['Display Name'].get('value', None)
    description = attributes.get('Description',{}).get('value', None)
    user_defined_status = attributes.get('User Defined Status',{}).get('value', None)
    agreement_status = attributes.get('Status',{}).get('value', None)
    agreement_identifier = attributes.get('Agreement Identifier',{}).get('value', None)

    version_identifier = attributes.get('Version Identifier',{}).get('value', None)

    actors = attributes.get('Agreement Actors',{}).get('value', None)
    actor_names = attributes.get('Agreement Actors',{}).get('name_list', None)
    actor_guids = attributes.get('Agreement Actors',{}).get('guid_list', None)
    anchor_guid = attributes.get('Anchor ID', {}).get('guid', None)
    parent_guid = attributes.get('Parent ID', {}).get('guid', None)
    parent_relationship_type_name = attributes.get('Parent Relationship Type Name', {}).get('value', None)
    parent_relationship_type_name = attributes.get('Parent Relationship Type Name', {}).get('value',"CollectionMembership")
    parent_at_end1 = attributes.get('Parent at End1', {}).get('value', True)
    anchor_scope_guid = attributes.get('Anchor Scope GUID', {}).get('value', None)
    is_own_anchor = attributes.get('Is Own Anchor', {}).get('value', True)
    if parent_guid is None:
        is_own_anchor = True


    additional_prop = attributes.get('Additional Properties', {}).get('value', None)
    additional_properties = json.loads(additional_prop) if additional_prop is not None else None
    extended_prop = attributes.get('Extended Properties', {}).get('value', None)
    extended_properties = json.loads(extended_prop) if extended_prop is not None else None
    external_source_guid = attributes.get('External Source Name', {}).get('guid', None)
    external_source_name = attributes.get('External Source Name', {}).get('value', None)
    effective_time = attributes.get('Effective Time', {}).get('value', None)
    for_lineage = attributes.get('For Lineage', {}).get('value', None)
    for_duplicate_processing = attributes.get('For Duplicate Processing', {}).get('value', None)

    replace_all_props = not attributes.get('Merge Update', {}).get('value', True)

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

                product_body = {
                        "class": "AgreementProperties",
                        "qualifiedName": qualified_name,
                        "userDefinedStatus": user_defined_status,
                        "name": display_name,
                        "description": description,
                        "identifier": agreement_identifier,
                        "additionalProperties": additional_properties,
                        "extendedProperties": extended_properties,
                    }

                body = set_update_body(object_type, attributes)
                body['properties'] = product_body

                egeria_client.update_agreement(guid, body, replace_all_props)
                status_update_body = set_element_status_request_body(object_type, attributes)
                egeria_client.update_agreement_status(guid, status_update_body)

                logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}\n\n___")
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                return egeria_client.get_collection_by_guid(guid, collection_type='Data Specification',
                                                            output_format='MD')

            elif object_action == "Create":
                if valid is False and exists:
                    msg = (f"  Digital Product `{display_name}` already exists and result document updated changing "
                           f"`Create` to `Update` in processed output\n\n___")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)

                else:
                    body = {
                        "class": "NewAgreementRequestBody",
                        "isOwnAnchor": is_own_anchor,
                        "parentGUID": parent_guid,
                        "parentRelationshipTypeName": parent_relationship_type_name,
                        "parentAtEnd1": parent_at_end1,
                        "properties": {
                            "class": "AgreementProperties",
                            "qualifiedName": qualified_name,
                            "userDefinedStatus": user_defined_status,
                            "name": display_name,
                            "description" : description,
                            "identifier" : agreement_identifier,
                            "additionalProperties": additional_properties,
                            "extendedProperties": extended_properties,
                            },
                        "initialStatus": agreement_status,
                        "externalSourceGUID": external_source_guid,
                        "externalSourceName": external_source_name,
                        "effectiveTime" : effective_time,
                        "forLineage": for_lineage,
                        "forDuplicateProcessing": for_duplicate_processing
                        }
                    if object_type == "Data Sharing Agreement":
                        guid = egeria_client.create_data_sharing_agreement(body)
                    elif object_type == "Agreement":
                        guid = egeria_client.create_agreement(body)

                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        msg = f"Created Element `{display_name}` with GUID {guid}\n\n___"
                        logger.success(msg)
                        return egeria_client.get_collection_by_guid(guid, collection_type='Digital Product',
                                                                    output_format='MD')
                    else:
                        msg = f"Failed to create element `{display_name}` with GUID {guid}\n\n___"
                        logger.error(msg)
                        return None

        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            return None
    else:
        return None


def process_link_agreement_item_command(egeria_client: EgeriaTech, txt: str,
                                        directive: str = "display") -> Optional[str]:
    """
    Processes a link or unlink command to associate or break up peer governance definitions.

    :param txt: A string representing the input cell to be processed for
        extracting blueprint-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))

    parsed_output = parse_view_command(egeria_client, object_type, object_action, txt, directive)

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']
    agreement = attributes.get('Agreement Name',{}).get('value', None)
    agreement_guid = attributes.get('Definition 1', {}).get('guid', None)
    item = attributes.get('Item Name',{}).get('value', None)
    item_guid = attributes.get('Definition 2', {}).get('guid', None)
    label = attributes.get('Link Label', {}).get('value', None)
    description = attributes.get('Description', {}).get('value', None)

    valid = parsed_output['valid']
    exists = agreement_guid is not None and  item_guid is not None


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
            if object_action == "Detach":
                if not exists:
                    msg = (f" Link `{label}` does not exist! Updating result document with Link "
                           f"object_action\n")
                    logger.error(msg)
                    out = parsed_output['display'].replace('Link', 'Detach', 1)
                    return out
                elif not valid:
                    return None
                else:
                    print(Markdown(
                        f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))
                    body = set_metadata_source_request_body(object_type, attributes)
                    item_props = {
                        "class": "AgreementItemProperties",
                        "agreementItemId": attributes["Agreement Item Id"],
                        "agreementStart": attributes["Agreement Start"],
                        "agreementEnd": attributes["Agreement End"],
                        "restrictions": attributes["Restrictions"],
                        "obligations": attributes["Obligations"],
                        "entitlements": attributes["Entitlements"],
                        "usageMeasurements": attributes["Usage Measurements"],
                        "effectiveFrom": attributes["Effective From"],
                        "effectiveTo": attributes["Effective To"]

                        }
                    body['properties'] = item_props
                    egeria_client.detach_agreement_item(agreement_guid, item_guid,body)

                    logger.success(f"===> Detached agreement item `{item}` from agreement `{agreement}`\n")
                    out = parsed_output['display'].replace('Unlink', 'Link', 1)

                    return (out)

            elif object_action == "Link":
                if valid is False and exists:
                    msg = (f"-->  Link called `{label}` already exists and result document updated changing "
                           f"`Link` to `Detach` in processed output\n")
                    logger.error(msg)

                elif valid is False:
                    msg = f"==>{object_type} Link with label `{label}` is not valid and can't be created"
                    logger.error(msg)
                    return

                else:
                    body = set_rel_request_body(object_type, attributes)
                    item_props = {
                        "class": "AgreementItemProperties",
                        "agreementItemId": attributes["Agreement Item Id"],
                        "agreementStart": attributes["Agreement Start"],
                        "agreementEnd": attributes["Agreement End"],
                        "restrictions": attributes["Restrictions"],
                        "obligations": attributes["Obligations"],
                        "entitlements": attributes["Entitlements"],
                        "usageMeasurements": attributes["Usage Measurements"],
                        "effectiveFrom": attributes["Effective From"],
                        "effectiveTo": attributes["Effective To"]

                    }
                    body['properties'] = item_props
                    egeria_client.link_agreement_item(agreement_guid,
                                                        item_guid, body)
                    msg = f"==>Linked {object_type} `{agreement} to item {item}\n"
                    logger.success(msg)
                    out = parsed_output['display'].replace('Link', 'Detach', 1)
                    return out


        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            return None
    else:
        return None



#
# View commands
#
@logger.catch
def process_collection_list_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a Data Dictionary list object_action by extracting key attributes such as
     search string from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting term-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))

    parsed_output = parse_view_command(egeria_client, object_type, object_action, txt, directive)

    col_type = to_pascal_case(object_type) if object_type != "Collections" else None

    valid = parsed_output['valid']
    print(Markdown(f"Performing {command}"))
    print(Markdown(parsed_output['display']))

    attr = parsed_output.get('attributes',{})
    columns = attr.get('Columns',{}).get('value',None).replace("'", '"')

    try:
        columns_list = json.loads(columns)
    except Exception as e:
        print(e)
        exit(1)

    effective_time = attr.get('effectiveTime', {}).get('value', None)
    as_of_time = attr.get('asOfTime', {}).get('value', None)
    for_duplicate_processing = attr.get('forDuplicateProcessing', {}).get('value', False)
    for_lineage = attr.get('forLineage',{}).get('value', False)
    limit_result_by_status = attr.get('limitResultsByStatus',{}).get('value', [])
    sequencing_property = attr.get('sequencingProperty',{}).get('value',"qualifiedName" )
    sequencing_order = attr.get('sequencingOrder',{}).get('value', "PROPERTY_ASCENDING")
    search_string = attr.get('Search String', {}).get('value', '*')
    search_string = search_string if search_string != "*" else None
    output_format = attr.get('Output Format', {}).get('value', 'LIST')
    detailed = attr.get('Detailed', {}).get('value', False)

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
        try:
            if not valid:  # First validate the command before we process it
                msg = f"Validation failed for {object_action} `{object_type}`\n"
                logger.error(msg)
                return None

            list_md = f"\n# `{col_type}` with filter: `{search_string}`\n\n"
            body = {
                    "class": "FilterRequestBody",
                    "asOfTime": as_of_time,
                    "effectiveTime": effective_time,
                    "forLineage": for_lineage,
                    "forDuplicateProcessing": for_duplicate_processing,
                    "limitResultsByStatus": limit_result_by_status,
                    "sequencingOrder": sequencing_order,
                    "sequencingProperty": sequencing_property,
                    "filter": search_string,
                }

            struct = egeria_client.find_collections_w_body(body, col_type,
                                                           output_format = output_format, columns=columns_list)
            if output_format == "DICT":
                list_md += f"```\n{json.dumps(struct, indent=4)}\n```\n"
            else:
                list_md += struct
            logger.info(f"Wrote `{col_type}` for search string: `{search_string}`")

            return list_md

        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            console.print_exception(show_locals=True)
            return None
    else:
        return None

