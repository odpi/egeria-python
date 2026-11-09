"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Analytic function registry — the "what analytic routines exist to plug into
a FormatSet action's `analytic_function` (Dr.Egeria's `extra_find`)" catalog.

Mirrors `dashboard_sheet_registry.py`'s shape (same env-var-driven JSON/module
config pattern, same runtime registration API, same collision semantics) so
the three registries (report specs, dashboard sheets, analytic functions)
stay consistent for anything that needs to browse or author against them --
Egeria Explorer, Egeria Advisor's report-spec builder, and
`format_set_executor.py`'s own resolution of `analytic_function` declarations.

Unlike report specs, there is no generated/Tinderbox source here (yet) --
BUILTINS is a hand-written list of the analytic functions that already exist
in `pyegeria.view.overview_metrics` (all proven live via the Overview
dashboard's own `/api/overview/*` endpoints; none of this is new analytics,
just registry wiring for functions that already work). A JSON-file-backed
CONFIG tier and a future Egeria-Asset-backed tier are planned as the registry
grows past what's worth hand-writing here (BACKLOG.md NEXT-14 successor
item) -- this module is hand-written and safe to edit, unlike
`base_report_formats.py`.

Each `AnalyticFunctionSpec.function` is a dotted import path, exactly the
string a FormatSet's `extra_find` (compiled into `ActionParameter.analytic_function`)
carries, and exactly what `format_set_executor._resolve_analytic_function`
resolves at call time. `params` documents the function's real keyword
arguments (excluding its leading client argument(s) -- those are its declared
`inputs`, which the executor supplies by role, see `role_supply`) for anything that wants
to render a param-entry form (Egeria Advisor) or a reference doc (Egeria
Explorer), not for validation -- there is deliberately no fixed
required/optional whitelist enforced at call time (see `ActionParameter`'s
docstring in `_output_format_models.py`); an unexpected keyword just raises
Python's own TypeError.
"""

from __future__ import annotations

import os
import re
import warnings
from importlib.metadata import entry_points
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

from loguru import logger
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

__all__ = [
    'AnalyticParam',
    'AnalyticFunctionSpec',
    'AnalyticActionSpec',
    'AnalyticDeclaration',
    'RoutineDeclaration',
    'ParamDeclaration',
    'Binding',
    'TileSafety',
    'Admission',
    'ROUTINE_KINDS',
    'BINDING_KINDS',
    'PARAM_CATEGORIES',
    'INPUT_ROLES',
    'get_routine_registry',
    'routine_declaration_errors',
    'MeasureDeclaration',
    'BasisDeclaration',
    'AbsenceSentences',
    'FieldDeclaration',
    'FieldCompanion',
    'CategoriesDeclaration',
    'ListDeclaration',
    'ROW_SHAPES',
    'RESULT_KINDS',
    'POPULATIONS',
    'COMPLETENESS',
    'FIELD_KINDS',
    'FIELD_TYPES',
    'CELL_COMPANIONS',
    'ABSENCE_STATES',
    'canonical_absence_state',
    'KNOWN_ANALYTIC_SOURCES',
    'AnalyticRegistryCollision',
    'refresh_analytic_functions',
    'ANALYTIC_ENTRY_POINT_GROUP',
    'analytic_entry_point_errors',
    'get_analytic_registry',
    'analytic_registry_payload',
    'register_analytic_functions',
    'unregister_analytic_function',
    'clear_runtime_analytic_functions',
]


# Known values for AnalyticFunctionSpec.source (ISSUE-149). Suggestive, not a closed list:
# ods = the operational data store, egeria = Egeria metadata, resource = the resource itself.
KNOWN_ANALYTIC_SOURCES = {"ods", "egeria", "resource"}


class AnalyticParam(BaseModel):
    """One keyword argument an analytic function accepts (beyond its leading
    client argument(s), which the executor supplies automatically)."""
    name: str
    type: str = "str"
    required: bool = False
    default: Optional[Any] = None
    description: str = ""
    #: What the parameter changes (PARAM_CATEGORIES): content, shape or performance (RS-W2-2).
    category: Literal["content", "shape", "performance"] = "content"


class AnalyticActionSpec(BaseModel):
    """A composite/derived analytic action, formalizing the pattern
    `ai_ready_assets` pioneered by hand (see its docstring) into a declared
    shape (BACKLOG.md NEXT-18, egeria-workspaces): a data-producing **fetch**
    step (typically one of this module's own `find_*`-backed functions, e.g.
    `counts_by_type`) whose raw result is passed to an optional **analytic**
    step, which may itself fetch further related data if needed (e.g. follow
    a relationship to enrich -- exactly what `ai_ready_assets` already does
    inline, just as an undeclared implementation detail rather than a named
    step). Both `fetch` and `analytic` are dotted import paths, resolved and
    client-bound the same way a plain `AnalyticFunctionSpec.function` is:
    by the fetch routine's declared `inputs` (see
    `format_set_executor.run_analytic_action` for the two-step invocation
    itself, and `role_supply` for how inputs are supplied).

    Deliberately *not* concerned with which of the resulting attributes
    appear in a given output (TABLE/REPORT/KPI/...) -- that selection is
    `Format.attributes`' existing job (its `key` projects a named field out
    of whatever dict the action returns), unchanged by this model. An action
    ends at producing the full attribute set; formatting picks from it.

    A future non-local step (e.g. a Prefect flow or other remote service,
    rather than an in-process Python callable) would only need `fetch`/
    `analytic` to grow beyond a plain dotted-path string -- not designed
    here, deliberately parked pending that real use case."""
    fetch: str
    analytic: Optional[str] = None
    fetch_params: List[AnalyticParam] = Field(default_factory=list)
    analytic_params: List[AnalyticParam] = Field(default_factory=list)


# Declaration (ISSUE-170): what an analytic function says about its own results,
# so a screen, report or chat answer can show them with no code written for that
# function. The minimum of trellis-analytics' `Declaration` (result kind, measures
# with unit/as-of/basis, the four absence sentences), with the same field names and
# vocabulary, so a trellis declaration validates here too; its richer blocks
# (extents, confidence, answers, ...) are ignored by this model, not refused.

#: The fixed result-kind vocabulary (trellis `RESULT_KINDS`).
RESULT_KINDS = ("measure", "series", "distribution", "list", "graph", "finding", "proposal", "table")

#: The four ways a result can be absent, each a sentence the function declares. Envelope states
#: map onto them: nothing_found -> nothing_found; not_established -> not_measured (or
#: not_permitted, told apart by the reason); not_applicable -> not_applicable.
ABSENCE_STATES = ("not_measured", "not_permitted", "not_applicable", "nothing_found")

#: The word 0.2 / 6.2.22 used for `nothing_found`. Read everywhere, written nowhere (RS-W1-1).
LEGACY_NOTHING_FOUND = "measured_nothing"


def canonical_absence_state(state: Any) -> Any:
    """The current absence word for `state`: the legacy `measured_nothing` reads as `nothing_found`;
    every other value is returned unchanged."""
    return "nothing_found" if state == LEGACY_NOTHING_FOUND else state


def _words(value: Any) -> str:
    return " ".join(str(value or "").split())


class BasisDeclaration(BaseModel):
    """The whole a counted measure is part of, so "456 of 1,236 columns" is derived, not written."""
    denominator_field: str  # the result field holding the whole, e.g. "column_count"
    denominator_label: str  # the whole in words, plural, e.g. "columns"

    @model_validator(mode="after")
    def _filled(self) -> "BasisDeclaration":
        if not _words(self.denominator_field) or not _words(self.denominator_label):
            raise ValueError("a basis needs both denominator_field and denominator_label")
        return self


#: The two populations a count can be taken over (trellis `POPULATIONS`, RS-W1-1 §5). `viewer`: what
#: the caller may see (Egeria pushDown=false, or any find); `repository`: the whole repository, fast,
#: with no per-element visibility check (pushDown=true).
POPULATIONS = ("viewer", "repository")

#: §5 completeness (trellis `COMPLETENESS`), replacing the boolean `capped_field`. A boolean result
#: field still reads: true is `lower_bound`, false is `complete`.
COMPLETENESS = ("complete", "lower_bound", "unknown")


def _is_fraction(unit: str) -> bool:
    """Does this unit say a share rather than a count (trellis `is_fraction`)? Its whole is in its words."""
    u = " ".join(str(unit or "").lower().split())
    return u.startswith(("fraction", "ratio", "percent", "share", "proportion")) or "(0-1)" in u or "%" in u


class MeasureDeclaration(BaseModel):
    """One number a function reports. A number never travels without its unit and its as-of.

    `as_of` names the result field saying when the value is of; `run.as_of` names the call's own
    `as_of` argument (None = when it ran), for a routine whose result carries no time of its own.
    `completeness_field` names the result field that says the value may be incomplete (one of
    COMPLETENESS, or a boolean: true = only a lower bound). `capped_field` is its old name, read
    with a DeprecationWarning. `population` is the population the value is counted in: always,
    or by default when the routine takes a `population` parameter (the caller may pass the other
    one). Empty when the server default applies. A `repository` value includes elements the viewer
    may not be able to see."""
    name: str
    unit: str  # in words, plural where it counts things: "tables", "fraction of rows (0-1)"
    as_of: str  # the result field saying when this was measured, e.g. "asOf"; or run.as_of
    value_field: str  # the result field holding the value; dotted for nested, trailing [] counts a list
    basis: Optional[BasisDeclaration] = None
    completeness_field: str = ""
    population: str = ""

    @model_validator(mode="before")
    @classmethod
    def _legacy_capped_field(cls, data: Any) -> Any:
        if isinstance(data, dict) and "capped_field" in data:
            data = dict(data)
            capped = data.pop("capped_field")
            if _words(data.get("completeness_field")) and _words(capped) != _words(data["completeness_field"]):
                raise ValueError(f"measure '{data.get('name', '')}' declares capped_field and completeness_field: "
                                 "capped_field is the old word for completeness_field, so declare that only")
            data["completeness_field"] = capped
            warnings.warn(f"measure '{data.get('name', '')}': capped_field is deprecated; use completeness_field",
                          DeprecationWarning, stacklevel=2)
        return data

    @property
    def capped_field(self) -> str:
        """The old name for `completeness_field`. Read-only; warns."""
        warnings.warn("MeasureDeclaration.capped_field is deprecated; use completeness_field",
                      DeprecationWarning, stacklevel=2)
        return self.completeness_field

    @field_validator("population")
    @classmethod
    def _population(cls, value: str) -> str:
        if value and value not in POPULATIONS:
            raise ValueError(f"population '{value}' is not one of {', '.join(POPULATIONS)}")
        return value

    @model_validator(mode="after")
    def _filled(self) -> "MeasureDeclaration":
        empty = [f for f in ("name", "unit", "as_of", "value_field") if not _words(getattr(self, f))]
        if empty:
            raise ValueError(f"measure '{self.name}' declares no {', '.join(empty)}: "
                             "a number never travels without its unit and its as-of")
        if self.basis is not None and _is_fraction(self.unit):
            raise ValueError(f"measure '{self.name}' declares a basis on a share ('{self.unit}'): "
                             "its whole is in its unit, so a basis belongs on a count only")
        return self


# ── Result fields (§5 of the report-spec pipeline model), mirrored from trellis-analytics ──
# The library (egeria-trellis-analytics) authors this vocabulary; pyegeria keeps the same names and
# meanings without importing it. tests/micro-tests/test_declarations_match_library.py checks every
# built-in declaration loads in the library when it is installed.

#: What a field is: plain data; a value cell with companions; a pre-built representation; nested
#: rows of a registered shape.
FIELD_KINDS = ("data", "cell", "representation", "dataset")

#: The plain field types; `list<T>` and `map<string,T>` take one of them as T.
FIELD_TYPES = ("string", "int", "float", "fraction", "bool", "datetime", "guid")

#: The companions a value cell may carry.
CELL_COMPANIONS = ("state", "completeness", "uncertainty", "unit", "as_of", "basis", "provenance", "score",
                   "population")

_FIELD_NAME = r"[A-Za-z_][A-Za-z0-9_]*"
_SCALAR = "|".join(FIELD_TYPES)
_FIELD_TYPE = re.compile(rf"(?:{_SCALAR})|list<(?:{_SCALAR})>|map<\s*string\s*,\s*(?:{_SCALAR})\s*>|"
                         rf"representation/[A-Za-z0-9_.+-]+")


class FieldCompanion(BaseModel):
    """A companion a cell carries, optionally narrowed to a named state set or a list of values."""
    name: str
    valid_values: Optional[Union[str, List[str]]] = None


class FieldDeclaration(BaseModel):
    """One field of a result (trellis `Field`). `name` is the result key (an identifier; a dot is a
    path, never part of a name), `label` the column name a person reads. A `cell` is a value with
    companions; a `dataset` is nested rows of the registered shape it names (ROW_SHAPES)."""
    name: str
    label: str = ""
    kind: Literal["data", "cell", "representation", "dataset"] = "data"
    type: str = ""
    unit: str = ""
    detail_spec: str = ""
    valid_values: Optional[Union[str, List[str]]] = None
    shape: str = ""
    companions: Optional[List[Union[str, FieldCompanion]]] = None
    format: str = ""
    measure: str = ""

    @model_validator(mode="after")
    def _shape(self) -> "FieldDeclaration":
        label = f"field '{self.name}'"
        if not re.fullmatch(_FIELD_NAME, self.name or ""):
            raise ValueError(f"{label} is not an identifier: a dot is a path, never part of a name")
        if not _words(self.label) and self.kind != "representation":
            raise ValueError(f"{label} declares no label: say the column name a person reads")
        if self.kind == "dataset":
            if not _words(self.shape) or _words(self.type):
                raise ValueError(f"{label} is a dataset: it names a shape and no type")
        else:
            if _words(self.shape):
                raise ValueError(f"{label} names a shape and is a '{self.kind}' field: a shape belongs to a dataset")
            if not _FIELD_TYPE.fullmatch(self.type or ""):
                raise ValueError(f"{label} type '{self.type}' is not a field type ({', '.join(FIELD_TYPES)}, "
                                 "list<T>, map<string,T>, representation/<format>)")
            if self.type.startswith("representation/") != (self.kind == "representation"):
                raise ValueError(f"{label}: a representation field, and only one, has type representation/<format>")
        if self.companions is not None:
            if self.kind != "cell":
                raise ValueError(f"{label} declares companions and is a '{self.kind}' field: companions belong to a cell")
            names = [c if isinstance(c, str) else c.name for c in self.companions]
            unknown = [n for n in names if n not in CELL_COMPANIONS]
            if unknown or len(set(names)) != len(names):
                raise ValueError(f"{label} companions {names} must be distinct cell companions "
                                 f"({', '.join(CELL_COMPANIONS)})")
        return self


class CategoriesDeclaration(BaseModel):
    """How a distribution's or graph's categories relate (trellis `CategoriesDeclaration`): exclusive
    when one item falls in exactly one category; `sums_to` names the field holding the stated total."""
    exclusive: bool
    sums_to: str = ""

    @model_validator(mode="after")
    def _sums(self) -> "CategoriesDeclaration":
        if _words(self.sums_to) and not self.exclusive:
            raise ValueError("categories that overlap cannot sum to a total: leave sums_to out or declare exclusive")
        return self


class ListDeclaration(BaseModel):
    """A list result's items (trellis `ListDeclaration`): the fields a row shows, the order in words,
    and the field that makes an item one item."""
    item_fields: List[str]
    order: str
    key_field: str
    item_label: str = ""

    @model_validator(mode="after")
    def _filled(self) -> "ListDeclaration":
        if not [f for f in self.item_fields if _words(f)] or not _words(self.order) or not _words(self.key_field):
            raise ValueError("a list declares its item_fields, its order in words and its key_field")
        return self


class AbsenceSentences(BaseModel):
    """The sentence shown for each way a result can be absent. All four are declared."""
    not_measured: str
    not_permitted: str
    not_applicable: str
    nothing_found: str

    @model_validator(mode="before")
    @classmethod
    def _legacy_word(cls, data: Any) -> Any:
        """Declarations authored before RS-W1-1 say `measured_nothing`; read it as `nothing_found`."""
        if isinstance(data, dict) and LEGACY_NOTHING_FOUND in data:
            data = dict(data)
            legacy = data.pop(LEGACY_NOTHING_FOUND)
            data.setdefault("nothing_found", legacy)
        return data

    @model_validator(mode="after")
    def _filled(self) -> "AbsenceSentences":
        empty = [s for s in ABSENCE_STATES if not _words(getattr(self, s))]
        if empty:
            raise ValueError(f"absence sentence for {', '.join(empty)} is empty: "
                             "an absence is declared, never improvised")
        return self

    def sentence(self, state: str) -> str:
        return getattr(self, canonical_absence_state(state))


class AnalyticDeclaration(BaseModel):
    """What an analytic function declares about its results: the minimum is `result_kind`,
    `measures` (required for measure/series/distribution/graph) and `absence`.

    `out` says the result's fields (for a list or series, the fields of one row) in one of the
    library's three forms: a list of fields (every pyegeria built-in), a registered shape's name, or
    an inline shape (`{"fields": [...], "extends": ...}`, kept as data); None or [] when not declared. Read it through
    `out_fields()`, never by iterating `out`, so a library declaration reads the same way (RS-W2-1a
    read-back F2). `categories` belongs to a distribution or graph and `listing` to a list, as in
    trellis-analytics; this model accepts a declaration without them, and the built-ins all carry
    them."""
    result_kind: str
    measures: List[MeasureDeclaration] = Field(default_factory=list)
    absence: AbsenceSentences
    categories: Optional[CategoriesDeclaration] = None
    listing: Optional[ListDeclaration] = None
    out: Optional[Union[List[FieldDeclaration], str, Dict[str, Any]]] = Field(default_factory=list)

    def out_fields(self) -> List[FieldDeclaration]:
        """The result's fields, whichever form `out` takes. A shape name pyegeria does not hold in
        ROW_SHAPES (one only the library registers) and an inline shape's reused fields (`extends`,
        `include`) are not resolved here, so they read as []; the resolver (RS-W2-2 PR-B) says why."""
        if self.out is None:  # the library's word for "not declared"
            return []
        if isinstance(self.out, list):
            return list(self.out)
        if isinstance(self.out, str):
            return list(ROW_SHAPES.get(self.out, []))
        return [FieldDeclaration.model_validate(f) for f in self.out.get("fields", [])
                if isinstance(f, dict) and "include" not in f]

    @field_validator("result_kind")
    @classmethod
    def _kind(cls, value: str) -> str:
        if value not in RESULT_KINDS:
            raise ValueError(f"result_kind '{value}' is not one of {', '.join(RESULT_KINDS)}")
        return value

    @model_validator(mode="after")
    def _measured_kinds_declare_measures(self) -> "AnalyticDeclaration":
        if self.result_kind in ("measure", "series", "distribution", "graph") and not self.measures:
            raise ValueError(f"result_kind '{self.result_kind}' declares no measures")
        return self


# ── Routine declaration and bindings (RS-W2-2 PR-A; note §2b), mirrored from trellis-analytics 0.4 ──
# A registry entry is a declaration (data: what the routine is, its inputs, parameters, constants and
# results) plus one or more bindings (how it is reached). The library authors the schema in
# `trellis_analytics.routine` (owner decision D2); pyegeria keeps the same names, words and rules
# without importing it, and tests/micro-tests/test_routine_declarations_match_library.py loads every
# built-in here in the library when it is installed. `AnalyticFunctionSpec` below is the compatibility
# view: its `function` is the one python binding.

#: What a declaration declares: a stage of a micro-flow (producer, processor, routine) or a step (a
#: routine deployed to an engine host).
ROUTINE_KINDS = ("producer", "processor", "routine", "step")

#: How a routine is reached. `python`: an importable `module.attr` path; `egeria_query`: a saved Egeria
#: query by name; `sql`: a named query a reader owns; `step`: a step's registered name.
BINDING_KINDS = ("python", "egeria_query", "sql", "step")

#: What a parameter changes: what is counted (`content`), how the result is laid out (`shape`), or
#: only how fast or how much is read (`performance`, which never changes a value).
PARAM_CATEGORIES = ("content", "shape", "performance")

#: The role words a routine's `inputs` use. `egeria_client` and `reader` take a qualifier.
#: The executor supplies each declared input from the environment's `role_supply.RoleSupply` and
#: binds it to the routine's leading positional parameters in declared order (RS-W2-3). An
#: `egeria_client:<Class>` names the class whose methods that argument calls; `EgeriaTech` only for
#: an argument that calls across several classes. Each input is declared once.
INPUT_ROLES = ("egeria_client", "reader", "viewer", "subject")

_INPUT_ROLE = re.compile(r"^(?:egeria_client:[A-Za-z_][A-Za-z0-9_]*|reader:[a-z_][a-z0-9_]*|viewer|subject)$")
_PYTHON_TARGET = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+$")


class _StrictModel(BaseModel):
    # An unknown key is refused, so a misspelt field is named rather than silently dropped.
    model_config = ConfigDict(extra="forbid")


class Binding(_StrictModel):
    """How a routine is reached: one of BINDING_KINDS and its target. A python target is a dotted
    import path; the module allow-list (`format_set_executor.python_binding_allowed`) applies to it,
    and only to it: a report spec names routines, never targets (ISSUE-173)."""
    kind: Literal["python", "egeria_query", "sql", "step"]
    target: str

    @model_validator(mode="after")
    def _target(self) -> "Binding":
        if not _words(self.target):
            raise ValueError(f"a {self.kind} binding names no target")
        if self.kind == "python" and not _PYTHON_TARGET.fullmatch(self.target):
            raise ValueError(f"python binding target '{self.target}' is not a dotted import path (module.attr)")
        return self


class ParamDeclaration(_StrictModel):
    """One parameter a caller may set. Either it has a default or it is required, never both."""
    name: str
    type: str = "str"
    default: Any = None
    required: bool = False
    category: Literal["content", "shape", "performance"] = "content"
    description: str = ""

    @model_validator(mode="after")
    def _shape(self) -> "ParamDeclaration":
        if not re.fullmatch(_FIELD_NAME, self.name or ""):
            raise ValueError(f"parameter name '{self.name}' is not an identifier")
        if self.required and self.default is not None:
            raise ValueError(f"parameter '{self.name}' is required and has a default: a required parameter has none")
        return self


class TileSafety(_StrictModel):
    """May the routine run on a tile's request path? `safe` with no `cap` is a yes at any size; a
    `cap` (param -> value) is a yes only within it. The reason is the evidence and is always said."""
    safe: bool
    cap: Dict[str, Any] = Field(default_factory=dict)
    reason: str

    @model_validator(mode="after")
    def _reason(self) -> "TileSafety":
        if not _words(self.reason):
            raise ValueError("tile_safe declares no reason: say the evidence (a timing, a cost class)")
        if self.cap and not self.safe:
            raise ValueError("tile_safe declares a cap and safe false: a cap says within what it IS safe")
        return self


class Admission(_StrictModel):
    """Where the routine may be offered: the resource types it is about ([] = any), and whether only
    in tests."""
    resource_types: List[str] = Field(default_factory=list)
    test_only: bool = False


#: A processor's input shape (`in`): a list of fields, a registered shape's name, or an inline shape.
ShapeRef = Union[List[FieldDeclaration], str, Dict[str, Any]]


class RoutineDeclaration(_StrictModel):
    """What a routine says about how it is called and what it returns (note §2b).

    Only `name` is required. `declaration` is the results (`AnalyticDeclaration`: result kind,
    measures, absence sentences, `out`); `out` lives there, not here, so a result's fields are
    declared once. `in` (attribute `in_`) is the shape a processor reads. `constants` are values
    fixed for every call; a constant is never also a parameter. At most one python binding.

    A shape name in `in` is not checked against ROW_SHAPES here (the library may register shapes
    pyegeria does not hold); the resolver checks it (RS-W2-2 PR-B, check 3)."""
    name: str
    kind: Literal["producer", "processor", "routine", "step"] = "routine"
    description: str = ""
    version: str = ""
    source: str = ""
    family: str = ""
    tags: List[str] = Field(default_factory=list)
    generic: bool = False
    binding_note: str = ""
    inputs: List[str] = Field(default_factory=list)
    params: List[ParamDeclaration] = Field(default_factory=list)
    constants: Dict[str, Any] = Field(default_factory=dict)
    in_: Optional[ShapeRef] = Field(default=None, alias="in")
    declaration: Optional[AnalyticDeclaration] = None
    pushdown: List[str] = Field(default_factory=list)
    tile_safe: Optional[TileSafety] = None
    admission: Admission = Field(default_factory=Admission)
    bindings: List[Binding] = Field(default_factory=list)
    annotation_type: str = ""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @model_validator(mode="after")
    def _whole(self) -> "RoutineDeclaration":
        if not re.fullmatch(_FIELD_NAME, self.name or ""):
            raise ValueError(f"routine name '{self.name}' is not an identifier")
        label = f"routine '{self.name}'"
        bad = [i for i in self.inputs if not _INPUT_ROLE.fullmatch(i or "")]
        if bad:
            raise ValueError(f"{label} input {', '.join(repr(b) for b in bad)} is not a role word "
                             "(egeria_client:<Class>, reader:<name>, viewer, subject)")
        if len(set(self.inputs)) != len(self.inputs):
            raise ValueError(f"{label} declares an input more than once")
        names = [p.name for p in self.params]
        twice = sorted({n for n in names if names.count(n) > 1})
        if twice:
            raise ValueError(f"{label} declares parameter {', '.join(twice)} more than once")
        clash = sorted(set(names) & set(self.constants))
        if clash:
            raise ValueError(f"{label} declares {', '.join(clash)} as a parameter and a constant: a constant is "
                             "fixed for every call, so it is not a parameter")
        if sum(1 for b in self.bindings if b.kind == "python") > 1:
            raise ValueError(f"{label} declares more than one python binding: one routine, one function")
        if self.in_ is not None and self.kind != "processor":
            raise ValueError(f"{label} declares in and is a '{self.kind}': only a processor reads a previous "
                             "stage's shape; a routine or producer names its inputs")
        if self.generic and _words(self.binding_note):
            raise ValueError(f"{label} is generic and declares a binding_note: the note names what is fixed, "
                             "and a generic routine fixes nothing")
        return self

    def python_target(self) -> str:
        """The python binding's target, or "" when it has none."""
        return next((b.target for b in self.bindings if b.kind == "python"), "")

    def out_fields(self) -> List[FieldDeclaration]:
        """The result's fields (`declaration.out`); [] when not declared."""
        return self.declaration.out_fields() if self.declaration is not None else []


