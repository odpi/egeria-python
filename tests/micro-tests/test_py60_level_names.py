"""PY-60: governance-level classification columns show the level name (Egeria 6.4 enums, from the laz checkout
8de9572c4d), the integer stays in the native value; an unknown integer shows as '7 (unknown level)'; a missing
property stays blank."""
import pytest

from pyegeria.view.column_source import resolve_source


def _el(cls, prop, value):
    props = {} if value is None else {prop: value}
    return {"elementHeader": {"classifications": [{"classificationName": cls, "classificationProperties": props}]}}


CASES = [
    ("Confidentiality", "confidentialityLevel", {0: "Unclassified", 1: "Internal", 2: "Confidential", 3: "Sensitive",
                                                4: "Restricted", 99: "Other"}),
    ("Confidence", "confidenceLevel", {0: "Unclassified", 1: "Ad Hoc", 2: "Transactional", 3: "Authoritative",
                                       4: "Derived", 5: "Obsolete", 99: "Other"}),
    ("Criticality", "criticalityLevel", {0: "Unclassified", 1: "Marginal", 2: "Important", 3: "Critical",
                                         4: "Catastrophic", 99: "Other"}),
    ("Impact", "severityLevel", {0: "Unclassified", 1: "Low", 2: "Medium", 3: "High", 99: "Other"}),
    ("Retention", "retentionBasis", {0: "Unclassified", 1: "Temporary", 2: "Project Lifetime", 3: "Team Lifetime",
                                     4: "Contract Lifetime", 5: "Regulated Lifetime", 6: "Time Boxed Lifetime",
                                     99: "Other"}),
]


@pytest.mark.parametrize("cls,prop,names", CASES)
def test_text_is_the_level_name_and_native_keeps_the_integer(cls, prop, names):
    for number, name in names.items():
        native, text = resolve_source(_el(cls, prop, number), f"class:{cls}.{prop}")
        assert text == name and native == number


@pytest.mark.parametrize("cls,prop,names", CASES)
def test_native_is_the_raw_integer(cls, prop, names):
    native, _ = resolve_source(_el(cls, prop, 3 if 3 in names else 1), f"class:{cls}.{prop}")
    assert native in (3, 1) and isinstance(native, int)


@pytest.mark.parametrize("cls,prop,names", CASES)
def test_unknown_integer_shows_raw_with_marker(cls, prop, names):
    _, text = resolve_source(_el(cls, prop, 7), f"class:{cls}.{prop}")
    assert text == "7 (unknown level)"


@pytest.mark.parametrize("cls,prop,names", CASES)
def test_missing_property_stays_blank(cls, prop, names):
    assert resolve_source(_el(cls, prop, None), f"class:{cls}.{prop}") == ("", "")


def test_a_numeric_string_is_read_as_the_integer():
    assert resolve_source(_el("Criticality", "criticalityLevel", "3"), "class:Criticality.criticalityLevel")[1] == "Critical"


def test_other_class_properties_are_untouched():
    assert resolve_source(_el("SecurityTags", "securityLabels", ["a", "b"]), "class:SecurityTags.securityLabels")[1] == "a, b"
