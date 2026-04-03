from typing import Any, cast

import pytest

from md_processing.v2.extraction import DrECommand
from md_processing.v2.governance import GovernanceLinkProcessor


class _FakeClient:
    def __init__(self):
        self.calls = []

    async def _async_attach_governed_by_definition(self, left: str, right: str, body: dict):
        self.calls.append(("attach_governed_by", left, right, body))

    async def _async_detach_governed_by_definition(self, left: str, right: str, body: dict):
        self.calls.append(("detach_governed_by", left, right, body))

    async def _async_attach_supporting_definitions(self, left: str, rel: str, right: str, body: dict):
        self.calls.append(("attach_supporting", left, rel, right, body))

    async def _async_link_governance_zones(self, left: str, right: str, body: dict):
        self.calls.append(("link_zone_hierarchy", left, right, body))

    async def _async_detach_governance_zones(self, left: str, right: str, body: dict):
        self.calls.append(("detach_zone_hierarchy", left, right, body))

    async def _async_add_certification_to_element(self, cert_type_guid: str, element_guid: str, body: dict):
        self.calls.append(("add_certification", cert_type_guid, element_guid, body))

    async def _async_add_license_to_element(self, license_type_guid: str, element_guid: str, body: dict):
        self.calls.append(("add_license", license_type_guid, element_guid, body))

    async def _async_link_agreement_item(self, agreement_guid: str, item_guid: str, body: dict):
        self.calls.append(("link_agreement_item", agreement_guid, item_guid, body))

    async def _async_detach_agreement_item(self, agreement_guid: str, item_guid: str, body: dict):
        self.calls.append(("detach_agreement_item", agreement_guid, item_guid, body))

    async def _async_link_peer_definitions(self, left: str, rel: str, right: str, body: dict):
        self.calls.append(("link_peer", left, rel, right, body))

    async def _async_detach_peer_definitions(self, left: str, rel: str, right: str, body: dict):
        self.calls.append(("detach_peer", left, rel, right, body))

    async def _async_link_monitored_resource(self, left: str, right: str, body: dict):
        self.calls.append(("link_monitored_resource", left, right, body))

    async def _async_detach_monitored_resource(self, left: str, right: str, body: dict):
        self.calls.append(("detach_monitored_resource", left, right, body))

    async def _async_decertify_element(self, certification_guid: str, body: dict):
        self.calls.append(("decertify", certification_guid, body))

    async def _async_unlicense_element(self, license_guid: str, body: dict):
        self.calls.append(("unlicense", license_guid, body))


@pytest.mark.asyncio
async def test_link_governed_by_uses_referenceable_and_definition_guids():
    client = _FakeClient()
    cmd = DrECommand(verb="Link", object_type="Governed By", attributes={}, raw_block="# Link Governed By")
    p = GovernanceLinkProcessor(client=cast(Any, client), command=cmd, context={})
    p.parsed_output = {
        "attributes": {
            "Referenceable": {"guid": "ref-guid"},
            "Governance Definition": {"guid": "gov-guid"},
        }
    }

    out = await p.apply_changes()

    assert "Operation completed" in out
    assert client.calls[0][0] == "attach_governed_by"
    assert client.calls[0][1] == "ref-guid"
    assert client.calls[0][2] == "gov-guid"


@pytest.mark.asyncio
async def test_unlink_governed_by_uses_singular_detach_method():
    client = _FakeClient()
    cmd = DrECommand(verb="Unlink", object_type="Governed By", attributes={}, raw_block="# Unlink Governed By")
    p = GovernanceLinkProcessor(client=cast(Any, client), command=cmd, context={})
    p.parsed_output = {
        "attributes": {
            "Referenceable": {"guid": "ref-guid"},
            "Governance Definition": {"guid": "gov-guid"},
        }
    }

    out = await p.apply_changes()

    assert "Operation completed" in out
    assert client.calls[0][0] == "detach_governed_by"


