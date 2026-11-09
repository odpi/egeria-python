"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Dashboard Sheet registry — mirrors `base_report_formats.py`'s report-spec
registry (`get_report_registry`/`register_report_specs`/`refresh_report_specs`)
for `DashboardSheet` objects (`_output_dashboard_sheet_models.py`), so the
two stay co-elements: same env-var-driven JSON config pattern, same runtime
registration API, same collision semantics.

Unlike report specs, there is no generated/built-in source here. The tiers,
lowest first:
  - EGERIA: sheets held in Egeria 6.3 as Dashboard element chains
    (`pyegeria.view.dashboards`), loaded with `refresh_egeria_dashboard_sheets(client)`
    or set with `set_egeria_dashboard_sheets(...)`. Never fetched implicitly: reading
    the registry makes no Egeria call.
  - CONFIG (env-var JSON files) and RUNTIME (registered at run time): the local
    sources. Same precedence as report specs: a local sheet overrides a same-named
    Egeria sheet, with one warning per name per process; never raised.
`get_dashboard_sheet_tier(name)` says which tier a sheet came from.

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
    'clear_egeria_dashboard_sheets',
    'get_dashboard_sheet_tier',
    'refresh_egeria_dashboard_sheets',
    'set_egeria_dashboard_sheets',
    'refresh_dashboard_sheets',
    'get_dashboard_sheet_registry',
    'register_dashboard_sheets',
    'unregister_dashboard_sheet',
    'clear_runtime_dashboard_sheets',
]

_RUNTIME_DASHBOARD_SHEETS = DashboardSheetDict()
_CONFIG_DASHBOARD_SHEETS = DashboardSheetDict()
_EGERIA_DASHBOARD_SHEETS = DashboardSheetDict()
_REGISTRY_TIERS: dict = {}
_SHADOW_WARNED: set = set()


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
    """Combine the Egeria, config-loaded and runtime dashboard sheets.

    The local sources (CONFIG, RUNTIME) must not repeat a name between them (that raises, as before). A
    local sheet overrides a same-named Egeria sheet: the Egeria one is left out, with one warning per name
    per process."""
    local = DashboardSheetDict()
    _add_with_collision_check(local, _CONFIG_DASHBOARD_SHEETS, source="CONFIG")
    _add_with_collision_check(local, _RUNTIME_DASHBOARD_SHEETS, source="RUNTIME")

    combined = DashboardSheetDict()
    tiers = {}
    for name, sheet in _EGERIA_DASHBOARD_SHEETS.items():
        if name in local.keys():
            if name not in _SHADOW_WARNED:
                _SHADOW_WARNED.add(name)
                logger.warning(f"Dashboard Sheet '{name}' is defined locally and held in Egeria; the local "
                               f"definition is used.")
            continue
        combined[name] = sheet
        tiers[name] = "egeria"
    for name, sheet in local.items():
        combined[name] = sheet
        tiers[name] = "local"
    _REGISTRY_TIERS.clear()
    _REGISTRY_TIERS.update(tiers)
    return combined


def get_dashboard_sheet_tier(name: str):
    """"egeria" or "local" for a sheet in the last registry read, else None."""
    if not _REGISTRY_TIERS:
        get_dashboard_sheet_registry()
    return _REGISTRY_TIERS.get(name)


def set_egeria_dashboard_sheets(sheets) -> None:
    """Replace the EGERIA tier with these sheets (a DashboardSheetDict, a dict, or a list of sheets)."""
    global _EGERIA_DASHBOARD_SHEETS
    if isinstance(sheets, list):
        sheets = {s.name: s for s in sheets}
    _EGERIA_DASHBOARD_SHEETS = sheets if isinstance(sheets, DashboardSheetDict) else DashboardSheetDict(sheets)


def refresh_egeria_dashboard_sheets(client=None) -> int:
    """Load the EGERIA tier from Egeria (`pyegeria.view.dashboards.list_dashboard_sheets`). Returns the
    number of sheets. With no client, one is made from the environment."""
    from pyegeria.view.dashboards import list_dashboard_sheets
    sheets = list_dashboard_sheets(client)
    set_egeria_dashboard_sheets(sheets)
    return len(sheets)


def clear_egeria_dashboard_sheets() -> None:
    _EGERIA_DASHBOARD_SHEETS.clear()
    _SHADOW_WARNED.clear()


def register_dashboard_sheets(new_sheets: Union[DashboardSheetDict, dict], *, source: str = "runtime") -> None:
    """Dynamically add dashboard sheets at runtime. Raises on duplicate name."""
    global _RUNTIME_DASHBOARD_SHEETS
    if not isinstance(new_sheets, DashboardSheetDict):
        new_sheets = DashboardSheetDict(new_sheets)
    existing = DashboardSheetDict()
    _add_with_collision_check(existing, _CONFIG_DASHBOARD_SHEETS, source="CONFIG")
    _add_with_collision_check(existing, _RUNTIME_DASHBOARD_SHEETS, source="RUNTIME")
    for name in new_sheets.keys():  # a runtime sheet may override an Egeria one; not another local one
        if name in existing.keys():
            raise DashboardSheetCollision(
                f"Dashboard Sheet '{name}' already exists; cannot register from {source}")
    for k, v in new_sheets.items():
        _RUNTIME_DASHBOARD_SHEETS[k] = v


def unregister_dashboard_sheet(name: str) -> bool:
    return bool(_RUNTIME_DASHBOARD_SHEETS.pop(name, None))


def clear_runtime_dashboard_sheets() -> None:
    _RUNTIME_DASHBOARD_SHEETS.clear()
