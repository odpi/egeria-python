# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Egeria 6.4 Phase B3: Link/Detach Project Target (Projects), Link/Detach Supported Variable Type (Schema Maker) and
Set/Clear Branch (Devops Pipeline), odpi/egeria#9463.

Each command's sample document goes through the real extractor, dispatcher and processor, into the real A6 wrapper
(ProjectManager, SchemaMaker, DevopsPipeline), whose HTTP call is captured (tests/micro-tests/e64_dre_harness.py).
The test checks the exact body the wrapper sends. Also: whole numbers for Position and the cardinalities, values
sent only when given, and the version gate ("needs Egeria 6.4", a WARNING row, nothing sent) for each family.

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

PROJECT = "90000000-0000-4000-8000-000000000001"
TARGET = "91000000-0000-4000-8000-000000000001"
PROCESS = "92000000-0000-4000-8000-000000000001"
SCHEMA_TYPE = "93000000-0000-4000-8000-000000000001"
LIBRARY = "94000000-0000-4000-8000-000000000001"

LINK_BASE = {"class": "NewRelationshipRequestBody", "forLineage": False, "forDuplicateProcessing": False,
             "makeAnchor": False}
DELETE_BASE = {"class": "DeleteRelationshipRequestBody", "forLineage": False, "forDuplicateProcessing": False}


# --------------------------------------------------------------------------------------------- Project Target

@pytest.mark.asyncio
async def test_link_project_target(monkeypatch):
    fake = h.FakeEgeria(monkeypatch)
    [result] = await h.run_doc(fake, f"## Link Project Target\n### Project\n{PROJECT}\n### Target Element\n{TARGET}\n"
                                     f"### Label\nscope\n### Description\nThe repository the project upgrades.\n")
    assert result["status"] == "success", result
    [call] = fake.calls
    assert call["path"] == f"project-manager/projects/{PROJECT}/project-targets/{TARGET}/attach"
    assert call["body"] == {**LINK_BASE, "properties": {
        "class": "ProjectTargetProperties", "typeName": "ProjectTarget", "label": "scope",
        "description": "The repository the project upgrades."}}


@pytest.mark.asyncio
async def test_link_project_target_with_no_properties_sends_none(monkeypatch):
    fake = h.FakeEgeria(monkeypatch)
    [result] = await h.run_doc(fake, f"## Link Project Target\n### Project\n{PROJECT}\n### Target Element\n{TARGET}\n")
    assert result["status"] == "success", result
    assert fake.calls[0]["body"] == LINK_BASE


@pytest.mark.asyncio
@pytest.mark.parametrize("verb", ["Detach", "Unlink"])
async def test_detach_project_target(monkeypatch, verb):
    fake = h.FakeEgeria(monkeypatch)
    [result] = await h.run_doc(fake, f"## {verb} Project Target\n### Project\n{PROJECT}\n### Target Element\n{TARGET}\n")
    assert result["status"] == "success", result
    [call] = fake.calls
    assert call["path"] == f"project-manager/projects/{PROJECT}/project-targets/{TARGET}/detach"
    assert call["body"] == DELETE_BASE


# --------------------------------------------------------------------------------------------- Supported Variable Type

@pytest.mark.asyncio
async def test_link_supported_variable_type_sends_position_and_cardinalities(monkeypatch):
    fake = h.FakeEgeria(monkeypatch)
    [result] = await h.run_doc(fake, f"""
## Link Supported Variable Type
### Element
{PROCESS}
### Schema Type
{SCHEMA_TYPE}
### Label
retries
### Position
1
### Min Cardinality
0
### Max Cardinality
3
""")
    assert result["status"] == "success", result
    [call] = fake.calls
    assert call["path"] == f"schema-maker/elements/{PROCESS}/supported-variable-types/{SCHEMA_TYPE}/attach"
    assert call["body"] == {**LINK_BASE, "properties": {
        "class": "SupportedVariableTypeProperties", "typeName": "SupportedVariableType", "label": "retries",
        "position": 1, "minCardinality": 0, "maxCardinality": 3}}


@pytest.mark.asyncio
async def test_supported_variable_type_values_left_out_are_not_sent(monkeypatch):
    fake = h.FakeEgeria(monkeypatch)
    [result] = await h.run_doc(fake, f"## Link Supported Variable Type\n### Element\n{PROCESS}\n### Schema Type\n"
                                     f"{SCHEMA_TYPE}\n")
    assert result["status"] == "success", result
    assert fake.calls[0]["body"] == LINK_BASE


@pytest.mark.asyncio
async def test_a_cardinality_that_is_not_a_whole_number_is_refused(monkeypatch):
    fake = h.FakeEgeria(monkeypatch)
    [result] = await h.run_doc(fake, f"## Link Supported Variable Type\n### Element\n{PROCESS}\n### Schema Type\n"
                                     f"{SCHEMA_TYPE}\n### Max Cardinality\nmany\n")
    assert result["status"] == "failure"
    assert "Max Cardinality must be a whole number" in result["message"]
    assert fake.calls == []


