"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module defines Pydantic models for **Dashboard Sheets** — named,
ordered, nestable layouts of placed ReportSpecs (FormatSets) — used to
compose dashboards. (Named "Dashboard Sheet" rather than "Container" to
avoid ambiguity with unrelated container concepts.)

Deliberately a **co-element of `FormatSet`** (`_output_format_models.py`), not
a standalone concept: same shape conventions (`name`/`aliases`/`family`),
same dict-with-alias-lookup pattern (`DashboardSheetDict` mirrors
`FormatSetDict`), and the same local JSON persistence mechanism
(`save_dashboard_sheets_to_json`/`load_dashboard_sheets_from_json` mirror
`save_format_sets_to_json`/`load_format_sets_from_json`). The two are meant
to be authored, stored, and (eventually) migrated into Egeria-native
metadata together — see egeria-workspaces `OVERVIEW_REPORTING_MODEL.md` §10
for the design history.

Not yet an Egeria element. **Planned**: Dashboard Sheet becomes an Egeria
`Collection` subtype (not immediate) — when that lands, this local model
retires in favor of real Egeria elements/relationships, and the matching
Dr.Egeria commands (`Create Dashboard Sheet`, `Link Report to Dashboard
Sheet` — Tinderbox-authored under the `Report` family, `Report - Refactored/
Bundles - Report/Dashboard Sheet Base` and `.../Report to Dashboard Sheet
Link Base`) switch their bundle inheritance to `Collection Base`.

A `DashboardSheet` holds an ordered list of `Placement`s. Each `Placement.ref`
is a name (or alias) that resolves against either a `FormatSetDict` (a leaf
ReportSpec/tile) or a `DashboardSheetDict` (a nested sub-sheet) — resolution
is the caller's job (e.g. `pyegeria.view.output_formatter` or an app-level
resolver), mirroring how `Column.detail_spec` on `FormatSet` is a plain
string reference resolved by the caller rather than a typed foreign key.

Example usage:
```python
from pyegeria.view._output_dashboard_sheet_models import DashboardSheet, Placement

sheet = DashboardSheet(
    name="overview-dashboard",
    heading="Egeria Overview",
    description="The system-default Overview dashboard",
    placements=[
        Placement(ref="assets", emphasis="kpi"),
        Placement(ref="people-panel", emphasis="panel", span="full"),
    ],
)
```
"""

import json
import os
from typing import Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, validator
from loguru import logger

__all__ = [
    'Placement',
    'DashboardSheet',
    'DashboardSheetDict',
    'save_dashboard_sheets_to_json',
    'load_dashboard_sheets_from_json',
]

Span = Literal["1", "2", "full"]
Emphasis = Literal["kpi", "panel"]


def save_dashboard_sheets_to_json(sheets: Dict[str, 'DashboardSheet'], file_path: str) -> None:
    """
    Save dashboard sheets to a JSON file. Mirrors save_format_sets_to_json.

    Args:
        sheets: The dashboard sheets to save
        file_path: The path to save the file to
    """
    serializable_dict = {key: value.dict() for key, value in sheets.items()}

    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

    try:
        with open(file_path, 'w') as f:
            json.dump(serializable_dict, f, indent=2)
        logger.info(f"Dashboard sheets saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving dashboard sheets to {file_path}: {e}")
        raise


def load_dashboard_sheets_from_json(file_path: str) -> Dict[str, 'DashboardSheet']:
    """
    Load dashboard sheets from a JSON file. Mirrors load_format_sets_from_json.

    Args:
        file_path: The path to load the file from

    Returns:
        Dict[str, DashboardSheet]: The loaded dashboard sheets
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        sheets = {}
        for key, value in data.items():
            sheets[key] = DashboardSheet(**value)

        logger.info(f"Dashboard sheets loaded from {file_path}")
        return sheets
    except Exception as e:
        logger.error(f"Error loading dashboard sheets from {file_path}: {e}")
        raise


class Placement(BaseModel):
    """
    One ordered entry in a Dashboard Sheet's layout.

    Fields:
        ref: The name (or alias) of the placed ReportSpec/FormatSet, or of
            another Dashboard Sheet for nesting. Resolved by the caller —
            this model does not know which dict `ref` lives in. For a text
            placement (`content` set), `ref` is instead the placement's own
            stable identifying name (Dr.Egeria's `Placement Name`) — not
            resolved against anything, just the replace-by-name key.
        span: Layout width hint — "1"/"2" (relative columns) or "full" (row width).
        emphasis: Presentation hint — "kpi" (compact tile) or "panel" (larger, detailed).
        content: Literal markdown text for a text placement (Dr.Egeria `Place
            Text on Dashboard Sheet` / `MD Content`) — section headers,
            explanations, captions. None for a Report/Sheet placement. A
            consuming app checks this before attempting to resolve `ref`
            against a Report or Sheet, since text needs no such lookup.
        perspectives: Viewer-role tags this placement is relevant to (e.g.
            "governance", "steward" — the same vocabulary
            `overview_specs.PERSP_KPIS`/`question_spec.perspectives` already
            uses for Overview's own perspective filtering,
            `overview_containers.view_for_perspective()`; egeria-workspaces
            BACKLOG.md NEXT-19). Empty list (the default) means "relevant to
            every perspective" — a consumer filtering by perspective should
            keep an untagged placement rather than hide it, the same
            fail-open default `view_for_perspective` uses for sub-containers.
        detail_spec: Optional drill-down target — the name of another Report
            Spec/FormatSet a consuming app can navigate to for more detail on
            this placement's result, mirroring `Attribute.detail_spec` on
            `FormatSet` (`_output_format_models.py`) exactly — same field
            name, same "a plain string reference resolved by the caller"
            contract this whole module's docstring already describes for
            `Placement.ref` (egeria-workspaces BACKLOG.md NEXT-21). None
            means this placement has no drill-down target.
    """
    ref: str
    span: Span = "1"
    emphasis: Emphasis = "kpi"
    content: Optional[str] = None
    perspectives: List[str] = Field(default_factory=list)
    detail_spec: Optional[str] = None


