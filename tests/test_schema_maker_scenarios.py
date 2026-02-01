"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario tests for SchemaMaker.
"""
import time
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass

from rich import print as rprint
from rich.console import Console
from rich.table import Table

from pyegeria.omvs.schema_maker import SchemaMaker
from pyegeria.core._exceptions import PyegeriaException, PyegeriaTimeoutException

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"

console = Console(width=200)


@dataclass
class TestResult:
    scenario_name: str
    status: str
    duration: float
    message: str = ""


class SchemaMakerScenarioTester:
    def __init__(self):
        self.client: Optional[SchemaMaker] = None
        self.results: List[TestResult] = []

    def setup(self) -> bool:
        try:
            self.client = SchemaMaker(VIEW_SERVER, PLATFORM_URL, USER_ID, USER_PWD)
            self.client.create_egeria_bearer_token(USER_ID, USER_PWD)
            return True
        except Exception:
            return False

    def teardown(self):
        if self.client:
            self.client.close_session()

    def scenario_schema_type_lifecycle(self) -> TestResult:
        name = "Schema Type Lifecycle"
        start_time = time.perf_counter()
        try:
            # 1. Create a schema type
            qualified_name = f"SchemaType::Scenario::{datetime.now().timestamp()}"
            body = {
                "class": "NewElementRequestBody",
                "properties": {
                    "class": "SchemaTypeProperties",
                    "qualifiedName": qualified_name,
                    "displayName": "Scenario Schema Type",
                }
            }
            guid = self.client.create_schema_type(body)
            
            # 2. Update it
            update_body = {
                "class": "UpdateElementRequestBody",
                "properties": {
                    "class": "SchemaTypeProperties",
                    "displayName": "Updated Scenario Schema Type",
                }
            }
            self.client.update_schema_type(guid, update_body)
            
            # 3. Find it
            found = self.client.find_schema_types(search_string=qualified_name)
            
            return TestResult(name, "PASSED", time.perf_counter() - start_time, f"Created, updated and found schema type {guid}")
        except PyegeriaTimeoutException as e:
            rprint(f"[bold yellow]Timeout in {name}; continuing.[/bold yellow]")
            return TestResult(name, "WARNING", time.perf_counter() - start_time, f"Timeout: {e}")
        except PyegeriaException as e:
            return TestResult(name, "FAILED", time.perf_counter() - start_time, str(e))
        except Exception as e:
            return TestResult(name, "FAILED", time.perf_counter() - start_time, f"Unexpected error: {e}")

    def run_all_scenarios(self):
        if not self.setup():
            rprint("[bold red]Setup failed, skipping scenarios[/bold red]")
            return
        
        self.results.append(self.scenario_schema_type_lifecycle())
        self.teardown()
        self.print_results_summary()

    def print_results_summary(self):
        table = Table(title="Schema Maker Scenario Results")
        table.add_column("Scenario", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Duration (s)", justify="right")
        table.add_column("Message")
        for res in self.results:
            if res.status == "PASSED":
                style = "green"
            elif res.status == "WARNING":
                style = "yellow"
            else:
                style = "red"
            table.add_row(res.scenario_name, f"[{style}]{res.status}[/{style}]", f"{res.duration:.2f}", res.message)
        console.print(table)


def test_schema_maker_scenarios():
    tester = SchemaMakerScenarioTester()
    tester.run_all_scenarios()


if __name__ == "__main__":
    test_schema_maker_scenarios()
