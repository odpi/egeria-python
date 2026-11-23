# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Egeria 6.4 Phase B2: the Dr.Egeria Data Engineer commands for Data Values (odpi/egeria#9463, model 0208).

Each command's sample document goes through the real extractor, dispatcher and processor, into the real A6
DataEngineer wrapper, whose HTTP call is captured (tests/micro-tests/e64_dre_harness.py). The test checks the exact
body the wrapper sends, so its own checks (properties class, unread keys, int positions) passed too.

Also: a Literal Value / List / Map selects LiteralDataValue; Position must be a whole number and is sent only when
given; and the version gate ("needs Egeria 6.4", a FAILURE row since PY-48, nothing sent) for the family.

No live server.
"""
import importlib.util
import json
import pathlib
import sys

import pytest

_spec = importlib.util.spec_from_file_location("e64_dre_harness",
                                               pathlib.Path(__file__).with_name("e64_dre_harness.py"))
h = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h)

DV = "b0000000-0000-4000-8000-000000000001"
DV2 = "b0000000-0000-4000-8000-000000000002"
ASSET = "c0000000-0000-4000-8000-000000000001"
PROCESS = "e0000000-0000-4000-8000-000000000002"

LINK_BASE = {"class": "NewRelationshipRequestBody", "forLineage": False, "forDuplicateProcessing": False,
             "makeAnchor": False}
DELETE_BASE = {"class": "DeleteRelationshipRequestBody", "forLineage": False, "forDuplicateProcessing": False}
CREATE_BASE = {"class": "NewElementRequestBody", "forLineage": False, "forDuplicateProcessing": False,
               "isOwnAnchor": True, "parentAtEnd1": True}


def _creates(fake):
    return [c for c in fake.calls if c["path"] == "data-engineer/data-values"]


# --------------------------------------------------------------------------------------------- Data Value

@pytest.mark.asyncio
async def test_create_data_value_sends_data_value_properties(monkeypatch):
    fake = h.FakeEgeria(monkeypatch)
    [result] = await h.run_doc(fake, """
