"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This file contains term-related object_action functions for processing Egeria Markdown


"""

import json
import os
import sys
from typing import Optional

from loguru import logger
from rich import print
from rich.console import Console
from rich.markdown import Markdown

from md_processing.md_processing_utils.common_md_proc_utils import (parse_upsert_command, parse_view_command )
from md_processing.md_processing_utils.common_md_utils import (
    update_element_dictionary,
    set_find_body,
    set_create_body,
    set_element_prop_body,
    set_update_body,
    set_rel_request_body,
    set_update_status_body,
    set_rel_prop_body,
    set_data_field_body,
)
# Developer note: Request bodies follow a two-layer pattern:
# - Outer: action wrapper (NewElementRequestBody/UpdateElementRequestBody/...)
# - Inner: element-specific Properties dict placed under the outer["properties"] key
# Always build inner bodies via helpers (set_element_prop_body, set_data_field_body, etc.) and assign to the outer
from md_processing.md_processing_utils.extraction_utils import (extract_command_plus, update_a_command)
from md_processing.md_processing_utils.md_processing_constants import (load_commands, ERROR)
from pyegeria import DEBUG_LEVEL, body_slimmer
from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.utils import make_format_set_name_from_type

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


#
# Helper functions for the data designer commands
#
@logger.catch
def add_member_to_data_collections(egeria_client: EgeriaTech, collection_list: list, display_name: str,
                                   guid: str) -> None:
    """
    Add member to data dictionaries and data specifications.
    """
    body = {
        "class": "NewRelationshipRequestBody", "properties": {
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
def remove_member_from_data_collections(egeria_client: EgeriaTech, collection_list: list, display_name: str,
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
            remove_member_from_data_collections(egeria_client, to_remove, display_name, guid)

        # add membership for collections that are in the to-be but are not in the as-is
        to_add = to_be_set - as_is
        logger.debug(f"to_add: {to_add}")
        if len(to_add) > 0:
            add_member_to_data_collections(egeria_client, to_add, display_name, guid)
    else:
        add_member_to_data_collections(egeria_client, guid_list, display_name, guid)


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


@logger.catch
def process_data_spec_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a data specification create or update object_action by extracting key attributes such as
    spec name, parent_guid, parent_relationship_type, parent_at_end_1, category

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

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']
    display_name = attributes.get('Display Name', {}).get('value', "None Found")
    status = attributes.get('Status', {}).get('value', None)
    print(Markdown(parsed_output['display']))

    in_data_spec_list = attributes.get('In Data Specification', {}).get('value', None)
    in_data_spec_valid = attributes.get('In Data Specification', {}).get('valid', None)
    in_data_spec_exists = attributes.get('In Data Specification', {}).get('exists', None)
    output_set = make_format_set_name_from_type(object_type)
    object_type = "DataSpec"
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

                body = set_update_body(object_type, attributes)
                body['properties'] = set_element_prop_body(object_type, qualified_name, attributes)

                egeria_client.update_collection(guid, body)
                if status:
                    egeria_client.update_collection_status(guid, status)

                logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}\n\n___")
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                })
                return egeria_client.get_collection_by_guid(guid, element_type='Data-Specification-DrE',
                                                            output_format='MD', output_format_set=output_set)

            elif object_action == "Create":
                if valid is False and exists:
                    msg = (f"  Data Specification `{display_name}` already exists and result document updated changing "
                           f"`Create` to `Update` in processed output\n\n___")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif valid is False and in_data_spec_valid is False:
                    msg = (f" Invalid data specification(s) `{in_data_spec_list}` "
                           f" invalid data? - Correct and try again\n\n___")
                    logger.error(msg)
                    return None
                else:
                    body = set_create_body(object_type, attributes)
                    body["properties"] = set_element_prop_body(object_type, qualified_name, attributes)
                    parent_guid = body.get('parentGuid', None)
                    if parent_guid:
                        body['parentRelationshipTypeName'] = "CollectionMembership"
                        body['parentAtEnd1'] = True

                    guid = egeria_client.create_collection(body=body)
                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                        })
                        msg = f"Created Element `{display_name}` with GUID {guid}\n\n___"
                        logger.success(msg)
                        return egeria_client.get_collection_by_guid(guid, object_type, output_format='MD', output_format_set=output_set)
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
def process_data_dict_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a data dictionary create or update object_action by extracting key attributes such as
    spec name, parent_guid, parent_relationship_type, parent_at_end_1, category

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
    display_name = attributes.get('Display Name', {}).get('value', "None Found")
    status = attributes.get('Status', {}).get('value', None)
    output_set = make_format_set_name_from_type(object_type)

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

                body = set_update_body(object_type, attributes)
                body['properties'] = set_element_prop_body("Data Spec", qualified_name, attributes)

                egeria_client.update_collection(guid, body)
                if status:
                    egeria_client.update_collection_status(guid, status)

                logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}\n\n___")
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                })
                return egeria_client.get_collection_by_guid(guid, element_type='Data Specification',
                                                            output_format='MD', output_format_set=output_set)

            elif object_action == "Create":
                if valid is False and exists:
                    msg = (f"  Data Specification `{display_name}` already exists and result document updated changing "
                           f"`Create` to `Update` in processed output\n\n___")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif valid is False :
                    msg = f" invalid data? - Correct and try again\n\n___"
                    logger.error(msg)
                    return None
                else:
                    body = set_create_body(object_type, attributes)
                    body["properties"] = set_element_prop_body(object_type, qualified_name, attributes)
                    parent_guid = body.get('parentGuid', None)
                    if parent_guid:
                        body['parentRelationshipTypeName'] = "CollectionMembership"
                        body['parentAtEnd1'] = True

                    guid = egeria_client.create_collection(body=body)
                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                        })
                        msg = f"Created Element `{display_name}` with GUID {guid}\n\n___"
                        logger.success(msg)
                        return egeria_client.get_collection_by_guid(guid, object_type, output_format='MD', output_format_set=output_set)
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
def process_data_structure_upsert_command(egeria_client: EgeriaTech, txt: str,
                                          directive: str = "display") -> Optional[str]:
    """
    Processes a data structure create or update object_action by extracting key attributes such as
    spec name, parent_guid, parent_relationship_type, parent_at_end_1, category

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
    output_set = make_format_set_name_from_type(object_type)

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
        display_name = attributes.get('Display Name', {}).get('value', None)
        qualified_name = attributes.get('Qualified Name',{}).get('value', None)
        if qualified_name is None:
            qualified_name = attributes.get('Display Name',{}).get('qualified_name', None)
            if qualified_name is None:
                logger.error(f"Element `{display_name}` does not have a valid specification? No qualified name..Review..\n\n___ ")
                return None
        prop_body = set_element_prop_body(object_type, qualified_name, attributes)
        prop_body['namespace'] = attributes.get('Namespace', {}).get('value', None)
        display_name = attributes.get('Display Name',{}).get('value', None)

        data_spec_name_list = attributes.get("In Data Specification", {}).get("name_list", "")
        data_spec_value = attributes.get("In Data Specification", {}).get("value", None)
        data_spec_guid_list = attributes.get("In Data Specification", {}).get("guid_list", None)

        in_data_dictionary = attributes.get('In Data Dictionary', {}).get('dict_list', None)
        data_dict_name_list = attributes.get('In Data Dictionary', {}).get('name_list', "")
        data_dict_value_list = attributes.get('In Data Dictionary', {}).get('value', None)
        data_dict_guid_list = attributes.get("In Data Dictionary", {}).get("guid_list", None)
        merge_update = attributes.get('Merge Update', {}).get('value', True)

        try:
            if object_action == "Update":
                if not exists:
                    logger.error(f"Element `{qualified_name}` does not exist! Updating result document with Create "
                                 f"object_action\n\n___")
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif not valid:
                    logger.error(f"Element `{qualified_name}` does not have a valid specification? Review..\n\n___ ")
                    return None
                else:
                    update_body = set_update_body(object_type,attributes)
                    update_body['properties'] = prop_body
                    egeria_client.update_data_structure(guid, update_body)
                    update_element_dictionary(qualified_name, {
                        'guid': guid, 'display_name': display_name
                        })
                    logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}\n\n___")

                    core_props = egeria_client.get_data_structure_by_guid(guid, output_format='MD', output_format_set=output_set)

                    update_element_dictionary(qualified_name, {
                        'guid': guid, 'display_name': display_name
                    })

                    update_data_collection_memberships(egeria_client, object_type, data_spec_guid_list, "DataSpec", guid,
                                                       display_name, merge_update)
                    update_data_collection_memberships(egeria_client, object_type, data_dict_guid_list, "DataSpec",
                                                       guid,display_name, merge_update)
                    core_props += f"## In Data Dictionary\n\n{data_dict_name_list}\n\n"
                    core_props += f"## In Data Specification\n\n{data_spec_name_list}\n\n"
                    logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}\n\n___")
                    return core_props


            if not valid:
                if exists and object_action == "Create":
                    msg = (f"Create failed because Element `{display_name}` exists - changing `Create` to `Update` in "
                           f"processed output \n\n___")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                else:
                    return None


            elif object_action == "Create":
                if exists:
                    logger.warning(f"\nTerm `{display_name}` already exists and result document updated\n\n___")
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                else:
                    body = set_create_body(object_type, attributes)
                    body['properties'] = prop_body
                    guid = egeria_client.create_data_structure(body_slimmer(body))
                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })

                        core_props = egeria_client.get_data_structure_by_guid(guid, output_format='MD', output_format_set=output_set)

                        if in_data_dictionary:
                            logger.info(f"Will add to data dictionary(s) `{in_data_dictionary}`")
                            add_member_to_data_collections(egeria_client, data_dict_guid_list,
                                                                    display_name,guid)
                            core_props += f"## In Data Dictionary\n\n{data_dict_name_list}\n\n"

                        if data_spec_guid_list:
                            add_member_to_data_collections(egeria_client, data_spec_guid_list,
                                                                    display_name, guid)
                            core_props += f"## In Data Specifications\n\n`{data_spec_name_list}`\n\n"

                        logger.info(f"Created Element `{display_name}` with GUID {guid}\n\n___")

                        return core_props
                    else:
                        logger.error(f"Failed to create Data Structure `{display_name}`\n\n___")
                        return None

        except Exception as e:
            logger.error(f"Error performing {object_action}: {e}\n\n___")
            return None
        else:
            return None


