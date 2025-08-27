#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Example script demonstrating how to use the Pydantic models for output formats.

This script shows how to:
1. Create custom columns, formats, and format sets
2. Compose formats by reusing columns
3. Add a custom format set to the output_format_sets dictionary
4. Use the functions in _output_formats.py with the new models
"""

import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyegeria._output_format_models import Column, Format, ActionParameter, FormatSet
from pyegeria._output_formats import (
    output_format_sets,
    select_output_format_set,
    output_format_set_list,
    get_output_format_set_heading,
    get_output_format_set_description,
    get_output_format_type_match,
)

def create_custom_format_set():
    """
    Create a custom format set with multiple formats.
    
    This demonstrates how to create columns, formats, and format sets,
    and how to compose formats by reusing columns.
    """
    print("\n=== Creating a custom format set ===")
    
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
    
    # Create a format set that includes all the formats
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
    
    # Print information about the format set
    print(f"Created format set: {custom_format_set.heading}")
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

def add_format_set_to_dictionary(format_set):
    """
    Add a format set to the output_format_sets dictionary.
    
    This demonstrates how to add a custom format set to the
    output_format_sets dictionary for use with the functions
    in _output_formats.py.
    """
    print("\n=== Adding format set to dictionary ===")
    
    # Add the format set to the output_format_sets dictionary
    output_format_sets["CustomExample"] = format_set
    
    # Verify that the format set was added
    format_sets = output_format_set_list()
    if "CustomExample" in format_sets:
        print("Format set successfully added to the dictionary!")
        print(f"Available format sets: {format_sets}")
    else:
        print("Failed to add format set to the dictionary.")

def use_output_format_functions():
    """
    Use the functions in _output_formats.py with the new models.
    
    This demonstrates how to use the functions in _output_formats.py
    with the new Pydantic models.
    """
    print("\n=== Using output format functions ===")
    
    # Get a format set by name
    format_set = select_output_format_set("CustomExample", "TABLE")
    if format_set:
        print("Successfully retrieved format set by name!")
        print(f"Heading: {format_set['heading']}")
        print(f"Description: {format_set['description']}")
    else:
        print("Failed to retrieve format set by name.")
    
    # Get a format set by alias
    format_set = select_output_format_set("Example", "TABLE")
    if format_set:
        print("\nSuccessfully retrieved format set by alias!")
        print(f"Heading: {format_set['heading']}")
        print(f"Description: {format_set['description']}")
    else:
        print("\nFailed to retrieve format set by alias.")
    
    # Get the heading and description of a format set
    heading = get_output_format_set_heading("CustomExample")
    description = get_output_format_set_description("CustomExample")
    print(f"\nHeading: {heading}")
    print(f"Description: {description}")
    
    # Match a format set with a specific output type
    format_set = select_output_format_set("CustomExample", "ANY")
    matched_format_set = get_output_format_type_match(format_set, "DETAIL")
    if matched_format_set and "formats" in matched_format_set:
        print("\nSuccessfully matched format set with output type!")
        print(f"Output type: {matched_format_set['formats']['types']}")
        print(f"Number of columns: {len(matched_format_set['formats']['columns'])}")
    else:
        print("\nFailed to match format set with output type.")

def main():
    """Run the example script."""
    print("=== Output Formats Example ===")
    
    # Create a custom format set
    custom_format_set = create_custom_format_set()
    
    # Add the format set to the output_format_sets dictionary
    add_format_set_to_dictionary(custom_format_set)
    
    # Use the functions in _output_formats.py with the new models
    use_output_format_functions()
    
    print("\n=== Example Complete ===")

if __name__ == "__main__":
    main()