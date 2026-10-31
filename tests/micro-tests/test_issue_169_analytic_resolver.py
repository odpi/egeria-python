"""ISSUE-169: a report spec's analytic_function may only name a registered function
or a dotted path under an allowed module prefix; anything else is refused before import."""
import sys

import pytest

import pyegeria.view.format_set_executor as fse
from pyegeria.core.utils import body_slimmer
from pyegeria.view import overview_metrics
from pyegeria.view.analytic_registry import (
    AnalyticFunctionSpec,
    clear_runtime_analytic_functions,
    register_analytic_functions,
)


@pytest.fixture(autouse=True)
def _clean(monkeypatch):
    monkeypatch.delenv("PYEGERIA_ANALYTIC_MODULE_PREFIXES", raising=False)
    clear_runtime_analytic_functions()
    yield
    clear_runtime_analytic_functions()


@pytest.fixture
def import_calls(monkeypatch):
    calls = []
    real = fse.importlib.import_module

    def _recording(name, *args, **kwargs):
        calls.append(name)
        return real(name, *args, **kwargs)

    monkeypatch.setattr(fse.importlib, "import_module", _recording)
    return calls


def test_registered_name_resolves_to_its_function():
    register_analytic_functions({"test-169-growth": AnalyticFunctionSpec(
        name="test-169-growth", function="pyegeria.view.overview_metrics.growth_series")})
    assert fse._resolve_analytic_function("test-169-growth") is overview_metrics.growth_series


def test_registered_function_outside_allowlist_is_trusted(monkeypatch):
    monkeypatch.setenv("PYEGERIA_ANALYTIC_MODULE_PREFIXES", "nothing_matches")
    register_analytic_functions({"test-169-json": AnalyticFunctionSpec(name="test-169-json", function="json.dumps")})
    import json
    assert fse._resolve_analytic_function("test-169-json") is json.dumps
    assert fse._resolve_analytic_function("json.dumps") is json.dumps


def test_allowed_dotted_path_resolves_and_logs_at_debug_only():
    from loguru import logger
    records = []
    sink = logger.add(lambda m: records.append(m.record), level="DEBUG")
    try:
        func = fse._resolve_analytic_function("pyegeria.core.utils.body_slimmer")
    finally:
        logger.remove(sink)
    assert func is body_slimmer
    mine = [r for r in records if "body_slimmer" in r["message"]]
    assert mine and all(r["level"].name == "DEBUG" for r in mine)


def test_prefix_is_a_package_boundary_not_a_string_prefix(import_calls):
    with pytest.raises(fse.AnalyticFunctionRefused):
        fse._resolve_analytic_function("pyegeria_extras.mod.func")
    assert import_calls == []


def test_refused_path_raises_and_never_imports(import_calls):
    sys.modules.pop("test_169_never_imported", None)
    with pytest.raises(fse.AnalyticFunctionRefused, match="not under an allowed prefix"):
        fse._resolve_analytic_function("test_169_never_imported.evil")
    with pytest.raises(fse.AnalyticFunctionRefused):
        fse._resolve_analytic_function("os.system")
    assert import_calls == []
    assert "test_169_never_imported" not in sys.modules


def test_unregistered_bare_name_is_refused(import_calls):
    with pytest.raises(fse.AnalyticFunctionRefused, match="not a registered name"):
        fse._resolve_analytic_function("no-such-function")
    assert import_calls == []


def test_env_var_overrides_the_allowlist(monkeypatch):
    monkeypatch.setenv("PYEGERIA_ANALYTIC_MODULE_PREFIXES", "json, trellis_analytics.")
    import json
    assert fse._resolve_analytic_function("json.dumps") is json.dumps
    with pytest.raises(fse.AnalyticFunctionRefused):
        fse._resolve_analytic_function("pyegeria.core.utils.body_slimmer")


def test_binder_factories_go_through_the_same_check():
    def analytic(ods=None):
        return ods
    with pytest.raises(fse.AnalyticFunctionRefused):
        fse._apply_analytic_binders(analytic, {"ods": "os:getcwd"}, {})
