# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""RS-W2-2 PR-B: every report spec is resolved at load through the §2c checks; a spec that fails
is listed as unrunnable with the failing check's words, never deleted and never run blank."""

import pytest
from loguru import logger

import pyegeria.view.base_report_formats as brf
from pyegeria.view import spec_resolver as sr
from pyegeria.view._output_format_models import ActionParameter, Column, Format, FormatSet
from pyegeria.view.analytic_registry import (AnalyticFunctionSpec, Binding,
                                             clear_runtime_analytic_functions, register_analytic_functions)

FIND = "ValidMetadataManager.get_valid_metadata_values"  # takes no **kwargs, so its names are checked


def _spec(action=None, types=("DICT",), columns=(), **kw) -> FormatSet:
    return FormatSet(heading="Probe", description="probe", target_type="Referenceable", action=action,
                     formats=[Format(types=list(types), attributes=list(columns))], **kw)


def _find(**kw) -> ActionParameter:
    return ActionParameter(function=kw.pop("function", FIND), **kw)


def _analytic(name="count_elements", **kw) -> ActionParameter:
    return ActionParameter(analytic_function=name, **kw)


def _words(result) -> str:
    assert isinstance(result, sr.Unrunnable), f"expected unrunnable, got {result}"
    return result.unrunnable_reason


@pytest.fixture(autouse=True)
def _clean():
    yield
    clear_runtime_analytic_functions()
    brf.clear_runtime_report_specs()


# ── The census over every registered spec (base_report_formats + analytic demo specs) ──

#: The unrunnable specs the first resolution found, each a real defect (see the PR body).
KNOWN_UNRUNNABLE = {
    "Asset-Graph": "its find method 'ServerClient.get_asset_graph' does not exist",
    "Data-Classes": "its find method 'DataDesigner.find_data_classes' does not exist",
}


def test_every_registered_spec_resolves_and_the_unrunnable_ones_are_the_known_defects():
    results = sr.resolve_all(refresh=True)
    assert set(results) == set(brf.get_report_registry())
    assert not [n for n, r in results.items() if r.kind == "unknown"], "the resolver itself failed on a spec"
    bad = sr.unrunnable_specs()
    assert set(bad) == set(KNOWN_UNRUNNABLE)
    for name, words in KNOWN_UNRUNNABLE.items():
        assert words in bad[name].unrunnable_reason and bad[name].checks == [1]


def test_format_only_specs_are_the_specs_with_no_action():
    registry = brf.get_report_registry()
    format_only = {n for n, r in sr.resolve_all().items() if isinstance(r, sr.Unrunnable) and r.kind == "format_only"}
    assert format_only == {n for n, s in registry.items() if not s.action}
    assert "Referenceable" in format_only
    assert "it has no action" in sr.spec_status("Referenceable")["unrunnable_reason"]


def test_every_analytic_demo_spec_is_runnable():
    from pyegeria.view.analytic_demo_specs import get_analytic_demo_specs
    results = sr.resolve_all()
    for label in get_analytic_demo_specs():
        assert results[label].runnable, results[label].unrunnable_reason


# ── Check 1: names ──

@pytest.mark.parametrize("action, words", [
    (_find(function="DataDesigner.find_nothing_at_all"), "client class DataDesigner has no '_async_find_nothing_at_all'"),
    (_find(function="NoSuchClass.find_nothing_at_all"), "EgeriaTech or any client it proxies to has no"),
    (_find(function="a.b.c"), "is not Class.method"),
    (_analytic("not_registered"), "'not_registered', which is not a registered name"),
    (_analytic("pyegeria.view.overview_metrics.count_elements"), "use its registered name 'count_elements'"),
    (_analytic("metric_trend", analytic_spec_params={"metric_path": "nope"}),
     "its metric_path 'nope' is not a registered routine name"),
    (_analytic("count_elements", analytic_binders={"type_name": "os.getcwd"}), "its binder for type_name is refused"),
])
def test_check_1_names(action, words):
    result = sr.resolve(_spec(action), "Probe")
    assert words in _words(result) and 1 in result.checks


def test_check_1_a_routine_with_no_python_binding():
    register_analytic_functions({"saved_census": AnalyticFunctionSpec(
        name="saved_census", bindings=[Binding(kind="egeria_query", target="Census query")])})
    assert ("routine 'saved_census' has no binding this executor can honour (its bindings: egeria_query "
            "'Census query'; pyegeria runs python bindings only)") in _words(sr.resolve(_spec(_analytic("saved_census"))))


