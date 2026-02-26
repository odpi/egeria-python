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
import json
import sys
from typing import Any, Dict, Optional

from loguru import logger

from pyegeria.omvs.classification_explorer import ClassificationExplorer
from pyegeria.omvs.actor_manager import ActorManager
from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.omvs.collection_manager import CollectionManager
from pyegeria.omvs.governance_officer import GovernanceOfficer
from pyegeria.omvs.glossary_manager import GlossaryManager
from pyegeria.core._globals import NO_ELEMENTS_FOUND
from pyegeria.core.config import settings
from pyegeria.omvs.external_links import ExternalReferences
from pyegeria.core._exceptions import PyegeriaException
from pyegeria.view.base_report_formats import (
    select_report_spec,
    get_report_spec_heading,
    get_report_spec_description,
    get_report_registry,
)
from pyegeria.view.output_formatter import generate_output


_CLIENT_CLASS_MAP = {
    "CollectionManager": CollectionManager,
    "GovernanceOfficer": GovernanceOfficer,
    "GlossaryManager": GlossaryManager,
    "ExternalReference": ExternalReferences,
    "ClassificationExplorer": ClassificationExplorer,
    "ActorManager": ActorManager,
}


def _resolve_client_and_method(func_decl: str):
    """Given a function declaration like 'ClassName.method', return (client_class, method_name)."""
    if not isinstance(func_decl, str) or "." not in func_decl:
        return (EgeriaTech, None)
    class_name, method_name = func_decl.split(".", 1)
    client_class = _CLIENT_CLASS_MAP.get(class_name, EgeriaTech)
    return (client_class, method_name)


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
            print("DEBUG: Function is async, using await.", file=sys.stderr)
            result = await func(**call_params)
        else:
            # If it's a synchronous function, call it directly
            print("DEBUG: Function is sync, calling directly.", file=sys.stderr)
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

    action = fmt["action"]
    func_decl = action.get("function")
    if isinstance(func_decl, str) and "." in func_decl:
        class_name, method_name = func_decl.split(".")

    if not method_name.startswith("_async_"):
        method_name = "_async_" + method_name
        func_decl = class_name + "." + method_name

    required_params = action.get("required_params", action.get("user_params", [])) or []
    optional_params = action.get("optional_params", []) or []
    spec_params = action.get("spec_params", {}) or {}
    print(f"func_decl={func_decl}", file=sys.stderr)
    # Build call params: required/optional provided by caller + fixed spec_params
    call_params: Dict[str, Any] = {}

    # Populate required and optional params when provided
    for p in required_params:
        if p in params and params[p] is not None:
            call_params[p] = params[p]
        elif p not in spec_params:
            # Missing required param
            logger.warning(f"Required parameter '{p}' not provided for format set '{report_name}'.")
    for p in optional_params:
        if p in params and params[p] is not None:
            call_params[p] = params[p]

    # Include fixed specifics
    call_params.update(spec_params)

    # Always include output_format and report_spec for downstream rendering
    call_params["output_format"] = output_format
    call_params["report_spec"] = report_name

    client_class, method_name = _resolve_client_and_method(func_decl)


    try:
        func = getattr(egeria_client, method_name) if method_name and hasattr(egeria_client, method_name) else None
        # Add logging to validate func
        msg = f"DEBUG: func={func}, method_name={method_name}, client_class={client_class}"
        logger.debug(msg)
        print(msg, file=sys.stderr)

        if func is None or not callable(func):
            raise TypeError(
                f"Resolved function '{method_name}'  not found in client class '{client_class.__name__}' is not callable."
            )
        # Only (re)create a bearer token if one is not already set on the client.
        try:
            existing_token = None
            if hasattr(egeria_client, "get_token"):
                existing_token = egeria_client.get_token()
            if not existing_token:
                print("DEBUG: No existing bearer token; attempting async creation...", file=sys.stderr)
                if user_name and user_pwd:
                    await egeria_client._async_create_egeria_bearer_token(user_name, user_pwd)
                else:
                    print("DEBUG: Missing credentials; skipping token creation and relying on pre-initialized token.", file=sys.stderr)
            else:
                print("DEBUG: Using existing bearer token.", file=sys.stderr)
        except Exception as auth_err:
            # Do not fail the entire call if token refresh fails; downstream call may still work
            print(f"DEBUG: Token creation/lookup issue: {auth_err}", file=sys.stderr)
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
                    entity_type=fmt.get("target_type", "Referenceable"),
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
    params = dict(params or {})

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

    action = fmt["action"]
    func_decl = action.get("function")
    required_params = action.get("required_params", action.get("user_params", [])) or []
    optional_params = action.get("optional_params", []) or []
    spec_params = action.get("spec_params", {}) or {}

    # Build call params: required/optional provided by caller + fixed spec_params
    call_params: Dict[str, Any] = {}

    # Populate required and optional params when provided
    for p in required_params:
        if p in params and params[p] is not None:
            call_params[p] = params[p]
        elif p not in spec_params:
            # Missing required param
            logger.warning(f"Required parameter '{p}' not provided for report spec '{format_set_name}'.")
    for p in optional_params:
        if p in params and params[p] is not None:
            call_params[p] = params[p]

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
                    entity_type=fmt.get("target_type", "Referenceable"),
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
    except ValueError as e:
        import traceback
        traceback.print_exc()

    finally:
        try:
            client.close_session()
        except Exception:
            pass
