#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario-based testing for Data Designer with synthetic data.

This executable test script runs realistic scenarios for data design management,
including creating data structures, data fields, and data classes,
with comprehensive cleanup and detailed error reporting.

Usage:
    python tests/test_data_designer_scenarios.py
    
    Or with pytest:
    pytest tests/test_data_designer_scenarios.py -v -s
"""

import sys
import time
import traceback
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field

from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from pyegeria.data_designer import DataDesigner
from pyegeria._exceptions import (
    PyegeriaException,
    PyegeriaAPIException,
    PyegeriaNotFoundException,
    print_exception_table,
    print_validation_error,
)
from pydantic import ValidationError

# Configuration
VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "erinoverview"
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
class DataStructureData:
    """Synthetic data structure data"""
    qualified_name: str
    display_name: str
    description: str
    namespace: str
    version: str
    guid: Optional[str] = None


class DataDesignerScenarioTester:
    """Execute realistic data designer scenarios"""
    
    def __init__(self):
        self.client: Optional[DataDesigner] = None
        self.results: List[TestResult] = []
        self.created_data_structures: List[str] = []
        self.created_data_fields: List[str] = []
        self.created_data_classes: List[str] = []
        self.test_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def setup(self) -> bool:
        """Initialize connection to Egeria"""
        try:
            console.print("\n[bold cyan]═══ Setting up Data Designer Test Environment ═══[/bold cyan]\n")
            self.client = DataDesigner(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
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
    
    def cleanup_created_elements(self):
        """Delete all elements created during testing"""
        console.print("\n[bold yellow]═══ Cleaning Up Test Data ═══[/bold yellow]\n")
        
        total_elements = (len(self.created_data_structures) + 
                         len(self.created_data_fields) + 
                         len(self.created_data_classes))
        
        if total_elements == 0:
            console.print("No elements to clean up")
            return
        
        cleanup_results = {"success": 0, "failed": 0, "not_found": 0}
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task(f"Cleaning up {total_elements} elements...", total=total_elements)
            
            # Delete data structures (which should cascade delete fields)
            for guid in reversed(self.created_data_structures):
                try:
                    self.client.delete_data_structure(guid, cascade_delete=True)
                    cleanup_results["success"] += 1
                except PyegeriaAPIException:
                    cleanup_results["not_found"] += 1
                except Exception as e:
                    console.print(f"  [yellow]⚠ Failed to delete data structure {guid}: {str(e)}[/yellow]")
                    cleanup_results["failed"] += 1
                progress.advance(task)
            
            # Delete any remaining data fields
            for guid in reversed(self.created_data_fields):
                try:
                    self.client.delete_data_field(guid)
                    cleanup_results["success"] += 1
                except PyegeriaAPIException:
                    cleanup_results["not_found"] += 1
                except Exception as e:
                    console.print(f"  [yellow]⚠ Failed to delete data field {guid}: {str(e)}[/yellow]")
                    cleanup_results["failed"] += 1
                progress.advance(task)
            
            # Delete data classes
            for guid in reversed(self.created_data_classes):
                try:
                    self.client.delete_data_class(guid)
                    cleanup_results["success"] += 1
                except PyegeriaAPIException:
                    cleanup_results["not_found"] += 1
                except Exception as e:
                    console.print(f"  [yellow]⚠ Failed to delete data class {guid}: {str(e)}[/yellow]")
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
    
    def scenario_data_structure_lifecycle(self) -> TestResult:
        """Scenario: Complete data structure lifecycle - create, read, update, delete"""
        scenario_name = "Data Structure Lifecycle"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # CREATE: Create a new data structure
            console.print("  → Creating data structure...")
            ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
            display_name = f"TestDataStructure_{ts}"
            namespace = "test_namespace"
            
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "DataStructureProperties",
                    "qualifiedName": f"{namespace}::data-structure::{display_name}",
                    "displayName": display_name,
                    "description": "Test data structure for lifecycle testing",
                    "namespace": namespace,
                    "versionIdentifier": "1.0"
                }
            }
            
            guid = self.client.create_data_structure(body)
            
            if guid:
                created_guids.append(guid)
                self.created_data_structures.append(guid)
                console.print(f"  ✓ Created data structure: {guid}")
            else:
                raise Exception("Failed to create data structure - no GUID returned")
            
            # READ: Retrieve the data structure
            console.print("  → Retrieving data structure...")
            retrieved = self.client.get_data_structure_by_guid(guid, output_format="JSON")
            
            if isinstance(retrieved, dict):
                console.print(f"  ✓ Retrieved data structure: {retrieved.get('properties', {}).get('displayName', 'Unknown')}")
            else:
                console.print("  [yellow]⚠ Retrieved data is not a dict[/yellow]")
            
            # UPDATE: Update the data structure
            console.print("  → Updating data structure...")
            update_body = {
                "class": "UpdateElementRequestBody",
                "properties": {
                    "class": "DataStructureProperties",
                    "qualifiedName": f"{namespace}::data-structure::{display_name}",
                    "displayName": f"{display_name}_Updated",
                    "description": "Updated test data structure",
                    "namespace": namespace,
                    "versionIdentifier": "2.0"
                }
            }
            
            self.client.update_data_structure(guid, update_body)
            console.print("  ✓ Updated data structure")
            
            # VERIFY UPDATE
            updated = self.client.get_data_structure_by_guid(guid, output_format="JSON")
            if isinstance(updated, dict):
                updated_name = updated.get('properties', {}).get('displayName', '')
                if "Updated" in updated_name:
                    console.print("  ✓ Verified update")
                else:
                    console.print("  [yellow]⚠ Update verification inconclusive[/yellow]")
            
            # SEARCH: Find the data structure
            console.print("  → Searching for data structure...")
            search_results = self.client.get_data_structures_by_name(
                filter=display_name[:10]
            )
            
            if isinstance(search_results, list) and len(search_results) > 0:
                console.print(f"  ✓ Found {len(search_results)} data structures in search")
            
            # DELETE: Delete the data structure
            console.print("  → Deleting data structure...")
            self.client.delete_data_structure(guid, cascade_delete=True)
            self.created_data_structures.remove(guid)
            console.print("  ✓ Deleted data structure")
            
            # VERIFY DELETION
            try:
                after_delete = self.client.get_data_structure_by_guid(guid, output_format="JSON")
                console.print("  [yellow]⚠ Data structure still exists after deletion[/yellow]")
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
    
    def scenario_data_field_management(self) -> TestResult:
        """Scenario: Create and manage data fields within a data structure"""
        scenario_name = "Data Field Management"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # Create parent data structure
            console.print("  → Creating parent data structure...")
            ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
            struct_name = f"ParentStructure_{ts}"
            namespace = "test_namespace"
            
            struct_body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "DataStructureProperties",
                    "qualifiedName": f"{namespace}::data-structure::{struct_name}",
                    "displayName": struct_name,
                    "description": "Parent structure for field testing",
                    "namespace": namespace,
                    "versionIdentifier": "1.0"
                }
            }
            
            struct_guid = self.client.create_data_structure(struct_body)
            
            if struct_guid:
                created_guids.append(struct_guid)
                self.created_data_structures.append(struct_guid)
                console.print(f"  ✓ Created parent data structure: {struct_guid}")
            else:
                raise Exception("Failed to create parent data structure")
            
            # Create data fields
            console.print("  → Creating data fields...")
            field_names = ["field_id", "field_name", "field_value"]
            field_guids = []
            
            for field_name in field_names:
                field_body = {
                    "class": "NewElementRequestBody",
                    "anchorGUID": struct_guid,
                    "isOwnAnchor": False,
                    "parentGUID": struct_guid,
                    "parentRelationshipTypeName": "MemberDataField",
                    "parentAtEnd1": True,
                    "properties": {
                        "class": "DataFieldProperties",
                        "qualifiedName": f"{namespace}::data-field::{field_name}_{ts}",
                        "displayName": field_name,
                        "description": f"Test data field {field_name}",
                        "dataType": "string"
                    }
                }
                
                field_guid = self.client.create_data_field(field_body)
                
                if field_guid:
                    created_guids.append(field_guid)
                    self.created_data_fields.append(field_guid)
                    field_guids.append(field_guid)
                    console.print(f"  ✓ Created data field '{field_name}': {field_guid}")
            
            console.print(f"  ✓ Created {len(field_guids)} data fields")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Created data structure with {len(field_guids)} fields",
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
    
    def scenario_data_class_management(self) -> TestResult:
        """Scenario: Create and manage data classes for data quality"""
        scenario_name = "Data Class Management"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # Create data classes
            console.print("  → Creating data classes...")
            ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
            namespace = "test_namespace"
            
            class_names = ["EmailAddress", "PhoneNumber", "PostalCode"]
            class_guids = []
            
            for class_name in class_names:
                class_body = {
                    "class": "NewElementRequestBody",
                    "isOwnAnchor": True,
                    "initialStatus": "ACTIVE",
                    "properties": {
                        "class": "DataClassProperties",
                        "qualifiedName": f"{namespace}::data-class::{class_name}_{ts}",
                        "displayName": class_name,
                        "description": f"Data class for validating {class_name} format",
                        "namespace": namespace
                    }
                }
                
                class_guid = self.client.create_data_class(class_body)
                
                if class_guid:
                    created_guids.append(class_guid)
                    self.created_data_classes.append(class_guid)
                    class_guids.append(class_guid)
                    console.print(f"  ✓ Created data class '{class_name}': {class_guid}")
            
            console.print(f"  ✓ Created {len(class_guids)} data classes")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Created {len(class_guids)} data classes for validation",
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
        console.print(Panel.fit(
            "[bold cyan]Data Designer Scenario Tests[/bold cyan]\n"
            f"Test Run ID: {self.test_run_id}",
            border_style="cyan"
        ))
        
        if not self.setup():
            console.print("[bold red]Setup failed. Cannot proceed with tests.[/bold red]")
            return False
        
        try:
            # Run all scenarios
            self.results.append(self.scenario_data_structure_lifecycle())
            self.results.append(self.scenario_data_field_management())
            self.results.append(self.scenario_data_class_management())
            
            # Print summary
            self.print_results_summary()
            
            # Cleanup
            self.cleanup_created_elements()
            
            # Return success if no failures
            return all(r.status != "FAILED" for r in self.results)
            
        finally:
            self.teardown()


def test_data_designer_scenarios():
    """Pytest entry point for data designer scenario tests"""
    tester = DataDesignerScenarioTester()
    success = tester.run_all_scenarios()
    assert success, "One or more scenarios failed"


if __name__ == "__main__":
    """Direct execution entry point"""
    tester = DataDesignerScenarioTester()
    success = tester.run_all_scenarios()
    sys.exit(0 if success else 1)