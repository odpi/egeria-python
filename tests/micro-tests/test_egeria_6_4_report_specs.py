# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Egeria 6.4 (odpi/egeria#9463) A4: report specs for Decision, DataValue and LiteralDataValue.

The specs are hand-maintained FormatSets in ``base_report_formats.base_report_specs``, the same
place and shape as ``License-Type``. These tests check that:

- each spec loads and resolves through ``select_report_spec``, the lookup ``License-Type`` uses, by
  its type name: the dashed label (``Data-Value``), the Egeria type name (``DataValue``) and the
  Dr.Egeria ``<Type>-DrE`` fallback name that ``render_result_markdown`` asks for;
- every column names a real field: a key of the type's Properties class in PROPERTIES_CLASS_FIELDS
  (A0's generated table), a relationship list in RELATIONSHIP_FIELDS, or the header GUID. The key is
  mapped the way the formatter maps it (``to_camel_case``), so a typo fails here, not as a blank
  column in Dr.Egeria or the Portal;
- the brief's columns and relationship lists are all there.
"""

import pytest

from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS
from pyegeria.models import to_camel_case
from pyegeria.view.base_report_formats import base_report_specs, select_report_spec
from pyegeria.view.egeria_relationship_fields import RELATIONSHIP_FIELDS

# label -> (Properties class, Egeria type name, Dr.Egeria fallback name)
SPECS = {
    "Decision": ("DecisionProperties", "Decision", "Decision-DrE"),
    "Data-Value": ("DataValueProperties", "DataValue", "Data-Value-DrE"),
    "Literal-Data-Value": ("LiteralDataValueProperties", "LiteralDataValue", "Literal-Data-Value-DrE"),
}

#: Keys that come from the element header rather than the Properties class.
HEADER_KEYS = {"guid"}

_DATA_VALUE_PROPS = {"displayName", "dataType", "dataFormat", "usage", "length"}
_DATA_VALUE_LISTS = {"dataValueUses", "dataValueSources", "embeddedDataValues"}

EXPECTED_PROPERTIES = {
    "Decision": {"displayName", "qualifiedName", "disposition", "importance", "contentStatus", "summary",
                 "scope", "nextReviewTime", "expiryTime"},
    "Data-Value": _DATA_VALUE_PROPS | {"qualifiedName"},
    "Literal-Data-Value": _DATA_VALUE_PROPS | {"qualifiedName", "dataValue", "dataValueList", "dataValueMap"},
}
EXPECTED_LISTS = {
    "Decision": {"decisionOutcomes", "inputsToDecision"},
    "Data-Value": _DATA_VALUE_LISTS,
    "Literal-Data-Value": _DATA_VALUE_LISTS,
}


def _columns(label):
    """(snake key, camelCase key, column) for every column in every format of the spec."""
    out = []
    for fmt in base_report_specs[label].formats:
        for col in fmt.attributes:
            out.append((col.key, to_camel_case(col.key), col))
    return out


@pytest.mark.parametrize("label", sorted(SPECS))
def test_spec_loads(label):
    assert label in base_report_specs, f"report spec {label!r} missing from base_report_specs"
    fs = base_report_specs[label]
    assert fs.target_type, label
    assert fs.formats, label
    assert fs.action is not None, f"{label}: no action, so a Portal table has nothing to run"


@pytest.mark.parametrize("label", sorted(SPECS))
def test_found_by_type_name(label):
    """The same lookup License-Type goes through: select_report_spec(name, output_type)."""
    _cls, type_name, dre_name = SPECS[label]
    assert select_report_spec("License-Type", "DICT") is not None  # the precedent still resolves
    for name in (label, type_name, dre_name):
        for output_type in ("DICT", "MD", "TABLE", "LIST", "REPORT"):
            got = select_report_spec(name, output_type)
            assert got is not None, f"select_report_spec({name!r}, {output_type!r}) found nothing"
            # The registry names an alias hit by the alias, so match on the spec itself.
            assert got["heading"] == base_report_specs[label].heading, (name, output_type, got["heading"])
            assert got["target_type"] == base_report_specs[label].target_type, (name, output_type)
            assert got["formats"]["attributes"], (name, output_type)


@pytest.mark.parametrize("label", sorted(SPECS))
def test_every_column_is_a_real_field(label):
    cls = SPECS[label][0]
    assert cls in PROPERTIES_CLASS_FIELDS, f"{cls} not in PROPERTIES_CLASS_FIELDS (A0 table)"
    _kind, fields = PROPERTIES_CLASS_FIELDS[cls]
    unknown = [snake for snake, camel, _c in _columns(label)
               if camel not in fields and camel not in RELATIONSHIP_FIELDS and snake not in HEADER_KEYS]
    assert not unknown, f"{label}: columns name no {cls} field or relationship list: {unknown}"


@pytest.mark.parametrize("label", sorted(SPECS))
def test_brief_columns_present(label):
    cls = SPECS[label][0]
    fields = set(PROPERTIES_CLASS_FIELDS[cls][1])
    have = {camel for _s, camel, _c in _columns(label)}
    assert "guid" in {s for s, _c, _x in _columns(label)}, f"{label}: no GUID column"
    missing = EXPECTED_PROPERTIES[label] - have
    assert not missing, f"{label}: missing columns {sorted(missing)}"
    assert EXPECTED_PROPERTIES[label] <= fields  # the brief's names are real for this class


@pytest.mark.parametrize("label", sorted(SPECS))
def test_relationship_lists_present(label):
    cols = {camel: col for _s, camel, col in _columns(label)}
    for rel_list in sorted(EXPECTED_LISTS[label]):
        assert rel_list in RELATIONSHIP_FIELDS, f"{rel_list} not in RELATIONSHIP_FIELDS (A0 table)"
        assert rel_list in cols, f"{label}: no column for relationship list {rel_list}"
        # A relationship list renders as the related elements' names, as Projects' assigned_actors does.
        assert cols[rel_list].label == "display_name", (label, rel_list)


def test_action_uses_existing_finder_for_the_type():
    """The finder exists today, ahead of A1/A2's typed finders, and is filtered to the 6.4 type."""
    from pyegeria.omvs.metadata_expert import MetadataExpert

    for label, (_cls, type_name, _dre) in SPECS.items():
        action = base_report_specs[label].action
        cls_name, method = action.function.split(".")
        assert cls_name == "MetadataExpert" and hasattr(MetadataExpert, method), action.function
        assert action.spec_params == {"metadata_element_type": type_name}, label


@pytest.mark.parametrize("label", sorted(SPECS))
def test_strict_authoring_validation_checks_and_accepts_the_spec(label):
    """target_type is the Egeria type name, so the authoring validator finds its Properties class and checks
    every column strictly (a spaced name such as 'Data Value' matches no class and skips the check)."""
    from pyegeria.authoring.models import SpecDraft
    from pyegeria.authoring.validate import validate

    _cls, type_name, _dre = SPECS[label]
    assert base_report_specs[label].target_type == type_name
    result = validate(SpecDraft(label=label, format_set=base_report_specs[label]))
    assert "column attributes" in result.checked, (label, result.not_checked)
    assert not result.errors, (label, result.errors)
