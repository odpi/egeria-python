"""PY-48: Dr.Egeria must not report success for a block that wrote nothing.

A block written one heading level off

    # Update Data Class
    ## Qualified Name
    DataClass::EmailAddress
    ## Display Name
    Email Address

ran as: no command at the H1 (a title), and the H2 attribute "Display Name" taken as a command of its own, "Display
Name", for which no processor exists. The run said commands_succeeded 1, no errors, and wrote nothing (the element
stayed at version 1); the only trace was a "warning" row. Three things are now failures, with words:

- a command no processor handles;
- a Create/Update that applied nothing (the processor handed back the block it was given);
- a Create/Update that came back with no GUID (None or empty), so nothing it did can be confirmed.

No Egeria: the processors are fakes registered with the real dispatcher.
"""
from typing import Any

import pytest

from md_processing.dr_egeria import setup_dispatcher
from md_processing.md_processing_utils.md_processing_constants import load_commands
from md_processing.v2.dispatcher import V2Dispatcher
from md_processing.v2.extraction import DrECommand, UniversalExtractor
from md_processing.v2.processors import AsyncBaseCommandProcessor
from pyegeria.authoring.runner import async_run_markdown

pytestmark = pytest.mark.unit


class _FakeClient:
    async def __async_get_guid__(self, *args, **kwargs):
        return "No elements found"


class _Writes(AsyncBaseCommandProcessor):
    """Creates an element and says so: the control."""

    async def apply_changes(self) -> str:
        self.parsed_output["guid"] = "guid-1"
        return "created"


class _NoGuid(AsyncBaseCommandProcessor):
    async def apply_changes(self) -> str:
        return "created"


class _EmptyGuid(AsyncBaseCommandProcessor):
    async def apply_changes(self) -> str:
        self.parsed_output["guid"] = ""
        return "created"


class _NothingApplied(AsyncBaseCommandProcessor):
    async def apply_changes(self) -> str:
        self.parsed_output["guid"] = "guid-1"
        return self.command.raw_block  # what a processor hands back when it did nothing


def _command(verb="Create", obj="Project"):
    return DrECommand(verb=verb, object_type=obj, attributes={"Display Name": "PY48Test::Widget"},
                      raw_block=f"## {verb} {obj}\n### Display Name\nPY48Test::Widget\n")


async def _run(processor_cls, verb="Create", directive="process"):
    load_commands()
    dispatcher = V2Dispatcher(_FakeClient())
    dispatcher.register(f"{verb} Project", processor_cls)
    return await dispatcher.dispatch(_command(verb), {"directive": directive, "request_id": "t", "input_file": "t"})


@pytest.mark.asyncio
async def test_a_processor_that_writes_and_names_the_element_is_still_a_success():
    result = await _run(_Writes)
    assert result["status"] == "success" and result["guid"] == "guid-1"


@pytest.mark.asyncio
async def test_a_command_no_processor_handles_is_a_failure_with_words():
    dispatcher = setup_dispatcher(_FakeClient())
    result = await dispatcher.dispatch(DrECommand(verb="Display", object_type="Name", attributes={},
                                                  raw_block="## Display Name\nEmail Address\n"), {})
    assert result["status"] == "failure"
    assert "No processor registered for 'Display Name'" in result["message"]
    assert result["errors"] and "nothing was run" in result["errors"][0].lower()


@pytest.mark.asyncio
@pytest.mark.parametrize("processor_cls", [_NoGuid, _EmptyGuid])
@pytest.mark.parametrize("verb", ["Create", "Update"])
async def test_a_create_or_update_that_returns_no_guid_is_a_failure(processor_cls, verb):
    result = await _run(processor_cls, verb)
    assert result["status"] == "failure", result
    assert "no GUID" in result["message"]
    assert result["errors"]


@pytest.mark.asyncio
@pytest.mark.parametrize("verb", ["Create", "Update"])
async def test_a_create_or_update_that_applied_nothing_is_a_failure(verb):
    result = await _run(_NothingApplied, verb)
    assert result["status"] == "failure", result
    assert "applied nothing" in result["message"]


@pytest.mark.asyncio
async def test_validate_does_not_need_a_guid():
    result = await _run(_NoGuid, directive="validate")
    assert result["status"] == "success"


@pytest.mark.asyncio
async def test_the_misleveled_block_is_a_failed_run_with_a_hint_about_the_heading_level():
    markdown = ("# Update Data Class\n## Qualified Name\nDataClass::EmailAddress\n## Display Name\nEmail Address\n"
                "## Content Status\nACTIVE\n")
    out = await async_run_markdown(_FakeClient(), markdown, "process")
    assert out["success"] is False
    assert out["commands_failed"] >= 1 and out["commands_succeeded"] == 0
    assert out["execution_errors"]
    hints = " ".join(out.get("hints") or [])
    assert "'# Update Data Class' is an H1 heading" in hints
    assert "'## Update Data Class'" in hints


def test_an_update_heading_at_h1_is_diagnosed_though_the_spec_is_named_create():
    attrs = {"Create Data Class": ["Qualified Name", "Display Name"]}
    hints = UniversalExtractor("# Update Data Class\n## Qualified Name\nx\n").diagnose(attrs)
    assert any("'# Update Data Class' is an H1 heading" in h for h in hints), hints


def test_a_well_formed_update_data_class_reaches_the_data_class_processor():
    commands = UniversalExtractor("## Update Data Class\n### Qualified Name\nDataClass::EmailAddress\n"
                                  "### Display Name\nEmail Address\n").extract_commands()
    dispatcher: Any = setup_dispatcher(_FakeClient())
    assert [type(c).__name__ for c in commands] == ["DrECommand"]
    assert dispatcher.resolve_processor_class(commands[0]).__name__ == "DataClassProcessor"


@pytest.mark.asyncio
async def test_a_document_that_runs_no_command_is_not_a_success():
    out = await async_run_markdown(_FakeClient(), "Some notes.\n\nMore notes.\n", "process")
    assert out["success"] is False and out["commands_total"] == 0 and out["hints"]


@pytest.mark.asyncio
async def test_a_classification_update_names_the_element_it_wrote_on():
    from md_processing.v2.curation import CurationClassifyProcessor

    calls = []

    class _Methods:
        def __getattr__(self, name):
            async def method(guid, body):
                calls.append((name, guid))
            return method

    class _Client:
        def __getattr__(self, name):
            return _Methods()

    load_commands()
    cmd = DrECommand(verb="Update", object_type="Data Scope", attributes={},
                     raw_block="## Update Data Scope\n### Target Element\nx\n")
    p = CurationClassifyProcessor(_Client(), cmd, {})
    p.parsed_output = {"attributes": {"Target Element": {"guid": "target-guid"}}}
    await p.apply_changes()
    assert p.parsed_output["guid"] == "target-guid" and calls
