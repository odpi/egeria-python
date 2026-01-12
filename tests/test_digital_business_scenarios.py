#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario-based testing for Digital Business with synthetic data.

This executable test script runs realistic scenarios for digital business management,
including linking business capabilities, managing digital support, and business significance,
with comprehensive cleanup and detailed error reporting.

Usage:
    python tests/test_digital_business_scenarios.py
    
    Or with pytest:
    pytest tests/test_digital_business_scenarios.py -v -s
"""

import sys
import time
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from pyegeria.omvs.digital_business import DigitalBusiness
from pyegeria.core._exceptions import (
    PyegeriaException,
    PyegeriaNotFoundException,
    print_exception_table,
)

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


class DigitalBusinessScenarioTester:
    """Execute realistic digital business management scenarios"""
    
    def __init__(self):
        self.client: Optional[DigitalBusiness] = None
        self.results: List[TestResult] = []
        self.created_capabilities: List[str] = []
        self.test_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def setup(self) -> bool:
        """Initialize connection to Egeria"""
        try:
            console.print("\n[bold cyan]═══ Setting up Digital Business Test Environment ═══[/bold cyan]\n")
            self.client = DigitalBusiness(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
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
    
    def cleanup_created_capabilities(self):
        """Delete all capabilities created during testing"""
        console.print("\n[bold yellow]═══ Cleaning Up Test Data ═══[/bold yellow]\n")
        
        if not self.created_capabilities:
            console.print("No capabilities to clean up")
            return
        
        cleanup_results = {"success": 0, "failed": 0, "not_found": 0}
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task(f"Cleaning up {len(self.created_capabilities)} capabilities...", total=len(self.created_capabilities))
            
            for guid in self.created_capabilities:
                try:
                    self.client.delete_business_capability(guid)
                    cleanup_results["success"] += 1
                except PyegeriaNotFoundException:
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
    
    def scenario_business_capability_dependency(self) -> TestResult:
        """Scenario: Link and unlink business capability dependencies"""
        scenario_name = "Business Capability Dependency Management"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # CREATE: Create two business capabilities for testing dependency
            console.print("  → Creating business capabilities for dependency test...")
            ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
            
            # Create first capability (the one that depends on another)
            body1 = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "BusinessCapabilityProperties",
                    "qualifiedName": f"BusinessCapability::DependentCapability::{ts}",
                    "displayName": f"Dependent Capability {ts}",
                    "description": "Business capability that depends on another",
                    "identifier": f"BC-DEP-{ts}",
                    "businessCapabilityType": 1
                }
            }
            
            capability_guid = self.client.create_business_capability(body1)
            if capability_guid:
                created_guids.append(capability_guid)
                self.created_capabilities.append(capability_guid)
                console.print(f"  ✓ Created dependent capability: {capability_guid}")
            else:
                raise Exception("Failed to create dependent capability")
            
            # Create second capability (the supporting one)
            body2 = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "BusinessCapabilityProperties",
                    "qualifiedName": f"BusinessCapability::SupportingCapability::{ts}",
                    "displayName": f"Supporting Capability {ts}",
                    "description": "Business capability that supports another",
                    "identifier": f"BC-SUP-{ts}",
                    "businessCapabilityType": 2
                }
            }
            
            supporting_guid = self.client.create_business_capability(body2)
            if supporting_guid:
                created_guids.append(supporting_guid)
                self.created_capabilities.append(supporting_guid)
                console.print(f"  ✓ Created supporting capability: {supporting_guid}")
            else:
                raise Exception("Failed to create supporting capability")
            
            # LINK: Link the dependency relationship
            console.print("  → Linking business capability dependency...")
            dependency_body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "BusinessCapabilityDependencyProperties",
                    "label": "Test Dependency",
                    "description": "Test dependency relationship"
                }
            }
            
            self.client.link_business_capability_dependency(
                capability_guid, supporting_guid, dependency_body
            )
            console.print("  ✓ Linked business capability dependency")
            
            # DETACH: Remove the dependency relationship
            console.print("  → Detaching business capability dependency...")
            body = {"class":"DeleteRelationshipRequestBody"}
            self.client.detach_business_capability_dependency(
                capability_guid, supporting_guid, body
            )
            console.print("  ✓ Detached business capability dependency")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Successfully tested dependency linking with {len(created_guids)} capabilities",
                created_guids=created_guids
            )
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Error: {str(e)}[/red]")
            print_exception_table(e) if isinstance(e, PyegeriaException) else console.print_exception()
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e)[:100],
                error=e
            )
    
    def scenario_digital_support(self) -> TestResult:
        """Scenario: Link and unlink digital support to business capabilities"""
        scenario_name = "Digital Support Management"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # CREATE: Create a business capability and another element for digital support
            console.print("  → Creating business capability for digital support test...")
            ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
            
            # Create business capability
            capability_body = {
                "class": "NewElementRequestBody",
                "typeName": "BusinessCapability",
                "properties": {
                    "class": "BusinessCapabilityProperties",
                    "qualifiedName": f"BusinessCapability::DigitalSupportTest::{ts}",
                    "displayName": f"Digital Support Test Capability {ts}",
                    "description": "Business capability for digital support testing",
                    "identifier": f"BC-DS-{ts}",
                    "businessCapabilityType": 1
                }
            }
            
            capability_guid = self.client.create_business_capability(capability_body)
            if capability_guid:
                created_guids.append(capability_guid)
                self.created_capabilities.append(capability_guid)
                console.print(f"  ✓ Created business capability: {capability_guid}")
            else:
                raise Exception("Failed to create business capability")
            
            # Create another business capability to act as the digital support element
            element_body = {
                "class": "NewElementRequestBody",
                "typeName": "BusinessCapability",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "BusinessCapabilityProperties",
                    "qualifiedName": f"BusinessCapability::DigitalSupportElement::{ts}",
                    "displayName": f"Digital Support Element {ts}",
                    "description": "Element providing digital support",
                    "identifier": f"BC-DSE-{ts}",
                    "businessCapabilityType": 2
                }
            }
            
            element_guid = self.client.create_business_capability(element_body)
            if element_guid:
                created_guids.append(element_guid)
                self.created_capabilities.append(element_guid)
                console.print(f"  ✓ Created digital support element: {element_guid}")
            else:
                raise Exception("Failed to create digital support element")
            
            # LINK: Link digital support
            console.print("  → Linking digital support...")
            support_body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "DigitalSupportProperties",
                    "label": "Test Digital Support",
                    "description": "Test digital support relationship"
                }
            }
            
            self.client.link_digital_support(capability_guid, element_guid, support_body)
            console.print("  ✓ Linked digital support")
            
            # DETACH: Remove digital support
            console.print("  → Detaching digital support...")
            body = {"class":"DeleteRelationshipRequestBody"}
            self.client.detach_digital_support(capability_guid, element_guid, body=body)
            console.print("  ✓ Detached digital support")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Successfully tested digital support with {len(created_guids)} elements",
                created_guids=created_guids
            )
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Error: {str(e)}[/red]")
            print_exception_table(e) if isinstance(e, PyegeriaException) else console.print_exception()
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e)[:100],
                error=e
            )
    
    def scenario_business_significance(self) -> TestResult:
        """Scenario: Set and clear business significance classification"""
        scenario_name = "Business Significance Classification"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # CREATE: Create a business capability for significance testing
            console.print("  → Creating business capability for significance test...")
            ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
            
            element_body = {
                "class": "NewElementRequestBody",
                "typeName": "BusinessCapability",
                "properties": {
                    "class": "BusinessCapabilityProperties",
                    "qualifiedName": f"BusinessCapability::SignificanceTest::{ts}",
                    "displayName": f"Significance Test Capability {ts}",
                    "description": "Business capability for significance testing",
                    "identifier": f"BC-SIG-{ts}",
                    "businessCapabilityType": 1
                }
            }
            
            element_guid = self.client.create_business_capability(element_body)
            if element_guid:
                created_guids.append(element_guid)
                self.created_capabilities.append(element_guid)
                console.print(f"  ✓ Created business capability: {element_guid}")
            else:
                raise Exception("Failed to create business capability")
            
            # SET: Set business significance classification
            console.print("  → Setting business significance...")
            significance_body = {
                "class": "NewClassificationRequestBody",
                "properties": {
                    "class": "BusinessSignificantProperties",
                    "subjectAreaName": "Test Subject Area"
                }
            }
            
            self.client.set_business_significant(element_guid, significance_body)
            console.print("  ✓ Set business significance")
            
            # CLEAR: Remove business significance classification
            console.print("  → Clearing business significance...")
            self.client.clear_business_significance(element_guid)
            console.print("  ✓ Cleared business significance")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Successfully tested business significance with {len(created_guids)} element",
                created_guids=created_guids
            )
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Error: {str(e)}[/red]")
            print_exception_table(e) if isinstance(e, PyegeriaException) else console.print_exception()
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e)[:100],
                error=e
            )
    
    def scenario_business_capability_lifecycle(self) -> TestResult:
        """Scenario: Complete business capability lifecycle - create, update, delete"""
        scenario_name = "Business Capability Lifecycle"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # CREATE: Create a new business capability
            console.print("  → Creating business capability...")
            ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
            
            body = {
                "class": "NewElementRequestBody",
                "typeName": "BusinessCapability",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "BusinessCapabilityProperties",
                    "qualifiedName": f"BusinessCapability::CapabilityTest::{ts}",
                    "displayName": f"Test Business Capability {ts}",
                    "description": f"Test business capability created at {datetime.now().isoformat()}",
                    "identifier": f"BC-{ts}",
                    "businessCapabilityType": 1
                }
            }
            
            guid = self.client.create_business_capability(body)
            
            if guid:
                created_guids.append(guid)
                self.created_capabilities.append(guid)
                console.print(f"  ✓ Created business capability: {guid}")
            else:
                raise Exception("Failed to create business capability - no GUID returned")
            
            # UPDATE: Update the business capability
            console.print("  → Updating business capability...")
            update_body = {
                "class": "UpdateElementRequestBody",
                "properties": {
                    "class": "BusinessCapabilityProperties",
                    "qualifiedName": f"BusinessCapability::CapabilityTest::{ts}",
                    "displayName": f"Test Business Capability {ts} (Updated)",
                    "description": f"Test business capability - Updated",
                    "businessCapabilityType": 2
                }
            }
            
            self.client.update_business_capability(guid, update_body)
            console.print("  ✓ Updated business capability")
            
            # RETRIEVE: Get the capability by GUID
            console.print("  → Retrieving business capability by GUID...")
            capability = self.client.get_business_capability_by_guid(guid)
            if capability:
                console.print(f"  ✓ Retrieved capability by GUID")
            
            # DELETE: Delete the capability
            console.print("  → Deleting business capability...")
            self.client.delete_business_capability(guid)
            console.print(f"  ✓ Deleted capability: {guid}")
            created_guids.remove(guid)  # Remove from tracking since we deleted it
            self.created_capabilities.remove(guid)
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message="Business capability lifecycle executed successfully",
                created_guids=created_guids
            )
            
        except Exception as e:
            duration = time.perf_counter() - start_time
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
    
    def scenario_retrieve_business_capabilities(self) -> TestResult:
        """Scenario: Test retrieval methods for business capabilities - get by GUID, get by name, find"""
        scenario_name = "Business Capability Retrieval Methods"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # CREATE: Create test capabilities for retrieval
            console.print("  → Creating test capabilities for retrieval...")
            capability_names = ["CapabilityAlpha", "CapabilityBeta", "CapabilityGamma"]
            
            for name in capability_names:
                ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
                body = {
                    "class": "NewElementRequestBody",
                    "typeName": "BusinessCapability",
                    "initialStatus": "ACTIVE",
                    "properties": {
                        "class": "BusinessCapabilityProperties",
                        "qualifiedName": f"BusinessCapability::RetrievalTest_{name}::{ts}",
                        "displayName": f"RetrievalTest {name} {ts}",
                        "description": f"Test capability for retrieval - {name}",
                        "identifier": f"BC-{name}-{ts}"
                    }
                }
                
                guid = self.client.create_business_capability(body)
                if guid:
                    created_guids.append(guid)
                    self.created_capabilities.append(guid)
                    console.print(f"  ✓ Created capability: {name} ({guid})")
                time.sleep(0.1)  # Small delay between creates
            
            # TEST 1: Get by GUID
            console.print("\n  → Testing get_business_capability_by_guid...")
            if created_guids:
                test_guid = created_guids[0]
                capability = self.client.get_business_capability_by_guid(test_guid)
                if capability:
                    console.print(f"  ✓ Retrieved capability by GUID: {test_guid}")
                else:
                    console.print(f"  [yellow]⚠ No capability found for GUID: {test_guid}[/yellow]")
            
            # TEST 2: Get by name (using filter string)
            console.print("\n  → Testing get_business_capabilities_by_name...")
            capabilities = self.client.get_business_capabilities_by_name(filter_string="RetrievalTest")
            if capabilities:
                console.print(f"  ✓ Found {len(capabilities)} capabilities with filter 'RetrievalTest'")
                for cap in capabilities[:3]:  # Show first 3
                    if isinstance(cap, dict):
                        name = cap.get('elementHeader', {}).get('properties', {}).get('displayName', 'N/A')
                        guid = cap.get('elementHeader', {}).get('guid', 'N/A')
                        console.print(f"    - {name} ({guid})")
            else:
                console.print("  [yellow]⚠ No capabilities found by name[/yellow]")
            
            # TEST 3: Find capabilities (search)
            console.print("\n  → Testing find_business_capabilities...")
            found_capabilities = self.client.find_business_capabilities(search_string="CapabilityAlpha",
                                                                        starts_with=False)
            if found_capabilities:
                console.print(f"  ✓ Found {len(found_capabilities)} capabilities matching 'CapabilityAlpha'")
                for cap in found_capabilities[:3]:  # Show first 3
                    if isinstance(cap, dict):
                        name = cap.get('elementHeader', {}).get('properties', {}).get('displayName', 'N/A')
                        guid = cap.get('elementHeader', {}).get('guid', 'N/A')
                        console.print(f"    - {name} ({guid})")
            else:
                console.print("  [yellow]⚠ No capabilities found by search[/yellow]")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Successfully tested retrieval methods with {len(created_guids)} capabilities",
                created_guids=created_guids
            )
            
        except Exception as e:
            duration = time.perf_counter() - start_time
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
    
    def run_all_scenarios(self):
        """Execute all test scenarios"""
        console.print("\n[bold magenta]═══ Running Digital Business Scenarios ═══[/bold magenta]")
        
        scenarios = [
            self.scenario_business_capability_lifecycle,
            self.scenario_retrieve_business_capabilities,
            self.scenario_business_capability_dependency,
            self.scenario_digital_support,
            self.scenario_business_significance,
        ]
        
        for scenario_func in scenarios:
            result = scenario_func()
            self.results.append(result)
            time.sleep(0.5)  # Brief pause between scenarios


def test_digital_business_scenarios():
    """Pytest entry point for digital business scenario tests"""
    exit_code = main()
    assert exit_code == 0, "One or more scenarios failed"


def main():
    """Main test execution"""
    tester = DigitalBusinessScenarioTester()
    
    try:
        if not tester.setup():
            console.print("[bold red]Setup failed. Exiting.[/bold red]")
            return 1
        
        tester.run_all_scenarios()
        tester.print_results_summary()
        tester.cleanup_created_capabilities()
        
        # Return exit code based on results
        failed_count = sum(1 for r in tester.results if r.status == "FAILED")
        return 1 if failed_count > 0 else 0
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Test execution interrupted by user[/yellow]")
        return 130
    except Exception as e:
        console.print(f"\n[bold red]Unexpected error: {str(e)}[/bold red]")
        console.print_exception()
        return 1
    finally:
        tester.teardown()


if __name__ == "__main__":
    sys.exit(main())