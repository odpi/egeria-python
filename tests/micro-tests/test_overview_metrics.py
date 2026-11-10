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


def _pages(rows):
    """A get_relationships / find_metadata_elements fake that pages like Egeria: the rows from the
    body's startFrom (where the scans put it), then an empty page -- the only end-of-scan signal."""
    def fake(*args, **kw):
        body = kw.get("body") or next((a for a in args if isinstance(a, dict)), None) or {}
        start = body.get("startFrom", kw.get("start_from", 0)) or 0
        size = body.get("pageSize", kw.get("page_size", 0)) or om.DEFAULT_CAP
        return list(rows[start:start + size])
    return fake


def _by_type(table):
    """A paging get_relationships fake keyed by relationship type; an exception value is raised."""
    def fake(*args, relationship_type=None, **kw):
        rows = table.get(relationship_type, [])
        if isinstance(rows, BaseException):
            raise rows
        return _pages(rows)(*args, **kw)
    return fake


def _native(answer):
    """A native count method fake: `answer(body)` gives the count for each request body."""
    return MagicMock(side_effect=lambda body, **kw: {"count": answer(body)})


def _has_desc_neq(body):
    conds = (body.get("searchProperties") or {}).get("conditions") or []
    return any(c.get("property") == "description" and c.get("operator") == "NEQ" for c in conds)


def _classified(body, name):
    conds = (body.get("matchClassifications") or {}).get("conditions") or []
    return any(c.get("name") == name for c in conds)


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
    mgr.find_metadata_elements.side_effect = _pages([{"a": 1}, {"b": 2}, {"c": 3}])
    n = om.count_elements(mgr, type_name="Asset", population="viewer")
    assert n == 3
    mgr.find_metadata_elements.assert_called_once()


def test_count_elements_falls_back_when_native_raises():
    mgr = _mgr(count_metadata_elements=MagicMock(side_effect=RuntimeError("not supported")))
    mgr.find_metadata_elements.side_effect = _pages([{"a": 1}])
    n = om.count_elements(mgr, type_name="Asset", population="viewer")
    assert n == 1
    # second call should skip native entirely (server marked unsupported)
    mgr.count_metadata_elements.reset_mock()
    om.count_elements(mgr, type_name="Asset", population="viewer")
    mgr.count_metadata_elements.assert_not_called()


def test_count_elements_passes_as_of_and_classifications():
    mgr = _mgr()
    mgr.find_metadata_elements.side_effect = _pages([])
    om.count_elements(mgr, type_name="Asset", as_of="2026-01-01T00:00:00+00:00",
                       classifications=["ZoneMembership", "Confidentiality"], population="viewer")
    body = mgr.find_metadata_elements.call_args[0][0]
    assert body["asOfTime"] == "2026-01-01T00:00:00+00:00"
    assert body["matchClassifications"]["matchCriteria"] == "ANY"
    names = [c["name"] for c in body["matchClassifications"]["conditions"]]
    assert names == ["ZoneMembership", "Confidentiality"]


# ── count_relationships ──────────────────────────────────────────────────────

def test_count_relationships_viewer_path_without_expert():
    ce = MagicMock()
    ce.get_relationships.side_effect = _pages([{"a": 1}, {"b": 2}])
    n = om.count_relationships(ce, "Certification", population="viewer")
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
    mgr = _mgr(count_metadata_elements=MagicMock(side_effect=[3, 5]))
    rows = om.counts_by_type(mgr, [("Data Stores", "DataStore"), ("Data Sets", "DataSet")])
    assert rows == [
        {"label": "Data Stores", "type": "DataStore", "count": 3},
        {"label": "Data Sets", "type": "DataSet", "count": 5},
    ]


# ── sum_counts / sum_type_counts (BACKLOG.md NEXT-18) ────────────────────────

def test_sum_counts_totals_a_counts_by_type_result():
    by_type = [
        {"label": "Data Stores", "type": "DataStore", "count": 3},
        {"label": "Data Sets", "type": "DataSet", "count": 5},
    ]
    assert om.sum_counts(by_type) == {"total": 8, "byType": by_type}


def test_sum_counts_ignores_the_unused_client_arg():
    # mgr is accepted but unused -- present purely for calling-convention
    # consistency with an analytic step that DOES need to fetch more.
    by_type = [{"label": "A", "type": "Alpha", "count": 2}]
    assert om.sum_counts(by_type, mgr=object()) == {"total": 2, "byType": by_type}


def test_sum_type_counts_runs_the_real_fetch_then_analytic_pipeline():
    # End-to-end through run_analytic_action -- not a mocked shortcut -- using
    # a real MetadataExpert-shaped mock, same convention as the
    # counts_by_type test above.
    mgr = _mgr(count_metadata_elements=MagicMock(side_effect=[3, 5]))
    result = om.sum_type_counts(mgr, [("Data Stores", "DataStore"), ("Data Sets", "DataSet")])
    assert result == {
        "total": 8,
        "byType": [
            {"label": "Data Stores", "type": "DataStore", "count": 3},
            {"label": "Data Sets", "type": "DataSet", "count": 5},
        ],
    }


def test_sum_type_counts_is_registered_with_a_matching_action_spec():
    from pyegeria.view.analytic_registry import get_analytic_registry

    spec = get_analytic_registry()["sum_type_counts"]
    assert spec.function == "pyegeria.view.overview_metrics.sum_type_counts"
    assert spec.action is not None
    assert spec.action.fetch == "pyegeria.view.overview_metrics.counts_by_type"
    assert spec.action.analytic == "pyegeria.view.overview_metrics.sum_counts"


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
    mgr.find_metadata_elements.side_effect = _pages(hits)
    result = om.governed_coverage(mgr)
    assert result["governedCount"] == 2
    assert result["byClassification"] == {"Confidentiality": 1, "ZoneMembership": 1}
    assert result["topZones"] == [{"zone": "clinical-trial", "count": 1}]


def test_governed_coverage_pages_past_the_first_page():
    # Every page is read until Egeria returns an empty one: 501 governed elements is 501, not "at least 500".
    mgr = _mgr()
    hits = [{"elementGUID": f"g{i}", "classifications": [{"classificationName": "Confidentiality"}]}
            for i in range(om.DEFAULT_CAP + 1)]
    mgr.find_metadata_elements.side_effect = _pages(hits)
    r = om.governed_coverage(mgr)
    assert r["governedCount"] == om.DEFAULT_CAP + 1 and r["governedCapped"] is False
    assert r["byClassification"] == {"Confidentiality": om.DEFAULT_CAP + 1}
    assert [c.args[0]["startFrom"] for c in mgr.find_metadata_elements.call_args_list] == [0, 500, 1000]


def test_governed_coverage_incomplete_scan_is_not_measured():
    # A server that ignores startFrom repeats its page: the scan is incomplete, so nothing is reported.
    mgr = _mgr()
    mgr.find_metadata_elements.return_value = [{"elementGUID": f"g{i}"} for i in range(om.DEFAULT_CAP)]
    with om.recording_unmeasured() as notes:
        r = om.governed_coverage(mgr)
    assert r["governedCount"] is None and r["governedCapped"] is None and r["fullyGoverned"] is None
    assert notes and "repeated only what it had already read" in notes[0]["reason"]


