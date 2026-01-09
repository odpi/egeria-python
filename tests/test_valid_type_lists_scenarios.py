"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario tests for ValidTypeLists.
"""
import time
from typing import List, Optional
from dataclasses import dataclass

from rich import print as rprint
from rich.console import Console
from rich.table import Table

from pyegeria.omvs.valid_type_lists import ValidTypeLists
from pyegeria.core._exceptions import PyegeriaException

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


class ValidTypeListsScenarioTester:
    def __init__(self):
        self.client: Optional[ValidTypeLists] = None
        self.results: List[TestResult] = []

    def setup(self) -> bool:
        try:
            self.client = ValidTypeLists(VIEW_SERVER, PLATFORM_URL, USER_ID, USER_PWD)
            self.client.create_egeria_bearer_token(USER_ID, USER_PWD)
            return True
        except Exception:
            return False

    def teardown(self):
        if self.client:
            self.client.close_session()

    def scenario_metadata_type_discovery(self) -> TestResult:
        name = "Metadata Type Discovery"
        start_time = time.perf_counter()
        try:
            # 1. Get all entity types
            types = self.client.get_all_entity_types()
            
            # 2. Get sub types
            subtypes = self.client.get_sub_types("Asset")
            
            return TestResult(name, "PASSED", time.perf_counter() - start_time, f"Retrieved {len(types) if types else 0} entity types and {len(subtypes) if subtypes else 0} subtypes for Asset")
        except PyegeriaException as e:
            return TestResult(name, "FAILED", time.perf_counter() - start_time, str(e))
        except Exception as e:
            return TestResult(name, "FAILED", time.perf_counter() - start_time, f"Unexpected error: {e}")

    def run_all_scenarios(self):
        if not self.setup():
            rprint("[bold red]Setup failed, skipping scenarios[/bold red]")
            return
        
        self.results.append(self.scenario_metadata_type_discovery())
        self.teardown()
        self.print_results_summary()

    def print_results_summary(self):
        table = Table(title="Valid Type Lists Scenario Results")
        table.add_column("Scenario", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Duration (s)", justify="right")
        table.add_column("Message")
        for res in self.results:
            style = "green" if res.status == "PASSED" else "red"
            table.add_row(res.scenario_name, f"[{style}]{res.status}[/{style}]", f"{res.duration:.2f}", res.message)
        console.print(table)


def test_valid_type_lists_scenarios():
    tester = ValidTypeListsScenarioTester()
    tester.run_all_scenarios()


if __name__ == "__main__":
    test_valid_type_lists_scenarios()
