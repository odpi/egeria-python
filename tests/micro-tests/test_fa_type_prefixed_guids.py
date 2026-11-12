# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""F-A item 8: Egeria GUIDs are opaque; the in-memory repository returns "<TypeName>-<uuid>".

extract_guid_or_raise accepted only hex/dashes, so on the round-trip probe (scratch 757a5df0) 213 Create
summary rows read "Execution failed: ValueError: Create X did not return a GUID string" for elements
Egeria had created -- and every post-create step (zones, governance classifications, parent links, the
element cache, journal entries) was skipped. The same assumption sat in resolve_element_guid,
action_author and governance._normalize_guid.
"""
from typing import Any, cast

import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.governance import GovernanceLinkProcessor
from md_processing.v2.processors import AsyncBaseCommandProcessor
from pyegeria.core.utils import is_guid, is_guid_reference

PREFIXED = "Glossary-5d2a1857-27fb-4615-aaae-e90e362f09b5"  # what create_glossary returned on 757a5df0
PLAIN = "5d2a1857-27fb-4615-aaae-e90e362f09b5"


@pytest.mark.parametrize("value, expected", [
    (PREFIXED, True), (PLAIN, True), ("Report-799ded80-1830-4952-9e4b-7fc17c3863e4", True),
    ("opaque-guid-7", True),  # opaque: no hex or UUID shape assumed
    ("GUIDResponse", False), ("No elements found", False), ("two words", False), ("", False), (None, False),
    ("ThreatDefinition::bad", False),
])
def test_is_guid_is_opaque(value, expected):
    assert is_guid(value) is expected


@pytest.mark.parametrize("value, expected", [
    (PREFIXED, True), (PLAIN, True), ("RTP::Diag::Glossary1", False), ("opaque-guid-7", False),
    ("Glossary-", False), ("No elements found", False),
])
def test_is_guid_reference_tells_a_guid_from_a_name(value, expected):
    assert is_guid_reference(value) is expected


class _Probe(AsyncBaseCommandProcessor):
    async def apply_changes(self):
        return ""


def _processor(cls=_Probe):
    return cls(client=cast(Any, object()),
               command=DrECommand(verb="Create", object_type="Glossary", attributes={}, raw_block="## Create Glossary"),
               context={})


@pytest.mark.parametrize("raw", [PREFIXED, f"  {PREFIXED} ", {"guid": PREFIXED}, {"elementHeader": {"guid": PREFIXED}},
                                 [PREFIXED], PLAIN])
def test_extract_guid_accepts_type_prefixed_guids(raw):
    assert _processor().extract_guid_or_raise(raw, "Create Glossary") in (PREFIXED, PLAIN)


def test_extract_guid_still_refuses_descriptive_strings():
    with pytest.raises(ValueError):
        _processor().extract_guid_or_raise("No elements found", "Create Glossary")


@pytest.mark.asyncio
async def test_resolve_element_guid_returns_a_prefixed_guid_as_is():
    assert await _processor().resolve_element_guid(PREFIXED) == PREFIXED


def test_governance_normalize_guid_accepts_prefixed():
    assert GovernanceLinkProcessor._normalize_guid(PREFIXED) == PREFIXED
    assert GovernanceLinkProcessor._normalize_guid("RTP::Not::A::Guid") is None
