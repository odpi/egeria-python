"""
ISSUE-85: SolutionArchitect solution-port create/update/delete/find/get wrappers.
ISSUE-154: cascade deletes send Egeria's cascadedDelete; renamed property classes are accepted
under both names.
ISSUE-158: GOV_DEF_PROPERTIES_LIST covers DataQualityRuleProperties; the governance create fallback
names the fields it would drop.
ISSUE-159: archive_project / archive_collection send the delete with deleteMethod ARCHIVE.
"""
import json

import pytest

from md_processing.v2.governance import GovernanceProcessor
from pyegeria.core._server_client import ServerClient
from pyegeria.models import DeleteElementRequestBody
from pyegeria.omvs.actor_manager import ActorManager
from pyegeria.omvs.classification_explorer import ClassificationExplorer
from pyegeria.omvs.collection_manager import CollectionManager
from pyegeria.omvs.governance_officer import GOV_DEF_PROPERTIES_LIST
from pyegeria.omvs.project_manager import ProjectManager
from pyegeria.omvs.solution_architect import SolutionArchitect


class _Response:
    def json(self):
        return {"relatedHTTPCode": 200, "guid": "new-guid", "elements": [{"elementHeader": {"guid": "p1"}}]}


def _capture(cls, monkeypatch):
    monkeypatch.setattr(cls, "check_connection", lambda self: "test")
    client = cls("view-server", "https://localhost:1", "user", "pwd")
    calls: list = []

    async def fake_make_request(method, url, payload=None, *args, **kwargs):
        calls.append({"method": method, "url": url,
                      "body": json.loads(payload) if isinstance(payload, str) else payload})
        return _Response()

    client._async_make_request = fake_make_request
    return client, calls


# --- ISSUE-85 -------------------------------------------------------------------------------

SA_ROOT = "/api/open-metadata/solution-architect"


async def test_create_solution_port(monkeypatch):
    client, calls = _capture(SolutionArchitect, monkeypatch)
    guid = await client._async_create_solution_port({
        "class": "NewElementRequestBody",
        "properties": {"class": "SolutionPortProperties", "qualifiedName": "SolutionPort::p", "direction": "INPUT"},
    })
    assert guid == "new-guid"
    assert calls[0]["url"].endswith(f"{SA_ROOT}/solution-ports")
    assert calls[0]["body"]["properties"]["class"] == "SolutionPortProperties"
    assert calls[0]["body"]["properties"]["direction"] == "INPUT"


@pytest.mark.parametrize("method, args, tail, body_class", [
    ("_async_create_solution_port_from_template",
     ({"class": "TemplateRequestBody", "templateGUID": "t1"},), "/solution-ports/from-template",
     "TemplateRequestBody"),
    ("_async_update_solution_port",
     ("p1", {"class": "UpdateElementRequestBody",
             "properties": {"class": "SolutionPortProperties", "direction": "OUTPUT"}}),
     "/solution-ports/p1/update", "UpdateElementRequestBody"),
    ("_async_delete_solution_port", ("p1",), "/solution-ports/p1/delete", "DeleteElementRequestBody"),
    ("_async_get_solution_ports_by_name", ("port",), "/solution-ports/by-name", "FilterRequestBody"),
    ("_async_find_solution_ports", ("port",), "/solution-ports/by-search-string", "SearchStringRequestBody"),
    ("_async_get_solution_port_by_guid", ("p1",), "/solution-ports/p1/retrieve", "GetRequestBody"),
])
async def test_solution_port_endpoints(monkeypatch, method, args, tail, body_class):
    client, calls = _capture(SolutionArchitect, monkeypatch)
    await getattr(client, method)(*args)
    assert calls[0]["method"] == "POST"
    assert calls[0]["url"].endswith(SA_ROOT + tail)
    assert calls[0]["body"]["class"] == body_class


# --- ISSUE-159 ------------------------------------------------------------------------------

