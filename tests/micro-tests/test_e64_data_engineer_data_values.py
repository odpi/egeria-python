# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""A2a for the Egeria 6.4 additions (odpi/egeria#9463): the seven data-value lifecycle requests on
DataEngineer. No Egeria: `_async_make_request` is replaced by a recorder, and each body is compared with the
sample body in the PR's `.http` collection (tests/fixtures/egeria-6.4/Egeria-api-data-engineer.http).

Covered for each request: the URL path and HTTP method, the body sent, and the local refusals (an update or a
create with no body; a `properties.class` that is neither DataValueProperties nor LiteralDataValueProperties).
LiteralDataValueProperties, with dataValueList and dataValueMap, must round-trip unchanged.
"""
import copy
import json
import re
from pathlib import Path

import pytest

from pyegeria.core import egeria_6_4_names as n
from pyegeria.core._exceptions import PyegeriaInvalidParameterException
from pyegeria.models import NewElementRequestBody, UpdateElementRequestBody
from pyegeria.omvs.data_engineer import DataEngineer

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "egeria-6.4" / "Egeria-api-data-engineer.http"
PLATFORM = "https://localhost:1"
SERVER = "view-server"
ROOT = f"{PLATFORM}/servers/{SERVER}/api/open-metadata/"
DV_GUID = "dv-guid-1"
# The `.http` samples use {{$isoTimestamp}}; any fixed instant in Egeria's own form will do.
TIMESTAMP = "2026-11-21T10:00:00Z"


def _samples() -> dict[str, dict]:
    """Every named request in the collection that has a JSON body: name -> body."""
    out = {}
    for block in re.split(r"\n###\n", FIXTURE.read_text(encoding="utf-8")):
        name = re.search(r"# @name (\w+)", block)
        start = block.find("\n{")
        if name and start >= 0:
            text = block[start + 1:].replace("{{$isoTimestamp}}", TIMESTAMP)
            body = json.JSONDecoder().raw_decode(text)[0]
            if "class" in body:
                out[name.group(1)] = body
    return out


SAMPLES = _samples()


def sample(name: str) -> dict:
    return copy.deepcopy(SAMPLES[name])


def literal(body: dict) -> dict:
    """The same body, with the properties of a LiteralDataValue (a list and a map as well as a single value)."""
    body = copy.deepcopy(body)
    props = body["properties"]
    props["class"] = n.LITERAL_DATA_VALUE_PROPERTIES
    props["dataValue"] = "42"
    props["dataValueList"] = ["red", "amber", "green"]
    props["dataValueMap"] = {"low": "1", "high": "9"}
    return body


class _Response:
    def __init__(self, payload: dict):
        self._payload = payload

    def json(self):
        return self._payload


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(DataEngineer, "check_connection", lambda self: "test")
    c = DataEngineer(SERVER, PLATFORM, "user", "pwd")
    c.calls = []
    c.reply = {"class": "GUIDResponse", "relatedHTTPCode": 200, "guid": "new-guid"}

    async def fake_make_request(method, url, payload=None, *args, **kwargs):
        body = json.loads(payload) if isinstance(payload, str) else payload
        c.calls.append((method, url, body))
        return _Response(c.reply)

    c._async_make_request = fake_make_request
    return c


def _url(path: str, **guids) -> str:
    return ROOT + path.format(**guids)


# --- create -------------------------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_posts_the_sample_body_and_returns_the_guid(client):
    guid = await client._async_create_data_value(sample("createDataValue"))
    assert guid == "new-guid"
    assert client.calls == [("POST", _url(n.DATA_VALUES_CREATE), sample("createDataValue"))]


@pytest.mark.asyncio
async def test_create_accepts_a_literal_data_value_and_round_trips_list_and_map(client):
    await client._async_create_data_value(literal(sample("createDataValue")))
    sent = client.calls[0][2]["properties"]
    assert sent["class"] == "LiteralDataValueProperties"
    assert sent["dataValueList"] == ["red", "amber", "green"]
    assert sent["dataValueMap"] == {"low": "1", "high": "9"}
    assert client.calls[0][2] == literal(sample("createDataValue"))


@pytest.mark.asyncio
async def test_create_accepts_a_model_body_and_keeps_the_literal_fields(client):
    await client._async_create_data_value(NewElementRequestBody.model_validate(literal(sample("createDataValue"))))
    sent = client.calls[0][2]["properties"]
    assert sent["dataValueList"] == ["red", "amber", "green"]
    assert sent["dataValueMap"] == {"low": "1", "high": "9"}


def test_create_sync_wrapper(client):
    assert client.create_data_value(sample("createDataValue")) == "new-guid"
    assert client.calls[0][1] == _url(n.DATA_VALUES_CREATE)


@pytest.mark.asyncio
async def test_create_without_a_body_is_refused_locally(client):
    with pytest.raises(PyegeriaInvalidParameterException):
        await client._async_create_data_value(None)
    assert client.calls == []


@pytest.mark.asyncio
async def test_create_with_the_wrong_properties_class_is_refused_naming_the_expected_class(client):
    body = sample("createDataValue")
    body["properties"]["class"] = "DecisionProperties"
    with pytest.raises(PyegeriaInvalidParameterException) as err:
        await client._async_create_data_value(body)
    assert "DataValueProperties" in str(err.value) and "LiteralDataValueProperties" in str(err.value)
    assert "DecisionProperties" in str(err.value)
    assert client.calls == []


@pytest.mark.asyncio
async def test_create_with_no_properties_class_is_refused(client):
    body = sample("createDataValue")
    del body["properties"]["class"]
    with pytest.raises(PyegeriaInvalidParameterException):
        await client._async_create_data_value(body)
    assert client.calls == []


# --- create from template -----------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_from_template_posts_the_sample_body_and_returns_the_guid(client):
    guid = await client._async_create_data_value_from_template(sample("createDataValueFromTemplate"))
    assert guid == "new-guid"
    assert client.calls == [("POST", _url(n.DATA_VALUES_FROM_TEMPLATE), sample("createDataValueFromTemplate"))]


def test_create_from_template_sync_wrapper(client):
    assert client.create_data_value_from_template(sample("createDataValueFromTemplate")) == "new-guid"


@pytest.mark.asyncio
async def test_create_from_template_without_a_body_is_refused_locally(client):
    with pytest.raises(PyegeriaInvalidParameterException):
        await client._async_create_data_value_from_template(None)
    assert client.calls == []


# --- update -------------------------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_update_posts_the_sample_body(client):
    await client._async_update_data_value(DV_GUID, sample("updateDataValue"))
    assert client.calls == [("POST", _url(n.DATA_VALUES_UPDATE, dataValueGUID=DV_GUID), sample("updateDataValue"))]


@pytest.mark.asyncio
async def test_update_accepts_a_literal_data_value_and_round_trips_list_and_map(client):
    await client._async_update_data_value(DV_GUID, literal(sample("updateDataValue")))
    assert client.calls[0][2] == literal(sample("updateDataValue"))


@pytest.mark.asyncio
async def test_update_accepts_a_model_body(client):
    await client._async_update_data_value(DV_GUID, UpdateElementRequestBody.model_validate(
        literal(sample("updateDataValue"))))
    sent = client.calls[0][2]
    assert sent["properties"]["dataValueMap"] == {"low": "1", "high": "9"}
    assert sent["mergeUpdate"] is True


@pytest.mark.asyncio
@pytest.mark.parametrize("merge", [True, False])
async def test_update_passes_merge_update_through(client, merge):
    body = sample("updateDataValue")
    body["mergeUpdate"] = merge
    await client._async_update_data_value(DV_GUID, body)
    assert client.calls[0][2]["mergeUpdate"] is merge


def test_update_sync_wrapper(client):
    client.update_data_value(DV_GUID, sample("updateDataValue"))
    assert client.calls[0][1] == _url(n.DATA_VALUES_UPDATE, dataValueGUID=DV_GUID)


@pytest.mark.asyncio
async def test_update_without_a_body_is_refused_locally(client):
    with pytest.raises(PyegeriaInvalidParameterException) as err:
        await client._async_update_data_value(DV_GUID, None)
    assert "body" in str(err.value)
    assert client.calls == []


@pytest.mark.asyncio
async def test_update_with_the_wrong_properties_class_is_refused_naming_the_expected_class(client):
    body = sample("updateDataValue")
    body["properties"]["class"] = "AssetProperties"
    with pytest.raises(PyegeriaInvalidParameterException) as err:
        await client._async_update_data_value(DV_GUID, body)
    assert "DataValueProperties" in str(err.value) and "AssetProperties" in str(err.value)
    assert client.calls == []


# --- delete -------------------------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_delete_posts_the_sample_body(client):
    await client._async_delete_data_value(DV_GUID, sample("deleteDataValue"))
    assert client.calls == [("POST", _url(n.DATA_VALUES_DELETE, dataValueGUID=DV_GUID), sample("deleteDataValue"))]


@pytest.mark.asyncio
async def test_delete_without_a_body_sends_a_plain_delete_body(client):
    await client._async_delete_data_value(DV_GUID)
    method, url, body = client.calls[0]
    assert (method, url) == ("POST", _url(n.DATA_VALUES_DELETE, dataValueGUID=DV_GUID))
    assert body == {"class": "DeleteElementRequestBody", "cascadedDelete": False}


def test_delete_sync_wrapper(client):
    client.delete_data_value(DV_GUID, cascade=True)
    assert client.calls[0][2]["cascadedDelete"] is True


# --- reads: by name, by GUID, by search string --------------------------------------------------------------
# These go through the shared read helpers, which validate the body into its pydantic model and send its dump:
# every key of the sample is sent unchanged, and the only extra keys are the model's own defaults.
READ_DEFAULTS = {"relationshipsPageSize": 0, "forLineage": False, "forDuplicateProcessing": False}


def _assert_sample_sent(sent: dict, expected: dict):
    for key, value in expected.items():
        assert sent.get(key) == value, f"{key}: sent {sent.get(key)!r}, sample {value!r}"
    extra = {k: v for k, v in sent.items() if k not in expected}
    assert extra.items() <= READ_DEFAULTS.items(), f"unexpected keys sent: {extra}"


@pytest.mark.asyncio
async def test_get_by_name_posts_the_sample_body(client):
    client.reply = {"relatedHTTPCode": 200, "elements": [{"elementHeader": {"guid": "g"}}]}
    result = await client._async_get_data_values_by_name(body=sample("getDataValuesByName"))
    method, url, body = client.calls[0]
    assert (method, url) == ("POST", _url(n.DATA_VALUES_BY_NAME))
    _assert_sample_sent(body, sample("getDataValuesByName"))
    assert result == [{"elementHeader": {"guid": "g"}}]


@pytest.mark.asyncio
async def test_get_by_name_from_a_name(client):
    client.reply = {"relatedHTTPCode": 200, "elements": []}
    await client._async_get_data_values_by_name("Threshold")
    assert client.calls[0][2]["filter"] == "Threshold"
    assert client.calls[0][2]["class"] == "FilterRequestBody"


def test_get_by_name_sync_wrapper(client):
    client.reply = {"relatedHTTPCode": 200, "elements": []}
    client.get_data_values_by_name("Threshold")
    assert client.calls[0][1] == _url(n.DATA_VALUES_BY_NAME)


@pytest.mark.asyncio
async def test_get_by_guid_posts_the_sample_body(client):
    client.reply = {"relatedHTTPCode": 200, "element": {"elementHeader": {"guid": DV_GUID}}}
    result = await client._async_get_data_value_by_guid(DV_GUID, body=sample("getDataValueByGUID"))
    method, url, body = client.calls[0]
    assert (method, url) == ("POST", _url(n.DATA_VALUES_RETRIEVE, dataValueGUID=DV_GUID))
    _assert_sample_sent(body, sample("getDataValueByGUID"))
    assert result == {"elementHeader": {"guid": DV_GUID}}


@pytest.mark.asyncio
async def test_get_by_guid_without_a_body_does_not_filter_out_literal_data_values(client):
    """A LiteralDataValue is a DataValue subtype: the default body must not narrow the result to DataValue only
    in a way that hides it. Egeria's metadataElementTypeName includes subtypes, so DataValue is safe."""
    client.reply = {"relatedHTTPCode": 200, "element": {"elementHeader": {"guid": DV_GUID}}}
    await client._async_get_data_value_by_guid(DV_GUID)
    body = client.calls[0][2]
    assert body["class"] == "GetRequestBody"
    assert body.get("metadataElementTypeName") in (None, "DataValue")


