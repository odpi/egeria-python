"""PY-53: Column.source, one mechanism with three forms (class:, rel:, of:)."""
import pytest

from pyegeria.view._output_format_models import Column, Format, FormatSet
try:  # a missing module fails each test on its own (the bite is counted per form)
    from pyegeria.view.column_source import SourceError, check_source, parse_source, resolve_source
except ImportError:  # pragma: no cover
    SourceError = Exception
    check_source = parse_source = resolve_source = None
from pyegeria.view.output_formatter import populate_common_columns


def _element():
    return {
        "elementHeader": {
            "guid": "g1",
            "type": {"typeName": "FileFolder"},
            "origin": {}, "versions": {},
            "classifications": [
                {"classificationName": "Branch",
                 "classificationProperties": {"displayName": "main", "scope": "release"}},
            ],
            "otherClassifications": [{"classificationName": "Campaign", "classificationProperties": {}}],
            "anchor": {"classificationName": "Anchors", "classificationProperties": {"anchorGUID": "x"}},
        },
        "properties": {"displayName": "Folder", "qualifiedName": "F::1"},
        "projectTargets": [
            {"relationshipProperties": {"label": "first"},
             "relatedElement": {"elementHeader": {"guid": "t1"}, "properties": {"displayName": "T1"}}},
            {"relationshipProperties": {"propertyValueMap": {"label": {"propertyValue": "second"}}},
             "relatedElement": {"elementHeader": {"guid": "t2"}, "properties": {"displayName": "T2"}}},
            {"relationshipProperties": {},
             "relatedElement": {"elementHeader": {"guid": "t3"}, "properties": {"displayName": "T3"}}},
        ],
    }


def _populate(*columns):
    struct = {"formats": {"attributes": [c.model_dump() for c in columns]}}
    out = populate_common_columns(_element(), struct)
    return {c["key"]: c for c in out["formats"]["attributes"]}


# ── form 1: classification property ──
def test_class_property_is_read_from_any_header_slot_by_type_name():
    got = _populate(Column(name="Branch", key="branch_scope", source="class:Branch.scope"))
    assert got["branch_scope"]["value"] == "release"


def test_class_matches_other_classifications_slot_by_type_name():
    got = _populate(Column(name="Kind", key="project_kind", source="class:Campaign"))
    assert got["project_kind"]["value"] == "Campaign"


def test_class_list_joins_all_present_not_the_first():
    got = _populate(Column(name="Kind", key="kinds", source="class:Task,Campaign,Branch"))
    assert got["kinds"]["value"] == "Campaign, Branch"


def test_class_absent_is_blank_never_none():
    got = _populate(Column(name="Kind", key="k", source="class:Task"),
                    Column(name="P", key="p", source="class:Branch.purpose"))
    assert got["k"]["value"] == "" and got["p"]["value"] == ""


# ── form 2: relationship property ──
def test_rel_property_reads_flat_bean_and_property_value_map():
    got = _populate(Column(name="Label", key="target_label", source="rel:projectTargets.label"))
    assert got["target_label"]["native"] == ["first", "second", ""]
    assert got["target_label"]["value"] == "first, second"


# ── form 3: attribute of the related element ──
def test_of_attribute_of_related_element():
    got = _populate(Column(name="T", key="targets", source="of:projectTargets.displayName"))
    assert got["targets"]["native"] == ["T1", "T2", "T3"]


def test_rel_and_of_columns_of_one_end_stay_aligned_by_position():
    got = _populate(Column(name="L", key="l", source="rel:projectTargets.label"),
                    Column(name="T", key="t", source="of:projectTargets.displayName"))
    pairs = list(zip(got["t"]["native"], got["l"]["native"]))
    assert pairs == [("T1", "first"), ("T2", "second"), ("T3", "")]


def test_no_related_elements_gives_empty_list_and_text():
    struct = {"formats": {"attributes": [Column(name="L", key="l", source="rel:projectTargets.label").model_dump()]}}
    out = populate_common_columns({"elementHeader": {}, "properties": {}}, struct)
    col = out["formats"]["attributes"][0]
    assert col["native"] == [] and col["value"] == ""


# ── grammar ──
@pytest.mark.parametrize("bad", ["", "class:", "rel:projectTargets", "of:x", "branch.scope", "class:A B"])
def test_bad_grammar_is_refused_by_the_column(bad):
    with pytest.raises(Exception):
        Column(name="x", key="x", source=bad)


def test_parse_forms():
    assert parse_source("class:A,B.p").names == ("A", "B")
    assert parse_source("rel:e.p").kind == "rel"
    with pytest.raises(SourceError):
        parse_source("nope")


# ── validator checks against the 6.4 tables ──
@pytest.mark.parametrize("good", ["class:Branch.scope", "class:Campaign,Task", "rel:projectTargets.label",
                                  "rel:catalogTargets.metadataSourceQualifiedName", "of:projectTargets.displayName"])
def test_validator_accepts_real_sources(good):
    assert check_source(good) == []


@pytest.mark.parametrize("bad", ["class:NoSuchClass", "class:Branch.nope", "rel:noSuchEnd.label",
                                 "rel:projectTargets.priority", "of:projectTargets.noSuchAttribute"])
def test_validator_errors_on_unknown_names(bad):
    assert len(check_source(bad)) == 1


def test_resolve_source_direct():
    native, text = resolve_source(_element(), "class:Branch.displayName")
    assert native == text == "main"


# ── the column survives the seed and the code emitter ──
def test_source_round_trips_through_microflow():
    from pyegeria.view.microflow import format_set_to_microflow, microflow_to_format_set
    fs = FormatSet(target_type="FileFolder", heading="H", description="d", formats=[
        Format(types=["ALL"], attributes=[Column(name="Scope", key="branch_scope", source="class:Branch.scope")])])
    back = microflow_to_format_set(format_set_to_microflow(fs), label="Folders-Branch")
    cols = [c for f in back.formats for c in f.attributes]
    assert [c.source for c in cols] == ["class:Branch.scope"]


def test_source_is_emitted_in_generated_code():
    from commands.tech.gen_report_specs import _format_column
    text = _format_column(Column(name="Scope", key="branch_scope", source="class:Branch.scope"))
    assert "source='class:Branch.scope'" in text


def test_validator_error_for_a_spec_with_a_bad_source():
    import asyncio
    import importlib
    v = importlib.import_module("pyegeria.authoring.validate")
    from types import SimpleNamespace
    fs = FormatSet(target_type="FileFolder", heading="H", description="d", formats=[
        Format(types=["ALL"], attributes=[Column(name="X", key="x", source="class:NoSuchClass")])])
    result = v.ValidationResult() if hasattr(v, "ValidationResult") else None
    draft = SimpleNamespace(format_set=fs, label="T")
    asyncio.run(v._check_spec(draft, result))
    assert any("NoSuchClass" in e for e in result.errors)
