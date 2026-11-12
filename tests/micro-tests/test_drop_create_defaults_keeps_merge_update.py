# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""A Create that resolves to an existing element drops the spec defaults the parser filled in (#498),
but keeps Merge Update: without it, a processor that defaults Merge Update to False would send a replace
update over the stored element."""
from typing import Any, cast

from md_processing.v2.extraction import DrECommand
from md_processing.v2.processors import AsyncBaseCommandProcessor


class _P(AsyncBaseCommandProcessor):
    async def apply_changes(self):
        return ""


def test_create_defaults_are_dropped_but_merge_update_is_kept():
    p = _P(client=cast(Any, object()), command=DrECommand(verb="Update", object_type="Data Field", attributes={},
                                                          raw_block="## Update Data Field"), context={})
    p.parsed_output = {"attributes": {
        "Display Name": {"value": "RTP"},
        "Is Nullable": {"value": True, "is_default": True},
        "Merge Update": {"value": True, "is_default": True},
        "Description": {"value": "written"}}}
    p._drop_create_defaults()
    assert set(p.parsed_output["attributes"]) == {"Display Name", "Merge Update", "Description"}
    assert p.parsed_output["attributes"]["Merge Update"]["value"] is True
