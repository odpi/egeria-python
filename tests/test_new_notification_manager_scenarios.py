#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario-based lifecycle testing for the Egeria Notification Manager.
This script tests creating resources, linking them via the Notification Manager,
and performing a clean teardown.

uv run tests/test_new_notification_manager_scenarios.py

pytest tests/test_new_notification_manager_scenarios.py -v -s
"""

# !/usr/bin/env python3
"""
Functional Lifecycle Scenario for Notification Manager.
Tests resource creation, subscriber linking, and cleanup using the EgeriaTech client.
"""

import time
from datetime import datetime
from typing import List
from dataclasses import dataclass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.omvs.notification_manager import NotificationManager
from pyegeria.core._exceptions import PyegeriaException, print_exception_table

# Configuration
VIEW_SERVER = "view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"

console = Console(width=150)


@dataclass
class TestResult:
    step: str
    status: str
    duration: float
    details: str = ""


class NotificationScenarioRunner:
    def __init__(self):
        # Use EgeriaTech for resource creation (Collections/Actors)
        self.tech_client = EgeriaTech(VIEW_SERVER, PLATFORM_URL, USER_ID, USER_PWD)
        # Use dedicated NotificationManager for linking
        self.nm_client = NotificationManager(VIEW_SERVER, PLATFORM_URL, USER_ID, USER_PWD)

        self.created_guids: List[str] = []
        self.results: List[TestResult] = []

    def setup(self) -> bool:
        try:
            console.print(Panel("[bold cyan]PRE-FLIGHT: Authenticating Clients[/bold cyan]"))
            token = self.tech_client.create_egeria_bearer_token(USER_ID, USER_PWD)
            self.nm_client.token = token
            console.print(f"  [green]✓[/green] Connected to {PLATFORM_URL} as {USER_ID}")
            return True
        except Exception as e:
            console.print(f"  [red]✗ Authentication failed: {e}[/red]")
            return False

    def run_scenario(self):
        ts = datetime.now().strftime("%H%M%S")
        start_scenario = time.perf_counter()

        try:
            # STEP 1: Create Notification Type
            step = "Create Notification Type"
            s_start = time.perf_counter()
            console.print(f"\n[bold blue]Step 1: {step}...[/bold blue]")
            nt_guid = self.tech_client.create_collection(
                display_name=f"Alerts-{ts}",
                description="Lifecycle Notification Type",
                collection_type="NotificationType",
                is_own_anchor=True
            )
            self.created_guids.append(nt_guid)
            self.results.append(TestResult(step, "SUCCESS", time.perf_counter() - s_start, nt_guid))

            # STEP 2: Create Monitored Resource
            step = "Create Monitored Resource"
            s_start = time.perf_counter()
            console.print(f"[bold blue]Step 2: {step}...[/bold blue]")
            res_guid = self.tech_client.create_collection(
                display_name=f"Resource-{ts}",
                description="Monitored Lifecycle Asset",
                collection_type="MonitoredResource",
                is_own_anchor=True
            )
            self.created_guids.append(res_guid)
            self.results.append(TestResult(step, "SUCCESS", time.perf_counter() - s_start, res_guid))

            # STEP 3: Link via Notification Manager
            step = "Link Resource"
            s_start = time.perf_counter()
            console.print(f"[bold blue]Step 3: {step}...[/bold blue]")
            # RelationshipProperties is the safe base class for generic links
            link_body = {"class": "RelationshipProperties", "label": "Lifecycle-Link"}
            self.nm_client.link_monitored_resource(nt_guid, res_guid, body=link_body)
            self.results.append(TestResult(step, "SUCCESS", time.perf_counter() - s_start, "Link established"))

            # STEP 4: Detach
            step = "Detach Resource"
            s_start = time.perf_counter()
            console.print(f"[bold blue]Step 4: {step}...[/bold blue]")
            self.nm_client.detach_monitored_resource(nt_guid, res_guid)
            self.results.append(TestResult(step, "SUCCESS", time.perf_counter() - s_start, "Link removed"))

        except Exception as e:
            console.print(f"\n[bold red]✗ Scenario Interrupted: {e}[/bold red]")
            if isinstance(e, PyegeriaException):
                print_exception_table(e)
            self.results.append(TestResult("Critical Failure", "ERROR", 0.0, str(e)))

    def cleanup(self):
        console.print("\n[bold yellow]TEARDOWN: Cleaning up synthetic data...[/bold yellow]")
        for guid in reversed(self.created_guids):
            try:
                # EgeriaTech delegates delete_collection via CollectionManager
                self.tech_client.delete_collection(guid)
                console.print(f"  • Deleted: {guid}")
            except Exception:
                pass
        self.tech_client.close_session()
        self.nm_client.close_session()

    def report(self):
        table = Table(title="\nNotification Manager Lifecycle Report", show_lines=True)
        table.add_column("Step", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Time (s)", justify="right")
        table.add_column("Details")

        for r in self.results:
            stat = f"[green]{r.status}[/green]" if r.status == "SUCCESS" else f"[red]{r.status}[/red]"
            table.add_row(r.step, stat, f"{r.duration:.3f}", r.details)
        console.print(table)


def main():
    runner = NotificationScenarioRunner()
    if runner.setup():
        runner.run_scenario()
    runner.cleanup()
    runner.report()


if __name__ == "__main__":
    main()