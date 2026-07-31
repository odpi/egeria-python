"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Analytic Function demo report specs -- one FormatSet per entry in
`pyegeria.view.analytic_registry`, proving each analytic function is
actually runnable as a report spec (not just documented in the registry).

Hand-written, mirroring egeria-workspaces-fs's `overview_specs.py` tile
pattern -- these are reference/demo specs, not Dr.Egeria-authored commands,
so there is deliberately no Tinderbox/compact-JSON/`refresh_specs` step here
(see analytic_registry.py's own module docstring for the same reasoning).
Unlike `overview_specs.py`'s tiles though, these ARE real, executable
FormatSets meant to be registered into pyegeria's own report-spec registry
(`base_report_formats.get_report_registry()`) via `register_report_specs`,
so they show up in the same places every other report spec does -- Egeria
Explorer's Report Specs browser, `/api/report-specs`, `exec_report_spec`.

IMPORTANT -- read before adding a new demo spec: every analytic function is
runnable from *any* report spec that points `action.analytic_function` at
it; these demo specs exist purely to prove that and give a copy-pasteable
example, not because the function is otherwise unreachable. Each spec's
`description` states plainly whether the underlying function is GENERIC
(the "what" it counts is itself a parameter -- retarget it freely via
`analytic_spec_params`) or a FIXED metric (the vocabulary is hardcoded in
the function body -- this demo spec IS that one metric, not a template for
others). See `AnalyticFunctionSpec.generic`/`binding_note` for the
machine-readable version of the same distinction.
"""

from __future__ import annotations

from typing import Dict

from pyegeria.view._output_format_models import (
    ActionParameter, Attribute, Format, FormatSet,
)
from pyegeria.view.analytic_registry import get_analytic_registry

FAMILY = "Analytic Function Demo"

_GENERIC_NOTE = (
    "GENERIC function -- the metric this counts is a parameter "
    "(`analytic_spec_params`), not fixed. This spec shows one example "
    "binding; copy it and change the params to count something else "
    "entirely with the same function."
)


def _fixed_note(binding_note: str) -> str:
    return f"FIXED metric -- {binding_note} This spec always returns that one metric."


def _demo(
    *, heading: str, what: str, analytic_function_name: str,
    demo_params: dict, result_shape: str, chart_types: list = None,
) -> FormatSet:
    spec = get_analytic_registry()[analytic_function_name]
    note = _GENERIC_NOTE if spec.generic else _fixed_note(spec.binding_note)
    types = ["DICT", "JSON"] + list(chart_types or [])
    params_note = (
        f" Default params (edit/override at run time): {demo_params}."
        if demo_params else ""
    )
    return FormatSet(
        heading=heading,
        description=f"{what} {note} Result shape: {result_shape}.{params_note}",
        family=FAMILY,
        target_type=None,
        # No declared attributes/columns: an analytic result's real keys vary
        # per function (scalar/dict/list-of-dict) and don't match any fixed
        # column list, so DICT/JSON rendering falls back to auto-deriving
        # columns from the result itself (see type-explorer.html's
        # DictResultView) rather than showing a bogus declared column that
        # never matches the data.
        formats=[Format(types=types, attributes=[])],
        action=ActionParameter(
            function="", analytic_function=spec.function, analytic_spec_params=demo_params,
        ),
    )


_DEMOS: Dict[str, FormatSet] = {
    "Analytic Demo - Element Count by Type": _demo(
        heading="Element Count by Type",
        what="Counts active GlossaryTerm elements.",
        analytic_function_name="count_elements",
        demo_params={"type_name": "GlossaryTerm"},
        result_shape="scalar (int)",
    ),
    "Analytic Demo - Assets by Type Breakdown": _demo(
        heading="Assets by Type Breakdown",
        what="Per-type counts across the core asset/infrastructure types -- pick BAR or PIE "
             "below for a chart, DICT/JSON for the raw {label, type, count} rows.",
        analytic_function_name="counts_by_type",
        demo_params={"type_map": [
            ["Data Stores", "DataStore"], ["Data Sets", "DataSet"],
            ["Software Components", "DeployedSoftwareComponent"],
        ]},
        result_shape="list[dict] ({label, type, count})",
        chart_types=["BAR", "PIE"],
    ),
    "Analytic Demo - Governance Coverage": _demo(
        heading="Governance Classification Coverage",
        what="Count of elements carrying at least one governance classification "
             "(ZoneMembership/Confidentiality/Criticality/Impact/Retention) -- NOT a percentage "
             "despite 'coverage' in the name (there's no cheap total-elements denominator to "
             "divide by yet). governedCapped=true means the query hit its result-page cap "
             "(DEFAULT_CAP), so governedCount is a floor, not exact, when true. byClassification "
             "and topZones are nested breakdowns of the same governedCount elements -- pick BAR "
             "below for a chart of byClassification.",
        analytic_function_name="governed_coverage",
        demo_params={},
        result_shape="dict (governedCount, governedCapped, byClassification, topZones)",
        chart_types=["BAR"],
    ),
    "Analytic Demo - Certifications and Exceptions": _demo(
        heading="Certifications & Exceptions Summary",
        what="Active/expiring Certification relationships and License counts. 'exceptions' is a "
             "GENERAL open-governance-Exception count (any Exception relationship in the "
             "repository) -- it is NOT scoped to certifications/licenses specifically, despite "
             "sitting in this same summary; treat it as a separate metric riding along here.",
        analytic_function_name="certifications_summary",
        demo_params={},
        result_shape="dict (active, expiring90, soon, licenses, exceptions)",
        chart_types=["BAR"],
    ),
    "Analytic Demo - People and Community": _demo(
        heading="People & Community Counts",
        what="Counts of Person/Team/Organization/ITProfile/Community actor profiles.",
        analytic_function_name="people_counts",
        demo_params={},
        result_shape="dict (persons, teams, organizations, itProfiles, communities)",
        chart_types=["BAR", "PIE"],
    ),
    "Analytic Demo - Feedback Summary": _demo(
        heading="Crowd-sourced Feedback Summary",
        what="Ratings/comments/likes/tags/noteLogs counts by type -- pick BAR below for a "
             "by-type breakdown chart. A trend over time isn't available from this metric yet "
             "(feedback_summary is a point-in-time snapshot, not a series) -- a real gap for later.",
        analytic_function_name="feedback_summary",
        demo_params={},
        result_shape="dict (byType, total)",
        chart_types=["BAR"],
    ),
    "Analytic Demo - Usage Context: Supply Chains & Blueprints": _demo(
        heading="Usage Context: Supply Chains & Blueprints",
        what="InformationSupplyChain and SolutionBlueprint counts -- the two structures that put "
             "assets in a business usage context (supply chain membership, blueprint realization).",
        analytic_function_name="usage_context_counts",
        demo_params={},
        result_shape="dict (informationSupplyChains, blueprints)",
    ),
    "Analytic Demo - Semantic Grounding": _demo(
        heading="Semantic Grounding Coverage",
        what="groundingLinks = count of SemanticAssignment relationships (term<->asset). "
             "groundingPct = that count as a percent of the broad Asset supertype count "
             "(i.e. 'percent of Assets' as the denominator, capped at 100 -- an asset with "
             "multiple assignments can push the raw ratio over 100%, which is why it's capped, "
             "not because grounding coverage is literally bounded there). A per-asset detail "
             "breakdown (which assets are/aren't grounded) isn't available from this metric --  "
             "a real gap for later.",
        analytic_function_name="semantic_grounding",
        demo_params={},
        result_shape="dict (groundingLinks, groundingPct)",
    ),
    "Analytic Demo - AI Context Readiness": _demo(
        heading="AI Context Readiness Funnel",
        what="Only 'cataloged' (Asset supertype count) and 'classified' (elements matching ANY "
             "of the same governance classifications governed_coverage uses) are actually "
             "computed today. 'documented', 'lineage', and 'aiReady' are always None -- each "
             "needs a traversal query (e.g. lineage relationships, a documentation-completeness "
             "rule) that doesn't exist yet as a cheap count; they're placeholders for a real "
             "funnel definition, not yet a complete one.",
        analytic_function_name="context_readiness_funnel",
        demo_params={},
        result_shape="dict (cataloged, documented, classified, lineage, aiReady)",
    ),
    "Analytic Demo - Catalog Growth Trend": _demo(
        heading="Catalog Growth Trend (6 Month)",
        what="Snapshot-based growth series -- assets/terms/governed/products, one point "
             "per window step. Run with output_format SERIES for a Vega-Lite line chart.",
        analytic_function_name="growth_series",
        demo_params={"window": "6mo"},
        result_shape="list[dict] (time series: {label, date, <series_key>: count, ...})",
        chart_types=["SERIES"],
    ),
}


def get_analytic_demo_specs() -> Dict[str, FormatSet]:
    """Loader entry point -- usable directly, or via
    PYEGERIA_REPORT_FORMATS_MODULES=pyegeria.view.analytic_demo_specs:get_analytic_demo_specs
    (see base_report_formats.refresh_report_specs)."""
    return dict(_DEMOS)


def register_analytic_demo_specs() -> None:
    """Register these demo specs into the RUNTIME tier of pyegeria's report-spec
    registry, so they appear in get_report_registry()/Egeria Explorer/
    /api/report-specs alongside every other report spec. Call once per process
    (e.g. at app startup) -- calling twice raises ReportFormatCollision, same
    as any duplicate report-spec registration."""
    from pyegeria.view.base_report_formats import register_report_specs
    register_report_specs(get_analytic_demo_specs(), source="analytic_demo_specs")
