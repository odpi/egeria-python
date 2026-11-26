# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""D2: an Update of a boundary that names an explicit GUID targets that element, or is refused.

Live check 2026-11-26 (scratch, 5a8d6a12): "Update Solution Boundary" with the GUID of a DesignModelBoundary was not
refused. The solution-architect getter answered not-found for the other boundary type, the generic lookup only warned
and fell back to the derived qualified name, found nothing, and the Update was rewritten to a Create: a NEW
SolutionBoundary. SolutionArchitectProcessor.fetch_as_is now reads such a GUID generically and refuses a wrong type or
an unreadable element before any fallback or rewrite. These tests use stub clients; no live claim.
"""
import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.v2.solution_architect import SolutionArchitectProcessor
from pyegeria.core._globals import NO_ELEMENTS_FOUND

pytestmark = pytest.mark.unit

OWN_READS = {"SolutionBoundary": "_async_get_solution_boundary_by_guid",
             "DesignModelBoundary": "_async_get_collection_by_guid"}
GENERIC_READ = "_async_get_element_by_guid_"


def _element(guid: str, type_name: str) -> dict:
    return {"elementHeader": {"guid": guid, "type": {"typeName": type_name}},
            "properties": {"class": f"{type_name}Properties", "displayName": "D2 Boundary"}}


class _Client:
    """Answers each _async_ method from `answers` (a value, or an exception to raise) and records every call."""

    def __init__(self, **answers):
        self.answers = answers
        self.calls = []

    def __getattr__(self, name):
        if not name.startswith("_async_"):
            raise AttributeError(name)

        async def method(*args, **kwargs):
            self.calls.append(name)
            answer = self.answers.get(name)
            if isinstance(answer, BaseException):
                raise answer
            return answer
        return method


def _processor(om_type: str, verb: str, client, explicit_guid: str | None = "target-guid") -> SolutionArchitectProcessor:
    object_type = {"SolutionBoundary": "Solution Boundary", "DesignModelBoundary": "Design Model Boundary",
                   "SolutionBlueprint": "Solution Blueprint"}[om_type]
    cmd = DrECommand(verb=verb, object_type=object_type, attributes={},
                     raw_block=f"## {verb} {object_type}\n### Display Name\nD2 Boundary\n")
    p = SolutionArchitectProcessor(client, cmd, {})
    p.get_command_spec = lambda: {"OM_TYPE": om_type, "family": "Solution Architect"}
    attributes = {"Display Name": {"value": "D2 Boundary"}}
    if explicit_guid is not None:
        attributes["GUID"] = {"value": explicit_guid}
    p.parsed_output = {"qualified_name": f"Coco::{om_type}::D2-Boundary", "attributes": attributes}
    return p


@pytest.fixture
def generic_lookup(monkeypatch):
    """Replace the generic (QN-fallback) lookup with a recorder: any call to it is the bug this fix closes."""
    seen = []

    async def fake(self):
        seen.append(self.command.verb)
        return None
    monkeypatch.setattr(AsyncBaseCommandProcessor, "fetch_as_is", fake)
    return seen


# ── both directions ──

async def test_update_solution_boundary_on_a_design_model_boundary_guid_is_refused(generic_lookup):
    # The live D2 case: the SolutionBoundary getter finds nothing for a DesignModelBoundary GUID.
    client = _Client(**{OWN_READS["SolutionBoundary"]: None, GENERIC_READ: _element("target-guid", "DesignModelBoundary")})
    with pytest.raises(ValueError) as refused:
        await _processor("SolutionBoundary", "Update", client).fetch_as_is()
    message = str(refused.value)
    assert "target-guid is a DesignModelBoundary, not a SolutionBoundary" in message
    assert "nothing was written" in message
    assert client.calls == [OWN_READS["SolutionBoundary"], GENERIC_READ]   # reads only: no create, no update
    assert generic_lookup == []                                            # no qualified-name fallback


async def test_update_design_model_boundary_on_a_solution_boundary_guid_found_through_the_subtype(generic_lookup):
    # The collection getter can return the SolutionBoundary (a subtype): it is returned, and the existing B5 guard
    # in apply_changes refuses it (as it did live).
    sb = _element("target-guid", "SolutionBoundary")
    client = _Client(**{OWN_READS["DesignModelBoundary"]: sb})
    p = _processor("DesignModelBoundary", "Update", client)
    assert await p.fetch_as_is() is sb
    assert generic_lookup == []
    p.as_is_element = sb
    p.parsed_output["guid"] = "target-guid"
    with pytest.raises(ValueError) as refused:
        await p.apply_changes()
    assert "is a SolutionBoundary, not a DesignModelBoundary" in str(refused.value)
    assert client.calls == [OWN_READS["DesignModelBoundary"]]             # no update request


async def test_update_design_model_boundary_on_a_solution_boundary_guid_its_getter_cannot_read(generic_lookup):
    client = _Client(**{OWN_READS["DesignModelBoundary"]: None, GENERIC_READ: _element("target-guid", "SolutionBoundary")})
    with pytest.raises(ValueError) as refused:
        await _processor("DesignModelBoundary", "Update", client).fetch_as_is()
    assert "target-guid is a SolutionBoundary, not a DesignModelBoundary" in str(refused.value)
    assert client.calls == [OWN_READS["DesignModelBoundary"], GENERIC_READ]
    assert generic_lookup == []


# ── a GUID that names nothing, or an element that can't be read ──

@pytest.mark.parametrize("om_type", ["SolutionBoundary", "DesignModelBoundary"])
async def test_update_on_a_missing_guid_is_refused_not_created(om_type, generic_lookup):
    client = _Client(**{OWN_READS[om_type]: None, GENERIC_READ: NO_ELEMENTS_FOUND})
    with pytest.raises(ValueError) as refused:
        await _processor(om_type, "Update", client).fetch_as_is()
    message = str(refused.value)
    assert f"Couldn't read element target-guid, so the Update {om_type} was not sent" in message
    assert "nothing was created" in message
    assert generic_lookup == []


@pytest.mark.parametrize("om_type", ["SolutionBoundary", "DesignModelBoundary"])
async def test_update_on_an_unreadable_element_is_refused(om_type, generic_lookup):
    client = _Client(**{OWN_READS[om_type]: RuntimeError("own read failed"),
                        GENERIC_READ: RuntimeError("generic read failed")})
    with pytest.raises(ValueError) as refused:
        await _processor(om_type, "Update", client).fetch_as_is()
    assert "Couldn't read element target-guid" in str(refused.value)
    assert generic_lookup == []


async def test_update_whose_own_getter_fails_on_an_element_of_its_own_type_is_refused(generic_lookup):
    client = _Client(**{OWN_READS["SolutionBoundary"]: None, GENERIC_READ: _element("target-guid", "SolutionBoundary")})
    with pytest.raises(ValueError) as refused:
        await _processor("SolutionBoundary", "Update", client).fetch_as_is()
    assert "The SolutionBoundary request could not read element target-guid" in str(refused.value)
    assert generic_lookup == []


# ── the happy path and everything outside the fix keep the generic lookup ──

@pytest.mark.parametrize("om_type", ["SolutionBoundary", "DesignModelBoundary"])
async def test_update_on_an_element_of_the_right_type_is_returned(om_type, generic_lookup):
    el = _element("target-guid", om_type)
    client = _Client(**{OWN_READS[om_type]: el})
    assert await _processor(om_type, "Update", client).fetch_as_is() is el
    assert client.calls == [OWN_READS[om_type]]
    assert generic_lookup == []


@pytest.mark.parametrize("om_type, verb, explicit_guid", [
    ("SolutionBoundary", "Update", None),          # no explicit GUID: qualified-name lookup as before
    ("DesignModelBoundary", "Update", None),
    ("SolutionBoundary", "Create", "target-guid"),  # Create (ISSUE-59 explicit-GUID behaviour) is not changed here
    ("SolutionBlueprint", "Update", "target-guid"),  # not a boundary
])
async def test_other_cases_keep_the_generic_lookup(om_type, verb, explicit_guid, generic_lookup):
    client = _Client()
    assert await _processor(om_type, verb, client, explicit_guid).fetch_as_is() is None
    assert generic_lookup == [verb]
    assert client.calls == []
