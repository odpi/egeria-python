"""
Dashboard Sheet Processors for Dr.Egeria v2.

Handles `Create Dashboard Sheet`, `Link Report to Dashboard Sheet` and `Add Text on Dashboard Sheet`. The
commands keep their names and syntax. Since Egeria 6.3 (odpi/egeria#9432) they write each sheet into Egeria
as the element chain of the report-spec pipeline note v5.5 §8d / §10.6(c):

    Dashboard  (Dashboard::<sheet name>; displayName = the heading)
      --Schema-->               DisplayDataSchemaType   (DashboardSchema::<sheet name>)
      --AttributeForSchema-->   DisplayDataContainer    (DashboardSheet::<sheet name>; the sheet)
      --NestedSchemaAttribute(position)--> one DisplayDataField per placement
                                (DashboardPlacement::<sheet name>::<position>::<placement name>;
                                 displayName `<sheet name> / <placement name>`, see placement_display_name)

    A REPORT placement: placementKind "report", span, presentationStyle; its Report is linked by
    DataSetContent from the Dashboard (queryId = the placement's qualifiedName, queryType "placement").
    A TEXT placement: placementKind "text", markdownContent.
    Every placement: ScopedBy from each Perspective it names; DataDescription to the ReportSpec it drills
    into, when that spec has an element.

DB-1 (owner, 2026-11-09): during the transition every command writes Egeria AND the local JSON store
(PYEGERIA_DASHBOARD_SHEETS_STORE, default ~/.pyegeria/dashboard_sheets.json). With the local-only switch
(`dr_egeria --local-only`, or PYEGERIA_DASHBOARD_SHEETS_LOCAL_ONLY=1), or with no Egeria connection, the store
alone is written and the command output says so.

Every write is an upsert by qualifiedName: re-running a document changes nothing. Removing a placement
detaches its DataSetContent link and deletes its field; deleting a sheet deletes its chain. Neither ever
deletes a Report or a ReportSpec -- a sheet shows reports, it does not own them.

`DashboardSheetEgeriaWriter` is the one implementation of the Egeria side. The processors use it, and so does
`python -m pyegeria.view.dashboards migrate` (which writes sheets from the JSON store without going through
markdown, so text placements round-trip byte for byte).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from loguru import logger

from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.v2.report import (
    REPORT_SPEC_QN_PREFIXES, _props_differ, find_element_by_qualified_name,
    find_report_spec_element, upsert_dashboard_asset,
)
from pyegeria.core._exceptions import PyegeriaConnectionException, PyegeriaNotFoundException
from pyegeria.view._output_dashboard_sheet_models import DashboardSheet, DashboardSheetDict, Placement

LOCAL_ONLY_ENV = "PYEGERIA_DASHBOARD_SHEETS_LOCAL_ONLY"
PLANNED_PREFIX = "planned:"
PAGE_SIZE = 25

# ---------------------------------------------------------------------------- qualified names

DASHBOARD_QN_PREFIX = "Dashboard::"
SCHEMA_QN_PREFIX = "DashboardSchema::"
SHEET_QN_PREFIX = "DashboardSheet::"
PLACEMENT_QN_PREFIX = "DashboardPlacement::"


def dashboard_qn(sheet_name: str) -> str:
    return f"{DASHBOARD_QN_PREFIX}{sheet_name}"


def schema_type_qn(sheet_name: str) -> str:
    return f"{SCHEMA_QN_PREFIX}{sheet_name}"


def sheet_container_qn(sheet_name: str) -> str:
    return f"{SHEET_QN_PREFIX}{sheet_name}"


def placement_qn(sheet_name: str, position: int, placement_name: str) -> str:
    return f"{PLACEMENT_QN_PREFIX}{sheet_name}::{position}::{placement_name}"


def sheet_name_from_dashboard_qn(qualified_name: str) -> Optional[str]:
    if qualified_name and qualified_name.startswith(DASHBOARD_QN_PREFIX):
        return qualified_name[len(DASHBOARD_QN_PREFIX):]
    return None


# ---------------------------------------------------------------------------- perspectives (DB-2)

# Today's sheets use the Overview keys; DB-2 (owner, 2026-11-09) maps them to the Trellis perspective names
# (pipeline note §10.8). The label stays the placement's display value; the mapping only picks the element
# that ScopedBy links to.
PERSPECTIVE_TRELLIS_NAMES = {
    "governance": "Governance",
    "steward": "Steward",
    "owner": "Data Owner",
    "consumer": "Consumer",
    "builder": "App/AI Builder",
    "privacy": "Privacy",
    "security": "Security",
    "architecture": "Architecture",
    "engineer": "Data Expert",
    "engineering": "Data Expert",
    "community": "Community",
    "financial": "Financial",
    "admin": "Administration",
}

# Where a Trellis name and the qualifiedName of the element Trellis actually creates differ. Checked live
# 2026-11-09 (read only, 12 Perspective:: elements): §10.8 calls it "Data Owner", the element is
# Perspective::Owner; "Admin" is Perspective::Administration.
PERSPECTIVE_QN_OVERRIDES = {
    "Data Owner": "Perspective::Owner",
    "Owner": "Perspective::Owner",
    "Admin": "Perspective::Administration",
}


def perspective_qualified_name(label: str) -> str:
    """The qualifiedName of the Trellis Perspective element a placement's perspective label maps to."""
    text = (label or "").strip()
    if text.startswith("Perspective::"):
        return text
    trellis = PERSPECTIVE_TRELLIS_NAMES.get(text.lower())
    if trellis is None:
        # Already a Trellis name ("Steward", "Data Expert", "App/AI Builder"); match it case-insensitively.
        trellis = next((v for v in set(PERSPECTIVE_TRELLIS_NAMES.values()) if v.lower() == text.lower()), text)
    return PERSPECTIVE_QN_OVERRIDES.get(trellis, f"Perspective::{trellis}")


# ---------------------------------------------------------------------------- helpers

def _default_store_path() -> str:
    return os.path.expanduser(
        os.getenv("PYEGERIA_DASHBOARD_SHEETS_STORE", "~/.pyegeria/dashboard_sheets.json")
    )


