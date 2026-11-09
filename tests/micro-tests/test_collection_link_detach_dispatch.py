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

    with pytest.raises(ValueError, match="did not resolve to a GUID"):
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


# --- Every detach branch refuses an unresolved end (read-back P3) ---------------

G1, G2 = COLLECTION_GUID, ELEMENT_GUID


class _RecordingClient:
    """Records every _async_detach_* / _async_remove_* call; other lookups fail."""

    def __init__(self, relationships=None):
        self.calls: list[tuple] = []
        self.relationships = relationships if relationships is not None else []

    async def _async_get_relationships(self, *args, **kwargs):
        return self.relationships

    def __getattr__(self, name):
        if name.startswith(("_async_detach", "_async_remove")):
            async def _record(*args, **kwargs):
                self.calls.append((name, args[:-1]))
            return _record
        raise AttributeError(name)


# (object type, both ends resolved, expected call, the end left out)
DETACH_CASES = [
    ("Data Description", {"Element Id": G1, "Collection Id": G2},
     ("_async_detach_data_description", (G1, G2)), "Collection Id"),
    ("Digital Subscriber", {"Subscriber Id": G1, "Subscription Id": G2},
     ("_async_detach_subscriber", (G1, G2)), "Subscription Id"),
    ("Member from Collection", {"Collection Id": G1, "Element Id": G2},
     ("_async_remove_from_collection", (G1, G2)), "Collection Id"),
    ("Business Capability Dependency", {"Dependent Capability": G1, "Supporting Capability": G2},
     ("_async_detach_business_capability_dependency", (G1, G2)), "Supporting Capability"),
    ("Digital Support", {"Supported Capability": G1, "Digital Service": G2},
     ("_async_detach_digital_support", (G1, G2)), "Digital Service"),
    ("Product Dependency", {"Digital Product 1": G1, "Digital Product 2": G2},
     ("_async_detach_digital_product_dependency", (G1, G2)), "Digital Product 2"),
    ("Agreement Item", {"Agreement Name": G1, "Item Name": G2},
     ("_async_detach_agreement_item", (G1, G2)), "Item Name"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("object_type,attrs,expected,_missing", DETACH_CASES,
                         ids=[c[0] for c in DETACH_CASES])
async def test_detach_with_both_ends_sends_one_call(object_type, attrs, expected, _missing):
    client = _RecordingClient()
    result = await _dispatch(client, "Detach", object_type, attrs)

    assert client.calls == [expected], result
    assert result["status"] == "success", result


@pytest.mark.asyncio
@pytest.mark.parametrize("object_type,attrs,_expected,missing", DETACH_CASES,
                         ids=[c[0] for c in DETACH_CASES])
async def test_detach_with_an_end_left_out_fails_and_sends_nothing(object_type, attrs, _expected, missing):
    """Through the real dispatcher: an omitted end never reaches Egeria as None.

    Optional ends (Collection Id, Subscription Id) pass validation and are
    refused by the processor; required ends are refused by validation first.
    Either way: failure, no call, no "Operation completed".
    """
    client = _RecordingClient()
    attrs = {k: v for k, v in attrs.items() if k != missing}
    result = await _dispatch(client, "Detach", object_type, attrs)

    assert client.calls == [], result
    assert result["status"] == "failure", result
    assert "Operation completed" not in str(result.get("output", "")), result
    assert missing in result["message"], result


@pytest.mark.asyncio
@pytest.mark.parametrize("object_type,attrs,_expected,missing", DETACH_CASES,
                         ids=[c[0] for c in DETACH_CASES])
async def test_detach_backstop_refuses_unresolved_end(object_type, attrs, _expected, missing):
    """The processor itself refuses, even when validation let an end through unresolved."""
    client = _RecordingClient()
    command = _command("Detach", object_type, {})
    p = CollectionLinkProcessor(client=client, command=command, context={})
    parsed = {k: {"value": v, "guid": v} for k, v in attrs.items()}
    parsed[missing] = {"value": "Unresolved Name", "guid": None}
    p.parsed_output = {"qualified_name": "", "attributes": parsed}

    with pytest.raises(ValueError, match=f"did not resolve to a GUID: {missing}"):
        await p.apply_changes()
    assert client.calls == []


@pytest.mark.asyncio
async def test_detach_agreement_actor_without_actors_fails():
    client = _RecordingClient()
    result = await _dispatch(client, "Detach", "Agreement Actor", {"Agreement Name": G1})

    assert client.calls == [], result
    assert result["status"] == "failure", result
    assert "Actors did not resolve" in result["message"], result


@pytest.mark.asyncio
async def test_detach_agreement_actor_not_linked_fails():
    """No AgreementActor relationship between the pair: refuse, don't report success."""
    client = _RecordingClient(relationships=[])
    result = await _dispatch(client, "Detach", "Agreement Actor", {"Agreement Name": G1, "Actors": G2})

    assert client.calls == [], result
    assert result["status"] == "failure", result
    assert "no AgreementActor relationship found" in result["message"], result


@pytest.mark.asyncio
async def test_detach_agreement_actor_by_pair_detaches_the_found_relationship():
    """The pair lookup is reachable from CollectionLinkProcessor (was AttributeError)."""
    client = _RecordingClient(relationships=[
        {"relationshipGUID": "rel-1", "elementGUIDAtEnd1": G1, "elementGUIDAtEnd2": G2}])
    result = await _dispatch(client, "Detach", "Agreement Actor", {"Agreement Name": G1, "Actors": G2})

    assert client.calls == [("_async_detach_agreement_actor", ("rel-1",))], result
    assert result["status"] == "success", result
