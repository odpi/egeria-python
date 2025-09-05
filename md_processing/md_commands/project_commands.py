"""
This file contains glossary-related object_action functions for processing Egeria Markdown
"""

import json
import os
import re
from typing import List, Optional

from inflect import engine
from loguru import logger
from pydantic import ValidationError
from rich import print
from rich.console import Console
from rich.markdown import Markdown

from md_processing.md_processing_utils.common_md_proc_utils import (parse_upsert_command, parse_view_command,
                                                                    sync_collection_memberships)
from md_processing.md_processing_utils.common_md_utils import update_element_dictionary, set_update_body, \
    set_element_status_request_body, set_element_prop_body, set_delete_request_body, set_rel_request_body, \
    set_peer_gov_def_request_body, \
    set_rel_request_body, set_create_body, set_object_classifications, set_product_body, set_rel_request_body_for_type

from md_processing.md_processing_utils.extraction_utils import (extract_command_plus, update_a_command)
from md_processing.md_processing_utils.md_processing_constants import (load_commands, ERROR)
from pyegeria import DEBUG_LEVEL, body_slimmer, to_pascal_case, PyegeriaException, print_basic_exception, \
    print_exception_table, print_validation_error
from pyegeria.egeria_tech_client import EgeriaTech



from md_processing.md_processing_utils.common_md_utils import (debug_level, print_msg, set_debug_level,
                                                               get_element_dictionary, update_element_dictionary,
                                                               )
from md_processing.md_processing_utils.extraction_utils import (extract_command_plus, extract_command,
                                                                process_simple_attribute, process_element_identifiers,
                                                                update_a_command, extract_attribute,
                                                                get_element_by_name, process_name_list)
from md_processing.md_processing_utils.md_processing_constants import (GLOSSARY_NAME_LABELS, TERM_NAME_LABELS,
                                                                       TERM_RELATIONSHPS, ALWAYS, ERROR, INFO,
                                                                       WARNING, pre_command, EXISTS_REQUIRED,
                                                                       OUTPUT_LABELS, SEARCH_LABELS, GUID_LABELS,
                                                                       ELEMENT_OUTPUT_FORMATS, command_seperator)
from pyegeria import body_slimmer
from pyegeria._globals import (NO_GLOSSARIES_FOUND, NO_ELEMENTS_FOUND, NO_CATEGORIES_FOUND)
from pyegeria.egeria_tech_client import EgeriaTech

# EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "170"))
# console = Console(width=EGERIA_WIDTH)



