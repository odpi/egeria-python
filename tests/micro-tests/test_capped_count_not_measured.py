# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
A count that timed out is never reported as a measured total.

Live (2026-11-08, platform build 082ecd44): the native count of a supertype (Asset, Process)
timed out at the client's 30 s limit, `_element_count` fell back to len(find), the find stopped
at DEFAULT_CAP, and the Portal tile showed "Total Cataloged Assets = 500". A full page is a lower
bound, never a total: the count is None ("not measured"), and the reason with the bound it saw
reaches the output. Every branch is executed here, not read.

Since 2026-11-08 the count helpers default to the repository population (push_down=True), which
has no find fallback at all: a failed repository count is None with its reason, never 0 and never a
viewer number. The fallback and its lower bound now only arise in the viewer population, so the
seam tests below ask for it explicitly.
"""
import json
from unittest.mock import MagicMock

import pytest

from pyegeria.view import format_set_executor as fse
from pyegeria.view import overview_metrics as om
from pyegeria.view.role_supply import Subject, Viewer

CAP = om.DEFAULT_CAP
REPO_TIMEOUT = ("the native count timed out, and a repository-population count has no fallback "
                "(the find fallback only sees what the viewer may see)")
TIMEOUT = RuntimeError("TIMEOUT_ERROR_408 the request to .../by-search-conditions/count timed out")


@pytest.fixture(autouse=True)
def _reset_seam_caches():
    om._count_caps.clear()
    om._native_server_ok.clear()
    yield
    om._count_caps.clear()
    om._native_server_ok.clear()


def _mgr(native=None, find_result=None, find_error=None):
    attrs = ["platform_url", "view_server", "find_metadata_elements"]
    if native is not None:
        attrs.append("count_metadata_elements")
    m = MagicMock(spec=attrs)
    m.platform_url, m.view_server = "https://localhost:9443", "test-server"
    if native is not None:
        m.count_metadata_elements = native
    if find_error is not None:
        m.find_metadata_elements.side_effect = find_error
    else:
        m.find_metadata_elements.return_value = find_result
    return m


def _page(n):
    return [{"elementGUID": f"g{i}"} for i in range(n)]


# ── the count seam ──

def test_a_timeout_whose_fallback_hits_the_cap_is_not_measured_with_its_lower_bound():
    mgr = _mgr(native=MagicMock(side_effect=TIMEOUT), find_result=_page(CAP))
    with om.recording_unmeasured() as notes:
        for strict in (True, False):
            assert om.count_elements(mgr, "Asset", strict=strict, population="viewer") is None  # never CAP
    assert notes == [{"count": "Asset", "at_least": CAP,
                      "reason": f"the native count timed out, and the find fallback stopped at its "
                                f"{CAP}-element page cap, so there are at least {CAP}"}] * 2


def test_a_timeout_whose_fallback_fails_is_not_measured_strict():
    mgr = _mgr(native=MagicMock(side_effect=TIMEOUT), find_error=RuntimeError("boom"))
    with om.recording_unmeasured() as notes:
        assert om.count_elements(mgr, "Process", strict=True, population="viewer") is None
    assert notes == [{"count": "Process", "at_least": None,
                      "reason": "the native count timed out, and the find fallback failed"}]


def test_a_timed_out_repository_count_is_not_measured_and_never_asks_the_find():
    mgr = _mgr(native=MagicMock(side_effect=TIMEOUT), find_result=_page(3))
    with om.recording_unmeasured() as notes:
        for strict in (True, False):
            assert om.count_elements(mgr, "Asset", strict=strict) is None  # never 0, never a viewer 3
    mgr.find_metadata_elements.assert_not_called()
    assert notes == [{"count": "Asset", "at_least": None, "reason": REPO_TIMEOUT}] * 2


def test_the_timeout_leaves_native_enabled_for_the_next_count():
    native = MagicMock(side_effect=[TIMEOUT, {"count": 7}])
    mgr = _mgr(native=native, find_result=_page(CAP))
    assert om.count_elements(mgr, "Asset", strict=True) is None
    assert om.count_elements(mgr, "DataStore", strict=True) == 7


def test_a_short_fallback_page_is_a_measured_count_and_records_nothing():
    mgr = _mgr(native=MagicMock(side_effect=TIMEOUT), find_result=_page(CAP - 1))
    with om.recording_unmeasured() as notes:
        assert om.count_elements(mgr, "Asset", population="viewer") == CAP - 1
        assert om.count_elements(mgr, "Asset", strict=True, population="viewer") == CAP - 1
    assert notes == []


def test_a_native_count_above_the_cap_is_trusted():
    with om.recording_unmeasured() as notes:
        assert om.count_elements(_mgr(native=MagicMock(return_value={"count": 1061})), "GlossaryTerm") == 1061
    assert notes == []


def test_a_failed_viewer_count_is_none_with_a_note_strict_or_not():
    # 6.2.28: the non-strict viewer 0 is gone -- a failed query is not "no Assets".
    for strict in (False, True):
        with om.recording_unmeasured() as notes:
            assert om.count_elements(_mgr(find_error=RuntimeError("boom")), "Asset", population="viewer",
                                     strict=strict) is None
        assert notes == [{"count": "Asset", "reason": "no native count is available, and the find fallback failed",
                          "at_least": None}]


def test_a_classification_count_names_what_it_counted():
    mgr = _mgr(find_result=_page(CAP))
    with om.recording_unmeasured() as notes:
        assert om.count_elements(mgr, None, classifications=["Confidentiality", "Impact"]) is None
    assert notes[0]["count"] == "elements classified Confidentiality/Impact"
    assert notes[0]["reason"].startswith("no native count is available")


def test_notes_are_only_kept_inside_a_recording_block():
    mgr = _mgr(find_result=_page(CAP))
    assert om.count_elements(mgr, "Asset") is None  # no block: nothing to append to, no error
    with om.recording_unmeasured() as outer:
        with om.recording_unmeasured() as inner:
            om.count_elements(mgr, "Asset")
        om.count_elements(mgr, "Process")
    assert [n["count"] for n in inner] == ["Asset"]
    assert [n["count"] for n in outer] == ["Process"]


def _rel_pages(rows):
    """get_relationships paging like Egeria: rows from the body's startFrom, then an empty page."""
    def fake(*a, body=None, **kw):
        start, size = body["startFrom"], body["pageSize"]
        return rows[start:start + size]
    return fake


