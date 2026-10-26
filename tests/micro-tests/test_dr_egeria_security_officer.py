"""
Dr.Egeria Security Officer processors: Link Control Applicability merges with
the existing relationship properties, because Egeria's attach replaces them
wholesale when the control is already linked (confirmed live, Egeria 6.3).
No live server: the SecurityOfficer client calls are stubbed.
"""
import pytest

from md_processing.v2.security_officer import ControlApplicabilityLinkProcessor, _related_guids


class _Cmd:
    verb = "Link"
    object_type = "Control Applicability"
    raw_block = ""


class _Client:
    def __init__(self, existing):
        self.existing = existing
        self.linked = []

    async def _async_get_statement_of_applicability_by_guid(self, guid, body=None):
        return {"otherRelatedElements": [{
            "relationshipHeader": {"type": {"typeName": "ControlApplicability"}},
            "relationshipProperties": {"class": "ControlApplicabilityProperties",
                                       "typeName": "ControlApplicability", **self.existing},
            "relatedElement": {"elementHeader": {"guid": "control-guid"}},
        }]}

    async def _async_link_control_applicability(self, soa_guid, control_guid, body):
        self.linked.append((soa_guid, control_guid, body))


def _processor(client, attributes):
    proc = ControlApplicabilityLinkProcessor.__new__(ControlApplicabilityLinkProcessor)
    proc.client = client
    proc.command = _Cmd()
    proc.parsed_output = {"attributes": {
        "Statement of Applicability": {"guid": "soa-guid"},
        "Control": {"guid": "control-guid"},
        **attributes,
    }}
    return proc


EXISTING = {"label": "8.20", "justification": "Ransomware", "inclusionReasons": ["Risk Treatment"],
            "implementationStatus": "PARTIALLY_IMPLEMENTED", "reviewDate": "2026-10-26T00:00:00.000+00:00"}


@pytest.mark.asyncio
async def test_relink_keeps_existing_properties_by_default():
    client = _Client(EXISTING)
    await _processor(client, {"Implementation Status": {"value": "IMPLEMENTED"}}).apply_changes()

    props = client.linked[0][2]["properties"]
    assert props["class"] == "ControlApplicabilityProperties"
    assert props["implementationStatus"] == "IMPLEMENTED"
    assert props["justification"] == "Ransomware"
    assert props["inclusionReasons"] == ["Risk Treatment"]
    assert "typeName" not in props


@pytest.mark.asyncio
async def test_relink_with_merge_update_false_replaces_properties():
    client = _Client(EXISTING)
    await _processor(client, {"Implementation Status": {"value": "IMPLEMENTED"},
                              "Merge Update": {"value": False}}).apply_changes()

    props = client.linked[0][2]["properties"]
    assert props == {"class": "ControlApplicabilityProperties", "implementationStatus": "IMPLEMENTED"}


def test_related_guids_filters_by_relationship_and_related_type():
    element = {
        "governedBy": [
            {"relationshipHeader": {"type": {"typeName": "GovernedBy"}},
             "relatedElement": {"elementHeader": {"guid": "cert", "type": {"typeName": "CertificationType"}}}},
            {"relationshipHeader": {"type": {"typeName": "GovernedBy"}},
             "relatedElement": {"elementHeader": {"guid": "policy", "type": {"typeName": "GovernancePolicy"}}}},
        ],
        "relevantToScopes": [
            {"relationshipHeader": {"type": {"typeName": "ScopedBy"}},
             "relatedElement": {"elementHeader": {"guid": "org", "type": {"typeName": "Organization"}}}},
        ],
    }
    assert _related_guids(element, "GovernedBy", "CertificationType") == {"cert"}
    assert _related_guids(element, "ScopedBy") == {"org"}
    assert _related_guids(None, "ScopedBy") == set()
