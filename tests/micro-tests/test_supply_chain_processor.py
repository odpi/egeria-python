# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Regression test for ISSUE-64: `Create Information Supply Chain`'s `Purposes`/
`Scope` attributes were silently dropped -- set_element_prop_body() (the
generic Referenceable-level body builder) has no knowledge of
InformationSupplyChainProperties-specific fields, and SupplyChainProcessor
.apply_changes() never added them on top, so --validate/--process reported
SUCCESS while the element was created with neither field ever set. Also
confirms the real wire property is "dataProcessingPurposes", not "purposes"
(confirmed against Egeria-api-solution-architect.http's
createInformationSupplyChain worked example).

No live server needed: a fake client captures the body passed to
_async_create_info_supply_chain / _async_update_info_supply_chain.
"""
from typing import Any, cast

import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.solution_architect import SupplyChainProcessor


class _FakeClient:
    def __init__(self):
        self.create_calls = []
        self.update_calls = []

    async def _async_create_info_supply_chain(self, body: dict) -> str:
        self.create_calls.append(body)
        return "9ef6a208-c7af-4dcb-89ae-7dc0de6411f2"

    async def _async_update_info_supply_chain(self, guid: str, body: dict) -> None:
        self.update_calls.append((guid, body))

    async def _async_get_info_supply_chain_by_guid(self, guid: str) -> dict:
        # No existing relationships -- sync_members has nothing to do.
        return {}


def _command(verb: str) -> DrECommand:
    return DrECommand(verb=verb, object_type="Information Supply Chain", attributes={},
                       raw_block=f"# {verb} Information Supply Chain")


@pytest.mark.asyncio
async def test_create_information_supply_chain_persists_purposes_and_scope():
    client = _FakeClient()
    p = SupplyChainProcessor(client=cast(Any, client), command=_command("Create"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": "InformationSupplyChain"}
    p.parsed_output = {
        "qualified_name": "InformationSupplyChain::test::1",
        "attributes": {
            "Display Name": {"value": "Test ISC"},
            "Purposes": {"value": ["purpose one", "purpose two"]},
            "Scope": {"value": "test scope"},
        },
    }

    await p.apply_changes()

    assert len(client.create_calls) == 1
    props = client.create_calls[0]["properties"]
    assert props["dataProcessingPurposes"] == ["purpose one", "purpose two"]
    assert props["scope"] == "test scope"
    # the compact spec's attribute is named "Purposes" but the real Egeria
    # wire property is "dataProcessingPurposes" -- confirm the wrong name
    # never leaks into the outgoing body.
    assert "purposes" not in props


@pytest.mark.asyncio
async def test_update_information_supply_chain_persists_purposes_and_scope():
    client = _FakeClient()
    p = SupplyChainProcessor(client=cast(Any, client), command=_command("Update"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": "InformationSupplyChain"}
    p.parsed_output = {
        "guid": "isc-guid-existing",
        "qualified_name": "InformationSupplyChain::test::1",
        "attributes": {
            "Display Name": {"value": "Test ISC"},
            "Purposes": {"value": ["updated purpose"]},
            "Scope": {"value": "updated scope"},
        },
    }
    p.as_is_element = {"elementHeader": {"guid": "isc-guid-existing"}}

    await p.apply_changes()

    assert len(client.update_calls) == 1
    guid, body = client.update_calls[0]
    assert guid == "isc-guid-existing"
    assert body["properties"]["dataProcessingPurposes"] == ["updated purpose"]
    assert body["properties"]["scope"] == "updated scope"


@pytest.mark.asyncio
async def test_create_information_supply_chain_omits_purposes_scope_when_unset():
    # merge_update / create-time None handling: if the caller never set
    # Purposes/Scope, the properties dict should carry them as None (create
    # path) rather than some stale/empty-list default that could overwrite
    # a real value on a later update.
    client = _FakeClient()
    p = SupplyChainProcessor(client=cast(Any, client), command=_command("Create"), context={})
    p.get_command_spec = lambda: {"OM_TYPE": "InformationSupplyChain"}
    p.parsed_output = {
        "qualified_name": "InformationSupplyChain::test::2",
        "attributes": {"Display Name": {"value": "Test ISC 2"}},
    }

    await p.apply_changes()

    props = client.create_calls[0]["properties"]
    assert props["dataProcessingPurposes"] is None
    assert props["scope"] is None
