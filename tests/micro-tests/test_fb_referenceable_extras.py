# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""F-B group 3: Classifications, Translation Details, User Defined Status, Supplementary Properties.

No processor applied these Referenceable-bundle attributes (88 rows each on the round-trip probe's
PostgreSQL baseline). Classifications and Translation Details now go to their Egeria homes; the other two
have none that Dr.Egeria can use yet, and say so.
"""
from typing import Any, cast

import pytest

from md_processing.md_processing_utils.typed_properties import not_applied_notes
from md_processing.v2.extraction import DrECommand
from md_processing.v2.processors import AsyncBaseCommandProcessor

GUID = "df9b80b5-5979-4ffa-9749-34c782fd11a2"


class _Recorder:
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        async def call(*args, **kwargs):
            self.calls.append((name, args))
            return None
        return call


class _Client:
    def __init__(self):
        self.metadata_expert = _Recorder()
        self.classification_manager = _Recorder()


class _P(AsyncBaseCommandProcessor):
    async def apply_changes(self):
        return ""


def _run_processor():
    client = _Client()
    p = _P(client=cast(Any, client), command=DrECommand(verb="Create", object_type="Glossary", attributes={},
                                                        raw_block="## Create Glossary"), context={})
    p.parsed_output = {"attributes": {}}
    return p, client


@pytest.mark.asyncio
async def test_classifications_are_typed_and_classified():
    p, client = _run_processor()
    attributes = {"Classifications": {"value": "- Taxonomy\n- NotAClassification"}}
    await p._sync_referenceable_extras(GUID, attributes)
    assert client.metadata_expert.calls == [
        ("_async_classify_metadata_element",
         (GUID, "Taxonomy", {"class": "NewClassificationRequestBody", "properties": {"class": "TaxonomyProperties"}}))]
    assert "not applied: Classifications: NotAClassification isn't an Egeria classification" in p.parsed_output["warnings"]


@pytest.mark.asyncio
async def test_translation_details_go_to_the_multi_language_service():
    p, client = _run_processor()
    attributes = {"Translation Details": {"value": "language: French\nlocale: fr-FR\nrtpKey: x"}}
    await p._sync_referenceable_extras(GUID, attributes)
    assert client.classification_manager.calls == [
        ("_async_set_translation", (GUID, {"class": "NewElementRequestBody", "properties": {
            "class": "TranslationDetailProperties", "language": "French", "locale": "fr-FR"}}))]
    assert not_applied_notes(attributes) == ["not applied: Translation Details: rtpKey isn't a property of "
                                             "TranslationDetail"]


@pytest.mark.asyncio
async def test_the_probes_arbitrary_translation_isnt_sent():
    p, client = _run_processor()
    await p._sync_referenceable_extras(GUID, {"Translation Details": {"value": "rtpKey: RTP x"}})
    assert client.classification_manager.calls == []


@pytest.mark.asyncio
async def test_user_defined_status_and_supplementary_properties_are_reported():
    p, client = _run_processor()
    attributes = {"User Defined Status": {"value": "custom"}, "Supplementary Properties": {"value": "summary: s"}}
    await p._sync_referenceable_extras(GUID, attributes)
    notes = not_applied_notes(attributes)
    assert notes[0].startswith("not applied: User Defined Status: no Egeria property on this element")
    assert notes[1].startswith("not applied: Supplementary Properties: Egeria keeps them on a separate glossary term")
    assert client.metadata_expert.calls == [] and client.classification_manager.calls == []


@pytest.mark.asyncio
async def test_a_processor_that_applied_an_attribute_itself_is_skipped():
    p, client = _run_processor()
    p.parsed_output["applied_attributes"] = {"Classifications"}
    await p._sync_referenceable_extras(GUID, {"Classifications": {"value": "- Taxonomy"}})
    assert client.metadata_expert.calls == []
