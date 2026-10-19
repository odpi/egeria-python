"""
ISSUE-156: AutomatedCuration.add/update_catalog_target posted a flat
"CatalogTargetRequestBody", a class Egeria does not have; the endpoints take
New/UpdateRelationshipRequestBody with CatalogTargetProperties.
ISSUE-157: set_gov_prop_body defaulted entitlements/obligations/restrictions
to [], which Egeria cannot read into its Map<String, String> fields, so
Create Service Level Objective was refused.
No live server: the HTTP call is captured and the body asserted.
"""
import json

import pytest

from pyegeria.omvs.automated_curation import AutomatedCuration
from md_processing.md_processing_utils.common_md_utils import set_gov_prop_body

CONNECTOR = "11111111-1111-1111-1111-111111111111"
ELEMENT = "22222222-2222-2222-2222-222222222222"
REL = "33333333-3333-3333-3333-333333333333"


class _Response:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def _client(calls: list, monkeypatch) -> AutomatedCuration:
    monkeypatch.setattr(AutomatedCuration, "check_connection", lambda self: "test")
    client = AutomatedCuration("view-server", "https://localhost:1", "user", "pwd")

    async def fake_make_request(method, url, payload_=None, *args, **kwargs):
        calls.append({"method": method, "url": url,
                      "body": json.loads(payload_) if isinstance(payload_, str) else payload_})
        return _Response({"class": "GUIDResponse", "guid": "rel-guid"})

    client._async_make_request = fake_make_request
    return client


@pytest.mark.asyncio
async def test_add_catalog_target_sends_new_relationship_request_body(monkeypatch):
    calls = []
    client = _client(calls, monkeypatch)
    guid = await client._async_add_catalog_target(
        CONNECTOR, ELEMENT, "target-1", connection_name="conn",
        config_properties={"a": "b"}, template_properties={"tmpl": "tmpl-guid"})

    assert guid == "rel-guid"
    call = calls[0]
    assert call["method"] == "POST"
    assert call["url"].endswith(
        f"/automated-curation/integration-connectors/{CONNECTOR}/catalog-targets/{ELEMENT}")
    body = call["body"]
    assert body["class"] == "NewRelationshipRequestBody"
    assert "catalogTargetName" not in body  # no flat properties at the top level
    assert body["properties"] == {
        "class": "CatalogTargetProperties",
        "catalogTargetName": "target-1",
        "connectionName": "conn",
        "configurationProperties": {"a": "b"},
        "templates": {"tmpl": "tmpl-guid"},
        "permittedSynchronization": "BOTH_DIRECTIONS",
        "deleteMethod": "ARCHIVE",
    }


@pytest.mark.asyncio
async def test_update_catalog_target_sends_update_relationship_request_body(monkeypatch):
    calls = []
    client = _client(calls, monkeypatch)
    await client._async_update_catalog_target(REL, "target-2", permitted_sync="FROM_THIRD_PARTY")

    call = calls[0]
    assert call["url"].endswith(f"/automated-curation/catalog-targets/{REL}/update")
    body = call["body"]
    assert body["class"] == "UpdateRelationshipRequestBody"
    assert body["properties"]["class"] == "CatalogTargetProperties"
    assert body["properties"]["catalogTargetName"] == "target-2"
    assert body["properties"]["permittedSynchronization"] == "FROM_THIRD_PARTY"
    assert "connectionName" not in body["properties"]


def _attrs(**values):
    return {k: {"value": v} for k, v in values.items()}


def test_service_level_objective_body_has_no_list_valued_map_fields():
    body = set_gov_prop_body("Service Level Objective", "SLO::pyeg-test",
                             _attrs(**{"Display Name": "Within an hour"}))
    for field in ("entitlements", "obligations", "restrictions"):
        assert body.get(field) is None, f"{field} must not default to a list"


def test_terms_and_conditions_maps_are_still_passed_through():
    body = set_gov_prop_body("Terms And Conditions", "TC::pyeg-test",
                             _attrs(**{"Display Name": "T&C", "Entitlements": {"read": "yes"}}))
    assert body["entitlements"] == {"read": "yes"}
    assert body.get("obligations") is None
