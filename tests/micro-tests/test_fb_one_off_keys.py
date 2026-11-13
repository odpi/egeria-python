# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""F-B group 6: one-off attributes go under the key Egeria's class declares, or are reported.

Round-trip probe, PostgreSQL baseline: Implementation Description (9 governance definitions), Headcount (3
roles), Digital Product dates and names, Working Set Disposition, Member Ordinal, Data Field cardinalities /
position / coverage category, ... were dropped -- left out, or sent under a key the class doesn't declare
(withdrawalDate, nextVersion).
"""
from md_processing.md_processing_utils.common_md_utils import (
    complete_bundle_properties, set_actor_manager_prop_body, set_product_body)
from md_processing.md_processing_utils.typed_properties import not_applied_notes


def _attrs(**kv):
    return {k.replace("_", " "): {"value": v} for k, v in kv.items()}


def test_declared_one_offs_are_filled():
    a = _attrs(Implementation_Description="RTP impl", Disposition="RTP disp", Member_Ordinal="7")
    assert complete_bundle_properties({"class": "CertificationTypeProperties"}, a)["implementationDescription"] == "RTP impl"
    assert complete_bundle_properties({"class": "WorkingSetProperties"}, a)["disposition"] == "RTP disp"
    assert complete_bundle_properties({"class": "ReferenceDataValueProperties"}, a)["ordinal"] == "7"
    # GovernancePolicyProperties declares none of them: not filled, and not reported (fill-only map)
    props = complete_bundle_properties({"class": "GovernancePolicyProperties"}, a)
    assert "implementationDescription" not in props


def test_digital_product_keys_are_egerias():
    a = _attrs(Display_Name="RTP P", Product_Name="RTP p", Maturity="m", Service_Life="s",
               Introduction_Date="2020-01-02", Withdrawal_Date="2031-01-02", Next_Version_Date="2031-01-02",
               Current_Version="2")
    props = set_product_body("Digital Product", "RTP::P", a)
    assert props["withdrawDate"] == "2031-01-02" and props["nextVersionDate"] == "2031-01-02"
    assert "withdrawalDate" not in props and "nextVersion" not in props
    assert props["productName"] == "RTP p" and props["maturity"] == "m" and props["serviceLife"] == "s"
    assert "not applied: Current Version: DigitalProductProperties has no currentVersion property" in not_applied_notes(a)


def test_headcount_is_head_count():
    a = _attrs(Display_Name="RTP Role", Headcount="7")
    props = set_actor_manager_prop_body("Governance Role", "RTP::Role", a)
    assert props.get("headCount") in (7, "7") and "headcount" not in props


def test_data_field_one_offs_without_a_field_are_reported():
    a = _attrs(Coverage_Category="RTP", Minimum_Cardinality="1", Maximum_Cardinality="2", Position="3")
    complete_bundle_properties({"class": "DataFieldProperties"}, a)
    notes = not_applied_notes(a)
    for attribute, key in (("Coverage Category", "coverageCategory"), ("Minimum Cardinality", "minCardinality"),
                           ("Maximum Cardinality", "maxCardinality"), ("Position", "position")):
        assert f"not applied: {attribute}: DataFieldProperties has no {key} property" in notes
