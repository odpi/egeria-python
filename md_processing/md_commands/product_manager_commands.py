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
from md_processing.md_processing_utils.common_md_utils import update_element_dictionary,  set_update_body, \
    set_element_status_request_body, set_element_prop_body, set_delete_request_body, set_rel_request_body, set_peer_gov_def_request_body, \
    set_rel_request_body, set_create_body, set_object_classifications, set_product_body

from md_processing.md_processing_utils.extraction_utils import (extract_command_plus, update_a_command)
from md_processing.md_processing_utils.md_processing_constants import (load_commands, ERROR)
from pyegeria import DEBUG_LEVEL, body_slimmer, to_pascal_case, PyegeriaException, print_basic_exception, print_exception_table
from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.utils import make_format_set_name_from_type

EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
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
LOCAL_QUALIFIER = os.environ.get("EGERIA_LOCAL_QUALIFIER", None)

load_commands('commands.json')
debug_level = DEBUG_LEVEL

console = Console(width=int(200))


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


#
# Product Manager Commands
#

@logger.catch
def process_collection_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a digital product create or update object_action by extracting key attributes such as
    spec name, parent_guid, parent_relationship_type, parent_at_end_1, category

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



    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']

    display_name = attributes['Display Name'].get('value', None)
    version = attributes['Version Identifier'].get('value', None)
    status = attributes.get('Status', {}).get('value', None)
    output_set = make_format_set_name_from_type(object_type)
    if object_type in ["Root Collection", "Folder"]:
        obj = "Collection"
        if object_type == "Folder":
            qn_prefix = "Folder"
        elif object_type == "Root Collection":
            qn_prefix = "Root"

        qualified_name = egeria_client.__create_qualified_name__(qn_prefix, display_name, LOCAL_QUALIFIER,
                                                                 version_identifier=version)

    else:
        obj = object_type
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
                           f"`{object_action}`\n")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif not valid:
                    return None
                else:
                    print(Markdown(
                        f"==> Validation of `{command}` completed successfully! Proceeding to apply the changes.\n"))
                prop_body = set_element_prop_body(obj, qualified_name, attributes)

                body = set_update_body(obj, attributes)
                body['properties'] = set_element_prop_body(obj, qualified_name, attributes)

                egeria_client.update_collection(guid, body)
                if status:
                    egeria_client.update_collection_status(guid, status)

                logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}\n\n___")
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                return egeria_client.get_collection_by_guid(guid, element_type= obj,
                                                            output_format='MD', output_format_set=output_set)


            elif object_action == "Create":
                if valid is False and exists:
                    msg = (f"  Digital Product `{display_name}` already exists and result document updated changing "
                           f"`Create` to `Update` in processed output\n\n___")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)

                else:
                    body = set_create_body(object_type,attributes)

                    # if this is a root or folder (maybe more in the future), then make sure that the classification is set.
                    body["initialClassifications"] = set_object_classifications(object_type, attributes, ["Folder", "Root Collection"])
                    body["properties"] = set_element_prop_body(obj, qualified_name, attributes)
                    parent_guid = body.get('parentGuid', None)
                    if parent_guid:
                        body['parentRelationshipTypeName'] = "CollectionMembership"
                        body['parentAtEnd1'] = True

                    guid = egeria_client.create_collection(body = body)
                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        msg = f"\nCreated Element `{display_name}` with GUID {guid}\n\n___"
                       # todo - add the source member asset to the product manager
                       # create_elem_from_template
                       # add this guid to the product collection
                        logger.success(msg)
                        return egeria_client.get_collection_by_guid(guid, obj, output_format='MD', output_format_set=output_set)
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

