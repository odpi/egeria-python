"""
This file contains general utility functions for processing Egeria Markdown
"""
import os
import re
import sys
import json
from datetime import datetime
from typing import Any
from loguru import logger
from rich import print
from rich.console import Console
from rich.markdown import Markdown

from pyegeria import Client2, PyegeriaException, egeria_client
from pyegeria.utils import (camel_to_title_case, body_slimmer)
from pyegeria._globals import DEBUG_LEVEL
from md_processing.md_processing_utils.message_constants import message_types

# Constants
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

GENERAL_GOVERNANCE_DEFINITIONS = ["Governance Definition", "Business Imperative", "Regulation Article", "Threat",
                                  "Governance Policy", "Governance Principle", "Governance Obligation",
                                  "Governance Approach",
                                  "Governance Processing Purpose"]
GOVERNANCE_DRIVERS = ["Governance Driver", "Governance Strategy", "Governance Imperative", "Regulation",
                     "Regulation Article", "Threat"]
GOVERNANCE_POLICIES = ["Governance Policy", "Governance Principle", "Governance Obligation", "Governance Approach"]


GOVERNANCE_CONTROLS = ["Governance Control", "Governance Rule", "Service Level Objective", "Governance Action",
                        "Security Access Control", "Governance Procedure","Governance Responsibility",
                       "Subject Area Definition", "Data Processing Purposes", "Methodology"]

ALL_GOVERNANCE_DEFINITIONS = GENERAL_GOVERNANCE_DEFINITIONS + GOVERNANCE_CONTROLS + ["Governance Strategy", "Regulation",
                                                "Security Group", "GovernanceMetric",
                                                "Naming Standard Rule", "TermsAndConditions", "Certification Type", "License Type"]
console = Console(width=EGERIA_WIDTH)
debug_level = DEBUG_LEVEL
global COMMAND_DEFINITIONS

def split_tb_string(input: str)-> [Any]:
    """Split the string and trim the items"""
    l = [item.strip() for item in re.split(r'[;,\n]+',input)] if input is not None else None
    return l

def str_to_bool(value: str) -> bool:
    """Converts a string to a boolean value."""
    return value.lower() in ("yes", "true", "t", "1")

def render_markdown(markdown_text: str) -> None:
    """Renders the given markdown text in the console."""
    console.print(Markdown(markdown_text))


def is_valid_iso_date(date_text) -> bool:
    """Checks if the given string is a valid ISO date."""
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def set_debug_level(directive: str) -> None:
    """Sets the debug level for the script."""
    global debug_level
    if directive == "display":
        debug_level = "display-only"


