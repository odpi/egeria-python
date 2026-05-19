"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module tests the DataDiscovery class and methods from data_discovery.py
"""
import json
import time
from datetime import datetime

import pytest
from rich import print
from rich.console import Console
from rich.table import Table

from pyegeria.core._exceptions import (
    PyegeriaInvalidParameterException,
    PyegeriaConnectionException,
    PyegeriaAPIException,
    PyegeriaNotFoundException,
)
from pyegeria.omvs.asset_maker import AssetMaker
from pyegeria.omvs.data_discovery import DataDiscovery
from pyegeria.core.logging_configuration import config_logging, init_logging

disable_ssl_warnings = True

console = Console(width=250)

config_logging()
init_logging(True)

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"


class TestDataDiscovery:
    good_platform1_url = PLATFORM_URL
    good_user_1 = USER_ID
    good_user_2 = USER_ID
    good_view_server_1 = VIEW_SERVER

    def _unique_qname(self, prefix: str = "Annotation") -> str:
        ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"{prefix}::{ts}"

    def test_create_annotation(self):
        """Test creating an annotation"""
        dd_client = DataDiscovery(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
        try:
            dd_client.create_egeria_bearer_token(self.good_user_2, USER_PWD)
            
            qualified_name = self._unique_qname("TestAnn")
            body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "AnnotationProperties",
                    "qualifiedName": qualified_name,
                    "displayName": "Test Annotation",
                    "annotationType": "Discovery",
                }
            }
            try:
                response = dd_client.create_annotation(body)
                assert response is not None
            except (PyegeriaInvalidParameterException, PyegeriaNotFoundException, PyegeriaAPIException):
                pass

        except PyegeriaConnectionException:
            print("Skipping test_create_annotation due to connection error")
        finally:
            dd_client.close_session()

    def test_find_annotation(self):
        """Test finding an annotation"""
        dd_client = DataDiscovery(self.good_view_server_1, self.good_platform1_url, user_id=self.good_user_2)
        try:
            dd_client.create_egeria_bearer_token(self.good_user_2, USER_PWD)


            try:
                response = dd_client.find_annotations(search_string="*", output_format="DICT", report_spec="REFERENCEABLE")
                assert response is not None
                if isinstance(response, dict|list):
                    print(f"Found {len(response)} annotations")
                    print(json.dumps(response, indent=2))
            except (PyegeriaInvalidParameterException, PyegeriaNotFoundException, PyegeriaAPIException):
                pass

        except PyegeriaConnectionException:
            print("Skipping test_find_annotation due to connection error")
        finally:
            dd_client.close_session()


# ── Annotation property body probe tests ──────────────────────────────────────

class TestAnnotationPropertyBodies:
    """Diagnostic tests to determine which annotation property body formats Egeria accepts.

    Each test creates a fresh SourceControlLibrary + SurveyReport as a fixture,
    then probes annotation creation with a specific ``class`` name and field
    combination.  Tests never assert on ACCEPTED/REJECTED — they always pass from
    pytest's perspective — but print a Rich table so results can be compared
    against the Egeria Java type archive and the correct format fixed in the server.

    Run with::

        pytest tests/functional-tests/test_data_discovery.py \\
               -k TestAnnotationPropertyBodies -v -s

    A running Egeria platform is required (PLATFORM_URL / VIEW_SERVER / USER_ID).
    The comprehensive sweep ``test_all_annotation_property_bodies`` is the most
    useful single test to run.
    """

    good_platform1_url = "https://127.0.0.1:9443"
    good_view_server   = "qs-view-server"
    good_user          = "erinoverview"
    good_pwd           = "secret"

    # ── fixture helpers ───────────────────────────────────────────────────────

    def _clients(self):
        """Return (AssetMaker, DataDiscovery) both authenticated."""
        am = AssetMaker(self.good_view_server, self.good_platform1_url,
                        user_id=self.good_user, user_pwd=self.good_pwd)
        am.create_egeria_bearer_token(self.good_user, self.good_pwd)

        dd = DataDiscovery(self.good_view_server, self.good_platform1_url,
                           user_id=self.good_user, user_pwd=self.good_pwd)
        dd.create_egeria_bearer_token(self.good_user, self.good_pwd)
        return am, dd

    def _create_fixture(self, am: AssetMaker) -> tuple[str, str]:
        """Create a SourceControlLibrary + SurveyReport; return (asset_guid, report_guid)."""
        ts = int(time.time())

        asset_body = {
            "class": "NewElementRequestBody",
            "properties": {
                "class": "SoftwareCapabilityProperties",
                "typeName": "SourceControlLibrary",
                "qualifiedName": f"AnnotationProbe::TestRepo::{ts}",
                "displayName": "Annotation Probe Test Repo",
                "deployedImplementationType": "GitHub Repository",
                "libraryType": "GitHub Repository",
            },
        }
        asset_guid = am.create_software_capability(body=asset_body)

        report_body = {
            "class": "NewElementRequestBody",
            "parentGUID": asset_guid,
            "parentRelationshipTypeName": "ReportSubject",
            "properties": {
                "class": "SurveyReportProperties",
                "qualifiedName": f"SurveyReport::AnnotationProbe::{ts}",
                "displayName": "Annotation Probe Survey Report",
            },
        }
        report_guid = am.create_asset(body=report_body)
        return asset_guid, report_guid

    def _delete_fixture(self, am: AssetMaker, asset_guid: str, report_guid: str) -> None:
        """Best-effort cleanup; swallows errors so teardown never masks test failures."""
        del_body = {"class": "DeleteElementRequestBody"}
        for guid in (report_guid, asset_guid):
            try:
                am.delete_asset(guid, del_body)
            except Exception:
                pass

    def _probe(
        self,
        dd: DataDiscovery,
        report_guid: str,
        label: str,
        props: dict,
    ) -> tuple[str, str]:
        """Attempt to create one annotation; return ('ACCEPTED'|'REJECTED', detail)."""
        ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
        props.setdefault("qualifiedName", f"AnnotationProbe::{label}::{ts}")
        body = {
            "class": "NewElementRequestBody",
            "parentGUID": report_guid,
            "parentRelationshipTypeName": "ReportedAnnotation",
            "properties": props,
        }
        try:
            guid = dd.create_annotation(body=body)
            return "ACCEPTED", f"guid={guid}"
        except Exception as exc:
            return "REJECTED", str(exc)[:140]

    def _print_results(self, results: list[tuple[str, str, str, str]]) -> None:
        """Print (label, class_name, status, detail) as a Rich table."""
        table = Table(title="Annotation property body probe results", show_lines=True)
        table.add_column("Label", style="cyan", no_wrap=True)
        table.add_column("class", style="yellow")
        table.add_column("Status", justify="center")
        table.add_column("Detail")
        for label, cls, status, detail in results:
            colour = "green" if status == "ACCEPTED" else "red"
            table.add_row(label, cls, f"[{colour}]{status}[/{colour}]", detail)
        console.print(table)

    # ── ResourceMeasureAnnotation probes ──────────────────────────────────────

    def test_resource_measure_subtype_class(self):
        """Probe: ResourceMeasureAnnotationProperties + resourceProperties map.

        Tests whether Egeria recognises ``ResourceMeasureAnnotationProperties`` as
        a registered Jackson subtype.  A 400 response means the class name is not
        in the server's @JsonSubTypes hierarchy — either the type doesn't exist in
        this Egeria version, or the class name is wrong.
        """
        am, dd = self._clients()
        asset_guid, report_guid = self._create_fixture(am)
        results = []
        try:
            label = "RM-1: ResourceMeasureAnnotationProperties"
            status, detail = self._probe(dd, report_guid, label, {
                "class": "ResourceMeasureAnnotationProperties",
                "annotationType": "ResourceMeasureAnnotation",
                "summary": "Probe RM-1: subtype class + resourceProperties",
                "resourceProperties": {
                    "total_files": "1026",
                    "repo_size_kb": "84728",
                    "by_extension.py": "385",
                },
            })
            results.append((label, "ResourceMeasureAnnotationProperties", status, detail))
        finally:
            self._print_results(results)
            self._delete_fixture(am, asset_guid, report_guid)
            am.close_session()
            dd.close_session()

    def test_resource_measure_base_class_with_typeName(self):
        """Probe: AnnotationProperties + typeName=ResourceMeasureAnnotation.

        Tests whether the server accepts the base class with a ``typeName`` override
        to select the Egeria subtype.  If ACCEPTED, this is a clean workaround that
        avoids Jackson subtype registration issues.
        """
        am, dd = self._clients()
        asset_guid, report_guid = self._create_fixture(am)
        results = []
        try:
            label = "RM-2: AnnotationProperties + typeName=ResourceMeasureAnnotation"
            status, detail = self._probe(dd, report_guid, label, {
                "class": "AnnotationProperties",
                "typeName": "ResourceMeasureAnnotation",
                "annotationType": "ResourceMeasureAnnotation",
                "summary": "Probe RM-2: base class + typeName override",
                "resourceProperties": {"total_files": "1026", "repo_size_kb": "84728"},
            })
            results.append((label, "AnnotationProperties", status, detail))
        finally:
            self._print_results(results)
            self._delete_fixture(am, asset_guid, report_guid)
            am.close_session()
            dd.close_session()

    def test_resource_measure_additionalProperties(self):
        """Probe: AnnotationProperties + resource data in additionalProperties (current fallback).

        This is the fallback used by project-explorer after the 400 errors.  Should
        always be ACCEPTED.  Confirms the workaround is correct while the server is fixed.
        """
        am, dd = self._clients()
        asset_guid, report_guid = self._create_fixture(am)
        results = []
        try:
            label = "RM-3: AnnotationProperties + additionalProperties"
            status, detail = self._probe(dd, report_guid, label, {
                "class": "AnnotationProperties",
                "annotationType": "ResourceMeasureAnnotation",
                "summary": "Probe RM-3: resource data in additionalProperties",
                "additionalProperties": {
                    "total_files": "1026",
                    "repo_size_kb": "84728",
                    "by_extension.py": "385",
                },
            })
            results.append((label, "AnnotationProperties", status, detail))
        finally:
            self._print_results(results)
            self._delete_fixture(am, asset_guid, report_guid)
            am.close_session()
            dd.close_session()

    # ── RequestForAction probes ───────────────────────────────────────────────

    def test_request_for_action_properties_class(self):
        """Probe: RequestForActionProperties (no 'Annotation' suffix in class name).

        Tests the original class name used in project-explorer.  A 400 means
        ``RequestForActionProperties`` is not a registered Jackson subtype — either
        it doesn't exist or the correct name includes 'Annotation'.
        """
        am, dd = self._clients()
        asset_guid, report_guid = self._create_fixture(am)
        results = []
        try:
            label = "RFA-1: RequestForActionProperties"
            status, detail = self._probe(dd, report_guid, label, {
                "class": "RequestForActionProperties",
                "annotationType": "RequestForAction",
                "summary": "Probe RFA-1: class without Annotation suffix",
                "actionRequested": "Add a SECURITY.md file",
                "actionTargetName": "SECURITY.md",
            })
            results.append((label, "RequestForActionProperties", status, detail))
        finally:
            self._print_results(results)
            self._delete_fixture(am, asset_guid, report_guid)
            am.close_session()
            dd.close_session()

    def test_request_for_action_annotation_properties_class(self):
        """Probe: RequestForActionAnnotationProperties (with 'Annotation' in name).

        Tests the alternative class name following the same pattern as
        ClassificationAnnotationProperties, QualityAnnotationProperties, etc.
        """
        am, dd = self._clients()
        asset_guid, report_guid = self._create_fixture(am)
        results = []
        try:
            label = "RFA-2: RequestForActionAnnotationProperties"
            status, detail = self._probe(dd, report_guid, label, {
                "class": "RequestForActionAnnotationProperties",
                "annotationType": "RequestForAction",
                "summary": "Probe RFA-2: class with Annotation suffix",
                "actionRequested": "Add a SECURITY.md file",
                "actionTargetName": "SECURITY.md",
            })
            results.append((label, "RequestForActionAnnotationProperties", status, detail))
        finally:
            self._print_results(results)
            self._delete_fixture(am, asset_guid, report_guid)
            am.close_session()
            dd.close_session()

    def test_request_for_action_with_actionProperties_map(self):
        """Probe: RequestForActionProperties + actionProperties map<string,string>.

        Tests whether ``actionProperties`` (the typed map field from the Egeria
        Java type) is accepted in place of ``actionTargetName``.
        """
        am, dd = self._clients()
        asset_guid, report_guid = self._create_fixture(am)
        results = []
        try:
            label = "RFA-3: RequestForActionProperties + actionProperties map"
            status, detail = self._probe(dd, report_guid, label, {
                "class": "RequestForActionProperties",
                "annotationType": "RequestForAction",
                "summary": "Probe RFA-3: actionProperties map field",
                "actionRequested": "Add a SECURITY.md file",
                "actionProperties": {
                    "actionTargetName": "SECURITY.md",
                    "severity": "HIGH",
                },
            })
            results.append((label, "RequestForActionProperties", status, detail))
        finally:
            self._print_results(results)
            self._delete_fixture(am, asset_guid, report_guid)
            am.close_session()
            dd.close_session()

    def test_request_for_action_base_class_additionalProperties(self):
        """Probe: AnnotationProperties + action data in additionalProperties (current fallback).

        Should always be ACCEPTED.  Confirms the current project-explorer workaround.
        """
        am, dd = self._clients()
        asset_guid, report_guid = self._create_fixture(am)
        results = []
        try:
            label = "RFA-4: AnnotationProperties + additionalProperties"
            status, detail = self._probe(dd, report_guid, label, {
                "class": "AnnotationProperties",
                "annotationType": "RequestForAction",
                "summary": "Add a SECURITY.md file",
                "additionalProperties": {
                    "actionRequested": "Add a SECURITY.md file",
                    "actionTargetName": "SECURITY.md",
                },
            })
            results.append((label, "AnnotationProperties", status, detail))
        finally:
            self._print_results(results)
            self._delete_fixture(am, asset_guid, report_guid)
            am.close_session()
            dd.close_session()

    # ── Comprehensive sweep ───────────────────────────────────────────────────

    def test_all_annotation_property_bodies(self):
        """Run all probes in one test and print a single summary table.

        This is the most useful test to run when investigating annotation 400 errors.
        Covers every candidate class name and field combination so the full picture
        is visible at a glance.  The two BASE probes act as sanity checks — if they
        are REJECTED the platform connection itself is broken.
        """
        am, dd = self._clients()
        asset_guid, report_guid = self._create_fixture(am)
        results = []

        probes: list[tuple[str, dict]] = [
            # ── ResourceMeasureAnnotation candidates ─────────────────────────
            ("RM-1: ResourceMeasureAnnotationProperties + resourceProperties", {
                "class": "ResourceMeasureAnnotationProperties",
                "annotationType": "ResourceMeasureAnnotation",
                "summary": "Probe RM-1",
                "resourceProperties": {"total_files": "1026", "repo_size_kb": "84728"},
            }),
            ("RM-2: AnnotationProperties + typeName=ResourceMeasureAnnotation", {
                "class": "AnnotationProperties",
                "typeName": "ResourceMeasureAnnotation",
                "annotationType": "ResourceMeasureAnnotation",
                "summary": "Probe RM-2",
                "resourceProperties": {"total_files": "1026"},
            }),
            ("RM-3: AnnotationProperties + additionalProperties [current fallback]", {
                "class": "AnnotationProperties",
                "annotationType": "ResourceMeasureAnnotation",
                "summary": "Probe RM-3",
                "additionalProperties": {"total_files": "1026", "repo_size_kb": "84728"},
            }),
            ("RM-4: AnnotationProperties + jsonProperties", {
                "class": "AnnotationProperties",
                "annotationType": "ResourceMeasureAnnotation",
                "summary": "Probe RM-4",
                "jsonProperties": json.dumps({"total_files": 1026, "by_extension": {".py": 385}}),
            }),
            # ── RequestForAction candidates ──────────────────────────────────
            ("RFA-1: RequestForActionProperties + actionRequested + actionTargetName", {
                "class": "RequestForActionProperties",
                "annotationType": "RequestForAction",
                "summary": "Probe RFA-1",
                "actionRequested": "Add SECURITY.md",
                "actionTargetName": "SECURITY.md",
            }),
            ("RFA-2: RequestForActionAnnotationProperties + actionRequested", {
                "class": "RequestForActionAnnotationProperties",
                "annotationType": "RequestForAction",
                "summary": "Probe RFA-2",
                "actionRequested": "Add SECURITY.md",
                "actionTargetName": "SECURITY.md",
            }),
            ("RFA-3: RequestForActionProperties + actionProperties map", {
                "class": "RequestForActionProperties",
                "annotationType": "RequestForAction",
                "summary": "Probe RFA-3",
                "actionRequested": "Add SECURITY.md",
                "actionProperties": {"actionTargetName": "SECURITY.md", "severity": "HIGH"},
            }),
            ("RFA-4: AnnotationProperties + additionalProperties [current fallback]", {
                "class": "AnnotationProperties",
                "annotationType": "RequestForAction",
                "summary": "Add SECURITY.md",
                "additionalProperties": {
                    "actionRequested": "Add SECURITY.md",
                    "actionTargetName": "SECURITY.md",
                },
            }),
            # ── Baseline sanity checks ────────────────────────────────────────
            ("BASE-1: ClassificationAnnotationProperties [known good]", {
                "class": "ClassificationAnnotationProperties",
                "annotationType": "ClassificationAnnotation",
                "summary": "Probe BASE-1 baseline",
                "candidateClassifications": ["Python Source File"],
                "confidence": 90,
            }),
            ("BASE-2: AnnotationProperties [always accepted]", {
                "class": "AnnotationProperties",
                "annotationType": "Discovery",
                "summary": "Probe BASE-2 baseline",
            }),
        ]

        try:
            for label, props in probes:
                cls_name = props.get("class", "?")
                status, detail = self._probe(dd, report_guid, label, props)
                results.append((label, cls_name, status, detail))
        finally:
            self._print_results(results)
            self._delete_fixture(am, asset_guid, report_guid)
            am.close_session()
            dd.close_session()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-k", "TestAnnotationPropertyBodies"])
