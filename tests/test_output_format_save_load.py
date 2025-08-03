#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Test script for saving and loading output format sets.
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyegeria._output_format_models import Column, Format, FormatSet, FormatSetDict
from pyegeria._output_formats import (
    output_format_sets,
    save_output_format_sets,
    load_output_format_sets,
    USER_FORMAT_SETS_DIR,
)

def test_save_load_all_format_sets():
    """Test saving and loading all format sets."""
    print("\nTesting saving and loading all format sets...")
    
    # Create a temporary directory for the test
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save all format sets to a file
        file_path = os.path.join(temp_dir, "all_format_sets.json")
        save_output_format_sets(file_path)
        
        # Check that the file exists
        assert os.path.exists(file_path), f"File {file_path} does not exist"
        
        # Check that the file is not empty
        assert os.path.getsize(file_path) > 0, f"File {file_path} is empty"
        
        # Load the file to verify it's valid JSON
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Check that the data contains all the format sets
        assert len(data) == len(output_format_sets), f"Expected {len(output_format_sets)} format sets, got {len(data)}"
        
        # Create a new FormatSetDict to load the format sets into
        global output_format_sets
        original_format_sets = output_format_sets.copy()
        
        # Replace the global output_format_sets with an empty dictionary
        output_format_sets = FormatSetDict()
        
        # Load the format sets from the file
        load_output_format_sets(file_path, merge=False)
        
        # Check that the loaded format sets match the original format sets
        assert len(output_format_sets) == len(original_format_sets), f"Expected {len(original_format_sets)} format sets, got {len(output_format_sets)}"
        
        # Restore the original format sets
        output_format_sets = original_format_sets
    
    print("Save and load all format sets test passed!")

def test_save_load_subset_format_sets():
    """Test saving and loading a subset of format sets."""
    print("\nTesting saving and loading a subset of format sets...")
    
    # Create a temporary directory for the test
    with tempfile.TemporaryDirectory() as temp_dir:
        # Select a subset of format sets to save
        subset_names = ["Collections", "DataDictionary"]
        
        # Save the subset of format sets to a file
        file_path = os.path.join(temp_dir, "subset_format_sets.json")
        save_output_format_sets(file_path, format_set_names=subset_names)
        
        # Check that the file exists
        assert os.path.exists(file_path), f"File {file_path} does not exist"
        
        # Check that the file is not empty
        assert os.path.getsize(file_path) > 0, f"File {file_path} is empty"
        
        # Load the file to verify it's valid JSON
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Check that the data contains only the subset of format sets
        assert len(data) == len(subset_names), f"Expected {len(subset_names)} format sets, got {len(data)}"
        
        # Check that the data contains the correct format sets
        for name in subset_names:
            assert name in data, f"Format set {name} not found in saved data"
        
        # Create a new FormatSetDict to load the format sets into
        test_format_sets = FormatSetDict()
        
        # Load the format sets from the file
        global output_format_sets
        original_format_sets = output_format_sets.copy()
        output_format_sets = test_format_sets
        
        load_output_format_sets(file_path, merge=True)
        
        # Check that the loaded format sets match the subset
        assert len(output_format_sets) == len(subset_names), f"Expected {len(subset_names)} format sets, got {len(output_format_sets)}"
        
        # Check that the loaded format sets have the correct names
        for name in subset_names:
            assert name in output_format_sets, f"Format set {name} not found in loaded format sets"
        
        # Restore the original format sets
        output_format_sets = original_format_sets
    
    print("Save and load subset of format sets test passed!")

