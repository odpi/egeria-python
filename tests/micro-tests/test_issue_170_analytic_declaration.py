"""ISSUE-170: an optional declaration on AnalyticFunctionSpec -- result kind, measures
with unit/as-of/basis, and the four absence sentences, mirroring trellis-analytics."""
import pytest
from pydantic import ValidationError

from pyegeria.view.analytic_registry import (
    AnalyticDeclaration,
    AnalyticFunctionSpec,
    analytic_registry_payload,
    clear_runtime_analytic_functions,
    get_analytic_registry,
    register_analytic_functions,
)

ABSENCE = {
    "not_measured": "Coverage was not measured: the catalog could not be read.",
    "not_permitted": "Coverage was not measured: reading the catalog is not permitted.",
    "not_applicable": "Coverage does not apply to this resource.",
    "nothing_found": "No columns were found to cover.",
}

DECLARATION = {
    "result_kind": "measure",
    "measures": [{
        "name": "described_columns", "unit": "columns", "as_of": "asOf", "value_field": "described",
        "basis": {"denominator_field": "column_count", "denominator_label": "columns"},
    }],
    "absence": ABSENCE,
}


def test_every_builtin_declares_its_results():
    """RS-W2-1a: every built-in now declares (asset_composition was the first, RS-W1-4); the field
    itself stays optional for specs registered by others."""
    assert all(spec.declaration is not None for spec in get_analytic_registry().values())
    assert AnalyticFunctionSpec(name="x", function="pyegeria.view.overview_metrics.growth_series").declaration is None


def test_declaration_round_trips_on_a_spec():
    spec = AnalyticFunctionSpec(name="coverage", function="pyegeria.view.overview_metrics.growth_series",
                                declaration=DECLARATION)
    m = spec.declaration.measures[0]
    assert (m.unit, m.as_of, m.basis.denominator_label) == ("columns", "asOf", "columns")
    assert spec.declaration.absence.sentence("nothing_found") == ABSENCE["nothing_found"]
    assert AnalyticFunctionSpec(**spec.model_dump()).declaration == spec.declaration


def test_registry_payload_carries_the_declaration():
    clear_runtime_analytic_functions()
    try:
        register_analytic_functions({"test-170": {"name": "test-170", "declaration": DECLARATION,
                                                  "function": "pyegeria.view.overview_metrics.growth_series"}})
        payload = analytic_registry_payload()["functions"]["test-170"]
        assert payload["declaration"]["absence"]["not_measured"] == ABSENCE["not_measured"]
    finally:
        clear_runtime_analytic_functions()


def test_richer_trellis_blocks_are_accepted_and_ignored():
    rich = dict(DECLARATION, extents=[{"name": "x"}], confidence={"form": "measured"}, answers=["Q-0001"])
    assert AnalyticDeclaration.model_validate(rich).result_kind == "measure"


@pytest.mark.parametrize("bad, words", [
    (dict(DECLARATION, result_kind="chart"), "not one of"),
    (dict(DECLARATION, measures=[]), "declares no measures"),
    (dict(DECLARATION, absence=dict(ABSENCE, not_permitted="  ")), "never improvised"),
    (dict(DECLARATION, measures=[{"name": "m", "unit": "", "as_of": "asOf", "value_field": "v"}]), "unit"),
    (dict(DECLARATION, measures=[dict(DECLARATION["measures"][0],
                                      basis={"denominator_field": "n", "denominator_label": ""})]), "basis"),
])
def test_incomplete_declarations_are_refused_with_a_sentence(bad, words):
    with pytest.raises(ValidationError, match=words):
        AnalyticDeclaration.model_validate(bad)


def test_unmeasured_kinds_need_no_measures():
    assert AnalyticDeclaration(result_kind="finding", absence=ABSENCE).measures == []


def test_legacy_measured_nothing_declaration_still_loads_and_is_written_as_nothing_found():
    legacy = dict(ABSENCE)
    legacy["measured_nothing"] = legacy.pop("nothing_found")
    decl = AnalyticDeclaration(**{**DECLARATION, "absence": legacy})
    assert decl.absence.nothing_found == ABSENCE["nothing_found"]
    assert decl.absence.sentence("measured_nothing") == ABSENCE["nothing_found"]
    dumped = decl.model_dump()
    assert "measured_nothing" not in dumped["absence"] and dumped["absence"]["nothing_found"]
