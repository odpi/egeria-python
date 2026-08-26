"""
Tests for the two-pass batch mechanism in V2Dispatcher/AsyncBaseCommandProcessor
that lets a command reference (by display name) an element defined LATER in
the same Dr.Egeria file (a forward reference) - see BACKLOG.md, "Forward
references to elements later in the same Dr.Egeria file don't actually
resolve".

These use a minimal fake processor registered directly with a fresh
V2Dispatcher (not the real ProjectProcessor) so the test is scoped to the
dispatch/resolution mechanism itself, not any one family's business logic -
that end-to-end proof is done separately against a live server. The real
"Create Project" compact spec is still used (via load_commands()) so
Sub-Projects resolves as a genuine "Reference Name List" attribute exactly
as it would in production.
"""
from typing import Any, Dict

import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.v2.dispatcher import V2Dispatcher
from md_processing.v2.project import ProjectProcessor, ProjectLinkProcessor
from md_processing.md_processing_utils.md_processing_constants import load_commands


class _FakeClient:
    """No live methods needed - resolve_element_guid() gracefully returns None
    for anything it can't resolve via cache/planned_elements/batch_target_qns,
    swallowing the resulting AttributeError from a missing client method."""
    pass


class _FakeParentChildProcessor(AsyncBaseCommandProcessor):
    """
    Minimal stand-in for a Create-command processor with an embedded
    'Sub-Projects'-style relationship attribute. Exercises the real
    execute()/resolve_element_guid()/Step-7 deferral pipeline through the
    real dispatcher, but replaces the actual Egeria API calls with simple
    in-memory bookkeeping (via the shared batch context) so this test has no
    live-server dependency.
    """

    async def apply_changes(self) -> str:
        qn = self.parsed_output["qualified_name"]
        guid = f"guid::{qn}"
        self.parsed_output["guid"] = guid
        store = self.context.setdefault("_store", {"applied_count": {}, "links": {}})
        store["applied_count"][qn] = store["applied_count"].get(qn, 0) + 1
        children = self.parsed_output["attributes"].get("Sub-Projects", {}).get("guid_list", [])
        if children:
            store["links"].setdefault(qn, set()).update(children)
        return f"created {qn}"


@pytest.mark.asyncio
async def test_forward_reference_parent_before_child_resolves_across_rounds():
    load_commands()

    parent_cmd = DrECommand(
        verb="Create",
        object_type="Project",
        attributes={
            "Display Name": "TwoPassTest Parent",
            "Sub-Projects": "TwoPassTest Child",
        },
        raw_block="## Create Project\n### Display Name\nTwoPassTest Parent\n### Sub-Projects\nTwoPassTest Child\n",
    )
    child_cmd = DrECommand(
        verb="Create",
        object_type="Project",
        attributes={"Display Name": "TwoPassTest Child"},
        raw_block="## Create Project\n### Display Name\nTwoPassTest Child\n",
    )

    dispatcher = V2Dispatcher(_FakeClient())
    dispatcher.register("Create Project", _FakeParentChildProcessor)

    context: Dict[str, Any] = {"directive": "process"}
    results = await dispatcher.dispatch_batch([parent_cmd, child_cmd], context)

    # Positional alignment: results must stay in original command order
    # regardless of which round each command actually completed in.
    assert len(results) == 2
    assert results[0]["status"] == "success"
    assert results[1]["status"] == "success"
    assert not results[0].get("deferred")
    assert not results[1].get("deferred")

    # The pre-scan recognized both display names as legitimate batch targets.
    assert "TwoPassTest Parent" in context["batch_target_qns"]
    assert "TwoPassTest Child" in context["batch_target_qns"]

    parent_qn = results[0]["qualified_name"]
    child_qn = results[1]["qualified_name"]
    store = context["_store"]

    # Child only ever needs one attempt - it has no forward reference.
    assert store["applied_count"][child_qn] == 1
    # Parent had to run at least twice: once in round 1 (creating itself
    # immediately despite the unresolved child - embedded-flavor commands
    # never wait on their own creation), then again once the child existed,
    # to actually complete the Sub-Projects link.
    assert store["applied_count"][parent_qn] >= 2
    assert store["links"][parent_qn] == {f"guid::{child_qn}"}


