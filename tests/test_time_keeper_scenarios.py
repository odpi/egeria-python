"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario tests for Time Keeper View Service.
"""
import time
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from pyegeria.omvs.time_keeper import TimeKeeper
from pyegeria.omvs.asset_maker import AssetMaker
from pyegeria.core._exceptions import (
    PyegeriaNotFoundException,
    PyegeriaConnectionException,
)

# Configuration
VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"

console = Console(width=250)

@dataclass
class TestResult:
    """Track results of test scenarios"""
    scenario_name: str
    status: str  # "PASSED", "FAILED", "WARNING"
    duration: float
    message: str = ""
    error: Optional[Exception] = None
    created_guids: List[str] = field(default_factory=list)


class TimeKeeperScenarioTester:
    """Execute realistic time keeper scenarios"""
    
    def __init__(self):
        self.tk_client: Optional[TimeKeeper] = None
        self.asset_maker: Optional[AssetMaker] = None
        self.results: List[TestResult] = []
        self.created_guids: List[str] = []
        self.test_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def setup(self) -> bool:
        """Initialize connection to Egeria"""
        try:
            console.print("\n[bold cyan]═══ Setting up Time Keeper Test Environment ═══[/bold cyan]\n")
            self.tk_client = TimeKeeper(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
            self.asset_maker = AssetMaker(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
            
            self.tk_client.create_egeria_bearer_token(USER_ID, USER_PWD)
            self.asset_maker.create_egeria_bearer_token(USER_ID, USER_PWD)
            
            console.print(f"✓ Connected to {PLATFORM_URL}")
            console.print(f"✓ Authenticated as {USER_ID}")
            console.print(f"✓ Test Run ID: {self.test_run_id}\n")
            return True
        except PyegeriaConnectionException:
            console.print("[bold red]✗ Setup failed: Connection Error (Egeria not running?)[/bold red]")
            return False
        except Exception as e:
            console.print(f"[bold red]✗ Setup failed: {str(e)}[/bold red]")
            return False
    
    def teardown(self):
        """Clean up and close connection"""
        if self.tk_client:
            self.tk_client.close_session()
        if self.asset_maker:
            self.asset_maker.close_session()
        console.print("\n✓ Sessions closed")
    
    def cleanup_created_elements(self):
        """Delete all elements created during testing"""
        console.print("\n[bold yellow]═══ Cleaning Up Test Data ═══[/bold yellow]\n")
        
        if not self.created_guids:
            console.print("No elements to clean up")
            return
        
        cleanup_results = {"success": 0, "failed": 0, "not_found": 0}
        
        # Reverse to handle dependencies if any
        for guid in reversed(self.created_guids):
            try:
                # Try deleting as context event first
                self.tk_client.delete_context_event(guid, {"class": "DeleteElementRequestBody"})
                cleanup_results["success"] += 1
            except Exception:
                try:
                    # Try deleting as asset
                    self.asset_maker.delete_asset(guid)
                    cleanup_results["success"] += 1
                except PyegeriaNotFoundException:
                    cleanup_results["not_found"] += 1
                except Exception:
                    cleanup_results["failed"] += 1
        
        console.print(f"Cleanup complete: {cleanup_results['success']} deleted, {cleanup_results['not_found']} already gone, {cleanup_results['failed']} failed")

    def print_results_summary(self):
        """Display summary of all test results"""
        table = Table(title=f"Time Keeper Scenario Test Results - {self.test_run_id}")
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

    def scenario_context_event_lifecycle(self) -> TestResult:
        """Scenario: Create, Link, Find and Delete Context Events"""
        name = "Context Event Lifecycle"
        start_time = time.perf_counter()
        created = []
        
        try:
            console.print(f"\n[bold blue]Scenario: {name}[/bold blue]")
            
            # 1. Create two context events
            ce1_qname = f"CE1::{self.test_run_id}"
            ce1_guid = self.tk_client.create_context_event({
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "ContextEventProperties",
                    "qualifiedName": ce1_qname,
                    "displayName": "Parent Event",
                }
            })
            created.append(ce1_guid)
            console.print(f"  ✓ Created Parent Context Event: {ce1_guid}")

            ce2_qname = f"CE2::{self.test_run_id}"
            ce2_guid = self.tk_client.create_context_event({
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "ContextEventProperties",
                    "qualifiedName": ce2_qname,
                    "displayName": "Child Event",
                }
            })
            created.append(ce2_guid)
            console.print(f"  ✓ Created Child Context Event: {ce2_guid}")

            # 2. Link them as dependent
            self.tk_client.link_dependent_context_events(ce1_guid, ce2_guid, {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "DependentContextEventProperties",
                    "description": "CE2 depends on CE1"
                }
            })
            console.print("  ✓ Linked CE1 and CE2 as dependent")

            # 3. Create an asset to link as evidence
            asset_qname = f"Asset::Evidence::{self.test_run_id}"
            asset_body = {
                  "class" : "NewElementRequestBody",

                  "isOwnAnchor": True,
                  "properties": {
                    "class" : "AssetProperties",
                    "qualifiedName": asset_qname,
                    "displayName": "Evidence Asset",
                    "description": "mew"
                  },

                }
            asset_guid = self.asset_maker.create_asset(body=asset_body)
            console.print(asset_guid)
            created.append(asset_guid)
            console.print(f"  ✓ Created Evidence Asset: {asset_guid}")

            # 4. Link asset as evidence to CE1
            self.tk_client.link_context_event_evidence(ce1_guid, asset_guid, {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "ContextEventEvidenceProperties",
                    "description": "Proof of event"
                }
            })
            console.print("  ✓ Linked asset as evidence to CE1")

            # 5. Find and verify
            events = self.tk_client.find_context_events(search_string=self.test_run_id)
            assert len(events) >= 2
            console.print(f"  ✓ Found {len(events)} context events matching test run ID")

            self.created_guids.extend(created)
            return TestResult(name, "PASSED", time.perf_counter() - start_time, "Successfully completed lifecycle", created_guids=created)

        except Exception as e:
            self.created_guids.extend(created)
            return TestResult(name, "FAILED", time.perf_counter() - start_time, str(e), error=e, created_guids=created)

    def run_all_scenarios(self):
        """Execute all defined scenarios"""
        if not self.setup():
            return
            
        try:
            self.results.append(self.scenario_context_event_lifecycle())
        finally:
            self.cleanup_created_elements()
            self.print_results_summary()
            self.teardown()


def test_time_keeper_scenarios():
    tester = TimeKeeperScenarioTester()
    tester.run_all_scenarios()
    
    # Assert all passed for pytest
    for res in tester.results:
        assert res.status == "PASSED", f"Scenario {res.scenario_name} failed: {res.message}"

if __name__ == "__main__":
    test_time_keeper_scenarios()
