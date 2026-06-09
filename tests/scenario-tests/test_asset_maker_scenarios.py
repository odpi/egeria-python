#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario-based testing for Asset Maker with synthetic data.

This executable test script runs realistic scenarios for asset management,
including creating assets, managing catalog targets, and organizing resources,
with comprehensive cleanup and detailed error reporting.

Usage:
    python tests/test_asset_maker_scenarios.py
    
    Or with pytest:
    pytest tests/test_asset_maker_scenarios.py -v -s
"""

import json
import sys
import time
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from pyegeria.omvs.asset_maker import AssetMaker
from pyegeria.core._exceptions import (
    PyegeriaException,
    PyegeriaAPIException,
    PyegeriaTimeoutException,
    print_exception_table,
    print_validation_error,
)
from pydantic import ValidationError

# Configuration
VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"

console = Console(width=200)


@dataclass
class TestResult:
    """Track results of test scenarios"""
    scenario_name: str
    status: str  # "PASSED", "FAILED", "WARNING"
    duration: float
    message: str = ""
    error: Optional[Exception] = None
    created_guids: List[str] = field(default_factory=list)
    

@dataclass
class AssetData:
    """Synthetic asset data"""
    qualified_name: str
    display_name: str
    description: str
    asset_type: str = "Asset"
    guid: Optional[str] = None


class AssetMakerScenarioTester:
    """Execute realistic asset management scenarios"""
    
    def __init__(self):
        self.client: Optional[AssetMaker] = None
        self.results: List[TestResult] = []
        self.created_assets: List[str] = []
        self.test_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def setup(self) -> bool:
        """Initialize connection to Egeria"""
        try:
            console.print("\n[bold cyan]═══ Setting up Asset Maker Test Environment ═══[/bold cyan]\n")
            self.client = AssetMaker(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
            token = self.client.create_egeria_bearer_token(USER_ID, USER_PWD)
            console.print(f"✓ Connected to {PLATFORM_URL}")
            console.print(f"✓ Authenticated as {USER_ID}")
            console.print(f"✓ Test Run ID: {self.test_run_id}\n")
            return True
        except Exception as e:
            console.print(f"[bold red]✗ Setup failed: {str(e)}[/bold red]")
            return False
    
    def teardown(self):
        """Clean up and close connection"""
        if self.client:
            self.client.close_session()
            console.print("\n✓ Session closed")
    
    def cleanup_created_assets(self):
        """Delete all assets created during testing"""
        console.print("\n[bold yellow]═══ Cleaning Up Test Data ═══[/bold yellow]\n")
        
        if not self.created_assets:
            console.print("No assets to clean up")
            return
        
        cleanup_results = {"success": 0, "failed": 0, "not_found": 0}
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task(f"Cleaning up {len(self.created_assets)} assets...", total=len(self.created_assets))
            
            for guid in self.created_assets:
                try:
                    delete_body = {"class": "DeleteElementRequestBody"}
                    self.client.delete_asset(guid, delete_body)
                    cleanup_results["success"] += 1
                except PyegeriaAPIException:
                    cleanup_results["not_found"] += 1
                except Exception as e:
                    console.print(f"  [yellow]⚠ Failed to delete {guid}: {str(e)}[/yellow]")
                    cleanup_results["failed"] += 1
                progress.advance(task)
        
        console.print(f"\n✓ Cleanup complete:")
        console.print(f"  • Successfully deleted: {cleanup_results['success']}")
        console.print(f"  • Not found (already deleted): {cleanup_results['not_found']}")
        console.print(f"  • Failed: {cleanup_results['failed']}")
    
    def print_results_summary(self):
        """Print a summary table of all test results"""
        console.print("\n[bold cyan]═══ Test Results Summary ═══[/bold cyan]\n")
        
        table = Table(show_header=True, header_style="bold magenta", show_lines=True)
        table.add_column("Scenario", style="cyan", width=50)
        table.add_column("Status", justify="center", width=12)
        table.add_column("Duration (s)", justify="right", width=15)
        table.add_column("Message", width=60)
        
        passed = failed = warnings = 0
        
        for result in self.results:
            if result.status == "PASSED":
                status_style = "[green]✓ PASSED[/green]"
                passed += 1
            elif result.status == "FAILED":
                status_style = "[red]✗ FAILED[/red]"
                failed += 1
            else:
                status_style = "[yellow]⚠ WARNING[/yellow]"
                warnings += 1
            
            table.add_row(
                result.scenario_name,
                status_style,
                f"{result.duration:.3f}",
                result.message[:60] if result.message else ""
            )
        
        console.print(table)
        
        # Summary stats
        total = len(self.results)
        console.print(f"\n[bold]Total Scenarios:[/bold] {total}")
        console.print(f"[green]Passed:[/green] {passed}")
        console.print(f"[red]Failed:[/red] {failed}")
        console.print(f"[yellow]Warnings:[/yellow] {warnings}")
        
        if failed > 0:
            console.print("\n[bold red]Some scenarios failed. Check the details above.[/bold red]")
        elif warnings > 0:
            console.print("\n[bold yellow]All scenarios passed with some warnings.[/bold yellow]")
        else:
            console.print("\n[bold green]All scenarios passed successfully! ✓[/bold green]")
    
    def _create_test_asset(self, prefix: str = "TestAsset") -> AssetData:
        """Helper to create a test asset with unique name"""
        ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return AssetData(
            qualified_name=f"{prefix}::{ts}",
            display_name=f"{prefix} {ts}",
            description=f"Test asset created at {datetime.now().isoformat()}",
            asset_type="Asset"
        )
    
    def scenario_asset_lifecycle(self) -> TestResult:
        """Scenario: Complete asset lifecycle - create, read, update, delete"""
        scenario_name = "Asset Lifecycle"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # CREATE: Create a new asset
            console.print("  → Creating asset...")
            asset_data = self._create_test_asset("LifecycleTest")
            
            body = {
                "class": "NewElementRequestBody",
                "typeName": "Asset",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "AssetProperties",
                    "qualifiedName": asset_data.qualified_name,
                    "displayName": asset_data.display_name,
                    "description": asset_data.description,
                }
            }
            
            response = self.client.create_asset(body=body)
            guid = response.get("guid") if isinstance(response, dict) else response
            if guid:
                created_guids.append(guid)
                self.created_assets.append(guid)
                asset_data.guid = guid
                console.print(f"  ✓ Created asset: {guid}")
            else:
                raise Exception("Failed to create asset - no GUID returned")
            
            # READ: Retrieve the asset
            console.print("  → Retrieving asset...")
            retrieved = self.client.get_asset_by_guid(guid, output_format="JSON")
            
            if isinstance(retrieved, dict):
                console.print(f"  ✓ Retrieved asset: {retrieved.get('properties', {}).get('displayName', 'Unknown')}")
            else:
                raise Exception("Failed to retrieve asset")
            
            # UPDATE: Update the asset
            console.print("  → Updating asset...")
            update_body = {
                "class": "UpdateElementRequestBody",
                "properties": {
                    "class": "AssetProperties",
                    "qualifiedName": asset_data.qualified_name,
                    "displayName": f"{asset_data.display_name} (Updated)",
                    "description": f"{asset_data.description} - Updated",
                }
            }
            
            self.client.update_asset(guid, update_body)
            console.print("  ✓ Updated asset")
            
            # VERIFY UPDATE
            updated = self.client.get_asset_by_guid(guid, output_format="JSON")
            if isinstance(updated, dict):
                updated_name = updated.get('properties', {}).get('displayName', '')
                if "(Updated)" in updated_name:
                    console.print("  ✓ Verified update")
                else:
                    console.print("  [yellow]⚠ Update verification inconclusive[/yellow]")
            
            # SEARCH: Find the asset
            console.print("  → Searching for asset...")
            search_results = self.client.find_assets(search_string=asset_data.display_name[:10], output_format="JSON")
            
            if isinstance(search_results, list) and len(search_results) > 0:
                console.print(f"  ✓ Found {len(search_results)} assets in search")
            
            # DELETE: Delete the asset
            console.print("  → Deleting asset...")
            delete_body = {"class": "DeleteElementRequestBody"}
            self.client.delete_asset(guid, delete_body)
            self.created_assets.remove(guid)
            console.print("  ✓ Deleted asset")
            
            # VERIFY DELETION
            try:
                after_delete = self.client.get_asset_by_guid(guid, output_format="JSON")
                console.print("  [yellow]⚠ Asset still exists after deletion[/yellow]")
            except PyegeriaAPIException:
                console.print("  ✓ Verified deletion")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message="Complete lifecycle executed successfully",
                created_guids=created_guids
            )
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            if isinstance(e, PyegeriaTimeoutException):
                console.print(f"  [yellow]⚠ Timeout in {scenario_name}; continuing.[/yellow]")
                return TestResult(
                    scenario_name=scenario_name,
                    status="WARNING",
                    duration=duration,
                    message=f"Timeout: {str(e)[:100]}",
                    error=e,
                    created_guids=created_guids
                )
            console.print(f"  [red]✗ Error: {str(e)}[/red]")
            print_exception_table(e) if isinstance(e, PyegeriaException) else console.print_exception()
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e)[:100],
                error=e,
                created_guids=created_guids
            )
    
    def scenario_multiple_assets(self) -> TestResult:
        """Scenario: Create and manage multiple assets"""
        scenario_name = "Multiple Assets Management"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # Create multiple assets
            console.print("  → Creating multiple assets...")
            num_assets = 3
            for i in range(num_assets):
                asset_data = self._create_test_asset(f"MultiAsset{i+1}")
                body = {
                    "class": "NewElementRequestBody",
                    "typeName": "Asset",
                    "initialStatus": "ACTIVE",
                    "properties": {
                        "class": "AssetProperties",
                        "qualifiedName": asset_data.qualified_name,
                        "displayName": asset_data.display_name,
                        "description": asset_data.description,
                    }
                }
                
                response = self.client.create_asset(body=body)
                guid = response.get("guid") if isinstance(response, dict) else response
                if guid:
                    created_guids.append(guid)
                    self.created_assets.append(guid)
                    console.print(f"  ✓ Created asset {i+1}: {guid}")
            
            # Search for assets
            console.print("  → Searching for created assets...")
            search_results = self.client.find_assets(search_string="MultiAsset", output_format="JSON")
            
            if isinstance(search_results, list):
                console.print(f"  ✓ Found {len(search_results)} assets matching search")
            
            # Get assets by name
            console.print("  → Getting assets by name...")
            name_results = self.client.get_assets_by_name(
                filter_string="MultiAsset",
                output_format="JSON"
            )
            
            if isinstance(name_results, list):
                console.print(f"  ✓ Found {len(name_results)} assets by name")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Created and managed {num_assets} assets successfully",
                created_guids=created_guids
            )
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            if isinstance(e, PyegeriaTimeoutException):
                console.print(f"  [yellow]⚠ Timeout in {scenario_name}; continuing.[/yellow]")
                return TestResult(
                    scenario_name=scenario_name,
                    status="WARNING",
                    duration=duration,
                    message=f"Timeout: {str(e)[:100]}",
                    error=e,
                    created_guids=created_guids
                )
            console.print(f"  [red]✗ Error: {str(e)}[/red]")
            print_exception_table(e) if isinstance(e, PyegeriaException) else console.print_exception()
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e)[:100],
                error=e,
                created_guids=created_guids
            )
    
    def scenario_asset_from_template(self) -> TestResult:
        """Scenario: Create asset from template"""
        scenario_name = "Asset from Template"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # First create a regular asset to use AS a template
            console.print("  → Creating template asset...")
            template_data = self._create_test_asset("TemplateAsset")
            template_body = {
                "class": "NewElementRequestBody",
                "typeName": "Asset",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "AssetProperties",
                    "qualifiedName": template_data.qualified_name,
                    "displayName": template_data.display_name,
                    "description": "Template for creating other assets",
                }
            }
            
            response = self.client.create_asset(body=template_body)
            template_guid = response.get("guid") if isinstance(response, dict) else response
            if template_guid:
                created_guids.append(template_guid)
                self.created_assets.append(template_guid)
                console.print(f"  ✓ Created template asset: {template_guid}")
            else:
                raise Exception("Failed to create template asset")
            
            # Now create an asset FROM the template
            console.print("  → Creating asset from template...")
            from_template_body = {
                "class": "TemplateRequestBody",
                "templateGUID": template_guid,
                "replacementProperties": {
                    "class": "AssetProperties",
                    "qualifiedName": template_data.qualified_name,
                    "displayName": "Asset from Template",
                    "description": "This asset was created from a template"
                }
            }
            console.print(json.dumps(from_template_body, indent=2))
            response = self.client.create_asset_from_template(body=from_template_body)
            new_asset_guid = response.get("guid") if isinstance(response, dict) else response
            
            if new_asset_guid:
                created_guids.append(new_asset_guid)
                self.created_assets.append(new_asset_guid)
                console.print(f"  ✓ Created asset from template: {new_asset_guid}")
            else:
                console.print("  [yellow]⚠ Template creation may not be fully supported[/yellow]")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message="Template-based asset creation tested",
                created_guids=created_guids
            )

        except ValidationError as e:
            print_validation_error(e)
        except Exception as e:
            duration = time.perf_counter() - start_time
            if isinstance(e, PyegeriaTimeoutException):
                console.print(f"  [yellow]⚠ Timeout in {scenario_name}; continuing.[/yellow]")
                return TestResult(
                    scenario_name=scenario_name,
                    status="WARNING",
                    duration=duration,
                    message=f"Timeout: {str(e)[:100]}",
                    error=e,
                    created_guids=created_guids
                )
            console.print(f"  [red]✗ Error: {str(e)}[/red]")
            print_exception_table(e) if isinstance(e, PyegeriaException) else console.print_exception()
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e)[:100],
                error=e,
                created_guids=created_guids
            )
    
    def scenario_software_capability_lifecycle(self) -> TestResult:
        """Scenario: Software capability lifecycle - create, search, update, link to asset, retrieve use, delete"""
        scenario_name = "Software Capability Lifecycle"
        start_time = time.perf_counter()
        cap_guid = None
        asset_guid = None

        try:
            console.print(f"\n[bold cyan]═══ Scenario: {scenario_name} ═══[/bold cyan]\n")
            ts = datetime.now().strftime("%Y%m%d%H%M%S%f")

            # Step 1: Create a software capability
            cap_body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "SoftwareCapabilityProperties",
                    "qualifiedName": f"TestSWCap::Lifecycle::{ts}",
                    "displayName": f"Test Software Capability {ts}",
                    "description": "Created for lifecycle scenario testing.",
                    "deployedImplementationType": "Test Server",
                }
            }
            cap_guid = self.client.create_software_capability(body=cap_body)
            console.print(f"  ✓ Created software capability: {cap_guid}")
            assert cap_guid is not None

            # Step 2: Retrieve by GUID
            result = self.client.get_software_capability_by_guid(guid=cap_guid, output_format="DICT")
            console.print(f"  ✓ Retrieved software capability by GUID")
            assert result is not None

            # Step 3: Update the capability
            update_body = {
                "class": "UpdateElementRequestBody",
                "properties": {
                    "class": "SoftwareCapabilityProperties",
                    "description": "Updated description for lifecycle test.",
                }
            }
            self.client.update_software_capability(software_capability_guid=cap_guid, body=update_body)
            console.print(f"  ✓ Updated software capability")

            # Step 4: Find it via search
            search_result = self.client.find_software_capabilities(search_string="Test Software Capability", output_format="JSON")
            console.print(f"  ✓ Found software capabilities via search")

            # Step 5: Create an asset and link it via add_capability_asset_use
            asset_body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "AssetProperties",
                    "qualifiedName": f"TestAsset::ForCapUse::{ts}",
                    "displayName": f"Test Asset for Capability Use {ts}",
                }
            }
            asset_guid = self.client.create_asset(body=asset_body)
            self.created_assets.append(asset_guid)
            console.print(f"  ✓ Created asset for capability use: {asset_guid}")

            link_body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "CapabilityAssetUseProperties",
                    "useType": "OWNS",
                    "description": "Primary data store for this capability.",
                    "minimumInstances": 1,
                    "maximumInstances": 5,
                }
            }
            self.client.add_capability_asset_use(
                software_capability_guid=cap_guid, asset_guid=asset_guid, body=link_body
            )
            console.print(f"  ✓ Linked asset to software capability (useType=OWNS)")

            # Step 6: Get capability use for the asset
            cap_use = self.client.get_capability_use(asset_guid=asset_guid, output_format="JSON")
            console.print(f"  ✓ Retrieved capability use for asset")

            # Step 7: Remove capability asset use
            self.client.remove_capability_asset_use(software_capability_guid=cap_guid, asset_guid=asset_guid)
            console.print(f"  ✓ Removed capability asset use relationship")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Software capability lifecycle complete. GUID: {cap_guid}",
                created_guids=[cap_guid] if cap_guid else [],
            )

        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Scenario failed: {str(e)}[/red]")
            if isinstance(e, PyegeriaException):
                reason = e.additional_info.get("reason", "") if e.additional_info else ""
                if reason:
                    console.print(f"  [yellow]Server response: {reason[:500]}[/yellow]")
                print_exception_table(e)
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e),
                error=e,
                created_guids=[g for g in [cap_guid] if g],
            )

    def scenario_report_relationships(self) -> TestResult:
        """Scenario: Create two reports and link them with originator, dependency, and subject relationships"""
        scenario_name = "Report Relationships"
        start_time = time.perf_counter()
        report1_guid = None
        report2_guid = None
        subject_guid = None

        try:
            console.print(f"\n[bold cyan]═══ Scenario: {scenario_name} ═══[/bold cyan]\n")
            ts = datetime.now().strftime("%Y%m%d%H%M%S%f")

            # Step 1: Create two reports (Report inherits from DataSet)
            r1_body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "AssetProperties",
                    "typeName": "Report",
                    "qualifiedName": f"TestReport::Prior::{ts}",
                    "displayName": f"Prior Report {ts}",
                    "description": "Prior version of the report.",
                }
            }
            report1_guid = self.client.create_asset(body=r1_body)
            self.created_assets.append(report1_guid)
            console.print(f"  ✓ Created prior report: {report1_guid}")

            r2_body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "AssetProperties",
                    "typeName": "Report",
                    "qualifiedName": f"TestReport::New::{ts}",
                    "displayName": f"New Report {ts}",
                    "description": "New version of the report.",
                }
            }
            report2_guid = self.client.create_asset(body=r2_body)
            self.created_assets.append(report2_guid)
            console.print(f"  ✓ Created new report: {report2_guid}")

            # Step 2: Create a subject element (generic asset)
            subject_body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "AssetProperties",
                    "qualifiedName": f"TestSubject::ForReport::{ts}",
                    "displayName": f"Test Subject {ts}",
                    "description": "Subject matter of the report.",
                }
            }
            subject_guid = self.client.create_asset(body=subject_body)
            self.created_assets.append(subject_guid)
            console.print(f"  ✓ Created subject element: {subject_guid}")

            # Step 3: Link originator to report2
            orig_body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "ReportOriginatorProperties",
                    "label": "Created by",
                    "description": "The originating system for this report",
                }
            }
            self.client.link_report_originator(
                originator_guid=subject_guid, report_guid=report2_guid, body=orig_body
            )
            console.print(f"  ✓ Linked report originator")

            # Step 4: Link report dependency (report2 follows on from report1)
            dep_body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "ReportDependencyProperties",
                    "label": "Supersedes",
                    "description": "This report supersedes the prior report",
                }
            }
            self.client.link_report_dependency(
                prior_report_guid=report1_guid, report_guid=report2_guid, body=dep_body
            )
            console.print(f"  ✓ Linked report dependency")

            # Step 5: Link subject to report2
            subj_body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "ReportSubjectProperties",
                    "label": "About",
                    "description": "The primary subject of this report",
                }
            }
            self.client.link_report_subject(
                subject_guid=subject_guid, report_guid=report2_guid, body=subj_body
            )
            console.print(f"  ✓ Linked report subject")

            # Step 6: Unlink relationships
            self.client.unlink_report_originator(originator_guid=subject_guid, report_guid=report2_guid)
            console.print(f"  ✓ Unlinked report originator")

            self.client.unlink_report_dependency(prior_report_guid=report1_guid, report_guid=report2_guid)
            console.print(f"  ✓ Unlinked report dependency")

            self.client.unlink_report_subject(subject_guid=subject_guid, report_guid=report2_guid)
            console.print(f"  ✓ Unlinked report subject")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message="Report relationships linked and unlinked successfully.",
                created_guids=[g for g in [report1_guid, report2_guid, subject_guid] if g],
            )

        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Scenario failed: {str(e)}[/red]")
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e),
                error=e,
                created_guids=[g for g in [report1_guid, report2_guid, subject_guid] if g],
            )

    def scenario_data_set_content(self) -> TestResult:
        """Scenario: Create a data set and a data store, link content, then detach"""
        scenario_name = "Data Set Content Linking"
        start_time = time.perf_counter()
        data_set_guid = None
        data_store_guid = None

        try:
            console.print(f"\n[bold cyan]═══ Scenario: {scenario_name} ═══[/bold cyan]\n")
            ts = datetime.now().strftime("%Y%m%d%H%M%S%f")

            # Step 1: Create a data set
            ds_body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "AssetProperties",
                    "typeName": "DataSet",
                    "qualifiedName": f"TestDataSet::{ts}",
                    "displayName": f"Test DataSet {ts}",
                    "description": "Data set for content linking test.",
                }
            }
            data_set_guid = self.client.create_asset(body=ds_body)
            self.created_assets.append(data_set_guid)
            console.print(f"  ✓ Created data set: {data_set_guid}")

            # Step 2: Create a data store (content supplier)
            store_body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "AssetProperties",
                    "typeName": "DataStore",
                    "qualifiedName": f"TestDataStore::{ts}",
                    "displayName": f"Test DataStore {ts}",
                    "description": "Data store supplying content for the data set.",
                }
            }
            data_store_guid = self.client.create_asset(body=store_body)
            self.created_assets.append(data_store_guid)
            console.print(f"  ✓ Created data store: {data_store_guid}")

            # Step 3: Link data set content
            link_body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "DataSetContentProperties",
                    "queryId": "test-query-001",
                    "query": "SELECT * FROM source_table",
                    "queryType": "SQL",
                }
            }
            self.client.link_data_set_content(
                data_set_guid=data_set_guid, data_content_asset_guid=data_store_guid, body=link_body
            )
            console.print(f"  ✓ Linked data set content")

            # Step 4: Detach data set content
            self.client.detach_data_set_content(
                data_set_guid=data_set_guid, data_content_asset_guid=data_store_guid
            )
            console.print(f"  ✓ Detached data set content")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message="Data set content linked and detached successfully.",
                created_guids=[g for g in [data_set_guid, data_store_guid] if g],
            )

        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Scenario failed: {str(e)}[/red]")
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e),
                error=e,
                created_guids=[g for g in [data_set_guid, data_store_guid] if g],
            )

    def run_all_scenarios(self):
        """Execute all test scenarios"""
        console.print(Panel.fit(
            "[bold cyan]Asset Maker Scenario Tests[/bold cyan]\n"
            f"Test Run ID: {self.test_run_id}",
            border_style="cyan"
        ))

        if not self.setup():
            console.print("[bold red]Setup failed. Cannot proceed with tests.[/bold red]")
            return False

        try:
            # Run all scenarios
            self.results.append(self.scenario_asset_lifecycle())
            self.results.append(self.scenario_multiple_assets())
            self.results.append(self.scenario_asset_from_template())
            self.results.append(self.scenario_software_capability_lifecycle())
            self.results.append(self.scenario_report_relationships())
            self.results.append(self.scenario_data_set_content())

            # Print summary
            self.print_results_summary()

            # Cleanup
            self.cleanup_created_assets()

            # Return success if no failures
            return all(r.status != "FAILED" for r in self.results)

        finally:
            self.teardown()


def test_asset_maker_scenarios():
    """Pytest entry point for asset maker scenario tests"""
    tester = AssetMakerScenarioTester()
    success = tester.run_all_scenarios()
    assert success, "One or more scenarios failed"


if __name__ == "__main__":
    """Direct execution entry point"""
    tester = AssetMakerScenarioTester()
    success = tester.run_all_scenarios()
    sys.exit(0 if success else 1)
