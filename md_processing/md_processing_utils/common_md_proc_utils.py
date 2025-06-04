"""
This file contains general utility functions for processing Egeria Markdown
"""
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
logger.add(sys.stderr, level="SUCCESS", format=log_format, colorize=True)
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

    command_spec = get_command_spec(object_type)
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

            elif style == 'GUID':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing)
            elif style == 'Ordered Int':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing)
            elif style == 'Simple Int':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing, default_value)
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
            if key == "Display Name":
                display_name = parsed_attributes[key]['value']

            value = parsed_attributes[key].get('value', None)

            if value is not None:
                # if the value is a dict, get the flattened name list
                value = parsed_attributes[key].get('name_list', None) if isinstance(value, (dict, list)) else value

                parsed_output['display'] += f"\n\t* {key}: `{value}`\n\t"

    parsed_output['attributes'] = parsed_attributes

    if display_name is None:
        msg = f"No displau name or name identifier found"
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
            msg = f"It is valid to create Element `{display_name}`"
            logger.success(msg)

    return parsed_output


@logger.catch
def parse_view_command(egeria_client: EgeriaTech, object_type: str, object_action: str, txt: str,
                         directive: str = "display") -> dict:
    parsed_attributes, parsed_output = {}, {}

    parsed_output['valid'] = True
    parsed_output['exists'] = False

    labels = {}

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
                if ((if_missing == ERROR) and parsed_attributes[key].get("value", None) and parsed_attributes[key][
                    'exists'] is False):
                    msg = f"Reference Name `{parsed_attributes[key]['value']}` is specified but does not exist"
                    logger.error(msg)
                    parsed_output['valid'] = False
                    parsed_output['reason'] += msg

            elif style == 'GUID':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing)
            elif style == 'Ordered Int':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing)
            elif style == 'Simple Int':
                parsed_attributes[key] = proc_simple_attribute(txt, object_action, labels, if_missing, default_value)
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
def proc_simple_attribute(txt: str, action: str, labels: set, if_missing: str = INFO, default_value=None) -> dict:
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

    attribute = extract_attribute(txt, labels)
    if default_value == "":
        default_value = None
    attribute = default_value if attribute is None else attribute

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

    elif action == "Update" and exists:
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
        logger.info(msg)
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
                logger.warning(msg)
                valid = False
            valid = valid if el_valid is None else (valid and el_valid)
            exists = exists and el_exists
            element_details[element] = details

        if elements:
            msg = f"Found {element_type}: {elements}"
            logger.info(msg)
            id_list_output = {
                "status": INFO, "reason": msg, "value": element_details, "valid": valid, "exists": exists,
                "name_list": new_element_list, "guid_list": guid_list,
                }
        else:
            msg = f" Name list contains one or more invalid qualified names."
            logger.info(msg)
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


