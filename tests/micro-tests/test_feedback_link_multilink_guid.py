# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Multi-link GUID handling for FeedbackLinkProcessor's External Reference /
Media Reference / Cited Document Link and Detach branches (ISSUE-73/74
follow-up).

ExternalReferenceLink, MediaReference, and CitedDocumentLink are all
MULTI_LINK relationship types (see pyegeria.core.relationship_multiplicity)
-- more than one instance can exist between the same pair of elements. This
processor's Link branches previously discarded the relationship GUID that
_async_link_external_reference / _async_link_media_reference /
_async_link_cited_document return (fixed under ISSUE-68 to return it), and
its Detach branches always used a pair-based call that removes every
matching relationship rather than one specific instance -- even though
GUID-targeted _by_id detach methods exist (added in PR #294). This confirms:
  - the create-time relationship GUID is now captured into
    parsed_output["guid"] and shown in the result markdown;
  - supplying an explicit "GUID" attribute on Detach routes to the
    relationship-GUID-targeted _by_id detach method for all three;
  - omitting it preserves the old pair-based fallback behavior.

No live server needed: a fake client stands in for the OMVS layer.
"""
from typing import Any, cast

import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.feedback import FeedbackLinkProcessor

EXT_REF_REL_GUID = "external-reference-rel-guid-0001"
MEDIA_REF_REL_GUID = "media-reference-rel-guid-0001"
CITED_DOC_REL_GUID = "cited-document-rel-guid-0001"


class _FakeClient:
    def __init__(self):
        self.link_external_reference_calls = []
        self.link_media_reference_calls = []
        self.link_cited_document_calls = []
        self.detach_external_reference_calls = []
        self.detach_external_reference_by_id_calls = []
        self.detach_media_reference_calls = []
        self.detach_media_reference_by_id_calls = []
        self.detach_cited_document_calls = []
        self.detach_cited_document_reference_by_id_calls = []

    async def _async_link_external_reference(self, elem_guid, ref_guid, body):
        self.link_external_reference_calls.append((elem_guid, ref_guid, body))
        return EXT_REF_REL_GUID

    async def _async_link_media_reference(self, elem_guid, ref_guid, body):
        self.link_media_reference_calls.append((elem_guid, ref_guid, body))
        return MEDIA_REF_REL_GUID

    async def _async_link_cited_document(self, elem_guid, ref_guid, body):
        self.link_cited_document_calls.append((elem_guid, ref_guid, body))
        return CITED_DOC_REL_GUID

    async def _async_detach_external_reference(self, elem_guid, ref_guid, body):
        self.detach_external_reference_calls.append((elem_guid, ref_guid, body))

    async def _async_detach_external_reference_by_id(self, rel_guid, body):
        self.detach_external_reference_by_id_calls.append((rel_guid, body))

    async def _async_detach_media_reference(self, elem_guid, ref_guid, body):
        self.detach_media_reference_calls.append((elem_guid, ref_guid, body))

    async def _async_detach_media_reference_by_id(self, rel_guid, body):
        self.detach_media_reference_by_id_calls.append((rel_guid, body))

    async def _async_detach_cited_document(self, elem_guid, ref_guid, body):
        self.detach_cited_document_calls.append((elem_guid, ref_guid, body))

    async def _async_detach_cited_document_reference_by_id(self, rel_guid, body):
        self.detach_cited_document_reference_by_id_calls.append((rel_guid, body))


def _command(verb: str, object_type: str) -> DrECommand:
    return DrECommand(verb=verb, object_type=object_type, attributes={},
                       raw_block=f"# {verb} {object_type}")


def _processor(client, verb, object_type, attributes):
    p = FeedbackLinkProcessor(client=cast(Any, client), command=_command(verb, object_type), context={})
    p.canonical_object_type = object_type
    p.parsed_output = {"qualified_name": f"{object_type}::test::1", "attributes": attributes}
    return p


@pytest.mark.asyncio
async def test_link_external_reference_returns_and_displays_relationship_guid():
    client = _FakeClient()
    p = _processor(client, "Link", "External Reference", {
        "Element Name": {"guid": "elem-guid"},
        "External Reference": {"guid": "ref-guid"},
    })

    result = await p.apply_changes()

    assert len(client.link_external_reference_calls) == 1
    assert p.parsed_output["guid"] == EXT_REF_REL_GUID
    assert EXT_REF_REL_GUID in result


@pytest.mark.asyncio
async def test_link_media_reference_returns_and_displays_relationship_guid():
    client = _FakeClient()
    p = _processor(client, "Link", "Media Reference", {
        "Element Name": {"guid": "elem-guid"},
        "Media Reference": {"guid": "ref-guid"},
    })

    result = await p.apply_changes()

    assert len(client.link_media_reference_calls) == 1
    assert p.parsed_output["guid"] == MEDIA_REF_REL_GUID
    assert MEDIA_REF_REL_GUID in result


@pytest.mark.asyncio
async def test_link_cited_document_returns_and_displays_relationship_guid():
    client = _FakeClient()
    p = _processor(client, "Link", "Cited Document", {
        "Element Name": {"guid": "elem-guid"},
        "Cited Document": {"guid": "ref-guid"},
    })

    result = await p.apply_changes()

    assert len(client.link_cited_document_calls) == 1
    assert p.parsed_output["guid"] == CITED_DOC_REL_GUID
    assert CITED_DOC_REL_GUID in result


@pytest.mark.asyncio
async def test_detach_external_reference_with_explicit_guid_uses_by_id():
    client = _FakeClient()
    p = _processor(client, "Detach", "External Reference", {
        "Element Name": {"guid": "elem-guid"},
        "External Reference": {"guid": "ref-guid"},
        "GUID": {"value": EXT_REF_REL_GUID},
    })

    await p.apply_changes()

    assert client.detach_external_reference_by_id_calls == [
        (EXT_REF_REL_GUID, client.detach_external_reference_by_id_calls[0][1])
    ]
    assert client.detach_external_reference_calls == []


@pytest.mark.asyncio
async def test_detach_external_reference_without_guid_falls_back_to_pair_based():
    client = _FakeClient()
    p = _processor(client, "Detach", "External Reference", {
        "Element Name": {"guid": "elem-guid"},
        "External Reference": {"guid": "ref-guid"},
    })

    await p.apply_changes()

    assert client.detach_external_reference_calls == [
        ("elem-guid", "ref-guid", client.detach_external_reference_calls[0][2])
    ]
    assert client.detach_external_reference_by_id_calls == []


@pytest.mark.asyncio
async def test_detach_media_reference_with_explicit_guid_uses_by_id():
    client = _FakeClient()
    p = _processor(client, "Detach", "Media Reference", {
        "Element Name": {"guid": "elem-guid"},
        "Media Reference": {"guid": "ref-guid"},
        "GUID": {"value": MEDIA_REF_REL_GUID},
    })

    await p.apply_changes()

    assert client.detach_media_reference_by_id_calls == [
        (MEDIA_REF_REL_GUID, client.detach_media_reference_by_id_calls[0][1])
    ]
    assert client.detach_media_reference_calls == []


@pytest.mark.asyncio
async def test_detach_cited_document_with_explicit_guid_uses_by_id():
    client = _FakeClient()
    p = _processor(client, "Detach", "Cited Document", {
        "Element Name": {"guid": "elem-guid"},
        "Cited Document": {"guid": "ref-guid"},
        "GUID": {"value": CITED_DOC_REL_GUID},
    })

    await p.apply_changes()

    assert client.detach_cited_document_reference_by_id_calls == [
        (CITED_DOC_REL_GUID, client.detach_cited_document_reference_by_id_calls[0][1])
    ]
    assert client.detach_cited_document_calls == []
