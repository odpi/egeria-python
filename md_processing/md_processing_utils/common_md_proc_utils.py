"""
This file contains general utility functions for processing Egeria Markdown
"""
import json
import os
import sys
from typing import List

from loguru import logger
from rich import print
from rich.console import Console

from md_processing.md_processing_utils.common_md_utils import (get_current_datetime_string, get_element_dictionary,
                                                               update_element_dictionary,
                                                               split_tb_string, str_to_bool, )
from md_processing.md_processing_utils.extraction_utils import (process_simple_attribute, extract_attribute,
                                                                get_element_by_name)
from md_processing.md_processing_utils.md_processing_constants import (get_command_spec)
from md_processing.md_processing_utils.message_constants import (ERROR, INFO, WARNING, ALWAYS, EXISTS_REQUIRED)
from pyegeria import EgeriaTech
from pyegeria._globals import DEBUG_LEVEL

log_format = "P {time} | {level} | {function} | {line} | {message} | {extra}"
logger.remove()
logger.add(sys.stderr, level="INFO", format=log_format, colorize=True)
logger.add("debug_log.log", rotation="1 day", retention="1 week", compression="zip", level="TRACE", format=log_format,
           colorize=True)
# Constants
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", "200"))
EGERIA_USAGE_LEVEL = os.environ.get("EGERIA_USAGE_LEVEL", "Basic")
console = Console(width=EGERIA_WIDTH)

debug_level = DEBUG_LEVEL
global COMMAND_DEFINITIONS


@logger.catch
def process_provenance_command(file_path: str, txt: [str]) -> str:
    """
    Processes a provenance object_action by extracting the file path and current datetime.

    Args:
        file_path: The path to the file being processed.
        txt: The text containing the provenance object_action.

    Returns:
        A string containing the provenance information.
    """
    now = get_current_datetime_string()
    file_name = os.path.basename(file_path)
    provenance = f"\n\n\n# Provenance:\n \n* Derived from processing file {file_name} on {now}\n"
    return provenance


