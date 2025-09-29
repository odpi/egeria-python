"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides a basic MCP server for Egeria.


"""

from typing import Any, Dict

try:
    # The reference Python MCP SDK from the Model Context Protocol project
    # Install via: pip install mcp
    from mcp import Server, ToolError
except ImportError as e:
    raise SystemExit("The 'mcp' package is required. Install with: pip install mcp") from e

from pyegeria.mcp.mcp_adapter import (
    list_mcp_tools,
    describe_mcp_tool,
    run_mcp_tool,
)


def _ok(result: Dict[str, Any]) -> Dict[str, Any]:
    # Pass-through helper in case you want to normalize or add metadata
    return result


def main() -> None:
    srv = Server(name="pyegeria-mcp", version="0.1.0")

    @srv.tool(
        name="list_format_sets",
        schema={"type": "object", "properties": {}, "additionalProperties": False},
    )
    def list_format_sets_tool(_: Dict[str, Any]) -> Dict[str, Any]:
        return _ok(list_mcp_tools())

    @srv.tool(
        name="describe_format_set",
        schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "outputType": {"type": "string", "default": "ANY"},
            },
            "required": ["name"],
            "additionalProperties": False,
        },
    )
    def describe_format_set_tool(args: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return _ok(describe_mcp_tool(args["name"], args.get("outputType", "ANY")))
        except Exception as e:
            raise ToolError(str(e))

    @srv.tool(
        name="run_format_set_action",
        schema={
            "type": "object",
            "properties": {
                "formatSet": {"type": "string"},
                "outputFormat": {
                    "type": "string",
                    "enum": ["DICT", "JSON", "REPORT", "MERMAID", "HTML"],
                    "default": "DICT",
                },
                "params": {"type": "object", "default": {}},
            },
            "required": ["formatSet"],
            "additionalProperties": False,
        },
    )
    def run_format_set_action_tool(args: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return _ok(
                run_mcp_tool(
                    formatSet=args["formatSet"],
                    outputFormat=args.get("outputFormat", "DICT"),
                    params=args.get("params", {}),
                )
            )
        except Exception as e:
            # pyegeria exceptions and value errors are mapped to ToolError
            raise ToolError(str(e))

    # Run in stdio mode so agent hosts can spawn the process
    srv.run_stdio()


if __name__ == "__main__":
    main()