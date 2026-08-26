# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Unit tests for scripts/dr_egeria_audit.py's pure logic (type-name shape
heuristic, dead-attribute usage matching). No live server or real compact
JSON needed.
"""
import importlib.util
import os
import sys

import pytest

_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "dr_egeria_audit.py")
_spec = importlib.util.spec_from_file_location("dr_egeria_audit", _SCRIPT_PATH)
dr_egeria_audit = importlib.util.module_from_spec(_spec)
sys.modules["dr_egeria_audit"] = dr_egeria_audit
_spec.loader.exec_module(dr_egeria_audit)


@pytest.mark.parametrize("value,expected", [
    ("TermHASARelationship", True),
    ("ISARelationship", True),
    ("ProjectProperties", True),
    ("ACTIVE", False),          # all-caps domain enum value, not a type name
    ("ISA", False),             # all-caps, no lower->upper transition
    ("Related Term", False),    # has a space
    ("related_term", False),    # not capitalized, has underscore
    ("Discovered", False),      # ordinary single-capitalized-word enum value
    ("Security", False),        # same -- only one uppercase letter
    ("Other", False),           # same
    ("", False),
])
def test_looks_like_type_name(value, expected):
    assert dr_egeria_audit.looks_like_type_name(value) is expected


def test_attribute_referenced_finds_display_name():
    source = "attributes.get('Display Name', {}).get('value')"
    assert dr_egeria_audit.attribute_referenced("Display Name", [], source) is True


def test_attribute_referenced_finds_alias():
    source = "attributes.get('Element Name', {}).get('guid')"
    assert dr_egeria_audit.attribute_referenced("Referenceable Element", ["Element Name", "Element Id"], source) is True


def test_attribute_referenced_false_when_absent():
    source = "attributes.get('Something Else', {}).get('value')"
    assert dr_egeria_audit.attribute_referenced("Display Name", [], source) is False


def test_check_om_type_flags_unknown_type():
    families = {
        "fake_family.json": {
            "commands": {
                "Link Fake Thing": {"OM_TYPE": "TotallyFakeRelationship"},
                "Link Real Thing": {"OM_TYPE": "Synonym"},
            }
        }
    }
    result = dr_egeria_audit.AuditResult()
    dr_egeria_audit.check_om_type(families, {"Synonym", "Certification"}, result)

    assert len(result.findings) == 1
    assert result.findings[0].category == "OM_TYPE"
    assert result.findings[0].command == "Link Fake Thing"


def test_check_enum_values_flags_only_type_shaped_values():
    families = {
        "fake_family.json": {
            "attribute_definitions": {
                "Status": {"style": "Enum", "valid_values": ["ACTIVE", "DRAFT"]},
                "Relationship Type": {"style": "Enum", "valid_values": ["Synonym", "TermHASARelationship"]},
            }
        }
    }
    result = dr_egeria_audit.AuditResult()
    dr_egeria_audit.check_enum_values(families, {"Synonym"}, result)

    assert len(result.findings) == 1
    assert result.findings[0].detail.count("TermHASARelationship") == 1
