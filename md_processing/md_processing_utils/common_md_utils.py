"""
This file contains general utility functions for processing Egeria Markdown
"""
import os
import re
from datetime import datetime
from typing import Any
from loguru import logger
from rich import print
from rich.console import Console
from rich.markdown import Markdown

from pyegeria import settings, ServerClient, PyegeriaException
from pyegeria.core.config import resolve_egeria_credentials
from pyegeria.core.utils import (camel_to_title_case)
from pyegeria.core._globals import DEBUG_LEVEL, GovernanceDomains, resolve_enum
from md_processing.md_processing_utils.message_constants import message_types
from md_processing.md_processing_utils.element_status import element_status_properties
from md_processing.md_processing_utils.typed_properties import (parent_relationship_properties,
                                                                  record_not_applied)

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
# Same precedence as the dr_egeria CLI: env, then config.json / .env, then defaults (ISSUE-161).
EGERIA_USER, EGERIA_USER_PASSWORD = resolve_egeria_credentials()
EGERIA_WIDTH = settings.Environment.egeria_width
EGERIA_JUPYTER = settings.Environment.egeria_jupyter
EGERIA_HOME_GLOSSARY_GUID = os.environ.get("EGERIA_HOME_GLOSSARY_GUID", None)
EGERIA_GLOSSARY_PATH = os.environ.get("EGERIA_GLOSSARY_PATH", None)
EGERIA_ROOT_PATH = os.environ.get("EGERIA_ROOT_PATH", "../../")
EGERIA_INBOX_PATH = os.environ.get("EGERIA_INBOX_PATH", "md_processing/dr_egeria_inbox")
EGERIA_OUTBOX_PATH = os.environ.get("EGERIA_OUTBOX_PATH", "md_processing/dr_egeria_outbox")

GENERAL_GOVERNANCE_DEFINITIONS = [
    "Governance Definition", "Business Imperative", "Regulation Article", "Threat",
    "Governance Policy", "Governance Principle", "Governance Obligation",
    "Governance Approach", "Data Processing Purpose",
]
GOVERNANCE_DRIVERS = ["Governance Driver", "Governance Strategy", "Governance Imperative", "Regulation",
                     "Regulation Article", "Threat"]
GOVERNANCE_POLICIES = ["Governance Policy", "Governance Principle", "Governance Obligation", "Governance Approach"]


GOVERNANCE_CONTROLS = [
    "Governance Control", "Governance Rule", "Service Level Objective", "Service Level Objectives",
    "Governance Action", "Security Access Control", "Governance Procedure", "Governance Responsibility",
    "Subject Area Definition", "Methodology", "Governance Metric",
]

ALL_GOVERNANCE_DEFINITIONS = GENERAL_GOVERNANCE_DEFINITIONS + GOVERNANCE_CONTROLS + [
    "Governance Strategy", "Regulation", "Security Group", "Governance Zone", "Notification Type",
    "Naming Standard Rule", "TermsAndConditions", "Terms & Conditions", "Certification Type", "License Type",
]
console = Console(width=EGERIA_WIDTH)
debug_level = DEBUG_LEVEL
ATTRIBUTE_LOG_LEVEL = os.environ.get("EGERIA_ATTRIBUTE_LOG_LEVEL", "debug").lower()
global COMMAND_DEFINITIONS

def split_tb_string(input: str)-> [Any]:
    """Split the string and trim the items, supporting markdown bullets"""
    if input is None:
        return None
    items = re.split(r'[;,\n]+', input)
    results = []
    for item in items:
        item = item.strip()
        if item:
            # Strip leading markdown bullet if present
            item = re.sub(r'^[\-\*\+]\s*', '', item)
            results.append(item)
    return results

_LIST_BULLET = re.compile(r'^\s*[\-\*\+]\s+')
#: A separator followed by another bullet marker: an inline list on one line ("- a; - b, c").
_INLINE_BULLETS = re.compile(r'[;,]\s*[\-\*\+]\s+')


def split_list_value(text: Any) -> list | None:
    """The items of a list attribute's VALUE (Simple List, List, NameList, Reference Name List).

    - A bulleted or multi-line value: each bullet (or line) is one item, verbatim -- a comma inside a
      bullet is part of the item ("- agreed with the depending domain, not set by IT alone" is one
      item). A leading markdown bullet (`- `, `* `, `+ `) is stripped. Wrapped continuations and
      wrapped prose are handled by `_split_multiline`.
    - A single-line value is split on commas and semicolons ("a, b" is two items), including an inline
      bulleted list on one line ("- a; - b, c" is three); a single bullet on its own line is one item.

    Until 6.2.39 every value was split on commas, semicolons and newlines, so a bullet with a comma
    became two items. Spec metadata (labels, valid values) still uses `split_tb_string`.
    """
    if text is None:
        return None
    if isinstance(text, (list, tuple)):
        return [str(i).strip() for i in text if str(i).strip()]
    lines = [line for line in str(text).splitlines() if line.strip()]
    if not lines:
        return []
    if len(lines) > 1:
        return _split_multiline(lines)
    line = lines[0]
    if _LIST_BULLET.match(line) and not _INLINE_BULLETS.search(line):
        return [_LIST_BULLET.sub('', line).strip()]  # one bullet: one item, commas and all
    items = [_LIST_BULLET.sub('', item).strip() for item in re.split(r'[;,]+', line)]
    return [item for item in items if item]


