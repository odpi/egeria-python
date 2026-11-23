"""One pager for Egeria find/get calls: an empty page is not the end, and on some paths neither is null.

Egeria's paging contract (finding-metadata/overview, "Paging", restated by the Egeria lead on 2026-11-13):
page with ``startFrom`` += ``pageSize`` until the server returns *null* (the ``elements`` key absent). An
*empty list* means server-side filtering (security, zones, Memento/lineage) removed every row of that page,
so the caller carries on. ``startFrom`` is an offset into the repository's rows *before* filtering, so the
pager always advances by the page size it asked for, never by the number of rows it got back.

On some paths Egeria also sends null for a page that filtering emptied (metadata-expert by-search-conditions:
raw capture 2026-11-13, ``~/.re-gate/B5-RAW-CAPTURE-2026-11-13.md``; MetadataElementHandler returns null for
an empty filtered list). There, null is not proof of the end. A call site says which kind of path it pages
with ``end_policy``:

- ``"trusted"``: null is the end (``end="confirmed"``).
- ``"suspect"`` (the default): on null, probe the next ``probe_pages`` pages. Rows there mean the null was a
  filtered page and paging resumes; nothing there ends the read with ``end="not_confirmed"``.

The result says how the read ended, so a caller never shows "nothing" or a total it didn't establish:

- ``confirmed``: the server said there is no more, on a path where that can be trusted.
- ``not_confirmed``: the read stopped without proof of the end (a suspect null and empty probes, or too
  many consecutive filtered positions).
- ``capped``: the caller's limits stopped it (``want`` rows collected, or ``max_pages``); there may be more.
- ``stalled``: a page brought only rows already read (a server ignoring ``startFrom``); stopped so it
  can't loop forever.
- ``first_page``: one page was read and not paged on (a caller's choice, e.g. a report run whose first
  page had rows). Set by callers, never by ``page_all``.

Anything but ``confirmed`` is "at least N" (``PageResult.count_text``), never a total.

``fetch(start, size)`` returns a list (rows; ``[]`` for a filtered page) or anything else (None, pyegeria's
"No elements found" string) for null. When ``fetch`` is a pyegeria list method, the pager reads what Egeria
actually sent from the method's list-request record, so a method that collapses ``[]`` into "No elements
found" still reads as a filtered page (``_end_signal``). Exceptions from ``fetch`` propagate: the caller decides what a failed
read means. This module only pages; it changes nothing about what pyegeria's public methods return.
"""
from __future__ import annotations

import json
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from typing import Any, Awaitable, Callable, Hashable, List, Optional, Tuple

DEFAULT_FETCH_PAGE_SIZE = 100   # rows asked for per request; below the server's maximum page size
DEFAULT_PROBE_PAGES = 3         # extra pages read after a null on a suspect path
DEFAULT_MAX_EMPTY_ROWS = 2000   # consecutive filtered positions before giving up (rows, not pages)
DEFAULT_MAX_PAGES = 1000        # requests per read, probes included

END_POLICIES = ("trusted", "suspect")
ENDS = ("confirmed", "not_confirmed", "capped", "stalled", "first_page")
#: Why a read ended (PageResult.end_reason). Only the first two may be acted on as the end (reached_end).
END_REASONS = ("trusted_null", "null_then_empty_probes", "empty_run_cap", "want", "max_pages", "stalled")

#: Methods whose null has been shown to mean the end (a filtered page comes back as []), with the evidence.
#: Everything else pages as "suspect". Add a method only with a raw capture like the one cited.
TRUSTED_END_METHODS = {
    # content-status search: [] for 11 filtered pages, then 79 + 7 rows, then null (Architect, laz, 2026-11-13)
    "find_authored_elements",
}


#: Methods proven to send null MID-SET (rows follow a null; a filtered-empty page is null, never []), so even a
#: null followed by empty probes is NOT an end on them: PageResult.reached_end is False, as for a limit, and no
#: write path may act on a read from them. Evidence: ~/.re-gate/CAPTURE-PAGER-STEP4-FINDINGS-2026-11-14.md
#: (laz, read-only, 2026-11-14): at pageSize 25, runs of up to 3 nulls mid-set on both, and no [] in 457
#: requests. Promotion to TRUSTED_END_METHODS is closed for these until Egeria returns [] for a filtered page
#: (the Architect's ruling after the step 4 capture).
#: The by-property-value reads joined on the exists-lookups ruling (2026-11-14): classification-explorer
#: by-property-value is StewardshipManagementHandler -> OpenMetadataClient.getMetadataElementsByPropertyValue,
#: which is findMetadataElements(...getSearchPropertiesByName...): the server method the capture caught.
#: Promotion of any of these is gated on an Egeria build with odpi/egeria #9453 and a post-rebuild capture.
#: The by-name reads joined on the MyEgeria read-back (R3, 2026-11-14), traced read-only in Egeria 2a27dad5:
#: CollectionManager / CommunityMatters / FeedbackManager ".../by-name" REST -> CollectionHandler.getCollectionsByName
#: / CommunityHandler.getCommunitiesByName / NoteLogHandler.getNoteLogsByName -> OpenMetadataHandlerBase
#: .getRootElementsByName -> openMetadataClient.findMetadataElements(...getSearchPropertiesByName...): the same server
#: method as find_metadata_elements. (Their search-string twins go findRootElements -> findMetadataElementsWithString
#: -> OMF findElements -> handler.findEntities, and attached/member reads go getRelatedRootElements ->
#: getRelatedMetadataElements; those stay plain suspect.)
BY_NAME_METHODS = frozenset({"get_collections_by_name", "_async_get_collections_by_name",
                             "get_communities_by_name", "_async_get_communities_by_name",
                             "get_note_logs_by_name", "_async_get_note_logs_by_name"})
