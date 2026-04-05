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
from typing import Any, Dict, Optional

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
        "property_value": ["search_string"],
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
        if output_format in {"REPORT", "REPORT-GRAPH", "MD", "FORM", "LIST", "HTML", "MERMAID"}:
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

            mime = "text/html" if output_format == "HTML" else "text/markdown"
            return {"kind": "text", "mime": mime, "content": content}

        return {"kind": "unknown", "raw": result}

    except PyegeriaException as e:
        # Re-raise with a simpler message for upstream mapping
        raise
    except ValidationError as e:
        print_validation_error(e)
        raise



def exec_report_spec(
    format_set_name: str | dict,
    *,
    output_format: str = "DICT",
    params: Optional[Dict[str, Any]] = None,
    view_server: str = settings.Environment.egeria_view_server,
    view_url: str = settings.Environment.egeria_view_server_url,
    user: str = settings.User_Profile.user_name,
    user_pass: str = settings.User_Profile.user_pwd,
) -> Dict[str, Any]:
    """
    Execute the action for a given format set and return a normalized result structure.

    Returns shapes:
    - {"kind":"empty"}
    - {"kind":"json","data": <list|dict|any>}
    - {"kind":"text","mime": "text/markdown"|"text/html","content": str}
    - {"kind":"unknown","raw": any}
    """
    output_format = (output_format or "DICT").upper()
    params = _normalize_report_params(dict(params or {}), action_mode="find")

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
        if output_format in {"REPORT", "REPORT-GRAPH", "MD", "FORM", "LIST", "HTML", "MERMAID"}:
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

            mime = "text/html" if output_format == "HTML" else "text/markdown"
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
