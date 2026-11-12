#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Write the golden hashes of every default report-spec output on the five CDO-sheet fixtures.

R1's gate (tests/micro-tests/test_r1_structured_table.py) compares against the file this writes. It was
generated at rs-fix-now 289f9e6b (fix-now F1-F10 on SD-2); regenerate it only for a deliberate change to
default rendering, and say so in the commit.

    uv run -p 3.13 python scripts/golden_report_outputs.py tests/micro-tests/data/report_specs/golden_default_outputs.json
"""
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent.parent / "tests" / "micro-tests"
_spec = importlib.util.spec_from_file_location("report_fixture_replay", HERE / "report_fixture_replay.py")
rfr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rfr)
FORMATS = ["TABLE", "DICT", "LIST", "REPORT", "MD", "FORM"]


def main(path: str) -> None:
    mp = pytest.MonkeyPatch()
    out = {}
    for name in rfr.TILES:
        replay = rfr.ReportReplay(mp, name)
        for fmt in FORMATS + (["MERMAID"] if name == "isc_register" else []):
            try:
                text = json.dumps(replay.run(fmt), ensure_ascii=False, default=str)
            except Exception as e:  # noqa: BLE001
                text = f"ERROR {type(e).__name__}: {e}"
            text = re.sub(r"created at \d{4}-\d{2}-\d{2} \d{2}:\d{2}", "created at <time>", text)
            out[f"{name}/{fmt}"] = {"sha256": hashlib.sha256(text.encode()).hexdigest(), "bytes": len(text.encode())}
    Path(path).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(f"{len(out)} golden outputs written to {path}")


if __name__ == "__main__":
    main(sys.argv[1])
