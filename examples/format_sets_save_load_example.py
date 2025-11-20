#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Example script demonstrating how to save and load report specs (formerly called format sets).

This script shows how to:
1. Create custom report specs
2. Save report specs to a file
3. Load report specs from a file
4. Use the loaded report specs
5. Work with the user report specs directory
"""

import sys
import os
import json
from pathlib import Path

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyegeria._output_format_models import Column, Format, ActionParameter, FormatSet, FormatSetDict
from pyegeria.base_report_formats import (
    report_specs,
    save_report_specs,
    load_report_specs,
    USER_FORMAT_SETS_DIR,
    select_report_spec,
)

def create_custom_format_sets():
    """
    Create custom report specs for the example.
    
    Returns:
        FormatSetDict: A dictionary of custom format sets
    """
    print("\n=== Creating Custom Report Specs ===")
    
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
    
    # Create format sets that include the formats
    product_format_set = FormatSet(
        heading="Product Format Set",
        description="A format set for product information",
        aliases=["Product", "Products"],
        formats=[table_format, detail_format, technical_format],
        action=[
            ActionParameter(
                function="ProductManager.find_products",
                required_params=["search_string"],
                spec_params={},
            )
        ],
    )
    
    customer_format_set = FormatSet(
        heading="Customer Format Set",
        description="A format set for customer information",
        aliases=["Customer", "Customers"],
        formats=[table_format, detail_format, full_format],
        action=[
            ActionParameter(
                function="CustomerManager.find_customers",
                required_params=["search_string"],
                spec_params={},
            )
        ],
    )
    
    # Create a FormatSetDict with the custom format sets
    custom_format_sets = FormatSetDict({
        "Product": product_format_set,
        "Customer": customer_format_set,
    })
    
    print(f"Created {len(custom_format_sets)} custom format sets:")
    for name, format_set in custom_format_sets.items():
        print(f"  - {name}: {format_set.heading}")
        print(f"    Description: {format_set.description}")
        print(f"    Aliases: {format_set.aliases}")
        print(f"    Number of formats: {len(format_set.formats)}")
    
    return custom_format_sets

def save_format_sets_example(custom_format_sets):
    """
    Example of saving report specs to a file.
    
    Args:
        custom_format_sets: The custom report specs to save
    
    Returns:
        str: The path to the saved file
    """
    print("\n=== Saving Report Specs ===")
    
    # Create a directory for the example files
    example_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "format_sets")
    os.makedirs(example_dir, exist_ok=True)
    
    # Save all format sets to a file
    all_format_sets_path = os.path.join(example_dir, "all_format_sets.json")
    save_report_specs(all_format_sets_path)
    print(f"Saved all report specs to {all_format_sets_path}")
    
    # Save only the custom format sets to a file
    custom_format_sets_path = os.path.join(example_dir, "custom_format_sets.json")
    custom_format_sets.save_to_json(custom_format_sets_path)
    print(f"Saved custom report specs to {custom_format_sets_path}")
    
    # Save a subset of the predefined format sets to a file
    subset_format_sets_path = os.path.join(example_dir, "subset_format_sets.json")
    save_report_specs(subset_format_sets_path, format_set_names=["Collections", "DataDictionary"])
    print(f"Saved subset of report specs to {subset_format_sets_path}")
    
    return custom_format_sets_path

def load_format_sets_example(file_path):
    """
    Example of loading report specs from a file.
    
    Args:
        file_path: The path to the file to load
    
    Returns:
        FormatSetDict: The loaded report specs
    """
    print("\n=== Loading Report Specs ===")
    
    # Create a new FormatSetDict to load the report specs into
    loaded_format_sets = FormatSetDict()
    
    # Load the report specs from the file
    try:
        loaded_format_sets = FormatSetDict.load_from_json(file_path)
        print(f"Loaded {len(loaded_format_sets)} report specs from {file_path}")
        
        # Print information about the loaded report specs
        for name, format_set in loaded_format_sets.items():
            print(f"  - {name}: {format_set.heading}")
            print(f"    Description: {format_set.description}")
            print(f"    Aliases: {format_set.aliases}")
            print(f"    Number of formats: {len(format_set.formats)}")
        
        return loaded_format_sets
    except Exception as e:
        print(f"Error loading report specs from {file_path}: {e}")
        return None

def use_loaded_format_sets(loaded_format_sets):
    """
    Example of using loaded report specs.
    
    Args:
        loaded_format_sets: The loaded report specs to use
    """
    print("\n=== Using Loaded Report Specs ===")
    
    # Add the loaded format sets to the global report_specs
    for name, format_set in loaded_format_sets.items():
        report_specs[name] = format_set
    
    # Use the select_report_spec function to get a report spec by name
    product_format_set = select_report_spec("Product", "TABLE")
    if product_format_set:
        print(f"Found report spec for 'Product' with output type 'TABLE'")
        print(f"  Heading: {product_format_set['heading']}")
        print(f"  Description: {product_format_set['description']}")
        print(f"  Number of columns: {len(product_format_set['formats']['columns'])}")
    else:
        print("Format set for 'Product' not found")
    
    # Use the select_report_spec function to get a report spec by alias
    customer_format_set = select_report_spec("Customers", "DETAIL")
    if customer_format_set:
        print(f"Found report spec for 'Customers' with output type 'DETAIL'")
        print(f"  Heading: {customer_format_set['heading']}")
        print(f"  Description: {customer_format_set['description']}")
        print(f"  Number of columns: {len(customer_format_set['formats']['columns'])}")
    else:
        print("Format set for 'Customers' not found")

def user_format_sets_directory_example(custom_format_sets):
    """
    Example of working with the user report specs directory.
    
    Args:
        custom_format_sets: The custom report specs to save to the user directory
    """
    print("\n=== Working with User Report Specs Directory ===")
    
    # Create the user report specs directory if it doesn't exist
    os.makedirs(USER_FORMAT_SETS_DIR, exist_ok=True)
    print(f"User report specs directory: {USER_FORMAT_SETS_DIR}")
    
    # Save a custom report spec to the user directory
    user_format_set = FormatSet(
        heading="User Custom Format Set",
        description="A custom format set for the user directory",
        formats=[
            Format(
                types=["TABLE"],
                columns=[
                    Column(name="Column 1", key="column1"),
                    Column(name="Column 2", key="column2"),
                ],
            ),
        ],
    )
    
    user_format_sets = FormatSetDict({"UserCustomFormatSet": user_format_set})
    user_format_sets_path = os.path.join(USER_FORMAT_SETS_DIR, "user_custom_format_sets.json")
    user_format_sets.save_to_json(user_format_sets_path)
    print(f"Saved user custom report spec to {user_format_sets_path}")
    
    # Load the user format sets
    from pyegeria.base_report_formats import load_user_report_specs
    load_user_report_specs()
    
    # Check if the user report spec was loaded
    if "UserCustomFormatSet" in report_specs:
        print("User custom report spec was successfully loaded")
        print(f"  Heading: {report_specs['UserCustomFormatSet'].heading}")
        print(f"  Description: {report_specs['UserCustomFormatSet'].description}")
    else:
        print("User custom report spec was not loaded")

def main():
    """Run the example."""
    print("=== Report Specs Save/Load Example ===")
    
    # Create custom format sets
    custom_format_sets = create_custom_format_sets()
    
    # Save format sets to files
    file_path = save_format_sets_example(custom_format_sets)
    
    # Load format sets from a file
    loaded_format_sets = load_format_sets_example(file_path)
    
    # Use the loaded format sets
    if loaded_format_sets:
        use_loaded_format_sets(loaded_format_sets)
    
    # Work with the user format sets directory
    user_format_sets_directory_example(custom_format_sets)
    
    print("\n=== Example Complete ===")

if __name__ == "__main__":
    main()