_SENTENCE_END = re.compile(r'[.!?;:]["\')\]]*$')
#: A wrapped line is at least this long; a shorter line that ends without punctuation stands alone.
_WRAP_WIDTH = 60


def _continues(previous: str, line: str) -> bool:
    """Whether a non-bullet `line` after a bullet is that bullet's wrapped continuation: indented, or
    starting in lower case after a bullet that did not end its sentence. Anything else stands alone."""
    if line[:1].isspace():
        return True
    return line.lstrip()[:1].islower() and not _SENTENCE_END.search(previous.rstrip())


def _split_multiline(lines: list) -> list:
    """Items of a multi-line list value (6.2.39):

    - **With bullets:** each bullet is an item. A non-bullet line after a bullet joins it when it is a
      wrapped continuation (indented, or starting in lower case); otherwise -- a closing sentence, say
      -- it is its own item. Lines before the first bullet (an intro) are their own items.
    - **Without bullets:** clearly wrapped prose -- every line but the last is at least 60 characters
      long and does not end a sentence (. ! ? ; :) -- is one item, its lines joined with spaces. Otherwise
      each line is an item (a line list): a short line, even in lower case ("crm", "erp", "data
      quality"), stands alone.
    Commas are never split inside a multi-line value."""
    if not any(_LIST_BULLET.match(line) for line in lines):
        if all(not _SENTENCE_END.search(a.rstrip()) and len(a.rstrip()) >= _WRAP_WIDTH for a in lines[:-1]):
            return [" ".join(line.strip() for line in lines)]
        return [line.strip() for line in lines if line.strip()]
    items: list = []
    in_bullet = False
    for line in lines:
        if _LIST_BULLET.match(line):
            items.append(_LIST_BULLET.sub('', line).strip())
            in_bullet = True
        elif in_bullet and _continues(items[-1], line):
            items[-1] = f"{items[-1]} {line.strip()}"
        else:
            items.append(line.strip())
            in_bullet = False
    return [item for item in items if item]


def str_to_bool(value: str) -> bool:
    """Converts a string to a boolean value."""
    return value.lower() in ("yes", "true", "t", "1")


def normalize_value(value: str | int | None) -> str:
    """Normalize a string for case-insensitive and format-flexible comparison.
       Strips whitespace, converts to upper case, replaces underscores/dashes with spaces,
       and collapses multiple spaces.
    """
    if value is None:
        return ""
    # Replace separators with spaces, then collapse multiple spaces and strip
    s = str(value).upper().replace('_', ' ').replace('-', ' ')
    return ' '.join(s.split())

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


def set_attribute_log_level(level: str) -> None:
    """Sets the verbosity for per-attribute messages."""
    global ATTRIBUTE_LOG_LEVEL
    normalized = (level or "").strip().lower()
    if normalized not in {"debug", "info", "none"}:
        raise ValueError(f"Invalid attribute log level: {level}")
    ATTRIBUTE_LOG_LEVEL = normalized


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
        return

    if ATTRIBUTE_LOG_LEVEL == "none":
        return

    formatted = f"{message_types.get(msg_level, '')}{msg}"
    if msg_level.startswith("DEBUG"):
        logger.debug(formatted)
        return

    if ATTRIBUTE_LOG_LEVEL == "debug":
        logger.debug(formatted)
        return

    if msg_level == "ERROR":
        logger.error(formatted)
    elif msg_level == "WARNING":
        logger.warning(formatted)
    elif msg_level == "DEBUG":
        logger.debug(formatted)
    else:
        logger.info(formatted)

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
    provenance = f"\n\n\n## Provenance:\n \n- Derived from processing file {file_name} on {now}\n"
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
        "endsWith": attributes.get('End With', {}).get('value', False),
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
    # RelationshipProperties is polymorphic: a raw dictionary (no "class") is a 400 that loses the whole
    # create. Typed by the parent relationship type; keys it doesn't read are reported, not sent.
    parent_props, notes = parent_relationship_properties(attributes)
    record_not_applied(attributes, "Parent Relationship Attributes"
                       if attributes.get("Parent Relationship Attributes", {}).get("value")
                       else "Parent Relationship Properties", notes)
    body = {
        "class": "NewElementRequestBody",
        "externalSourceGUID": attributes.get('External Source GUID', {}).get('guid', None),
        "externalSourceName": attributes.get('External Source Name', {}).get('value', None),
        "effectiveTime": attributes.get('Effective Time', {}).get('value', None),
        "forLineage": attributes.get('For Lineage', {}).get('value', False),
        "forDuplicateProcessing": attributes.get('For Duplicate Processing', {}).get('value', False),
        "anchorGUID": attributes.get('Anchor ID', {}).get('guid', None),
        "isOwnAnchor": attributes.get('Is Own Anchor', {}).get('value', True),
        "parentGUID": attributes.get('Parent ID', {}).get('guid', None),
        "parentRelationshipTypeName": attributes.get('Parent Relationship Type Name', {}).get('value', None) or attributes.get('Parent Relationship Type', {}).get('value', None),
        "parentRelationshipProperties": parent_props,
        "parentAtEnd1": attributes.get('Parent at End1', {}).get('value', True),
        # Egeria reads a list, anchorScopeGUIDs; the singular key was dropped (ISSUE-164)
        "anchorScopeGUIDs": ([attributes['Anchor Scope ID']['guid']]
                             if attributes.get('Anchor Scope ID', {}).get('guid') else None),
        "properties": "",
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
      "effectiveTime": attributes.get('Effective Time', {}).get('value', None),
      "forLineage": attributes.get('For Lineage', {}).get('value', False),
      "forDuplicateProcessing": attributes.get('For Duplicate Processing', {}).get('value', False),
              "mergeUpdate": attributes.get('Merge Update', {}).get('value', True),
      "properties": "",
    }
