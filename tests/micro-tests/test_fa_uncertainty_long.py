# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""F-A item 3: Absolute/Relative Uncertainty are Java Longs in Egeria.

DataValueSpecificationProperties.java:42-43 (odpi/egeria origin/main 0b7ee0fb) declares both as Long.
The compact spec's Simple Float style sent the probe's "7.5" as a string: a 400 ("Cannot deserialize value
of type java.lang.Long from String") that lost the whole Create Data Value Specification. The spec style
correction (Float -> Int) goes to F-C.
"""
from typing import Any, cast

import pytest

from md_processing.md_processing_utils.typed_properties import not_applied_notes
from md_processing.v2.data_designer import DataValueSpecificationProcessor
from md_processing.v2.extraction import DrECommand


class _DataDesigner:
    def __init__(self):
        self.bodies = []

    async def _async_create_data_value_specification(self, body):
        self.bodies.append(body)
        return "dddddddd-0000-0000-0000-000000000001"


class _Client:
    def __init__(self):
        self.data_designer = _DataDesigner()


async def _async_value(value):
    return value


async def _create(attributes):
    client = _Client()
    p = DataValueSpecificationProcessor(client=cast(Any, client),
                                        command=DrECommand(verb="Create", object_type="Data Value Specification",
                                                           attributes={}, raw_block="## Create Data Value Specification"),
                                        context={})
    p.get_command_spec = lambda: {"OM_TYPE": "DataValueSpecification"}
    p.parsed_output = {"qualified_name": "RTP::DVS", "attributes": {"Display Name": {"value": "RTP DVS"},
                                                                     **attributes}}
    p.as_is_element = None
    p.render_result_markdown = lambda guid: _async_value(guid)

    async def _no_parent(*a, **k):
        return None
    p._sync_value_spec_parent = _no_parent
    await p.apply_changes()
    return client.data_designer.bodies[0]["properties"], p


@pytest.mark.asyncio
async def test_integral_uncertainty_is_sent_as_a_number():
    props, _ = await _create({"Absolute Uncertainty": {"value": "7"}, "Relative Uncertainty": {"value": "7.0"}})
    assert props["absoluteUncertainty"] == 7 and isinstance(props["absoluteUncertainty"], int)
    assert props["relativeUncertainty"] == 7 and isinstance(props["relativeUncertainty"], int)


@pytest.mark.asyncio
async def test_the_probes_7_5_is_refused_with_a_sentence_not_sent():
    props, p = await _create({"Absolute Uncertainty": {"value": "7.5"}, "Relative Uncertainty": {"value": "7.5"}})
    assert props.get("absoluteUncertainty") is None and props.get("relativeUncertainty") is None
    notes = not_applied_notes(p.parsed_output["attributes"])
    assert notes == [
        "not applied: Absolute Uncertainty: '7.5' isn't a whole number; Egeria stores it as an integer",
        "not applied: Relative Uncertainty: '7.5' isn't a whole number; Egeria stores it as an integer"]
