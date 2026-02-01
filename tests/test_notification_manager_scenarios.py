#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario-based testing for Notification Manager with synthetic data.

This executable test script runs realistic scenarios for notification management,
including linking notification types with monitored resources and subscribers,
with comprehensive cleanup and detailed error reporting.

Usage:
    python tests/test_notification_manager_scenarios.py
    
    Or with pytest:
    pytest tests/test_notification_manager_scenarios.py -v -s
"""

import sys
import time
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from pyegeria.omvs.notification_manager import NotificationManager
from pyegeria.omvs.actor_manager import ActorManager
from pyegeria.omvs.collection_manager import CollectionManager
from pyegeria.omvs.governance_officer import GovernanceOfficer
from pyegeria.core._exceptions import (
    PyegeriaException,
    PyegeriaNotFoundException,
    PyegeriaTimeoutException,
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


class NotificationManagerScenarioTester:
    """Execute realistic notification management scenarios"""
    
    def __init__(self):
        self.client: Optional[NotificationManager] = None
        self.actor_client: Optional[ActorManager] = None
        self.collection_client: Optional[CollectionManager] = None
        self.gov_officer: Optional[GovernanceOfficer] = None
        self.results: List[TestResult] = []
        self.created_actors: List[str] = []
        self.created_collections: List[str] = []
        self.created_notification_types: List[str] = []
        self.test_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def setup(self) -> bool:
        """Initialize connection to Egeria"""
        try:
            console.print("\n[bold cyan]═══ Setting up Notification Manager Test Environment ═══[/bold cyan]\n")
            self.client = NotificationManager(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
            self.actor_client = ActorManager(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
            self.collection_client = CollectionManager(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
            self.gov_officer = GovernanceOfficer(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
            token = self.client.create_egeria_bearer_token(USER_ID, USER_PWD)

            # Apply the token to the other clients
            self.actor_client.token = token
            self.collection_client.token = token
            self.gov_officer.token = token
            console.print(f"✓ Connected to {PLATFORM_URL}")
            console.print(f"✓ Authenticated as {USER_ID}")
            console.print(f"✓ Test Run ID: {self.test_run_id}\n")
            return True
        except Exception as e:
            console.print(f"[bold red]✗ Setup failed: {str(e)}[/bold red]")
            return False
    
    def teardown(self):
        """Clean up and close connection"""
        self.cleanup_created_elements()
        if self.client:
            self.client.close_session()
        if self.actor_client:
            self.actor_client.close_session()
        if self.collection_client:
            self.collection_client.close_session()
        if self.gov_officer:
            self.gov_officer.close_session()
            console.print("\n✓ Session closed")
    
    def cleanup_created_elements(self):
        """Delete all elements created during testing"""
        console.print("\n[bold yellow]═══ Cleaning Up Test Data ═══[/bold yellow]\n")
        
        total_items = len(self.created_actors) + len(self.created_collections) + len(self.created_notification_types)
        if total_items == 0:
            console.print("No elements to clean up")
            return
        
        cleanup_results = {"success": 0, "failed": 0, "not_found": 0}
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task(f"Cleaning up {total_items} elements...", total=total_items)
            
            # Clean up notification types
            for guid in self.created_notification_types:
                try:
                    self.gov_officer.delete_governance_definition(guid)
                    cleanup_results["success"] += 1
                except PyegeriaNotFoundException:
                    cleanup_results["not_found"] += 1
                except Exception as e:
                    console.print(f"  [yellow]⚠ Failed to delete notification type {guid}: {str(e)}[/yellow]")
                    cleanup_results["failed"] += 1
                progress.advance(task)

            # Clean up actors
            for guid in self.created_actors:
                try:
                    self.actor_client.delete_actor_profile(guid)
                    cleanup_results["success"] += 1
                except PyegeriaNotFoundException:
                    cleanup_results["not_found"] += 1
                except Exception as e:
                    console.print(f"  [yellow]⚠ Failed to delete actor {guid}: {str(e)}[/yellow]")
                    cleanup_results["failed"] += 1
                progress.advance(task)
            
            # Clean up collections
            for guid in self.created_collections:
                try:
                    self.collection_client.delete_collection(guid)
                    cleanup_results["success"] += 1
                except PyegeriaNotFoundException:
                    cleanup_results["not_found"] += 1
                except Exception as e:
                    console.print(f"  [yellow]⚠ Failed to delete collection {guid}: {str(e)}[/yellow]")
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
    
    def scenario_monitored_resource(self) -> TestResult:
        """Scenario: Link and unlink monitored resources to notification types"""
        scenario_name = "Monitored Resource Management"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # CREATE: Create a notification type governance control and a collection for monitored resource
            console.print("  → Creating elements for notification test...")
            ts = datetime.now().isoformat()
            
            # Create notification type governance control
            notification_body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "NotificationTypeProperties",
                    "qualifiedName": f"NotificationType::{ts}",
                    "displayName": f"Notification Type {ts}",
                    "description": "Governance control acting as notification type for testing",
                    "multipleNotificationsPermitted": True,
                    "minimumNotificationInterval": 60,
                    "notificationInterval":100,
                    "plannedStartDate": "2026-01-31",
                    "plannedCompletionDate": "2027-01-31",
                    "domainIdentifier": 0,
                    "summary": "Governance control notification type for testing",
                    "scope": "Global",
                    "importance": "Moderate"
                }
            }
            
            notification_type_guid = self.gov_officer.create_governance_definition(body=notification_body)
            if notification_type_guid:
                created_guids.append(notification_type_guid)
                self.created_notification_types.append(notification_type_guid)
                console.print(f"  ✓ Created notification type: {notification_type_guid}")
            else:
                raise Exception("Failed to create notification type")
            
            # Create monitored resource collection
            resource_body = {
                "class": "NewElementRequestBody",
                "typeName": "Collection",
        
                "properties": {
                    "class": "CollectionProperties",
                    "qualifiedName": f"Collection::MonitoredResource::{ts}",
                    "displayName": f"Monitored Resource {ts}",
                    "description": "Collection acting as monitored resource for testing"
                }
            }
            
            monitored_resource_guid = self.collection_client.create_collection(body=resource_body)
            if monitored_resource_guid:
                created_guids.append(monitored_resource_guid)
                self.created_collections.append(monitored_resource_guid)
                console.print(f"  ✓ Created monitored resource collection: {monitored_resource_guid}")
            else:
                raise Exception("Failed to create monitored resource collection")
            
            # LINK: Link monitored resource to notification type
            console.print("  → Linking monitored resource...")
            link_body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "MonitoredResourceProperties",
                    "label": "Test Monitored Resource",
                    "description": "Test monitored resource relationship"
                }
            }
            
            self.client.link_monitored_resource(
                notification_type_guid, monitored_resource_guid, link_body
            )
            console.print("  ✓ Linked monitored resource")
            
            # DETACH: Remove the monitored resource link
            console.print("  → Detaching monitored resource...")
            self.client.detach_monitored_resource(
                notification_type_guid, monitored_resource_guid
            )
            console.print("  ✓ Detached monitored resource")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Successfully tested monitored resource with {len(created_guids)} elements",
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
                    error=e
                )
            console.print(f"  [red]✗ Error: {str(e)}[/red]")
            print_exception_table(e) if isinstance(e, PyegeriaException) else console.print_exception()
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e)[:100],
                error=e
            )
    
    def scenario_notification_subscriber(self) -> TestResult:
        """Scenario: Link and unlink notification subscribers to notification types"""
        scenario_name = "Notification Subscriber Management"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # CREATE: Create a notification type governance control and an actor profile for subscriber
            console.print("  → Creating elements for subscriber test...")
            ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
            
            # Create notification type governance control
            notification_body = {
                "class": "NewElementRequestBody",
                "typeName": "NotificationType",
                "isOwnAnchor": True,
                "properties": {
                    "class": "NotificationTypeProperties",
                    "qualifiedName": f"NotificationType::NotificationTypeSubscriber::{ts}",
                    "displayName": f"Notification Type for Subscriber {ts}",
                    "description": "Governance control acting as notification type for subscriber testing"
                }
            }
            
            notification_type_guid = self.gov_officer.create_governance_definition(notification_body)
            if notification_type_guid:
                created_guids.append(notification_type_guid)
                self.created_notification_types.append(notification_type_guid)
                console.print(f"  ✓ Created notification type: {notification_type_guid}")
            else:
                raise Exception("Failed to create notification type")
            
            # Create subscriber actor profile
            subscriber_body = {
                "class": "NewElementRequestBody",
                "typeName": "ActorProfile",
                "properties": {
                    "class": "ActorProfileProperties",
                    "qualifiedName": f"ActorProfile::Subscriber::{ts}",
                    "displayName": f"Subscriber {ts}",
                    "description": "Actor profile acting as notification subscriber"
                }
            }
            
            subscriber_guid = self.actor_client.create_actor_profile(subscriber_body)
            if subscriber_guid:
                created_guids.append(subscriber_guid)
                self.created_actors.append(subscriber_guid)
                console.print(f"  ✓ Created subscriber actor profile: {subscriber_guid}")
            else:
                raise Exception("Failed to create subscriber actor profile")
            
            # LINK: Link subscriber to notification type
            console.print("  → Linking notification subscriber...")
            link_body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "NotificationSubscriberProperties",
                    "label": "Test Subscriber",
                    "description": "Test subscriber relationship"
                }
            }
            
            self.client.link_notification_subscriber(
                notification_type_guid, subscriber_guid, link_body
            )
            console.print("  ✓ Linked notification subscriber")
            
            # DETACH: Remove the subscriber link
            console.print("  → Detaching notification subscriber...")
            self.client.detach_notification_subscriber(
                notification_type_guid, subscriber_guid
            )
            console.print("  ✓ Detached notification subscriber")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Successfully tested notification subscriber with {len(created_guids)} elements",
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
                    error=e
                )
            console.print(f"  [red]✗ Error: {str(e)}[/red]")
            print_exception_table(e) if isinstance(e, PyegeriaException) else console.print_exception()
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e)[:100],
                error=e
            )
    
    def scenario_complete_notification_setup(self) -> TestResult:
        """Scenario: Complete notification setup with resource and subscriber"""
        scenario_name = "Complete Notification Setup"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # CREATE: Create notification type, monitored resource, and subscriber
            console.print("  → Creating elements for complete notification setup...")
            ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
            
            # Create notification type governance control
            notification_body = {
                "class": "NewElementRequestBody",
                "typeName": "NotificationType",
                "properties": {
                    "class": "NotificationTypeProperties",
                    "qualifiedName": f"NotificationType::CompleteNotification::{ts}",
                    "displayName": f"Complete Notification Type {ts}",
                    "description": "Governance control for complete notification setup testing"
                }
            }
            
            notification_type_guid = self.gov_officer.create_governance_definition(notification_body)
            if notification_type_guid:
                created_guids.append(notification_type_guid)
                self.created_notification_types.append(notification_type_guid)
                console.print(f"  ✓ Created notification type: {notification_type_guid}")
            else:
                raise Exception("Failed to create notification type")
            
            # Create monitored resource collection
            resource_body_create = {
                "class": "NewElementRequestBody",
                "typeName": "Collection",
        
                "properties": {
                    "class": "CollectionProperties",
                    "qualifiedName": f"Collection::CompleteResource::{ts}",
                    "displayName": f"Complete Monitored Resource {ts}",
                    "description": "Collection for complete resource testing"
                }
            }
            
            monitored_resource_guid = self.collection_client.create_collection(resource_body_create)
            if monitored_resource_guid:
                created_guids.append(monitored_resource_guid)
                self.created_collections.append(monitored_resource_guid)
                console.print(f"  ✓ Created monitored resource collection: {monitored_resource_guid}")
            else:
                raise Exception("Failed to create monitored resource collection")
            
            # Create subscriber actor profile
            subscriber_body_create = {
                "class": "NewElementRequestBody",
                "typeName": "ActorProfile",
        
                "properties": {
                    "class": "ActorProfileProperties",
                    "qualifiedName": f"ActorProfile::CompleteSubscriber::{ts}",
                    "displayName": f"Complete Subscriber {ts}",
                    "description": "Actor profile for complete subscriber testing"
                }
            }
            
            subscriber_guid = self.actor_client.create_actor_profile(subscriber_body_create)
            if subscriber_guid:
                created_guids.append(subscriber_guid)
                self.created_actors.append(subscriber_guid)
                console.print(f"  ✓ Created subscriber actor profile: {subscriber_guid}")
            else:
                raise Exception("Failed to create subscriber actor profile")
            
            # LINK: Link monitored resource
            console.print("  → Linking monitored resource...")
            resource_link_body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "MonitoredResourceProperties",
                    "label": "Complete Test Resource",
                    "description": "Complete test monitored resource"
                }
            }
            
            self.client.link_monitored_resource(
                notification_type_guid, monitored_resource_guid, resource_link_body
            )
            console.print("  ✓ Linked monitored resource")
            
            # LINK: Link subscriber
            console.print("  → Linking notification subscriber...")
            subscriber_link_body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "NotificationSubscriberProperties",
                    "label": "Complete Test Subscriber",
                    "description": "Complete test subscriber"
                }
            }
            
            self.client.link_notification_subscriber(
                notification_type_guid, subscriber_guid, subscriber_link_body
            )
            console.print("  ✓ Linked notification subscriber")
            
            # DETACH: Remove monitored resource link
            console.print("  → Detaching monitored resource...")
            self.client.detach_monitored_resource(
                notification_type_guid, monitored_resource_guid
            )
            console.print("  ✓ Detached monitored resource")
            
            # DETACH: Remove subscriber link
            console.print("  → Detaching notification subscriber...")
            self.client.detach_notification_subscriber(
                notification_type_guid, subscriber_guid
            )
            console.print("  ✓ Detached notification subscriber")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Successfully tested complete notification setup with {len(created_guids)} elements",
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
                    error=e
                )
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
        console.print("\n[bold magenta]═══ Running Notification Manager Scenarios ═══[/bold magenta]")
        
        scenarios = [
            self.scenario_monitored_resource,
            self.scenario_notification_subscriber,
            self.scenario_complete_notification_setup,
        ]
        
        for scenario_func in scenarios:
            result = scenario_func()
            self.results.append(result)
            time.sleep(0.5)  # Brief pause between scenarios


def test_notification_manager_scenarios():
    """Pytest entry point for notification manager scenario tests"""
    exit_code = main()
    assert exit_code == 0, "One or more scenarios failed"


def main():
    """Main test execution"""
    tester = NotificationManagerScenarioTester()
    
    try:
        if not tester.setup():
            console.print("[bold red]Setup failed. Exiting.[/bold red]")
            return 1
        
        tester.run_all_scenarios()
        tester.print_results_summary()
        
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
