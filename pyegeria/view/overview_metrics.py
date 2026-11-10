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

import contextlib
import contextvars
import functools
import inspect
import time
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, TypedDict

from loguru import logger

from pyegeria.core._exceptions import (
    PyegeriaConnectionException,
    PyegeriaNotFoundException,
    PyegeriaTimeoutException,
)
from pyegeria.core._globals import max_paging_size

__all__ = [
    "DEFAULT_CAP",
    "recording_unmeasured",
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
    "solution_component_realisation",
    "karma_leaderboard",
    "engagement_series",
    "orphan_glossary_terms",
    "stale_assets",
    "growth_series",
    "metric_trend",
    "term_definition_completeness",
    "active_contributors",
    "asset_subtype_tree",
    "asset_composition",
    "AssetComposition",
    "AssetCompositionRow",
    "CompositionCell",
    "COMPOSITION_DEFAULT_CONCURRENCY",
    "COMPOSITION_MAX_CONCURRENCY",
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
_native_server_ok: Dict[str, float] = {}  # server key -> monotonic time native was found unsupported


def _server_key(client) -> str:
    return f"{getattr(client, 'platform_url', '')}|{getattr(client, 'view_server', '')}"


# How long a "this server has no native counts" verdict is trusted before the
# next count tries native again (a server upgraded to support it is picked up
# without a process restart).
NATIVE_DISABLE_TTL_S = 300.0

_UNSUPPORTED_MARKERS = ("not implemented", "not supported", "unsupported", "no such method",
                        "no static resource", "not found")


def _native_unsupported(exc: Exception) -> bool:
    """True only when `exc` says the server lacks the native count endpoint
    (404/405/501 or an equivalent message). A timeout, a connection error or
    any other transient failure is NOT evidence of that: it fails only the one
    count (which then uses the len(find) fallback) and leaves native enabled."""
    if isinstance(exc, (PyegeriaTimeoutException, PyegeriaConnectionException)):
        return False
    if isinstance(exc, PyegeriaNotFoundException):
        return True
    code = getattr(exc, "http_status_code", None) or getattr(exc, "related_http_code", None)
    if code in (404, 405, 501):
        return True
    ai = getattr(exc, "additional_info", None)
    if isinstance(ai, dict) and ai.get("relatedHTTPCode") in (404, 405, 501):
        return True
    if isinstance(exc, (AttributeError, NotImplementedError)):
        return True
    msg = str(exc).lower()
    return any(m in msg for m in _UNSUPPORTED_MARKERS)


def _native_disabled(client) -> bool:
    key = _server_key(client)
    since = _native_server_ok.get(key)
    if since is None:
        return False
    if time.monotonic() - since > NATIVE_DISABLE_TTL_S:
        _native_server_ok.pop(key, None)  # expired: try native again
        return False
    return True


def _disable_native(client, exc) -> None:
    """Record that native counting failed. Only a 'server lacks it' error
    disables native for the server (until NATIVE_DISABLE_TTL_S); anything else
    is transient and only that one count falls back."""
    if not _native_unsupported(exc):
        logger.info(f"overview_metrics count seam: native count failed once for "
                    f"{_server_key(client)} ({exc}) -- this count falls back; native stays enabled")
        return
    if not _native_disabled(client):
        logger.info(f"overview_metrics count seam: native count not supported by "
                    f"{_server_key(client)} -- using len(find/get) fallback for "
                    f"{NATIVE_DISABLE_TTL_S:.0f}s ({exc})")
    _native_server_ok[_server_key(client)] = time.monotonic()


def _native_count_method(client, candidates: Sequence[str], cache_key: str) -> Optional[str]:
    if cache_key not in _count_caps:
        name = next((c for c in candidates if callable(getattr(client, c, None))), None)
        _count_caps[cache_key] = name
        logger.info(f"overview_metrics count seam [{cache_key}]: "
                    + (f"native via {name}" if name else "fallback to len(find/get)"))
    name = _count_caps[cache_key]
    # The cache is per class name; a client of another class with the same name may lack the method.
    return name if name and callable(getattr(client, name, None)) else None


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
    return _find_or_none(mgr, body, page_size) or []


def _find_or_none(mgr, body: dict, page_size: int = DEFAULT_CAP, start_from: int = 0) -> Optional[list]:
    """Run a FindRequestBody: a list of elements, [] when nothing matched (a list
    or pyegeria's "No elements found" string), or None when the query failed or
    answered with something else. Never raises."""
    try:
        # find_metadata_elements sends body exactly as given (no injected
        # defaults) -- graphQueryDepth/startFrom/pageSize all belong in the
        # body itself now, not separate kwargs (ISSUE-34, PYEGERIA_ISSUES.md:
        # startFrom/pageSize as URL query params -- the older convention --
        # stopped working once Egeria moved pagination for this endpoint
        # into the request body; find_metadata_elements no longer accepts
        # them as parameters at all, to avoid this drifting stale again).
        b = {**body, "graphQueryDepth": 0, "startFrom": start_from, "pageSize": page_size}
        raw = mgr.find_metadata_elements(b)
    except Exception as exc:  # noqa: BLE001 -- best-effort, degrade don't fail
        logger.debug(f"overview_metrics _find failed for {body.get('metadataElementTypeName')!r}: {exc}")
        return None
    if isinstance(raw, list):
        return [el for el in raw if isinstance(el, dict)]
    if isinstance(raw, str):
        return []  # pyegeria's miss sentinel
    logger.debug(f"overview_metrics _find: unexpected result for {body.get('metadataElementTypeName')!r}: "
                 f"{type(raw).__name__}")
    return None


# ── exhaustive scans ───────────────────────────────────────────────────────
# A figure computed from a scan (distinct relationship ends, per-element checks) is only a figure when
# the scan read everything. Egeria's paging contract: only an EMPTY page means done -- a short page is not
# the last page, because a server may filter hits out of a page after fetching it. So these helpers page
# until an empty page, advancing startFrom by the full page size every time, and a scan that would need
# more than MAX_SCAN_PAGES pages stops and is not measured (None plus a note), never reported from the
# part it had read. Found live 2026-11-08: one 500-relationship SemanticAssignment page held 8 distinct
# terms, all 747 held 77, so the orphan-term count read 1,053 instead of 984.
MAX_SCAN_PAGES = 40


class _ScanIncomplete(Exception):
    """Internal: a scan helper returned None (its note is already recorded)."""


def _scan_stopped_reason(kind: str, n: int) -> str:
    return (f"the {kind} scan stopped after {MAX_SCAN_PAGES} pages of {DEFAULT_CAP} ({n} read) before "
            f"Egeria returned an empty page, so it is incomplete")


def _repeated_page_reason(kind: str, n: int) -> str:
    return (f"the {kind} scan got a page that repeated only what it had already read, so the server "
            f"is not paging and the scan is incomplete ({n} read)")


def _all_relationships(ce, relationship_type: str, as_of: Optional[str] = None) -> Optional[list]:
    """Every relationship of `relationship_type` (as of `as_of`), paged until Egeria returns an empty page.

    Distinct by relationship GUID: a page may repeat relationships an earlier page returned. Returns None,
    with a note for `recording_unmeasured()`, when the scan is incomplete -- it reached MAX_SCAN_PAGES, or a
    page added nothing new (the server ignored startFrom). Raises when a page query fails, so each caller
    keeps its own failure path.

    The body always carries startFrom/pageSize: ClassificationExplorer.get_relationships ignores its
    start_from/page_size arguments whenever a body is given."""
    out: list = []
    seen: set = set()
    prev: Optional[list] = None
    what = f"{relationship_type} relationships"
    for i in range(MAX_SCAN_PAGES):
        start = i * DEFAULT_CAP
        body: Dict[str, Any] = {"class": "ResultsRequestBody", "startFrom": start, "pageSize": DEFAULT_CAP}
        if as_of:
            body["asOfTime"] = as_of
        page = _json_list(ce.get_relationships(relationship_type=relationship_type, output_format="JSON",
                                               start_from=start, page_size=DEFAULT_CAP, body=body))
        if not page:
            return out
        if page == prev:  # the same page again: startFrom was ignored (a GUID check cannot see it without GUIDs)
            _not_measured(what, _repeated_page_reason("relationship", len(out)), at_least=len(out))
            return None
        prev = page
        added = 0
        for r in page:
            g = (r.get("relationshipHeader") or {}).get("guid") or r.get("guid")
            if g:
                if g in seen:
                    continue
                seen.add(g)
            out.append(r)
            added += 1
        if added == 0:
            _not_measured(what, _repeated_page_reason("relationship", len(out)), at_least=len(out))
            return None
    _not_measured(what, _scan_stopped_reason("relationship", len(out)), at_least=len(out))
    return None


def _element_guid(el: dict) -> Optional[str]:
    return el.get("elementGUID") or (el.get("elementHeader") or {}).get("guid") or el.get("guid")


def _all_elements(mgr, body: dict) -> Optional[list]:
    """Every element a FindRequestBody matches, paged until Egeria returns an empty page.

    Distinct by element GUID. Returns None when a page query fails (no note: the caller's own failure
    path), and None with a note when the scan is incomplete (MAX_SCAN_PAGES reached, or a page that added
    nothing new). Never raises."""
    out: list = []
    seen: set = set()
    prev: Optional[list] = None
    for i in range(MAX_SCAN_PAGES):
        page = _find_or_none(mgr, body, DEFAULT_CAP, start_from=i * DEFAULT_CAP)
        if page is None:
            return None
        if not page:
            return out
        if page == prev:  # the same page again: startFrom was ignored
            _not_measured(_count_label(body), _repeated_page_reason("find", len(out)), at_least=len(out))
            return None
        prev = page
        added = 0
        for el in page:
            g = _element_guid(el)
            if g:
                if g in seen:
                    continue
                seen.add(g)
            out.append(el)
            added += 1
        if added == 0:
            _not_measured(_count_label(body), _repeated_page_reason("find", len(out)), at_least=len(out))
            return None
    _not_measured(_count_label(body), _scan_stopped_reason("find", len(out)), at_least=len(out))
    return None


def _one_page_or_none(mgr, body: dict, what: str) -> Optional[list]:
    """One find page, for a routine whose population is too large to page through (Asset): the page,
    [] when nothing matched, or None when the query failed or the page was full. A full page is a sample,
    not the population, so a figure computed from it is not measured (a note says so)."""
    page = _find_or_none(mgr, body)
    if page is not None and len(page) >= DEFAULT_CAP:
        _not_measured(what, f"the find stopped at its {DEFAULT_CAP}-element page cap, so this figure would "
                            f"describe only the first {len(page)} elements, not all of them", at_least=len(page))
        return None
    return page


# ── counting by last-update time ───────────────────────────────────────────
# Egeria cannot count by an updateTime condition: a search condition only reaches an element's own
# properties, and the header's updateTime (set at create, so never empty) is not one of them -- a count
# with `updateTime LT <cutoff>` answers 0 for every Asset (checked live 2026-11-09, and in the postgres
# connector's QueryBuilder, where update_time is only a sort column). It can SORT by it (sequencingOrder
# LAST_UPDATE_OLDEST), and startFrom is an offset into the repository's own sorted rows: a row the
# viewer may not see still takes its offset and reads as an empty one-row page. So the number of rows
# last updated before a cutoff is the offset of the first row updated at or after it, and a bisection
# over offsets finds it in about log2(total / 25) one-row reads plus one read of the last window (12 for
# 37,000 Assets), never paging the population.
MAX_BISECT_READS = 64
BISECT_WINDOW = 25  # the last window is read as one page of at most this many rows


def _rows_updated_before(mgr, body: dict, cutoff, total: int, what: str) -> Optional[int]:
    """How many of the `total` rows `body` matches were last updated before `cutoff`, by bisection over
    their offsets in LAST_UPDATE_OLDEST order. One-row reads, then one read of the last window of at most
    BISECT_WINDOW rows (it settles the count when every row in it is visible), at most MAX_BISECT_READS.

    A row the viewer cannot see reads as an empty page, and it still counts: a hidden row between two rows
    updated before the cutoff was updated before it too (the order is by update time), so the count is in
    the repository population, like `total`. Only hidden rows between the last row seen before the cutoff
    and the first row seen after it cannot be placed; then the result is None with a note giving the
    range. None with a note, too, when a read fails or the reads run out. Never raises."""
    b = {**body, "sequencingOrder": "LAST_UPDATE_OLDEST"}
    lo, hi = 0, total  # rows [0, lo) were updated before the cutoff; rows [hi, total) were not
    unknown: set = set()  # offsets that read as empty (hidden) or carried no update time
    reads = 0
    window_read = False
    while lo < hi:
        if not window_read and hi - lo <= BISECT_WINDOW and reads < MAX_BISECT_READS:
            # One read of the whole remaining window settles it when every row in it is visible: then the
            # page's positions are the offsets. With a hidden row in it, carry on one row at a time.
            window_read = True
            reads += 1
            page = _find_or_none(mgr, b, hi - lo, start_from=lo)
            if page is None:
                _not_measured(what, "a read of the rows in update-time order failed")
                return None
            times = [_update_time(el) for el in page]
            if len(page) == hi - lo and all(t is not None for t in times):
                return lo + sum(1 for t in times if t < cutoff)
            continue
        mid = (lo + hi) // 2
        found = None
        for k in list(range(mid, hi)) + list(range(mid - 1, lo - 1, -1)):
            if k in unknown:
                continue
            if reads >= MAX_BISECT_READS:
                _not_measured(what, f"the update-time bisection used all {MAX_BISECT_READS} of its one-row reads "
                                    f"(rows you cannot see lie between offsets {lo} and {hi}), so there are "
                                    f"between {lo} and {hi}", at_least=lo)
                return None
            reads += 1
            page = _find_or_none(mgr, b, 1, start_from=k)
            if page is None:
                _not_measured(what, "a read of the rows in update-time order failed")
                return None
            when = _update_time(page[0]) if page else None
            if when is None:
                unknown.add(k)
                continue
            found = (k, when)
            break
        if found is None:
            _not_measured(what, f"the {hi - lo} rows between the last one updated before the cutoff and the "
                                f"first one updated after it are not visible to you, so there are between "
                                f"{lo} and {hi}", at_least=lo)
            return None
        k, when = found
        if when < cutoff:
            lo = k + 1
        else:
            hi = k
    return lo


SCOPE_VIEWER = "viewer"
SCOPE_REPOSITORY = "repository"


def _population_keyword(fn):
    """Accept `population=` ("viewer" | "repository"), the owner's word (RS-W1-1 §5, 2026-11-06), as the
    count helpers' keyword. `scope=` still works as a deprecated alias: `scope` already means result level
    (resource, container, member, field) in the declaration model, so the population word must not reuse it.
    Passing both with different values is a ValueError."""
    sig = inspect.signature(fn)
    params = list(sig.parameters.values()) + [
        inspect.Parameter("population", inspect.Parameter.KEYWORD_ONLY, default=None, annotation=Optional[str])]

    @functools.wraps(fn)
    def wrapper(*args, population: Optional[str] = None, **kwargs):
        scope = kwargs.get("scope")
        if scope is not None:
            if population is not None and population != scope:
                raise ValueError(f"{fn.__name__}: population={population!r} and scope={scope!r} disagree; "
                                 f"pass population= only")
            if population is None:
                warnings.warn(f"{fn.__name__}(scope=...) is deprecated; use population=",
                              DeprecationWarning, stacklevel=2)
        if population is not None:
            kwargs["scope"] = population
        return fn(*args, **kwargs)

    wrapper.__signature__ = sig.replace(parameters=params)
    return wrapper


def _push_down(scope: Optional[str]) -> Optional[bool]:
    """Map a count scope to the native `push_down` argument: "viewer" -> False
    (server counts only what the caller may see), "repository" -> True (a raw
    repository COUNT: fast, but it also counts elements the caller cannot see),
    None -> None (omit it; the server default applies). Raises ValueError for
    any other value -- a programming error, not a runtime condition."""
    if scope is None:
        return None
    if scope == SCOPE_VIEWER:
        return False
    if scope == SCOPE_REPOSITORY:
        return True
    raise ValueError(f"scope must be None, {SCOPE_VIEWER!r} or {SCOPE_REPOSITORY!r}; got {scope!r}")


def _pop(scope: Optional[str]) -> Dict[str, Optional[str]]:
    """Keyword arguments that forward a composite's population to a count helper. `population=None`
    means "not given" to the keyword wrapper (the helper's repository default then applies), so the
    server default, scope=None, is forwarded as `scope=None` instead -- explicitly, not lost."""
    return {"population": scope} if scope is not None else {"scope": None}


# ── not-measured notes ─────────────────────────────────────────────────────
# A count that comes back None is "not measured", never 0 and never the find
# cap. The value alone cannot say why, or what lower bound the fallback did
# see, so every count that returns None for that reason also records a note
# here; `recording_unmeasured()` collects them for whoever wants the words
# (the report-spec executor puts them on its output, see format_set_executor).
_UNMEASURED: "contextvars.ContextVar[Optional[List[Dict[str, Any]]]]" = contextvars.ContextVar(
    "pyegeria_unmeasured_counts", default=None)


@contextlib.contextmanager
def recording_unmeasured():
    """Collect a note for every count that is not measured while the block runs.

    Yields a list that fills with {"count": what was counted, "reason": why it is
    not measured, "at_least": the lower bound the find fallback saw, or None}.
    Notes are per context (a ContextVar), so a worker thread records into its own
    block, not its caller's."""
    notes: List[Dict[str, Any]] = []
    token = _UNMEASURED.set(notes)
    try:
        yield notes
    finally:
        _UNMEASURED.reset(token)


def _not_measured(what: str, reason: str, at_least: Optional[int] = None) -> None:
    logger.warning(f"overview_metrics: count of {what!r} not measured -- {reason}")
    notes = _UNMEASURED.get()
    if notes is not None:
        notes.append({"count": what, "reason": reason, "at_least": at_least})


def _native_failure_words(exc: Optional[BaseException], tried: bool) -> str:
    """What happened to the native count, in words, for a not-measured reason."""
    if not tried:
        return "no native count is available"
    if exc is None:
        return "the native count gave no number"
    text = str(exc).lower()
    if isinstance(exc, PyegeriaTimeoutException) or "timed out" in text or "timeout" in text or "408" in text:
        return "the native count timed out"
    return f"the native count failed ({type(exc).__name__})"


def _count_label(body: dict) -> str:
    label = body.get("metadataElementTypeName") or "elements"
    props = ((body.get("searchProperties") or {}).get("conditions")) or []
    words = [f"{c.get('property')} {'=' if c.get('operator') == 'EQ' else '!='} "
             f"{((c.get('value') or {}).get('primitiveValue'))!r}" for c in props if isinstance(c, dict)]
    if words:
        label = f"{label} with {' and '.join(words)}"
    conditions = ((body.get("matchClassifications") or {}).get("conditions")) or []
    names = [c.get("name") for c in conditions if isinstance(c, dict) and c.get("name")]
    return f"{label} classified {'/'.join(names)}" if names else label


def _capped_reason(native_words: str, n: int) -> str:
    return (f"{native_words}, and the find fallback stopped at its {DEFAULT_CAP}-element page cap, "
            f"so there are at least {n}")


def _element_count(mgr, body: dict, as_of: Optional[str] = None, strict: bool = False,
                   scope: Optional[str] = None) -> Optional[int]:
    """Count elements matching a FindRequestBody -- native when available, else
    len(find_metadata_elements(...)).

    scope="repository" (the default of every public count helper): only a
    native push-down count can answer. The len(find) fallback is always
    viewer-scoped, so it is NOT used -- a failed native count is None (strict
    or not) with a note, never 0 and never a viewer number masquerading as a
    repository one.

    scope="viewer" or None: the len(find) fallback answers when the native
    count cannot. None, with a note, when that query fails too (strict or not:
    a 0 would read as "none of them", 6.2.28), and None when it returned a full
    page (DEFAULT_CAP). That is only a lower bound, never a total, so it is
    never returned as one; the bound and the reason go to
    `recording_unmeasured()`'s notes. `strict` no longer changes any result; it
    is kept so existing callers still work.
    """
    push_down = _push_down(scope)
    kw = {} if push_down is None else {"push_down": push_down}
    b = dict(body)
    if as_of:
        b["asOfTime"] = as_of
    what = _count_label(body)
    name = _native_count_method(mgr, _ELEMENT_COUNT_CANDIDATES, "elem:" + type(mgr).__name__)
    tried, native_exc = False, None
    if name and not _native_disabled(mgr):
        tried = True
        try:
            c = _as_count(getattr(mgr, name)(b, **kw))
            if c is not None:
                return c
        except Exception as exc:  # noqa: BLE001 -- old server: mark unsupported, fall back
            native_exc = exc
            _disable_native(mgr, exc)
    native_words = _native_failure_words(native_exc, tried)
    if scope == SCOPE_REPOSITORY:
        # Strict or not: a repository count has no fallback, and 0 here would read as an empty catalog.
        _not_measured(what, f"{native_words}, and a repository-population count has no fallback "
                            f"(the find fallback only sees what the viewer may see)")
        return None
    found = _find_or_none(mgr, b)
    if found is None:  # strict or not: a failed query is not "none of them" (6.2.28)
        _not_measured(what, f"{native_words}, and the find fallback failed")
        return None
    if len(found) >= DEFAULT_CAP:  # a full page is a lower bound, never a total (strict or not)
        _not_measured(what, _capped_reason(native_words, len(found)), at_least=len(found))
        return None
    return len(found)


@_population_keyword
def count_elements(
    mgr,
    type_name: Optional[str] = None,
    as_of: Optional[str] = None,
    classifications: Optional[Sequence[str]] = None,
    strict: bool = False,
    scope: Optional[str] = SCOPE_REPOSITORY,
) -> Optional[int]:
    """
    Count ACTIVE elements, optionally of a given type and/or matching ANY of
    the given classifications, with native `count_metadata_elements`.

    In the repository population (the default) only the native count can
    answer: when it is unavailable, fails or times out the result is None,
    strict or not, with its reason recorded for `recording_unmeasured()`.

    Only in the viewer population (or scope=None) does a missing or failed
    native count fall back to `len(find_metadata_elements(...))`. There a
    failed query is None, not 0 (strict or not, since 6.2.28), and a fallback
    that stops at DEFAULT_CAP gives None, never the cap: that page is a lower
    bound, not a total (its bound and reason are recorded too).

    Parameters
    ----------
    mgr : MetadataExpert (or compatible client)
    type_name : the open-metadata type name to count (None = any type)
    as_of : ISO-8601 asOfTime for a point-in-time count (None = now)
    classifications : classification names to match ANY of -- keep to a
        single call's worth (some connectors mishandle 2+ ANY conditions)
    strict : no longer changes the result: a count that is not measured is
        None either way (since 6.2.28 a failed viewer query is None too, not 0).
        Kept so existing callers still work
    scope : "repository" (the default: push_down=True, a whole-repository raw
        count -- fast, and it includes elements the caller may not be able to
        see; a deliberate interim choice, until zone-aware push-down exists),
        "viewer" (push_down=False: only what the caller may see) or None (omit
        push_down; the server default, which is viewer-scoped). The len(find)
        fallback always answers in viewer scope, so with scope="repository" it
        is never used: a failed native count is None, strict or not.

    Returns
    -------
    Optional[int] -- None whenever the count is not measured: a failed or
    unavailable repository count, a failed viewer query, or a capped fallback
    (never 0 for any of those, and never raises)
    """
    body: Dict[str, Any] = {"class": "FindRequestBody", "limitResultsByStatus": ["ACTIVE"]}
    if type_name:
        body["metadataElementTypeName"] = type_name
    if classifications:
        body["matchClassifications"] = {
            "class": "SearchClassifications", "matchCriteria": "ANY",
            "conditions": [{"name": n} for n in classifications],
        }
    return _element_count(mgr, body, as_of, strict, scope)


@_population_keyword
def count_elements_by_property(
    mgr,
    type_name: str,
    property_name: str,
    property_value: str,
    as_of: Optional[str] = None,
    strict: bool = False,
    scope: Optional[str] = SCOPE_REPOSITORY,
    operator: str = "EQ",
) -> Optional[int]:
    """
    Count ACTIVE elements of a given type whose named string property equals
    a given value -- e.g. counting DigitalProduct elements by deploymentStatus
    (Overview dashboard's Data Products tile, OVERVIEW_NEXT_STEPS.md
    "Remaining app wiring"). Same count seam as count_elements -- native
    only in the repository population, a capped-find fallback only in the
    viewer population -- just with a searchProperties EQ (or NEQ) condition
    instead of a bare type filter: one cheap native COUNT call per distinct
    value, no element fetch, same cost class as the plain count.

    Parameters
    ----------
    mgr : MetadataExpert (or compatible client)
    type_name : the open-metadata type name to count
    property_name : the element property to match (e.g. "deploymentStatus")
    property_value : the exact string value to match
    as_of : ISO-8601 asOfTime for a point-in-time count (None = now)
    strict : as for count_elements -- accepted, changes nothing (not measured is always None)
    scope : as for count_elements ("repository" by default | "viewer" | None)
    operator : "EQ" (the default: the property equals `property_value`) or
        "NEQ" (it is set and differs -- e.g. property_value="" counts elements
        whose property is set to something other than the empty string)

    Returns
    -------
    Optional[int] -- as for count_elements
    """
    if operator not in ("EQ", "NEQ"):
        raise ValueError(f"count_elements_by_property: operator must be 'EQ' or 'NEQ'; got {operator!r}")
    body: Dict[str, Any] = {
        "class": "FindRequestBody",
        "metadataElementTypeName": type_name,
        "limitResultsByStatus": ["ACTIVE"],
        "searchProperties": {
            "class": "SearchProperties",
            "matchCriteria": "ALL",
            "conditions": [{
                "property": property_name,
                "operator": operator,
                "value": {"class": "PrimitiveTypePropertyValue", "typeName": "string", "primitiveValue": property_value},
            }],
        },
    }
    return _element_count(mgr, body, as_of, strict, scope)


@_population_keyword
def count_relationships(ce, relationship_type: str, as_of: Optional[str] = None, expert=None,
                        scope: Optional[str] = SCOPE_REPOSITORY) -> Optional[int]:
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
    ce : EgeriaTech (or another client with both get_relationships and the native
        count_relationships_between_elements; a bare ClassificationExplorer has
        only get_relationships, so it can answer a viewer count only)
    relationship_type : the relationship type name to count
    as_of : ISO-8601 asOfTime for a point-in-time count (None = now)
    expert : optional MetadataExpert to enable the native fast-path. With
        scope="repository" and no `expert`, `ce` itself is used when it has the
        native method (an EgeriaTech does; a bare ClassificationExplorer does not)
    scope : "repository" (the default: native push_down=True, whole repository,
        including relationships the caller may not be able to see), "viewer"
        (native push_down=False) or None (the get_relationships path, unless an
        `expert` is passed). Only the native path takes a scope; the
        get_relationships path is always viewer-scoped, so with
        scope="repository" it is never used -- no native method, an
        unsupported server or a failed native call gives None with a note, not
        a viewer number.

    Returns
    -------
    Optional[int] -- None on total failure, and None when the get_relationships
    page came back full (DEFAULT_CAP): that is a lower bound, never a total
    (its bound and reason are recorded for `recording_unmeasured()`). Never raises.
    """
    push_down = _push_down(scope)
    kw = {} if push_down is None else {"push_down": push_down}
    tried, native_exc = False, None
    if expert is None and scope == SCOPE_REPOSITORY:
        expert = ce  # only a native count can answer for the repository; ce may be able to give one
    if expert is not None and not _native_disabled(expert):
        name = _native_count_method(expert, _REL_COUNT_CANDIDATES, "rel:" + type(expert).__name__)
        if name:
            tried = True
            body = {"class": "FindRelationshipRequestBody", "relationshipTypeName": relationship_type,
                    "limitResultsByStatus": ["ACTIVE"]}
            if as_of:
                body["asOfTime"] = as_of
            try:
                c = _as_count(getattr(expert, name)(body, **kw))
                if c is not None:
                    return c
            except Exception as exc:  # noqa: BLE001
                native_exc = exc
                _disable_native(expert, exc)
    if scope == SCOPE_REPOSITORY:
        words = (_native_failure_words(native_exc, tried) if tried
                 else "no native relationship count is available (it needs a MetadataExpert client)")
        _not_measured(relationship_type, f"{words}, and a repository-population count has no fallback "
                                         f"(get_relationships only sees what the viewer may see)")
        return None
    try:
        # Paged to an empty page (Egeria's contract), so the count is every relationship the viewer may
        # see, not one page of them; an incomplete scan is None with its note (see _all_relationships).
        rels = _all_relationships(ce, relationship_type, as_of)
    except Exception as exc:  # noqa: BLE001
        logger.debug(f"overview_metrics count_relationships({relationship_type}) failed: {exc}")
        _not_measured(relationship_type, f"{_native_failure_words(native_exc, tried)}, and the "
                                         f"get_relationships fallback failed")
        return None
    return None if rels is None else len(rels)


@_population_keyword
def counts_by_type(mgr, type_map: Sequence[Tuple[str, str]], as_of: Optional[str] = None,
                   strict: bool = False, scope: Optional[str] = SCOPE_REPOSITORY) -> List[Dict[str, Any]]:
    """
    Per-type counts for a set of (label, type_name) pairs -- e.g. the assets-
    by-type composition breakdown. A type that cannot be counted (unknown,
    failed, timed out, or a capped fallback) is None for its own row, never 0,
    rather than failing the whole call (see count_elements). `scope` is passed
    to count_elements; `strict` is accepted for compatibility and changes
    nothing.

    Returns a list of {"label": ..., "type": ..., "count": ...} dicts, in the
    order given.
    """
    return [{"label": label, "type": type_name, "count": count_elements(mgr, type_name, as_of, strict=strict, **_pop(scope))}
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
    # strict: a failed count is None, not 0, so the total is None rather than an undercount.
    return run_analytic_action(spec, mgr, fetch_kwargs={"type_map": type_map, "as_of": as_of, "strict": True})


def sum_counts(by_type: List[Dict[str, Any]], mgr=None) -> Dict[str, Any]:
    """The analytic step for `sum_type_counts` -- receives `counts_by_type`'s
    raw result plus the same client `counts_by_type` itself was given
    (unused here; kept purely for calling-convention consistency with an
    analytic step that DOES need to fetch more -- e.g. following a
    relationship to enrich, the pattern `ai_ready_assets` already uses
    inline). Also directly reusable on a `by_type` result a caller already
    has, without re-fetching (see `sum_type_counts`'s docstring).

    `total` is None when any row's count is None (not measured): a sum over
    the measured rows only would read as the whole total."""
    counts = [r["count"] for r in by_type]
    total = None if any(c is None for c in counts) else sum(counts)
    return {"total": total, "byType": by_type}


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
    classification, by governance zone, and by a Fully/Partial 3-bucket split
    (Ungoverned isn't returned here -- it's `assetTotal - fully - partial`,
    computed the same way the frontend already derives its governed % using
    `assetTotal` as denominator, see egeria-overview.html's `governedPctNum`).

    The Fully/Partial split reuses the exact same `hits` list already
    fetched for `byClassification`/`topZones` above -- no extra round trip.
    "Partial (zone only)" = carries `ZoneMembership` and none of the other
    (substantive) governance classifications; "Fully governed" = carries at
    least one substantive classification (Confidentiality/Criticality/
    Impact/Retention), with or without a zone. Same population-scope caveat
    `governedCount` already carries: this query isn't restricted to Asset
    type, so these are catalog-wide counts, not Asset-only -- an existing,
    already-accepted proxy in this dashboard, not a new one introduced here.

    The find is paged until Egeria returns an empty page, so every figure
    covers every governed element. If it fails or the scan is incomplete
    (MAX_SCAN_PAGES; a note is recorded), governedCount/governedCapped/
    fullyGoverned/partialZoneOnly are None (unmeasured) and byClassification/
    topZones are empty. `governedCapped` is False whenever measured (kept for
    callers that read it).

    Returns {"governedCount": int|None, "byClassification": {name: count},
    "topZones": [{"zone": name, "count": count}, ...8 max],
    "fullyGoverned": int|None, "partialZoneOnly": int|None}.
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
    hits = _all_elements(mgr, body)  # every page; None when it failed or was incomplete (noted)
    if hits is None:  # unmeasured, not "nothing governed"
        return {
            "governedCount": None,
            "governedCapped": None,
            "byClassification": {},
            "topZones": [],
            "fullyGoverned": None,
            "partialZoneOnly": None,
        }

    substantive = set(GOVERNANCE_CLASSIFICATIONS) - {"ZoneMembership"}
    by_classification: Dict[str, int] = {}
    zone_counts: Dict[str, int] = {}
    fully_governed = 0
    partial_zone_only = 0
    for el in hits:
        names = _classifications_of(el)
        for name in names:
            by_classification[name] = by_classification.get(name, 0) + 1
        for z in _zone_names(el):
            if z:
                zone_counts[z] = zone_counts.get(z, 0) + 1
        governance_names = names & set(GOVERNANCE_CLASSIFICATIONS)
        if governance_names & substantive:
            fully_governed += 1
        elif "ZoneMembership" in governance_names:
            partial_zone_only += 1
    top_zones = sorted(zone_counts.items(), key=lambda kv: -kv[1])[:8]

    return {
        "governedCount": len(hits),
        "governedCapped": False,  # every page was read
        "byClassification": by_classification,
        "topZones": [{"zone": z, "count": c} for z, c in top_zones],
        "fullyGoverned": fully_governed,
        "partialZoneOnly": partial_zone_only,
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

    The find is paged until Egeria returns an empty page. If it fails or the
    scan is incomplete, ownershipCount/ownershipCapped are None (unmeasured, as
    in governed_coverage) and byOwnerType is empty -- not 0, which read as
    "nothing owned". `ownershipCapped` is False whenever measured.

    Returns {"ownershipCount": int|None, "ownershipCapped": bool|None,
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
    hits = _all_elements(mgr, body)  # every page; None when it failed or was incomplete (noted)
    if hits is None:  # unmeasured, not "nothing owned"
        return {"ownershipCount": None, "ownershipCapped": None, "byOwnerType": {}}

    by_owner_type: Dict[str, int] = {}
    for el in hits:
        owner_type = _owner_type_name(el) or "Unspecified"
        by_owner_type[owner_type] = by_owner_type.get(owner_type, 0) + 1

    return {
        "ownershipCount": len(hits),
        "ownershipCapped": False,  # every page was read
        "byOwnerType": by_owner_type,
    }


@_population_keyword
def business_value_signals(mgr, as_of: Optional[str] = None,
                           scope: Optional[str] = SCOPE_REPOSITORY) -> Dict[str, Any]:
    """
    Real signals behind the Overview dashboard's four "Business Value" tiles
    (NEXT-9) -- replaces the four previously-synthetic narrative numbers
    (Risk & Compliance, Productivity, Trust & Adoption, Cost Avoidance) with
    honest, precisely-scoped proxies. Deliberately proxies, not direct
    measures -- see each field's use-site in overview_handler.py / this
    function's own module docs for the causal-claim caveat that goes with
    it (e.g. "more described assets" is a proxy for self-service findability,
    not a measure of actual query/access frequency).

    Every field is a native count in one population, `scope` ("repository" by
    default: the whole repository, including elements the viewer may not be
    able to see; or "viewer"), so the asset-scoped shares never mix
    populations:

    - assetTotal: Assets (the supertype, so every subtype).
    - confidentialCount: Assets carrying Confidentiality.
    - describedCount: Assets whose `description` is set and not the empty
      string (`NEQ ""`; a whitespace-only description counts as described).
    - duplicateCount: elements of any type carrying ConsolidatedDuplicate.

    IMPORTANT scoping distinction from `governed_coverage`'s own
    `byClassification["Confidentiality"]`: that number is NOT Asset-scoped
    (any element type carrying the classification counts, per its own
    documented caveat), whereas `confidentialCount` here IS Asset-scoped
    (the count names the Asset type). Confirmed live 2026-08-02 on a real
    dataset: 5 total Confidentiality-classified elements exist, only 1 of
    which is Asset-typed (a CSVFile; the other 4 are typed `Referenceable`,
    not under `Asset`) -- the two numbers are both correct, just different
    populations, not a discrepancy to "fix."

    Data Products (Trust & Adoption) is deliberately NOT duplicated here --
    callers already have a live `dataProducts` count from
    `count_elements(mgr, "DigitalProduct", as_of)` elsewhere in the same
    request; no rating/adoption signal is wired (no `AttachedRating`
    relationships exist against `DigitalProduct` in a typical demo dataset,
    confirmed live -- so a rating average is honestly omitted rather than
    faked).

    These figures used to come from one capped Asset find, so on a catalog
    over DEFAULT_CAP assets they described the first page only. A count that
    was not measured is None, never 0. `assetCapped` is kept for callers that
    read it: False when assetTotal was measured (a native count is
    complete), None when it was not.

    Returns {"assetTotal": int|None, "assetCapped": bool|None,
    "confidentialCount": int|None, "describedCount": int|None,
    "duplicateCount": int|None}.
    """
    total = count_elements(mgr, "Asset", as_of, strict=True, **_pop(scope))
    return {
        "assetTotal": total,
        "assetCapped": None if total is None else False,
        "confidentialCount": count_elements(mgr, "Asset", as_of, classifications=["Confidentiality"],
                                            strict=True, **_pop(scope)),
        "describedCount": count_elements_by_property(mgr, "Asset", "description", "", as_of, strict=True,
                                                     **_pop(scope), operator="NEQ"),
        "duplicateCount": count_elements(mgr, None, as_of, classifications=["ConsolidatedDuplicate"],
                                         strict=True, **_pop(scope)),
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
    The Certification relationships are paged to Egeria's empty page; an
    incomplete scan leaves active/expiring90 None (with a note), never a count
    of the first page.
    """
    from datetime import datetime, timezone, timedelta

    out: Dict[str, Any] = {"active": None, "expiring90": None, "soon": [], "licenses": None, "exceptions": None}
    try:
        certs = _all_relationships(ce, "Certification", as_of)  # every page, not the first
        if certs is None:  # incomplete scan (noted): active/expiring are not measured, not a count of a page
            raise _ScanIncomplete()
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
    except _ScanIncomplete:
        pass
    except Exception as exc:  # noqa: BLE001
        logger.debug(f"overview_metrics certifications_summary: query failed: {exc}")

    # One population per payload: active/expiring come from a get_relationships scan (viewer-scoped).
    out["licenses"] = count_relationships(ce, "License", as_of, population=SCOPE_VIEWER)
    out["exceptions"] = count_relationships(ce, "Exception", as_of, population=SCOPE_VIEWER)
    return out


def orphan_glossary_terms(mgr, ce, as_of: Optional[str] = None) -> Dict[str, Optional[int]]:
    """
    Approved-but-unassigned glossary terms -- the Attention Queue's "Orphan
    glossary terms" row. A term with no `SemanticAssignment` relationship to
    anything (asset, schema element, data field, ...) was authored but never
    actually put to use grounding the catalog -- a stewardship gap distinct
    from `semantic_grounding`'s own asset-side coverage % (that one asks "how
    much of the catalog is grounded"; this one asks "how much of the
    glossary is idle").

    Same relationship-scan shape as `contextualised_coverage` (ImplementedBy):
    every `SemanticAssignment` relationship, paged until Egeria returns an
    empty page, filtered to the GlossaryTerm-typed end; the distinct-GUID count
    is the "referenced" set; orphan = term total - referenced. An incomplete
    scan makes referencedCount and orphanCount None (with a note), never a
    figure from the pages it did read: one 500-relationship page held 8
    distinct terms live (2026-11-08), all 747 held 77, so a one-page scan
    reported 1,053 orphans instead of 984. Not scoped to "approved" status
    specifically (Egeria's term status isn't filtered here) -- same
    catalog-wide-not-sub-filtered tradeoff `governedCount` etc. already
    carry, not a new one.

    Egeria cannot count the distinct ends of a relationship type natively, so
    the referenced set needs the scan. The term total is counted in the
    viewer population, because the scan only sees what the viewer may see,
    and a viewer count is slow (13.5 s live for 1,061 terms, against 0.7 s
    for the repository count). So it runs on its own thread while the scan
    pages (6.2.29): the routine takes about as long as the slower of the two,
    not their sum. Its note, if any, still reaches the caller's
    `recording_unmeasured()`.

    Returns {"termTotal": int|None, "referencedCount": int|None,
    "orphanCount": int|None}. Any field is None on total failure for its own
    step (never raises).
    """
    # One population per payload: this payload's other figures come from a scan, which only sees what the
    # viewer may see, so its native total is counted in the viewer population too (never a repository
    # total under a viewer numerator). Two reads at once, not one after the other.
    pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="orphan-terms")
    term_future = pool.submit(contextvars.copy_context().run, count_elements, mgr, "GlossaryTerm", as_of,
                              strict=True, population=SCOPE_VIEWER)
    pool.shutdown(wait=False)

    referenced_count = None
    try:
        rels = _all_relationships(ce, "SemanticAssignment", as_of)  # every page: one page is not the set
        term_guids: set = set()
        for r in rels or []:
            for end_key in ("end1", "end2"):
                end = (r.get(end_key) or {}) if isinstance(r, dict) else {}
                end_type = end.get("type") or {}
                type_names = {end_type.get("typeName")} | set(end_type.get("superTypeNames") or [])
                if "GlossaryTerm" in type_names and end.get("guid"):
                    term_guids.add(end["guid"])
        referenced_count = None if rels is None else len(term_guids)
    except Exception as exc:  # noqa: BLE001
        logger.debug(f"orphan_glossary_terms: SemanticAssignment query failed: {exc}")

    try:
        term_total = term_future.result()
    except Exception as exc:  # noqa: BLE001 -- count_elements does not raise; belt and braces
        logger.debug(f"orphan_glossary_terms: GlossaryTerm count failed: {exc}")
        _not_measured("GlossaryTerm", f"the count failed ({type(exc).__name__})")
        term_total = None

    orphan_count = None
    if term_total is not None and referenced_count is not None:
        orphan_count = max(term_total - referenced_count, 0)

    return {"termTotal": term_total, "referencedCount": referenced_count, "orphanCount": orphan_count}


def stale_assets(mgr, as_of: Optional[str] = None, days: int = 180) -> Dict[str, Optional[int]]:
    """
    Assets with no update in the last `days` -- the Attention Queue's "Stale
    assets" row, candidates for archival review.

    Both figures are in the repository population (the whole repository,
    including Assets the viewer may not be able to see), so the payload never
    mixes populations:

    - assetTotal: the native push-down count of ACTIVE Assets.
    - staleCount: how many of those were last updated before the cutoff.
      Egeria cannot count by an update-time condition, but it sorts by update
      time, so this is a bisection over the sorted rows' offsets
      (`_rows_updated_before`): about log2(assetTotal / 25) one-row reads and
      one read of the last 25-row window (12 for 37,000 Assets), never a page
      of Assets (6.2.29). An Asset updated while
      the bisection runs can shift the offsets by one.

    `as_of` anchors both the query and the cutoff clock (an as-of-time
    dashboard view should ask "stale as of that moment", not "stale as of
    right now" -- consistent with `certifications_summary`'s own as_of
    anchoring).

    Returns {"staleCount": int|None, "assetTotal": int|None}. Either is None,
    with an `unmeasured` note, when it is not measured: the native count
    failed (staleCount bisects over it, so it is None too), a read failed,
    rows the viewer cannot see sit exactly at the cutoff (the note gives the
    range), or the reads ran out. Never a figure from a sample of Assets.
    """
    from datetime import datetime, timezone, timedelta

    what = f"Assets not updated within {days} days"
    body: Dict[str, Any] = {"class": "FindRequestBody", "metadataElementTypeName": "Asset",
                            "limitResultsByStatus": ["ACTIVE"]}
    total = _element_count(mgr, body, as_of, scope=SCOPE_REPOSITORY)  # noted when not measured
    if total is None:
        _not_measured(what, "the Asset count it bisects over was not measured")
        return {"staleCount": None, "assetTotal": None}
    anchor = datetime.now(timezone.utc)
    if as_of:
        try:
            anchor = datetime.fromisoformat(as_of.replace("Z", "+00:00"))
        except ValueError:
            _not_measured(what, f"as_of {as_of!r} is not an ISO-8601 time, so there is no cutoff")
            return {"staleCount": None, "assetTotal": total}
        if anchor.tzinfo is None:
            anchor = anchor.replace(tzinfo=timezone.utc)
    b = dict(body, asOfTime=as_of) if as_of else dict(body)
    stale_count = _rows_updated_before(mgr, b, anchor - timedelta(days=days), total, what)
    return {"staleCount": stale_count, "assetTotal": total}


def _is_asset_end(end: Dict[str, Any]) -> bool:
    """True when a relationship end is an Asset (its type, or one of its supertypes, is Asset)."""
    end_type = end.get("type") or {}
    return "Asset" in ({end_type.get("typeName")} | set(end_type.get("superTypeNames") or []))


def semantic_grounding(mgr, ce, as_of: Optional[str] = None) -> Dict[str, Any]:
    """
    Semantic-grounding tally: how much of the catalog is linked to glossary
    terms by `SemanticAssignment` -- the "meaning layer" that grounds AI context.

    Two measures, each in one population:

    - `groundedAssets` / `groundedAssetPct` (6.2.31): the number of
      DISTINCT Assets with at least one SemanticAssignment, and that number as
      a percent of all Assets. Egeria cannot count the distinct ends of a
      relationship type natively, so the count comes from a scan of every
      SemanticAssignment (paged until Egeria returns an empty page), keeping
      the Asset-typed ends. A scan sees only what the caller may see, so the
      Asset total it divides by is counted in the same, viewer population
      (`groundedAssetTotal`), on its own thread while the scan pages. When
      that total cannot be measured (it times out on a large catalog),
      `groundedAssetPct` is None with its reason recorded: never a viewer
      count over a repository total. An incomplete scan makes both None.
    - `groundingLinks` / `groundingPct`: the native, repository-wide count of
      SemanticAssignment relationships, and that count per hundred Assets
      (the repository Asset total), at most 100. This is links, not Assets:
      one Asset with three terms counts three times, and a link to a
      non-Asset counts too. Kept for callers that read it.

    `mgr` is the MetadataExpert the native counts need.

    Returns {"groundedAssets": int|None, "groundedAssetTotal": int|None,
    "groundedAssetPct": int|None, "groundingLinks": int|None,
    "groundingPct": int|None}.
    """
    pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="grounding-assets")
    total_future = pool.submit(contextvars.copy_context().run, count_elements, mgr, "Asset", as_of,
                               strict=True, population=SCOPE_VIEWER)
    pool.shutdown(wait=False)

    cataloged = count_elements(mgr, "Asset", as_of, strict=True, population=SCOPE_REPOSITORY)
    links = count_relationships(ce, "SemanticAssignment", as_of, expert=mgr, population=SCOPE_REPOSITORY)
    pct = min(100, round(100 * links / cataloged)) if cataloged and links is not None else None

    grounded = None
    try:
        rels = _all_relationships(ce, "SemanticAssignment", as_of)  # every page: one page is not the set
        if rels is not None:
            assets: set = set()
            for r in rels:
                for end_key in ("end1", "end2"):
                    end = (r.get(end_key) or {}) if isinstance(r, dict) else {}
                    if end.get("guid") and _is_asset_end(end):
                        assets.add(end["guid"])
            grounded = len(assets)
    except Exception as exc:  # noqa: BLE001
        logger.debug(f"semantic_grounding: SemanticAssignment scan failed: {exc}")
        _not_measured("SemanticAssignment relationships", f"the scan failed ({type(exc).__name__})")

    try:
        asset_total = total_future.result()
    except Exception as exc:  # noqa: BLE001 -- count_elements does not raise; belt and braces
        logger.debug(f"semantic_grounding: viewer Asset count failed: {exc}")
        _not_measured("Asset", f"the count failed ({type(exc).__name__})")
        asset_total = None

    grounded_pct = (min(100, round(100 * grounded / asset_total))
                    if grounded is not None and asset_total else None)
    return {"groundedAssets": grounded, "groundedAssetTotal": asset_total, "groundedAssetPct": grounded_pct,
            "groundingLinks": links, "groundingPct": pct}


