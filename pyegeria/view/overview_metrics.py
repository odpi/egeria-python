"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Reusable metric/KPI functions extracted from the Egeria Overview dashboard
(egeria-workspaces `overview_handler.py`) so they're callable independently
of that one FastAPI app -- the palette a new Dashboard Sheet's placements
can reference once a generic execution engine exists (see egeria-workspaces
`OVERVIEW_REPORTING_MODEL.md` §10, "NEXT-10 P3" for why that engine doesn't
exist yet and this module is a deliberate first step towards it, not the
engine itself).

Design boundary: every function here takes an **already-constructed,
already-authenticated** pyegeria client (`MetadataExpert` for element counts,
`ClassificationExplorer` for relationship counts) as its first argument.
Client construction/auth (URL, server, user credentials, bearer tokens) stays
app-level -- that's portal-specific, not reusable Egeria-query logic. This
mirrors the boundary `vega_utilities.py` and `_output_dashboard_sheet_models.py`
already use: reusable computation here, app wiring stays in the app.

Every function is independently callable, independently testable (mock the
client), and returns a plain value or small dict -- no HTTP/caching/FastAPI
concerns. `overview_handler.py` is the reference caller; see its git history
for the original inline versions this was extracted from.
"""

import inspect
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from loguru import logger

from pyegeria.core._globals import max_paging_size

__all__ = [
    "DEFAULT_CAP",
    "GOVERNANCE_CLASSIFICATIONS",
    "count_elements",
    "count_relationships",
    "counts_by_type",
    "governed_coverage",
    "ownership_coverage",
    "business_value_signals",
    "certifications_summary",
    "semantic_grounding",
    "context_readiness_funnel",
    "ai_ready_assets",
    "asset_modality",
    "drl_readiness_gates",
    "people_counts",
    "feedback_summary",
    "usage_context_counts",
    "contextualised_coverage",
    "karma_leaderboard",
    "engagement_series",
    "growth_series",
    "metric_trend",
    "term_definition_completeness",
    "active_contributors",
    "WINDOWS",
    "growth_label",
]

# Same ceiling used elsewhere in the Overview app (and the wider portal) --
# Egeria's find API returns paged element lists with no total-count metadata,
# so counts are capped here unless the server supports native counting.
# Derived from pyegeria's shared, env-configurable max_paging_size (EGERIA_MAX_
# PAGE_SIZE / "Egeria Max Page Size") rather than an independent hardcoded
# literal, so a future Egeria server-side page-size limit change (see
# max_paging_size's own comment -- hit live 2026-08-17,
# findRelationshipsBetweenMetadataElements rejected a hardcoded 5000 as
# "greater than the allowable maximum of 1000") is a config edit, not another
# hunt across every module with its own copy of this number.
DEFAULT_CAP = max_paging_size

# Governed-data classifications that count as "governed" (single-condition
# tallies only -- some connectors' matchClassifications ANY/ALL silently
# return zero once 2+ conditions are present, so every caller here keeps to
# a single ANY-over-these-names query, never combining with another filter).
GOVERNANCE_CLASSIFICATIONS = ("ZoneMembership", "Confidentiality", "Criticality", "Impact", "Retention")

# Time-window -> (total span seconds, default #points) for growth_series.
WINDOWS = {
    "8h":  (8 * 3600,       8),
    "1d":  (86400,          6),
    "3d":  (3 * 86400,      6),
    "7d":  (7 * 86400,      7),
    "30d": (30 * 86400,     6),
    "90d": (90 * 86400,     7),
    "6mo": (180 * 86400,    6),
    "1y":  (365 * 86400,    12),
}


def growth_label(d, span_s: int) -> str:
    """Format a snapshot date for a growth-series point, granularity following span."""
    if span_s <= 2 * 86400:
        return d.strftime("%H:00")          # hourly / intraday
    if span_s <= 120 * 86400:
        return d.strftime("%-d %b")         # daily / weekly
    return d.strftime("%b")                 # monthly


# ── count seam -- native Egeria instance counting when available ────────────
# Egeria added native counting in odpi/egeria#9168 (MetadataExpert.
# count_metadata_elements / count_relationships_between_elements -> a real
# SELECT COUNT(*), no result-set materialization). Used when the client
# exposes the method AND the target server supports it; otherwise falls back
# to len(find/get) -- same result, just heavier. The per-server capability
# cache means a single failed native probe on an older server disables
# further attempts rather than paying a failed round-trip on every count.

_ELEMENT_COUNT_CANDIDATES = ("count_metadata_elements", "get_metadata_element_count")
_REL_COUNT_CANDIDATES = ("count_relationships_between_elements", "count_relationships")
_count_caps: Dict[str, Optional[str]] = {}
_native_server_ok: Dict[str, bool] = {}


def _server_key(client) -> str:
    return f"{getattr(client, 'platform_url', '')}|{getattr(client, 'view_server', '')}"


def _native_disabled(client) -> bool:
    return _native_server_ok.get(_server_key(client)) is False


def _disable_native(client, exc) -> None:
    if not _native_disabled(client):
        logger.info(f"overview_metrics count seam: native count not supported by "
                    f"{_server_key(client)} -- using len(find/get) fallback ({exc})")
    _native_server_ok[_server_key(client)] = False


def _native_count_method(client, candidates: Sequence[str], cache_key: str) -> Optional[str]:
    if cache_key not in _count_caps:
        name = next((c for c in candidates if callable(getattr(client, c, None))), None)
        _count_caps[cache_key] = name
        logger.info(f"overview_metrics count seam [{cache_key}]: "
                    + (f"native via {name}" if name else "fallback to len(find/get)"))
    return _count_caps[cache_key]


def _as_count(res) -> Optional[int]:
    if isinstance(res, int):
        return res
    if isinstance(res, dict) and res.get("count") is not None:
        return int(res["count"])
    return None


def _json_list(raw) -> list:
    """Normalise a pyegeria output_format='JSON' result to a list of dicts."""
    if isinstance(raw, list):
        return [r for r in raw if isinstance(r, dict)]
    if isinstance(raw, dict):
        for k in ("elements", "items", "relationships", "list"):
            if isinstance(raw.get(k), list):
                return [r for r in raw[k] if isinstance(r, dict)]
    return []


def _find(mgr, body: dict, page_size: int = DEFAULT_CAP) -> list:
    """Run a FindRequestBody, always returning a (possibly empty) list. Never raises."""
    try:
        # find_metadata_elements sends body exactly as given (no injected
        # defaults) -- graphQueryDepth/startFrom/pageSize all belong in the
        # body itself now, not separate kwargs (ISSUE-34, PYEGERIA_ISSUES.md:
        # startFrom/pageSize as URL query params -- the older convention --
        # stopped working once Egeria moved pagination for this endpoint
        # into the request body; find_metadata_elements no longer accepts
        # them as parameters at all, to avoid this drifting stale again).
        b = {**body, "graphQueryDepth": 0, "startFrom": 0, "pageSize": page_size}
        raw = mgr.find_metadata_elements(b)
        return [el for el in (raw if isinstance(raw, list) else []) if isinstance(el, dict)]
    except Exception as exc:  # noqa: BLE001 -- best-effort, degrade don't fail
        logger.debug(f"overview_metrics _find failed for {body.get('metadataElementTypeName')!r}: {exc}")
        return []


def _element_count(mgr, body: dict, as_of: Optional[str] = None) -> int:
    """Count elements matching a FindRequestBody -- native when available, else
    len(find_metadata_elements(...))."""
    b = dict(body)
    if as_of:
        b["asOfTime"] = as_of
    name = _native_count_method(mgr, _ELEMENT_COUNT_CANDIDATES, "elem:" + type(mgr).__name__)
    if name and not _native_disabled(mgr):
        try:
            c = _as_count(getattr(mgr, name)(b))
            if c is not None:
                return c
        except Exception as exc:  # noqa: BLE001 -- old server: mark unsupported, fall back
            _disable_native(mgr, exc)
    return len(_find(mgr, b))


def count_elements(
    mgr,
    type_name: Optional[str] = None,
    as_of: Optional[str] = None,
    classifications: Optional[Sequence[str]] = None,
) -> int:
    """
    Count ACTIVE elements, optionally of a given type and/or matching ANY of
    the given classifications. Uses native `count_metadata_elements` when the
    client + server support it, else `len(find_metadata_elements(...))`.

    Parameters
    ----------
    mgr : MetadataExpert (or compatible client)
    type_name : the open-metadata type name to count (None = any type)
    as_of : ISO-8601 asOfTime for a point-in-time count (None = now)
    classifications : classification names to match ANY of -- keep to a
        single call's worth (some connectors mishandle 2+ ANY conditions)

    Returns
    -------
    int -- 0 on any failure (never raises)
    """
    body: Dict[str, Any] = {"class": "FindRequestBody", "limitResultsByStatus": ["ACTIVE"]}
    if type_name:
        body["metadataElementTypeName"] = type_name
    if classifications:
        body["matchClassifications"] = {
            "class": "SearchClassifications", "matchCriteria": "ANY",
            "conditions": [{"name": n} for n in classifications],
        }
    return _element_count(mgr, body, as_of)


def count_elements_by_property(
    mgr,
    type_name: str,
    property_name: str,
    property_value: str,
    as_of: Optional[str] = None,
) -> int:
    """
    Count ACTIVE elements of a given type whose named string property equals
    a given value -- e.g. counting DigitalProduct elements by deploymentStatus
    (Overview dashboard's Data Products tile, OVERVIEW_NEXT_STEPS.md
    "Remaining app wiring"). Same native-count-with-fallback seam as
    count_elements, just with a searchProperties EQ condition instead of a
    bare type filter -- one cheap native COUNT call per distinct value, no
    element fetch, same cost class as the plain count.

    Parameters
    ----------
    mgr : MetadataExpert (or compatible client)
    type_name : the open-metadata type name to count
    property_name : the element property to match (e.g. "deploymentStatus")
    property_value : the exact string value to match
    as_of : ISO-8601 asOfTime for a point-in-time count (None = now)

    Returns
    -------
    int -- 0 on any failure (never raises)
    """
    body: Dict[str, Any] = {
        "class": "FindRequestBody",
        "metadataElementTypeName": type_name,
        "limitResultsByStatus": ["ACTIVE"],
        "searchProperties": {
            "class": "SearchProperties",
            "matchCriteria": "ALL",
            "conditions": [{
                "property": property_name,
                "operator": "EQ",
                "value": {"class": "PrimitiveTypePropertyValue", "typeName": "string", "primitiveValue": property_value},
            }],
        },
    }
    return _element_count(mgr, body, as_of)


def count_relationships(ce, relationship_type: str, as_of: Optional[str] = None, expert=None) -> Optional[int]:
    """
    Count relationships of a type, optionally as of a past time.

    Uses `len(ClassificationExplorer.get_relationships(...))` by default -- the
    path most portal apps (e.g. Audit) use, so counts stay consistent across
    the portal. A native `MetadataExpert.count_relationships_between_elements`
    fast-path is available when `expert` is passed, but is opt-in: the two
    OMVS layers can disagree for some relationship types (Egeria issue
    tracked as PY-18 in egeria-workspaces PYEGERIA_ISSUES.md -- e.g. an
    `Exception` count differed 276 natively vs 55 via get_relationships), so
    the default stays on the more widely-matched path.

    Parameters
    ----------
    ce : ClassificationExplorer (or compatible client)
    relationship_type : the relationship type name to count
    as_of : ISO-8601 asOfTime for a point-in-time count (None = now)
    expert : optional MetadataExpert to enable the native fast-path

    Returns
    -------
    Optional[int] -- None on total failure (never raises)
    """
    if expert is not None and not _native_disabled(expert):
        name = _native_count_method(expert, _REL_COUNT_CANDIDATES, "rel:" + type(expert).__name__)
        if name:
            body = {"class": "FindRelationshipRequestBody", "relationshipTypeName": relationship_type,
                    "limitResultsByStatus": ["ACTIVE"]}
            if as_of:
                body["asOfTime"] = as_of
            try:
                c = _as_count(getattr(expert, name)(body))
                if c is not None:
                    return c
            except Exception as exc:  # noqa: BLE001
                _disable_native(expert, exc)
    try:
        body = {"class": "ResultsRequestBody", "asOfTime": as_of} if as_of else None
        return len(_json_list(ce.get_relationships(
            relationship_type=relationship_type, output_format="JSON",
            start_from=0, page_size=DEFAULT_CAP, body=body)))
    except Exception as exc:  # noqa: BLE001
        logger.debug(f"overview_metrics count_relationships({relationship_type}) failed: {exc}")
        return None


def counts_by_type(mgr, type_map: Sequence[Tuple[str, str]], as_of: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Per-type counts for a set of (label, type_name) pairs -- e.g. the assets-
    by-type composition breakdown. Unknown/wrong types just yield 0 rather
    than failing the whole call.

    Returns a list of {"label": ..., "type": ..., "count": ...} dicts, in the
    order given.
    """
    return [{"label": label, "type": type_name, "count": count_elements(mgr, type_name, as_of)}
            for label, type_name in type_map]


