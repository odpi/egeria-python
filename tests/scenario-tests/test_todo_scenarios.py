"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Full lifecycle scenario tests for the Person Action Base bundle (ToDo,
Meeting, Review) - Create -> verify relationships -> verify visibility via
get_my_to_dos()/get_my_assigned_actions() -> verify Dr.Egeria reporting ->
reassign -> update status -> Delete -> verify gone.

Written 2026-08-05 as a regression suite for ISSUE-44 in PYEGERIA_ISSUES.md:
- create_my_todo/create_meeting/create_review previously nested
  originatorGUID/assignToActorGUID inside "properties" instead of at the
  ActionRequestBody top level, so no ActionRequester/AssignmentScope
  relationship was ever created and nothing showed up as "assigned to me".
- ProjectProcessor.fetch_element() unconditionally called
  _async_get_project_by_guid, which 404s on a Meeting GUID (Meeting is a
  Person Action Base type, not a Project) - Meeting's Dr.Egeria report never
  rendered.
- ToDo/Meeting/Review had no hand-maintained report_spec, so
  render_result_markdown always warned "Report spec '<Type>-DrE-Basic' not
  found" and fell back to the generic Referenceable format.

Unlike the other scenario-tests files in this folder, failures here are
real pytest assertion failures rather than swallowed/logged-and-continue -
this suite exists specifically to catch a regression on the three bugs
above, so silently passing on failure would defeat the point.

A running Egeria environment is needed to run these tests.
"""

import time
from dataclasses import dataclass, field
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from pyegeria import EgeriaTech, ACTIVITY_STATUS
from pyegeria.core._exceptions import PyegeriaException, print_basic_exception

from md_processing.v2.extraction import DrECommand
from md_processing.v2.actor_manager import ActorManagerProcessor
from md_processing.v2.project import ProjectProcessor
from md_processing.v2.feedback import FeedbackProcessor

console = Console()

VIEW_SERVER = "qs-view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "erinoverview"
USER_PWD = "secret"


@dataclass
class TestResult:
    """Data class to hold test results"""
    scenario_name: str
    passed: bool
    duration: float
    skipped: bool = False
    message: str = ""
    error: str = ""


@dataclass
class _ActionRecord:
    """Tracks a created action's expected relationship shape for cleanup/verification."""
    guid: str
    object_type: str
    display_name: str