def _parse_placement_perspectives(attributes: Dict[str, Any]) -> list:
    """Read "Placement Perspectives" out of a command's parsed attributes -- a "Simple List"-style
    attribute, which the base attribute-parsing pipeline may hand back either as an already-split list or
    as a raw comma-separated string; tolerate either."""
    value = attributes.get("Placement Perspectives", {}).get("value") or []
    if isinstance(value, str):
        return [p.strip() for p in value.split(",") if p.strip()]
    return list(value)


def _load_store(path: str) -> DashboardSheetDict:
    if os.path.exists(path):
        return DashboardSheetDict.load_from_json(path)
    return DashboardSheetDict()


def _truthy(value: Optional[str]) -> bool:
    return str(value or "").strip().lower() in ("1", "true", "yes", "on")


def _is_guid_like(value: Any) -> bool:
    text = str(value or "").strip()
    return bool(text) and not text.startswith(("(", "No ")) and " found" not in text


def placement_kind(placement: Placement) -> str:
    return "text" if placement.content is not None else "report"


def placement_display_name(sheet_name: str, placement_name: str) -> str:
    """A placement field's displayName: `<sheet name> / <placement name>`.

    Not the bare placement name: a REPORT placement is named after its Report, and Dr.Egeria resolves
    `Report Name` by displayName across all types, so a field sharing the Report's displayName makes that
    lookup ambiguous and the next `Link Report to Dashboard Sheet` fails. The bare name is kept in
    additionalProperties `placementName` (and in the qualifiedName).
    """
    return f"{sheet_name} / {placement_name}"


def field_placement_name(properties: Dict[str, Any]) -> str:
    """The bare placement name of a DisplayDataField: `placementName`, else the qualifiedName's last part."""
    extra = properties.get("additionalProperties") or {}
    if extra.get("placementName"):
        return extra["placementName"]
    qn = properties.get("qualifiedName") or ""
    if qn.startswith(PLACEMENT_QN_PREFIX):
        parts = qn[len(PLACEMENT_QN_PREFIX):].split("::", 2)
        if len(parts) == 3:
            return parts[2]
    return properties.get("displayName") or ""


def placement_field_properties(sheet_name: str, position: int, placement: Placement,
                               qualified_name: Optional[str] = None) -> Dict[str, Any]:
    """The DisplayDataField properties for one placement.

    The perspective labels and the drill-down spec name are also kept on the field (additionalProperties
    `perspectives`, comma-separated, and `detailSpec`): the ScopedBy / DataDescription links carry the graph
    meaning, but only when the element exists, and a label is not recoverable from the element it maps to
    ("owner" and "Data Owner" both map to Perspective::Owner). The reader gives back the labels as written.
    """
    extra: Dict[str, str] = {"placementName": placement.ref}
    if placement.perspectives:
        extra["perspectives"] = ",".join(placement.perspectives)
    if placement.detail_spec:
        extra["detailSpec"] = placement.detail_spec
    kind = placement_kind(placement)
    return {
        "class": "DisplayDataFieldProperties",
        "typeName": "DisplayDataField",
        "qualifiedName": qualified_name or placement_qn(sheet_name, position, placement.ref),
        "displayName": placement_display_name(sheet_name, placement.ref),
        "placementKind": kind,
        "span": placement.span,
        "presentationStyle": placement.emphasis,
        "markdownContent": placement.content if kind == "text" else None,
        "additionalProperties": extra,
    }


def _refuse_kind_clash(sheet_name: str, placement: Placement, existing_kind: str) -> None:
    """Placements are matched by name within a sheet, so a report and a text placement cannot share a name:
    the second would silently replace the first. Refuse, in words."""
    kind = placement_kind(placement)
    if existing_kind != kind:
        raise ValueError(
            f"Dashboard Sheet '{sheet_name}' already has a {existing_kind} placement named '{placement.ref}'; a "
            f"{kind} placement cannot share its name (placements are matched by name). Give it another name.")


def duplicate_placement_names(sheet: DashboardSheet) -> List[str]:
    """Names used by more than one placement of a sheet (they would collapse into one placement)."""
    seen, dups = set(), []
    for p in sheet.placements:
        ref = p.get("ref") if isinstance(p, dict) else p.ref
        if ref in seen and ref not in dups:
            dups.append(ref)
        seen.add(ref)
    return dups


def _field_props_differ(desired: Dict[str, Any], current: Dict[str, Any]) -> bool:
    """Like _props_differ, but a property set on the field and now unset also counts as a change (a
    placement re-run without perspectives must clear them)."""
    if _props_differ(desired, current):
        return True
    if desired.get("markdownContent") is None and current.get("markdownContent"):
        return True
    return False


@dataclass
class SheetChain:
    """The GUIDs of one sheet's chain in Egeria. A guid starting `planned:` is one a dry run would create."""
    sheet_name: str
    dashboard_guid: Optional[str] = None
    schema_type_guid: Optional[str] = None
    container_guid: Optional[str] = None
    dashboard: Optional[Dict[str, Any]] = None


@dataclass
class FieldInfo:
    guid: str
    qualified_name: str
    display_name: str  # the bare placement name (field_placement_name), not the field's displayName
    position: Optional[int]
    properties: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------- the writer

