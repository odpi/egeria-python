"""PY-51: regenerating the specs and templates must be stable, and the committed copies must be current.

Two things drifted on main (46b092d6) with no change to any spec:

* md_processing/data/generated_format_sets.json was stale: every attribute now carries render, max_items,
  max_lines and label, every format a document, and the 6.4 commands (Data Value, Decision, ...) had no sets.
  Regeneration itself is deterministic; the file was just never regenerated. test_generated_format_sets_json_is_current
  keeps it that way.
* The Valid Values line of a template came out in whatever order the Egeria server returned the valid metadata
  values, which differs between servers, so a regeneration against another server rewrote the template.
  The dynamic values are now written sorted.

No Egeria: the client is a stub.
"""
from __future__ import annotations

import io
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]
COMPACT_DIR = ROOT / "md_processing" / "data" / "compact_commands"


class _StubClient:
    def __init__(self, values):
        self._values = values

    def get_valid_metadata_values(self, property_name):
        return [{"preferredValue": v} for v in self._values]


def _valid_values_line(values, usage_level="Advanced"):
    from commands.tech.generate_md_cmd_templates import _write_attr_block

    out = io.StringIO()
    attr = {"description": "d", "property_name": "renderer", "valid_values": []}
    _write_attr_block(out, "Renderer", attr, client=_StubClient(values))
    lines = [ln for ln in out.getvalue().splitlines() if "**Valid Values**" in ln]
    assert len(lines) == 1, out.getvalue()
    return lines[0]


@pytest.mark.parametrize(
    "server_order",
    [
        ["PIE", "FORM", "TABLE", "BAR"],
        ["FORM", "REPORT", "BAR", "PIE", "TABLE"],
        ["table", "Bar", "form", "Pie"],
    ],
)
def test_server_valid_values_are_written_in_a_fixed_order(server_order):
    forward = _valid_values_line(server_order)
    reverse = _valid_values_line(list(reversed(server_order)))
    assert forward == reverse
    written = forward.split("**Valid Values**: ")[1].split("; ")
    assert written == sorted(server_order, key=str.lower)


def test_the_printed_attribute_lists_valid_values_in_the_same_fixed_order(capsys):
    from commands.tech.generate_md_cmd_templates import _print_attr

    attr = {"description": "d", "property_name": "renderer", "valid_values": []}
    _print_attr("Renderer", attr, client=_StubClient(["PIE", "FORM", "BAR"]))
    printed = [ln for ln in capsys.readouterr().out.splitlines() if "Valid Values" in ln]
    assert printed and printed[0].endswith("BAR; FORM; PIE"), printed


def test_valid_values_the_spec_lists_are_left_as_written():
    from commands.tech.generate_md_cmd_templates import _write_attr_block

    out = io.StringIO()
    attr = {"description": "d", "valid_values": ["tabs", "single-column", "grid"]}
    _write_attr_block(out, "Layout Style", attr, client=None)
    assert "**Valid Values**: tabs,single-column,grid" in out.getvalue()


def _json_bytes(tmp_path, name):
    from commands.tech.gen_report_specs import build_format_sets_from_commands

    sets = build_format_sets_from_commands(str(COMPACT_DIR), usage_level=None)
    out = tmp_path / name
    sets.save_to_json(str(out))
    return out.read_bytes()


def test_two_regenerations_of_the_format_sets_give_identical_bytes(tmp_path):
    assert _json_bytes(tmp_path, "one.json") == _json_bytes(tmp_path, "two.json")


def test_generated_format_sets_json_is_current(tmp_path):
    committed = (ROOT / "md_processing" / "data" / "generated_format_sets.json").read_bytes()
    assert committed == _json_bytes(tmp_path, "fresh.json"), (
        "md_processing/data/generated_format_sets.json is stale: run refresh_specs --merge-reports"
    )
