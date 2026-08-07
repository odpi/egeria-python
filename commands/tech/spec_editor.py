"""
spec_editor.py

A local web editor for Dr.Egeria compact command specification JSON files
(md_processing/data/compact_commands/*.json). Replaces Tinderbox as the
authoring tool for attribute_definitions / bundles / commands.

Reuses the existing parsing/validation modules rather than reimplementing
their logic:
  - md_processing.md_processing_utils.parse_compact_export
  - md_processing.md_processing_utils.validate_compact_json
  - md_processing.md_processing_utils.compact_spec_validator

Usage:
  dr_egeria_spec_editor [--port 8420] [--dir <compact_commands dir>]
"""
from __future__ import annotations

import asyncio
import io
import json
import re
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

import click
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from md_processing.md_processing_utils.parse_compact_export import resolve_bundle_chain
from md_processing.md_processing_utils.validate_compact_json import validate_compact_json
from md_processing.md_processing_utils.compact_spec_validator import validate_compact_specs

DEFAULT_COMPACT_DIR = Path(__file__).resolve().parents[2] / "md_processing" / "data" / "compact_commands"
STATIC_DIR = Path(__file__).resolve().parent / "spec_editor_static"

app = FastAPI(title="Dr.Egeria Spec Editor")
_state: dict[str, Path] = {"compact_dir": DEFAULT_COMPACT_DIR}


@app.middleware("http")
async def _no_cache(request, call_next):
    # Local single-user dev tool editing live JSON — staleness (an old
    # index.html/app.js served from the browser cache) is actively harmful,
    # so disable caching entirely rather than chase cache-busting query params.
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    return response


def _compact_dir() -> Path:
    return _state["compact_dir"]