def test_merge_format_sets():
    """Test merging loaded format sets with existing ones."""
    print("\nTesting merging loaded format sets with existing ones...")
    
    # Create a temporary directory for the test
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a custom format set
        custom_format_set = FormatSet(
            heading="Custom Format Set",
            description="A custom format set for testing",
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
        
        # Create a FormatSetDict with the custom format set
        custom_format_sets = FormatSetDict({"CustomFormatSet": custom_format_set})
        
        # Save the custom format sets to a file
        file_path = os.path.join(temp_dir, "custom_format_sets.json")
        custom_format_sets.save_to_json(file_path)
        
        # Check that the file exists
        assert os.path.exists(file_path), f"File {file_path} does not exist"
        
        # Create a new FormatSetDict to load the format sets into
        test_format_sets = FormatSetDict()
        
        # Add some existing format sets
        test_format_sets["ExistingFormatSet"] = FormatSet(
            heading="Existing Format Set",
            description="An existing format set for testing",
            formats=[
                Format(
                    types=["TABLE"],
                    columns=[
                        Column(name="Column A", key="columnA"),
                        Column(name="Column B", key="columnB"),
                    ],
                ),
            ],
        )
        
        # Load the custom format sets and merge with the existing ones
        global output_format_sets
        original_format_sets = output_format_sets.copy()
        output_format_sets = test_format_sets
        
        load_output_format_sets(file_path, merge=True)
        
        # Check that the merged format sets contain both the existing and custom format sets
        assert "ExistingFormatSet" in output_format_sets, "Existing format set not found in merged format sets"
        assert "CustomFormatSet" in output_format_sets, "Custom format set not found in merged format sets"
        
        # Check that the merged format sets have the correct number of format sets
        assert len(output_format_sets) == 2, f"Expected 2 format sets, got {len(output_format_sets)}"
        
        # Restore the original format sets
        output_format_sets = original_format_sets
    
    print("Merge format sets test passed!")

def test_handle_invalid_file():
    """Test handling of invalid files."""
    print("\nTesting handling of invalid files...")
    
    # Create a temporary directory for the test
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create an invalid JSON file
        file_path = os.path.join(temp_dir, "invalid.json")
        with open(file_path, 'w') as f:
            f.write("This is not valid JSON")
        
        # Check that the file exists
        assert os.path.exists(file_path), f"File {file_path} does not exist"
        
        # Try to load the invalid file
        try:
            load_output_format_sets(file_path)
            assert False, "Expected an exception when loading an invalid file"
        except Exception as e:
            print(f"Correctly caught exception: {type(e).__name__}")
        
        # Create a file with valid JSON but invalid format sets
        file_path = os.path.join(temp_dir, "invalid_format_sets.json")
        with open(file_path, 'w') as f:
            json.dump({"InvalidFormatSet": {"not_a_format_set": True}}, f)
        
        # Check that the file exists
        assert os.path.exists(file_path), f"File {file_path} does not exist"
        
        # Try to load the file with invalid format sets
        try:
            load_output_format_sets(file_path)
            assert False, "Expected an exception when loading a file with invalid format sets"
        except Exception as e:
            print(f"Correctly caught exception: {type(e).__name__}")
    
    print("Handle invalid file test passed!")

def test_user_format_sets_directory():
    """Test the user format sets directory."""
    print("\nTesting the user format sets directory...")
    
    # Save the original USER_FORMAT_SETS_DIR
    original_dir = USER_FORMAT_SETS_DIR
    
    try:
        # Create a temporary directory for the test
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set the USER_FORMAT_SETS_DIR to the temporary directory
            global USER_FORMAT_SETS_DIR
            USER_FORMAT_SETS_DIR = temp_dir
            
            # Create a custom format set
            custom_format_set = FormatSet(
                heading="User Custom Format Set",
                description="A custom format set for testing the user directory",
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
            
            # Create a FormatSetDict with the custom format set
            custom_format_sets = FormatSetDict({"UserCustomFormatSet": custom_format_set})
            
            # Save the custom format sets to a file in the user directory
            os.makedirs(USER_FORMAT_SETS_DIR, exist_ok=True)
            file_path = os.path.join(USER_FORMAT_SETS_DIR, "user_custom_format_sets.json")
            custom_format_sets.save_to_json(file_path)
            
            # Check that the file exists
            assert os.path.exists(file_path), f"File {file_path} does not exist"
            
            # Create a new FormatSetDict to load the format sets into
            test_format_sets = FormatSetDict()
            
            # Load the user format sets
            global output_format_sets
            original_format_sets = output_format_sets.copy()
            output_format_sets = test_format_sets
            
            from pyegeria._output_formats import load_user_format_sets
            load_user_format_sets()
            
            # Check that the user format sets were loaded
            assert "UserCustomFormatSet" in output_format_sets, "User custom format set not found in loaded format sets"
            
            # Restore the original format sets
            output_format_sets = original_format_sets
    finally:
        # Restore the original USER_FORMAT_SETS_DIR
        USER_FORMAT_SETS_DIR = original_dir
    
    print("User format sets directory test passed!")

def main():
    """Run all tests."""
    test_save_load_all_format_sets()
    test_save_load_subset_format_sets()
    test_merge_format_sets()
    test_handle_invalid_file()
    test_user_format_sets_directory()
    
    print("\nAll tests passed!")

if __name__ == "__main__":
    main()