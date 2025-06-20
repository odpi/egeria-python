"""
This file contains display-related constants and formatting functions for Egeria Markdown processing
"""
import importlib.resources
import json
import os

from rich.markdown import Markdown

from md_processing.md_processing_utils.message_constants import ERROR
from pyegeria._globals import DEBUG_LEVEL
from md_processing.md_processing_utils.message_constants import message_types, ALWAYS, ERROR, INFO, WARNING

EGERIA_ROOT_PATH = os.environ.get("EGERIA_ROOT_PATH", "/home/jovyan")
EGERIA_INBOX_PATH = os.environ.get("EGERIA_INBOX_PATH", "loading-bay/dr_egeria_inbox")

# Constants for element labels
GLOSSARY_NAME_LABELS = ["Glossary Name", "Glossary", "Glossaries", "Owning Glossary", "In Glossary"]
CATEGORY_NAME_LABELS = ["Glossary Category Name", "Glossary Category", "Glossary Categories", "Category Name",
                        "Category", "Categories"]
PARENT_CATEGORY_LABELS = ["Parent Category Name", "Parent Category", "parent category name", "parent category"]
CHILD_CATEGORY_LABELS = ["Child Categories", "Child Category", "child category names", "child categories",
                         "Child Category Names"]
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
command_list = ["Provenance", "Create Glossary", "Update Glossary", "Create Term", "Update Term", "List Terms",
                "List Term Details", "List Glossary Terms", "List Term History", "List Term Revision History",
                "List Term Update History", "List Glossary Structure", "List Glossaries", "List Categories",
                "List Glossary Categories", "Create Personal Project", "Update Personal Project", "Create Category",
                "Update Category", "Create Solution Blueprint", "Update Solution Blueprint", "View Solution Blueprint", "View Solution Blueprints", "View Blueprints",
                "View Information Supply Chain", "View Information Supply Chains", "View Supply Chains", "View Supply Chain",
                "View Solution Components", "View Solution Component", "View Solution Roles", "View Solution Role",
                "Create Information Supply Chain", "Update Information Supply Chain",
                "Create Information Supply Chain Segment", "Update Information Supply Chain Segment", "Link Segments", "Detach Segments",
                "Create Solution Component", "Update Solution Component", "Create Term-Term Relationship",
                "Update Term-Term Relationship", "Create Data Spec", "Create Data Specification", "Update Data Spec",
                "Update Data Specification", "Create Data Field", "Update Data Field", "Create Data Structure",
                "Update Data Structure", "Create Data Dictionary", "Update Data Dictionary", "Create Data Dict",
                "Update Data Dict", " View Data Dictionary", "View Data Dictionaries", "View Data Specifications",
                "View Data Specs", "View Data Structures", "View Data Structure", "View Data Fields", "View Data Field",
                "View Dataa Classes", "View Data Class", "Create Data Class", "Update Data Class",]


pre_command = "\n---\n==> Processing object_action:"
command_seperator = Markdown("\n---\n")
EXISTS_REQUIRED = "Exists Required"
COMMAND_DEFINITIONS = {}

debug_level = DEBUG_LEVEL


def load_commands(filename: str) -> None:
    global COMMAND_DEFINITIONS

    try:
        config_path = importlib.resources.files("md_processing") / "data" / filename
        config_str = config_path.read_text(encoding="utf-8")
        COMMAND_DEFINITIONS = json.loads(config_str)

    except FileNotFoundError:
        msg = f"ERROR: File {filename} not found."
        print(ERROR, msg, debug_level)


def get_command_spec(command: str) -> dict | None:
    global COMMAND_DEFINITIONS
    com = COMMAND_DEFINITIONS.get('Command Specifications', {}).get(command, None)
    if com:
        return com
    else:
        obj = find_alternate_names(command)
        if obj:
            return COMMAND_DEFINITIONS.get('Command Specifications', {}).get(obj, None)


def find_alternate_names(command: str) -> str | None:
    global COMMAND_DEFINITIONS
    comm_spec = COMMAND_DEFINITIONS.get('Command Specifications', {})
    for key, value in comm_spec.items():
        if isinstance(value, dict):
            v = value.get('alternate_names', "")
            if command in v:
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