def sum_type_counts(mgr, type_map: Sequence[Tuple[str, str]], as_of: Optional[str] = None) -> Dict[str, Any]:
    """
    Composite: sum counts_by_type() across a caller-given (label, type_name)
    list -- e.g. the Overview dashboard's "Cataloged Assets" total, which
    used to be raw Python (`asset_total = sum(r["count"] for r in by_type)`)
    in overview_handler.py rather than a reusable analytic function
    (BACKLOG.md NEXT-18, egeria-workspaces).

    Implemented via the generic fetch+analytic action executor
    (`format_set_executor.run_analytic_action`) instead of hand-composing
    the two calls inline, so this also doubles as the first real exercise of
    that two-step action shape (`analytic_registry.AnalyticActionSpec`) --
    see its docstring for why a composite metric is modeled as
    (fetch, analytic) rather than one more hand-written function that
    repeats `counts_by_type`'s own fetch inline (the way `ai_ready_assets`
    does today).

    A caller that already has a `counts_by_type()` result in hand (as
    overview_handler.py does, for its own breakdown/chart) should call
    `sum_counts()` directly on it instead -- this function re-fetches.
    """
    from pyegeria.view.format_set_executor import run_analytic_action
    from pyegeria.view.analytic_registry import AnalyticActionSpec
    spec = AnalyticActionSpec(
        fetch="pyegeria.view.overview_metrics.counts_by_type",
        analytic="pyegeria.view.overview_metrics.sum_counts",
    )
    return run_analytic_action(spec, mgr, fetch_kwargs={"type_map": type_map, "as_of": as_of})


def sum_counts(by_type: List[Dict[str, Any]], mgr=None) -> Dict[str, Any]:
    """The analytic step for `sum_type_counts` -- receives `counts_by_type`'s
    raw result plus the same client `counts_by_type` itself was given
    (unused here; kept purely for calling-convention consistency with an
    analytic step that DOES need to fetch more -- e.g. following a
    relationship to enrich, the pattern `ai_ready_assets` already uses
    inline). Also directly reusable on a `by_type` result a caller already
    has, without re-fetching (see `sum_type_counts`'s docstring)."""
    return {"total": sum(r["count"] for r in by_type), "byType": by_type}


