# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""PY-4: Default Value Override is sent only when the running Egeria's type system declares it.

Egeria's SchemaAttributeProperties declares defaultValueOverride, but the 757a5df0 repository TypeDef for
SchemaAttribute / DisplayDataContainer / DisplayDataField didn't, so sending it failed the whole create
(OMRS-REPOSITORY-400-028). Egeria main c61bad65 declares it (OpenMetadataTypesArchive.java:1095). So the
type definition decides: declared -> sent; not declared -> reported as not applied; unreadable -> reported as
not applied with that reason (undetermined is not absent), and the create still succeeds.
"""
from typing import Any, cast

import pytest

from md_processing.md_processing_utils.typed_properties import not_applied_notes, type_declares_property
from md_processing.v2.extraction import DrECommand
from md_processing.v2.schema_maker import SchemaElementProcessor


class _SchemaMaker:
    def __init__(self):
        self.bodies = []

    def __getattr__(self, name):
        async def call(*args, **kwargs):
            self.bodies.append((name, args, kwargs))
            return "aaaaaaaa-0000-0000-0000-000000000009"
        return call


class _ValidMetadata:
    """Type definitions by name: {name: (super type, [declared attribute names])}; a name left out is unreadable."""

    def __init__(self, types):
        self.types, self.reads = types, []

    async def _async_get_typedef_by_name(self, name):
        self.reads.append(name)
        if name not in self.types:
            return {}
        parent, attributes = self.types[name]
        return {"guid": f"guid-{name}", "name": name, "superType": {"name": parent} if parent else None,
                "attributeDefinitions": [{"attributeName": a} for a in attributes]}


class _Client:
    def __init__(self, types=None):
        self.schema_maker = _SchemaMaker()
        if types is not None:
            self.valid_metadata = _ValidMetadata(types)


async def _async_value(value):
    return value


def _types(declared_on_super):
    return {"SchemaAttribute": ("Referenceable", ["defaultValueOverride"] if declared_on_super else ["position"]),
            "Referenceable": (None, ["qualifiedName"]),
            "DisplayDataField": ("SchemaAttribute", ["inputField"]),
            "DisplayDataContainer": ("SchemaAttribute", ["renderer"])}


async def _create(om_type, client, verb="Create"):
    p = SchemaElementProcessor(client=cast(Any, client),
                               command=DrECommand(verb=verb, object_type=om_type, attributes={},
                                                  raw_block=f"## {verb} {om_type}"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": om_type}
    p.parsed_output = {"qualified_name": f"RTP::{om_type}", "attributes": {
        "Display Name": {"value": f"RTP {om_type}"},
        "Default Value Override": {"value": "RTP DefaultValueOverride"}}}
    p.as_is_element = None
    p.render_result_markdown = lambda guid: _async_value(guid)
    await p.apply_changes()
    return p


@pytest.mark.asyncio
@pytest.mark.parametrize("om_type", ["SchemaAttribute", "DisplayDataContainer", "DisplayDataField"])
async def test_default_value_override_is_sent_when_the_type_declares_it(om_type):
    client = _Client(_types(declared_on_super=True))
    p = await _create(om_type, client)
    (name, args, kwargs), = client.schema_maker.bodies
    assert name == "_async_create_schema_attribute"
    assert args[0]["properties"]["defaultValueOverride"] == "RTP DefaultValueOverride"
    assert not_applied_notes(p.parsed_output["attributes"]) == []


@pytest.mark.asyncio
@pytest.mark.parametrize("om_type", ["SchemaAttribute", "DisplayDataContainer", "DisplayDataField"])
async def test_default_value_override_is_reported_when_the_type_lacks_it(om_type):
    client = _Client(_types(declared_on_super=False))
    p = await _create(om_type, client)
    assert "defaultValueOverride" not in repr(client.schema_maker.bodies)
    assert not_applied_notes(p.parsed_output["attributes"]) == [
        "not applied: Default Value Override: not in this Egeria's type system"]


@pytest.mark.asyncio
async def test_unreadable_type_is_reported_not_guessed():
    client = _Client({})          # no type is readable
    p = await _create("SchemaAttribute", client)
    assert "defaultValueOverride" not in repr(client.schema_maker.bodies)
    assert not_applied_notes(p.parsed_output["attributes"]) == [
        "not applied: Default Value Override: couldn't read SchemaAttribute's type definition to check it"]
    assert client.schema_maker.bodies, "the create must still happen"


@pytest.mark.asyncio
async def test_no_type_lookup_when_default_value_override_is_not_given():
    client = _Client(_types(declared_on_super=True))
    p = SchemaElementProcessor(client=cast(Any, client), command=DrECommand(
        verb="Create", object_type="SchemaAttribute", attributes={}, raw_block="## Create SchemaAttribute"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": "SchemaAttribute"}
    p.parsed_output = {"qualified_name": "RTP::SA", "attributes": {"Display Name": {"value": "RTP"}}}
    p.as_is_element = None
    p.render_result_markdown = lambda guid: _async_value(guid)
    await p.apply_changes()
    assert client.valid_metadata.reads == []


@pytest.mark.asyncio
async def test_type_declares_property_walks_the_super_types_and_never_guesses():
    client = _Client(_types(declared_on_super=True))
    assert await type_declares_property(client, "DisplayDataField", "defaultValueOverride") is True
    assert await type_declares_property(client, "DisplayDataField", "nope") is False
    assert await type_declares_property(_Client({}), "DisplayDataField", "x") is None   # unreadable: can't tell
    assert await type_declares_property(_Client(), "DisplayDataField", "x") is None      # no valid_metadata
