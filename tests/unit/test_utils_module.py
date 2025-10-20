"""
Unit tests for pyegeria utility modules.

These tests cover utility functions and helper modules.
"""

import pytest
import json
from unittest.mock import Mock, patch
from datetime import datetime

from pyegeria.utils import (
    init_log, print_rest_request_body, print_rest_response, print_guid_list,
    body_slimmer, camel_to_title_case, to_camel_case, dynamic_catch
)


@pytest.mark.unit
class TestUtilsModule:
    """Unit tests for utils module."""
    
    def test_init_log(self):
        """Test init_log function."""
        # This function currently does nothing, just test it doesn't raise
        result = init_log()
        assert result is None
    
    def test_print_rest_request_body(self):
        """Test print_rest_request_body function."""
        test_body = {"key1": "value1", "key2": "value2"}
        
        # Test that function doesn't raise exception
        print_rest_request_body(test_body)
        
        # Test with None
        print_rest_request_body(None)
        
        # Test with empty dict
        print_rest_request_body({})
    
    def test_print_rest_response(self):
        """Test print_rest_response function."""
        test_response = {"status": "success", "data": [1, 2, 3]}
        
        # Test that function doesn't raise exception
        print_rest_response(test_response)
        
        # Test with None
        print_rest_response(None)
        
        # Test with empty dict
        print_rest_response({})
    
    def test_print_guid_list(self):
        """Test print_guid_list function."""
        test_guids = ["guid1", "guid2", "guid3"]
        
        # Test that function doesn't raise exception
        print_guid_list(test_guids)
        
        # Test with None
        print_guid_list(None)
        
        # Test with empty list
        print_guid_list([])
    
    def test_body_slimmer_basic(self):
        """Test body_slimmer with basic dictionary."""
        test_body = {
            "key1": "value1",
            "key2": "value2",
            "key3": None,
            "key4": "",
            "key5": 0
        }
        
        result = body_slimmer(test_body)
        
        # Should remove None values but keep empty string and 0
        assert "key1" in result
        assert "key2" in result
        assert "key3" not in result  # None should be removed
        assert "key4" in result  # Empty string should be kept
        assert "key5" in result  # 0 should be kept
        
        assert result["key1"] == "value1"
        assert result["key2"] == "value2"
        assert result["key4"] == ""
        assert result["key5"] == 0
    
    def test_body_slimmer_nested(self):
        """Test body_slimmer with nested dictionaries."""
        test_body = {
            "key1": "value1",
            "nested": {
                "nested_key1": "nested_value1",
                "nested_key2": None,
                "nested_key3": ""
            },
            "key2": None
        }
        
        result = body_slimmer(test_body)
        
        assert "key1" in result
        assert "nested" in result
        assert "key2" not in result
        
        nested = result["nested"]
        assert "nested_key1" in nested
        assert "nested_key2" not in nested  # None should be removed
        assert "nested_key3" in nested  # Empty string should be kept
        
        assert nested["nested_key1"] == "nested_value1"
        assert nested["nested_key3"] == ""
    
    def test_body_slimmer_empty_nested(self):
        """Test body_slimmer with empty nested dictionaries."""
        test_body = {
            "key1": "value1",
            "empty_nested": {
                "nested_key1": None,
                "nested_key2": None
            },
            "key2": "value2"
        }
        
        result = body_slimmer(test_body)
        
        assert "key1" in result
        assert "empty_nested" not in result  # Empty nested dict should be removed
        assert "key2" in result
        
        assert result["key1"] == "value1"
        assert result["key2"] == "value2"
    
    def test_body_slimmer_none_input(self):
        """Test body_slimmer with None input."""
        result = body_slimmer(None)
        assert result == {}
    
    def test_body_slimmer_empty_dict(self):
        """Test body_slimmer with empty dictionary."""
        result = body_slimmer({})
        assert result == {}
    
    def test_body_slimmer_with_tuples(self):
        """Test body_slimmer with tuple values."""
        test_body = {
            "key1": "value1",
            "key2": ("tuple", "value"),
            "key3": None
        }
        
        result = body_slimmer(test_body)
        
        assert "key1" in result
        assert "key2" not in result  # Tuples should be removed
        assert "key3" not in result  # None should be removed
        
        assert result["key1"] == "value1"
    
    def test_camel_to_title_case(self):
        """Test camel_to_title_case function."""
        # Test basic camelCase
        result = camel_to_title_case("camelCase")
        assert result == "Camel Case"
        
        # Test PascalCase
        result = camel_to_title_case("PascalCase")
        assert result == "Pascal Case"
        
        # Test single word
        result = camel_to_title_case("word")
        assert result == "Word"
        
        # Test multiple words
        result = camel_to_title_case("thisIsATest")
        assert result == "This Is A Test"
        
        # Test with numbers
        result = camel_to_title_case("test123Case")
        assert result == "Test123 Case"
        
        # Test empty string
        result = camel_to_title_case("")
        assert result == ""
    
    def test_to_camel_case(self):
        """Test to_camel_case function."""
        # Test basic conversion
        result = to_camel_case("test_case")
        assert result == "testCase"
        
        # Test with underscores
        result = to_camel_case("test_case_example")
        assert result == "testCaseExample"
        
        # Test single word
        result = to_camel_case("test")
        assert result == "test"
        
        # Test already camelCase
        result = to_camel_case("testCase")
        assert result == "testCase"
        
        # Test with numbers
        result = to_camel_case("test_123_case")
        assert result == "test123Case"
        
        # Test empty string
        result = to_camel_case("")
        assert result == ""
    
    def test_dynamic_catch_decorator(self):
        """Test dynamic_catch decorator."""
        # Test successful function execution
        @dynamic_catch
        def test_function_success():
            return "success"
        
        result = test_function_success()
        assert result == "success"
        
        # Test function that raises exception
        @dynamic_catch
        def test_function_error():
            raise ValueError("test error")
        
        # The decorator should catch the exception and return None or handle it
        result = test_function_error()
        # The exact behavior depends on the decorator implementation
        # This test verifies it doesn't crash the test suite
    
    def test_dynamic_catch_with_args(self):
        """Test dynamic_catch decorator with function arguments."""
        @dynamic_catch
        def test_function_with_args(arg1, arg2=None):
            return f"{arg1}_{arg2}"
        
        result = test_function_with_args("test", "value")
        assert result == "test_value"
        
        result = test_function_with_args("test")
        assert result == "test_None"
    
    def test_dynamic_catch_with_kwargs(self):
        """Test dynamic_catch decorator with keyword arguments."""
        @dynamic_catch
        def test_function_with_kwargs(**kwargs):
            return kwargs
        
        result = test_function_with_kwargs(key1="value1", key2="value2")
        assert result == {"key1": "value1", "key2": "value2"}
    
    def test_dynamic_catch_exception_handling(self):
        """Test dynamic_catch decorator exception handling."""
        @dynamic_catch
        def test_function_exception():
            raise RuntimeError("test runtime error")
        
        # The decorator should handle the exception gracefully
        result = test_function_exception()
        # The exact return value depends on the decorator implementation
        # This test ensures the decorator doesn't crash


