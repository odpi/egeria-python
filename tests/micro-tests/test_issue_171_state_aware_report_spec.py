"""ISSUE-171: when an analytic function's result is not a measured value, exec_report_spec
says so -- with the function's declared absence sentence -- instead of returning empty
or drawing numbers that read as an answer."""
import sys
import types

import pytest

import pyegeria.view.format_set_executor as fse
from pyegeria.view.analytic_registry import (
    clear_runtime_analytic_functions, get_analytic_registry, register_analytic_functions)

MOD = "fake_issue_171_analytics"

ABSENCE = {
    "not_measured": "Coverage was not measured: the catalog could not be read.",
    "not_permitted": "Coverage was not measured: reading the catalog is not permitted.",
    "not_applicable": "Coverage does not apply to this resource.",
    "measured_nothing": "The catalog was read and holds no columns.",
}


def not_established():
    return {"state": "not_established", "state_reason": "could not open the ODS", "described": 0}


def not_permitted():
    return {"state": "not_established", "state_reason": "403 from the catalog", "absence": "not_permitted"}


def not_applicable():
    return {"state": "not_applicable", "state_reason": "not a database"}


def nothing_found_empty():
    return {"envelope": {"state": "nothing_found"}, "counts": {}}


def nothing_found_counts():
    return {"state": "nothing_found", "byType": {"Table": 0, "Column": 0}}


def measured():
    return {"state": "measured", "byType": {"Table": 3, "Column": 12}}


@pytest.fixture(autouse=True)
def fake_module(monkeypatch):
    mod = types.ModuleType(MOD)
    for f in (not_established, not_permitted, not_applicable, nothing_found_empty, nothing_found_counts, measured):
        setattr(mod, f.__name__, f)
    monkeypatch.setitem(sys.modules, MOD, mod)
    monkeypatch.setenv("PYEGERIA_ANALYTIC_MODULE_PREFIXES", f"pyegeria,{MOD}")  # if ISSUE-169's resolver is in
    monkeypatch.setattr(fse, "EgeriaTech", lambda *a, **k: pytest.fail("no Egeria call expected"))
    monkeypatch.setattr(fse, "get_report_spec_heading", lambda name: "Coverage")
    clear_runtime_analytic_functions()
    yield
    clear_runtime_analytic_functions()


def _declare(func_name: str):
    register_analytic_functions({f"cov-{func_name}": {
        "name": f"cov-{func_name}", "function": f"{MOD}.{func_name}",
        "declaration": {"result_kind": "measure", "absence": ABSENCE, "measures": [
            {"name": "described", "unit": "columns", "as_of": "asOf", "value_field": "described"}]},
    }})


def _run(monkeypatch, func_name: str, output_format: str = "DICT"):
    # Report specs name functions by registered name (ISSUE-173); an undeclared
    # function is registered with no declaration.
    name = f"cov-{func_name}"
    if name not in get_analytic_registry():
        register_analytic_functions({name: {"name": name, "function": f"{MOD}.{func_name}"}})
    fmt = {"action": {"analytic_function": name}, "target_type": "Referenceable"}
    monkeypatch.setattr(fse, "select_report_spec", lambda name, fmt_type: fmt)
    return fse.exec_report_spec("coverage", output_format=output_format)


@pytest.mark.parametrize("output_format", ["DICT", "BAR"])
def test_not_established_says_the_declared_sentence_and_draws_nothing(monkeypatch, output_format):
    _declare("not_established")
    out = _run(monkeypatch, "not_established", output_format)
    assert out["kind"] == "absent"
    assert out["content"] == ABSENCE["not_measured"]
    assert out["absence"] == {"state": "not_measured", "sentence": ABSENCE["not_measured"],
                              "reason": "could not open the ODS", "declared": True}
    assert "data" not in out  # no top-level counts to draw as an answer
    assert out["detail"]["described"] == 0  # the partial result is still there, labelled as detail


def test_the_result_can_claim_not_permitted(monkeypatch):
    _declare("not_permitted")
    out = _run(monkeypatch, "not_permitted")
    assert (out["kind"], out["absence"]["state"], out["content"]) == (
        "absent", "not_permitted", ABSENCE["not_permitted"])


def test_not_applicable_says_so(monkeypatch):
    _declare("not_applicable")
    out = _run(monkeypatch, "not_applicable", "BAR")
    assert (out["kind"], out["content"]) == ("absent", ABSENCE["not_applicable"])


def test_nothing_found_carries_the_measured_nothing_sentence(monkeypatch):
    _declare("nothing_found_empty")
    out = _run(monkeypatch, "nothing_found_empty")
    assert out["kind"] == "json"  # a real answer: the dict, with its sentence
    assert out["absence"]["state"] == "measured_nothing"
    assert out["absence"]["sentence"] == ABSENCE["measured_nothing"]


def test_nothing_found_counts_are_charted_with_the_declared_sentence(monkeypatch):
    _declare("nothing_found_counts")
    out = _run(monkeypatch, "nothing_found_counts", "BAR")
    assert "$schema" in out["data"]
    assert out["data"]["title"] == {"text": "Coverage", "subtitle": ABSENCE["measured_nothing"]}


def test_undeclared_function_gets_words_from_its_own_reason(monkeypatch):
    out = _run(monkeypatch, "not_established")
    assert out["kind"] == "absent"
    assert out["content"] == "Not measured: could not open the ODS."
    assert out["absence"]["declared"] is False


def test_measured_result_is_unchanged(monkeypatch):
    _declare("measured")
    out = _run(monkeypatch, "measured")
    assert out["kind"] == "json" and "absence" not in out
    assert out["data"]["byType"] == {"Table": 3, "Column": 12}


def test_registered_name_finds_the_declaration(monkeypatch):
    _declare("not_established")
    assert fse._declaration_for("cov-not_established").absence.not_measured == ABSENCE["not_measured"]
    assert fse._declaration_for(f"{MOD}.not_established") is not None
    assert fse._declaration_for(f"{MOD}.unregistered") is None
