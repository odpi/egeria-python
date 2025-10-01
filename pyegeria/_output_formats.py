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
    target_type="Example",
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
from typing import List, Union

from loguru import logger

from pyegeria._output_format_models import (Column, Format, ActionParameter, FormatSet, FormatSetDict)


# from pyegeria.config import settings

def combine_format_set_dicts(dict1: dict, dict2: dict) -> dict:
    """
    Combine two FormatSetDicts, merging their contents.

    Args:
        dict1 (dict): The first FormatSetDict.
        dict2 (dict): The second FormatSetDict.

    Returns:
        dict: A new dictionary combining both, with keys from dict2
              overwriting keys from dict1 in case of conflicts.
    """
    combined = dict1.copy()  # Start with dict1
    for key, value in dict2.items():
        if key in combined:
            if isinstance(combined[key], dict) and isinstance(value, dict):
                # Recursively merge if both values are dictionaries
                combined[key] = combine_format_set_dicts(combined[key], value)
            else:
                # Otherwise, overwrite with dict2's value.
                combined[key] = value
        else:
            # Key from dict2 doesn't exist in dict1, add it
            combined[key] = value
    return combined


# Get the configured value for the user format sets directory

# USER_FORMAT_SETS_DIR = os.path.expanduser(settings.Environment.pyegeria_user_format_sets_dir)
USER_FORMAT_SETS_DIR = os.getenv("PYEGERIA_USER_FORMAT_SETS_DIR", "./")
# Constants
MD_SEPARATOR = "\n---\n\n"

# Standard optional parameters for search functions
OPTIONAL_PARAMS = ["page_size", "start_from", "starts_with", "ends_with", "ignore_case"]

# Define shared elements
COMMON_COLUMNS = [
    Column(name='Display Name', key='display_name'),
    Column(name='Qualified Name', key='qualified_name', format=True),
    Column(name='Category', key='category'),
    Column(name='Description', key='description', format=True),
    Column(name='Status', key='status'),
]