@pytest.mark.asyncio
async def test_link_governance_response_maps_driver_policy_to_supporting_relationship():
    client = _FakeClient()
    cmd = DrECommand(verb="Link", object_type="Governance Response", attributes={}, raw_block="# Link Governance Response")
    p = GovernanceLinkProcessor(client=cast(Any, client), command=cmd, context={})
    p.parsed_output = {
        "attributes": {
            "Driver": {"guid": "driver-guid"},
            "Policy": {"guid": "policy-guid"},
            "Rationale": {"value": "because"},
        }
    }

    out = await p.apply_changes()

    assert "Operation completed" in out
    assert client.calls[0][0] == "attach_supporting"
    assert client.calls[0][1] == "driver-guid"
    assert client.calls[0][2] == "GovernanceResponse"
    assert client.calls[0][3] == "policy-guid"


@pytest.mark.asyncio
async def test_link_governed_by_raises_on_unresolved_references():
    client = _FakeClient()
    cmd = DrECommand(verb="Link", object_type="Governed By", attributes={}, raw_block="# Link Governed By")
    p = GovernanceLinkProcessor(client=cast(Any, client), command=cmd, context={})
    p.parsed_output = {"attributes": {"Referenceable": {}, "Governance Definition": {"guid": "gov-guid"}}}

    with pytest.raises(ValueError):
        await p.apply_changes()


@pytest.mark.asyncio
async def test_link_zone_hierarchy_uses_security_officer_methods():
    client = _FakeClient()
    cmd = DrECommand(verb="Link", object_type="Zone Hierarchy", attributes={}, raw_block="# Link Zone Hierarchy")
    p = GovernanceLinkProcessor(client=cast(Any, client), command=cmd, context={})
    p.parsed_output = {
        "attributes": {
            "Parent Zone": {"guid": "parent-guid"},
            "Child Zone": {"guid": "child-guid"},
        }
    }

    out = await p.apply_changes()

    assert "Operation completed" in out
    assert client.calls[0][0] == "link_zone_hierarchy"
    assert client.calls[0][1] == "parent-guid"
    assert client.calls[0][2] == "child-guid"


@pytest.mark.asyncio
async def test_link_associated_group_routes_to_peer_link_method():
    client = _FakeClient()
    cmd = DrECommand(verb="Link", object_type="Associated Group", attributes={}, raw_block="# Link Associated Group")
    p = GovernanceLinkProcessor(client=cast(Any, client), command=cmd, context={})
    p.parsed_output = {
        "attributes": {
            "Access Control": {"guid": "access-guid"},
            "Security Group": {"guid": "group-guid"},
        }
    }

    out = await p.apply_changes()

    assert "Operation completed" in out
    assert client.calls[0][0] == "link_peer"
    assert client.calls[0][1] == "access-guid"
    assert client.calls[0][2] == "AssociatedSecurityGroup"
    assert client.calls[0][3] == "group-guid"


@pytest.mark.asyncio
async def test_unlink_associated_group_routes_to_peer_detach_method():
    client = _FakeClient()
    cmd = DrECommand(verb="Unlink", object_type="Associated Group", attributes={}, raw_block="# Unlink Associated Group")
    p = GovernanceLinkProcessor(client=cast(Any, client), command=cmd, context={})
    p.parsed_output = {
        "attributes": {
            "Access Control": {"guid": "access-guid"},
            "Security Group": {"guid": "group-guid"},
        }
    }

    out = await p.apply_changes()

    assert "Operation completed" in out
    assert client.calls[0][0] == "detach_peer"
    assert client.calls[0][2] == "AssociatedSecurityGroup"


