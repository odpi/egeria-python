"""
This file contains display-related constants and formatting functions for Egeria Markdown processing
"""
import importlib.resources
import json
import os

import inflect
from loguru import logger
from rich.markdown import Markdown

from pyegeria.core._globals import DEBUG_LEVEL
from pyegeria.core.logging_configuration import config_logging

inflect_engine = inflect.engine()

EGERIA_ROOT_PATH = os.environ.get("EGERIA_ROOT_PATH", "/home/jovyan")
EGERIA_INBOX_PATH = os.environ.get("EGERIA_INBOX_PATH", "loading-bay/dr_egeria_inbox")

# Constants for compact resource loading
USE_COMPACT_RESOURCES = True
COMPACT_RESOURCE_DIR = str(importlib.resources.files("md_processing") / "data" / "compact_commands")
COMPACT_FAMILIES = []  # Empty list means all families are loaded

# Constants for element labels
GLOSSARY_NAME_LABELS = ["Glossary Name", "Glossary", "Glossaries", "Owning Glossary", "In Glossary"]

TERM_NAME_LABELS = ["Glossary Term Name", "Glossary Term", "Glossary Terms", "Term Name", "Term", "Terms", "Term Names"]
PROJECT_NAME_LABELS = ["Project Name", "Project", "Project Names", "Projects"]
BLUEPRINT_NAME_LABELS = ["Solution Blueprint Name", "Solution Blueprint", "Solution Blueprints", "Blueprint Name",
                         "Blueprint", "Blueprints"]
COMPONENT_NAME_LABELS = ["Solution Component Name", "Solution Component", "Solution Components", "Component Name",
                         "Component", "Components", "Parent Components", "Parent Component"]
SOLUTION_ROLE_LABELS = ["Solution Role Name", "Solution Role", "Solution Roles", "Role Name", "Role", "Roles"]
SOLUTION_ACTOR_ROLE_LABELS = ["Solution Actor Role Name", "Solution Actor Role Names", "Solution Actor Role",
                              "Solution Actor Roles", "Actor Role Name", "Actor Role", "Actor Roles",
                              "Actor Role Names"]
SOLUTION_LINKING_ROLE_LABELS = ["Solution Linking Role Name", "Solution Linking Role Names", "Solution Linking Role",
                                "Solution Linking Roles", "Linking Role Name", "Linking Role", "Linking Roles",
                                "Linking Role Names"]
OUTPUT_LABELS = ["Output", "Output Format"]
SEARCH_LABELS = ['Search String', 'Filter']
GUID_LABELS = ['GUID', 'guid']

# Constants for output formats
ELEMENT_OUTPUT_FORMATS = ["LIST", "DICT", "MD", "FORM", "REPORT"]

# Constants for term relationships
TERM_RELATIONSHPS = ["Synonym", "Translation", "PreferredTerm", "TermISATYPEOFRelationship", "TermTYPEDBYRelationship",
                     "Antonym", "ReplacementTerm", "ValidValue", "TermHASARelationship", "RelatedTerm",
                     "ISARelationship"]

# List of supported md_commands
GOV_LINK_LIST = ["Link Governance Drivers", "Link Drivers", "Detach Governance Drivers", "Detach Drivers",
                 "Link Governance Policies", "Link Policies", "Detach Governance Policies", "Detach Policies",
                 "Link Governance Controls", "Link Controls", "Detach Governance Controls", "Detach Controls",
                 ]

GOV_COM_LIST = ["Create Business Imperative", "Update Business Imperative",
                "Create Regulation Article Definition", "Update Regulation Article Definition",
                "Create Threat Definition", "Update Threat Definition",
                "Create Governance Principle", "Update Governance Principle",
                "Create Governance Obligation", "Update Governance Obligation",
                "Create Governance Approach", "Update Governance Approach",
                "Create Governance Strategy", "Update Governance Strategy",
                "Create Regulation", "Create Regulation Definition", "Update Regulation",
                "Update Regulation Definition",
                "Create Governance Control:", "Update Governance Control",
                "Create Governance Rule:", "Update Governance Rule",
                "Create Service Level Objective", "Update Service Level Objective",
                "Create Governance Process", "Update Governance Process",
                "Create Governance Responsibility", "Update Governance Responsibility",
                "Create Governance Procedure", "Update Governance Procedure",
                "Create Security Access Control", "Update Security Access Control",
                "Create Security Group", "Update Security Group",
                "Create Naming Standard Rule", "Update Naming Standard Rule",
                "Create Certification Type", "Update Certification Type",
                "Create License Type", "Update License Type",

                ]

