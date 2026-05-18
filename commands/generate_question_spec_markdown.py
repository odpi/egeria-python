#!/usr/bin/env python3
"""
generate_question_spec_markdown.py — generate Dr. Egeria markdown install files

Reads question_specs from base_report_specs and generated_format_sets and writes:
  - sample-data/question-spec-install/00_perspectives.md  (all unique perspectives)
  - sample-data/question-spec-install/<label>.md          (one file per report type)
  - sample-data/question-spec-install/run_all.sh          (process all files in order)

Usage:
    python commands/generate_question_spec_markdown.py [--output-dir <path>]
"""

import argparse
import os
import re
import stat
import sys
from collections import OrderedDict
from pathlib import Path


def _safe_filename(label: str) -> str:
    """Convert a report type label to a safe filename."""
    safe = re.sub(r'[^\w\s-]', '', label)
    safe = re.sub(r'\s+', '_', safe.strip())
    return safe


def _slug(text: str) -> str:
    """Convert display name to a QN-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[?',\".!;:()\[\]{}]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text


def _perspective_block(name: str) -> str:
    """Generate a Create Perspective markdown block."""
    qn = f"Perspective::{name}"
    return f"""\
## Create Perspective

### Display Name

{name}

### Qualified Name

{qn}

### GUID

___

"""


def _report_type_block(label: str) -> str:
    """Generate a Create Report Type markdown block."""
    qn = f"ReportType::{label}"
    return f"""\
## Create Report Type

### Display Name

{label}

### Qualified Name

{qn}

### GUID

___

"""


def _question_spec_block(label: str, idx: int) -> str:
    """Generate a Create Question Spec markdown block."""
    name = f"{label}::{idx}"
    qn = f"QuestionSpec::{name}"
    return f"""\
## Create Question Spec

### Display Name

{name}

### Qualified Name

{qn}

### GUID

___

"""


def _add_member_block(element_qn: str, collection_qn: str, rationale: str = "") -> str:
    """Generate an Add Member to Collection markdown block."""
    rationale_line = rationale or "Link to parent collection."
    return f"""\
## Add Member to Collection

### Element Id

{element_qn}

### Membership Rationale

{rationale_line}

### Membership Status

ACTIVE

### Collection Id

{collection_qn}

"""


def _create_question_block(question_text: str) -> str:
    """Generate a Create Question markdown block."""
    qn = f"Question::{_slug(question_text)}"
    return f"""\
## Create Question

### Display Name

{question_text}

### Qualified Name

{qn}

### GUID

___

"""


def _link_perspective_block(perspective_name: str, question_text: str) -> str:
    """Generate a Link Perspective to Question markdown block."""
    p_qn = f"Perspective::{perspective_name}"
    q_qn = f"Question::{_slug(question_text)}"
    return f"""\
## Link Perspective to Question

### Perspective Name

{p_qn}

### Question Name

{q_qn}

