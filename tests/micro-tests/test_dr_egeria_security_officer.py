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


# --- Survey reports and security findings (model 0665) ---

from md_processing.v2.security_officer import (  # noqa: E402
    SecurityFindingProcessor, SurveyReportProcessor, _annotation_properties,
)


def test_annotation_properties_maps_type_fields_and_skips_unset():
    props = _annotation_properties("VulnerabilityAnnotation", "VulnerabilityFinding::x", {
        "Display Name": {"value": "Log4Shell"},
        "Severity": {"value": "Critical"},
        "CVSS Score": {"value": 10.0},
        "Package URL": {"value": "pkg:maven/x@1"},
        "Exploit Available": {"value": None},
        "Vulnerability Identifiers": {"value": ["CVE-2021-44228"]},
        "Weakness Identifiers": {"value": []},
    })
    assert props["class"] == "VulnerabilityAnnotationProperties"
    assert props["severity"] == "Critical" and props["cvssScore"] == 10.0
    assert props["packageURL"] == "pkg:maven/x@1"
    assert props["vulnerabilityIdentifiers"] == ["CVE-2021-44228"]
    assert "exploitAvailable" not in props and "weaknessIdentifiers" not in props


def test_annotation_properties_posture_counts_are_ints():
    props = _annotation_properties("SecurityPostureAnnotation", "SecurityPosture::x", {
        "Finding Counts By Severity": {"value": {"Critical": "1", "High": "4"}},
        "Resources In Scope Count": {"value": 3},
    })
    assert props["class"] == "SecurityPostureAnnotationProperties"
    assert props["findingCountsBySeverity"] == {"Critical": 1, "High": 4}
    assert props["resourcesInScopeCount"] == 3


NEW_GUID = "5b0e2f7c-1c1a-4d55-9a3e-6f0d2b8c9e11"


class _FindingClient:
    def __init__(self):
        self.calls = []

    async def _async_create_annotation(self, body):
        self.calls.append(("create", body))
        return NEW_GUID

    async def _async_link_annotation_to_described_element(self, annotation_guid, element_guid, body):
        self.calls.append(("associated", annotation_guid, element_guid))

    async def _async_link_annotation_to_its_predecessor(self, annotation_guid, predecessor_guid, body):
        self.calls.append(("predecessor", annotation_guid, predecessor_guid))


def _finding_processor(client, attributes, om_type="PenetrationTestFindingAnnotation"):
    proc = SecurityFindingProcessor.__new__(SecurityFindingProcessor)
    proc.client = client
    proc.command = type("Cmd", (), {"verb": "Create", "object_type": "Penetration Test Finding", "raw_block": ""})()
    proc.parsed_output = {"qualified_name": "PenetrationTestFinding::x", "attributes": attributes}
    proc.as_is_element = None
    proc.get_command_spec = lambda: {"OM_TYPE": om_type}

    async def render(guid):
        return guid
    proc.render_result_markdown = render
    proc.add_related_result = lambda *a, **k: None
    return proc


@pytest.mark.asyncio
async def test_new_finding_is_created_under_its_report_and_linked(monkeypatch):
    monkeypatch.setattr("md_processing.v2.security_officer.update_element_dictionary", lambda *a, **k: None)
    client = _FindingClient()
    await _finding_processor(client, {
        "Display Name": {"value": "SQL injection"},
        "Survey Report": {"value": "SurveyReport::x", "guid": "report-guid"},
        "Severity": {"value": "High"},
        "Affected Elements": {"value": ["Collection::portal"], "guid_list": ["portal-guid"]},
        "Previous Finding": {"value": "PenetrationTestFinding::old", "guid": "old-guid"},
    }).apply_changes()

    kind, body = client.calls[0]
    assert kind == "create"
    assert (body["parentGUID"], body["anchorGUID"], body["parentRelationshipTypeName"]) == \
        ("report-guid", "report-guid", "ReportedAnnotation")
    assert body["parentAtEnd1"] is True and body["isOwnAnchor"] is False
    assert body["properties"]["class"] == "PenetrationTestFindingAnnotationProperties"
    assert ("associated", NEW_GUID, "portal-guid") in client.calls
    assert ("predecessor", NEW_GUID, "old-guid") in client.calls


@pytest.mark.asyncio
async def test_new_finding_without_resolved_report_fails():
    with pytest.raises(ValueError):
        await _finding_processor(_FindingClient(), {"Display Name": {"value": "x"},
                                                    "Survey Report": {"value": "missing"}}).apply_changes()


class _UpdateClient:
    def __init__(self):
        self.updates = []

    async def _async_update_annotation(self, guid, body):
        self.updates.append((guid, body))


@pytest.mark.asyncio
async def test_merge_update_carries_primitives_forward(monkeypatch):
    # Egeria resets an omitted primitive to 0 / false on a merge update (ISSUE-166).
    monkeypatch.setattr("md_processing.v2.security_officer.update_element_dictionary", lambda *a, **k: None)
    client = _UpdateClient()
    proc = _finding_processor(client, {"Display Name": {"value": "SQL injection"},
                                       "Reproduction Steps": {"value": "Search for ' OR 1=1"}})
    proc.as_is_element = {"elementHeader": {"guid": NEW_GUID},
                          "properties": {"cvssScore": 8.6, "exploitAvailable": True, "severity": "High"}}
    proc.filter_update_properties = lambda props, merge: props
    await proc.apply_changes()

    props = client.updates[0][1]["properties"]
    assert props["cvssScore"] == 8.6 and props["exploitAvailable"] is True
    assert props["reproductionSteps"] == "Search for ' OR 1=1"
    assert "severity" not in props          # non-primitives merge correctly on their own


@pytest.mark.asyncio
async def test_command_value_wins_over_current_and_numbers_are_typed(monkeypatch):
    monkeypatch.setattr("md_processing.v2.security_officer.update_element_dictionary", lambda *a, **k: None)
    client = _UpdateClient()
    proc = _finding_processor(client, {"Display Name": {"value": "x"}, "CVSS Score": {"value": "9.1"}})
    proc.as_is_element = {"elementHeader": {"guid": NEW_GUID}, "properties": {"cvssScore": 8.6}}
    proc.filter_update_properties = lambda props, merge: props
    await proc.apply_changes()
    assert client.updates[0][1]["properties"]["cvssScore"] == 9.1
