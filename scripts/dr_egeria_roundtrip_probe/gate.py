#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""The round-trip probe as a pyegeria release gate.

    python scripts/dr_egeria_roundtrip_probe/gate.py                 # scratch up, probe, compare, scratch down
    python scripts/dr_egeria_roundtrip_probe/gate.py --rebaseline    # same, then (re)write the baseline
    python scripts/dr_egeria_roundtrip_probe/gate.py --results RESULTS-<UTC>.json   # compare a finished run only

Compared with the committed baseline (baseline/<egeria digest>.json), the gate FAILS on:
  - a row that was MATCH and now isn't (a regression);
  - a new REJECTED, CREATE-FAILED or UNRESOLVED;
  - a command that has disappeared.
Improvements don't fail: they print "update the baseline". Rows in known-gaps.json (accepted as not
fixable in pyegeria, each with a reason and a reference) never fail; when one becomes MATCH the gate
prints "remove from known gaps".

A new Egeria digest means a new baseline file: run with --rebaseline and review the diff between the
old and new digest baselines in the PR (Egeria-side changes show there).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASELINE_DIR = HERE / "baseline"
KNOWN_GAPS = HERE / "known-gaps.json"
sys.path.insert(0, str(HERE))
FAILURES = ("REJECTED", "CREATE-FAILED", "UNRESOLVED")


def row_key(row: dict) -> str:
    return f"{row['command']}|{row.get('attribute') or ''}"


def verdict_map(rows: list[dict]) -> dict[str, str]:
    return {row_key(r): r["verdict"] for r in rows}


def is_failure(verdict: str | None) -> bool:
    return bool(verdict) and verdict.startswith(FAILURES)


def known_gap(key: str, known: dict) -> dict | None:
    """The known-gaps entry for a row: exact `command|attribute`, or `*|attribute`, or `command|*`."""
    command, attribute = key.split("|", 1)
    return known.get(key) or known.get(f"*|{attribute}") or known.get(f"{command}|*")


def compare(baseline: dict[str, str], current: dict[str, str], known: dict) -> dict:
    """The gate's verdict on a run: what fails it and what only asks for a baseline/known-gaps update."""
    out = {"regressions": [], "new_failures": [], "commands_gone": [], "improvements": [], "changed": [],
           "rows_gone": [], "new_rows": [], "known_gap_fixed": [], "known_gap_hits": 0}
    current_commands = {k.split("|", 1)[0] for k in current}
    gone = set()
    for key, base in sorted(baseline.items()):
        command = key.split("|", 1)[0]
        cur = current.get(key)
        if cur is None:
            if command not in current_commands:
                if command not in gone:
                    gone.add(command)
                    out["commands_gone"].append(command)
            else:
                out["rows_gone"].append((key, base))
            continue
        gap = known_gap(key, known)
        if gap is not None and gap.get("verdict") and cur not in (gap["verdict"], "MATCH"):
            gap = None  # the gap explains one verdict only; failing another way is judged normally
        if gap is not None:
            if cur == "MATCH":
                out["known_gap_fixed"].append((key, base, gap.get("reason", "")))
            else:
                out["known_gap_hits"] += 1
            continue
        if cur == base:
            continue
        if base == "MATCH":
            out["regressions"].append((key, base, cur))
        elif is_failure(cur):
            out["new_failures"].append((key, base, cur))
        elif cur == "MATCH" or is_failure(base):
            out["improvements"].append((key, base, cur))
        else:
            out["changed"].append((key, base, cur))
    for key, cur in sorted(current.items()):
        if key in baseline:
            continue
        command = key.split("|", 1)[0]
        # A command the baseline couldn't diff (its create failed) has no attribute rows there: its static
        # REJECTED rows (attributes the probe never sends) are new rows of an improvement, not new failures.
        newly_diffable = is_failure(baseline.get(f"{command}|")) and key != f"{command}|"
        if is_failure(cur) and known_gap(key, known) is None and not (newly_diffable and cur.startswith("REJECTED")):
            out["new_failures"].append((key, None, cur))
        else:
            out["new_rows"].append((key, cur))
    out["failed"] = bool(out["regressions"] or out["new_failures"] or out["commands_gone"])
    return out


def render(result: dict) -> str:
    lines = [f"GATE: {'FAIL' if result['failed'] else 'PASS'}"]

    def section(title, items, fmt):
        if items:
            lines.append(f"\n{title} ({len(items)}):")
            lines.extend("  " + fmt(i) for i in items)

    section("REGRESSIONS (MATCH before, not now)", result["regressions"], lambda i: f"{i[0]}: {i[1]} -> {i[2]}")
    section("NEW FAILURES", result["new_failures"], lambda i: f"{i[0]}: {i[1]} -> {i[2]}")
    section("COMMANDS GONE", result["commands_gone"], str)
    section("IMPROVEMENTS (update the baseline)", result["improvements"], lambda i: f"{i[0]}: {i[1]} -> {i[2]}")
    section("CHANGED, not a regression (update the baseline)", result["changed"],
            lambda i: f"{i[0]}: {i[1]} -> {i[2]}")
    section("KNOWN GAPS NOW MATCH (remove from known gaps)", result["known_gap_fixed"],
            lambda i: f"{i[0]}: {i[1]} -> MATCH ({i[2]})")
    section("ROWS GONE (command still present)", result["rows_gone"], lambda i: f"{i[0]}: was {i[1]}")
    section("NEW ROWS (update the baseline)", result["new_rows"], lambda i: f"{i[0]}: {i[1]}")
    lines.append(f"\nknown-gap rows not fixed: {result['known_gap_hits']}")
    return "\n".join(lines)