# ── certifications_summary ────────────────────────────────────────────────

def test_certifications_summary_shape_and_expiry():
    ce = MagicMock()
    from datetime import datetime, timezone, timedelta
    soon_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    far_date = (datetime.now(timezone.utc) + timedelta(days=400)).isoformat()
    ce.get_relationships.side_effect = _by_type({
        "Certification": [
            {"relationshipProperties": {"coverageEnd": soon_date}, "end2": {"properties": {"displayName": "cert-A"}}},
            {"relationshipProperties": {"coverageEnd": far_date}},
        ],
        "License": [{"x": 1}],
        "Exception": [],
    })
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

def _assignment(i, asset, end1_type=("CSVFile", ["DataFile", "Asset", "Referenceable"])):
    type_name, supers = end1_type
    return {"relationshipHeader": {"guid": f"r{i}"},
            "end1": {"guid": asset, "type": {"typeName": type_name, "superTypeNames": supers}},
            "end2": {"guid": f"t{i}", "type": {"typeName": "GlossaryTerm", "superTypeNames": ["Referenceable"]}}}


def test_semantic_grounding_computes_percent():
    mgr = _mgr(count_metadata_elements=MagicMock(return_value=100),
               count_relationships_between_elements=MagicMock(return_value=61))
    ce = MagicMock()
    ce.get_relationships.side_effect = _pages([])
    result = om.semantic_grounding(mgr, ce)
    assert result["groundingLinks"] == 61
    assert result["groundingPct"] == 61
    # links: both native counts in the repository population; the relationship count goes through mgr (R4).
    # grounded Assets: the Asset total in the viewer population (the scan's own population).
    assert sorted(c.kwargs["push_down"] for c in mgr.count_metadata_elements.call_args_list) == [False, True]
    assert mgr.count_relationships_between_elements.call_args.kwargs == {"push_down": True}


def test_semantic_grounding_counts_distinct_assets_not_links():
    # 6 links: asset a1 three times, a2 twice, and one link to a non-Asset (a glossary category)
    rels = [_assignment(0, "a1"), _assignment(1, "a1"), _assignment(2, "a1"), _assignment(3, "a2"),
            _assignment(4, "a2"), _assignment(5, "c1", ("GlossaryCategory", ["Referenceable"]))]
    mgr = _mgr(count_metadata_elements=MagicMock(return_value=40),
               count_relationships_between_elements=MagicMock(return_value=6))
    ce = MagicMock()
    ce.get_relationships.side_effect = _pages(rels)
    result = om.semantic_grounding(mgr, ce)
    assert result["groundedAssets"] == 2          # distinct Assets, not 6 links
    assert result["groundedAssetTotal"] == 40         # the viewer Asset total
    assert result["groundedAssetPct"] == 5            # 2 / 40
    assert result["groundingLinks"] == 6 and result["groundingPct"] == 15   # links per hundred Assets


def test_semantic_grounding_share_is_not_measured_when_the_viewer_asset_total_is_not():
    rels = [_assignment(0, "a1"), _assignment(1, "a2")]

    def count(body, push_down=None, **kw):
        if push_down is False:
            raise TimeoutError("viewer count timed out")
        return 100

    mgr = _mgr(count_metadata_elements=MagicMock(side_effect=count),
               count_relationships_between_elements=MagicMock(return_value=2))
    mgr.find_metadata_elements.side_effect = lambda *a, **k: [{"elementHeader": {"guid": f"x{i}"}} for i in range(om.DEFAULT_CAP)]
    ce = MagicMock()
    ce.get_relationships.side_effect = _pages(rels)
    with om.recording_unmeasured() as notes:
        result = om.semantic_grounding(mgr, ce)
    assert result["groundedAssets"] == 2           # the count always shows
    assert result["groundedAssetTotal"] is None and result["groundedAssetPct"] is None   # never mixed populations
    assert any(n["count"] == "Asset" for n in notes)
    assert result["groundingLinks"] == 2 and result["groundingPct"] == 2


def test_semantic_grounding_handles_zero_cataloged():
    mgr = _mgr()
    mgr.find_metadata_elements.side_effect = _pages([])
    ce = MagicMock()
    ce.get_relationships.side_effect = _pages([])
    result = om.semantic_grounding(mgr, ce)
    assert result["groundingPct"] is None


def test_semantic_grounding_caps_at_100():
    # more links than assets -- shouldn't happen, but don't overshoot 100%
    mgr = _mgr(count_metadata_elements=MagicMock(return_value=10),
               count_relationships_between_elements=MagicMock(return_value=50))
    ce = MagicMock()
    result = om.semantic_grounding(mgr, ce)
    assert result["groundingPct"] == 100


# ── context_readiness_funnel / people_counts / usage_context_counts ──────

def _funnel_mgr():
    def answer(body):
        if _has_desc_neq(body):
            return 2
        if body.get("matchClassifications"):
            return 4
        return 5
    return _mgr(count_metadata_elements=_native(answer),
                count_relationships_between_elements=MagicMock(return_value=3))


def test_context_readiness_funnel_shape():
    mgr = _funnel_mgr()
    ce = MagicMock()
    result = om.context_readiness_funnel(mgr, ce)
    assert set(result.keys()) == {"cataloged", "documented", "classified", "lineage", "aiReady"}
    # aiReady still isn't computed -- it needs a true cross-criteria
    # intersection, not another independent count (see NEXT-18).
    assert result == {"cataloged": 5, "documented": 2, "classified": 4, "lineage": 3, "aiReady": None}
    ce.get_relationships.assert_not_called()
    mgr.find_metadata_elements.assert_not_called()


def test_context_readiness_funnel_is_all_native_repository_counts():
    mgr = _funnel_mgr()
    om.context_readiness_funnel(mgr, MagicMock())
    calls = mgr.count_metadata_elements.call_args_list + mgr.count_relationships_between_elements.call_args_list
    assert len(calls) == 4 and all(c.kwargs == {"push_down": True} for c in calls)
    documented = [c.args[0] for c in mgr.count_metadata_elements.call_args_list if _has_desc_neq(c.args[0])]
    cond = documented[0]["searchProperties"]["conditions"][0]
    assert documented[0]["metadataElementTypeName"] == "Asset"
    assert (cond["operator"], cond["value"]["primitiveValue"]) == ("NEQ", "")


# ── ai_ready_assets ──────────────────────────────────────────────────────

def _asset(guid, description=None, classifications=None):
    """Build a fake find_metadata_elements-shaped Asset element."""
    props = {}
    if description is not None:
        props["description"] = {"primitiveValue": description}
    return {
        "elementGUID": guid,
        "elementProperties": {"propertyValueMap": props},
        "classifications": [{"classificationName": c} for c in (classifications or [])],
    }


