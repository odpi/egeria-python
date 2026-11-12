# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Typed Egeria property bodies for Dr.Egeria dictionaries (BRIEF F-A items 1-3).

Egeria's RelationshipProperties / ClassificationProperties / EntityProperties are polymorphic: a
dictionary sent without a "class" is a 400 (InvalidTypeIdException) that loses the whole create. On the
round-trip probe's run 1 (2026-11-12, scratch 757a5df0) `Parent Relationship Attributes` alone failed
108 of 110 creates. The fixtures below are the values the probe's generated blocks sent.
"""
import pytest

from md_processing.md_processing_utils.common_md_utils import set_create_body
from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS
from md_processing.md_processing_utils.typed_properties import (
    classification_map, entity_properties, long_value, new_element_properties, not_applied_notes,
    parent_relationship_properties,
    properties_class, record_not_applied)

# What the probe's generated `## Create Governance Action Process` block sent (run-20261112T092519Z).
PROBE_PARENT_DICT = {"rtpKey": "RTP CreateGovernanceActionProcess ParentRelationshipAttributes"}


def _attrs(**values):
    return {name.replace("_", " "): {"value": value} for name, value in values.items()}


# ── the generated table ──

def test_table_knows_the_kinds_and_inherited_fields():
    kind, fields = PROPERTIES_CLASS_FIELDS["CollectionMembershipProperties"]
    assert kind == "relationship" and "membershipRationale" in fields and "effectiveFrom" in fields
    assert PROPERTIES_CLASS_FIELDS["TaxonomyProperties"][0] == "classification"
    assert PROPERTIES_CLASS_FIELDS["GlossaryProperties"][0] == "entity"
    # governance classifications inherit through a *Base class, which the generator must follow
    assert PROPERTIES_CLASS_FIELDS["ConfidenceProperties"][0] == "classification"


def test_properties_class_lookup():
    assert properties_class("relationship", "CollectionMembership") == "CollectionMembershipProperties"
    assert properties_class("classification", "Taxonomy") == "TaxonomyProperties"
    assert properties_class("relationship", "Taxonomy") is None  # wrong kind
    assert properties_class("relationship", "NoSuchType") is None


# ── item 1: Parent Relationship Attributes ──

def test_probe_dictionary_without_a_type_is_not_sent_and_says_why():
    attributes = {"Parent Relationship Attributes": {"value": PROBE_PARENT_DICT}}
    body, notes = parent_relationship_properties(attributes)
    assert body is None
    assert notes == ["not applied: Parent Relationship Attributes: it needs a Parent Relationship Type Name "
                     "to say which relationship properties these are (rtpKey)"]


def test_unknown_key_for_the_relationship_is_reported_not_sent():
    attributes = {"Parent Relationship Attributes": {"value": PROBE_PARENT_DICT},
                  "Parent Relationship Type Name": {"value": "CollectionMembership"}}
    body, notes = parent_relationship_properties(attributes)
    assert body is None  # nothing the relationship reads: no properties at all, rather than a bare class
    assert notes == ["not applied: Parent Relationship Attributes: rtpKey isn't a property of CollectionMembership"]


def test_known_keys_go_out_typed():
    attributes = {"Parent Relationship Attributes": {"value": {"membershipRationale": "why", "rtpKey": "x"}},
                  "Parent Relationship Type Name": {"value": "CollectionMembership"}}
    body, notes = parent_relationship_properties(attributes)
    assert body == {"class": "CollectionMembershipProperties", "membershipRationale": "why"}
    assert notes == ["not applied: Parent Relationship Attributes: rtpKey isn't a property of CollectionMembership"]


def test_relationship_type_with_no_properties_class():
    attributes = {"Parent Relationship Attributes": {"value": {"a": "b"}},
                  "Parent Relationship Type Name": {"value": "NotAnEgeriaRelationship"}}
    body, notes = parent_relationship_properties(attributes)
    assert body is None and "has no relationship properties in Egeria" in notes[0]


def test_json_text_value_is_accepted():
    attributes = {"Parent Relationship Attributes": {"value": '{"membershipRationale": "why"}'},
                  "Parent Relationship Type Name": {"value": "CollectionMembership"}}
    assert parent_relationship_properties(attributes)[0] == {"class": "CollectionMembershipProperties",
                                                           "membershipRationale": "why"}


def test_set_create_body_never_sends_a_raw_parent_dictionary():
    attributes = {"Display Name": {"value": "x"},
                  "Parent Relationship Attributes": {"value": PROBE_PARENT_DICT}}
    body = set_create_body("Governance Action Process", attributes)
    assert body["parentRelationshipProperties"] is None
    assert not_applied_notes(attributes) == [
        "not applied: Parent Relationship Attributes: it needs a Parent Relationship Type Name to say which "
        "relationship properties these are (rtpKey)"]


def test_set_create_body_sends_the_typed_class():
    attributes = {"Parent Relationship Attributes": {"value": {"membershipRationale": "why"}},
                  "Parent Relationship Type Name": {"value": "CollectionMembership"}}
    body = set_create_body("Collection", attributes)
    assert body["parentRelationshipProperties"]["class"] == "CollectionMembershipProperties"
    assert not_applied_notes(attributes) == []


def test_record_not_applied_dedupes_and_collects_in_order():
    attributes = _attrs(A="1", B="2")
    record_not_applied(attributes, "B", ["not applied: B: x"])
    record_not_applied(attributes, "A", ["not applied: A: y", "not applied: A: y"])
    record_not_applied(attributes, "B", ["not applied: B: x"])
    assert not_applied_notes(attributes) == ["not applied: A: y", "not applied: B: x"]


# ── item 2: Template Properties / Generic Initial Classifications ──

def test_classification_map_types_each_classification():
    out, notes = classification_map({"Taxonomy": {"organizingPrinciple": "p", "rtpKey": "x"},
                                     "rtpKey": "RTP CreateElement GenericInitialClassifications"},
                                    "Generic Initial Classifications")
    assert out == {"Taxonomy": {"class": "TaxonomyProperties", "organizingPrinciple": "p"}}
    assert "not applied: Generic Initial Classifications: rtpKey isn't a property of Taxonomy" in notes
    assert any("rtpKey needs a dictionary of its properties" in n for n in notes)


def test_classification_map_unknown_classification():
    out, notes = classification_map({"NotAClassification": {}}, "Generic Initial Classifications")
    assert out is None
    assert notes == ["not applied: Generic Initial Classifications: NotAClassification isn't an Egeria "
                     "classification"]


def test_classification_with_no_properties_is_sent_as_its_class():
    out, _ = classification_map({"Taxonomy": {}}, "Initial Classifications")
    assert out == {"Taxonomy": {"class": "TaxonomyProperties"}}


def test_entity_properties_need_a_known_type():
    body, notes = entity_properties(None, {"description": "d"}, "Template Properties")
    assert body is None and "element type isn't known" in notes[0]
    body, notes = entity_properties("SchemaType", {"description": "d", "rtpKey": "x"}, "Template Properties")
    assert body == {"class": "SchemaTypeProperties", "description": "d"}
    assert notes == ["not applied: Template Properties: rtpKey isn't a property of SchemaType"]


# ── item 3: Java Long fields ──

@pytest.mark.parametrize("raw, expected", [("7", 7), ("7.0", 7), (7, 7), (" 12 ", 12)])
def test_long_value_coerces_integral_input(raw, expected):
    assert long_value({"Absolute Uncertainty": {"value": raw}}, "Absolute Uncertainty") == (expected, [])


@pytest.mark.parametrize("raw, fragment", [("7.5", "isn't a whole number"), ("seven", "isn't a number")])
def test_long_value_refuses_with_a_sentence(raw, fragment):
    value, notes = long_value({"Absolute Uncertainty": {"value": raw}}, "Absolute Uncertainty")
    assert value is None and fragment in notes[0] and notes[0].startswith("not applied: Absolute Uncertainty")


def test_long_value_absent():
    assert long_value({}, "Absolute Uncertainty") == (None, [])


def test_new_element_properties_for_the_related_elements_endpoint():
    typed = {"class": "CollectionMembershipProperties", "membershipRationale": "why", "confidence": 7}
    assert new_element_properties(typed) == {
        "class": "NewElementProperties",
        "propertyValueMap": {
            "membershipRationale": {"class": "PrimitiveTypePropertyValue", "typeName": "string",
                                    "primitiveTypeCategory": "OM_PRIMITIVE_TYPE_STRING", "primitiveValue": "why"},
            "confidence": {"class": "PrimitiveTypePropertyValue", "typeName": "int",
                           "primitiveTypeCategory": "OM_PRIMITIVE_TYPE_INT", "primitiveValue": 7}}}
    assert new_element_properties({"class": "X"}) is None
    assert new_element_properties(None) is None
