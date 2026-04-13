import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.parsing import AttributeFirstParser
from pyegeria.core._globals import GovernanceDomains, resolve_enum


@pytest.mark.parametrize(
    "raw_value, expected",
    [
        ("ALL", 0),
        ("data", 1),
        ("Privacy", 2),
        ("IT_INFRASTRUCTURE", 4),
        ("IT Infrastructure", 4),
        ("software-development", 5),
        ("Asset Management", 7),
        ("99", 99),
        (99, 99),
    ],
)
def test_resolve_enum_governance_domains_aliases(raw_value, expected):
    assert resolve_enum(GovernanceDomains, raw_value) == expected


@pytest.mark.parametrize("raw_value", ["", None, "NOT_A_DOMAIN"])
def test_resolve_enum_governance_domains_invalid_values(raw_value):
    assert resolve_enum(GovernanceDomains, raw_value) is None


@pytest.mark.asyncio
async def test_parser_resolves_domain_identifier_enum_to_integer():
    cmd = DrECommand(
        verb="Create",
        object_type="Governance Zone",
        attributes={
            "Display Name": "Sales Governance Zone",
            "Qualified Name": "GovernanceZone::Sales::1.0",
            "Domain Identifier": "IT_INFRASTRUCTURE",
        },
        raw_block="# Create Governance Zone",
    )

    result = await AttributeFirstParser(cmd, directive="process").parse()

    assert result["attributes"]["Domain Identifier"]["value"] == 4


