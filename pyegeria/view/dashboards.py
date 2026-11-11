"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Dashboard sheets held in Egeria: the reader, and the migration from the local JSON store
(report-spec pipeline note v5.5 §8d / §10.6(c); BRIEF RS-DASH PR-2).

    load_dashboard_sheet(name)   -> the sheet, read from its Egeria element chain, or None
    list_dashboard_sheets()      -> the sheets in the configured dashboard folders; with none configured,
                                    every sheet held in Egeria (Dashboard::* elements), and it says so
    read_dashboard_consumer_index() -> {sheet: [consumer, ...]} over the dashboard folder tree

Dashboard folders (LD-1) mirror report-spec consumer folders: a root `RootCollection::DashboardSheets`
(PYEGERIA_DASHBOARD_ROOT) holds one `DashboardFolder::Consumer::<App>` CollectionFolder per consumer
(Portal, EgeriaAdvisor, ...), sub-folders allowed; a sheet's `Dashboard` element is the member, and one
sheet may sit in several consumer folders. Which folders a listing takes: PYEGERIA_DASHBOARD_FOLDERS
(comma-separated), else config.json's "Pyegeria Dashboard Folders". The walk is egeria_folders', the
same one the report-spec cache uses.

Both return today's `DashboardSheet` / `Placement` model, so a consumer keeps its code. The objects are the
subclasses `EgeriaDashboardSheet` / `EgeriaPlacement`, which add only what an Egeria-held sheet must say:
`source` ("egeria"), a placement's `kind` ("report" / "text" / "missing") and `note`, and a sheet's `breaks`.
`as_local_model()` drops those, giving a plain `DashboardSheet` that compares equal to the JSON record it
was written from.

