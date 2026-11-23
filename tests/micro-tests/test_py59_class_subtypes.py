"""PY-59: a `class:A` column matches a classification named A or any of its subtypes (Egeria 6.4)."""
import importlib.util
import pathlib

import pytest

from pyegeria.view.column_source import check_source, resolve_source

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _el(*classifications):
    return {"elementHeader": {"classifications": [
        {"classificationName": name, "classificationProperties": props} for name, props in classifications]}}


def test_a_subtype_classification_fills_a_supertype_class_column():
    el = _el(("PolicyEnforcementPoint", {"pointType": "gate"}))
    assert resolve_source(el, "class:PolicyManagementPoint.pointType")[1] == "gate"
    assert resolve_source(el, "class:PolicyManagementPoint")[1] == "PolicyEnforcementPoint"


def test_the_exact_name_still_matches():
    el = _el(("PolicyManagementPoint", {"pointType": "base"}))
    assert resolve_source(el, "class:PolicyManagementPoint.pointType") == ("base", "base")
    assert resolve_source(el, "class:PolicyManagementPoint")[1] == "PolicyManagementPoint"


def test_an_unrelated_classification_does_not_fill_it():
    el = _el(("Confidence", {"confidenceLevel": 3}), ("PolicyManagementPoint", {"pointType": "x"}))
    assert resolve_source(el, "class:PolicyManagementPoint")[1] == "PolicyManagementPoint"
    assert resolve_source(_el(("Confidence", {})), "class:PolicyManagementPoint") == ("", "")


def test_a_supertype_does_not_fill_a_subtype_column():
    el = _el(("PolicyManagementPoint", {"pointType": "x"}))
    assert resolve_source(el, "class:PolicyEnforcementPoint") == ("", "")


def test_a_sibling_subtype_does_not_fill_another_subtypes_column():
    el = _el(("PolicyDecisionPoint", {}))
    assert resolve_source(el, "class:PolicyEnforcementPoint") == ("", "")


def test_a_project_kind_column_matches_its_subtypes():
    el = _el(("Campaign", {}), ("Task", {}))
    assert resolve_source(el, "class:ProjectKind")[1] == "Campaign, Task"


def test_two_names_still_list_every_match_once():
    el = _el(("PolicyEnforcementPoint", {}), ("Confidence", {}))
    assert resolve_source(el, "class:PolicyManagementPoint,Confidence")[1] == "PolicyEnforcementPoint, Confidence"


def test_the_supertype_table_names_real_classifications():
    from md_processing.md_processing_utils.properties_class_fields import (CLASSIFICATION_SUPERTYPES,
                                                                           PROPERTIES_CLASS_FIELDS)
    assert CLASSIFICATION_SUPERTYPES["PolicyEnforcementPoint"] == ("PolicyManagementPoint",)
    for sub, above in CLASSIFICATION_SUPERTYPES.items():
        assert PROPERTIES_CLASS_FIELDS[f"{sub}Properties"][0] == "classification"
        for sup in above:
            assert PROPERTIES_CLASS_FIELDS[f"{sup}Properties"][0] == "classification", (sub, sup)
    assert not any(a == "ClassificationBean" for above in CLASSIFICATION_SUPERTYPES.values() for a in above)


def test_the_validator_still_accepts_a_supertype_source():
    assert check_source("class:PolicyManagementPoint.pointType") == []


def test_the_generator_records_supertype_chains():
    spec = importlib.util.spec_from_file_location("gen_pcf", ROOT / "scripts/gen_properties_class_fields.py")
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)

    def java(name, parent, setter):
        return (f"package org.x.properties;\npublic class {name} extends {parent} {{\n"
                f"  public void set{setter}(String v) {{ }}\n}}\n")
    sources = {
        "a/src/main/java/org/x/properties/ClassificationProperties.java":
            "package org.x.properties;\npublic class ClassificationProperties { public void setTypeName(String v){} }\n",
        "a/src/main/java/org/x/properties/WidgetProperties.java": java("WidgetProperties", "ClassificationProperties", "Size"),
        "a/src/main/java/org/x/properties/BigWidgetProperties.java": java("BigWidgetProperties", "WidgetProperties", "Weight"),
        "a/src/main/java/org/x/properties/HugeWidgetProperties.java": java("HugeWidgetProperties", "BigWidgetProperties", "Mass"),
    }
    table = gen.build_table(sources)
    assert table["HugeWidgetProperties"][0] == "classification"
    assert gen.supertypes["HugeWidget"] == ("BigWidget", "Widget")
    assert gen.supertypes["BigWidget"] == ("Widget",)
    assert "Widget" not in gen.supertypes