@logger.catch
def process_digital_product_upsert_command(egeria_client: EgeriaTech, txt: str,
                                           directive: str = "display") -> Optional[str]:
    """
    Processes a digital product create or update object_action by extracting key attributes such as
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

    display_name = attributes['Display Name'].get('value', None)
    product_manager = attributes.get('Product Manager',{}).get('value', None)
    product_status = attributes.get('Product Status',{}).get('value', None)
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
            prop_body = set_product_body(object_type, qualified_name, attributes)

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
                body['properties'] = prop_body
                # Todo: Update product manager later?

                egeria_client.update_digital_product(guid, body)
                # if product_status:
                #     egeria_client.update_digital_product_status(guid, product_status)


                logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}\n\n___")
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                return egeria_client.get_collection_by_guid(guid, element_type='Digital Product',
                                                            output_format='MD', output_format_set=output_set)


            elif object_action == "Create":
                if valid is False and exists:
                    msg = (f"  Digital Product `{display_name}` already exists and result document updated changing "
                           f"`Create` to `Update` in processed output\n\n___")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)

                else:
                    body = set_create_body(object_type, attributes)
                    body["initialClassifications"] = set_object_classifications(object_type, attributes, [])

                    body["properties"] = prop_body

                    guid = egeria_client.create_digital_product(body_slimmer(body))
                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        # Todo: Add product manager link later? Agreements?

                        msg = f"Created Element `{display_name}` with GUID {guid}\n\n___"
                        logger.success(msg)
                        return egeria_client.get_collection_by_guid(guid, element_type='Digital Product',
                                                                    output_format='MD', output_format_set=output_set)
                    else:
                        msg = f"Failed to create element `{display_name}` with GUID {guid}\n\n___"
                        logger.error(msg)
                        return None

        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            return None
    else:
        return None

    # @logger.catch
    # def process_digital_product_catalog_upsert_command(egeria_client: EgeriaTech, txt: str,
    #                                            directive: str = "display") -> Optional[str]:
    #     """
    #     Processes a digital product catalog create or update object_action by extracting key attributes such as
    #     spec name, parent_guid, parent_relationship_type, parent_at_end_1, category
    #
    #     :param txt: A string representing the input cell to be processed for
    #         extracting glossary-related attributes.
    #     :param directive: an optional string indicating the directive to be used - display, validate or execute
    #     :return: A string summarizing the outcome of the processing.
    #     """
    #
    #     command, object_type, object_action = extract_command_plus(txt)
    #     print(Markdown(f"# {command}\n"))
    #
    #     parsed_output = parse_upsert_command(egeria_client, object_type, object_action, txt, directive)
    #
    #     valid = parsed_output['valid']
    #     exists = parsed_output['exists']
    #
    #     qualified_name = parsed_output.get('qualified_name', None)
    #     guid = parsed_output.get('guid', None)
    #
    #     print(Markdown(parsed_output['display']))
    #
    #     logger.debug(json.dumps(parsed_output, indent=4))
    #
    #     attributes = parsed_output['attributes']
    #
    #     display_name = attributes['Display Name'].get('value', None)
    #
    #     output_set = make_format_set_name_from_type(object_type)
    #
    #     if directive == "display":
    #
    #         return None
    #     elif directive == "validate":
    #         if valid:
    #             print(Markdown(f"==> Validation of {command} completed successfully!\n"))
    #         else:
    #             msg = f"Validation failed for object_action `{command}`\n"
    #         return valid
    #
    #     elif directive == "process":
    #         try:
    #             prop_body = set_product_body(object_type, qualified_name, attributes)
    #
    #             if object_action == "Update":
    #                 if not exists:
    #                     msg = (f" Element `{display_name}` does not exist! Updating result document with Create "
    #                            f"object_action\n")
    #                     logger.error(msg)
    #                     return update_a_command(txt, object_action, object_type, qualified_name, guid)
    #                 elif not valid:
    #                     return None
    #                 else:
    #                     print(Markdown(
    #                         f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))
    #
    #                 body = set_update_body(object_type, attributes)
    #                 body['properties'] = prop_body
    #                 # Todo: Update product manager later?
    #
    #                 egeria_client.update_digital_product(guid, body)
    #                 # if product_status:
    #                 #     egeria_client.update_digital_product_status(guid, product_status)
    #
    #                 logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}\n\n___")
    #                 update_element_dictionary(qualified_name, {
    #                     'guid': guid, 'display_name': display_name
    #                 })
    #                 return egeria_client.get_collection_by_guid(guid, element_type='Digital Product',
    #                                                             output_format='MD', output_format_set=output_set)
    #
    #
    #             elif object_action == "Create":
    #                 if valid is False and exists:
    #                     msg = (
    #                         f"  Digital Product `{display_name}` already exists and result document updated changing "
    #                         f"`Create` to `Update` in processed output\n\n___")
    #                     logger.error(msg)
    #                     return update_a_command(txt, object_action, object_type, qualified_name, guid)
    #
    #                 else:
    #                     body = set_create_body(object_type, attributes)
    #                     body["initialClassifications"] = set_object_classifications(object_type, attributes, [])
    #
    #                     body["properties"] = prop_body
    #
    #                     guid = egeria_client.create_digital_product(body_slimmer(body))
    #                     if guid:
    #                         update_element_dictionary(qualified_name, {
    #                             'guid': guid, 'display_name': display_name
    #                         })
    #                         # Todo: Add product manager link later? Agreements?
    #
    #                         msg = f"Created Element `{display_name}` with GUID {guid}\n\n___"
    #                         logger.success(msg)
    #                         return egeria_client.get_collection_by_guid(guid, element_type='Digital Product',
    #                                                                     output_format='MD',
    #                                                                     output_format_set=output_set)
    #                     else:
    #                         msg = f"Failed to create element `{display_name}` with GUID {guid}\n\n___"
    #                         logger.error(msg)
    #                         return None
    #
    #         except Exception as e:
    #             logger.error(f"Error performing {command}: {e}")
    #             return None
    #     else:
    #         return None