def _family_path(family: str) -> Path:
    path = _compact_dir() / f"{family}.json"
    if not path.exists():
        raise HTTPException(404, f"Unknown family '{family}'")
    return path


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _save(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n")


_NAME_RE = re.compile(r"^commands_[a-z0-9_]+_compact$")


def _slug(family_name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", family_name.strip().lower()).strip("_")
    return f"commands_{slug}_compact"


def _references_to(data: dict[str, Any], attr_name: str) -> list[str]:
    """Where (bundle/command names) is this attribute name referenced, within one family file."""
    refs = []
    for bname, bdef in data.get("bundles", {}).items():
        if attr_name in (bdef.get("own_attributes") or []):
            refs.append(f"bundle:{bname}")
    for cname, cdef in data.get("commands", {}).items():
        if attr_name in (cdef.get("custom_attributes") or []):
            refs.append(f"command:{cname}")
    return refs


def _bundle_dependents(data: dict[str, Any], bundle_name: str) -> list[str]:
    refs = []
    for bname, bdef in data.get("bundles", {}).items():
        if bdef.get("inherits") == bundle_name:
            refs.append(f"bundle:{bname}")
    for cname, cdef in data.get("commands", {}).items():
        if cdef.get("bundle") == bundle_name:
            refs.append(f"command:{cname}")
    return refs


def _scan_attribute_families() -> dict[str, list[str]]:
    """attribute name -> list of family display names (one per file) that define it.

    Every family's Tinderbox export bakes in copies of Shared Attribute
    Definitions, so the same attribute name legitimately appears in many
    files' attribute_definitions with no structural marker distinguishing
    "family-specific" from "shared/common" — this reconstructs that
    distinction by cross-referencing all files.
    """
    out: dict[str, list[str]] = {}
    for path in sorted(_compact_dir().glob("*.json")):
        try:
            data = _load(path)
        except json.JSONDecodeError:
            continue
        family_name = data.get("family") or path.stem
        for name in data.get("attribute_definitions", {}):
            out.setdefault(name, []).append(family_name)
    return out


# ---------------------------------------------------------------- families

@app.get("/api/families")
def list_families():
    out = []
    for path in sorted(_compact_dir().glob("*.json")):
        try:
            data = _load(path)
        except json.JSONDecodeError as exc:
            out.append({"filename": path.stem, "family": None, "error": str(exc)})
            continue
        out.append({
            "filename": path.stem,
            "family": data.get("family"),
            "attribute_count": len(data.get("attribute_definitions", {})),
            "bundle_count": len(data.get("bundles", {})),
            "command_count": len(data.get("commands", {})),
        })
    return out


@app.get("/api/families/{family}")
def get_family(family: str):
    data = _load(_family_path(family))
    this_family = data.get("family")
    sharing = _scan_attribute_families()
    attribute_sharing = {
        name: [f for f in families if f != this_family]
        for name, families in sharing.items()
        if name in data.get("attribute_definitions", {})
    }
    return {**data, "attribute_sharing": attribute_sharing}


@app.post("/api/families")
def create_family(body: dict[str, Any]):
    name = (body.get("family") or "").strip()
    if not name:
        raise HTTPException(400, "family name is required")
    filename_stem = _slug(name)
    path = _compact_dir() / f"{filename_stem}.json"
    if path.exists():
        raise HTTPException(409, f"Family file '{filename_stem}.json' already exists")
    data = {
        "family": name,
        "exported": "",
        "attribute_definitions": {},
        "bundles": {},
        "commands": {},
    }
    _save(path, data)
    return {"filename": filename_stem, **data}


# --------------------------------------------------------------- attributes

@app.post("/api/families/{family}/attributes")
def create_attribute(family: str, body: dict[str, Any]):
    path = _family_path(family)
    data = _load(path)
    name = body.get("name")
    if not name:
        raise HTTPException(400, "attribute 'name' is required")
    if name in data.setdefault("attribute_definitions", {}):
        raise HTTPException(409, f"Attribute '{name}' already exists")
    data["attribute_definitions"][name] = body.get("definition", {})
    _save(path, data)
    return data["attribute_definitions"][name]


@app.put("/api/families/{family}/attributes/{name}")
def update_attribute(family: str, name: str, body: dict[str, Any]):
    path = _family_path(family)
    data = _load(path)
    if name not in data.get("attribute_definitions", {}):
        raise HTTPException(404, f"Attribute '{name}' not found")
    data["attribute_definitions"][name] = body.get("definition", {})
    _save(path, data)
    return data["attribute_definitions"][name]


@app.delete("/api/families/{family}/attributes/{name}")
def delete_attribute(family: str, name: str):
    path = _family_path(family)
    data = _load(path)
    if name not in data.get("attribute_definitions", {}):
        raise HTTPException(404, f"Attribute '{name}' not found")
    refs = _references_to(data, name)
    if refs:
        raise HTTPException(409, f"Attribute '{name}' is still referenced by: {', '.join(refs)}")
    del data["attribute_definitions"][name]
    _save(path, data)
    return {"deleted": name}


# ------------------------------------------------------------------ bundles

@app.post("/api/families/{family}/bundles")
def create_bundle(family: str, body: dict[str, Any]):
    path = _family_path(family)
    data = _load(path)
    name = body.get("name")
    if not name:
        raise HTTPException(400, "bundle 'name' is required")
    if name in data.setdefault("bundles", {}):
        raise HTTPException(409, f"Bundle '{name}' already exists")
    definition = body.get("definition", {})
    _validate_bundle_definition(data, name, definition)
    data["bundles"][name] = definition
    _save(path, data)
    return data["bundles"][name]


@app.put("/api/families/{family}/bundles/{name}")
def update_bundle(family: str, name: str, body: dict[str, Any]):
    path = _family_path(family)
    data = _load(path)
    if name not in data.get("bundles", {}):
        raise HTTPException(404, f"Bundle '{name}' not found")
    definition = body.get("definition", {})
    _validate_bundle_definition(data, name, definition)
    data["bundles"][name] = definition
    _save(path, data)
    return data["bundles"][name]


@app.delete("/api/families/{family}/bundles/{name}")
def delete_bundle(family: str, name: str):
    path = _family_path(family)
    data = _load(path)
    if name not in data.get("bundles", {}):
        raise HTTPException(404, f"Bundle '{name}' not found")
    refs = _bundle_dependents(data, name)
    if refs:
        raise HTTPException(409, f"Bundle '{name}' is still referenced by: {', '.join(refs)}")
    del data["bundles"][name]
    _save(path, data)
    return {"deleted": name}


def _validate_bundle_definition(data: dict[str, Any], name: str, definition: dict[str, Any]) -> None:
    trial_bundles = dict(data.get("bundles", {}))
    trial_bundles[name] = definition
    try:
        resolve_bundle_chain(name, trial_bundles)
    except (ValueError, KeyError) as exc:
        raise HTTPException(400, str(exc)) from exc
    known_attrs = set(data.get("attribute_definitions", {}).keys())
    unknown = [a for a in definition.get("own_attributes", []) if a not in known_attrs]
    if unknown:
        raise HTTPException(400, f"Unknown attribute name(s): {', '.join(unknown)}")


# ----------------------------------------------------------------- commands

@app.post("/api/families/{family}/commands")
def create_command(family: str, body: dict[str, Any]):
    path = _family_path(family)
    data = _load(path)
    name = body.get("name")
    if not name:
        raise HTTPException(400, "command 'name' is required")
    if name in data.setdefault("commands", {}):
        raise HTTPException(409, f"Command '{name}' already exists")
    definition = body.get("definition", {})
    _validate_command_definition(data, definition)
    data["commands"][name] = definition
    _save(path, data)
    return data["commands"][name]


@app.put("/api/families/{family}/commands/{name}")
def update_command(family: str, name: str, body: dict[str, Any]):
    path = _family_path(family)
    data = _load(path)
    if name not in data.get("commands", {}):
        raise HTTPException(404, f"Command '{name}' not found")
    definition = body.get("definition", {})
    _validate_command_definition(data, definition)
    data["commands"][name] = definition
    _save(path, data)
    return data["commands"][name]


@app.delete("/api/families/{family}/commands/{name}")
def delete_command(family: str, name: str):
    path = _family_path(family)
    data = _load(path)
    if name not in data.get("commands", {}):
        raise HTTPException(404, f"Command '{name}' not found")
    del data["commands"][name]
    _save(path, data)
    return {"deleted": name}


def _validate_command_definition(data: dict[str, Any], definition: dict[str, Any]) -> None:
    bundle_name = definition.get("bundle")
    if bundle_name and bundle_name not in data.get("bundles", {}):
        raise HTTPException(400, f"Unknown bundle '{bundle_name}'")
    known_attrs = set(data.get("attribute_definitions", {}).keys())
    unknown = [a for a in definition.get("custom_attributes", []) if a not in known_attrs]
    if unknown:
        raise HTTPException(400, f"Unknown attribute name(s): {', '.join(unknown)}")


# ---------------------------------------------------------------- validate

@app.post("/api/validate/{family}")
def validate_family(family: str):
    _family_path(family)  # 404 if missing
    buf = io.StringIO()
    with redirect_stdout(buf):
        structurally_ok = validate_compact_json(str(_compact_dir()))
    findings = validate_compact_specs(_compact_dir(), valid_om_types=None)
    return {
        "structural_ok": structurally_ok,
        "structural_output": buf.getvalue(),
        "findings": [
            {
                "severity": f.severity,
                "code": f.code,
                "command_name": f.command_name,
                "file": Path(f.file_path).name,
                "message": f.message,
            }
            for f in findings
        ],
    }


# ------------------------------------------------------------------ static

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index():
    return FileResponse(str(STATIC_DIR / "index.html"))


@click.command()
@click.option("--port", default=8420, show_default=True, type=int)
@click.option("--dir", "compact_dir", default=None, help="compact_commands directory (default: bundled location)")
def main(port: int, compact_dir: str | None) -> None:
    """Start the local Dr.Egeria spec editor web server."""
    if compact_dir:
        _state["compact_dir"] = Path(compact_dir).resolve()
    click.echo(f"Serving compact_commands from: {_state['compact_dir']}")
    click.echo(f"Open http://localhost:{port} in your browser")
    # Some pyegeria imports apply nest_asyncio, which patches asyncio.run() with a
    # signature that doesn't accept uvicorn.run()'s internal loop_factory kwarg.
    # Building the Server ourselves and calling plain asyncio.run(server.serve())
    # avoids that incompatible call path.
    config = uvicorn.Config(app, host="127.0.0.1", port=port)
    server = uvicorn.Server(config)
    asyncio.run(server.serve())


if __name__ == "__main__":
    main()
