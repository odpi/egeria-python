# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
ISSUE-113: Egeria removed `initialStatus` from new-element requests, so Dr.Egeria
must put a status in the property each type actually has -- contentStatus,
activityStatus, deploymentStatus -- or nowhere, for types with none.
"""
from md_processing.md_processing_utils.common_md_utils import set_create_body, set_element_prop_body
from md_processing.md_processing_utils.element_status import element_status_properties


def _attrs(**kv):
    out = {}
    for k, v in kv.items():
        name = k.replace("_", " ")
        out[name] = v if isinstance(v, dict) else {"value": v}
    return out


def test_written_status_goes_to_content_status_for_authored_content():
    assert element_status_properties("GlossaryTermProperties", _attrs(Status="DRAFT")) == {"contentStatus": "DRAFT"}


def test_written_status_goes_to_activity_status_for_actions():
    assert element_status_properties("ToDoProperties", _attrs(Status="IN_PROGRESS")) == {
        "activityStatus": "IN_PROGRESS"}


def test_written_status_goes_to_deployment_status_for_infrastructure():
    assert element_status_properties("SoftwareServerProperties", _attrs(Status="STANDBY")) == {
        "deploymentStatus": "STANDBY"}


def test_type_with_two_fields_takes_the_first_that_accepts_the_value():
    # SolutionComponent has contentStatus and deploymentStatus; DRAFT is only a content value.
    assert element_status_properties("SolutionComponentProperties", _attrs(Status="DRAFT")) == {
        "contentStatus": "DRAFT"}
    assert element_status_properties("SolutionComponentProperties", _attrs(Status="UNDER_DEVELOPMENT")) == {
        "deploymentStatus": "UNDER_DEVELOPMENT"}


def test_type_without_a_status_gets_none():
    assert element_status_properties("ActorProfileProperties", _attrs(Status="DRAFT")) == {}
    assert element_status_properties("AssetProperties", _attrs(Content_Status="DRAFT")) == {}


def test_value_invalid_for_the_type_is_dropped():
    assert element_status_properties("ToDoProperties", _attrs(Status="DRAFT")) == {}


def test_explicit_attribute_wins_over_generic_status():
    attrs = _attrs(Status="ACTIVE", Content_Status="PROPOSED")
    assert element_status_properties("GlossaryTermProperties", attrs) == {"contentStatus": "PROPOSED"}


def test_default_status_only_ever_sets_content_status():
    default = {"Status": {"value": "ACTIVE", "is_default": True}}
    assert element_status_properties("GlossaryTermProperties", default) == {"contentStatus": "ACTIVE"}
    # ACTIVE is a valid deployment status, but a default must not start overwriting it.
    assert element_status_properties("SoftwareServerProperties", default) == {}


def test_written_status_beats_a_defaulted_content_status():
    # What `dr_egeria --validate` showed: Content Status carries its own spec default of ACTIVE.
    attrs = {"Status": {"value": "DRAFT"}, "Content Status": {"value": "ACTIVE", "is_default": True}}
    assert element_status_properties("DataStructureProperties", attrs) == {"contentStatus": "DRAFT"}


def test_written_status_reaches_deployment_status_past_a_defaulted_content_status():
    attrs = {"Status": {"value": "UNDER_DEVELOPMENT"}, "Content Status": {"value": "ACTIVE", "is_default": True}}
    assert element_status_properties("SolutionComponentProperties", attrs) == {
        "deploymentStatus": "UNDER_DEVELOPMENT", "contentStatus": "ACTIVE"}


def test_unknown_properties_class_keeps_old_behaviour():
    attrs = _attrs(Status="DRAFT", Activity_Status="WAITING")
    assert element_status_properties("NoSuchThingProperties", attrs) == {
        "contentStatus": "DRAFT", "activityStatus": "WAITING"}


def test_set_element_prop_body_uses_the_mapping():
    term = set_element_prop_body("Glossary Term", "qn", _attrs(Status="DRAFT"))
    assert term["contentStatus"] == "DRAFT"
    todo = set_element_prop_body("To Do", "qn", _attrs(Status="COMPLETED"))
    assert todo["class"] == "ToDoProperties"
    assert todo["activityStatus"] == "COMPLETED" and "contentStatus" not in todo
    actor = set_element_prop_body("Actor Profile", "qn", _attrs(Status="DRAFT"))
    assert "contentStatus" not in actor


def test_create_body_no_longer_sends_initial_status():
    assert "initialStatus" not in set_create_body("Glossary Term", _attrs(Status="DRAFT"))


async def test_template_create_no_longer_sends_initial_status():
    from typing import Any, cast

    from md_processing.v2.asset_maker import AssetMakerProcessor
    from md_processing.v2.extraction import DrECommand

    bodies = []

    class _Curation:
        async def _async_create_elem_from_template(self, body):
            bodies.append(body)
            return "cccccccc-0000-0000-0000-000000000003"

    class _Client:
        automated_curation = _Curation()

    async def _rendered(guid):
        return guid

    p = AssetMakerProcessor(client=cast(Any, _Client()),
                            command=DrECommand(verb="Create", object_type="Element", attributes={},
                                               raw_block="## Create Element"), context={})
    p.get_command_spec = lambda: {}
    p.parsed_output = {"qualified_name": None, "attributes": {
        "Template GUID": {"value": "3f9a0ab3-072c-4cb1-a14f-6e0492e00dd7"}, "Initial Status": {"value": "DRAFT"}}}
    p.render_result_markdown = _rendered

    await p.apply_changes()

    assert "initialStatus" not in bodies[0]
