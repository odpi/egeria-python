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

``via`` carries Egeria's own names; callers map them to words. ``complete`` is True only when every read ended
confirmed. A read that fails, or isn't confirmed, is said in ``notes`` and makes ``complete`` False: an empty
``items`` is then "nothing found in what Egeria returned", never "used by none". What the user can't see is not
listed: the answer is their view.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pyegeria.authoring.models import ANSWER_ABSENT, AuthoringRefused

REPORT_SCAN_PAGE = 100
REPORT_SCAN_MAX_PAGES = 20       # at most 2000 Reports per call (the Architect's cost guard)
RELATED_PAGE = 100
RELATED_MAX_PAGES = 10
USED_BY_KINDS = ("spec", "report", "sheet")
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
    names = {spec_label, f"ReportSpec::{spec_label}", f"ReportType::{spec_label}"}

    async def fetch(start, size):
        return await client.classification_manager._async_get_elements(
            "Report", start_from=start, page_size=size, graph_query_depth=0)
    try:
        paged = await _paged(fetch, "get_elements", client, REPORT_SCAN_PAGE, REPORT_SCAN_MAX_PAGES)
    except Exception as exc:  # noqa: BLE001 -- said, never "none"
        out.unconfirmed(f"The Reports couldn't be read ({type(exc).__name__}), so which run this spec isn't known.")
        return
    hits = [e for e in paged.items if isinstance(e, dict) and _type(e) == "Report"
            and str((_props(e).get("additionalProperties") or {}).get("reportSpec") or "") in names]
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


async def async_used_by(kind: str, label: str, client: Any) -> Dict[str, Any]:
    """What uses `kind` `label`, as `client`'s user. Never raises for a failed read (it's in ``notes``); raises
    AuthoringRefused for a bad kind, no client, or a Report or sheet that can't be resolved (pyegeria's words, with
    ``answer`` absent or unknown)."""
    from pyegeria.authoring.lifecycle import _by_qualified_name, _report_element
    from pyegeria.authoring.serialize import DASHBOARD_FOLDER_PREFIX, SPEC_FOLDER_PREFIX
    if kind not in USED_BY_KINDS:
        raise AuthoringRefused(f"used_by works on one of {', '.join(USED_BY_KINDS)}, not {kind!r}.")
    if not label:
        raise AuthoringRefused("used_by needs the artifact's name.")
    if client is None or not getattr(client, "user_id", None):
        raise AuthoringRefused("used_by reads Egeria as you: a signed-in client is needed.")
    out = _Answer()

    if kind == "spec":
        from md_processing.v2.report import find_report_spec_element
        bare = label.split("::", 1)[1] if label.startswith(("ReportSpec::", "ReportType::")) else label
        await _reports_running(bare, client, out)
        try:
            el = await find_report_spec_element(client, label)
        except Exception as exc:  # noqa: BLE001
            out.unconfirmed(f"The spec's element couldn't be read ({type(exc).__name__}), so its folders aren't known.")
            return out.result()
        if el is None:
            out.notes.append(f"Egeria holds no report spec {label!r} that you can see, so no consumer folder holds "
                             f"it for you (it may be built in, or local).")
        elif _guid(el):
            await _members_of(_guid(el), client, SPEC_FOLDER_PREFIX, "spec", out)
        return out.result()

    if kind == "report":
        el = await _report_element(client, label)   # unknown raises "couldn't confirm" (answer unknown)
        if not el:
            raise AuthoringRefused(f"Egeria holds no Report named {label!r} that you can see.", answer=ANSWER_ABSENT)
        await _sheets_placing(_guid(el), client, out)
        return out.result()

    qn = label if label.startswith("Dashboard::") else f"Dashboard::{label}"
    try:
        el = await _by_qualified_name(client, qn)
    except Exception as exc:  # noqa: BLE001
        out.unconfirmed(f"The sheet's Dashboard couldn't be read ({type(exc).__name__}), so its folders aren't known.")
        return out.result()
    if not el:
        raise AuthoringRefused(f"Egeria holds no dashboard sheet {label!r} ({qn}) that you can see.",
                               answer=ANSWER_ABSENT)
    await _members_of(_guid(el), client, DASHBOARD_FOLDER_PREFIX, "sheet", out)
    return out.result()


def used_by(kind: str, label: str, client: Any) -> Dict[str, Any]:
    """Sync form of async_used_by."""
    from pyegeria.core.async_runner import run_sync
    return run_sync(async_used_by(kind, label, client))
