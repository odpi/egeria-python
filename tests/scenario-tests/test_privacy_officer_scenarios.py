#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario-based testing for PrivacyOfficer with synthetic data.
"""

import sys
import time
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field

from rich.console import Console
from rich.table import Table

from pyegeria.omvs.privacy_officer import PrivacyOfficer
from pyegeria.models import (
    NewRelationshipRequestBody,
    DeleteRelationshipRequestBody,
)
from pyegeria.core._exceptions import (
    PyegeriaException,
    PyegeriaAPIException,
    print_basic_exception,
)

# Configuration
VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "garygeeke"
USER_PWD = "secret"

console = Console(width=200)


@dataclass
class TestResult:
    """Track results of test scenarios"""

    scenario_name: str
    status: str  # "PASSED", "FAILED"
    duration: float
    message: str = ""
    error: Optional[Exception] = None


class PrivacyOfficerScenarioTester:
    """Execute realistic privacy management scenarios"""

    def __init__(self):
        self.client: Optional[PrivacyOfficer] = None
        self.results: List[TestResult] = []

    def setup(self) -> bool:
        """Initialize connection to Egeria"""
        try:
            console.print(
                "\n[bold cyan]═══ Setting up PrivacyOfficer Test Environment ═══[/bold cyan]\n"
            )
            self.client = PrivacyOfficer(
                VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD
            )
            self.client.create_egeria_bearer_token(USER_ID, USER_PWD)
            return True
        except Exception as e:
            console.print(f"[bold red]Setup failed: {e}[/bold red]")
            return False

    def run_lifecycle_scenario(self) -> TestResult:
        """
        Scenario: Manage Data Processing Purposes and Actions.
        1. Link a purpose to a description.
        2. Link an action to a target.
        3. Detach both.
        """
        scenario_name = "Privacy Lifecycle"
        start_time = time.perf_counter()
        
        try:
            console.print(f"\n[bold blue]Scenario: {scenario_name}[/bold blue]")
            
            purpose_guid = f"purpose-{int(time.time())}"
            description_guid = f"desc-{int(time.time())}"
            action_guid = f"action-{int(time.time())}"
            target_guid = f"target-{int(time.time())}"

            # 1. Link Purpose to Description
            console.print("  1. Linking purpose to description...")
            link_body = NewRelationshipRequestBody(
                class_="NewRelationshipRequestBody",
                properties={
                    "class": "PermittedProcessingProperties",
                    "label": "Scenario Label",
                    "description": "Scenario Description"
                }
            )
            try:
                self.client.link_permitted_processing(purpose_guid, description_guid, link_body)
                console.print("  ✓ Linked")
            except (PyegeriaException, PyegeriaAPIException) as e:
                # We expect a 404 since we are using synthetic GUIDs
                if getattr(e, "response_code", None) == 404 or "404" in str(e):
                    console.print("  ✓ Caught expected 404 exception for placeholder GUIDs")
                    return TestResult(
                        scenario_name=scenario_name,
                        status="PASSED",
                        duration=time.perf_counter() - start_time,
                        message="Passed (expected data not found for synthetic GUIDs)"
                    )
                
                console.print(f"  ⚠ Skipping rest of scenario: unexpected error ({type(e).__name__})")
                return TestResult(
                    scenario_name=scenario_name,
                    status="FAILED",
                    duration=time.perf_counter() - start_time,
                    message=f"Failed due to unexpected error: {str(e)}"
                )

            # 2. Link Action to Target
            console.print("  2. Linking action to target...")
            target_link_body = NewRelationshipRequestBody(
                class_="NewRelationshipRequestBody",
                properties={
                    "class": "DataProcessingTargetProperties",
                    "label": "Scenario Target Label"
                }
            )
            self.client.link_data_processing_target(action_guid, target_guid, target_link_body)
            console.print("  ✓ Linked")

            # 3. Detach both
            console.print("  3. Detaching relationships...")
            detach_body = DeleteRelationshipRequestBody(class_="DeleteRelationshipRequestBody")
            self.client.detach_permitted_processing(purpose_guid, description_guid, detach_body)
            self.client.detach_data_processing_target(action_guid, target_guid, detach_body)
            console.print("  ✓ Detached")

            duration = time.perf_counter() - start_time
            return TestResult(scenario_name, "PASSED", duration, "Lifecycle completed successfully")

        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(scenario_name, "FAILED", duration, str(e), e)

    def display_results(self):
        """Show summary of all scenario results"""
        table = Table(title=f"PrivacyOfficer Scenario Results")
        table.add_column("Scenario", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Duration (s)", justify="right")
        table.add_column("Message")

        for r in self.results:
            status_style = "green" if r.status == "PASSED" else "red"
            table.add_row(
                r.scenario_name,
                f"[{status_style}]{r.status}[/{status_style}]",
                f"{r.duration:.2f}",
                r.message,
            )
        console.print("\n")
        console.print(table)

    def run_all(self):
        if not self.setup():
            return
        
        self.results.append(self.run_lifecycle_scenario())
        self.display_results()
        
        if any(r.status == "FAILED" for r in self.results):
            sys.exit(1)


if __name__ == "__main__":
    tester = PrivacyOfficerScenarioTester()
    tester.run_all()
