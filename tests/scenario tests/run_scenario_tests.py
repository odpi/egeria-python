#!/usr/bin/env python3
"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This script is a simple test runner for Egeria Python scenarios. It finds and executes all test files matching the
pattern 'test_*_scenarios.py' and summarizes the results.
"""

import subprocess
import sys
import time
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def run_scenario_tests():
    """Find and run all files matching test_*_scenarios.py and summarize results."""
    test_dir = Path(__file__).parent
    scenario_files = sorted(list(test_dir.glob("test_*_scenarios.py")))

    if not scenario_files:
        console.print("[bold red]No scenario tests found in the tests/ directory.[/bold red]")
        return

    console.print(Panel.fit(
        "[bold cyan]Egeria Python - Automated Scenario Test Runner[/bold cyan]",
        border_style="cyan"
    ))

    results = []

    with console.status("[bold green]Executing scenarios...") as status:
        for test_file in scenario_files:
            status.update(f"[bold yellow]Running: {test_file.name}...")

            start_time = time.perf_counter()
            # Execute using pytest via 'uv run' to ensure environment consistency
            process = subprocess.run(
                ["uv", "run", "pytest", str(test_file), "-v", "--tb=short"],
                capture_output=True,
                text=True
            )
            duration = time.perf_counter() - start_time

            status_str = "[green]PASSED[/green]" if process.returncode == 0 else "[red]FAILED[/red]"
            results.append({
                "name": test_file.name,
                "status": status_str,
                "duration": f"{duration:.2f}s",
                "output": process.stdout if process.returncode != 0 else ""
            })

    # Summary Table
    table = Table(title="\nScenario Test Results Summary", show_lines=True)
    table.add_column("Test Suite", style="magenta")
    table.add_column("Status", justify="center")
    table.add_column("Duration", justify="right")

    passed_count = 0
    for res in results:
        table.add_row(res["name"], res["status"], res["duration"])
        if "PASSED" in res["status"]:
            passed_count += 1

    console.print(table)

    # Report Failures if any
    for res in results:
        if "FAILED" in res["status"]:
            console.print(f"\n[bold red]Details for {res['name']}:[/bold red]")
            console.print(res["output"])

    final_msg = f"\n[bold]Total:[/bold] {len(results)} | [green]Passed:[/green] {passed_count} | [red]Failed:[/red] {len(results) - passed_count}"
    console.print(final_msg)

    if passed_count < len(results):
        sys.exit(1)


if __name__ == "__main__":
    try:
        run_scenario_tests()
    except KeyboardInterrupt:
        console.print("\n[bold red]Test execution interrupted by user.[/bold red]")
        sys.exit(1)