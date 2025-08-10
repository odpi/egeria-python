"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.
"""

"""
# Purpose
This file manages output format sets.

pyegeria allows find and get requests to generate output in different output formats - 
including DICT, MD, FORM, REPORT, LIST, MERMAID, TABLE, and perhaps additional ones in the future.

It is important to be able to filter which attributes to
display, and the order in which they appear. However, many, if not most users will likely not want to customize
the column list and so we need a sensible set of defaults for each type of output. These defaults are used 
by the find and get methods if the user doesn't provide a value for the columns parameter.

This file contains these defaults and functions to work with them. The output format sets are now implemented
using Pydantic models defined in `_output_format_models.py`, which provide several advantages:
- Type validation: The models ensure that the data has the correct types and structure.
- Composition: The models support composition of formats, allowing formats to be reused and combined.
- Documentation: The models provide clear documentation of the data structure.
- IDE support: The models provide better IDE support, including autocompletion and type hints.

The functions in this module are designed to be backward compatible with code that expects the old
dictionary-based format. They convert between Pydantic models and dictionaries as needed.

Example usage:
```python
# Get a format set by name and output type
format_set = select_output_format_set("Collections", "TABLE")

# Get a list of all available format sets
format_sets = output_format_set_list()

# Get the heading and description of a format set
heading = get_output_format_set_heading("Collections")
description = get_output_format_set_description("Collections")

# Match a format set with a specific output type
matched_format_set = get_output_format_type_match(format_set, "DICT")
```

For more advanced usage, you can work directly with the Pydantic models:
```python
from pyegeria._output_format_models import Column, Format, FormatSet

# Create a new format set
format_set = FormatSet(
    heading="Example Format Set",
    description="An example format set",
    formats=[
        Format(
            types=["TABLE", "DICT"],
            columns=[
                Column(name="Display Name", key="display_name"),
                Column(name="Description", key="description", format=True),
            ],
        ),
    ],
)

# Add the format set to the output_format_sets dictionary
output_format_sets["Example"] = format_set
```
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from loguru import logger

from pyegeria._output_format_models import Column, Format, ActionParameter, FormatSet, FormatSetDict, save_format_sets_to_json, load_format_sets_from_json
from pyegeria.load_config import get_app_config

# Get the configured value for the user format sets directory
app_config = get_app_config()
USER_FORMAT_SETS_DIR = os.path.expanduser(app_config.Environment.pyegeria_user_format_sets_dir)

# Constants
MD_SEPARATOR = "\n---\n\n"

# Define shared elements
COMMON_COLUMNS = [
    Column(name='Display Name', key='display_name'),
    Column(name='Qualified Name', key='qualified_name', format=True),
    Column(name='Category', key='category'),
    Column(name='Description', key='description', format=True),
]

COMMON_METADATA_COLUMNS = [
    Column(name='GUID', key='guid', format=True),
    Column(name='Metadata Collection ID', key='metadata_collection_id', format=True),
    Column(name='Metadata Collection Name', key='metadata_collection_name', format=True),
]

COMMON_HEADER_COLUMNS = [
    Column(name="Classifications", key='classifications'),
    Column(name="Created By", key='created_by'),
    Column(name="Create Time", key='create_time'),
    Column(name="Updated By", key='updated_by'),
    Column(name="Update Time", key='update_time'),
    Column(name="Effective From", key='effective_from'),
    Column(name="Effective To", key='effective_to'),
    Column(name="Version", key='version'),
    Column(name="Open Metadata Type Name", key='type_name'),
    ]


REFERNCEABLE_COLUMNS = COMMON_COLUMNS + [
    Column(name='Version Identifier', key='version_identifier'),
    Column(name='Additional Properties', key='additional_properties')
    ]


COMMON_FORMATS_ALL = Format(
    types=["ALL"],
    columns=COMMON_COLUMNS,
)


COLLECTIONS_COLUMNS = COMMON_COLUMNS + [
    Column(name="Created By", key='created_by'),
    Column(name="Create Time", key='create_time'),
    Column(name="Updated By", key='updated_by'),
    Column(name="Update Time", key='update_time'),
]

