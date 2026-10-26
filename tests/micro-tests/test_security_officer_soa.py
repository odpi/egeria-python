"""
Statement of applicability methods on SecurityOfficer (Egeria 6.3), and the
delete_annotation body default on DataDiscovery.
No live server: the HTTP call is captured and the verb, URL and body asserted
against Egeria-api-security-officer.http and SecurityOfficerResource.java.
"""
import json

import pytest
from pydantic import ValidationError

from pyegeria.models import ControlApplicabilityProperties, ControlImplementationStatus
from pyegeria.omvs.data_discovery import DataDiscovery
from pyegeria.omvs.security_officer import SecurityOfficer


class _Response:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def _capture(client, calls: list, payload: dict | None = None):
    async def fake_make_request(method, url, payload_body=None, *args, **kwargs):
        calls.append({"method": method, "url": url,
                      "body": json.loads(payload_body) if isinstance(payload_body, str) else payload_body})
        return _Response(payload or {"class": "VoidResponse", "relatedHTTPCode": 200})

    client._async_make_request = fake_make_request
    return client


def _security_officer(calls, monkeypatch, payload=None):
    monkeypatch.setattr(SecurityOfficer, "check_connection", lambda self: "test")
    return _capture(SecurityOfficer("view-server", "https://localhost:1", "user", "pwd"), calls, payload)


ROOT = "/servers/view-server/api/open-metadata/security-officer/statements-of-applicability"

SOA_PROPS = {
    "class": "StatementOfApplicabilityProperties",
    "qualifiedName": "StatementOfApplicability::Coco Pharmaceuticals ISMS",
    "displayName": "Coco Pharmaceuticals ISMS",
    "versionIdentifier": "1.0",
    "scope": "Coco Pharmaceuticals ISMS",
    "reviewDate": "2026-10-26T00:00:00Z",
    "authors": ["Simon Burr"],
    "contentStatus": "DRAFT",
}

CA_PROPS = {
    "class": "ControlApplicabilityProperties",
    "isApplicable": True,
    "justification": "Ransomware disruption to manufacturing",
    "inclusionReasons": ["Risk Treatment"],
    "implementationStatus": "PARTIALLY_IMPLEMENTED",
    "implementationDescription": "Network segmentation in progress",
    "reviewDate": "2026-10-26T00:00:00Z",
    "label": "8.20",
    "description": "Network security",
}


@pytest.mark.asyncio
async def test_create_statement_of_applicability(monkeypatch):
    calls: list = []
    client = _security_officer(calls, monkeypatch, {"class": "GUIDResponse", "guid": "soa-guid"})

    guid = await client._async_create_statement_of_applicability(
        {"class": "NewElementRequestBody", "isOwnAnchor": True, "properties": SOA_PROPS})

    assert guid == "soa-guid"
    assert calls[0]["method"] == "POST"
    assert calls[0]["url"].endswith(ROOT)
    assert calls[0]["body"]["class"] == "NewElementRequestBody"
    # scope and reviewDate are new to this type: neither may be dropped on the way out
    assert calls[0]["body"]["properties"] == SOA_PROPS


@pytest.mark.asyncio
async def test_create_statement_of_applicability_from_template(monkeypatch):
    calls: list = []
    client = _security_officer(calls, monkeypatch, {"class": "GUIDResponse", "guid": "soa-guid"})

    guid = await client._async_create_statement_of_applicability_from_template(
        {"class": "TemplateRequestBody", "templateGUID": "template-guid"})

    assert guid == "soa-guid"
    assert calls[0]["url"].endswith(f"{ROOT}/from-template")
    assert calls[0]["body"]["class"] == "TemplateRequestBody"
    assert calls[0]["body"]["templateGUID"] == "template-guid"


@pytest.mark.asyncio
async def test_update_statement_of_applicability(monkeypatch):
    calls: list = []
    client = _security_officer(calls, monkeypatch)
    props = {"class": "StatementOfApplicabilityProperties", "contentStatus": "APPROVED",
             "reviewDate": "2026-11-01T00:00:00Z"}

    await client._async_update_statement_of_applicability(
        "soa-guid", {"class": "UpdateElementRequestBody", "mergeUpdate": True, "properties": props})

    assert calls[0]["url"].endswith(f"{ROOT}/soa-guid/update")
    assert calls[0]["body"]["class"] == "UpdateElementRequestBody"
    assert calls[0]["body"]["properties"] == props