SIMPLE_BASE_COLLECTIONS: set = {"Collection", "Home Collection", "Digital Product", "Result Set", "Recent Access",
                                "Reference List", "Work Item List", "Data Sharing Agreement", "Namespace", "Agreement",
                                "Digital Subscription", "Data Product", "Subscription",
                                "Root Collection", "Folder", "Context Event Collection", "Name Space Collection",
                                # "Data Specifications", "Data Specifications", "Data Specs", "Data Specs",
                                # "Data Dictionaries", "Data Dictionaries",
                                "Event Set Collection", "Naming Standard Ruleset", "Digital Product Catalog"
                                }
LIST_COMMANDS = {"Run Report"}

SIMPLE_COLLECTIONS: set = set()
for element in SIMPLE_BASE_COLLECTIONS:
    SIMPLE_COLLECTIONS.add(f"Create {element}")
    SIMPLE_COLLECTIONS.add(f"Update {element}")
    plural = inflect_engine.plural_noun(element)
    SIMPLE_COLLECTIONS.add(f"Create {plural}")
    SIMPLE_COLLECTIONS.add(f"Update {plural}")

COLLECTIONS_LIST = []

PROJECT_COMMANDS = ["Create Project", "Update Project", "Create Campaign", "Update Campaign",
                    "Create Task", "Update Task", "Create Study Project", "Update Study Project",
                    "Create Personal Project", "Update Personal Project"]

LINK_EXT_REF = ["Link External Reference", "Link Referenceable->External Reference", "Attach External Reference",
                "Detach External Reference", "Detach External Reference Link", "Link External Data Source",
                "Link External Model Source", "Detach External Data Source", "Detach External Model Source", ]

LINK_MEDIA = ["Link Related Media", "Link Referenceable->Related Media", "Attach Related Media",
              "Attach Media Reference Link",
              "Detach Related Media", "Detach Related Media Link", "Detach Media Reference Link"]

LINK_CITED_DOC = ["Link Cited Document", "Link Referenceable->Cited Document", "Attach Cited Document",
                  "Attach Cited Document Link",
                  "Detach Cited Document", "Detach Cited Document Link", ]

EXT_REF_UPSERT = ["Create External Reference", "Update External Reference",
                  "Create Related Media", "Update Related Media",
                  "Create Cited Document", "Update Cited Document",
                  "Create External Data Source", "Update External Data Source", "Create External Model Source",
                  "Update External Model Source", ]
EXT_REF_COMMANDS = EXT_REF_UPSERT + LINK_EXT_REF + LINK_MEDIA + LINK_CITED_DOC

COLLECTION_CREATE = ["Create Collection", "Update Collection", "Create Digital Product Catalog",
                     "Update Digital Product Catalog",
                     "Create Root Collection", "Update Root Collection", "Create Folder", "Update Folder",
                     ]
FEEDBACK_COMMANDS = ["Create Comment", "Update Comment", "Create Journal Entry",
                     "Create Informal Tag", "Update Informal Tag", "Link Tag->Element", "Link Tag", "Detach Tag"]

LINK_VERBS = ("Link", "Attach", "Add", "Detach", "Unlink", "Remove")
CREATE_VERBS = ("Create", "Update")
VIEW_VERBS = ("View", "List", "Run")
ALL_VERBS = set(LINK_VERBS + CREATE_VERBS + VIEW_VERBS)

command_list = ["Provenance"]
pre_command = "\n---\n==> Processing object_action:"
command_seperator = Markdown("\n---\n")
EXISTS_REQUIRED = "Exists Required"
COMMAND_DEFINITIONS = {}

def _normalize_command(text: str) -> str:
    return " ".join(text.split())


