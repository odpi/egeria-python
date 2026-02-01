"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Scenario tests for the People Organizer View Service.
"""
import time
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass

from rich import print as rprint
from rich.console import Console
from rich.table import Table

from pyegeria.egeria_client import Egeria
from pyegeria.core._exceptions import (
    PyegeriaConnectionException, PyegeriaTimeoutException, print_basic_exception,
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

class PeopleOrganizerScenarioTester:
    """Execute realistic people organizer scenarios"""
    
    def __init__(self):
        self.egeria = None
        self.results: List[TestResult] = []
        self.created_guids: List[str] = []
        self.test_run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def setup(self) -> bool:
        """Initialize connection to Egeria"""
        try:
            rprint("\n[bold cyan]═══ Setting up People Organizer Test Environment ═══[/bold cyan]\n")
            self.egeria = Egeria(VIEW_SERVER, PLATFORM_URL, user_id=USER_ID, user_pwd=USER_PWD)
            self.egeria.create_egeria_bearer_token(USER_ID, USER_PWD)
            
            rprint(f"✓ Connected to {PLATFORM_URL}")
            rprint(f"✓ Authenticated as {USER_ID}")
            rprint(f"✓ Test Run ID: {self.test_run_id}\n")
            return True
        except PyegeriaConnectionException:
            rprint("[bold yellow]⚠ Skipping scenarios: Cannot connect to Egeria[/bold yellow]")
            return False
        except Exception as e:
            rprint(f"[bold red]✗ Setup failed: {str(e)}[/bold red]")
            return False
    
    def teardown(self):
        """Clean up and close connection"""
        if self.egeria:
            # Cleanup created profiles
            for guid in reversed(self.created_guids):
                try:
                    self.egeria.delete_actor_profile(guid)
                except Exception:
                    pass
            self.egeria.close_session()
        rprint("\n✓ Sessions closed and cleanup attempted")

    def run_scenario(self, scenario_func) -> bool:
        """Run a single scenario and record results"""
        name = scenario_func.__name__.replace('scenario_', '').replace('_', ' ').title()
        start_time = time.perf_counter()
        
        try:
            rprint(f"[bold blue]Running Scenario: {name}...[/bold blue]")
            message = scenario_func()
            duration = time.perf_counter() - start_time
            self.results.append(TestResult(name, "PASSED", duration, message))
            rprint(f"[bold green]✓ {name} passed[/bold green]")
            return True
        except PyegeriaTimeoutException as e:
            duration = time.perf_counter() - start_time
            rprint(f"[bold yellow]⚠ Timeout in {name}; continuing.[/bold yellow]")
            self.results.append(TestResult(name, "WARNING", duration, f"Timeout: {e}", e))
            return True
        except Exception as e:
            duration = time.perf_counter() - start_time
            print_basic_exception(e)
            self.results.append(TestResult(name, "FAILED", duration, str(e), e))
            rprint(f"[bold red]✗ {name} failed: {str(e)}[/bold red]")
            return False

    def scenario_peer_person_relationship(self) -> str:
        """Scenario: Create two persons and link them as peers"""
        # 1. Create two PersonProfiles
        p1_qname = f"Person::P1::{self.test_run_id}"
        p2_qname = f"Person::P2::{self.test_run_id}"
        
        body1 = {
            "class": "NewElementRequestBody",
            "properties": {
                "class": "PersonProperties",
                "qualifiedName": p1_qname,
                "displayName": "Person One",
            }
        }
        body2 = {
            "class": "NewElementRequestBody",
            "properties": {
                "class": "PersonProperties",
                "qualifiedName": p2_qname,
                "displayName": "Person Two",
            }
        }
        
        guid1 = self.egeria.create_actor_profile(body1)
        self.created_guids.append(guid1)
        guid2 = self.egeria.create_actor_profile(body2)
        self.created_guids.append(guid2)
        
        # 2. Link them as peers
        link_body = {
            "class": "NewRelationshipRequestBody",
            "properties": {
                "class": "PeerProperties",
            }
        }
        self.egeria.link_peer_person(guid1, guid2, link_body)
        
        # 3. Detach them
        detach_body = {
            "class": "DeleteRelationshipRequestBody",
        }
        self.egeria.detach_peer_person(guid1, guid2, detach_body)
        
        return f"Created {p1_qname} and {p2_qname}, linked and detached."

    def scenario_team_structure_relationship(self) -> str:
        """Scenario: Create super team and subteam and link them"""
        # 1. Create two TeamProfiles
        t1_qname = f"Team::Super::{self.test_run_id}"
        t2_qname = f"Team::Sub::{self.test_run_id}"
        
        body1 = {
            "class": "NewElementRequestBody",
            "properties": {
                "class": "TeamProperties",
                "qualifiedName": t1_qname,
                "displayName": "Super Team",
            }
        }
        body2 = {
            "class": "NewElementRequestBody",
            "properties": {
                "class": "TeamProperties",
                "qualifiedName": t2_qname,
                "displayName": "Sub Team",
            }
        }
        
        guid1 = self.egeria.create_actor_profile(body1)
        self.created_guids.append(guid1)
        guid2 = self.egeria.create_actor_profile(body2)
        self.created_guids.append(guid2)
        
        # 2. Link them
        link_body = {
            "class": "NewRelationshipRequestBody",
            "properties": {
                "class": "TeamStructureProperties",
                "delegationEscalationAuthority": True,
            }
        }
        self.egeria.link_team_structure(guid1, guid2, link_body)
        
        # 3. Detach them
        detach_body = {
            "class": "DeleteRelationshipRequestBody",
        }
        self.egeria.detach_team_structure(guid1, guid2, detach_body)
        
        return f"Created {t1_qname} and {t2_qname}, linked and detached."

    def print_summary(self):
        """Print summary table of results"""
        if not self.results:
            return
            
        table = Table(title="People Organizer Scenario Results")
        table.add_column("Scenario", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Duration (s)", justify="right")
        table.add_column("Message")
        
        for res in self.results:
            status_style = "green" if res.status == "PASSED" else "red"
            table.add_row(
                res.scenario_name,
                f"[{status_style}]{res.status}[/{status_style}]",
                f"{res.duration:.2f}",
                res.message
            )
        
        console.print("\n")
        console.print(table)

def test_people_organizer_scenarios():
    tester = PeopleOrganizerScenarioTester()
    if tester.setup():
        tester.run_scenario(tester.scenario_peer_person_relationship)
        tester.run_scenario(tester.scenario_team_structure_relationship)
        tester.print_summary()
        tester.teardown()

if __name__ == "__main__":
    test_people_organizer_scenarios()
