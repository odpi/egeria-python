"""
Security annotation models and the DataDiscovery security finding / posture views (Egeria 6.3, model 0665).
No live server: the annotation lists are stubbed, in the shape a live 6.3 platform returns.

Egeria stores cvssScore, exploitAvailable, patchAvailable and the posture counts as Java primitives, so an
unset value comes back as 0 / false (confirmed live). The display rows must not present those as answers.
"""
import pytest
from pydantic import ValidationError

from pyegeria.models import (
    PenetrationTestFindingAnnotationProperties,
    SecurityPostureAnnotationProperties,
    VulnerabilityAnnotationProperties,
)
from pyegeria.omvs.data_discovery import AnnotationProperties, DataDiscovery


def _annotation(type_name, guid, props, report=None):
    element = {
        "elementHeader": {"guid": guid, "type": {"typeName": type_name},
                          "versions": {"createTime": f"2026-10-26T00:00:0{guid[-1]}Z"}},
        "properties": {"class": f"{type_name}Properties", "typeName": type_name, "displayName": guid, **props},
    }
    if report:
        element["fromSurveyReports"] = [{
            "relationshipHeader": {"type": {"typeName": "ReportedAnnotation"}},
            "relatedElement": {"elementHeader": {"guid": report["guid"], "type": {"typeName": "SurveyReport"}},
                               "properties": {k: v for k, v in report.items() if k != "guid"}},
        }]
    return element


# An unset vulnerability, as returned live: only severity was supplied.
SPARSE = _annotation("VulnerabilityAnnotation", "sparse-1",
                     {"severity": "Medium", "cvssScore": 0.0, "exploitAvailable": False, "patchAvailable": False})
FULL = _annotation("VulnerabilityAnnotation", "full-2",
                   {"severity": "Critical", "cvssScore": 10.0, "exploitAvailable": True,
                    "packageURL": "pkg:maven/org.apache.logging.log4j/log4j-core@2.14.1"})
PENTEST = _annotation("PenetrationTestFindingAnnotation", "pen-3", {"severity": "High", "cvssScore": 8.6})
NONE_SCORE = _annotation("SecurityFindingAnnotation", "info-4", {"severity": "None", "cvssScore": 0.0})
OTHER = _annotation("ResourceProfileAnnotation", "other-5", {})


def test_models_serialize_egeria_field_names():
    v = VulnerabilityAnnotationProperties(**{"class": "VulnerabilityAnnotationProperties", "qualifiedName": "q",
                                             "displayName": "d", "severity": "High", "cvssScore": 7.5,
                                             "packageURL": "pkg:x", "patchAvailable": True})
    assert v.model_dump(by_alias=True, exclude_none=True) == {
        "class": "VulnerabilityAnnotationProperties", "qualifiedName": "q", "displayName": "d",
        "severity": "High", "cvssScore": 7.5, "packageURL": "pkg:x", "patchAvailable": True}
    p = SecurityPostureAnnotationProperties(**{"class": "SecurityPostureAnnotationProperties", "qualifiedName": "q",
                                               "displayName": "d", "findingCountsBySeverity": {"High": 4},
                                               "resourcesInScopeCount": 3})
    assert p.model_dump(by_alias=True, exclude_none=True)["findingCountsBySeverity"] == {"High": 4}
    pen = PenetrationTestFindingAnnotationProperties(**{"class": "PenetrationTestFindingAnnotationProperties",
                                                        "qualifiedName": "q", "displayName": "d",
                                                        "attackTechniques": ["T1190"]})
    assert pen.model_dump(by_alias=True, exclude_none=True)["attackTechniques"] == ["T1190"]


def test_models_reject_bad_severity_and_score():
    with pytest.raises(ValidationError):
        VulnerabilityAnnotationProperties(**{"class": "VulnerabilityAnnotationProperties", "qualifiedName": "q",
                                             "displayName": "d", "severity": "Severe"})
    with pytest.raises(ValidationError):
        VulnerabilityAnnotationProperties(**{"class": "VulnerabilityAnnotationProperties", "qualifiedName": "q",
                                             "displayName": "d", "cvssScore": 11})


def test_annotation_properties_uses_egerias_confidence_field():
    # The old local model used confidence_level, which Egeria silently ignores.
    a = AnnotationProperties(**{"class": "AnnotationProperties", "qualifiedName": "q", "displayName": "d",
                                "confidence": 80})
    assert a.model_dump(by_alias=True, exclude_none=True)["confidence"] == 80


def test_unrecorded_primitives_are_blank_not_zero_or_false():
    row = DataDiscovery._security_row(SPARSE)["properties"]
    assert row["cvssScore"] is None
    assert row["exploitAvailable"] is None
    assert row["patchAvailable"] is None
    assert row["findingType"] == "Vulnerability"


