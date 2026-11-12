# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""F-B group 7: Project attributes go where Egeria keeps them (PROJECT-ATTRIBUTES-MAPPING-2026-11-12).

ProjectProperties (odpi/egeria origin/main 0b7ee0fb) has no projectIdentifier / purposes / projectType /
projectScope / project{Approach,ManagementStyle,ResultsUsage}: all were sent and silently ignored.
- Project Identifier -> identifier (ReferenceableProperties);
- Approach / Management Style / Results Usage -> the ProjectClassification classification;
- Project Type -> its named classification (Campaign, Task, ...);
- Purposes (removed) and Project Scope (no Egeria property) -> reported with the owner's decisions.
"""
from typing import Any, cast

import pytest

from md_processing.md_processing_utils.typed_properties import not_applied_notes
from md_processing.v2.extraction import DrECommand
from md_processing.v2.project import ProjectProcessor


class _Client:
    def __init__(self):
        self.bodies = []

    async def _async_create_project(self, body):
        self.bodies.append(body)
        return "3bd40b37-3d70-4caa-9733-91548ba0eee1"


async def _async_value(value):
    return value


def _attrs(**kv):
    return {k.replace("_", " "): {"value": v} for k, v in kv.items()}


async def _create(attributes, object_type="Project"):
    client = _Client()
    p = ProjectProcessor(client=cast(Any, client), command=DrECommand(
        verb="Create", object_type=object_type, attributes={}, raw_block=f"## Create {object_type}"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": "Project"}
    p.parsed_output = {"qualified_name": "RTP::Project", "attributes": attributes}
    p.as_is_element = None
    p.render_result_markdown = lambda guid: _async_value(guid)

    async def no_subs(*a, **k):
        return {}
    p._sync_sub_projects = no_subs
    await p.apply_changes()
    return client.bodies[0], attributes


@pytest.mark.asyncio
async def test_project_attributes_go_to_their_egeria_homes():
    body, attributes = await _create(_attrs(
        Display_Name="RTP Project", Project_Identifier="RTP-P-1", Project_Approach="agile",
        Project_Management_Style="lean", Project_Results_Usage="internal", Project_Type="Campaign",
        Purposes=["p1"], Project_Scope="everything"))
    props = body["properties"]
    for key in ("projectIdentifier", "purposes", "projectType", "projectScope", "projectApproach",
                "projectManagementStyle", "projectResultsUsage"):
        assert key not in props
    assert props["identifier"] == "RTP-P-1"
    classifications = body["initialClassifications"]
    assert classifications["ProjectClassification"] == {"class": "ProjectClassificationProperties",
                                                        "approach": "agile", "managementStyle": "lean",
                                                        "resultsUsage": "internal"}
    assert classifications["Campaign"] == {"class": "CampaignProperties"}
    notes = not_applied_notes(attributes)
    assert "not applied: Purposes: Project Purposes was removed (owner's decision, 2026-11-12)" in notes
    assert any(n.startswith("not applied: Project Scope: Project has no scope property in Egeria") for n in notes)


@pytest.mark.asyncio
async def test_unknown_project_type_is_reported():
    body, attributes = await _create(_attrs(Display_Name="RTP Project", Project_Type="Moonshot"))
    assert "Moonshot" not in body.get("initialClassifications", {})
    assert not_applied_notes(attributes) == [
        "not applied: Project Type: Moonshot isn't an Egeria project classification"]


@pytest.mark.asyncio
async def test_identifier_and_project_identifier_both_given():
    body, attributes = await _create(_attrs(Display_Name="RTP Project", Identifier="RTP-id",
                                            Project_Identifier="RTP-P-1"))
    assert body["properties"]["identifier"] == "RTP-id"
    assert not_applied_notes(attributes) == [
        "not applied: Project Identifier: Identifier is also given, and both are Egeria's identifier"]
