# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
A figure computed from a scan is only a figure when the scan read everything (6.2.28).

Found live 2026-11-08 (READBACK-6.2.27): `orphan_glossary_terms` read one 500-relationship
SemanticAssignment page, which held 8 distinct terms, so it reported 1,053 orphans; all 747
relationships hold 77 terms, so the answer is 984. `stale_assets` reported staleCount 0 from a full
500-Asset page beside a not-measured assetTotal.

Egeria's paging contract: a short page is not the last page, and an empty page is a filtered one; only null
ends a read (pager step 4). These scans are suspect paths, so a null followed by empty probes is acted on but
marked unconfirmed (the overview_metrics ruling (ii)), and a scan that cannot finish (MAX_SCAN_PAGES, or a
server that repeats its page) is None plus an `unmeasured` note, never a figure from the part it read.
Routines whose population is too large to page (an Asset find) report None plus a note when their
page is full, never the sample's figure.
"""
from unittest.mock import MagicMock

import pytest

from pyegeria.view import overview_metrics as om

CAP = om.DEFAULT_CAP


@pytest.fixture(autouse=True)
def _clean():
    om._count_caps.clear()
    om._native_server_ok.clear()
    yield
    om._count_caps.clear()
    om._native_server_ok.clear()


def _rel_pages(table):
    """get_relationships paging like Egeria, keyed by type: rows from the body's startFrom, then null ("No
    elements found"; [] would be a filtered page, pager step 4)."""
    def fake(*a, relationship_type=None, body=None, **kw):
        rows = table.get(relationship_type, [])
        if isinstance(rows, BaseException):
            raise rows
        return rows[body["startFrom"]:body["startFrom"] + body["pageSize"]] or "No elements found"
    return fake


def _find_pages(rows):
    def fake(body, *a, **kw):
        return rows[body["startFrom"]:body["startFrom"] + body["pageSize"]] or "No elements found"
    return fake


def _semantic_assignments(n_rels, n_terms):
    """n_rels SemanticAssignments over n_terms distinct terms, the first page holding few of them
    (as live: the first 500 relationships held 8 terms)."""
    rels = []
    for i in range(n_rels):
        term = f"t{i % 8}" if i < CAP else f"t{8 + (i - CAP) % (n_terms - 8)}"
        rels.append({"relationshipHeader": {"guid": f"r{i}"},
                     "end1": {"guid": f"a{i}", "type": {"typeName": "CSVFile", "superTypeNames": ["Asset"]}},
                     "end2": {"guid": term, "type": {"typeName": "GlossaryTerm"}}})
    return rels


def _mgr(term_total=1061, find=None):
    mgr = MagicMock(spec=["platform_url", "view_server", "find_metadata_elements", "count_metadata_elements"])
    mgr.platform_url, mgr.view_server = "https://localhost:9443", "test-server"
    mgr.count_metadata_elements.return_value = {"count": term_total}
    if find is not None:
        mgr.find_metadata_elements.side_effect = find
    return mgr


# ── orphan_glossary_terms ──────────────────────────────────────────────────

def test_orphan_terms_read_every_semantic_assignment_page():
    ce = MagicMock()
    ce.get_relationships.side_effect = _rel_pages({"SemanticAssignment": _semantic_assignments(747, 77)})
    with om.recording_unmeasured() as notes:
        r = om.orphan_glossary_terms(_mgr(), ce)
    marks = r.pop("unconfirmed")   # pager step 4: get_relationships is NULL_NOT_END, so marked (ruling (ii))
    # 77, not 8; orphanCount needs the whole set, so it isn't measured on an unconfirmed read (after-capture
    # ruling, 3): never 1,053 from part, and never "at most" either
    assert r == {"termTotal": 1061, "referencedCount": 77, "orphanCount": None}
    assert marks["referencedCount"]["words"] == "77 found; Egeria didn't confirm there are no more"
    assert [n["count"] for n in notes] == ["orphanCount"] and "needs the whole set" in notes[0]["reason"]
    # to Egeria's null at 2*CAP, then 6 probes (NULL_NOT_END_PROBE_PAGES)
    assert [c.kwargs["body"]["startFrom"] for c in ce.get_relationships.call_args_list] == [
        k * CAP for k in range(9)]