@logger.catch
def process_agreement_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes an agreement create or update object_action by extracting key attributes such as
    spec name, parent_guid, parent_relationship_type, parent_at_end_1, category

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
            if object_type in ["Data Sharing Agreement"]:
                obj = "Agreement"
            else:
                obj = object_type

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
                prop_body = set_element_prop_body(obj, qualified_name, attributes)

                body = set_update_body(object_type, attributes)
                body['properties'] = set_element_prop_body(object_type, qualified_name, attributes)

                egeria_client.update_agreement(guid, body)
                # if status is not None and status !={}:
                #     egeria_client.update_agreement_status(guid, status)

                logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}\n\n___")
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                return egeria_client.get_collection_by_guid(guid, element_type='Data Specification',
                                                            output_format='MD', output_format_set=output_set)


            elif object_action == "Create":
                if valid is False and exists:
                    msg = (f"  Digital Product `{display_name}` already exists and result document updated changing "
                           f"`Create` to `Update` in processed output\n\n___")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)

                else:
                    body = set_create_body(object_type, attributes)

                    # if this is a root or folder (maybe more in the future), then make sure that the classification is set.
                    body["initialClassifications"] = set_object_classifications(object_type, attributes,
                                                                                ["Data Sharing Agreement"])
                    body["properties"] = set_element_prop_body(obj, qualified_name, attributes)

                    guid = egeria_client.create_agreement(body=body)
                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        msg = f"Created Element `{display_name}` with GUID {guid}\n\n___"
                        logger.success(msg)
                        return egeria_client.get_collection_by_guid(guid, obj, output_format='MD', output_format_set=output_set)
                    else:
                        msg = f"Failed to create element `{display_name}` with GUID {guid}\n\n___"
                        logger.error(msg)
                        return None

        except PyegeriaException as e:
            logger.error(f"Pyegeria error performing {command}: {e}")
            print_exception_table(e)
            return None
        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
    else:
        return None



