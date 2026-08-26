# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Regression test for ISSUE-77 (PYEGERIA_ISSUES.md): "Make Anchor"/"Anchor
Scope IDs" live on the "Link Command Base" bundle (relationship-establishing
commands) but set_rel_request_body() never included them in the outer
NewRelationshipRequestBody -- confirmed against Egeria-api-lineage-linker.http.
"""
from md_processing.md_processing_utils.common_md_utils import set_rel_request_body


def test_make_anchor_and_anchor_scope_ids_included_when_present():
    attributes = {
        "Make Anchor": {"value": True},
        "Anchor Scope IDs": {"guid_list": ["guid-1", "guid-2"]},
    }
    body = set_rel_request_body("SomeRelationship", attributes)

    assert body["makeAnchor"] is True
    assert body["anchorScopeGUIDs"] == ["guid-1", "guid-2"]


def test_make_anchor_and_anchor_scope_ids_absent_when_not_provided():
    body = set_rel_request_body("SomeRelationship", {})

    assert body["makeAnchor"] is None
    assert body["anchorScopeGUIDs"] is None
