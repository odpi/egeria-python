#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Test script for the FormatSetDict class in _output_format_models.py.
This script tests the ability to find format sets by either name or alias.
"""

import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyegeria._output_format_models import Column, Format, FormatSet, FormatSetDict

def test_format_set_dict_find_by_name_or_alias():
    """Test the ability to find format sets by either name or alias."""
    print("\nTesting FormatSetDict find_by_name_or_alias method...")
    
    # Create some test format sets with aliases
    format_set1 = FormatSet(
        heading="Test Format Set 1",
        description="A test format set with aliases",
        aliases=["test1", "format1", "set1"],
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
    
    format_set2 = FormatSet(
        heading="Test Format Set 2",
        description="Another test format set with aliases",
        aliases=["test2", "format2", "set2"],
        formats=[
            Format(
                types=["DICT"],
                columns=[
                    Column(name="Column A", key="columnA"),
                    Column(name="Column B", key="columnB"),
                ],
            ),
        ],
    )
    
    # Create a FormatSetDict with the test format sets
    format_set_dict = FormatSetDict({
        "TestFormatSet1": format_set1,
        "TestFormatSet2": format_set2,
    })
    
    # Test find_by_name_or_alias method
    print("Testing find_by_name_or_alias method...")
    
    # Test finding by name
    result1 = format_set_dict.find_by_name_or_alias("TestFormatSet1")
    assert result1 is not None, "Expected to find format set by name"
    assert result1.heading == "Test Format Set 1", f"Expected 'Test Format Set 1', got '{result1.heading}'"
    print(f"Found format set by name: {result1.heading}")
    
    # Test finding by alias
    result2 = format_set_dict.find_by_name_or_alias("test1")
    assert result2 is not None, "Expected to find format set by alias"
    assert result2.heading == "Test Format Set 1", f"Expected 'Test Format Set 1', got '{result2.heading}'"
    print(f"Found format set by alias: {result2.heading}")
    
    # Test finding by another alias
    result3 = format_set_dict.find_by_name_or_alias("format2")
    assert result3 is not None, "Expected to find format set by alias"
    assert result3.heading == "Test Format Set 2", f"Expected 'Test Format Set 2', got '{result3.heading}'"
    print(f"Found format set by alias: {result3.heading}")
    
    # Test finding a non-existent format set
    result4 = format_set_dict.find_by_name_or_alias("NonExistentFormatSet")
    assert result4 is None, "Expected None for non-existent format set"
    print("Correctly returned None for non-existent format set")
    
    print("find_by_name_or_alias method test passed!")

def test_format_set_dict_get():
    """Test the get method with both names and aliases."""
    print("\nTesting FormatSetDict get method...")
    
    # Create some test format sets with aliases
    format_set1 = FormatSet(
        heading="Test Format Set 1",
        description="A test format set with aliases",
        aliases=["test1", "format1", "set1"],
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
    
    format_set2 = FormatSet(
        heading="Test Format Set 2",
        description="Another test format set with aliases",
        aliases=["test2", "format2", "set2"],
        formats=[
            Format(
                types=["DICT"],
                columns=[
                    Column(name="Column A", key="columnA"),
                    Column(name="Column B", key="columnB"),
                ],
            ),
        ],
    )
    
    # Create a FormatSetDict with the test format sets
    format_set_dict = FormatSetDict({
        "TestFormatSet1": format_set1,
        "TestFormatSet2": format_set2,
    })
    
    # Test get method
    print("Testing get method...")
    
    # Test getting by name
    result1 = format_set_dict.get("TestFormatSet1")
    assert result1 is not None, "Expected to get format set by name"
    assert result1.heading == "Test Format Set 1", f"Expected 'Test Format Set 1', got '{result1.heading}'"
    print(f"Got format set by name: {result1.heading}")
    
    # Test getting by alias
    result2 = format_set_dict.get("test1")
    assert result2 is not None, "Expected to get format set by alias"
    assert result2.heading == "Test Format Set 1", f"Expected 'Test Format Set 1', got '{result2.heading}'"
    print(f"Got format set by alias: {result2.heading}")
    
    # Test getting by another alias
    result3 = format_set_dict.get("format2")
    assert result3 is not None, "Expected to get format set by alias"
    assert result3.heading == "Test Format Set 2", f"Expected 'Test Format Set 2', got '{result3.heading}'"
    print(f"Got format set by alias: {result3.heading}")
    
    # Test getting a non-existent format set
    result4 = format_set_dict.get("NonExistentFormatSet")
    assert result4 is None, "Expected None for non-existent format set"
    print("Correctly returned None for non-existent format set")
    
    # Test getting a non-existent format set with a default value
    default_value = "Default Value"
    result5 = format_set_dict.get("NonExistentFormatSet", default_value)
    assert result5 == default_value, f"Expected '{default_value}', got '{result5}'"
    print(f"Correctly returned default value for non-existent format set: {result5}")
    
    print("get method test passed!")

def test_format_set_dict_getitem():
    """Test the __getitem__ method with both names and aliases."""
    print("\nTesting FormatSetDict __getitem__ method...")
    
    # Create some test format sets with aliases
    format_set1 = FormatSet(
        heading="Test Format Set 1",
        description="A test format set with aliases",
        aliases=["test1", "format1", "set1"],
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
    
    format_set2 = FormatSet(
        heading="Test Format Set 2",
        description="Another test format set with aliases",
        aliases=["test2", "format2", "set2"],
        formats=[
            Format(
                types=["DICT"],
                columns=[
                    Column(name="Column A", key="columnA"),
                    Column(name="Column B", key="columnB"),
                ],
            ),
        ],
    )
    
    # Create a FormatSetDict with the test format sets
    format_set_dict = FormatSetDict({
        "TestFormatSet1": format_set1,
        "TestFormatSet2": format_set2,
    })
    
    # Test __getitem__ method
    print("Testing __getitem__ method...")
    
    # Test getting by name
    try:
        result1 = format_set_dict["TestFormatSet1"]
        assert result1.heading == "Test Format Set 1", f"Expected 'Test Format Set 1', got '{result1.heading}'"
        print(f"Got format set by name: {result1.heading}")
    except KeyError:
        assert False, "Unexpected KeyError when getting by name"
    
    # Test getting by alias
    try:
        result2 = format_set_dict["test1"]
        assert result2.heading == "Test Format Set 1", f"Expected 'Test Format Set 1', got '{result2.heading}'"
        print(f"Got format set by alias: {result2.heading}")
    except KeyError:
        assert False, "Unexpected KeyError when getting by alias"
    
    # Test getting by another alias
    try:
        result3 = format_set_dict["format2"]
        assert result3.heading == "Test Format Set 2", f"Expected 'Test Format Set 2', got '{result3.heading}'"
        print(f"Got format set by alias: {result3.heading}")
    except KeyError:
        assert False, "Unexpected KeyError when getting by alias"
    
    # Test getting a non-existent format set
    try:
        result4 = format_set_dict["NonExistentFormatSet"]
        assert False, "Expected KeyError for non-existent format set"
    except KeyError:
        print("Correctly raised KeyError for non-existent format set")
    
    print("__getitem__ method test passed!")

def test_format_set_dict_contains():
    """Test the __contains__ method with both names and aliases."""
    print("\nTesting FormatSetDict __contains__ method...")
    
    # Create some test format sets with aliases
    format_set1 = FormatSet(
        heading="Test Format Set 1",
        description="A test format set with aliases",
        aliases=["test1", "format1", "set1"],
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
    
    format_set2 = FormatSet(
        heading="Test Format Set 2",
        description="Another test format set with aliases",
        aliases=["test2", "format2", "set2"],
        formats=[
            Format(
                types=["DICT"],
                columns=[
                    Column(name="Column A", key="columnA"),
                    Column(name="Column B", key="columnB"),
                ],
            ),
        ],
    )
    
    # Create a FormatSetDict with the test format sets
    format_set_dict = FormatSetDict({
        "TestFormatSet1": format_set1,
        "TestFormatSet2": format_set2,
    })
    
    # Test __contains__ method
    print("Testing __contains__ method...")
    
    # Test checking by name
    assert "TestFormatSet1" in format_set_dict, "Expected format set to be found by name"
    print("Format set found by name")
    
    # Test checking by alias
    assert "test1" in format_set_dict, "Expected format set to be found by alias"
    print("Format set found by alias")
    
    # Test checking by another alias
    assert "format2" in format_set_dict, "Expected format set to be found by alias"
    print("Format set found by alias")
    
    # Test checking a non-existent format set
    assert "NonExistentFormatSet" not in format_set_dict, "Expected format set not to be found"
    print("Non-existent format set correctly not found")
    
    print("__contains__ method test passed!")

def main():
    """Run all tests."""
    test_format_set_dict_find_by_name_or_alias()
    test_format_set_dict_get()
    test_format_set_dict_getitem()
    test_format_set_dict_contains()
    
    print("\nAll tests passed!")

if __name__ == "__main__":
    main()