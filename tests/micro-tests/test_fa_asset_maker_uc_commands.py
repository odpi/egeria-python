# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""F-A item 5: the UC Server / UC Schema / UC Table Element commands reach their client calls.

The compact spec (and templates, help) name them "UC Server Element" etc.; AssetMakerProcessor matched
only "Unity Catalog Server Element", so the round-trip probe got
"AssetMakerProcessor: unrecognized command" for all three. A command with no mapping now says
"not supported yet", and a missing technology type names itself instead of sending a null template GUID.
"""
from typing import Any, cast

import pytest

from md_processing.v2.asset_maker import AssetMakerProcessor
from md_processing.v2.extraction import DrECommand
from pyegeria import PyegeriaException
from pyegeria.core._globals import NO_ELEMENTS_FOUND
from pyegeria.omvs.automated_curation import AutomatedCuration


class _Curation:
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        async def record(**kwargs):
            self.calls.append((name, kwargs))
            return "eeeeeeee-0000-0000-0000-000000000001"
        return record


class _Client:
    def __init__(self):
        self.automated_curation = _Curation()


async def _async_value(value):
    return value


def _processor(object_type, om_type, attributes):
    client = _Client()
    p = AssetMakerProcessor(client=cast(Any, client),
                            command=DrECommand(verb="Create", object_type=object_type, attributes={},
                                               raw_block=f"## Create {object_type}"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": om_type}
    p.parsed_output = {"qualified_name": None, "attributes": attributes}
    p.render_result_markdown = lambda guid: _async_value(guid)
    return p, client


@pytest.mark.asyncio
@pytest.mark.parametrize("object_type, om_type, method", [
    ("UC Server Element", "SoftwareServer", "_async_create_uc_server_element_from_template"),
    ("UC Schema Element", "DeployedDatabaseSchema", "_async_create_uc_schema_element_from_template"),
    ("UC Table Element", "RelationalTable", "_async_create_uc_table_element_from_template"),
    ("Unity Catalog Server Element", "SoftwareServer", "_async_create_uc_server_element_from_template"),
])
async def test_uc_commands_reach_their_client_call(object_type, om_type, method):
    p, client = _processor(object_type, om_type, {"UC Server Name": {"value": "RTP UC"},
                                                  "UC Catalog Name": {"value": "c"},
                                                  "UC Schema Name": {"value": "s"},
                                                  "UC Table Name": {"value": "t"}})
    await p.apply_changes()
    assert client.automated_curation.calls[0][0] == method


@pytest.mark.asyncio
async def test_unmapped_command_says_not_supported_yet():
    p, _ = _processor("Mystery Element", "MysteryType", {})
    with pytest.raises(ValueError) as exc:
        await p.apply_changes()
    assert "not supported yet" in str(exc.value) and "unrecognized" not in str(exc.value)
    assert "Create Mystery Element" in str(exc.value)


@pytest.mark.asyncio
async def test_missing_technology_type_names_itself():
    client = object.__new__(AutomatedCuration)

    async def no_type(*a, **k):
        return NO_ELEMENTS_FOUND
    client._async_get_tech_type_detail = no_type
    with pytest.raises(PyegeriaException) as exc:
        await client._async_get_template_guid_for_technology_type("Unity Catalog Server")
    assert exc.value.message == ("No technology type 'Unity Catalog Server' on this Egeria server, so there is "
                                 "no catalog template to create from.")


@pytest.mark.asyncio
async def test_technology_type_without_a_template_names_itself():
    client = object.__new__(AutomatedCuration)

    async def no_templates(*a, **k):
        return {"catalogTemplates": []}
    client._async_get_tech_type_detail = no_templates
    with pytest.raises(PyegeriaException) as exc:
        await client._async_get_template_guid_for_technology_type("PostgreSQL Server")
    assert "No catalog template is registered for technology type 'PostgreSQL Server'" in exc.value.message
