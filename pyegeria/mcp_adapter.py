"""
SPDX-License-Identifier: Apache-2.0

Thin adapter helpers to surface pyegeria FormatSets as MCP-style tools without
side effects. This does NOT implement an MCP transport/server; it focuses on
programmatic functions that an MCP server entry point can call.

Only format sets that advertise DICT or ALL are considered eligible.
"""
from __future__ import annotations

import json
import sys
from typing import Any, Dict, Optional

from loguru import logger

from pyegeria._output_formats import (
    list_mcp_format_sets,
    select_output_format_set,
)
from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.format_set_executor import exec_format_set, _async_run_report


def list_reports() -> dict:
    """List eligible format sets as MCP tools (support DICT or ALL)."""
    return  list_mcp_format_sets()


def describe_report(name: str, output_type: str = "DICT") -> Dict[str, Any]:
    """
    Describe a format set for MCP discovery. If outputType != ANY, a concrete format
    will be resolved; otherwise only metadata/action are returned.
    """
    meta = select_output_format_set(name, output_type)
    if not meta:
        raise ValueError(f"Unknown or incompatible format set: {name}")
    return meta


def _execute_egeria_call_blocking(
        *,
        report: str,
        params: Optional[Dict[str, Any]] = None,
        view_server: Optional[str] = None,
        view_url: Optional[str] = None,
        user: Optional[str] = None,
        user_pass: Optional[str] = None,) -> Dict[str, Any]:
    """
    Executes the synchronous, blocking Egeria client call on a dedicated worker thread.

    You must replace the hardcoded return with your actual Egeria client logic here.
    All code in this function runs in a blocking, synchronous manner.
    """

    print(
        f"Format set: {report}\nparams: {json.dumps(params)}\nview_server: {view_server}\nview_url: {view_url}\nuser: {user}\nuser_pass: {user_pass}",
        file=sys.stderr)
    # Lazy import of settings to avoid circulars when optional args are None
    # from pyegeria.config import settings as _settings
    from pyegeria.config import settings as _settings


    return exec_format_set(
        format_set_name=report,
        output_format="DICT",
        params=params or {},
        view_server=view_server if view_server is not None else _settings.Environment.egeria_view_server,
        view_url=view_url if view_url is not None else _settings.Environment.egeria_view_server_url,
        user=user if user is not None else _settings.User_Profile.user_name,
        user_pass=user_pass if user_pass is not None else _settings.User_Profile.user_pwd,
    )
    # # Returning the hardcoded success for now to prove the async structure works.
    # return {
    #     "status": "SUCCESS (Thread Test)",
    #     "report_name": report_name,
    #     "message": "The blocking call was successfully run on a separate thread, preventing timeout."
    # }



def run_report(
    *,
    report: str,
    params: Optional[Dict[str, Any]] = None,
    view_server: Optional[str] = None,
    view_url: Optional[str] = None,
    user: Optional[str] = None,
    user_pass: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute a format set action as an MCP-style tool. Enforces DICT/ALL by default.
    Caller may pass credentials explicitly; otherwise defaults are used from config.
    """
    print(f"Format set: {report}\nparams: {json.dumps(params)}\nview_server: {view_server}\nview_url: {view_url}\nuser: {user}\nuser_pass: {user_pass}", file=sys.stderr)
    # Lazy import of settings to avoid circulars when optional args are None
    from pyegeria.config import settings as _settings
    logger.info(f"Format set: {report}\nparams: {json.dumps(params)}\nview_server: {view_server}\nview_url: {view_url}\nuser: {user}\nuser_pass: {user_pass}")
    return run_format_set(
        format_set_name=report,
        output_format="DICT",
        params=params or {},
        view_server=view_server if view_server is not None else _settings.Environment.egeria_view_server,
        view_url=view_url if view_url is not None else _settings.Environment.egeria_view_server_url,
        user=user if user is not None else _settings.User_Profile.user_name,
        user_pass=user_pass if user_pass is not None else _settings.User_Profile.user_pwd,
    )

async def _async_run_report_tool(
    *,
    report: str,
    egeria_client: EgeriaTech,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Execute a format set action as an MCP-style tool. Enforces DICT/ALL by default.
    Caller may pass credentials explicitly; otherwise defaults are used from config.
    """
    # Lazy import of settings to avoid circulars when optional args are None

    print(f"Report: {report}\n params: {json.dumps(params)}\n", file=sys.stderr)
    result = await _async_run_report(report, egeria_client, output_format="DICT", params=params)
    return result
