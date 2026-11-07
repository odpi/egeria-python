"""
Display-name pre-check (processors.py step 4a) performance fixes:

1. Egeria's OMAG-GENERIC-HANDLERS-404-002 "Multiple ... entities where found"
   answer is classified as ambiguous and cached once per batch (previously only
   the SDK's "Multiple elements found" wording was, so every command repeated
   the ~1s/candidate lookup).
2. Action-style commands (supports_target_element_lookup() False, e.g. Create
   Subscription Type) skip the display-name pre-check entirely.
"""
from typing import Any, Dict, List

import pytest

from pyegeria import NO_ELEMENTS_FOUND
from pyegeria.core._exceptions import PyegeriaException

from md_processing.v2.extraction import DrECommand
from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.v2.dispatcher import V2Dispatcher
from md_processing.md_processing_utils.md_processing_constants import load_commands

_SHARED = "Weekly refresh subscription"
_MSG = ("OMAG-GENERIC-HANDLERS-404-002 Multiple OpenMetadataRoot entities where found "
        "for name Weekly refresh subscription")


class _Client:
    def __init__(self):
        self.calls: List[str] = []

    async def __async_get_guid__(self, qualified_name=None, display_name=None, property_name="qualifiedName",
                                  tech_type=None, **kwargs):
        name = display_name or qualified_name
        if name == _SHARED:
            self.calls.append(name)
            raise PyegeriaException(_MSG)
        return NO_ELEMENTS_FOUND


class _Create(AsyncBaseCommandProcessor):
    async def apply_changes(self) -> str:
        qn = self.parsed_output["qualified_name"]
        self.parsed_output["guid"] = f"guid::{qn}"
        return f"created {qn}"


class _ActionCreate(_Create):
    def supports_target_element_lookup(self) -> bool:
        return False

    async def fetch_as_is(self):
        return None


def _cmds(n):
    return [DrECommand(verb="Create", object_type="Project",
                       attributes={"Display Name": _SHARED},
                       raw_block=f"## Create Project\n### Display Name\n{_SHARED}\n### Description\nd{i}\n")
            for i in range(n)]


async def _run(proc_cls):
    load_commands()
    client = _Client()
    d = V2Dispatcher(client)
    d.register("Create Project", proc_cls)
    results = await d.dispatch_batch(_cmds(4), {"directive": "process"})
    return client, results


@pytest.mark.asyncio
async def test_404_002_ambiguous_is_cached_once_per_batch():
    client, results = await _run(_Create)
    assert all(r["status"] == "success" for r in results)
    # Step 4a probes the shared name; typed pass + untyped pass only for the
    # first command (two distinct queries), cached silently for the rest.
    assert len(client.calls) == 1


@pytest.mark.asyncio
async def test_action_commands_skip_display_name_precheck():
    client, results = await _run(_ActionCreate)
    assert all(r["status"] == "success" for r in results)
    assert client.calls == []