@pytest.mark.asyncio
async def test_forward_reference_by_explicit_qualified_name_resolves():
    """
    Regression test: prescan_batch_target_qns() must register a command's
    *explicit* user-supplied "Qualified Name" (when present), not just its
    auto-derived one - derive_qualified_name() has no knowledge of an
    explicit override and always auto-generates from Display Name, so
    calling it unconditionally (as the pre-scan previously did) silently
    registered the wrong name for any command using an explicit Qualified
    Name. This made a forward reference *by that explicit name* invisible
    to the pre-scan, even though the exact same file structure worked fine
    when the reference used the referenced element's Display Name instead.

    Found live 2026-08-03 in a real user file (jules-90-day-plan.md) where
    every project used an explicit, human-designed Qualified Name (e.g.
    "JulesKeeper::Project::First30DaysLearningPhase") and a parent Campaign
    referenced its Sub-Projects by those exact qualified names.
    """
    load_commands()

    parent_cmd = DrECommand(
        verb="Create",
        object_type="Project",
        attributes={
            "Display Name": "TwoPassTest QN Parent",
            "Sub-Projects": "TwoPassTest::QN::Child",
        },
        raw_block="## Create Project\n### Display Name\nTwoPassTest QN Parent\n### Sub-Projects\nTwoPassTest::QN::Child\n",
    )
    child_cmd = DrECommand(
        verb="Create",
        object_type="Project",
        attributes={
            "Display Name": "TwoPassTest QN Child",
            "Qualified Name": "TwoPassTest::QN::Child",
        },
        raw_block="## Create Project\n### Display Name\nTwoPassTest QN Child\n### Qualified Name\nTwoPassTest::QN::Child\n",
    )

    dispatcher = V2Dispatcher(_FakeClient())
    dispatcher.register("Create Project", _FakeParentChildProcessor)

    context: Dict[str, Any] = {"directive": "process"}
    results = await dispatcher.dispatch_batch([parent_cmd, child_cmd], context)

    assert len(results) == 2
    assert results[0]["status"] == "success"
    assert results[1]["status"] == "success"

    # The pre-scan must recognize the child's *explicit* qualified name, not
    # just whatever name it would have auto-derived from Display Name.
    assert "TwoPassTest::QN::Child" in context["batch_target_qns"]

    parent_qn = results[0]["qualified_name"]
    child_qn = results[1]["qualified_name"]
    assert child_qn == "TwoPassTest::QN::Child"
    store = context["_store"]
    assert store["links"][parent_qn] == {f"guid::{child_qn}"}


@pytest.mark.asyncio
async def test_genuinely_unresolvable_reference_still_fails_clearly_not_forever_deferred():
    load_commands()

    parent_cmd = DrECommand(
        verb="Create",
        object_type="Project",
        attributes={
            "Display Name": "TwoPassTest Orphan Parent",
            "Sub-Projects": "Some Project That Never Exists Anywhere",
        },
        raw_block="## Create Project\n### Display Name\nTwoPassTest Orphan Parent\n### Sub-Projects\nSome Project That Never Exists Anywhere\n",
    )

    dispatcher = V2Dispatcher(_FakeClient())
    dispatcher.register("Create Project", _FakeParentChildProcessor)

    context: Dict[str, Any] = {"directive": "process"}
    results = await dispatcher.dispatch_batch([parent_cmd], context)

    assert len(results) == 1
    # A name that isn't a legitimate target anywhere in the batch must not be
    # deferred at all (there is nothing to wait for) - today's exact
    # existing hard-fail behavior, unchanged.
    assert results[0]["status"] == "failure"
    assert not results[0].get("deferred")
    assert "Some Project That Never Exists Anywhere" in results[0]["message"]


def test_structural_discriminator_qualified_name_presence():
    """
    The mechanism distinguishes "embedded" commands (create their own element,
    e.g. Create Project) from "standalone" commands (the entire command IS a
    relationship, e.g. Link Project Hierarchy) by whether derive_qualified_name()
    returns a non-empty string - self-verifying, not a hand-maintained list.
    """
    load_commands()

    embedded_cmd = DrECommand(
        verb="Create",
        object_type="Project",
        attributes={"Display Name": "Discriminator Test Project"},
        raw_block="## Create Project\n### Display Name\nDiscriminator Test Project\n",
    )
    embedded_processor = ProjectProcessor(_FakeClient(), embedded_cmd, {})
    raw_shim = {k: {"value": v} for k, v in embedded_cmd.attributes.items()}
    assert embedded_processor.derive_qualified_name(raw_shim) != ""

    standalone_cmd = DrECommand(
        verb="Link",
        object_type="Project Hierarchy",
        attributes={
            "Parent Project": "Discriminator Test Project",
            "Child Project": "Discriminator Test Child",
        },
        raw_block="## Link Project Hierarchy\n### Parent Project\nDiscriminator Test Project\n### Child Project\nDiscriminator Test Child\n",
    )
    standalone_processor = ProjectLinkProcessor(_FakeClient(), standalone_cmd, {})
    raw_shim = {k: {"value": v} for k, v in standalone_cmd.attributes.items()}
    assert standalone_processor.derive_qualified_name(raw_shim) == ""
