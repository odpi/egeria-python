# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""The browser renderers for pyegeria's own result shapes, shipped as package data (D3, 2026-11-14).

`egeria-table.js` draws exactly what `exec_report_spec(..., output_format="TABLE", table_shape="structured")`
emits (pyegeria.view.structured_table): the columns, the rows, the total and its basis, and every note. Shipping
it with the executor keeps the two in lockstep: a consumer on pyegeria X serves the renderer for X's shape.
Its stylesheet is inside the file (`EgeriaTable.CSS`).

Serve it from wherever pyegeria is installed (checkout, wheel, image), never by a path into another package:

    from pyegeria.view.renderers import static_dir, egeria_table_js
    app.mount("/static/pyegeria", StaticFiles(directory=static_dir()))      # FastAPI / Starlette
    egeria_table_js()          # Path to the file
    renderer_record()          # where it came from and its sha256 (egeria-table.js.source.json)

trellis-ui re-exports it at /static/trellis-ui/egeria-table.js. The Egeria Portal can serve this copy too.
Same pattern as commands/tech/spec_editor_static.
"""
from __future__ import annotations

import json
from importlib import resources
from pathlib import Path
from typing import Any, Dict

__all__ = ["RENDERER_FILES", "egeria_table_js", "renderer_record", "static_dir"]

#: Every file in pyegeria/view/static that a page loads. The wheel test checks each one is shipped.
RENDERER_FILES = ("egeria-table.js",)
_RECORD = "egeria-table.js.source.json"


def static_dir() -> Path:
    """The directory holding pyegeria's renderers, wherever pyegeria is installed."""
    return Path(str(resources.files("pyegeria.view") / "static"))


def egeria_table_js() -> Path:
    return static_dir() / "egeria-table.js"


def renderer_record() -> Dict[str, Any]:
    """egeria-table.js.source.json: the origin commit and the sha256 of the shipped file."""
    return json.loads((static_dir() / _RECORD).read_text(encoding="utf-8"))