def _as_analytic_declaration(decl: Any) -> Optional[AnalyticDeclaration]:
    """A declaration as pyegeria's model. A subclass's richer declaration (trellis-analytics'
    `Declaration`) is read through its dump; the blocks pyegeria does not model are left out."""
    if decl is None or isinstance(decl, AnalyticDeclaration):
        return decl
    return AnalyticDeclaration.model_validate(decl.model_dump() if isinstance(decl, BaseModel) else decl)


class AnalyticFunctionSpec(BaseModel):
    """One entry in the analytic function registry.

    `generic` is the load-bearing field for reuse: it tells a report-spec
    author whether *what* the function counts/aggregates is itself a
    parameter (generic=True -- e.g. `count_elements(type_name=...)`, freely
    retargetable at any element type via a report spec's `analytic_spec_params`),
    or hardcoded inside the function body (generic=False -- e.g.
    `governed_coverage` always counts `GOVERNANCE_CLASSIFICATIONS`; a report
    spec can still point at it, but always gets that one fixed metric --
    retargeting it means editing the Python function, not authoring a new
    report spec). `binding_note` names exactly what's fixed, for the generic=False
    case (blank when generic=True, since there's nothing fixed to name).

    `action`, if set, is a structured (fetch, analytic) breakdown of what
    `function` does internally (see `AnalyticActionSpec`) -- additive only:
    `function` always still resolves to a real, directly-callable entry
    point that returns exactly what `returns` describes (for an
    action-backed entry, a thin composite wrapper -- see `sum_type_counts`
    -- built via `format_set_executor.run_analytic_action`), so every
    existing consumer that only reads `.function` -- including every other
    entry in this registry -- keeps working completely unchanged."""
    name: str
    # The one python binding's target (a dotted import path, e.g.
    # "pyegeria.view.overview_metrics.growth_series"). "" only for an entry whose bindings has no
    # python binding; this pyegeria runs python bindings only, and refuses such an entry by name.
    function: str = ""
    description: str = ""
    returns: str = ""  # human-readable result shape, e.g. "scalar (int)", "list[dict] (time series)"
    generic: bool = False
    binding_note: str = ""
    params: List[AnalyticParam] = Field(default_factory=list)
    action: Optional[AnalyticActionSpec] = None

    # Manifest fields (ISSUE-149), all optional so every existing entry is unchanged.
    # trellis-analytics' RoutineManifest/StepManifest subclass this class and used to
    # carry these themselves.
    # routine: runs in the caller; step: a survey-style step; producer/processor: a stage (RS-W2-2)
    kind: Literal["producer", "processor", "routine", "step"] = "routine"
    source: str = ""  # where the data comes from; known values in KNOWN_ANALYTIC_SOURCES
    version: str = ""  # the producer's version, stamped on every result
    envelope: bool = False  # the result carries a state envelope (measured / nothing_found / ...)
    annotation_type: str = ""  # a step's result type, e.g. ResourceMeasureAnnotation; empty for a routine
    resource_types: List[str] = Field(default_factory=list)  # e.g. ["database"]
    family: str = ""  # same word and meaning as FormatSet.family; in Egeria a family is a Collection
    tags: List[str] = Field(default_factory=list)
    # What the results mean (ISSUE-170): result kind, measures with unit/as-of/basis, absence
    # sentences. Optional; trellis-analytics' StepManifest narrows it to its fuller Declaration.
    declaration: Optional[AnalyticDeclaration] = None

    # The routine declaration's own fields (RS-W2-2 PR-A), so this view carries a RoutineDeclaration
    # whole: `routine()` and `from_routine()` round-trip. All optional; no existing entry sets them.
    bindings: List[Binding] = Field(default_factory=list)  # every binding; the python one is `function`
    inputs: List[str] = Field(default_factory=list)  # role words (INPUT_ROLES)
    constants: Dict[str, Any] = Field(default_factory=dict)
    in_: Optional[ShapeRef] = Field(default=None, alias="in")
    pushdown: List[str] = Field(default_factory=list)
    tile_safe: Optional[TileSafety] = None
    test_only: bool = False  # with resource_types, the routine's Admission

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def _function_is_the_python_binding(cls, data: Any) -> Any:
        """`function` and the python binding are one value: either fills the other; two that differ,
        two python bindings, or no binding at all are refused."""
        if not isinstance(data, dict):
            return data
        data = dict(data)
        label = f"analytic function '{data.get('name', '')}'"
        function = data.get("function") or ""
        bindings = list(data.get("bindings") or [])

        def _get(b: Any, key: str) -> Any:
            return b.get(key) if isinstance(b, dict) else getattr(b, key, None)

        python = [_get(b, "target") for b in bindings if _get(b, "kind") == "python"]
        if len(python) > 1:
            raise ValueError(f"{label} declares more than one python binding: one routine, one function")
        if function and not python:
            bindings.insert(0, {"kind": "python", "target": function})
        elif python and not function:
            data["function"] = python[0]
        elif python and python[0] != function:
            raise ValueError(f"{label} names function '{function}' and python binding '{python[0]}': they are "
                             "one value, so name it once")
        if not bindings:
            raise ValueError(f"{label} declares no binding: name its function (a python binding) or a binding")
        data["bindings"] = bindings
        return data

    @field_validator("source")
    @classmethod
    def _suggest_known_source(cls, value: str) -> str:
        """Value lists are suggestive: an unknown source warns, never rejects."""
        if value and value not in KNOWN_ANALYTIC_SOURCES:
            logger.warning(f"Analytic source '{value}' is not one of the known values "
                           f"{sorted(KNOWN_ANALYTIC_SOURCES)}; keeping it.")
        return value

    def python_target(self) -> str:
        """The python binding's target ("" when the entry has none)."""
        return next((b.target for b in self.bindings if b.kind == "python"), "")

    def routine(self) -> RoutineDeclaration:
        """This entry as a RoutineDeclaration (the declaration + bindings it is a view of). Raises
        ValueError, in words, when the entry breaks a declaration rule; `get_routine_registry`
        records that instead of raising."""
        return RoutineDeclaration(
            name=self.name, kind=self.kind, description=self.description, version=self.version,
            source=self.source, family=self.family, tags=list(self.tags), generic=self.generic,
            binding_note=self.binding_note, inputs=list(self.inputs),
            params=[ParamDeclaration(name=p.name, type=p.type, default=p.default, required=p.required,
                                     category=p.category, description=p.description) for p in self.params],
            constants=dict(self.constants), in_=self.in_,
            declaration=_as_analytic_declaration(self.declaration), pushdown=list(self.pushdown),
            tile_safe=self.tile_safe,
            admission=Admission(resource_types=list(self.resource_types), test_only=self.test_only),
            bindings=list(self.bindings),
            annotation_type=self.annotation_type if self.kind == "step" else "",
        )

    @classmethod
    def from_routine(cls, routine: RoutineDeclaration, *, returns: str = "",
                     action: Optional[AnalyticActionSpec] = None, envelope: bool = False,
                     **extra: Any) -> "AnalyticFunctionSpec":
        """The compatibility view of a RoutineDeclaration. `returns`, `action` and `envelope` are
        the view's own fields, which a declaration does not carry (its results are in
        `declaration`). `extra` is passed on, for a subclass's own fields."""
        r = routine
        return cls(
            name=r.name, function=r.python_target(), description=r.description, returns=returns,
            generic=r.generic, binding_note=r.binding_note,
            params=[AnalyticParam(name=p.name, type=p.type, required=p.required, default=p.default,
                                  description=p.description, category=p.category) for p in r.params],
            action=action, kind=r.kind, source=r.source, version=r.version, envelope=envelope,
            annotation_type=r.annotation_type, resource_types=list(r.admission.resource_types),
            family=r.family, tags=list(r.tags), declaration=r.declaration, bindings=list(r.bindings),
            inputs=list(r.inputs), constants=dict(r.constants), in_=r.in_, pushdown=list(r.pushdown),
            tile_safe=r.tile_safe, test_only=r.admission.test_only, **extra,
        )


