# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Unit tests for pyegeria.view.vega_utilities — Vega-Lite spec generators.

Pure functions, no live server / mocking needed. Verifies each generator
produces a well-formed Vega-Lite envelope for valid input and returns None
for empty/invalid input.
"""

from pyegeria.view.vega_utilities import (
    generate_vega_bar_chart,
    generate_vega_pie_chart,
    generate_vega_line_chart,
    generate_vega_area_chart,
    generate_vega_scatter_chart,
    generate_vega_funnel_chart,
    generate_vega_chart,
)


def _is_valid_envelope(spec):
    return (
        isinstance(spec, dict)
        and spec.get("$schema", "").startswith("https://vega.github.io/schema/vega-lite/")
        and "data" in spec
        and "mark" in spec
        and "encoding" in spec
    )


# ── bar / pie (pre-existing, sanity-checked here for regression coverage) ───

def test_bar_chart_valid():
    spec = generate_vega_bar_chart({"DataStore": 312, "DataSet": 268}, title="Assets by type")
    assert _is_valid_envelope(spec)
    assert spec["mark"]["type"] == "bar"
    assert len(spec["data"]["values"]) == 2


def test_pie_chart_empty_returns_none():
    assert generate_vega_pie_chart({}, title="empty") is None
    assert generate_vega_pie_chart(None, title="none") is None


# ── line ──────────────────────────────────────────────────────────────────

def test_line_chart_multiseries_fold():
    records = [
        {"label": "Jan", "assets": 100, "terms": 40},
        {"label": "Feb", "assets": 120, "terms": 45},
    ]
    spec = generate_vega_line_chart(records, x_field="label", y_fields=["assets", "terms"],
                                     title="Growth")
    assert _is_valid_envelope(spec)
    assert spec["mark"] == "line"
    assert spec["transform"] == [{"fold": ["assets", "terms"], "as": ["series", "value"]}]
    assert spec["encoding"]["x"]["field"] == "label"
    assert spec["encoding"]["color"]["field"] == "series"


def test_line_chart_single_series_string_field():
    records = [{"label": "Jan", "assets": 100}]
    spec = generate_vega_line_chart(records, x_field="label", y_fields="assets", title="Assets")
    assert spec["transform"][0]["fold"] == ["assets"]


def test_line_chart_empty_records_returns_none():
    assert generate_vega_line_chart([], x_field="label", y_fields="assets", title="x") is None
    assert generate_vega_line_chart([{"label": "Jan"}], x_field="label", y_fields=[], title="x") is None


# ── area ──────────────────────────────────────────────────────────────────

def test_area_chart_stacked_by_default():
    records = [{"label": "Jan", "governed": 30, "ungoverned": 70}]
    spec = generate_vega_area_chart(records, x_field="label", y_fields=["governed", "ungoverned"],
                                     title="Composition")
    assert _is_valid_envelope(spec)
    assert spec["mark"]["type"] == "area"
    assert "stack" not in spec["encoding"]["y"]  # default (stacked) leaves Vega-Lite's own default


def test_area_chart_unstacked_sets_stack_none():
    records = [{"label": "Jan", "a": 1, "b": 2}]
    spec = generate_vega_area_chart(records, x_field="label", y_fields=["a", "b"],
                                     title="t", stacked=False)
    assert spec["encoding"]["y"]["stack"] is None


# ── scatter ───────────────────────────────────────────────────────────────

def test_scatter_chart_valid():
    records = [{"x": 1, "y": 2}, {"x": 3, "y": 4}]
    spec = generate_vega_scatter_chart(records, x_field="x", y_field="y", title="Correlation")
    assert _is_valid_envelope(spec)
    assert spec["mark"]["type"] == "point"
    assert "color" not in spec["encoding"]


def test_scatter_chart_with_color_field():
    records = [{"x": 1, "y": 2, "zone": "clinical"}]
    spec = generate_vega_scatter_chart(records, x_field="x", y_field="y", title="t", color_field="zone")
    assert spec["encoding"]["color"]["field"] == "zone"


def test_scatter_chart_empty_returns_none():
    assert generate_vega_scatter_chart([], x_field="x", y_field="y", title="t") is None


# ── funnel ────────────────────────────────────────────────────────────────

def test_funnel_chart_preserves_order_and_computes_percent():
    stages = {"Cataloged": 1284, "Documented": 912, "Classified": 873, "AI-Ready": 612}
    spec = generate_vega_funnel_chart(stages, title="Context readiness")
    assert _is_valid_envelope(spec)
    values = spec["data"]["values"]
    assert [v["stage"] for v in values] == list(stages.keys())
    assert values[0]["pctOfFirst"] == 100.0
    assert values[-1]["pctOfFirst"] == round(100 * 612 / 1284, 1)
    assert spec["encoding"]["y"]["sort"] == list(stages.keys())


def test_funnel_chart_skips_non_numeric_stages():
    stages = {"A": 100, "B": "not-a-number", "C": 50}
    spec = generate_vega_funnel_chart(stages, title="t")
    assert [v["stage"] for v in spec["data"]["values"]] == ["A", "C"]


def test_funnel_chart_empty_returns_none():
    assert generate_vega_funnel_chart({}, title="t") is None


# ── generic escape hatch ──────────────────────────────────────────────────

def test_generate_vega_chart_assembles_envelope():
    values = [{"x": 1, "y": 2}]
    encoding = {"x": {"field": "x", "type": "quantitative"}, "y": {"field": "y", "type": "quantitative"}}
    spec = generate_vega_chart(values, mark="rule", encoding=encoding, title="Custom")
    assert _is_valid_envelope(spec)
    assert spec["mark"] == "rule"
    assert spec["encoding"] == encoding
    assert spec["description"] == "Custom"


def test_generate_vega_chart_with_transform():
    values = [{"x": 1}]
    encoding = {"x": {"field": "x", "type": "quantitative"}}
    transform = [{"filter": "datum.x > 0"}]
    spec = generate_vega_chart(values, mark="bar", encoding=encoding, title="t", transform=transform)
    assert spec["transform"] == transform


def test_generate_vega_chart_invalid_inputs_return_none():
    assert generate_vega_chart([], mark="bar", encoding={"x": {}}, title="t") is None
    assert generate_vega_chart([{"x": 1}], mark="", encoding={"x": {}}, title="t") is None
    assert generate_vega_chart([{"x": 1}], mark="bar", encoding={}, title="t") is None
