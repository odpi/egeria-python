"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Dashboard Sheet registry — mirrors `base_report_formats.py`'s report-spec
registry (`get_report_registry`/`register_report_specs`/`refresh_report_specs`)
for `DashboardSheet` objects (`_output_dashboard_sheet_models.py`), so the
two stay co-elements: same env-var-driven JSON config pattern, same runtime
registration API, same collision semantics.

Unlike report specs, there is no generated/built-in source here — no
Tinderbox/`refresh_specs` pipeline authors dashboard sheets as Egeria
elements (yet; see egeria-workspaces `OVERVIEW_REPORTING_MODEL.md` §10 for
the plan — Dashboard Sheet is planned to become an Egeria `Collection`
subtype). The registry is CONFIG (env-var JSON files) + RUNTIME (dynamically
registered, e.g. by the Dr.Egeria `Create Dashboard Sheet` command's
processor) only.

This module is hand-written and safe to edit — unlike `base_report_formats.py`,
nothing regenerates it.
"""

import os
from pathlib import Path
from typing import Union

from loguru import logger

from pyegeria.view._output_dashboard_sheet_models import DashboardSheet, DashboardSheetDict

__all__ = [
    'DashboardSheetCollision',
    'refresh_dashboard_sheets',
    'get_dashboard_sheet_registry',
    'register_dashboard_sheets',
    'unregister_dashboard_sheet',
    'clear_runtime_dashboard_sheets',
]

_RUNTIME_DASHBOARD_SHEETS = DashboardSheetDict()
_CONFIG_DASHBOARD_SHEETS = DashboardSheetDict()


class DashboardSheetCollision(ValueError):
    """Raised when two dashboard-sheet sources define the same sheet name."""
    pass


def _add_with_collision_check(target: DashboardSheetDict, new: DashboardSheetDict, source: str) -> None:
    for name in new.keys():
        if name in target.keys():
            raise DashboardSheetCollision(
                f"Dashboard Sheet '{name}' already defined; conflict from {source}")
    for k, v in new.items():
        target[k] = v


def _load_json_file(path: str) -> DashboardSheetDict:
    p = Path(os.path.expanduser(path)).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Dashboard sheets JSON not found: {p}")
    return DashboardSheetDict.load_from_json(str(p))


def refresh_dashboard_sheets() -> None:
    """Reload dashboard sheets from configured JSON files and optional modules.
    Environment variables:
      - PYEGERIA_DASHBOARD_SHEETS_JSON: comma-separated JSON file paths
      - PYEGERIA_DASHBOARD_SHEETS_MODULES: optional comma-separated module callables
        (pkg.mod:func or pkg.mod.func)
    Collisions across sources will raise DashboardSheetCollision.
    """
    global _CONFIG_DASHBOARD_SHEETS
    _CONFIG_DASHBOARD_SHEETS = DashboardSheetDict()

    json_paths = os.getenv("PYEGERIA_DASHBOARD_SHEETS_JSON", "").strip()
    if json_paths:
        for raw in json_paths.split(","):
            raw = raw.strip()
            if not raw:
                continue
            loaded = _load_json_file(raw)
            _add_with_collision_check(_CONFIG_DASHBOARD_SHEETS, loaded, source=f"JSON:{raw}")

    modules = os.getenv("PYEGERIA_DASHBOARD_SHEETS_MODULES", "").strip()
    if modules:
        for m in modules.split(","):
            m = m.strip()
            if not m:
                continue
            if ":" in m:
                pkg, func = m.split(":", 1)
            else:
                pkg, func = m.rsplit(".", 1)
            mod = __import__(pkg, fromlist=[func])
            loader = getattr(mod, func)
            loaded = loader()
            if not isinstance(loaded, DashboardSheetDict):
                loaded = DashboardSheetDict(loaded)
            _add_with_collision_check(_CONFIG_DASHBOARD_SHEETS, loaded, source=f"MODULE:{m}")


def get_dashboard_sheet_registry() -> DashboardSheetDict:
    """Combine config-loaded and runtime dashboard sheets. Enforce no
    duplicate names across sources."""
    combined = DashboardSheetDict()
    _add_with_collision_check(combined, _CONFIG_DASHBOARD_SHEETS, source="CONFIG")
    _add_with_collision_check(combined, _RUNTIME_DASHBOARD_SHEETS, source="RUNTIME")
    return combined


def register_dashboard_sheets(new_sheets: Union[DashboardSheetDict, dict], *, source: str = "runtime") -> None:
    """Dynamically add dashboard sheets at runtime. Raises on duplicate name."""
    global _RUNTIME_DASHBOARD_SHEETS
    if not isinstance(new_sheets, DashboardSheetDict):
        new_sheets = DashboardSheetDict(new_sheets)
    existing = get_dashboard_sheet_registry()
    for name in new_sheets.keys():
        if name in existing.keys():
            raise DashboardSheetCollision(
                f"Dashboard Sheet '{name}' already exists; cannot register from {source}")
    for k, v in new_sheets.items():
        _RUNTIME_DASHBOARD_SHEETS[k] = v


def unregister_dashboard_sheet(name: str) -> bool:
    return bool(_RUNTIME_DASHBOARD_SHEETS.pop(name, None))


def clear_runtime_dashboard_sheets() -> None:
    _RUNTIME_DASHBOARD_SHEETS.clear()
