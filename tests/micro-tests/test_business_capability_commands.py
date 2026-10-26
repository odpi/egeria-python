# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Dr.Egeria support for the 0715 Digital Business model: Business Capability (a
Collection subtype) and its BusinessCapabilityDependency / DigitalSupport
relationships. Requested by Mandy Chessell, 2026-10-24.

Confirms:
  - Create/Update Business Capability route to CollectionManagerProcessor and
    send businessCapabilityType / businessImplementationType;
  - the four Link/Detach commands route to CollectionLinkProcessor and call the
    DigitalBusiness SDK methods with the ends in the right order.

No live server needed: a fake client stands in for the OMVS layer.
"""
from typing import Any, cast

import pytest

from md_processing.md_processing_utils.common_md_utils import set_collection_manager_body
from md_processing.md_processing_utils.md_processing_constants import COLLECTION_SUBTYPES
from md_processing.v2.collection_manager_processor import CollectionLinkProcessor
from md_processing.v2.extraction import DrECommand


class _FakeClient:
    def __init__(self):
        self.calls = []

    async def _async_link_business_capability_dependency(self, bc_guid, supporting_guid, body):
        self.calls.append(("link_dependency", bc_guid, supporting_guid, body))

    async def _async_detach_business_capability_dependency(self, bc_guid, supporting_guid, body):
        self.calls.append(("detach_dependency", bc_guid, supporting_guid, body))

    async def _async_link_digital_support(self, bc_guid, element_guid, body):
        self.calls.append(("link_support", bc_guid, element_guid, body))

    async def _async_detach_digital_support(self, bc_guid, element_guid, body):
        self.calls.append(("detach_support", bc_guid, element_guid, body))


def _processor(client, verb, object_type, attributes):
    command = DrECommand(verb=verb, object_type=object_type, attributes={}, raw_block=f"# {verb} {object_type}")
    p = CollectionLinkProcessor(client=cast(Any, client), command=command, context={})
    p.canonical_object_type = object_type
    p.parsed_output = {"qualified_name": f"{object_type}::test::1", "attributes": attributes}
    return p


def test_business_capability_is_a_collection_subtype():
    assert "Business Capability" in COLLECTION_SUBTYPES


def test_business_capability_body_carries_its_own_properties():
    body = set_collection_manager_body("BusinessCapability", "BusinessCapability::bc1", {
        "Display Name": {"value": "Order Management"},
        "Business Capability Type": {"value": "BUSINESS_AREA"},
        "Business Implementation Type": {"value": "organization"},
    })
    assert body["class"] == "BusinessCapabilityProperties"
    assert body["businessCapabilityType"] == "BUSINESS_AREA"
    assert body["businessImplementationType"] == "organization"


@pytest.mark.asyncio
async def test_link_business_capability_dependency_sends_ends_in_order():
    client = _FakeClient()
    p = _processor(client, "Link", "Business Capability Dependency", {
        "Dependent Capability": {"guid": "bc1-guid"},
        "Supporting Capability": {"guid": "bc2-guid"},
        "Label": {"value": "needs-payments"},
    })

    await p.apply_changes()

    name, end1, end2, body = client.calls[0]
    assert (name, end1, end2) == ("link_dependency", "bc1-guid", "bc2-guid")
    assert body["properties"]["class"] == "BusinessCapabilityDependencyProperties"
    assert body["properties"]["label"] == "needs-payments"


@pytest.mark.asyncio
async def test_detach_business_capability_dependency():
    client = _FakeClient()
    p = _processor(client, "Detach", "Business Capability Dependency", {
        "Dependent Capability": {"guid": "bc1-guid"},
        "Supporting Capability": {"guid": "bc2-guid"},
    })

    await p.apply_changes()

    assert client.calls[0][:3] == ("detach_dependency", "bc1-guid", "bc2-guid")


@pytest.mark.asyncio
async def test_link_and_detach_digital_support():
    client = _FakeClient()
    attributes = {
        "Supported Capability": {"guid": "bc1-guid"},
        "Digital Service": {"guid": "service-guid"},
    }

    await _processor(client, "Link", "Digital Support", attributes).apply_changes()
    await _processor(client, "Detach", "Digital Support", attributes).apply_changes()

    assert client.calls[0][:3] == ("link_support", "bc1-guid", "service-guid")
    assert client.calls[0][3]["properties"]["class"] == "DigitalSupportProperties"
    assert client.calls[1][:3] == ("detach_support", "bc1-guid", "service-guid")
