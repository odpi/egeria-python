from typing import Any, cast
from unittest.mock import AsyncMock

import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.governance import GovernanceProcessor, logger


class _FakeCreateClient:
    def __init__(self):
        self.create_body = None

    async def _async_create_governance_definition(self, body: dict):
        self.create_body = body
        return "11111111-1111-1111-1111-111111111111"


class _RetryingSecurityGroupClient:
    def __init__(self):
        self.calls = []

    async def _async_create_governance_definition(self, body: dict):
        self.calls.append(body)
        if len(self.calls) == 1:
            raise Exception(
                "OMAG-REPOSITORY-HANDLER-400-001 An unsupported property named newProperties was passed; "
                "A property called domainIdentifier has been proposed for type SecurityGroup"
            )
        return "11111111-1111-1111-1111-111111111111"


class _RetryingClassMismatchClient:
    def __init__(self):
        self.calls = []

    async def _async_create_governance_definition(self, body: dict):
        self.calls.append(body)
        if len(self.calls) == 1:
            raise Exception(
                "OMAG-COMMON-400-029 The properties object passed on the createGovernanceDefinition operation "
                "is either null or not of the correct GovernanceDefinitionProperties class"
            )
        return "11111111-1111-1111-1111-111111111111"


@pytest.mark.asyncio
async def test_create_security_group_uses_security_group_properties_class():
    client = _FakeCreateClient()
    cmd = DrECommand(verb="Create", object_type="Security Group", attributes={}, raw_block="# Create Security Group")
    p = GovernanceProcessor(client=cast(Any, client), command=cmd, context={})
    p.render_result_markdown = AsyncMock(return_value="ok")
    p.parsed_output = {
        "attributes": {
            "Display Name": {"value": "Board Forecast Readers"},
            "Domain Identifier": {"value": "SECURITY"},
            "Distinguished Name": {"value": "cn=BoardForecastReaders,ou=SecurityGroups,dc=example,dc=com"},
        },
        "qualified_name": "SecurityGroup::SalesForecast::BoardForecastReaders::1.0",
    }

    out = await p.apply_changes()

    assert out == "ok"
    assert client.create_body is not None
    assert client.create_body["properties"]["class"] == "SecurityGroupProperties"
    assert client.create_body["properties"]["typeName"] == "SecurityGroup"
    assert "domainIdentifier" not in client.create_body["properties"]
    assert "summary" not in client.create_body["properties"]
    assert client.create_body["properties"]["distinguishedName"] == "cn=BoardForecastReaders,ou=SecurityGroups,dc=example,dc=com"


@pytest.mark.asyncio
async def test_create_security_group_compact_type_name_also_prunes_governance_only_fields():
    client = _FakeCreateClient()
    cmd = DrECommand(verb="Create", object_type="SecurityGroup", attributes={}, raw_block="# Create Security Group")
    p = GovernanceProcessor(client=cast(Any, client), command=cmd, context={})
    p.render_result_markdown = AsyncMock(return_value="ok")
    p.parsed_output = {
        "attributes": {
            "Display Name": {"value": "Board Forecast Readers"},
            "Domain Identifier": {"value": "SECURITY"},
            "Distinguished Name": {"value": "cn=BoardForecastReaders,ou=SecurityGroups,dc=example,dc=com"},
        },
        "qualified_name": "SecurityGroup::SalesForecast::BoardForecastReaders::1.0",
    }

    await p.apply_changes()

    assert client.create_body is not None
    assert client.create_body["properties"]["class"] == "SecurityGroupProperties"
    assert "domainIdentifier" not in client.create_body["properties"]
    assert "summary" not in client.create_body["properties"]


@pytest.mark.asyncio
async def test_create_security_group_retries_after_newproperties_rejection_with_narrowed_payload():
    client = _RetryingSecurityGroupClient()
    cmd = DrECommand(verb="Create", object_type="Security Group", attributes={}, raw_block="# Create Security Group")
    p = GovernanceProcessor(client=cast(Any, client), command=cmd, context={})
    p.render_result_markdown = AsyncMock(return_value="ok")
    p.parsed_output = {
        "attributes": {
            "Display Name": {"value": "Board Forecast Readers"},
            "Domain Identifier": {"value": "SECURITY"},
            "Summary": {"value": "Security group summary"},
            "Distinguished Name": {"value": "cn=BoardForecastReaders,ou=SecurityGroups,dc=example,dc=com"},
        },
        "qualified_name": "SecurityGroup::SalesForecast::BoardForecastReaders::1.0",
    }

    out = await p.apply_changes()

    assert out == "ok"
    assert len(client.calls) == 2
    assert "domainIdentifier" not in client.calls[1]["properties"]
    assert client.calls[1]["properties"]["distinguishedName"] == "cn=BoardForecastReaders,ou=SecurityGroups,dc=example,dc=com"


