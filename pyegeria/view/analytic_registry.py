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
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from loguru import logger
from pydantic import BaseModel, Field

__all__ = [
    'AnalyticParam',
    'AnalyticFunctionSpec',
    'AnalyticRegistryCollision',
    'refresh_analytic_functions',
    'get_analytic_registry',
    'analytic_registry_payload',
    'register_analytic_functions',
    'unregister_analytic_function',
    'clear_runtime_analytic_functions',
]


class AnalyticParam(BaseModel):
    """One keyword argument an analytic function accepts (beyond its leading
    client argument(s), which the executor supplies automatically)."""
    name: str
    type: str = "str"
    required: bool = False
    default: Optional[Any] = None
    description: str = ""


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
    case (blank when generic=True, since there's nothing fixed to name)."""
    name: str
    function: str  # dotted import path, e.g. "pyegeria.view.overview_metrics.growth_series"
    description: str = ""
    returns: str = ""  # human-readable result shape, e.g. "scalar (int)", "list[dict] (time series)"
    generic: bool = False
    binding_note: str = ""
    params: List[AnalyticParam] = Field(default_factory=list)


class AnalyticFunctionDict(Dict[str, AnalyticFunctionSpec]):
    """Name -> AnalyticFunctionSpec, mirroring FormatSetDict/DashboardSheetDict."""
    pass


def _as_of(description: str = "ISO-8601 asOfTime for a point-in-time value (None = now).") -> AnalyticParam:
    return AnalyticParam(name="as_of", type="str", description=description)


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
        params=[_as_of()],
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
        params=[_as_of()],
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
                    "instance for both, matching semantic_grounding's convention. aiReady remains None "
                    "(needs a true cross-criteria intersection -- see NEXT-18, composite/derived metrics).",
        returns="dict (cataloged, documented, classified, lineage, aiReady)",
        generic=False,
        binding_note="Fixed 5-stage readiness definition baked into the function body -- not a parameter.",
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
                          description="Dotted import path of the target function, e.g. "
                                       "'pyegeria.view.overview_metrics.governed_coverage'."),
            AnalyticParam(name="window", type="str", default="6mo",
                          description="8h|1d|3d|7d|30d|90d|6mo|1y -- sets span + default point count."),
            AnalyticParam(name="points", type="int",
                          description="Override the number of snapshots (2-24)."),
            AnalyticParam(name="metric_params", type="dict",
                          description="Extra keyword arguments forwarded to the target function at "
                                       "every snapshot (e.g. classifications for count_elements)."),
        ],
    ),
}

_RUNTIME_ANALYTIC_FUNCTIONS = AnalyticFunctionDict()
_CONFIG_ANALYTIC_FUNCTIONS = AnalyticFunctionDict()


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
    """
    global _CONFIG_ANALYTIC_FUNCTIONS
    _CONFIG_ANALYTIC_FUNCTIONS = AnalyticFunctionDict()

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


def get_analytic_registry() -> AnalyticFunctionDict:
    """Combine built-ins, config-loaded, and runtime-registered analytic functions.
    Enforce no duplicate names across all sources."""
    combined = AnalyticFunctionDict()
    _add_with_collision_check(combined, _BUILTINS, source="BUILTINS")
    _add_with_collision_check(combined, _CONFIG_ANALYTIC_FUNCTIONS, source="CONFIG")
    _add_with_collision_check(combined, _RUNTIME_ANALYTIC_FUNCTIONS, source="RUNTIME")
    return combined


def analytic_registry_payload() -> dict:
    """JSON-ready payload for an API endpoint (e.g. Egeria Explorer/Advisor's
    'browse analytic functions' view)."""
    registry = get_analytic_registry()
    return {
        "total": len(registry),
        "functions": {name: spec.dict() for name, spec in registry.items()},
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