class DashboardSheetEgeriaWriter:
    """Writes Dashboard Sheets into Egeria as the §8d element chain. The one implementation, used by the
    Dr.Egeria processors and by migration.

    `notes` collects what a reader of the command output must know (a report or perspective with no
    element, a link not written); `actions` records every write made, or with `dry_run=True` every write
    that would be made ("create DisplayDataField DashboardPlacement::..."), with "unchanged ..." for elements
    already as wanted. A dry run still reads Egeria (bounded, page size 25) but writes nothing.
    """

    def __init__(self, client: Any, *, dry_run: bool = False):
        self.client = client
        self.dry_run = dry_run
        self.notes: List[str] = []
        self.actions: List[str] = []
        self._perspective_cache: Dict[str, Optional[str]] = {}
        self._planned = 0

    # ------------------------------------------------------------ small primitives

    def _note(self, text: str) -> None:
        if text not in self.notes:
            self.notes.append(text)

    def _plan(self, what: str) -> str:
        self._planned += 1
        return f"{PLANNED_PREFIX}{self._planned}:{what}"

    @staticmethod
    def _is_planned(guid: Optional[str]) -> bool:
        return bool(guid) and str(guid).startswith(PLANNED_PREFIX)

    async def _find(self, qualified_name: str) -> Optional[Dict[str, Any]]:
        return await find_element_by_qualified_name(self.client, qualified_name)

    async def _related(self, guid: Optional[str], relationship: str, start_at_end: int = 1) -> List[Dict[str, Any]]:
        """Every element related to `guid` by `relationship`, paged at 25. Only an empty page ends the read
        (a short page is not the last page)."""
        if not guid or self._is_planned(guid):
            return []
        out: List[Dict[str, Any]] = []
        start = 0
        while True:
            try:
                page = await self.client.classification_manager._async_get_related_elements(
                    guid, relationship, start_at_end=start_at_end, start_from=start, page_size=PAGE_SIZE,
                    graph_query_depth=0)
            except PyegeriaNotFoundException:
                page = []
            items = [e for e in page if isinstance(e, dict) and e.get("elementHeader")] if isinstance(page, list) else []
            if not items:
                return out
            out.extend(items)
            start += len(items)

    @staticmethod
    def _guid(element: Dict[str, Any]) -> str:
        return element["elementHeader"]["guid"]

    @staticmethod
    def _type(element: Dict[str, Any]) -> str:
        return ((element.get("elementHeader") or {}).get("type") or {}).get("typeName", "")

    @staticmethod
    def _rel_props(element: Dict[str, Any]) -> Dict[str, Any]:
        return ((element.get("relatedBy") or {}).get("relationshipProperties")) or {}

    def _created_guid(self, raw: Any, what: str) -> str:
        if isinstance(raw, str) and raw.strip():
            return raw.strip()
        if isinstance(raw, dict) and raw.get("guid"):
            return raw["guid"]
        raise ValueError(f"Egeria returned no GUID creating {what}: {raw!r}")

    async def _create_schema_element(self, kind: str, props: Dict[str, Any], anchor_guid: Optional[str]) -> str:
        """Create a schema type (kind "type") or attribute, anchored to the Dashboard."""
        qn = props["qualifiedName"]
        self.actions.append(f"create {props['typeName']} {qn}")
        if self.dry_run:
            return self._plan(qn)
        body = {"class": "NewElementRequestBody", "isOwnAnchor": False, "anchorGUID": anchor_guid,
                "properties": props}
        maker = self.client.schema_maker
        raw = await (maker._async_create_schema_type(body) if kind == "type"
                     else maker._async_create_schema_attribute(body))
        return self._created_guid(raw, qn)

    async def _update_schema_attribute(self, guid: str, props: Dict[str, Any]) -> None:
        self.actions.append(f"update {props['typeName']} {props['qualifiedName']}")
        if self.dry_run:
            return
        await self.client.schema_maker._async_update_schema_attribute(
            guid, {"class": "UpdateElementRequestBody", "properties": props, "mergeUpdate": False})

    # ------------------------------------------------------------ reading the chain (no writes)

    async def find_chain(self, sheet_name: str) -> SheetChain:
        """The chain as it is in Egeria; any missing part is None."""
        chain = SheetChain(sheet_name=sheet_name)
        dashboard = await self._find(dashboard_qn(sheet_name))
        if not dashboard:
            return chain
        chain.dashboard = dashboard
        chain.dashboard_guid = self._guid(dashboard)
        schema_types = [e for e in await self._related(chain.dashboard_guid, "Schema")
                        if self._type(e) == "DisplayDataSchemaType"]
        if schema_types:
            wanted = [e for e in schema_types if (e.get("properties") or {}).get("qualifiedName")
                      == schema_type_qn(sheet_name)]
            chain.schema_type_guid = self._guid((wanted or schema_types)[0])
            containers = [e for e in await self._related(chain.schema_type_guid, "AttributeForSchema")
                          if self._type(e) == "DisplayDataContainer"]
            wanted = [e for e in containers if (e.get("properties") or {}).get("qualifiedName")
                      == sheet_container_qn(sheet_name)]
            if containers:
                chain.container_guid = self._guid((wanted or containers)[0])
        return chain

    async def list_fields(self, container_guid: Optional[str]) -> List[FieldInfo]:
        """The placements under a sheet container, in position order."""
        fields: List[FieldInfo] = []
        for e in await self._related(container_guid, "NestedSchemaAttribute"):
            if self._type(e) != "DisplayDataField":
                continue
            props = e.get("properties") or {}
            position = self._rel_props(e).get("position")
            fields.append(FieldInfo(guid=self._guid(e), qualified_name=props.get("qualifiedName", ""),
                                    display_name=field_placement_name(props),
                                    position=int(position) if position is not None else None,
                                    properties=props))
        fields.sort(key=lambda f: (f.position is None, f.position or 0))
        return fields

    # ------------------------------------------------------------ sheet

    async def ensure_sheet(self, sheet_name: str, heading: str, description: str = "",
                           family: Optional[str] = None, aliases: Optional[List[str]] = None) -> SheetChain:
        """Create or update the Dashboard, its DisplayDataSchemaType and the sheet's DisplayDataContainer."""
        chain = await self.find_chain(sheet_name)

        # 1. the Dashboard asset -- through upsert_dashboard_asset, the same code as `Create Dashboard`
        props: Dict[str, Any] = {
            "class": "DashboardProperties",
            "typeName": "Dashboard",
            "qualifiedName": dashboard_qn(sheet_name),
            "displayName": heading or sheet_name,
            "description": description or None,
            "aliases": list(aliases) if aliases else None,
            "additionalProperties": {"family": family} if family else None,
        }
        if self.dry_run:
            if chain.dashboard is None:
                self.actions.append(f"create Dashboard {props['qualifiedName']}")
                chain.dashboard_guid = self._plan(props["qualifiedName"])
            elif _props_differ(props, chain.dashboard.get("properties") or {}):
                self.actions.append(f"update Dashboard {props['qualifiedName']}")
            else:
                self.actions.append(f"unchanged Dashboard {props['qualifiedName']}")
        else:
            guid, verb_word, _ = await upsert_dashboard_asset(
                self.client, props["qualifiedName"], props, chain.dashboard,
                create_body={"class": "NewElementRequestBody", "isOwnAnchor": True})
            chain.dashboard_guid = self._created_guid(guid, props["qualifiedName"])
            self.actions.append(f"{verb_word.lower()} Dashboard {props['qualifiedName']}")

        # 2. its DisplayDataSchemaType, linked by Schema
        if chain.schema_type_guid is None:
            st_props = {"class": "DisplayDataSchemaTypeProperties", "typeName": "DisplayDataSchemaType",
                        "qualifiedName": schema_type_qn(sheet_name), "displayName": f"{sheet_name} layout"}
            existing = None if self._is_planned(chain.dashboard_guid) else await self._find(st_props["qualifiedName"])
            chain.schema_type_guid = (self._guid(existing) if existing
                                      else await self._create_schema_element("type", st_props, chain.dashboard_guid))
            self.actions.append(f"link Schema {dashboard_qn(sheet_name)} -> {st_props['qualifiedName']}")
            if not self.dry_run:
                await self.client.schema_maker._async_link_schema(chain.dashboard_guid, chain.schema_type_guid)
        else:
            self.actions.append(f"unchanged DisplayDataSchemaType {schema_type_qn(sheet_name)}")
            # found through the Schema link, so that link is in place too; itemised so a re-run's
            # "unchanged" count matches the first run's change count
            self.actions.append(f"unchanged Schema {dashboard_qn(sheet_name)} -> {schema_type_qn(sheet_name)}")

        # 3. the sheet's DisplayDataContainer, linked by AttributeForSchema (position 1)
        if chain.container_guid is None:
            c_props = {"class": "DisplayDataContainerProperties", "typeName": "DisplayDataContainer",
                       "qualifiedName": sheet_container_qn(sheet_name), "displayName": f"{sheet_name} sheet"}
            existing = None if self._is_planned(chain.schema_type_guid) else await self._find(c_props["qualifiedName"])
            chain.container_guid = (self._guid(existing) if existing
                                    else await self._create_schema_element("attribute", c_props, chain.dashboard_guid))
            self.actions.append(f"link AttributeForSchema {schema_type_qn(sheet_name)} -> {c_props['qualifiedName']} (position 1)")
            if not self.dry_run:
                await self.client.schema_maker._async_link_attribute_for_schema(
                    chain.schema_type_guid, chain.container_guid,
                    {"class": "NewRelationshipRequestBody",
                     "properties": {"class": "AttributeForSchemaProperties", "position": 1}})
        else:
            self.actions.append(f"unchanged DisplayDataContainer {sheet_container_qn(sheet_name)}")
            self.actions.append(f"unchanged AttributeForSchema {schema_type_qn(sheet_name)} -> "
                                f"{sheet_container_qn(sheet_name)}")
        return chain

    async def ensure_ownership(self, dashboard_guid: Optional[str], qn: str, owner: str) -> str:
        """DB-3: the Dashboard's Ownership classification (owner = a userId), set once. A Dashboard that
        already has an owner keeps it. No zone is set. Used by `Create Dashboard Sheet` and by
        `python -m pyegeria.view.dashboards migrate`.

        Returns "set", "unchanged" (already owned) or "planned" (dry run)."""
        current = None if self._is_planned(dashboard_guid) else await self._find(qn)
        existing = (((current or {}).get("elementHeader") or {}).get("ownership") or {})
        if existing:
            have = (existing.get("classificationProperties") or {}).get("owner")
            self.actions.append(f"unchanged Ownership {qn}")
            if have and have != owner:
                self._note(f"Dashboard '{qn}' is already owned by '{have}'; its owner was not changed to '{owner}'.")
            return "unchanged"
        self.actions.append(f"classify Ownership {qn} (owner {owner})")
        if self.dry_run:
            return "planned"
        await self.client.classification_manager._async_add_ownership_to_element(
            dashboard_guid, {"class": "NewClassificationRequestBody",
                             "properties": {"class": "OwnershipProperties", "owner": owner,
                                            "ownerTypeName": "UserIdentity", "ownerPropertyName": "userId"}})
        return "set"

    # ------------------------------------------------------------ placements

    async def _resolve_report(self, report_name: str) -> Optional[str]:
        """The GUID of the Report a placement shows: the one `Report` whose displayName is exactly
        `report_name` (an exact, type-filtered lookup: 0.1 s live, where a contains-search took ~35 s),
        else the Report whose qualifiedName it is. None if there
        is none; two or more exact matches are a note, and no link.

        Not Dr.Egeria's `__async_get_guid__`: it tries a unique-name lookup first, which Egeria rejects
        when the name is shared with an element of another type -- seen live 2026-11-09 for 'Term
        Definition Completeness' and 'Governance Classification Coverage', both real Reports."""
        matches: List[str] = []
        start = 0
        while True:
            try:
                page = await self.client.classification_manager._async_get_elements_by_property_value(
                    report_name, ["displayName"], metadata_element_type="Report",
                    start_from=start, page_size=PAGE_SIZE, graph_query_depth=0)
            except PyegeriaNotFoundException:
                page = []
            items = [e for e in page if isinstance(e, dict) and e.get("elementHeader")] if isinstance(page, list) else []
            if not items:
                break
            matches += [self._guid(e) for e in items
                        if (e.get("properties") or {}).get("displayName") == report_name
                        and self._type(e) == "Report"]
            start += len(items)
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            self._note(f"{len(matches)} Reports are named '{report_name}' in Egeria: no report link was written "
                       f"for that placement. Give the placement's report a unique name.")
            return None
        element = await self._find(report_name)
        if element and self._type(element) == "Report":
            return self._guid(element)
        return None

    async def _perspective_guid(self, label: str) -> Optional[str]:
        qn = perspective_qualified_name(label)
        if qn not in self._perspective_cache:
            element = await self._find(qn)
            self._perspective_cache[qn] = self._guid(element) if element else None
        return self._perspective_cache[qn]

    async def upsert_placement(self, chain: SheetChain, placement: Placement, *,
                               position: Optional[int] = None,
                               report_guid: Optional[str] = None) -> str:
        """Create or update one placement's DisplayDataField and its links. Found by name within the sheet
        (a re-run with the same name updates in place; its qualifiedName and position never change)."""
        sheet = chain.sheet_name
        fields = await self.list_fields(chain.container_guid)
        existing = next((f for f in fields if f.display_name == placement.ref), None)

        if existing:
            _refuse_kind_clash(sheet, placement, existing.properties.get("placementKind") or "report")
            pos = existing.position if existing.position is not None else (position or 0)
            props = placement_field_properties(sheet, pos, placement, existing.qualified_name)
            field_guid = existing.guid
            if _field_props_differ(props, existing.properties):
                await self._update_schema_attribute(field_guid, props)
            else:
                self.actions.append(f"unchanged DisplayDataField {existing.qualified_name}")
            self.actions.append(f"unchanged NestedSchemaAttribute {sheet_container_qn(sheet)} -> "
                                f"{existing.qualified_name} (position {pos})")
        else:
            taken = [f.position for f in fields if f.position is not None]
            if position is not None and position not in taken:
                pos = position
            else:  # never reuse a taken position (after a removal, an index can equal one)
                pos = max(taken) + 1 if taken else 1
            props = placement_field_properties(sheet, pos, placement)
            found = None if self._is_planned(chain.container_guid) else await self._find(props["qualifiedName"])
            if found:
                field_guid = self._guid(found)
                if _field_props_differ(props, found.get("properties") or {}):
                    await self._update_schema_attribute(field_guid, props)
            else:
                field_guid = await self._create_schema_element("attribute", props, chain.dashboard_guid)
            self.actions.append(f"link NestedSchemaAttribute {sheet_container_qn(sheet)} -> {props['qualifiedName']} (position {pos})")
            if not self.dry_run:
                await self.client.schema_maker._async_link_nested_schema_attribute(
                    chain.container_guid, field_guid,
                    {"class": "NewRelationshipRequestBody",
                     "properties": {"class": "NestedSchemaAttributeProperties", "position": pos}})

        qn = props["qualifiedName"]
        await self._sync_report_link(chain, placement, qn, report_guid)
        await self._sync_perspectives(field_guid, placement)
        await self._sync_detail_spec(field_guid, placement)
        return field_guid

    async def _sync_report_link(self, chain: SheetChain, placement: Placement, qn: str,
                                report_guid: Optional[str]) -> None:
        """DataSetContent Dashboard -> Report, queryId = the placement's qualifiedName."""
        binding: Dict[str, Any] = {"state": "unbound", "links": []}
        if not self._is_planned(chain.dashboard_guid):
            bindings = await self.client.asset_maker._async_get_placement_reports(chain.dashboard_guid, [qn])
            binding = (bindings or {}).get(qn) or binding
        if placement_kind(placement) == "text":
            if binding["links"]:
                await self._detach_report(chain, qn, "the placement is text now")
            return
        if report_guid and not _is_guid_like(report_guid):
            report_guid = None  # "(Planned: ...)" or a not-found string from attribute resolution
        if report_guid is None:
            report_guid = await self._resolve_report(placement.ref)
        if not report_guid:
            self._note(f"Report '{placement.ref}' was not found in Egeria: placement '{placement.ref}' on sheet "
                       f"'{chain.sheet_name}' was written without its report link, and reads as missing until a "
                       f"Report with that name exists and the command is run again.")
            if binding["links"]:
                await self._detach_report(chain, qn, "its report is gone")
            return
        if binding.get("state") == "bound" and binding.get("report_guid") == report_guid:
            self.actions.append(f"unchanged DataSetContent {dashboard_qn(chain.sheet_name)} -> {placement.ref} [{qn}]")
            return
        if binding["links"]:
            await self._detach_report(chain, qn, "it showed a different report")
        self.actions.append(f"link DataSetContent {dashboard_qn(chain.sheet_name)} -> Report '{placement.ref}' "
                            f"(queryId {qn})")
        if not self.dry_run:
            await self.client.asset_maker._async_link_placement_report(chain.dashboard_guid, report_guid, qn)

    async def _detach_report(self, chain: SheetChain, qn: str, why: str) -> None:
        self.actions.append(f"detach DataSetContent for {qn} ({why})")
        if not self.dry_run:
            await self.client.asset_maker._async_detach_placement_report(chain.dashboard_guid, qn)

    async def _sync_perspectives(self, field_guid: str, placement: Placement) -> None:
        """ScopedBy Perspective -> placement, one per label whose Trellis element exists. Never creates a
        Perspective: a label with no element is written without that link, with a note."""
        wanted: Dict[str, str] = {}
        for label in placement.perspectives:
            guid = await self._perspective_guid(label)
            if guid:
                wanted[guid] = label
            else:
                self._note(f"Perspective '{label}' (as {perspective_qualified_name(label)}) does not exist in "
                           f"Egeria: placement '{placement.ref}' was written without that ScopedBy link. "
                           f"Perspectives are not created here.")
        current = {self._guid(e) for e in await self._related(field_guid, "ScopedBy", start_at_end=2)
                   if self._type(e) == "Perspective"}
        for guid in current - set(wanted):
            self.actions.append(f"detach ScopedBy {guid} -> {placement.ref}")
            if not self.dry_run:
                await self.client.classification_manager._async_clear_scope_from_element(guid, field_guid)
        for guid, label in wanted.items():
            if guid in current:
                continue
            self.actions.append(f"link ScopedBy {perspective_qualified_name(label)} -> {placement.ref}")
            if not self.dry_run:
                await self.client.classification_manager._async_add_scope_to_element(guid, field_guid)

    async def _sync_detail_spec(self, field_guid: str, placement: Placement) -> None:
        """DataDescription placement -> the ReportSpec it drills into, when the spec has an element."""
        wanted: Optional[str] = None
        if placement.detail_spec:
            element = await find_report_spec_element(self.client, placement.detail_spec)
            if element:
                wanted = self._guid(element)
            else:
                self._note(f"Drill-down spec '{placement.detail_spec}' of placement '{placement.ref}' has no Egeria "
                           f"element (looked for {' and '.join(p + placement.detail_spec for p in REPORT_SPEC_QN_PREFIXES)}): "
                           f"no DataDescription link was written; the name is kept on the placement.")
        current = {self._guid(e) for e in await self._related(field_guid, "DataDescription", start_at_end=1)}
        for guid in current - ({wanted} if wanted else set()):
            self.actions.append(f"detach DataDescription {placement.ref} -> {guid}")
            if not self.dry_run:
                await self.client.collection_manager._async_detach_data_description(field_guid, guid)
        if wanted and wanted not in current:
            self.actions.append(f"link DataDescription {placement.ref} -> {placement.detail_spec}")
            if not self.dry_run:
                await self.client.collection_manager._async_attach_data_description(field_guid, wanted)

    # ------------------------------------------------------------ whole sheets, removal

    async def write_sheet(self, sheet: DashboardSheet) -> SheetChain:
        """Write a whole sheet (migration): the chain, then every placement at its 1-based position.
        A sheet with two placements of one name is refused before anything is written: they would collapse
        into one placement."""
        dups = duplicate_placement_names(sheet)
        if dups:
            raise ValueError(f"Dashboard Sheet '{sheet.name}' has more than one placement named "
                             f"{', '.join(repr(d) for d in dups)}; placements are matched by name, so they would "
                             f"collapse into one. Rename them in the store first. Nothing was written.")
        chain = await self.ensure_sheet(sheet.name, sheet.heading, sheet.description, sheet.family, sheet.aliases)
        for index, placement in enumerate(sheet.placements, start=1):
            if isinstance(placement, dict):
                placement = Placement(**placement)
            await self.upsert_placement(chain, placement, position=index)
        return chain

    async def remove_placement(self, sheet_name: str, placement_name: str) -> bool:
        """Detach a placement's DataSetContent link and delete its field. Never deletes the Report.
        False if the sheet or placement is not in Egeria."""
        chain = await self.find_chain(sheet_name)
        fields = await self.list_fields(chain.container_guid)
        target = next((f for f in fields if f.display_name == placement_name), None)
        if not target:
            return False
        await self._detach_report(chain, target.qualified_name, "placement removed")
        self.actions.append(f"delete DisplayDataField {target.qualified_name}")
        if not self.dry_run:
            await self.client.schema_maker._async_delete_schema_attribute(target.guid)
        return True

    async def delete_sheet(self, sheet_name: str) -> bool:
        """Delete a sheet's chain: each placement (link, then field), the container, the schema type, the
        Dashboard. Reports and ReportSpecs are never deleted. False if the Dashboard is not in Egeria."""
        chain = await self.find_chain(sheet_name)
        if not chain.dashboard_guid:
            return False
        for f in await self.list_fields(chain.container_guid):
            await self._detach_report(chain, f.qualified_name, "sheet deleted")
            self.actions.append(f"delete DisplayDataField {f.qualified_name}")
            if not self.dry_run:
                await self.client.schema_maker._async_delete_schema_attribute(f.guid)
        if chain.container_guid:
            self.actions.append(f"delete DisplayDataContainer {sheet_container_qn(sheet_name)}")
            if not self.dry_run:
                await self.client.schema_maker._async_delete_schema_attribute(chain.container_guid)
        if chain.schema_type_guid:
            self.actions.append(f"delete DisplayDataSchemaType {schema_type_qn(sheet_name)}")
            if not self.dry_run:
                await self.client.schema_maker._async_delete_schema_type(chain.schema_type_guid)
        self.actions.append(f"delete Dashboard {dashboard_qn(sheet_name)}")
        if not self.dry_run:
            await self.client.asset_maker._async_delete_asset(chain.dashboard_guid)
        return True


