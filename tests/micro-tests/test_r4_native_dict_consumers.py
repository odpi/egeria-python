# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""R4: the consumers that read DICT strings work on native DICT rows too
(AUDIT-NATIVE-DICT-CONSUMERS-2026-11-11 breaks 1-5 and the Glossaries Folders watch item).

Native and flat rows come from the same real fixtures (raw Egeria JSON captured read-only on laz,
replayed by report_fixture_replay.py): for each fixed consumer, both shapes give the same names.
"""
import ast
import asyncio
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

from commands.cat import my_reports
from pyegeria.view import format_set_executor as fse
from pyegeria.view.output_formatter import value_names

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("report_fixture_replay",
                                               Path(__file__).parent / "report_fixture_replay.py")
replay_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(replay_mod)


def _rows(monkeypatch, name, **kw):
    fx = replay_mod.ReportReplay(monkeypatch, name).fixture
    return fse.exec_report_spec(fx["spec"], output_format="DICT", params=dict(fx["params"]),
                                view_server="qs-view-server", view_url="https://localhost:9443",
                                user=fx["user"], user_pass="", token="replay-token", **kw)["data"]


@pytest.mark.parametrize("name, column", [("isc_register", "Containing Members"), ("isc_register", "Member Of"),
                                          ("digital_products", "Members")])
def test_native_and_flat_rows_give_the_same_names(monkeypatch, name, column):
    flat = _rows(monkeypatch, name)
    native = _rows(monkeypatch, name, dict_shape="native")
    assert any(r.get(column) for r in flat)
    for f, n in zip(flat, native):
        assert isinstance(n[column], (list, type(None), str))
        assert value_names(f[column]) == value_names(n[column])


def test_link_wrapped_flat_value_is_unwrapped():
    """Break 2: format_for_markdown_table wraps a "::" value as " [a, b](#guid) "."""
    assert value_names(" [Folder::A, Folder::B](#1234) ") == ["Folder::A", "Folder::B"]


def test_a_string_is_never_read_character_by_character():
    """Break 5 (build_domain_details): iterating a flat string made one tree leaf per character."""
    assert value_names("Capability::Finance, Capability::HR") == ["Capability::Finance", "Capability::HR"]
    assert value_names("Capability::Finance") == ["Capability::Finance"]
    assert value_names(None) == [] and value_names("") == []


def test_glossary_folders_string_still_splits():
    """Watch item: glossary_manager builds Folders as a ", \\n"-joined string, not via the native layer."""
    assert value_names("GlossaryCategory::A, \nGlossaryTerm::B") == ["GlossaryCategory::A", "GlossaryTerm::B"]


# ── The call sites ──

HANDLER = ROOT / "my_egeria" / "my_egeria" / "shop_for_data_handler.py"
DEMO = ROOT / "my_egeria" / "my_egeria" / "DemoCode" / "Data_Products_Demo" / "data_products.py"


def _exec_calls(path):
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "exec_report_spec":
            kw = {k.arg: k.value for k in node.keywords}
            yield (ast.literal_eval(kw["format_set_name"]) if isinstance(kw.get("format_set_name"), ast.Constant)
                   else "<param>"), kw


def test_the_fixed_call_sites_ask_for_native_rows():
    shapes = {name: (kw.get("dict_shape").value if kw.get("dict_shape") is not None else None)
              for name, kw in _exec_calls(HANDLER)}
    assert shapes["BusinessCapabilities"] == "native"          # build_domain_details
    assert shapes["Digital-Product-Catalog"] == "native"       # build_catalog_details
    assert shapes["<param>"] == "native"                       # _fetch_one (BasicCollections, Glossaries)


@pytest.mark.parametrize("path", [HANDLER, DEMO])
def test_no_split_on_a_dict_value_remains(path):
    text = path.read_text()
    for needle in ('collection_memberships.split(', 'str.split(root_collection_contains', 'glossary_folders.split(',
                   'member.split(', 'member_ext.split(', 'item_string.split('):
        assert needle not in text, needle


# ── The TUI: a list or dict is one cell, never extra columns (break 3) ──

class _Table:
    id = "spec_output_datatable"

    def __init__(self):
        self.columns, self.rows = [], []

    def clear(self, columns=False):
        self.columns, self.rows = [], []

    def add_column(self, name):
        self.columns.append(name)

    def add_row(self, *cells):
        self.rows.append(cells)

    def refresh(self):
        pass


class _Container:
    async def mount(self, *a, **k):
        pass


def _tui(response):
    table = _Table()
    fake = SimpleNamespace(rotated_table={}, log=lambda *a, **k: None, id="t",
                           query_one=lambda sel, cls=None: table if "datatable" in sel else _Container())
    asyncio.run(my_reports.RunSpec.display_response(fake, response))
    return table


def test_tui_list_and_dict_values_stay_in_their_column(monkeypatch):
    rows = _rows(monkeypatch, "digital_products", dict_shape="native")[:3]
    table = _tui({"kind": "json", "data": rows})
    assert table.columns == list(rows[0].keys())               # no column per list item or dict key
    members = table.columns.index("Members")
    assert table.rows[0][members] == ", ".join(value_names(rows[0]["Members"]))


def test_tui_cell():
    assert my_reports.tui_cell([str(i) for i in range(12)]) == "0, 1, 2, 3, 4, 5, 6, 7, 8, 9 (+2 more)"
    assert my_reports.tui_cell({"contactName": "Robbie"}) == '{"contactName": "Robbie"}'
    assert my_reports.tui_cell("x") == "x"
