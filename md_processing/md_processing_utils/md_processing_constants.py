"""
This file contains display-related constants and formatting functions for Egeria Markdown processing
"""
import importlib.resources
import json
import os
import inflect

from rich.markdown import Markdown

from md_processing.md_processing_utils.message_constants import ERROR
from pyegeria._globals import DEBUG_LEVEL
from md_processing.md_processing_utils.message_constants import message_types, ALWAYS, ERROR, INFO, WARNING

inflect_engine = inflect.engine()


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
GOV_LINK_LIST = [ "Link Governance Drivers", "Detach Governance Drivers",
                "Link Governance Policies", "Detach Governance Policies",
                "Link Governance Controls", "Detach Governance Controls",]

GOV_COM_LIST = [ "Create Business Imperative", "Update Business Imperative",
                "Create Regulation Article Definition", "Update Regulation Article Definition",
                "Create Threat Definition", "Update Threat Definition",
                "Create Governance Principle", "Update Governance Principle",
                "Create Governance Obligation", "Update Governance Obligation",
                "Create Governance Approach", "Update Governance Approach",
                "Create Governance Strategy", "Update Governance Strategy",
                "Create Regulation", "Create Regulation Definition", "Update Regulation", "Update Regulation Definition",
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
                "Create License Type", "Update License Type",]

SIMPLE_BASE_COLLECTIONS: set = { "Collection", "Home Collection", "Digital Product", "Result Set" , "Recent Access",
                       "Reference List", "Work Item List", "Data Sharing Agreement", "Namespace", "Agreement",
                       "Digital Subscription", "Data Product", "Subscription",
                      "Root Collection",  "Folders",  "Context Event Collection",  "Name Space Collection",
                    # "Data Specifications", "Data Specifications", "Data Specs", "Data Specs",
                    # "Data Dictionaries", "Data Dictionaries",
                     "Event Set Collection", "Naming Standard Ruleset",
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
                    "List Naming Standard Rulesets", "View Naming Standard Rulesets",
                    ]

command_list = ["Provenance", "Create Glossary", "Update Glossary", "Create Term", "Update Term", "List Terms",
                "List Term Details", "List Glossary Terms", "List Term History", "List Term Revision History",
                "List Term Update History", "List Glossary Structure", "List Glossaries", "List Categories",
                "List Glossary Categories", "Create Personal Project", "Update Personal Project", "Create Category",
                "Update Category", "Create Solution Blueprint", "Update Solution Blueprint", "View Solution Blueprint",
                "View Solution Blueprints", "View Blueprints",
                "View Information Supply Chain", "View Information Supply Chains", "View Supply Chains", "View Supply Chain",
                "View Solution Components", "View Solution Component", "View Solution Roles", "View Solution Role",
                "Create Information Supply Chain", "Update Information Supply Chain",
                "Link Information Supply Chain Peers", "Link Supply Chains", "Link Information Supply Chains",
                "Unlink Information Supply Chain Peers", "Unlink Information Supply Chains", "Unlink Supply Chains",
                "Create Solution Component", "Update Solution Component", "Link Solution Components", "Wire Solution Components",
                "Detach Solution Components", "Unlink Solution Components", "Create Term-Term Relationship",
                "Update Term-Term Relationship", "Create Data Spec", "Create Data Specification", "Update Data Spec",
                "Update Data Specification", "Create Data Field", "Update Data Field", "Create Data Structure",
                "Update Data Structure", "Create Data Dictionary", "Update Data Dictionary", "Create Data Dict",
                "Update Data Dict",
                "View Data Structures", "View Data Structure", "View Data Fields", "View Data Field",
                "View Dataa Classes", "View Data Class", "Create Data Class", "Update Data Class",
                "Create Digital Product", "Create Data Product", "Update Digital Product", "Update Data Product",
                "Create Agreement", "Update Agreement",
                "Link Digital Products", "Link Data Products", "Detach Digital Products", "Detach Data Products",
                # "Create Data Sharing Agreement", "Update Data Sharing Agreement",
                "Create Digital Subscription", "Create Product Subscription", "Update Digital Subscription", "Update Product Subscription",
                "Attach Agreement Items", "Detach Agreement Items",
                "Attach Contract", "Detach Contract",
                "Attach Subscriber", "Detach Subscriber",
                "Link Collection to Resource", "Attach Collection to Resource",
                "Unlink Collection From Resource", "Detach Collection From Resource",
                "Add Member to Collection", "Add Member", "Member->Collection",
                "Remove Member from Collection","Remove Member from Collection",
                 "View Governance Definitions", "View Gov Definitions",
                 "List Governance Definitions", "List Gov Definitions",
                "View Governance Definition Context","List Governance Definition Context",
                "View Governance Def Context", "List Governance Def Context",
                # "Create Business Imperative", "Update Business Imperative",
                # "Create Regulation Article Definition", "Update Regulation Article Definition",
                # "Create Threat Definition", "Update Threat Definition",
                # "Create Governance Principle", "Update Governance Principle",
                # "Create Governance Obligation", "Update Governance Obligation",
                # "Create Governance Approach", "Update Governance Approach",
                # "Create Governance Strategy", "Update Governance Strategy",
                # "Create Regulation", "Create Regulation Definition", "Update Regulation", "Update Regulation Definition",
                # "Create Governance Control:", "Update Governance Control",
                # "Create Governance Rule:", "Update Governance Rule",
                # "Create Service Level Objective", "Update Service Level Objective",
                # "Create Governance Process", "Update Governance Process",
                # "Create Governance Responsibility", "Update Governance Responsibility",
                # "Create Governance Procedure", "Update Governance Procedure",
                # "Create Security Access Control", "Update Security Access Control",
                # "Create Security Group", "Update Security Group",
                # "Create Naming Standard Rule", "Update Naming Standard Rule",
                # "Create Certification Type", "Update Certification Type",
                # "Create License Type", "Update License Type",
                # "Link Governance Drivers", "Detach Governance Drivers",
                # "Link Governance Policies", "Detach Governance Policies",
                # "Link Governance Controls", "Detach Governance Controls",

                ]

command_list.extend(GOV_COM_LIST)
command_list.extend(GOV_LINK_LIST)
command_list.extend(COLLECTIONS_LIST)
command_list.extend(SIMPLE_COLLECTIONS)

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
