"""Validate compact command specs against Dr.Egeria processing assumptions."""

from __future__ import annotations

import json
from pathlib import Path
import os

import click
from rich.console import Console
from rich.table import Table

from md_processing.md_processing_utils.compact_spec_validator import (
    collect_derived_processing_types,
    fetch_valid_om_types,
    validate_compact_specs,
)


def _print_table(findings, target: str) -> None:
    console = Console()
    table = Table(title=f"Compact Spec Validation: {target}")
    table.add_column("Severity")
    table.add_column("Code")
    table.add_column("Command")
    table.add_column("File")
    table.add_column("Message")

    for finding in findings:
        table.add_row(
            finding.severity,
            finding.code,
            finding.command_name,
            Path(finding.file_path).name,
            finding.message,
        )

    if findings:
        console.print(table)
    else:
        console.print("No issues found.")


def _print_derived_types_table(rows, target: str) -> None:
    console = Console()
    table = Table(title=f"Derived Processing Types: {target}")
    table.add_column("Command")
    table.add_column("File")
    table.add_column("OM_TYPE")
    table.add_column("Derived Type")

    for row in rows:
        table.add_row(
            row["command_name"],
            Path(row["file_path"]).name,
            row.get("om_type", ""),
            row["derived_processing_type"],
        )

    console.print(table)


@click.command(name="validate-compact-specs")
@click.argument("spec_path", required=False)
@click.option("--strict", is_flag=True, help="Return non-zero if warnings are found.")
@click.option("--format", "output_format", type=click.Choice(["table", "json", "both"]), default="both")
@click.option("--validate-om-types/--no-validate-om-types", default=True, help="Validate OM_TYPE values against Egeria type defs.")
@click.option(
    "--validate-derived-match/--no-validate-derived-match",
    default=False,
    help="Validate OM_TYPE equals derived processing type (disabled by default).",
)
@click.option("--server", default=lambda: os.environ.get("EGERIA_VIEW_SERVER", "qs-view-server"), show_default=True)
@click.option("--url", default=lambda: os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443"), show_default=True)
@click.option("--userid", default=lambda: os.environ.get("EGERIA_USER", "erinoverview"), show_default=True)
@click.option("--password", default=lambda: os.environ.get("EGERIA_USER_PASSWORD", "secret"), show_default=True)
def main(
    spec_path: str | None,
    strict: bool,
    output_format: str,
    validate_om_types: bool,
    validate_derived_match: bool,
    server: str,
    url: str,
    userid: str,
    password: str,
) -> None:
    """Validate compact command JSON files and report errors/warnings.

    SPEC_PATH can be a compact command directory or a single compact JSON file.
    """
    target = spec_path or "md_processing/data/compact_commands"

    valid_om_types = None
    if validate_om_types:
        try:
            valid_om_types = fetch_valid_om_types(server=server, url=url, user_id=userid, user_pwd=password)
        except Exception as exc:
            raise click.ClickException(
                "Unable to fetch OM types from Egeria using get_all_entity_defs/get_all_relationship_defs: "
                f"{exc}"
            ) from exc

    findings = validate_compact_specs(
        target,
        valid_om_types=valid_om_types,
        validate_derived_match=validate_derived_match,
    )
    errors = [f for f in findings if f.severity == "ERROR"]
    warnings = [f for f in findings if f.severity == "WARNING"]

    derived_rows = collect_derived_processing_types(target)

    if output_format in {"table", "both"}:
        _print_table(findings, target)
        click.echo(f"\nErrors: {len(errors)}  Warnings: {len(warnings)}")
        _print_derived_types_table(derived_rows, target)

    if output_format in {"json", "both"}:
        rows = [
            {
                "severity": f.severity,
                "file_path": f.file_path,
                "command_name": f.command_name,
                "code": f.code,
                "message": f.message,
            }
            for f in findings
        ]
        click.echo(
            json.dumps(
                {
                    "errors": len(errors),
                    "warnings": len(warnings),
                    "findings": rows,
                    "derived_processing_types": derived_rows,
                },
                indent=2,
            )
        )

    if errors or (strict and warnings):
        raise click.ClickException("Compact spec validation failed.")


if __name__ == "__main__":
    main()
