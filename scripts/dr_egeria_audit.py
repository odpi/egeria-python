#!/usr/bin/env python3
"""Audit Dr.Egeria's compact command specs against real Egeria ground truth.

`scripts/omvs_audit.py` reconciles the *pyegeria SDK* against `.http` ground
truth. This script covers the layer above it -- the Dr.Egeria compact
command JSON (`md_processing/data/compact_commands/*.json`) and its
processors (`md_processing/v2/*.py`) -- for the specific failure classes
found live in ISSUE-76 (2026-08-26): a hardcoded relationship-type name that
was never real, offered to users via an enum, and a required attribute a
processor silently never reads.

Checks
------
  OM_TYPE          - every non-empty `OM_TYPE` field in a compact command
                      against a live server's real entity/relationship/
                      classification type names.
  ENUM_VALUE       - every `valid_values` entry that is *shaped* like an
                      Egeria type name (CamelCase, no spaces/underscores,
                      not all-uppercase) against the same live type-name set.
                      Heuristic, by design: ordinary domain enums (STATUS
                      values, etc.) don't look like this, so the false-
                      positive rate on real enums is low, but a genuinely
                      novel-but-real type name could still be flagged --
                      treat findings as "confirm before fixing", not gospel.
  DEAD_ATTRIBUTE   - every attribute a command's bundle chain resolves to
                      (via `parse_compact_export.expand_command`), checked
                      for at least one `.get('<name>'` / `.get("<name>"` (or
                      a listed `attr_labels` alias) reference anywhere under
                      `md_processing/v2/` or `md_processing/md_processing_utils/`.
                      Static and coarse (no per-family processor routing) --
                      a real hit here still needs a human to confirm the
                      *right* processor actually never reads it, same as the
                      `Link Term as Context` case this script's checks are
                      modeled on.

Usage
-----
    python scripts/dr_egeria_audit.py                    # DEAD_ATTRIBUTE only (no server needed)
    python scripts/dr_egeria_audit.py --live              # adds OM_TYPE + ENUM_VALUE
    python scripts/dr_egeria_audit.py --live --report PATH

Exit status is 1 when any finding is reported, so this can gate CI once the
current backlog of findings is triaged.
"""
from __future__ import annotations

import argparse
import asyncio
import glob
import json
import os
import re
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from md_processing.md_processing_utils.parse_compact_export import expand_command

COMPACT_DIR = "md_processing/data/compact_commands"
SEARCH_DIRS = ["md_processing/v2", "md_processing/md_processing_utils"]

# Style values whose valid_values are plausibly type names rather than plain
# domain enums (status codes, etc. use "Enum"/"Valid Value" too, so this
# doesn't narrow much -- the CamelCase shape heuristic below does the real
# filtering).
ENUM_STYLES = {"Enum", "Valid Value"}


@dataclass
class Finding:
    category: str
    file: str
    command: str
    detail: str


@dataclass
class AuditResult:
    findings: list = field(default_factory=list)

    def add(self, category: str, file: str, command: str, detail: str):
        self.findings.append(Finding(category, file, command, detail))


def load_families() -> dict[str, dict]:
    families = {}
    for path in sorted(glob.glob(os.path.join(COMPACT_DIR, "*.json"))):
        with open(path) as f:
            families[os.path.basename(path)] = json.load(f)
    return families


def looks_like_type_name(value: str) -> bool:
    """True if `value` is shaped like a compound PascalCase Egeria type name
    (e.g. "TermHASARelationship", "ISARelationship", "ProjectProperties") --
    starts uppercase, no spaces/underscores, at least one lowercase letter
    (rules out all-caps enum values like "ACTIVE" or short acronyms like
    "ISA"), and at least 2 uppercase letters total (rules out an ordinary
    single-capitalized-word enum value like "Discovered" or "Security",
    which real domain enums use plenty of -- a real compound type name
    always has a second capitalized "word" joined in, even with an
    acronym-shaped prefix like "ISARelationship")."""
    if not value or " " in value or "_" in value:
        return False
    if not value[0].isupper():
        return False
    if not any(c.islower() for c in value):
        return False
    if sum(1 for c in value if c.isupper()) < 2:
        return False
    return True


async def fetch_known_type_names(platform_url: str, view_server: str, user_id: str, user_pwd: str) -> set[str]:
    from pyegeria import EgeriaTech

    client = EgeriaTech(view_server=view_server, platform_url=platform_url, user_id=user_id, user_pwd=user_pwd)
    client.create_egeria_bearer_token()

    names: set[str] = set()
    for getter in (
        client._async_get_all_entity_defs,
        client._async_get_all_relationship_defs,
        client._async_get_all_classification_defs,
    ):
        defs = await getter()
        if isinstance(defs, list):
            for d in defs:
                if isinstance(d, dict) and d.get("name"):
                    names.add(d["name"])
    return names


