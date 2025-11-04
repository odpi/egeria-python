"""
This file contains display-related constants and formatting functions for Egeria Markdown processing
"""
import importlib.resources
import json
import os

import inflect
from loguru import logger
from rich.markdown import Markdown

from pyegeria._globals import DEBUG_LEVEL
from pyegeria.logging_configuration import config_logging

inflect_engine = inflect.engine()

EGERIA_ROOT_PATH = os.environ.get("EGERIA_ROOT_PATH", "/home/jovyan")
EGERIA_INBOX_PATH = os.environ.get("EGERIA_INBOX_PATH", "loading-bay/dr_egeria_inbox")

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
LIST_COMMANDS = {"List Collections", "View Collections", "List Agreements", "View Agreements",
                 "List Digital Products", "View Digital Products", "List Products", "View Products",
                 "List Subscriptions", "View Subscriptions", "List Folders", "View Folders",
                 "List Data Specifications", "View Data Specifications", "List Data Specs", "View Data Specs",
                 "List Data Dictionaries", "View Data Dictionaries",
                 "List Governance Definitions", "View Governance Definitions", "List Governance Drivers",
                 "View Governance Drivers",
                 "List Governance Policies", "View Governance Policies", "List Governance Controls",
                 "View Governance Controls",
                 "List Governance Rules", "View Governance Rules", "List Governance Principles",
                 "View Governance Principles",
                 "List Governance Obligations", "View Governance Obligations", "List Governance Approaches",
                 "View Governance Approaches",
                 "List Governance Strategies", "View Governance Strategies", "List Regulations", "View Regulations",
                 "List Regulation Definitions", "View Regulation Definitions",
                 "List Naming Standard Rulesets", "View Naming Standard Rulesets", "List Governance Drivers",
                 "List Governance Strategies", "List Business Imperatives" "List Regulations",
                 "List Regulation Articles", "List Threats",
                 "List Governance Metrics", "View Governance Metrics", "List Service Level Objectives",
                 "View Service Level Objectives",
                 "List Governance Rules", "View Governance Rules", "List Notification Types", "View Notification Types",
                 "List Security Access Controls", "View Security Access Controls", "List Security Groups",
                 "View Security Groups",
                 "List Governance Procedures", "View Governance Procedures", "List Methodologies", "View Methodologies",
                 "List Governance Responsibilities", "View Governance Responsibilities", "List Terms and Conditions",
                 "View Terms and Conditions", "List License Types", "View License Types", "List Certification Types",
                 "View Certification Types",
                 "List Subject Area Definitions", "View Subject Area Definitions", "List Data Processing Purposes",
                 "View Data Processing Purposes",
                 "List Projects", "View Projects",

                 }

SIMPLE_COLLECTIONS: set = set()
for element in SIMPLE_BASE_COLLECTIONS:
    SIMPLE_COLLECTIONS.add(f"Create {element}")
    SIMPLE_COLLECTIONS.add(f"Update {element}")
    plural = inflect_engine.plural_noun(element)
    SIMPLE_COLLECTIONS.add(f"Create {plural}")
    SIMPLE_COLLECTIONS.add(f"Update {plural}")

COLLECTIONS_LIST = ["List Collections", "View Collections", "List Digital Products", "View Digital Products",
                    "List Data Products", "View Data Products",
                    "List Data Sharing Agreements", "View Data Sharing Agreements",
                    "List Agreements", "View Agreements",
                    "List Digital Subscriptions", "View Digital Subscriptions",
                    "List Subscriptions", "View Subscriptions",
                    "List Root Collections", "View Root Collections",
                    "List Data Specifications", "View Data Specifications", "List Data Specs", "View Data Specs",
                    "List Data Dictionaries", "View Data Dictionaries",
                    "List Folders", "View Folders",
                    "List Context Event Collections", "View Context Event Collections",
                    "List Name Space Collections", "View Name Space Collections",
                    "List Event Set Collections", "View Event Set Collections",
                    "List Naming Standard Rulesets", "View Naming Standard Rulesets", "List External Reference",
                    "List Related Media", "List Cited Document", "List External Data Source",
                    "List External Model Source",
                    "List Digital Product Catalogs", "View Digital Product Catalogs", ]

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

