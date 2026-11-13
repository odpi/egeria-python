# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Held artifacts: load one as a draft, read its history, plan its publish or withdraw, apply a plan.

Every Egeria read here uses the caller's `client`, signed in as the user; every write runs through the
caller's runner (`run(markdown, directive)`), as the user. This module never authenticates and never
uses a service account.
"""
from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Optional, Union

from loguru import logger

from pyegeria.authoring.models import (
    AuthoringGates, AuthoringRefused, ReportDraft, SheetDraft, SheetPlacement, SpecDraft, as_draft, default_gates,
)
from pyegeria.authoring.serialize import (
    DASHBOARD_FOLDER_PREFIX, FIND_PARAMETERS, PINNED_VERSION_KEY, SPEC_FOLDER_PREFIX, serialize,
)
from pyegeria.view.report_spec_publish import (
    PublishRefused, build_publish_document, build_withdraw_document, document_digest, run_document, section,
)

#: The consumers that have folders today (design note §1). A folder is `<prefix><consumer>`.
KNOWN_CONSUMERS = ("EgeriaAdvisor", "Jupyter", "MyEgeria", "Portal", "ResourceExplorer", "pyegeria")
RESTRICTED_LATER = "Restricted publish comes later, after the zone proof: publish as public for now."
PIN_REFUSED = "Pinning a spec version is switched off here (AuthoringGates.allow_pinning, D14)."
BUILTIN_REFUSED = ("'{label}' is a built-in spec: it ships with pyegeria and isn't published from here. "
                   "Copy it with new_from(prototype=('spec', '{label}'), new_label=...) and publish the copy.")


# ── Reading held artifacts, as the caller ─────────────────────────────────────

async def _by_qualified_name(client: Any, qn: str) -> Optional[Dict[str, Any]]:
    from md_processing.v2.report import find_element_by_qualified_name
    return await find_element_by_qualified_name(client, qn)


async def _report_element(client: Any, label: str) -> Optional[Dict[str, Any]]:
    """A Report by qualified name, else by exact display name (one Report must match)."""
    el = await _by_qualified_name(client, label)
    if el and _type_name(el) == "Report":
        return el
    found = await client.classification_manager._async_get_elements_by_property_value(
        label, ["displayName"], metadata_element_type="Report", starts_with=False, ends_with=False,
        ignore_case=False, page_size=25, graph_query_depth=0)
    matches = [e for e in found if isinstance(e, dict) and (e.get("properties") or {}).get("displayName") == label] \
        if isinstance(found, list) else []
    if len(matches) > 1:
        raise AuthoringRefused(f"{len(matches)} Reports are named {label!r}; give its qualified name.")
    return matches[0] if matches else None


def _type_name(el: Dict[str, Any]) -> str:
    return ((el.get("elementHeader") or {}).get("type") or {}).get("typeName", "")


def _version(el: Dict[str, Any]) -> Optional[int]:
    v = ((el.get("elementHeader") or {}).get("versions") or {}).get("version")
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def report_draft_from_element(el: Dict[str, Any]) -> ReportDraft:
    """A ReportDraft from a Report element. Parameters are read from the typed `reportParameters` first
    (D7), then from the camelCase additionalProperties keys; `notes` says which was read."""
    from md_processing.v2.report import _camel_to_snake
    props = el.get("properties") or {}
    extra = dict(props.get("additionalProperties") or {})
    notes: List[str] = []
    analytic: Dict[str, Any] = {}
    raw_analytic = extra.get("analyticParams")
    if raw_analytic:
        try:
            analytic = json.loads(raw_analytic) if isinstance(raw_analytic, str) else dict(raw_analytic)
        except (TypeError, ValueError):
            notes.append("analyticParams is not JSON; not read")
    params: Dict[str, Any] = {}
    pinned = extra.pop(PINNED_VERSION_KEY, None)
    try:
        pinned = int(pinned) if pinned not in (None, "") else None
    except (TypeError, ValueError):
        notes.append(f"{PINNED_VERSION_KEY} {pinned!r} is not a version number; following the latest version")
        pinned = None
    typed = props.get("reportParameters")
    if typed:
        try:
            doc = json.loads(typed) if isinstance(typed, str) else dict(typed)
            params = {k: v for k, v in doc.items() if k not in analytic}
            notes.append("parameters read from reportParameters")
        except (TypeError, ValueError):
            notes.append("reportParameters is not JSON; read the additionalProperties keys instead")
            typed = None
    if not typed:
        for key, value in extra.items():
            if key in ("reportSpec", "outputFormat", "analyticParams"):
                continue
            params[_camel_to_snake(key)] = _decode(value) if _camel_to_snake(key) in FIND_PARAMETERS else value
        notes.append("parameters read from the additionalProperties keys (no reportParameters)")
    return ReportDraft(display_name=props.get("displayName") or "", qualified_name=props.get("qualifiedName"),
                       description=props.get("description"), spec=extra.get("reportSpec") or "",
                       output_format=props.get("outputFormat") or extra.get("outputFormat") or "DICT",
                       parameters=params, analytic_params=analytic, pinned_version=pinned,
                       guid=(el.get("elementHeader") or {}).get("guid"),
                       base_version=_version(el), notes=notes)


def _decode(value: Any) -> Any:
    """A camelCase-copy value back to its type: "True" -> True, "25" -> 25, "['A']" / '["A"]' -> ["A"]."""
    if not isinstance(value, str):
        return value
    text = value.strip()
    if text in ("True", "False"):
        return text == "True"
    if text.lstrip("-").isdigit():
        return int(text)
    if text.startswith("[") and text.endswith("]"):
        try:
            return json.loads(text)
        except ValueError:
            import ast
            try:
                return list(ast.literal_eval(text))
            except (ValueError, SyntaxError):
                return value
    return value


def sheet_draft_from_sheet(sheet: Any) -> SheetDraft:
    """A SheetDraft from a sheet read from Egeria (pyegeria.view.dashboards.EgeriaDashboardSheet)."""
    notes = list(getattr(sheet, "breaks", None) or [])
    placements = []
    for i, p in enumerate(sheet.placements, start=1):
        kind = getattr(p, "kind", "report")
        if getattr(p, "note", None):
            notes.append(f"placement {i} ({p.ref}): {p.note}")
        if kind == "text" or p.content is not None:
            placements.append(SheetPlacement(text=p.content or "", name=p.ref, span=p.span, emphasis=p.emphasis,
                                             perspectives=list(p.perspectives or []), detail_spec=p.detail_spec))
        else:
            if kind == "missing":
                notes.append(f"placement {i} ({p.ref}): its Report link is missing in Egeria; kept by name")
            placements.append(SheetPlacement(report=p.ref, span=p.span, emphasis=p.emphasis,
                                             perspectives=list(p.perspectives or []), detail_spec=p.detail_spec))
    return SheetDraft(name=sheet.name, heading=sheet.heading, description=sheet.description or "",
                      family=sheet.family, placements=placements, guid=getattr(sheet, "guid", None), notes=notes)


async def async_load_held(kind: str, label: str, client: Any) -> Union[SpecDraft, ReportDraft, SheetDraft]:
    """The held artifact `label` as a draft, read from Egeria as the caller, with its Egeria version.
    - spec: the ReportSpec element `ReportSpec::<label>` (or `ReportType::<label>`), converted by the same
      code the spec cache uses;
    - report: a Report by qualified name or exact display name;
    - sheet: `Dashboard::<label>` and its element chain.
    Not held, or not visible to this user, is refused in words."""
    if client is None:
        raise AuthoringRefused("Reading a held artifact reads Egeria as you: a client is needed.")
    if kind == "spec":
        from md_processing.v2.report import find_report_spec_element
        from pyegeria.view.egeria_spec_cache import _Skip, _build
        el = await find_report_spec_element(client, label)
        if not el:
            raise AuthoringRefused(f"Egeria holds no report spec {label!r} that you can see.")
        try:
            built = _build(el, folders=[], identity=getattr(client, "user_id", "") or "")
        except _Skip as exc:
            raise AuthoringRefused(f"Report spec {label!r} is held but can't be read as a spec: {exc.reason}")
        return SpecDraft(label=built.label, format_set=built.format_set, guid=built.guid,
                         qualified_name=built.provenance.get("qualified_name"),
                         base_version=built.provenance.get("header_version"), notes=list(built.notes))
    if kind == "report":
        el = await _report_element(client, label)
        if not el:
            raise AuthoringRefused(f"Egeria holds no Report {label!r} that you can see.")
        return report_draft_from_element(el)
    if kind == "sheet":
        from pyegeria.view.dashboards import read_sheet_from_chain
        sheet = await read_sheet_from_chain(client, label)
        if sheet is None:
            raise AuthoringRefused(f"Egeria holds no dashboard sheet {label!r} (Dashboard::{label}) that you can see.")
        draft = sheet_draft_from_sheet(sheet)
        dash = await _by_qualified_name(client, f"Dashboard::{label}")
        draft.base_version = _version(dash) if dash else None
        return draft
    raise AuthoringRefused(f"A held artifact is a spec, report or sheet, not {kind!r}.")


def load_held(kind: str, label: str, client: Any):
    from pyegeria.core.async_runner import run_sync
    return run_sync(async_load_held(kind, label, client))


async def async_history(kind: str, label: str, client: Any) -> Dict[str, Any]:
    """The held artifact's versions from Egeria, newest first: {version, update_time, updated_by, ...}.
    Read only. When Egeria's history can't be read, `read` is False and `why` says so (no empty list
    standing for "no history")."""
    draft = await async_load_held(kind, label, client)
    out: Dict[str, Any] = {"kind": kind, "label": label, "guid": draft.guid, "current_version": draft.base_version,
                           "versions": [], "read": False, "why": None}
    if not draft.guid:
        out["why"] = "the held element has no GUID to read history for"
        return out
    try:
        raw = await client.metadata_expert._async_get_element_history(draft.guid, oldest_first=False,
                                                                      page_size=50)
    except Exception as exc:  # noqa: BLE001 -- said, not raised: the current version is still known
        out["why"] = f"Egeria's history could not be read: {type(exc).__name__}: {' '.join(str(exc).split())[:200]}"
        return out
    items = raw if isinstance(raw, list) else []
    if not isinstance(raw, list):
        out["why"] = f"Egeria answered {str(raw)[:120]!r}, not a list of versions"
        return out
    from pyegeria.authoring.versions import as_element
    for el in items:
        versions = (as_element(el or {}).get("elementHeader") or {}).get("versions") or {}
        out["versions"].append({"version": versions.get("version"), "update_time": versions.get("updateTime"),
                                "updated_by": versions.get("updatedBy"), "create_time": versions.get("createTime"),
                                "created_by": versions.get("createdBy")})
    out["read"] = True
    out["capped"] = len(items) >= 50
    if out["capped"]:
        out["why"] = "the 50 newest versions are shown; older ones were not read"
    return out


def history(kind: str, label: str, client: Any) -> Dict[str, Any]:
    from pyegeria.core.async_runner import run_sync
    return run_sync(async_history(kind, label, client))


# ── Plans ─────────────────────────────────────────────────────────────────────

def check_folders(folders: Iterable[str], prefix: str, *, action: str = "Publish") -> List[str]:
    """The consumer folders, each `<prefix><known consumer>`; any other is refused in words."""
    out: List[str] = []
    for f in folders or []:
        if f not in out:
            out.append(f)
    if not out:
        raise AuthoringRefused(f"{action} needs at least one consumer folder ({prefix}<consumer>).")
    allowed = [prefix + c for c in KNOWN_CONSUMERS]
    bad = [f for f in out if f not in allowed]
    if bad:
        raise AuthoringRefused(f"Unknown consumer folder: {', '.join(bad)}. The folders are {', '.join(allowed)}.")
    return out


def _is_builtin(label: str) -> bool:
    from pyegeria.view.base_report_formats import lookup_report_spec
    try:
        return lookup_report_spec(label)[1] == "builtin"
    except Exception:  # noqa: BLE001 -- unknown is not built-in
        return False


def _plan(kind: str, label: str, qn: str, markdown: str, steps: List[str], **extra: Any) -> Dict[str, Any]:
    return {"kind": kind, "label": label, "qualified_name": qn, "markdown": markdown,
            "digest": document_digest(markdown), "steps": steps, **extra}


def publish_plan(draft: Any, *, folders: Iterable[str] = (), visibility: str = "public",
                 held: Optional[Dict[str, Any]] = None, gates: Optional[AuthoringGates] = None) -> Dict[str, Any]:
    """The document that publishes a draft, its digest, and its steps in words.

    - spec: `report_spec_publish.build_publish_document` into ReportSpecFolder::Consumer::<X> folders;
    - report: its Create Report block (a Report is placed on a sheet, not filed in a folder);
    - sheet: its sheet commands, then Add Member to Collection into DashboardFolder::Consumer::<X>.
    Refused in words: restricted publish (after the zone proof), built-in specs, unknown folders, a pinned
    spec version (D14), a sheet target other than Egeria (D4)."""
    draft = as_draft(draft)
    gates = gates or default_gates()
    if visibility != "public":
        raise AuthoringRefused(RESTRICTED_LATER)
    try:
        if isinstance(draft, SpecDraft):
            if _is_builtin(draft.label):
                raise AuthoringRefused(BUILTIN_REFUSED.format(label=draft.label))
            folders = check_folders(folders, SPEC_FOLDER_PREFIX)
            plan = build_publish_document(draft.label, draft.format_set, folders=folders, held=held)
            return {**plan, "kind": "spec"}
        if isinstance(draft, ReportDraft):
            if draft.pinned_version is not None and not gates.allow_pinning:
                raise AuthoringRefused(PIN_REFUSED)
            if list(folders or []):
                raise AuthoringRefused("A Report isn't filed in a consumer folder: publish the sheet that places it.")
            from pyegeria.authoring.serialize import report_rows
            promoting = bool((held or {}).get("zones"))
            markdown = f"# Report {draft.display_name}\n\n" + section(
                "Create Report", report_rows(draft, marker="published" if promoting else None))
            qn = draft.qualified_name or f"(derived from the display name {draft.display_name!r})"
            steps = [f"create or update the Report {draft.display_name!r} running spec {draft.spec!r} "
                     f"({draft.output_format}"
                     + (f", pinned at version {draft.pinned_version}" if draft.pinned_version else ", latest version")
                     + f"), with {len(draft.parameters)} parameter(s) written out"]
            markdown, steps = _declassify(markdown, steps, draft.qualified_name or draft.display_name, held)
            return _plan("report", draft.display_name, qn, markdown, steps)
        if gates.sheet_target != "egeria":
            raise AuthoringRefused("Sheets are written to Egeria only (D4).")
        folders = check_folders(folders, DASHBOARD_FOLDER_PREFIX)
        qn = f"Dashboard::{draft.name}"
        blocks = [serialize(draft, title=f"# Publish dashboard sheet {draft.name}")]
        blocks += [section("Add Member to Collection", [("Element Id", qn), ("Collection Id", f)]) for f in folders]
        steps = [f"create or update the sheet {qn} with {len(draft.placements)} placement(s), in order"]
        if (held or {}).get("zones"):
            blocks.insert(1, section("Declassify Zone Membership", [("Target Element", qn)]))
            steps.append(f"remove its zones ({', '.join(held['zones'])}): the draft becomes public")
        steps += [f"add it to {f}" for f in folders]
        markdown = "\n".join(blocks)
        return _plan("sheet", draft.name, qn, markdown, steps, folders=folders)
    except PublishRefused as exc:
        raise AuthoringRefused(str(exc)) from exc


def _declassify(markdown: str, steps: List[str], target: str, held: Optional[Dict[str, Any]]):
    """Promotion of a private draft: clear its zones (Declassify Zone Membership) after the Create."""
    if not (held or {}).get("zones"):
        return markdown, steps
    markdown += "\n" + section("Declassify Zone Membership", [("Target Element", target)])
    return markdown, steps + [f"remove its zones ({', '.join(held['zones'])}): the draft becomes public"]


def withdraw_plan(kind: str, label: str, *, folders: Iterable[str]) -> Dict[str, Any]:
    """Remove a published spec or sheet from consumer folders (the element itself stays in Egeria)."""
    try:
        if kind == "spec":
            folders = check_folders(folders, SPEC_FOLDER_PREFIX, action="Withdraw")
            return {**build_withdraw_document(label, folders), "kind": "spec"}
        if kind == "sheet":
            folders = check_folders(folders, DASHBOARD_FOLDER_PREFIX, action="Withdraw")
            qn = f"Dashboard::{label}"
            blocks = [f"# Withdraw dashboard sheet {label}\n"]
            blocks += [section("Remove Member from Collection", [("Element Id", qn), ("Collection Id", f)])
                       for f in folders]
            return _plan("sheet", label, qn, "\n".join(blocks),
                         [f"remove {qn} from {f} (the sheet itself stays in Egeria)" for f in folders],
                         folders=folders)
    except PublishRefused as exc:
        raise AuthoringRefused(str(exc)) from exc
    if kind == "report":
        raise AuthoringRefused("A Report isn't in a consumer folder: withdraw the sheet that places it.")
    raise AuthoringRefused(f"Withdraw works on a spec or a sheet, not {kind!r}.")


def apply(plan: Dict[str, Any], *, step: str, run: Any = None, confirmed: bool = False,
          digest: Optional[str] = None) -> Dict[str, Any]:
    """One step of a plan: preview (nothing runs), validate (Dr.Egeria validate, as the user), or process
    (refused unless confirmed and the digest is the previewed plan's). report_spec_publish.run_document."""
    try:
        return run_document(plan, step=step, run=run, confirmed=confirmed, digest=digest)
    except PublishRefused as exc:
        raise AuthoringRefused(str(exc)) from exc