class AnalyticFunctionDict(Dict[str, AnalyticFunctionSpec]):
    """Name -> AnalyticFunctionSpec, mirroring FormatSetDict/DashboardSheetDict."""
    pass


def _as_of(description: str = "ISO-8601 asOfTime for a point-in-time value (None = now).") -> AnalyticParam:
    return AnalyticParam(name="as_of", type="str", description=description)


def _strict() -> AnalyticParam:
    return AnalyticParam(name="strict", type="bool", default=False,
                         description="Accepted for compatibility; changes nothing. Since 6.2.28 a count "
                                     "that could not be measured (query failed, or the fallback hit the "
                                     "page-size cap) is None in every population, never 0. ISSUE-123.")


def _population() -> AnalyticParam:
    return AnalyticParam(name="population", type="str", default="repository",
                         description="repository (the default: the whole repository, including elements "
                                     "the caller may not be able to see -- fast, native count only) or "
                                     "viewer (only what the caller may see; can take minutes for a large type).")


#: Said by every routine whose totals count the whole repository (owner decision 2026-11-08, an interim
#: choice until zone-aware push-down exists).
REPOSITORY_WORDS = (" Its totals count the whole repository (population=repository), including elements you may not be able to "
                    "see (a deliberate interim choice until zone-aware push-down exists).")


# ── Declaration literals (RS-W2-1a). Short builders so each entry below reads as its declaration. ──
# `as_of="run.as_of"` names the call's own as_of argument (None = when it ran): these routines'
# results carry no time of their own.

RUN_AS_OF = "run.as_of"


def _measure(name: str, unit: str, value_field: str, as_of: str = RUN_AS_OF, **kw: Any) -> MeasureDeclaration:
    return MeasureDeclaration(name=name, unit=unit, as_of=as_of, value_field=value_field, **kw)


def _basis(denominator_field: str, denominator_label: str) -> BasisDeclaration:
    return BasisDeclaration(denominator_field=denominator_field, denominator_label=denominator_label)


def _field(name: str, label: str, type: str = "", kind: str = "data", **kw: Any) -> FieldDeclaration:
    return FieldDeclaration(name=name, label=label, type=type, kind=kind, **kw)


def _absence(not_measured: str, not_permitted: str, not_applicable: str, nothing_found: str) -> AbsenceSentences:
    return AbsenceSentences(not_measured=not_measured, not_permitted=not_permitted,
                            not_applicable=not_applicable, nothing_found=nothing_found)


def _always_applies(what: str) -> str:
    """The not_applicable sentence for a routine with no input that could make it not apply."""
    return (f"{what} applies to every catalog, so this routine never reports it as not applicable; "
            "seeing this means the result was labelled wrongly.")


#: Row shapes the built-in declarations name from a `dataset` field (trellis registered shapes).
ROW_SHAPES: Dict[str, List[FieldDeclaration]] = {
    "TypeCount": [
        _field("label", "Label", "string"),
        _field("type", "Type", "string"),
        _field("count", "Count", "int", unit="elements"),
    ],
    "ZoneCount": [
        _field("zone", "Zone", "string"),
        _field("count", "Elements", "int", unit="elements"),
    ],
    "ExpiringCertification": [
        _field("name", "Certification", "string"),
        _field("days", "Days left", "int", unit="days"),
    ],
    "CompositionRow": [
        _field("type_name", "Type", "string"),
        _field("parent", "Parent", "string"),
        _field("level", "Level", "int"),
        _field("exact_type", "Exactly the parent type", "bool"),
        _field("subtypes_error", "Subtypes not read", "string"),
        _field("viewer", "Viewer count", "int", kind="cell", unit="elements",
               companions=["state", "completeness", "as_of", "population"], measure="viewer_count"),
        _field("repository", "Repository count", "int", kind="cell", unit="elements",
               companions=["state", "completeness", "as_of", "population"], measure="repository_count"),
        _field("not_visible", "Not visible to you", "int", kind="cell", unit="elements",
               companions=["state"], measure="not_visible"),
    ],
}


