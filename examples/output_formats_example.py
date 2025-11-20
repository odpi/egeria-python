#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Example script demonstrating how to use the Pydantic models for output report specs.

This script shows how to:
1. Create custom columns, formats, and report specs
2. Compose formats by reusing columns
3. Add a custom report spec to the report_specs dictionary
4. Use the functions in _output_formats.py with the new models
"""

import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyegeria._output_format_models import Column, Format, ActionParameter, FormatSet
from pyegeria.base_report_formats import (
    report_specs,
    select_report_spec,
    report_spec_list,
    get_report_spec_heading,
    get_report_spec_description,
    get_report_spec_match,
)

def create_custom_report_spec():
    """
    Create a custom format set with multiple formats.
    
    This demonstrates how to create columns, formats, and format sets,
    and how to compose formats by reusing columns.
    """
    print("\n=== Creating a custom report spec ===")
    
    # Create common columns that will be used in multiple formats
    common_columns = [
        Column(name="ID", key="id"),
        Column(name="Name", key="name"),
        Column(name="Description", key="description", format=True),
    ]
    
    # Create additional columns for specific formats
    detail_columns = [
        Column(name="Created By", key="created_by"),
        Column(name="Created Date", key="created_date"),
        Column(name="Modified By", key="modified_by"),
        Column(name="Modified Date", key="modified_date"),
    ]
    
    technical_columns = [
        Column(name="Type", key="type"),
        Column(name="Status", key="status"),
        Column(name="Version", key="version"),
    ]
    
    # Create formats that reuse and compose columns
    table_format = Format(
        types=["TABLE"],
        columns=common_columns,  # Basic columns for table view
    )
    
    detail_format = Format(
        types=["DETAIL", "FORM"],
        columns=common_columns + detail_columns,  # Common columns plus detail columns
    )
    
    technical_format = Format(
        types=["TECHNICAL", "DICT"],
        columns=common_columns + technical_columns,  # Common columns plus technical columns
    )
    
    full_format = Format(
        types=["FULL", "REPORT"],
        columns=common_columns + detail_columns + technical_columns,  # All columns
    )
    
    # Create a report spec (format set) that includes all the formats
    custom_format_set = FormatSet(
        heading="Custom Example Format Set",
        description="A custom format set demonstrating composition of formats",
        aliases=["CustomExample", "Example"],
        annotations={"wikilinks": ["[[Example]]", "[[Custom]]"]},
        formats=[table_format, detail_format, technical_format, full_format],
        action=[
            ActionParameter(
                function="ExampleManager.find_examples",
                required_params=["search_string"],
                spec_params={},
            )
        ],
    )
    
    # Print information about the report spec
    print(f"Created report spec: {custom_format_set.heading}")
    print(f"Description: {custom_format_set.description}")
    print(f"Aliases: {custom_format_set.aliases}")
    print(f"Number of formats: {len(custom_format_set.formats)}")
    
    # Print information about each format
    for i, format in enumerate(custom_format_set.formats):
        print(f"\nFormat {i+1}:")
        print(f"  Types: {format.types}")
        print(f"  Number of columns: {len(format.columns)}")
        print(f"  Columns: {[column.name for column in format.columns]}")
    
    return custom_format_set

def add_report_spec_to_dictionary(format_set):
    """
    Add a report spec to the report_specs dictionary.
    
    This demonstrates how to add a custom report spec to the
    report_specs dictionary for use with the functions
    in _output_formats.py.
    """
    print("\n=== Adding report spec to dictionary ===")
    
    # Add the report spec to the report_specs dictionary
    report_specs["CustomExample"] = format_set
    
    # Verify that the report spec was added
    format_sets = report_spec_list()
    if "CustomExample" in format_sets:
        print("Report spec successfully added to the dictionary!")
        print(f"Available report specs: {format_sets}")
    else:
        print("Failed to add report spec to the dictionary.")

def use_output_format_functions():
    """
    Use the functions in _output_formats.py with the new models.
    
    This demonstrates how to use the functions in _output_formats.py
    with the new Pydantic models.
    """
    print("\n=== Using output format functions ===")
    
    # Get a report spec by name
    format_set = select_report_spec("CustomExample", "TABLE")
    if format_set:
        print("Successfully retrieved report spec by name!")
        print(f"Heading: {format_set['heading']}")
        print(f"Description: {format_set['description']}")
    else:
        print("Failed to retrieve report spec by name.")
    
    # Get a report spec by alias
    format_set = select_report_spec("Example", "TABLE")
    if format_set:
        print("\nSuccessfully retrieved report spec by alias!")
        print(f"Heading: {format_set['heading']}")
        print(f"Description: {format_set['description']}")
    else:
        print("\nFailed to retrieve report spec by alias.")
    
    # Get the heading and description of a report spec
    heading = get_report_spec_heading("CustomExample")
    description = get_report_spec_description("CustomExample")
    print(f"\nHeading: {heading}")
    print(f"Description: {description}")
    
    # Match a report spec with a specific output type
    format_set = select_report_spec("CustomExample", "ANY")
    matched_format_set = get_report_spec_match(format_set, "DETAIL")
    if matched_format_set and "formats" in matched_format_set:
        print("\nSuccessfully matched report spec with output type!")
        print(f"Output type: {matched_format_set['formats']['types']}")
        print(f"Number of columns: {len(matched_format_set['formats']['columns'])}")
    else:
        print("\nFailed to match report spec with output type.")

def main():
    """Run the example script."""
    print("=== Output Formats Example ===")
    
    # Create a custom report spec
    custom_format_set = create_custom_report_spec()
    
    # Add the report spec to the report_specs dictionary
    add_report_spec_to_dictionary(custom_format_set)
    
    # Use the functions in _output_formats.py with the new models
    use_output_format_functions()
    
    print("\n=== Example Complete ===")

if __name__ == "__main__":
    main()