def set_rel_prop_body(object_type: str, attributes: dict)->dict:
    prop_name = object_type.replace(" ", "")
    display_name = attributes.get('Display Name', {}).get('value', None)

    body = {
        "class": prop_name + "Properties",
        "description": attributes.get('Description', {}).get('value', None),
        "label": attributes.get('Label', {}).get('value', None) or attributes.get('Link Label', {}).get('value', None),
        "typeName" : attributes.get('Type Name', {}).get('value') or prop_name,
        "effectiveFrom": attributes.get('Effective From', {}).get('value', None),
        "effectiveTo": attributes.get('Effective To', {}).get('value', None),
        "extendedProperties": attributes.get('Extended Properties', {}).get('value', None),
        }

    # Type-specific relationship properties -- set_rel_prop_body is otherwise
    # fully generic, so a type declaring its own compact-spec attributes
    # (beyond the shared Description/Label/Effective From/To pool) needs an
    # explicit branch here, same pattern as update_gov_body_for_type/
    # set_collection_manager_body for element bodies. Each of these was
    # found silently dropped (declared in the compact spec, never read
    # anywhere) via scripts/dr_egeria_attribute_consumption_audit.py.
    if prop_name == "NotificationSubscriber":
        # An empty Zone Membership sets no zones (None), not an empty list.
        body["zoneMembership"] = attributes.get('Zone Membership', {}).get('value') or None
        body["lastNotification"] = attributes.get('Last Notification', {}).get('value')
        body["activityStatus"] = attributes.get('Activity Status', {}).get('value')
    elif prop_name == "AssignmentScope":
        body["assignmentType"] = attributes.get('Assignment Type', {}).get('value')
    elif prop_name in {"PersonRoleAppointment", "TeamRoleAppointment"}:
        body["expectedTimeAllocationPercent"] = attributes.get('Expected Time Allocation Percent', {}).get('value')

    return body


def _to_egeria_type_name(object_type: str) -> str:
    """Normalize human-readable object labels into canonical Egeria type names."""
    aliases = {
        "Terms & Conditions": "TermsAndConditions",
        "Terms and Conditions": "TermsAndConditions",
        "T&C": "TermsAndConditions",
    }
    if object_type in aliases:
        return aliases[object_type]

    tokens = re.findall(r"[A-Za-z0-9]+", object_type or "")
    if not tokens:
        return (object_type or "").replace(" ", "")
    if len(tokens) == 1:
        return tokens[0]
    return "".join(token[:1].upper() + token[1:] for token in tokens)

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
    prop_name = _to_egeria_type_name(object_type)
    display_name = attributes.get('Display Name', {}).get('value', None)

    body = {
        "class": prop_name + "Properties",
        "typeName": prop_name,
        "displayName": attributes.get('Display Name', {}).get('value', None),
        "qualifiedName" : qualified_name,
        "description": attributes.get('Description', {}).get('value', None),
        "category": attributes.get('Category', {}).get('value', None),
        "identifier": attributes.get('Identifier', {}).get('value', None),
        "url": attributes.get('URL', {}).get('value', None),
        "authors": attributes.get('Authors', {}).get('value', []),
        "userDefinedContentStatus": attributes.get('User Defined Content Status', {}).get('value', None),
        "versionIdentifier": attributes.get('Version Identifier', {}).get('value', None),
        "effectiveFrom": attributes.get('Effective From', {}).get('value', None),
        "effectiveTo": attributes.get('Effective To', {}).get('value', None),
        "additionalProperties": attributes.get('Additional Properties', {}).get('value', None),
        "extendedProperties": attributes.get('Extended Properties', {}).get('value', None),
        "supportLevel": attributes.get('Support Level', {}).get('value', None),
        "serviceLevels": attributes.get('Service Levels', {}).get('value', None),
        "legal": attributes.get('Legal', {}).get('value', None),
        }
    # contentStatus / activityStatus / deploymentStatus, whichever this type has (ISSUE-113).
    body.update(element_status_properties(body["class"], attributes))
    # The rest of the bundle the type declares (namespacePath, source, resourceName, ... for assets); a given
    # bundle attribute the type has no property for is reported (F-B group 5).
    return complete_bundle_properties(body, attributes)

#: The Referenceable / Authored / Asset bundle attributes and the Egeria property each fills.
BUNDLE_PROPERTIES = {
    "Description": "description", "Category": "category", "Identifier": "identifier", "URL": "url",
    "Legal": "legal", "Version Identifier": "versionIdentifier", "Authors": "authors",
    "User Defined Content Status": "userDefinedContentStatus", "Effective From": "effectiveFrom",
    "Effective To": "effectiveTo", "Additional Properties": "additionalProperties",
    "Namespace Path": "namespacePath", "Source": "source", "Resource Name": "resourceName",
    "Deployed Implementation Type": "deployedImplementationType",
}


