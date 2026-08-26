# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
ISSUE-48 (PYEGERIA_ISSUES.md): "Link/Detach Schema Attribute Definition"
originally shipped via Option 2 -- the generic MetadataExpert relationship
mechanism -- as a stopgap while no bespoke Egeria REST endpoint existed for
the SchemaAttributeDefinition relationship. That's no longer true:
DataDesigner._async_link_schema_attribute_definition/
_async_detach_schema_attribute_definition (added 2026-08-21, verified
against a live 6.2-SNAPSHOT server's /v3/api-docs) now wrap the real
endpoint directly, and LinkSchemaAttributeDefinitionProcessor was migrated
to call them (Option 1) -- see md_processing/v2/data_designer.py's
LinkSchemaAttributeDefinitionProcessor docstring. This test exercises that
current call path; it previously stubbed the retired MetadataExpert path
and went stale when the processor migrated off it.

No live server needed: a fake client captures the outgoing calls.
"""
from typing import Any, cast

import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.data_designer import LinkSchemaAttributeDefinitionProcessor

DATA_FIELD_GUID = "aaaaaaaa-0000-0000-0000-000000000001"
SCHEMA_ATTRIBUTE_GUID = "bbbbbbbb-0000-0000-0000-000000000002"


class _FakeDataDesigner:
    def __init__(self):
        self.link_calls = []
        self.detach_calls = []

    async def _async_link_schema_attribute_definition(self, data_field_guid, schema_attribute_guid, body=None):
        self.link_calls.append((data_field_guid, schema_attribute_guid, body))

    async def _async_detach_schema_attribute_definition(self, data_field_guid, schema_attribute_guid,
                                                         body=None, cascade_delete=False):
        self.detach_calls.append((data_field_guid, schema_attribute_guid, body, cascade_delete))


class _FakeClient:
    def __init__(self):
        self.data_designer = _FakeDataDesigner()


def _command(verb: str) -> DrECommand:
    return DrECommand(verb=verb, object_type="Schema Attribute Definition", attributes={},
                       raw_block=f"# {verb} Schema Attribute Definition")


def _attributes():
    return {
        "Data Field": {"guid": DATA_FIELD_GUID, "value": "DataField::Test::Field"},
        "Schema Attribute": {"guid": SCHEMA_ATTRIBUTE_GUID, "value": "SchemaAttribute::Test::Column"},
    }


@pytest.mark.asyncio
async def test_link_calls_data_designer_with_correct_guids_and_body():
    client = _FakeClient()
    p = LinkSchemaAttributeDefinitionProcessor(client=cast(Any, client), command=_command("Link"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": "SchemaAttributeDefinition"}
    p.parsed_output = {"qualified_name": None, "attributes": _attributes()}

    result = await p.apply_changes()

    assert len(client.data_designer.link_calls) == 1
    data_field_guid, schema_attribute_guid, body = client.data_designer.link_calls[0]
    assert data_field_guid == DATA_FIELD_GUID
    assert schema_attribute_guid == SCHEMA_ATTRIBUTE_GUID
    assert body["class"] == "NewRelationshipRequestBody"
    assert body["properties"]["class"] == "SchemaAttributeDefinitionProperties"
    assert DATA_FIELD_GUID in result and SCHEMA_ATTRIBUTE_GUID in result


@pytest.mark.asyncio
async def test_link_without_both_guids_raises():
    client = _FakeClient()
    p = LinkSchemaAttributeDefinitionProcessor(client=cast(Any, client), command=_command("Link"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": "SchemaAttributeDefinition"}
    p.parsed_output = {"qualified_name": None, "attributes": {"Data Field": {"guid": DATA_FIELD_GUID}}}

    with pytest.raises(ValueError, match="Schema Attribute"):
        await p.apply_changes()

    assert client.data_designer.link_calls == []


@pytest.mark.asyncio
async def test_detach_calls_data_designer_directly_with_no_relationship_lookup():
    client = _FakeClient()
    p = LinkSchemaAttributeDefinitionProcessor(client=cast(Any, client), command=_command("Detach"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": "SchemaAttributeDefinition"}
    p.parsed_output = {"qualified_name": None, "attributes": _attributes()}

    result = await p.apply_changes()

    assert client.data_designer.detach_calls == [(DATA_FIELD_GUID, SCHEMA_ATTRIBUTE_GUID, None, False)]
    assert DATA_FIELD_GUID in result and SCHEMA_ATTRIBUTE_GUID in result


@pytest.mark.asyncio
async def test_detach_without_both_guids_raises():
    client = _FakeClient()
    p = LinkSchemaAttributeDefinitionProcessor(client=cast(Any, client), command=_command("Detach"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": "SchemaAttributeDefinition"}
    p.parsed_output = {"qualified_name": None, "attributes": {"Schema Attribute": {"guid": SCHEMA_ATTRIBUTE_GUID}}}

    with pytest.raises(ValueError, match="Data Field"):
        await p.apply_changes()

    assert client.data_designer.detach_calls == []


def test_supports_target_element_lookup_is_false():
    # Relationship-only processor -- see ISSUE-68's AsyncBaseCommandProcessor
    # upsert-rewrite bug (processors.py) for why this matters.
    client = _FakeClient()
    p = LinkSchemaAttributeDefinitionProcessor(client=cast(Any, client), command=_command("Link"), context={})
    assert p.supports_target_element_lookup() is False