COLLECTIONS_MEMBERS_COLUMNS = COLLECTIONS_COLUMNS + [
    Column(name="Members", key='members'),
    ]

COLLECTION_DICT = Format(
    types=["DICT"],
    columns=COLLECTIONS_COLUMNS,
)

COLLECTION_TABLE = Format(
    types=["TABLE"],
    columns=COMMON_COLUMNS,
)

GOVERNANCE_DEFINITIONS_COLUMNS = COMMON_COLUMNS + [
    Column(name="Document Identifier", key='document_identifier'),
    Column(name="Title", key='title'),
    Column(name="Scope", key='scope'),
    ]

COMMON_ANNOTATIONS = {
    "wikilinks": ["[[Commons]]"]
}

# Modularized output_format_sets
output_format_sets = FormatSetDict({
    "Referenceable": FormatSet(
        heading="Common Attributes",
        description="Attributes that apply to all Referenceables.",
        annotations={},  # No specific annotations
        formats=[
            Format(
                types=["ALL"],
                columns=COMMON_COLUMNS + COMMON_METADATA_COLUMNS + [
                    Column(name='Version Identifier', key='version_identifier'),
                    Column(name="Classifications", key='classifications'),
                    Column(name="Additional Properties", key='additional_properties'),
                    Column(name="Created By", key='created_by'),
                    Column(name="Create Time", key='create_time'),
                    Column(name="Updated By", key='updated_by'),
                    Column(name="Update Time", key='update_time'),
                    Column(name="Effective From", key='effective_from'),
                    Column(name="Effective To", key='effective_to'),
                    Column(name="Version", key='version'),
                    Column(name="Open Metadata Type Name", key='type_name'),
                ],
            )
        ],
    ),
    "Basic-Terms": FormatSet(
        heading="Basic Glossary Term Attributes",
        description="Attributes that apply to all Basic Glossary Terms.",
        annotations={},
        formats=[
            Format(
                types=["ALL"],
                columns=COMMON_COLUMNS + COMMON_METADATA_COLUMNS + [
                    Column(name='Version Identifier', key='version_identifier'),
                    Column(name="Summary", key='summary'),
                    Column(name="Additional Properties", key='additional_properties'),
                    Column(name="Example", key='example'),
                    Column(name="Usage", key='usage'),
                    Column(name="Updated By", key='updated_by'),
                    Column(name="Update Time", key='update_time'),
                    Column(name="Effective From", key='effective_from'),
                    Column(name="Effective To", key='effective_to'),
                    Column(name="GUID", key='guid'),
                    Column(name="Open Metadata Type Name", key='type_name'),
                ],
            )
            ]
        ),

    "Collections": FormatSet(
        heading="Common Collection Information",
        description="Attributes generic to all Collections.",
        aliases=["Collection", "RootCollection", "Folder", "ReferenceList", "HomeCollection",
                "ResultSet", "RecentAccess", "WorkItemList", "Namespace"],
        annotations=COMMON_ANNOTATIONS,
        formats=[COLLECTION_DICT, COLLECTION_TABLE, COMMON_FORMATS_ALL],  # Reusing common formats
        action=[ActionParameter(
            function="CollectionManager.find_collections",
            user_params=["search_string"],
            spec_params={},
        )]
    ),

    "CollectionMembers": FormatSet(
        heading="Collection Membership Information",
        description="Attributes about all CollectionMembers.",
        aliases=["CollectionMember", "Member", "Members"],
        annotations= {"wikilinks": ["[[CollectionMembers]]"]},
        formats = [COLLECTION_DICT, COLLECTION_TABLE],
        action=[ActionParameter(
            function="CollectionManager.get_collection_members",
            user_params=["collection_guid"],
            spec_params={"output_format": "DICT"},
            )]
        ),
    "DigitalProducts": FormatSet(
        heading="Digital Product Information",
        description="Attributes useful to Digital Products.",
        aliases=["DigitalProduct", "DataProducts"],
        annotations={},
        formats=[
            Format(
                types=["REPORT"],
                columns=COMMON_COLUMNS + [
                    Column(name="Status", key='status'),
                    Column(name='Product Name', key='product_name'),
                    Column(name='Identifier', key='identifier'),
                    Column(name='Maturity', key='maturity'),
                    Column(name='Service Life', key='service_life'),
                    Column(name='Next Version', key='next_version'),
                    Column(name='Withdraw Date', key='withdraw_date'),
                    Column(name='Members', key='members', format=True),
                ],
            )
        ],
        action=[ActionParameter(
            function="CollectionManager.find_collections",
            user_params=["search_string"],
            spec_params={"classification_name": "DigitalProducts"},
        )]
    ),

    "Agreements": FormatSet(
        heading="General Agreement Information",
        description="Attributes generic to all Agreements.",
        aliases=["DataSharingAgreement"],
        annotations={"wikilinks": ["[[Agreements]]", "[[Egeria]]"]},
        formats=[COMMON_FORMATS_ALL]  # Reusing common formats and columns
    ),

    "DataDictionary": FormatSet(
        heading="Data Dictionary Information",
        description="Attributes useful to Data Dictionary.",
        aliases=["Data Dict", "Data Dictionary"],
        annotations={"wikilinks": ["[[Data Dictionary]]"]},
        formats=[COMMON_FORMATS_ALL],  # Reusing common formats and columns
        action=[ActionParameter(
            function="CollectionManager.find_collections",
            user_params=["search_string"],
            spec_params={"classification_name": "DataDictionary"},
        )]
    ),

    "Data Specification": FormatSet(
        heading="Data Specification Information",
        description="Attributes useful to Data Specification.",
        aliases=["Data Spec", "DataSpec", "DataSpecification"],
        annotations={"wikilinks": ["[[Data Specification]]"]},
        formats=[
            Format(types=["REPORT", "HTML"],columns=COMMON_COLUMNS + [Column(name="Mermaid", key='mermaid'),]),
            Format(types=["MERMAID"], columns=[
                Column(name="Display Name", key='display_name'),
                Column(name="Mermaid", key='mermaid'),
                ]),
            Format(types=["ALL"], columns=COMMON_COLUMNS)],  # Reusing common formats and columns
        action=[ActionParameter(
            function="CollectionManager.find_collections",
            user_params=["search_string"],
            spec_params={"classification_name": "DataSpec"},
        )]
    ),

    "DataStruct": FormatSet(
        heading="Data Structure Information",
        description="Attributes useful to Data Structures.",
        aliases=["Data Structure", "DataStructures", "Data Structures", "Data Struct", "DataStructure"],
        annotations={"wikilinks": ["[[Data Structure]]"]},
        formats=[Format(types=["ALL"], columns=COMMON_COLUMNS)],  # Reusing common formats and columns
        action=[ActionParameter(
            function="DataDesigner.find_data_structures",
            user_params=["search_string"],
            spec_params={},
        )]
    ),

    "DataField": FormatSet(
        heading="Data Structure Information",
        description="Attributes useful to Data Structures.",
        aliases=["Data Field", "Data Fields", "DataFields"],
        annotations={"wikilinks": ["[[Data Field]]"]},
        formats=[Format(types=["ALL"], columns=COMMON_COLUMNS)],  # Reusing common formats and columns
        action=[ActionParameter(
            function="DataDesigner.find_data_fields",
            user_params=["search_string"],
            spec_params={},
        )]
    ),

    "Mandy-DataStruct": FormatSet(
        heading="Puddy Approves",
        description="This is a tutorial on how to use a data struct description",
        aliases=[],
        annotations={"wikilinks": ["[[Data Structure]]"]},
        formats=[
            Format(types=["TABLE"], columns=COMMON_COLUMNS + [Column(name='GUID', key='GUID')]),
            Format(types=[ "DICT","LIST", ], columns=COMMON_COLUMNS + [Column(name='GUID', key='GUID')]),
            Format(types=["REPORT","MERMAID", "HTML"], columns=[Column(name='Display Name', key='display_name'),
                                               Column(name='Mermaid', key='mermaid'),]),
        ],
        action=[ActionParameter(
            function="DataDesigner.find_data_structures",
            user_params=["search_string"],
            spec_params={"output_format":"DICT"},
        )]
    ),

    "Governance Definitions": FormatSet(
        heading="Governance-Definitions Information",
        description="Attributes useful to Governance-Definitions.",
        aliases=["GovernanceDefinitions"],
        annotations={"wikilinks": ["[[Governance]]"]},
        formats=[Format(types=["ALL"], columns=GOVERNANCE_DEFINITIONS_COLUMNS)],
        action=[ActionParameter(
            function="GovernanceOfficer.find_governance_definitions",
            user_params=["search_filter"],
            spec_params={"output_format":"DICT"},
            )]
    ),
    })

