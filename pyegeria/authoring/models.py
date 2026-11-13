# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""The authoring API's types: drafts, the gate switches, and the results of validate and diff.

Three kinds of draft (BRIEF-PYEGERIA-AUTHORING-API-PHASE1-2026-11-13 §3):

- `SpecDraft`: a report spec (a `FormatSet`) with its label, qualified name, and where it came from;
- `ReportDraft`: a Report, the "what to run" of a placement: a spec label, an output format, and its
  parameters, typed against what the spec declares;
- `SheetDraft`: a dashboard sheet: heading, family and ordered placements (a Report or text).

`Draft` is their union, told apart by `kind`.
"""
from __future__ import annotations

import os
from typing import Annotated, Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, model_validator

from pyegeria.view._output_format_models import FormatSet

KINDS = ("spec", "report", "sheet")
Kind = Literal["spec", "report", "sheet"]


# ── The gates (§2): built as switches until the owner decides ────────────────

class AuthoringGates(BaseModel):
    """The undecided design gates, as switches. The defaults are the brief's "until it's decided".

    - **D7, decided "Keep both for now"** `camel_copy`: a Report's parameters go to the typed
      `reportParameters` document AND to the camelCase `additionalProperties` keys today's Portal and EA read,
      always. Kept as a switch (default both, no drop date); Dr.Egeria's Report processor reads the same switch
      from `PYEGERIA_REPORT_CAMEL_PARAMS` (`camel_copy_env()`). Reading prefers `reportParameters`.
    - **D14, decided "Follow latest, pin allowed"** `allow_pinning`: a Report follows its spec's latest version
      by default and may pin one (`pinned_version`), resolved as the user (pyegeria.authoring.versions).
      Published versions are treated as immutable in effect.
    - **D16, decided "Egeria, private, 30-day prune"** `draft_backend`: "egeria" (the element itself, zoned
      private to the author, written as the author; EgeriaDraftStore) is the default for apps; "local" is for
      tests and offline use.
    - **D4** (sheet store, pending) `sheet_target`: "egeria" only. The API never writes the local sheet store
      (`~/.pyegeria/dashboard_sheets.json`).
    """
    model_config = ConfigDict(frozen=True)

    camel_copy: bool = True
    allow_pinning: bool = True
    draft_backend: Literal["local", "egeria"] = "egeria"
    sheet_target: Literal["egeria"] = "egeria"


CAMEL_COPY_ENV = "PYEGERIA_REPORT_CAMEL_PARAMS"


def camel_copy_env() -> bool:
    """D7, as Dr.Egeria's Report processor reads it: on unless PYEGERIA_REPORT_CAMEL_PARAMS is 0/false/no/off."""
    return os.environ.get(CAMEL_COPY_ENV, "1").strip().lower() not in ("0", "false", "no", "off")


def default_gates() -> AuthoringGates:
    """The gates in force: the brief's defaults, with D7 following PYEGERIA_REPORT_CAMEL_PARAMS."""
    return AuthoringGates(camel_copy=camel_copy_env())


# ── Drafts ────────────────────────────────────────────────────────────────────

