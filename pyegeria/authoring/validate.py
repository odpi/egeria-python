# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""validate(draft): structural, semantic, then Dr.Egeria's own validate. Never raises for a bad draft.

- **Structural:** the draft's model, and whether it serializes safely (no line break, rule or heading
  where Dr.Egeria would read a new block).
- **Semantic:**
  - spec: the target type exists in Egeria's type system (pyegeria's Properties-class catalog); every
    column of a find spec names an attribute of that type, or a key pyegeria's own specs use; the spec
    passes pyegeria's load-time resolution (the find method or analytic routine is registered and
    allowed, its parameters are ones it accepts, chart formats have a routine, detail specs exist);
  - report: its spec resolves (pyegeria's registry, else Egeria as the caller); the output format is one
    the spec produces; every parameter is one the spec declares (or a common find parameter) and has the
    right type; a pinned version is refused (D14);
  - sheet: every report placement names a Report Egeria holds for this user, and that Report's spec
    resolves; detail specs resolve; placement names are unique.
- **Dr.Egeria validate** of the serialized document, through the caller's runner, when one is given.

What could not be checked (no client, no runner, an unknown parameter type) is listed in `not_checked`,
so an empty `errors` is never read as "checked and fine" when it wasn't.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Set

from loguru import logger
from pydantic import ValidationError

from pyegeria.authoring.models import (
    AuthoringGates, AuthoringRefused, ReportDraft, SheetDraft, SpecDraft, ValidationResult, as_draft, default_gates,
)
from pyegeria.authoring.serialize import FIND_PARAMETERS, serialize

#: Column keys the formatter derives from an element's header or relationships, not a property of the type.
DERIVED_KEYS = {"guid", "type_name", "classifications", "created_by", "create_time", "updated_by", "update_time",
                "version", "status", "anchor", "mermaid", "related", "members", "member_of", "properties"}


def _snake(camel: str) -> str:
    out = []
    for ch in camel:
        out.append("_" + ch.lower() if ch.isupper() else ch)
    return "".join(out).lstrip("_")


def type_attributes(type_name: str) -> Optional[Set[str]]:
    """The snake_case property names of an Egeria type (inherited included), from pyegeria's generated
    Properties-class catalog; None if the catalog has no such type."""
    from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS
    entry = PROPERTIES_CLASS_FIELDS.get(f"{type_name}Properties")
    if not entry or entry[0] != "entity":
        return None
    return {_snake(f) for f in entry[1]}


def _registry_columns_and_types() -> tuple:
    """(every column key pyegeria's registered specs use, every target type they name). Read only."""
    from pyegeria.view.base_report_formats import get_report_registry
    keys: Set[str] = set()
    types: Set[str] = set()
    for fs in get_report_registry().values():
        if getattr(fs, "target_type", None):
            types.add(fs.target_type)
        for fmt in fs.formats or []:
            for col in getattr(fmt, "attributes", None) or []:
                key = col.get("key") if isinstance(col, dict) else getattr(col, "key", None)
                if key:
                    keys.add(key)
    return keys, types


def _check_spec(draft: SpecDraft, result: ValidationResult) -> None:
    from pyegeria.view.spec_resolver import Unrunnable, resolve
    fs = draft.format_set
    used_keys, used_types = _registry_columns_and_types()
    target = fs.target_type
    attrs = type_attributes(target) if target else None
    if target:
        if attrs is None and target not in used_types:
            result.error(f"Target type '{target}' isn't a type in Egeria's type system (no {target}Properties) "
                         f"and no pyegeria spec uses it.")
        result.checked.append("target type")
    action = fs.action
    is_find = bool(getattr(action, "function", None)) and not getattr(action, "analytic_function", None)
    if is_find and attrs is not None:
        known = attrs | DERIVED_KEYS | used_keys
        for fmt in fs.formats or []:
            for col in getattr(fmt, "attributes", None) or []:
                key = col.get("key") if isinstance(col, dict) else col.key
                name = col.get("name") if isinstance(col, dict) else col.name
                if key and key not in known:
                    result.error(f"Column '{name}' names '{key}', which isn't an attribute of {target} "
                                 f"(nor a key pyegeria's formatter derives).")
        result.checked.append("column attributes")
    elif is_find:
        result.not_checked.append(f"column attributes: no attribute catalog for target type {target!r}")
    else:
        result.not_checked.append("column attributes: an analytic spec's columns are checked against its "
                                  "routine's declared fields by load-time resolution")
    resolution = resolve(fs, draft.label)
    result.checked.append("load-time resolution (find method / analytic routine, parameters, formats)")
    if isinstance(resolution, Unrunnable):
        for words in resolution.words:
            result.error(words)
    for w in getattr(resolution, "warnings", None) or []:
        result.warn(w)


_TYPE_CHECKS = {
    "str": lambda v: isinstance(v, str),
    "int": lambda v: (isinstance(v, int) and not isinstance(v, bool)) or (isinstance(v, str) and v.strip().lstrip("-").isdigit()),
    "bool": lambda v: isinstance(v, bool) or (isinstance(v, str) and v.strip().lower() in ("true", "false")),
    "dict": lambda v: isinstance(v, dict),
}
_FIND_TYPES = {"text": "str", "bool": "bool", "int": "int", "list": "list", "jsonlist": "list"}


def _type_ok(declared: str, value: Any) -> Optional[bool]:
    """True/False, or None when the declared type isn't one checked here."""
    declared = (declared or "").strip()
    if declared.startswith("list"):
        return isinstance(value, (list, tuple))
    check = _TYPE_CHECKS.get(declared)
    return None if check is None else check(value)


async def _spec_for(label: str, client: Any, result: ValidationResult):
    """The FormatSet a Report's spec label names: pyegeria's registry, else Egeria read as the caller."""
    from pyegeria.view.base_report_formats import lookup_report_spec
    fs = lookup_report_spec(label)[0]
    if fs is not None:
        return fs
    if client is None:
        result.not_checked.append(f"spec {label!r}: not in pyegeria's registry, and no client to read Egeria")
        return None
    from pyegeria.authoring.lifecycle import async_load_held
    try:
        return (await async_load_held("spec", label, client)).format_set
    except AuthoringRefused as exc:
        result.error(f"The Report's spec doesn't resolve: {exc}")
        return None


async def _check_report(draft: ReportDraft, client: Any, result: ValidationResult, gates: AuthoringGates) -> None:
    from pyegeria.view.spec_resolver import CHART_FORMATS, routine_entry
    if draft.pinned_version is not None and not gates.allow_pinning:
        from pyegeria.authoring.lifecycle import PIN_REFUSED
        result.error(PIN_REFUSED)
    if draft.pinned_version is not None and gates.allow_pinning:
        from pyegeria.authoring.versions import async_spec_at_version
        if client is None:
            result.not_checked.append(f"pinned version {draft.pinned_version} of {draft.spec!r}: no client to "
                                      f"read the spec's versions from Egeria")
            fs = await _spec_for(draft.spec, None, result)
        else:
            try:
                fs = await async_spec_at_version(client, draft.spec, draft.pinned_version)
                result.checked.append(f"pinned version {draft.pinned_version} exists")
            except AuthoringRefused as exc:
                result.error(str(exc))
                return
    else:
        fs = await _spec_for(draft.spec, client, result)
    if fs is None:
        if not any(draft.spec in e for e in result.errors) and not any(draft.spec in n for n in result.not_checked):
            result.error(f"The Report's spec {draft.spec!r} doesn't resolve.")
        return
    result.checked.append("spec resolves")
    action = fs.action
    analytic = getattr(action, "analytic_function", None)
    produced = {t.upper() for fmt in fs.formats or [] for t in (getattr(fmt, "types", None) or [])}
    out = draft.output_format.upper()
    if analytic and out in CHART_FORMATS:
        pass
    elif produced and out not in produced and "ALL" not in produced and not (out == "TABLE" and "DICT" in produced):
        result.error(f"Output format {out} isn't one spec {draft.spec!r} produces ({', '.join(sorted(produced))}).")
    result.checked.append("output format")

    declared: Dict[str, Optional[str]] = {name: _FIND_TYPES[style] for name, (_, style) in FIND_PARAMETERS.items()}
    for name in (getattr(action, "required_params", None) or []) + (getattr(action, "optional_params", None) or []):
        declared.setdefault(name, None)
    routine_types: Dict[str, str] = {}
    if analytic:
        entry = routine_entry(analytic)
        for p in (getattr(entry, "params", None) or []):
            routine_types[p.name] = p.type
    for name, value in sorted(draft.parameters.items()):
        if name not in declared and name not in routine_types:
            result.error(f"'{name}' isn't a parameter of spec {draft.spec!r} (it declares "
                         f"{', '.join(sorted(set(declared) - set(FIND_PARAMETERS))) or 'only the common find parameters'}).")
            continue
        kind = declared.get(name) or routine_types.get(name)
        if kind is None:
            result.not_checked.append(f"type of parameter '{name}': the spec declares no type for it")
            continue
        ok = _type_ok(kind, value)
        if ok is False:
            result.error(f"Parameter '{name}' should be {kind}, not {type(value).__name__} ({value!r}).")
    for name, value in sorted(draft.analytic_params.items()):
        if not analytic:
            result.error(f"Spec {draft.spec!r} has no analytic routine, so analytic parameter '{name}' does nothing.")
            continue
        if name not in routine_types:
            result.error(f"'{name}' isn't a parameter of routine {analytic!r} "
                         f"(it declares {', '.join(sorted(routine_types)) or 'none'}).")
            continue
        ok = _type_ok(routine_types[name], value)
        if ok is False:
            result.error(f"Analytic parameter '{name}' should be {routine_types[name]}, not "
                         f"{type(value).__name__} ({value!r}).")
        elif ok is None:
            result.not_checked.append(f"type of analytic parameter '{name}' ({routine_types[name]})")
    result.checked.append("parameters")


async def _check_sheet(draft: SheetDraft, client: Any, result: ValidationResult, gates: AuthoringGates) -> None:
    from pyegeria.view.base_report_formats import lookup_report_spec
    names = [p.name for p in draft.placements]
    dupes = sorted({n for n in names if names.count(n) > 1})
    if dupes:
        result.error(f"Placement names must be unique on a sheet: {', '.join(dupes)} appear more than once.")
    if draft.perspectives:
        result.not_applied.append("Sheet perspectives: Create Dashboard Sheet has no sheet-level perspectives; "
                                  "put them on placements")
    for i, p in enumerate(draft.placements, start=1):
        if p.text is not None and p.detail_spec:
            result.not_applied.append(f"Placement {i} ({p.name}): a text placement has no detail spec")
        if p.detail_spec and lookup_report_spec(p.detail_spec)[0] is None:
            result.warn(f"Placement {i} ({p.name}): detail spec {p.detail_spec!r} isn't in pyegeria's registry; "
                        f"the drill-down may not resolve.")
        if p.report is None:
            continue
        if client is None:
            result.not_checked.append(f"placement {i} ({p.report}): no client to read the Report from Egeria")
            continue
        from pyegeria.authoring.lifecycle import async_load_held
        try:
            report = await async_load_held("report", p.report, client)
        except AuthoringRefused as exc:
            result.error(f"Placement {i} names a Report that doesn't resolve: {exc}")
            continue
        if not report.spec:
            result.error(f"Placement {i}: Report {p.report!r} names no report spec.")
        elif await _spec_for(report.spec, client, ValidationResult()) is None:
            result.error(f"Placement {i}: Report {p.report!r} runs spec {report.spec!r}, which doesn't resolve.")
    result.checked.append("placements")


async def async_validate(draft: Any, client: Any = None, *, run: Any = None,
                         gates: Optional[AuthoringGates] = None) -> ValidationResult:
    result = ValidationResult()
    gates = gates or default_gates()
    try:
        draft = as_draft(draft)
    except ValidationError as exc:
        for e in exc.errors():
            result.error(f"{'.'.join(str(x) for x in e.get('loc', ()))}: {e.get('msg')}")
        return result
    result.checked.append("structure")
    try:
        markdown = serialize(draft)
    except AuthoringRefused as exc:
        result.error(str(exc))
        markdown = None
    try:
        if isinstance(draft, SpecDraft):
            _check_spec(draft, result)
        elif isinstance(draft, ReportDraft):
            await _check_report(draft, client, result, gates)
        else:
            await _check_sheet(draft, client, result, gates)
    except Exception as exc:  # noqa: BLE001 -- a failed check is reported, never raised
        logger.exception("authoring validate")
        result.error(f"Validation could not finish: {type(exc).__name__}: {' '.join(str(exc).split())[:300]}")
    if markdown is None:
        result.not_checked.append("Dr.Egeria validate: the draft didn't serialize")
    elif run is None:
        result.not_checked.append("Dr.Egeria validate: no runner given")
    else:
        from pyegeria.view.report_spec_publish import _call, summarise
        try:
            env = summarise(_call(run, markdown, "validate"))
        except Exception as exc:  # noqa: BLE001
            env = {"success": False, "execution_errors": [{"message": f"{type(exc).__name__}: {exc}"}]}
        result.dr_egeria = env
        result.checked.append("Dr.Egeria validate")
        if not env.get("success", False):
            for e in (env.get("validation_errors") or []) + (env.get("execution_errors") or []):
                result.error(f"Dr.Egeria: {e.get('message') if isinstance(e, dict) else e}")
            if not (env.get("validation_errors") or env.get("execution_errors")):
                result.error("Dr.Egeria validate did not succeed.")
    return result


def validate(draft: Any, client: Any = None, *, run: Any = None,
             gates: Optional[AuthoringGates] = None) -> ValidationResult:
    from pyegeria.core.async_runner import run_sync
    return run_sync(async_validate(draft, client, run=run, gates=gates))
