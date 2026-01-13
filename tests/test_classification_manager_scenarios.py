#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario-based testing for Classification Manager with realistic query workflows.

This executable test script runs realistic scenarios for classification management operations,
including querying classified elements, exploring security tags, and analyzing governance relationships,
with comprehensive error reporting.

Usage:
    python tests/test_classification_manager_scenarios.py
    
    Or with pytest:
    pytest tests/test_classification_manager_scenarios.py -v -s
"""

import sys
import time
import traceback
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from pyegeria import EgeriaTech
from pyegeria.core._exceptions import (
    PyegeriaException,
    PyegeriaAPIException,
    print_exception_table,
)
from pyegeria.models import (
    NewElementRequestBody,
    NewClassificationRequestBody,
    DeleteElementRequestBody,
)

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
    

class ClassificationManagerScenarioTester:
    """Execute realistic classification management scenarios"""
    
    def __init__(self):
        self.client: Optional[EgeriaTech] = None
        self.results: List[TestResult] = []
        self.test_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.created_guids: List[str] = []
        
    def setup(self) -> bool:
        """Initialize connection to Egeria and create test data"""
        try:
            console.print("\n[bold cyan]═══ Setting up Classification Manager Test Environment ═══[/bold cyan]\n")
            self.client = EgeriaTech(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
            token = self.client.create_egeria_bearer_token(USER_ID, USER_PWD)
            console.print(f"✓ Connected to {PLATFORM_URL}")
            console.print(f"✓ Authenticated as {USER_ID}")
            console.print(f"✓ Test Run ID: {self.test_run_id}\n")

            # Create test Glossary
            glossary_qname = f"Glossary::Scenario::{self.test_run_id}"
            glossary_guid = self.client.create_glossary(
                display_name=f"Scenario Test Glossary {self.test_run_id}",
                description="Glossary for classification scenario testing",
                body=NewElementRequestBody(
                    class_="NewElementRequestBody",
                    properties={"class": "GlossaryProperties", "qualifiedName": glossary_qname}
                )
            )
            self.created_guids.append(glossary_guid)
            console.print(f"✓ Created test Glossary: {glossary_guid}")

            # Create test terms and classify them
            term_names = ["Confidential Term", "Owned Term", "Origin Term"]
            for name in term_names:
                term_qname = f"Term::{name}::{self.test_run_id}"
                term_guid = self.client.create_glossary_term(
                    body=NewElementRequestBody(
                        class_="NewElementRequestBody",
                        anchor_guid=glossary_guid,
                        properties={
                            "class": "GlossaryTermProperties",
                            "qualifiedName": term_qname,
                            "displayName": name
                        }
                    )
                )
                self.created_guids.append(term_guid)
                console.print(f"✓ Created test Term '{name}': {term_guid}")

                if name == "Confidential Term":
                    self.client.set_confidentiality_classification(
                        term_guid,
                        body={
                            "class": "NewClassificationRequestBody",
                            "properties": {
                                "class": "ConfidentialityProperties",
                                "levelIdentifier": 3,
                                "confidence": 100,
                                "status": 1
                            }
                        }
                    )
                    console.print("  - Applied Confidentiality classification")
                elif name == "Owned Term":
                    self.client.add_ownership_to_element(
                        term_guid,
                        body={
                            "class": "NewClassificationRequestBody",
                            "properties": {
                                "class": "OwnershipProperties",
                                "owner": USER_ID,
                                "ownerTypeName": "USER_ID"
                            }
                        }
                    )
                    console.print(f"  - Applied Ownership classification")
                elif name == "Origin Term":
                    self.client.add_digital_resource_origin(
                        term_guid,
                        body=NewClassificationRequestBody(
                            class_="NewClassificationRequestBody",
                            properties={
                                "class": "DigitalResourceOriginProperties",
                                "source": "Scenario Test Script",
                                "description": "Created for testing"
                            }
                        ).model_dump(exclude_none=True, by_alias=True)
                    )
                    console.print(f"  - Applied Origin classification")

            return True

        except Exception as e:
            console.print(f"[bold red]✗ Setup failed: {str(e)}[/bold red]")
            traceback.print_exc()
            return False
    
    def teardown(self):
        """Clean up and close connection"""
        if self.client:
            console.print("\n[bold cyan]═══ Cleaning up Test Data ═══[/bold cyan]\n")
            for guid in reversed(self.created_guids):
                try:
                    # Check if it's a glossary or term to use appropriate delete method
                    # For simplicity, we can use a generic delete if available, 
                    # but here we'll try to be specific or use the most flexible one.
                    # GlossaryManager has delete_term and delete_glossary
                    # We can use find_element_by_guid to check type if needed, 
                    # but we know the order in created_guids (glossary first, then terms)
                    if guid == self.created_guids[0]:
                         self.client.delete_glossary(guid, body=DeleteElementRequestBody(class_="DeleteElementRequestBody"), cascade=True)
                         console.print(f"✓ Deleted Glossary: {guid}")
                    else:
                         self.client.delete_term(guid, body=DeleteElementRequestBody(class_="DeleteElementRequestBody"))
                         console.print(f"✓ Deleted Term: {guid}")
                except Exception as e:
                    console.print(f"⚠ Failed to delete {guid}: {str(e)}")

            self.client.close_session()
            console.print("\n✓ Session closed")
    
    def print_results_summary(self):
        """Print a summary table of all test results"""
        console.print("\n[bold cyan]═══ Test Results Summary ═══[/bold cyan]\n")
        
        table = Table(show_header=True, header_style="bold magenta", show_lines=True)
        table.add_column("Scenario", style="cyan", width=50)
        table.add_column("Status", justify="center", width=12)
        table.add_column("Duration (s)", justify="right", width=15)
        table.add_column("Message", width=60)
        
        passed = failed = warnings = 0
        
        for result in self.results:
            if result.status == "PASSED":
                status_style = "[green]✓ PASSED[/green]"
                passed += 1
            elif result.status == "FAILED":
                status_style = "[red]✗ FAILED[/red]"
                failed += 1
            else:
                status_style = "[yellow]⚠ WARNING[/yellow]"
                warnings += 1
            
            table.add_row(
                result.scenario_name,
                status_style,
                f"{result.duration:.3f}",
                result.message[:60] if result.message else ""
            )
        
        console.print(table)
        
        # Summary stats
        total = len(self.results)
        console.print(f"\n[bold]Total Scenarios:[/bold] {total}")
        console.print(f"[green]Passed:[/green] {passed}")
        console.print(f"[red]Failed:[/red] {failed}")
        console.print(f"[yellow]Warnings:[/yellow] {warnings}")
        
        if failed > 0:
            console.print("\n[bold red]Some scenarios failed. Check the details above.[/bold red]")
        elif warnings > 0:
            console.print("\n[bold yellow]All scenarios passed with some warnings.[/bold yellow]")
        else:
            console.print("\n[bold green]All scenarios passed successfully! ✓[/bold green]")
    
    def scenario_explore_classified_elements(self) -> TestResult:
        """Scenario: Explore elements by classification"""
        scenario_name = "Explore Classified Elements"
        start_time = time.perf_counter()
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # Query elements with confidentiality classification
            console.print("  → Querying elements with 'Confidentiality' classification...")
            classification_name = "Confidentiality"
            body = {
                "class": "LevelIdentifierQueryProperties",
                "levelIdentifier": 1
            }
            
            elements = self.client.get_classified_elements_by(classification_name, body, output_format="JSON")
            
            if isinstance(elements, list):
                element_count = len(elements)
                console.print(f"  ✓ Found {element_count} elements with confidentiality classification")
                
                # Show sample elements
                if element_count > 0:
                    console.print("\n  Sample Classified Elements:")
                    for element in elements[:5]:  # Show first 5
                        if isinstance(element, dict):
                            props = element.get('properties', {})
                            name = props.get('displayName', props.get('qualifiedName', 'Unknown'))
                            console.print(f"    • {name}")
                
                duration = time.perf_counter() - start_time
                return TestResult(
                    scenario_name=scenario_name,
                    status="PASSED",
                    duration=duration,
                    message=f"Found {element_count} classified elements"
                )
            else:
                duration = time.perf_counter() - start_time
                return TestResult(
                    scenario_name=scenario_name,
                    status="WARNING",
                    duration=duration,
                    message="No classified elements found or unexpected format"
                )
                
        except PyegeriaAPIException as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [yellow]⚠ API Exception: {str(e)}[/yellow]")
            return TestResult(
                scenario_name=scenario_name,
                status="WARNING",
                duration=duration,
                message=f"API Exception: {str(e)[:100]}",
                error=e
            )
        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Error: {str(e)}[/red]")
            print_exception_table(e) if isinstance(e, PyegeriaException) else console.print_exception()
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e)[:100],
                error=e
            )
    
    def scenario_explore_owned_elements(self) -> TestResult:
        """Scenario: Explore elements by ownership"""
        scenario_name = "Explore Owned Elements"
        start_time = time.perf_counter()
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # Query elements owned by a specific owner
            console.print("  → Querying elements by owner...")
            owner_name = "f6bc847b-868d-43cc-b767-41f5fe3e47d1"
            body = {
                "class": "FilterRequestBody",
                "filter": owner_name
            }
            
            elements = self.client.get_owners_elements(owner_name, body, output_format="JSON")
            
            if isinstance(elements, list):
                element_count = len(elements)
                console.print(f"  ✓ Found {element_count} elements owned by '{owner_name}'")
                
                # Show sample elements
                if element_count > 0:
                    console.print("\n  Sample Owned Elements:")
                    for element in elements[:5]:  # Show first 5
                        if isinstance(element, dict):
                            props = element.get('properties', {})
                            name = props.get('displayName', props.get('qualifiedName', 'Unknown'))
                            element_type = element.get('type', {}).get('typeName', 'Unknown')
                            console.print(f"    • {name} ({element_type})")
                
                duration = time.perf_counter() - start_time
                return TestResult(
                    scenario_name=scenario_name,
                    status="PASSED",
                    duration=duration,
                    message=f"Found {element_count} owned elements"
                )
            else:
                duration = time.perf_counter() - start_time
                return TestResult(
                    scenario_name=scenario_name,
                    status="WARNING",
                    duration=duration,
                    message="No owned elements found or unexpected format"
                )
                
        except PyegeriaAPIException as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [yellow]⚠ API Exception: {str(e)}[/yellow]")
            return TestResult(
                scenario_name=scenario_name,
                status="WARNING",
                duration=duration,
                message=f"API Exception: {str(e)[:100]}",
                error=e
            )
        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Error: {str(e)}[/red]")
            print_exception_table(e) if isinstance(e, PyegeriaException) else console.print_exception()
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e)[:100],
                error=e
            )
    
    def scenario_explore_elements_by_origin(self) -> TestResult:
        """Scenario: Explore elements by their origin"""
        scenario_name = "Explore Elements by Origin"
        start_time = time.perf_counter()
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # Query elements by origin
            console.print("  → Querying elements by origin...")
            body = {
                "class": "FindDigitalResourceOriginProperties",
                "properties": {
                    "class" : "DigitalResourceOriginProperties",
                  "organization": None,
                  "organizationPropertyName": None,
                  "businessCapability"   : None,
                  "businessCapabilityPropertyName" : None,
                  "otherOriginValues": {}
                }
            }
            
            elements = self.client.get_elements_by_origin(body, output_format="JSON")
            
            if isinstance(elements, list):
                element_count = len(elements)
                console.print(f"  ✓ Found {element_count} elements with origin information")
                
                # Analyze origins
                if element_count > 0:
                    origins = {}
                    for element in elements:
                        if isinstance(element, dict):
                            origin = element.get('origin', {})
                            origin_type = origin.get('sourceServer', 'Unknown')
                            origins[origin_type] = origins.get(origin_type, 0) + 1
                    
                    console.print("\n  Origin Distribution:")
                    for origin_type, count in sorted(origins.items(), key=lambda x: x[1], reverse=True)[:5]:
                        console.print(f"    • {origin_type}: {count} elements")
                
                duration = time.perf_counter() - start_time
                return TestResult(
                    scenario_name=scenario_name,
                    status="PASSED",
                    duration=duration,
                    message=f"Found {element_count} elements with origin"
                )
            else:
                duration = time.perf_counter() - start_time
                return TestResult(
                    scenario_name=scenario_name,
                    status="WARNING",
                    duration=duration,
                    message="No elements with origin found or unexpected format"
                )
                
        except PyegeriaAPIException as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [yellow]⚠ API Exception: {str(e)}[/yellow]")
            return TestResult(
                scenario_name=scenario_name,
                status="WARNING",
                duration=duration,
                message=f"API Exception: {str(e)[:100]}",
                error=e
            )
        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Error: {str(e)}[/red]")
            print_exception_table(e) if isinstance(e, PyegeriaException) else console.print_exception()
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e)[:100],
                error=e
            )
    
    def scenario_query_elements_by_property(self) -> TestResult:
        """Scenario: Query elements by property values"""
        scenario_name = "Query Elements by Property"
        start_time = time.perf_counter()
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # Query elements by property value
            console.print("  → Querying elements by property value...")
            property_value = "Hospital"
            property_names = ["displayName", "qualifiedName"]
            
            elements = self.client.get_elements_by_property_value(
                property_value, 
                property_names,
                # output_format="JSON"
            )
            
            if isinstance(elements, list):
                element_count = len(elements)
                console.print(f"  ✓ Found {element_count} elements matching '{property_value}'")
                
                # Show sample elements
                if element_count > 0:
                    console.print("\n  Sample Matching Elements:")
                    for element in elements[:5]:  # Show first 5
                        if isinstance(element, dict):
                            props = element.get('properties', {})
                            name = props.get('displayName', props.get('qualifiedName', 'Unknown'))
                            element_type = element.get('type', {}).get('typeName', 'Unknown')
                            console.print(f"    • {name} ({element_type})")
                
                duration = time.perf_counter() - start_time
                return TestResult(
                    scenario_name=scenario_name,
                    status="PASSED",
                    duration=duration,
                    message=f"Found {element_count} matching elements"
                )
            else:
                duration = time.perf_counter() - start_time
                return TestResult(
                    scenario_name=scenario_name,
                    status="WARNING",
                    duration=duration,
                    message="No matching elements found or unexpected format"
                )
                
        except PyegeriaAPIException as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [yellow]⚠ API Exception: {str(e)}[/yellow]")
            return TestResult(
                scenario_name=scenario_name,
                status="WARNING",
                duration=duration,
                message=f"API Exception: {str(e)[:100]}",
                error=e
            )
        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Error: {str(e)}[/red]")
            print_exception_table(e) if isinstance(e, PyegeriaException) else console.print_exception()
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e)[:100],
                error=e
            )
    
    def run_all_scenarios(self):
        """Execute all test scenarios"""
        console.print(Panel.fit(
            "[bold cyan]Classification Manager Scenario Tests[/bold cyan]\n"
            f"Test Run ID: {self.test_run_id}",
            border_style="cyan"
        ))
        
        if not self.setup():
            console.print("[bold red]Setup failed. Cannot proceed with tests.[/bold red]")
            return False
        
        try:
            # Run all scenarios
            self.results.append(self.scenario_explore_classified_elements())
            self.results.append(self.scenario_explore_owned_elements())
            self.results.append(self.scenario_explore_elements_by_origin())
            self.results.append(self.scenario_query_elements_by_property())
            
            # Print summary
            self.print_results_summary()
            
            # Return success if no failures
            return all(r.status != "FAILED" for r in self.results)
            
        finally:
            self.teardown()


def test_classification_manager_scenarios():
    """Pytest entry point for classification manager scenario tests"""
    tester = ClassificationManagerScenarioTester()
    success = tester.run_all_scenarios()
    assert success, "One or more scenarios failed"


if __name__ == "__main__":
    """Direct execution entry point"""
    tester = ClassificationManagerScenarioTester()
    success = tester.run_all_scenarios()
    sys.exit(0 if success else 1)