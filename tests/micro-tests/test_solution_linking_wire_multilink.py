# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Multi-link support for SolutionLinkingWire (Dr.Egeria "Link Solution Components").

SolutionLinkingWire allows more than one wire between the same ordered pair of
components (Egeria PR #9156), so surfacing the new relationship's own GUID on
create matters -- it's the only way to target that specific wire later via
Update/Detach. Previously `_async_new_relationship_request` discarded the
GUID Egeria's create endpoints return (`{"class": "GUIDResponse", "guid":
"..."}`), so `SolutionLinkProcessor.apply_changes()`'s brand-new-wire branch
fell through to a generic "Linked X to Y" message with no GUID shown, unlike
the sibling "Updated existing wire" branch. Confirms both:
  1. `_async_link_solution_linking_wire` (the SDK method) returns the GUID.
  2. `SolutionLinkProcessor.apply_changes()` captures it into
     `parsed_output["guid"]` and displays it in the result markdown.

No live server needed: a fake client stands in for the OMVS layer.
"""
from typing import Any, cast

import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.solution_architect import SolutionLinkProcessor

NEW_WIRE_GUID = "a1b2c3d4-0000-1111-2222-333344445555"
EXISTING_WIRE_GUID = "existing-wire-guid-0001"


class _FakeClient:
    def __init__(self, existing_wires=None):
        self.link_calls = []
        self.update_calls = []
        self._existing_wires = existing_wires or []

    async def _async_link_solution_linking_wire(self, component1_guid, component2_guid, body):
        self.link_calls.append((component1_guid, component2_guid, body))
        return NEW_WIRE_GUID

    async def _async_update_solution_linking_wire(self, wire_guid, body):
        self.update_calls.append((wire_guid, body))

    async def _async_find_relationships_between_elements(self, body):
        return self._existing_wires


def _command(verb: str) -> DrECommand:
    return DrECommand(verb=verb, object_type="Solution Components", attributes={},
                       raw_block=f"# {verb} Solution Components")


def _base_attributes(label=None):
    attrs = {
        "Component1": {"guid": "comp-1-guid", "value": "Comp1"},
        "Component2": {"guid": "comp-2-guid", "value": "Comp2"},
    }
    if label is not None:
        attrs["Label"] = {"value": label}
    return attrs


@pytest.mark.asyncio
async def test_create_new_solution_linking_wire_returns_and_displays_guid():
    client = _FakeClient()
    p = SolutionLinkProcessor(client=cast(Any, client), command=_command("Link"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": "SolutionLinkingWire", "custom_attributes": ["Component1", "Component2"]}
    p.parsed_output = {
        "qualified_name": "SolutionLinkingWire::test::1",
        "attributes": _base_attributes(label="unique-label-1"),
    }

    result = await p.apply_changes()

    assert len(client.link_calls) == 1
    assert client.link_calls[0][0] == "comp-1-guid"
    assert client.link_calls[0][1] == "comp-2-guid"
    # The new wire's own GUID must be surfaced, not silently discarded.
    assert p.parsed_output["guid"] == NEW_WIRE_GUID
    assert NEW_WIRE_GUID in result
    assert "Created wire" in result


@pytest.mark.asyncio
async def test_relink_existing_labeled_wire_updates_in_place_not_create():
    existing = [{
        "elementGUIDAtEnd1": "comp-1-guid",
        "elementGUIDAtEnd2": "comp-2-guid",
        "relationshipGUID": EXISTING_WIRE_GUID,
        "relationshipProperties": {"label": "unique-label-1"},
    }]
    client = _FakeClient(existing_wires=existing)
    p = SolutionLinkProcessor(client=cast(Any, client), command=_command("Link"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": "SolutionLinkingWire", "custom_attributes": ["Component1", "Component2"]}
    p.parsed_output = {
        "qualified_name": "SolutionLinkingWire::test::1",
        "attributes": _base_attributes(label="unique-label-1"),
    }

    result = await p.apply_changes()

    assert len(client.link_calls) == 0
    assert len(client.update_calls) == 1
    assert client.update_calls[0][0] == EXISTING_WIRE_GUID
    assert EXISTING_WIRE_GUID in result
    assert "Updated wire" in result
