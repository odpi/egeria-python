"""
ISSUE-160 follow-up: the remaining template-placeholder gaps.
- Postgres server/database templates take credentials from a secrets store
  (secretsStorePathName / secretsCollectionName); databaseUserId and
  databasePassword are no longer placeholders, so db_user/db_pwd are deprecated.
- An unset optional argument must not leave a literal ~{name}~: it is sent as "".
- Unity Catalog and Kafka builders send the placeholders their templates declare.
No live server: the template lookup and the create call are captured.
"""
import warnings

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


def _values(captured):
    return captured["body"]["placeholderPropertyValues"]


@pytest.mark.asyncio
async def test_postgres_server_sends_secrets_and_resource_name(monkeypatch):
    captured = {}
    client = _client(captured, monkeypatch)
    await client._async_create_postgres_server_element_from_template(
        "pg1", "db.example", "5432", secrets_store_path_name="secrets/pg.omsecrets",
        secrets_collection_name="pg1-creds", version="16")

    values = _values(captured)
    assert values["secretsStorePathName"] == "secrets/pg.omsecrets"
    assert values["secretsCollectionName"] == "pg1-creds"
    assert values["resourceName"] == "pg1"
    assert values["versionIdentifier"] == "16"
    assert "databaseUserId" not in values and "databasePassword" not in values


@pytest.mark.asyncio
async def test_postgres_db_user_and_password_are_deprecated_and_not_sent(monkeypatch):
    captured = {}
    client = _client(captured, monkeypatch)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        await client._async_create_postgres_database_element_from_template(
            "sales", "pg1", "db.example", "5432", "user", "secret", description="Sales")

    values = _values(captured)
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)
    assert "databaseUserId" not in values and "databasePassword" not in values
    assert "secret" not in values.values()
    assert values["databaseDescription"] == "Sales"
    assert values["secretsStorePathName"] == "" and values["secretsCollectionName"] == ""


@pytest.mark.asyncio
async def test_unset_optional_placeholders_are_sent_as_empty_strings(monkeypatch):
    captured = {}
    client = _client(captured, monkeypatch)
    await client._async_create_folder_element_from_template("/data/landing", "landing", None)

    values = _values(captured)
    for key in ("description", "versionIdentifier", "fileSystemName"):
        assert values[key] == "", key


@pytest.mark.asyncio
async def test_csv_unset_file_system_and_description_are_empty_strings(monkeypatch):
    captured = {}
    client = _client(captured, monkeypatch)
    await client._async_create_csv_data_file_element_from_template("a.csv", "CSV Data File", "/data/a.csv", None)

    values = _values(captured)
    assert values["fileSystemName"] == ""
    assert values["description"] == ""
    assert values["versionIdentifier"] == ""


@pytest.mark.asyncio
async def test_kafka_sends_resource_name_and_version(monkeypatch):
    captured = {}
    client = _client(captured, monkeypatch)
    await client._async_create_kafka_server_element_from_template("kafka1", "kafka.example", "9092")

    values = _values(captured)
    assert values["resourceName"] == "kafka1"
    assert values["versionIdentifier"] == ""


@pytest.mark.asyncio
async def test_uc_server_sends_resource_name(monkeypatch):
    captured = {}
    client = _client(captured, monkeypatch)
    await client._async_create_uc_server_element_from_template("uc1", "http://uc.example", "8080",
                                                               resource_name="uc-main")
    assert _values(captured)["resourceName"] == "uc-main"


@pytest.mark.asyncio
async def test_uc_catalog_sends_server_qualified_name(monkeypatch):
    captured = {}
    client = _client(captured, monkeypatch)
    await client._async_create_uc_catalog_element_from_template(
        "cat1", "http://uc.example:8080", uc_server_qualified_name="SoftwareServer::uc1")
    assert _values(captured)["ucServerQualifiedName"] == "SoftwareServer::uc1"


@pytest.mark.asyncio
@pytest.mark.parametrize("method, args", [
    ("_async_create_uc_table_element_from_template",
     ("cat1", "sch1", "t1", "MANAGED", "s3://b/t1", "DELTA", "http://uc.example:8080")),
    ("_async_create_uc_function_element_from_template",
     ("cat1", "sch1", "f1", "http://uc.example:8080")),
])
async def test_uc_table_and_function_send_root_schema_type(method, args, monkeypatch):
    captured = {}
    client = _client(captured, monkeypatch)
    await getattr(client, method)(*args, root_schema_type_qualified_name="RootSchemaType::x")
    assert _values(captured)["rootSchemaTypeQualifiedName"] == "RootSchemaType::x"


@pytest.mark.asyncio
async def test_uc_volume_sends_directory_and_local_storage(monkeypatch):
    captured = {}
    client = _client(captured, monkeypatch)
    await client._async_create_uc_volume_element_from_template(
        "cat1", "sch1", "v1", "MANAGED", "s3://b/v1", "http://uc.example:8080",
        directory_path_name="/volumes/v1", local_storage_location="/mnt/v1")

    values = _values(captured)
    assert values["directoryPathName"] == "/volumes/v1"
    assert values["localStorageLocation"] == "/mnt/v1"


def test_sync_wrappers_pass_new_arguments_through(monkeypatch):
    captured = {}
    client = _client(captured, monkeypatch)
    client.create_postgres_server_element_from_template(
        "pg1", "db.example", "5432", secrets_store_path_name="s.omsecrets", secrets_collection_name="c")
    assert _values(captured)["secretsStorePathName"] == "s.omsecrets"
    client.create_uc_volume_element_from_template(
        "cat1", "sch1", "v1", "MANAGED", "s3://b/v1", "http://uc.example:8080", local_storage_location="/mnt/v1")
    assert _values(captured)["localStorageLocation"] == "/mnt/v1"
