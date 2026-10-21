"""
ISSUE-152: five update methods passed the body positionally into
_async_update_element_body_request(url, prop=None, body=None), so it landed in
`prop`, `body` was None, and the call failed before sending anything
("'NoneType' object has no attribute 'model_dump_json'").
No live server: the HTTP call is captured and the body asserted.
"""
import json

import pytest

from pyegeria.models import UpdateElementRequestBody
from pyegeria.omvs.data_discovery import DataDiscovery
from pyegeria.omvs.schema_maker import SchemaMaker
from pyegeria.omvs.subject_area import SubjectArea
from pyegeria.omvs.time_keeper import TimeKeeper

GUID = "44444444-4444-4444-4444-444444444444"

CASES = [
    (DataDiscovery, "_async_update_annotation", "AnnotationProperties",
     f"/api/open-metadata/data-discovery/annotations/{GUID}/update"),
    (TimeKeeper, "_async_update_context_event", "ContextEventProperties",
     f"/api/open-metadata/time-keeper/context-events/{GUID}/update"),
    (SchemaMaker, "_async_update_schema_type", "SchemaTypeProperties",
     f"/api/open-metadata/schema-maker/schema-types/{GUID}/update"),
    (SchemaMaker, "_async_update_schema_attribute", "SchemaAttributeProperties",
     f"/api/open-metadata/schema-maker/schema-attributes/{GUID}/update"),
    (SubjectArea, "_async_update_subject_area", "SubjectAreaProperties",
     f"/api/open-metadata/subject-area/collections/{GUID}/update"),
]
IDS = [c[1] for c in CASES]


class _Response:
    def json(self):
        return {"class": "VoidResponse"}


def _client(cls, calls: list, monkeypatch):
    monkeypatch.setattr(cls, "check_connection", lambda self: "test")
    client = cls("view-server", "https://localhost:1", "user", "pwd")

    async def fake_make_request(method, url, payload=None, *args, **kwargs):
        calls.append({"method": method, "url": url,
                      "body": json.loads(payload) if isinstance(payload, str) else payload})
        return _Response()

    client._async_make_request = fake_make_request
    return client


def _body(prop_class: str) -> dict:
    return {"class": "UpdateElementRequestBody", "mergeUpdate": True,
            "properties": {"class": prop_class, "displayName": "pyeg-test"}}


@pytest.mark.asyncio
@pytest.mark.parametrize("cls, method, prop_class, path", CASES, ids=IDS)
async def test_update_sends_dict_body(cls, method, prop_class, path, monkeypatch):
    calls = []
    client = _client(cls, calls, monkeypatch)
    await getattr(client, method)(GUID, _body(prop_class))

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert calls[0]["url"].endswith(path)
    assert calls[0]["body"]["class"] == "UpdateElementRequestBody"
    assert calls[0]["body"]["properties"] == {"class": prop_class, "displayName": "pyeg-test"}


@pytest.mark.asyncio
@pytest.mark.parametrize("cls, method, prop_class, path", CASES, ids=IDS)
async def test_update_sends_model_body(cls, method, prop_class, path, monkeypatch):
    calls = []
    client = _client(cls, calls, monkeypatch)
    await getattr(client, method)(GUID, UpdateElementRequestBody.model_validate(_body(prop_class)))

    assert len(calls) == 1
    assert calls[0]["url"].endswith(path)
    assert calls[0]["body"]["properties"]["class"] == prop_class
