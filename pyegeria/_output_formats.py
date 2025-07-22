"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.
"""
import json

"""
# Purpose
pyegeria allows find and get requests to generate output in different output formats - 
including DICT, MD, FORM, REPORT, LIST, MERMAID, TABLE, and perhaps additional ones in the future.

Some of the formats, such as REPORT and LIST,  allow the user to filter which attributes to
display, and the order in which they appear. However, many, if not most users will likely not want to customize
the column list and so we need a sensible set of defaults for each type of output. These defaults are used 
by the find and get methods if the user doesn't provide a value for the columns parameter.

This file cotains these defaults and a function to return the the right default dict for a given type.

"""

output_sets = {
    "Referenceable" : {
        "heading": "Common Attributes",
        "description": "Attributes that apply to all Referenceables.",
        "annotations" : {},
        "columns": [
            {'name': 'Display Name', 'key': 'display_name'},
            {'name': 'Qualified Name', 'key': 'qualified_name', 'format': True},
            {'name': 'Version Identifier', 'key': 'version_identifier'},
            {'name': 'Description', 'key': 'description', 'format': True},
            {'name': "Category", 'key': 'category'},
            {'name': "Classifications", 'key': 'classifications'},
            {'name': "Additional Properties", 'key': 'additional_properties'},
            ],
        "formats": ["ALL"]
        },
    "Collections" : {
         "heading": "Common Collection Information",
         "description": "Attributes generic to all Collections.",
         "aliases": ["Collection", "RootCollection", "Folder", "ReferenceList", "HomeCollection",
                     "ResultSet", "RecentAccess", "WorkItemList", "Namespace"],
        "annotations": {"wikilinks": ["[[Collections]]"]},
         "columns": [
            {'name': 'Display Name', 'key': 'display_name'},
            {'name': 'Qualified Name', 'key': 'qualified_name', 'format': True},
            {'name': 'Category', 'key': 'category'},
            {'name': 'Description', 'key': 'description', 'format': True},
            {'name': "Classifications", 'key': 'classifications'},
            {'name': 'Members', 'key': 'members', 'format': True},
            ],
        "formats": ["ALL"]
        },
    "DigitalProducts" : {
        "heading": "Digital Product Information",
        "description": "Attributes useful to Digital Products.",
        "aliases": ["DataProducts"],
        "annotations": {},
        "columns": [
            {'name': 'Display Name', 'key': 'display_name'},
            {'name': 'Qualified Name', 'key': 'qualified_name', 'format': True},
            {'name': 'Category', 'key': 'category'},
            {'name': 'Description', 'key': 'description', 'format': True},
            {'name': "Status", 'key': 'status'},
            {'name': 'Product Name', 'key': 'product_name'},
            {'name': 'Identifier', 'key': 'identifier'},
            {'name': 'Maturity', 'key': 'maturity'},
            {'name': 'Service Life', 'key': 'service_life'},
            {'name': 'Next Version', 'key': 'next_version'},
            {'name': 'Withdraw Date', 'key': 'withdraw_date'},
            {'name': 'Members', 'key': 'members', 'format': True},
            ],
        "formats": ["REPORT"]
    },
    "Agreements": {
        "heading": "General Agreement Information",
        "description": "Attributes generic to all Agreements.",
        "aliases": ["DataSharingAgreement" ],
        "columns": [
            {'name': 'Name', 'key': 'display_name'},
            {'name': 'Qualified Name', 'key': 'qualified_name', 'format': True},
            {'name': 'Category', 'key': 'category'},
            {'name': 'Description', 'key': 'description', 'format': True},
            {'name': "Classifications", 'key': 'classifications'},
            {'name': 'Members', 'key': 'members', 'format': True},
            ],
        "formats": ["ALL"],
        "annotations": {"wikilinks": ["[[Agreements]]", "[[Egeria]]"]},
        },
    "DigitalSubscriptions": {
        "heading": "Digital Subscription Agreement Information",
        "description": "Attributes useful to Digital Subscriptions.",
        "annotations": {},
        "columns": [
            {'name': 'Display Name', 'key': 'display_name'},
            {'name': 'Qualified Name', 'key': 'qualified_name', 'format': True},
            # {'name': 'Category', 'key': 'category'},
            {'name': 'Description', 'key': 'description', 'format': True},
            {'name': "Status", 'key': 'status'},
            {'name': 'Version Identifier', 'key': 'version_identifier'},
            # {'name': 'Identifier', 'key': 'identifier'},
            {'name': 'Service Level', 'key': 'service_level'},
            {'name': 'Support Levels', 'key': 'support_levels'},
            {'name': 'Members', 'key': 'members', 'format': True},
            ],
        "formats": ["LIST"],
        }
    }
    # "Digital Products": {
    #     "description": "Attributes useful to Digital Products",
    #     "columns": [
    #         {'name': 'Name', 'key': 'display_name'},
    #         {'name': 'Qualified Name', 'key': 'qualified_name', 'format': True},
    #         {'name': 'Category', 'key': 'category'},
    #         {'name': 'Description', 'key': 'description', 'format': True},
    #         {'name': "Status", 'key': 'status'},
    #         {'name': 'Product Name', 'key': 'product_name'},
    #         {'name': 'Identifier', 'key': 'identifier'},
    #         {'name': 'Maturity', 'key': 'maturity'},
    #         {'name': 'Service Life', 'key': 'service_life'},
    #         {'name': 'Next Version', 'key': 'next_version'},
    #         {'name': 'Withdraw Date', 'key': 'withdraw_date'},
    #         {'name': 'Members', 'key': 'members', 'format': True},
    #         ],
    #     "formats": ["REPORT"]
    # }

def select_column_set(kind: str, format: str) -> dict | None:
    # Check if the kind exists in the output_sets dictionary
    format = format.upper()  # Normalize format to uppercase for consistency
    element = output_sets.get(kind, None)

    if element is None:
        # Try to find the kind within aliases if `kind` doesn't match the keys directly
        for key, value in output_sets.items():
            if "aliases" in value and kind in value["aliases"]:
                element = value
                break

    if element:
        # Check if the format is allowed
        if format in element.get("formats", []) or "ALL" in element.get("formats", []):
            return element

    # If no match is found, return None
    print(f"No matching column set found for kind='{kind}' and format='{format}'.")
    return None