def test_a_viewer_relationship_count_reads_every_page():
    # A full page is not the last page: the viewer count pages on until Egeria returns an empty page.
    ce = MagicMock()
    ce.get_relationships.side_effect = _rel_pages([{"relationshipHeader": {"guid": f"r{i}"}}
                                                   for i in range(CAP + 247)])
    with om.recording_unmeasured() as notes:
        assert om.count_relationships(ce, "SemanticAssignment", population="viewer") == CAP + 247
    assert notes == []
    assert [c.kwargs["body"]["startFrom"] for c in ce.get_relationships.call_args_list] == [0, CAP, 2 * CAP]


def test_a_relationship_scan_that_cannot_finish_is_not_a_count():
    # A server that ignores startFrom repeats the page: the count is not measured, never the page.
    ce = MagicMock()
    ce.get_relationships.return_value = [{"relationshipHeader": {"guid": f"r{i}"}} for i in range(CAP)]
    with om.recording_unmeasured() as notes:
        assert om.count_relationships(ce, "SemanticAssignment", population="viewer") is None
    assert notes[0]["count"] == "SemanticAssignment relationships" and notes[0]["at_least"] == CAP
    ce.get_relationships.reset_mock(return_value=True)
    ce.get_relationships.side_effect = _rel_pages([{"relationshipHeader": {"guid": "r1"}}])
    assert om.count_relationships(ce, "SemanticAssignment", population="viewer") == 1


