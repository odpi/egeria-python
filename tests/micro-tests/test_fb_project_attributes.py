# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""F-B group 7: Project attributes go where Egeria keeps them (PROJECT-ATTRIBUTES-MAPPING-2026-11-12).

ProjectProperties (odpi/egeria origin/main 0b7ee0fb) has no projectIdentifier / purposes / projectType /
project{Approach,ManagementStyle,ResultsUsage}: all were sent and silently ignored.
- Project Identifier -> identifier (ReferenceableProperties);
- Approach / Management Style / Results Usage -> the ProjectClassification classification;
- Project Type -> its named classification (Campaign, Task, ...);
- Purposes (removed) -> reported with the owner's decision;
- Project Scope -> scope (ProjectProperties.scope, odpi/egeria #9448; the owner's 2026-11-15 decision replaced the
  2026-11-12 "no scope property" one).
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
    assert props["scope"] == "everything"
    assert not any("Project Scope" in n for n in notes)   # applied, so nothing to report


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


class _UpdateClient:
    def __init__(self):
        self.updates = []

    async def _async_update_project(self, project_guid, body):
        self.updates.append((project_guid, body))


async def _update(attributes):
    client = _UpdateClient()
    p = ProjectProcessor(client=cast(Any, client), command=DrECommand(
        verb="Update", object_type="Project", attributes={}, raw_block="## Update Project"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": "Project"}
    p.parsed_output = {"qualified_name": "RTP::Project", "guid": "3bd40b37-3d70-4caa-9733-91548ba0eee1",
                       "attributes": attributes}
    p.as_is_element = None
    p.render_result_markdown = lambda guid: _async_value(guid)

    async def no_subs(*a, **k):
        return {}
    p._sync_sub_projects = no_subs
    await p.apply_changes()
    return client.updates[0][1]


@pytest.mark.asyncio
async def test_project_scope_is_sent_on_update():
    body = await _update(_attrs(Display_Name="RTP Project", Project_Scope="in: the API; out: the UI"))
    assert body["properties"]["scope"] == "in: the API; out: the UI"
    assert "projectScope" not in body["properties"]


@pytest.mark.asyncio
async def test_project_scope_omitted_leaves_stored_scope_alone_on_merge_update():
    body = await _update(_attrs(Display_Name="RTP Project"))
    assert "scope" not in body["properties"]       # merge update drops None, so Egeria keeps what it has


def test_a_project_read_shows_scope():
    from pyegeria.view.output_formatter import _get_element_value
    from pyegeria.view.base_report_formats import get_report_registry
    element = {"elementHeader": {"guid": "g"}, "properties": {"displayName": "P", "scope": "in: the API"}}
    columns = [c for fs in get_report_registry().values() if fs.target_type == "Project"
               for f in fs.formats for c in f.attributes if c.name == "Project Scope"]
    assert columns, "no Project report spec lists Project Scope"
    assert {c.key for c in columns} == {"scope"}
    assert _get_element_value(element, columns[0].key) == "in: the API"
