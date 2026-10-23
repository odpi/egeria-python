"""
ISSUE-164: request fields that were silently dropped, either by pyegeria's own
models (extra='ignore') or by Egeria (ignoreUnknown=true), so the call
succeeded but ignored the option. Each test captures the body actually sent.
No live server.
"""
import json

import pytest

from pyegeria.omvs.project_manager import ProjectManager


class _Response:
    def json(self):
        return {"class": "GUIDResponse", "guid": "g", "elements": [], "relatedHTTPCode": 200}


def _client(cls, calls, monkeypatch):
    monkeypatch.setattr(cls, "check_connection", lambda self: "test")
    client = cls("view-server", "https://localhost:1", "user", "pwd")

    async def fake_make_request(method, url, payload=None, *args, **kwargs):
        calls.append({"url": url, "body": json.loads(payload) if isinstance(payload, str) else payload})
        return _Response()

    client._async_make_request = fake_make_request
    return client


# --- group 1: anchor scope, and the find helper's keys ------------------------

@pytest.mark.parametrize("key", ["anchorScopeGUIDs", "anchorScopeGuids", "anchor_scope_guids"])
def test_anchor_scope_is_sent_under_egerias_name_whichever_spelling_the_caller_uses(key):
    # Egeria's MakeAnchorOptions reads anchorScopeGUIDs. The documented spelling
    # used to be dropped client-side, and the model's own spelling server-side.
    from pyegeria.models import NewElementRequestBody, NewRelationshipRequestBody, TemplateRequestBody
    for model, extra in ((NewElementRequestBody, {}), (NewRelationshipRequestBody, {}),
                         (TemplateRequestBody, {"templateGUID": "t"})):
        sent = model.model_validate({"class": model.__name__, key: ["scope-1"], **extra}).model_dump(
            by_alias=True, exclude_none=True)
        assert sent["anchorScopeGUIDs"] == ["scope-1"]
        assert "anchorScopeGuids" not in sent


@pytest.mark.asyncio
async def test_find_forwards_zone_filter_relationship_page_size_and_anchor_scope(monkeypatch):
    calls: list = []
    client = _client(ProjectManager, calls, monkeypatch)

    # find_projects forwards these through **kwargs to the shared find helper
    await client._async_find_projects("clinical", governance_zone_filter=["quarantine"],
                                      relationship_page_size=7, anchor_scope_guid="scope-1")

    body = calls[0]["body"]
    assert body["class"] == "SearchStringRequestBody"
    assert body["searchString"] == "clinical"
    assert body["governanceZoneFilter"] == ["quarantine"]
    assert body["relationshipsPageSize"] == 7
    assert body["anchorScopeGUID"] == "scope-1"
    for dropped in ("zoneFilter", "relationshipPageSize", "anchorScopeGuid"):
        assert dropped not in body


@pytest.mark.asyncio
async def test_find_with_property_names_also_sends_zone_filter_and_paging(monkeypatch):
    calls: list = []
    client = _client(ProjectManager, calls, monkeypatch)

    await client._async_find_request(
        "https://localhost:1/x", _type="Project", _gen_output=None, search_string="clinical",
        property_names=["displayName"], governance_zone_filter=["quarantine"],
        relationship_page_size=7, anchor_scope_guid="scope-1", start_from=5, page_size=10)

    body = calls[0]["body"]
    assert body["class"] == "FindPropertyNamesProperties"
    assert body["propertyValue"] == "clinical"
    assert body["governanceZoneFilter"] == ["quarantine"]
    assert body["relationshipsPageSize"] == 7
    assert body["anchorScopeGUID"] == "scope-1"
    assert body["startFrom"] == 5


# --- group 2: always-400 calls and wrong class names --------------------------

@pytest.mark.asyncio
@pytest.mark.parametrize("method, args, expected", [
    # endpoint declares DeleteClassificationRequestBody (a sibling class is a 400)
    ("_async_remove_is_abstract_concept", ("term-guid",), "DeleteClassificationRequestBody"),
    ("_async_remove_activity_description",
     ("term-guid", {"class": "DeleteClassificationRequestBody", "forLineage": True}),
     "DeleteClassificationRequestBody"),
    # search keywords are elements: the endpoint declares DeleteElementRequestBody
    ("_async_remove_search_keyword", ("kw-guid",), "DeleteElementRequestBody"),
])
async def test_glossary_and_keyword_removals_send_the_declared_delete_class(monkeypatch, method, args, expected):
    from pyegeria.omvs.glossary_manager import GlossaryManager
    calls: list = []
    client = _client(GlossaryManager, calls, monkeypatch)
    await getattr(client, method)(*args)
    assert calls[0]["body"]["class"] == expected


@pytest.mark.asyncio
async def test_detach_cohort_member_no_longer_sends_a_metadata_source_body(monkeypatch):
    # The metadata-source helper always sent {"class": "MetadataSourceRequestBody"}, which
    # is not a registered DeleteRequestBody subtype, so every call was a 400.
    from pyegeria.omvs.runtime_manager import RuntimeManager
    calls: list = []
    client = _client(RuntimeManager, calls, monkeypatch)
    await client._async_detach_cohort_member("cohort-guid", "member-guid")
    assert calls[0]["url"].endswith("/metadata-repository-cohorts/cohort-guid/cohort-members/member-guid/detach")
    assert calls[0]["body"] is None
    await client._async_detach_cohort_member("cohort-guid", "member-guid",
                                             {"class": "DeleteRelationshipRequestBody", "forLineage": True})
    assert calls[1]["body"]["class"] == "DeleteRelationshipRequestBody"


