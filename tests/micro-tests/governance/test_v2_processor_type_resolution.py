from typing import Any

import pytest

from md_processing.v2 import processors as processors_module

from md_processing.v2.extraction import DrECommand
from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.common_md_utils import set_gov_prop_body
from md_processing.md_processing_utils.md_processing_constants import load_commands, resolve_command_spec


class _NoopProcessor(AsyncBaseCommandProcessor):
    async def apply_changes(self) -> str:
        return ""


class _FakeClient:
    pass


class _FallbackClient:
    def __init__(self):
        self.calls = []

    async def _async_get_guid_for_name(self, name: str, type_name: str = None):
        self.calls.append((name, type_name))
        if type_name:
            raise Exception(
                "OMAG-COMMON-400-018 The type name ThreatDefinition passed on method findMetadataElements of service Open Metadata Store Services is not recognized"
            )
        return "2dd3c85f-cc0b-4f08-8c33-2dfd64958caa"


def test_resolve_command_spec_uses_alias_to_return_canonical_command_name():
    load_commands()
    canonical_name, spec = resolve_command_spec("Create Terms & Conditions")

    assert canonical_name == "Create Terms and Conditions"
    assert isinstance(spec, dict)
    assert spec.get("find_constraints")


def test_processor_derives_egeria_type_from_canonical_spec_not_alias_display_name():
    load_commands()
    cmd = DrECommand(
        verb="Create",
        object_type="Terms & Conditions",
        attributes={"Display Name": "Policy A"},
        raw_block="# Create Terms & Conditions",
    )

    processor = _NoopProcessor(client=_FakeClient(), command=cmd, context={"directive": "validate"})

    assert processor.canonical_command_name == "Create Terms and Conditions"
    assert processor.canonical_object_type == "Terms and Conditions"
    assert processor.egeria_type_name == "TermsAndConditions"


def test_processor_derives_threatdefinition_type_from_threat_definition_alias():
    load_commands()
    cmd = DrECommand(
        verb="Create",
        object_type="Threat Definition",
        attributes={"Display Name": "CRM Data Quality Degradation"},
        raw_block="# Create Threat Definition",
    )

    processor = _NoopProcessor(client=_FakeClient(), command=cmd, context={"directive": "validate"})

    assert processor.canonical_command_name == "Create Threat"
    assert processor.canonical_object_type == "Threat"
    assert processor.egeria_type_name == "Threat"


def test_processor_derives_securitygroup_type_for_create_security_group():
    load_commands()
    cmd = DrECommand(
        verb="Create",
        object_type="Security Group",
        attributes={"Display Name": "Board Forecast Readers"},
        raw_block="# Create Security Group",
    )

    processor = _NoopProcessor(client=_FakeClient(), command=cmd, context={"directive": "validate"})

    assert processor.canonical_command_name == "Create Security Group"
    assert processor.canonical_object_type == "Security Group"
    assert processor.egeria_type_name == "SecurityGroup"


@pytest.mark.asyncio
async def test_resolve_element_guid_warns_and_falls_back_when_typed_lookup_uses_unsupported_type(monkeypatch):
    load_commands()
    cmd = DrECommand(
        verb="Create",
        object_type="Threat Definition",
        attributes={"Display Name": "CRM Data Quality Degradation"},
        raw_block="# Create Threat Definition",
    )
    processor = _NoopProcessor(client=_FallbackClient(), command=cmd, context={"directive": "validate"})
    processor.parsed_output = {"warnings": []}

    # Rebind the imported symbol so the test can raise plain Exception objects.
    monkeypatch.setattr(processors_module, "PyegeriaException", Exception)

    guid = await processor.resolve_element_guid(
        "ThreatDefinition::SalesForecast::CRMDataQualityDegradation::1.0",
        tech_type="ThreatDefinition",
    )

    assert guid == "2dd3c85f-cc0b-4f08-8c33-2dfd64958caa"
    assert len(processor.parsed_output["warnings"]) == 1
    assert "OMAG-COMMON-400-018" in processor.parsed_output["warnings"][0]
    assert "not recognized" in processor.parsed_output["warnings"][0]


def test_extract_guid_or_raise_accepts_dict_payload_guid_key():
    cmd = DrECommand(verb="Create", object_type="Threat", attributes={}, raw_block="# Create Threat")
    processor = _NoopProcessor(client=_FakeClient(), command=cmd, context={"directive": "process"})

    guid = processor.extract_guid_or_raise(
        {"guid": "2dd3c85f-cc0b-4f08-8c33-2dfd64958caa"},
        "Create Threat",
    )

    assert guid == "2dd3c85f-cc0b-4f08-8c33-2dfd64958caa"


def test_extract_guid_or_raise_hard_fails_on_non_guid_value():
    cmd = DrECommand(verb="Create", object_type="Threat", attributes={}, raw_block="# Create Threat")
    processor = _NoopProcessor(client=_FakeClient(), command=cmd, context={"directive": "process"})

    with pytest.raises(ValueError):
        processor.extract_guid_or_raise({"guid": "ThreatDefinition::bad"}, "Create Threat")


def test_extract_guid_or_raise_accepts_nested_guid_payloads():
    cmd = DrECommand(verb="Create", object_type="Threat", attributes={}, raw_block="# Create Threat")
    processor = _NoopProcessor(client=_FakeClient(), command=cmd, context={"directive": "process"})

    guid = processor.extract_guid_or_raise(
        {"class": "GUIDResponse", "relatedHTTPCode": 200, "response": {"elementHeader": {"guid": "2dd3c85f-cc0b-4f08-8c33-2dfd64958caa"}}},
        "Create Threat",
    )

    assert guid == "2dd3c85f-cc0b-4f08-8c33-2dfd64958caa"


def test_set_gov_prop_body_normalizes_terms_and_conditions_type_name():
    props = set_gov_prop_body(
        "Terms and Conditions",
        "TermsAndConditions::SalesForecast::DataSharing::1.0",
        {
            "Display Name": {"value": "Sales Forecast Data Sharing Terms and Conditions"},
            "Summary": {"value": "summary"},
        },
    )

    assert props["class"] == "TermsAndConditionsProperties"
    assert props["typeName"] == "TermsAndConditions"



