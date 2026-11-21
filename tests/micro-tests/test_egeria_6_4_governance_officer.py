# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Egeria 6.4 (odpi/egeria#9463) Governance Officer requests: decisions, their outcomes and assessments.

The 12 requests are checked against the `.http` samples in tests/fixtures/egeria-6.4/, with every URL path
taken from pyegeria.core.egeria_6_4_names. For each method: the HTTP verb, the URL, and that the body sent
equals the sample once its placeholders are filled. Also: attach with no body sends no body; update without a
body is refused locally; mergeUpdate passes through; link_assessment returns the relationship GUID; a
properties object of the wrong class is refused locally, naming the class expected. Writes are compared to the
sample by exact equality (A6: one body rule, pyegeria.core.egeria_6_4_bodies); reads to the sample plus
Egeria's own defaults.

No live server: the HTTP call is captured.
"""
import json
import re
from pathlib import Path

import pytest

from pyegeria.core import egeria_6_4_names as n
from pyegeria.core._exceptions import PyegeriaInvalidParameterException
from pyegeria.core._globals import NO_GUID_RETURNED
from pyegeria.omvs.governance_officer import GovernanceOfficer

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "egeria-6.4" / "Egeria-api-governance-officer.http"
PLATFORM = "https://localhost:1"
SERVER = "view-server"
ROOT = f"{PLATFORM}/servers/{SERVER}/api/open-metadata/"
TIMESTAMP = "2026-11-21T12:00:00Z"
REL_GUID = "assessment-rel-guid-0001"

DECISION_GUID = "decision-guid-1"
OUTCOME_GUID = "outcome-guid-1"
ELEMENT_GUID = "element-guid-1"


def _samples() -> dict:
    """`# @name` -> (verb, path relative to /api/open-metadata/, body or None) for every request in the file."""
    out = {}
    for block in FIXTURE.read_text().split("\n###"):
        m = re.search(r"^# @name (\S+)", block, re.M)
        req = re.search(r"^(POST|GET) \{\{baseURL\}\}/servers/\{\{viewServer\}\}/api/open-metadata/(\S+)", block, re.M)
        if not (m and req):
            continue
        start = re.compile(r"^\{", re.M).search(block, req.end())  # the body opens on a line of its own
        body = None
        if start:
            body_text = block[start.start():].replace("{{$isoTimestamp}}", TIMESTAMP)
            body = json.JSONDecoder().raw_decode(body_text)[0]
        out[m.group(1)] = (req.group(1), req.group(2).replace("{{", "{").replace("}}", "}"), body)
    return out


SAMPLES = _samples()


def _sample_body(name: str) -> dict:
    return json.loads(json.dumps(SAMPLES[name][2]))  # a fresh copy each time


class _Response:
    def __init__(self, payload: dict):
        self._payload = payload

    def json(self):
        return self._payload


def _client(monkeypatch, calls: list, response: dict | None = None) -> GovernanceOfficer:
    monkeypatch.setattr(GovernanceOfficer, "check_connection", lambda self: "test")
    client = GovernanceOfficer(SERVER, PLATFORM, "user", "pwd")
    payload = response or {"class": "VoidResponse", "relatedHTTPCode": 200}

    async def fake_make_request(method, url, payload_=None, *args, **kwargs):
        body = json.loads(payload_) if isinstance(payload_, str) else payload_
        calls.append({"method": method, "url": url, "body": body})
        return _Response(payload)

    client._async_make_request = fake_make_request
    return client


def _url(path: str, **guids) -> str:
    return ROOT + path.format(**guids)


# --- the fixture and the names module agree on the 12 requests -----------------------------------------------

CASES = {
    # sample name: (names-module path, guids for the path)
    "createDecision": (n.DECISIONS_CREATE, {}),
    "createDecisionFromTemplate": (n.DECISIONS_FROM_TEMPLATE, {}),
    "updateDecision": (n.DECISIONS_UPDATE, {"decisionGUID": DECISION_GUID}),
    "deleteDecision": (n.DECISIONS_DELETE, {"decisionGUID": DECISION_GUID}),
    "getDecisionsByName": (n.DECISIONS_BY_NAME, {}),
    "getDecisionByGUID": (n.DECISIONS_RETRIEVE, {"decisionGUID": DECISION_GUID}),
    "findDecisions": (n.DECISIONS_BY_SEARCH_STRING, {}),
    "linkDecisionOutcome": (n.OUTCOMES_ATTACH, {"decisionGUID": DECISION_GUID, "outcomeGUID": OUTCOME_GUID}),
    "detachDecisionOutcome": (n.OUTCOMES_DETACH, {"decisionGUID": DECISION_GUID, "outcomeGUID": OUTCOME_GUID}),
    "linkAssessment": (n.ASSESSMENTS_ATTACH, {"elementGUID": ELEMENT_GUID, "decisionGUID": DECISION_GUID}),
    "updateAssessment": (n.ASSESSMENTS_UPDATE, {"assessmentGUID": REL_GUID}),
    "detachAssessment": (n.ASSESSMENTS_DETACH, {"assessmentGUID": REL_GUID}),
}


def test_the_twelve_samples_match_the_names_module():
    assert len(CASES) == 12
    for name, (path, _guids) in CASES.items():
        verb, sample_path, _body = SAMPLES[name]
        assert verb == "POST", name
        assert sample_path == path, name


# --- each method: verb, URL and the body sent equal to the sample ---------------------------------------------

async def _call(client: GovernanceOfficer, name: str, body):
    if name == "createDecision":
        return await client._async_create_decision(body)
    if name == "createDecisionFromTemplate":
        return await client._async_create_decision_from_template(body)
    if name == "updateDecision":
        return await client._async_update_decision(DECISION_GUID, body)
    if name == "deleteDecision":
        return await client._async_delete_decision(DECISION_GUID, body)
    if name == "getDecisionsByName":
        return await client._async_get_decisions_by_name(body=body)
    if name == "getDecisionByGUID":
        return await client._async_get_decision_by_guid(DECISION_GUID, body=body)
    if name == "findDecisions":
        return await client._async_find_decisions(body=body)
    if name == "linkDecisionOutcome":
        return await client._async_link_decision_outcome(DECISION_GUID, OUTCOME_GUID, body)
    if name == "detachDecisionOutcome":
        return await client._async_detach_decision_outcome(DECISION_GUID, OUTCOME_GUID, body)
    if name == "linkAssessment":
        return await client._async_link_assessment(ELEMENT_GUID, DECISION_GUID, body)
    if name == "updateAssessment":
        return await client._async_update_assessment(REL_GUID, body)
    if name == "detachAssessment":
        return await client._async_detach_assessment(REL_GUID, body)
    raise AssertionError(name)


@pytest.mark.asyncio
@pytest.mark.parametrize("name", list(CASES))
async def test_each_request_sends_the_sample_body_to_the_right_url(monkeypatch, name):
    calls: list = []
    client = _client(monkeypatch, calls, {"class": "GUIDResponse", "guid": "new-guid", "elements": [{"x": 1}],
                                          "element": {"x": 1}})
    path, guids = CASES[name]

    await _call(client, name, _sample_body(name))

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert calls[0]["url"] == _url(path, **guids)
    if name in READS:
        # Reads use the shared request helpers; their only additions are Egeria's own defaults for those
        # fields, listed here so any other addition fails.
        assert calls[0]["body"] == {**SAMPLES[name][2], **READ_DEFAULTS[name]}
    else:
        # Writes send the caller's body exactly (pyegeria.core.egeria_6_4_bodies): no model re-dump, no
        # added defaults.
        assert calls[0]["body"] == SAMPLES[name][2]


_GET_DEFAULTS = {"relationshipsPageSize": 0}
_LIST_DEFAULTS = {"forLineage": False, "forDuplicateProcessing": False, "relationshipsPageSize": 0}
READ_DEFAULTS = {
    "getDecisionsByName": _LIST_DEFAULTS,                                                # FilterRequestBody
    "getDecisionByGUID": _GET_DEFAULTS,                                                  # GetRequestBody
    "findDecisions": _LIST_DEFAULTS,                                                     # SearchStringRequestBody
}
READS = set(READ_DEFAULTS)


@pytest.mark.parametrize("name", list(CASES))
def test_each_request_has_a_sync_wrapper_whose_docstring_names_egeria_6_4(name):
    method = {
        "createDecision": "create_decision", "createDecisionFromTemplate": "create_decision_from_template",
        "updateDecision": "update_decision", "deleteDecision": "delete_decision",
        "getDecisionsByName": "get_decisions_by_name", "getDecisionByGUID": "get_decision_by_guid",
        "findDecisions": "find_decisions", "linkDecisionOutcome": "link_decision_outcome",
        "detachDecisionOutcome": "detach_decision_outcome", "linkAssessment": "link_assessment",
        "updateAssessment": "update_assessment", "detachAssessment": "detach_assessment",
    }[name]
    for attr in (method, f"_async_{method}"):
        fn = getattr(GovernanceOfficer, attr)
        assert fn.__doc__ and "Egeria 6.4" in fn.__doc__, attr


def test_sync_wrapper_reaches_the_same_request(monkeypatch):
    calls: list = []
    client = _client(monkeypatch, calls, {"class": "GUIDResponse", "guid": REL_GUID})
    assert client.link_assessment(ELEMENT_GUID, DECISION_GUID) == REL_GUID
    assert calls[0]["url"] == _url(n.ASSESSMENTS_ATTACH, elementGUID=ELEMENT_GUID, decisionGUID=DECISION_GUID)


# --- attach / detach with no body send no body -----------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["linkDecisionOutcome", "detachDecisionOutcome", "linkAssessment",
                                  "detachAssessment"])
async def test_attach_and_detach_with_no_body_send_no_body(monkeypatch, name):
    calls: list = []
    client = _client(monkeypatch, calls, {"class": "GUIDResponse", "guid": REL_GUID})
    path, guids = CASES[name]

    await _call(client, name, None)

    assert calls == [{"method": "POST", "url": _url(path, **guids), "body": None}]


# --- link_assessment returns the relationship GUID -------------------------------------------------------------

@pytest.mark.asyncio
async def test_link_assessment_returns_the_relationship_guid(monkeypatch):
    calls: list = []
    client = _client(monkeypatch, calls, {"class": "GUIDResponse", "guid": REL_GUID})
    assert await client._async_link_assessment(ELEMENT_GUID, DECISION_GUID, _sample_body("linkAssessment")) == REL_GUID


@pytest.mark.asyncio
async def test_link_assessment_without_a_guid_in_the_answer_says_so(monkeypatch):
    calls: list = []
    client = _client(monkeypatch, calls, {"class": "VoidResponse"})
    assert await client._async_link_assessment(ELEMENT_GUID, DECISION_GUID) == NO_GUID_RETURNED


# --- updates need a body; mergeUpdate passes through ------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["updateDecision", "updateAssessment"])
async def test_update_without_a_body_is_refused_locally(monkeypatch, name):
    calls: list = []
    client = _client(monkeypatch, calls)
    with pytest.raises(PyegeriaInvalidParameterException) as exc:
        await _call(client, name, None)
    assert "needs a request body" in str(exc.value)
    assert calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("name", ["updateDecision", "updateAssessment"])
@pytest.mark.parametrize("merge", [True, False])
async def test_merge_update_passes_through(monkeypatch, name, merge):
    calls: list = []
    client = _client(monkeypatch, calls)
    body = _sample_body(name)
    body["mergeUpdate"] = merge

    await _call(client, name, body)

    assert calls[0]["body"]["mergeUpdate"] is merge


# --- a properties object of the wrong class is refused locally ---------------------------------------------------

WRONG_CLASS = {
    "createDecision": "DecisionProperties",
    "updateDecision": "DecisionProperties",
    "linkDecisionOutcome": "OutcomeProperties",
    "linkAssessment": "AssessmentProperties",
    "updateAssessment": "AssessmentProperties",
}


@pytest.mark.asyncio
@pytest.mark.parametrize("name", list(WRONG_CLASS))
async def test_a_wrong_properties_class_is_refused_naming_the_class_expected(monkeypatch, name):
    calls: list = []
    client = _client(monkeypatch, calls)
    body = _sample_body(name)
    body["properties"]["class"] = "GovernanceDefinitionProperties"

    with pytest.raises(PyegeriaInvalidParameterException) as exc:
        await _call(client, name, body)

    assert WRONG_CLASS[name] in str(exc.value)
    assert "GovernanceDefinitionProperties" in str(exc.value)
    assert calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("name", list(WRONG_CLASS))
async def test_a_properties_object_with_no_class_is_refused(monkeypatch, name):
    calls: list = []
    client = _client(monkeypatch, calls)
    body = _sample_body(name)
    del body["properties"]["class"]

    with pytest.raises(PyegeriaInvalidParameterException) as exc:
        await _call(client, name, body)

    assert WRONG_CLASS[name] in str(exc.value)
    assert calls == []


@pytest.mark.asyncio
async def test_a_wrong_class_in_a_model_body_is_refused_too(monkeypatch):
    from pyegeria.models import NewRelationshipRequestBody
    calls: list = []
    client = _client(monkeypatch, calls)
    body = NewRelationshipRequestBody.model_validate(
        {"class": "NewRelationshipRequestBody", "properties": {"class": "LicenseProperties"}})

    with pytest.raises(PyegeriaInvalidParameterException) as exc:
        await client._async_link_assessment(ELEMENT_GUID, DECISION_GUID, body)

    assert "AssessmentProperties" in str(exc.value)
    assert calls == []


@pytest.mark.asyncio
async def test_attach_with_a_body_but_no_properties_is_sent(monkeypatch):
    calls: list = []
    client = _client(monkeypatch, calls)
    body = {"class": "NewRelationshipRequestBody", "forLineage": False, "forDuplicateProcessing": False}

    await client._async_link_decision_outcome(DECISION_GUID, OUTCOME_GUID, body)

    assert calls[0]["body"] == body
