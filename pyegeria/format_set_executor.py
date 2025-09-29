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

import json
from typing import Any, Dict, Optional

from loguru import logger

from pyegeria import (
    EgeriaTech,
    CollectionManager,
    GovernanceOfficer,
    GlossaryManager,
    NO_ELEMENTS_FOUND,
)
from pyegeria.config import settings
from pyegeria.external_references import ExternalReferences
from pyegeria._exceptions_new import PyegeriaException
from pyegeria._output_formats import (
    select_output_format_set,
    get_output_format_set_heading,
    get_output_format_set_description,
)


_CLIENT_CLASS_MAP = {
    "CollectionManager": CollectionManager,
    "GovernanceOfficer": GovernanceOfficer,
    "GlossaryManager": GlossaryManager,
    "ExternalReference": ExternalReferences,
}


def _resolve_client_and_method(func_decl: str):
    """Given a function declaration like 'ClassName.method', return (client_class, method_name)."""
    if not isinstance(func_decl, str) or "." not in func_decl:
        return (EgeriaTech, None)
    class_name, method_name = func_decl.split(".", 1)
    client_class = _CLIENT_CLASS_MAP.get(class_name, EgeriaTech)
    return (client_class, method_name)


def run_format_set_action_return(
    format_set_name: str,
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
    fmt = select_output_format_set(format_set_name, output_format)
    if not fmt:
        raise ValueError(
            f"Output format set '{format_set_name}' does not have a compatible '{output_format}' format."
        )
    if "action" not in fmt:
        raise ValueError(f"Output format set '{format_set_name}' does not have an action property.")

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
            logger.warning(f"Required parameter '{p}' not provided for format set '{format_set_name}'.")
    for p in optional_params:
        if p in params and params[p] is not None:
            call_params[p] = params[p]

    # Include fixed specifics
    call_params.update(spec_params)

    # Always include output_format and output_format_set for downstream rendering
    call_params["output_format"] = output_format
    call_params["output_format_set"] = format_set_name

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

        # Prepare optional preamble for narrative outputs
        heading = get_output_format_set_heading(format_set_name)
        desc = get_output_format_set_description(format_set_name)
        preamble = f"# {heading}\n{desc}\n\n" if heading and desc else ""

        if output_format in {"DICT", "JSON", "ALL"}:
            # Return raw data (list/dict/any) — do not stringify here
            return {"kind": "json", "data": result}
        elif output_format in {"REPORT", "MERMAID"}:
            content = result
            if isinstance(result, (list, dict)):
                # Make a simple JSON code block if the source returned structured data unexpectedly
                content = preamble + "```json\n" + json.dumps(result, indent=2) + "\n```"
            else:
                content = preamble + str(result)
            return {"kind": "text", "mime": "text/markdown", "content": content}
        elif output_format == "HTML":
            content = str(result)
            return {"kind": "text", "mime": "text/html", "content": content}
        else:
            # Unknown or table-like formats which aren't appropriate for MCP by default
            return {"kind": "unknown", "raw": result}

    except PyegeriaException as e:
        # Re-raise with a simpler message for upstream mapping
        raise
    finally:
        try:
            client.close_session()
        except Exception:
            pass
