"""
Unit tests for pyegeria output formats module.

These tests cover output format management and selection.
"""

import pytest
from unittest.mock import Mock, patch

from pyegeria.base_report_formats import (
    combine_format_set_dicts, select_report_spec, report_spec_list,
    get_report_spec_heading, get_report_spec_description,
    get_report_spec_match, list_mcp_format_sets
)


@pytest.mark.unit
class TestOutputFormatsModule:
    """Unit tests for _output_formats module."""
    
    def test_combine_format_set_dicts_basic(self):
        """Test combine_format_set_dicts with basic dictionaries."""
        dict1 = {"key1": "value1", "key2": "value2"}
        dict2 = {"key3": "value3", "key4": "value4"}
        
        result = combine_format_set_dicts(dict1, dict2)
        
        assert result["key1"] == "value1"
        assert result["key2"] == "value2"
        assert result["key3"] == "value3"
        assert result["key4"] == "value4"
        assert len(result) == 4
    
    def test_combine_format_set_dicts_overwrite(self):
        """Test combine_format_set_dicts with key overwriting."""
        dict1 = {"key1": "value1", "key2": "value2"}
        dict2 = {"key1": "new_value1", "key3": "value3"}
        
        result = combine_format_set_dicts(dict1, dict2)
        
        assert result["key1"] == "new_value1"  # Overwritten by dict2
        assert result["key2"] == "value2"  # From dict1
        assert result["key3"] == "value3"  # From dict2
        assert len(result) == 3
    
    def test_combine_format_set_dicts_nested(self):
        """Test combine_format_set_dicts with nested dictionaries."""
        dict1 = {
            "nested": {
                "key1": "value1",
                "key2": "value2"
            },
            "top_key": "top_value"
        }
        dict2 = {
            "nested": {
                "key2": "new_value2",
                "key3": "value3"
            },
            "another_top": "another_value"
        }
        
        result = combine_format_set_dicts(dict1, dict2)
        
        assert result["top_key"] == "top_value"
        assert result["another_top"] == "another_value"
        assert result["nested"]["key1"] == "value1"  # From dict1
        assert result["nested"]["key2"] == "new_value2"  # Overwritten by dict2
        assert result["nested"]["key3"] == "value3"  # From dict2
        assert len(result["nested"]) == 3
    
    def test_combine_format_set_dicts_empty(self):
        """Test combine_format_set_dicts with empty dictionaries."""
        dict1 = {}
        dict2 = {"key1": "value1"}
        
        result = combine_format_set_dicts(dict1, dict2)
        assert result == {"key1": "value1"}
        
        result = combine_format_set_dicts(dict2, dict1)
        assert result == {"key1": "value1"}
        
        result = combine_format_set_dicts({}, {})
        assert result == {}
    
    def test_combine_format_set_dicts_non_dict_overwrite(self):
        """Test combine_format_set_dicts with non-dict value overwriting."""
        dict1 = {"key1": {"nested": "value"}}
        dict2 = {"key1": "string_value"}
        
        result = combine_format_set_dicts(dict1, dict2)
        assert result["key1"] == "string_value"  # Non-dict overwrites dict
    
    @patch('pyegeria._output_formats.report_specs')
    def test_select_report_spec_existing(self, mock_format_sets):
        """Test select_report_spec with existing format set."""
        mock_format_sets.__getitem__.return_value = {
            "target_type": "TestType",
            "heading": "Test Heading",
            "description": "Test Description",
            "formats": [
                {
                    "types": ["DICT", "JSON"],
                    "columns": [
                        {"name": "Name", "key": "name"},
                        {"name": "Description", "key": "description"}
                    ]
                }
            ]
        }
        
        result = select_report_spec("TestFormat", "DICT")
        
        assert result is not None
        assert result["target_type"] == "TestType"
        assert result["heading"] == "Test Heading"
        assert result["description"] == "Test Description"
        assert "formats" in result
    
    @patch('pyegeria._output_formats.report_specs')
    def test_select_report_spec_nonexistent(self, mock_format_sets):
        """Test select_report_spec with non-existent format set."""
        mock_format_sets.__getitem__.side_effect = KeyError("Format not found")
        
        result = select_report_spec("NonExistentFormat", "DICT")
        
        assert result is None
    
    @patch('pyegeria._output_formats.report_specs')
    def test_select_report_spec_incompatible_type(self, mock_format_sets):
        """Test select_report_spec with incompatible output type."""
        mock_format_sets.__getitem__.return_value = {
            "target_type": "TestType",
            "formats": [
                {
                    "types": ["DICT", "JSON"],
                    "columns": []
                }
            ]
        }
        
        result = select_report_spec("TestFormat", "INCOMPATIBLE_TYPE")
        
        assert result is None
    
    @patch('pyegeria._output_formats.report_specs')
    def test_report_spec_list(self, mock_format_sets):
        """Test report_spec_list function."""
        mock_format_sets.items.return_value = [
            ("Format1", {"target_type": "Type1"}),
            ("Format2", {"target_type": "Type2"}),
            ("Format3", {"target_type": "Type3"})
        ]
        
        result = report_spec_list()
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert "Format1" in result
        assert "Format2" in result
        assert "Format3" in result
    
    @patch('pyegeria._output_formats.report_specs')
    def test_get_report_spec_heading_existing(self, mock_format_sets):
        """Test get_report_spec_heading with existing format set."""
        mock_format_sets.__getitem__.return_value = {
            "heading": "Test Heading"
        }
        
        result = get_report_spec_heading("TestFormat")
        
        assert result == "Test Heading"
    
    @patch('pyegeria._output_formats.report_specs')
    def test_get_report_spec_heading_nonexistent(self, mock_format_sets):
        """Test get_report_spec_heading with non-existent format set."""
        mock_format_sets.__getitem__.side_effect = KeyError("Format not found")
        
        result = get_report_spec_heading("NonExistentFormat")
        
        assert result is None
    
    @patch('pyegeria._output_formats.report_specs')
    def test_get_report_spec_description_existing(self, mock_format_sets):
        """Test get_report_spec_description with existing format set."""
        mock_format_sets.__getitem__.return_value = {
            "description": "Test Description"
        }
        
        result = get_report_spec_description("TestFormat")
        
        assert result == "Test Description"
    
    @patch('pyegeria._output_formats.report_specs')
    def test_get_report_spec_description_nonexistent(self, mock_format_sets):
        """Test get_report_spec_description with non-existent format set."""
        mock_format_sets.__getitem__.side_effect = KeyError("Format not found")
        
        result = get_report_spec_description("NonExistentFormat")
        
        assert result is None
    
    def test_get_report_spec_match_compatible(self):
        """Test get_report_spec_match with compatible format."""
        format_set = {
            "formats": [
                {
                    "types": ["DICT", "JSON"],
                    "columns": [
                        {"name": "Name", "key": "name"}
                    ]
                },
                {
                    "types": ["TABLE"],
                    "columns": [
                        {"name": "Name", "key": "name"},
                        {"name": "Description", "key": "description"}
                    ]
                }
            ]
        }
        
        result = get_report_spec_match(format_set, "DICT")
        
        assert result is not None
        assert result["types"] == ["DICT", "JSON"]
        assert len(result["columns"]) == 1
        assert result["columns"][0]["name"] == "Name"
    
    def test_get_report_spec_match_incompatible(self):
        """Test get_report_spec_match with incompatible format."""
        format_set = {
            "formats": [
                {
                    "types": ["TABLE"],
                    "columns": []
                }
            ]
        }
        
        result = get_report_spec_match(format_set, "DICT")
        
        assert result is None
    
    def test_get_report_spec_match_no_formats(self):
        """Test get_report_spec_match with no formats."""
        format_set = {}
        
        result = get_report_spec_match(format_set, "DICT")
        
        assert result is None
    
    def test_get_report_spec_match_none_format_set(self):
        """Test get_report_spec_match with None format set."""
        result = get_report_spec_match(None, "DICT")
        
        assert result is None
    
    @patch('pyegeria._output_formats.report_specs')
    def test_list_mcp_format_sets(self, mock_format_sets):
        """Test list_mcp_format_sets function."""
        mock_format_sets.items.return_value = [
            ("Digital-Products", {
                "target_type": "DigitalProduct",
                "heading": "Digital Products",
                "description": "List digital products",
                "formats": [
                    {
                        "types": ["DICT", "JSON"],
                        "columns": [
                            {"name": "Name", "key": "display_name"},
                            {"name": "Description", "key": "description"}
                        ]
                    }
                ]
            }),
            ("Glossary-Terms", {
                "target_type": "GlossaryTerm",
                "heading": "Glossary Terms",
                "description": "List glossary terms",
                "formats": [
                    {
                        "types": ["DICT", "JSON"],
                        "columns": [
                            {"name": "Term", "key": "display_name"},
                            {"name": "Definition", "key": "summary"}
                        ]
                    }
                ]
            })
        ]
        
        result = list_mcp_format_sets()
        
        assert isinstance(result, dict)
        assert "formatSets" in result
        assert isinstance(result["formatSets"], list)
        assert len(result["formatSets"]) == 2
        
        # Check first format set
        first_format = result["formatSets"][0]
        assert first_format["name"] == "Digital-Products"
        assert first_format["target_type"] == "DigitalProduct"
        assert first_format["heading"] == "Digital Products"
        assert first_format["description"] == "List digital products"
        
        # Check second format set
        second_format = result["formatSets"][1]
        assert second_format["name"] == "Glossary-Terms"
        assert second_format["target_type"] == "GlossaryTerm"
        assert second_format["heading"] == "Glossary Terms"
        assert second_format["description"] == "List glossary terms"
    
    @patch('pyegeria._output_formats.report_specs')
    def test_list_mcp_format_sets_empty(self, mock_format_sets):
        """Test list_mcp_format_sets with empty format sets."""
        mock_format_sets.items.return_value = []
        
        result = list_mcp_format_sets()
        
        assert isinstance(result, dict)
        assert "formatSets" in result
        assert isinstance(result["formatSets"], list)
        assert len(result["formatSets"]) == 0
    
    def test_format_set_structure_validation(self):
        """Test format set structure validation."""
        # Test valid format set structure
        valid_format_set = {
            "target_type": "TestType",
            "heading": "Test Heading",
            "description": "Test Description",
            "formats": [
                {
                    "types": ["DICT", "JSON"],
                    "columns": [
                        {"name": "Name", "key": "name"},
                        {"name": "Description", "key": "description"}
                    ]
                }
            ]
        }
        
        # Test that the structure is valid
        assert "target_type" in valid_format_set
        assert "heading" in valid_format_set
        assert "description" in valid_format_set
        assert "formats" in valid_format_set
        assert isinstance(valid_format_set["formats"], list)
        assert len(valid_format_set["formats"]) > 0
        
        # Test format structure
        format_item = valid_format_set["formats"][0]
        assert "types" in format_item
        assert "columns" in format_item
        assert isinstance(format_item["types"], list)
        assert isinstance(format_item["columns"], list)
        
        # Test column structure
        column = format_item["columns"][0]
        assert "name" in column
        assert "key" in column
    
    def test_output_type_compatibility(self):
        """Test output type compatibility checking."""
        # Test compatible types
        compatible_types = ["DICT", "JSON", "TABLE", "REPORT", "MERMAID", "HTML"]
        
        for output_type in compatible_types:
            format_set = {
                "formats": [
                    {
                        "types": [output_type],
                        "columns": []
                    }
                ]
            }
            
            result = get_report_spec_match(format_set, output_type)
            assert result is not None, f"Output type {output_type} should be compatible"
        
        # Test incompatible type
        format_set = {
            "formats": [
                {
                    "types": ["DICT"],
                    "columns": []
                }
            ]
        }
        
        result = get_report_spec_match(format_set, "INCOMPATIBLE")
        assert result is None, "Incompatible output type should return None"
