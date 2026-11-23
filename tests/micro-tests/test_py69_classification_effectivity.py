"""PY-69: every Dr.Egeria classification command sends Effective From, Effective To and Extended Properties
(inherited from Request Base); before, only the fields a classification mapped by hand reached Egeria."""
import asyncio
import json
import os
from typing import Any, List

import pytest

from pyegeria import NO_ELEMENTS_FOUND
from md_processing.dr_egeria import register_curation_processors
from md_processing.v2.curation import CLASSIFICATION_METHODS, CURATION_CLASSIFICATION_CLIENTS
from md_processing.v2.dispatcher import V2Dispatcher
from md_processing.v2.extraction import DrECommand

_ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "md_processing", "data", "compact_commands")
_FAMILY = json.load(open(os.path.join(_ROOT, "commands_curation_compact.json")))
_GUID = "11111111-2222-3333-4444-555555555555"
_TARGET = "Referenceable::PY-69 target"

THREE = {"Effective From": ("effectiveFrom", "2026-01-01T00:00:00"),
         "Effective To": ("effectiveTo", "2027-01-01T00:00:00"),
         "Extended Properties": ("extendedProperties", '{"owner": "ops"}')}


def _classify_commands():
    out = []
    for name, cmd in _FAMILY["commands"].items():
        if cmd["verb"] == "Classify" and cmd.get("OM_TYPE") in CLASSIFICATION_METHODS:
            out.append((name, cmd["OM_TYPE"], name[len("Classify "):]))
    return sorted(out)


class _Recorder:
    def __init__(self):
        self.calls: List[tuple] = []

    def __getattr__(self, method):
        if method.startswith("__"):
            raise AttributeError(method)

        async def _call(guid, body=None, *args, **kwargs):
            self.calls.append((method, guid, body))
        return _call


class _FakeClient:
    def __init__(self):
        self.recorders = {}

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return self.recorders.setdefault(name, _Recorder())

    async def __async_get_guid__(self, qualified_name=None, display_name=None, **kwargs):
        return _GUID if (qualified_name or display_name) == _TARGET else NO_ELEMENTS_FOUND


def _dispatch(command_name, object_type, extra=None):
    client = _FakeClient()
    dispatcher = V2Dispatcher(client)
    register_curation_processors(dispatcher.register)
    attrs = {"Target Element": _TARGET, **{k: v for k, (_, v) in THREE.items()}, **(extra or {})}
    raw = f"## Classify {object_type}\n" + "".join(f"### {k}\n{v}\n" for k, v in attrs.items())
    cmd = DrECommand(verb="Classify", object_type=object_type, attributes=attrs, raw_block=raw)
    result = asyncio.run(dispatcher.dispatch_batch([cmd], {"directive": "process"}))[0]
    sent = [c for r in client.recorders.values() for c in r.calls if isinstance(c[2], dict) and 'properties' in c[2]]
    return result, sent


@pytest.mark.parametrize("command,om_type,object_type", _classify_commands(), ids=[c[0] for c in _classify_commands()])
def test_every_classify_command_sends_the_effectivity_and_extended_properties(command, om_type, object_type):
    if om_type == "Retention":
        pytest.skip("Retention is sent as RetentionClassificationProperties; covered by the generic builder test")
    result, sent = _dispatch(command, object_type)
    assert result["status"] == "success", (command, result)
    assert len(sent) == 1, (command, sent)
    props = sent[0][2]["properties"]
    for attr, (prop, value) in THREE.items():
        want = {"owner": "ops"} if prop == "extendedProperties" else value
        assert props.get(prop) == want, (command, prop, props)


def test_the_builder_sends_the_three_for_a_spec_with_no_fields_of_its_own():
    from md_processing.v2.curation import _build_classification_properties
    spec = CLASSIFICATION_METHODS["KnownDuplicate"]
    assert not spec.fields
    attrs = {"Effective From": {"value": "2026-01-01T00:00:00"}, "Effective To": {"value": None},
             "Extended Properties": {"value": {"a": "b"}}}
    assert _build_classification_properties(spec, attrs) == {
        "class": spec.props_class, "effectiveFrom": "2026-01-01T00:00:00", "extendedProperties": {"a": "b"}}


def test_a_blank_one_is_not_sent_and_a_spec_field_is_not_overridden():
    from md_processing.v2.curation import _build_classification_properties
    props = _build_classification_properties(CLASSIFICATION_METHODS["Ownership"], {"Owner": {"value": "erin"}})
    assert props == {"class": "OwnershipProperties", "owner": "erin"}


def test_the_data_scope_fields_are_not_listed_twice():
    spec = CLASSIFICATION_METHODS["DataScope"]
    assert "Effective From" not in spec.fields  # sent by the shared rule, once
