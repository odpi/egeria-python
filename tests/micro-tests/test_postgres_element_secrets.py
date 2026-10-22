"""
ISSUE-160 follow-up: Egeria's Postgres templates take credentials from a secrets
store, so the Dr.Egeria 'Create Postgres Server/Database Element' commands pass
secrets_store_path_name / secrets_collection_name (plus version, and
resource_name for the server) and no longer pass the deprecated db_user/db_pwd.
"""
import json
from pathlib import Path
from typing import Any, cast

import pytest

from md_processing.v2.asset_maker import AssetMakerProcessor
from md_processing.v2.extraction import DrECommand

SPEC_FILE = (Path(__file__).resolve().parents[2]
             / "md_processing/data/compact_commands/commands_asset_maker_compact.json")


class _FakeCuration:
    def __init__(self):
        self.calls = {}

    async def _async_create_postgres_server_element_from_template(self, **kwargs):
        self.calls["server"] = kwargs
        return "aaaaaaaa-0000-0000-0000-000000000001"

    async def _async_create_postgres_database_element_from_template(self, **kwargs):
        self.calls["database"] = kwargs
        return "aaaaaaaa-0000-0000-0000-000000000002"


class _FakeClient:
    def __init__(self):
        self.automated_curation = _FakeCuration()


async def _async_value(value):
    return value


async def _run(object_type: str, om_type: str, attributes: dict) -> _FakeCuration:
    client = _FakeClient()
    p = AssetMakerProcessor(client=cast(Any, client),
                            command=DrECommand(verb="Create", object_type=object_type, attributes={},
                                               raw_block=f"## Create {object_type}"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": om_type}
    p.parsed_output = {"qualified_name": None,
                       "attributes": {k: {"value": v} for k, v in attributes.items()}}
    p.render_result_markdown = lambda guid: _async_value(guid)
    await p.apply_changes()
    return client.automated_curation


COMMON = {
    "Host Name": "localhost",
    "Port": "5432",
    "Secrets Store Path Name": "loading-bay/secrets/default.omsecrets",
    "Secrets Collection Name": "postgres",
    "Version Identifier": "1.0",
    # Stale values a user may still have in an old template: must not be sent.
    "Database User Id": "old-user",
    "Database Password": "old-pwd",
}


@pytest.mark.asyncio
async def test_postgres_server_passes_secrets_not_credentials():
    curation = await _run("Postgres Server Element", "SoftwareServer",
                          {**COMMON, "Postgres Server Name": "pg1", "Resource Name": "pg1-res"})
    kwargs = curation.calls["server"]
    assert kwargs["secrets_store_path_name"] == "loading-bay/secrets/default.omsecrets"
    assert kwargs["secrets_collection_name"] == "postgres"
    assert kwargs["version"] == "1.0"
    assert kwargs["resource_name"] == "pg1-res"
    assert "db_user" not in kwargs and "db_pwd" not in kwargs


@pytest.mark.asyncio
async def test_postgres_database_passes_secrets_not_credentials():
    curation = await _run("Postgres Database Element", "RelationalDatabase",
                          {**COMMON, "Postgres Database Name": "db1", "Postgres Server Name": "pg1"})
    kwargs = curation.calls["database"]
    assert kwargs["secrets_store_path_name"] == "loading-bay/secrets/default.omsecrets"
    assert kwargs["secrets_collection_name"] == "postgres"
    assert kwargs["version"] == "1.0"
    assert "db_user" not in kwargs and "db_pwd" not in kwargs


@pytest.mark.parametrize("command", ["Create Postgres Server Element", "Create Postgres Database Element"])
def test_postgres_specs_expose_secrets_fields(command):
    spec = json.loads(SPEC_FILE.read_text())
    attrs = spec["commands"][command]["custom_attributes"]
    assert {"Secrets Store Path Name", "Secrets Collection Name", "Version Identifier"} <= set(attrs)
    assert "Database User Id" not in attrs and "Database Password" not in attrs