def _split_command(command: str) -> tuple[str, str]:
    normalized = _normalize_command(command)
    parts = normalized.split(maxsplit=1)
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def _parse_alternate_names(spec: dict) -> list[str]:
    alt = spec.get("alternate_names", "")
    if not alt:
        return []
    return [_normalize_command(item) for item in alt.split(";") if item.strip()]


def _expand_command_phrase(verb: str, noun: str, allow_update: bool) -> set[str]:
    if verb in LINK_VERBS:
        return {f"{v} {noun}".strip() for v in LINK_VERBS}
    if verb in VIEW_VERBS:
        if noun == "Report":
            return {"View Report", "Run Report"}
        return set()
    if verb in CREATE_VERBS:
        if allow_update:
            return {f"{v} {noun}".strip() for v in CREATE_VERBS}
        return {f"{verb} {noun}".strip()}
    return {f"{verb} {noun}".strip()}


def build_command_variants(spec_name: str, spec: dict) -> set[str]:
    variants = set()
    if not spec_name:
        return variants

    base_verb, base_noun = _split_command(spec_name)
    allow_update = bool(spec.get("upsert"))

    def add_phrase(phrase: str) -> None:
        verb, noun = _split_command(phrase)
        if not noun:
            return
        variants.update(_expand_command_phrase(verb, noun, allow_update))

    add_phrase(spec_name)

    for alt in _parse_alternate_names(spec):
        alt_verb, _ = _split_command(alt)
        if alt_verb in ALL_VERBS:
            add_phrase(alt)
        else:
            add_phrase(f"{base_verb} {alt}")

    return {cmd for cmd in variants if cmd}


def build_command_list_from_specs(specs: dict, include_provenance: bool = True) -> list[str]:
    commands = set()
    for name, spec in specs.items():
        if not isinstance(spec, dict):
            continue
        commands.update(build_command_variants(name, spec))
    if include_provenance:
        commands.add("Provenance")
    return sorted(commands)


def get_command_variants_for_specs(spec_names: set[str]) -> set[str]:
    specs = COMMAND_DEFINITIONS.get("Command Specifications", {})
    commands = set()
    for name in spec_names:
        spec = specs.get(name)
        if isinstance(spec, dict):
            commands.update(build_command_variants(name, spec))
    return commands

generic_bodies = {

}

config_logging()
logger.enable("pyegeria")
debug_level = DEBUG_LEVEL


# def load_commands(filename: str) -> None:
#     global COMMAND_DEFINITIONS
#
#     try:
#         config_path = importlib.resources.files("md_processing") / "data" / filename
#         config_str = config_path.read_text(encoding="utf-8")
#         COMMAND_DEFINITIONS = json.loads(config_str)
#
#     except FileNotFoundError:
#         msg = f"ERROR: File {filename} not found."
#         print(ERROR, msg, debug_level)

