# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""F7 (read-back 2026-11-13): preview of a draft spec through the REAL executor leaves nothing behind.

test_authoring_api.py's preview test fakes `exec_report_spec`, so it proves only that preview.py itself
registers nothing. Here the executor is pyegeria's own (`exec_report_spec` -> `_exec_report_spec_impl` ->
`_run_analytic_function`), run on the one-spec dict preview builds. The only stand-in is the routine itself: a
registered analytic function in an injected module that declares no Egeria client, so the run needs no
server (ISSUE-137: no client declared, no connection made), and EgeriaTech is replaced by one that fails the
test if anything builds a client.
"""
import asyncio
import copy
import sys
import types

import pytest

from pyegeria.authoring import SpecDraft
from pyegeria.authoring.preview import async_preview
from pyegeria.view import format_set_executor as fse
from pyegeria.view._output_format_models import FormatSet
from pyegeria.view.analytic_registry import clear_runtime_analytic_functions, register_analytic_functions

pytestmark = pytest.mark.unit

MOD = "tests_f7_preview_routines"
CALLS = []


def team_rows(team: str = "all", page_size=None, **kw):
    CALLS.append({"team": team, "page_size": page_size})
    return [{"name": f"{team}-{i}"} for i in range(40)]


class _NothingHeld:
    async def _async_get_elements_by_property_value(self, *a, **k):
        return "No elements found"


class _Viewer:
    user_id = "erinoverview"
    user_pwd = None
    token = "erin-token"
    server_name = "qs-view-server"
    platform_url = "https://localhost:9443"
    classification_manager = _NothingHeld()


@pytest.fixture(autouse=True)
def routine(monkeypatch):
    mod = types.ModuleType(MOD)
    mod.team_rows = team_rows
    monkeypatch.setitem(sys.modules, MOD, mod)
    monkeypatch.setenv("PYEGERIA_ANALYTIC_MODULE_PREFIXES", f"pyegeria,{MOD}")   # ISSUE-169

    def no_egeria(*a, **k):
        raise AssertionError("preview built an Egeria client for a routine that declares none")
    monkeypatch.setattr(fse, "EgeriaTech", no_egeria)
    clear_runtime_analytic_functions()
    register_analytic_functions({"f7-team-rows": {"name": "f7-team-rows", "function": f"{MOD}.team_rows"}})
    CALLS.clear()
    yield
    clear_runtime_analytic_functions()


def _state():
    from pyegeria.view import egeria_spec_cache
    from pyegeria.view.base_report_formats import get_report_registry
    reg = get_report_registry()
    return (sorted(reg.keys()), {k: id(v) for k, v in reg.items()}, dict(egeria_spec_cache._FETCHED),
            copy.deepcopy(dict(getattr(egeria_spec_cache, "_TIER", {}) or {})))


def _draft() -> SpecDraft:
    return SpecDraft(label="F7 Draft Team Rows", format_set=FormatSet.model_validate({
        "heading": "Team rows", "description": "a draft no one has registered",
        "formats": [{"types": ["DICT"], "attributes": [{"name": "Name", "key": "name"}]}],
        "action": {"analytic_function": "f7-team-rows", "analytic_spec_params": {"team": "blue"}}}))


def test_preview_through_the_real_executor_registers_and_fetches_nothing():
    from pyegeria.view.base_report_formats import lookup_report_spec
    before = _state()
    out = asyncio.run(async_preview(_draft(), client=_Viewer(), max_rows=5))
    assert _state() == before                                  # registry, fetched map, tier map untouched
    assert lookup_report_spec("F7 Draft Team Rows")[0] is None  # the draft was never registered
    assert CALLS == [{"team": "blue", "page_size": 5}]          # the real executor ran the routine once
    assert out["kind"] == "spec" and out["viewer"] == "erinoverview"
    # the routine's 40 rows, capped by preview to 5, and said
    assert out["result"] == {"kind": "json", "data": [{"name": f"blue-{i}"} for i in range(5)]}
    assert out["capped"] is True and out["shown"] == 5 and "capped: 5 of 40 rows shown" in out["notes"]


def test_preview_twice_leaves_the_same_state():
    before = _state()
    asyncio.run(async_preview(_draft(), client=_Viewer(), max_rows=5))
    asyncio.run(async_preview(_draft(), client=_Viewer(), max_rows=3))
    assert _state() == before and [c["page_size"] for c in CALLS] == [5, 3]