@logger.catch
def parse_upsert_command(egeria_client: EgeriaTech, object_type: str, object_action: str, txt: str,
                       directive: str = "display") -> dict:
    parsed_attributes, parsed_output = {}, {}

    parsed_output['valid'] = True
    parsed_output['exists'] = False
    parsed_output['display'] = ""
    display_name = ""
    labels = {}

    command_spec = get_command_spec(f"Create {object_type}")
    attributes = command_spec.get('Attributes', [])
    command_display_name = command_spec.get('display_name', None)
    command_qn_prefix = command_spec.get('qn_prefix', None)

    parsed_output['display_name'] = command_display_name
    parsed_output['qn_prefix'] = command_qn_prefix

    parsed_output['is_own_anchor'] = command_spec.get('isOwnAnchor', True)

    parsed_output['reason'] = ""

    msg = f"\tProcessing {object_action} on a {object_type}  \n"
    logger.info(msg)

    # get the version early because we may need it to construct qualified names.
    version = process_simple_attribute(txt, {'Version', "Version Identifier", "Published Version"}, INFO)
    parsed_output['version'] = version

    for attr in attributes:
        for key in attr:
            # Run some checks to see if the attribute is appropriate to the operation and usage level
            for_update = attr[key].get('inUpdate', True)
            level = attr[key].get('level', 'Basic')
            msg = (f"___\nProcessing `{key}` in `{object_action}` on a `{object_type}` "
                   f"\n\twith usage level: `{EGERIA_USAGE_LEVEL}` and  attribute level `{level}` and for_update `"
                   f"{for_update}`\n")
            logger.trace(msg)
            if for_update is False and object_action == "Update":
                logger.trace(f"Attribute `{key}`is not allowed for `Update`", highlight=True)
                continue
            if EGERIA_USAGE_LEVEL == "Basic" and level != "Basic":
                logger.trace(f"Attribute `{key}` is not supported for `{EGERIA_USAGE_LEVEL}` usage level. Skipping.",
                            highlight=True)
                continue
            if EGERIA_USAGE_LEVEL == "Advanced" and level in ["Expert", "Invisible"]:
                logger.trace(f"Attribute `{key}` is not supported for `{EGERIA_USAGE_LEVEL}` usage level. Skipping.",
                            highlight=True)
                continue
            if EGERIA_USAGE_LEVEL == "Expert" and level == "Invisible":
                logger.trace(f"Attribute `{key}` is not supported for `{EGERIA_USAGE_LEVEL}` usage level. Skipping.",
                            highlight=True)
                continue

            if attr[key].get('input_required', False) is True:
                if_missing = ERROR
            else:
                if_missing = INFO

            # lab = [item.strip() for item in re.split(r'[;,\n]+',attr[key]['attr_labels'])]
            lab = split_tb_string(attr[key]['attr_labels'])
            labels: set = set()
            labels.add(key.strip())
            if key == 'Display Name':
                labels.add(object_type.strip())
            if lab is not None and lab != [""]:
                labels.update(lab)

            default_value = attr[key].get('default_value', None)

            style = attr[key]['style']
            if style in ['Simple', 'Dictionary', 'Comment']:
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing, default_value)
            elif style == 'Valid Value':
                parsed_attributes[key] = proc_valid_value(txt, object_action, labels,
                                                          attr[key].get('valid_values', None), if_missing,
                                                          default_value)
            elif style == 'QN':
                parsed_attributes[key] = proc_el_id(egeria_client, command_display_name, command_qn_prefix, labels, txt,
                                                    object_action, version, if_missing)
                if key == 'Qualified Name' and parsed_attributes[key]['value'] and parsed_attributes[key][
                    'exists'] is False:
                    parsed_output['exists'] = False
            elif style == 'ID':
                parsed_attributes[key] = proc_el_id(egeria_client, command_display_name, command_qn_prefix, labels, txt,
                                                    object_action, version, if_missing)

                parsed_output['guid'] = parsed_attributes[key].get('guid', None)
                parsed_output['qualified_name'] = parsed_attributes[key].get('qualified_name', None)
                parsed_output['exists'] = parsed_attributes[key]['exists']
                if parsed_attributes[key]['valid'] is False:
                    parsed_output['valid'] = False
                    parsed_output['reason'] += parsed_attributes[key]['reason']

            elif style == 'Reference Name':
                parsed_attributes[key] = proc_ids(egeria_client, key, labels, txt, object_action, if_missing)
                if ((if_missing == ERROR) and parsed_attributes[key].get("value", None) and parsed_attributes[key][
                    'exists'] is False):
                    msg = f"Reference Name `{parsed_attributes[key]['value']}` is specified but does not exist"
                    logger.error(msg)
                    parsed_output['valid'] = False
                    parsed_output['reason'] += msg
                elif parsed_attributes[key]['valid'] is False:
                    parsed_output['valid'] = False
                    parsed_output['reason'] += parsed_attributes[key]['reason']

            elif style == 'GUID':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing)
            elif style == 'Ordered Int':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing)
            elif style == 'Simple Int':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing, default_value, "int")
            elif style == 'Simple List':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing, default_value)
                name_list = parsed_attributes[key]['value']
                # attribute = re.split(r'[;,\n]+', name_list) if name_list is not None else None
                attribute = split_tb_string(name_list)
                parsed_attributes[key]['value'] = attribute
                parsed_attributes[key]['name_list'] = name_list
            elif style == 'Parent':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing, default_value)
            elif style == 'Bool':
                parsed_attributes[key] = proc_bool_attribute(txt, object_action, labels, if_missing, default_value)
            elif style == "Dictionary List":
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing, default_value)
                parsed_attributes[key]['list'] = json.loads(parsed_attributes[key]['value'])


            elif style == 'Reference Name List':
                parsed_attributes[key] = proc_name_list(egeria_client, key, txt, labels, if_missing)
                if (parsed_attributes[key].get("value", None) and (
                        parsed_attributes[key]['exists'] is False or parsed_attributes[key]['valid'] is False)):
                    msg = (f"A Reference Name in `{parsed_attributes[key].get('name_list', None)}` is specified but "
                           f"does not exist")
                    logger.error(msg)
                    parsed_output['valid'] = False
                    parsed_output['reason'] += msg
            else:
                msg = f"Unknown attribute style: {style} for key `{key}`"
                logger.error(msg)
                sys.exit(1)
                parsed_attributes[key]['valid'] = False
                parsed_attributes[key]['value'] = None
            if key == "Display Name":
                display_name = parsed_attributes[key]['value']

            value = parsed_attributes[key].get('value', None)

            if value is not None:
                # if the value is a dict, get the flattened name list
                value = parsed_attributes[key].get('name_list', None) if isinstance(value, (dict, list)) else value
                parsed_output['display'] += f"\n\t* {key}: `{value}`\n\t"


    parsed_output['attributes'] = parsed_attributes

    if display_name is None:
        msg = f"No display name or name identifier found"
        logger.error(msg)
        parsed_output['valid'] = False
        parsed_output['reason'] = msg
        return parsed_output


    if parsed_attributes.get('Parent ID', {}).get('value', None) is not None:
        if (parsed_attributes['Parent Relationship Type Name']['value'] is None) or (
                parsed_attributes['Parent at End1']['value'] is None):
            msg = "Parent ID was found but either Parent `Relationship Type Name` or `Parent at End1` are missing"
            logger.error(msg)
            parsed_output['valid'] = False
            parsed_output['reason'] = msg
        if parsed_attributes['Parent Relationship Type Name'].get('exists', False) is False:
            msg = "Parent ID was found but does not exist"
            logger.error(msg)
            parsed_output['valid'] = False
            parsed_output['reason'] = msg

    if directive in ["validate", "process"] and object_action == "Update" and not parsed_output[
        'exists']:  # check to see if provided information exists and is consistent with existing info
        msg = f"Update request invalid, element `{display_name}` does not exist\n"
        logger.error(msg)
        parsed_output['valid'] = False
    if directive in ["validate", "process"] and not parsed_output['valid'] and object_action == "Update":
        msg = f"Request is invalid, `{object_action} {object_type}` is not valid - see previous messages\n"
        logger.error(msg)

    elif directive in ["validate",
                       "process"] and object_action == 'Create':  # if the object_action is create, check that it
        # doesn't already exist
        if parsed_output['exists']:
            msg = f"Element `{display_name}` cannot be created since it already exists\n"
            logger.error(msg)
            parsed_output['valid'] = False
        else:
            msg = f"Element `{display_name}` does not exist so it can be created\n"
            logger.info(msg)


    if parsed_output.get('qualified_name',None) and "* Qualified Name" not in parsed_output['display']:
        parsed_output['display'] += f"\n\t* Qualified Name: `{parsed_output['qualified_name']}`\n\t"
    if parsed_output.get('guid',None):
        parsed_output['display'] += f"\n\t* GUID: `{parsed_output['guid']}`\n\t"

    return parsed_output


