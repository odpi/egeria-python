"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Comprehensive scenario tests for GovernanceOfficer.
Tests full CRUD workflows for governance definitions with proper cleanup.

A running Egeria environment is needed to run these tests.
"""

import time
from dataclasses import dataclass
from datetime import datetime

from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from pyegeria.governance_officer import GovernanceOfficer
from pyegeria._exceptions import (
    PyegeriaException,
    PyegeriaAPIException,
    PyegeriaNotFoundException,
    print_basic_exception,
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


class GovernanceOfficerScenarioTester:
    """Test harness for GovernanceOfficer scenarios"""

    def __init__(self):
        self.view_server = "qs-view-server"
        self.platform_url = "https://127.0.0.1:9443"
        self.user = "peterprofile"
        self.password = "secret"
        self.client = None
        self.created_definitions = []

    def setup(self):
        """Initialize the client"""
        try:
            self.client = GovernanceOfficer(
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
            self.cleanup_created_entities()
            self.client.close_session()
            console.print("[green]✓[/green] Session closed")

    def cleanup_created_entities(self):
        """Delete all created test entities"""
        console.print("\n[bold cyan]Cleaning up created entities...[/bold cyan]")

        for def_guid in reversed(self.created_definitions):
            try:
                self.client.delete_governance_definition(def_guid, cascade=False)
                console.print(f"[green]✓[/green] Deleted governance definition: {def_guid}")
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Could not delete definition {def_guid}: {str(e)}")

        self.created_definitions.clear()

    def scenario_complete_governance_definition_lifecycle(self) -> TestResult:
        """
        Scenario: Complete governance definition lifecycle
        - Create a governance definition
        - Update the definition
        - Retrieve the definition
        - Delete the definition
        """
        scenario_name = "Complete Governance Definition Lifecycle"
        start_time = time.perf_counter()

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            display_name = f"Test_Gov_Def_{timestamp}"
            q_name = self.client.__create_qualified_name__("GovernanceDefinition", display_name)

            # Step 1: Create governance definition
            console.print(f"\n[cyan]Creating governance definition: {display_name}[/cyan]")
            body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "GovernanceDefinitionProperties",
                    "typeName": "GovernanceDefinition",
                    "domainIdentifier": 0,
                    "qualifiedName": q_name,
                    "displayName": display_name,
                    "summary": "Test governance definition",
                    "description": "A test governance definition for scenario testing",
                    "scope": "Test",
                    "importance": "High",
                    "implications": [],
                    "outcomes": [],
                    "results": []
                },
            }

            def_guid = self.client.create_governance_definition(body)
            self.created_definitions.append(def_guid)
            console.print(f"[green]✓[/green] Created governance definition with GUID: {def_guid}")

            # Step 2: Update governance definition
            console.print(f"\n[cyan]Updating governance definition: {def_guid}[/cyan]")
            update_body = {
                "class": "UpdateElementRequestBody",
                "properties": {
                    "class": "GovernanceDefinitionProperties",
                    "typeName": "GovernanceDefinition",
                    "qualifiedName": q_name,
                    "displayName": display_name,
                    "summary": "Updated test governance definition",
                    "description": "Updated description for testing",
                    "scope": "Test-Updated",
                    "importance": "Critical",
                },
            }
            self.client.update_governance_definition(def_guid, update_body)
            console.print(f"[green]✓[/green] Updated governance definition")

            # Step 3: Retrieve governance definition
            console.print(f"\n[cyan]Retrieving governance definition: {def_guid}[/cyan]")
            retrieved = self.client.get_governance_definition_by_guid(def_guid)
            if isinstance(retrieved, dict):
                console.print(f"[green]✓[/green] Retrieved governance definition")
            else:
                console.print(f"[green]✓[/green] Retrieved definition data")

            # Step 4: Delete governance definition
            console.print(f"\n[cyan]Deleting governance definition: {def_guid}[/cyan]")
            self.client.delete_governance_definition(def_guid, cascade=True)
            self.created_definitions.remove(def_guid)
            console.print(f"[green]✓[/green] Deleted governance definition")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=True,
                duration=duration,
                message=f"Successfully completed full lifecycle for {display_name}",
            )

        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=False,
                duration=duration,
                error=str(e),
            )

    def scenario_search_governance_definitions(self) -> TestResult:
        """
        Scenario: Search governance definitions
        - Create multiple governance definitions
        - Search by name
        - Find with search string
        - Retrieve specific definitions
        - Clean up
        """
        scenario_name = "Search Governance Definitions"
        start_time = time.perf_counter()

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = f"Search_Test_{timestamp}"

            # Step 1: Create multiple governance definitions
            def_names = [
                f"{base_name}_Policy",
                f"{base_name}_Standard",
                f"{base_name}_Control"
            ]
            created_guids = []

            for name in def_names:
                console.print(f"\n[cyan]Creating governance definition: {name}[/cyan]")
                q_name = self.client.__create_qualified_name__("GovernanceDefinition", name)

                body = {
                    "class": "NewElementRequestBody",
                    "properties": {
                        "class": "GovernanceDefinitionProperties",
                        "typeName": "GovernanceDefinition",
                        "domainIdentifier": 0,
                        "qualifiedName": q_name,
                        "displayName": name,
                        "summary": f"Test definition for {name}",
                        "description": f"Search testing definition",
                        "scope": "Test",
                        "importance": "Medium",
                    },
                }

                guid = self.client.create_governance_definition(body)
                created_guids.append(guid)
                self.created_definitions.append(guid)
                console.print(f"[green]✓[/green] Created: {guid}")

            # Step 2: Search by name
            console.print(f"\n[cyan]Searching for definitions with name: {base_name}[/cyan]")
            search_results = self.client.get_governance_definitions_by_name(filter_string=base_name)
            if isinstance(search_results, list):
                console.print(f"[green]✓[/green] Found {len(search_results)} definitions")
            else:
                console.print(f"[green]✓[/green] Search completed")

            # Step 3: Find with search string
            console.print(f"\n[cyan]Finding definitions with search string: {base_name}[/cyan]")
            find_results = self.client.find_governance_definitions(search_string=base_name)
            if isinstance(find_results, list):
                console.print(f"[green]✓[/green] Found {len(find_results)} definitions")
            else:
                console.print(f"[green]✓[/green] Find completed")

            # Step 4: Retrieve each definition by GUID
            for guid in created_guids:
                console.print(f"\n[cyan]Retrieving definition: {guid}[/cyan]")
                definition = self.client.get_governance_definition_by_guid(guid)
                if isinstance(definition, dict):
                    console.print(f"[green]✓[/green] Retrieved definition")
                else:
                    console.print(f"[green]✓[/green] Retrieved definition data")

            # Step 5: Clean up
            for guid in created_guids:
                console.print(f"\n[cyan]Deleting definition: {guid}[/cyan]")
                self.client.delete_governance_definition(guid, cascade=True)
                self.created_definitions.remove(guid)
                console.print(f"[green]✓[/green] Deleted")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=True,
                duration=duration,
                message=f"Successfully searched and retrieved {len(def_names)} definitions",
            )

        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=False,
                duration=duration,
                error=str(e),
            )

    def scenario_governance_definition_from_template(self) -> TestResult:
        """
        Scenario: Create governance definition from template
        - Create a template definition
        - Create new definition from template
        - Verify both exist
        - Clean up
        """
        scenario_name = "Governance Definition from Template"
        start_time = time.perf_counter()

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Step 1: Create template definition
            template_name = f"Template_Def_{timestamp}"
            console.print(f"\n[cyan]Creating template definition: {template_name}[/cyan]")
            template_q_name = self.client.__create_qualified_name__("GovernanceDefinition", template_name)

            template_body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "GovernanceDefinitionProperties",
                    "typeName": "GovernanceDefinition",
                    "domainIdentifier": 0,
                    "qualifiedName": template_q_name,
                    "displayName": template_name,
                    "summary": "Template for creating new definitions",
                    "description": "A template governance definition",
                    "scope": "Template",
                    "importance": "High",
                },
            }

            template_guid = self.client.create_governance_definition(template_body)
            self.created_definitions.append(template_guid)
            console.print(f"[green]✓[/green] Created template: {template_guid}")

            # Step 2: Create definition from template
            new_name = f"From_Template_{timestamp}"
            console.print(f"\n[cyan]Creating definition from template: {new_name}[/cyan]")
            new_q_name = self.client.__create_qualified_name__("GovernanceDefinition", new_name)

            from_template_body = {
                "class": "TemplateRequestBody",
                "templateGUID": template_guid,
                "replacementProperties": {
                    "class": "GovernanceDefinitionProperties",
                    "qualifiedName": new_q_name,
                    "displayName": new_name,
                    "summary": "Created from template",
                },
            }

            new_guid = self.client.create_governance_definition_from_template(from_template_body)
            self.created_definitions.append(new_guid)
            console.print(f"[green]✓[/green] Created from template: {new_guid}")

            # Step 3: Verify both exist
            console.print(f"\n[cyan]Verifying template definition[/cyan]")
            template_def = self.client.get_governance_definition_by_guid(template_guid)
            console.print(f"[green]✓[/green] Template definition exists")

            console.print(f"\n[cyan]Verifying new definition[/cyan]")
            new_def = self.client.get_governance_definition_by_guid(new_guid)
            console.print(f"[green]✓[/green] New definition exists")

            # Step 4: Clean up
            for guid in [template_guid, new_guid]:

                console.print(f"\n[cyan]Deleting definition: {guid}[/cyan]")
                self.client.delete_governance_definition(guid, cascade=False)
                self.created_definitions.remove(guid)
                console.print(f"[green]✓[/green] Deleted")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=True,
                duration=duration,
                message="Successfully created definition from template",
            )

        except PyegeriaException as e:
            duration = time.perf_counter() - start_time
            print_basic_exception(e)
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
            "[bold cyan]GovernanceOfficer Scenario Tests[/bold cyan]\n"
            "Testing comprehensive CRUD workflows for governance definitions",
            border_style="cyan"
        ))

        if not self.setup():
            return results

        try:
            # Run each scenario
            scenarios = [
                self.scenario_complete_governance_definition_lifecycle,
                self.scenario_search_governance_definitions,
                self.scenario_governance_definition_from_template,
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


def test_governance_officer_scenarios():
    """Pytest entry point"""
    tester = GovernanceOfficerScenarioTester()
    results = tester.run_all_scenarios()
    tester.print_results_summary(results)

    # Assert that all scenarios passed
    assert all(result.passed for result in results), "Some scenarios failed"


if __name__ == "__main__":
    tester = GovernanceOfficerScenarioTester()
    results = tester.run_all_scenarios()
    tester.print_results_summary(results)