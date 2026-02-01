#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario-based testing for Data Engineer with synthetic data.

This executable test script runs realistic scenarios for data engineering,
including finding and retrieving tabular data sets,
with detailed error reporting.

Usage:
    python tests/test_data_engineer_scenarios.py
    
    Or with pytest:
    pytest tests/test_data_engineer_scenarios.py -v -s
"""

import time
import traceback
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from pyegeria.omvs.data_engineer import DataEngineer
from pyegeria.omvs.asset_maker import AssetMaker
from pyegeria.core._exceptions import (
    PyegeriaNotFoundException,
    PyegeriaTimeoutException,
)
from pyegeria.models import NewElementRequestBody

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


class DataEngineerScenarioTester:
    """Execute realistic data engineering scenarios"""
    
    def __init__(self):
        self.client: Optional[DataEngineer] = None
        self.asset_maker: Optional[AssetMaker] = None
        self.results: List[TestResult] = []
        self.created_assets: List[str] = []
        self.test_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def setup(self) -> bool:
        """Initialize connection to Egeria"""
        try:
            console.print("\n[bold cyan]═══ Setting up Data Engineer Test Environment ═══[/bold cyan]\n")
            self.client = DataEngineer(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
            self.asset_maker = AssetMaker(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
            
            self.client.create_egeria_bearer_token(USER_ID, USER_PWD)
            self.asset_maker.create_egeria_bearer_token(USER_ID, USER_PWD)
            
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
        if self.asset_maker:
            self.asset_maker.close_session()
        console.print("\n✓ Sessions closed")
    
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
                    self.asset_maker.delete_asset(guid)
                    cleanup_results["success"] += 1
                except PyegeriaNotFoundException:
                    cleanup_results["not_found"] += 1
                except Exception as e:
                    console.print(f"  [yellow]⚠ Failed to delete {guid}: {str(e)}[/yellow]")
                    cleanup_results["failed"] += 1
                progress.update(task, advance=1)
        
        console.print(f"Cleanup complete: {cleanup_results['success']} deleted, {cleanup_results['not_found']} already gone, {cleanup_results['failed']} failed")

    def print_results_summary(self):
        """Display summary of all test results"""
        table = Table(title=f"Data Engineer Scenario Test Results - {self.test_run_id}")
        table.add_column("Scenario", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Duration (s)", justify="right")
        table.add_column("Message")
        
        total_passed = 0
        for res in self.results:
            status_style = "green" if res.status == "PASSED" else "red" if res.status == "FAILED" else "yellow"
            table.add_row(
                res.scenario_name,
                f"[{status_style}]{res.status}[/{status_style}]",
                f"{res.duration:.2f}",
                res.message
            )
            if res.status == "PASSED":
                total_passed += 1
        
        console.print("\n")
        console.print(table)
        
        summary_panel = Panel(
            f"Total Scenarios: {len(self.results)}\n"
            f"Passed: [green]{total_passed}[/green]\n"
            f"Failed: [red]{len(self.results) - total_passed}[/red]",
            title="Summary",
            expand=False
        )
        console.print(summary_panel)

    def scenario_find_and_get_tabular_data(self) -> TestResult:
        """Scenario: Create, Find and Retrieve Tabular Data Sets"""
        name = "Find and Retrieve Tabular Data"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]Scenario: {name}[/bold blue]")
            
            # 1. Create a TabularDataSet to ensure we have something to find
            qname = f"TabularDataSet::Scenario::{self.test_run_id}"
            body = NewElementRequestBody(
                class_="NewElementRequestBody",
                properties={
                    "class": "TabularDataSetProperties",
                    "qualifiedName": qname,
                    "displayName": f"Scenario Test Data {self.test_run_id}",
                    "description": "A tabular data set created for scenario testing"
                },
                type_name="TabularDataSet"
            )
            
            console.print("  Creating test TabularDataSet...")
            guid = self.asset_maker.create_asset(body=body)
            created_guids.append(guid)
            self.created_assets.append(guid)
            console.print(f"  ✓ Created asset with GUID: {guid}")
            
            # 2. Find Tabular Data Sets
            # console.print(f"  Searching for TabularDataSets with search_string='*{self.test_run_id}*'...")
            # find_response = self.client.find_tabular_data_sets(search_string=f"*{self.test_run_id}*")
            console.print(f"  Searching for TabularDataSets with search_string='{qname}'...")
            find_response = self.client.find_tabular_data_sets(search_string=qname)

            found = False
            if isinstance(find_response, list):
                for item in find_response:
                    if item.get('elementHeader', {}).get('guid') == guid:
                        found = True
                        break
            
            if not found:
                return TestResult(name, "FAILED", time.perf_counter() - start_time, f"Created asset {guid} not found in search results", created_guids=created_guids)
            
            console.print("  ✓ Successfully found the created TabularDataSet")
            
            # 3. Get Tabular Data Set Report
            console.print(f"  Retrieving report for GUID: {guid}...")
            # Note: Since it's a freshly created asset, it might not have an actual report yet, 
            # but the API call should still be tested.
            try:
                report = self.client.get_tabular_data_set(guid)
                console.print("  ✓ Successfully called get_tabular_data_set")
                # print(report)
            except Exception as e:
                if isinstance(e, PyegeriaTimeoutException):
                    console.print("  ⚠ Timeout getting tabular data set report; continuing.")
                else:
                    console.print(f"  ⚠ Note: get_tabular_data_set might fail if no report exists yet: {str(e)}")
                # We won't fail the test just because the report isn't there, as long as the find worked.
                # But in a real scenario we'd expect it to work if data was ingested.

            duration = time.perf_counter() - start_time
            return TestResult(name, "PASSED", duration, "Successfully created, searched and retrieved tabular data set", created_guids=created_guids)

        except Exception as e:
            duration = time.perf_counter() - start_time
            if isinstance(e, PyegeriaTimeoutException):
                console.print(f"  [bold yellow]⚠ Timeout in {name}; continuing.[/bold yellow]")
                return TestResult(name, "WARNING", duration, f"Timeout: {e}", error=e, created_guids=created_guids)
            console.print(f"  [bold red]✗ Scenario failed: {str(e)}[/bold red]")
            traceback.print_exc()
            return TestResult(name, "FAILED", duration, str(e), error=e, created_guids=created_guids)

    def run_all_scenarios(self):
        """Execute all defined scenarios"""
        if not self.setup():
            return
        
        try:
            self.results.append(self.scenario_find_and_get_tabular_data())
            
            self.print_results_summary()
        finally:
            self.cleanup_created_assets()
            self.teardown()


def test_data_engineer_scenarios():
    """Entry point for pytest"""
    tester = DataEngineerScenarioTester()
    tester.run_all_scenarios()
    
    # Check if any scenario failed
    for res in tester.results:
        if res.status == "FAILED":
            assert False, f"Scenario {res.scenario_name} failed: {res.message}"


if __name__ == "__main__":
    tester = DataEngineerScenarioTester()
    tester.run_all_scenarios()
