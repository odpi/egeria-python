"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.
"""

"""
# Purpose
pyegeria allows find and get requests to generate output in different output formats - 
including DICT, MD, FORM, REPORT, LIST, MERMAID, TABLE, and perhaps additional ones in the future.

Some of the formats, such as REPORT and LIST,  allow the user to filter which attributes to
display, and the order in which they appear. However, many, if not most users will likely not want to customize
the column list and so we need a sensible set of defaults for each type of output. These defaults are used 
by the find and get methods if the user doesn't provide a value for the columns parameter.

This file contains these defaults and a function to return the the right default dict for a given type.

"""

# Define shared elements
COMMON_COLUMNS = [
    {'name': 'Display Name', 'key': 'display_name'},
    {'name': 'Qualified Name', 'key': 'qualified_name', 'format': True},
    {'name': 'Category', 'key': 'category'},
    {'name': 'Description', 'key': 'description', 'format': True},
]

COMMON_METADATA_COLUMNS = [
    {'name': 'GUID', 'key': 'guid', 'format': True},
    {'name': 'Metadata Collection ID', 'key': 'metadata_collection_id', 'format': True},
    {'name': 'Metadata Collection Name', 'key': 'metadata_collection_name', 'format': True},
]

COMMON_FORMATS_ALL = {
        "types": ["ALL"],
        "columns": COMMON_COLUMNS,
    }


COLLECTIONS_COLUMNS =  COMMON_COLUMNS + [
                        {'name': "Created By", 'key': 'created_by'},
                        {'name': "Create Time", 'key': 'create_time'},
                        {'name': "Updated By", 'key': 'updated_by'},
                        {'name': "Update Time", 'key': 'update_time'},
                    ]

COLLECTION_DICT = {
        "types": ["DICT"],
        "columns": COLLECTIONS_COLUMNS,
    }

COMMON_ANNOTATIONS = {
    "wikilinks": ["[[Commons]]"]
}

# Modularized output_format_sets
output_format_sets = {
    "Referenceable": {
        "heading": "Common Attributes",
        "description": "Attributes that apply to all Referenceables.",
        "annotations": {},  # No specific annotations
        "formats": [
            {
                "types": ["ALL"],
                "columns": COMMON_COLUMNS + COMMON_METADATA_COLUMNS + [
                    {'name': 'Version Identifier', 'key': 'version_identifier'},
                    {'name': "Classifications", 'key': 'classifications'},
                    {'name': "Additional Properties", 'key': 'additional_properties'},
                    {'name': "Created By", 'key': 'created_by'},
                    {'name': "Create Time", 'key': 'create_time'},
                    {'name': "Updated By", 'key': 'updated_by'},
                    {'name': "Update Time", 'key': 'update_time'},
                    {'name': "Effective From", 'key': 'effective_from'},
                    {'name': "Effective To", 'key': 'effective_to'},
                    {'name': "Version", 'key': 'version'},
                    {'name': "Open Metadata Type Name", 'key': 'type_name'},
                ],
            }
        ],
    },

    "Collections": {
        "heading": "Common Collection Information",
        "description": "Attributes generic to all Collections.",
        "aliases": ["Collection", "RootCollection", "Folder", "ReferenceList", "HomeCollection",
                    "ResultSet", "RecentAccess", "WorkItemList", "Namespace"],
        "annotations": COMMON_ANNOTATIONS,
        "formats": [COMMON_FORMATS_ALL, COLLECTION_DICT]  # Reusing common formats
    },

    "DigitalProducts": {
        "heading": "Digital Product Information",
        "description": "Attributes useful to Digital Products.",
        "aliases": ["DigitalProduct", "DataProducts"],
        "annotations": {},
        "formats": [
            {
                "types": ["REPORT"],
                "columns": COMMON_COLUMNS + [
                    {'name': "Status", 'key': 'status'},
                    {'name': 'Product Name', 'key': 'product_name'},
                    {'name': 'Identifier', 'key': 'identifier'},
                    {'name': 'Maturity', 'key': 'maturity'},
                    {'name': 'Service Life', 'key': 'service_life'},
                    {'name': 'Next Version', 'key': 'next_version'},
                    {'name': 'Withdraw Date', 'key': 'withdraw_date'},
                    {'name': 'Members', 'key': 'members', 'format': True},
                ],
            }
        ]
    },

    "Agreements": {
        "heading": "General Agreement Information",
        "description": "Attributes generic to all Agreements.",
        "aliases": ["DataSharingAgreement"],
        "annotations": {"wikilinks": ["[[Agreements]]", "[[Egeria]]"]},
        "formats": COMMON_FORMATS_ALL  # Reusing common formats and columns
    },

    "Data Dictionary": {
        "heading": "Data Dictionary Information",
        "description": "Attributes useful to Data Dictionary.",
        "aliases": ["Data Dict"],
        "annotations": {"wikilinks": ["[[Data Dictionary]]"]},
        "formats": COMMON_FORMATS_ALL  # Reusing common formats and columns
    },

    "Data Specification": {
        "heading": "Data Specification Information",
        "description": "Attributes useful to Data Specification.",
        "aliases": ["Data Spec"],
        "annotations": {"wikilinks": ["[[Data Specification]]"]},
        "formats": COMMON_FORMATS_ALL  # Reusing common formats and columns
    },
}


def select_output_format_set(kind: str, output_type: str) -> dict | None:
    """
    This function retrieves the appropriate output set configuration dictionary based on the `kind` and `output_type`.

    :param kind: The kind of output set (e.g., "Referenceable", "Collections").
    :param output_type: The desired output format type (e.g., "DICT", "LIST", "REPORT").
    :return: The matched output set dictionary or None if no match is found.

    Returns:
        dict | None: 
    """
    from loguru import logger
    from pyegeria.logging_configuration import config_logging

    config_logging()

    # Normalize the output type to uppercase for consistency
    output_type = output_type.upper()
    output_struct:dict = {}

    # Step 1: Check if `kind` exists in the `output_format_sets` dictionary
    element = output_format_sets.get(kind)

    # Step 2: If not found, attempt to match `kind` in aliases
    if element is None:
        for value in output_format_sets.values():
            aliases = value.get("aliases", [])
            if kind in aliases:
                element = value
                break


    # Step 3: If still not found, return None
    if element is None:
        msg = "No matching column set found for kind='{kind}' and output type='{output_type}'."
        logger.error(msg)
        return None
    else:
        output_struct["aliases"] = element.get("aliases", [])
        output_struct["heading"] = element.get("heading", [])
        output_struct["description"] = element.get("description", [])
        output_struct["annotations"] = element.get("annotations", {})

    # Step 4: Search for a matching format in the `formats` list
    for format in element.get("formats", []):
        if output_type in format.get("types", []):
            output_struct["formats"] = format
            return output_struct

    # Step 5: Handle the fallback case of "ALL"
    for format in element.get("formats", []):
        if "ALL" in format.get("types", []):
            output_struct["formats"] = format
            return output_struct

    # Step 6: If no match is found, return None
    logger.error(f"No matching format found for kind='{kind}' with output type='{output_type}'.")
    return None