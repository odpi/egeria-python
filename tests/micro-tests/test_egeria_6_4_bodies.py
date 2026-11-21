# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
The one Egeria 6.4 body checker, pyegeria.core.egeria_6_4_bodies (A6 consolidation).

One test group per rule of the Architect's ruling:
1. writes send the caller's body exactly as given (no model re-dump), no body on a bodiless attach/detach, a
   required body refused with words;
2. reads keep the shared helpers (their added defaults are checked per wrapper in the A1/A2 tests); here, that
   the checker is not on the read path;
3. the class check takes a set of accepted Properties classes and names them all when it refuses;
4. unread keys are refused, naming the class and the keys it reads; a class missing from the table only warns;
5. it is the ONE checker: the five 6.4 modules import it, define no helper of their own, and only it imports
   the md_processing table.

No live server.
"""
import ast
import inspect
import json
from pathlib import Path

import pytest
from loguru import logger

from pyegeria.core import egeria_6_4_bodies as bodies
from pyegeria.core import egeria_6_4_names as n
from pyegeria.core._exceptions import PyegeriaInvalidParameterException
from pyegeria.models import NewRelationshipRequestBody

REPO = Path(__file__).resolve().parents[2]
SIX_FOUR_MODULES = ("governance_officer", "data_engineer", "project_manager", "schema_maker", "devops_pipeline")


def _refusal(fn, *args, **kwargs) -> str:
    with pytest.raises(PyegeriaInvalidParameterException) as raised:
        fn(*args, **kwargs)
    return str(raised.value)


# --- rule 1: writes send exactly what was given ----------------------------------------------------------------

def test_a_dict_body_is_sent_exactly_even_keys_the_model_lacks_and_timestamp_formats():
    body = {"class": "NewRelationshipRequestBody",
            "aKeyNoPyegeriaModelHas": ["kept"],          # the model is extra='ignore': a dump would drop it
            "effectiveTime": "2026-11-21T12:00:00.000+00:00",  # a dump would reformat it
            "properties": {"class": n.ASSESSMENT_PROPERTIES, "label": "first",
                           "assessmentTime": "2026-11-21T12:00:00.000+00:00"}}
    original = json.loads(json.dumps(body))

    sent = bodies.checked_body(body, "link_assessment", request_class="NewRelationshipRequestBody",
                               properties_classes={n.ASSESSMENT_PROPERTIES})

    assert json.loads(sent) == original
    assert body == original, "the caller's dict is not changed"


def test_no_body_sends_no_body_on_attach_and_detach():
    assert bodies.checked_body(None, "link_x", request_class="NewRelationshipRequestBody",
                               properties_classes={n.OUTCOME_PROPERTIES}) is None
    assert bodies.checked_body(None, "detach_x", request_class="DeleteRelationshipRequestBody") is None


def test_a_required_body_is_refused_with_words():
    words = _refusal(bodies.checked_body, None, "update_decision", request_class="UpdateElementRequestBody",
                     required=True)
    assert "update_decision needs a request body" in words


def test_a_default_body_is_sent_only_when_none_is_given():
    default = {"class": "DeleteElementRequestBody", "cascadedDelete": True}
    assert json.loads(bodies.checked_body(None, "delete_x", request_class="DeleteElementRequestBody",
                                          default_body=default)) == default
    given = {"class": "DeleteElementRequestBody", "externalSourceName": "x"}
    assert json.loads(bodies.checked_body(given, "delete_x", request_class="DeleteElementRequestBody",
                                          default_body=default)) == given


def test_a_body_with_no_class_is_given_the_request_class_and_nothing_else():
    body = {"properties": {"class": n.PROJECT_TARGET_PROPERTIES, "label": "x"}}
    sent = json.loads(bodies.checked_body(body, "setup_project_target", request_class="NewRelationshipRequestBody",
                                          properties_classes={n.PROJECT_TARGET_PROPERTIES}))
    assert sent == {"class": "NewRelationshipRequestBody", **body}
    assert "class" not in body


def test_a_body_of_another_request_class_is_refused():
    words = _refusal(bodies.checked_body, {"class": "DeleteRelationshipRequestBody"}, "link_x",
                     request_class="NewRelationshipRequestBody")
    assert "NewRelationshipRequestBody" in words and "DeleteRelationshipRequestBody" in words


def test_a_model_body_is_sent_as_its_own_dump():
    model = NewRelationshipRequestBody.model_validate(
        {"class": "NewRelationshipRequestBody",
         "properties": {"class": n.OUTCOME_PROPERTIES, "label": "x"}})
    sent = json.loads(bodies.checked_body(model, "link_decision_outcome", request_class="NewRelationshipRequestBody",
                                          properties_classes={n.OUTCOME_PROPERTIES}))
    assert sent["class"] == "NewRelationshipRequestBody"
    assert sent["properties"]["class"] == n.OUTCOME_PROPERTIES and sent["properties"]["label"] == "x"


def test_something_that_is_not_a_body_is_refused():
    assert "not a str" in _refusal(bodies.checked_body, "{}", "link_x", request_class="NewRelationshipRequestBody")


def test_a_malformed_body_is_refused_with_words_not_a_raw_validation_error():
    words = _refusal(bodies.checked_body, {"class": "NewRelationshipRequestBody", "forLineage": "not-a-bool"},
                     "link_x", request_class="NewRelationshipRequestBody")
    assert "not a valid NewRelationshipRequestBody" in words


# --- rule 2: reads are not checked here ---------------------------------------------------------------------------

def test_the_6_4_reads_do_not_use_the_write_checker():
    from pyegeria.omvs.data_engineer import DataEngineer
    from pyegeria.omvs.governance_officer import GovernanceOfficer
    reads = [GovernanceOfficer._async_get_decisions_by_name, GovernanceOfficer._async_get_decision_by_guid,
             GovernanceOfficer._async_find_decisions, DataEngineer._async_get_data_values_by_name,
             DataEngineer._async_get_data_value_by_guid, DataEngineer._async_find_data_values]
    for read in reads:
        assert "checked_body" not in inspect.getsource(read), read.__qualname__


# --- rule 3: a SET of accepted Properties classes ------------------------------------------------------------------

ACCEPTED = {n.DATA_VALUE_PROPERTIES, n.LITERAL_DATA_VALUE_PROPERTIES}


@pytest.mark.parametrize("cls", sorted(ACCEPTED))
def test_each_accepted_class_passes(cls):
    body = {"class": "NewElementRequestBody", "properties": {"class": cls, "qualifiedName": "q"}}
    assert json.loads(bodies.checked_body(body, "create_data_value", request_class="NewElementRequestBody",
                                          properties_classes=ACCEPTED, required=True)) == body


@pytest.mark.parametrize("sent", ["DecisionProperties", None])
def test_another_class_or_none_is_refused_naming_every_accepted_class(sent):
    props = {"qualifiedName": "q"} if sent is None else {"class": sent, "qualifiedName": "q"}
    words = _refusal(bodies.checked_body, {"class": "NewElementRequestBody", "properties": props},
                     "create_data_value", request_class="NewElementRequestBody", properties_classes=ACCEPTED)
    for cls in ACCEPTED:
        assert cls in words
    assert ("DecisionProperties" in words) if sent else ("names no class" in words)


def test_a_single_class_string_is_accepted_as_a_set_of_one():
    assert bodies.check_properties_class({"class": n.BRANCH_PROPERTIES}, n.BRANCH_PROPERTIES, "m") == \
        n.BRANCH_PROPERTIES


def test_properties_that_are_not_an_object_are_refused():
    words = _refusal(bodies.check_properties_class, ["x"], {n.BRANCH_PROPERTIES}, "set_element_as_branch")
    assert n.BRANCH_PROPERTIES in words


def test_an_int_key_must_be_an_int():
    body = {"class": "NewRelationshipRequestBody",
            "properties": {"class": n.PROCESSING_VARIABLE_PROPERTIES, "position": "1"}}
    words = _refusal(bodies.checked_body, body, "link_processing_variable",
                     request_class="NewRelationshipRequestBody",
                     properties_classes={n.PROCESSING_VARIABLE_PROPERTIES}, int_keys=("position",))
    assert "position must be an int" in words
    body["properties"]["position"] = 0
    assert json.loads(bodies.checked_body(body, "link_processing_variable",
                                          request_class="NewRelationshipRequestBody",
                                          properties_classes={n.PROCESSING_VARIABLE_PROPERTIES},
                                          int_keys=("position",))) == body


# --- rule 4: unread keys are refused ---------------------------------------------------------------------------------

def test_an_unread_key_is_refused_naming_the_class_and_the_keys_it_reads():
    body = {"class": "NewClassificationRequestBody",
            "properties": {"class": n.BRANCH_PROPERTIES, "displayName": "main", "label": "not read"}}
    words = _refusal(bodies.checked_body, body, "set_element_as_branch",
                     request_class="NewClassificationRequestBody", properties_classes={n.BRANCH_PROPERTIES})
    assert "BranchProperties does not read label" in words
    for key in ("displayName", "scope", "purpose", "url"):
        assert key in words.split("reads:")[1]


def test_every_properties_class_the_6_4_wrappers_send_is_in_the_table():
    table = bodies.properties_class_fields()
    for cls in n.PROPERTIES_CLASSES:
        assert cls in table, cls


def test_a_class_missing_from_the_table_only_warns(monkeypatch):
    real = bodies.properties_class_fields()
    monkeypatch.setattr(bodies, "properties_class_fields",
                        lambda: {k: v for k, v in real.items() if k != n.OUTCOME_PROPERTIES})
    seen: list = []
    sink = logger.add(lambda message: seen.append(str(message)), level="WARNING")
    try:
        body = {"class": "NewRelationshipRequestBody",
                "properties": {"class": n.OUTCOME_PROPERTIES, "anythingAtAll": 1}}
        sent = bodies.checked_body(body, "link_decision_outcome", request_class="NewRelationshipRequestBody",
                                   properties_classes={n.OUTCOME_PROPERTIES})
    finally:
        logger.remove(sink)
    assert json.loads(sent) == body
    assert any("OutcomeProperties is not in PROPERTIES_CLASS_FIELDS" in line for line in seen)


# --- rule 5: one checker, in pyegeria/core --------------------------------------------------------------------------

def _source(module: str) -> str:
    return (REPO / "pyegeria" / "omvs" / f"{module}.py").read_text()


@pytest.mark.parametrize("module", SIX_FOUR_MODULES)
def test_each_6_4_module_imports_the_core_checker_and_defines_none_of_its_own(module):
    tree = ast.parse(_source(module))
    imported = {(node.module, alias.name) for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
                for alias in node.names}
    assert ("pyegeria.core.egeria_6_4_bodies", "checked_body") in imported
    assert ("pyegeria.core.egeria_6_4_bodies", "e64_url") in imported
    defined = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    for helper in ("_checked_6_4_body", "_e64_body", "_e64_link_body", "_e64_detach_body", "_e64_url",
                   "_require_properties_class", "_require_body"):
        assert helper not in defined, f"{module} defines {helper}"


@pytest.mark.parametrize("module", SIX_FOUR_MODULES)
def test_only_the_core_checker_imports_the_md_processing_table(module):
    assert "properties_class_fields" not in _source(module)


def test_the_url_builder_joins_a_names_path_to_the_open_metadata_root():
    assert bodies.e64_url("https://p:9443", "qs-view-server", n.ASSESSMENTS_UPDATE, assessmentGUID="g1") == \
        "https://p:9443/servers/qs-view-server/api/open-metadata/" + n.ASSESSMENTS_UPDATE.format(assessmentGUID="g1")


# --- rule 4 reaches every module's wrappers (A1 and A2 gained it in A6; A3 had it) ----------------------------------

def _capturing(cls, monkeypatch, calls):
    monkeypatch.setattr(cls, "check_connection", lambda self: "test")
    client = cls("view-server", "https://localhost:1", "user", "pwd")

    async def fake_make_request(method, url, payload=None, *args, **kwargs):
        calls.append((method, url, payload))
        raise AssertionError("nothing may be sent")

    client._async_make_request = fake_make_request
    return client


def _unread_cases():
    from pyegeria.omvs.data_engineer import DataEngineer
    from pyegeria.omvs.governance_officer import GovernanceOfficer
    element = {"class": "NewElementRequestBody"}
    relationship = {"class": "NewRelationshipRequestBody"}
    return [
        (GovernanceOfficer, "_async_create_decision", (),
         {**element, "properties": {"class": n.DECISION_PROPERTIES, "qualifiedName": "q", "startDate": "x"}},
         n.DECISION_PROPERTIES, "startDate"),
        (GovernanceOfficer, "_async_link_assessment", ("e", "d"),
         {**relationship, "properties": {"class": n.ASSESSMENT_PROPERTIES, "assessorType": "x"}},
         n.ASSESSMENT_PROPERTIES, "assessorType"),
        (DataEngineer, "_async_create_data_value", (),
         {**element, "properties": {"class": n.LITERAL_DATA_VALUE_PROPERTIES, "qualifiedName": "q",
                                    "dataValues": ["a"]}},
         n.LITERAL_DATA_VALUE_PROPERTIES, "dataValues"),
        (DataEngineer, "_async_link_embedded_data_value", ("p", "c"),
         {**relationship, "properties": {"class": n.EMBEDDED_DATA_VALUE_PROPERTIES, "ordinal": 1}},
         n.EMBEDDED_DATA_VALUE_PROPERTIES, "ordinal"),
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("case", range(4))
async def test_wrappers_refuse_unread_keys_before_sending(monkeypatch, case):
    cls, method, args, body, props_class, key = _unread_cases()[case]
    calls: list = []
    client = _capturing(cls, monkeypatch, calls)
    with pytest.raises(PyegeriaInvalidParameterException) as raised:
        await getattr(client, method)(*args, body)
    assert f"{props_class} does not read {key}" in str(raised.value)
    assert calls == []
