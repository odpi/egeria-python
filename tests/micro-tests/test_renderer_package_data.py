# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""egeria-table.js ships as pyegeria package data (D3, 2026-11-14): found by importlib.resources, unchanged
from its record, admitted by the package-data rules, and present in a built wheel."""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from pyegeria.view.renderers import RENDERER_FILES, egeria_table_js, renderer_record, static_dir

REPO = Path(__file__).resolve().parents[2]


def test_renderer_is_found_through_importlib_resources():
    assert static_dir().is_dir()
    for name in RENDERER_FILES:
        assert (static_dir() / name).is_file(), name
    assert egeria_table_js().name == "egeria-table.js"


def test_renderer_matches_its_record():
    rec = renderer_record()
    data = egeria_table_js().read_bytes()
    assert hashlib.sha256(data).hexdigest() == rec["sha256"]
    assert data.count(b"\n") == rec["lines"]
    assert rec["origin_repo"] == "odpi/egeria-workspaces" and len(rec["origin_commit"]) == 40


def test_renderer_is_standalone_and_carries_its_css():
    js = egeria_table_js().read_text(encoding="utf-8")
    assert "root.EgeriaTable = api" in js and "module.exports = api" in js
    assert "STYLE_ID" in js and "egeria-table-css" in js   # the stylesheet is in the file


def test_package_data_rules_admit_the_renderer():
    assert '"view/static/*"' in (REPO / "pyproject.toml").read_text()
    assert "recursive-include pyegeria/view/static" in (REPO / "MANIFEST.in").read_text()


def _build_wheel(out: Path) -> Path:
    uv = shutil.which("uv")
    if uv:
        cmd = [uv, "build", "--wheel", "--out-dir", str(out), str(REPO)]
    else:
        pytest.importorskip("build")
        cmd = [sys.executable, "-m", "build", "--wheel", "--outdir", str(out), str(REPO)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if proc.returncode != 0:
        pytest.fail(f"wheel build failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}")
    wheels = sorted(out.glob("pyegeria-*.whl"))
    assert wheels, f"no wheel in {out}"
    return wheels[-1]


def test_renderer_is_in_the_wheel(tmp_path):
    wheel = _build_wheel(tmp_path)
    with zipfile.ZipFile(wheel) as z:
        names = set(z.namelist())
        for name in RENDERER_FILES + ("egeria-table.js.source.json",):
            assert f"pyegeria/view/static/{name}" in names, name
        shipped = z.read("pyegeria/view/static/egeria-table.js")
    assert hashlib.sha256(shipped).hexdigest() == renderer_record()["sha256"]