# ── Built-ins -- every analytic function already proven live via the Overview
# dashboard's /api/overview/* endpoints (overview_handler.py), just not yet
# reachable from a Dr.Egeria report spec. ──────────────────────────────────
_BUILTINS: Dict[str, AnalyticFunctionSpec] = {
    "count_elements": AnalyticFunctionSpec(
        name="count_elements",
        function="pyegeria.view.overview_metrics.count_elements",
        inputs=["egeria_client:MetadataExpert"],
        description="Count active elements of a given type, optionally filtered by classification. "
                    "Cost: one native count, sub-second in the repository population (0.2-0.8 s "
                    "measured); a viewer-population count reads every element and can take minutes "
                    "for a large type (Process: 120 s). Only in the viewer population does a server "
                    "with no native count fall back to a capped find; a repository count has no "
                    "fallback and is not measured instead." + REPOSITORY_WORDS,
        returns="scalar (int)",
        generic=True,
        params=[
            AnalyticParam(name="type_name", type="str",
                          description="Open metadata type to count, e.g. GlossaryTerm, DigitalProduct. Omit for any type."),
            _as_of(),
            _strict(),
            AnalyticParam(name="classifications", type="list[str]",
                          description="Match ANY of these classification names."),
            _population(),
        ],
        declaration=AnalyticDeclaration(
            result_kind="measure",
            measures=[_measure("elements", "elements", "value", population="repository")],
            absence=_absence(
                not_measured="The elements were not counted: the count query failed or timed out, or "
                             "the server could not answer it in the population asked for. A fallback "
                             "that stopped at its page cap is a lower bound, never a total.",
                not_permitted="You are not permitted to count these elements.",
                not_applicable="This count does not apply: the type named is not an element type "
                               "the server knows.",
                nothing_found="Counted: there are no active elements of this type with these "
                              "classifications.",
            ),
            out=[_field("value", "Elements", "int", unit="elements")],
        ),
    ),
    "counts_by_type": AnalyticFunctionSpec(
        name="counts_by_type",
        function="pyegeria.view.overview_metrics.counts_by_type",
        inputs=["egeria_client:MetadataExpert"],
        description="Per-type element counts for a set of (label, type_name) pairs -- a breakdown/"
                    "composition metric, e.g. the assets-by-type chart. "
                    "Cost: one native count per type, sub-second each in the repository population; a viewer-population count can take minutes for a large type." + REPOSITORY_WORDS,
        returns="list[dict] (breakdown: {label, type, count})",
        generic=True,
        params=[
            AnalyticParam(name="type_map", type="list[tuple[str, str]]", required=True,
                          description="(label, type_name) pairs to count, e.g. [('Data Stores', 'DataStore'), ...]."),
            _as_of(),
            _strict(),
            _population(),
        ],
        declaration=AnalyticDeclaration(
            result_kind="distribution",
            measures=[_measure("count", "elements", "count", population="repository")],
            # The caller picks the types; a supertype and its subtype may both be listed.
            categories=CategoriesDeclaration(exclusive=False),
            absence=_absence(
                not_measured="The types were not counted: the count queries failed or timed out, or "
                             "the server could not answer them in the population asked for. A fallback "
                             "that stopped at its page cap is a lower bound, never a total.",
                not_permitted="You are not permitted to count elements of these types.",
                not_applicable="A breakdown by type does not apply: no types were given to count.",
                nothing_found="Counted: there are no active elements of any of these types.",
            ),
            out=ROW_SHAPES["TypeCount"],
        ),
    ),
    "governed_coverage": AnalyticFunctionSpec(
        name="governed_coverage",
        function="pyegeria.view.overview_metrics.governed_coverage",
        inputs=["egeria_client:MetadataExpert"],
        description="Share of assets carrying at least one governance classification, plus a "
                    "by-classification / top-zones breakdown. "
                    "Cost: one find, paged until Egeria returns an empty page (an incomplete scan is not measured), seconds.",
        returns="dict (governedCount, governedCapped, byClassification, topZones)",
        generic=False,
        binding_note="Fixed to GOVERNANCE_CLASSIFICATIONS: ZoneMembership, Confidentiality, "
                     "Criticality, Impact, Retention -- not a parameter.",
        params=[_as_of()],
        declaration=AnalyticDeclaration(
            result_kind="measure",
            # The find is not restricted to Asset: these count elements of any type.
            measures=[
                _measure("governed_elements", "elements of any type carrying at least one of the five "
                         "governance classifications", "governedCount",
                         completeness_field="governedCapped", population="viewer"),
                _measure("fully_governed", "elements carrying Confidentiality, Criticality, Impact or "
                         "Retention", "fullyGoverned", completeness_field="governedCapped", population="viewer",
                         basis=_basis("governedCount", "governed elements")),
                _measure("zone_only", "elements carrying ZoneMembership and no other governance "
                         "classification", "partialZoneOnly", completeness_field="governedCapped",
                         population="viewer", basis=_basis("governedCount", "governed elements")),
            ],
            absence=_absence(
                not_measured="Governance coverage was not measured: the find of classified elements failed.",
                not_permitted="You are not permitted to read the classified elements, so governance "
                              "coverage was not measured.",
                not_applicable=_always_applies("Governance coverage"),
                nothing_found="Counted: no active element carries any of the five governance "
                              "classifications (ZoneMembership, Confidentiality, Criticality, Impact, "
                              "Retention).",
            ),
            out=[
                _field("governedCount", "Governed elements", "int", unit="elements"),
                _field("governedCapped", "At least (false when measured: every page is read)", "bool"),
                _field("fullyGoverned", "Fully governed", "int", unit="elements"),
                _field("partialZoneOnly", "Zone only", "int", unit="elements"),
                _field("byClassification", "By classification", "map<string,int>", unit="elements"),
                _field("topZones", "Top zones", kind="dataset", shape="ZoneCount"),
            ],
        ),
    ),
    "ownership_coverage": AnalyticFunctionSpec(
        name="ownership_coverage",
        function="pyegeria.view.overview_metrics.ownership_coverage",
        inputs=["egeria_client:MetadataExpert"],
        description="Share of assets carrying an Ownership classification (a named owner "
                    "responsible for management/governance decisions), plus a by-owner-type "
                    "breakdown. Distinct from governed_coverage -- data mesh literature names "
                    "'clean, owned, product-based data' as its own foundation for trustworthy "
                    "AI consumption, not a synonym for governance-classification coverage. "
                    "Cost: one find, paged until Egeria returns an empty page (an incomplete scan is not measured), seconds.",
        returns="dict (ownershipCount, ownershipCapped, byOwnerType)",
        generic=False,
        binding_note="Fixed to the Ownership classification -- not a parameter.",
        params=[_as_of()],
        declaration=AnalyticDeclaration(
            result_kind="measure",
            measures=[_measure("owned_elements", "elements of any type carrying an Ownership classification",
                               "ownershipCount", completeness_field="ownershipCapped", population="viewer")],
            absence=_absence(
                not_measured="Ownership coverage was not measured: the find of owned elements failed.",
                not_permitted="You are not permitted to read the owned elements, so ownership coverage "
                              "was not measured.",
                not_applicable=_always_applies("Ownership coverage"),
                nothing_found="Counted: no active element carries an Ownership classification.",
            ),
            out=[
                _field("ownershipCount", "Owned elements", "int", unit="elements"),
                _field("ownershipCapped", "At least (false when measured: every page is read)", "bool"),
                _field("byOwnerType", "By owner type", "map<string,int>", unit="elements"),
            ],
        ),
    ),
    "business_value_signals": AnalyticFunctionSpec(
        name="business_value_signals",
        function="pyegeria.view.overview_metrics.business_value_signals",
        inputs=["egeria_client:MetadataExpert"],
        description="Real signals behind the four Overview dashboard Business Value tiles "
                    "(Risk & Compliance, Productivity, Trust & Adoption, Cost Avoidance): "
                    "Confidentiality-classified asset count, described-asset count, "
                    "ConsolidatedDuplicate-flagged element count -- all proxies with a "
                    "documented causal-claim caveat, not direct measures (NEXT-9). "
                    "Cost: four native counts, sub-second each in the repository population." + REPOSITORY_WORDS,
        returns="dict (assetTotal, assetCapped, confidentialCount, describedCount, duplicateCount)",
        generic=False,
        binding_note="Fixed to the Asset type hierarchy and Confidentiality/ConsolidatedDuplicate "
                     "classifications -- not a parameter.",
        params=[_as_of(), _population()],
        declaration=AnalyticDeclaration(
            result_kind="measure",
            measures=[
                _measure("assets", "Assets", "assetTotal", completeness_field="assetCapped",
                         population="repository"),
                _measure("confidential_assets", "Assets carrying a Confidentiality classification",
                         "confidentialCount", completeness_field="assetCapped", population="repository",
                         basis=_basis("assetTotal", "Assets")),
                _measure("described_assets", "Assets with a description (set, not empty)", "describedCount",
                         completeness_field="assetCapped", population="repository",
                         basis=_basis("assetTotal", "Assets")),
                _measure("duplicate_elements", "elements of any type carrying ConsolidatedDuplicate",
                         "duplicateCount", population="repository"),
            ],
            absence=_absence(
                not_measured="The business-value signals were not measured: their counts failed, or "
                             "the server could not answer them in the population asked for.",
                not_permitted="You are not permitted to read the Assets, so the business-value "
                              "signals were not measured.",
                not_applicable=_always_applies("The business-value signals"),
                nothing_found="Counted: there are no active Assets and no elements marked as duplicates.",
            ),
            out=[
                _field("assetTotal", "Assets", "int", unit="Assets"),
                _field("assetCapped", "At least (false when counted: a native count is complete; empty when not measured)", "bool"),
                _field("confidentialCount", "Confidential Assets", "int", unit="Assets"),
                _field("describedCount", "Described Assets", "int", unit="Assets"),
                _field("duplicateCount", "Duplicates", "int", unit="elements"),
            ],
        ),
    ),
    "certifications_summary": AnalyticFunctionSpec(
        name="certifications_summary",
        function="pyegeria.view.overview_metrics.certifications_summary",
        inputs=["egeria_client:ClassificationExplorer"],
        description="Active/expiring Certification relationships, licenses, and open Exception counts. "
                    "Cost: one relationship scan, paged until Egeria returns an empty page, plus two counts, seconds.",
        returns="dict (active, expiring90, soon, licenses, exceptions)",
        generic=False,
        binding_note="Fixed to the Certification and Exception relationship types -- not a parameter.",
        params=[_as_of()],
        declaration=AnalyticDeclaration(
            result_kind="measure",
            # active/expiring90 come from every Certification page; an incomplete scan is None, noted.
            measures=[
                _measure("certifications", "Certification relationships", "active", population="viewer"),
                _measure("expiring_certifications", "Certification relationships ending within 90 days",
                         "expiring90", population="viewer", basis=_basis("active", "certifications")),
                _measure("licenses", "License relationships", "licenses", population="viewer"),
                _measure("exceptions", "Exception relationships", "exceptions", population="viewer"),
            ],
            absence=_absence(
                not_measured="Certifications were not measured: the relationship queries failed.",
                not_permitted="You are not permitted to read certifications, licenses or exceptions.",
                not_applicable=_always_applies("A certification summary"),
                nothing_found="Counted: there are no active certifications, licenses or exceptions.",
            ),
            out=[
                _field("active", "Certifications", "int", unit="relationships"),
                _field("expiring90", "Ending within 90 days", "int", unit="relationships"),
                _field("soon", "Ending soonest", kind="dataset", shape="ExpiringCertification"),
                _field("licenses", "Licenses", "int", unit="relationships"),
                _field("exceptions", "Exceptions", "int", unit="relationships"),
            ],
        ),
    ),
    "people_counts": AnalyticFunctionSpec(
        name="people_counts",
        function="pyegeria.view.overview_metrics.people_counts",
        inputs=["egeria_client:MetadataExpert"],
        description="Counts of Person / Team / Organization / ITProfile / Community actor profiles. "
                    "Cost: five native counts, sub-second each in the repository population." + REPOSITORY_WORDS,
        returns="dict (persons, teams, organizations, itProfiles, communities)",
        generic=False,
        binding_note="Fixed to Person/Team/Organization/ITProfile/Community -- not a parameter.",
        params=[_as_of(), _strict(), _population()],
        declaration=AnalyticDeclaration(
            result_kind="measure",
            measures=[
                _measure("persons", "Person profiles", "persons", population="repository"),
                _measure("teams", "Team profiles", "teams", population="repository"),
                _measure("organizations", "Organization profiles", "organizations", population="repository"),
                _measure("it_profiles", "ITProfile profiles", "itProfiles", population="repository"),
                _measure("communities", "Community profiles", "communities", population="repository"),
            ],
            absence=_absence(
                not_measured="The actor profiles were not counted: the count queries failed, or the "
                             "server could not answer them in the population asked for.",
                not_permitted="You are not permitted to count actor profiles.",
                not_applicable=_always_applies("Counting actor profiles"),
                nothing_found="Counted: there are no active Person, Team, Organization, ITProfile or "
                              "Community profiles.",
            ),
            out=[
                _field("persons", "People", "int", unit="profiles"),
                _field("teams", "Teams", "int", unit="profiles"),
                _field("organizations", "Organizations", "int", unit="profiles"),
                _field("itProfiles", "IT profiles", "int", unit="profiles"),
                _field("communities", "Communities", "int", unit="profiles"),
            ],
        ),
    ),
    "feedback_summary": AnalyticFunctionSpec(
        name="feedback_summary",
        function="pyegeria.view.overview_metrics.feedback_summary",
        # EgeriaTech, not ClassificationExplorer: a repository count needs the native relationship count
        # (MetadataExpert's), which a ClassificationExplorer lacks; EgeriaTech has both it and get_relationships.
        inputs=["egeria_client:EgeriaTech"],
        description="Crowd-sourced feedback counts (ratings/comments/likes/tags/noteLogs) by type, "
                    "via Collaboration OMAS relationships. "
                    "Takes an EgeriaTech: the repository count is MetadataExpert's native relationship count, "
                    "and the viewer path is ClassificationExplorer's get_relationships. "
                    "Cost: five native counts, sub-second each in the repository population; population=viewer "
                    "reads five relationship scans instead, paged until Egeria returns an empty page." + REPOSITORY_WORDS,
        returns="dict (byType, total)",
        generic=False,
        binding_note="Fixed to Collaboration OMAS's feedback relationship types -- not a parameter.",
        params=[_as_of(), _population()],
        declaration=AnalyticDeclaration(
            result_kind="measure",
            measures=[
                _measure("feedback", "feedback relationships", "total", population="repository"),
                _measure("ratings", "AttachedRating relationships", "byType.ratings", population="repository"),
                _measure("comments", "AttachedComment relationships", "byType.comments", population="repository"),
                _measure("likes", "AttachedLike relationships", "byType.likes", population="repository"),
                _measure("tags", "AttachedTag relationships", "byType.tags", population="repository"),
                _measure("note_logs", "AttachedNoteLog relationships", "byType.noteLogs", population="repository"),
            ],
            absence=_absence(
                not_measured="Feedback was not counted: a relationship query failed, or a repository "
                             "count was asked for and no native count could answer it (the client "
                             "has none, or it failed or timed out).",
                not_permitted="You are not permitted to read feedback relationships.",
                not_applicable=_always_applies("A feedback summary"),
                nothing_found="Counted: nothing in the catalog has been rated, commented on, liked, "
                              "tagged or given a note log.",
            ),
            out=[
                _field("total", "Feedback", "int", unit="relationships"),
                _field("byType", "By type", "map<string,int>", unit="relationships"),
            ],
        ),
    ),
    "usage_context_counts": AnalyticFunctionSpec(
        name="usage_context_counts",
        function="pyegeria.view.overview_metrics.usage_context_counts",
        inputs=["egeria_client:MetadataExpert"],
        description="InformationSupplyChain and SolutionBlueprint counts -- the two structures that "
                    "put assets in a business usage context (supply chain membership, blueprint "
                    "realization). "
                    "Cost: two native counts, sub-second each in the repository population." + REPOSITORY_WORDS,
        returns="dict (informationSupplyChains, blueprints)",
        generic=False,
        binding_note="Fixed to InformationSupplyChain and SolutionBlueprint -- not a parameter.",
        params=[_as_of(), _strict(), _population()],
        declaration=AnalyticDeclaration(
            result_kind="measure",
            measures=[
                _measure("supply_chains", "InformationSupplyChain elements", "informationSupplyChains", population="repository"),
                _measure("blueprints", "SolutionBlueprint elements", "blueprints", population="repository"),
            ],
            absence=_absence(
                not_measured="Supply chains and blueprints were not counted: the count queries failed, "
                             "or the server could not answer them in the population asked for.",
                not_permitted="You are not permitted to count supply chains or blueprints.",
                not_applicable=_always_applies("Counting supply chains and blueprints"),
                nothing_found="Counted: there are no active information supply chains or solution "
                              "blueprints.",
            ),
            out=[
                _field("informationSupplyChains", "Information supply chains", "int", unit="elements"),
                _field("blueprints", "Solution blueprints", "int", unit="elements"),
            ],
        ),
    ),
    "semantic_grounding": AnalyticFunctionSpec(
        name="semantic_grounding",
        function="pyegeria.view.overview_metrics.semantic_grounding",
        inputs=["egeria_client:MetadataExpert", "egeria_client:ClassificationExplorer"],
        description="SemanticAssignment relationship count and coverage percent -- the meaning layer "
                    "that grounds AI. Takes two leading clients (mgr, ce) -- the executor supplies the "
                    "same EgeriaTech instance for both. "
                    "Both counts are native, in the repository population, so the percentage never divides "
                    "one population by the other. "
                    "Cost: two native counts, sub-second each." + REPOSITORY_WORDS,
        returns="dict (groundingLinks, groundingPct)",
        generic=False,
        binding_note="Fixed to the SemanticAssignment relationship type -- not a parameter.",
        params=[_as_of()],
        declaration=AnalyticDeclaration(
            result_kind="measure",
            measures=[
                _measure("grounding_links", "SemanticAssignment relationships", "groundingLinks",
                         population="repository"),
                # links / Assets, not the share of Assets with a link: one Asset may carry several.
                _measure("grounding_percent", "percent: SemanticAssignment links per hundred Assets, "
                         "at most 100", "groundingPct", population="repository"),
            ],
            absence=_absence(
                not_measured="Semantic grounding was not measured: the SemanticAssignment count or the "
                             "Asset count to divide by failed or timed out, or the server could not "
                             "answer it in the repository population.",
                not_permitted="You are not permitted to read the semantic assignments.",
                not_applicable=_always_applies("Semantic grounding"),
                nothing_found="Counted: no glossary term is assigned to anything.",
            ),
            out=[
                _field("groundingLinks", "Grounding links", "int", unit="relationships"),
                _field("groundingPct", "Links per hundred Assets", "int", unit="percent"),
            ],
        ),
    ),
    "context_readiness_funnel": AnalyticFunctionSpec(
        name="context_readiness_funnel",
        function="pyegeria.view.overview_metrics.context_readiness_funnel",
        inputs=["egeria_client:MetadataExpert", "egeria_client:ClassificationExplorer"],
        description="Cataloged -> Documented -> Classified -> Lineage-traced -> AI-Ready funnel counts. "
                    "Takes two leading clients (mgr, ce) -- the executor supplies the same EgeriaTech "
                    "instance for both, matching semantic_grounding's convention. This function's own "
                    "aiReady stays None always by design -- it's four independent counts, and aiReady "
                    "needs a true cross-criteria intersection instead. Pair with ai_ready_assets "
                    "(below) for that -- overview_handler.py calls both and merges the result. "
                    "Every stage is a native count in the repository population. "
                    "Cost: four native counts, sub-second each." + REPOSITORY_WORDS,
        returns="dict (cataloged, documented, classified, lineage, aiReady)",
        generic=False,
        binding_note="Fixed 5-stage readiness definition baked into the function body -- not a parameter.",
        params=[_as_of()],
        declaration=AnalyticDeclaration(
            result_kind="measure",
            # Four independent native counts in one population, not nested stages of one set.
            measures=[
                _measure("cataloged", "Assets", "cataloged", population="repository"),
                _measure("documented", "Assets with a description (set, not empty)", "documented",
                         population="repository"),
                _measure("classified", "elements of any type carrying a governance classification",
                         "classified", population="repository"),
                _measure("lineage", "DataFlow relationships", "lineage", population="repository"),
            ],
            absence=_absence(
                not_measured="The readiness funnel was not measured: its counts failed, or the server "
                             "could not answer them in the repository population.",
                not_permitted="You are not permitted to read the Assets, so the readiness funnel was "
                              "not measured.",
                not_applicable=_always_applies("The readiness funnel"),
                nothing_found="Counted: there are no active Assets, governed elements or DataFlow "
                              "relationships.",
            ),
            out=[
                _field("cataloged", "Cataloged", "int", unit="Assets"),
                _field("documented", "Documented", "int", unit="Assets"),
                _field("classified", "Classified", "int", unit="elements"),
                _field("lineage", "Lineage-traced", "int", unit="relationships"),
                _field("aiReady", "AI-ready (always empty here; see ai_ready_assets)", "int", unit="Assets"),
            ],
        ),
    ),
    "ai_ready_assets": AnalyticFunctionSpec(
        name="ai_ready_assets",
        function="pyegeria.view.overview_metrics.ai_ready_assets",
        inputs=["egeria_client:MetadataExpert", "egeria_client:ClassificationExplorer"],
        description="The true 'AI-Ready' composite: Asset elements that are governed AND documented "
                    "AND lineage-traced simultaneously, not three independent counts intersected after "
                    "the fact. First real implementation of the composite/derived analytic metric "
                    "pattern -- see NEXT-18 (egeria-workspaces BACKLOG.md) for why this pattern didn't "
                    "exist here before. Takes two leading clients (mgr, ce), same convention as "
                    "semantic_grounding/context_readiness_funnel. "
                    "Cost: one Asset find page (a full page is a sample, so not measured) plus every DataFlow "
                    "relationship page, seconds.",
        returns="dict (aiReadyCount, total, capped)",
        generic=False,
        binding_note="Fixed to governed+documented+lineage-traced over Asset elements -- not a parameter.",
        params=[_as_of()],
        declaration=AnalyticDeclaration(
            result_kind="measure",
            measures=[
                _measure("assets_checked", "Assets", "total", completeness_field="capped", population="viewer"),
                _measure("ai_ready_assets", "Assets that are governed, documented and lineage-traced",
                         "aiReadyCount", completeness_field="capped", population="viewer",
                         basis=_basis("total", "Assets checked")),
            ],
            absence=_absence(
                not_measured="AI readiness was not measured: the Asset find or the DataFlow query failed.",
                not_permitted="You are not permitted to read the Assets, so AI readiness was not measured.",
                not_applicable=_always_applies("AI readiness"),
                nothing_found="Checked: there are no active Assets to assess.",
            ),
            out=[
                _field("aiReadyCount", "AI-ready Assets", "int", unit="Assets"),
                _field("total", "Assets checked", "int", unit="Assets"),
                _field("capped", "Asset page full (true: a sample, so nothing is measured)", "bool"),
            ],
        ),
    ),
    "drl_readiness_gates": AnalyticFunctionSpec(
        name="drl_readiness_gates",
        function="pyegeria.view.overview_metrics.drl_readiness_gates",
        inputs=["egeria_client:MetadataExpert", "egeria_client:ClassificationExplorer"],
        description="A recency-narrowed view of ai_ready_assets plus a modality breakdown "
                    "(tabular / text_media / other) of the Asset population -- the two Data "
                    "Readiness Level pieces computable today. Not a DRL band distribution: "
                    "Analytics-Ready and RAG-Ready are deliberately absent until their gates exist. "
                    "Takes two leading clients (mgr, ce). Cost: one Asset find page (a full page is a sample, "
                    "so not measured) and every DataFlow relationship page, seconds.",
        returns="dict (total, capped, aiReadyCount, aiReadyRecentCount, byModality)",
        generic=False,
        binding_note="Fixed to governed+documented+lineage-traced Asset elements and the "
                     "asset_modality type lists -- recency_days tunes the window, not what is measured.",
        params=[
            _as_of(),
            AnalyticParam(name="recency_days", type="int", default=180,
                          description="Provisional recency window, in days (not yet a decided band threshold)."),
        ],
        declaration=AnalyticDeclaration(
            result_kind="measure",
            measures=[
                _measure("assets_checked", "Assets", "total", completeness_field="capped", population="viewer"),
                _measure("ai_ready_assets", "Assets that are governed, documented and lineage-traced",
                         "aiReadyCount", completeness_field="capped", population="viewer",
                         basis=_basis("total", "Assets checked")),
                _measure("ai_ready_recent_assets", "AI-ready Assets updated within recency_days",
                         "aiReadyRecentCount", completeness_field="capped", population="viewer",
                         basis=_basis("aiReadyCount", "AI-ready Assets")),
                _measure("tabular_assets", "tabular Assets", "byModality.tabular",
                         completeness_field="capped", population="viewer", basis=_basis("total", "Assets checked")),
                _measure("text_media_assets", "text and media Assets", "byModality.text_media",
                         completeness_field="capped", population="viewer", basis=_basis("total", "Assets checked")),
                _measure("other_assets", "Assets of other modalities", "byModality.other",
                         completeness_field="capped", population="viewer", basis=_basis("total", "Assets checked")),
            ],
            absence=_absence(
                not_measured="Readiness gates were not measured: the Asset find or the DataFlow query failed.",
                not_permitted="You are not permitted to read the Assets, so the readiness gates were "
                              "not measured.",
                not_applicable=_always_applies("The readiness gates"),
                nothing_found="Checked: there are no active Assets to assess.",
            ),
            out=[
                _field("total", "Assets checked", "int", unit="Assets"),
                _field("capped", "Asset page full (true: a sample, so nothing is measured)", "bool"),
                _field("aiReadyCount", "AI-ready Assets", "int", unit="Assets"),
                _field("aiReadyRecentCount", "AI-ready and recent", "int", unit="Assets"),
                _field("byModality", "By modality", "map<string,int>", unit="Assets"),
            ],
        ),
    ),
    "growth_series": AnalyticFunctionSpec(
        name="growth_series",
        function="pyegeria.view.overview_metrics.growth_series",
        inputs=["egeria_client:MetadataExpert"],
        description="Snapshot-based growth series (assets/terms/governed/products by default) via "
                    "asOfTime, one point per window step. The one shape SERIES output format "
                    "(a Vega-Lite line chart) is proven against today. "
                    "Cost: one native count per series per snapshot (four series by default), sub-second each "
                    "in the repository population." + REPOSITORY_WORDS,
        returns="list[dict] (time series: {label, date, <series_key>: count, ...})",
        # Generic: what it counts is type_map. (Its binding_note used to repeat type_map's own
        # description; a generic routine fixes nothing, so it declares no note -- RS-W2-2.)
        generic=True,
        params=[
            AnalyticParam(name="window", type="str", default="6mo",
                          description="8h|1d|3d|7d|30d|90d|6mo|1y -- sets span + default point count."),
            AnalyticParam(name="points", type="int",
                          description="Override the number of snapshots (2-24)."),
            AnalyticParam(name="type_map", type="list[tuple[str, str, list[str] | None]]",
                          description="Override which series to snapshot; defaults to assets/terms/governed/products."),
            _population(),
        ],
        declaration=AnalyticDeclaration(
            result_kind="series",
            # One row per snapshot, oldest first; the measures are the default type_map's keys.
            measures=[
                _measure("assets", "Assets", "assets", as_of="date", population="repository"),
                _measure("terms", "GlossaryTerm elements", "terms", as_of="date", population="repository"),
                _measure("governed", "elements of any type carrying a governance classification",
                         "governed", as_of="date", population="repository"),
                _measure("products", "DigitalProduct elements", "products", as_of="date", population="repository"),
            ],
            absence=_absence(
                not_measured="The growth series was not measured: the snapshot counts failed.",
                not_permitted="You are not permitted to count these elements, so the growth series "
                              "was not measured.",
                not_applicable="A growth series does not apply to this window: it needs at least two "
                               "snapshots.",
                nothing_found="Counted: there were no elements of these types at any snapshot in the window.",
            ),
            out=[
                _field("label", "Snapshot", "string"),
                _field("date", "Date", "string"),
                _field("assets", "Assets", "int", unit="Assets"),
                _field("terms", "Terms", "int", unit="elements"),
                _field("governed", "Governed", "int", unit="elements"),
                _field("products", "Products", "int", unit="elements"),
            ],
        ),
    ),
    "term_definition_completeness": AnalyticFunctionSpec(
        name="term_definition_completeness",
        function="pyegeria.view.overview_metrics.term_definition_completeness",
        inputs=["egeria_client:MetadataExpert"],
        description="Share of GlossaryTerms whose description is set and not empty -- a definitions-"
                    "coverage metric, distinct from semantic_grounding (term<->asset linkage, not "
                    "whether the term itself is actually defined). "
                    "Both numbers are native counts in the repository population, so the share never mixes "
                    "populations; a whitespace-only description counts as defined. "
                    "Cost: two native counts, sub-second each." + REPOSITORY_WORDS,
        returns="dict (total, defined, undefinedPct)",
        generic=False,
        binding_note="Fixed to GlossaryTerm's description property -- not a parameter.",
        params=[_as_of()],
        declaration=AnalyticDeclaration(
            result_kind="measure",
            # Two native counts in one population: the share never divides across populations.
            measures=[
                _measure("terms", "GlossaryTerm elements", "total", population="repository"),
                _measure("defined_terms", "GlossaryTerm elements with a description (set, not empty)", "defined",
                         population="repository", basis=_basis("total", "terms")),
                _measure("undefined_percent", "percent of terms without a description (0-100)",
                         "undefinedPct", population="repository"),
            ],
            absence=_absence(
                not_measured="Term definitions were not measured: a count failed, or the server could not "
                             "answer it in the repository population.",
                not_permitted="You are not permitted to read the glossary terms.",
                not_applicable=_always_applies("Term definition completeness"),
                nothing_found="Counted: there are no active glossary terms.",
            ),
            out=[
                _field("total", "Terms", "int", unit="elements"),
                _field("defined", "Defined", "int", unit="elements"),
                _field("undefinedPct", "Undefined", "int", unit="percent"),
            ],
        ),
    ),
    "active_contributors": AnalyticFunctionSpec(
        name="active_contributors",
        function="pyegeria.view.overview_metrics.active_contributors",
        inputs=["egeria_client:ClassificationExplorer"],
        description="Distinct usernames behind at least one feedback relationship (ratings/comments/"
                    "likes/tags/noteLogs) -- an engagement signal feedback_summary's raw relationship "
                    "counts don't give you (one prolific commenter vs. many occasional ones). "
                    "Cost: five relationship scans, paged until Egeria returns an empty page, seconds.",
        returns="dict (contributors, byType)",
        generic=False,
        binding_note="Fixed to Collaboration OMAS's feedback relationship types -- not a parameter.",
        params=[_as_of()],
        declaration=AnalyticDeclaration(
            result_kind="measure",
            # Users who attached feedback, read from relationship audit headers (createdBy).
            measures=[
                _measure("contributors", "distinct users who attached feedback", "contributors",
                         population="viewer"),
                _measure("raters", "distinct users who attached a rating", "byType.ratings", population="viewer"),
                _measure("commenters", "distinct users who attached a comment", "byType.comments",
                         population="viewer"),
                _measure("likers", "distinct users who attached a like", "byType.likes", population="viewer"),
                _measure("taggers", "distinct users who attached a tag", "byType.tags", population="viewer"),
                _measure("note_loggers", "distinct users who attached a note log", "byType.noteLogs",
                         population="viewer"),
            ],
            absence=_absence(
                not_measured="Contributors were not counted: a feedback relationship query failed.",
                not_permitted="You are not permitted to read feedback relationships, so contributors "
                              "were not counted.",
                not_applicable=_always_applies("Counting contributors"),
                nothing_found="Counted: nobody has attached a rating, comment, like, tag or note log.",
            ),
            out=[
                _field("contributors", "Contributors", "int", unit="users"),
                _field("byType", "By feedback type", "map<string,int>", unit="users"),
            ],
        ),
    ),
    "sum_type_counts": AnalyticFunctionSpec(
        name="sum_type_counts",
        function="pyegeria.view.overview_metrics.sum_type_counts",
        inputs=["egeria_client:MetadataExpert"],
        description="Sum of counts_by_type() across a caller-given (label, type_name) list -- "
                    "e.g. the Overview dashboard's 'Cataloged Assets' total. First real registered "
                    "user of the fetch+analytic action shape (see AnalyticActionSpec) -- fetch is "
                    "counts_by_type itself (already registered above, reused as-is), analytic is a "
                    "small sum-reducer over its result; `function` above is the thin composite "
                    "wrapper that runs both via run_analytic_action, so calling it directly (the "
                    "old, single-function path) still works exactly like every other entry here. "
                    "Cost: as counts_by_type: one native count per type." + REPOSITORY_WORDS,
        returns="dict (total, byType)",
        generic=True,
        action=AnalyticActionSpec(
            fetch="pyegeria.view.overview_metrics.counts_by_type",
            analytic="pyegeria.view.overview_metrics.sum_counts",
            fetch_params=[
                AnalyticParam(name="type_map", type="list[tuple[str, str]]", required=True,
                              description="(label, type_name) pairs to count and sum."),
                _as_of(),
            ],
        ),
        params=[
            AnalyticParam(name="type_map", type="list[tuple[str, str]]", required=True,
                          description="(label, type_name) pairs to count and sum."),
            _as_of(),
        ],
        declaration=AnalyticDeclaration(
            result_kind="measure",
            measures=[_measure("total", "elements", "total", population="repository")],
            absence=_absence(
                not_measured="The total was not counted: the per-type count queries failed.",
                not_permitted="You are not permitted to count elements of these types.",
                not_applicable="A total does not apply: no types were given to count.",
                nothing_found="Counted: there are no active elements of any of these types.",
            ),
            out=[
                _field("total", "Total", "int", unit="elements"),
                _field("byType", "By type", kind="dataset", shape="TypeCount"),
            ],
        ),
    ),
    "count_elements_by_property": AnalyticFunctionSpec(
        name="count_elements_by_property",
        function="pyegeria.view.overview_metrics.count_elements_by_property",
        inputs=["egeria_client:MetadataExpert"],
        description="Count active elements of a given type whose named string property equals a "
                    "given value (or, with operator NEQ, is set and differs) -- e.g. DigitalProduct elements with "
                    "deploymentStatus=ACTIVE. Same count seam as count_elements: one cheap native COUNT "
                    "call per distinct value, no element fetch; a capped-find fallback only in the "
                    "viewer population. "
                    "Cost: one native count, sub-second in the repository population; a viewer-population count can take minutes for a large type." + REPOSITORY_WORDS,
        returns="scalar (int)",
        generic=True,
        params=[
            AnalyticParam(name="type_name", type="str", required=True,
                          description="Open metadata type to count, e.g. DigitalProduct."),
            AnalyticParam(name="property_name", type="str", required=True,
                          description="String property to match, e.g. deploymentStatus."),
            AnalyticParam(name="property_value", type="str", required=True,
                          description="Value to match the property against, e.g. ACTIVE."),
            AnalyticParam(name="operator", type="str", default="EQ",
                          description="EQ (equals the value) or NEQ (set, and not the value; "
                                      "property_value='' counts elements with the property set and not empty)."),
            _as_of(),
            _strict(),
            _population(),
        ],
        declaration=AnalyticDeclaration(
            result_kind="measure",
            measures=[_measure("elements", "elements", "value", population="repository")],
            absence=_absence(
                not_measured="The elements were not counted: the count query failed or timed out, or "
                             "the server could not answer it in the population asked for. A fallback "
                             "that stopped at its page cap is a lower bound, never a total.",
                not_permitted="You are not permitted to count these elements.",
                not_applicable="This count does not apply: the type or property named is not one "
                               "the server knows.",
                nothing_found="Counted: no active element of this type has this property value.",
            ),
            out=[_field("value", "Elements", "int", unit="elements")],
        ),
    ),
    "count_relationships": AnalyticFunctionSpec(
        name="count_relationships",
        function="pyegeria.view.overview_metrics.count_relationships",
        # EgeriaTech, as for feedback_summary: the repository count needs MetadataExpert's native method.
        inputs=["egeria_client:EgeriaTech"],
        description="Count active relationships of one type. By default a native count over the "
                    "whole repository, which needs a client with the native count (EgeriaTech has it; "
                    "a bare ClassificationExplorer does not, and gives not measured). population=viewer "
                    "without a MetadataExpert reads one capped get_relationships page instead (the two "
                    "paths can disagree for some types, PY-18). Takes an EgeriaTech as its leading client. "
                    "Cost: the native count is sub-second; a relationship page takes seconds." + REPOSITORY_WORDS,
        returns="scalar (int | None)",
        generic=True,
        params=[
            AnalyticParam(name="relationship_type", type="str", required=True,
                          description="Relationship type to count, e.g. SemanticAssignment."),
            _as_of(),
            _population(),
        ],
        declaration=AnalyticDeclaration(
            result_kind="measure",
            measures=[_measure("relationships", "relationships", "value", population="repository")],
            absence=_absence(
                not_measured="The relationships were not counted: the query failed, or a "
                             "repository count was asked for and no native count could answer it.",
                not_permitted="You are not permitted to read these relationships.",
                not_applicable="This count does not apply: the relationship type named is not one "
                               "the server knows.",
                nothing_found="Counted: there are no active relationships of this type.",
            ),
            out=[_field("value", "Relationships", "int", unit="relationships")],
        ),
    ),
    "contextualised_coverage": AnalyticFunctionSpec(
        name="contextualised_coverage",
        function="pyegeria.view.overview_metrics.contextualised_coverage",
        inputs=["egeria_client:MetadataExpert", "egeria_client:ClassificationExplorer"],
        description="Percent of Assets given business/solution-design context via an ImplementedBy "
                    "relationship to a SolutionComponent. A proxy, not the literal 'participates in "
                    "an ISC/blueprint' metric -- confirms some solution-design context exists, not "
                    "that the specific SolutionComponent is itself wired into an ISC/blueprint (a "
                    "second hop this function doesn't take). Takes two leading clients (mgr, ce), "
                    "same convention as semantic_grounding. "
                    "Cost: one relationship scan, paged until Egeria returns an empty page, plus one count, seconds.",
        returns="dict (contextualisedCount, assetTotal, contextualisedPct)",
        generic=False,
        binding_note="Fixed to the ImplementedBy relationship, filtered to Asset-subtype ends -- not a parameter.",
        params=[_as_of()],
        declaration=AnalyticDeclaration(
            result_kind="measure",
            measures=[
                _measure("contextualised_assets", "Assets that implement a SolutionComponent (ImplementedBy)",
                         "contextualisedCount", population="viewer"),
                _measure("assets", "Assets", "assetTotal"),
                _measure("contextualised_percent", "percent of Assets (0-100)", "contextualisedPct"),
            ],
            absence=_absence(
                not_measured="Contextualised coverage was not measured: the ImplementedBy query or the "
                             "Asset count failed.",
                not_permitted="You are not permitted to read the ImplementedBy relationships.",
                not_applicable=_always_applies("Contextualised coverage"),
                nothing_found="Counted: no Asset implements a solution component.",
            ),
            out=[
                _field("contextualisedCount", "Contextualised Assets", "int", unit="Assets"),
                _field("assetTotal", "Assets", "int", unit="Assets"),
                _field("contextualisedPct", "Contextualised", "float", unit="percent"),
            ],
        ),
    ),
    "solution_component_realisation": AnalyticFunctionSpec(
        name="solution_component_realisation",
        function="pyegeria.view.overview_metrics.solution_component_realisation",
        inputs=["egeria_client:MetadataExpert", "egeria_client:ClassificationExplorer"],
        description="SolutionComponent count and how many of them are realised (have at least one "
                    "ImplementedBy implementation) -- the Overview's Solution Blueprints drill-down. A "
                    "single-hop proxy: the implementation need not itself sit in the component's "
                    "supply chain or blueprint. Takes two leading clients (mgr, ce). Cost: one native "
                    "count plus one ImplementedBy relationship scan, paged until Egeria returns an empty page, seconds.",
        returns="dict (solutionComponentsTotal, solutionComponentsRealised)",
        generic=False,
        binding_note="Fixed to SolutionComponent and the ImplementedBy relationship -- not a parameter.",
        params=[_as_of()],
        declaration=AnalyticDeclaration(
            result_kind="measure",
            measures=[
                _measure("solution_components", "SolutionComponent elements", "solutionComponentsTotal"),
                _measure("realised_components", "SolutionComponents with an ImplementedBy implementation",
                         "solutionComponentsRealised", population="viewer"),
            ],
            absence=_absence(
                not_measured="Solution component realisation was not measured: the count or the "
                             "ImplementedBy query failed.",
                not_permitted="You are not permitted to read solution components or their implementations.",
                not_applicable=_always_applies("Solution component realisation"),
                nothing_found="Counted: there are no active solution components.",
            ),
            out=[
                _field("solutionComponentsTotal", "Solution components", "int", unit="elements"),
                _field("solutionComponentsRealised", "Realised", "int", unit="elements"),
            ],
        ),
    ),
    "karma_leaderboard": AnalyticFunctionSpec(
        name="karma_leaderboard",
        function="pyegeria.view.overview_metrics.karma_leaderboard",
        inputs=["egeria_client:MetadataExpert"],
        description="Top-N people by karma -- every ContributionRecord, karmaPoints is a "
                    "scalar property on the record itself (not derived from counting related things), "
                    "filtered to the given anchor type(s) via each record's own Anchors classification. "
                    "Cost: one find, paged until Egeria returns an empty page, seconds.",
        returns="list[dict] (name, karmaPoints, anchorGuid, anchorType), longest-karma first",
        generic=False,
        binding_note="Fixed to ContributionRecord.karmaPoints -- top_n and anchor_types tune the "
                     "result but don't change what's being measured.",
        params=[
            AnalyticParam(name="top_n", type="int", default=10, description="How many entries to return."),
            AnalyticParam(name="anchor_types", type="list[str]", default=["Person"],
                          description="Anchor typeName(s) to include, e.g. ['Person', 'ITProfile']."),
            _as_of(),
        ],
        declaration=AnalyticDeclaration(
            result_kind="list",
            measures=[_measure("karma_points", "karma points", "karmaPoints")],
            listing=ListDeclaration(item_fields=["name", "karmaPoints", "anchorType"],
                                    order="most karma first", key_field="anchorGuid",
                                    item_label="contributors"),
            absence=_absence(
                not_measured="The leaderboard was not read: the find of contribution records failed.",
                not_permitted="You are not permitted to read contribution records.",
                not_applicable="A leaderboard does not apply to these anchor types: no contribution "
                               "record is anchored to them.",
                nothing_found="Read: nobody of these anchor types has a contribution record with karma "
                              "points.",
            ),
            out=[
                _field("name", "Name", "string"),
                _field("karmaPoints", "Karma points", "int", unit="karma points"),
                _field("anchorGuid", "Profile", "guid"),
                _field("anchorType", "Profile type", "string"),
            ],
        ),
    ),
    "engagement_series": AnalyticFunctionSpec(
        name="engagement_series",
        function="pyegeria.view.overview_metrics.engagement_series",
        inputs=["egeria_client:ClassificationExplorer"],
        description="Weekly-bucketed feedback-event trend (comments/ratings/likes/tags/noteLogs), "
                    "zero-filled across the trailing window -- reuses the same 5 relationship-type "
                    "queries feedback_summary() already makes, keeping createTime instead of only "
                    "the count. Takes ce as its leading client. "
                    "Cost: five relationship scans, paged until Egeria returns an empty page, seconds.",
        returns="list[dict] (week, comments, ratings, likes, tags, noteLogs, total), oldest week first",
        generic=False,
        binding_note="Fixed to Collaboration OMAS's 5 feedback relationship types -- weeks tunes the window, not what's measured.",
        params=[
            AnalyticParam(name="weeks", type="int", default=12, description="Trailing window size, in weeks."),
            _as_of(),
        ],
        declaration=AnalyticDeclaration(
            result_kind="series",
            # One row per ISO week, oldest first, zero-filled; each type is read in full (None when not measured).
            measures=[
                _measure("feedback", "feedback relationships created in the week", "total", as_of="week",
                         population="viewer"),
                _measure("comments", "AttachedComment relationships created in the week", "comments",
                         as_of="week", population="viewer"),
                _measure("ratings", "AttachedRating relationships created in the week", "ratings",
                         as_of="week", population="viewer"),
                _measure("likes", "AttachedLike relationships created in the week", "likes",
                         as_of="week", population="viewer"),
                _measure("tags", "AttachedTag relationships created in the week", "tags",
                         as_of="week", population="viewer"),
                _measure("note_logs", "AttachedNoteLog relationships created in the week", "noteLogs",
                         as_of="week", population="viewer"),
            ],
            absence=_absence(
                not_measured="Engagement was not measured: the feedback relationship queries failed.",
                not_permitted="You are not permitted to read feedback relationships.",
                not_applicable="An engagement series does not apply to a window of no weeks.",
                nothing_found="Counted: no feedback was attached in any week of the window.",
            ),
            out=[
                _field("week", "Week", "string"),
                _field("comments", "Comments", "int", unit="relationships"),
                _field("ratings", "Ratings", "int", unit="relationships"),
                _field("likes", "Likes", "int", unit="relationships"),
                _field("tags", "Tags", "int", unit="relationships"),
                _field("noteLogs", "Note logs", "int", unit="relationships"),
                _field("total", "Total", "int", unit="relationships"),
            ],
        ),
    ),
    "orphan_glossary_terms": AnalyticFunctionSpec(
        name="orphan_glossary_terms",
        function="pyegeria.view.overview_metrics.orphan_glossary_terms",
        inputs=["egeria_client:MetadataExpert", "egeria_client:ClassificationExplorer"],
        description="Approved-but-unassigned glossary terms -- a term with no SemanticAssignment "
                    "relationship to anything was authored but never put to use grounding the "
                    "catalog. One bounded SemanticAssignment fetch, distinct GlossaryTerm-end GUID "
                    "count is the 'referenced' set; orphan = term total - referenced. Takes two "
                    "leading clients (mgr, ce), same convention as semantic_grounding. "
                    "Cost: one count plus one relationship scan, paged until Egeria returns an empty page, seconds.",
        returns="dict (termTotal, referencedCount, orphanCount)",
        generic=False,
        binding_note="Fixed to the SemanticAssignment relationship type and GlossaryTerm elements -- not a parameter.",
        params=[_as_of()],
        declaration=AnalyticDeclaration(
            result_kind="measure",
            measures=[
                _measure("terms", "GlossaryTerm elements", "termTotal"),
                _measure("referenced_terms", "GlossaryTerm elements assigned to something", "referencedCount",
                         population="viewer"),
                _measure("orphan_terms", "GlossaryTerm elements assigned to nothing", "orphanCount",
                         basis=_basis("termTotal", "glossary terms")),
            ],
            absence=_absence(
                not_measured="Orphan terms were not measured: the term count or the SemanticAssignment "
                             "query failed.",
                not_permitted="You are not permitted to read the glossary terms or their assignments.",
                not_applicable=_always_applies("Finding orphan glossary terms"),
                nothing_found="Counted: every glossary term is assigned to something, or there are no terms.",
            ),
            out=[
                _field("termTotal", "Terms", "int", unit="elements"),
                _field("referencedCount", "Assigned", "int", unit="elements"),
                _field("orphanCount", "Orphans", "int", unit="elements"),
            ],
        ),
    ),
    "stale_assets": AnalyticFunctionSpec(
        name="stale_assets",
        function="pyegeria.view.overview_metrics.stale_assets",
        inputs=["egeria_client:MetadataExpert"],
        description="Assets with no update in the last N days (default 180) -- candidates for "
                    "archival review. One bounded Asset element fetch, each element's own version "
                    "metadata compared against the cutoff, no relationship traversal. "
                    "Cost: one Asset find page (a full page is a sample, so staleCount is not measured) plus one "
                    "count, seconds.",
        returns="dict (staleCount, assetTotal)",
        generic=False,
        binding_note="Fixed to the Asset type -- population isn't a parameter, but the staleness threshold (days) is.",
        params=[
            AnalyticParam(name="days", type="int", default=180, description="Staleness threshold, in days."),
            _as_of(),
        ],
        declaration=AnalyticDeclaration(
            result_kind="measure",
            # staleCount comes from one find page (None when full), assetTotal from a native count: no basis.
            measures=[
                _measure("stale_assets", "Assets not updated within `days` (not measured when the Asset find fills its page)",
                         "staleCount", population="viewer"),
                _measure("assets", "Assets", "assetTotal"),
            ],
            absence=_absence(
                not_measured="Stale assets were not measured: the Asset find failed, or it filled its page, "
                             "so it held only some of the Assets.",
                not_permitted="You are not permitted to read the Assets.",
                not_applicable=_always_applies("Finding stale assets"),
                nothing_found="Checked: every Asset read was updated within the threshold, or there are no Assets.",
            ),
            out=[
                _field("staleCount", "Stale Assets", "int", unit="Assets"),
                _field("assetTotal", "Assets", "int", unit="Assets"),
            ],
        ),
    ),
    "metric_trend": AnalyticFunctionSpec(
        name="metric_trend",
        function="pyegeria.view.overview_metrics.metric_trend",
        # A target that declares EgeriaTech for a slot (feedback_summary, count_relationships: a repository
        # relationship count needs MetadataExpert's native method) gets the EgeriaTech in that slot.
        inputs=["egeria_client:EgeriaTech", "egeria_client:ClassificationExplorer"],
        description="Turn any single-snapshot function in this module into a time series, by "
                    "re-calling it once per asOfTime snapshot -- the same windowing growth_series "
                    "uses, generalized to any function here instead of one hardcoded type_map. Takes "
                    "two leading clients (mgr, ce) -- the executor supplies the same EgeriaTech "
                    "instance for both, matching semantic_grounding's convention. "
                    "Cost: the target routine's cost once per snapshot.",
        returns="list[dict] (time series: {label, date, **snapshot})",
        generic=True,
        params=[
            AnalyticParam(name="metric_path", type="str", required=True,
                          description="Registered name of the target analytic function, e.g. "
                                       "'governed_coverage'. A dotted path is deprecated."),
            AnalyticParam(name="window", type="str", default="6mo",
                          description="8h|1d|3d|7d|30d|90d|6mo|1y -- sets span + default point count."),
            AnalyticParam(name="points", type="int",
                          description="Override the number of snapshots (2-24)."),
            AnalyticParam(name="metric_params", type="dict",
                          description="Extra keyword arguments forwarded to the target function at "
                                       "every snapshot (e.g. classifications for count_elements)."),
        ],
        declaration=AnalyticDeclaration(
            result_kind="series",
            # A row is the target routine's own result fields (a dict merged in) or `value` (anything
            # else); the target's declaration says what those fields are.
            measures=[_measure("value", "the target routine's unit", "value", as_of="date")],
            absence=_absence(
                not_measured="The trend was not measured: the target routine failed at every snapshot.",
                not_permitted="You are not permitted to run the target routine, so the trend was not measured.",
                not_applicable="A trend does not apply: the target routine does not take an as_of time.",
                nothing_found="Measured: the target routine found nothing at any snapshot in the window.",
            ),
            out=[
                _field("label", "Snapshot", "string"),
                _field("date", "Date", "string"),
                _field("value", "Value", "float"),
            ],
        ),
    ),
    "asset_composition": AnalyticFunctionSpec(
        name="asset_composition",
        function="pyegeria.view.overview_metrics.asset_composition",
        inputs=["egeria_client:EgeriaTech"],
        description="The composition of a type (default Asset) by subtype: one row per type in its "
                    "subtype tree to `depth`, each counted in viewer and/or repository scope, an "
                    "`other` row per parent (elements typed as exactly the parent), and not_visible = "
                    "repository - viewer. Stages (reporting model §10.8): a `typedefs` producer, two "
                    "per-row `derive`s (viewer count, repository count) and a `difference`. All counts "
                    "share one pool of `concurrency` workers (default 3, capped at 5). Takes two "
                    "leading clients (mgr, vm); vm defaults to mgr (an EgeriaTech has both). "
                    "Cost: one count per type per population in a pool of 3-5; repository counts sub-second, viewer counts can take minutes for a large type (Process: 120 s).",
        returns="AssetComposition (dict: state, state_reason, root, depth, populations, as_of, concurrency, "
                "rows[{type_name, parent, level, exact_type, subtypes_error, viewer?, repository?, "
                "not_visible}], not_measured, provenance); each count cell is {value, state, "
                "completeness, as_of, population, reason, elapsed_s}",
        generic=True,
        envelope=True,
        params=[
            AnalyticParam(name="root", type="str", default="Asset",
                          description="The type whose subtypes are counted."),
            AnalyticParam(name="depth", type="int", default=2,
                          description="Subtype levels below root (0 = root only)."),
            _as_of("ISO-8601 asOfTime for point-in-time counts (None = now); the subtype tree is today's."),
            AnalyticParam(name="populations", type="list[str]", default=["viewer", "repository"],
                          description="Populations to count: viewer (what the caller may see) and/or "
                                      "repository (whole repository, fast). Each cell names its "
                                      "population under `population`."),
            AnalyticParam(name="concurrency", type="int", default=3,
                          description="Counts in flight at once across both scopes, 1-5 (above 5 is "
                                      "lowered to 5: Egeria's database pool is 10 connections)."),
        ],
        declaration=AnalyticDeclaration(
            result_kind="distribution",
            measures=[
                MeasureDeclaration(name="repository_count", unit="elements", as_of="as_of",
                                   value_field="rows.repository.value",
                                   completeness_field="rows.repository.completeness", population="repository"),
                MeasureDeclaration(name="viewer_count", unit="elements", as_of="as_of",
                                   value_field="rows.viewer.value",
                                   completeness_field="rows.viewer.completeness", population="viewer"),
                MeasureDeclaration(name="not_visible", unit="elements", as_of="as_of",
                                   value_field="rows.not_visible.value"),
            ],
            # A parent row counts its subtypes too, so the rows overlap and never sum.
            categories=CategoriesDeclaration(exclusive=False),
            absence=AbsenceSentences(
                not_measured="The subtype counts could not be measured: the count queries failed or "
                             "the server could not answer them.",
                not_permitted="You are not permitted to count these elements.",
                not_applicable="A subtype composition does not apply to this type.",
                nothing_found="Counted: there are no elements of this type or its subtypes.",
            ),
            out=[
                _field("state", "State", "string"),
                _field("state_reason", "Why", "string"),
                _field("root", "Root type", "string"),
                _field("depth", "Depth", "int"),
                _field("as_of", "As of", "datetime"),
                _field("concurrency", "Counts in flight", "int"),
                _field("rows", "Types", kind="dataset", shape="CompositionRow"),
                _field("not_measured", "Not measured", "list<string>"),
            ],
        ),
    ),
    "control_implementation_summary": AnalyticFunctionSpec(
        name="control_implementation_summary",
        function="pyegeria.view.overview_metrics.control_implementation_summary",
        inputs=["egeria_client:SecurityOfficer"],
        description="Applicable controls in a statement of applicability, counted by implementation "
                    "status (NOT_STARTED, PLANNED, PARTIALLY_IMPLEMENTED, IMPLEMENTED, OTHER). "
                    "Cost: one read of one statement of applicability's control relationships, seconds.",
        returns="dict ({status: count})",
        generic=False,
        binding_note="Fixed to the ControlApplicability relationships of one StatementOfApplicability.",
        params=[
            AnalyticParam(name="soa_guid", type="str", required=True,
                          description="GUID of the statement of applicability."),
        ],
        declaration=AnalyticDeclaration(
            result_kind="distribution",
            # No as_of parameter: the counts are of the moment the call ran.
            measures=[_measure(status.lower(), "applicable controls", status)
                      for status in ("NOT_STARTED", "PLANNED", "PARTIALLY_IMPLEMENTED", "IMPLEMENTED", "OTHER")],
            # One control has one implementation status; controls marked not applicable are left out.
            categories=CategoriesDeclaration(exclusive=True),
            absence=_absence(
                not_measured="Control implementation was not measured: the statement of applicability "
                             "could not be read.",
                not_permitted="You are not permitted to read this statement of applicability.",
                not_applicable="Control implementation does not apply: the element named is not a "
                               "statement of applicability.",
                nothing_found="Counted: this statement of applicability has no applicable controls.",
            ),
            out=[_field(status, label, "int", unit="controls") for status, label in (
                ("NOT_STARTED", "Not started"), ("PLANNED", "Planned"),
                ("PARTIALLY_IMPLEMENTED", "Partially implemented"), ("IMPLEMENTED", "Implemented"),
                ("OTHER", "Other"))],
        ),
    ),
}

