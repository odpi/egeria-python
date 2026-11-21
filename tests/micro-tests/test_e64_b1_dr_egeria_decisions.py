# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Egeria 6.4 Phase B1: the Dr.Egeria Governance Officer commands for Decisions (odpi/egeria#9463).

Each command's sample document goes through the real extractor, dispatcher and processor, into the real A6
GovernanceOfficer wrapper, whose HTTP call is captured (tests/micro-tests/e64_dre_harness.py). The test checks the
exact body the wrapper sends, so the wrapper's own checks (properties class, unread keys) passed too.

Also: how Update/Detach Assessment pick one assessment (the Architect's §2 ruling), and the version gate
("needs Egeria 6.4", a WARNING row, nothing sent) for the family.

No live server.
"""
import importlib.util
import pathlib
import sys

import pytest

from pyegeria.core._exceptions import PyegeriaClientException
from pyegeria.core import egeria_6_4_gate as gate

_spec = importlib.util.spec_from_file_location("e64_dre_harness",
                                               pathlib.Path(__file__).with_name("e64_dre_harness.py"))
h = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h)

DECISION = "d0000000-0000-4000-8000-000000000001"
ELEMENT = "e0000000-0000-4000-8000-000000000001"
OUTCOME = "f0000000-0000-4000-8000-000000000001"
REL_1 = "a0000000-0000-4000-8000-000000000001"
REL_2 = "a0000000-0000-4000-8000-000000000002"
REL_3 = "a0000000-0000-4000-8000-000000000003"

# makeAnchor false is the Link Command Base's Make Anchor default, and Egeria's own (A1 read-back).
LINK_BASE = {"class": "NewRelationshipRequestBody", "forLineage": False, "forDuplicateProcessing": False,
             "makeAnchor": False}
DELETE_BASE = {"class": "DeleteRelationshipRequestBody", "forLineage": False, "forDuplicateProcessing": False}


def _assessment(rel_guid, element, label, time):
    return {"relationshipHeader": {"guid": rel_guid, "type": {"typeName": "Assessment"}},
            "relationshipProperties": {"class": "AssessmentProperties", "label": label, "assessmentTime": time},
            "relatedElement": {"elementHeader": {"guid": element}, "properties": {"qualifiedName": "X"}}}


INPUTS = [
    _assessment(REL_1, ELEMENT, "fit", "2026-11-01T10:00:00.000+00:00"),
    _assessment(REL_2, ELEMENT, "fit", "2026-11-15T10:00:00.000+00:00"),
    _assessment(REL_3, ELEMENT, "risk", 1763200800000),   # 2025-11-15T10:00:00Z as epoch milliseconds
]


def _decision_with(inputs):
    def respond(method, path, body):
        if path.endswith(f"decisions/{DECISION}/retrieve"):
            element = {"elementHeader": {"guid": DECISION}, "properties": {"qualifiedName": "Decision::d"}}
            if inputs is not None:
                element["inputsToDecision"] = inputs
            return {"class": "DecisionResponse", "relatedHTTPCode": 200, "element": element}
        if path.endswith("/attach") and "assessments" in path:
            return {"class": "GUIDResponse", "relatedHTTPCode": 200, "guid": REL_1}
        return None
    return respond


# --------------------------------------------------------------------------------------------- Decision

@pytest.mark.asyncio
async def test_create_decision_sends_exact_decision_properties(monkeypatch):
    fake = h.FakeEgeria(monkeypatch)
    [result] = await h.run_doc(fake, """
## Create Decision
### Display Name
Adopt Egeria 6.4 B1-create
### Description
Move the demo to 6.4.
### Summary
Upgrade.
### Scope
Demo platforms
### Usage
For the laz demo.
### Importance
High
### Disposition
Approved
### Implications
- Re-test the Portal
- Release pyegeria
### Notes
See the build plan.
### Start Time
2026-11-22T00:00:00Z
### Last Review Time
2026-11-21T00:00:00Z
### Next Review Time
2026-12-22T00:00:00Z
### Expiry Time
2027-11-22T00:00:00Z
### Content Status
DRAFT
### Authors
Dan
""")
    assert result["status"] == "success", result
    [create] = [c for c in fake.calls if c["path"] == "governance-officer/decisions"]
    assert create["body"] == {
        "class": "NewElementRequestBody", "forLineage": False, "forDuplicateProcessing": False,
        "isOwnAnchor": True, "parentAtEnd1": True,
        "properties": {
            "class": "DecisionProperties", "typeName": "Decision",
            "displayName": "Adopt Egeria 6.4 B1-create", "qualifiedName": "Decision::Adopt Egeria 6.4 B1-create",
            "description": "Move the demo to 6.4.", "authors": ["Dan"], "contentStatus": "DRAFT",
            "summary": "Upgrade.", "scope": "Demo platforms", "usage": "For the laz demo.", "importance": "High",
            "disposition": "Approved", "implications": ["Re-test the Portal", "Release pyegeria"],
            "notes": "See the build plan.", "startTime": "2026-11-22T00:00:00Z",
            "lastReviewTime": "2026-11-21T00:00:00Z", "nextReviewTime": "2026-12-22T00:00:00Z",
            "expiryTime": "2027-11-22T00:00:00Z"}}


@pytest.mark.asyncio
async def test_update_decision_sends_merge_update_to_the_existing_decision(monkeypatch):
    qn = "Decision::Adopt Egeria 6.4 B1-update"

    def respond(method, path, body):
        if path.endswith(f"decisions/{DECISION}/retrieve"):
            return {"class": "DecisionResponse", "relatedHTTPCode": 200,
                    "element": {"elementHeader": {"guid": DECISION}, "properties": {"qualifiedName": qn}}}
        return None

    fake = h.FakeEgeria(monkeypatch, names={qn: DECISION}, respond=respond)
    [result] = await h.run_doc(fake, """
## Update Decision
### Display Name
Adopt Egeria 6.4 B1-update
### Disposition
Deferred
### Next Review Time
2027-01-15T00:00:00Z
""")
    assert result["status"] == "success", result
    [update] = fake.writes(f"decisions/{DECISION}/update")
    assert update["body"] == {
        "class": "UpdateElementRequestBody", "forLineage": False, "forDuplicateProcessing": False,
        "mergeUpdate": True,
        "properties": {"class": "DecisionProperties", "typeName": "Decision",
                       "displayName": "Adopt Egeria 6.4 B1-update", "qualifiedName": qn,
                       "disposition": "Deferred", "nextReviewTime": "2027-01-15T00:00:00Z"}}
    assert "authors" not in update["body"]["properties"]      # an empty list on a merge update would clear them


# --------------------------------------------------------------------------------------------- Outcome

@pytest.mark.asyncio
async def test_link_decision_outcome_sends_outcome_properties(monkeypatch):
    fake = h.FakeEgeria(monkeypatch)
    [result] = await h.run_doc(fake, f"""
## Link Decision Outcome
### Decision
{DECISION}
### Outcome
{OUTCOME}
### Label
upgrade-ticket
### Description
The upgrade work item.
### Importance
High
### Disposition
Done
""")
    assert result["status"] == "success", result
    [call] = fake.calls
    assert call["path"] == f"governance-officer/decisions/{DECISION}/outcomes/{OUTCOME}/attach"
    assert call["body"] == {**LINK_BASE, "properties": {
        "class": "OutcomeProperties", "typeName": "Outcome", "label": "upgrade-ticket",
        "description": "The upgrade work item.", "importance": "High", "disposition": "Done"}}


@pytest.mark.asyncio
async def test_link_decision_outcome_with_no_properties_sends_none(monkeypatch):
    fake = h.FakeEgeria(monkeypatch)
    [result] = await h.run_doc(fake, f"## Link Decision Outcome\n### Decision\n{DECISION}\n### Outcome\n{OUTCOME}\n")
    assert result["status"] == "success", result
    assert fake.calls[0]["body"] == LINK_BASE


@pytest.mark.asyncio
@pytest.mark.parametrize("verb", ["Detach", "Unlink"])
async def test_detach_decision_outcome(monkeypatch, verb):
    fake = h.FakeEgeria(monkeypatch)
    [result] = await h.run_doc(fake, f"## {verb} Decision Outcome\n### Decision\n{DECISION}\n### Outcome\n{OUTCOME}\n")
    assert result["status"] == "success", result
    [call] = fake.calls
    assert call["path"] == f"governance-officer/decisions/{DECISION}/outcomes/{OUTCOME}/detach"
    assert call["body"] == DELETE_BASE


# --------------------------------------------------------------------------------------------- Assessment

ASSESSMENT_DOC = f"""
## Link Assessment
### Element
{ELEMENT}
### Decision
{DECISION}
### Label
fit
### Description
Fits the platform.
### Assessor
Erin Overview
### Assessor Type Name
Person
### Assessor Property Name
qualifiedName
### Assessment Time
2026-11-21T10:00:00Z
### Expiry Time
2027-11-21T10:00:00Z
### Notes
Checked on laz.
### Additional Properties
source: laz
"""

ASSESSMENT_PROPERTIES = {
    "class": "AssessmentProperties", "typeName": "Assessment", "label": "fit", "description": "Fits the platform.",
    "assessor": "Erin Overview", "assessorTypeName": "Person", "assessorPropertyName": "qualifiedName",
    "assessmentTime": "2026-11-21T10:00:00Z", "expiryTime": "2027-11-21T10:00:00Z", "notes": "Checked on laz.",
    "additionalProperties": {"source": "laz"}}


@pytest.mark.asyncio
async def test_link_assessment_sends_exact_body_and_writes_its_guid_into_the_document(monkeypatch):
    fake = h.FakeEgeria(monkeypatch, respond=_decision_with(INPUTS))
    [result] = await h.run_doc(fake, ASSESSMENT_DOC)
    assert result["status"] == "success", result
    [call] = fake.calls
    assert call["path"] == f"governance-officer/elements/{ELEMENT}/assessments/{DECISION}/attach"
    assert call["body"] == {**LINK_BASE, "properties": ASSESSMENT_PROPERTIES}
    assert f"### Assessment GUID\n{REL_1}\n" in result["output"]
    assert result["output"].lstrip().startswith("## Link Assessment")


@pytest.mark.asyncio
async def test_link_assessment_run_again_with_its_guid_updates_it_instead_of_adding_another(monkeypatch):
    fake = h.FakeEgeria(monkeypatch, respond=_decision_with(INPUTS))
    doc = ASSESSMENT_DOC.replace("### Label\n", f"### Assessment GUID\n{REL_2}\n### Label\n")
    [result] = await h.run_doc(fake, doc)
    assert result["status"] == "success", result
    [call] = fake.calls
    assert call["path"] == f"governance-officer/assessments/{REL_2}/update"
    assert call["body"] == {"class": "UpdateRelationshipRequestBody", "forLineage": False,
                            "forDuplicateProcessing": False, "mergeUpdate": True, "properties": ASSESSMENT_PROPERTIES}
    assert result["output"].count("### Assessment GUID") == 1


@pytest.mark.asyncio
async def test_update_assessment_by_guid(monkeypatch):
    fake = h.FakeEgeria(monkeypatch)
    [result] = await h.run_doc(fake, f"## Update Assessment\n### Assessment GUID\n{REL_2}\n### Notes\nRe-checked.\n")
    assert result["status"] == "success", result
    [call] = fake.calls
    assert call["path"] == f"governance-officer/assessments/{REL_2}/update"
    assert call["body"] == {"class": "UpdateRelationshipRequestBody", "forLineage": False,
                            "forDuplicateProcessing": False, "mergeUpdate": True,
                            "properties": {"class": "AssessmentProperties", "typeName": "Assessment",
                                           "notes": "Re-checked."}}


def _pick_doc(verb, label="fit", time=None):
    doc = f"## {verb} Assessment\n### Element\n{ELEMENT}\n### Decision\n{DECISION}\n### Label\n{label}\n"
    if time:
        doc += f"### Assessment Time\n{time}\n"
    return doc + ("### Notes\nRe-checked.\n" if verb == "Update" else "")


@pytest.mark.asyncio
@pytest.mark.parametrize("time", ["2026-11-15T10:00:00Z", "2026-11-15T11:00:00+01:00", "2026-11-15T10:00:00.000Z"])
async def test_detach_assessment_picks_the_one_at_that_instant(monkeypatch, time):
    fake = h.FakeEgeria(monkeypatch, respond=_decision_with(INPUTS))
    [result] = await h.run_doc(fake, _pick_doc("Detach", time=time))
    assert result["status"] == "success", result
    [detach] = fake.writes("/detach")
    assert detach["path"] == f"governance-officer/assessments/{REL_2}/detach"
    assert detach["body"] == DELETE_BASE


@pytest.mark.asyncio
async def test_update_assessment_picks_the_only_one_with_that_label(monkeypatch):
    fake = h.FakeEgeria(monkeypatch, respond=_decision_with(INPUTS))
    [result] = await h.run_doc(fake, _pick_doc("Update", label="risk"))
    assert result["status"] == "success", result
    [update] = fake.writes("/update")
    assert update["path"] == f"governance-officer/assessments/{REL_3}/update"


@pytest.mark.asyncio
async def test_epoch_millisecond_times_compare_as_instants(monkeypatch):
    fake = h.FakeEgeria(monkeypatch, respond=_decision_with(INPUTS))
    [result] = await h.run_doc(fake, _pick_doc("Detach", label="risk", time="2025-11-15T10:00:00Z"))
    assert result["status"] == "success", result
    assert fake.writes("/detach")[0]["path"] == f"governance-officer/assessments/{REL_3}/detach"


@pytest.mark.asyncio
@pytest.mark.parametrize("verb", ["Update", "Detach"])
async def test_several_matches_are_refused_listing_each_candidate(monkeypatch, verb):
    fake = h.FakeEgeria(monkeypatch, respond=_decision_with(INPUTS))
    [result] = await h.run_doc(fake, _pick_doc(verb))
    assert result["status"] == "failure"
    message = result["message"]
    assert "2 assessments match" in message and "none was picked" in message
    for rel, time in ((REL_1, "2026-11-01T10:00:00.000+00:00"), (REL_2, "2026-11-15T10:00:00.000+00:00")):
        assert rel in message and time in message
    assert "'fit'" in message and REL_3 not in message
    assert not fake.writes("/update") and not fake.writes("/detach")


@pytest.mark.asyncio
async def test_no_match_is_refused_listing_the_candidates(monkeypatch):
    fake = h.FakeEgeria(monkeypatch, respond=_decision_with(INPUTS))
    [result] = await h.run_doc(fake, _pick_doc("Detach", time="2026-11-02T10:00:00Z"))
    assert result["status"] == "failure"
    assert "no assessment matches" in result["message"]
    assert REL_1 in result["message"] and REL_2 in result["message"]   # same element and label, other times
    assert not fake.writes("/detach")


@pytest.mark.asyncio
async def test_no_assessed_inputs_is_said_in_words_not_none(monkeypatch):
    fake = h.FakeEgeria(monkeypatch, respond=_decision_with(None))
    [result] = await h.run_doc(fake, _pick_doc("Detach"))
    assert result["status"] == "failure"
    assert "lists no assessed inputs" in result["message"]
    assert not fake.writes("/detach")


@pytest.mark.asyncio
@pytest.mark.parametrize("verb", ["Update", "Detach", "Link"])
async def test_a_time_with_no_zone_is_refused_with_words(monkeypatch, verb):
    fake = h.FakeEgeria(monkeypatch, respond=_decision_with(INPUTS))
    doc = (_pick_doc(verb, time="2026-11-15T10:00:00") if verb != "Link"
           else ASSESSMENT_DOC.replace("2026-11-21T10:00:00Z\n### Expiry", "2026-11-21T10:00:00\n### Expiry"))
    [result] = await h.run_doc(fake, doc)
    assert result["status"] == "failure"
    assert "has no time zone" in result["message"]
    assert not [c for c in fake.calls if not c["path"].endswith("/retrieve")]


@pytest.mark.asyncio
async def test_update_assessment_without_guid_or_finders_says_what_is_missing(monkeypatch):
    fake = h.FakeEgeria(monkeypatch)
    [result] = await h.run_doc(fake, f"## Update Assessment\n### Element\n{ELEMENT}\n### Notes\nx\n")
    assert result["status"] == "failure"
    assert "needs the Assessment GUID" in result["message"] and "Decision, Label are missing" in result["message"]
    assert fake.calls == []


# --------------------------------------------------------------------------------------------- version gate

B1_DOCS = {
    "Create Decision": "## Create Decision\n### Display Name\nGate decision\n",
    "Link Decision Outcome": f"## Link Decision Outcome\n### Decision\n{DECISION}\n### Outcome\n{OUTCOME}\n",
    "Detach Decision Outcome": f"## Detach Decision Outcome\n### Decision\n{DECISION}\n### Outcome\n{OUTCOME}\n",
    "Link Assessment": f"## Link Assessment\n### Element\n{ELEMENT}\n### Decision\n{DECISION}\n### Label\nfit\n",
    "Update Assessment": f"## Update Assessment\n### Assessment GUID\n{REL_1}\n### Notes\nx\n",
    "Detach Assessment": f"## Detach Assessment\n### Assessment GUID\n{REL_1}\n",
}


@pytest.mark.asyncio
@pytest.mark.parametrize("directive", ["process", "validate"])
@pytest.mark.parametrize("command", list(B1_DOCS))
async def test_before_egeria_6_4_every_b1_command_says_needs_6_4(monkeypatch, command, directive):
    fake = h.FakeEgeria(monkeypatch, about=h.ABOUT_6_3)
    [result] = await h.run_doc(fake, B1_DOCS[command], directive=directive)
    assert result["status"] == "warning"                  # not an error, and not "none"
    assert result["message"].startswith(f"{command} needs Egeria 6.4")
    assert "runs Egeria 6.3" in result["message"] and "Nothing was sent" in result["message"]
    assert "Needs Egeria 6.4" in result["output"]
    assert fake.calls == []


@pytest.mark.asyncio
async def test_a_6_4_snapshot_built_before_the_merge_also_needs_6_4(monkeypatch):
    early = '{"version": "6.4-SNAPSHOT", "time": "2026-11-20T23:00:00Z"}'
    fake = h.FakeEgeria(monkeypatch, about=early)
    [result] = await h.run_doc(fake, B1_DOCS["Detach Assessment"])
    assert result["status"] == "warning" and "needs Egeria 6.4" in result["message"]
    assert fake.calls == []


@pytest.mark.asyncio
async def test_on_egeria_6_4_the_command_runs(monkeypatch):
    fake = h.FakeEgeria(monkeypatch, about=h.ABOUT_6_4)
    [result] = await h.run_doc(fake, B1_DOCS["Detach Assessment"])
    assert result["status"] == "success", result
    assert fake.calls[0]["path"] == f"governance-officer/assessments/{REL_1}/detach"


@pytest.mark.asyncio
async def test_unknown_version_and_a_bare_404_reads_as_needs_6_4(monkeypatch):
    def respond(method, path, body):
        return PyegeriaClientException(h._Response({}, status_code=404), {"caller_method": "x"}, {})

    fake = h.FakeEgeria(monkeypatch, about="not json", respond=respond)
    [result] = await h.run_doc(fake, B1_DOCS["Link Decision Outcome"])
    assert result["status"] == "warning"
    assert "needs Egeria 6.4" in result["message"] and "does not serve this request" in result["message"]


@pytest.mark.parametrize("about, expected", [
    ('{"version": "6.3"}', False),
    ('{"version": "6.3-SNAPSHOT", "time": "2026-11-21T22:00:00Z"}', False),
    ('{"version": "6.4"}', True),
    ('{"version": "6.4.1"}', True),
    ('{"version": "6.4-SNAPSHOT", "time": "2026-11-21T19:51:36Z"}', True),
    ('{"version": "6.4-SNAPSHOT", "time": "2026-11-21T19:51:35Z"}', False),
    ('{"version": "6.4-SNAPSHOT"}', None),               # no build time: unknown, never "no"
    ('{"version": "6.5-SNAPSHOT", "time": "2026-12-01T00:00:00Z"}', True),
    ('{"version": "banana"}', None),
    ("not json", None),
])
def test_carries_6_4(about, expected):
    assert gate.carries_6_4(about)[0] is expected


# --------------------------------------------------------------------------------------------- spec <-> processor

B1_COMMANDS = ["Create Decision", "Link Decision Outcome", "Detach Decision Outcome", "Link Assessment",
               "Update Assessment", "Detach Assessment"]
_ROOT = pathlib.Path(__file__).resolve().parents[2]


def _load_audit():
    spec = importlib.util.spec_from_file_location(
        "dr_egeria_attribute_consumption_audit", _ROOT / "scripts" / "dr_egeria_attribute_consumption_audit.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module          # its dataclasses look their module up by name
    spec.loader.exec_module(module)
    return module


def test_attribute_consumption_audit_finds_nothing_on_the_b1_commands():
    audit = _load_audit()
    findings = [f for c in ("Decision", "Assessment") for f in audit.audit(None, c)]
    assert findings == []


def test_every_b1_command_attribute_is_read_by_name_in_its_processor():
    """Stricter than the audit (which looks for the name anywhere): each command's own attributes are read
    in md_processing/v2/decisions.py, and its bundle's by the shared body builders the processors call."""
    import json
    family = json.loads((_ROOT / "md_processing/data/compact_commands/commands_governance_officer_compact.json")
                        .read_text())
    source = (_ROOT / "md_processing/v2/decisions.py").read_text()
    for command in B1_COMMANDS:
        for attribute in family["commands"][command]["custom_attributes"]:
            assert f'"{attribute}"' in source, (command, attribute)