## Create Data Value
### Display Name
Retry limit B2-plain
### Description
How many times a step retries.
### Data Format
integer
### Length
3
### Data Type
int
### Usage
Process configuration.
### Fingerprint
ab12
### Fingerprint Algorithm
simhash
### Hash
1234567890123
### Hash Algorithm
crc64
""")
    assert result["status"] == "success", result
    [create] = _creates(fake)
    assert create["body"] == {**CREATE_BASE, "properties": {
        "class": "DataValueProperties", "typeName": "DataValue", "displayName": "Retry limit B2-plain",
        "qualifiedName": "DataValue::Retry limit B2-plain", "description": "How many times a step retries.",
        "dataFormat": "integer", "length": 3, "dataType": "int", "usage": "Process configuration.",
        "fingerprint": "ab12", "fingerprintAlgorithm": "simhash", "hash": 1234567890123,
        "hashAlgorithm": "crc64"}}


@pytest.mark.asyncio
@pytest.mark.parametrize("literal, expected", [
    ("### Literal Value\n42\n", {"dataValue": "42"}),
    ("### Literal Value List\n- red\n- amber\n- green\n", {"dataValueList": ["red", "amber", "green"]}),
    ("### Literal Value Map\nlow: 1\nhigh: 9\n", {"dataValueMap": {"low": "1", "high": "9"}}),
])
async def test_a_literal_value_list_or_map_makes_a_literal_data_value(monkeypatch, literal, expected):
    fake = h.FakeEgeria(monkeypatch)
    name = f"Threshold B2-{next(iter(expected))}"
    [result] = await h.run_doc(fake, f"## Create Data Value\n### Display Name\n{name}\n### Data Type\nstring\n{literal}")
    assert result["status"] == "success", result
    [create] = _creates(fake)
    assert create["body"] == {**CREATE_BASE, "properties": {
        "class": "LiteralDataValueProperties", "typeName": "LiteralDataValue", "displayName": name,
        "qualifiedName": f"DataValue::{name}", "dataType": "string", **expected}}


def _existing(qn, guid, type_name):
    def respond(method, path, body):
        if path.endswith(f"data-values/{guid}/retrieve"):
            return {"class": "DataValueResponse", "relatedHTTPCode": 200,
                    "element": {"elementHeader": {"guid": guid, "type": {"typeName": type_name}},
                                "properties": {"qualifiedName": qn}}}
        return None
    return respond


@pytest.mark.asyncio
async def test_update_of_a_literal_data_value_keeps_its_class(monkeypatch):
    qn = "DataValue::Threshold B2-update"
    fake = h.FakeEgeria(monkeypatch, names={qn: DV}, respond=_existing(qn, DV, "LiteralDataValue"))
    [result] = await h.run_doc(fake, "## Update Data Value\n### Display Name\nThreshold B2-update\n### Usage\nAlerting\n")
    assert result["status"] == "success", result
    [update] = fake.writes(f"data-values/{DV}/update")
    assert update["body"] == {
        "class": "UpdateElementRequestBody", "forLineage": False, "forDuplicateProcessing": False,
        "mergeUpdate": True,
        "properties": {"class": "LiteralDataValueProperties", "typeName": "LiteralDataValue",
                       "displayName": "Threshold B2-update", "qualifiedName": qn, "usage": "Alerting"}}


@pytest.mark.asyncio
async def test_a_literal_value_for_an_existing_plain_data_value_is_refused_in_words(monkeypatch):
    qn = "DataValue::Plain B2-refuse"
    fake = h.FakeEgeria(monkeypatch, names={qn: DV}, respond=_existing(qn, DV, "DataValue"))
    [result] = await h.run_doc(fake, "## Update Data Value\n### Display Name\nPlain B2-refuse\n### Literal Value\n7\n")
    assert result["status"] == "failure"
    assert "is a DataValue, not a LiteralDataValue" in result["message"] and "Literal Value" in result["message"]
    assert not fake.writes("/update")


@pytest.mark.asyncio
async def test_a_length_that_is_not_a_whole_number_is_refused(monkeypatch):
    fake = h.FakeEgeria(monkeypatch)
    [result] = await h.run_doc(fake, "## Create Data Value\n### Display Name\nBad B2-length\n### Length\nlong\n")
    assert result["status"] == "failure"
    assert "Length must be a whole number" in result["message"]
    assert not _creates(fake)


# --------------------------------------------------------------------------------------------- links

LINKS = {
    "Data Value Source": ("Data Value", DV, "Asset", ASSET, "DataValueSourceProperties",
                          f"data-engineer/data-values/{DV}/data-value-sources/{ASSET}", False),
    "Processing Variable": ("Element", PROCESS, "Data Value", DV, "ProcessingVariableProperties",
                            f"data-engineer/elements/{PROCESS}/processing-variables/{DV}", True),
    "Embedded Data Value": ("Parent Data Value", DV, "Embedded Data Value", DV2, "EmbeddedDataValueProperties",
                            f"data-engineer/data-values/{DV}/embedded-data-values/{DV2}", True),
}


@pytest.mark.asyncio
@pytest.mark.parametrize("noun", list(LINKS))
async def test_link_sends_the_relationship_properties(monkeypatch, noun):
    end1, g1, end2, g2, cls, path, positioned = LINKS[noun]
    fake = h.FakeEgeria(monkeypatch)
    doc = f"## Link {noun}\n### {end1}\n{g1}\n### {end2}\n{g2}\n### Label\nv1\n### Description\nThe link.\n"
    if positioned:
        doc += "### Position\n2\n"
    [result] = await h.run_doc(fake, doc)
    assert result["status"] == "success", result
    [call] = fake.calls
    assert call["path"] == f"{path}/attach"
    props = {"class": cls, "typeName": cls[:-len("Properties")], "label": "v1", "description": "The link."}
    if positioned:
        props["position"] = 2
    assert call["body"] == {**LINK_BASE, "properties": props}


@pytest.mark.asyncio
@pytest.mark.parametrize("noun", ["Processing Variable", "Embedded Data Value"])
async def test_position_left_out_is_not_sent(monkeypatch, noun):
    end1, g1, end2, g2, *_ = LINKS[noun]
    fake = h.FakeEgeria(monkeypatch)
    [result] = await h.run_doc(fake, f"## Link {noun}\n### {end1}\n{g1}\n### {end2}\n{g2}\n")
    assert result["status"] == "success", result
    assert fake.calls[0]["body"] == LINK_BASE


@pytest.mark.asyncio
async def test_a_position_that_is_not_a_whole_number_is_refused(monkeypatch):
    fake = h.FakeEgeria(monkeypatch)
    [result] = await h.run_doc(fake, f"## Link Processing Variable\n### Element\n{PROCESS}\n### Data Value\n{DV}\n"
                                     f"### Position\nfirst\n")
    assert result["status"] == "failure"
    assert "Position must be a whole number" in result["message"]
    assert fake.calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("verb", ["Detach", "Unlink"])
@pytest.mark.parametrize("noun", list(LINKS))
async def test_detach(monkeypatch, noun, verb):
    end1, g1, end2, g2, _, path, _ = LINKS[noun]
    fake = h.FakeEgeria(monkeypatch)
    [result] = await h.run_doc(fake, f"## {verb} {noun}\n### {end1}\n{g1}\n### {end2}\n{g2}\n")
    assert result["status"] == "success", result
    [call] = fake.calls
    assert call["path"] == f"{path}/detach"
    assert call["body"] == DELETE_BASE


# --------------------------------------------------------------------------------------------- version gate

B2_DOCS = {
    "Create Data Value": "## Create Data Value\n### Display Name\nGate value\n### Literal Value\n1\n",
    **{f"{verb} {noun}": f"## {verb} {noun}\n### {e1}\n{g1}\n### {e2}\n{g2}\n"
       for noun, (e1, g1, e2, g2, *_) in LINKS.items() for verb in ("Link", "Detach")},
}


@pytest.mark.asyncio
@pytest.mark.parametrize("directive", ["process", "validate"])
@pytest.mark.parametrize("command", list(B2_DOCS))
async def test_before_egeria_6_4_every_b2_command_says_needs_6_4(monkeypatch, command, directive):
    fake = h.FakeEgeria(monkeypatch, about=h.ABOUT_6_3)
    [result] = await h.run_doc(fake, B2_DOCS[command], directive=directive)
    assert result["status"] == "failure"
    assert result["message"].startswith(f"{command} needs Egeria 6.4")
    assert "runs Egeria 6.3" in result["message"] and "Nothing was sent" in result["message"]
    assert fake.calls == []


# --------------------------------------------------------------------------------------------- spec <-> processor

B2_COMMANDS = ["Create Data Value"] + [f"{v} {n}" for n in LINKS for v in ("Link", "Detach")]
_ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_attribute_consumption_audit_finds_nothing_on_the_b2_commands():
    spec = importlib.util.spec_from_file_location(
        "dr_egeria_attribute_consumption_audit", _ROOT / "scripts" / "dr_egeria_attribute_consumption_audit.py")
    audit = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = audit
    spec.loader.exec_module(audit)
    assert audit.audit("Data Engineer", None) == []


def test_every_b2_command_attribute_is_read_by_name_in_its_processor():
    family = json.loads((_ROOT / "md_processing/data/compact_commands/commands_data_engineer_compact.json")
                        .read_text())
    assert sorted(family["commands"]) == sorted(B2_COMMANDS)
    source = (_ROOT / "md_processing/v2/data_values.py").read_text()
    for command in B2_COMMANDS:
        for attribute in family["commands"][command]["custom_attributes"]:
            assert f'"{attribute}"' in source, (command, attribute)