#: get_elements (classification-explorer elements/by-type) -> ClassificationExplorerRESTServices.getRootElementsByType
#: -> StewardshipManagementHandler.getRootElementsByType -> openMetadataClient.findMetadataElements: the same server
#: method again (traced 2026-11-14 for P3 used_by, the Architect's ruling (c)), so NULL_NOT_END and gated like it.
BY_TYPE_METHODS = frozenset({"get_elements", "_async_get_elements"})
NULL_NOT_END_METHODS = frozenset({"find_metadata_elements", "get_relationships",
                                  "get_elements_by_property_value", "find_elements_by_property_value",
                                  "_async_get_elements_by_property_value"}) | BY_NAME_METHODS | BY_TYPE_METHODS

#: Probe pages after a null on a NULL_NOT_END method: the capture's longest null run was 3; 6 gives 2x headroom.
NULL_NOT_END_PROBE_PAGES = 6

assert not (TRUSTED_END_METHODS & NULL_NOT_END_METHODS), "a NULL_NOT_END method can't be trusted"


def end_policy_for(method_name: Optional[str]) -> str:
    """"trusted" for a method in TRUSTED_END_METHODS (never one in NULL_NOT_END_METHODS), else "suspect"."""
    if method_name in NULL_NOT_END_METHODS:
        return "suspect"
    return "trusted" if method_name in TRUSTED_END_METHODS else "suspect"


# ── Step 6: the per-fix version gate (#9453, the Architect's step 6 ruling, 2026-11-14; #9454, G2, 2026-11-15) ──
# Each upstream paging fix makes some reads send [] for a filtered page and null only at the end. A read is promoted
# to trusted only on a platform whose /api/about shows every fix it needs (METHOD_NEEDS); anything else keeps the
# NULL_NOT_END paging (6 probes, never reached_end).
# - #9453 (2a27dad5, merged 2026-11-14T19:52Z) fixed the find paths: find_metadata_elements, by-property-value,
#   by-name and by-type (post-#9453 capture on laz, 5deda38d:
#   ~/.re-gate/RESULTS-EGERIA-UPGRADE-5deda38d-AND-POST-9453-CAPTURE-2026-11-14.md).
# - #9454 (970092b9) fixed get_relationships and get_related_elements (G1 capture on laz a5c3a195, main c61bad65:
#   ~/.re-gate/CAPTURE-G1-9454-2026-11-15/, read back PASS in READBACK-G1-9454-CAPTURE-AND-G2-BRIEF-2026-11-15.md).
#   get_related_elements' metadata_element_type-filtered form is the same endpoint with a body filter, so it rides
#   along; if a later capture shows a mid-set null there, it comes back out.

FIX_9453 = "9453"
FIX_9454 = "9454"

#: The upstream paging fixes the gate knows. For each:
#: - snapshot_cutoff: a "6.3-SNAPSHOT" built at or after it carries the fix;
#: - release_floor: the first release (major, minor, patch) that carries it, or None: no release is promoted;
#: - later_snapshots: whether every SNAPSHOT of a later line (6.4-SNAPSHOT, ...) carries it.
FIXES = {
    FIX_9453: {"snapshot_cutoff": "2026-11-14T19:52:00Z",   # the #9453 merge
               "release_floor": (6, 3, 0),                  # 2a27dad5 is in the V6.3 tag (a81af02c), checked 2026-11-16
               "later_snapshots": True},                    # step 6 read-back R1
    FIX_9454: {"snapshot_cutoff": "2026-11-15T07:26:00Z",
               "release_floor": (6, 3, 0), # G3 passed 2026-11-16: 970092b9 is an ancestor of the V6.3 tag (a81af02c)
                                           # (GitHub compare 970092b9...V6.3 = "ahead"), so 6.3.0 carries #9454
               "later_snapshots": True},   # a5c3a195 (6.3-SNAPSHOT, built 08:29Z) carries 970092b9 (merged 07:26Z)
                                           # on main, so every later line's SNAPSHOT does too (G2 ruling 4)
}

