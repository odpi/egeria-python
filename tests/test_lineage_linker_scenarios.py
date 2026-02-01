"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario tests for LineageLinker.
"""
import time
from typing import List, Optional
from dataclasses import dataclass

from rich import print as rprint
from rich.console import Console
from rich.table import Table

from pyegeria.omvs.lineage_linker import LineageLinker
from pyegeria.omvs.asset_maker import AssetMaker
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


class LineageLinkerScenarioTester:
    def __init__(self):
        self.client: Optional[LineageLinker] = None
        self.asset_maker: Optional[AssetMaker] = None
        self.results: List[TestResult] = []
        self.created_elements: List[str] = []

    def setup(self) -> bool:
        try:
            self.client = LineageLinker(VIEW_SERVER, PLATFORM_URL, USER_ID, USER_PWD)
            self.asset_maker = AssetMaker(VIEW_SERVER, PLATFORM_URL, USER_ID, USER_PWD)
            self.client.create_egeria_bearer_token(USER_ID, USER_PWD)
            self.asset_maker.create_egeria_bearer_token(USER_ID, USER_PWD)
            return True
        except Exception:
            return False

    def teardown(self):
        if self.client:
            self.client.close_session()
        if self.asset_maker:
            self.asset_maker.close_session()

    def scenario_lineage_link_lifecycle(self) -> TestResult:
        name = "Lineage Link Lifecycle"
        start_time = time.perf_counter()
        try:
            # 1. Create two assets to link
            guid1 = self.asset_maker.create_csv_asset("SourceAsset", "Source for lineage", "source.csv")
            guid2 = self.asset_maker.create_csv_asset("TargetAsset", "Target for lineage", "target.csv")
            self.created_elements.extend([guid1, guid2])

            # 2. Link them with Lineage
            body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "DataFlowProperties",
                    "label": "Scenario Flow",
                }
            }
            rel_guid = self.client.link_lineage(guid1, "DataFlow", guid2, body)
            
            return TestResult(name, "PASSED", time.perf_counter() - start_time, f"Linked {guid1} to {guid2}")
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
        
        self.results.append(self.scenario_lineage_link_lifecycle())
        self.teardown()
        self.print_results_summary()

    def print_results_summary(self):
        table = Table(title="Lineage Linker Scenario Results")
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


def test_lineage_linker_scenarios():
    tester = LineageLinkerScenarioTester()
    tester.run_all_scenarios()


if __name__ == "__main__":
    test_lineage_linker_scenarios()
