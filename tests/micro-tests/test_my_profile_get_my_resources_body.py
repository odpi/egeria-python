# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
ISSUE-115: MyProfile.get_my_resources sent its rendering hint "Resource" as
metadataElementTypeName, which isn't an Egeria type, so every call failed with
OMAG-COMMON-400-018. The endpoint's .http example (Egeria-api-my-profile.http,
getMyResources) sends a plain ResultsRequestBody with no type filter.

Captures the outgoing request instead of calling a server.
"""
import json
from unittest.mock import AsyncMock, MagicMock, patch

from pyegeria import MyProfile


def _client_capturing_requests() -> tuple[MyProfile, AsyncMock]:
    # The constructor pings the platform (check_connection()) before any mock can be
    # installed, so it is patched out while the client is built.
    with patch("pyegeria.core._base_server_client.BaseServerClient.check_connection", return_value=""):
        client = MyProfile("qs-view-server", "https://localhost:9443", "garygeeke", "secret")
    response = MagicMock()
    response.json.return_value = {"elements": [{"elementHeader": {"guid": "g1"}, "properties": {}}]}
    client._async_make_request = AsyncMock(return_value=response)
    return client, client._async_make_request


async def test_get_my_resources_sends_no_type_filter():
    client, make_request = _client_capturing_requests()

    result = await client._async_get_my_resources(output_format="JSON")

    verb, url, json_body = make_request.call_args.args
    body = json.loads(json_body)
    assert verb == "POST"
    assert url.endswith("/api/open-metadata/my-profile/assigned-resources?includeUserIds=true&includeRoles=true")
    assert body["class"] == "ResultsRequestBody"
    assert "metadataElementTypeName" not in body
    assert result == [{"elementHeader": {"guid": "g1"}, "properties": {}}]


async def test_get_my_resources_caller_body_is_sent_unchanged():
    client, make_request = _client_capturing_requests()

    await client._async_get_my_resources(body={"class": "ResultsRequestBody", "pageSize": 5})

    body = json.loads(make_request.call_args.args[2])
    assert body["pageSize"] == 5
    assert "metadataElementTypeName" not in body
