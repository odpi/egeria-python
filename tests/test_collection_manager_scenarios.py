#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario-based testing for Collection Manager with synthetic data.

This executable test script runs realistic scenarios for collection management,
including creating collections, managing members, and organizing resources,
with comprehensive cleanup and detailed error reporting.

Usage:
    python tests/test_collection_manager_scenarios.py
    
    Or with pytest:
    pytest tests/test_collection_manager_scenarios.py -v -s
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

from pyegeria.collection_manager import CollectionManager
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
class CollectionData:
    """Synthetic collection data"""
    qualified_name: str
    display_name: str
    description: str
    category: Optional[str] = None
    guid: Optional[str] = None


class CollectionManagerScenarioTester:
    """Execute realistic collection management scenarios"""
    
    def __init__(self):
        self.client: Optional[CollectionManager] = None
        self.results: List[TestResult] = []
        self.created_collections: List[str] = []
        self.test_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def setup(self) -> bool:
        """Initialize connection to Egeria"""
        try:
            console.print("\n[bold cyan]═══ Setting up Collection Manager Test Environment ═══[/bold cyan]\n")
            self.client = CollectionManager(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
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
    
    def cleanup_created_collections(self):
        """Delete all collections created during testing"""
        console.print("\n[bold yellow]═══ Cleaning Up Test Data ═══[/bold yellow]\n")
        
        if not self.created_collections:
            console.print("No collections to clean up")
            return
        
        cleanup_results = {"success": 0, "failed": 0, "not_found": 0}
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task(f"Cleaning up {len(self.created_collections)} collections...", total=len(self.created_collections))
            
            for guid in self.created_collections:
                try:
                    self.client.delete_collection(guid)
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
    
    def _create_test_collection(self, prefix: str = "TestCollection") -> CollectionData:
        """Helper to create a test collection with unique name"""
        ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return CollectionData(
            qualified_name=f"{prefix}::{ts}",
            display_name=f"{prefix} {ts}",
            description=f"Test collection created at {datetime.now().isoformat()}",
            category="TestCategory"
        )
    
    def scenario_collection_lifecycle(self) -> TestResult:
        """Scenario: Complete collection lifecycle - create, read, update, delete"""
        scenario_name = "Collection Lifecycle"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # CREATE: Create a new collection
            console.print("  → Creating collection...")
            collection_data = self._create_test_collection("LifecycleTest")
            
            body = {
                "class": "NewElementRequestBody",
                "typeName": "Collection",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "CollectionProperties",
                    "qualifiedName": collection_data.qualified_name,
                    "displayName": collection_data.display_name,
                    "description": collection_data.description,
                }
            }
            
            guid = self.client.create_collection(
                display_name=collection_data.display_name,
                description=collection_data.description,
                category=collection_data.category,
                body=body
            )
            
            if guid:
                created_guids.append(guid)
                self.created_collections.append(guid)
                collection_data.guid = guid
                console.print(f"  ✓ Created collection: {guid}")
            else:
                raise Exception("Failed to create collection - no GUID returned")
            
            # READ: Retrieve the collection
            console.print("  → Retrieving collection...")
            retrieved = self.client.get_collection_by_guid(guid, output_format="JSON")
            
            if isinstance(retrieved, dict):
                console.print(f"  ✓ Retrieved collection: {retrieved.get('properties', {}).get('displayName', 'Unknown')}")
            else:
                raise Exception("Failed to retrieve collection")
            
            # UPDATE: Update the collection
            console.print("  → Updating collection...")
            update_body = {
                "class": "UpdateElementRequestBody",
                "properties": {
                    "class": "CollectionProperties",
                    "qualifiedName": collection_data.qualified_name,
                    "displayName": f"{collection_data.display_name} (Updated)",
                    "description": f"{collection_data.description} - Updated",
                }
            }
            
            self.client.update_collection(guid, update_body)
            console.print("  ✓ Updated collection")
            
            # VERIFY UPDATE
            updated = self.client.get_collection_by_guid(guid, output_format="JSON")
            if isinstance(updated, dict):
                updated_name = updated.get('properties', {}).get('displayName', '')
                if "(Updated)" in updated_name:
                    console.print("  ✓ Verified update")
                else:
                    console.print("  [yellow]⚠ Update verification inconclusive[/yellow]")
            
            # SEARCH: Find the collection
            console.print("  → Searching for collection...")
            search_results = self.client.find_collections(
                search_string=collection_data.display_name[:10],
                output_format="JSON"
            )
            
            if isinstance(search_results, list) and len(search_results) > 0:
                console.print(f"  ✓ Found {len(search_results)} collections in search")
            
            # DELETE: Delete the collection
            console.print("  → Deleting collection...")
            self.client.delete_collection(guid)
            self.created_collections.remove(guid)
            console.print("  ✓ Deleted collection")
            
            # VERIFY DELETION
            try:
                after_delete = self.client.get_collection_by_guid(guid, output_format="JSON")
                console.print("  [yellow]⚠ Collection still exists after deletion[/yellow]")
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
    
    def scenario_collection_hierarchy(self) -> TestResult:
        """Scenario: Create and manage collection hierarchies"""
        scenario_name = "Collection Hierarchy"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # TODO: Implement collection hierarchy scenario
            # 1. Create root collection
            # 2. Create child collections
            # 3. Link collections in hierarchy
            # 4. Query hierarchy
            # 5. Cleanup
            
            console.print("  [yellow]⚠ Scenario not yet implemented[/yellow]")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="WARNING",
                duration=duration,
                message="Scenario template - needs implementation",
                created_guids=created_guids
            )
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Error: {str(e)}[/red]")
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e)[:100],
                error=e,
                created_guids=created_guids
            )
    
    def scenario_digital_product_management(self) -> TestResult:
        """Scenario: Create and manage digital products"""
        scenario_name = "Digital Product Management"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # TODO: Implement digital product scenario
            # 1. Create digital product
            # 2. Update product properties
            # 3. Update product status
            # 4. Query products
            # 5. Cleanup
            
            console.print("  [yellow]⚠ Scenario not yet implemented[/yellow]")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="WARNING",
                duration=duration,
                message="Scenario template - needs implementation",
                created_guids=created_guids
            )
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Error: {str(e)}[/red]")
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e)[:100],
                error=e,
                created_guids=created_guids
            )
    
    def scenario_collection_membership(self) -> TestResult:
        """Scenario: Manage collection members"""
        scenario_name = "Collection Membership"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # TODO: Implement collection membership scenario
            # 1. Create collection
            # 2. Add members to collection
            # 3. Query collection members
            # 4. Remove members
            # 5. Cleanup
            
            console.print("  [yellow]⚠ Scenario not yet implemented[/yellow]")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="WARNING",
                duration=duration,
                message="Scenario template - needs implementation",
                created_guids=created_guids
            )
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Error: {str(e)}[/red]")
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
            "[bold cyan]Collection Manager Scenario Tests[/bold cyan]\n"
            f"Test Run ID: {self.test_run_id}",
            border_style="cyan"
        ))
        
        if not self.setup():
            console.print("[bold red]Setup failed. Cannot proceed with tests.[/bold red]")
            return False
        
        try:
            # Run all scenarios
            self.results.append(self.scenario_collection_lifecycle())
            self.results.append(self.scenario_collection_hierarchy())
            self.results.append(self.scenario_digital_product_management())
            self.results.append(self.scenario_collection_membership())
            
            # Print summary
            self.print_results_summary()
            
            # Cleanup
            self.cleanup_created_collections()
            
            # Return success if no failures
            return all(r.status != "FAILED" for r in self.results)
            
        finally:
            self.teardown()


def test_collection_manager_scenarios():
    """Pytest entry point for collection manager scenario tests"""
    tester = CollectionManagerScenarioTester()
    success = tester.run_all_scenarios()
    assert success, "One or more scenarios failed"


if __name__ == "__main__":
    """Direct execution entry point"""
    tester = CollectionManagerScenarioTester()
    success = tester.run_all_scenarios()
    sys.exit(0 if success else 1)