# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
TemplateRequestBody.deep_copy used to default to False, while Egeria's
TemplateOptions defaults deepCopy to true. Every create-from-template body is
validated through the model and serialised with exclude_none=True, so a caller
that never mentioned deepCopy sent "deepCopy": false -- and Egeria created the
element without any of the template's anchored attachments (e.g. a PostgreSQL
data set with no connection). An unset value must now be left out, so
Egeria's own default applies.
"""
import json
from typing import Any, cast

import pytest
from pydantic import TypeAdapter

from md_processing.v2.asset_maker import AssetMakerProcessor
from md_processing.v2.extraction import DrECommand
from pyegeria.models import TemplateRequestBody

ADAPTER = TypeAdapter(TemplateRequestBody)
TEMPLATE_GUID = "3f9a0ab3-072c-4cb1-a14f-6e0492e00dd7"


def _serialised(body: dict) -> dict:
    # Mirrors _async_create_element_from_template's validate + dump.
    return json.loads(ADAPTER.validate_python(body).model_dump_json(exclude_none=True, by_alias=True))


def test_unset_deep_copy_is_left_to_egeria_default():
    sent = _serialised({"class": "TemplateRequestBody", "templateGUID": TEMPLATE_GUID})
    assert "deepCopy" not in sent


@pytest.mark.parametrize("value", [True, False])
def test_explicit_deep_copy_is_sent(value):
    sent = _serialised({"class": "TemplateRequestBody", "templateGUID": TEMPLATE_GUID, "deepCopy": value})
    assert sent["deepCopy"] is value


class _FakeCuration:
    def __init__(self):
        self.bodies = []

    async def _async_create_elem_from_template(self, body):
        self.bodies.append(body)
        return "cccccccc-0000-0000-0000-000000000003"


class _FakeClient:
    def __init__(self):
        self.automated_curation = _FakeCuration()


@pytest.mark.asyncio
@pytest.mark.parametrize("attributes, expected", [
    ({}, None),
    ({"Deep Copy": {"value": False}}, False),
    ({"Deep Copy": {"value": True}}, True),
])
async def test_create_element_maps_deep_copy(attributes, expected):
    client = _FakeClient()
    p = AssetMakerProcessor(client=cast(Any, client),
                            command=DrECommand(verb="Create", object_type="Element", attributes={},
                                               raw_block="## Create Element"), context={})
    p.get_command_spec = lambda: {}
    p.parsed_output = {"qualified_name": None,
                       "attributes": {"Template GUID": {"value": TEMPLATE_GUID}, **attributes}}
    p.render_result_markdown = lambda guid: _async_value(guid)

    await p.apply_changes()

    assert client.automated_curation.bodies[0]["deepCopy"] is expected


async def _async_value(value):
    return value
