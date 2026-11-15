# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Pager step 6 (the catalog-health capture attempt, 2026-11-14): a request to a view server that isn't running on
the platform (OMAG-MULTI-TENANT-404-001) answered relatedHTTPCode 404, pyegeria raised it as
PyegeriaNotFoundException, and load_held reported "Egeria holds no dashboard sheet ... that you can see" -- a
wrong server name read as an absent element. A server/service-not-available 404 is now an API error, never
"not found"; an element's own not-found is unchanged."""
import httpx
import pytest

from pyegeria.core._exceptions import PyegeriaAPIException, PyegeriaNotFoundException
from pyegeria.omvs.collection_manager import CollectionManager

pytestmark = pytest.mark.unit

SERVER_NOT_AVAILABLE = {
    "class": "ElementResponse", "relatedHTTPCode": 404,
    "exceptionClassName": "org.odpi.openmetadata.frameworks.openmetadata.ffdc.InvalidParameterException",
    "exceptionErrorMessageId": "OMAG-MULTI-TENANT-404-001",
    "exceptionErrorMessage": "OMAG-MULTI-TENANT-404-001 The OMAG Server qs-view-server is not available to service "
                             "a request from user garygeeke",
}
SERVICE_NOT_AVAILABLE = {**SERVER_NOT_AVAILABLE, "exceptionErrorMessageId": "OMAG-MULTI-TENANT-404-002"}
ELEMENT_NOT_FOUND = {
    "class": "ElementResponse", "relatedHTTPCode": 404,
    "exceptionClassName": "org.odpi.openmetadata.frameworks.openmetadata.ffdc.PropertyServerException",
    "exceptionErrorMessageId": "OMAG-GENERIC-HANDLERS-404-001",
    "exceptionErrorMessage": "OMAG-GENERIC-HANDLERS-404-001 no element",
}


def _client(monkeypatch, body):
    monkeypatch.setattr(CollectionManager, "check_connection", lambda self: "test")
    client = CollectionManager("qs-view-server", "https://localhost:1", "garygeeke", "pwd")

    async def fake_post(endpoint, **kwargs):
        return httpx.Response(200, json=body, request=httpx.Request("POST", endpoint))

    monkeypatch.setattr(client.session, "post", fake_post)
    return client


@pytest.mark.asyncio
@pytest.mark.parametrize("body", [SERVER_NOT_AVAILABLE, SERVICE_NOT_AVAILABLE], ids=["server", "service"])
async def test_a_server_not_available_404_is_an_api_error_not_not_found(monkeypatch, body):
    client = _client(monkeypatch, body)
    with pytest.raises(PyegeriaAPIException) as exc:
        await client._async_make_request("POST", "https://localhost:1/x", {"class": "X"})
    assert not isinstance(exc.value, PyegeriaNotFoundException)
    assert "MULTI-TENANT-404" in str(exc.value)


@pytest.mark.asyncio
async def test_an_elements_own_not_found_is_still_not_found(monkeypatch):
    client = _client(monkeypatch, ELEMENT_NOT_FOUND)
    with pytest.raises(PyegeriaNotFoundException):
        await client._async_make_request("POST", "https://localhost:1/x", {"class": "X"})


@pytest.mark.asyncio
async def test_load_held_on_a_wrong_server_raises_instead_of_holds_no(monkeypatch):
    from md_processing.v2.report import find_element_by_qualified_name

    class CM:
        async def _async_get_element_by_unique_name(self, qn):
            return await _client(monkeypatch, SERVER_NOT_AVAILABLE)._async_make_request(
                "POST", "https://localhost:1/x", {"class": "X"})

    client = type("C", (), {"classification_manager": CM()})()
    with pytest.raises(PyegeriaAPIException) as exc:
        await find_element_by_qualified_name(client, "Dashboard::catalog-health")
    assert not isinstance(exc.value, PyegeriaNotFoundException)   # so load_held never says "holds no"