def test_a_short_page_is_not_the_last_page():
    # A server may filter hits out of a page after fetching it: a short page with more behind it.
    rels = _semantic_assignments(747, 77)
    pages = [rels[:300], rels[CAP:]]   # then null (pager step 4: [] would be a filtered page)
    ce = MagicMock()
    ce.get_relationships.side_effect = lambda *a, body=None, **kw: (
        pages[body["startFrom"] // CAP] if body["startFrom"] // CAP < len(pages) else "No elements found")
    r = om.orphan_glossary_terms(_mgr(), ce)
    assert r["referencedCount"] == 77 and len(ce.get_relationships.call_args_list) == 2 + 7   # null + 6 probes


def test_an_incomplete_semantic_assignment_scan_is_not_an_orphan_count(monkeypatch):
    monkeypatch.setattr(om, "MAX_SCAN_PAGES", 1)
    ce = MagicMock()
    ce.get_relationships.side_effect = _rel_pages({"SemanticAssignment": _semantic_assignments(747, 77)})
    with om.recording_unmeasured() as notes:
        r = om.orphan_glossary_terms(_mgr(), ce)
    assert r == {"termTotal": 1061, "referencedCount": None, "orphanCount": None}
    assert notes == [{"count": "SemanticAssignment relationships", "at_least": CAP,
                      "reason": f"the relationship scan stopped after 1 pages of {CAP} ({CAP} read) before Egeria "
                                f"returned an empty page, so it is incomplete"}]


def test_relationship_scans_carry_paging_and_as_of_in_the_body():
    # get_relationships ignores start_from/page_size whenever a body is given, so the body must carry them.
    ce = MagicMock()
    ce.get_relationships.side_effect = _rel_pages({})
    om.orphan_glossary_terms(_mgr(), ce, as_of="2026-11-01T00:00:00Z")
    assert ce.get_relationships.call_args_list[0].kwargs["body"] == {
        "class": "ResultsRequestBody", "startFrom": 0, "pageSize": CAP, "asOfTime": "2026-11-01T00:00:00Z"}
    assert ce.get_relationships.call_args.kwargs["body"]["asOfTime"] == "2026-11-01T00:00:00Z"   # probes too


# ── stale_assets ────────────────────────────────────────────────────────────

def _assets(n, updated="2020-01-01T00:00:00+00:00"):
    return [{"elementGUID": f"a{i}", "elementHeader": {"versions": {"updateTime": updated}}} for i in range(n)]


# stale_assets no longer reads a page of Assets (6.2.29): it bisects over Egeria's update-time order.
# Its tests are in test_native_counts_dashboard.py.


# ── the other scanners ─────────────────────────────────────────────────────

def test_ai_ready_and_drl_on_a_limited_asset_read_measure_nothing():
    # Pager step 6 (the sweep): the Asset find is paged; a server repeating its full page stalls the read -- a
    # limit -- so nothing is measured, and the note carries the lower bound.
    mgr = _mgr(find=lambda body, *a, **kw: _assets(CAP))
    ce = MagicMock()
    ce.get_relationships.side_effect = _rel_pages({})
    with om.recording_unmeasured() as notes:
        assert om.ai_ready_assets(mgr, ce) == {"aiReadyCount": None, "total": None, "capped": True}
        assert om.drl_readiness_gates(mgr, ce) == {"total": None, "capped": True, "aiReadyCount": None,
                                                    "aiReadyRecentCount": None, "byModality": None}
    assert [n["count"] for n in notes] == ["Asset", "Asset"] and all(n["at_least"] == CAP for n in notes)
    ce.get_relationships.assert_not_called()


def test_ai_ready_reads_assets_past_a_short_page():
    # a short first page is not every Asset (pager step 6): a1 on page 1, a2 on page 2
    def asset(guid):
        return {"elementGUID": guid, "classifications": [{"classificationName": "Confidentiality"}],
                "elementProperties": {"propertyValueMap": {"description": {"primitiveValue": "d"}}}}
    pages = {0: [asset("a1")], CAP: [asset("a2")]}
    mgr = _mgr(find=lambda body, *a, **kw: pages.get(body["startFrom"], "No elements found"))
    ce = MagicMock()
    ce.get_relationships.side_effect = _rel_pages({"DataFlow": [
        {"relationshipHeader": {"guid": "f1"}, "end1": {"guid": "a1"}, "end2": {"guid": "a2"}}]})
    r = om.ai_ready_assets(mgr, ce)
    assert r["total"] == 2 and r["aiReadyCount"] == 2
    assert r["unconfirmed"]["total"]["words"] == "at least 2"   # find_metadata_elements, ungated: unconfirmed


def test_ai_ready_on_a_gated_platform_is_a_plain_total(monkeypatch):
    from pyegeria.core import paging
    monkeypatch.setattr(paging, "paging_for", lambda method, client=None: (
        {"end_policy": "trusted"} if method == "find_metadata_elements" else paging._paging(method, False)))
    asset = {"elementGUID": "a1", "classifications": [{"classificationName": "Confidentiality"}],
             "elementProperties": {"propertyValueMap": {"description": {"primitiveValue": "d"}}}}
    mgr = _mgr(find=_find_pages([asset]))
    ce = MagicMock()
    ce.get_relationships.side_effect = _rel_pages({"DataFlow": [
        {"relationshipHeader": {"guid": "f1"}, "end1": {"guid": "a1"}, "end2": {}}]})
    r = om.ai_ready_assets(mgr, ce)
    assert r["total"] == 1   # a confirmed Asset read: no mark on the total
    assert "total" not in r.get("unconfirmed", {}) and "aiReadyCount" in r["unconfirmed"]   # DataFlow: never trusted


def test_lineage_reads_every_dataflow_page():
    asset = {"elementGUID": "a1", "classifications": [{"classificationName": "Confidentiality"}],
             "elementProperties": {"propertyValueMap": {"description": {"primitiveValue": "d"}}}}
    mgr = _mgr(find=_find_pages([asset]))
    flows = [{"relationshipHeader": {"guid": f"f{i}"}, "end1": {"guid": f"x{i}"}, "end2": {"guid": f"y{i}"}}
             for i in range(CAP)] + [{"relationshipHeader": {"guid": "last"}, "end1": {"guid": "a1"}, "end2": {}}]
    ce = MagicMock()
    ce.get_relationships.side_effect = _rel_pages({"DataFlow": flows})
    r = om.ai_ready_assets(mgr, ce)
    marks = r.pop("unconfirmed")
    assert r == {"aiReadyCount": 1, "total": 1, "capped": False}  # a1 is on page 2
    assert marks["aiReadyCount"]["words"] == "at least 1"


@pytest.mark.parametrize("routine,field", [(om.governed_coverage, "governedCount"),
                                           (om.ownership_coverage, "ownershipCount")])
def test_coverage_finds_page_past_the_first_page(routine, field):
    els = [{"elementGUID": f"e{i}", "classifications": [{"classificationName": "Ownership"}]}
           for i in range(CAP + 1)]
    r = routine(_mgr(find=_find_pages(els)))
    assert r[field] == CAP + 1


def test_karma_leaderboard_reads_every_page():
    def rec(i, karma):
        return {"elementGUID": f"c{i}", "elementProperties": {"propertyValueMap": {
                    "karmaPoints": {"primitiveValue": karma},
                    "displayName": {"primitiveValue": f"Contribution record for p{i}"}}},
                "classifications": [{"classificationName": "Anchors", "classificationProperties": {
                    "propertyValueMap": {"anchorTypeName": {"primitiveValue": "Person"}}}}]}
    records = [rec(i, 1) for i in range(CAP)] + [rec(CAP, 99)]   # the top contributor is on page 2
    top = om.karma_leaderboard(_mgr(find=_find_pages(records)), top_n=1)
    assert top[0]["name"] == f"p{CAP}" and top[0]["karmaPoints"] == 99


def test_certifications_scan_reads_every_page():
    certs = [{"relationshipHeader": {"guid": f"c{i}"}} for i in range(CAP + 3)]
    ce = MagicMock()
    ce.get_relationships.side_effect = _rel_pages({"Certification": certs})
    assert om.certifications_summary(ce)["active"] == CAP + 3


@pytest.mark.parametrize("routine,field", [(om.contextualised_coverage, "contextualisedCount"),
                                           (om.solution_component_realisation, "solutionComponentsRealised")])
def test_implemented_by_scans_read_every_page(routine, field):
    rels = [{"relationshipHeader": {"guid": f"r{i}"},
             "end1": {"guid": f"sc{i}", "type": {"typeName": "SolutionComponent"}},
             "end2": {"guid": f"a{i}", "type": {"typeName": "CSVFile", "superTypeNames": ["Asset"]}}}
            for i in range(CAP + 2)]
    ce = MagicMock()
    ce.get_relationships.side_effect = _rel_pages({"ImplementedBy": rels})
    assert routine(_mgr(term_total=2000), ce)[field] == CAP + 2


def test_active_contributors_read_every_page_and_an_incomplete_type_is_none(monkeypatch):
    rows = [{"relationshipHeader": {"guid": f"r{i}", "versions": {"createdBy": f"u{i}"}}} for i in range(CAP + 1)]
    ce = MagicMock()
    ce.get_relationships.side_effect = _rel_pages({"AttachedRating": rows})
    assert om.active_contributors(ce)["byType"]["ratings"] == CAP + 1
    monkeypatch.setattr(om, "MAX_SCAN_PAGES", 1)
    r = om.active_contributors(ce)
    assert r["byType"]["ratings"] is None and r["contributors"] is None


def test_engagement_series_a_failed_type_is_none_never_a_row_of_zeros():
    ce = MagicMock()
    ce.get_relationships.side_effect = _rel_pages({"AttachedComment": RuntimeError("down")})
    with om.recording_unmeasured() as notes:
        series = om.engagement_series(ce, as_of="2026-11-08T00:00:00Z", weeks=3)
    assert len(series) == 3
    assert all(p["comments"] is None and p["total"] is None and p["ratings"] == 0 for p in series)
    assert notes and notes[0]["count"] == "AttachedComment relationships"