command_list = ["Provenance", "Create Glossary", "Update Glossary", "Create Term", "Update Term", "List Terms",
                "List Term Details", "List Glossary Terms", "List Term History", "List Term Revision History",
                "List Term Update History", "List Glossary Structure", "List Glossaries", "List Categories",
                "List Glossary Categories", "Link Project Dependency", "Attach Project Dependency",
                "Detach Project Dependency", "Link Parent Project", "Attach Parent Project", "Detach Parent Project",
                "Detach Parent Project",
                "Create Solution Blueprint", "Update Solution Blueprint", "View Solution Blueprint",
                "View Solution Blueprints", "View Blueprints",
                "View Information Supply Chain", "View Information Supply Chains", "View Supply Chains",
                "View Supply Chain",
                "View Solution Components", "View Solution Component", "View Solution Roles", "View Solution Role",
                "Create Information Supply Chain", "Update Information Supply Chain",
                "Link Information Supply Chain Peers", "Link Supply Chains", "Link Information Supply Chains",
                "Unlink Information Supply Chain Peers", "Unlink Information Supply Chains", "Unlink Supply Chains",
                "Create Solution Component", "Update Solution Component", "Link Solution Components",
                "Wire Solution Components",
                "Detach Solution Components", "Unlink Solution Components", "Link Term-Term Relationship", "Link Terms",
                "Detach Terms",
                "Detach Term-Term Relationship", "Create Data Spec", "Create Data Specification", "Update Data Spec",
                "Update Data Specification", "Create Data Field", "Update Data Field", "Create Data Structure",
                "Update Data Structure", "Create Data Dictionary", "Update Data Dictionary", "Create Data Dict",
                "Update Data Dict",
                "View Data Structures", "View Data Structure", "View Data Fields", "View Data Field",
                "View Data Classes", "View Data Class", "Create Data Class", "Update Data Class",

                "Create Data Specifications", "Update Data Specifications", "Create Data Specs", "Update Data Specs",
                "Create Data Dictionaries", "Update Data Dictionaries", "Create Data Dicts", "Update Data Dicts",
                "View Data Specifications", "View Data Specification", "View Data Specs", "View Data Specification",
                "View Data Dictionaries", "View Data Dictionary", "View Data Dicts", "View Data Dictionary",
                "Link Collection->Root Collection", "Link Collection->Folder",
                "Link Collection->Context Event Collection", "Link Collection->Name Space Collection",
                "Link Collection->Event Set Collection", "Link Collection->Naming Standard Ruleset",
                "Create Digital Product", "Create Data Product", "Update Digital Product", "Update Data Product",
                "Create Agreement", "Update Agreement",
                "Link Digital Products", "Link Product-Product", "Detach Digital Products", "Detach Product-Product",
                "Create Data Sharing Agreement", "Update Data Sharing Agreement",
                "Create Digital Subscription", "Create Product Subscription", "Update Digital Subscription",
                "Update Product Subscription",
                "Link Agreement->Item", "Detach Agreement->Item",
                "Attach Contract", "Detach Contract",
                "Link Subscriber->Subscription", "Detach Subscriber->Subscription",
                "Link Collection->Resource", "Attach Collection->Resource",
                "Unlink Collection->Resource", "Detach Collection->Resource",
                "Add Member to Collection", "Add Member", "Add Member->Collection", 'Add Member', 'Add to Folder',
                "Remove Member from Collection", "Remove Member->Collection", ' Remove Member', 'Remove from Folder',
                "View Governance Definitions", "View Gov Definitions",
                "List Governance Definitions", "List Gov Definitions",
                "View Governance Definition Context", "List Governance Definition Context",
                "View Governance Def Context", "List Governance Def Context",
                "View Report",
                "Create Business Imperative", "Update Business Imperative",
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
                "Link Governance Drivers", "Detach Governance Drivers",
                "Link Governance Policies", "Detach Governance Policies",
                "Link Governance Controls", "Detach Governance Controls",
                "Link Governed By", "Attach Governed By", "Detach Governed By",
                "Create CSV File"

                ]
command_list.extend(LIST_COMMANDS)
command_list.extend(GOV_COM_LIST)
command_list.extend(GOV_LINK_LIST)
command_list.extend(COLLECTIONS_LIST)
command_list.extend(COLLECTION_CREATE)
command_list.extend(SIMPLE_COLLECTIONS)
command_list.extend(PROJECT_COMMANDS)
command_list.extend(EXT_REF_COMMANDS)
command_list.extend(["Link Governance Response", "Detach Governance Response",
                     "Link Governance Mechanism", "Detach Governance Mechanism"])
command_list.extend(FEEDBACK_COMMANDS)
pre_command = "\n---\n==> Processing object_action:"
command_seperator = Markdown("\n---\n")
EXISTS_REQUIRED = "Exists Required"
COMMAND_DEFINITIONS = {}

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
    global COMMAND_DEFINITIONS

    try:
        config_path = importlib.resources.files("md_processing") / "data" / filename
        config_str = config_path.read_text(encoding="utf-8")

        # Validate JSON before attempting to load
        try:
            COMMAND_DEFINITIONS = json.loads(config_str)
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
        raise FileNotFoundError(msg)
    except Exception as e:
        msg = f"ERROR: Unexpected error loading {filename}: {str(e)}"
        print(msg)
        COMMAND_DEFINITIONS = {}
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
    # Define verb synonyms
    verbs_synonyms = {
        "Link": ["Link", "Attach", "Detach", "Unlink"],
        "Create": ["Create", "Update"],
        "View": ["List", "View"],
    }

    # Extract the verb from the command
    command_parts = command.split(maxsplit=1)
    if len(command_parts) < 2:
        return False  # Invalid command structure
    verb, terms = command_parts

    # Generate all possible combinations and check for a match
    for primary_verb, synonyms in verbs_synonyms.items():
        for synonym in synonyms:
            for alt_name in alt_names:
                alt_name = alt_name.strip()
                tst = f"{synonym} {alt_name}"
                if tst == command:
                    return True
    return False


def find_alternate_names(command: str) -> str | None:
    global COMMAND_DEFINITIONS

    comm_spec = COMMAND_DEFINITIONS.get('Command Specifications', {})
    for key, value in comm_spec.items():
        if isinstance(value, dict):
            v = value.get('alternate_names', "")
            v = v.split(';') if v else ""
            verb = command.split()[0] if command else ""
            normalized_command = " ".join(command.split())
            # normalized_alternates = (" ".join(s.split()) for s in v)
            if (normalized_command in v):
                return key
            elif does_command_match(normalized_command, v):
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
