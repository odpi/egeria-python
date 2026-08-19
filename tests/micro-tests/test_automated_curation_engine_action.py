# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Unit tests for AutomatedCuration._async_initiate_engine_action.

No live server: `_async_make_request` is mocked to capture the request. This is a
regression test for a real bug fixed in b17f71e -- the URL was missing the required
{governanceEngineName} path segment (confirmed against AutomatedCurationResource.java's
actual @PostMapping route: .../governance-engines/{governanceEngineName}/engine-actions/
initiate), so the method was unusable before the fix.
"""
from unittest.mock import MagicMock, patch

from pyegeria.omvs.automated_curation import AutomatedCuration


def _client():
    # BaseServerClient.__init__ does its own live connectivity probe
    # (check_connection()) before any mock can be installed, so
    # check_connection is patched out for the duration of client
    # construction -- otherwise this file would silently depend on a
    # reachable Egeria platform despite living in tests/micro-tests/.
    with patch("pyegeria.core._base_server_client.BaseServerClient.check_connection", return_value=""):
        return AutomatedCuration(view_server="vs", platform_url="https://localhost:9443",
                                  user_id="u", user_pwd="p")


def _mock_request(capture, payload):
    async def fake(method, url, body=None, **kwargs):
        capture["method"] = method
        capture["url"] = url
        capture["body"] = body
        resp = MagicMock()
        resp.json = MagicMock(return_value=payload)
        return resp
    return fake


async def test_initiate_engine_action_url_includes_governance_engine_name():
    ac = _client()
    cap = {}
    ac._async_make_request = _mock_request(cap, {"guid": "engine-action-guid"})

    guid = await ac._async_initiate_engine_action(
        governance_engine_name="AssetSurveyEngine",
        qualified_name="EngineAction:test",
        domain_identifier=0,
        display_name="Test Engine Action",
        description="A test",
        request_source_guids=[],
        action_targets=[],
        received_guards=[],
        request_type="survey-file-folder",
    )

    assert guid == "engine-action-guid"
    assert cap["method"] == "POST"
    assert cap["url"].endswith(
        "/automated-curation/governance-engines/AssetSurveyEngine/engine-actions/initiate"
    )


async def test_initiate_engine_action_body_shape():
    ac = _client()
    cap = {}
    ac._async_make_request = _mock_request(cap, {"guid": "engine-action-guid"})

    await ac._async_initiate_engine_action(
        governance_engine_name="AssetSurveyEngine",
        qualified_name="EngineAction:test",
        domain_identifier=0,
        display_name="Test Engine Action",
        description="A test",
        request_source_guids=["src-guid"],
        action_targets=[{"actionTargetName": "resource", "actionTargetGUID": "tgt-guid"}],
        received_guards=[],
        request_type="survey-file-folder",
        request_parameters={"key": "value"},
    )

    body = cap["body"]
    assert body["class"] == "GovernanceActionRequestBody"
    assert body["requestType"] == "survey-file-folder"
    assert body["requestSourceGUIDs"] == ["src-guid"]
    assert body["actionTargets"] == [{"actionTargetName": "resource", "actionTargetGUID": "tgt-guid"}]
    assert body["requestParameters"] == {"key": "value"}
    # qualifiedName has a timestamp suffix appended -- just confirm the prefix survives
    assert body["qualifiedName"].startswith("EngineAction:test")


async def test_initiate_engine_action_defaults_to_action_not_initiated():
    ac = _client()
    cap = {}
    ac._async_make_request = _mock_request(cap, {})  # no "guid" field
    guid = await ac._async_initiate_engine_action(
        governance_engine_name="AssetSurveyEngine",
        qualified_name="EngineAction:test",
        domain_identifier=0,
        display_name="Test Engine Action",
        description="A test",
        request_source_guids=[],
        action_targets=[],
        received_guards=[],
    )
    assert guid == "Action not initiated"


def test_initiate_engine_action_sync_wrapper_delegates_to_async():
    ac = _client()
    cap = {}
    ac._async_make_request = _mock_request(cap, {"guid": "engine-action-guid"})
    guid = ac.initiate_engine_action(
        governance_engine_name="AssetSurveyEngine",
        qualified_name="EngineAction:test",
        domain_identifier=0,
        display_name="Test Engine Action",
        description="A test",
        request_source_guids=[],
        action_targets=[],
        received_guards=[],
    )
    assert guid == "engine-action-guid"
    assert cap["url"].endswith(
        "/automated-curation/governance-engines/AssetSurveyEngine/engine-actions/initiate"
    )
