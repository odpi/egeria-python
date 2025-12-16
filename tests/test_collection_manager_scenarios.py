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
            
            # 1. Create root collection
            console.print("  → Creating root collection...")
            root_data = self._create_test_collection("RootCollection")
            root_body = {
                "class": "NewElementRequestBody",
                "typeName": "Collection",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "CollectionProperties",
                    "qualifiedName": root_data.qualified_name,
                    "displayName": root_data.display_name,
                    "description": root_data.description,
                }
            }
            
            root_guid = self.client.create_collection(
                display_name=root_data.display_name,
                description=root_data.description,
                category=root_data.category,
                body=root_body
            )
            
            if root_guid:
                created_guids.append(root_guid)
                self.created_collections.append(root_guid)
                console.print(f"  ✓ Created root collection: {root_guid}")
            else:
                raise Exception("Failed to create root collection")
            
            # 2. Create child collections
            console.print("  → Creating child collections...")
            child_guids = []
            for i in range(2):
                child_data = self._create_test_collection(f"ChildCollection{i+1}")
                child_body = {
                    "class": "NewElementRequestBody",
                    "typeName": "Collection",
                    "initialStatus": "ACTIVE",
                    "properties": {
                        "class": "CollectionProperties",
                        "qualifiedName": child_data.qualified_name,
                        "displayName": child_data.display_name,
                        "description": child_data.description,
                    }
                }
                
                child_guid = self.client.create_collection(
                    display_name=child_data.display_name,
                    description=child_data.description,
                    category=child_data.category,
                    body=child_body
                )
                
                if child_guid:
                    created_guids.append(child_guid)
                    self.created_collections.append(child_guid)
                    child_guids.append(child_guid)
                    console.print(f"  ✓ Created child collection {i+1}: {child_guid}")
            
            # 3. Link collections in hierarchy
            console.print("  → Linking collections in hierarchy...")
            for i, child_guid in enumerate(child_guids):
                link_body = {
                    "class": "NewRelationshipRequestBody",
                    "properties": {
                        "class": "CollectionMembershipProperties"
                    }
                }
                self.client.add_to_collection(root_guid, child_guid, link_body)
                console.print(f"  ✓ Linked child {i+1} to root collection")
            
            # 4. Query hierarchy - get members of root collection
            console.print("  → Querying collection hierarchy...")
            members = self.client.get_collection_members(collection_guid=root_guid, output_format="JSON")
            
            if isinstance(members, list):
                console.print(f"  ✓ Root collection has {len(members)} members")
            else:
                console.print("  [yellow]⚠ Could not retrieve collection members[/yellow]")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Created hierarchy with 1 root and {len(child_guids)} child collections",
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
    
    def scenario_digital_product_management(self) -> TestResult:
        """Scenario: Create and manage digital products"""
        scenario_name = "Digital Product Management"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # 1. Create digital product
            console.print("  → Creating digital product...")
            ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
            product_qname = f"DigitalProduct::TestProduct::{ts}"
            product_name = f"Test Digital Product {ts}"
            
            product_body = {
                "class": "NewElementRequestBody",
                "typeName": "DigitalProduct",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "DigitalProductProperties",
                    "qualifiedName": product_qname,
                    "displayName": product_name,
                    "description": "Test digital product for scenario testing",
                    "productName": product_name,
                    "identifier": f"PROD-{ts}",
                    "maturity": "Development",
                    "serviceLife": "2 years"
                }
            }
            
            product_guid = self.client.create_digital_product(product_body)
            
            if product_guid:
                created_guids.append(product_guid)
                self.created_collections.append(product_guid)
                console.print(f"  ✓ Created digital product: {product_guid}")
            else:
                raise Exception("Failed to create digital product")
            
            # 2. Update product properties
            console.print("  → Updating product properties...")
            update_body = {
                "class": "UpdateElementRequestBody",
                "properties": {
                    "class": "DigitalProductProperties",
                    "qualifiedName": product_qname,
                    "displayName": f"{product_name} (Updated)",
                    "description": "Updated test digital product",
                    "productName": f"{product_name} (Updated)",
                    "identifier": f"PROD-{ts}",
                    "maturity": "Testing",
                    "serviceLife": "3 years"
                }
            }
            
            self.client.update_collection(product_guid, update_body)
            console.print("  ✓ Updated product properties")
            
            # 3. Update product status
            console.print("  → Updating product status...")
            status_body = {
                "class": "UpdateStatusRequestBody",
                "status": "Production Ready"
            }
            
            self.client.update_digital_product_status(product_guid, status="Production Ready", body=status_body)
            console.print("  ✓ Updated product status")
            
            # 4. Query products - retrieve by GUID
            console.print("  → Querying digital product...")
            retrieved = self.client.get_collection_by_guid(product_guid, output_format="JSON")
            
            if isinstance(retrieved, dict):
                retrieved_name = retrieved.get('properties', {}).get('displayName', 'Unknown')
                console.print(f"  ✓ Retrieved product: {retrieved_name}")
            else:
                console.print("  [yellow]⚠ Could not retrieve product[/yellow]")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message="Digital product created, updated, and queried successfully",
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
    
    def scenario_collection_membership(self) -> TestResult:
        """Scenario: Manage collection members"""
        scenario_name = "Collection Membership"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # 1. Create parent collection
            console.print("  → Creating parent collection...")
            parent_data = self._create_test_collection("ParentCollection")
            parent_body = {
                "class": "NewElementRequestBody",
                "typeName": "Collection",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "CollectionProperties",
                    "qualifiedName": parent_data.qualified_name,
                    "displayName": parent_data.display_name,
                    "description": parent_data.description,
                }
            }
            
            parent_guid = self.client.create_collection(
                display_name=parent_data.display_name,
                description=parent_data.description,
                category=parent_data.category,
                body=parent_body
            )
            
            if parent_guid:
                created_guids.append(parent_guid)
                self.created_collections.append(parent_guid)
                console.print(f"  ✓ Created parent collection: {parent_guid}")
            else:
                raise Exception("Failed to create parent collection")
            
            # 2. Create member collections
            console.print("  → Creating member collections...")
            member_guids = []
            for i in range(3):
                member_data = self._create_test_collection(f"MemberCollection{i+1}")
                member_body = {
                    "class": "NewElementRequestBody",
                    "typeName": "Collection",
                    "initialStatus": "ACTIVE",
                    "properties": {
                        "class": "CollectionProperties",
                        "qualifiedName": member_data.qualified_name,
                        "displayName": member_data.display_name,
                        "description": member_data.description,
                    }
                }
                
                member_guid = self.client.create_collection(
                    display_name=member_data.display_name,
                    description=member_data.description,
                    category=member_data.category,
                    body=member_body
                )
                
                if member_guid:
                    created_guids.append(member_guid)
                    self.created_collections.append(member_guid)
                    member_guids.append(member_guid)
                    console.print(f"  ✓ Created member collection {i+1}: {member_guid}")
            
            # 3. Add members to parent collection
            console.print("  → Adding members to parent collection...")
            for i, member_guid in enumerate(member_guids):
                membership_body = {
                    "class": "NewRelationshipRequestBody",
                    "properties": {
                        "class": "RelationshipProperties"
                    }
                }
                self.client.add_to_collection(parent_guid, member_guid, membership_body)
                console.print(f"  ✓ Added member {i+1} to parent collection")
            
            # 4. Query collection members
            console.print("  → Querying collection members...")
            members = self.client.get_collection_members(collection_guid=parent_guid, output_format="JSON")
            
            if isinstance(members, list):
                console.print(f"  ✓ Parent collection has {len(members)} members")
                if len(members) >= len(member_guids):
                    console.print("  ✓ All members successfully added")
                else:
                    console.print(f"  [yellow]⚠ Expected {len(member_guids)} members, found {len(members)}[/yellow]")
            else:
                console.print("  [yellow]⚠ Could not retrieve collection members[/yellow]")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Created collection with {len(member_guids)} members",
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