"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario tests for JacquardDataSets.
"""
import time
from typing import List, Optional
from dataclasses import dataclass

from rich import print as rprint
from rich.console import Console
from rich.table import Table

from examples.jacquard_data_sets import JacquardDataSets
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


class JacquardDataSetsScenarioTester:
    def __init__(self):
        self.client: Optional[JacquardDataSets] = None
        self.results: List[TestResult] = []

    def setup(self) -> bool:
        try:
            self.client = JacquardDataSets(VIEW_SERVER, PLATFORM_URL, USER_ID, USER_PWD)
            self.client.create_egeria_bearer_token(USER_ID, USER_PWD)
            return True
        except Exception:
            return False

    def teardown(self):
        if self.client:
            self.client.close_session()

    def scenario_tabular_data_set_discovery(self) -> TestResult:
        name = "Tabular Data Set Discovery"
        start_time = time.perf_counter()
        try:
            # 1. Find assets by name
            assets = self.client.find_assets_by_name("Valid Metadata Value Set List")
            
            # 2. Find tabular data sets
            datasets = self.client.find_tabular_data_sets()
            
            return TestResult(name, "PASSED", time.perf_counter() - start_time, f"Found {len(assets) if assets else 0} assets and {len(datasets) if datasets else 0} datasets")
        except PyegeriaException as e:
            return TestResult(name, "FAILED", time.perf_counter() - start_time, str(e))
        except Exception as e:
            return TestResult(name, "FAILED", time.perf_counter() - start_time, f"Unexpected error: {e}")

    def run_all_scenarios(self):
        if not self.setup():
            rprint("[bold red]Setup failed, skipping scenarios[/bold red]")
            return
        
        self.results.append(self.scenario_tabular_data_set_discovery())
        self.teardown()
        self.print_results_summary()

    def print_results_summary(self):
        table = Table(title="Jacquard Data Sets Scenario Results")
        table.add_column("Scenario", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Duration (s)", justify="right")
        table.add_column("Message")
        for res in self.results:
            style = "green" if res.status == "PASSED" else "red"
            table.add_row(res.scenario_name, f"[{style}]{res.status}[/{style}]", f"{res.duration:.2f}", res.message)
        console.print(table)


def test_jacquard_data_sets_scenarios():
    tester = JacquardDataSetsScenarioTester()
    tester.run_all_scenarios()


if __name__ == "__main__":
    test_jacquard_data_sets_scenarios()
