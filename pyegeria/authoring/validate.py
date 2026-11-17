# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""validate(draft): structural, semantic, then Dr.Egeria's own validate. Never raises for a bad draft.

- **Structural:** the draft's model, and whether it serializes safely (no line break, rule or heading
  where Dr.Egeria would read a new block).
- **Semantic:**
  - spec: the target type exists in Egeria's type system (pyegeria's Properties-class catalog); the find
    method returns the target type (FIND_ELEMENT_TYPES: a mismatch is refused, an unknown fit is a warning);
    every column of a find spec names an attribute of that type (its supertypes' included), a key the
    formatter derives (computed from the formatter), a documented related-element or annotation field, or, for a
    generated "-DrE-" spec, a Dr.Egeria command attribute; an unknown key is refused naming it (``legacy=True`` keeps the old loose check, which
    also accepted any key some pyegeria spec uses, for legacy specs, with a warning per such key); the spec
    passes pyegeria's load-time resolution (the find method or analytic routine is registered and
    allowed, its parameters are ones it accepts, chart formats have a routine, detail specs exist);
  - report: its spec resolves (pyegeria's registry, else Egeria as the caller); the output format is one
    the spec produces; every parameter is one the spec declares (or a common find parameter) and has the
    right type; a pinned version must exist (refused only when AuthoringGates.allow_pinning is off, D14),
    and `not_applied` says that dashboards don't honour the pin yet;
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


#: Fields the view service attaches to an element from its relationships, read by the formatter's step 3
#: (`element[camelCase(key)]`). No type definition lists them, so the attribute catalog can't. Each is used by
#: a shipped find spec.
RELATED_ELEMENT_KEYS = frozenset({
    "collection_members", "member_of_collections", "assigned_actors", "actor_list", "governed_by", "next_version",
    "solution_designs", "used_by_digital_products", "uses_digital_products", "agreement_items", "service_levels",
    "support_level", "folder_display_names", "as_of_data_field", "basis_data_field", "managed_projects",
    "project_roles", "resource_list", "report_type_instances", "note_log_name", "note_log_qualified_name",
    # The shipped 'Projects' spec reads start_date, which ProjectProperties doesn't have (it has
    # planned/actual start dates) and the view service doesn't attach, so it shows nothing today. Allowed so that
    # authoring doesn't refuse a copy of a shipped spec; the spec itself is to be fixed against live output.
    "start_date",
})

#: Properties of the survey annotation subtypes, which the Properties-class catalog doesn't list.
ANNOTATION_KEYS = frozenset({
    "report_name", "finding_type", "package_url", "installed_version", "fixed_version", "patch_available",
    "report_completion_time", "critical_findings", "high_findings", "medium_findings", "low_findings",
    "none_findings",
})

_GENERATED_MARK = "Auto-generated format for"


def _formatter_derived_keys() -> Set[str]:
    """Keys the output formatter fills from an element's header and referenceable properties
    (`_extract_referenceable_properties`: guid, origin, versions, type, classifications, status, zones, ...), plus
    the ones it handles by name (subject_area, mermaid). Computed from the formatter itself, so it can't drift."""
    from pyegeria.view.output_formatter import _extract_referenceable_properties
    probe = {"elementHeader": {"guid": "g", "origin": {}, "versions": {}, "type": {}}, "properties": {"qualifiedName": "q"}}
    return set(DERIVED_KEYS) | set(_extract_referenceable_properties(probe)) | {"subject_area", "mermaid"}


def _derived_by_rule(key: str) -> bool:
    """Keys the formatter fills by a rule rather than a list: GUID in any case, Mermaid graphs, chart columns."""
    from pyegeria.view.output_formatter import is_mermaid_graph_key
    return key.lower() == "guid" or is_mermaid_graph_key(key) or key.endswith(("BarGraph", "PieGraph"))


_COMMAND_ATTRIBUTE_KEYS: Optional[Set[str]] = None


def _command_attribute_keys() -> Set[str]:
    """The variable names of every attribute of every Dr.Egeria command, as the compact loader expands them
    (gen_report_specs reads the same). Generated "-DrE-" specs take their columns from a Create command's
    attributes, so those keys are valid for them."""
    global _COMMAND_ATTRIBUTE_KEYS
    if _COMMAND_ATTRIBUTE_KEYS is None:
        from pathlib import Path
        import md_processing
        from md_processing.md_processing_utils.compact_loader import load_compact_specs_from_dir
        keys: Set[str] = set()
        try:
            specs = load_compact_specs_from_dir(str(Path(md_processing.__file__).parent / "data" / "compact_commands"))
        except Exception:  # noqa: BLE001 -- no specs: no extra keys, so the strict check stays strict
            specs = {}
        for spec in specs.values():
            for entry in spec.get("Attributes") or []:
                if not isinstance(entry, dict):
                    continue
                for details in ([entry] if entry.get("variable_name") else entry.values()):
                    if isinstance(details, dict) and details.get("variable_name"):
                        keys.add(details["variable_name"])
        _COMMAND_ATTRIBUTE_KEYS = keys
    return _COMMAND_ATTRIBUTE_KEYS


def _is_generated(fs: Any, label: str) -> bool:
    return str(getattr(fs, "description", "") or "").startswith(_GENERATED_MARK) or "-DrE" in (label or "")


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


#: What each find method returns, as an Egeria type name; None = any element type. The fit check refuses a
#: spec whose target type isn't this type or one of its subtypes (prototype C06: target Asset + find_projects).
#: A method not listed is "unknown", which is a warning, never a pass. Keys are the spec's `action.function`.
FIND_ELEMENT_TYPES: Dict[str, Optional[str]] = {
    "ActorManager.find_actor_profiles": "ActorProfile",
    "ActorManager.find_actor_roles": "ActorRole",
    "ActorManager.find_perspectives": "Perspective",
    "ActorManager.find_skills": "Skill",
    "ActorManager.find_user_identities": "UserIdentity",
    "AssetMaker.find_assets": "Asset",
    "AssetCatalog.get_asset_graph_by_guid": "Asset",
    "ClassificationExplorer.find_elements_by_property_value": None,
    "ClassificationExplorer.get_elements": None,
    "CollectionManager.find_collections": "Collection",
    "CollectionManager.get_collection_members": None,
    "DataDesigner.find_data_fields": "DataField",
    "DataDesigner.find_data_structures": "DataStructure",
    "DataDesigner.find_data_value_specifications": "DataValueSpecification",
    "EgeriaTech.get_elements_by_property_value": None,
    "ExternalReference.find_external_references": "ExternalReference",
    "ExternalReferences.find_external_references": "ExternalReference",
    "GlossaryManager.find_glossaries": "Glossary",
    "GlossaryManager.find_glossary_terms": "GlossaryTerm",
    "GovernanceOfficer.find_governance_definitions": "GovernanceDefinition",
    "MetadataExpert.find_metadata_elements_with_string": None,
    "ProjectManager.find_projects": "Project",
    "ReferenceDataManager.find_valid_value_definitions": "ValidValueDefinition",
    "SecurityOfficer.find_statements_of_applicability": "StatementOfApplicability",
    "SolutionArchitect.find_design_patterns": "DesignPattern",
    "SolutionArchitect.find_information_supply_chains": "InformationSupplyChain",
    "SolutionArchitect.find_solution_blueprints": "SolutionBlueprint",
    "SolutionArchitect.find_solution_components": "SolutionComponent",
    "SolutionArchitect.find_solution_roles": "SolutionActorRole",
    "reference_data.find_valid_value_definitions": "ValidValueDefinition",
}


def _type_key(name: Optional[str]) -> str:
    """'Actor Profile', 'User-Identity' and 'ActorProfile' are the same type."""
    return "".join(ch for ch in (name or "") if ch.isalnum()).lower()


def _registry_pairs() -> Set[tuple]:
    """(find method, normalised target type) pairs pyegeria's own registered specs already use: known to fit."""
    from pyegeria.view.base_report_formats import get_report_registry
    pairs: Set[tuple] = set()
    for fs in get_report_registry().values():
        action = getattr(fs, "action", None)
        function = getattr(action, "function", None) if action else None
        if function and getattr(fs, "target_type", None):
            pairs.add((function, _type_key(fs.target_type)))
    return pairs


async def _check_find_fit(fs: Any, client: Any, result: ValidationResult) -> None:
    """The find method must return the target type: refuse when it returns another type."""
    action = fs.action
    function = getattr(action, "function", None)
    target = fs.target_type
    if not function or getattr(action, "analytic_function", None) or not target:
        return
    if function not in FIND_ELEMENT_TYPES:
        result.warn(f"Can't tell whether find method {function} returns {target} elements: pyegeria has no "
                    f"record of its element type.")
        result.not_checked.append(f"find method {function} fits target type {target}: element type unknown")
        return
    expected = FIND_ELEMENT_TYPES[function]
    if expected is None or _type_key(expected) == _type_key(target) or (function, _type_key(target)) in _registry_pairs():
        result.checked.append("find method fits the target type")
        return
    from md_processing.md_processing_utils.typed_properties import type_super_chain
    chain = await type_super_chain(client, target) if client is not None else None
    if chain is None:
        result.warn(f"Can't tell whether find method {function} (which returns {expected}) fits target type "
                    f"{target}: {target}'s super types couldn't be read from Egeria.")
        result.not_checked.append(f"find method {function} fits target type {target}: super types not read")
    elif any(_type_key(t) == _type_key(expected) for t in chain):
        result.checked.append("find method fits the target type")
    else:
        result.error(f"Find method {function} returns {expected} elements, but the target type is {target}, "
                     f"which isn't {expected} or a subtype of it ({' > '.join(chain)}).")


async def _check_spec(draft: SpecDraft, result: ValidationResult, client: Any = None, *,
                      legacy: bool = False) -> None:
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
    if is_find and target:
        await _check_find_fit(fs, client, result)
    if is_find and attrs is not None:
        strict_known = attrs | _formatter_derived_keys() | RELATED_ELEMENT_KEYS | ANNOTATION_KEYS
        if _is_generated(fs, draft.label):
            strict_known = strict_known | _command_attribute_keys()
        for fmt in fs.formats or []:
            for col in getattr(fmt, "attributes", None) or []:
                key = col.get("key") if isinstance(col, dict) else col.key
                name = col.get("name") if isinstance(col, dict) else col.name
                if not key or key in strict_known or _derived_by_rule(key):
                    continue
                if legacy and key in used_keys:
                    result.warn(f"Column '{name}' names '{key}', which isn't an attribute of {target}; it is "
                                f"accepted only because another pyegeria spec uses that key (legacy spec).")
                else:
                    result.error(f"Column '{name}' names '{key}', which isn't an attribute of {target} (or its "
                                 f"super types), nor a key pyegeria's formatter derives.")
        result.checked.append("column attributes" + (" (legacy: loose)" if legacy else ""))
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
_FIND_TYPES = {"text": "str", "bool": "bool", "int": "int", "list": "list", "statuslist": "list"}


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
        from pyegeria.authoring.lifecycle import PIN_NOT_HONOURED
        from pyegeria.authoring.versions import async_spec_at_version
        result.not_applied.append(PIN_NOT_HONOURED.format(version=draft.pinned_version))
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
                         gates: Optional[AuthoringGates] = None, legacy: bool = False) -> ValidationResult:
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
            await _check_spec(draft, result, client, legacy=legacy)
        elif isinstance(draft, ReportDraft):
            await _check_report(draft, client, result, gates)
        else:
            await _check_sheet(draft, client, result, gates)
    except Exception as exc:  # noqa: BLE001 -- a failed check is reported, never raised
        logger.exception("authoring validate")
        result.error(f"Validation could not finish: {type(exc).__name__}: {' '.join(str(exc).split())[:300]}")
    if client is not None:
        from pyegeria.authoring.publication import async_publication_notes
        notes, unread = await async_publication_notes(client, draft)
        result.not_applied += notes
        result.not_checked += unread
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
             gates: Optional[AuthoringGates] = None, legacy: bool = False) -> ValidationResult:
    from pyegeria.core.async_runner import run_sync
    return run_sync(async_validate(draft, client, run=run, gates=gates, legacy=legacy))
