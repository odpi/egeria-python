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
format_set = select_report_spec("Collections", "TABLE")

# Get a list of all available format sets
format_sets = report_spec_list()

# Get the heading and description of a format set
heading = get_report_spec_heading("Collections")
description = get_report_spec_description("Collections")

# Match a format set with a specific output type
matched_format_set = get_report_spec_match(format_set, "DICT")
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
            attributes=[
                Column(name="Display Name", key="display_name"),
                Column(name="Description", key="description", format=True),
            ],
        ),
    ],
)

# Add the format set to the report_specs dictionary
report_specs["Example"] = format_set
```

Exceptions
----------
This module may raise the following exceptions:
- ReportFormatCollision: Raised when duplicate report spec labels are detected while
  combining built-in, generated, config-loaded, or runtime format sets.
- FileNotFoundError: Raised when a configured JSON file containing report specs cannot be found.
- ImportError | AttributeError: Raised when a configured module function for loading
  report specs cannot be imported or resolved.
- KeyError: Raised when accessing a non-existent report spec label (e.g., direct dict access).
- ValueError: Raised for invalid or unsupported output types, or malformed structures.
- pydantic.ValidationError: Raised when constructing `FormatSet`/`Format`/`Attribute`
  instances with invalid data.
"""

import os
from pathlib import Path
from typing import List, Union

from loguru import logger

from pyegeria._output_format_models import (
    Attribute,
    Column,
    Format,
    ActionParameter,
    FormatSet,
    FormatSetDict
)

# Import generated format sets from within pyegeria package
try:
    from pyegeria.dr_egeria_reports import generated_format_sets

    logger.debug(f"Loaded {len(generated_format_sets)} generated format sets from pyegeria.dr_egeria_reports")
except (ImportError) as e:
    logger.debug(f"No pyegeria.dr_egeria_reports module found, using empty set: {e}")
    generated_format_sets = FormatSetDict()


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

# USER_FORMAT_SETS_DIR = os.path.expanduser(settings.Environment.pyegeria_user_report_specs_dir)
# Prefer new env var, fallback to old for backward compatibility
USER_FORMAT_SETS_DIR = os.getenv("PYEGERIA_USER_REPORT_SPECS_DIR", os.getenv("PYEGERIA_USER_FORMAT_SETS_DIR", "./"))
# Constants
MD_SEPARATOR = "\n---\n\n"

# Standard optional parameters for search functions
OPTIONAL_SEARCH_PARAMS= ["page_size", "start_from", "starts_with", "ends_with", "ignore_case"]
OPTIONAL_FILTER_PARAMS= ["page_size", "start_from"]

# Define shared elements
COMMON_COLUMNS = [
    Column(name='Display Name', key='display_name'),
    Column(name='Qualified Name', key='qualified_name', format=False),
    Column(name='Category', key='category'),
    Column(name='Description', key='description', format=True),
    Column(name='Status', key='status'),
    Column(name='Type Name', key='type_name'),
    Column(name='URL', key='url')
]
# Preferred terminology alias
COMMON_ATTRIBUTES = COMMON_COLUMNS

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
    attributes=COMMON_COLUMNS,
)

MERMAID_FORMAT = Format(
    types=["MERMAID"],
    attributes=[Attribute(name='Mermaid', key='mermaidGraph')]
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
    attributes=COLLECTIONS_MEMBERS_COLUMNS + [
        Column(name="GUID", key='GUID'),
    ],
)

BASIC_COLLECTIONS_COLUMNS = [
    Column(name='Qualified Name', key='qualified_name', format=False),
    Column(name='GUID', key='guid', format=True),
    Column(name='Type Name', key='type_name'),
    Column(name="Containing Members", key='collection_members'),
    Column(name="Member Of", key='member_of_collections')
]

COLLECTION_REPORT = Format(
    types=["REPORT"],
    attributes=COLLECTIONS_MEMBERS_COLUMNS + [
        Column(name="GUID", key='GUID'),
        Column(name="Mermaid", key='mermaidGraph'),
    ],
)

COLLECTION_TABLE = Format(
    types=["TABLE"],
    attributes=COLLECTIONS_MEMBERS_COLUMNS,
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
    Column(name='Qualified Name', key='qualified_name', format=False),
    Column(name="GUID", key='guid', format=True),
]
COMMON_ANNOTATIONS = {
    "wikilinks": ["[[Commons]]"]
}

WHO = [
    "Who created this?", # header
    "Who last updated this?", # header
    "Who owns this?", # ownership classification
    "Who has been working on this?"  # header - modified_users
]
WHAT = [
    "What is this?", # description
    "What is the source of this?", # metadata_collection_id/name
    "What type is this?" # type
    "What zone is this?" # Anchors classification - zone membership
]

WHEN = [
    "When was this created?", # create
    "When was this last updated?",
    "When did this become effective?",
    "When will this no longer be effective?",
    "Is this effective?",
    "What was the value last week?",
    "What was the value last month?",
    "What was the value last quarter?",
    "What was the value last year?"
]

TIME_PARAMETERS = ["as_of_time", "effective_time"]

# Modularized report_specs
base_report_specs = FormatSetDict({
    "Default": FormatSet(
        heading="Default Base Attributes",
        description="Was a valid combination of report_spec and output_format provided?",
        annotations={},  # No specific annotations
        family="General",
        question_spec=[{'perspectives':["ANY"], 'questions': WHO + WHAT + WHEN}],
        formats=[
            Format(
                types=["ALL", "TABLE", "DICT"],
                attributes=COMMON_COLUMNS + COMMON_METADATA_COLUMNS + [
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
        action=ActionParameter(
            function="ClassificationManager.get_elements_by_property_value",
            optional_params=OPTIONAL_FILTER_PARAMS + ["metadata_element_type_name"] + TIME_PARAMETERS,
            required_params=["property_value"],
            spec_params={"property_names":["displayName", "qualifiedName"]},
        )
    ),
"Element-By-Owner": FormatSet(
        heading="Elements by Owner",
        description="Return elements for the specified owner",
        annotations={},  # No specific annotations
        family="General",
        question_spec=[{'perspectives':["ANY"], 'questions': WHO + WHAT + WHEN}],
        formats=[
            Format(
                types=["ALL", "TABLE","DICT"],
                attributes=COMMON_COLUMNS + COMMON_METADATA_COLUMNS + [
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
        action=ActionParameter(
            function="ClassificationManager.get_owners_elements",
            optional_params=['body'],
            required_params=["owner_name"],
            spec_params={},
        )
    ),
    "Actor-Profiles": FormatSet(
        target_type="Actor Profile",
        heading="Actor Profile",
        description="Actor Profile Information",
        annotations={},  # No specific annotations
        family="ActorManager",
        formats=[
            Format(
                types=["ALL"],
                attributes=COMMON_COLUMNS  + COMMON_METADATA_COLUMNS + [
                    Column(name="Open Metadata Type Name", key='type_name'),
                ],
            )
        ],
        action=ActionParameter(
            function="ActorManager.find_actor_profiles",
            optional_params=   OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
            required_params=["search_string"],
            spec_params={},
        )
    ),
    "Actor-Roles": FormatSet(
        target_type="Actor Profile",
        heading="Actor Profile",
        description="Actor Profile Information",
        annotations={},  # No specific annotations
        family="ActorManager",
        formats=[
            Format(
                types=["ALL"],
                attributes=COMMON_COLUMNS + COMMON_METADATA_COLUMNS + [
                    Column(name="Scope", key='scope'),
                ],
            )
        ],
        action=ActionParameter(
            function="ActorManager.find_roles_profiles",
            optional_params=   OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
            required_params=["search_string"],
            spec_params={},
        )
    ),

    "User-Identities": FormatSet(
        target_type="User-Identity",
        heading="User Identity Information",
        description="User Identity Information",
        annotations={},  # No specific annotations
        family="ActorManager",
        formats=[
            Format(
                types=["ALL"],
                attributes=COMMON_COLUMNS + COMMON_METADATA_COLUMNS + [
                    Column(name="User ID", key='user_id'),
                    Column(name="Distinguished Name", key='distinguished_name')
                ],
            )
        ],
        action=ActionParameter(
            function="ActorManager.find_user_identities",
            optional_params=   OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
            required_params=["search_string"],
            spec_params={},
        )
    ),

    "TypeDef": FormatSet(
        target_type="TypeDef",
        heading="TypeDef",
        description="Attributes that describe TypeDefs",
        annotations={},  # No specific annotations
        family="TypeDef",
        formats=[
            Format(
                types=["ALL"],
                attributes=[
                    Column(name='Type Name', key='name'),
                    Column(name="Category", key='category'),
                    Column(name="Description", key='description'),
                    Column(name="Bean Class", key='beanClassName'),
                    Column(name="Initial Status", key='initialStatus'),
                    Column(name="Description Wiki", key='descriptionWiki'),

                ],
            )
        ],
    ),

    "Valid-Values": FormatSet(
        target_type="Valid-Values",
        heading="Valid Values",
        description="Attributes that describe valid values",
        annotations={},  # No specific annotations
        family="Valid-Values",
        formats=[
            Format(
                types=["ALL"],
                attributes= [
                    Column(name='Name', key='display_name'),
                    Column(name="Category", key='category'),
                    Column(name="Property Name", key='property_name'),
                    Column(name="Description", key='description'),
                    Column(name="Preferred Value", key='preferred_value'),
                    Column(name="Data Type", key='dataType'),
                    Column(name="Is Case Sensitive", key='is_case_sensitive'),
                    Column(name="Additional Properties", key='additional_properties'),

                ],
            )
        ],
        action=ActionParameter(
            function="ValidValueManager.find_valid_values",
            optional_params=   OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS + ["type_name"],
            required_params=["property_name"],
            spec_params={},
        )
    ),

"Engine-Actions": FormatSet(
        target_type="Referenceable",
        heading="Engine Actions",
        description="A Display of Engine Actions",
        annotations={},  # No specific annotations
        family="AutomatedCuration",
        formats=[
            Format(
                types=["ALL"],
                attributes=COMMON_COLUMNS + COMMON_METADATA_COLUMNS + [
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
"Asset-Graph": FormatSet(
        target_type="Asset",
        heading="Asset Graph",
        description="Attributes that apply to all Assets",
        annotations={},  # No specific annotations
        family="AssetCatalog",
        formats=[
            Format(
                types=["ALL"],
                attributes=COMMON_COLUMNS + COMMON_METADATA_COLUMNS + [
                    Column(name="Classifications", key='classifications'),
                    Column(name="Created By", key='created_by'),
                    Column(name="Create Time", key='create_time'),
                    Column(name="Updated By", key='updated_by'),
                    Column(name="Update Time", key='update_time'),
                    Column(name="Version", key='version'),
                    Column(name="Open Metadata Type Name", key='type_name'),
                    Column(name="Mermaid Graph", key='mermaidGraph'),
                    Column(name="Anchor Graph", key='anchorMermaidGRaph'),
                    Column(name="Field Level Lineage Graph", key='fieldLevelLineageGraph'),
                ],
            )
        ],
    action=ActionParameter(
        function="ServerClient.get_asset_graph",
        optional_params=   OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS ,
        required_params=["asset_guid"],
        spec_params={},
    )
    ),
    "Common-Mermaid": FormatSet(
        target_type="Referenceable",
        heading="Common Attributes with Mermaid",
        description="Common Attributes and all Mermaid graphs.",
        annotations={},  # No specific annotations
        family="General",
        formats=[
            Format(
                types=["DICT", "REPORT"],
                attributes=[
                    Column(name='Display Name', key='display_name'),
                    Column(name="Qualified Name", key='qualified_name'),
                    Column(name="Description", key='description'),
                    Column(name="GUID", key='guid'),
                    Column(name="Mermaid Graph", key='mermaidGraph'),
                    Column(name="Anchor Mermaid Graph", key='anchorMermaidGraph'),
                    Column(name="Information Supply Chain Mermaid Graph", key='informationSupplyChainMermaidGraph'),
                    Column(name="Field Level Lineage Graph", key='fieldLevelLineageGraph'),
                    Column(name="Action Mermaid Graph", key='actionMermaidGraph'),
                    Column(name="Local Lineage Graph", key="localLineageGraph"),
                    Column(name="Edge Mermaid", key="edgeMermaidGraph"),
                    Column(name="ISC Implementation Graph", key='iscImplementationGraph'),
                    Column(name="Specification Mermaid Graph", key='specificationMermaidGraph'),
                    Column(name="Solution Blueprint Mermaid Graph", key='solutionBlueprintMermaidGraph'),
                    Column(name="Solution Subcomponent Mermaid Graph", key='solutionSubcomponentMermaidGraph'),

                ],
            ),
        Format(
            types=["MERMAID"],
            attributes = [
                   Column(name="Mermaid Graph", key='mermaidGraph')
            ])
        ],

    ),
    "Tech-Type-Elements": FormatSet(
        target_type="TechTypeElements",
        heading="Technology Type Elements",
        description="Elements of a Technology",
        annotations={},  # No specific annotations
        family="Automated Curation",
        formats=[
            Format(
                types=[ "MD", "FORM", ],
                attributes= COMMON_HEADER_COLUMNS + [
                    Column(name='Display Name', key='display_name'),
                    Column(name="Qualified Name", key='qualified_name'),
                    Column(name="GUID", key='guid', format=True),
                    Column(name="Description", key='description'),
                    Column(name='Metadata Collection Name', key='metadata_collection_name', format=True),
                    Column(name="Deployed Implementation", key='deployedImplementationType'),
                    Column(name="Mermaid Graph", key='mermaidGraph'),
                    Column(name="Specification Mermaid Graph", key='specificationMermaidGraph')
                ],
            ),
            Format(
                types=[ "MERMAID","HTML", "REPORT"],
                attributes= COMMON_HEADER_COLUMNS + [
                    Column(name='Display Name', key='display_name'),
                    Column(name="Qualified Name", key='qualified_name'),
                    Column(name="GUID", key='guid', Format = True),
                    Column(name="Description", key='description'),
                    Column(name="Deployed Implementation", key='deployedImplementationType'),
                    Column(name="Mermaid Graph", key='mermaidGraph'),
                    Column(name="Specification Mermaid Graph", key='specificationMermaidGraph')
                ]
            ),
            Format(
                types=[ "DICT","TABLE", "LIST"],
                attributes= [
                    Column(name='Display Name', key='display_name'),
                    Column(name="Qualified Name", key='qualified_name'),
                    Column(name="GUID", key='guid', Format = True),
                    Column(name="Description", key='description'),
                    Column(name="Deployed Implementation", key='deployedImplementationType'),
                ]
            )
        ],
        action=ActionParameter(
            function="EgeriaTech.get_technology_type_elements",
            optional_params=   OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS + ["get_templates"],
            required_params=["filter"],
            spec_params={},
        )
    ),
    "Search-Keywords": FormatSet(
        heading="Search Keyword Report",
        description="A report of elements with search keywords matching the specified string",
        annotations={},  # No specific annotations
        family="Feedback Manager",
        formats=[
            Format(
                types=["ALL"],
                attributes=[
                    Column(name='Search Keyword', key='keyword'),
                    Column(name="Search Keyword GUID", key='guid'),
                    Column(name="Element Display Name", key='element_display_name'),
                    Column(name="Element GUID", key='element_guid'),
                    Column(name="Element Type", key='element_type'),
                    Column(name="Element Description", key='element_description'),
                    Column(name="Element Category", key='element_category'),
                ],
            )
        ],
        action=ActionParameter(
            function="_client_new.find_search_keywords",
            optional_params=OPTIONAL_SEARCH_PARAMS,
            required_params=["search_string"],
            spec_params={},
        ),
        get_additional_props=ActionParameter(
            function="_client_extract_element_properties_for_keyword",
            required_params=[],
            spec_params={},
        )
    ),
    "Tech-Type-Details": FormatSet(
        target_type="TechTypeDetail",
        heading="Technology Type Details",
        description="Details of a Technology Type Valid Value.",
        annotations={},  # No specific annotations
        family="Automated Curation",
        formats=[
            Format(
                types=["ALL"],
                attributes=[
                    Column(name='Display Name', key='display_name'),
                    Column(name="Qualified Name", key='qualified_name'),
                    Column(name="GUID", key='guid'),
                    Column(name="Description", key='description'),
                    Column(name="Catalog Template Placeholders", key='catalog_template_specs'),
                ],
            )
        ],
        action=ActionParameter(
            function="ServerClient.get_tech_type_detail",
            optional_params=   OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
            required_params=["filter"],
            spec_params={},
        )
    ),
    "Tech-Type-Processes": FormatSet(
        target_type="TechTypeDetail",
        heading="Technology Type Processes",
        description="Governance Processes for a Tech Type",
        annotations={},  # No specific annotations
        family="Automated Curation",
        formats=[
            Format(
                types=["REPORT","LIST","FORM","MD", "TABLE"],
                attributes=[
                    Column(name='Display Name', key='display_name'),
                    Column(name="Qualified Name", key='qualified_name'),
                    Column(name="Governance Processes", key='governance_processes'),
                ],
            ),
            Format(
                types=["DICT"],
                attributes=[
                    Column(name='Display Name', key='display_name'),
                    Column(name="Qualified Name", key='qualified_name'),
                    Column(name="Governance Processes", key='governance_processes_d'),
                    Column(name="Mermaid", key='mermaidGraph'),
                    Column(name="Mermaid Specification", key='specificationMermaidGraph'),
                ],
            ),
            Format(
                types=["MERMAID"],
                attributes=[
                    Column(name="Mermaid", key='mermaidGraph'),
                    Column(name="Mermaid Specification", key='specificationMermaidGraph'),
                ],
            )
        ],
        action=ActionParameter(
            function="ServerClient.get_tech_type_detail",
            optional_params=   OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
            required_params=["filter"],
            spec_params={},
        )
    ),
    "Tech-Types": FormatSet(
        target_type="TechTypeDetail",
        heading="Technology Type Details",
        description="Details of a Technology Type Valid Value.",
        annotations={},  # No specific annotations
        family="Automated Curation",
        formats=[
            Format(
                types=["ALL"],
                attributes=[
                    Column(name='Display Name', key='display_name'),
                    Column(name="Qualified Name", key='qualified_name'),
                    Column(name="GUID", key='guid'),
                    Column(name="Description", key='description'),
                    Column(name="Reference URL", key='url'),
                ],
            )
        ],
        action=ActionParameter(
            function="ServerClient.find_technology_types",
            optional_params=OPTIONAL_SEARCH_PARAMS,
            required_params=["search_string"],
            spec_params={},
        )
    ),

    "Journal-Entry-DrE": FormatSet(
        target_type="Notification",
        heading="Journal Entry",
        description="Details of a journal entry.",
        annotations={},  # No specific annotations
        family="Feedback Manager",
        formats=[
            Format(
                types=["ALL"],
                attributes=[
                    Column(name='Journal Name', key='note_log_name'),
                    Column(name='Journal Qualified Name', key='note_log_qualified_name'),
                    Column(name="Journal Entry Qualified Name", key='qualified_name'),
                    Column(name="Journal Entry GUID", key='guid'),
                    Column(name="Journal Entry", key='description')
                ],
            )
        ],
        action=ActionParameter(
            function="ServerClient.find_notes",
            optional_params=OPTIONAL_SEARCH_PARAMS,
            required_params=["search_string"],
            spec_params={},
        )
    ),
    "Informal-Tags-DrE": FormatSet(
        target_type="Informal Tag",
        heading="Informal Tags",
        description="Details of Informal Tags.",
        annotations={},  # No specific annotations
        family="Feedback Manager",
        formats=[
            Format(
                types=["ALL"],
                attributes=[
                    Column(name='Tag Name', key='display_name'),
                    Column(name='Qualified Name', key='qualified_name'),
                    Column(name="Description", key='description'),
                    Column(name="GUID", key='guid'),
                    Column(name="Tagged Elements", key='tagged_elements'),
                ],
            )
        ],
        action=ActionParameter(
            function="ServerClient.find_tags",
            optional_params=OPTIONAL_SEARCH_PARAMS,
            required_params=["search_string"],
            spec_params={},
        )
    ),

    "ExternalReference": FormatSet(
        target_type="External Reference",
        heading="External Reference Attributes",
        description="Attributes that apply to all External References.",
        annotations={},
        family="External References",
        aliases=["ExternalDataSource", "ExternalModelSource", "External References"],
        formats=[
            Format(
                types=["ALL"],
                attributes=EXT_REF_COLUMNS,
            )
        ],
        action=ActionParameter(
            function="ExternalReference.find_external_references",
            optional_params=OPTIONAL_SEARCH_PARAMS,
            required_params=["search_string"],
            spec_params={},
        )
    ),
    "RelatedMedia": FormatSet(
        target_type="Related Media",
        heading="Related Media Attributes",
        description="Attributes that apply to related media.",
        annotations={},
        family="External References",
        formats=[
            Format(
                types=["ALL", "LIST"],
                attributes=EXT_REF_COLUMNS + [
                    Column(name="Media Type", key='media_type'),
                    Column(name="Media Type Other Id", key='media_type_other_id'),
                    Column(name="Default Media Usage", key='default_media_usage'),
                    Column(name="Default Media Usage Other Id", key='default_media_usage_other_id')
                ],
            )
        ],
        action=ActionParameter(
            function="ExternalReference.find_external_references",
            optional_params=OPTIONAL_SEARCH_PARAMS,
            required_params=["search_string"],
            spec_params={"metadata_element_subtypes": ["RelatedMedia"]},
        )

    ),
    "CitedDocument": FormatSet(
        target_type="Cited Document",
        heading="Cited Document Attributes",
        description="Attributes that apply to all Cited Documents.",
        annotations={},
        family="External References",
        formats=[
            Format(
                types=["ALL", "LIST"],
                attributes=EXT_REF_COLUMNS + [
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
            optional_params=OPTIONAL_SEARCH_PARAMS,
            required_params=["search_string"],
            spec_params={"metadata_element_subtypes": ["CitedDocument"]},
        )

    ),
    "Projects": FormatSet(
        target_type="Project",
        heading="Project Attributes",
        description="Attributes that apply to all Projects.",
        annotations={},
        family="Project Manager",
        formats=[
            Format(
                types=["ALL", "LIST"],
                attributes=PROJECT_COLUMNS
            )
        ],
        action=ActionParameter(
            function="ProjectManager.find_projects",
            optional_params=OPTIONAL_SEARCH_PARAMS,
            required_params=["search_string"],
            spec_params={},
        )

    ),
    "Glossaries": FormatSet(
        target_type="Glossary",
        heading="Glossary Attributes",
        description="Attributes that apply to all Glossaries.",
        annotations={"wikilinks": ["[[Glossaries]]"]},
        family="Glossary Manager",
        formats=[
            Format(
                types=["ALL"],
                attributes=GLOSSARY_COLUMNS
            )
        ],
        action=ActionParameter(
            function="GlossaryManager.find_glossaries",
            optional_params=OPTIONAL_SEARCH_PARAMS,
            required_params=["search_string"],
            spec_params={},
        )
    ),
    "Glossary-Terms": FormatSet(
        target_type="Term",
        # aliases=["Glossary-Terms"],
        heading="Basic Glossary Term Attributes",
        description="Attributes that apply to all Basic Glossary Terms.",
        annotations={},
        family="Glossary Manager",
        formats=[
            Format(
                types=["ALL"],
                attributes=COMMON_COLUMNS + COMMON_METADATA_COLUMNS + [
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
            optional_params=OPTIONAL_SEARCH_PARAMS,
            spec_params={},
        )
    ),
    "Help-Terms": FormatSet(
        target_type="Term",
        heading="Display Help for Dr.Egeria Commands",
        description="Designed for help output of Dr.Egeria commands.",
        annotations={"wikilinks": ["[[Help]]", "[[Dr.Egeria]]"]},
        family="General",
        formats=[
            Format(

                types=["DICT", "FORM", "REPORT", "LIST", "TABLE"],
                attributes=[
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
            optional_params=OPTIONAL_SEARCH_PARAMS,
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
        family="Collection Manager",
        formats=[MERMAID_FORMAT, COLLECTION_DICT, COLLECTION_TABLE, COLLECTION_REPORT, COMMON_FORMATS_ALL],
        # Reusing common formats
        action=ActionParameter(
            function="CollectionManager.find_collections",
            required_params=["search_string"],
            optional_params=OPTIONAL_SEARCH_PARAMS,
            spec_params={},
        )
    ),
    "BasicCollections": FormatSet(
        target_type="Collection",
        heading="Common Collection Information",
        description="Attributes generic to all Collections.",
        aliases=[],
        annotations=COMMON_ANNOTATIONS,
        family="Collection Manager",
        formats=[Format(
            types=["ALL"],
            attributes=BASIC_COLLECTIONS_COLUMNS,
        )],  # Reusing common formats
        action=ActionParameter(
            function="CollectionManager.find_collections",
            required_params=["search_string"],
            optional_params=OPTIONAL_SEARCH_PARAMS,
            spec_params={},
        )
    ),
    "Folders": FormatSet(
        target_type="Folder",
        heading="Common Folder Information",
        description="Attributes generic to all Folders.",
        aliases=[],
        annotations=COMMON_ANNOTATIONS,
        family="External References",
        formats=[Format(
            types=["ALL"],
            attributes=BASIC_COLLECTIONS_COLUMNS,
        )],  # Reusing common formats
        action=ActionParameter(
            function="CollectionManager.find_collections",
            required_params=["search_string"],
            optional_params=OPTIONAL_SEARCH_PARAMS,
            spec_params={"metadata_element_typs": ["FolderCollection"]},
        )
    ),

    "Collection Members": FormatSet(
        target_type="Collection",
        heading="Collection Membership Information",
        description="Attributes about all CollectionMembers.",
        aliases=["CollectionMember", "Member", "Members"],
        annotations={"wikilinks": ["[[CollectionMembers]]"]},
        family="External References",
        formats=[COLLECTION_DICT, COLLECTION_TABLE],
        action=ActionParameter(
            function="CollectionManager.get_collection_members",
            required_params=["collection_guid"],
            optional_params= OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
            spec_params={"output_format": "DICT"},
        )
    ),
    "Solution-Blueprint": FormatSet(
        target_type="SolutionBlueprint",
        heading="Solution Blueprint Report",
        description="Details of a Solution Blueprint.",
        aliases=[],
        annotations={"Wikilinks": ["[[Solution-Blueprint]]"]},
        family="Solution Architect",
        formats=[
            Format(
                types=["DICT", "TABLE", "LIST", "MD", "FORM"],
                attributes=COLLECTIONS_MEMBERS_COLUMNS
            ),
            Format(
                types=["REPORT", "HTML"],
                attributes=COLLECTIONS_MEMBERS_COLUMNS + [
                    Column(name="GUID", key='GUID'),
                    Column(name="Mermaid", key='mermaidGraph'),
                    Column(name="Solution Blueprint Mermaid Graph", key='solutionBlueprintMermaidGraph'),
                ]),
            Format(
                types=["MERMAID"],
                attributes=[
                    Column(name="Mermaid", key='mermaidGraph'),
                    Column(name="Solution Blueprint Mermaid Graph", key='solutionBlueprintMermaidGraph'),
                ])
        ],
        action=ActionParameter(
            function="SolutionArchitect.find_solution_blueprints",
            required_params=["search_string"],
            optional_params=OPTIONAL_SEARCH_PARAMS,
            spec_params={},
        ),
    ),
    "Registered-Services": FormatSet(
        target_type="Registered-Services",
        heading="Registered Services",
        description="Registered services on the OMAG Server Platform.",
        annotations={},
        family="Platform",
        formats=[
            Format(
                types=["ALL"],
                attributes=[
                    Column(name="Service Name", key='service_name'),
                    Column(name="Description", key='service_description'),
                    Column(name="URL Marker", key='service_url_marker'),
                    Column(name="Service Type", key='service_type'),
                    Column(name="Wiki", key='service_wiki'),
                    Column(name="Conformance Profile", key='conformance_profile'),
                ],
            )
        ],
    ),
    "Severity-Definitions": FormatSet(
        target_type="Severity-Definitions",
        heading="Audit Log Severity Definitions",
        description="Severity definitions available in the OMAG Server.",
        annotations={},
        family="Platform",
        formats=[
            Format(
                types=["ALL"],
                attributes=[
                    Column(name="Name", key='name'),
                    Column(name="Ordinal", key='ordinal'),
                    Column(name="Description", key='description'),
                    Column(name="Severity Code", key='severity_code'),
                    Column(name="System Action", key='system_action'),
                    Column(name="User Action", key='user_action'),
                ],
            )
        ],
    ),
    "Asset-Types": FormatSet(
        target_type="Asset-Types",
        heading="Asset Types",
        description="Types of assets available in the catalog.",
        annotations={},
        family="AssetCatalog",
        formats=[
            Format(
                types=["ALL"],
                attributes=[
                    Column(name="Type Name", key='type_name'),
                    Column(name="Display Name", key='display_name'),
                    Column(name="Description", key='description'),
                    Column(name="Super Type", key='super_type'),
                ],
            )
        ],
    ),
    "Digital-Product-Catalog": FormatSet(
        target_type="DigitalProductCatalog",
        heading="Catalogs for Digital Products",
        description="Attributes generic to all Digital Product Catalogs..",
        aliases=["Product Catalog", "DataProductCatalog"],
        annotations={"Wikilinks": ["[[Digital Products]]"]},
        family="Product Manager",
        question_spec=[{'perspectives':["ANY"], 'questions': WHO + WHAT + WHEN}],
        formats=[
            Format(
                types=["DICT", "TABLE", "LIST", "MD", "FORM"],
                attributes=COLLECTIONS_MEMBERS_COLUMNS
            ),
            Format(
                types=["REPORT", "HTML"],
                attributes=COLLECTIONS_MEMBERS_COLUMNS + [
                    Column(name="GUID", key='GUID'),
                    Column(name="Mermaid", key='mermaidGraph'),
                ]),
            Format(
                types=["MERMAID"],
                attributes=[
                    Column(name="Mermaid", key='mermaidGraph'),
                ])
        ],
        action=ActionParameter(
            function="CollectionManager.find_collections",
            required_params=["search_string"],
            optional_params=OPTIONAL_SEARCH_PARAMS + ['body'],
            spec_params={"metadata_element_subtypes": ["DigitalProductCatalog"]},
        ),
    ),
    "Digital-Product-Catalog-MyE": FormatSet(
        target_type="DigitalProductCatalog",
        heading="Catalogs for Digital Products",
        description="Attributes generic to all Digital Product Catalogs..",
        aliases=[],
        annotations={},
        family="Product Manager",
        formats=[
            Format(
                types=["DICT", "TABLE", "LIST", "MD", "FORM", "REPORT"],
                attributes=COMMON_COLUMNS + [
                    Column(name="Containing Members", key='collection_members'),
                    Column(name="Member Of", key='member_of_collections')
                ]
            ),

        ],
        action=ActionParameter(
            function="CollectionManager.find_collections",
            required_params=["search_string"],
            optional_params=OPTIONAL_SEARCH_PARAMS,
            spec_params={"metadata_element_subtypes": ["DigitalProductCatalog"]},
        ),
    ),

    "Digital-Products": FormatSet(
        target_type="DigitalProduct",
        heading="Digital Product Information",
        description="Attributes useful to Digital Products.",
        aliases=["DigitalProduct", "DataProducts"],
        annotations={},
        family="Product Manager",
        question_spec=[{'perspectives':["ANY"], 'questions': WHO + WHAT + WHEN}],
        formats=[
            Format(
                types=["FORM", "DICT", "TABLE", "LIST"],
                attributes=COMMON_COLUMNS + [
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
                types=["REPORT", "HTML"],
                attributes=COMMON_COLUMNS + [
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
                    Column(name="Mermaid", key="mermaid")
                ],
            )
        ],
        action=ActionParameter(
            function="CollectionManager.find_collections",
            required_params=["search_string"],
            optional_params=OPTIONAL_SEARCH_PARAMS,
            spec_params={"metadata_element_subtypes": ["DigitalProduct"]},
        ),
        get_additional_props=ActionParameter(
            function="CollectionManager._extract_digital_product_properties",
            required_params=[],
            spec_params={},
        )
    ),
    "Digital-Products-MyE": FormatSet(
        target_type="DigitalProduct",
        heading="Digital Product Information",
        description="Attributes useful to Digital Products.",
        aliases=[],
        annotations={},
        family="Product Manager",
        formats=[
            Format(
                types=["FORM", "DICT", "TABLE", "LIST", "MD"],
                attributes=COMMON_COLUMNS + [
                    Column(name="Status", key='status'),
                    Column(name='Product Name', key='product_name'),
                    Column(name='Members', key='members', format=True),
                    Column(name='Product Manager', key='assigned_actors'),
                ]),
            Format(
                types=["REPORT", "HTML"],
                attributes=COMMON_COLUMNS + [
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
                    Column(name="Mermaid", key="mermaid")
                ],
            )
        ],
        action=ActionParameter(
            function="CollectionManager.find_collections",
            required_params=["search_string"],
            optional_params=OPTIONAL_SEARCH_PARAMS,
            spec_params={"metadata_element_subtypes": ["DigitalProduct"]},
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
        family="Product Manager",
        formats=[
            Format(
                types=["REPORT", "DICT", "TABLE", "LIST", "FORM"],
                attributes=COMMON_COLUMNS + COMMON_HEADER_COLUMNS + [
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
            spec_params={"metadata_element_subtypes": ["Agreement"]},
            # spec_params={},
        ),
        get_additional_props=ActionParameter(
            function="CollectionManager._extract_agreement_properties",
            required_params=[],
            spec_params={},
        ),
    ),

    "Data-Dictionaries": FormatSet(
        target_type="Data Dictionary",
        heading="Data Dictionary Information",
        description="Attributes about Data Dictionary.",
        aliases=["Data Dict", "Data Dictionary"],
        annotations={"wikilinks": ["[[Data Dictionary]]"]},
        family="Data Designer",
        formats=[COMMON_FORMATS_ALL],  # Reusing common formats and columns
        action=ActionParameter(
            function="CollectionManager.find_collections",
            required_params=["search_string"],
            spec_params={"metadata_element_subtypes": ["DataDictionary"]},
        )
    ),

    "Data-Specifications": FormatSet(
        target_type="Data Specification",
        heading="Data Specification Information",
        description="Attributes about Data Specification.",
        aliases=["Data Spec", "DataSpec", "DataSpecification"],
        annotations={"wikilinks": ["[[Data Specification]]"]},
        family="Data Designer",
        formats=[
            Format(types=["REPORT", "HTML"], attributes=COMMON_COLUMNS + [Column(name="Mermaid", key='mermaidGraph'), ]),
            Format(types=["MERMAID"], attributes=[
                Column(name="Display Name", key='display_name'),
                Column(name="Mermaid", key='mermaidGraph'),
            ]),
            Format(types=["ALL"], attributes=COMMON_COLUMNS)],  # Reusing common formats and columns
        action=ActionParameter(
            function="CollectionManager.find_collections",
            required_params=["search_string"],
            spec_params={"metadata_element_subtypes": ["DdataSpec"]},
        )
    ),

    "Data-Structures": FormatSet(
        target_type="Data Structure",
        heading="Data Structure Information",
        description="Attributes about Data Structures.",
        aliases=["Data Structure", "DataStructures", "Data Structures", "Data Struct", "DataStructure"],
        annotations={"wikilinks": ["[[Data Structure]]"]},
        family="Data Designer",
        formats=[Format(types=["FORM", "DICT", "LIST"], attributes=COMMON_COLUMNS +
                                                                   [
                                                                       Column(name="In Data Specifications",
                                                                              key='in_data_spec'),
                                                                       Column(name="In Data Dictionaries",
                                                                              key='in_data_dictionary'),
                                                                       Column(name="Member Data Fields",
                                                                              key='member_data_fields')]
                        ),  # Reusing common formats and columns
                 Format(types=["REPORT"], attributes=COMMON_COLUMNS +
                                                     [
                                                         Column(name="In Data Specifications", key='in_data_spec'),
                                                         Column(name="In Data Dictionaries", key='in_data_dictionary'),
                                                         Column(name="Member Data Fields", key='member_data_fields'),
                                                         Column(name="Mermaid", key='mermaidGraph')
                                                     ]
                        )],
        action=ActionParameter(
            function="DataDesigner.find_data_structures",
            required_params=["search_string"],
            spec_params={},
        )
    ),

    "Data-Fields": FormatSet(
        target_type="Data Field",
        heading="Data Field Information",
        description="Attributes about Data Fields.",
        aliases=["Data Field", "Data Fields", "DataFields"],
        annotations={"wikilinks": ["[[Data Field]]"]},
        family="Data Designer",
        formats=[Format(types=["MD", "FORM", "DICT", "LIST"], attributes=COMMON_COLUMNS + [
                            Column(name="In Data Dictionaries", key='in_data_dictionary'),
                            Column(name="In Data Structure", key='in_data_structure')]),
                 Format(types=["REPORT"], attributes=COMMON_COLUMNS +
                         [
                             Column(name="In Data Structure", key='in_data_structure'),
                             Column(name="In Data Dictionaries", key='in_data_dictionary'),
                             Column(name="Member Data Fields", key='member_data_fields'),
                             Column(name="Mermaid", key='mermaidGraph')
                         ]
                        )],

        action=ActionParameter(
            function="DataDesigner.find_data_fields",
            required_params=["search_string"],
            spec_params={},
        )
    ),
    "Data-Classes": FormatSet(
        target_type="Data Class",
        heading="Data Class Information",
        description="Attributes about Data Classes",
        aliases=["Data Field", "Data Fields", "DataFields"],
        annotations={"wikilinks": ["[[Data Field]]"]},
        family="Data Designer",
        formats=[Format(types=["MD", "FORM", "DICT", "LIST"], attributes=COMMON_COLUMNS + [
                        Column(name="Data Type", key='data_type'),
                        Column(name="Specification", key='specification'),
                        Column(name="In Data Dictionaries", key='in_data_dictionary'),
                        Column(name="In Data Structure", key='in_data_structure')]),
                 Format(types=["REPORT"], attributes=COMMON_COLUMNS +
                     [
                         Column(name="Data Type", key='data_type'),
                         Column(name="Specification", key='specification'),
                         Column(name="In Data Dictionaries", key='in_data_dictionary'),
                         Column(name="Containing Data Class", key='containing_data_class'),
                         Column(name="Specializes", key='specializes_data_class'),
                         Column(name="Mermaid", key='mermaidGraph')
                     ]
                        )],

        action=ActionParameter(
            function="DataDesigner.find_data_classes",
            required_params=["search_string"],
            spec_params={},
        )
    ),
    'External-References': FormatSet(target_type='External-Reference',
                                     heading='External-Reference Attributes',
                                     description='External References',
                                     family="External References",
                                     formats=[
                                         Format(types=['MD', 'FORM', 'DICT'],
                                                attributes=[Column(name='Display Name', key='display_name'),
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
                                         Format(types=['TABLE', 'LIST'],
                                                attributes=[Column(name='Display Name', key='display_name'),

                                                            Column(name='Category', key='category'),
                                                            Column(name='Reference Title', key='reference_title'),

                                                            Column(name='Sources', key='reference_sources'),
                                                            Column(name='License', key='license'),
                                                            Column(name='Qualified Name', key='qualified_name'),
                                                            ]),
                                         Format(types=["REPORT"],
                                                attributes=[Column(name='Display Name', key='display_name'),
                                                            Column(name='Description', key='description'),
                                                            Column(name='Category', key='category'),
                                                            Column(name='Reference Title', key='reference_title'),
                                                            Column(name='Reference Abstract', key='reference_abstract'),
                                                            Column(name='Organization', key='organization'),
                                                            Column(name='URL', key='reference_url'),
                                                            Column(name='Sources', key='reference_sources'),
                                                            Column(name='License', key='license'),
                                                            Column(name='Qualified Name', key='qualified_name'),
                                                            Column(name='Mermaid', key='mermaidGraph'),
                                                            ]),

                                         Format(types=["MERMAID"], attributes=[Column(name='Mermaid', key='mermaidGraph')]),
                                     ],
                                     action=ActionParameter(function='ExternalReference.find_external_references',
                                                            required_params=['search_string'],
                                                            optional_params=['page_size', 'start_from',
                                                                             'starts_with', 'ends_with',
                                                                             'ignore_case'], spec_params={
                                             'metadata_element_subtypes': ['ExternalReference']})
                                     ),

    "Governance Basics": FormatSet(
        target_type="Governance Definition",
        heading="Basic Governance-Definitions Information",
        description="Core Attributes useful to Governance-Definitions.",
        aliases=["BasicGovernance"],
        annotations={"wikilinks": ["[[Governance]]"]},
        family="Governance Officer",
        formats=[Format(types=["ALL"], attributes=GOVERNANCE_DEFINITIONS_BASIC)],
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
        family="Governance Officer",
        question_spec=[{'perspectives':["ANY"], 'questions': WHO + WHAT + WHEN}],
        formats=[Format(types=["ALL"], attributes=GOVERNANCE_DEFINITIONS_COLUMNS)],
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
        family="Governance Officer",
        formats=[Format(types=["ALL"], attributes=GOVERNANCE_DEFINITIONS_BASIC)],
        action=ActionParameter(
            function="GovernanceOfficer.find_governance_definitions",
            required_params=["search_string"],
            spec_params={"metadata_element_subtypes": ["GovernancePrinciple", "GovernanceStrategy", "GovernanceResponse"]},
        )
    ),
    'Governance-Controls': FormatSet(target_type='Governance Control',
                                    heading='Control Attributes',
                                    description='Governance Control (Create).',
                                    family="Governance Officer",
                                    question_spec=[{'perspectives':["Governance"], 'questions': WHO + WHAT + WHEN + [
                                        "What governance controls have been defined?",
                                        "What measurements and measurement targets have been defined for governance controls?",
                                        "What are the implications of the governance controls?",
                                        "What are the risks associated with the governance controls?",
                                    ]}],
                                    formats=[
                                        Format(types=['DICT', 'MD', 'FORM', 'REPORT'],
                                               attributes=[Column(name='Display Name', key='display_name'),
                                                           Column(name='Summary', key='summary'),
                                                           Column(name='Description', key='description'),
                                                           Column(name='Category', key='category'),
                                                           Column(name='Domain Identifier', key='domain_identifier'),
                                                           Column(name='Identifier', key='identifier'),
                                                           Column(name='Version Identifier', key='version_identifier'),
                                                           Column(name='Usage', key='usage'),
                                                           Column(name='Scope', key='scope'),
                                                           Column(name='Importance', key='importance'),
                                                           Column(name='measurement', key='measurement'),
                                                           Column(name='target', key='target'),
                                                           Column(name='Implications', key='implications'),
                                                           Column(name='Outcomes', key='outcomes'),
                                                           Column(name='Results', key='results'),
                                                           Column(name='Status', key='element_status'),
                                                           Column(name='User Defined Status',
                                                                  key='user_defined_status'),
                                                           Column(name='Qualified Name', key='qualified_name'),
                                                           Column(name='GUID', key='guid')
                                                           ]),
                                        Format(types=['TABLE', 'LIST'],
                                               attributes=[Column(name='Display Name', key='display_name'),
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
                                        optional_params=OPTIONAL_SEARCH_PARAMS,
                                        spec_params={"metadata_element_subtypes": ["GovernanceControl"]},
                                    )
        ),
'Governance-Process': FormatSet(target_type='Governance Process',
                                    heading='Governance Process Attributes',
                                    description='Governance Process Attributes.',
                                    family="Governance Officer",
                                    formats=[
                                        Format(types=['TABLE','LIST', 'MD', 'FORM', 'REPORT'],
                                               attributes=[Column(name='Display Name', key='display_name'),
                                                           Column(name='Description', key='description'),
                                                           Column(name='Category', key='category'),
                                                           Column(name='Qualified Name', key='qualified_name'),
                                                           Column(name='GUID', key='guid')
                                                           ]),
                                        Format(types=['DICT'],
                                               attributes=[Column(name='Display Name', key='display_name'),
                                                           Column(name='Summary', key='summary'),
                                                           Column(name='Category', key='category'),
                                                           Column(name='Status', key='element_status'),
                                                           Column(name='Qualified Name', key='qualified_name'),
                                                           ])
                                    ],
                                    action=ActionParameter(
                                        function="GovernanceOfficer.find_governance_definitions",
                                        required_params=["search_string"],
                                        optional_params=OPTIONAL_SEARCH_PARAMS,
                                        spec_params={"metadata_element_subtypes": ["GovernanceActionProcess"]},
                                    )
                     ),
    "Valid-Value-Def": FormatSet(
        target_type="Valid Value Definition",
        heading="Valid Value Definitions Information",
        description="Attributes useful to Valid Value Definitions.",
        aliases=[],
        annotations={"wikilinks": ["[[VV-Def]]"]},
        family="General",
        formats=[Format(types=["ALL"], attributes=COMMON_COLUMNS +
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

    'License-Type': FormatSet(target_type='License Type',
                              heading='License Type Attributes',
                              description='Attributes of a License type.',
                              family="Governance Officer",
                              formats=[
                                  Format(types=['DICT', 'MD', 'FORM', 'REPORT'],
                                         attributes=[Column(name='Display Name', key='display_name'),
                                                     Column(name='Summary', key='summary'),
                                                     Column(name='Description', key='description'),
                                                     Column(name='Category', key='category'),
                                                     Column(name='Domain Identifier', key='domain_identifier'),
                                                     Column(name='Identifier', key='identifier'),
                                                     Column(name='Version Identifier', key='version_identifier'),
                                                     Column(name='Usage', key='usage'),
                                                     Column(name='Scope', key='scope'),
                                                     Column(name='Importance', key='importance'),
                                                     Column(name='measurement', key='measurement'),
                                                     Column(name='target', key='target'),
                                                     Column(name='Implications', key='implications'),
                                                     Column(name='Outcomes', key='outcomes'),
                                                     Column(name='Results', key='results'),
                                                     Column(name='Status', key='element_status'),
                                                     Column(name='User Defined Status', key='user_defined_status'),
                                                     Column(name='Qualified Name', key='qualified_name'),
                                                     Column(name='GUID', key='guid')
                                                     ]),
                                  Format(types=['TABLE', 'LIST'],
                                         attributes=[Column(name='Display Name', key='display_name'),
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
                                  optional_params=OPTIONAL_SEARCH_PARAMS,
                                  spec_params={"metadata_element_subtypes": ["LicenseType"]},
                              )
                              ),

    "Governance Policies": FormatSet(
        target_type="GovernancePolicy",
        heading="Governance-Definitions Information",
        description="Attributes useful to Governance-Definitions.",
        aliases=["GovernanceDefinitions"],
        annotations={"wikilinks": ["[[Governance]]"]},
        family="Governance Officer",
        formats=[Format(types=["ALL"], attributes=GOVERNANCE_DEFINITIONS_COLUMNS)],
        action=ActionParameter(
            function="GovernanceOfficer.find_governance_definitions",
            required_params=["search_string"],
            optional_params=OPTIONAL_SEARCH_PARAMS,
            spec_params={"metadata_element_subtypes": ["GovernancePolicy"]},
        )
    )

}
)

# Build initial combined specs, then reorganize by family and slugged names
_initial_combined_specs = combine_format_set_dicts(base_report_specs, generated_format_sets)

# Utilities for reorganizing specs by family and normalizing labels
import re as _re


def _slugify_label(label: str) -> str:
    """Turn a display label into a key by collapsing whitespace to '-'.
    Keeps existing hyphens, trims outer whitespace, and collapses multiple dashes.
    """
    if not isinstance(label, str):
        return str(label)
    s = label.strip()
    s = _re.sub(r"\s+", "-", s)
    s = _re.sub(r"-+", "-", s)
    return s


def _add_alias(fs: FormatSet, alias: str) -> None:
    try:
        if alias and alias not in fs.aliases:
            fs.aliases.append(alias)
    except Exception:
        # Ensure aliases exists even if not initialized
        try:
            fs.aliases = list(set((getattr(fs, 'aliases', []) or []) + [alias]))
        except Exception:
            pass


def _build_family_registries(specs: FormatSetDict) -> dict[str, FormatSetDict]:
    """Group specs by family and return mapping family -> FormatSetDict with slugified keys.
    - Missing/blank family -> "General"
    - Keys are slugified (spaces -> '-')
    - If slug differs from original, add original as an alias for backward compatibility
    - Within each family, entries are alphabetized by slugified name (case-insensitive)
    - Disambiguate collisions by appending numeric suffixes
    """
    families: dict[str, FormatSetDict] = {}
    for orig_name, fs in specs.items():
        fam_raw = getattr(fs, 'family', None)
        family = (fam_raw or '').strip() or 'General'
        fam_dict = families.setdefault(family, FormatSetDict())

        base_slug = _slugify_label(orig_name)
        slug = base_slug
        suffix = 2
        while slug in fam_dict:
            slug = f"{base_slug}-{suffix}"
            suffix += 1
        # Add alias if the key is changing
        if slug != orig_name:
            _add_alias(fs, orig_name)
        # Also add a space-restored alias if someone passes slug with spaces (reverse unlikely but cheap)
        maybe_space = orig_name.replace('-', ' ')
        if maybe_space != orig_name:
            _add_alias(fs, maybe_space)
        fam_dict[slug] = fs

    # Sort each family by key and rebuild as FormatSetDict in that order (preserves insertion order)
    for fam, fdict in list(families.items()):
        ordered = FormatSetDict()
        for key in sorted(list(fdict.keys()), key=lambda s: s.lower()):
            ordered[key] = fdict[key]
        families[fam] = ordered
    return families


# Build family registries and a merged overall report_specs ordered by family then name
family_report_specs = _build_family_registries(_initial_combined_specs)

_report_specs_merged = FormatSetDict()
for fam_name in sorted(family_report_specs.keys(), key=lambda s: s.lower()):
    fam_dict = family_report_specs[fam_name]
    for key, fs in fam_dict.items():
        _report_specs_merged[key] = fs

report_specs = _report_specs_merged


def select_report_spec(kind: str, output_type: str) -> dict | None:
    """
    Retrieve the appropriate output set configuration dictionary based on `kind` and `output_type`.

    Intent of special output_type values:
    - "ANY": Discovery-only. Resolve the FormatSet (including aliases), action, and metadata, but DO NOT
      resolve a concrete format. Callers typically use this to check existence or to later pick a specific type
      via get_report_spec_match(...).

    :param kind: The kind of output set (e.g., "Referenceable", "Collections"). Aliases are supported.
    :param output_type: The desired output format type (e.g., "DICT", "LIST", "REPORT"), or "ANY".
    :return: The matched output set dictionary or None if no match is found.
    """
    # Normalize the output type to uppercase for consistency
    output_type = output_type.upper()
    output_struct: dict = {}

    # Step 1: Check if `kind` exists in the `report_specs` dictionary
    element = report_specs.get(kind)

    # Step 2: If not found, attempt to match `kind` in aliases
    if element is None:
        for key, value in report_specs.items():
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
            output_struct["action"] = element.action.model_dump()
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


def report_spec_list(*, show_family: bool = False, sort_by_family: bool = False, return_kind: str = "strings") \
        -> list[str] | str | list[dict]:
    """
    Return the available report specs in one of three forms: strings (default), a Markdown table, or records.

    Parameters
    - show_family: when True and return_kind=="strings", include the family tag alongside each name (e.g., "Collections [Catalog]")
    - sort_by_family: when True, sort results by family (case-insensitive; empty/no-family first),
      then alphabetize by name within each family (case-insensitive). When False, preserve insertion order.
    - return_kind: one of {"strings", "markdown_table", "markdown", "records", "dicts"}
      - "strings" (default): returns list[str] (optionally decorated with family when show_family=True)
      - "markdown_table"/"markdown": returns a Markdown table string with columns: Family | Report Name | Description
      - "records"/"dicts": returns a list of dicts: {"family": str|None, "name": str, "description": str}

    Returns
    - list[str] when return_kind=="strings"
    - str when return_kind in {"markdown_table", "markdown"}
    - list[dict] when return_kind in {"records", "dicts"}

    Notes
    - Default behavior remains backward-compatible with previous implementation: calling with no
      arguments returns only names in insertion order.
    """
    # Build list of (name, FormatSet)
    items = list(report_specs.items())

    if sort_by_family:
        def _key(n_fs: tuple[str, FormatSet]):
            name, fs = n_fs
            fam = (getattr(fs, "family", None) or "").strip().lower()
            return (fam, name.lower())

        items.sort(key=_key)

    rk = (return_kind or "strings").strip().lower()

    if rk in ("markdown_table", "markdown",):
        # Build rows for the markdown table
        def _esc(text: str) -> str:
            # Replace pipes and newlines to keep table intact
            return str(text).replace("|", "\\|").replace("\n", " ")

        header = "| Family | Report Name | Description |\n|---|---|---|"
        lines: list[str] = [header]
        for name, fs in items:
            fam = (getattr(fs, "family", None) or "").strip()
            desc = getattr(fs, "description", "") or ""
            lines.append(f"| {_esc(fam)} | {_esc(name)} | {_esc(desc)} |")
        return "\n".join(lines)

    if rk in ("records", "dicts"):
        records: list[dict] = []
        for name, fs in items:
            records.append({
                "family": getattr(fs, "family", None),
                "name": name,
                "description": getattr(fs, "description", "") or "",
            })
        return records

    # Default: strings
    if show_family:
        out: list[str] = []
        for name, fs in items:
            fam = getattr(fs, "family", None)
            if fam and str(fam).strip():
                out.append(f"{name} [{fam}]")
            else:
                out.append(name)
        return out
    else:
        # Names only
        return [name for name, _ in items]


def list_mcp_format_sets() -> dict:
    """
    Returns only those format set names that can be safely exposed as MCP tools.
    A format set is eligible if it has a DICT format or an ALL catch-all format.

    This allows MCP to prefer machine-consumable outputs and avoid side effects.
    """

    return {
        name: {
            "description": fs.description,
            "target_type": fs.target_type,
            "required_params": ", ".join(fs.action.required_params) or "",
            "optional_params": ", ".join(fs.action.optional_params) or "",
        }
        for name, fs in sorted(report_specs.items())
        if fs and fs.action and any(
            format_type in ["DICT", "ALL"]
            for format_obj in fs.formats
            for format_type in format_obj.types
        )
    }


def get_report_spec_heading(format_set: str) -> str:
    """
    Gets the heading of a format set.

    Args:
        format_set: The name of the format set

    Returns:
        str: The heading of the format set
    """
    return report_specs[format_set].heading


def get_report_spec_description(format_set: str) -> str:
    """
    Gets the description of a format set.

    Args:
        format_set: The name of the format set

    Returns:
        str: The description of the format set
    """
    return report_specs[format_set].description


def get_report_spec_match(format_set: Union[dict, FormatSet], output_format: str) -> dict:
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
            # Handle the case where format_set is a dictionary from select_report_spec with the "ANY" output type
            # In this case, we need to look up the format set by name and get the formats
            if "heading" in format_set_dict and "description" in format_set_dict:
                # Try to find the format set by heading
                for key, value in report_specs.items():
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


def save_report_specs(file_path: str, format_set_names: List[str] = None) -> None:
    """
    Save output format sets to a JSON file.

    This function allows saving all format sets or a subset of format sets to a JSON file.
    The saved format sets can later be loaded using the `load_report_specs` function.

    Args:
        file_path: The path to save the file to
        format_set_names: Optional list of format set names to save. If None, all format sets are saved.
    """
    if format_set_names is None:
        # Save all format sets
        report_specs.save_to_json(file_path)
        logger.info(f"All format sets saved to {file_path}")
    else:
        # Save only specified format sets
        subset = FormatSetDict()
        for name in format_set_names:
            format_set = report_specs.get(name)
            if format_set:
                subset[name] = format_set
            else:
                logger.warning(f"Format set '{name}' not found, skipping")

        if subset:
            subset.save_to_json(file_path)
            logger.info(f"Selected format sets saved to {file_path}")
        else:
            logger.warning(f"No valid format sets to save, file not created")


def load_report_specs(file_path: str, merge: bool = True) -> None:
    """
    Load output format sets from a JSON file.

    This function loads format sets from a JSON file and either merges them with the existing
    format sets or replaces the existing format sets.

    Args:
        file_path: The path to load the file from
        merge: If True, merge with existing format sets. If False, replace existing format sets.
    """
    global report_specs
    try:
        loaded_sets = FormatSetDict.load_from_json(file_path)

        if merge:
            # Merge with existing format sets
            for key, value in loaded_sets.items():
                report_specs[key] = value
            logger.info(f"Format sets from {file_path} merged with existing format sets")
        else:
            # Replace existing format sets
            report_specs = loaded_sets
            logger.info(f"Existing format sets replaced with format sets from {file_path}")
    except Exception as e:
        logger.error(f"Error loading format sets from {file_path}: {e}")
        raise


def load_user_report_specs() -> None:
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
            load_report_specs(str(file_path), merge=True)
        except Exception as e:
            logger.error(f"Error loading format sets from {file_path}: {e}")


def report_spec_markdown() -> str:
    """Return a markdown list of all output format sets with target type, aliases, and column names.

    This function is intended for external use to document available format sets.
    It generates a markdown string containing sections for each format set. For each
    set, it lists:
    - Target type
    - Aliases (if any)
    - Available formats (types) and their column display names with keys
    """
    lines: list[str] = ["# Available Output Format Sets", ""]
    for name in sorted(report_specs.keys()):
        fs = report_specs.get(name)
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
    load_user_report_specs()
except Exception as e:
    logger.error(f"Error loading user-defined format sets: {e}")
    for key, format_set in report_specs.items():
        if not format_set.formats:
            logger.warning(f"FormatSet {key} has no formats defined.")

# =============================
# Report format dynamic registry and new API (backward-compatible)
# =============================

from typing import Optional

# Runtime and config-loaded registries (do not mutate built-ins)
_RUNTIME_REPORT_FORMATS = FormatSetDict()
_CONFIG_REPORT_FORMATS = FormatSetDict()


class ReportFormatCollision(ValueError):
    pass


def _add_with_collision_check(target: FormatSetDict, new: FormatSetDict, source: str) -> None:
    for label in new.keys():
        if label in target.keys():
            raise ReportFormatCollision(
                f"Report format label '{label}' already defined; conflict from {source}")
    # Now safe to merge
    for k, v in new.items():
        target[k] = v


def _load_json_file(path: str) -> FormatSetDict:
    p = Path(os.path.expanduser(path)).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Report formats JSON not found: {p}")
    return FormatSetDict.load_from_json(str(p))


def refresh_report_specs() -> None:
    """Reload formats from configured JSON files and optional modules.
    Environment variables:
      - PYEGERIA_REPORT_FORMATS_JSON: comma-separated JSON file paths
      - PYEGERIA_REPORT_FORMATS_MODULES: optional comma-separated module callables (pkg.mod:func or pkg.mod.func)
    Collisions across sources will raise ReportFormatCollision.
    """
    global _CONFIG_REPORT_FORMATS
    _CONFIG_REPORT_FORMATS = FormatSetDict()

    json_paths = os.getenv("PYEGERIA_REPORT_FORMATS_JSON", "").strip()
    if json_paths:
        for raw in json_paths.split(","):
            raw = raw.strip()
            if not raw:
                continue
            loaded = _load_json_file(raw)
            _add_with_collision_check(_CONFIG_REPORT_FORMATS, loaded, source=f"JSON:{raw}")

    modules = os.getenv("PYEGERIA_REPORT_FORMATS_MODULES", "").strip()
    if modules:
        for m in modules.split(","):
            m = m.strip()
            if not m:
                continue
            # support both "pkg.mod.func" and "pkg.mod:func"
            if ":" in m:
                pkg, func = m.split(":", 1)
            else:
                pkg, func = m.rsplit(".", 1)
            mod = __import__(pkg, fromlist=[func])
            loader = getattr(mod, func)
            loaded = loader()
            if not isinstance(loaded, FormatSetDict):
                loaded = FormatSetDict(loaded)
            _add_with_collision_check(_CONFIG_REPORT_FORMATS, loaded, source=f"MODULE:{m}")


def get_report_registry() -> FormatSetDict:
    """Combine built-ins, generated, config-loaded, and runtime formats.
    Enforce no duplicate labels across all sources.
    """
    combined = FormatSetDict()
    _add_with_collision_check(combined, base_report_specs, source="BUILTINS")
    _add_with_collision_check(combined, generated_format_sets, source="GENERATED")
    _add_with_collision_check(combined, _CONFIG_REPORT_FORMATS, source="CONFIG")
    _add_with_collision_check(combined, _RUNTIME_REPORT_FORMATS, source="RUNTIME")
    return combined


def find_report_specs_by_perspective(perspective: str, *, case_insensitive: bool = True) -> list[dict]:
    """
    Return a list of dicts for report specs whose `question_spec` includes the given perspective.

    Each dict has the shape:
      { 'perspective': <perspective>, 'report_spec': <label>, 'questions': [..questions..] }

    Args:
        perspective: The perspective to search for (e.g., "Data Steward").
        case_insensitive: If True, compare perspectives case-insensitively.

    Returns:
        List of dictionaries, one per matching question_spec item, sorted by 'report_spec'.
    """
    if not perspective:
        return []
    needle = perspective.strip()
    norm = (lambda s: (s or "").strip().lower()) if case_insensitive else (lambda s: (s or "").strip())
    needle_cmp = norm(needle)

    results: list[dict] = []
    for label, fs in get_report_registry().items():
        qspec = getattr(fs, "question_spec", None)
        if not qspec:
            continue
        for item in qspec:
            perspectives = getattr(item, "perspectives", []) or []
            if any(norm(p) == needle_cmp for p in perspectives):
                questions = getattr(item, "questions", []) or []
                results.append({
                    "perspective": perspective,
                    "report_spec": label,
                    "questions": questions,
                })
    return sorted(results, key=lambda d: d.get("report_spec", ""))


def find_report_specs_by_question(
    question: str,
    *,
    case_insensitive: bool = True,
    substring: bool = True,
) -> list[dict]:
    """
    Return a list of dicts for report specs whose `question_spec` includes a matching example question.

    Each dict has the shape:
      { 'question': <input question>, 'report_spec': <label>, 'perspectives': [..perspectives..] }

    Args:
        question: The question to search for.
        case_insensitive: If True, compare questions case-insensitively.
        substring: If True, treat `question` as a substring to match within example questions;
                   otherwise require exact match.

    Returns:
        List of dictionaries, one per matching question_spec item, sorted by 'report_spec'.
    """
    if not question:
        return []
    needle = question.strip()
    norm = (lambda s: (s or "").strip().lower()) if case_insensitive else (lambda s: (s or "").strip())
    needle_cmp = norm(needle)

    results: list[dict] = []
    for label, fs in get_report_registry().items():
        qspec = getattr(fs, "question_spec", None)
        if not qspec:
            continue
        for item in qspec:
            questions = getattr(item, "questions", []) or []
            hit = False
            for q in questions:
                qn = norm(q)
                if substring:
                    if needle_cmp in qn:
                        hit = True
                        break
                else:
                    if needle_cmp == qn:
                        hit = True
                        break
            if hit:
                perspectives = getattr(item, "perspectives", []) or []
                results.append({
                    "question": question,
                    "report_spec": label,
                    "perspectives": perspectives,
                })
    return sorted(results, key=lambda d: d.get("report_spec", ""))


def find_report_specs(
    *,
    perspective: str | None = None,
    question: str | None = None,
    report_spec: str | None = None,
    case_insensitive: bool = True,
    substring: bool = True,
) -> list[dict]:
    """
    Flexible finder that accepts optional filters and returns matching report_spec dicts.

    Logical semantics: provided filters are ANDed; any filter not provided is treated as ANY.

    Returned dict shape (one per matching question_spec item):
      { 'report_spec': <label>, 'perspectives': [...], 'questions': [...] }

    The result list is sorted by 'report_spec'.
    """
    norm = (lambda s: (s or "").strip().lower()) if case_insensitive else (lambda s: (s or "").strip())
    persp_cmp = norm(perspective) if perspective else None
    quest_cmp = norm(question) if question else None
    rs_cmp = norm(report_spec) if report_spec else None

    results: list[dict] = []
    for label, fs in get_report_registry().items():
        # filter on report_spec by label or alias
        if rs_cmp is not None:
            label_match = norm(label) == rs_cmp
            alias_match = any(norm(a) == rs_cmp for a in getattr(fs, "aliases", []) or [])
            if not (label_match or alias_match):
                continue

        qspec = getattr(fs, "question_spec", None)
        if not qspec:
            # If there are no question specs, it cannot match perspective/question filters
            if persp_cmp is None and quest_cmp is None:
                # Only report_spec filter was provided and matched; emit a single entry with empty lists
                results.append({
                    "report_spec": label,
                    "perspectives": [],
                    "questions": [],
                })
            continue

        for item in qspec:
            perspectives = getattr(item, "perspectives", []) or []
            questions = getattr(item, "questions", []) or []

            if persp_cmp is not None:
                if not any(norm(p) == persp_cmp for p in perspectives):
                    continue

            if quest_cmp is not None:
                q_hit = False
                for q in questions:
                    qn = norm(q)
                    if substring:
                        if quest_cmp in qn:
                            q_hit = True
                            break
                    else:
                        if quest_cmp == qn:
                            q_hit = True
                            break
                if not q_hit:
                    continue

            results.append({
                "report_spec": label,
                "perspectives": perspectives,
                "questions": questions,
            })

    return sorted(results, key=lambda d: d.get("report_spec", ""))


def register_report_specs(new_formats: Union[FormatSetDict, dict], *, source: str = "runtime") -> None:
    """Dynamically add report formats at runtime. Raises on duplicate label."""
    global _RUNTIME_REPORT_FORMATS
    if not isinstance(new_formats, FormatSetDict):
        new_formats = FormatSetDict(new_formats)
    existing = get_report_registry()
    for label in new_formats.keys():
        if label in existing.keys():
            raise ReportFormatCollision(
                f"Report format label '{label}' already exists; cannot register from {source}")
    for k, v in new_formats.items():
        _RUNTIME_REPORT_FORMATS[k] = v


def unregister_report_spec(label: str) -> bool:
    return bool(_RUNTIME_REPORT_FORMATS.pop(label, None))


def clear_runtime_report_specs() -> None:
    _RUNTIME_REPORT_FORMATS.clear()


def list_report_specs() -> list[str]:
    return list(get_report_registry().keys())


def _select_from_registry(registry: FormatSetDict, kind: str, output_type: str) -> dict | None:
    # Normalize

    output_type = output_type.upper()
    element: Optional[FormatSet] = registry.get(kind)
    if element is None:
        # try aliases
        for value in registry.values():
            if kind in value.aliases:
                element = value
                break
    if element is None:
        logger.error(f"No matching report format found for kind='{kind}' and output type='{output_type}'.")
        return None

    output_struct: dict = {
        "aliases": element.aliases,
        "heading": element.heading,
        "description": element.description,
        "question_spec": element.question_spec,
        "annotations": element.annotations,
        "target_type": element.target_type,
    }
    if element.action:
        output_struct["action"] = element.action.dict()
    if element.get_additional_props:
        output_struct["get_additional_props"] = element.get_additional_props.dict()

    if output_type == "ANY":
        return output_struct

    for fmt in element.formats:
        if output_type in fmt.types:
            output_struct["formats"] = fmt.dict()
            return output_struct
    for fmt in element.formats:
        if "ALL" in fmt.types:
            output_struct["formats"] = fmt.dict()
            return output_struct
    logger.error(f"No matching format found for kind='{kind}' with output type='{output_type}'.")
    return None


# New public API (preferred)

def select_report_format(kind: str, output_type: str) -> dict | None:
    return _select_from_registry(get_report_registry(), kind, output_type)


def report_format_list() -> list[str]:
    return list_report_specs()


def get_report_format_heading(fmt_name: str) -> Optional[str]:
    reg = get_report_registry()
    fs = reg.get(fmt_name)
    if fs is None:
        for k, v in reg.items():
            if fmt_name in v.aliases:
                return v.heading
        return None
    return fs.heading


def get_report_format_description(fmt_name: str) -> Optional[str]:
    reg = get_report_registry()
    fs = reg.get(fmt_name)
    if fs is None:
        for k, v in reg.items():
            if fmt_name in v.aliases:
                return v.description
        return None
    return fs.description


# Legacy names remain available (no change to behavior) and can be deprecated later.
# Temporary aliases for backwards compatibility during migration
select_report_spec = select_report_format
