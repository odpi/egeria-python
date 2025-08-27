"""
This file contains term-related object_action functions for processing Egeria Markdown
"""
import json
import os
from typing import Optional

from inflect import engine
from jsonschema import ValidationError
from loguru import logger
from md_processing.md_processing_utils.common_md_proc_utils import (parse_upsert_command, parse_view_command,
                                                                    process_output_command)
from md_processing.md_processing_utils.common_md_utils import (set_gov_prop_body,
                                                               set_update_body, set_create_body,
                                                               set_peer_gov_def_request_body,
                                                               ALL_GOVERNANCE_DEFINITIONS, GOVERNANCE_POLICIES,
                                                               GOVERNANCE_CONTROLS, GOVERNANCE_DRIVERS,
                                                               set_find_body,
                                                               set_delete_request_body)
from md_processing.md_processing_utils.extraction_utils import (extract_command_plus, update_a_command)
from md_processing.md_processing_utils.md_processing_constants import (load_commands)
from pyegeria import DEBUG_LEVEL, body_slimmer, PyegeriaException, print_basic_exception, print_validation_error
from pyegeria.egeria_tech_client import EgeriaTech
from rich import print
from rich.console import Console
from rich.markdown import Markdown

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

console = Console(width=int(250))


#
# Helper functions for the governance officer commands
#

@logger.catch
def sync_gov_rel_elements(egeria_client: EgeriaTech, object_action: str, object_type: str, guid: str,
                          qualified_name: str, attributes: dict):
    # TODO: when the next release is available, I should be able to more easily get the asis elements - so will
    # TODO: hold off on implementing replace all
    try:
        merge_update = attributes.get("Merge Update", {}).get("value", True)
        to_be_supports_policies = attributes.get("Supports Policies", {}).get("guid_list", None)
        to_be_governance_drivers = attributes.get("Governance Drivers", {}).get("guid_list", None)

        if merge_update or object_action == "Create":
            if to_be_supports_policies:
                for policy in to_be_supports_policies:
                    egeria_client.attach_supporting_definitions(policy, "GovernanceImplementation", guid)
                    print(f"Added `{policy}` to `{guid}`")
            elif to_be_governance_drivers:
                for policy in to_be_governance_drivers:
                    egeria_client.attach_supporting_definitions(policy, "GovernanceResponse", guid)
                    print(f"Added `{policy}` to `{guid}`")
    except Exception as ex:
        print(ex)


