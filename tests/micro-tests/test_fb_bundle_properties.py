# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""F-B group 5: the Referenceable/Authored/Asset bundle on processors that built partial bodies.

On the round-trip probe's PostgreSQL baseline, Data Class / Data Grain / Data Value Specification /
Measurement Specification / Informal Tag / Solution Role / Schema Type / Dashboard Sheet and the my-profile
creates dropped bundle attributes (Identifier, Category, Legal, URL, Version Identifier, Authors, Content
Status, Effective From/To, Namespace Path, Source, ...). Each is now sent where the type's Java class
declares it, or reported "not applied" where it doesn't -- never sent to be silently ignored.
"""
from typing import Any, cast

import pytest

from md_processing.md_processing_utils.common_md_utils import (
    complete_bundle_properties, person_action_extras, set_element_prop_body, set_solution_architect_body)
from md_processing.md_processing_utils.typed_properties import not_applied_notes
from md_processing.v2.data_designer import _data_spec_fields
from md_processing.v2.extraction import DrECommand
from md_processing.v2.feedback import FeedbackProcessor


def _attrs(**kv):
    return {k.replace("_", " "): {"value": v} for k, v in kv.items()}


def test_declared_bundle_keys_are_filled_and_processor_values_win():
    a = _attrs(Identifier="RTP id", Namespace_Path="RTP ns", Category="RTP cat", Status="DRAFT")
    props = complete_bundle_properties({"class": "DataValueSpecificationProperties", "category": "kept"}, a)
    assert props["identifier"] == "RTP id" and props["namespacePath"] == "RTP ns" and props["category"] == "kept"
    assert props["contentStatus"] == "DRAFT"
    assert not_applied_notes(a) == []


def test_undeclared_bundle_keys_are_stripped_and_reported():
    a = _attrs(Authors=["a"], User_Defined_Content_Status="u", Scope="sc")
    props = complete_bundle_properties({"class": "SolutionActorRoleProperties", "authors": ["a"],
                                        "userDefinedContentStatus": "u"}, a)
    assert "authors" not in props and "userDefinedContentStatus" not in props and props["scope"] == "sc"
    assert not_applied_notes(a) == [
        "not applied: Authors: SolutionActorRoleProperties has no authors property",
        "not applied: User Defined Content Status: SolutionActorRoleProperties has no userDefinedContentStatus property"]


def test_set_element_prop_body_completes_asset_fields():
    a = _attrs(Display_Name="RTP Report", Namespace_Path="RTP ns", Source="RTP src")
    props = set_element_prop_body("Report", "RTP::Report", a)
    assert props["namespacePath"] == "RTP ns" and props["source"] == "RTP src"


def test_solution_role_reports_its_missing_fields():
    a = _attrs(Display_Name="R", Role_Domain_Identifier="Data", Title="t", Content_Status="ACTIVE", Scope="sc")
    props = set_solution_architect_body("SolutionActorRole", "QN", a)
    assert "domainIdentifier" not in props and props["scope"] == "sc"
    notes = not_applied_notes(a)
    assert "not applied: Role Domain Identifier: SolutionActorRoleProperties has no domainIdentifier property" in notes
    assert "not applied: Title: SolutionActorRoleProperties has no title property" in notes
    assert "not applied: Content Status: SolutionActorRoleProperties has no contentStatus property" in notes


def test_data_spec_family_fields_and_coercions():
    a = _attrs(Data_Type="string", Units="kg", Match_Threshold="7", Absolute_Uncertainty="7.5",
               Name_Patterns="x", Identifier="id", Namespace_Path="ns")
    props = _data_spec_fields({"class": "DataGrainProperties"}, a)
    assert props["dataType"] == "string" and props["units"] == "kg" and props["matchThreshold"] == 7
    assert props["identifier"] == "id" and props["namespacePath"] == "ns" and "absoluteUncertainty" not in props
    notes = not_applied_notes(a)
    assert "not applied: Name Patterns: DataGrainProperties has no namePatterns property" in notes
    assert any(n.startswith("not applied: Absolute Uncertainty: '7.5' isn't a whole number") for n in notes)


def test_person_actions_get_effective_dates_and_objective_is_reported():
    a = _attrs(Effective_From="2020-01-02", Effective_To="2031-01-02", Objective="o")
    assert person_action_extras(a, "ToDoProperties") == {"effectiveFrom": "2020-01-02", "effectiveTo": "2031-01-02"}
    assert not_applied_notes(a) == ["not applied: Objective: ToDoProperties has no objective property"]
    b = _attrs(Objective="o")
    person_action_extras(b, "MeetingProperties")
    assert not_applied_notes(b) == []


class _MyProfile:
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        async def create(**kwargs):
            self.calls.append((name, kwargs))
            return "11831149-eed7-466a-9488-270d6164f442"
        return create


class _Client:
    def __init__(self):
        self.my_profile = _MyProfile()


@pytest.mark.asyncio
async def test_blog_entry_sends_a_full_typed_body():
    client = _Client()
    p = FeedbackProcessor(client=cast(Any, client), command=DrECommand(
        verb="Create", object_type="Blog Entry", attributes={}, raw_block="## Create Blog Entry"), context={})
    p.parsed_output = {"qualified_name": "RTP::Blog", "attributes": _attrs(
        Display_Name="RTP Blog", Description="text", Situation="RTP situation", Effective_From="2020-01-02",
        Identifier="RTP id")}

    async def render(guid):
        return guid
    p.render_result_markdown = render
    await p.apply_changes()
    props = client.my_profile.calls[0][1]["body"]["properties"]
    assert props["class"] == "BlogEntryProperties" and props["situation"] == "RTP situation"
    assert props["effectiveFrom"] == "2020-01-02" and props["identifier"] == "RTP id"
    assert props["qualifiedName"] == "RTP::Blog"
