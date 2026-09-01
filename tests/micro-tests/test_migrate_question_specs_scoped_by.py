# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Regression test for ISSUE-81 (PYEGERIA_ISSUES.md): `migrate_question_specs.py`'s
`_ensure_scoped_by()` used to call `actor_manager.link_assignment_scope`,
which creates Egeria's `AssignmentScope` relationship -- a different, wrong
relationship ("identifies actors assigned to manage resources", per
https://egeria-project.org/types/1/0120-Assignment-Scopes/) that the
runtime reader (`load_egeria_report_specs`) never looked for, since it
queries specifically for `ScopedBy`. Fixed to call
`classification_manager.add_scope_to_element`, matching the Dr.Egeria
"Link Perspective to Question" command and creating the real `ScopedBy`
relationship.

No live server needed: a fake client captures the outgoing call.
"""
from commands.migrate_question_specs import _ensure_scoped_by

PERSPECTIVE_GUID = "perspective-guid-0001"
QUESTION_GUID = "question-guid-0001"


class _FakeClassificationManager:
    def __init__(self):
        self.add_scope_calls = []

    def add_scope_to_element(self, scoped_by_guid, element_guid, body=None):
        self.add_scope_calls.append((scoped_by_guid, element_guid, body))


class _FakeActorManager:
    """Present so a regression to the old (wrong) call path would be
    caught explicitly rather than raising AttributeError."""

    def __init__(self):
        self.link_assignment_scope_calls = []

    def link_assignment_scope(self, scope_element_guid, actor_guid, body=None):
        self.link_assignment_scope_calls.append((scope_element_guid, actor_guid, body))


class _FakeClient:
    def __init__(self):
        self.classification_manager = _FakeClassificationManager()
        self.actor_manager = _FakeActorManager()

    def get_related_elements(self, guid, relationship_type=None):
        return "No elements found"  # no existing link -- always creates


def test_ensure_scoped_by_creates_real_scopedby_not_assignmentscope():
    client = _FakeClient()

    _ensure_scoped_by(client, PERSPECTIVE_GUID, QUESTION_GUID, dry_run=False)

    assert client.classification_manager.add_scope_calls == [
        (PERSPECTIVE_GUID, QUESTION_GUID, {
            "class": "NewRelationshipRequestBody",
            "properties": {"class": "ScopedByProperties"},
        })
    ]
    # The old, wrong call path must never fire.
    assert client.actor_manager.link_assignment_scope_calls == []


def test_ensure_scoped_by_skips_creation_when_already_linked():
    client = _FakeClient()
    client.get_related_elements = lambda guid, relationship_type=None: [
        {"elementHeader": {"guid": PERSPECTIVE_GUID}}
    ]

    _ensure_scoped_by(client, PERSPECTIVE_GUID, QUESTION_GUID, dry_run=False)

    assert client.classification_manager.add_scope_calls == []


def test_ensure_scoped_by_dry_run_makes_no_calls():
    client = _FakeClient()

    _ensure_scoped_by(client, PERSPECTIVE_GUID, QUESTION_GUID, dry_run=True)

    assert client.classification_manager.add_scope_calls == []
    assert client.actor_manager.link_assignment_scope_calls == []
