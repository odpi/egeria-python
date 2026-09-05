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
import sys
from typing import Any, Dict, Optional, Union

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
from pyegeria.view.analytic_registry import AnalyticActionSpec
from pyegeria.egeria_tech_client import EgeriaTech

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


def _resolve_analytic_function(func_decl: str):
    """Given a dotted import path like 'pyegeria.view.overview_metrics.growth_series',
    import and return the callable. Unlike `function` (find_method), `analytic_function`
    (extra_find) targets a plain module-level function, not a client class method --
    overview_metrics.py's whole design boundary is that its functions take an
    already-constructed, already-authenticated client as their first argument, so
    there's no client class to resolve here, just the function itself."""
    if not isinstance(func_decl, str) or "." not in func_decl:
        raise ValueError(f"Invalid analytic_function declaration: {func_decl!r}")
    module_path, func_name = func_decl.rsplit(".", 1)
    module = importlib.import_module(module_path)
    func = getattr(module, func_name, None)
    if func is None or not callable(func):
        raise AttributeError(f"'{func_name}' not found in module '{module_path}'")
    return func


# Parameter names an analytic function uses for its leading client argument(s)
# -- pyegeria.view.overview_metrics's functions take one (`mgr` or `ce`) or,
# for semantic_grounding, two (`mgr`, `ce`) positional clients before their
# real parameters. EgeriaTech is a facade that proxies to every subclient via
# __getattr__ (see egeria_tech_client.py), so the same instance satisfies
# either role -- no need to construct a second client.
_ANALYTIC_CLIENT_PARAM_NAMES = {"mgr", "ce", "expert", "client"}


def _bind_client_args(func, client: Any) -> list:
    """Return the positional args to pass before **kwargs: one copy of `client`
    per leading parameter named like a client (mgr/ce/expert/client)."""
    args = []
    for name, param in inspect.signature(func).parameters.items():
        if name in _ANALYTIC_CLIENT_PARAM_NAMES and param.kind in (
            inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD,
        ):
            args.append(client)
        else:
            break
    return args