@logger.catch
def parse_view_command(egeria_client: EgeriaTech, object_type: str, object_action: str, txt: str,
                         directive: str = "display") -> dict:
    parsed_attributes, parsed_output = {}, {}

    parsed_output['valid'] = True
    parsed_output['exists'] = False

    labels = {}
    if object_action in ["Unlink","Detach"]:
        command_spec = get_command_spec(f"Link {object_type}")
    else:
        command_spec = get_command_spec(f"{object_action} {object_type}")
    attributes = command_spec.get('Attributes', [])
    command_display_name = command_spec.get('display_name', None)

    parsed_output['reason'] = ""
    parsed_output['display'] = ""

    msg = f"\tProcessing {object_action} on  {object_type}  \n"
    logger.info(msg)

    # get the version early because we may need it to construct qualified names.

    for attr in attributes:
        for key in attr:
            # Run some checks to see if the attribute is appropriate to the operation and usage level

            level = attr[key].get('level', 'Basic')
            msg = (f"___\nProcessing `{key}` in `{object_action}` on a `{object_type}` "
                   f"\n\twith usage level: `{EGERIA_USAGE_LEVEL}` ")
            logger.trace(msg)

            if EGERIA_USAGE_LEVEL == "Basic" and level != "Basic":
                logger.trace(f"Attribute `{key}` is not supported for `{EGERIA_USAGE_LEVEL}` usage level. Skipping.",
                             highlight=True)
                continue
            if EGERIA_USAGE_LEVEL == "Advanced" and level in ["Expert", "Invisible"]:
                logger.trace(f"Attribute `{key}` is not supported for `{EGERIA_USAGE_LEVEL}` usage level. Skipping.",
                             highlight=True)
                continue
            if EGERIA_USAGE_LEVEL == "Expert" and level == "Invisible":
                logger.trace(f"Attribute `{key}` is not supported for `{EGERIA_USAGE_LEVEL}` usage level. Skipping.",
                             highlight=True)
                continue

            if attr[key].get('input_required', False) is True:
                if_missing = ERROR
            else:
                if_missing = INFO

            # lab = [item.strip() for item in re.split(r'[;,\n]+',attr[key]['attr_labels'])]
            lab = split_tb_string(attr[key]['attr_labels'])
            labels: set = set()
            labels.add(key.strip())

            if lab is not None and lab != [""]:
                labels.update(lab)

            # set these to none since not needed for view commands
            version = None
            command_qn_prefix = None

            default_value = attr[key].get('default_value', None)

            style = attr[key]['style']
            if style in ['Simple', 'Dictionary', 'Comment']:
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing, default_value)
            elif style == 'Valid Value':
                parsed_attributes[key] = proc_valid_value(txt, object_action, labels,
                                                          attr[key].get('valid_values', None), if_missing,
                                                          default_value)
            elif style == 'QN':
                parsed_attributes[key] = proc_el_id(egeria_client, command_display_name, command_qn_prefix, labels, txt,
                                                    object_action, version, if_missing)
                if key == 'Qualified Name' and parsed_attributes[key]['value'] and parsed_attributes[key][
                    'exists'] is False:
                    parsed_output['exists'] = False
            elif style == 'ID':
                parsed_attributes[key] = proc_el_id(egeria_client, command_display_name, command_qn_prefix, labels, txt,
                                                    object_action, version, if_missing)

                parsed_output['guid'] = parsed_attributes[key].get('guid', None)
                parsed_output['qualified_name'] = parsed_attributes[key].get('qualified_name', None)
                parsed_output['exists'] = parsed_attributes[key]['exists']
                if parsed_attributes[key]['valid'] is False:
                    parsed_output['valid'] = False
                    parsed_output['reason'] += parsed_attributes[key]['reason']

            elif style == 'Reference Name':
                parsed_attributes[key] = proc_ids(egeria_client, key, labels, txt, object_action, if_missing)
                if ((if_missing == ERROR) and parsed_attributes[key].get("value", None) is None):
                    msg = f"Required parameter `{parsed_attributes[key]['value']}` is missing"
                    logger.error(msg)
                    parsed_output['valid'] = False
                    parsed_output['reason'] += msg
                elif parsed_attributes[key]['value'] and parsed_attributes[key]['exists'] is False:
                    msg = f"Reference Name `{parsed_attributes[key]['value']}` is specified but does not exist"
                    logger.error(msg)
                    parsed_output['valid'] = False
                    parsed_output['reason'] += msg

            elif style == 'GUID':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing)
            elif style == 'Ordered Int':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing)
            elif style == 'Simple Int':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing, default_value, "int")
            elif style == 'Simple List':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing, default_value)
                name_list = parsed_attributes[key]['value']
                # attribute = re.split(r'[;,\n]+', name_list) if name_list is not None else None
                attribute = split_tb_string(name_list)
                parsed_attributes[key]['value'] = attribute
                parsed_attributes[key]['name_list'] = name_list
            elif style == 'Parent':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing, default_value)
            elif style == 'Bool':
                parsed_attributes[key] = proc_bool_attribute(txt, object_action, labels, if_missing, default_value)
            elif style == "Dictionary List":
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing, default_value)
                # parsed_attributes[key]['list'] = json.loads(parsed_attributes[key]['value'])

            elif style == 'Reference Name List':
                parsed_attributes[key] = proc_name_list(egeria_client, key, txt, labels, if_missing)
                if (parsed_attributes[key].get("value", None) and (
                        parsed_attributes[key]['exists'] is False or parsed_attributes[key]['valid'] is False)):
                    msg = (f"A Reference Name in `{parsed_attributes[key].get('name_list', None)}` is specified but "
                           f"does not exist")
                    logger.error(msg)
                    parsed_output['valid'] = False
                    parsed_output['reason'] += msg
            else:
                msg = f"Unknown attribute style: {style}"
                logger.error(msg)
                sys.exit(1)
                parsed_attributes[key]['valid'] = False
                parsed_attributes[key]['value'] = None

            value = parsed_attributes[key].get('value', None)

            if value is not None:
                # if the value is a dict, get the flattened name list
                value = parsed_attributes[key].get('name_list', None) if isinstance(value, (dict, list)) else value
                parsed_output['display'] += f"\n\t* {key}: `{value}`\n\t"

    parsed_output['attributes'] = parsed_attributes


    if directive in ["validate", "process"] and not parsed_output['valid'] and object_action == "Update":
        msg = f"Request is invalid, `{object_action} {object_type}` is not valid - see previous messages\n"
        logger.error(msg)


    return parsed_output


