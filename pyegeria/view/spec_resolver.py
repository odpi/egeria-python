"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Load-time resolution of report specs (RS-W2-2 PR-B; report-spec pipeline model §2c).

A spec is resolved when it is loaded, not when it is run: `resolve(spec)` runs the §2c checks
and returns a `ResolvedSpec`, or an `Unrunnable` carrying the failing checks' words. A spec that
fails is still listed (`list_report_specs(with_status=True)`), so a person sees why it cannot
run instead of a blank result. No spec is deleted, and resolution never stops a run: the
executor is unchanged here.

Today's specs are single-stage: one find method (`action.function`) or one analytic routine
(`action.analytic_function`). For them the §2c checks are:

  1. names: the find method resolves on the client class the executor would use; the analytic
     routine is a registered name with a python binding that imports; function-valued
     parameters name what they must.
  2. parameters: every parameter the executor always sends (required params, spec_params,
     output_format, report_spec) is one the find method accepts; every analytic_spec_params key
     is a parameter the routine declares. (No spec declares constants or `$param`s yet.)
  3. stage shapes: a single stage has no previous stage to check against (recorded, not run).
  4. formatter vs out: every output format is one the executor knows; a chart format needs an
     analytic routine; every column an analytic spec lists is a field the routine declares in
     `out`; every column's detail_spec names a registered spec. A find method declares no `out`,
     so a find spec's columns are not checked (recorded).
  5. role inputs: the routine's declared inputs, read by `declared_inputs`, the function the
     executor calls before it binds them (RS-W2-3). A declaration whose egeria_client inputs do
     not match the leading client arguments its python binding takes is refused, at load and at
     run, with the same words. Which environment supplies each role is the run's: a role the
     supply cannot provide refuses the run before its first stage (`role_supply.supply_inputs`).
  6. admission and tile_safe: recorded from the routine's declaration.
  7. seeding: the find method a spec may be seeded by is recorded.

