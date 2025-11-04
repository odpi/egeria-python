"""
This file contains feedback-related object_action functions for processing Egeria Markdown
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


from pyegeria import DEBUG_LEVEL, body_slimmer, to_pascal_case, PyegeriaException, print_basic_exception, \
    print_exception_table, print_validation_error, COMMENT_TYPES
from pyegeria.egeria_tech_client import EgeriaTech



from md_processing.md_processing_utils.common_md_utils import (debug_level, print_msg, set_debug_level,
                                                               get_element_dictionary, update_element_dictionary,
                                                               )
from md_processing.md_processing_utils.extraction_utils import (extract_command_plus, extract_command,
                                                                process_simple_attribute, process_element_identifiers,
                                                                update_a_command, extract_attribute,
                                                                get_element_by_name, process_name_list)


from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.utils import make_format_set_name_from_type, body_slimmer



def process_add_comment_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a comment create or update object_action by extracting key attributes such as
    from the given text. If the Parent Comment is provided, then this comment will be a `reply` and the `Associated Element`
    will be ignored. One of `Associated Element` and `Parent Comment` must be provided.

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

    attributes = parsed_output['attributes']

    valid = parsed_output['valid']
    exists = parsed_output['exists']

    qualified_name = parsed_output.get('qualified_name', None)
    guid = parsed_output.get('guid', None)

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))



    display_name = attributes['Display Name'].get('value', None)
    associated_element = attributes.get('Associated Element', {}).get('value', None)
    associated_element_guid = attributes.get('Associated Element', {}).get('guid', None)
    description = attributes.get('Comment Text', {}).get('value', None)
    comment_type = attributes.get('Comment Type', {}).get('value', None).strip()


    # if associated_element_guid is None and parent_comment_guid is None:
    #     valid = False
    #     msg = f"Validation failed for {command} - One of `Associated Element` or `Parent Comment` must be specified\n"
    #     logger.error(msg)
    #     print(msg)
    # else:
    #     if description:
    #         valid = True
    #         exists = True
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

            obj = "Comment"
            if comment_type not in COMMENT_TYPES:
                raise ValueError(f"Invalid comment type: {comment_type}")
            # target_guid = parent_comment_guid if parent_comment_guid else associated_element_guid
            if qualified_name is None:
                qualified_name = egeria_client.make_feedback_qn("Comment",associated_element_guid,display_name)
            #   Set the property body for a glossary collection
            #
            prop_body = {
                    "class": "CommentProperties",
                    "displayName": display_name,
                    "qualifiedName": qualified_name,
                    "description": description,
                    "commentType": comment_type
                }

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

                egeria_client.update_comment(guid, body)

                logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}\n\n___")
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                return egeria_client.get_comment_by_guid(guid, element_type='Comment',
                                                            output_format='MD', report_spec = "Comments-DrE")


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
                    body['class'] = "NewAttachmentRequestBody"
                    body["properties"] = prop_body
                    slim_body = body_slimmer(body)
                    # if parent_comment_guid:
                    #     guid = egeria_client.add_comment_reply(element_guid = parent_comment_guid, body = slim_body)
                    # else:
                    guid = egeria_client.add_comment_to_element(element_guid = associated_element_guid, body =slim_body)

                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        msg = f"## ==> Created Element `{display_name}` with GUID {guid}\n\n___"
                        logger.success(msg)
                        print(Markdown(msg))
                        return egeria_client.get_comment_by_guid(guid, output_format='MD', report_spec = "Comments-DrE")
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

def process_journal_entry_command(egeria_client: EgeriaTech, txt: str,
                                         directive: str = "display") -> Optional[str]:
    """
    Creates or updates a journal entry. If the journal (NoteLog) doesn't exist, then it will be created. Each journal
    entry is a note in a NoteLog.

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

    journal_name = attributes['Journal Name'].get('value', None)
    journal_qn = attributes['Journal Name'].get('qualified_name', None)
    journal_exists = attributes['Journal Name'].get('Exists', False)
    note_entry = attributes['Note Entry'].get('value', None)
    journal_description = attributes['Journal Description'].get('value', None)

    associated_element = attributes.get('Associated Element', {}).get('value', None)
    associated_element_qn = attributes.get('Associated Element', {}).get('qualified_name', None)

    if journal_exists is False:
        qualified_name = None
        journal_qn = None


    if journal_name and note_entry:
        valid = True
    else:
        valid = False
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

            if object_action == "Create":
                if valid is False:
                    msg = "Journal name or Journal entry are missing."
                    logger.error(msg)
                    print(msg)
                    print(Markdown(f"==> Validation of {command} failed!!\n"))
                    return None

                else:

                    note_guid = egeria_client.add_journal_entry(note_log_qn = journal_qn,
                                                                   element_qn = associated_element_qn,
                                                                   note_log_display_name = journal_name,
                                                                   note_entry = note_entry )
                    if note_guid:
                        msg = f"Created entry in `{journal_name}` with GUID {note_guid}\n\n___"
                        logger.success(msg)
                        print(Markdown(msg))
                        return egeria_client.get_note_by_guid(note_guid,
                                                                   output_format='MD', report_spec = "Journal-Entry-DrE")
                    else:
                        msg = f"Failed to create entry for  `{journal_name}`\n\n___"
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


