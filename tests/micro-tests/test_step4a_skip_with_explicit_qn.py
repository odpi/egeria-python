"""
Regression test for ISSUE-107: AsyncBaseCommandProcessor.execute()'s step 4a
("check for duplicate display_name if we are creating a new element") used to
run unconditionally on every Create, calling resolve_element_guid() a second
time (on top of the one fetch_as_is() already issued) even when the command
supplied an explicit, unambiguous Qualified Name. That's wasted cost on the
same expensive ambiguous-name-lookup path the ISSUE-107 report measured at
~1s/candidate server-side, multiplied further whenever many elements share a
Display Name.

The fix: step 4a is now skipped when the markdown explicitly authored a
'Qualified Name' attribute (captured before any auto-derivation can inject
one under the same key) - fetch_as_is() already looked that exact name up,
and finding nothing is authoritative, no auto-derivation collision (ISSUE-59)
is possible.

Uses the real dispatcher/processor pipeline (not the real Egeria client) so
this exercises execute()'s actual step ordering, following the pattern in
test_dispatcher_forward_references.py.
"""
from typing import Any, Dict, Optional

import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.v2.dispatcher import V2Dispatcher
from md_processing.md_processing_utils.md_processing_constants import load_commands


class _FakeClient:
    """No live methods are actually invoked - resolve_element_guid() is
    overridden below to short-circuit before touching self.client."""
    pass


class _CountingProcessor(AsyncBaseCommandProcessor):
    """Minimal Create-command processor that counts resolve_element_guid()
    calls and always reports 'nothing found', so both fetch_as_is() and
    step 4a (when not skipped) take their real code paths without needing a
    live server."""

    async def resolve_element_guid(self, name_or_guid: str, tech_type: Optional[str] = None) -> Optional[str]:
        store = self.context.setdefault("_resolve_calls", [])
        store.append(name_or_guid)
        return None

    async def apply_changes(self) -> str:
        qn = self.parsed_output["qualified_name"]
        self.parsed_output["guid"] = f"guid::{qn}"
        return f"created {qn}"


@pytest.mark.asyncio
async def test_step4a_runs_when_qualified_name_is_derived():
    """No explicit Qualified Name -> step 4a's duplicate-Display-Name check
    still runs (pre-existing ISSUE-59 protection must not regress): expect
    resolve_element_guid() called at least twice (fetch_as_is + step 4a)."""
    load_commands()

    cmd = DrECommand(
        verb="Create",
        object_type="Project",
        attributes={"Display Name": "Step4aTest Derived"},
        raw_block="## Create Project\n### Display Name\nStep4aTest Derived\n",
    )

    dispatcher = V2Dispatcher(_FakeClient())
    dispatcher.register("Create Project", _CountingProcessor)

    context: Dict[str, Any] = {"directive": "process"}
    results = await dispatcher.dispatch_batch([cmd], context)

    assert results[0]["status"] == "success"
    assert len(context["_resolve_calls"]) >= 2


@pytest.mark.asyncio
async def test_step4a_skipped_when_qualified_name_is_explicit():
    """Explicit Qualified Name -> step 4a must be skipped: only fetch_as_is()'s
    single resolve_element_guid() call should happen."""
    load_commands()

    cmd = DrECommand(
        verb="Create",
        object_type="Project",
        attributes={
            "Display Name": "Step4aTest Explicit",
            "Qualified Name": "Step4aTest::Explicit::QN",
        },
        raw_block=(
            "## Create Project\n### Display Name\nStep4aTest Explicit\n"
            "### Qualified Name\nStep4aTest::Explicit::QN\n"
        ),
    )

    dispatcher = V2Dispatcher(_FakeClient())
    dispatcher.register("Create Project", _CountingProcessor)

    context: Dict[str, Any] = {"directive": "process"}
    results = await dispatcher.dispatch_batch([cmd], context)

    assert results[0]["status"] == "success"
    assert context["_resolve_calls"] == ["Step4aTest::Explicit::QN"]