_RUNTIME_ANALYTIC_FUNCTIONS = AnalyticFunctionDict()
_CONFIG_ANALYTIC_FUNCTIONS = AnalyticFunctionDict()

# Installed packages register analytic functions and steps through this entry-point
# group (ISSUE-172; the `trellis.analytics` alias was removed in 6.2.19). An entry point names an AnalyticFunctionSpec (or subclass), a list of them, or
# a callable returning either. Read lazily on first use of the registry; only the
# manifests are loaded then -- a function's own module is imported on its first run,
# by format_set_executor._resolve_analytic_function.
ANALYTIC_ENTRY_POINT_GROUP = "pyegeria.analytics"
_ENTRY_POINT_ANALYTIC_FUNCTIONS: Optional[AnalyticFunctionDict] = None  # None = not read yet
_ENTRY_POINT_ERRORS: Dict[str, str] = {}


class AnalyticRegistryCollision(ValueError):
    """Raised when two analytic-registry sources define the same function name."""
    pass


def _add_with_collision_check(target: AnalyticFunctionDict, new: Dict[str, AnalyticFunctionSpec], source: str) -> None:
    for name in new.keys():
        if name in target.keys():
            raise AnalyticRegistryCollision(
                f"Analytic function '{name}' already defined; conflict from {source}")
    for k, v in new.items():
        target[k] = v


