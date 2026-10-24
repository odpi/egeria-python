"""
ISSUE-162: an Update that doesn't mention a property must not change it.
- Update Glossary Term sent isAbstractConcept/isActivityDescription/isContext/isDataValue
  = False whenever the document omitted them.
- Update Data Value Specification / Data Class sent allowsDuplicateValues/isNullable = True
  and empty lists/maps/0 for several properties, so an update reset them.
Defaults now apply only on Create. No live server: the client is mocked.
"""
from unittest.mock import AsyncMock

import pytest

from md_processing.v2.data_designer import DataClassProcessor, DataValueSpecificationProcessor
from md_processing.v2.extraction import DrECommand
from md_processing.v2.glossary import TermProcessor

GUID = "11111111-1111-1111-1111-111111111111"
TERM_FLAGS = ("isAbstractConcept", "isActivityDescription", "isContext", "isDataValue")
DV_DEFAULTED = {
    "matchPropertyNames": [], "matchThreshold": 0, "specificationDetails": {},
    "allowsDuplicateValues": True, "isNullable": True, "sampleValues": [],
    "dataPatterns": [], "additionalProperties": {},
}


def _processor(cls, verb, object_type, attributes, client, om_type=None, guid=None):
    cmd = DrECommand(verb=verb, object_type=object_type, attributes=attributes, raw_block=f"{verb} {object_type}")
    proc = cls(client, cmd)
    proc.parsed_output = {"attributes": attributes, "qualified_name": attributes["Qualified Name"]["value"],
                          "valid": True}
    if guid:
        proc.parsed_output["guid"] = guid
    if om_type:
        proc.get_command_spec = lambda: {"OM_TYPE": om_type}
    proc.render_result_markdown = AsyncMock(return_value="# Result")
    return proc


def _term_attrs(**extra):
    attrs = {"Display Name": {"value": "T"}, "Qualified Name": {"value": "GlossaryTerm::T"},
             "Description": {"value": "new description"}}
    attrs.update(extra)
    return attrs


async def test_term_update_without_flags_sends_none_of_them():
    client = AsyncMock()
    client._async_get_related_elements.return_value = []
    proc = _processor(TermProcessor, "Update", "Glossary Term", _term_attrs(), client, guid=GUID)
    await proc.apply_changes()

    body = client._async_update_glossary_term.call_args.args[1]
    for flag in TERM_FLAGS:
        assert flag not in body["properties"], flag
    assert body["properties"]["description"] == "new description"


async def test_term_update_sends_a_flag_the_document_sets():
    client = AsyncMock()
    client._async_get_related_elements.return_value = []
    proc = _processor(TermProcessor, "Update", "Glossary Term", _term_attrs(**{"Is Context": {"value": True}}),
                      client, guid=GUID)
    await proc.apply_changes()

    props = client._async_update_glossary_term.call_args.args[1]["properties"]
    assert props["isContext"] is True
    assert "isAbstractConcept" not in props


async def test_term_create_still_defaults_flags_to_false():
    client = AsyncMock()
    client._async_create_glossary_term.return_value = GUID
    proc = _processor(TermProcessor, "Create", "Glossary Term", _term_attrs(), client)
    await proc.apply_changes()

    call = client._async_create_glossary_term.call_args
    props = (call.kwargs.get("body") or call.args[0])["properties"]
    for flag in TERM_FLAGS:
        assert props[flag] is False, flag


def _dv_attrs():
    return {"Display Name": {"value": "D"}, "Qualified Name": {"value": "DataValueSpecification::D"},
            "Description": {"value": "changed"}}


@pytest.mark.parametrize("cls, om_type", [(DataValueSpecificationProcessor, "DataValueSpecification"),
                                          (DataClassProcessor, "DataClass")])
async def test_data_designer_update_does_not_send_defaults(cls, om_type):
    client = AsyncMock()
    proc = _processor(cls, "Update", "Data Value Specification", _dv_attrs(), client, om_type=om_type, guid=GUID)
    proc._sync_value_spec_parent = AsyncMock()
    proc._sync_all_rels = AsyncMock()
    await proc.apply_changes()

    props = client.data_designer._async_update_data_value_specification.call_args.args[1]["properties"]
    for key in DV_DEFAULTED:
        # None is dropped by body_slimmer before sending; anything else would overwrite Egeria's value
        assert props.get(key) is None, key
    assert props["description"] == "changed"


@pytest.mark.parametrize("cls, om_type, create_method", [
    (DataValueSpecificationProcessor, "DataValueSpecification", "_async_create_data_value_specification"),
    (DataClassProcessor, "DataClass", "_async_create_data_class")])
async def test_data_designer_create_keeps_defaults(cls, om_type, create_method):
    client = AsyncMock()
    getattr(client.data_designer, create_method).return_value = GUID
    proc = _processor(cls, "Create", "Data Value Specification", _dv_attrs(), client, om_type=om_type)
    proc._sync_value_spec_parent = AsyncMock()
    proc._sync_all_rels = AsyncMock()
    await proc.apply_changes()

    props = getattr(client.data_designer, create_method).call_args.args[0]["properties"]
    for key, default in DV_DEFAULTED.items():
        assert props[key] == default, key