@pytest.mark.asyncio
async def test_create_security_group_prunes_even_if_derived_egeria_type_name_is_wrong():
    client = _FakeCreateClient()
    cmd = DrECommand(verb="Create", object_type="Security Group", attributes={}, raw_block="# Create Security Group")
    p = GovernanceProcessor(client=cast(Any, client), command=cmd, context={})
    p.render_result_markdown = AsyncMock(return_value="ok")
    p.egeria_type_name = "GovernanceDefinition"
    p.parsed_output = {
        "attributes": {
            "Display Name": {"value": "Board Forecast Readers"},
            "Domain Identifier": {"value": "SECURITY"},
            "Distinguished Name": {"value": "cn=BoardForecastReaders,ou=SecurityGroups,dc=example,dc=com"},
        },
        "qualified_name": "SecurityGroup::SalesForecast::BoardForecastReaders::1.0",
    }

    out = await p.apply_changes()

    assert out == "ok"
    assert client.create_body is not None
    assert client.create_body["properties"]["class"] == "SecurityGroupProperties"
    assert client.create_body["properties"]["typeName"] == "SecurityGroup"
    assert "domainIdentifier" not in client.create_body["properties"]


@pytest.mark.asyncio
async def test_create_security_group_preserves_user_defined_keys_in_extended_properties():
    client = _FakeCreateClient()
    cmd = DrECommand(verb="Create", object_type="Security Group", attributes={}, raw_block="# Create Security Group")
    p = GovernanceProcessor(client=cast(Any, client), command=cmd, context={})
    p.render_result_markdown = AsyncMock(return_value="ok")
    p.parsed_output = {
        "attributes": {
            "Display Name": {"value": "Board Forecast Readers"},
            "Domain Identifier": {"value": "SECURITY"},
            "Extended Properties": {"value": {"domainIdentifier": 3, "kept": True}},
            "Distinguished Name": {"value": "cn=BoardForecastReaders,ou=SecurityGroups,dc=example,dc=com"},
        },
        "qualified_name": "SecurityGroup::SalesForecast::BoardForecastReaders::1.0",
    }

    out = await p.apply_changes()

    assert out == "ok"
    props = client.create_body["properties"]
    assert "domainIdentifier" not in props
    assert props.get("extendedProperties", {}).get("kept") is True
    assert props.get("extendedProperties", {}).get("domainIdentifier") == 3


@pytest.mark.asyncio
async def test_create_security_group_retries_with_base_class_when_server_requires_governance_definition_properties():
    client = _RetryingClassMismatchClient()
    cmd = DrECommand(verb="Create", object_type="Security Group", attributes={}, raw_block="# Create Security Group")
    p = GovernanceProcessor(client=cast(Any, client), command=cmd, context={})
    p.render_result_markdown = AsyncMock(return_value="ok")
    p.parsed_output = {
        "attributes": {
            "Display Name": {"value": "Board Forecast Readers"},
            "Domain Identifier": {"value": "SECURITY"},
            "Distinguished Name": {"value": "cn=BoardForecastReaders,ou=SecurityGroups,dc=example,dc=com"},
        },
        "qualified_name": "SecurityGroup::SalesForecast::BoardForecastReaders::1.0",
    }

    out = await p.apply_changes()

    assert out == "ok"
    assert len(client.calls) == 2
    assert client.calls[0]["properties"]["class"] == "SecurityGroupProperties"
    assert client.calls[1]["properties"]["class"] == "GovernanceDefinitionProperties"
    assert "domainIdentifier" not in client.calls[1]["properties"]
    assert client.calls[1]["properties"].get("additionalProperties", {}).get("distinguishedName") == "cn=BoardForecastReaders,ou=SecurityGroups,dc=example,dc=com"


@pytest.mark.asyncio
async def test_create_security_group_preserves_user_defined_keys_in_additional_properties():
    client = _FakeCreateClient()
    cmd = DrECommand(verb="Create", object_type="Security Group", attributes={}, raw_block="# Create Security Group")
    p = GovernanceProcessor(client=cast(Any, client), command=cmd, context={})
    p.render_result_markdown = AsyncMock(return_value="ok")
    p.parsed_output = {
        "attributes": {
            "Display Name": {"value": "Board Forecast Readers"},
            "Domain Identifier": {"value": "SECURITY"},
            "Additional Properties": {"value": {"domainIdentifier": 3, "customKey": "kept"}},
            "Distinguished Name": {"value": "cn=BoardForecastReaders,ou=SecurityGroups,dc=example,dc=com"},
        },
        "qualified_name": "SecurityGroup::SalesForecast::BoardForecastReaders::1.0",
    }

    out = await p.apply_changes()

    assert out == "ok"
    props = client.create_body["properties"]
    assert "domainIdentifier" not in props
    assert props.get("additionalProperties", {}).get("domainIdentifier") == 3
    assert props.get("additionalProperties", {}).get("customKey") == "kept"


def test_strip_keys_recursive_warns_with_context_and_preserves_user_defined_branches(monkeypatch):
    warnings: list[str] = []

    def _capture(msg: str):
        warnings.append(msg)

    monkeypatch.setattr(logger, "warning", _capture)

    payload = {
        "domainIdentifier": 1,
        "extendedProperties": {"domainIdentifier": 99, "kept": True},
        "nested": {"summary": "drop me"},
    }

    cleaned = GovernanceProcessor._strip_keys_recursive(
        payload,
        {"domainIdentifier", "summary"},
        preserve_under={"extendedProperties", "additionalProperties"},
        context_label="Create Security Group retry payload",
    )

    assert "domainIdentifier" not in cleaned
    assert "summary" not in cleaned.get("nested", {})
    assert cleaned.get("extendedProperties", {}).get("domainIdentifier") == 99
    assert warnings
    assert "Create Security Group retry payload" in warnings[0]