def test_a_relationship_scan_stops_at_max_scan_pages_and_is_not_measured(monkeypatch):
    monkeypatch.setattr(om, "MAX_SCAN_PAGES", 3)
    ce = MagicMock()
    ce.get_relationships.side_effect = _rel_pages([{"relationshipHeader": {"guid": f"r{i}"}}
                                                   for i in range(3 * CAP + 1)])
    with om.recording_unmeasured() as notes:
        assert om.count_relationships(ce, "SemanticAssignment", population="viewer") is None
    assert "stopped after 3 pages" in notes[0]["reason"] and notes[0]["at_least"] == 3 * CAP


def test_semantic_grounding_no_longer_reports_500_links_100_percent():
    mgr = _mgr(native=MagicMock(side_effect=TIMEOUT), find_result=_page(CAP))
    ce = MagicMock()
    ce.get_relationships.return_value = [{"guid": f"r{i}"} for i in range(CAP)]
    with om.recording_unmeasured() as notes:
        assert om.semantic_grounding(mgr, ce) == {"groundedAssets": None, "groundedAssetTotal": None, "groundedAssetPct": None, "groundingLinks": None, "groundingPct": None}
    # the native link count and Asset counts, and the distinct-Asset scan (which saw one page again)
    assert {n["count"] for n in notes} == {"Asset", "SemanticAssignment", "SemanticAssignment relationships"}


def test_counts_by_type_and_its_sum_never_add_a_lower_bound_into_a_total():
    native = MagicMock(side_effect=lambda body, **kw: (
        {"count": 843} if body["metadataElementTypeName"] == "DataStore" else (_ for _ in ()).throw(TIMEOUT)))
    mgr = _mgr(native=native, find_result=_page(CAP))
    rows = om.counts_by_type(mgr, [("Data Stores", "DataStore"), ("Processes", "Process")])
    assert rows == [{"label": "Data Stores", "type": "DataStore", "count": 843},
                    {"label": "Processes", "type": "Process", "count": None}]
    assert om.sum_counts(rows)["total"] is None
    assert om.sum_counts(rows[:1])["total"] == 843


def test_an_asset_composition_cell_carries_the_lower_bound_in_its_reason():
    mgr = _mgr(native=MagicMock(side_effect=TIMEOUT), find_result=_page(CAP))
    cell = om._count_cell(mgr, "Asset", None, "viewer", "now")
    assert cell["value"] is None and cell["state"] == om.CELL_NOT_MEASURED
    assert f"so there are at least {CAP}" in cell["reason"]


# ── what a reader sees through exec_report_spec ──

class _Fake:
    """Native element counts time out except DataStore; the find fallback returns a full page."""
    platform_url, view_server = "https://fake:9443", "fake"

    def count_metadata_elements(self, body, **kw):
        if body.get("metadataElementTypeName") == "DataStore":
            return {"count": 843}
        raise TIMEOUT

    def find_metadata_elements(self, body, *a, **kw):
        return _page(min(CAP, body.get("pageSize") or CAP))

    def get_relationships(self, *a, page_size=None, **kw):
        return [{"guid": f"r{i}"} for i in range(min(CAP, page_size or CAP))]


class _Supply:
    def __init__(self):
        self.fake = _Fake()

    def client(self, cls):
        return self.fake

    def viewer(self):
        return Viewer(user_id="u", is_admin=False, display_name="U")

    def reader(self, source):
        return None

    def subject(self):
        return Subject(guid="g", type_name="Asset")

    def refusal_words(self, kind):
        return f"cannot supply {kind}"


def _exec(label, fmt="DICT", **params):
    return fse.exec_report_spec(label, output_format=fmt, params=params, view_server="vs", view_url="https://x",
                                user="u", user_pass="p", supply=_Supply())


def test_the_total_cataloged_assets_tile_says_not_measured_and_why():
    out = _exec("Analytic Demo - Element Count by Type", type_name="Asset")
    assert out["kind"] == "absent" and "data" not in out
    assert out["absence"]["state"] == "not_measured"
    assert out["unmeasured"] == [{"count": "Asset", "at_least": None, "reason": REPO_TIMEOUT}]
    assert "Asset: the native count timed out" in out["content"]


