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


DECLARED = {"qualifiedName": ("string", "PRIMITIVE"), "versionIdentifier": ("string", "PRIMITIVE"),
            "count": ("int", "PRIMITIVE"), "flag": ("boolean", "PRIMITIVE"), "ratio": ("double", "PRIMITIVE"),
            "tags": ("map<string,string>", "COLLECTION"), "status": ("TermStatus", "ENUM_DEF")}


def test_property_types_come_from_the_type_definition_not_the_text():
    pm = element_properties({"flag": "true", "count": "42", "versionIdentifier": "007", "qualifiedName": "1"},
                            "EntityElementProperties", DECLARED, "Thing")
    values = pm["propertyValueMap"]
    assert pm["class"] == "EntityElementProperties"
    assert values["flag"]["typeName"] == "boolean" and values["flag"]["primitiveValue"] is True
    assert values["count"]["primitiveValue"] == 42
    # a string property keeps its text: leading zeros survive, "1" does not become an int
    assert values["versionIdentifier"] == {"class": "PrimitiveTypePropertyValue", "typeName": "string",
                                           "primitiveValue": "007"}
    assert values["qualifiedName"]["primitiveValue"] == "1"
    assert element_properties({}, "EntityElementProperties") is None


@pytest.mark.parametrize("properties, fragment", [
    ({"tags": "a"}, "map/array"),                # map property
    ({"status": "ACTIVE"}, "enum"),              # enum property
    ({"nope": "x"}, "not a property"),           # undeclared property
    ({"count": "abc"}, "whole number"),          # wrong text for the declared type
    ({"flag": "maybe"}, "true or false"),
    ({"ratio": "x"}, "a number"),
    ({"qualifiedName": {"a": "b"}}, "map/list"),  # a dict is never stringified
    ({"qualifiedName": ["a", "b"]}, "map/list"),
])
def test_unsupported_or_mismatched_properties_are_refused(properties, fragment):
    with pytest.raises(PyegeriaException, match=fragment):
        element_properties(properties, "EntityElementProperties", DECLARED, "Thing")


def test_properties_without_a_type_definition_are_refused():
    with pytest.raises(PyegeriaException):
        element_properties({"qualifiedName": "x"}, "EntityElementProperties")


def test_new_instance_body_parent_needs_relationship_type():
    base = {"Instance Type Name": {"value": "GlossaryTerm"},
            "Instance Properties": {"value": {"qualifiedName": "T::1"}}, "Parent GUID": {"value": "g1"}}
    with pytest.raises(PyegeriaException):
        new_instance_body(base, DECLARED)
    body = new_instance_body({**base, "Parent Relationship Type Name": {"value": "CollectionMembership"}}, DECLARED)
    assert body["parentGUID"] == "g1" and body["parentAtEnd1"] is True and body["typeName"] == "GlossaryTerm"


def test_related_and_update_bodies():
    body = related_elements_body({"Relationship Type Name": {"value": "SemanticAssignment"},
                                  "Element 1 GUID": {"value": "a"}, "Element 2 GUID": {"value": "b"}})
    assert body["metadataElement1GUID"] == "a" and "properties" not in body
    with pytest.raises(PyegeriaException):
        related_elements_body({"Relationship Type Name": {"value": "X"}, "Element 1 GUID": {"value": "a"}})
    upd = update_properties_body({"qualifiedName": "v"}, "RelationshipElementProperties",
                                 {"Replace Properties": {"value": "true"}}, DECLARED, "Thing")
    assert upd["replaceProperties"] is True
    with pytest.raises(PyegeriaException):
        update_properties_body({}, "EntityElementProperties", {})


# ----------------------------------------------------------------------------------------------
# Processor level: the real dispatcher with a fake client.
# ----------------------------------------------------------------------------------------------
from typing import Any, Dict, List

from md_processing.dr_egeria import setup_dispatcher
from md_processing.md_processing_utils.md_processing_constants import COMMAND_DEFINITIONS
from md_processing.v2.extraction import DrECommand
from md_processing.v2.metadata_expert import _delete_method