def _load_json_file(path: str) -> AnalyticFunctionDict:
    p = Path(os.path.expanduser(path)).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Analytic functions JSON not found: {p}")
    import json
    raw = json.loads(p.read_text(encoding="utf-8"))
    return AnalyticFunctionDict({name: AnalyticFunctionSpec(**spec) for name, spec in raw.items()})


def refresh_analytic_functions() -> None:
    """Reload the CONFIG tier from JSON files and/or modules. Environment variables:
      - PYEGERIA_ANALYTIC_FUNCTIONS_JSON: comma-separated JSON file paths
      - PYEGERIA_ANALYTIC_FUNCTIONS_MODULES: comma-separated module callables
        (pkg.mod:func or pkg.mod.func) returning a dict/AnalyticFunctionDict
    Collisions across sources (including against BUILTINS) raise AnalyticRegistryCollision.
    Also forgets the installed (entry-point) tier, so it is re-read on next use.
    """
    global _CONFIG_ANALYTIC_FUNCTIONS, _ENTRY_POINT_ANALYTIC_FUNCTIONS
    _CONFIG_ANALYTIC_FUNCTIONS = AnalyticFunctionDict()
    _ENTRY_POINT_ANALYTIC_FUNCTIONS = None  # installed packages are re-read on next use

    json_paths = os.getenv("PYEGERIA_ANALYTIC_FUNCTIONS_JSON", "").strip()
    if json_paths:
        for raw in json_paths.split(","):
            raw = raw.strip()
            if not raw:
                continue
            loaded = _load_json_file(raw)
            _add_with_collision_check(_CONFIG_ANALYTIC_FUNCTIONS, loaded, source=f"JSON:{raw}")

    modules = os.getenv("PYEGERIA_ANALYTIC_FUNCTIONS_MODULES", "").strip()
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
            if not isinstance(loaded, AnalyticFunctionDict):
                loaded = AnalyticFunctionDict(loaded)
            _add_with_collision_check(_CONFIG_ANALYTIC_FUNCTIONS, loaded, source=f"MODULE:{m}")


