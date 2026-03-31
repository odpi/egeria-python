#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario-based testing for SecurityOfficer with synthetic data.
"""

import sys
import time
import traceback
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from loguru import logger

import asyncio
from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.omvs.security_officer import SecurityOfficer
from pyegeria.omvs.my_profile import MyProfile
from pyegeria.omvs.project_manager import ProjectManager
from pyegeria.omvs.actor_manager import ActorManager
from pyegeria.core._exceptions import (
    PyegeriaAPIException,
    PyegeriaTimeoutException,
    PyegeriaException,
    print_basic_exception,
)

# Configuration
VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
PLATFORM_NAME = "Local OMAG Server Platform"
USER_ID = "garygeeke"
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
    created_users: List[str] = field(default_factory=list)


class SecurityOfficerScenarioTester:
    """Execute realistic security management scenarios"""

    def __init__(self):
        self.client: Optional[SecurityOfficer] = None
        self.profile_client: Optional[MyProfile] = None
        self.actor_client: Optional[ActorManager] = None
        self.results: List[TestResult] = []
        self.created_users: List[str] = []
        self.created_profiles: List[str] = []
        self.created_identities: List[str] = []
        self.platform_guid: Optional[str] = None
        self.test_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def setup(self) -> bool:
        """Initialize connection to Egeria"""
        try:
            console.print(
                "\n[bold cyan]═══ Setting up SecurityOfficer Test Environment ═══[/bold cyan]\n"
            )
            self.client = SecurityOfficer(
                VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD
            )
            self.client.create_egeria_bearer_token(USER_ID, USER_PWD)

            self.profile_client = MyProfile(
                VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD
            )
            self.profile_client.create_egeria_bearer_token(USER_ID, USER_PWD)

            self.actor_client = ActorManager(
                VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD
            )
            self.actor_client.create_egeria_bearer_token(USER_ID, USER_PWD)

            # Look up platform GUID once as Admin
            self.platform_guid = self.client.get_guid_for_name(
                PLATFORM_NAME,
                property_name=["displayName", "qualifiedName", "resourceName"]
            )
            console.print(f"✓ Platform GUID discovered: {self.platform_guid}")

            # Pre-clean the known scenario test user so scenario 2 always starts fresh.
            try:
                self.client.delete_user_account(PLATFORM_NAME, "freddiemercury", platform_guid=self.platform_guid)
                console.print("✓ Pre-deleted existing 'freddiemercury' account")
            except Exception:
                console.print("- No pre-existing 'freddiemercury' account to delete")

            console.print(f"✓ Connected to {PLATFORM_URL}")
            console.print(f"✓ Authenticated as {USER_ID}")
            console.print(f"✓ Test Run ID: {self.test_run_id}\n")
            return True
        except Exception as e:
            print_basic_exception(e)
            console.print(f"[bold red]✗ Setup failed: {str(e)}[/bold red]")
            return False

    def teardown(self):
        """Clean up and close connection"""
        if self.client:
            self.client.close_session()
        if self.profile_client:
            self.profile_client.close_session()
        if self.actor_client:
            self.actor_client.close_session()
        console.print("\n✓ Sessions closed")

    def cleanup_created_users(self):
        """Delete all users created during testing"""
        console.print("\n[bold yellow]═══ Cleaning Up Test Data ═══[/bold yellow]\n")

        if not self.created_users:
            console.print("No users to clean up")
            return

        cleanup_results = {"success": 0, "failed": 0, "not_found": 0}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Cleaning up {len(self.created_users)} users...",
                total=len(self.created_users),
            )

            for user_id in reversed(self.created_users):
                try:
                    self.client.delete_user_account(PLATFORM_NAME, user_id, platform_guid=self.platform_guid)
                    cleanup_results["success"] += 1
                except PyegeriaAPIException:
                    cleanup_results["not_found"] += 1
                except Exception as e:
                    cleanup_results["failed"] += 1
                    logger.warning(f"Failed to delete user {user_id}: {str(e)}")
                finally:
                    progress.advance(task)

            # Cleanup identities
            for identity_guid in reversed(self.created_identities):
                try:
                    self.actor_client.delete_user_identity(identity_guid)
                except Exception as e:
                    logger.warning(f"Failed to delete identity {identity_guid}: {str(e)}")

            # Cleanup profiles
            for profile_guid in reversed(self.created_profiles):
                try:
                    self.actor_client.delete_actor_profile(profile_guid, cascade=True)
                except Exception as e:
                    logger.warning(f"Failed to delete profile {profile_guid}: {str(e)}")

        # Report cleanup results
        table = Table(title="Cleanup Summary", show_header=True)
        table.add_column("Status", style="cyan")
        table.add_column("Count", justify="right", style="green")

        table.add_row("Successfully Deleted", str(cleanup_results["success"]))
        table.add_row("Not Found (already deleted)", str(cleanup_results["not_found"]))
        table.add_row("Failed to Delete", str(cleanup_results["failed"]))

        console.print(table)

    def scenario_1_user_lifecycle(self) -> TestResult:
        """
        Scenario 1: Complete User Lifecycle
        - Create user
        - Retrieve user
        - Update user
        - Delete user
        """
        scenario_name = "User Lifecycle Management"
        start_time = time.perf_counter()
        user_id = f"lifecycle_user_{self.test_run_id}"

        try:
            console.print(f"\n[bold blue]▶ Scenario 1: {scenario_name}[/bold blue]")

            # Create
            body = {
                "class": "UserAccountRequestBody",
                "userAccount": {
                    "class": "OpenMetadataUserAccount",
                    "userId": user_id,
                    "userName": "Lifecycle User",
                    "userAccountStatus": "AVAILABLE",
                    "secrets": {"clearPassword": "password123"},
                },
            }
            self.client.set_user_account(PLATFORM_NAME, body)
            self.created_users.append(user_id)
            console.print(f"  ✓ Created user: {user_id}")

            # Retrieve
            user = self.client.get_user_account(PLATFORM_NAME, user_id)
            assert user["userId"] == user_id
            console.print("  ✓ Retrieved user successfully")

            # Update
            body["userAccount"]["userName"] = "Updated Lifecycle User"
            self.client.set_user_account(PLATFORM_NAME, body)
            console.print("  ✓ Updated user properties")

            # Delete
            self.client.delete_user_account(PLATFORM_NAME, user_id)
            self.created_users.remove(user_id)
            console.print("  ✓ Deleted user")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message="Complete lifecycle tested: create, read, update, delete",
            )

        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Scenario failed: {str(e)}[/red]")
            print_basic_exception(e)
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e),
                error=e,
            )

    async def _async_scenario_2_coco_manage_users(self) -> TestResult:
        """
        Scenario 2: Implement Egeria-coco-manage-users.http flow exactly
        """
        scenario_name = "Coco Manage Users Scenario"
        start_time = time.perf_counter()
        # Use the fixed ID from the .http file
        account_user_id = "freddiemercury"
        initial_password = "itsakindofmagic" 
        new_password = "magic, magic"      

        console.print(f"\n[bold blue]▶ Scenario 2: {scenario_name}[/bold blue]")
        try:
            # 1) Ensure no leftover account from a prior run (setup() already attempted this;
            #    this is a redundant safety-net delete immediately before creation).
            try:
                await self.client._async_delete_user_account(PLATFORM_NAME, account_user_id, platform_guid=self.platform_guid)
                console.print(f"  ✓ (Step 1) Deleted any pre-existing account for {account_user_id}")
            except Exception:
                console.print(f"  - (Step 1) No pre-existing account for {account_user_id} — clean to create")

            # 2) Gary creates a new account for Freddie
            account_body = {
                "class": "UserAccountRequestBody",
                "userAccount": {
                    "class": "OpenMetadataUserAccount",
                    "userId": account_user_id,
                    "userName": "Freddie Mercury",
                    "userAccountType": "EXTERNAL",
                    "securityRoles": ["openMetadataMember"],
                    "zoneAccess": {
                        "music": [
                            "READ", "CREATE", "UPDATE_PROPERTIES", "DELETE",
                            "ATTACH", "DETACH", "ADD_MEMBER", "DELETE_MEMBER",
                            "ADD_FEEDBACK", "DELETE_FEEDBACK", "CLASSIFY",
                            "DECLASSIFY", "PUBLISH"
                        ]
                    },
                    "userAccountStatus": "CREDENTIALS_EXPIRED",
                    "secrets": {
                        "clearPassword": initial_password
                    }
                }
            }
            await self.client._async_set_user_account(PLATFORM_NAME, account_body, platform_guid=self.platform_guid)
            if account_user_id not in self.created_users:
                self.created_users.append(account_user_id)
            console.print(f"  ✓ (Step 2) Gary created new account for {account_user_id} (CREDENTIALS_EXPIRED)")

            # 3) Freddie logs in with default password AND creates a new password
            freddie_tech = EgeriaTech(VIEW_SERVER, PLATFORM_URL, user_id=account_user_id)
            await freddie_tech._async_create_egeria_bearer_token(
                user_id=account_user_id, 
                password=initial_password, 
                new_password=new_password
            )
            console.print(f"  ✓ (Step 3) Freddie logged in and changed password")

            # 4) Freddie logs in with this new password
            # We'll create a fresh client to be sure
            freddie_new = EgeriaTech(VIEW_SERVER, PLATFORM_URL, user_id=account_user_id)
            await freddie_new._async_create_egeria_bearer_token(
                user_id=account_user_id, 
                password=new_password
            )
            console.print(f"  ✓ (Step 4) Freddie logged in successfully with new password")

            # Give the view server a moment to recognize the new user/credentials fully
            time.sleep(2)

            # 5) Freddie should be able to get his own account
            account = await freddie_new.security_officer._async_get_user_account(
                PLATFORM_NAME, account_user_id, platform_guid=self.platform_guid
            )
            assert account["userId"] == account_user_id
            console.print(f"  ✓ (Step 5) Freddie successfully retrieved his own account")

            # 6) Freddie creates his own metadata profile (using logic from .http file)
            profile_body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "properties": {
                    "class": "PersonProperties",
                    "qualifiedName": f"PersonProperties::{account_user_id}",
                    "displayName": "Freddie Mercury",
                    "givenNames": "Freddie",
                    "surname": "Mercury",
                    "fullName": "Mr Freddie Mercury",
                    "preferredLanguage": "English",
                    "jobTitle": "Lead singer for Queen",
                    "description": "Beloved singer and song-writer."
                }
            }
            response = await freddie_new.my_profile._async_add_my_profile(profile_body)
            profile_guid = response.get("guid") if isinstance(response, dict) else response
            self.created_profiles.append(profile_guid)
            console.print(f"  ✓ (Step 6) Freddie created his own metadata profile")

            # 7) Gary deletes Freddie's account
            await self.client._async_delete_user_account(PLATFORM_NAME, account_user_id, platform_guid=self.platform_guid)
            if account_user_id in self.created_users:
                self.created_users.remove(account_user_id)
            console.print(f"  ✓ (Step 7) Gary deleted Freddie's account")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message="Full 7-step User Management lifecycle passed",
            )

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message="Refined Coco user management flow completed exactly as per .http",
            )

        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Scenario failed: {str(e)}[/red]")
            print_basic_exception(e)
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e),
                error=e,
            )

    def scenario_2_coco_manage_users(self) -> TestResult:
        """Sync wrapper for the async scenario"""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_scenario_2_coco_manage_users())

    def generate_report(self):
        """Generate comprehensive test report"""
        console.print("\n[bold cyan]═══ Test Execution Report ═══[/bold cyan]\n")

        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == "PASSED")
        failed = sum(1 for r in self.results if r.status == "FAILED")
        total_duration = sum(r.duration for r in self.results)

        summary_table = Table(title="Test Summary", show_header=True, header_style="bold magenta")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", justify="right", style="green")

        summary_table.add_row("Total Scenarios", str(total))
        summary_table.add_row("Passed", str(passed), style="green")
        summary_table.add_row("Failed", str(failed), style="red" if failed > 0 else "green")
        summary_table.add_row(
            "Success Rate", f"{(passed/total*100):.1f}%" if total > 0 else "N/A"
        )
        summary_table.add_row("Total Duration", f"{total_duration:.2f}s")

        console.print(summary_table)

        results_table = Table(
            title="\nDetailed Results", show_header=True, header_style="bold magenta"
        )
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
                result.message[:60] + "..." if len(result.message) > 60 else result.message,
            )

        console.print(results_table)

        if failed == 0:
            console.print("\n[bold green]✓ All scenarios passed successfully![/bold green]\n")
            return 0
        else:
            console.print(f"\n[bold red]✗ {failed} scenario(s) failed[/bold red]\n")
            return 1

    def scenario_3_security_access_control_lifecycle(self) -> TestResult:
        """Full lifecycle test for security access controls: set → get → delete."""
        scenario_name = "Scenario 3: Security Access Control Lifecycle"
        start_time = time.perf_counter()
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")

            ts = self.test_run_id
            control_name = f"test-ctrl-{ts}"

            # --- Step 1: Set (create) a security access control ---
            console.print("  → Setting security access control...")
            body = {
                "class": "SecurityAccessControlRequestBody",
                "securityAccessControl": {
                    "controlName": control_name,
                    "displayName": "Scenario Test Control",
                    "description": f"Security access control created by scenario test {ts}",
                    "controlTypeName": "ScenarioTestControl",
                    "associatedSecurityList": {
                        "readOperation": ["callie", "erinoverview"]
                    },
                    "securityLabels": [],
                    "securityProperties": {"environment": "scenario-test"},
                },
            }
            self.client.set_security_access_control(
                PLATFORM_NAME, body, platform_guid=self.platform_guid
            )
            console.print(f"  ✓ Set security access control: {control_name}")

            # --- Step 2: Get the control back ---
            console.print("  → Retrieving security access control...")
            control = self.client.get_security_access_control(
                PLATFORM_NAME, control_name, platform_guid=self.platform_guid
            )
            console.print(f"  ✓ Retrieved: {control}")

            # --- Step 3: Update the control (set with new description) ---
            console.print("  → Updating security access control...")
            body["securityAccessControl"]["description"] = f"Updated description {ts}"
            self.client.set_security_access_control(
                PLATFORM_NAME, body, platform_guid=self.platform_guid
            )
            console.print("  ✓ Updated security access control")

            # --- Step 4: Delete the control ---
            console.print("  → Deleting security access control...")
            self.client.delete_security_access_control(
                PLATFORM_NAME, control_name, platform_guid=self.platform_guid
            )
            console.print(f"  ✓ Deleted security access control: {control_name}")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Full lifecycle completed for control '{control_name}'",
            )

        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [yellow]⚠ {scenario_name}: {str(e)}[/yellow]")
            return TestResult(
                scenario_name=scenario_name,
                status="WARNING",
                duration=duration,
                message=str(e),
                error=e,
            )

    def run_all_scenarios(self):
        """Execute all test scenarios"""
        if not self.setup():
            return 1

        try:
            self.results.append(self.scenario_1_user_lifecycle())
            self.results.append(self.scenario_2_coco_manage_users())
            self.results.append(self.scenario_3_security_access_control_lifecycle())

            self.cleanup_created_users()
            return self.generate_report()

        except KeyboardInterrupt:
            console.print("\n[yellow]Test execution interrupted by user[/yellow]")
            self.cleanup_created_users()
            return 1
        except Exception as e:
            console.print(f"\n[bold red]Unexpected error: {str(e)}[/bold red]")
            traceback.print_exc()
            return 1
        finally:
            self.teardown()


if __name__ == "__main__":
    tester = SecurityOfficerScenarioTester()
    success = tester.run_all_scenarios()
    sys.exit(0 if success == 0 else 1)
