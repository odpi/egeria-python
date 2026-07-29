"""
Dashboard Sheet Processors for Dr.Egeria v2.

Handles `Create Dashboard Sheet` and `Link Report to Dashboard Sheet` -- the
first Dr.Egeria commands that manage a purely local, pyegeria-only record
(see pyegeria.view._output_dashboard_sheet_models.DashboardSheet) instead of
an Egeria element. No OMVS calls are made.

Design: rather than bypass AsyncBaseCommandProcessor entirely, the base
class's Egeria-lookup primitives (fetch_element / resolve_element_guid) are
overridden to consult a local JSON store instead of Egeria -- so the
inherited create<->update upsert-transition, qualified-name derivation,
caching, and validate/display dry-run machinery all keep working, just
against local data. This is a first version: once Dashboard Sheet becomes a
real Egeria Collection subtype (see OVERVIEW_REPORTING_MODEL.md SS10 and the
"PLANNED" notes on the Dashboard Sheet Base / Report to Dashboard Sheet Link
Base Tinderbox bundles), these processors extend to call real OMVS methods
instead of the local store, without changing the compact command specs.

Store: PYEGERIA_DASHBOARD_SHEETS_STORE (default ~/.pyegeria/dashboard_sheets.json),
a single JSON file loaded fresh and saved back on every command -- durable
across separate `dr_egeria` invocations, unlike dashboard_sheet_registry.py's
in-memory RUNTIME store (which is for app-level consumers reading a merged
CONFIG+RUNTIME view, not for this authoring path).
"""
import os
from typing import Any, Dict, Optional

from loguru import logger

from md_processing.v2.processors import AsyncBaseCommandProcessor
from pyegeria.view._output_dashboard_sheet_models import DashboardSheet, Placement, DashboardSheetDict
from pyegeria.view.base_report_formats import select_report_spec


def _default_store_path() -> str:
    return os.path.expanduser(
        os.getenv("PYEGERIA_DASHBOARD_SHEETS_STORE", "~/.pyegeria/dashboard_sheets.json")
    )


def _load_store(path: str) -> DashboardSheetDict:
    if os.path.exists(path):
        return DashboardSheetDict.load_from_json(path)
    return DashboardSheetDict()


def _sheet_to_element(sheet: DashboardSheet) -> Dict[str, Any]:
    """Wrap a DashboardSheet in a minimal Egeria-elementHeader-shaped dict so
    the inherited pipeline's generic `element.get('elementHeader', {})...`
    patterns work unmodified against local data."""
    return {
        "elementHeader": {"guid": sheet.name, "type": {"typeName": "DashboardSheet"}},
        "properties": {
            "qualifiedName": f"Dashboard::{sheet.name}",
            "displayName": sheet.heading,
            "description": sheet.description,
        },
    }


class CreateDashboardSheetProcessor(AsyncBaseCommandProcessor):
    """Processor for Create Dashboard Sheet (and its Update transition)."""

    def derive_qualified_name(self, attributes: Optional[Dict[str, Any]] = None) -> str:
        """Override the inherited Egeria-style qn_prefix/org/version qualified-name
        derivation -- local records are keyed by their plain Dashboard Sheet Name,
        so that's what fetch_as_is()/resolve_element_guid() need to match against."""
        if attributes is None:
            attributes = self.parsed_output.get("attributes", {})
        return attributes.get("Dashboard Sheet Name", {}).get("value") or ""

    async def resolve_element_guid(self, name_or_guid: str, tech_type: Optional[str] = None) -> Optional[str]:
        if not name_or_guid:
            return None
        sheets = _load_store(_default_store_path())
        return name_or_guid if name_or_guid in sheets else None

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        sheets = _load_store(_default_store_path())
        sheet = sheets.get(guid)
        return _sheet_to_element(sheet) if sheet else None

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        name = attributes.get("Dashboard Sheet Name", {}).get("value")
        if not name:
            raise ValueError("Dashboard Sheet Name is required.")
        heading = attributes.get("Dashboard Sheet Heading", {}).get("value") or name
        description = attributes.get("Dashboard Sheet Description", {}).get("value") or ""
        family = attributes.get("Dashboard Sheet Family", {}).get("value") or None

        path = _default_store_path()
        sheets = _load_store(path)
        is_update = name in sheets
        sheets.upsert(name, DashboardSheet(name=name, heading=heading, description=description, family=family))
        sheets.save_to_json(path)

        self.parsed_output["guid"] = name
        verb_word = "Updated" if is_update else "Created"
        logger.success(f"{verb_word} Dashboard Sheet '{name}' at {path}")
        return (
            f"\n\n## {self.command.verb} Dashboard Sheet\n\n"
            f"{verb_word} Dashboard Sheet **{name}**\n\n"
            f"- **Heading**: {heading}\n"
            f"- **Description**: {description or '_(none)_'}\n"
            f"- **Family**: {family or '_(none)_'}\n"
        )


class LinkReportToDashboardSheetProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Link Report to Dashboard Sheet -- places a Report Spec
    (FormatSet) into a Dashboard Sheet as an ordered Placement. The target
    Dashboard Sheet must already exist (created via Create Dashboard Sheet);
    the Report Spec name is checked against pyegeria's report-spec registry
    as a best-effort warning (mirrors ViewProcessor's own select_report_spec
    usage) but not otherwise resolved -- FormatSets aren't Egeria elements
    either, so there's no GUID to find.
    """

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    def supports_target_element_lookup(self) -> bool:
        return False

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        sheet_name = attributes.get("Dashboard Sheet Name", {}).get("value")
        report_spec_name = attributes.get("Report Spec", {}).get("value")
        span = attributes.get("Placement Span", {}).get("value") or "1"
        emphasis = attributes.get("Placement Emphasis", {}).get("value") or "kpi"

        if not sheet_name:
            raise ValueError("Dashboard Sheet Name is required.")
        if not report_spec_name:
            raise ValueError("Report Spec is required.")

        if not select_report_spec(report_spec_name, "ANY"):
            self._add_warning(f"Report Spec '{report_spec_name}' was not found in the report registry.")

        path = _default_store_path()
        sheets = _load_store(path)
        sheet = sheets.get(sheet_name)
        if not sheet:
            raise ValueError(
                f"Dashboard Sheet '{sheet_name}' does not exist. Create it first with 'Create Dashboard Sheet'."
            )

        placement = Placement(ref=report_spec_name, span=span, emphasis=emphasis)
        replaced = False
        for i, p in enumerate(sheet.placements):
            if p.ref == report_spec_name:
                sheet.placements[i] = placement
                replaced = True
                break
        if not replaced:
            sheet.placements.append(placement)

        sheets.save_to_json(path)
        verb_word = "Updated placement of" if replaced else "Placed"
        logger.success(f"{verb_word} Report Spec '{report_spec_name}' in Dashboard Sheet '{sheet_name}'")
        return (
            f"\n\n## {self.command.verb} Report to Dashboard Sheet\n\n"
            f"{verb_word} **{report_spec_name}** in Dashboard Sheet **{sheet_name}** "
            f"(span={span}, emphasis={emphasis})\n"
        )
