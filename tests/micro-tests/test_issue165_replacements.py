"""
ISSUE-165: SDK methods whose Egeria endpoints were removed now delegate, deprecated, to the
replacements the Egeria team named (Mandy Chessell, 2026-10-23):
  analysis reports         -> SurveyReport assets (AssetMaker) and the ReportSubject relationship
  subject-area membership  -> CollectionMembership on the subject area
  find_governance_action_processes -> find_governance_definitions(type GovernanceActionProcess)
  get_gov_def_in_context   -> get_governance_definition_by_guid (context returned by default)
  data classifications     -> data value specifications (best-effort mapping)
No live server: requests are captured at the ServerClient level, so delegated clients are seen too.
"""
import json

import pytest

from pyegeria.core._server_client import ServerClient
from pyegeria.core._exceptions import PyegeriaException


class _Response:
    def json(self):
        return {"class": "GUIDResponse", "guid": "new-guid", "elements": [], "element": {},
                "relatedHTTPCode": 200}


@pytest.fixture
def calls(monkeypatch):
    captured: list = []

    async def fake_make_request(self, method, url, payload=None, *args, **kwargs):
        captured.append({"method": method, "url": url,
                         "body": json.loads(payload) if isinstance(payload, str) else payload})
        return _Response()

    monkeypatch.setattr(ServerClient, "check_connection", lambda self: "test")
    monkeypatch.setattr(ServerClient, "_async_make_request", fake_make_request)
    return captured


def _make(cls):
    return cls("view-server", "https://localhost:1", "user", "pwd")


@pytest.mark.asyncio
async def test_analysis_reports_become_survey_report_assets(calls):
    from pyegeria.omvs.data_discovery import DataDiscovery
    dd = _make(DataDiscovery)
    with pytest.warns(DeprecationWarning, match="SurveyReport is now a Report asset"):
        await dd._async_create_analysis_report({
            "class": "NewElementRequestBody",
            "properties": {"class": "AnalysisReportProperties", "qualifiedName": "q", "displayName": "r"}})
    assert "/api/open-metadata/asset-maker/assets" in calls[0]["url"]
    assert calls[0]["body"]["properties"]["class"] == "SurveyReportProperties"

    with pytest.warns(DeprecationWarning):
        await dd._async_find_analysis_reports("weekly")
    assert calls[1]["url"].endswith("/asset-maker/assets/by-search-string")
    assert calls[1]["body"]["metadataElementTypeName"] == "SurveyReport"


@pytest.mark.asyncio
@pytest.mark.parametrize("method, verb", [("_async_link_analysis_report_to_asset", "attach"),
                                          ("_async_detach_analysis_report_from_asset", "detach")])
async def test_analysis_report_link_is_report_subject(calls, method, verb):
    from pyegeria.omvs.data_discovery import DataDiscovery
    dd = _make(DataDiscovery)
    with pytest.warns(DeprecationWarning, match="report_subject"):
        await getattr(dd, method)("report-guid", "asset-guid")
    # ReportSubject: /elements/{subjectGUID}/reports/{reportGUID}/attach - the asset is the subject
    assert calls[0]["url"].endswith(f"/asset-maker/elements/asset-guid/reports/report-guid/{verb}")


@pytest.mark.asyncio
async def test_find_governance_action_processes_searches_definitions_of_that_type(calls):
    from pyegeria.omvs.governance_officer import GovernanceOfficer
    go = _make(GovernanceOfficer)
    with pytest.warns(DeprecationWarning, match="find_governance_definitions"):
        await go._async_find_governance_action_processes("onboarding")
    assert calls[0]["url"].endswith("/governance-definitions/by-search-string")
    assert calls[0]["body"]["metadataElementTypeName"] == "GovernanceActionProcess"
    assert calls[0]["body"]["searchString"] == "onboarding"


@pytest.mark.asyncio
async def test_get_gov_def_in_context_is_a_plain_retrieve(calls):
    from pyegeria.omvs.governance_officer import GovernanceOfficer
    go = _make(GovernanceOfficer)
    with pytest.warns(DeprecationWarning, match="returns the context by default"):
        await go._async_get_gov_def_in_context("def-guid")
    assert calls[0]["url"].endswith("/governance-definitions/def-guid/retrieve")


@pytest.mark.asyncio
async def test_data_classifications_map_to_data_value_specifications(calls):
    from pyegeria.omvs.data_designer import DataDesigner
    dsn = _make(DataDesigner)
    with pytest.warns(DeprecationWarning, match="data value specifications"):
        await dsn._async_create_data_classification({
            "class": "NewElementRequestBody",
            "properties": {"class": "DataClassificationProperties", "qualifiedName": "q"}})
    assert calls[0]["url"].endswith("/data-designer/data-value-specifications")
    assert calls[0]["body"]["properties"]["class"] == "DataClassProperties"

    with pytest.warns(DeprecationWarning):
        await dsn._async_link_data_classification_to_data_field("spec-guid", "field-guid")
    assert calls[1]["url"].endswith("/data-designer/elements/field-guid/data-value-specifications/spec-guid/attach")
    assert calls[1]["body"]["properties"]["class"] == "DataValueAssignmentProperties"

    with pytest.warns(DeprecationWarning):
        await dsn._async_detach_data_classification_from_data_field("spec-guid", "field-guid")
    assert calls[2]["url"].endswith("/data-designer/elements/field-guid/data-value-specifications/spec-guid/detach")


@pytest.mark.asyncio
async def test_subject_area_membership_needs_the_subject_area_guid(calls):
    from pyegeria.omvs.classification_explorer import ClassificationExplorer
    ce = _make(ClassificationExplorer)
    # Without the subject area's GUID there is nothing to delegate to: a clear error, no request.
    with pytest.warns(DeprecationWarning):
        with pytest.raises(PyegeriaException):
            await ce._async_add_element_to_subject_area("el-guid", {"class": "NewClassificationRequestBody"})
    assert calls == []

    with pytest.warns(DeprecationWarning, match="add_to_collection"):
        await ce._async_add_element_to_subject_area("el-guid", {"class": "NewClassificationRequestBody"},
                                                    subject_area_guid="sa-guid")
    assert calls[0]["url"].endswith("/collections/sa-guid/members/el-guid/attach")

    with pytest.warns(DeprecationWarning, match="remove_from_collection"):
        await ce._async_remove_element_from_subject_area("el-guid", subject_area_guid="sa-guid")
    assert calls[1]["url"].endswith("/collections/sa-guid/members/el-guid/detach")


def test_dr_egeria_governance_context_no_longer_calls_the_removed_endpoint():
    import inspect
    from md_processing.v2.governance import GovernanceContextProcessor
    src = inspect.getsource(GovernanceContextProcessor)
    assert "_async_get_governance_definition_by_guid" in src
    assert "_async_get_gov_def_in_context" not in src
