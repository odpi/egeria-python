# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""R2: Column.render, max_items, max_lines and label (model, microflow carry, defaults).

Fixtures are raw Egeria JSON captured read-only on laz (report_fixture_replay.py)."""
import importlib.util
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

import pyegeria.view.egeria_spec_cache as esc
import pyegeria.view.microflow as mfm
from pyegeria.view import format_set_executor as fse
from pyegeria.view._output_format_models import Column, Format, FormatSet
from pyegeria.view.base_report_formats import get_report_registry
from pyegeria.view.structured_table import build_structured_table

_spec = importlib.util.spec_from_file_location("report_fixture_replay",
                                               Path(__file__).parent / "report_fixture_replay.py")
replay_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(replay_mod)
ReportReplay = replay_mod.ReportReplay


def _run(monkeypatch, name, fmt, **kw):
    fx = ReportReplay(monkeypatch, name).fixture
    return fse.exec_report_spec(fx["spec"], output_format=fmt, params=dict(fx["params"]),
                                view_server="qs-view-server", view_url="https://localhost:9443",
                                user=fx["user"], user_pass="", token="replay-token", **kw)


# ── Model ──

def test_column_accepts_the_new_fields():
    c = Column(name="Implications", key="implications", render="bullets", max_items=5, max_lines=2,
               label="display_name")
    assert (c.render, c.max_items, c.max_lines, c.label) == ("bullets", 5, 2, "display_name")
    assert Column(name="Rows", key="rows", render="subtable").detail_spec is None   # allowed: own scalar keys
    assert Column(name="a", key="a").render is None                                # unset: inferred


@pytest.mark.parametrize("bad", [{"render": "fancy"}, {"max_items": 0}, {"max_lines": -1},
                                 {"label": "short_name"}])
def test_column_refuses_bad_values(bad):
    with pytest.raises(ValidationError):
        Column(name="a", key="a", **bad)


# ── microflow carry ──

def _with_r2_fields():
    return FormatSet(heading="R2", description="d", target_type="DigitalProduct",
                     action={"function": "ProductManager.find_digital_products", "required_params": ["search_string"]},
                     formats=[Format(types=["DICT", "TABLE"], attributes=[
                         Column(name="Display Name", key="display_name"),
                         Column(name="Description", key="description", render="text", max_lines=4),
                         Column(name="Members", key="members", render="join", max_items=3),
                         Column(name="Product Manager", key="assigned_actors", label="display_name")])])


def test_round_trip_keeps_render_max_items_max_lines_and_label():
    fs = _with_r2_fields()
    mf = mfm.format_set_to_microflow(fs)
    items = mf.model_dump(exclude_none=True)["formatters"]["DICT"]["columns"]
    assert items[1] == {"field": "description", "label": "Description", "render": "text", "max_lines": 4}
    assert items[3]["related_label"] == "display_name" and items[3]["label"] == "Product Manager"
    text = mf.to_json()
    back = mfm.microflow_to_format_set(mfm.parse_microflow(text)[0], label="R2", target_type="DigitalProduct")
    cols = {c.key: c for c in back.formats[0].attributes}
    assert (cols["description"].render, cols["description"].max_lines) == ("text", 4)
    assert (cols["members"].render, cols["members"].max_items) == ("join", 3)
    assert cols["assigned_actors"].label == "display_name"
    assert cols["display_name"].render is None and cols["display_name"].label is None


def test_the_seed_carries_digital_products_labels():
    seed = json.loads((Path(mfm.__file__).parent / "seed" / "Product Manager.json").read_text())
    spec = next(s for s in seed["specs"] if s["label"] == "Digital-Products")
    items = [i for f in spec["microflow"]["formatters"].values() for i in (f.get("columns") or [])
             if isinstance(i, dict)]
    assert {i["field"] for i in items if i.get("related_label") == "display_name"} == {"assigned_actors", "governed_by"}
    cols = {c.key: c for f in get_report_registry()["Digital-Products"].formats for c in f.attributes}
    assert cols["assigned_actors"].label == "display_name" and cols["governed_by"].label == "display_name"


def _held(columns):
    mf = {"format": "microflow/1", "params": {"search_string": {"type": "string", "required": True}},
          "stages": [{"stage": "producer/find", "function": "CollectionManager.find_collections",
                      "params": {"search_string": "$search_string"}}],
          "formatters": {"DICT": {"columns": columns}}}
    props = {"class": "ReportSpecProperties", "qualifiedName": "ReportSpec::Held R2", "displayName": "Held R2",
             "description": "d", "versionIdentifier": "1.0", "category": "Product Manager", "purpose": "Held R2",
             "microflow": json.dumps(mf), "targetTypeName": "Collection", "outputTypes": ["DICT"],
             "contentStatus": "ACTIVE"}
    return {"elementHeader": {"guid": "5d0c0000-0000-0000-0000-0000000000r2",
                              "type": {"typeName": "ReportSpec", "superTypeNames": ["ReportType", "DataSpec",
                                                                                   "Collection", "Referenceable"]},
                              "versions": {"version": 1, "updateTime": "2026-11-11T20:00:00.000+00:00"}},
            "properties": props}


def test_a_held_spec_with_r2_fields_builds():
    built = esc._build(_held([{"field": "display_name", "label": "Display Name"},
                              {"field": "assigned_actors", "label": "Product Manager", "render": "join",
                               "max_items": 5, "related_label": "display_name"}]),
                       folders=[], identity="erinoverview", registry_names=set())
    col = built.format_set.formats[0].attributes[1]
    assert (col.render, col.max_items, col.label) == ("join", 5, "display_name")


@pytest.mark.parametrize("bad", [{"render": "fancy"}, {"max_items": 0}, {"related_label": "short"}])
def test_a_held_spec_with_a_bad_value_is_skipped_with_a_reason(bad):
    with pytest.raises(esc._Skip) as caught:
        esc._build(_held([{"field": "display_name", "label": "Display Name", **bad}]),
                   folders=[], identity="erinoverview", registry_names=set())
    assert caught.value.reason.startswith("the spec does not load:")


# ── label in text outputs ──

def test_label_display_name_is_per_column(monkeypatch):
    rows = _run(monkeypatch, "digital_products", "DICT")["data"]
    pm = [r["Product Manager"] for r in rows if r["Product Manager"]]
    lic = [r["License"] for r in rows if r["License"]]
    assert pm and all(v.startswith("Product Manager for") for v in pm)
    assert lic and not any("LicenseType::" in v for v in lic)
    assert all("::" in r["Members"] for r in rows)                  # unlabelled: qualifiedNames, as before


# ── Default inference ──

EXPECTED_RENDERS = {
    "risk_register": {"Description": "text", "Implications": "bullets", "Authors": "bullets"},
    "governance_metrics": {"Description": "text", "Implications": "bullets", "Outcomes": "bullets"},
    "ninety_day_plan": {"Mission": "text", "Success Criteria": "bullets"},
    "digital_products": {"Members": "join", "License": "join", "Product Manager": "join"},
    "isc_register": {"Containing Members": "count"},          # more members than max_items (10)
}


@pytest.mark.parametrize("name", sorted(EXPECTED_RENDERS))
def test_default_render_on_each_fixture(monkeypatch, name):
    cols = {c["name"]: c for c in _run(monkeypatch, name, "TABLE", table_shape="structured")["columns"]}
    for col, render in EXPECTED_RENDERS[name].items():
        assert cols[col]["render"] == render, (col, cols[col])


def test_a_spec_render_wins_over_the_default():
    out = build_structured_table([{"Implications": ["a", "b"]}],
                                 [{"name": "Implications", "key": "implications", "render": "join"}])
    assert out["columns"][0]["render"] == "join" and out["columns"][0]["type"] == "list"


def test_long_element_lists_default_to_count():
    refs = [{"guid": f"g{i}", "qualifiedName": f"QN::{i}"} for i in range(12)]
    out = build_structured_table([{"Members": refs}], [{"name": "Members", "key": "members"}])
    assert out["columns"][0]["render"] == "count"
    out = build_structured_table([{"Members": refs}], [{"name": "Members", "key": "members", "max_items": 20}])
    assert out["columns"][0]["render"] == "join"
