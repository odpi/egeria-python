# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""F-A item 2: template and classification dictionaries go out typed, never raw.

TemplateRequestBody.replacementProperties is the polymorphic EntityProperties and
replacementClassifications / NewElementRequestBody.initialClassifications are
Map<String, ClassificationProperties> (TemplateRequestBody.java:30-31, NewElementRequestBody.java:24,
odpi/egeria origin/main 0b7ee0fb): sent raw (no "class") each was a 400 on the round-trip probe
(Create Element, Create Schema Type/Attribute From Template). The values are the probe's.
"""
from typing import Any, cast

import pytest

from md_processing.v2.asset_maker import AssetMakerProcessor
from md_processing.v2.extraction import DrECommand
from md_processing.v2.schema_maker import SchemaTemplateProcessor, _outer_body

TEMPLATE_GUID = "3f9a0ab3-072c-4cb1-a14f-6e0492e00dd7"


async def _async_value(value):
    return value


class _Recorder:
    def __init__(self):
        self.bodies = []

    async def _async_create_elem_from_template(self, body):
        self.bodies.append(body)
        return "cccccccc-0000-0000-0000-000000000003"

    async def _async_create_schema_type_from_template(self, body):
        self.bodies.append(body)
        return "cccccccc-0000-0000-0000-000000000004"


class _FakeClient:
    def __init__(self):
        self.automated_curation = _Recorder()
        self.schema_maker = _Recorder()


def _processor(cls, object_type, attributes, spec):
    client = _FakeClient()
    p = cls(client=cast(Any, client),
            command=DrECommand(verb="Create", object_type=object_type, attributes={},
                               raw_block=f"## Create {object_type}"), context={})
    p.get_command_spec = lambda: spec
    p.parsed_output = {"qualified_name": None, "attributes": attributes}
    p.render_result_markdown = lambda guid: _async_value(guid)
    return p, client


@pytest.mark.asyncio
async def test_create_element_sends_typed_replacement_properties_and_classifications():
    attributes = {
        "Template GUID": {"value": TEMPLATE_GUID},
        "Element Type Name": {"value": "SchemaType"},
        "Template Properties": {"value": {"description": "d", "rtpKey": "RTP CreateElement TemplateProperties"}},
        "Generic Initial Classifications": {"value": {"Taxonomy": {"organizingPrinciple": "p"},
                                                      "rtpKey": "RTP CreateElement GenericInitialClassifications"}},
    }
    p, client = _processor(AssetMakerProcessor, "Element", attributes, {})
    await p.apply_changes()
    body = client.automated_curation.bodies[0]
    assert body["replacementProperties"] == {"class": "SchemaTypeProperties", "description": "d"}
    assert body["replacementClassifications"] == {"Taxonomy": {"class": "TaxonomyProperties",
                                                               "organizingPrinciple": "p"}}
    assert "initialClassifications" not in body
    warnings = p.parsed_output["warnings"]
    assert "not applied: Template Properties: rtpKey isn't a property of SchemaType" in warnings
    assert any(w.startswith("not applied: Generic Initial Classifications: rtpKey") for w in warnings)


@pytest.mark.asyncio
async def test_create_element_without_a_type_does_not_send_template_properties():
    attributes = {"Template GUID": {"value": TEMPLATE_GUID},
                  "Template Properties": {"value": {"rtpKey": "RTP CreateElement TemplateProperties"}}}
    p, client = _processor(AssetMakerProcessor, "Element", attributes, {})
    await p.apply_changes()
    assert client.automated_curation.bodies[0]["replacementProperties"] is None
    assert any("element type isn't known" in w for w in p.parsed_output["warnings"])


@pytest.mark.asyncio
async def test_schema_type_from_template_types_by_the_command():
    attributes = {"Template GUID": {"value": TEMPLATE_GUID},
                  "Template Properties": {"value": {"rtpKey": "RTP CreateSchemaTypeFromTemplate TemplateProperties",
                                                    "description": "d"}}}
    p, client = _processor(SchemaTemplateProcessor, "Schema Type From Template", attributes,
                           {"OM_TYPE": "SchemaType"})
    await p.apply_changes()
    assert client.schema_maker.bodies[0]["replacementProperties"] == {"class": "SchemaTypeProperties",
                                                                      "description": "d"}
    assert ("not applied: Template Properties: rtpKey isn't a property of SchemaType"
            in p.parsed_output["warnings"])


def test_schema_outer_body_types_initial_classifications():
    attributes = {"Initial Classifications": {"value": {"Taxonomy": {}, "NotAClassification": {}}}}
    body = _outer_body(attributes, {"class": "SchemaTypeProperties"})
    assert body["initialClassifications"] == {"Taxonomy": {"class": "TaxonomyProperties"}}
    assert attributes["Initial Classifications"]["not_applied"] == [
        "not applied: Initial Classifications: NotAClassification isn't an Egeria classification"]