def test_real_values_are_kept():
    assert DataDiscovery._security_row(FULL)["properties"]["cvssScore"] == 10.0
    assert DataDiscovery._security_row(FULL)["properties"]["exploitAvailable"] is True
    assert DataDiscovery._security_row(FULL)["properties"]["packageUrl"].startswith("pkg:maven")
    # A 0.0 score is real when the severity says None.
    assert DataDiscovery._security_row(NONE_SCORE)["properties"]["cvssScore"] == 0.0


def test_posture_counts():
    report = {"guid": "r1", "displayName": "Run 1", "completionTime": "2026-10-01T00:00:00Z"}
    recorded = _annotation("SecurityPostureAnnotation", "p-1",
                           {"findingCountsBySeverity": {"High": 1}, "resourcesInScopeCount": 3,
                            "resourcesTestedCount": 0, "newFindingCount": 1}, report)
    row = DataDiscovery._security_row(recorded)["properties"]
    assert (row["criticalFindings"], row["highFindings"], row["lowFindings"]) == (0, 1, 0)
    assert row["resourcesInScopeCount"] == 3
    assert row["resourcesTestedCount"] == 0          # real: in scope was recorded
    assert row["reportName"] == "Run 1"

    unrecorded = _annotation("SecurityPostureAnnotation", "p-2",
                             {"resourcesInScopeCount": 0, "resourcesTestedCount": 0})
    row = DataDiscovery._security_row(unrecorded)["properties"]
    assert row["highFindings"] is None
    assert row["resourcesInScopeCount"] is None and row["resourcesTestedCount"] is None


def _client(monkeypatch, annotations):
    monkeypatch.setattr(DataDiscovery, "check_connection", lambda self: "test")
    client = DataDiscovery("view-server", "https://localhost:1", "user", "pwd")
    calls = []

    async def new_annotations(guid, **kwargs):
        calls.append(("report", guid))
        return annotations

    async def for_element(guid, **kwargs):
        calls.append(("element", guid))
        return annotations

    async def find(search, **kwargs):
        calls.append(("find", kwargs.get("metadata_element_type")))
        return annotations

    client._async_get_new_annotations = new_annotations
    client._async_get_annotations_for_element = for_element
    client._async_find_annotations = find
    return client, calls


REPORT_GUID = "9696d446-58fb-4bc0-a473-7ece72212671"


@pytest.mark.asyncio
async def test_findings_sorted_by_cvss_with_unrecorded_last(monkeypatch):
    client, calls = _client(monkeypatch, [SPARSE, PENTEST, OTHER, FULL])
    findings = await client._async_get_security_findings(report_guid=REPORT_GUID)
    assert calls == [("report", REPORT_GUID)]
    assert [f["elementHeader"]["guid"] for f in findings] == ["full-2", "pen-3", "sparse-1"]


@pytest.mark.asyncio
async def test_findings_filters(monkeypatch):
    client, calls = _client(monkeypatch, [SPARSE, PENTEST, FULL])
    high = await client._async_get_security_findings(element_guid=REPORT_GUID, min_severity="High")
    assert calls == [("element", REPORT_GUID)]
    assert [f["elementHeader"]["guid"] for f in high] == ["full-2", "pen-3"]
    pen = await client._async_get_security_findings(report_guid=REPORT_GUID,
                                                    finding_types=["PenetrationTestFindingAnnotation"])
    assert [f["elementHeader"]["guid"] for f in pen] == ["pen-3"]


@pytest.mark.asyncio
async def test_findings_argument_checks(monkeypatch):
    client, _ = _client(monkeypatch, [])
    with pytest.raises(ValueError):
        await client._async_get_security_findings()
    with pytest.raises(ValueError):
        await client._async_get_security_findings(report_guid=REPORT_GUID, element_guid=REPORT_GUID)
    with pytest.raises(ValueError):
        await client._async_get_security_findings(report_guid=REPORT_GUID, min_severity="Severe")


@pytest.mark.asyncio
async def test_posture_history_oldest_first_and_prefix(monkeypatch):
    later = _annotation("SecurityPostureAnnotation", "p-1", {},
                        {"guid": "r2", "qualifiedName": "SurveyReport::Portal::Q2", "completionTime": "2027-01-16"})
    earlier = _annotation("SecurityPostureAnnotation", "p-2", {},
                          {"guid": "r1", "qualifiedName": "SurveyReport::Portal::Q1", "completionTime": "2026-10-16"})
    other = _annotation("SecurityPostureAnnotation", "p-3", {},
                        {"guid": "r3", "qualifiedName": "SurveyReport::Other::Q1", "completionTime": "2026-01-01"})
    client, calls = _client(monkeypatch, [later, other, earlier])
    history = await client._async_get_security_posture_history("SurveyReport::Portal::")
    assert calls == [("find", "SecurityPostureAnnotation")]
    assert [p["elementHeader"]["guid"] for p in history] == ["p-2", "p-1"]
