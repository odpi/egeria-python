"""
Automation family (md_processing/v2/automation.py) through the real dispatcher
with a fake client, plus the AutomatedCuration request-body fixes it relies on.
"""
import json
from typing import Any, Dict, List

import pytest

from pyegeria import NO_ELEMENTS_FOUND
from pyegeria.omvs.automated_curation import AutomatedCuration

from md_processing.dr_egeria import setup_dispatcher
from md_processing.v2.extraction import DrECommand

ELEMENTS = {
    # name -> (guid, element json)
    "Egeria::DailyGovernanceActionProcess": ("gap-1", {"properties": {"qualifiedName": "Egeria::DailyGovernanceActionProcess"}}),
    "PostgreSQLSurvey::survey-postgres-database": ("gat-1", {"properties": {"qualifiedName": "PostgreSQLSurvey::survey-postgres-database"}}),
    "Sales Database": ("db-1", {"properties": {"qualifiedName": "PostgreSQLDatabase::sales"}}),
    "Erin": ("person-1", {"properties": {"qualifiedName": "Person::Erin"}}),
    "Landing Table": ("asset-1", {"properties": {"qualifiedName": "Table::landing"}}),
    "ProvisioningActionProcess::Ref Data::Create Subscription::EVALUATION-SUBSCRIPTION":
        ("sub-type-1", {"properties": {"qualifiedName": "ProvisioningActionProcess::Ref Data::Create Subscription::EVALUATION-SUBSCRIPTION"}}),
    "Subscription::with-cancel": ("subscription-1", {
        "properties": {"qualifiedName": "Subscription::with-cancel"},
        "resourceList": [
            {"relationshipProperties": {"resourceUse": "Other"},
             "relatedElement": {"properties": {"qualifiedName": "Something::else"}}},
            {"relationshipProperties": {"resourceUse": "Cancel Subscription"},
             "relatedElement": {"properties": {"qualifiedName": "DeletingActionProcess::cancellingGovernanceActionType::subscription-1"}}},
        ]}),
    "Subscription::without-cancel": ("subscription-2", {"properties": {"qualifiedName": "Subscription::without-cancel"}}),
}
BY_GUID = {guid: element for guid, element in ELEMENTS.values()}


class _Response:
    def __init__(self, body):
        self._body = body

    def json(self):
        return self._body


class _FakeClassificationManager:
    platform_url = "https://egeria"
    view_server = "view"

    async def _async_make_request(self, method, url, body=None):
        return _Response({"element": BY_GUID[url.rsplit("/", 1)[-1]]})


class _FakeClient:
    def __init__(self):
        self.calls: List[tuple] = []
        self.classification_manager = _FakeClassificationManager()

    async def __async_get_guid__(self, qualified_name=None, display_name=None, property_name="qualifiedName",
                                 tech_type=None, **kwargs):
        entry = ELEMENTS.get(qualified_name or display_name)
        return entry[0] if entry else NO_ELEMENTS_FOUND

    async def _async_initiate_gov_action_process(self, *args, **kwargs):
        self.calls.append(("process", args, kwargs))
        return "process-instance-1"

    async def _async_initiate_gov_action_type(self, *args, **kwargs):
        self.calls.append(("type", args, kwargs))
        return "engine-action-1"

    async def _async_initiate_survey(self, *args, **kwargs):
        self.calls.append(("survey", args, kwargs))
        return "engine-action-2"


def _cmd(verb: str, object_type: str, attributes: Dict[str, Any]) -> DrECommand:
    raw = f"## {verb} {object_type}\n" + "".join(f"### {k}\n{v}\n" for k, v in attributes.items())
    return DrECommand(verb=verb, object_type=object_type, attributes=attributes, raw_block=raw)


async def _run(command: DrECommand):
    client = _FakeClient()
    results = await setup_dispatcher(client).dispatch_batch([command], {"directive": "process"})
    return results[0], client.calls


@pytest.mark.asyncio
async def test_initiate_governance_action_process_with_action_targets():
    result, calls = await _run(_cmd("Initiate", "Governance Action Process", {
        "Governance Action Process": "Egeria::DailyGovernanceActionProcess",
        "Action Targets": "databaseToCheck: Sales Database",
        "Request Parameters": "mode: full",
    }))
    assert result["status"] == "success", result
    [(kind, args, kwargs)] = calls
    assert kind == "process" and args == ("Egeria::DailyGovernanceActionProcess",)
    assert kwargs["action_targets"] == [{"class": "NewActionTarget", "actionTargetName": "databaseToCheck", "actionTargetGUID": "db-1"}]
    assert kwargs["request_parameters"] == {"mode": "full"}


