# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Re-running a Dr.Egeria `Link` command on a MULTI_LINK relationship type must
update the instance it describes, not add a duplicate (Egeria never merges a
second MULTI_LINK instance itself).

Each case gives the relationship's end order as Egeria's type definition has
it (confirmed live against get_all_relationship_defs, 2026-09-25) -- e.g.
Certification/License put the certified element at end 1 and the type at end
2, the reverse of the command's own argument order -- and the properties that
identify an instance of that type.

No live server needed: the fake returns the real find-relationships envelope
({"relationships": [...]}, properties in OMRS propertyValueMap form).
"""
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, cast

import pytest

from md_processing.v2.action_author import ActionProcessStepLinkProcessor
from md_processing.v2.collection_manager_processor import CollectionLinkProcessor
from md_processing.v2.extraction import DrECommand
from md_processing.v2.feedback import FeedbackLinkProcessor
from md_processing.v2.governance import GovernanceLinkProcessor
from md_processing.v2.lineage_linker import LineageLinkProcessor
from md_processing.v2.multilink import async_link_or_update
from md_processing.v2.saved_query import SmartQueryLinkProcessor
from pyegeria.omvs.metadata_expert import MetadataExpert

pytestmark = pytest.mark.unit

NEW_GUID = "new-relationship-guid"
EXISTING_GUID = "existing-relationship-guid"


def relationship(guid, end1, end2, props):
    return {
        "relationshipGUID": guid,
        "elementGUIDAtEnd1": end1,
        "elementGUIDAtEnd2": end2,
        "relationshipProperties": {"propertyValueMap": {
            k: {"class": "PrimitiveTypePropertyValue", "typeName": "string", "primitiveValue": v}
            for k, v in props.items()}},
    }


class RecordingClient:
    """Stands in for EgeriaTech: records every _async_* call; creates return NEW_GUID."""

    def __init__(self, existing=None):
        self.existing = existing or []
        self.calls = []

    @property
    def metadata_expert(self):
        return self

    @property
    def collection_manager(self):
        return self

    async def _async_find_relationships_between_elements(self, body):
        if not self.existing:
            return "No elements returned"
        return {"relationships": self.existing, "mermaidGraph": ""}

    def __getattr__(self, name):
        if not name.startswith("_async_"):
            raise AttributeError(name)

        async def record(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            return NEW_GUID
        return record

    def called(self, name):
        return [args for n, args, _ in self.calls if n == name]


@dataclass
class Case:
    id: str
    make: Callable[[Any], Any]
    ends: tuple
    key: dict
    create: str
    update: Optional[str]
    extra: dict = field(default_factory=dict)


def _processor(cls, verb, object_type, attributes, om_type=None):
    def make(client):
        p = cls(client=cast(Any, client),
                command=DrECommand(verb=verb, object_type=object_type, attributes={},
                                   raw_block=f"# {verb} {object_type}"),
                context={})
        p.canonical_object_type = object_type
        if om_type:
            p.get_command_spec = lambda: {"OM_TYPE": om_type}

        async def render(guid):
            return f"rendered {guid}"
        p.render_result_markdown = render
        p.parsed_output = {"qualified_name": f"{object_type}::test", "attributes": attributes}
        return p
    return make


CASES = [
    Case("certification", _processor(GovernanceLinkProcessor, "Link", "Certification", {
        "Certification Type": {"guid": "cert-type"}, "Referenceable": {"guid": "element"},
        "Certificate GUID": {"value": "CERT-1"}}, "Certification"),
        ("element", "cert-type"), {"certificateId": "CERT-1"},
        "_async_add_certification_to_element", "_async_update_certification"),
    Case("license", _processor(GovernanceLinkProcessor, "Link", "License", {
        "License Type": {"guid": "license-type"}, "Referenceable": {"guid": "element"},
        "License GUID": {"value": "LIC-1"}}, "License"),
        ("element", "license-type"), {"licenseId": "LIC-1"},
        "_async_add_license_to_element", "_async_update_license"),
    Case("agreement-terms", _processor(GovernanceLinkProcessor, "Link", "Agreement Terms and Conditions", {
        "Agreement Name": {"guid": "agreement"}, "Terms & Conditions Id": {"guid": "terms"},
        "Agreement Item Id": {"value": "ITEM-1"}}, "AgreementItem"),
        ("agreement", "terms"), {"agreementItemId": "ITEM-1"},
        "_async_link_agreement_item", "_async_update_agreement_item"),
    Case("associated-security-list", _processor(GovernanceLinkProcessor, "Link", "Associated List", {
        "Access Control": {"guid": "access-control"}, "Security List": {"guid": "security-list"},
        "Operation Name": {"value": "read"}}, "AssociatedSecurityList"),
        ("access-control", "security-list"), {"operationName": "read"},
        "_async_create_related_elements", None),
    Case("external-reference", _processor(FeedbackLinkProcessor, "Link", "External Reference", {
        "Referenceable Element": {"guid": "element"}, "External Reference": {"guid": "ext-ref"},
        "Reference Id": {"value": "REF-1"}}),
        ("element", "ext-ref"), {"referenceId": "REF-1"},
        "_async_link_external_reference", "_async_update_external_reference_link"),
    Case("media-reference", _processor(FeedbackLinkProcessor, "Link", "Media Reference", {
        "Referenceable Element": {"guid": "element"}, "Media Reference": {"guid": "media"},
        "Media Id": {"value": "MEDIA-1"}}),
        ("element", "media"), {"mediaId": "MEDIA-1"},
        "_async_link_media_reference", "_async_update_media_reference"),
    Case("cited-document", _processor(FeedbackLinkProcessor, "Link", "Cited Document", {
        "Referenceable Element": {"guid": "element"}, "Cited Document": {"guid": "doc"},
        "Reference Id": {"value": "REF-2"}}),
        ("element", "doc"), {"referenceId": "REF-2"},
        "_async_link_cited_document", "_async_update_cited_document_reference"),
    Case("next-process-step", _processor(ActionProcessStepLinkProcessor, "Link", "Next Process Step", {
        "Governance Action Process Step": {"guid": "step-1"},
        "Next Governance Action Process Step": {"guid": "step-2"}, "Guard": {"value": "approved"}},
        "NextGovernanceActionProcessStep"),
        ("step-1", "step-2"), {"guard": "approved"},
        "_async_setup_next_action_process_step", "_async_update_next_action_process_step"),
    Case("data-flow", _processor(LineageLinkProcessor, "Link", "Data Flow", {
        "Element One": {"guid": "source"}, "Element Two": {"guid": "target"},
        "Label": {"value": "feeds"}, "ISC Qualified Name": {"value": "ISC::A"}}, "DataFlow"),
        ("source", "target"), {"label": "feeds", "iscQualifiedName": "ISC::A"},
        "_async_link_data_flow", "_async_update_lineage"),
    Case("control-flow", _processor(LineageLinkProcessor, "Link", "Control Flow", {
        "Element One": {"guid": "source"}, "Element Two": {"guid": "target"},
        "Label": {"value": "then"}, "ISC Qualified Name": {"value": "ISC::A"}}, "ControlFlow"),
        ("source", "target"), {"label": "then", "iscQualifiedName": "ISC::A"},
        "_async_link_lineage", "_async_update_lineage"),
    Case("agreement-item", _processor(CollectionLinkProcessor, "Link", "Agreement Item", {
        "Agreement Name": {"guid": "agreement"}, "Item Name": {"guid": "item"},
        "Agreement Item Id": {"value": "ITEM-2"}}),
        ("agreement", "item"), {"agreementItemId": "ITEM-2"},
        "_async_link_agreement_item", "_async_update_agreement_item"),
    Case("agreement-actor", _processor(CollectionLinkProcessor, "Link", "Agreement Actor", {
        "Agreement Name": {"guid": "agreement"}, "Actors": {"guid": "actor"},
        "Actor Name": {"value": "buyer"}}),
        ("agreement", "actor"), {"actorRole": "buyer"},
        "_async_link_agreement_actor", None),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", CASES, ids=[c.id for c in CASES])
async def test_rerun_targets_existing_relationship(case):
    client = RecordingClient([relationship(EXISTING_GUID, *case.ends, case.key)])

    await case.make(client).apply_changes()

    assert client.called(case.create) == [], "re-run must not create a duplicate"
    if case.update:
        assert [args[0] for args in client.called(case.update)] == [EXISTING_GUID]
        update_body = client.called(case.update)[0][1]
        assert update_body["class"] == "UpdateRelationshipRequestBody"
        assert update_body["mergeUpdate"] is True


@pytest.mark.asyncio
@pytest.mark.parametrize("case", CASES, ids=[c.id for c in CASES])
async def test_different_identity_creates_new_relationship(case):
    other_key = {k: f"OTHER-{v}" for k, v in case.key.items()}
    client = RecordingClient([relationship(EXISTING_GUID, *case.ends, other_key)])

    await case.make(client).apply_changes()

    assert len(client.called(case.create)) == 1
    if case.update:
        assert client.called(case.update) == []


@pytest.mark.asyncio
@pytest.mark.parametrize("case", [c for c in CASES if c.id in ("certification", "license")],
                         ids=["certification", "license"])
async def test_certification_and_license_match_in_type_def_end_order(case):
    reversed_ends = tuple(reversed(case.ends))
    client = RecordingClient([relationship(EXISTING_GUID, *reversed_ends, case.key)])

    await case.make(client).apply_changes()

    assert len(client.called(case.create)) == 1


class _FailingLookupClient(RecordingClient):
    async def _async_find_relationships_between_elements(self, body):
        raise RuntimeError("server unavailable")


@pytest.mark.asyncio
async def test_failed_lookup_falls_back_to_create():
    client = _FailingLookupClient()

    guid, created = await async_link_or_update(
        client, "DataFlow", "a", "b", {"label": "x"},
        create=lambda: client._async_link_data_flow("a", "DataFlow", "b", {}),
        update=lambda g: client._async_update_lineage(g, {}))

    assert (guid, created) == (NEW_GUID, True)


@pytest.mark.asyncio
async def test_explicit_guid_skips_lookup():
    client = _FailingLookupClient()

    guid, created = await async_link_or_update(
        client, "DataFlow", "a", "b", {"label": "x"},
        create=lambda: client._async_link_data_flow("a", "DataFlow", "b", {}),
        update=lambda g: client._async_update_lineage(g, {}),
        explicit_guid="given-guid")

    assert (guid, created) == ("given-guid", False)
    assert [args[0] for args in client.called("_async_update_lineage")] == ["given-guid"]


@pytest.mark.asyncio
async def test_unlink_saved_query_finds_relationship_in_real_envelope():
    client = RecordingClient([relationship(EXISTING_GUID, "results-set", "saved-query", {})])
    make = _processor(SmartQueryLinkProcessor, "Unlink", "Saved Query to Results Set", {
        "Results Set": {"guid": "results-set"}, "Saved Query": {"guid": "saved-query"}})

    await make(client).apply_changes()

    assert client.called("_async_detach_saved_query_from_results_set") == [(EXISTING_GUID,)]


@pytest.mark.asyncio
async def test_unlink_saved_query_without_relationship_raises():
    client = RecordingClient()
    make = _processor(SmartQueryLinkProcessor, "Unlink", "Saved Query to Results Set", {
        "Results Set": {"guid": "results-set"}, "Saved Query": {"guid": "saved-query"}})

    with pytest.raises(ValueError, match="No SmartQuery relationship found"):
        await make(client).apply_changes()


class _PagingProbe:
    platform_url = "https://fake:9443"
    view_server = "fake-view"

    def __init__(self):
        self.sent = None

    async def _async_make_request(self, method, url, body, timeout=None):
        self.sent = body

        class _Response:
            @staticmethod
            def json():
                return {"relationshipList": {"relationships": []}}
        return _Response()


@pytest.mark.asyncio
async def test_find_relationships_sends_paging_in_body():
    probe = _PagingProbe()
    caller_body = {"class": "FindRelationshipRequestBody", "relationshipTypeName": "DataFlow"}

    await MetadataExpert._async_find_relationships_between_elements(
        cast(Any, probe), caller_body, start_from=10, page_size=5, for_lineage=True)

    assert probe.sent["startFrom"] == 10
    assert probe.sent["pageSize"] == 5
    assert probe.sent["forLineage"] is True
    assert "startFrom" not in caller_body


@pytest.mark.asyncio
async def test_find_relationships_default_leaves_page_size_to_server():
    probe = _PagingProbe()

    await MetadataExpert._async_find_relationships_between_elements(
        cast(Any, probe), {"class": "FindRelationshipRequestBody", "pageSize": 50})

    assert "startFrom" not in probe.sent
    assert probe.sent["pageSize"] == 50
