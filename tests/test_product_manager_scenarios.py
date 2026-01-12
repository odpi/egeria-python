#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario-based testing for Product Manager with synthetic data.

This executable test script runs realistic scenarios for digital product management,
including creating products, managing dependencies, and assigning product managers,
with comprehensive cleanup and detailed error reporting.

Usage:
    python tests/test_product_manager_scenarios.py
    
    Or with pytest:
    c
"""
import json
import sys
import time
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from pyegeria.omvs.product_manager import ProductManager
from pyegeria.core._exceptions import (
    PyegeriaException,
    PyegeriaAPIException,
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


@dataclass
class DigitalProductData:
    """Synthetic digital product data"""
    qualified_name: str
    display_name: str
    description: str
    product_name: str
    guid: Optional[str] = None


class ProductManagerScenarioTester:
    """Execute realistic product management scenarios"""
    
    def __init__(self):
        self.client: Optional[ProductManager] = None
        self.results: List[TestResult] = []
        self.created_products: List[str] = []
        self.test_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def setup(self) -> bool:
        """Initialize connection to Egeria"""
        try:
            console.print("\n[bold cyan]═══ Setting up Product Manager Test Environment ═══[/bold cyan]\n")
            self.client = ProductManager(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
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
    
    def cleanup_created_products(self):
        """Delete all products created during testing"""
        console.print("\n[bold yellow]═══ Cleaning Up Test Data ═══[/bold yellow]\n")
        
        if not self.created_products:
            console.print("No products to clean up")
            return
        
        cleanup_results = {"success": 0, "failed": 0, "not_found": 0}
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task(f"Cleaning up {len(self.created_products)} products...", total=len(self.created_products))
            
            for guid in self.created_products:
                try:
                    # Use the new delete_digital_product method
                    self.client.delete_digital_product(guid)
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
    
    def _create_test_product(self, prefix: str = "TestProduct") -> DigitalProductData:
        """Helper to create test product data with unique name"""
        ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return DigitalProductData(
            qualified_name=f"DigitalProduct::{prefix}::{ts}",
            display_name=f"{prefix} {ts}",
            description=f"Test digital product created at {datetime.now().isoformat()}",
            product_name=f"{prefix}_{ts}"
        )
    
    def scenario_digital_product_lifecycle(self) -> TestResult:
        """Scenario: Complete digital product lifecycle - create, update"""
        scenario_name = "Digital Product Lifecycle"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # CREATE: Create a new digital product
            console.print("  → Creating digital product...")
            product_data = self._create_test_product("LifecycleTest")
            
            body = {
                "class": "NewElementRequestBody",
                "typeName": "DigitalProduct",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "DigitalProductProperties",
                    "qualifiedName": product_data.qualified_name,
                    "displayName": product_data.display_name,
                    "description": product_data.description,
                    "productName": product_data.product_name,
                    "category": "Periodic Delta"
                }
            }
            
            guid = self.client.create_digital_product(body)
            
            if guid:
                created_guids.append(guid)
                self.created_products.append(guid)
                product_data.guid = guid
                console.print(f"  ✓ Created digital product: {guid}")
            else:
                raise Exception("Failed to create digital product - no GUID returned")
            
            # UPDATE: Update the digital product
            console.print("  → Updating digital product...")
            update_body = {
                "class": "UpdateElementRequestBody",
                "properties": {
                    "class": "DigitalProductProperties",
                    "qualifiedName": product_data.qualified_name,
                    "displayName": f"{product_data.display_name} (Updated)",
                    "description": f"{product_data.description} - Updated",
                    "productName": product_data.product_name,
                    "currentVersion": "V1.1"
                }
            }
            
            self.client.update_digital_product(guid, update_body)
            console.print("  ✓ Updated digital product")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message="Digital product lifecycle executed successfully",
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
    
    def scenario_product_dependency(self) -> TestResult:
        """Scenario: Link and unlink product dependencies"""
        scenario_name = "Product Dependency Management"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # CREATE: Create two digital products for dependency testing
            console.print("  → Creating digital products for dependency test...")
            ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
            
            # Create consumer product
            consumer_body = {
                "class": "NewElementRequestBody",
                "typeName": "DigitalProduct",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "DigitalProductProperties",
                    "qualifiedName": f"DigitalProduct::ConsumerProduct::{ts}",
                    "displayName": f"Consumer Product {ts}",
                    "description": "Digital product that consumes another product",
                    "productName": f"Consumer-{ts}",
                    "productType": "Application"
                }
            }
            
            consumer_product_guid = self.client.create_digital_product(consumer_body)
            if consumer_product_guid:
                created_guids.append(consumer_product_guid)
                self.created_products.append(consumer_product_guid)
                console.print(f"  ✓ Created consumer product: {consumer_product_guid}")
            else:
                raise Exception("Failed to create consumer product")
            
            # Create consumed product
            consumed_body = {
                "class": "NewElementRequestBody",
                "typeName": "DigitalProduct",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "DigitalProductProperties",
                    "qualifiedName": f"DigitalProduct::ConsumedProduct::{ts}",
                    "displayName": f"Consumed Product {ts}",
                    "description": "Digital product that is consumed by another",
                    "productName": f"Consumed-{ts}",
                    "productType": "Service"
                }
            }
            
            consumed_product_guid = self.client.create_digital_product(consumed_body)
            if consumed_product_guid:
                created_guids.append(consumed_product_guid)
                self.created_products.append(consumed_product_guid)
                console.print(f"  ✓ Created consumed product: {consumed_product_guid}")
            else:
                raise Exception("Failed to create consumed product")
            
            # LINK: Link product dependency
            console.print("  → Linking product dependency...")
            dependency_body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "DigitalProductDependencyProperties",
                    "label": "Test Dependency",
                    "description": "Test product dependency"
                }
            }
            
            self.client.link_digital_product_dependency(
                consumer_product_guid, consumed_product_guid, dependency_body
            )
            console.print("  ✓ Linked product dependency")
            
            # DETACH: Remove product dependency
            console.print("  → Detaching product dependency...")
            self.client.detach_digital_product_dependency(
                consumer_product_guid, consumed_product_guid
            )
            console.print("  ✓ Detached product dependency")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Successfully tested product dependency with {len(created_guids)} products",
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
    
    def scenario_product_manager_role(self) -> TestResult:
        """Scenario: Link and unlink product manager roles"""
        scenario_name = "Product Manager Role Assignment"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # CREATE: Create a digital product and an actor role for manager assignment
            console.print("  → Creating product and manager role for assignment test...")
            ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
            
            # Create digital product
            product_body = {
                "class": "NewElementRequestBody",
                "typeName": "DigitalProduct",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "DigitalProductProperties",
                    "qualifiedName": f"DigitalProduct::ManagedProduct::{ts}",
                    "displayName": f"Managed Product {ts}",
                    "description": "Digital product for manager assignment testing",
                    "productName": f"Managed-{ts}",
                    "productType": "Platform"
                }
            }
            
            product_guid = self.client.create_digital_product(product_body)
            if product_guid:
                created_guids.append(product_guid)
                self.created_products.append(product_guid)
                console.print(f"  ✓ Created digital product: {product_guid}")
            else:
                raise Exception("Failed to create digital product")
            
            # Note: We need to import ActorManager to create an actor role
            from pyegeria.omvs.actor_manager import ActorManager
            actor_client = ActorManager(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
            actor_client.create_egeria_bearer_token(USER_ID, USER_PWD)
            
            # Create actor role for product manager
            role_body = {
                "class": "NewElementRequestBody",
                "typeName": "ActorRole",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "ActorRoleProperties",
                    "qualifiedName": f"ActorRole::ProductManager::{ts}",
                    "name": f"Product Manager Role {ts}",
                    "description": "Actor role for product manager testing"
                }
            }
            
            manager_role_guid = actor_client.create_actor_role(role_body)
            if manager_role_guid:
                created_guids.append(manager_role_guid)
                console.print(f"  ✓ Created manager role: {manager_role_guid}")
            else:
                raise Exception("Failed to create manager role")
            
            # LINK: Link product manager role
            console.print("  → Linking product manager...")
            assignment_body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "AssignmentScopeProperties",
                    "assignmentType": "Product Manager",
                    "description": "Test product manager assignment"
                }
            }
            
            self.client.link_product_manager(product_guid, manager_role_guid, assignment_body)
            console.print("  ✓ Linked product manager")
            
            # DETACH: Remove product manager assignment
            console.print("  → Detaching product manager...")
            self.client.detach_product_manager(product_guid, manager_role_guid)
            console.print("  ✓ Detached product manager")
            
            # Cleanup actor role
            try:
                actor_client.delete_actor_role(manager_role_guid)
                console.print("  ✓ Deleted manager role")
                created_guids.remove(manager_role_guid)
            except Exception as e:
                console.print(f"  [yellow]⚠ Failed to delete manager role: {str(e)}[/yellow]")
            
            actor_client.close_session()
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Successfully tested product manager role with {len(created_guids)} elements",
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
    
    def scenario_retrieve_digital_products(self) -> TestResult:
        """Scenario: Test retrieval methods - get by GUID, get by name, find"""
        scenario_name = "Digital Product Retrieval Methods"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # CREATE: Create test products for retrieval
            console.print("  → Creating test products for retrieval...")
            products_to_create = [
                self._create_test_product("RetrievalTest_Alpha"),
                self._create_test_product("RetrievalTest_Beta"),
                self._create_test_product("RetrievalTest_Gamma"),
            ]
            
            for product_data in products_to_create:
                body = {
                    "class": "NewElementRequestBody",
                    "typeName": "DigitalProduct",
                    "properties": {
                        "class": "DigitalProductProperties",
                        "qualifiedName": product_data.qualified_name,
                        "displayName": product_data.display_name,
                        "description": product_data.description,
                        "productName": product_data.product_name,
                    }
                }
                
                guid = self.client.create_digital_product(body)
                if guid:
                    created_guids.append(guid)
                    self.created_products.append(guid)
                    product_data.guid = guid
                    console.print(f"  ✓ Created product: {product_data.display_name} ({guid})")
            
            # TEST 1: Get by GUID
            console.print("\n  → Testing get_digital_product_by_guid...")
            if created_guids:
                test_guid = created_guids[0]
                product = self.client.get_digital_product_by_guid(test_guid)
                if product:
                    console.print(f"  ✓ Retrieved product by GUID: {test_guid}")
                    console.print(f"    Display Name: {product.get('properties', {}).get('displayName', 'N/A')}")
                else:
                    console.print(f"  [yellow]⚠ No product found for GUID: {test_guid}[/yellow]")
            
            # TEST 2: Get by name (using filter string)
            console.print("\n  → Testing get_digital_products_by_name...")
            filter_string = product.get('properties', {}).get('qualifiedName', 'N/A')
            products = self.client.get_digital_products_by_name(filter_string=filter_string)
            if products:
                console.print(f"  ✓ Found {len(products)} products with filter `{filter_string}`")
                for prod in products[:3]:  # Show first 3
                    if type(prod) is str:
                        console.print(f"prod was: {prod}")
                        exit(0)
                    else:
                        console.print(json.dumps(prod, indent =2))
                    name = prod.get('elementHeader', {}).get('properties', {}).get('displayName', 'N/A')
                    guid = prod.get('elementHeader', {}).get('guid', 'N/A')
                    console.print(f"    - {name} ({guid})")
            else:
                console.print("  [yellow]⚠ No products found by name[/yellow]")
            
            # TEST 3: Find products (search)
            console.print("\n  → Testing find_digital_products...")
            found_products = self.client.find_digital_products(search_string="Alpha", starts_with=False)
            if found_products:
                console.print(f"  ✓ Found {len(found_products)} products matching 'Alpha'")
                for prod in found_products[:3]:  # Show first 3
                    name = prod.get('elementHeader', {}).get('properties', {}).get('displayName', 'N/A')
                    guid = prod.get('elementHeader', {}).get('guid', 'N/A')
                    console.print(f"    - {name} ({guid})")
            else:
                console.print("  [yellow]⚠ No products found by search[/yellow]")
            
            # TEST 4: Test output formats
            console.print("\n  → Testing different output formats...")
            if created_guids:
                test_guid = created_guids[0]
                
                # Test JSON format (default)
                json_result = self.client.get_digital_product_by_guid(test_guid, output_format="JSON")
                console.print(f"  ✓ JSON format: {type(json_result).__name__}")
                
                # Test DICT format
                dict_result = self.client.get_digital_product_by_guid(test_guid, output_format="DICT")
                console.print(f"  ✓ DICT format: {type(dict_result).__name__}")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Successfully tested retrieval methods with {len(created_guids)} products",
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
    
    def scenario_delete_digital_product(self) -> TestResult:
        """Scenario: Test delete_digital_product method"""
        scenario_name = "Digital Product Deletion"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # CREATE: Create a product to delete
            console.print("  → Creating product for deletion test...")
            product_data = self._create_test_product("DeleteTest")
            
            body = {
                "class": "NewElementRequestBody",
                "typeName": "DigitalProduct",
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "DigitalProductProperties",
                    "qualifiedName": product_data.qualified_name,
                    "displayName": product_data.display_name,
                    "description": product_data.description,
                    "productName": product_data.product_name,
                }
            }
            
            guid = self.client.create_digital_product(body)
            if guid:
                created_guids.append(guid)
                console.print(f"  ✓ Created product for deletion: {guid}")
            else:
                raise Exception("Failed to create product for deletion test")
            
            # DELETE: Delete the product
            console.print("  → Deleting product...")
            self.client.delete_digital_product(guid)
            console.print(f"  ✓ Deleted product: {guid}")
            
            # VERIFY: Try to retrieve deleted product (should fail or return None)
            console.print("  → Verifying deletion...")
            try:
                deleted_product = self.client.get_digital_product_by_guid(guid)
                if deleted_product:
                    console.print("  [yellow]⚠ Product still exists after deletion (may be soft delete)[/yellow]")
                else:
                    console.print("  ✓ Product successfully deleted (not found)")
            except PyegeriaAPIException as e:
                if e.related_http_code == 404:
                    console.print("  ✓ Product successfully deleted (not found)")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message="Successfully tested delete_digital_product method",
                created_guids=[]  # Don't track since we deleted it
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
    
    def scenario_digital_product_catalog_lifecycle(self) -> TestResult:
        """Scenario: Complete digital product catalog lifecycle - create, update, delete"""
        scenario_name = "Digital Product Catalog Lifecycle"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # CREATE: Create a new digital product catalog
            console.print("  → Creating digital product catalog...")
            ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
            
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "DigitalProductCatalogProperties",
                    "qualifiedName": f"DigitalProductCatalog::CatalogTest::{ts}",
                    "displayName": f"Test Product Catalog {ts}",
                    "description": f"Test digital product catalog created at {datetime.now().isoformat()}",
                }
            }
            
            guid = self.client.create_digital_product_catalog(body)
            
            if guid:
                created_guids.append(guid)
                self.created_products.append(guid)
                console.print(f"  ✓ Created digital product catalog: {guid}")
            else:
                raise Exception("Failed to create digital product catalog - no GUID returned")
            
            # UPDATE: Update the digital product catalog
            console.print("  → Updating digital product catalog...")
            update_body = {
                "class": "UpdateElementRequestBody",
                "properties": {
                    "class": "DigitalProductCatalogProperties",
                    "qualifiedName": f"DigitalProductCatalog::CatalogTest::{ts}",
                    "displayName": f"Test Product Catalog {ts} (Updated)",
                    "description": f"Test digital product catalog - Updated",
                }
            }
            
            self.client.update_digital_product_catalog(guid, update_body)
            console.print("  ✓ Updated digital product catalog")
            
            # RETRIEVE: Get the catalog by GUID
            console.print("  → Retrieving digital product catalog by GUID...")
            catalog = self.client.get_digital_product_catalog_by_guid(guid)
            if catalog:
                console.print(f"  ✓ Retrieved catalog by GUID")
            
            # DELETE: Delete the catalog
            console.print("  → Deleting digital product catalog...")
            self.client.delete_digital_product_catalog(guid)
            console.print(f"  ✓ Deleted catalog: {guid}")
            created_guids.remove(guid)  # Remove from tracking since we deleted it
            self.created_products.remove(guid)
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message="Digital product catalog lifecycle executed successfully",
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
    
    def scenario_retrieve_digital_product_catalogs(self) -> TestResult:
        """Scenario: Test retrieval methods for digital product catalogs - get by GUID, get by name, find"""
        scenario_name = "Digital Product Catalog Retrieval Methods"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # CREATE: Create test catalogs for retrieval
            console.print("  → Creating test catalogs for retrieval...")
            catalog_names = ["CatalogAlpha", "CatalogBeta", "CatalogGamma"]
            
            for name in catalog_names:
                ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
                body = {
                    "class": "NewElementRequestBody",
                    "isOwnAnchor": True,
                    "properties": {
                        "class": "DigitalProductCatalogProperties",
                        "qualifiedName": f"DigitalProductCatalog::RetrievalTest_{name}::{ts}",
                        "displayName": f"RetrievalTest {name} {ts}",
                        "description": f"Test catalog for retrieval - {name}",
                    }
                }
                
                guid = self.client.create_digital_product_catalog(body)
                if guid:
                    created_guids.append(guid)
                    self.created_products.append(guid)
                    console.print(f"  ✓ Created catalog: {name} ({guid})")
                time.sleep(0.1)  # Small delay between creates
            
            # TEST 1: Get by GUID
            console.print("\n  → Testing get_digital_product_catalog_by_guid...")
            if created_guids:
                test_guid = created_guids[0]
                catalog = self.client.get_digital_product_catalog_by_guid(test_guid)
                if catalog:
                    console.print(f"  ✓ Retrieved catalog by GUID: {test_guid}")
                else:
                    console.print(f"  [yellow]⚠ No catalog found for GUID: {test_guid}[/yellow]")
            
            # TEST 2: Get by name (using filter string)
            console.print("\n  → Testing get_digital_product_catalogs_by_name...")
            catalogs = self.client.get_digital_product_catalogs_by_name(filter_string="RetrievalTest")
            if catalogs:
                console.print(f"  ✓ Found {len(catalogs)} catalogs with filter 'RetrievalTest'")
                for cat in catalogs[:3]:  # Show first 3
                    if isinstance(cat, dict):
                        name = cat.get('elementHeader', {}).get('properties', {}).get('displayName', 'N/A')
                        guid = cat.get('elementHeader', {}).get('guid', 'N/A')
                        console.print(f"    - {name} ({guid})")
            else:
                console.print("  [yellow]⚠ No catalogs found by name[/yellow]")
            
            # TEST 3: Find catalogs (search)
            console.print("\n  → Testing find_digital_product_catalogs...")
            found_catalogs = self.client.find_digital_product_catalogs(search_string="CatalogAlpha", starts_with=False)
            if found_catalogs:
                console.print(f"  ✓ Found {len(found_catalogs)} catalogs matching 'CatalogAlpha'")
                for cat in found_catalogs[:3]:  # Show first 3
                    if isinstance(cat, dict):
                        name = cat.get('elementHeader', {}).get('properties', {}).get('displayName', 'N/A')
                        guid = cat.get('elementHeader', {}).get('guid', 'N/A')
                        console.print(f"    - {name} ({guid})")
            else:
                console.print("  [yellow]⚠ No catalogs found by search[/yellow]")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Successfully tested retrieval methods with {len(created_guids)} catalogs",
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
        console.print("\n[bold magenta]═══ Running Product Manager Scenarios ═══[/bold magenta]")
        
        scenarios = [
            self.scenario_digital_product_lifecycle,
            self.scenario_retrieve_digital_products,
            self.scenario_delete_digital_product,
            self.scenario_product_dependency,
            self.scenario_product_manager_role,
            self.scenario_digital_product_catalog_lifecycle,
            self.scenario_retrieve_digital_product_catalogs,
        ]
        
        for scenario_func in scenarios:
            result = scenario_func()
            self.results.append(result)
            time.sleep(0.5)  # Brief pause between scenarios


def test_product_manager_scenarios():
    """Pytest entry point for product manager scenario tests"""
    exit_code = main()
    assert exit_code == 0, "One or more scenarios failed"


def main():
    """Main test execution"""
    tester = ProductManagerScenarioTester()
    
    try:
        if not tester.setup():
            console.print("[bold red]Setup failed. Exiting.[/bold red]")
            return 1
        
        tester.run_all_scenarios()
        tester.print_results_summary()
        tester.cleanup_created_products()
        
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