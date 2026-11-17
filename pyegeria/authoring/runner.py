# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""A runner that processes a Dr.Egeria document in-process, as the client it's given.

`inprocess_runner(client)` returns `run(markdown, directive) -> dict`, the runner shape
`report_spec_publish.run_document` and `pyegeria.authoring.apply` take. The client must be signed in as
the user the document runs as: this module never authenticates. Apps with their own runner (the Portal's
Dr.Egeria API, EA's action agent) pass theirs instead.
"""
from __future__ import annotations

import uuid
from typing import Any, Callable, Dict

DIRECTIVES = ("validate", "process")


async def async_run_markdown(client: Any, markdown: str, directive: str) -> Dict[str, Any]:
    if directive not in DIRECTIVES:
        raise ValueError(f"Directive must be one of {', '.join(DIRECTIVES)}, not {directive!r}.")
    from md_processing.dr_egeria import setup_dispatcher
    from md_processing.v2.extraction import UniversalExtractor
    commands = UniversalExtractor(markdown).extract_commands()
    if not commands:
        return {"success": False, "commands_total": 0, "commands_succeeded": 0, "commands_failed": 0,
                "commands_detail": [], "validation_errors": [{"message": "the document holds no Dr.Egeria command"}]}
    dispatcher = setup_dispatcher(client)
    results = await dispatcher.dispatch_batch(commands, {"directive": directive, "request_id": str(uuid.uuid4()),
                                                         "input_file": "authoring", "debug": False})
    detail, failed = [], 0
    errors = []
    for r in results or []:
        status = (r or {}).get("status") or "unknown"
        detail.append({"command": f"{r.get('verb', '')} {r.get('object_type', '')}".strip(), "status": status,
                       "message": r.get("message"), "display_name": r.get("display_name"),
                       "qualified_name": r.get("qualified_name"), "warnings": r.get("warnings") or []})
        if status in ("failure", "error", "unknown"):
            failed += 1
            for e in r.get("errors") or [r.get("message") or status]:
                errors.append({"command": detail[-1]["command"], "message": e})
    key = "validation_errors" if directive == "validate" else "execution_errors"
    return {"success": failed == 0, "commands_total": len(detail), "commands_succeeded": len(detail) - failed,
            "commands_failed": failed, "commands_detail": detail, key: errors}


def inprocess_runner(client: Any) -> Callable[[str, str], Dict[str, Any]]:
    """`run(markdown, directive)` that runs a document as `client`'s signed-in user."""
    def run(markdown: str, directive: str) -> Dict[str, Any]:
        from pyegeria.core.async_runner import run_sync
        return run_sync(async_run_markdown(client, markdown, directive))
    return run
