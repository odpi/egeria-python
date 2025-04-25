"""
This file contains display-related constants and formatting functions for Egeria Markdown processing
"""
from rich.markdown import Markdown
from pyegeria._globals import DEBUG_LEVEL

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
TERM_RELATIONSHPS = [
    "Synonym",
    "Translation",
    "PreferredTerm",
    "TermISATYPEOFRelationship",
    "TermTYPEDBYRelationship",
    "Antonym",
    "ReplacementTerm",
    "ValidValue",
    "TermHASARelationship",
    "RelatedTerm",
    "ISARelationship"
]

# List of supported md_commands
command_list = ["Provenance", "Create Glossary", "Update Glossary", "Create Term", "Update Term", "List Terms", "List Term Details",
                "List Glossary Terms", "List Term History", "List Term Revision History", "List Term Update History",
                "List Glossary Structure", "List Glossaries", "List Categories", "List Glossary Categories",
                "Create Personal Project", "Update Personal Project", "Create Category", "Update Category",
                "Create Solution Blueprint", "Update Solution Blueprint", "Create Solution Component",
                "Update Solution Component", "Create Term-Term Relationship", "Update Term-Term Relationship",]


message_types = {
    "INFO": "INFO-", "WARNING": "WARNING->", "ERROR": "ERROR->", "DEBUG-INFO": "DEBUG-INFO->",
    "DEBUG-WARNING": "DEBUG-WARNING->", "DEBUG-ERROR": "DEBUG-ERROR->", "ALWAYS": "\n\n==> "
}
ALWAYS = "ALWAYS"
ERROR = "ERROR"
INFO = "INFO"
WARNING = "WARNING"
pre_command = "\n---\n==> Processing command:"
command_seperator = Markdown("\n---\n")
EXISTS_REQUIRED = "Exists Required"

debug_level = DEBUG_LEVEL