def select_output_format_set(kind: str, output_type: str) -> dict | None:
    """
    This function retrieves the appropriate output set configuration dictionary based on the `kind` and `output_type`.
    If output_type = `ANY` that indicates this is just a test to see of the output format set exists.

    :param kind: The kind of output set (e.g., "Referenceable", "Collections").
    :param output_type: The desired output format type (e.g., "DICT", "LIST", "REPORT").
    :return: The matched output set dictionary or None if no match is found.

    Returns:
        dict | None: 
    """
    # Normalize the output type to uppercase for consistency
    output_type = output_type.upper()
    output_struct: dict = {}

    # Step 1: Check if `kind` exists in the `output_format_sets` dictionary
    element = output_format_sets.get(kind)

    # Step 2: If not found, attempt to match `kind` in aliases
    if element is None:
        for key, value in output_format_sets.items():
            aliases = value.aliases
            if kind in aliases:
                element = value
                break

    # Step 3: If still not found, return None
    if element is None:
        msg = f"No matching column set found for kind='{kind}' and output type='{output_type}'."
        logger.error(msg)
        return None
    else:
        # Convert FormatSet to dictionary for backward compatibility
        output_struct["aliases"] = element.aliases
        output_struct["heading"] = element.heading
        output_struct["description"] = element.description
        output_struct["annotations"] = element.annotations
        if element.action:
            # Convert ActionParameter to dictionary for backward compatibility
            output_struct["action"] = [action.dict() for action in element.action]

    # If this was just a validation that the format set could be found then the output type is ANY - so just return.
    if output_type == "ANY":
        return output_struct

    # Step 4: Search for a matching format in the `formats` list
    for format in element.formats:
        if output_type in format.types:
            # Convert Format to dictionary for backward compatibility
            output_struct["formats"] = format.dict()
            return output_struct

    # Step 5: Handle the fallback case of "ALL"
    for format in element.formats:
        if "ALL" in format.types:
            # Convert Format to dictionary for backward compatibility
            output_struct["formats"] = format.dict()
            return output_struct

    # Step 6: If no match is found, return None
    logger.error(f"No matching format found for kind='{kind}' with output type='{output_type}'.")
    return None

