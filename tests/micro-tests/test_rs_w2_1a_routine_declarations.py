# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""RS-W2-1a: every registered routine declares its results -- measures with unit and as-of, the four
nothing_found-vocabulary absence sentences and an `out` field list -- and the model mirrors the
trellis-analytics §5 vocabulary (population, completeness, fields)."""
import re
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


def test_stale_and_term_routines_failure_is_unmeasured():
    from pyegeria.view import overview_metrics as om
    mgr, _ = _failing_clients()
    assert om.stale_assets(mgr)["staleCount"] is None
    assert om.term_definition_completeness(mgr) == {"total": None, "defined": None, "undefinedPct": None}


# ── the census: every registered routine is declared, and its declaration is true of its result ──

from pyegeria.view import overview_metrics as om  # noqa: E402
from pyegeria.view.analytic_registry import (  # noqa: E402
    ABSENCE_STATES,
    LEGACY_NOTHING_FOUND,
    ROW_SHAPES,
    _BUILTINS,
    get_analytic_registry,
)

#: pyegeria's own routines. The registry also holds entry points from installed packages
#: (egeria-trellis-analytics, for one), whose declarations are the library's models, so the
#: checks below that read pyegeria's declaration model run over the built-ins only.
BUILTINS = _BUILTINS
AS_OF = "2026-10-01T00:00:00+00:00"


def test_every_builtin_is_declared():
    undeclared = sorted(name for name, spec in BUILTINS.items() if spec.declaration is None)
    assert undeclared == []


def _trellis_analytics_version():
    """The installed egeria-trellis-analytics version as a tuple, or None when it is not installed."""
    from importlib.metadata import PackageNotFoundError, version
    try:
        raw = version("egeria-trellis-analytics")
    except PackageNotFoundError:
        return None
    return raw, tuple(int(p) for p in re.findall(r"\d+", raw)[:3])


def test_every_registry_entry_is_declared():
    """The census over the whole registry, entry points included: each has a declaration.
    egeria-trellis-analytics before 0.4.0 registers entry points that predate declarations, so
    the census is skipped there; the built-ins are still checked by test_every_builtin_is_declared."""
    installed = _trellis_analytics_version()
    if installed is not None and installed[1] < (0, 4, 0):
        pytest.skip(f"egeria-trellis-analytics {installed[0]} is installed; its entry points predate "
                    "declarations (0.4.0 adds them)")
    undeclared = sorted(name for name, spec in get_analytic_registry().items() if spec.declaration is None)
    assert undeclared == []


def test_the_three_overview_routines_are_registered():
    """D6: the Overview depends on these, so they are routines, registered and declared."""
    for name in ("count_relationships", "drl_readiness_gates", "solution_component_realisation"):
        assert BUILTINS[name].function == f"pyegeria.view.overview_metrics.{name}"


@pytest.mark.parametrize("name", sorted(BUILTINS))
def test_absence_sentences_use_the_four_words(name):
    absence = BUILTINS[name].declaration.absence
    dumped = absence.model_dump()
    assert set(dumped) == set(ABSENCE_STATES)
    assert LEGACY_NOTHING_FOUND not in dumped
    assert all(s.strip() and s.strip()[-1] in ".:" for s in dumped.values())
    assert len(set(dumped.values())) == 4, "each absence says something different"


@pytest.mark.parametrize("name", sorted(BUILTINS))
def test_kind_blocks_out_fields_and_shapes(name):
    decl = BUILTINS[name].declaration
    assert decl.out, "every routine lists its out fields"
    if decl.result_kind in ("distribution", "graph"):
        assert decl.categories is not None
    if decl.result_kind == "list":
        assert decl.listing is not None
    for f in decl.out:
        if f.kind == "dataset":
            assert f.shape in ROW_SHAPES
    names = [m.name for m in decl.measures]
    assert len(names) == len(set(names))
    assert not any(m.population and m.population not in ("viewer", "repository") for m in decl.measures)


# Fixtures: a client with no native count (so counts fall back to the find) that answers
# every find with three Assets and every relationship query with one relationship.

def _asset(guid, desc=None, cls=(), upd="2026-09-01T00:00:00+00:00"):
    pvm = {"displayName": {"primitiveValue": f"Contribution record for {guid}"},
           "karmaPoints": {"primitiveValue": 7}}
    if desc:
        pvm["description"] = {"primitiveValue": desc}
    classifications = [{"classificationName": c} for c in cls] + [{
        "classificationName": "Anchors", "classificationProperties": {"propertyValueMap": {
            "anchorTypeName": {"primitiveValue": "Person"}, "anchorGUID": {"primitiveValue": f"p-{guid}"}}}}]
    return {"elementGUID": guid, "elementProperties": {"propertyValueMap": pvm}, "classifications": classifications,
            "type": {"typeName": "CSVFile", "superTypeNames": ["DataFile", "Asset"]},
            "elementHeader": {"versions": {"updateTime": upd}}}


_REL = {"end1": {"guid": "sc1", "type": {"typeName": "SolutionComponent"}},
        "end2": {"guid": "a1", "type": {"typeName": "CSVFile", "superTypeNames": ["Asset", "GlossaryTerm"]}},
        "relationshipHeader": {"versions": {"createTime": "2026-09-28T00:00:00+00:00", "createdBy": "erin"}}}


class _NoSubtypes:
    def get_sub_types(self, type_name, **_):
        return "No elements found"


def _clients():
    from unittest.mock import MagicMock
    mgr = MagicMock(spec=["platform_url", "view_server", "find_metadata_elements",
                          "get_control_implementation_summary"])
    mgr.platform_url, mgr.view_server = "https://localhost:9443", "test-server"
    assets = [_asset("a1", "d", ["Confidentiality", "ZoneMembership"]),
              _asset("a2"), _asset("a3", "d", upd="2025-01-01T00:00:00+00:00")]
    # Both fakes page like Egeria (rows from startFrom, then an empty page): the scans read to an empty page.
    mgr.find_metadata_elements.side_effect = lambda body, *a, **k: assets[body.get("startFrom", 0):][:body.get(
        "pageSize") or len(assets)]
    mgr.get_control_implementation_summary.return_value = {"byStatus": {
        "NOT_STARTED": 1, "PLANNED": 0, "PARTIALLY_IMPLEMENTED": 0, "IMPLEMENTED": 2, "OTHER": 0}}
    ce = MagicMock(spec=["get_relationships"])
    ce.get_relationships.side_effect = lambda *a, body=None, **k: [_REL][(body or {}).get("startFrom", 0):]
    return mgr, ce


CALLS = {
    "count_elements": lambda m, c: om.count_elements(m, "Asset"),
    "count_elements_by_property": lambda m, c: om.count_elements_by_property(m, "Asset", "name", "x"),
    "count_relationships": lambda m, c: om.count_relationships(c, "SemanticAssignment"),
    "counts_by_type": lambda m, c: om.counts_by_type(m, [("Files", "CSVFile")]),
    "sum_type_counts": lambda m, c: om.sum_type_counts(m, [("Files", "CSVFile")]),
    "governed_coverage": lambda m, c: om.governed_coverage(m),
    "ownership_coverage": lambda m, c: om.ownership_coverage(m),
    "business_value_signals": lambda m, c: om.business_value_signals(m),
    "certifications_summary": lambda m, c: om.certifications_summary(c, AS_OF),
    "semantic_grounding": lambda m, c: om.semantic_grounding(m, c),
    "people_counts": lambda m, c: om.people_counts(m),
    "feedback_summary": lambda m, c: om.feedback_summary(c),
    "usage_context_counts": lambda m, c: om.usage_context_counts(m),
    "active_contributors": lambda m, c: om.active_contributors(c),
    "karma_leaderboard": lambda m, c: om.karma_leaderboard(m),
    "context_readiness_funnel": lambda m, c: om.context_readiness_funnel(m, c),
    "ai_ready_assets": lambda m, c: om.ai_ready_assets(m, c),
    "drl_readiness_gates": lambda m, c: om.drl_readiness_gates(m, c, AS_OF),
    "contextualised_coverage": lambda m, c: om.contextualised_coverage(m, c),
    "solution_component_realisation": lambda m, c: om.solution_component_realisation(m, c),
    "growth_series": lambda m, c: om.growth_series(m, window="7d", points=3),
    "engagement_series": lambda m, c: om.engagement_series(c, AS_OF, weeks=3),
    "metric_trend": lambda m, c: om.metric_trend(m, c, "count_elements", window="7d", points=2,
                                                 metric_params={"type_name": "Asset"}),
    "term_definition_completeness": lambda m, c: om.term_definition_completeness(m),
    "orphan_glossary_terms": lambda m, c: om.orphan_glossary_terms(m, c),
    "stale_assets": lambda m, c: om.stale_assets(m, AS_OF),
    "control_implementation_summary": lambda m, c: om.control_implementation_summary(m, "soa"),
    "asset_composition": lambda m, c: om.asset_composition(m, _NoSubtypes(), depth=0),
    "saved_query": lambda m, c: __import__("pyegeria.view.saved_query", fromlist=["saved_query"]).saved_query(
        m, "SavedQuery::not-there"),
}

_MISSING = object()


def _resolve(value, path: str):
    """A declared field path against a result: dotted for nested, applied to every row of a list.
    A bare-number result answers the path `value`."""
    if not isinstance(value, (dict, list)):
        return value if path == "value" else _MISSING
    head, _, rest = path.partition(".")
    if isinstance(value, list):
        found = [_resolve(row, path) for row in value]
        return _MISSING if not found or _MISSING in found else found
    if head not in value:
        return _MISSING
    return _resolve(value[head], rest) if rest else value[head]


def test_calls_cover_the_registry():
    assert set(CALLS) == set(BUILTINS)


@pytest.mark.parametrize("name", sorted(CALLS))
def test_declared_value_fields_exist(name):
    om._count_caps.clear()
    om._native_server_ok.clear()
    mgr, ce = _clients()
    if name == "asset_composition":  # counts strictly: give it a native count to answer with
        mgr = __import__("unittest.mock", fromlist=["MagicMock"]).MagicMock(
            spec=["platform_url", "view_server", "count_metadata_elements"])
        mgr.platform_url, mgr.view_server = "https://localhost:9443", "test-server"
        mgr.count_metadata_elements.return_value = {"count": 5}
    result = CALLS[name](mgr, ce)
    decl = BUILTINS[name].declaration
    for m in decl.measures:
        for path in (m.value_field, m.completeness_field, m.basis.denominator_field if m.basis else ""):
            if path:
                assert _resolve(result, path) is not _MISSING, f"{name}: {path} not in the result"
        if not m.as_of.startswith("run."):
            assert _resolve(result, m.as_of) is not _MISSING, f"{name}: as_of {m.as_of} not in the result"
    rows = result if isinstance(result, list) else [result]
    for f in decl.out:
        if isinstance(rows[0], dict):
            assert all(f.name in r for r in rows), f"{name}: out field {f.name} not in the result"
