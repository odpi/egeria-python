# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Regression test for ISSUE-71 (PYEGERIA_ISSUES.md): `GovernanceActionType` and
`GovernanceActionProcessStep` had no branch in `update_gov_body_for_type`, so
every attribute their compact-spec bundles add on top of the base governance
fields -- Implementation Description, Produced Guards, Wait Time, and (for
Process Step only) Ignore Multiple Triggers -- was silently dropped from the
outgoing body. Processing still reported SUCCESS; the value just never
reached the element.
"""
from md_processing.md_processing_utils.common_md_utils import set_gov_prop_body


def test_governance_action_type_includes_produced_guards_and_wait_time():
    attrs = {
        "Display Name": {"value": "Probe Guards On Action Type"},
        "Domain Identifier": {"value": "DATA"},
        "Implementation Description": {"value": "Runs the outcome probe."},
        "Produced Guards": {"value": ["recovered", "partial", "no_signal", "unverified", "regression"]},
        "Wait Time": {"value": 0},
    }

    body = set_gov_prop_body("GovernanceActionType", "GovActionType::ProbeOutcomeVocab::probe", attrs)

    assert body["class"] == "GovernanceActionTypeProperties"
    assert body["implementationDescription"] == "Runs the outcome probe."
    assert body["producedGuards"] == ["recovered", "partial", "no_signal", "unverified", "regression"]
    assert body["waitTime"] == 0
    # Not a Process Step -- Ignore Multiple Triggers isn't part of this bundle.
    assert "ignoreMultipleTriggers" not in body


def test_governance_action_process_step_includes_ignore_multiple_triggers():
    attrs = {
        "Display Name": {"value": "Probe Guards On Process Step"},
        "Domain Identifier": {"value": "DATA"},
        "Produced Guards": {"value": ["recovered", "partial"]},
        "Wait Time": {"value": 5},
        "Ignore Multiple Triggers": {"value": True},
    }

    body = set_gov_prop_body("GovernanceActionProcessStep", "GovActionProcessStep::ProbeOutcomeVocab::probe", attrs)

    assert body["class"] == "GovernanceActionProcessStepProperties"
    assert body["producedGuards"] == ["recovered", "partial"]
    assert body["waitTime"] == 5
    assert body["ignoreMultipleTriggers"] is True


def test_governance_action_type_defaults_produced_guards_to_empty_list():
    attrs = {
        "Display Name": {"value": "No Guards Declared"},
        "Domain Identifier": {"value": "DATA"},
    }

    body = set_gov_prop_body("GovernanceActionType", "GovActionType::NoGuards::1", attrs)

    assert body["producedGuards"] == []