@pytest.mark.asyncio
async def test_detach_supported_variable_type(monkeypatch):
    fake = h.FakeEgeria(monkeypatch)
    [result] = await h.run_doc(fake, f"## Detach Supported Variable Type\n### Element\n{PROCESS}\n### Schema Type\n"
                                     f"{SCHEMA_TYPE}\n")
    assert result["status"] == "success", result
    [call] = fake.calls
    assert call["path"] == f"schema-maker/elements/{PROCESS}/supported-variable-types/{SCHEMA_TYPE}/detach"
    assert call["body"] == DELETE_BASE


# --------------------------------------------------------------------------------------------- Branch

@pytest.mark.asyncio
async def test_set_branch_sends_branch_properties(monkeypatch):
    fake = h.FakeEgeria(monkeypatch)
    [result] = await h.run_doc(fake, f"""
## Set Branch
### Target Element
{LIBRARY}
### Display Name
main
### Scope
repository
### Purpose
default branch
### URL
https://github.com/odpi/egeria/tree/main
""")
    assert result["status"] == "success", result
    [call] = fake.calls
    assert call["path"] == f"devops-pipeline/elements/{LIBRARY}/branch"
    assert call["body"] == {"class": "NewClassificationRequestBody", "forLineage": False,
                            "forDuplicateProcessing": False,
                            "properties": {"class": "BranchProperties", "displayName": "main",
                                           "scope": "repository", "purpose": "default branch",
                                           "url": "https://github.com/odpi/egeria/tree/main"}}


@pytest.mark.asyncio
async def test_clear_branch_sends_a_metadata_source_body(monkeypatch):
    fake = h.FakeEgeria(monkeypatch)
    [result] = await h.run_doc(fake, f"## Clear Branch\n### Target Element\n{LIBRARY}\n")
    assert result["status"] == "success", result
    [call] = fake.calls
    assert call["path"] == f"devops-pipeline/elements/{LIBRARY}/branch/remove"
    assert call["body"] == {"class": "MetadataSourceRequestBody", "forLineage": False,
                            "forDuplicateProcessing": False}


# --------------------------------------------------------------------------------------------- version gate

B3_DOCS = {
    "Link Project Target": f"## Link Project Target\n### Project\n{PROJECT}\n### Target Element\n{TARGET}\n",
    "Detach Project Target": f"## Detach Project Target\n### Project\n{PROJECT}\n### Target Element\n{TARGET}\n",
    "Link Supported Variable Type": f"## Link Supported Variable Type\n### Element\n{PROCESS}\n### Schema Type\n{SCHEMA_TYPE}\n",
    "Detach Supported Variable Type": f"## Detach Supported Variable Type\n### Element\n{PROCESS}\n### Schema Type\n{SCHEMA_TYPE}\n",
    "Set Branch": f"## Set Branch\n### Target Element\n{LIBRARY}\n### Display Name\nmain\n",
    "Clear Branch": f"## Clear Branch\n### Target Element\n{LIBRARY}\n",
}


@pytest.mark.asyncio
@pytest.mark.parametrize("directive", ["process", "validate"])
@pytest.mark.parametrize("command", list(B3_DOCS))
async def test_before_egeria_6_4_every_b3_command_says_needs_6_4(monkeypatch, command, directive):
    fake = h.FakeEgeria(monkeypatch, about=h.ABOUT_6_3)
    [result] = await h.run_doc(fake, B3_DOCS[command], directive=directive)
    assert result["status"] == "warning"
    assert result["message"].startswith(f"{command} needs Egeria 6.4")
    assert "runs Egeria 6.3" in result["message"] and "Nothing was sent" in result["message"]
    assert fake.calls == []


# --------------------------------------------------------------------------------------------- spec <-> processor

_ROOT = pathlib.Path(__file__).resolve().parents[2]
B3_FILES = {
    "commands_project_compact.json": ["Link Project Target", "Detach Project Target"],
    "commands_schema_maker_compact.json": ["Link Supported Variable Type", "Detach Supported Variable Type"],
    "commands_devops_pipeline_compact.json": ["Set Branch", "Clear Branch"],
}


def test_attribute_consumption_audit_finds_nothing_on_the_b3_commands():
    spec = importlib.util.spec_from_file_location(
        "dr_egeria_attribute_consumption_audit", _ROOT / "scripts" / "dr_egeria_attribute_consumption_audit.py")
    audit = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = audit
    spec.loader.exec_module(audit)
    findings = [f for c in ("Project Target", "Supported Variable Type", "Branch") for f in audit.audit(None, c)]
    assert findings == []


def test_every_b3_command_attribute_is_read_by_name_in_its_processor():
    source = (_ROOT / "md_processing/v2/egeria_6_4_other.py").read_text()
    for fname, commands in B3_FILES.items():
        family = json.loads((_ROOT / "md_processing/data/compact_commands" / fname).read_text())
        for command in commands:
            for attribute in family["commands"][command]["custom_attributes"]:
                assert f'"{attribute}"' in source, (command, attribute)
