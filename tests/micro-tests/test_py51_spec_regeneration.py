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


# --- omit empty fields (Dan: "Omit empty fields") --------------------------------------------------------
_OPTIONAL_NEW_KEYS = ("render", "max_items", "max_lines", "label", "document")


def _sample_sets():
    from pyegeria.view._output_format_models import Column, Format, FormatSet, FormatSetDict

    plain = Column(name="Display Name", key="display_name")
    rendered = Column(name="Tags", key="tags", render="join", max_items=5, max_lines=2, label="display_name")
    fs = FormatSet(
        target_type="Thing", heading="Things", description="d",
        formats=[Format(types=["LIST"], attributes=[plain, rendered])],
    )
    return FormatSetDict({"Thing-DrE-Basic": fs})


def _walk_keys(node, found):
    if isinstance(node, dict):
        for k, v in node.items():
            found.append((k, v))
            _walk_keys(v, found)
    elif isinstance(node, list):
        for v in node:
            _walk_keys(v, found)


def test_a_null_optional_field_is_not_written(tmp_path):
    import json

    sets = _sample_sets()
    path = tmp_path / "s.json"
    sets.save_to_json(str(path))
    data = json.loads(path.read_text())
    cols = data["Thing-DrE-Basic"]["formats"][0]["attributes"]
    assert not any(k in cols[0] for k in _OPTIONAL_NEW_KEYS), cols[0]
    assert (cols[1]["render"], cols[1]["max_items"], cols[1]["max_lines"], cols[1]["label"]) == ("join", 5, 2, "display_name")
    assert "document" not in data["Thing-DrE-Basic"]["formats"][0]


def test_save_then_load_gives_back_the_same_sets(tmp_path):
    from pyegeria.view._output_format_models import FormatSetDict

    sets = _sample_sets()
    path = tmp_path / "s.json"
    sets.save_to_json(str(path))
    loaded = FormatSetDict.load_from_json(str(path))
    assert loaded.to_dict() == sets.to_dict()
    assert loaded["Thing-DrE-Basic"].formats[0].attributes[0].render is None  # absent reads as the null default


def test_the_committed_generated_format_sets_json_carries_none_of_the_empty_new_fields():
    import json

    data = json.loads((ROOT / "md_processing" / "data" / "generated_format_sets.json").read_text())
    found = []
    _walk_keys(data, found)
    bad = [k for k, v in found if k in _OPTIONAL_NEW_KEYS and v is None]
    assert bad == [], f"{len(bad)} null optional fields written"


def test_the_committed_generated_format_sets_json_loads_and_round_trips(tmp_path):
    from pyegeria.view._output_format_models import FormatSetDict

    committed = ROOT / "md_processing" / "data" / "generated_format_sets.json"
    loaded = FormatSetDict.load_from_json(str(committed))
    again = tmp_path / "again.json"
    loaded.save_to_json(str(again))
    assert again.read_bytes() == committed.read_bytes()


# --- PY-52: no Egeria connection must not silently drop the Valid Values lines -----------------------------
NO_CONNECTION = "valid values not read (no Egeria connection)"


class _FailingClient:
    def get_valid_metadata_values(self, property_name):
        raise ConnectionError("platform down")


def _block(attr, client):
    from commands.tech.generate_md_cmd_templates import _write_attr_block

    out = io.StringIO()
    _write_attr_block(out, "Renderer", attr, client=client)
    return out.getvalue()


def test_without_a_connection_a_looked_up_attribute_says_its_values_were_not_read():
    text = _block({"description": "d", "property_name": "renderer", "valid_values": []}, client=None)
    assert f">\t**Valid Values**: {NO_CONNECTION}" in text


def test_a_failed_lookup_says_so_and_names_the_error():
    text = _block({"description": "d", "property_name": "renderer", "valid_values": []}, client=_FailingClient())
    line = [ln for ln in text.splitlines() if "**Valid Values**" in ln]
    assert len(line) == 1 and "valid values not read (Egeria lookup failed: ConnectionError)" in line[0], text


def test_no_marker_when_the_spec_lists_its_values_or_nothing_is_looked_up():
    listed = _block({"description": "d", "property_name": "renderer", "valid_values": ["a", "b"]}, client=None)
    assert "a,b" in listed and "not read" not in listed
    plain = _block({"description": "d", "valid_values": []}, client=None)
    assert "Valid Values" not in plain


def test_no_marker_when_the_server_answers():
    text = _block({"description": "d", "property_name": "renderer", "valid_values": []}, client=_StubClient(["B", "A"]))
    assert "**Valid Values**: A; B" in text and "not read" not in text


def test_the_printed_attribute_carries_the_same_marker(capsys):
    from commands.tech.generate_md_cmd_templates import _print_attr

    _print_attr("Renderer", {"description": "d", "property_name": "renderer", "valid_values": []}, client=None)
    assert f"Valid Values: {NO_CONNECTION}" in capsys.readouterr().out