# ---------------------------------------------------------------------------- processors

def local_only_reason(processor: AsyncBaseCommandProcessor) -> Optional[str]:
    """Why this command writes the local store alone, or None when it writes Egeria too (DB-1)."""
    if processor.context.get("dashboard_sheets_local_only"):
        return "--local-only was given"
    if _truthy(os.getenv(LOCAL_ONLY_ENV)):
        return f"{LOCAL_ONLY_ENV} is set"
    if processor.client is None:
        return "there is no Egeria connection"
    return None


def _egeria_section(writer: Optional[DashboardSheetEgeriaWriter], local_reason: Optional[str]) -> str:
    if local_reason:
        return f"\n- **Egeria**: not written ({local_reason}); the local store alone was written.\n"
    lines = ["\n- **Egeria**: written"]
    if writer is not None:
        changed = [a for a in writer.actions if not a.startswith("unchanged")]
        lines[0] += f" ({len(changed)} change(s))" if changed else " (no change: already as written)"
        for note in writer.notes:
            lines.append(f"  - Note: {note}")
    return "\n".join(lines) + "\n"


class _DashboardSheetProcessorMixin:
    """Shared Egeria plumbing for the three sheet commands."""

    async def _with_egeria(self, work: Callable[[DashboardSheetEgeriaWriter], Any]):
        """Run `work` against Egeria unless the command is local-only. Returns (writer, local_reason).
        An unreachable Egeria falls back to the store alone and says so; any other Egeria error fails the
        command (and the store is then not written, so the two stay consistent)."""
        reason = local_only_reason(self)
        if reason:
            return None, reason
        writer = DashboardSheetEgeriaWriter(self.client)
        try:
            await work(writer)
        except PyegeriaConnectionException as e:
            return None, f"Egeria could not be reached ({e.__class__.__name__})"
        for note in writer.notes:
            self._add_warning(note)
        return writer, None