COMMON_METADATA_COLUMNS = [
    Column(name='GUID', key='guid', format=True),
    Column(name='Type Name', key='type_name'),
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


MERMAID_FORMAT = Format(
    types = ["MERMAID"],
    columns = [Column(name='Mermaid', key='mermaid')]
)

EXT_REF_COLUMNS = COMMON_COLUMNS + [
    Column(name='Reference Title', key='reference_title'),
    Column(name='Reference Abstract', key='reference_abstract'),
    Column(name='Authors', key='authors'),
    Column(name='Organization', key='organization'),
    Column(name='Reference URL', key='reference_url'),
    Column(name='Sources', key='sources'),
    Column(name='License', key='license'),
    Column(name='Copyright', key='copyright'),
    Column(name='Attribution', key='attribution'),
]

PROJECT_COLUMNS = COMMON_COLUMNS + [
    Column(name="Classifications", key='classifications'),
    Column(name='Priority', key='priority'),
    Column(name='Project Status', key='project_status'),
    Column(name='Element Status', key='status'),
    Column(name='Start Date', key='start_date'),
    Column(name='Assigned Actors', key='assigned_actors'),
    Column(name='Resources', key='resource_list'),
    Column(name="Project Roles", key='project_roles'),
    Column(name="Managed Projects", key='managed_projects'),
]

GLOSSARY_COLUMNS = COMMON_COLUMNS + [
    Column(name="Language", key='language'),
    Column(name='Usage', key='usage'),
    Column(name='Folders', key='collection_members'),
]

COLLECTIONS_COLUMNS = COMMON_COLUMNS + [
    Column(name='Type Name', key='type_name'),
    Column(name='Classifications', key='classifications'),
    Column(name="Created By", key='created_by'),
    Column(name="Create Time", key='create_time'),
    Column(name="Updated By", key='updated_by'),
    Column(name="Update Time", key='update_time'),
]

COLLECTIONS_MEMBERS_COLUMNS = COLLECTIONS_COLUMNS + [
    Column(name="Containing Members", key='collection_members'),
    Column(name="Member Of", key='member_of_collections')
]

COLLECTION_DICT = Format(
    types=["DICT"],
    columns=COLLECTIONS_MEMBERS_COLUMNS + [
        Column(name="GUID", key='GUID'),
    ],
)

BASIC_COLLECTIONS_COLUMNS = [
    Column(name='Qualified Name', key='qualified_name', format=True),
    Column(name='GUID', key='guid', format=True),
    Column(name='Type Name', key='type_name'),
    Column(name="Containing Members", key='collection_members'),
    Column(name="Member Of", key='member_of_collections')
]

COLLECTION_REPORT = Format(
    types=["REPORT"],
    columns=COLLECTIONS_MEMBERS_COLUMNS + [
        Column(name="GUID", key='GUID'),
        Column(name="Mermaid", key='mermaid'),
    ],
)

COLLECTION_TABLE = Format(
    types=["TABLE"],
    columns=COLLECTIONS_MEMBERS_COLUMNS,
)

GOVERNANCE_DEFINITIONS_COLUMNS = COMMON_COLUMNS + [
    Column(name="Summary", key='summary'),
    Column(name="Usage", key='usage'),
    Column(name="Importance", key='importance'),
    Column(name="Scope", key='scope'),
    Column(name="Type", key='type_name'),
]
GOVERNANCE_DEFINITIONS_BASIC = [
    Column(name="Type", key='type_name'),
    Column(name="Summary", key='summary'),
    Column(name='Qualified Name', key='qualified_name', format=True),
    Column(name="GUID", key='guid', format=True),
]
COMMON_ANNOTATIONS = {
    "wikilinks": ["[[Commons]]"]
}

# Modularized output_format_sets
base_output_format_sets = FormatSetDict({
    "Default": FormatSet(
        heading="Default Base Attributes",
        description="Was a valid combination of output_format_set and output_format provided?",
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
    "Referenceable": FormatSet(
        target_type="Referenceable",
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
    "ExternalReference": FormatSet(
        target_type="External Reference",
        heading="External Reference Attributes",
        description="Attributes that apply to all External References.",
        annotations={},
        aliases=["ExternalDataSource", "ExternalModelSource", "External References"],
        formats=[
            Format(
                types=["ALL"],
                columns=EXT_REF_COLUMNS,
            )
        ],
        action=ActionParameter(
            function="ExternalReference.find_external_references",
            optional_params=OPTIONAL_PARAMS,
            required_params=["search_string"],
            spec_params={},
        )
    ),
    "RelatedMedia": FormatSet(
        target_type="Related Media",
        heading="Related Media Attributes",
        description="Attributes that apply to related media.",
        annotations={},
        formats=[
            Format(
                types=["ALL", "LIST"],
                columns=EXT_REF_COLUMNS + [
                    Column(name="Media Type", key='media_type'),
                    Column(name="Media Type Other Id", key='media_type_other_id'),
                    Column(name="Default Media Usage", key='default_media_usage'),
                    Column(name="Default Media Usage Other Id", key='default_media_usage_other_id')
                ],
            )
        ],
        action=ActionParameter(
            function="ExternalReference.find_external_references",
            optional_params=OPTIONAL_PARAMS,
            required_params=["search_string"],
            spec_params={"metadata_element_types": ["RelatedMedia"]},
        )

    ),
    "CitedDocument": FormatSet(
        target_type="Cited Document",
        heading="Cited Document Attributes",
        description="Attributes that apply to all Cited Documents.",
        annotations={},
        formats=[
            Format(
                types=["ALL", "LIST"],
                columns=EXT_REF_COLUMNS + [
                    Column(name="Number of Pages", key='number_of_pages'),
                    Column(name="Page Range", key='page_range'),
                    Column(name="Publication Series", key='publication_series'),
                    Column(name="Publication Series Volume", key='publication_series_volume'),
                    Column(name="Publisher", key='publisher'),
                    Column(name="Edition", key='edition'),
                    Column(name="First Publication Date", key='first_publication_date'),
                    Column(name="Publication Date", key='publication_date'),
                    Column(name="Publication City", key='publication_city'),
                    Column(name="Publication Year", key='publication_year'),
                    Column(name="Publication Numbers", key='publication_numbers'),
                ],
            )
        ],
        action=ActionParameter(
            function="ExternalReference.find_external_references",
            optional_params=OPTIONAL_PARAMS,
            required_params=["search_string"],
            spec_params={"metadata_element_types": ["CitedDocument"]},
        )

    ),
    "Projects": FormatSet(
        target_type="Project",
        heading="Project Attributes",
        description="Attributes that apply to all Projects.",
        annotations={},
        formats=[
            Format(
                types=["ALL", "LIST"],
                columns=PROJECT_COLUMNS
            )
        ],
        action=ActionParameter(
            function="ProjectManager.find_projects",
            optional_params=OPTIONAL_PARAMS,
            required_params=["search_string"],
            spec_params={},
        )

    ),
    "Glossaries": FormatSet(
        target_type="Glossary",
        heading="Glossary Attributes",
        description="Attributes that apply to all Glossaries.",
        annotations={"wikilinks": ["[[Glossaries]]"]},
        formats=[
            Format(
                types=["ALL"],
                columns=GLOSSARY_COLUMNS
            )
        ],
        action=ActionParameter(
            function="GlossaryManager.find_glossaries",
            optional_params=OPTIONAL_PARAMS,
            required_params=["search_string"],
            spec_params={},
        )
    ),
    "Terms": FormatSet(
        target_type="Term",
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
                    Column(name="Glossary", key='parent_glossary'),
                    Column(name="Subject Area", key='subject_area'),
                ],
            )
        ],
        action=ActionParameter(
            function="GlossaryManager.find_glossary_terms",
            required_params=["search_string"],
            optional_params=OPTIONAL_PARAMS,
            spec_params={},
        )
    ),
    "Help-Terms": FormatSet(
        target_type="Term",
        heading="Display Help for Dr.Egeria Commands",
        description="Designed for help output of Dr.Egeria commands.",
        annotations={"wikilinks": ["[[Help]]", "[[Dr.Egeria]]"]},
        formats=[
            Format(

                types=["DICT", "FORM", "REPORT", "LIST", "TABLE"],
                columns=[
                    Column(name='Term Name', key='display_name'),
                    Column(name='Description', key='description'),
                    Column(name="Usage", key='usage', format=True),
                    Column(name="Update Time", key='update_time')

                ],
            )
        ],
        action=ActionParameter(
            function="GlossaryManager.find_glossary_terms",
            required_params=["search_string"],
            optional_params=OPTIONAL_PARAMS,
            spec_params={},
        )
    ),

    "Collections": FormatSet(
        target_type="Collection",
        heading="Common Collection Information",
        description="Attributes generic to all Collections.",
        aliases=["Collection", "RootCollection", "Folder", "ReferenceList", "HomeCollection",
                 "ResultSet", "RecentAccess", "WorkItemList", "Namespace"],
        annotations=COMMON_ANNOTATIONS,
        formats=[MERMAID_FORMAT, COLLECTION_DICT, COLLECTION_TABLE, COLLECTION_REPORT, COMMON_FORMATS_ALL],  # Reusing common formats
        action=ActionParameter(
            function="CollectionManager.find_collections",
            required_params=["search_string"],
            optional_params=OPTIONAL_PARAMS,
            spec_params={},
        )
    ),
    "BasicCollections": FormatSet(
        target_type="Collection",
        heading="Common Collection Information",
        description="Attributes generic to all Collections.",
        aliases=[],
        annotations=COMMON_ANNOTATIONS,
        formats=[Format(
            types=["ALL"],
            columns=BASIC_COLLECTIONS_COLUMNS,
        )],  # Reusing common formats
        action=ActionParameter(
            function="CollectionManager.find_collections",
            required_params=["search_string"],
            optional_params=OPTIONAL_PARAMS,
            spec_params={},
        )
    ),
    "Folders": FormatSet(
        target_type="Folder",
        heading="Common Folder Information",
        description="Attributes generic to all Folders.",
        aliases=[],
        annotations=COMMON_ANNOTATIONS,
        formats=[Format(
            types=["ALL"],
            columns=BASIC_COLLECTIONS_COLUMNS,
        )],  # Reusing common formats
        action=ActionParameter(
            function="CollectionManager.find_collections",
            required_params=["search_string"],
            optional_params=OPTIONAL_PARAMS,
            spec_params={"classification_names": ["Folder"]},
        )
    ),

    "Collection Members": FormatSet(
        target_type="Collection",
        heading="Collection Membership Information",
        description="Attributes about all CollectionMembers.",
        aliases=["CollectionMember", "Member", "Members"],
        annotations={"wikilinks": ["[[CollectionMembers]]"]},
        formats=[COLLECTION_DICT, COLLECTION_TABLE],
        action=ActionParameter(
            function="CollectionManager.get_collection_members",
            required_params=["collection_guid"],
            optional_params=OPTIONAL_PARAMS,
            spec_params={"output_format": "DICT"},
        )
    ),
    "Digital-Product-Catalog": FormatSet(
        target_type="DigitalProductCatalog",
        heading="Catalogs for Digital Products",
        description="Attributes generic to all Digital Product Catalogs..",
        aliases=["Product Catalog", "DataProductCatalog"],
        annotations={"Wikilinks": ["[[Digital Products]]"]},
        formats=[
            Format(
                types=["DICT", "TABLE", "LIST", "MD", "FORM"],
                columns=COLLECTIONS_MEMBERS_COLUMNS
            ),
            Format(
                types=["REPORT", "HTML"],
                columns=COLLECTIONS_MEMBERS_COLUMNS + [
                    Column(name="GUID", key='GUID'),
                    Column(name="Mermaid", key='mermaid'),
                ]),
            Format(
                types=["MERMAID"],
                columns= [
                    Column(name="Mermaid", key='mermaid'),
                ])
        ],
        action=ActionParameter(
            function="CollectionManager.find_collections",
            required_params=["search_string"],
            optional_params=OPTIONAL_PARAMS,
            spec_params={"metadata_element_types": ["DigitalProductCatalog"]},
        ),
    ),

    "Digital-Products": FormatSet(
        target_type="DigitalProduct",
        heading="Digital Product Information",
        description="Attributes useful to Digital Products.",
        aliases=["DigitalProduct", "DataProducts"],
        annotations={},
        formats=[
            Format(
                types=["FORM", "DICT", "TABLE", "LIST"],
                columns=COMMON_COLUMNS + [
                    Column(name="Status", key='status'),
                    Column(name='Product Name', key='product_name'),
                    Column(name='Identifier', key='identifier'),
                    Column(name='Maturity', key='maturity'),
                    Column(name='Service Life', key='service_life'),
                    Column(name='Next Version', key='next_version'),
                    Column(name='Withdraw Date', key='withdraw_date'),
                    Column(name='Members', key='members', format=True),
                    Column(name='Uses Products', key='uses_digital_products'),
                    Column(name='Used by Products', key='used_by_digital_products'),
                    Column(name='Product Manager', key='assigned_actors'),
                    Column(name='License', key='governed_by'),
                    Column(name='Solution Blueprint', key='solution_designs'),
                ]),
            Format(
                types=[ "REPORT", "HTML"],
                columns=COMMON_COLUMNS + [
                    Column(name="Status", key='status'),
                    Column(name='Product Name', key='product_name'),
                    Column(name='Identifier', key='identifier'),
                    Column(name='Maturity', key='maturity'),
                    Column(name='Service Life', key='service_life'),
                    Column(name='Next Version', key='next_version'),
                    Column(name='Withdraw Date', key='withdraw_date'),
                    Column(name='Members', key='members', format=True),
                    Column(name='Uses Products', key='uses_digital_products'),
                    Column(name='Used by Products', key='used_by_digital_products'),
                    Column(name='Product Manager', key='assigned_actors'),
                    Column(name='License', key='governed_by'),
                    Column(name='Solution Blueprint', key='solution_designs'),
                    Column(name="Mermaid",key = "mermaid")
                ],
            )
        ],
        action=ActionParameter(
            function="CollectionManager.find_collections",
            required_params=["search_string"],
            optional_params=OPTIONAL_PARAMS,
            spec_params={"metadata_element_types": ["DigitalProduct"]},
        ),
        get_additional_props=ActionParameter(
            function="CollectionManager._extract_digital_product_properties",
            required_params=[],
            spec_params={},
        )
    ),

    "Agreements": FormatSet(
        target_type="Agreement",
        heading="General Agreement Information",
        description="Attributes generic to all Agreements.",
        aliases=["DataSharingAgreement", "Agreement", "Subscriptions"],
        annotations={"wikilinks": ["[[Agreements]]", "[[Egeria]]"]},
        formats=[
            Format(
                types=["REPORT", "DICT", "TABLE", "LIST", "FORM"],
                columns=COMMON_COLUMNS + COMMON_HEADER_COLUMNS + [
                    Column(name='Identifier', key='identifier'),
                    Column(name='Support Level', key='support_level'),
                    Column(name='service Levels', key='service_levels'),
                    Column(name='Agreement Items', key='agreement_items', format=True),
                    Column(name='Members', key='members', format=True),
                ]
            )
        ],
        action=ActionParameter(
            function="CollectionManager.find_collections",
            required_params=["search_string"],
            spec_params={"metadata_element_types": ["Agreement"]},
            # spec_params={},
        ),
        get_additional_props=ActionParameter(
            function="CollectionManager._extract_agreement_properties",
            required_params=[],
            spec_params={},
        ),
    ),

    "Data Dictionary": FormatSet(
        target_type="Data Dictionary",
        heading="Data Dictionary Information",
        description="Attributes useful to Data Dictionary.",
        aliases=["Data Dict", "Data Dictionary"],
        annotations={"wikilinks": ["[[Data Dictionary]]"]},
        formats=[COMMON_FORMATS_ALL],  # Reusing common formats and columns
        action=ActionParameter(
            function="CollectionManager.find_collections",
            required_params=["search_string"],
            spec_params={"metadata_element_types": ["DataDictionary"]},
        )
    ),

    "Data Specification": FormatSet(
        target_type="Data Specification",
        heading="Data Specification Information",
        description="Attributes useful to Data Specification.",
        aliases=["Data Spec", "DataSpec", "DataSpecification"],
        annotations={"wikilinks": ["[[Data Specification]]"]},
        formats=[
            Format(types=["REPORT", "HTML"], columns=COMMON_COLUMNS + [Column(name="Mermaid", key='mermaid'), ]),
            Format(types=["MERMAID"], columns=[
                Column(name="Display Name", key='display_name'),
                Column(name="Mermaid", key='mermaid'),
            ]),
            Format(types=["ALL"], columns=COMMON_COLUMNS)],  # Reusing common formats and columns
        action=ActionParameter(
            function="CollectionManager.find_collections",
            required_params=["search_string"],
            spec_params={"metadata_element_types": ["DdataSpec"]},
        )
    ),

    "Data Structures": FormatSet(
        target_type="Data Structure",
        heading="Data Structure Information",
        description="Attributes useful to Data Structures.",
        aliases=["Data Structure", "DataStructures", "Data Structures", "Data Struct", "DataStructure"],
        annotations={"wikilinks": ["[[Data Structure]]"]},
        formats=[Format(types=["FORM", "DICT", "LIST"], columns=COMMON_COLUMNS +
                                               [
                                                   Column(name="In Data Specifications", key='in_data_spec'),
                                                   Column(name="In Data Dictionaries", key='in_data_dictionary'),
                                                   Column(name="Member Data Fields", key='member_data_fields')                                               ]
                        ),  # Reusing common formats and columns
                Format(types=["REPORT"], columns=COMMON_COLUMNS +
                                               [
                                                   Column(name="In Data Specifications", key='in_data_spec'),
                                                   Column(name="In Data Dictionaries", key='in_data_dictionary'),
                                                   Column(name="Member Data Fields", key='member_data_fields'),
                                                   Column(name="Mermaid", key='mermaid')
                                               ]
                        )],
        action=ActionParameter(
            function="DataDesigner.find_data_structures",
            required_params=["search_string"],
            spec_params={},
        )
    ),

    "Data Fields": FormatSet(
        target_type="Data Field",
        heading="Data Structure Information",
        description="Attributes useful to Data Structures.",
        aliases=["Data Field", "Data Fields", "DataFields"],
        annotations={"wikilinks": ["[[Data Field]]"]},
        formats=[Format(types=["MD", "FORM", "DICT"], columns=COMMON_COLUMNS + [
                                                        Column(name="In Data Dictionaries", key='in_data_dictionary'),
                                                        Column(name="In Data Structure", key='in_data_structure')]),
                 Format(types=["REPORT"], columns=COMMON_COLUMNS +
                                                  [
                                                      Column(name="In Data Structure", key='in_data_structure'),
                                                      Column(name="In Data Dictionaries", key='in_data_dictionary'),
                                                      Column(name="Member Data Fields", key='member_data_fields'),
                                                      Column(name="Mermaid", key='mermaid')
                                                  ]
                        )],

        action=ActionParameter(
            function="DataDesigner.find_data_fields",
            required_params=["search_string"],
            spec_params={},
        )
    ),
    'External-Reference': FormatSet(target_type='External-Reference',
                                    heading='External-Reference Attributes',
                                    description='External References', formats=[
            Format(types=['MD', 'FORM', 'DICT'], columns=[Column(name='Display Name', key='display_name'),
                                                          Column(name='Description', key='description'),
                                                          Column(name='Category', key='category'),
                                                          Column(name='Reference Title', key='reference_title'),
                                                          Column(name='Reference Abstract', key='reference_abstract'),
                                                          Column(name='Authors', key='authors'),
                                                          Column(name='Organization', key='organization'),
                                                          Column(name='URL', key='reference_url'),
                                                          Column(name='Sources', key='reference_sources'),
                                                          Column(name='License', key='license'),
                                                          Column(name='Copyright', key='copyright'),
                                                          Column(name='Number of Pages', key='number_of_pages'),
                                                          Column(name='Page Range', key='page_range'),
                                                          Column(name='Publication Series', key='publication_series'),
                                                          Column(name='Publication Series Volume',
                                                                 key='pub_series_volume'),
                                                          Column(name='Publisher', key='publisher'),
                                                          Column(name='First Publication Date', key='first_pub_date'),
                                                          Column(name='Publication Date', key='pub_date'),
                                                          Column(name='Publication City', key='pub_city'),
                                                          Column(name='Publication Year', key='pub_year'),
                                                          Column(name='Publication Numbers', key='pub_numbers'),
                                                          Column(name='Version Identifier', key='current_version'),
                                                          Column(name='Classifications', key='classifications'),
                                                          Column(name='Qualified Name', key='qualified_name'),
                                                          Column(name='GUID', key='guid')]),
            Format(types=['TABLE','LIST'], columns=[Column(name='Display Name', key='display_name'),

                                             Column(name='Category', key='category'),
                                             Column(name='Reference Title', key='reference_title'),

                                             Column(name='Sources', key='reference_sources'),
                                             Column(name='License', key='license'),
                                             Column(name='Qualified Name', key='qualified_name'),
                                             ]),
            Format(types=["REPORT"], columns=[Column(name='Display Name', key='display_name'),
                                              Column(name='Description', key='description'),
                                              Column(name='Category', key='category'),
                                              Column(name='Reference Title', key='reference_title'),
                                              Column(name='Reference Abstract', key='reference_abstract'),
                                              Column(name='Organization', key='organization'),
                                              Column(name='URL', key='reference_url'),
                                              Column(name='Sources', key='reference_sources'),
                                              Column(name='License', key='license'),
                                              Column(name='Qualified Name', key='qualified_name'),
                                              Column(name='Mermaid', key='mermaid'),
                                              ]),

            Format(types=["MERMAID"], columns=[Column(name='Mermaid', key='mermaid')]),
        ],
                                    action=ActionParameter(function='ExternalReference.find_external_references',
                                                           required_params=['search_string'],
                                                           optional_params=['page_size', 'start_from',
                                                                            'starts_with', 'ends_with',
                                                                            'ignore_case'], spec_params={
                                            'metadata_element_types': ['ExternalReference']})),

    "Mandy-DataStruct": FormatSet(
        target_type="Data Structure",
        heading="Puddy Approves",
        description="This is a tutorial on how to use a data struct description",
        aliases=[],
        annotations={"wikilinks": ["[[Data Structure]]"]},
        formats=[
            Format(types=["TABLE"], columns=COMMON_COLUMNS + [Column(name='GUID', key='GUID')]),
            Format(types=["DICT", "LIST", ], columns=COMMON_COLUMNS + [Column(name='GUID', key='GUID')]),
            Format(types=["REPORT", "MERMAID", "HTML"], columns=[Column(name='Display Name', key='display_name'),
                                                                 Column(name='Mermaid', key='mermaid'), ]),
        ],
        action=ActionParameter(
            function="DataDesigner.find_data_structures",
            required_params=["search_string"],
            spec_params={"output_format": "DICT"},
        )
    ),
    "DataStruct-DrE": FormatSet(
        target_type="Data Structure",
        heading="Data Structure Information",
        description="Information used with Dr. Egeria to describe Data Structures.",
        aliases=[],
        annotations={"wikilinks": ["[[Data Structure]]"]},
        formats=[
            Format(types=["TABLE", "LIST"], columns=COMMON_COLUMNS + [
                Column(name='Namespace', key='namespace'),
                Column(name='In Data Specifications', key='member_of_data_spec_qnames'),
                Column(name='In Data Dictionary', key='member_of_data_dicts_qnames'),
                Column(name='Data Fields', key='containsDataFields'),
                Column(name='Glossary Term', key='glossary_term'),
            ]),
            Format(types=["DICT", "MD"], columns=COMMON_COLUMNS + [
                Column(name='Namespace', key='namespace'),
                Column(name='In Data Specifications', key='member_of_data_spec_qnames'),
                Column(name='In Data Dictionary', key='member_of_data_dicts_qnames'),
                Column(name='Glossary Term', key='glossary_term'),
                Column(name='GUID', key='GUID')]),
            Format(types=["REPORT", "MERMAID", "HTML"], columns=COMMON_COLUMNS + [
                Column(name='Namespace', key='namespace'),
                Column(name='In Data Specifications', key='member_of_data_spec_qnames'),
                Column(name='In Data Dictionary', key='member_of_data_dicts_qnames'),
                Column(name='Glossary Term', key='glossary_term'),
                Column(name='Mermaid', key='mermaid'),
                Column(name='GUID', key='GUID')])
        ],
        action=ActionParameter(
            function="DataDesigner.find_data_structures",
            required_params=["search_string"],
            spec_params={"output_format": "DICT"},
        )
    ),
    "Governance Basics": FormatSet(
        target_type="Governance Definition",
        heading="Basic Governance-Definitions Information",
        description="Core Attributes useful to Governance-Definitions.",
        aliases=["BasicGovernance"],
        annotations={"wikilinks": ["[[Governance]]"]},
        formats=[Format(types=["ALL"], columns=GOVERNANCE_DEFINITIONS_BASIC)],
        action=ActionParameter(
            function="GovernanceOfficer.find_governance_definitions",
            required_params=["search_string"],
            spec_params={},
        )
    ),
    "Governance Definitions": FormatSet(
        target_type="Governance Definition",
        heading="Governance-Definitions Information",
        description="Attributes useful to Governance-Definitions.",
        aliases=["GovernanceDefinitions"],
        annotations={"wikilinks": ["[[Governance]]"]},
        formats=[Format(types=["ALL"], columns=GOVERNANCE_DEFINITIONS_COLUMNS)],
        action=ActionParameter(
            function="GovernanceOfficer.find_governance_definitions",
            required_params=["search_string"],
            spec_params={},
        )
    ),
    "Governance Def": FormatSet(
        target_type="Governance Definition",
        heading="Governance-Definitions Information",
        description="Attributes useful to Governance-Definitions.",
        aliases=["GovernanceDefinitions"],
        annotations={"wikilinks": ["[[Governance]]"]},
        formats=[Format(types=["ALL"], columns=GOVERNANCE_DEFINITIONS_BASIC)],
        action=ActionParameter(
            function="GovernanceOfficer.find_governance_definitions",
            required_params=["search_string"],
            spec_params={"metadata_element_types": ["GovernancePrinciple", "GovernanceStrategy", "GovernanceResponse"]},
        )
    ),
    'Governance-Control': FormatSet(target_type='Governance Control', heading='Control Attributes',
                                    description= 'Governance Control (Create).', formats=[
            Format(types=['DICT', 'MD', 'FORM', 'REPORT'],
                   columns=[Column(name='Display Name', key='display_name'), Column(name='Summary', key='summary'),
                            Column(name='Description', key='description'), Column(name='Category', key='category'),
                            Column(name='Domain Identifier', key='domain_identifier'),
                            Column(name='Identifier', key='identifier'),
                            Column(name='Version Identifier', key='version_identifier'),
                            Column(name='Usage', key='usage'), Column(name='Scope', key='scope'),
                            Column(name='Importance', key='importance'), Column(name='measurement', key='measurement'),
                            Column(name='target', key='target'), Column(name='Implications', key='implications'),
                            Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'),
                            Column(name='Status', key='element_status'),
                            Column(name='User Defined Status', key='user_defined_status'),
                            Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid')
                            ]),
            Format(types=['TABLE', 'LIST'],
                   columns=[Column(name='Display Name', key='display_name'),
                            Column(name='Summary', key='summary'),
                            Column(name='Category', key='category'),
                            Column(name='Identifier', key='identifier'),
                            Column(name='Usage', key='usage'),
                            Column(name='Status', key='element_status'),
                            Column(name='Qualified Name', key='qualified_name'),
                            ])
        ],
            action=ActionParameter(
                function="GovernanceOfficer.find_governance_definitions",
                required_params=["search_string"],
                optional_params=OPTIONAL_PARAMS,
                spec_params={"metadata_element_types": ["GovernanceControl"]},
            )
    ),
    "Valid-Value-Def": FormatSet(
        target_type="Valid Value Definition",
        heading="Valid Value Definitions Information",
        description="Attributes useful to Valid Value Definitions.",
        aliases=[],
        annotations={"wikilinks": ["[[VV-Def]]"]},
        formats=[Format(types=["ALL"], columns=COMMON_COLUMNS +
                                               [Column(name='Data Type', key='data_type'),
                                                Column(name='Preferred Value', key='preferred_value'),
                                                Column(name='Usage', key='usage'),
                                                Column(name='Scope', key='scope'),
                                        ])
                 ],
        action=ActionParameter(
            function="reference_data.find_valid_value_definitions",
            required_params=["search_string"],
            spec_params={},
        )
    ),

    'License-Type': FormatSet(target_type='License Type', heading='License Type Attributes',
                                    description='Attributes of a License type.', formats=[
            Format(types=['DICT', 'MD', 'FORM', 'REPORT'],
                   columns=[Column(name='Display Name', key='display_name'), Column(name='Summary', key='summary'),
                            Column(name='Description', key='description'), Column(name='Category', key='category'),
                            Column(name='Domain Identifier', key='domain_identifier'),
                            Column(name='Identifier', key='identifier'),
                            Column(name='Version Identifier', key='version_identifier'),
                            Column(name='Usage', key='usage'), Column(name='Scope', key='scope'),
                            Column(name='Importance', key='importance'), Column(name='measurement', key='measurement'),
                            Column(name='target', key='target'), Column(name='Implications', key='implications'),
                            Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'),
                            Column(name='Status', key='element_status'),
                            Column(name='User Defined Status', key='user_defined_status'),
                            Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid')
                            ]),
            Format(types=['TABLE', 'LIST'],
                   columns=[Column(name='Display Name', key='display_name'),
                            Column(name='Summary', key='summary'),
                            Column(name='Category', key='category'),
                            Column(name='Identifier', key='identifier'),
                            Column(name='Usage', key='usage'),
                            Column(name='Status', key='element_status'),
                            Column(name='Qualified Name', key='qualified_name'),
                            ])
        ],
            action=ActionParameter(
                function="GovernanceOfficer.find_governance_definitions",
                required_params=["search_string"],
                optional_params=OPTIONAL_PARAMS,
                spec_params={"metadata_element_types": ["LicenseType"]},
            )
            ),

    "Governance Policies": FormatSet(
        target_type="GovernancePolicy",
        heading="Governance-Definitions Information",
        description="Attributes useful to Governance-Definitions.",
        aliases=["GovernanceDefinitions"],
        annotations={"wikilinks": ["[[Governance]]"]},
        formats=[Format(types=["ALL"], columns=GOVERNANCE_DEFINITIONS_COLUMNS)],
        action=ActionParameter(
            function="GovernanceOfficer.find_governance_definitions",
            required_params=["search_string"],
            optional_params=OPTIONAL_PARAMS,
            spec_params={"metadata_element_types": ["GovernancePolicy"]},
        )
    )

}
)

