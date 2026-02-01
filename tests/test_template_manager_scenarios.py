#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario-based testing for Template Manager with synthetic data.

Usage:
    python tests/test_template_manager_scenarios.py
    
    Or with pytest:
    pytest tests/test_template_manager_scenarios.py -v -s
"""

import sys
import time
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from loguru import logger

from pyegeria.egeria_tech_client import EgeriaTech
from pyegeria.core._exceptions import (
    PyegeriaNotFoundException,
    PyegeriaTimeoutException,
)

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

class TemplateScenarioTester:
    """Execute realistic template management scenarios using EgeriaTech client"""
    
    def __init__(self):
        self.tech: Optional[EgeriaTech] = None
        self.results: List[TestResult] = []
        self.created_elements: List[str] = []
        self.test_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def setup(self) -> bool:
        """Initialize connection to Egeria"""
        try:
            console.print("\n[bold cyan]═══ Setting up Template Manager Scenario Test Environment ═══[/bold cyan]\n")
            self.tech = EgeriaTech(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
            self.tech.create_egeria_bearer_token(USER_ID, USER_PWD)
            console.print(f"✓ Connected to {PLATFORM_URL}")
            console.print(f"✓ Authenticated as {USER_ID}")
            console.print(f"✓ Test Run ID: {self.test_run_id}\n")
            return True
        except Exception as e:
            console.print(f"[bold red]✗ Setup failed: {str(e)}[/bold red]")
            return False
    
    def teardown(self):
        """Clean up and close connection"""
        if self.tech:
            self.tech.close_session()
            console.print("\n✓ Session closed")
    
    def cleanup_created_elements(self):
        """Delete all elements created during testing using MetadataExpert"""
        console.print("\n[bold yellow]═══ Cleaning Up Test Data ═══[/bold yellow]\n")
        
        if not self.created_elements:
            console.print("No elements to clean up")
            return
        
        cleanup_results = {"success": 0, "failed": 0, "not_found": 0}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Cleaning up...", total=len(self.created_elements))
            
            # Delete in reverse order of creation
            for guid in reversed(self.created_elements):
                try:
                    self.tech.expert.delete_metadata_element(
                        guid, 
                        {"class": "OpenMetadataDeleteRequestBody"}
                    )
                    cleanup_results["success"] += 1
                except PyegeriaNotFoundException:
                    cleanup_results["not_found"] += 1
                except Exception as e:
                    cleanup_results["failed"] += 1
                    logger.error(f"Failed to delete {guid}: {str(e)}")
                
                progress.advance(task)
        
        console.print(f"Cleanup complete: {cleanup_results['success']} deleted, "
                      f"{cleanup_results['not_found']} not found, "
                      f"{cleanup_results['failed']} failed")

    def _unique_qname(self, prefix: str) -> str:
        return f"{prefix}_{self.test_run_id}_{len(self.created_elements)}"

    def scenario_1_template_lifecycle(self) -> TestResult:
        """Test the lifecycle of a template element using expert and template clients"""
        start_time = time.perf_counter()
        scenario_name = "Template Lifecycle & Classification"
        created_in_scenario = []
        
        try:
            # 1. Create a metadata element using MetadataExpert
            qname = self._unique_qname("Template_Expert")
            body = {
                "class": "NewOpenMetadataElementRequestBody",
                "typeName": "Referenceable",
                "properties": {
                    "class": "ElementProperties",
                    "propertyValueMap": {
                        "qualifiedName": {
                            "class": "PrimitiveTypePropertyValue",
                            "typeName": "string",
                            "primitiveValue": qname
                        },
                        "description": {
                            "class": "PrimitiveTypePropertyValue",
                            "typeName": "string",
                            "primitiveValue": "Template for lifecycle testing"
                        }
                    }
                }
            }
            
            guid = self.tech.expert.create_metadata_element(body)
            self.created_elements.append(guid)
            created_in_scenario.append(guid)
            console.print(f"  [green]✓[/green] Created base element: {guid}")
            
            # 2. Classify it as a template using TemplateManager
            self.tech.templates.add_template_classification(guid, {
                "class": "NewClassificationRequestBody",
                "properties": {
                    "class": "TemplateProperties",
                    "displayName": "Test Template",
                    "description": "A test template classification"
                }
            })
            console.print(f"  [green]✓[/green] Added Template classification")
            
            # 3. Create another element from it using MetadataExpert
            new_qname = self._unique_qname("From_Template")
            from_template_body = {
                "class": "TemplateRequestBody",
                "templateGUID": guid,
                "replacementProperties": {
                    "class": "ElementProperties",
                    "propertyValueMap": {
                        "qualifiedName": {
                            "class": "PrimitiveTypePropertyValue",
                            "typeName": "string",
                            "primitiveValue": new_qname
                        }
                    }
                }
            }
            new_guid = self.tech.expert.create_metadata_element_from_template(from_template_body)
            self.created_elements.append(new_guid)
            created_in_scenario.append(new_guid)
            console.print(f"  [green]✓[/green] Created new element from template: {new_guid}")
            
            # 4. Link them using link_sourced_from in TemplateManager
            self.tech.templates.link_sourced_from(new_guid, guid, {
                "class": "NewRelationshipRequestBody",
                "relationshipProperties": {
                    "class": "SourceFromProperties",
                    "sourceVersionNumber": 1
                }
            })
            console.print(f"  [green]✓[/green] Linked new element to source template")
            
            # 5. Remove classification
            self.tech.templates.remove_template_classification(guid)
            console.print(f"  [green]✓[/green] Removed Template classification")
            
            duration = time.perf_counter() - start_time
            return TestResult(scenario_name, "PASSED", duration, "Successfully completed template lifecycle", created_guids=created_in_scenario)
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            if isinstance(e, PyegeriaTimeoutException):
                console.print(f"[bold yellow]⚠ Timeout in {scenario_name}; continuing.[/bold yellow]")
                return TestResult(scenario_name, "WARNING", duration, f"Timeout: {e}", error=e, created_guids=created_in_scenario)
            return TestResult(scenario_name, "FAILED", duration, str(e), error=e, created_guids=created_in_scenario)

    def scenario_2_catalog_template_management(self) -> TestResult:
        """Test catalog template management"""
        start_time = time.perf_counter()
        scenario_name = "Catalog Template Management"
        created_in_scenario = []
        
        try:
            # 1. Create a "parent" element (e.g. an Asset)
            qname_asset = self._unique_qname("Asset")
            asset_guid = self.tech.expert.create_metadata_element({
                "class": "NewOpenMetadataElementRequestBody",
                "typeName": "Asset",
                "properties": {
                    "class": "ElementProperties",
                    "propertyValueMap": {
                        "qualifiedName": {"class": "PrimitiveTypePropertyValue", "typeName": "string", "primitiveValue": qname_asset}
                    }
                }
            })
            self.created_elements.append(asset_guid)
            created_in_scenario.append(asset_guid)
            
            # 2. Create a template element
            qname_template = self._unique_qname("CatalogTemplate")
            template_guid = self.tech.expert.create_metadata_element({
                "class": "NewOpenMetadataElementRequestBody",
                "typeName": "Referenceable",
                "properties": {
                    "class": "ElementProperties",
                    "propertyValueMap": {
                        "qualifiedName": {"class": "PrimitiveTypePropertyValue", "typeName": "string", "primitiveValue": qname_template}
                    }
                }
            })
            self.created_elements.append(template_guid)
            created_in_scenario.append(template_guid)
            
            # 3. Link Catalog Template
            self.tech.templates.link_catalog_template(asset_guid, template_guid, {
                "class": "NewRelationshipRequestBody",
                "relationshipProperties": {"class": "CatalogTemplateProperties"}
            })
            console.print(f"  [green]✓[/green] Linked catalog template")
            
            # 4. Detach Catalog Template
            self.tech.templates.detach_catalog_template(asset_guid, template_guid)
            console.print(f"  [green]✓[/green] Detached catalog template")
            
            duration = time.perf_counter() - start_time
            return TestResult(scenario_name, "PASSED", duration, "Successfully managed catalog templates", created_guids=created_in_scenario)
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            if isinstance(e, PyegeriaTimeoutException):
                console.print(f"[bold yellow]⚠ Timeout in {scenario_name}; continuing.[/bold yellow]")
                return TestResult(scenario_name, "WARNING", duration, f"Timeout: {e}", error=e, created_guids=created_in_scenario)
            return TestResult(scenario_name, "FAILED", duration, str(e), error=e, created_guids=created_in_scenario)

    def generate_report(self):
        """Display test results in a nice table"""
        table = Table(title=f"Template Manager Scenario Test Results - {self.test_run_id}")
        table.add_column("Scenario", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Duration (s)", justify="right")
        table.add_column("Message")
        
        for res in self.results:
            status_style = "green" if res.status == "PASSED" else "red"
            table.add_row(
                res.scenario_name,
                f"[{status_style}]{res.status}[/{status_style}]",
                f"{res.duration:.3f}",
                res.message
            )
        
        console.print("\n")
        console.print(table)
        console.print("\n")

    def run_all_scenarios(self):
        """Run all defined scenarios"""
        if not self.setup():
            return
            
        scenarios = [
            self.scenario_1_template_lifecycle,
            self.scenario_2_catalog_template_management,
        ]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Running scenarios...", total=len(scenarios))
            
            for scenario in scenarios:
                progress.update(task, description=f"Running {scenario.__name__}...")
                result = scenario()
                self.results.append(result)
                progress.advance(task)
                
        self.generate_report()
        self.cleanup_created_elements()
        self.teardown()
        
        # Return True if all passed
        return all(r.status == "PASSED" for r in self.results)

def test_template_manager_scenarios():
    """Entry point for pytest"""
    tester = TemplateScenarioTester()
    success = tester.run_all_scenarios()
    assert success, "One or more scenarios failed"

if __name__ == "__main__":
    tester = TemplateScenarioTester()
    success = tester.run_all_scenarios()
    sys.exit(0 if success else 1)
