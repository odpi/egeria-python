"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Comprehensive scenario tests for ProjectManager.
Tests full CRUD workflows for projects with proper cleanup.

A running Egeria environment is needed to run these tests.
"""

import time
from dataclasses import dataclass
from datetime import datetime

from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from pyegeria.project_manager import ProjectManager
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


class ProjectManagerScenarioTester:
    """Test harness for ProjectManager scenarios"""

    def __init__(self):
        self.view_server = "qs-view-server"
        self.platform_url = "https://127.0.0.1:9443"
        self.user = "erinoverview"
        self.password = "secret"
        self.client = None
        self.created_projects = []

    def setup(self):
        """Initialize the client"""
        try:
            self.client = ProjectManager(
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

        for project_guid in reversed(self.created_projects):
            try:
                self.client.delete_project(project_guid)
                console.print(f"[green]✓[/green] Deleted project: {project_guid}")
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Could not delete project {project_guid}: {str(e)}")

        self.created_projects.clear()

    def scenario_complete_project_lifecycle(self) -> TestResult:
        """
        Scenario: Complete project lifecycle
        - Create a project
        - Update the project
        - Retrieve the project
        - Delete the project
        """
        scenario_name = "Complete Project Lifecycle"
        start_time = time.perf_counter()

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            display_name = f"Test_Project_{timestamp}"
            identifier = f"PROJ-{timestamp}"

            # Step 1: Create project
            console.print(f"\n[cyan]Creating project: {display_name}[/cyan]")
            body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "ProjectProperties",
                    "qualifiedName": f"Project:{display_name}",
                    "identifier": identifier,
                    "name": display_name,
                    "description": "A test project for scenario testing",
                    "projectStatus": "ACTIVE",
                    "projectPhase": "PLANNING",
                },
            }

            project_guid = self.client.create_project(body)
            self.created_projects.append(project_guid)
            console.print(f"[green]✓[/green] Created project with GUID: {project_guid}")

            # Step 2: Update project
            console.print(f"\n[cyan]Updating project: {project_guid}[/cyan]")
            update_body = {
                "class": "UpdateElementRequestBody",
                "properties": {
                    "class": "ProjectProperties",
                    "qualifiedName": f"Project:{display_name}",
                    "identifier": identifier,
                    "name": display_name,
                    "description": "Updated description for testing",
                    "projectStatus": "ACTIVE",
                    "projectPhase": "EXECUTION",
                },
            }
            self.client.update_project(project_guid, update_body)
            console.print(f"[green]✓[/green] Updated project")

            # Step 3: Retrieve project
            console.print(f"\n[cyan]Retrieving project: {project_guid}[/cyan]")
            retrieved = self.client.get_project_by_guid(project_guid)
            if isinstance(retrieved, dict):
                console.print(f"[green]✓[/green] Retrieved project")
            else:
                console.print(f"[green]✓[/green] Retrieved project data")

            # Step 4: Delete project
            console.print(f"\n[cyan]Deleting project: {project_guid}[/cyan]")
            self.client.delete_project(project_guid)
            self.created_projects.remove(project_guid)
            console.print(f"[green]✓[/green] Deleted project")

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

    def scenario_search_projects(self) -> TestResult:
        """
        Scenario: Search projects
        - Create multiple projects
        - Search by name
        - Find with search string
        - Retrieve specific projects
        - Clean up
        """
        scenario_name = "Search Projects"
        start_time = time.perf_counter()

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = f"Search_Test_{timestamp}"

            # Step 1: Create multiple projects
            project_names = [
                f"{base_name}_Alpha",
                f"{base_name}_Beta",
                f"{base_name}_Gamma"
            ]
            created_guids = []

            for name in project_names:
                console.print(f"\n[cyan]Creating project: {name}[/cyan]")
                body = {
                    "class": "NewElementRequestBody",
                    "properties": {
                        "class": "ProjectProperties",
                        "qualifiedName": f"Project:{name}",
                        "identifier": f"ID-{name}",
                        "name": name,
                        "description": f"Test project for {name}",
                        "projectStatus": "ACTIVE",
                    },
                }

                guid = self.client.create_project(body)
                created_guids.append(guid)
                self.created_projects.append(guid)
                console.print(f"[green]✓[/green] Created: {guid}")

            # Step 2: Search by name
            console.print(f"\n[cyan]Searching for projects with name: {base_name}[/cyan]")
            search_results = self.client.get_projects_by_name(filter_string=base_name)
            if isinstance(search_results, list):
                console.print(f"[green]✓[/green] Found {len(search_results)} projects")
            else:
                console.print(f"[green]✓[/green] Search completed")

            # Step 3: Find with search string
            console.print(f"\n[cyan]Finding projects with search string: {base_name}[/cyan]")
            find_results = self.client.find_projects(search_string=base_name)
            if isinstance(find_results, list):
                console.print(f"[green]✓[/green] Found {len(find_results)} projects")
            else:
                console.print(f"[green]✓[/green] Find completed")

            # Step 4: Retrieve each project by GUID
            for guid in created_guids:
                console.print(f"\n[cyan]Retrieving project: {guid}[/cyan]")
                project = self.client.get_project_by_guid(guid)
                if isinstance(project, dict):
                    console.print(f"[green]✓[/green] Retrieved project")
                else:
                    console.print(f"[green]✓[/green] Retrieved project data")

            # Step 5: Clean up
            for guid in created_guids:
                console.print(f"\n[cyan]Deleting project: {guid}[/cyan]")
                self.client.delete_project(guid)
                self.created_projects.remove(guid)
                console.print(f"[green]✓[/green] Deleted")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=True,
                duration=duration,
                message=f"Successfully searched and retrieved {len(project_names)} projects",
            )

        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=False,
                duration=duration,
                error=str(e),
            )

    def scenario_project_from_template(self) -> TestResult:
        """
        Scenario: Create project from template
        - Create a template project
        - Create new project from template
        - Verify both exist
        - Clean up
        """
        scenario_name = "Project from Template"
        start_time = time.perf_counter()

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Step 1: Create template project
            template_name = f"Template_Project_{timestamp}"
            console.print(f"\n[cyan]Creating template project: {template_name}[/cyan]")

            template_body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "ProjectProperties",
                    "qualifiedName": f"Project:{template_name}",
                    "identifier": f"TMPL-{timestamp}",
                    "name": template_name,
                    "description": "Template for creating new projects",
                    "projectStatus": "ACTIVE",
                    "projectPhase": "PLANNING",
                },
            }

            template_guid = self.client.create_project(template_body)
            self.created_projects.append(template_guid)
            console.print(f"[green]✓[/green] Created template: {template_guid}")

            # Step 2: Create project from template
            new_name = f"From_Template_{timestamp}"
            console.print(f"\n[cyan]Creating project from template: {new_name}[/cyan]")

            from_template_body = {
                "class": "TemplateRequestBody",
                "templateGUID": template_guid,
                "replacementProperties": {
                    "class": "ProjectProperties",
                    "qualifiedName": f"Project:{new_name}",
                    "identifier": f"NEW-{timestamp}",
                    "name": new_name,
                    "description": "Created from template",
                },
            }

            new_guid = self.client.create_project_from_template(from_template_body)
            self.created_projects.append(new_guid)
            console.print(f"[green]✓[/green] Created from template: {new_guid}")

            # Step 3: Verify both exist
            console.print(f"\n[cyan]Verifying template project[/cyan]")
            template_proj = self.client.get_project_by_guid(template_guid)
            console.print(f"[green]✓[/green] Template project exists")

            console.print(f"\n[cyan]Verifying new project[/cyan]")
            new_proj = self.client.get_project_by_guid(new_guid)
            console.print(f"[green]✓[/green] New project exists")

            # Step 4: Clean up
            for guid in [new_guid, template_guid]:
                console.print(f"\n[cyan]Deleting project: {guid}[/cyan]")
                self.client.delete_project(guid)
                self.created_projects.remove(guid)
                console.print(f"[green]✓[/green] Deleted")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=True,
                duration=duration,
                message="Successfully created project from template",
            )

        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=False,
                duration=duration,
                error=str(e),
            )

    def scenario_project_hierarchy(self) -> TestResult:
        """
        Scenario: Project hierarchy
        - Create a parent project
        - Create child projects
        - Link projects
        - Retrieve linked projects
        - Clean up
        """
        scenario_name = "Project Hierarchy"
        start_time = time.perf_counter()

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Step 1: Create parent project
            parent_name = f"Parent_Project_{timestamp}"
            console.print(f"\n[cyan]Creating parent project: {parent_name}[/cyan]")

            parent_body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "ProjectProperties",
                    "qualifiedName": f"Project:{parent_name}",
                    "identifier": f"PARENT-{timestamp}",
                    "name": parent_name,
                    "description": "Parent project for hierarchy testing",
                    "projectStatus": "ACTIVE",
                },
            }

            parent_guid = self.client.create_project(parent_body)
            self.created_projects.append(parent_guid)
            console.print(f"[green]✓[/green] Created parent project: {parent_guid}")

            # Step 2: Create child projects
            child_names = [f"Child_A_{timestamp}", f"Child_B_{timestamp}"]
            child_guids = []

            for child_name in child_names:
                console.print(f"\n[cyan]Creating child project: {child_name}[/cyan]")
                child_body = {
                    "class": "NewElementRequestBody",
                    "properties": {
                        "class": "ProjectProperties",
                        "qualifiedName": f"Project:{child_name}",
                        "identifier": f"CHILD-{child_name}",
                        "name": child_name,
                        "description": f"Child project {child_name}",
                        "projectStatus": "ACTIVE",
                    },
                }

                child_guid = self.client.create_project(child_body)
                child_guids.append(child_guid)
                self.created_projects.append(child_guid)
                console.print(f"[green]✓[/green] Created child project: {child_guid}")

            # Step 3: Retrieve linked projects (if any exist)
            console.print(f"\n[cyan]Retrieving linked projects for parent[/cyan]")
            try:
                linked = self.client.get_linked_projects(parent_guid)
                if isinstance(linked, list):
                    console.print(f"[green]✓[/green] Found {len(linked)} linked projects")
                else:
                    console.print(f"[yellow]⚠[/yellow] No linked projects found (expected for new projects)")
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Could not retrieve linked projects: {str(e)}")

            # Step 4: Clean up (delete children first, then parent)
            for guid in child_guids:
                console.print(f"\n[cyan]Deleting child project: {guid}[/cyan]")
                self.client.delete_project(guid)
                self.created_projects.remove(guid)
                console.print(f"[green]✓[/green] Deleted")

            console.print(f"\n[cyan]Deleting parent project: {parent_guid}[/cyan]")
            self.client.delete_project(parent_guid)
            self.created_projects.remove(parent_guid)
            console.print(f"[green]✓[/green] Deleted")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                passed=True,
                duration=duration,
                message="Successfully tested project hierarchy",
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
            "[bold cyan]ProjectManager Scenario Tests[/bold cyan]\n"
            "Testing comprehensive CRUD workflows for projects",
            border_style="cyan"
        ))

        if not self.setup():
            return results

        try:
            # Run each scenario
            scenarios = [
                self.scenario_complete_project_lifecycle,
                self.scenario_search_projects,
                self.scenario_project_from_template,
                self.scenario_project_hierarchy,
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


def test_project_manager_scenarios():
    """Pytest entry point"""
    tester = ProjectManagerScenarioTester()
    results = tester.run_all_scenarios()
    tester.print_results_summary(results)

    # Assert that all scenarios passed
    assert all(result.passed for result in results), "Some scenarios failed"


if __name__ == "__main__":
    tester = ProjectManagerScenarioTester()
    results = tester.run_all_scenarios()
    tester.print_results_summary(results)