def output_format_set_list() -> list[str]:
    """
    Returns a list of all available format set names.
    
    Returns:
        list[str]: A list of format set names
    """
    return list(output_format_sets.keys())

def get_output_format_set_heading(format_set: str) -> str:
    """
    Gets the heading of a format set.
    
    Args:
        format_set: The name of the format set
        
    Returns:
        str: The heading of the format set
    """
    return output_format_sets[format_set].heading

def get_output_format_set_description(format_set: str) -> str:
    """
    Gets the description of a format set.
    
    Args:
        format_set: The name of the format set
        
    Returns:
        str: The description of the format set
    """
    return output_format_sets[format_set].description

def get_output_format_type_match(format_set: Union[dict, FormatSet], output_format: str) -> dict:
    """
    Matches a format set with a specific output format.
    
    Args:
        format_set: The format set to match, either a FormatSet instance or a dictionary
        output_format: The output format to match
        
    Returns:
        dict: The format set with the matching format
    """
    # Convert FormatSet to dictionary if needed
    if isinstance(format_set, FormatSet):
        format_set_dict = format_set.dict()
    else:
        format_set_dict = format_set
    
    # Handle the case where format_set is a list (legacy code)
    if isinstance(format_set_dict, list):
        for format in format_set_dict.get("formats", []):
            if output_format in format.get("types", []):
                format_set_dict["formats"] = format
                return format_set_dict

        # Handle the fallback case of "ALL"
        for format in format_set_dict.get("formats", []):
            if "ALL" in format.get("types", []):
                format_set_dict["formats"] = format
                return format_set_dict
    else:
        # Handle the case where format_set is a dictionary
        if "formats" in format_set_dict:
            formats = format_set_dict["formats"]
            if isinstance(formats, list):
                for format in formats:
                    if output_format in format.get("types", []):
                        format_set_dict["formats"] = format
                        return format_set_dict
                
                # Handle the fallback case of "ALL"
                for format in formats:
                    if "ALL" in format.get("types", []):
                        format_set_dict["formats"] = format
                        return format_set_dict
        else:
            # Handle the case where format_set is a dictionary from select_output_format_set with the "ANY" output type
            # In this case, we need to look up the format set by name and get the formats
            if "heading" in format_set_dict and "description" in format_set_dict:
                # Try to find the format set by heading
                for key, value in output_format_sets.items():
                    if value.heading == format_set_dict["heading"] and value.description == format_set_dict["description"]:
                        # Found the format set, now find the matching format
                        for format in value.formats:
                            if output_format in format.types:
                                format_set_dict["formats"] = format.dict()
                                return format_set_dict
                        
                        # Handle the fallback case of "ALL"
                        for format in value.formats:
                            if "ALL" in format.types:
                                format_set_dict["formats"] = format.dict()
                                return format_set_dict
    
    # If no match is found, return the original format set
    return format_set_dict

