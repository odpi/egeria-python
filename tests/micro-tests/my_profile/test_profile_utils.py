"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Unit tests for profile_utils module.
"""

import pytest
from profile_utils import (
    truncate_at_sequence,
    clean_structure,
    bools_to_strings,
    extract_glossary_terms,
)


class TestTruncateAtSequence:
    """Tests for truncate_at_sequence function."""

    def test_truncate_string_with_target(self):
        s = "some prefix specificationMermaidGraph and suffix"
        result, terminated = truncate_at_sequence(s, "specificationMermaidGraph")
        assert result == "some prefix "
        assert terminated is True

    def test_truncate_string_without_target(self):
        s = "clean string without target"
        result, terminated = truncate_at_sequence(s, "specificationMermaidGraph")
        assert result == "clean string without target"
        assert terminated is False

    def test_truncate_dict_with_target_in_key(self):
        d = {
            "valid_key": "valid_value",
            "prefix_specificationMermaidGraph_suffix": "graph data",
            "next_key": "should not matter",
        }
        result, terminated = truncate_at_sequence(d, "specificationMermaidGraph")
        assert "prefix_" in result
        assert terminated is True
        assert result["prefix_"] == "graph data"

    def test_truncate_dict_with_target_in_value(self):
        d = {
            "title": "My Title",
            "graph": "prefix specificationMermaidGraph details",
            "extra": "ignored",
        }
        result, terminated = truncate_at_sequence(d, "specificationMermaidGraph")
        assert result["title"] == "My Title"
        assert result["graph"] == "prefix "
        assert terminated is True

    def test_truncate_dict_without_target(self):
        d = {"a": 1, "b": "hello", "c": [1, 2, 3]}
        result, terminated = truncate_at_sequence(d, "specificationMermaidGraph")
        assert result == d
        assert terminated is False

    def test_truncate_list_with_target(self):
        lst = ["item1", "item2 specificationMermaidGraph suffix", "item3", "item4"]
        result, terminated = truncate_at_sequence(lst, "specificationMermaidGraph")
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0] == "item1"
        assert result[1] == "item2 "
        assert terminated is True

    def test_truncate_tuple_preserves_type(self):
        tup = ("item1", "item2 specificationMermaidGraph suffix", "item3")
        result, terminated = truncate_at_sequence(tup, "specificationMermaidGraph")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == "item1"
        assert result[1] == "item2 "
        assert terminated is True

    def test_truncate_nested_structures(self):
        nested = {
            "level1": {
                "items": [
                    {"name": "n1"},
                    {"name": "n2 specificationMermaidGraph extra"},
                    {"name": "n3"},
                ]
            }
        }
        result, terminated = truncate_at_sequence(nested, "specificationMermaidGraph")
        assert terminated is True
        items = result["level1"]["items"]
        assert len(items) == 2
        assert items[0]["name"] == "n1"
        assert items[1]["name"] == "n2 "

    def test_truncate_primitives(self):
        assert truncate_at_sequence(123, "target") == (123, False)
        assert truncate_at_sequence(3.14, "target") == (3.14, False)
        assert truncate_at_sequence(True, "target") == (True, False)
        assert truncate_at_sequence(None, "target") == (None, False)


class TestCleanStructure:
    """Tests for clean_structure wrapper."""

    def test_clean_structure_strips_target(self):
        raw = {"data": ["ok", "truncate_specificationMermaidGraph_tail", "never_reached"]}
        cleaned = clean_structure(raw, "specificationMermaidGraph")
        assert cleaned == {"data": ["ok", "truncate_"]}

    def test_clean_structure_noop_when_no_target(self):
        raw = {"key": "val", "num": 42}
        assert clean_structure(raw) == raw


class TestBoolsToStrings:
    """Tests for bools_to_strings function."""

    def test_bools_conversion_primitives(self):
        assert bools_to_strings(True) == "True"
        assert bools_to_strings(False) == "False"
        assert bools_to_strings(1) == 1
        assert bools_to_strings(0) == 0
        assert bools_to_strings("hello") == "hello"
        assert bools_to_strings(None) is None
        assert bools_to_strings(42.5) == 42.5

    def test_bools_in_dict(self):
        d = {"is_active": True, "is_deleted": False, "count": 10, "name": "test"}
        converted = bools_to_strings(d)
        assert converted == {
            "is_active": "True",
            "is_deleted": "False",
            "count": 10,
            "name": "test",
        }

    def test_bools_in_list_and_tuple(self):
        lst = [True, False, 123, "abc"]
        converted_list = bools_to_strings(lst)
        assert converted_list == ["True", "False", 123, "abc"]
        assert isinstance(converted_list, list)

        tup = (True, False, 456)
        converted_tup = bools_to_strings(tup)
        assert converted_tup == ("True", "False", 456)
        assert isinstance(converted_tup, tuple)

    def test_bools_in_nested_structure(self):
        nested = {
            "outer": [
                {"flag": True, "values": (False, True, 1)},
                {"enabled": False},
            ]
        }
        converted = bools_to_strings(nested)
        assert converted["outer"][0]["flag"] == "True"
        assert converted["outer"][0]["values"] == ("False", "True", 1)
        assert converted["outer"][1]["enabled"] == "False"


class TestExtractGlossaryTerms:
    """Tests for extract_glossary_terms regex utility."""

    def test_extract_single_term(self):
        text = "Related element: GlossaryTerm::ClinicalTrial, other text"
        terms = extract_glossary_terms(text)
        assert terms == ["ClinicalTrial"]

    def test_extract_multiple_terms(self):
        text = "Item1: GlossaryTerm::TermOne, Item2: GlossaryTerm::TermTwo, Item3: GlossaryTerm::TermThree"
        terms = extract_glossary_terms(text)
        assert terms == ["TermOne", "TermTwo", "TermThree"]

    def test_extract_no_terms(self):
        text = "There are no terms in this string"
        terms = extract_glossary_terms(text)
        assert terms == []

    def test_extract_terms_with_whitespace_and_quotes(self):
        text = "GlossaryTerm::Hospital Patient, GlossaryTerm::Medication Prescription"
        terms = extract_glossary_terms(text)
        assert len(terms) == 2
        assert terms == ["Hospital Patient", "Medication Prescription"]
