"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

A pure helper to execute a FormatSet action and return normalized results without side effects
(printing or writing to disk). This is suitable for programmatic use (e.g., MCP adapters,
notebooks, services) that want DICT/JSON or text output directly.

Notes
- Only use this for read-style format sets. It assumes the action is safe to call.
- Credentials and endpoints default from pyegeria.config.settings (ENV/config.json/ENV files).
- Prefer output_format="DICT" for machine-consumable results. REPORT/HTML/MERMAID are returned as text.
"""
from __future__ import annotations

import asyncio
import inspect
import json
import os
import re
import string
import sys
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from loguru import logger
from pydantic import ValidationError

import importlib
from pyegeria.core._globals import NO_ELEMENTS_FOUND
from pyegeria.core.config import settings
from pyegeria.core._exceptions import PyegeriaException, print_validation_error
from pyegeria.view.base_report_formats import (
    select_report_spec,
    get_report_spec_heading,
    get_report_spec_description,
    get_report_registry,
)
from pyegeria.view.output_formatter import generate_output
from pyegeria.view.analytic_registry import ABSENCE_STATES, AnalyticActionSpec, canonical_absence_state
from pyegeria.view.analytic_registry import get_analytic_registry as get_analytic_registry_functions
from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.view.role_supply import PlainSupply, RoleRefused, RoleSupply, supply_inputs
from pyegeria.view.overview_metrics import recording_unmeasured
from pyegeria.view._output_format_models import DOCUMENT_OUTPUT_TYPE, check_document_file_name
from pyegeria.view.document_validators import run_document_validator
from pyegeria.core._server_client import recording_list_requests
from pyegeria.view.output_formatter import check_dict_shape, dict_shape_for_call
from pyegeria.view.structured_table import build_structured_table, check_table_shape, mark_relationship_absence

_CLIENT_CLASS_MAP = {
    "CollectionManager": "pyegeria.omvs.collection_manager.CollectionManager",
    "GovernanceOfficer": "pyegeria.omvs.governance_officer.GovernanceOfficer",
    "GlossaryManager": "pyegeria.omvs.glossary_manager.GlossaryManager",
    "ExternalReference": "pyegeria.omvs.external_links.ExternalReferences",
    "ClassificationExplorer": "pyegeria.omvs.classification_explorer.ClassificationExplorer",
    "ActorManager": "pyegeria.omvs.actor_manager.ActorManager",
    "ValidMetadataManager": "pyegeria.omvs.valid_metadata.ValidMetadataManager",
    "DataDesigner": "pyegeria.omvs.data_designer.DataDesigner",
    "MyProfile": "pyegeria.omvs.my_profile.MyProfile",
    "ProjectManager": "pyegeria.omvs.project_manager.ProjectManager",
    "SolutionArchitect": "pyegeria.omvs.solution_architect.SolutionArchitect",
    "ReferenceDataManager": "pyegeria.omvs.reference_data.ReferenceDataManager",
    "reference_data": "pyegeria.omvs.reference_data.ReferenceDataManager",
}


def _resolve_report_target_type(fmt: Dict[str, Any], report_name: str) -> str:
    """Return safe target type for rendering and warn when a spec omits it."""
    target_type = fmt.get("target_type") if isinstance(fmt, dict) else None
    if target_type is None:
        logger.warning(
            f"Report spec '{report_name}' has target_type=None. Falling back to 'Referenceable'."
        )
        return "Referenceable"
    return str(target_type)


def _resolve_client_and_method(func_decl: str):
    """Given a function declaration like 'ClassName.method', return (client_class, method_name)."""
    # Lazy import EgeriaTech to avoid circular dependency
    from pyegeria.egeria_tech_client import EgeriaTech

    if not isinstance(func_decl, str) or "." not in func_decl:
        return (EgeriaTech, None)
    class_name, method_name = func_decl.split(".", 1)
    
    path = _CLIENT_CLASS_MAP.get(class_name)
    if path and isinstance(path, str):
        # Lazy import
        module_path, attr_name = path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        client_class = getattr(module, attr_name)
    else:
        client_class = EgeriaTech
        
    return (client_class, method_name)


# Module prefixes a report spec may name directly as a dotted path (ISSUE-169).
# Override with PYEGERIA_ANALYTIC_MODULE_PREFIXES (comma-separated). A prefix
# matches the module itself or anything under it, so "pyegeria" does not
# admit "pyegeria_extras".
DEFAULT_ANALYTIC_MODULE_PREFIXES = ("pyegeria", "trellis_analytics")


class AnalyticFunctionRefused(ValueError):
    """A report spec named a callable that is neither registered nor under an allowed module prefix."""
    pass


def _is_spec_refusal(exc: BaseException) -> bool:
    """True when `exc` is a report spec refusal: an expected outcome, not a failure.

    The refusals are the allowlist's (AllowlistRefusal), the analytic-function resolver's
    (AnalyticFunctionRefused), a declared input the environment cannot supply (RoleRefused),
    a microflow this pyegeria cannot run or parse (CannotRunYet, MicroflowError), and a search a
    find method refuses to send (SearchRefused: '*' with no type or a root type).
    """
    from pyegeria.view.microflow import AllowlistRefusal, CannotRunYet, MicroflowError  # lazy: microflow imports this module
    from pyegeria.core.request_filters import SearchRefused
    return isinstance(exc, (AllowlistRefusal, AnalyticFunctionRefused, RoleRefused, CannotRunYet, MicroflowError,
                            SearchRefused))


def analytic_module_prefixes() -> tuple:
    """The allowed module prefixes: PYEGERIA_ANALYTIC_MODULE_PREFIXES if set, else the defaults."""
    raw = os.getenv("PYEGERIA_ANALYTIC_MODULE_PREFIXES", "").strip()
    if not raw:
        return DEFAULT_ANALYTIC_MODULE_PREFIXES
    return tuple(p.strip().rstrip(".") for p in raw.split(",") if p.strip())


def _module_allowed(module_path: str) -> bool:
    return any(module_path == p or module_path.startswith(p + ".") for p in analytic_module_prefixes())


def python_binding_allowed(target: str) -> bool:
    """Is a python binding's target under an allowed module prefix? The allow-list applies to
    binding targets only: a report spec names routines by registered name and never carries a
    target (ISSUE-173, RS-W2-2)."""
    return isinstance(target, str) and "." in target and _module_allowed(target.rsplit(".", 1)[0])


def _python_binding_of(spec) -> str:
    """A registered entry's python binding target, or AnalyticFunctionRefused naming the bindings
    it has instead (this pyegeria runs python bindings only)."""
    target = spec.python_target() if hasattr(spec, "python_target") else spec.function
    if not target:
        kinds = ", ".join(f"{b.kind} '{b.target}'" for b in getattr(spec, "bindings", [])) or "none"
        raise AnalyticFunctionRefused(
            f"Analytic function '{spec.name}' has no python binding (its bindings: {kinds}); this pyegeria "
            f"runs python bindings only.")
    return target


def _import_callable(func_decl: str):
    module_path, func_name = func_decl.rsplit(".", 1)
    module = importlib.import_module(module_path)
    func = getattr(module, func_name, None)
    if func is None or not callable(func):
        raise AttributeError(f"'{func_name}' not found in module '{module_path}'")
    return func


def _resolve_analytic_function(func_decl: str):
    """Return the callable a report spec's analytic_function (or an action's
    fetch/analytic step) names.

    Unlike `function` (find_method), `analytic_function` (extra_find) targets a
    plain module-level function, not a client class method -- overview_metrics.py's
    whole design boundary is that its functions take an already-constructed,
    already-authenticated client as their first argument, so there's no client
    class to resolve here, just the function itself.

    A report spec is data, so it may not import arbitrary code (ISSUE-169):
      1. A registered name (analytic_registry) resolves to that entry's python
         binding; an entry with none is refused by name.
      2. A dotted path some registered entry declares is trusted as-is.
      3. Any other dotted path must sit under an allowed module prefix
         (`python_binding_allowed`); anything else raises
         AnalyticFunctionRefused before any import happens.
    Cases 2 and 3 are binding targets (an action's fetch/analytic step): a report
    spec never reaches them, because
    `resolve_report_spec_function` accepts registered names only (ISSUE-173).
    """
    if not isinstance(func_decl, str) or not func_decl.strip():
        raise ValueError(f"Invalid analytic_function declaration: {func_decl!r}")
    from pyegeria.view.analytic_registry import get_analytic_registry

    registry = get_analytic_registry()
    spec = registry.get(func_decl)
    if spec is not None:
        return _import_callable(_python_binding_of(spec))
    if "." not in func_decl:
        raise AnalyticFunctionRefused(
            f"Analytic function '{func_decl}' is not a registered name, and is not a dotted path.")
    if any(s.function and s.function == func_decl for s in registry.values()):
        return _import_callable(func_decl)
    if not python_binding_allowed(func_decl):
        raise AnalyticFunctionRefused(
            f"Analytic function '{func_decl}' is not registered and its module is not under an allowed "
            f"prefix {list(analytic_module_prefixes())}. Register it in the analytic registry, or add its "
            f"package to PYEGERIA_ANALYTIC_MODULE_PREFIXES.")
    logger.debug(f"Analytic function '{func_decl}' resolved by dotted path (not registered).")
    return _import_callable(func_decl)


def resolve_report_spec_function(func_decl: str):
    """Resolve a function a report spec names: its `analytic_function`, or a
    function-valued parameter such as metric_trend's `metric_path`.

    A report spec names an analytic function by its registered name (ISSUE-173).
    Anything else, including a dotted path, raises AnalyticFunctionRefused before
    any import; the message names the registered name to use when one exists.
    Dotted paths were deprecated in 6.2.18 and are refused from 6.2.19.
    """
    registry = get_analytic_registry_functions()
    if isinstance(func_decl, str) and func_decl in registry:
        return _resolve_analytic_function(func_decl)
    names = sorted(n for n, s in registry.items() if s.function == func_decl)
    instead = (f"use its registered name '{names[0]}'" if names else
               "register it through the 'pyegeria.analytics' entry-point group and use its name")
    raise AnalyticFunctionRefused(
        f"Report spec names analytic function {func_decl!r}, which is not a registered name; {instead}. "
        f"Report specs name analytic functions by registered name only (dotted paths are refused "
        f"from pyegeria 6.2.19).")


def _plain_client(view_server: str, view_url: str, user: str, user_pass: str,
                  token: Optional[str] = None) -> Any:
    """The caller's EgeriaTech, authenticated: with `token` when given (ISSUE-86), else a token
    minted from `user`/`user_pass`. `PlainSupply` calls this at most once per run, and only when a
    routine declares an egeria_client input (ISSUE-137: no client, no connection)."""
    client = EgeriaTech(view_server, view_url, user_id=user, user_pwd=user_pass)
    if token:
        client.set_bearer_token(token)
    else:
        client.create_egeria_bearer_token()
    return client


def run_analytic_action(
    action: AnalyticActionSpec, client: Any = None, *,
    fetch_kwargs: Optional[Dict[str, Any]] = None,
    analytic_kwargs: Optional[Dict[str, Any]] = None,
    supply: Optional[RoleSupply] = None,
) -> Any:
    """Run an `analytic_registry.AnalyticActionSpec`'s fetch step, then (if
    declared) its analytic step over the fetch's raw result -- the executor
    for the fetch+analytic action shape (BACKLOG.md NEXT-18, egeria-workspaces).
    Generalizes the pattern `ai_ready_assets` (overview_metrics.py) already
    used by hand into a declared, reusable shape; every existing registered
    analytic function with a plain `.function` string is untouched by this
    and keeps using `_run_analytic_function`/`_resolve_analytic_function`
    below exactly as before -- this is a separate, additive entry point, not
    a replacement.

    The fetch step must be a registered routine (by name or by its python binding's path): its
    declared `inputs` are supplied, in declared order, from `supply` -- or, when none is given,
    from `PlainSupply(client)`, the caller's already-authenticated client (RS-W2-3: inputs by
    role, never by parameter name). The analytic step gets the fetch's raw result followed by the
    SAME supplied arguments, so it can itself make a further client call (e.g. follow a
    relationship to enrich) with the identical client the fetch used.
    """
    from pyegeria.view.spec_resolver import declared_inputs  # lazy: the resolver imports this module
    fetch_func = _resolve_analytic_function(action.fetch)
    if supply is None:
        supply = PlainSupply(client)
    fetch_args = supply_inputs(action.fetch, declared_inputs(action.fetch, fetch_func), supply)
    raw_result = fetch_func(*fetch_args, **(fetch_kwargs or {}))

    if not action.analytic:
        return raw_result

    analytic_func = _resolve_analytic_function(action.analytic)
    return analytic_func(raw_result, *fetch_args, **(analytic_kwargs or {}))


# Result-state envelope (ISSUE-139/140). A routine that reports how sure it is
# carries one of these states; only an established answer (measured, or
# nothing_found = a real zero) has numbers worth charting.
ENVELOPE_STATES = ("measured", "nothing_found", "not_established", "not_applicable")
CHARTABLE_STATES = ("measured", "nothing_found")


def _result_envelope(result: Any) -> Optional[Dict[str, str]]:
    """Read a result's state envelope, or None if it has none.

    Recognised shapes: a dict with `state` (and optional `state_reason`/`subtitle`),
    a dict with `resultState`/`resultStateReason` (the additionalProperties carrier),
    a dict with a nested `envelope` dict in either style, or an object whose
    `envelope` attribute has `result_state`/`result_state_reason`.
    """
    def _from_mapping(m: Dict[str, Any]) -> Optional[Dict[str, str]]:
        state = m.get("state", m.get("resultState", m.get("result_state")))
        if state is None:
            return None
        state = str(getattr(state, "value", state))
        if state not in ENVELOPE_STATES:
            return None
        reason = str(m.get("state_reason", m.get("resultStateReason", m.get("result_state_reason", ""))) or "")
        subtitle = m.get("subtitle") or (state.replace("_", " ") + (f" \u00b7 {reason}" if reason else ""))
        found = {"state": state, "reason": reason, "subtitle": str(subtitle)}
        claimed = canonical_absence_state(m.get("absence"))  # legacy measured_nothing reads as nothing_found
        if claimed in ABSENCE_STATES:  # the result says which absence (ISSUE-171)
            found["absence"] = claimed
        return found

    if isinstance(result, dict):
        found = _from_mapping(result)
        if found:
            return found
        nested = result.get("envelope")
        if isinstance(nested, dict):
            return _from_mapping(nested)
        return None
    env = getattr(result, "envelope", None)
    if env is not None and not isinstance(env, bool):
        if isinstance(env, dict):
            return _from_mapping(env)
        return _from_mapping({"result_state": getattr(env, "result_state", None),
                              "result_state_reason": getattr(env, "result_state_reason", "")})
    return None


def _jsonable(result: Any) -> Any:
    """A pydantic result (e.g. a routine's own result model) as plain data."""
    dump = getattr(result, "model_dump", None)
    return dump(mode="json") if callable(dump) else result


def _with_envelope(out: Dict[str, Any], envelope: Optional[Dict[str, str]]) -> Dict[str, Any]:
    if envelope:
        out["envelope"] = envelope
    return out


# Envelope state -> the declared absence it is (ISSUE-171). not_established reads as
# not_measured unless the result itself claims not_permitted (an `absence` key);
# the reason text is never parsed to guess which.
_ABSENCE_FOR_STATE = {
    "nothing_found": "nothing_found",
    "not_established": "not_measured",
    "not_applicable": "not_applicable",
}

# Used only when the function declares no absence sentences; built from its own reason.
_UNDECLARED_ABSENCE_WORDS = {
    "not_measured": "Not measured",
    "not_permitted": "Not measured: not permitted",
    "not_applicable": "Does not apply",
    "nothing_found": "Measured; nothing found",
}


def _declaration_for(func_decl: str):
    """The registered declaration for an analytic_function, by registry name or by the
    dotted path a registered entry declares; None when the function declares none."""
    registry = get_analytic_registry_functions()
    spec = registry.get(func_decl) or next((s for s in registry.values() if s.function == func_decl), None)
    return spec.declaration if spec is not None else None


def _absence_for(envelope: Optional[Dict[str, str]], func_decl: str) -> Optional[Dict[str, Any]]:
    """What a reader is told when a result is not a measured value (ISSUE-171): the absence
    state, the function's declared sentence for it (or words built from its reason when it
    declares none, marked declared=False), and the reason. None for a measured result or
    one with no envelope, which keep their old shapes."""
    if not envelope or envelope["state"] not in _ABSENCE_FOR_STATE:
        return None
    state = canonical_absence_state(_ABSENCE_FOR_STATE[envelope["state"]])
    if state == "not_measured" and envelope.get("absence") == "not_permitted":
        state = "not_permitted"
    reason = envelope.get("reason", "")
    declaration = _declaration_for(func_decl)
    if declaration is not None:
        return {"state": state, "sentence": declaration.absence.sentence(state), "reason": reason,
                "declared": True}
    words = _UNDECLARED_ABSENCE_WORDS[state]
    return {"state": state, "sentence": f"{words}: {reason}." if reason else f"{words}.", "reason": reason,
            "declared": False}


def _run_recording_unmeasured(action: dict, **kwargs: Any) -> Tuple[Any, List[Dict[str, Any]]]:
    """Run the analytic routine and collect a note for every count in it that was not measured
    (a failed or timed-out count, or a find fallback that stopped at its page cap -- a lower
    bound, never a total). See overview_metrics.recording_unmeasured."""
    with recording_unmeasured() as notes:
        result = _run_analytic_function(action, **kwargs)
    unique: List[Dict[str, Any]] = []  # a series repeats the same note once per point
    for note in notes:
        if note not in unique:
            unique.append(note)
    return result, unique


def _unmeasured_envelope(notes: List[Dict[str, Any]]) -> Dict[str, str]:
    """The not_established envelope for a result whose value is a count that was not measured;
    the reason is each note's own words, so the lower bound ("at least 500") reaches the reader."""
    reason = "; ".join(f"{n['count']}: {n['reason']}" for n in notes)
    return {"state": "not_established", "reason": reason, "subtitle": f"not established \u00b7 {reason}"}


def _absent_output(result: Any, envelope: Dict[str, str], absence: Dict[str, Any],
                   notes: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Output for a result whose value is not established or does not apply: the sentence,
    never top-level data a chart or table would draw as an answer. Any partial result rides
    under `detail`. With `notes` (counts that were not measured), `content` also says which
    and why, lower bound included, and the notes ride under `unmeasured`."""
    content = absence["sentence"]
    if notes:
        content = f"{content} Not measured: " + "; ".join(f"{n['count']}: {n['reason']}" for n in notes) + "."
    out: Dict[str, Any] = {"kind": "absent", "content": content, "absence": absence}
    if result not in (None, [], {}):
        out["detail"] = result
    if notes:
        out["unmeasured"] = notes
    return _with_envelope(out, envelope)


def _run_analytic_function(
    action: dict, *, params: Dict[str, Any],
    view_server: str, view_url: str, user: str, user_pass: str,
    token: Optional[str] = None,
    supply: Optional[RoleSupply] = None,
) -> Any:
    """Resolve and call a report spec action's `analytic_function` (extra_find),
    returning the function's raw result -- no chart-wrapping, no output_format
    handling. Shared by `_exec_analytic_series` (SERIES/chart path) and
    `exec_report_spec`'s analytic-only passthrough (DICT/JSON/etc. path).

    ISSUE-86: when `token` is given, the client is authenticated with it
    directly (`set_bearer_token`) instead of minting a fresh token via
    `create_egeria_bearer_token()` -- lets a caller that already holds a
    bearer token for the calling user (e.g. Egeria Advisor's app JWT, which
    carries the user's Egeria token and no longer the password) run a report
    as that user instead of falling back to the `user`/`user_pass` service
    account. Backward compatible: `user`/`user_pass` keep working exactly as
    before when no token is given.

    RS-W2-3: the routine's leading arguments are its declared `inputs`, in declared order, each
    asked of `supply` (default: `PlainSupply` over the caller's client built from the arguments
    above). Every input is obtained before the routine runs, so a role the supply cannot provide
    -- or a declaration that does not match its binding (check 5) -- raises `RoleRefused` with
    its words before any stage. No parameter name is read to decide what to pass.
    """
    func_decl = action.get("analytic_function")
    if not func_decl:
        raise ValueError("Report spec action has no analytic_function (extra_find).")
    spec_params = action.get("analytic_spec_params", {}) or {}

    # Deliberately no fixed required/optional-param whitelist (see
    # _exec_analytic_chart's docstring) -- every caller-supplied param is
    # forwarded as-is; Python's own TypeError on an unexpected keyword is the
    # validation. `analytic_spec_params` are DEFAULTS, not pins: a report
    # spec author sets a sensible starting value (e.g. type_name="GlossaryTerm"),
    # and a caller who explicitly supplies that same param overrides it --
    # this is what lets a report spec's "Element Count by Type" demo, e.g.,
    # actually be re-pointed at a different type from the UI/API instead of
    # being permanently locked to the demo's own default.
    call_params: Dict[str, Any] = dict(spec_params)
    call_params.update({k: v for k, v in params.items() if v not in (None, "")})

    func = resolve_report_spec_function(func_decl)
    from pyegeria.view.spec_resolver import declared_inputs  # lazy: the resolver imports this module
    inputs = declared_inputs(func_decl, func)  # check 5: the same function the resolver runs at load
    if supply is None:
        supply = PlainSupply(client_factory=lambda: _plain_client(view_server, view_url, user, user_pass, token))
    # Every role is obtained here, before the routine runs; a routine that declares no
    # egeria_client input never connects or mints a token (ISSUE-137).
    args = supply_inputs(func_decl, inputs, supply)
    return func(*args, **call_params)


def _resolve_action_target_client(egeria_client: EgeriaTech, client_class: type) -> Any:
    """Resolve the concrete client instance to invoke for a report action."""
    if client_class is EgeriaTech or isinstance(egeria_client, client_class):
        return egeria_client

    # Prefer an existing lazy-loaded subclient that exactly matches the declared class.
    subclient_map = getattr(egeria_client, "_subclient_map", {})
    if isinstance(subclient_map, dict) and hasattr(egeria_client, "_get_subclient"):
        for attr_name, sub_cls in subclient_map.items():
            if sub_cls is client_class:
                return egeria_client._get_subclient(attr_name)

    # Fallback for non-standard clients outside EgeriaTech's map.
    client = client_class(
        egeria_client.view_server,
        egeria_client.platform_url,
        user_id=egeria_client.user_id,
        user_pwd=egeria_client.user_pwd,
        token=egeria_client.token,
    )
    client._token_minted_for = getattr(egeria_client, "_token_minted_for", None)
    return client


def _normalize_report_params(params: Dict[str, Any], action_mode: str = "generic") -> Dict[str, Any]:
    """Normalize Dr.Egeria/CLI param aliases to action-call names and drop empty optionals."""
    normalized = dict(params or {})

    search_alias_target = "filter_string" if action_mode == "get" else "search_string"
    aliases = {
        search_alias_target: ["search_string"],
        "metadata_element_type": ["metadata_element_type_name", "metadata_element_name"],
        "metadata_element_subtypes": ["metadata_element_subtype_names"],
        "limit_results_by_status": ["limit_result_by_status"],
        "sequencing_order": ["sort_order", "output_sort_order"],
        "sequencing_property": ["order_property_name"],
        "anchor_scope_guid": ["anchor_scope_id"],
    }

    for canonical_key, alias_keys in aliases.items():
        if canonical_key in normalized and normalized.get(canonical_key) not in (None, "", []):
            continue
        for alias_key in alias_keys:
            alias_value = normalized.get(alias_key)
            if alias_value not in (None, "", []):
                normalized[canonical_key] = alias_value
                break

    # Some filters are list-valued in request models; accept common scalar forms
    # from markdown/CLI and coerce to list[str] for downstream body validation.
    list_like_keys = {
        "limit_results_by_status",
        "limit_result_by_status",
        "metadata_element_subtypes",
        "metadata_element_subtype_names",
        "skip_relationships",
        "include_only_relationships",
        "skip_classified_elements",
        "include_only_classified_elements",
        "governance_zone_filter",
        "classification_names",
    }

    def _to_string_list(raw_value: Any) -> Any:
        if isinstance(raw_value, str):
            text = raw_value.strip()
            if text.startswith("[") and text.endswith("]"):
                text = text[1:-1]
            parts = [
                p.strip().strip("\"'")
                for p in text.replace("\n", ",").split(",")
                if p.strip()
            ]
            return parts if parts else ([] if text == "" else [text])
        if isinstance(raw_value, tuple | set):
            return [str(v).strip() for v in raw_value if str(v).strip()]
        return raw_value

    for list_key in list_like_keys:
        if list_key in normalized:
            normalized[list_key] = _to_string_list(normalized.get(list_key))

    cleaned: Dict[str, Any] = {}
    for key, value in normalized.items():
        if isinstance(value, str):
            value = value.strip()
            if value == "":
                continue
        elif isinstance(value, (list, tuple, set)):
            value = [v for v in value if v not in (None, "")]
            if len(value) == 0:
                continue
        if value is None:
            continue
        cleaned[key] = value

    return _canonical_param_names(cleaned)


# Run-parameter names that are aliases or rendering options rather than parameters of the report:
# consumed under another name, so never reported as dropped.
_RUN_PARAM_ALIASES = frozenset({
    "search_string", "filter_string", "property_value", "filter", "output_format", "report_spec",
    "graph_query_depth", "metadata_element_name", "limit_result_by_status", "sort_order",
    "output_sort_order", "order_property_name", "anchor_scope_id",
})


def _warn_dropped_params(report_name: str, params: Dict[str, Any], call_params: Dict[str, Any],
                         declared: Iterable[str]) -> None:
    """A caller's run parameter that the report does not take is dropped; say so (P3: never silent).

    Same warning class as an unknown filter on a method call (UnknownFilterWarning), plus a log line.
    """
    import warnings
    from pyegeria.core.request_filters import (DEPRECATED_NAMES, LEGACY_ALIASES, RENDER_OPTIONS,
                                               UnknownFilterWarning, _SKIP_PREFIXES)

    known = _RUN_PARAM_ALIASES | RENDER_OPTIONS | set(DEPRECATED_NAMES) | set(LEGACY_ALIASES)
    dropped = sorted(k for k in (params or {}) if k not in call_params and k not in known)
    if not dropped:
        return
    takes = ", ".join(sorted(set(declared))) or "no parameters"
    msg = (f"report '{report_name}': parameter(s) {', '.join(repr(k) for k in dropped)} ignored -- "
           f"not parameters of this report (it takes: {takes}). "
           f"(pyegeria will raise an error for unknown parameters in a future release.)")
    logger.warning(msg)
    warnings.warn(msg, UnknownFilterWarning, skip_file_prefixes=_SKIP_PREFIXES)


def _bind_search_parameter(func: Any, call_params: Dict[str, Any]) -> Dict[str, Any]:
    """Generated report specs always pass the user's text as `search_string`. A method that takes it
    as `property_value` instead (ClassificationExplorer.find_elements_by_property_value) gets it
    under that name."""
    try:
        names = inspect.signature(func).parameters
    except (TypeError, ValueError):
        return call_params
    if "search_string" in call_params and "search_string" not in names and "property_value" in names \
            and "property_value" not in call_params:
        out = dict(call_params)
        out["property_value"] = out.pop("search_string")
        return out
    return call_params


def _canonical_param_names(params: Dict[str, Any]) -> Dict[str, Any]:
    """Rename deprecated filter spellings (metadata_element_type_name, ...) to the canonical
    names, quietly: a report spec or Dr.Egeria parameter list is not the caller's code, so it
    should not trip the methods' DeprecationWarning. A canonical value already present wins."""
    from pyegeria.core.request_filters import DEPRECATED_NAMES, _canonical_value

    out = dict(params)
    for old, new in DEPRECATED_NAMES.items():
        if old in out:
            value = out.pop(old)
            if out.get(new) in (None, "", []):
                out[new] = _canonical_value(new, value)
    return out


def _extract_param_value(params: Dict[str, Any], param_name: str, action_mode: str = "generic") -> Any:
    """Get action parameter value with tolerance for known alias names."""
    if param_name in params:
        return params[param_name]

    search_aliases = ["search_string"]
    if action_mode == "get":
        search_aliases = ["search_string", "property_value"]

    alias_lookup = {
        "property_value": search_aliases,
        "search_string": ["property_value"],
        "filter_string": ["search_string", "property_value", "filter"],
        "filter": ["search_string", "property_value", "filter_string"],
        "metadata_element_type": ["metadata_element_type_name", "metadata_element_name"],
        "metadata_element_name": ["metadata_element_type", "metadata_element_type_name"],
        "metadata_element_subtypes": ["metadata_element_subtype_names"],
        "limit_results_by_status": ["limit_result_by_status"],
        "sequencing_order": ["sort_order", "output_sort_order"],
        "sequencing_property": ["order_property_name"],
        "anchor_scope_guid": ["anchor_scope_id"],
    }
    for alias in alias_lookup.get(param_name, []):
        if alias in params:
            return params[alias]
    return None


def _infer_action_mode(method_name: Optional[str]) -> str:
    base_name = (method_name or "").replace("_async_", "")
    if base_name.startswith("get_"):
        return "get"
    if base_name.startswith("find_"):
        return "find"
    return "generic"


def _merge_signature_params(func: Any, params: Dict[str, Any], call_params: Dict[str, Any]) -> Dict[str, Any]:
    """Add extra normalized params that the resolved function explicitly accepts."""
    try:
        sig = inspect.signature(func)
    except Exception:
        return call_params

    accepted = set(sig.parameters.keys())
    has_var_kw = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())

    merged = dict(call_params)
    for key, value in (params or {}).items():
        if key in {"output_format", "report_spec"}:
            continue
        if key in merged:
            continue
        if key in accepted or has_var_kw:
            merged[key] = value
    return merged


# Request options every find/get method understands but report specs don't list in
# their required/optional params. exec_report_spec only copies declared params, so
# without this a caller's graph_query_depth was silently dropped and every call ran
# at the SDK default depth of 3 -- the dominant cost of list calls (ISSUE-15).
_PASS_THROUGH_REQUEST_OPTIONS = ("graph_query_depth",)


def _add_request_options(func: Any, params: Dict[str, Any], call_params: Dict[str, Any]) -> Dict[str, Any]:
    """Forward _PASS_THROUGH_REQUEST_OPTIONS from the caller's params when the method accepts them."""
    try:
        sig = inspect.signature(func)
    except Exception:
        return call_params
    accepts_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
    merged = dict(call_params)
    for key in _PASS_THROUGH_REQUEST_OPTIONS:
        value = (params or {}).get(key)
        if value is not None and key not in merged and (key in sig.parameters or accepts_kwargs):
            merged[key] = value
    return merged


def _validate_report_spec_params(report_spec, params):
    """Validate that required parameters are present in the provided params dictionary."""
    missing_params = [param for param in report_spec.required_params if param not in params]
    if missing_params:
        raise PyegeriaException(f"Missing required parameters: {', '.join(missing_params)}")


async def safe_call_tool(func, **call_params):
    """
    Safely calls a function, awaiting it only if it is an asynchronous coroutine.
    """
    try:
        if asyncio.iscoroutinefunction(func):
            # If it's an async function, call it with await
            logger.debug("Function is async, using await.")
            result = await func(**call_params)
        else:
            # If it's a synchronous function, call it directly
            logger.debug("Function is sync, calling directly.")
            result = func(**call_params)

        return result

    except Exception as e:
        print(f"ERROR calling function: {e}", file=sys.stderr)
        raise



# Parameter naming note:
# - exec_report_spec and run_report expect parameter names in snake_case (e.g., metadata_element_subtypes).
# - The underlying clients map these to on-wire camelCase when serializing request bodies for Egeria.
def _with_spec_source(result: Any, name: Any, output_format: str) -> Any:
    """Add `spec_source` beside `kind` (never inside `data`) and, for an Egeria-held spec, the
    provenance footer on REPORT/MD/HTML text (RS-EGERIA-TIER §7a "Provenance")."""
    if not isinstance(result, dict) or not isinstance(name, str):
        return result
    from pyegeria.view.base_report_formats import add_spec_footer, report_spec_source
    try:
        source = report_spec_source(name)
    except Exception as exc:  # noqa: BLE001 -- provenance must never fail a run
        logger.debug(f"spec_source for {name!r} unavailable: {exc}")
        source = None
    if source is not None:
        result["spec_source"] = source
    if result.get("kind") == "text":
        result["content"] = add_spec_footer(result.get("content"), name, output_format)
    return result


async def _async_run_report(
    report_name: str,
    egeria_client: EgeriaTech,
    output_format: str = "DICT",
    params: Optional[Dict[str, Any]] = None,
    refresh_spec: bool = False,
    *,
    table_shape: Optional[str] = None,
    dict_shape: Optional[str] = None,
) -> Dict[str, Any]:
    """Run a report spec with an async EgeriaTech client (see `_async_run_report_impl`).

    `refresh_spec=True` fetches the spec from Egeria for this call (RS-EGERIA-TIER §7a); a failed
    fetch raises with words and never falls back to the cached copy. The result carries
    `spec_source` beside `kind`."""
    if refresh_spec:
        from pyegeria.view.egeria_spec_cache import async_fetch_spec_for_call
        report_name = await async_fetch_spec_for_call(egeria_client, report_name)
    result = await _async_run_report_impl(report_name, egeria_client, output_format=output_format, params=params,
                                          table_shape=table_shape, dict_shape=dict_shape)
    return _with_spec_source(result, report_name, output_format)


async def _async_run_report_impl(
    report_name: str,
    egeria_client: EgeriaTech,
    output_format: str = "DICT",
    params: Optional[Dict[str, Any]] = None,
    *,
    table_shape: Optional[str] = None,
    dict_shape: Optional[str] = None,
) -> Dict[str, Any]:
    """
        Execute the action for a given format set and return a normalized result structure.

        Returns shapes:
        - {"kind":"empty"}
        - {"kind":"json","data": <list|dict|any>}
        - {"kind":"text","mime": "text/markdown"|"text/html","content": str}
        - {"kind":"unknown","raw": any}
        """
    params = coerce_paging_params(dict(params or {}))
    row_shape = _row_shape(str(output_format or "DICT").upper(), table_shape, dict_shape)
    user_name = egeria_client.user_id
    user_pwd = egeria_client.user_pwd

    # SD-1: DOCUMENT specs run through exec_report_spec (the analytic/role-supply path), which
    # this find-only async path does not have. Refuse in words rather than fail inside it.
    if str(output_format).upper() == DOCUMENT_OUTPUT_TYPE or _document_spec_struct(report_name) is not None:
        raise ValueError(
            f"Report spec '{report_name}' ({output_format}): DOCUMENT output runs through exec_report_spec "
            f"(output_format='DOCUMENT'), not the async find path")

    # Resolve the format set and action
    effective_format = "REPORT" if output_format in ["HTML", "MARKDOWN"] else output_format
    if effective_format == "JSON":
        effective_format = "DICT"

    # First, check if the report spec exists at all (independent of type)
    fmt_any = select_report_spec(report_name, "ANY")
    if not fmt_any:
        raise ValueError(
            f"Unknown report spec '{report_name}'. Run 'list_reports' to see available reports."
        )

    # Then, check if the requested output format is supported
    fmt = select_report_spec(report_name, effective_format)
    if not fmt:
        # Try to collect available types for a clearer message
        available: list[str] = []
        try:
            registry = get_report_registry()
            fs = registry.get(report_name)
            if fs is None:
                for key, v in registry.items():
                    aliases = getattr(v, "aliases", []) or []
                    if report_name in aliases:
                        fs = v
                        break
            if fs is not None:
                seen = set()
                for f in getattr(fs, "formats", []) or []:
                    for t in getattr(f, "types", []) or []:
                        seen.add(str(t).upper())
                available = sorted(seen)
        except Exception:
            pass
        hint = f" Available formats: {', '.join(available)}." if available else ""
        raise ValueError(
            f"Report spec '{report_name}' does not support requested output_format '{output_format}'.{hint} "
            f"Run 'list_reports' to see available reports."
        )

    if "action" not in fmt:
        raise ValueError(f"Output format set '{report_name}' does not have an action property.")

    safe_target_type = _resolve_report_target_type(fmt, report_name)

    action = fmt["action"]
    func_decl = action.get("function")
    method_name = None
    if isinstance(func_decl, str) and "." in func_decl:
        class_name, method_name = func_decl.split(".")
        if not method_name.startswith("_async_"):
            method_name = "_async_" + method_name
            func_decl = class_name + "." + method_name
    else:
        raise ValueError(f"Invalid action function declaration for report '{report_name}': {func_decl!r}")

    required_params = action.get("required_params", action.get("user_params", [])) or []
    optional_params = action.get("optional_params", []) or []
    spec_params = action.get("spec_params", {}) or {}
    action_mode = _infer_action_mode(method_name)
    params = _normalize_report_params(params, action_mode=action_mode)
    # Build call params: required/optional provided by caller + fixed spec_params
    call_params: Dict[str, Any] = {}
    missing_required: list[str] = []

    # Populate required and optional params when provided
    for p in required_params:
        value = _extract_param_value(params, p, action_mode=action_mode)
        if value is not None:
            call_params[p] = value
        elif p not in spec_params:
            # Missing required param — collect for a single clear error
            missing_required.append(p)
            logger.warning(f"Required parameter '{p}' not provided for format set '{report_name}'.")

    if missing_required:
        raise ValueError(
            f"Report '{report_name}' requires the following parameter(s) that were not provided: "
            f"{', '.join(missing_required)}. Please add them to your command."
        )

    for p in optional_params:
        value = _extract_param_value(params, p, action_mode=action_mode)
        if value is not None:
            call_params[p] = value

    # Include fixed specifics
    call_params.update(spec_params)
    call_params = _canonical_param_names(call_params)

    # Always include output_format and report_spec for downstream rendering
    call_params["output_format"] = output_format
    call_params["report_spec"] = report_name

    client_class, method_name = _resolve_client_and_method(func_decl)
    target_client = _resolve_action_target_client(egeria_client, client_class)


    try:
        func = getattr(target_client, method_name) if method_name and hasattr(target_client, method_name) else None
        # Add logging to validate func
        msg = f"func={func}, method_name={method_name}, client_class={client_class}, target_client={type(target_client)}"
        logger.debug(msg)

        if func is None or not callable(func):
            raise TypeError(
                f"Resolved function '{method_name}'  not found in client class '{client_class.__name__}' is not callable."
            )

        call_params = _merge_signature_params(func, params, call_params)
        call_params = _bind_search_parameter(func, call_params)
        _warn_dropped_params(report_name, params, call_params,
                             [*required_params, *optional_params, *spec_params])
        # Only (re)create a bearer token if one is not already set on the client.
        try:
            existing_token = None
            if hasattr(egeria_client, "get_token"):
                existing_token = egeria_client.get_token()
            if not existing_token:
                logger.debug("No existing bearer token; attempting async creation...")
                if user_name and user_pwd:
                    await egeria_client._async_create_egeria_bearer_token(user_name, user_pwd)
                else:
                    logger.debug("Missing credentials; skipping token creation and relying on pre-initialized token.")
            else:
                logger.debug("Using existing bearer token.")
        except Exception as auth_err:
            # Do not fail the entire call if token refresh fails; downstream call may still work
            logger.debug(f"Token creation/lookup issue: {auth_err}")
        with recording_list_requests() as list_record, dict_shape_for_call(row_shape):
            result = await func(**call_params)

        if not result or result == NO_ELEMENTS_FOUND:
            return {"kind": "empty"}
        cap_notes = page_cap_notes(func, call_params, result, list_record)

        if output_format == "TABLE" and table_shape == "structured":
            return build_structured_table(result, (fmt.get("formats") or {}).get("attributes") or [],
                                          notes=cap_notes, capped=bool(cap_notes), record=list_record)
        if output_format == "DICT" and row_shape == "native" and isinstance(result, list):
            cap_notes = cap_notes + mark_relationship_absence(  # "none" / "not read" (R1 follow-up)
                result, [c if isinstance(c, dict) else c.model_dump()
                         for c in (fmt.get("formats") or {}).get("attributes") or []], list_record, keyed_by="name")
        if output_format in {"DICT", "JSON", "ALL", "TABLE"}:
            # Return raw data (list/dict/any) — do not stringify here; include TABLE to enable Rich rendering upstream
            return {"kind": "json", "data": result, **({"notes": cap_notes} if cap_notes else {})}

        # For narrative formats, try to use generate_output if the result is structured
        if output_format in {"REPORT", "REPORT-GRAPH", "MD", "FORM", "LIST", "HTML", "MERMAID", "GRAPH"}:
            if isinstance(result, (list, dict)):
                result = generate_output(
                    elements=result,
                    search_string=call_params.get("search_string")
                    or call_params.get("filter_string")
                    or "All",
                    entity_type=safe_target_type,
                    output_format=output_format,
                    columns_struct=fmt,
                )

            # If it's already a string, it might have its own preamble. 
            # We only add our preamble if it doesn't look like it has one.
            heading = get_report_spec_heading(report_name)
            desc = get_report_spec_description(report_name)
            preamble = f"# {heading}\n{desc}\n\n" if heading and desc else ""
            
            content = str(result)
            if preamble and not content.strip().startswith("#"):
                content = preamble + content

            mime = "text/html" if output_format in ["HTML", "GRAPH"] else "text/markdown"
            if cap_notes:  # fix-now F8: a capped result says so in the text too
                content = content.rstrip("\n") + "\n\n" + "\n".join(
                    (f"<p><em>{n}</em></p>" if mime == "text/html" else f"_{n}_") for n in cap_notes) + "\n"
            return {"kind": "text", "mime": mime, "content": content,
                    **({"notes": cap_notes} if cap_notes else {})}

        return {"kind": "unknown", "raw": result}

    except PyegeriaException as e:
        # Re-raise with a simpler message for upstream mapping
        raise
    except ValidationError as e:
        print_validation_error(e)
        raise



def _exec_analytic_chart(
    format_set_name: str,
    *,
    chart_kind: str,
    params: Dict[str, Any],
    view_server: str,
    view_url: str,
    user: str,
    user_pass: str,
    token: Optional[str] = None,
    supply: Optional[RoleSupply] = None,
) -> Dict[str, Any]:
    """Run a report spec's `analytic_function` (extra_find) and wrap the
    result as a Vega-Lite chart -- `chart_kind` picks which:

    - "line": a time series -- List[Dict] of {label, date, <metric>: value, ...}
      points, one line per metric key (e.g. growth_series).
    - "bar"/"pie": a flat category breakdown -- either a plain
      {category: value} dict (e.g. governed_coverage's byClassification), or
      a List[Dict] with one label-like field and exactly one numeric field
      (e.g. counts_by_type's [{label, type, count}, ...]).

    Falls back to returning the raw result (`{"kind":"json","data":...}`,
    same as the plain DICT/JSON analytic path) if the result doesn't match
    the requested chart_kind's expected shape, rather than raising --
    picking a chart output_format is a rendering *preference*, not a
    contract every analytic function's result shape can satisfy.
    """
    from pyegeria.view.vega_utilities import generate_vega_line_chart, generate_vega_bar_chart, generate_vega_pie_chart

    fmt_any = select_report_spec(format_set_name, "ANY")
    if not fmt_any:
        raise ValueError(f"Unknown report spec '{format_set_name}'. Run 'list_reports' to see available reports.")
    if "action" not in fmt_any:
        raise ValueError(f"Report spec '{format_set_name}' does not have an action property.")

    action = fmt_any["action"]
    if not action.get("analytic_function"):
        raise ValueError(
            f"Report spec '{format_set_name}' has no analytic_function (extra_find) -- "
            f"{chart_kind.upper()} output isn't supported for this spec."
        )

    result, notes = _run_recording_unmeasured(
        action, params=params, view_server=view_server, view_url=view_url,
        user=user, user_pass=user_pass, token=token, supply=supply,
    )
    envelope = _result_envelope(result)
    result = _jsonable(result)
    # W2 (6.2.34): a trend whose only unmeasured points are lower bounds is drawn, each bound
    # plotted at its bound and labelled "≥N", with a subtitle saying how many there are.
    bounded = _bounded_trend(result) if chart_kind == "line" and notes else None
    # A count in the result was not measured: its value is None, and a chart would draw that as
    # a missing bar, a gap or a re-proportioned pie. Withhold the chart and say why instead.
    if notes and bounded is None and (envelope is None or envelope["state"] in CHARTABLE_STATES):
        envelope = _unmeasured_envelope(notes)
    absence = _absence_for(envelope, action["analytic_function"])
    # Chart only an established answer (ISSUE-140): measured, or nothing_found (a real
    # zero). For not_established / not_applicable the numbers aren't known, so say so
    # (ISSUE-171), never a chart whose zeros would read as an answer.
    if envelope and envelope["state"] not in CHARTABLE_STATES:
        return _absent_output(result, envelope, absence, notes)
    if not result:
        return _with_envelope({"kind": "empty", **({"absence": absence} if absence else {})}, envelope)

    try:
        heading = get_report_spec_heading(format_set_name) or str(format_set_name)
    except Exception:  # noqa: BLE001 -- registry lookup quirks shouldn't block chart rendering
        heading = str(format_set_name)

    def _chart_out(chart):
        if not chart:
            return _with_envelope({"kind": "json", "data": result}, envelope)
        if envelope:  # the state rides on the chart itself (ISSUE-139)
            subtitle = absence["sentence"] if absence and absence["declared"] else envelope["subtitle"]
            chart["title"] = {"text": chart.get("title") or heading, "subtitle": subtitle}
        out = {"kind": "json", "data": chart, **({"absence": absence} if absence else {})}
        return _with_envelope(out, envelope)

    if chart_kind == "line" and bounded is not None:
        records, n_bounds = bounded
        chart = generate_vega_line_chart(records, x_field="label", y_fields=["value"], title=heading,
                                         x_label="Label", y_label="Count")
        if not chart:
            return _with_envelope({"kind": "json", "data": result}, envelope)
        chart = _mark_lower_bounds(chart)
        chart["title"] = {"text": heading, "subtitle": (
            f"{n_bounds} of {len(records)} points are lower bounds (shown as \u2265N): "
            f"the count stopped at its page cap")}
        return {"kind": "json", "data": chart, "unmeasured": notes,
                **({"absence": absence} if absence else {})}

    if chart_kind == "line":
        if not isinstance(result, list) or not all(isinstance(pt, dict) for pt in result):
            return _with_envelope({"kind": "json", "data": result}, envelope)
        x_field = "label" if any("label" in pt for pt in result) else "date"
        y_fields = sorted({
            k for pt in result for k, v in pt.items()
            if k not in ("label", "date") and isinstance(v, (int, float)) and not isinstance(v, bool)
        })
        if not y_fields:
            return _with_envelope({"kind": "json", "data": result}, envelope)
        chart = generate_vega_line_chart(
            result, x_field=x_field, y_fields=y_fields,
            title=heading, x_label=x_field.capitalize(), y_label="Count",
        )
        return _chart_out(chart)

    # bar / pie -- both need a plain {category: numeric_value} mapping
    cat_values = _as_category_value_dict(result)
    if not cat_values:
        return _with_envelope({"kind": "json", "data": result}, envelope)
    chart = (generate_vega_bar_chart(cat_values, title=heading) if chart_kind == "bar"
             else generate_vega_pie_chart(cat_values, title=heading))
    return _chart_out(chart)


def _bounded_trend(result: Any) -> Optional[Tuple[List[Dict[str, Any]], int]]:
    """A scalar `metric_trend` series whose every inexact point is a lower bound: the records to
    plot (a bound at its bound, flagged `lowerBound`, with its `display` "≥N") and how many bounds.
    None for anything else, so the caller withholds the chart as before."""
    if not isinstance(result, list) or not result:
        return None
    records, n_bounds = [], 0
    for pt in result:
        m = pt.get("measurement") if isinstance(pt, dict) else None
        if not isinstance(m, dict) or "display" not in pt:
            return None  # not a scalar metric_trend point
        if m.get("exact") and isinstance(pt.get("value"), (int, float)):
            records.append({"label": pt.get("label"), "date": pt.get("date"), "value": pt["value"],
                            "display": pt["display"], "lowerBound": False})
        elif m.get("capped") and m.get("at_least") is not None and m.get("how") != "error":
            n_bounds += 1
            records.append({"label": pt.get("label"), "date": pt.get("date"), "value": m["at_least"],
                            "display": pt["display"], "lowerBound": True})
        else:
            return None  # a point with no number at all: no chart
    return (records, n_bounds) if n_bounds else None


def _mark_lower_bounds(chart: Dict[str, Any]) -> Dict[str, Any]:
    """Layer a "≥N" label over every lower-bound point, and show `display` in the tooltip, so a
    bound is never read as an exact number."""
    line = {k: chart.pop(k) for k in ("mark", "encoding")}
    line["mark"] = {"type": "line", "point": True}
    line["encoding"]["tooltip"] = [{"field": "label", "type": "nominal"},
                                   {"field": "display", "type": "nominal", "title": "Count"}]
    label = {"transform": [{"filter": "datum.lowerBound"}],
             "mark": {"type": "text", "dy": -10},
             "encoding": {"x": line["encoding"]["x"], "y": line["encoding"]["y"],
                          "text": {"field": "display", "type": "nominal"}}}
    chart["layer"] = [line, label]
    return chart


def _as_category_value_dict(result: Any) -> Optional[Dict[str, Union[int, float]]]:
    """Coerce an analytic result into {category: numeric_value} for a bar/pie
    chart, or None if it doesn't fit that shape. Handles two real shapes:
    a plain dict already in that form (numeric values only -- non-numeric
    entries are dropped rather than disqualifying the whole dict, e.g.
    governed_coverage's topZones sits alongside byClassification), and a
    list[dict] with one label-like field plus exactly one numeric field
    (e.g. counts_by_type's [{label, type, count}, ...])."""
    if isinstance(result, dict):
        numeric = {str(k): v for k, v in result.items()
                   if isinstance(v, (int, float)) and not isinstance(v, bool)}
        if len(numeric) >= 2:
            return numeric
        # Fewer than 2 top-level numeric fields isn't a meaningful bar/pie (a
        # single bar/slice) -- prefer a nested dict-of-numerics breakdown
        # instead, e.g. governed_coverage's byClassification or
        # feedback_summary's byType, which is usually what "chart this" means
        # for a summary dict whose interesting content is one level down.
        for v in result.values():
            if isinstance(v, dict):
                nested = {str(k): v2 for k, v2 in v.items()
                          if isinstance(v2, (int, float)) and not isinstance(v2, bool)}
                if len(nested) >= 2:
                    return nested
        return numeric or None
    if isinstance(result, list) and result and all(isinstance(r, dict) for r in result):
        sample = result[0]
        label_key = "label" if "label" in sample else next(
            (k for k, v in sample.items() if isinstance(v, str)), None)
        numeric_keys = [k for k, v in sample.items()
                         if isinstance(v, (int, float)) and not isinstance(v, bool)]
        if label_key and len(numeric_keys) == 1:
            value_key = numeric_keys[0]
            return {str(r.get(label_key)): r.get(value_key) for r in result if r.get(label_key) is not None}
    return None


def _effective_page_size(func: Any, call_params: Dict[str, Any]) -> Optional[int]:
    """The page size a find call ran with: the one sent, else the find function's own default
    (e.g. find_digital_products' page_size=100). None when neither is a positive whole number (the
    server then chose, and pyegeria cannot know its cap)."""
    sent = call_params.get("page_size")
    if isinstance(sent, int) and sent > 0:
        return sent
    try:
        default = inspect.signature(func).parameters["page_size"].default
    except (KeyError, TypeError, ValueError):
        return None
    return default if isinstance(default, int) and default > 0 else None


def _cap_words(shown: int, size: int, start: int) -> str:
    first = f"rows {start + 1}-{start + shown}" if start else f"the first {shown}"
    return f"Showing {first}: the query stopped at its page size of {size}; more may exist."


def page_cap_notes(func: Any, call_params: Dict[str, Any], result: Any,
                   record: Optional[Dict[str, Any]] = None) -> List[str]:
    """Fix-now F8: a find result that filled its page says so, never a bare N. Egeria's paging
    contract means a full page may or may not be the last, so the words are "more may exist".

    `record` is this call's own list-request record (`recording_list_requests`), which covers a find
    method that renders text itself; a plain list result is checked against the page size sent (or the
    find function's own default) as well. No state is read from the client (read-back C1)."""
    cap = (record or {}).get("cap")
    if cap:
        shown, size, start = cap
        return [_cap_words(shown, size, start)]
    size = _effective_page_size(func, call_params)
    if isinstance(result, list) and size and len(result) >= size:
        return [_cap_words(len(result), size, call_params.get("start_from") or 0)]
    return []


_PAGING_PARAMS = ("page_size", "start_from")


def coerce_paging_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """page_size/start_from as whole numbers (fix-now F8): a numeric string is converted, anything else
    is refused in words rather than sent to Egeria (where it failed as an HTTP 500)."""
    for name in _PAGING_PARAMS:
        value = params.get(name)
        if value in (None, ""):
            continue
        if isinstance(value, bool):
            raise ValueError(f"{name} must be a whole number of 0 or more, not {value!r}")
        try:
            number = int(str(value).strip()) if not isinstance(value, int) else value
        except ValueError:
            raise ValueError(f"{name} must be a whole number of 0 or more, not {value!r}") from None
        if number < 0:
            raise ValueError(f"{name} must be a whole number of 0 or more, not {value!r}")
        params[name] = number
    return params


def _row_shape(output_format: str, table_shape: Optional[str], dict_shape: Optional[str]) -> str:
    """The DICT row shape a find call runs with (R1): "native" for DICT + dict_shape="native" and for
    TABLE + table_shape="structured", else "flat" (TABLE stays flat under dict_shape: its structured
    form is table_shape). Unknown values are refused with a sentence."""
    table_shape = check_table_shape(table_shape)
    dict_shape = check_dict_shape(dict_shape)
    if output_format == "DICT" and dict_shape == "native":
        return "native"
    if output_format == "TABLE" and table_shape == "structured":
        return "native"
    return "flat"


def _spec_display_name(format_set_name: Any) -> str:
    if isinstance(format_set_name, dict):
        return str(format_set_name.get("_report_spec_name") or format_set_name.get("heading") or "?")
    return str(format_set_name)


def _document_spec_struct(format_set_name: Any) -> Optional[Dict[str, Any]]:
    """The selected-spec struct (as `select_report_spec` returns it) when this spec is a DOCUMENT
    spec, else None. A spec passed as a dict is read as given (a FormatSet dict or a selected
    struct); by name it is looked up across tiers and aliases."""
    if isinstance(format_set_name, dict):
        formats = format_set_name.get("formats")
        rows = formats if isinstance(formats, list) else [formats] if formats else []
        for row in rows:
            row = row.dict() if hasattr(row, "dict") and not isinstance(row, dict) else row
            if isinstance(row, dict) and row.get("document"):
                struct = dict(format_set_name)
                struct["formats"] = row
                action = struct.get("action")
                if action is not None and not isinstance(action, dict):
                    struct["action"] = action.model_dump()
                return struct
        return None
    try:
        struct = select_report_spec(format_set_name, DOCUMENT_OUTPUT_TYPE)
    except Exception:  # noqa: BLE001 -- an unknown name is reported by the normal path below
        return None
    if struct and isinstance(struct.get("formats"), dict) and struct["formats"].get("document"):
        return struct
    return None


_FILE_NAME_UNSAFE = re.compile(r"[^A-Za-z0-9._+-]+")


def fill_document_file_name(template: str, params: Dict[str, Any]) -> str:
    """Fill a DOCUMENT file-name template from the run's parameters.

    A field is a plain parameter name, or alternatives separated by `|` (6.2.38): `{scope|search_string}`
    takes the first one the run supplies, so one template serves an exporter that takes either. Nothing
    else is allowed (no attribute or index access, no format spec). Each value is made file-name safe
    (anything but letters, digits and `._+-` becomes `_`, and `..` is broken up), so a qualifiedName such
    as `Folder::Sales/EU` cannot become a path. The result is checked again; a template that still names
    a path, or a field none of whose parameters the run supplied, is refused with a sentence."""
    out: List[str] = []
    for literal, field, spec, conversion in string.Formatter().parse(template):
        out.append(literal)
        if field is None:
            continue
        names = field.split("|")
        if not all(n.isidentifier() for n in names):
            raise ValueError(f"DOCUMENT file_name template '{template}' has field '{{{field}}}'; only plain "
                             f"parameter names (or alternatives a|b) are allowed")
        if spec or conversion:
            raise ValueError(f"DOCUMENT file_name template '{template}' formats field '{field}'; only plain "
                             f"parameter names are allowed")
        raw = next((params.get(n) for n in names if params.get(n) not in (None, "")), None)
        if raw is None:
            wanted = f"parameter '{names[0]}'" if len(names) == 1 else "one of the parameters " + ", ".join(
                f"'{n}'" for n in names)
            raise ValueError(f"DOCUMENT file_name template '{template}' needs {wanted}, which this run did not "
                             f"supply")
        out.append(_FILE_NAME_UNSAFE.sub("_", str(raw)).replace("..", "_").strip("._") or "_")
    file_name = "".join(out)
    reason = check_document_file_name(file_name)
    if reason:
        raise ValueError(f"DOCUMENT file_name refused: {reason}")
    return file_name


def _exec_document(
    name: str, struct: Dict[str, Any], *, params: Dict[str, Any],
    view_server: str, view_url: str, user: str, user_pass: str,
    token: Optional[str] = None, supply: Optional[RoleSupply] = None,
) -> Dict[str, Any]:
    """Run a DOCUMENT spec (SD-1): call its exporter, validate what it returns, and return

    {"kind": "document", "standard", "media_type", "file_name", "text",
     "validation": {"state", "validator", "findings", "reason"}, "notes": [...]}

    The exporter is the action's analytic function; it returns `{"text": str, "notes"?: [str]}`
    (or a plain string, read as text with no notes). `validation` and `notes` are always present:
    an empty `notes` means the exporter had nothing to say about the document's content. A
    validator that raises leaves the document `not_validated` with its error, never `invalid`.
    """
    action = struct.get("action") or {}
    if not action.get("analytic_function"):
        raise ValueError(f"Report spec '{name}' has a DOCUMENT format but no analytic_function (exporter)")
    doc = struct["formats"]["document"]
    fill_from = {**(action.get("analytic_spec_params") or {}),
                 **{k: v for k, v in params.items() if v not in (None, "")}}
    file_name = fill_document_file_name(doc["file_name"], fill_from)

    result = _run_analytic_function(action, params=params, view_server=view_server, view_url=view_url,
                                    user=user, user_pass=user_pass, token=token, supply=supply)
    if isinstance(result, str):
        text, notes = result, []
    elif isinstance(result, dict) and isinstance(result.get("text"), str):
        text = result["text"]
        raw_notes = result.get("notes") or []
        notes = [str(n) for n in (raw_notes if isinstance(raw_notes, list) else [raw_notes])]
    else:
        raise ValueError(
            f"Report spec '{name}': exporter '{action['analytic_function']}' returned "
            f"{type(result).__name__}, not a document ({{'text': str, 'notes'?: [str]}})")
    validation = run_document_validator(text, doc["media_type"], doc.get("validator"),
                                        doc.get("validator_options") or {})
    return {"kind": "document", "standard": doc["standard"], "media_type": doc["media_type"],
            "file_name": file_name, "text": text, "validation": validation, "notes": notes}


def exec_report_spec(
    format_set_name: str | dict,
    *,
    output_format: str = "DICT",
    params: Optional[Dict[str, Any]] = None,
    view_server: str = settings.Environment.egeria_view_server,
    view_url: str = settings.Environment.egeria_view_server_url,
    user: str = settings.User_Profile.user_name,
    user_pass: str = settings.User_Profile.user_pwd,
    token: Optional[str] = None,
    supply: Optional[RoleSupply] = None,
    refresh_spec: bool = False,
    table_shape: Optional[str] = None,
    dict_shape: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute the action for a given report spec (see `_exec_report_spec_impl` for the result
    shapes).

    R1: `table_shape="structured"` with output_format TABLE returns the structured table
    (`pyegeria.view.structured_table`, `kind: "table"`); `dict_shape="native"` with DICT returns rows
    with native values. Both are caller flags; the defaults ("rows", "flat") return today's shapes, and
    any other value is refused with a sentence. They apply to a find-method spec only: DOCUMENT, chart
    and analytic results ignore them.

    RS-EGERIA-TIER: the name may be tier-addressed (`egeria:<label>`, `builtin:<label>`,
    `seed:<label>`). The result carries `spec_source` (`{"tier", "label", "version", "guid"?,
    "synced_at"?}`) beside `kind`, never inside `data`; REPORT/MD/HTML text of an Egeria-held spec
    ends with a one-line provenance footer. `refresh_spec=True` fetches the spec from Egeria for
    this call: written through to a per-user cache, kept in-process for a shared one. A failed
    fetch raises with words; it never falls back to the cached copy.
    """
    if refresh_spec and isinstance(format_set_name, str):
        format_set_name = _fetch_for_exec(format_set_name, view_server=view_server, view_url=view_url,
                                          user=user, user_pass=user_pass, token=token)
    result = _exec_report_spec_impl(format_set_name, output_format=output_format, params=params,
                                    view_server=view_server, view_url=view_url, user=user, user_pass=user_pass,
                                    token=token, supply=supply, table_shape=table_shape, dict_shape=dict_shape)
    return _with_spec_source(result, format_set_name, (output_format or "DICT").upper())


def _fetch_for_exec(name: str, *, view_server: str, view_url: str, user: str, user_pass: str,
                    token: Optional[str]) -> str:
    from pyegeria.omvs.collection_manager import CollectionManager
    from pyegeria.view.egeria_spec_cache import fetch_spec_for_call
    client = CollectionManager(view_server, view_url, user_id=user, user_pwd=user_pass)
    try:
        if token:
            client.set_bearer_token(token)
        else:
            client.create_egeria_bearer_token()
        return fetch_spec_for_call(client, name)
    finally:
        try:
            client.close_session()
        except Exception:  # noqa: BLE001
            pass


def _exec_report_spec_impl(
    format_set_name: str | dict,
    *,
    output_format: str = "DICT",
    params: Optional[Dict[str, Any]] = None,
    view_server: str = settings.Environment.egeria_view_server,
    view_url: str = settings.Environment.egeria_view_server_url,
    user: str = settings.User_Profile.user_name,
    user_pass: str = settings.User_Profile.user_pwd,
    token: Optional[str] = None,
    supply: Optional[RoleSupply] = None,
    table_shape: Optional[str] = None,
    dict_shape: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute the action for a given format set and return a normalized result structure.

    Returns shapes:
    - {"kind":"empty"}
    - {"kind":"json","data": <list|dict|any>}
    - {"kind":"text","mime": "text/markdown"|"text/html","content": str}
    - {"kind":"unknown","raw": any}

    An analytic result that carries a state envelope (ISSUE-139) also gets
    `"envelope": {"state", "reason", "subtitle"}` on any of these shapes. For
    SERIES/BAR/PIE the subtitle is put on the chart, and no chart is drawn
    unless the state is `measured` or `nothing_found` (ISSUE-140).

    A count inside an analytic result that was not measured -- it failed, timed out, or its
    find fallback stopped at the page cap, which is a lower bound and never a total -- is
    None in the data, never 0 or the cap, and the output carries `"unmeasured": [{"count",
    "reason", "at_least"}, ...]` naming each one. A scalar result that is such a count, and
    any SERIES/BAR/PIE whose result holds one, come back as `kind: "absent"` (no chart: a
    missing bar or a re-proportioned pie would read as an answer), with the reason and the
    lower bound in `content`.

    ISSUE-86: `token`, when given, authenticates the client(s) built here with
    `set_bearer_token(token)` instead of minting a fresh token from
    `user`/`user_pass` via `create_egeria_bearer_token()`. Use this when the
    caller already holds a bearer token for the calling user (e.g. an app
    whose session carries the user's Egeria token, not their password) so
    report execution -- and its provenance -- reflects that user, not a
    fallback service account. `user`/`user_pass` remain fully backward
    compatible when `token` is not given.

    RS-W2-3: `supply` (a `role_supply.RoleSupply`) provides an analytic routine's declared inputs
    -- its Egeria client(s), and any reader, viewer or subject it declares. Omitted, plain
    pyegeria's `PlainSupply` is built from the arguments above and supplies the caller's
    EgeriaTech only. A role the supply cannot provide raises `role_supply.RoleRefused`, with the
    environment's words, before the routine runs. A find-method spec (no analytic routine) does
    not read `supply`: it builds its client class from the arguments above, as before.
    """
    output_format = (output_format or "DICT").upper()
    params = coerce_paging_params(_normalize_report_params(dict(params or {}), action_mode="find"))
    row_shape = _row_shape(output_format, table_shape, dict_shape)

    # SERIES/BAR/PIE are not Format-row output types like TABLE/DICT/REPORT --
    # they don't need per-column formatting at all, just the analytic
    # function's already-aggregated result wrapped as the corresponding
    # Vega-Lite chart. Dispatch before the normal Format-row lookup (which
    # would reject them as unsupported, since no FormatSet declares a
    # "SERIES"/"BAR"/"PIE" Format row).
    # DOCUMENT (SD-1): a document spec answers only DOCUMENT, and DOCUMENT is answered only by a
    # document spec. Checked before the chart dispatch so SERIES/BAR/PIE are refused too.
    doc_struct = _document_spec_struct(format_set_name)
    if doc_struct is not None or output_format == DOCUMENT_OUTPUT_TYPE:
        name = _spec_display_name(format_set_name)
        if doc_struct is None:
            raise ValueError(
                f"Report spec '{name}' does not produce a document: DOCUMENT output is only for a spec "
                f"with a DOCUMENT format (an exporter). Run 'list_reports' to see available reports.")
        if output_format != DOCUMENT_OUTPUT_TYPE:
            doc = doc_struct["formats"]["document"]
            raise ValueError(
                f"Report spec '{name}' is a DOCUMENT spec: it produces one {doc['standard']} document "
                f"({doc['media_type']}), not {output_format}. Ask for output_format DOCUMENT.")
        return _exec_document(
            name, doc_struct, params=params, view_server=view_server, view_url=view_url, user=user,
            user_pass=user_pass, token=token, supply=supply)

    _CHART_KINDS = {"SERIES": "line", "BAR": "bar", "PIE": "pie"}
    if output_format in _CHART_KINDS:
        return _exec_analytic_chart(
            format_set_name, chart_kind=_CHART_KINDS[output_format], params=params,
            view_server=view_server, view_url=view_url, user=user, user_pass=user_pass,
            token=token, supply=supply,
        )

    # Resolve the format set and action
    if isinstance(format_set_name, dict):
        fmt = format_set_name
    else:
        # First, validate existence regardless of type
        fmt_any = select_report_spec(format_set_name, "ANY")
        if not fmt_any:
            raise ValueError(
                f"Unknown report spec '{format_set_name}'. Run 'list_reports' to see available reports."
            )
        fmt = select_report_spec(format_set_name, output_format)

    if not fmt:
        # Provide a clearer unsupported-format message with available types
        available: list[str] = []
        try:
            registry = get_report_registry()
            fs = registry.get(format_set_name)
            if fs is None:
                for key, v in registry.items():
                    aliases = getattr(v, "aliases", []) or []
                    if format_set_name in aliases:
                        fs = v
                        break
            if fs is not None:
                seen = set()
                for f in getattr(fs, "formats", []) or []:
                    for t in getattr(f, "types", []) or []:
                        seen.add(str(t).upper())
                available = sorted(seen)
        except Exception:
            pass
        hint = f" Available formats: {', '.join(available)}." if available else ""
        raise ValueError(
            f"Report spec '{format_set_name}' does not support requested output_format '{output_format}'.{hint} "
            f"Run 'list_reports' to see available reports."
        )

    if "action" not in fmt:
        raise ValueError(f"Output report spec '{format_set_name}' does not have an action property.")

    safe_target_type = _resolve_report_target_type(fmt, str(format_set_name))

    action = fmt["action"]
    func_decl = action.get("function")

    # Analytic-only report spec (no find_method -- e.g. an Overview-style KPI
    # backed by an overview_metrics function that returns a scalar/dict, not a
    # list of elements to format). SERIES is handled above via the dedicated
    # chart-wrapping path; this covers every other output_format (DICT/JSON/
    # TABLE/...) by just running the analytic function and returning its
    # result as-is -- there's no element list here to run through
    # generate_output's column formatting. A spec with BOTH a real find_method
    # and an analytic_function (the "supports both" case the ActionParameter
    # docstring describes) still falls through to the find path below for
    # anything other than SERIES, unchanged.
    if action.get("analytic_function") and not func_decl:
        result, notes = _run_recording_unmeasured(
            action, params=params, view_server=view_server, view_url=view_url,
            user=user, user_pass=user_pass, token=token, supply=supply,
        )
        envelope = _result_envelope(result)
        result = _jsonable(result)
        # The value itself is a count that was not measured (a scalar None): say so, with the
        # reason and any lower bound, never "empty". A dict or list keeps its measured values;
        # its unmeasured ones are None and the notes below name each one.
        if notes and envelope is None and result is None:
            envelope = _unmeasured_envelope(notes)
        unmeasured = {"unmeasured": notes} if notes else {}
        absence = _absence_for(envelope, action["analytic_function"])
        if envelope and envelope["state"] not in CHARTABLE_STATES:
            return _absent_output(result, envelope, absence, notes)  # ISSUE-171
        extra = {"absence": absence} if absence else {}
        if result is None or result == [] or result == {}:
            return _with_envelope({"kind": "empty", **extra, **unmeasured}, envelope)
        return _with_envelope({"kind": "json", "data": result, **extra, **unmeasured}, envelope)

    required_params = action.get("required_params", action.get("user_params", [])) or []
    optional_params = action.get("optional_params", []) or []
    spec_params = action.get("spec_params", {}) or {}

    # Build call params: required/optional provided by caller + fixed spec_params
    call_params: Dict[str, Any] = {}

    # Populate required and optional params when provided
    for p in required_params:
        value = _extract_param_value(params, p, action_mode="find")
        if value is not None:
            call_params[p] = value
        elif p not in spec_params:
            # Missing required param
            logger.warning(f"Required parameter '{p}' not provided for report spec '{format_set_name}'.")
    for p in optional_params:
        value = _extract_param_value(params, p, action_mode="find")
        if value is not None:
            call_params[p] = value

    # Include fixed specifics
    call_params.update(spec_params)
    call_params = _canonical_param_names(call_params)

    # Always include output_format and report_spec for downstream rendering
    call_params["output_format"] = output_format
    call_params["report_spec"] = format_set_name

    client_class, method_name = _resolve_client_and_method(func_decl)
    client = client_class(view_server, view_url, user_id=user, user_pwd=user_pass)

    try:
        if token:
            client.set_bearer_token(token)
        else:
            client.create_egeria_bearer_token()
        func = getattr(client, method_name) if method_name and hasattr(client, method_name) else None
        if func is None:
            raise AttributeError(
                f"Method '{method_name}' not found in client class '{client_class.__name__}'."
            )

        call_params = _add_request_options(func, params, call_params)
        call_params = _bind_search_parameter(func, call_params)
        _warn_dropped_params(format_set_name, params, call_params,
                             [*required_params, *optional_params, *spec_params])
        with recording_list_requests() as list_record, dict_shape_for_call(row_shape):
            result = func(**call_params)

        if not result or result == NO_ELEMENTS_FOUND:
            return {"kind": "empty"}
        cap_notes = page_cap_notes(func, call_params, result, list_record)

        if output_format == "TABLE" and table_shape == "structured":
            return build_structured_table(result, (fmt.get("formats") or {}).get("attributes") or [],
                                          notes=cap_notes, capped=bool(cap_notes), record=list_record)
        if output_format == "DICT" and row_shape == "native" and isinstance(result, list):
            cap_notes = cap_notes + mark_relationship_absence(  # "none" / "not read" (R1 follow-up)
                result, [c if isinstance(c, dict) else c.model_dump()
                         for c in (fmt.get("formats") or {}).get("attributes") or []], list_record, keyed_by="name")
        if output_format in {"DICT", "JSON", "ALL", "TABLE"}:
            # Return raw data (list/dict/any) — do not stringify here
            return {"kind": "json", "data": result, **({"notes": cap_notes} if cap_notes else {})}

        # For narrative formats, try to use generate_output if the result is structured
        if output_format in {"REPORT", "REPORT-GRAPH", "MD", "FORM", "LIST", "HTML", "MERMAID", "GRAPH"}:
            if isinstance(result, (list, dict)):
                result = generate_output(
                    elements=result,
                    search_string=call_params.get("search_string")
                    or call_params.get("filter_string")
                    or "All",
                    entity_type=safe_target_type,
                    output_format=output_format,
                    columns_struct=fmt,
                )

            # If it's already a string, it might have its own preamble. 
            # We only add our preamble if it doesn't look like it has one.
            heading = get_report_spec_heading(format_set_name)
            desc = get_report_spec_description(format_set_name)
            preamble = f"# {heading}\n{desc}\n\n" if heading and desc else ""
            
            content = str(result)
            if preamble and not content.strip().startswith("#"):
                content = preamble + content

            mime = "text/html" if output_format in ["HTML", "GRAPH"] else "text/markdown"
            if cap_notes:  # fix-now F8: a capped result says so in the text too
                content = content.rstrip("\n") + "\n\n" + "\n".join(
                    (f"<p><em>{n}</em></p>" if mime == "text/html" else f"_{n}_") for n in cap_notes) + "\n"
            return {"kind": "text", "mime": mime, "content": content,
                    **({"notes": cap_notes} if cap_notes else {})}

        return {"kind": "unknown", "raw": result}

    except PyegeriaException as e:
        # Re-raise with a simpler message for upstream mapping
        raise
    except ValidationError as e:
        print_validation_error(e)
        raise
    except ValueError as e:
        # Never a silent None (6.2.28): the caller gets the error and its words.
        # A refusal is expected (WARNING); any other ValueError is a real failure (ERROR).
        log = logger.warning if _is_spec_refusal(e) else logger.error
        log(f"Report spec '{format_set_name}' ({output_format}) failed: {e}")
        # Re-raised, as the async path does: a plain-words refusal must not reach the caller as "no result".
        raise

    finally:
        try:
            client.close_session()
        except Exception:
            pass
