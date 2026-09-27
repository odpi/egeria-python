# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Data Designer relationship commands, aligned with Egeria types 0580/0581
(DataField, DataStructure and their MemberDataField/NestedDataField/
LinkedDataField/SchemaAttributeDefinition/SchemaTypeDefinition relationships)
plus the 0540 DataValueDefinition/DataValueHierarchy/DataClassComposition links.

Covers DataDesignerLinkProcessor (one OM_TYPE-driven processor for all of
them), DataFieldPrimaryKeyProcessor, the SDK's relationship parsing
(DataDesigner.get_data_rel_elements_dict) and set_data_field_body.

No live server needed: a fake client captures the outgoing calls.
"""
from typing import Any, cast

import pytest

from md_processing.md_processing_utils.common_md_utils import set_data_field_body
from md_processing.v2.data_designer import (
    DATA_DESIGNER_LINKS, DataDesignerLinkProcessor, DataFieldPrimaryKeyProcessor,
)
from md_processing.v2.extraction import DrECommand
from pyegeria.omvs.data_designer import DataDesigner

GUID1 = "aaaaaaaa-0000-0000-0000-000000000001"
GUID2 = "bbbbbbbb-0000-0000-0000-000000000002"


class _Recorder:
    """Records every awaited method call as (method name, args)."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        async def _record(*args, **kwargs):
            self.calls.append((name, args, kwargs))
        return _record


class _FakeClient:
    def __init__(self):
        self.data_designer = _Recorder()
        self.schema_maker = _Recorder()


