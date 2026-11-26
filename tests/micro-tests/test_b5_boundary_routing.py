# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""B5: Dr.Egeria routing for the boundary commands (odpi/egeria#9465).

"Create Solution Boundary" (OM_TYPE SolutionBoundary) and "Create Design Model Boundary" (OM_TYPE DesignModelBoundary)
go to SolutionArchitectProcessor. SolutionBoundary uses the solution-architect boundary requests; DesignModelBoundary,
which that view service has no request for, uses the generic collection requests. Members are added with the existing
Collection Membership command, so nothing here syncs members.

The command specs come with B4; these tests use synthetic specs with the pinned command names. The SolutionBoundary
read uses the real shape captured in window P (5a8d6a12); the DesignModelBoundary read shape is SYNTHETIC (no real
capture exists). No live claim.
"""
import json
from pathlib import Path

import pytest

import md_processing.md_processing_utils.md_processing_constants as mpc
from md_processing.dr_egeria import register_solution_architect_processors
from md_processing.v2.extraction import DrECommand
from md_processing.v2.solution_architect import (
    BlueprintProcessor, SolutionArchitectProcessor, SolutionLinkProcessor)

pytestmark = pytest.mark.unit

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
REAL_BOUNDARY = FIXTURES / "solution_boundary_retrieve_real_shape_2026_11_25_5a8d6a12.json"

SOLUTION_BOUNDARY = "Create Solution Boundary"
DESIGN_MODEL_BOUNDARY = "Create Design Model Boundary"
OM_TYPES = {SOLUTION_BOUNDARY: "SolutionBoundary", DESIGN_MODEL_BOUNDARY: "DesignModelBoundary"}


# ── routing ─────────────────────────────────────────────────────────────────

def _routes(monkeypatch, specs: dict) -> dict:
    monkeypatch.setattr(mpc, "load_commands", lambda *a, **k: None)
    monkeypatch.setattr(mpc, "COMMAND_DEFINITIONS", {"Command Specifications": specs})
    routed = {}
    register_solution_architect_processors(lambda name, cls: routed.__setitem__(name, cls))
    return routed


def _spec(om_type: str, family: str = "Solution Architect") -> dict:
    return {"family": family, "OM_TYPE": om_type, "verb": "Create", "upsert": True}


def test_both_boundary_commands_route_to_the_solution_architect_processor(monkeypatch):
    routed = _routes(monkeypatch, {name: _spec(t) for name, t in OM_TYPES.items()})
    assert routed == {SOLUTION_BOUNDARY: SolutionArchitectProcessor, DESIGN_MODEL_BOUNDARY: SolutionArchitectProcessor}


def test_boundary_branch_leaves_blueprint_and_link_routing_alone(monkeypatch):
    routed = _routes(monkeypatch, {
        "Create Solution Blueprint": _spec("SolutionBlueprint"),
        "Link Component to Boundary": _spec("CollectionMembership"),  # a link verb wins over the noun
        SOLUTION_BOUNDARY: _spec("SolutionBoundary"),
        "Create Boundary Elsewhere": _spec("SolutionBoundary", family="Collections"),  # other families untouched
    })
    assert routed["Create Solution Blueprint"] is BlueprintProcessor
    assert routed["Link Component to Boundary"] is SolutionLinkProcessor
    assert routed[SOLUTION_BOUNDARY] is SolutionArchitectProcessor
    assert "Create Boundary Elsewhere" not in routed


# ── the processor ───────────────────────────────────────────────────────────

class _RecordingClient:
    """Records every SDK call; create calls return a GUID, reads return what the test gives."""

    def __init__(self, read_result=None):
        self.calls = []
        self.read_result = read_result

    def __getattr__(self, name):
        if not name.startswith("_async_"):
            raise AttributeError(name)

        async def method(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            if name.startswith("_async_create_"):
                return "new-boundary-guid"
            if name.startswith("_async_get_"):
                return self.read_result
            return None
        return method


def _processor(command_name: str, verb: str, client, guid: str | None = None) -> SolutionArchitectProcessor:
    object_type = command_name.split(" ", 1)[1]
    cmd = DrECommand(verb=verb, object_type=object_type, attributes={},
                     raw_block=f"## {verb} {object_type}\n### Display Name\nB5 Boundary\n")
    p = SolutionArchitectProcessor(client, cmd, {})
    p.get_command_spec = lambda: {"OM_TYPE": OM_TYPES[command_name], "family": "Solution Architect"}

    async def _render(g):
        return f"rendered {g}"
    p.render_result_markdown = _render
    p.parsed_output = {
        "qualified_name": "SolutionBoundary::B5 Boundary",
        "attributes": {"Display Name": {"value": "B5 Boundary"}, "Description": {"value": "d"},
                       "Purpose": {"value": "group the payment components"}},
    }
    if guid:
        p.parsed_output["guid"] = guid
    return p


@pytest.mark.parametrize("command_name, method, kwarg_body", [
    (SOLUTION_BOUNDARY, "_async_create_solution_boundary", False),
    (DESIGN_MODEL_BOUNDARY, "_async_create_collection", True),
])
async def test_create_calls_the_right_request_with_the_typed_properties(command_name, method, kwarg_body):
    client = _RecordingClient()
    out = await _processor(command_name, "Create", client).apply_changes()
    assert out == "rendered new-boundary-guid"
    assert [c[0] for c in client.calls] == [method]
    _, args, kwargs = client.calls[0]
    body = kwargs["body"] if kwarg_body else args[0]
    props = body["properties"]
    assert props["class"] == f"{OM_TYPES[command_name]}Properties"
    assert props["displayName"] == "B5 Boundary"
    assert props["purpose"] == "group the payment components"
    if kwarg_body:
        assert kwargs["prop"] == ["DesignModelBoundaryProperties"]


@pytest.mark.parametrize("command_name, method", [
    (SOLUTION_BOUNDARY, "_async_update_solution_boundary"),
    (DESIGN_MODEL_BOUNDARY, "_async_update_collection"),
])
async def test_update_calls_the_right_request_for_the_known_guid(command_name, method):
    client = _RecordingClient()
    out = await _processor(command_name, "Update", client, guid="existing-guid").apply_changes()
    assert out == "rendered existing-guid"
    assert [c[0] for c in client.calls] == [method]
    _, args, _ = client.calls[0]
    assert args[0] == "existing-guid"
    assert args[1]["properties"]["class"] == f"{OM_TYPES[command_name]}Properties"


async def test_solution_boundary_is_read_back_with_the_boundary_request_real_shape():
    real = json.loads(REAL_BOUNDARY.read_text(encoding="utf-8"))
    guid = real["elementHeader"]["guid"]
    client = _RecordingClient(read_result=real)
    element = await _processor(SOLUTION_BOUNDARY, "Create", client).fetch_element(guid)
    assert client.calls == [("_async_get_solution_boundary_by_guid", (guid,), {})]
    assert element["elementHeader"]["type"]["typeName"] == "SolutionBoundary"


async def test_design_model_boundary_is_read_back_with_the_collection_request_synthetic_shape():
    synthetic = {"elementHeader": {"guid": "dmb-guid", "type": {"typeName": "DesignModelBoundary"}},
                 "properties": {"class": "DesignModelBoundaryProperties", "displayName": "SYNTHETIC"}}
    client = _RecordingClient(read_result=synthetic)
    element = await _processor(DESIGN_MODEL_BOUNDARY, "Create", client).fetch_element("dmb-guid")
    assert client.calls == [("_async_get_collection_by_guid", ("dmb-guid",), {})]
    assert element is synthetic