#: Attributes several types share under the same key but with other meanings elsewhere (e.g. Project Scope):
#: filled when the type declares the key, never reported when it doesn't.
BUNDLE_OPTIONAL = {
    "Scope": "scope", "Usage": "usage", "Purpose": "purpose",
    # one-offs a processor left out (F-B group 6), under the key Egeria's class declares
    "Headcount": "headCount", "Disposition": "disposition", "Implementation Description": "implementationDescription",
    "Product Name": "productName", "Maturity": "maturity", "Service Life": "serviceLife",
    "Introduction Date": "introductionDate", "Withdrawal Date": "withdrawDate", "Next Version Date": "nextVersionDate",
    "Member Ordinal": "ordinal",
}

#: One-off attributes with no property on most of the types that offer them: filled where the class declares
#: the key, reported where it doesn't (F-B group 6).
ONE_OFF_REPORTED = {
    "Current Version": "currentVersion", "Coverage Category": "coverageCategory",
    "Minimum Cardinality": "minCardinality", "Maximum Cardinality": "maxCardinality", "Position": "position",
    "Is Default Member": "isDefaultMember", "Default Member": "defaultMember",
}

#: Keys some processors send under a name the Java class doesn't declare, and the name it does.
KEY_RENAMES = {"withdrawalDate": "withdrawDate", "nextVersion": "nextVersionDate", "headcount": "headCount"}


def complete_bundle_properties(props: dict, attributes: dict) -> dict:
    """Fill in the bundle attributes a processor that builds its own properties left out (F-B group 5).

    For each BUNDLE_PROPERTIES attribute the document gives and `props` doesn't already set: sent when the
    properties class (properties_class_fields, from Egeria's Java) declares the key, otherwise reported as
    "not applied: <attribute>: <class> has no <key> property". The type's status field is filled the same
    way (element_status_properties). Values a processor set itself always win.
    """
    from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS
    cls = props.get("class") or ""
    fields = (PROPERTIES_CLASS_FIELDS.get(cls) or ("", None))[1]
    for attribute, key in BUNDLE_PROPERTIES.items():
        value = (attributes.get(attribute) or {}).get("value")
        if fields is not None and key not in fields:
            # Egeria ignores a key its class doesn't declare: don't send it, and say so if it was given
            if props.pop(key, None) not in (None, "", [], {}) or value not in (None, "", [], {}):
                record_not_applied(attributes, attribute, [f"not applied: {attribute}: {cls} has no {key} property"])
            continue
        if value in (None, "", [], {}) or props.get(key) not in (None, "", [], {}):
            continue
        props[key] = value
    if fields is not None:
        for wrong, right in KEY_RENAMES.items():
            if wrong in props and wrong not in fields and right in fields:
                value = props.pop(wrong)
                if props.get(right) in (None, "", [], {}):
                    props[right] = value
    for attribute, key in ONE_OFF_REPORTED.items():
        value = (attributes.get(attribute) or {}).get("value")
        if value in (None, "", [], {}) or props.get(key) not in (None, "", [], {}):
            continue
        if fields is not None and key not in fields:
            record_not_applied(attributes, attribute, [f"not applied: {attribute}: {cls} has no {key} property"])
        else:
            props[key] = value
    for attribute, key in BUNDLE_OPTIONAL.items():  # filled where the type declares them; never reported
        value = (attributes.get(attribute) or {}).get("value")
        if fields is not None and key in fields and value not in (None, "", [], {}) \
                and props.get(key) in (None, "", [], {}):
            props[key] = value
    for key, value in element_status_properties(cls, attributes).items():
        if props.get(key) in (None, ""):
            props[key] = value
    report_status_not_applied(cls, attributes)
    return props


def person_action_extras(attributes: dict, properties_class: str) -> dict:
    """The properties a my-profile create (To-Do, Meeting, Review) doesn't take as arguments: effective dates.
    Objective is reported where the type has none (only MeetingProperties does). F-B group 5/6."""
    from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS
    fields = (PROPERTIES_CLASS_FIELDS.get(properties_class) or ("", ()))[1]
    if (attributes.get("Objective") or {}).get("value") not in (None, "") and "objective" not in fields:
        record_not_applied(attributes, "Objective", [f"not applied: Objective: {properties_class} has no objective property"])
    return {"effectiveFrom": (attributes.get("Effective From") or {}).get("value"),
            "effectiveTo": (attributes.get("Effective To") or {}).get("value")}


def report_status_not_applied(properties_class: str, attributes: dict) -> None:
    """A written status attribute the type has no field for is reported, not just logged (F-B group 6):
    Content/Activity/Deployment Status by its own field, the generic Status when the type has none at all.
    The header element status can't be set on create."""
    from md_processing.md_processing_utils.element_status import EXPLICIT_STATUS_ATTRIBUTES
    from md_processing.md_processing_utils.element_status_fields import STATUS_FIELDS_BY_PROPERTIES_CLASS
    if properties_class not in STATUS_FIELDS_BY_PROPERTIES_CLASS:
        return
    supported = STATUS_FIELDS_BY_PROPERTIES_CLASS[properties_class]
    for attribute, field in EXPLICIT_STATUS_ATTRIBUTES.items():
        entry = attributes.get(attribute) or {}
        if entry.get("value") not in (None, "") and not entry.get("is_default") and field not in supported:
            record_not_applied(attributes, attribute,
                               [f"not applied: {attribute}: {properties_class} has no {field} property"])
    entry = attributes.get("Status") or {}
    if entry.get("value") not in (None, "") and not entry.get("is_default") and not supported:
        record_not_applied(attributes, "Status", [f"not applied: Status: {properties_class} has no status property"])