class CreateDashboardSheetProcessor(_DashboardSheetProcessorMixin, AsyncBaseCommandProcessor):
    """Processor for Create Dashboard Sheet (and its Update transition).

    The target is the Egeria Dashboard `Dashboard::<Display Name>` (or, local-only, the store record).
    The Dashboard asset itself is written by `upsert_dashboard_asset`, the same code as `Create Dashboard`.
    """

    def derive_qualified_name(self, attributes: Optional[Dict[str, Any]] = None) -> str:
        if attributes is None:
            attributes = self.parsed_output.get("attributes", {})
        name = attributes.get("Display Name", {}).get("value") or ""
        return dashboard_qn(name) if name else ""

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        name = self.parsed_output.get("attributes", {}).get("Display Name", {}).get("value")
        if not name:
            return None
        if local_only_reason(self) is None:
            try:
                element = await find_element_by_qualified_name(self.client, dashboard_qn(name))
            except PyegeriaConnectionException:
                element = None
            if element:
                return element
        sheet = _load_store(_default_store_path()).get(name)
        if sheet:
            return {"elementHeader": {"guid": f"local:{sheet.name}", "type": {"typeName": "DashboardSheet"}},
                    "properties": {"qualifiedName": dashboard_qn(sheet.name), "displayName": sheet.heading,
                                   "description": sheet.description}}
        return None

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        name = attributes.get("Display Name", {}).get("value")
        if not name:
            raise ValueError("Display Name is required.")
        heading = attributes.get("Dashboard Sheet Heading", {}).get("value") or name
        description = attributes.get("Dashboard Sheet Description", {}).get("value") or ""
        family = attributes.get("Dashboard Sheet Family", {}).get("value") or None

        path = _default_store_path()
        sheets = _load_store(path)
        aliases = list(sheets[name].aliases) if name in sheets else []

        # DB-3: owned by the user the command runs as (client.user_id; in the Portal, by default, its service
        # user) unless Dashboard Owner names another userId; set once.
        explicit_owner = attributes.get("Dashboard Owner", {}).get("value") or None
        owner = explicit_owner or getattr(self.client, "user_id", None) or None
        ownership = {}

        async def _work(writer: DashboardSheetEgeriaWriter):
            chain = await writer.ensure_sheet(name, heading, description, family, aliases)
            self.parsed_output["guid"] = chain.dashboard_guid
            if owner:
                ownership["status"] = await writer.ensure_ownership(chain.dashboard_guid, dashboard_qn(name), owner)

        writer, local_reason = await self._with_egeria(_work)

        is_update = name in sheets
        sheets.upsert(name, DashboardSheet(name=name, heading=heading, description=description, family=family))
        sheets.save_to_json(path)
        status_notes = ""
        if local_reason:
            # `name` stands in for the GUID (the sheet is in the local store only), so the base
            # processor must not sync anything to Egeria with it.
            self.parsed_output["guid"] = name
            self.parsed_output["local_only"] = local_reason
            if attributes.get("Zone Membership", {}).get("value"):
                status_notes = "\n- **Zone Membership**: not written (local only)"
            status_notes += "\n- **Ownership**: not written (local only)"
        elif ownership.get("status") == "set":
            status_notes = f"\n- **Ownership**: {owner}"
        elif ownership.get("status") == "unchanged":
            status_notes = "\n- **Ownership**: unchanged (already owned)"

        verb_word = "Updated" if is_update else "Created"
        logger.success(f"{verb_word} Dashboard Sheet '{name}' (local store {path}; Egeria: "
                       f"{'not written, ' + local_reason if local_reason else 'written'})")
        return (
            f"\n\n## {self.command.verb} Dashboard Sheet\n\n"
            f"{verb_word} Dashboard Sheet **{name}**\n\n"
            f"- **Heading**: {heading}\n"
            f"- **Description**: {description or '_(none)_'}\n"
            f"- **Family**: {family or '_(none)_'}\n"
            f"- **Local store**: {path}"
            f"{status_notes}"
            f"{_egeria_section(writer, local_reason)}"
        )