@logger.catch
def proc_simple_attribute(txt: str, action: str, labels: set, if_missing: str = INFO, default_value=None,
                          simp_type: str = None) -> dict:
    """Process a simple attribute based on the provided labels and if_missing value.
       Extract the attribute value from the text and store it in a dictionary along with valid.
       If it doesn`t exist, mark the dictionary entry as invalid and print an error message with severity of if_missing.

       Parameters:
       ----------
       txt: str
         The block of object_action text to extract attributes from.
       labels: list
         The possible attribute labels to search for. The first label will be used in messages.
       if_missing: str, default is INFO
         Can be one of "WARNING", "ERROR", "INFO". The severity of the missing attribute.
       default_value: default is None
        The default value to return if the attribute is missing.
    """
    valid = True

    if if_missing not in ["WARNING", "ERROR", "INFO"]:
        msg = "Invalid severity for missing attribute"
        logger.error(msg)
        return {"status": ERROR, "reason": msg, "value": None, "valid": False}

    if default_value == "":
        default_value = None

    attribute = extract_attribute(txt, labels)

    attribute = default_value if attribute is None else attribute.replace('\n', '')

    if attribute is None:
        if if_missing == INFO or if_missing == WARNING:
            msg = f"Optional attribute with labels: `{labels}` missing"
            valid = True
            logger.info(msg)
        else:
            msg = f"Missing attribute with labels `{labels}` "
            valid = False
            logger.error(msg)
        return {"status": if_missing, "reason": msg, "value": None, "valid": valid, "exists": False}

    if attribute and simp_type == "int" :
        attribute = int(attribute)

    return {"status": INFO, "OK": None, "value": attribute, "valid": valid, "exists": True}


