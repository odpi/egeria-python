# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""preview(draft): a live sample, run as the caller, with no global side effect.

- **spec:** runs the draft's own FormatSet through `exec_report_spec`, handed over as the run dictionary
  the executor accepts. The draft is **never registered**: pyegeria's report-spec registry, the Egeria
  spec cache and the fetched-spec map are left as they were (a fetched name shared across users is the
  Portal-3 hazard). A structured TABLE, at most `max_rows` rows, saying when it's capped.
- **report:** the Report's spec (pyegeria's registry, else read from Egeria as the caller, not fetched
  into any cache) run with the Report's parameters and output format.
- **sheet:** each placement resolved as the caller (`async_resolve_sheet`, with no fetch of missing specs);
  placements aren't run unless `run=True`.

Every result says what it is: `capped`, `shown`, `notes`. "Not run" and "nothing found" read differently.
"""
from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from pyegeria.authoring.models import AuthoringRefused, ReportDraft, SheetDraft, SpecDraft, as_draft
from pyegeria.view._output_format_models import FormatSetDict

CHART_FORMATS = ("SERIES", "BAR", "PIE")


def run_dict(label: str, fs, output_format: str) -> Dict[str, Any]:
    """The executor's run dictionary for `fs`, built from a one-spec registry: nothing global is touched."""
    from pyegeria.view.base_report_formats import _select_from_registry
    found = _select_from_registry(FormatSetDict({label: fs}), label, output_format)
    if found is None:
        raise AuthoringRefused(f"Spec {label!r} has no {output_format} format to preview.")
    return found


def _identity(client: Any) -> Dict[str, Any]:
    return {"view_server": getattr(client, "server_name", None) or getattr(client, "view_server", None),
            "view_url": getattr(client, "platform_url", None), "user": getattr(client, "user_id", None),
            "user_pass": getattr(client, "user_pwd", None), "token": getattr(client, "token", None)}


def _cap(result: Dict[str, Any], max_rows: int, notes: List[str]) -> Dict[str, Any]:
    rows = None
    if isinstance(result, dict) and result.get("kind") == "table":
        rows = result.get("rows")
    elif isinstance(result, dict) and result.get("kind") == "json" and isinstance(result.get("data"), list):
        rows = result.get("data")
    end = result.get("end") if isinstance(result, dict) else None
    out = {"result": result, "capped": False, "shown": None, "notes": notes, "end": end}
    if isinstance(result, dict) and result.get("kind") == "empty":
        out["shown"] = 0
        if end in (None, "confirmed"):   # None: not a find (an analytic or chart result says its own absence)
            notes.append("ran, and found nothing")
        else:   # pager step 3: "found nothing" only when the end is confirmed
            notes.extend(result.get("notes") or ["nothing in what was read; can't rule out more"])
        return out
    if rows is None:
        notes.append(f"ran; the result is {result.get('kind') if isinstance(result, dict) else type(result).__name__}, "
                     f"not rows, so it isn't capped")
        return out
    out["shown"] = min(len(rows), max_rows)
    if len(rows) > max_rows:
        trimmed = dict(result)
        trimmed["rows" if result.get("kind") == "table" else "data"] = rows[:max_rows]
        out["result"] = trimmed
        out["capped"] = True
        notes.append(f"capped: {max_rows} of {len(rows)} rows shown")
    elif len(rows) == max_rows:
        out["capped"] = True
        notes.append(f"capped: the run asked for {max_rows} rows and got {max_rows}; there may be more")
    elif end not in (None, "confirmed"):   # pager step 3: the end wasn't reached, whatever the count
        out["capped"] = True
        notes.append(f"{len(rows)} rows shown; Egeria didn't confirm there are no more")  # end stays structured
    elif not rows:
        notes.append("ran, and found nothing")
    return out


async def _run(label: str, fs, client: Any, output_format: str, params: Dict[str, Any], max_rows: int,
               notes: List[str]) -> Dict[str, Any]:
    from pyegeria.view.format_set_executor import exec_report_spec
    out = (output_format or "TABLE").upper()
    if out in CHART_FORMATS:
        # The executor dispatches a chart by registered name, which a draft hasn't got (and mustn't get):
        # preview the routine's data instead, and say so.
        notes.append(f"{out} is previewed as its data (DICT): a chart runs by registered name, and a draft "
                     f"isn't registered")
        out = "DICT"
    params = {**params, "page_size": max_rows}
    # Pager step 3: page a list format fully, up to max_rows rows, so a filtered first page doesn't read as
    # "found nothing" (a text format reads its first page and says so when that showed nothing).
    kwargs = dict(output_format=out, params=params, page_to=max_rows, **_identity(client))
    if out == "TABLE":
        kwargs["table_shape"] = "structured"
    result = await asyncio.to_thread(exec_report_spec, run_dict(label, fs, out), **kwargs)
    return _cap(result, max_rows, notes)