@logger.catch
def process_gov_definition_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[
    str]:
    """
    Processes a data specification create or update object_action by extracting key attributes.

    :param txt: Command details in text format.
    :param directive: An optional string indicating the directive - display, validate, or process.
    :return: A string summarizing the outcome, or None if no processing is needed.
    """
    try:
        # Extract basic command information
        command, object_type, object_action = extract_command_plus(txt)
        if not (command and object_type and object_action):
            logger.error("Failed to parse `command`, `object_type`, or `object_action` from input text.")
            return None
        if object_type not in ALL_GOVERNANCE_DEFINITIONS:
            logger.error(f"Invalid object type: {object_type}")
            return None
        # Log command details
        print(Markdown(f"# {command}\n"))

        # Parse command attributes
        parsed_output = parse_upsert_command(egeria_client, object_type, object_action, txt, directive)
        if not parsed_output or 'valid' not in parsed_output:
            logger.error(f"Unable to parse command properly: {txt}")
            return None

        valid = parsed_output['valid']
        exists = parsed_output['exists']
        qualified_name = parsed_output.get('qualified_name')
        display_name = parsed_output.get('attributes', {}).get('Display Name', {}).get('value')
        guid = parsed_output.get('guid')

        print(Markdown(parsed_output.get('display', '')))
        logger.debug(json.dumps(parsed_output, indent=4))

        if directive == "display":
            logger.info("Directive set to display. No processing required.")
            return None

        elif directive == "validate":
            if valid:
                print(Markdown(f"==> Validation of {command} completed successfully!\n"))
            else:
                logger.error(f"Validation failed for `{command}`.")
            return valid

        elif directive == "process":
            if object_action == "Update":
                if not guid:
                    msg = (f"The `{object_type}` '{display_name}' does not yet exist.\n The result document has been "
                           f"updated to change `Update` to `Create` in processed output\n{'-' * 80}\n ")
                    logger.error(msg)
                    # print(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)

                if not valid:
                    logger.error("Invalid data for update action.")
                    return None

                # Proceed with the update
                update_body = set_update_body(object_type, parsed_output['attributes'])
                update_body['properties'] = set_gov_prop_body(object_type, qualified_name, parsed_output['attributes'])
                egeria_client.update_governance_definition(guid, body_slimmer(update_body))
                if status := parsed_output['attributes'].get('Status', {}).get('value', None):
                    egeria_client.update_governance_definition_status(guid, status)
                logger.success(f"Updated {object_type} `{display_name}` with GUID {guid}")
                return egeria_client.get_governance_definition_by_guid(guid, output_format='MD')

            elif object_action == "Create":
                if valid is False and exists:
                    msg = (f"Failed to create `{object_type}` named `{display_name}` because it already exists.\n "
                           f"Result document has been updated to change `Create` to `Update` in processed o"
                           f"utput\n{'-' * 80}\n")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif valid is False:
                    msg = f" invalid data? - Correct and try again\n\n___"
                    logger.error(msg)
                    return None
                else:
                    create_body = set_create_body(object_type, parsed_output['attributes'])
                    create_body['properties'] = set_gov_prop_body(object_type, qualified_name,
                                                                  parsed_output['attributes'])
                    guid = egeria_client.create_governance_definition(body_slimmer(create_body))
                    if guid:
                        logger.success(f"Created {object_type} `{display_name}` with GUID {guid}")
                        return egeria_client.get_governance_definition_by_guid(guid, output_format='MD')
                    else:
                        logger.error(f"Failed to create {object_type} `{display_name}`.")
                        return None

        else:
            logger.error(f"Unsupported directive: {directive}")
            return None

    except PyegeriaException as e:
        logger.error(f"PyegeriaException occurred: {e}")
        print_basic_exception(e)
        return None

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
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
    exists = definition1 is not None and definition2 is not None

    if directive == "display":

        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
        return valid

    elif directive == "process":
        # Initialize the inflect engine
        inflector = engine()

        # Split the object_type into words
        object_type_parts = object_type.split()

        # Determine which word to singularize (third word if present, otherwise fallback to last word)
        if len(object_type_parts) >= 3:
            word_to_singularize = object_type_parts[2]
        else:
            word_to_singularize = object_type_parts[-1]  # Fallback to last word

        # Singularize the selected word
        singular_word = inflector.singular_noun(word_to_singularize) or word_to_singularize

        # Construct gov_peer_relationship_type
        gov_peer_relationship_type = f"Governance{singular_word}Link"

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

            egeria_client.detach_peer_definitions(definition1, gov_peer_relationship_type,
                                                  definition2, body)

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

    except ValidationError as e:
        print_validation_error(e)
        logger.error(f"Validation Error performing {command}: {e}")
        return None
    except PyegeriaException as e:
        print_basic_exception(e)
        logger.error(f"PyegeriaException occurred: {e}")
        return None

    except Exception as e:
        logger.error(f"Error performing {command}: {e}")
        return None
    else:
        return None


@logger.catch
def process_supporting_gov_def_link_detach_command(egeria_client: EgeriaTech, txt: str,
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
    exists = definition1 is not None and definition2 is not None

    if directive == "display":

        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
        return valid

    elif directive == "process":

        # Construct gov_peer_relationship_type
        relationship_type_name = object_type.replace(' ', '')
        print(f"relationship_type_name: {relationship_type_name}")
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

            egeria_client.detach_supporting_definitions(definition1, relationship_type_name,
                                                        definition2, body)

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
                body_prop = {
                    "class": "SupportingDefinitionProperties",
                    "rationale": attributes.get('Rationale', {}).get('value', None),
                    "effectiveFrom": attributes.get('Effective From', {}).get('value', None),
                    "effectiveTo": attributes.get('Effective To', {}).get('value', None),
                    }

                body = set_peer_gov_def_request_body(object_type, attributes)
                body['properties'] = body_prop
                egeria_client.attach_supporting_definitions(definition1, relationship_type_name,
                                                            definition2, body)
                msg = f"==>Created {object_type} link named `{label}`\n"
                logger.success(msg)
                out = parsed_output['display'].replace('Link', 'Detach', 1)
                return out

    except ValidationError as e:
        print_validation_error(e)
        logger.error(f"Validation Error performing {command}: {e}")
        return None
    except PyegeriaException as e:
        print_basic_exception(e)
        logger.error(f"PyegeriaException occurred: {e}")
        return None

    except Exception as e:
        logger.error(f"Error performing {command}: {e}")
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

    attr = parsed_output.get('attributes', {})

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

            struct = egeria_client.get_gov_def_in_context(guid, body=body, output_format=output_format)
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
