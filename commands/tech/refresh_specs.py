#!/usr/bin/env python3
"""
refresh_specs.py

A unified script to automatically refresh the generated documentation and report
specifications for Dr. Egeria.

This script executes the following generation processes in order:
1. Markdown command templates generation (generate_md_cmd_templates)
2. Dr. Egeria help documentation generation (generate_dr_help)
3. Report FormatSet specifications generation (gen_report_specs)

Usage:
  uv run python refresh_specs.py [options]

Options allow filtering generation by specific --family and/or --usage-level.
"""
import argparse
import subprocess
import sys
from loguru import logger

def run_command(cmd_args: list[str], description: str):
    logger.info(f"Running: {description}")
    logger.debug(f"Command: {' '.join(cmd_args)}")

    try:
        result = subprocess.run(cmd_args, check=True, text=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed during {description}")
        logger.error(f"Error Code: {e.returncode}")
        sys.exit(1)

    logger.info(f"Successfully completed: {description}\n")

def main():
    parser = argparse.ArgumentParser(description="Refresh generated specs and templates for Dr. Egeria.")
    parser.add_argument("--usage-level", choices=["Basic", "Advanced"], default=None,
                        help="Egeria usage level (Basic or Advanced). "
                             "If omitted, both Basic and Advanced are generated.")
    parser.add_argument("--family", type=str, default=None,
                        help="Generate only for a specific family (applies to cmd templates)")
    parser.add_argument("--merge-reports", action="store_true", default=False,
                        help="Persist generated report specs by merging them into base_report_formats.py")
    args = parser.parse_args()

    # Base executable path for scripts
    python_exec = sys.executable

    # When no usage level is requested, refresh both Basic and Advanced.
    usage_levels = [args.usage_level] if args.usage_level else ["Basic", "Advanced"]

    # 1. Generate Markdown Command Templates (per usage level)
    for usage_level in usage_levels:
        cmd_templates = [
            python_exec,
            "-m", "commands.tech.generate_md_cmd_templates",
            "--usage-level", usage_level,
        ]
        if args.family:
            cmd_templates.extend(["--family", args.family])
        run_command(cmd_templates, f"Markdown Command Templates Generation ({usage_level})")

    # 2. Generate Dr. Egeria Help (per usage level)
    for usage_level in usage_levels:
        cmd_help = [
            python_exec,
            "-m", "commands.tech.generate_dr_help"
        ]
        if usage_level == "Advanced":
            cmd_help.append("--advanced")
        run_command(cmd_help, f"Dr. Egeria Help Generation ({usage_level})")

    # 3. Generate Report Specifications
    cmd_reports = [
        python_exec,
        "-m", "commands.tech.gen_report_specs"
    ]
    # We generally always default to non-interactive mode to prevent blocking
    # We pass the default path to the compact_commands dir as the input argument.
    cmd_reports.append("md_processing/data/compact_commands")

    if args.usage_level:
        cmd_reports.extend(["--usage-level", args.usage_level])
    if args.merge_reports:
        cmd_reports.append("--merge")

    run_command(cmd_reports, "Report Specifications Generation")

    logger.info("All regeneration tasks have completed successfully.")

if __name__ == "__main__":
    main()