@logger.catch
def process_csv_element_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a create CSV element command by extracting key attributes and calling the pyegeria
    api that creates a csv element from template.

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
    output_set = make_format_set_name_from_type(object_type)

    file_name = attributes.get('File Name', {}).get('value', None)
    file_type = attributes.get('File Type', {}).get('value', None)
    file_path = attributes.get('File Path', {}).get('value', None)
    file_encoding = attributes.get('File Encoding', {}).get('value', 'UTF-8')
    file_extension = attributes.get('File Extension', {}).get('value', 'csv')
    file_system_name = attributes.get('File System Name', {}).get('value', None)
    version_identifier = attributes.get('Version Identifier', {}).get('value', None)
    description = attributes.get('Description', {}).get('value', None)

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

            if object_action == "Create":
                if valid is False and exists:
                    msg = (f"  Element `{display_name}` already exists and result document updated changing "
                           f"`Create` to `Update` in processed output\n\n___")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)

                else:
                    guid = egeria_client.get_create_csv_data_file_element_from_template(
                       file_name, file_type, file_path, version_identifier, file_encoding, file_extension, file_system_name, description)

                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        msg = f"Created Element `{display_name}` with GUID {guid}\n\n___"
                        logger.success(msg)
                        output_md = (f"# Create CSV File\n\n## Display Name:\n\n {display_name}\n\n"
                                    f"## File Type:\n\n {file_type}\n\n## File Path:\n\n {file_path}\n\n"
                                    f"## File Encoding:\n\n {file_encoding}\n\n## File Extension:\n\n {file_extension}\n\n"
                                    f"## File System Name:\n\n {file_system_name}\n\n## Version Identifier:\n\n {version_identifier}\n\n"
                                    f"## Description:\n\n {description}\n\n"
                                    f"## Qualified Name\n\n {qualified_name}\n\n"
                                    f"## GUID:\n\n {guid}\n\n"
                                     )
                        return output_md
                    else:
                        msg = f"Failed to create element `{display_name}` with GUID {guid}\n\n___"
                        logger.error(msg)
                        return None
            else:
                logger.error(f"Currently only the Create action is supported for this command: {command}")

        except PyegeriaException as e:
            logger.error(f"Pyegeria error performing {command}: {e}")
            print_exception_table(e)
            return None
        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
    else:
        logger.error(f"Invalid directive `{directive}`")
        return None



