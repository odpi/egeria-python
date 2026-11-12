# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""F-B follow-up: a schema attribute's position and cardinalities belong on its link to the parent.

In Egeria 6 position / minCardinality / maxCardinality are properties of the AttributeForSchema /
NestedSchemaAttribute relationships (AttributeForSchemaProperties, NestedSchemaAttributeProperties; types
archive ~8386/8436, written by OpenMetadataRelationshipBuilder), and the entity's ordered flag is
`orderedValues`. Dr.Egeria sent elementPosition / minCardinality / maxCardinality / isOrderedValues on the
SchemaAttribute entity, where Egeria ignored them (round-trip probe: in the body, not stored).
"""
from typing import Any, cast

import pytest

from md_processing.md_processing_utils.typed_properties import not_applied_notes
from md_processing.v2.extraction import DrECommand
from md_processing.v2.schema_maker import SchemaElementProcessor

PARENT = "7a1c2e5d-0000-0000-0000-00000000000a"


class _SchemaMaker:
    def __init__(self):
        self.bodies = []

    async def _async_create_schema_attribute(self, body):
        self.bodies.append(body)
        return "aaaaaaaa-0000-0000-0000-000000000009"


class _Client:
    def __init__(self):
        self.schema_maker = _SchemaMaker()


async def _async_value(value):
    return value


async def _create(attributes):
    client = _Client()
    p = SchemaElementProcessor(client=cast(Any, client), command=DrECommand(
        verb="Create", object_type="Schema Attribute", attributes={}, raw_block="## Create Schema Attribute"),
        context={})
    p.get_command_spec = lambda: {"OM_TYPE": "SchemaAttribute"}
    p.parsed_output = {"qualified_name": "RTP::SA", "attributes": {"Display Name": {"value": "RTP SA"}, **attributes}}
    p.as_is_element = None
    p.render_result_markdown = lambda guid: _async_value(guid)
    await p.apply_changes()
    return client.schema_maker.bodies[0], p.parsed_output["attributes"]


@pytest.mark.asyncio
async def test_link_properties_go_on_the_parent_relationship():
    body, attributes = await _create({
        "Parent ID": {"value": "RTP::ST", "guid": PARENT},
        "Parent Relationship Type Name": {"value": "AttributeForSchema"},
        "Element Position": {"value": 7}, "Min Cardinality": {"value": "0"}, "Max Cardinality": {"value": 1},
        "Is Ordered Values": {"value": True}})
    props = body["properties"]
    for key in ("elementPosition", "minCardinality", "maxCardinality", "isOrderedValues", "position"):
        assert key not in props
    assert props["orderedValues"] is True
    assert body["parentRelationshipProperties"] == {"class": "AttributeForSchemaProperties", "position": 7,
                                                    "minCardinality": 0, "maxCardinality": 1}
    assert not_applied_notes(attributes) == []


@pytest.mark.asyncio
async def test_without_a_schema_link_they_are_reported():
    body, attributes = await _create({"Element Position": {"value": 7}, "Min Cardinality": {"value": 0}})
    assert body["parentRelationshipProperties"] is None
    notes = not_applied_notes(attributes)
    assert notes == [
        "not applied: Element Position: belongs on the link to the parent; give a Parent ID (Parent Relationship "
        "Type Name AttributeForSchema or NestedSchemaAttribute)",
        "not applied: Min Cardinality: belongs on the link to the parent; give a Parent ID (Parent Relationship "
        "Type Name AttributeForSchema or NestedSchemaAttribute)"]