def context_readiness_funnel(mgr, ce, as_of: Optional[str] = None) -> Dict[str, Optional[int]]:
    """
    Context-readiness funnel stages: how much cataloged data becomes
    trustworthy AI context.

    Every stage is a native count in the repository population (the whole
    repository, including elements the viewer may not be able to see), so the
    stages can be compared without mixing populations.

    `documented` -- count of `Asset` elements whose `description` is set and
    not the empty string (a native `NEQ ""` property count, the same one
    `term_definition_completeness` uses; a whitespace-only description counts
    as documented).

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

    `cataloged` and `classified` are None only when unmeasured (query failed,
    or the fallback count hit DEFAULT_CAP); a measured 0 is returned as 0.

    Returns {"cataloged": int|None, "documented": int|None, "classified": int|None,
    "lineage": int|None, "aiReady": None}.
    """
    pop = SCOPE_REPOSITORY
    cataloged = count_elements(mgr, "Asset", as_of, strict=True, population=pop)
    classified = count_elements(mgr, None, as_of, classifications=GOVERNANCE_CLASSIFICATIONS, strict=True,
                                population=pop)
    documented = count_elements_by_property(mgr, "Asset", "description", "", as_of, strict=True,
                                            population=pop, operator="NEQ")
    lineage = count_relationships(ce, "DataFlow", as_of, expert=mgr, population=pop)

    return {
        "cataloged": cataloged,
        "documented": documented,
        "classified": classified,
        "lineage": lineage,
        "aiReady": None,
    }


