# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""RS-W2-1a: every registered routine declares its results -- measures with unit and as-of, the four
nothing_found-vocabulary absence sentences and an `out` field list -- and the model mirrors the
trellis-analytics §5 vocabulary (population, completeness, fields)."""
import warnings

import pytest
from pydantic import ValidationError

from pyegeria.view.analytic_registry import (
    AnalyticDeclaration,
    FieldDeclaration,
    MeasureDeclaration,
)

ABSENCE = {"not_measured": "a", "not_permitted": "b", "not_applicable": "c", "nothing_found": "d"}


# ── model: completeness replaces capped_field; population; fields ──

def test_capped_field_reads_as_completeness_field_with_a_warning():
    with pytest.warns(DeprecationWarning, match="completeness_field"):
        m = MeasureDeclaration(name="n", unit="assets", as_of="run.as_of", value_field="v", capped_field="capped")
    assert m.completeness_field == "capped"
    assert "capped_field" not in m.model_dump()
    with pytest.warns(DeprecationWarning):
        assert m.capped_field == "capped"


def test_capped_field_and_a_different_completeness_field_are_refused():
    with pytest.raises(ValidationError, match="declare that only"):
        MeasureDeclaration(name="n", unit="assets", as_of="a", value_field="v",
                           capped_field="x", completeness_field="y")


def test_completeness_field_alone_does_not_warn():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        MeasureDeclaration(name="n", unit="assets", as_of="a", value_field="v", completeness_field="capped")


@pytest.mark.parametrize("population, ok", [("", True), ("viewer", True), ("repository", True), ("scope", False)])
def test_population_is_viewer_or_repository(population, ok):
    kw = dict(name="n", unit="assets", as_of="a", value_field="v", population=population)
    if ok:
        assert MeasureDeclaration(**kw).population == population
    else:
        with pytest.raises(ValidationError, match="population"):
            MeasureDeclaration(**kw)


def test_a_basis_on_a_share_is_refused():
    with pytest.raises(ValidationError, match="basis on a share"):
        MeasureDeclaration(name="n", unit="percent of assets", as_of="a", value_field="v",
                           basis={"denominator_field": "t", "denominator_label": "assets"})


@pytest.mark.parametrize("field, words", [
    (dict(name="a.b", label="A", type="int"), "identifier"),
    (dict(name="a", type="int"), "label"),
    (dict(name="a", label="A", type="number"), "not a field type"),
    (dict(name="a", label="A", kind="dataset"), "names a shape"),
    (dict(name="a", label="A", type="int", companions=["state"]), "companions belong to a cell"),
    (dict(name="a", label="A", type="int", kind="cell", companions=["colour"]), "cell companions"),
])
def test_bad_fields_are_refused_with_a_sentence(field, words):
    with pytest.raises(ValidationError, match=words):
        FieldDeclaration(**field)


def test_out_defaults_empty_so_older_declarations_still_load():
    d = AnalyticDeclaration(result_kind="list", absence=ABSENCE)
    assert d.out == [] and d.categories is None and d.listing is None


# ── a failed query is None (not_measured), never 0 (RS-W2-1a §3.3) ──

def _failing_clients():
    from unittest.mock import MagicMock
    mgr = MagicMock(spec=["platform_url", "view_server", "find_metadata_elements"])
    mgr.platform_url, mgr.view_server = "https://localhost:9443", "test-server"
    mgr.find_metadata_elements.side_effect = RuntimeError("boom")
    ce = MagicMock(spec=["get_relationships"])
    ce.get_relationships.side_effect = RuntimeError("boom")
    return mgr, ce


def test_ownership_coverage_failure_is_unmeasured():
    from pyegeria.view import overview_metrics as om
    mgr, _ = _failing_clients()
    assert om.ownership_coverage(mgr) == {"ownershipCount": None, "ownershipCapped": None, "byOwnerType": {}}


def test_active_contributors_failure_is_unmeasured():
    from pyegeria.view import overview_metrics as om
    _, ce = _failing_clients()
    result = om.active_contributors(ce)
    assert result["contributors"] is None
    assert set(result["byType"].values()) == {None}


def test_readiness_routines_failure_is_unmeasured():
    from pyegeria.view import overview_metrics as om
    mgr, ce = _failing_clients()
    assert om.context_readiness_funnel(mgr, ce)["documented"] is None
    assert om.ai_ready_assets(mgr, ce) == {"aiReadyCount": None, "total": None, "capped": None}
    assert set(om.drl_readiness_gates(mgr, ce).values()) == {None}


def test_drl_lineage_failure_keeps_the_asset_population():
    from unittest.mock import MagicMock

    from pyegeria.view import overview_metrics as om
    mgr, _ = _failing_clients()
    mgr.find_metadata_elements.side_effect = None
    mgr.find_metadata_elements.return_value = [{"elementGUID": "a1", "type": {"typeName": "CSVFile"}}]
    ce = MagicMock(spec=["get_relationships"])
    ce.get_relationships.side_effect = RuntimeError("boom")
    result = om.drl_readiness_gates(mgr, ce)
    assert (result["total"], result["aiReadyCount"], result["aiReadyRecentCount"]) == (1, None, None)
    assert sum(result["byModality"].values()) == 1