#: The relationship reads #9454 fixed (G2 ruling, 2026-11-15). The async names are what report specs page under
#: (format_set_executor prefixes ``_async_``).
#: - get_relationships (OpenMetadataRelationshipList) was caught sending null mid-set (the 11-14 capture and G1's
#:   pre-#9454 runs): NULL_NOT_END without #9454. _async_get_relationships is the same server call, so it joins.
#: - get_related_elements (getRelatedMetadataElements, another list class) was never shown sending a mid-set null:
#:   its filtered page is [] (MyEgeria R3 Java check), and G1 shows [] and a clean end. It stays plain suspect
#:   without #9454 (today's behaviour), and is trusted with it.
RELATIONSHIP_NULL_NOT_END_METHODS = frozenset({"get_relationships", "_async_get_relationships"})
RELATED_ELEMENTS_METHODS = frozenset({"get_related_elements", "_async_get_related_elements"})
RELATIONSHIP_METHODS = RELATIONSHIP_NULL_NOT_END_METHODS | RELATED_ELEMENTS_METHODS
NULL_NOT_END_METHODS = NULL_NOT_END_METHODS | RELATIONSHIP_NULL_NOT_END_METHODS
assert not (TRUSTED_END_METHODS & NULL_NOT_END_METHODS), "a NULL_NOT_END method can't be trusted"

#: The fixes each gated method needs before it is trusted. Every other method is never promoted.
METHOD_NEEDS = {
    **{m: frozenset({FIX_9453}) for m in ({"find_metadata_elements", "get_elements_by_property_value",
                                          "find_elements_by_property_value", "_async_get_elements_by_property_value"}
                                         | BY_NAME_METHODS | BY_TYPE_METHODS)},   # findMetadataElements underneath
    **{m: frozenset({FIX_9454}) for m in RELATIONSHIP_METHODS},
}
#: Promoted to trusted on a platform carrying the fixes they need (METHOD_NEEDS) only.
GATED_TRUSTED_METHODS = frozenset(METHOD_NEEDS)
assert GATED_TRUSTED_METHODS <= NULL_NOT_END_METHODS | RELATED_ELEMENTS_METHODS
assert not (GATED_TRUSTED_METHODS & TRUSTED_END_METHODS)
assert all(needs <= set(FIXES) for needs in METHOD_NEEDS.values())

GATE_SNAPSHOT_VERSION = "6.3-SNAPSHOT"
GATE_SNAPSHOT_TIME = FIXES[FIX_9453]["snapshot_cutoff"]   # back-compatible name: the #9453 cutoff
GATE_TTL_SECONDS = 3600          # a parsed /api/about answer
GATE_FAILED_TTL_SECONDS = 60     # a failed about-read: retried soon, so a platform restart doesn't turn trust off
GATE_ABOUT_TIMEOUT_SECONDS = 5   # the about-read's own timeout, where the client takes one
GATE_OVERRIDE_ENV = "PYEGERIA_TRUSTED_END"   # "off" turns every fix off everywhere; there is no "force on"

NO_FIXES: frozenset = frozenset()

_GATE_CACHE: dict = {}   # platform URL -> (expires at, frozenset of the fixes it carries)


def _fix_in(fix: dict, numbers: Tuple[int, int, int], snapshot: bool, built: Any) -> bool:
    from datetime import datetime
    if not snapshot:
        floor = fix.get("release_floor")
        return floor is not None and numbers >= tuple(floor)
    if numbers[:2] > (6, 3):
        return bool(fix.get("later_snapshots"))
    if numbers[:2] < (6, 3) or not built:
        return False
    when = datetime.fromisoformat(str(built).replace("Z", "+00:00"))
    cutoff = datetime.fromisoformat(str(fix["snapshot_cutoff"]).replace("Z", "+00:00"))
    return when.tzinfo is not None and when >= cutoff


def fixes_from_about(about: Any) -> frozenset:
    """The paging fixes (FIXES keys) a platform's /api/about answer shows. Fail-safe: anything not clearly
    carrying a fix (an older version or build time, unparsable, no time) leaves it out, so doubt is NO_FIXES.

    - a release carries a fix from its release_floor on; a fix with no floor is carried by no release;
    - "6.3-SNAPSHOT" carries a fix when built at or after its snapshot_cutoff;
    - a SNAPSHOT of a later line (6.4-SNAPSHOT) carries the fixes marked later_snapshots; an earlier one, none;
    - known limit: a 6.3-SNAPSHOT built after a cutoff from code without that fix reads as carrying it
      (PYEGERIA_TRUSTED_END=off covers it)."""
    import re
    try:
        if isinstance(about, (str, bytes)):
            about = json.loads(about)
        if not isinstance(about, dict):
            return NO_FIXES
        version = str(about.get("version") or "").strip()
        m = re.fullmatch(r"(\d+)\.(\d+)(?:\.(\d+))?(-SNAPSHOT)?", version)
        if not m:
            return NO_FIXES
        numbers = tuple(int(g or 0) for g in m.groups()[:3])
        snapshot = bool(m.group(4))
        if snapshot and numbers[:2] == (6, 3) and version != GATE_SNAPSHOT_VERSION:
            return NO_FIXES   # e.g. "6.3.1-SNAPSHOT": not the main-line SNAPSHOT the cutoffs are measured on
        built = about.get("time")
        return frozenset(name for name, fix in FIXES.items() if _fix_in(fix, numbers, snapshot, built))
    except Exception:  # noqa: BLE001 -- fail safe: never trusted on unknown
        return NO_FIXES