async def _placement_chain(writer: DashboardSheetEgeriaWriter, sheet_name: str,
                           local_sheet: Optional[DashboardSheet]) -> SheetChain:
    """The sheet's chain for a placement command. A sheet held only in the local store (made before its
    commands wrote Egeria) is written to Egeria whole first, so the Egeria sheet is never a partial copy."""
    chain = await writer.find_chain(sheet_name)
    if chain.container_guid:
        return chain
    if local_sheet is None:
        raise ValueError(f"Dashboard Sheet '{sheet_name}' does not exist. Create it first with "
                         f"'Create Dashboard Sheet'.")
    writer._note(f"Dashboard Sheet '{sheet_name}' was only in the local store; it was written to Egeria "
                 f"whole ({len(local_sheet.placements)} placement(s)) before this placement.")
    return await writer.write_sheet(local_sheet)


class LinkReportToDashboardSheetProcessor(_DashboardSheetProcessorMixin, AsyncBaseCommandProcessor):
    """
    Processor for Link Report to Dashboard Sheet -- places a Report (an Egeria `Report` asset created via
    `Create Report`) on a Dashboard Sheet as an ordered placement. In Egeria: a DisplayDataField with
    placementKind "report", linked to the Report by the Dashboard's DataSetContent (queryId = the
    placement's qualifiedName); ScopedBy to its perspectives; DataDescription to its drill-down spec. In the
    local store: a Placement whose `ref` is the report's name. Re-running with the same Report Name
    updates the placement in place.
    """

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    def supports_target_element_lookup(self) -> bool:
        return False

    async def resolve_element_guid(self, name_or_guid: str, tech_type: Optional[str] = None) -> Optional[str]:
        """`Report Name` is resolved first as the one Report with exactly that displayName (the writer's typed
        lookup), then as before. Dr.Egeria's untyped lookup is refused by Egeria when another element type
        shares the name (live 2026-11-09: 'Term Definition Completeness', 'Governance Classification
        Coverage'), which failed this command at validation."""
        text = str(name_or_guid or "").strip()
        if text and "(guid:" not in text and self.client is not None:
            try:
                guid = await DashboardSheetEgeriaWriter(self.client)._resolve_report(text)
            except (AttributeError, PyegeriaConnectionException):
                guid = None
            if guid:
                return guid
        return await super().resolve_element_guid(name_or_guid, tech_type)

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        sheet_name = attributes.get("Dashboard Sheet Name", {}).get("value")
        report_name = attributes.get("Report Name", {}).get("value")
        report_guid = attributes.get("Report Name", {}).get("guid")
        span = attributes.get("Placement Span", {}).get("value") or "1"
        emphasis = attributes.get("Placement Emphasis", {}).get("value") or "kpi"
        perspectives = _parse_placement_perspectives(attributes)
        detail_spec = attributes.get("Placement Detail Spec", {}).get("value") or None

        if not sheet_name:
            raise ValueError("Dashboard Sheet Name is required.")
        if not report_name:
            raise ValueError("Report Name is required.")

        path = _default_store_path()
        sheets = _load_store(path)
        sheet = sheets.get(sheet_name)
        placement = Placement(ref=report_name, span=span, emphasis=emphasis,
                              perspectives=perspectives, detail_spec=detail_spec)

        async def _work(writer: DashboardSheetEgeriaWriter):
            chain = await _placement_chain(writer, sheet_name, sheet)
            await writer.upsert_placement(chain, placement, report_guid=report_guid)

        writer, local_reason = await self._with_egeria(_work)

        if local_reason and not report_guid:
            self._add_warning(
                f"Report '{report_name}' was not found in Egeria — the placement will be "
                f"unresolved until a Report with that name exists (create one with 'Create Report')."
            )
        if not sheet:
            if local_reason:
                raise ValueError(f"Dashboard Sheet '{sheet_name}' does not exist. Create it first with "
                                 f"'Create Dashboard Sheet'.")
            # Held in Egeria only (made elsewhere): start its local copy so the store stays a full fallback.
            sheet = DashboardSheet(name=sheet_name, heading=sheet_name)
            sheets[sheet_name] = sheet
            sheet = sheets.get(sheet_name)

        replaced = _put_placement(sheet, placement)
        sheets.save_to_json(path)
        verb_word = "Updated placement of" if replaced else "Placed"
        logger.success(f"{verb_word} Report '{report_name}' in Dashboard Sheet '{sheet_name}'")
        extra = []
        if perspectives:
            extra.append(f"perspectives={','.join(perspectives)}")
        if detail_spec:
            extra.append(f"detail_spec={detail_spec}")
        extra_str = (", " + ", ".join(extra)) if extra else ""
        return (
            f"\n\n## {self.command.verb} Report to Dashboard Sheet\n\n"
            f"{verb_word} **{report_name}** in Dashboard Sheet **{sheet_name}** "
            f"(span={span}, emphasis={emphasis}{extra_str})\n"
            f"{_egeria_section(writer, local_reason)}"
        )


