#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Turn a probe RESULTS-<UTC>.json into RESULTS-<UTC>.md (and print the counts).

    uv run -p 3.13 python scripts/dr_egeria_roundtrip_probe/report.py ~/.re-gate/roundtrip-probe/RESULTS-<UTC>.json \\
        [--extra-header file.md] [--out results.md]
"""
import argparse
import collections
import json
from pathlib import Path

FIRST = ("DROPPED", "NOT RETURNED", "CHANGED", "DEFAULTED")


def cell(value) -> str:
    if value is None:
        return ""
    text = value if isinstance(value, str) else json.dumps(value, default=str)
    return text.replace("|", "\\|").replace("\n", "<br>")[:300]


def render(data: dict, extra: str = "") -> str:
    meta, rows = data["meta"], data["rows"]
    counts = collections.Counter(r["verdict"] for r in rows)
    lines = ["# Dr.Egeria round-trip probe results (phase 1: property styles)", "",
             f"- Image: `{meta['image']}`", f"- Server option: {meta['option']}",
             f"- pyegeria: {meta['pyegeria']}", f"- User: {meta['user']}",
             f"- Start: {meta['start']}  End: {meta['end']}", f"- Create commands: {meta['commands']}",
             f"- laz `quickstart-egeria-main` StartedAt before/after: {meta.get('laz_started_at_before')} / "
             f"{meta.get('laz_started_at_after')}",
             f"- Run folder (generated docs, dr_egeria logs): `{meta['run_dir']}`", ""]
    if extra:
        lines += [extra.rstrip(), ""]
    lines += ["## Counts per verdict", "", "| Verdict | Rows |", "|---|---|"]
    lines += [f"| {v} | {n} |" for v, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]
    first = [r for r in rows if r["verdict"].startswith(FIRST)]
    sides = collections.Counter(r.get("side", "?").split(" (")[0] for r in first)
    lines += ["", f"## DROPPED, CHANGED and DEFAULTED ({len(first)} rows; " +
              ", ".join(f"{k} {v}" for k, v in sorted(sides.items())) + ")", "",
              "| Family | Command | Attribute | Style | Sent | Read back | Stored (raw) | Verdict | Side | Note |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    order = lambda v: next(i for i, f in enumerate(FIRST) if v.startswith(f))  # noqa: E731
    for r in sorted(first, key=lambda r: (order(r["verdict"]), r["family"], r["command"], r["attribute"])):
        lines.append(f"| {cell(r['family'])} | {cell(r['command'])} | {cell(r['attribute'])} | {cell(r['style'])} | "
                     f"{cell(r['sent'])} | {cell(r['read'])} | {cell(r.get('stored'))} | {r['verdict']} | "
                     f"{cell(r.get('side'))} | {cell(r['note'])} |")
    lines += ["", "## Full table", "",
              "| Family | Command | Attribute | Style | Sent | Read back | Stored (raw) | Verdict | Note |",
              "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {cell(r['family'])} | {cell(r['command'])} | {cell(r['attribute'])} | {cell(r['style'])} | "
                     f"{cell(r['sent'])} | {cell(r['read'])} | {cell(r.get('stored'))} | {r['verdict']} | "
                     f"{cell(r['note'])} |")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("--extra-header", default="")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    src = Path(args.results).expanduser()
    data = json.loads(src.read_text())
    extra = Path(args.extra_header).expanduser().read_text() if args.extra_header else ""
    out = Path(args.out).expanduser() if args.out else src.with_suffix(".md")
    out.write_text(render(data, extra), encoding="utf-8")
    print(out, dict(collections.Counter(r["verdict"] for r in data["rows"])))


if __name__ == "__main__":
    main()