def test_a_non_strict_dashboard_count_is_never_a_confident_zero():
    out = _exec("Analytic Demo - Element Count by Type", type_name="Asset", strict=False)
    assert out["kind"] == "absent" and "data" not in out
    assert out["unmeasured"][0]["reason"] == REPO_TIMEOUT


def test_a_viewer_tile_still_says_at_least_500():
    out = _exec("Analytic Demo - Element Count by Type", type_name="Asset", population="viewer")
    assert out["kind"] == "absent"
    assert out["unmeasured"] == [{"count": "Asset", "at_least": CAP, "reason": (
        f"the native count timed out, and the find fallback stopped at its {CAP}-element page cap, "
        f"so there are at least {CAP}")}]
    assert f"at least {CAP}" in out["content"]


def test_a_measured_tile_is_unchanged():
    out = _exec("Analytic Demo - Element Count by Type", type_name="DataStore")
    # RS-EGERIA-TIER: provenance beside kind, not in data. Stage 2 (S2-2): the analytic demos ship in the seed.
    assert out.pop("spec_source")["tier"] == "builtin"
    assert out == {"kind": "json", "data": 843}


def test_the_breakdown_rows_keep_measured_counts_and_name_the_unmeasured_one():
    out = _exec("Analytic Demo - Assets by Type Breakdown",
                type_map=[["Data Stores", "DataStore"], ["Processes", "Process"]])
    assert out["kind"] == "json"
    assert out["data"] == [{"label": "Data Stores", "type": "DataStore", "count": 843},
                           {"label": "Processes", "type": "Process", "count": None}]
    assert [(n["count"], n["at_least"]) for n in out["unmeasured"]] == [("Process", None)]
    assert CAP not in [r["count"] for r in out["data"]]


@pytest.mark.parametrize("fmt", ["BAR", "PIE"])
def test_no_chart_is_drawn_over_an_unmeasured_count(fmt):
    out = _exec("Analytic Demo - Assets by Type Breakdown", fmt,
                type_map=[["Data Stores", "DataStore"], ["Processes", "Process"]])
    assert out["kind"] == "absent" and "data" not in out  # no vega spec: a missing bar would read as 0
    assert out["detail"][1] == {"label": "Processes", "type": "Process", "count": None}
    assert "Process: the native count timed out" in out["content"]


def test_semantic_grounding_spec_reports_nulls_and_why():
    out = _exec("Analytic Demo - Semantic Grounding")
    assert out["data"] == {"groundedAssets": None, "groundedAssetTotal": None, "groundedAssetPct": None, "groundingLinks": None, "groundingPct": None}
    assert {n["count"] for n in out["unmeasured"]} == {"Asset", "SemanticAssignment",
                                                        "SemanticAssignment relationships"}
    rel = next(n for n in out["unmeasured"] if n["count"] == "SemanticAssignment")
    assert rel["reason"].startswith("no native relationship count is available")


def test_a_series_repeats_no_note():
    out = _exec("Analytic Demo - Catalog Growth Trend", "SERIES")
    assert out["kind"] == "absent"
    keys = [json.dumps(n, sort_keys=True) for n in out["unmeasured"]]
    assert len(keys) == len(set(keys))


def test_no_rendered_output_carries_the_cap_as_a_count():
    for label, fmt, params in [
        ("Analytic Demo - Element Count by Type", "DICT", {"type_name": "Asset"}),
        ("Analytic Demo - Assets by Type Breakdown", "DICT", {"type_map": [["P", "Process"]]}),
        ("Analytic Demo - Assets by Type Breakdown", "BAR", {"type_map": [["P", "Process"]]}),
        ("Analytic Demo - People and Community", "PIE", {}),
    ]:
        out = _exec(label, fmt, **params)
        shown = {k: v for k, v in out.items() if k not in ("unmeasured", "absence", "envelope", "content", "detail")}
        assert str(CAP) not in json.dumps(shown), (label, fmt, out)