def digest_short(image: str) -> str:
    m = re.search(r"sha256:([0-9a-f]{8})", image or "")
    return m.group(1) if m else "unknown"


def baseline_path(meta: dict) -> Path:
    return BASELINE_DIR / f"{digest_short(meta.get('image', ''))}.json"


def load_baseline(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def write_baseline(path: Path, data: dict, results_name: str) -> dict:
    """(Re)write the baseline from a run. Rows that changed against the previous baseline are listed under
    `changes` with a `reason` to fill in before committing (one line each)."""
    meta, rows = data["meta"], data["rows"]
    previous = load_baseline(path)
    old_rows, old_changes = previous.get("rows", {}), previous.get("changes", {})
    new_rows = verdict_map(rows)
    changes = {}
    for key in sorted(set(old_rows) | set(new_rows)):
        if old_rows and old_rows.get(key) != new_rows.get(key):
            reason = (old_changes.get(key) or {}).get("reason", "<one-line reason>")
            changes[key] = {"from": old_rows.get(key), "to": new_rows.get(key), "reason": reason}
    baseline = {"egeria_image": meta.get("image"), "pyegeria": meta.get("pyegeria"),
                "repository": meta.get("repository"), "content_packs": meta.get("content_packs"),
                "cut_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                "from_results": results_name, "rows": new_rows, "changes": changes}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(baseline, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    return baseline


def gate_results(results: Path, baseline: Path | None = None, known: Path = KNOWN_GAPS,
                 rebaseline: bool = False) -> int:
    data = json.loads(results.read_text())
    path = baseline or baseline_path(data["meta"])
    if rebaseline:
        b = write_baseline(path, data, results.name)
        print(f"baseline written: {path} ({len(b['rows'])} rows, {len(b['changes'])} changed against the "
              "previous baseline: give each a one-line reason before committing)")
        return 0
    if not path.exists():
        print(f"GATE: FAIL -- no baseline {path} for {data['meta'].get('image')}; cut one with --rebaseline")
        return 2
    known_gaps = json.loads(known.read_text()).get("gaps", {}) if known.exists() else {}
    result = compare(load_baseline(path).get("rows", {}), verdict_map(data["rows"]), known_gaps)
    text = render(result)
    print(text)
    results.with_suffix(".gate.txt").write_text(text + "\n", encoding="utf-8")
    return 1 if result["failed"] else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--results", help="compare a finished RESULTS-<UTC>.json; no platform is started")
    ap.add_argument("--baseline", help="baseline file (default: baseline/<egeria digest>.json)")
    ap.add_argument("--known-gaps", default=str(KNOWN_GAPS))
    ap.add_argument("--rebaseline", action="store_true", help="write the baseline from this run instead of gating")
    ap.add_argument("--digest", help="the platform image digest (default: scratch.py's laz pin)")
    ap.add_argument("--out", default="~/.re-gate/roundtrip-probe")
    ap.add_argument("--keep-up", action="store_true", help="leave the scratch platform running afterwards")
    ap.add_argument("--no-send-rejected", action="store_true",
                    help="skip the pyegeria-side REJECTED attributes (they're sent by default)")
    ap.add_argument("--repository", default="postgres", choices=("postgres", "memory"),
                    help="the scratch platform's repository (default postgres, as a real platform)")
    args = ap.parse_args(argv)
    if args.digest:
        import scratch as _scratch  # noqa: E402 (beside this file)
        _scratch.checked_digest(args.digest)  # before anything starts
    baseline = Path(args.baseline).expanduser() if args.baseline else None
    known = Path(args.known_gaps).expanduser()
    if args.results:
        return gate_results(Path(args.results).expanduser(), baseline, known, args.rebaseline)

    sys.path.insert(0, str(HERE))
    import probe
    import report
    import scratch
    out = Path(args.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    scratch.up(args.digest or scratch.DEFAULT_DIGEST, out, args.repository)
    try:
        before = set(out.glob("RESULTS-*.json"))
        probe.main(["--run", "--out", str(out)] + (["--no-send-rejected"] if args.no_send_rejected else []))
        results = max(set(out.glob("RESULTS-*.json")) - before, key=lambda p: p.stat().st_mtime)
        results.with_suffix(".md").write_text(report.render(json.loads(results.read_text())), encoding="utf-8")
        code = gate_results(results, baseline, known, args.rebaseline)
        print(f"results: {results} and {results.with_suffix('.md')}")
    finally:
        if not args.keep_up:
            scratch.down(out)
    return code


if __name__ == "__main__":
    sys.exit(main())