def test_ai_ready_assets_requires_all_three_criteria():
    mgr = _mgr()
    mgr.find_metadata_elements.side_effect = _pages([
        _asset("a1", "documented", ["Confidentiality"]),   # governed + documented, NOT lineage-traced
        _asset("a2", "documented", ["Confidentiality"]),   # governed + documented + lineage-traced -> AI-ready
        _asset("a3", None, ["Confidentiality"]),            # governed + lineage-traced, NOT documented
        _asset("a4", "documented", []),                     # documented + lineage-traced, NOT governed
    ])
    ce = MagicMock()
    ce.get_relationships.side_effect = _pages([
        {"end1": {"guid": "a2"}, "end2": {"guid": "a3"}},
        {"end1": {"guid": "a4"}, "end2": {"guid": "other-asset"}},
    ])
    result = om.ai_ready_assets(mgr, ce)
    assert result == {"aiReadyCount": 1, "total": 4, "capped": False}


def test_ai_ready_assets_empty_catalog():
    mgr = _mgr()
    mgr.find_metadata_elements.side_effect = _pages([])
    ce = MagicMock()
    ce.get_relationships.side_effect = _pages([])
    result = om.ai_ready_assets(mgr, ce)
    assert result == {"aiReadyCount": 0, "total": 0, "capped": False}


def test_ai_ready_assets_lineage_query_failure_is_unmeasured():
    mgr = _mgr()
    mgr.find_metadata_elements.side_effect = _pages([
        _asset("a1", "documented", ["Confidentiality"]),
    ])
    ce = MagicMock()
    ce.get_relationships.side_effect = Exception("boom")
    result = om.ai_ready_assets(mgr, ce)
    # lineage query failed -> aiReadyCount is unmeasured (None), not 0, and not a crash (RS-W2-1a)
    assert result["aiReadyCount"] is None
    assert result["total"] == 1


# ── asset_modality ───────────────────────────────────────────────────────

def _typed(type_name, super_type_names=None):
    return {"type": {"typeName": type_name, "superTypeNames": super_type_names or []}}


def test_asset_modality_tabular_leaf_type():
    assert om.asset_modality(_typed("RelationalColumn")) == "tabular"


def test_asset_modality_text_media_leaf_type():
    assert om.asset_modality(_typed("PDFFile")) == "text_media"


def test_asset_modality_resolves_via_supertype_chain():
    # A subtype not itself listed, but whose supertype chain includes one --
    # e.g. a connector-specific DataFile subtype.
    assert om.asset_modality(_typed("CustomLogFile", ["DataFile", "DataStore", "Asset"])) == "text_media"


def test_asset_modality_unknown_type_is_other_not_a_guess():
    assert om.asset_modality(_typed("APIEndpoint")) == "other"


def test_asset_modality_missing_type_block_is_other():
    assert om.asset_modality({}) == "other"


# ── drl_readiness_gates ──────────────────────────────────────────────────

def _asset_full(guid, description=None, classifications=None, type_name=None, update_time=None):
    el = _asset(guid, description, classifications)
    if type_name:
        el["type"] = {"typeName": type_name, "superTypeNames": []}
    if update_time:
        el["elementHeader"] = {"versions": {"updateTime": update_time}}
    return el


def test_drl_readiness_gates_narrows_ai_ready_by_recency():
    mgr = _mgr()
    mgr.find_metadata_elements.side_effect = _pages([
        _asset_full("a1", "documented", ["Confidentiality"], "RelationalTable",
                    update_time="2026-08-01T00:00:00Z"),   # AI-ready + recent
        _asset_full("a2", "documented", ["Confidentiality"], "PDFFile",
                    update_time="2020-01-01T00:00:00Z"),   # AI-ready, stale
        _asset_full("a3", None, ["Confidentiality"], "APIEndpoint"),  # not documented
    ])
    ce = MagicMock()
    ce.get_relationships.side_effect = _pages([
        {"end1": {"guid": "a1"}, "end2": {"guid": "x"}},
        {"end1": {"guid": "a2"}, "end2": {"guid": "y"}},
    ])
    result = om.drl_readiness_gates(mgr, ce, as_of="2026-08-02T00:00:00Z", recency_days=180)
    assert result["total"] == 3
    assert result["aiReadyCount"] == 2
    assert result["aiReadyRecentCount"] == 1
    assert result["byModality"] == {"tabular": 1, "text_media": 1, "other": 1}


def test_drl_readiness_gates_empty_catalog():
    mgr = _mgr()
    mgr.find_metadata_elements.side_effect = _pages([])
    ce = MagicMock()
    ce.get_relationships.side_effect = _pages([])
    result = om.drl_readiness_gates(mgr, ce)
    assert result["total"] == 0
    assert result["aiReadyCount"] == 0
    assert result["aiReadyRecentCount"] == 0
    assert result["byModality"] == {"tabular": 0, "text_media": 0, "other": 0}


def test_drl_readiness_gates_missing_update_time_not_counted_recent():
    mgr = _mgr()
    mgr.find_metadata_elements.side_effect = _pages([
        _asset_full("a1", "documented", ["Confidentiality"], "RelationalTable"),  # no updateTime
    ])
    ce = MagicMock()
    ce.get_relationships.side_effect = _pages([{"end1": {"guid": "a1"}, "end2": {"guid": "x"}}])
    result = om.drl_readiness_gates(mgr, ce)
    assert result["aiReadyCount"] == 1
    assert result["aiReadyRecentCount"] == 0


def _bv_mgr(asset=4, confidential=2, described=2, duplicate=0):
    def answer(body):
        if _classified(body, "ConsolidatedDuplicate"):
            return duplicate
        if _classified(body, "Confidentiality"):
            return confidential
        if _has_desc_neq(body):
            return described
        return asset
    return _mgr(count_metadata_elements=_native(answer))


def test_business_value_signals_counts_each_signal_natively():
    mgr = _bv_mgr()
    result = om.business_value_signals(mgr)
    assert result == {
        "assetTotal": 4, "assetCapped": False,
        "confidentialCount": 2, "describedCount": 2, "duplicateCount": 0,
    }
    mgr.find_metadata_elements.assert_not_called()
    bodies = [c.args[0] for c in mgr.count_metadata_elements.call_args_list]
    assert all(c.kwargs == {"push_down": True} for c in mgr.count_metadata_elements.call_args_list)
    confidential = next(b for b in bodies if _classified(b, "Confidentiality"))
    assert confidential["metadataElementTypeName"] == "Asset"   # Asset-scoped, unlike governed_coverage


def test_business_value_signals_is_never_capped_at_the_page_size():
    result = om.business_value_signals(_bv_mgr(asset=26994))
    assert result["assetTotal"] == 26994 and result["assetCapped"] is False


def test_business_value_signals_counts_duplicates_separately():
    assert om.business_value_signals(_bv_mgr(duplicate=2))["duplicateCount"] == 2


def test_business_value_signals_empty_catalog():
    result = om.business_value_signals(_bv_mgr(0, 0, 0, 0))
    assert result == {
        "assetTotal": 0, "assetCapped": False,
        "confidentialCount": 0, "describedCount": 0, "duplicateCount": 0,
    }