def _classifications_of(el: dict) -> set:
    out = set()
    for c in el.get("classifications") or []:
        if isinstance(c, dict) and c.get("classificationName"):
            out.add(c["classificationName"])
    return out


def _zone_names(el: dict) -> list:
    for c in el.get("classifications") or []:
        if isinstance(c, dict) and c.get("classificationName") == "ZoneMembership":
            pvm = (c.get("classificationProperties") or {}).get("propertyValueMap") or {}
            zv = pvm.get("zoneMembership")
            if isinstance(zv, dict) and zv.get("class") == "ArrayTypePropertyValue":
                arr = (zv.get("arrayValues") or {}).get("propertyValueMap") or {}
                return [arr[k].get("primitiveValue") for k in sorted(arr, key=lambda k: int(k) if k.isdigit() else 0)
                        if isinstance(arr.get(k), dict)]
    return []


def governed_coverage(mgr, as_of: Optional[str] = None) -> Dict[str, Any]:
    """
    Governance-classification-based coverage tally: how many elements carry
    at least one of `GOVERNANCE_CLASSIFICATIONS`, broken down by which
    classification and by governance zone.

    Returns {"governedCount": int, "byClassification": {name: count},
    "topZones": [{"zone": name, "count": count}, ...8 max]}.
    """
    body = {
        "class": "FindRequestBody",
        "matchClassifications": {
            "class": "SearchClassifications", "matchCriteria": "ANY",
            "conditions": [{"name": n} for n in GOVERNANCE_CLASSIFICATIONS],
        },
        "limitResultsByStatus": ["ACTIVE"],
    }
    if as_of:
        body["asOfTime"] = as_of
    hits = _find(mgr, body)

    by_classification: Dict[str, int] = {}
    zone_counts: Dict[str, int] = {}
    for el in hits:
        for name in _classifications_of(el):
            by_classification[name] = by_classification.get(name, 0) + 1
        for z in _zone_names(el):
            if z:
                zone_counts[z] = zone_counts.get(z, 0) + 1
    top_zones = sorted(zone_counts.items(), key=lambda kv: -kv[1])[:8]

    return {
        "governedCount": len(hits),
        "governedCapped": len(hits) >= DEFAULT_CAP,
        "byClassification": by_classification,
        "topZones": [{"zone": z, "count": c} for z, c in top_zones],
    }


def _owner_type_name(el: dict) -> Optional[str]:
    for c in el.get("classifications") or []:
        if isinstance(c, dict) and c.get("classificationName") == "Ownership":
            pvm = (c.get("classificationProperties") or {}).get("propertyValueMap") or {}
            owner_type = pvm.get("ownerTypeName")
            if isinstance(owner_type, dict):
                return owner_type.get("primitiveValue")
    return None


def ownership_coverage(mgr, as_of: Optional[str] = None) -> Dict[str, Any]:
    """
    Ownership-classification-based coverage tally: how many elements carry an
    `Ownership` classification (a named owner responsible for management/
    governance decisions), broken down by the owner's type (Person, Team,
    SolutionActorRole, ...). Same shape as `governed_coverage` -- a distinct
    Data Mesh / data-contract-adjacent signal ("clean, owned, product-based
    data" is repeatedly named as the foundation for trustworthy AI
    consumption), not a duplicate of governance-classification coverage.

    Returns {"ownershipCount": int, "ownershipCapped": bool,
    "byOwnerType": {typeName: count}}.
    """
    body = {
        "class": "FindRequestBody",
        "matchClassifications": {
            "class": "SearchClassifications", "matchCriteria": "ANY",
            "conditions": [{"name": "Ownership"}],
        },
        "limitResultsByStatus": ["ACTIVE"],
    }
    if as_of:
        body["asOfTime"] = as_of
    hits = _find(mgr, body)

    by_owner_type: Dict[str, int] = {}
    for el in hits:
        owner_type = _owner_type_name(el) or "Unspecified"
        by_owner_type[owner_type] = by_owner_type.get(owner_type, 0) + 1

    return {
        "ownershipCount": len(hits),
        "ownershipCapped": len(hits) >= DEFAULT_CAP,
        "byOwnerType": by_owner_type,
    }


def business_value_signals(mgr, as_of: Optional[str] = None) -> Dict[str, Any]:
    """
    Real signals behind the Overview dashboard's four "Business Value" tiles
    (NEXT-9) -- replaces the four previously-synthetic narrative numbers
    (Risk & Compliance, Productivity, Trust & Adoption, Cost Avoidance) with
    honest, precisely-scoped proxies. Deliberately proxies, not direct
    measures -- see each field's use-site in overview_handler.py / this
    function's own module docs for the causal-claim caveat that goes with
    it (e.g. "more described assets" is a proxy for self-service findability,
    not a measure of actual query/access frequency).

    A single Asset-hierarchy fetch answers two of the four fields
    (confidentiality exposure and description coverage -- both are
    per-element checks on the same fetched set, same "check several signals
    from one fetch" shape `context_readiness_funnel` already uses).

    IMPORTANT scoping distinction from `governed_coverage`'s own
    `byClassification["Confidentiality"]`: that number is NOT Asset-scoped
    (any element type carrying the classification counts, per its own
    documented caveat), whereas `confidentialCount` here IS Asset-scoped by
    construction (checked only on elements this function's own Asset-
    hierarchy fetch returned). Confirmed live 2026-08-02 on a real dataset:
    5 total Confidentiality-classified elements exist, only 1 of which is
    Asset-typed (a CSVFile; the other 4 are typed `Referenceable`, not under
    `Asset`) -- the two numbers are both correct, just different
    populations, not a discrepancy to "fix."

    Duplicate detection is a separate classification count. Data Products
    (Trust & Adoption) is deliberately NOT duplicated here -- callers already
    have a live `dataProducts` count from `count_elements(mgr, "DigitalProduct", as_of)`
    elsewhere in the same request; no rating/adoption signal is wired (no
    `AttachedRating` relationships exist against `DigitalProduct` in a typical
    demo dataset, confirmed live -- so a rating average is honestly omitted
    rather than faked).

    Returns {"assetTotal": int, "assetCapped": bool, "confidentialCount": int,
    "describedCount": int, "duplicateCount": int}.
    """
    body = {"class": "FindRequestBody", "limitResultsByStatus": ["ACTIVE"],
            "metadataElementTypeName": "Asset"}
    if as_of:
        body["asOfTime"] = as_of
    assets = _find(mgr, body)

    confidential = 0
    described = 0
    for a in assets:
        if "Confidentiality" in _classifications_of(a):
            confidential += 1
        pvm = (a.get("elementProperties") or {}).get("propertyValueMap") or {}
        desc = (pvm.get("description") or {}).get("primitiveValue")
        if isinstance(desc, str) and desc.strip():
            described += 1

    duplicate = count_elements(mgr, None, as_of, classifications=["ConsolidatedDuplicate"])

    return {
        "assetTotal": len(assets),
        "assetCapped": len(assets) >= DEFAULT_CAP,
        "confidentialCount": confidential,
        "describedCount": described,
        "duplicateCount": duplicate,
    }


