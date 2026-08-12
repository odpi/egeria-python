# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Unit tests for pyegeria.view._output_dashboard_sheet_models (DashboardSheet/
Placement/DashboardSheetDict) and pyegeria.view.dashboard_sheet_registry.

No live server. DashboardSheet is a deliberate co-element of FormatSet —
these tests mirror the shape of FormatSet's own tests (roundtrip, alias
lookup, merge, JSON persistence, registry collision handling).
"""

import pytest

from pyegeria.view._output_dashboard_sheet_models import (
    DashboardSheet,
    Placement,
    DashboardSheetDict,
    save_dashboard_sheets_to_json,
    load_dashboard_sheets_from_json,
)
from pyegeria.view import dashboard_sheet_registry as reg


# ── Placement / DashboardSheet basics ────────────────────────────────────────

def test_placement_defaults():
    p = Placement(ref="assets")
    assert p.span == "1"
    assert p.emphasis == "kpi"
    assert p.content is None
    # BACKLOG.md NEXT-19/NEXT-21 (egeria-workspaces-fs) -- empty perspectives
    # means "relevant to every perspective" (fail-open), not "relevant to none".
    assert p.perspectives == []
    assert p.detail_spec is None


def test_placement_accepts_perspectives_and_detail_spec():
    p = Placement(ref="assets", perspectives=["governance", "steward"], detail_spec="assets-detail")
    assert p.perspectives == ["governance", "steward"]
    assert p.detail_spec == "assets-detail"


def test_dashboard_sheet_placements_accept_dicts():
    s = DashboardSheet(name="dash", heading="Dashboard",
                        placements=[{"ref": "assets"}, {"ref": "terms", "span": "2", "emphasis": "panel"}])
    assert all(isinstance(p, Placement) for p in s.placements)
    assert s.placements[1].span == "2"
    assert s.placements[1].emphasis == "panel"


def test_dashboard_sheet_dict_roundtrip():
    s = DashboardSheet(name="dash", heading="Dashboard", description="d",
                        aliases=["Overview"], family="dashboard",
                        placements=[Placement(ref="assets")])
    d = s.dict()
    assert d["name"] == "dash"
    # Pre-existing failure fixed in passing (2026-08-11): this assertion was
    # stale since `content` was added to Placement without updating it here
    # (confirmed via git stash -- failed on main before this session's
    # perspectives/detail_spec fields were ever added). Now lists every field
    # explicitly rather than repeating the same drift.
    assert d["placements"] == [{
        "ref": "assets", "span": "1", "emphasis": "kpi",
        "content": None, "perspectives": [], "detail_spec": None,
    }]
    # round-trip through the dict form
    s2 = DashboardSheet(**d)
    assert s2.placements[0].ref == "assets"


# ── merge_with ────────────────────────────────────────────────────────────

def test_merge_with_updates_simple_fields_only_when_nonempty():
    s1 = DashboardSheet(name="dash", heading="Old", description="old-desc", family="fam1")
    s2 = DashboardSheet(name="dash", heading="New", description="", family="")
    s1.merge_with(s2)
    assert s1.heading == "New"       # updated (non-empty)
    assert s1.description == "old-desc"  # unchanged (other was empty)
    assert s1.family == "fam1"       # unchanged (other was empty)


def test_merge_with_replaces_existing_ref_and_appends_new():
    s1 = DashboardSheet(name="dash", heading="H", placements=[
        Placement(ref="assets", span="1"), Placement(ref="terms", span="1"),
    ])
    s2 = DashboardSheet(name="dash", heading="H", placements=[
        Placement(ref="assets", span="2"),  # replace
        Placement(ref="products"),          # append
    ])
    s1.merge_with(s2)
    refs = [p.ref for p in s1.placements]
    assert refs == ["assets", "terms", "products"]
    assert s1.placements[0].span == "2"


def test_merge_with_unions_aliases():
    s1 = DashboardSheet(name="dash", heading="H", aliases=["A"])
    s2 = DashboardSheet(name="dash", heading="H", aliases=["B"])
    s1.merge_with(s2)
    assert set(s1.aliases) == {"A", "B"}


# ── DashboardSheetDict lookup ─────────────────────────────────────────────

def test_dashboard_sheet_dict_lookup_by_name_alias_and_space_dash():
    sd = DashboardSheetDict()
    sd["overview-dashboard"] = DashboardSheet(name="overview-dashboard", heading="H", aliases=["Overview"])
    assert sd.get("overview-dashboard") is not None
    assert sd.get("Overview") is not None          # alias
    assert sd.get("overview dashboard") is not None  # space -> dash normalization
    assert sd.get("nope", "default") == "default"


def test_dashboard_sheet_dict_getitem_raises_keyerror():
    sd = DashboardSheetDict()
    with pytest.raises(KeyError):
        sd["missing"]


def test_dashboard_sheet_dict_contains():
    sd = DashboardSheetDict()
    sd["dash"] = DashboardSheet(name="dash", heading="H", aliases=["Overview"])
    assert "dash" in sd
    assert "Overview" in sd
    assert "nope" not in sd


def test_dashboard_sheet_dict_setitem_accepts_dict():
    sd = DashboardSheetDict()
    sd["dash"] = {"name": "dash", "heading": "H"}
    assert isinstance(sd["dash"], DashboardSheet)


def test_filter_by_family():
    sd = DashboardSheetDict()
    sd["a"] = DashboardSheet(name="a", heading="A", family="dashboard")
    sd["b"] = DashboardSheet(name="b", heading="B", family="panel-library")
    sd["c"] = DashboardSheet(name="c", heading="C")
    assert set(sd.filter_by_family("dashboard").keys()) == {"a"}
    assert set(sd.filter_by_family("").keys()) == {"c"}
    assert set(sd.filter_by_family("PANEL-LIBRARY").keys()) == {"b"}  # case-insensitive


def test_upsert_new_vs_existing():
    sd = DashboardSheetDict()
    sd.upsert("dash", DashboardSheet(name="dash", heading="H1", placements=[Placement(ref="assets")]))
    assert sd["dash"].heading == "H1"
    sd.upsert("dash", DashboardSheet(name="dash", heading="H2", placements=[Placement(ref="terms")]))
    assert sd["dash"].heading == "H2"
    assert [p.ref for p in sd["dash"].placements] == ["assets", "terms"]


# ── JSON persistence ──────────────────────────────────────────────────────

def test_save_and_load_json_roundtrip(tmp_path):
    sd = DashboardSheetDict()
    sd["dash"] = DashboardSheet(name="dash", heading="Dashboard",
                                 placements=[Placement(ref="assets"), Placement(ref="terms", span="2")])
    path = tmp_path / "sheets.json"
    save_dashboard_sheets_to_json(sd, str(path))
    assert path.exists()

    loaded = load_dashboard_sheets_from_json(str(path))
    assert set(loaded.keys()) == {"dash"}
    assert loaded["dash"].heading == "Dashboard"
    assert [p.ref for p in loaded["dash"].placements] == ["assets", "terms"]
    assert loaded["dash"].placements[1].span == "2"


def test_dashboard_sheet_dict_save_load_methods(tmp_path):
    sd = DashboardSheetDict()
    sd["dash"] = DashboardSheet(name="dash", heading="Dashboard")
    path = tmp_path / "sheets2.json"
    sd.save_to_json(str(path))
    loaded = DashboardSheetDict.load_from_json(str(path))
    assert isinstance(loaded, DashboardSheetDict)
    assert loaded["dash"].heading == "Dashboard"


def test_load_missing_file_raises():
    with pytest.raises(Exception):
        load_dashboard_sheets_from_json("/nonexistent/path/sheets.json")


# ── registry: refresh/get/register/collisions ────────────────────────────

@pytest.fixture(autouse=True)
def _reset_registry(monkeypatch):
    """Isolate registry global state across tests."""
    reg._CONFIG_DASHBOARD_SHEETS = DashboardSheetDict()
    reg._RUNTIME_DASHBOARD_SHEETS = DashboardSheetDict()
    monkeypatch.delenv("PYEGERIA_DASHBOARD_SHEETS_JSON", raising=False)
    monkeypatch.delenv("PYEGERIA_DASHBOARD_SHEETS_MODULES", raising=False)
    yield
    reg._CONFIG_DASHBOARD_SHEETS = DashboardSheetDict()
    reg._RUNTIME_DASHBOARD_SHEETS = DashboardSheetDict()


def test_get_dashboard_sheet_registry_empty_by_default():
    assert dict(reg.get_dashboard_sheet_registry()) == {}


def test_refresh_dashboard_sheets_loads_json_env_var(tmp_path, monkeypatch):
    sd = DashboardSheetDict()
    sd["dash"] = DashboardSheet(name="dash", heading="Dashboard")
    path = tmp_path / "cfg.json"
    save_dashboard_sheets_to_json(sd, str(path))

    monkeypatch.setenv("PYEGERIA_DASHBOARD_SHEETS_JSON", str(path))
    reg.refresh_dashboard_sheets()

    registry = reg.get_dashboard_sheet_registry()
    assert "dash" in registry
    assert registry["dash"].heading == "Dashboard"


def test_register_dashboard_sheets_runtime_and_unregister():
    reg.register_dashboard_sheets({"dash": DashboardSheet(name="dash", heading="H")}, source="test")
    assert "dash" in reg.get_dashboard_sheet_registry()
    assert reg.unregister_dashboard_sheet("dash") is True
    assert "dash" not in reg.get_dashboard_sheet_registry()
    assert reg.unregister_dashboard_sheet("dash") is False


def test_register_dashboard_sheets_collision_raises():
    reg.register_dashboard_sheets({"dash": DashboardSheet(name="dash", heading="H")}, source="first")
    with pytest.raises(reg.DashboardSheetCollision):
        reg.register_dashboard_sheets({"dash": DashboardSheet(name="dash", heading="H2")}, source="second")


def test_clear_runtime_dashboard_sheets():
    reg.register_dashboard_sheets({"dash": DashboardSheet(name="dash", heading="H")}, source="test")
    reg.clear_runtime_dashboard_sheets()
    assert "dash" not in reg.get_dashboard_sheet_registry()


def test_config_and_runtime_collision_raises(tmp_path, monkeypatch):
    sd = DashboardSheetDict()
    sd["dash"] = DashboardSheet(name="dash", heading="H")
    path = tmp_path / "cfg2.json"
    save_dashboard_sheets_to_json(sd, str(path))
    monkeypatch.setenv("PYEGERIA_DASHBOARD_SHEETS_JSON", str(path))
    reg.refresh_dashboard_sheets()

    reg._RUNTIME_DASHBOARD_SHEETS["dash"] = DashboardSheet(name="dash", heading="H2")
    with pytest.raises(reg.DashboardSheetCollision):
        reg.get_dashboard_sheet_registry()
