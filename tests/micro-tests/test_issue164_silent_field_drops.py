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
