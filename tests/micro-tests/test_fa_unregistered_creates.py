# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""F-A item 7: the five Create commands that "succeeded" with nothing to read back.

On the round-trip probe Create Data Sharing Request, Subject Area, CSV File, Rating and Like produced
no element. None had run: each summary row read "No processor registered for '<command>'".
- Subject Area is a Collection subtype in Egeria (SubjectAreaProperties extends CollectionProperties):
  now a collection subtype like the rest.
- CSV File: the processor existed as "Create CSV Element"; the spec's name is "Create CSV File".
- Rating / Like are attachments, and Data Sharing Request is a ToDo subtype the spec mis-describes as
  a collection: each now fails with a sentence saying why, and nothing is sent.
"""
from typing import Any, cast

import pytest

from md_processing.dr_egeria import setup_dispatcher
from md_processing.v2.collection_manager_processor import CollectionManagerProcessor, CSVElementProcessor
from md_processing.v2.extraction import DrECommand
from md_processing.v2.not_supported import NOT_SUPPORTED_YET, NotSupportedYetProcessor


@pytest.fixture(scope="module")
def processors():
    registry = setup_dispatcher(cast(Any, object())).processors
    return {k.lower(): v for k, v in registry.items()}


@pytest.mark.parametrize("command, expected", [
    ("Create Subject Area", CollectionManagerProcessor),
    ("Update Subject Area", CollectionManagerProcessor),
    ("Create CSV File", CSVElementProcessor),
    ("Create Rating", NotSupportedYetProcessor),
    ("Create Like", NotSupportedYetProcessor),
    ("Create Data Sharing Request", NotSupportedYetProcessor),
])
def test_every_spec_create_has_a_processor(processors, command, expected):
    assert processors.get(command.lower()) is expected


@pytest.mark.asyncio
@pytest.mark.parametrize("command", sorted(NOT_SUPPORTED_YET))
async def test_not_supported_yet_says_why_and_sends_nothing(command):
    verb, object_type = command.split(" ", 1)
    p = NotSupportedYetProcessor(client=cast(Any, object()),
                                 command=DrECommand(verb=verb, object_type=object_type, attributes={},
                                                    raw_block=f"## {command}"), context={})
    p.parsed_output = {"attributes": {}}
    with pytest.raises(ValueError) as exc:
        await p.apply_changes()
    text = str(exc.value)
    assert text.startswith(f"{command} is not supported yet: ") and text.endswith("Nothing was sent to Egeria.")
    assert NOT_SUPPORTED_YET[command] in text


class _CSVClient:
    def __init__(self):
        self.calls = []

    async def _async_get_create_csv_data_file_element_from_template(self, *args):
        self.calls.append(args)
        return "ffffffff-0000-0000-0000-000000000001"


@pytest.mark.asyncio
async def test_create_csv_file_names_the_file_by_its_display_name():
    client = _CSVClient()
    p = CSVElementProcessor(client=cast(Any, client),
                            command=DrECommand(verb="Create", object_type="CSV File", attributes={},
                                               raw_block="## Create CSV File"), context={})
    p.parsed_output = {"qualified_name": "RTP::CSV", "attributes": {
        "Display Name": {"value": "RTP CreateCsvFile DisplayName"},
        "File Path": {"value": "/data/rtp.csv"}, "File Extension": {"value": "csv"}}}
    out = await p.apply_changes()
    args = client.calls[0]
    assert args[0] == "RTP CreateCsvFile DisplayName" and args[1] == "CSV Data File" and args[2] == "/data/rtp.csv"
    assert "## Created CSV File" in out and p.parsed_output["guid"] == "ffffffff-0000-0000-0000-000000000001"