def process_project_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a project create or update object_action by extracting key attributes such as
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
            obj = "Project"
            project_types = ["Campaign", "Task", "Personal Project", "Study Project"]


            #   Set the property body for a glossary collection
            #
            prop_body = set_element_prop_body(obj, qualified_name, attributes)
            prop_body["identifier"] = attributes.get('Identifier', {}).get('value', None)
            prop_body["mission"] = attributes.get('Mission', {}).get('value', None)
            prop_body["purposes"] = attributes.get('Purposes', {}).get('value', None)
            prop_body["startDate"] = attributes.get('Start Date', {}).get('value', None)
            prop_body["endDate"] = attributes.get('End Date', {}).get('value', None)
            prop_body["priority"] = attributes.get('Priority', {}).get('value', None)
            prop_body["projectPhase"] = attributes.get('Project Phase', {}).get('value', None)
            prop_body["projectStatus"] = attributes.get('Project Status', {}).get('value', None)
            prop_body["projectHealth"] = attributes.get('Project Health', {}).get('value', None)

            if object_action == "Update":
                if not exists:
                    msg = (f" Element `{display_name}` does not exist! Updating result document with Create "
                           f"{object_action}\n")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif not valid:
                    msg = ("  The input data is invalid and cannot be processed. \nPlease review")
                    logger.error(msg)
                    print(Markdown(f"==> Validation of {command} failed!!\n"))
                    print(Markdown(msg))
                    return None
                else:
                    print(Markdown(
                        f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))


                body = set_update_body(obj, attributes)
                body['properties'] = prop_body

                egeria_client.update_project(guid, body)
                # if status:
                #     egeria_client.update_project_status(guid, status)

                logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}\n\n___")
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                return egeria_client.get_project_by_guid(guid, element_type='Project',
                                                            output_format='MD', output_format_set = "Projects")


            elif object_action == "Create":
                if valid is False and exists:
                    msg = (f"Project `{display_name}` already exists and result document updated changing "
                           f"`Create` to `Update` in processed output\n\n___")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif not valid:
                    msg = ("The input data is invalid and cannot be processed. \nPlease review")
                    logger.error(msg)
                    print(Markdown(f"==> Validation of {command} failed!!\n"))
                    print(Markdown(msg))
                    return None

                else:
                    body = set_create_body(object_type,attributes)

                    # if this is a root or folder (maybe more in the future), then make sure that the classification is set.
                    body["initialClassifications"] = set_object_classifications(object_type, attributes, project_types)

                    body["properties"] = prop_body
                    slim_body = body_slimmer(body)
                    guid = egeria_client.create_project(body = slim_body)
                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        msg = f"Created Element `{display_name}` with GUID {guid}\n\n___"
                        logger.success(msg)
                        return egeria_client.get_project_by_guid(guid, output_format='MD', output_format_set = "Projects")
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



def process_link_project_hierarchy_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:

#     """ Set one project to manage another."""
#
    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))

    parsed_output = parse_view_command(egeria_client, object_type, object_action,
                                       txt, directive)

    if not parsed_output:
        logger.error(f"No output for `{object_action}`")
        print(Markdown("## Parsing failed"))
        return None

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']

    parent_project_guid = attributes.get('Parent Project', {}).get('guid', None)
    child_project_guid = attributes.get('Child Project', {}).get('guid', None)
    label = attributes.get('Link Label', {}).get('value', "")

    valid = parsed_output['valid']
    exists = parent_project_guid is not None and child_project_guid  is not None

    if directive == "display":

        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
            logger.error(msg)
            print(Markdown(f"==> Validation of {command} failed!!\n"))
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

                    egeria_client.clear_project_hierarchy(child_project_guid, parent_project_guid,body)

                    logger.success(f"===> Detached segment with {label} from `{child_project_guid}`to {parent_project_guid}\n")
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
                    body = set_rel_request_body_for_type("ProjectHierarchy", attributes)

                    egeria_client.set_project_hierarchy(project_guid =child_project_guid,
                                                        parent_project_guid = parent_project_guid)
                                                        # body=body_slimmer(body))
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



def process_link_project_dependency_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:

#     """ Set one project dependence on another."""
#

    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))

    parsed_output = parse_view_command(egeria_client, object_type, object_action,
                                       txt, directive)

    if not parsed_output:
        logger.error(f"No output for `{object_action}`")
        print(Markdown("## Parsing failed"))
        return None

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']

    parent_project_guid = attributes.get('Parent Project', {}).get('guid', None)
    child_project_guid = attributes.get('Child Project', {}).get('guid', None)
    label = attributes.get('Link Label', {}).get('value', "")

    valid = parsed_output['valid']
    exists = parent_project_guid is not None and child_project_guid  is not None

    if directive == "display":

        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
            logger.error(msg)
            print(Markdown(f"==> Validation of {command} failed!!\n"))
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

                    egeria_client.clear_project_dependency(child_project_guid, parent_project_guid,body)

                    logger.success(f"===> Detached segment with {label} from `{child_project_guid}`to {parent_project_guid}\n")
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
                    body = set_rel_request_body_for_type("ProjectDependency", attributes)

                    egeria_client.set_project_dependency(project_guid =child_project_guid,
                                                        upstream_project_guid = parent_project_guid,
                                                        body=body_slimmer(body))
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
