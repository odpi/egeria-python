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


# Shape taken from a live getStatementOfApplicabilityByGUID response (6.3).
def _rel(rel_type, control_guid, control_props, rel_props):
    return {
        "class": "RelatedMetadataElementSummary",
        "relationshipHeader": {"guid": f"rel-{control_guid}", "type": {"typeName": rel_type}},
        "relationshipProperties": {"class": f"{rel_type}Properties", "typeName": rel_type, **rel_props},
        "relatedElement": {"elementHeader": {"guid": control_guid, "type": {"typeName": "GovernanceControl"}},
                           "properties": control_props},
    }


SOA_WITH_CONTROLS = {
    "elementHeader": {"guid": "soa-guid", "type": {"typeName": "StatementOfApplicability"}},
    "properties": SOA_PROPS,
    "otherRelatedElements": [
        _rel("ControlApplicability", "c-825", {"displayName": "Secure development", "description": "Control text"},
             {"label": "8.25", "implementationStatus": "PLANNED"}),
        _rel("ControlApplicability", "c-820", {"displayName": "Network security"},
             {"label": "8.20", "description": "Plant network first", "isApplicable": True,
              "implementationStatus": "IMPLEMENTED"}),
        _rel("ControlApplicability", "c-501", {"displayName": "Policies"},
             {"label": "5.1", "isApplicable": False, "justification": "Covered by group policy"}),
        _rel("ControlApplicability", "c-600", {"displayName": "Screening"}, {"label": "6.1"}),
        _rel("SomethingElse", "x-1", {"displayName": "Not a control"}, {}),
    ],
}


def test_control_applicability_rows_flatten_one_row_per_control():
    rows = SecurityOfficer._control_applicability_rows(SOA_WITH_CONTROLS)

    assert [r["properties"]["label"] for r in rows] == ["5.1", "6.1", "8.20", "8.25"]
    by_label = {r["properties"]["label"]: r for r in rows}
    # The relationship description becomes notes; the control's own description is kept.
    assert by_label["8.20"]["properties"]["notes"] == "Plant network first"
    assert by_label["8.25"]["properties"]["description"] == "Control text"
    # Unset isApplicable reads as applicable, as Egeria treats it.
    assert by_label["6.1"]["properties"]["isApplicable"] is True
    assert by_label["5.1"]["properties"]["isApplicable"] is False
    assert by_label["8.20"]["elementHeader"]["guid"] == "c-820"
    assert "typeName" not in by_label["8.20"]["properties"]


@pytest.mark.asyncio
async def test_control_implementation_summary_counts_applicable_controls(monkeypatch):
    calls: list = []
    client = _security_officer(calls, monkeypatch,
                               {"class": "OpenMetadataRootElementResponse", "element": SOA_WITH_CONTROLS})

    summary = await client._async_get_control_implementation_summary("8f7e6a1c-1111-4222-8333-944455556666")

    # Every status is present, so zeros are real counts; 6.1 has no status and counts as NOT_STARTED.
    assert summary["byStatus"] == {"NOT_STARTED": 1, "PLANNED": 1, "PARTIALLY_IMPLEMENTED": 0,
                                   "IMPLEMENTED": 1, "OTHER": 0}
    assert summary["applicable"] == 3
    assert summary["notApplicable"] == 1


@pytest.mark.asyncio
async def test_statement_of_applicability_controls_accepts_qualified_name(monkeypatch):
    calls: list = []
    client = _security_officer(calls, monkeypatch)
    responses = iter([
        {"class": "OpenMetadataRootElementsResponse", "elements": [SOA_WITH_CONTROLS]},
        {"class": "OpenMetadataRootElementResponse", "element": SOA_WITH_CONTROLS},
    ])

    async def fake_make_request(method, url, payload_body=None, *args, **kwargs):
        calls.append(url)
        return _Response(next(responses))

    client._async_make_request = fake_make_request

    rows = await client._async_get_statement_of_applicability_controls("StatementOfApplicability::Coco ISMS")

    assert calls[0].endswith(f"{ROOT}/by-name")
    assert calls[1].endswith(f"{ROOT}/soa-guid/retrieve")
    assert len(rows) == 4
