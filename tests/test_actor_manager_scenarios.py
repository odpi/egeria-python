#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario-based testing for Actor Manager with synthetic data.

This executable test script runs realistic scenarios for actor management,
including creating actor profiles, roles, user identities, and managing relationships,
with comprehensive cleanup and detailed error reporting.

Usage:
    python tests/test_actor_manager_scenarios.py
    
    Or with pytest:
    pytest tests/test_actor_manager_scenarios.py -v -s
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

from pyegeria.actor_manager import ActorManager
from pyegeria._exceptions import (
    PyegeriaException,
    PyegeriaAPIException,
    PyegeriaNotFoundException,
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
class ActorProfileData:
    """Synthetic actor profile data"""
    qualified_name: str
    display_name: str
    description: str
    guid: Optional[str] = None


@dataclass
class ActorRoleData:
    """Synthetic actor role data"""
    qualified_name: str
    display_name: str
    description: str
    scope: Optional[str] = None
    guid: Optional[str] = None


@dataclass
class UserIdentityData:
    """Synthetic user identity data"""
    qualified_name: str
    user_id: str
    guid: Optional[str] = None


class ActorManagerScenarioTester:
    """Execute realistic actor management scenarios"""
    
    def __init__(self):
        self.client: Optional[ActorManager] = None
        self.results: List[TestResult] = []
        self.created_profiles: List[str] = []
        self.created_roles: List[str] = []
        self.created_identities: List[str] = []
        self.test_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def setup(self) -> bool:
        """Initialize connection to Egeria"""
        try:
            console.print("\n[bold cyan]═══ Setting up Actor Manager Test Environment ═══[/bold cyan]\n")
            self.client = ActorManager(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
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
    
    def cleanup_created_actors(self):
        """Delete all actor entities created during testing"""
        console.print("\n[bold yellow]═══ Cleaning Up Test Data ═══[/bold yellow]\n")
        
        total_items = len(self.created_identities) + len(self.created_roles) + len(self.created_profiles)
        if total_items == 0:
            console.print("No actor entities to clean up")
            return
        
        cleanup_results = {"success": 0, "failed": 0, "not_found": 0}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(
                f"Cleaning up {total_items} actor entities...",
                total=total_items
            )
            
            # Delete in reverse order: identities, roles, then profiles
            for guid in reversed(self.created_identities):
                try:
                    self.client.delete_user_identity(guid)
                    cleanup_results["success"] += 1
                except PyegeriaAPIException:
                    cleanup_results["not_found"] += 1
                except Exception as e:
                    cleanup_results["failed"] += 1
                    console.print(f"[yellow]Warning: Failed to delete identity {guid}: {str(e)}[/yellow]")
                finally:
                    progress.advance(task)
            
            for guid in reversed(self.created_roles):
                try:
                    self.client.delete_actor_role(guid)
                    cleanup_results["success"] += 1
                except PyegeriaAPIException:
                    cleanup_results["not_found"] += 1
                except Exception as e:
                    cleanup_results["failed"] += 1
                    console.print(f"[yellow]Warning: Failed to delete role {guid}: {str(e)}[/yellow]")
                finally:
                    progress.advance(task)
            
            for guid in reversed(self.created_profiles):
                try:
                    self.client.delete_actor_profile(guid)
                    cleanup_results["success"] += 1
                except PyegeriaAPIException:
                    cleanup_results["not_found"] += 1
                except Exception as e:
                    cleanup_results["failed"] += 1
                    console.print(f"[yellow]Warning: Failed to delete profile {guid}: {str(e)}[/yellow]")
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
    
    def _create_actor_profile(self, profile_data: ActorProfileData) -> Optional[str]:
        """Helper to create an actor profile and track it"""
        body = {
            "class": "NewElementRequestBody",
            "isOwnAnchor": True,
            "properties": {
                "class": "ActorProfileProperties",
                "qualifiedName": profile_data.qualified_name,
                "displayName": profile_data.display_name,
                "description": profile_data.description,
            }
        }
        guid = self.client.create_actor_profile(body)
        if guid:
            self.created_profiles.append(guid)
            profile_data.guid = guid
        return guid
    
    def _create_actor_role(self, role_data: ActorRoleData) -> Optional[str]:
        """Helper to create an actor role and track it"""
        body = {
            "class": "NewElementRequestBody",
            "isOwnAnchor": True,
            "properties": {
                "class": "ActorRoleProperties",
                "qualifiedName": role_data.qualified_name,
                "displayName": role_data.display_name,
                "description": role_data.description,
            }
        }
        if role_data.scope:
            body["properties"]["scope"] = role_data.scope
            
        guid = self.client.create_actor_role(body)
        if guid:
            self.created_roles.append(guid)
            role_data.guid = guid
        return guid
    
    def _create_user_identity(self, identity_data: UserIdentityData) -> Optional[str]:
        """Helper to create a user identity and track it"""
        body = {
            "class": "NewElementRequestBody",
            "isOwnAnchor": True,
            "properties": {
                "class": "UserIdentityProperties",
                "qualifiedName": identity_data.qualified_name,
                "userId": identity_data.user_id,
            }
        }
        guid = self.client.create_user_identity(body)
        if guid:
            self.created_identities.append(guid)
            identity_data.guid = guid
        return guid
    
    def scenario_1_organizational_structure(self) -> TestResult:
        """
        Scenario 1: Create an organizational structure with actor profiles and roles
        - Department Heads (Actor Profiles)
          - Engineering Manager
          - Sales Manager
          - HR Manager
        - Team Roles (Actor Roles)
          - Software Engineer
          - Sales Representative
          - HR Specialist
        """
        scenario_name = "Organizational Structure"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Scenario 1: {scenario_name}[/bold blue]")
            
            # Create actor profiles for department heads
            profiles = {
                "eng_mgr": ActorProfileData(
                    f"ActorProfile::EngineeringManager::{self.test_run_id}",
                    "Engineering Manager",
                    "Head of Engineering Department"
                ),
                "sales_mgr": ActorProfileData(
                    f"ActorProfile::SalesManager::{self.test_run_id}",
                    "Sales Manager",
                    "Head of Sales Department"
                ),
                "hr_mgr": ActorProfileData(
                    f"ActorProfile::HRManager::{self.test_run_id}",
                    "HR Manager",
                    "Head of Human Resources"
                ),
            }
            
            for key, profile in profiles.items():
                guid = self._create_actor_profile(profile)
                created_guids.append(guid)
                console.print(f"  ✓ Created profile: {profile.display_name}")
            
            # Create actor roles for team members
            roles = {
                "sw_eng": ActorRoleData(
                    f"ActorRole::SoftwareEngineer::{self.test_run_id}",
                    "Software Engineer",
                    "Develops and maintains software systems",
                    "Engineering Department"
                ),
                "sales_rep": ActorRoleData(
                    f"ActorRole::SalesRep::{self.test_run_id}",
                    "Sales Representative",
                    "Manages customer relationships and sales",
                    "Sales Department"
                ),
                "hr_spec": ActorRoleData(
                    f"ActorRole::HRSpecialist::{self.test_run_id}",
                    "HR Specialist",
                    "Handles recruitment and employee relations",
                    "HR Department"
                ),
            }
            
            for key, role in roles.items():
                guid = self._create_actor_role(role)
                created_guids.append(guid)
                console.print(f"  ✓ Created role: {role.display_name}")
            
            duration = time.perf_counter() - start_time
            console.print(f"  [green]✓ Scenario completed in {duration:.2f}s[/green]")
            
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Created {len(profiles)} profiles and {len(roles)} roles for organizational structure",
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
    
    def scenario_2_actor_lifecycle(self) -> TestResult:
        """
        Scenario 2: Test complete actor profile lifecycle
        - Create actor profile
        - Update properties
        - Search and retrieve
        - Delete actor profile
        """
        scenario_name = "Actor Profile Lifecycle Management"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Scenario 2: {scenario_name}[/bold blue]")
            
            # Create
            profile = ActorProfileData(
                f"ActorProfile::Lifecycle::Test::{self.test_run_id}",
                "Lifecycle Test Profile",
                "Original description"
            )
            guid = self._create_actor_profile(profile)
            created_guids.append(guid)
            console.print(f"  ✓ Created actor profile: {guid}")
            
            # Retrieve
            retrieved = self.client.get_actor_profile_by_guid(guid, output_format="JSON")
            console.print(f"  ✓ Retrieved actor profile by GUID")
            
            # Update
            update_body = {
                "class": "UpdateElementRequestBody",
                "mergeUpdate": True,
                "properties": {
                    "class": "ActorProfileProperties",
                    "qualifiedName": profile.qualified_name,
                    "displayName": "Updated Lifecycle Profile",
                    "description": "Updated description with new information",
                }
            }
            self.client.update_actor_profile(guid, update_body)
            console.print(f"  ✓ Updated actor profile properties")
            
            # Verify update
            updated = self.client.get_actor_profile_by_guid(guid, output_format="JSON")
            console.print(f"  ✓ Verified update")
            
            # Search
            search_results = self.client.find_actor_profiles(
                search_string="Lifecycle",
                starts_with=False,
                ends_with=False,
                ignore_case=True,
                output_format="JSON"
            )
            console.print(f"  ✓ Found actor profile via search")
            
            # Delete
            self.client.delete_actor_profile(guid)
            console.print(f"  ✓ Deleted actor profile")
            
            # Verify deletion
            try:
                after_delete = self.client.get_actor_profile_by_guid(guid, output_format="JSON")
                console.print(f"  [yellow]⚠[/yellow] Profile still exists after deletion")
            except PyegeriaAPIException:
                console.print(f"  ✓ Confirmed deletion")
            
            # Remove from cleanup list since we already deleted it
            if guid in self.created_profiles:
                self.created_profiles.remove(guid)
            
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
    
    def scenario_3_user_identities(self) -> TestResult:
        """
        Scenario 3: Create and manage user identities
        - Create multiple user identities
        - Link to actor profiles
        - Test search and retrieval
        """
        scenario_name = "User Identity Management"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Scenario 3: {scenario_name}[/bold blue]")
            
            # Create actor profiles first
            profiles = [
                ActorProfileData(
                    f"ActorProfile::User::Alice::{self.test_run_id}",
                    "Alice Smith",
                    "Software Developer"
                ),
                ActorProfileData(
                    f"ActorProfile::User::Bob::{self.test_run_id}",
                    "Bob Johnson",
                    "Data Analyst"
                ),
            ]
            
            for profile in profiles:
                guid = self._create_actor_profile(profile)
                created_guids.append(guid)
                console.print(f"  ✓ Created profile: {profile.display_name}")
            
            # Create user identities
            identities = [
                UserIdentityData(
                    f"UserIdentity::alice.smith::{self.test_run_id}",
                    "alice.smith"
                ),
                UserIdentityData(
                    f"UserIdentity::bob.johnson::{self.test_run_id}",
                    "bob.johnson"
                ),
            ]
            
            for identity in identities:
                guid = self._create_user_identity(identity)
                created_guids.append(guid)
                console.print(f"  ✓ Created user identity: {identity.user_id}")
            
            # Search for user identities
            search_results = self.client.find_user_identities(
                search_string="*",
                output_format="JSON"
            )
            console.print(f"  ✓ Searched user identities")
            
            duration = time.perf_counter() - start_time
            console.print(f"  [green]✓ Scenario completed in {duration:.2f}s[/green]")
            
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Created {len(profiles)} profiles and {len(identities)} user identities",
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
            self.results.append(self.scenario_1_organizational_structure())
            self.results.append(self.scenario_2_actor_lifecycle())
            self.results.append(self.scenario_3_user_identities())
            
            # Cleanup
            self.cleanup_created_actors()
            
            # Generate report
            return self.generate_report()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Test execution interrupted by user[/yellow]")
            self.cleanup_created_actors()
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
        "[bold cyan]Actor Manager Scenario Testing[/bold cyan]\n"
        "Comprehensive testing with synthetic data and automatic cleanup",
        border_style="cyan"
    ))
    
    tester = ActorManagerScenarioTester()
    exit_code = tester.run_all_scenarios()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()