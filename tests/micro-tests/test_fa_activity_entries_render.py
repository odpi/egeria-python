# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""F-A item 9: Create Blog / Journal / Activity Entry reported failure for an entry Egeria had created.

After the create, the processor read the entry back with _async_get_note_by_guid, which asks for type Note;
Egeria refuses a BlogEntry (or JournalEntry, ActivityEntry) for that: "OMAG-REPOSITORY-HANDLER-404-001 ...
of type BlogEntry rather than type Note" (round-trip probe, PostgreSQL scratch, 2026-11-12). The result is
now rendered from the created element itself.
"""
from typing import Any, cast

import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.feedback import FeedbackProcessor

GUID = "11831149-eed7-466a-9488-270d6164f442"


class _MyProfile:
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        async def create(**kwargs):
            self.calls.append((name, kwargs))
            return GUID
        return create


class _Client:
    def __init__(self):
        self.my_profile = _MyProfile()

    async def _async_get_note_by_guid(self, *args, **kwargs):
        raise AssertionError("an activity entry is not a Note: Egeria refuses this read")


@pytest.mark.asyncio
@pytest.mark.parametrize("object_type, method", [
    ("Blog Entry", "_async_blog_my_activity"),
    ("Journal Entry", "_async_journal_my_activity"),
    ("Activity Entry", "_async_log_my_activity"),
])
async def test_activity_entry_result_is_rendered_from_the_entry(object_type, method):
    client = _Client()
    p = FeedbackProcessor(client=cast(Any, client),
                          command=DrECommand(verb="Create", object_type=object_type, attributes={},
                                             raw_block=f"## Create {object_type}"), context={})
    p.parsed_output = {"qualified_name": f"RTP::{object_type}", "attributes": {
        "Display Name": {"value": f"RTP {object_type}"}, "Description": {"value": "text"}}}

    async def render(guid):
        return f"rendered {guid}"
    p.render_result_markdown = render
    out = await p.apply_changes()
    assert out == f"rendered {GUID}"
    assert client.my_profile.calls[0][0] == method and p.parsed_output["guid"] == GUID
