"""
SPDX-License-Identifier: Apache-2.0

Thin adapter helpers to surface pyegeria FormatSets as MCP-style tools without
side effects. This does NOT implement an MCP transport/server; it focuses on
programmatic functions that an MCP server entry point can call.

Only format sets that advertise DICT or ALL are considered eligible.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from loguru import logger

from pyegeria._output_formats import (
    list_mcp_format_sets,
    select_output_format_set,
    get_output_format_type_match,
)
from pyegeria.format_set_executor import run_format_set_action_return


def list_mcp_tools() -> Dict[str, Any]:
    """List eligible format sets as MCP tools (support DICT or ALL)."""
    return {"formatSets": list_mcp_format_sets()}


def describe_mcp_tool(name: str, outputType: str = "ANY") -> Dict[str, Any]:
    """
    Describe a format set for MCP discovery. If outputType != ANY, a concrete format
    will be resolved; otherwise only metadata/action are returned.
    """
    meta = select_output_format_set(name, outputType)
    if not meta:
        raise ValueError(f"Unknown or incompatible format set: {name}")
    return meta


def run_mcp_tool(
    *,
    formatSet: str,
    params: Optional[Dict[str, Any]] = None,
    outputFormat: str = "DICT",
    view_server: Optional[str] = None,
    view_url: Optional[str] = None,
    user: Optional[str] = None,
    user_pass: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute a format set action as an MCP-style tool. Enforces DICT/ALL by default.
    Caller may pass credentials explicitly; otherwise defaults are used from config.
    """
    # Enforce DICT/ALL eligibility at runtime too
    desired = (outputFormat or "DICT").upper()
    if desired not in {"DICT", "ALL", "JSON", "REPORT", "MERMAID", "HTML"}:
        desired = "DICT"

    # When asked for JSON, map to DICT if present
    if desired == "JSON":
        desired = "DICT"

    # Lazy import of settings to avoid circulars when optional args are None
    from pyegeria.config import settings as _settings

    return run_format_set_action_return(
        format_set_name=formatSet,
        output_format=desired,
        params=params or {},
        view_server=view_server if view_server is not None else _settings.Environment.egeria_view_server,
        view_url=view_url if view_url is not None else _settings.Environment.egeria_view_server_url,
        user=user if user is not None else _settings.User_Profile.user_name,
        user_pass=user_pass if user_pass is not None else _settings.User_Profile.user_pwd,
    )