def gate_from_about(about: Any) -> bool:
    """Whether a platform's /api/about answer shows the #9453 paging fix (back-compatible alias:
    ``FIX_9453 in fixes_from_about(about)``)."""
    return FIX_9453 in fixes_from_about(about)


def _gate_overridden() -> bool:
    import os
    return os.environ.get(GATE_OVERRIDE_ENV, "").strip().lower() == "off"


def _gate_cached(platform_url: str) -> Optional[frozenset]:
    import time
    hit = _GATE_CACHE.get(platform_url)
    if hit is not None and hit[0] > time.monotonic():
        return hit[1]
    return None


def _gate_store(platform_url: str, fixes: frozenset, failed: bool = False) -> frozenset:
    import time
    ttl = GATE_FAILED_TTL_SECONDS if failed else GATE_TTL_SECONDS
    _GATE_CACHE[platform_url] = (time.monotonic() + ttl, fixes)
    return fixes


def _about_reader(client: Any, name: str):
    """The client's own platform-origin reader (``name``), or a subclient's (EgeriaTech proxies), or None."""
    reader = getattr(type(client), name, None) and getattr(client, name, None)
    if reader is None:
        for sub in ("classification_manager", "metadata_expert"):
            inner = getattr(client, sub, None)
            reader = getattr(inner, name, None) if inner is not None else None
            if reader is not None:
                break
    return reader


def _call_about(reader: Callable[[], Any]) -> Any:
    """The sync about-read, bounded by GATE_ABOUT_TIMEOUT_SECONDS (on a worker thread, which is abandoned if
    it overruns: the read is only ever "not promoted" then)."""
    from concurrent.futures import ThreadPoolExecutor
    pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="pyegeria-about")
    try:
        return pool.submit(_read_and_close, reader).result(timeout=GATE_ABOUT_TIMEOUT_SECONDS)
    finally:
        pool.shutdown(wait=False)


def _read_and_close(reader: Callable[[], Any]) -> Any:
    """Run the about-read on this worker thread, then close what the read opened here: the client's
    thread-local session and this thread's run_sync loop (step 6 gate read-back advisory: one was left unclosed
    per platform per TTL)."""
    try:
        return reader()
    finally:
        _close_thread_resources(getattr(reader, "__self__", None))


def _close_thread_resources(owner: Any) -> None:
    from pyegeria.core import async_runner
    try:
        local = getattr(owner, "_thread_local", None)
        session = getattr(local, "session", None) if local is not None else None
        loop = getattr(async_runner._thread_state, "loop", None)
        if session is not None and loop is not None and not loop.is_closed():
            loop.run_until_complete(session.aclose())
        if local is not None:
            for name in ("session", "session_loop"):
                if hasattr(local, name):
                    delattr(local, name)
        if loop is not None and not loop.is_closed():
            loop.close()
    except Exception:  # noqa: BLE001 -- cleanup only: never turns a read into an error
        pass


def platform_fixes(client: Any) -> frozenset:
    """The paging fixes `client`'s platform carries: one best-effort /api/about read per platform URL per
    GATE_TTL_SECONDS, shared by every fix. Never raises, never blocks a read: a failed or unparsable read, no
    client, or PYEGERIA_TRUSTED_END=off is NO_FIXES."""
    if client is None or _gate_overridden():
        return NO_FIXES
    url = getattr(client, "platform_url", None)
    if not isinstance(url, str) or not url:
        return NO_FIXES
    if (cached := _gate_cached(url)) is not None:
        return cached
    try:
        reader = _about_reader(client, "get_platform_origin")
        about = _call_about(reader) if reader is not None else None
    except Exception:  # noqa: BLE001 -- a failed about-read only means "no fixes"
        about = None
    return _gate_store(url, fixes_from_about(about), failed=not about)


async def async_platform_fixes(client: Any) -> frozenset:
    """``platform_fixes`` for async code (the same cache)."""
    if client is None or _gate_overridden():
        return NO_FIXES
    url = getattr(client, "platform_url", None)
    if not isinstance(url, str) or not url:
        return NO_FIXES
    if (cached := _gate_cached(url)) is not None:
        return cached
    try:
        reader = _about_reader(client, "async_get_platform_origin")
        about = None
        if reader is not None:
            import asyncio
            about = await asyncio.wait_for(reader(), timeout=GATE_ABOUT_TIMEOUT_SECONDS)
    except Exception:  # noqa: BLE001 -- a failed or slow about-read only means "no fixes"
        about = None
    return _gate_store(url, fixes_from_about(about), failed=not about)


def platform_promoted(client: Any) -> bool:
    """Whether `client`'s platform carries the #9453 fix (back-compatible alias: ``FIX_9453 in platform_fixes``)."""
    return FIX_9453 in platform_fixes(client)


