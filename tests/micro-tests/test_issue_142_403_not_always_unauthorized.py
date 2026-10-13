# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
ISSUE-142: Egeria also uses relatedHTTPCode 403 for errors that are not about
authorization (e.g. OMAG-GENERIC-HANDLERS-403-005, an InvalidParameterException
for deleting an element that still has dependents). pyegeria raised every
401/403 as "User not authorized ... for user - ``", hiding the real cause.
"""
import httpx
import pytest

from pyegeria.core._exceptions import PyegeriaAPIException, PyegeriaUnauthorizedException
from pyegeria.omvs.collection_manager import CollectionManager


def _client(monkeypatch, body):
    monkeypatch.setattr(CollectionManager, "check_connection", lambda self: "test")
    client = CollectionManager("view-server", "https://localhost:1", "erinoverview", "pwd")

    async def fake_post(endpoint, **kwargs):
        return httpx.Response(200, json=body, request=httpx.Request("POST", endpoint))

    monkeypatch.setattr(client.session, "post", fake_post)
    return client


DEPENDENT = {
    "class": "VoidResponse", "relatedHTTPCode": 403,
    "exceptionClassName": "org.odpi.openmetadata.frameworks.openmetadata.ffdc.InvalidParameterException",
    "exceptionErrorMessageId": "OMAG-GENERIC-HANDLERS-403-005",
    "exceptionErrorMessage": "OMAG-GENERIC-HANDLERS-403-005 The WorkingSet still has a dependent RelationalTable",
}
NOT_AUTHORIZED = {
    "class": "VoidResponse", "relatedHTTPCode": 403,
    "exceptionClassName": "org.odpi.openmetadata.frameworks.openmetadata.ffdc.UserNotAuthorizedException",
    "exceptionErrorMessage": "OMAG-COMMON-403-001 User erinoverview is not authorized",
}


@pytest.mark.asyncio
async def test_403_invalid_parameter_is_not_reported_as_unauthorized(monkeypatch):
    client = _client(monkeypatch, DEPENDENT)
    with pytest.raises(PyegeriaAPIException) as exc:
        await client._async_make_request("POST", "https://localhost:1/x", {"class": "DeleteElementRequestBody"})
    assert not isinstance(exc.value, PyegeriaUnauthorizedException)
    assert "403-005" in str(exc.value)


@pytest.mark.asyncio
async def test_real_authorization_failure_still_unauthorized_and_names_the_user(monkeypatch):
    client = _client(monkeypatch, NOT_AUTHORIZED)
    with pytest.raises(PyegeriaUnauthorizedException) as exc:
        await client._async_make_request("POST", "https://localhost:1/x", {"class": "X"})
    assert "erinoverview" in exc.value.message
    assert exc.value.related_http_code == 403


@pytest.mark.asyncio
async def test_401_without_exception_class_is_unauthorized(monkeypatch):
    client = _client(monkeypatch, {"class": "VoidResponse", "relatedHTTPCode": 401})
    with pytest.raises(PyegeriaUnauthorizedException):
        await client._async_make_request("POST", "https://localhost:1/x", {"class": "X"})