def check_om_type(families: dict, known_types: set[str], result: AuditResult):
    for fname, data in families.items():
        for cmd_name, cmd in data.get("commands", {}).items():
            om_type = (cmd.get("OM_TYPE") or "").strip()
            if not om_type:
                continue
            if om_type not in known_types:
                result.add("OM_TYPE", fname, cmd_name,
                           f"OM_TYPE '{om_type}' not found among live entity/relationship/classification type names")


def check_enum_values(families: dict, known_types: set[str], result: AuditResult):
    for fname, data in families.items():
        attr_defs = data.get("attribute_definitions", {})
        for attr_name, attr in attr_defs.items():
            if attr.get("style") not in ENUM_STYLES:
                continue
            for value in attr.get("valid_values") or []:
                if looks_like_type_name(value) and value not in known_types:
                    result.add("ENUM_VALUE", fname, attr_name,
                               f"valid_values entry '{value}' looks like a type name but isn't a live one")


def build_usage_index() -> str:
    """Concatenated source of every .py file under SEARCH_DIRS, for a cheap
    substring-based usage check. Coarse by design -- see module docstring."""
    chunks = []
    for d in SEARCH_DIRS:
        for path in glob.glob(os.path.join(d, "*.py")):
            with open(path, encoding="utf-8", errors="replace") as f:
                chunks.append(f.read())
    return "\n".join(chunks)


def attribute_referenced(name: str, aliases: list[str], source: str) -> bool:
    candidates = [name] + aliases
    for cand in candidates:
        cand = cand.strip()
        if not cand:
            continue
        if f"'{cand}'" in source or f'"{cand}"' in source:
            return True
    return False


def check_dead_attributes(families: dict, result: AuditResult):
    source = build_usage_index()
    for fname, data in families.items():
        bundles = data.get("bundles", {})
        attr_defs = data.get("attribute_definitions", {})
        for cmd_name, cmd in data.get("commands", {}).items():
            expanded = expand_command(cmd, bundles, attr_defs)
            for attr in expanded.get("all_attributes", []):
                name = attr["name"]
                labels = [a.strip() for a in (attr.get("attr_labels") or "").split(";") if a.strip()]
                if not attribute_referenced(name, labels, source):
                    result.add("DEAD_ATTRIBUTE", fname, cmd_name,
                               f"attribute '{name}' (bundle chain: {' -> '.join(expanded.get('bundle_chain', []))}) "
                               f"never referenced under {' or '.join(SEARCH_DIRS)}")


def write_report(result: AuditResult, path: str):
    by_category: dict[str, list[Finding]] = {}
    for f in result.findings:
        by_category.setdefault(f.category, []).append(f)

    lines = ["# Dr.Egeria Compact Spec Audit Report\n"]
    if not result.findings:
        lines.append("No findings.\n")
    for category in sorted(by_category):
        findings = by_category[category]
        lines.append(f"## {category} ({len(findings)})\n")
        for f in findings:
            lines.append(f"- **{f.file}** / `{f.command}` — {f.detail}")
        lines.append("")

    with open(path, "w") as out:
        out.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--live", action="store_true",
                        help="Also run OM_TYPE and ENUM_VALUE checks against a live Egeria server.")
    parser.add_argument("--platform-url", default=os.environ.get("PYEGERIA_PLATFORM_URL", "https://localhost:9443"))
    parser.add_argument("--view-server", default=os.environ.get("PYEGERIA_VIEW_SERVER", "qs-view-server"))
    parser.add_argument("--user-id", default=os.environ.get("PYEGERIA_USER_ID", "erinoverview"))
    parser.add_argument("--user-pwd", default=os.environ.get("PYEGERIA_USER_PWD", "secret"))
    parser.add_argument("--report", default="dr_egeria_audit_report.md")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    families = load_families()
    result = AuditResult()

    check_dead_attributes(families, result)

    if args.live:
        try:
            known_types = asyncio.run(fetch_known_type_names(
                args.platform_url, args.view_server, args.user_id, args.user_pwd))
        except Exception as e:
            print(f"Live checks skipped -- could not reach platform: {e}", file=sys.stderr)
            known_types = None
        if known_types:
            check_om_type(families, known_types, result)
            check_enum_values(families, known_types, result)

    write_report(result, args.report)

    if not args.quiet:
        by_category: dict[str, int] = {}
        for f in result.findings:
            by_category[f.category] = by_category.get(f.category, 0) + 1
        print(f"Dr.Egeria audit: {len(result.findings)} finding(s)")
        for cat, n in sorted(by_category.items()):
            print(f"  {cat}: {n}")
        print(f"Report written to {args.report}")

    sys.exit(1 if result.findings else 0)


if __name__ == "__main__":
    main()
