# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
CollectionLinkProcessor must route every command phrasing to a real
relationship call, and must never report "Operation completed" when it sent
nothing.

Seen live with pyegeria 6.2.27: ``## Detach Member from Collection`` resolves
(via its compact spec's alternate names) to the canonical command "Add Member
to Collection", so the processor's object type is "Member to Collection".  The
Detach branch picked its call by substring ("Collection Membership" /
"Collection Member"), matched nothing, sent no request, and still returned
"Operation completed" -- the membership stayed in place.

These tests go through the real ``setup_dispatcher()`` registry and
``V2Dispatcher.dispatch()`` with a fake client, so command-name resolution,
canonical object type and OM_TYPE are all the production ones.
"""
import uuid
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest

from md_processing.dr_egeria import setup_dispatcher
from md_processing.v2.collection_manager_processor import CollectionLinkProcessor
from md_processing.v2.extraction import DrECommand

COLLECTION_GUID = str(uuid.UUID(int=1))
ELEMENT_GUID = str(uuid.UUID(int=2))
RESOURCE_GUID = str(uuid.UUID(int=3))


class _FakeClient:
    """Records the relationship calls the processor makes; nothing else."""

    def __init__(self):
        self.calls: list[tuple] = []

    def __getattr__(self, name):
        # Any other client method (lookups during validation) -> AttributeError
        # is what a missing method looks like; keep unknown _async_ calls
        # visible instead of silently succeeding.
        raise AttributeError(name)

    async def _async_remove_from_collection(self, collection_guid, element_guid, body=None):
        self.calls.append(("remove_from_collection", collection_guid, element_guid))

    async def _async_add_to_collection(self, collection_guid, element_guid, body=None):
        self.calls.append(("add_to_collection", collection_guid, element_guid))

    async def _async_attach_collection(self, resource_guid, collection_guid, body=None):
        self.calls.append(("attach_collection", resource_guid, collection_guid))

    async def _async_detach_collection(self, resource_guid, collection_guid, body=None):
        self.calls.append(("detach_collection", resource_guid, collection_guid))


def _command(verb: str, object_type: str, attributes: Dict[str, str]) -> DrECommand:
    raw = f"## {verb} {object_type}\n" + "".join(f"### {k}\n{v}\n" for k, v in attributes.items())
    return DrECommand(verb=verb, object_type=object_type, attributes=attributes, raw_block=raw)


async def _dispatch(client, verb, object_type, attributes):
    dispatcher = setup_dispatcher(client)
    context: Dict[str, Any] = {"directive": "process"}
    return await dispatcher.dispatch(_command(verb, object_type, attributes), context)


MEMBER_ATTRS = {"Collection Id": COLLECTION_GUID, "Element Id": ELEMENT_GUID}


@pytest.mark.asyncio
@pytest.mark.parametrize("verb,object_type", [
    ("Detach", "Member from Collection"),   # the live failure
    ("Remove", "Member from Collection"),
    ("Unlink", "Member"),
    ("Detach", "Member from Folder"),
])
async def test_detach_member_sends_exactly_one_remove(verb, object_type):
    client = _FakeClient()
    result = await _dispatch(client, verb, object_type, MEMBER_ATTRS)

    assert client.calls == [("remove_from_collection", COLLECTION_GUID, ELEMENT_GUID)], result
    assert result["status"] == "success", result


@pytest.mark.asyncio
async def test_add_member_still_sends_one_add():
    client = _FakeClient()
    result = await _dispatch(client, "Add", "Member to Collection", MEMBER_ATTRS)

    assert client.calls == [("add_to_collection", COLLECTION_GUID, ELEMENT_GUID)], result
    assert result["status"] == "success", result


@pytest.mark.asyncio
@pytest.mark.parametrize("verb,expected", [
    ("Attach", "attach_collection"),
    ("Detach", "detach_collection"),
])
async def test_collection_to_resource_phrasings_route(verb, expected):
    # Same shape as the member bug: "Attach Collection to Resource" resolves
    # to object type "Collection to Resource", which neither the old Link
    # test ("Attach Collection") nor the old Detach test matched.
    client = _FakeClient()
    attrs = {"Collection Id": COLLECTION_GUID, "Element Id": RESOURCE_GUID}  # spec names the resource end "Element Id"
    noun = "Collection to Resource" if verb == "Attach" else "Collection from Resource"
    result = await _dispatch(client, verb, noun, attrs)

    assert client.calls == [(expected, RESOURCE_GUID, COLLECTION_GUID)], result
    assert result["status"] == "success", result


@pytest.mark.asyncio
@pytest.mark.parametrize("verb", ["Detach", "Link"])
async def test_unmatched_object_type_fails_loudly(verb):
    """A relationship type no branch handles must fail, never 'Operation completed'."""
    client = _FakeClient()
    command = _command(verb, "Gizmo Widget", {})
    p = CollectionLinkProcessor(client=client, command=command, context={})
    p.canonical_object_type = "Gizmo Widget"
    p.egeria_type_name = "GizmoWidget"
    p.parsed_output = {"qualified_name": "", "attributes": {}}

    with pytest.raises(ValueError, match="nothing was sent to Egeria"):
        await p.apply_changes()
    assert client.calls == []


@pytest.mark.asyncio
async def test_detach_member_without_guids_fails():
    client = _FakeClient()
    command = _command("Detach", "Member from Collection", {})
    p = CollectionLinkProcessor(client=client, command=command, context={})
    p.parsed_output = {"qualified_name": "", "attributes": {"Collection Id": {"value": "x"}}}

    with pytest.raises(ValueError, match="must both resolve"):
        await p.apply_changes()
    assert client.calls == []


def test_every_registered_phrasing_resolves_to_a_relationship():
    """Every Link/Detach phrasing routed to CollectionLinkProcessor lands on a handler."""
    dispatcher = setup_dispatcher(MagicMock())
    misses = []
    for key, cls in dispatcher.processors.items():
        if cls is not CollectionLinkProcessor:
            continue
        verb, _, noun = key.partition(" ")
        if verb not in ("Link", "Attach", "Add", "Detach", "Unlink", "Remove"):
            continue
        p = CollectionLinkProcessor(client=MagicMock(), command=_command(verb, noun, {}), context={})
        try:
            p._relationship_type(p.canonical_object_type)
        except ValueError:
            misses.append(key)
    assert misses == []