def report_spec_microflow(attributes: dict) -> str | None:
    """The Report Spec's `Microflow` attribute as canonical microflow/1 text, or None if not given.

    A bare JSON list (legacy format 0) is converted with `microflow_from_legacy`, the same function
    the report-spec sync uses; a microflow/1 object is validated. Raises ValueError with words for
    invalid JSON or an invalid micro-flow (RS-EGERIA-TIER, report-spec pipeline model §7a)."""
    from pyegeria.view.microflow import MicroflowError, normalize_microflow_text
    value = attributes.get('Microflow', {}).get('value', None)
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    try:
        return normalize_microflow_text(value)
    except MicroflowError as exc:
        raise ValueError(f"Microflow: {exc}") from exc


def set_collection_manager_body(object_type: str, qualified_name: str, attributes: dict) -> dict:
    """
    Build the INNER element-specific Properties body for Collection Manager elements.
    Handles subtypes like Digital Product, Agreement, Digital Subscription, etc.
    """
    prop_bod = set_element_prop_body(object_type, qualified_name, attributes)
    prop_bod["purpose"] = attributes.get('Purpose', {}).get('value', None)

    # Handle Digital Product and Digital Product Family
    if "Digital Product" in object_type:
        prop_bod.update({
            "productName": attributes.get('Product Name', {}).get('value', None),
            "maturity": attributes.get('Maturity', {}).get('value', None),
            "currentVersion": attributes.get('Current Version', {}).get('value', None),
            "serviceLife": attributes.get('Service Life', {}).get('value', None),
            "introductionDate": attributes.get('Introduction Date', {}).get('value', None),
            "withdrawalDate": attributes.get('Withdrawal Date', {}).get('value', None),
            "nextVersionDate": attributes.get('Next Version Date', {}).get('value', None),
        })

    # Agreement: AgreementProperties declares no fields of its own (ISSUE-145).
    # Digital Subscription's supportLevel/serviceLevels are set by set_element_prop_body().

    # Handle Glossary
    if "Glossary" in object_type:
        prop_bod.update({
            "language": attributes.get('Language', {}).get('value', "English"),
            "usage": attributes.get('Usage', {}).get('value', None),
        })

    # Handle Report Type (a DataSpec subtype, 0580)
    if object_type in ["Report Type", "ReportType"]:
        prop_bod.update({
            "createdTime": attributes.get('Created Time', {}).get('value', None),
            "lastModifiedTime": attributes.get('Last Modified Time', {}).get('value', None),
            "lastModifier": attributes.get('Last Modifier', {}).get('value', None),
        })

    # Handle Report Spec (a ReportType subtype, Egeria 6.3 / odpi/egeria#9432)
    if object_type in ["Report Spec", "ReportSpec"]:
        prop_bod.update({
            # RS-EGERIA-TIER: always stored as microflow/1 (a bare list is converted, an object
            # validated); invalid JSON raises with words instead of passing through verbatim.
            "microflow": report_spec_microflow(attributes),
            "targetTypeName": attributes.get('Target Type Name', {}).get('value', None),
            "aliases": attributes.get('Aliases', {}).get('value', None),
            "outputTypes": attributes.get('Output Types', {}).get('value', None),
            "includePreamble": attributes.get('Include Preamble', {}).get('value', None),
        })

    # Handle Security subtypes
    if object_type in ["Security Group", "Security List", "Security Role", "SecurityGroup", "SecurityList", "SecurityRole"]:
        prop_bod['distinguishedName'] = attributes.get('Distinguished Name', {}).get('value', None)

    # Handle Working Set
    if "Working Set" in object_type:
        prop_bod['disposition'] = attributes.get('Disposition', {}).get('value', None)

    # Handle Business Capability (0715 Digital Business)
    if object_type in ["Business Capability", "BusinessCapability"]:
        prop_bod.update({
            "businessCapabilityType": attributes.get('Business Capability Type', {}).get('value', None),
            "businessImplementationType": attributes.get('Business Implementation Type', {}).get('value', None),
        })

    return complete_bundle_properties(prop_bod, attributes)  # keys added after the common builder (F-B 6)