@pytest.mark.asyncio
async def test_delete_statement_of_applicability_without_body(monkeypatch):
    calls: list = []
    client = _security_officer(calls, monkeypatch)

    await client._async_delete_statement_of_applicability("soa-guid")

    assert calls[0]["method"] == "POST"
    assert calls[0]["url"].endswith(f"{ROOT}/soa-guid/delete")


@pytest.mark.asyncio
async def test_get_statements_of_applicability_by_name(monkeypatch):
    calls: list = []
    client = _security_officer(calls, monkeypatch, {"class": "OpenMetadataRootElementsResponse", "elements": []})

    await client._async_get_statements_of_applicability_by_name("Coco Pharmaceuticals ISMS")

    assert calls[0]["url"].endswith(f"{ROOT}/by-name")
    assert calls[0]["body"]["class"] == "FilterRequestBody"
    assert calls[0]["body"]["filter"] == "Coco Pharmaceuticals ISMS"


@pytest.mark.asyncio
async def test_find_statements_of_applicability(monkeypatch):
    calls: list = []
    client = _security_officer(calls, monkeypatch, {"class": "OpenMetadataRootElementsResponse", "elements": []})

    await client._async_find_statements_of_applicability("ISMS")

    assert calls[0]["url"].endswith(f"{ROOT}/by-search-string")
    assert calls[0]["body"]["class"] == "SearchStringRequestBody"
    assert calls[0]["body"]["searchString"] == "ISMS"


@pytest.mark.asyncio
async def test_get_statement_of_applicability_by_guid(monkeypatch):
    calls: list = []
    element = {"elementHeader": {"guid": "soa-guid", "type": {"typeName": "StatementOfApplicability"}},
               "properties": SOA_PROPS}
    client = _security_officer(calls, monkeypatch, {"class": "OpenMetadataRootElementResponse", "element": element})

    result = await client._async_get_statement_of_applicability_by_guid("soa-guid")

    assert calls[0]["url"].endswith(f"{ROOT}/soa-guid/retrieve")
    assert calls[0]["body"]["class"] == "GetRequestBody"
    assert result["properties"]["scope"] == SOA_PROPS["scope"]


@pytest.mark.asyncio
async def test_link_control_applicability(monkeypatch):
    calls: list = []
    client = _security_officer(calls, monkeypatch)

    await client._async_link_control_applicability(
        "soa-guid", "control-guid", {"class": "NewRelationshipRequestBody", "properties": CA_PROPS})

    assert calls[0]["method"] == "POST"
    assert calls[0]["url"].endswith(f"{ROOT}/soa-guid/control-applicability/control-guid/attach")
    assert calls[0]["body"]["class"] == "NewRelationshipRequestBody"
    assert calls[0]["body"]["properties"] == CA_PROPS


@pytest.mark.asyncio
async def test_link_control_applicability_without_body_sends_properties_class(monkeypatch):
    calls: list = []
    client = _security_officer(calls, monkeypatch)

    await client._async_link_control_applicability("soa-guid", "control-guid")

    assert calls[0]["body"]["properties"]["class"] == "ControlApplicabilityProperties"


@pytest.mark.asyncio
async def test_detach_control_applicability(monkeypatch):
    calls: list = []
    client = _security_officer(calls, monkeypatch)

    await client._async_detach_control_applicability(
        "soa-guid", "control-guid", {"class": "DeleteRelationshipRequestBody", "externalSourceGUID": "src"})

    assert calls[0]["url"].endswith(f"{ROOT}/soa-guid/control-applicability/control-guid/detach")
    assert calls[0]["body"]["class"] == "DeleteRelationshipRequestBody"


def test_control_applicability_model_serializes_egeria_field_names():
    props = ControlApplicabilityProperties(**CA_PROPS)

    assert props.implementation_status == ControlImplementationStatus.PARTIALLY_IMPLEMENTED
    dumped = json.loads(props.model_dump_json(by_alias=True, exclude_none=True))
    assert dumped == CA_PROPS


def test_control_applicability_model_rejects_unknown_implementation_status():
    with pytest.raises(ValidationError):
        ControlApplicabilityProperties(**{**CA_PROPS, "implementationStatus": "DONE"})


@pytest.mark.asyncio
async def test_delete_annotation_body_is_optional(monkeypatch):
    calls: list = []
    monkeypatch.setattr(DataDiscovery, "check_connection", lambda self: "test")
    client = _capture(DataDiscovery("view-server", "https://localhost:1", "user", "pwd"), calls)

    await client._async_delete_annotation("annotation-guid")

    assert calls[0]["method"] == "POST"
    assert calls[0]["url"].endswith("/data-discovery/annotations/annotation-guid/delete")
