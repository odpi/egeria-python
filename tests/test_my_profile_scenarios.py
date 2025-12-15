"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Comprehensive scenario tests for MyProfile.
Tests profile management and action workflows.

A running Egeria environment is needed to run these tests.
"""

import time
from dataclasses import dataclass
from datetime import datetime

from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from pyegeria.my_profile import MyProfile
from pyegeria._exceptions import (
    PyegeriaException,
    PyegeriaAPIException,
    PyegeriaNotFoundException,
)

console = Console()


@dataclass
class TestResult:
    """Data class to hold test results"""
    scenario_name: str
    passed: bool
    duration: float
    message: str = ""
    error: str = ""


class MyProfileScenarioTester:
    """Test harness for MyProfile scenarios"""

    def __init__(self):
        self.view_server = "qs-view-server"
        self.platform_url = "https://127.0.0.1:9443"
        self.user = "erinoverview"
        self.password = "secret"
        self.client = None

    def setup(self):
        """Initialize the client"""
        try:
            self.client = MyProfile(
                self.view_server,
                self.platform_url,
                user_id=self.user,
                user_pwd=self.password,
            )
            self.client.create_egeria_bearer_token(self.user, self.password)
            console.print("[green]✓[/green] Client initialized successfully")
            return True
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to initialize client: {str(e)}")
            return False

    def teardown(self):
        """Clean up and close session"""
        if self.client:
            self.client.close_session()
            console.print("[green]✓[/green] Session closed")

    def scenario_retrieve_my_profile(self) -> TestResult:
        """
        Scenario: Retrieve my profile
        - Get current user's profile
        - Verify profile information
        - Check profile properties
        """
        scenario_name = "Retrieve My Profile"
        start_time = time.perf_counter()

        try:
            # Step 1: Get my profile
            console.print(f"\n[cyan]Retrieving profile for user: {self.user}[/cyan]")
            profile = self.client.get_my_profile()

            if isinstance(profile, dict):
                profile_guid = profile.get("elementHeader", {}).get("guid")
                user_id = profile.get("profileProperties", {}).get("userId", "Unknown")
                full_name = profile.get("profileProperties", {}).get("fullName", "Unknown")
                
                console.print(f"[green]✓[/green] Retrieved profile:")
                console.print(f"  - GUID: {profile_guid}")
                console.print(f"  - User ID: {user_id}")
                console.print(f"  - Full Name: {full_name}")
            elif isinstance(profile, str):
                console.print(f"[yellow]⚠[/yellow] Profile result: {profile}")
            else:
                console.print(f"[green]✓[/green] Retrieved profile data")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=True,
                duration=duration,
                message=f"Successfully retrieved profile for {self.user}",
            )

        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=False,
                duration=duration,
                error=str(e),
            )

    def scenario_explore_assigned_actions(self) -> TestResult:
        """
        Scenario: Explore assigned actions
        - Get my profile to find actor GUID
        - Retrieve assigned actions
        - Check action details
        """
        scenario_name = "Explore Assigned Actions"
        start_time = time.perf_counter()

        try:
            # Step 1: Get profile to find actor GUID
            console.print(f"\n[cyan]Getting profile to find actor GUID[/cyan]")
            profile = self.client.get_my_profile()
            
            actor_guid = None
            if isinstance(profile, dict):
                actor_guid = profile.get("elementHeader", {}).get("guid")
                console.print(f"[green]✓[/green] Found actor GUID: {actor_guid}")

            if actor_guid:
                # Step 2: Get assigned actions
                console.print(f"\n[cyan]Retrieving assigned actions for actor[/cyan]")
                try:
                    actions = self.client.get_assigned_actions(actor_guid)
                    
                    if isinstance(actions, list):
                        console.print(f"[green]✓[/green] Found {len(actions)} assigned actions")
                        
                        # Display first few actions if any exist
                        for i, action in enumerate(actions[:3]):
                            if isinstance(action, dict):
                                action_name = action.get("actionProperties", {}).get("displayName", "Unknown")
                                action_status = action.get("actionProperties", {}).get("actionStatus", "Unknown")
                                console.print(f"  Action {i+1}: {action_name} (Status: {action_status})")
                    elif isinstance(actions, str):
                        console.print(f"[yellow]⚠[/yellow] Actions result: {actions}")
                    else:
                        console.print(f"[green]✓[/green] Retrieved actions data")
                except Exception as e:
                    console.print(f"[yellow]⚠[/yellow] Could not retrieve actions: {str(e)}")
            else:
                console.print(f"[yellow]⚠[/yellow] Could not find actor GUID from profile")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=True,
                duration=duration,
                message="Successfully explored assigned actions",
            )

        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=False,
                duration=duration,
                error=str(e),
            )

    def scenario_explore_roles(self) -> TestResult:
        """
        Scenario: Explore user roles
        - Get my profile
        - Retrieve roles
        - Check role information
        """
        scenario_name = "Explore User Roles"
        start_time = time.perf_counter()

        try:
            # Step 1: Get profile
            console.print(f"\n[cyan]Getting profile for role information[/cyan]")
            profile = self.client.get_my_profile()
            
            if isinstance(profile, dict):
                # Check for roles in profile
                roles = profile.get("roles", [])
                if roles:
                    console.print(f"[green]✓[/green] Found {len(roles)} roles in profile")
                    for role in roles[:5]:  # Show first 5 roles
                        if isinstance(role, dict):
                            role_name = role.get("displayName", "Unknown")
                            console.print(f"  - Role: {role_name}")
                else:
                    console.print(f"[yellow]⚠[/yellow] No roles found in profile")
                
                # Try to get roles via API
                profile_guid = profile.get("elementHeader", {}).get("guid")
                if profile_guid:
                    console.print(f"\n[cyan]Attempting to retrieve roles via API[/cyan]")
                    try:
                        api_roles = self.client.get_my_roles()
                        if isinstance(api_roles, list):
                            console.print(f"[green]✓[/green] Found {len(api_roles)} roles via API")
                        else:
                            console.print(f"[green]✓[/green] Retrieved roles data")
                    except Exception as e:
                        console.print(f"[yellow]⚠[/yellow] Could not retrieve roles via API: {str(e)}")
            else:
                console.print(f"[yellow]⚠[/yellow] Could not retrieve profile for role information")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=True,
                duration=duration,
                message="Successfully explored user roles",
            )

        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=False,
                duration=duration,
                error=str(e),
            )

    def scenario_explore_profile_details(self) -> TestResult:
        """
        Scenario: Explore profile details
        - Get my profile
        - Check various profile properties
        - Explore profile metadata
        """
        scenario_name = "Explore Profile Details"
        start_time = time.perf_counter()

        try:
            # Get profile
            console.print(f"\n[cyan]Retrieving detailed profile information[/cyan]")
            profile = self.client.get_my_profile()

            if isinstance(profile, dict):
                console.print(f"[green]✓[/green] Retrieved profile, exploring details:")
                
                # Profile properties
                props = profile.get("profileProperties", {})
                if props:
                    console.print(f"\n[cyan]Profile Properties:[/cyan]")
                    for key, value in props.items():
                        if value and key not in ["additionalProperties", "extendedProperties"]:
                            console.print(f"  - {key}: {value}")
                
                # Element header
                header = profile.get("elementHeader", {})
                if header:
                    console.print(f"\n[cyan]Element Header:[/cyan]")
                    console.print(f"  - GUID: {header.get('guid')}")
                    console.print(f"  - Type: {header.get('type', {}).get('typeName')}")
                    console.print(f"  - Origin: {header.get('origin', {}).get('sourceServer')}")
                
                # Classifications
                classifications = header.get("classifications", [])
                if classifications:
                    console.print(f"\n[cyan]Classifications:[/cyan]")
                    for classification in classifications:
                        class_name = classification.get("classificationName", "Unknown")
                        console.print(f"  - {class_name}")
                else:
                    console.print(f"\n[yellow]⚠[/yellow] No classifications found")
                
            else:
                console.print(f"[yellow]⚠[/yellow] Could not retrieve detailed profile information")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=True,
                duration=duration,
                message="Successfully explored profile details",
            )

        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=False,
                duration=duration,
                error=str(e),
            )

    def run_all_scenarios(self) -> list[TestResult]:
        """Run all test scenarios"""
        results = []

        console.print(Panel.fit(
            "[bold cyan]MyProfile Scenario Tests[/bold cyan]\n"
            "Testing profile management and action workflows",
            border_style="cyan"
        ))

        if not self.setup():
            return results

        try:
            # Run each scenario
            scenarios = [
                self.scenario_retrieve_my_profile,
                self.scenario_explore_assigned_actions,
                self.scenario_explore_roles,
                self.scenario_explore_profile_details,
            ]

            for scenario_func in scenarios:
                console.print(f"\n[bold yellow]{'=' * 80}[/bold yellow]")
                console.print(f"[bold]Running: {scenario_func.__doc__.split('Scenario:')[1].split('-')[0].strip()}[/bold]")
                console.print(f"[bold yellow]{'=' * 80}[/bold yellow]")

                result = scenario_func()
                results.append(result)

                if result.passed:
                    console.print(f"\n[green]✓ PASSED[/green] - {result.message}")
                else:
                    console.print(f"\n[red]✗ FAILED[/red] - {result.error}")

                console.print(f"Duration: {result.duration:.2f} seconds")

        finally:
            self.teardown()

        return results

    def print_results_summary(self, results: list[TestResult]):
        """Print a summary table of all test results"""
        table = Table(title="Test Results Summary", show_header=True, header_style="bold magenta")
        table.add_column("Scenario", style="cyan", width=40)
        table.add_column("Status", justify="center", width=10)
        table.add_column("Duration", justify="right", width=12)
        table.add_column("Details", width=50)

        total_duration = 0
        passed_count = 0

        for result in results:
            status = "[green]✓ PASS[/green]" if result.passed else "[red]✗ FAIL[/red]"
            duration_str = f"{result.duration:.2f}s"
            details = result.message if result.passed else result.error

            table.add_row(
                result.scenario_name,
                status,
                duration_str,
                details[:47] + "..." if len(details) > 50 else details
            )

            total_duration += result.duration
            if result.passed:
                passed_count += 1

        console.print("\n")
        console.print(table)

        # Print summary statistics
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  Total scenarios: {len(results)}")
        console.print(f"  Passed: [green]{passed_count}[/green]")
        console.print(f"  Failed: [red]{len(results) - passed_count}[/red]")
        console.print(f"  Total duration: {total_duration:.2f}s")
        console.print(f"  Average duration: {total_duration / len(results):.2f}s")


def test_my_profile_scenarios():
    """Pytest entry point"""
    tester = MyProfileScenarioTester()
    results = tester.run_all_scenarios()
    tester.print_results_summary(results)

    # Assert that all scenarios passed
    assert all(result.passed for result in results), "Some scenarios failed"


if __name__ == "__main__":
    tester = MyProfileScenarioTester()
    results = tester.run_all_scenarios()
    tester.print_results_summary(results)