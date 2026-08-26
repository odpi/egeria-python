# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Regression tests for ISSUE-77 (PYEGERIA_ISSUES.md): several classification
attributes on the shared "Referenceable" bundle (inherited by nearly every
Create command) were parsed and validated but never actually applied --
confirmed dead by scripts/dr_egeria_audit.py's DEAD_ATTRIBUTE check.

- Security Tags / Policy Management Point are genuinely generic (their real
  Egeria endpoints work on any Referenceable) -- wired into
  AsyncBaseCommandProcessor._sync_referenceable_classifications, called for
  every Create/Update command.
- Class Word / Modifier / Prime Word are GlossaryTerm-only (their real
  endpoints are `/glossaries/terms/{term_guid}/...`) -- removed from the
  generic bundle, added only to the term-specific bundle, and wired into
  AsyncBaseCommandProcessor._sync_term_naming_classifications, called only
  from TermProcessor/QuestionProcessor (md_processing.v2.glossary) where the
  guid is known to be a real term.

No live server needed: a fake client stands in for the OMVS layer.
"""
from typing import Any, cast

import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.processors import AsyncBaseCommandProcessor


class _NoopProcessor(AsyncBaseCommandProcessor):
    """Minimal concrete subclass -- only apply_changes() is abstract, and
    these tests exercise the sync methods directly, not apply_changes()."""

    async def apply_changes(self) -> str:
        return self.command.raw_block


class _FakeClassificationManager:
    def __init__(self):
        self.set_calls = []
        self.clear_calls = []

    async def _async_set_security_tags_classification(self, guid, body):
        self.set_calls.append((guid, body))

    async def _async_clear_security_tags_classification(self, guid):
        self.clear_calls.append(guid)


class _FakeGovernanceOfficer:
    def __init__(self):
        self.set_calls = []
        self.clear_calls = []

    async def _async_set_policy_management_point(self, guid, body):
        self.set_calls.append((guid, body))

    async def _async_clear_policy_management_point(self, guid):
        self.clear_calls.append(guid)


class _FakeGlossaryManager:
    def __init__(self):
        self.set_calls = {}
        self.clear_calls = {}

    async def _async_set_is_class_word(self, guid, body):
        self.set_calls.setdefault("ClassWord", []).append((guid, body))

    async def _async_clear_is_class_word(self, guid):
        self.clear_calls.setdefault("ClassWord", []).append(guid)

    async def _async_set_is_modifier(self, guid, body):
        self.set_calls.setdefault("Modifier", []).append((guid, body))

    async def _async_clear_is_modifier(self, guid):
        self.clear_calls.setdefault("Modifier", []).append(guid)

    async def _async_set_is_prime_word(self, guid, body):
        self.set_calls.setdefault("PrimeWord", []).append((guid, body))

    async def _async_clear_is_prime_word(self, guid):
        self.clear_calls.setdefault("PrimeWord", []).append(guid)


class _FakeClient:
    def __init__(self):
        self.classification_manager = _FakeClassificationManager()
        self.governance_officer = _FakeGovernanceOfficer()
        self.glossary_manager = _FakeGlossaryManager()


def _processor(client) -> _NoopProcessor:
    command = DrECommand(verb="Create", object_type="Governance Action Process", attributes={},
                          raw_block="# Create Governance Action Process")
    return _NoopProcessor(client=cast(Any, client), command=command, context={})


@pytest.mark.asyncio
async def test_security_tags_set_when_present():
    client = _FakeClient()
    p = _processor(client)

    await p._sync_referenceable_classifications("elem-guid", {"Security Tags": {"value": ["Label1", "Label2"]}})

    assert len(client.classification_manager.set_calls) == 1
    guid, body = client.classification_manager.set_calls[0]
    assert guid == "elem-guid"
    assert body["properties"]["securityLabels"] == ["Label1", "Label2"]


@pytest.mark.asyncio
async def test_security_tags_cleared_when_falsy():
    client = _FakeClient()
    p = _processor(client)

    await p._sync_referenceable_classifications("elem-guid", {"Security Tags": {"value": []}})

    assert client.classification_manager.clear_calls == ["elem-guid"]
    assert client.classification_manager.set_calls == []


@pytest.mark.asyncio
async def test_security_tags_untouched_when_absent():
    client = _FakeClient()
    p = _processor(client)

    await p._sync_referenceable_classifications("elem-guid", {})

    assert client.classification_manager.set_calls == []
    assert client.classification_manager.clear_calls == []


@pytest.mark.asyncio
async def test_policy_management_point_set_with_dict_value():
    client = _FakeClient()
    p = _processor(client)

    await p._sync_referenceable_classifications("elem-guid", {
        "Policy Management Point": {"value": {"point_type": "PolicyAdministrationPoint",
                                               "name": "PMP-1", "description": "test"}}
    })

    assert len(client.governance_officer.set_calls) == 1
    guid, body = client.governance_officer.set_calls[0]
    assert guid == "elem-guid"
    props = body["properties"]
    assert props["pointType"] == "PolicyAdministrationPoint"
    assert props["label"] == "PMP-1"
    assert props["description"] == "test"


@pytest.mark.asyncio
async def test_class_word_modifier_prime_word_set_when_true():
    client = _FakeClient()
    p = _processor(client)

    await p._sync_term_naming_classifications("term-guid", {
        "Class Word Classification": {"value": True},
        "Modifier Classification": {"value": True},
        "Prime Word Classification": {"value": True},
    })

    assert client.glossary_manager.set_calls["ClassWord"] == [("term-guid", {
        "class": "NewClassificationRequestBody", "properties": {"class": "ClassWordProperties"}})]
    assert "Modifier" in client.glossary_manager.set_calls
    assert "PrimeWord" in client.glossary_manager.set_calls


@pytest.mark.asyncio
async def test_class_word_cleared_when_false():
    client = _FakeClient()
    p = _processor(client)

    await p._sync_term_naming_classifications("term-guid", {"Class Word Classification": {"value": False}})

    assert client.glossary_manager.clear_calls["ClassWord"] == ["term-guid"]
    assert "ClassWord" not in client.glossary_manager.set_calls
