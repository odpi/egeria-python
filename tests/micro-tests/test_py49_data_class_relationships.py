# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""PY-49 Group B: the Data-Classes and Data-Value-Spec columns `containing_data_class` and `specializes_data_class`.

Both columns named things no code produced, so they were blank in every report. In Egeria 6.4:

- the data class a class is part of is the DataClassComposition relationship, read from the element as `partOfDataClasses`
  (end 1 is the whole);
- there is no data-class specialization relationship; specialization is DataValueHierarchy, read as
  `superDataValueSpecification` (a single related element, not a list).

`nestedDataClasses` and `specializedDataValueSpecifications` exist in no Egeria tree, so they are no longer read.
No Egeria: the element body is a captured shape.
"""
import pytest

from pyegeria.omvs.data_designer import DataDesigner

pytestmark = pytest.mark.unit


def _related(guid, name):
    return {"relatedElement": {"elementHeader": {"guid": guid, "type": {"typeName": "DataClass"}},
                               "properties": {"displayName": name, "qualifiedName": f"DataClass::{name}"}}}


def _rel_dict(el):
    return DataDesigner.get_data_rel_elements_dict(DataDesigner.__new__(DataDesigner), el)


def test_containing_data_class_comes_from_the_data_class_composition_list():
    out = _rel_dict({"partOfDataClasses": [_related("g1", "Address"), _related("g2", "Contact")]})
    assert out["containing_data_class"] == ["DataClass::Address", "DataClass::Contact"]
    assert out["containing_data_class_guids"] == ["g1", "g2"]
    assert out["containing_data_class_names"] == ["Address", "Contact"]


def test_specializes_data_class_comes_from_the_single_data_value_hierarchy_parent():
    out = _rel_dict({"superDataValueSpecification": _related("g9", "Postal Code")})
    assert out["specializes_data_class"] == ["DataClass::Postal Code"]


def test_nothing_related_gives_empty_lists_not_none():
    out = _rel_dict({})
    assert out["containing_data_class"] == [] and out["specializes_data_class"] == []


def test_the_dead_fallback_keys_are_no_longer_read():
    out = _rel_dict({"nestedDataClasses": [_related("g1", "X")],
                     "specializedDataValueSpecifications": [_related("g2", "Y")]})
    assert out["containing_data_class"] == [] and out["specializes_data_class"] == []


def test_the_misleading_nested_key_is_renamed():
    out = _rel_dict({"partOfDataClasses": [_related("g1", "Address")]})
    assert not [k for k in out if k.startswith("nested_data_class")]


def test_the_data_class_extractor_fills_both_columns():
    dd = DataDesigner.__new__(DataDesigner)
    element = {"elementHeader": {"guid": "gc", "type": {"typeName": "DataClass"}, "origin": {}, "versions": {}},
               "properties": {"displayName": "Postal Code", "qualifiedName": "DataClass::Postal Code"},
               "partOfDataClasses": [_related("g1", "Address")],
               "superDataValueSpecification": _related("g9", "Code")}
    cols = {"formats": {"types": ["ALL"], "attributes": [
        {"name": "Containing Data Class", "key": "containing_data_class", "value": None},
        {"name": "Specializes Data Class", "key": "specializes_data_class", "value": None}]}}
    out = dd._extract_data_class_properties(element, cols)
    values = {c["key"]: c["value"] for c in out["formats"]["attributes"]}
    assert values == {"containing_data_class": ["DataClass::Address"], "specializes_data_class": ["DataClass::Code"]}