def load_commands(filename: str) -> None:
    global COMMAND_DEFINITIONS, command_list

    try:
        config_path = importlib.resources.files("md_processing") / "data" / filename
        config_str = config_path.read_text(encoding="utf-8")

        # Validate JSON before attempting to load
        try:
            COMMAND_DEFINITIONS = json.loads(config_str)
            base_specs = COMMAND_DEFINITIONS.get("Command Specifications", {})

            # Optionally merge compact specs from a separate directory
            if USE_COMPACT_RESOURCES:
                try:
                    from md_processing.md_processing_utils.compact_loader import load_compact_specs_from_dir

                    if os.path.isdir(COMPACT_RESOURCE_DIR):
                        overlay_specs = load_compact_specs_from_dir(
                            COMPACT_RESOURCE_DIR, COMPACT_FAMILIES if COMPACT_FAMILIES else None
                        )
                        if overlay_specs:
                            # Merge/overlay into base specs
                            merged = dict(base_specs)
                            merged.update(overlay_specs)
                            COMMAND_DEFINITIONS["Command Specifications"] = merged
                            logger.debug(
                                f"Loaded {len(overlay_specs)} compact commands from {COMPACT_RESOURCE_DIR}"
                                + (f" for families: {COMPACT_FAMILIES}" if COMPACT_FAMILIES else "")
                            )
                except Exception as merge_err:
                    logger.warning(f"Compact commands merge skipped due to error: {merge_err}")

            command_list = build_command_list_from_specs(
                COMMAND_DEFINITIONS.get("Command Specifications", {})
            )
            msg = f"Successfully loaded {filename}"
            logger.debug(msg)
        except json.JSONDecodeError as json_err:
            # Provide detailed error information
            error_line = json_err.lineno
            error_col = json_err.colno
            error_pos = json_err.pos

            # Extract context around the error
            lines = config_str.split('\n')
            start_line = max(0, error_line - 3)
            end_line = min(len(lines), error_line + 2)

            context = '\n'.join([
                f"Line {i + 1}: {lines[i]}"
                for i in range(start_line, end_line)
            ])

            error_msg = (
                f"\n{'=' * 80}\n"
                f"ERROR: Invalid JSON in {filename}\n"
                f"{'=' * 80}\n"
                f"Location: Line {error_line}, Column {error_col} (char position {error_pos})\n"
                f"Error: {json_err.msg}\n"
                f"\nContext around error:\n{context}\n"
                f"{'=' * 80}\n"
                f"\nPlease fix the JSON syntax error in {filename} at line {error_line}.\n"
                f"Common issues:\n"
                f"  - Missing comma between elements\n"
                f"  - Trailing comma before closing bracket/brace\n"
                f"  - Unescaped quotes in strings\n"
                f"  - Missing closing bracket/brace\n"
                f"{'=' * 80}\n"
            )

            print(error_msg)

            # Initialize with empty dict to allow application to continue
            # (though functionality will be limited)
            COMMAND_DEFINITIONS = {}
            command_list = ["Provenance"]

            # Re-raise with more context
            raise json.JSONDecodeError(
                f"Invalid JSON in {filename}: {json_err.msg}",
                json_err.doc,
                json_err.pos
            ) from json_err

    except FileNotFoundError:
        msg = f"ERROR: File {filename} not found."
        print(msg)
        COMMAND_DEFINITIONS = {}
        command_list = ["Provenance"]
        raise FileNotFoundError(msg)
    except Exception as e:
        msg = f"ERROR: Unexpected error loading {filename}: {str(e)}"
        print(msg)
        COMMAND_DEFINITIONS = {}
        command_list = ["Provenance"]
        raise


def validate_json_file(filename: str) -> tuple[bool, str]:
    """
    Validate a JSON file and return status with error details.

    Returns:
        tuple: (is_valid: bool, message: str)
    """
    try:
        config_path = importlib.resources.files("md_processing") / "data" / filename
        config_str = config_path.read_text(encoding="utf-8")
        json.loads(config_str)
        return True, f"JSON file {filename} is valid"
    except json.JSONDecodeError as e:
        error_msg = (
            f"Invalid JSON at line {e.lineno}, column {e.colno}: {e.msg}\n"
            f"Character position: {e.pos}"
        )
        return False, error_msg
    except Exception as e:
        return False, f"Error reading file: {str(e)}"


def find_json_errors(filename: str, max_errors: int = 10) -> list[str]:
    """
    Attempt to find multiple JSON errors in a file.

    This function tries to parse the JSON and collect error information.
    """
    errors = []
    try:
        config_path = importlib.resources.files("md_processing") / "data" / filename
        config_str = config_path.read_text(encoding="utf-8")

        # Try to parse
        json.loads(config_str)
        return ["No errors found - JSON is valid"]

    except json.JSONDecodeError as e:
        lines = config_str.split('\n')
        error_line = e.lineno - 1  # Convert to 0-indexed

        # Get context
        start = max(0, error_line - 2)
        end = min(len(lines), error_line + 3)

        error_context = []
        for i in range(start, end):
            prefix = ">>> " if i == error_line else "    "
            error_context.append(f"{prefix}Line {i + 1}: {lines[i]}")

        error_msg = (
                f"Error at line {e.lineno}, column {e.colno}: {e.msg}\n" +
                "\n".join(error_context)
        )
        errors.append(error_msg)

    except Exception as e:
        errors.append(f"Unexpected error: {str(e)}")

    return errors