def process_upsert_note_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a NoteLog Note request to create or update object_action from the given text.

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
    note_log = attributes.get('Note Log',{}).get('value', {})
    note_log_guid = attributes.get('Note Log',{}).get('guid', None)
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
            obj = "Notification"

            #   Set the property body for a glossary collection
            #
            prop_body = set_element_prop_body(obj, qualified_name, attributes)

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
                slim_body = body_slimmer(body)
                egeria_client.update_note(guid, slim_body)


                logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}\n\n___")
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                return egeria_client.get_note_by_guid(guid, output_format='MD', report_spec = "Note-DrE")


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

                    body["properties"] = prop_body
                    slim_body = body_slimmer(body)
                    guid = egeria_client.create_project(body = slim_body)
                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        msg = f"Created Element `{display_name}` with GUID {guid}\n\n___"
                        logger.success(msg)
                        return egeria_client.get_note_by_guid(guid, output_format='MD', report_spec = "Note-DrE")
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

def process_attach_note_log_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:

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

def process_upsert_informal_tag_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a informal tag create or update object_action by extracting key attributes such as
    from the given text.

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
    description = attributes['Description'].get('value', None)
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
            obj = "InformalTag"

            #   Set the property body for a glossary collection
            #
            prop_body = set_element_prop_body(obj, qualified_name, attributes)

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

                egeria_client.update_tag_description(guid, description)

                logger.success(f"Updated  {object_type} `{display_name}` with GUID {guid}\n\n___")
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                return egeria_client.get_tag_by_guid(guid, element_type='InformalTag',
                                                            output_format='MD', report_spec = "Informal-Tag-DrE")


            elif object_action == "Create":
                if valid is False and exists:
                    msg = (f"Informal Tag `{display_name}` already exists and result document updated changing "
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

                    guid = egeria_client.create_informal_tag(display_name, description, qualified_name)
                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        msg = f"Created Element `{display_name}` with GUID {guid}\n\n___"
                        print(Markdown(msg))
                        logger.success(msg)
                        return egeria_client.get_tag_by_guid(guid, output_format='MD', report_spec = "Informal-Tags-DrE")
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


def process_tag_element_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:

#     """ Tag an Element with the specified Informal Tag."""
#
    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))

    parsed_output = parse_view_command(egeria_client, object_type, object_action,
                                       txt, directive)
    tag_id = parsed_output['attributes']['Tag ID'].get('value', None)
    tag_guid = parsed_output['attributes']['Tag ID'].get('guid', None)
    element_id = parsed_output['attributes']['Element ID'].get('value', None)
    element_guid = parsed_output['attributes']['Element ID'].get('guid', None)

    if not parsed_output:
        logger.error(f"No output for `{object_action}`")
        print(Markdown("## Parsing failed"))
        return None

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    valid = parsed_output['valid']
    exists = tag_guid is not None and element_guid  is not None

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
                    msg = (f" The tag or element do not exist! Updating result document with Link "
                           f"object_action\n")
                    logger.error(msg)
                    out = parsed_output['display'].replace('Link', 'Detach', 1)
                    return out
                elif not valid:
                    return None
                else:
                    print(Markdown(
                        f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))

                    egeria_client.remove_tag_from_element(element_guid, tag_guid)

                    logger.success(f"===> Detached tab {tag_id} from `{element_id}`\n")
                    out = parsed_output['display'].replace('Unlink', 'Link', 1)

                    return (out)


            elif object_action == "Link":
                if valid is False and exists:
                    msg = ("-->  Link already exists and result document updated changing "
                           "`Link` to `Detach` in processed output\n")
                    logger.error(msg)

                elif valid is False:
                    msg = f"==>{object_type} Add link request is not valid and can't be created"
                    logger.error(msg)
                    return

                else:
                    egeria_client.add_tag_to_element(element_guid =element_guid,
                                                        tag_guid = tag_guid)

                    msg = f"==>Created {object_type} link \n"
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


