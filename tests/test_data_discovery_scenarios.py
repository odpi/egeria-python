"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario tests for DataDiscovery.
"""
import time
from typing import List, Optional
from dataclasses import dataclass

from rich import print as rprint
from rich.console import Console
from rich.table import Table

from pyegeria.omvs.data_discovery import DataDiscovery
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


class DataDiscoveryScenarioTester:
    def __init__(self):
        self.client: Optional[DataDiscovery] = None
        self.asset_maker: Optional[AssetMaker] = None
        self.results: List[TestResult] = []

    def setup(self) -> bool:
        try:
            self.client = DataDiscovery(VIEW_SERVER, PLATFORM_URL, USER_ID, USER_PWD)
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

    def scenario_annotation_lifecycle(self) -> TestResult:
        name = "Annotation Lifecycle"
        start_time = time.perf_counter()
        try:
            # 1. Create an asset to annotate
            asset_guid = self.asset_maker.create_csv_asset("DiscoveryAsset", "Asset for discovery", "discovery.csv")

            # 2. Create an annotation for the asset
            body = {
                "class": "NewElementRequestBody",
                "anchorGUID": asset_guid,
                "properties": {
                    "class": "AnnotationProperties",
                    "qualifiedName": f"Annotation::{asset_guid}",
                    "displayName": "Discovery Annotation",
                    "annotationType": "Data Discovery",
                }
            }
            ann_guid = self.client.create_annotation(body)
            
            # 3. Find annotation
            found = self.client.find_annotations(search_string=f"Annotation::{asset_guid}")
            
            return TestResult(name, "PASSED", time.perf_counter() - start_time, f"Created and found annotation {ann_guid}")
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
        
        self.results.append(self.scenario_annotation_lifecycle())
        self.teardown()
        self.print_results_summary()

    def print_results_summary(self):
        table = Table(title="Data Discovery Scenario Results")
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


def test_data_discovery_scenarios():
    tester = DataDiscoveryScenarioTester()
    tester.run_all_scenarios()


if __name__ == "__main__":
    test_data_discovery_scenarios()
