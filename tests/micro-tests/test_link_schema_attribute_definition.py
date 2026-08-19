# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
ISSUE-48 (PYEGERIA_ISSUES.md): new "Link/Detach Schema Attribute Definition"
Dr.Egeria command, implemented via Option 2 -- the generic MetadataExpert
relationship mechanism (_async_create_related_elements/
_async_delete_related_elements, typeName-based) rather than a dedicated
wrapper method, since no bespoke Egeria REST endpoint exists yet for the
SchemaAttributeDefinition relationship (confirmed live against the server's
full OpenAPI spec). Replace LinkSchemaAttributeDefinitionProcessor's
implementation with a bespoke DataDesigner wrapper once Egeria ships one.

No live server needed: a fake client captures the outgoing calls.
"""
from typing import Any, cast

import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.data_designer import LinkSchemaAttributeDefinitionProcessor

DATA_FIELD_GUID = "aaaaaaaa-0000-0000-0000-000000000001"
SCHEMA_ATTRIBUTE_GUID = "bbbbbbbb-0000-0000-0000-000000000002"
REL_GUID = "cccccccc-0000-0000-0000-000000000003"


class _FakeMetadataExpert:
    def __init__(self, existing_relationships=None):
        self.create_calls = []
        self.delete_calls = []
        self._existing = existing_relationships if existing_relationships is not None else "No elements found"

    async def _async_create_related_elements(self, body):
        self.create_calls.append(body)
        return REL_GUID

    async def _async_find_relationships_between_elements(self, body):
        return self._existing

    async def _async_delete_related_elements(self, relationship_guid, body):
        self.delete_calls.append((relationship_guid, body))


class _FakeClient:
    def __init__(self, existing_relationships=None):
        self.metadata_expert = _FakeMetadataExpert(existing_relationships)


def _command(verb: str) -> DrECommand:
    return DrECommand(verb=verb, object_type="Schema Attribute Definition", attributes={},
                       raw_block=f"# {verb} Schema Attribute Definition")


def _attributes():
    return {
        "Data Field": {"guid": DATA_FIELD_GUID, "value": "DataField::Test::Field"},
        "Schema Attribute": {"guid": SCHEMA_ATTRIBUTE_GUID, "value": "SchemaAttribute::Test::Column"},
    }


@pytest.mark.asyncio
async def test_link_creates_generic_related_elements_and_displays_guid():
    client = _FakeClient()
    p = LinkSchemaAttributeDefinitionProcessor(client=cast(Any, client), command=_command("Link"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": "SchemaAttributeDefinition"}
    p.parsed_output = {"qualified_name": None, "attributes": _attributes()}

    result = await p.apply_changes()

    assert len(client.metadata_expert.create_calls) == 1
    body = client.metadata_expert.create_calls[0]
    assert body["typeName"] == "SchemaAttributeDefinition"
    assert body["metadataElement1GUID"] == DATA_FIELD_GUID
    assert body["metadataElement2GUID"] == SCHEMA_ATTRIBUTE_GUID
    assert p.parsed_output["guid"] == REL_GUID
    assert REL_GUID in result


@pytest.mark.asyncio
async def test_link_without_both_guids_raises():
    client = _FakeClient()
    p = LinkSchemaAttributeDefinitionProcessor(client=cast(Any, client), command=_command("Link"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": "SchemaAttributeDefinition"}
    p.parsed_output = {"qualified_name": None, "attributes": {"Data Field": {"guid": DATA_FIELD_GUID}}}

    with pytest.raises(ValueError, match="Schema Attribute"):
        await p.apply_changes()


@pytest.mark.asyncio
async def test_detach_looks_up_relationship_guid_by_element_pair_then_deletes():
    existing = {
        "relationships": [
            {"relationshipGUID": REL_GUID, "elementGUIDAtEnd1": DATA_FIELD_GUID, "elementGUIDAtEnd2": SCHEMA_ATTRIBUTE_GUID},
        ]
    }
    client = _FakeClient(existing_relationships=existing)
    p = LinkSchemaAttributeDefinitionProcessor(client=cast(Any, client), command=_command("Detach"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": "SchemaAttributeDefinition"}
    p.parsed_output = {"qualified_name": None, "attributes": _attributes()}

    result = await p.apply_changes()

    assert client.metadata_expert.delete_calls == [(REL_GUID, {"class": "DeleteRelationshipRequestBody"})]
    assert REL_GUID in result


@pytest.mark.asyncio
async def test_detach_with_no_existing_relationship_raises():
    client = _FakeClient(existing_relationships="No elements found")
    p = LinkSchemaAttributeDefinitionProcessor(client=cast(Any, client), command=_command("Detach"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": "SchemaAttributeDefinition"}
    p.parsed_output = {"qualified_name": None, "attributes": _attributes()}

    with pytest.raises(ValueError, match="no existing relationship found"):
        await p.apply_changes()


def test_supports_target_element_lookup_is_false():
    # Relationship-only processor -- see ISSUE-68's AsyncBaseCommandProcessor
    # upsert-rewrite bug (processors.py) for why this matters.
    client = _FakeClient()
    p = LinkSchemaAttributeDefinitionProcessor(client=cast(Any, client), command=_command("Link"), context={})
    assert p.supports_target_element_lookup() is False
