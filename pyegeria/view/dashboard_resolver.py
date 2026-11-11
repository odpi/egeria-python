"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

The dashboard data step, shared by every app that shows a Dashboard Sheet held in Egeria (BRIEF
EA-CATCHUP-AND-DASHBOARDS B4, decision D4): the Portal and Egeria Advisor resolve a sheet the same way.

    resolve_dashboard_sheet(client, name, *, perspective=None, run=False) -> ResolvedSheet | None

Data only: no rendering, no caching, no auth. Each app keeps its own display, caching and sign-in, and
passes a client that is already signed in AS THE VIEWER: every read is the viewer's, so Egeria's zone
check decides what they see. pyegeria needs no server of its own to do this; Egeria is the only server.

What it does, per sheet:
  1. read the sheet from its Egeria element chain (pyegeria.view.dashboards, the same reader the
     Dr.Egeria writer is checked against);
  2. keep the placements for `perspective` (a placement with no perspectives shows in every one), in
     sheet order;
  3. for each REPORT placement, read its Report element as the viewer and find the ReportSpec the
     Report names (`reportSpec`) in pyegeria's registry, with the spec's source tier;
  4. say whether the spec can run (pyegeria's own spec resolver), and with `run=True` run it with the
     Report's stored parameters (exec_report_spec).

Absence is said in words, never as an empty value. A placement comes back as one of:
  - "report":     its Report was read; `spec_source` says which tier the spec came from, or `error` says
                  the spec was not found;
  - "text":       markdown held on the sheet;
  - "missing":    its Report is gone (or its link is), with the reader's words in `reason`;
  - "restricted": its Report or ReportSpec is in a zone this viewer cannot see. `restricted` is True,
                  `reason` is "not visible to you", `restricted_element` says which. The sheet's other
                  placements still resolve.

How "restricted" is told from "missing" (checked in Egeria's Java, OpenMetadataAccessSecurityConnector):
Egeria drops an element the viewer may not see from relationship reads and searches without a word, so a
zoned Report's DataSetContent link simply vanishes for that viewer. An EXPLICIT read by GUID is different:
Egeria answers "not authorized" (OPEN-METADATA-SECURITY-403-020) for an element in a hidden zone and "not
found" for one that is gone. So the resolver reads by GUID: the GUID the Dr.Egeria writer records on each
report placement (`reportGUID`), and the GUID the EGERIA spec tier holds for a spec synced by another
user. A placement written before the writer recorded GUIDs, whose link is gone, can only say "missing".
"""
from __future__ import annotations

import asyncio
import json
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple

from loguru import logger
from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "NOT_VISIBLE", "REPORT_GONE", "ResolvedPlacement", "ResolvedReport", "ResolvedSheet",
    "async_list_dashboard_sheets_for_viewer", "async_resolve_dashboard_sheet", "async_resolve_sheet",
    "is_not_visible_error", "list_dashboard_sheets_for_viewer", "placements_for_perspective", "SPEC_NOT_IN_FOLDER",
    "report_from_element", "resolve_dashboard_sheet", "resolve_sheet",
]

#: The reason a restricted placement gives (§4.7): the same words whichever element is hidden.
NOT_VISIBLE = "not visible to you"
#: A Report this viewer was linked to but Egeria no longer holds.
REPORT_GONE = "the Report this placement shows is no longer in Egeria"
#: A placement whose spec no tier here holds, fetched from Egeria as the viewer: consumer folders govern
#: what a tool LISTS, not whether a spec a sheet already references can RUN (Architect, B7a read-back).
SPEC_NOT_IN_FOLDER = "held in Egeria, not in this tool's folder"

#: Egeria's message ids for "this element is in a zone you cannot see": an explicit read (403-020) and a
#: filtered one (500-002, normally swallowed by the server, matched in case it surfaces).
_NOT_VISIBLE_IDS = ("OPEN-METADATA-SECURITY-403-020", "OPEN-METADATA-SECURITY-500-002")
_NOT_VISIBLE_WORDS = ("is not visible to user", "is not authorized to issue an operation read")
_MAX_CONCURRENT_READS = 6


class ResolvedReport(BaseModel):
    """A Report element as the viewer read it: what to run and how. `params` are the Report's stored
    execution parameters (its additionalProperties, less reportSpec / outputFormat / analyticParams);
    `analytic_params` is its decoded `analyticParams` JSON."""
    guid: Optional[str] = None
    name: str
    qualified_name: Optional[str] = None
    description: str = ""
    report_spec: Optional[str] = None
    output_format: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)
    analytic_params: Dict[str, Any] = Field(default_factory=dict)


class ResolvedPlacement(BaseModel):
    """One placement of a resolved sheet. See the module docstring for the kinds."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    position: int                       # 1-based, in sheet order (before any perspective filter)
    ref: str                            # the placement's name: its Report's name for a report placement
    kind: Literal["report", "text", "missing", "restricted"]
    title: str
    span: str = "1"
    emphasis: str = "kpi"
    perspectives: List[str] = Field(default_factory=list)
    detail_spec: Optional[str] = None
    content: Optional[str] = None       # markdown, for a text placement
    note: Optional[str] = None          # the sheet reader's words (drift, an odd span, a missing link)
    restricted: bool = False
    restricted_element: Optional[Literal["Report", "ReportSpec"]] = None
    reason: Optional[str] = None        # why this placement shows no report: restricted or missing
    report_guid: Optional[str] = None
    report: Optional[ResolvedReport] = None
    spec: Optional[str] = None          # the ReportSpec label the Report names
    spec_source: Optional[Dict[str, Any]] = None   # {"tier", "label", "version", ...}; None if not found
    format_set: Any = Field(default=None, exclude=True)   # the FormatSet itself, for the caller's use
    runnable: Optional[bool] = None     # None: the spec was not resolved (unknown, not "runnable")
    refusal: Optional[str] = None       # the spec resolver's words when not runnable
    result: Optional[Dict[str, Any]] = None   # with run=True: exec_report_spec's result
    error: Optional[str] = None         # what went wrong finding the spec or running it, in words
    #: The internal name ("egeria:<label>@v<N>") a spec fetched as the viewer runs under; None otherwise.
    fetched_as: Optional[str] = None


class ResolvedSheet(BaseModel):
    """A Dashboard Sheet held in Egeria, resolved for one viewer."""
    name: str
    heading: str
    description: str = ""
    family: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)
    guid: Optional[str] = None
    source: str = "egeria"
    breaks: List[str] = Field(default_factory=list)
    perspective: Optional[str] = None
    viewer: Optional[str] = None
    placements: List[ResolvedPlacement] = Field(default_factory=list)


# ---------------------------------------------------------------------------- helpers

def is_not_visible_error(exc: BaseException) -> bool:
    """True when Egeria refused a read because the element is in a zone the caller cannot see. A refused or
    expired TOKEN is not this (it is a 401 the app must handle), so it reads False and is re-raised."""
    text = " ".join(str(part) for part in (exc, getattr(exc, "message", ""), getattr(exc, "additional_info", "")))
    if any(i in text for i in _NOT_VISIBLE_IDS) or any(w in text.lower() for w in _NOT_VISIBLE_WORDS):
        return True
    from pyegeria.core._exceptions import PyegeriaUnauthorizedException
    return isinstance(exc, PyegeriaUnauthorizedException) and getattr(exc, "related_http_code", None) == 403


def _is_not_found_error(exc: BaseException) -> bool:
    from pyegeria.core._exceptions import PyegeriaNotFoundException
    return isinstance(exc, PyegeriaNotFoundException) or "-404-" in str(exc)


def placements_for_perspective(placements: List[Any], perspective: Optional[str]) -> List[Any]:
    """The placements for `perspective`, in order. A placement with no perspectives shows in every one;
    no perspective means every placement."""
    if not perspective:
        return list(placements)
    return [p for p in placements if not (getattr(p, "perspectives", None) or []) or perspective in p.perspectives]


def report_from_element(element: Dict[str, Any], fallback_name: str = "") -> ResolvedReport:
    """A ResolvedReport from a Report element (flat `properties`, as classification-explorer returns it)."""
    props = element.get("properties") or {}
    extra = dict(props.get("additionalProperties") or {})
    analytic: Dict[str, Any] = {}
    raw = extra.get("analyticParams")
    if raw:
        try:
            decoded = json.loads(raw) if isinstance(raw, str) else raw
            if isinstance(decoded, dict):
                analytic = decoded
        except (TypeError, ValueError):
            logger.debug(f"dashboard resolver: unparseable analyticParams on {fallback_name!r}: {raw!r}")
    return ResolvedReport(
        guid=(element.get("elementHeader") or {}).get("guid"),
        name=props.get("displayName") or fallback_name,
        qualified_name=props.get("qualifiedName"),
        description=props.get("description") or "",
        report_spec=extra.get("reportSpec"),
        output_format=extra.get("outputFormat"),
        params={k: v for k, v in extra.items() if k not in ("reportSpec", "outputFormat", "analyticParams")},
        analytic_params=analytic,
    )


async def _read_by_guid(client: Any, guid: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    """("found", element) | ("restricted", None) | ("gone", None), read as the viewer. Any other failure
    (Egeria down, a refused token) raises: it says nothing about the element."""
    try:
        element = await client.classification_manager._async_get_element_by_guid_(guid)
    except Exception as exc:  # noqa: BLE001 -- classified below; anything else propagates
        if is_not_visible_error(exc):
            return "restricted", None
        if _is_not_found_error(exc):
            return "gone", None
        raise
    if isinstance(element, dict) and element.get("elementHeader"):
        return "found", element
    return "gone", None


def _default_spec_lookup(label: str) -> Tuple[Any, Optional[Dict[str, Any]]]:
    """(FormatSet, spec_source) from pyegeria's registry, or (None, None)."""
    from pyegeria.view.base_report_formats import lookup_report_spec, report_spec_source
    fs, _tier, _label = lookup_report_spec(label)
    if fs is None:
        return None, None
    return fs, report_spec_source(label)


def _function_valued_param_refusal(analytic_params: Dict[str, Any], action: Any) -> Optional[str]:
    """A placement's own analyticParams can name a routine (metric_path) the spec never did; the spec
    resolver checks only the spec's fixed params. Refuse it with pyegeria's own words."""
    if not analytic_params:
        return None
    from pyegeria.view.format_set_executor import AnalyticFunctionRefused, resolve_report_spec_function
    from pyegeria.view.spec_resolver import FUNCTION_VALUED_PARAMS, routine_entry
    analytic = getattr(action, "analytic_function", None) if action is not None else None
    declared = None
    if analytic:
        entry = routine_entry(analytic)
        if entry is not None:
            declared = {getattr(p, "name", "") for p in (getattr(entry, "params", None) or [])}
    for param in FUNCTION_VALUED_PARAMS:
        value = analytic_params.get(param)
        if value in (None, "") or (declared is not None and param not in declared):
            continue
        try:
            resolve_report_spec_function(value)
        except AnalyticFunctionRefused as exc:
            return f"This placement's {param} '{value}' is refused: {exc}"
        except Exception as exc:  # noqa: BLE001 -- a resolver failure is not a verdict either way
            logger.debug(f"placement {param} {value!r} not checked: {exc}")
    return None


def _runnable(label: str, resolutions: Dict[str, Any], analytic_params: Dict[str, Any],
              action: Any) -> Tuple[Optional[bool], Optional[str]]:
    res = resolutions.get(label)
    if res is None:
        return None, None
    if getattr(res, "runnable", False):
        refusal = _function_valued_param_refusal(analytic_params, action)
        return (False, refusal) if refusal else (True, None)
    words = list(getattr(res, "words", None) or [])
    return False, " ".join(words) or f"Spec '{label}' cannot run."


def _all_resolutions() -> Dict[str, Any]:
    try:
        from pyegeria.view.spec_resolver import resolve_all
        return resolve_all()
    except Exception as exc:  # noqa: BLE001 -- a sheet must not go down with the resolver
        logger.warning(f"dashboard resolver: spec resolution unavailable: {exc}")
        return {}


def _run_report(client: Any, placement: ResolvedPlacement) -> Dict[str, Any]:
    """exec_report_spec as the viewer: the client's own token, server and platform."""
    from pyegeria.view.format_set_executor import exec_report_spec
    report = placement.report
    action = getattr(placement.format_set, "action", None)
    analytic = bool(getattr(action, "analytic_function", None)) if action is not None else False
    params = dict(report.analytic_params if analytic else report.params)
    return exec_report_spec(
        placement.fetched_as or placement.spec, output_format=report.output_format or "DICT", params=params,
        view_server=getattr(client, "server_name", None) or getattr(client, "view_server", None),
        view_url=getattr(client, "platform_url", None), user=getattr(client, "user_id", None),
        user_pass=getattr(client, "user_pwd", None), token=getattr(client, "token", None))


# ---------------------------------------------------------------------------- the data step

def _fetched_not_synced(source: Optional[Dict[str, Any]]) -> bool:
    """An EGERIA-tier spec that is in the cache only because a call fetched it: no synced folder holds it."""
    if not source or source.get("tier") != "egeria" or not source.get("label"):
        return False
    from pyegeria.view.egeria_spec_cache import egeria_tier_info
    info = egeria_tier_info(source["label"])
    return bool(info) and not info.get("folders")


async def _fetch_as_viewer(client: Any, label: str) -> Tuple[Any, Optional[Dict[str, Any]], Optional[str], Optional[str]]:
    """Fetch a spec no tier holds from Egeria, as the viewer `client` (Egeria's zone check on this read is
    the authority). `(FormatSet, spec_source, internal name, None)`, or `(None, None, None, why)` with
    Egeria's or pyegeria's words; `why` is None when this client cannot read collections at all."""
    if not callable(getattr(client, "_async_get_collections_by_name", None)):
        return None, None, None, None
    from pyegeria.view.egeria_spec_cache import async_fetch_spec_for_call, fetched_spec, fetched_spec_source
    try:
        name = await async_fetch_spec_for_call(client, label)
    except Exception as exc:  # noqa: BLE001 -- the placement says why, in words
        why = NOT_VISIBLE if is_not_visible_error(exc) or is_not_visible_error(exc.__cause__ or exc) else None
        return None, None, None, why or " ".join(str(exc).split())[:300]
    internal = name.split(":", 1)[1] if name.startswith("egeria:") else name
    fs = fetched_spec(internal)
    if fs is None:
        return None, None, None, f"'{name}' was fetched but is not loadable"
    return fs, fetched_spec_source(internal), name, None


async def _resolve_report_placement(client: Any, base: Dict[str, Any], p: Any, resolutions: Dict[str, Any],
                                    spec_lookup: Callable, check_spec_visibility: bool,
                                    spec_visibility: Dict[str, asyncio.Future], gate: asyncio.Semaphore,
                                    fetch_missing: bool = True) -> ResolvedPlacement:
    guid = getattr(p, "report_guid", None)
    kind = getattr(p, "kind", "report")
    note = getattr(p, "note", None)

    if not guid:
        # A "missing" placement with no recorded GUID: the reader's words are all there is.
        return ResolvedPlacement(**base, kind="missing", reason=note or REPORT_GONE)
    async with gate:
        state, element = await _read_by_guid(client, guid)
    if state == "restricted":
        return ResolvedPlacement(**base, kind="restricted", restricted=True, restricted_element="Report",
                                 reason=NOT_VISIBLE, report_guid=guid)
    if state == "gone":
        return ResolvedPlacement(**base, kind="missing", report_guid=guid,
                                 reason=note if kind == "missing" and note else REPORT_GONE)

    report = report_from_element(element, p.ref)
    out = ResolvedPlacement(**{**base, "title": report.name or base["title"]}, kind="report", report_guid=guid,
                            report=report, spec=report.report_spec)
    if not report.report_spec:
        out.error = f"Report '{report.name}' names no report spec"
        return out
    fs, source = spec_lookup(report.report_spec)
    if fs is None and fetch_missing:
        async with gate:
            fs, source, fetched_as, why = await _fetch_as_viewer(client, report.report_spec)
        if fs is None:
            out.error = f"report spec '{report.report_spec}' was not found in any tier" + (
                f", and fetching it from Egeria as {getattr(client, 'user_id', None) or 'the viewer'} failed: {why}"
                if why else "")
            return out
        out.fetched_as = fetched_as
        out.note = f"{out.note}; {SPEC_NOT_IN_FOLDER}" if out.note else SPEC_NOT_IN_FOLDER
    if fs is None:
        out.error = f"report spec '{report.report_spec}' was not found in any tier"
        return out
    out.format_set, out.spec_source = fs, source
    if out.fetched_as is None and _fetched_not_synced(source):
        # Fetched as a viewer on an earlier view and written through to a per-user cache: it is in a tier now,
        # but still in none of this tool's folders, so it still says so (Architect, LD-1 read-back).
        out.note = f"{out.note}; {SPEC_NOT_IN_FOLDER}" if out.note else SPEC_NOT_IN_FOLDER
    spec_guid = (source or {}).get("guid") if (source or {}).get("tier") == "egeria" else None
    if check_spec_visibility and spec_guid:
        # The EGERIA tier may be filled by another user (the app's service user, into a shared cache);
        # Egeria's own zone check on THIS viewer's read is the authority (§4.6).
        if spec_guid not in spec_visibility:
            async def _check(g=spec_guid):
                async with gate:
                    return (await _read_by_guid(client, g))[0]
            spec_visibility[spec_guid] = asyncio.ensure_future(_check())
        if await spec_visibility[spec_guid] == "restricted":
            return ResolvedPlacement(**base, kind="restricted", restricted=True, restricted_element="ReportSpec",
                                     reason=NOT_VISIBLE, report_guid=guid, report=report, spec=report.report_spec)
    out.runnable, out.refusal = _runnable(report.report_spec, resolutions, report.analytic_params,
                                          getattr(fs, "action", None))
    return out


async def async_resolve_dashboard_sheet(client: Any, name: str, *, perspective: Optional[str] = None,
                                        run: bool = False, spec_lookup: Optional[Callable] = None,
                                        check_spec_visibility: bool = True,
                                        fetch_missing: bool = True) -> Optional[ResolvedSheet]:
    """Resolve the Egeria-held sheet `name` as the viewer `client` is signed in as. None if Egeria holds
    no such sheet for this viewer (a sheet in a zone they cannot see reads the same as no sheet).

    `spec_lookup(label) -> (FormatSet | None, spec_source | None)` finds a ReportSpec; the default is
    pyegeria's registry (local, EGERIA and built-in tiers). An app with a per-user spec tier passes its own.
    `check_spec_visibility`: re-read an EGERIA-tier spec by GUID as this viewer (one read per distinct spec).
    `run`: also run each runnable report placement (exec_report_spec, as the viewer); off by default, since
    an app that runs placements itself (the Portal) only needs the data.
    `fetch_missing`: a placement whose spec no tier holds is fetched from Egeria as this viewer and noted
    SPEC_NOT_IN_FOLDER: consumer folders govern what a tool lists, not whether a referenced spec can run.
    A spec the viewer cannot read stays absent, with Egeria's reason in `error`.
    """
    from pyegeria.view.dashboards import read_sheet_from_chain
    sheet = await read_sheet_from_chain(client, name)
    if sheet is None:
        return None
    return await async_resolve_sheet(client, sheet, perspective=perspective, run=run, spec_lookup=spec_lookup,
                                     check_spec_visibility=check_spec_visibility, fetch_missing=fetch_missing)


async def async_resolve_sheet(client: Any, sheet: Any, *, perspective: Optional[str] = None, run: bool = False,
                              spec_lookup: Optional[Callable] = None,
                              check_spec_visibility: bool = True, fetch_missing: bool = True) -> ResolvedSheet:
    """Resolve a sheet the caller has ALREADY read from Egeria (an EgeriaDashboardSheet, e.g. from its own
    cache of load_dashboard_sheet), so an app that caches sheet reads does not walk the chain twice. The
    sheet must have been read as the same viewer as `client`. Otherwise as async_resolve_dashboard_sheet."""
    resolved = ResolvedSheet(name=sheet.name, heading=sheet.heading, description=sheet.description or "",
                             family=sheet.family, aliases=list(sheet.aliases or []), guid=getattr(sheet, "guid", None),
                             breaks=list(getattr(sheet, "breaks", None) or []), perspective=perspective,
                             viewer=getattr(client, "user_id", None))
    resolutions = _all_resolutions()
    lookup = spec_lookup or _default_spec_lookup
    gate = asyncio.Semaphore(_MAX_CONCURRENT_READS)
    spec_visibility: Dict[str, asyncio.Future] = {}

    positions = {id(p): i for i, p in enumerate(sheet.placements, start=1)}
    work = []
    for p in placements_for_perspective(sheet.placements, perspective):
        base = dict(position=positions[id(p)], ref=p.ref, title=p.ref, span=p.span, emphasis=p.emphasis,
                    perspectives=list(p.perspectives or []), detail_spec=p.detail_spec,
                    note=getattr(p, "note", None))
        if getattr(p, "kind", None) == "text" or p.content is not None:
            async def _text(base=base, p=p):
                return ResolvedPlacement(**base, kind="text", content=p.content or "")
            work.append(_text())
        else:
            work.append(_resolve_report_placement(client, base, p, resolutions, lookup, check_spec_visibility,
                                                  spec_visibility, gate, fetch_missing))
    resolved.placements = list(await asyncio.gather(*work))

    if run:
        for pl in resolved.placements:
            if pl.kind != "report" or pl.format_set is None or pl.runnable is False:
                continue
            try:
                pl.result = await asyncio.to_thread(_run_report, client, pl)
            except Exception as exc:  # noqa: BLE001 -- one placement's failure is that placement's words
                if is_not_visible_error(exc):
                    pl.kind, pl.restricted, pl.reason = "restricted", True, NOT_VISIBLE
                    pl.restricted_element = "ReportSpec"
                else:
                    pl.error = f"{type(exc).__name__}: {' '.join(str(exc).split())[:300]}"
    return resolved


async def async_list_dashboard_sheets_for_viewer(client: Any, folders: Optional[List[str]] = None) -> List[Any]:
    """The sheets Egeria holds that the viewer `client` is signed in as can see. Listing is per viewer:
    a sheet in a zone they cannot see is not listed, so an app caching this keys it by the viewer's
    credential identity, never a shared key. `folders` (else the configured dashboard folders) scopes it
    as `async_list_dashboard_sheets` does; the result is its DashboardSheetListing, notes included."""
    from pyegeria.view.dashboards import async_list_dashboard_sheets
    return await async_list_dashboard_sheets(client, folders)


def resolve_dashboard_sheet(client: Any, name: str, *, perspective: Optional[str] = None, run: bool = False,
                            spec_lookup: Optional[Callable] = None,
                            check_spec_visibility: bool = True,
                            fetch_missing: bool = True) -> Optional[ResolvedSheet]:
    """Sync form of async_resolve_dashboard_sheet."""
    from pyegeria.core.async_runner import run_sync
    return run_sync(async_resolve_dashboard_sheet(client, name, perspective=perspective, run=run,
                                                  spec_lookup=spec_lookup,
                                                  check_spec_visibility=check_spec_visibility,
                                                  fetch_missing=fetch_missing))


def resolve_sheet(client: Any, sheet: Any, *, perspective: Optional[str] = None, run: bool = False,
                  spec_lookup: Optional[Callable] = None, check_spec_visibility: bool = True,
                  fetch_missing: bool = True) -> ResolvedSheet:
    """Sync form of async_resolve_sheet."""
    from pyegeria.core.async_runner import run_sync
    return run_sync(async_resolve_sheet(client, sheet, perspective=perspective, run=run, spec_lookup=spec_lookup,
                                        check_spec_visibility=check_spec_visibility, fetch_missing=fetch_missing))


def list_dashboard_sheets_for_viewer(client: Any, folders: Optional[List[str]] = None) -> List[Any]:
    """Sync form of async_list_dashboard_sheets_for_viewer."""
    from pyegeria.core.async_runner import run_sync
    return run_sync(async_list_dashboard_sheets_for_viewer(client, folders))