def _read_entry_points() -> Tuple[AnalyticFunctionDict, Dict[str, str]]:
    """Load every manifest in the entry-point groups. A broken entry point is recorded
    in the returned errors, naming it, and the rest still load."""
    found = AnalyticFunctionDict()
    errors: Dict[str, str] = {}
    for group in (ANALYTIC_ENTRY_POINT_GROUP,):
        for ep in entry_points(group=group):
            label = f"{group}:{ep.name}"
            try:
                obj = ep.load()
                if callable(obj) and not isinstance(obj, AnalyticFunctionSpec):
                    obj = obj()
                items = obj if isinstance(obj, (list, tuple)) else [obj]
                for spec in items:
                    if not isinstance(spec, AnalyticFunctionSpec):
                        raise TypeError(f"{type(spec).__name__} is not an AnalyticFunctionSpec")
                    prior = found.get(spec.name)
                    if prior is not None and prior.function != spec.function:
                        raise AnalyticRegistryCollision(
                            f"'{spec.name}' is already provided by another entry point as {prior.function}")
                    found[spec.name] = spec
            except Exception as exc:  # noqa: BLE001 -- one broken package must not hide the others
                errors[label] = f"entry point {label} ({ep.value}) could not be loaded: {exc}"
                logger.warning(errors[label])
    return found, errors


