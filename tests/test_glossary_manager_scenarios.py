"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Comprehensive scenario tests for GlossaryManager.
Tests full CRUD workflows for glossaries and terms with proper cleanup.

A running Egeria environment is needed to run these tests.
"""

import time
from dataclasses import dataclass
from datetime import datetime

from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from pyegeria import GlossaryManager
from pyegeria._exceptions import (
    PyegeriaException,
    PyegeriaAPIException,
    PyegeriaNotFoundException,
    print_basic_exception,
)
from pyegeria.glossary_manager import GlossaryTermProperties
from pyegeria.models import NewElementRequestBody

console = Console()


@dataclass
class TestResult:
    """Data class to hold test results"""
    scenario_name: str
    passed: bool
    duration: float
    message: str = ""
    error: str = ""


class GlossaryScenarioTester:
    """Test harness for GlossaryManager scenarios"""

    def __init__(self):
        self.view_server = "qs-view-server"
        self.platform_url = "https://laz.local:9443"
        self.user = "erinoverview"
        self.password = "secret"
        self.client = None
        self.created_glossaries = []
        self.created_terms = []

    def setup(self):
        """Initialize the client"""
        try:
            self.client = GlossaryManager(
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

        # Delete terms first (they depend on glossaries)
        for term_guid in reversed(self.created_terms):
            try:
                self.client.delete_term(term_guid)
                console.print(f"[green]✓[/green] Deleted term: {term_guid}")
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Could not delete term {term_guid}: {str(e)}")

        # Then delete glossaries
        for glossary_guid in reversed(self.created_glossaries):
            try:
                self.client.delete_glossary(glossary_guid, cascade=True)
                console.print(f"[green]✓[/green] Deleted glossary: {glossary_guid}")
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Could not delete glossary {glossary_guid}: {str(e)}")

        self.created_glossaries.clear()
        self.created_terms.clear()

    def scenario_complete_glossary_lifecycle(self) -> TestResult:
        """
        Scenario: Complete glossary lifecycle
        - Create a glossary
        - Update the glossary
        - Retrieve the glossary
        - Delete the glossary
        """
        scenario_name = "Complete Glossary Lifecycle"
        start_time = time.perf_counter()

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            display_name = f"Test_Glossary_{timestamp}"
            description = "A test glossary for scenario testing"
            language = "English"
            usage = "Testing purposes only"

            # Step 1: Create glossary
            console.print(f"\n[cyan]Creating glossary: {display_name}[/cyan]")
            glossary_guid = self.client.create_glossary(
                display_name, description, language, usage
            )
            self.created_glossaries.append(glossary_guid)
            console.print(f"[green]✓[/green] Created glossary with GUID: {glossary_guid}")

            # Step 2: Update glossary
            console.print(f"\n[cyan]Updating glossary: {glossary_guid}[/cyan]")
            updated_description = f"{description} - Updated"
            update_body = {
                "class": "UpdateElementRequestBody",
                "properties": {
                    "class": "GlossaryProperties",
                    "displayName": display_name,
                    "description": updated_description,
                    "qualifiedName": f"Glossary:{display_name}",
                },
            }
            self.client.update_glossary(glossary_guid, update_body)
            console.print(f"[green]✓[/green] Updated glossary description")

            # Step 3: Retrieve glossary
            console.print(f"\n[cyan]Retrieving glossary: {glossary_guid}[/cyan]")
            retrieved = self.client.get_glossary_by_guid(glossary_guid)
            if isinstance(retrieved, dict):
                console.print(f"[green]✓[/green] Retrieved glossary successfully")
            elif isinstance(retrieved, str):
                console.print(f"[green]✓[/green] Retrieved glossary (string format)")
            else:
                console.print(f"[green]✓[/green] Retrieved glossary")

            # Step 4: Delete glossary
            console.print(f"\n[cyan]Deleting glossary: {glossary_guid}[/cyan]")
            self.client.delete_glossary(glossary_guid, cascade=True)
            self.created_glossaries.remove(glossary_guid)
            console.print(f"[green]✓[/green] Deleted glossary")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=True,
                duration=duration,
                message=f"Successfully completed full glossary lifecycle for {display_name}",
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
        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"[red]Unexpected error:[/red] {str(e)}")
            return TestResult(
                scenario_name=scenario_name,
                passed=False,
                duration=duration,
                error=str(e),
            )

    def scenario_glossary_term_management(self) -> TestResult:
        """
        Scenario: Glossary term management
        - Create a glossary
        - Create multiple terms in the glossary
        - Update a term
        - Retrieve terms
        - Delete terms
        - Delete glossary
        """
        scenario_name = "Glossary Term Management"
        start_time = time.perf_counter()

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            glossary_name = f"Terms_Glossary_{timestamp}"

            # Step 1: Create glossary
            console.print(f"\n[cyan]Creating glossary: {glossary_name}[/cyan]")
            glossary_guid = self.client.create_glossary(
                glossary_name,
                "Glossary for term management testing",
                "English",
                "Testing term operations"
            )
            self.created_glossaries.append(glossary_guid)
            console.print(f"[green]✓[/green] Created glossary: {glossary_guid}")

            # Step 2: Create multiple terms
            term_names = ["Customer", "Product", "Order"]
            created_term_guids = []

            for term_name in term_names:
                console.print(f"\n[cyan]Creating term: {term_name}[/cyan]")
                qualified_name = f"GlossaryTerm:{glossary_name}:{term_name}_{timestamp}"

                prop_body = GlossaryTermProperties(
                    class_="GlossaryTermProperties",
                    display_name=term_name,
                    description=f"Test term for {term_name}",
                    qualified_name=qualified_name,
                    summary=f"A {term_name} entity",
                    abbreviation=term_name[:3].upper(),
                    examples=f"Example {term_name}",
                    usage=f"Used to represent {term_name} information",
                )

                body = NewElementRequestBody(
                    class_="NewElementRequestBody",
                    parent_guid=glossary_guid,
                    is_own_anchor=True,
                    anchor_scope_guid=glossary_guid,
                    parent_relationship_type_name="CollectionMembership",
                    parent_at_end_1=True,
                    properties=prop_body.model_dump(exclude_none=True),
                )

                term_guid = self.client.create_glossary_term(body)
                created_term_guids.append(term_guid)
                self.created_terms.append(term_guid)
                console.print(f"[green]✓[/green] Created term: {term_name} ({term_guid})")

            # Step 3: Update a term
            if created_term_guids:
                term_to_update = created_term_guids[0]
                console.print(f"\n[cyan]Updating term: {term_to_update}[/cyan]")

                update_body = {
                    "class": "UpdateElementRequestBody",
                    "properties": {
                        "class": "GlossaryTermProperties",
                        "displayName": term_names[0],
                        "description": f"Updated description for {term_names[0]}",
                        "qualifiedName": f"GlossaryTerm:{glossary_name}:{term_names[0]}_{timestamp}",
                    },
                }
                self.client.update_glossary_term(term_to_update, update_body)
                console.print(f"[green]✓[/green] Updated term")

            # Step 4: Retrieve terms
            console.print(f"\n[cyan]Retrieving terms by name[/cyan]")
            terms = self.client.get_terms_by_name(filter_string=glossary_name)
            if isinstance(terms, list):
                console.print(f"[green]✓[/green] Retrieved {len(terms)} terms")
            else:
                console.print(f"[green]✓[/green] Retrieved terms")

            # Step 5: Delete terms
            for term_guid in created_term_guids:
                console.print(f"\n[cyan]Deleting term: {term_guid}[/cyan]")
                self.client.delete_term(term_guid)
                self.created_terms.remove(term_guid)
                console.print(f"[green]✓[/green] Deleted term")

            # Step 6: Delete glossary
            console.print(f"\n[cyan]Deleting glossary: {glossary_guid}[/cyan]")
            self.client.delete_glossary(glossary_guid, cascade=True)
            self.created_glossaries.remove(glossary_guid)
            console.print(f"[green]✓[/green] Deleted glossary")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=True,
                duration=duration,
                message=f"Successfully managed {len(term_names)} terms in glossary",
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
        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"[red]Unexpected error:[/red] {str(e)}")
            return TestResult(
                scenario_name=scenario_name,
                passed=False,
                duration=duration,
                error=str(e),
            )

    def scenario_glossary_search_and_retrieval(self) -> TestResult:
        """
        Scenario: Glossary search and retrieval
        - Create multiple glossaries
        - Search for glossaries by name
        - Find glossaries with search string
        - Retrieve specific glossaries
        - Clean up
        """
        scenario_name = "Glossary Search and Retrieval"
        start_time = time.perf_counter()

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = f"Search_Test_{timestamp}"

            # Step 1: Create multiple glossaries
            glossary_names = [
                f"{base_name}_Finance",
                f"{base_name}_HR",
                f"{base_name}_IT"
            ]
            created_guids = []

            for name in glossary_names:
                console.print(f"\n[cyan]Creating glossary: {name}[/cyan]")
                guid = self.client.create_glossary(
                    name,
                    f"Test glossary for {name}",
                    "English",
                    "Search testing"
                )
                created_guids.append(guid)
                self.created_glossaries.append(guid)
                console.print(f"[green]✓[/green] Created: {guid}")

            # Step 2: Search by name
            console.print(f"\n[cyan]Searching for glossaries with name: {base_name}[/cyan]")
            search_results = self.client.get_glossaries_by_name(filter_string=base_name)
            if isinstance(search_results, list):
                console.print(f"[green]✓[/green] Found {len(search_results)} glossaries")
            else:
                console.print(f"[green]✓[/green] Search completed")

            # Step 3: Find with search string
            console.print(f"\n[cyan]Finding glossaries with search string: {base_name}[/cyan]")
            find_results = self.client.find_glossaries(search_string=base_name)
            if isinstance(find_results, list):
                console.print(f"[green]✓[/green] Found {len(find_results)} glossaries")
            else:
                console.print(f"[green]✓[/green] Find completed")

            # Step 4: Retrieve each glossary by GUID
            for guid in created_guids:
                console.print(f"\n[cyan]Retrieving glossary: {guid}[/cyan]")
                glossary = self.client.get_glossary_by_guid(guid)
                if isinstance(glossary, dict):
                    console.print(f"[green]✓[/green] Retrieved glossary")
                else:
                    console.print(f"[green]✓[/green] Retrieved glossary data")

            # Step 5: Clean up
            for guid in created_guids:
                console.print(f"\n[cyan]Deleting glossary: {guid}[/cyan]")
                self.client.delete_glossary(guid, cascade=True)
                self.created_glossaries.remove(guid)
                console.print(f"[green]✓[/green] Deleted")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=True,
                duration=duration,
                message=f"Successfully searched and retrieved {len(glossary_names)} glossaries",
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
        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"[red]Unexpected error:[/red] {str(e)}")
            return TestResult(
                scenario_name=scenario_name,
                passed=False,
                duration=duration,
                error=str(e),
            )

    def scenario_term_copy_and_relationships(self) -> TestResult:
        """
        Scenario: Term copy and relationships
        - Create a glossary
        - Create a term
        - Copy the term to another glossary
        - Verify both terms exist
        - Clean up
        """
        scenario_name = "Term Copy and Relationships"
        start_time = time.perf_counter()

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Step 1: Create source glossary
            source_name = f"Source_Glossary_{timestamp}"
            console.print(f"\n[cyan]Creating source glossary: {source_name}[/cyan]")
            source_guid = self.client.create_glossary(
                source_name,
                "Source glossary for term copy",
                "English",
                "Testing term copy"
            )
            self.created_glossaries.append(source_guid)
            console.print(f"[green]✓[/green] Created source glossary: {source_guid}")

            # Step 2: Create target glossary
            target_name = f"Target_Glossary_{timestamp}"
            console.print(f"\n[cyan]Creating target glossary: {target_name}[/cyan]")
            target_guid = self.client.create_glossary(
                target_name,
                "Target glossary for term copy",
                "English",
                "Testing term copy"
            )
            self.created_glossaries.append(target_guid)
            console.print(f"[green]✓[/green] Created target glossary: {target_guid}")

            # Step 3: Create a term in source glossary
            term_name = "OriginalTerm"
            qualified_name = f"GlossaryTerm:{source_name}:{term_name}_{timestamp}"
            console.print(f"\n[cyan]Creating term: {term_name}[/cyan]")

            prop_body = GlossaryTermProperties(
                class_="GlossaryTermProperties",
                display_name=term_name,
                description="Original term for copying",
                qualified_name=qualified_name,
                summary="A term to be copied",
                abbreviation="OT",
            )

            body = NewElementRequestBody(
                class_="NewElementRequestBody",
                parent_guid=source_guid,
                is_own_anchor=True,
                anchor_scope_guid=source_guid,
                parent_relationship_type_name="CollectionMembership",
                parent_at_end_1=True,
                properties=prop_body.model_dump(exclude_none=True),
            )

            term_guid = self.client.create_glossary_term(body)
            self.created_terms.append(term_guid)
            console.print(f"[green]✓[/green] Created term: {term_guid}")

            # Step 4: Copy term to target glossary
            copied_name = f"CopiedTerm_{timestamp}"
            console.print(f"\n[cyan]Copying term to target glossary as: {copied_name}[/cyan]")
            copied_guid = self.client.create_term_copy(target_guid, term_guid, copied_name)
            self.created_terms.append(copied_guid)
            console.print(f"[green]✓[/green] Copied term: {copied_guid}")

            # Step 5: Verify both terms exist
            console.print(f"\n[cyan]Verifying original term[/cyan]")
            original = self.client.get_term_by_guid(term_guid)
            console.print(f"[green]✓[/green] Original term exists")

            console.print(f"\n[cyan]Verifying copied term[/cyan]")
            copied = self.client.get_term_by_guid(copied_guid)
            console.print(f"[green]✓[/green] Copied term exists")

            # Step 6: Clean up
            for guid in [term_guid, copied_guid]:
                console.print(f"\n[cyan]Deleting term: {guid}[/cyan]")
                self.client.delete_term(guid)
                self.created_terms.remove(guid)
                console.print(f"[green]✓[/green] Deleted term")

            for guid in [source_guid, target_guid]:
                console.print(f"\n[cyan]Deleting glossary: {guid}[/cyan]")
                self.client.delete_glossary(guid, cascade=True)
                self.created_glossaries.remove(guid)
                console.print(f"[green]✓[/green] Deleted glossary")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=True,
                duration=duration,
                message="Successfully copied term between glossaries",
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
        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"[red]Unexpected error:[/red] {str(e)}")
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
            "[bold cyan]GlossaryManager Scenario Tests[/bold cyan]\n"
            "Testing comprehensive CRUD workflows",
            border_style="cyan"
        ))

        if not self.setup():
            return results

        try:
            # Run each scenario
            scenarios = [
                self.scenario_complete_glossary_lifecycle,
                self.scenario_glossary_term_management,
                self.scenario_glossary_search_and_retrieval,
                self.scenario_term_copy_and_relationships,
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


def test_glossary_manager_scenarios():
    """Pytest entry point"""
    tester = GlossaryScenarioTester()
    results = tester.run_all_scenarios()
    tester.print_results_summary(results)

    # Assert that all scenarios passed
    assert all(result.passed for result in results), "Some scenarios failed"


if __name__ == "__main__":
    tester = GlossaryScenarioTester()
    results = tester.run_all_scenarios()
    tester.print_results_summary(results)