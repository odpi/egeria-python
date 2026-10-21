"""
ISSUE-160: AutomatedCuration's template builders did not send placeholders that
Egeria's templates now use, so the created elements kept literal ~{name}~ values:
- File System Directory: endpoint address ~{directoryAddress}~ (a folder survey
  then fails with BASIC-FILE-CONNECTOR-404-001), and deployedImplementationType.
- CSV Data File / YAML File Secrets Collection: endpoint address ~{fileAddress}~,
  and deployedImplementationType.
- PostgreSQL Relational Database: the description placeholder is databaseDescription.
No live server: the template lookup and the create call are captured.
"""
import pytest

from pyegeria.omvs.automated_curation import AutomatedCuration


def _client(captured: dict, monkeypatch) -> AutomatedCuration:
    monkeypatch.setattr(AutomatedCuration, "check_connection", lambda self: "test")
    client = AutomatedCuration("view-server", "https://localhost:1", "user", "pwd")

    async def fake_template_guid(type_name, **kwargs):
        captured["technology_type"] = type_name
        return "template-guid"

    async def fake_create(body=None):
        captured["body"] = body
        return "new-guid"

    client._async_get_template_guid_for_technology_type = fake_template_guid
    client._async_create_elem_from_template = fake_create
    return client


@pytest.mark.asyncio
async def test_folder_sends_directory_address_and_deployed_type(monkeypatch):
    captured = {}
    client = _client(captured, monkeypatch)
    await client._async_create_folder_element_from_template(
        "/data/landing", "landing", "fs1", description="d", version="1.0")

    values = captured["body"]["placeholderPropertyValues"]
    assert captured["technology_type"] == "File System Directory"
    assert values["directoryAddress"] == "/data/landing"
    assert values["directoryPathName"] == "/data/landing"  # still used in the qualifiedName
    assert values["deployedImplementationType"] == "File System Directory"


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["_async_create_csv_data_file_element_from_template",
                                    "_async_get_create_csv_data_file_element_from_template"])
async def test_csv_sends_file_address_and_deployed_type(method, monkeypatch):
    captured = {}
    client = _client(captured, monkeypatch)
    await getattr(client, method)("a.csv", "CSV Data File", "/data/a.csv", "1.0")

    values = captured["body"]["placeholderPropertyValues"]
    assert captured["technology_type"] == "CSV Data File"
    assert values["fileAddress"] == "/data/a.csv"
    assert values["filePathName"] == "/data/a.csv"
    assert values["deployedImplementationType"] == "CSV Data File"


@pytest.mark.asyncio
async def test_secrets_store_sends_file_address_and_deployed_type(monkeypatch):
    captured = {}
    client = _client(captured, monkeypatch)
    await client._async_create_secrets_store_element_from_template(
        "secrets/s.omsecrets", "s.omsecrets", "d", "1.0")

    values = captured["body"]["placeholderPropertyValues"]
    assert captured["technology_type"] == "YAML File Secrets Collection"
    assert values["fileAddress"] == "secrets/s.omsecrets"
    assert values["deployedImplementationType"] == "YAML File Secrets Collection"


@pytest.mark.asyncio
async def test_postgres_database_sends_database_description(monkeypatch):
    captured = {}
    client = _client(captured, monkeypatch)
    await client._async_create_postgres_database_element_from_template(
        "sales", "pg1", "db.example", "5432", "u", "p", description="Sales data")

    values = captured["body"]["placeholderPropertyValues"]
    assert captured["technology_type"] == "PostgreSQL Relational Database"
    assert values["databaseDescription"] == "Sales data"
    assert values["databaseName"] == "sales"