@pytest.mark.asyncio
async def test_link_monitored_resource_routes_to_notification_manager_method():
    client = _FakeClient()
    cmd = DrECommand(verb="Link", object_type="Monitored Resource", attributes={}, raw_block="# Link Monitored Resource")
    p = GovernanceLinkProcessor(client=cast(Any, client), command=cmd, context={})
    p.parsed_output = {
        "attributes": {
            "Notification Type": {"guid": "notification-guid"},
            "Monitored Resource": {"guid": "resource-guid"},
        }
    }

    out = await p.apply_changes()

    assert "Operation completed" in out
    assert client.calls[0][0] == "link_monitored_resource"
    assert client.calls[0][1] == "notification-guid"
    assert client.calls[0][2] == "resource-guid"


@pytest.mark.asyncio
async def test_unlink_monitored_resource_routes_to_notification_manager_detach():
    client = _FakeClient()
    cmd = DrECommand(verb="Unlink", object_type="Monitored Resource", attributes={}, raw_block="# Unlink Monitored Resource")
    p = GovernanceLinkProcessor(client=cast(Any, client), command=cmd, context={})
    p.parsed_output = {
        "attributes": {
            "Notification Type": {"guid": "notification-guid"},
            "Monitored Resource": {"guid": "resource-guid"},
        }
    }

    out = await p.apply_changes()

    assert "Operation completed" in out
    assert client.calls[0][0] == "detach_monitored_resource"


@pytest.mark.asyncio
async def test_link_regulation_certification_type_routes_to_peer_link_method():
    client = _FakeClient()
    cmd = DrECommand(
        verb="Link",
        object_type="Regulation Certification Type",
        attributes={},
        raw_block="# Link Regulation Certification Type",
    )
    p = GovernanceLinkProcessor(client=cast(Any, client), command=cmd, context={})
    p.parsed_output = {
        "attributes": {
            "Regulation": {"guid": "reg-guid"},
            "Certification Type": {"guid": "cert-guid"},
        }
    }

    out = await p.apply_changes()

    assert "Operation completed" in out
    assert client.calls[0][0] == "link_peer"
    assert client.calls[0][2] == "RegulationCertificationType"
    assert client.calls[0][1] == "reg-guid"
    assert client.calls[0][3] == "cert-guid"


@pytest.mark.asyncio
async def test_link_certification_routes_to_classification_explorer_method():
    client = _FakeClient()
    cmd = DrECommand(verb="Link", object_type="Certification", attributes={}, raw_block="# Link Certification")
    p = GovernanceLinkProcessor(client=cast(Any, client), command=cmd, context={})
    p.parsed_output = {
        "attributes": {
            "Certification Type": {"guid": "cert-type-guid"},
            "Referenceable": {"guid": "element-guid"},
            "Certificate GUID": {"value": "CERT-1"},
        }
    }

    out = await p.apply_changes()

    assert "Operation completed" in out
    assert client.calls[0][0] == "add_certification"
    assert client.calls[0][1] == "cert-type-guid"
    assert client.calls[0][2] == "element-guid"


@pytest.mark.asyncio
async def test_link_license_routes_to_classification_explorer_method():
    client = _FakeClient()
    cmd = DrECommand(verb="Link", object_type="License", attributes={}, raw_block="# Link License")
    p = GovernanceLinkProcessor(client=cast(Any, client), command=cmd, context={})
    p.parsed_output = {
        "attributes": {
            "License Type": {"guid": "license-type-guid"},
            "Referenceable": {"guid": "element-guid"},
            "License GUID": {"value": "LIC-1"},
        }
    }

    out = await p.apply_changes()

    assert "Operation completed" in out
    assert client.calls[0][0] == "add_license"
    assert client.calls[0][1] == "license-type-guid"
    assert client.calls[0][2] == "element-guid"


@pytest.mark.asyncio
async def test_link_agreement_tc_routes_to_collection_manager_method():
    client = _FakeClient()
    cmd = DrECommand(verb="Link", object_type="Agreement T&C", attributes={}, raw_block="# Link Agreement T&C")
    p = GovernanceLinkProcessor(client=cast(Any, client), command=cmd, context={})
    p.parsed_output = {
        "attributes": {
            "Agreement Name": {"guid": "agreement-guid"},
            "Terms & Conditions Id": {"guid": "item-guid"},
        }
    }

    out = await p.apply_changes()

    assert "Operation completed" in out
    assert client.calls[0][0] == "link_agreement_item"
    assert client.calls[0][1] == "agreement-guid"
    assert client.calls[0][2] == "item-guid"


