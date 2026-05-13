"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.
"""
from pyegeria.core._exceptions import PyegeriaInvalidParameterException

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

from pyegeria.view._output_format_models import (
    Attribute,
    Column,
    Format,
    ActionParameter,
    FormatSet,
    FormatSetDict
)

# --- GENERATED FORMAT SETS ---
# This section is updated by gen-report-specs.
generated_format_sets = FormatSetDict({
    'Agreement-DrE-Basic': FormatSet(target_type='Agreement', heading='Agreement-DrE-Basic Attributes', description='Auto-generated format for Agreement (Create, Basic).', family='Digital Product Manager', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Agreement Type', key='agreement_type'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose'), Column(name='Agreement Type', key='agreement_type')])], action=ActionParameter(function='CollectionManager.find_collections', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'Agreement'})),
    'Business-Imperative-DrE-Basic': FormatSet(target_type='Business Imperative', heading='Business-Imperative-DrE-Basic Attributes', description='Auto-generated format for Business Imperative (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'BusinessImperative'})),
    'Campaign-DrE-Basic': FormatSet(target_type='Campaign', heading='Campaign-DrE-Basic Attributes', description='Auto-generated format for Campaign (Create, Basic).', family='Projects', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Actual Completion Date', key='actual_completion_date'), Column(name='Actual Start Date', key='actual_start_date'), Column(name='Mission', key='mission'), Column(name='Planned Completion Date', key='planned_completion_date'), Column(name='Planned Start Date', key='planned_start_date'), Column(name='Priority', key='priority'), Column(name='Project Approach', key='approach'), Column(name='Project Health', key='project_health'), Column(name='Project Identifier', key='project_identifier'), Column(name='Project Management Style', key='management_style'), Column(name='Project Phase', key='project_phase'), Column(name='Project Results Usage', key='results_usage'), Column(name='Project Scope', key='project_scope'), Column(name='Project Type', key='project_type', valid_values=['Project', 'Campaign', 'Task', 'PersonalProject', 'StudyProject', 'Experiment']), Column(name='Purposes', key='purposes'), Column(name='Success Criteria', key='success_criteria'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Project Status', key='project_status'), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Actual Completion Date', key='actual_completion_date'), Column(name='Actual Start Date', key='actual_start_date'), Column(name='Mission', key='mission'), Column(name='Planned Completion Date', key='planned_completion_date'), Column(name='Planned Start Date', key='planned_start_date'), Column(name='Priority', key='priority'), Column(name='Project Approach', key='approach'), Column(name='Project Health', key='project_health'), Column(name='Project Identifier', key='project_identifier'), Column(name='Project Management Style', key='management_style'), Column(name='Project Phase', key='project_phase'), Column(name='Project Results Usage', key='results_usage'), Column(name='Project Scope', key='project_scope'), Column(name='Project Status', key='project_status'), Column(name='Project Type', key='project_type', valid_values=['Project', 'Campaign', 'Task', 'PersonalProject', 'StudyProject', 'Experiment']), Column(name='Purposes', key='purposes'), Column(name='Success Criteria', key='success_criteria')])], action=ActionParameter(function='ProjectManager.find_projects', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'include_only_classified_elements': ['Campaign']})),
    'Certification-Type-DrE-Basic': FormatSet(target_type='Certification Type', heading='Certification-Type-DrE-Basic Attributes', description='Auto-generated format for Certification Type (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Entitlements', key='entitlements'), Column(name='Obligations', key='obligations'), Column(name='Restrictions', key='restrictions'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Entitlements', key='entitlements'), Column(name='Obligations', key='obligations'), Column(name='Restrictions', key='restrictions')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'CertificationType'})),
    'Cited-Document-DrE-Basic': FormatSet(target_type='Cited Document', heading='Cited-Document-DrE-Basic Attributes', description='Auto-generated format for Cited Document (Create, Basic).', family='External Reference', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Attribution', key='attribution'), Column(name='Copyright', key='copyright'), Column(name='License', key='license'), Column(name='Organization', key='organization'), Column(name='Reference Abstract', key='reference_abstract'), Column(name='Reference Title', key='reference_title'), Column(name='Sources', key='reference_sources'), Column(name='Edition', key='edition'), Column(name='First Publication Date', key='first_pub_date'), Column(name='Number of Pages', key='number_of_pages'), Column(name='Page Range', key='page_range'), Column(name='Publication City', key='pub_city'), Column(name='Publication Date', key='pub_date'), Column(name='Publication Numbers', key='pub_numbers'), Column(name='Publication Series', key='publication_series'), Column(name='Publication Series Volume', key='pub_series_volume'), Column(name='Publication Year', key='pub_year'), Column(name='Publisher', key='publisher'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Attribution', key='attribution'), Column(name='Copyright', key='copyright'), Column(name='License', key='license'), Column(name='Organization', key='organization'), Column(name='Reference Abstract', key='reference_abstract'), Column(name='Reference Title', key='reference_title'), Column(name='Sources', key='reference_sources'), Column(name='Edition', key='edition'), Column(name='First Publication Date', key='first_pub_date'), Column(name='Number of Pages', key='number_of_pages'), Column(name='Page Range', key='page_range'), Column(name='Publication City', key='pub_city'), Column(name='Publication Date', key='pub_date'), Column(name='Publication Numbers', key='pub_numbers'), Column(name='Publication Series', key='publication_series'), Column(name='Publication Series Volume', key='pub_series_volume'), Column(name='Publication Year', key='pub_year'), Column(name='Publisher', key='publisher')])], action=ActionParameter(function='ExternalReferences.find_external_references', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_types': ['CitedDocument']})),
    'Collection-DrE-Basic': FormatSet(target_type='Collection', heading='Collection-DrE-Basic Attributes', description='Auto-generated format for Collection (Create, Basic).', family='Collections', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose')])], action=ActionParameter(function='CollectionManager.find_collections', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'])),
    'Collection-Folder-DrE-Basic': FormatSet(target_type='Collection Folder', heading='Collection-Folder-DrE-Basic Attributes', description='Auto-generated format for Collection Folder (Create, Basic).', family='Collections', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose')])], action=ActionParameter(function='CollectionManager.find_collections', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'CollectionFolder'})),
    'Comment-DrE-Basic': FormatSet(target_type='Comment', heading='Comment-DrE-Basic Attributes', description='Auto-generated format for Comment (Create, Basic).', family='Feedback', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Commented On Element', key='commented_on_element'), Column(name='Comment Type', key='comment_type', valid_values=['STANDARD_COMMENT', 'QUESTION', 'ANSWER', 'SUGGESTION', 'USAGE_EXPERIENCE', 'REQUIREMENT', 'OTHER']), Column(name='Version Identifier', key='version_identifier'), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Commented On Element', key='commented_on_element'), Column(name='Comment Type', key='comment_type', valid_values=['STANDARD_COMMENT', 'QUESTION', 'ANSWER', 'SUGGESTION', 'USAGE_EXPERIENCE', 'REQUIREMENT', 'OTHER'])])], action=ActionParameter(function='ServerClient.find_comments', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'])),
    'CSV-File-DrE-Basic': FormatSet(target_type='CSV File', heading='CSV-File-DrE-Basic Attributes', description='Auto-generated format for CSV File (Create, Basic).', family='Digital Product Manager', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='File Encoding', key='file_encoding'), Column(name='File Extension', key='file_extension'), Column(name='File Path', key='file_path'), Column(name='File System Name', key='file_system_name'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='File Encoding', key='file_encoding'), Column(name='File Extension', key='file_extension'), Column(name='File Path', key='file_path'), Column(name='File System Name', key='file_system_name')])], action=ActionParameter(function='AssetMaker.find_assets', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'CSVFile'})),
    'Data-Class-DrE-Basic': FormatSet(target_type='Data Class', heading='Data-Class-DrE-Basic Attributes', description='Auto-generated format for Data Class (Create, Basic).', family='Data Designer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Absolute Uncertainty', key='absolute_uncertainty'), Column(name='Data Type', key='data_type', valid_values=['string', 'int', 'long', 'date', 'boolean', 'char', 'byte', 'float', 'double', 'biginteger', 'bigdecimal', 'array<string>', 'array<int>', 'map<string,string>', 'map<string,boolean>', 'map<string,int>', 'map<string,long>', 'map<string,double>', 'map<string,date>', 'map<string,object>', 'short', 'map<string,array<string>>', 'other']), Column(name='In Data Value Specification', key='in_data_value_specification'), Column(name='Match Property Names', key='match_property_names'), Column(name='Match Threshold', key='match_threshold'), Column(name='Name Patterns', key='name_patterns'), Column(name='Namespace Path', key='namespace_path'), Column(name='Relative Uncertainty', key='relative_uncertainty'), Column(name='Specializes Data Value Specification', key='specializes_data_value_specification'), Column(name='Specification', key='specification'), Column(name='Specification Details', key='specification_details'), Column(name='Units', key='units'), Column(name='Allow Duplicate Values', key='allows_duplicate_values'), Column(name='Average Value', key='average_value'), Column(name='Containing Data Class', key='containing_data_class'), Column(name='Data Patterns', key='data_patterns'), Column(name='Default Value', key='default_value'), Column(name='Is Case Sensitive', key='is_case_sensitive'), Column(name='Is Nullable', key='is_nullable'), Column(name='Sample Values', key='sample_values'), Column(name='Value List', key='value_list'), Column(name='Value Range From', key='value_range_from'), Column(name='Value Range To', key='value_range_to'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Absolute Uncertainty', key='absolute_uncertainty'), Column(name='Data Type', key='data_type', valid_values=['string', 'int', 'long', 'date', 'boolean', 'char', 'byte', 'float', 'double', 'biginteger', 'bigdecimal', 'array<string>', 'array<int>', 'map<string,string>', 'map<string,boolean>', 'map<string,int>', 'map<string,long>', 'map<string,double>', 'map<string,date>', 'map<string,object>', 'short', 'map<string,array<string>>', 'other']), Column(name='In Data Value Specification', key='in_data_value_specification'), Column(name='Match Property Names', key='match_property_names'), Column(name='Match Threshold', key='match_threshold'), Column(name='Name Patterns', key='name_patterns'), Column(name='Namespace Path', key='namespace_path'), Column(name='Relative Uncertainty', key='relative_uncertainty'), Column(name='Specializes Data Value Specification', key='specializes_data_value_specification'), Column(name='Specification', key='specification'), Column(name='Specification Details', key='specification_details'), Column(name='Units', key='units'), Column(name='Allow Duplicate Values', key='allows_duplicate_values'), Column(name='Average Value', key='average_value'), Column(name='Containing Data Class', key='containing_data_class'), Column(name='Data Patterns', key='data_patterns'), Column(name='Default Value', key='default_value'), Column(name='Is Case Sensitive', key='is_case_sensitive'), Column(name='Is Nullable', key='is_nullable'), Column(name='Sample Values', key='sample_values'), Column(name='Value List', key='value_list'), Column(name='Value Range From', key='value_range_from'), Column(name='Value Range To', key='value_range_to')])], action=ActionParameter(function='DataDesigner.find_data_classes', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'DataClass'})),
    'Data-Dictionary-DrE-Basic': FormatSet(target_type='Data Dictionary', heading='Data-Dictionary-DrE-Basic Attributes', description='Auto-generated format for Data Dictionary (Create, Basic).', family='Data Designer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose')])], action=ActionParameter(function='CollectionManager.find_collections', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'DataDictionary'})),
    'Data-Field-DrE-Basic': FormatSet(target_type='Data Field', heading='Data-Field-DrE-Basic Attributes', description='Auto-generated format for Data Field (Create, Basic).', family='Data Designer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Aliases', key='aliases'), Column(name='Data Class', key='data_class'), Column(name='Data Type', key='data_type', valid_values=['string', 'int', 'long', 'date', 'boolean', 'char', 'byte', 'float', 'double', 'biginteger', 'bigdecimal', 'array<string>', 'array<int>', 'map<string,string>', 'map<string,boolean>', 'map<string,int>', 'map<string,long>', 'map<string,double>', 'map<string,date>', 'map<string,object>', 'short', 'map<string,array<string>>', 'other']), Column(name='Default Value', key='default_value'), Column(name='In Data Field', key='in_data_field'), Column(name='In Data Structure', key='in_data_structure'), Column(name='Is Nullable', key='is_nullable'), Column(name='Length', key='length'), Column(name='Maximum Cardinality', key='maximum_cardinality'), Column(name='Minimum Cardinality', key='minimum_cardinality'), Column(name='Minimum Length', key='minimum_length'), Column(name='Name Patterns', key='name_patterns'), Column(name='Namespace Path', key='namespace_path'), Column(name='Ordered Values', key='ordered_values'), Column(name='Position', key='position'), Column(name='Precision', key='precision'), Column(name='Sort Order', key='sort_order'), Column(name='Units', key='units'), Column(name='Allow Duplicate Values', key='allows_duplicate_values'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Aliases', key='aliases'), Column(name='Data Class', key='data_class'), Column(name='Data Type', key='data_type', valid_values=['string', 'int', 'long', 'date', 'boolean', 'char', 'byte', 'float', 'double', 'biginteger', 'bigdecimal', 'array<string>', 'array<int>', 'map<string,string>', 'map<string,boolean>', 'map<string,int>', 'map<string,long>', 'map<string,double>', 'map<string,date>', 'map<string,object>', 'short', 'map<string,array<string>>', 'other']), Column(name='Default Value', key='default_value'), Column(name='In Data Field', key='in_data_field'), Column(name='In Data Structure', key='in_data_structure'), Column(name='Is Nullable', key='is_nullable'), Column(name='Length', key='length'), Column(name='Maximum Cardinality', key='maximum_cardinality'), Column(name='Minimum Cardinality', key='minimum_cardinality'), Column(name='Minimum Length', key='minimum_length'), Column(name='Name Patterns', key='name_patterns'), Column(name='Namespace Path', key='namespace_path'), Column(name='Ordered Values', key='ordered_values'), Column(name='Position', key='position'), Column(name='Precision', key='precision'), Column(name='Sort Order', key='sort_order'), Column(name='Units', key='units'), Column(name='Allow Duplicate Values', key='allows_duplicate_values')])], action=ActionParameter(function='DataDesigner.find_data_fields', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'DataField'})),
    'Data-Grain-DrE-Basic': FormatSet(target_type='Data Grain', heading='Data-Grain-DrE-Basic Attributes', description='Auto-generated format for Data Grain (Create, Basic).', family='Data Designer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Absolute Uncertainty', key='absolute_uncertainty'), Column(name='Data Type', key='data_type', valid_values=['string', 'int', 'long', 'date', 'boolean', 'char', 'byte', 'float', 'double', 'biginteger', 'bigdecimal', 'array<string>', 'array<int>', 'map<string,string>', 'map<string,boolean>', 'map<string,int>', 'map<string,long>', 'map<string,double>', 'map<string,date>', 'map<string,object>', 'short', 'map<string,array<string>>', 'other']), Column(name='In Data Value Specification', key='in_data_value_specification'), Column(name='Match Property Names', key='match_property_names'), Column(name='Match Threshold', key='match_threshold'), Column(name='Name Patterns', key='name_patterns'), Column(name='Namespace Path', key='namespace_path'), Column(name='Relative Uncertainty', key='relative_uncertainty'), Column(name='Specializes Data Value Specification', key='specializes_data_value_specification'), Column(name='Specification', key='specification'), Column(name='Specification Details', key='specification_details'), Column(name='Units', key='units'), Column(name='Granularity Basis', key='granularity_basis'), Column(name='Grain Statement', key='grain_statement'), Column(name='Interval', key='interval'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Absolute Uncertainty', key='absolute_uncertainty'), Column(name='Data Type', key='data_type', valid_values=['string', 'int', 'long', 'date', 'boolean', 'char', 'byte', 'float', 'double', 'biginteger', 'bigdecimal', 'array<string>', 'array<int>', 'map<string,string>', 'map<string,boolean>', 'map<string,int>', 'map<string,long>', 'map<string,double>', 'map<string,date>', 'map<string,object>', 'short', 'map<string,array<string>>', 'other']), Column(name='In Data Value Specification', key='in_data_value_specification'), Column(name='Match Property Names', key='match_property_names'), Column(name='Match Threshold', key='match_threshold'), Column(name='Name Patterns', key='name_patterns'), Column(name='Namespace Path', key='namespace_path'), Column(name='Relative Uncertainty', key='relative_uncertainty'), Column(name='Specializes Data Value Specification', key='specializes_data_value_specification'), Column(name='Specification', key='specification'), Column(name='Specification Details', key='specification_details'), Column(name='Units', key='units'), Column(name='Granularity Basis', key='granularity_basis'), Column(name='Grain Statement', key='grain_statement'), Column(name='Interval', key='interval')])], action=ActionParameter(function='DataDesigner.find_data_value_specifications', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'DataGrain'})),
    'Data-Lens-DrE-Basic': FormatSet(target_type='Data Lens', heading='Data-Lens-DrE-Basic Attributes', description='Auto-generated format for Data Lens (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Max Height', key='max_height'), Column(name='Data Collection End Time', key='data_collection_end_time'), Column(name='Data Collection Start Time', key='data_collection_start_time'), Column(name='Max Latitude', key='max_latitude'), Column(name='Max Longitude', key='max_longitude'), Column(name='Min Height', key='min_height'), Column(name='Min Latitude', key='min_latitude'), Column(name='Min Longitude', key='min_longitude'), Column(name='Scope Elements', key='scope_elements'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Max Height', key='max_height'), Column(name='Data Collection End Time', key='data_collection_end_time'), Column(name='Data Collection Start Time', key='data_collection_start_time'), Column(name='Max Latitude', key='max_latitude'), Column(name='Max Longitude', key='max_longitude'), Column(name='Min Height', key='min_height'), Column(name='Min Latitude', key='min_latitude'), Column(name='Min Longitude', key='min_longitude'), Column(name='Scope Elements', key='scope_elements')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'DataLens'})),
    'Data-Processing-Purpose-DrE-Basic': FormatSet(target_type='Data Processing Purpose', heading='Data-Processing-Purpose-DrE-Basic Attributes', description='Auto-generated format for Data Processing Purpose (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'DataProcessingPurpose'})),
    'Data-Sharing-Agreement-DrE-Basic': FormatSet(target_type='Data Sharing Agreement', heading='Data-Sharing-Agreement-DrE-Basic Attributes', description='Auto-generated format for Data Sharing Agreement (Create, Basic).', family='Digital Product Manager', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Agreement Type', key='agreement_type'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose'), Column(name='Agreement Type', key='agreement_type')])], action=ActionParameter(function='CollectionManager.find_collections', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'classification_names': ['DataSharingAgreement']})),
    'Data-Spec-DrE-Basic': FormatSet(target_type='Data Spec', heading='Data-Spec-DrE-Basic Attributes', description='Auto-generated format for Data Spec (Create, Basic).', family='Data Designer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose')])], action=ActionParameter(function='CollectionManager.find_collections', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'DataSpec'})),
    'Data-Structure-DrE-Basic': FormatSet(target_type='Data Structure', heading='Data-Structure-DrE-Basic Attributes', description='Auto-generated format for Data Structure (Create, Basic).', family='Data Designer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='In Data Dictionary', key='in_data_dictionary'), Column(name='In Data Specification', key='in_data_specification'), Column(name='In Data Structure', key='in_data_structure'), Column(name='Name Patterns', key='name_patterns'), Column(name='Namespace Path', key='namespace_path'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='In Data Dictionary', key='in_data_dictionary'), Column(name='In Data Specification', key='in_data_specification'), Column(name='In Data Structure', key='in_data_structure'), Column(name='Name Patterns', key='name_patterns'), Column(name='Namespace Path', key='namespace_path')])], action=ActionParameter(function='DataDesigner.find_data_structures', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'DataStructure'})),
    'Data-Value-Specification-DrE-Basic': FormatSet(target_type='Data Value Specification', heading='Data-Value-Specification-DrE-Basic Attributes', description='Auto-generated format for Data Value Specification (Create, Basic).', family='Data Designer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Absolute Uncertainty', key='absolute_uncertainty'), Column(name='Data Type', key='data_type', valid_values=['string', 'int', 'long', 'date', 'boolean', 'char', 'byte', 'float', 'double', 'biginteger', 'bigdecimal', 'array<string>', 'array<int>', 'map<string,string>', 'map<string,boolean>', 'map<string,int>', 'map<string,long>', 'map<string,double>', 'map<string,date>', 'map<string,object>', 'short', 'map<string,array<string>>', 'other']), Column(name='In Data Value Specification', key='in_data_value_specification'), Column(name='Match Property Names', key='match_property_names'), Column(name='Match Threshold', key='match_threshold'), Column(name='Name Patterns', key='name_patterns'), Column(name='Namespace Path', key='namespace_path'), Column(name='Relative Uncertainty', key='relative_uncertainty'), Column(name='Specializes Data Value Specification', key='specializes_data_value_specification'), Column(name='Specification', key='specification'), Column(name='Specification Details', key='specification_details'), Column(name='Units', key='units'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Absolute Uncertainty', key='absolute_uncertainty'), Column(name='Data Type', key='data_type', valid_values=['string', 'int', 'long', 'date', 'boolean', 'char', 'byte', 'float', 'double', 'biginteger', 'bigdecimal', 'array<string>', 'array<int>', 'map<string,string>', 'map<string,boolean>', 'map<string,int>', 'map<string,long>', 'map<string,double>', 'map<string,date>', 'map<string,object>', 'short', 'map<string,array<string>>', 'other']), Column(name='In Data Value Specification', key='in_data_value_specification'), Column(name='Match Property Names', key='match_property_names'), Column(name='Match Threshold', key='match_threshold'), Column(name='Name Patterns', key='name_patterns'), Column(name='Namespace Path', key='namespace_path'), Column(name='Relative Uncertainty', key='relative_uncertainty'), Column(name='Specializes Data Value Specification', key='specializes_data_value_specification'), Column(name='Specification', key='specification'), Column(name='Specification Details', key='specification_details'), Column(name='Units', key='units')])], action=ActionParameter(function='DataDesigner.find_data_value_specifications', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'DataValueSpecification'})),
    'Digital-Product-Catalog-DrE-Basic': FormatSet(target_type='Digital Product Catalog', heading='Digital-Product-Catalog-DrE-Basic Attributes', description='Auto-generated format for Digital Product Catalog (Create, Basic).', family='Digital Product Manager', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose')])], action=ActionParameter(function='CollectionManager.find_collections', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'classification_names': ['DigitalProductCatalog']})),
    'Digital-Product-DrE-Basic': FormatSet(target_type='Digital Product', heading='Digital-Product-DrE-Basic Attributes', description='Auto-generated format for Digital Product (Create, Basic).', family='Digital Product Manager', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Current Version', key='current_version'), Column(name='Introduction Date', key='introduction_date'), Column(name='Maturity', key='maturity'), Column(name='Next Version Date', key='next_version_date'), Column(name='Product Name', key='product_name'), Column(name='Product Type', key='product_type'), Column(name='Service Life', key='service_life'), Column(name='Withdrawal Date', key='withdrawal_date'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Product Status', key='product_status'), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose'), Column(name='Current Version', key='current_version'), Column(name='Introduction Date', key='introduction_date'), Column(name='Maturity', key='maturity'), Column(name='Next Version Date', key='next_version_date'), Column(name='Product Name', key='product_name'), Column(name='Product Status', key='product_status'), Column(name='Product Type', key='product_type'), Column(name='Service Life', key='service_life'), Column(name='Withdrawal Date', key='withdrawal_date')])], action=ActionParameter(function='CollectionManager.find_collections', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'DigitalProduct'})),
    'Digital-Subscription-DrE-Basic': FormatSet(target_type='Digital Subscription', heading='Digital-Subscription-DrE-Basic Attributes', description='Auto-generated format for Digital Subscription (Create, Basic).', family='Digital Product Manager', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Agreement Type', key='agreement_type'), Column(name='Subscription Level', key='subscription_level'), Column(name='Support Level', key='support_level'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose'), Column(name='Agreement Type', key='agreement_type'), Column(name='Subscription Level', key='subscription_level'), Column(name='Support Level', key='support_level')])], action=ActionParameter(function='CollectionManager.find_collections', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'DigitalSubscription'})),
    'External-Data-Source-DrE-Basic': FormatSet(target_type='External Data Source', heading='External-Data-Source-DrE-Basic Attributes', description='Auto-generated format for External Data Source (Create, Basic).', family='External Reference', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Attribution', key='attribution'), Column(name='Copyright', key='copyright'), Column(name='License', key='license'), Column(name='Organization', key='organization'), Column(name='Reference Abstract', key='reference_abstract'), Column(name='Reference Title', key='reference_title'), Column(name='Sources', key='reference_sources'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Attribution', key='attribution'), Column(name='Copyright', key='copyright'), Column(name='License', key='license'), Column(name='Organization', key='organization'), Column(name='Reference Abstract', key='reference_abstract'), Column(name='Reference Title', key='reference_title'), Column(name='Sources', key='reference_sources')])], action=ActionParameter(function='ExternalReferences.find_external_references', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_types': ['ExternalDataSource']})),
    'External-Model-Source-DrE-Basic': FormatSet(target_type='External Model Source', heading='External-Model-Source-DrE-Basic Attributes', description='Auto-generated format for External Model Source (Create, Basic).', family='External Reference', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Attribution', key='attribution'), Column(name='Copyright', key='copyright'), Column(name='License', key='license'), Column(name='Organization', key='organization'), Column(name='Reference Abstract', key='reference_abstract'), Column(name='Reference Title', key='reference_title'), Column(name='Sources', key='reference_sources'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Attribution', key='attribution'), Column(name='Copyright', key='copyright'), Column(name='License', key='license'), Column(name='Organization', key='organization'), Column(name='Reference Abstract', key='reference_abstract'), Column(name='Reference Title', key='reference_title'), Column(name='Sources', key='reference_sources')])], action=ActionParameter(function='ExternalReferences.find_external_references', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_types': ['ExternalModelSource']})),
    'External-Reference-DrE-Basic': FormatSet(target_type='External Reference', heading='External-Reference-DrE-Basic Attributes', description='Auto-generated format for External Reference (Create, Basic).', family='External Reference', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Attribution', key='attribution'), Column(name='Copyright', key='copyright'), Column(name='License', key='license'), Column(name='Organization', key='organization'), Column(name='Reference Abstract', key='reference_abstract'), Column(name='Reference Title', key='reference_title'), Column(name='Sources', key='reference_sources'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Attribution', key='attribution'), Column(name='Copyright', key='copyright'), Column(name='License', key='license'), Column(name='Organization', key='organization'), Column(name='Reference Abstract', key='reference_abstract'), Column(name='Reference Title', key='reference_title'), Column(name='Sources', key='reference_sources')])], action=ActionParameter(function='ExternalReferences.find_external_references', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'])),
    'External-Source-Code-DrE-Basic': FormatSet(target_type='External Source Code', heading='External-Source-Code-DrE-Basic Attributes', description='Auto-generated format for External Source Code (Create, Basic).', family='External Reference', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Attribution', key='attribution'), Column(name='Copyright', key='copyright'), Column(name='License', key='license'), Column(name='Organization', key='organization'), Column(name='Reference Abstract', key='reference_abstract'), Column(name='Reference Title', key='reference_title'), Column(name='Sources', key='reference_sources'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Attribution', key='attribution'), Column(name='Copyright', key='copyright'), Column(name='License', key='license'), Column(name='Organization', key='organization'), Column(name='Reference Abstract', key='reference_abstract'), Column(name='Reference Title', key='reference_title'), Column(name='Sources', key='reference_sources')])], action=ActionParameter(function='ExternalReferences.find_external_references', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_types': ['ExternalSourceCode']})),
    'Folio-DrE-Basic': FormatSet(target_type='Folio', heading='Folio-DrE-Basic Attributes', description='Auto-generated format for Folio (Create, Basic).', family='Collections', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose')])], action=ActionParameter(function='CollectionManager.find_collections', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'Folio'})),
    'Glossary-as-Taxonomy-DrE-Basic': FormatSet(target_type='Glossary as Taxonomy', heading='Glossary-as-Taxonomy-DrE-Basic Attributes', description='Auto-generated format for Glossary as Taxonomy (Create, Basic).', family='Glossary', formats=[Format(types=['LIST'], attributes=[Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Glossary Name', key='glossary_names'), Column(name='Version Identifier', key='current_version'), Column(name='Identifier', key='identifier'), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Glossary Name', key='glossary_names'), Column(name='Category', key='category'), Column(name='Version Identifier', key='current_version'), Column(name='Identifier', key='identifier'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='URL', key='url')])], action=ActionParameter(function='GlossaryManager.find_glossaries', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'])),
    'Glossary-DrE-Basic': FormatSet(target_type='Glossary', heading='Glossary-DrE-Basic Attributes', description='Auto-generated format for Glossary (Create, Basic).', family='Glossary', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Language', key='language'), Column(name='Usage', key='usage'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose'), Column(name='Language', key='language'), Column(name='Usage', key='usage')])], action=ActionParameter(function='GlossaryManager.find_glossaries', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'])),
    'Glossary-Term-DrE-Basic': FormatSet(target_type='Glossary Term', heading='Glossary-Term-DrE-Basic Attributes', description='Auto-generated format for Glossary Term (Create, Basic).', family='Glossary', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Abbreviation', key='abbreviation'), Column(name='Aliases', key='aliases'), Column(name='Example', key='example'), Column(name='Folders', key='folders'), Column(name='Glossary Name', key='glossary_names'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Abbreviation', key='abbreviation'), Column(name='Aliases', key='aliases'), Column(name='Example', key='example'), Column(name='Folders', key='folders'), Column(name='Glossary Name', key='glossary_names'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage')])], action=ActionParameter(function='GlossaryManager.find_glossary_terms', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'])),
    'Governance-Action-DrE-Basic': FormatSet(target_type='Governance Action', heading='Governance-Action-DrE-Basic Attributes', description='Auto-generated format for Governance Action (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'GovernanceAction'})),
    'Governance-Approach-DrE-Basic': FormatSet(target_type='Governance Approach', heading='Governance-Approach-DrE-Basic Attributes', description='Auto-generated format for Governance Approach (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'GovernanceApproach'})),
    'Governance-Control-DrE-Basic': FormatSet(target_type='Governance Control', heading='Governance-Control-DrE-Basic Attributes', description='Auto-generated format for Governance Control (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'GovernanceControl'})),
    'Governance-Definition-DrE-Basic': FormatSet(target_type='Governance Definition', heading='Governance-Definition-DrE-Basic Attributes', description='Auto-generated format for Governance Definition (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'GovernanceDefinition'})),
    'Governance-Driver-DrE-Basic': FormatSet(target_type='Governance Driver', heading='Governance-Driver-DrE-Basic Attributes', description='Auto-generated format for Governance Driver (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'GovernanceDriver'})),
    'Governance-Metric-DrE-Basic': FormatSet(target_type='Governance Metric', heading='Governance-Metric-DrE-Basic Attributes', description='Auto-generated format for Governance Metric (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Measurement', key='measurement'), Column(name='Target', key='target'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Measurement', key='measurement'), Column(name='Target', key='target')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'GovernanceMetric'})),
    'Governance-Obligation-DrE-Basic': FormatSet(target_type='Governance Obligation', heading='Governance-Obligation-DrE-Basic Attributes', description='Auto-generated format for Governance Obligation (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'GovernanceObligation'})),
    'Governance-Policy-DrE-Basic': FormatSet(target_type='Governance Policy', heading='Governance-Policy-DrE-Basic Attributes', description='Auto-generated format for Governance Policy (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'GovernancePolicy'})),
    'Governance-Principle-DrE-Basic': FormatSet(target_type='Governance Principle', heading='Governance-Principle-DrE-Basic Attributes', description='Auto-generated format for Governance Principle (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'GovernancePrinciple'})),
    'Governance-Procedure-DrE-Basic': FormatSet(target_type='Governance Procedure', heading='Governance-Procedure-DrE-Basic Attributes', description='Auto-generated format for Governance Procedure (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'GovernanceProcedure'})),
    'Governance-Responsibility-DrE-Basic': FormatSet(target_type='Governance Responsibility', heading='Governance-Responsibility-DrE-Basic Attributes', description='Auto-generated format for Governance Responsibility (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'GovernanceResponsibility'})),
    'Governance-Rule-DrE-Basic': FormatSet(target_type='Governance Rule', heading='Governance-Rule-DrE-Basic Attributes', description='Auto-generated format for Governance Rule (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'GovernanceRule'})),
    'Governance-Strategy-DrE-Basic': FormatSet(target_type='Governance Strategy', heading='Governance-Strategy-DrE-Basic Attributes', description='Auto-generated format for Governance Strategy (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Business Imperatives', key='business_imperatives'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Business Imperatives', key='business_imperatives')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'GovernanceStrategy'})),
    'Governance-Zone-DrE-Basic': FormatSet(target_type='Governance Zone', heading='Governance-Zone-DrE-Basic Attributes', description='Auto-generated format for Governance Zone (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Criteria', key='criteria'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Criteria', key='criteria')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'GovernanceZone'})),
    'Home-Collection-DrE-Basic': FormatSet(target_type='Home Collection', heading='Home-Collection-DrE-Basic Attributes', description='Auto-generated format for Home Collection (Create, Basic).', family='Collections', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose')])], action=ActionParameter(function='CollectionManager.find_collections', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'HomeCollection'})),
    'Informal-Tag-DrE-Basic': FormatSet(target_type='Informal Tag', heading='Informal-Tag-DrE-Basic Attributes', description='Auto-generated format for Informal Tag (Create, Basic).', family='Feedback', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Version Identifier', key='version_identifier'), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier')])], action=ActionParameter(function='ServerClient.find_tags', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'])),
    'Information-Supply-Chain-DrE-Basic': FormatSet(target_type='Information Supply Chain', heading='Information-Supply-Chain-DrE-Basic Attributes', description='Auto-generated format for Information Supply Chain (Create, Basic).', family='Solution Architect', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='In Information Supply Chain', key='in_supply_chain'), Column(name='Integration Style', key='integration_style'), Column(name='Nested Information Supply Chains', key='nested_info_supply_chains'), Column(name='Purposes', key='purposes'), Column(name='Scope', key='scope'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose'), Column(name='In Information Supply Chain', key='in_supply_chain'), Column(name='Integration Style', key='integration_style'), Column(name='Nested Information Supply Chains', key='nested_info_supply_chains'), Column(name='Purposes', key='purposes'), Column(name='Scope', key='scope')])], action=ActionParameter(function='SolutionArchitect.find_information_supply_chains', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'])),
    'IT-Profile-Role-DrE-Basic': FormatSet(target_type='IT Profile Role', heading='IT-Profile-Role-DrE-Basic Attributes', description='Auto-generated format for IT Profile Role (Create, Basic).', family='Actor Manager', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Scope', key='scope'), Column(name='Version Identifier', key='version_identifier'), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Scope', key='scope')])], action=ActionParameter(function='ActorManager.find_actor_roles', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'ITProfileRole'})),
    'License-Type-DrE-Basic': FormatSet(target_type='License Type', heading='License-Type-DrE-Basic Attributes', description='Auto-generated format for License Type (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Entitlements', key='entitlements'), Column(name='Obligations', key='obligations'), Column(name='Restrictions', key='restrictions'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Entitlements', key='entitlements'), Column(name='Obligations', key='obligations'), Column(name='Restrictions', key='restrictions')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'LicenseType'})),
    'Like-DrE-Basic': FormatSet(target_type='Like', heading='Like-DrE-Basic Attributes', description='Auto-generated format for Like (Create, Basic).', family='Feedback', formats=[Format(types=['LIST'], attributes=[Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Version Identifier', key='current_version'), Column(name='Identifier', key='identifier'), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Version Identifier', key='current_version'), Column(name='Identifier', key='identifier'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='URL', key='url')])]),
    'Methodology-DrE-Basic': FormatSet(target_type='Methodology', heading='Methodology-DrE-Basic Attributes', description='Auto-generated format for Methodology (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'Methodology'})),
    'Namespace-DrE-Basic': FormatSet(target_type='Namespace', heading='Namespace-DrE-Basic Attributes', description='Auto-generated format for Namespace (Create, Basic).', family='Collections', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose')])], action=ActionParameter(function='CollectionManager.find_collections', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'Namespace'})),
    'Naming-Standard-Rule-DrE-Basic': FormatSet(target_type='Naming Standard Rule', heading='Naming-Standard-Rule-DrE-Basic Attributes', description='Auto-generated format for Naming Standard Rule (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Name Patterns', key='name_patterns'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Name Patterns', key='name_patterns')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'NamingStandardRule'})),
    'Notification-Type-DrE-Basic': FormatSet(target_type='Notification Type', heading='Notification-Type-DrE-Basic Attributes', description='Auto-generated format for Notification Type (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Planned Completion Date', key='planned_completion_date'), Column(name='Multiple Notifications Permitted', key='multiple_notifications_permitted'), Column(name='Next Scheduled Notification', key='next_scheduled_notification'), Column(name='Notification Count', key='notification_count'), Column(name='Notification Interval', key='notification_interval'), Column(name='Minimum Notification Interval', key='minimum_notification_interval'), Column(name='Planned Start Date', key='planned_start_date'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Planned Completion Date', key='planned_completion_date'), Column(name='Multiple Notifications Permitted', key='multiple_notifications_permitted'), Column(name='Next Scheduled Notification', key='next_scheduled_notification'), Column(name='Notification Count', key='notification_count'), Column(name='Notification Interval', key='notification_interval'), Column(name='Minimum Notification Interval', key='minimum_notification_interval'), Column(name='Planned Start Date', key='planned_start_date')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'NotificationType'})),
    'Organization-DrE-Basic': FormatSet(target_type='Organization', heading='Organization-DrE-Basic Attributes', description='Auto-generated format for Organization (Create, Basic).', family='Actor Manager', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Team Type', key='team_type'), Column(name='Version Identifier', key='version_identifier'), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Team Type', key='team_type')])], action=ActionParameter(function='ActorManager.find_actor_profiles', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'Organization'})),
    'Person-DrE-Basic': FormatSet(target_type='Person', heading='Person-DrE-Basic Attributes', description='Auto-generated format for Person (Create, Basic).', family='Actor Manager', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Courtesy Title', key='courtesy_title'), Column(name='Employee Number', key='employee_number'), Column(name='Employee Type', key='employee_type'), Column(name='Full Name', key='full_name'), Column(name='Given Names', key='given_names'), Column(name='Initials', key='initials'), Column(name='Job Title', key='job_title'), Column(name='Preferred Language', key='preferred_language'), Column(name='Pronouns', key='pronouns'), Column(name='Resident Country', key='resident_country'), Column(name='Surname', key='surname'), Column(name='Time Zone', key='time_zone'), Column(name='Version Identifier', key='version_identifier'), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Courtesy Title', key='courtesy_title'), Column(name='Employee Number', key='employee_number'), Column(name='Employee Type', key='employee_type'), Column(name='Full Name', key='full_name'), Column(name='Given Names', key='given_names'), Column(name='Initials', key='initials'), Column(name='Job Title', key='job_title'), Column(name='Preferred Language', key='preferred_language'), Column(name='Pronouns', key='pronouns'), Column(name='Resident Country', key='resident_country'), Column(name='Surname', key='surname'), Column(name='Time Zone', key='time_zone')])], action=ActionParameter(function='ActorManager.find_actor_profiles', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'Person'})),
    'Person-Role-DrE-Basic': FormatSet(target_type='Person Role', heading='Person-Role-DrE-Basic Attributes', description='Auto-generated format for Person Role (Create, Basic).', family='Actor Manager', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Scope', key='scope'), Column(name='Headcount', key='head_count'), Column(name='Version Identifier', key='version_identifier'), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Scope', key='scope'), Column(name='Headcount', key='head_count')])], action=ActionParameter(function='ActorManager.find_actor_roles', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'PersonRole'})),
    'Personal-Project-DrE-Basic': FormatSet(target_type='Personal Project', heading='Personal-Project-DrE-Basic Attributes', description='Auto-generated format for Personal Project (Create, Basic).', family='Projects', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Actual Completion Date', key='actual_completion_date'), Column(name='Actual Start Date', key='actual_start_date'), Column(name='Mission', key='mission'), Column(name='Planned Completion Date', key='planned_completion_date'), Column(name='Planned Start Date', key='planned_start_date'), Column(name='Priority', key='priority'), Column(name='Project Approach', key='approach'), Column(name='Project Health', key='project_health'), Column(name='Project Identifier', key='project_identifier'), Column(name='Project Management Style', key='management_style'), Column(name='Project Phase', key='project_phase'), Column(name='Project Results Usage', key='results_usage'), Column(name='Project Scope', key='project_scope'), Column(name='Project Type', key='project_type', valid_values=['Project', 'Campaign', 'Task', 'PersonalProject', 'StudyProject', 'Experiment']), Column(name='Purposes', key='purposes'), Column(name='Success Criteria', key='success_criteria'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Project Status', key='project_status'), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Actual Completion Date', key='actual_completion_date'), Column(name='Actual Start Date', key='actual_start_date'), Column(name='Mission', key='mission'), Column(name='Planned Completion Date', key='planned_completion_date'), Column(name='Planned Start Date', key='planned_start_date'), Column(name='Priority', key='priority'), Column(name='Project Approach', key='approach'), Column(name='Project Health', key='project_health'), Column(name='Project Identifier', key='project_identifier'), Column(name='Project Management Style', key='management_style'), Column(name='Project Phase', key='project_phase'), Column(name='Project Results Usage', key='results_usage'), Column(name='Project Scope', key='project_scope'), Column(name='Project Status', key='project_status'), Column(name='Project Type', key='project_type', valid_values=['Project', 'Campaign', 'Task', 'PersonalProject', 'StudyProject', 'Experiment']), Column(name='Purposes', key='purposes'), Column(name='Success Criteria', key='success_criteria')])], action=ActionParameter(function='ProjectManager.find_projects', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'include_only_classified_elements': ['PersonalProject']})),
    'Project-DrE-Basic': FormatSet(target_type='Project', heading='Project-DrE-Basic Attributes', description='Auto-generated format for Project (Create, Basic).', family='Projects', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Actual Completion Date', key='actual_completion_date'), Column(name='Actual Start Date', key='actual_start_date'), Column(name='Mission', key='mission'), Column(name='Planned Completion Date', key='planned_completion_date'), Column(name='Planned Start Date', key='planned_start_date'), Column(name='Priority', key='priority'), Column(name='Project Approach', key='approach'), Column(name='Project Health', key='project_health'), Column(name='Project Identifier', key='project_identifier'), Column(name='Project Management Style', key='management_style'), Column(name='Project Phase', key='project_phase'), Column(name='Project Results Usage', key='results_usage'), Column(name='Project Scope', key='project_scope'), Column(name='Project Type', key='project_type', valid_values=['Project', 'Campaign', 'Task', 'PersonalProject', 'StudyProject', 'Experiment']), Column(name='Purposes', key='purposes'), Column(name='Success Criteria', key='success_criteria'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Project Status', key='project_status'), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Actual Completion Date', key='actual_completion_date'), Column(name='Actual Start Date', key='actual_start_date'), Column(name='Mission', key='mission'), Column(name='Planned Completion Date', key='planned_completion_date'), Column(name='Planned Start Date', key='planned_start_date'), Column(name='Priority', key='priority'), Column(name='Project Approach', key='approach'), Column(name='Project Health', key='project_health'), Column(name='Project Identifier', key='project_identifier'), Column(name='Project Management Style', key='management_style'), Column(name='Project Phase', key='project_phase'), Column(name='Project Results Usage', key='results_usage'), Column(name='Project Scope', key='project_scope'), Column(name='Project Status', key='project_status'), Column(name='Project Type', key='project_type', valid_values=['Project', 'Campaign', 'Task', 'PersonalProject', 'StudyProject', 'Experiment']), Column(name='Purposes', key='purposes'), Column(name='Success Criteria', key='success_criteria')])], action=ActionParameter(function='ProjectManager.find_projects', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'])),
    'Rating-DrE-Basic': FormatSet(target_type='Rating', heading='Rating-DrE-Basic Attributes', description='Auto-generated format for Rating (Create, Basic).', family='Feedback', formats=[Format(types=['LIST'], attributes=[Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Stars', key='stars', valid_values=['NO_RECOMMENDATION', 'ONE_STAR', 'TWO_STARS', 'THREE_STARS', 'FOUR_STARS', 'FIVE_STARS']), Column(name='Review', key='review'), Column(name='Version Identifier', key='current_version'), Column(name='Identifier', key='identifier'), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Stars', key='stars', valid_values=['NO_RECOMMENDATION', 'ONE_STAR', 'TWO_STARS', 'THREE_STARS', 'FOUR_STARS', 'FIVE_STARS']), Column(name='Review', key='review'), Column(name='Category', key='category'), Column(name='Version Identifier', key='current_version'), Column(name='Identifier', key='identifier'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='URL', key='url')])]),
    'Recent-Access-DrE-Basic': FormatSet(target_type='Recent Access', heading='Recent-Access-DrE-Basic Attributes', description='Auto-generated format for Recent Access (Create, Basic).', family='Collections', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose')])], action=ActionParameter(function='CollectionManager.find_collections', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'RecentAccess'})),
    'Regulation-Article-DrE-Basic': FormatSet(target_type='Regulation Article', heading='Regulation-Article-DrE-Basic Attributes', description='Auto-generated format for Regulation Article (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'RegulationArticle'})),
    'Regulation-DrE-Basic': FormatSet(target_type='Regulation', heading='Regulation-DrE-Basic Attributes', description='Auto-generated format for Regulation (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Regulation Source', key='regulation_source'), Column(name='Regulators', key='regulators'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Regulation Source', key='regulation_source'), Column(name='Regulators', key='regulators')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'Regulation'})),
    'Related-Media-DrE-Basic': FormatSet(target_type='Related Media', heading='Related-Media-DrE-Basic Attributes', description='Auto-generated format for Related Media (Create, Basic).', family='External Reference', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Attribution', key='attribution'), Column(name='Copyright', key='copyright'), Column(name='License', key='license'), Column(name='Organization', key='organization'), Column(name='Reference Abstract', key='reference_abstract'), Column(name='Reference Title', key='reference_title'), Column(name='Sources', key='reference_sources'), Column(name='Default Media Usage', key='default_media_usage', valid_values=['ICON', 'THUMBNAIL', 'ILLUSTRATION', 'USAGE_GUIDANCE', 'OTHER']), Column(name='Default Media Usage Other Id', key='default_media_usage_other_id'), Column(name='Media Type', key='media_type', valid_values=['IMAGE', 'AUDIO', 'DOCUMENT', 'VIDEO', 'OTHER']), Column(name='Media Type Other Id', key='media_type_other_id'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Attribution', key='attribution'), Column(name='Copyright', key='copyright'), Column(name='License', key='license'), Column(name='Organization', key='organization'), Column(name='Reference Abstract', key='reference_abstract'), Column(name='Reference Title', key='reference_title'), Column(name='Sources', key='reference_sources'), Column(name='Default Media Usage', key='default_media_usage', valid_values=['ICON', 'THUMBNAIL', 'ILLUSTRATION', 'USAGE_GUIDANCE', 'OTHER']), Column(name='Default Media Usage Other Id', key='default_media_usage_other_id'), Column(name='Media Type', key='media_type', valid_values=['IMAGE', 'AUDIO', 'DOCUMENT', 'VIDEO', 'OTHER']), Column(name='Media Type Other Id', key='media_type_other_id')])], action=ActionParameter(function='ExternalReferences.find_external_references', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_types': ['RelatedMedia']})),
    'Report-Type-DrE-Basic': FormatSet(target_type='Report Type', heading='Report-Type-DrE-Basic Attributes', description='Auto-generated format for Report Type (Create, Basic).', family='Data Designer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose')])], action=ActionParameter(function='CollectionManager.find_collections', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'ReportType'})),
    'Results-Set-DrE-Basic': FormatSet(target_type='Results Set', heading='Results-Set-DrE-Basic Attributes', description='Auto-generated format for Results Set (Create, Basic).', family='Collections', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose')])], action=ActionParameter(function='CollectionManager.find_collections', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'ResultsSet'})),
    'Root-Collection-DrE-Basic': FormatSet(target_type='Root Collection', heading='Root-Collection-DrE-Basic Attributes', description='Auto-generated format for Root Collection (Create, Basic).', family='Collections', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose')])], action=ActionParameter(function='CollectionManager.find_collections', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'RootCollection'})),
    'Security-Access-Control-DrE-Basic': FormatSet(target_type='Security Access Control', heading='Security-Access-Control-DrE-Basic Attributes', description='Auto-generated format for Security Access Control (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'SecurityAccessControl'})),
    'Security-Group-DrE-Basic': FormatSet(target_type='Security Group', heading='Security-Group-DrE-Basic Attributes', description='Auto-generated format for Security Group (Create, Basic).', family='Collections', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Distinguished Name', key='distinguished_name'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose'), Column(name='Distinguished Name', key='distinguished_name')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'SecurityGroup'})),
    'Security-List-DrE-Basic': FormatSet(target_type='Security List', heading='Security-List-DrE-Basic Attributes', description='Auto-generated format for Security List (Create, Basic).', family='Collections', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Distinguished Name', key='distinguished_name'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose'), Column(name='Distinguished Name', key='distinguished_name')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'SecurityList'})),
    'Security-Role-DrE-Basic': FormatSet(target_type='Security Role', heading='Security-Role-DrE-Basic Attributes', description='Auto-generated format for Security Role (Create, Basic).', family='Collections', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Distinguished Name', key='distinguished_name'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose'), Column(name='Distinguished Name', key='distinguished_name')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'SecurityRole'})),
    'Service-Level-Objective-DrE-Basic': FormatSet(target_type='Service Level Objective', heading='Service-Level-Objective-DrE-Basic Attributes', description='Auto-generated format for Service Level Objective (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'ServiceLevelObjective'})),
    'Solution-Blueprint-DrE-Basic': FormatSet(target_type='Solution Blueprint', heading='Solution-Blueprint-DrE-Basic Attributes', description='Auto-generated format for Solution Blueprint (Create, Basic).', family='Solution Architect', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Role List', key='role_list'), Column(name='Solution Components', key='solution_components'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose'), Column(name='Role List', key='role_list'), Column(name='Solution Components', key='solution_components')])], action=ActionParameter(function='SolutionArchitect.find_solution_blueprints', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'])),
    'Solution-Component-DrE-Basic': FormatSet(target_type='Solution Component', heading='Solution-Component-DrE-Basic Attributes', description='Auto-generated format for Solution Component (Create, Basic).', family='Solution Architect', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Actors', key='actors'), Column(name='In Information Supply Chain', key='in_supply_chain'), Column(name='In Solution Blueprints', key='in_solution_blueprints'), Column(name='In Solution Components', key='in_components'), Column(name='Planned Deployed Implementation Type', key='planned_deployed_impl_type'), Column(name='Solution Component Type', key='solution_component_type'), Column(name='Solution SubComponents', key='solution_sub_components'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Actors', key='actors'), Column(name='In Information Supply Chain', key='in_supply_chain'), Column(name='In Solution Blueprints', key='in_solution_blueprints'), Column(name='In Solution Components', key='in_components'), Column(name='Planned Deployed Implementation Type', key='planned_deployed_impl_type'), Column(name='Solution Component Type', key='solution_component_type'), Column(name='Solution SubComponents', key='solution_sub_components')])], action=ActionParameter(function='SolutionArchitect.find_solution_components', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'])),
    'Solution-Role-DrE-Basic': FormatSet(target_type='Solution Role', heading='Solution-Role-DrE-Basic Attributes', description='Auto-generated format for Solution Role (Create, Basic).', family='Solution Architect', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Role Domain Identifier', key='role_domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Role Identifier', key='role_identifier'), Column(name='Role Type', key='role_type'), Column(name='Scope', key='scope'), Column(name='Title', key='title'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Role Domain Identifier', key='role_domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Role Identifier', key='role_identifier'), Column(name='Role Type', key='role_type'), Column(name='Scope', key='scope'), Column(name='Title', key='title')])], action=ActionParameter(function='SolutionArchitect.find_solution_roles', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'])),
    'Study-Project-DrE-Basic': FormatSet(target_type='Study Project', heading='Study-Project-DrE-Basic Attributes', description='Auto-generated format for Study Project (Create, Basic).', family='Projects', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Actual Completion Date', key='actual_completion_date'), Column(name='Actual Start Date', key='actual_start_date'), Column(name='Mission', key='mission'), Column(name='Planned Completion Date', key='planned_completion_date'), Column(name='Planned Start Date', key='planned_start_date'), Column(name='Priority', key='priority'), Column(name='Project Approach', key='approach'), Column(name='Project Health', key='project_health'), Column(name='Project Identifier', key='project_identifier'), Column(name='Project Management Style', key='management_style'), Column(name='Project Phase', key='project_phase'), Column(name='Project Results Usage', key='results_usage'), Column(name='Project Scope', key='project_scope'), Column(name='Project Type', key='project_type', valid_values=['Project', 'Campaign', 'Task', 'PersonalProject', 'StudyProject', 'Experiment']), Column(name='Purposes', key='purposes'), Column(name='Success Criteria', key='success_criteria'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Project Status', key='project_status'), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Actual Completion Date', key='actual_completion_date'), Column(name='Actual Start Date', key='actual_start_date'), Column(name='Mission', key='mission'), Column(name='Planned Completion Date', key='planned_completion_date'), Column(name='Planned Start Date', key='planned_start_date'), Column(name='Priority', key='priority'), Column(name='Project Approach', key='approach'), Column(name='Project Health', key='project_health'), Column(name='Project Identifier', key='project_identifier'), Column(name='Project Management Style', key='management_style'), Column(name='Project Phase', key='project_phase'), Column(name='Project Results Usage', key='results_usage'), Column(name='Project Scope', key='project_scope'), Column(name='Project Status', key='project_status'), Column(name='Project Type', key='project_type', valid_values=['Project', 'Campaign', 'Task', 'PersonalProject', 'StudyProject', 'Experiment']), Column(name='Purposes', key='purposes'), Column(name='Success Criteria', key='success_criteria')])], action=ActionParameter(function='ProjectManager.find_projects', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'include_only_classified_elements': ['StudyProject']})),
    'Subject-Area-DrE-Basic': FormatSet(target_type='Subject Area', heading='Subject-Area-DrE-Basic Attributes', description='Auto-generated format for Subject Area (Create, Basic).', family='Collections', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose')])], action=ActionParameter(function='CollectionManager.find_collections', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'SubjectArea'})),
    'Task-DrE-Basic': FormatSet(target_type='Task', heading='Task-DrE-Basic Attributes', description='Auto-generated format for Task (Create, Basic).', family='Projects', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Actual Completion Date', key='actual_completion_date'), Column(name='Actual Start Date', key='actual_start_date'), Column(name='Mission', key='mission'), Column(name='Planned Completion Date', key='planned_completion_date'), Column(name='Planned Start Date', key='planned_start_date'), Column(name='Priority', key='priority'), Column(name='Project Approach', key='approach'), Column(name='Project Health', key='project_health'), Column(name='Project Identifier', key='project_identifier'), Column(name='Project Management Style', key='management_style'), Column(name='Project Phase', key='project_phase'), Column(name='Project Results Usage', key='results_usage'), Column(name='Project Scope', key='project_scope'), Column(name='Project Type', key='project_type', valid_values=['Project', 'Campaign', 'Task', 'PersonalProject', 'StudyProject', 'Experiment']), Column(name='Purposes', key='purposes'), Column(name='Success Criteria', key='success_criteria'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Project Status', key='project_status'), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Actual Completion Date', key='actual_completion_date'), Column(name='Actual Start Date', key='actual_start_date'), Column(name='Mission', key='mission'), Column(name='Planned Completion Date', key='planned_completion_date'), Column(name='Planned Start Date', key='planned_start_date'), Column(name='Priority', key='priority'), Column(name='Project Approach', key='approach'), Column(name='Project Health', key='project_health'), Column(name='Project Identifier', key='project_identifier'), Column(name='Project Management Style', key='management_style'), Column(name='Project Phase', key='project_phase'), Column(name='Project Results Usage', key='results_usage'), Column(name='Project Scope', key='project_scope'), Column(name='Project Status', key='project_status'), Column(name='Project Type', key='project_type', valid_values=['Project', 'Campaign', 'Task', 'PersonalProject', 'StudyProject', 'Experiment']), Column(name='Purposes', key='purposes'), Column(name='Success Criteria', key='success_criteria')])], action=ActionParameter(function='ProjectManager.find_projects', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'include_only_classified_elements': ['Task']})),
    'Team-DrE-Basic': FormatSet(target_type='Team', heading='Team-DrE-Basic Attributes', description='Auto-generated format for Team (Create, Basic).', family='Actor Manager', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Team Type', key='team_type'), Column(name='Version Identifier', key='version_identifier'), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Team Type', key='team_type')])], action=ActionParameter(function='ActorManager.find_actor_profiles', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'Team'})),
    'Team-Role-DrE-Basic': FormatSet(target_type='Team Role', heading='Team-Role-DrE-Basic Attributes', description='Auto-generated format for Team Role (Create, Basic).', family='Actor Manager', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Scope', key='scope'), Column(name='Headcount', key='head_count'), Column(name='Version Identifier', key='version_identifier'), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Scope', key='scope'), Column(name='Headcount', key='head_count')])], action=ActionParameter(function='ActorManager.find_actor_roles', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'TeamRole'})),
    'Terms-and-Conditions-DrE-Basic': FormatSet(target_type='Terms and Conditions', heading='Terms-and-Conditions-DrE-Basic Attributes', description='Auto-generated format for Terms and Conditions (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Entitlements', key='entitlements'), Column(name='Obligations', key='obligations'), Column(name='Restrictions', key='restrictions'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Implementation Description', key='implementation_description'), Column(name='Entitlements', key='entitlements'), Column(name='Obligations', key='obligations'), Column(name='Restrictions', key='restrictions')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'TermsAndConditions'})),
    'Threat-DrE-Basic': FormatSet(target_type='Threat', heading='Threat-DrE-Basic Attributes', description='Auto-generated format for Threat (Create, Basic).', family='Governance Officer', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Domain Identifier', key='domain_identifier', valid_values=['ALL', 'DATA', 'PRIVACY', 'SECURITY', 'IT_INFRASTRUCTURE', 'SOFTWARE_DEVELOPMENT', 'CORPORATE', 'ASSET_MANAGEMENT', 'OTHER']), Column(name='Implications', key='implications'), Column(name='Importance', key='importance'), Column(name='Outcomes', key='outcomes'), Column(name='Results', key='results'), Column(name='Scope', key='scope'), Column(name='Summary', key='summary'), Column(name='Usage', key='usage')])], action=ActionParameter(function='GovernanceOfficer.find_governance_definitions', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'Threat'})),
    'Work-Item-List-DrE-Basic': FormatSet(target_type='Work Item List', heading='Work-Item-List-DrE-Basic Attributes', description='Auto-generated format for Work Item List (Create, Basic).', family='Collections', formats=[Format(types=['LIST'], attributes=[Column(name='Display Name', key='display_name'), Column(name='Qualified Name', key='qualified_name'), Column(name='GUID', key='guid'), Column(name='Description', key='description'), Column(name='Authors', key='authors'), Column(name='Purpose', key='purpose'), Column(name='Version Identifier', key='version_identifier'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Category', key='category')]), Format(types=['ALL'], attributes=[Column(name='Category', key='category'), Column(name='Description', key='description'), Column(name='Display Name', key='display_name'), Column(name='GUID', key='guid'), Column(name='Qualified Name', key='qualified_name'), Column(name='URL', key='url'), Column(name='Version Identifier', key='version_identifier'), Column(name='Authors', key='authors'), Column(name='Content Status', key='content_status', valid_values=['DRAFT', 'PREPARED', 'PROPOSED', 'APPROVED', 'REJECTED', 'ACTIVE', 'DEPRECATED', 'OTHER']), Column(name='Purpose', key='purpose')])], action=ActionParameter(function='CollectionManager.find_collections', required_params=['search_string'], optional_params=['sequencing_order', 'sequencing_property', 'page_size', 'start_from', 'starts_with', 'ends_with', 'ignore_case', 'classification_names', 'metadata_element_subtypes', 'metadata_element_type'], spec_params={'metadata_element_type': 'WorkItemList'})),
    'Report-Spec-Schema': FormatSet(
        target_type='Report Spec Schema',
        heading='Report Spec Schema Attributes',
        description='Auto-generated format for Report Spec Schema discovery.',
        family='Report Engine',
        formats=[
            Format(
                types=['LIST', 'ALL', 'DICT'],
                attributes=[
                    Column(name='Attribute Path', key='attribute_path'),
                    Column(name='Data Type', key='data_type')
                ]
            )
        ],
        action=ActionParameter(
            function='EgeriaTech.get_report_spec_schema',
            required_params=['report_spec_name'],
            optional_params=[],
            spec_params={}
        )
    )
})
# --- END GENERATED FORMAT SETS ---


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
            elif hasattr(combined[key], 'merge_with') and hasattr(value, 'merge_with'):
                # Deep merge FormatSet objects
                combined[key].merge_with(value)
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
USER_FORMAT_SETS_DIR = os.getenv("PYEGERIA_USER_REPORT_SPECS_DIR", os.getenv("PYEGERIA_USER_FORMAT_SETS_DIR", "../"))
# Constants
MD_SEPARATOR = "\n---\n\n"

# Standard optional parameters for search functions
OPTIONAL_SEQUENCING_PARAMS = ["sequencing_order", "sequencing_property"]
OPTIONAL_SEARCH_PARAMS = OPTIONAL_SEQUENCING_PARAMS + ["page_size", "start_from", "starts_with", "ends_with", "ignore_case","classification_names","metadata_element_subtypes","metadata_element_type" ]
OPTIONAL_FILTER_PARAMS = OPTIONAL_SEQUENCING_PARAMS + ["page_size", "start_from"]
# Define shared elements

COMMON_COLUMNS = [
    Column(name='Display Name', key='display_name'),
    Column(name='Qualified Name', key='qualified_name', format=False),
    Column(name='Category', key='category'),
    Column(name='Description', key='description', format=True),
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

NEW_MERMAID_COLUMNS = [
    Column(name="Collection Mermaid Mind Map", key="collectionMermaidMindMap"),
    Column(name="Zone Profile Mermaid Pie Chart", key="zoneProfileMermaidPieChart"),
    Column(name="Zone Profile Anchored Mermaid Pie Chart", key="zoneProfileAnchoredMermaidPieChart"),
    Column(name="Zone Profile All Mermaid Pie Chart", key="zoneProfileAllMermaidPieChart"),
]

# TODO: Research SecretStore retrieval/extraction path before enabling:
# - userAccountTypeProfileMermaidPieChart
# - userAccountStatusProfileMermaidPieChart


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
    Column(name='Folders', key='folder_display_names'),
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
    Column(name="Containing Members", key='collection_members', format='bulleted-list'),
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
    "Who created this?",  # header
    "Who last updated this?",  # header
    "Who owns this?",  # ownership classification
    "Who has been working on this?"  # header - modified_users
]
WHAT = [
    "What is this?",  # description
    "What is the source of this?",  # metadata_collection_id/name
    "What type is this?",  # type
    "What zone is this?",  # Anchors classification - zone membership
]

WHEN = [
    "When was this created?",  # create
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
    "Referenceable": FormatSet(
        heading="Default Attributes for a Referenceable",
        description="Basic attributes for a Referenceable",
        annotations={},  # No specific annotations
        family="General",
        question_spec=[{'perspectives': ["ANY"], 'questions': WHO + WHAT + WHEN}],
        formats=[
            Format(
                types=["ALL", "TABLE", "DICT"],
                attributes=COMMON_COLUMNS + [
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
                    Column(name="Content Status", key='content_status'),
                    Column(name="Activity Status", key='activity_status'),
                    Column(name="Deployment Status", key='deployment_status'),
                ],
            )
        ],
        # action=ActionParameter(
        #     function="ClassificationExplorer.get_elements_by_property_value",
        #     optional_params=OPTIONAL_FILTER_PARAMS + ["metadata_element_type"] + TIME_PARAMETERS,
        #     required_params=["property_value"],
        #     spec_params={"property_names": ["displayName", "qualifiedName"]},
        # )
    ),
    "Default": FormatSet(
        heading="Default Base Attributes",
        target_type="Any Metadata Element",
        description="Was a valid combination of report_spec and output_format provided?",
        annotations={},  # No specific annotations
        family="General",
        question_spec=[{'perspectives': ["ANY"], 'questions': WHO + WHAT + WHEN}],
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
            function="ClassificationExplorer.get_elements",
            optional_params=OPTIONAL_FILTER_PARAMS + ["metadata_element_type"] + TIME_PARAMETERS ,
            # spec_params={"property_names": ["displayName", "qualifiedName"]},
        )
    ),
    "Element-By-Owner": FormatSet(
        heading="Elements by Owner",
        description="Return elements for the specified owner",
        annotations={},  # No specific annotations
        family="General",
        question_spec=[{'perspectives': ["ANY"], 'questions': WHO + WHAT + WHEN}],
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
            function="ClassificationExplorer.get_owners_elements",
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
        question_spec=[
            {'perspectives': ["Business Analyst"],
             'questions': [
                 "Who is responsible for [data or domain]?",
                 "Find the contact for [team or department].",
                 "Who owns [dataset]?",
             ]},
            {'perspectives': ["Data Steward"],
             'questions': [
                 "Who are the data owners in [domain]?",
                 "Find actor profiles for [department].",
             ]},
            {'perspectives': ["Governance Officer"],
             'questions': [
                 "Who has governance responsibilities for [domain]?",
                 "Show me all registered actor profiles.",
             ]},
            {'perspectives': ["Project Manager"],
             'questions': [
                 "Who are the key stakeholders for [project]?",
             ]},
        ],
        formats=[
            Format(
                types=["ALL"],
                attributes=COMMON_COLUMNS + [
                    Column(name="Open Metadata Type Name", key='type_name'),
                    Column(name="GUID", key='GUID'),
                ],
            )
        ],
        action=ActionParameter(
            function="ActorManager.find_actor_profiles",
            optional_params=OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
            required_params=["search_string"],
            spec_params={},
        )
    ),
    "Actor-Profiles-Assigned-MD": FormatSet(
        target_type="Actor Profile",
        heading="Actor Profile - Assigned Actors",
        description="Actor Profile Assigned Actor Information",
        annotations={},  # No specific annotations
        family="ActorManager",
        question_spec=[
            {'perspectives': ["Governance Officer", "Data Steward"],
             'questions': [
                 "Who has been assigned to [role or responsibility]?",
                 "Which profiles have actors assigned to them?",
             ]},
        ],
        formats=[
            Format(
                types=["ALL"],
                attributes=COMMON_COLUMNS + [
                    Column(name="Open Metadata Type Name", key='type_name'),
                    Column(name="GUID", key='GUID'),
                    Column(name="Assigned Actors", key='sideLinks', detail_spec="Profile-Team-Detail"),
                ],
            )
        ],
        action=ActionParameter(
            function="ActorManager.find_actor_profiles",
            optional_params=OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
            required_params=["search_string"],
            spec_params={},
        )
    ),
"Profile-Team-Detail": FormatSet(
    target_type="Actor Profile",
    heading="Assigned Actors",
    description="Assigned Actors",
    family="ActorManager",
    formats=[
        Format(
            types=["LIST", "REPORT", "DICT", "TABLE"],
            attributes=[
                Column(name="Name", key="displayName"),
                Column(name="Qualified Name", key="qualifiedName"),
                Column(name="Employee Type", key="employeeType"),
                Column(name="Identifier", key="identifier"),
                Column(name="Employee Number", key="employeeNumber")
            ],
        )
    ],
),

    "Actor-Roles": FormatSet(
        target_type="Actor Profile",
        heading="Actor Profile",
        description="Actor Profile Information",
        annotations={},  # No specific annotations
        family="ActorManager",
        question_spec=[
            {'perspectives': ["Governance Officer"],
             'questions': [
                 "What data governance roles are defined?",
                 "What roles exist for [domain]?",
                 "Show me all actor roles.",
             ]},
            {'perspectives': ["Data Steward"],
             'questions': [
                 "What are the responsibilities of the [role] role?",
                 "What is the scope of the [role]?",
             ]},
            {'perspectives': ["Solution Architect"],
             'questions': [
                 "What roles are involved in [process]?",
             ]},
        ],
        formats=[
            Format(
                types=["ALL"],
                attributes=COMMON_COLUMNS + COMMON_METADATA_COLUMNS + [
                    Column(name="Scope", key='scope'),
                ],
            )
        ],
        action=ActionParameter(
            function="ActorManager.find_actor_roles",
            optional_params=OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
            required_params=["search_string"],
            spec_params={},
        )
    ),
    "Team-Members": FormatSet(
        target_type="Team",
        heading="Team Members",
        description="Team Members and Leaders Information",
        family="ActorManager",
        question_spec=[
            {'perspectives': ["Business Analyst"],
             'questions': [
                 "Who is on the [team] team?",
                 "What teams exist in our organization?",
             ]},
            {'perspectives': ["Project Manager"],
             'questions': [
                 "What team is responsible for [project]?",
                 "Who are the members of [team]?",
             ]},
            {'perspectives': ["Governance Officer", "Data Steward"],
             'questions': [
                 "What governance teams exist?",
                 "Which team manages [data domain]?",
             ]},
        ],
        formats=[
            Format(
                types=["ALL"],
                attributes=COMMON_COLUMNS + [
                    Column(name="Team Type", key='team_type'),
                    Column(name="Members", key="assigned_actors", detail_spec="Team-Member-Role-Detail"),
                ],
            )
        ],
        action=ActionParameter(
            function="ActorManager.find_actor_profiles",
            optional_params=OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
            required_params=["search_string"],
            spec_params={"metadata_element_type": "Team"},
        )
    ),
    "Team-Member-Role-Detail": FormatSet(
        target_type="Actor Role",
        heading="Team Members",
        description="Assigned Actors and Individuals",
        family="ActorManager",
        formats=[
            Format(
                types=["LIST", "REPORT", "DICT", "TABLE"],
                attributes=[
                    Column(name="Role", key="name"),
                    Column(name="Assignment Type", key="assignment_type"),
                    Column(name="Individual", key="individual_name"),
                    Column(name="Individual GUID", key="individual_guid"),
                ],
            )
        ],
    ),

    "User-Identities": FormatSet(
        target_type="User-Identity",
        heading="User Identity Information",
        description="User Identity Information",
        annotations={},  # No specific annotations
        family="ActorManager",
        question_spec=[
            {'perspectives': ["Security Officer"],
             'questions': [
                 "What user identities are registered?",
                 "Find the user identity for [person].",
                 "What is the user ID for [name]?",
             ]},
            {'perspectives': ["Governance Officer"],
             'questions': [
                 "Who has registered user identities?",
             ]},
        ],
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
            optional_params=OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
            required_params=["search_string"],
            spec_params={},
        )
    ),
"My-User": FormatSet(
        target_type="My-User",
        heading="My Information",
        description="User Information",
        annotations={},  # No specific annotations
        family="MyProfile",
        question_spec=[
            {'perspectives': ["Individual"],
             'questions': [
                 "Show me my profile.",
                 "What is my job title?",
                 "What roles am I assigned to?",
                 "What teams am I a member of?",
                 "What communities am I part of?",
                 "What projects am I on?",
             ]},
        ],
        formats=[
            Format(
                types=["DICT","LIST", "TABLE"],
                attributes= [
                    Column(name="Full Name", key='full_name'),
                    Column(name="Job Title", key='job_title'),
                    Column(name="Employee Number", key='employee_number'),
                    Column(name="Employee Type", key='employee_type'),
                    Column(name="User ID", key='user_id'),
                    Column(name="Job Status", key='job_status'),
                    Column(name="Contact Methods", key='contact_methods'),
                    Column(name="Roles", key='roles'),
                    Column(name="Teams", key='teams'),
                    Column(name="Communities", key='communities'),
                    Column(name="Projects", key='projects'),
                    Column(name="Note Logs", key='note_logs'),
                ],
            )
        ],
        action=ActionParameter(
            function="MyProfile.get_my_profile",
            optional_params=OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
            required_params=[],
            spec_params={},
        )
    ),
"My-User-MD": FormatSet(
        target_type="My-User",
        heading="My Information Master-Detail",
        description="User Information with links to details",
        annotations={},  # No specific annotations
        family="MyProfile",
        question_spec=[
            {'perspectives': ["Individual"],
             'questions': [
                 "Show me my full profile with all details.",
                 "Show me my roles, teams, projects and communities.",
                 "What is my contribution record?",
                 "Show me my activity and journals.",
             ]},
        ],
        formats=[
            Format(
                types=["DICT","LIST", "REPORT", "TABLE"],
                attributes= [
                    Column(name="Full Name", key='full_name'),
                    Column(name="Job Title", key='job_title'),
                    Column(name="Employee Number", key='employee_number'),
                    Column(name="Employee Type", key='employee_type'),
                    Column(name="User ID", key='user_id'),
                    Column(name="Job Status", key='job_status'),
                    Column(name="Contact Methods", key="contact_methods", detail_spec="My-User-Contact-Detail"),
                    Column(name="Roles", key="roles", detail_spec="My-User-Roles-Detail"),
                    Column(name="Teams", key="teams", detail_spec="My-User-Teams-Detail"),
                    Column(name="Communities", key="communities", detail_spec="My-User-Communities-Detail"),
                    Column(name="Projects", key="projects", detail_spec="My-User-Projects-Detail"),
                    Column(name="Contribution Record", key="contribution_record", detail_spec="My-User-Contribution-Record-Detail"),
                    Column(name="Note Logs", key="note_logs", detail_spec="My-User-Note-Logs-Detail"),
                    Column(name="Activity", key="activity_entries", detail_spec="My-User-Note-Logs-Detail"),
                    Column(name="Blogs", key="blog_entries", detail_spec="My-User-Note-Logs-Detail"),
                    Column(name="Journal", key="journal_entries", detail_spec="My-User-Note-Logs-Detail"),
                ],
            )
        ],
        action=ActionParameter(
            function="MyProfile.get_my_profile",
            optional_params=OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
            required_params=[],
            spec_params={},
        )
    ),
    "My-User-Contribution-Record-Detail": FormatSet(
        target_type="ContributionRecord",
        heading="Contribution Record",
        description="Detailed Contribution Record",
        family="MyProfile",
        formats=[
            Format(
                types=["LIST", "REPORT", "DICT", "TABLE"],
                attributes=[
                    Column(name="Karma Points", key="karma_points")
                ],
            )
        ],
    ),
    "My-User-Note-Logs-Detail": FormatSet(
        target_type="NoteLogEntry",
        heading="Note Log Entries",
        description="Detailed Note Log Entries",
        family="MyProfile",
        formats=[
            Format(
                types=["LIST", "REPORT", "DICT", "TABLE"],
                attributes=[
                    Column(name="Title", key="title"),
                    Column(name="Text", key="text"),
                    Column(name="Time", key="time"),
                    Column(name="Priority", key="priority"),
                    Column(name="Activity Status", key="activityStatus"),
                ],
            )
        ],
    ),
    "My-User-Activities": FormatSet(
        target_type="My-User",
        heading="My Activities",
        description="User Activity Entries",
        family="MyProfile",
        question_spec=[
            {'perspectives': ["Individual"],
             'questions': [
                 "Show me my recent activity.",
                 "What have I been working on?",
             ]},
        ],
        formats=[
            Format(
                types=["DICT", "LIST", "REPORT", "TABLE"],
                attributes=[
                    Column(name="Activity Entries", key="activity_entries", detail_spec="My-User-Note-Logs-Detail"),
                ],
            )
        ],
        action=ActionParameter(
            function="MyProfile.get_my_profile",
            optional_params=OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
            required_params=[],
            spec_params={},
        )
    ),
    "My-User-Blogs": FormatSet(
        target_type="My-User",
        heading="My Blogs",
        description="User Blog Entries",
        family="MyProfile",
        question_spec=[
            {'perspectives': ["Individual"],
             'questions': [
                 "Show me my blog posts.",
                 "What have I written about?",
             ]},
        ],
        formats=[
            Format(
                types=["DICT", "LIST", "REPORT", "TABLE"],
                attributes=[
                    Column(name="Blog Entries", key="blog_entries", detail_spec="My-User-Note-Logs-Detail"),
                ],
            )
        ],
        action=ActionParameter(
            function="MyProfile.get_my_profile",
            optional_params=OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
            required_params=[],
            spec_params={},
        )
    ),
    "My-User-Journals": FormatSet(
        target_type="My-User",
        heading="My Journals",
        description="User Journal Entries",
        family="MyProfile",
        question_spec=[
            {'perspectives': ["Individual"],
             'questions': [
                 "Show me my journal entries.",
                 "What are my recent journal notes?",
             ]},
        ],
        formats=[
            Format(
                types=["DICT", "LIST", "REPORT", "TABLE"],
                attributes=[
                    Column(name="Journal Entries", key="journal_entries", detail_spec="My-User-Note-Logs-Detail"),
                ],
            )
        ],
        action=ActionParameter(
            function="MyProfile.get_my_profile",
            optional_params=OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
            required_params=[],
            spec_params={},
        )
    ),
    "My-User-Contact-Detail": FormatSet(
    target_type="ContactDetails",
    heading="Contact Methods",
    description="Detailed Contact Methods",
    family="MyProfile",
    formats=[
        Format(
            types=["LIST", "REPORT", "DICT", "TABLE"],
            attributes=[
                Column(name="Name", key="name"),
                Column(name="Method Type", key="contactMethodType"),
                Column(name="Contact Type", key="contactType"),
                Column(name="Service", key="contactMethodService"),
                Column(name="Value", key="contactMethodValue"),
                Column(name="GUID", key="guid", format=True)


            ],
        )
    ],
),

"My-User-Roles-Detail": FormatSet(
    target_type="PersonRole",
    heading="Roles",
    description="Detailed Roles",
    family="MyProfile",
    formats=[
        Format(
            types=["LIST", "REPORT", "DICT", "TABLE"],
            attributes=[
                Column(name="Name", key="name"),
                Column(name="Type", key="type"),
                Column(name="Assignment Type", key="assignmentType"),
                Column(name="Identifier", key="identifier"),
                Column(name="Scope", key="scope"),
                Column(name="Description", key="description"),
                Column(name="GUID", key="guid", format=True),

            ],
        )
    ],
),

"My-User-Teams-Detail": FormatSet(
    target_type="Team",
    heading="Teams",
    description="Detailed Teams",
    family="MyProfile",
    formats=[
        Format(
            types=["LIST", "REPORT", "DICT", "TABLE"],
            attributes=[
                Column(name="Name", key="name"),
                Column(name="Assignment Type", key="assignmentType"),
                Column(name="Identifier", key="identifier"),
                Column(name="Team Type", key="teamType"),
                Column(name="Description", key="description"),
                Column(name="GUID", key="guid", format=True),
            ],
        )
    ],
),
"My-User-Projects-Detail": FormatSet(
    target_type="Project",
    heading="Projects",
    description="Details on projects I'm involved in",
    family="MyProfile",
    formats=[
        Format(
            types=["LIST", "DICT", "REPORT", "TABLE"],
            attributes=[
                Column(name="Name", key="display_name"),
                Column(name="Qualified Name", key="qualified_name"),
                Column(name="Project Status", key="project_status"),
                Column(name="Project Type", key="projectType"),
                Column(name="Description", key="description"),
                Column(name="Priority", key="priority"),
                Column(name="GUID", key="guid", format=True),
            ],
        )
    ],
),

"My-User-Communities-Detail": FormatSet(
    target_type="Community",
    heading="Communities",
    description="Detailed Communities",
    family="MyProfile",
    formats=[
        Format(
            types=["LIST", "REPORT", "DICT", "TABLE"],
            attributes=[
                Column(name="Name", key="name"),
                Column(name="Assignment Type", key="assignmentType"),
                Column(name="Description", key="description"),
                Column(name="GUID", key="guid", format=True),
            ],
        )
    ],
),
"My-User-ToDos": FormatSet(
    target_type="Todo",
    heading="Todos",
    description="My Todos",
    family="MyProfile",
    question_spec=[
        {'perspectives': ["Individual"],
         'questions': [
             "What are my open to-dos?",
             "Show me my to-do list.",
             "What tasks do I need to complete?",
             "What are my high-priority tasks?",
         ]},
    ],
    formats=[
        Format(
            types=["LIST", "REPORT", "DICT", "TABLE"],
            attributes=[
                Column(name="Name", key="displayName"),
                Column(name="Qualified Name", key="qualifiedName"),
                Column(name="Description", key="description"),
                Column(name="GUID", key="guid", format=True),
                Column(name="Type", key="typeName"),
                Column(name="Activity Status", key="activityStatus"),
                Column(name="Priority", key="priority"),
            ],
        )
    ],
    action=ActionParameter(
        function="MyProfile.get_my_to_dos",
        optional_params=OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
        required_params=[],
        spec_params={},
    )
),
"Org-Chart": FormatSet(
    target_type="Organization",
    heading="Org Chart",
    description="Organization Chart",
    family="Actor Manager",
    question_spec=[
        {'perspectives': ["Business Analyst"],
         'questions': [
             "Show me the organization chart.",
             "What does the [org / team] org chart look like?",
             "Who reports to [person or team]?",
         ]},
        {'perspectives': ["Governance Officer"],
         'questions': [
             "Show me the organizational structure for [division].",
             "Who are the senior leaders?",
         ]},
    ],
    formats=[
        Format(
            types=["MERMAID","REPORT"],
            attributes=[
                Column(name="Name", key='display_name'),
                Column(name="Mermaid Graph", key='mermaidGraph')
            ])
    ],
    action=ActionParameter(
        function="ActorManager.find_actor_profiles",
        optional_params=OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
        required_params=["search_string"],
        spec_params={'metadata_element_subtypes': ['Organization','Team'],'max_mermaid_node_count':10},
    )
),
    "TypeDef": FormatSet(
        target_type="TypeDef",
        heading="TypeDef",
        description="Attributes that describe TypeDefs",
        annotations={},  # No specific annotations
        family="TypeDef",
        question_spec=[
            {'perspectives': ["Data Engineer", "Solution Architect"],
             'questions': [
                 "What metadata types are defined?",
                 "What is [type name]?",
                 "Show me types in category [category].",
                 "What is the initial status for [type]?",
             ]},
        ],
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
        description="Attributes that describe valid values used by Egeria for metadata governance.",
        annotations={},  # No specific annotations
        family="Valid-Values",
        question_spec=[
            {'perspectives': ["Data Steward"],
             'questions': [
                 "What valid values are defined for [property name]?",
                 "What is the preferred value for [concept]?",
                 "What category does [valid value] belong to?",
                 "Show me all valid values for [type].",
             ]},
            {'perspectives': ["Data Engineer"],
             'questions': [
                 "What values are allowed for [field]?",
                 "Is [value] a valid entry for [property]?",
                 "What data type is used for [property]?",
             ]},
        ],
        formats=[
            Format(
                types=["ALL"],
                attributes=[
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
            function="ValidMetadataManager.get_valid_metadata_values",
            optional_params=OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS + ["type_name"],
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
        question_spec=[
            {'perspectives': ["DevOps Engineer"],
             'questions': [
                 "What engine actions are running?",
                 "Show me recent engine actions.",
                 "What actions are targeting [element]?",
                 "What are the action request sources for [action]?",
             ]},
        ],
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
                    Column(name="Action Targets", key='action_targets', detail_spec="Action-Targets-Detail"),
                    Column(name="Action Request Sources", key='action_request_sources', detail_spec="Action-Request-Sources-Detail"),
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
        question_spec=[
            {'perspectives': ["Business Analyst"],
             'questions': [
                 "Show me the full picture of [asset].",
                 "What systems does [asset] connect to?",
             ]},
            {'perspectives': ["Data Steward"],
             'questions': [
                 "Show me all details and relationships for [asset].",
                 "What anchors or classifies [asset]?",
             ]},
            {'perspectives': ["Solution Architect", "Data Engineer"],
             'questions': [
                 "Show me the data flow and lineage for [asset].",
                 "What is the field-level lineage for [asset]?",
             ]},
            {'perspectives': ["Data Scientist"],
             'questions': [
                 "Where does [dataset] come from? Show me the lineage.",
             ]},
        ],
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
            optional_params=OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
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
                               Column(name="Information Supply Chain Mermaid Graph",
                                      key='informationSupplyChainMermaidGraph'),
                               Column(name="Field Level Lineage Graph", key='fieldLevelLineageGraph'),
                               Column(name="Action Mermaid Graph", key='actionMermaidGraph'),
                               Column(name="Local Lineage Graph", key="localLineageGraph"),
                               Column(name="Edge Mermaid", key="edgeMermaidGraph"),
                               Column(name="ISC Implementation Graph", key='iscImplementationGraph'),
                               Column(name="Specification Mermaid Graph", key='specificationMermaidGraph'),
                               Column(name="Solution Blueprint Mermaid Graph", key='solutionBlueprintMermaidGraph'),
                               Column(name="Solution Subcomponent Mermaid Graph",
                                      key='solutionSubcomponentMermaidGraph'),
                           ] + NEW_MERMAID_COLUMNS,
            ),
            Format(
                types=["MERMAID"],
                attributes=[
                               Column(name="Mermaid Graph", key='mermaidGraph'),
                           ] + NEW_MERMAID_COLUMNS)
        ],

    ),
    "Common-Mermaid-Prop-Value": FormatSet(
        target_type="Referenceable",
        heading="Mermaid Graphs by Property Value",
        description="Mermaid Graphs using get by property value.",
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
                               Column(name="Information Supply Chain Mermaid Graph",
                                      key='informationSupplyChainMermaidGraph'),
                               Column(name="Field Level Lineage Graph", key='fieldLevelLineageGraph'),
                               Column(name="Action Mermaid Graph", key='actionMermaidGraph'),
                               Column(name="Local Lineage Graph", key="localLineageGraph"),
                               Column(name="Edge Mermaid", key="edgeMermaidGraph"),
                               Column(name="ISC Implementation Graph", key='iscImplementationGraph'),
                               Column(name="Specification Mermaid Graph", key='specificationMermaidGraph'),
                               Column(name="Solution Blueprint Mermaid Graph", key='solutionBlueprintMermaidGraph'),
                               Column(name="Solution Subcomponent Mermaid Graph",
                                      key='solutionSubcomponentMermaidGraph'),
                               Column(name="Governance Action Process Mermaid Graph",
                                      key='governanceActionProcessMermaidGraph'),
                           ] + NEW_MERMAID_COLUMNS,
            ),
            Format(
                types=["MERMAID"],
                attributes=[
                               Column(name="Mermaid Graph", key='mermaidGraph'),
                           ] + NEW_MERMAID_COLUMNS)
        ],
        action=ActionParameter(
            function="EgeriaTech.get_elements_by_property_value",
            optional_params=OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS + ["get_templates"],
            required_params=["property_value","property_names"],
            spec_params={},
        )
    ),
    "Tech-Type-Elements": FormatSet(
        target_type="TechTypeElements",
        heading="Technology Type Elements",
        description="Elements of a Technology",
        annotations={},  # No specific annotations
        family="Automated Curation",
        question_spec=[
            {'perspectives': ["DevOps Engineer", "Integration Specialist"],
             'questions': [
                 "What elements are catalogued for [tech type]?",
                 "Show me deployed instances of [technology].",
                 "What is the architecture diagram for [tech type]?",
             ]},
        ],
        formats=[
            Format(
                types=["MD", "FORM", ],
                attributes=COMMON_HEADER_COLUMNS + [
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
                types=["MERMAID", "HTML", "REPORT"],
                attributes=COMMON_HEADER_COLUMNS + [
                    Column(name='Display Name', key='display_name'),
                    Column(name="Qualified Name", key='qualified_name'),
                    Column(name="GUID", key='guid', Format=True),
                    Column(name="Description", key='description'),
                    Column(name="Deployed Implementation", key='deployedImplementationType'),
                    Column(name="Mermaid Graph", key='mermaidGraph'),
                    Column(name="Specification Mermaid Graph", key='specificationMermaidGraph')
                ]
            ),
            Format(
                types=["DICT", "TABLE", "LIST"],
                attributes=[
                    Column(name='Display Name', key='display_name'),
                    Column(name="Qualified Name", key='qualified_name'),
                    Column(name="GUID", key='guid', Format=True),
                    Column(name="Description", key='description'),
                    Column(name="Deployed Implementation", key='deployedImplementationType'),
                ]
            )
        ],
        action=ActionParameter(
            function="EgeriaTech.get_technology_type_elements",
            optional_params=OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS + ["get_templates"],
            required_params=["filter_string"],
            spec_params={},
        )
    ),
    "Search-Keywords": FormatSet(
        heading="Search Keyword Report",
        description="A report of elements with search keywords matching the specified string",
        annotations={},  # No specific annotations
        family="Feedback Manager",
        question_spec=[
            {'perspectives': ["Business Analyst", "Data Steward"],
             'questions': [
                 "What elements are tagged with [keyword]?",
                 "What is tagged as [topic]?",
                 "Find everything related to [term].",
             ]},
        ],
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
        question_spec=[
            {'perspectives': ["DevOps Engineer", "Integration Specialist"],
             'questions': [
                 "What are the details for [tech type]?",
                 "What catalog template placeholders does [tech type] require?",
                 "Show me full details for [technology].",
             ]},
        ],
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
            optional_params=OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
            required_params=["filter_string"],
            spec_params={},
        )
    ),
    "Tech-Type-Details-MD": FormatSet(
        target_type="TechTypeDetail",
        heading="Technology Type Details",
        description="Details of a Technology Type Valid Value as a Master-Detail pattern",
        annotations={},  # No specific annotations
        family="Automated Curation",
        question_spec=[
            {'perspectives': ["DevOps Engineer", "Integration Specialist"],
             'questions': [
                 "Show me the full master-detail for [tech type] including templates, processes, and references.",
                 "What governance processes and catalog templates exist for [technology]?",
             ]},
        ],
        formats=[
            Format(
                types=["ALL"],
                attributes=[
                    Column(name='Display Name', key='display_name'),
                    Column(name="Qualified Name", key='qualified_name'),
                    Column(name="GUID", key='guid'),
                    Column(name="Description", key='description'),
                    Column(name="Catalog Templates", key='catalog_templates', detail_spec="Catalog-Template-Detail"),
                    Column(name="Governance Processes", key='governance_action_processes', detail_spec="Governance-Action-Processes-Detail"),
                    Column(name="External References", key='external_references', detail_spec="External-Reference-Detail"),
                ],
            )
        ],
        action=ActionParameter(
            function="ServerClient.get_tech_type_detail",
            optional_params=OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
            required_params=["filter_string"],
            spec_params={},
        )
    ),
    "Catalog-Template-Detail": FormatSet(
        target_type="CatalogTemplates",
        heading="Catalog Templates",
        description="Detailed Catalog Template",
        family="Automated Curation",
        formats=[
            Format(
                types=["ALL"],
                attributes=[
                    Column(name="Catalog Template Name", key="template_display_name"),
                    Column(name="Catalog Template GUID", key="template_guid"),
                    Column(name="Description", key="template_description"),
                    # Column(name="Target Asset Name", key="target_display_name"),
                    # Column(name="Target Qualified Name", key="target_qualified_name"),
                    Column(name="Placeholder Properties", key="placeHolderProperty", detail_spec="Place-Holder-Property-Detail"),
                ],
            )
        ],
    ),
    "Governance-Action-Processes-Detail": FormatSet(
        target_type="GovernanceActionProcesses",
        heading="Governance Processes",
        description="Detailed Governance Processes",
        family="Automated Curation",
        formats=[
            Format(
                types=["LIST", "REPORT", "DICT", "TABLE"],
                attributes=[
                    Column(name="Governance Process Name", key="proc_display_name"),
                    Column(name="Qualified Name", key="proc_qualified_name"),
                    Column(name="Description", key="proc_description"),
                    Column(name="GUID", key="guid"),
                    Column(name="Governance Action Steps", key="governance_action_steps", detail_spec="Governance-Action-Steps-Detail"),
                ],
            )
        ],
    ),
    "Place-Holder-Property-Detail": FormatSet(
        target_type="placeHolderProperty",
        heading="Place Holder Properties",
        description="Detailed Place Holder Properties",
        family="Automated Curation",
        formats=[
            Format(
                types=["ALL"],
                attributes=[
                    Column(name="Property Name", key="name"),
                    Column(name="Description", key="description"),
                    Column(name="Data Type", key="dataType"),
                    Column(name="Example", key="example"),
                    Column(name="Required", key="required"),
                ],
            )
        ],
    ),
    "External-Reference-Detail": FormatSet(
        target_type="ExternalReferences",
        heading="External References",
        description="Detailed External References",
        family="Automated Curation",
        formats=[
            Format(
                types=["ALL"],
                attributes=[
                    Column(name="Reference Name", key="ref_display_name"),
                    Column(name="Qualified Name", key="ref_qualified_name"),
                    Column(name="Description", key="ref_description"),
                    Column(name="URL", key="ref_url"),
                ],
            )
        ],
    ),
    "Governance-Action-Steps-Detail": FormatSet(
        target_type="governanceActionSteps",
        heading="Governance Action Steps",
        description="Detailed Governance Action Steps",
        family="Automated Curation",
        formats=[
            Format(
                types=["ALL"],
                attributes=[
                    Column(name="Step Name", key="step_display_name"),
                    Column(name="Type Name", key="type_display_name"),
                    Column(name="Status", key="status"),
                ],
            )
        ],
    ),
    "Action-Targets-Detail": FormatSet(
        target_type="actionTargets",
        heading="Action Targets",
        description="Detailed Action Targets",
        family="Automated Curation",
        formats=[
            Format(
                types=["ALL"],
                attributes=[
                    Column(name="Target Name", key="target_display_name"),
                    Column(name="Qualified Name", key="target_qualified_name"),
                    Column(name="Description", key="target_description"),
                    Column(name="Action Target Name", key="actionTargetName"),
                ],
            )
        ],
    ),
    "Action-Request-Sources-Detail": FormatSet(
        target_type="actionRequestSources",
        heading="Action Request Sources",
        description="Detailed Action Request Sources",
        family="Automated Curation",
        formats=[
            Format(
                types=["ALL"],
                attributes=[
                    Column(name="Source Name", key="source_display_name"),
                    Column(name="Qualified Name", key="source_qualified_name"),
                ],
            )
        ],
    ),
    "Catalog-Target": FormatSet(
        target_type="CatalogTarget",
        heading="Catalog Target",
        description="Detailed Catalog Target Information",
        family="Automated Curation",
        question_spec=[
            {'perspectives': ["DevOps Engineer", "Integration Specialist"],
             'questions': [
                 "What catalog targets are configured?",
                 "What is [connector] cataloguing?",
                 "What is the target name for [integration connector]?",
             ]},
        ],
        formats=[
            Format(
                types=["ALL"],
                attributes=COMMON_COLUMNS + [
                    Column(name="Target Name", key="target_display_name"),
                    Column(name="Target Qualified Name", key="target_qualified_name"),
                    Column(name="Target Description", key="target_description"),
                    Column(name="Catalog Target Name", key="catalogTargetName"),
                ],
            )
        ],
    ),
    "Tech-Type-Processes": FormatSet(
        target_type="TechTypeDetail",
        heading="Technology Type Processes",
        description="Governance Processes for a Tech Type",
        annotations={},  # No specific annotations
        family="Automated Curation",
        question_spec=[
            {'perspectives': ["DevOps Engineer", "Governance Officer"],
             'questions': [
                 "What governance processes are defined for [tech type]?",
                 "Show me the process diagram for [tech type].",
                 "What automation is in place for [technology]?",
             ]},
        ],
        formats=[
            Format(
                types=["REPORT", "LIST", "FORM", "MD", "TABLE"],
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
            optional_params=OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
            required_params=["filter_string"],
            spec_params={},
        )
    ),
    "Tech-Types": FormatSet(
        target_type="TechTypeDetail",
        heading="Technology Type Details",
        description="Details of a Technology Type Valid Value.",
        annotations={},  # No specific annotations
        family="Automated Curation",
        question_spec=[
            {'perspectives': ["DevOps Engineer", "Integration Specialist"],
             'questions': [
                 "What technology types are registered?",
                 "Is [technology] a registered tech type?",
                 "Show me tech types matching [name].",
             ]},
            {'perspectives': ["Data Engineer"],
             'questions': [
                 "What technology types can be catalogued?",
                 "What is [tech type] used for?",
             ]},
        ],
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
    "Platforms": FormatSet(
        target_type="Platform",
        heading="OMAG Server Platform",
        description="Details of an OMAG Server Platform",
        annotations={},
        family="RuntimeManager",
        question_spec=[
            {'perspectives': ["DevOps Engineer"],
             'questions': [
                 "What OMAG platforms are registered?",
                 "What version is [platform] running?",
                 "When did [platform] last start?",
                 "What servers are on [platform]?",
             ]},
        ],
        formats=[
            Format(
                types=["ALL", "TABLE", "DICT"],
                attributes=COMMON_COLUMNS + [
                    Column(name="GUID", key='guid'),
                    Column(name="Platform URL", key='platform_url_root'),
                    Column(name="Platform Version", key='version'),
                    Column(name="Platform Origin", key='platform_origin'),
                    Column(name="Platform Start Time", key='platform_start_time'),
                    Column(name="Build Properties", key="platform_build_properties"),
                    Column(name="Servers", key="omag_servers"),
                ],
            )
        ],
    ),
    "OMAGServers": FormatSet(
        target_type="OMAGServer",
        heading="OMAG Server",
        description="Details of an OMAG Server",
        annotations={},
        family="RuntimeManager",
        question_spec=[
            {'perspectives': ["DevOps Engineer"],
             'questions': [
                 "What OMAG servers are running?",
                 "What is the status of [server]?",
                 "What type of server is [server]?",
                 "Show me the configuration for [server].",
             ]},
        ],
        formats=[
            Format(
                types=["ALL", "TABLE", "DICT"],
                attributes=COMMON_COLUMNS + [
                    Column(name="GUID", key='guid'),
                    Column(name="Server Name", key='server_name'),
                    Column(name="Server Type", key='server_type'),
                    Column(name="Server Status", key='server_active_status'),
                    Column(name="Server Config", key='server_configuration'),
                ],
            )
        ],
    ),
    "IntegrationConnectors": FormatSet(
        target_type="IntegrationConnector",
        heading="Integration Connector",
        description="Details of an Integration Connector",
        annotations={},
        family="RuntimeManager",
        question_spec=[
            {'perspectives': ["DevOps Engineer", "Integration Specialist"],
             'questions': [
                 "What integration connectors are running?",
                 "What is the status of [connector]?",
                 "What does [connector] integrate with?",
                 "When did [connector] last change status?",
                 "What metadata source does [connector] use?",
             ]},
        ],
        formats=[
            Format(
                types=["ALL", "TABLE", "DICT"],
                attributes=COMMON_COLUMNS + [
                    Column(name="GUID", key='guid'),
                    Column(name="Connector Name", key='connector_name'),
                    Column(name="Connector Type", key='connector_type'),
                    Column(name="Metadata Source", key='metadata_source_qualified_name'),
                    Column(name="Status", key='status'),
                    Column(name="Last Status Change", key='last_status_change'),
                ],
            )
        ],
    ),

    "Journal-Entry-DrE": FormatSet(
        target_type="Notification",
        heading="Journal Entry",
        description="Details of a journal entry.",
        annotations={},  # No specific annotations
        family="Feedback Manager",
        question_spec=[
            {'perspectives': ["Individual"],
             'questions': [
                 "Show me journal entries for [topic].",
                 "What notes exist in [journal]?",
             ]},
            {'perspectives': ["Data Steward"],
             'questions': [
                 "What stewardship notes have been recorded for [element]?",
                 "Show me journal entries about [data or subject].",
             ]},
        ],
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
        question_spec=[
            {'perspectives': ["Business Analyst", "Data Steward"],
             'questions': [
                 "What informal tags exist?",
                 "What elements are tagged with [tag]?",
                 "Show me all tags matching [name].",
             ]},
        ],
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
        question_spec=[
            {'perspectives': ["Researcher", "Business Analyst"],
             'questions': [
                 "What external references are catalogued?",
                 "Are there references to [topic or standard]?",
                 "What is the URL for [reference]?",
                 "Who published [reference]?",
             ]},
            {'perspectives': ["Data Steward"],
             'questions': [
                 "What external sources are linked to [element]?",
                 "Show me references categorised as [category].",
             ]},
        ],
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
        question_spec=[
            {'perspectives': ["Researcher", "Business Analyst"],
             'questions': [
                 "What related media is catalogued?",
                 "Are there images or videos for [topic]?",
                 "Show me media of type [media type].",
             ]},
        ],
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
        question_spec=[
            {'perspectives': ["Researcher"],
             'questions': [
                 "What documents are cited in the metadata?",
                 "Who published [document]?",
                 "What is the publication date of [document]?",
                 "Show me cited documents about [topic].",
             ]},
            {'perspectives': ["Governance Officer"],
             'questions': [
                 "What regulatory documents or standards are referenced?",
             ]},
        ],
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
        question_spec=[
            {'perspectives': ["Business Analyst"],
             'questions': [
                 "What data projects are underway?",
                 "Are there any projects affecting [data domain]?",
             ]},
            {'perspectives': ["Project Manager"],
             'questions': [
                 "What projects are currently active?",
                 "Show me projects by priority.",
                 "Who is assigned to [project]?",
                 "What is the status of [project]?",
                 "What projects started in [period]?",
             ]},
            {'perspectives': ["Data Steward"],
             'questions': [
                 "Are there active projects that will change [data]?",
                 "What governance projects are running?",
             ]},
        ],
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
        question_spec=[
            {'perspectives': ["Business Analyst", "Researcher"],
             'questions': [
                 "What glossaries do we have?",
                 "Is there a glossary for [finance / customer / HR / regulatory]?",
                 "Which glossary covers [subject area or topic]?",
                 "Where can I find definitions for [domain]?",
             ]},
            {'perspectives': ["Data Steward"],
             'questions': [
                 "What is the [glossary name] glossary used for?",
                 "Which glossaries are in [language]?",
                 "How many glossaries exist?",
                 "What folders are defined in [glossary]?",
             ]},
            {'perspectives': ["Governance Officer"],
             'questions': [
                 "Which glossaries are approved for regulatory or compliance use?",
                 "Show me the compliance glossary.",
             ]},
        ],
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
        question_spec=[
            {'perspectives': ["Business Analyst", "Researcher"],
             'questions': [
                 "What does [term] mean?",
                 "Find terms related to [concept or topic].",
                 "What terms are in the [subject area]?",
                 "Give me an example of how [term] is used.",
                 "Is there a definition for [abbreviation or acronym]?",
             ]},
            {'perspectives': ["Data Steward"],
             'questions': [
                 "Which terms have usage notes?",
                 "Show me terms that are no longer effective.",
                 "Who last updated [term]?",
                 "What terms were updated recently?",
                 "Which terms belong to [glossary]?",
             ]},
            {'perspectives': ["Data Scientist", "Data Engineer"],
             'questions': [
                 "What are the technical definitions for [feature or concept]?",
                 "Find terms related to [dataset or model].",
             ]},
            {'perspectives': ["Governance Officer"],
             'questions': [
                 "What regulatory or compliance terms are defined?",
                 "Show me terms with usage restrictions.",
                 "Which terms are still in draft status?",
             ]},
        ],
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
        question_spec=[
            {'perspectives': ["Business Analyst", "Data Steward", "Data Engineer"],
             'questions': [
                 "How do I use [Dr.Egeria command]?",
                 "What does [command] do?",
                 "Show me help for [topic].",
                 "What commands are available for [task]?",
             ]},
        ],
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
        question_spec=[
            {'perspectives': ["Business Analyst"],
             'questions': [
                 "What data collections are available?",
                 "Show me collections about [topic or domain].",
                 "What is in the [collection name] collection?",
                 "What collections were created recently?",
             ]},
            {'perspectives': ["Data Steward"],
             'questions': [
                 "Who created the [collection] collection?",
                 "Which collections have no classification?",
                 "What collections is [element] a member of?",
                 "When was [collection] last updated?",
             ]},
            {'perspectives': ["Solution Architect"],
             'questions': [
                 "Show me a visual map of our data collections.",
                 "How are our collections structured and related?",
             ]},
        ],
        formats=[MERMAID_FORMAT, COLLECTION_DICT, COLLECTION_TABLE, COLLECTION_REPORT, COMMON_FORMATS_ALL],
        # Reusing common formats
        action=ActionParameter(
            function="CollectionManager.find_collections",
            required_params=["search_string"],
            optional_params=OPTIONAL_SEARCH_PARAMS,
            spec_params={},
        )
    ),
    "Collection-MindMap": FormatSet(
        target_type="Collection",
        heading="Collection Mind Map",
        description="Displays the collection Mermaid mind map.",
        annotations=COMMON_ANNOTATIONS,
        family="Collection Manager",
        question_spec=[
            {'perspectives': ["Business Analyst"],
             'questions': [
                 "Show me a mind map of [collection].",
                 "Give me a visual overview of what is in [collection].",
             ]},
            {'perspectives': ["Data Steward"],
             'questions': [
                 "Show me the structure of [collection] as a diagram.",
                 "What does the collection hierarchy look like?",
             ]},
        ],
        formats=[
            Format(
                types=["REPORT"],
                attributes=COMMON_COLUMNS + [
                    Column(name="GUID", key="guid"),
                    Column(name="Collection Mermaid Mind Map", key="collectionMermaidMindMap"),
                ],
            ),
            Format(
                types=["MERMAID"],
                attributes=[
                    Column(name="Collection Mermaid Mind Map", key="collectionMermaidMindMap"),
                ],
            ),
        ],
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
        question_spec=[
            {'perspectives': ["Business Analyst", "Data Steward", "Solution Architect"],
             'questions': [
                 "List all data collections.",
                 "What type of collection is [name]?",
                 "What does [collection] contain?",
                 "What collections belong to [parent collection]?",
             ]},
        ],
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
        question_spec=[
            {'perspectives': ["Business Analyst", "Data Steward"],
             'questions': [
                 "What folders exist in [collection or catalog]?",
                 "What is in the [folder name] folder?",
                 "Show me folders for [topic or domain].",
             ]},
        ],
        formats=[Format(
            types=["ALL"],
            attributes=BASIC_COLLECTIONS_COLUMNS,
        )],  # Reusing common formats
        action=ActionParameter(
            function="CollectionManager.find_collections",
            required_params=["search_string"],
            optional_params=OPTIONAL_SEARCH_PARAMS,
            spec_params={"metadata_element_type": "FolderCollection"},
        )
    ),
    "BusinessCapabilities": FormatSet(
        target_type="BusinessCapability",
        heading="Common Business Capability Information",
        description="Attributes generic to all Business Capabilities.",
        aliases=[],
        annotations=COMMON_ANNOTATIONS,
        family="Digital Business",
        question_spec=[
            {'perspectives': ["Business Analyst"],
             'questions': [
                 "What business capabilities are defined?",
                 "What systems support [capability]?",
             ]},
            {'perspectives': ["Solution Architect"],
             'questions': [
                 "What business capabilities exist?",
                 "Which capabilities map to [process or system]?",
                 "What is the implementation approach for [capability]?",
             ]},
            {'perspectives': ["Governance Officer"],
             'questions': [
                 "What capabilities are in scope for [regulation]?",
             ]},
        ],
        formats=[Format(
            types=["ALL"],
            attributes=BASIC_COLLECTIONS_COLUMNS + [
                    Column(name='Business Capability Type', key='business_capability_type'),
                    Column(name='Business Implementation Type', key='business_implementation_type')
            ]
        )],  # Reusing common formats
        action=ActionParameter(
            function="CollectionManager.find_collections",
            required_params=["search_string"],
            optional_params=OPTIONAL_SEARCH_PARAMS,
            spec_params={"metadata_element_type": "BusinessCapability"},
        )
    ),

    "Collection Members": FormatSet(
        target_type="Collection",
        heading="Collection Membership Information",
        description="Attributes about all CollectionMembers.",
        aliases=["CollectionMember", "Member", "Members"],
        annotations={"wikilinks": ["[[CollectionMembers]]"]},
        family="External References",
        question_spec=[
            {'perspectives': ["Business Analyst", "Data Steward"],
             'questions': [
                 "What is in [collection]?",
                 "List the members of [collection].",
                 "What elements belong to [collection]?",
             ]},
        ],
        formats=[COLLECTION_DICT, COLLECTION_TABLE],
        action=ActionParameter(
            function="CollectionManager.get_collection_members",
            required_params=["collection_guid"],
            optional_params=OPTIONAL_FILTER_PARAMS + TIME_PARAMETERS,
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
        question_spec=[
            {'perspectives': ["Solution Architect"],
             'questions': [
                 "What solution blueprints exist?",
                 "Show me the blueprint for [solution].",
                 "What components make up [solution blueprint]?",
                 "Show me the architecture diagram for [solution].",
             ]},
            {'perspectives': ["Digital Product Manager"],
             'questions': [
                 "Which solution blueprint supports [data product]?",
                 "Show me the solution design for [product].",
             ]},
        ],
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
        question_spec=[
            {'perspectives': ["DevOps Engineer"],
             'questions': [
                 "What services are registered on the platform?",
                 "What is the URL marker for [service]?",
                 "What type is [service]?",
                 "What services are available for [capability]?",
             ]},
        ],
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
        question_spec=[
            {'perspectives': ["DevOps Engineer"],
             'questions': [
                 "What audit log severity levels are defined?",
                 "What does [severity code] mean?",
                 "What action should I take for [severity]?",
             ]},
        ],
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
        question_spec=[
            {'perspectives': ["Business Analyst"],
             'questions': [
                 "What types of data assets are catalogued?",
                 "What is a [type name]?",
             ]},
            {'perspectives': ["Data Engineer", "Solution Architect"],
             'questions': [
                 "What asset types does Egeria support?",
                 "Show me the hierarchy of asset types.",
                 "Which asset type should I use for [use case]?",
             ]},
        ],
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
        question_spec=[
            {'perspectives': ["Business Analyst"],
             'questions': [
                 "What data product catalogs exist?",
                 "Which catalog covers [domain or topic]?",
                 "What products are in the [catalog name] catalog?",
             ]},
            {'perspectives': ["Digital Product Manager"],
             'questions': [
                 "How many products are in each catalog?",
                 "When was [catalog] last updated?",
                 "Who created the [catalog] catalog?",
             ]},
            {'perspectives': ["Solution Architect"],
             'questions': [
                 "How are our product catalogs organized?",
                 "Which catalogs contain [collection type]?",
             ]},
        ],
        formats=[
            Format(
                types=["DICT", "TABLE", "LIST", "MD", "FORM","REPORT-GRAPH"],
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
            # spec_params={"metadata_element_subtypes": ["DigitalProductCatalog"],"_type":"DigitalProductCatalog"},
            spec__params={"metadata_element_type": "DigitalProductCatalog", "_type":"DigitalProductCatalog"}
        )
    ),
    "Digital-Product-Catalog-MyE": FormatSet(
        target_type="DigitalProductCatalog",
        heading="Catalogs for Digital Products",
        description="Attributes generic to all Digital Product Catalogs..",
        aliases=[],
        annotations={},
        family="Product Manager",
        question_spec=[
            {'perspectives': ["Digital Product Manager"],
             'questions': [
                 "What digital product catalogs exist?",
                 "What products are in [catalog]?",
                 "Which catalog contains [product]?",
             ]},
            {'perspectives': ["Business Analyst"],
             'questions': [
                 "Where can I browse data products?",
                 "What catalogs are available?",
             ]},
        ],
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
            # spec_params={"metadata_element_subtypes": ["DigitalProductCatalog"], "_type":"DigitalProductCatalog"},
            spec_params={"metadata_element_type": "DigitalProductCatalog","_type":"DigitalProductCatalog"}
        ),
    ),

    "Digital-Products": FormatSet(
        target_type="DigitalProduct",
        heading="Digital Product Information",
        description="Attributes useful to Digital Products.",
        aliases=["DigitalProduct", "DataProducts"],
        annotations={},
        family="Product Manager",
        question_spec=[
            {'perspectives': ["Business Analyst"],
             'questions': [
                 "What data products are available?",
                 "Show me active data products for [topic or domain].",
                 "What data does [product] include?",
                 "Who manages the [product] data product?",
                 "What license does [product] use?",
                 "Is [product] still supported?",
             ]},
            {'perspectives': ["Data Scientist"],
             'questions': [
                 "What datasets are available for analysis?",
                 "Show me mature data products for [domain].",
                 "What data products can I use for [use case]?",
             ]},
            {'perspectives': ["Digital Product Manager"],
             'questions': [
                 "Which products are nearing end of service life?",
                 "What products are due for a new version?",
                 "What is the withdrawal date for [product]?",
                 "Which products are still in development or draft?",
                 "What other products does [product] depend on?",
             ]},
            {'perspectives': ["Data Owner"],
             'questions': [
                 "What data products include my data assets?",
                 "Which products are built on [dataset]?",
             ]},
        ],
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
            spec_params={"metadata_element_subtypes": ["DigitalProduct"], "_type":"DigitalProduct"},
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
        question_spec=[
            {'perspectives': ["Digital Product Manager"],
             'questions': [
                 "What digital products are available?",
                 "What is the status of [product]?",
                 "Who manages [product]?",
                 "What data does [product] contain?",
             ]},
            {'perspectives': ["Business Analyst"],
             'questions': [
                 "Show me active data products.",
                 "What data products cover [topic]?",
             ]},
        ],
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
            spec_params={"_type": "DigitalProductProperties",
                         "metadata_element_subtypes": ["DigitalProduct"],
                         "metadata_element_type": "DigitalProduct",
                        },
        ),
        get_additional_props=ActionParameter(
            function="CollectionManager._extract_digital_product_properties",
            required_params=[],
            spec_params={},
        )
    ),
    "Digital-Products-Slim": FormatSet(
        target_type="DigitalProduct",
        heading="Digital Product Information",
        description="Attributes useful to Digital Products.",
        aliases=[],
        annotations={},
        family="Product Manager",
        question_spec=[
            {'perspectives': ["Business Analyst", "Digital Product Manager"],
             'questions': [
                 "Give me a quick list of data products.",
                 "What products are deployed?",
                 "Who is the contact for [product]?",
             ]},
        ],
        formats=[
            Format(
                types=["FORM", "TABLE", "LIST", "MD"],
                attributes=[
                    Column(name="Display Name", key='display_name'),
                    Column(name="Type Name", key='type_name'),
                    Column(name="Content Status", key='content_status'),
                    Column(name="Deployment Status", key='deployment_status'),
                    Column(name='Product Name', key='product_name'),
                    Column(name='Members', key='members', format=True),
                    # Column(name='Product Manager', key='assigned_actors'),
                    Column(name='Contacts', key='actor_list'),
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
            spec_params={"_type": "DigitalProductProperties",
                         "metadata_element_subtypes": ["DigitalProduct"],
                         "metadata_element_type": "DigitalProduct",
                         },
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
        question_spec=[
            {'perspectives': ["Business Analyst"],
             'questions': [
                 "What data sharing agreements are in place?",
                 "What agreements cover [dataset or domain]?",
                 "Is there an agreement that allows use of [data]?",
             ]},
            {'perspectives': ["Data Owner"],
             'questions': [
                 "What agreements cover my data assets?",
                 "What are the terms of the agreement with [party]?",
                 "What is the support level for [agreement]?",
             ]},
            {'perspectives': ["Governance Officer", "Data Steward"],
             'questions': [
                 "Which agreements are currently effective?",
                 "What service levels are defined in [agreement]?",
                 "Show me all data sharing agreements and their status.",
                 "What data sharing agreements involve external parties?",
             ]},
        ],
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
        question_spec=[
            {'perspectives': ["Business Analyst"],
             'questions': [
                 "Is there a dictionary that defines [term or field]?",
                 "Where can I find field definitions for [system or domain]?",
             ]},
            {'perspectives': ["Data Steward"],
             'questions': [
                 "What data dictionaries exist?",
                 "Which dictionary covers [domain]?",
                 "Is there a data dictionary for [system]?",
             ]},
            {'perspectives': ["Data Engineer"],
             'questions': [
                 "Show me the data dictionary for [dataset].",
                 "What dictionaries contain [field name]?",
             ]},
        ],
        formats=[COMMON_FORMATS_ALL],  # Reusing common formats and columns
        action=ActionParameter(
            function="CollectionManager.find_collections",
            required_params=["search_string"],
            spec_params={"metadata_element_type": "DataDictionary"},
        )
    ),

    "Data-Specifications": FormatSet(
        target_type="Data Specification",
        heading="Data Specification Information",
        description="Attributes about Data Specification.",
        aliases=["Data Spec", "DataSpec", "DataSpecification"],
        annotations={"wikilinks": ["[[Data Specification]]"]},
        family="Data Designer",
        question_spec=[
            {'perspectives': ["Solution Architect"],
             'questions': [
                 "What data specifications have been defined?",
                 "Show me the specification for [system or product].",
                 "Show me a visual of [data specification].",
             ]},
            {'perspectives': ["Data Engineer"],
             'questions': [
                 "What data specifications cover [integration or system]?",
             ]},
            {'perspectives': ["Data Steward"],
             'questions': [
                 "Which data specifications are approved for [domain]?",
             ]},
        ],
        formats=[
            Format(types=["REPORT", "HTML"],
                   attributes=COMMON_COLUMNS + [Column(name="Mermaid", key='mermaidGraph'), ]),
            Format(types=["MERMAID"], attributes=[
                Column(name="Display Name", key='display_name'),
                Column(name="Mermaid", key='mermaidGraph'),
            ]),
            Format(types=["ALL"], attributes=COMMON_COLUMNS)],  # Reusing common formats and columns
        action=ActionParameter(
            function="CollectionManager.find_collections",
            required_params=["search_string"],
            spec_params={"metadata_element_subtypes": ["DataSpec"]},
        )
    ),

    "Data-Structures": FormatSet(
        target_type="Data Structure",
        heading="Data Structure Information",
        description="Attributes about Data Structures.",
        aliases=["Data Structure", "DataStructures", "Data Structures", "Data Struct", "DataStructure"],
        annotations={"wikilinks": ["[[Data Structure]]"]},
        family="Data Designer",
        question_spec=[
            {'perspectives': ["Business Analyst"],
             'questions': [
                 "What information is captured in [structure]?",
                 "What fields make up [structure]?",
             ]},
            {'perspectives': ["Data Engineer"],
             'questions': [
                 "What data structures are defined for [system]?",
                 "Show me the fields in [structure].",
                 "Which data structures are used in [specification]?",
             ]},
            {'perspectives': ["Data Scientist"],
             'questions': [
                 "What is the structure of [dataset]?",
                 "What fields does [structure] contain?",
             ]},
            {'perspectives': ["Data Steward"],
             'questions': [
                 "Which data structures are in the [dictionary]?",
                 "Which structures belong to [data specification]?",
             ]},
        ],
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
        question_spec=[
            {'perspectives': ["Business Analyst"],
             'questions': [
                 "What information is captured in [structure]?",
                 "What does the [field] field contain?",
             ]},
            {'perspectives': ["Data Engineer"],
             'questions': [
                 "What fields are in [structure]?",
                 "Find all fields named [name] across structures.",
                 "What data type is [field]?",
             ]},
            {'perspectives': ["Data Scientist"],
             'questions': [
                 "What fields are available in [dataset]?",
                 "Which structure contains [field]?",
             ]},
            {'perspectives': ["Data Steward"],
             'questions': [
                 "Which fields are in [data dictionary]?",
                 "Show me fields missing descriptions in [dictionary].",
             ]},
        ],
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
        question_spec=[
            {'perspectives': ["Data Steward"],
             'questions': [
                 "What data classes are defined?",
                 "What is the [class name] data class?",
                 "Which classes specialize [parent class]?",
                 "Which data classes are in [dictionary]?",
             ]},
            {'perspectives': ["Data Engineer"],
             'questions': [
                 "What data type does [class] represent?",
                 "Show me the specification for [class].",
             ]},
            {'perspectives': ["Solution Architect"],
             'questions': [
                 "Show me the hierarchy of data classes.",
                 "What specification does [class] use?",
             ]},
        ],
        formats=[Format(types=["MD", "FORM", "DICT", "LIST","TABLE"], attributes=COMMON_COLUMNS + [
            Column(name="Data Type", key='data_type'),
            Column(name="Specification", key='specification'),
            Column(name="In Data Dictionaries", key='in_data_dictionary'),
            Column(name="In Data Structure", key='in_data_structure')]),
                 Format(types=["REPORT"], attributes=COMMON_COLUMNS +
                                                     [
                                                         Column(name="Data Type", key='data_type'),
                                                         Column(name="Specification", key='specification'),
                                                         Column(name="In Data Dictionaries", key='in_data_dictionary'),
                                                         Column(name="Containing Data Class",
                                                                key='containing_data_class'),
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
"Data-Value-Spec": FormatSet(
        target_type="Data Value Specification",
        heading="Data Value Specification Information",
        description="Attributes about Data Value Specifications",
        aliases=["Data Value Spec"],
        annotations={"wikilinks": ["[[Data Value Specification]]"]},
        family="Data Designer",
        question_spec=[
            {'perspectives': ["Data Steward"],
             'questions': [
                 "What data value specifications are defined?",
                 "What is the [spec name] data value specification?",
                 "Which data value specs are in [dictionary]?",
                 "What namespace does [spec] belong to?",
             ]},
            {'perspectives': ["Data Engineer"],
             'questions': [
                 "What data type does [spec] define?",
                 "What is the specification detail for [spec]?",
                 "What units does [spec] use?",
             ]},
            {'perspectives': ["Solution Architect"],
             'questions': [
                 "Show me the hierarchy of data value specifications.",
                 "Which spec specializes [parent spec]?",
             ]},
        ],
        formats=[Format(types=["MD", "FORM", "DICT", "LIST","TABLE"], attributes=COMMON_COLUMNS + [
            Column(name="Data Type", key='data_type'),
            Column(name="Specification", key='specification'),
            Column(name="In Data Dictionaries", key='in_data_dictionary'),
            Column(name="Units", key='units'),
            Column(name="Namespace Path", key='namespace_path'),
        ]),
             Format(types=["REPORT"], attributes=COMMON_COLUMNS +
                 [
                     Column(name="Data Type", key='data_type'),
                     Column(name="Specification", key='specification'),
                     Column(name="In Data Dictionaries", key='in_data_dictionary'),
                     Column(name="Containing Data Class",  key='containing_data_class'),
                     Column(name="Specializes", key='specializes_data_class'),
                     Column(name="Mermaid", key='mermaidGraph')
                 ]
            )],

        action=ActionParameter(
            function="DataDesigner.find_data_value_specifications",
            required_params=["search_string"],
            optional_params=OPTIONAL_SEARCH_PARAMS,
            spec_params={},
        )
    ),
    'External-References': FormatSet(target_type='External-Reference',
                                     heading='External-Reference Attributes',
                                     description='External References',
                                     family="External References",
                                     question_spec=[
                                         {'perspectives': ["Researcher", "Business Analyst"],
                                          'questions': [
                                              "What external references are catalogued?",
                                              "Find references about [topic or standard]?",
                                              "Who published [reference]?",
                                              "What is the URL for [reference]?",
                                          ]},
                                         {'perspectives': ["Data Steward"],
                                          'questions': [
                                              "What external sources are linked to [element]?",
                                              "Show me references categorised as [category].",
                                          ]},
                                     ],
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

                                         Format(types=["MERMAID"],
                                                attributes=[Column(name='Mermaid', key='mermaidGraph')]),
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
        question_spec=[
            {'perspectives': ["Governance Officer"],
             'questions': [
                 "List all governance definitions.",
                 "What governance definitions exist in [domain]?",
                 "What type is [definition]?",
             ]},
            {'perspectives': ["Data Steward"],
             'questions': [
                 "What governance definition covers [subject]?",
                 "Give me a summary of [definition].",
             ]},
        ],
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
        question_spec=[
            {'perspectives': ["Governance Officer"],
             'questions': [
                 "What governance definitions are in place?",
                 "Show me all definitions in the [data / privacy / security] domain.",
                 "What is the scope of [definition]?",
                 "What are the implications of [definition]?",
                 "Which definitions are approved and active?",
             ]},
            {'perspectives': ["Data Steward"],
             'questions': [
                 "What governance definition applies to [subject]?",
                 "What is the usage guidance for [definition]?",
             ]},
            {'perspectives': ["Solution Architect"],
             'questions': [
                 "Which governance definitions affect [system or data product]?",
                 "What is the importance rating of [definition]?",
             ]},
        ],
        formats=[Format(types=["ALL"], attributes=GOVERNANCE_DEFINITIONS_COLUMNS)],
        action=ActionParameter(
            function="GovernanceOfficer.find_governance_definitions",
            required_params=["search_string"],
            optional_params=OPTIONAL_SEARCH_PARAMS,
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
        question_spec=[
            {'perspectives': ["Governance Officer"],
             'questions': [
                 "What governance principles are defined?",
                 "What strategies have been documented?",
                 "What governance responses are in place?",
                 "List the principles in [domain].",
             ]},
            {'perspectives': ["Data Steward"],
             'questions': [
                 "What principle applies to [subject]?",
                 "What is the summary for [principle or strategy]?",
             ]},
        ],
        formats=[Format(types=["ALL"], attributes=GOVERNANCE_DEFINITIONS_BASIC)],
        action=ActionParameter(
            function="GovernanceOfficer.find_governance_definitions",
            required_params=["search_string"],
            spec_params={
                "metadata_element_subtypes": ["GovernancePrinciple", "GovernanceStrategy", "GovernanceResponse"]},
        )
    ),
    'Governance-Controls': FormatSet(target_type='Governance Control',
                                     heading='Control Attributes',
                                     description='Governance Control (Create).',
                                     family="Governance Officer",
                                     question_spec=[
                                         {'perspectives': ["Governance Officer"],
                                          'questions': [
                                              "What governance controls have been defined?",
                                              "What measurements and targets are defined for governance controls?",
                                              "What are the implications of the governance controls?",
                                              "What risks are associated with the governance controls?",
                                              "Show me controls in [domain].",
                                          ]},
                                         {'perspectives': ["Data Steward"],
                                          'questions': [
                                              "What controls apply to [data or process]?",
                                              "What is the scope of [control]?",
                                          ]},
                                     ],
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
    'Governance-Zones': FormatSet(target_type='Governance Zone',
                                     heading='Governance Zones',
                                     description='Descriptions of Governance Zones',
                                     family="Governance Officer",
                                     question_spec=[
                                         {'perspectives': ["Business Analyst"],
                                          'questions': [
                                              "What data zones exist?",
                                              "Which zone is [data] in?",
                                              "What does it mean to be in the [zone] zone?",
                                          ]},
                                         {'perspectives': ["Data Owner"],
                                          'questions': [
                                              "Which governance zone is my data in?",
                                              "What restrictions apply to data in [zone]?",
                                          ]},
                                         {'perspectives': ["Data Steward"],
                                          'questions': [
                                              "What data is in the [zone] zone?",
                                              "How many items are in each governance zone?",
                                              "What is the scope of the [zone] zone?",
                                          ]},
                                         {'perspectives': ["Governance Officer"],
                                          'questions': [
                                              "What governance zones have been defined?",
                                              "Which zones have the most data?",
                                              "What are the compliance requirements for [zone]?",
                                          ]},
                                     ],
                                     formats=[
                                         Format(types=['DICT', 'MD', 'FORM'],
                                                attributes=[Column(name='Display Name', key='display_name'),
                                                            Column(name='Summary', key='summary'),
                                                            Column(name='Description', key='description'),
                                                            Column(name='Category', key='category'),
                                                            Column(name='Domain Identifier', key='domain_identifier'),
                                                            Column(name='Identifier', key='identifier'),
                                                            Column(name='Version Identifier', key='version_identifier'),
                                                            Column(name='Usage', key='usage'),
                                                            Column(name='Scope', key='scope'),
                                                            Column(name='Total Zone Membership', key='total_membership'),
                                                            Column(name='Zone Membership Types', key='type_membership'),
                                                            Column(name='Asset Type Breakdown (Bar)', key='typeMembershipBarGraph'),
                                                            Column(name='Asset Type Breakdown (Pie)', key='typeMembershipPieGraph'),
                                                            Column(name='Anchored Total Membership', key='anchored_total_membership'),
                                                            Column(name='Anchored Type Membership', key='anchored_type_membership'),
                                                            Column(name='All Total Membership', key='all_total_membership'),
                                                            Column(name='all Type Membership', key='all_type_membership'),
                                                            Column(name='Analysis Time', key='analysis_time'),
                                                            Column(name='Qualified Name', key='qualified_name'),
                                                            Column(name='GUID', key='guid')
                                                            ]),
                                         Format(types=['REPORT', 'GRAPH'],
                                                attributes=[Column(name='Display Name', key='display_name'),
                                                            Column(name='Summary', key='summary'),
                                                            Column(name='Description', key='description'),
                                                            Column(name='Category', key='category'),
                                                            Column(name='Domain Identifier', key='domain_identifier'),
                                                            Column(name='Identifier', key='identifier'),
                                                            Column(name='Version Identifier', key='version_identifier'),
                                                            Column(name='Usage', key='usage'),
                                                            Column(name='Scope', key='scope'),
                                                            Column(name='Total Zone Membership', key='total_membership'),
                                                            Column(name='Zone Membership Types', key='type_membership'),
                                                            Column(name='Asset Type Breakdown (Bar)', key='typeMembershipBarGraph'),
                                                            Column(name='Asset Type Breakdown (Pie)', key='typeMembershipPieGraph'),
                                                            Column(name='Anchored Total Membership', key='anchored_total_membership'),
                                                            Column(name='Anchored Type Membership', key='anchored_type_membership'),
                                                            Column(name='All Total Membership', key='all_total_membership'),
                                                            Column(name='all Type Membership', key='all_type_membership'),
                                                            Column(name='Analysis Time', key='analysis_time'),
                                                            Column(name='Qualified Name', key='qualified_name'),
                                                            Column(name='GUID', key='guid')
                                                            ]),
                                         Format(types=['TABLE', 'LIST'],
                                                attributes=[Column(name='Display Name', key='display_name'),
                                                            Column(name='Summary', key='summary'),
                                                            Column(name='Category', key='category'),
                                                            Column(name='Identifier', key='identifier'),
                                                            Column(name='Total Zone Membership', key='total_membership'),
                                                            Column(name='Zone Memebership Types', key='type_membership'),
                                                            Column(name='Qualified Name', key='qualified_name'),
                                                            ])
                                     ],
                                     action=ActionParameter(
                                         function="GovernanceOfficer.find_governance_definitions",
                                         required_params=["search_string"],
                                         optional_params=OPTIONAL_SEARCH_PARAMS,
                                         spec_params={"metadata_element_subtypes": ["GovernanceZone"]},
                                     )
                                     ),
    'Governance-Process': FormatSet(target_type='Governance Process',
                                    heading='Governance Process Attributes',
                                    description='Governance Process Attributes.',
                                    family="Governance Officer",
                                    question_spec=[
                                        {'perspectives': ["Governance Officer"],
                                         'questions': [
                                             "What governance processes are defined?",
                                             "Show me processes in [category or domain].",
                                             "What is the [process name] process?",
                                         ]},
                                        {'perspectives': ["Data Steward"],
                                         'questions': [
                                             "What governance processes apply to [data]?",
                                         ]},
                                    ],
                                    formats=[
                                        Format(types=['TABLE', 'LIST', 'MD', 'FORM', 'REPORT'],
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
    'Governance-Zone-Overview-Charts': FormatSet(target_type='Governance Zone',
                                    heading='Governance Zone Charts',
                                    description='Governance Zone Overview',
                                    family="Governance Officer",
                                    question_spec=[
                                        {'perspectives': ["Governance Officer"],
                                         'questions': [
                                             "Show me the governance zone membership overview.",
                                             "What is the distribution of data across governance zones?",
                                             "Which zones have the most anchored items?",
                                         ]},
                                        {'perspectives': ["Data Steward"],
                                         'questions': [
                                             "Give me a visual summary of zone memberships.",
                                             "Show me zone profile charts.",
                                         ]},
                                    ],
                                    formats=[
                                        Format(types=['MERMAID', 'REPORT', 'DICT'],
                                               attributes=[Column(name='Mermaid Graph', key='mermaidGraph'),
                                                           Column(name='Zone Profiles', key='zoneProfileMermaidPieChart'),
                                                           Column(name='Zone Profile Anchored', key='zoneProfileAnchoredMermaidPieChart'),
                                                           Column(name='Zone Profile All', key='zoneProfileAllMermaidPieChart')
                                                           ])
                                    ],
                                    action=ActionParameter(
                                        function="GovernanceOfficer.find_governance_definitions",
                                        required_params=["search_string"],
                                        optional_params=OPTIONAL_SEARCH_PARAMS,
                                        spec_params={"metadata_element_subtypes": ["GovernanceZone"]},
                                    )
                                    ),
    'Secrets-Collection-User-Profile-Charts': FormatSet(target_type='SecretsCollection',
                                                 heading='Secrets Collection User Profile Charts',
                                                 description='Secrets Collection User Profile',
                                                 family="Governance Officer",
                                                 question_spec=[
                                                     {'perspectives': ["Security Officer", "Governance Officer"],
                                                      'questions': [
                                                          "Show me the user account profile for [secrets collection].",
                                                          "What account types are used in [collection]?",
                                                          "What is the account status distribution?",
                                                      ]},
                                                 ],
                                                 formats=[
                                                     Format(types=['MERMAID', 'REPORT', 'DICT'],
                                                            attributes=[
                                                                Column(name='Mermaid Graph', key='mermaidGraph'),
                                                                Column(name='Account Type Profile',
                                                                       key='userAccountTypeProfileMermaidPieChart'),
                                                                Column(name='Account Status Profile',
                                                                       key='userAccountStatusProfileMermaidPieChart'),
                                                                ])
                                                 ],
                                                 action=ActionParameter(
                                                     function="GovernanceOfficer.find_governance_definitions",
                                                     required_params=["search_string"],
                                                     optional_params=OPTIONAL_SEARCH_PARAMS,
                                                     spec_params={"metadata_element_subtypes": ["GovernanceZone"]},
                                                 )
                                                 ),
    "Valid-Value-Def": FormatSet(
        target_type="Valid Value Definition",
        heading="Valid Value Definitions Information",
        description="Attributes useful to Business Reference Data (Valid Value Definitions).",
        aliases=[],
        annotations={"wikilinks": ["[[VV-Def]]"]},
        family="General",
        question_spec=[
            {'perspectives': ["Data Steward"],
             'questions': [
                 "What valid value definitions are defined?",
                 "What is the preferred value for [concept]?",
                 "What data type does [valid value] use?",
                 "What is the scope of [valid value definition]?",
             ]},
            {'perspectives': ["Data Engineer"],
             'questions': [
                 "How should I encode [concept] in my data?",
                 "What valid values exist for [property name]?",
             ]},
            {'perspectives': ["Governance Officer"],
             'questions': [
                 "What are the approved reference values for [domain]?",
                 "Show me valid value definitions in [scope].",
             ]},
        ],
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
                              question_spec=[
                                  {'perspectives': ["Business Analyst", "Data Scientist"],
                                   'questions': [
                                       "What license does [data product or dataset] use?",
                                       "What are the restrictions on using [data]?",
                                       "What licenses allow commercial use?",
                                   ]},
                                  {'perspectives': ["Governance Officer", "Data Steward"],
                                   'questions': [
                                       "What license types are defined?",
                                       "What are the obligations under [license]?",
                                       "What data is covered by [license type]?",
                                       "Show me licenses in [domain].",
                                   ]},
                              ],
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
        question_spec=[
            {'perspectives': ["Governance Officer"],
             'questions': [
                 "What governance policies are in place?",
                 "Show me policies in the [data / privacy / security] domain.",
                 "What is the scope of [policy]?",
                 "What are the implications of [policy]?",
                 "Which policies are active and approved?",
             ]},
            {'perspectives': ["Data Steward"],
             'questions': [
                 "What policy applies to [data or subject]?",
                 "What is the usage guidance for [policy]?",
                 "What is the importance of [policy]?",
             ]},
            {'perspectives': ["Solution Architect"],
             'questions': [
                 "Which policies affect [system or data product]?",
                 "What outcomes are expected from [policy]?",
             ]},
        ],
        formats=[Format(types=["ALL"], attributes=GOVERNANCE_DEFINITIONS_COLUMNS)],
        action=ActionParameter(
            function="GovernanceOfficer.find_governance_definitions",
            required_params=["search_string"],
            optional_params=OPTIONAL_SEARCH_PARAMS,
            spec_params={"metadata_element_type": "GovernancePolicy"},
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
        msg = f"No matching column set found for kind='{kind}' and output type_name = '{output_type}'."
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
    logger.error(f"No matching format found for kind='{kind}' with output type_name = '{output_type}'.")
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
                report_specs.upsert(key, value)
            logger.info(f"Format sets from {file_path} merged with existing format sets (upsert)")
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
    if output_type is None:
        reason = "Invalid Parameter - output_type is None"
        logger.error(reason)
        raise PyegeriaInvalidParameterException(context={"reason": reason})

    output_type = output_type.upper()
    element: Optional[FormatSet] = registry.get(kind)
    if element is None:
        # try aliases
        for value in registry.values():
            if kind in value.aliases:
                element = value
                break
    if element is None:
        logger.debug(f"No matching report format found for kind='{kind}' and output type_name = '{output_type}'.")
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

    # Fallback for TABLE -> DICT
    if output_type == "TABLE":
        for fmt in element.formats:
            if "DICT" in fmt.types:
                output_struct["formats"] = fmt.dict()
                return output_struct

    for fmt in element.formats:
        if "ALL" in fmt.types:
            output_struct["formats"] = fmt.dict()
            return output_struct
    logger.debug(f"No matching format found for kind='{kind}' with output type_name = '{output_type}'.")
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
