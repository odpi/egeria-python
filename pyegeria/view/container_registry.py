"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Container registry — mirrors `base_report_formats.py`'s report-spec registry
(`get_report_registry`/`register_report_specs`/`refresh_report_specs`) for
`Container` objects (`_output_container_models.py`), so the two stay
co-elements: same env-var-driven JSON config pattern, same runtime
registration API, same collision semantics.

Unlike report specs, there is no generated/built-in source here — no
Tinderbox/`refresh_specs` pipeline authors containers (yet; see
egeria-workspaces `OVERVIEW_REPORTING_MODEL.md` §10 for the plan). The
registry is CONFIG (env-var JSON files) + RUNTIME (dynamically registered,
e.g. by a future Dr.Egeria `Create Container` command's processor) only.

This module is hand-written and safe to edit — unlike `base_report_formats.py`,
nothing regenerates it.
"""

import os
from pathlib import Path
from typing import Union

from loguru import logger

from pyegeria.view._output_container_models import Container, ContainerDict

__all__ = [
    'ContainerCollision',
    'refresh_containers',
    'get_container_registry',
    'register_containers',
    'unregister_container',
    'clear_runtime_containers',
]

_RUNTIME_CONTAINERS = ContainerDict()
_CONFIG_CONTAINERS = ContainerDict()


class ContainerCollision(ValueError):
    """Raised when two container sources define the same container name."""
    pass


def _add_with_collision_check(target: ContainerDict, new: ContainerDict, source: str) -> None:
    for name in new.keys():
        if name in target.keys():
            raise ContainerCollision(
                f"Container '{name}' already defined; conflict from {source}")
    for k, v in new.items():
        target[k] = v


def _load_json_file(path: str) -> ContainerDict:
    p = Path(os.path.expanduser(path)).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Containers JSON not found: {p}")
    return ContainerDict.load_from_json(str(p))


def refresh_containers() -> None:
    """Reload containers from configured JSON files and optional modules.
    Environment variables:
      - PYEGERIA_CONTAINERS_JSON: comma-separated JSON file paths
      - PYEGERIA_CONTAINERS_MODULES: optional comma-separated module callables
        (pkg.mod:func or pkg.mod.func)
    Collisions across sources will raise ContainerCollision.
    """
    global _CONFIG_CONTAINERS
    _CONFIG_CONTAINERS = ContainerDict()

    json_paths = os.getenv("PYEGERIA_CONTAINERS_JSON", "").strip()
    if json_paths:
        for raw in json_paths.split(","):
            raw = raw.strip()
            if not raw:
                continue
            loaded = _load_json_file(raw)
            _add_with_collision_check(_CONFIG_CONTAINERS, loaded, source=f"JSON:{raw}")

    modules = os.getenv("PYEGERIA_CONTAINERS_MODULES", "").strip()
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
            if not isinstance(loaded, ContainerDict):
                loaded = ContainerDict(loaded)
            _add_with_collision_check(_CONFIG_CONTAINERS, loaded, source=f"MODULE:{m}")


def get_container_registry() -> ContainerDict:
    """Combine config-loaded and runtime containers. Enforce no duplicate
    names across sources."""
    combined = ContainerDict()
    _add_with_collision_check(combined, _CONFIG_CONTAINERS, source="CONFIG")
    _add_with_collision_check(combined, _RUNTIME_CONTAINERS, source="RUNTIME")
    return combined


def register_containers(new_containers: Union[ContainerDict, dict], *, source: str = "runtime") -> None:
    """Dynamically add containers at runtime. Raises on duplicate name."""
    global _RUNTIME_CONTAINERS
    if not isinstance(new_containers, ContainerDict):
        new_containers = ContainerDict(new_containers)
    existing = get_container_registry()
    for name in new_containers.keys():
        if name in existing.keys():
            raise ContainerCollision(
                f"Container '{name}' already exists; cannot register from {source}")
    for k, v in new_containers.items():
        _RUNTIME_CONTAINERS[k] = v


def unregister_container(name: str) -> bool:
    return bool(_RUNTIME_CONTAINERS.pop(name, None))


def clear_runtime_containers() -> None:
    _RUNTIME_CONTAINERS.clear()
