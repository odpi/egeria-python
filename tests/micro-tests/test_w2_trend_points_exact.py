# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""W2 (6.2.34): every metric_trend point says whether its number is exact, and a lower bound is
never shown as a bare number.

Live finding (2026-11-10): `metric_trend` over count_elements(GlossaryTerm), 90d / 3 points, gave
200, 200, 1065. Checked the same day on laz, read-only: those are true. Egeria's native count honours
asOfTime (MetadataElementHandler.countMetadataElements passes it to the repository's SQL COUNT), the
GlossaryTerm count is 200 at 96 hours ago and 1061 at 72 (a glossary load), and paged finds at the
past time end at 200 for page sizes 70, 200 and 1000; Asset reads 288 at the same times, above the
cap. The first test is that real shape: all exact, all native.

The fakes below answer like Egeria: count_metadata_elements(body) gives {"count": n}, and
find_metadata_elements gives a page of at most DEFAULT_CAP. Nothing reaches Egeria.
"""
import json

import pytest

from pyegeria.view import format_set_executor as fse
from pyegeria.view import overview_metrics as om
from pyegeria.view.role_supply import Subject, Viewer

pytestmark = pytest.mark.unit

CAP = om.DEFAULT_CAP
GE = "≥"


@pytest.fixture(autouse=True)
def _reset_seam_caches():
    om._count_caps.clear()
    om._native_server_ok.clear()
    yield
    om._count_caps.clear()
    om._native_server_ok.clear()


class _Egeria:
    """GlossaryTerm: `past` before now, `now` today. `as_of_ok=False`: a native count with asOfTime
    is refused (an old server), and the find fallback sees a full page in the past."""
    platform_url, view_server = "https://fake:9443", "fake"

    def __init__(self, past=200, now=1065, as_of_ok=True):
        self.past, self.now, self.as_of_ok = past, now, as_of_ok
        self.native_calls, self.find_calls = [], []

    def count_metadata_elements(self, body, **kw):
        self.native_calls.append(body.get("asOfTime"))
        if body.get("asOfTime") and not self.as_of_ok:
            raise RuntimeError("PROPERTY_SERVER_ERROR_500 the history query for the count failed")
        return {"count": self.past if body.get("asOfTime") else self.now}

    def find_metadata_elements(self, body, *a, **kw):
        self.find_calls.append(body.get("asOfTime"))
        n = self.past if body.get("asOfTime") else self.now
        return [{"elementGUID": f"g{i}"} for i in range(min(n, body.get("pageSize") or CAP, CAP))]


def _trend(egeria, population="repository", **kw):
    return om.metric_trend(egeria, egeria, "count_elements", window="90d", points=3,
                           metric_params={"type_name": "GlossaryTerm", "population": population}, **kw)


def test_the_live_shape_is_exact_at_every_point():
    egeria = _Egeria(past=200, now=1065)
    series = _trend(egeria)
    assert [p["value"] for p in series] == [200, 200, 1065]
    assert [p["display"] for p in series] == ["200", "200", "1065"]
    for p in series:
        assert p["measurement"] == {"exact": True, "capped": False, "at_least": None, "how": "native",
                                    "reasons": []}
    assert len([a for a in egeria.native_calls if a]) == 2  # asOfTime reached the native count
    assert egeria.find_calls == []


def test_a_native_count_that_refuses_as_of_time_gives_lower_bounds_in_the_viewer_population():
    egeria = _Egeria(past=5000, now=1065, as_of_ok=False)
    with om.recording_unmeasured() as notes:
        series = _trend(egeria, population="viewer")
    past, today = series[:2], series[2]
    for p in past:
        assert p["value"] is None  # never the cap as a value
        assert p["display"] == f"{GE}{CAP}"
        assert p["measurement"]["exact"] is False and p["measurement"]["capped"] is True
        assert p["measurement"]["at_least"] == CAP and p["measurement"]["how"] == "find-capped"
        assert f"at least {CAP}" in p["measurement"]["reasons"][0]["reason"]
    assert today["value"] == 1065 and today["display"] == "1065" and today["measurement"]["exact"]
    assert len(notes) == 2  # the enclosing recorder still hears each point's note


def test_a_repository_count_that_refuses_as_of_time_is_not_measured_not_a_bound():
    series = _trend(_Egeria(as_of_ok=False))
    for p in series[:2]:
        assert p["value"] is None and p["display"] == "not measured"
        assert p["measurement"]["how"] == "not-measured" and p["measurement"]["capped"] is False
    assert series[2]["measurement"]["exact"]


def test_a_short_find_page_is_exact_and_says_find():
    series = _trend(_Egeria(past=40, now=50, as_of_ok=False), population="viewer")
    assert [p["display"] for p in series] == ["40", "40", "50"]
    assert [p["measurement"]["how"] for p in series] == ["find", "find", "native"]
    assert all(p["measurement"]["exact"] for p in series)


def test_strict_raises_with_the_points_that_are_not_exact():
    with pytest.raises(om.TrendNotExact) as exc:
        _trend(_Egeria(past=5000, as_of_ok=False), population="viewer", strict=True)
    assert exc.value.total == 3 and len(exc.value.points) == 2
    assert "2 of 3 points are not exact (2 lower bounds)" in str(exc.value)
    assert f"{GE}{CAP}" in str(exc.value)


def test_strict_on_an_exact_series_returns_it():
    assert [p["value"] for p in _trend(_Egeria(), strict=True)] == [200, 200, 1065]


def test_strict_reaches_a_target_that_takes_it(monkeypatch):
    seen = []
    real = om.count_elements

    def spy(mgr, type_name=None, as_of=None, strict=False, population=None):
        seen.append(strict)
        return real(mgr, type_name, as_of, strict=strict, population=population)

    monkeypatch.setattr(om, "count_elements", spy)
    from pyegeria.view import format_set_executor
    monkeypatch.setattr(format_set_executor, "resolve_report_spec_function", lambda name: spy)
    _trend(_Egeria(), strict=True)
    assert seen == [True, True, True]


def test_a_failed_snapshot_says_error_and_is_not_exact():
    def boom(mgr, as_of=None):
        raise RuntimeError("boom")

    from pyegeria.view.analytic_registry import clear_runtime_analytic_functions, register_analytic_functions
    om._w2_boom = boom
    register_analytic_functions({"w2-boom": {"name": "w2-boom", "function": "pyegeria.view.overview_metrics._w2_boom"}})
    try:
        series = om.metric_trend(_Egeria(), _Egeria(), "w2-boom", window="7d", points=2)
        assert all(p["value"] is None and p["display"] == "not measured" for p in series)
        assert all(p["measurement"]["how"] == "error" and not p["measurement"]["exact"] for p in series)
        with pytest.raises(om.TrendNotExact):
            om.metric_trend(_Egeria(), _Egeria(), "w2-boom", window="7d", points=2, strict=True)
    finally:
        clear_runtime_analytic_functions()
        del om._w2_boom


def test_a_dict_target_carries_measurement_but_no_display():
    series = om.metric_trend(_Egeria(), _Egeria(), "term_definition_completeness", window="7d", points=2)
    assert all("measurement" in p and "display" not in p for p in series)


# ── what a reader sees: the SERIES chart ──

class _Supply:
    def __init__(self, egeria):
        self.egeria = egeria

    def client(self, cls):
        return self.egeria

    def viewer(self):
        return Viewer(user_id="u", is_admin=False, display_name="U")

    def reader(self, source):
        return None

    def subject(self):
        return Subject(guid="g", type_name="Asset")

    def refusal_words(self, kind):
        return f"cannot supply {kind}"


def _series(egeria, fmt="SERIES", population="repository"):
    return fse.exec_report_spec(
        "Analytic Demo - Metric Trend (Governance Coverage)", output_format=fmt,
        params={"metric_path": "count_elements", "window": "90d", "points": 3,
                "metric_params": {"type_name": "GlossaryTerm", "population": population}},
        view_server="vs", view_url="https://x", user="u", user_pass="p", supply=_Supply(egeria))


def _layers(chart):
    return chart.get("layer") or [chart]


def test_an_exact_trend_is_charted_with_its_values():
    out = _series(_Egeria())
    assert out["kind"] == "json" and "unmeasured" not in out
    assert [r["value"] for r in out["data"]["data"]["values"]] == [200, 200, 1065]


def test_a_lower_bounded_trend_is_charted_with_every_bound_marked():
    out = _series(_Egeria(past=5000, as_of_ok=False), population="viewer")
    assert out["kind"] == "json"
    chart = out["data"]
    rows = chart["data"]["values"]
    assert [r["display"] for r in rows] == [f"{GE}{CAP}", f"{GE}{CAP}", "1065"]
    assert [r["lowerBound"] for r in rows] == [True, True, False]
    assert chart["title"]["subtitle"].startswith("2 of 3 points are lower bounds")
    label = chart["layer"][1]
    assert label["encoding"]["text"]["field"] == "display"
    assert label["transform"] == [{"filter": "datum.lowerBound"}]
    assert {"field": "display", "type": "nominal", "title": "Count"} in chart["layer"][0]["encoding"]["tooltip"]
    assert [n["at_least"] for n in out["unmeasured"]] == [CAP]  # one note, not one per point


def test_a_trend_with_an_unmeasured_point_draws_no_chart():
    out = _series(_Egeria(as_of_ok=False))  # repository: no bound, no number
    assert out["kind"] == "absent" and "data" not in out


@pytest.mark.parametrize("past,population,bounded", [
    (5000, "viewer", True),
    (5000, "repository", False),
])
@pytest.mark.parametrize("fmt", ["SERIES", "BAR", "DICT"])
def test_no_lower_bound_is_ever_shown_without_its_marker(past, population, bounded, fmt):
    out = _series(_Egeria(past=past, as_of_ok=False), fmt, population)
    text = json.dumps(out, ensure_ascii=False)
    if out["kind"] == "absent":
        assert "data" not in out
        return
    data = out["data"]
    rows = data["data"]["values"] if isinstance(data, dict) and "data" in data else data
    for r in rows:
        if r.get("lowerBound") or (isinstance(r.get("measurement"), dict) and r["measurement"]["capped"]):
            assert r["display"].startswith(GE), (fmt, r)
            assert r.get("value") in (None, CAP)
            if r.get("value") == CAP:
                assert r.get("lowerBound") is True
    assert (f"{GE}{CAP}" in text) == bounded
    assert f'"value": {CAP}' not in text or bounded and fmt == "SERIES"  # only a marked chart bound
