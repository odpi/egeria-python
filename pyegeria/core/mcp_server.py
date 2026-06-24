"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides a basic MCP server for Egeria.
"""
import re
import sys
import nest_asyncio
from loguru import logger

from typing import Any, Dict, Optional, Literal

from mcp.server.fastmcp.exceptions import ValidationError

from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.core._exceptions import print_validation_error
from pyegeria.view.base_report_formats import load_egeria_report_specs

GLOBAL_EGERIA_CLIENT: Optional[EgeriaTech] = None
nest_asyncio.apply()

try:
    # We use Optional[] and List[] types, so we import them.
    from mcp.server.fastmcp import FastMCP
    from pyegeria.core.mcp_adapter import (
        list_reports,
        describe_report,
        run_report, _execute_egeria_call_blocking,
        _async_run_report_tool, run_find_report_specs
    )

    print("MCP import successful...", file=sys.stderr)
except ImportError:
    print("MCP import failed.", file=sys.stderr)
    raise


def _ok(result: Dict[str, Any]) -> Dict[str, Any]:
    # Pass-through helper in case you want to normalize or add metadata
    print("OK: Operation completed successfully.", file=sys.stderr)
    return result


def main() -> None:
    # Initialize the server

    global GLOBAL_EGERIA_CLIENT

    try:
        """ Runs ONCE when the server starts.
            Initializes the Egeria client and stores it in the server's state.
        """
        logger.debug("Initializing Egeria client...")
        from pyegeria.core.config import settings as _settings
        user_id = _settings.User_Profile.user_name
        user_pwd = _settings.User_Profile.user_pwd

        GLOBAL_EGERIA_CLIENT = EgeriaTech(
            _settings.Environment.egeria_view_server,
            _settings.Environment.egeria_view_server_url,
            user_id,
            user_pwd
        )
        logger.debug("Egeria Client initialized")
        GLOBAL_EGERIA_CLIENT.create_egeria_bearer_token("erinoverview", "secret")
        logger.debug("Egeria Client connected")

        load_egeria_report_specs(GLOBAL_EGERIA_CLIENT)
        logger.debug("Egeria report specs loaded into registry")

    except ValidationError as e:
        print_validation_error(e)
        raise
    except Exception as e:
        logger.debug(f"Exception occurred: {str(e)}")
        raise

    srv = FastMCP(name="pyegeria-mcp")
    print("Starting MCP server...", file=sys.stderr)

    # list_reports tool (formerly list_format_sets)
    @srv.tool(name="list_reports")
    def list_reports_tool(output_type: Literal["DICT", "JSON", "MARKDOWN"] = "DICT") -> Dict[str, Any]:
        """Lists all available reports (FormatSets)."""
        logger.debug("Listing reports...")
        return _ok(list_reports())

    @srv.tool(name="find_report_specs")
    def find_report_specs_tool(perspective: str=None, question: str=None, report_spec: str=None, output_type: Literal["DICT", "JSON", "MARKDOWN"] = "DICT") -> Dict[str, Any]:
        """Finds report specs that match the given perspective, question, and report spec."""
        logger.debug("Finding report specs...")
        return _ok(run_find_report_specs(perspective=perspective, question=question, report_spec=report_spec))


    @srv.tool(name="describe_report")
    def describe_report_tool(name: str, output_type: Literal["DICT", "JSON", "MARKDOWN"] = "DICT") -> Dict[str, Any]:
        """Returns the schema and details for a specified report."""
        # FastMCP handles validation of 'name' and 'output_type' types automatically.
        effective_output_type = "REPORT" if output_type == "MARKDOWN" else ("DICT" if output_type == "JSON" else output_type)

        logger.debug(f"Describing report: {name} with output type: {effective_output_type}")
        try:
            return _ok(describe_report(name, effective_output_type))
        except Exception as e:
            logger.debug(f"Exception during describe_report: {str(e)}")
            raise

    @srv.tool(name="run_report")
    async def run_report_tool(
            report_name: str,
            search_string: str = "*",
            page_size: Optional[int] = 0,
            start_from: Optional[int] = 0,
            starts_with: Optional[bool] = None,
            ends_with: Optional[bool] = None,
            ignore_case: Optional[bool] = None,
            output_type: Literal[
                "DICT", "JSON", "MARKDOWN",
                "LIST", "TABLE", "REPORT", "REPORT-GRAPH",
                "FORM", "MD", "MERMAID", "HTML", "GRAPH",
            ] = "DICT"
    ) -> Dict[str, Any]:
        import asyncio
        import nest_asyncio
        nest_asyncio.apply()

        """Run a report with the specified parameters."""
        print("DEBUG: Running report...", file=sys.stderr)
        # 1. Automatic Validation: FastMCP/Pydantic ensures types are correct.

        # 2. Manual Validation (for specific values like output_format)
        # "MARKDOWN" is a friendly alias for the executor's internal "REPORT".
        # Every other type is passed through as-is so callers get the full
        # fidelity of pyegeria's output formats (LIST, FORM, MERMAID, HTML, ...).
        # Unsupported-for-this-spec types are rejected downstream by the
        # executor with a clear "does not support output_format" message that
        # lists the available formats — we do not pre-empt that here.
        effective_output_format = "REPORT" if output_type == "MARKDOWN" else output_type

        _VALID_OUTPUT_FORMATS = [
            "DICT", "JSON", "LIST", "TABLE", "REPORT", "REPORT-GRAPH",
            "FORM", "MD", "MERMAID", "HTML", "GRAPH",
        ]
        if effective_output_format not in _VALID_OUTPUT_FORMATS:
            print(f"DEBUG: Invalid output_format: {effective_output_format}", file=sys.stderr)
            raise ValueError(
                f"Invalid output_format: {effective_output_format}. "
                f"Must be one of {_VALID_OUTPUT_FORMATS}.")

        # 3. Build params dictionary with only non-None values for clean passing
        params = {
            "search_string": search_string,
            "page_size": page_size,
            "start_from": start_from,
            "starts_with": starts_with,
            "ends_with": ends_with,
            "ignore_case": ignore_case,
        }
        # Filter out None values before passing to run_report
        params = {k: v for k, v in params.items() if v is not None}

        logger.debug(f"Running report={report_name} with params={params}")

        try:
            # Build a fresh Egeria client bound to THIS handler's event loop and
            # mint a fresh bearer token per call. Reusing the module-level
            # GLOBAL_EGERIA_CLIENT (created in the server's startup loop) caused
            # intermittent CLIENT_ERROR_400 ("unable to connect") because its
            # httpx async client is bound to a different loop than the one
            # FastMCP runs tool handlers in. A per-call client (mirroring
            # exec_report_spec / the CLI) is reliable.
            from pyegeria.core.config import settings as _settings
            _user = _settings.User_Profile.user_name
            _pwd = _settings.User_Profile.user_pwd
            egeria_client = EgeriaTech(
                _settings.Environment.egeria_view_server,
                _settings.Environment.egeria_view_server_url,
                _user,
                _pwd,
            )
            await egeria_client._async_create_egeria_bearer_token(_user, _pwd)
            logger.debug("Egeria Client connected (fresh per-call client)")
            try:
                # Large/multi-request reports (e.g. master-detail LIST, big
                # graph reports) can legitimately take well over 30s; a tight
                # cap cancels them mid-request and surfaces as a confusing
                # CLIENT_ERROR_400. Use a generous, env-configurable timeout.
                import os
                _report_timeout = float(os.environ.get("PYEGERIA_MCP_REPORT_TIMEOUT", "300"))
                result = await asyncio.wait_for(
                    _async_run_report_tool(
                        report=report_name,
                        egeria_client=egeria_client,
                        params=params,
                        output_format=effective_output_format),
                    timeout=_report_timeout
                )
            finally:
                # Release the per-call client's HTTP connections (sync method).
                try:
                    egeria_client.close_session()
                except Exception:
                    pass

            logger.debug("run_report completed successfully")
            return _ok(result)
        except Exception as e:
            # Re-raise the exception to be sent back as a JSON-RPC error
            logger.debug(f"Exception occurred: {str(e)}")
            raise

    @srv.tool(name="prompt")
    async def natural_language_prompt(prompt: str) -> Dict[str, Any]:
        """
        Handles natural language queries from the user.
        In a production environment, this would call an LLM API.
        """
        logger.debug(f"Received natural language prompt: {prompt}")

        # Example of simple logic: If the user asks to list reports, delegate to the tool.
        if "list" in prompt.lower() and "reports" in prompt.lower():
            logger.debug("Delegating prompt to list_reports tool.")
            return list_reports()  # This is sync, so no await needed
        elif "run" in prompt.lower() and "report" in prompt.lower():
            logger.debug("Delegating prompt to run_report tool.")

            match = re.search(r'report\s+([a-zA-Z0-9]+)', prompt, re.IGNORECASE)
            report_name = match.group(1) if match else None

            if report_name:
                logger.debug(f"Extracted report name: {report_name}")

                page_size_match = re.search(r'page size of\s+(\d+)', prompt, re.IGNORECASE)
                page_size = int(page_size_match.group(1)) if page_size_match else None

                search_match = re.search(r'search for\s+(.*?)(?:\s+in\s+report|\.|$)', prompt, re.IGNORECASE)

                if search_match:
                    search_string = search_match.group(1).strip()

                    if search_string:
                        print(
                            f"DEBUG: Delegating prompt to run_report tool. Report: {report_name}, Search: '{search_string}'",
                            file=sys.stderr)

                        # AWAIT the async function call
                        return await run_report_tool(report_name=report_name, search_string=search_string,
                                                     page_size=page_size)

                # AWAIT the async function call
                return await run_report_tool(report_name=report_name, page_size=page_size)

        return {
            "response": f"Acknowledged natural language query: '{prompt}'. This would be sent to an LLM."
        }

    # CRITICAL: This is the missing step. It tells the server to read and process
    # JSON-RPC messages from standard input (stdin).
    srv.run()
    print("MCP server finished running.", file=sys.stderr)


if __name__ == "__main__":
    main()