@pytest.mark.asyncio
async def test_initiate_survey_leaves_target_name_to_the_sdk():
    result, calls = await _run(_cmd("Initiate", "Survey", {
        "Survey Type": "PostgreSQLSurvey::survey-postgres-database",
        "Resource to Survey": "Sales Database",
    }))
    assert result["status"] == "success", result
    [(kind, args, kwargs)] = calls
    assert kind == "survey" and args == ("PostgreSQLSurvey::survey-postgres-database", "db-1")
    assert kwargs["action_target_name"] is None


@pytest.mark.asyncio
async def test_initiate_subscription_runs_subscription_process():
    result, calls = await _run(_cmd("Initiate", "Subscription", {
        "Subscription Type": "ProvisioningActionProcess::Ref Data::Create Subscription::EVALUATION-SUBSCRIPTION",
        "Subscription Requester": "Erin",
        "Destination Data Set": "Landing Table",
    }))
    assert result["status"] == "success", result
    [(kind, args, kwargs)] = calls
    assert kind == "process"
    assert args == ("ProvisioningActionProcess::Ref Data::Create Subscription::EVALUATION-SUBSCRIPTION",)
    assert {t["actionTargetName"]: t["actionTargetGUID"] for t in kwargs["action_targets"]} == {
        "digitalSubscriptionRequester": "person-1", "destinationDataSet": "asset-1"}


@pytest.mark.asyncio
async def test_cancel_subscription_runs_its_cancel_process():
    result, calls = await _run(_cmd("Cancel", "Subscription", {"Digital Subscription": "Subscription::with-cancel"}))
    assert result["status"] == "success", result
    [(kind, args, _)] = calls
    assert kind == "process"
    assert args == ("DeletingActionProcess::cancellingGovernanceActionType::subscription-1",)


@pytest.mark.asyncio
async def test_cancel_subscription_without_cancel_process_fails_clearly():
    result, calls = await _run(_cmd("Cancel", "Subscription", {"Digital Subscription": "Subscription::without-cancel"}))
    assert result["status"] != "success"
    assert calls == []


# ---------------------------------------------------------------- SDK request bodies

def _curation(monkeypatch, supported: list) -> tuple:
    monkeypatch.setattr(AutomatedCuration, "check_connection", lambda self: "test")
    client = AutomatedCuration("view-server", "https://localhost:1", "user", "pwd")
    sent: list = []

    async def fake_make_request(method, url, body=None, *args, **kwargs):
        sent.append(json.loads(body) if isinstance(body, str) else body)
        return _Response({"guid": "g"})

    async def fake_supported(qualified_name):
        return supported

    client._async_make_request = fake_make_request
    client._async_get_supported_action_target_names = fake_supported
    return client, sent


@pytest.mark.asyncio
@pytest.mark.parametrize("supported, expected", [
    (["postgresDatabase"], "postgresDatabase"),   # read from the survey type
    (["*"], "serverToSurvey"),                    # any name accepted -> default
    ([], "serverToSurvey"),                       # lookup failed -> default
])
async def test_initiate_survey_action_target_name(monkeypatch, supported, expected):
    client, sent = _curation(monkeypatch, supported)
    await client._async_initiate_survey("PostgreSQLSurvey::survey-postgres-database", "db-1")
    assert sent[0]["actionTargets"][0]["actionTargetName"] == expected


@pytest.mark.asyncio
async def test_initiate_survey_explicit_target_name_wins(monkeypatch):
    client, sent = _curation(monkeypatch, ["postgresDatabase"])
    await client._async_initiate_survey("X::y", "db-1", action_target_name="custom")
    assert sent[0]["actionTargets"][0]["actionTargetName"] == "custom"


@pytest.mark.asyncio
async def test_initiate_bodies_use_egeria_field_names(monkeypatch):
    client, sent = _curation(monkeypatch, [])
    await client._async_initiate_gov_action_process("P::q", request_source_guids=["s1"])
    await client._async_initiate_gov_action_type("T::q", ["s1"], [])
    process_body, type_body = sent
    assert process_body["class"] == "InitiateGovernanceActionProcessRequestBody"
    assert process_body["actionSourceGUIDs"] == ["s1"] and "startDate" in process_body
    assert "requestSourceGUIDs" not in process_body and "startTime" not in process_body
    assert type_body["actionSourceGUIDs"] == ["s1"] and "requestSourceGUIDs" not in type_body
