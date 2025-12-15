#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario-based testing for Solution Architect with synthetic data.

This executable test script runs realistic scenarios for solution architecture management,
including creating information supply chains, solution blueprints, and solution components,
with comprehensive cleanup and detailed error reporting.

Usage:
    python tests/test_solution_architect_scenarios.py
    
    Or with pytest:
    pytest tests/test_solution_architect_scenarios.py -v -s
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

from pyegeria.solution_architect import SolutionArchitect
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
USER_ID = "erinoverview"
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
class SupplyChainData:
    """Synthetic information supply chain data"""
    qualified_name: str
    display_name: str
    description: str
    scope: Optional[str] = None
    purposes: Optional[List[str]] = None
    guid: Optional[str] = None


@dataclass
class BlueprintData:
    """Synthetic solution blueprint data"""
    qualified_name: str
    display_name: str
    description: str
    guid: Optional[str] = None


@dataclass
class ComponentData:
    """Synthetic solution component data"""
    qualified_name: str
    display_name: str
    description: str
    guid: Optional[str] = None


class SolutionArchitectScenarioTester:
    """Execute realistic solution architecture scenarios"""
    
    def __init__(self):
        self.client: Optional[SolutionArchitect] = None
        self.results: List[TestResult] = []
        self.created_supply_chains: List[str] = []
        self.created_blueprints: List[str] = []
        self.created_components: List[str] = []
        self.test_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def setup(self) -> bool:
        """Initialize connection to Egeria"""
        try:
            console.print("\n[bold cyan]═══ Setting up Solution Architect Test Environment ═══[/bold cyan]\n")
            self.client = SolutionArchitect(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
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
    
    def cleanup_created_elements(self):
        """Delete all solution architecture elements created during testing"""
        console.print("\n[bold yellow]═══ Cleaning Up Test Data ═══[/bold yellow]\n")
        
        total_items = len(self.created_components) + len(self.created_blueprints) + len(self.created_supply_chains)
        if total_items == 0:
            console.print("No solution architecture elements to clean up")
            return
        
        cleanup_results = {"success": 0, "failed": 0, "not_found": 0}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(
                f"Cleaning up {total_items} solution architecture elements...",
                total=total_items
            )
            
            # Delete in reverse order: components, blueprints, then supply chains
            for guid in reversed(self.created_components):
                try:
                    self.client.delete_solution_component(guid)
                    cleanup_results["success"] += 1
                except PyegeriaAPIException:
                    cleanup_results["not_found"] += 1
                except Exception as e:
                    cleanup_results["failed"] += 1
                    console.print(f"[yellow]Warning: Failed to delete component {guid}: {str(e)}[/yellow]")
                finally:
                    progress.advance(task)
            
            for guid in reversed(self.created_blueprints):
                try:
                    self.client.delete_solution_blueprint(guid)
                    cleanup_results["success"] += 1
                except PyegeriaAPIException:
                    cleanup_results["not_found"] += 1
                except Exception as e:
                    cleanup_results["failed"] += 1
                    console.print(f"[yellow]Warning: Failed to delete blueprint {guid}: {str(e)}[/yellow]")
                finally:
                    progress.advance(task)
            
            for guid in reversed(self.created_supply_chains):
                try:
                    self.client.delete_info_supply_chain(guid)
                    cleanup_results["success"] += 1
                except PyegeriaAPIException:
                    cleanup_results["not_found"] += 1
                except Exception as e:
                    cleanup_results["failed"] += 1
                    console.print(f"[yellow]Warning: Failed to delete supply chain {guid}: {str(e)}[/yellow]")
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
    
    def _create_supply_chain(self, chain_data: SupplyChainData) -> Optional[str]:
        """Helper to create an information supply chain and track it"""
        body = {
            "class": "NewElementRequestBody",
            "isOwnAnchor": True,
            "properties": {
                "class": "InformationSupplyChainProperties",
                "qualifiedName": chain_data.qualified_name,
                "displayName": chain_data.display_name,
                "description": chain_data.description,
            }
        }
        if chain_data.scope:
            body["properties"]["scope"] = chain_data.scope
        if chain_data.purposes:
            body["properties"]["purposes"] = chain_data.purposes
            
        guid = self.client.create_info_supply_chain(body)
        if guid:
            self.created_supply_chains.append(guid)
            chain_data.guid = guid
        return guid
    
    def _create_blueprint(self, blueprint_data: BlueprintData) -> Optional[str]:
        """Helper to create a solution blueprint and track it"""
        body = {
            "class": "NewElementRequestBody",
            "isOwnAnchor": True,
            "properties": {
                "class": "SolutionBlueprintProperties",
                "qualifiedName": blueprint_data.qualified_name,
                "displayName": blueprint_data.display_name,
                "description": blueprint_data.description,
            }
        }
        guid = self.client.create_solution_blueprint(body)
        if guid:
            self.created_blueprints.append(guid)
            blueprint_data.guid = guid
        return guid
    
    def _create_component(self, component_data: ComponentData) -> Optional[str]:
        """Helper to create a solution component and track it"""
        body = {
            "class": "NewElementRequestBody",
            "isOwnAnchor": True,
            "properties": {
                "class": "SolutionComponentProperties",
                "qualifiedName": component_data.qualified_name,
                "displayName": component_data.display_name,
                "description": component_data.description,
            }
        }
        guid = self.client.create_solution_component(body)
        if guid:
            self.created_components.append(guid)
            component_data.guid = guid
        return guid
    
    def scenario_1_supply_chain_architecture(self) -> TestResult:
        """
        Scenario 1: Create an information supply chain architecture
        - Data Ingestion Supply Chain
        - Data Processing Supply Chain
        - Data Distribution Supply Chain
        """
        scenario_name = "Information Supply Chain Architecture"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Scenario 1: {scenario_name}[/bold blue]")
            
            # Create supply chains
            supply_chains = {
                "ingestion": SupplyChainData(
                    f"SupplyChain::DataIngestion::{self.test_run_id}",
                    "Data Ingestion Supply Chain",
                    "Manages data ingestion from various sources",
                    "Enterprise",
                    ["data collection", "data validation"]
                ),
                "processing": SupplyChainData(
                    f"SupplyChain::DataProcessing::{self.test_run_id}",
                    "Data Processing Supply Chain",
                    "Handles data transformation and enrichment",
                    "Enterprise",
                    ["data transformation", "data quality"]
                ),
                "distribution": SupplyChainData(
                    f"SupplyChain::DataDistribution::{self.test_run_id}",
                    "Data Distribution Supply Chain",
                    "Distributes processed data to consumers",
                    "Enterprise",
                    ["data delivery", "data access"]
                ),
            }
            
            for key, chain in supply_chains.items():
                guid = self._create_supply_chain(chain)
                created_guids.append(guid)
                console.print(f"  ✓ Created supply chain: {chain.display_name}")
            
            duration = time.perf_counter() - start_time
            console.print(f"  [green]✓ Scenario completed in {duration:.2f}s[/green]")
            
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Created {len(supply_chains)} information supply chains",
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
    
    def scenario_2_solution_blueprint_design(self) -> TestResult:
        """
        Scenario 2: Create solution blueprints for different architectures
        - Microservices Architecture Blueprint
        - Data Lake Architecture Blueprint
        - API Gateway Architecture Blueprint
        """
        scenario_name = "Solution Blueprint Design"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Scenario 2: {scenario_name}[/bold blue]")
            
            # Create solution blueprints
            blueprints = {
                "microservices": BlueprintData(
                    f"Blueprint::Microservices::{self.test_run_id}",
                    "Microservices Architecture",
                    "Blueprint for microservices-based applications"
                ),
                "data_lake": BlueprintData(
                    f"Blueprint::DataLake::{self.test_run_id}",
                    "Data Lake Architecture",
                    "Blueprint for enterprise data lake implementation"
                ),
                "api_gateway": BlueprintData(
                    f"Blueprint::APIGateway::{self.test_run_id}",
                    "API Gateway Architecture",
                    "Blueprint for API management and gateway"
                ),
            }
            
            for key, blueprint in blueprints.items():
                guid = self._create_blueprint(blueprint)
                created_guids.append(guid)
                console.print(f"  ✓ Created blueprint: {blueprint.display_name}")
            
            duration = time.perf_counter() - start_time
            console.print(f"  [green]✓ Scenario completed in {duration:.2f}s[/green]")
            
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Created {len(blueprints)} solution blueprints",
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
    
    def scenario_3_solution_components(self) -> TestResult:
        """
        Scenario 3: Create solution components for implementation
        - Database Component
        - Message Queue Component
        - API Service Component
        """
        scenario_name = "Solution Component Definition"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Scenario 3: {scenario_name}[/bold blue]")
            
            # Create solution components
            components = {
                "database": ComponentData(
                    f"Component::Database::{self.test_run_id}",
                    "Database Component",
                    "Relational database for data storage"
                ),
                "message_queue": ComponentData(
                    f"Component::MessageQueue::{self.test_run_id}",
                    "Message Queue Component",
                    "Message broker for asynchronous communication"
                ),
                "api_service": ComponentData(
                    f"Component::APIService::{self.test_run_id}",
                    "API Service Component",
                    "RESTful API service for data access"
                ),
            }
            
            for key, component in components.items():
                guid = self._create_component(component)
                created_guids.append(guid)
                console.print(f"  ✓ Created component: {component.display_name}")
            
            duration = time.perf_counter() - start_time
            console.print(f"  [green]✓ Scenario completed in {duration:.2f}s[/green]")
            
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Created {len(components)} solution components",
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
            self.results.append(self.scenario_1_supply_chain_architecture())
            self.results.append(self.scenario_2_solution_blueprint_design())
            self.results.append(self.scenario_3_solution_components())
            
            # Cleanup
            self.cleanup_created_elements()
            
            # Generate report
            return self.generate_report()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Test execution interrupted by user[/yellow]")
            self.cleanup_created_elements()
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
        "[bold cyan]Solution Architect Scenario Testing[/bold cyan]\n"
        "Comprehensive testing with synthetic data and automatic cleanup",
        border_style="cyan"
    ))
    
    tester = SolutionArchitectScenarioTester()
    exit_code = tester.run_all_scenarios()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()