"""Body builders for the MetadataExpert Dr.Egeria family (no live server)."""
import pytest

from pyegeria import PyegeriaException
from md_processing.v2.metadata_expert import enum_def_body, type_def_body
from md_processing.v2.extraction import STANDARD_VERBS

pytestmark = pytest.mark.unit


def attrs(**kw):
    return {k.replace("_", " "): {"value": v} for k, v in kw.items()}


def test_entity_def_body():
    body = type_def_body({
        "Type Def Name": {"value": "Recipe"}, "Super Type": {"value": "Referenceable"},
        "Type Def Attributes": {"value": {"servings": "int", "cuisine": "CuisineType"}}})
    assert body["class"] == "OpenMetadataEntityDef" and body["superType"] == {"name": "Referenceable"}
    types = {a["attributeName"]: a["attributeType"] for a in body["attributeDefinitions"]}
    assert types["servings"] == {"class": "OpenMetadataPrimitiveDef", "name": "int"}
    assert types["cuisine"] == {"class": "OpenMetadataEnumDef", "name": "CuisineType"}


def test_classification_def_body():
    body = type_def_body({
        "Type Def Name": {"value": "Vegan"}, "Type Def Category": {"value": "Classification"},
        "Valid Entity Types": {"value": "Recipe, Dish"}, "Propagatable": {"value": "true"}})
    assert body["class"] == "OpenMetadataClassificationDef"
    assert body["validEntityDefs"] == [{"name": "Recipe"}, {"name": "Dish"}] and body["propagatable"] is True


def test_relationship_def_needs_both_ends():
    base = {"Type Def Name": {"value": "Uses"}, "Type Def Category": {"value": "Relationship"},
            "End1 Entity Type": {"value": "Recipe"}, "End1 Attribute Name": {"value": "usedBy"}}
    with pytest.raises(PyegeriaException):
        type_def_body(base)
    body = type_def_body({**base, "End2 Entity Type": {"value": "Ingredient"}, "End2 Attribute Name": {"value": "uses"}})
    assert body["endDef2"] == {"entityType": {"name": "Ingredient"}, "attributeName": "uses"}


def test_enum_def_body_ordinals_and_default():
    body = enum_def_body({"Enum Def Name": {"value": "Cuisine"},
                          "Enum Values": {"value": {"Unknown": "not recorded", "Other": "elsewhere"}},
                          "Enum Default Value": {"value": "Other"}})
    assert [e["ordinal"] for e in body["elementDefs"]] == [0, 1]
    assert body["defaultValue"]["value"] == "Other"
    with pytest.raises(PyegeriaException):
        enum_def_body({"Enum Def Name": {"value": "X"}, "Enum Values": {"value": {"a": ""}},
                       "Enum Default Value": {"value": "zzz"}})


def test_count_is_a_recognised_verb():
    assert "Count" in STANDARD_VERBS


from md_processing.v2.metadata_expert import (element_properties, new_instance_body, related_elements_body,
                                              update_properties_body)


def test_property_types_are_inferred():
    pm = element_properties({"a": "true", "b": "42", "c": "hello"}, "EntityElementProperties")
    assert pm["class"] == "EntityElementProperties"
    assert pm["propertyValueMap"]["a"]["typeName"] == "boolean" and pm["propertyValueMap"]["a"]["primitiveValue"] is True
    assert pm["propertyValueMap"]["b"]["primitiveValue"] == 42
    assert pm["propertyValueMap"]["c"]["typeName"] == "string"
    assert element_properties({}, "EntityElementProperties") is None


def test_new_instance_body_parent_needs_relationship_type():
    base = {"Instance Type Name": {"value": "GlossaryTerm"},
            "Instance Properties": {"value": {"qualifiedName": "T::1"}}, "Parent GUID": {"value": "g1"}}
    with pytest.raises(PyegeriaException):
        new_instance_body(base)
    body = new_instance_body({**base, "Parent Relationship Type Name": {"value": "CollectionMembership"}})
    assert body["parentGUID"] == "g1" and body["parentAtEnd1"] is True and body["typeName"] == "GlossaryTerm"


def test_related_and_update_bodies():
    body = related_elements_body({"Relationship Type Name": {"value": "SemanticAssignment"},
                                  "Element 1 GUID": {"value": "a"}, "Element 2 GUID": {"value": "b"}})
    assert body["metadataElement1GUID"] == "a" and "properties" not in body
    with pytest.raises(PyegeriaException):
        related_elements_body({"Relationship Type Name": {"value": "X"}, "Element 1 GUID": {"value": "a"}})
    upd = update_properties_body({"k": "v"}, "RelationshipElementProperties", {"Replace Properties": {"value": "true"}})
    assert upd["replaceProperties"] is True
    with pytest.raises(PyegeriaException):
        update_properties_body({}, "EntityElementProperties", {})