def get_current_datetime_string():
    """Returns the current date and time as a human-readable string."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    return now


def print_msg(msg_level: str, msg: str, verbosity: str):
    """
    Prints a message based on its type and verbosity level.

    This function handles the output of messages depending on the specified
    verbosity level and message type. It uses predefined message types and
    formats the output accordingly.

    Args:
        msg_level: The type of the message, such as 'WARNING', 'ERROR', 'INFO', or
            'ALWAYS'.
        msg: The content of the message to display.
        verbosity: The verbosity level, which determines how the message is
            displayed ('verbose', 'quiet', or 'debug').
    """
    if msg_level == "ALWAYS":
        print(f"{message_types.get(msg_level, '')}{msg}")
    # else:
    #     logger.info(f"{message_types.get(msg_level, '')}{msg}")
    # elif verbosity == "verbose" and msg_level in ["INFO", "WARNING", "ERROR"]:
    #     print(f"{message_types.get(msg_level, '')}{msg}")
    # elif verbosity == "quiet" and msg_level in ["WARNING", "ERROR"]:
    #     print(f"{message_types.get(msg_level, '')}{msg}")
    # elif verbosity == "debug" and msg_level in ["INFO", "WARNING", "ERROR", "DEBUG-INFO", "DEBUG-WARNING",
    #                                             "DEBUG-ERROR"]:
    #     print(f"{message_types.get(msg_level, '')}{msg}")
    # elif verbosity == "display-only" and msg_level in ["ALWAYS", "ERROR"]:
    #     print(f"{message_types.get(msg_level, '')}{msg}")
    elif msg_level == "ERROR":
        logger.error(f"{message_types.get(msg_level, '')}{msg}")
    elif msg_level == "WARNING":
        logger.warning(f"{message_types.get(msg_level, '')}{msg}")
    elif msg_level == "DEBUG":
        logger.debug(f"{message_types.get(msg_level, '')}{msg}")
    else:
        logger.info(f"{message_types.get(msg_level, '')}{msg}")

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


# Dictionary to store element information to avoid redundant API calls
element_dictionary = {}


def get_element_dictionary():
    """
    Get the shared element dictionary.

    Returns:
        dict: The shared element dictionary
    """
    global element_dictionary
    return element_dictionary


def update_element_dictionary(key, value):
    """
    Update the shared element dictionary with a new key-value pair.

    Args:
        key (str): The key to update
        value (dict): The value to associate with the key
    """
    global element_dictionary
    if (key is None or value is None):
        print(f"===>ERROR Key is {key} and value is {value}")
        return
    element_dictionary[key] = value


def clear_element_dictionary():
    """
    Clear the shared element dictionary.
    """
    global element_dictionary
    element_dictionary.clear()


def is_present(value: str) -> bool:
    global element_dictionary
    present = value in element_dictionary.keys() or any(
        value in inner_dict.values() for inner_dict in element_dictionary.values())
    return present


def find_key_with_value(value: str) -> str | None:
    """
    Finds the top-level key whose nested dictionary contains the given value.

    Args:
        data (dict): A dictionary where keys map to nested dictionaries.
        value (str): The value to search for.

    Returns:
        str | None: The top-level key that contains the value, or None if not found.
    """
    global element_dictionary
    # Check if the value matches a top-level key
    if value in element_dictionary.keys():
        return value

    # Check if the value exists in any of the nested dictionaries
    for key, inner_dict in element_dictionary.items():
        if value in inner_dict.values():
            return key

    return None  # If value not found


def set_find_body(object_type: str, attributes: dict)->dict:
    prop_name = object_type.replace(" ", "")
    s = attributes.get('Search String', {}).get('value', None)
    search_string = None if s =='*' else s


    body = {
        "class": "SearchStringRequestBody",
        "searchString": search_string,
        "startsWith": attributes.get('Start With', {}).get('value', True),
        "endWith": attributes.get('End With', {}).get('value', False),
        "ignoreCase": attributes.get('Ignore Case', {}).get('value', False),
        "limitResultsByStatus": attributes.get('Limit Results By Status', {}).get('value', []),
        "startFrom": int(attributes.get('Start From', {}).get('value', 0)),
        "pageSize": int(attributes.get('Page Size', {}).get('value', 0)),
        # "metadataElementSubtypeNames": attributes.get('Metadata Element Subtype Name', {}).get('value', None),
        "metadataElementTypeName": attributes.get('Metadata Element Type Name', {}).get('value', None),
        "effectiveTime": attributes.get('Effective Time', {}).get('value', None),
        "governanceZoneFilter" : attributes.get('Governance Zone Filter', {}).get('value', None),
        "graphQueryDepth": int(attributes.get('Graph Query Depth', {}).get('value', 0)),
    }

    return body


def set_create_body(object_type: str, attributes: dict)->dict:
    """
    Build the OUTER request body for a create action (NewElementRequestBody).

    Notes on two-layer convention:
    - Outer layer (this function): action wrapper with metadata like externalSource*, effectiveTime, anchor/parent hints, and an empty "properties" field.
    - Inner layer: an element-type-specific Properties structure built by set_element_prop_body, set_product_body, set_data_field_body, etc.
    Callers should build the inner body separately with the appropriate helper and then assign it to body["properties"].
    """
    prop_name = object_type.replace(" ", "")
    body = {
        "class": "NewElementRequestBody",
        "externalSourceGUID": attributes.get('External Source GUID', {}).get('guid', None),
        "externalSourceName": attributes.get('External Source Name', {}).get('value', None),
        "effectiveTime": attributes.get('Effective Time', {}).get('value', None),
        "governanceZoneFilter" : attributes.get('Governance Zone Filter', {}).get('value', None),
        "forLineage": attributes.get('For Lineage', {}).get('value', False),
        "forDuplicateProcessing": attributes.get('For Duplicate Processing', {}).get('value', False),
        "anchorGUID": attributes.get('Anchor ID', {}).get('guid', None),
        "isOwnAnchor": attributes.get('Is Own Anchor', {}).get('value', True),
        "parentGUID": attributes.get('Parent ID', {}).get('guid', None),
        "parentRelationshipTypeName": attributes.get('Parent Relationship Type Name', {}).get('value', None),
        "parentRelationshipProperties": attributes.get('Parent Relationship Properties', {}).get('value', None),
        "parentAtEnd1": attributes.get('Parent at End1', {}).get('value', True),
        "anchorScopeGUID": attributes.get('Anchor Scope GUID', {}).get('guid', None),
        "properties": "",
        "initialStatus": attributes.get('Status', {}).get('value', "ACTIVE"),
        "initialClassifications": {}}

    return body




def set_update_body(object_type: str, attributes: dict)->dict:
    """
    Build the OUTER request body for an update action (UpdateElementRequestBody).

    Two-layer convention:
    - Outer layer (this function) provides action metadata and an empty "properties" slot.
    - Inner layer must be constructed via element-specific helpers (e.g., set_element_prop_body) and assigned to the returned dict's "properties" key by the caller before invoking the client.
    """
    return {
      "class" : "UpdateElementRequestBody",
      "externalSourceGUID": attributes.get('External Source GUID', {}).get('guid', None),
      "externalSourceName": attributes.get('External Source Name', {}).get('value', None),
      "governanceZoneFilter": attributes.get('Governance Zone Filter', {}).get('value', None),
      "effectiveTime": attributes.get('Effective Time', {}).get('value', None),
      "forLineage": attributes.get('For Lineage', {}).get('value', False),
      "forDuplicateProcessing": attributes.get('For Duplicate Processing', {}).get('value', False),
              "mergeUpdate": attributes.get('Merge Update', {}).get('value', True),
      "properties": "",
    }
def set_rel_prop_body(object_type: str, attributes: dict)->dict:
    prop_name = object_type.replace(" ", "")
    display_name = attributes.get('Display Name', {}).get('value', None)

    return {
        "class": prop_name + "Properties",
        "description": attributes['Description'].get('value', None),
        "label": attributes.get('Label', {}).get('value', None) or attributes.get('Link Label', {}).get('value', None),
        "typeName" : attributes.get('Type Name', {}).get('value', None),
        "effectiveFrom": attributes.get('Effective From', {}).get('value', None),
        "effectiveTo": attributes.get('Effective To', {}).get('value', None),
        "extendedProperties": attributes.get('Extended Properties', {}).get('value', None),
        }

def set_element_prop_body(object_type: str, qualified_name: str, attributes: dict)->dict:
    """
    Build the INNER element-specific Properties body to be placed under the outer body's "properties" key.

    This returns the typed properties structure (e.g., "ReferenceableProperties" subtypes) appropriate for the object_type.
    Usage example:
    - outer = set_create_body(object_type, attributes)
    - props = set_element_prop_body(object_type, qualified_name, attributes)
    - outer["properties"] = props
    - client.create_xxx(outer)
    """
    prop_name = object_type.replace(" ", "")
    display_name = attributes.get('Display Name', {}).get('value', None)

    return {
        "class": prop_name + "Properties",
        "displayName": attributes.get('Display Name', {}).get('value', None),
        "qualifiedName" : qualified_name,
        "description": attributes['Description'].get('value', None),
        "category": attributes.get('Category', {}).get('value', None),
        "identifier": attributes.get('Identifier', {}).get('value', None),
        "userDefinedStatus": attributes.get('User Defined Status', {}).get('value', None),
        "versionIdentifier": attributes.get('Version Identifier', {}).get('value', None),
        "effectiveFrom": attributes.get('Effective From', {}).get('value', None),
        "effectiveTo": attributes.get('Effective To', {}).get('value', None),
        "additionalProperties": attributes.get('Additional Properties', {}).get('value', None),
        "extendedProperties": attributes.get('Extended Properties', {}).get('value', None),
        "supportLevel": attributes.get('Support Level', {}).get('value', None),
        "serviceLevels": attributes.get('Service Levels', {}).get('value', None),
        }

def set_product_body(object_type: str, qualified_name: str, attributes: dict)->dict:
    prop_bod = set_element_prop_body(object_type, qualified_name, attributes)
    prop_bod["identifier"] = attributes.get('Identifier', {}).get('value', None)
    prop_bod["productName"] = attributes.get('Product Name', {}).get('value', None)
    prop_bod["maturity"] = attributes.get('Maturity', {}).get('value', None)
    prop_bod["serviceLife"] = attributes.get('Service Life', {}).get('value', None)
    prop_bod["introductionDate"] = attributes.get('Introduction Date', {}).get('value', [])
    prop_bod["withdrawalDate"] = attributes.get('Withdrawal Date', {}).get('value', [])
    prop_bod["nextVersion"] = attributes.get('Next Version Date', {}).get('value', [])
    return prop_bod

def set_data_field_body(object_type: str, qualified_name: str, attributes: dict)->dict:
    prop_bod = set_element_prop_body(object_type, qualified_name, attributes)
    prop_bod["namespace"] = attributes.get('Namespace', {}).get('value', None)
    prop_bod["aliases"] = attributes.get('Aliases', {}).get('value', [])
    prop_bod["namePatterns"] = attributes.get('Name Patterns', {}).get('value', [])
    prop_bod["defaultValue"] = attributes.get('Default Value', {}).get('value', None)
    prop_bod["isNullable"] = attributes.get('Is Nullable', {}).get('value', None)
    prop_bod["dataType"] = attributes.get('Data Type', {}).get('value', None)
    prop_bod["units"] = attributes.get('Units', {}).get('value', None)
    prop_bod["minimumLength"] = attributes.get('Minimum Length', {}).get('value', None)
    prop_bod["length"] = attributes.get('Length', {}).get('value', None)
    prop_bod["precision"] = attributes.get('Precision', {}).get('value', None)
    prop_bod["orderedValues"] = attributes.get('Ordered Values', {}).get('value', [])
    prop_bod["sortOrder"] = attributes.get('Sort Order', {}).get('value', None)
    return prop_bod

def set_update_status_body(object_type: str, attributes: dict)->dict:
    return {
      "class" : "UpdateStatusRequestBody",
      "effectiveTime": attributes.get('Effective Time', {}).get('value', None),
      "forLineage": attributes.get('For Lineage', {}).get('value', False),
      "forDuplicateProcessing": attributes.get('For Duplicate Processing', {}).get('value', False),
      "mergeUpdate": attributes.get('Merge Update', {}).get('value', True),
    }

def set_gov_prop_body(object_type: str, qualified_name: str, attributes: dict)->dict:
    prop_name = object_type.replace(" ", "")
    prop_bod = set_element_prop_body(object_type, qualified_name, attributes)
    prop_bod["domainIdentifier"] = attributes.get('Domain Identifier', {}).get('value', None)
    prop_bod["displayName"]= attributes.get('Display Name', {}).get('value', None)
    prop_bod['qualifiedName'] = qualified_name
    prop_bod["versionIdentifier"] = attributes.get('Version Identifier', {}).get('value', None)
    prop_bod["summary"] = attributes.get('Summary', {}).get('value', None)
    prop_bod["description"] = attributes.get('Description', {}).get('value', None)

    prop_bod["scope"] = attributes.get('Scope', {}).get('value', None)
    prop_bod["importance"] = attributes.get('Importance', {}).get('value', None)
    prop_bod["implications"] = attributes.get('Implication', {}).get('value', [])
    prop_bod["outcomes"] = attributes.get('Outcomes', {}).get('value', [])
    prop_bod["results"] = attributes.get('Results', {}).get('value', []) or []
    prop_bod["effectiveFrom"] = attributes.get('Effective From', {}).get('value', None),
    prop_bod["effectiveTo"] = attributes.get('Effective To', {}).get('value', None),
    prop_bod["additionalProperties"] = attributes.get('Additional Properties', {}).get('value', None),
    prop_bod["extendedProperties"] = attributes.get('Extended Properties', {}).get('value', None)


    body = update_gov_body_for_type(object_type, prop_bod, attributes)
    return body
    

def update_gov_body_for_type(object_type: str, body: dict, attributes: dict) -> dict:
    gov_def_name = object_type.replace(" ", "")
    if object_type in GENERAL_GOVERNANCE_DEFINITIONS:
        return body
    elif object_type == "Governance Strategy":
        body['businessImperatives'] = attributes.get('Business Imperatives', {}).get('value', [])
        return body

    elif object_type == "Regulation":
        body['regulationSource'] = attributes.get('Regulation Source', {}).get('value', None)
        body['regulators'] = attributes.get('Regulators', {}).get('value', [])
        return body

    elif object_type in GOVERNANCE_CONTROLS:
        body['implementationDescription'] = attributes.get('Implementation Description', {}).get('value', None)
        return body
    elif object_type == "Security Group":
        body['distinguishedName'] = attributes.get('Distinguished Name', {}).get('value', None)
        return body
    elif object_type == "GovernanceMetric":
        body['measurement'] = attributes.get('Measurement', {}).get('value', None)
        body['target'] = attributes.get('Target', {}).get('value', None)
        return body
    elif object_type == "Naming Standard Rule":
        body['namePatterns'] = attributes.get('Name Patterns', {}).get('value', [])
        return body
    elif object_type in ["TermsAndConditions", "Certification Type", "License Type"]:
        entitlements = attributes.get('Entitlementss', {}).get('value', {}) if attributes.get('Entitlementss',None) else None
        restrictions = attributes.get('Restrictions', {}).get('value', {}) if attributes.get('Restrictions',None) else None
        obligations = attributes.get('Obligations', {}).get('value', {}) if attributes.get('Obligations',None) else None
        body['entitlements'] = entitlements
        body['restrictions'] = restrictions
        body['obligations'] = obligations

        return body


def set_rel_request_body(object_type: str, attributes: dict)->dict:
    """
    Build the OUTER request body for creating a relationship (NewRelationshipRequestBody).
    The inner relationship properties must be assigned to the returned dict under the "properties" key,
    commonly via set_rel_prop_body or set_rel_request_body_for_type.
    """
    return {
      "class" : "NewRelationshipRequestBody",
      "externalSourceGUID": attributes.get('External Source GUID', {}).get('guid', None),
      "externalSourceName": attributes.get('External Source Name', {}).get('value', None),
      "effectiveTime": attributes.get('Effective Time', {}).get('value', None),
      "forLineage": attributes.get('For Lineage', {}).get('value', False),
      "forDuplicateProcessing": attributes.get('For Duplicate Processing', {}).get('value', False),
      "properties": "",
    }

def set_peer_gov_def_request_body(object_type: str, attributes: dict)->dict:
    rel_body = set_rel_request_body(object_type, attributes)
    rel_body["properties"] = {
        "class" : "PeerDefinitionProperties",
        "description": attributes.get('Description', {}).get('value', None),
        "effectiveFrom": attributes.get('Effective From', {}).get('value', None),
        "effectiveTo": attributes.get('Effective To', {}).get('value', None),
        "label": attributes.get('Label', {}).get('value', None),
        }
    return rel_body

def set_rel_request_body_for_type(object_type: str, attributes: dict)->dict:
    """
    Convenience helper that builds both layers (outer + inner) for a relationship of a known type.
    It creates the outer NewRelationshipRequestBody via set_rel_request_body and fills rel_body["properties"]
    with a typed properties structure under the "class" of f"{object_type}Properties".
    """
    rel_body = set_rel_request_body(object_type, attributes)
    # class_prop = camel_to_title_case(object_type) + "Properties"
    class_prop = f"{object_type}Properties"
    rel_body["properties"] = {
        "class" : class_prop,
        "description": attributes.get('Description', {}).get('value', None),
        "effectiveFrom": attributes.get('Effective From', {}).get('value', None),
        "effectiveTo": attributes.get('Effective To', {}).get('value', None),
        "label": attributes.get('Label', {}).get('value', None),
        }
    return rel_body

def set_delete_request_body(object_type: str, attributes: dict)->dict:
    return {
        "class": "DeleteElementRequestBody",
        "externalSourceGUID": attributes.get('External Source GUID', {}).get('guid', None),
        "externalSourceName": attributes.get('External Source Name', {}).get('value', None),
        "effectiveTime": attributes.get('Effective Time', {}).get('value', None),
        "forLineage": attributes.get('For Lineage', {}).get('value', False),
        "forDuplicateProcessing": attributes.get('For Duplicate Processing', {}).get('value', False)
        }



def set_filter_request_body(object_type: str, attributes: dict)->dict:
    return {
            "class": "FilterRequestBody",
            "asOfTime": attributes.get('AsOfTime', {}).get('value', None),
            "effectiveTime": attributes.get('Effective Time', {}).get('value', None),
            "forLineage": attributes.get('For Lineage', {}).get('value', False),
            "forDuplicateProcessing": attributes.get('For Duplicate Processing', {}).get('value', False),
            "limitResultsByStatus": attributes.get('Limit Result by Status', {}).get('value', None),
            "sequencingOrder": attributes.get('Sequencing Order', {}).get('value', None),
            "sequencingProperty": attributes.get('Sequencing Property', {}).get('value', None),
            "filter": attributes.get('Search String', {}).get('value', None),
             }

def set_element_status_request_body(object_type: str, attributes: dict)->dict:
    return {
        "class": f"{camel_to_title_case(object_type)}StatusRequestBody",
        "status": attributes.get('Status', {}).get('value', None),
        "externalSourceGUID": attributes.get('External Source GUID', {}).get('guid', None),
        "externalSourceName": attributes.get('External Source Name', {}).get('value', None),
        "effectiveTime": attributes.get('Effective Time', {}).get('value', None),
        "forLineage": attributes.get('For Lineage', {}).get('value', False),
        "forDuplicateProcessing": attributes.get('For Duplicate Processing', {}).get('value', False)
    }


def set_classifications(object_type: str, attributes: dict)->dict:
    classifications = attributes.get('Classifications', {}).get('name_list', None)
    body = None
    if classifications:
        body = {classification: {} for classification in classifications} if classifications else {}
    return body

def set_object_classifications(object_type: str, attributes: dict, obj_types: list[str])->dict:
    classifications = attributes.get('Classifications', {}).get('name_list', None)
    obj = object_type.replace(" ", "")
    if object_type in obj_types:
        if classifications:
            if object_type not in classifications:
                classifications.append(obj)
        else:
            classifications = [obj]

    body = {}
    if classifications:
        for classification in classifications:
            body[classification] = {"class" : f"{classification}Properties"}
    return body

def add_search_keywords(client: Client2, element_guid: str, keywords: list[str]):
    """Add a search keyword to an element. Throw an exception if a problem is encountered.

    Args:
        client (Client2): The Egeria client instance.
        element_guid (str): The GUID of the element to add the keyword to.
        keyword (str): The search keyword to add.

    Returns:
        None
    """
    try:
        for keyword in keywords:
            client.add_search_keyword_to_element(element_guid, keyword)
            print("Added keyword `{}` to element `{}`".format(keyword, element_guid))

    except PyegeriaException as e:
        context = {
            "readon" : "Exception encountered executing add_search_keyword",
            "element_guid": element_guid,
            "keyword": keyword,
            "exception": str(e)
        }
        raise PyegeriaException(context = context)

def add_note_in_dr_e(client: Client2, qualified_name: str, display_name: str, journal_entry: str)-> str:
    if journal_entry:
        note_log_qn = f"{qualified_name}-NoteLog"
        note_log_display_name = f"{display_name}-NoteLog"
        note_display_name = f"{qualified_name}-Journal-Entry-{datetime.now().strftime('%Y-%m-%d %H:%M')}"
        journal_entry_guid = client.add_journal_entry(note_log_qn, qualified_name, note_log_display_name,
                                                      note_display_name, journal_entry)
        logger.info(f"Added journal entry `{journal_entry_guid}` to `{qualified_name}`")
        return journal_entry_guid
    else:
        return None