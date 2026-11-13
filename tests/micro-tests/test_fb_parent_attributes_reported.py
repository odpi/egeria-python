# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""F-B group 8: Parent Relationship Attributes are never dropped silently.

Processors that build their own create body (Data Class, Data Value Specification, Measurement
Specification, Informal Tag, Solution Component) never looked at them: 6 rows DROPPED on the round-trip
probe's PostgreSQL baseline. With no Parent ID there is nothing to attach them to, and the command now says
so; with a Parent ID the base processor's typed _sync_parent_relationship applies them (F-A 1).
"""
from typing import Any, cast

import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.processors import AsyncBaseCommandProcessor


class _P(AsyncBaseCommandProcessor):
    async def apply_changes(self):
        return ""


def test_parent_attributes_without_a_parent_are_reported():
    p = _P(client=cast(Any, object()), command=DrECommand(verb="Create", object_type="Data Class", attributes={},
                                                          raw_block="## Create Data Class"), context={})
    p.parsed_output = {"qualified_name": "RTP::DC", "attributes": {
        "Display Name": {"value": "RTP DC"},
        "Parent Relationship Attributes": {"value": {"rtpKey": "RTP"}}}}
    p._report_unapplied()
    warnings = p.parsed_output.get("warnings", [])
    assert ("not applied: Parent Relationship Attributes: there is no Parent ID to attach them to" in warnings)


def test_with_a_parent_or_an_earlier_report_nothing_is_added():
    p = _P(client=cast(Any, object()), command=DrECommand(verb="Create", object_type="Data Class", attributes={},
                                                          raw_block="## Create Data Class"), context={})
    p.parsed_output = {"attributes": {
        "Parent ID": {"value": "x", "guid": "0d2c3c3e-0000-0000-0000-000000000001"},
        "Parent Relationship Attributes": {"value": {"k": "v"}}}}
    p._report_unapplied()
    assert p.parsed_output.get("warnings", []) == []
