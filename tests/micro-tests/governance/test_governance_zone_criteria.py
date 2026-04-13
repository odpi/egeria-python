from md_processing.md_processing_utils.common_md_utils import set_gov_prop_body


def test_set_gov_prop_body_includes_governance_zone_criteria():
    attrs = {
        "Display Name": {"value": "SalesAnalytics Zone"},
        "Summary": {"value": "Zone summary"},
        "Description": {"value": "Zone description"},
        "Domain Identifier": {"value": "DATA"},
        "Criteria": {"value": "Used in production or consumption of Sales Forecast data."},
    }

    body = set_gov_prop_body("Governance Zone", "GovernanceZone::SalesAnalytics::1.0", attrs)

    assert body["class"] == "GovernanceZoneProperties"
    assert body["domainIdentifier"] == 1
    assert body["criteria"] == "Used in production or consumption of Sales Forecast data."


def test_set_gov_prop_body_non_zone_does_not_add_criteria():
    attrs = {
        "Display Name": {"value": "Policy A"},
        "Summary": {"value": "Policy summary"},
        "Description": {"value": "Policy description"},
        "Domain Identifier": {"value": "DATA"},
        "Criteria": {"value": "Should not be used for non-zone types."},
    }

    body = set_gov_prop_body("Governance Policy", "GovernancePolicy::A::1.0", attrs)

    assert "criteria" not in body


def test_set_gov_prop_body_normalizes_domain_identifier_aliases():
    attrs = {
        "Display Name": {"value": "Policy B"},
        "Summary": {"value": "Policy summary"},
        "Description": {"value": "Policy description"},
        "Domain Identifier": {"value": "Software Development"},
    }

    body = set_gov_prop_body("Governance Policy", "GovernancePolicy::B::1.0", attrs)

    assert body["domainIdentifier"] == 5