async def async_platform_promoted(client: Any) -> bool:
    """``platform_promoted`` for async code (the same cache)."""
    return FIX_9453 in await async_platform_fixes(client)


def _paging(method_name: Optional[str], promoted: bool) -> dict:
    """page_all keywords for a method; ``promoted`` means the platform carries every fix the method needs."""
    if promoted and method_name in GATED_TRUSTED_METHODS:
        return {"end_policy": "trusted"}
    if method_name in NULL_NOT_END_METHODS:
        return {"end_policy": "suspect", "probe_pages": NULL_NOT_END_PROBE_PAGES, "null_not_end": True}
    return {"end_policy": end_policy_for(method_name)}


def _needs_met(method_name: Optional[str], fixes: frozenset) -> bool:
    needs = METHOD_NEEDS.get(method_name)
    return needs is not None and needs <= fixes


# What the old ``"get_relationships" not in GATED_TRUSTED_METHODS`` assert stood for: on a platform without #9454,
# get_relationships stays NULL_NOT_END (the long probe, never reached_end), whatever else it carries; and
# get_related_elements stays plain suspect there (G2 ruling 1).
_WITHOUT_9454 = frozenset(FIXES) - {FIX_9454}
assert all(_paging(m, _needs_met(m, _WITHOUT_9454)).get("null_not_end") is True
           for m in RELATIONSHIP_NULL_NOT_END_METHODS)
assert all(_paging(m, _needs_met(m, _WITHOUT_9454)) == {"end_policy": "suspect"} for m in RELATED_ELEMENTS_METHODS)


def paging_for(method_name: Optional[str], client: Any = None) -> dict:
    """page_all keyword arguments for a method: its end_policy and, for a NULL_NOT_END method, the longer
    probe and ``null_not_end`` (so a null-then-empty-probes read is never ``reached_end``).

    Given the ``client`` that makes the read, a GATED_TRUSTED_METHODS method is trusted on a platform that carries
    every fix it needs (METHOD_NEEDS, ``platform_fixes``). The platform is only asked when the method is gated."""
    promoted = method_name in GATED_TRUSTED_METHODS and _needs_met(method_name, platform_fixes(client))
    return _paging(method_name, promoted)


async def async_paging_for(method_name: Optional[str], client: Any = None) -> dict:
    """``paging_for`` for async code: the platform's /api/about is read without blocking the event loop."""
    promoted = method_name in GATED_TRUSTED_METHODS and _needs_met(method_name, await async_platform_fixes(client))
    return _paging(method_name, promoted)


@dataclass(frozen=True)
class PageResult:
    """What a paged read found and how it ended. ``items`` is cut to ``want`` when one was given."""
    items: List[Any]
    end: str
    note: Optional[str] = None
    pages_read: int = 0
    positions_read: int = 0   # how far into the server's (pre-filter) rows the read got
    end_reason: Optional[str] = None   # why it ended: one of END_REASONS (None only for a caller-built result)
    null_not_end: bool = False         # read from a NULL_NOT_END method: a null is never the end

    @property
    def complete(self) -> bool:
        """True only when the server confirmed there is nothing more."""
        return self.end == "confirmed"

    @property
    def reached_end(self) -> bool:
        """True when the read may be acted on as the end (step-4 ruling (A)): a trusted null, or a suspect
        null whose probes found nothing. ``complete`` is stricter: only it allows a total or "none" to be
        shown. A limit (capped, stalled, the empty-run cap) is never the end."""
        if self.end_reason == "null_then_empty_probes" and self.null_not_end:
            return False   # NULL_NOT_END_METHODS: rows have followed a null on this method
        return self.end_reason in ("trusted_null", "null_then_empty_probes")

    def trace(self) -> dict:
        """How the read ended, for a log line or a run result: positions_read, end, end_reason."""
        return {"positions_read": self.positions_read, "end": self.end, "end_reason": self.end_reason}

    def count_text(self) -> str:
        """The count as it may be shown: "N" when complete, else "at least N"."""
        n = len(self.items)
        return str(n) if self.complete else f"at least {n}"


_GUID_FIELDS = ("guid", "elementGUID", "relationshipGUID")


def default_key(item: Any) -> Hashable:
    """A row's GUID, whichever shape it comes in:

    - an Egeria 6 element or relationship: ``elementHeader.guid`` / ``relationshipHeader.guid``;
    - the metadata-expert shape (``OpenMetadataElement``, ``OpenMetadataRelationship``): ``elementGUID`` /
      ``relationshipGUID`` on the row itself;
    - a bare ``guid`` on the row.

    A row with none of these is keyed by its content (equal JSON, equal key), never by object identity:
    every page is decoded afresh, so the same row read twice is two different objects."""
    if isinstance(item, dict):
        for holder in (item.get("elementHeader"), item.get("relationshipHeader"), item):
            if isinstance(holder, dict):
                for name in _GUID_FIELDS:
                    if isinstance(holder.get(name), str) and holder[name]:
                        return holder[name]
    try:
        return "content:" + json.dumps(item, sort_keys=True, default=str)
    except (TypeError, ValueError):   # a circular or otherwise undumpable row: identity is all there is
        return id(item)


