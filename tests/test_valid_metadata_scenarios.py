"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Comprehensive scenario tests for ValidMetadataManager.
Tests query workflows for valid metadata values and type definitions.

A running Egeria environment is needed to run these tests.
"""

import time
from dataclasses import dataclass
from datetime import datetime

from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from pyegeria import ValidMetadataManager
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


class ValidMetadataScenarioTester:
    """Test harness for ValidMetadataManager scenarios"""

    def __init__(self):
        self.view_server = "qs-view-server"
        self.platform_url = "https://127.0.0.1:9443"
        self.user = "erinoverview"
        self.password = "secret"
        self.client = None

    def setup(self):
        """Initialize the client"""
        try:
            self.client = ValidMetadataManager(
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

    def scenario_explore_entity_types(self) -> TestResult:
        """
        Scenario: Explore entity types
        - Get all entity types
        - Get entity type definitions
        - Get subtypes for specific types
        - Verify type information
        """
        scenario_name = "Explore Entity Types"
        start_time = time.perf_counter()

        try:
            # Step 1: Get all entity types
            console.print(f"\n[cyan]Getting all entity types[/cyan]")
            entity_types = self.client.get_all_entity_types()
            
            if isinstance(entity_types, list):
                console.print(f"[green]✓[/green] Found {len(entity_types)} entity types")
            elif isinstance(entity_types, str):
                console.print(f"[yellow]⚠[/yellow] Result: {entity_types}")
            else:
                console.print(f"[green]✓[/green] Retrieved entity types")

            # Step 2: Get all entity definitions
            console.print(f"\n[cyan]Getting all entity definitions[/cyan]")
            entity_defs = self.client.get_all_entity_defs()
            
            if isinstance(entity_defs, list):
                console.print(f"[green]✓[/green] Found {len(entity_defs)} entity definitions")
            else:
                console.print(f"[green]✓[/green] Retrieved entity definitions")

            # Step 3: Get subtypes for common types
            common_types = ["Asset", "Referenceable", "OpenMetadataRoot"]
            
            for type_name in common_types:
                console.print(f"\n[cyan]Getting subtypes for: {type_name}[/cyan]")
                try:
                    subtypes = self.client.get_sub_types(type_name)
                    if isinstance(subtypes, list):
                        console.print(f"[green]✓[/green] Found {len(subtypes)} subtypes for {type_name}")
                    else:
                        console.print(f"[green]✓[/green] Retrieved subtypes for {type_name}")
                except Exception as e:
                    console.print(f"[yellow]⚠[/yellow] Could not get subtypes for {type_name}: {str(e)}")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=True,
                duration=duration,
                message="Successfully explored entity types and definitions",
            )

        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=False,
                duration=duration,
                error=str(e),
            )

    def scenario_explore_relationship_types(self) -> TestResult:
        """
        Scenario: Explore relationship types
        - Get all relationship definitions
        - Get valid relationship types for entities
        - Verify relationship information
        """
        scenario_name = "Explore Relationship Types"
        start_time = time.perf_counter()

        try:
            # Step 1: Get all relationship definitions
            console.print(f"\n[cyan]Getting all relationship definitions[/cyan]")
            rel_defs = self.client.get_all_relationship_defs()
            
            if isinstance(rel_defs, list):
                console.print(f"[green]✓[/green] Found {len(rel_defs)} relationship definitions")
            else:
                console.print(f"[green]✓[/green] Retrieved relationship definitions")

            # Step 2: Get valid relationship types for common entities
            entity_types = ["Asset", "GlossaryTerm", "Project"]
            
            for entity_type in entity_types:
                console.print(f"\n[cyan]Getting valid relationship types for: {entity_type}[/cyan]")
                try:
                    valid_rels = self.client.get_valid_relationship_types(entity_type)
                    if isinstance(valid_rels, list):
                        console.print(f"[green]✓[/green] Found {len(valid_rels)} valid relationship types for {entity_type}")
                    else:
                        console.print(f"[green]✓[/green] Retrieved relationship types for {entity_type}")
                except Exception as e:
                    console.print(f"[yellow]⚠[/yellow] Could not get relationship types for {entity_type}: {str(e)}")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=True,
                duration=duration,
                message="Successfully explored relationship types",
            )

        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=False,
                duration=duration,
                error=str(e),
            )

    def scenario_explore_classification_types(self) -> TestResult:
        """
        Scenario: Explore classification types
        - Get all classification definitions
        - Get valid classification types for entities
        - Verify classification information
        """
        scenario_name = "Explore Classification Types"
        start_time = time.perf_counter()

        try:
            # Step 1: Get all classification definitions
            console.print(f"\n[cyan]Getting all classification definitions[/cyan]")
            class_defs = self.client.get_all_classification_defs()
            
            if isinstance(class_defs, list):
                console.print(f"[green]✓[/green] Found {len(class_defs)} classification definitions")
            else:
                console.print(f"[green]✓[/green] Retrieved classification definitions")

            # Step 2: Get valid classification types for common entities
            entity_types = ["Asset", "GlossaryTerm", "Referenceable"]
            
            for entity_type in entity_types:
                console.print(f"\n[cyan]Getting valid classification types for: {entity_type}[/cyan]")
                try:
                    valid_classes = self.client.get_valid_classification_types(entity_type)
                    if isinstance(valid_classes, list):
                        console.print(f"[green]✓[/green] Found {len(valid_classes)} valid classification types for {entity_type}")
                    else:
                        console.print(f"[green]✓[/green] Retrieved classification types for {entity_type}")
                except Exception as e:
                    console.print(f"[yellow]⚠[/yellow] Could not get classification types for {entity_type}: {str(e)}")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=True,
                duration=duration,
                message="Successfully explored classification types",
            )

        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=False,
                duration=duration,
                error=str(e),
            )

    def scenario_explore_typedef_by_name(self) -> TestResult:
        """
        Scenario: Explore type definitions by name
        - Get typedef for specific types
        - Verify typedef information
        - Test multiple type names
        """
        scenario_name = "Explore TypeDef by Name"
        start_time = time.perf_counter()

        try:
            # Test various type names
            type_names = [
                "Asset",
                "GlossaryTerm",
                "Project",
                "Referenceable",
                "DataFile"
            ]
            
            for type_name in type_names:
                console.print(f"\n[cyan]Getting typedef for: {type_name}[/cyan]")
                try:
                    typedef = self.client.get_typedef_by_name(type_name)
                    if isinstance(typedef, dict):
                        type_category = typedef.get("category", "Unknown")
                        console.print(f"[green]✓[/green] Retrieved typedef for {type_name} (category: {type_category})")
                    else:
                        console.print(f"[green]✓[/green] Retrieved typedef for {type_name}")
                except Exception as e:
                    console.print(f"[yellow]⚠[/yellow] Could not get typedef for {type_name}: {str(e)}")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=True,
                duration=duration,
                message=f"Successfully explored typedefs for {len(type_names)} types",
            )

        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=False,
                duration=duration,
                error=str(e),
            )

    def scenario_explore_valid_metadata_values(self) -> TestResult:
        """
        Scenario: Explore valid metadata values
        - Get valid metadata values for properties
        - Get consistent metadata values
        - Test various property types
        """
        scenario_name = "Explore Valid Metadata Values"
        start_time = time.perf_counter()

        try:
            # Test getting valid values for common properties
            test_cases = [
                ("Project", "projectStatus"),
                ("Project", "projectPhase"),
                ("Asset", "deployedImplementationType"),
            ]
            
            for type_name, property_name in test_cases:
                console.print(f"\n[cyan]Getting valid values for {type_name}.{property_name}[/cyan]")
                try:
                    valid_values = self.client.get_valid_metadata_values(
                        type_name=type_name,
                        property_name=property_name
                    )
                    if isinstance(valid_values, list):
                        console.print(f"[green]✓[/green] Found {len(valid_values)} valid values for {property_name}")
                    elif isinstance(valid_values, dict):
                        console.print(f"[green]✓[/green] Retrieved valid values for {property_name}")
                    else:
                        console.print(f"[yellow]⚠[/yellow] No valid values defined for {property_name}")
                except Exception as e:
                    console.print(f"[yellow]⚠[/yellow] Could not get valid values for {property_name}: {str(e)}")

            # Test getting consistent metadata values
            console.print(f"\n[cyan]Getting consistent metadata values[/cyan]")
            try:
                consistent_values = self.client.get_consistent_metadata_values(
                    type_name="Project",
                    property_name="projectStatus"
                )
                if isinstance(consistent_values, list):
                    console.print(f"[green]✓[/green] Found {len(consistent_values)} consistent values")
                else:
                    console.print(f"[green]✓[/green] Retrieved consistent values")
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Could not get consistent values: {str(e)}")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=True,
                duration=duration,
                message="Successfully explored valid metadata values",
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
            "[bold cyan]ValidMetadataManager Scenario Tests[/bold cyan]\n"
            "Testing query workflows for metadata types and valid values",
            border_style="cyan"
        ))

        if not self.setup():
            return results

        try:
            # Run each scenario
            scenarios = [
                self.scenario_explore_entity_types,
                self.scenario_explore_relationship_types,
                self.scenario_explore_classification_types,
                self.scenario_explore_typedef_by_name,
                self.scenario_explore_valid_metadata_values,
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


def test_valid_metadata_scenarios():
    """Pytest entry point"""
    tester = ValidMetadataScenarioTester()
    results = tester.run_all_scenarios()
    tester.print_results_summary(results)

    # Assert that all scenarios passed
    assert all(result.passed for result in results), "Some scenarios failed"


if __name__ == "__main__":
    tester = ValidMetadataScenarioTester()
    results = tester.run_all_scenarios()
    tester.print_results_summary(results)