# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Unit tests for pyegeria.view.overview_metrics -- the reusable metric/KPI
palette extracted from the Egeria Overview dashboard.

No live server: clients are MagicMocks. Verifies the native-count-vs-fallback
seam, composition helpers, and each metric function's shape.
"""

from unittest.mock import MagicMock

import pytest

from pyegeria.view import overview_metrics as om


def _mgr(**attrs):
    """A MetadataExpert-like mock with only the given attrs/methods set."""
    m = MagicMock(spec=[a for a in attrs] + ["platform_url", "view_server", "find_metadata_elements"])
    m.platform_url = "https://localhost:9443"
    m.view_server = "test-server"
    for k, v in attrs.items():
        setattr(m, k, v)
    return m


@pytest.fixture(autouse=True)
def _reset_seam_caches():
    """The count seam caches native-method detection per server; isolate tests."""
    om._count_caps.clear()
    om._native_server_ok.clear()
    yield
    om._count_caps.clear()
    om._native_server_ok.clear()


# ── count_elements: native vs fallback seam ──────────────────────────────────

def test_count_elements_uses_native_when_available():
    mgr = _mgr(count_metadata_elements=MagicMock(return_value={"count": 42}))
    n = om.count_elements(mgr, type_name="Asset")
    assert n == 42
    mgr.count_metadata_elements.assert_called_once()
    mgr.find_metadata_elements.assert_not_called()


def test_count_elements_native_returns_plain_int():
    mgr = _mgr(count_metadata_elements=MagicMock(return_value=7))
    assert om.count_elements(mgr, type_name="GlossaryTerm") == 7


def test_count_elements_falls_back_when_no_native_method():
    mgr = _mgr()
    mgr.find_metadata_elements.return_value = [{"a": 1}, {"b": 2}, {"c": 3}]
    n = om.count_elements(mgr, type_name="Asset")
    assert n == 3
    mgr.find_metadata_elements.assert_called_once()


def test_count_elements_falls_back_when_native_raises():
    mgr = _mgr(count_metadata_elements=MagicMock(side_effect=RuntimeError("not supported")))
    mgr.find_metadata_elements.return_value = [{"a": 1}]
    n = om.count_elements(mgr, type_name="Asset")
    assert n == 1
    # second call should skip native entirely (server marked unsupported)
    mgr.count_metadata_elements.reset_mock()
    om.count_elements(mgr, type_name="Asset")
    mgr.count_metadata_elements.assert_not_called()


def test_count_elements_passes_as_of_and_classifications():
    mgr = _mgr()
    mgr.find_metadata_elements.return_value = []
    om.count_elements(mgr, type_name="Asset", as_of="2026-01-01T00:00:00+00:00",
                       classifications=["ZoneMembership", "Confidentiality"])
    body = mgr.find_metadata_elements.call_args[0][0]
    assert body["asOfTime"] == "2026-01-01T00:00:00+00:00"
    assert body["matchClassifications"]["matchCriteria"] == "ANY"
    names = [c["name"] for c in body["matchClassifications"]["conditions"]]
    assert names == ["ZoneMembership", "Confidentiality"]


# ── count_relationships ──────────────────────────────────────────────────────

def test_count_relationships_default_path():
    ce = MagicMock()
    ce.get_relationships.return_value = [{"a": 1}, {"b": 2}]
    n = om.count_relationships(ce, "Certification")
    assert n == 2


def test_count_relationships_none_on_failure():
    ce = MagicMock()
    ce.get_relationships.side_effect = RuntimeError("boom")
    assert om.count_relationships(ce, "Certification") is None


def test_count_relationships_native_fast_path_via_expert():
    ce = MagicMock()
    expert = _mgr(count_relationships_between_elements=MagicMock(return_value={"count": 99}))
    n = om.count_relationships(ce, "License", expert=expert)
    assert n == 99
    ce.get_relationships.assert_not_called()


# ── counts_by_type ────────────────────────────────────────────────────────

def test_counts_by_type_composes_count_elements():
    mgr = _mgr()
    mgr.find_metadata_elements.side_effect = [[{"a": 1}] * 3, [{"a": 1}] * 5]
    rows = om.counts_by_type(mgr, [("Data Stores", "DataStore"), ("Data Sets", "DataSet")])
    assert rows == [
        {"label": "Data Stores", "type": "DataStore", "count": 3},
        {"label": "Data Sets", "type": "DataSet", "count": 5},
    ]


# ── governed_coverage ────────────────────────────────────────────────────

def test_governed_coverage_extracts_classifications_and_zones():
    mgr = _mgr()
    hits = [
        {"classifications": [{"classificationName": "Confidentiality"}]},
        {"classifications": [
            {"classificationName": "ZoneMembership",
             "classificationProperties": {"propertyValueMap": {"zoneMembership": {
                 "class": "ArrayTypePropertyValue",
                 "arrayValues": {"propertyValueMap": {"0": {"primitiveValue": "clinical-trial"}}},
             }}}},
        ]},
    ]
    mgr.find_metadata_elements.return_value = hits
    result = om.governed_coverage(mgr)
    assert result["governedCount"] == 2
    assert result["byClassification"] == {"Confidentiality": 1, "ZoneMembership": 1}
    assert result["topZones"] == [{"zone": "clinical-trial", "count": 1}]


def test_governed_coverage_capped_flag():
    mgr = _mgr()
    mgr.find_metadata_elements.return_value = [{}] * om.DEFAULT_CAP
    assert om.governed_coverage(mgr)["governedCapped"] is True


# ── certifications_summary ────────────────────────────────────────────────

def test_certifications_summary_shape_and_expiry():
    ce = MagicMock()
    from datetime import datetime, timezone, timedelta
    soon_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    far_date = (datetime.now(timezone.utc) + timedelta(days=400)).isoformat()
    ce.get_relationships.side_effect = [
        [
            {"relationshipProperties": {"coverageEnd": soon_date}, "end2": {"properties": {"displayName": "cert-A"}}},
            {"relationshipProperties": {"coverageEnd": far_date}},
        ],
        [{"x": 1}],   # License
        [],           # Exception
    ]
    result = om.certifications_summary(ce)
    assert result["active"] == 2
    assert result["expiring90"] == 1
    assert result["soon"][0]["name"] == "cert-A"
    assert result["licenses"] == 1
    assert result["exceptions"] == 0


def test_certifications_summary_degrades_on_failure():
    ce = MagicMock()
    ce.get_relationships.side_effect = RuntimeError("boom")
    result = om.certifications_summary(ce)
    assert result["active"] is None
    assert result["soon"] == []


# ── semantic_grounding ────────────────────────────────────────────────────

def test_semantic_grounding_computes_percent():
    mgr = _mgr()
    mgr.find_metadata_elements.return_value = [{}] * 100
    ce = MagicMock()
    ce.get_relationships.return_value = [{}] * 61
    result = om.semantic_grounding(mgr, ce)
    assert result["groundingLinks"] == 61
    assert result["groundingPct"] == 61


def test_semantic_grounding_handles_zero_cataloged():
    mgr = _mgr()
    mgr.find_metadata_elements.return_value = []
    ce = MagicMock()
    ce.get_relationships.return_value = []
    result = om.semantic_grounding(mgr, ce)
    assert result["groundingPct"] is None


def test_semantic_grounding_caps_at_100():
    mgr = _mgr()
    mgr.find_metadata_elements.return_value = [{}] * 10
    ce = MagicMock()
    ce.get_relationships.return_value = [{}] * 50   # more links than assets -- shouldn't happen, but don't overshoot 100%
    result = om.semantic_grounding(mgr, ce)
    assert result["groundingPct"] == 100


# ── context_readiness_funnel / people_counts / usage_context_counts ──────

def test_context_readiness_funnel_shape():
    mgr = _mgr()
    mgr.find_metadata_elements.return_value = [{}] * 5
    result = om.context_readiness_funnel(mgr)
    assert set(result.keys()) == {"cataloged", "documented", "classified", "lineage", "aiReady"}
    assert result["documented"] is None
    assert result["lineage"] is None
    assert result["aiReady"] is None


def test_people_counts_shape():
    mgr = _mgr()
    mgr.find_metadata_elements.return_value = [{}] * 2
    result = om.people_counts(mgr)
    assert set(result.keys()) == {"persons", "teams", "organizations", "itProfiles", "communities"}
    assert all(v == 2 for v in result.values())


def test_usage_context_counts_shape():
    mgr = _mgr()
    mgr.find_metadata_elements.return_value = [{}] * 4
    result = om.usage_context_counts(mgr)
    assert result == {"informationSupplyChains": 4, "blueprints": 4}


# ── feedback_summary ──────────────────────────────────────────────────────

def test_feedback_summary_sums_by_type():
    ce = MagicMock()
    ce.get_relationships.side_effect = [[{}] * 3, [{}] * 1, [], [{}] * 2, []]
    result = om.feedback_summary(ce)
    assert result["byType"] == {"ratings": 3, "comments": 1, "likes": 0, "tags": 2, "noteLogs": 0}
    assert result["total"] == 6


# ── growth_series ─────────────────────────────────────────────────────────

def test_growth_series_point_count_and_ordering():
    mgr = _mgr()
    mgr.find_metadata_elements.return_value = [{}] * 3
    series = om.growth_series(mgr, window="7d", points=4)
    assert len(series) == 4
    # last point (index -1) is "now" -- has a label/date but the loop counts down to i=0
    assert all("label" in p and "date" in p for p in series)
    assert all(p["assets"] == 3 for p in series)


def test_growth_series_custom_type_map():
    mgr = _mgr()
    mgr.find_metadata_elements.return_value = [{}] * 9
    series = om.growth_series(mgr, window="1d", points=2,
                               type_map=[("widgets", "Widget", None)])
    assert len(series) == 2
    assert all(p["widgets"] == 9 for p in series)
    assert all("assets" not in p for p in series)


def test_growth_label_granularity():
    from datetime import datetime, timezone
    d = datetime(2026, 3, 15, 14, 30, tzinfo=timezone.utc)
    assert om.growth_label(d, 3600) == "14:00"          # <= 2 days -> hourly
    assert om.growth_label(d, 7 * 86400) == "15 Mar"    # <= 120 days -> daily
    assert om.growth_label(d, 200 * 86400) == "Mar"     # > 120 days -> monthly