def _lineage_guids(ce, as_of: Optional[str], who: str) -> Optional[set]:
    """GUIDs at either end of any DataFlow relationship (every page), or None when the scan failed or was
    incomplete (an incomplete one is noted)."""
    try:
        rels = _all_relationships(ce, "DataFlow", as_of)
    except Exception as exc:  # noqa: BLE001
        logger.debug(f"{who}: DataFlow relationship query failed: {exc}")
        return None
    if rels is None:
        return None
    return {g for r in rels if isinstance(r, dict) for k in ("end1", "end2")
            if (g := (r.get(k) or {}).get("guid"))}


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

    The Asset find is one DEFAULT_CAP page. When that page is full it is a
    sample, not the catalog, so aiReadyCount and total are None with an
    `unmeasured` note and capped is True (6.2.28; it used to report the
    sample's count). The DataFlow relationships are paged until Egeria returns
    an empty page.

    Returns {"aiReadyCount": int|None, "total": int|None, "capped": bool|None}
    -- "total" is the Asset population checked (every Asset, since a full page
    is not measured), so a caller can compute a percentage without a separate
    cataloged-count call. A failed Asset find makes all three None; a failed or
    incomplete DataFlow scan makes aiReadyCount None (no asset can be shown
    lineage-traced, which is not the same as none being so) and keeps
    total/capped.
    """
    body: Dict[str, Any] = {"class": "FindRequestBody", "limitResultsByStatus": ["ACTIVE"],
                             "metadataElementTypeName": "Asset"}
    if as_of:
        body["asOfTime"] = as_of
    assets = _find_or_none(mgr, body)
    if assets is None:
        return {"aiReadyCount": None, "total": None, "capped": None}
    if len(assets) >= DEFAULT_CAP:
        # A full page is a sample of the Assets, not all of them: a count from it is not the count.
        _not_measured("AI-ready Assets", f"the Asset find stopped at its {DEFAULT_CAP}-element page cap, so "
                                         f"only the first {len(assets)} Assets could be checked", at_least=None)
        return {"aiReadyCount": None, "total": None, "capped": True}

    lineage_guids = _lineage_guids(ce, as_of, "ai_ready_assets")
    if lineage_guids is None:
        return {"aiReadyCount": None, "total": len(assets), "capped": False}

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

    return {"aiReadyCount": ai_ready, "total": len(assets), "capped": False}


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

    Returns {"total": int|None, "capped": bool|None, "aiReadyCount": int|None,
    "aiReadyRecentCount": int|None, "byModality": {"tabular", "text_media", "other"}|None}.
    A failed Asset find makes every field None; a full Asset page (a sample,
    not the catalog) makes every field None too, with capped True and an
    `unmeasured` note (6.2.28); a failed or incomplete DataFlow scan makes
    aiReadyCount/aiReadyRecentCount None and keeps the rest -- unmeasured, not 0.
    """
    from datetime import datetime, timedelta, timezone

    body: Dict[str, Any] = {"class": "FindRequestBody", "limitResultsByStatus": ["ACTIVE"],
                             "metadataElementTypeName": "Asset"}
    if as_of:
        body["asOfTime"] = as_of
    assets = _find_or_none(mgr, body)
    if assets is None:
        return {"total": None, "capped": None, "aiReadyCount": None, "aiReadyRecentCount": None,
                "byModality": None}
    if len(assets) >= DEFAULT_CAP:
        # A full page is a sample of the Assets, not all of them: no figure here may describe it as all.
        _not_measured("DRL readiness gates", f"the Asset find stopped at its {DEFAULT_CAP}-element page cap, "
                                             f"so only the first {len(assets)} Assets could be checked")
        return {"total": None, "capped": True, "aiReadyCount": None, "aiReadyRecentCount": None,
                "byModality": None}

    lineage_guids = _lineage_guids(ce, as_of, "drl_readiness_gates")

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
        lineage_traced = lineage_guids is not None and guid in lineage_guids
        if not (documented and governed and lineage_traced):
            continue
        ai_ready += 1

        updated = _update_time(a)
        if updated is not None and (now - updated) <= horizon:
            ai_ready_recent += 1

    return {
        "total": len(assets),
        "capped": False,
        "aiReadyCount": ai_ready if lineage_guids is not None else None,
        "aiReadyRecentCount": ai_ready_recent if lineage_guids is not None else None,
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


@_population_keyword
def people_counts(mgr, as_of: Optional[str] = None, strict: bool = False, scope: Optional[str] = SCOPE_REPOSITORY) -> Dict[str, Optional[int]]:
    """
    Person / Team / Organization / ITProfile / Community counts via native
    element counts (sub-second where an older find-and-bucket approach would
    materialize every profile). NB: this counts every entity of the type in
    the repository; a curated find-and-bucket approach can return a smaller,
    filtered set, so totals may differ from an older implementation -- this
    raw count is the authoritative repository count.

    Returns {"persons": int|None, "teams": int|None, "organizations": int|None,
    "itProfiles": int|None, "communities": int|None}. A count that could not be
    measured is None, never 0 (see count_elements; `strict` changes nothing).
    """
    return {
        "persons": count_elements(mgr, "Person", as_of, strict=strict, **_pop(scope)),
        "teams": count_elements(mgr, "Team", as_of, strict=strict, **_pop(scope)),
        "organizations": count_elements(mgr, "Organization", as_of, strict=strict, **_pop(scope)),
        "itProfiles": count_elements(mgr, "ITProfile", as_of, strict=strict, **_pop(scope)),
        "communities": count_elements(mgr, "Community", as_of, strict=strict, **_pop(scope)),
    }


_FEEDBACK_RELATIONSHIP_TYPES = (
    ("AttachedRating", "ratings"),
    ("AttachedComment", "comments"),
    ("AttachedLike", "likes"),
    ("AttachedTag", "tags"),
    ("AttachedNoteLog", "noteLogs"),
)


@_population_keyword
def feedback_summary(ce, as_of: Optional[str] = None, scope: Optional[str] = SCOPE_REPOSITORY, expert=None) -> Dict[str, Any]:
    """
    Crowd-sourced feedback tally -- ratings/comments/likes/tags/note-logs
    (Collaboration OMAS relationship counts). Often sparse in demo data, but
    real.

    `scope` (and the MetadataExpert it needs, `expert`) are passed to
    count_relationships; scope="repository" without `expert` yields None for
    every type.

    A type whose count failed is None in `byType`; `total` is None unless every
    type was measured (a partial sum would read as "less feedback").

    Returns {"byType": {ratings, comments, likes, tags, noteLogs: int|None},
    "total": int|None}.
    """
    by_type = {key: count_relationships(ce, rel, as_of, expert=expert, **_pop(scope)) for rel, key in _FEEDBACK_RELATIONSHIP_TYPES}
    measured = all(v is not None for v in by_type.values())
    return {"byType": by_type, "total": sum(by_type.values()) if measured else None}


@_population_keyword
def usage_context_counts(mgr, as_of: Optional[str] = None, strict: bool = False, scope: Optional[str] = SCOPE_REPOSITORY) -> Dict[str, Optional[int]]:
    """
    InformationSupplyChain and SolutionBlueprint counts -- what puts assets
    in a *usage context* ("this store feeds the Clinical Trial supply
    chain", "this component realises the Sales blueprint").

    Returns {"informationSupplyChains": int|None, "blueprints": int|None}. A
    count that could not be measured is None, never 0 (see count_elements;
    `strict` changes nothing).
    """
    return {
        "informationSupplyChains": count_elements(mgr, "InformationSupplyChain", as_of, strict=strict, **_pop(scope)),
        "blueprints": count_elements(mgr, "SolutionBlueprint", as_of, strict=strict, **_pop(scope)),
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

    Every ImplementedBy relationship is read, paged until Egeria returns an
    empty page; an incomplete scan makes contextualisedCount None (with a
    note), never a count from the pages it did read.

    Returns {"contextualisedCount": int|None, "assetTotal": int|None,
    "contextualisedPct": float|None}. Any field is None on total failure for
    its own step (never raises).
    """
    contextualised_count = None
    try:
        rels = _all_relationships(ce, "ImplementedBy", as_of)  # every page; None when incomplete (noted)
        if rels is None:
            raise _ScanIncomplete()
        asset_guids: set = set()
        for r in rels:
            for end_key in ("end1", "end2"):
                end = (r.get(end_key) or {}) if isinstance(r, dict) else {}
                end_type = end.get("type") or {}
                type_names = {end_type.get("typeName")} | set(end_type.get("superTypeNames") or [])
                if "Asset" in type_names and end.get("guid"):
                    asset_guids.add(end["guid"])
        contextualised_count = len(asset_guids)
    except _ScanIncomplete:
        pass
    except Exception as exc:  # noqa: BLE001
        logger.debug(f"contextualised_coverage: ImplementedBy query failed: {exc}")

    # One population per payload: this payload's other figures come from a find, which only sees what the
    # viewer may see, so its native total is counted in the viewer population too (never a repository
    # total under a viewer numerator).
    asset_total = count_elements(mgr, "Asset", as_of, strict=True, population=SCOPE_VIEWER)

    pct = None
    if contextualised_count is not None and asset_total:
        pct = round(100.0 * contextualised_count / asset_total, 1)

    return {
        "contextualisedCount": contextualised_count,
        "assetTotal": asset_total or None,
        "contextualisedPct": pct,
    }


def solution_component_realisation(mgr, ce, as_of: Optional[str] = None) -> Dict[str, Optional[int]]:
    """
    SolutionComponent count and how many of them are "realised" (have at
    least one concrete implementation) -- Overview dashboard's Solution
    Blueprints drill-down panel, whose secondary stats ("components",
    "realised by") were hardcoded placeholder dashes (drillLivePatch only
    ever overlaid the headline blueprint count, stats[0]).

    `solutionComponentsTotal` is a plain native count (count_elements,
    same cost class as usage_context_counts' blueprint/ISC counts).
    `solutionComponentsRealised` reuses the exact ImplementedBy relationship
    fetch contextualised_coverage already makes (model 0737, Solution
    Implementation) -- that function counts distinct Asset-subtype end2
    GUIDs; this one counts distinct SolutionComponent end1 GUIDs from the
    same relationship instead, i.e. how many components have >=1 real
    implementation rather than how many assets got *some* context. Two
    independent relationship fetches (this function does not share
    contextualised_coverage's already-fetched list), same as every other
    metric function in this module -- consistent with the codebase's
    one-function-one-fetch convention, at the cost of one duplicate
    ImplementedBy fetch when both are called together (as the Usage Context
    endpoint does).

    Honesty note: a component with an ImplementedBy link has *a* concrete
    implementation, not necessarily one that itself participates in the
    ISC/blueprint the component is drawn from -- same single-hop proxy
    tradeoff as contextualised_coverage's own docstring.

    Returns {"solutionComponentsTotal": int|None, "solutionComponentsRealised":
    int|None}. Either field is None on total failure for its own step (never
    raises).
    """
    # One population per payload: this payload's other figures come from a find, which only sees what the
    # viewer may see, so its native total is counted in the viewer population too (never a repository
    # total under a viewer numerator).
    total = count_elements(mgr, "SolutionComponent", as_of, strict=True, population=SCOPE_VIEWER)

    realised_count = None
    try:
        rels = _all_relationships(ce, "ImplementedBy", as_of)  # every page; None when incomplete (noted)
        if rels is None:
            raise _ScanIncomplete()
        component_guids: set = set()
        for r in rels:
            end1 = (r.get("end1") or {}) if isinstance(r, dict) else {}
            end1_type = end1.get("type") or {}
            type_names = {end1_type.get("typeName")} | set(end1_type.get("superTypeNames") or [])
            if "SolutionComponent" in type_names and end1.get("guid"):
                component_guids.add(end1["guid"])
        realised_count = len(component_guids)
    except _ScanIncomplete:
        pass
    except Exception as exc:  # noqa: BLE001
        logger.debug(f"solution_component_realisation: ImplementedBy query failed: {exc}")

    return {
        "solutionComponentsTotal": total or None,
        "solutionComponentsRealised": realised_count,
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

    `find_metadata_elements`, paged until Egeria returns an empty page,
    returns every ContributionRecord with properties + classifications
    attached (an incomplete scan gives an empty list with an `unmeasured`
    note, never the top of one page); this
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
        # Every page: a top-N from one page is the top of that page, not of everyone.
        records = _all_elements(mgr, body)
    except Exception as exc:  # noqa: BLE001
        logger.debug(f"karma_leaderboard: find failed: {exc}")
        return []
    if records is None:  # failed, or incomplete (noted): no leaderboard rather than a wrong one
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

    Each relationship type is read in full, paged until Egeria returns an
    empty page. A type whose query failed or whose scan was incomplete is None
    in every week (with an `unmeasured` note), and so is every week's total --
    never a row of zeros (6.2.28; a failed type used to read as no activity).

    Returns a list of {"week": "2026-W33", "comments": int|None, "ratings":
    int|None, "likes": int|None, "tags": int|None, "noteLogs": int|None,
    "total": int|None}, oldest week first, length == `weeks` (never raises).
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

    unmeasured_fields: set = set()
    for rel_type, field in _FEEDBACK_RELATIONSHIP_TYPES_FOR_SERIES:
        try:
            rels = _all_relationships(ce, rel_type, as_of)  # every page; None when incomplete (noted)
        except Exception as exc:  # noqa: BLE001
            logger.debug(f"engagement_series: {rel_type} query failed: {exc}")
            _not_measured(f"{rel_type} relationships", "the get_relationships query failed")
            rels = None
        if rels is None:  # not measured: None in every week, never a row of zeros
            unmeasured_fields.add(field)
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
        b: Dict[str, Optional[int]] = {k: (None if k in unmeasured_fields else v) for k, v in buckets[wk].items()}
        series.append({"week": wk, **b, "total": None if unmeasured_fields else sum(b.values())})
    return series


def growth_series(
    mgr,
    window: str = "6mo",
    points: Optional[int] = None,
    type_map: Optional[Sequence[Tuple[str, Optional[str], Optional[Sequence[str]]]]] = None,
    population: str = SCOPE_REPOSITORY,
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
    population : "repository" (the default: whole-repository native counts,
        including elements the viewer may not be able to see) or "viewer"

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

    _push_down(population)  # ValueError for an unknown population, before any count
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
                point[key] = count_elements(mgr, type_name, as_of, classifications=classifications, strict=True,
                                            **_pop(population))
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

    `metric_path` names the function the way a report spec's
    `analytic_function` does: a registered analytic function name (e.g.
    "governed_coverage"). It is resolved through the report-spec resolver
    (ISSUE-173), so a caller-supplied value gets the same allowlist check.
    Only registered names are accepted; a dotted path is refused
    (AnalyticFunctionRefused, since 6.2.19).

    Pass both `mgr` and `ce` regardless of what the target function actually
    needs -- only the client parameter names it declares (by leading
    positional parameter named "mgr"/"ce") are bound; the other is unused.
    `mgr` is an EgeriaTech: a slot the target declares as
    `egeria_client:EgeriaTech` gets `mgr`, even one named `ce` --
    feedback_summary and count_relationships count repository relationships
    through `ce`, which needs MetadataExpert's native count, and a
    ClassificationExplorer lacks it.

    `metric_params` are extra keyword arguments forwarded to the target
    function at every snapshot (e.g. `classifications` for `count_elements`);
    `as_of` is supplied by this function and must not be included there.

    Returns a list of dicts, oldest first: {"label", "date", **snapshot} --
    the target function's result is merged directly into the point if it's a
    dict (matching growth_series's flat-per-point shape), else stored under
    "value". A snapshot that raises logs at debug and stores None instead of
    aborting the whole series.
    """
    from datetime import datetime, timezone
    from pyegeria.view.format_set_executor import resolve_report_spec_function  # lazy: keeps the design boundary

    func = resolve_report_spec_function(metric_path)

    clients = {"mgr": mgr, "ce": ce}
    from pyegeria.view.analytic_registry import get_analytic_registry  # lazy, as above
    target = get_analytic_registry().get(metric_path)
    declared = list(getattr(target, "inputs", None) or [])
    bound_args = []
    for pname, param in inspect.signature(func).parameters.items():
        if pname in _CLIENT_PARAM_NAMES and param.kind in (
            inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD,
        ):
            i = len(bound_args)
            wants_tech = i < len(declared) and declared[i] == "egeria_client:EgeriaTech"
            bound_args.append(mgr if wants_tech else clients[pname])
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

    Both numbers are native counts in the repository population (the whole
    repository, including terms the viewer may not be able to see), so the
    ratio never divides a viewer-scoped numerator by a repository total:
    `total` counts GlossaryTerms, `defined` those whose `description` is set
    and not the empty string (`NEQ ""`). A whitespace-only description counts
    as defined -- Egeria's LIKE (regex) condition counted 0 for every pattern
    tried live (2026-11-08), so "not blank" cannot be counted natively; live,
    9 of 1061 terms differ. This used to scan one page of terms, so on a
    glossary over DEFAULT_CAP terms the total was the page size, not the total.

    Returns {"total": int|None, "defined": int|None, "undefinedPct": int|None}
    (`undefinedPct` mirrors `semantic_grounding.groundingPct`'s naming: the
    gap, not the coverage, since a near-100%-defined glossary is the
    uninteresting case and the gap is what's actionable). A count that was not
    measured is None, and so is the percentage -- unmeasured, not an empty
    glossary.
    """
    pop = SCOPE_REPOSITORY
    total = count_elements(mgr, "GlossaryTerm", as_of, strict=True, population=pop)
    defined = count_elements_by_property(mgr, "GlossaryTerm", "description", "", as_of, strict=True,
                                         population=pop, operator="NEQ")
    undefined_pct = (round(100 * (total - defined) / total)
                     if total and defined is not None else None)
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

    Each type is read in full, paged until Egeria returns an empty page. A
    type whose query failed or whose scan was incomplete is None in byType,
    and `contributors` is None unless every type was read -- a partial union would read as fewer people,
    the same rule feedback_summary's `total` follows.
    """
    def _actor_usernames(rel_type: str) -> set:
        rels = _all_relationships(ce, rel_type, as_of)  # every page; None when incomplete (noted)
        if rels is None:
            raise _ScanIncomplete()
        return {
            u for rel in rels
            if (u := (rel.get("relationshipHeader") or {}).get("versions", {}).get("createdBy"))
        }

    by_type: Dict[str, Optional[int]] = {}
    all_users: set = set()
    measured = True
    for rel_type, key in _FEEDBACK_RELATIONSHIP_TYPES:
        try:
            users = _actor_usernames(rel_type)
        except _ScanIncomplete:
            by_type[key] = None
            measured = False
            continue
        except Exception as exc:  # noqa: BLE001
            logger.debug(f"overview_metrics active_contributors: {rel_type} failed: {exc}")
            by_type[key] = None
            measured = False
            continue
        by_type[key] = len(users)
        all_users |= users
    return {"contributors": len(all_users) if measured else None, "byType": by_type}


def control_implementation_summary(client, soa_guid: str) -> Dict[str, int]:
    """
    Count the applicable controls in a statement of applicability by
    implementation status -- the input to an "Annex A control implementation
    rate" style metric.

    Every ControlImplementationStatus value is a key, so a zero is a real
    count. A control with no implementation status counts as NOT_STARTED (the
    enum's default); controls marked not applicable are left out.

    Parameters
    ----------
    client : SecurityOfficer (or EgeriaTech)
    soa_guid : the statement of applicability's GUID, or its qualified name

    Returns
    -------
    dict -- {status: count}, one key per ControlImplementationStatus value
    """
    return client.get_control_implementation_summary(soa_guid)["byStatus"]


# ── Asset composition (RS-W1-4): the Asset subtype tree, counted in two scopes ──
#
# One routine today, opaque to the executor (as the reporting model's §7 allows).
# In the reporting model's §10.8 words it is four stages, so step (a'') can split
# it later without changing what it returns:
#   1. a `typedefs` producer   -- asset_subtype_tree(): the subtype tree under root;
#   2. a per-row `derive`      -- each row counted in viewer scope;
#   3. a per-row `derive`      -- each row counted in repository scope;
#   4. a `difference`          -- not_visible = repository - viewer per row, and each
#                                 parent's `other` row = parent - sum(children).

#: The cell's word for which population was counted ("viewer" | "repository"). The
#: owner chose `population` (RS-W1-1 §5). The keywords are `populations=` (asset_composition) and
#: `population=` (the count helpers); `scopes=` / `scope=` remain as deprecated aliases.
POPULATION_WORD = "population"

#: Cell and row states. A 0 is nothing_found; a failure is not_measured, never 0.
CELL_MEASURED = "measured"
CELL_NOTHING_FOUND = "nothing_found"
CELL_NOT_MEASURED = "not_measured"
_ESTABLISHED = (CELL_MEASURED, CELL_NOTHING_FOUND)

#: Completeness of an established cell, per population: a repository count is the
#: whole repository; a viewer count is what one person's client may see, which the
#: routine cannot judge complete (RS-W1-1 §5 default under a person's client).
_COMPLETENESS = {SCOPE_REPOSITORY: "complete", SCOPE_VIEWER: "unknown"}

#: Concurrency is a performance parameter below Egeria's database pool (10
#: connections): the default leaves room for other users; the cap is never exceeded.
COMPOSITION_DEFAULT_CONCURRENCY = 3
COMPOSITION_MAX_CONCURRENCY = 5


class CompositionCell(TypedDict, total=False):
    """One count of one row in one population."""
    value: Optional[int]       # None unless state is measured or nothing_found
    state: str                 # measured | nothing_found | not_measured
    completeness: str          # complete (repository) | unknown (viewer, or not measured)
    as_of: str                 # when the count is of: the requested as_of, else the run time
    population: str            # viewer | repository (POPULATION_WORD)
    reason: str                # why not measured; "" when established
    elapsed_s: Optional[float] # wall time of this count; None for a derived (`other`) cell


class AssetCompositionRow(TypedDict, total=False):
    """One type in the subtype tree. `viewer` / `repository` are present for each requested scope."""
    type_name: str
    parent: Optional[str]      # None for the root row
    level: int                 # 0 = root, 1 = its direct subtypes, ...
    exact_type: bool           # True on an `other` row: elements typed as exactly `parent`
    subtypes_error: Optional[str]  # set when this type's subtypes could not be read
    viewer: CompositionCell
    repository: CompositionCell
    not_visible: Dict[str, Any]  # {value, state, reason}: repository - viewer


class AssetComposition(TypedDict, total=False):
    """asset_composition()'s result: the rows plus the envelope executors read."""
    state: str                 # measured | nothing_found | not_established
    state_reason: str          # lists the cells that were not measured
    root: str
    depth: int
    scopes: List[str]
    as_of: str
    concurrency: int
    rows: List[AssetCompositionRow]
    not_measured: List[str]    # "<type_name>/<population>" for each failed count
    provenance: Dict[str, Any]  # pyegeria version, platform, server, run time, elapsed


def _typedef_names(result, parent: str) -> List[str]:
    """Direct subtype names from a get_sub_types result. A null/"no elements" result is
    no subtypes. A TypeDef whose superType names another type is skipped, in case a
    server answers with every descendant rather than the direct children."""
    if isinstance(result, dict):
        result = result.get("typeDefs", result.get("typeDefList"))
    if not isinstance(result, list):
        return []
    names = []
    for td in result:
        if not isinstance(td, dict) or not td.get("name"):
            continue
        sup = td.get("superType")
        sup_name = sup.get("name") if isinstance(sup, dict) else None
        if sup_name and sup_name != parent:
            continue
        names.append(td["name"])
    return sorted(set(names))


def asset_subtype_tree(vm, root: str = "Asset", depth: int = 2) -> List[Dict[str, Any]]:
    """
    The subtype tree under `root` to `depth`, breadth-first, from
    `ValidMetadataManager.get_sub_types` (one call per expanded node).

    Rows: {type_name, parent, level, exact_type, subtypes_error}. The root is level 0;
    its direct subtypes are level 1. After the children of each parent comes one
    `other` row (type_name = parent, level = the children's level, exact_type=True)
    for elements typed as exactly the parent -- an "other" row shows rather than hides.

    A null result is "no subtypes", not an error. A call that raises sets the node's
    `subtypes_error` (its children are unknown, so it gets no `other` row) and the
    walk carries on.
    """
    if depth < 0:
        raise ValueError(f"depth must be >= 0; got {depth!r}")
    rows: List[Dict[str, Any]] = [
        {"type_name": root, "parent": None, "level": 0, "exact_type": False, "subtypes_error": None}]
    frontier = [rows[0]]
    for level in range(1, depth + 1):
        next_frontier = []
        for node in frontier:
            try:
                children = _typedef_names(vm.get_sub_types(node["type_name"]), node["type_name"])
            except Exception as exc:  # noqa: BLE001 -- recorded on the row, never a silent leaf
                node["subtypes_error"] = f"subtypes of {node['type_name']} could not be read: {exc}"
                logger.warning(f"overview_metrics asset_subtype_tree: {node['subtypes_error']}")
                continue
            if not children:
                continue
            for name in children:
                row = {"type_name": name, "parent": node["type_name"], "level": level,
                       "exact_type": False, "subtypes_error": None}
                rows.append(row)
                next_frontier.append(row)
            rows.append({"type_name": node["type_name"], "parent": node["type_name"], "level": level,
                         "exact_type": True, "subtypes_error": None})
        frontier = next_frontier
    return rows


def _pyegeria_version() -> str:
    try:
        from importlib.metadata import version
        return version("pyegeria")
    except Exception:  # noqa: BLE001
        return "unknown"


def _count_cell(mgr, type_name: str, as_of: Optional[str], scope: str, stamp: str) -> Dict[str, Any]:
    """One strict count, as a cell. A 0 is nothing_found; None or an exception is not_measured."""
    started = time.monotonic()
    reason = ""
    try:
        with recording_unmeasured() as notes:
            value = count_elements(mgr, type_name, as_of, strict=True, **_pop(scope))
        if value is None:
            reason = (f"the {scope} count of {type_name} could not be measured: "
                      + ("; ".join(n["reason"] for n in notes) if notes
                         else "query failed, native count unavailable, or the fallback hit its cap"))
    except Exception as exc:  # noqa: BLE001 -- the exception's words become the reason
        value = None
        reason = f"the {scope} count of {type_name} failed: {exc}"
    elapsed = round(time.monotonic() - started, 3)
    if value is None:
        state = CELL_NOT_MEASURED
    else:
        state = CELL_MEASURED if value > 0 else CELL_NOTHING_FOUND
    return {"value": value, "state": state,
            "completeness": _COMPLETENESS[scope] if state in _ESTABLISHED else "unknown",
            "as_of": stamp, POPULATION_WORD: scope, "reason": reason, "elapsed_s": elapsed}


def _derived_cell(value: Optional[int], reason: str, scope: str, stamp: str) -> Dict[str, Any]:
    if value is None:
        state = CELL_NOT_MEASURED
    else:
        state = CELL_MEASURED if value > 0 else CELL_NOTHING_FOUND
    return {"value": value, "state": state,
            "completeness": _COMPLETENESS[scope] if state in _ESTABLISHED else "unknown",
            "as_of": stamp, POPULATION_WORD: scope, "reason": reason, "elapsed_s": None}


def _other_cell(parent_cell: Optional[Dict[str, Any]], child_cells: List[Dict[str, Any]],
                scope: str, stamp: str) -> Dict[str, Any]:
    """parent - sum(children), only when the parent and every child are established."""
    if parent_cell is None or parent_cell["state"] not in _ESTABLISHED:
        return _derived_cell(None, "the parent count is missing", scope, stamp)
    if any(c["state"] not in _ESTABLISHED for c in child_cells):
        return _derived_cell(None, "a child count is missing", scope, stamp)
    rest = parent_cell["value"] - sum(c["value"] for c in child_cells)
    if rest < 0:
        return _derived_cell(None, "the children's counts exceed the parent's "
                                   "(counts taken at different moments)", scope, stamp)
    return _derived_cell(rest, "", scope, stamp)


def _not_visible(row: Dict[str, Any]) -> Dict[str, Any]:
    """repository - viewer, only when both cells are established."""
    viewer, repo = row.get(SCOPE_VIEWER), row.get(SCOPE_REPOSITORY)
    if viewer is None or repo is None:
        return {"value": None, "state": CELL_NOT_MEASURED, "reason": "needs both scopes"}
    if viewer["state"] not in _ESTABLISHED or repo["state"] not in _ESTABLISHED:
        return {"value": None, "state": CELL_NOT_MEASURED, "reason": "needs both scopes measured"}
    diff = repo["value"] - viewer["value"]
    if diff < 0:
        return {"value": None, "state": CELL_NOT_MEASURED,
                "reason": "the viewer count exceeds the repository count (counts taken at different moments)"}
    return {"value": diff, "state": CELL_MEASURED if diff > 0 else CELL_NOTHING_FOUND, "reason": ""}


def asset_composition(
    mgr,
    vm=None,
    root: str = "Asset",
    depth: int = 2,
    as_of: Optional[str] = None,
    scopes: Optional[Sequence[str]] = None,
    concurrency: int = COMPOSITION_DEFAULT_CONCURRENCY,
    strict: bool = True,
    *,
    populations: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """
    The composition of `root` by subtype: one row per type in the subtype tree to
    `depth`, each counted in every requested scope, with an `other` row per parent
    and `not_visible` = repository - viewer.

    Stages, in the reporting model's §10.8 words (one opaque routine today; step
    (a'') can split it along these lines): a `typedefs` producer
    (asset_subtype_tree), two per-row `derive`s (the viewer count and the
    repository count, via count_elements(..., strict=True, scope=...)), and a
    `difference` (not_visible per row; each `other` row = parent - sum(children),
    only when every child count is established in that scope).

    Every count, in both scopes, goes through ONE ThreadPoolExecutor of
    `concurrency` workers, so `concurrency` is the real number of counts in flight
    against Egeria. The default is 3; above COMPOSITION_MAX_CONCURRENCY (5) it is
    lowered to 5, because Egeria's database pool is 10 connections and one sheet
    must not starve other users.

    Cells (see CompositionCell): `value`, `state` (a 0 is nothing_found; a failed
    count is not_measured with the failure's words in `reason`, never 0),
    `completeness` (repository "complete", viewer "unknown"), `as_of`,
    `population` ("viewer" | "repository"), `reason`, `elapsed_s` (a viewer
    `Process` count can take minutes; the page can say which cell was slow).

    Parameters
    ----------
    mgr : MetadataExpert (or EgeriaTech) -- counts elements
    vm : ValidMetadataManager -- reads the subtype tree. None (the default) uses
        `mgr`, which works when mgr is an EgeriaTech; the report-spec executor binds
        only clients named mgr/ce/expert/client, so it relies on this default.
    root : the type whose subtypes are counted
    depth : how many subtype levels below root (0 = root only)
    as_of : ISO-8601 asOfTime for point-in-time counts (None = now). The subtype
        tree is always today's.
    populations : any of "viewer", "repository" -- the populations to count; each cell
        names its population under `population`. `scopes=` is a deprecated alias.
    concurrency : counts in flight at once, 1..5 (default 3)
    strict : must be True -- the routine never turns a failure into a 0

    Returns
    -------
    AssetComposition -- {state, state_reason, root, depth, scopes, as_of,
    concurrency, rows, not_measured, provenance}. `state` is measured when any
    cell is measured, nothing_found when every established cell is 0, else
    not_established.
    """
    if not strict:
        raise ValueError("asset_composition always counts strictly: a failed count is not_measured, never 0")
    if scopes is not None:
        if populations is not None and list(populations) != list(scopes):
            raise ValueError("asset_composition: populations= and scopes= disagree; pass populations= only")
        if populations is None:
            warnings.warn("asset_composition(scopes=...) is deprecated; use populations=",
                          DeprecationWarning, stacklevel=2)
            populations = scopes
    if populations is None:
        populations = (SCOPE_VIEWER, SCOPE_REPOSITORY)
    scopes = populations
    wanted: List[str] = []
    for s in scopes:
        _push_down(s)  # ValueError for an unknown scope
        if s is None:
            raise ValueError("scopes must name 'viewer' and/or 'repository'")
        if s not in wanted:
            wanted.append(s)
    if not wanted:
        raise ValueError("scopes must name 'viewer' and/or 'repository'")
    if not isinstance(concurrency, int) or concurrency < 1:
        raise ValueError(f"concurrency must be a positive int; got {concurrency!r}")
    if concurrency > COMPOSITION_MAX_CONCURRENCY:
        logger.warning(f"overview_metrics asset_composition: concurrency {concurrency} lowered to the cap "
                       f"{COMPOSITION_MAX_CONCURRENCY} (Egeria's database pool is 10 connections)")
        concurrency = COMPOSITION_MAX_CONCURRENCY

    from datetime import datetime, timezone
    run_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    stamp = as_of or run_at
    started = time.monotonic()

    rows = asset_subtype_tree(mgr if vm is None else vm, root=root, depth=depth)

    # Each distinct type is counted once per scope; an `other` row reuses its parent's count.
    type_names: List[str] = []
    for row in rows:
        if not row["exact_type"] and row["type_name"] not in type_names:
            type_names.append(row["type_name"])
    cells: Dict[Tuple[str, str], Dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=concurrency, thread_name_prefix="asset-composition") as pool:
        futures = {pool.submit(_count_cell, mgr, t, as_of, s, stamp): (t, s)
                   for s in wanted for t in type_names}
        for fut in as_completed(futures):
            cells[futures[fut]] = fut.result()

    for row in rows:
        if row["exact_type"]:
            continue
        for s in wanted:
            row[s] = dict(cells[(row["type_name"], s)])
    for row in rows:
        if not row["exact_type"]:
            continue
        parent = row["type_name"]
        parent_row = next(r for r in rows if r["type_name"] == parent and not r["exact_type"])
        children = [r for r in rows if r["parent"] == parent and not r["exact_type"]]
        for s in wanted:
            row[s] = _other_cell(parent_row.get(s), [c[s] for c in children], s, stamp)
    for row in rows:
        row["not_visible"] = _not_visible(row)

    all_cells = [row[s] for row in rows for s in wanted]
    failed = [f"{t}/{s}" for s in wanted for t in type_names if cells[(t, s)]["state"] == CELL_NOT_MEASURED]
    tree_errors = [r["subtypes_error"] for r in rows if r["subtypes_error"]]
    if any(c["state"] == CELL_MEASURED for c in all_cells):
        state = "measured"
    elif any(c["state"] == CELL_NOTHING_FOUND for c in all_cells):
        state = "nothing_found"
    else:
        state = "not_established"
    reasons = []
    if failed:
        reasons.append("not measured: " + ", ".join(failed))
    reasons.extend(tree_errors)

    return {
        "state": state,
        "state_reason": "; ".join(reasons),
        "root": root,
        "depth": depth,
        "populations": wanted,
        "scopes": wanted,  # deprecated key, same value as "populations"
        "as_of": stamp,
        "concurrency": concurrency,
        "rows": rows,
        "not_measured": failed,
        "provenance": {
            "pyegeria_version": _pyegeria_version(),
            "platform": getattr(mgr, "platform_url", None),
            "server": getattr(mgr, "view_server", None),
            "run_at": run_at,
            "as_of_requested": as_of,
            "elapsed_s": round(time.monotonic() - started, 3),
        },
    }
