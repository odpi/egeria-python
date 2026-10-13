# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
ISSUE-129: MetadataExpert's related-elements/type and linked-by-* queries took
start_from, page_size, for_lineage, for_duplicate_processing (and, for
related-elements, starting_at_end) and sent none of them. They now go in the
ResultsRequestBody (and startingAtEnd in the query string), without
overriding a field the caller's body already sets.
"""
import json

import pytest

from pyegeria.omvs.metadata_expert import MetadataExpert


class _Response:
    def json(self):
        return {"elementList": []}


@pytest.fixture
def client_and_calls(monkeypatch):
    monkeypatch.setattr(MetadataExpert, "check_connection", lambda self: "test")
    client = MetadataExpert("view-server", "https://localhost:1", "user", "pwd")
    calls = []

    async def fake_make_request(method, url, body=None, *args, **kwargs):
        calls.append((url, json.loads(body) if isinstance(body, str) else body))
        return _Response()

    client._async_make_request = fake_make_request
    return client, calls


@pytest.mark.asyncio
async def test_related_elements_by_type_sends_paging_end_and_lineage(client_and_calls):
    client, calls = client_and_calls

    await client._async_get_related_metadata_elements(
        "g1", "SolutionCompositionLink", None, for_lineage=True, starting_at_end=2, start_from=10, page_size=5)

    url, body = calls[0]
    assert url.endswith("/related-elements/g1/type/SolutionCompositionLink?startingAtEnd=2")
    assert body["startFrom"] == 10 and body["pageSize"] == 5 and body["forLineage"] is True
    assert "forDuplicateProcessing" not in body


@pytest.mark.asyncio
async def test_body_fields_win_over_keyword_arguments(client_and_calls):
    client, calls = client_and_calls

    await client._async_get_related_metadata_elements(
        "g1", "T", {"class": "ResultsRequestBody", "pageSize": 7}, page_size=500)

    assert calls[0][1]["pageSize"] == 7


@pytest.mark.asyncio
@pytest.mark.parametrize("method, args, path", [
    ("_async_get_all_metadata_element_relationships", ("e1", "e2"), "/metadata-elements/e1/linked-by-any-type/to-elements/e2"),
    ("_async_get_metadata_element_relationships", ("e1", "e2", "T"), "/metadata-elements/e1/linked-by-type/T/to-elements/e2"),
])
async def test_linked_by_queries_send_paging(client_and_calls, method, args, path):
    client, calls = client_and_calls
    fn = getattr(client, method)

    if method == "_async_get_metadata_element_relationships":
        await fn(end1_guid=args[0], end2_guid=args[1], relationship_type=args[2], body=None,
                 start_from=3, page_size=4)
    else:
        await fn(args[0], args[1], None, start_from=3, page_size=4)

    url, body = calls[0]
    assert url.endswith(path)
    assert body["startFrom"] == 3 and body["pageSize"] == 4
