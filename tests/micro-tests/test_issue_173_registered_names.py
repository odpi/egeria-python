"""ISSUE-173: report specs name analytic functions by registered name. A dotted path
still resolves this release, with a DeprecationWarning and a log line naming what
to use instead; pyegeria's own specs use names only."""
import warnings

import pytest

import pyegeria.view.format_set_executor as fse
from pyegeria.view import overview_metrics
from pyegeria.view.analytic_demo_specs import get_analytic_demo_specs
from pyegeria.view.analytic_registry import clear_runtime_analytic_functions, get_analytic_registry
from pyegeria.view.base_report_formats import base_report_specs


@pytest.fixture(autouse=True)
def _clean(monkeypatch):
    monkeypatch.delenv("PYEGERIA_ANALYTIC_MODULE_PREFIXES", raising=False)
    monkeypatch.setattr(fse, "_DOTTED_PATH_WARNED", set())
    clear_runtime_analytic_functions()
    yield
    clear_runtime_analytic_functions()


@pytest.fixture
def log_lines():
    from loguru import logger
    lines = []
    sink = logger.add(lambda m: lines.append(m.record), level="WARNING")
    yield lines
    logger.remove(sink)


def test_registered_name_resolves_without_warning(log_lines):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert fse.resolve_report_spec_function("governed_coverage") is overview_metrics.governed_coverage
    assert log_lines == []


def test_registered_dotted_path_warns_and_names_the_registered_name(log_lines):
    path = "pyegeria.view.overview_metrics.governed_coverage"
    with pytest.warns(DeprecationWarning, match="use the registered name 'governed_coverage'"):
        assert fse.resolve_report_spec_function(path) is overview_metrics.governed_coverage
    with pytest.warns(DeprecationWarning):
        fse.resolve_report_spec_function(path)
    mine = [r for r in log_lines if path in r["message"]]
    assert len(mine) == 1 and mine[0]["level"].name == "WARNING"  # logged once, warned every time


def test_unregistered_dotted_path_warns_to_register_it():
    with pytest.warns(DeprecationWarning, match="'pyegeria.analytics' entry-point group"):
        fse.resolve_report_spec_function("pyegeria.core.utils.body_slimmer")


def test_refused_path_raises_without_a_deprecation_warning():
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        with pytest.raises(fse.AnalyticFunctionRefused):
            fse.resolve_report_spec_function("os.system")


def test_metric_trend_metric_path_goes_through_the_allowlist():
    with pytest.raises(fse.AnalyticFunctionRefused):
        overview_metrics.metric_trend(None, None, metric_path="os.getcwd", points=2)


def test_metric_trend_accepts_a_registered_name(monkeypatch):
    calls = []
    monkeypatch.setattr(overview_metrics, "governed_coverage", lambda mgr, as_of=None: calls.append(as_of) or {"n": 1})
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        series = overview_metrics.metric_trend("mgr", "ce", metric_path="governed_coverage", points=2)
    assert len(series) == 2 and len(calls) == 2


def _pyegeria_spec_functions():
    specs = {**base_report_specs, **get_analytic_demo_specs()}
    for label, fs in specs.items():
        action = fs.action
        if action is not None and action.analytic_function:
            yield label, action.analytic_function, action.analytic_spec_params or {}


def test_pyegeria_specs_name_registered_functions_only():
    registry = get_analytic_registry()
    found = list(_pyegeria_spec_functions())
    assert found, "expected pyegeria to ship analytic report specs"
    for label, name, params in found:
        assert name in registry, f"{label} names {name!r}, not a registered name"
        if "metric_path" in params:
            assert params["metric_path"] in registry, f"{label} metric_path {params['metric_path']!r}"
