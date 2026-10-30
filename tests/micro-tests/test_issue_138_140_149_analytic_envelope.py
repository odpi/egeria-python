# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Regression tests for the analytic executor and registry changes requested by
trellis-analytics (PYEGERIA_ISSUES.md):

- ISSUE-138: `analytic_binders` builds a non-JSON argument (e.g. a reader) from
  the call params, so a routine can be named by its own dotted path.
- ISSUE-139: a result's state envelope is returned on every output and put on
  the chart as a subtitle.
- ISSUE-140: no chart is drawn unless the state is `measured`.
- ISSUE-149: AnalyticFunctionSpec carries the manifest fields, all optional.

No live server: the routines live in a fake module, and the spec lookup is patched.
"""
import sys
import types

import pytest
from pydantic import BaseModel, ValidationError

import pyegeria.view.format_set_executor as fse
from pyegeria.view.analytic_registry import AnalyticFunctionSpec

MOD = "fake_trellis_analytics"


class Reader:
    def __init__(self, url: str = ""):
        self.url = url


class Env(BaseModel):
    result_state: str
    result_state_reason: str = ""


class CoverageResult(BaseModel):
    envelope: Env
    published: int = 0


def read_with(ods: Reader, slug: str) -> dict:
    return {"state": "measured", "url": ods.url, "slug": slug, "Published": 3, "Not yet published": 1}


def measured() -> dict:
    return {"state": "measured", "Published": 3, "Not yet published": 1}


def not_established() -> dict:
    return {"state": "not_established", "state_reason": "could not open the ODS", "Published": 0, "Blocked": 0}


def nothing_found() -> dict:
    return {"state": "nothing_found", "Published": 0, "Not yet published": 0}


def not_applicable() -> dict:
    return {"state": "not_applicable", "state_reason": "not a database", "Published": 0, "Other": 0}


def plain_counts() -> dict:
    return {"A": 1, "B": 2}


def model_result() -> CoverageResult:
    return CoverageResult(envelope=Env(result_state="nothing_found"), published=0)


@pytest.fixture(autouse=True)
def fake_module(monkeypatch):
    mod = types.ModuleType(MOD)
    for f in (Reader, read_with, measured, not_established, nothing_found, not_applicable, plain_counts, model_result):
        setattr(mod, f.__name__, f)
    monkeypatch.setitem(sys.modules, MOD, mod)

    def no_egeria(*a, **k):
        raise AssertionError("an analytic routine with no client must not build an Egeria client")

    monkeypatch.setattr(fse, "EgeriaTech", no_egeria)
    monkeypatch.setattr(fse, "get_report_spec_heading", lambda name: "Heading")
    yield


def _use_spec(monkeypatch, action: dict):
    fmt = {"target_type": None, "action": {"function": None, **action}}
    monkeypatch.setattr(fse, "select_report_spec", lambda name, fmt_type: fmt)


# ISSUE-138
def test_binder_builds_the_reader_from_params(monkeypatch):
    _use_spec(monkeypatch, {"analytic_function": f"{MOD}.read_with",
                            "analytic_binders": {"ods": f"{MOD}.Reader"}})
    out = fse.exec_report_spec("tile", output_format="DICT", params={"slug": "db1", "url": "pg://x"})
    assert out["data"]["url"] == "pg://x"  # the factory got url
    assert out["data"]["slug"] == "db1"  # the routine still got its own param


def test_binder_accepts_colon_form(monkeypatch):
    _use_spec(monkeypatch, {"analytic_function": f"{MOD}.read_with",
                            "analytic_binders": {"ods": f"{MOD}:Reader"}})
    out = fse.exec_report_spec("tile", output_format="DICT", params={"slug": "db1"})
    assert out["data"]["url"] == ""


# ISSUE-139 / ISSUE-140
def test_measured_bar_gets_subtitle_and_envelope(monkeypatch):
    _use_spec(monkeypatch, {"analytic_function": f"{MOD}.measured"})
    out = fse.exec_report_spec("tile", output_format="BAR")
    chart = out["data"]
    assert "$schema" in chart
    assert chart["title"] == {"text": "Heading", "subtitle": "measured"}
    assert out["envelope"]["state"] == "measured"


def test_not_established_draws_no_chart(monkeypatch):
    _use_spec(monkeypatch, {"analytic_function": f"{MOD}.not_established"})
    out = fse.exec_report_spec("tile", output_format="BAR")
    assert out["kind"] == "absent" and "data" not in out  # ISSUE-171: the sentence, not a chart
    assert out["envelope"] == {"state": "not_established", "reason": "could not open the ODS",
                               "subtitle": "not established · could not open the ODS"}


def test_nothing_found_is_charted_as_real_zeros(monkeypatch):
    _use_spec(monkeypatch, {"analytic_function": f"{MOD}.nothing_found"})
    out = fse.exec_report_spec("tile", output_format="BAR")
    assert "$schema" in out["data"]
    assert out["data"]["title"]["subtitle"] == "nothing found"


def test_not_applicable_draws_no_chart(monkeypatch):
    _use_spec(monkeypatch, {"analytic_function": f"{MOD}.not_applicable"})
    out = fse.exec_report_spec("tile", output_format="BAR")
    assert out["kind"] == "absent" and out["envelope"]["state"] == "not_applicable"


def test_dict_output_carries_envelope(monkeypatch):
    _use_spec(monkeypatch, {"analytic_function": f"{MOD}.not_established"})
    out = fse.exec_report_spec("tile", output_format="DICT")
    assert out["kind"] == "absent" and out["envelope"]["state"] == "not_established"  # ISSUE-171


def test_model_result_with_envelope_attribute(monkeypatch):
    _use_spec(monkeypatch, {"analytic_function": f"{MOD}.model_result"})
    out = fse.exec_report_spec("tile", output_format="DICT")
    assert out["envelope"]["state"] == "nothing_found"
    assert out["data"]["published"] == 0  # dumped to plain data


def test_no_envelope_keeps_old_shape(monkeypatch):
    _use_spec(monkeypatch, {"analytic_function": f"{MOD}.plain_counts"})
    out = fse.exec_report_spec("tile", output_format="BAR")
    assert "envelope" not in out
    assert out["data"]["title"] == "Heading"  # plain title, no subtitle


# ISSUE-149
def test_manifest_fields_default_and_existing_entries_still_load():
    spec = AnalyticFunctionSpec(name="x", function=f"{MOD}.measured")
    assert (spec.kind, spec.source, spec.version, spec.envelope) == ("routine", "", "", False)
    assert spec.annotation_type == "" and spec.resource_types == [] and spec.family == "" and spec.tags == []


def test_manifest_fields_set():
    spec = AnalyticFunctionSpec(name="x", function=f"{MOD}.measured", kind="step", source="ods",
                                version="0.1.0", envelope=True, annotation_type="ResourceMeasureAnnotation",
                                resource_types=["database"], family="Curation", tags=["coverage"])
    assert spec.kind == "step" and spec.resource_types == ["database"] and spec.family == "Curation"


def test_unknown_source_warns_not_rejects():
    spec = AnalyticFunctionSpec(name="x", function=f"{MOD}.measured", source="kafka")
    assert spec.source == "kafka"


def test_kind_is_routine_or_step():
    with pytest.raises(ValidationError):
        AnalyticFunctionSpec(name="x", function=f"{MOD}.measured", kind="spec")
