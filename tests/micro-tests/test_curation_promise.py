"""
Classify/Declassify Promise (0010) through the real dispatcher and
CurationClassifyProcessor, with a fake client.

A Promise-classified element is only visible to forLineage=true requests, so
Declassify Promise must (a) resolve its Target Element with forLineage=true
and (b) send its clear request with forLineage=true -- even if the author
explicitly wrote "For Lineage: false". Editing commands default to
forLineage=true anyway (lineage_visible() around execute()); the fake client
reads that flag the same way the real request layer applies it.
"""
from typing import Any, Dict, List

import pytest

from pyegeria import NO_ELEMENTS_FOUND
from pyegeria.core._base_platform_client import _for_lineage_default

from md_processing.dr_egeria import register_curation_processors
from md_processing.v2.dispatcher import V2Dispatcher
from md_processing.v2.extraction import DrECommand

_TARGET = "DataSet::Promised Sales Feed"
_TARGET_GUID = "11111111-2222-3333-4444-555555555555"


class _FakeClassificationManager:
    def __init__(self):
        self.set_calls: List[tuple] = []
        self.clear_calls: List[tuple] = []

    async def _async_set_element_as_promise(self, element_guid, body):
        self.set_calls.append((element_guid, body))

    async def _async_clear_element_as_promise(self, element_guid, body):
        self.clear_calls.append((element_guid, body))


class _FakeClient:
    """Target is found by a normal lookup until it has been promised; after
    that only a for_lineage=True lookup finds it (as on a real server)."""

    def __init__(self, promised: bool):
        self.promised = promised
        self.lookups: List[bool] = []
        self.classification_manager = _FakeClassificationManager()

    async def __async_get_guid__(self, qualified_name=None, display_name=None, property_name="qualifiedName",
                                 tech_type=None, for_lineage=False, **kwargs):
        name = qualified_name or display_name
        if name != _TARGET:
            return NO_ELEMENTS_FOUND
        for_lineage = for_lineage or _for_lineage_default.get()
        self.lookups.append(for_lineage)
        if self.promised and not for_lineage:
            return NO_ELEMENTS_FOUND
        return _TARGET_GUID


def _dispatcher(client) -> V2Dispatcher:
    dispatcher = V2Dispatcher(client)
    register_curation_processors(dispatcher.register)
    return dispatcher


def _cmd(verb: str, attributes: Dict[str, Any]) -> DrECommand:
    raw = f"## {verb} Promise\n" + "".join(f"### {k}\n{v}\n" for k, v in attributes.items())
    return DrECommand(verb=verb, object_type="Promise", attributes=attributes, raw_block=raw)


@pytest.mark.asyncio
async def test_classify_promise_sends_promise_properties():
    client = _FakeClient(promised=False)
    results = await _dispatcher(client).dispatch_batch(
        [_cmd("Classify", {"Target Element": _TARGET, "Deployment Status": "UNDER_DEVELOPMENT",
                           "Due Time": "2026-12-31T00:00:00"})],
        {"directive": "process"},
    )

    assert results[0]["status"] == "success", results[0]
    [(guid, body)] = client.classification_manager.set_calls
    assert guid == _TARGET_GUID
    assert body["class"] == "NewClassificationRequestBody"
    assert body["properties"]["class"] == "PromiseProperties"
    assert body["properties"]["deploymentStatus"] == "UNDER_DEVELOPMENT"
    assert body["properties"]["dueTime"] == "2026-12-31T00:00:00"
    assert client.lookups and all(client.lookups)  # editing commands default to forLineage=true


@pytest.mark.asyncio
async def test_declassify_promise_uses_lineage_lookup_and_body():
    client = _FakeClient(promised=True)
    results = await _dispatcher(client).dispatch_batch(
        [_cmd("Declassify", {"Target Element": _TARGET})],
        {"directive": "process"},
    )

    assert results[0]["status"] == "success", results[0]
    [(guid, body)] = client.classification_manager.clear_calls
    assert guid == _TARGET_GUID
    assert body["class"] == "DeleteClassificationRequestBody"
    assert body["forLineage"] is True
    assert client.lookups and all(client.lookups)


@pytest.mark.asyncio
async def test_declassify_promise_ignores_explicit_for_lineage_false():
    client = _FakeClient(promised=True)
    results = await _dispatcher(client).dispatch_batch(
        [_cmd("Declassify", {"Target Element": _TARGET, "For Lineage": "false"})],
        {"directive": "process"},
    )

    assert results[0]["status"] == "success", results[0]
    [(_, body)] = client.classification_manager.clear_calls
    assert body["forLineage"] is True
