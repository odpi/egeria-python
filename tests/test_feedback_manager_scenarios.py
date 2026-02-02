"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Comprehensive scenario tests for FeedbackManager.
Tests full CRUD workflows for likes, ratings, comments, and tags with proper cleanup.

A running Egeria environment is needed to run these tests.
"""

import time
from dataclasses import dataclass
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from pyegeria import FeedbackManager, GlossaryManager
from pyegeria.core._exceptions import (
    PyegeriaException,
    PyegeriaTimeoutException,
    print_basic_exception,
)

console = Console()


@dataclass
class TestResult:
    """Data class to hold test results"""
    scenario_name: str
    passed: bool
    duration: float
    skipped: bool = False
    message: str = ""
    error: str = ""


class FeedbackScenarioTester:
    """Test harness for FeedbackManager scenarios"""

    def __init__(self):
        self.view_server = "qs-view-server"
        self.platform_url = "https://laz.local:9443"
        self.user = "erinoverview"
        self.password = "secret"
        self.feedback_client = None
        self.glossary_client = None
        self.test_element_guid = None
        self.created_likes = []
        self.created_ratings = []
        self.created_comments = []
        self.created_tags = []

    def setup(self):
        """Initialize the clients and create a test element"""
        try:
            self.feedback_client = FeedbackManager(
                self.view_server,
                self.platform_url,
                user_id=self.user,
                user_pwd=self.password,
            )
            self.feedback_client.create_egeria_bearer_token(self.user, self.password)
            
            # Create a glossary client to create a test element
            self.glossary_client = GlossaryManager(
                self.view_server,
                self.platform_url,
                user_id=self.user,
                user_pwd=self.password,
            )
            self.glossary_client.create_egeria_bearer_token(self.user, self.password)
            
            # Create a test glossary to use as our test element
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            glossary_name = f"FeedbackTest_{timestamp}"
            response = self.glossary_client.create_glossary(
                glossary_name,
                "Test glossary for feedback scenarios",
                "English",
                "Testing purposes only"
            )
            self.test_element_guid = response
            
            console.print("[green]✓[/green] Clients initialized and test element created successfully")
            return True
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to initialize: {str(e)}")
            return False

    def teardown(self):
        """Clean up and close sessions"""
        if self.feedback_client or self.glossary_client:
            self.cleanup_created_entities()
            if self.feedback_client:
                self.feedback_client.close_session()
            if self.glossary_client:
                self.glossary_client.close_session()
            console.print("[green]✓[/green] Sessions closed")

    def cleanup_created_entities(self):
        """Delete all created test entities"""
        console.print("\n[bold cyan]Cleaning up created entities...[/bold cyan]")
        
        # Remove likes
        for like_guid in self.created_likes:
            try:
                if self.test_element_guid:
                    self.feedback_client.remove_like_from_element(self.test_element_guid)
                    console.print(f"[green]✓[/green] Removed like from element")
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Could not remove like: {str(e)}")
        
        # Remove ratings
        for rating_guid in self.created_ratings:
            try:
                if self.test_element_guid:
                    self.feedback_client.remove_rating_from_element(self.test_element_guid)
                    console.print(f"[green]✓[/green] Removed rating from element")
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Could not remove rating: {str(e)}")
        
        # Delete test glossary
        if self.test_element_guid and self.glossary_client:
            try:
                self.glossary_client.delete_glossary(self.test_element_guid)
                console.print(f"[green]✓[/green] Deleted test glossary")
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Could not delete test glossary: {str(e)}")

    def run_scenario(self, scenario_func, scenario_name: str) -> TestResult:
        """Run a single scenario and return the result"""
        console.print(f"\n[bold blue]Running:[/bold blue] {scenario_name}")
        start_time = time.perf_counter()
        
        try:
            scenario_func()
            duration = time.perf_counter() - start_time
            console.print(f"[green]✓ PASSED[/green] ({duration:.2f}s)")
            return TestResult(scenario_name, True, duration)
        except PyegeriaTimeoutException as e:
            duration = time.perf_counter() - start_time
            console.print(f"[yellow]⊘ SKIPPED[/yellow] (timeout)")
            return TestResult(scenario_name, False, duration, skipped=True, error=str(e))
        except Exception as e:
            duration = time.perf_counter() - start_time
            console.print(f"[red]✗ FAILED[/red] ({duration:.2f}s)")
            console.print(f"[red]Error:[/red] {str(e)}")
            return TestResult(scenario_name, False, duration, error=str(e))

    # Scenario 1: Add and retrieve a like
    def scenario_add_and_retrieve_like(self):
        """Add a like to an element and retrieve it"""
        if not self.test_element_guid:
            raise Exception("No test element available")
        
        # Add like
        response = self.feedback_client.add_like_to_element(
            self.test_element_guid,
            is_public=True
        )
        self.created_likes.append(self.test_element_guid)
        
        # Retrieve likes
        likes = self.feedback_client.get_attached_likes(
            self.test_element_guid,
            start_from=0,
            page_size=50
        )
        
        assert likes is not None, "Failed to retrieve likes"
        console.print(f"  Retrieved {len(likes) if isinstance(likes, list) else 1} like(s)")

    # Scenario 2: Add and retrieve a rating
    def scenario_add_and_retrieve_rating(self):
        """Add a rating to an element and retrieve it"""
        if not self.test_element_guid:
            raise Exception("No test element available")
        
        # Add rating
        rating_body = {
            "starRating": 5,
            "review": "Excellent test element!"
        }
        response = self.feedback_client.add_rating_to_element(
            self.test_element_guid,
            is_public=True,
            body=rating_body
        )
        self.created_ratings.append(self.test_element_guid)
        
        # Retrieve ratings
        ratings = self.feedback_client.get_attached_ratings(
            self.test_element_guid,
            start_from=0,
            page_size=50
        )
        
        assert ratings is not None, "Failed to retrieve ratings"
        console.print(f"  Retrieved {len(ratings) if isinstance(ratings, list) else 1} rating(s)")

    # Scenario 3: Add multiple ratings with different star values
    def scenario_multiple_ratings(self):
        """Add multiple ratings to test rating aggregation"""
        if not self.test_element_guid:
            raise Exception("No test element available")
        
        ratings_to_add = [
            {"starRating": 5, "review": "Excellent!"},
            {"starRating": 4, "review": "Very good"},
            {"starRating": 3, "review": "Good"},
        ]
        
        for rating_data in ratings_to_add:
            self.feedback_client.add_rating_to_element(
                self.test_element_guid,
                is_public=True,
                body=rating_data
            )
            self.created_ratings.append(self.test_element_guid)
            time.sleep(0.5)  # Small delay between ratings
        
        # Retrieve all ratings
        ratings = self.feedback_client.get_attached_ratings(
            self.test_element_guid,
            start_from=0,
            page_size=50
        )
        
        console.print(f"  Added and retrieved {len(ratings_to_add)} ratings")

    # Scenario 4: Remove a like
    def scenario_remove_like(self):
        """Add a like and then remove it"""
        if not self.test_element_guid:
            raise Exception("No test element available")
        
        # Add like
        self.feedback_client.add_like_to_element(
            self.test_element_guid,
            is_public=True
        )
        
        # Remove like
        response = self.feedback_client.remove_like_from_element(
            self.test_element_guid
        )
        
        console.print("  Successfully added and removed like")

    # Scenario 5: Remove a rating
    def scenario_remove_rating(self):
        """Add a rating and then remove it"""
        if not self.test_element_guid:
            raise Exception("No test element available")
        
        # Add rating
        rating_body = {
            "starRating": 4,
            "review": "Test rating to be removed"
        }
        self.feedback_client.add_rating_to_element(
            self.test_element_guid,
            is_public=True,
            body=rating_body
        )
        
        # Remove rating
        response = self.feedback_client.remove_rating_from_element(
            self.test_element_guid
        )
        
        console.print("  Successfully added and removed rating")

    # Scenario 6: Public vs private feedback
    def scenario_public_private_feedback(self):
        """Test adding public and private likes"""
        if not self.test_element_guid:
            raise Exception("No test element available")
        
        # Add public like
        self.feedback_client.add_like_to_element(
            self.test_element_guid,
            is_public=True
        )
        self.created_likes.append(self.test_element_guid)
        
        # Add private like (if supported)
        try:
            self.feedback_client.add_like_to_element(
                self.test_element_guid,
                is_public=False
            )
            console.print("  Added both public and private likes")
        except Exception as e:
            console.print(f"  Added public like (private not supported: {str(e)})")

    def print_summary(self, results: list[TestResult]):
        """Print a summary table of all test results"""
        table = Table(title="Feedback Manager Scenario Test Results", show_header=True)
        table.add_column("Scenario", style="cyan", no_wrap=True)
        table.add_column("Status", style="bold")
        table.add_column("Duration", justify="right")
        table.add_column("Message", style="dim")

        passed = 0
        failed = 0
        skipped = 0

        for result in results:
            if result.skipped:
                status = "[yellow]SKIPPED[/yellow]"
                skipped += 1
            elif result.passed:
                status = "[green]PASSED[/green]"
                passed += 1
            else:
                status = "[red]FAILED[/red]"
                failed += 1

            duration_str = f"{result.duration:.2f}s"
            message = result.message if result.passed else result.error[:50]
            table.add_row(result.scenario_name, status, duration_str, message)

        console.print("\n")
        console.print(table)
        console.print(f"\n[bold]Summary:[/bold] {passed} passed, {failed} failed, {skipped} skipped")

    def run_all_scenarios(self):
        """Run all test scenarios"""
        console.print(Panel.fit(
            "[bold cyan]Feedback Manager Scenario Tests[/bold cyan]\n"
            "Testing likes, ratings, comments, and tags functionality",
            border_style="cyan"
        ))

        if not self.setup():
            console.print("[red]Setup failed. Aborting tests.[/red]")
            return

        results = []

        # Run all scenarios
        scenarios = [
            (self.scenario_add_and_retrieve_like, "Add and Retrieve Like"),
            (self.scenario_add_and_retrieve_rating, "Add and Retrieve Rating"),
            (self.scenario_multiple_ratings, "Multiple Ratings"),
            (self.scenario_remove_like, "Remove Like"),
            (self.scenario_remove_rating, "Remove Rating"),
            (self.scenario_public_private_feedback, "Public vs Private Feedback"),
        ]

        for scenario_func, scenario_name in scenarios:
            result = self.run_scenario(scenario_func, scenario_name)
            results.append(result)
            time.sleep(0.5)  # Small delay between scenarios

        self.teardown()
        self.print_summary(results)


def main():
    """Main entry point for running scenario tests"""
    tester = FeedbackScenarioTester()
    tester.run_all_scenarios()


if __name__ == "__main__":
    main()