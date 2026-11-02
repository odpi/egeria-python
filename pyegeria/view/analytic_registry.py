"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Analytic function registry — the "what analytic routines exist to plug into
a FormatSet action's `analytic_function` (Dr.Egeria's `extra_find`)" catalog.

Mirrors `dashboard_sheet_registry.py`'s shape (same env-var-driven JSON/module
config pattern, same runtime registration API, same collision semantics) so
the three registries (report specs, dashboard sheets, analytic functions)
stay consistent for anything that needs to browse or author against them --
Egeria Explorer, Egeria Advisor's report-spec builder, and
`format_set_executor.py`'s own resolution of `analytic_function` declarations.

Unlike report specs, there is no generated/Tinderbox source here (yet) --
BUILTINS is a hand-written list of the analytic functions that already exist
in `pyegeria.view.overview_metrics` (all proven live via the Overview
dashboard's own `/api/overview/*` endpoints; none of this is new analytics,
just registry wiring for functions that already work). A JSON-file-backed
CONFIG tier and a future Egeria-Asset-backed tier are planned as the registry
grows past what's worth hand-writing here (BACKLOG.md NEXT-14 successor
item) -- this module is hand-written and safe to edit, unlike
`base_report_formats.py`.

Each `AnalyticFunctionSpec.function` is a dotted import path, exactly the
string a FormatSet's `extra_find` (compiled into `ActionParameter.analytic_function`)
carries, and exactly what `format_set_executor._resolve_analytic_function`
resolves at call time. `params` documents the function's real keyword
arguments (excluding its leading client argument(s) -- `format_set_executor`
binds those automatically, see `_bind_client_args`) for anything that wants
to render a param-entry form (Egeria Advisor) or a reference doc (Egeria
Explorer), not for validation -- there is deliberately no fixed
required/optional whitelist enforced at call time (see `ActionParameter`'s
docstring in `_output_format_models.py`); an unexpected keyword just raises
Python's own TypeError.
"""

from __future__ import annotations

import os
from importlib.metadata import entry_points
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

from loguru import logger
from pydantic import BaseModel, Field, field_validator, model_validator

__all__ = [
    'AnalyticParam',
    'AnalyticFunctionSpec',
    'AnalyticActionSpec',
    'AnalyticDeclaration',
    'MeasureDeclaration',
    'BasisDeclaration',
    'AbsenceSentences',
    'RESULT_KINDS',
    'ABSENCE_STATES',
    'KNOWN_ANALYTIC_SOURCES',
    'AnalyticRegistryCollision',
    'refresh_analytic_functions',
    'ANALYTIC_ENTRY_POINT_GROUP',
    'analytic_entry_point_errors',
    'get_analytic_registry',
    'analytic_registry_payload',
    'register_analytic_functions',
    'unregister_analytic_function',
    'clear_runtime_analytic_functions',
]


# Known values for AnalyticFunctionSpec.source (ISSUE-149). Suggestive, not a closed list:
# ods = the operational data store, egeria = Egeria metadata, resource = the resource itself.
KNOWN_ANALYTIC_SOURCES = {"ods", "egeria", "resource"}


class AnalyticParam(BaseModel):
    """One keyword argument an analytic function accepts (beyond its leading
    client argument(s), which the executor supplies automatically)."""
    name: str
    type: str = "str"
    required: bool = False
    default: Optional[Any] = None
    description: str = ""


class AnalyticActionSpec(BaseModel):
    """A composite/derived analytic action, formalizing the pattern
    `ai_ready_assets` pioneered by hand (see its docstring) into a declared
    shape (BACKLOG.md NEXT-18, egeria-workspaces): a data-producing **fetch**
    step (typically one of this module's own `find_*`-backed functions, e.g.
    `counts_by_type`) whose raw result is passed to an optional **analytic**
    step, which may itself fetch further related data if needed (e.g. follow
    a relationship to enrich -- exactly what `ai_ready_assets` already does
    inline, just as an undeclared implementation detail rather than a named
    step). Both `fetch` and `analytic` are dotted import paths, resolved and
    client-bound the same way a plain `AnalyticFunctionSpec.function` always
    has been (see `format_set_executor._resolve_analytic_function`/
    `_bind_client_args`, and its `run_analytic_action` for the two-step
    invocation itself).

    Deliberately *not* concerned with which of the resulting attributes
    appear in a given output (TABLE/REPORT/KPI/...) -- that selection is
    `Format.attributes`' existing job (its `key` projects a named field out
    of whatever dict the action returns), unchanged by this model. An action
    ends at producing the full attribute set; formatting picks from it.

    A future non-local step (e.g. a Prefect flow or other remote service,
    rather than an in-process Python callable) would only need `fetch`/
    `analytic` to grow beyond a plain dotted-path string -- not designed
    here, deliberately parked pending that real use case."""
    fetch: str
    analytic: Optional[str] = None
    fetch_params: List[AnalyticParam] = Field(default_factory=list)
    analytic_params: List[AnalyticParam] = Field(default_factory=list)


# Declaration (ISSUE-170): what an analytic function says about its own results,
# so a screen, report or chat answer can show them with no code written for that
# function. The minimum of trellis-analytics' `Declaration` (result kind, measures
# with unit/as-of/basis, the four absence sentences), with the same field names and
# vocabulary, so a trellis declaration validates here too; its richer blocks
# (extents, confidence, answers, ...) are ignored by this model, not refused.

#: The fixed result-kind vocabulary (trellis `RESULT_KINDS`).
RESULT_KINDS = ("measure", "series", "distribution", "list", "graph", "finding", "proposal", "table")

#: The four ways a result can be absent, each a sentence the function declares. Envelope states
#: map onto them: nothing_found -> measured_nothing; not_established -> not_measured (or
#: not_permitted, told apart by the reason); not_applicable -> not_applicable.
ABSENCE_STATES = ("not_measured", "not_permitted", "not_applicable", "measured_nothing")


def _words(value: Any) -> str:
    return " ".join(str(value or "").split())


class BasisDeclaration(BaseModel):
    """The whole a counted measure is part of, so "456 of 1,236 columns" is derived, not written."""
    denominator_field: str  # the result field holding the whole, e.g. "column_count"
    denominator_label: str  # the whole in words, plural, e.g. "columns"

    @model_validator(mode="after")
    def _filled(self) -> "BasisDeclaration":
        if not _words(self.denominator_field) or not _words(self.denominator_label):
            raise ValueError("a basis needs both denominator_field and denominator_label")
        return self


class MeasureDeclaration(BaseModel):
    """One number a function reports. A number never travels without its unit and its as-of."""
    name: str
    unit: str  # in words, plural where it counts things: "tables", "fraction of rows (0-1)"
    as_of: str  # the result field saying when this was measured, e.g. "asOf"
    value_field: str  # the result field holding the value; dotted for nested, trailing [] counts a list
    basis: Optional[BasisDeclaration] = None
    capped_field: str = ""  # the result field that is true when the value is only a lower bound

    @model_validator(mode="after")
    def _filled(self) -> "MeasureDeclaration":
        empty = [f for f in ("name", "unit", "as_of", "value_field") if not _words(getattr(self, f))]
        if empty:
            raise ValueError(f"measure '{self.name}' declares no {', '.join(empty)}: "
                             "a number never travels without its unit and its as-of")
        return self


class AbsenceSentences(BaseModel):
    """The sentence shown for each way a result can be absent. All four are declared."""
    not_measured: str
    not_permitted: str
    not_applicable: str
    measured_nothing: str

    @model_validator(mode="after")
    def _filled(self) -> "AbsenceSentences":
        empty = [s for s in ABSENCE_STATES if not _words(getattr(self, s))]
        if empty:
            raise ValueError(f"absence sentence for {', '.join(empty)} is empty: "
                             "an absence is declared, never improvised")
        return self

    def sentence(self, state: str) -> str:
        return getattr(self, state)


class AnalyticDeclaration(BaseModel):
    """What an analytic function declares about its results: the minimum is `result_kind`,
    `measures` (required for measure/series/distribution/graph) and `absence`."""
    result_kind: str
    measures: List[MeasureDeclaration] = Field(default_factory=list)
    absence: AbsenceSentences

    @field_validator("result_kind")
    @classmethod
    def _kind(cls, value: str) -> str:
        if value not in RESULT_KINDS:
            raise ValueError(f"result_kind '{value}' is not one of {', '.join(RESULT_KINDS)}")
        return value

    @model_validator(mode="after")
    def _measured_kinds_declare_measures(self) -> "AnalyticDeclaration":
        if self.result_kind in ("measure", "series", "distribution", "graph") and not self.measures:
            raise ValueError(f"result_kind '{self.result_kind}' declares no measures")
        return self


class AnalyticFunctionSpec(BaseModel):
    """One entry in the analytic function registry.

    `generic` is the load-bearing field for reuse: it tells a report-spec
    author whether *what* the function counts/aggregates is itself a
    parameter (generic=True -- e.g. `count_elements(type_name=...)`, freely
    retargetable at any element type via a report spec's `analytic_spec_params`),
    or hardcoded inside the function body (generic=False -- e.g.
    `governed_coverage` always counts `GOVERNANCE_CLASSIFICATIONS`; a report
    spec can still point at it, but always gets that one fixed metric --
    retargeting it means editing the Python function, not authoring a new
    report spec). `binding_note` names exactly what's fixed, for the generic=False
    case (blank when generic=True, since there's nothing fixed to name).

    `action`, if set, is a structured (fetch, analytic) breakdown of what
    `function` does internally (see `AnalyticActionSpec`) -- additive only:
    `function` always still resolves to a real, directly-callable entry
    point that returns exactly what `returns` describes (for an
    action-backed entry, a thin composite wrapper -- see `sum_type_counts`
    -- built via `format_set_executor.run_analytic_action`), so every
    existing consumer that only reads `.function` -- including every other
    entry in this registry -- keeps working completely unchanged."""
    name: str
    function: str  # dotted import path, e.g. "pyegeria.view.overview_metrics.growth_series"
    description: str = ""
    returns: str = ""  # human-readable result shape, e.g. "scalar (int)", "list[dict] (time series)"
    generic: bool = False
    binding_note: str = ""
    params: List[AnalyticParam] = Field(default_factory=list)
    action: Optional[AnalyticActionSpec] = None

    # Manifest fields (ISSUE-149), all optional so every existing entry is unchanged.
    # trellis-analytics' RoutineManifest/StepManifest subclass this class and used to
    # carry these themselves.
    kind: Literal["routine", "step"] = "routine"  # routine: runs in the caller; step: a survey-style step
    source: str = ""  # where the data comes from; known values in KNOWN_ANALYTIC_SOURCES
    version: str = ""  # the producer's version, stamped on every result
    envelope: bool = False  # the result carries a state envelope (measured / nothing_found / ...)
    annotation_type: str = ""  # a step's result type, e.g. ResourceMeasureAnnotation; empty for a routine
    resource_types: List[str] = Field(default_factory=list)  # e.g. ["database"]
    family: str = ""  # same word and meaning as FormatSet.family; in Egeria a family is a Collection
    tags: List[str] = Field(default_factory=list)
    # What the results mean (ISSUE-170): result kind, measures with unit/as-of/basis, absence
    # sentences. Optional; trellis-analytics' StepManifest narrows it to its fuller Declaration.
    declaration: Optional[AnalyticDeclaration] = None

    @field_validator("source")
    @classmethod
    def _suggest_known_source(cls, value: str) -> str:
        """Value lists are suggestive: an unknown source warns, never rejects."""
        if value and value not in KNOWN_ANALYTIC_SOURCES:
            logger.warning(f"Analytic source '{value}' is not one of the known values "
                           f"{sorted(KNOWN_ANALYTIC_SOURCES)}; keeping it.")
        return value


class AnalyticFunctionDict(Dict[str, AnalyticFunctionSpec]):
    """Name -> AnalyticFunctionSpec, mirroring FormatSetDict/DashboardSheetDict."""
    pass


def _as_of(description: str = "ISO-8601 asOfTime for a point-in-time value (None = now).") -> AnalyticParam:
    return AnalyticParam(name="as_of", type="str", description=description)


def _strict() -> AnalyticParam:
    return AnalyticParam(name="strict", type="bool", default=False,
                         description="Return None instead of 0 when a count could not be measured "
                                     "(query failed, or the fallback hit the page-size cap). ISSUE-123.")


# ── Built-ins -- every analytic function already proven live via the Overview
# dashboard's /api/overview/* endpoints (overview_handler.py), just not yet
# reachable from a Dr.Egeria report spec. ──────────────────────────────────
_BUILTINS: Dict[str, AnalyticFunctionSpec] = {
    "count_elements": AnalyticFunctionSpec(
        name="count_elements",
        function="pyegeria.view.overview_metrics.count_elements",
        description="Count active elements of a given type, optionally filtered by classification.",
        returns="scalar (int)",
        generic=True,
        params=[
            AnalyticParam(name="type_name", type="str",
                          description="Open metadata type to count, e.g. GlossaryTerm, DigitalProduct. Omit for any type."),
            _as_of(),
            _strict(),
            AnalyticParam(name="classifications", type="list[str]",
                          description="Match ANY of these classification names."),
        ],
    ),
    "counts_by_type": AnalyticFunctionSpec(
        name="counts_by_type",
        function="pyegeria.view.overview_metrics.counts_by_type",
        description="Per-type element counts for a set of (label, type_name) pairs -- a breakdown/"
                    "composition metric, e.g. the assets-by-type chart.",
        returns="list[dict] (breakdown: {label, type, count})",
        generic=True,
        params=[
            AnalyticParam(name="type_map", type="list[tuple[str, str]]", required=True,
                          description="(label, type_name) pairs to count, e.g. [('Data Stores', 'DataStore'), ...]."),
            _as_of(),
            _strict(),
        ],
    ),
    "governed_coverage": AnalyticFunctionSpec(
        name="governed_coverage",
        function="pyegeria.view.overview_metrics.governed_coverage",
        description="Share of assets carrying at least one governance classification, plus a "
                    "by-classification / top-zones breakdown.",
        returns="dict (governedCount, governedCapped, byClassification, topZones)",
        generic=False,
        binding_note="Fixed to GOVERNANCE_CLASSIFICATIONS: ZoneMembership, Confidentiality, "
                     "Criticality, Impact, Retention -- not a parameter.",
        params=[_as_of()],
    ),
    "ownership_coverage": AnalyticFunctionSpec(
        name="ownership_coverage",
        function="pyegeria.view.overview_metrics.ownership_coverage",
        description="Share of assets carrying an Ownership classification (a named owner "
                    "responsible for management/governance decisions), plus a by-owner-type "
                    "breakdown. Distinct from governed_coverage -- data mesh literature names "
                    "'clean, owned, product-based data' as its own foundation for trustworthy "
                    "AI consumption, not a synonym for governance-classification coverage.",
        returns="dict (ownershipCount, ownershipCapped, byOwnerType)",
        generic=False,
        binding_note="Fixed to the Ownership classification -- not a parameter.",
        params=[_as_of()],
    ),
    "business_value_signals": AnalyticFunctionSpec(
        name="business_value_signals",
        function="pyegeria.view.overview_metrics.business_value_signals",
        description="Real signals behind the four Overview dashboard Business Value tiles "
                    "(Risk & Compliance, Productivity, Trust & Adoption, Cost Avoidance): "
                    "Confidentiality-classified asset count, described-asset count, "
                    "ConsolidatedDuplicate-flagged element count -- all proxies with a "
                    "documented causal-claim caveat, not direct measures (NEXT-9).",
        returns="dict (assetTotal, assetCapped, confidentialCount, describedCount, duplicateCount)",
        generic=False,
        binding_note="Fixed to the Asset type hierarchy and Confidentiality/ConsolidatedDuplicate "
                     "classifications -- not a parameter.",
        params=[_as_of()],
    ),
    "certifications_summary": AnalyticFunctionSpec(
        name="certifications_summary",
        function="pyegeria.view.overview_metrics.certifications_summary",
        description="Active/expiring Certification relationships, licenses, and open Exception counts.",
        returns="dict (active, expiring90, soon, licenses, exceptions)",
        generic=False,
        binding_note="Fixed to the Certification and Exception relationship types -- not a parameter.",
        params=[_as_of()],
    ),
    "people_counts": AnalyticFunctionSpec(
        name="people_counts",
        function="pyegeria.view.overview_metrics.people_counts",
        description="Counts of Person / Team / Organization / ITProfile / Community actor profiles.",
        returns="dict (persons, teams, organizations, itProfiles, communities)",
        generic=False,
        binding_note="Fixed to Person/Team/Organization/ITProfile/Community -- not a parameter.",
        params=[_as_of(), _strict()],
    ),
    "feedback_summary": AnalyticFunctionSpec(
        name="feedback_summary",
        function="pyegeria.view.overview_metrics.feedback_summary",
        description="Crowd-sourced feedback counts (ratings/comments/likes/tags/noteLogs) by type, "
                    "via Collaboration OMAS relationships.",
        returns="dict (byType, total)",
        generic=False,
        binding_note="Fixed to Collaboration OMAS's feedback relationship types -- not a parameter.",
        params=[_as_of()],
    ),
    "usage_context_counts": AnalyticFunctionSpec(
        name="usage_context_counts",
        function="pyegeria.view.overview_metrics.usage_context_counts",
        description="InformationSupplyChain and SolutionBlueprint counts -- the two structures that "
                    "put assets in a business usage context (supply chain membership, blueprint "
                    "realization).",
        returns="dict (informationSupplyChains, blueprints)",
        generic=False,
        binding_note="Fixed to InformationSupplyChain and SolutionBlueprint -- not a parameter.",
        params=[_as_of(), _strict()],
    ),
    "semantic_grounding": AnalyticFunctionSpec(
        name="semantic_grounding",
        function="pyegeria.view.overview_metrics.semantic_grounding",
        description="SemanticAssignment relationship count and coverage percent -- the meaning layer "
                    "that grounds AI. Takes two leading clients (mgr, ce) -- the executor supplies the "
                    "same EgeriaTech instance for both.",
        returns="dict (groundingLinks, groundingPct)",
        generic=False,
        binding_note="Fixed to the SemanticAssignment relationship type -- not a parameter.",
        params=[_as_of()],
    ),
    "context_readiness_funnel": AnalyticFunctionSpec(
        name="context_readiness_funnel",
        function="pyegeria.view.overview_metrics.context_readiness_funnel",
        description="Cataloged -> Documented -> Classified -> Lineage-traced -> AI-Ready funnel counts. "
                    "Takes two leading clients (mgr, ce) -- the executor supplies the same EgeriaTech "
                    "instance for both, matching semantic_grounding's convention. This function's own "
                    "aiReady stays None always by design -- it's four independent counts, and aiReady "
                    "needs a true cross-criteria intersection instead. Pair with ai_ready_assets "
                    "(below) for that -- overview_handler.py calls both and merges the result.",
        returns="dict (cataloged, documented, classified, lineage, aiReady)",
        generic=False,
        binding_note="Fixed 5-stage readiness definition baked into the function body -- not a parameter.",
        params=[_as_of()],
    ),
    "ai_ready_assets": AnalyticFunctionSpec(
        name="ai_ready_assets",
        function="pyegeria.view.overview_metrics.ai_ready_assets",
        description="The true 'AI-Ready' composite: Asset elements that are governed AND documented "
                    "AND lineage-traced simultaneously, not three independent counts intersected after "
                    "the fact. First real implementation of the composite/derived analytic metric "
                    "pattern -- see NEXT-18 (egeria-workspaces BACKLOG.md) for why this pattern didn't "
                    "exist here before. Takes two leading clients (mgr, ce), same convention as "
                    "semantic_grounding/context_readiness_funnel.",
        returns="dict (aiReadyCount, total, capped)",
        generic=False,
        binding_note="Fixed to governed+documented+lineage-traced over Asset elements -- not a parameter.",
        params=[_as_of()],
    ),
    "growth_series": AnalyticFunctionSpec(
        name="growth_series",
        function="pyegeria.view.overview_metrics.growth_series",
        description="Snapshot-based growth series (assets/terms/governed/products by default) via "
                    "asOfTime, one point per window step. The one shape SERIES output format "
                    "(a Vega-Lite line chart) is proven against today.",
        returns="list[dict] (time series: {label, date, <series_key>: count, ...})",
        generic=True,
        binding_note="type_map defaults to assets/terms/governed/products but is fully overridable.",
        params=[
            AnalyticParam(name="window", type="str", default="6mo",
                          description="8h|1d|3d|7d|30d|90d|6mo|1y -- sets span + default point count."),
            AnalyticParam(name="points", type="int",
                          description="Override the number of snapshots (2-24)."),
            AnalyticParam(name="type_map", type="list[tuple[str, str, list[str] | None]]",
                          description="Override which series to snapshot; defaults to assets/terms/governed/products."),
        ],
    ),
    "term_definition_completeness": AnalyticFunctionSpec(
        name="term_definition_completeness",
        function="pyegeria.view.overview_metrics.term_definition_completeness",
        description="Share of GlossaryTerms carrying a non-empty description -- a definitions-"
                    "coverage metric, distinct from semantic_grounding (term<->asset linkage, not "
                    "whether the term itself is actually defined).",
        returns="dict (total, defined, undefinedPct)",
        generic=False,
        binding_note="Fixed to GlossaryTerm's description property -- not a parameter.",
        params=[_as_of()],
    ),
    "active_contributors": AnalyticFunctionSpec(
        name="active_contributors",
        function="pyegeria.view.overview_metrics.active_contributors",
        description="Distinct usernames behind at least one feedback relationship (ratings/comments/"
                    "likes/tags/noteLogs) -- an engagement signal feedback_summary's raw relationship "
                    "counts don't give you (one prolific commenter vs. many occasional ones).",
        returns="dict (contributors, byType)",
        generic=False,
        binding_note="Fixed to Collaboration OMAS's feedback relationship types -- not a parameter.",
        params=[_as_of()],
    ),
    "sum_type_counts": AnalyticFunctionSpec(
        name="sum_type_counts",
        function="pyegeria.view.overview_metrics.sum_type_counts",
        description="Sum of counts_by_type() across a caller-given (label, type_name) list -- "
                    "e.g. the Overview dashboard's 'Cataloged Assets' total. First real registered "
                    "user of the fetch+analytic action shape (see AnalyticActionSpec) -- fetch is "
                    "counts_by_type itself (already registered above, reused as-is), analytic is a "
                    "small sum-reducer over its result; `function` above is the thin composite "
                    "wrapper that runs both via run_analytic_action, so calling it directly (the "
                    "old, single-function path) still works exactly like every other entry here.",
        returns="dict (total, byType)",
        generic=True,
        action=AnalyticActionSpec(
            fetch="pyegeria.view.overview_metrics.counts_by_type",
            analytic="pyegeria.view.overview_metrics.sum_counts",
            fetch_params=[
                AnalyticParam(name="type_map", type="list[tuple[str, str]]", required=True,
                              description="(label, type_name) pairs to count and sum."),
                _as_of(),
            ],
        ),
        params=[
            AnalyticParam(name="type_map", type="list[tuple[str, str]]", required=True,
                          description="(label, type_name) pairs to count and sum."),
            _as_of(),
        ],
    ),
    "count_elements_by_property": AnalyticFunctionSpec(
        name="count_elements_by_property",
        function="pyegeria.view.overview_metrics.count_elements_by_property",
        description="Count active elements of a given type whose named string property equals a "
                    "given value -- e.g. DigitalProduct elements with deploymentStatus=ACTIVE. Same "
                    "native-count-with-fallback seam as count_elements, one cheap native COUNT call "
                    "per distinct value, no element fetch.",
        returns="scalar (int)",
        generic=True,
        params=[
            AnalyticParam(name="type_name", type="str", required=True,
                          description="Open metadata type to count, e.g. DigitalProduct."),
            AnalyticParam(name="property_name", type="str", required=True,
                          description="String property to match, e.g. deploymentStatus."),
            AnalyticParam(name="property_value", type="str", required=True,
                          description="Value to match the property against, e.g. ACTIVE."),
            _as_of(),
            _strict(),
        ],
    ),
    "contextualised_coverage": AnalyticFunctionSpec(
        name="contextualised_coverage",
        function="pyegeria.view.overview_metrics.contextualised_coverage",
        description="Percent of Assets given business/solution-design context via an ImplementedBy "
                    "relationship to a SolutionComponent. A proxy, not the literal 'participates in "
                    "an ISC/blueprint' metric -- confirms some solution-design context exists, not "
                    "that the specific SolutionComponent is itself wired into an ISC/blueprint (a "
                    "second hop this function doesn't take). Takes two leading clients (mgr, ce), "
                    "same convention as semantic_grounding.",
        returns="dict (contextualisedCount, assetTotal, contextualisedPct)",
        generic=False,
        binding_note="Fixed to the ImplementedBy relationship, filtered to Asset-subtype ends -- not a parameter.",
        params=[_as_of()],
    ),
    "karma_leaderboard": AnalyticFunctionSpec(
        name="karma_leaderboard",
        function="pyegeria.view.overview_metrics.karma_leaderboard",
        description="Top-N people by karma -- one bounded ContributionRecord fetch, karmaPoints is a "
                    "scalar property on the record itself (not derived from counting related things), "
                    "filtered to the given anchor type(s) via each record's own Anchors classification.",
        returns="list[dict] (name, karmaPoints, anchorGuid, anchorType), longest-karma first",
        generic=False,
        binding_note="Fixed to ContributionRecord.karmaPoints -- top_n and anchor_types tune the "
                     "result but don't change what's being measured.",
        params=[
            AnalyticParam(name="top_n", type="int", default=10, description="How many entries to return."),
            AnalyticParam(name="anchor_types", type="list[str]", default=["Person"],
                          description="Anchor typeName(s) to include, e.g. ['Person', 'ITProfile']."),
            _as_of(),
        ],
    ),
    "engagement_series": AnalyticFunctionSpec(
        name="engagement_series",
        function="pyegeria.view.overview_metrics.engagement_series",
        description="Weekly-bucketed feedback-event trend (comments/ratings/likes/tags/noteLogs), "
                    "zero-filled across the trailing window -- reuses the same 5 relationship-type "
                    "queries feedback_summary() already makes, keeping createTime instead of only "
                    "the count. Takes ce as its leading client.",
        returns="list[dict] (week, comments, ratings, likes, tags, noteLogs, total), oldest week first",
        generic=False,
        binding_note="Fixed to Collaboration OMAS's 5 feedback relationship types -- weeks tunes the window, not what's measured.",
        params=[
            AnalyticParam(name="weeks", type="int", default=12, description="Trailing window size, in weeks."),
            _as_of(),
        ],
    ),
    "orphan_glossary_terms": AnalyticFunctionSpec(
        name="orphan_glossary_terms",
        function="pyegeria.view.overview_metrics.orphan_glossary_terms",
        description="Approved-but-unassigned glossary terms -- a term with no SemanticAssignment "
                    "relationship to anything was authored but never put to use grounding the "
                    "catalog. One bounded SemanticAssignment fetch, distinct GlossaryTerm-end GUID "
                    "count is the 'referenced' set; orphan = term total - referenced. Takes two "
                    "leading clients (mgr, ce), same convention as semantic_grounding.",
        returns="dict (termTotal, referencedCount, orphanCount)",
        generic=False,
        binding_note="Fixed to the SemanticAssignment relationship type and GlossaryTerm elements -- not a parameter.",
        params=[_as_of()],
    ),
    "stale_assets": AnalyticFunctionSpec(
        name="stale_assets",
        function="pyegeria.view.overview_metrics.stale_assets",
        description="Assets with no update in the last N days (default 180) -- candidates for "
                    "archival review. One bounded Asset element fetch, each element's own version "
                    "metadata compared against the cutoff, no relationship traversal.",
        returns="dict (staleCount, assetTotal)",
        generic=False,
        binding_note="Fixed to the Asset type -- population isn't a parameter, but the staleness threshold (days) is.",
        params=[
            AnalyticParam(name="days", type="int", default=180, description="Staleness threshold, in days."),
            _as_of(),
        ],
    ),
    "metric_trend": AnalyticFunctionSpec(
        name="metric_trend",
        function="pyegeria.view.overview_metrics.metric_trend",
        description="Turn any single-snapshot function in this module into a time series, by "
                    "re-calling it once per asOfTime snapshot -- the same windowing growth_series "
                    "uses, generalized to any function here instead of one hardcoded type_map. Takes "
                    "two leading clients (mgr, ce) -- the executor supplies the same EgeriaTech "
                    "instance for both, matching semantic_grounding's convention.",
        returns="list[dict] (time series: {label, date, **snapshot})",
        generic=True,
        params=[
            AnalyticParam(name="metric_path", type="str", required=True,
                          description="Registered name of the target analytic function, e.g. "
                                       "'governed_coverage'. A dotted path is deprecated."),
            AnalyticParam(name="window", type="str", default="6mo",
                          description="8h|1d|3d|7d|30d|90d|6mo|1y -- sets span + default point count."),
            AnalyticParam(name="points", type="int",
                          description="Override the number of snapshots (2-24)."),
            AnalyticParam(name="metric_params", type="dict",
                          description="Extra keyword arguments forwarded to the target function at "
                                       "every snapshot (e.g. classifications for count_elements)."),
        ],
    ),
    "control_implementation_summary": AnalyticFunctionSpec(
        name="control_implementation_summary",
        function="pyegeria.view.overview_metrics.control_implementation_summary",
        description="Applicable controls in a statement of applicability, counted by implementation "
                    "status (NOT_STARTED, PLANNED, PARTIALLY_IMPLEMENTED, IMPLEMENTED, OTHER).",
        returns="dict ({status: count})",
        generic=False,
        binding_note="Fixed to the ControlApplicability relationships of one StatementOfApplicability.",
        params=[
            AnalyticParam(name="soa_guid", type="str", required=True,
                          description="GUID of the statement of applicability."),
        ],
    ),
}

_RUNTIME_ANALYTIC_FUNCTIONS = AnalyticFunctionDict()
_CONFIG_ANALYTIC_FUNCTIONS = AnalyticFunctionDict()

# Installed packages register analytic functions and steps through this entry-point
# group (ISSUE-172; the `trellis.analytics` alias was removed in 6.2.19). An entry point names an AnalyticFunctionSpec (or subclass), a list of them, or
# a callable returning either. Read lazily on first use of the registry; only the
# manifests are loaded then -- a function's own module is imported on its first run,
# by format_set_executor._resolve_analytic_function.
ANALYTIC_ENTRY_POINT_GROUP = "pyegeria.analytics"
_ENTRY_POINT_ANALYTIC_FUNCTIONS: Optional[AnalyticFunctionDict] = None  # None = not read yet
_ENTRY_POINT_ERRORS: Dict[str, str] = {}


class AnalyticRegistryCollision(ValueError):
    """Raised when two analytic-registry sources define the same function name."""
    pass


def _add_with_collision_check(target: AnalyticFunctionDict, new: Dict[str, AnalyticFunctionSpec], source: str) -> None:
    for name in new.keys():
        if name in target.keys():
            raise AnalyticRegistryCollision(
                f"Analytic function '{name}' already defined; conflict from {source}")
    for k, v in new.items():
        target[k] = v


def _load_json_file(path: str) -> AnalyticFunctionDict:
    p = Path(os.path.expanduser(path)).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Analytic functions JSON not found: {p}")
    import json
    raw = json.loads(p.read_text(encoding="utf-8"))
    return AnalyticFunctionDict({name: AnalyticFunctionSpec(**spec) for name, spec in raw.items()})


def refresh_analytic_functions() -> None:
    """Reload the CONFIG tier from JSON files and/or modules. Environment variables:
      - PYEGERIA_ANALYTIC_FUNCTIONS_JSON: comma-separated JSON file paths
      - PYEGERIA_ANALYTIC_FUNCTIONS_MODULES: comma-separated module callables
        (pkg.mod:func or pkg.mod.func) returning a dict/AnalyticFunctionDict
    Collisions across sources (including against BUILTINS) raise AnalyticRegistryCollision.
    Also forgets the installed (entry-point) tier, so it is re-read on next use.
    """
    global _CONFIG_ANALYTIC_FUNCTIONS, _ENTRY_POINT_ANALYTIC_FUNCTIONS
    _CONFIG_ANALYTIC_FUNCTIONS = AnalyticFunctionDict()
    _ENTRY_POINT_ANALYTIC_FUNCTIONS = None  # installed packages are re-read on next use

    json_paths = os.getenv("PYEGERIA_ANALYTIC_FUNCTIONS_JSON", "").strip()
    if json_paths:
        for raw in json_paths.split(","):
            raw = raw.strip()
            if not raw:
                continue
            loaded = _load_json_file(raw)
            _add_with_collision_check(_CONFIG_ANALYTIC_FUNCTIONS, loaded, source=f"JSON:{raw}")

    modules = os.getenv("PYEGERIA_ANALYTIC_FUNCTIONS_MODULES", "").strip()
    if modules:
        for m in modules.split(","):
            m = m.strip()
            if not m:
                continue
            if ":" in m:
                pkg, func = m.split(":", 1)
            else:
                pkg, func = m.rsplit(".", 1)
            mod = __import__(pkg, fromlist=[func])
            loader = getattr(mod, func)
            loaded = loader()
            if not isinstance(loaded, AnalyticFunctionDict):
                loaded = AnalyticFunctionDict(loaded)
            _add_with_collision_check(_CONFIG_ANALYTIC_FUNCTIONS, loaded, source=f"MODULE:{m}")


def _read_entry_points() -> Tuple[AnalyticFunctionDict, Dict[str, str]]:
    """Load every manifest in the entry-point groups. A broken entry point is recorded
    in the returned errors, naming it, and the rest still load."""
    found = AnalyticFunctionDict()
    errors: Dict[str, str] = {}
    for group in (ANALYTIC_ENTRY_POINT_GROUP,):
        for ep in entry_points(group=group):
            label = f"{group}:{ep.name}"
            try:
                obj = ep.load()
                if callable(obj) and not isinstance(obj, AnalyticFunctionSpec):
                    obj = obj()
                items = obj if isinstance(obj, (list, tuple)) else [obj]
                for spec in items:
                    if not isinstance(spec, AnalyticFunctionSpec):
                        raise TypeError(f"{type(spec).__name__} is not an AnalyticFunctionSpec")
                    prior = found.get(spec.name)
                    if prior is not None and prior.function != spec.function:
                        raise AnalyticRegistryCollision(
                            f"'{spec.name}' is already provided by another entry point as {prior.function}")
                    found[spec.name] = spec
            except Exception as exc:  # noqa: BLE001 -- one broken package must not hide the others
                errors[label] = f"entry point {label} ({ep.value}) could not be loaded: {exc}"
                logger.warning(errors[label])
    return found, errors


def _entry_point_functions() -> AnalyticFunctionDict:
    global _ENTRY_POINT_ANALYTIC_FUNCTIONS, _ENTRY_POINT_ERRORS
    if _ENTRY_POINT_ANALYTIC_FUNCTIONS is None:
        _ENTRY_POINT_ANALYTIC_FUNCTIONS, _ENTRY_POINT_ERRORS = _read_entry_points()
    return _ENTRY_POINT_ANALYTIC_FUNCTIONS


def analytic_entry_point_errors() -> Dict[str, str]:
    """Entry points that are installed but could not be loaded, each with a sentence
    naming it and the error (empty when every one loaded, or none is installed)."""
    _entry_point_functions()
    return dict(_ENTRY_POINT_ERRORS)


def get_analytic_registry() -> AnalyticFunctionDict:
    """Combine built-ins, config-loaded, installed (entry-point) and runtime-registered
    analytic functions. Enforce no duplicate names across all sources, except that an
    installed function whose name is already a built-in or config entry is skipped and
    reported by analytic_entry_point_errors(), so an installed package can't break the
    registry for everyone."""
    combined = AnalyticFunctionDict()
    _add_with_collision_check(combined, _BUILTINS, source="BUILTINS")
    _add_with_collision_check(combined, _CONFIG_ANALYTIC_FUNCTIONS, source="CONFIG")
    for name, spec in _entry_point_functions().items():
        if name in combined:
            label = f"entry point function '{name}'"
            if label not in _ENTRY_POINT_ERRORS:
                _ENTRY_POINT_ERRORS[label] = (f"{label} ({spec.function}) was skipped: the name is already "
                                              f"defined by a built-in or config entry")
                logger.warning(_ENTRY_POINT_ERRORS[label])
            continue
        combined[name] = spec
    _add_with_collision_check(combined, _RUNTIME_ANALYTIC_FUNCTIONS, source="RUNTIME")
    return combined


def analytic_registry_payload() -> dict:
    """JSON-ready payload for an API endpoint (e.g. Egeria Explorer/Advisor's
    'browse analytic functions' view)."""
    registry = get_analytic_registry()
    return {
        "total": len(registry),
        "functions": {name: spec.dict() for name, spec in registry.items()},
        "entry_point_errors": analytic_entry_point_errors(),
    }


def register_analytic_functions(new_functions: Union[AnalyticFunctionDict, dict], *, source: str = "runtime") -> None:
    """Dynamically add analytic functions at runtime. Raises on duplicate name."""
    global _RUNTIME_ANALYTIC_FUNCTIONS
    if not isinstance(new_functions, AnalyticFunctionDict):
        new_functions = AnalyticFunctionDict(
            {k: (v if isinstance(v, AnalyticFunctionSpec) else AnalyticFunctionSpec(**v))
             for k, v in new_functions.items()}
        )
    existing = get_analytic_registry()
    for name in new_functions.keys():
        if name in existing.keys():
            raise AnalyticRegistryCollision(
                f"Analytic function '{name}' already exists; cannot register from {source}")
    for k, v in new_functions.items():
        _RUNTIME_ANALYTIC_FUNCTIONS[k] = v


def unregister_analytic_function(name: str) -> bool:
    return bool(_RUNTIME_ANALYTIC_FUNCTIONS.pop(name, None))


def clear_runtime_analytic_functions() -> None:
    _RUNTIME_ANALYTIC_FUNCTIONS.clear()