def _processor(cls, verb: str, object_type: str, om_type: str, attributes: dict, client=None):
    client = client or _FakeClient()
    p = cls(client=cast(Any, client), command=DrECommand(verb=verb, object_type=object_type, attributes={},
                                                         raw_block=f"# {verb} {object_type}"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": om_type}
    p.parsed_output = {"qualified_name": None, "attributes": attributes}
    return p, client


def _ends(om_type: str) -> dict:
    end1, end2 = DATA_DESIGNER_LINKS[om_type][:2]
    return {end1: {"guid": GUID1}, end2: {"guid": GUID2}}


@pytest.mark.asyncio
@pytest.mark.parametrize("om_type", sorted(DATA_DESIGNER_LINKS))
async def test_link_calls_mapped_method_with_typed_properties(om_type):
    p, client = _processor(DataDesignerLinkProcessor, "Link", om_type, om_type, _ends(om_type))
    await p.apply_changes()

    (method, args, _), = client.data_designer.calls
    assert method == DATA_DESIGNER_LINKS[om_type][2]
    assert args[:2] == (GUID1, GUID2)
    assert args[2]["class"] == "NewRelationshipRequestBody"
    assert args[2]["properties"]["class"] == f"{om_type}Properties"


@pytest.mark.asyncio
@pytest.mark.parametrize("verb", ["Detach", "Unlink", "Remove"])
@pytest.mark.parametrize("om_type", sorted(DATA_DESIGNER_LINKS))
async def test_detach_verbs_detach_rather_than_link(om_type, verb):
    p, client = _processor(DataDesignerLinkProcessor, verb, om_type, om_type, _ends(om_type))
    await p.apply_changes()

    (method, args, _), = client.data_designer.calls
    assert method == DATA_DESIGNER_LINKS[om_type][3]
    assert args[:2] == (GUID1, GUID2)
    assert args[2]["class"] == "DeleteRelationshipRequestBody"


@pytest.mark.asyncio
@pytest.mark.parametrize("om_type", ["MemberDataField", "NestedDataField"])
async def test_membership_links_carry_part_of_properties(om_type):
    attributes = {**_ends(om_type), "Position": {"value": 2}, "Minimum Cardinality": {"value": 1},
                  "Maximum Cardinality": {"value": 5}, "Coverage Category": {"value": "CORE_DETAIL"}}
    p, client = _processor(DataDesignerLinkProcessor, "Link", om_type, om_type, attributes)
    await p.apply_changes()

    props = client.data_designer.calls[0][1][2]["properties"]
    assert props == {"class": f"{om_type}Properties", "position": 2, "minCardinality": 1,
                     "maxCardinality": 5, "coverageCategory": "CORE_DETAIL"}


@pytest.mark.asyncio
async def test_linked_data_field_properties():
    attributes = {**_ends("LinkedDataField"), "Link Relationship Type Name": {"value": "ForeignKey"},
                  "Relationship End": {"value": 1}, "Label": {"value": "customer"},
                  "Description": {"value": "order -> customer"}}
    p, client = _processor(DataDesignerLinkProcessor, "Link", "Data Field", "LinkedDataField", attributes)
    await p.apply_changes()

    props = client.data_designer.calls[0][1][2]["properties"]
    assert props["relationshipTypeName"] == "ForeignKey"
    assert props["relationshipEnd"] == 1
    assert props["displayName"] == "customer"
    assert props["description"] == "order -> customer"
    assert "label" not in props


@pytest.mark.asyncio
async def test_missing_end_raises_without_calling_egeria():
    p, client = _processor(DataDesignerLinkProcessor, "Link", "Nested Data Field", "NestedDataField",
                           {"Parent Data Field": {"guid": GUID1}})
    with pytest.raises(ValueError, match="Nested Data Field"):
        await p.apply_changes()
    assert client.data_designer.calls == []


@pytest.mark.asyncio
async def test_primary_key_classify_and_declassify():
    attributes = {"Data Field": {"guid": GUID1}, "Primary Key Name": {"value": "order id"},
                  "Primary Key Pattern": {"value": "NATURAL_KEY"}}
    p, client = _processor(DataFieldPrimaryKeyProcessor, "Classify", "Data Field as Primary Key", "PrimaryKey",
                           attributes)
    await p.apply_changes()
    (method, args, _), = client.schema_maker.calls
    assert method == "_async_add_primary_key_classification"
    assert args[0] == GUID1
    assert args[1]["properties"] == {"class": "PrimaryKeyProperties", "displayName": "order id",
                                     "keyPattern": "NATURAL_KEY"}

    p, client = _processor(DataFieldPrimaryKeyProcessor, "Declassify", "Data Field as Primary Key", "PrimaryKey",
                           attributes)
    await p.apply_changes()
    assert [c[0] for c in client.schema_maker.calls] == ["_async_remove_primary_key_classification"]


def _rel(guid: str, name: str) -> dict:
    return {"relatedElement": {"elementHeader": {"guid": guid},
                               "properties": {"displayName": name, "qualifiedName": f"QN::{name}"}}}


def test_rel_elements_reads_current_egeria_relationship_keys():
    element = {
        "partOfDataStructures": [_rel("ds", "Structure")],
        "parentDataFields": [_rel("pf", "Parent")],
        "semanticDefinitions": [_rel("term", "Term")],
        "dataValueSpecifications": [_rel("dc", "Class")],
        "partOfDataClasses": [_rel("pdc", "Parent Class")],
        "superDataValueSpecification": _rel("sup", "Super"),  # uni-link side: a single dict
    }
    rels = DataDesigner.get_data_rel_elements_dict(cast(Any, None), element)
    assert rels["data_structure_guids"] == ["ds"]
    assert rels["parent_guids"] == ["pf"]
    assert rels["assigned_meanings_guids"] == ["term"]
    assert rels["data_class_guids"] == ["dc"]
    assert rels["nested_data_class_guids"] == ["pdc"]
    assert rels["specialized_data_value_spec_guids"] == ["sup"]


def test_data_field_body_includes_0580_properties():
    attributes = {"Namespace Path": {"value": "sales"}, "Is Partition Key": {"value": True},
                  "Partition Key Position": {"value": 1}, "Allow Duplicate Values": {"value": False},
                  "Sort Order": {"value": "ASCENDING"}}
    body = set_data_field_body("DataField", "DataField::sales::order_id", attributes)
    assert body["namespacePath"] == "sales"
    assert body["isPartitionKey"] is True
    assert body["partitionKeyPosition"] == 1
    assert body["allowsDuplicateValues"] is False
    assert body["sortOrder"] == "ASCENDING"