@logger.catch
def proc_valid_value(txt: str, action: str, labels: set, valid_values: [], if_missing: str = INFO,
                     default_value=None) -> dict:
    """Process a string attribute to check that it is a member of the associated value values list.
       Extract the attribute value from the text and store it in a dictionary along with valid.
       If it doesn`t exist, mark the dictionary entry as invalid and print an error message with severity of if_missing.

       Parameters:
       ----------
       txt: str
         The block of object_action text to extract attributes from.
       labels: list
         The possible attribute labels to search for. The first label will be used in messages.
       if_missing: str, default is INFO
         Can be one of "WARNING", "ERROR", "INFO". The severity of the missing attribute.
       default_value: default is None
        The default value to return if the attribute is missing.
    """
    valid = True
    v_values = []

    if if_missing not in ["WARNING", "ERROR", "INFO"]:
        msg = "Invalid severity for missing attribute"
        logger.error(msg)
        return {"status": ERROR, "reason": msg, "value": None, "valid": False}
    if valid_values is None:
        msg = "Missing valid values list"
        logger.error(msg)
        return {"status": WARNING, "reason": msg, "value": None, "valid": False}
    if isinstance(valid_values, str):
        # v_values = [item.strip() for item in re.split(r'[;,\n]+', valid_values)]
        v_values = split_tb_string(valid_values)
    if isinstance(valid_values, list):
        v_values = valid_values
    if not isinstance(v_values, list):
        msg = "Valid values list is not a list"
        logger.error(msg)
        return {"status": WARNING, "reason": msg, "value": None, "valid": False}
    if len(v_values) == 0:
        msg = "Valid values list is empty"
        logger.error(msg)
        return {"status": WARNING, "reason": msg, "value": None, "valid": False}

    attribute = extract_attribute(txt, labels)
    if default_value == "":
        default_value = None
    attribute = default_value if attribute is None else attribute

    if attribute is None:
        if if_missing == INFO or if_missing == WARNING:
            msg = f"Optional attribute with labels: `{labels}` missing"
            logger.info(msg)
            valid = True
        else:
            msg = f"Missing attribute with labels `{labels}` "
            valid = False
            logger.error(msg)
        return {"status": if_missing, "reason": msg, "value": None, "valid": valid, "exists": False}
    else:
        if attribute not in v_values:
            msg = f"Invalid value for attribute `{labels}`"
            logger.warning(msg)
            return {"status": WARNING, "reason": msg, "value": attribute, "valid": False, "exists": True}

    return {"status": INFO, "OK": "OK", "value": attribute, "valid": valid, "exists": True}