class _DraftBase(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    #: Where it came from: "prototype:<kind>:<label>" or "template:<name>" (new_from), None for a new draft.
    derived_from: Optional[str] = None
    #: The Egeria version this draft was loaded at (load_held), None for a draft never held.
    base_version: Optional[int] = None
    #: The Egeria GUID it was loaded from, when held.
    guid: Optional[str] = None
    #: What load_held or new_from could not read or carry over, in words (never silent).
    notes: List[str] = Field(default_factory=list)


class SpecDraft(_DraftBase):
    """A report spec draft: a `FormatSet` with its label (`ReportSpec::<label>` in Egeria)."""
    kind: Literal["spec"] = "spec"
    label: str
    format_set: FormatSet
    qualified_name: Optional[str] = None

    @model_validator(mode="after")
    def _qn(self):
        if not self.qualified_name:
            self.qualified_name = f"ReportSpec::{self.label}"
        return self


class ReportDraft(_DraftBase):
    """A Report draft: the spec it runs, its output format and its parameters.

    `parameters` uses the spec's own (snake_case) parameter names: `search_string`, `page_size`,
    `limit_result_by_status`, `collection_guid`, ... `analytic_params` are an analytic routine's.
    `pinned_version` (D14): None follows the spec's latest version; a number pins that version."""
    kind: Literal["report"] = "report"
    display_name: str
    qualified_name: Optional[str] = None
    description: Optional[str] = None
    spec: str
    output_format: str = "DICT"
    parameters: Dict[str, Any] = Field(default_factory=dict)
    analytic_params: Dict[str, Any] = Field(default_factory=dict)
    pinned_version: Optional[int] = None


class SheetPlacement(BaseModel):
    """One placement of a sheet: a Report (by its display name) or text (markdown, with a placement name)."""
    report: Optional[str] = None
    text: Optional[str] = None
    #: The placement's own name: required for text, the Report's name for a report placement.
    name: Optional[str] = None
    span: Literal["1", "2", "full"] = "1"
    emphasis: Literal["kpi", "panel"] = "kpi"
    perspectives: List[str] = Field(default_factory=list)
    detail_spec: Optional[str] = None

    @model_validator(mode="after")
    def _one_of(self):
        if (self.report is None) == (self.text is None):
            raise ValueError("a placement is either a report or text: give exactly one of report / text")
        if self.text is not None and not (self.name or "").strip():
            raise ValueError("a text placement needs a name (its Placement Name)")
        if self.report is not None and not self.name:
            self.name = self.report
        return self

    @property
    def kind(self) -> str:
        return "report" if self.report is not None else "text"


class SheetDraft(_DraftBase):
    """A dashboard sheet draft (`Dashboard::<name>` in Egeria)."""
    kind: Literal["sheet"] = "sheet"
    name: str
    heading: str
    description: str = ""
    family: Optional[str] = None
    perspectives: List[str] = Field(default_factory=list)
    placements: List[SheetPlacement] = Field(default_factory=list)


Draft = Annotated[Union[SpecDraft, ReportDraft, SheetDraft], Field(discriminator="kind")]


class DraftEnvelope(BaseModel):
    """A draft with its kind, for storage and transport (`DraftEnvelope.model_validate({"draft": {...}})`)."""
    draft: Draft


def as_draft(value: Any) -> Union[SpecDraft, ReportDraft, SheetDraft]:
    """A draft object from a draft or its dict form (with `kind`)."""
    if isinstance(value, (SpecDraft, ReportDraft, SheetDraft)):
        return value
    return DraftEnvelope.model_validate({"draft": value}).draft


def draft_key(draft: Union[SpecDraft, ReportDraft, SheetDraft]) -> str:
    """The draft's own name: the spec label, the Report's display name or the sheet name."""
    if isinstance(draft, SpecDraft):
        return draft.label
    if isinstance(draft, ReportDraft):
        return draft.display_name
    return draft.name


# ── Results ───────────────────────────────────────────────────────────────────

class ValidationResult(BaseModel):
    """What validate found. `ok` is False when there is any error. `not_applied` lists what the document
    would not send; `checked` and `not_checked` say what was and was not looked at, so silence is never
    read as a pass."""
    ok: bool = True
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    not_applied: List[str] = Field(default_factory=list)
    checked: List[str] = Field(default_factory=list)
    not_checked: List[str] = Field(default_factory=list)
    dr_egeria: Optional[Dict[str, Any]] = None

    def error(self, words: str) -> None:
        if words not in self.errors:
            self.errors.append(words)
        self.ok = False

    def warn(self, words: str) -> None:
        if words not in self.warnings:
            self.warnings.append(words)


class Change(BaseModel):
    """One difference between two drafts. `area`: field, column, parameter, placement, format."""
    area: str
    name: str
    change: Literal["added", "removed", "changed"]
    before: Any = None
    after: Any = None
    breaking: bool = False
    why: Optional[str] = None


class Diff(BaseModel):
    changes: List[Change] = Field(default_factory=list)

    @property
    def breaking(self) -> List[Change]:
        return [c for c in self.changes if c.breaking]

    def summary(self) -> Dict[str, Any]:
        return {"changes": [c.model_dump() for c in self.changes],
                "breaking": [c.model_dump() for c in self.breaking]}


class AuthoringRefused(ValueError):
    """The request can't be carried out; the words say why and what to do instead."""