class DashboardSheet(BaseModel):
    """
    A named, ordered, nestable placement list — the unit dashboards compose
    from. A top-level Dashboard Sheet (with no Dashboard Sheet placing it) is
    a Dashboard.

    Fields:
        name: Unique identifier (mirrors FormatSetDict's dict-key convention;
            also carried on the object itself, unlike FormatSet, so a
            DashboardSheet can be handed around/serialized standalone).
        heading: Display title.
        description: What the sheet is for.
        aliases: Alternative names for lookup (mirrors FormatSet.aliases).
        family: Optional grouping tag (mirrors FormatSet.family), e.g.
            "dashboard" (top-level, user-facing) vs "panel-library" (reusable
            sub-sheets meant to be nested, not shown standalone).
        placements: Ordered list of Placement entries.
    """
    name: str
    heading: str
    description: str = ""
    aliases: List[str] = Field(default_factory=list)
    family: Optional[str] = None
    placements: List[Union[Placement, Dict]] = Field(default_factory=list)

    @validator('placements', pre=True)
    def validate_placements(cls, v):
        """Convert dictionary placements to Placement objects."""
        result = []
        for item in v:
            if isinstance(item, dict):
                result.append(Placement(**item))
            else:
                result.append(item)
        return result

    def dict(self, *args, **kwargs):
        """Override dict method to convert Placement objects back to dictionaries."""
        result = super().dict(*args, **kwargs)
        result['placements'] = [
            p if isinstance(p, dict) else p.dict() for p in self.placements
        ]
        return result

    def get(self, key, default=None):
        """Dictionary-like get method for backward compatibility."""
        if hasattr(self, key):
            return getattr(self, key)
        return default

    def merge_with(self, other: "DashboardSheet") -> "DashboardSheet":
        """Deep merge another DashboardSheet into this one. Mirrors FormatSet.merge_with.

        Updates simple fields (heading, description, family) if the other one
        has non-empty values. Placements are merged by `ref`: a placement
        with a matching `ref` is replaced, otherwise appended — order of
        first appearance is preserved for existing refs; new refs append at
        the end (append-only merge, not a full reorder)."""
        if other.heading:
            self.heading = other.heading
        if other.description:
            self.description = other.description
        if other.family:
            self.family = other.family

        if other.aliases:
            existing_aliases = set(self.aliases or [])
            existing_aliases.update(other.aliases)
            self.aliases = sorted(list(existing_aliases))

        for other_p in other.placements:
            if isinstance(other_p, dict):
                other_p = Placement(**other_p)
            found = False
            for i, existing_p in enumerate(self.placements):
                if isinstance(existing_p, dict):
                    existing_p = Placement(**existing_p)
                    self.placements[i] = existing_p
                if existing_p.ref == other_p.ref:
                    self.placements[i] = other_p
                    found = True
                    break
            if not found:
                self.placements.append(other_p)

        return self


class DashboardSheetDict(Dict[str, DashboardSheet]):
    """
    A dictionary of dashboard sheets, with alias-lookup/merge conveniences.
    Mirrors FormatSetDict exactly — see its docstrings for the rationale
    behind each method (name-or-alias lookup, space/dash normalization,
    family filtering, upsert-with-merge).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def find_by_name_or_alias(self, key, default=None):
        sheet = super().get(key, None)

        if sheet is None and isinstance(key, str) and " " in key:
            sheet = super().get(key.replace(" ", "-"), None)

        if sheet is None:
            for value in self.values():
                if key in value.aliases:
                    sheet = value
                    break

        return sheet if sheet is not None else default

    def get(self, key, default=None):
        return self.find_by_name_or_alias(key, default)

    def filter_by_family(self, family: str) -> Dict[str, DashboardSheet]:
        """Return a plain dict of dashboard sheets whose `family` matches
        (case-insensitive; pass "" to select entries with no family assigned)."""
        fam_norm = (family or "").strip().lower()
        result: Dict[str, DashboardSheet] = {}
        for name, s in self.items():
            s_family_norm = (getattr(s, "family", None) or "").strip().lower()
            if fam_norm == "":
                if s_family_norm == "":
                    result[name] = s
            else:
                if s_family_norm == fam_norm:
                    result[name] = s
        return result

    def values(self):
        return super().values()

    def keys(self):
        return super().keys()

    def items(self):
        return super().items()

    def __getitem__(self, key):
        sheet = self.find_by_name_or_alias(key, None)
        if sheet is None:
            raise KeyError(key)
        return sheet

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            value = DashboardSheet(**value)
        super().__setitem__(key, value)

    def __contains__(self, key):
        return self.find_by_name_or_alias(key, None) is not None

    def upsert(self, key: str, value: Union[DashboardSheet, Dict]) -> None:
        """Add a dashboard sheet if it doesn't exist, or deep merge it if it does."""
        if isinstance(value, dict):
            value = DashboardSheet(**value)

        existing = self.find_by_name_or_alias(key, None)
        if existing:
            existing.merge_with(value)
        else:
            self[key] = value

    def to_dict(self):
        return {key: value.dict() for key, value in self.items()}

    def save_to_json(self, file_path: str) -> None:
        save_dashboard_sheets_to_json(self, file_path)

    @classmethod
    def load_from_json(cls, file_path: str) -> 'DashboardSheetDict':
        sheets = load_dashboard_sheets_from_json(file_path)
        return cls(sheets)