@dataclass
class _Pager:
    """The paging state machine, shared by the sync and async drivers. ``request()`` gives the next
    (start, size) to fetch or None when done; ``feed(page)`` takes what that fetch returned."""
    want: Optional[int]
    size: int
    policy: str
    probe_pages: int
    max_empty_rows: int
    max_pages: int
    key: Callable[[Any], Hashable]
    start: int = 0
    stall_pages: int = 1                # consecutive pages of only rows already read before "stalled"
    trim_to_want: bool = False          # ask for no more rows than `want` still needs (a preview's last page)
    asked: int = 0                      # the size of the request in flight
    no_new: int = 0
    last_keys: Optional[list] = None    # the previous page's row keys: the same page again is a stall
    pages: int = 0
    empty_rows: int = 0
    probes_left: Optional[int] = None   # None: not probing
    null_at: Optional[int] = None       # where the suspect null came back
    items: List[Any] = field(default_factory=list)
    seen: set = field(default_factory=set)
    result: Optional[PageResult] = None

    def request(self) -> Optional[Tuple[int, int]]:
        if self.result is not None:
            return None
        if self.pages >= self.max_pages:
            self._finish("capped", f"stopped after {self.pages} pages of {self.size}; there may be more",
                         "max_pages")
            return None
        self.asked = self.size
        if self.trim_to_want and self.want is not None:
            self.asked = max(1, min(self.size, self.want - len(self.items)))
        return self.start, self.asked

    def feed(self, page: Any) -> None:
        self.pages += 1
        at = self.start
        self.start += self.asked or self.size
        if not isinstance(page, list):
            self._null(at)
        elif not page:
            self._empty(at)
        else:
            self._rows(page, at)

    # ── one handler per kind of page ──

    def _null(self, at: int) -> None:
        if self.policy == "trusted":
            self._finish("confirmed", None, "trusted_null")
            return
        if self.probes_left is None:
            self.probes_left, self.null_at = self.probe_pages, at
        else:
            self.probes_left -= 1
        if self.probes_left <= 0:
            self._finish("not_confirmed",
                         f"Egeria reported no more at position {self.null_at}, and the next "
                         f"{self.probe_pages} pages of {self.size} were empty too; on this path a filtered page "
                         f"also reads as 'no more', so later matches can't be ruled out", "null_then_empty_probes")

    def _empty(self, at: int) -> None:
        self.probes_left = None   # an empty page means the server has rows here: not the end
        self.empty_rows += self.asked or self.size
        if self.empty_rows >= self.max_empty_rows:
            self._finish("not_confirmed",
                         f"{self.empty_rows} consecutive positions (up to {at + (self.asked or self.size)}) were filtered out "
                         f"for you; there may be more", "empty_run_cap")

    def _rows(self, page: list, at: int) -> None:
        self.probes_left = None
        self.empty_rows = 0
        fresh = []
        keys = []
        for item in page:
            k = self.key(item)
            keys.append(k)
            if k not in self.seen:
                self.seen.add(k)
                fresh.append(item)
        same_as_last, self.last_keys = keys == self.last_keys, keys
        if not fresh:
            self.no_new += 1
            # overlapping short pages (export_dcat) are not yet a stall; the very same page again always is
            if self.no_new < self.stall_pages and not same_as_last:
                return
            self._finish("stalled",
                         f"the read from position {at} returned only rows already read (the server may be "
                         f"ignoring startFrom), so it stopped at {len(self.items)}", "stalled")
            return
        self.no_new = 0
        self.items.extend(fresh)
        if self.want is not None and len(self.items) >= self.want:
            self._finish("capped", f"stopped at the {self.want} rows asked for; there may be more", "want")

    def _finish(self, end: str, note: Optional[str], reason: str) -> None:
        items = self.items[: self.want] if self.want is not None else self.items
        self.result = PageResult(items=list(items), end=end, note=note, pages_read=self.pages,
                                 positions_read=self.start, end_reason=reason)


def _pager(want, fetch_page_size, end_policy, probe_pages, max_empty_rows, max_pages, key,
           start_from=0, stall_pages=1, trim_to_want=False) -> _Pager:
    if end_policy not in END_POLICIES:
        raise ValueError(f"end_policy must be one of {END_POLICIES}, not {end_policy!r}")
    for name, value, low in (("fetch_page_size", fetch_page_size, 1), ("probe_pages", probe_pages, 1),
                             ("max_empty_rows", max_empty_rows, 1), ("max_pages", max_pages, 1),
                             ("stall_pages", stall_pages, 1)):
        if not isinstance(value, int) or isinstance(value, bool) or value < low:
            raise ValueError(f"{name} must be a whole number of at least {low}, not {value!r}")
    if want is not None and (not isinstance(want, int) or isinstance(want, bool) or want < 1):
        raise ValueError(f"want must be None or a whole number of at least 1, not {want!r}")
    if not isinstance(start_from, int) or isinstance(start_from, bool) or start_from < 0:
        raise ValueError(f"start_from must be a whole number of at least 0, not {start_from!r}")
    return _Pager(want=want, size=fetch_page_size, policy=end_policy, probe_pages=probe_pages,
                  max_empty_rows=max_empty_rows, max_pages=max_pages, key=key or default_key, start=start_from,
                  stall_pages=stall_pages, trim_to_want=trim_to_want)