def _rel_end_date(rel: dict):
    """Best-effort expiry date for a relationship: domain property, then effectivity."""
    from datetime import datetime
    props = rel.get("relationshipProperties") or {}
    header = rel.get("relationshipHeader") or {}
    candidates = [props.get(k) for k in ("coverageEnd", "end", "endDate", "expiry", "expirationDate")]
    candidates.append((header.get("effectivityDates") or {}).get("effectiveToTime"))
    candidates.append(header.get("effectiveToTime"))
    for v in candidates:
        if not v:
            continue
        s = str(v).replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(s)
        except Exception:  # noqa: BLE001
            pass
    return None


def certifications_summary(ce, as_of: Optional[str] = None) -> Dict[str, Any]:
    """
    Active certifications, those expiring within 90 days (anchored to `as_of`
    if given, else wall-clock now), a soonest-5 list, license count, and open
    governance-exception count.

    Returns {"active": int|None, "expiring90": int|None, "soon": [...],
    "licenses": int|None, "exceptions": int|None}. Degrades to Nones on
    failure rather than raising (a demo/dev server may simply have none).
    """
    from datetime import datetime, timezone, timedelta

    out: Dict[str, Any] = {"active": None, "expiring90": None, "soon": [], "licenses": None, "exceptions": None}
    body = {"class": "ResultsRequestBody", "asOfTime": as_of} if as_of else None
    try:
        certs = _json_list(ce.get_relationships(relationship_type="Certification",
                                                output_format="JSON", start_from=0,
                                                page_size=DEFAULT_CAP, body=body))
        now = datetime.fromisoformat(as_of.replace("Z", "+00:00")) if as_of else datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        horizon = now + timedelta(days=90)
        soon = []
        expiring = 0
        for r in certs:
            end = _rel_end_date(r)
            if end is not None:
                if end.tzinfo is None:
                    end = end.replace(tzinfo=timezone.utc)
                if now <= end <= horizon:
                    expiring += 1
                    end2 = r.get("end2") or {}
                    name = ((end2.get("properties") or end2) or {}).get("displayName") or "certification"
                    soon.append({"name": name, "days": (end - now).days})
        soon.sort(key=lambda s: s["days"])
        out["active"] = len(certs)
        out["expiring90"] = expiring
        out["soon"] = soon[:5]
    except Exception as exc:  # noqa: BLE001
        logger.debug(f"overview_metrics certifications_summary: query failed: {exc}")

    out["licenses"] = count_relationships(ce, "License", as_of)
    out["exceptions"] = count_relationships(ce, "Exception", as_of)
    return out


def semantic_grounding(mgr, ce, as_of: Optional[str] = None) -> Dict[str, Any]:
    """
    Semantic-grounding tally: `SemanticAssignment` relationships (term <->
    asset), as a count and as a percentage of the broad `Asset` supertype
    count -- the "meaning layer" that grounds AI context.

    Returns {"groundingLinks": int|None, "groundingPct": int|None}.
    """
    cataloged = count_elements(mgr, "Asset", as_of)
    links = count_relationships(ce, "SemanticAssignment", as_of)
    pct = min(100, round(100 * links / cataloged)) if cataloged and links is not None else None
    return {"groundingLinks": links, "groundingPct": pct}


def context_readiness_funnel(mgr, ce, as_of: Optional[str] = None) -> Dict[str, Optional[int]]:
    """
    Context-readiness funnel stages: how much cataloged data becomes
    trustworthy AI context.

    `documented` -- count of `Asset` elements carrying a non-empty
    `description`, same field-value-check approach `term_definition_completeness`
    uses for GlossaryTerm (fetches element bodies via `_find`, capped at
    DEFAULT_CAP -- no native count exists for "has a description", same
    tradeoff `governed_coverage`'s by-classification breakdown already accepts).

    `lineage` -- count of `DataFlow` relationships (design/business lineage --
    literal data-movement edges between assets/processes; distinct from
    OpenLineage's *operational*, run-level lineage, which is a separate
    signal not computed here). Verified live: `DataFlow`'s end1/end2 connect
    real infrastructure types (e.g. SoftwareServer -> Topic), unlike the
    `LineageRelationship` supertype (which also sweeps in unrelated things
    like `ActionRequester`, a governance-action assignment, not data lineage
    -- confirmed by inspecting live relationship type names before picking
    `DataFlow`). Same "relationship count as a coverage proxy" convention
    `semantic_grounding` already uses for `groundingLinks` -- not a
    deduplicated distinct-asset count, a rough signal.

    `aiReady` remains None -- a true reading needs assets meeting ALL of
    documented+classified+lineage simultaneously (a real cross-criteria
    intersection, not another independent count), which none of the above
    three cheaply gives on their own. This is the same "composite/derived
    analytic metric" gap egeria-workspaces BACKLOG.md NEXT-18 already
    flagged (no analytic function here composes/derives across multiple
    underlying queries yet) -- fold `aiReady` into that work rather than
    faking an approximate number here.

    Returns {"cataloged": int, "documented": int|None, "classified": int,
    "lineage": int|None, "aiReady": None}.
    """
    cataloged = count_elements(mgr, "Asset", as_of)
    classified = count_elements(mgr, None, as_of, classifications=GOVERNANCE_CLASSIFICATIONS)

    documented = None
    try:
        body: Dict[str, Any] = {"class": "FindRequestBody", "limitResultsByStatus": ["ACTIVE"],
                                 "metadataElementTypeName": "Asset"}
        if as_of:
            body["asOfTime"] = as_of
        assets = _find(mgr, body)
        documented = 0
        for a in assets:
            pvm = (a.get("elementProperties") or {}).get("propertyValueMap") or {}
            desc = (pvm.get("description") or {}).get("primitiveValue")
            if isinstance(desc, str) and desc.strip():
                documented += 1
    except Exception as exc:  # noqa: BLE001
        logger.debug(f"context_readiness_funnel: documented query failed: {exc}")

    lineage = count_relationships(ce, "DataFlow", as_of)

    return {
        "cataloged": cataloged or None,
        "documented": documented,
        "classified": classified or None,
        "lineage": lineage,
        "aiReady": None,
    }


