#!/usr/bin/env python3
"""Audit whether every compact-spec command attribute is actually consumed
by the processor code that runs it.

This closes the gap `scripts/omvs_audit.py` doesn't cover: that script
reconciles pyegeria's OMVS clients against the `.http` ground truth (does the
SDK call the right URL/verb/body?). This script reconciles one layer up --
does the *Dr.Egeria processor* actually read every attribute its own compact
command spec declares? A spec change (new bundle attribute, new custom
attribute) and the processor code that has to act on it are edited in
different places and can drift silently: the attribute parses fine, renders
fine in the generated template, and the command still reports SUCCESS while
quietly doing nothing with the value.

Two known real bugs motivated this (see PYEGERIA_ISSUES.md ISSUE-97/98):

  * ISSUE-98 (UNCONSUMED): `Create Digital Product`'s `Product Status`/
    `Product Type`/`Current Version` were declared in the compact spec but
    never referenced anywhere in the processor/body-builder code at all.
  * ISSUE-97 (CARDINALITY_MISMATCH): `Create Data Structure`'s
    `In Data Specification` (and siblings) *were* referenced in the
    processor, but the spec declares them singular (`Reference Name`) while
    the processor only ever read the plural `guid_list` key -- so the
    singular `guid` value it actually got was silently never used.

This is a static heuristic, not a proof. Read the FINDINGS and go look --
see "Known limitations" below before trusting a clean run.

Checks
------
UNCONSUMED
    The attribute's display name never appears, as a quoted string, in any
    processor module under `md_processing/v2/` or `md_processing/
    md_processing_utils/`. High confidence: Dr.Egeria's own convention (see
    CLAUDE.md) is `attributes.get('<Display Name>', {})...` everywhere, so a
    genuinely-consumed attribute's exact display-name string almost always
    appears literally somewhere in that tree.

CARDINALITY_MISMATCH
    The attribute has `style` "Reference Name" (singular) or "Reference Name
    List" (plural) -- these resolve to a `guid` or `guid_list` key
    respectively in the parsed attribute dict (see `processors.py`,
    AttributeFirstParser). This check finds every place the attribute's
    display name is used as a dict key/lookup and checks whether the code
    near it reads the *matching* key. A singular attribute whose code only
    ever reads `guid_list` (or vice versa) is the exact ISSUE-97 shape.

Known limitations (read before trusting a clean run)
------------------------------------------------------
* UNCONSUMED has false positives for attributes intentionally handled by a
  fully generic, name-agnostic path (e.g. iterated from a dict rather than
  looked up by literal string) -- rare in this codebase but possible.
* UNCONSUMED can miss a real bug if the attribute name happens to appear as
  a *substring* of an unrelated string, or in a comment/docstring rather
  than a functional lookup -- it doesn't distinguish those from a real
  `attributes.get(...)` call. Treat a "consumed" verdict as "probably fine",
  not certain.
* CARDINALITY_MISMATCH only understands the `.get('guid')` / `.get('guid_list')`
  / `['guid']` / `['guid_list']` idiom actually used in this codebase. A
  processor using some other access pattern won't be checked either way.
* Attributes with no registered processor (parse-only commands, e.g. some
  Curation classification types per CLAUDE.md) are reported separately
  (UNROUTED) and not checked -- there's deliberately no code to check yet.
* This is a *candidate list*, not a bug list. Confirm each finding by reading
  the processor before reporting it as a bug (same discipline as
  omvs_audit.py's BODY-check caveat).

Usage
-----
    python scripts/dr_egeria_attribute_consumption_audit.py [--family NAME]
                                                              [--command NAME]
                                                              [--report PATH]

Exit status is 1 if any UNCONSUMED or CARDINALITY_MISMATCH finding survives,
so it can gate CI once the existing backlog is triaged (it will NOT be clean
on first run against a live codebase -- this is a discovery tool first).
"""

from __future__ import annotations