@logger.catch
def process_data_field_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a data field create or update object_action by extracting key attributes such as
    spec name, parent_guid, parent_relationship_type, parent_at_end_1, category

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    from md_processing.md_processing_utils.common_md_utils import set_debug_level

    set_debug_level(directive)

    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))

    parsed_output = parse_upsert_command(egeria_client, object_type, object_action, txt, directive)
    attributes = parsed_output['attributes']
    display_name = attributes['Display Name'].get('value', None)
    qualified_name = parsed_output.get('qualified_name', None)
    guid = parsed_output.get('guid', None)
    valid = parsed_output['valid']
    exists = parsed_output['exists']
    output_set = make_format_set_name_from_type(object_type)

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


        merge_update = attributes.get('Merge Update', {}).get('value', None)

        position = attributes.get('Position', {}).get('value', None)
        min_cardinality = attributes.get('Minimum Cardinality', {}).get('value', None)
        max_cardinality = attributes.get('Maximum Cardinality', {}).get('value', None)

        in_data_structure = attributes.get('In Data Structure', {}).get('value', None)
        data_structure_guid_list = attributes.get('In Data Structure', {}).get('guid_list', None)
        in_data_structure_names = attributes.get('In Data Structure Names', {}).get('name_list', None)

        data_class = attributes.get('Data Class', {}).get('value', None)
        data_class_guid = attributes.get('Data Class', {}).get('guid', None)
        glossary_term = attributes.get('Glossary Term', {}).get('value', None)
        glossary_term_guid = attributes.get('Glossary Term', {}).get('guid', None)
        if glossary_term_guid:
            glossary_term_guid = [glossary_term_guid]

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
                       f"processed output\n\n___")
                logger.error(msg)
                return update_a_command(txt, object_action, object_type, qualified_name, guid)
            else:
                msg = f"Invalid specification - please review\n\n___"
                logger.error(msg)
                return None
        else:
            print(Markdown(f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))

        props_body = set_data_field_body(object_type, qualified_name, attributes)

        try:
            if object_action == "Update":
                if not exists:
                    logger.error(f"Element `{display_name}` does not exist! Updating result document with Create "
                                 f"object_action\n\n___")
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)

                # first update the base data field
                body = set_update_body(object_type, attributes)
                body['properties'] = props_body
                egeria_client.update_data_field(guid, body)
                logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}")
                # Update data dictionary membership
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                core_props = egeria_client.get_data_field_by_guid(guid, output_format='MD', output_format_set=output_set)  ## update back to by_guid?

                # existing_data_field = egeria_client.get_data_field_by_guid(guid, output_format='JSON')

                # Sync membership in data dictionaries
                update_data_collection_memberships(egeria_client, object_type, data_dict_guid_list, "DataDictionary",
                                                   guid, display_name, replace_all_props)
                logger.success(f"Updating data dictionaries `{in_data_dictionary_names}`")
                core_props += f"\n\n## In Data Dictionary\n\n{in_data_dictionary_names}\n\n"

                # Sync data field related elements (data structure, parent data fields, terms, data classes
                sync_data_field_rel_elements(egeria_client, data_structure_guid_list, parent_data_field_guids,
                                             glossary_term_guid, data_class_guid, guid, display_name, replace_all_props)
                core_props += f"\n\n## In Data Structure {in_data_structure_names}\n\n"
                core_props += f"\n\n## Glossary Term \n\n{glossary_term}\n\n"
                core_props += f"\n\n## Parent Data Field\n\n{parent_data_field_names}\n\n"
                core_props += f"\n\n## Data Class\n\n{data_class}\n\n"
                core_props += "\n_______________________________________________________________________________\n\n"

                # Update data classes
                logger.success(f"Updated Element `{display_name}`\n\n___")
                return core_props

            elif object_action == "Create":
                if valid is False and exists:
                    logger.error(
                        f"\nData Field `{display_name}` already exists and result document updated changing `Create` "
                        f"to `Update` in processed output\n\n___")
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                else:
                    # First lets create the data field
                    body = set_create_body(object_type, attributes)
                    body['properties'] = props_body
                    parent_guid = body.get('parentGuid', None)

                    guid = egeria_client.create_data_field(body)
                    if guid:
                        # Now update our element dictionary with the new information
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        # Start assembling the information we will present back out
                        core_props = egeria_client.get_data_field_by_guid(guid, 'MD', output_format_set=output_set)

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
                                prop_body = set_rel_prop_body("MemberDataFieldProperties", attributes)
                                prop_body["position"] = position
                                prop_body["minimumCardinality"] = min_cardinality
                                prop_body["maximumCardinality"] = max_cardinality

                                body = set_rel_request_body(object_type, attributes)
                                body['properties'] = prop_body

                                msg = f"Adding field to structure {ds_guid}"
                                logger.info(msg)
                                egeria_client.link_member_data_field(ds_guid, guid, body)
                            core_props += f"\n\n## In Data Structure {in_data_structure_names}\n\n"

                        if glossary_term:
                            if glossary_term_guid:
                                term_body = set_rel_prop_body("GlossaryTermProperties", attributes)
                                body = set_rel_request_body(object_type, attributes)
                                body['properties'] = term_body

                                core_props += f"\n\n## Glossary Term \n\n{glossary_term}\n\n"
                                egeria_client.link_semantic_definition(guid, glossary_term_guid, term_body)

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
                        if data_class:
                            prop_body = set_rel_prop_body("DataClassProperties", attributes)
                            body = set_rel_request_body(object_type, attributes)
                            body['properties'] = prop_body

                            core_props += f"\n\n## Data Class\n\n{data_class}\n\n"
                            egeria_client.link_data_class_definition(guid, data_class_guid, body)
                            msg = f"Adding data class `{data_class}` to data field {display_name}"
                            logger.info(msg)

                        logger.success(f"Created Element `{display_name}` with guid `{guid}`")
                        logger.success("=====================================================\n\n")
                        core_props += "\n___\n\n"
                        return core_props

                    else:
                        logger.error(f"Failed to create Term `{display_name}`\n\n___")
                        return None

        except Exception as e:
            logger.error(f"Error performing {command}: {e}\n\n___")
            return None
    else:
        return None