def ai_ready_assets(mgr, ce, as_of: Optional[str] = None) -> Dict[str, Any]:
    """
    The actual "AI-Ready" claim `context_readiness_funnel`'s own UI already
    makes ("48% -- governed + documented + lineage"): a true composite --
    Asset elements that are simultaneously governed (>=1 of
    GOVERNANCE_CLASSIFICATIONS), documented (non-empty description), AND
    lineage-traced (participates in >=1 DataFlow relationship) -- not three
    independent counts intersected after the fact from separate endpoints,
    which is what `context_readiness_funnel` alone can give you. First real
    implementation of the "composite/derived analytic metric" pattern
    egeria-workspaces BACKLOG.md NEXT-18 flagged as missing (no analytic
    function here composed across multiple underlying queries before this).

    Implementation note -- one fetch, not three: a single capped `_find` on
    `metadataElementTypeName: "Asset"` already returns each element's own
    `classifications` list (confirmed live -- the same shape
    `governed_coverage`'s `_classifications_of()` already reads) alongside
    `elementProperties` (for the description check), so "governed" and
    "documented" are checked per-element from that one fetch; only "lineage"
    needs a second query (the DataFlow relationships, to build the set of
    GUIDs that participate in at least one). Field-name gotcha, verified
    live: a `find_metadata_elements` result's own GUID is `elementGUID`, but
    a relationship's `end1`/`end2` (`ElementStub`) GUID is plain `guid` --
    genuinely two different key names for the same concept depending on
    which API path returned the data; using the wrong one silently produces
    an empty intersection instead of an error, so this was checked against
    live responses before writing the intersection logic, not assumed.

    Same DEFAULT_CAP tradeoff every field-value-check function in this
    module already accepts (`term_definition_completeness`,
    `context_readiness_funnel`'s own `documented` stage) -- a floor, not
    exact, on a catalog larger than DEFAULT_CAP.

    Returns {"aiReadyCount": int, "total": int, "capped": bool} -- "total" is
    the (possibly capped) Asset population actually checked, so a caller can
    compute a percentage without a separate cataloged-count call.
    """
    body: Dict[str, Any] = {"class": "FindRequestBody", "limitResultsByStatus": ["ACTIVE"],
                             "metadataElementTypeName": "Asset"}
    if as_of:
        body["asOfTime"] = as_of
    assets = _find(mgr, body)

    lineage_guids: set = set()
    try:
        rel_body = {"class": "ResultsRequestBody", "asOfTime": as_of} if as_of else None
        rels = _json_list(ce.get_relationships(
            relationship_type="DataFlow", output_format="JSON",
            start_from=0, page_size=DEFAULT_CAP, body=rel_body))
        for r in rels:
            for end_key in ("end1", "end2"):
                end = (r.get(end_key) or {}) if isinstance(r, dict) else {}
                g = end.get("guid")
                if g:
                    lineage_guids.add(g)
    except Exception as exc:  # noqa: BLE001
        logger.debug(f"ai_ready_assets: lineage relationship query failed: {exc}")

    ai_ready = 0
    for a in assets:
        guid = a.get("elementGUID")
        pvm = (a.get("elementProperties") or {}).get("propertyValueMap") or {}
        desc = (pvm.get("description") or {}).get("primitiveValue")
        documented = isinstance(desc, str) and bool(desc.strip())
        governed = bool(_classifications_of(a) & set(GOVERNANCE_CLASSIFICATIONS))
        lineage_traced = guid in lineage_guids
        if documented and governed and lineage_traced:
            ai_ready += 1

    return {"aiReadyCount": ai_ready, "total": len(assets), "capped": len(assets) >= DEFAULT_CAP}


# ── Modality tagging (§1.9) ──────────────────────────────────────────────────
# Derived automatically from an asset's existing Open Metadata type -- no new
# classification. See egeria-workspaces OVERVIEW_CONTEXT_INTELLIGENCE.md §1.9.

_TABULAR_TYPES = frozenset({
    "DataField", "TabularColumn", "TabularFileColumn", "RelationalColumn",
    "RelationalTable", "TabularFile", "RelationalDatabase", "TabularSchemaType",
})
_TEXT_MEDIA_TYPES = frozenset({
    "Document", "DataFile", "MediaFile", "AudioFile", "VideoFile", "ImageFile",
    "PDFFile", "DocumentStore",
})


def _element_type_names(el: dict) -> set:
    """typeName + superTypeNames from an element's `type` block, so a subtype
    not itself listed in _TABULAR_TYPES/_TEXT_MEDIA_TYPES still resolves via
    its supertype chain rather than falling through to "other"."""
    t = el.get("type") or (el.get("elementHeader") or {}).get("type") or {}
    names = set()
    if t.get("typeName"):
        names.add(t["typeName"])
    names.update(t.get("superTypeNames") or [])
    return names


def asset_modality(el: dict) -> str:
    """
    Classify an asset element as "tabular", "text_media", or "other" from its
    existing Open Metadata type -- the §1.9 resolution: no new classification,
    derive from structure already there. Checked against the full type
    hierarchy (typeName + superTypeNames), not just the leaf type.

    Returns "tabular" | "text_media" | "other" -- never raises. "other" is
    the honest fallback for asset types this pass doesn't classify (e.g.
    APIs, processes), not a guess.
    """
    names = _element_type_names(el)
    if names & _TABULAR_TYPES:
        return "tabular"
    if names & _TEXT_MEDIA_TYPES:
        return "text_media"
    return "other"


# ── DRL bands (§1.9) ──────────────────────────────────────────────────────
# Data Readiness Level: Raw -> Analytics-Ready -> RAG-Ready -> AI-Ready, as
# cumulative gate checklists (gates-not-weights, §1.7/§1.8), not a blended
# score. See egeria-workspaces OVERVIEW_CONTEXT_INTELLIGENCE.md §1.9.
#
# Only the gate this module can honestly compute today beyond what
# `ai_ready_assets` already covers is recency. Two gates the design doc's
# ladder calls for -- Survey Annotation presence (Tier 2, no verified
# relationship type yet) and the modality-aware Structural Readiness
# sub-check -- are still open decisions (design doc "Open decisions"
# section), so this function does NOT claim to certify the full
# Analytics-Ready/RAG-Ready rungs. Rather than approximate them from
# whatever gates ARE available and risk mislabeling the result, it narrows
# the already-shipped `ai_ready_assets` intersection by recency and reports
# that -- same "leave it out, don't fake it" convention
# `context_readiness_funnel`'s own `aiReady=None` already established.


def drl_readiness_gates(mgr, ce, as_of: Optional[str] = None, recency_days: int = 180) -> Dict[str, Any]:
    """
    A recency-narrowed view of `ai_ready_assets`, plus a modality breakdown
    of the underlying Asset population -- the two DRL-ladder pieces (§1.9)
    that are honestly computable today without Survey Annotation coverage or
    a Structural Readiness sub-check (both still open decisions).

    NOT a full DRL band distribution: `analyticsReadyCount`/`ragReadyCount`
    are deliberately absent, not approximated, until those two gates exist.

    Parameters
    ----------
    mgr : MetadataExpert (or compatible client)
    ce : ClassificationExplorer (or compatible client)
    as_of : ISO-8601 asOfTime for a point-in-time read (None = now)
    recency_days : provisional recency window for "recent" -- not yet a
        decided band threshold, see design doc "Open decisions"

    Returns {"total": int, "capped": bool, "aiReadyCount": int,
    "aiReadyRecentCount": int, "byModality": {"tabular", "text_media", "other"}}.
    """
    from datetime import datetime, timedelta, timezone

    body: Dict[str, Any] = {"class": "FindRequestBody", "limitResultsByStatus": ["ACTIVE"],
                             "metadataElementTypeName": "Asset"}
    if as_of:
        body["asOfTime"] = as_of
    assets = _find(mgr, body)

    lineage_guids: set = set()
    try:
        rel_body = {"class": "ResultsRequestBody", "asOfTime": as_of} if as_of else None
        rels = _json_list(ce.get_relationships(
            relationship_type="DataFlow", output_format="JSON",
            start_from=0, page_size=DEFAULT_CAP, body=rel_body))
        for r in rels:
            for end_key in ("end1", "end2"):
                g = ((r.get(end_key) or {}) if isinstance(r, dict) else {}).get("guid")
                if g:
                    lineage_guids.add(g)
    except Exception as exc:  # noqa: BLE001
        logger.debug(f"drl_readiness_gates: DataFlow relationship query failed: {exc}")

    now = datetime.fromisoformat(as_of.replace("Z", "+00:00")) if as_of else datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    horizon = timedelta(days=recency_days)

    ai_ready = 0
    ai_ready_recent = 0
    by_modality = {"tabular": 0, "text_media": 0, "other": 0}
    for a in assets:
        by_modality[asset_modality(a)] += 1

        guid = a.get("elementGUID")
        pvm = (a.get("elementProperties") or {}).get("propertyValueMap") or {}
        desc = (pvm.get("description") or {}).get("primitiveValue")
        documented = isinstance(desc, str) and bool(desc.strip())
        governed = bool(_classifications_of(a) & set(GOVERNANCE_CLASSIFICATIONS))
        lineage_traced = guid in lineage_guids
        if not (documented and governed and lineage_traced):
            continue
        ai_ready += 1

        updated = _update_time(a)
        if updated is not None and (now - updated) <= horizon:
            ai_ready_recent += 1

    return {
        "total": len(assets),
        "capped": len(assets) >= DEFAULT_CAP,
        "aiReadyCount": ai_ready,
        "aiReadyRecentCount": ai_ready_recent,
        "byModality": by_modality,
    }