def _entry_point_functions() -> AnalyticFunctionDict:
    global _ENTRY_POINT_ANALYTIC_FUNCTIONS, _ENTRY_POINT_ERRORS
    if _ENTRY_POINT_ANALYTIC_FUNCTIONS is None:
        _ENTRY_POINT_ANALYTIC_FUNCTIONS, _ENTRY_POINT_ERRORS = _read_entry_points()
    return _ENTRY_POINT_ANALYTIC_FUNCTIONS


def analytic_entry_point_errors() -> Dict[str, str]:
    """Entry points that are installed but could not be loaded, each with a sentence
    naming it and the error (empty when every one loaded, or none is installed)."""
    _entry_point_functions()
    return dict(_ENTRY_POINT_ERRORS)


def get_analytic_registry() -> AnalyticFunctionDict:
    """Combine built-ins, config-loaded, installed (entry-point) and runtime-registered
    analytic functions. Enforce no duplicate names across all sources, except that an
    installed function whose name is already a built-in or config entry is skipped and
    reported by analytic_entry_point_errors(), so an installed package can't break the
    registry for everyone."""
    combined = AnalyticFunctionDict()
    _add_with_collision_check(combined, _BUILTINS, source="BUILTINS")
    _add_with_collision_check(combined, _CONFIG_ANALYTIC_FUNCTIONS, source="CONFIG")
    for name, spec in _entry_point_functions().items():
        if name in combined:
            label = f"entry point function '{name}'"
            if label not in _ENTRY_POINT_ERRORS:
                _ENTRY_POINT_ERRORS[label] = (f"{label} ({spec.function}) was skipped: the name is already "
                                              f"defined by a built-in or config entry")
                logger.warning(_ENTRY_POINT_ERRORS[label])
            continue
        combined[name] = spec
    _add_with_collision_check(combined, _RUNTIME_ANALYTIC_FUNCTIONS, source="RUNTIME")
    return combined


def analytic_registry_payload() -> dict:
    """JSON-ready payload for an API endpoint (e.g. Egeria Explorer/Advisor's
    'browse analytic functions' view)."""
    registry = get_analytic_registry()
    return {
        "total": len(registry),
        "functions": {name: spec.dict() for name, spec in registry.items()},
        "entry_point_errors": analytic_entry_point_errors(),
    }


def register_analytic_functions(new_functions: Union[AnalyticFunctionDict, dict], *, source: str = "runtime") -> None:
    """Dynamically add analytic functions at runtime. Raises on duplicate name."""
    global _RUNTIME_ANALYTIC_FUNCTIONS
    if not isinstance(new_functions, AnalyticFunctionDict):
        new_functions = AnalyticFunctionDict(
            {k: (v if isinstance(v, AnalyticFunctionSpec) else AnalyticFunctionSpec(**v))
             for k, v in new_functions.items()}
        )
    existing = get_analytic_registry()
    for name in new_functions.keys():
        if name in existing.keys():
            raise AnalyticRegistryCollision(
                f"Analytic function '{name}' already exists; cannot register from {source}")
    for k, v in new_functions.items():
        _RUNTIME_ANALYTIC_FUNCTIONS[k] = v


def get_routine_registry() -> Dict[str, RoutineDeclaration]:
    """Every registry entry (built-in, config, installed, runtime) as a RoutineDeclaration: the
    declaration + bindings each `AnalyticFunctionSpec` is a view of. An entry that breaks a
    declaration rule is left out and named, with the rule's words, by `routine_declaration_errors()`;
    it still runs as before (RS-W2-2 PR-A changes no behaviour)."""
    routines, _ = _routines_and_errors()
    return routines


def routine_declaration_errors() -> Dict[str, str]:
    """Registry entries that cannot be read as a RoutineDeclaration, each with a sentence naming the
    entry and the rule it breaks (empty when every entry reads)."""
    _, errors = _routines_and_errors()
    return errors


def _routines_and_errors() -> Tuple[Dict[str, RoutineDeclaration], Dict[str, str]]:
    routines: Dict[str, RoutineDeclaration] = {}
    errors: Dict[str, str] = {}
    for name, spec in get_analytic_registry().items():
        try:
            routines[name] = spec.routine()
        except ValueError as exc:  # pydantic's ValidationError is a ValueError
            errors[name] = f"analytic function '{name}' is not a valid routine declaration: {exc}"
    return routines, errors


def unregister_analytic_function(name: str) -> bool:
    return bool(_RUNTIME_ANALYTIC_FUNCTIONS.pop(name, None))


def clear_runtime_analytic_functions() -> None:
    _RUNTIME_ANALYTIC_FUNCTIONS.clear()
