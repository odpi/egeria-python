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

__all__ = [
    "DEFAULT_CAP",
    "GOVERNANCE_CLASSIFICATIONS",
    "count_elements",
    "count_relationships",
    "counts_by_type",
    "governed_coverage",
    "ownership_coverage",
    "certifications_summary",
    "semantic_grounding",
    "context_readiness_funnel",
    "people_counts",
    "feedback_summary",
    "usage_context_counts",
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
DEFAULT_CAP = 500

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
        raw = mgr.find_metadata_elements(body, start_from=0, page_size=page_size, graph_query_depth=0)
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
            start_from=0, page_size=5000, body=body)))
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


def context_readiness_funnel(mgr, as_of: Optional[str] = None) -> Dict[str, Optional[int]]:
    """
    Context-readiness funnel stages: how much cataloged data becomes
    trustworthy AI context. `documented`/`lineage`/`aiReady` remain None --
    each needs a traversal query not yet available as a simple count (see
    egeria-workspaces OVERVIEW_NEXT_STEPS.md R-2 for the design work needed
    before these can be honestly computed).

    Returns {"cataloged": int, "documented": None, "classified": int,
    "lineage": None, "aiReady": None}.
    """
    cataloged = count_elements(mgr, "Asset", as_of)
    classified = count_elements(mgr, None, as_of, classifications=GOVERNANCE_CLASSIFICATIONS)
    return {
        "cataloged": cataloged or None,
        "documented": None,
        "classified": classified or None,
        "lineage": None,
        "aiReady": None,
    }


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
