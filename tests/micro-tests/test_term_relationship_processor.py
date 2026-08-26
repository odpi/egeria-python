# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Regression tests for ISSUE-76 (PYEGERIA_ISSUES.md): TermRelationshipProcessor
offered several term-to-term relationship types that have never existed as
real Egeria types (TermHASARelationship, TermTYPEDBYRelationship,
TermISATYPEOFRelationship -- confirmed against a live server's
get_all_relationship_defs() and against every open-metadata-types archive
version in odpi/egeria's own history), so every "Link Term-Term
Relationship" command using HASA/TYPED BY/TYPE OF always failed server-side
with a 400.

Worse: apply_changes() caught that failure internally and returned
self.command.raw_block instead of letting it propagate, which defeated
AsyncBaseCommandProcessor.execute()'s own failure reporting -- the batch
summary said "status": "success" for a command that changed nothing.

No live server needed: a fake client stands in for the OMVS layer.
"""
from typing import Any, cast

import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.glossary import TermRelationshipProcessor
from pyegeria.core._exceptions import PyegeriaException


class _FakeClient:
    def __init__(self, raise_on_add: bool = False):
        self.add_calls = []
        self.remove_calls = []
        self.raise_on_add = raise_on_add

    async def _async_add_relationship_between_terms(self, term1_guid, term2_guid, relationship):
        if self.raise_on_add:
            raise PyegeriaException()
        self.add_calls.append((term1_guid, term2_guid, relationship))

    async def _async_remove_relationship_between_terms(self, term1_guid, term2_guid, relationship):
        self.remove_calls.append((term1_guid, term2_guid, relationship))


def _command(verb: str) -> DrECommand:
    return DrECommand(verb=verb, object_type="Term-Term Relationship", attributes={},
                       raw_block=f"# {verb} Term-Term Relationship")


def _processor(client, verb, relationship_value):
    p = TermRelationshipProcessor(client=cast(Any, client), command=_command(verb), context={})
    p.parsed_output = {
        "qualified_name": "TermRel::test::1",
        "attributes": {
            "Term 1": {"guid": "term-1-guid", "qualified_name": "Term::One"},
            "Term 2": {"guid": "term-2-guid", "qualified_name": "Term::Two"},
            "Relationship Type": {"value": relationship_value},
        },
    }
    return p


@pytest.mark.asyncio
async def test_real_relationship_type_links_successfully():
    client = _FakeClient()
    p = _processor(client, "Link", "Synonym")

    result = await p.apply_changes()

    assert client.add_calls == [("term-1-guid", "term-2-guid", "Synonym")]
    assert "Synonym" in result


@pytest.mark.asyncio
async def test_isa_alias_maps_to_real_isa_relationship_type():
    client = _FakeClient()
    p = _processor(client, "Link", "ISA")

    await p.apply_changes()

    assert client.add_calls == [("term-1-guid", "term-2-guid", "ISARelationship")]


@pytest.mark.asyncio
async def test_obsolete_hasa_type_raises_clear_error_instead_of_hitting_the_server():
    client = _FakeClient()
    p = _processor(client, "Link", "HASA")

    with pytest.raises(ValueError, match="Unknown term relationship type"):
        await p.apply_changes()

    # Never reached the client at all -- caught before the request was built.
    assert client.add_calls == []


@pytest.mark.asyncio
async def test_obsolete_type_of_type_raises_clear_error():
    client = _FakeClient()
    p = _processor(client, "Link", "TYPE OF")

    with pytest.raises(ValueError, match="Unknown term relationship type"):
        await p.apply_changes()


@pytest.mark.asyncio
async def test_server_failure_propagates_instead_of_being_swallowed():
    """The core ISSUE-76 regression: a real PyegeriaException from the client
    must propagate out of apply_changes(), not be caught and turned into a
    quiet self.command.raw_block return -- swallowing it here is exactly
    what let execute() report "status": "success" for a failed link."""
    client = _FakeClient(raise_on_add=True)
    p = _processor(client, "Link", "Synonym")

    with pytest.raises(PyegeriaException):
        await p.apply_changes()


