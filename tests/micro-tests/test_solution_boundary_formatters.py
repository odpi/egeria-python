# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Solution boundaries (odpi/egeria#9465), the output side: the "Solution-Boundary" report spec, the validate-map and allowlist
entries, and the member hierarchy.

The nested-member shape is the one Egeria's Java defines: a member that is itself a boundary is an item of `collectionMembers` with
`nestedElements` (its own members, same shape, possibly nested again) and `sideLinks` (RelatedMetadataHierarchySummary extends
RelatedMetadataElementSummary, odpi/egeria main 2e22b1e85b). It has NOT been seen on a platform yet, so every element below is
SYNTHETIC, built from that class and the real element header shape, and nothing here is a live claim.
"""
import pytest

from pyegeria import SolutionArchitect
from pyegeria.authoring.validate import client_derived_columns
from pyegeria.omvs.solution_architect import solution_boundary_member_hierarchy as hierarchy
from pyegeria.view.base_report_formats import get_report_registry
from pyegeria.view.microflow import FIND_METHOD_ALLOWLIST


def member(guid, type_name, name, nested=None, side=None):
    """SYNTHETIC RelatedMetadataHierarchySummary: the related element plus nestedElements / sideLinks."""
    item = {"relationshipHeader": {"type": {"typeName": "CollectionMembership"}},
            "relatedElement": {"elementHeader": {"guid": guid, "type": {"typeName": type_name}},
                               "properties": {"displayName": name, "qualifiedName": "q::" + name}}}
    if nested is not None:
        item["nestedElements"] = nested
    if side is not None:
        item["sideLinks"] = side
    return item


def boundary(members, guid="root"):
    return {"elementHeader": {"guid": guid, "status": "ACTIVE", "type": {"typeName": "SolutionBoundary", "typeId": "t"},
                              "origin": {"originCategory": "LOCAL_COHORT", "homeMetadataCollectionId": "mc"},
                              "versions": {"createdBy": "user", "version": 1}},
            "properties": {"class": "SolutionBoundaryProperties", "qualifiedName": "Boundary::Root", "displayName": "Root"},
            "collectionMembers": members, "mermaidGraph": "flowchart LR\n a-->b"}


# ── the report spec and the lists that must name the new find method ──────────────────────────────

def test_the_solution_boundary_spec_is_registered_and_runs_the_boundary_find():
    registry = get_report_registry()
    for label in ("Solution-Boundary", "Solution-Boundary-Mermaid"):
        spec = registry[label]
        assert spec.target_type == "SolutionBoundary" and spec.family == "Solution Architect"
        assert spec.action.function == "SolutionArchitect.find_solution_boundaries"


def test_the_spec_shows_the_member_hierarchy_and_the_blueprint_mermaid_field():
    spec = get_report_registry()["Solution-Boundary"]
    keys = {c.key for f in spec.formats for c in f.attributes}
    assert {"member_hierarchy", "collection_members", "solutionBlueprintMermaidGraph", "mermaidGraph"} <= keys


def test_the_find_method_is_on_the_allowlist_and_its_computed_column_is_declared():
    assert "SolutionArchitect.find_solution_boundaries" in FIND_METHOD_ALLOWLIST
    # strict validation accepts the spec's computed column only because the client declares it
    assert "member_hierarchy" in client_derived_columns("SolutionArchitect.find_solution_boundaries", "SolutionBoundary")


# ── the member hierarchy ─────────────────────────────────────────────────────────────────────────

def test_no_members_no_lines():
    assert hierarchy(boundary([])) == []
    assert hierarchy({}) == []
    assert hierarchy(None) == []


def test_flat_members():
    lines = hierarchy(boundary([member("c1", "SolutionComponent", "Comp A"), member("r1", "SolutionActorRole", "Role A")]))
    assert lines == ["SolutionComponent: Comp A", "SolutionActorRole: Role A"]


def test_a_nested_boundary_shows_its_members_indented_and_a_third_level_too():
    deep = member("b3", "SolutionBoundary", "Inner", nested=[member("c2", "SolutionComponent", "Deep comp")])
    mid = member("b2", "SolutionBoundary", "Middle", nested=[deep, member("r1", "SolutionActorRole", "Role A")])
    lines = hierarchy(boundary([mid, member("c1", "SolutionComponent", "Comp A")]))
    assert lines == ["SolutionBoundary: Middle", "  SolutionBoundary: Inner", "    SolutionComponent: Deep comp",
                     "  SolutionActorRole: Role A", "SolutionComponent: Comp A"]


def test_side_links_are_named_not_followed():
    side = [member("p2", "SolutionBlueprint", "Other blueprint")]
    lines = hierarchy(boundary([member("b2", "SolutionBoundary", "Middle", nested=[], side=side)]))
    assert lines == ["SolutionBoundary: Middle", "  also linked to: SolutionBlueprint: Other blueprint"]


def test_a_cycle_is_not_followed():
    # the nested member is the root itself, and a member that is its own ancestor
    again = member("b2", "SolutionBoundary", "Middle again")
    mid = member("b2", "SolutionBoundary", "Middle", nested=[again, member("root", "SolutionBoundary", "Root again")])
    lines = hierarchy(boundary([mid]))
    assert lines == ["SolutionBoundary: Middle",
                     "  SolutionBoundary: Middle again (already above: not followed again)",
                     "  SolutionBoundary: Root again (already above: not followed again)"]


def test_a_shared_member_under_two_parents_is_listed_under_each_and_is_not_a_cycle():
    shared = lambda: member("c9", "SolutionComponent", "Shared")  # noqa: E731
    lines = hierarchy(boundary([member("b2", "SolutionBoundary", "One", nested=[shared()]),
                                member("b3", "SolutionBoundary", "Two", nested=[shared()])]))
    assert lines == ["SolutionBoundary: One", "  SolutionComponent: Shared", "SolutionBoundary: Two", "  SolutionComponent: Shared"]


def test_the_depth_limit_says_so_instead_of_cutting_silently():
    leaf = member("c1", "SolutionComponent", "Leaf")
    chain = leaf
    for n in range(5):
        chain = member(f"b{n}", "SolutionBoundary", f"Level {n}", nested=[chain])
    lines = hierarchy(boundary([chain]), max_depth=3)
    assert lines[-1].strip().startswith("... deeper members not shown (limit of 3 levels)")
    assert not any("Leaf" in line for line in lines)


def test_the_size_limit_says_so():
    lines = hierarchy(boundary([member(f"c{n}", "SolutionComponent", f"C{n}") for n in range(10)]), max_nodes=4)
    assert len(lines) == 5 and lines[-1].startswith("... more members not shown (limit of 4 lines)")


def test_a_member_without_a_name_or_header_does_not_break_the_walk():
    lines = hierarchy(boundary([{"relatedElement": {}}, {}]))
    assert lines == ["?: (no name)", "?: (no name)"]


# ── the extractor puts the hierarchy in its column ───────────────────────────────────────────────

def test_dict_output_with_the_boundary_spec_carries_the_member_hierarchy(monkeypatch):
    monkeypatch.setattr(SolutionArchitect, "check_connection", lambda self: "test", raising=False)
    client = SolutionArchitect("view-server", "https://localhost:1", "user", "pwd")
    el = boundary([member("b2", "SolutionBoundary", "Middle", nested=[member("c1", "SolutionComponent", "Comp A")])])
    rows = client.generate_solution_boundary_output(el, "root", "SolutionBoundary", "DICT", report_spec="Solution-Boundary")
    assert rows[0]["Display Name"] == "Root"
    assert rows[0]["Member Hierarchy"] == "SolutionBoundary: Middle\n  SolutionComponent: Comp A"


@pytest.mark.parametrize("fmt", ["DICT", "MD", "REPORT", "LIST"])
def test_the_default_spec_of_the_methods_now_resolves_for_every_text_format(monkeypatch, fmt):
    # B2's methods default to report_spec="Solution-Boundary", which did not exist before this change
    monkeypatch.setattr(SolutionArchitect, "check_connection", lambda self: "test", raising=False)
    client = SolutionArchitect("view-server", "https://localhost:1", "user", "pwd")
    out = client.generate_solution_boundary_output(boundary([]), "root", "SolutionBoundary", fmt, report_spec="Solution-Boundary")
    assert out
