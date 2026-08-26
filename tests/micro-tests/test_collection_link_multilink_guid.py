# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Multi-link GUID handling for CollectionLinkProcessor's Agreement Item /
Agreement Actor / Product Dependency Link and Detach branches (ISSUE-68
follow-up).

AgreementItem, AgreementActor, and DigitalProductDependency are all
MULTI_LINK relationship types (see pyegeria.core.relationship_multiplicity)
-- more than one instance can exist between the same pair of elements. This
processor's Link branches previously discarded the relationship GUID that
_async_link_agreement_item / _async_link_agreement_actor /
_async_link_digital_product_dependency return, and its Detach branches had
no way to target a specific instance: AgreementItem/DigitalProductDependency
went straight to a pair-based (ambiguous) detach call, and AgreementActor
fell back to a first-match pair lookup. This confirms:
  - the create-time relationship GUID is now captured into
    parsed_output["guid"] and shown in the result markdown;
  - supplying an explicit "GUID" attribute on Detach routes to the
    relationship-GUID-targeted detach method (_by_id for
    AgreementItem/DigitalProductDependency, direct guid for AgreementActor);
  - omitting it preserves the old pair-based fallback behavior.

No live server needed: a fake client stands in for the OMVS layer.
"""
from typing import Any, cast

import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.collection_manager_processor import CollectionLinkProcessor

ITEM_REL_GUID = "agreement-item-rel-guid-0001"
ACTOR_REL_GUID = "agreement-actor-rel-guid-0001"
DEPENDENCY_REL_GUID = "product-dependency-rel-guid-0001"


class _FakeClient:
    def __init__(self):
        self.link_item_calls = []
        self.link_actor_calls = []
        self.link_dependency_calls = []
        self.detach_item_calls = []
        self.detach_item_by_id_calls = []
        self.detach_actor_calls = []
        self.detach_dependency_calls = []
        self.detach_dependency_by_id_calls = []

    async def _async_link_agreement_item(self, agreement_guid, item_guid, body):
        self.link_item_calls.append((agreement_guid, item_guid, body))
        return ITEM_REL_GUID

    async def _async_link_agreement_actor(self, agreement_guid, actor_guid, body):
        self.link_actor_calls.append((agreement_guid, actor_guid, body))
        return ACTOR_REL_GUID

    async def _async_link_digital_product_dependency(self, guid1, guid2, body):
        self.link_dependency_calls.append((guid1, guid2, body))
        return DEPENDENCY_REL_GUID

    async def _async_detach_agreement_item(self, agreement_guid, item_guid, body):
        self.detach_item_calls.append((agreement_guid, item_guid, body))

    async def _async_detach_agreement_item_by_id(self, rel_guid, body):
        self.detach_item_by_id_calls.append((rel_guid, body))

    async def _async_detach_agreement_actor(self, rel_guid, body):
        self.detach_actor_calls.append((rel_guid, body))

    async def _async_detach_digital_product_dependency(self, guid1, guid2, body):
        self.detach_dependency_calls.append((guid1, guid2, body))

    async def _async_detach_digital_product_dependency_by_id(self, rel_guid, body):
        self.detach_dependency_by_id_calls.append((rel_guid, body))

    async def _async_get_relationships(self, *args, **kwargs):
        # Not exercised when an explicit GUID is supplied; used only by the
        # legacy first-match resolver fallback path.
        return []


def _command(verb: str, object_type: str) -> DrECommand:
    return DrECommand(verb=verb, object_type=object_type, attributes={},
                       raw_block=f"# {verb} {object_type}")


def _processor(client, verb, object_type, attributes):
    p = CollectionLinkProcessor(client=cast(Any, client), command=_command(verb, object_type), context={})
    p.canonical_object_type = object_type
    p.parsed_output = {"qualified_name": f"{object_type}::test::1", "attributes": attributes}
    return p


@pytest.mark.asyncio
async def test_link_agreement_item_returns_and_displays_relationship_guid():
    client = _FakeClient()
    p = _processor(client, "Link", "Agreement Item", {
        "Agreement Name": {"guid": "agreement-guid"},
        "Item Name": {"guid": "item-guid"},
    })

    result = await p.apply_changes()

    assert len(client.link_item_calls) == 1
    assert client.link_item_calls[0][:2] == ("agreement-guid", "item-guid")
    assert p.parsed_output["guid"] == ITEM_REL_GUID
    assert ITEM_REL_GUID in result


@pytest.mark.asyncio
async def test_link_agreement_actor_returns_and_displays_relationship_guid():
    client = _FakeClient()
    p = _processor(client, "Link", "Agreement Actor", {
        "Agreement Name": {"guid": "agreement-guid"},
        "Actors": {"guid": "actor-guid"},
    })

    result = await p.apply_changes()

    assert len(client.link_actor_calls) == 1
    assert p.parsed_output["guid"] == ACTOR_REL_GUID
    assert ACTOR_REL_GUID in result


@pytest.mark.asyncio
async def test_link_product_dependency_returns_and_displays_relationship_guid():
    client = _FakeClient()
    p = _processor(client, "Link", "Product Dependency", {
        "Digital Product 1": {"guid": "product-1-guid"},
        "Digital Product 2": {"guid": "product-2-guid"},
    })

    result = await p.apply_changes()

    assert len(client.link_dependency_calls) == 1
    assert p.parsed_output["guid"] == DEPENDENCY_REL_GUID
    assert DEPENDENCY_REL_GUID in result


@pytest.mark.asyncio
async def test_detach_agreement_item_with_explicit_guid_uses_by_id():
    client = _FakeClient()
    p = _processor(client, "Detach", "Agreement Item", {
        "Agreement Name": {"guid": "agreement-guid"},
        "Item Name": {"guid": "item-guid"},
        "GUID": {"value": ITEM_REL_GUID},
    })

    await p.apply_changes()

    assert client.detach_item_by_id_calls == [(ITEM_REL_GUID, client.detach_item_by_id_calls[0][1])]
    assert client.detach_item_calls == []


@pytest.mark.asyncio
async def test_detach_agreement_item_without_guid_falls_back_to_pair_based():
    client = _FakeClient()
    p = _processor(client, "Detach", "Agreement Item", {
        "Agreement Name": {"guid": "agreement-guid"},
        "Item Name": {"guid": "item-guid"},
    })

    await p.apply_changes()

    assert client.detach_item_calls == [("agreement-guid", "item-guid", client.detach_item_calls[0][2])]
    assert client.detach_item_by_id_calls == []


@pytest.mark.asyncio
async def test_detach_product_dependency_with_explicit_guid_uses_by_id():
    client = _FakeClient()
    p = _processor(client, "Detach", "Product Dependency", {
        "Digital Product 1": {"guid": "product-1-guid"},
        "Digital Product 2": {"guid": "product-2-guid"},
        "GUID": {"value": DEPENDENCY_REL_GUID},
    })

    await p.apply_changes()

    assert client.detach_dependency_by_id_calls == [
        (DEPENDENCY_REL_GUID, client.detach_dependency_by_id_calls[0][1])
    ]
    assert client.detach_dependency_calls == []


@pytest.mark.asyncio
async def test_detach_agreement_actor_with_explicit_guid_skips_resolver():
    client = _FakeClient()
    p = _processor(client, "Detach", "Agreement Actor", {
        "Agreement Name": {"guid": "agreement-guid"},
        "Actors": {"guid": "actor-guid"},
        "GUID": {"value": ACTOR_REL_GUID},
    })

    await p.apply_changes()

    assert client.detach_actor_calls == [(ACTOR_REL_GUID, client.detach_actor_calls[0][1])]