def test_business_value_signals_viewer_population_on_request():
    mgr = _bv_mgr()
    om.business_value_signals(mgr, population="viewer")
    assert all(c.kwargs == {"push_down": False} for c in mgr.count_metadata_elements.call_args_list)


def test_people_counts_shape():
    mgr = _mgr(count_metadata_elements=MagicMock(return_value=2))
    result = om.people_counts(mgr)
    assert set(result.keys()) == {"persons", "teams", "organizations", "itProfiles", "communities"}
    assert all(v == 2 for v in result.values())


def test_usage_context_counts_shape():
    mgr = _mgr(count_metadata_elements=MagicMock(return_value=4))
    result = om.usage_context_counts(mgr)
    assert result == {"informationSupplyChains": 4, "blueprints": 4}


# ── feedback_summary ──────────────────────────────────────────────────────

def test_feedback_summary_sums_by_type():
    ce = MagicMock()
    ce.get_relationships.side_effect = _by_type({"AttachedRating": [{}] * 3, "AttachedComment": [{}],
                                                 "AttachedTag": [{}] * 2})
    result = om.feedback_summary(ce, population="viewer")
    assert result["byType"] == {"ratings": 3, "comments": 1, "likes": 0, "tags": 2, "noteLogs": 0}
    assert result["total"] == 6


def test_feedback_summary_counts_the_repository_through_a_client_with_the_native_count():
    # PlainSupply hands an EgeriaTech for ce, which has the native relationship count.
    ce = _mgr(count_relationships_between_elements=MagicMock(side_effect=[3, 1, 0, 2, 0]), get_relationships=MagicMock())
    result = om.feedback_summary(ce)
    assert result["total"] == 6
    assert all(c.kwargs == {"push_down": True} for c in ce.count_relationships_between_elements.call_args_list)
    ce.get_relationships.assert_not_called()


# ── growth_series ─────────────────────────────────────────────────────────

def test_growth_series_point_count_and_ordering():
    mgr = _mgr(count_metadata_elements=MagicMock(return_value=3))
    series = om.growth_series(mgr, window="7d", points=4)
    assert len(series) == 4
    # last point (index -1) is "now" -- has a label/date but the loop counts down to i=0
    assert all("label" in p and "date" in p for p in series)
    assert all(p["assets"] == 3 for p in series)
    assert all(c.kwargs == {"push_down": True} for c in mgr.count_metadata_elements.call_args_list)
    mgr.find_metadata_elements.assert_not_called()


def test_growth_series_viewer_population_on_request():
    mgr = _mgr(count_metadata_elements=MagicMock(return_value=3))
    om.growth_series(mgr, window="7d", points=2, population="viewer")
    assert all(c.kwargs == {"push_down": False} for c in mgr.count_metadata_elements.call_args_list)
    with pytest.raises(ValueError):
        om.growth_series(mgr, window="7d", points=2, population="everyone")


def test_growth_series_custom_type_map():
    mgr = _mgr(count_metadata_elements=MagicMock(return_value=9))
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


# ── term_definition_completeness ──────────────────────────────────────────

def test_term_definition_completeness_divides_two_repository_counts():
    mgr = _mgr(count_metadata_elements=_native(lambda b: 536 if _has_desc_neq(b) else 1061))
    result = om.term_definition_completeness(mgr)
    assert result == {"total": 1061, "defined": 536, "undefinedPct": 49}
    calls = mgr.count_metadata_elements.call_args_list
    assert len(calls) == 2 and all(c.kwargs == {"push_down": True} for c in calls)
    assert all(c.args[0]["metadataElementTypeName"] == "GlossaryTerm" for c in calls)
    mgr.find_metadata_elements.assert_not_called()   # no capped scan: the total is never the page size


def test_term_definition_completeness_empty_glossary():
    mgr = _mgr(count_metadata_elements=MagicMock(return_value=0))
    result = om.term_definition_completeness(mgr)
    assert result == {"total": 0, "defined": 0, "undefinedPct": None}


def test_term_definition_completeness_unmeasured_numerator_is_no_percentage():
    def answer(body):
        if _has_desc_neq(body):
            raise RuntimeError("TIMEOUT_ERROR_408 timed out")
        return 1061
    mgr = _mgr(count_metadata_elements=MagicMock(side_effect=lambda b, **kw: {"count": answer(b)}))
    with om.recording_unmeasured() as notes:
        result = om.term_definition_completeness(mgr)
    assert result == {"total": 1061, "defined": None, "undefinedPct": None}
    assert notes[0]["count"] == "GlossaryTerm with description != ''"


# ── active_contributors ───────────────────────────────────────────────────

def test_active_contributors_dedupes_by_username_across_types():
    ce = MagicMock()
    ce.get_relationships.side_effect = _by_type({
        "AttachedRating": [{"relationshipHeader": {"guid": "r1", "versions": {"createdBy": "alice"}}},
                           {"relationshipHeader": {"guid": "r2", "versions": {"createdBy": "alice"}}}],
        "AttachedComment": [{"relationshipHeader": {"guid": "c1", "versions": {"createdBy": "bob"}}}],
        "AttachedNoteLog": [{"relationshipHeader": {"guid": "n1", "versions": {"createdBy": "alice"}}}],
    })
    result = om.active_contributors(ce)
    assert result["contributors"] == 2  # alice, bob
    assert result["byType"] == {"ratings": 1, "comments": 1, "likes": 0, "tags": 0, "noteLogs": 1}


def test_active_contributors_degrades_per_type_on_failure():
    ce = MagicMock()
    ce.get_relationships.side_effect = _by_type({
        "AttachedRating": RuntimeError("boom"),
        "AttachedComment": [{"relationshipHeader": {"versions": {"createdBy": "bob"}}}],
    })
    result = om.active_contributors(ce)
    # the failed type is unmeasured (None), and so is the union it would be part of (RS-W2-1a)
    assert result["byType"]["ratings"] is None
    assert result["byType"]["comments"] == 1
    assert result["contributors"] is None


# ── metric_trend ──────────────────────────────────────────────────────────

def test_metric_trend_calls_target_once_per_point_and_merges_dict_result():
    mgr = _mgr(count_metadata_elements=MagicMock(return_value=3))
    series = om.metric_trend(
        mgr, MagicMock(), "people_counts",
        window="7d", points=3,
    )
    assert len(series) == 3
    assert all("label" in p and "date" in p and p["persons"] == 3 for p in series)


def test_metric_trend_scalar_result_stored_under_value():
    mgr = _mgr(count_metadata_elements=MagicMock(return_value=5))
    series = om.metric_trend(
        mgr, MagicMock(), "count_elements",
        window="7d", points=2, metric_params={"type_name": "Asset"},
    )
    assert len(series) == 2
    assert all(p["value"] == 5 for p in series)


