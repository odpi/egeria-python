# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""pyegeria.authoring, phase 1 (BRIEF-PYEGERIA-AUTHORING-API-PHASE1-2026-11-13 §7). Offline: fake clients and
runners stand in for Egeria.

Real shapes:
- the Stage 1a golden (EA's own publish documents, tests/micro-tests/data/report_spec_publish);
- the CDO Report's stored map on laz (CocoPharma::Report::CDODashboard::MyNinetyDayPlanProgress, 2026-11-12);
- pyegeria's built-in specs (Project-DrE-Basic, the Analytic Demo specs the catalog-health sheet runs).
"""
import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

from pyegeria.authoring import (
    AuthoringGates, AuthoringRefused, ReportDraft, SheetDraft, SheetPlacement, SpecDraft, apply, diff, has_parent_id,
    new_draft, new_from, publish_plan, report_parameter_maps, serialize, validate, withdraw_plan,
)
from pyegeria.authoring import mcp_tools
from pyegeria.authoring.drafts import EgeriaDraftStore, LocalDraftStore
from pyegeria.authoring.preview import async_preview
from pyegeria.authoring.serialize import parsed_commands
from pyegeria.view import report_spec_publish as rsp
from pyegeria.view._output_format_models import FormatSet

pytestmark = pytest.mark.unit

GOLD = json.loads((Path(__file__).parent / "data" / "report_spec_publish" / "ea_goldens_2026_11_12.json").read_text())

# The CDO Report's stored additionalProperties on laz, 2026-11-12 (version 1).
CDO_STORED = {"reportSpec": "Project-DrE-Basic", "searchString": "JulesKeeper::", "graphQueryDepth": "1",
              "startFrom": "0", "ignoreCase": "False", "endsWith": "False", "pageSize": "0",
              "limitResultByStatus": "['ACTIVE']", "outputFormat": "LIST", "startsWith": "True"}
CDO_QN = "CocoPharma::Report::CDODashboard::MyNinetyDayPlanProgress"


def cdo_report(**over) -> ReportDraft:
    fields = dict(display_name="My Ninety Day Plan Progress", qualified_name=CDO_QN, spec="Project-DrE-Basic",
                  output_format="LIST",
                  parameters={"search_string": "JulesKeeper::", "graph_query_depth": 1, "start_from": 0,
                              "ignore_case": False, "ends_with": False, "page_size": 0,
                              "limit_result_by_status": ["ACTIVE"], "starts_with": True})
    fields.update(over)
    return ReportDraft(**fields)


def catalog_health_sheet() -> SheetDraft:
    return SheetDraft(name="catalog-health", heading="Catalog Health", family="Overview",
                      description="How complete and how current the catalog is.", placements=[
                          SheetPlacement(text="**What these tiles measure**\n\nThe readiness funnel counts assets.",
                                         name="What these tiles measure", span="full", emphasis="panel"),
                          SheetPlacement(report="Catalog Health - AI Context Readiness", span="2", emphasis="panel"),
                          SheetPlacement(report="Catalog Health - Asset Ownership", perspectives=["governance"]),
                      ])



# ── D14: every publish plan has its target resolved first ────────────────────

NEW = {"resolved": True, "held": False, "guid": None, "qualified_name": None, "zones": [],
       "published_version": None, "published_versions": [], "edited_since": False, "notes": []}


def _publish(draft, *, held=None, **kw):
    """publish_plan with a resolved target: not held, unless `held` says otherwise (zones, a version)."""
    target = {**NEW, **({"held": True, "guid": "g-held"} if (held or {}).get("held") else {}), **(held or {})}
    return publish_plan(draft, held=target, published_by="erinoverview", **kw)


def _unstamped(markdown):
    """The document less its publication stamp row (the Stage 1a golden has none)."""
    import re as _re
    return _re.sub(r"### Additional Properties\npublishedAt: [^\n]*\npublishedBy: [^\n]*\npublishedVersion: \d+\n",
                   "", markdown)

def _gold_fs(case) -> FormatSet:
    d = json.loads(json.dumps(GOLD["specs"][case["spec"]]))
    if case.get("alias"):
        d["aliases"] = case["alias"]
    return FormatSet.model_validate(d)


# ── Golden: the spec document is Stage 1a's, byte for byte ───────────────────

PUBLIC = [c for c in GOLD["publish"] if c["kw"].get("visibility", "public") == "public"]


@pytest.mark.parametrize("case", PUBLIC, ids=[c["id"] for c in PUBLIC])
def test_spec_publish_plan_is_byte_identical_to_the_stage_1a_golden(case, monkeypatch):
    monkeypatch.setattr("pyegeria.authoring.lifecycle._is_builtin", lambda label: False)
    kw = dict(case["kw"])
    folders = [rsp.ADVISOR_FOLDER] + ([rsp.PORTAL_FOLDER] if kw.pop("also_portal", False) else [])
    plan = _publish(SpecDraft(label=case["label"], format_set=_gold_fs(case)), folders=folders,
                        held=kw.get("held"))
    # D14: the same document, plus the publication stamp in the spec's own block
    assert _unstamped(plan["markdown"]) == case["expect"]["markdown"]
    assert "### Additional Properties\npublishedAt: (set when published)\npublishedBy: erinoverview\npublishedVersion: 1" \
        in plan["markdown"]
    # serialize writes the same Create/Update Report Spec block
    block = serialize(SpecDraft(label=case["label"], format_set=_gold_fs(case))).split("\n", 2)[2]
    if not (kw.get("held") or {}).get("held"):
        assert block in case["expect"]["markdown"]


def test_restricted_publish_is_refused_in_words():
    draft = SpecDraft(label="Team Projects", format_set=_gold_fs({"spec": "simple"}))
    with pytest.raises(AuthoringRefused, match="Restricted publish comes later, after the zone proof"):
        _publish(draft, folders=[rsp.ADVISOR_FOLDER], visibility="restricted")


# ── The CDO Report: every parameter explicit, every key reproduced ───────────

def _equivalent_status(a: str, b: str) -> bool:
    from pyegeria.view.format_set_executor import _normalize_report_params
    norm = lambda v: _normalize_report_params({"limit_result_by_status": v})["limit_results_by_status"]  # noqa: E731
    return norm(a) == norm(b)


def test_cdo_report_round_trip_reproduces_all_ten_keys_and_typed_parameters():
    draft = cdo_report()
    maps = report_parameter_maps(draft)
    camel = maps["additionalProperties"]
    assert set(camel) == set(CDO_STORED)
    for key, stored in CDO_STORED.items():
        if key == "limitResultByStatus":   # written as JSON; the executor reads both forms as ["ACTIVE"]
            assert _equivalent_status(camel[key], stored)
        else:
            assert camel[key] == stored, key
    assert maps["reportParameters"] == {"search_string": "JulesKeeper::", "graph_query_depth": 1, "start_from": 0,
                                        "ignore_case": False, "ends_with": False, "page_size": 0,
                                        "limit_result_by_status": ["ACTIVE"], "starts_with": True}


def test_every_parameter_is_written_out():
    md = serialize(cdo_report())
    for attribute in ("Search String", "Graph Query Depth", "Start From", "Ignore Case", "Ends With", "Page Size",
                      "Limit Result by Status", "Starts With"):
        assert f"### {attribute}\n" in md


def test_d7_switch_drops_the_camel_copy_only():
    maps = report_parameter_maps(cdo_report(), camel_copy=False)
    assert maps["additionalProperties"] == {} and maps["reportParameters"]["search_string"] == "JulesKeeper::"


def test_processor_honours_the_d7_switch(monkeypatch):
    from md_processing.v2.report import _report_additional_properties
    attrs = dict(parsed_commands(serialize(cdo_report()))[0][1])
    monkeypatch.setenv("PYEGERIA_REPORT_CAMEL_PARAMS", "0")
    assert _report_additional_properties(attrs) == {}
    monkeypatch.setenv("PYEGERIA_REPORT_CAMEL_PARAMS", "1")
    assert _report_additional_properties(attrs)["searchString"] == "JulesKeeper::"


# ── Never a Parent ID ─────────────────────────────────────────────────────────

def test_no_serializer_output_names_a_parent_id(monkeypatch):
    monkeypatch.setattr("pyegeria.authoring.lifecycle._is_builtin", lambda label: False)
    spec = SpecDraft(label="Team Projects", format_set=_gold_fs({"spec": "rich"}))
    docs = [serialize(spec), serialize(cdo_report()), serialize(catalog_health_sheet()),
            _publish(spec, folders=[rsp.ADVISOR_FOLDER])["markdown"],
            _publish(cdo_report())["markdown"],
            _publish(catalog_health_sheet(), folders=["DashboardFolder::Consumer::Portal"])["markdown"],
            withdraw_plan("sheet", "catalog-health", folders=["DashboardFolder::Consumer::Portal"])["markdown"],
            withdraw_plan("spec", "Team Projects", folders=[rsp.ADVISOR_FOLDER])["markdown"]]
    for md in docs:
        assert not has_parent_id(md)
        assert "parent id" not in md.lower()


# ── The sheet document parses back to its placements ─────────────────────────

def test_sheet_document_parses_back_to_the_same_placements():
    sheet = catalog_health_sheet()
    parsed = parsed_commands(serialize(sheet))
    assert [c for c, _ in parsed] == ["Create Dashboard Sheet", "Add Text on Dashboard Sheet",
                                      "Link Report to Dashboard Sheet", "Link Report to Dashboard Sheet"]
    assert parsed[0][1]["Dashboard Sheet Heading"]["value"] == "Catalog Health"
    text = parsed[1][1]
    assert text["Placement Name"]["value"] == "What these tiles measure"
    assert "readiness funnel" in text["MD Content"]["value"]
    assert parsed[2][1]["Report Name"]["value"] == "Catalog Health - AI Context Readiness"
    assert parsed[2][1]["Placement Span"]["value"] == "2"
    assert parsed[3][1]["Placement Perspectives"]["value"] == ["governance"]


def test_text_that_would_start_a_block_is_refused():
    bad = SheetDraft(name="s", heading="S", placements=[SheetPlacement(text="## Create Glossary", name="t")])
    with pytest.raises(AuthoringRefused, match="would start a new Dr.Egeria block"):
        serialize(bad)


# ── validate ─────────────────────────────────────────────────────────────────

def _spec(**over) -> SpecDraft:
    fs = {"target_type": "Project", "heading": "Projects", "description": "d",
          "formats": [{"types": ["TABLE"], "attributes": [{"name": "Name", "key": "display_name"}]}],
          "action": {"function": "ProjectManager.find_projects", "required_params": ["search_string"]}}
    fs.update(over)
    return SpecDraft(label="Draft Projects", format_set=FormatSet.model_validate(fs))


def test_validate_passes_a_good_spec():
    result = validate(_spec())
    assert result.ok, result.errors
    assert "Dr.Egeria validate: no runner given" in result.not_checked


def test_validate_catches_a_nonexistent_column_attribute():
    result = validate(_spec(formats=[{"types": ["TABLE"], "attributes": [{"name": "Colour", "key": "favourite_colour"}]}]))
    assert not result.ok
    assert any("favourite_colour" in e and "isn't an attribute of Project" in e for e in result.errors)


def test_validate_catches_an_unknown_target_type():
    result = validate(_spec(target_type="NoSuchEgeriaType"))
    assert any("NoSuchEgeriaType" in e for e in result.errors)


def test_validate_catches_an_unknown_routine():
    result = validate(_spec(target_type=None, action={"analytic_function": "no_such_routine"},
                            formats=[{"types": ["DICT"], "attributes": []}]))
    assert not result.ok
    assert any("no_such_routine" in e for e in result.errors)


def test_validate_catches_a_mistyped_parameter():
    result = validate(cdo_report(parameters={"search_string": "x", "page_size": "lots"}))
    assert any("page_size" in e and "should be int" in e for e in result.errors)
    result = validate(ReportDraft(display_name="Stale", spec="Analytic Demo - Stale Assets", output_format="DICT",
                                  analytic_params={"days": "a while"}))
    assert any("days" in e and "should be int" in e for e in result.errors)


def test_validate_catches_an_undeclared_parameter():
    result = validate(cdo_report(parameters={"collection_guid": "c-1"}))
    assert any("'collection_guid' isn't a parameter" in e for e in result.errors)


def test_a_pinned_version_without_a_client_is_said_not_checked():
    result = validate(cdo_report(pinned_version=3))
    assert result.ok
    assert any("pinned version 3" in n and "no client" in n for n in result.not_checked)
    assert "### Additional Properties\nreportSpecVersion: 3" in serialize(cdo_report(pinned_version=3))
    assert any("D14" in e for e in validate(cdo_report(pinned_version=3), gates=AuthoringGates(allow_pinning=False)).errors)


class _NoReports:
    """A client whose Egeria holds no Report (and nothing else)."""
    user_id = "erinoverview"

    class _CM:
        async def _async_get_element_by_unique_name(self, qn):
            return "No elements found"

        async def _async_get_elements_by_property_value(self, *a, **k):
            return "No elements found"

    classification_manager = _CM()


def test_validate_catches_an_unresolvable_placement():
    result = validate(catalog_health_sheet(), _NoReports())
    assert not result.ok
    assert sum("doesn't resolve" in e for e in result.errors) == 2


def test_validate_without_a_client_says_what_it_did_not_check():
    result = validate(catalog_health_sheet())
    assert result.ok
    assert sum("no client" in n for n in result.not_checked) == 2


def test_validate_runs_dr_egeria_through_the_runner():
    calls = []

    def run(md, directive):
        calls.append(directive)
        return {"success": False, "validation_errors": [{"message": "Report Spec is required"}]}
    result = validate(cdo_report(), run=run)
    assert calls == ["validate"]
    assert "Dr.Egeria: Report Spec is required" in result.errors


def test_validate_never_raises_for_a_bad_draft():
    result = validate({"kind": "report", "display_name": "x"})
    assert not result.ok and any("spec" in e for e in result.errors)


# ── preview: as the caller, capped, no global side effect ────────────────────

class _NothingHeld:
    """classification-explorer answering "No elements found" (a publish target that isn't held yet)."""
    async def _async_get_elements_by_property_value(self, *a, **k):
        return "No elements found"


class _Viewer:
    user_id = "erinoverview"
    user_pwd = None
    token = "erin-token"
    server_name = "qs-view-server"
    platform_url = "https://localhost:9443"
    classification_manager = _NothingHeld()


def _state():
    from pyegeria.view import egeria_spec_cache
    from pyegeria.view.base_report_formats import get_report_registry
    reg = get_report_registry()
    return (sorted(reg.keys()), {k: id(v) for k, v in reg.items()}, dict(egeria_spec_cache._FETCHED),
            dict(getattr(egeria_spec_cache, "_TIER", {}) or {}))


def test_preview_runs_as_the_caller_caps_and_leaves_the_registry_alone(monkeypatch):
    seen: Dict[str, Any] = {}

    def fake_exec(spec, **kw):
        seen.update(spec=spec, **kw)
        return {"kind": "table", "columns": [{"key": "display_name"}],
                "rows": [{"display_name": f"P{i}"} for i in range(kw["params"]["page_size"])]}
    monkeypatch.setattr("pyegeria.view.format_set_executor.exec_report_spec", fake_exec)
    before = _state()
    out = asyncio.run(async_preview(_spec(), client=_Viewer(), max_rows=5))
    assert _state() == before
    assert isinstance(seen["spec"], dict) and seen["spec"]["_report_spec_name"] == "Draft Projects"
    assert seen["token"] == "erin-token" and seen["user"] == "erinoverview" and seen["table_shape"] == "structured"
    assert out["capped"] is True and out["shown"] == 5
    assert any("there may be more" in n for n in out["notes"])
    from pyegeria.view.base_report_formats import lookup_report_spec
    assert lookup_report_spec("Draft Projects")[0] is None


def test_preview_says_nothing_found():
    async def go(monkeypatch=None):
        return None
    import pyegeria.view.format_set_executor as fse
    orig = fse.exec_report_spec
    fse.exec_report_spec = lambda spec, **kw: {"kind": "table", "columns": [], "rows": []}
    try:
        out = asyncio.run(async_preview(_spec(), client=_Viewer()))
    finally:
        fse.exec_report_spec = orig
    assert out["capped"] is False and out["shown"] == 0 and "ran, and found nothing" in out["notes"]


def test_preview_needs_a_client():
    with pytest.raises(AuthoringRefused, match="signed in as you"):
        asyncio.run(async_preview(_spec(), client=None))


# ── diff ──────────────────────────────────────────────────────────────────────

def test_diff_flags_each_breaking_kind():
    a = _spec(formats=[{"types": ["TABLE"], "attributes": [{"name": "Name", "key": "display_name"},
                                                           {"name": "Status", "key": "project_status"}]}])
    b = _spec(target_type="Collection")
    d = diff(a, b)
    broken = {(c.area, c.name) for c in d.breaking}
    assert ("column", "project_status") in broken and ("field", "target_type") in broken

    d = diff(cdo_report(), cdo_report(parameters={**cdo_report().parameters, "page_size": "0"}))
    assert [(c.name, c.breaking) for c in d.changes] == [("page_size", True)]

    s1 = catalog_health_sheet()
    s2 = SheetDraft(**{**s1.model_dump(), "placements": [p.model_dump() for p in s1.placements[:2]]})
    d = diff(s1, s2)
    assert [(c.area, c.name, c.change) for c in d.breaking] == [("placement", "Catalog Health - Asset Ownership",
                                                                 "removed")]


def test_a_pin_is_said_not_to_reach_dashboards_yet():
    """F3 (read-back 2026-11-13): nothing that runs a placed Report reads reportSpecVersion yet."""
    pinned = cdo_report(pinned_version=3)
    assert any("dashboards don't read it yet" in n for n in validate(pinned).not_applied)
    steps = _publish(pinned)["steps"]
    assert any("pinned at published version 3" in s for s in steps)
    assert any("runs the spec's latest version" in s for s in steps)
    assert not any("dashboards don't read" in s for s in _publish(cdo_report())["steps"])


def test_sheet_update_limits_are_said_in_the_plan_and_the_diff():
    """F4: publishing adds and updates placements; it doesn't remove or reorder them on an existing sheet."""
    s1 = catalog_health_sheet()
    steps = _publish(s1, folders=["DashboardFolder::Consumer::Portal"])["steps"]
    assert any("a placement no longer in this draft stays on the sheet" in s for s in steps)
    fewer = SheetDraft(**{**s1.model_dump(), "placements": [p.model_dump() for p in s1.placements[:2]]})
    removed, = [c for c in diff(s1, fewer).changes if c.change == "removed"]
    assert "doesn't remove it" in removed.why
    swapped = SheetDraft(**{**s1.model_dump(),
                            "placements": [p.model_dump() for p in reversed(s1.placements)]})
    order, = [c for c in diff(s1, swapped).changes if c.name == "(order)"]
    assert "doesn't reorder" in order.why and not order.breaking


def test_diff_added_things_are_not_breaking():
    d = diff(cdo_report(parameters={}), cdo_report())
    assert d.changes and not d.breaking


# ── drafts, new_from, the D16 store ──────────────────────────────────────────

def test_new_from_a_builtin_prototype_records_where_it_came_from():
    d = new_from(prototype=("spec", "Project-DrE-Basic"), new_label="My Projects")
    assert d.label == "My Projects" and d.derived_from == "prototype:spec:Project-DrE-Basic"
    assert d.format_set.aliases == []
    from pyegeria.view.base_report_formats import lookup_report_spec
    assert lookup_report_spec("My Projects")[0] is None


def test_new_from_a_template():
    d = new_from(template="report", new_label="Blank")
    assert d.kind == "report" and d.derived_from == "template:report"


def test_built_in_specs_are_not_published():
    d = SpecDraft(label="Project-DrE-Basic", format_set=new_from(prototype=("spec", "Project-DrE-Basic"),
                                                                 new_label="x").format_set)
    with pytest.raises(AuthoringRefused, match="built-in spec"):
        _publish(d, folders=[rsp.PORTAL_FOLDER])


def test_unknown_folders_are_refused():
    with pytest.raises(AuthoringRefused, match="Unknown consumer folder"):
        _publish(catalog_health_sheet(), folders=["DashboardFolder::Consumer::Nowhere"])


def test_local_store_keeps_drafts_per_user(tmp_path):
    store = LocalDraftStore(tmp_path)
    store.save("erinoverview", cdo_report())
    assert store.load("erinoverview", "report", "My Ninety Day Plan Progress") == cdo_report()
    assert store.load("garygeeke", "report", "My Ninety Day Plan Progress") is None
    assert store.list("erinoverview") == [{"kind": "report", "name": "My Ninety Day Plan Progress"}]
    with pytest.raises(AuthoringRefused):
        store.save("../garygeeke", cdo_report())


def test_a_user_id_that_names_a_controlled_zone_is_refused():
    eg = _DraftEgeria(user="public")
    with pytest.raises(AuthoringRefused, match="name of a controlled zone"):
        EgeriaDraftStore(eg, eg.run, controlled_zones=["public"]).save("public", cdo_report())
    eg = _DraftEgeria(user="governance")
    eg.governance_zones = ["governance"]
    with pytest.raises(AuthoringRefused, match="name of a governance zone"):
        EgeriaDraftStore(eg, eg.run).save("governance", cdo_report())
    assert eg.ran == []


def test_the_api_never_writes_the_local_sheet_store(tmp_path, monkeypatch):
    store = tmp_path / "dashboard_sheets.json"
    monkeypatch.setenv("PYEGERIA_DASHBOARD_SHEETS_STORE", str(store))
    sheet = catalog_health_sheet()
    serialize(sheet)
    _publish(sheet, folders=["DashboardFolder::Consumer::Portal"])
    validate(sheet)
    assert not store.exists()


# ── apply and the MCP write tool ─────────────────────────────────────────────

def test_apply_refuses_unconfirmed_and_changed_documents():
    plan = _publish(cdo_report())
    ran = []
    run = lambda md, d: ran.append(d) or {"success": True}  # noqa: E731
    with pytest.raises(AuthoringRefused, match="Confirm first"):
        apply(plan, step="process", run=run, client=_Viewer(), digest=plan["digest"])
    with pytest.raises(AuthoringRefused, match="changed since you previewed"):
        apply(plan, step="process", run=run, client=_Viewer(), confirmed=True, digest="0" * 16)
    assert ran == []
    assert apply(plan, step="process", run=run, client=_Viewer(), confirmed=True,
                 digest=plan["digest"])["result"]["success"]


@pytest.fixture
def mcp(tmp_path, monkeypatch):
    monkeypatch.setenv(mcp_tools.DRAFTS_DIR_ENV, str(tmp_path))
    monkeypatch.setattr(mcp_tools, "_service_user", lambda: "svc-account")
    made: List[Any] = []
    monkeypatch.setattr(mcp_tools, "CLIENT_FACTORY", lambda u, t: made.append((u, t)) or _Viewer())
    ran: List[str] = []
    monkeypatch.setattr(mcp_tools, "inprocess_runner",
                        lambda client: (lambda md, d: ran.append(d) or {"success": True}))
    return made, ran


ERIN = {"user_id": "erinoverview", "token": "erin-token"}


def test_mcp_apply_refuses_without_an_as_user_credential(mcp):
    out = mcp_tools.authoring_apply("process", confirmed=True, digest="x", draft=cdo_report().model_dump(),
                                    user_id="erinoverview")
    assert out["ok"] is False and "never authors with its own service credentials" in out["refused"]


def test_mcp_apply_refuses_the_service_account(mcp):
    out = mcp_tools.authoring_apply("process", confirmed=True, digest="x", draft=cdo_report().model_dump(),
                                    as_user={"user_id": "svc-account", "token": "t"})
    assert out["ok"] is False and "service account" in out["refused"]


def test_mcp_apply_refuses_without_confirmed_and_with_a_mismatched_digest(mcp):
    made, ran = mcp
    draft = cdo_report().model_dump()
    out = mcp_tools.authoring_apply("process", digest="x", draft=draft, as_user=ERIN)
    assert out["ok"] is False and "Confirm first" in out["refused"]
    out = mcp_tools.authoring_apply("process", confirmed=True, digest="0" * 16, draft=draft, as_user=ERIN)
    assert out["ok"] is False and "changed since you previewed" in out["refused"]
    assert ran == []
    plan = mcp_tools.authoring_publish_plan(draft=draft, as_user=ERIN)["plan"]
    out = mcp_tools.authoring_apply("process", confirmed=True, digest=plan["digest"], draft=draft, as_user=ERIN)
    assert out["ok"] is True and ran == ["process"] and made[-1] == ("erinoverview", "erin-token")


def test_mcp_read_tools_keep_drafts_per_user(mcp):
    out = mcp_tools.authoring_new_draft("report", cdo_report().model_dump(exclude={"kind"}), user_id="erinoverview")
    assert out["ok"] and "### Search String" in out["markdown"]
    plan = mcp_tools.authoring_publish_plan(kind="report", name="My Ninety Day Plan Progress", user_id="erinoverview")
    assert plan["ok"] is False and "finds the exact element it would write" in plan["refused"]   # D14: as you
    plan = mcp_tools.authoring_publish_plan(kind="report", name="My Ninety Day Plan Progress", as_user=ERIN)
    assert plan["ok"] and plan["plan"]["digest"]
    other = mcp_tools.authoring_publish_plan(kind="report", name="My Ninety Day Plan Progress",
                                             as_user={"user_id": "garygeeke", "token": "gary-token"})
    assert other["ok"] is False and "no saved report draft" in other["refused"]
    v = asyncio.run(mcp_tools.authoring_validate(kind="report", name="My Ninety Day Plan Progress",
                                                 user_id="erinoverview"))
    assert v["ok"] and v["validation"]["ok"], v
    p = asyncio.run(mcp_tools.authoring_preview(kind="report", name="My Ninety Day Plan Progress",
                                                user_id="erinoverview"))
    assert p["ok"] is False and "Preview acts as you" in p["refused"]


def test_mcp_tools_register_on_a_server():
    names = []

    class Srv:
        def tool(self, name):
            names.append(name)
            return lambda fn: fn
    mcp_tools.register(Srv())
    assert names == ["authoring_new_draft", "authoring_new_from", "authoring_validate", "authoring_preview",
                     "authoring_diff", "authoring_history", "authoring_publish_plan", "authoring_apply"]


# ── D7: both parameter forms, always, carrying the same values ───────────────

def _both_forms_agree(draft):
    from pyegeria.authoring.lifecycle import _decode
    from md_processing.v2.report import _snake_to_camel
    maps = report_parameter_maps(draft)
    typed, camel = maps["reportParameters"], maps["additionalProperties"]
    analytic = json.loads(camel.get("analyticParams") or "{}")
    for name, value in typed.items():
        if name in analytic:
            assert analytic[name] == value, name
            continue
        key = _snake_to_camel(name)
        assert key in camel, f"{name} is in reportParameters but not in the camelCase copy"
        if name == "limit_result_by_status":
            assert _equivalent_status(camel[key], json.dumps(value))
        else:
            assert _decode(camel[key]) == value or camel[key] == value, name
    return typed, camel


@pytest.mark.parametrize("draft", [
    cdo_report(), cdo_report(output_format="TABLE"),
    ReportDraft(display_name="Members", spec="Collection Members", output_format="TABLE",
                parameters={"collection_guid": "c-1", "page_size": 25, "search_string": "*"}),
    ReportDraft(display_name="Stale", spec="Analytic Demo - Stale Assets", output_format="DICT",
                analytic_params={"days": 180}),
    ReportDraft(display_name="Growth", spec="Analytic Demo - Catalog Growth Trend", output_format="SERIES",
                analytic_params={"window": "90d", "points": 6}),
], ids=["cdo-list", "cdo-table", "collection-members", "stale", "growth"])
def test_d7_both_forms_are_written_and_agree(draft):
    typed, camel = _both_forms_agree(draft)
    assert camel["reportSpec"] == draft.spec and camel["outputFormat"] == draft.output_format.upper()


# ── D14: pinning, resolved as the user from the spec's own history ───────────

class _SpecHistory:
    """A client holding spec 'Team Projects' at versions 3 (current) and 2, as Egeria returns them."""
    user_id = "erinoverview"
    token = "erin-token"

    def __init__(self):
        from pyegeria.view.microflow import format_set_to_microflow

        def element(version, heading):
            fs = _gold_fs({"spec": "simple"})
            mf = json.loads(format_set_to_microflow(fs).to_json())
            return {"elementHeader": {"guid": "spec-guid", "type": {"typeName": "ReportSpec",
                                                                     "superTypeNames": ["Collection"]},
                                      "versions": {"version": version}},
                    "properties": {"qualifiedName": "ReportSpec::Team Projects", "displayName": "Team Projects",
                                   "description": heading, "targetTypeName": "Project",
                                   "microflow": json.dumps(mf), "contentStatus": "ACTIVE",
                                   "additionalProperties": {"publishedVersion": str(version)}}}
        self.current, self.v2 = element(3, "now"), element(2, "before")
        outer = self

        class CM:
            async def _async_get_element_by_unique_name(self, qn):
                return outer.current if qn == "ReportSpec::Team Projects" else "No elements found"

        class ME:
            async def _async_get_element_history(self, guid, start_from=0, page_size=0, **kw):
                return [outer.current, outer.v2][start_from:start_from + page_size] if page_size else \
                    [outer.current, outer.v2]
        self.classification_manager, self.metadata_expert = CM(), ME()


def test_a_pinned_version_resolves_as_the_user_without_the_fetched_map():
    from pyegeria.authoring.versions import async_spec_at_version
    from pyegeria.view import egeria_spec_cache
    before = dict(egeria_spec_cache._FETCHED)
    fs = asyncio.run(async_spec_at_version(_SpecHistory(), "Team Projects", 2))
    assert fs.description == "before"
    assert dict(egeria_spec_cache._FETCHED) == before
    with pytest.raises(AuthoringRefused, match="has no published version 7; its published versions are 2, 3"):
        asyncio.run(async_spec_at_version(_SpecHistory(), "Team Projects", 7))


def test_validate_checks_the_pinned_version_exists():
    draft = ReportDraft(display_name="Pinned", spec="Team Projects", output_format="TABLE", pinned_version=7,
                        parameters={"search_string": "*"})
    result = validate(draft, _SpecHistory())
    assert any("has no published version 7" in e for e in result.errors)
    ok = validate(draft.model_copy(update={"pinned_version": 2}), _SpecHistory())
    assert ok.ok, ok.errors
    assert "pinned version 2 exists" in ok.checked


def test_a_held_pinned_report_reads_back_its_version():
    from pyegeria.authoring.lifecycle import report_draft_from_element
    el = {"elementHeader": {"guid": "r", "versions": {"version": 1}},
          "properties": {"displayName": "Pinned", "additionalProperties": {**CDO_STORED, "reportSpecVersion": "2"}}}
    draft = report_draft_from_element(el)
    assert draft.pinned_version == 2 and "report_spec_version" not in draft.parameters


# ── D16: drafts in Egeria, private to the author ─────────────────────────────

class _DraftEgeria:
    """A fake Egeria holding elements by qualified name, with zones; records what the runner was given."""
    def __init__(self, user="erinoverview"):
        self.user_id = user
        self.elements: Dict[str, Dict[str, Any]] = {}
        self.ran: List[tuple] = []
        self.deleted: List[str] = []
        self.governance_zones: List[str] = []
        self.zone_lookup_error: Optional[Exception] = None
        self.members: Dict[str, List[str]] = {}       # element guid -> collections it's filed in
        self.membership_error: Optional[Exception] = None
        self.deleted_sheets: List[str] = []
        outer = self

        class CM:
            async def _async_get_element_by_unique_name(self, qn):
                return outer.elements.get(qn) or "No elements found"

            async def _async_get_elements_by_property_value(self, value, names, metadata_element_type=None, **kw):
                if metadata_element_type == "GovernanceZone":
                    if outer.zone_lookup_error:
                        raise outer.zone_lookup_error
                    same = (lambda z: z.lower() == value.lower()) if kw.get("ignore_case") else (lambda z: z == value)
                    return [{"properties": {"zoneName": z}} for z in outer.governance_zones if same(z)] \
                        or "No elements found"
                return [e for e in outer.elements.values()
                        if e["properties"].get("displayName") == value] or "No elements found"

            async def _async_find_elements_by_property_value(self, value, names, metadata_element_type=None,
                                                             governance_zone_filter=None, start_from=0, **kw):
                if start_from:
                    return []
                return [e for e in outer.elements.values()
                        if e["elementHeader"]["type"]["typeName"] == metadata_element_type]

            async def _async_get_related_elements(self, guid, relationship_type=None, start_at_end=1, **kw):
                assert relationship_type == "CollectionMembership" and start_at_end == 2
                if outer.membership_error:
                    raise outer.membership_error
                return [{"elementHeader": {"guid": c}} for c in outer.members.get(guid, [])] or "No elements found"

        class AM:
            async def _async_delete_asset(self, guid):
                outer.deleted.append(guid)
        self.classification_manager, self.asset_maker = CM(), AM()

    def hold(self, qn, name, type_name, zones, created, marked=True, updated=None):
        self.elements[qn] = {"elementHeader": {"guid": f"g-{name}", "type": {"typeName": type_name},
                                               "versions": {"version": 1, "createTime": created,
                                                            **({"updateTime": updated} if updated else {})},
                                               "zoneMembership": {"classificationProperties":
                                                                  {"zoneMembership": zones}}},
                             "properties": {"qualifiedName": qn, "displayName": name,
                                            "additionalProperties": {"reportSpec": "Project-DrE-Basic",
                                                                     **({"authoringState": "draft"} if marked else {})}}}

    def run(self, md, directive):
        self.ran.append((directive, md))
        return {"success": True}


def test_an_egeria_draft_is_saved_as_the_author_in_their_private_zone():
    eg = _DraftEgeria()
    store = EgeriaDraftStore(eg, eg.run)
    qn = store.save("erinoverview", cdo_report())
    assert qn == CDO_QN
    (directive, md), = eg.ran
    assert directive == "process" and "### Zone Membership\nerinoverview" in md
    assert "### Additional Properties\nauthoringState: draft" in md
    assert "Add Member to Collection" not in md            # never filed into a consumer folder
    assert not has_parent_id(md)
    with pytest.raises(AuthoringRefused, match="signed in as 'erinoverview', not 'garygeeke'"):
        store.save("garygeeke", cdo_report())


def test_an_egeria_draft_never_overwrites_a_published_element():
    eg = _DraftEgeria()
    eg.hold(CDO_QN, "My Ninety Day Plan Progress", "Report", [], "2026-11-12T10:00:00Z")
    store = EgeriaDraftStore(eg, eg.run)
    with pytest.raises(AuthoringRefused, match="would change what others see"):
        store.save("erinoverview", cdo_report())
    assert eg.ran == []


def test_prune_removes_only_the_authors_old_unpromoted_drafts():
    from datetime import datetime, timedelta, timezone
    eg = _DraftEgeria()
    old = (datetime.now(timezone.utc) - timedelta(days=45)).isoformat()
    new = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
    eg.hold("R::old", "Old draft", "Report", ["erinoverview"], old)
    eg.hold("R::new", "New draft", "Report", ["erinoverview"], new)
    eg.hold("R::public", "Published", "Report", [], old)            # promoted: not in the zone
    eg.hold("R::gary", "Gary's", "Report", ["garygeeke"], old)  # another author's
    eg.hold("R::unmarked", "Unmarked", "Report", ["erinoverview"], old, marked=False)  # zoned, but no marker
    store = EgeriaDraftStore(eg, eg.run)
    preview_only = store.prune_drafts("erinoverview", dry_run=True)
    assert preview_only["removed"] == ["report:Old draft"] and eg.deleted == []
    out = store.prune_drafts("erinoverview")
    assert out["removed"] == ["report:Old draft"] and out["kept"] == ["report:New draft"]
    assert out["not_marked"] == ["Unmarked"]
    assert eg.deleted == ["g-Old draft"]


def _days_ago(n):
    from datetime import datetime, timedelta, timezone
    return (datetime.now(timezone.utc) - timedelta(days=n)).isoformat()


def test_prune_takes_a_sheet_only_when_it_is_an_unfiled_private_draft(monkeypatch):
    """F1 (read-back 2026-11-13): a sheet has no draft marker, so prune must prove it is an unfiled private
    draft before deleting it -- a shared or filed (published, Declassify not run) sheet must survive."""
    eg = _DraftEgeria()

    async def fake_delete_sheet(self, name):
        eg.deleted_sheets.append(name)
        return True
    monkeypatch.setattr("md_processing.v2.dashboard_sheet.DashboardSheetEgeriaWriter.delete_sheet",
                        fake_delete_sheet)
    monkeypatch.setattr("md_processing.v2.dashboard_sheet.DashboardSheetEgeriaWriter.__init__",
                        lambda self, client: None)
    eg.hold("Dashboard::scratchpad", "scratchpad", "Dashboard", ["erinoverview"], _days_ago(60))
    eg.hold("Dashboard::shared", "shared", "Dashboard", ["erinoverview", "team-zone"], _days_ago(60))
    eg.hold("Dashboard::filed", "filed", "Dashboard", ["erinoverview"], _days_ago(60))
    eg.members["g-filed"] = ["DashboardFolder::Consumer::Portal"]   # published; its Declassify step failed
    eg.hold("Dashboard::busy", "busy", "Dashboard", ["erinoverview"], _days_ago(60), updated=_days_ago(2))
    eg.hold("Legacy sheet", "Legacy sheet", "Dashboard", ["erinoverview"], _days_ago(60))  # no Dashboard:: QN
    store = EgeriaDraftStore(eg, eg.run)
    out = store.prune_drafts("erinoverview")
    assert out["removed"] == ["sheet:scratchpad"] and eg.deleted_sheets == ["scratchpad"]
    assert out["kept"] == ["sheet:busy"]                       # aged by last update, not creation
    assert out["kept_reasons"] == {"sheet:shared": "zoned beyond your private zone (shared)",
                                   "sheet:filed": "filed in a collection (published)",
                                   "sheet:Legacy sheet": "not a Dashboard:: sheet"}


def test_prune_keeps_a_sheet_whose_memberships_cant_be_read(monkeypatch):
    eg = _DraftEgeria()
    eg.hold("Dashboard::scratchpad", "scratchpad", "Dashboard", ["erinoverview"], _days_ago(60))
    eg.membership_error = TimeoutError("slow")
    out = EgeriaDraftStore(eg, eg.run).prune_drafts("erinoverview")
    assert out["removed"] == [] and "couldn't be read" in out["kept_reasons"]["sheet:scratchpad"]


def test_prune_reports_only_real_deletes(monkeypatch):
    eg = _DraftEgeria()
    eg.hold("Dashboard::gone", "gone", "Dashboard", ["erinoverview"], _days_ago(60))

    async def nothing_deleted(self, name):
        return False
    monkeypatch.setattr("md_processing.v2.dashboard_sheet.DashboardSheetEgeriaWriter.delete_sheet",
                        nothing_deleted)
    monkeypatch.setattr("md_processing.v2.dashboard_sheet.DashboardSheetEgeriaWriter.__init__",
                        lambda self, client: None)
    out = EgeriaDraftStore(eg, eg.run).prune_drafts("erinoverview")
    assert out["removed"] == [] and out["not_deleted"] == ["sheet:gone"]


def test_prune_never_takes_a_report_zoned_beyond_the_author():
    eg = _DraftEgeria()
    eg.hold("R::shared", "Shared draft", "Report", ["erinoverview", "finance"], _days_ago(60))
    out = EgeriaDraftStore(eg, eg.run).prune_drafts("erinoverview")
    assert out["removed"] == [] and eg.deleted == []


def test_the_zone_name_check_fails_closed_when_the_lookup_errors():
    """F2: a lookup error is not "no such zone"; the draft isn't saved."""
    from pyegeria.core._exceptions import PyegeriaNotFoundException
    eg = _DraftEgeria()
    eg.zone_lookup_error = TimeoutError("slow")
    with pytest.raises(AuthoringRefused, match="Couldn't check whether user id 'erinoverview'"):
        EgeriaDraftStore(eg, eg.run).save("erinoverview", cdo_report())
    assert eg.ran == []
    eg.zone_lookup_error = PyegeriaNotFoundException.__new__(PyegeriaNotFoundException)  # a "not found" answer
    EgeriaDraftStore(eg, eg.run).save("erinoverview", cdo_report())
    assert len(eg.ran) == 1


def test_the_zone_name_check_ignores_case():
    eg = _DraftEgeria()
    eg.governance_zones = ["ErinOverview"]
    with pytest.raises(AuthoringRefused, match="governance zone"):
        EgeriaDraftStore(eg, eg.run).save("erinoverview", cdo_report())


def test_promotion_clears_the_private_zone():
    eg = _DraftEgeria()
    eg.hold("Dashboard::catalog-health", "catalog-health", "Dashboard", ["erinoverview"], "2026-11-12")
    store = EgeriaDraftStore(eg, eg.run)
    sheet = catalog_health_sheet()
    plan = _publish(sheet, folders=["DashboardFolder::Consumer::Portal"],
                        held={"held": True, "zones": [store.zone("erinoverview")]})
    assert "## Declassify Zone Membership\n### Target Element\nDashboard::catalog-health" in plan["markdown"]
    assert any("becomes public" in s for s in plan["steps"])
    report_plan = _publish(cdo_report(), held={"held": True, "zones": ["erinoverview"]})
    assert f"## Declassify Zone Membership\n### Target Element\n{CDO_QN}" in report_plan["markdown"]


# ── Shapes seen live on the scratch Egeria (757a5df0) ─────────────────────────

def test_history_entries_are_read_in_egerias_open_metadata_element_shape():
    """Egeria's element history returns OpenMetadataElements, not view beans (seen live, 2026-11-13)."""
    from pyegeria.authoring.versions import as_element
    item = {"elementGUID": "g1", "type": {"typeName": "ReportSpec", "superTypeNames": ["Collection"]},
            "versions": {"version": 2, "updateTime": "2026-11-13T02:15:09Z", "updatedBy": "garygeeke"},
            "elementProperties": {"propertyValueMap": {
                "qualifiedName": {"primitiveValue": "ReportSpec::X"},
                "description": {"primitiveValue": "second version"}}}}
    el = as_element(item)
    assert el["elementHeader"]["guid"] == "g1" and el["elementHeader"]["versions"]["version"] == 2
    assert el["properties"] == {"qualifiedName": "ReportSpec::X", "description": "second version"}


def test_preview_says_an_empty_run_found_nothing(monkeypatch):
    monkeypatch.setattr("pyegeria.view.format_set_executor.exec_report_spec", lambda spec, **kw: {"kind": "empty"})
    out = asyncio.run(async_preview(_spec(), client=_Viewer()))
    assert out["shown"] == 0 and "ran, and found nothing" in out["notes"]


def test_a_spec_draft_is_marked_draft_and_promotion_makes_it_active(monkeypatch):
    monkeypatch.setattr("pyegeria.authoring.lifecycle._is_builtin", lambda label: False)
    spec = SpecDraft(label="Team Projects", format_set=_gold_fs({"spec": "simple"}))
    md = serialize(spec, zones=["erinoverview"], as_draft_element=True)
    assert "### Content Status\nDRAFT" in md and "### Zone Membership\nerinoverview" in md
    plan = _publish(spec, folders=[rsp.PORTAL_FOLDER], held={"held": True, "zones": ["erinoverview"]})
    assert "### Content Status\nACTIVE" in plan["markdown"]
    assert "## Declassify Zone Membership" in plan["markdown"] and "### Zone Membership" not in plan["markdown"]


def test_a_promoted_report_is_marked_published():
    plan = _publish(cdo_report(), held={"held": True, "zones": ["erinoverview"]})
    assert "### Additional Properties\nauthoringState: published" in plan["markdown"]
    stamp = ["publishedAt: (set when published)", "publishedBy: erinoverview", "publishedVersion: 1"]
    assert _publish(cdo_report())["markdown"] == serialize(cdo_report(), stamp=stamp)