def _update_time(el: dict):
    """Best-effort last-update timestamp from an element's version metadata."""
    from datetime import datetime
    header = el.get("elementHeader") or {}
    versions = header.get("versions") or el.get("versions") or {}
    v = versions.get("updateTime") or versions.get("createTime")
    if not v:
        return None
    try:
        return datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except Exception:  # noqa: BLE001
        return None


def people_counts(mgr, as_of: Optional[str] = None) -> Dict[str, int]:
    """
    Person / Team / Organization / ITProfile / Community counts via native
    element counts (sub-second where an older find-and-bucket approach would
    materialize every profile). NB: this counts every entity of the type in
    the repository; a curated find-and-bucket approach can return a smaller,
    filtered set, so totals may differ from an older implementation -- this
    raw count is the authoritative repository count.

    Returns {"persons": int, "teams": int, "organizations": int,
    "itProfiles": int, "communities": int}.
    """
    return {
        "persons": count_elements(mgr, "Person", as_of),
        "teams": count_elements(mgr, "Team", as_of),
        "organizations": count_elements(mgr, "Organization", as_of),
        "itProfiles": count_elements(mgr, "ITProfile", as_of),
        "communities": count_elements(mgr, "Community", as_of),
    }


_FEEDBACK_RELATIONSHIP_TYPES = (
    ("AttachedRating", "ratings"),
    ("AttachedComment", "comments"),
    ("AttachedLike", "likes"),
    ("AttachedTag", "tags"),
    ("AttachedNoteLog", "noteLogs"),
)


def feedback_summary(ce, as_of: Optional[str] = None) -> Dict[str, Any]:
    """
    Crowd-sourced feedback tally -- ratings/comments/likes/tags/note-logs
    (Collaboration OMAS relationship counts). Often sparse in demo data, but
    real.

    Returns {"byType": {ratings, comments, likes, tags, noteLogs}, "total": int}.
    """
    by_type = {key: (count_relationships(ce, rel, as_of) or 0) for rel, key in _FEEDBACK_RELATIONSHIP_TYPES}
    return {"byType": by_type, "total": sum(by_type.values())}


def usage_context_counts(mgr, as_of: Optional[str] = None) -> Dict[str, int]:
    """
    InformationSupplyChain and SolutionBlueprint counts -- what puts assets
    in a *usage context* ("this store feeds the Clinical Trial supply
    chain", "this component realises the Sales blueprint").

    Returns {"informationSupplyChains": int, "blueprints": int}.
    """
    return {
        "informationSupplyChains": count_elements(mgr, "InformationSupplyChain", as_of),
        "blueprints": count_elements(mgr, "SolutionBlueprint", as_of),
    }


def contextualised_coverage(mgr, ce, as_of: Optional[str] = None) -> Dict[str, Optional[int]]:
    """
    % of Assets that have been given business/solution-design context via a
    SolutionComponent -- OVERVIEW_NEXT_STEPS.md's "Usage % contextualised",
    stuck as a documented TODO since it looked like it needed a full
    per-asset participation traversal (no native "count of elements reachable
    from a relationship" API exists). It doesn't, once you go through the
    right relationship instead of trying to walk every asset: `ImplementedBy`
    (model 0737, Solution Implementation) links a SolutionComponent to its
    concrete implementation -- end1 is always SolutionComponent, end2 is
    whatever actually implements it. Confirmed live 2026-08-17: on this
    dataset end2 is a real mix (109 GovernanceActionType, but 31 genuine
    Asset-subtype elements -- IntegrationConnector/SoftwareServer/Topic/
    SoftwareServerPlatform) -- so filtering end2 to Asset-subtype elements
    and counting distinct GUIDs is a single bounded relationship fetch, not a
    traversal. `ImplementationResource` (the sibling relationship) was also
    checked live and found to connect only to GovernanceActionType in this
    dataset -- not useful for this metric, not included here.

    Honesty note (this is a proxy, not the literal metric): an asset
    connected to a SolutionComponent via ImplementedBy has been given
    *some* solution-design context, but confirming that specific
    SolutionComponent is itself wired into an InformationSupplyChain or
    SolutionBlueprint would need a second hop (SolutionComponent ->
    composition relationship -> ISC/blueprint) this function doesn't take --
    same "single relationship-count hop, not a full graph walk" tradeoff
    every other proxy metric in this module already makes (e.g. `lineage`
    counting DataFlow relationships rather than confirming each one sits on
    a path Egeria would call "lineage" in the strict sense).

    Capped at max_paging_size ImplementedBy relationships (matches every
    other relationship fetch in this module) -- undercounts if a deployment
    has more, same documented tradeoff as governed_coverage/
    certifications_summary's own caps.

    Returns {"contextualisedCount": int|None, "assetTotal": int|None,
    "contextualisedPct": float|None}. Any field is None on total failure for
    its own step (never raises).
    """
    contextualised_count = None
    try:
        rel_body = {"class": "ResultsRequestBody", "asOfTime": as_of} if as_of else None
        rels = _json_list(ce.get_relationships(
            relationship_type="ImplementedBy", output_format="JSON",
            start_from=0, page_size=max_paging_size, body=rel_body))
        asset_guids: set = set()
        for r in rels:
            for end_key in ("end1", "end2"):
                end = (r.get(end_key) or {}) if isinstance(r, dict) else {}
                end_type = end.get("type") or {}
                type_names = {end_type.get("typeName")} | set(end_type.get("superTypeNames") or [])
                if "Asset" in type_names and end.get("guid"):
                    asset_guids.add(end["guid"])
        contextualised_count = len(asset_guids)
    except Exception as exc:  # noqa: BLE001
        logger.debug(f"contextualised_coverage: ImplementedBy query failed: {exc}")

    asset_total = count_elements(mgr, "Asset", as_of)

    pct = None
    if contextualised_count is not None and asset_total:
        pct = round(100.0 * contextualised_count / asset_total, 1)

    return {
        "contextualisedCount": contextualised_count,
        "assetTotal": asset_total or None,
        "contextualisedPct": pct,
    }