def get_command_spec(command: str, body_type: str = None) -> dict | None:
    global COMMAND_DEFINITIONS

    com = COMMAND_DEFINITIONS.get('Command Specifications', {}).get(command, None)
    if com:
        return com
    else:
        obj = find_alternate_names(command)
        if obj:
            return COMMAND_DEFINITIONS.get('Command Specifications', {}).get(obj, None)


def does_command_match(command: str, alt_names: list[str]) -> bool:
    command_parts = command.split(maxsplit=1)
    if len(command_parts) < 2:
        return False
    verb, _ = command_parts

    if verb in LINK_VERBS:
        synonyms = LINK_VERBS
    elif verb in VIEW_VERBS:
        synonyms = VIEW_VERBS
    elif verb in CREATE_VERBS:
        synonyms = CREATE_VERBS
    else:
        synonyms = (verb,)

    for alt_name in alt_names:
        alt_name = alt_name.strip()
        if not alt_name:
            continue
        alt_verb, alt_terms = _split_command(alt_name)
        if alt_verb in ALL_VERBS and alt_terms:
            alt_name = alt_terms
        for synonym in synonyms:
            tst = f"{synonym} {alt_name}".strip()
            if tst == command:
                return True
    return False


def find_alternate_names(command: str) -> str | None:
    global COMMAND_DEFINITIONS

    comm_spec = COMMAND_DEFINITIONS.get('Command Specifications', {})
    for key, value in comm_spec.items():
        if isinstance(value, dict):
            v = value.get('alternate_names', "")
            v = [item.strip() for item in v.split(';') if item.strip()] if v else []
            verb = command.split()[0] if command else ""
            normalized_command = " ".join(command.split())
            # normalized_alternates = (" ".join(s.split()) for s in v)
            if (normalized_command in v):
                return key
            elif does_command_match(normalized_command, v):
                return key
            else:
                key_parts = key.split(maxsplit=1)
                if len(key_parts) == 2 and does_command_match(normalized_command, [key_parts[1]]):
                    return key
    return None


def get_alternate_names(command: str) -> list | None:
    global COMMAND_DEFINITIONS
    return get_command_spec(command).get('alternate_names', None)


def get_attribute(command: str, attrib_name: str) -> dict | None:
    attr = get_command_spec(command)['Attributes']
    if attr:
        for attribute_dict in attr:
            if "Display Name" in attribute_dict:
                return attribute_dict["Display Name"]
    else:
        print("Key not found in the dictionary.")


def get_attribute_labels(command: str, attrib_name: str) -> list | None:
    label_str = get_attribute(command, attrib_name).get('attr_labels', None)
    if label_str:
        return label_str.split(';')
    else:
        print("Key not found in the dictionary.")
        return None


