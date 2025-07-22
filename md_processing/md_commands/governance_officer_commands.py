"""
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

from md_processing.md_processing_utils.common_md_proc_utils import (parse_upsert_command, parse_view_command)
from md_processing.md_processing_utils.common_md_utils import (update_element_dictionary, set_gov_prop_body, \
    set_update_body, set_create_body, set_peer_gov_def_request_body, set_rel_request_body,
    set_metadata_source_request_body, set_filter_request_body, setup_log)
from md_processing.md_processing_utils.extraction_utils import (extract_command_plus, update_a_command)
from md_processing.md_processing_utils.md_processing_constants import (load_commands, ERROR)
from pyegeria import DEBUG_LEVEL, body_slimmer
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

GENERAL_GOVERNANCE_DEFINITIONS = ["Business Imperative", "Regulation Article", "Threat", "Governance Principle",
                                  "Governance Obligation", "Governance Approach", "Governance Processing Purpose"]

GOVERNANCE_CONTROLS = ["Governance Rule", "Service Level Objective", "Governance Process",
                       "Governance Responsibility", "Governance Procedure", "Security Access Control"]

load_commands('commands.json')
debug_level = DEBUG_LEVEL

console = Console(width=int(200))
setup_log()

#
# Helper functions for the governance officer commands
#

@logger.catch
def sync_gov_rel_elements(egeria_client: EgeriaTech, object_action:str, object_type:str, guid:str, qualified_name:str, attributes: dict):
# TODO: when the next release is available, I should be able to more easily get the asis elements - so will
# TODO: hold off on implementing replace all
    try:
        merge_update = attributes.get("Merge Update", {}).get("value",True)
        to_be_supports_policies = attributes.get("Supports Policies", {}).get("guid_list",None)
        to_be_governance_drivers = attributes.get("Governance Drivers", {}).get("guid_list",None)

        if merge_update or object_action == "Create":
            if to_be_supports_policies:
                for policy in to_be_supports_policies:
                    egeria_client.attach_supporting_definitions(policy, "GovernanceImplementation",guid)
                    print(f"Added `{policy}` to `{guid}`")
            elif to_be_governance_drivers:
                for policy in to_be_governance_drivers:
                    egeria_client.attach_supporting_definitions(policy, "GovernanceResponse",guid)
                    print(f"Added `{policy}` to `{guid}`")
    except Exception as ex:
        print(ex)

@logger.catch
def process_gov_definition_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a data specification create or update object_action by extracting key attributes such as
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
    display_name = parsed_output.get('display_name', None)
    guid = parsed_output.get('guid', None)

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']

    display_name = attributes['Display Name'].get('value', None)

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
                update_body = set_update_body(object_type, attributes)
                update_body['properties'] = set_gov_prop_body(object_type, qualified_name, attributes)

                egeria_client.update_governance_definition(guid, update_body, replace_all_props)
                logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}\n\n___")
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                sync_gov_rel_elements(egeria_client,object_type, object_type,guid, qualified_name, attributes)
                return egeria_client.get_governance_definition_by_guid(guid, output_format='MD')


            elif object_action == "Create":
                if valid is False and exists:
                    msg = (f"  Data Specification `{display_name}` already exists and result document updated changing "
                           f"`Create` to `Update` in processed output\n\n___")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                # elif valid is False and in_data_spec_valid is False:
                #     msg = (f" Invalid data specification(s) `{in_data_spec_list}` "
                #            f" invalid data? - Correct and try again\n\n___")
                #     logger.error(msg)
                #     return None
                else:
                    create_body = set_create_body(object_type, attributes)
                    create_body['properties'] = set_gov_prop_body(object_type, qualified_name,attributes)
                    guid = egeria_client.create_governance_definition(create_body)
                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        sync_gov_rel_elements(egeria_client, object_action,
                                              object_type, guid, qualified_name,
                                              attributes)

                        msg = f"Created Element `{display_name}` with GUID {guid}\n\n___"
                        logger.success(msg)
                        return egeria_client.get_governance_definition_by_guid(guid, output_format='MD')
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
def process_gov_def_link_detach_command(egeria_client: EgeriaTech, txt: str,
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

    definition1 = attributes.get('Definition 1', {}).get('guid', None)
    definition2 = attributes.get('Definition 2', {}).get('guid', None)
    label = attributes.get('Link Label', {}).get('value', None)
    description = attributes.get('Description', {}).get('value', None)

    valid = parsed_output['valid']
    exists = definition1 is not None and  definition2 is not None


    if directive == "display":

        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
        return valid

    elif directive == "process":
        gov_peer_relationship_type = object_type[:-1].replace(" ","") + "Link"

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

                egeria_client._async_detach_peer_definitions(definition1, gov_peer_relationship_type,
                                                             definition2,body)

                logger.success(f"===> Detached segment with {label} from `{definition1}`to {definition2}\n")
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
                    body = set_peer_gov_def_request_body(object_type, attributes)

                    egeria_client.link_peer_definitions(definition1, gov_peer_relationship_type,
                                                        definition2, body)
                    msg = f"==>Created {object_type} link named `{label}`\n"
                    logger.success(msg)
                    out = parsed_output['display'].replace('Link', 'Detach', 1)
                    return out


        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            return None
    else:
        return None


@logger.catch
def process_gov_definition_list_command(egeria_client: EgeriaTech, txt: str,
                                         directive: str = "display") -> Optional[str]:
    """
    Processes a Governance Definition  list object_action by extracting key attributes such as
     search string from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting term-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))

    parsed_output = parse_view_command(egeria_client, object_type, object_action, txt, directive)



    valid = parsed_output['valid']
    print(Markdown(f"Performing {command}"))
    print(Markdown(parsed_output['display']))

    attr = parsed_output.get('attributes',{})

    search_string = attr.get('Search String', {}).get('value', '*')
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

            list_md = f"\n# `{object_type}` with filter: `{search_string}`\n\n"
            body = set_update_body(object_type, attr)

            struct = egeria_client.find_governance_definitions(search_string,
                                                                       body = body,
                                                                      output_format=output_format)
            if output_format.upper() == "DICT":
                list_md += f"```\n{json.dumps(struct, indent=4)}\n```\n"
            else:
                list_md += struct
            logger.info(f"Wrote `{object_type}` for search string: `{search_string}`")

            return list_md

        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            console.print_exception(show_locals=True)
            return None
    else:
        return None

@logger.catch
def process_gov_def_context_command(egeria_client: EgeriaTech, txt: str,
                                         directive: str = "display") -> Optional[str]:
    """
    Retrieves the context graph for a governance definition.

    :param txt: A string representing the input cell to be processed for
        extracting term-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))

    parsed_output = parse_view_command(egeria_client, object_type, object_action, txt, directive)

    valid = parsed_output['valid']
    exists = parsed_output['exists']
    qualified_name = parsed_output.get('qualified_name', None)
    display_name = parsed_output.get('display_name', None)
    guid = parsed_output.get('guid', None)

    print(Markdown(parsed_output['display']))

    attr = parsed_output.get('attributes',{})

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

            list_md = f"\n# `{object_type}` with Qualified Name: `{qualified_name}`\n\n"
            body = set_update_body(object_type, attr)

            struct = egeria_client.get_gov_def_in_context(guid, body = body, output_format=output_format)
            if output_format.upper() == "DICT":
                list_md += f"```\n{json.dumps(struct, indent=4)}\n```\n"
            else:
                list_md += struct
            logger.info(f"Wrote `{object_type}` graph for : `{qualified_name}`")

            return list_md

        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            console.print_exception(show_locals=True)
            return None
    else:
        return None