Results are cached per spec and invalidated when the spec object or the analytic registry
changes (both are compared by identity, so re-registering either is a change).
"""

from __future__ import annotations

import inspect
import warnings
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

from loguru import logger

__all__ = [
    "ResolvedSpec",
    "Unrunnable",
    "resolve",
    "resolve_all",
    "unrunnable_specs",
    "spec_status",
    "log_resolution_summary",
    "OUTPUT_FORMATS",
    "CHART_FORMATS",
    "FUNCTION_VALUED_PARAMS",
    "declared_inputs",
    "routine_entry",
]

#: Output formats the executor renders from a Format row ("ALL" means every one of them).
OUTPUT_FORMATS = ("ALL", "DICT", "JSON", "TABLE", "LIST", "REPORT", "REPORT-GRAPH", "MD", "FORM", "HTML",
                  "MERMAID", "GRAPH")
#: Chart formats: dispatched before any Format row, and only for an analytic routine.
CHART_FORMATS = ("SERIES", "BAR", "PIE")
#: Routine parameters whose value names another routine (by registered name only, ISSUE-173).
FUNCTION_VALUED_PARAMS = ("metric_path",)

#: What the executor always passes a find method, besides the spec's own parameters.
_ALWAYS_SENT = ("output_format", "report_spec")


@dataclass
class ResolvedSpec:
    """A spec that passed every check that could run. `notes` say which checks did not run and why;
    `warnings` are defects that bite only when a caller uses an optional parameter."""
    name: str
    kind: str  # "find" | "analytic" | "find+analytic"
    target_type_name: Optional[str] = None
    stages: List[Dict[str, str]] = field(default_factory=list)
    params: List[str] = field(default_factory=list)
    output_formats: List[str] = field(default_factory=list)
    role_inputs: List[str] = field(default_factory=list)
    tile_safe: Optional[Dict[str, Any]] = None
    admission: Dict[str, Any] = field(default_factory=dict)
    seeds: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    runnable = True
    unrunnable_reason = ""


@dataclass
class Unrunnable:
    """A spec that failed a check. `words` holds one sentence per failure, each naming its check;
    `checks` the failing check numbers. `kind` is "format_only" for a spec with no action (it
    formats elements another call fetched)."""
    name: str
    kind: str
    words: List[str]
    checks: List[int]
    target_type_name: Optional[str] = None
    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    runnable = False

    @property
    def unrunnable_reason(self) -> str:
        return " ".join(self.words)


Resolution = Union[ResolvedSpec, Unrunnable]


# ── Client classes, as the executor resolves them ──

def _egeria_tech_classes() -> List[type]:
    """EgeriaTech plus every subclient class it proxies to: the one list `PlainSupply` serves."""
    from pyegeria.view.role_supply import egeria_tech_classes
    return egeria_tech_classes()


# ── Check 5: a routine's declared inputs, for the resolver and the executor alike ──

#: The leading parameter names the pre-W2-3 executor bound a client to by name. Read here ONLY to
#: check a declaration against its python binding (check 5); nothing binds by these names.
_BINDING_CLIENT_PARAM_NAMES = ("mgr", "ce", "expert", "client")


def _binding_client_slots(func: Any) -> int:
    """How many leading client arguments a python binding takes (check 5's consistency count)."""
    try:
        params = inspect.signature(func).parameters.values()
    except (TypeError, ValueError):
        return 0
    count = 0
    for param in params:
        if param.name in _BINDING_CLIENT_PARAM_NAMES and param.kind in (
                inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
            count += 1
        else:
            break
    return count


def routine_entry(func_decl: Any) -> Any:
    """The registry entry a routine reference names: by registered name, else the entry whose
    python binding is that dotted path (a fetch step names its function by path). None if none."""
    from pyegeria.view.analytic_registry import get_analytic_registry
    registry = get_analytic_registry()
    if isinstance(func_decl, str):
        if func_decl in registry:
            return registry[func_decl]
        return next((s for s in registry.values() if s.python_target() == func_decl), None)
    return None


def declared_inputs(func_decl: Any, func: Any = None) -> List[str]:
    """The inputs a routine declares, in declared order: what the executor supplies and binds to
    its leading positional parameters. The resolver's check 5 and the executor both call this, so
    a routine refused at load is refused at run with the same words.

    Raises `role_supply.RoleRefused` when the routine is not registered (so it declares nothing),
    when an input is not a role word or is repeated, or when its python binding (`func`, imported
    from the entry when not given) takes a different number of leading client arguments than the
    declaration lists egeria_client inputs."""
    from pyegeria.view.analytic_registry import _INPUT_ROLE
    from pyegeria.view.role_supply import RoleRefused, role_kind

    name = getattr(func_decl, "__name__", func_decl)
    def refuse(reason: str) -> None:
        raise RoleRefused(f"Routine '{name}' cannot run: {reason}.", routine=str(name), reason=reason)

    entry = routine_entry(func_decl)
    if entry is None:
        refuse(f"'{name}' is not a registered routine, so it declares no inputs for the executor to supply")
    name = entry.name
    inputs = list(entry.inputs)
    bad = [i for i in inputs if not _INPUT_ROLE.fullmatch(i or "")]
    if bad:
        refuse(f"routine {name}'s input {', '.join(repr(b) for b in bad)} is not a role word "
               "(egeria_client:<Class>, reader:<name>, viewer, subject)")
    if len(set(inputs)) != len(inputs):
        refuse(f"routine {name} declares an input more than once")
    if func is None:
        from pyegeria.view.format_set_executor import _import_callable
        func = _import_callable(entry.python_target())
    slots = _binding_client_slots(func)
    clients = sum(1 for i in inputs if role_kind(i) == "egeria_client")
    if slots != clients:
        refuse(f"routine {name}'s binding takes {slots} leading client argument(s) and its declaration "
               f"lists {clients} egeria_client input(s)")
    return inputs


def _find_method(func_decl: str) -> Tuple[Optional[Any], str]:
    """The method the executor would call for `Class.method`, or (None, the words why not)."""
    from pyegeria.view.format_set_executor import _resolve_client_and_method

    parts = func_decl.split(".")
    if len(parts) != 2 or not all(parts):
        return None, (f"its find method '{func_decl}' is not Class.method, which the executor needs "
                      f"(exactly one dot)")
    class_name, method_name = parts
    if not method_name.startswith("_async_"):
        method_name = "_async_" + method_name
    try:
        client_class, method_name = _resolve_client_and_method(f"{class_name}.{method_name}")
    except Exception as exc:  # noqa: BLE001 -- an unimportable mapped class is the finding
        return None, f"its find method's client class '{class_name}' cannot be imported: {exc}"
    from pyegeria.egeria_tech_client import EgeriaTech
    classes = _egeria_tech_classes() if client_class is EgeriaTech else [client_class]
    for cls in classes:
        method = getattr(cls, method_name, None)
        if callable(method):
            return method, ""
    where = ("EgeriaTech or any client it proxies to" if client_class is EgeriaTech
             else f"client class {client_class.__name__}")
    return None, f"its find method '{func_decl}' does not exist: {where} has no '{method_name}'"


def _accepts(method: Any) -> Tuple[set, bool]:
    try:
        sig = inspect.signature(method)
    except (TypeError, ValueError):
        return set(), True  # unknowable: treat as accepting anything
    names = {n for n in sig.parameters if n != "self"}
    var_kw = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
    return names, var_kw


# ── The checks ──

def _as_dict(spec: Any) -> Dict[str, Any]:
    if hasattr(spec, "model_dump"):
        return spec.model_dump()
    return dict(spec or {})


def _target_type_name(data: Dict[str, Any]) -> Optional[str]:
    """Egeria's property name (`target_type_name`), with `target_type` read as its alias."""
    return data.get("target_type_name") or data.get("target_type")


def _check_find(name: str, action: Dict[str, Any], fail, notes, warns, out: Dict[str, Any]) -> None:
    func_decl = action.get("function")
    if not isinstance(func_decl, str) or "." not in func_decl:
        fail(1, f"its find method {func_decl!r} is not Class.method")
        return
    method, why = _find_method(func_decl)
    if method is None:
        fail(1, why)
        return
    out["stages"].append({"kind": "producer", "name": func_decl, "binding": "python (client method)"})
    out["seeds"].append(func_decl)
    accepted, var_kw = _accepts(method)
    if var_kw:
        notes.append(f"check 2: {func_decl} takes **kwargs, so its parameter names are not checked")
        return
    required = list(action.get("required_params") or [])
    spec_params = list((action.get("spec_params") or {}).keys())
    always = [p for p in _ALWAYS_SENT if p not in accepted]
    if always:
        fail(2, f"the executor always passes {', '.join(always)} and {func_decl} does not accept "
                f"{'it' if len(always) == 1 else 'them'}")
    for label, names in (("required parameter", required), ("spec parameter", spec_params)):
        bad = [p for p in names if p not in accepted]
        if bad:
            fail(2, f"its {label}{'s' if len(bad) > 1 else ''} {', '.join(bad)} "
                    f"{'is' if len(bad) == 1 else 'are'} sent on every run and {func_decl} does not accept "
                    f"{'it' if len(bad) == 1 else 'them'}")
    optional = [p for p in (action.get("optional_params") or []) if p not in accepted]
    if optional:
        warns.append(f"check 2: optional parameter{'s' if len(optional) > 1 else ''} {', '.join(optional)} "
                     f"{'is' if len(optional) == 1 else 'are'} not accepted by {func_decl}: a caller who "
                     f"passes {'it' if len(optional) == 1 else 'one'} gets a TypeError")
    out["params"].extend(p for p in required + list(action.get("optional_params") or []) if p not in out["params"])


def _check_analytic(name: str, action: Dict[str, Any], fail, notes, warns, out: Dict[str, Any]) -> Any:
    """Checks 1, 2, 5, 6 for the analytic stage. Returns the routine's declaration, or None."""
    from pyegeria.view.analytic_registry import get_analytic_registry
    from pyegeria.view.format_set_executor import (AnalyticFunctionRefused, _import_callable,
                                                   resolve_report_spec_function)
    from pyegeria.view.role_supply import RoleRefused

    func_decl = action["analytic_function"]
    registry = get_analytic_registry()
    entry = registry.get(func_decl)
    if entry is None:
        try:
            resolve_report_spec_function(func_decl)
        except AnalyticFunctionRefused as exc:
            fail(1, str(exc))
        return None
    target = entry.python_target()
    if not target:
        kinds = ", ".join(f"{b.kind} '{b.target}'" for b in entry.bindings) or "none"
        fail(1, f"routine '{func_decl}' has no binding this executor can honour (its bindings: {kinds}; "
                f"pyegeria runs python bindings only)")
        return None
    try:
        _import_callable(target)
    except Exception as exc:  # noqa: BLE001 -- an unimportable binding is the finding
        fail(1, f"routine '{func_decl}' binds python target '{target}', which cannot be imported: {exc}")
        return None
    out["stages"].append({"kind": entry.kind, "name": func_decl, "binding": f"python {target}"})
    if entry.action is not None:
        notes.append(f"check 3: routine '{func_decl}' runs fetch {entry.action.fetch} then analytic "
                     f"{entry.action.analytic}; neither step declares its shapes, so the hand-off is not checked")

    declared = [p.name for p in entry.params]
    out["params"].extend(p for p in declared if p not in out["params"])
    spec_params = action.get("analytic_spec_params") or {}
    unknown = [k for k in spec_params if k not in declared]
    if unknown and not declared:
        # A routine that declares no parameters at all is silent about them, not declaring none:
        # the spec runs today, so this is the declaration's gap, said as a warning.
        warns.append(f"check 2: routine '{func_decl}' declares no parameters, so analytic_spec_params "
                     f"{', '.join(unknown)} cannot be checked; the routine's declaration should list them")
    elif unknown:
        fail(2, f"its analytic_spec_params {', '.join(unknown)} {'is' if len(unknown) == 1 else 'are'} not "
                f"declared by routine '{func_decl}' (declared: {', '.join(declared)})")
    for param in FUNCTION_VALUED_PARAMS:
        value = spec_params.get(param)
        if param in declared and value is not None and value not in registry:
            fail(1, f"its {param} '{value}' is not a registered routine name (a report spec names routines by "
                    f"registered name only)")

    try:
        out["role_inputs"] = declared_inputs(func_decl)
    except RoleRefused as exc:
        fail(5, exc.reason)
    else:
        notes.append("check 5: " + (f"role inputs {', '.join(out['role_inputs'])}" if out["role_inputs"] else
                                    f"routine '{func_decl}' declares no role inputs")
                     + "; the environment's supply provides each before the first stage runs")

    try:
        routine = entry.routine()
    except ValueError as exc:
        notes.append(f"check 6: routine '{func_decl}' is not a valid routine declaration, so its "
                     f"admission and tile_safe are not recorded: {exc}")
        return entry.declaration
    out["tile_safe"] = routine.tile_safe.model_dump() if routine.tile_safe else None
    out["admission"] = routine.admission.model_dump()
    if routine.tile_safe is None:
        notes.append(f"check 6: routine '{func_decl}' declares no tile_safe")
    return routine.declaration


def _check_formats(data: Dict[str, Any], has_analytic: bool, decl: Any, fail, notes, out: Dict[str, Any],
                   registry_names: set) -> None:
    seen: List[str] = []
    out_names = None
    if decl is not None:
        fields = decl.out_fields()
        out_names = {f.name for f in fields} if fields else None
    analytic_name = (data.get("action") or {}).get("analytic_function")
    for fmt in data.get("formats") or []:
        types = [str(t).upper() for t in (fmt.get("types") or [])]
        for t in types:
            if t not in seen:
                seen.append(t)
        unknown = [t for t in types if t not in OUTPUT_FORMATS + CHART_FORMATS]
        if unknown:
            fail(4, f"its output format{'s' if len(unknown) > 1 else ''} {', '.join(unknown)} "
                    f"{'is' if len(unknown) == 1 else 'are'} not one the executor renders")
        charts = [t for t in types if t in CHART_FORMATS]
        if charts and not has_analytic:
            fail(4, f"it offers {', '.join(charts)}, a chart, and has no analytic routine to chart")
        for col in fmt.get("attributes") or []:
            key = str(col.get("key") or "")
            detail = col.get("detail_spec")
            if detail and detail not in registry_names:
                fail(4, f"its column '{col.get('name') or key}' drills into detail_spec '{detail}', which is not "
                        f"a registered report spec")
            if has_analytic and out_names is not None and key and key.split(".", 1)[0] not in out_names:
                fail(4, f"its column '{col.get('name') or key}' reads field '{key}', which routine "
                        f"'{analytic_name}' does not declare in out (declared: {', '.join(sorted(out_names))})")
    if has_analytic and decl is not None and out_names is None:
        notes.append(f"check 4: routine '{analytic_name}' declares no out, so its columns are not checked")
    if (data.get("action") or {}).get("function"):
        notes.append("check 4: a find method declares no out, so the columns (element properties) are not checked")
    out["output_formats"] = seen


def resolve(spec: Any, name: Optional[str] = None, *, registry_names: Optional[set] = None) -> Resolution:
    """Resolve one report spec (a FormatSet or its dict) through the §2c checks."""
    data = _as_dict(spec)
    name = name or data.get("heading") or "?"
    if registry_names is None:
        from pyegeria.view.base_report_formats import get_report_registry
        registry_names = set(get_report_registry().keys())
    target = _target_type_name(data)
    words: List[str] = []
    checks: List[int] = []
    notes: List[str] = []
    warns: List[str] = []

    def fail(check: int, sentence: str) -> None:
        words.append(f"Spec '{name}' cannot run (check {check}): {sentence}.")
        if check not in checks:
            checks.append(check)

    action = data.get("action")
    if not action:
        return Unrunnable(name=name, kind="format_only", checks=[1], target_type_name=target, words=[
            f"Spec '{name}' cannot run on its own: it has no action, so it formats elements another call "
            f"fetched (it is a detail or a command's output format)."])

    out: Dict[str, Any] = {"stages": [], "params": [], "seeds": [], "role_inputs": [], "tile_safe": None,
                           "admission": {}}
    has_find = bool(action.get("function"))
    has_analytic = bool(action.get("analytic_function"))
    kind = "+".join(k for k, on in (("find", has_find), ("analytic", has_analytic)) if on) or "none"
    if has_find:
        _check_find(name, action, fail, notes, warns, out)
    decl = _check_analytic(name, action, fail, notes, warns, out) if has_analytic else None
    if not has_find and not has_analytic:
        fail(1, "its action names neither a find method nor an analytic routine")
    notes.append("check 3: a single stage, so there is no previous stage's shape to check against")
    _check_formats(data, has_analytic, decl, fail, notes, out, registry_names)

    if words:
        return Unrunnable(name=name, kind=kind, words=words, checks=sorted(checks), target_type_name=target,
                          notes=notes, warnings=warns)
    return ResolvedSpec(name=name, kind=kind, target_type_name=target, notes=notes, warnings=warns, **out)


# ── All specs, cached ──

_CACHE: Dict[str, Tuple[int, Tuple, Resolution]] = {}
_SUMMARY_LOGGED = False


def _analytic_fingerprint() -> Tuple:
    from pyegeria.view.analytic_registry import get_analytic_registry
    return tuple(sorted((n, id(s)) for n, s in get_analytic_registry().items()))


def resolve_all(*, refresh: bool = False) -> Dict[str, Resolution]:
    """Every registered report spec, resolved. Cached per spec: a spec is re-resolved when its
    FormatSet object, the set of registered spec names, or the analytic registry changes."""
    from pyegeria.view.base_report_formats import get_report_registry
    registry = get_report_registry()
    names = set(registry.keys())
    fingerprint = (_analytic_fingerprint(), tuple(sorted(names)))
    results: Dict[str, Resolution] = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        for label, spec in registry.items():
            cached = _CACHE.get(label)
            if not refresh and cached and cached[0] == id(spec) and cached[1] == fingerprint:
                results[label] = cached[2]
                continue
            try:
                result = resolve(spec, label, registry_names=names)
            except Exception as exc:  # noqa: BLE001 -- the resolver must not take the listing down
                result = Unrunnable(name=label, kind="unknown", checks=[], words=[
                    f"Spec '{label}' could not be resolved: {type(exc).__name__}: {exc}."])
            _CACHE[label] = (id(spec), fingerprint, result)
            results[label] = result
    for gone in set(_CACHE) - names:
        _CACHE.pop(gone, None)
    return results


def unrunnable_specs(*, include_format_only: bool = False) -> Dict[str, Unrunnable]:
    """The specs that cannot run, with their words. Specs with no action (format-only) are left
    out unless asked for: they are not meant to run on their own."""
    return {n: r for n, r in resolve_all().items()
            if isinstance(r, Unrunnable) and (include_format_only or r.kind != "format_only")}


def spec_status(label: str) -> Dict[str, Any]:
    """{name, runnable, unrunnable_reason} for one registered spec."""
    result = resolve_all().get(label)
    if result is None:
        return {"name": label, "runnable": False, "unrunnable_reason": f"Spec '{label}' is not registered."}
    return {"name": label, "runnable": result.runnable, "unrunnable_reason": result.unrunnable_reason}


def log_resolution_summary(*, force: bool = False, where: str = "load") -> Dict[str, Unrunnable]:
    """Resolve every spec and log the count of unrunnable specs and each one's words. Logged once
    per process unless `force` (refresh_specs and archive loads force it)."""
    global _SUMMARY_LOGGED
    bad = unrunnable_specs()
    if _SUMMARY_LOGGED and not force:
        return bad
    _SUMMARY_LOGGED = True
    total = len(_CACHE)
    format_only = sum(1 for r in resolve_all().values() if isinstance(r, Unrunnable) and r.kind == "format_only")
    if bad:
        logger.warning(f"Report specs resolved at {where}: {len(bad)} of {total} cannot run "
                       f"({format_only} more are format-only and not run on their own).")
        for result in bad.values():
            logger.warning(result.unrunnable_reason)
    else:
        logger.info(f"Report specs resolved at {where}: all {total - format_only} runnable specs resolve "
                    f"({format_only} format-only).")
    return bad
