# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Egeria 6.4 A3 (odpi/egeria#9463): ProjectTarget, SupportedVariableType and the new DevopsPipeline client.

Six requests, all POST:
  project-manager   projects/{p}/project-targets/{t}/attach|detach        ProjectManager
  schema-maker      elements/{e}/supported-variable-types/{st}/attach|detach  SchemaMaker
  devops-pipeline   elements/{e}/branch and elements/{e}/branch/remove     DevopsPipeline (new)

No Egeria: the HTTP call is captured. Every path comes from pyegeria.core.egeria_6_4_names, and every
sample body from the `.http` collections in tests/fixtures/egeria-6.4/ (the PR's own samples), so a rename
in review breaks these tests rather than the calls.
"""
from __future__ import annotations

import importlib
import json
import re
from pathlib import Path

import pytest

from md_processing.md_processing_utils.properties_class_fields import PROPERTIES_CLASS_FIELDS
from pyegeria.core import egeria_6_4_names as n
from pyegeria.core._exceptions import PyegeriaException
from pyegeria.omvs.project_manager import ProjectManager
from pyegeria.omvs.schema_maker import SchemaMaker

pytestmark = pytest.mark.unit

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "egeria-6.4"
ROOT = "https://localhost:1/servers/view-server/api/open-metadata/"
TIMESTAMP = "2026-11-21T12:00:00Z"


def _sample(collection: str, name: str) -> dict:
    """The JSON body of request `name` in the collection, placeholders filled."""
    text = (FIXTURES / f"Egeria-api-{collection}.http").read_text()
    start = text.index(f"# @name {name}\n")
    block = text[start:].split("\n###", 1)[0]
    body = block[block.index("\n{"):].strip()
    body = body.replace("{{$isoTimestamp}}", TIMESTAMP)
    assert "{{" not in body, f"unfilled placeholder in {name}"
    return json.loads(body)


def _path(template: str, **guids) -> str:
    return ROOT + re.sub(r"\{(\w+)\}", lambda m: guids[m.group(1)], template)


class _Response:
    def json(self):
        return {"class": "VoidResponse", "relatedHTTPCode": 200}


def _client(cls, calls: list, monkeypatch):
    monkeypatch.setattr(cls, "check_connection", lambda self: "test", raising=False)
    client = cls("view-server", "https://localhost:1", "user", "pwd")

    async def fake_make_request(method, url, payload=None, *args, **kwargs):
        calls.append({"method": method, "url": url,
                      "body": json.loads(payload) if isinstance(payload, str) else payload})
        return _Response()

    client._async_make_request = fake_make_request
    return client


def _devops_cls():
    from pyegeria.omvs.devops_pipeline import DevopsPipeline
    return DevopsPipeline


# --- (client factory, method, path template, guid args, .http collection, sample name, properties class) ---
CASES = [
    pytest.param(lambda: ProjectManager, "_async_setup_project_target", n.PROJECT_TARGETS_ATTACH,
                 {"projectGUID": "p-guid", "targetGUID": "t-guid"}, "project-manager", "setupProjectTarget",
                 n.PROJECT_TARGET_PROPERTIES, id="setup_project_target"),
    pytest.param(lambda: ProjectManager, "_async_clear_project_target", n.PROJECT_TARGETS_DETACH,
                 {"projectGUID": "p-guid", "targetGUID": "t-guid"}, "project-manager", "clearProjectTarget",
                 None, id="clear_project_target"),
    pytest.param(lambda: SchemaMaker, "_async_link_supported_variable_type", n.SUPPORTED_VARIABLE_TYPES_ATTACH,
                 {"elementGUID": "e-guid", "schemaTypeGUID": "st-guid"}, "schema-maker",
                 "linkSupportedVariableType", n.SUPPORTED_VARIABLE_TYPE_PROPERTIES,
                 id="link_supported_variable_type"),
    pytest.param(lambda: SchemaMaker, "_async_detach_supported_variable_type", n.SUPPORTED_VARIABLE_TYPES_DETACH,
                 {"elementGUID": "e-guid", "schemaTypeGUID": "st-guid"}, "schema-maker",
                 "detachSupportedVariableType", None, id="detach_supported_variable_type"),
    pytest.param(_devops_cls, "_async_set_element_as_branch", n.BRANCH_SET, {"elementGUID": "e-guid"},
                 "devops-pipeline", "setElementAsBranch", n.BRANCH_PROPERTIES, id="set_element_as_branch"),
    pytest.param(_devops_cls, "_async_clear_element_as_branch", n.BRANCH_REMOVE, {"elementGUID": "e-guid"},
                 "devops-pipeline", "clearElementAsBranch", None, id="clear_element_as_branch"),
]
ATTACH_CASES = [c for c in CASES if c.values[6] is not None]


@pytest.mark.asyncio
@pytest.mark.parametrize("factory, method, template, guids, collection, sample, props_class", CASES)
async def test_path_method_and_body_equal_the_http_sample(factory, method, template, guids, collection, sample,
                                                          props_class, monkeypatch):
    calls: list = []
    client = _client(factory(), calls, monkeypatch)
    body = _sample(collection, sample)

    await getattr(client, method)(*guids.values(), body)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert calls[0]["url"] == _path(template, **guids)
    assert calls[0]["body"] == body


@pytest.mark.asyncio
@pytest.mark.parametrize("factory, method, template, guids, collection, sample, props_class", ATTACH_CASES)
async def test_attach_with_no_body_sends_no_body(factory, method, template, guids, collection, sample,
                                                 props_class, monkeypatch):
    calls: list = []
    client = _client(factory(), calls, monkeypatch)

    await getattr(client, method)(*guids.values())

    assert calls == [{"method": "POST", "url": _path(template, **guids), "body": None}]


@pytest.mark.asyncio
@pytest.mark.parametrize("factory, method, template, guids, collection, sample, props_class", ATTACH_CASES)
async def test_wrong_properties_class_is_refused_locally(factory, method, template, guids, collection, sample,
                                                         props_class, monkeypatch):
    calls: list = []
    client = _client(factory(), calls, monkeypatch)
    body = _sample(collection, sample)
    body["properties"]["class"] = "ReferenceableProperties"   # a parent class: the TR-89 silent-drop case

    with pytest.raises(PyegeriaException) as raised:
        await getattr(client, method)(*guids.values(), body)

    assert calls == [], "nothing may reach Egeria"
    assert props_class in str(raised.value), "the words must name the class the call needs"


@pytest.mark.asyncio
@pytest.mark.parametrize("factory, method, template, guids, collection, sample, props_class", ATTACH_CASES)
async def test_properties_with_no_class_are_refused_locally(factory, method, template, guids, collection, sample,
                                                            props_class, monkeypatch):
    calls: list = []
    client = _client(factory(), calls, monkeypatch)
    body = _sample(collection, sample)
    del body["properties"]["class"]

    with pytest.raises(PyegeriaException) as raised:
        await getattr(client, method)(*guids.values(), body)

    assert calls == []
    assert props_class in str(raised.value)


@pytest.mark.asyncio
@pytest.mark.parametrize("factory, method, template, guids, collection, sample, props_class", ATTACH_CASES)
async def test_a_key_the_class_does_not_read_is_refused_locally(factory, method, template, guids, collection,
                                                                sample, props_class, monkeypatch):
    """Egeria ignores unknown keys silently (the TR-89 libraryType drop), so the client refuses them."""
    calls: list = []
    client = _client(factory(), calls, monkeypatch)
    body = _sample(collection, sample)
    body["properties"]["notARealProperty"] = "x"

    with pytest.raises(PyegeriaException) as raised:
        await getattr(client, method)(*guids.values(), body)

    assert calls == []
    assert "notARealProperty" in str(raised.value)


# --- Branch --------------------------------------------------------------------------------------------------

def test_branch_properties_have_no_label_or_description():
    kind, keys = PROPERTIES_CLASS_FIELDS[n.BRANCH_PROPERTIES]
    assert kind == "classification"
    assert "label" not in keys and "description" not in keys
    assert {"displayName", "scope", "purpose", "url"} <= set(keys)
    assert "label" not in _sample("devops-pipeline", "setElementAsBranch")["properties"]


@pytest.mark.asyncio
@pytest.mark.parametrize("key", ["label", "description"])
async def test_set_element_as_branch_refuses_label_and_description(key, monkeypatch):
    calls: list = []
    client = _client(_devops_cls(), calls, monkeypatch)
    body = _sample("devops-pipeline", "setElementAsBranch")
    body["properties"][key] = "would be dropped by Egeria"

    with pytest.raises(PyegeriaException) as raised:
        await client._async_set_element_as_branch("e-guid", body)

    assert calls == []
    assert key in str(raised.value)


@pytest.mark.asyncio
async def test_set_element_as_branch_builds_the_body_from_keywords(monkeypatch):
    calls: list = []
    client = _client(_devops_cls(), calls, monkeypatch)

    await client._async_set_element_as_branch("e-guid", display_name="main", scope="repo",
                                              purpose="default branch", url="https://example.org/r/tree/main")

    assert calls[0]["body"] == {
        "class": "NewClassificationRequestBody",
        "properties": {"class": "BranchProperties", "displayName": "main", "scope": "repo",
                       "purpose": "default branch", "url": "https://example.org/r/tree/main"},
    }


@pytest.mark.asyncio
async def test_set_element_as_branch_refuses_body_and_keywords_together(monkeypatch):
    calls: list = []
    client = _client(_devops_cls(), calls, monkeypatch)

    with pytest.raises(PyegeriaException):
        await client._async_set_element_as_branch("e-guid", _sample("devops-pipeline", "setElementAsBranch"),
                                                  display_name="main")
    assert calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("body", [None, {"externalSourceName": "src"}])
async def test_clear_element_as_branch_sends_a_metadata_source_request_body(body, monkeypatch):
    calls: list = []
    client = _client(_devops_cls(), calls, monkeypatch)

    await client._async_clear_element_as_branch("e-guid", body)

    assert calls[0]["url"] == _path(n.BRANCH_REMOVE, elementGUID="e-guid")
    assert calls[0]["body"]["class"] == "MetadataSourceRequestBody"
    if body:
        assert calls[0]["body"]["externalSourceName"] == "src"


@pytest.mark.asyncio
async def test_clear_element_as_branch_refuses_another_body_class(monkeypatch):
    calls: list = []
    client = _client(_devops_cls(), calls, monkeypatch)

    with pytest.raises(PyegeriaException) as raised:
        await client._async_clear_element_as_branch("e-guid", {"class": "DeleteClassificationRequestBody"})

    assert calls == []
    assert "MetadataSourceRequestBody" in str(raised.value)


# --- Wrong request-body class, detach with no body, sync wrappers, docstrings -------------------------------

@pytest.mark.asyncio
@pytest.mark.parametrize("factory, method, template, guids, collection, sample, props_class", ATTACH_CASES)
async def test_wrong_request_body_class_is_refused_locally(factory, method, template, guids, collection, sample,
                                                           props_class, monkeypatch):
    calls: list = []
    client = _client(factory(), calls, monkeypatch)
    body = _sample(collection, sample)
    body["class"] = "UpdateRelationshipRequestBody"

    with pytest.raises(PyegeriaException):
        await getattr(client, method)(*guids.values(), body)
    assert calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("factory, method, template, guids",
                         [pytest.param(*c.values[:4], id=c.id) for c in CASES
                          if c.values[6] is None and "branch" not in c.id])
async def test_detach_with_no_body_sends_no_body(factory, method, template, guids, monkeypatch):
    calls: list = []
    client = _client(factory(), calls, monkeypatch)

    await getattr(client, method)(*guids.values())

    assert calls == [{"method": "POST", "url": _path(template, **guids), "body": None}]


@pytest.mark.parametrize("factory, method, template, guids, collection, sample, props_class", CASES)
def test_sync_wrapper_sends_the_same_request(factory, method, template, guids, collection, sample, props_class,
                                             monkeypatch):
    calls: list = []
    client = _client(factory(), calls, monkeypatch)
    body = _sample(collection, sample)

    getattr(client, method.removeprefix("_async_"))(*guids.values(), body)

    assert calls[0]["url"] == _path(template, **guids)
    assert calls[0]["body"] == body


@pytest.mark.parametrize("factory, method, template, guids, collection, sample, props_class", CASES)
def test_docstrings_say_the_call_needs_egeria_6_4(factory, method, template, guids, collection, sample,
                                                  props_class):
    cls = factory()
    for name in (method, method.removeprefix("_async_")):
        assert "Egeria 6.4" in (getattr(cls, name).__doc__ or ""), name


# --- The new client is importable from every place its siblings are -----------------------------------------

def test_devops_pipeline_is_exported_where_its_siblings_are():
    cls = _devops_cls()
    for module_name in ("pyegeria", "pyegeria.omvs"):
        module = importlib.import_module(module_name)
        assert getattr(module, "SchemaMaker") is SchemaMaker  # the sibling, as the reference
        assert getattr(module, "DevopsPipeline") is cls, module_name
        assert "DevopsPipeline" in module.__all__, module_name


@pytest.mark.parametrize("module_name, class_name", [("pyegeria.egeria_client", "Egeria"),
                                                     ("pyegeria.egeria_tech_client", "EgeriaTech")])
def test_devops_pipeline_is_registered_in_the_composite_clients(module_name, class_name):
    cls = _devops_cls()
    composite = getattr(importlib.import_module(module_name), class_name)("view-server", "https://localhost:1",
                                                                         "user", "pwd")
    assert composite._subclient_map["devops_pipeline"] is cls
    assert composite._subclient_map["schema_maker"] is SchemaMaker
    assert composite._subclient_map["project_manager"] is ProjectManager


def test_devops_pipeline_url_marker_and_base_url(monkeypatch):
    client = _client(_devops_cls(), [], monkeypatch)
    assert client.url_marker == n.DEVOPS_PIPELINE
    assert client.devops_pipeline_command_root == ROOT + n.DEVOPS_PIPELINE
