# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Unit tests for relationship_multiplicity.async_find_matching_relationship, which
lets Dr.Egeria's multi-link Link commands update the instance a re-run describes
instead of creating a duplicate.

The fake mirrors what MetadataExpert._async_find_relationships_between_elements
really returns: the relationshipList envelope {"relationships": [...], ...} with
properties in OMRS propertyValueMap form, or a "No elements returned" string.
"""
import pytest

from pyegeria.core.relationship_multiplicity import async_find_matching_relationship

pytestmark = pytest.mark.unit


def omrs_rel(guid, end1, end2, **props):
    return {
        "relationshipGUID": guid,
        "elementGUIDAtEnd1": end1,
        "elementGUIDAtEnd2": end2,
        "relationshipProperties": {
            "class": "ElementProperties",
            "propertyValueMap": {
                k: {"class": "PrimitiveTypePropertyValue", "typeName": "string", "primitiveValue": v}
                for k, v in props.items()
            },
        },
    }


class _FakeClient:
    def __init__(self, result):
        self.result = result
        self.bodies = []

    async def _async_find_relationships_between_elements(self, body):
        self.bodies.append(body)
        return self.result


def envelope(*rels):
    return {"relationships": list(rels), "mermaidGraph": "flowchart LR"}


@pytest.mark.asyncio
async def test_matches_real_envelope_and_property_value_map():
    client = _FakeClient(envelope(
        omrs_rel("other-label", "p1", "p2", label="feeds", iscQualifiedName="ISC::B"),
        omrs_rel("wanted", "p1", "p2", label="feeds", iscQualifiedName="ISC::A"),
    ))

    guid = await async_find_matching_relationship(
        client, "DigitalProductDependency", "p1", "p2", {"label": "feeds", "iscQualifiedName": "ISC::A"})

    assert guid == "wanted"


@pytest.mark.asyncio
async def test_search_is_narrowed_on_server_by_non_null_properties():
    client = _FakeClient("No elements returned")

    await async_find_matching_relationship(
        client, "DigitalProductDependency", "p1", "p2", {"label": "feeds", "iscQualifiedName": None})

    body = client.bodies[0]
    assert body["relationshipTypeName"] == "DigitalProductDependency"
    conditions = body["searchProperties"]["conditions"]
    assert [(c["property"], c["operator"], c["value"]["primitiveValue"]) for c in conditions] == [
        ("label", "EQ", "feeds")]
    assert body["searchProperties"]["matchCriteria"] == "ALL"


@pytest.mark.asyncio
async def test_no_elements_string_returns_none():
    client = _FakeClient("No elements returned")
    assert await async_find_matching_relationship(client, "SolutionLinkingWire", "c1", "c2", {"label": "x"}) is None


@pytest.mark.asyncio
async def test_reversed_ends_do_not_match():
    client = _FakeClient(envelope(omrs_rel("r1", "p1", "p2", label="feeds")))
    assert await async_find_matching_relationship(
        client, "DigitalProductDependency", "p2", "p1", {"label": "feeds"}) is None


@pytest.mark.asyncio
async def test_expected_none_property_must_be_absent():
    client = _FakeClient(envelope(omrs_rel("with-chain", "p1", "p2", label="feeds", iscQualifiedName="ISC::A")))
    assert await async_find_matching_relationship(
        client, "DigitalProductDependency", "p1", "p2", {"label": "feeds", "iscQualifiedName": None}) is None


@pytest.mark.asyncio
async def test_expected_none_property_matches_when_absent():
    client = _FakeClient(envelope(omrs_rel("no-chain", "p1", "p2", label="feeds")))
    assert await async_find_matching_relationship(
        client, "DigitalProductDependency", "p1", "p2", {"label": "feeds", "iscQualifiedName": None}) == "no-chain"


@pytest.mark.asyncio
async def test_flat_properties_also_accepted():
    flat = {"relationshipGUID": "flat", "elementGUIDAtEnd1": "c1", "elementGUIDAtEnd2": "c2",
            "relationshipProperties": {"label": "x"}}
    client = _FakeClient(envelope(flat))
    assert await async_find_matching_relationship(client, "SolutionLinkingWire", "c1", "c2", {"label": "x"}) == "flat"


@pytest.mark.asyncio
async def test_missing_end_guid_skips_lookup():
    client = _FakeClient(envelope())
    assert await async_find_matching_relationship(client, "SolutionLinkingWire", None, "c2", {"label": "x"}) is None
    assert client.bodies == []