@logger.catch
def proc_bool_attribute(txt: str, action: str, labels: set, if_missing: str = INFO, default_value=None) -> dict:
    """Process a boolean attribute based on the provided labels and if_missing value.
       Extract the attribute value from the text and store it in a dictionary along with valid.
       If it doesn`t exist, mark the dictionary entry as invalid and print an error message with severity of if_missing.

       Parameters:
       ----------
       txt: str
         The block of object_action text to extract attributes from.
       labels: list
         The possible attribute labels to search for. The first label will be used in messages.
       if_missing: str, default is INFO
         Can be one of "WARNING", "ERROR", "INFO". The severity of the missing attribute.
       default_value: default is None
        The default value to return if the attribute is missing.
    """
    valid = True

    if if_missing not in ["WARNING", "ERROR", "INFO"]:
        msg = "Invalid severity for missing attribute"
        logger.error(msg)
        return {"status": ERROR, "reason": msg, "value": None, "valid": False}

    attribute = extract_attribute(txt, labels)
    if default_value == "":
        default = None
    else:
        default = str_to_bool(default_value)
    attribute = default if attribute is None else attribute

    if attribute is None:
        if if_missing == INFO or if_missing == WARNING:
            msg = f"Optional attribute with labels: `{labels}` missing"
            logger.info(msg)
            valid = True
        else:
            msg = f"Missing attribute with labels `{labels}` "
            valid = False
            logger.error(msg)
        return {"status": if_missing, "reason": msg, "value": None, "valid": valid, "exists": False}

    if isinstance(attribute, str):
        attribute = attribute.strip().lower()
        if attribute in ["true", "yes", "1"]:
            attribute = True
        elif attribute in ["false", "no", "0"]:
            attribute = False
        else:
            msg = f"Invalid value for boolean attribute `{labels}`"
            logger.error(msg)
            return {"status": ERROR, "reason": msg, "value": attribute, "valid": False, "exists": True}

    return {"status": INFO, "OK": None, "value": attribute, "valid": valid, "exists": True}


@logger.catch
def proc_el_id(egeria_client: EgeriaTech, element_type: str, qn_prefix: str, element_labels: list[str], txt: str,
               action: str, version: str = None, if_missing: str = INFO) -> dict:
    """
    Processes display_name and qualified_name by extracting them from the input text,
    checking if the element exists in Egeria, and validating the information. If a qualified
    name isn't found, one will be created.

    Parameters
    ----------
    egeria_client: EgeriaTech
        Client object for interacting with Egeria.
    element_type: str
        type of element to process (e.g., 'blueprint', 'category', 'term')
    element_labels: a list of equivalent label names to use in processing the element.
    txt: str
        A string representing the input text to be processed for extracting element identifiers.
    action: str
        The action object_action to be executed (e.g., 'Create', 'Update', 'Display', ...)
    version: str, optional = None
        An optional version identifier used if we need to construct the qualified name

    Returns: dict with keys:
        status
        reason
        value   - value of display name
        valid   - name we parse out
        exists
        qualified_name - qualified name - either that we find or the one we construct
        guid - guid of the element if it already exists
    """
    valid = True
    exists = False
    identifier_output = {}

    element_name = extract_attribute(txt, element_labels)
    qualified_name = extract_attribute(txt, ["Qualified Name"])

    if element_name is None:
        msg = f"Optional attribute with label`{element_type}` missing"
        logger.info(msg)
        identifier_output = {"status": INFO, "reason": msg, "value": None, "valid": False, "exists": False, }
        return identifier_output

    if qualified_name:
        q_name, guid, unique, exists = get_element_by_name(egeria_client, element_type,
                                                           qualified_name)  # Qualified name could be different if it
        # is being updated
    else:
        q_name, guid, unique, exists = get_element_by_name(egeria_client, element_type, element_name)
        qualified_name = q_name

    if unique is False:
        msg = f"Multiple elements named  {element_name} found"
        logger.error(msg)
        identifier_output = {"status": ERROR, "reason": msg, "value": element_name, "valid": False, "exists": True, }
        valid = False

    if action == "Update" and not exists:
        msg = f"Element {element_name} does not exist"
        logger.error(msg)
        identifier_output = {"status": ERROR, "reason": msg, "value": element_name, "valid": False, "exists": False, }

    elif action in ["Update", "View"] and exists:
        msg = f"Element {element_name} exists"
        logger.info(msg)
        identifier_output = {
            "status": INFO, "reason": msg, "value": element_name, "valid": True, "exists": True,
            'qualified_name': q_name, 'guid': guid
            }

    elif action == "Create" and exists:
        msg = f"Element {element_name} already exists"
        logger.error(msg)
        identifier_output = {
            "status": ERROR, "reason": msg, "value": element_name, "valid": False, "exists": True,
            'qualified_name': qualified_name, 'guid': guid,
            }

    elif action == "Create" and not exists and valid:
        msg = f"{element_type} `{element_name}` does not exist"
        logger.info(msg)

        if q_name is None and qualified_name is None:
            q_name = egeria_client.__create_qualified_name__(qn_prefix, element_name, version_identifier=version)
            update_element_dictionary(q_name, {'display_name': element_name})

        elif qualified_name:
            update_element_dictionary(qualified_name, {'display_name': element_name})
            q_name = qualified_name

        identifier_output = {
            "status": INFO, "reason": msg, "value": element_name, "valid": True, "exists": False,
            'qualified_name': q_name
            }

    return identifier_output


