# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Regression test for PYEGERIA_ISSUES.md ISSUE-79's "naming trap" follow-up
(Egeria team update, 2026-08-30): a governance action type is registered
under `<governanceEngineName>::<requestType>` -- two colons, engine name
singular -- not the single-colon/plural-engine forms several
`AutomatedCuration.initiate_*_survey` convenience methods were hardcoding.
A wrong name doesn't fail loudly with a clear message; it raises
OMAG-GENERIC-HANDLERS-400-013 ("the name is not recognized") without
saying what it wanted instead.

Confirmed correct names either directly from the Egeria team (FileSurvey,
ApacheKafkaSurvey) or independently via a live
`EgeriaTech.get_elements("GovernanceActionType")` query against a real
server (UnityCatalogSurvey, PostgreSQLSurvey) during this repo's own
ISSUE-79 investigation.

No live server needed: a mocked `_async_make_request` confirms the actual
outgoing `governanceActionTypeQualifiedName`.
"""
from unittest.mock import MagicMock, patch

from pyegeria.omvs.automated_curation import AutomatedCuration


def _client():
    with patch("pyegeria.core._base_server_client.BaseServerClient.check_connection", return_value=""):
        return AutomatedCuration(view_server="vs", platform_url="https://localhost:9443",
                                  user_id="u", user_pwd="p")


def _mock_request(capture):
    async def fake(method, url, body=None, **kwargs):
        capture["body"] = body
        resp = MagicMock()
        resp.json = MagicMock(return_value={"guid": "action-guid"})
        return resp
    return fake


def test_initiate_file_folder_survey_default_name():
    client = _client()
    cap = {}
    client._async_make_request = _mock_request(cap)

    client.initiate_file_folder_survey("folder-guid")

    assert cap["body"]["governanceActionTypeQualifiedName"] == "FileSurvey::survey-folder"


def test_initiate_file_survey_name():
    client = _client()
    cap = {}
    client._async_make_request = _mock_request(cap)

    client.initiate_file_survey("file-guid")

    assert cap["body"]["governanceActionTypeQualifiedName"] == "FileSurvey::survey-data-file"


def test_initiate_postgres_database_survey_name():
    client = _client()
    cap = {}
    client._async_make_request = _mock_request(cap)

    client.initiate_postgres_database_survey("db-guid")

    assert cap["body"]["governanceActionTypeQualifiedName"] == "PostgreSQLSurvey::survey-postgres-database"


def test_initiate_postgres_server_survey_name_was_already_correct():
    client = _client()
    cap = {}
    client._async_make_request = _mock_request(cap)

    client.initiate_postgres_server_survey("server-guid")

    assert cap["body"]["governanceActionTypeQualifiedName"] == "PostgreSQLSurvey::survey-postgres-server"


def test_initiate_kafka_server_survey_name():
    client = _client()
    cap = {}
    client._async_make_request = _mock_request(cap)

    client.initiate_kafka_server_survey("kafka-guid")

    assert cap["body"]["governanceActionTypeQualifiedName"] == "ApacheKafkaSurvey::survey-kafka-server"


def test_initiate_uc_server_survey_name():
    client = _client()
    cap = {}
    client._async_make_request = _mock_request(cap)

    client.initiate_uc_server_survey("uc-server-guid")

    assert cap["body"]["governanceActionTypeQualifiedName"] == "UnityCatalogSurvey::survey-unity-catalog-server"


def test_initiate_uc_schema_survey_name():
    client = _client()
    cap = {}
    client._async_make_request = _mock_request(cap)

    client.initiate_uc_schema_survey("uc-schema-guid")

    assert cap["body"]["governanceActionTypeQualifiedName"] == "UnityCatalogSurvey::survey-unity-catalog-schema"