@contextmanager
def _end_signal():
    """Record what Egeria actually sent for the list request ``fetch`` makes (pager step 2).

    pyegeria's list helpers note it in ``LIST_REQUEST_RECORD["page"]`` ("null", "empty" or "rows") before a
    method collapses ``[]`` into "No elements found", so the pager can tell a filtered page from the end
    without any public method changing what it returns. A caller already recording (``exec_report_spec``
    reads ``cap``) gets this request's facts merged into its own record afterwards, as if this block were
    not there: the record keeps the last list request, as it always has."""
    from pyegeria.core._server_client import LIST_REQUEST_RECORD, recording_list_requests
    outer = LIST_REQUEST_RECORD.get()
    with recording_list_requests() as record:
        yield record
    if outer is not None:
        outer.update(record)


def _signalled(page: Any, record: dict) -> Any:
    """``page`` as the pager should read it: ``[]`` when Egeria sent an empty list that the method collapsed,
    None when Egeria sent null. When no list helper recorded anything (a fetch that isn't a pyegeria list
    call, or a path not yet routed through the record), ``page`` is read as it is."""
    sent = record.get("page")
    if sent == "empty" and not (isinstance(page, list) and page):
        return []
    if sent == "null" and not isinstance(page, list):
        return None
    return page


def page_all(fetch: Callable[[int, int], Any], *, want: Optional[int] = None,
             fetch_page_size: int = DEFAULT_FETCH_PAGE_SIZE, end_policy: str = "suspect",
             probe_pages: int = DEFAULT_PROBE_PAGES, max_empty_rows: int = DEFAULT_MAX_EMPTY_ROWS,
             max_pages: int = DEFAULT_MAX_PAGES, key: Optional[Callable[[Any], Hashable]] = None,
             start_from: int = 0, stall_pages: int = 1, null_not_end: bool = False,
             trim_to_want: bool = False) -> PageResult:
    """Read every row ``fetch(start, size)`` gives (or the first ``want``), paging until the end is known
    or a limit stops it, starting at ``start_from``. See the module docstring for ``end_policy`` and the
    ``end`` states.

    ``key`` gives each row's identity, for dropping rows read twice and for the stall guard. The default
    (``default_key``) is the row's GUID in any of Egeria's shapes, else its JSON content. A caller paging
    rows that have no GUID and can legitimately repeat (aggregates, counts, value lists) must pass its own
    ``key``: under the content fallback two equal rows are one row, and a page of them reads as a stall.

    Each ``fetch`` runs inside ``_end_signal``, so a pyegeria list method that collapses ``[]`` into
    "No elements found" is still read as a filtered page, not as the end.

    ``stall_pages`` is how many pages in a row bringing only rows already read end the read as "stalled"
    (default 1; a path known to return overlapping short pages may allow 2).

    ``null_not_end`` (a NULL_NOT_END method: pass ``**paging_for(method)``) marks the result so that a null
    followed by empty probes is not ``reached_end``.

    ``trim_to_want`` (a preview) asks for no more rows than ``want`` still needs, so the last request is the
    remainder and no page is read past ``want``; a short or empty page still does not end the read."""
    pager = _pager(want, fetch_page_size, end_policy, probe_pages, max_empty_rows, max_pages, key, start_from,
                   stall_pages, trim_to_want)
    while (req := pager.request()) is not None:
        with _end_signal() as record:
            page = fetch(*req)
        pager.feed(_signalled(page, record))
    return replace(pager.result, null_not_end=True) if null_not_end else pager.result


async def async_page_all(fetch: Callable[[int, int], Awaitable[Any]], *, want: Optional[int] = None,
                         fetch_page_size: int = DEFAULT_FETCH_PAGE_SIZE, end_policy: str = "suspect",
                         probe_pages: int = DEFAULT_PROBE_PAGES, max_empty_rows: int = DEFAULT_MAX_EMPTY_ROWS,
                         max_pages: int = DEFAULT_MAX_PAGES,
                         key: Optional[Callable[[Any], Hashable]] = None, start_from: int = 0,
                         stall_pages: int = 1, null_not_end: bool = False,
                         trim_to_want: bool = False) -> PageResult:
    """``page_all`` for an async ``fetch`` (same ``key`` and end-signal rules)."""
    pager = _pager(want, fetch_page_size, end_policy, probe_pages, max_empty_rows, max_pages, key, start_from,
                   stall_pages, trim_to_want)
    while (req := pager.request()) is not None:
        with _end_signal() as record:
            page = await fetch(*req)
        pager.feed(_signalled(page, record))
    return replace(pager.result, null_not_end=True) if null_not_end else pager.result


