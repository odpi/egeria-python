"""
ProductManager: subscription types (one-time / periodic / ongoing-update) and the Open Data
Contract / Product Standard (ODCS / ODPS) import, publish and generate calls
(Egeria-api-product-manager.http). No live server: the HTTP call is captured.
"""
import json

import httpx
import pytest

from pyegeria.core._globals import NO_ELEMENTS_FOUND
from pyegeria.omvs.product_manager import ProductManager

ROOT = "/api/open-metadata/product-manager"
YAML_DOC = "apiVersion: v3.1.0\nkind: DataContract\nid: 6d0f\nname: Weekly measurements\n"


class _Response:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def _client(calls: list, payload: dict, monkeypatch) -> ProductManager:
    monkeypatch.setattr(ProductManager, "check_connection", lambda self: "test")
    client = ProductManager("view-server", "https://localhost:1", "user", "pwd")

    async def fake_make_request(method, url, payload_=None, is_json=True, params=None, *,
                                timeout=None, as_text=False, **kwargs):
        calls.append({"method": method, "url": url, "as_text": as_text,
                      "body": payload_ if isinstance(payload_, (dict, type(None))) else
                      (payload_ if as_text else json.loads(payload_))})
        return _Response(payload)

    client._async_make_request = fake_make_request
    return client


@pytest.mark.asyncio
@pytest.mark.parametrize("method, kind", [
    ("_async_create_one_time_subscription", "one-time"),
    ("_async_create_periodic_subscription", "periodic"),
    ("_async_create_ongoing_update_subscription", "ongoing-update"),
])
async def test_subscription_types_post_to_the_kind_and_return_the_process_guid(method, kind, monkeypatch):
    calls: list = []
    client = _client(calls, {"class": "GUIDResponse", "guid": "gap-guid"}, monkeypatch)
    body = {"identifier": "ID", "displayName": "Name", "minimumNotificationInterval": 10,
            "monitoredResourceGUIDs": ["asset-1"]}

    guid = await getattr(client, method)("product-1", body)

    assert guid == "gap-guid"
    assert calls[0]["method"] == "POST"
    assert calls[0]["url"].endswith(f"{ROOT}/digital-products/product-1/subscription-types/{kind}")
    assert calls[0]["body"]["class"] == "NewSubscriptionTypeRequestBody"
    assert calls[0]["body"]["monitoredResourceGUIDs"] == ["asset-1"]   # explicit alias, not "...Guids"
    assert calls[0]["body"]["minimumNotificationInterval"] == 10
    # TRANSITIONAL: also sent under the pre-rename name until Egeria's oak2026 change merges.
    assert calls[0]["body"]["notificationInterval"] == 10


@pytest.mark.asyncio
async def test_subscription_type_accepts_the_old_interval_name_and_sends_both(monkeypatch):
    # TRANSITIONAL: a caller still using notificationInterval keeps working on a 6.3 platform.
    calls: list = []
    client = _client(calls, {"class": "GUIDResponse", "guid": "gap-guid"}, monkeypatch)
    await client._async_create_periodic_subscription("product-1", {"notificationInterval": 1440})
    assert calls[0]["body"]["minimumNotificationInterval"] == 1440
    assert calls[0]["body"]["notificationInterval"] == 1440


@pytest.mark.asyncio
async def test_subscription_body_is_optional(monkeypatch):
    calls: list = []
    client = _client(calls, {"guid": "g"}, monkeypatch)

    await client._async_create_one_time_subscription("product-1")

    assert calls[0]["body"] is None


@pytest.mark.asyncio
@pytest.mark.parametrize("method, tail", [
    ("_async_publish_data_contract_string", "data-contracts/publish-document-string"),
    ("_async_publish_data_product_string", "data-products/publish-document-string"),
])
async def test_publish_sends_the_document_as_text_to_the_daemon(method, tail, monkeypatch):
    calls: list = []
    client = _client(calls, {"class": "VoidResponse"}, monkeypatch)

    result = await getattr(client, method)("daemon-1", YAML_DOC)

    assert result is None
    assert calls[0]["url"].endswith(f"{ROOT}/integration-daemons/daemon-1/{tail}")
    assert calls[0]["as_text"] is True and calls[0]["body"] == YAML_DOC


@pytest.mark.asyncio
@pytest.mark.parametrize("method, tail", [
    ("_async_import_data_contract_string", "data-contracts/import-document-string"),
    ("_async_import_data_product_string", "data-products/import-document-string"),
])
async def test_import_string_sends_text_and_returns_guid(method, tail, monkeypatch):
    calls: list = []
    client = _client(calls, {"guid": "new-guid"}, monkeypatch)

    guid = await getattr(client, method)(YAML_DOC)

    assert guid == "new-guid"
    assert calls[0]["url"].endswith(f"{ROOT}/{tail}")
    assert calls[0]["as_text"] is True and calls[0]["body"] == YAML_DOC