def add_default_upsert_attributes(attributes: list[dict]) -> list[dict]:
    new_attributes = attributes
    default_upsert_attributes = [
        {
            "Status": {
                "variable_name": "element_status",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "APPROVED",
                "default_value": "ACTIVE",
                "valid_values": "DRAFT; PREPARED; PROPOSED; APPROVED; REJECTED; APPROVED_CONCEPT; UNDER_DEVELOPMENT; DEVELOPMENT_COMPLETE; APPROVED_FOR_DEPLOYMENT; ACTIVE; DISABLED; DEPRECATED; OTHER",
                "existing_element": "",
                "description": "The status of the digital product. There is a list of valid values that this conforms to.",

                "generated": False,
                "style": "Valid Value",
                "user_specified": True,
                "unique": False,
                "input_required": False,

                "min_cardinality": 1,
                "max_cardinality": 1,
                "level": "INVISIBLE",

            }
        },
        {
            "User Defined Status": {
                "variable_name": "user_defined_status",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "Pink",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "Only valid if Product Status is set to OTHER. User defined & managed status values.",
                "generated": False,
                "style": "Simple",
                "user_specified": True,
                "unique": False,
                "input_required": False,
                "min_cardinality": 0,
                "max_cardinality": 1,
                "level": "Basic",
            }
        },

        {
            "Category": {
                "variable_name": "category",
                "inUpdate": True,
                "attr_labels": "Category Name",
                "examples": "",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "A user specified category name that can be used for example, to define product types or agreement types.",

                "generated": False,
                "style": "Simple",
                "user_specified": True,
                "unique": False,
                "input_required": False,

                "min_cardinality": 0,
                "max_cardinality": 1,
                "level": "Basic",

            }
        },
        {
            "Version Identifier": {
                "variable_name": "current_version",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "V1.01",
                "default_value": "1.0",
                "valid_values": "",
                "existing_element": "",
                "description": "Published product version identifier.",

                "generated": False,
                "style": "Simple",
                "user_specified": True,
                "unique": False,
                "input_required": False,

                "min_cardinality": 0,
                "max_cardinality": 1,
                "level": "Basic",

            }
        },
        {
            "URL": {
                "variable_name": "url",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "Link to supporting information",

                "generated": False,
                "style": "Simple",
                "user_specified": True,
                "unique": False,
                "input_required": False,

                "min_cardinality": 0,
                "max_cardinality": 1,
                "level": "Basic",

            }
        },
        {
            "Identifier": {
                "variable_name": "identifier",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "role identifier",

                "generated": False,
                "style": "Simple",
                "user_specified": True,
                "unique": False,
                "input_required": False,

                "min_cardinality": 1,
                "max_cardinality": 1,
                "level": "Basic",

            }
        },
        {
            "Classifications": {
                "variable_name": "classifications",
                "inUpdate": True,
                "attr_labels": "classification",
                "examples": "Folder;  RootCollection; ReferenceList; HomeCollection; ResultSet; RecentAccess; WorkItemList; NameSpace ",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "Optionally specify the initial classifications for a collection. Multiple classifications can be specified. ",

                "generated": False,
                "style": "Named DICT",
                "min_cardinality": 0,
                "max_cardinality": 1,
                "level": "Advanced"
            }
        },
        {
            "Is Own Anchor": {
                "variable_name": "is_own_anchor",
                "inUpdate": True,
                "attr_labels": "Own Anchor",
                "examples": "",
                "default_value": "True",
                "valid_values": "",
                "existing_element": "",
                "description": "Generally True. ",

                "generated": False,
                "style": "Bool",
                "user_specified": True,
                "unique": False,
                "input_required": False,

                "min_cardinality": 1,
                "max_cardinality": 1,
                "level": "Advanced",

            }
        },
        {
            "Anchor ID": {
                "variable_name": "anchor_id",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "Anchor identity for the collection. Typically a qualified name but if display name is unique then it could be used (not recommended)",

                "generated": False,
                "style": "Reference Name",
                "user_specified": True,
                "unique": True,
                "input_required": False,

                "min_cardinality": 0,
                "max_cardinality": 1,
                "level": "Advanced",

            }
        },
        {
            "Parent ID": {
                "variable_name": "parent_id",
                "inUpdate": True,
                "attr_labels": "Parent;",
                "examples": "DataDict::MyParent",
                "default_value": "",
                "valid_values": "",
                "existing_element": "DataDicti",
                "description": "Unique name of the parent element.",

                "generated": False,
                "style": "Reference Name",
                "user_specified": True,
                "unique": False,
                "input_required": False,

                "min_cardinality": 0,
                "max_cardinality": 1,
                "level": "Advanced",
                "Journal Entry": "Should the parent be anything or just a collection?"
            }
        },
        {
            "Parent Relationship Type Name": {
                "variable_name": "parent_rel_type_name",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "The kind of the relationship to the parent element.",

                "generated": False,
                "style": "Simple",
                "user_specified": True,
                "unique": False,
                "input_required": False,

                "min_cardinality": 0,
                "max_cardinality": 1,
                "level": "Advanced",
                "Journal Entry": "Any restrictions?"
            }
        },
        {
            "Anchor Scope Name": {
                "variable_name": "anchor_scope_guid",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "",
                "default_value": "",
                "valid_values": "",
                "existing_element": "DataDict",
                "description": "Optional qualified name of an anchor scope.",

                "generated": False,
                "style": "Reference Name",
                "user_specified": True,
                "unique": False,
                "input_required": False,

                "min_cardinality": 0,
                "max_cardinality": 1,
                "level": "Advanced",

            }
        },
        {
            "Parent at End1": {
                "variable_name": "parent_end1",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "",
                "default_value": "True",
                "valid_values": "",
                "existing_element": "",
                "description": "Is the parent at end1 of the relationship?",

                "generated": False,
                "style": "Bool",
                "user_specified": True,
                "unique": False,
                "input_required": False,

                "min_cardinality": 0,
                "max_cardinality": 1,
                "level": "Advanced",

            }
        },
        {
            "Qualified Name": {
                "variable_name": "qualified_name",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "dataField::a data field",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "A unique qualified name for the element. Generated using the qualified name pattern  if not user specified.",
                "qualified_name_pattern": "local_qualifier::namespace::DataDictionary:display_name::version_id",
                "generated": True,
                "style": "QN",
                "user_specified": True,
                "unique": True,
                "input_required": False,

                "min_cardinality": 1,
                "max_cardinality": 1,
                "level": "Basic",

            }
        },
        {
            "GUID": {
                "variable_name": "guid",
                "inUpdate": True,
                "attr_labels": "Guid; guid",
                "examples": "00585a82-0f7d-45ef-9b87-7078665917a9",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "A system generated unique identifier.",

                "generated": True,
                "style": "GUID",
                "user_specified": False,
                "unique": True,
                "input_required": False,

                "min_cardinality": 1,
                "max_cardinality": 1,
                "level": "Basic",

            }
        },
        {
            "Effective Time": {
                "variable_name": "effective_time",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "An ISO-8601 string representing the time to use for evaluating effectivity of the elements related to this one.",

                "generated": False,
                "style": "Simple",
                "user_specified": True,
                "unique": False,
                "input_required": False,

                "min_cardinality": 1,
                "max_cardinality": 1,
                "level": "Advanced",

            }
        },
        {
            "Effective From": {
                "variable_name": "effective_from",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "A string in ISO-8601 format that defines the when an element becomes effective (visible).",
                "generated": False,
                "style": "Simple",
                "user_specified": True,
                "unique": False,
                "input_required": False,
                "min_cardinality": 0,
                "max_cardinality": 1,
                "level": "Advanced",

            }
        },
        {
            "Effective To": {
                "variable_name": "effective_to",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "A string in ISO-8601 format that defines the when an element is no longer effective (visible).",

                "generated": False,
                "style": "Simple",
                "user_specified": True,
                "unique": False,
                "input_required": False,

                "min_cardinality": 1,
                "max_cardinality": 1,
                "level": "Advanced",

            }
        },
        {
            "Merge Update": {
                "variable_name": "merge_update",
                "inUpdate": True,
                "attr_labels": "Merge",
                "examples": "",
                "default_value": "True",
                "valid_values": "",
                "existing_element": "",
                "description": "If True, only those attributes specified in the update will be updated; If False, any attributes not provided during the update will be set to None.",

                "generated": False,
                "style": "Bool",
                "user_specified": True,
                "unique": False,
                "input_required": False,

                "min_cardinality": 0,
                "max_cardinality": 1,
                "level": "Advanced",

            }
        },
        {
            "Additional Properties": {
                "variable_name": "additional_properties",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "Additional user defined values organized as name value pairs in a dictionary.",

                "generated": False,
                "style": "Dictionary",
                "user_specified": True,
                "unique": False,
                "input_required": False,

                "min_cardinality": 0,
                "max_cardinality": -1,
                "level": "Advanced",

            }
        },
        {
            "Extended Properties": {
                "variable_name": "additional_properties",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "Additional user defined values organized as name value pairs in a dictionary.",
                "generated": False,
                "style": "Named DICT",
                "user_specified": True,
                "unique": False,
                "input_required": False,
                "min_cardinality": 0,
                "max_cardinality": -1,
                "level": "Invisible",
            }
        },
        {
            "External Source GUID": {
                "variable_name": "external_source_guid",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "Identifier of an external source that is associated with this element.",

                "generated": False,
                "style": "Simple",
                "user_specified": True,
                "unique": False,
                "input_required": False,

                "min_cardinality": 0,
                "max_cardinality": 1,
                "level": "Advanced",

            }
        },
        {
            "External Source Name": {
                "variable_name": "external_source_name",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "Name of an external element that is associated with this element.",
                "generated": False,
                "style": "Simple",
                "user_specified": True,
                "unique": False,
                "input_required": False,
                "min_cardinality": 0,
                "max_cardinality": 1,
                "level": "Advanced",

            }
        },
        {
            "Journal Entry": {
                "variable_name": "journal_entry",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "",
                "generated": False,
                "style": "Simple",
                "user_specified": True,
                "unique": False,
                "input_required": False,

                "min_cardinality": 0,
                "max_cardinality": 1,
                "level": "Basic",

            }
        },
        {
            "URL": {
                "variable_name": "url",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "Link to supporting information",

                "generated": False,
                "style": "Simple",
                "user_specified": True,
                "unique": False,
                "input_required": False,

                "min_cardinality": 0,
                "max_cardinality": 1,
                "level": "Basic",

            }
        },
        {
            "Search Keywords": {
                "variable_name": "search_keywords",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "Keywords to facilitate finding the element",

                "generated": False,
                "style": "Simple List",
                "user_specified": True,
                "unique": False,
                "input_required": False,

                "min_cardinality": 0,
                "max_cardinality": 20,
                "level": "Basic",

            }
        },
        {
            "Translation Details": {
                "variable_name": "translation_details",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "Allow translation information for the element to be provided.",
                "generated": False,
                "style": "Named DICT",
                "user_specified": True,
                "unique": False,
                "input_required": False,
                "min_cardinality": 0,
                "max_cardinality": -1,
                "level": "Invisible",
            }
        },
        {
            "Supplementary Properties": {
                "variable_name": "supplementary_properties",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "Provide supplementary information to the element using the structure of a glossary term",
                "generated": False,
                "style": "Named DICT",
                "user_specified": True,
                "unique": False,
                "input_required": False,
                "min_cardinality": 0,
                "max_cardinality": -1,
                "level": "Advanced",
            }
        },
    ]
    new_attributes.extend(default_upsert_attributes)
    return new_attributes


