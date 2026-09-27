# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
expand_command() builds the attribute list that runtime specs, generated
templates, help and report specs all consume. An attribute named both in a
command's bundle chain and in its custom_attributes (or declared by a bundle
and again by one it inherits from) must appear once, at its first position.
"""
from md_processing.md_processing_utils.parse_compact_export import expand_command

ATTR_DEFS = {name: {"variable_name": name.lower().replace(" ", "_")}
             for name in ("Display Name", "Description", "Data Type", "Position", "Units")}
BUNDLES = {
    "Base": {"inherits": None, "own_attributes": ["Display Name", "Description"]},
    "Field": {"inherits": "Base", "own_attributes": ["Data Type", "Description", "Position"]},
}


def _names(expanded: dict) -> list[str]:
    return [a["name"] for a in expanded["all_attributes"]]


def test_custom_attributes_already_in_bundle_are_listed_once():
    command = {"bundle": "Field", "custom_attributes": ["Position", "Units", "Data Type", "Units"]}
    expanded = expand_command(command, BUNDLES, ATTR_DEFS)

    assert _names(expanded) == ["Display Name", "Description", "Data Type", "Position", "Units"]
    assert expanded["bundle_attribute_count"] == 4
    assert expanded["custom_attribute_count"] == 1
    assert expanded["total_attribute_count"] == 5


def test_command_custom_attributes_list_is_not_modified():
    # Some processors read custom_attributes by position (e.g. SolutionLinkProcessor's
    # link endpoints), so dedupe must only affect the expanded list, not the command.
    command = {"bundle": "Field", "custom_attributes": ["Position", "Units"]}
    expand_command(command, BUNDLES, ATTR_DEFS)
    assert command["custom_attributes"] == ["Position", "Units"]