TYPEDEFS = {
    "Referenceable": {"attributeDefinitions": [{"attributeName": "qualifiedName",
                                                "attributeType": {"name": "string", "category": "PRIMITIVE"}}]},
    "Thing": {"superType": {"name": "Referenceable"}, "attributeDefinitions": [
        {"attributeName": "versionIdentifier", "attributeType": {"name": "string", "category": "PRIMITIVE"}},
        {"attributeName": "count", "attributeType": {"name": "int", "category": "PRIMITIVE"}},
        {"attributeName": "tags", "attributeType": {"name": "map<string,string>", "category": "COLLECTION"}}]},
    "Uses": {"attributeDefinitions": [{"attributeName": "label",
                                       "attributeType": {"name": "string", "category": "PRIMITIVE"}}]},
}
GUID = "11111111-1111-1111-1111-111111111111"


class _FakeExpert:
    def __init__(self, calls):
        self.calls = calls

    def _record(self, name):
        async def call(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            return "new-guid"
        return call

    def __getattr__(self, name):
        if name.startswith("_async_"):
            return self._record(name)
        raise AttributeError(name)

    async def _async_get_metadata_element_by_guid(self, guid, **kwargs):
        return {"elementHeader": {"guid": guid, "type": {"typeName": "Thing"}}}

    async def _async_get_relationship_by_guid(self, guid, **kwargs):
        return {"relationshipHeader": {"guid": guid, "type": {"typeName": "Uses"}}}


class _FakeValidMetadata:
    async def _async_get_typedef_by_name(self, name, **kwargs):
        return {"guid": f"td-{name}", "name": name, **TYPEDEFS[name]}


class _FakeClient:
    def __init__(self):
        self.calls: List[tuple] = []
        self.metadata_expert = _FakeExpert(self.calls)
        self.valid_metadata = _FakeValidMetadata()


def _cmd(verb: str, object_type: str, attributes: Dict[str, Any]) -> DrECommand:
    raw = f"## {verb} {object_type}\n" + "".join(f"### {k}\n{v}\n" for k, v in attributes.items())
    return DrECommand(verb=verb, object_type=object_type, attributes=attributes, raw_block=raw)


async def _run(verb, object_type, attributes, directive="process"):
    client = _FakeClient()
    results = await setup_dispatcher(client).dispatch_batch([_cmd(verb, object_type, attributes)],
                                                            {"directive": directive})
    return results[0], client.calls


def _writes(calls):
    return [c for c in calls if c[0] not in ("_async_get_metadata_element_by_guid", "_async_get_relationship_by_guid")]


@pytest.mark.asyncio
@pytest.mark.parametrize("verb, object_type, attributes, method", [
    ("Create", "Instance", {"Instance Type Name": "Thing", "Instance Properties": "qualifiedName: T::1"},
     "_async_create_metadata_element"),
    ("Update", "Instance", {"Metadata Element GUID": GUID, "Instance Properties": "count: 3"},
     "_async_update_metadata_element_properties"),
    ("Delete", "Instance", {"Metadata Element GUID": GUID}, "_async_delete_metadata_element"),
    ("Link", "Instances", {"Relationship Type Name": "Uses", "Element 1 GUID": GUID, "Element 2 GUID": "33333333-3333-3333-3333-333333333333"},
     "_async_create_related_elements"),
    ("Unlink", "Instances", {"Relationship GUID": GUID}, "_async_delete_related_elements"),
    ("Update", "Relationship", {"Relationship GUID": GUID, "Relationship Properties": "label: x"},
     "_async_update_related_elements_properties"),
    ("Declassify", "Instance", {"Metadata Element GUID": GUID, "Classification Name": "Confidence"},
     "_async_declassify_metadata_element"),
])
async def test_verb_and_object_route_to_the_right_sdk_call(verb, object_type, attributes, method):
    result, calls = await _run(verb, object_type, attributes)
    assert result["status"] == "success", result
    assert [c[0] for c in _writes(calls)] == [method]


@pytest.mark.asyncio
async def test_delete_defaults_to_soft_delete():
    for verb, object_type, attributes in (("Delete", "Instance", {"Metadata Element GUID": GUID}),
                                          ("Unlink", "Instances", {"Relationship GUID": GUID})):
        result, calls = await _run(verb, object_type, attributes)
        assert result["status"] == "success", result
        [(_, args, _)] = _writes(calls)
        assert args[1]["deleteMethod"] == "SOFT_DELETE"


@pytest.mark.asyncio
@pytest.mark.parametrize("verb, object_type, guid_attr", [("Delete", "Instance", "Metadata Element GUID"),
                                                          ("Unlink", "Instances", "Relationship GUID")])
async def test_purge_is_refused_without_the_guid_echo(verb, object_type, guid_attr):
    for extra in ({}, {"Confirm Delete GUID": "22222222-2222-2222-2222-222222222222"}):
        result, calls = await _run(verb, object_type, {guid_attr: GUID, "Delete Method": "PURGE", **extra})
        assert result["status"] != "success"
        assert _writes(calls) == [], "nothing may be sent when the echo is missing or wrong"
    result, calls = await _run(verb, object_type, {guid_attr: GUID, "Delete Method": "PURGE",
                                                   "Confirm Delete GUID": GUID})
    assert result["status"] == "success", result
    assert _writes(calls)[0][1][1]["deleteMethod"] == "PURGE"


def test_hard_delete_needs_the_echo_too():
    with pytest.raises(PyegeriaException, match="permanent"):
        _delete_method({"Delete Method": {"value": "HARD_DELETE"}}, GUID)
    assert _delete_method({"Delete Method": {"value": "hard_delete"}, "Confirm Delete GUID": {"value": GUID}},
                          GUID) == "HARD_DELETE"
    assert _delete_method({}, GUID) == "SOFT_DELETE"


@pytest.mark.asyncio
@pytest.mark.parametrize("replace, expected", [("true", True), ("false", False), (None, False)])
async def test_update_instance_replace_properties(replace, expected):
    attributes = {"Metadata Element GUID": GUID, "Instance Properties": "versionIdentifier: 007"}
    if replace is not None:
        attributes["Replace Properties"] = replace
    result, calls = await _run("Update", "Instance", attributes)
    assert result["status"] == "success", result
    [(_, args, _)] = _writes(calls)
    assert args[1]["replaceProperties"] is expected
    # the string property keeps its leading zeros
    assert args[1]["properties"]["propertyValueMap"]["versionIdentifier"]["primitiveValue"] == "007"


@pytest.mark.asyncio
@pytest.mark.parametrize("properties", ["tags: a", "nope: x", "count: abc"])
async def test_non_primitive_or_undeclared_property_is_refused_before_anything_is_sent(properties):
    result, calls = await _run("Create", "Instance", {"Instance Type Name": "Thing",
                                                      "Instance Properties": properties})
    assert result["status"] != "success"
    assert _writes(calls) == []


MX_COMMANDS = sorted(name for name, spec in COMMAND_DEFINITIONS["Command Specifications"].items()
                     if spec.get("family") == "MetadataExpert")


def test_the_family_is_registered_and_advanced_only():
    assert len(MX_COMMANDS) == 16
    for name in MX_COMMANDS:
        assert COMMAND_DEFINITIONS["Command Specifications"][name]["level"] == "Advanced", name


@pytest.mark.parametrize("name", MX_COMMANDS)
def test_every_command_is_marked_non_idempotent_and_not_for_chat(name):
    spec = COMMAND_DEFINITIONS["Command Specifications"][name]
    assert spec.get("idempotent") is False, f"{name} must be idempotent:false"
    assert spec.get("chat_allowed") is False, f"{name} must be chat_allowed:false"


@pytest.mark.asyncio
async def test_validate_says_the_command_is_not_idempotent():
    result, calls = await _run("Create", "Instance", {"Instance Type Name": "Thing"}, directive="validate")
    assert "not idempotent" in str(result), result
    assert _writes(calls) == []