def karma_leaderboard(mgr, as_of: Optional[str] = None, top_n: int = 10,
                       anchor_types: Sequence[str] = ("Person",)) -> List[Dict[str, Any]]:
    """
    Top-N people by karma -- OVERVIEW_NEXT_STEPS.md's "leaderboard" (per-person
    karma rollup), previously left None as "deferred", turned out not to need
    a per-person loop: karma is a scalar `karmaPoints` property directly on
    each `ContributionRecord` element (not something derived from counting
    related things), and every ContributionRecord is *anchored* to its owning
    actor (Person/ITProfile/ActorProfile) via the standard `Anchors`
    classification -- so `anchorGUID`/`anchorTypeName` are already attached
    to the element itself, no relationship traversal needed to know whose
    karma it is.

    One bounded `find_metadata_elements` call (capped at max_paging_size,
    same discipline as every other fetch in this module) returns every
    ContributionRecord with properties + classifications attached; this
    filters to `anchor_types` (Person only by default -- pass e.g.
    `("Person", "ITProfile")` to include automation/engine contributors too),
    sorts by karmaPoints descending, and returns the top N. Display name is
    derived by stripping the "Contribution record for " prefix off the
    ContributionRecord's own displayName (set by
    ContributionRecordHandler.addContributionRecordToElement()) rather than
    an extra per-person fetch of the anchor element -- zero additional round
    trips.

    Returns a list of {"name": str, "karmaPoints": int, "anchorGuid": str,
    "anchorType": str}, longest-karma first, length ≤ top_n. Empty list on
    total failure (never raises).
    """
    try:
        body: Dict[str, Any] = {"class": "FindRequestBody", "limitResultsByStatus": ["ACTIVE"],
                                 "metadataElementTypeName": "ContributionRecord"}
        if as_of:
            body["asOfTime"] = as_of
        records = _find(mgr, body)
    except Exception as exc:  # noqa: BLE001
        logger.debug(f"karma_leaderboard: find failed: {exc}")
        return []

    entries: List[Dict[str, Any]] = []
    for el in records:
        pvm = (el.get("elementProperties") or {}).get("propertyValueMap") or {}
        karma_raw = (pvm.get("karmaPoints") or {}).get("primitiveValue")
        try:
            karma = int(karma_raw)
        except (TypeError, ValueError):
            continue

        anchor_type = None
        anchor_guid = None
        for c in (el.get("classifications") or []):
            if c.get("classificationName") != "Anchors":
                continue
            apvm = (c.get("classificationProperties") or {}).get("propertyValueMap") or {}
            anchor_type = (apvm.get("anchorTypeName") or {}).get("primitiveValue")
            anchor_guid = (apvm.get("anchorGUID") or {}).get("primitiveValue")
            break
        if anchor_type not in anchor_types:
            continue

        display_name = (pvm.get("displayName") or {}).get("primitiveValue") or ""
        name = display_name[len("Contribution record for "):] if display_name.startswith(
            "Contribution record for ") else (display_name or "(unnamed)")

        entries.append({"name": name, "karmaPoints": karma, "anchorGuid": anchor_guid, "anchorType": anchor_type})

    entries.sort(key=lambda e: e["karmaPoints"], reverse=True)
    return entries[:top_n]


_FEEDBACK_RELATIONSHIP_TYPES_FOR_SERIES = _FEEDBACK_RELATIONSHIP_TYPES


def engagement_series(ce, as_of: Optional[str] = None, weeks: int = 12) -> List[Dict[str, Any]]:
    """
    Weekly feedback-event trend -- OVERVIEW_NEXT_STEPS.md's "engagementSeries",
    previously left None as "deferred". Reuses the exact same
    `get_relationships` calls `feedback_summary()` already makes for each of
    the 5 feedback relationship types (AttachedRating/Comment/Like/Tag/
    NoteLog) -- that function only keeps `len()`; this keeps the relationship
    objects themselves and buckets each one's `relationshipHeader.versions.
    createTime` into its ISO week. No new API surface, no per-element loop
    beyond the same bounded relationship fetches already happening elsewhere.

    Weeks with zero events for every type are included (zero-filled, not
    omitted) across the trailing `weeks` window ending at the current week (or
    `as_of`'s week, if given) -- a real zero is a real data point for a trend
    line, not a gap to hide. Honesty note: with sparse demo data this can be
    a near-flat line with one or two non-zero weeks -- that's the real
    signal, not a rendering bug.

    Returns a list of {"week": "2026-W33", "comments": int, "ratings": int,
    "likes": int, "tags": int, "noteLogs": int, "total": int}, oldest week
    first, length == `weeks`. Empty list on total failure (never raises).
    """
    from datetime import datetime, timedelta, timezone

    try:
        anchor = datetime.fromisoformat(as_of.replace("Z", "+00:00")) if as_of else datetime.now(timezone.utc)
    except Exception:  # noqa: BLE001
        anchor = datetime.now(timezone.utc)

    def _week_key(dt: datetime) -> str:
        iso = dt.isocalendar()
        return f"{iso[0]}-W{iso[1]:02d}"

    week_keys: List[str] = []
    for i in range(weeks - 1, -1, -1):
        week_keys.append(_week_key(anchor - timedelta(weeks=i)))

    buckets: Dict[str, Dict[str, int]] = {wk: {"comments": 0, "ratings": 0, "likes": 0, "tags": 0, "noteLogs": 0}
                                           for wk in week_keys}

    for rel_type, field in _FEEDBACK_RELATIONSHIP_TYPES_FOR_SERIES:
        try:
            rel_body = {"class": "ResultsRequestBody", "asOfTime": as_of} if as_of else None
            rels = _json_list(ce.get_relationships(
                relationship_type=rel_type, output_format="JSON",
                start_from=0, page_size=max_paging_size, body=rel_body))
        except Exception as exc:  # noqa: BLE001
            logger.debug(f"engagement_series: {rel_type} query failed: {exc}")
            continue
        for r in rels:
            create_time = (((r.get("relationshipHeader") or {}).get("versions") or {}).get("createTime"))
            if not create_time:
                continue
            try:
                dt = datetime.fromisoformat(str(create_time).replace("Z", "+00:00"))
            except Exception:  # noqa: BLE001
                continue
            wk = _week_key(dt)
            if wk in buckets:
                buckets[wk][field] += 1

    series = []
    for wk in week_keys:
        b = buckets[wk]
        series.append({"week": wk, **b, "total": sum(b.values())})
    return series


def growth_series(
    mgr,
    window: str = "6mo",
    points: Optional[int] = None,
    type_map: Optional[Sequence[Tuple[str, Optional[str], Optional[Sequence[str]]]]] = None,
) -> List[Dict[str, Any]]:
    """
    A real growth series -- one snapshot per point, using Egeria's native
    `asOfTime` support (no separate time-series store needed).

    Parameters
    ----------
    mgr : MetadataExpert (or compatible client)
    window : one of WINDOWS's keys ("8h".."1y"); sets span + default point count
    points : override the number of snapshots (2-24)
    type_map : what to snapshot at each point, as (series_key, type_name,
        classifications) triples. Defaults to the Overview dashboard's own
        four series: assets/terms/governed/products.

    Returns a list of dicts, oldest first, each
    {"label": ..., "date": ..., <series_key>: count, ...}.
    """
    from datetime import datetime, timezone

    if type_map is None:
        type_map = [
            ("assets", "Asset", None),
            ("terms", "GlossaryTerm", None),
            ("governed", None, GOVERNANCE_CLASSIFICATIONS),
            ("products", "DigitalProduct", None),
        ]

    span_s, default_pts = WINDOWS.get(window, WINDOWS["6mo"])
    n = points or default_pts

    now = datetime.now(timezone.utc)
    step = span_s / (n - 1)
    date_fmt = "%d %b %Y %H:%M" if span_s <= 2 * 86400 else "%d %b %Y"

    series = []
    for i in range(n - 1, -1, -1):
        if i == 0:
            d, as_of = now, None
        else:
            d = datetime.fromtimestamp(now.timestamp() - i * step, tz=timezone.utc)
            as_of = d.isoformat()
        point = {"label": growth_label(d, span_s), "date": d.strftime(date_fmt)}
        try:
            for key, type_name, classifications in type_map:
                point[key] = count_elements(mgr, type_name, as_of, classifications=classifications)
        except Exception as exc:  # noqa: BLE001
            logger.debug(f"overview_metrics growth_series: snapshot {i} failed: {exc}")
            for key, _, _ in type_map:
                point.setdefault(key, None)
        series.append(point)
    return series