@logger.catch
def add_member_to_data_collections(egeria_client: EgeriaTech, collection_list: list, display_name: str,
                                   guid: str) -> None:
    """
    Add member to data dictionaries and data specifications.
    """
    body = {
        "class": "CollectionMembershipProperties", "membershipRationale": "User Specified",
        "notes": "Added by Dr.Egeria"
        }
    try:
        for collection in collection_list:
            egeria_client.add_to_collection(collection, guid, body)
            msg = f"Added `{display_name}` member to `{collection}`"
            logger.info(msg)
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
                                       collection_type: str, guid: str, display_name: str,
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
        # compare the existing collections to desired collections
        if collection_type == "Data Dictionary":
            as_is = set(coll_list.get("DictList", None))
        elif collection_type == "Data Specification":
            as_is = set(coll_list.get("SpecList", None))

        dict_set = set(coll_list.get("DictList", None))
        spec_set = set(coll_list.get("SpecList", None))
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
    if replace_all_props:
        rel_el_list = egeria_client.get_data_field_rel_elements(guid)
        # should I throw an exception if empty?
        as_is_data_structs = set(rel_el_list.get("data_structure_guids", []))
        as_is_parent_fields = set(rel_el_list.get("parent_guids", []))
        as_is_assigned_meanings = set(rel_el_list.get("assigned_meanings_guids", []))
        as_is_data_classes = set(rel_el_list.get("data_class_guids", []))

        to_be_data_structs = set(structure_list) if structure_list is not None else set()
        to_be_parent_fields = set(parent_field_list) if parent_field_list is not None else set()
        to_be_assigned_meanings = set(terms) if terms is not None else set()
        to_be_data_classes = set(data_class_guid) if data_class_guid is not None else set()

        logger.trace(f"as_is_data_structs: {list(as_is_data_structs)} to_be_data_struct: {list(to_be_data_structs)}")
        logger.trace(
            f"as_is_parent_fields: {list(as_is_parent_fields)} to_be_parent_fields: {list(to_be_parent_fields)}")
        logger.trace(
            f"as_is_assigned_meanings: {list(as_is_assigned_meanings)} to_be_assigned_meanings: "
            f"{list(to_be_assigned_meanings)}")
        logger.trace(
            f"as_is_data_classes: {list(as_is_data_classes)} to_be_assigned_data_classes: "
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

        classes_to_remove = as_is_data_classes - to_be_data_classes
        logger.trace(f"classes_to_remove: {list(classes_to_remove)}")
        if len(terms_to_remove) > 0:
            for dc in classes_to_remove:
                egeria_client.detach_data_class_definition(guid, dc)
                msg = f"Removed `{dc}` from `{display_name}`"
                logger.trace(msg)
        classes_to_add = to_be_data_classes - as_is_data_classes
        logger.trace(f"classes_to_add: {list(classes_to_add)}")
        if len(terms_to_add) > 0:
            for dc in classes_to_add:
                egeria_client.link_data_class_definition(guid, dc)
                msg = f"Added `{dc}` to`{display_name}`"
                logger.trace(msg)


    else:  # merge - add field to related elements
        add_field_to_data_structures(egeria_client, display_name, structure_list, guid)
        msg = f"Added `{display_name}` to `{structure_list}`"
        logger.trace(msg)

        for field in parent_field_list:
            egeria_client.link_nested_data_field(field, guid, None)
            msg = f"Added `{display_name}` to `{field}`"
            logger.trace(msg)
        for term in terms:
            egeria_client.link_semantic_definition(guid, term, None)
            msg = f"Added `{term}` to `{display_name}`"
            logger.trace(msg)

        egeria_client.link_data_class_definition(guid, data_class_guid)
        msg = f"Added `{data_class_guid}` to `{display_name}`"
        logger.trace(msg)

@logger.catch
def sync_data_class_rel_elements(egeria_client: EgeriaTech, containing_data_class_guids: list, terms: list,
                                 containing_data_classes: list, super_data_classes: list, guid: str,
                                 display_name: str, replace_all_props: bool = True) -> None:
    """Sync a data class' related elements.

    TODO:  may need to revisit bodies.

    """
    if replace_all_props:
        rel_el_list = egeria_client.get_data_field_rel_elements(guid)
        # should I throw an exception if empty?
        as_is_containing_data_class_guids = set(rel_el_list.get("data_structure_guids", []))
        as_is_parent_fields = set(rel_el_list.get("parent_guids", []))
        as_is_assigned_meanings = set(rel_el_list.get("assigned_meanings_guids", []))
        as_is_data_classes = set(rel_el_list.get("data_class_guids", []))

    #     to_be_data_structs = set(structure_list) if structure_list is not None else set()
    #     to_be_parent_fields = set(parent_field_list) if parent_field_list is not None else set()
    #     to_be_assigned_meanings = set(terms) if data_class_list is not None else set()
    #     to_be_assigned_data_classes = set(data_class_list) if data_class_list is not None else set()
    #
    #     logger.trace(f"as_is_data_structs: {list(as_is_data_structs)} to_be_data_struct: {list(to_be_data_structs)}")
    #     logger.trace(
    #         f"as_is_parent_fields: {list(as_is_parent_fields)} to_be_parent_fields: {list(to_be_parent_fields)}")
    #     logger.trace(
    #         f"as_is_assigned_meanings: {list(as_is_assigned_meanings)} to_be_assigned_meanings: "
    #         f"{list(to_be_assigned_meanings)}")
    #     logger.trace(
    #         f"as_is_data_classes: {list(as_is_data_classes)} to_be_assigned_data_classes: "
    #         f"{list(to_be_assigned_data_classes)}")
    #
    #     data_struct_to_remove = as_is_data_structs - to_be_data_structs
    #     logger.trace(f"data_struct_to_remove: {list(data_struct_to_remove)}")
    #     if len(data_struct_to_remove) > 0:
    #         for ds in data_struct_to_remove:
    #             egeria_client.detach_member_data_field(ds, guid, None)
    #             msg = f"Removed `{display_name}` from structure `{ds}`"
    #             logger.trace(msg)
    #     data_struct_to_add = to_be_data_structs - as_is_data_structs
    #     logger.trace(f"data_struct_to_add: {list(data_struct_to_add)}")
    #     if len(data_struct_to_add) > 0:
    #         for ds in data_struct_to_add:
    #             egeria_client.link_member_data_field(ds, guid, None)
    #             msg = f"Added `{display_name}` to structure `{ds}`"
    #             logger.trace(msg)
    #
    #     parent_field_to_remove = to_be_parent_fields - as_is_parent_fields
    #     logger.trace(f"parent_field_to_remove: {list(parent_field_to_remove)}")
    #     if len(parent_field_to_remove) > 0:
    #         for field in parent_field_to_remove:
    #             egeria_client.detach_nested_data_field(field, guid, None)
    #             msg = f"Removed `{display_name}` from field `{field}`"
    #             logger.trace(msg)
    #     parent_field_to_add = to_be_parent_fields - as_is_parent_fields
    #     logger.trace(f"parent_field_to_add: {list(parent_field_to_add)}")
    #     if len(parent_field_to_add) > 0:
    #         for field in parent_field_to_add:
    #             egeria_client.link_nested_data_field(field, guid, None)
    #             msg = f"Added `{display_name}` to field `{field}`"
    #             logger.trace(msg)
    #
    #     terms_to_remove = as_is_assigned_meanings - to_be_assigned_meanings
    #     logger.trace(f"terms_to_remove: {list(terms_to_remove)}")
    #     if len(terms_to_remove) > 0:
    #         for term in terms_to_remove:
    #             egeria_client.detach_semantic_definition(guid, term, None)
    #             msg = f"Removed `{term}` from `{display_name}`"
    #             logger.trace(msg)
    #     terms_to_add = to_be_assigned_meanings - as_is_assigned_meanings
    #     logger.trace(f"terms_to_add: {list(terms_to_add)}")
    #     if len(terms_to_add) > 0:
    #         for term in terms_to_add:
    #             egeria_client.link_semantic_definition(guid, term, None)
    #             msg = f"Added `{term}` to`{display_name}`"
    #             logger.trace(msg)
    #
    # else:  # merge - add field to related elements
    #     add_field_to_data_structures(egeria_client, display_name, structure_list, guid)
    #     msg = f"Added `{display_name}` to `{structure_list}`"
    #     logger.trace(msg)
    #
    #     for field in parent_field_list:
    #         egeria_client.link_nested_data_field(field, guid, None)
    #         msg = f"Added `{display_name}` to `{field}`"
    #         logger.trace(msg)
    #     for term in terms:
    #         egeria_client.link_semantic_definition(guid, term, None)
    #         msg = f"Added `{term}` to `{display_name}`"
    #         logger.trace(msg)


def sync_data_spec_membership(egeria_client: EgeriaTech, in_data_spec_names: list, in_data_spec: dict, guid: str,
                              object_type: str) -> dict:
    pass


def sync_term_links(egeria_client: EgeriaTech, term_guid: str, links_exist: bool, links_list: List[str]) -> None:
    pass


def sync_parent_data_field(egeria_client: EgeriaTech, term_guid: str, links_exist: bool, links_list: List[str]) -> None:
    pass