@pytest.mark.asyncio
async def test_unlink_agreement_tc_routes_to_collection_manager_detach():
    client = _FakeClient()
    cmd = DrECommand(verb="Unlink", object_type="Agreement T&C", attributes={}, raw_block="# Unlink Agreement T&C")
    p = GovernanceLinkProcessor(client=cast(Any, client), command=cmd, context={})
    p.parsed_output = {
        "attributes": {
            "Agreement Name": {"guid": "agreement-guid"},
            "Terms & Conditions Id": {"guid": "item-guid"},
        }
    }

    out = await p.apply_changes()

    assert "Operation completed" in out
    assert client.calls[0][0] == "detach_agreement_item"


@pytest.mark.asyncio
async def test_link_governance_mechanism_uses_governance_mechanism_relationship():
    client = _FakeClient()
    cmd = DrECommand(verb="Link", object_type="Governance Mechanism", attributes={}, raw_block="# Link Governance Mechanism")
    p = GovernanceLinkProcessor(client=cast(Any, client), command=cmd, context={})
    p.parsed_output = {
        "attributes": {
            "Policy": {"guid": "policy-guid"},
            "Mechanism": {"guid": "control-guid"},
        }
    }

    out = await p.apply_changes()

    assert "Operation completed" in out
    assert client.calls[0][0] == "attach_supporting"
    assert client.calls[0][2] == "GovernanceMechanism"


@pytest.mark.asyncio
async def test_unlink_certification_requires_relationship_guid_when_missing():
    client = _FakeClient()
    cmd = DrECommand(verb="Unlink", object_type="Certification", attributes={}, raw_block="# Unlink Certification")
    p = GovernanceLinkProcessor(client=cast(Any, client), command=cmd, context={})
    p.parsed_output = {
        "attributes": {
            "Certification Type": {"guid": "cert-type-guid"},
            "Referenceable": {"guid": "element-guid"},
        }
    }

    with pytest.raises(ValueError):
        await p.apply_changes()


@pytest.mark.asyncio
async def test_unlink_certification_uses_relationship_guid_when_provided():
    client = _FakeClient()
    cmd = DrECommand(verb="Unlink", object_type="Certification", attributes={}, raw_block="# Unlink Certification")
    p = GovernanceLinkProcessor(client=cast(Any, client), command=cmd, context={})
    p.parsed_output = {
        "guid": "2dd3c85f-cc0b-4f08-8c33-2dfd64958caa",
        "attributes": {
            "Certification Type": {"guid": "cert-type-guid"},
            "Referenceable": {"guid": "element-guid"},
        }
    }

    out = await p.apply_changes()

    assert "Operation completed" in out
    assert client.calls[0][0] == "decertify"
    assert client.calls[0][1] == "2dd3c85f-cc0b-4f08-8c33-2dfd64958caa"


@pytest.mark.asyncio
async def test_unlink_license_uses_relationship_guid_when_provided():
    client = _FakeClient()
    cmd = DrECommand(verb="Unlink", object_type="License", attributes={}, raw_block="# Unlink License")
    p = GovernanceLinkProcessor(client=cast(Any, client), command=cmd, context={})
    p.parsed_output = {
        "attributes": {
            "License Type": {"guid": "license-type-guid"},
            "Referenceable": {"guid": "element-guid"},
            "GUID": {"value": "2dd3c85f-cc0b-4f08-8c33-2dfd64958caa"},
        }
    }

    out = await p.apply_changes()

    assert "Operation completed" in out
    assert client.calls[0][0] == "unlicense"
    assert client.calls[0][1] == "2dd3c85f-cc0b-4f08-8c33-2dfd64958caa"


