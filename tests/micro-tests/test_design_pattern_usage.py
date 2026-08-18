# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Regression test for ISSUE-66: `Create Design Pattern` had no `Usage`
attribute at all -- `usage` is a real `DesignPatternProperties` field
(confirmed in `Egeria-api-solution-architect.http`'s
createDesignPattern/updateDesignPattern worked examples) that the
"Design Pattern Base" compact-spec bundle never declared, so it couldn't
even be set (a `### Usage` block would fail --validate outright, not just
be silently dropped) and `set_solution_architect_body()`'s DesignPattern
branch never built it into the outgoing properties.

No live server needed: set_solution_architect_body is a pure function.
"""
from md_processing.md_processing_utils.common_md_utils import set_solution_architect_body


def test_design_pattern_body_includes_usage():
    attributes = {
        "Usage": {"value": "Use this pattern when X."},
        "Context": {"value": "Some context"},
    }
    body = set_solution_architect_body("DesignPattern", "DesignPattern::test::1", attributes)
    assert body["usage"] == "Use this pattern when X."
    assert body["context"] == "Some context"


def test_design_pattern_body_usage_none_when_unset():
    body = set_solution_architect_body("DesignPattern", "DesignPattern::test::2", {})
    assert body["usage"] is None


def test_non_design_pattern_object_types_unaffected():
    # Usage is DesignPattern-specific here; SolutionBlueprint (which has no
    # such field, per its own real properties class) shouldn't gain one.
    body = set_solution_architect_body("SolutionBlueprint", "SolutionBlueprint::test::1", {})
    assert "usage" not in body