"""


def _separator() -> str:
    return "____\n"


def generate_perspectives_file(all_perspectives: list[str], output_dir: Path) -> Path:
    """Write 00_perspectives.md with one Create Perspective block per unique perspective."""
    lines = ["# Perspectives\n\n"]
    lines.append("> This file creates all unique Perspective entities used across report type question specs.\n")
    lines.append("> Process this file BEFORE any report-type files.\n\n")
    lines.append(_separator() + "\n")

    for name in all_perspectives:
        lines.append(_perspective_block(name))
        lines.append(_separator() + "\n")

    out_path = output_dir / "00_perspectives.md"
    out_path.write_text("".join(lines), encoding="utf-8")
    return out_path


def generate_report_type_file(label: str, format_set, output_dir: Path) -> Path:
    """Write one markdown file for a report type with its question specs."""
    question_spec = getattr(format_set, "question_spec", None) or []

    lines = [f"# {label}\n\n"]
    lines.append(f"> Install file for the **{label}** report type question specs.\n")
    lines.append("> Process 00_perspectives.md before this file.\n\n")
    lines.append(_separator() + "\n")

    # Create Report Type
    rt_qn = f"ReportType::{label}"
    lines.append(f"# Create Report Type: {label}\n\n")
    lines.append(_report_type_block(label))
    lines.append(_separator() + "\n")

    for idx, entry in enumerate(question_spec, start=1):
        if hasattr(entry, "perspectives"):
            perspectives = entry.perspectives
            questions = entry.questions
        else:
            perspectives = entry.get("perspectives", [])
            questions = entry.get("questions", [])

        if not questions:
            continue

        qs_name = f"{label}::{idx}"
        qs_qn = f"QuestionSpec::{qs_name}"

        lines.append(f"# Question Spec {idx}: {qs_name}\n\n")

        # Create Question Spec folder
        lines.append(_question_spec_block(label, idx))
        lines.append(_separator() + "\n")

        # Link Question Spec to Report Type
        lines.append(f"# Link Question Spec {idx} to Report Type\n\n")
        lines.append(_add_member_block(qs_qn, rt_qn, f"Link question spec {idx} to {label} report type."))
        lines.append(_separator() + "\n")

        # Create each question
        for q_text in questions:
            q_qn = f"Question::{_slug(q_text)}"
            lines.append(f"# Question: {q_text[:60]}{'...' if len(q_text) > 60 else ''}\n\n")
            lines.append(_create_question_block(q_text))
            lines.append(_separator() + "\n")

            # Link question to its question spec folder
            lines.append(_add_member_block(q_qn, qs_qn, f"Add question to {qs_name}."))
            lines.append(_separator() + "\n")

            # Link each perspective to this question
            for p_name in perspectives:
                if p_name == "ANY":
                    continue
                lines.append(f"# Link Perspective '{p_name}' to Question\n\n")
                lines.append(_link_perspective_block(p_name, q_text))
                lines.append(_separator() + "\n")

    safe_name = _safe_filename(label)
    out_path = output_dir / f"{safe_name}.md"
    out_path.write_text("".join(lines), encoding="utf-8")
    return out_path


def generate_run_all_script(file_order: list[str], output_dir: Path) -> Path:
    """Write run_all.sh to process all install files in order."""
    lines = [
        "#!/usr/bin/env bash\n",
        "# Auto-generated by generate_question_spec_markdown.py\n",
        "# Processes all question-spec install files in order.\n",
        "#\n",
        "# Usage: bash run_all.sh [--url <platform_url>] [--server <view_server>]\n",
        "#                        [--userid <user_id>] [--user_pass <user_pwd>]\n\n",
        "set -e\n",
        'SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"\n\n',
        "# Pass through any arguments to dr_egeria\n",
        'ARGS="$@"\n\n',
    ]

    for fname in file_order:
        lines.append(f'echo "Processing {fname}..."\n')
        lines.append(f'dr_egeria "${{SCRIPT_DIR}}/{fname}" --process $ARGS\n')
        lines.append('echo "Done."\n\n')

    out_path = output_dir / "run_all.sh"
    out_path.write_text("".join(lines), encoding="utf-8")
    # Make executable
    out_path.chmod(out_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Dr. Egeria markdown install files for question specs."
    )
    parser.add_argument(
        "--output-dir",
        default="sample-data/question-spec-install",
        help="Output directory (default: sample-data/question-spec-install)",
    )
    args = parser.parse_args()

    # Import here so the script fails fast if the package isn't installed
    from pyegeria.view.base_report_formats import base_report_specs, generated_format_sets

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Merge both sources; base_report_specs takes priority
    all_specs: dict = {}
    for label, fs in list(base_report_specs.items()) + list(generated_format_sets.items()):
        if label not in all_specs:
            all_specs[label] = fs

    # Filter to only those with question_specs
    specs_with_questions = {
        label: fs
        for label, fs in all_specs.items()
        if getattr(fs, "question_spec", None)
    }

    if not specs_with_questions:
        print("No question_specs found — nothing to generate.", file=sys.stderr)
        sys.exit(1)

    # Collect all unique perspectives in encounter order
    seen_perspectives: dict[str, None] = {}
    for fs in specs_with_questions.values():
        for entry in (fs.question_spec or []):
            perspectives = entry.perspectives if hasattr(entry, "perspectives") else entry.get("perspectives", [])
            for p in perspectives:
                if p != "ANY":
                    seen_perspectives[p] = None

    all_perspectives = list(seen_perspectives.keys())

    # Generate perspectives file
    persp_path = generate_perspectives_file(all_perspectives, output_dir)
    print(f"Written: {persp_path}")

    # Generate one file per label (sorted)
    generated_files = ["00_perspectives.md"]
    for label in sorted(specs_with_questions.keys()):
        fs = specs_with_questions[label]
        out_path = generate_report_type_file(label, fs, output_dir)
        generated_files.append(out_path.name)
        print(f"Written: {out_path}")

    # Generate run_all.sh
    script_path = generate_run_all_script(generated_files, output_dir)
    print(f"Written: {script_path}")

    print(
        f"\nGenerated {len(specs_with_questions)} report-type files + "
        f"1 perspectives file + run_all.sh in {output_dir}/"
    )


if __name__ == "__main__":
    main()
