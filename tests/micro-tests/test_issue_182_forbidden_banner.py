# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""ISSUE-182: an element hidden by zone security was reported as "AUTHORIZATION_ERROR_401".

Egeria answers a read of an element in a zone the user can't see with an HTTP 200 wrapping relatedHTTPCode 403,
OPEN-METADATA-SECURITY-403-020 and a UserNotAuthorizedException. pyegeria raised the right class but labelled it
401 "User not authorized", which points at credentials. Now the message names 403 and Egeria's message id; the
class, related_http_code and the 401-only token retry are unchanged. Nothing reaches Egeria.
"""
import httpx
import pytest

from pyegeria.core._exceptions import PyegeriaAPIException, PyegeriaUnauthorizedException
from pyegeria.omvs.collection_manager import CollectionManager
from pyegeria.view.dashboard_resolver import is_not_visible_error

pytestmark = pytest.mark.unit

NOT_VISIBLE = {
    "class": "OpenMetadataElementResponse", "relatedHTTPCode": 403,
    "exceptionClassName": "org.odpi.openmetadata.frameworks.openmetadata.ffdc.UserNotAuthorizedException",
    "actionDescription": "getMetadataElementByGUID",
    "exceptionErrorMessageId": "OPEN-METADATA-SECURITY-403-020",
    "exceptionErrorMessage": "OPEN-METADATA-SECURITY-403-020 The element 1b2c is not visible to user erinoverview",
    "exceptionSystemAction": "The system is unable to process the request.",
    "exceptionUserAction": "Request access to the zone, or use another user.",
}


def _client(monkeypatch, responses):
    """A client whose POSTs answer from `responses` in turn; counts token refreshes."""
    monkeypatch.setattr(CollectionManager, "check_connection", lambda self: "test")
    client = CollectionManager("view-server", "https://localhost:1", "erinoverview", "pwd")
    client.posts, client.refreshes = 0, 0

    async def fake_post(endpoint, **kwargs):
        resp = responses[min(client.posts, len(responses) - 1)]
        client.posts += 1
        return resp(endpoint)

    async def fake_refresh(*a, **k):
        client.refreshes += 1
        return "new-token"

    monkeypatch.setattr(client.session, "post", fake_post)
    monkeypatch.setattr(client, "_async_create_egeria_bearer_token", fake_refresh)
    monkeypatch.setattr(client, "_owns_token", lambda: True)
    return client


def _wrapped(body):
    return lambda endpoint: httpx.Response(200, json=body, request=httpx.Request("POST", endpoint))


def _bare(code):
    return lambda endpoint: httpx.Response(code, text="Unauthorized", request=httpx.Request("POST", endpoint))


@pytest.mark.asyncio
async def test_403_020_names_403_and_the_egeria_message_id(monkeypatch):
    client = _client(monkeypatch, [_wrapped(NOT_VISIBLE)])
    with pytest.raises(PyegeriaUnauthorizedException) as exc:
        await client._async_make_request("POST", "https://localhost:1/x", {"class": "X"})
    e = exc.value
    assert isinstance(e, PyegeriaAPIException)  # class unchanged
    assert e.related_http_code == 403
    assert e.egeria_message_id == "OPEN-METADATA-SECURITY-403-020"
    assert e.pyegeria_code == "AUTHORIZATION_ERROR_403"
    assert e.message.startswith("HTTP Code: 403 OPEN-METADATA-SECURITY-403-020 The element 1b2c is not visible")
    assert "erinoverview" in e.message
    text = str(e)
    assert "AUTHORIZATION_ERROR_401" not in text and "User not authorized received" not in text
    assert is_not_visible_error(e)
    # Callers that match text (the Portal's _is_auth_error helpers) still recognise it, and read 403.
    assert "AUTHORIZATION_ERROR" in text.upper() and "HTTP CODE: 403" in text.upper()


@pytest.mark.asyncio
async def test_403_020_is_never_retried_with_a_new_token(monkeypatch):
    client = _client(monkeypatch, [_wrapped(NOT_VISIBLE)])
    with pytest.raises(PyegeriaUnauthorizedException):
        await client._async_make_request("POST", "https://localhost:1/x", {"class": "X"})
    assert client.refreshes == 0 and client.posts == 1


@pytest.mark.asyncio
async def test_403_message_without_the_id_gets_it_prefixed(monkeypatch):
    body = {**NOT_VISIBLE, "exceptionErrorMessage": "The element is not visible to user erinoverview"}
    client = _client(monkeypatch, [_wrapped(body)])
    with pytest.raises(PyegeriaUnauthorizedException) as exc:
        await client._async_make_request("POST", "https://localhost:1/x", {"class": "X"})
    assert exc.value.message.startswith("HTTP Code: 403 OPEN-METADATA-SECURITY-403-020 The element")


@pytest.mark.asyncio
async def test_a_transport_401_is_unchanged_and_retried_once(monkeypatch):
    client = _client(monkeypatch, [_bare(401)])
    with pytest.raises(PyegeriaUnauthorizedException) as exc:
        await client._async_make_request("POST", "https://localhost:1/x", {"class": "X"})
    e = exc.value
    assert client.refreshes == 1 and client.posts == 2  # one refresh, one retry, then raised
    assert e.pyegeria_code == "AUTHORIZATION_ERROR_401"
    assert e.related_http_code == 401
    assert e.message == "User not authorized received for user - `erinoverview`."
    assert e.egeria_message_id == ""
    assert not is_not_visible_error(e)


@pytest.mark.asyncio
async def test_a_wrapped_401_stays_401(monkeypatch):
    client = _client(monkeypatch, [_wrapped({"class": "VoidResponse", "relatedHTTPCode": 401})])
    with pytest.raises(PyegeriaUnauthorizedException) as exc:
        await client._async_make_request("POST", "https://localhost:1/x", {"class": "X"})
    assert exc.value.pyegeria_code == "AUTHORIZATION_ERROR_401"
    assert client.refreshes == 0
