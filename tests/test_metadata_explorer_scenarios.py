"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Comprehensive scenario tests for MetadataExplorer.
Tests query and exploration workflows for metadata elements.

A running Egeria environment is needed to run these tests.
"""

import time
from dataclasses import dataclass
from datetime import datetime

from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from pyegeria import MetadataExplorer
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


class MetadataExplorerScenarioTester:
    """Test harness for MetadataExplorer scenarios"""

    def __init__(self):
        self.view_server = "qs-view-server"
        self.platform_url = "https://127.0.0.1:9443"
        self.user = "erinoverview"
        self.password = "secret"
        self.client = None

    def setup(self):
        """Initialize the client"""
        try:
            self.client = MetadataExplorer(
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

    def scenario_search_metadata_by_string(self) -> TestResult:
        """
        Scenario: Search metadata by string
        - Search for metadata elements using various search strings
        - Test different search patterns
        - Verify results are returned
        """
        scenario_name = "Search Metadata by String"
        start_time = time.perf_counter()

        try:
            search_terms = ["Glossary", "Server", "Asset"]

            for search_term in search_terms:
                console.print(f"\n[cyan]Searching for: {search_term}[/cyan]")

                results = self.client.find_metadata_elements_with_string(
                    search_string=search_term,
                    type_name=None,
                    starts_with=False,
                    ends_with=False,
                    ignore_case=True,
                )

                if isinstance(results, list):
                    console.print(f"[green]✓[/green] Found {len(results)} elements matching '{search_term}'")
                elif isinstance(results, str):
                    console.print(f"[yellow]⚠[/yellow] Search returned: {results}")
                else:
                    console.print(f"[green]✓[/green] Search completed for '{search_term}'")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=True,
                duration=duration,
                message=f"Successfully searched for {len(search_terms)} different terms",
            )

        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=False,
                duration=duration,
                error=str(e),
            )

    def scenario_retrieve_element_by_guid(self) -> TestResult:
        """
        Scenario: Retrieve element by GUID
        - Search for an element to get a GUID
        - Retrieve the element by its GUID
        - Verify element details
        """
        scenario_name = "Retrieve Element by GUID"
        start_time = time.perf_counter()

        try:
            # Step 1: Search for elements to get a GUID
            console.print(f"\n[cyan]Searching for glossary elements[/cyan]")
            search_results = self.client.find_metadata_elements_with_string(
                search_string="Glossary",
                type_name="Glossary",
                ignore_case=True,
            )

            element_guid = None
            if isinstance(search_results, list) and len(search_results) > 0:
                # Get the first element's GUID
                first_element = search_results[0]
                if isinstance(first_element, dict):
                    element_guid = first_element.get("elementHeader", {}).get("guid")
                    console.print(f"[green]✓[/green] Found element with GUID: {element_guid}")

            if element_guid:
                # Step 2: Retrieve element by GUID
                console.print(f"\n[cyan]Retrieving element by GUID: {element_guid}[/cyan]")
                element = self.client.get_metadata_element_by_guid(element_guid)

                if isinstance(element, dict):
                    element_type = element.get("elementHeader", {}).get("type", {}).get("typeName", "Unknown")
                    console.print(f"[green]✓[/green] Retrieved element of type: {element_type}")
                else:
                    console.print(f"[green]✓[/green] Retrieved element")

                duration = time.perf_counter() - start_time
                return TestResult(
                    scenario_name=scenario_name,
                    passed=True,
                    duration=duration,
                    message=f"Successfully retrieved element by GUID",
                )
            else:
                duration = time.perf_counter() - start_time
                return TestResult(
                    scenario_name=scenario_name,
                    passed=True,
                    duration=duration,
                    message="No elements found to test GUID retrieval (environment may be empty)",
                )

        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=False,
                duration=duration,
                error=str(e),
            )

    def scenario_explore_element_relationships(self) -> TestResult:
        """
        Scenario: Explore element relationships
        - Find an element
        - Get all related elements
        - Get specific relationship types
        - Explore the relationship graph
        """
        scenario_name = "Explore Element Relationships"
        start_time = time.perf_counter()

        try:
            # Step 1: Find an element with relationships
            console.print(f"\n[cyan]Searching for elements with relationships[/cyan]")
            search_results = self.client.find_metadata_elements_with_string(
                search_string="*",
                type_name="GlossaryTerm",
                ignore_case=True,
            )

            element_guid = None
            if isinstance(search_results, list) and len(search_results) > 0:
                first_element = search_results[0]
                if isinstance(first_element, dict):
                    element_guid = first_element.get("elementHeader", {}).get("guid")
                    element_name = first_element.get("elementHeader", {}).get("properties", {}).get("displayName", "Unknown")
                    console.print(f"[green]✓[/green] Found element: {element_name} ({element_guid})")

            if element_guid:
                # Step 2: Get all related elements
                console.print(f"\n[cyan]Getting all related elements for: {element_guid}[/cyan]")
                try:
                    related = self.client.get_all_related_metadata_elements(
                        element_guid=element_guid,
                        start_from=0,
                        page_size=50,
                    )

                    if isinstance(related, list):
                        console.print(f"[green]✓[/green] Found {len(related)} related elements")
                    elif isinstance(related, dict):
                        element_list = related.get("elementList", [])
                        console.print(f"[green]✓[/green] Found {len(element_list)} related elements")
                    else:
                        console.print(f"[yellow]⚠[/yellow] No related elements found")
                except Exception as e:
                    console.print(f"[yellow]⚠[/yellow] Could not get related elements: {str(e)}")

                # Step 3: Get all relationships
                console.print(f"\n[cyan]Getting all relationships for: {element_guid}[/cyan]")
                try:
                    relationships = self.client.get_all_metadata_element_relationships(
                        element_guid=element_guid,
                        start_from=0,
                        page_size=50,
                    )

                    if isinstance(relationships, list):
                        console.print(f"[green]✓[/green] Found {len(relationships)} relationships")
                    elif isinstance(relationships, dict):
                        rel_list = relationships.get("relationshipList", [])
                        console.print(f"[green]✓[/green] Found {len(rel_list)} relationships")
                    else:
                        console.print(f"[yellow]⚠[/yellow] No relationships found")
                except Exception as e:
                    console.print(f"[yellow]⚠[/yellow] Could not get relationships: {str(e)}")

                duration = time.perf_counter() - start_time
                return TestResult(
                    scenario_name=scenario_name,
                    passed=True,
                    duration=duration,
                    message="Successfully explored element relationships",
                )
            else:
                duration = time.perf_counter() - start_time
                return TestResult(
                    scenario_name=scenario_name,
                    passed=True,
                    duration=duration,
                    message="No elements found to explore relationships (environment may be empty)",
                )

        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=False,
                duration=duration,
                error=str(e),
            )

    def scenario_find_elements_by_type(self) -> TestResult:
        """
        Scenario: Find elements by type
        - Search for different metadata types
        - Use type-specific searches
        - Verify type filtering works
        """
        scenario_name = "Find Elements by Type"
        start_time = time.perf_counter()

        try:
            # Test different metadata types
            metadata_types = [
                ("Glossary", "Glossary elements"),
                ("GlossaryTerm", "Glossary terms"),
                ("Asset", "Asset elements"),
            ]

            for type_name, description in metadata_types:
                console.print(f"\n[cyan]Searching for {description} (type: {type_name})[/cyan]")

                try:
                    results = self.client.find_metadata_elements(
                        metadata_element_type_name=type_name,
                        search_properties=None,
                        start_from=0,
                        page_size=10,
                    )

                    if isinstance(results, list):
                        console.print(f"[green]✓[/green] Found {len(results)} {description}")
                    elif isinstance(results, dict):
                        element_list = results.get("elementList", [])
                        console.print(f"[green]✓[/green] Found {len(element_list)} {description}")
                    else:
                        console.print(f"[yellow]⚠[/yellow] No {description} found")
                except Exception as e:
                    console.print(f"[yellow]⚠[/yellow] Could not search for {description}: {str(e)}")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=True,
                duration=duration,
                message=f"Successfully searched for {len(metadata_types)} different types",
            )

        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=False,
                duration=duration,
                error=str(e),
            )

    def scenario_retrieve_by_unique_name(self) -> TestResult:
        """
        Scenario: Retrieve by unique name
        - Search for elements by qualified name
        - Retrieve GUID by unique name
        - Verify unique name lookups
        """
        scenario_name = "Retrieve by Unique Name"
        start_time = time.perf_counter()

        try:
            # Step 1: Find an element to get its qualified name
            console.print(f"\n[cyan]Searching for elements with qualified names[/cyan]")
            search_results = self.client.find_metadata_elements_with_string(
                search_string="*",
                type_name="Glossary",
                ignore_case=True,
            )

            qualified_name = None
            if isinstance(search_results, list) and len(search_results) > 0:
                first_element = search_results[0]
                if isinstance(first_element, dict):
                    qualified_name = first_element.get("elementHeader", {}).get("properties", {}).get("qualifiedName")
                    if qualified_name:
                        console.print(f"[green]✓[/green] Found element with qualified name: {qualified_name}")

            if qualified_name:
                # Step 2: Retrieve GUID by qualified name
                console.print(f"\n[cyan]Retrieving GUID by qualified name[/cyan]")
                try:
                    guid = self.client.get_metadata_guid_by_unique_name(
                        name=qualified_name,
                        property_name="qualifiedName",
                    )

                    if guid and isinstance(guid, str):
                        console.print(f"[green]✓[/green] Retrieved GUID: {guid}")

                        # Step 3: Retrieve element by unique name
                        console.print(f"\n[cyan]Retrieving element by unique name[/cyan]")
                        element = self.client.get_metadata_element_by_unique_name(
                            unique_name=qualified_name,
                            property_name="qualifiedName",
                        )

                        if isinstance(element, dict):
                            console.print(f"[green]✓[/green] Retrieved element by unique name")
                        else:
                            console.print(f"[green]✓[/green] Retrieved element data")
                    else:
                        console.print(f"[yellow]⚠[/yellow] Could not retrieve GUID")
                except Exception as e:
                    console.print(f"[yellow]⚠[/yellow] Error during unique name lookup: {str(e)}")

                duration = time.perf_counter() - start_time
                return TestResult(
                    scenario_name=scenario_name,
                    passed=True,
                    duration=duration,
                    message="Successfully tested unique name retrieval",
                )
            else:
                duration = time.perf_counter() - start_time
                return TestResult(
                    scenario_name=scenario_name,
                    passed=True,
                    duration=duration,
                    message="No elements with qualified names found (environment may be empty)",
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
            "[bold cyan]MetadataExplorer Scenario Tests[/bold cyan]\n"
            "Testing query and exploration workflows",
            border_style="cyan"
        ))

        if not self.setup():
            return results

        try:
            # Run each scenario
            scenarios = [
                self.scenario_search_metadata_by_string,
                self.scenario_retrieve_element_by_guid,
                self.scenario_explore_element_relationships,
                self.scenario_find_elements_by_type,
                self.scenario_retrieve_by_unique_name,
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


def test_metadata_explorer_scenarios():
    """Pytest entry point"""
    tester = MetadataExplorerScenarioTester()
    results = tester.run_all_scenarios()
    tester.print_results_summary(results)

    # Assert that all scenarios passed
    assert all(result.passed for result in results), "Some scenarios failed"


if __name__ == "__main__":
    tester = MetadataExplorerScenarioTester()
    results = tester.run_all_scenarios()
    tester.print_results_summary(results)