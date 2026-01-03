"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Tests for the utility functions in the pyegeria.utils module.
"""

import pytest
from pyegeria.utils import to_camel_case


class TestUtils:
    """Test class for utility functions in the pyegeria.utils module."""

    def test_to_camel_case_empty_string(self):
        """Test to_camel_case with an empty string."""
        assert to_camel_case("") == ""

    def test_to_camel_case_single_word(self):
        """Test to_camel_case with a single word."""
        assert to_camel_case("test") == "test"
        assert to_camel_case("Test") == "test"
        assert to_camel_case("TEST") == "test"

    def test_to_camel_case_multiple_words(self):
        """Test to_camel_case with multiple words."""
        assert to_camel_case("test string") == "testString"
        assert to_camel_case("Test String") == "testString"
        assert to_camel_case("TEST STRING") == "testString"

    def test_to_camel_case_singular_to_singular(self):
        """Test to_camel_case with singular words that should remain singular."""
        assert to_camel_case("data category") == "dataCategory"
        assert to_camel_case("business term") == "businessTerm"
        assert to_camel_case("glossary category") == "glossaryCategory"

    def test_to_camel_case_plural_to_singular(self):
        """Test to_camel_case with plural words that should be converted to singular."""
        assert to_camel_case("data categories") == "dataCategory"
        assert to_camel_case("business terms") == "businessTerm"
        assert to_camel_case("glossary categories") == "glossaryCategory"

    def test_to_camel_case_plural_endings(self):
        """Test to_camel_case with various plural endings."""
        # Words ending in 'ies' -> 'y'
        assert to_camel_case("categories") == "category"
        assert to_camel_case("properties") == "property"
        
        # Words ending in 'es'
        assert to_camel_case("classes") == "class"
        assert to_camel_case("boxes") == "box"
        assert to_camel_case("bushes") == "bush"
        assert to_camel_case("processes") == "process"
        
        # Words ending in 's' but not 'ss'
        assert to_camel_case("terms") == "term"
        assert to_camel_case("collections") == "collection"
        
        # Words ending in 'ss' should not be changed
        assert to_camel_case("class") == "class"
        assert to_camel_case("process") == "process"

    def test_to_camel_case_mixed_cases(self):
        """Test to_camel_case with mixed case inputs."""
        assert to_camel_case("Data Categories") == "dataCategory"
        assert to_camel_case("BUSINESS TERMS") == "businessTerm"
        assert to_camel_case("glossary CATEGORIES") == "glossaryCategory"

    def test_to_camel_case_examples_from_docstring(self):
        """Test the examples provided in the function's docstring."""
        assert to_camel_case("data categories") == "dataCategory"
        assert to_camel_case("business terms") == "businessTerm"
        assert to_camel_case("glossary categories") == "glossaryCategory"