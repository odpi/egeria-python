"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

The `microflow/1` representation of a report spec's micro-flow, and its conversions
(report-spec pipeline model §7a "Representation", O-H4; RS-EGERIA-TIER stage 1).

A report spec held in Egeria stores its micro-flow, parameters and formatters as JSON text in the
`ReportSpec.microflow` property. Two formats exist:

- **format 0** (legacy): a bare JSON list of stages, each carrying its own `required_params`,
  `optional_params` and `columns`. This is what Dr.Egeria wrote before stage 1, and what
  `ReportSpec::E-Collections` holds. It is read with one warning naming the spec, through
  `microflow_from_legacy`, the one function that converts it.
- **format 1** (`microflow/1`): an object
  `{"format": "microflow/1", "params": {...}, "stages": [...], "formatters": {...}}`.
  `MicroflowV1` is the one parser for it; `schemas/microflow-1.json` is its JSON Schema.

Stage 1 runs a subset: `microflow_to_format_set` converts what today's executor can run into a
`FormatSet` (one `producer/find` stage, optionally followed by one registered analytic, or one
`producer/analytic` stage) and raises `CannotRunYet` with words for anything else.

Every Egeria-held spec is untrusted input. `check_allowlist` enforces §7a "Safety": a find stage
may name only a `Class.method` on `FIND_METHOD_ALLOWLIST` (a positive list: the methods today's
built-in specs name, plus reviewed additions) and never one on `FIND_METHOD_DENYLIST`; an analytic
stage only a registered analytic name; never a dotted module path or a `python` binding.
"""

from __future__ import annotations

import json
from collections import Counter
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

__all__ = [
    "MICROFLOW_FORMAT",
    "FIND_METHOD_ALLOWLIST",
    "FIND_METHOD_ADDITIONS",
    "FIND_METHOD_DENYLIST",
    "ADDITIONAL_PROPS_HOOKS",
    "LEGACY_CLASS_ALIASES",
    "ParamDecl",
    "Stage",
    "Formatter",
    "MicroflowV1",
    "MicroflowError",
    "CannotRunYet",
    "AllowlistRefusal",
    "parse_microflow",
    "normalize_microflow_text",
    "microflow_from_legacy",
    "microflow_to_format_set",
    "format_set_to_microflow",
    "check_allowlist",
    "find_method_allowed",
    "additional_props_allowed",
]

MICROFLOW_FORMAT = "microflow/1"

#: The find methods a spec held in Egeria may name, as `Class.method` exactly as the spec writes it
#: (an `_async_` twin of an entry is allowed too). A POSITIVE list: a method that is not on it is
#: refused, whatever its name (a find_/get_/list_ prefix is not proof that a method only reads; see
#: FIND_METHOD_DENYLIST). It is the union of two named parts:
#:
#: - `_CENSUS_FIND_METHODS`: every find method a runnable built-in or generated spec names, taken from
#:   the 437-spec census on 2026-11-09 (47 methods, every spec runnable since 6.2.28 repointed
#:   Asset-Graph and Data-Classes). The micro-test `test_every_runnable_builtin_spec_function_is_on_the_allowlist`
#:   fails when a built-in or generated spec names one that is missing, so the stage-2 seed (today's
#:   built-ins written into Egeria) can never be refused.
#: - `FIND_METHOD_ADDITIONS`: methods no built-in names yet, each added after reading it.
#:
#: Every entry is scanned for write words in its name and docstring by
#: `test_no_allowlisted_method_reads_as_a_write`; a hit must be reviewed there, by Class.method.
_CENSUS_FIND_METHODS: frozenset = frozenset({
    "ActorManager.find_actor_profiles",
    "ActorManager.find_actor_roles",
    "ActorManager.find_perspectives",
    "ActorManager.find_skills",
    "ActorManager.find_user_identities",
    "AssetCatalog.get_asset_graph_by_guid",
    "AssetMaker.find_assets",
    "ClassificationExplorer.find_elements_by_property_value",  # the 40 generic-search DrE specs (6.2.28)
    "ClassificationExplorer.get_elements",
    "ClassificationExplorer.get_owners_elements",
    "CollectionManager.find_collections",
    "CollectionManager.get_collection_members",
    "DataDesigner.find_data_fields",
    "DataDesigner.find_data_structures",
    "DataDesigner.find_data_value_specifications",
    "DataDiscovery.get_security_findings",
    "DataDiscovery.get_security_posture_history",
    "EgeriaTech.get_elements_by_property_value",
    "EgeriaTech.get_technology_type_elements",
    "ExternalReference.find_external_identifiers",
    "ExternalReference.find_external_references",
    "ExternalReferences.find_external_references",
    "GlossaryManager.find_glossaries",
    "GlossaryManager.find_glossary_terms",
    "GovernanceOfficer.find_governance_definitions",
    "MetadataExpert.find_metadata_elements_with_string",
    "MyProfile.get_my_profile",
    "MyProfile.get_my_to_dos",
    "ProjectManager.find_projects",
    "ReferenceDataManager.find_valid_value_definitions",
    "SecurityOfficer.find_statements_of_applicability",
    "SecurityOfficer.get_statement_of_applicability_controls",
    "ServerClient.find_comments",
    "ServerClient.find_notes",
    "ServerClient.find_tags",
    "ServerClient.find_technology_types",
    "ServerClient.get_attached_comments",
    "ServerClient.get_tech_type_detail",
    "SolutionArchitect.find_concept_model_elements",
    "SolutionArchitect.find_design_patterns",
    "SolutionArchitect.find_information_supply_chains",
    "SolutionArchitect.find_solution_blueprints",
    "SolutionArchitect.find_solution_components",
    "SolutionArchitect.find_solution_roles",
    "ValidMetadataManager.get_valid_metadata_values",
    "_client_new.find_search_keywords",
    "reference_data.find_valid_value_definitions",
})

#: Reviewed additions: find methods no built-in spec names yet. Add an entry only after reading the
#: method (it must only read), and give the reason in a comment beside it.
FIND_METHOD_ADDITIONS: frozenset = frozenset({
    # Read only: POSTs a FindRequestBody to .../elements/by-complex-query and returns the elements.
    # find_elements_by_property_value calls it for the technology specs (deployedImplementationType
    # EQ the technology AND the name match, evaluated by Egeria in one query).
    "ClassificationExplorer.find_root_elements",
})

FIND_METHOD_ALLOWLIST: frozenset = _CENSUS_FIND_METHODS | FIND_METHOD_ADDITIONS

#: Find methods an Egeria-held spec may never name. Kept beside the positive allowlist as a second,
#: independent check (belt and braces): an entry here is refused even if it is ever added to the
#: allowlist by mistake, and the micro-tests fail if the two lists overlap. Each entry here reads
#: like a find but writes to Egeria. An entry denies the method on every class that has it (and its
#: `_async_` twin), since EgeriaTech and its subclasses inherit it.
FIND_METHOD_DENYLIST: frozenset = frozenset({
    # "Create a CSV file element from a template if it doesn't exist": an Egeria write.
    "AutomatedCuration.get_create_csv_data_file_element_from_template",
})
_DENIED_METHOD_NAMES = frozenset(e.rsplit(".", 1)[-1] for e in FIND_METHOD_DENYLIST)

#: The functions a find stage's `additional_props` key may name (RS-EGERIA-TIER stage 2, brief
#: decision 4). `additional_props` carries today's `FormatSet.get_additional_props`: a client method
#: the formatter calls per element for extra properties. It names code, so it is a closed list, held
#: here beside the find-method allowlist: exactly the functions the built-in specs name on
#: 2026-11-09 (5 specs: Search-Keywords; Digital-Products, -MyE and -Slim; Agreements). Any other
#: name is refused, by `check_allowlist` and by `microflow_to_format_set`, with words.
ADDITIONAL_PROPS_HOOKS: frozenset = frozenset({
    "_client_extract_element_properties_for_keyword",
    "CollectionManager._extract_digital_product_properties",
    "CollectionManager._extract_agreement_properties",
})

#: Legacy class names that today's built-in specs use and the executor maps to a client class
#: (`_resolve_client_and_method` falls back to EgeriaTech for an unknown name). Listed explicitly so
#: the allowlist accepts exactly these, and no other unknown name.
LEGACY_CLASS_ALIASES: Dict[str, str] = {"_client_new": "EgeriaTech"}

_FIND_STAGE = "producer/find"
_ANALYTIC_STAGE = "producer/analytic"
_STAGE_KINDS_RUNNABLE = (_FIND_STAGE, _ANALYTIC_STAGE)


class MicroflowError(ValueError):
    """The microflow text is not valid JSON, not a known format, or does not match the model."""


class CannotRunYet(ValueError):
    """A valid microflow/1 that this pyegeria cannot run yet (stage 1 runs one find and/or one
    registered analytic). The message starts "uses stages this pyegeria cannot run yet: "."""

    def __init__(self, detail: str):
        super().__init__(f"uses stages this pyegeria cannot run yet: {detail}")


class AllowlistRefusal(ValueError):
    """A stage names something an Egeria-held spec may not name (§7a "Safety")."""


# ── The model ──

class ParamDecl(BaseModel):
    """One spec-level parameter (§2b): its type, default and whether a caller must supply it."""
    model_config = ConfigDict(extra="forbid")
    type: str = "string"
    default: Any = None
    required: bool = False
    category: Optional[str] = None


class Stage(BaseModel):
    """One stage of the micro-flow. `params` binds the stage's arguments: a value "$name" is the
    spec parameter `name`, anything else is a constant."""
    model_config = ConfigDict(extra="allow")
    stage: str
    type: Optional[str] = None
    function: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)
    out: Optional[str] = None

    @field_validator("stage")
    @classmethod
    def _stage_kind(cls, v: str) -> str:
        if not isinstance(v, str) or "/" not in v:
            raise ValueError(f"stage kind {v!r} is not '<kind>/<name>' (for example 'producer/find')")
        return v


ColumnItem = Union[str, Dict[str, Any]]


class Formatter(BaseModel):
    """One output format's formatter: `columns` (a list of field keys or column objects, or "*"
    for every field of the shape), or one `field` (for example MERMAID's `mermaidGraph`), or
    `same_as`: the name of an earlier output format whose formatter this one shares (stage 2). A
    spec that renders several output formats with one column list (a `Format` with several `types`)
    writes the list once, under its first type, and `{"same_as": "<that type>"}` for the others, so
    the list is not repeated and the converted `FormatSet` groups them as one `Format` again."""
    model_config = ConfigDict(extra="allow")
    columns: Optional[Union[Literal["*"], List[ColumnItem]]] = None
    field: Optional[str] = None
    label: Optional[str] = None
    same_as: Optional[str] = None
    #: A DOCUMENT formatter's document block (SD-1): standard, media_type, file_name, validator,
    #: validator_options. Carried as written; the FormatSet model checks it.
    document: Optional[Dict[str, Any]] = None

    @model_validator(mode="after")
    def _one_of(self):
        if self.same_as is not None:
            if self.columns is not None or self.field is not None:
                raise ValueError("a formatter with 'same_as' carries no 'columns' or 'field' of its own")
            return self
        if self.columns is None and self.field is None:
            raise ValueError("a formatter needs 'columns', 'field' or 'same_as'")
        if isinstance(self.columns, list):
            for item in self.columns:
                if isinstance(item, dict) and not isinstance(item.get("field"), str):
                    raise ValueError(f"column object {item!r} needs a string 'field'")
                if not isinstance(item, (str, dict)):
                    raise ValueError(f"column {item!r} is neither a field key nor a column object")
        return self


class MicroflowV1(BaseModel):
    """The canonical stored micro-flow (§7a "Representation", §10.1)."""
    model_config = ConfigDict(extra="forbid")
    format: Literal["microflow/1"] = MICROFLOW_FORMAT
    params: Dict[str, ParamDecl] = Field(default_factory=dict)
    stages: List[Stage]
    formatters: Dict[str, Formatter] = Field(default_factory=dict)

    @field_validator("formatters")
    @classmethod
    def _upper_keys(cls, v):
        return {str(k).upper(): f for k, f in v.items()}

    @model_validator(mode="after")
    def _stages_or_format_only(self):
        """At least one stage, except for a format-only spec (owner decision S2-1, 2026-11-09): a
        spec with no action, which other specs name as a `detail_spec` or render with data they
        already hold. It has `"stages": []`, no `params`, and at least one formatter."""
        if not self.stages:
            if self.params:
                raise ValueError("a micro-flow with no stages (a format-only spec) declares no params")
            if not self.formatters:
                raise ValueError("a micro-flow needs at least one stage, or (a format-only spec) at least one "
                                 "formatter")
        return self

    @model_validator(mode="after")
    def _same_as_targets(self):
        """`same_as` names an output format written earlier in `formatters` that has columns or a
        field of its own (never another `same_as`)."""
        seen: Dict[str, Formatter] = {}
        for out_type, f in self.formatters.items():
            if f.same_as is not None:
                target = seen.get(str(f.same_as).upper())
                if target is None:
                    raise ValueError(f"formatter {out_type} is same_as '{f.same_as}', which is not an output "
                                     f"format written before it")
                if target.same_as is not None:
                    raise ValueError(f"formatter {out_type} is same_as '{f.same_as}', which is itself a "
                                     f"same_as; name the formatter that holds the columns")
            seen[out_type] = f
        return self

    def to_json(self) -> str:
        return json.dumps(self.model_dump(mode="json", exclude_none=True), ensure_ascii=False)


# ── Parsing: one entry point for both formats ──

def microflow_from_legacy(stages: list, *, notes: Optional[List[str]] = None) -> MicroflowV1:
    """Convert a format-0 micro-flow (a bare list of stages) into `microflow/1`.

    - Each stage's `required_params` / `optional_params` become spec `params` (`required`
      true/false). Format 0 has no types, so every parameter is typed "string" (noted).
    - Each stage's `columns` become `formatters.ALL.columns` (format 0 has one column list, which
      the executor uses for every output format that falls back to ALL).
    - A stage with no `stage` kind is a find (`producer/find`): the early Dr.Egeria examples
      wrote `[{"function": ..., "params": ...}]` (noted).
    - Every other stage key maps one to one.

    `notes`, when given, collects the sentences describing what was assumed.
    """
    if not isinstance(stages, list):
        raise MicroflowError(f"a format-0 micro-flow is a JSON list of stages, not {type(stages).__name__}")
    if not stages:
        raise MicroflowError("a format-0 micro-flow needs at least one stage")
    notes = notes if notes is not None else []
    params: Dict[str, Dict[str, Any]] = {}
    new_stages: List[Dict[str, Any]] = []
    columns: Optional[list] = None
    for i, raw in enumerate(stages):
        if not isinstance(raw, dict):
            raise MicroflowError(f"format-0 stage {i} is not a JSON object")
        stage = dict(raw)
        if "stage" not in stage:
            stage["stage"] = _FIND_STAGE
            notes.append(f"format-0 stage {i} names no stage kind; read as {_FIND_STAGE}")
        for name in stage.pop("required_params", None) or []:
            params.setdefault(name, {"type": "string", "required": True})
            params[name]["required"] = True
        for name in stage.pop("optional_params", None) or []:
            params.setdefault(name, {"type": "string", "required": False})
        stage_cols = stage.pop("columns", None)
        if stage_cols is not None:
            if columns is not None and stage_cols != columns:
                raise MicroflowError("format-0 stages carry two different column lists; microflow/1 has one per "
                                     "output format, so this cannot be converted without a choice")
            columns = stage_cols
        new_stages.append(stage)
    if params:
        notes.append(f"format 0 carries no parameter types: {len(params)} parameter(s) typed 'string'")
    obj: Dict[str, Any] = {"format": MICROFLOW_FORMAT, "params": params, "stages": new_stages, "formatters": {}}
    if columns is not None:
        obj["formatters"]["ALL"] = {"columns": columns}
    try:
        return MicroflowV1.model_validate(obj)
    except ValidationError as exc:
        raise MicroflowError(f"the format-0 micro-flow does not convert to microflow/1: {_first_error(exc)}") from exc


def parse_microflow(text: Union[str, list, dict, None]) -> Tuple[MicroflowV1, int, List[str]]:
    """Parse a stored `microflow` value. Returns `(model, stored_format, notes)` where
    `stored_format` is 0 (a bare list, converted) or 1. Raises `MicroflowError` with words for
    invalid JSON, an unknown `format`, or a value that does not match the model."""
    notes: List[str] = []
    if text is None or (isinstance(text, str) and not text.strip()):
        raise MicroflowError("the spec has no microflow")
    if isinstance(text, str):
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise MicroflowError(f"the microflow is not valid JSON: {exc}") from exc
    else:
        data = text
    if isinstance(data, list):
        return microflow_from_legacy(data, notes=notes), 0, notes
    if isinstance(data, dict):
        fmt = data.get("format")
        if fmt != MICROFLOW_FORMAT:
            raise MicroflowError(f"unknown microflow format {fmt!r} (this pyegeria reads '{MICROFLOW_FORMAT}' "
                                 f"and a bare list, format 0)")
        try:
            return MicroflowV1.model_validate(data), 1, notes
        except ValidationError as exc:
            raise MicroflowError(f"the microflow/1 object is not valid: {_first_error(exc)}") from exc
    raise MicroflowError(f"the microflow is a JSON {type(data).__name__}, not a microflow/1 object or a list")


def _first_error(exc: ValidationError) -> str:
    errs = exc.errors()
    if not errs:
        return str(exc)
    e = errs[0]
    where = ".".join(str(p) for p in e.get("loc", ())) or "(top)"
    more = f" (and {len(errs) - 1} more)" if len(errs) > 1 else ""
    return f"{where}: {e.get('msg')}{more}"


def normalize_microflow_text(value: Union[str, list, dict, None]) -> str:
    """The canonical `microflow/1` JSON text for a Microflow value an author wrote (Dr.Egeria
    `Create/Update Report Spec`, §7a "Representation"): a bare list (format 0) is converted with
    `microflow_from_legacy`; a `microflow/1` object is validated against the model. Raises
    `MicroflowError` with words for invalid JSON or an invalid micro-flow."""
    mf, _stored, _notes = parse_microflow(value)
    return mf.to_json()


# ── The allowlist (§7a "Safety") ──

def _allowed_class_names() -> Dict[str, type]:
    from pyegeria.view.spec_resolver import _egeria_tech_classes
    return {c.__name__: c for c in _egeria_tech_classes()}


def find_method_allowed(func_decl: Any) -> Tuple[bool, str]:
    """Whether an Egeria-held spec may name `func_decl` as its find method, and the words why not.

    Allowed: `Class.method` (exactly one dot) where `Class` is an EgeriaTech client class (or a
    name the executor maps to one, `_CLIENT_CLASS_MAP` / `LEGACY_CLASS_ALIASES`), `Class.method`
    (or the method's `_async_` twin) is on `FIND_METHOD_ALLOWLIST`, it is not on
    `FIND_METHOD_DENYLIST` (on any class), and the method exists there."""
    from pyegeria.view.format_set_executor import _CLIENT_CLASS_MAP
    from pyegeria.view.spec_resolver import _find_method

    if not isinstance(func_decl, str) or not func_decl:
        return False, f"its find method {func_decl!r} is not a Class.method name"
    parts = func_decl.split(".")
    if len(parts) != 2 or not all(parts):
        return False, (f"its find method '{func_decl}' is not Class.method (a dotted module path is never "
                       f"allowed in a spec held in Egeria)")
    class_name, method_name = parts
    bare = method_name[len("_async_"):] if method_name.startswith("_async_") else method_name
    classes = _allowed_class_names()
    mapped = _CLIENT_CLASS_MAP.get(class_name)
    if class_name in classes:
        pass
    elif class_name in LEGACY_CLASS_ALIASES:
        pass
    elif isinstance(mapped, str) and mapped.rsplit(".", 1)[-1] in classes:
        pass
    else:
        return False, f"its find method's class '{class_name}' is not an EgeriaTech client class"
    if (func_decl in FIND_METHOD_DENYLIST or f"{class_name}.{bare}" in FIND_METHOD_DENYLIST
            or bare in _DENIED_METHOD_NAMES):
        return False, f"its find method '{func_decl}' is on the denylist"
    if f"{class_name}.{bare}" not in FIND_METHOD_ALLOWLIST:
        return False, (f"its find method '{func_decl}' is not on the allowlist of find methods a spec held in "
                       f"Egeria may name (FIND_METHOD_ALLOWLIST: the methods today's built-in specs name, "
                       f"plus reviewed additions)")
    method, why = _find_method(f"{class_name}.{bare}")
    if method is None:
        return False, why
    return True, ""


def _analytic_allowed(name: Any) -> Tuple[bool, str]:
    from pyegeria.view.analytic_registry import get_analytic_registry
    if not isinstance(name, str) or not name:
        return False, f"its analytic {name!r} is not a registered analytic name"
    if "." in name:
        return False, (f"its analytic '{name}' is a dotted path; a spec held in Egeria names a registered "
                       f"analytic only, never a module path")
    if name not in get_analytic_registry():
        return False, f"its analytic '{name}' is not a registered analytic"
    return True, ""


def additional_props_allowed(stage: Stage, name: Any) -> Tuple[bool, str]:
    """Whether a stage may carry `additional_props` naming `name`: only a find stage, and only a
    name on `ADDITIONAL_PROPS_HOOKS`."""
    if stage.stage != _FIND_STAGE:
        return False, (f"'additional_props' belongs on the find stage ({_FIND_STAGE}), not on a "
                       f"{stage.stage} stage")
    if not isinstance(name, str) or name not in ADDITIONAL_PROPS_HOOKS:
        return False, (f"its additional_props hook {name!r} is not on ADDITIONAL_PROPS_HOOKS (the client "
                       f"functions today's built-in specs name: {', '.join(sorted(ADDITIONAL_PROPS_HOOKS))})")
    return True, ""


def check_allowlist(mf: MicroflowV1) -> None:
    """Raise `AllowlistRefusal` naming the first stage that names something an Egeria-held spec
    may not name. Never imports or calls anything a stage names."""
    for i, stage in enumerate(mf.stages):
        extra = stage.model_extra or {}
        if "python" in extra or "binding" in extra or "module" in extra:
            raise AllowlistRefusal(f"stage {i} ({stage.stage}) carries a python binding; a spec held in Egeria "
                                   f"may never name one")
        if "additional_props" in extra:
            ok, why = additional_props_allowed(stage, extra["additional_props"])
            if not ok:
                raise AllowlistRefusal(f"stage {i}: {why}")
        if stage.stage == _FIND_STAGE:
            if stage.function is not None:
                ok, why = find_method_allowed(stage.function)
                if not ok:
                    raise AllowlistRefusal(f"stage {i}: {why}")
        elif stage.stage == _ANALYTIC_STAGE:
            ok, why = _analytic_allowed(stage.function)
            if not ok:
                raise AllowlistRefusal(f"stage {i}: {why}")
        elif stage.function is not None and "." in str(stage.function):
            raise AllowlistRefusal(f"stage {i} ({stage.stage}) names '{stage.function}', a dotted path; a spec "
                                   f"held in Egeria names registered functions only")


# ── Columns: a key, or an object ──

def _column_catalog() -> Dict[str, Dict[str, Any]]:
    """key -> {name, format} for a bare field key, until shapes are registered (§5).

    The common columns come first (they are what format 0's ALL lists hold); every other key takes
    the name and format the built-in specs most often give it."""
    global _CATALOG
    if _CATALOG is not None:
        return _CATALOG
    from pyegeria.view import base_report_formats as brf
    catalog: Dict[str, Dict[str, Any]] = {}
    for col in brf.COMMON_COLUMNS:
        catalog[col.key] = {"name": col.name, "format": col.format}
    seen: Dict[str, Counter] = {}
    for fs in list(brf.base_report_specs.values()) + list(brf.generated_format_sets.values()):
        for fmt in fs.formats or []:
            for col in getattr(fmt, "attributes", []) or []:
                key = getattr(col, "key", None)
                if key and key not in catalog:
                    seen.setdefault(key, Counter())[(col.name, col.format)] += 1
    for key, counts in seen.items():
        (name, fmt), _ = counts.most_common(1)[0]
        catalog[key] = {"name": name, "format": fmt}
    _CATALOG = catalog
    return catalog


_CATALOG: Optional[Dict[str, Dict[str, Any]]] = None


def _title(key: str) -> str:
    words = key.replace("-", "_").split("_")
    return " ".join(w[:1].upper() + w[1:] for w in words if w) or key


#: The column-item key that carries `Column.label` (qualified_name / display_name). A column item's own
#: "label" is the column's title, so the related-element label has its own key (R2).
RELATED_LABEL_KEY = "related_label"


def _to_column(item: ColumnItem, cache: Optional[Dict[Any, Any]] = None):
    """The `Column` for a formatter's column item. With `cache` (the seed loader passes one for the whole
    seed), an identical item yields the one shared `Column`, as the Python constants share theirs: 15,475
    columns in the 437 shipped specs are 642 distinct ones. Nothing changes a Column after it is built."""
    if cache is not None:
        key = item if isinstance(item, str) else (item.get("field"), item.get("label"), item.get("format"),
                                                  item.get("detail_spec"), repr(item.get("valid_values")),
                                                  item.get("render"), item.get("max_items"), item.get("max_lines"),
                                                  item.get(RELATED_LABEL_KEY))
        col = cache.get(key)
        if col is None:
            col = cache[key] = _to_column(item)
        return col
    from pyegeria.view._output_format_models import Column
    if isinstance(item, str):
        known = _column_catalog().get(item)
        if known:
            return Column(name=known["name"], key=item, format=known["format"])
        return Column(name=_title(item), key=item)
    data: Dict[str, Any] = {"key": item["field"], "name": item.get("label") or
                            _column_catalog().get(item["field"], {}).get("name") or _title(item["field"])}
    for k in ("format", "detail_spec", "valid_values", "render", "max_items", "max_lines"):
        if k in item and item[k] is not None:
            data[k] = item[k]
    if item.get(RELATED_LABEL_KEY) is not None:  # Column.label; "label" is the column's title here
        data["label"] = item[RELATED_LABEL_KEY]
    return Column(**data)


# ── microflow/1 -> FormatSet (what stage 1 runs) ──

def _bind(stage: Stage, params: Dict[str, ParamDecl]) -> Dict[str, Any]:
    """The stage's constant arguments (spec_params). A "$name" binding must name a declared spec
    parameter of the same name: the executor passes parameters by name."""
    constants: Dict[str, Any] = {}
    for arg, value in (stage.params or {}).items():
        if isinstance(value, str) and value.startswith("$"):
            ref = value[1:]
            if ref != arg:
                raise CannotRunYet(f"stage {stage.stage} binds '{arg}' to '${ref}', a renamed parameter")
            if ref not in params:
                raise MicroflowError(f"stage {stage.stage} binds '{arg}' to '${ref}', which the spec does not "
                                     f"declare in params")
        else:
            constants[arg] = value
    return constants


def microflow_to_format_set(mf: MicroflowV1, *, label: str, heading: Optional[str] = None,
                            description: str = "", target_type: Optional[str] = None,
                            aliases: Optional[List[str]] = None, family: Optional[str] = None,
                            annotations: Optional[Dict[str, List[str]]] = None,
                            question_spec: Optional[List[Any]] = None,
                            notes: Optional[List[str]] = None,
                            column_cache: Optional[Dict[Any, Any]] = None):
    """Convert a `microflow/1` into today's `FormatSet`. A pure function: it imports nothing a
    stage names. Raises `CannotRunYet` for stages stage 1 cannot run, `MicroflowError` for an
    inconsistent micro-flow.

    A micro-flow with no stages is a format-only spec (S2-1): its `FormatSet` has no action. A find
    stage's `additional_props` becomes `FormatSet.get_additional_props` (only a name on
    `ADDITIONAL_PROPS_HOOKS`). Formatters joined by `same_as` become one `Format` with several types."""
    from pyegeria.view._output_format_models import ActionParameter, Format, FormatSet

    notes = notes if notes is not None else []
    stages = list(mf.stages)
    kinds = [s.stage for s in stages]
    binders: Dict[str, Any] = {}
    hook: Optional[str] = None
    for i, s in enumerate(stages):
        extra = dict(s.model_extra or {})
        if "additional_props" in extra:
            name = extra.pop("additional_props")
            ok, why = additional_props_allowed(s, name)
            if not ok:
                raise MicroflowError(f"stage {i}: {why}")
            hook = name
        # A stage's `analytic_binders` (removed in RS-W2-3 PR-B) is passed on to the action, so the
        # ActionParameter shim drops it there and records the names, and the spec resolver warns
        # with BINDERS_DEPRECATED_PREFIX (owner decision O1-a): exactly as for a local spec. An
        # empty one is dropped silently, as the shim does.
        stage_binders = extra.pop("analytic_binders", None)
        if stage_binders:
            if isinstance(stage_binders, dict):
                binders.update(stage_binders)
            else:
                binders[repr(stage_binders)] = stage_binders
        unknown = sorted(extra.keys())
        if unknown:
            notes.append(f"stage {i} ({s.stage}) carries key(s) this pyegeria does not read: "
                         f"{', '.join(unknown)}; ignored")
    unsupported = [k for k in kinds if k not in _STAGE_KINDS_RUNNABLE]
    if unsupported:
        raise CannotRunYet(", ".join(sorted(set(unsupported))))
    finds = [s for s in stages if s.stage == _FIND_STAGE]
    analytics = [s for s in stages if s.stage == _ANALYTIC_STAGE]
    if len(finds) > 1:
        raise CannotRunYet(f"{len(finds)} find producers")
    if len(analytics) > 1:
        raise CannotRunYet(f"{len(analytics)} analytic producers")
    if finds and analytics and kinds.index(_FIND_STAGE) > kinds.index(_ANALYTIC_STAGE):
        raise CannotRunYet("an analytic stage before the find stage")

    required = [n for n, p in mf.params.items() if p.required]
    optional = [n for n, p in mf.params.items() if not p.required]
    if any(p.default is not None for p in mf.params.values()):
        notes.append("parameter defaults are recorded but not applied in stage 1 (the find method's own "
                     "defaults apply)")
    action: Dict[str, Any] = {}
    if finds:
        find = finds[0]
        if not find.function:
            raise CannotRunYet(f"a find stage for type {find.type!r} with no function (type-implied find methods "
                               f"come with the shape registry)")
        action.update(function=find.function, required_params=required, optional_params=optional,
                      spec_params=_bind(find, mf.params))
        if find.out:
            notes.append(f"out shape '{find.out}' is not registered (shapes are not registered in stage 1); "
                         f"recorded, not checked")
    if analytics:
        an = analytics[0]
        if not an.function:
            raise MicroflowError("the analytic stage names no function")
        action["analytic_function"] = an.function
        action["analytic_spec_params"] = {k: v for k, v in (an.params or {}).items()
                                          if not (isinstance(v, str) and v.startswith("$"))}
        if not finds:
            action.update(required_params=required, optional_params=optional)

    if binders and action:
        action["analytic_binders"] = binders

    formats = []
    by_type: Dict[str, Any] = {}
    for out_type, f in mf.formatters.items():
        if f.same_as is not None:
            fmt = by_type[str(f.same_as).upper()]
            fmt.types.append(out_type)
            by_type[out_type] = fmt
            continue
        if f.columns == "*":
            raise CannotRunYet(f"formatter {out_type} uses columns '*', which needs a registered shape")
        if f.columns is not None:
            cols = [_to_column(c, column_cache) for c in f.columns]
        else:
            cols = [_to_column({"field": f.field, "label": f.label} if f.label else f.field, column_cache)]
        fmt = Format(types=[out_type], attributes=cols, document=f.document)
        formats.append(fmt)
        by_type[out_type] = fmt
    if not formats:
        raise MicroflowError("the micro-flow has no formatters, so no output format can be rendered")

    return FormatSet(target_type=target_type, heading=heading or label, description=description or "",
                     aliases=list(aliases or []), family=family, formats=formats,
                     annotations=dict(annotations or {}),
                     action=ActionParameter(**action) if action else None,
                     get_additional_props=ActionParameter(function=hook) if hook else None,
                     question_spec=question_spec)


# ── FormatSet -> microflow/1 (used to write the canonical text; W3, Dr.Egeria tests) ──

def format_set_to_microflow(fs) -> MicroflowV1:
    """The `microflow/1` that converts back to the same `FormatSet` action and formats. Every
    column is written as an object carrying its label (and format/detail_spec when set), so the
    round trip does not depend on the column catalog.

    - A spec with no action (format-only) is written with `"stages": []` (S2-1).
    - `get_additional_props` is written as the find stage's `additional_props` (only a bare function
      name on `ADDITIONAL_PROPS_HOOKS`; anything else raises, so nothing is dropped silently).
    - A `Format` with several types is written once, under its first type, and `same_as` for the rest.
    - An output type that two `Format`s both list raises: the executor uses the first, and writing
      only that one would drop the second without a word."""
    action = fs.action
    action = action if isinstance(action, dict) or action is None else action.model_dump()
    hook = getattr(fs, "get_additional_props", None)
    hook = hook if isinstance(hook, dict) or hook is None else hook.model_dump()
    hook_name: Optional[str] = None
    if hook:
        hook_name = hook.get("function")
        rest = {k: v for k, v in hook.items() if k != "function" and v not in (None, [], {})}
        if rest or not isinstance(hook_name, str) or hook_name not in ADDITIONAL_PROPS_HOOKS:
            raise MicroflowError(f"get_additional_props {hook!r} is not a bare function on ADDITIONAL_PROPS_HOOKS, "
                                 f"so microflow/1 cannot carry it")
        if not (action and action.get("function")):
            raise MicroflowError("get_additional_props needs a find stage to carry it, and the spec has none")
    if not action:
        return MicroflowV1.model_validate({"format": MICROFLOW_FORMAT, "params": {}, "stages": [],
                                          "formatters": _formatters_of(fs)})
    params: Dict[str, Dict[str, Any]] = {}
    for n in action.get("required_params") or []:
        params[n] = {"type": "string", "required": True}
    for n in action.get("optional_params") or []:
        params.setdefault(n, {"type": "string", "required": False})
    stages: List[Dict[str, Any]] = []
    if action.get("function"):
        bind = {n: f"${n}" for n in action.get("required_params") or []}
        bind.update(action.get("spec_params") or {})
        stage = {"stage": _FIND_STAGE, "function": action["function"], "params": bind}
        if fs.target_type:
            stage["type"] = fs.target_type
        if hook_name:
            stage["additional_props"] = hook_name
        stages.append(stage)
    if action.get("analytic_function"):
        stages.append({"stage": _ANALYTIC_STAGE, "function": action["analytic_function"],
                       "params": dict(action.get("analytic_spec_params") or {})})
    return MicroflowV1.model_validate({"format": MICROFLOW_FORMAT, "params": params, "stages": stages,
                                      "formatters": _formatters_of(fs)})


def _formatters_of(fs) -> Dict[str, Dict[str, Any]]:
    formatters: Dict[str, Dict[str, Any]] = {}
    for fmt in fs.formats or []:
        fmt = fmt if isinstance(fmt, dict) else fmt.model_dump()
        cols = []
        for c in fmt["attributes"]:
            c = c if isinstance(c, dict) else c.model_dump()
            if c.get("value") is not None:
                raise MicroflowError(f"column '{c['key']}' carries a constant value, which microflow/1 cannot carry")
            item: Dict[str, Any] = {"field": c["key"], "label": c["name"]}
            if c.get("format"):
                item["format"] = c["format"]
            if c.get("detail_spec"):
                item["detail_spec"] = c["detail_spec"]
            if c.get("valid_values"):
                item["valid_values"] = c["valid_values"]
            for k in ("render", "max_items", "max_lines"):  # R2: carried, or Egeria-held specs lose them
                if c.get(k) is not None:
                    item[k] = c[k]
            if c.get("label") is not None:
                item[RELATED_LABEL_KEY] = c["label"]
            cols.append(item)
        first: Optional[str] = None
        for t in fmt["types"]:
            key = t.upper()
            if key in formatters:
                raise MicroflowError(f"output type {key} is listed by two formats; microflow/1 holds one formatter "
                                     f"per output type")
            formatters[key] = {"columns": cols} if first is None else {"same_as": first}
            if first is None and fmt.get("document"):
                formatters[key]["document"] = {k: v for k, v in fmt["document"].items() if v not in (None, {}, [])}
            first = first or key
    return formatters