# Parameter names this module's own functions use for their leading client
# argument(s) -- a small local copy of format_set_executor._bind_client_args'
# binding logic (mgr/ce only; nothing here uses "expert"/"client") rather than
# importing that module, to keep this module's stated design boundary intact
# (independently callable/testable, no report-spec-registry dependency).
_CLIENT_PARAM_NAMES = ("mgr", "ce")


def metric_trend(
    mgr,
    ce,
    metric_path: str,
    window: str = "6mo",
    points: Optional[int] = None,
    metric_params: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Turn any single-snapshot function in this module into a time series, by
    re-calling it once per `asOfTime` snapshot -- the same windowing
    `growth_series` uses (BACKLOG NEXT-17), generalized to any function here
    instead of one hardcoded type_map. This is what gives every existing
    (and future) fixed-metric function trend support for free, without
    adding `window`/`points` params to each one individually.

    `metric_path` is a dotted import path exactly like `analytic_function`/
    `extra_find` declarations use (e.g. "pyegeria.view.overview_metrics.
    governed_coverage") -- resolved via `importlib`, not the analytic
    registry, to keep this module free of the report-spec-registry layer
    (see module docstring's design boundary; the registry itself already
    carries these same dotted paths in `AnalyticFunctionSpec.function`).

    Pass both `mgr` and `ce` regardless of what the target function actually
    needs -- only the client parameter names it declares (by leading
    positional parameter named "mgr"/"ce") are bound; the other is unused.

    `metric_params` are extra keyword arguments forwarded to the target
    function at every snapshot (e.g. `classifications` for `count_elements`);
    `as_of` is supplied by this function and must not be included there.

    Returns a list of dicts, oldest first: {"label", "date", **snapshot} --
    the target function's result is merged directly into the point if it's a
    dict (matching growth_series's flat-per-point shape), else stored under
    "value". A snapshot that raises logs at debug and stores None instead of
    aborting the whole series.
    """
    import importlib
    from datetime import datetime, timezone

    module_path, func_name = metric_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    func = getattr(module, func_name, None)
    if func is None or not callable(func):
        raise AttributeError(f"'{func_name}' not found in module '{module_path}'")

    clients = {"mgr": mgr, "ce": ce}
    bound_args = []
    for pname, param in inspect.signature(func).parameters.items():
        if pname in _CLIENT_PARAM_NAMES and param.kind in (
            inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD,
        ):
            bound_args.append(clients[pname])
        else:
            break

    span_s, default_pts = WINDOWS.get(window, WINDOWS["6mo"])
    n = points or default_pts
    now = datetime.now(timezone.utc)
    step = span_s / (n - 1)
    date_fmt = "%d %b %Y %H:%M" if span_s <= 2 * 86400 else "%d %b %Y"

    series = []
    for i in range(n - 1, -1, -1):
        if i == 0:
            d, as_of = now, None
        else:
            d = datetime.fromtimestamp(now.timestamp() - i * step, tz=timezone.utc)
            as_of = d.isoformat()
        point = {"label": growth_label(d, span_s), "date": d.strftime(date_fmt)}
        try:
            result = func(*bound_args, as_of=as_of, **(metric_params or {}))
            if isinstance(result, dict):
                point.update(result)
            else:
                point["value"] = result
        except Exception as exc:  # noqa: BLE001
            logger.debug(f"overview_metrics metric_trend: snapshot {i} of {metric_path} failed: {exc}")
            point["value"] = None
        series.append(point)
    return series


def term_definition_completeness(mgr, as_of: Optional[str] = None) -> Dict[str, Any]:
    """
    Share of GlossaryTerms carrying a non-empty `description` -- a
    definitions-coverage metric (BACKLOG NEXT-17), distinct from
    `semantic_grounding` (which measures term<->asset linkage, not whether
    the term itself is actually defined).

    Unlike `count_elements`'s classification-only filter, "has a
    description" is a field-value check, so this fetches term bodies (via
    `_find`, same `FindRequestBody`/`metadataElementTypeName` shape
    `count_elements` uses) rather than using a native count -- no fast
    native-count path exists for this, same tradeoff `governed_coverage`
    accepts for its by-classification breakdown. `description` is read the
    same way `_zone_names` reads `zoneMembership`: verified live against a
    running server that `find_metadata_elements` returns raw
    `elementProperties.propertyValueMap.description.primitiveValue`, not a
    flat `properties.description` (that flatter shape belongs to the
    output_format='JSON' relationship/report path other functions here use,
    e.g. `certifications_summary`'s `end2`, not this raw element-query path).

    Returns {"total": int, "defined": int, "undefinedPct": int|None}
    (`undefinedPct` mirrors `semantic_grounding.groundingPct`'s naming: the
    gap, not the coverage, since a near-100%-defined glossary is the
    uninteresting case and the gap is what's actionable).
    """
    body: Dict[str, Any] = {"class": "FindRequestBody", "limitResultsByStatus": ["ACTIVE"],
                             "metadataElementTypeName": "GlossaryTerm"}
    if as_of:
        body["asOfTime"] = as_of
    terms = _find(mgr, body)
    total = len(terms)
    defined = 0
    for t in terms:
        pvm = (t.get("elementProperties") or {}).get("propertyValueMap") or {}
        desc = (pvm.get("description") or {}).get("primitiveValue")
        if isinstance(desc, str) and desc.strip():
            defined += 1
    undefined_pct = round(100 * (total - defined) / total) if total else None
    return {"total": total, "defined": defined, "undefinedPct": undefined_pct}


def active_contributors(ce, as_of: Optional[str] = None) -> Dict[str, Any]:
    """
    Distinct usernames behind at least one feedback relationship (ratings/
    comments/likes/tags/noteLogs -- the same Collaboration OMAS types
    `feedback_summary` counts) -- a real engagement signal
    `feedback_summary`'s raw relationship counts don't give you: ten
    comments from one person and ten comments from ten people both show up
    as "10" there, but very differently here (BACKLOG NEXT-17).

    Neither relationship end is a Person -- `AttachedComment`/`AttachedRating`/
    etc. link a Referenceable to the Comment/Rating/... element itself, and
    `CommentProperties` (etc.) carry no author field. The actor is instead
    the relationship's own audit metadata: `relationshipHeader.versions.
    createdBy` (verified live against a running server -- who *attached* the
    feedback, distinct from `end1`/`end2`, which are the commented-on
    element and the comment/rating/... element). `count_relationships`'
    native count can't give this since it only returns a number, not the
    relationship bodies.

    Returns {"contributors": int, "byType": {ratings, comments, likes, tags,
    noteLogs}} where byType is the distinct-username count per relationship
    type (one person active in two types counts once in "contributors" but
    once per type in byType).
    """
    body = {"class": "ResultsRequestBody", "asOfTime": as_of} if as_of else None

    def _actor_usernames(rel_type: str) -> set:
        rels = _json_list(ce.get_relationships(
            relationship_type=rel_type, output_format="JSON",
            start_from=0, page_size=DEFAULT_CAP, body=body))
        return {
            u for rel in rels
            if (u := (rel.get("relationshipHeader") or {}).get("versions", {}).get("createdBy"))
        }

    by_type: Dict[str, int] = {}
    all_users: set = set()
    for rel_type, key in _FEEDBACK_RELATIONSHIP_TYPES:
        try:
            users = _actor_usernames(rel_type)
        except Exception as exc:  # noqa: BLE001
            logger.debug(f"overview_metrics active_contributors: {rel_type} failed: {exc}")
            users = set()
        by_type[key] = len(users)
        all_users |= users
    return {"contributors": len(all_users), "byType": by_type}
