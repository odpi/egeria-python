"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Dashboard sheets held in Egeria: the reader, and the migration from the local JSON store
(report-spec pipeline note v5.5 §8d / §10.6(c); BRIEF RS-DASH PR-2).

    load_dashboard_sheet(name)   -> the sheet, read from its Egeria element chain, or None
    list_dashboard_sheets()      -> every sheet held in Egeria (Dashboard::* elements)

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
import os
import sys
from typing import Any, Dict, List, Literal, Optional

from loguru import logger
from pydantic import Field

from md_processing.v2.dashboard_sheet import (
    DASHBOARD_QN_PREFIX, DashboardSheetEgeriaWriter, _default_store_path, _load_store, dashboard_qn,
    perspective_qualified_name, sheet_name_from_dashboard_qn,
)
from pyegeria.view._output_dashboard_sheet_models import DashboardSheet, DashboardSheetDict, Placement

__all__ = [
    "EgeriaDashboardSheet", "EgeriaPlacement", "REPORT_LINK_MISSING", "as_local_model",
    "async_list_dashboard_sheets", "async_load_dashboard_sheet", "async_migrate_dashboard_sheets",
    "list_dashboard_sheets", "load_dashboard_sheet", "main", "read_sheet_from_chain",
]

PAGE_SIZE = 25
REPORT_LINK_MISSING = "report link missing in Egeria"
_SPANS = ("1", "2", "full")
_STYLES = ("kpi", "panel")


class EgeriaPlacement(Placement):
    """A Placement read from Egeria. `kind`: "report", "text", or "missing" (a report placement whose
    report link is gone); `note` says what is missing or odd, in words."""
    kind: Literal["report", "text", "missing"] = "report"
    note: Optional[str] = None
    source: str = "egeria"


class EgeriaDashboardSheet(DashboardSheet):
    """A DashboardSheet read from Egeria. `breaks` names each broken link of its element chain (empty when
    the chain is whole); `guid` is the Dashboard's."""
    source: str = "egeria"
    guid: Optional[str] = None
    breaks: List[str] = Field(default_factory=list)


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
                                            perspectives=perspectives, detail_spec=detail_spec, kind="report")
            else:
                if binding.get("state") == "ambiguous":
                    notes.insert(0, f"{len(binding['links'])} reports are linked to this placement in Egeria; "
                                    f"none is chosen")
                else:
                    notes.insert(0, REPORT_LINK_MISSING)
                placement = EgeriaPlacement(ref=f.display_name, span=span, emphasis=style,
                                            perspectives=perspectives, detail_spec=detail_spec, kind="missing")
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
    start = 0
    while True:
        page = await client.classification_manager._async_get_elements(
            "Dashboard", start_from=start, page_size=PAGE_SIZE, graph_query_depth=0)
        items = [e for e in page if isinstance(e, dict) and e.get("elementHeader")] if isinstance(page, list) else []
        if not items:
            return out
        out.extend(e for e in items
                   if ((e.get("properties") or {}).get("qualifiedName") or "").startswith(DASHBOARD_QN_PREFIX))
        start += len(items)


async def async_list_dashboard_sheets(client: Any) -> List[EgeriaDashboardSheet]:
    """Every sheet held in Egeria, by name. A Dashboard whose chain is broken (for example one made with
    plain `Create Dashboard`) is listed with its `breaks`, not dropped."""
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


def list_dashboard_sheets(client: Any = None) -> List[EgeriaDashboardSheet]:
    """Sync form of async_list_dashboard_sheets. With no client, one is made from the environment."""
    from pyegeria.core.async_runner import run_sync

    async def _go():
        return await async_list_dashboard_sheets(client or await _signed_in_client())
    return run_sync(_go())


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
    """DB-3: a migrated sheet is owned by the user who migrates it -- the Dashboard's Ownership
    classification (owner = that userId). Left alone when the Dashboard already has an owner. No zone is
    set: the sheet is shared, in the default zone."""
    current = None if writer._is_planned(dashboard_guid) else await writer._find(qn)
    header = (current or {}).get("elementHeader") or {}
    if header.get("ownership"):
        writer.actions.append(f"unchanged Ownership {qn}")
        return
    writer.actions.append(f"classify Ownership {qn} (owner {owner})")
    if writer.dry_run:
        return
    await writer.client.classification_manager._async_add_ownership_to_element(
        dashboard_guid, {"class": "NewClassificationRequestBody",
                         "properties": {"class": "OwnershipProperties", "owner": owner,
                                        "ownerTypeName": "UserIdentity", "ownerPropertyName": "userId"}})


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
