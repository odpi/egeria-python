# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Read the rendered Dr.Egeria command templates that ship with pyegeria.

The templates are the files ``gen_md_cmd_templates`` renders from the compact
command specs, one per command, grouped by family, at two usage levels:
``basic`` (Common/Domain/Basic attributes) and ``advanced`` (all visible
attributes). Because they ship in the same wheel as the dispatcher that runs
them, a consumer that reads them here can never compose a command from a
template older than the executor.

Where they come from:

* An installed wheel carries them as package data under
  ``md_processing/data/templates/{basic,advanced}/<Family>/<Command>.md``
  (copied from ``sample-data/templates`` at build time by ``setup.py``).
* A source checkout or editable install has no copy there, so this module
  falls back to ``<repo>/sample-data/templates``, the generator's own output
  and the single source of truth.

Example::

    from md_processing.templates import list_templates, read_template

    for t in list_templates("basic"):
        print(t.family, t.command)
    text = read_template("Create Glossary", level="advanced")
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Optional

LEVELS = ("basic", "advanced")

__all__ = [
    "LEVELS",
    "TemplateInfo",
    "TemplateNotFound",
    "templates_root",
    "templates_source",
    "list_families",
    "list_templates",
    "find_template",
    "read_template",
]


class TemplateNotFound(LookupError):
    """No template matches the requested command (and family) at that level."""


@dataclass(frozen=True)
class TemplateInfo:
    """One rendered template.

    ``command`` is the command name from the file's ``## <Command>`` heading
    (e.g. ``"Link Term-Term Relationship"``); ``file_name`` is the file's name
    (``"Link_Term-Term_Relationship.md"``); ``resource`` is a path relative to
    the level root (``"Glossary/Link_Term-Term_Relationship.md"``).
    """

    level: str
    family: str
    command: str
    file_name: str
    resource: str


def _norm_level(level: str) -> str:
    lv = (level or "").strip().lower()
    if lv not in LEVELS:
        raise ValueError(f"Unknown template level {level!r}; expected one of {LEVELS}")
    return lv


def _packaged_root() -> Traversable:
    return resources.files("md_processing") / "data" / "templates"


def _checkout_root() -> Path:
    # <repo>/md_processing/templates.py -> <repo>/sample-data/templates
    return Path(__file__).resolve().parent.parent / "sample-data" / "templates"


@lru_cache(maxsize=None)
def _root_and_source(level: str) -> tuple[Optional[Traversable], str]:
    packaged = _packaged_root() / level
    if packaged.is_dir():
        return packaged, "package"
    checkout = _checkout_root() / level
    if checkout.is_dir():
        return checkout, "checkout"
    return None, "missing"


def templates_root(level: str = "basic") -> Traversable:
    """The directory holding the templates for ``level``.

    Raises ``FileNotFoundError`` if neither the packaged copy nor a source
    checkout's ``sample-data/templates`` is present.
    """
    lv = _norm_level(level)
    root, _ = _root_and_source(lv)
    if root is None:
        raise FileNotFoundError(
            f"No Dr.Egeria '{lv}' templates: not in the installed md_processing package "
            f"and no sample-data/templates/{lv} beside it"
        )
    return root


def templates_source(level: str = "basic") -> str:
    """Where ``level``'s templates are read from: ``"package"`` (installed
    wheel), ``"checkout"`` (source tree / editable install) or ``"missing"``."""
    return _root_and_source(_norm_level(level))[1]


def _heading_command(text: str) -> Optional[str]:
    for line in text.splitlines():
        if line.startswith("## "):
            return line[3:].strip()
    return None


@lru_cache(maxsize=None)
def _index(level: str) -> tuple[TemplateInfo, ...]:
    root = templates_root(level)
    items: list[TemplateInfo] = []
    for fam_dir in root.iterdir():
        if not fam_dir.is_dir() or fam_dir.name.startswith((".", "_")):
            continue
        for f in fam_dir.iterdir():
            if not f.is_file() or not f.name.endswith(".md"):
                continue
            command = _heading_command(f.read_text(encoding="utf-8"))
            if not command:
                command = f.name[:-3].replace("_", " ")
            items.append(TemplateInfo(
                level=level,
                family=fam_dir.name,
                command=command,
                file_name=f.name,
                resource=f"{fam_dir.name}/{f.name}",
            ))
    items.sort(key=lambda t: (t.family.lower(), t.command.lower()))
    return tuple(items)


def list_families(level: str = "basic") -> list[str]:
    """Family names (template sub-folders) at ``level``, sorted."""
    return sorted({t.family for t in _index(_norm_level(level))}, key=str.lower)


def list_templates(level: str = "basic", family: Optional[str] = None) -> list[TemplateInfo]:
    """Every template at ``level``, optionally only one family's, sorted by
    family then command."""
    items = _index(_norm_level(level))
    if family is not None:
        fam = family.strip().lower()
        items = tuple(t for t in items if t.family.lower() == fam)
    return list(items)


def _key(name: str) -> str:
    n = name.strip()
    if n.lower().endswith(".md"):
        n = n[:-3]
    return " ".join(n.replace("_", " ").split()).lower()


def find_template(command: str, level: str = "basic", family: Optional[str] = None) -> TemplateInfo:
    """The ``TemplateInfo`` for ``command`` at ``level``.

    ``command`` matches the heading name or the file name, case-insensitively,
    with ``_`` and spaces treated alike (``"Create Glossary"``,
    ``"create_glossary"`` and ``"Create_Glossary.md"`` are the same). Pass
    ``family`` if the same command name appears in more than one family.
    """
    want = _key(command)
    matches = [
        t for t in list_templates(level, family)
        if _key(t.command) == want or _key(t.file_name) == want
    ]
    if not matches:
        where = f" in family {family!r}" if family else ""
        raise TemplateNotFound(f"No {_norm_level(level)} template for {command!r}{where}")
    if len(matches) > 1:
        fams = ", ".join(sorted(t.family for t in matches))
        raise TemplateNotFound(
            f"{command!r} is in more than one family ({fams}); pass family= to choose"
        )
    return matches[0]


def read_template(command: str, level: str = "basic", family: Optional[str] = None) -> str:
    """The markdown text of ``command``'s template at ``level``."""
    info = find_template(command, level, family)
    lv = _norm_level(level)
    return (templates_root(lv) / info.family / info.file_name).read_text(encoding="utf-8")

