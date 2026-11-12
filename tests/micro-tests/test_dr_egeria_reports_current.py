"""pyegeria/view/dr_egeria_reports.py is the generated report specs as Python code; it must not go stale.

refresh_specs regenerates it (6.2.32). It holds the same report-spec sets as
md_processing/data/generated_format_sets.json, which refresh_specs writes in the same pass.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]


def test_view_dr_egeria_reports_matches_generated_format_sets():
    from pyegeria.view.dr_egeria_reports import generated_format_sets

    generated = json.loads((ROOT / "md_processing" / "data" / "generated_format_sets.json").read_text())
    assert sorted(generated_format_sets.keys()) == sorted(generated.keys())


def test_the_orphan_copies_are_gone():
    assert not (ROOT / "pyegeria" / "dr_egeria_reports.py").exists()
    assert not (ROOT / "pyegeria" / "config" / "dr_egeria_reports.py").exists()


def test_refresh_specs_regenerates_it():
    text = (ROOT / "commands" / "tech" / "refresh_specs.py").read_text()
    assert '"pyegeria/view/dr_egeria_reports.py", "--emit", "code"' in text