@pytest.mark.asyncio
@pytest.mark.parametrize("method, tail", [
    ("_async_import_data_contract", "data-contracts/import-document"),
    ("_async_import_data_product", "data-products/import-document"),
])
async def test_import_bean_sends_json_unchanged_and_returns_guid(method, tail, monkeypatch):
    calls: list = []
    client = _client(calls, {"guid": "new-guid"}, monkeypatch)
    bean = {"apiVersion": "v3.1.0", "kind": "DataContract", "id": "6d0f", "name": "n", "status": "active"}

    guid = await getattr(client, method)(bean)

    assert guid == "new-guid"
    assert calls[0]["url"].endswith(f"{ROOT}/{tail}")
    assert calls[0]["as_text"] is False and calls[0]["body"] == bean   # no class / forLineage injected


@pytest.mark.asyncio
async def test_import_rejects_a_wrong_document_type_before_any_request(monkeypatch):
    calls: list = []
    client = _client(calls, {}, monkeypatch)

    with pytest.raises(Exception):
        await client._async_import_data_contract(12345)

    assert calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("method, arg, tail, key", [
    ("_async_generate_data_contract", "agr-1", "agreements/agr-1/data-contract-document", "dataContract"),
    ("_async_generate_data_product", "prod-1", "digital-products/prod-1/data-product-document", "dataProduct"),
])
async def test_generate_returns_the_document(method, arg, tail, key, monkeypatch):
    calls: list = []
    client = _client(calls, {key: {"kind": "x", "id": "1"}}, monkeypatch)

    doc = await getattr(client, method)(arg)

    assert doc == {"kind": "x", "id": "1"}
    assert calls[0]["method"] == "GET" and calls[0]["url"].endswith(f"{ROOT}/{tail}")


@pytest.mark.asyncio
async def test_generate_with_no_document_says_so_rather_than_returning_empty(monkeypatch):
    client = _client([], {"class": "DataContractResponse"}, monkeypatch)

    assert await client._async_generate_data_contract("agr-1") == NO_ELEMENTS_FOUND


@pytest.mark.asyncio
async def test_as_text_reaches_the_http_layer_as_text_plain(monkeypatch):
    """The real _async_make_request, with only httpx stubbed: a str payload sent as_text goes out as
    text/plain; the default stays application/json."""
    monkeypatch.setattr(ProductManager, "check_connection", lambda self: "test")
    client = ProductManager("view-server", "https://localhost:1", "user", "pwd")
    seen: list = []

    async def fake_post(endpoint, **kwargs):
        seen.append(kwargs["headers"]["Content-Type"])
        return httpx.Response(200, json={"relatedHTTPCode": 200, "guid": "g"}, request=httpx.Request("POST", endpoint))

    monkeypatch.setattr(client.session, "post", fake_post)

    await client._async_make_request("POST", "https://localhost:1/x", YAML_DOC, as_text=True)
    await client._async_make_request("POST", "https://localhost:1/x", YAML_DOC)

    assert seen == ["text/plain", "application/json"]


@pytest.mark.asyncio
async def test_governance_action_processes_by_name_uses_the_product_catalog_url(monkeypatch):
    calls: list = []
    client = _client(calls, {"elements": [{"elementHeader": {"guid": "gap-1"}}]}, monkeypatch)

    result = await client._async_get_governance_action_processes_by_name(
        "ProvisioningActionProcess::Hospital Data::Create Subscription::EVAL")

    assert result == [{"elementHeader": {"guid": "gap-1"}}]
    assert calls[0]["method"] == "POST"
    assert calls[0]["url"].endswith("/api/open-metadata/product-catalog/governance-definitions/by-name")
    assert calls[0]["body"]["filter"] == "ProvisioningActionProcess::Hospital Data::Create Subscription::EVAL"
    # a filter by name, not by an element type (a wrong type name is rejected by the server)
    assert "metadataElementTypeName" not in calls[0]["body"]


def test_subscription_type_body_rejects_two_different_intervals():
    # TRANSITIONAL: both names are sent, so a pre-rename platform would use one value and a
    # post-rename platform the other. Refuse rather than send a body whose meaning depends on the server.
    from pyegeria.models import NewSubscriptionTypeRequestBody
    with pytest.raises(ValueError, match=r"minimumNotificationInterval \(10\) and notificationInterval \(1440\)"):
        NewSubscriptionTypeRequestBody.model_validate(
            {"class": "NewSubscriptionTypeRequestBody", "minimumNotificationInterval": 10,
             "notificationInterval": 1440})


@pytest.mark.asyncio
async def test_subscription_type_with_two_different_intervals_is_not_sent(monkeypatch):
    calls: list = []
    client = _client(calls, {"class": "GUIDResponse", "guid": "gap-guid"}, monkeypatch)
    try:
        await client._async_create_periodic_subscription(
            "product-1", {"minimumNotificationInterval": 10, "notificationInterval": 1440})
    except Exception:
        pass   # dynamic_catch may raise or swallow; either way nothing must reach Egeria
    assert calls == []


@pytest.mark.asyncio
async def test_subscription_type_with_equal_intervals_under_both_names_is_sent(monkeypatch):
    calls: list = []
    client = _client(calls, {"class": "GUIDResponse", "guid": "gap-guid"}, monkeypatch)
    await client._async_create_periodic_subscription(
        "product-1", {"minimumNotificationInterval": 60, "notificationInterval": 60})
    assert calls[0]["body"]["minimumNotificationInterval"] == 60
    assert calls[0]["body"]["notificationInterval"] == 60