def set_actor_manager_prop_body(object_type: str, qualified_name: str, attributes: dict) -> dict:
    """
    Build the INNER element-specific Properties body for Actor Manager elements.
    """
    prop_bod = set_element_prop_body(object_type, qualified_name, attributes)

    # Handle Person
    if "Person" in object_type and "Role" not in object_type:
        prop_bod.update({
            "courtesyTitle": attributes.get('Courtesy Title', {}).get('value', None),
            "employeeNumber": attributes.get('Employee Number', {}).get('value', None),
            "employeeType": attributes.get('Employee Type', {}).get('value', None),
            "fullName": attributes.get('Full Name', {}).get('value', None),
            "givenNames": attributes.get('Given Names', {}).get('value', None),
            "initials": attributes.get('Initials', {}).get('value', None),
            "jobTitle": attributes.get('Job Title', {}).get('value', None),
            "preferredLanguage": attributes.get('Preferred Language', {}).get('value', None),
            "pronouns": attributes.get('Pronouns', {}).get('value', None),
            "residentCountry": attributes.get('Resident Country', {}).get('value', None),
            "surname": attributes.get('Surname', {}).get('value', None),
            "timeZone": attributes.get('Time Zone', {}).get('value', None),
        })

    # Handle Team and Organization
    if "Team" in object_type or "Organization" in object_type:
        if "Role" not in object_type:
            prop_bod["teamType"] = attributes.get('Team Type', {}).get('value', None)

    # Handle Actor Roles
    if "Role" in object_type:
        prop_bod["scope"] = attributes.get('Scope', {}).get('value', None)
        if "Person Role" in object_type or "Team Role" in object_type:
            # headCount is an integer; left unset when not given, so an update keeps the stored value
            headcount = attributes.get('Headcount', {}).get('value')
            try:
                prop_bod["headCount"] = int(headcount) if headcount not in (None, "") else None
            except (ValueError, TypeError):
                prop_bod["headCount"] = None

    return complete_bundle_properties(prop_bod, attributes)  # keys added after the common builder (F-B 6)


def set_solution_architect_body(object_type: str, qualified_name: str, attributes: dict) -> dict:
    """
    Build the INNER element-specific Properties body for Solution Architect elements.
    Adds DesignPattern-specific fields on top of set_element_prop_body.
    """
    prop_bod = set_element_prop_body(object_type, qualified_name, attributes)

    if object_type == "DesignPattern":
        prop_bod.update({
            "context": attributes.get('Context', {}).get('value', None),
            "problemStatement": attributes.get('Problem Statement', {}).get('value', None),
            "problemExample": attributes.get('Problem Example', {}).get('value', None),
            "solutionDescription": attributes.get('Solution Description', {}).get('value', None),
            "solutionExample": attributes.get('Solution Example', {}).get('value', None),
            "forces": attributes.get('Forces', {}).get('value', None),
            "benefits": attributes.get('Benefits', {}).get('value', None),
            "liabilities": attributes.get('Liabilities', {}).get('value', None),
            # ISSUE-66: usage is a real DesignPatternProperties field (confirmed in
            # Egeria-api-solution-architect.http's createDesignPattern/updateDesignPattern
            # worked examples) that the "Design Pattern Base" bundle never declared, so it
            # could never be set at all -- not even silently dropped, since --validate
            # would reject an undeclared "### Usage" attribute outright.
            "usage": attributes.get('Usage', {}).get('value', None),
        })

    if object_type in ("Solution Role", "SolutionRole", "SolutionActorRole"):
        # SolutionActorRoleProperties (odpi/egeria origin/main 0b7ee0fb) has scope and actorRoleGroups but no
        # domainIdentifier or title: those were sent and silently ignored (round-trip probe).
        for attribute, key in (("Role Domain Identifier", "domainIdentifier"), ("Title", "title")):
            if attributes.get(attribute, {}).get('value') not in (None, ""):
                record_not_applied(attributes, attribute,
                                   [f"not applied: {attribute}: SolutionActorRoleProperties has no {key} property"])

    return complete_bundle_properties(prop_bod, attributes)  # keys added after the common builder (F-B 6)


def set_product_body(object_type: str, qualified_name: str, attributes: dict) -> dict:
    prop_bod = set_element_prop_body(object_type, qualified_name, attributes)
    prop_bod["identifier"] = attributes.get('Identifier', {}).get('value', None)
    prop_bod["productName"] = attributes.get('Product Name', {}).get('value', None)
    prop_bod["maturity"] = attributes.get('Maturity', {}).get('value', None)
    prop_bod["serviceLife"] = attributes.get('Service Life', {}).get('value', None)
    prop_bod["introductionDate"] = attributes.get('Introduction Date', {}).get('value', [])
    prop_bod["withdrawalDate"] = attributes.get('Withdrawal Date', {}).get('value', [])
    prop_bod["nextVersion"] = attributes.get('Next Version Date', {}).get('value', [])
    return complete_bundle_properties(prop_bod, attributes)  # keys added after the common builder (F-B 6)