def test_metric_trend_snapshot_failure_yields_none_not_raise():
    mgr = _mgr()
    mgr.find_metadata_elements.side_effect = RuntimeError("boom")

    def _boom(mgr, as_of=None):
        raise RuntimeError("boom")

    import pyegeria.view.overview_metrics as om_module
    from pyegeria.view.analytic_registry import clear_runtime_analytic_functions, register_analytic_functions
    om_module._boom_for_test = _boom
    # metric_path is a registered name from 6.2.19 (ISSUE-173)
    register_analytic_functions({"boom-for-test": {
        "name": "boom-for-test", "function": "pyegeria.view.overview_metrics._boom_for_test"}})
    try:
        series = om.metric_trend(mgr, MagicMock(), "boom-for-test", window="7d", points=2)
        assert len(series) == 2
        assert all(p["value"] is None for p in series)
    finally:
        clear_runtime_analytic_functions()
        del om_module._boom_for_test


# ── count_elements_by_property ────────────────────────────────────────────

def test_count_elements_by_property_uses_native_when_available():
    mgr = _mgr(count_metadata_elements=MagicMock(return_value={"count": 2}))
    n = om.count_elements_by_property(mgr, "DigitalProduct", "deploymentStatus", "ACTIVE")
    assert n == 2
    mgr.count_metadata_elements.assert_called_once()
    body = mgr.count_metadata_elements.call_args[0][0]
    assert body["metadataElementTypeName"] == "DigitalProduct"
    assert body["limitResultsByStatus"] == ["ACTIVE"]
    condition = body["searchProperties"]["conditions"][0]
    assert condition["property"] == "deploymentStatus"
    assert condition["operator"] == "EQ"
    assert condition["value"]["primitiveValue"] == "ACTIVE"


def test_count_elements_by_property_falls_back_when_no_native_method():
    mgr = _mgr()
    mgr.find_metadata_elements.side_effect = _pages([{}, {}, {}])
    n = om.count_elements_by_property(mgr, "DigitalProduct", "deploymentStatus", "ACTIVE", population="viewer")
    assert n == 3


def test_count_elements_by_property_neq_and_bad_operator():
    mgr = _mgr(count_metadata_elements=MagicMock(return_value={"count": 536}))
    assert om.count_elements_by_property(mgr, "GlossaryTerm", "description", "", operator="NEQ") == 536
    cond = mgr.count_metadata_elements.call_args[0][0]["searchProperties"]["conditions"][0]
    assert cond["operator"] == "NEQ" and cond["value"]["primitiveValue"] == ""
    with pytest.raises(ValueError, match="operator"):
        om.count_elements_by_property(mgr, "GlossaryTerm", "description", "", operator="LIKE")


def test_count_elements_by_property_passes_as_of():
    mgr = _mgr(count_metadata_elements=MagicMock(return_value={"count": 1}))
    om.count_elements_by_property(mgr, "DigitalProduct", "deploymentStatus", "ACTIVE", as_of="2026-01-01T00:00:00+00:00")
    body = mgr.count_metadata_elements.call_args[0][0]
    assert body["asOfTime"] == "2026-01-01T00:00:00+00:00"


# ── contextualised_coverage ────────────────────────────────────────────────

def _implemented_by(end1_type, end2_type, end2_guid, super_types=None):
    return {
        "end1": {"guid": "sc-guid", "type": {"typeName": end1_type}},
        "end2": {"guid": end2_guid, "type": {"typeName": end2_type, "superTypeNames": super_types or []}},
    }


def test_contextualised_coverage_counts_only_asset_subtype_ends():
    mgr = _mgr(count_metadata_elements=MagicMock(return_value={"count": 384}))
    ce = MagicMock()
    ce.get_relationships.side_effect = _pages([
        _implemented_by("SolutionComponent", "GovernanceActionType", "gat-1"),
        _implemented_by("SolutionComponent", "IntegrationConnector", "asset-1", super_types=["Asset"]),
        _implemented_by("SolutionComponent", "SoftwareServer", "asset-2", super_types=["Asset"]),
    ])
    result = om.contextualised_coverage(mgr, ce)
    assert result["contextualisedCount"] == 2
    assert result["assetTotal"] == 384
    assert result["contextualisedPct"] == round(100.0 * 2 / 384, 1)


def test_contextualised_coverage_dedupes_by_guid():
    mgr = _mgr(count_metadata_elements=MagicMock(return_value={"count": 10}))
    ce = MagicMock()
    ce.get_relationships.side_effect = _pages([
        _implemented_by("SolutionComponent", "SoftwareServer", "asset-1", super_types=["Asset"]),
        _implemented_by("SolutionComponent", "SoftwareServer", "asset-1", super_types=["Asset"]),
    ])
    result = om.contextualised_coverage(mgr, ce)
    assert result["contextualisedCount"] == 1


def test_contextualised_coverage_matches_asset_typename_directly_too():
    # end2's own typeName (not just its superTypeNames) can be "Asset".
    mgr = _mgr(count_metadata_elements=MagicMock(return_value={"count": 5}))
    ce = MagicMock()
    ce.get_relationships.side_effect = _pages([
        _implemented_by("SolutionComponent", "Asset", "asset-1"),
    ])
    result = om.contextualised_coverage(mgr, ce)
    assert result["contextualisedCount"] == 1


def test_contextualised_coverage_relationship_fetch_failure_yields_none_count():
    mgr = _mgr(count_metadata_elements=MagicMock(return_value={"count": 384}))
    ce = MagicMock()
    ce.get_relationships.side_effect = RuntimeError("boom")
    result = om.contextualised_coverage(mgr, ce)
    assert result["contextualisedCount"] is None
    assert result["assetTotal"] == 384
    assert result["contextualisedPct"] is None


def test_contextualised_coverage_zero_asset_total_yields_none_pct_not_zero_division():
    mgr = _mgr(count_metadata_elements=MagicMock(return_value={"count": 0}))
    ce = MagicMock()
    ce.get_relationships.side_effect = _pages([])
    result = om.contextualised_coverage(mgr, ce)
    assert result["contextualisedCount"] == 0
    assert result["assetTotal"] is None
    assert result["contextualisedPct"] is None


# ── unmeasured != zero (overview defects: egeria-workspaces#783) ─────────

def test_funnel_keeps_measured_zero_and_none_on_failure():
    mgr = _mgr(count_metadata_elements=MagicMock(return_value=0),
               count_relationships_between_elements=MagicMock(return_value=0))
    ce = MagicMock()
    r = om.context_readiness_funnel(mgr, ce)
    assert r["cataloged"] == 0 and r["classified"] == 0 and r["documented"] == 0 and r["lineage"] == 0

    mgr.count_metadata_elements.side_effect = RuntimeError("down")
    mgr.count_relationships_between_elements.side_effect = RuntimeError("down")
    mgr.find_metadata_elements.side_effect = _pages([])   # a viewer answer must never stand in
    r = om.context_readiness_funnel(mgr, ce)
    assert r["cataloged"] is None and r["classified"] is None
    assert r["documented"] is None and r["lineage"] is None


def test_feedback_summary_total_none_unless_all_measured():
    ce = MagicMock()
    ce.get_relationships.side_effect = _by_type({"AttachedRating": [{}] * 3, "AttachedComment": RuntimeError("x")})
    r = om.feedback_summary(ce, population="viewer")
    assert r["byType"]["comments"] is None and r["byType"]["ratings"] == 3
    assert r["total"] is None