def save_output_format_sets(file_path: str, format_set_names: List[str] = None) -> None:
    """
    Save output format sets to a JSON file.
    
    This function allows saving all format sets or a subset of format sets to a JSON file.
    The saved format sets can later be loaded using the `load_output_format_sets` function.
    
    Args:
        file_path: The path to save the file to
        format_set_names: Optional list of format set names to save. If None, all format sets are saved.
    """
    if format_set_names is None:
        # Save all format sets
        output_format_sets.save_to_json(file_path)
        logger.info(f"All format sets saved to {file_path}")
    else:
        # Save only specified format sets
        subset = FormatSetDict()
        for name in format_set_names:
            format_set = output_format_sets.get(name)
            if format_set:
                subset[name] = format_set
            else:
                logger.warning(f"Format set '{name}' not found, skipping")
        
        if subset:
            subset.save_to_json(file_path)
            logger.info(f"Selected format sets saved to {file_path}")
        else:
            logger.warning(f"No valid format sets to save, file not created")

def load_output_format_sets(file_path: str, merge: bool = True) -> None:
    """
    Load output format sets from a JSON file.
    
    This function loads format sets from a JSON file and either merges them with the existing
    format sets or replaces the existing format sets.
    
    Args:
        file_path: The path to load the file from
        merge: If True, merge with existing format sets. If False, replace existing format sets.
    """
    global output_format_sets
    try:
        loaded_sets = FormatSetDict.load_from_json(file_path)
        
        if merge:
            # Merge with existing format sets
            for key, value in loaded_sets.items():
                output_format_sets[key] = value
            logger.info(f"Format sets from {file_path} merged with existing format sets")
        else:
            # Replace existing format sets
            output_format_sets = loaded_sets
            logger.info(f"Existing format sets replaced with format sets from {file_path}")
    except Exception as e:
        logger.error(f"Error loading format sets from {file_path}: {e}")
        raise

def load_user_format_sets() -> None:
    """
    Load all user-defined format sets from the user format sets directory.
    
    This function loads all JSON files in the user format sets directory and merges
    the format sets with the existing format sets.
    """
    if not os.path.exists(USER_FORMAT_SETS_DIR):
        logger.debug(f"User format sets directory {USER_FORMAT_SETS_DIR} does not exist")
        return
    
    # Load all JSON files in the directory
    for file_path in Path(USER_FORMAT_SETS_DIR).glob("*.json"):
        try:
            load_output_format_sets(str(file_path), merge=True)
        except Exception as e:
            logger.error(f"Error loading format sets from {file_path}: {e}")

# Load user-defined format sets at module initialization
try:
    load_user_format_sets()
except Exception as e:
    logger.error(f"Error loading user-defined format sets: {e}")