def set_data_field_body(object_type: str, qualified_name: str, attributes: dict)->dict:
    prop_bod = set_element_prop_body(object_type, qualified_name, attributes)
    prop_bod["namespacePath"] = attributes.get('Namespace Path', {}).get('value', None)
    prop_bod["aliases"] = attributes.get('Aliases', {}).get('value', [])
    prop_bod["namePatterns"] = attributes.get('Name Patterns', {}).get('value', [])
    prop_bod["defaultValue"] = attributes.get('Default Value', {}).get('value', None)
    prop_bod["isNullable"] = attributes.get('Is Nullable', {}).get('value', None)
    prop_bod["allowsDuplicateValues"] = attributes.get('Allow Duplicate Values', {}).get('value', None)
    prop_bod["dataType"] = attributes.get('Data Type', {}).get('value', None)
    prop_bod["units"] = attributes.get('Units', {}).get('value', None)
    prop_bod["minimumLength"] = attributes.get('Minimum Length', {}).get('value', None)
    prop_bod["length"] = attributes.get('Length', {}).get('value', None)
    prop_bod["precision"] = attributes.get('Precision', {}).get('value', None)
    prop_bod["orderedValues"] = attributes.get('Ordered Values', {}).get('value', None)
    prop_bod["sortOrder"] = attributes.get('Sort Order', {}).get('value', None)
    prop_bod["isPartitionKey"] = attributes.get('Is Partition Key', {}).get('value', None)
    prop_bod["partitionKeyPosition"] = attributes.get('Partition Key Position', {}).get('value', None)
    return complete_bundle_properties(prop_bod, attributes)  # keys added after the common builder (F-B 6)

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
    domain_id = attributes.get('Domain Identifier', {}).get('value', 0)
    resolved_domain = resolve_enum(GovernanceDomains, domain_id)
    if resolved_domain is not None:
        prop_bod["domainIdentifier"] = resolved_domain
    else:
        prop_bod["domainIdentifier"] = domain_id
    prop_bod["displayName"]= attributes.get('Display Name', {}).get('value', None)
    prop_bod['qualifiedName'] = qualified_name
    prop_bod["versionIdentifier"] = attributes.get('Version Identifier', {}).get('value', None)
    prop_bod["summary"] = attributes.get('Summary', {}).get('value', None)
    prop_bod["description"] = attributes.get('Description', {}).get('value', None)

    prop_bod["scope"] = attributes.get('Scope', {}).get('value', None)
    prop_bod["importance"] = attributes.get('Importance', {}).get('value', None)
    prop_bod["implications"] = attributes.get('Implications', {}).get('value', [])
    prop_bod["outcomes"] = attributes.get('Outcomes', {}).get('value', [])
    prop_bod["results"] = attributes.get('Results', {}).get('value', []) or []
    # ISSUE-157: Egeria types these as Map<String, String> (TermsAndConditionsProperties and its
    # subtypes, e.g. ServiceLevelObjectiveProperties); a [] default made the server refuse the body.
    prop_bod["entitlements"] = attributes.get('Entitlements', {}).get('value', None)
    prop_bod["obligations"] = attributes.get('Obligations', {}).get('value', None)
    prop_bod["restrictions"] = attributes.get('Restrictions', {}).get('value', None)
    prop_bod["usage"] = attributes.get('Usage', {}).get('value', None)
    prop_bod["effectiveFrom"] = attributes.get('Effective From', {}).get('value', None)
    prop_bod["effectiveTo"] = attributes.get('Effective To', {}).get('value', None)
    prop_bod["additionalProperties"] = attributes.get('Additional Properties', {}).get('value', None)
    prop_bod["extendedProperties"] = attributes.get('Extended Properties', {}).get('value', None)


    body = update_gov_body_for_type(object_type, prop_bod, attributes)
    return complete_bundle_properties(body, attributes)  # keys added after the common builder (F-B 6)
    

