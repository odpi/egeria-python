# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""The element-status refusal points at the command's own status attribute (offline, stub valid-metadata client).

Since pyegeria 6.3.3 the `Status` that `add_default_upsert_attributes` adds is checked against Egeria's valid
metadata values for `status` (ACTIVE, DELETED, INVALID, OTHER, UNKNOWN), so `Status: DRAFT` is refused. Where the
command has a Content / Activity / Deployment Status that accepts the value, the error now says to use it.
"""
import asyncio

import pytest

from md_processing.md_processing_utils.md_processing_constants import load_commands
from md_processing.v2.extraction import DrECommand
from md_processing.v2.parsing import AttributeFirstParser

ELEMENT_STATUSES = ("ACTIVE", "DELETED", "INVALID", "OTHER", "UNKNOWN")
REFUSED = "is not a valid metadata value for 'Status' (Validated by Egeria)"


class StubValidMetadata:
    """Egeria's valid metadata values: property `status` lists the element statuses; other properties list none."""

    async def _async_validate_metadata_value(self, prop, type_name, value):
        return None

    async def _async_get_valid_metadata_values(self, prop, type_name):
        if prop == "status":
            return [{"preferredValue": v, "displayName": v} for v in ELEMENT_STATUSES]
        return []


def parse(command: str, attributes: dict) -> AttributeFirstParser:
    load_commands()
    AttributeFirstParser._valid_values_cache.clear()
    verb, object_type = command.split(" ", 1)
    block = f"## {command}\n" + "".join(f"### {k}\n{v}\n" for k, v in attributes.items())
    parser = AttributeFirstParser(DrECommand(verb=verb, object_type=object_type, attributes=attributes,
                                             raw_block=block), client=StubValidMetadata())
    asyncio.run(parser.parse())
    AttributeFirstParser._valid_values_cache.clear()
    return parser


@pytest.mark.parametrize("command", ["Create Schema Type", "Create Schema Attribute",
                                     "Create Display Data Container", "Create Display Data Field"])
def test_status_draft_is_refused_with_a_pointer_to_content_status(command):
    parser = parse(command, {"Display Name": "Hint Test", "Status": "DRAFT"})
    errors = [e for e in parser.errors if REFUSED in e]
    assert errors == [
        "Value 'DRAFT' is not a valid metadata value for 'Status' (Validated by Egeria). 'Status' here is the "
        "element status; to set DRAFT, use 'Content Status' instead"
    ]


@pytest.mark.parametrize("command", ["Create Schema Type", "Create Display Data Field"])
def test_content_status_draft_is_accepted(command):
    parser = parse(command, {"Display Name": "Hint Test", "Content Status": "DRAFT"})
    assert not [e for e in parser.errors if "DRAFT" in e]


def test_an_element_status_value_is_still_accepted():
    parser = parse("Create Schema Type", {"Display Name": "Hint Test", "Status": "ACTIVE"})
    assert not [e for e in parser.errors if REFUSED in e]


def test_a_value_no_status_attribute_takes_gets_no_pointer():
    parser = parse("Create Schema Type", {"Display Name": "Hint Test", "Status": "NOT_A_STATUS"})
    assert [e for e in parser.errors if REFUSED in e] == [
        "Value 'NOT_A_STATUS' is not a valid metadata value for 'Status' (Validated by Egeria)"
    ]


def test_a_command_without_a_type_specific_status_gets_no_pointer():
    parser = parse("Create Rating", {"Status": "DRAFT"})
    refused = [e for e in parser.errors if REFUSED in e]
    assert refused == ["Value 'DRAFT' is not a valid metadata value for 'Status' (Validated by Egeria)"]
