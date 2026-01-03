#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Test script for the output formats module.
"""

import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyegeria.base_report_formats import (
    report_specs,
    select_report_spec,
    report_spec_list,
    get_report_spec_heading,
    get_report_spec_description,
    get_report_spec_match,
)
from pyegeria._output_format_models import Column, Format, ActionParameter, FormatSet, FormatSetDict

def test_report_specs():
    """Test that the report_specs dictionary is correctly initialized."""
    print("\nTesting report_specs initialization...")
    
    # Check that report_specs is a FormatSetDict
    assert isinstance(report_specs, FormatSetDict), f"Expected FormatSetDict, got {type(report_specs)}"
    
    # Check that we have some format sets
    assert len(report_specs) > 0, "Expected at least one format set"
    
    # Check that each format set is a FormatSet
    for key, value in report_specs.items():
        assert isinstance(value, FormatSet), f"Expected FormatSet for {key}, got {type(value)}"
        
        # Check that each format set has the required attributes
        assert hasattr(value, "heading"), f"Format set {key} missing heading"
        assert hasattr(value, "description"), f"Format set {key} missing description"
        assert hasattr(value, "formats"), f"Format set {key} missing formats"
        
        # Check that each format is a Format
        for format in value.formats:
            assert isinstance(format, Format), f"Expected Format in {key}, got {type(format)}"
            
            # Check that each format has the required attributes
            assert hasattr(format, "types"), f"Format in {key} missing types"
            assert hasattr(format, "columns"), f"Format in {key} missing columns"
            
            # Check that each column is a Column
            for column in format.columns:
                assert isinstance(column, Column), f"Expected Column in {key}, got {type(column)}"
                
                # Check that each column has the required attributes
                assert hasattr(column, "name"), f"Column in {key} missing name"
                assert hasattr(column, "key"), f"Column in {key} missing key"
    
    print("Output format sets initialization test passed!")

def test_select_report_spec():
    """Test the select_report_spec function."""
    print("\nTesting select_report_spec function...")
    
    # Test getting a format set by name
    format_set = select_report_spec("Collections", "TABLE")
    assert format_set is not None, "Expected format set for Collections"
    assert "heading" in format_set, "Expected heading in format set"
    assert "description" in format_set, "Expected description in format set"
    assert "formats" in format_set, "Expected formats in format set"
    
    # Test getting a format set by alias
    format_set = select_report_spec("Collection", "TABLE")
    assert format_set is not None, "Expected format set for Collection alias"
    
    # Test getting a format set with a specific output type
    format_set = select_report_spec("Collections", "DICT")
    assert format_set is not None, "Expected format set for Collections with DICT output type"
    assert "formats" in format_set, "Expected formats in format set"
    assert "types" in format_set["formats"], "Expected types in format"
    assert "DICT" in format_set["formats"]["types"], "Expected DICT in types"
    
    # Test getting a format set with the ANY output type
    format_set = select_report_spec("Collections", "ANY")
    assert format_set is not None, "Expected format set for Collections with ANY output type"
    assert "formats" not in format_set, "Expected no formats in format set for ANY output type"
    
    # Test getting a format set that doesn't exist
    format_set = select_report_spec("NonExistentFormatSet", "TABLE")
    assert format_set is None, "Expected None for non-existent format set"
    
    print("Select output format set test passed!")

def test_report_spec_list():
    """Test the report_spec_list function."""
    print("\nTesting report_spec_list function...")
    
    # Get the list of format sets
    format_sets = report_spec_list()
    
    # Check that we have some format sets
    assert len(format_sets) > 0, "Expected at least one format set"
    
    # Check that each format set is a string
    for format_set in format_sets:
        assert isinstance(format_set, str), f"Expected string, got {type(format_set)}"
    
    # Check that some expected format sets are in the list
    assert "Collections" in format_sets, "Expected Collections in format sets"
    assert "Referenceable" in format_sets, "Expected Referenceable in format sets"
    
    print("Output format set list test passed!")


def test_report_spec_list_records_and_markdown():
    """Test the new return kinds for report_spec_list: records and markdown."""
    from pyegeria.base_report_formats import report_spec_list

    # Records mode
    records = report_spec_list(return_kind="records")
    assert isinstance(records, list), f"Expected list for records, got {type(records)}"
    assert len(records) > 0, "Expected at least one record"
    sample = records[0]
    assert set(["family", "name", "description"]).issubset(sample.keys()), "Missing expected keys in record"
    assert isinstance(sample["name"], str)
    assert isinstance(sample.get("family", None) if sample.get("family", None) is None else sample.get("family"), (str, type(None)))

    # Markdown mode
    md = report_spec_list(return_kind="markdown_table")
    assert isinstance(md, str), f"Expected markdown string, got {type(md)}"
    assert md.startswith("| Family | Report Name | Description |")
    # It should contain at least one row separator
    assert "\n|---|---|---|\n" in md or "\n|---|---|---|" in md

def test_get_report_spec_heading_and_description():
    """Test the get_report_spec_heading and get_report_spec_description functions."""
    print("\nTesting get_report_spec_heading and get_report_spec_description functions...")
    
    # Get the heading and description for a format set
    heading = get_report_spec_heading("Collections")
    description = get_report_spec_description("Collections")
    
    # Check that the heading and description are strings
    assert isinstance(heading, str), f"Expected string for heading, got {type(heading)}"
    assert isinstance(description, str), f"Expected string for description, got {type(description)}"
    
    # Check that the heading and description are not empty
    assert heading, "Expected non-empty heading"
    assert description, "Expected non-empty description"
    
    print("Get output format set heading and description test passed!")

def test_get_output_format_type_match():
    """Test the get_report_spec_match function."""
    print("\nTesting get_report_spec_match function...")
    
    # Get a format set
    format_set = select_report_spec("Collections", "ANY")
    
    # Match the format set with a specific output type
    matched_format_set = get_report_spec_match(format_set, "TABLE")
    
    # Check that the matched format set is a dictionary
    assert isinstance(matched_format_set, dict), f"Expected dict, got {type(matched_format_set)}"
    
    # Check that the matched format set has the formats attribute
    assert "formats" in matched_format_set, "Expected formats in matched format set"
    
    # Check that the matched format has the correct output type
    assert "types" in matched_format_set["formats"], "Expected types in matched format"
    assert "TABLE" in matched_format_set["formats"]["types"], "Expected TABLE in types"
    
    print("Get output format type match test passed!")

def test_format_composition():
    """Test the composition of formats."""
    print("\nTesting format composition...")
    
    # Create a new format set with composed formats
    common_columns = [
        Column(name="Common Column 1", key="common_column_1"),
        Column(name="Common Column 2", key="common_column_2"),
    ]
    
    specific_columns = [
        Column(name="Specific Column 1", key="specific_column_1"),
        Column(name="Specific Column 2", key="specific_column_2"),
    ]
    
    common_format = Format(
        types=["ALL"],
        columns=common_columns,
    )
    
    specific_format = Format(
        types=["TABLE"],
        columns=common_columns + specific_columns,
    )
    
    format_set = FormatSet(
        heading="Test Format Set",
        description="A test format set for testing format composition",
        formats=[common_format, specific_format],
    )
    
    # Convert the format set to a dictionary
    format_set_dict = format_set.dict()
    
    # Check that the format set has the correct attributes
    assert "heading" in format_set_dict, "Expected heading in format set"
    assert "description" in format_set_dict, "Expected description in format set"
    assert "formats" in format_set_dict, "Expected formats in format set"
    
    # Check that the formats have the correct attributes
    assert len(format_set_dict["formats"]) == 2, "Expected 2 formats"
    assert "types" in format_set_dict["formats"][0], "Expected types in format"
    assert "columns" in format_set_dict["formats"][0], "Expected columns in format"
    
    # Check that the columns have the correct attributes
    assert len(format_set_dict["formats"][0]["columns"]) == 2, "Expected 2 columns in common format"
    assert len(format_set_dict["formats"][1]["columns"]) == 4, "Expected 4 columns in specific format"
    
    print("Format composition test passed!")

def main():
    """Run all tests."""
    test_report_specs()
    test_select_report_spec()
    test_report_spec_list()
    test_get_report_spec_heading_and_description()
    test_get_output_format_type_match()
    test_format_composition()
    
    print("\nAll tests passed!")

if __name__ == "__main__":
    main()