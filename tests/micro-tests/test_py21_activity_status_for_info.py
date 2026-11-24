"""PY-21 (open half): every generated Dr.Egeria activity_status column offers the whole 6.4 ActivityStatus enum,
FOR_INFO included (ActivityStatus.java, odpi/egeria 8de9572c4d)."""
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
ENUM = ["REQUESTED", "APPROVED", "WAITING", "ACTIVATING", "IN_PROGRESS", "PAUSED", "FOR_INFO", "COMPLETED",
        "INVALID", "IGNORED", "FAILED", "CANCELLED", "ABANDONED", "OTHER"]


def _walk(o):
    if isinstance(o, dict):
        if o.get("key") == "activity_status" or o.get("field") == "activity_status":
            yield o
        for v in o.values():
            yield from _walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v)


def test_compact_activity_status_attributes_offer_the_whole_enum():
    files = sorted((ROOT / "md_processing/data/compact_commands").glob("*.json"))
    seen = 0
    for f in files:
        attrs = json.loads(f.read_text()).get("attribute_definitions", {})
        if "Activity Status" in attrs:
            seen += 1
            assert attrs["Activity Status"]["valid_values"] == ENUM, f.name
    assert seen >= 12


def test_generated_snapshot_activity_status_columns_offer_the_whole_enum():
    snap = json.loads((ROOT / "md_processing/data/generated_format_sets.json").read_text())
    cols = [c for c in _walk(snap) if c.get("valid_values")]
    assert cols
    assert all(c["valid_values"] == ENUM for c in cols)


@pytest.mark.parametrize("seed", ["Actor Manager", "Feedback", "Projects"])
def test_seed_activity_status_columns_offer_the_whole_enum(seed):
    data = json.loads((ROOT / f"pyegeria/view/seed/{seed}.json").read_text())
    cols = [c for c in _walk(data) if c.get("valid_values")]
    assert cols, seed
    assert all(c["valid_values"] == ENUM for c in cols)


def test_python_constants_offer_the_whole_enum_in_every_activity_status_column():
    from pyegeria.view.dr_egeria_reports import generated_format_sets
    cols = [c for fs in generated_format_sets.values() for f in fs.formats for c in f.attributes
            if c.key == "activity_status" and c.valid_values]
    assert cols
    assert all(list(c.valid_values) == ENUM for c in cols)
