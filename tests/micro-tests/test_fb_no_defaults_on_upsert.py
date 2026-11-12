# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""A Create that resolves to an existing element is an update: the spec defaults the parser filled in for
a create (Content Status ACTIVE, ...) must not overwrite values the document never mentioned."""
from typing import Any, cast

from md_processing.v2.extraction import DrECommand
from md_processing.v2.processors import AsyncBaseCommandProcessor


class _P(AsyncBaseCommandProcessor):
    async def apply_changes(self):
        return ""


def test_spec_defaults_are_dropped_and_written_values_kept():
    p = _P(client=cast(Any, object()), command=DrECommand(verb="Create", object_type="Glossary", attributes={},
                                                          raw_block="## Create Glossary"), context={})
    p.parsed_output = {"attributes": {
        "Display Name": {"value": "RTP"},
        "Content Status": {"value": "ACTIVE", "is_default": True},
        "Description": {"value": "written"},
        "Merge Update": {"value": True, "is_default": True}}}
    p._drop_spec_defaults()
    assert set(p.parsed_output["attributes"]) == {"Display Name", "Description"}
