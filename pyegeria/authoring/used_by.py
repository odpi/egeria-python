"""What uses this spec, Report or sheet? (P3, for Studio's impact view; DESIGN-P3-AUTHORING-USED-BY-2026-11-14,
APPROVED by the Architect's ruling (c), RULINGS-SD-DCAT-BATCH-2026-11-14-late.)

``async_used_by(kind, label, client) -> {"items": [{"kind", "name", "qualified_name", "via"}], "complete", "notes"}``

Every read is live, as `client`'s user, through the pager; nothing is cached, and the Portal's shared consumer
index is never used (it's built as the sync identity, leaves zoned specs out, and covers folders only):

- a spec's Reports: every Report the user can see (by type), matched on ``additionalProperties.reportSpec``
  (the label, or ``ReportSpec::``/``ReportType::`` + label); via ``"reportSpec"``;
- a spec's consumer folders: its element's CollectionMembership (the spec at end 2), kept to
  ``ReportSpecFolder::Consumer::`` folders; via ``"CollectionMembership"``;
- a Report's sheets: DataSetContent from a Dashboard to the Report (the Report at end 2); via ``"DataSetContent"``;
- a sheet's consumer folders: ``Dashboard::<name>``'s CollectionMembership, kept to ``DashboardFolder::Consumer::``.

``via`` is a closed set of machine keys (``VIA_KEYS``): ``"reportSpec"`` (runs this spec),
``"CollectionMembership"`` (in a consumer folder), ``"DataSetContent"`` (placed on a sheet). They're Egeria's own
names; callers (Studio) map them to words, and pyegeria carries no UI words (the Architect's P3 open point 2).

Resolving the artifact comes first, through Egeria's exact unique-name read (P3-1): "absent" only on Egeria's
specific not-found; anything else is "unknown". An unresolvable artifact raises AuthoringRefused with ``.answer``
``"absent"`` or ``"unknown"``; nothing is scanned. One exception: a built-in spec that Egeria doesn't hold still
gets its Reports listed, with a note.

Call it on demand (when the user opens "Used by"), never per keystroke or on page load: a spec costs one bounded
Report scan (at most 2,000 Reports) plus a related read. ``complete`` is True only when every read ended
confirmed. A read that fails, or isn't confirmed, is said in ``notes`` and makes ``complete`` False: an empty
``items`` is then "nothing found in what Egeria returned", never "used by none". What the user can't see is not
listed: the answer is their view.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pyegeria.authoring.models import ANSWER_ABSENT, ANSWER_UNKNOWN, AuthoringRefused

REPORT_SCAN_PAGE = 100
REPORT_SCAN_MAX_PAGES = 20       # at most 2000 Reports per call (the Architect's cost guard)
RELATED_PAGE = 100
RELATED_MAX_PAGES = 10
USED_BY_KINDS = ("spec", "report", "sheet")
VIA_KEYS = ("reportSpec", "CollectionMembership", "DataSetContent")   # closed: Studio's word map tests against it
SPEC_PREFIX = "ReportSpec::"
LEGACY_SPEC_PREFIX = "ReportType::"   # the legacy loader's form only: remove with it in the next release


def spec_label_of(value: Any) -> str:
    """A reportSpec value (or a spec name) as a bare label: one ``ReportSpec::`` or legacy ``ReportType::`` prefix
    stripped, nothing else changed. Matching is exact and case-sensitive on the result (P3-2)."""
    value = value if isinstance(value, str) else ""
    for prefix in (SPEC_PREFIX, LEGACY_SPEC_PREFIX):
        if value.startswith(prefix):
            return value[len(prefix):]
    return value
AS_YOU = "Read as you: what you can't see in Egeria isn't listed."


def _props(el: Dict[str, Any]) -> Dict[str, Any]:
    return (el or {}).get("properties") or {}


def _guid(el: Dict[str, Any]) -> Optional[str]:
    return ((el or {}).get("elementHeader") or {}).get("guid")


def _type(el: Dict[str, Any]) -> str:
    return (((el or {}).get("elementHeader") or {}).get("type") or {}).get("typeName", "")


def _related(entry: Dict[str, Any]) -> Dict[str, Any]:
    return entry.get("relatedElement") if isinstance(entry.get("relatedElement"), dict) else entry


class _Answer:
    def __init__(self):
        self.items: List[Dict[str, Any]] = []
        self.notes: List[str] = []
        self.complete = True
        self._seen = set()

    def add(self, kind: str, name: str, qn: Optional[str], via: str) -> None:
        key = (kind, qn or name, via)
        if key not in self._seen:
            self._seen.add(key)
            self.items.append({"kind": kind, "name": name, "qualified_name": qn, "via": via})

    def unconfirmed(self, words: str) -> None:
        self.complete = False
        self.notes.append(words)

    def result(self) -> Dict[str, Any]:
        notes = list(self.notes)
        if not self.items and not self.complete:
            notes.append("Nothing found in what Egeria returned; that isn't \"used by none\".")
        return {"items": self.items, "complete": self.complete, "notes": notes + [AS_YOU]}


async def _paged(fetch, method: str, client: Any, page: int, max_pages: int):
    from pyegeria.core.paging import async_page_all, async_paging_for, log_end
    paged = await async_page_all(fetch, fetch_page_size=page, max_pages=max_pages,
                                 **await async_paging_for(method, client))
    log_end(f"used_by.{method}", paged)
    return paged


async def _reports_running(spec_label: str, client: Any, out: _Answer) -> None:
    from pyegeria.core.paging import at_least_note

    async def fetch(start, size):
        return await client.classification_manager._async_get_elements(
            "Report", start_from=start, page_size=size, graph_query_depth=0)
    try:
        paged = await _paged(fetch, "get_elements", client, REPORT_SCAN_PAGE, REPORT_SCAN_MAX_PAGES)
    except Exception as exc:  # noqa: BLE001 -- said, never "none"
        out.unconfirmed(f"The Reports couldn't be read ({type(exc).__name__}), so which run this spec isn't known.")
        return
    hits = [e for e in paged.items if isinstance(e, dict) and _type(e) == "Report"
            and spec_label_of((_props(e).get("additionalProperties") or {}).get("reportSpec")) == spec_label]
    for e in hits:
        p = _props(e)
        out.add("report", p.get("displayName") or p.get("qualifiedName"), p.get("qualifiedName"), "reportSpec")
    if not paged.complete:
        out.unconfirmed(at_least_note(paged, "Reports that run this spec", len(hits)))


async def _members_of(guid: str, client: Any, prefix: str, what: str, out: _Answer) -> None:
    """The consumer folders `guid` is a member of (CollectionMembership, the member at end 2)."""
    from pyegeria.core._exceptions import PyegeriaNotFoundException
    from pyegeria.core.paging import at_least_note

    async def fetch(start, size):
        try:
            return await client.classification_manager._async_get_related_elements(
                guid, "CollectionMembership", start_at_end=2, start_from=start, page_size=size,
                graph_query_depth=0)
        except PyegeriaNotFoundException:
            return None
    try:
        paged = await _paged(fetch, "get_related_elements", client, RELATED_PAGE, RELATED_MAX_PAGES)
    except Exception as exc:  # noqa: BLE001
        out.unconfirmed(f"The folders holding this {what} couldn't be read ({type(exc).__name__}).")
        return
    n = 0
    for entry in paged.items:
        folder = _related(entry) if isinstance(entry, dict) else {}
        qn = str(_props(folder).get("qualifiedName") or "")
        if qn.startswith(prefix):
            n += 1
            out.add("folder", qn[len(prefix):], qn, "CollectionMembership")
    if not paged.complete:
        out.unconfirmed(at_least_note(paged, f"consumer folders holding this {what}", n))


async def _sheets_placing(report_guid: str, client: Any, out: _Answer) -> None:
    from pyegeria.core._exceptions import PyegeriaNotFoundException
    from pyegeria.core.paging import at_least_note
    from pyegeria.view.dashboards import DASHBOARD_QN_PREFIX, sheet_name_from_dashboard_qn

    async def fetch(start, size):
        try:
            return await client.classification_manager._async_get_related_elements(
                report_guid, "DataSetContent", start_at_end=2, start_from=start, page_size=size,
                graph_query_depth=0)
        except PyegeriaNotFoundException:
            return None
    try:
        paged = await _paged(fetch, "get_related_elements", client, RELATED_PAGE, RELATED_MAX_PAGES)
    except Exception as exc:  # noqa: BLE001
        out.unconfirmed(f"The sheets placing this Report couldn't be read ({type(exc).__name__}).")
        return
    n = 0
    for entry in paged.items:
        dash = _related(entry) if isinstance(entry, dict) else {}
        qn = str(_props(dash).get("qualifiedName") or "")
        if qn.startswith(DASHBOARD_QN_PREFIX):
            n += 1
            out.add("sheet", sheet_name_from_dashboard_qn(qn), qn, "DataSetContent")
    if not paged.complete:
        out.unconfirmed(at_least_note(paged, "sheets placing this Report", n))


async def _unique(client: Any, qn: str, what: str):
    """Egeria's exact unique-name read of `qn`: the element, or None on Egeria's specific not-found. Unknown raises
    AuthoringRefused(answer="unknown"), never None."""
    from pyegeria.core.unique_name import async_by_unique_name
    found = await async_by_unique_name(client, qn)
    if found.answer == "unknown":
        raise AuthoringRefused(f"Couldn't confirm whether Egeria holds {what}: {found.reason or 'no clear answer'}",
                               answer=ANSWER_UNKNOWN)
    return found.element if found.found else None


def _is_builtin_spec(label: str) -> bool:
    from pyegeria.view.base_report_formats import lookup_report_spec
    try:
        fs, _tier, _label = lookup_report_spec(f"builtin:{label}")
    except Exception:  # noqa: BLE001 -- not known as built in
        return False
    return fs is not None


async def async_used_by(kind: str, label: str, client: Any) -> Dict[str, Any]:
    """What uses `kind` `label`, as `client`'s user. Never raises for a failed read of what USES it (that's in
    ``notes``, and ``complete`` is False). Raises AuthoringRefused for a bad kind or no client, and, with ``answer``
    ``"absent"`` or ``"unknown"``, for an artifact that can't be resolved (P3-1)."""
    from pyegeria.authoring.lifecycle import _report_element
    from pyegeria.authoring.serialize import DASHBOARD_FOLDER_PREFIX, SPEC_FOLDER_PREFIX
    if kind not in USED_BY_KINDS:
        raise AuthoringRefused(f"used_by works on one of {', '.join(USED_BY_KINDS)}, not {kind!r}.")
    if not label:
        raise AuthoringRefused("used_by needs the artifact's name.")
    if client is None or not getattr(client, "user_id", None):
        raise AuthoringRefused("used_by reads Egeria as you: a signed-in client is needed.")
    out = _Answer()

    if kind == "spec":
        bare = spec_label_of(label)
        el = None
        for qn in (f"{SPEC_PREFIX}{bare}", f"{LEGACY_SPEC_PREFIX}{bare}"):
            el = await _unique(client, qn, f"a report spec {qn}")
            if el:
                break
        if el is None and not _is_builtin_spec(bare):
            raise AuthoringRefused(f"Egeria holds no report spec named {bare!r} that you can see.",
                                   answer=ANSWER_ABSENT)
        await _reports_running(bare, client, out)
        if el is None:
            out.notes.append(f"Egeria holds no report spec {bare!r} that you can see (it's built in), so no "
                             f"consumer folder holds it for you.")
        elif _guid(el):
            await _members_of(_guid(el), client, SPEC_FOLDER_PREFIX, "spec", out)
        return out.result()

    if kind == "report":
        el = await _unique(client, label, f"a Report {label}")
        if not (el and _type(el) == "Report"):
            try:
                el = await _report_element(client, label)   # by display name; unknown raises (answer unknown)
            except AuthoringRefused:
                raise
            except Exception as exc:  # noqa: BLE001 -- couldn't tell: unknown, never absent
                raise AuthoringRefused(f"Couldn't confirm whether Egeria holds a Report named {label!r} "
                                       f"({type(exc).__name__}).", answer=ANSWER_UNKNOWN) from exc
        if not el:
            raise AuthoringRefused(f"Egeria holds no Report named {label!r} that you can see.", answer=ANSWER_ABSENT)
        await _sheets_placing(_guid(el), client, out)
        return out.result()

    qn = label if label.startswith("Dashboard::") else f"Dashboard::{label}"
    el = await _unique(client, qn, f"a dashboard sheet {qn}")
    if not el:
        raise AuthoringRefused(f"Egeria holds no dashboard sheet {label!r} ({qn}) that you can see.",
                               answer=ANSWER_ABSENT)
    await _members_of(_guid(el), client, DASHBOARD_FOLDER_PREFIX, "sheet", out)
    return out.result()


def used_by(kind: str, label: str, client: Any) -> Dict[str, Any]:
    """Sync form of async_used_by."""
    from pyegeria.core.async_runner import run_sync
    return run_sync(async_used_by(kind, label, client))