@pytest.mark.asyncio
async def test_initiate_engine_action_uses_egerias_field_names(monkeypatch):
    # InitiateEngineActionRequestBody has actionSourceGUIDs and startDate; the old
    # requestSourceGUIDs / startTime were dropped, so a scheduled action started at once.
    from datetime import datetime
    from pyegeria.omvs.automated_curation import AutomatedCuration
    calls: list = []
    client = _client(AutomatedCuration, calls, monkeypatch)
    when = datetime(2030, 1, 2, 3, 4, 5)
    await client._async_initiate_engine_action(
        "engine", "qn::action", 0, "Action", "desc", ["source-guid"], [], [], start_time=when)
    body = calls[0]["body"]
    assert body["class"] == "InitiateEngineActionRequestBody"
    assert body["actionSourceGUIDs"] == ["source-guid"]
    assert body["startDate"] == int(when.timestamp() * 1000)
    assert "requestSourceGUIDs" not in body and "startTime" not in body


@pytest.mark.asyncio
async def test_add_is_data_value_default_class_is_the_one_the_handler_accepts(monkeypatch):
    # GlossaryManager's setTermAsDataValue checks `instanceof DataValueMeaningProperties`;
    # DataValueProperties is no registered subtype (a 400 when no body is given).
    from pyegeria.omvs.glossary_manager import GlossaryManager
    calls: list = []
    client = _client(GlossaryManager, calls, monkeypatch)
    await client._async_add_is_data_value("term-guid")
    assert calls[0]["body"]["properties"]["class"] == "DataValueMeaningProperties"


def test_solution_role_and_governance_purpose_use_registered_class_names():
    from pyegeria.models import NewElementRequestBody
    from pyegeria.omvs.governance_officer import GOV_DEF_PROPERTIES_LIST
    # create_solution_role posts to createActorRole, which takes ActorRoleProperties subtypes
    assert NewElementRequestBody.model_validate({
        "class": "NewElementRequestBody",
        "properties": {"class": "SolutionActorRoleProperties", "qualifiedName": "q"}})
    assert "DataProcessingPurposeProperties" in GOV_DEF_PROPERTIES_LIST
    assert "GovernanceProcessingPurposeProperties" not in GOV_DEF_PROPERTIES_LIST


# --- group 3: model gaps and Dr.Egeria / CLI keys ------------------------------

def test_action_request_body_carries_egerias_anchor_fields_and_new_action_targets():
    # My Profile sends isOwnAnchor for to-dos/meetings/reviews; the model lacked it, so
    # Pydantic dropped it. Egeria's field for targets is newActionTargets.
    from pyegeria.models import ActionRequestBody
    targets = [{"actionTargetName": "subject", "actionTargetGUID": "t-1"}]
    for key in ("newActionTargets", "actionTargetGUIDs"):
        sent = ActionRequestBody.model_validate({
            "class": "ActionRequestBody", "isOwnAnchor": True, "anchorGUID": "a-1",
            "anchorScopeGUIDs": ["s-1"], key: targets}).model_dump(by_alias=True, exclude_none=True)
        assert sent["isOwnAnchor"] is True
        assert sent["anchorGUID"] == "a-1"
        assert sent["anchorScopeGUIDs"] == ["s-1"]
        assert sent["newActionTargets"] == targets
        assert "actionTargetGUIDs" not in sent


def test_template_request_body_sends_replacement_classifications_and_parent_relationship_properties():
    from pyegeria.models import TemplateRequestBody
    cls = {"Confidentiality": {"class": "ConfidentialityProperties", "confidentialityLevel": 1}}
    rel = {"class": "CollectionMembershipProperties"}
    for key in ("initialClassifications", "replacementClassifications"):
        sent = TemplateRequestBody.model_validate({
            "class": "TemplateRequestBody", "templateGUID": "t", key: cls,
            "parentRelationshipProperties": rel}).model_dump(by_alias=True, exclude_none=True)
        assert sent["replacementClassifications"] == cls
        assert sent["parentRelationshipProperties"] == rel
        assert "initialClassifications" not in sent


def test_dr_egeria_find_create_update_bodies_use_keys_the_models_read():
    from md_processing.md_processing_utils.common_md_utils import set_create_body, set_find_body, set_update_body
    from pyegeria.models import NewElementRequestBody, SearchStringRequestBody

    find = set_find_body("Glossary Term", {"Search String": {"value": "x"}, "End With": {"value": True}})
    assert find["endsWith"] is True and "endWith" not in find
    assert SearchStringRequestBody.model_validate(find).ends_with is True

    create = set_create_body("Glossary Term", {"Anchor Scope ID": {"guid": "scope-1"}})
    # callers fill "properties" in afterwards (two-layer convention)
    assert NewElementRequestBody.model_validate({**create, "properties": None}).model_dump(
        by_alias=True, exclude_none=True)["anchorScopeGUIDs"] == ["scope-1"]
    # create/update bodies have no zone filter in Egeria
    assert "governanceZoneFilter" not in create
    assert "governanceZoneFilter" not in set_update_body("Glossary Term", {})
