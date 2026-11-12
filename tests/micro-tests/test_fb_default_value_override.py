# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""F-B group 9: Default Value Override isn't in this Egeria's type system, so it isn't sent.

Egeria's SchemaAttributeProperties declares defaultValueOverride and its builder writes it, but the 757a5df0
repository TypeDef for SchemaAttribute / DisplayDataContainer / DisplayDataField doesn't have it: sending it
failed the whole create (OMRS-REPOSITORY-400-028; round-trip probe, PostgreSQL scratch). Until Egeria declares
it, Dr.Egeria leaves it out and says so, and the create succeeds.
"""
from typing import Any, cast

import pytest

from md_processing.md_processing_utils.typed_properties import not_applied_notes
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


class _Client:
    def __init__(self):
        self.schema_maker = _SchemaMaker()


async def _async_value(value):
    return value


@pytest.mark.asyncio
@pytest.mark.parametrize("om_type", ["SchemaAttribute", "DisplayDataContainer", "DisplayDataField"])
async def test_default_value_override_is_reported_not_sent(om_type):
    client = _Client()
    p = SchemaElementProcessor(client=cast(Any, client),
                               command=DrECommand(verb="Create", object_type=om_type, attributes={},
                                                  raw_block=f"## Create {om_type}"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": om_type}
    p.parsed_output = {"qualified_name": f"RTP::{om_type}", "attributes": {
        "Display Name": {"value": f"RTP {om_type}"},
        "Default Value Override": {"value": "RTP CreateSchemaAttribute DefaultValueOverride"}}}
    p.as_is_element = None
    p.render_result_markdown = lambda guid: _async_value(guid)
    await p.apply_changes()
    sent = repr(client.schema_maker.bodies)
    assert "defaultValueOverride" not in sent and "DefaultValueOverride" not in sent
    assert not_applied_notes(p.parsed_output["attributes"]) == [
        "not applied: Default Value Override: not in this Egeria's type system"]
