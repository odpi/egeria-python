"""ISSUE-172: installed packages register analytic functions and steps through the
`pyegeria.analytics` entry-point group, read lazily on first use of the registry,
with a broken entry point reported, not fatal. The `trellis.analytics` alias group
was removed in 6.2.19."""
import sys

import pytest

import pyegeria.view.analytic_registry as reg
from pyegeria.view.analytic_registry import AnalyticFunctionSpec


class FakeEntryPoint:
    def __init__(self, name, value, obj=None, error=None):
        self.name, self.value, self._obj, self._error = name, value, obj, error
        self.loads = 0

    def load(self):
        self.loads += 1
        if self._error:
            raise self._error
        return self._obj


ROUTINE = AnalyticFunctionSpec(name="ep-routine", function="ep_pkg.routines.coverage")
STEP = AnalyticFunctionSpec(name="ep-step", function="ep_pkg.steps.staleness", kind="step")


@pytest.fixture
def installed(monkeypatch):
    """Install fake entry points per group; returns the dict to fill and a call counter."""
    groups = {reg.ANALYTIC_ENTRY_POINT_GROUP: [], "trellis.analytics": []}
    calls = []

    def fake_entry_points(group):
        calls.append(group)
        return list(groups.get(group, []))

    monkeypatch.setattr(reg, "entry_points", fake_entry_points)
    monkeypatch.setattr(reg, "_ENTRY_POINT_ANALYTIC_FUNCTIONS", None)
    monkeypatch.setattr(reg, "_ENTRY_POINT_ERRORS", {})
    reg.clear_runtime_analytic_functions()
    yield groups, calls
    reg.clear_runtime_analytic_functions()


def test_functions_and_steps_are_registered(installed):
    groups, _ = installed
    groups[reg.ANALYTIC_ENTRY_POINT_GROUP].append(FakeEntryPoint("one", "ep_pkg:ROUTINE", ROUTINE))
    groups[reg.ANALYTIC_ENTRY_POINT_GROUP].append(FakeEntryPoint("two", "ep_pkg:steps", lambda: [STEP]))
    registry = reg.get_analytic_registry()
    assert registry["ep-routine"].function == "ep_pkg.routines.coverage"
    assert registry["ep-step"].kind == "step"
    assert reg.analytic_entry_point_errors() == {}


def test_discovery_is_lazy_and_read_once(installed):
    groups, calls = installed
    ep = FakeEntryPoint("one", "ep_pkg:ROUTINE", ROUTINE)
    groups[reg.ANALYTIC_ENTRY_POINT_GROUP].append(ep)
    assert calls == []  # nothing read until the registry is used
    reg.get_analytic_registry()
    reg.get_analytic_registry()
    assert ep.loads == 1
    reg.refresh_analytic_functions()
    reg.get_analytic_registry()
    assert ep.loads == 2  # refresh re-reads installed packages


def test_function_module_is_not_imported_by_discovery(installed):
    groups, _ = installed
    groups[reg.ANALYTIC_ENTRY_POINT_GROUP].append(FakeEntryPoint("one", "ep_pkg:ROUTINE", ROUTINE))
    reg.get_analytic_registry()
    assert "ep_pkg.routines" not in sys.modules


def test_broken_entry_point_is_reported_and_the_rest_still_load(installed):
    groups, _ = installed
    groups[reg.ANALYTIC_ENTRY_POINT_GROUP] += [
        FakeEntryPoint("broken", "bad_pkg:manifest", error=ModuleNotFoundError("No module named 'xxhash'")),
        FakeEntryPoint("one", "ep_pkg:ROUTINE", ROUTINE),
    ]
    assert "ep-routine" in reg.get_analytic_registry()
    errors = reg.analytic_entry_point_errors()
    assert list(errors) == [f"{reg.ANALYTIC_ENTRY_POINT_GROUP}:broken"]
    assert "No module named 'xxhash'" in errors[f"{reg.ANALYTIC_ENTRY_POINT_GROUP}:broken"]
    assert reg.analytic_registry_payload()["entry_point_errors"] == errors


def test_an_entry_point_naming_something_else_is_an_error(installed):
    groups, _ = installed
    groups[reg.ANALYTIC_ENTRY_POINT_GROUP].append(FakeEntryPoint("odd", "ep_pkg:thing", {"name": "x"}))
    reg.get_analytic_registry()
    assert "is not an AnalyticFunctionSpec" in reg.analytic_entry_point_errors()[
        f"{reg.ANALYTIC_ENTRY_POINT_GROUP}:odd"]


def test_installed_name_clashing_with_a_builtin_is_skipped_not_fatal(installed):
    groups, _ = installed
    builtin = next(iter(reg._BUILTINS))
    clash = AnalyticFunctionSpec(name=builtin, function="ep_pkg.other.func")
    groups[reg.ANALYTIC_ENTRY_POINT_GROUP].append(FakeEntryPoint("clash", "ep_pkg:clash", clash))
    registry = reg.get_analytic_registry()
    assert registry[builtin].function == reg._BUILTINS[builtin].function
    assert any("was skipped" in e for e in reg.analytic_entry_point_errors().values())


def test_trellis_alias_group_is_no_longer_read(installed):
    groups, calls = installed
    groups["trellis.analytics"].append(FakeEntryPoint("one", "ep_pkg:ROUTINE", ROUTINE))
    assert "ep-routine" not in reg.get_analytic_registry()
    assert calls == [reg.ANALYTIC_ENTRY_POINT_GROUP]


def test_runtime_register_skipping_existing_names_still_works(installed):
    """trellis-analytics' register() checks get_analytic_registry() and skips names present."""
    groups, _ = installed
    groups[reg.ANALYTIC_ENTRY_POINT_GROUP].append(FakeEntryPoint("one", "ep_pkg:ROUTINE", ROUTINE))
    existing = set(reg.get_analytic_registry())
    new = {n: m for n, m in {"ep-routine": ROUTINE}.items() if n not in existing}
    assert new == {}
