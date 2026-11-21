# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""A2b for the Egeria 6.4 additions (odpi/egeria#9463): the three data-value link pairs on DataEngineer
(DataValueSource, ProcessingVariable and EmbeddedDataValue, attach and detach). No Egeria:
`_async_make_request` is replaced by a recorder, and each body is compared with the sample body in the PR's
`.http` collection (tests/fixtures/egeria-6.4/Egeria-api-data-engineer.http).

Covered for each request: the URL path and HTTP method; the body sent; attach and detach with no body send no
body; a `properties.class` of the wrong relationship is refused locally, naming the expected class; and
`position` (ProcessingVariable, EmbeddedDataValue) is an int, 0 meaning unset, passed through unchanged.
"""
import copy
import json
import re
from pathlib import Path

import pytest

from pyegeria.core import egeria_6_4_names as n
from pyegeria.core._exceptions import PyegeriaInvalidParameterException
from pyegeria.models import NewRelationshipRequestBody
from pyegeria.omvs.data_engineer import DataEngineer

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "egeria-6.4" / "Egeria-api-data-engineer.http"
PLATFORM = "https://localhost:1"
SERVER = "view-server"
ROOT = f"{PLATFORM}/servers/{SERVER}/api/open-metadata/"
TIMESTAMP = "2026-11-21T10:00:00Z"


def _samples() -> dict[str, dict]:
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

    async def fake_make_request(method, url, payload=None, *args, **kwargs):
        body = json.loads(payload) if isinstance(payload, str) else payload
        c.calls.append((method, url, body))
        return _Response({"class": "GUIDResponse", "relatedHTTPCode": 200, "guid": "rel-guid"})

    c._async_make_request = fake_make_request
    return c


# (method stem, path for attach, path for detach, the two GUID placeholders, attach sample, detach sample,
#  the properties class, whether it has a position)
PAIRS = [
    ("data_value_source", n.DATA_VALUE_SOURCES_ATTACH, n.DATA_VALUE_SOURCES_DETACH, ("dataValueGUID", "assetGUID"),
     "linkDataValueSource", "detachDataValueSource", n.DATA_VALUE_SOURCE_PROPERTIES, False),
    ("processing_variable", n.PROCESSING_VARIABLES_ATTACH, n.PROCESSING_VARIABLES_DETACH,
     ("elementGUID", "dataValueGUID"), "linkProcessingVariable", "detachProcessingVariable",
     n.PROCESSING_VARIABLE_PROPERTIES, True),
    ("embedded_data_value", n.EMBEDDED_DATA_VALUES_ATTACH, n.EMBEDDED_DATA_VALUES_DETACH,
     ("parentDataValueGUID", "embeddedDataValueGUID"), "linkEmbeddedDataValue", "detachEmbeddedDataValue",
     n.EMBEDDED_DATA_VALUE_PROPERTIES, True),
]
IDS = [p[0] for p in PAIRS]
GUID1, GUID2 = "guid-one", "guid-two"


def _url(path: str, names: tuple[str, str]) -> str:
    return ROOT + path.format(**{names[0]: GUID1, names[1]: GUID2})


@pytest.mark.asyncio
@pytest.mark.parametrize("pair", PAIRS, ids=IDS)
async def test_link_posts_the_sample_body_and_returns_the_relationship_guid(client, pair):
    stem, attach, _, names, link_sample, *_ = pair
    guid = await getattr(client, f"_async_link_{stem}")(GUID1, GUID2, sample(link_sample))
    assert guid == "rel-guid"
    assert client.calls == [("POST", _url(attach, names), sample(link_sample))]


@pytest.mark.asyncio
@pytest.mark.parametrize("pair", PAIRS, ids=IDS)
async def test_link_with_no_body_sends_no_body(client, pair):
    stem, attach, _, names, *_ = pair
    await getattr(client, f"_async_link_{stem}")(GUID1, GUID2)
    assert client.calls == [("POST", _url(attach, names), None)]


@pytest.mark.asyncio
@pytest.mark.parametrize("pair", PAIRS, ids=IDS)
async def test_link_with_a_body_but_no_properties_is_sent(client, pair):
    stem, attach, _, names, *_ = pair
    body = {"class": "NewRelationshipRequestBody", "forLineage": False}
    await getattr(client, f"_async_link_{stem}")(GUID1, GUID2, body)
    assert client.calls == [("POST", _url(attach, names), body)]


@pytest.mark.asyncio
@pytest.mark.parametrize("pair", PAIRS, ids=IDS)
async def test_link_accepts_a_model_body(client, pair):
    stem, attach, _, names, link_sample, _, cls, _ = pair
    await getattr(client, f"_async_link_{stem}")(GUID1, GUID2,
                                                 NewRelationshipRequestBody.model_validate(sample(link_sample)))
    assert client.calls[0][2]["properties"] == sample(link_sample)["properties"]
    assert client.calls[0][2]["properties"]["class"] == cls


@pytest.mark.asyncio
@pytest.mark.parametrize("pair", PAIRS, ids=IDS)
async def test_link_with_the_wrong_properties_class_is_refused_naming_the_expected_class(client, pair):
    stem, _, _, _, link_sample, _, cls, _ = pair
    body = sample(link_sample)
    body["properties"]["class"] = "AssessmentProperties"
    with pytest.raises(PyegeriaInvalidParameterException) as err:
        await getattr(client, f"_async_link_{stem}")(GUID1, GUID2, body)
    assert cls in str(err.value) and "AssessmentProperties" in str(err.value)
    assert client.calls == []


@pytest.mark.parametrize("pair", PAIRS, ids=IDS)
def test_link_sync_wrapper(client, pair):
    stem, attach, _, names, link_sample, *_ = pair
    assert getattr(client, f"link_{stem}")(GUID1, GUID2, sample(link_sample)) == "rel-guid"
    assert client.calls[0][1] == _url(attach, names)


@pytest.mark.asyncio
@pytest.mark.parametrize("pair", PAIRS, ids=IDS)
async def test_detach_posts_the_sample_body(client, pair):
    stem, _, detach, names, _, detach_sample, *_ = pair
    await getattr(client, f"_async_detach_{stem}")(GUID1, GUID2, sample(detach_sample))
    assert client.calls == [("POST", _url(detach, names), sample(detach_sample))]


@pytest.mark.asyncio
@pytest.mark.parametrize("pair", PAIRS, ids=IDS)
async def test_detach_with_no_body_sends_no_body(client, pair):
    stem, _, detach, names, *_ = pair
    await getattr(client, f"_async_detach_{stem}")(GUID1, GUID2)
    assert client.calls == [("POST", _url(detach, names), None)]


@pytest.mark.parametrize("pair", PAIRS, ids=IDS)
def test_detach_sync_wrapper(client, pair):
    stem, _, detach, names, *_ = pair
    assert getattr(client, f"detach_{stem}")(GUID1, GUID2) is None
    assert client.calls[0][1] == _url(detach, names)


# --- position -----------------------------------------------------------------------------------------------
POSITIONED = [p for p in PAIRS if p[7]]


@pytest.mark.asyncio
@pytest.mark.parametrize("position", [0, 1, 7])
@pytest.mark.parametrize("pair", POSITIONED, ids=[p[0] for p in POSITIONED])
async def test_position_is_an_int_passed_through_and_zero_means_unset(client, pair, position):
    stem, _, _, _, link_sample, *_ = pair
    body = sample(link_sample)
    body["properties"]["position"] = position
    await getattr(client, f"_async_link_{stem}")(GUID1, GUID2, body)
    sent = client.calls[0][2]["properties"]["position"]
    assert sent == position and type(sent) is int


@pytest.mark.asyncio
@pytest.mark.parametrize("bad", ["3", 2.5, True])
@pytest.mark.parametrize("pair", POSITIONED, ids=[p[0] for p in POSITIONED])
async def test_a_position_that_is_not_an_int_is_refused(client, pair, bad):
    stem, _, _, _, link_sample, *_ = pair
    body = sample(link_sample)
    body["properties"]["position"] = bad
    with pytest.raises(PyegeriaInvalidParameterException) as err:
        await getattr(client, f"_async_link_{stem}")(GUID1, GUID2, body)
    assert "position" in str(err.value)
    assert client.calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("pair", POSITIONED, ids=[p[0] for p in POSITIONED])
async def test_position_may_be_left_out(client, pair):
    stem, _, _, _, link_sample, *_ = pair
    body = sample(link_sample)
    del body["properties"]["position"]
    await getattr(client, f"_async_link_{stem}")(GUID1, GUID2, body)
    assert "position" not in client.calls[0][2]["properties"]


# --- docstrings ----------------------------------------------------------------------------------------------
@pytest.mark.parametrize("method", [f"{verb}_{p[0]}" for p in PAIRS for verb in ("link", "detach")])
def test_docstrings_say_the_call_needs_egeria_6_4(method):
    for name in (method, f"_async_{method}"):
        doc = getattr(DataEngineer, name).__doc__ or ""
        assert "Egeria 6.4" in doc, f"{name} does not say it needs Egeria 6.4"