generated_format_sets = FormatSetDict({
    'Agreement-DrE': FormatSet(target_type='Agreement-DrE', heading='Agreement-DrE Attributes',
                               description='Auto-generated format for Agreement (Create).', formats=[
            Format(types=['ALL'], columns=[Column(name='Display Name', key='display_name'),
                                           Column(name='Description', key='description'),
                                           Column(name='Identifier', key='agreement_identifier'),
                                           Column(name='Category', key='category'),
                                           Column(name='Status', key='element_status'),
                                           Column(name='User Defined Status', key='user_defined_status'),
                                           Column(name='Version Identifier', key='version_identifier'),
                                           Column(name='Agreement Actors', key='agreement_actors'),
                                           Column(name='Qualified Name', key='qualified_name'),
                                           Column(name='GUID', key='guid')])],
                               action=ActionParameter(function='CollectionManager.find_collections',
                                                      required_params=['search_string'],
                                                      optional_params=['page_size', 'start_from', 'starts_with',
                                                                       'ends_with', 'ignore_case'],
                                                      spec_params={'metadata_element_types': ['Agreement']})),
    'Business-Imperative-DrE': FormatSet(target_type='Business-Imperative-DrE',
                                         heading='Business-Imperative-DrE Attributes',
                                         description='Auto-generated format for Business Imperative (Create).',
                                         formats=[Format(types=['ALL'],
                                                         columns=[Column(name='Display Name', key='display_name'),
                                                                  Column(name='Summary', key='summary'),
                                                                  Column(name='Description', key='description'),
                                                                  Column(name='Category', key='category'),
                                                                  Column(name='Domain Identifier',
                                                                         key='domain_identifier'),
                                                                  Column(name='Identifier', key='identifier'),
                                                                  Column(name='Version Identifier',
                                                                         key='version_identifier'),
                                                                  Column(name='Usage', key='usage'),
                                                                  Column(name='Scope', key='scope'),
                                                                  Column(name='Importance', key='importance'),
                                                                  Column(name='Implications', key='implications'),
                                                                  Column(name='Outcomes', key='outcomes'),
                                                                  Column(name='Results', key='results'),
                                                                  Column(name='Status', key='element_status'),
                                                                  Column(name='User Defined Status',
                                                                         key='user_defined_status'),
                                                                  Column(name='Qualified Name', key='qualified_name'),
                                                                  Column(name='GUID', key='guid')])],
                                         action=ActionParameter(
                                             function='GovernanceOfficer.find_governance_definitions',
                                             required_params=['search_string'],
                                             optional_params=['page_size', 'start_from', 'starts_with', 'ends_with',
                                                              'ignore_case'],
                                             spec_params={'metadata_element_types': ['GovernanceDriver']})),
    'Campaign-DrE': FormatSet(target_type='Campaign-DrE', heading='Campaign-DrE Attributes',
                              description='Auto-generated format for Campaign (Create).',
                              formats=[Format(types=['ALL'],
                                              columns=[
                                                  Column(
                                                      name='Display Name',
                                                      key='display_name'),
                                                  Column(
                                                      name='Description',
                                                      key='description'),
                                                  Column(
                                                      name='Project Type',
                                                      key='project_type'),
                                                  Column(
                                                      name='Category',
                                                      key='category'),
                                                  Column(
                                                      name='Identifier',
                                                      key='project_identifier'),
                                                  Column(
                                                      name='Mission',
                                                      key='mission'),
                                                  Column(
                                                      name='Purposes',
                                                      key='purposes'),
                                                  Column(
                                                      name='Start Date',
                                                      key='start_date'),
                                                  Column(
                                                      name='Planned End Date',
                                                      key='end_date'),
                                                  Column(
                                                      name='Priority',
                                                      key='priority'),
                                                  Column(
                                                      name='Project Phase',
                                                      key='project_phase'),
                                                  Column(
                                                      name='Project Status',
                                                      key='project_status'),
                                                  Column(
                                                      name='Project Health',
                                                      key='project_health'),
                                                  Column(
                                                      name='Qualified Name',
                                                      key='qualified_name'),
                                                  Column(
                                                      name='GUID',
                                                      key='guid')])],
                              action=ActionParameter(function='ProjectManager.find_projects',
                                                     required_params=['search_string'],
                                                     optional_params=['page_size', 'start_from', 'starts_with',
                                                                      'ends_with', 'ignore_case'],
                                                     spec_params={'classification_names': ['Campaign']})),
    'Certification-Type-DrE': FormatSet(target_type='Certification-Type-DrE',
                                        heading='Certification-Type-DrE Attributes',
                                        description='Auto-generated format for Certification Type (Create).', formats=[
            Format(types=['ALL'],
                   columns=[Column(name='Display Name', key='display_name'), Column(name='Summary', key='summary'),
                            Column(name='Description', key='description'), Column(name='Category', key='category'),
                            Column(name='Domain Identifier', key='domain_identifier'),
                            Column(name='Document Identifier', key='document_identifier'),
                            Column(name='Version Identifier', key='version_identifier'),
                            Column(name='Scope', key='scope'), Column(name='Importance', key='importance'),
                            Column(name='Details', key='details'), Column(name='Implications', key='implications'),
                            Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'),
                            Column(name='Status', key='element_status'),
                            Column(name='User Defined Status', key='user_defined_status'),
                            Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid')])],
                                        action=ActionParameter(function='GovernanceOfficer.find_governance_definitions',
                                                               required_params=['search_string'],
                                                               optional_params=['page_size', 'start_from',
                                                                                'starts_with', 'ends_with',
                                                                                'ignore_case'], spec_params={
                                                'metadata_element_types': ['CertificationTYpe']})),
    'Collection-DrE': FormatSet(target_type='Collection-DrE', heading='Collection-DrE Attributes',
                                description='Auto-generated format for Collection (Create).', formats=[
            Format(types=['ALL'], columns=[Column(name='Display Name', key='display_name'),
                                           Column(name='Description', key='description'),
                                           Column(name='Classifications', key='classifications'),
                                           Column(name='Category', key='category'),
                                           Column(name='Version Identifier', key='current_version'),
                                           Column(name='Qualified Name', key='qualified_name'),
                                           Column(name='GUID', key='guid')])],
                                action=ActionParameter(function='CollectionManager.find_collections',
                                                       required_params=['search_string'],
                                                       optional_params=['page_size', 'start_from', 'starts_with',
                                                                        'ends_with', 'ignore_case'])),
    'Data-Class-DrE': FormatSet(target_type='Data-Class-DrE', heading='Data-Class-DrE Attributes',
                                description='Auto-generated format for Data Class (Create).', formats=[
            Format(types=['ALL'], columns=[Column(name='Display Name', key='display_name'),
                                           Column(name='Description', key='description'),
                                           Column(name='Category', key='category'),
                                           Column(name='Status', key='element_status'),
                                           Column(name='Namespace', key='namespace'),
                                           Column(name='Match Property Names', key='match_property_names'),
                                           Column(name='Match Threshold', key='match_threshold'),
                                           Column(name='IsCaseSensitive', key='is_case_sensitive'),
                                           Column(name='Data Type', key='data_type'),
                                           Column(name='Allow Duplicate Values', key='duplicates_allowed'),
                                           Column(name='isNullable', key='is_nullable'),
                                           Column(name='Default Value', key='default_value'),
                                           Column(name='Average Value', key='avg_value'),
                                           Column(name='Value List', key='value_list'),
                                           Column(name='Value Range From', key='value_range_from'),
                                           Column(name='Value Range To', key='value_range_to'),
                                           Column(name='Sample Values', key='sample_values'),
                                           Column(name='Data Patterns', key='data_patterns'),
                                           Column(name='In Data Dictionary', key='in_data_dictionary'),
                                           Column(name='Containing Data Class', key='containing_data_class'),
                                           Column(name='Specializes Data Class', key='specializes_data_class'),
                                           Column(name='Qualified Name', key='qualified_name'),
                                           Column(name='GUID', key='guid')])],
                                action=ActionParameter(function='DataDesigner.find_data_classes',
                                                       required_params=['search_string'],
                                                       optional_params=['page_size', 'start_from', 'starts_with',
                                                                        'ends_with', 'ignore_case'])),
    'Data-Dictionary-DrE': FormatSet(target_type='Data-Dictionary-DrE', heading='Data-Dictionary-DrE Attributes',
                                     description='Auto-generated format for Data Dictionary (Create).', formats=[
            Format(types=['ALL'], columns=[Column(name='Display Name', key='display_name'),
                                           Column(name='Description', key='description'),
                                           Column(name='Category', key='category'),
                                           Column(name='Qualified Name', key='qualified_name'),
                                           Column(name='GUID', key='guid')])],
                                     action=ActionParameter(function='CollectionManager.find_collections',
                                                            required_params=['search_string'],
                                                            optional_params=['page_size', 'start_from', 'starts_with',
                                                                             'ends_with', 'ignore_case'], spec_params={
                                             'metadata_element_types': ['DataDictionary']})),
    'Data-Field-DrE': FormatSet(target_type='Data-Field-DrE', heading='Data-Field-DrE Attributes',
                                description='Auto-generated format for Data Field (Create).', formats=[
            Format(types=['ALL', 'MD'], columns=[Column(name='Display Name', key='display_name'),
                                           Column(name='Description', key='description'),
                                           Column(name='Category', key='category'),
                                           Column(name='Status', key='element_status'),
                                           Column(name='Data Type', key='data_type'),
                                           Column(name='Position', key='position'),
                                           Column(name='Minimum Cardinality', key='min_cardinality'),
                                           Column(name='Maximum Cardinality', key='max_cardinality'),
                                           Column(name='In Data Structure', key='in_data_structure'),
                                           Column(name='Data Class', key='data_class'),
                                           Column(name='Glossary Term', key='glossary_term'),
                                           Column(name='isNullable', key='is_nullable'),
                                           Column(name='Minimum Length', key='min_length'),
                                           Column(name='Length', key='length'),
                                           Column(name='Precision', key='precision'),
                                           Column(name='Ordered Values', key='ordered_values'),
                                           Column(name='Units', key='units'),
                                           Column(name='Default Value', key='default_value'),
                                           Column(name='Version Identifier', key='version_id'),
                                           Column(name='In Data Dictionary', key='in_data_dictionary'),
                                           Column(name='Parent Data Field', key='parent_data_field'),
                                           Column(name='Qualified Name', key='qualified_name'),
                                           Column(name='GUID', key='guid')])],
                                action=ActionParameter(function='DataDesigner.find_data_fields',
                                                       required_params=['search_string'],
                                                       optional_params=['page_size', 'start_from', 'starts_with',
                                                                        'ends_with', 'ignore_case'])),
    'Data-Processing-Purpose-DrE': FormatSet(target_type='Data-Processing-Purpose-DrE',
                                             heading='Data-Processing-Purpose-DrE Attributes',
                                             description='Auto-generated format for Data Processing Purpose (Create).',
                                             formats=[Format(types=['ALL'],
                                                             columns=[Column(name='Display Name', key='display_name'),
                                                                      Column(name='Summary', key='summary'),
                                                                      Column(name='Description', key='description'),
                                                                      Column(name='Category', key='category'),
                                                                      Column(name='Domain Identifier',
                                                                             key='domain_identifier'),
                                                                      Column(name='Identifier', key='identifier'),
                                                                      Column(name='Version Identifier',
                                                                             key='version_identifier'),
                                                                      Column(name='Usage', key='usage'),
                                                                      Column(name='Scope', key='scope'),
                                                                      Column(name='Importance', key='importance'),
                                                                      Column(name='Implications', key='implications'),
                                                                      Column(name='Outcomes', key='outcomes'),
                                                                      Column(name='Results', key='results'),
                                                                      Column(name='Status', key='element_status'),
                                                                      Column(name='User Defined Status',
                                                                             key='user_defined_status'),
                                                                      Column(name='Qualified Name',
                                                                             key='qualified_name'),
                                                                      Column(name='GUID', key='guid')])],
                                             action=ActionParameter(
                                                 function='GovernanceOfficer.find_governance_definitions',
                                                 required_params=['search_string'],
                                                 optional_params=['page_size', 'start_from', 'starts_with', 'ends_with',
                                                                  'ignore_case'],
                                                 spec_params={'metadata_element_types': ['DataProcessingPurpose']})),
    'Data-Sharing-Agreement-DrE': FormatSet(target_type='Data-Sharing-Agreement-DrE',
                                            heading='Data-Sharing-Agreement-DrE Attributes',
                                            description='Auto-generated format for Data Sharing Agreement (Create).',
                                            formats=[Format(types=['ALL'],
                                                            columns=[Column(name='Display Name', key='display_name'),
                                                                     Column(name='Description', key='description'),
                                                                     Column(name='Category', key='category'),
                                                                     Column(name='Identifier', key='identifier'),
                                                                     Column(name='Status', key='element_status'),
                                                                     Column(name='User_Defined_Status',
                                                                            key='user_defined_status'),
                                                                     Column(name='Version Identifier',
                                                                            key='version_identifier'),
                                                                     Column(name='Product Manager',
                                                                            key='product_manager'),
                                                                     Column(name='Qualified Name',
                                                                            key='qualified_name'),
                                                                     Column(name='GUID', key='guid')])],
                                            action=ActionParameter(function='CollectionManager.find_collections',
                                                                   required_params=['search_string'],
                                                                   optional_params=['page_size', 'start_from',
                                                                                    'starts_with', 'ends_with',
                                                                                    'ignore_case'], spec_params={
                                                    'classification_names': ['DataSharingAgreement']})),
    'Data-Specification-DrE': FormatSet(target_type='Data-Specification-DrE',
                                        heading='Data-Specification-DrE Attributes',
                                        description='Auto-generated format for Data Specification (Create).', formats=[
            Format(types=['ALL'], columns=[Column(name='Display Name', key='display_name'),
                                           Column(name='Description', key='description'),
                                           Column(name='Category', key='category'),
                                           Column(name='Qualified Name', key='qualified_name'),
                                           Column(name='GUID', key='guid')])],
                                        action=ActionParameter(function='CollectionManager.find_collections',
                                                               required_params=['search_string'],
                                                               optional_params=['page_size', 'start_from',
                                                                                'starts_with', 'ends_with',
                                                                                'ignore_case'],
                                                               spec_params={'metadata_element_types': ['DataSpec']})),
    'Data-Structure-DrE': FormatSet(target_type='Data-Structure-DrE', heading='Data-Structure-DrE Attributes',
                                    description='Auto-generated format for Data Structure (Create).', formats=[
            Format(types=['ALL'], columns=[Column(name='Display Name', key='display_name'),
                                           Column(name='Description', key='description'),
                                           Column(name='Category', key='category'),
                                           Column(name='Status', key='element_status'),
                                           Column(name='In Data Specification', key='in_data_spec'),
                                           Column(name='In Data Dictionary', key='in_data_dictionary'),
                                           Column(name='Qualified Name', key='qualified_name'),
                                           Column(name='GUID', key='guid')])],
                                    action=ActionParameter(function='DataDesigner.find_data_structures',
                                                           required_params=['search_string'],
                                                           optional_params=['page_size', 'start_from', 'starts_with',
                                                                            'ends_with', 'ignore_case'])),
    'Digital-Product-DrE': FormatSet(target_type='Digital-Product-DrE', heading='Digital-Product-DrE Attributes',
                                     description='Auto-generated format for Digital Product (Create).', formats=[
            Format(types=['ALL'], columns=[Column(name='Display Name', key='display_name'),
                                           Column(name='Description', key='description'),
                                           Column(name='Product Name', key='product_name'),
                                           Column(name='Status', key='element_status'),
                                           Column(name='User Defined Status', key='user_defined_status'),
                                           Column(name='Category', key='category'),
                                           Column(name='Identifier', key='identifier'),
                                           Column(name='Maturity', key='maturity'),
                                           Column(name='Service Life', key='service_life'),
                                           Column(name='Introduction Date', key='introduction_date'),
                                           Column(name='Next Version Date', key='next_version_date'),
                                           Column(name='Withdrawal Date', key='withdrawal_date'),
                                           Column(name='Version Identifier', key='current_version'),
                                           Column(name='Product Manager', key='product_manager'),
                                           Column(name='Qualified Name', key='qualified_name'),
                                           Column(name='GUID', key='guid')])],
                                     action=ActionParameter(function='CollectionManager.find_collections',
                                                            required_params=['search_string'],
                                                            optional_params=['page_size', 'start_from', 'starts_with',
                                                                             'ends_with', 'ignore_case'], spec_params={
                                             'metadata_element_types': ['DigitalProductCatalog', 'DigitalProductCatalogFolder']})),
    'Digital-Subscription-DrE': FormatSet(target_type='Digital-Subscription-DrE',
                                          heading='Digital-Subscription-DrE Attributes',
                                          description='Auto-generated format for Digital Subscription (Create).',
                                          formats=[Format(types=['ALL'],
                                                          columns=[Column(name='Display Name', key='display_name'),
                                                                   Column(name='Description', key='description'),
                                                                   Column(name='Identifier', key='identifier'),
                                                                   Column(name='Category', key='category'),
                                                                   Column(name='Status', key='element_status'),
                                                                   Column(name='User_Defined_Status',
                                                                          key='user_defined_status'),
                                                                   Column(name='Support Level', key='support_level'),
                                                                   Column(name='Service Levels', key='service_levels'),
                                                                   Column(name='Version Identifier',
                                                                          key='version_identifier'),
                                                                   Column(name='Qualified Name', key='qualified_name'),
                                                                   Column(name='GUID', key='guid')])],
                                          action=ActionParameter(function='CollectionManager.find_collections',
                                                                 required_params=['search_string'],
                                                                 optional_params=['page_size', 'start_from',
                                                                                  'starts_with', 'ends_with',
                                                                                  'ignore_case'], spec_params={
                                                  'metadata_element_types': ['DigitalSubscription']})),
    'External-Data-Source-DrE': FormatSet(target_type='External Data Source',
                                          heading='External-Data-Source-DrE Attributes',
                                          description='Auto-generated format for External Data Source (Create).',
                                          formats=[Format(types=['ALL'],
                                                          columns=[Column(name='Display Name', key='display_name'),
                                                                   Column(name='Description', key='description'),
                                                                   Column(name='Category', key='category'),
                                                                   Column(name='Reference Title',
                                                                          key='reference_title'),
                                                                   Column(name='Reference Abstract',
                                                                          key='reference_abstract'),
                                                                   Column(name='Authors', key='authors'),
                                                                   Column(name='Organization', key='organization'),
                                                                   Column(name='URL', key='reference_url'),
                                                                   Column(name='Sources', key='reference_sources'),
                                                                   Column(name='License', key='license'),
                                                                   Column(name='Copyright', key='copyright'),
                                                                   Column(name='Version Identifier',
                                                                          key='current_version'),
                                                                   Column(name='Classifications',
                                                                          key='classifications'),
                                                                   Column(name='Qualified Name', key='qualified_name'),
                                                                   Column(name='GUID', key='guid')])],
                                          action=ActionParameter(function='ExternalReference.find_external_references',
                                                                 required_params=['search_string'],
                                                                 optional_params=['page_size', 'start_from',
                                                                                  'starts_with', 'ends_with',
                                                                                  'ignore_case'], spec_params={
                                                  'metadata_element_types': ['ExternalDataSource']})),
    'External-Reference-DrE': FormatSet(target_type='External-Reference-DrE',
                                        heading='External-Reference-DrE Attributes',
                                        description='Auto-generated format for External Reference (Create).', formats=[
            Format(types=['ALL'], columns=[Column(name='Display Name', key='display_name'),
                                           Column(name='Description', key='description'),
                                           Column(name='Category', key='category'),
                                           Column(name='Reference Title', key='reference_title'),
                                           Column(name='Reference Abstract', key='reference_abstract'),
                                           Column(name='Authors', key='authors'),
                                           Column(name='Organization', key='organization'),
                                           Column(name='URL', key='reference_url'),
                                           Column(name='Sources', key='reference_sources'),
                                           Column(name='License', key='license'),
                                           Column(name='Copyright', key='copyright'),
                                           Column(name='Number of Pages', key='number_of_pages'),
                                           Column(name='Page Range', key='page_range'),
                                           Column(name='Publication Series', key='publication_series'),
                                           Column(name='Publication Series Volume', key='pub_series_volume'),
                                           Column(name='Publisher', key='publisher'),
                                           Column(name='First Publication Date', key='first_pub_date'),
                                           Column(name='Publication Date', key='pub_date'),
                                           Column(name='Publication City', key='pub_city'),
                                           Column(name='Publication Year', key='pub_year'),
                                           Column(name='Publication Numbers', key='pub_numbers'),
                                           Column(name='Version Identifier', key='current_version'),
                                           Column(name='Classifications', key='classifications'),
                                           Column(name='Qualified Name', key='qualified_name'),
                                           Column(name='GUID', key='guid')])],
                                        action=ActionParameter(function='ExternalReference.find_external_references',
                                                               required_params=['search_string'],
                                                               optional_params=['page_size', 'start_from',
                                                                                'starts_with', 'ends_with',
                                                                                'ignore_case'], spec_params={
                                                'metadata_element_types': ['ExternalReference']})),

    'Glossary-DrE': FormatSet(target_type='Glossary-DrE', heading='Glossary-DrE Attributes',
                              description='Auto-generated format for Glossary (Create).', formats=[Format(types=['ALL'],
                                                                                                          columns=[
                                                                                                              Column(
                                                                                                                  name='Display Name',
                                                                                                                  key='display_name'),
                                                                                                              Column(
                                                                                                                  name='Description',
                                                                                                                  key='description'),
                                                                                                              Column(
                                                                                                                  name='Category',
                                                                                                                  key='category'),
                                                                                                              Column(
                                                                                                                  name='Language',
                                                                                                                  key='language'),
                                                                                                              Column(
                                                                                                                  name='Qualified Name',
                                                                                                                  key='qualified_name'),
                                                                                                              Column(
                                                                                                                  name='GUID',
                                                                                                                  key='guid')])],
                              action=ActionParameter(function='CollectionManager.find_collections',
                                                     required_params=['search_string'],
                                                     optional_params=['page_size', 'start_from', 'starts_with',
                                                                      'ends_with', 'ignore_case'],
                                                     spec_params={'metadata_element_types': ['Glossary']})),
    'Glossary-Term-DrE': FormatSet(target_type='Glossary-Term-DrE', heading='Glossary-Term-DrE Attributes',
                                   description='Auto-generated format for Glossary Term (Create).', formats=[
            Format(types=['ALL'],
                   columns=[Column(name='Display Name', key='term_name'), Column(name='Glossary', key='glossary_name'),
                            Column(name='Summary', key='summary'), Column(name='Description', key='description'),
                            Column(name='Abbreviation', key='abbreviation'), Column(name='Example', key='example'),
                            Column(name='Usage', key='usage'), Column(name='Status', key='element_status'),
                            Column(name='Version Identifier', key='version_identifier'),
                            Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid')])],
                                   action=ActionParameter(function='GlossaryManager.find_glossary_terms',
                                                          required_params=['search_string'],
                                                          optional_params=['page_size', 'start_from', 'starts_with',
                                                                           'ends_with', 'ignore_case'])),
    'Governance-Action-DrE': FormatSet(target_type='Governance-Action-DrE', heading='Governance-Action-DrE Attributes',
                                       description='Auto-generated format for Governance Action (Create).', formats=[
            Format(types=['ALL'],
                   columns=[Column(name='Display Name', key='display_name'), Column(name='Summary', key='summary'),
                            Column(name='Description', key='description'), Column(name='Category', key='category'),
                            Column(name='Domain Identifier', key='domain_identifier'),
                            Column(name='Identifier', key='identifier'),
                            Column(name='Version Identifier', key='version_identifier'),
                            Column(name='Usage', key='usage'), Column(name='Scope', key='scope'),
                            Column(name='Importance', key='importance'),
                            Column(name='Implications', key='implications'), Column(name='Outcomes', key='outcomes'),
                            Column(name='Results', key='results'), Column(name='Status', key='element_status'),
                            Column(name='User Defined Status', key='user_defined_status'),
                            Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid')])],
                                       action=ActionParameter(function='GovernanceOfficer.find_governance_definitions',
                                                              required_params=['search_string'],
                                                              optional_params=['page_size', 'start_from', 'starts_with',
                                                                               'ends_with', 'ignore_case'],
                                                              spec_params={
                                                                  'metadata_element_types': ['GovernanceAction']})),
    'Governance-Approach-DrE': FormatSet(target_type='Governance-Approach-DrE',
                                         heading='Governance-Approach-DrE Attributes',
                                         description='Auto-generated format for Governance Approach (Create).',
                                         formats=[Format(types=['ALL'],
                                                         columns=[Column(name='Display Name', key='display_name'),
                                                                  Column(name='Summary', key='summary'),
                                                                  Column(name='Description', key='description'),
                                                                  Column(name='Category', key='category'),
                                                                  Column(name='Domain Identifier',
                                                                         key='domain_identifier'),
                                                                  Column(name='Identifier', key='identifier'),
                                                                  Column(name='Version Identifier',
                                                                         key='version_identifier'),
                                                                  Column(name='Usage', key='usage'),
                                                                  Column(name='Scope', key='scope'),
                                                                  Column(name='Importance', key='importance'),
                                                                  Column(name='Implications', key='implications'),
                                                                  Column(name='Outcomes', key='outcomes'),
                                                                  Column(name='Results', key='results'),
                                                                  Column(name='Status', key='element_status'),
                                                                  Column(name='User Defined Status',
                                                                         key='user_defined_status'),
                                                                  Column(name='Qualified Name', key='qualified_name'),
                                                                  Column(name='GUID', key='guid')])],
                                         action=ActionParameter(
                                             function='GovernanceOfficer.find_governance_definitions',
                                             required_params=['search_string'],
                                             optional_params=['page_size', 'start_from', 'starts_with', 'ends_with',
                                                              'ignore_case'],
                                             spec_params={'metadata_element_types': ['GovernanceApproach']})),
    'Governance-Control-DrE': FormatSet(target_type='Governance-Control-DrE',
                                        heading='Governance-Control-DrE Attributes',
                                        description='Auto-generated format for Governance Control (Create).', formats=[
            Format(types=['ALL'],
                   columns=[Column(name='Display Name', key='display_name'), Column(name='Summary', key='summary'),
                            Column(name='Description', key='description'), Column(name='Category', key='category'),
                            Column(name='Domain Identifier', key='domain_identifier'),
                            Column(name='Identifier', key='identifier'),
                            Column(name='Version Identifier', key='version_identifier'),
                            Column(name='Usage', key='usage'), Column(name='Scope', key='scope'),
                            Column(name='Importance', key='importance'), Column(name='measurement', key='measurement'),
                            Column(name='target', key='target'), Column(name='Implications', key='implications'),
                            Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'),
                            Column(name='Status', key='element_status'),
                            Column(name='User Defined Status', key='user_defined_status'),
                            Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid')])],
                                        action=ActionParameter(function='GovernanceOfficer.find_governance_definitions',
                                                               required_params=['search_string'],
                                                               optional_params=['page_size', 'start_from',
                                                                                'starts_with', 'ends_with',
                                                                                'ignore_case'], spec_params={
                                                'metadata_element_types': ['GovernanceMetric']})),
    'Governance-Driver-DrE': FormatSet(target_type='Governance-Driver-DrE', heading='Governance-Driver-DrE Attributes',
                                       description='Auto-generated format for Governance Driver (Create).', formats=[
            Format(types=['ALL'],
                   columns=[Column(name='Display Name', key='display_name'), Column(name='Summary', key='summary'),
                            Column(name='Description', key='description'), Column(name='Category', key='category'),
                            Column(name='Domain Identifier', key='domain_identifier'),
                            Column(name='Identifier', key='identifier'),
                            Column(name='Version Identifier', key='version_identifier'),
                            Column(name='Usage', key='usage'), Column(name='Scope', key='scope'),
                            Column(name='Importance', key='importance'),
                            Column(name='Implications', key='implications'), Column(name='Outcomes', key='outcomes'),
                            Column(name='Results', key='results'), Column(name='Status', key='element_status'),
                            Column(name='User Defined Status', key='user_defined_status'),
                            Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid')])],
                                       action=ActionParameter(function='GovernanceOfficer.find_governance_definitions',
                                                              required_params=['search_string'],
                                                              optional_params=['page_size', 'start_from', 'starts_with',
                                                                               'ends_with', 'ignore_case'],
                                                              spec_params={
                                                                  'metadata_element_types': ['GovernanceDriver']})),
    'Governance-Obligation-DrE': FormatSet(target_type='Governance-Obligation-DrE',
                                           heading='Governance-Obligation-DrE Attributes',
                                           description='Auto-generated format for Governance Obligation (Create).',
                                           formats=[Format(types=['ALL'],
                                                           columns=[Column(name='Display Name', key='display_name'),
                                                                    Column(name='Summary', key='summary'),
                                                                    Column(name='Description', key='description'),
                                                                    Column(name='Category', key='category'),
                                                                    Column(name='Domain Identifier',
                                                                           key='domain_identifier'),
                                                                    Column(name='Identifier', key='identifier'),
                                                                    Column(name='Version Identifier',
                                                                           key='version_identifier'),
                                                                    Column(name='Usage', key='usage'),
                                                                    Column(name='Scope', key='scope'),
                                                                    Column(name='Importance', key='importance'),
                                                                    Column(name='Implications', key='implications'),
                                                                    Column(name='Outcomes', key='outcomes'),
                                                                    Column(name='Results', key='results'),
                                                                    Column(name='Status', key='element_status'),
                                                                    Column(name='User Defined Status',
                                                                           key='user_defined_status'),
                                                                    Column(name='Qualified Name', key='qualified_name'),
                                                                    Column(name='GUID', key='guid')])],
                                           action=ActionParameter(
                                               function='GovernanceOfficer.find_governance_definitions',
                                               required_params=['search_string'],
                                               optional_params=['page_size', 'start_from', 'starts_with', 'ends_with',
                                                                'ignore_case'],
                                               spec_params={'metadata_element_types': ['GovernanceObligation']})),
    'Governance-Policy-DrE': FormatSet(target_type='Governance-Policy-DrE', heading='Governance-Policy-DrE Attributes',
                                       description='Auto-generated format for Governance Policy (Create).', formats=[
            Format(types=['ALL'],
                   columns=[Column(name='Display Name', key='display_name'), Column(name='Summary', key='summary'),
                            Column(name='Description', key='description'), Column(name='Category', key='category'),
                            Column(name='Domain Identifier', key='domain_identifier'),
                            Column(name='Identifier', key='identifier'),
                            Column(name='Version Identifier', key='version_identifier'),
                            Column(name='Usage', key='usage'), Column(name='Scope', key='scope'),
                            Column(name='Importance', key='importance'),
                            Column(name='Implications', key='implications'), Column(name='Outcomes', key='outcomes'),
                            Column(name='Results', key='results'), Column(name='Status', key='element_status'),
                            Column(name='User Defined Status', key='user_defined_status'),
                            Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid')])],
                                       action=ActionParameter(function='GovernanceOfficer.find_governance_definitions',
                                                              required_params=['search_string'],
                                                              optional_params=['page_size', 'start_from', 'starts_with',
                                                                               'ends_with', 'ignore_case'],
                                                              spec_params={
                                                                  'metadata_element_types': ['GovernancePolicy']})),
    'Governance-Principle-DrE': FormatSet(target_type='Governance-Principle-DrE',
                                          heading='Governance-Principle-DrE Attributes',
                                          description='Auto-generated format for Governance Principle (Create).',
                                          formats=[Format(types=['ALL'],
                                                          columns=[Column(name='Display Name', key='display_name'),
                                                                   Column(name='Summary', key='summary'),
                                                                   Column(name='Description', key='description'),
                                                                   Column(name='Category', key='category'),
                                                                   Column(name='Domain Identifier',
                                                                          key='domain_identifier'),
                                                                   Column(name='Identifier', key='identifier'),
                                                                   Column(name='Version Identifier',
                                                                          key='version_identifier'),
                                                                   Column(name='Usage', key='usage'),
                                                                   Column(name='Scope', key='scope'),
                                                                   Column(name='Importance', key='importance'),
                                                                   Column(name='Implications', key='implications'),
                                                                   Column(name='Outcomes', key='outcomes'),
                                                                   Column(name='Results', key='results'),
                                                                   Column(name='Status', key='element_status'),
                                                                   Column(name='User Defined Status',
                                                                          key='user_defined_status'),
                                                                   Column(name='Qualified Name', key='qualified_name'),
                                                                   Column(name='GUID', key='guid')])],
                                          action=ActionParameter(
                                              function='GovernanceOfficer.find_governance_definitions',
                                              required_params=['search_string'],
                                              optional_params=['page_size', 'start_from', 'starts_with', 'ends_with',
                                                               'ignore_case'],
                                              spec_params={'metadata_element_types': ['GovernancePrinciple']})),
    'Governance-Procedure-DrE': FormatSet(target_type='Governance-Procedure-DrE',
                                          heading='Governance-Procedure-DrE Attributes',
                                          description='Auto-generated format for Governance Procedure (Create).',
                                          formats=[Format(types=['ALL'],
                                                          columns=[Column(name='Display Name', key='display_name'),
                                                                   Column(name='Summary', key='summary'),
                                                                   Column(name='Description', key='description'),
                                                                   Column(name='Category', key='category'),
                                                                   Column(name='Domain Identifier',
                                                                          key='domain_identifier'),
                                                                   Column(name='Document Identifier',
                                                                          key='document_identifier'),
                                                                   Column(name='Version Identifier',
                                                                          key='version_identifier'),
                                                                   Column(name='Scope', key='scope'),
                                                                   Column(name='Importance', key='importance'),
                                                                   Column(name='Implementation Description',
                                                                          key='implementation_description'),
                                                                   Column(name='Supports Policies',
                                                                          key='supports_policies'),
                                                                   Column(name='Implications', key='implications'),
                                                                   Column(name='Outcomes', key='outcomes'),
                                                                   Column(name='Results', key='results'),
                                                                   Column(name='Status', key='element_status'),
                                                                   Column(name='User Defined Status',
                                                                          key='user_defined_status'),
                                                                   Column(name='Qualified Name', key='qualified_name'),
                                                                   Column(name='GUID', key='guid')])],
                                          action=ActionParameter(
                                              function='GovernanceOfficer.find_governance_definitions',
                                              required_params=['search_string'],
                                              optional_params=['page_size', 'start_from', 'starts_with', 'ends_with',
                                                               'ignore_case'],
                                              spec_params={'metadata_element_types': ['GovernanceProcedure']})),
    'Governance-Responsibility-DrE': FormatSet(target_type='Governance-Responsibility-DrE',
                                               heading='Governance-Responsibility-DrE Attributes',
                                               description='Auto-generated format for Governance Responsibility (Create).',
                                               formats=[Format(types=['ALL'],
                                                               columns=[Column(name='Display Name', key='display_name'),
                                                                        Column(name='Summary', key='summary'),
                                                                        Column(name='Description', key='description'),
                                                                        Column(name='Category', key='category'),
                                                                        Column(name='Domain Identifier',
                                                                               key='domain_identifier'),
                                                                        Column(name='Document Identifier',
                                                                               key='document_identifier'),
                                                                        Column(name='Version Identifier',
                                                                               key='version_identifier'),
                                                                        Column(name='Scope', key='scope'),
                                                                        Column(name='Importance', key='importance'),
                                                                        Column(name='Implementation Description',
                                                                               key='implementation_description'),
                                                                        Column(name='Supports Policies',
                                                                               key='supports_policies'),
                                                                        Column(name='Implications', key='implications'),
                                                                        Column(name='Outcomes', key='outcomes'),
                                                                        Column(name='Results', key='results'),
                                                                        Column(name='Status', key='element_status'),
                                                                        Column(name='User Defined Status',
                                                                               key='user_defined_status'),
                                                                        Column(name='Qualified Name',
                                                                               key='qualified_name'),
                                                                        Column(name='GUID', key='guid')])],
                                               action=ActionParameter(
                                                   function='GovernanceOfficer.find_governance_definitions',
                                                   required_params=['search_string'],
                                                   optional_params=['page_size', 'start_from', 'starts_with',
                                                                    'ends_with', 'ignore_case'], spec_params={
                                                       'metadata_element_types': ['GovernanceResponsibility']})),
    'Governance-Rule-DrE': FormatSet(target_type='Governance-Rule-DrE', heading='Governance-Rule-DrE Attributes',
                                     description='Auto-generated format for Governance Rule (Create).', formats=[
            Format(types=['ALL'],
                   columns=[Column(name='Display Name', key='display_name'), Column(name='Summary', key='summary'),
                            Column(name='Description', key='description'), Column(name='Category', key='category'),
                            Column(name='Domain Identifier', key='domain_identifier'),
                            Column(name='Document Identifier', key='document_identifier'),
                            Column(name='Version Identifier', key='version_identifier'),
                            Column(name='Scope', key='scope'), Column(name='Importance', key='importance'),
                            Column(name='Implementation Description', key='implementation_description'),
                            Column(name='Supports Policies', key='supports_policies'),
                            Column(name='Implications', key='implications'), Column(name='Outcomes', key='outcomes'),
                            Column(name='Results', key='results'), Column(name='Status', key='element_status'),
                            Column(name='User Defined Status', key='user_defined_status'),
                            Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid')])],
                                     action=ActionParameter(function='GovernanceOfficer.find_governance_definitions',
                                                            required_params=['search_string'],
                                                            optional_params=['page_size', 'start_from', 'starts_with',
                                                                             'ends_with', 'ignore_case'], spec_params={
                                             'metadata_element_types': ['GovernanceRule']})),
    'Governance-Strategy-DrE': FormatSet(target_type='Governance-Strategy-DrE',
                                         heading='Governance-Strategy-DrE Attributes',
                                         description='Auto-generated format for Governance Strategy (Create).',
                                         formats=[Format(types=['ALL'],
                                                         columns=[Column(name='Display Name', key='display_name'),
                                                                  Column(name='Summary', key='summary'),
                                                                  Column(name='Description', key='description'),
                                                                  Column(name='Category', key='category'),
                                                                  Column(name='Domain Identifier',
                                                                         key='domain_identifier'),
                                                                  Column(name='Identifier', key='identifier'),
                                                                  Column(name='Version Identifier',
                                                                         key='version_identifier'),
                                                                  Column(name='Usage', key='usage'),
                                                                  Column(name='Scope', key='scope'),
                                                                  Column(name='Importance', key='importance'),
                                                                  Column(name='Implications', key='implications'),
                                                                  Column(name='Outcomes', key='outcomes'),
                                                                  Column(name='Results', key='results'),
                                                                  Column(name='Status', key='element_status'),
                                                                  Column(name='User Defined Status',
                                                                         key='user_defined_status'),
                                                                  Column(name='Qualified Name', key='qualified_name'),
                                                                  Column(name='GUID', key='guid')])],
                                         action=ActionParameter(
                                             function='GovernanceOfficer.find_governance_definitions',
                                             required_params=['search_string'],
                                             optional_params=['page_size', 'start_from', 'starts_with', 'ends_with',
                                                              'ignore_case'],
                                             spec_params={'metadata_element_types': ['GovernanceStrategy']})),
    'Information-Supply-Chain-DrE': FormatSet(target_type='Information-Supply-Chain-DrE',
                                              heading='Information-Supply-Chain-DrE Attributes',
                                              description='Auto-generated format for Information Supply Chain (Create).',
                                              formats=[Format(types=['ALL'],
                                                              columns=[Column(name='Display Name', key='display_name'),
                                                                       Column(name='Description', key='description'),
                                                                       Column(name='Category', key='category'),
                                                                       Column(name='Scope', key='scope'),
                                                                       Column(name='Purposes', key='purposes'),
                                                                       Column(name='Nested Information Supply Chains',
                                                                              key='nested_info_supply_chains'),
                                                                       Column(name='In Information Supply Chain',
                                                                              key='in_supply_chain'),
                                                                       Column(name='Qualified Name',
                                                                              key='qualified_name'),
                                                                       Column(name='GUID', key='guid'),
                                                                       Column(name='Merge Update',
                                                                              key='merge_update')])],
                                              action=ActionParameter(
                                                  function='SolutionArchitect.find_information_supply_chains',
                                                  required_params=['search_string'],
                                                  optional_params=['page_size', 'start_from', 'starts_with',
                                                                   'ends_with', 'ignore_case'])),
    'License-Type-DrE': FormatSet(target_type='License-Type-DrE', heading='License-Type-DrE Attributes',
                                  description='Auto-generated format for License Type (Create).', formats=[
            Format(types=['ALL'],
                   columns=[Column(name='Display Name', key='display_name'), Column(name='Summary', key='summary'),
                            Column(name='Description', key='description'), Column(name='Category', key='category'),
                            Column(name='Domain Identifier', key='domain_identifier'),
                            Column(name='Document Identifier', key='document_identifier'),
                            Column(name='Version Identifier', key='version_identifier'),
                            Column(name='Scope', key='scope'), Column(name='Importance', key='importance'),
                            Column(name='Details', key='details'), Column(name='Implications', key='implications'),
                            Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'),
                            Column(name='Status', key='element_status'),
                            Column(name='User Defined Status', key='user_defined_status'),
                            Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid')])],
                                  action=ActionParameter(function='GovernanceOfficer.find_governance_definitions',
                                                         required_params=['search_string'],
                                                         optional_params=['page_size', 'start_from', 'starts_with',
                                                                          'ends_with', 'ignore_case'],
                                                         spec_params={'metadata_element_types': ['LicenseType']})),
    'Naming-Standard-Rule-DrE': FormatSet(target_type='Naming-Standard-Rule-DrE',
                                          heading='Naming-Standard-Rule-DrE Attributes',
                                          description='Auto-generated format for Naming Standard Rule (Create).',
                                          formats=[Format(types=['ALL'],
                                                          columns=[Column(name='Display Name', key='display_name'),
                                                                   Column(name='Summary', key='summary'),
                                                                   Column(name='Description', key='description'),
                                                                   Column(name='Category', key='category'),
                                                                   Column(name='Domain Identifier',
                                                                          key='domain_identifier'),
                                                                   Column(name='Document Identifier',
                                                                          key='document_identifier'),
                                                                   Column(name='Version Identifier',
                                                                          key='version_identifier'),
                                                                   Column(name='Scope', key='scope'),
                                                                   Column(name='Importance', key='importance'),
                                                                   Column(name='Implementation Description',
                                                                          key='implementation_description'),
                                                                   Column(name='Supports Policies',
                                                                          key='supports_policies'),
                                                                   Column(name='Name Patterns', key='implications'),
                                                                   Column(name='Outcomes', key='outcomes'),
                                                                   Column(name='Results', key='results'),
                                                                   Column(name='Status', key='element_status'),
                                                                   Column(name='User Defined Status',
                                                                          key='user_defined_status'),
                                                                   Column(name='Qualified Name', key='qualified_name'),
                                                                   Column(name='GUID', key='guid')])],
                                          action=ActionParameter(
                                              function='GovernanceOfficer.find_governance_definitions',
                                              required_params=['search_string'],
                                              optional_params=['page_size', 'start_from', 'starts_with', 'ends_with',
                                                               'ignore_case'],
                                              spec_params={'metadata_element_types': ['NamingStandardRule']})),
    'Personal-Project-DrE': FormatSet(target_type='Personal-Project-DrE', heading='Personal-Project-DrE Attributes',
                                      description='Auto-generated format for Personal Project (Create).', formats=[
            Format(types=['ALL'], columns=[Column(name='Display Name', key='display_name'),
                                           Column(name='Description', key='description'),
                                           Column(name='Project Type', key='project_type'),
                                           Column(name='Category', key='category'),
                                           Column(name='Identifier', key='project_identifier'),
                                           Column(name='Mission', key='mission'),
                                           Column(name='Purposes', key='purposes'),
                                           Column(name='Start Date', key='start_date'),
                                           Column(name='Planned End Date', key='end_date'),
                                           Column(name='Priority', key='priority'),
                                           Column(name='Project Phase', key='project_phase'),
                                           Column(name='Project Status', key='project_status'),
                                           Column(name='Project Health', key='project_health'),
                                           Column(name='Qualified Name', key='qualified_name'),
                                           Column(name='GUID', key='guid')])],
                                      action=ActionParameter(function='ProjectManager.find_projects',
                                                             required_params=['search_string'],
                                                             optional_params=['page_size', 'start_from', 'starts_with',
                                                                              'ends_with', 'ignore_case'], spec_params={
                                              'classification_names': ['PersonalProject']})),
    'Project-DrE': FormatSet(target_type='Project-DrE', heading='Project-DrE Attributes',
                             description='Auto-generated format for Project (Create).', formats=[Format(types=['ALL'],
                                                                                                        columns=[Column(
                                                                                                            name='Display Name',
                                                                                                            key='display_name'),
                                                                                                            Column(
                                                                                                                name='Description',
                                                                                                                key='description'),
                                                                                                            Column(
                                                                                                                name='Project Type',
                                                                                                                key='project_type'),
                                                                                                            Column(
                                                                                                                name='Category',
                                                                                                                key='category'),
                                                                                                            Column(
                                                                                                                name='Identifier',
                                                                                                                key='project_identifier'),
                                                                                                            Column(
                                                                                                                name='Mission',
                                                                                                                key='mission'),
                                                                                                            Column(
                                                                                                                name='Purposes',
                                                                                                                key='purposes'),
                                                                                                            Column(
                                                                                                                name='Start Date',
                                                                                                                key='start_date'),
                                                                                                            Column(
                                                                                                                name='Planned End Date',
                                                                                                                key='end_date'),
                                                                                                            Column(
                                                                                                                name='Priority',
                                                                                                                key='priority'),
                                                                                                            Column(
                                                                                                                name='Project Phase',
                                                                                                                key='project_phase'),
                                                                                                            Column(
                                                                                                                name='Project Status',
                                                                                                                key='project_status'),
                                                                                                            Column(
                                                                                                                name='Project Health',
                                                                                                                key='project_health'),
                                                                                                            Column(
                                                                                                                name='Qualified Name',
                                                                                                                key='qualified_name'),
                                                                                                            Column(
                                                                                                                name='GUID',
                                                                                                                key='guid')])],
                             action=ActionParameter(function='ProjectManager.find_projects',
                                                    required_params=['search_string'],
                                                    optional_params=['page_size', 'start_from', 'starts_with',
                                                                     'ends_with', 'ignore_case'])),
    'Regulation-Article-DrE': FormatSet(target_type='Regulation-Article-DrE',
                                        heading='Regulation-Article-DrE Attributes',
                                        description='Auto-generated format for Regulation Article (Create).', formats=[
            Format(types=['ALL'],
                   columns=[Column(name='Display Name', key='display_name'), Column(name='Summary', key='summary'),
                            Column(name='Description', key='description'), Column(name='Category', key='category'),
                            Column(name='Domain Identifier', key='domain_identifier'),
                            Column(name='Identifier', key='identifier'),
                            Column(name='Version Identifier', key='version_identifier'),
                            Column(name='Usage', key='usage'), Column(name='Scope', key='scope'),
                            Column(name='Importance', key='importance'),
                            Column(name='Implications', key='implications'), Column(name='Outcomes', key='outcomes'),
                            Column(name='Results', key='results'), Column(name='Status', key='element_status'),
                            Column(name='User Defined Status', key='user_defined_status'),
                            Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid')])],
                                        action=ActionParameter(function='GovernanceOfficer.find_governance_definitions',
                                                               required_params=['search_string'],
                                                               optional_params=['page_size', 'start_from',
                                                                                'starts_with', 'ends_with',
                                                                                'ignore_case'], spec_params={
                                                'metadata_element_types': ['RegulationArticle']})),
    'Regulation-DrE': FormatSet(target_type='Regulation-DrE', heading='Regulation-DrE Attributes',
                                description='Auto-generated format for Regulation (Create).', formats=[
            Format(types=['ALL'],
                   columns=[Column(name='Display Name', key='display_name'), Column(name='Summary', key='summary'),
                            Column(name='Description', key='description'), Column(name='Category', key='category'),
                            Column(name='Domain Identifier', key='domain_identifier'),
                            Column(name='Identifier', key='identifier'),
                            Column(name='Version Identifier', key='version_identifier'),
                            Column(name='Usage', key='usage'), Column(name='Scope', key='scope'),
                            Column(name='Importance', key='importance'),
                            Column(name='Regulation Source', key='regulation_source'),
                            Column(name='Regulators', key='regulators'),
                            Column(name='Implications', key='implications'), Column(name='Outcomes', key='outcomes'),
                            Column(name='Results', key='results'), Column(name='Status', key='element_status'),
                            Column(name='User Defined Status', key='user_defined_status'),
                            Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid')])],
                                action=ActionParameter(function='GovernanceOfficer.find_governance_definitions',
                                                       required_params=['search_string'],
                                                       optional_params=['page_size', 'start_from', 'starts_with',
                                                                        'ends_with', 'ignore_case'],
                                                       spec_params={'metadata_element_types': ['Regulation']})),
    'Security-Access-Control-DrE': FormatSet(target_type='Security-Access-Control-DrE',
                                             heading='Security-Access-Control-DrE Attributes',
                                             description='Auto-generated format for Security Access Control (Create).',
                                             formats=[Format(types=['ALL'],
                                                             columns=[Column(name='Display Name', key='display_name'),
                                                                      Column(name='Summary', key='summary'),
                                                                      Column(name='Description', key='description'),
                                                                      Column(name='Category', key='category'),
                                                                      Column(name='Domain Identifier',
                                                                             key='domain_identifier'),
                                                                      Column(name='Identifier', key='identifier'),
                                                                      Column(name='Version Identifier',
                                                                             key='version_identifier'),
                                                                      Column(name='Usage', key='usage'),
                                                                      Column(name='Scope', key='scope'),
                                                                      Column(name='Importance', key='importance'),
                                                                      Column(name='Implications', key='implications'),
                                                                      Column(name='Outcomes', key='outcomes'),
                                                                      Column(name='Results', key='results'),
                                                                      Column(name='Status', key='element_status'),
                                                                      Column(name='User Defined Status',
                                                                             key='user_defined_status'),
                                                                      Column(name='Qualified Name',
                                                                             key='qualified_name'),
                                                                      Column(name='GUID', key='guid')])],
                                             action=ActionParameter(
                                                 function='GovernanceOfficer.find_governance_definitions',
                                                 required_params=['search_string'],
                                                 optional_params=['page_size', 'start_from', 'starts_with', 'ends_with',
                                                                  'ignore_case'],
                                                 spec_params={'metadata_element_types': ['SecurityAccessControl']})),
    'Security-Group-DrE': FormatSet(target_type='Security-Group-DrE', heading='Security-Group-DrE Attributes',
                                    description='Auto-generated format for Security Group (Create).', formats=[
            Format(types=['ALL'],
                   columns=[Column(name='Display Name', key='display_name'), Column(name='Summary', key='summary'),
                            Column(name='Description', key='description'), Column(name='Category', key='category'),
                            Column(name='Domain Identifier', key='domain_identifier'),
                            Column(name='Identifier', key='identifier'),
                            Column(name='Version Identifier', key='version_identifier'),
                            Column(name='Usage', key='usage'), Column(name='Scope', key='scope'),
                            Column(name='Importance', key='importance'),
                            Column(name='Implications', key='implications'), Column(name='Outcomes', key='outcomes'),
                            Column(name='Results', key='results'), Column(name='Status', key='element_status'),
                            Column(name='User Defined Status', key='user_defined_status'),
                            Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid')])],
                                    action=ActionParameter(function='GovernanceOfficer.find_governance_definitions',
                                                           required_params=['search_string'],
                                                           optional_params=['page_size', 'start_from', 'starts_with',
                                                                            'ends_with', 'ignore_case'],
                                                           spec_params={'metadata_element_types': ['SEcurityGroup']})),
    'security_access_control-DrE': FormatSet(target_type='security_access_control-DrE',
                                             heading='security_access_control-DrE Attributes',
                                             description='Auto-generated format for security_access_control (Create).',
                                             formats=[Format(types=['ALL'],
                                                             columns=[Column(name='Display Name', key='display_name'),
                                                                      Column(name='Summary', key='summary'),
                                                                      Column(name='Description', key='description'),
                                                                      Column(name='Category', key='category'),
                                                                      Column(name='Domain Identifier',
                                                                             key='domain_identifier'),
                                                                      Column(name='Identifier', key='identifier'),
                                                                      Column(name='Version Identifier',
                                                                             key='version_identifier'),
                                                                      Column(name='Usage', key='usage'),
                                                                      Column(name='Scope', key='scope'),
                                                                      Column(name='Importance', key='importance'),
                                                                      Column(name='criteria', key='criteria'),
                                                                      Column(name='Implications', key='implications'),
                                                                      Column(name='Outcomes', key='outcomes'),
                                                                      Column(name='Results', key='results'),
                                                                      Column(name='Status', key='element_status'),
                                                                      Column(name='User Defined Status',
                                                                             key='user_defined_status'),
                                                                      Column(name='Qualified Name',
                                                                             key='qualified_name'),
                                                                      Column(name='GUID', key='guid')])],
                                             action=ActionParameter(
                                                 function='GovernanceOfficer.find_governance_definitions',
                                                 required_params=['search_string'],
                                                 optional_params=['page_size', 'start_from', 'starts_with', 'ends_with',
                                                                  'ignore_case'],
                                                 spec_params={'metadata_element_types': ['GovernanceZone']})),
    'Service-Level-Objectives-DrE': FormatSet(target_type='Service-Level-Objectives-DrE',
                                              heading='Service-Level-Objectives-DrE Attributes',
                                              description='Auto-generated format for Service Level Objectives (Create).',
                                              formats=[Format(types=['ALL'],
                                                              columns=[Column(name='Display Name', key='display_name'),
                                                                       Column(name='Summary', key='summary'),
                                                                       Column(name='Description', key='description'),
                                                                       Column(name='Category', key='category'),
                                                                       Column(name='Domain Identifier',
                                                                              key='domain_identifier'),
                                                                       Column(name='Document Identifier',
                                                                              key='document_identifier'),
                                                                       Column(name='Version Identifier',
                                                                              key='version_identifier'),
                                                                       Column(name='Scope', key='scope'),
                                                                       Column(name='Importance', key='importance'),
                                                                       Column(name='Implementation Description',
                                                                              key='implementation_description'),
                                                                       Column(name='Supports Policies',
                                                                              key='supports_policies'),
                                                                       Column(name='Implications', key='implications'),
                                                                       Column(name='Outcomes', key='outcomes'),
                                                                       Column(name='Results', key='results'),
                                                                       Column(name='Status', key='element_status'),
                                                                       Column(name='User Defined Status',
                                                                              key='user_defined_status'),
                                                                       Column(name='Qualified Name',
                                                                              key='qualified_name'),
                                                                       Column(name='GUID', key='guid')])],
                                              action=ActionParameter(
                                                  function='GovernanceOfficer.find_governance_definitions',
                                                  required_params=['search_string'],
                                                  optional_params=['page_size', 'start_from', 'starts_with',
                                                                   'ends_with', 'ignore_case'],
                                                  spec_params={'metadata_element_types': ['ServiceLevelObjectives']})),
    'Solution-Blueprint-DrE': FormatSet(target_type='Solution-Blueprint-DrE',
                                        heading='Solution-Blueprint-DrE Attributes',
                                        description='Auto-generated format for Solution Blueprint (Create).', formats=[
            Format(types=['ALL'], columns=[Column(name='Display Name', key='display_name'),
                                           Column(name='Description', key='description'),
                                           Column(name='Category', key='category'),
                                           Column(name='Status', key='element_status'),
                                           Column(name='Version Identifier', key='version_id'),
                                           Column(name='Solution Components', key='solution_components'),
                                           Column(name='Qualified Name', key='qualified_name'),
                                           Column(name='GUID', key='guid')])],
                                        action=ActionParameter(function='SolutionArchitect.find_solution_blueprints',
                                                               required_params=['search_string'],
                                                               optional_params=['page_size', 'start_from',
                                                                                'starts_with', 'ends_with',
                                                                                'ignore_case'])),
    'Solution-Component-DrE': FormatSet(target_type='Solution-Component-DrE',
                                        heading='Solution-Component-DrE Attributes',
                                        description='Auto-generated format for Solution Component (Create).', formats=[
            Format(types=['ALL'], columns=[Column(name='Display Name', key='display_name'),
                                           Column(name='Qualified Name', key='qualified_name'),
                                           Column(name='Category', key='category'),
                                           Column(name='Description', key='description'),
                                           Column(name='Status', key='element_status'),
                                           Column(name='Solution Component Type', key='soln_comp_type'),
                                           Column(name='Planned Deployed Implementation Type',
                                                  key='planned_deployed_impl_type'),
                                           Column(name='Initial Status', key='initial_status'),
                                           Column(name='In Solution Components', key='in_components'),
                                           Column(name='In Solution Blueprints', key='solution_blueprints'),
                                           Column(name='In Information Supply Chains', key='in_supply_chains'),
                                           Column(name='Actors', key='actors'), Column(name='GUID', key='guid'),
                                           Column(name='Merge Update', key='merge_update')])],
                                        action=ActionParameter(function='SolutionArchitect.find_solution_components',
                                                               required_params=['search_string'],
                                                               optional_params=['page_size', 'start_from',
                                                                                'starts_with', 'ends_with',
                                                                                'ignore_case'])),
    'Solution-Role-DrE': FormatSet(target_type='Solution-Role-DrE', heading='Solution-Role-DrE Attributes',
                                   description='Auto-generated format for Solution Role (Create).', formats=[
            Format(types=['ALL'],
                   columns=[Column(name='Name', key='name'), Column(name='Description', key='description'),
                            Column(name='Title', key='title'), Column(name='Scope', key='scope'),
                            Column(name='identifier', key='identifier'),
                            Column(name='Domain Identifier', key='domain_identifier'),
                            Column(name='Category', key='category'),
                            Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid')])],
                                   action=ActionParameter(function='SolutionArchitect.find_solution_roles',
                                                          required_params=['search_string'],
                                                          optional_params=['page_size', 'start_from', 'starts_with',
                                                                           'ends_with', 'ignore_case'])),
    'Study-Project-DrE': FormatSet(target_type='Study-Project-DrE', heading='Study-Project-DrE Attributes',
                                   description='Auto-generated format for Study Project (Create).', formats=[
            Format(types=['ALL'], columns=[Column(name='Display Name', key='display_name'),
                                           Column(name='Description', key='description'),
                                           Column(name='Project Type', key='project_type'),
                                           Column(name='Category', key='category'),
                                           Column(name='Identifier', key='project_identifier'),
                                           Column(name='Mission', key='mission'),
                                           Column(name='Purposes', key='purposes'),
                                           Column(name='Start Date', key='start_date'),
                                           Column(name='Planned End Date', key='end_date'),
                                           Column(name='Priority', key='priority'),
                                           Column(name='Project Phase', key='project_phase'),
                                           Column(name='Project Status', key='project_status'),
                                           Column(name='Project Health', key='project_health'),
                                           Column(name='Qualified Name', key='qualified_name'),
                                           Column(name='GUID', key='guid')])],
                                   action=ActionParameter(function='ProjectManager.find_projects',
                                                          required_params=['search_string'],
                                                          optional_params=['page_size', 'start_from', 'starts_with',
                                                                           'ends_with', 'ignore_case'],
                                                          spec_params={'classification_names': ['StudyProject']})),
    'Task-DrE': FormatSet(target_type='Task-DrE', heading='Task-DrE Attributes',
                          description='Auto-generated format for Task (Create).', formats=[Format(types=['ALL'],
                                                                                                  columns=[Column(
                                                                                                      name='Display Name',
                                                                                                      key='display_name'),
                                                                                                      Column(
                                                                                                          name='Description',
                                                                                                          key='description'),
                                                                                                      Column(
                                                                                                          name='Project Type',
                                                                                                          key='project_type'),
                                                                                                      Column(
                                                                                                          name='Category',
                                                                                                          key='category'),
                                                                                                      Column(
                                                                                                          name='Identifier',
                                                                                                          key='project_identifier'),
                                                                                                      Column(
                                                                                                          name='Mission',
                                                                                                          key='mission'),
                                                                                                      Column(
                                                                                                          name='Purposes',
                                                                                                          key='purposes'),
                                                                                                      Column(
                                                                                                          name='Start Date',
                                                                                                          key='start_date'),
                                                                                                      Column(
                                                                                                          name='Planned End Date',
                                                                                                          key='end_date'),
                                                                                                      Column(
                                                                                                          name='Priority',
                                                                                                          key='priority'),
                                                                                                      Column(
                                                                                                          name='Project Phase',
                                                                                                          key='project_phase'),
                                                                                                      Column(
                                                                                                          name='Project Status',
                                                                                                          key='project_status'),
                                                                                                      Column(
                                                                                                          name='Project Health',
                                                                                                          key='project_health'),
                                                                                                      Column(
                                                                                                          name='Qualified Name',
                                                                                                          key='qualified_name'),
                                                                                                      Column(
                                                                                                          name='GUID',
                                                                                                          key='guid')])],
                          action=ActionParameter(function='ProjectManager.find_projects',
                                                 required_params=['search_string'],
                                                 optional_params=['page_size', 'start_from', 'starts_with', 'ends_with',
                                                                  'ignore_case'],
                                                 spec_params={'classification_names': ['Task']})),
    'Threat-Definition-DrE': FormatSet(target_type='Threat-Definition-DrE', heading='Threat-Definition-DrE Attributes',
                                       description='Auto-generated format for Threat Definition (Create).', formats=[
            Format(types=['ALL'],
                   columns=[Column(name='Display Name', key='display_name'), Column(name='Summary', key='summary'),
                            Column(name='Description', key='description'), Column(name='Category', key='category'),
                            Column(name='Domain Identifier', key='domain_identifier'),
                            Column(name='Identifier', key='identifier'),
                            Column(name='Version Identifier', key='version_identifier'),
                            Column(name='Usage', key='usage'), Column(name='Scope', key='scope'),
                            Column(name='Importance', key='importance'),
                            Column(name='Implications', key='implications'), Column(name='Outcomes', key='outcomes'),
                            Column(name='Results', key='results'), Column(name='Status', key='element_status'),
                            Column(name='User Defined Status', key='user_defined_status'),
                            Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid')])],
                                       action=ActionParameter(function='GovernanceOfficer.find_governance_definitions',
                                                              required_params=['search_string'],
                                                              optional_params=['page_size', 'start_from', 'starts_with',
                                                                               'ends_with', 'ignore_case'],
                                                              spec_params={
                                                                  'metadata_element_types': ['ThreatDefinition']}))
})

output_format_sets = combine_format_set_dicts(base_output_format_sets, generated_format_sets)


def select_output_format_set(kind: str, output_type: str) -> dict | None:
    """
    Retrieve the appropriate output set configuration dictionary based on `kind` and `output_type`.

    Intent of special output_type values:
    - "ANY": Discovery-only. Resolve the FormatSet (including aliases), action, and metadata, but DO NOT
      resolve a concrete format. Callers typically use this to check existence or to later pick a specific type
      via get_output_format_type_match(...).

    :param kind: The kind of output set (e.g., "Referenceable", "Collections"). Aliases are supported.
    :param output_type: The desired output format type (e.g., "DICT", "LIST", "REPORT"), or "ANY".
    :return: The matched output set dictionary or None if no match is found.
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
        # Include target_type for callers that need to know the intended target entity type
        output_struct["target_type"] = element.target_type
        if element.action:
            # Convert ActionParameter to dictionary for backward compatibility
            output_struct["action"] = element.action.dict()
        if element.get_additional_props:
            output_struct["get_additional_props"] = element.get_additional_props.dict()

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


def list_mcp_format_sets() -> dict:
    """
    Returns only those format set names that can be safely exposed as MCP tools.
    A format set is eligible if it has a DICT format or an ALL catch-all format.
    
    This allows MCP to prefer machine-consumable outputs and avoid side effects.
    """
    # eligible: list[str] = []
    # for name, fs in output_format_sets.items():
    #     try:
    #         # fs is a FormatSet
    #         has_dict = any("DICT" in f.types for f in fs.formats)
    #         has_all = any("ALL" in f.types for f in fs.formats)
    #         if has_dict or has_all:
    #             eligible.append(name)
    #     except Exception:
    #         # Defensive: skip malformed entries
    #         continue
    # return sorted(eligible)
    return {
        name: {
            "description": fs.description,
            "target_type": fs.target_type,
            "required_params": ", ".join(fs.action.required_params) or "",
            "optional_params": ", ".join(fs.action.optional_params) or "",
        }
        for name, fs in sorted(output_format_sets.items())
        if fs and fs.action and any(
            format_type in ["DICT", "ALL"]
            for format_obj in fs.formats
            for format_type in format_obj.types
        )
    }


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
                    if value.heading == format_set_dict["heading"] and value.description == format_set_dict[
                        "description"]:
                        # Found the format set, now find the matching format
                        for format in value.formats:
                            if output_format in format.types:
                                format_set_dict["formats"] = format.dict()
                                # Ensure target_type is included when reconstructing dict
                                format_set_dict["target_type"] = value.target_type
                                return format_set_dict

                        # Handle the fallback case of "ALL"
                        for format in value.formats:
                            if "ALL" in format.types:
                                format_set_dict["formats"] = format.dict()
                                # Ensure target_type is included when reconstructing dict
                                format_set_dict["target_type"] = value.target_type
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


def format_sets_markdown() -> str:
    """Return a markdown list of all output format sets with target type, aliases, and column names.
    
    This function is intended for external use to document available format sets.
    It generates a markdown string containing sections for each format set. For each
    set, it lists:
    - Target type
    - Aliases (if any)
    - Available formats (types) and their column display names with keys
    """
    lines: list[str] = ["# Available Output Format Sets", ""]
    for name in sorted(output_format_sets.keys()):
        fs = output_format_sets.get(name)
        if not fs:
            continue
        lines.append(f"## {name}")
        if fs.heading:
            lines.append(f"- Heading: {fs.heading}")
        if fs.description:
            lines.append(f"- Description: {fs.description}")
        lines.append(f"- Target type: {fs.target_type if hasattr(fs, 'target_type') else ''}")
        aliases = getattr(fs, 'aliases', []) or []
        if aliases:
            lines.append(f"- Aliases: {', '.join(aliases)}")
        # Formats
        try:
            fmt_list = fs.formats if hasattr(fs, 'formats') else []
            if fmt_list:
                lines.append("- Formats:")
                for fmt in fmt_list:
                    types = ", ".join(fmt.types) if getattr(fmt, 'types', None) else ""
                    lines.append(f"  - Types: {types}")
                    cols = getattr(fmt, 'columns', []) or []
                    if cols:
                        lines.append("    - Columns:")
                        for col in cols:
                            name_disp = getattr(col, 'name', '')
                            key = getattr(col, 'key', '')
                            lines.append(f"      - {name_disp} ({key})")
        except Exception as e:
            logger.debug(f"Error while documenting format set {name}: {e}")
        lines.append("")
    return "\n".join(lines) + "\n"


# Load user-defined format sets at module initialization
try:
    load_user_format_sets()
except Exception as e:
    logger.error(f"Error loading user-defined format sets: {e}")
    for key, format_set in output_format_sets.items():
        if not format_set.formats:
            logger.warning(f"FormatSet {key} has no formats defined.")