Absence and drift are said in words, never as an empty value:
  - a REPORT placement whose field exists but whose DataSetContent link is gone reads `kind: "missing"`,
    note "report link missing in Egeria" (its `ref` is the placement's name, so it can still be shown);
  - a sheet whose chain is broken (no layout schema, no sheet container) is listed with the break named
    in `breaks`, not dropped;
  - a placement whose stored perspective labels or drill-down name disagree with its ScopedBy /
    DataDescription links (edited in Egeria directly) gets a note naming the difference.

The chain is walked with the same primitives that write it (md_processing.v2.dashboard_sheet), so the
writer and the reader cannot disagree about its shape. Every Egeria read is bounded: page size 25,
graph_query_depth 0, paged until an empty page.

Command line (writes are shared writes: run them only with the owner's word and the Coordinator's CLEAR):

    python -m pyegeria.view.dashboards list
    python -m pyegeria.view.dashboards show NAME
    python -m pyegeria.view.dashboards migrate [--sheet NAME] [--rename NEW_NAME] [--store PATH] [--dry-run]
    python -m pyegeria.view.dashboards delete --sheet NAME [--dry-run] [--local]

`migrate` reads the JSON store and writes each sheet through PR-1's writer (one implementation); it is
idempotent by qualifiedName, and `--dry-run` lists every element it would create. It never writes the
store. `delete` removes a sheet's Egeria chain (never its Reports or ReportSpecs); `--local` also removes
the store record.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from typing import Any, Dict, List, Literal, Optional

from loguru import logger
from pydantic import Field

from md_processing.v2.dashboard_sheet import (
    DASHBOARD_QN_PREFIX, DashboardSheetEgeriaWriter, _default_store_path, _load_store, dashboard_qn,
    perspective_qualified_name, sheet_name_from_dashboard_qn,
)
from pyegeria.view import egeria_folders as _folders
from pyegeria.view._output_dashboard_sheet_models import DashboardSheet, DashboardSheetDict, Placement

__all__ = [
    "DASHBOARD_CONSUMER_PREFIX", "DASHBOARD_CONSUMERS_FORMAT", "DASHBOARD_FOLDERS_ENV", "DASHBOARD_ROOT_ENV",
    "DEFAULT_DASHBOARD_ROOT", "DashboardSheetListing", "EgeriaDashboardSheet", "EgeriaPlacement",
    "NO_FOLDERS_NOTE", "REPORT_LINK_MISSING", "as_local_model", "async_list_dashboard_sheets",
    "async_load_dashboard_sheet", "async_migrate_dashboard_sheets", "async_resolve_dashboard_sheet",
    "build_dashboard_consumer_index", "configured_dashboard_folders", "configured_dashboard_root",
    "list_dashboard_sheets", "load_dashboard_sheet", "main", "read_dashboard_consumer_index",
    "read_sheet_from_chain", "resolve_dashboard_sheet",
]

PAGE_SIZE = 25
REPORT_LINK_MISSING = "report link missing in Egeria"
_SPANS = ("1", "2", "full")
_STYLES = ("kpi", "panel")

DASHBOARD_ROOT_ENV = "PYEGERIA_DASHBOARD_ROOT"
DEFAULT_DASHBOARD_ROOT = "RootCollection::DashboardSheets"
DASHBOARD_CONSUMER_PREFIX = "DashboardFolder::Consumer::"
DASHBOARD_FOLDERS_ENV = "PYEGERIA_DASHBOARD_FOLDERS"
DASHBOARD_CONSUMERS_FORMAT = "pyegeria-dashboard-consumers/1"
NO_FOLDERS_NOTE = "no dashboard folders configured: listing every Dashboard:: sheet"


class EgeriaPlacement(Placement):
    """A Placement read from Egeria. `kind`: "report", "text", or "missing" (a report placement whose
    report link is gone); `note` says what is missing or odd, in words."""
    kind: Literal["report", "text", "missing"] = "report"
    note: Optional[str] = None
    source: str = "egeria"
    #: The Report's GUID: the linked one for a bound placement; for a "missing" one, the GUID the writer
    #: recorded on the field (`reportGUID`), if any, so the resolver can tell a Report the viewer may not
    #: see from one that is gone.
    report_guid: Optional[str] = None


class EgeriaDashboardSheet(DashboardSheet):
    """A DashboardSheet read from Egeria. `breaks` names each broken link of its element chain (empty when
    the chain is whole); `guid` is the Dashboard's."""
    source: str = "egeria"
    guid: Optional[str] = None
    breaks: List[str] = Field(default_factory=list)
    #: The configured dashboard folders the sheet was found in (empty for an unfiltered listing).
    folders: List[str] = Field(default_factory=list)
    #: The consumers those folders belong to (`DashboardFolder::Consumer::<App>`).
    used_by: List[str] = Field(default_factory=list)


class DashboardSheetListing(list):
    """The sheets a listing found (a plain list, so existing callers keep working), and how it read them.

    `notes` says what the reader should know: no folders configured, a folder not found or not readable,
    a sub-folder the walk could not read. `folders` has one entry per configured folder: its
    `qualifiedName`, `status` ("read", "partial", "not found", "not read"), `reason` and `sheets`. A
    folder that could not be read is never reported as an empty one."""

    def __init__(self, sheets: Any = (), *, notes: Optional[List[str]] = None,
                 folders: Optional[List[Dict[str, Any]]] = None) -> None:
        super().__init__(sheets)
        self.notes: List[str] = list(notes or [])
        self.folders: List[Dict[str, Any]] = list(folders or [])


def as_local_model(sheet: DashboardSheet) -> DashboardSheet:
    """The plain DashboardSheet / Placement form of a sheet (Egeria-only fields dropped), as the JSON store
    holds it. A whole Egeria sheet compares equal to the record it was written from."""
    base_fields = set(Placement.model_fields)
    placements = [Placement(**{k: v for k, v in (p if isinstance(p, dict) else p.model_dump()).items()
                               if k in base_fields}) for p in sheet.placements]
    return DashboardSheet(name=sheet.name, heading=sheet.heading, description=sheet.description,
                          aliases=list(sheet.aliases), family=sheet.family, placements=placements)


# ---------------------------------------------------------------------------- reading

def _split_labels(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [p.strip() for p in str(value or "").split(",") if p.strip()]


async def _scoped_by_qns(writer: DashboardSheetEgeriaWriter, field_guid: str) -> List[str]:
    """qualifiedNames of the Perspectives linked to a placement by ScopedBy."""
    return [(e.get("properties") or {}).get("qualifiedName") or ""
            for e in await writer._related(field_guid, "ScopedBy", start_at_end=2)
            if writer._type(e) == "Perspective"]


async def _data_descriptions(writer: DashboardSheetEgeriaWriter, field_guid: str) -> List[Dict[str, Any]]:
    return [e.get("properties") or {} for e in await writer._related(field_guid, "DataDescription", start_at_end=1)]


def _perspective_drift(labels: List[str], linked_qns: List[str]) -> List[str]:
    """Where the stored labels and the ScopedBy links disagree (someone edited one in Egeria), in words."""
    expected = {perspective_qualified_name(label): label for label in labels}
    notes = []
    unlinked = [label for qn, label in expected.items() if qn not in linked_qns]
    extra = [qn for qn in linked_qns if qn not in expected]
    if unlinked:
        notes.append(f"stored perspective(s) {', '.join(unlinked)} have no ScopedBy link in Egeria")
    if extra:
        notes.append(f"ScopedBy link(s) to {', '.join(extra)} are not in the stored perspectives")
    return notes


def _detail_drift(stored: Optional[str], linked: List[Dict[str, Any]]) -> List[str]:
    """A DataDescription link that the stored drill-down name does not explain. A stored name with no link is
    not drift: a spec held only in pyegeria has no element to link to."""
    names = []
    for props in linked:
        qn = props.get("qualifiedName") or ""
        names.append((props.get("displayName"), qn, qn.split("::", 1)[1] if "::" in qn else qn))
    if not names:
        return []
    if stored and any(stored in n for n in names):
        return []
    shown = ", ".join(n[1] or n[0] or "?" for n in names)
    return [f"DataDescription links to {shown}, but the stored drill-down is {stored or 'none'}"]


async def read_sheet_from_chain(client: Any, sheet_name: str,
                                dashboard: Optional[Dict[str, Any]] = None) -> Optional[EgeriaDashboardSheet]:
    """Read one sheet by walking its Egeria chain. None if there is no `Dashboard::<sheet_name>`."""
    writer = DashboardSheetEgeriaWriter(client)
    chain = await writer.find_chain(sheet_name)
    if not chain.dashboard_guid:
        return None
    props = (chain.dashboard or dashboard or {}).get("properties") or {}
    extra = props.get("additionalProperties") or {}
    sheet = EgeriaDashboardSheet(
        name=sheet_name, heading=props.get("displayName") or sheet_name,
        description=props.get("description") or "", aliases=list(props.get("aliases") or []),
        family=extra.get("family") or None, guid=chain.dashboard_guid)

    if not chain.schema_type_guid:
        sheet.breaks.append("no layout schema: the Dashboard has no Schema link to a DisplayDataSchemaType")
        return sheet
    if not chain.container_guid:
        sheet.breaks.append("no sheet container: the DisplayDataSchemaType has no AttributeForSchema link to a "
                            "DisplayDataContainer")
        return sheet

    fields = await writer.list_fields(chain.container_guid)
    bindings: Dict[str, Dict[str, Any]] = {}
    report_qns = [f.qualified_name for f in fields if (f.properties.get("placementKind") or "report") != "text"]
    if report_qns:
        bindings = await client.asset_maker._async_get_placement_reports(chain.dashboard_guid, report_qns) or {}

    for f in fields:
        fp = f.properties
        f_extra = fp.get("additionalProperties") or {}
        notes: List[str] = []
        if f.position is None:
            notes.append("no position on its NestedSchemaAttribute link; shown last")
        span = str(fp.get("span") or "1")
        if span not in _SPANS:
            notes.append(f"span '{span}' is not one of {', '.join(_SPANS)}; shown as 1")
            span = "1"
        style = str(fp.get("presentationStyle") or "kpi")
        if style not in _STYLES:
            notes.append(f"presentationStyle '{style}' is not one of {', '.join(_STYLES)}; shown as kpi")
            style = "kpi"
        # The labels and drill-down name stored on the field are what the author wrote; the ScopedBy /
        # DataDescription links carry the graph meaning. Read both, and say where they disagree.
        linked_qns = await _scoped_by_qns(writer, f.guid)
        if "perspectives" in f_extra:
            perspectives = _split_labels(f_extra.get("perspectives"))
            notes += _perspective_drift(perspectives, linked_qns)
        else:
            perspectives = [qn.split("::", 1)[1] if qn.startswith("Perspective::") else qn for qn in linked_qns]
        linked_specs = await _data_descriptions(writer, f.guid)
        detail_spec = f_extra.get("detailSpec") or None
        if "detailSpec" in f_extra or "placementName" in f_extra:
            notes += _detail_drift(detail_spec, linked_specs)
        if detail_spec is None and linked_specs:
            detail_spec = linked_specs[0].get("displayName") or linked_specs[0].get("qualifiedName")

        kind = fp.get("placementKind") or "report"
        if kind == "text":
            content = fp.get("markdownContent")
            if content is None:
                notes.append("text placement with no markdownContent in Egeria")
                content = ""
            placement = EgeriaPlacement(ref=f.display_name, span=span, emphasis=style, content=content,
                                        perspectives=perspectives, detail_spec=detail_spec, kind="text")
        else:
            binding = bindings.get(f.qualified_name) or {"state": "unbound", "links": []}
            if binding.get("state") == "bound" and binding.get("report_name"):
                placement = EgeriaPlacement(ref=binding["report_name"], span=span, emphasis=style,
                                            perspectives=perspectives, detail_spec=detail_spec, kind="report",
                                            report_guid=binding.get("report_guid"))
            else:
                if binding.get("state") == "ambiguous":
                    notes.insert(0, f"{len(binding['links'])} reports are linked to this placement in Egeria; "
                                    f"none is chosen")
                else:
                    notes.insert(0, REPORT_LINK_MISSING)
                placement = EgeriaPlacement(ref=f.display_name, span=span, emphasis=style,
                                            perspectives=perspectives, detail_spec=detail_spec, kind="missing",
                                            report_guid=f_extra.get("reportGUID") or None)
        if notes:
            placement.note = "; ".join(notes)
        sheet.placements.append(placement)
    return sheet


async def async_load_dashboard_sheet(client: Any, name: str) -> Optional[EgeriaDashboardSheet]:
    """The Egeria-held sheet `name` (its Dashboard is `Dashboard::<name>`), or None."""
    return await read_sheet_from_chain(client, name)


async def _dashboard_elements(client: Any) -> List[Dict[str, Any]]:
    """Every Dashboard whose qualifiedName starts `Dashboard::`. Read by type in pages of 25 (Dashboard is a
    small type; only an empty page ends the read) and filtered here: a starts-with search on qualifiedName
    took 21 s on the live platform with no Dashboards at all, the type read 2.8 s."""
    out: List[Dict[str, Any]] = []
    seen: set = set()
    start = 0
    while True:
        page = await client.classification_manager._async_get_elements(
            "Dashboard", start_from=start, page_size=PAGE_SIZE, graph_query_depth=0)
        items = [e for e in page if isinstance(e, dict) and e.get("elementHeader")] if isinstance(page, list) else []
        if not items:
            return out
        fresh = [e for e in items if (e.get("elementHeader") or {}).get("guid") not in seen]
        if not fresh:   # a page of elements already read: paging did not advance, and would never end (6.2.36)
            logger.warning(f"dashboards: paging did not advance at position {start}; stopped with {len(seen)} read")
            return out
        seen.update((e.get("elementHeader") or {}).get("guid") for e in fresh)
        items = fresh
        out.extend(e for e in items
                   if ((e.get("properties") or {}).get("qualifiedName") or "").startswith(DASHBOARD_QN_PREFIX))
        start += len(items)


async def _all_sheets(client: Any) -> List[EgeriaDashboardSheet]:
    sheets: List[EgeriaDashboardSheet] = []
    seen = set()
    for element in await _dashboard_elements(client):
        name = sheet_name_from_dashboard_qn((element.get("properties") or {}).get("qualifiedName") or "")
        if not name or name in seen:
            continue
        seen.add(name)
        sheet = await read_sheet_from_chain(client, name, dashboard=element)
        if sheet is not None:
            sheets.append(sheet)
    sheets.sort(key=lambda s: s.name.lower())
    return sheets


def configured_dashboard_folders() -> List[str]:
    """The folders a listing takes: PYEGERIA_DASHBOARD_FOLDERS (comma-separated qualified names), else
    config.json's "Pyegeria Dashboard Folders". Empty by default."""
    env_val = os.getenv(DASHBOARD_FOLDERS_ENV)
    if env_val is not None:
        return [p.strip() for p in env_val.split(",") if p.strip()]
    try:
        from pyegeria.core.config import settings
        return list(getattr(settings.Environment, "pyegeria_dashboard_folders", None) or [])
    except Exception:  # noqa: BLE001 -- settings may not load in every context; then nothing is configured
        return []


def configured_dashboard_root() -> str:
    """The root of the dashboard folder tree: PYEGERIA_DASHBOARD_ROOT, else RootCollection::DashboardSheets."""
    return (os.getenv(DASHBOARD_ROOT_ENV) or "").strip() or DEFAULT_DASHBOARD_ROOT


def _is_dashboard_member(el: Dict[str, Any]) -> bool:
    """A sheet's Dashboard element: type Dashboard, qualifiedName Dashboard::<sheet>."""
    qn = (el.get("properties") or {}).get("qualifiedName") or ""
    return "Dashboard" in _folders._type_names(el) and bool(sheet_name_from_dashboard_qn(qn))


def _used_by(folder: Dict[str, Any]) -> List[str]:
    """The consumer a configured folder belongs to: its own name if it is a consumer folder, the consumer
    segment of its qualified name if it is a sub-folder of one, else none."""
    qn = (folder.get("properties") or {}).get("qualifiedName") or ""
    if _folders.is_top_consumer_qn(qn, DASHBOARD_CONSUMER_PREFIX):
        return [_folders.consumer_name(folder, DASHBOARD_CONSUMER_PREFIX)]
    if _folders.is_consumer_qn(qn, DASHBOARD_CONSUMER_PREFIX):
        return [qn[len(DASHBOARD_CONSUMER_PREFIX):].split("::", 1)[0]]
    return []


def _walk_dashboard_folders(client: Any, folder_qns: List[str], depth_cap: int):
    """Read each configured folder (recursively, inside its consumer) and gather its Dashboard members.
    Synchronous, like the report-spec cache's walk: callers in a loop run it in a worker thread.

    Returns ({sheet name: {"element", "folders", "used_by"}}, notes, per-folder status)."""
    found: Dict[str, Dict[str, Any]] = {}
    notes: List[str] = []
    status: List[Dict[str, Any]] = []
    identity = _folders.client_identity(client)
    stop = [configured_dashboard_root()]
    for qn in folder_qns:
        entry: Dict[str, Any] = {"qualifiedName": qn, "status": "read", "reason": None, "sheets": 0}
        status.append(entry)
        try:
            folder = _folders.find_folder(client, qn)
        except Exception as exc:  # noqa: BLE001 -- one folder failing must not hide the others
            entry.update(status="not read", reason=f"could not be read: {exc}")
            notes.append(f"{qn}: {entry['reason']}")
            continue
        if folder is None:
            entry.update(status="not found", reason=f"not found, or not visible to {identity}")
            notes.append(f"{qn}: {entry['reason']}")
            continue
        try:
            walk = _folders.walk_folder(client, folder, recursive=True, consumer_prefix=DASHBOARD_CONSUMER_PREFIX,
                                        depth_cap=depth_cap, stop_qns=stop, member=_is_dashboard_member)
        except Exception as exc:  # noqa: BLE001
            entry.update(status="not read", reason=f"its members could not be read: {exc}")
            notes.append(f"{qn}: {entry['reason']}")
            continue
        problems = [f"{p}: {e}" for p, e in walk.errors]
        if walk.capped:
            problems.append(f"depth cap reached ({depth_cap} levels); not read: " + ", ".join(walk.capped))
        if problems:
            entry.update(status="partial", reason="; ".join(problems))
            notes.append(f"{qn}: not fully read: {entry['reason']}")
        notes.extend(f"{qn}: {p} not visible or not found" for p, _e in walk.gone)
        used_by = _used_by(folder)
        names = set()
        for m in walk.members:
            name = sheet_name_from_dashboard_qn((m.get("properties") or {}).get("qualifiedName") or "")
            hit = found.setdefault(name, {"element": m, "folders": [], "used_by": []})
            if qn not in hit["folders"]:
                hit["folders"].append(qn)
            hit["used_by"].extend(u for u in used_by if u not in hit["used_by"])
            names.add(name)
        entry["sheets"] = len(names)
    return found, notes, status


async def async_list_dashboard_sheets(client: Any, folders: Optional[List[str]] = None, *,
                                      depth_cap: int = _folders.DEPTH_CAP) -> DashboardSheetListing:
    """The sheets held in Egeria, by name, as a DashboardSheetListing.

    `folders` (else `configured_dashboard_folders()`): only the sheets in those CollectionFolders, followed
    recursively inside their consumer folder, each tagged with `folders` and `used_by`; a folder not found
    or not readable is named in `notes` and `folders`, never shown as empty. With no folders: every
    `Dashboard::` sheet, as before, and `notes` says that is what it is. A Dashboard whose chain is broken
    (for example one made with plain `Create Dashboard`) is listed with its `breaks`, not dropped."""
    chosen = configured_dashboard_folders() if folders is None else [f for f in folders if f]
    if not chosen:
        return DashboardSheetListing(await _all_sheets(client), notes=[NO_FOLDERS_NOTE])
    found, notes, status = await asyncio.to_thread(_walk_dashboard_folders, client, chosen, depth_cap)
    sheets: List[EgeriaDashboardSheet] = []
    for name in sorted(found, key=str.lower):
        hit = found[name]
        sheet = await read_sheet_from_chain(client, name, dashboard=hit["element"])
        if sheet is None:
            notes.append(f"{name}: in {', '.join(hit['folders'])}, but its Dashboard could not be read")
            continue
        sheet.folders, sheet.used_by = list(hit["folders"]), sorted(hit["used_by"])
        sheets.append(sheet)
    return DashboardSheetListing(sheets, notes=notes, folders=status)


def _sheet_key(m: Dict[str, Any], consumer: str, notes: List[str]) -> Optional[str]:
    return sheet_name_from_dashboard_qn((m.get("properties") or {}).get("qualifiedName") or "")


def build_dashboard_consumer_index(client: Any, *, root: Optional[str] = None,
                                   depth_cap: int = _folders.DEPTH_CAP) -> Dict[str, Any]:
    """Read the dashboard folder tree once: `{sheet: [consumer, ...]}` with how it was read, in the shape of
    the report-spec consumer index (`status` read / partial / not read, `consumers`, `notes`; each consumer
    entry counts its `sheets`). A tree that could not be read is "not read" with a reason, never empty."""
    return _folders.read_consumer_tree(client, root_qn=root or configured_dashboard_root(),
                                       consumer_prefix=DASHBOARD_CONSUMER_PREFIX, key=_sheet_key,
                                       fmt=DASHBOARD_CONSUMERS_FORMAT, depth_cap=depth_cap,
                                       member=_is_dashboard_member, count_field="sheets")


def _client_from_env() -> Any:
    """An EgeriaTech client from the environment (EGERIA_VIEW_SERVER, EGERIA_VIEW_SERVER_URL or
    EGERIA_PLATFORM_URL, EGERIA_USER / EGERIA_USER_PASSWORD, else pyegeria's settings), not yet signed in."""
    from pyegeria import EgeriaTech
    from pyegeria.core.config import resolve_egeria_credentials, settings
    server = os.environ.get("EGERIA_VIEW_SERVER") or settings.Environment.egeria_view_server
    url = (os.environ.get("EGERIA_VIEW_SERVER_URL") or os.environ.get("EGERIA_PLATFORM_URL")
           or settings.Environment.egeria_view_server_url)
    user, pwd = resolve_egeria_credentials()
    return EgeriaTech(server, url, user, pwd)


async def _signed_in_client() -> Any:
    client = _client_from_env()
    await client._async_create_egeria_bearer_token(client.user_id, client.user_pwd)
    return client


def load_dashboard_sheet(name: str, client: Any = None) -> Optional[EgeriaDashboardSheet]:
    """Sync form of async_load_dashboard_sheet. With no client, one is made from the environment."""
    from pyegeria.core.async_runner import run_sync

    async def _go():
        return await async_load_dashboard_sheet(client or await _signed_in_client(), name)
    return run_sync(_go())


def list_dashboard_sheets(client: Any = None, folders: Optional[List[str]] = None) -> DashboardSheetListing:
    """Sync form of async_list_dashboard_sheets. With no client, one is made from the environment."""
    from pyegeria.core.async_runner import run_sync

    async def _go():
        return await async_list_dashboard_sheets(client or await _signed_in_client(), folders)
    return run_sync(_go())


def read_dashboard_consumer_index(client: Any = None, *, root: Optional[str] = None,
                                  depth_cap: int = _folders.DEPTH_CAP) -> Dict[str, Any]:
    """The dashboard consumer index, read from Egeria now (sheets have no local cache to read it from).
    With no client, one is made from the environment; a failure to sign in is "not read", with its reason."""
    if client is None:
        from pyegeria.core.async_runner import run_sync
        try:
            client = run_sync(_signed_in_client())
        except Exception as exc:  # noqa: BLE001 -- said in the result, never an empty index
            return {"format": DASHBOARD_CONSUMERS_FORMAT, "root": root or configured_dashboard_root(),
                    "status": "not read", "reason": f"could not sign in to Egeria: {exc}", "consumers": [],
                    "index": {}, "notes": []}
    return build_dashboard_consumer_index(client, root=root, depth_cap=depth_cap)


# ---------------------------------------------------------------------------- the data step (B4 / D4)

async def async_resolve_dashboard_sheet(client: Any, name: str, **kwargs: Any):
    """The shared dashboard data step; see pyegeria.view.dashboard_resolver."""
    from pyegeria.view.dashboard_resolver import async_resolve_dashboard_sheet as _resolve
    return await _resolve(client, name, **kwargs)


def resolve_dashboard_sheet(client: Any, name: str, **kwargs: Any):
    """Sync form of async_resolve_dashboard_sheet; see pyegeria.view.dashboard_resolver."""
    from pyegeria.view.dashboard_resolver import resolve_dashboard_sheet as _resolve
    return _resolve(client, name, **kwargs)


# ---------------------------------------------------------------------------- migration

async def async_migrate_dashboard_sheets(client: Any, sheets: DashboardSheetDict, *,
                                         only: Optional[str] = None, rename: Optional[str] = None,
                                         dry_run: bool = False,
                                         owner: Optional[str] = None) -> Dict[str, DashboardSheetEgeriaWriter]:
    """Write sheets from the JSON store to Egeria through the PR-1 writer, one writer per sheet (so each
    sheet's actions and notes stay apart). Idempotent by qualifiedName. Never writes the store.

    `only` picks one sheet; `rename` writes it under another name (a scratch copy, e.g. for a live test).
    DB-3: the sheets are shared (default zone) and owned by `owner`, by default the client's user.
    """
    if rename and not only:
        raise ValueError("--rename needs --sheet: it renames one sheet")
    if owner is None:
        owner = getattr(client, "user_id", None)
    selected = [sheets[only]] if only else list(sheets.values())
    results: Dict[str, DashboardSheetEgeriaWriter] = {}
    for sheet in selected:
        target = sheet.model_copy(deep=True)
        if rename:
            target.name = rename
        writer = DashboardSheetEgeriaWriter(client, dry_run=dry_run)
        chain = await writer.write_sheet(target)
        if owner:
            await _ensure_ownership(writer, chain.dashboard_guid, dashboard_qn(target.name), owner)
        results[target.name] = writer
    return results


async def _ensure_ownership(writer: DashboardSheetEgeriaWriter, dashboard_guid: Optional[str], qn: str,
                            owner: str) -> None:
    """DB-3: a migrated sheet is owned by the user who migrates it. The one implementation is
    `DashboardSheetEgeriaWriter.ensure_ownership`, which `Create Dashboard Sheet` uses too."""
    await writer.ensure_ownership(dashboard_guid, qn, owner)


# ---------------------------------------------------------------------------- command line

def _print_actions(name: str, writer: DashboardSheetEgeriaWriter, dry_run: bool) -> None:
    changed = [a for a in writer.actions if not a.startswith("unchanged")]
    title = "would make" if dry_run else "made"
    print(f"\n== {name}: {title} {len(changed)} change(s), {len(writer.actions) - len(changed)} unchanged")
    for action in writer.actions:
        print(f"   {'(dry run) ' if dry_run and not action.startswith('unchanged') else ''}{action}")
    for note in writer.notes:
        print(f"   NOTE: {note}")


def _print_sheet(sheet: EgeriaDashboardSheet) -> None:
    print(f"{sheet.name} | {sheet.heading} | {len(sheet.placements)} placement(s)"
          + (f" | BROKEN: {'; '.join(sheet.breaks)}" if sheet.breaks else ""))
    for i, p in enumerate(sheet.placements, start=1):
        print(f"   {i:>2}. [{p.kind}] {p.ref} (span {p.span}, {p.emphasis})"
              + (f" perspectives={','.join(p.perspectives)}" if p.perspectives else "")
              + (f" detail={p.detail_spec}" if p.detail_spec else "")
              + (f"  -- {p.note}" if p.note else ""))


async def _amain(args: argparse.Namespace) -> int:
    client = await _signed_in_client()
    if args.command == "list":
        for sheet in await async_list_dashboard_sheets(client):
            _print_sheet(sheet)
        return 0
    if args.command == "show":
        sheet = await async_load_dashboard_sheet(client, args.name)
        if sheet is None:
            print(f"No dashboard sheet '{args.name}' in Egeria (looked for {dashboard_qn(args.name)}).")
            return 1
        _print_sheet(sheet)
        return 0
    if args.command == "migrate":
        store = args.store or _default_store_path()
        sheets = _load_store(store)
        if args.sheet and args.sheet not in sheets:
            print(f"No sheet '{args.sheet}' in {store}.")
            return 1
        print(f"Migrating from {store}{' (DRY RUN: nothing is written)' if args.dry_run else ''}")
        results = await async_migrate_dashboard_sheets(client, sheets, only=args.sheet, rename=args.rename,
                                                       dry_run=args.dry_run, owner=args.owner)
        for name, writer in results.items():
            _print_actions(name, writer, args.dry_run)
        return 0
    if args.command == "delete":
        writer = DashboardSheetEgeriaWriter(client, dry_run=args.dry_run)
        found = await writer.delete_sheet(args.sheet)
        if not found:
            print(f"No dashboard sheet '{args.sheet}' in Egeria (looked for {dashboard_qn(args.sheet)}).")
        else:
            _print_actions(args.sheet, writer, args.dry_run)
        if args.local and not args.dry_run:
            store = args.store or _default_store_path()
            sheets = _load_store(store)
            if args.sheet in sheets.keys():
                del sheets[args.sheet]
                sheets.save_to_json(store)
                print(f"Removed '{args.sheet}' from {store}.")
        return 0 if found else 1
    return 2


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m pyegeria.view.dashboards",
                                     description="Dashboard sheets held in Egeria: read, migrate, delete.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="list the sheets held in Egeria")
    show = sub.add_parser("show", help="read one sheet from Egeria")
    show.add_argument("name")
    mig = sub.add_parser("migrate", help="write sheets from the JSON store to Egeria (a shared write)")
    mig.add_argument("--sheet", help="migrate only this sheet")
    mig.add_argument("--rename", help="write the --sheet under this name instead (a scratch copy)")
    mig.add_argument("--store", help="the JSON store (default PYEGERIA_DASHBOARD_SHEETS_STORE or "
                                     "~/.pyegeria/dashboard_sheets.json)")
    mig.add_argument("--dry-run", action="store_true", help="list every write; write nothing")
    mig.add_argument("--owner", help="owner of the migrated Dashboards (default: the signed-in user; DB-3)")
    dele = sub.add_parser("delete", help="delete a sheet's Egeria chain (never its Reports)")
    dele.add_argument("--sheet", required=True)
    dele.add_argument("--dry-run", action="store_true")
    dele.add_argument("--local", action="store_true", help="also remove the sheet from the JSON store")
    dele.add_argument("--store")
    args = parser.parse_args(argv)
    logger.remove()
    logger.add(sys.stderr, level=os.environ.get("PYEGERIA_DASHBOARDS_LOG_LEVEL", "WARNING"))
    from pyegeria.core.async_runner import run_sync
    return run_sync(_amain(args))


if __name__ == "__main__":
    sys.exit(main())