@pytest.mark.unit
class TestUtilsIntegration:
    """Integration tests for utils module."""
    
    def test_body_slimmer_complex_structure(self):
        """Test body_slimmer with complex nested structure."""
        complex_body = {
            "level1": {
                "level2": {
                    "level3": {
                        "key1": "value1",
                        "key2": None,
                        "key3": ""
                    },
                    "key4": "value4",
                    "key5": None
                },
                "key6": "value6"
            },
            "key7": None,
            "key8": "value8",
            "empty_nested": {
                "all_none": None,
                "all_empty": ""
            }
        }
        
        result = body_slimmer(complex_body)
        
        # Check top level
        assert "level1" in result
        assert "key7" not in result
        assert "key8" in result
        assert "empty_nested" not in result
        
        # Check level 1
        level1 = result["level1"]
        assert "level2" in level1
        assert "key6" in level1
        
        # Check level 2
        level2 = level1["level2"]
        assert "level3" in level2
        assert "key4" in level2
        assert "key5" not in level2
        
        # Check level 3
        level3 = level2["level3"]
        assert "key1" in level3
        assert "key2" not in level3
        assert "key3" in level3
        
        assert level3["key1"] == "value1"
        assert level3["key3"] == ""
    
    def test_camel_case_conversion_roundtrip(self):
        """Test camel case conversion roundtrip."""
        original = "this_is_a_test_case"
        camel = to_camel_case(original)
        title = camel_to_title_case(camel)
        
        # Should be able to convert back and forth
        assert camel == "thisIsATestCase"
        assert title == "This Is A Test Case"
    
    def test_utility_functions_with_edge_cases(self):
        """Test utility functions with edge cases."""
        # Test body_slimmer with various data types
        edge_case_body = {
            "string": "test",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "list": [1, 2, 3],
            "none": None,
            "empty_string": "",
            "zero": 0,
            "false": False
        }
        
        result = body_slimmer(edge_case_body)
        
        # All non-None values should be preserved
        assert result["string"] == "test"
        assert result["number"] == 42
        assert result["float"] == 3.14
        assert result["boolean"] is True
        assert result["list"] == [1, 2, 3]
        assert result["none"] is None  # None should be removed
        assert result["empty_string"] == ""
        assert result["zero"] == 0
        assert result["false"] is False
        
        # None should be removed
        assert "none" not in result
    
    def test_string_conversion_functions(self):
        """Test string conversion functions with various inputs."""
        test_cases = [
            ("snake_case", "snakeCase", "Snake Case"),
            ("PascalCase", "pascalCase", "Pascal Case"),
            ("alreadyCamelCase", "alreadyCamelCase", "Already Camel Case"),
            ("", "", ""),
            ("single", "single", "Single"),
            ("a", "a", "A"),
            ("test_123_case", "test123Case", "Test123 Case"),
            ("XMLHttpRequest", "xMLHttpRequest", "X M L Http Request"),
        ]
        
        for snake, expected_camel, expected_title in test_cases:
            camel_result = to_camel_case(snake)
            title_result = camel_to_title_case(camel_result)
            
            assert camel_result == expected_camel, f"Failed for {snake}: expected {expected_camel}, got {camel_result}"
            assert title_result == expected_title, f"Failed for {camel_result}: expected {expected_title}, got {title_result}"
