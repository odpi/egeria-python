#!/usr/bin/env python3
"""
Run all dr_test_*.md files in validate mode then process mode,
capturing output to a results file.
"""
import asyncio
import sys
import os
import io
from datetime import datetime

# Redirect rich console to file
RESULTS_FILE = "/Users/dwolfson/localGit/egeria-python/dr_test_results.txt"

TEST_FILES = [
    "dr_test_glossary.md",
    "dr_test_governance.md",
    "dr_test_projects.md",
    "dr_test_collections_good.md",
    "dr_test_collections_mean.md",
    "dr_test_products_good.md",
    "dr_test_external_ref.md",
    "dr_test_feedback.md",
    "dr_test_data_designer.md",
    "dr_test_report.md",
    "dr_test_solution.md",
]

def run_one(input_file: str, directive: str, results_fh):
    """Run one test file with the given directive, writing summary to results_fh."""
    from pyegeria import EgeriaTech
    from pyegeria.core.config import settings
    from md_processing.dr_egeria import process_md_file_v2

    print(f"\n{'='*80}", file=results_fh)
    print(f"FILE: {input_file}  |  DIRECTIVE: {directive}  |  {datetime.now().strftime('%H:%M:%S')}", file=results_fh)
    print(f"{'='*80}", file=results_fh)
    results_fh.flush()

    try:
        client = EgeriaTech(
            settings.Environment.egeria_view_server,
            settings.Environment.egeria_view_server_url,
            "erinoverview",
            "secret",
        )
        client.create_egeria_bearer_token()

        # Capture rich console output by temporarily replacing stdout
        from rich.console import Console
        import md_processing.dr_egeria as dre_module

        buf = io.StringIO()
        # Monkeypatch the console used in the module
        old_console = dre_module.console
        dre_module.console = Console(file=buf, width=200, highlight=False, markup=True)

        try:
            asyncio.run(process_md_file_v2(
                input_file=input_file,
                output_folder="",
                directive=directive,
                client=client,
                parse_summary="all",
                attribute_logs="info",
                summary_only=True,
            ))
        finally:
            dre_module.console = old_console

        output = buf.getvalue()
        print(output, file=results_fh)
        results_fh.flush()

        # Count successes/failures/warnings from the output
        successes = output.count("SUCCESS")
        failures = output.count("FAILURE")
        warnings = output.count("WARNING")
        print(f"\nSCORE: {successes} SUCCESS  {failures} FAILURE  {warnings} WARNING", file=results_fh)
        results_fh.flush()
        return successes, failures, warnings

    except Exception as e:
        import traceback
        msg = f"EXCEPTION running {input_file} ({directive}): {e}\n{traceback.format_exc()}"
        print(msg, file=results_fh)
        results_fh.flush()
        return 0, 1, 0


def main():
    with open(RESULTS_FILE, "w") as fh:
        print(f"Dr. Egeria Test Run — {datetime.now()}", file=fh)
        print(f"Directive: VALIDATE (all files)", file=fh)
        fh.flush()

        totals = {"success": 0, "failure": 0, "warning": 0}
        file_results = []

        print("\n\n### VALIDATE MODE ###", file=fh)
        for test_file in TEST_FILES:
            s, f, w = run_one(test_file, "validate", fh)
            totals["success"] += s
            totals["failure"] += f
            totals["warning"] += w
            file_results.append((test_file, "validate", s, f, w))

        print(f"\n\n{'='*80}", file=fh)
        print("VALIDATE MODE SUMMARY", file=fh)
        print(f"{'='*80}", file=fh)
        print(f"{'File':<40} {'S':>5} {'F':>5} {'W':>5}", file=fh)
        for fname, directive, s, f, w in file_results:
            print(f"{fname:<40} {s:>5} {f:>5} {w:>5}", file=fh)
        print(f"\nTOTALS: {totals['success']} SUCCESS  {totals['failure']} FAILURE  {totals['warning']} WARNING", file=fh)
        fh.flush()

    print(f"Results written to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()

