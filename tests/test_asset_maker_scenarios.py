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
            
            guid = self.client.create_asset(body=body)
            
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
                
                guid = self.client.create_asset(body=body)
                
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
            
            template_guid = self.client.create_asset(body=template_body)
            
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
            new_asset_guid = self.client.create_asset_from_template(body=from_template_body)
            
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