# ── Step 4: what a loop says and logs about how its read ended (ruling (A), 2026-11-13) ──

def at_least_note(paged: PageResult, what: str, count: Optional[int] = None) -> Optional[str]:
    """The words a loop that shows a count or a list adds when the end isn't confirmed, or None when it is:
    "Showing at least N <what>: <why>." Never a total, never "none". ``count`` is what the loop shows when it
    filters the rows it read (default: the rows read)."""
    if paged.complete:
        return None
    n = len(paged.items) if count is None else count
    return f"Showing at least {n} {what}: {paged.note or 'there may be more'}."


def log_end(method: str, paged: PageResult) -> dict:
    """Log one structured line for a read (method, positions_read, end, end_reason) and return those fields,
    so a write path can carry them in its own result and a later miss can be traced to the read."""
    from loguru import logger
    fields = {"method": method, **paged.trace()}
    if paged.complete:
        logger.debug(f"paged read: {fields}")
    else:
        logger.info(f"paged read: {fields}")
    return fields


# ── Step 5: "exists?" lookups (the exists-lookups ruling, 2026-11-14) ─────────────────────────────────────────
# found = a match was read; absent = the read reached the end (never on a NULL_NOT_END method); unknown otherwise.
# Use only where one "found" decides the outcome, never to prove uniqueness. A write guard treats unknown as
# "don't create; log it". ("None" as display words still needs a confirmed end: brief condition 4.)

EXISTS_MAX_PAGES = 10
EXISTS_ANSWERS = ("found", "absent", "unknown")


@dataclass(frozen=True)
class Exists:
    """A three-way existence answer, with the matches read and how the read ended."""
    answer: str
    matches: List[Any]
    read: PageResult

    @property
    def found(self) -> bool:
        return self.answer == "found"

    def words(self, what: str) -> str:
        if self.answer == "found":
            return f"{what}: found"
        if self.answer == "absent":
            return f"{what}: not found (the read reached the end)"
        return (f"{what}: can't tell whether it exists ({self.read.positions_read} positions read, end "
                f"{self.read.end}, {self.read.end_reason}): Egeria didn't confirm there are no more")


def _exists_pager(method: Optional[str], fetch_page_size: int, max_pages: int, p: dict) -> _Pager:
    if not isinstance(max_pages, int) or isinstance(max_pages, bool) or not 1 <= max_pages <= EXISTS_MAX_PAGES:
        raise ValueError(f"max_pages must be a whole number from 1 to {EXISTS_MAX_PAGES}, not {max_pages!r}")
    return _pager(None, fetch_page_size, p["end_policy"], p.get("probe_pages", DEFAULT_PROBE_PAGES),
                  DEFAULT_MAX_EMPTY_ROWS, max_pages, None)


def _exists_answer(pager: _Pager, matches: List[Any], p: dict) -> Exists:
    result = pager.result or PageResult(items=list(pager.items), end="capped", note="stopped at the first match",
                                        pages_read=pager.pages, positions_read=pager.start, end_reason="want")
    if p.get("null_not_end"):
        result = replace(result, null_not_end=True)
    if matches:
        return Exists("found", matches, result)
    return Exists("absent" if result.reached_end else "unknown", [], result)


def exists(fetch: Callable[[int, int], Any], match: Callable[[Any], bool], *, method: Optional[str],
           fetch_page_size: int = DEFAULT_FETCH_PAGE_SIZE, max_pages: int = EXISTS_MAX_PAGES,
           client: Any = None) -> Exists:
    """Page ``fetch`` (with ``**paging_for(method, client)``) until a row satisfies ``match`` (an exact,
    client-side test), the end is reached, or ``max_pages`` (at most EXISTS_MAX_PAGES) stops it."""
    p = paging_for(method, client)
    pager = _exists_pager(method, fetch_page_size, max_pages, p)
    matches: List[Any] = []
    while not matches and (req := pager.request()) is not None:
        with _end_signal() as record:
            page = fetch(*req)
        before = len(pager.items)
        pager.feed(_signalled(page, record))
        matches = [row for row in pager.items[before:] if match(row)]
    return _exists_answer(pager, matches, p)


async def async_exists(fetch: Callable[[int, int], Awaitable[Any]], match: Callable[[Any], bool], *,
                       method: Optional[str], fetch_page_size: int = DEFAULT_FETCH_PAGE_SIZE,
                       max_pages: int = EXISTS_MAX_PAGES, client: Any = None) -> Exists:
    """``exists`` for an async ``fetch``."""
    p = await async_paging_for(method, client)
    pager = _exists_pager(method, fetch_page_size, max_pages, p)
    matches: List[Any] = []
    while not matches and (req := pager.request()) is not None:
        with _end_signal() as record:
            page = await fetch(*req)
        before = len(pager.items)
        pager.feed(_signalled(page, record))
        matches = [row for row in pager.items[before:] if match(row)]
    return _exists_answer(pager, matches, p)