def test_get_by_guid_sync_wrapper(client):
    client.reply = {"relatedHTTPCode": 200, "element": {"elementHeader": {"guid": DV_GUID}}}
    assert client.get_data_value_by_guid(DV_GUID) == {"elementHeader": {"guid": DV_GUID}}


@pytest.mark.asyncio
async def test_find_posts_the_sample_body(client):
    client.reply = {"relatedHTTPCode": 200, "elements": [{"elementHeader": {"guid": "g"}}]}
    result = await client._async_find_data_values(body=sample("findDataValues"))
    method, url, body = client.calls[0]
    assert (method, url) == ("POST", _url(n.DATA_VALUES_BY_SEARCH_STRING))
    _assert_sample_sent(body, sample("findDataValues"))
    assert result == [{"elementHeader": {"guid": "g"}}]


@pytest.mark.asyncio
async def test_find_from_a_search_string(client):
    client.reply = {"relatedHTTPCode": 200, "elements": []}
    await client._async_find_data_values("thresh")
    body = client.calls[0][2]
    assert body["class"] == "SearchStringRequestBody" and body["searchString"] == "thresh"


def test_find_sync_wrapper(client):
    client.reply = {"relatedHTTPCode": 200, "elements": []}
    client.find_data_values("thresh")
    assert client.calls[0][1] == _url(n.DATA_VALUES_BY_SEARCH_STRING)


# --- docstrings ----------------------------------------------------------------------------------------------
LIFECYCLE = ("create_data_value", "create_data_value_from_template", "update_data_value", "delete_data_value",
             "get_data_values_by_name", "get_data_value_by_guid", "find_data_values")


@pytest.mark.parametrize("method", LIFECYCLE)
def test_docstrings_say_the_call_needs_egeria_6_4(method):
    for name in (method, f"_async_{method}"):
        doc = getattr(DataEngineer, name).__doc__ or ""
        assert "Egeria 6.4" in doc, f"{name} does not say it needs Egeria 6.4"
