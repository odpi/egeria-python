"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module defines Pydantic models for **Containers** — named, ordered,
nestable layouts of placed ReportSpecs (FormatSets) — used to compose
dashboards.

Deliberately a **co-element of `FormatSet`** (`_output_format_models.py`), not
a standalone concept: same shape conventions (`name`/`aliases`/`family`),
same dict-with-alias-lookup pattern (`ContainerDict` mirrors `FormatSetDict`),
and the same local JSON persistence mechanism (`save_containers_to_json`/
`load_containers_from_json` mirror `save_format_sets_to_json`/
`load_format_sets_from_json`). The two are meant to be authored, stored, and
(eventually) migrated into Egeria-native metadata together — see
egeria-workspaces `OVERVIEW_REPORTING_MODEL.md` §10 for the design history.

A `Container` holds an ordered list of `Placement`s. Each `Placement.ref` is a
name (or alias) that resolves against either a `FormatSetDict` (a leaf
ReportSpec/tile) or a `ContainerDict` (a nested sub-container) — resolution is
the caller's job (e.g. `pyegeria.view.output_formatter` or an app-level
resolver), mirroring how `Column.detail_spec` on `FormatSet` is a plain
string reference resolved by the caller rather than a typed foreign key.

Example usage:
```python
from pyegeria.view._output_container_models import Container, Placement

container = Container(
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
    'Container',
    'ContainerDict',
    'save_containers_to_json',
    'load_containers_from_json',
]

Span = Literal["1", "2", "full"]
Emphasis = Literal["kpi", "panel"]


def save_containers_to_json(containers: Dict[str, 'Container'], file_path: str) -> None:
    """
    Save containers to a JSON file. Mirrors save_format_sets_to_json.

    Args:
        containers: The containers to save
        file_path: The path to save the file to
    """
    serializable_dict = {key: value.dict() for key, value in containers.items()}

    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

    try:
        with open(file_path, 'w') as f:
            json.dump(serializable_dict, f, indent=2)
        logger.info(f"Containers saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving containers to {file_path}: {e}")
        raise


def load_containers_from_json(file_path: str) -> Dict[str, 'Container']:
    """
    Load containers from a JSON file. Mirrors load_format_sets_from_json.

    Args:
        file_path: The path to load the file from

    Returns:
        Dict[str, Container]: The loaded containers
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        containers = {}
        for key, value in data.items():
            containers[key] = Container(**value)

        logger.info(f"Containers loaded from {file_path}")
        return containers
    except Exception as e:
        logger.error(f"Error loading containers from {file_path}: {e}")
        raise


class Placement(BaseModel):
    """
    One ordered entry in a Container's layout.

    Fields:
        ref: The name (or alias) of the placed ReportSpec/FormatSet, or of
            another Container for nesting. Resolved by the caller — this
            model does not know which dict `ref` lives in.
        span: Layout width hint — "1"/"2" (relative columns) or "full" (row width).
        emphasis: Presentation hint — "kpi" (compact tile) or "panel" (larger, detailed).
    """
    ref: str
    span: Span = "1"
    emphasis: Emphasis = "kpi"


class Container(BaseModel):
    """
    A named, ordered, nestable placement list — the unit dashboards compose
    from. A top-level Container (with no Container placing it) is a Dashboard.

    Fields:
        name: Unique identifier (mirrors FormatSetDict's dict-key convention;
            also carried on the object itself, unlike FormatSet, so a
            Container can be handed around/serialized standalone).
        heading: Display title.
        description: What the container is for.
        aliases: Alternative names for lookup (mirrors FormatSet.aliases).
        family: Optional grouping tag (mirrors FormatSet.family), e.g.
            "dashboard" (top-level, user-facing) vs "panel-library" (reusable
            sub-containers meant to be nested, not shown standalone).
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

    def merge_with(self, other: "Container") -> "Container":
        """Deep merge another Container into this one. Mirrors FormatSet.merge_with.

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


class ContainerDict(Dict[str, Container]):
    """
    A dictionary of containers, with alias-lookup/merge conveniences.
    Mirrors FormatSetDict exactly — see its docstrings for the rationale
    behind each method (name-or-alias lookup, space/dash normalization,
    family filtering, upsert-with-merge).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def find_by_name_or_alias(self, key, default=None):
        container = super().get(key, None)

        if container is None and isinstance(key, str) and " " in key:
            container = super().get(key.replace(" ", "-"), None)

        if container is None:
            for value in self.values():
                if key in value.aliases:
                    container = value
                    break

        return container if container is not None else default

    def get(self, key, default=None):
        return self.find_by_name_or_alias(key, default)

    def filter_by_family(self, family: str) -> Dict[str, Container]:
        """Return a plain dict of containers whose `family` matches (case-insensitive;
        pass "" to select entries with no family assigned)."""
        fam_norm = (family or "").strip().lower()
        result: Dict[str, Container] = {}
        for name, c in self.items():
            c_family_norm = (getattr(c, "family", None) or "").strip().lower()
            if fam_norm == "":
                if c_family_norm == "":
                    result[name] = c
            else:
                if c_family_norm == fam_norm:
                    result[name] = c
        return result

    def values(self):
        return super().values()

    def keys(self):
        return super().keys()

    def items(self):
        return super().items()

    def __getitem__(self, key):
        container = self.find_by_name_or_alias(key, None)
        if container is None:
            raise KeyError(key)
        return container

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            value = Container(**value)
        super().__setitem__(key, value)

    def __contains__(self, key):
        return self.find_by_name_or_alias(key, None) is not None

    def upsert(self, key: str, value: Union[Container, Dict]) -> None:
        """Add a container if it doesn't exist, or deep merge it if it does."""
        if isinstance(value, dict):
            value = Container(**value)

        existing = self.find_by_name_or_alias(key, None)
        if existing:
            existing.merge_with(value)
        else:
            self[key] = value

    def to_dict(self):
        return {key: value.dict() for key, value in self.items()}

    def save_to_json(self, file_path: str) -> None:
        save_containers_to_json(self, file_path)

    @classmethod
    def load_from_json(cls, file_path: str) -> 'ContainerDict':
        containers = load_containers_from_json(file_path)
        return cls(containers)