def add_default_link_attributes(attributes: list[dict]) -> list[dict]:
    new_attributes = attributes
    default_link_attributes = [
        {
            "Effective Time": {
                "variable_name": "effective_time",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "An ISO-8601 string representing the time to use for evaluating effectivity of the elements related to this one.",

                "generated": False,
                "style": "Simple",
                "user_specified": True,
                "unique": False,
                "input_required": False,

                "min_cardinality": 1,
                "max_cardinality": 1,
                "level": "Advanced",

            }
        },
        {
            "Effective From": {
                "variable_name": "effective_from",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "A string in ISO-8601 format that defines the when an element becomes effective (visible).",

                "generated": False,
                "style": "Simple",
                "user_specified": True,
                "unique": False,
                "input_required": False,

                "min_cardinality": 0,
                "max_cardinality": 1,
                "level": "Advanced",

            }
        },
        {
            "Effective To": {
                "variable_name": "effective_to",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "A string in ISO-8601 format that defines the when an element is no longer effective (visible).",

                "generated": False,
                "style": "Simple",
                "user_specified": True,
                "unique": False,
                "input_required": False,

                "min_cardinality": 1,
                "max_cardinality": 1,
                "level": "Advanced",

            }
        },
        {
            "Extended Properties": {
                "variable_name": "additional_properties",
                "inUpdate": True,
                "attr_labels": "",
                "examples": "",
                "default_value": "",
                "valid_values": "",
                "existing_element": "",
                "description": "Additional user defined values organized as name value pairs in a dictionary.",

                "generated": False,
                "style": "Dictionary",
                "user_specified": True,
                "unique": False,
                "input_required": False,

                "min_cardinality": 0,
                "max_cardinality": -1,
                "level": "Invisible",

            }
        }

    ]
    new_attributes.extend(default_link_attributes)
    return new_attributes
