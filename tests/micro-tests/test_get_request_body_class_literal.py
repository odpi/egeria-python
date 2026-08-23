# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Regression test for ISSUE-298 (PYEGERIA_ISSUES.md; filed by the
egeria-workspaces session, github.com/odpi/egeria-python/issues/298):
`GetRequestBody`/`ResultsRequestBody`'s `class` field was a hardcoded
`Literal[...]` matching only the base model's own name, so any dict body
with a real Egeria polymorphism subclass tag -- including tags this SDK's
own docstrings tell callers to use, e.g. `SolutionArchitect.
get_solution_component_by_guid`'s "AnyTimeRequestBody" and `ProjectManager.
get_linked_projects`'s "RelationshipRequestBody" -- was rejected by
`_async_get_guid_request`'s dict-validation branch before the request ever
reached the server.

No live server needed: exercises the Pydantic model directly.
"""
from pydantic import TypeAdapter

from pyegeria.models.models import GetRequestBody, ResultsRequestBody


def test_get_request_body_accepts_any_time_request_body_tag():
    body = TypeAdapter(GetRequestBody).validate_python(
        {"class": "AnyTimeRequestBody", "graphQueryDepth": 10, "maxMermaidNodeCount": 250}
    )
    dumped = body.model_dump(by_alias=True, exclude_none=True)
    assert dumped["class"] == "AnyTimeRequestBody"
    assert dumped["graphQueryDepth"] == 10
    assert dumped["maxMermaidNodeCount"] == 250


def test_get_request_body_accepts_relationship_request_body_tag():
    body = TypeAdapter(GetRequestBody).validate_python({"class": "RelationshipRequestBody"})
    assert body.model_dump(by_alias=True, exclude_none=True)["class"] == "RelationshipRequestBody"


def test_get_request_body_still_requires_class_field():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        TypeAdapter(GetRequestBody).validate_python({"graphQueryDepth": 10})


def test_results_request_body_accepts_non_literal_tag_and_own_fields():
    body = TypeAdapter(ResultsRequestBody).validate_python(
        {"class": "AnyTimeRequestBody", "pageSize": 25, "startFrom": 5}
    )
    dumped = body.model_dump(by_alias=True, exclude_none=True)
    assert dumped["class"] == "AnyTimeRequestBody"
    assert dumped["pageSize"] == 25
    assert dumped["startFrom"] == 5
