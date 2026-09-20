"""
Regression test for ISSUE-107's second fix: resolve_element_guid()'s "not
found" / "ambiguous" outcomes are now cached per (name, effective_type) in
the batch-shared context, so repeated commands naming the same (possibly
ambiguous) name - e.g. many Creates sharing a Display Name, the exact
scenario the original report measured - don't each independently re-pay the
same expensive server-side lookup.

A genuine single-match "found" result is deliberately NOT cached (see the
comment in resolve_element_guid itself): it's already the cheap path
server-side, and caching it risks going stale within a batch if a later
sibling creates an element sharing that exact name.

Uses the real dispatcher/processor pipeline with a fake client whose
__async_get_guid__ counts calls and can be scripted to return "not found"
or raise the SDK's own ambiguous-match exception, following the pattern in
test_dispatcher_forward_references.py.
"""
from typing import Any, Dict, List, Optional

import pytest

from pyegeria import NO_ELEMENTS_FOUND
from pyegeria.core._exceptions import PyegeriaException

from md_processing.v2.extraction import DrECommand
from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.v2.dispatcher import V2Dispatcher
from md_processing.md_processing_utils.md_processing_constants import load_commands


_PROBE_NAME = "Prime Words"


class _AmbiguousNameClient:
    """__async_get_guid__ reports the shared probe name as ambiguous (mirrors
    the real SDK's behavior for a name shared by multiple elements), and
    reports 'not found' for anything else (e.g. each sibling's own unique
    derived Qualified Name, which fetch_as_is() looks up first) so execution
    reaches each sibling's apply_changes(). Counts every call it receives."""

    def __init__(self):
        self.calls: List[str] = []

    async def __async_get_guid__(self, qualified_name=None, display_name=None, property_name="qualifiedName",
                                  tech_type=None, **kwargs):
        name = display_name or qualified_name
        if name == _PROBE_NAME:
            self.calls.append(name)
            raise PyegeriaException(f"Multiple elements found for name '{name}'")
        return NO_ELEMENTS_FOUND


class _NotFoundNameClient:
    """__async_get_guid__ reports 'not found' for everything, but only
    counts calls for the shared probe name."""

    def __init__(self):
        self.calls: List[str] = []

    async def __async_get_guid__(self, qualified_name=None, display_name=None, property_name="qualifiedName",
                                  tech_type=None, **kwargs):
        name = display_name or qualified_name
        if name == _PROBE_NAME:
            self.calls.append(name)
        return NO_ELEMENTS_FOUND


class _SiblingCreateProcessor(AsyncBaseCommandProcessor):
    """Create-command processor whose apply_changes() directly probes
    resolve_element_guid() for a shared, ambiguous/not-found name -- standing
    in for step 4a's own duplicate-Display-Name lookup, isolated from the
    rest of execute() so the test is scoped to the cache itself."""

    async def apply_changes(self) -> str:
        await self.resolve_element_guid(_PROBE_NAME, tech_type=self.egeria_type_name)
        qn = self.parsed_output["qualified_name"]
        self.parsed_output["guid"] = f"guid::{qn}"
        return f"created {qn}"


def _make_commands(n: int) -> List[DrECommand]:
    return [
        DrECommand(
            verb="Create",
            object_type="Project",
            attributes={"Display Name": f"Sibling {i}"},
            raw_block=f"## Create Project\n### Display Name\nSibling {i}\n",
        )
        for i in range(n)
    ]


@pytest.mark.asyncio
async def test_ambiguous_lookup_cached_across_sibling_commands():
    load_commands()
    client = _AmbiguousNameClient()
    dispatcher = V2Dispatcher(client)
    dispatcher.register("Create Project", _SiblingCreateProcessor)

    context: Dict[str, Any] = {"directive": "process"}
    results = await dispatcher.dispatch_batch(_make_commands(5), context)

    assert all(r["status"] == "success" for r in results)
    # All 5 siblings probed the same ambiguous name; only the first should
    # have actually reached the client -- the rest hit the cached outcome.
    assert client.calls == [_PROBE_NAME]


@pytest.mark.asyncio
async def test_not_found_lookup_cached_across_sibling_commands():
    load_commands()
    client = _NotFoundNameClient()
    dispatcher = V2Dispatcher(client)
    dispatcher.register("Create Project", _SiblingCreateProcessor)

    context: Dict[str, Any] = {"directive": "process"}
    results = await dispatcher.dispatch_batch(_make_commands(5), context)

    assert all(r["status"] == "success" for r in results)
    # Only the first sibling should reach the client at all, and it pays for
    # both of resolve_element_guid's internal passes (Pass 1 WITH the type
    # constraint, Pass 2 WITHOUT -- two genuinely different queries, each
    # cached under its own key). Siblings 2-5 hit both caches and make zero
    # calls: 2 total for 5 siblings, not 10.
    assert client.calls == [_PROBE_NAME, _PROBE_NAME]