def process_link_agreement_item_command(egeria_client: EgeriaTech, txt: str,
                                        directive: str = "display") -> Optional[str]:
    """
    Processes a link or unlink command to add or remove an agreement item.

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
    agreement_guid = attributes.get('Agreement Name', {}).get('guid', None)
    item = attributes.get('Item Name',{}).get('value', None)
    item_guid = attributes.get('Item Name', {}).get('guid', None)
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
                    body = set_delete_request_body(object_type, attributes)

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
                    msg = f"==>{object_type} Link with Agreement `{agreement}` and item `{item}` is not valid and can't be created"
                    logger.error(msg)
                    return

                else:
                    body = set_rel_request_body(object_type, attributes)
                    item_props = {
                        "class": "AgreementItemProperties",
                        "agreementItemId": attributes.get("Agreement Item Id",{}).get("value", None),
                        "agreementItemTypeName": attributes.get("Agreement Item Type",{}).get("value", None),
                        "agreementStart": attributes.get("Agreement Start",{}).get("value", None),
                        "agreementEnd": attributes.get("Agreement End",{}).get("value", None),
                        "restrictions": attributes.get("Restrictions",{}).get("value", None),
                        "obligations": attributes.get("Obligations",{}).get("value", None),
                        "entitlements": attributes.get("Entitlements",{}).get("value", None),
                        "usageMeasurements": attributes.get("Usage Measurements",{}).get("value", None),
                        "effectiveFrom": attributes.get("Effective From",{}).get("value", None),
                        "effectiveTo": attributes.get("Effective To",{}).get("value", None)

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

def process_add_to_collection_command(egeria_client: EgeriaTech, txt: str,
                                        directive: str = "display") -> Optional[str]:
    """
    Processes a link or unlink command to add or remove a member to/from a collection..

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
    element_guid = attributes.get('Element Id',{}).get('guid', None)
    collection_guid = attributes.get('Collection Id', {}).get('guid', None)
    membership_rationale = attributes.get('Membership Rationale',{}).get('value', None)
    expression = attributes.get('Expression', {}).get('value', None)
    confidence = attributes.get('Confidence', {}).get('value', None)
    membership_status = attributes.get('Membership Status', {}).get('value', None)
    user_defined_status = attributes.get('User Defined Status', {}).get('value', None)
    steward = attributes.get('Steward', {}).get('guid', None)
    steward_type_name = attributes.get('Steward Type Name', {}).get('value', None)
    steward_property_name = attributes.get('Steward Property Name', {}).get('value', None)
    source = attributes.get('Source', {}).get('value', None)
    notes = attributes.get('Notes', {}).get('value', None)
    glossary_term = attributes.get('Glossary Term', {}).get('value', None)
    journal_entry = attributes.get('Journal Entry', {}).get('value', None)


    valid = parsed_output['valid']
    # exists = agreement_guid is not None and  item_guid is not None
    exists = collection_guid is not None and element_guid is not None

    if directive == "display":

        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
        return valid

    elif directive == "process":
        prop_body = {
            "class" : "CollectionMembershipProperties",
            "membershipRationale": membership_rationale,
            "expression": expression,
            "membershipStatus": membership_status,
            "userDefinedStatus": user_defined_status,
            "confidence": confidence,
            "steward": steward,
            "stewardTypeName": steward_type_name,
            "stewardPropertyName": steward_property_name,
            "source": source,
            "notes": notes,
            }
        label = "Add Member"
        try:
            if object_action in["Detach", "Unlink", "Remove"]:
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
                    body = set_delete_request_body(object_type, attributes)

                    egeria_client.remove_from_collection(collection_guid, element_guid,body)

                    logger.success(f"===> Detached element `{element_guid}` from collection `{collection_guid}`\n")
                    out = parsed_output['display'].replace('Unlink', 'Link', 1)

                    return (out)

            elif object_action in ["Link", "Add", "Attach"]:
                if valid is False and exists:
                    msg = (f"-->  Link called `{label}` already exists and result document updated changing "
                           f"`Link` to `Detach` in processed output\n")
                    logger.error(msg)
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

                    body['properties'] = prop_body
                    body = body_slimmer(body)
                    egeria_client.add_to_collection(collection_guid,
                                                        element_guid, body)
                    msg = f"==>Linked `{element_guid}` to collection `{collection_guid}` \n"
                    logger.success(msg)
                    out = parsed_output['display'].replace('Link', 'Detach', 1)
                    return out


        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            return None
    else:
        return None

