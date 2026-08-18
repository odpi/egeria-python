# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
New Dr.Egeria "Update <relationship>" commands for MULTI_LINK types where the
OMVS layer's Update/Detach was already GUID-based but Dr.Egeria had no way to
target one specific instance for an update (ISSUE-68 follow-up).

Before this, `Update` was never auto-generated for a Link-family compact
command (build_command_variants' LINK_VERBS has no "Update"); the only
existing example was Lineage Linker's hand-added "Update Lineage
Relationship". This adds the same pattern for Certification, License, and
NextGovernanceActionProcessStep, since each already has a GUID-based OMVS
update endpoint and an existing Dr.Egeria Link/Detach command family.

No live server needed: fake clients capture the outgoing call.
"""
from typing import Any, cast

import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.governance import GovernanceLinkProcessor
from md_processing.v2.action_author import ActionProcessStepLinkProcessor


def _command(verb: str, object_type: str) -> DrECommand:
    return DrECommand(verb=verb, object_type=object_type, attributes={},
                       raw_block=f"# {verb} {object_type}")


class _FakeGovClient:
    def __init__(self):
        self.certify_update_calls = []
        self.license_update_calls = []

    async def _async_update_certification(self, rel_guid, body):
        self.certify_update_calls.append((rel_guid, body))

    async def _async_update_license(self, rel_guid, body):
        self.license_update_calls.append((rel_guid, body))


@pytest.mark.asyncio
async def test_update_certification_targets_relationship_guid():
    client = _FakeGovClient()
    p = GovernanceLinkProcessor(client=cast(Any, client), command=_command("Update", "Certification"), context={})
    p.canonical_object_type = "Certification"
    p.get_command_spec = lambda: {"OM_TYPE": "Certification"}
    p.parsed_output = {
        "qualified_name": "Certification::test::1",
        "attributes": {
            "Certificate GUID": {"value": "aaaaaaaa-0000-0000-0000-000000000001"},
            "Conditions": {"value": "renewed"},
        },
    }

    result = await p.apply_changes()

    assert len(client.certify_update_calls) == 1
    rel_guid, body = client.certify_update_calls[0]
    assert rel_guid == "aaaaaaaa-0000-0000-0000-000000000001"
    assert body["properties"]["conditions"] == "renewed"
    assert body["mergeUpdate"] is True
    assert "aaaaaaaa-0000-0000-0000-000000000001" in result


@pytest.mark.asyncio
async def test_update_certification_without_guid_raises():
    client = _FakeGovClient()
    p = GovernanceLinkProcessor(client=cast(Any, client), command=_command("Update", "Certification"), context={})
    p.canonical_object_type = "Certification"
    p.get_command_spec = lambda: {"OM_TYPE": "Certification"}
    p.parsed_output = {"qualified_name": "Certification::test::1", "attributes": {}}

    with pytest.raises(ValueError, match="requires the relationship GUID"):
        await p.apply_changes()


@pytest.mark.asyncio
async def test_update_license_targets_relationship_guid():
    client = _FakeGovClient()
    p = GovernanceLinkProcessor(client=cast(Any, client), command=_command("Update", "License"), context={})
    p.canonical_object_type = "License"
    p.get_command_spec = lambda: {"OM_TYPE": "License"}
    p.parsed_output = {
        "qualified_name": "License::test::1",
        "attributes": {
            "License GUID": {"value": "bbbbbbbb-0000-0000-0000-000000000002"},
            "Entitlements": {"value": "read-only"},
        },
    }

    result = await p.apply_changes()

    assert len(client.license_update_calls) == 1
    rel_guid, body = client.license_update_calls[0]
    assert rel_guid == "bbbbbbbb-0000-0000-0000-000000000002"
    assert body["properties"]["entitlements"] == "read-only"
    assert "bbbbbbbb-0000-0000-0000-000000000002" in result


class _FakeActionAuthorClient:
    def __init__(self):
        self.update_calls = []
        self.setup_calls = []

    async def _async_update_next_action_process_step(self, relationship_guid, body):
        self.update_calls.append((relationship_guid, body))

    async def _async_setup_next_action_process_step(self, step_guid, next_step_guid, body):
        self.setup_calls.append((step_guid, next_step_guid, body))
        return "cccccccc-0000-0000-0000-000000000003"


@pytest.mark.asyncio
async def test_update_next_process_step_targets_relationship_guid():
    client = _FakeActionAuthorClient()
    p = ActionProcessStepLinkProcessor(client=cast(Any, client), command=_command("Update", "Next Process Step"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": "NextGovernanceActionProcessStep"}
    p.parsed_output = {
        "qualified_name": "NextProcessStep::test::1",
        "attributes": {
            "GUID": {"value": "cccccccc-0000-0000-0000-000000000003"},
            "Guard": {"value": "SUCCESS"},
        },
    }

    result = await p.apply_changes()

    assert len(client.update_calls) == 1
    rel_guid, body = client.update_calls[0]
    assert rel_guid == "cccccccc-0000-0000-0000-000000000003"
    assert body["properties"]["guard"] == "SUCCESS"
    assert "cccccccc-0000-0000-0000-000000000003" in result


@pytest.mark.asyncio
async def test_update_next_process_step_without_guid_raises():
    client = _FakeActionAuthorClient()
    p = ActionProcessStepLinkProcessor(client=cast(Any, client), command=_command("Update", "Next Process Step"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": "NextGovernanceActionProcessStep"}
    p.parsed_output = {"qualified_name": "NextProcessStep::test::1", "attributes": {}}

    with pytest.raises(ValueError, match="no relationship GUID resolved"):
        await p.apply_changes()


@pytest.mark.asyncio
async def test_link_next_process_step_still_displays_new_relationship_guid():
    # Regression check for the Link-branch GUID-display fix made alongside
    # the new Update command (previously discarded the GUID
    # _async_setup_next_action_process_step now returns).
    client = _FakeActionAuthorClient()
    p = ActionProcessStepLinkProcessor(client=cast(Any, client), command=_command("Link", "Next Process Step"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": "NextGovernanceActionProcessStep"}
    p.parsed_output = {
        "qualified_name": "NextProcessStep::test::1",
        "attributes": {
            "Governance Action Process Step": {"guid": "step-1-guid"},
            "Next Governance Action Process Step": {"guid": "step-2-guid"},
        },
    }

    result = await p.apply_changes()

    assert len(client.setup_calls) == 1
    assert p.parsed_output["guid"] == "cccccccc-0000-0000-0000-000000000003"
    assert "cccccccc-0000-0000-0000-000000000003" in result
