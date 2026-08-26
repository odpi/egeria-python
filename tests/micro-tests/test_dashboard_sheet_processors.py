# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Unit tests for md_processing.v2.dashboard_sheet's attribute-parsing helpers.

No live server, no AsyncBaseCommandProcessor scaffolding -- targets the pure
parsing logic Step 3 of the dr-egeria-command-sync skill requires verifying
whenever a compact-spec attribute changes (BACKLOG.md NEXT-19/NEXT-21,
egeria-workspaces-fs): that "Placement Perspectives"/"Placement Detail Spec"
are actually read by the processors that execute Link Report to Dashboard
Sheet / Add Text on Dashboard Sheet, not just declared in the spec.
"""

from md_processing.v2.dashboard_sheet import _parse_placement_perspectives


def test_parse_placement_perspectives_missing_attribute_yields_empty_list():
    assert _parse_placement_perspectives({}) == []


def test_parse_placement_perspectives_already_a_list():
    attrs = {"Placement Perspectives": {"value": ["governance", "steward"]}}
    assert _parse_placement_perspectives(attrs) == ["governance", "steward"]


def test_parse_placement_perspectives_comma_separated_string():
    attrs = {"Placement Perspectives": {"value": "governance, steward,  owner "}}
    assert _parse_placement_perspectives(attrs) == ["governance", "steward", "owner"]


def test_parse_placement_perspectives_empty_string_yields_empty_list():
    attrs = {"Placement Perspectives": {"value": ""}}
    assert _parse_placement_perspectives(attrs) == []


def test_parse_placement_perspectives_none_value_yields_empty_list():
    attrs = {"Placement Perspectives": {"value": None}}
    assert _parse_placement_perspectives(attrs) == []