def update_gov_body_for_type(object_type: str, body: dict, attributes: dict) -> dict:
    # Callers pass either the spaced display name (e.g. "Certification Type") or the
    # no-space OM_TYPE (e.g. "CertificationType", which is what GovernanceProcessor
    # actually uses for every governance-officer command). Normalize once and compare
    # every branch against the no-space form so both callers match consistently.
    gov_def_name = object_type.replace(" ", "")
    general_defs = {t.replace(" ", "") for t in GENERAL_GOVERNANCE_DEFINITIONS}
    controls = {t.replace(" ", "") for t in GOVERNANCE_CONTROLS}

    if gov_def_name in general_defs:
        return body
    elif gov_def_name == "GovernanceStrategy":
        body['businessImperatives'] = attributes.get('Business Imperatives', {}).get('value', [])
        return body

    elif gov_def_name == "Regulation":
        body['regulationSource'] = attributes.get('Regulation Source', {}).get('value', None)
        body['regulators'] = attributes.get('Regulators', {}).get('value', [])
        return body

    elif gov_def_name == "GovernanceMetric":
        # Inherits Implementation Description from the Governance Control Base bundle,
        # plus its own Measurement/Target attributes.
        body['implementationDescription'] = attributes.get('Implementation Description', {}).get('value', None)
        body['measurement'] = attributes.get('Measurement', {}).get('value', None)
        body['target'] = attributes.get('Target', {}).get('value', None)
        return body
    elif gov_def_name in controls:
        body['implementationDescription'] = attributes.get('Implementation Description', {}).get('value', None)
        return body
    elif gov_def_name == "SecurityGroup":
        # Some servers model SecurityGroup with a narrower property set than other governance definitions.
        for field in [
            "domainIdentifier",
            "summary",
            "scope",
            "importance",
            "implications",
            "outcomes",
            "results",
            "usage",
        ]:
            body.pop(field, None)
        body['distinguishedName'] = attributes.get('Distinguished Name', {}).get('value', None)
        return body
    elif gov_def_name == "NamingStandardRule":
        body['namePatterns'] = attributes.get('Name Patterns', {}).get('value', [])
        return body
    elif gov_def_name == "GovernanceZone":
        body['criteria'] = attributes.get('Criteria', {}).get('value', None)
        return body
    elif gov_def_name == "NotificationType":
        body['plannedCompletionDate'] = attributes.get('Planned Completion Date', {}).get('value', None)
        body['multipleNotificationsPermitted'] = attributes.get('Multiple Notifications Permitted', {}).get('value', None)
        # nextScheduledNotification is informational only (maintained by the notification manager), so it is
        # never sent. notificationInterval was removed in Egeria 6.3 (deprecated in 6.2, ignored if sent):
        # minimumNotificationInterval (minutes) is the period for a type with no monitored resources and a
        # throttle for one with monitored resources.
        body['notificationCount'] = attributes.get('Notification Count', {}).get('value', None)
        body['minimumNotificationInterval'] = attributes.get('Minimum Notification Interval', {}).get('value', None)
        body['plannedStartDate'] = attributes.get('Planned Start Date', {}).get('value', None)
        return body
    elif gov_def_name in {"TermsAndConditions", "Terms&Conditions", "CertificationType", "LicenseType"}:
        entitlements = attributes.get('Entitlements', {}).get('value', {}) if attributes.get('Entitlements',None) else None
        restrictions = attributes.get('Restrictions', {}).get('value', {}) if attributes.get('Restrictions',None) else None
        obligations = attributes.get('Obligations', {}).get('value', {}) if attributes.get('Obligations',None) else None
        body['entitlements'] = entitlements
        body['restrictions'] = restrictions
        body['obligations'] = obligations

        return body

    elif gov_def_name in {"GovernanceActionType", "GovernanceActionProcessStep"}:
        # ISSUE-71: neither type had a branch here, so every attribute added by
        # their compact-spec bundles -- Implementation Description (inherited
        # from Governance Control Base), Produced Guards and Wait Time
        # (Governance Action Type Base), and Ignore Multiple Triggers
        # (Governance Action Process Step Base, GovernanceActionProcessStep
        # only) -- was silently dropped: they fell through to the generic
        # "no dedicated mapping" fallback below, which only preserves base
        # Referenceable/GovernanceDefinition fields.
        body['implementationDescription'] = attributes.get('Implementation Description', {}).get('value', None)
        body['producedGuards'] = attributes.get('Produced Guards', {}).get('value', [])
        body['waitTime'] = attributes.get('Wait Time', {}).get('value', None)
        if gov_def_name == "GovernanceActionProcessStep":
            body['ignoreMultipleTriggers'] = attributes.get('Ignore Multiple Triggers', {}).get('value', None)
        return body

    elif gov_def_name == "DataLens":
        # ISSUE-99 follow-up: DataLens had no branch here either, so all 9 of
        # its compact-spec attributes fell through to the generic fallback
        # below -- same shape as the GovernanceActionType/ProcessStep gap
        # above (ISSUE-71).
        body['dataCollectionStartTime'] = attributes.get('Data Collection Start Time', {}).get('value', None)
        body['dataCollectionEndTime'] = attributes.get('Data Collection End Time', {}).get('value', None)
        body['minLongitude'] = attributes.get('Min Longitude', {}).get('value', None)
        body['maxLongitude'] = attributes.get('Max Longitude', {}).get('value', None)
        body['minLatitude'] = attributes.get('Min Latitude', {}).get('value', None)
        body['maxLatitude'] = attributes.get('Max Latitude', {}).get('value', None)
        body['minHeight'] = attributes.get('Min Height', {}).get('value', None)
        body['maxHeight'] = attributes.get('Max Height', {}).get('value', None)
        body['scopeElements'] = attributes.get('Scope Elements', {}).get('value', None)
        return body

    # Preserve base governance fields for subtypes without dedicated custom mappings.
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
      # ISSUE-77: "Make Anchor"/"Anchor Scope IDs" live on the "Link Command
      # Base" bundle (relationship-establishing commands) but were parsed and
      # validated without ever being sent -- confirmed against
      # Egeria-api-lineage-linker.http (NewRelationshipRequestBody sample
      # body): both are real top-level fields here, not on the create-element
      # body (that's the separate, already-wired singular "Anchor Scope ID").
      "makeAnchor": attributes.get('Make Anchor', {}).get('value', None),
      "anchorScopeGUIDs": attributes.get('Anchor Scope IDs', {}).get('guid_list', None),
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

def set_delete_rel_request_body(object_type: str, attributes: dict)->dict:
    return {
        "class": "DeleteRelationshipRequestBody",
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

def add_search_keywords(client: ServerClient, element_guid: str, keywords: list[str]):
    """Add a search keyword to an element. Throw an exception if a problem is encountered.

    Args:
        client (ServerClient): The Egeria client instance.
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

def add_note_in_dr_e(client: ServerClient, qualified_name: str, display_name: str, journal_entry: str)-> str:
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

async def async_add_note_in_dr_e(client: ServerClient, qualified_name: str, display_name: str, journal_entry: str) -> str:
    if journal_entry:
        note_log_qn = f"{qualified_name}-NoteLog"
        note_log_display_name = f"{display_name}-NoteLog"
        note_display_name = f"{qualified_name}-Journal-Entry-{datetime.now().strftime('%Y-%m-%d %H:%M')}"
        journal_entry_guid = await client._async_add_journal_entry(note_log_qn, qualified_name, note_log_display_name,
                                                                 note_display_name, journal_entry)
        logger.info(f"Added journal entry `{journal_entry_guid}` to `{qualified_name}`")
        return journal_entry_guid
    else:
        return None
