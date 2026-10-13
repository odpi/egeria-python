# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
ISSUE-144: SemanticAssignmentProperties carries its status in `termAssignmentStatus`
(an enum). Dr.Egeria sent `status`, which Egeria silently ignores.
"""
from typing import Any, cast

import pytest

from md_processing.v2.curation import CurationLinkProcessor, _term_assignment_status
from md_processing.v2.extraction import DrECommand


@pytest.mark.parametrize("value, expected", [
    (3, "VALIDATED"), ("1", "PROPOSED"), (99, "OTHER"), ("Validated", "VALIDATED"),
    ("PROPOSED", "PROPOSED"), (None, None), ("", None), (42, None),
])
def test_term_assignment_status_conversion(value, expected):
    assert _term_assignment_status(value) == expected


async def test_link_semantic_assignment_sends_term_assignment_status():
    bodies = []

    class _ClassificationManager:
        async def _async_setup_semantic_assignment(self, glossary_term_guid, element_guid, body):
            bodies.append(body)

    class _Client:
        classification_manager = _ClassificationManager()

    p = CurationLinkProcessor(client=cast(Any, _Client()),
                              command=DrECommand(verb="Link", object_type="Semantic Assignment", attributes={},
                                                 raw_block="## Link Semantic Assignment"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": "SemanticAssignment"}
    p.parsed_output = {"attributes": {
        "Target Element": {"guid": "eeeeeeee-0000-0000-0000-000000000001"},
        "Glossary Term": {"guid": "tttttttt-0000-0000-0000-000000000002"},
        "Governance Status": {"value": 1},
    }}

    await p.apply_changes()

    props = bodies[0]["properties"]
    assert props["termAssignmentStatus"] == "PROPOSED"
    assert "status" not in props