def test_governed_coverage_and_business_value_none_on_failed_find():
    mgr = _mgr()
    mgr.find_metadata_elements.side_effect = RuntimeError("down")
    g = om.governed_coverage(mgr)
    assert g["governedCount"] is None and g["fullyGoverned"] is None and g["partialZoneOnly"] is None
    b = om.business_value_signals(mgr)
    assert b["assetTotal"] is None and b["confidentialCount"] is None
    assert b["describedCount"] is None and b["duplicateCount"] is None


# ── sticky native-count switch ───────────────────────────────────────────

def test_timeout_does_not_disable_native_counting():
    from pyegeria.core._exceptions import PyegeriaTimeoutException
    mgr = _mgr(count_metadata_elements=MagicMock(side_effect=[PyegeriaTimeoutException(), 987]))
    mgr.find_metadata_elements.side_effect = _pages([{}] * 3)
    assert om.count_elements(mgr, "Asset", population="viewer") == 3   # that one count falls back
    assert not om._native_disabled(mgr)
    assert om.count_elements(mgr, "GlossaryTerm", strict=True) == 987  # native still used


def test_transient_generic_error_does_not_disable_native():
    mgr = _mgr(count_metadata_elements=MagicMock(side_effect=[RuntimeError("boom"), 5]))
    mgr.find_metadata_elements.side_effect = _pages([])
    om.count_elements(mgr, "Asset")
    assert not om._native_disabled(mgr)
    assert om.count_elements(mgr, "Asset") == 5


def test_not_supported_error_disables_native():
    from pyegeria.core._exceptions import PyegeriaNotFoundException
    resp = MagicMock(status_code=404, url="https://x/count", text="")
    resp.json.return_value = {}
    for exc in (PyegeriaNotFoundException(resp), RuntimeError("Operation not implemented")):
        om._native_server_ok.clear(); om._count_caps.clear()
        mgr = _mgr(count_metadata_elements=MagicMock(side_effect=exc))
        mgr.find_metadata_elements.side_effect = _pages([{}] * 2)
        assert om.count_elements(mgr, "Asset", population="viewer") == 2
        assert om._native_disabled(mgr)
        om.count_elements(mgr, "Asset", population="viewer")
        assert mgr.count_metadata_elements.call_count == 1   # not retried


def test_native_disable_expires(monkeypatch):
    mgr = _mgr(count_metadata_elements=MagicMock(return_value=9))
    om._native_server_ok[om._server_key(mgr)] = om.time.monotonic() - om.NATIVE_DISABLE_TTL_S - 1
    assert not om._native_disabled(mgr)
    assert om.count_elements(mgr, "Asset") == 9


# ── count scope -> native push_down ──────────────────────────────────────

@pytest.mark.parametrize("scope,expected", [("viewer", False), ("repository", True)])
def test_scope_maps_to_push_down(scope, expected):
    mgr = _mgr(count_metadata_elements=MagicMock(return_value=11))
    assert om.count_elements(mgr, "Asset", population=scope) == 11
    assert mgr.count_metadata_elements.call_args.kwargs == {"push_down": expected}


def test_default_population_is_repository_push_down():
    mgr = _mgr(count_metadata_elements=MagicMock(return_value=11))
    om.count_elements(mgr, "Asset")
    assert mgr.count_metadata_elements.call_args.kwargs == {"push_down": True}


def test_scope_none_omits_push_down():
    mgr = _mgr(count_metadata_elements=MagicMock(return_value=11))
    om.count_elements(mgr, "Asset", scope=None)   # the server default stays reachable
    assert mgr.count_metadata_elements.call_args.kwargs == {}


def test_invalid_scope_raises():
    with pytest.raises(ValueError):
        om.count_elements(_mgr(), "Asset", population="everyone")


def test_repository_scope_failure_strict_is_none_not_find_result():
    mgr = _mgr(count_metadata_elements=MagicMock(side_effect=RuntimeError("boom")))
    mgr.find_metadata_elements.side_effect = _pages([{}] * 43)     # viewer-scope answer
    with om.recording_unmeasured() as notes:
        assert om.count_elements(mgr, "Asset", strict=True, population="repository") is None
        assert om.count_elements(mgr, "Asset", population="repository") is None   # never 0, strict or not
    mgr.find_metadata_elements.assert_not_called()
    assert len(notes) == 2 and all("has no fallback" in n["reason"] for n in notes)


def test_repository_scope_without_native_method_is_none():
    mgr = _mgr()
    mgr.find_metadata_elements.side_effect = _pages([{}] * 3)
    assert om.count_elements(mgr, "Asset", strict=True, population="repository") is None
    assert om.count_elements(mgr, "Asset", strict=True, population="viewer") == 3   # viewer may fall back


def test_scope_threads_through_helpers():
    mgr = _mgr(count_metadata_elements=MagicMock(return_value=2))
    om.counts_by_type(mgr, [("A", "Asset")], population="repository")
    om.people_counts(mgr, population="repository")
    om.usage_context_counts(mgr, population="repository")
    om.count_elements_by_property(mgr, "DigitalProduct", "deploymentStatus", "ACTIVE", population="repository")
    calls = mgr.count_metadata_elements.call_args_list
    assert len(calls) == 1 + 5 + 2 + 1
    assert all(c.kwargs == {"push_down": True} for c in calls)


def test_count_relationships_scope():
    expert = MagicMock(spec=["count_relationships_between_elements", "platform_url", "view_server"])
    expert.platform_url, expert.view_server = "u", "v"
    expert.count_relationships_between_elements.return_value = 4
    ce = MagicMock()
    ce.get_relationships.side_effect = _pages([{}] * 9)
    assert om.count_relationships(ce, "License", expert=expert, population="repository") == 4
    assert expert.count_relationships_between_elements.call_args.kwargs == {"push_down": True}
    # no expert, and ce has no native count: repository scope cannot be answered by the viewer-scoped path
    ce = MagicMock(spec=["get_relationships"])
    ce.get_relationships.side_effect = _pages([{}] * 9)
    with om.recording_unmeasured() as notes:
        assert om.count_relationships(ce, "License", population="repository") is None
        assert om.count_relationships(ce, "License") is None   # repository is the default
    assert notes[0] == {"count": "License", "at_least": None, "reason": (
        "no native relationship count is available (it needs a MetadataExpert client), and a "
        "repository-population count has no fallback (get_relationships only sees what the viewer may see)")}
    assert om.count_relationships(ce, "License", population="viewer") == 9
    assert om.feedback_summary(ce)["total"] is None
    assert om.feedback_summary(ce, population="viewer")["total"] == 45


# ── asset_subtype_tree / asset_composition (RS-W1-4) ─────────────────────────

import threading
import time as _time

_TREE = {  # three levels under Asset
    "Asset": ["DataAsset", "Process"],
    "DataAsset": ["DataSet", "DataStore"],
    "Process": [],  # null result: no subtypes
    "DataSet": ["Report"],
}