async def _spec_of(report: ReportDraft, client: Any, notes: List[str]):
    if report.pinned_version is not None:
        from pyegeria.authoring.versions import async_spec_at_version
        fs = await async_spec_at_version(client, report.spec, report.pinned_version)
        from pyegeria.authoring.lifecycle import PIN_NOT_HONOURED
        notes.append(f"spec {report.spec!r} pinned at version {report.pinned_version}, read from Egeria as you; "
                     f"not cached; {PIN_NOT_HONOURED.format(version=report.pinned_version)}")
        return fs
    from pyegeria.view.base_report_formats import lookup_report_spec
    fs = lookup_report_spec(report.spec)[0]
    if fs is not None:
        return fs
    from pyegeria.authoring.lifecycle import async_load_held
    held = await async_load_held("spec", report.spec, client)
    notes.append(f"spec {report.spec!r} read from Egeria as you (version {held.base_version}); not cached")
    return held.format_set


async def _sheet_for_resolver(draft: SheetDraft, client: Any, notes: List[str]):
    """The draft as the sheet object async_resolve_sheet reads, each Report read by name as the caller."""
    from pyegeria.authoring.lifecycle import _report_element
    from pyegeria.view.dashboards import EgeriaDashboardSheet, EgeriaPlacement
    placements = []
    for i, p in enumerate(draft.placements, start=1):
        common = dict(span=p.span, emphasis=p.emphasis, perspectives=list(p.perspectives), detail_spec=p.detail_spec)
        if p.text is not None:
            placements.append(EgeriaPlacement(ref=p.name, content=p.text, kind="text", **common))
            continue
        try:
            el = await _report_element(client, p.report)
        except AuthoringRefused as exc:
            el = None
            notes.append(f"placement {i} ({p.report}): {exc}")
        guid = (el or {}).get("elementHeader", {}).get("guid")
        placements.append(EgeriaPlacement(ref=p.report, kind="report" if guid else "missing", report_guid=guid,
                                          note=None if guid else "no Report by this name that you can see",
                                          **common))
    return EgeriaDashboardSheet(name=draft.name, heading=draft.heading, description=draft.description,
                                family=draft.family, placements=placements)


def _registry_lookup(label: str):
    """Read-only spec lookup for a previewed sheet: pyegeria's registry tiers, never a fetch."""
    from pyegeria.view.base_report_formats import lookup_report_spec, report_spec_source
    fs = lookup_report_spec(label)[0]
    return (fs, report_spec_source(label)) if fs is not None else (None, None)


async def async_preview(draft: Any, *, client: Any, max_rows: int = 25, output_format: Optional[str] = None,
                        params: Optional[Dict[str, Any]] = None, perspective: Optional[str] = None,
                        run: bool = False) -> Dict[str, Any]:
    """A live sample of `draft`, run as `client`'s user. See the module docstring."""
    if client is None:
        raise AuthoringRefused("Preview runs as you against Egeria: a client signed in as you is needed.")
    if not isinstance(max_rows, int) or max_rows < 1:
        raise AuthoringRefused("max_rows must be a whole number of at least 1.")
    draft = as_draft(draft)
    from pyegeria.authoring.publication import async_publication_notes
    said, unread = await async_publication_notes(client, draft)
    notes: List[str] = said + unread
    viewer = getattr(client, "user_id", None)
    if isinstance(draft, SpecDraft):
        out = await _run(draft.label, draft.format_set, client, output_format or "TABLE", params or {}, max_rows, notes)
        return {"kind": "spec", "label": draft.label, "viewer": viewer, **out}
    if isinstance(draft, ReportDraft):
        fs = await _spec_of(draft, client, notes)
        analytic = bool(getattr(fs.action, "analytic_function", None)) if fs.action else False
        run_params = dict(draft.analytic_params if analytic else draft.parameters)
        run_params.update(params or {})
        out = await _run(draft.spec, fs, client, output_format or draft.output_format, run_params, max_rows, notes)
        return {"kind": "report", "label": draft.display_name, "spec": draft.spec, "viewer": viewer, **out}
    from pyegeria.view.dashboard_resolver import async_resolve_sheet
    sheet = await _sheet_for_resolver(draft, client, notes)
    resolved = await async_resolve_sheet(client, sheet, perspective=perspective, run=run,
                                         spec_lookup=_registry_lookup, fetch_missing=False)
    if not run:
        notes.append("placements resolved, not run (run=True runs them)")
    return {"kind": "sheet", "label": draft.name, "viewer": viewer, "capped": False, "shown": None,
            "result": resolved.model_dump(), "notes": notes}


def preview(draft: Any, *, client: Any, max_rows: int = 25, **kwargs: Any) -> Dict[str, Any]:
    from pyegeria.core.async_runner import run_sync
    return run_sync(async_preview(draft, client=client, max_rows=max_rows, **kwargs))