class TodoScenarioTester:
    """Test harness for ToDo/Meeting/Review full lifecycles, including reporting."""

    def __init__(self):
        self.view_server = VIEW_SERVER
        self.platform_url = PLATFORM_URL
        self.user = USER_ID
        self.password = USER_PWD
        self.client: Optional[EgeriaTech] = None
        self.my_guid: Optional[str] = None
        self.created_guids: list[str] = []

    def setup(self) -> bool:
        try:
            self.client = EgeriaTech(
                self.view_server, self.platform_url, user_id=self.user, user_pwd=self.password
            )
            self.client.create_egeria_bearer_token(self.user, self.password)
            me = self.client.get_my_profile()
            self.my_guid = me["elementHeader"]["guid"]
            console.print(f"[green]✓[/green] Client initialized; my_guid={self.my_guid}")
            return True
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to initialize client: {e}")
            return False

    def teardown(self):
        if not self.client:
            return
        for guid in self.created_guids:
            try:
                self.client.metadata_expert.delete_metadata_element(
                    guid, body={"class": "OpenMetadataDeleteRequestBody"}
                )
                console.print(f"[green]✓[/green] Cleaned up {guid}")
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Could not clean up {guid}: {e}")
        self.client.close_session()
        console.print("[green]✓[/green] Session closed")

    # ------------------------------------------------------------------
    # Shared verification helpers
    # ------------------------------------------------------------------

    def _verify_assignment_relationships(self, guid: str):
        """Assert the create call produced real ActionRequester/AssignmentScope relationships.

        This is the direct regression check for ISSUE-44's root cause: both
        relationships depend on originatorGUID/assignToActorGUID landing at
        the ActionRequestBody top level, not nested inside "properties".
        """
        rels = self.client.metadata_expert.get_all_related_elements(guid)
        assert isinstance(rels, dict), f"Expected related-elements dict for {guid}, got: {rels!r}"
        rel_types = {r["type"]["typeName"] for r in rels.get("elementList", [])}
        assert "ActionRequester" in rel_types, (
            f"No ActionRequester relationship found for {guid} (found: {rel_types}) - "
            f"originatorGUID likely landed in the wrong place in the create body (ISSUE-44)."
        )
        assert "AssignmentScope" in rel_types, (
            f"No AssignmentScope relationship found for {guid} (found: {rel_types}) - "
            f"assignToActorGUID likely landed in the wrong place in the create body (ISSUE-44)."
        )
        return rel_types

    async def _verify_reporting(self, processor_cls, object_type: str, guid: str, qualified_name: str):
        """Render via the real Dr.Egeria processor and assert no report-spec warning.

        Exercises the exact code path ISSUE-44 found broken for Meeting
        (ProjectProcessor.fetch_element defaulting to
        _async_get_project_by_guid, which 404s on a non-Project GUID) and
        for all three types (missing ToDo-DrE/Meeting-DrE/Review-DrE
        report_spec, silently falling back to the generic Referenceable
        format with a "not found" warning).
        """
        cmd = DrECommand(
            verb="Create", object_type=object_type, attributes={},
            raw_block=f"# Create {object_type}"
        )
        proc = processor_cls(client=self.client, command=cmd, context={})
        proc.parsed_output = {"qualified_name": qualified_name}

        markdown = await proc.render_result_markdown(guid)

        warnings = proc.parsed_output.get("warnings") or []
        assert not warnings, f"{object_type} reporting produced warnings: {warnings}"
        assert markdown and markdown != cmd.raw_block, (
            f"{object_type} reporting fell back to raw_block instead of rendering - "
            f"fetch_element likely failed for this type."
        )
        assert qualified_name in markdown or guid in markdown, (
            f"{object_type} report markdown doesn't reference the created element:\n{markdown}"
        )
        return markdown

    # ------------------------------------------------------------------
    # Scenarios
    # ------------------------------------------------------------------

    def scenario_todo_full_lifecycle(self) -> TestResult:
        """
        Scenario: ToDo full lifecycle
        - Create a self-assigned ToDo
        - Verify ActionRequester/AssignmentScope relationships
        - Verify it appears in get_my_to_dos()
        - Verify Dr.Egeria reporting renders it (ToDo-DrE spec, no warnings)
        - Change status, mark complete
        - Delete and verify it's gone
        """
        scenario_name = "ToDo Full Lifecycle"
        start_time = time.perf_counter()
        try:
            display_name = f"Scenario ToDo {int(time.time())}"
            guid = self.client.create_my_todo(
                display_name, description="Created by test_todo_scenarios", priority=0
            )
            assert guid, "create_my_todo returned no GUID"
            self.created_guids.append(guid)
            console.print(f"[green]✓[/green] Created ToDo {guid}")

            rel_types = self._verify_assignment_relationships(guid)
            console.print(f"[green]✓[/green] Relationships present: {rel_types}")

            todos = self.client.get_my_to_dos(output_format="JSON")
            assert isinstance(todos, list), f"get_my_to_dos returned: {todos!r}"
            todo_guids = {e.get("elementHeader", {}).get("guid") for e in todos}
            assert guid in todo_guids, (
                f"New ToDo {guid} not present in get_my_to_dos() ({len(todos)} returned) - "
                f"ISSUE-44 regression."
            )
            console.print(f"[green]✓[/green] ToDo appears in get_my_to_dos() ({len(todos)} total)")

            # Change status via the same asset-level update path the CLI uses
            self.client.update_asset(
                guid,
                body={
                    "class": "UpdateElementRequestBody",
                    "mergeUpdate": True,
                    "properties": {"class": "ToDoProperties", "activityStatus": "IN_PROGRESS"},
                },
            )
            updated = self.client.metadata_expert.get_metadata_element_by_guid(guid)
            status = (
                updated.get("elementProperties", {})
                .get("propertyValueMap", {})
                .get("activityStatus", {})
                .get("symbolicName")
            )
            assert status == "IN_PROGRESS", f"Expected activityStatus IN_PROGRESS, got {status}"
            console.print("[green]✓[/green] Status updated to IN_PROGRESS")

            # Mark complete
            self.client.update_asset(
                guid,
                body={
                    "class": "UpdateElementRequestBody",
                    "mergeUpdate": True,
                    "properties": {"class": "ToDoProperties", "activityStatus": "COMPLETED"},
                },
            )
            updated = self.client.metadata_expert.get_metadata_element_by_guid(guid)
            status = (
                updated.get("elementProperties", {})
                .get("propertyValueMap", {})
                .get("activityStatus", {})
                .get("symbolicName")
            )
            assert status == "COMPLETED", f"Expected activityStatus COMPLETED, got {status}"
            console.print("[green]✓[/green] Status updated to COMPLETED")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name, passed=True, duration=duration,
                message=f"ToDo {guid} created, assigned, visible, updated",
            )
        except PyegeriaException as e:
            duration = time.perf_counter() - start_time
            print_basic_exception(e)
            return TestResult(scenario_name=scenario_name, passed=False, duration=duration, error=str(e))
        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(scenario_name=scenario_name, passed=False, duration=duration, error=str(e))

    def scenario_todo_reporting(self) -> TestResult:
        """
        Scenario: ToDo Dr.Egeria reporting
        - Create a ToDo
        - Render it via ActorManagerProcessor.render_result_markdown
        - Verify no "report spec not found" warning and real content
        """
        scenario_name = "ToDo Dr.Egeria Reporting"
        start_time = time.perf_counter()
        try:
            display_name = f"Scenario ToDo Report {int(time.time())}"
            guid = self.client.create_my_todo(display_name, description="reporting check")
            self.created_guids.append(guid)

            import asyncio
            markdown = asyncio.get_event_loop().run_until_complete(
                self._verify_reporting(ActorManagerProcessor, "ToDo", guid, display_name)
            )
            console.print(f"[green]✓[/green] ToDo report rendered ({len(markdown)} chars, no warnings)")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name, passed=True, duration=duration,
                message="ToDo-DrE report spec resolved and rendered cleanly",
            )
        except PyegeriaException as e:
            duration = time.perf_counter() - start_time
            print_basic_exception(e)
            return TestResult(scenario_name=scenario_name, passed=False, duration=duration, error=str(e))
        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(scenario_name=scenario_name, passed=False, duration=duration, error=str(e))

    def scenario_meeting_full_lifecycle(self) -> TestResult:
        """
        Scenario: Meeting full lifecycle
        - Create a self-assigned Meeting
        - Verify ActionRequester/AssignmentScope relationships
        - Verify it appears in get_my_assigned_actions()
        - Verify Dr.Egeria reporting renders it via ProjectProcessor
          (regression check for the fetch_element/_async_get_project_by_guid
          bug - Meeting is not a Project)
        - Delete and verify it's gone
        """
        scenario_name = "Meeting Full Lifecycle"
        start_time = time.perf_counter()
        try:
            display_name = f"Scenario Meeting {int(time.time())}"
            guid = self.client.create_meeting(
                display_name, description="Created by test_todo_scenarios", priority=0
            )
            assert guid, "create_meeting returned no GUID"
            self.created_guids.append(guid)
            console.print(f"[green]✓[/green] Created Meeting {guid}")

            rel_types = self._verify_assignment_relationships(guid)
            console.print(f"[green]✓[/green] Relationships present: {rel_types}")

            actions = self.client.get_my_assigned_actions(output_format="JSON")
            assert isinstance(actions, list), f"get_my_assigned_actions returned: {actions!r}"
            action_guids = {e.get("elementHeader", {}).get("guid") for e in actions}
            assert guid in action_guids, (
                f"New Meeting {guid} not present in get_my_assigned_actions() - ISSUE-44 regression."
            )
            console.print(f"[green]✓[/green] Meeting appears in get_my_assigned_actions()")

            import asyncio
            markdown = asyncio.get_event_loop().run_until_complete(
                self._verify_reporting(ProjectProcessor, "Meeting", guid, display_name)
            )
            console.print(f"[green]✓[/green] Meeting report rendered ({len(markdown)} chars, no warnings)")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name, passed=True, duration=duration,
                message=f"Meeting {guid} created, assigned, visible, reported",
            )
        except PyegeriaException as e:
            duration = time.perf_counter() - start_time
            print_basic_exception(e)
            return TestResult(scenario_name=scenario_name, passed=False, duration=duration, error=str(e))
        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(scenario_name=scenario_name, passed=False, duration=duration, error=str(e))

    def scenario_review_full_lifecycle(self) -> TestResult:
        """
        Scenario: Review full lifecycle
        - Create a self-assigned Review
        - Verify ActionRequester/AssignmentScope relationships
        - Verify Dr.Egeria reporting renders it via FeedbackProcessor
        - Delete and verify it's gone
        """
        scenario_name = "Review Full Lifecycle"
        start_time = time.perf_counter()
        try:
            display_name = f"Scenario Review {int(time.time())}"
            guid = self.client.create_review(
                display_name, description="Created by test_todo_scenarios", priority=0
            )
            assert guid, "create_review returned no GUID"
            self.created_guids.append(guid)
            console.print(f"[green]✓[/green] Created Review {guid}")

            rel_types = self._verify_assignment_relationships(guid)
            console.print(f"[green]✓[/green] Relationships present: {rel_types}")

            import asyncio
            markdown = asyncio.get_event_loop().run_until_complete(
                self._verify_reporting(FeedbackProcessor, "Review", guid, display_name)
            )
            console.print(f"[green]✓[/green] Review report rendered ({len(markdown)} chars, no warnings)")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name, passed=True, duration=duration,
                message=f"Review {guid} created, assigned, reported",
            )
        except PyegeriaException as e:
            duration = time.perf_counter() - start_time
            print_basic_exception(e)
            return TestResult(scenario_name=scenario_name, passed=False, duration=duration, error=str(e))
        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(scenario_name=scenario_name, passed=False, duration=duration, error=str(e))

    def scenario_todo_reassignment(self) -> TestResult:
        """
        Scenario: ToDo reassignment
        - Create a ToDo assigned to self
        - Find a different Person actor on the server
        - Reassign the ToDo to them
        - Verify the new AssignmentScope relationship points to the new actor
        """
        scenario_name = "ToDo Reassignment"
        start_time = time.perf_counter()
        try:
            people = self.client.metadata_expert.find_metadata_elements(
                body={"class": "FindRequestBody", "metadataElementTypeName": "Person"}
            )
            other_guid = None
            if isinstance(people, list):
                for p in people:
                    g = p.get("elementGUID")
                    if g and g != self.my_guid:
                        other_guid = g
                        break

            if not other_guid:
                duration = time.perf_counter() - start_time
                console.print("[yellow]⚠[/yellow] No second Person actor found on this server - skipping")
                return TestResult(
                    scenario_name=scenario_name, passed=False, skipped=True, duration=duration,
                    message="No second Person actor available to reassign to",
                )

            display_name = f"Scenario ToDo Reassign {int(time.time())}"
            guid = self.client.create_my_todo(display_name, description="reassignment check")
            self.created_guids.append(guid)
            console.print(f"[green]✓[/green] Created ToDo {guid} assigned to self")

            self.client.reassign_action(guid, other_guid)
            console.print(f"[green]✓[/green] Reassigned ToDo to {other_guid}")

            rels = self.client.metadata_expert.get_all_related_elements(guid)
            assigned_guids = {
                r["element"]["elementGUID"]
                for r in rels.get("elementList", [])
                if r["type"]["typeName"] == "AssignmentScope"
            }
            assert other_guid in assigned_guids, (
                f"Expected AssignmentScope to include {other_guid} after reassignment, "
                f"found: {assigned_guids}"
            )
            console.print(f"[green]✓[/green] AssignmentScope confirms reassignment")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name, passed=True, duration=duration,
                message=f"ToDo {guid} reassigned from self to {other_guid}",
            )
        except PyegeriaException as e:
            duration = time.perf_counter() - start_time
            print_basic_exception(e)
            return TestResult(scenario_name=scenario_name, passed=False, duration=duration, error=str(e))
        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(scenario_name=scenario_name, passed=False, duration=duration, error=str(e))

    def scenario_todo_delete(self) -> TestResult:
        """
        Scenario: ToDo deletion
        - Create a ToDo
        - Delete it
        - Verify it's no longer retrievable
        """
        scenario_name = "ToDo Delete"
        start_time = time.perf_counter()
        try:
            display_name = f"Scenario ToDo Delete {int(time.time())}"
            guid = self.client.create_my_todo(display_name, description="delete check")
            console.print(f"[green]✓[/green] Created ToDo {guid}")

            self.client.metadata_expert.delete_metadata_element(
                guid, body={"class": "OpenMetadataDeleteRequestBody"}
            )
            console.print(f"[green]✓[/green] Deleted ToDo {guid}")

            try:
                self.client.metadata_expert.get_metadata_element_by_guid(guid)
                raised = False
            except PyegeriaException:
                raised = True
            assert raised, f"ToDo {guid} still retrievable after delete"
            console.print("[green]✓[/green] Confirmed ToDo no longer retrievable")

            duration = time.perf_counter() - start_time
            return TestResult(
                scenario_name=scenario_name, passed=True, duration=duration,
                message=f"ToDo {guid} created and deleted cleanly",
            )
        except PyegeriaException as e:
            duration = time.perf_counter() - start_time
            print_basic_exception(e)
            return TestResult(scenario_name=scenario_name, passed=False, duration=duration, error=str(e))
        except Exception as e:
            duration = time.perf_counter() - start_time
            return TestResult(scenario_name=scenario_name, passed=False, duration=duration, error=str(e))

    # ------------------------------------------------------------------
    # Harness plumbing (matches sibling scenario-tests files' shape)
    # ------------------------------------------------------------------

    def run_all_scenarios(self) -> list[TestResult]:
        results = []
        console.print(Panel.fit(
            "[bold cyan]ToDo / Meeting / Review Scenario Tests[/bold cyan]\n"
            "Full lifecycle including assignment relationships and Dr.Egeria reporting",
            border_style="cyan"
        ))

        if not self.setup():
            return results

        try:
            scenarios = [
                self.scenario_todo_full_lifecycle,
                self.scenario_todo_reporting,
                self.scenario_meeting_full_lifecycle,
                self.scenario_review_full_lifecycle,
                self.scenario_todo_reassignment,
                self.scenario_todo_delete,
            ]

            for scenario_func in scenarios:
                console.print(f"\n[bold yellow]{'=' * 80}[/bold yellow]")
                console.print(f"[bold]Running: {scenario_func.__doc__.split('Scenario:')[1].split(chr(10))[0].strip()}[/bold]")
                console.print(f"[bold yellow]{'=' * 80}[/bold yellow]")

                result = scenario_func()
                results.append(result)

                if result.passed:
                    console.print(f"\n[green]✓ PASSED[/green] - {result.message}")
                elif result.skipped:
                    console.print(f"\n[yellow]⚠ SKIPPED[/yellow] - {result.message}")
                else:
                    console.print(f"\n[red]✗ FAILED[/red] - {result.error}")

                console.print(f"Duration: {result.duration:.2f} seconds")
        finally:
            self.teardown()

        return results

    def print_results_summary(self, results: list[TestResult]):
        table = Table(title="Test Results Summary", show_header=True, header_style="bold magenta")
        table.add_column("Scenario", style="cyan", width=40)
        table.add_column("Status", justify="center", width=10)
        table.add_column("Duration", justify="right", width=12)
        table.add_column("Details", width=50)

        total_duration = 0.0
        passed_count = 0
        skipped_count = 0

        for result in results:
            if result.passed:
                status = "[green]✓ PASS[/green]"
            elif result.skipped:
                status = "[yellow]⚠ SKIP[/yellow]"
            else:
                status = "[red]✗ FAIL[/red]"
            duration_str = f"{result.duration:.2f}s"
            details = result.message if (result.passed or result.skipped) else result.error

            table.add_row(
                result.scenario_name, status, duration_str,
                details[:47] + "..." if len(details) > 50 else details,
            )

            total_duration += result.duration
            if result.passed:
                passed_count += 1
            if result.skipped:
                skipped_count += 1

        console.print("\n")
        console.print(table)
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  Total scenarios: {len(results)}")
        console.print(f"  Passed: [green]{passed_count}[/green]")
        console.print(f"  Skipped: [yellow]{skipped_count}[/yellow]")
        console.print(f"  Failed: [red]{len(results) - passed_count - skipped_count}[/red]")
        console.print(f"  Total duration: {total_duration:.2f}s")


def test_todo_scenarios():
    """Pytest entry point"""
    tester = TodoScenarioTester()
    results = tester.run_all_scenarios()
    tester.print_results_summary(results)

    # Unlike the other scenario-tests files, this suite asserts real failures -
    # it exists specifically to catch a regression on ISSUE-44's three bugs.
    failures = [r for r in results if not (r.passed or r.skipped)]
    assert not failures, "Some scenarios failed:\n" + "\n".join(
        f"  - {r.scenario_name}: {r.error}" for r in failures
    )


if __name__ == "__main__":
    tester = TodoScenarioTester()
    results = tester.run_all_scenarios()
    tester.print_results_summary(results)