class _FakeVM:
    def __init__(self, tree=_TREE, fail=()):
        self.tree, self.fail, self.calls = tree, set(fail), []

    def get_sub_types(self, type_name, **_):
        self.calls.append(type_name)
        if type_name in self.fail:
            raise RuntimeError("typedef service down")
        kids = self.tree.get(type_name)
        if not kids:
            return "No elements found"  # pyegeria's NO_ELEMENTS_FOUND sentinel
        return [{"name": k, "superType": {"name": type_name}} for k in kids]


_COUNTS = {
    "repository": {"Asset": 100, "DataAsset": 60, "DataSet": 40, "DataStore": 15, "Process": 30, "Report": 5},
    "viewer": {"Asset": 90, "DataAsset": 55, "DataSet": 36, "DataStore": 15, "Process": 30, "Report": 5},
}


class _FakeCounter:
    """Stands in for count_elements: records concurrency, fails on chosen (type, scope) pairs."""

    def __init__(self, counts=_COUNTS, fail=(), raise_on=(), delay=0.02):
        self.counts, self.fail, self.raise_on, self.delay = counts, set(fail), set(raise_on), delay
        self.lock = threading.Lock()
        self.active = self.peak = 0
        self.calls = []

    def __call__(self, mgr, type_name=None, as_of=None, classifications=None, strict=False, scope=None,
                 population=None):
        assert strict is True
        scope = population or scope
        with self.lock:
            self.active += 1
            self.peak = max(self.peak, self.active)
            self.calls.append((type_name, scope, as_of))
        try:
            _time.sleep(self.delay)
            if (type_name, scope) in self.raise_on:
                raise RuntimeError("HikariPool timeout")
            if (type_name, scope) in self.fail:
                return None
            return self.counts[scope].get(type_name, 0)
        finally:
            with self.lock:
                self.active -= 1


def _rows(result):
    return {(r["type_name"], r["exact_type"]): r for r in result["rows"]}


def test_asset_subtype_tree_breadth_first_with_other_rows():
    rows = om.asset_subtype_tree(_FakeVM(), root="Asset", depth=2)
    got = [(r["type_name"], r["parent"], r["level"], r["exact_type"]) for r in rows]
    assert got == [
        ("Asset", None, 0, False),
        ("DataAsset", "Asset", 1, False), ("Process", "Asset", 1, False), ("Asset", "Asset", 1, True),
        ("DataSet", "DataAsset", 2, False), ("DataStore", "DataAsset", 2, False),
        ("DataAsset", "DataAsset", 2, True),
    ]  # Process has no subtypes: no `other` row; DataSet's Report is below depth 2


def test_asset_subtype_tree_depth_three_and_skips_non_direct():
    tree = dict(_TREE)
    vm = _FakeVM(tree)
    real = vm.get_sub_types
    vm.get_sub_types = lambda t, **k: (real(t) if t != "Asset" else
                                       real(t) + [{"name": "DataSet", "superType": {"name": "DataAsset"}}])
    rows = om.asset_subtype_tree(vm, depth=3)
    names = [(r["type_name"], r["level"]) for r in rows if not r["exact_type"]]
    assert ("Report", 3) in names
    assert names.count(("DataSet", 1)) == 0  # a grandchild returned for Asset is not a direct child


def test_asset_subtype_tree_records_a_failed_subtype_call():
    rows = om.asset_subtype_tree(_FakeVM(fail={"DataAsset"}), depth=2)
    da = next(r for r in rows if r["type_name"] == "DataAsset" and not r["exact_type"])
    assert "could not be read" in da["subtypes_error"]
    assert not any(r["parent"] == "DataAsset" for r in rows)  # no children, no `other` row


def test_asset_composition_cells_other_rows_and_not_visible(monkeypatch):
    counter = _FakeCounter()
    monkeypatch.setattr(om, "count_elements", counter)
    res = om.asset_composition(MagicMock(platform_url="u", view_server="s"), _FakeVM(), depth=2)
    rows = _rows(res)
    assert res["state"] == "measured" and res["state_reason"] == "" and res["not_measured"] == []
    asset = rows[("Asset", False)]
    assert asset["repository"] == {"value": 100, "state": "measured", "completeness": "complete",
                                   "as_of": res["as_of"], "population": "repository", "reason": "",
                                   "elapsed_s": asset["repository"]["elapsed_s"]}
    assert asset["viewer"]["completeness"] == "unknown" and asset["viewer"]["population"] == "viewer"
    assert asset["not_visible"] == {"value": 10, "state": "measured", "reason": ""}
    # other rows: parent - sum(children), per scope
    assert rows[("Asset", True)]["repository"]["value"] == 100 - 60 - 30
    assert rows[("Asset", True)]["viewer"]["value"] == 90 - 55 - 30
    assert rows[("DataAsset", True)]["repository"]["value"] == 60 - 40 - 15
    assert rows[("DataAsset", True)]["repository"]["elapsed_s"] is None  # derived
    # an `other` row reuses its parent's count: each distinct type counted once per scope
    assert sorted((t, s) for t, s, _ in counter.calls) == sorted(
        (t, s) for s in ("viewer", "repository") for t in ("Asset", "DataAsset", "Process", "DataSet", "DataStore"))
    assert res["provenance"]["server"] == "s" and res["provenance"]["pyegeria_version"]


def test_asset_composition_zero_is_nothing_found(monkeypatch):
    counts = {s: dict(c) for s, c in _COUNTS.items()}
    counts["repository"]["Process"] = 0
    counts["viewer"]["Process"] = 0
    monkeypatch.setattr(om, "count_elements", _FakeCounter(counts))
    rows = _rows(om.asset_composition(MagicMock(), _FakeVM(), depth=1))
    proc = rows[("Process", False)]
    assert proc["repository"]["state"] == "nothing_found" and proc["repository"]["value"] == 0
    assert proc["repository"]["completeness"] == "complete"
    assert proc["not_visible"] == {"value": 0, "state": "nothing_found", "reason": ""}


def test_asset_composition_failure_is_not_measured_never_zero(monkeypatch):
    counter = _FakeCounter(fail={("DataStore", "viewer")}, raise_on={("Process", "repository")})
    monkeypatch.setattr(om, "count_elements", counter)
    res = om.asset_composition(MagicMock(), _FakeVM(), depth=2)
    rows = _rows(res)
    ds_viewer = rows[("DataStore", False)]["viewer"]
    assert ds_viewer["value"] is None and ds_viewer["state"] == "not_measured"
    assert ds_viewer["completeness"] == "unknown" and "could not be measured" in ds_viewer["reason"]
    proc_repo = rows[("Process", False)]["repository"]
    assert proc_repo["value"] is None and "HikariPool timeout" in proc_repo["reason"]
    # the failed scope's `other` row is not_measured; the other scope still derives
    assert rows[("DataAsset", True)]["viewer"] == {**rows[("DataAsset", True)]["viewer"],
                                                   "value": None, "state": "not_measured",
                                                   "reason": "a child count is missing"}
    assert rows[("DataAsset", True)]["repository"]["value"] == 5
    assert rows[("Asset", True)]["repository"]["reason"] == "a child count is missing"
    assert rows[("Asset", True)]["viewer"]["value"] == 5
    # not_visible needs both scopes established
    assert rows[("DataStore", False)]["not_visible"]["state"] == "not_measured"
    assert rows[("Process", False)]["not_visible"]["value"] is None
    assert rows[("DataSet", False)]["not_visible"]["value"] == 4
    # envelope: still measured (other cells are), and the reason lists the failed cells
    assert res["state"] == "measured"
    assert set(res["not_measured"]) == {"DataStore/viewer", "Process/repository"}
    assert "DataStore/viewer" in res["state_reason"] and "Process/repository" in res["state_reason"]


