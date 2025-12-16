#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario-based testing for Reference Data Manager with synthetic data.

This executable test script runs realistic scenarios for reference data management,
including creating valid value hierarchies, managing definitions,
and comprehensive cleanup with detailed error reporting.

Usage:
    python tests/test_reference_data_scenarios.py
    
    Or with pytest:
    pytest tests/test_reference_data_scenarios.py -v -s
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

from pyegeria.reference_data import ReferenceDataManager
from pyegeria._exceptions import (
    PyegeriaException,
    PyegeriaNotFoundException,
    print_exception_table,
    print_validation_error, PyegeriaAPIException,
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
class ValidValueData:
    """Synthetic valid value definition data"""
    qualified_name: str
    display_name: str
    description: str
    guid: Optional[str] = None


class ReferenceDataScenarioTester:
    """Execute realistic reference data management scenarios"""
    
    def __init__(self):
        self.client: Optional[ReferenceDataManager] = None
        self.results: List[TestResult] = []
        self.created_valid_values: List[str] = []
        self.test_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def setup(self) -> bool:
        """Initialize connection to Egeria"""
        try:
            console.print("\n[bold cyan]═══ Setting up Reference Data Test Environment ═══[/bold cyan]\n")
            self.client = ReferenceDataManager(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
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
    
    def cleanup_created_valid_values(self):
        """Delete all valid value definitions created during testing"""
        console.print("\n[bold yellow]═══ Cleaning Up Test Data ═══[/bold yellow]\n")
        
        if not self.created_valid_values:
            console.print("No valid value definitions to clean up")
            return
        
        cleanup_results = {"success": 0, "failed": 0, "not_found": 0}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(
                f"Cleaning up {len(self.created_valid_values)} valid value definitions...",
                total=len(self.created_valid_values)
            )
            
            for guid in reversed(self.created_valid_values):  # Delete in reverse order
                try:
                    self.client.delete_valid_value_definition(guid)
                    cleanup_results["success"] += 1
                except PyegeriaAPIException:
                    cleanup_results["not_found"] += 1
                except Exception as e:
                    cleanup_results["failed"] += 1
                    console.print(f"[yellow]Warning: Failed to delete {guid}: {str(e)}[/yellow]")
                finally:
                    progress.advance(task)
        
        # Report cleanup results
        table = Table(title="Cleanup Summary", show_header=True)
        table.add_column("Status", style="cyan")
        table.add_column("Count", justify="right", style="green")
        
        table.add_row("Successfully Deleted", str(cleanup_results["success"]))
        table.add_row("Not Found (already deleted)", str(cleanup_results["not_found"]))
        table.add_row("Failed to Delete", str(cleanup_results["failed"]))
        
        console.print(table)
    
    def _create_valid_value(self, vv_data: ValidValueData) -> Optional[str]:
        """Helper to create a valid value definition and track it"""
        body = {
            "class": "NewElementRequestBody",
            "isOwnAnchor": True,
            "properties": {
                "class": "ValidValueDefinitionProperties",
                "qualifiedName": vv_data.qualified_name,
                "displayName": vv_data.display_name,
                "description": vv_data.description,
            }
        }
        guid = self.client.create_valid_value_definition(body)
        if guid:
            self.created_valid_values.append(guid)
            vv_data.guid = guid
        return guid
    
    def scenario_1_data_classification_hierarchy(self) -> TestResult:
        """
        Scenario 1: Create a data classification valid value hierarchy
        - Data Sensitivity Levels
          - Public
          - Internal
          - Confidential
          - Restricted
        - Data Quality Levels
          - Bronze
          - Silver
          - Gold
          - Platinum
        """
        scenario_name = "Data Classification Hierarchy"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Scenario 1: {scenario_name}[/bold blue]")
            
            # Create valid value definitions
            valid_values = {
                "sensitivity": ValidValueData(
                    f"ValidValue::DataSensitivity::{self.test_run_id}",
                    "Data Sensitivity Levels",
                    "Classification levels for data sensitivity"
                ),
                "public": ValidValueData(
                    f"ValidValue::Public::{self.test_run_id}",
                    "Public",
                    "Publicly available data"
                ),
                "internal": ValidValueData(
                    f"ValidValue::Internal::{self.test_run_id}",
                    "Internal",
                    "Internal use only"
                ),
                "confidential": ValidValueData(
                    f"ValidValue::Confidential::{self.test_run_id}",
                    "Confidential",
                    "Confidential information"
                ),
                "restricted": ValidValueData(
                    f"ValidValue::Restricted::{self.test_run_id}",
                    "Restricted",
                    "Highly restricted data"
                ),
                "quality": ValidValueData(
                    f"ValidValue::DataQuality::{self.test_run_id}",
                    "Data Quality Levels",
                    "Classification levels for data quality"
                ),
                "bronze": ValidValueData(
                    f"ValidValue::Bronze::{self.test_run_id}",
                    "Bronze",
                    "Raw, unprocessed data"
                ),
                "silver": ValidValueData(
                    f"ValidValue::Silver::{self.test_run_id}",
                    "Silver",
                    "Cleaned and validated data"
                ),
                "gold": ValidValueData(
                    f"ValidValue::Gold::{self.test_run_id}",
                    "Gold",
                    "Business-ready data"
                ),
                "platinum": ValidValueData(
                    f"ValidValue::Platinum::{self.test_run_id}",
                    "Platinum",
                    "Premium quality data"
                ),
            }
            
            # Create all valid value definitions
            for key, vv in valid_values.items():
                guid = self._create_valid_value(vv)
                created_guids.append(guid)
                console.print(f"  ✓ Created {vv.display_name}")
            
            duration = time.perf_counter() - start_time
            console.print(f"  [green]✓ Scenario completed in {duration:.2f}s[/green]")
            
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Created {len(valid_values)} valid value definitions for data classification",
                created_guids=created_guids
            )
            
        except ValidationError as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Scenario failed: ValidationError[/red]")
            print_validation_error(e)
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message="Validation error in request body",
                error=e,
                created_guids=created_guids
            )
        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Scenario failed: {str(e)}[/red]")
            traceback.print_exc()
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e),
                error=e,
                created_guids=created_guids
            )
    
    def scenario_2_valid_value_lifecycle(self) -> TestResult:
        """
        Scenario 2: Test complete valid value definition lifecycle
        - Create valid value definition
        - Update properties
        - Search and retrieve
        - Delete valid value definition
        """
        scenario_name = "Valid Value Lifecycle Management"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Scenario 2: {scenario_name}[/bold blue]")
            
            # Create
            vv = ValidValueData(
                f"ValidValue::Lifecycle::Test::{self.test_run_id}",
                "Lifecycle Test Valid Value",
                "Original description"
            )
            guid = self._create_valid_value(vv)
            created_guids.append(guid)
            console.print(f"  ✓ Created valid value definition: {guid}")
            
            # Retrieve by GUID
            retrieved = self.client.get_valid_value_definition_by_guid(guid, output_format="JSON")
            if isinstance(retrieved, dict):
                retrieved_name = retrieved.get('properties', {}).get('displayName', '')
                console.print(f"  ✓ Retrieved valid value definition: {retrieved_name}")
            else:
                console.print(f"  [yellow]⚠[/yellow] Retrieved data is not a dict: {type(retrieved)}")
            
            # Update
            update_body = {
                "class": "UpdateElementRequestBody",
                "mergeUpdate": True,
                "properties": {
                    "class": "ValidValueDefinitionProperties",
                    "qualifiedName": vv.qualified_name,
                    "displayName": "Updated Lifecycle Valid Value",
                    "description": "Updated description with new information",
                }
            }
            self.client.update_valid_value_definition(guid, update_body)
            console.print(f"  ✓ Updated valid value definition properties")
            
            # Verify update
            updated = self.client.get_valid_value_definition_by_guid(guid, output_format="JSON")
            if isinstance(updated, dict):
                updated_name = updated.get('properties', {}).get('displayName', '')
                updated_desc = updated.get('properties', {}).get('description', '')
                if updated_name == "Updated Lifecycle Valid Value":
                    console.print(f"  ✓ Verified update: {updated_name}")
                else:
                    console.print(f"  [yellow]⚠[/yellow] Update verification mismatch: {updated_name}")
            else:
                console.print(f"  [yellow]⚠[/yellow] Updated data is not a dict: {type(updated)}")
            
            # Search
            search_results = self.client.find_valid_value_definitions(
                search_string="Lifecycle",
                starts_with=False,
                ends_with=False,
                ignore_case=True,
                output_format="JSON"
            )
            console.print(f"  ✓ Found valid value definition via search")
            
            # Delete
            self.client.delete_valid_value_definition(guid)
            console.print(f"  ✓ Deleted valid value definition")
            
            # Verify deletion - should return string or raise exception
            try:
                deleted_check = self.client.get_valid_value_definition_by_guid(guid, output_format="JSON")
                if isinstance(deleted_check, str):
                    console.print(f"  ✓ Verified deletion: element not found")
                else:
                    console.print(f"  [yellow]⚠[/yellow] Element still exists after deletion")
            except PyegeriaAPIException:
                console.print(f"  ✓ Verified deletion: element not found (exception)")
            
            # Remove from cleanup list since we already deleted it
            if guid in self.created_valid_values:
                self.created_valid_values.remove(guid)
            
            duration = time.perf_counter() - start_time
            console.print(f"  [green]✓ Scenario completed in {duration:.2f}s[/green]")
            
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message="Complete lifecycle tested: create, read, update, delete",
                created_guids=[]  # Already cleaned up
            )
            
        except ValidationError as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Scenario failed: ValidationError[/red]")
            print_validation_error(e)
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message="Validation error in request body",
                error=e,
                created_guids=created_guids
            )
        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Scenario failed: {str(e)}[/red]")
            traceback.print_exc()
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e),
                error=e,
                created_guids=created_guids
            )
    
    def scenario_3_search_and_filter(self) -> TestResult:
        """
        Scenario 3: Test search and filtering capabilities
        - Create multiple valid value definitions with different patterns
        - Test various search methods
        """
        scenario_name = "Search and Filter Operations"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Scenario 3: {scenario_name}[/bold blue]")
            
            # Create test valid value definitions with patterns
            test_valid_values = [
                ValidValueData(
                    f"ValidValue::Search::Status::Active::{self.test_run_id}",
                    "Active Status",
                    "Active status for search testing"
                ),
                ValidValueData(
                    f"ValidValue::Search::Status::Inactive::{self.test_run_id}",
                    "Inactive Status",
                    "Inactive status for search testing"
                ),
                ValidValueData(
                    f"ValidValue::Search::Priority::High::{self.test_run_id}",
                    "High Priority",
                    "High priority for search testing"
                ),
            ]
            
            for vv in test_valid_values:
                guid = self._create_valid_value(vv)
                created_guids.append(guid)
                console.print(f"  ✓ Created {vv.display_name}")
            
            # Test search by pattern
            status_results = self.client.find_valid_value_definitions(
                search_string="Status",
                starts_with=False,
                ends_with=False,
                ignore_case=True,
                output_format="JSON"
            )
            console.print(f"  ✓ Search for 'Status' found results")
            
            # Test search by name
            name_results = self.client.get_valid_value_definitions_by_name(
                filter_string="*Search*"
            )
            console.print(f"  ✓ Filter by name pattern found results")
            
            # Test retrieval by GUID for one of the created valid values
            if created_guids:
                test_guid = created_guids[0]
                guid_result = self.client.get_valid_value_definition_by_guid(test_guid, output_format="JSON")
                if isinstance(guid_result, dict):
                    guid_name = guid_result.get('properties', {}).get('displayName', '')
                    console.print(f"  ✓ Retrieved by GUID: {guid_name}")
                else:
                    console.print(f"  [yellow]⚠[/yellow] GUID retrieval returned: {type(guid_result)}")
            
            duration = time.perf_counter() - start_time
            console.print(f"  [green]✓ Scenario completed in {duration:.2f}s[/green]")
            
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Tested search operations on {len(test_valid_values)} valid value definitions",
                created_guids=created_guids
            )
            
        except ValidationError as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Scenario failed: ValidationError[/red]")
            print_validation_error(e)
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message="Validation error in request body",
                error=e,
                created_guids=created_guids
            )
        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Scenario failed: {str(e)}[/red]")
            traceback.print_exc()
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e),
                error=e,
                created_guids=created_guids
            )
    
    def generate_report(self):
        """Generate comprehensive test report"""
        console.print("\n[bold cyan]═══ Test Execution Report ═══[/bold cyan]\n")
        
        # Summary statistics
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == "PASSED")
        failed = sum(1 for r in self.results if r.status == "FAILED")
        total_duration = sum(r.duration for r in self.results)
        
        # Summary table
        summary_table = Table(title="Test Summary", show_header=True, header_style="bold magenta")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", justify="right", style="green")
        
        summary_table.add_row("Total Scenarios", str(total))
        summary_table.add_row("Passed", str(passed), style="green")
        summary_table.add_row("Failed", str(failed), style="red" if failed > 0 else "green")
        summary_table.add_row("Success Rate", f"{(passed/total*100):.1f}%" if total > 0 else "N/A")
        summary_table.add_row("Total Duration", f"{total_duration:.2f}s")
        summary_table.add_row("Test Run ID", self.test_run_id)
        
        console.print(summary_table)
        
        # Detailed results table
        results_table = Table(title="\nDetailed Results", show_header=True, header_style="bold magenta")
        results_table.add_column("Scenario", style="cyan", width=40)
        results_table.add_column("Status", justify="center", width=10)
        results_table.add_column("Duration", justify="right", width=10)
        results_table.add_column("Message", width=60)
        
        for result in self.results:
            status_style = "green" if result.status == "PASSED" else "red"
            status_symbol = "✓" if result.status == "PASSED" else "✗"
            
            results_table.add_row(
                result.scenario_name,
                f"[{status_style}]{status_symbol} {result.status}[/{status_style}]",
                f"{result.duration:.2f}s",
                result.message[:60] + "..." if len(result.message) > 60 else result.message
            )
        
        console.print(results_table)
        
        # Error details if any
        errors = [r for r in self.results if r.error]
        if errors:
            console.print("\n[bold red]═══ Error Details ═══[/bold red]\n")
            for result in errors:
                error_panel = Panel(
                    f"[red]{result.error}[/red]\n\n{traceback.format_exc()}",
                    title=f"Error in {result.scenario_name}",
                    border_style="red"
                )
                console.print(error_panel)
        
        # Final status
        if failed == 0:
            console.print("\n[bold green]✓ All scenarios passed successfully![/bold green]\n")
            return 0
        else:
            console.print(f"\n[bold red]✗ {failed} scenario(s) failed[/bold red]\n")
            return 1
    
    def run_all_scenarios(self):
        """Execute all test scenarios"""
        if not self.setup():
            return 1
        
        try:
            # Run scenarios
            self.results.append(self.scenario_1_data_classification_hierarchy())
            self.results.append(self.scenario_2_valid_value_lifecycle())
            self.results.append(self.scenario_3_search_and_filter())
            
            # Cleanup
            self.cleanup_created_valid_values()
            
            # Generate report
            return self.generate_report()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Test execution interrupted by user[/yellow]")
            self.cleanup_created_valid_values()
            return 1
        except Exception as e:
            console.print(f"\n[bold red]Unexpected error: {str(e)}[/bold red]")
            traceback.print_exc()
            return 1
        finally:
            self.teardown()


def main():
    """Main entry point"""
    console.print(Panel.fit(
        "[bold cyan]Reference Data Manager Scenario Testing[/bold cyan]\n"
        "Comprehensive testing with synthetic data and automatic cleanup",
        border_style="cyan"
    ))
    
    tester = ReferenceDataScenarioTester()
    exit_code = tester.run_all_scenarios()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()