# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Unit tests for pyegeria.view._output_container_models (Container/Placement/
ContainerDict) and pyegeria.view.container_registry.

No live server. Container is a deliberate co-element of FormatSet — these
tests mirror the shape of FormatSet's own tests (roundtrip, alias lookup,
merge, JSON persistence, registry collision handling).
"""

import pytest

from pyegeria.view._output_container_models import (
    Container,
    Placement,
    ContainerDict,
    save_containers_to_json,
    load_containers_from_json,
)
from pyegeria.view import container_registry as reg


# ── Placement / Container basics ─────────────────────────────────────────────

def test_placement_defaults():
    p = Placement(ref="assets")
    assert p.span == "1"
    assert p.emphasis == "kpi"


def test_container_placements_accept_dicts():
    c = Container(name="dash", heading="Dashboard",
                   placements=[{"ref": "assets"}, {"ref": "terms", "span": "2", "emphasis": "panel"}])
    assert all(isinstance(p, Placement) for p in c.placements)
    assert c.placements[1].span == "2"
    assert c.placements[1].emphasis == "panel"


def test_container_dict_roundtrip():
    c = Container(name="dash", heading="Dashboard", description="d",
                   aliases=["Overview"], family="dashboard",
                   placements=[Placement(ref="assets")])
    d = c.dict()
    assert d["name"] == "dash"
    assert d["placements"] == [{"ref": "assets", "span": "1", "emphasis": "kpi"}]
    # round-trip through the dict form
    c2 = Container(**d)
    assert c2.placements[0].ref == "assets"


# ── merge_with ────────────────────────────────────────────────────────────

def test_merge_with_updates_simple_fields_only_when_nonempty():
    c1 = Container(name="dash", heading="Old", description="old-desc", family="fam1")
    c2 = Container(name="dash", heading="New", description="", family="")
    c1.merge_with(c2)
    assert c1.heading == "New"       # updated (non-empty)
    assert c1.description == "old-desc"  # unchanged (other was empty)
    assert c1.family == "fam1"       # unchanged (other was empty)


def test_merge_with_replaces_existing_ref_and_appends_new():
    c1 = Container(name="dash", heading="H", placements=[
        Placement(ref="assets", span="1"), Placement(ref="terms", span="1"),
    ])
    c2 = Container(name="dash", heading="H", placements=[
        Placement(ref="assets", span="2"),  # replace
        Placement(ref="products"),          # append
    ])
    c1.merge_with(c2)
    refs = [p.ref for p in c1.placements]
    assert refs == ["assets", "terms", "products"]
    assert c1.placements[0].span == "2"


def test_merge_with_unions_aliases():
    c1 = Container(name="dash", heading="H", aliases=["A"])
    c2 = Container(name="dash", heading="H", aliases=["B"])
    c1.merge_with(c2)
    assert set(c1.aliases) == {"A", "B"}


# ── ContainerDict lookup ──────────────────────────────────────────────────

def test_container_dict_lookup_by_name_alias_and_space_dash():
    cd = ContainerDict()
    cd["overview-dashboard"] = Container(name="overview-dashboard", heading="H", aliases=["Overview"])
    assert cd.get("overview-dashboard") is not None
    assert cd.get("Overview") is not None          # alias
    assert cd.get("overview dashboard") is not None  # space -> dash normalization
    assert cd.get("nope", "default") == "default"


def test_container_dict_getitem_raises_keyerror():
    cd = ContainerDict()
    with pytest.raises(KeyError):
        cd["missing"]


def test_container_dict_contains():
    cd = ContainerDict()
    cd["dash"] = Container(name="dash", heading="H", aliases=["Overview"])
    assert "dash" in cd
    assert "Overview" in cd
    assert "nope" not in cd


def test_container_dict_setitem_accepts_dict():
    cd = ContainerDict()
    cd["dash"] = {"name": "dash", "heading": "H"}
    assert isinstance(cd["dash"], Container)


def test_filter_by_family():
    cd = ContainerDict()
    cd["a"] = Container(name="a", heading="A", family="dashboard")
    cd["b"] = Container(name="b", heading="B", family="panel-library")
    cd["c"] = Container(name="c", heading="C")
    assert set(cd.filter_by_family("dashboard").keys()) == {"a"}
    assert set(cd.filter_by_family("").keys()) == {"c"}
    assert set(cd.filter_by_family("PANEL-LIBRARY").keys()) == {"b"}  # case-insensitive


def test_upsert_new_vs_existing():
    cd = ContainerDict()
    cd.upsert("dash", Container(name="dash", heading="H1", placements=[Placement(ref="assets")]))
    assert cd["dash"].heading == "H1"
    cd.upsert("dash", Container(name="dash", heading="H2", placements=[Placement(ref="terms")]))
    assert cd["dash"].heading == "H2"
    assert [p.ref for p in cd["dash"].placements] == ["assets", "terms"]


# ── JSON persistence ──────────────────────────────────────────────────────

def test_save_and_load_json_roundtrip(tmp_path):
    cd = ContainerDict()
    cd["dash"] = Container(name="dash", heading="Dashboard",
                            placements=[Placement(ref="assets"), Placement(ref="terms", span="2")])
    path = tmp_path / "containers.json"
    save_containers_to_json(cd, str(path))
    assert path.exists()

    loaded = load_containers_from_json(str(path))
    assert set(loaded.keys()) == {"dash"}
    assert loaded["dash"].heading == "Dashboard"
    assert [p.ref for p in loaded["dash"].placements] == ["assets", "terms"]
    assert loaded["dash"].placements[1].span == "2"


def test_container_dict_save_load_methods(tmp_path):
    cd = ContainerDict()
    cd["dash"] = Container(name="dash", heading="Dashboard")
    path = tmp_path / "containers2.json"
    cd.save_to_json(str(path))
    loaded = ContainerDict.load_from_json(str(path))
    assert isinstance(loaded, ContainerDict)
    assert loaded["dash"].heading == "Dashboard"


def test_load_missing_file_raises():
    with pytest.raises(Exception):
        load_containers_from_json("/nonexistent/path/containers.json")


# ── registry: refresh/get/register/collisions ────────────────────────────

@pytest.fixture(autouse=True)
def _reset_registry(monkeypatch):
    """Isolate registry global state across tests."""
    reg._CONFIG_CONTAINERS = ContainerDict()
    reg._RUNTIME_CONTAINERS = ContainerDict()
    monkeypatch.delenv("PYEGERIA_CONTAINERS_JSON", raising=False)
    monkeypatch.delenv("PYEGERIA_CONTAINERS_MODULES", raising=False)
    yield
    reg._CONFIG_CONTAINERS = ContainerDict()
    reg._RUNTIME_CONTAINERS = ContainerDict()


def test_get_container_registry_empty_by_default():
    assert dict(reg.get_container_registry()) == {}


def test_refresh_containers_loads_json_env_var(tmp_path, monkeypatch):
    cd = ContainerDict()
    cd["dash"] = Container(name="dash", heading="Dashboard")
    path = tmp_path / "cfg.json"
    save_containers_to_json(cd, str(path))

    monkeypatch.setenv("PYEGERIA_CONTAINERS_JSON", str(path))
    reg.refresh_containers()

    registry = reg.get_container_registry()
    assert "dash" in registry
    assert registry["dash"].heading == "Dashboard"


def test_register_containers_runtime_and_unregister():
    reg.register_containers({"dash": Container(name="dash", heading="H")}, source="test")
    assert "dash" in reg.get_container_registry()
    assert reg.unregister_container("dash") is True
    assert "dash" not in reg.get_container_registry()
    assert reg.unregister_container("dash") is False


def test_register_containers_collision_raises():
    reg.register_containers({"dash": Container(name="dash", heading="H")}, source="first")
    with pytest.raises(reg.ContainerCollision):
        reg.register_containers({"dash": Container(name="dash", heading="H2")}, source="second")


def test_clear_runtime_containers():
    reg.register_containers({"dash": Container(name="dash", heading="H")}, source="test")
    reg.clear_runtime_containers()
    assert "dash" not in reg.get_container_registry()


def test_config_and_runtime_collision_raises(tmp_path, monkeypatch):
    cd = ContainerDict()
    cd["dash"] = Container(name="dash", heading="H")
    path = tmp_path / "cfg2.json"
    save_containers_to_json(cd, str(path))
    monkeypatch.setenv("PYEGERIA_CONTAINERS_JSON", str(path))
    reg.refresh_containers()

    reg._RUNTIME_CONTAINERS["dash"] = Container(name="dash", heading="H2")
    with pytest.raises(reg.ContainerCollision):
        reg.get_container_registry()