@pytest.mark.parametrize("cls, method, tail", [
    (ProjectManager, "_async_archive_project", "/project-manager/projects/g1/delete"),
    (CollectionManager, "_async_archive_collection", "/collection-manager/collections/g1/delete"),
])
async def test_archive_sends_delete_with_archive_method(monkeypatch, cls, method, tail):
    client, calls = _capture(cls, monkeypatch)
    await getattr(client, method)("g1")
    assert calls[0]["url"].endswith(tail)
    assert calls[0]["body"]["class"] == "DeleteElementRequestBody"
    assert calls[0]["body"]["deleteMethod"] == "ARCHIVE"
    assert not calls[0]["body"].get("cascadedDelete")


async def test_archive_keeps_caller_fields_but_forces_archive(monkeypatch):
    client, calls = _capture(ProjectManager, monkeypatch)
    caller_body = {"class": "DeleteElementRequestBody", "deleteMethod": "PURGE", "archiveProcess": "RE close-out"}
    await client._async_archive_project("g1", caller_body)
    assert calls[0]["body"]["deleteMethod"] == "ARCHIVE"
    assert calls[0]["body"]["archiveProcess"] == "RE close-out"
    assert caller_body["deleteMethod"] == "PURGE"  # the caller's dict is not changed


def test_archive_body_from_model():
    body = DeleteElementRequestBody.model_validate({"class": "DeleteElementRequestBody", "deleteMethod": "PURGE"})
    archived = ServerClient._archive_delete_body(body)
    assert archived.delete_method == "ARCHIVE"
    assert body.delete_method == "PURGE"


# --- ISSUE-154 ------------------------------------------------------------------------------

@pytest.mark.parametrize("name", ["RetentionClassificationProperties", "RetentionProperties"])
async def test_retention_accepts_old_and_new_class_names(monkeypatch, name):
    client, calls = _capture(ClassificationExplorer, monkeypatch)
    await client._async_set_retention_classification(
        "e1", {"class": "NewClassificationRequestBody", "properties": {"class": name, "retentionBasis": 2}})
    assert calls[0]["body"]["properties"]["class"] == name


@pytest.mark.parametrize("name", ["SecurityGroupMembershipProperties", "SecurityListMembershipProperties"])
async def test_security_membership_accepts_old_and_new_class_names(monkeypatch, name):
    client, calls = _capture(ActorManager, monkeypatch)
    await client._async_add_security_group_membership(
        "u1", body={"class": "NewClassificationRequestBody", "properties": {"class": name, "groups": ["g"]}})
    assert calls[0]["body"]["properties"]["class"] == name


# --- ISSUE-158 ------------------------------------------------------------------------------

def test_governance_definition_list_covers_data_quality_rule_without_duplicates():
    assert "DataQualityRuleProperties" in GOV_DEF_PROPERTIES_LIST
    assert len(GOV_DEF_PROPERTIES_LIST) == len(set(GOV_DEF_PROPERTIES_LIST))


def test_base_fallback_reports_type_specific_fields():
    create_props = {
        "class": "GovernanceMetricProperties", "typeName": "GovernanceMetric",
        "qualifiedName": "GovernanceMetric::m", "displayName": "m",
        "measurement": "count of open issues", "target": "", "domainIdentifier": None,
    }
    fallback = GovernanceProcessor._to_base_governance_definition_properties(create_props, "Governance Metric")
    assert GovernanceProcessor._fields_dropped_by_base_fallback(create_props, fallback) == ["measurement"]


def test_base_fallback_with_only_cross_type_fields_drops_nothing():
    create_props = {"class": "GovernanceStrategyProperties", "typeName": "GovernanceStrategy",
                    "qualifiedName": "GovernanceStrategy::s", "displayName": "s", "description": "d"}
    fallback = GovernanceProcessor._to_base_governance_definition_properties(create_props, "Governance Strategy")
    assert GovernanceProcessor._fields_dropped_by_base_fallback(create_props, fallback) == []