def _put_placement(sheet: DashboardSheet, placement: Placement) -> bool:
    """Replace the placement with the same ref, or append it. True if replaced. A same-named placement of the
    other kind (report vs text) is refused, as in Egeria."""
    for i, p in enumerate(sheet.placements):
        if isinstance(p, dict):
            p = Placement(**p)
        if p.ref == placement.ref:
            _refuse_kind_clash(sheet.name, placement, placement_kind(p))
            sheet.placements[i] = placement
            return True
    sheet.placements.append(placement)
    return False


class AddTextOnDashboardSheetProcessor(_DashboardSheetProcessorMixin, AsyncBaseCommandProcessor):
    """
    Processor for Add Text on Dashboard Sheet -- places literal markdown text (a section header,
    explanation or caption) on a Dashboard Sheet as an ordered placement, alongside report placements. In
    Egeria: a DisplayDataField with placementKind "text" and markdownContent. `Placement Name` is the
    placement's name (its displayName, and the local replace-by-name key).
    """

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    def supports_target_element_lookup(self) -> bool:
        return False

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        sheet_name = attributes.get("Dashboard Sheet Name", {}).get("value")
        placement_name = attributes.get("Placement Name", {}).get("value")
        content = attributes.get("MD Content", {}).get("value")
        span = attributes.get("Placement Span", {}).get("value") or "1"
        emphasis = attributes.get("Placement Emphasis", {}).get("value") or "kpi"
        perspectives = _parse_placement_perspectives(attributes)

        if not sheet_name:
            raise ValueError("Dashboard Sheet Name is required.")
        if not placement_name:
            raise ValueError("Placement Name is required.")
        if not content:
            raise ValueError("MD Content is required.")

        path = _default_store_path()
        sheets = _load_store(path)
        sheet = sheets.get(sheet_name)
        placement = Placement(ref=placement_name, span=span, emphasis=emphasis, content=content,
                              perspectives=perspectives)

        async def _work(writer: DashboardSheetEgeriaWriter):
            chain = await _placement_chain(writer, sheet_name, sheet)
            await writer.upsert_placement(chain, placement)

        writer, local_reason = await self._with_egeria(_work)

        if not sheet:
            if local_reason:
                raise ValueError(f"Dashboard Sheet '{sheet_name}' does not exist. Create it first with "
                                 f"'Create Dashboard Sheet'.")
            sheets[sheet_name] = DashboardSheet(name=sheet_name, heading=sheet_name)
            sheet = sheets.get(sheet_name)

        replaced = _put_placement(sheet, placement)
        sheets.save_to_json(path)
        verb_word = "Updated" if replaced else "Placed"
        logger.success(f"{verb_word} text placement '{placement_name}' in Dashboard Sheet '{sheet_name}'")
        extra_str = f", perspectives={','.join(perspectives)}" if perspectives else ""
        return (
            f"\n\n## {self.command.verb} Text on Dashboard Sheet\n\n"
            f"{verb_word} text placement **{placement_name}** in Dashboard Sheet **{sheet_name}** "
            f"(span={span}, emphasis={emphasis}{extra_str})\n"
            f"{_egeria_section(writer, local_reason)}"
        )


__all__ = [
    "AddTextOnDashboardSheetProcessor", "CreateDashboardSheetProcessor", "DashboardSheetEgeriaWriter",
    "FieldInfo", "LinkReportToDashboardSheetProcessor", "LOCAL_ONLY_ENV", "PERSPECTIVE_QN_OVERRIDES",
    "PERSPECTIVE_TRELLIS_NAMES", "SheetChain", "dashboard_qn", "field_placement_name", "local_only_reason", "perspective_qualified_name",
    "placement_display_name", "placement_field_properties", "placement_kind", "placement_qn", "schema_type_qn", "sheet_container_qn",
    "sheet_name_from_dashboard_qn",
]