def test_check_1_an_unimportable_python_binding():
    register_analytic_functions({"gone": AnalyticFunctionSpec(name="gone", function="pyegeria.no_such_module.f")})
    assert "binds python target 'pyegeria.no_such_module.f', which cannot be imported" in _words(
        sr.resolve(_spec(_analytic("gone"))))


# ── Check 2: parameters ──

def test_check_2_a_spec_param_the_method_does_not_accept():
    words = _words(sr.resolve(_spec(_find(required_params=["property_name"], spec_params={"colour": "red"}))))
    assert f"its spec parameter colour is sent on every run and {FIND} does not accept it" in words


def test_check_2_a_required_param_the_method_does_not_accept():
    words = _words(sr.resolve(_spec(_find(required_params=["property_name", "search_string"]))))
    assert "its required parameter search_string is sent on every run" in words


def test_check_2_output_format_and_report_spec_are_always_sent(monkeypatch):
    async def _async_find_things(self, search_string: str):
        return []
    monkeypatch.setattr(sr, "_find_method", lambda decl: (_async_find_things, ""))
    words = _words(sr.resolve(_spec(_find(function="Things.find_things", required_params=["search_string"]))))
    assert "the executor always passes output_format, report_spec and Things.find_things does not accept them" in words


def test_check_2_an_optional_param_the_method_does_not_accept_is_a_warning():
    result = sr.resolve(_spec(_find(required_params=["property_name"], optional_params=["as_of_time"])))
    assert result.runnable
    assert any("optional parameter as_of_time is not accepted" in w for w in result.warnings)


def test_check_2_analytic_param_not_declared_is_refused_with_the_declared_list():
    words = _words(sr.resolve(_spec(_analytic(analytic_spec_params={"typename": "Asset"}))))
    assert ("its analytic_spec_params typename is not declared by routine 'count_elements' "
            "(declared: type_name, as_of, strict, classifications, population)") in words


def test_check_2_a_routine_that_declares_no_params_warns_instead():
    register_analytic_functions({"silent": AnalyticFunctionSpec(
        name="silent", function="pyegeria.view.overview_metrics.count_elements")})
    result = sr.resolve(_spec(_analytic("silent", analytic_spec_params={"type_name": "Asset"})))
    assert result.runnable
    assert any("routine 'silent' declares no parameters" in w for w in result.warnings)


# ── Check 4: formatter vs out ──

@pytest.mark.parametrize("spec, words", [
    (_spec(_find(required_params=["property_name"]), types=("DICT", "SPREADSHEET")),
     "its output format SPREADSHEET is not one the executor renders"),
    (_spec(_find(required_params=["property_name"]), types=("BAR",)),
     "it offers BAR, a chart, and has no analytic routine to chart"),
    (_spec(_find(required_params=["property_name"]),
           columns=[Column(name="Terms", key="terms", detail_spec="No-Such-Spec")]),
     "drills into detail_spec 'No-Such-Spec', which is not a registered report spec"),
    (_spec(_analytic(), columns=[Column(name="Count", key="count")]),
     "its column 'Count' reads field 'count', which routine 'count_elements' does not declare in out "
     "(declared: value)"),
])
def test_check_4_formatter_against_out(spec, words):
    result = sr.resolve(spec, "Probe")
    assert words in _words(result) and 4 in result.checks


def test_check_4_a_declared_column_and_a_chart_pass():
    result = sr.resolve(_spec(_analytic("counts_by_type"), types=("DICT", "BAR"),
                              columns=[Column(name="Count", key="count"), Column(name="Type", key="type")]))
    assert result.runnable and result.output_formats == ["DICT", "BAR"]


# ── What a resolved spec records (checks 3, 5, 6, 7) ──

def test_a_find_spec_records_its_stage_and_seed():
    result = sr.resolve(_spec(_find(required_params=["property_name"])))
    assert result.runnable and result.kind == "find"
    assert result.seeds == [FIND]
    assert result.stages == [{"kind": "producer", "name": FIND, "binding": "python (client method)"}]
    assert any(n.startswith("check 3: a single stage") for n in result.notes)
    assert any("a find method declares no out" in n for n in result.notes)


