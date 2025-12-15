#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario-based testing for Automated Curation with realistic automation workflows.

This executable test script runs realistic scenarios for automated curation operations,
including exploring technology types, managing governance actions, and monitoring engine actions,
with comprehensive error reporting.

Usage:
    python tests/test_automated_curation_scenarios.py
    
    Or with pytest:
    pytest tests/test_automated_curation_scenarios.py -v -s
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

from pyegeria.automated_curation import AutomatedCuration
from pyegeria._exceptions import (
    PyegeriaException,
    PyegeriaAPIException,
    PyegeriaNotFoundException,
    print_exception_table,
    print_validation_error, print_basic_exception,
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
    

class AutomatedCurationScenarioTester:
    """Execute realistic automated curation scenarios"""
    
    def __init__(self):
        self.client: Optional[AutomatedCuration] = None
        self.results: List[TestResult] = []
        self.test_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def setup(self) -> bool:
        """Initialize connection to Egeria"""
        try:
            console.print("\n[bold cyan]═══ Setting up Automated Curation Test Environment ═══[/bold cyan]\n")
            self.client = AutomatedCuration(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
            token = self.client.create_egeria_bearer_token(USER_ID, USER_PWD)
            console.print(f"✓ Connected to {PLATFORM_URL}")
            console.print(f"✓ View Server {VIEW_SERVER}")
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
    
    def scenario_explore_technology_types(self) -> TestResult:
        """Scenario: Explore available technology types and their hierarchies"""
        scenario_name = "Explore Technology Types"
        start_time = time.perf_counter()
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # Get all technology types
            console.print("  → Retrieving all technology types...")
            all_types = self.client.get_all_technology_types(output_format="JSON")
            
            if isinstance(all_types, list):
                type_count = len(all_types)
                console.print(f"  ✓ Found {type_count} technology types")
                
                # Show sample types
                if type_count > 0:
                    console.print("\n  Sample Technology Types:")
                    for tech_type in all_types[:5]:  # Show first 5
                        if isinstance(tech_type, dict):
                            name = tech_type.get('displayName', tech_type.get('qualifiedName', 'Unknown'))
                            console.print(f"    • {name}")
                
                # Get detailed info for a specific type
                if type_count > 0:
                    console.print("\n  → Getting detailed information for first type...")
                    detail = self.client.get_tech_type_detail(filter = all_types[0]['displayName'],output_format="JSON")
                    if detail:
                        console.print("  ✓ Retrieved technology type details")
                
                duration = time.perf_counter() - start_time
                return TestResult(
                    scenario_name=scenario_name,
                    status="PASSED",
                    duration=duration,
                    message=f"Found {type_count} technology types"
                )
            else:
                duration = time.perf_counter() - start_time
                return TestResult(
                    scenario_name=scenario_name,
                    status="WARNING",
                    duration=duration,
                    message="No technology types found or unexpected format"
                )
                
        except PyegeriaAPIException as e:
            duration = time.perf_counter() - start_time
            print_basic_exception(e)
            console.print(f"  [yellow]⚠ API Exception: {str(e)}[/yellow]")
            return TestResult(
                scenario_name=scenario_name,
                status="WARNING",
                duration=duration,
                message=f"API Exception: {str(e)[:100]}",
                error=e
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
    
    def scenario_monitor_engine_actions(self) -> TestResult:
        """Scenario: Monitor and explore engine actions"""
        scenario_name = "Monitor Engine Actions"
        start_time = time.perf_counter()
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # Get active engine actions
            console.print("  → Retrieving active engine actions...")
            actions = self.client.get_active_engine_actions(output_format="JSON")
            
            if isinstance(actions, list):
                action_count = len(actions)
                console.print(f"  ✓ Found {action_count} engine actions")
                
                # Show sample actions
                if action_count > 0:
                    console.print("\n  Recent Engine Actions:")
                    for action in actions[:5]:  # Show first 5
                        if isinstance(action, dict):
                            props = action.get('properties', {})
                            display_name = props.get('displayName', 'Unknown')
                            status = props.get('actionStatus', 'Unknown')
                            console.print(f"    • {display_name} - Status: {status}")
                
                # Find engine actions by search
                console.print("\n  → Finding engine actions...")
                found_actions = self.client.find_engine_actions("*", output_format="JSON")
                
                if isinstance(found_actions, list):
                    found_count = len(found_actions)
                    console.print(f"  ✓ Found {found_count} engine actions via search")
                
                duration = time.perf_counter() - start_time
                return TestResult(
                    scenario_name=scenario_name,
                    status="PASSED",
                    duration=duration,
                    message=f"Found {action_count} active actions, {found_count if isinstance(found_actions, list) else 0} via search"
                )
            else:
                duration = time.perf_counter() - start_time
                return TestResult(
                    scenario_name=scenario_name,
                    status="WARNING",
                    duration=duration,
                    message="No engine actions found or unexpected format"
                )
                
        except PyegeriaAPIException as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [yellow]⚠ API Exception: {str(e)}[/yellow]")
            print_basic_exception(e) if isinstance(e, PyegeriaException) else console.print_exception()
            return TestResult(
                scenario_name=scenario_name,
                status="WARNING",
                duration=duration,
                message=f"API Exception: {str(e)[:100]}",
                error=e
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
    
    def scenario_explore_technology_type_details(self) -> TestResult:
        """Scenario: Explore detailed technology type information"""
        scenario_name = "Explore Technology Type Details"
        start_time = time.perf_counter()
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # Find specific technology types
            console.print("  → Finding technology types...")
            search_string = "PostgreSQL"
            found_types = self.client.find_technology_types(search_string, output_format="JSON")
            
            if isinstance(found_types, list):
                type_count = len(found_types)
                console.print(f"  ✓ Found {type_count} technology types matching '{search_string}'")
                
                # Show sample types
                if type_count > 0:
                    console.print("\n  Matching Technology Types:")
                    for tech_type in found_types[:5]:  # Show first 5
                        if isinstance(tech_type, dict):

                            name = tech_type.get('displayName', tech_type.get('qualifiedName', 'Unknown'))
                            console.print(f"    • {name}")
                
                duration = time.perf_counter() - start_time
                return TestResult(
                    scenario_name=scenario_name,
                    status="PASSED",
                    duration=duration,
                    message=f"Found {type_count} technology types"
                )
            else:
                duration = time.perf_counter() - start_time
                return TestResult(
                    scenario_name=scenario_name,
                    status="WARNING",
                    duration=duration,
                    message="No technology types found or unexpected format"
                )
                
        except PyegeriaAPIException as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [yellow]⚠ API Exception: {str(e)}[/yellow]")
            return TestResult(
                scenario_name=scenario_name,
                status="WARNING",
                duration=duration,
                message=f"API Exception: {str(e)[:100]}",
                error=e
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
    
    def scenario_explore_technology_hierarchy(self) -> TestResult:
        """Scenario: Explore technology type hierarchies"""
        scenario_name = "Explore Technology Hierarchy"
        start_time = time.perf_counter()
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # Get technology type hierarchy
            console.print("  → Retrieving technology type hierarchy...")
            root = self.client.get_tech_type_hierarchy(filter = '*',
                                                            output_format="JSON")
            hierarchy = root['subTypes']
            if isinstance(hierarchy, list):
                hierarchy_count = len(hierarchy)
                console.print(f"  ✓ Found {hierarchy_count} items in hierarchy")
                
                # Show sample hierarchy items
                if hierarchy_count > 0:
                    console.print("\n  Sample Hierarchy Items:")
                    for item in hierarchy[:5]:  # Show first 5
                        if isinstance(item, dict):
                            name = item.get('displayName', item.get('qualifiedName', 'Unknown'))
                            console.print(f"    • {name}")
                
                duration = time.perf_counter() - start_time
                return TestResult(
                    scenario_name=scenario_name,
                    status="PASSED",
                    duration=duration,
                    message=f"Found {hierarchy_count} items in hierarchy"
                )
            else:
                duration = time.perf_counter() - start_time
                return TestResult(
                    scenario_name=scenario_name,
                    status="WARNING",
                    duration=duration,
                    message="No hierarchy found or unexpected format"
                )
                
        except PyegeriaAPIException as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [yellow]⚠ API Exception: {str(e)}[/yellow]")
            print_basic_exception(e)
            return TestResult(
                scenario_name=scenario_name,
                status="WARNING",
                duration=duration,
                message=f"API Exception: {str(e)[:100]}",
                error=e
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
    
    def run_all_scenarios(self):
        """Execute all test scenarios"""
        console.print(Panel.fit(
            "[bold cyan]Automated Curation Scenario Tests[/bold cyan]\n"
            f"Test Run ID: {self.test_run_id}",
            border_style="cyan"
        ))
        
        if not self.setup():
            console.print("[bold red]Setup failed. Cannot proceed with tests.[/bold red]")
            return False
        
        try:
            # Run all scenarios
            self.results.append(self.scenario_explore_technology_types())
            self.results.append(self.scenario_monitor_engine_actions())
            self.results.append(self.scenario_explore_technology_type_details())
            self.results.append(self.scenario_explore_technology_hierarchy())
            
            # Print summary
            self.print_results_summary()
            
            # Return success if no failures
            return all(r.status != "FAILED" for r in self.results)
            
        finally:
            self.teardown()


def test_automated_curation_scenarios():
    """Pytest entry point for automated curation scenario tests"""
    tester = AutomatedCurationScenarioTester()
    success = tester.run_all_scenarios()
    assert success, "One or more scenarios failed"


if __name__ == "__main__":
    """Direct execution entry point"""
    tester = AutomatedCurationScenarioTester()
    success = tester.run_all_scenarios()
    sys.exit(0 if success else 1)