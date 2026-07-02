#!/usr/bin/env python3
"""
Run all dr_test_*.md files in this folder in validate mode (and optionally
process mode), capturing output to a results file.

Migrated from tests/scenario-tests/run_dr_tests.py, which resolved
TEST_FILES relative to the configured Dr.Egeria Inbox path -- mixing test
fixtures into a working scratch folder (sample-data/egeria-inbox/dr-egeria-inbox/).
This version uses absolute paths (process_md_file_v2's input_file accepts an
absolute path or one relative to EGERIA_INBOX_PATH), so the markdown
fixtures and this runner live together here, self-contained and reviewable
in a normal git diff.

Usage:
    python run_dr_tests.py            # validate mode only (safe, no writes)
    python run_dr_tests.py --process  # also run process mode (writes to Egeria)
"""
import asyncio
import io
import os
import sys
from datetime import datetime

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_FILE = os.path.join(THIS_DIR, "dr_test_results.txt")

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
    "dr_test_new_commands.md",
    "dr_test_action_author.md",
]


def run_one(input_file: str, directive: str, results_fh):
    from pyegeria import EgeriaTech
    from pyegeria.core.config import settings
    from md_processing.dr_egeria import process_md_file_v2

    abs_path = os.path.join(THIS_DIR, input_file)

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

        from rich.console import Console
        import md_processing.dr_egeria as dre_module

        buf = io.StringIO()
        old_console = dre_module.console
        dre_module.console = Console(file=buf, width=200, highlight=False, markup=True)

        try:
            asyncio.run(process_md_file_v2(
                input_file=abs_path,
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


def run_mode(directive: str, fh):
    print(f"\n\n### {directive.upper()} MODE ###", file=fh)
    totals = {"success": 0, "failure": 0, "warning": 0}
    file_results = []
    for test_file in TEST_FILES:
        s, f, w = run_one(test_file, directive, fh)
        totals["success"] += s
        totals["failure"] += f
        totals["warning"] += w
        file_results.append((test_file, s, f, w))

    print(f"\n\n{'='*80}", file=fh)
    print(f"{directive.upper()} MODE SUMMARY", file=fh)
    print(f"{'='*80}", file=fh)
    print(f"{'File':<40} {'S':>5} {'F':>5} {'W':>5}", file=fh)
    for fname, s, f, w in file_results:
        print(f"{fname:<40} {s:>5} {f:>5} {w:>5}", file=fh)
    print(f"\nTOTALS: {totals['success']} SUCCESS  {totals['failure']} FAILURE  {totals['warning']} WARNING", file=fh)
    fh.flush()


def main():
    do_process = "--process" in sys.argv

    with open(RESULTS_FILE, "w") as fh:
        print(f"Dr. Egeria Test Run — {datetime.now()}", file=fh)
        fh.flush()

        run_mode("validate", fh)
        if do_process:
            run_mode("process", fh)

    print(f"Results written to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