def run_analytic_action(
    action: AnalyticActionSpec, client: Any, *,
    fetch_kwargs: Optional[Dict[str, Any]] = None,
    analytic_kwargs: Optional[Dict[str, Any]] = None,
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

    `client` is resolved once by the caller (same convention as
    `_run_analytic_function`) and bound positionally to both steps' leading
    client-shaped parameters -- `fetch` via the usual signature introspection
    (`_bind_client_args`), `analytic` via the SAME resolved client args
    (not re-introspected from `analytic`'s own signature, since its first
    positional parameter is the fetch result, not a client) -- so `analytic`
    can itself make a further client call (e.g. follow a relationship to
    enrich) using the identical already-authenticated client `fetch` used.
    """
    fetch_func = _resolve_analytic_function(action.fetch)
    fetch_clients = _bind_client_args(fetch_func, client)
    raw_result = fetch_func(*fetch_clients, **(fetch_kwargs or {}))

    if not action.analytic:
        return raw_result

    analytic_func = _resolve_analytic_function(action.analytic)
    return analytic_func(raw_result, *fetch_clients, **(analytic_kwargs or {}))


def _run_analytic_function(
    action: dict, *, params: Dict[str, Any],
    view_server: str, view_url: str, user: str, user_pass: str,
    token: Optional[str] = None,
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

    func = _resolve_analytic_function(func_decl)
    if token:
        client = EgeriaTech(view_server, view_url, user_id=user, user_pwd=user_pass)
        client.set_bearer_token(token)
    else:
        client = EgeriaTech(view_server, view_url, user_id=user, user_pwd=user_pass)
        client.create_egeria_bearer_token()
    return func(*_bind_client_args(func, client), **call_params)


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
    return client_class(
        egeria_client.view_server,
        egeria_client.platform_url,
        user_id=egeria_client.user_id,
        user_pwd=egeria_client.user_pwd,
        token=egeria_client.token,
    )


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

    return cleaned


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
async def _async_run_report(
    report_name: str,
    egeria_client: EgeriaTech,
    output_format: str = "DICT",
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
        Execute the action for a given format set and return a normalized result structure.

        Returns shapes:
        - {"kind":"empty"}
        - {"kind":"json","data": <list|dict|any>}
        - {"kind":"text","mime": "text/markdown"|"text/html","content": str}
        - {"kind":"unknown","raw": any}
        """
    params = dict(params or {})
    user_name = egeria_client.user_id
    user_pwd = egeria_client.user_pwd

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
        result = await func(**call_params)

        if not result or result == NO_ELEMENTS_FOUND:
            return {"kind": "empty"}

        if output_format in {"DICT", "JSON", "ALL", "TABLE"}:
            # Return raw data (list/dict/any) — do not stringify here; include TABLE to enable Rich rendering upstream
            return {"kind": "json", "data": result}

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
            return {"kind": "text", "mime": mime, "content": content}

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

    result = _run_analytic_function(
        action, params=params, view_server=view_server, view_url=view_url,
        user=user, user_pass=user_pass, token=token,
    )
    if not result:
        return {"kind": "empty"}

    try:
        heading = get_report_spec_heading(format_set_name) or str(format_set_name)
    except Exception:  # noqa: BLE001 -- registry lookup quirks shouldn't block chart rendering
        heading = str(format_set_name)

    if chart_kind == "line":
        if not isinstance(result, list) or not all(isinstance(pt, dict) for pt in result):
            return {"kind": "json", "data": result}
        x_field = "label" if any("label" in pt for pt in result) else "date"
        y_fields = sorted({
            k for pt in result for k, v in pt.items()
            if k not in ("label", "date") and isinstance(v, (int, float)) and not isinstance(v, bool)
        })
        if not y_fields:
            return {"kind": "json", "data": result}
        chart = generate_vega_line_chart(
            result, x_field=x_field, y_fields=y_fields,
            title=heading, x_label=x_field.capitalize(), y_label="Count",
        )
        return {"kind": "json", "data": chart} if chart else {"kind": "json", "data": result}

    # bar / pie -- both need a plain {category: numeric_value} mapping
    cat_values = _as_category_value_dict(result)
    if not cat_values:
        return {"kind": "json", "data": result}
    chart = (generate_vega_bar_chart(cat_values, title=heading) if chart_kind == "bar"
             else generate_vega_pie_chart(cat_values, title=heading))
    return {"kind": "json", "data": chart} if chart else {"kind": "json", "data": result}


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
) -> Dict[str, Any]:
    """
    Execute the action for a given format set and return a normalized result structure.

    Returns shapes:
    - {"kind":"empty"}
    - {"kind":"json","data": <list|dict|any>}
    - {"kind":"text","mime": "text/markdown"|"text/html","content": str}
    - {"kind":"unknown","raw": any}

    ISSUE-86: `token`, when given, authenticates the client(s) built here with
    `set_bearer_token(token)` instead of minting a fresh token from
    `user`/`user_pass` via `create_egeria_bearer_token()`. Use this when the
    caller already holds a bearer token for the calling user (e.g. an app
    whose session carries the user's Egeria token, not their password) so
    report execution -- and its provenance -- reflects that user, not a
    fallback service account. `user`/`user_pass` remain fully backward
    compatible when `token` is not given.
    """
    output_format = (output_format or "DICT").upper()
    params = _normalize_report_params(dict(params or {}), action_mode="find")

    # SERIES/BAR/PIE are not Format-row output types like TABLE/DICT/REPORT --
    # they don't need per-column formatting at all, just the analytic
    # function's already-aggregated result wrapped as the corresponding
    # Vega-Lite chart. Dispatch before the normal Format-row lookup (which
    # would reject them as unsupported, since no FormatSet declares a
    # "SERIES"/"BAR"/"PIE" Format row).
    _CHART_KINDS = {"SERIES": "line", "BAR": "bar", "PIE": "pie"}
    if output_format in _CHART_KINDS:
        return _exec_analytic_chart(
            format_set_name, chart_kind=_CHART_KINDS[output_format], params=params,
            view_server=view_server, view_url=view_url, user=user, user_pass=user_pass,
            token=token,
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
        result = _run_analytic_function(
            action, params=params, view_server=view_server, view_url=view_url,
            user=user, user_pass=user_pass, token=token,
        )
        if result is None or result == [] or result == {}:
            return {"kind": "empty"}
        return {"kind": "json", "data": result}

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

        result = func(**call_params)

        if not result or result == NO_ELEMENTS_FOUND:
            return {"kind": "empty"}

        if output_format in {"DICT", "JSON", "ALL", "TABLE"}:
            # Return raw data (list/dict/any) — do not stringify here
            return {"kind": "json", "data": result}

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
            return {"kind": "text", "mime": mime, "content": content}

        return {"kind": "unknown", "raw": result}

    except PyegeriaException as e:
        # Re-raise with a simpler message for upstream mapping
        raise
    except ValidationError as e:
        print_validation_error(e)
        raise
    except ValueError as e:
        import traceback
        traceback.print_exc()

    finally:
        try:
            client.close_session()
        except Exception:
            pass
