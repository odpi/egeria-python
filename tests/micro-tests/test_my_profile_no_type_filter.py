# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
ISSUE-115 / ISSUE-116: four MyProfile "linked to my profile" queries sent their
rendering hint (the _type passed to _async_get_results_body_request) as
metadataElementTypeName. None of these endpoints' .http examples
(Egeria-api-my-profile.http) send a type filter, and with one the server either
rejected the call or silently returned nothing:

- get_my_resources       "Resource"       -> OMAG-COMMON-400-018, not an Egeria type
- get_my_actors          "ActorProfile"   -> OMAG-REPOSITORY-HANDLER-404-001
- get_my_user_identities "UserIdentity"   -> "No elements found" for every user
- get_my_roles           "GovernanceRole" -> "No elements found" for every user

Captures the outgoing request instead of calling a server.
"""
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pyegeria import MyProfile

ENDPOINTS = [
    ("_async_get_my_resources", "/my-profile/assigned-resources?includeUserIds=true&includeRoles=true"),
    ("_async_get_my_actors", "/my-profile/actors"),
    ("_async_get_my_user_identities", "/my-profile/actors/user-identities"),
    ("_async_get_my_roles", "/my-profile/actors/assigned-roles"),
]


def _client_capturing_requests() -> tuple[MyProfile, AsyncMock]:
    # The constructor pings the platform (check_connection()) before any mock can be
    # installed, so it is patched out while the client is built.
    with patch("pyegeria.core._base_server_client.BaseServerClient.check_connection", return_value=""):
        client = MyProfile("qs-view-server", "https://localhost:9443", "garygeeke", "secret")
    response = MagicMock()
    response.json.return_value = {"elements": [{"elementHeader": {"guid": "g1"}, "properties": {}}]}
    client._async_make_request = AsyncMock(return_value=response)
    return client, client._async_make_request


@pytest.mark.parametrize("method, path", ENDPOINTS)
async def test_sends_no_type_filter(method, path):
    client, make_request = _client_capturing_requests()

    result = await getattr(client, method)(output_format="JSON")

    verb, url, json_body = make_request.call_args.args
    body = json.loads(json_body)
    assert verb == "POST"
    assert url.endswith("/api/open-metadata" + path)
    assert body["class"] == "ResultsRequestBody"
    assert "metadataElementTypeName" not in body
    assert result == [{"elementHeader": {"guid": "g1"}, "properties": {}}]


@pytest.mark.parametrize("method, path", ENDPOINTS)
async def test_caller_body_is_sent_unchanged(method, path):
    client, make_request = _client_capturing_requests()

    await getattr(client, method)(body={"class": "ResultsRequestBody", "pageSize": 5})

    body = json.loads(make_request.call_args.args[2])
    assert body["pageSize"] == 5
    assert "metadataElementTypeName" not in body