import argparse
import inspect
import os
import re
import sys
from dataclasses import dataclass, field

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Attributes that are handled entirely generically (base Referenceable /
# request-envelope plumbing in processors.py itself, not per-command code)
# and would otherwise dominate the UNCONSUMED list with known-fine noise.
# Confirmed present in the shared `Referenceable`/`Link Command Base`
# bundles (see CLAUDE.md's Compact Attribute Global Namespace note) and
# handled in processors.py/common_md_utils.py's generic envelope builders.
SKIP_ATTRIBUTES = {
    "Qualified Name", "GUID", "Display Name", "Description",
    "Effective From", "Effective To", "Effective Time",
    "For Lineage", "For Duplicate Processing",
    "External Source GUID", "External Source Name", "Request ID",
    "Merge Update", "Journal Entry", "Status", "Content Status",
    "Version Identifier", "Is Own Anchor", "Anchor Scope IDs", "Make Anchor",
    "Extended Properties", "Additional Properties",
}

REFERENCE_STYLES = {"Reference Name": "guid", "Reference Name List": "guid_list"}


@dataclass
class Finding:
    command: str
    attribute: str
    style: str
    processor: str
    kind: str  # UNCONSUMED | CARDINALITY_MISMATCH
    detail: str


@dataclass
class SourceIndex:
    files: dict = field(default_factory=dict)  # path -> list[str] lines
    combined: str = ""

    @classmethod
    def build(cls, roots: list[str]) -> "SourceIndex":
        idx = cls()
        chunks = []
        for root in roots:
            for dirpath, _, filenames in os.walk(root):
                if "__pycache__" in dirpath:
                    continue
                for fn in filenames:
                    if not fn.endswith(".py"):
                        continue
                    path = os.path.join(dirpath, fn)
                    try:
                        with open(path, "r", encoding="utf-8") as fh:
                            lines = fh.readlines()
                    except OSError:
                        continue
                    idx.files[path] = lines
                    chunks.append("".join(lines))
        idx.combined = "\n".join(chunks)
        return idx


def load_dispatcher_and_specs():
    """Import dr_egeria (triggers load_commands()) and build a dispatcher."""
    import md_processing.dr_egeria as dre
    from md_processing.md_processing_utils.md_processing_constants import (
        COMMAND_DEFINITIONS,
    )

    dispatcher = dre.setup_dispatcher(None)  # registration touches no client
    specs = COMMAND_DEFINITIONS.get("Command Specifications", {})
    return dispatcher, specs


def find_reference_key_evidence(lines: list[str], attr_name: str) -> tuple[bool, bool]:
    """Scan a file's lines for `attr_name` used as a lookup key, and report
    whether a `guid` and/or `guid_list` access appears within a small window
    around each occurrence. Returns (saw_guid, saw_guid_list)."""
    saw_guid = False
    saw_guid_list = False
    quoted = f"'{attr_name}'"
    quoted_dq = f'"{attr_name}"'
    for i, line in enumerate(lines):
        if quoted not in line and quoted_dq not in line:
            continue
        window = "".join(lines[max(0, i - 1): i + 4])
        if re.search(r"""\[\s*['"]guid_list['"]\s*\]|\.get\(\s*['"]guid_list['"]""", window):
            saw_guid_list = True
        if re.search(r"""\[\s*['"]guid['"]\s*\]|\.get\(\s*['"]guid['"]""", window):
            saw_guid = True
    return saw_guid, saw_guid_list


def audit(family_filter: str | None, command_filter: str | None) -> list[Finding]:
    dispatcher, specs = load_dispatcher_and_specs()

    v2_root = os.path.join(REPO_ROOT, "md_processing", "v2")
    utils_root = os.path.join(REPO_ROOT, "md_processing", "md_processing_utils")
    index = SourceIndex.build([v2_root, utils_root])

    findings: list[Finding] = []
    unrouted: list[str] = []

    for command_name, spec in specs.items():
        if not isinstance(spec, dict):
            continue
        if family_filter and spec.get("family") != family_filter:
            continue
        if command_filter and command_filter.lower() not in command_name.lower():
            continue

        from md_processing.dr_egeria import normalize_command_key

        processor_cls = dispatcher.processors.get(normalize_command_key(command_name))
        if processor_cls is None:
            unrouted.append(command_name)
            continue
        processor_name = processor_cls.__name__

        for attr in spec.get("Attributes", []):
            if not isinstance(attr, dict):
                continue
            name = attr.get("name")
            if not name or name in SKIP_ATTRIBUTES:
                continue
            style = attr.get("style", "")

            quoted = f"'{name}'"
            quoted_dq = f'"{name}"'
            if quoted not in index.combined and quoted_dq not in index.combined:
                findings.append(Finding(
                    command=command_name, attribute=name, style=style,
                    processor=processor_name, kind="UNCONSUMED",
                    detail="attribute display name not found as a literal anywhere "
                           "under md_processing/v2/ or md_processing/md_processing_utils/",
                ))
                continue

            if style in REFERENCE_STYLES:
                expected_key = REFERENCE_STYLES[style]
                saw_guid_any = False
                saw_guid_list_any = False
                for path, lines in index.files.items():
                    g, gl = find_reference_key_evidence(lines, name)
                    saw_guid_any = saw_guid_any or g
                    saw_guid_list_any = saw_guid_list_any or gl

                if expected_key == "guid" and saw_guid_list_any and not saw_guid_any:
                    findings.append(Finding(
                        command=command_name, attribute=name, style=style,
                        processor=processor_name, kind="CARDINALITY_MISMATCH",
                        detail="spec declares this singular (Reference Name), but code "
                               "near it only ever reads the plural 'guid_list' key -- "
                               "the ISSUE-97 shape (parser stores singular refs under "
                               "'guid', never 'guid_list')",
                    ))
                elif expected_key == "guid_list" and saw_guid_any and not saw_guid_list_any:
                    findings.append(Finding(
                        command=command_name, attribute=name, style=style,
                        processor=processor_name, kind="CARDINALITY_MISMATCH",
                        detail="spec declares this plural (Reference Name List), but code "
                               "near it only ever reads the singular 'guid' key -- likely "
                               "drops all but one selected reference",
                    ))

    if unrouted:
        print(f"# {len(unrouted)} command(s) have no registered processor "
              f"(parse-only by design, or a genuine gap -- not checked here):",
              file=sys.stderr)
        for u in sorted(unrouted):
            print(f"#   - {u}", file=sys.stderr)

    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--family", default=None, help="Restrict to one compact-spec family, e.g. 'Digital Products'")
    ap.add_argument("--command", default=None, help="Restrict to commands whose name contains this substring")
    ap.add_argument("--report", default=None, help="Write the report to this path instead of stdout")
    args = ap.parse_args()

    findings = audit(args.family, args.command)

    lines = []
    lines.append(f"# Dr.Egeria attribute-consumption audit -- {len(findings)} finding(s)\n")
    if not findings:
        lines.append("No candidates found. Remember: this is a heuristic, not a proof "
                      "(see \"Known limitations\" in the script docstring).\n")
    else:
        by_kind: dict[str, list[Finding]] = {}
        for f in findings:
            by_kind.setdefault(f.kind, []).append(f)
        for kind in ("UNCONSUMED", "CARDINALITY_MISMATCH"):
            group = by_kind.get(kind, [])
            if not group:
                continue
            lines.append(f"\n## {kind} ({len(group)})\n")
            for f in sorted(group, key=lambda x: (x.command, x.attribute)):
                lines.append(f"- **{f.command}** / `{f.attribute}` (style: {f.style or '?'}, "
                              f"processor: {f.processor})\n  {f.detail}")

    report = "\n".join(lines) + "\n"
    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"Report written to {args.report}")
    else:
        print(report)

    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
