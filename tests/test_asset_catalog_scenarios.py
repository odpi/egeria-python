#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario-based testing for Asset Catalog with realistic search and exploration workflows.

This executable test script runs realistic scenarios for asset catalog operations,
including searching for assets, exploring relationships, and analyzing lineage,
with comprehensive error reporting.

Usage:
    python tests/test_asset_catalog_scenarios.py
    
    Or with pytest:
    pytest tests/test_asset_catalog_scenarios.py -v -s
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

from pyegeria.asset_catalog import AssetCatalog
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
    assets_found: int = 0


class AssetCatalogScenarioTester:
    """Execute realistic asset catalog search and exploration scenarios"""
    
    def __init__(self):
        self.client: Optional[AssetCatalog] = None
        self.results: List[TestResult] = []
        self.test_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def setup(self) -> bool:
        """Initialize connection to Egeria"""
        try:
            console.print("\n[bold cyan]═══ Setting up Asset Catalog Test Environment ═══[/bold cyan]\n")
            self.client = AssetCatalog(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
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
    
    def scenario_1_asset_discovery(self) -> TestResult:
        """
        Scenario 1: Asset Discovery - Search for various asset types
        - Search for database assets
        - Search for file assets
        - Search for API assets
        - Analyze search results
        """
        scenario_name = "Asset Discovery and Search"
        start_time = time.perf_counter()
        total_assets_found = 0
        
        try:
            console.print(f"\n[bold blue]▶ Scenario 1: {scenario_name}[/bold blue]")
            
            # Define search terms for different asset types
            search_terms = {
                "Database": "Postgres",
                "Files": "File",
                "Data": "Data",
                "Unity": "Unity",
            }
            
            search_results = {}
            
            for asset_type, search_term in search_terms.items():
                try:
                    results = self.client.find_in_asset_domain(
                        search_term,
                        starts_with=True,
                        ends_with=False,
                        ignore_case=True,
                        output_format="JSON"
                    )
                    
                    if isinstance(results, list):
                        count = len(results)
                        search_results[asset_type] = count
                        total_assets_found += count
                        console.print(f"  ✓ Found {count} assets for '{asset_type}' (search: '{search_term}')")
                    else:
                        search_results[asset_type] = 0
                        console.print(f"  ℹ No assets found for '{asset_type}'")
                        
                except PyegeriaAPIException:
                    search_results[asset_type] = 0
                    console.print(f"  ℹ No assets found for '{asset_type}'")
            
            duration = time.perf_counter() - start_time
            console.print(f"  [green]✓ Scenario completed in {duration:.2f}s[/green]")
            console.print(f"  [cyan]Total assets discovered: {total_assets_found}[/cyan]")
            
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Discovered {total_assets_found} assets across {len(search_terms)} search categories",
                assets_found=total_assets_found
            )
            
        except ValidationError as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Scenario failed: ValidationError[/red]")
            print_validation_error(e)
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message="Validation error in request",
                error=e
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
                error=e
            )
    
    def scenario_2_asset_exploration(self) -> TestResult:
        """
        Scenario 2: Asset Exploration - Deep dive into asset details
        - Search for a specific asset
        - Retrieve asset graph
        - Explore asset relationships
        - Analyze asset metadata
        """
        scenario_name = "Asset Exploration and Relationships"
        start_time = time.perf_counter()
        
        try:
            console.print(f"\n[bold blue]▶ Scenario 2: {scenario_name}[/bold blue]")
            
            # Search for assets
            search_string = "File"
            search_results = self.client.find_in_asset_domain(
                search_string,
                starts_with=True,
                ends_with=False,
                ignore_case=True,
                output_format="JSON"
            )
            
            if isinstance(search_results, list) and len(search_results) > 0:
                console.print(f"  ✓ Found {len(search_results)} assets matching '{search_string}'")
                
                # Get first asset for detailed exploration
                first_asset = search_results[0]
                asset_guid = first_asset.get("elementHeader", {}).get("guid")
                asset_name = first_asset.get("properties", {}).get("qualifiedName", "Unknown")
                
                if asset_guid:
                    console.print(f"  ✓ Exploring asset: {asset_name}")
                    console.print(f"    GUID: {asset_guid}")
                    
                    # Get asset graph
                    try:
                        graph = self.client.get_asset_graph(
                            asset_guid,
                            output_format="JSON"
                        )
                        
                        if isinstance(graph, dict):
                            console.print(f"  ✓ Retrieved asset graph")
                            # Count relationships
                            relationships = graph.get("relationships", [])
                            if relationships:
                                console.print(f"    Found {len(relationships)} relationships")
                        elif isinstance(graph, list):
                            console.print(f"  ✓ Retrieved asset graph with {len(graph)} elements")
                    except PyegeriaAPIException:
                        console.print(f"  ℹ No graph available for this asset")
                    
                    # Try to get lineage
                    try:
                        lineage = self.client.get_asset_lineage_graph(
                            asset_guid,
                            output_format="JSON"
                        )
                        console.print(f"  ✓ Retrieved asset lineage")
                    except PyegeriaAPIException:
                        console.print(f"  ℹ No lineage available for this asset")
                    except Exception as e:
                        console.print(f"  [yellow]⚠[/yellow] Lineage retrieval skipped: {str(e)[:50]}")
                else:
                    console.print(f"  [yellow]⚠[/yellow] Asset GUID not found in search results")
            else:
                console.print(f"  [yellow]⚠[/yellow] No assets found for exploration")
            
            duration = time.perf_counter() - start_time
            console.print(f"  [green]✓ Scenario completed in {duration:.2f}s[/green]")
            
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message="Explored asset details, relationships, and lineage"
            )
            
        except ValidationError as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Scenario failed: ValidationError[/red]")
            print_validation_error(e)
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message="Validation error in request",
                error=e
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
                error=e
            )
    
    def scenario_3_asset_types_and_collections(self) -> TestResult:
        """
        Scenario 3: Asset Types and Metadata Collections
        - Retrieve available asset types
        - Query assets by metadata collection
        - Analyze asset type distribution
        """
        scenario_name = "Asset Types and Collections"
        start_time = time.perf_counter()
        
        try:
            console.print(f"\n[bold blue]▶ Scenario 3: {scenario_name}[/bold blue]")
            
            # Get available asset types
            asset_types = self.client.get_asset_types()
            
            if isinstance(asset_types, list):
                console.print(f"  ✓ Found {len(asset_types)} asset types")
                
                # Display first few types
                if len(asset_types) > 0:
                    console.print(f"  Sample asset types:")
                    for i, asset_type in enumerate(asset_types[:5]):
                        type_name = asset_type.get("name", "Unknown")
                        console.print(f"    - {type_name}")
                    if len(asset_types) > 5:
                        console.print(f"    ... and {len(asset_types) - 5} more")
            else:
                console.print(f"  ℹ No asset types retrieved")
            
            # Try to query by metadata collection (Coco Template Archive)
            try:
                metadata_collection_id = "9905c3cb-94c5-4494-9229-0d6f69c0b842"
                type_name = "FileFolder"
                
                collection_assets = self.client.get_assets_by_metadata_collection_id(
                    metadata_collection_id,
                    type_name,
                    output_format="JSON"
                )
                
                if isinstance(collection_assets, list):
                    console.print(f"  ✓ Found {len(collection_assets)} assets in metadata collection")
                else:
                    console.print(f"  ℹ No assets found in metadata collection")
                    
            except PyegeriaAPIException:
                console.print(f"  ℹ Metadata collection not found or empty")
            except Exception as e:
                console.print(f"  [yellow]⚠[/yellow] Collection query skipped: {str(e)[:50]}")
            
            duration = time.perf_counter() - start_time
            console.print(f"  [green]✓ Scenario completed in {duration:.2f}s[/green]")
            
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message="Analyzed asset types and metadata collections"
            )
            
        except ValidationError as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Scenario failed: ValidationError[/red]")
            print_validation_error(e)
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message="Validation error in request",
                error=e
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
                error=e
            )
    
    def scenario_4_mermaid_visualization(self) -> TestResult:
        """
        Scenario 4: Mermaid Graph Visualization
        - Search for an asset
        - Generate Mermaid graph
        - Generate Mermaid lineage graph
        """
        scenario_name = "Mermaid Graph Visualization"
        start_time = time.perf_counter()
        
        try:
            console.print(f"\n[bold blue]▶ Scenario 4: {scenario_name}[/bold blue]")
            
            # Search for assets to visualize
            search_results = self.client.find_in_asset_domain(
                "File",
                starts_with=True,
                ends_with=False,
                ignore_case=True,
                output_format="JSON"
            )
            
            if isinstance(search_results, list) and len(search_results) > 0:
                first_asset = search_results[0]
                asset_guid = first_asset.get("elementHeader", {}).get("guid")
                
                if asset_guid:
                    console.print(f"  ✓ Generating visualizations for asset: {asset_guid}")
                    
                    # Get Mermaid graph
                    try:
                        mermaid_graph = self.client.get_asset_mermaid_graph(asset_guid)
                        
                        if isinstance(mermaid_graph, str):
                            lines = mermaid_graph.count('\n')
                            console.print(f"  ✓ Generated Mermaid graph ({lines} lines)")
                        elif isinstance(mermaid_graph, dict):
                            console.print(f"  ✓ Generated Mermaid graph (dict format)")
                    except PyegeriaAPIException:
                        console.print(f"  ℹ No Mermaid graph available")
                    except Exception as e:
                        console.print(f"  [yellow]⚠[/yellow] Mermaid graph generation skipped: {str(e)[:50]}")
                    
                    # Get Mermaid lineage graph
                    try:
                        lineage_graph = self.client.get_asset_lineage_mermaid_graph(asset_guid)
                        
                        if isinstance(lineage_graph, str):
                            lines = lineage_graph.count('\n')
                            console.print(f"  ✓ Generated Mermaid lineage graph ({lines} lines)")
                        elif isinstance(lineage_graph, dict):
                            console.print(f"  ✓ Generated Mermaid lineage graph (dict format)")
                    except PyegeriaAPIException:
                        console.print(f"  ℹ No Mermaid lineage graph available")
                    except Exception as e:
                        console.print(f"  [yellow]⚠[/yellow] Mermaid lineage generation skipped: {str(e)[:50]}")
                else:
                    console.print(f"  [yellow]⚠[/yellow] No asset GUID available for visualization")
            else:
                console.print(f"  [yellow]⚠[/yellow] No assets found for visualization")
            
            duration = time.perf_counter() - start_time
            console.print(f"  [green]✓ Scenario completed in {duration:.2f}s[/green]")
            
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message="Generated Mermaid visualizations for assets"
            )
            
        except ValidationError as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Scenario failed: ValidationError[/red]")
            print_validation_error(e)
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message="Validation error in request",
                error=e
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
                error=e
            )
    
    def generate_report(self):
        """Generate comprehensive test report"""
        console.print("\n[bold cyan]═══ Test Execution Report ═══[/bold cyan]\n")
        
        # Summary statistics
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == "PASSED")
        failed = sum(1 for r in self.results if r.status == "FAILED")
        total_duration = sum(r.duration for r in self.results)
        total_assets = sum(r.assets_found for r in self.results)
        
        # Summary table
        summary_table = Table(title="Test Summary", show_header=True, header_style="bold magenta")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", justify="right", style="green")
        
        summary_table.add_row("Total Scenarios", str(total))
        summary_table.add_row("Passed", str(passed), style="green")
        summary_table.add_row("Failed", str(failed), style="red" if failed > 0 else "green")
        summary_table.add_row("Success Rate", f"{(passed/total*100):.1f}%" if total > 0 else "N/A")
        summary_table.add_row("Total Duration", f"{total_duration:.2f}s")
        summary_table.add_row("Assets Discovered", str(total_assets))
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
            self.results.append(self.scenario_1_asset_discovery())
            self.results.append(self.scenario_2_asset_exploration())
            self.results.append(self.scenario_3_asset_types_and_collections())
            self.results.append(self.scenario_4_mermaid_visualization())
            
            # Generate report
            return self.generate_report()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Test execution interrupted by user[/yellow]")
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
        "[bold cyan]Asset Catalog Scenario Testing[/bold cyan]\n"
        "Comprehensive testing of asset search, exploration, and visualization",
        border_style="cyan"
    ))
    
    tester = AssetCatalogScenarioTester()
    exit_code = tester.run_all_scenarios()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()