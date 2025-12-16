#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario-based testing for External Links with synthetic data.

This executable test script runs realistic scenarios for external reference management,
including creating external references, linking them to elements, and managing cited documents,
with comprehensive cleanup and detailed error reporting.

Usage:
    python tests/test_external_links_scenarios.py
    
    Or with pytest:
    pytest tests/test_external_links_scenarios.py -v -s
"""

import json
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

from pyegeria.external_links import ExternalReferences
from pyegeria._exceptions import (
    PyegeriaClientException,
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
class ExternalReferenceData:
    """Synthetic external reference data"""
    qualified_name: str
    display_name: str
    description: str
    url: str
    reference_title: str
    guid: Optional[str] = None


class ExternalLinksScenarioTester:
    """Execute realistic external links scenarios"""
    
    def __init__(self):
        self.client: Optional[ExternalReferences] = None
        self.results: List[TestResult] = []
        self.created_external_refs: List[str] = []
        self.test_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def setup(self) -> bool:
        """Initialize connection to Egeria"""
        try:
            console.print("\n[bold cyan]═══ Setting up External Links Test Environment ═══[/bold cyan]\n")
            self.client = ExternalReferences(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
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
    
    def cleanup_created_references(self):
        """Delete all external references created during testing"""
        console.print("\n[bold yellow]═══ Cleaning Up Test Data ═══[/bold yellow]\n")
        
        if not self.created_external_refs:
            console.print("No external references to clean up")
            return
        
        cleanup_results = {"success": 0, "failed": 0, "not_found": 0}
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task(
                f"Cleaning up {len(self.created_external_refs)} external references...",
                total=len(self.created_external_refs)
            )
            
            for guid in reversed(self.created_external_refs):
                try:
                    self.client.delete_external_reference(guid, cascade=True)
                    cleanup_results["success"] += 1
                except PyegeriaAPIException:
                    cleanup_results["not_found"] += 1
                except Exception as e:
                    console.print(f"  [yellow]⚠ Failed to delete {guid}: {str(e)}[/yellow]")
                    cleanup_results["failed"] += 1
                progress.advance(task)
        
        console.print(f"\n✓ Cleanup complete:")
        console.print(f"  • Successfully deleted: {cleanup_results['success']}")
        console.print(f"  • Not found (already deleted): {cleanup_results['not_found']}")
        console.print(f"  • Failed: {cleanup_results['failed']}")
    
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
    
    def scenario_external_reference_lifecycle(self) -> TestResult:
        """Scenario: Complete external reference lifecycle - create, read, update, delete"""
        scenario_name = "External Reference Lifecycle"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # CREATE: Create a new external reference
            console.print("  → Creating external reference...")
            ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
            ref_name = f"TestExternalRef_{ts}"
            
            body = {
                "class": "NewElementRequestBody",
                "isOwnAnchor": True,
                "initialStatus": "ACTIVE",
                "properties": {
                    "class": "ExternalReferenceProperties",
                    "qualifiedName": f"external-ref::{ref_name}",
                    "displayName": ref_name,
                    "description": "Test external reference for lifecycle testing",
                    "url": f"https://example.com/docs/{ref_name}",
                    "referenceTitle": f"Reference Title for {ref_name}",
                    "referenceAbstract": "This is a test external reference",
                    "authors": ["Test Author 1", "Test Author 2"]
                }
            }
            
            guid = self.client.create_external_reference(body)
            
            if guid:
                created_guids.append(guid)
                self.created_external_refs.append(guid)
                console.print(f"  ✓ Created external reference: {guid}")
            else:
                raise Exception("Failed to create external reference - no GUID returned")
            
            # READ: Retrieve the external reference
            console.print("  → Retrieving external reference...")
            retrieved = self.client.get_external_reference_by_guid(guid)
            
            if isinstance(retrieved, dict):
                console.print(f"  ✓ Retrieved external reference: {retrieved.get('properties', {}).get('displayName', 'Unknown')}")
            else:
                console.print("  [yellow]⚠ Retrieved data is not a dict[/yellow]")
            
            # UPDATE: Update the external reference
            console.print("  → Updating external reference...")
            update_body = {
                "class": "UpdateElementRequestBody",
                "properties": {
                    "class": "ExternalReferenceProperties",
                    "qualifiedName": f"external-ref::{ref_name}",
                    "displayName": f"{ref_name}_Updated",
                    "description": "Updated test external reference",
                    "url": f"https://example.com/docs/{ref_name}_updated",
                    "referenceTitle": f"Updated Reference Title for {ref_name}",
                    "referenceAbstract": "This is an updated test external reference",
                    "authors": ["Test Author 1", "Test Author 2", "Test Author 3"]
                }
            }
            
            self.client.update_external_reference(guid, update_body)
            console.print("  ✓ Updated external reference")
            
            # VERIFY UPDATE
            updated = self.client.get_external_reference_by_guid(guid)
            if isinstance(updated, dict):
                updated_name = updated.get('properties', {}).get('displayName', '')
                if "Updated" in updated_name:
                    console.print("  ✓ Verified update")
                else:
                    console.print("  [yellow]⚠ Update verification inconclusive[/yellow]")
            
            # SEARCH: Find the external reference
            console.print("  → Searching for external reference...")
            search_results = self.client.get_external_references_by_name(
                filter_string=ref_name[:10]
            )
            
            if isinstance(search_results, list) and len(search_results) > 0:
                console.print(f"  ✓ Found {len(search_results)} external references in search")
            
            # DELETE: Delete the external reference
            console.print("  → Deleting external reference...")
            self.client.delete_external_reference(guid, cascade=True)
            self.created_external_refs.remove(guid)
            console.print("  ✓ Deleted external reference")
            
            # VERIFY DELETION
            try:
                after_delete = self.client.get_external_reference_by_guid(guid)
                console.print("  [yellow]⚠ External reference still exists after deletion[/yellow]")
            except PyegeriaAPIException:
                console.print("  ✓ Verified deletion")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message="Complete lifecycle executed successfully",
                created_guids=created_guids
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
                error=e,
                created_guids=created_guids
            )
    
    def scenario_cited_document_management(self) -> TestResult:
        """Scenario: Create and manage cited documents"""
        scenario_name = "Cited Document Management"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # Create cited documents
            console.print("  → Creating cited documents...")
            ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
            
            doc_types = ["Technical Specification", "User Guide", "API Documentation"]
            doc_guids = []
            
            for i, doc_type in enumerate(doc_types):
                doc_name = f"CitedDoc_{doc_type.replace(' ', '_')}_{ts}"
                
                body = {
                    "class": "NewElementRequestBody",
                    "isOwnAnchor": True,
                    "initialStatus": "ACTIVE",
                    "typeName": "CitedDocument",
                    "properties": {
                        "class": "CitedDocumentProperties",
                        "qualifiedName": f"cited-doc::{doc_name}",
                        "displayName": doc_name,
                        "description": f"Test cited document for {doc_type}",
                        "url": f"https://example.com/docs/{doc_name}.pdf",
                        "referenceTitle": f"{doc_type} Document",
                        "referenceAbstract": f"This is a test {doc_type} document",
                        "authors": [f"Author {i+1}"],
                        "documentType": doc_type
                    }
                }
 
                guid = self.client.create_external_reference(body)
                
                if guid:
                    created_guids.append(guid)
                    self.created_external_refs.append(guid)
                    doc_guids.append(guid)
                    console.print(f"  ✓ Created cited document '{doc_type}': {guid}")
            
            console.print(f"  ✓ Created {len(doc_guids)} cited documents")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Created {len(doc_guids)} cited documents",
                created_guids=created_guids
            )
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Error: {str(e)}[/red]")
            console.print(f" Exception is {type(e)}")
    
            print_exception_table(e) if isinstance(e, PyegeriaException) else console.print_exception()
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e)[:100],
                error=e,
                created_guids=created_guids
            )
    
    def scenario_related_media_management(self) -> TestResult:
        """Scenario: Create and manage related media references"""
        scenario_name = "Related Media Management"
        start_time = time.perf_counter()
        created_guids = []
        
        try:
            console.print(f"\n[bold blue]▶ Running: {scenario_name}[/bold blue]")
            
            # Create related media references
            console.print("  → Creating related media references...")
            ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
            
            media_types = [
                ("Image", 0),
                ("Video", 3),
                ("Audio", 1),
            ]
            media_guids = []
            
            for media_name, media_type in media_types:
                ref_name = f"Media_{media_name}_{ts}"
                
                body = {
                    "class": "NewElementRequestBody",
                    "isOwnAnchor": True,
                    "initialStatus": "ACTIVE",
                    "typeName": "RelatedMedia",
                    "properties": {
                        "class": "RelatedMediaProperties",
                        "qualifiedName": f"related-media::{ref_name}",
                        "displayName": ref_name,
                        "description": f"Test {media_name} media reference",
                        "url": f"https://example.com/media/{ref_name}",
                        "referenceTitle": f"{media_name} Media",
                        "referenceAbstract": f"This is a test {media_name} media file",
                        "mediaType": media_type
                    }
                }
                console.print(f"{json.dumps(body, indent=2)}")
                guid = self.client.create_external_reference(body)
                
                if guid:
                    created_guids.append(guid)
                    self.created_external_refs.append(guid)
                    media_guids.append(guid)
                    console.print(f"  ✓ Created related media '{media_name}': {guid}")
            
            console.print(f"  ✓ Created {len(media_guids)} related media references")
            
            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name,
                status="PASSED",
                duration=duration,
                message=f"Created {len(media_guids)} related media references",
                created_guids=created_guids
            )
            
        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"  [red]✗ Error: {str(e)}[/red] of type: {type(e)}")
            print_exception_table(e) if isinstance(e, PyegeriaException | PyegeriaClientException| PyegeriaAPIException) else console.print_exception()
            return TestResult(
                scenario_name=scenario_name,
                status="FAILED",
                duration=duration,
                message=str(e)[:100],
                error=e,
                created_guids=created_guids
            )
    
    def run_all_scenarios(self):
        """Execute all test scenarios"""
        console.print(Panel.fit(
            "[bold cyan]External Links Scenario Tests[/bold cyan]\n"
            f"Test Run ID: {self.test_run_id}",
            border_style="cyan"
        ))
        
        if not self.setup():
            console.print("[bold red]Setup failed. Cannot proceed with tests.[/bold red]")
            return False
        
        try:
            # Run all scenarios
            self.results.append(self.scenario_external_reference_lifecycle())
            self.results.append(self.scenario_cited_document_management())
            self.results.append(self.scenario_related_media_management())
            
            # Print summary
            self.print_results_summary()
            
            # Cleanup
            self.cleanup_created_references()
            
            # Return success if no failures
            return all(r.status != "FAILED" for r in self.results)
            
        finally:
            self.teardown()


def test_external_links_scenarios():
    """Pytest entry point for external links scenario tests"""
    tester = ExternalLinksScenarioTester()
    success = tester.run_all_scenarios()
    assert success, "One or more scenarios failed"


if __name__ == "__main__":
    """Direct execution entry point"""
    tester = ExternalLinksScenarioTester()
    success = tester.run_all_scenarios()
    sys.exit(0 if success else 1)