def test_asset_composition_all_failed_is_not_established(monkeypatch):
    monkeypatch.setattr(om, "count_elements", lambda *a, **k: None)
    res = om.asset_composition(MagicMock(), _FakeVM(), depth=1, populations=("repository",))
    assert res["state"] == "not_established"
    assert all(r["repository"]["value"] is None for r in res["rows"])


def test_asset_composition_single_scope_not_visible_needs_both(monkeypatch):
    monkeypatch.setattr(om, "count_elements", _FakeCounter())
    res = om.asset_composition(MagicMock(), _FakeVM(), depth=1, populations=("repository",))
    asset = _rows(res)[("Asset", False)]
    assert "viewer" not in asset and res["populations"] == ["repository"]
    assert asset["not_visible"] == {"value": None, "state": "not_measured", "reason": "needs both scopes"}


@pytest.mark.parametrize("asked, cap", [(1, 1), (2, 2), (3, 3), (5, 5), (12, 5)])
def test_asset_composition_one_pool_for_both_scopes_respects_cap(monkeypatch, asked, cap):
    counter = _FakeCounter(delay=0.05)
    monkeypatch.setattr(om, "count_elements", counter)
    res = om.asset_composition(MagicMock(), _FakeVM(), depth=2, concurrency=asked)
    assert res["concurrency"] == cap
    assert len(counter.calls) == 10  # 5 types x 2 scopes, all through the one pool
    assert counter.peak <= cap
    if cap > 1:
        assert counter.peak > 1  # really concurrent, and across both scopes together


def test_asset_composition_default_concurrency_is_three(monkeypatch):
    counter = _FakeCounter(delay=0.05)
    monkeypatch.setattr(om, "count_elements", counter)
    res = om.asset_composition(MagicMock(), _FakeVM(), depth=2)
    assert res["concurrency"] == 3 and counter.peak == 3


def test_asset_composition_passes_as_of_and_vm_defaults_to_mgr(monkeypatch):
    counter = _FakeCounter()
    monkeypatch.setattr(om, "count_elements", counter)
    both = _FakeVM()
    res = om.asset_composition(both, depth=1, as_of="2026-01-01T00:00:00+00:00")
    assert both.calls == ["Asset"]
    assert {a for _, _, a in counter.calls} == {"2026-01-01T00:00:00+00:00"}
    assert res["as_of"] == "2026-01-01T00:00:00+00:00"
    assert all(r[s]["as_of"] == res["as_of"] for r in res["rows"] for s in res["populations"])


@pytest.mark.parametrize("kwargs", [{"populations": ()}, {"populations": ("everyone",)}, {"concurrency": 0},
                                    {"strict": False}])
def test_asset_composition_rejects_bad_arguments(kwargs):
    with pytest.raises(ValueError):
        om.asset_composition(MagicMock(), _FakeVM(), **kwargs)


def test_asset_composition_uses_the_real_count_seam_per_scope():
    """Through the real count_elements: push_down follows the scope."""
    mgr = _mgr(count_metadata_elements=MagicMock(return_value={"count": 4}))
    res = om.asset_composition(mgr, _FakeVM({"Asset": []}), depth=1)
    push = sorted(c.kwargs["push_down"] for c in mgr.count_metadata_elements.call_args_list)
    assert push == [False, True]
    assert res["rows"][0]["repository"]["value"] == 4


def test_asset_composition_is_registered_with_a_declaration():
    from pyegeria.view.analytic_registry import get_analytic_registry
    spec = get_analytic_registry()["asset_composition"]
    assert spec.function == "pyegeria.view.overview_metrics.asset_composition" and spec.envelope
    decl = spec.declaration
    assert decl.result_kind == "distribution"
    assert {m.name for m in decl.measures} == {"repository_count", "viewer_count", "not_visible"}
    assert all(m.unit == "elements" and m.as_of == "as_of" for m in decl.measures)
    assert decl.absence.nothing_found


# ── population= is the keyword; scope= / scopes= are deprecated aliases (RS-W1-1 §5) ──

def test_count_elements_scope_alias_warns_and_matches_population():
    mgr = _mgr()
    mgr.count_metadata_elements = MagicMock(return_value=7)
    with pytest.warns(DeprecationWarning, match="population="):
        old = om.count_elements(mgr, "Asset", scope="repository")
    new = om.count_elements(mgr, "Asset", population="repository")
    assert old == new == 7


def test_count_elements_population_and_scope_must_agree():
    with pytest.raises(ValueError, match="disagree"):
        om.count_elements(_mgr(), "Asset", population="viewer", scope="repository")


def test_population_keyword_is_in_every_count_helper_signature():
    import inspect
    for fn in (om.count_elements, om.count_elements_by_property, om.count_relationships, om.counts_by_type,
               om.business_value_signals, om.people_counts, om.feedback_summary, om.usage_context_counts):
        assert "population" in inspect.signature(fn).parameters, fn.__name__


def test_asset_composition_scopes_alias_warns_and_matches_populations():
    with pytest.warns(DeprecationWarning, match="populations="):
        old = om.asset_composition(MagicMock(), _FakeVM(), depth=1, scopes=("repository",))
    assert old["populations"] == old["scopes"] == ["repository"]
    with pytest.raises(ValueError, match="disagree"):
        om.asset_composition(MagicMock(), _FakeVM(), depth=1, scopes=("viewer",), populations=("repository",))


def test_scope_none_reaches_the_server_default_through_every_composite():
    # population=None means "not given" to the keyword wrapper, so a composite must forward the
    # server default as scope=None explicitly, or its counts silently become repository counts.
    mgr = _mgr(count_metadata_elements=MagicMock(return_value=2))
    om.counts_by_type(mgr, [("A", "Asset")], scope=None)
    om.people_counts(mgr, scope=None)
    om.usage_context_counts(mgr, scope=None)
    om.business_value_signals(mgr, scope=None)
    om.growth_series(mgr, window="7d", points=2, population=None)
    calls = mgr.count_metadata_elements.call_args_list
    assert len(calls) == 1 + 5 + 2 + 4 + 2 * 4 and all(c.kwargs == {} for c in calls)
    ce = MagicMock()
    ce.get_relationships.side_effect = _pages([{}] * 2)
    assert om.feedback_summary(ce, scope=None)["total"] == 10   # the get_relationships path, not None