@logger.catch
def proc_ids(egeria_client: EgeriaTech, element_type: str, element_labels: set, txt: str, action: str,
             if_missing: str = INFO, version: str = None) -> dict:
    """
    Processes element identifiers from the input text using the labels supplied,
    checking if the element exists in Egeria, and validating the information.
    Only a single element is allowed.

    Parameters
    ----------
    egeria_client: EgeriaTech
        Client object for interacting with Egeria.
    element_type: str
        type of element to process (e.g., 'blueprint', 'category', 'term')
    element_labels: a list of equivalent label names to use in processing the element.
    txt: str
        A string representing the input text to be processed for extracting element identifiers.
    action: str
        The action object_action to be executed (e.g., 'Create', 'Update', 'Display', ...)
    if_missing: str, optional = None
        Optional version identifier used if we need to construct the qualified name
    version: str, optional = INFO
        What to do if the element doesn't exist. Default is INFO. Can be one of "WARNING", "ERROR", "INFO".

    Returns: dict with keys:
        status
        reason
        value
        valid   - name we parse out
        exists
        qualified_name - what we find exists
        guid
    """
    valid = True
    exists = False
    identifier_output = {}
    unique = True
    value = None

    element_name = extract_attribute(txt, element_labels)

    if element_name:
        if '\n' in element_name or ',' in element_name:
            msg = f"Element name `{element_name}` appears to be a list rather than a single element"
            logger.error(msg)
            return {"status": ERROR, "reason": msg, "value": None, "valid": False, "exists": False, }
        q_name, guid, unique, exists = get_element_by_name(egeria_client, element_type, element_name)
        value = element_name
    else:
        exists = False
        q_name = None
        unique = None

    if exists is True and unique is False:
        # Multiple elements found - so need to respecify with qualified name
        msg = f"Multiple elements named  {element_name} found"
        logger.error(msg)
        identifier_output = {"status": ERROR, "reason": msg, "value": element_name, "valid": False, "exists": True, }


    elif action == EXISTS_REQUIRED or if_missing == ERROR and not exists:
        # a required identifier doesn't exist
        msg = f"Required {element_type} `{element_name}` does not exist"
        logger.error(msg)
        identifier_output = {"status": ERROR, "reason": msg, "value": element_name, "valid": False, "exists": False, }
    elif value is None and if_missing == INFO:
        # an optional identifier is empty
        msg = f"Optional attribute with label`{element_type}` missing"
        logger.info(msg)
        identifier_output = {"status": INFO, "reason": msg, "value": None, "valid": True, "exists": False, }
    elif value and exists is False:
        # optional identifier specified but doesn't exist
        msg = f"Optional attribute with label`{element_type}` specified but doesn't exist"
        logger.error(msg)
        identifier_output = {"status": ERROR, "reason": msg, "value": value, "valid": False, "exists": False, }

    else:
        # all good.
        msg = f"Element {element_type} `{element_name}` exists"
        logger.info(msg)
        identifier_output = {
            "status": INFO, "reason": msg, "value": element_name, "valid": True, "exists": True,
            "qualified_name": q_name, 'guid': guid
            }

    return identifier_output


