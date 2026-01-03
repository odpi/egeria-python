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
import traceback
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field

from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from loguru import logger

from pyegeria.template_manager_omvs import TemplateManager
from pyegeria._exceptions import (
    PyegeriaException,
    PyegeriaNotFoundException,
    print_exception_table, PyegeriaAPIException,
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
    """Execute realistic template management scenarios"""
    
    def __init__(self):
        self.client: Optional[TemplateManager] = None
        self.results: List[TestResult] = []
        self.created_elements: List[str] = []
        self.test_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def setup(self) -> bool:
        """Initialize connection to Egeria"""
        try:
            console.print("\n[bold cyan]═══ Setting up Template Manager Test Environment ═══[/bold cyan]\n")
            self.client = TemplateManager(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
            self.client.create_egeria_bearer_token(USER_ID, USER_PWD)
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
        """Delete all elements created during testing"""
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
                    self.client.delete_metadata_element_in_store(
                        guid, 
                        {"class": "DeleteElementRequestBody"}
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
        """Test the lifecycle of a template element"""
        start_time = time.perf_counter()
        scenario_name = "Template Lifecycle"
        created_in_scenario = []
        
        try:
            # 1. Create a metadata element that will serve as a template
            qname = self._unique_qname("Template_Lifecycle")
            body = {
                "class": "NewOpenMetadataElementRequestBody",
                "typeName": "Referenceable",
                "properties": {
                    "class": "ReferenceableProperties",
                    "qualifiedName": qname,
                    "description": "Template for lifecycle testing"
                }
            }
            
            guid = self.client.create_metadata_element_in_store(body)
            self.created_elements.append(guid)
            created_in_scenario.append(guid)
            
            # 2. Classify it as a template
            classify_body = {
                "class": "ClassificationRequestBody",
                "properties": {
                    "class": "ClassificationProperties",
                }
            }
            self.client.classify_metadata_element_in_store(guid, "Template", classify_body)
            
            # 3. Update the template
            update_body = {
                "class": "UpdateOpenMetadataElementRequestBody",
                "properties": {
                    "class": "ReferenceableProperties",
                    "qualifiedName": qname,
                    "description": "Updated template description"
                }
            }
            self.client.update_metadata_element_in_store(guid, update_body)
            
            # 4. Use it to create another element from template
            new_qname = self._unique_qname("From_Template")
            from_template_body = {
                "class": "TemplateRequestBody",
                "templateGUID": guid,
                "replacementProperties": {
                    "class": "ReferenceableProperties",
                    "qualifiedName": new_qname
                }
            }
            new_guid = self.client.create_metadata_element_from_template(from_template_body)
            self.created_elements.append(new_guid)
            created_in_scenario.append(new_guid)
            
            duration = time.perf_counter() - start_time
            return TestResult(scenario_name, "PASSED", duration, "Successfully completed template lifecycle", created_guids=created_in_scenario)
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(scenario_name, "FAILED", duration, str(e), error=e, created_guids=created_in_scenario)

    def scenario_2_template_classification_management(self) -> TestResult:
        """Test management of classifications on template elements"""
        start_time = time.perf_counter()
        scenario_name = "Template Classification Management"
        created_in_scenario = []
        
        try:
            # 1. Create element
            qname = self._unique_qname("Template_Class")
            guid = self.client.create_metadata_element_in_store({
                "class": "NewOpenMetadataElementRequestBody",
                "typeName": "Referenceable",
                "properties": {"class": "ReferenceableProperties", "qualifiedName": qname}
            })
            self.created_elements.append(guid)
            created_in_scenario.append(guid)
            
            # 2. Add classification
            self.client.classify_metadata_element_in_store(guid, "SubjectArea", {
                "class": "ClassificationRequestBody",
                "properties": {"class": "SubjectAreaClassificationProperties", "name": "TestArea"}
            })
            
            # 3. Update classification
            self.client.reclassify_metadata_element_in_store(guid, "SubjectArea", {
                "class": "ClassificationRequestBody",
                "properties": {"class": "SubjectAreaClassificationProperties", "name": "UpdatedArea"}
            })
            
            # 4. Remove classification
            self.client.declassify_metadata_element_in_store(guid, "SubjectArea", {"class": "ClassificationRequestBody"})
            
            duration = time.perf_counter() - start_time
            return TestResult(scenario_name, "PASSED", duration, "Successfully managed classifications", created_guids=created_in_scenario)
            
        except Exception as e:
            duration = time.perf_counter() - start_time
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
            self.scenario_2_template_classification_management,
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