def test_an_analytic_spec_records_role_inputs_admission_and_tile_safe():
    result = sr.resolve(_spec(_analytic()))
    assert result.runnable and result.kind == "analytic" and result.seeds == []
    assert result.stages == [{"kind": "routine", "name": "count_elements",
                              "binding": "python pyegeria.view.overview_metrics.count_elements"}]
    assert result.admission == {"resource_types": [], "test_only": False} and result.tile_safe is None
    assert any(n.startswith("check 5:") and "(W2-3)" in n for n in result.notes)
    assert any("declares no tile_safe" in n for n in result.notes)
    assert "type_name" in result.params


def test_a_composite_routine_says_its_hand_off_is_not_checked():
    result = sr.resolve(_spec(_analytic("sum_type_counts")))
    assert any("runs fetch pyegeria.view.overview_metrics.counts_by_type then analytic" in n for n in result.notes)


def test_target_type_name_is_read_with_target_type_as_its_alias():
    assert sr.resolve(_spec(_analytic())).target_type_name == "Referenceable"
    assert sr.resolve({"heading": "h", "description": "d", "formats": [], "target_type_name": "Asset",
                       "action": {"analytic_function": "count_elements"}}).target_type_name == "Asset"


def test_formatset_accepts_target_type_name():
    fs = FormatSet(heading="h", description="d", formats=[], target_type_name="Asset")
    assert fs.target_type == fs.target_type_name == "Asset"
    with pytest.raises(ValueError, match="disagree"):
        FormatSet(heading="h", description="d", formats=[], target_type_name="Asset", target_type="Glossary")


# ── Listing, caching, load hooks ──

def test_list_report_specs_is_unchanged_by_default_and_gains_status_on_request():
    names = brf.list_report_specs()
    assert names and all(isinstance(n, str) for n in names)
    status = {d["name"]: d for d in brf.list_report_specs(with_status=True)}
    assert set(status) == set(names)
    assert status["Data-Classes"]["runnable"] is False
    assert "check 1" in status["Data-Classes"]["unrunnable_reason"]
    assert status["Analytic Demo - Element Count by Type"] == {
        "name": "Analytic Demo - Element Count by Type", "runnable": True, "unrunnable_reason": ""}


def test_results_are_cached_and_a_registry_change_invalidates():
    first = sr.resolve_all()
    assert sr.resolve_all()["Data-Classes"] is first["Data-Classes"]
    brf.register_report_specs({"Probe-Spec": _spec(_analytic("not_yet_registered"))}, source="test")
    assert not sr.resolve_all()["Probe-Spec"].runnable
    register_analytic_functions({"not_yet_registered": AnalyticFunctionSpec(
        name="not_yet_registered", function="pyegeria.view.overview_metrics.count_elements")})
    assert sr.resolve_all()["Probe-Spec"].runnable
    brf.unregister_report_spec("Probe-Spec")
    assert "Probe-Spec" not in sr.resolve_all()


def test_the_resolver_never_raises_on_a_spec():
    brf.register_report_specs({"Probe-Broken": _spec(_analytic())}, source="test")
    real = sr.resolve

    def boom(spec, name=None, **kw):
        if name == "Probe-Broken":
            raise RuntimeError("bad spec")
        return real(spec, name, **kw)

    sr.resolve = boom
    try:
        result = sr.resolve_all(refresh=True)["Probe-Broken"]
    finally:
        sr.resolve = real
    assert result.kind == "unknown" and "could not be resolved: RuntimeError: bad spec" in result.unrunnable_reason


def _captured(fn) -> str:
    lines = []
    logger.enable("pyegeria")
    sink = logger.add(lambda m: lines.append(str(m)), level="INFO", format="{message}")
    try:
        fn()
    finally:
        logger.remove(sink)
        logger.disable("pyegeria")
    return "".join(lines)


def test_refresh_report_specs_logs_the_unrunnable_count_and_words():
    brf.get_report_registry()  # startup has happened
    text = _captured(brf.refresh_report_specs)
    assert "Report specs resolved at refresh_report_specs: 2 of" in text
    assert "Spec 'Data-Classes' cannot run (check 1)" in text


def test_the_summary_is_logged_once_unless_forced():
    sr.log_resolution_summary()
    assert _captured(sr.log_resolution_summary) == ""
    assert "cannot run" in _captured(lambda: sr.log_resolution_summary(force=True, where="test"))