def process_product_dependency_command(egeria_client: EgeriaTech, txt: str,
                                        directive: str = "display") -> Optional[str]:
    """
    Processes a link or unlink command to associate or break up a dependency between digital products..

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
    digital_product1_guid = attributes.get('Digital Product 1', None)
    digital_product2_guid = attributes.get('Digital Product 2', None)
    label = attributes.get('Label',{}).get('value', None)
    description = attributes.get('Description', {}).get('value', None)
    effective_from = attributes.get('Effective From', {}).get('value', None)
    effective_to = attributes.get('Effective To', {}).get('value', None)


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
        prop_body = {
            "class" : "DigitalProductDependencyProperties",
            "label": label,
            "description": description,
            "effectiveFrom": effective_from,
            "effectiveTo": effective_to
            }

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
                    body = set_delete_request_body(object_type, attributes)

                    egeria_client.detach_digital_product_dependency(digital_product1_guid, digital_product2_guid,body)

                    logger.success(f"===> Detached dependency between products `{digital_product1_guid}` and `{digital_product2_guid}`\n")
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

                    body['properties'] = prop_body
                    egeria_client.link_digital_product_dependency(digital_product1_guid,
                                                        digital_product2_guid, body)
                    msg = f"==>Linked dependency from digital product `{digital_product1_guid}` to product `{digital_product2_guid}` \n"
                    logger.success(msg)
                    out = parsed_output['display'].replace('Link', 'Detach', 1)
                    return out


        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            return None
    else:
        return None

def process_attach_collection_command(egeria_client: EgeriaTech, txt: str,
                                        directive: str = "display") -> Optional[str]:
    """
    Processes a link or unlink command to attach a collection to a resources.

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
    collection_guid = attributes.get('Collection Id', {}).get('guid', None)
    resource_guid = attributes.get('Resource Id', {}).get('guid', None)
    resource_use = attributes.get('Resource Use', {}).get('value', None)
    resource_description = attributes.get('Resource Description', {}).get('value', None)
    resource_properties = attributes.get('Resource Properties', {}).get('value', None)
    effective_from = attributes.get('Effective From', {}).get('value', None)
    effective_to = attributes.get('Effective To', {}).get('value', None)


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
        prop_body = {
            "class" : "ResourceListProperties",
            "resourceUse": resource_use,
            "resourceDescription": resource_description,
            "resourceProperties": resource_properties,
            "effectiveFrom": effective_from,
            "effectiveTo": effective_to
            }

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
                    body = set_delete_request_body(object_type, attributes)

                    egeria_client.detach_collection(resource_guid, collection_guid,body)

                    logger.success(f"===> Detached linkage between resource `{resource_guid}` and collection`{collection_guid}`\n")
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

                    body['properties'] = prop_body
                    egeria_client.attach_collection(resource_guid,
                                                        collection_guid, body)
                    msg = f"==>Attached collection `{collection_guid}` to resource `{resource_guid}` \n"
                    logger.success(msg)
                    out = parsed_output['display'].replace('Link', 'Detach', 1)
                    return out


        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            return None
    else:
        return None

def process_attach_subscriber_command(egeria_client: EgeriaTech, txt: str,
                                        directive: str = "display") -> Optional[str]:
    """
    Processes a link or unlink command to attach a subscriber to a subscription.

    :param txt: A string representing the input cell to be processed for
        extracting blueprint-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))

    parsed_output = parse_view_command(egeria_client, object_type, object_action, txt, directive)
    if parsed_output is None:
        logger.error(f"Input error in command `{txt}`")
        return None

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']
    subscriber_guid = attributes.get('Subscriber Id', {}).get('guid', None)
    subscription_guid = attributes.get('Subscription', {}).get('guid', None)

    valid = parsed_output['valid']

    if directive == "display":

        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
        return valid

    elif directive == "process":
        prop_body = {
            "class": "DigitalSubscriberProperties",
            "subscriberId":  attributes.get('Subscriber Id', {}).get('value', None),
            "effectiveFrom": attributes.get('Effective From', {}).get('value', None),
            "effectiveTo": attributes.get('Effective To', {}).get('value', None),
        }

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
                    body = set_delete_request_body(object_type, attributes)

                    egeria_client.detach_subscriber(subscriber_guid, subscription_guid,body)

                    logger.success(f"===> Detached linkage between subscriber `{subscriber_guid}` and subscription`{subscription_guid}`\n")
                    out = parsed_output['display'].replace('Unlink', 'Link', 1)

                    return (out)

            elif object_action == "Link":
                if valid is False and exists:
                    msg = (f"-->  Link called `{label}` already exists and result document updated changing "
                           f"`Link` to `Detach` in processed output\n")
                    logger.error(msg)

                elif valid is False:
                    msg = f"==>{object_type} Subscription link `{subscriber_guid}` is not valid and can't be created"
                    logger.error(msg)
                    return

                else:
                    body = set_rel_request_body(object_type, attributes)

                    body['properties'] = prop_body
                    egeria_client.link_subscriber(subscriber_guid,
                                                        subscription_guid, body)
                    msg = f"==>Attached subscriber `{subscriber_guid}` to subscription `{subscriber_guid}` \n"
                    logger.success(msg)
                    out = parsed_output['display'].replace('Link', 'Detach', 1)
                    return out


        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            return None
    else:
        return None