@logger.catch
def process_data_class_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a data class create or update object_action by extracting key attributes such as
    spec name, parent_guid, parent_relationship_type, parent_at_end_1, category

    :param txt: A string representing the input cell to be processed for
        extracting glossary-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """

    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))

    parsed_output = parse_upsert_command(egeria_client, object_type, object_action, txt, directive)

    attributes = parsed_output['attributes']
    display_name = attributes['Display Name'].get('value', None)
    qualified_name = parsed_output.get('qualified_name', None)
    guid = parsed_output.get('guid', None)
    valid = parsed_output['valid']
    exists = parsed_output['exists']
    output_set = make_format_set_name_from_type(object_type)

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
        for_lineage = attributes.get('For Lineage', {}).get('value', False)
        for_duplicate_processing = attributes.get('For Duplicate Processing', {}).get('value', False)
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
        output_set = make_format_set_name_from_type(object_type)

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

        glossary_term = attributes.get('Glossary Term', {}).get('value', None)
        glossary_term_guid = attributes.get('Glossary Term', {}).get('guid', None)

        merge_update = attributes.get('Merge Update', {}).get('value', True)

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
                       f"processed output\n\n___")
                logger.error(msg)
                return update_a_command(txt, object_action, object_type, qualified_name, guid)
            else:
                msg = f"Invalid specification - please review\n\n___"
                return None
        else:
            print(Markdown(f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))

        try:
            if object_action == "Update":
                if not exists:
                    logger.error(f"Element `{display_name}` does not exist! Updating result document with Create "
                                 f"object_action\n\n___")
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)

                # first update the base data class
                body = {
                    "class": "UpdateElementRequestBody", "externalSourceGUID": external_source_guid,
                    "externalSourceName": external_source_name, "effectiveTime": effective_time,
                    "forLineage": for_lineage, "forDuplicateProcessing": for_duplicate_processing, "properties": {
                        "class": "DataClassProperties", "qualifiedName": qualified_name, "displayName": display_name,
                        "description": description, "namespace": namespace, "matchPropertyNames": match_property_names,
                        "matchThreshold": match_threshold, "specification": specification,
                        "specificationDetails": specification_details, "dataType": data_type,
                        "allowsDuplicateValues": allow_duplicates, "isNullable": is_nullable,
                        "defaultValue": default_value, "averageValue": average_value, "valueList": value_list,
                        "valueRangeFrom": value_range_from, "valueRangeTo": value_range_to,
                        "sampleValues": sample_values, "dataPatterns": data_patterns,
                        "additionalProperties": additional_properties
                        }
                    }

                egeria_client.update_data_class(guid, body, not merge_update)
                logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}")
                # Update data dictionary membership
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                core_props = egeria_client.get_data_class_by_guid(guid, None, 'MD', output_format_set=output_set)

                # Sync membership in data dictionaries
                update_data_collection_memberships(egeria_client, object_type, data_dict_guid_list, "DataDictionary",
                                                   guid, display_name, replace_all_props)
                logger.success(f"Updating data dictionaries `{in_data_dictionary_names}`")
                core_props += f"\n\n## In Data Dictionary\n\n{in_data_dictionary_names}\n\n"

                # Sync data field related elements (data structure, parent data fields, terms, data classes
                sync_data_class_rel_elements(egeria_client, containing_data_class_guids, glossary_term_guid,
                                             specializes_data_class_guid, guid, display_name, replace_all_props)

                core_props += f"\n\n## Glossary Term \n\n{glossary_term}\n\n"
                core_props += f"\n\n## Containing Data Class\n\n{containing_data_class_names}\n\n"
                core_props += "\n___\n\n"

                # Update data classes
                logger.success(f"Updated Element `{display_name}`\n\n___")
                return core_props

            elif object_action == "Create":
                if valid is False and exists:
                    logger.error(
                        f"\nData Class `{display_name}` already exists and result document updated changing `Create` "
                        f"to `Update` in processed output\n\n___")
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                else:
                    # First lets create the data class
                    body = {
                        "class": "NewElementRequestBody", "properties": {
                            "class": "DataClassProperties", "qualifiedName": qualified_name,
                            "displayName": display_name, "description": description, "namespace": namespace,
                            "matchPropertyNames": match_property_names, "matchThreshold": match_threshold,
                            "specification": specification, "specificationDetails": specification_details,
                            "dataType": data_type, "allowsDuplicateValues": allow_duplicates, "isNullable": is_nullable,
                            "defaultValue": default_value, "averageValue": average_value, "valueList": value_list,
                            "valueRangeFrom": value_range_from, "valueRangeTo": value_range_to,
                            "sampleValues": sample_values, "dataPatterns": data_patterns,
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
                        core_props = egeria_client.get_data_class_by_guid(guid, None, 'MD', output_format_set=output_set)

                        # Add the field to any data dictionaries
                        if in_data_dictionary:
                            logger.info(f"Will add to data dictionary `{in_data_dictionary}`")
                            add_member_to_data_collections(egeria_client, data_dict_guid_list, display_name, guid)
                            core_props += f"\n\n## In Data Dictionary\n\n{in_data_dictionary_names}\n\n"

                        if glossary_term:
                            if glossary_term_guid:
                                glossary_body = {
                                    "class": "RelationshipRequestBody", "externalSourceGUID": external_source_guid,
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
                        logger.error(f"Failed to create Term `{display_name}`\n\n___")
                        return None

        except Exception as e:
            logger.error(f"Error performing {command}: {e}\n\n___")
            return None
    else:
        return None

