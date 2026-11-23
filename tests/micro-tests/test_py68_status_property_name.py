"""PY-68: the Status attribute is looked up in Egeria as the valid-metadata property `status`
(Egeria:ValidMetadataValue::status-: ACTIVE, DELETED, INVALID, OTHER, UNKNOWN); the capital-S "Status" matches
nothing, so templates carried no values."""
import json
import pathlib

import md_processing.md_processing_utils.md_processing_constants as m

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _walk(o):
    if isinstance(o, dict):
        yield o
        for v in o.values():
            yield from _walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v)


def test_no_compact_attribute_uses_capital_S_Status_as_property_name():
    bad = []
    for f in sorted((ROOT / "md_processing/data/compact_commands").glob("*.json")):
        for d in _walk(json.loads(f.read_text()).get("attribute_definitions", {})):
            if d.get("property_name") == "Status":
                bad.append(f.name)
    assert bad == []


def test_the_default_upsert_status_looks_up_status():
    out = m.add_default_upsert_attributes([])
    status = [a for a in out if a.get("name") == "Status"]
    assert len(status) == 1 and status[0]["property_name"] == "status"


def test_no_expanded_command_attribute_looks_up_capital_S_Status():
    m.load_commands()
    bad = {(d.get("name"), d.get("variable_name"))
           for d in _walk(m.COMMAND_DEFINITIONS) if d.get("property_name") == "Status"}
    assert bad == set()


def test_a_compact_status_attribute_gets_status_when_the_defaults_are_applied():
    out = m.add_default_upsert_attributes([{"name": "Status", "variable_name": "status", "valid_values": [],
                                            "style": "Simple"}])
    assert [a["property_name"] for a in out if a["name"] == "Status"] == ["status"]
