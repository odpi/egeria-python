# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Multi-link GUID display for GovernanceLinkProcessor's Certification / License /
Agreement T&C create paths (ISSUE-68 follow-up).

Certification, License, and AgreementItem are all MULTI_LINK relationship
types (see pyegeria.core.relationship_multiplicity) -- more than one
instance can exist between the same pair of elements, and
GovernanceLinkProcessor's own Detach branch already requires the
relationship GUID (_resolve_relationship_guid raises ValueError without
it). But the create branch previously discarded the GUID that
_async_add_certification_to_element / _async_add_license_to_element /
_async_link_agreement_item return, falling through to a generic
"Operation completed." message -- leaving the user with no way to get the
GUID they'll need for a later Update/Detach except a separate find. This
confirms the GUID is now captured into parsed_output["guid"] and shown in
the result markdown.

No live server needed: a fake client stands in for the OMVS layer.
"""
from typing import Any, cast

import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.governance import GovernanceLinkProcessor

CERT_REL_GUID = "cert-rel-guid-0001"
LICENSE_REL_GUID = "license-rel-guid-0001"


class _FakeClient:
    def __init__(self):
        self.certify_calls = []
        self.license_calls = []

    async def _async_add_certification_to_element(self, certification_type_guid, element_guid, body):
        self.certify_calls.append((certification_type_guid, element_guid, body))
        return CERT_REL_GUID

    async def _async_add_license_to_element(self, license_type_guid, element_guid, body):
        self.license_calls.append((license_type_guid, element_guid, body))
        return LICENSE_REL_GUID


def _command(verb: str, object_type: str) -> DrECommand:
    return DrECommand(verb=verb, object_type=object_type, attributes={},
                       raw_block=f"# {verb} {object_type}")


@pytest.mark.asyncio
async def test_create_certification_returns_and_displays_relationship_guid():
    client = _FakeClient()
    p = GovernanceLinkProcessor(client=cast(Any, client), command=_command("Link", "Certification"), context={})
    p.canonical_object_type = "Certification"
    p.get_command_spec = lambda: {"OM_TYPE": "Certification"}
    p.parsed_output = {
        "qualified_name": "Certification::test::1",
        "attributes": {
            "Certification Type": {"guid": "cert-type-guid"},
            "Referenceable": {"guid": "elem-guid"},
        },
    }

    result = await p.apply_changes()

    assert len(client.certify_calls) == 1
    assert client.certify_calls[0][0] == "cert-type-guid"
    assert client.certify_calls[0][1] == "elem-guid"
    assert p.parsed_output["guid"] == CERT_REL_GUID
    assert CERT_REL_GUID in result


@pytest.mark.asyncio
async def test_create_license_returns_and_displays_relationship_guid():
    client = _FakeClient()
    p = GovernanceLinkProcessor(client=cast(Any, client), command=_command("Link", "License"), context={})
    p.canonical_object_type = "License"
    p.get_command_spec = lambda: {"OM_TYPE": "License"}
    p.parsed_output = {
        "qualified_name": "License::test::1",
        "attributes": {
            "License Type": {"guid": "license-type-guid"},
            "Referenceable": {"guid": "elem-guid"},
        },
    }

    result = await p.apply_changes()

    assert len(client.license_calls) == 1
    assert client.license_calls[0][0] == "license-type-guid"
    assert client.license_calls[0][1] == "elem-guid"
    assert p.parsed_output["guid"] == LICENSE_REL_GUID
    assert LICENSE_REL_GUID in result
