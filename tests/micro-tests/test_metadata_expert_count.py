# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Unit tests for MetadataExpert.count_metadata_elements /
count_relationships_between_elements (Egeria native instance counting, PR odpi/egeria#9168).

No live server: `_async_make_request` is mocked to return a CountResponse. Verifies
the endpoint URL, POST method, body slimming, asOfTime pass-through, and count parsing.
"""
from unittest.mock import MagicMock

from pyegeria.omvs.metadata_expert import MetadataExpert


def _client():
    return MetadataExpert(view_server="vs", platform_url="https://localhost:9443",
                          user_id="u", user_pwd="p")


def _mock_request(capture, count_payload):
    async def fake(method, url, body=None, **kwargs):
        capture["method"] = method
        capture["url"] = url
        capture["body"] = body
        resp = MagicMock()
        resp.json = MagicMock(return_value=count_payload)
        return resp
    return fake


async def test_count_metadata_elements_url_and_count():
    me = _client()
    cap = {}
    me._async_make_request = _mock_request(cap, {"class": "CountResponse", "count": 42})
    body = {"class": "FindRequestBody", "metadataElementTypeName": "Asset",
            "limitResultsByStatus": ["ACTIVE"], "asOfTime": "2026-03-25T00:00:00+00:00",
            "empty": None}
    n = await me._async_count_metadata_elements(body)
    assert n == 42
    assert cap["method"] == "POST"
    assert cap["url"].endswith("/metadata-expert/metadata-elements/by-search-conditions/count")
    # body_slimmer drops the None-valued key but keeps asOfTime
    assert "empty" not in cap["body"]
    assert cap["body"]["asOfTime"] == "2026-03-25T00:00:00+00:00"
    assert cap["body"]["metadataElementTypeName"] == "Asset"


async def test_count_relationships_url_and_count():
    me = _client()
    cap = {}
    me._async_make_request = _mock_request(cap, {"class": "CountResponse", "count": 7})
    body = {"class": "FindRelationshipRequestBody", "relationshipTypeName": "Certification"}
    n = await me._async_count_relationships_between_elements(body)
    assert n == 7
    assert cap["method"] == "POST"
    assert cap["url"].endswith("/metadata-expert/relationships/by-search-conditions/count")
    assert cap["body"]["relationshipTypeName"] == "Certification"


async def test_count_defaults_to_zero_when_absent():
    me = _client()
    cap = {}
    me._async_make_request = _mock_request(cap, {"class": "CountResponse"})   # no count field
    n = await me._async_count_metadata_elements({"class": "FindRequestBody"})
    assert n == 0


def test_sync_wrappers_delegate_to_async():
    # Sync wrappers should run the async coroutine and return the int.
    me = _client()
    cap = {}
    me._async_make_request = _mock_request(cap, {"count": 5})
    assert me.count_metadata_elements({"class": "FindRequestBody"}) == 5
    assert me.count_relationships_between_elements({"class": "FindRelationshipRequestBody"}) == 5