@logger.catch
def proc_name_list(egeria_client: EgeriaTech, element_type: str, txt: str, element_labels: set,
                   if_missing: str = INFO) -> dict:
    """
    Processes a list of names specified in the given text, retrieves details for each
    element based on the provided type, and generates a list of valid qualified names.

    The function reads a text block, extracts a list of element names according to the specified
    element type, looks them up using the provided Egeria client, and classifies them as valid or
    invalid. It returns the processed names, a list of qualified names, and validity and existence
    flags.

    Args:

        egeria_client (EgeriaTech): The client instance to connect and query elements from an
            external system.
        Element_type (str): The type of element, such as schema or attribute, to process.
        Txt (str): The raw input text containing element names to be processed.
        element_labels: a list of equivalent label names to use in processing the element.
        required: bool, default is False
            - indicates whether the list of names is required to be present in the input text.

    Returns:
        Dict containing:
        'names'    - Concatenated valid input names as a single string (or None if empty).
        'name_list'    - A list of known qualified names extracted from the processed elements.
        'valid'    - A boolean indicating whether all elements are valid.
        'exists'    - A boolean indicating whether all elements exist.
    """
    valid = True
    exists = True
    id_list_output = {}
    elements = ""
    new_element_list = []
    guid_list = []
    elements_txt = extract_attribute(txt, element_labels)

    if elements_txt is None:
        msg = f"Attribute with labels `{{element_type}}` missing"
        logger.debug(msg)
        return {"status": if_missing, "reason": msg, "value": None, "valid": False, "exists": False, }
    else:
        # element_list = re.split(r'[;,\n]+', elements_txt)
        element_list = split_tb_string(elements_txt)
        element_details = {}
        for element in element_list:
            # Get the element using the generalized function
            known_q_name, known_guid, el_valid, el_exists = get_element_by_name(egeria_client, element_type, element)
            details = {"known_q_name": known_q_name, "known_guid": known_guid, "el_valid": el_valid}
            elements += element + ", "  # list of the input names

            if el_exists and el_valid:
                new_element_list.append(known_q_name)  # list of qualified names
                guid_list.append(known_guid)
            elif not el_exists:
                msg = f"No {element_type} `{element}` found"
                logger.debug(msg)
                valid = False
            valid = valid if el_valid is None else (valid and el_valid)
            exists = exists and el_exists
            element_details[element] = details

        if elements:
            msg = f"Found {element_type}: {elements}"
            logger.debug(msg)
            id_list_output = {
                "status": INFO, "reason": msg, "value": element_details, "valid": valid, "exists": exists,
                "name_list": new_element_list, "guid_list": guid_list,
                }
        else:
            msg = f" Name list contains one or more invalid qualified names."
            logger.debug(msg)
            id_list_output = {
                "status": if_missing, "reason": msg, "value": elements, "valid": valid, "exists": exists,
                "dict_list": element_details, "guid_list": guid_list
                }
        return id_list_output


@logger.catch
def update_term_categories(egeria_client: EgeriaTech, term_guid: str, categories_exist: bool,
                           categories_list: List[str]) -> None:
    """

    Adds or removes a term to/from specified categories in a glossary.

    This function associates a term, identified by its GUID, with one or more
    categories. It uses the provided EgeriaTech client to assign the term
    to the categories. If the GUID of a category is not readily available, it
    is retrieved either from a pre-loaded dictionary or through a client lookup.

    Args:
        egeria_client (EgeriaTech): The client to interact with the glossary.
        term_guid (str): The GUID of the term to be associated with categories.
        categories_exist (bool): Flag indicating whether the categories already
                                 exist.
        categories_list (List[str]): A list of category names to associate with
                                     the term.

    Returns:
        None
    """
    to_be_cat_guids: list[str] = []
    # find the categories a term is currently in.
    existing_categories = egeria_client.get_categories_for_term(term_guid)
    if type(existing_categories) is str:
        current_categories = []
    else:
        current_categories = [cat['elementHeader']['guid'] for cat in existing_categories]

    if categories_exist is True and categories_list is not None:
        if type(categories_list) is str:
            # categories_list = re.split(r'[;,\n]+', categories_list)
            # categories_list = categories_list.split(";,").trim()
            categories_list = split_tb_string(categories_list)
        for category in categories_list:
            cat_guid = None
            cat_el = category.strip()
            element_dict = get_element_dictionary()
            if cat_el in element_dict:
                cat = element_dict.get(cat_el, None)
                cat_guid = cat.get('guid', None) if cat else None
            if cat_guid is None:
                cat_guid = egeria_client.__get_guid__(qualified_name=cat_el)
                update_element_dictionary(cat_el, {'guid': cat_guid})
            to_be_cat_guids.append(cat_guid)

        for cat in to_be_cat_guids:
            if cat not in current_categories:
                egeria_client.add_term_to_category(term_guid, cat)
                current_categories.append(cat)
                msg = f"Added term {term_guid} to category {cat}"
                logger.info(msg)

        for cat in current_categories:
            if cat not in to_be_cat_guids:
                egeria_client.remove_term_from_category(term_guid, cat)
                msg = f"Removed term {term_guid} from category {cat}"
                logger.info(msg)
    else:  # No categories specified - so remove any categories a term is in
        for cat in current_categories:
            egeria_client.remove_term_from_category(term_guid, cat)
            msg = f"Removed term {term_guid} from category {cat}"
            logger.info(msg)




