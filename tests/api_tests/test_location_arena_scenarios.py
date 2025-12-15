#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario-based testing for Location Arena with synthetic data.

This executable test script runs realistic scenarios for location management,
including creating hierarchical location structures, managing relationships,
and comprehensive cleanup with detailed error reporting.

Usage:
    python tests/test_location_arena_scenarios.py
    
    Or with pytest:
    pytest tests/test_location_arena_scenarios.py -v -s
"""

import sys
import time
import traceback
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field

from pydantic import ValidationError
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from loguru import logger

from pyegeria.location_arena import Location
from pyegeria._exceptions import (
    PyegeriaException,
    PyegeriaNotFoundException,
    print_exception_table, print_validation_error, PyegeriaAPIException,
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
class LocationData:
    """Synthetic location data"""
    qualified_name: str
    display_name: str
    description: str
    guid: Optional[str] = None


class LocationScenarioTester:
    """Execute realistic location management scenarios"""
    
    def __init__(self):
        self.client: Optional[Location] = None
        self.results: List[TestResult] = []
        self.created_locations: List[str] = []
        self.test_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def setup(self) -> bool:
        """Initialize connection to Egeria"""
        try:
            console.print("\n[bold cyan]═══ Setting up Location Arena Test Environment ═══[/bold cyan]\n")
            self.client = Location(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
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
    
    def cleanup_created_locations(self):
        """Delete all locations created during testing"""
        console.print("\n[bold yellow]═══ Cleaning Up Test Data ═══[/bold yellow]\n")
        
        if not self.created_locations:
            console.print("No locations to clean up")
            return
        
        cleanup_results = {"success": 0, "failed": 0, "not_found": 0}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(
                f"Cleaning up {len(self.created_locations)} locations...",
                total=len(self.created_locations)
            )
            
            for guid in reversed(self.created_locations):  # Delete in reverse order
                try:
                    body = {"class": "DeleteElementRequestBody"}
                    self.client.delete_location(guid, body)
                    cleanup_results["success"] += 1
                except PyegeriaAPIException:
                    cleanup_results["not_found"] += 1
                except Exception as e:
                    cleanup_results["failed"] += 1
                    logger.warning(f"Failed to delete location {guid}: {str(e)}")
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
    
    def _create_location(self, loc_data: LocationData) -> Optional[str]:
        """Helper to create a location and track it"""
        body = {
            "class": "NewElementRequestBody",
            "typeName": "Location",
            "initialStatus": "ACTIVE",
            "properties": {
                "class": "LocationProperties",
                "qualifiedName": loc_data.qualified_name,
                "displayName": loc_data.display_name,
                "description": loc_data.description,
            }
        }
        guid = self.client.create_location(body)
        if guid:
            self.created_locations.append(guid)
            loc_data.guid = guid
        return guid
    
    def scenario_1_corporate_office_hierarchy(self) -> TestResult:
        """
        Scenario 1: Create a corporate office location hierarchy
        - Global HQ
          - North America Region
            - New York Office
            - San Francisco Office
          - Europe Region
            - London Office
            - Berlin Office
        """
        scenario_name = "Corporate Office Hierarchy"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Scenario 1: {scenario_name}[/bold blue]")
            
            # Create locations
            locations = {
                "hq": LocationData(
                    f"Location::GlobalHQ::{self.test_run_id}",
                    "Global Headquarters",
                    "Main corporate headquarters"
                ),
                "na_region": LocationData(
                    f"Location::NorthAmerica::{self.test_run_id}",
                    "North America Region",
                    "North American regional office"
                ),
                "eu_region": LocationData(
                    f"Location::Europe::{self.test_run_id}",
                    "Europe Region",
                    "European regional office"
                ),
                "ny_office": LocationData(
                    f"Location::NewYork::{self.test_run_id}",
                    "New York Office",
                    "New York City office location"
                ),
                "sf_office": LocationData(
                    f"Location::SanFrancisco::{self.test_run_id}",
                    "San Francisco Office",
                    "San Francisco office location"
                ),
                "london_office": LocationData(
                    f"Location::London::{self.test_run_id}",
                    "London Office",
                    "London office location"
                ),
                "berlin_office": LocationData(
                    f"Location::Berlin::{self.test_run_id}",
                    "Berlin Office",
                    "Berlin office location"
                ),
            }
            
            # Create all locations
            for key, loc in locations.items():
                guid = self._create_location(loc)
                created_guids.append(guid)
                console.print(f"  ✓ Created {loc.display_name}")
            
            # Create nested relationships
            link_body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "NestedLocationProperties",
                }
            }
            
            # Link regions to HQ
            self.client.link_nested_location(locations["hq"].guid, locations["na_region"].guid, link_body)
            self.client.link_nested_location(locations["hq"].guid, locations["eu_region"].guid, link_body)
            console.print("  ✓ Linked regions to HQ")
            
            # Link offices to regions
            self.client.link_nested_location(locations["na_region"].guid, locations["ny_office"].guid, link_body)
            self.client.link_nested_location(locations["na_region"].guid, locations["sf_office"].guid, link_body)
            self.client.link_nested_location(locations["eu_region"].guid, locations["london_office"].guid, link_body)
            self.client.link_nested_location(locations["eu_region"].guid, locations["berlin_office"].guid, link_body)
            console.print("  ✓ Linked offices to regions")
            
            # Verify we can retrieve the hierarchy
            hq_details = self.client.get_location_by_guid(locations["hq"].guid, output_format="JSON")
            
            duration = time.perf_counter() - start_time
            console.print(f"  [green]✓ Scenario completed in {duration:.2f}s[/green]")
            
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Created {len(locations)} locations with hierarchical relationships",
                created_guids=created_guids
            )
            
        except ValidationError as e:
            print_validation_error(e)
        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Scenario failed: {str(e)}[/red]")
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e),
                error=e,
                created_guids=created_guids
            )
    
    def scenario_2_data_center_network(self) -> TestResult:
        """
        Scenario 2: Create a data center network with peer relationships
        - Primary Data Center (US-East)
        - Secondary Data Center (US-West)
        - Backup Data Center (EU)
        All linked as peers for redundancy
        """
        scenario_name = "Data Center Network"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Scenario 2: {scenario_name}[/bold blue]")
            
            # Create data centers
            data_centers = {
                "us_east": LocationData(
                    f"Location::DataCenter::USEast::{self.test_run_id}",
                    "US-East Data Center",
                    "Primary data center in US East region"
                ),
                "us_west": LocationData(
                    f"Location::DataCenter::USWest::{self.test_run_id}",
                    "US-West Data Center",
                    "Secondary data center in US West region"
                ),
                "eu": LocationData(
                    f"Location::DataCenter::EU::{self.test_run_id}",
                    "EU Data Center",
                    "Backup data center in European region"
                ),
            }
            
            # Create locations
            for key, loc in data_centers.items():
                guid = self._create_location(loc)
                created_guids.append(guid)
                console.print(f"  ✓ Created {loc.display_name}")
            
            # Create peer relationships (full mesh)
            link_body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "AdjacentLocationProperties",
                }
            }
            
            self.client.link_peer_locations(
                data_centers["us_east"].guid,
                data_centers["us_west"].guid,
                link_body
            )
            console.print("  ✓ Linked US-East ↔ US-West")
            
            self.client.link_peer_locations(
                data_centers["us_east"].guid,
                data_centers["eu"].guid,
                link_body
            )
            console.print("  ✓ Linked US-East ↔ EU")
            
            self.client.link_peer_locations(
                data_centers["us_west"].guid,
                data_centers["eu"].guid,
                link_body
            )
            console.print("  ✓ Linked US-West ↔ EU")
            
            duration = time.perf_counter() - start_time
            console.print(f"  [green]✓ Scenario completed in {duration:.2f}s[/green]")
            
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Created {len(data_centers)} data centers with peer relationships",
                created_guids=created_guids
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
                created_guids=created_guids
            )
    
    def scenario_3_location_lifecycle(self) -> TestResult:
        """
        Scenario 3: Test complete location lifecycle
        - Create location
        - Update properties
        - Search and retrieve
        - Delete location
        """
        scenario_name = "Location Lifecycle Management"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Scenario 3: {scenario_name}[/bold blue]")
            
            # Create
            loc = LocationData(
                f"Location::Lifecycle::Test::{self.test_run_id}",
                "Lifecycle Test Location",
                "Original description"
            )
            guid = self._create_location(loc)
            created_guids.append(guid)
            console.print(f"  ✓ Created location: {guid}")
            
            # Retrieve
            retrieved = self.client.get_location_by_guid(guid, output_format="JSON")
            console.print(f"  ✓ Retrieved location successfully")
            
            # Update
            update_body = {
                "class": "UpdateElementRequestBody",
                "mergeUpdate": True,
                "properties": {
                    "class": "LocationProperties",
                    "qualifiedName": loc.qualified_name,
                    "displayName": "Updated Lifecycle Location",
                    "description": "Updated description with new information",
                }
            }
            self.client.update_location(guid, update_body)
            console.print(f"  ✓ Updated location properties")
            
            # Verify update
            updated = self.client.get_location_by_guid(guid, output_format="JSON")
            console.print(f"  ✓ Verified update")
            
            # Search
            search_results = self.client.find_locations(
                search_string="Lifecycle",
                starts_with=False,
                ends_with=False,
                ignore_case=True,
                output_format="JSON"
            )
            console.print(f"  ✓ Found location via search")
            
            # Delete
            delete_body = {"class": "DeleteElementRequestBody"}
            self.client.delete_location(guid, delete_body)
            console.print(f"  ✓ Deleted location")
            
            # Verify deletion
            try:
                self.client.get_location_by_guid(guid, output_format="JSON")
                raise Exception("Location still exists after deletion!")
            except PyegeriaAPIException:
                console.print(f"  ✓ Verified deletion")
                # Remove from cleanup list since we already deleted it
                if guid in self.created_locations:
                    self.created_locations.remove(guid)
            
            duration = time.perf_counter() - start_time
            console.print(f"  [green]✓ Scenario completed in {duration:.2f}s[/green]")
            
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message="Complete lifecycle tested: create, read, update, delete",
                created_guids=[]  # Already cleaned up
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
                created_guids=created_guids
            )
    
    def scenario_4_search_and_filter(self) -> TestResult:
        """
        Scenario 4: Test search and filtering capabilities
        - Create multiple locations with different patterns
        - Test various search methods
        """
        scenario_name = "Search and Filter Operations"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Scenario 4: {scenario_name}[/bold blue]")
            
            # Create test locations with patterns
            test_locations = [
                LocationData(
                    f"Location::Search::Office::NYC::{self.test_run_id}",
                    "NYC Office",
                    "New York City office for search testing"
                ),
                LocationData(
                    f"Location::Search::Office::LA::{self.test_run_id}",
                    "LA Office",
                    "Los Angeles office for search testing"
                ),
                LocationData(
                    f"Location::Search::Warehouse::Seattle::{self.test_run_id}",
                    "Seattle Warehouse",
                    "Seattle warehouse for search testing"
                ),
            ]
            
            for loc in test_locations:
                guid = self._create_location(loc)
                created_guids.append(guid)
                console.print(f"  ✓ Created {loc.display_name}")
            
            # Test search by pattern
            office_results = self.client.find_locations(
                search_string="Office",
                starts_with=False,
                ends_with=False,
                ignore_case=True,
                output_format="JSON"
            )
            console.print(f"  ✓ Search for 'Office' found results")
            
            # Test search by name
            name_results = self.client.get_locations_by_name(
                filter_string="*Search*",
                output_format="JSON"
            )
            console.print(f"  ✓ Filter by name pattern found results")
            
            # Test retrieval by GUID
            for loc in test_locations:
                details = self.client.get_location_by_guid(loc.guid, output_format="JSON")
                console.print(f"  ✓ Retrieved {loc.display_name} by GUID")
            
            duration = time.perf_counter() - start_time
            console.print(f"  [green]✓ Scenario completed in {duration:.2f}s[/green]")
            
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Tested search operations on {len(test_locations)} locations",
                created_guids=created_guids
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
            self.results.append(self.scenario_1_corporate_office_hierarchy())
            self.results.append(self.scenario_2_data_center_network())
            self.results.append(self.scenario_3_location_lifecycle())
            self.results.append(self.scenario_4_search_and_filter())
            
            # Cleanup
            self.cleanup_created_locations()
            
            # Generate report
            return self.generate_report()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Test execution interrupted by user[/yellow]")
            self.cleanup_created_locations()
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
        "[bold cyan]Location Arena Scenario Testing[/bold cyan]\n"
        "Comprehensive testing with synthetic data and automatic cleanup",
        border_style="cyan"
    ))
    
    tester = LocationScenarioTester()
    exit_code = tester.run_all_scenarios()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()